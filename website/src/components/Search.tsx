import type MiniSearch from 'minisearch';
import { useCallback, useEffect, useId, useMemo, useRef, useState } from 'preact/hooks';
import './Search.css';

interface SearchProps {
  base: string;
}

interface SearchDocument {
  id: string;
  title: string;
  chapter: string;
  number: string;
  url: string;
  text: string;
}

type LoadState = 'idle' | 'loading' | 'ready' | 'error';

interface Snippet {
  before: string;
  match: string;
  after: string;
  prefix: boolean;
  suffix: boolean;
}

const RESULT_LIMIT = 8;
const REQUEST_TIMEOUT_MS = 15_000;
const DOCUMENT_FIELDS = ['id', 'title', 'chapter', 'number', 'url', 'text'] as const;

/** Search data is fetched independently of the initial reader payload. */
function readDocuments(value: unknown): SearchDocument[] {
  if (!Array.isArray(value) || value.length === 0) throw new Error('Invalid search data');
  const ids = new Set<string>();

  return value.map((entry: unknown) => {
    if (entry === null || typeof entry !== 'object') throw new Error('Invalid search entry');
    const row = entry as Record<string, unknown>;
    if (DOCUMENT_FIELDS.some((field) => typeof row[field] !== 'string')) {
      throw new Error('Invalid search fields');
    }
    const document = row as unknown as SearchDocument;
    if (!document.id || !document.title || !document.url || ids.has(document.id)) {
      throw new Error('Invalid search identity');
    }
    const destination = new URL(document.url, window.location.href);
    if (
      destination.origin !== window.location.origin ||
      !['https:', 'http:'].includes(destination.protocol)
    ) {
      throw new Error('Invalid search destination');
    }
    ids.add(document.id);
    return { ...document, text: document.text.replace(/\s+/gu, ' ').trim() };
  });
}

/** Find a literal query occurrence, then keep its surrounding sentence fragment. */
function snippetFor(text: string, query: string): Snippet {
  const folded = text.toLocaleLowerCase();
  const phrase = query.trim().toLocaleLowerCase();
  let at = phrase ? folded.indexOf(phrase) : -1;
  let length = at >= 0 ? phrase.length : 0;

  if (at < 0) {
    const terms = phrase.match(/[\p{L}\p{N}]+/gu) ?? [];
    for (const term of terms) {
      const found = folded.indexOf(term);
      if (found >= 0 && (at < 0 || found < at)) {
        at = found;
        length = term.length;
      }
    }
  }

  let start = Math.max(0, (at < 0 ? 0 : at) - 65);
  if (start > 0) {
    const boundary = text.indexOf(' ', start);
    if (boundary >= 0 && boundary < at) start = boundary + 1;
  }
  let end = Math.min(text.length, Math.max(start + 205, at + length));
  if (end < text.length) {
    const boundary = text.lastIndexOf(' ', end);
    if (boundary > Math.max(start + 100, at + length)) end = boundary;
  }
  if (at < 0) {
    return {
      before: text.slice(start, end),
      match: '',
      after: '',
      prefix: start > 0,
      suffix: end < text.length,
    };
  }
  return {
    before: text.slice(start, at),
    match: text.slice(at, at + length),
    after: text.slice(at + length, end),
    prefix: start > 0,
    suffix: end < text.length,
  };
}

export default function Search({ base }: SearchProps) {
  const id = useId();
  const headingId = `${id}-heading`;
  const resultsId = `${id}-results`;
  const helpId = `${id}-help`;
  const dialogRef = useRef<HTMLDialogElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const returnFocusRef = useRef<HTMLElement | null>(null);
  const indexRef = useRef<MiniSearch<SearchDocument> | null>(null);
  const documentsRef = useRef(new Map<string, SearchDocument>());
  const pendingRef = useRef<Promise<void> | null>(null);
  const requestRef = useRef<AbortController | null>(null);
  const aliveRef = useRef(true);
  const [open, setOpen] = useState(false);
  const [loadState, setLoadState] = useState<LoadState>('idle');
  const [query, setQuery] = useState('');
  const [active, setActive] = useState(0);
  const normalizedBase = base.endsWith('/') ? base : `${base}/`;

  const loadIndex = useCallback((): Promise<void> => {
    if (indexRef.current !== null) return Promise.resolve();
    if (pendingRef.current !== null) return pendingRef.current;

    const controller = new AbortController();
    requestRef.current = controller;
    setLoadState('loading');
    const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    const pending = (async () => {
      try {
        const [response, { default: SearchIndex }] = await Promise.all([
          fetch(`${normalizedBase}search.json`, { signal: controller.signal }),
          import('minisearch'),
        ]);
        if (!response.ok) throw new Error('Search request failed');
        const documents = readDocuments(await response.json());
        if (controller.signal.aborted) throw new Error('Search request cancelled');

        const index = new SearchIndex<SearchDocument>({
          idField: 'id',
          fields: ['title', 'text', 'chapter', 'number'],
          searchOptions: {
            boost: { title: 6, number: 3, chapter: 1.5, text: 1 },
            combineWith: 'AND',
            prefix: (_term, position, terms) => position === terms.length - 1,
            fuzzy: false,
          },
        });
        await index.addAllAsync(documents, { chunkSize: 12 });
        if (!aliveRef.current) return;
        if (controller.signal.aborted) throw new Error('Search indexing cancelled');
        documentsRef.current = new Map(documents.map((document) => [document.id, document]));
        indexRef.current = index;
        setLoadState('ready');
      } catch {
        if (aliveRef.current) setLoadState('error');
      } finally {
        window.clearTimeout(timeout);
        if (requestRef.current === controller) requestRef.current = null;
        pendingRef.current = null;
      }
    })();
    pendingRef.current = pending;
    return pending;
  }, [normalizedBase]);

  const showDialog = useCallback(() => {
    const dialog = dialogRef.current;
    if (dialog === null) return;
    if (dialog.open) {
      inputRef.current?.focus();
      return;
    }
    returnFocusRef.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;
    dialog.showModal();
    setOpen(true);
    inputRef.current?.focus();
    void loadIndex();
  }, [loadIndex]);

  const closeDialog = useCallback(() => {
    if (dialogRef.current?.open) dialogRef.current.close();
  }, []);

  const finishClose = useCallback(() => {
    setOpen(false);
    setQuery('');
    setActive(0);
    const previous = returnFocusRef.current;
    returnFocusRef.current = null;
    if (previous?.isConnected) previous.focus({ preventScroll: true });
  }, []);

  useEffect(() => {
    aliveRef.current = true;
    const shortcut = (event: KeyboardEvent) => {
      if (
        event.key.toLowerCase() === 'k' &&
        (event.ctrlKey || event.metaKey) &&
        !event.altKey &&
        !event.shiftKey
      ) {
        event.preventDefault();
        showDialog();
      }
    };
    const requested = () => showDialog();
    window.addEventListener('keydown', shortcut);
    window.addEventListener('agentic:search', requested);
    document.addEventListener('agentic:search', requested);
    // A non-hydrated header can leave a request on the server-rendered dialog.
    const dialog = dialogRef.current;
    if (dialog !== null) {
      dialog.dataset.searchReady = 'true';
      if (dialog.dataset.searchRequested === 'true') {
        delete dialog.dataset.searchRequested;
        showDialog();
      }
    }
    return () => {
      aliveRef.current = false;
      requestRef.current?.abort();
      if (dialog !== null) delete dialog.dataset.searchReady;
      window.removeEventListener('keydown', shortcut);
      window.removeEventListener('agentic:search', requested);
      document.removeEventListener('agentic:search', requested);
    };
  }, [showDialog]);

  useEffect(() => {
    if (!open) return;
    const previous = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    return () => {
      document.documentElement.style.overflow = previous;
    };
  }, [open]);

  const matches = useMemo(() => {
    const term = query.trim();
    if (!term || loadState !== 'ready' || indexRef.current === null) return [];
    return indexRef.current
      .search(term)
      .map((result) => documentsRef.current.get(String(result.id)))
      .filter((result): result is SearchDocument => result !== undefined);
  }, [query, loadState]);
  const results = matches.slice(0, RESULT_LIMIT);

  useEffect(() => {
    const result = dialogRef.current?.querySelector<HTMLElement>(
      `[data-search-result="${String(active)}"]`,
    );
    result?.scrollIntoView({ block: 'nearest' });
  }, [active, query, loadState]);

  const status =
    loadState === 'loading'
      ? 'Loading the search index…'
      : loadState === 'error'
        ? 'Search is temporarily unavailable.'
        : !query.trim()
          ? 'Type a term to search the full text.'
          : matches.length === 0
            ? 'No matching passages.'
            : matches.length > RESULT_LIMIT
              ? `Showing ${String(RESULT_LIMIT)} of ${String(matches.length)} matches.`
              : `${String(matches.length)} ${matches.length === 1 ? 'match' : 'matches'}.`;

  return (
    <dialog
      class="search-dialog"
      ref={dialogRef}
      aria-labelledby={headingId}
      onClose={finishClose}
      onCancel={(event) => {
        event.preventDefault();
        closeDialog();
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget) closeDialog();
      }}
      onKeyDown={(event) => {
        if (event.isComposing) return;
        if (event.key === 'Escape') {
          event.preventDefault();
          closeDialog();
          return;
        }
        if (event.key === 'Tab') {
          const focusable = Array.from(
            event.currentTarget.querySelectorAll<HTMLElement>(
              'button:not([disabled]), input:not([disabled]), a[href]:not([tabindex="-1"]), [tabindex="0"]',
            ),
          ).filter((element) => element.getClientRects().length > 0);
          const first = focusable[0];
          const last = focusable.at(-1);
          if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last?.focus();
          } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first?.focus();
          }
          return;
        }
        const inSearch =
          event.target === inputRef.current ||
          (event.target instanceof Element &&
            event.target.closest('[data-search-result]') !== null);
        if (!inSearch) return;
        if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
          event.preventDefault();
          if (results.length > 0) {
            const direction = event.key === 'ArrowDown' ? 1 : -1;
            setActive((current) => (current + direction + results.length) % results.length);
          }
        } else if (event.key === 'Enter' && results.length > 0 && !event.isComposing) {
          event.preventDefault();
          dialogRef.current
            ?.querySelector<HTMLAnchorElement>(`[data-search-result="${String(active)}"]`)
            ?.click();
        }
      }}
    >
      <div class="search-panel">
        <header class="search-header">
          <div>
            <p class="search-eyebrow">Agentic State</p>
            <h2 id={headingId} class="search-heading">
              Search the book
            </h2>
          </div>
          <button
            class="search-close"
            type="button"
            aria-label="Close search"
            title="Close search (Escape)"
            onClick={closeDialog}
          >
            <i class="ph ph-x" aria-hidden="true" />
          </button>
        </header>

        <div class="search-field">
          <i class="ph ph-magnifying-glass" aria-hidden="true" />
          <input
            ref={inputRef}
            class="search-input"
            type="search"
            placeholder="Find a concept, method, or passage"
            value={query}
            autoComplete="off"
            spellcheck={false}
            maxLength={240}
            role="combobox"
            aria-label="Search the full text of Agentic State"
            aria-autocomplete="list"
            aria-haspopup="listbox"
            aria-expanded={open && results.length > 0}
            aria-controls={resultsId}
            aria-activedescendant={
              open && results[active] !== undefined ? `${id}-result-${String(active)}` : undefined
            }
            aria-describedby={helpId}
            onInput={(event) => {
              setQuery(event.currentTarget.value);
              setActive(0);
            }}
          />
        </div>

        <p class="search-status" role="status" aria-live="polite" aria-atomic="true">
          {status}
        </p>

        <div class="search-content" aria-busy={loadState === 'loading'}>
          <div
            id={resultsId}
            class="search-results"
            role="listbox"
            aria-label="Matching chapters and sections"
            hidden={results.length === 0}
          >
            {results.map((result, position) => {
              const snippet = snippetFor(result.text, query);
              const label = [result.chapter, result.number].filter(Boolean).join(' · ');
              return (
                <a
                  key={result.id}
                  id={`${id}-result-${String(position)}`}
                  class="search-result"
                  href={result.url}
                  role="option"
                  aria-selected={active === position}
                  tabIndex={-1}
                  data-search-result={position}
                  onPointerMove={(event) => {
                    if (event.pointerType !== 'touch') setActive(position);
                  }}
                  onClick={(event) => {
                    if (
                      event.button === 0 &&
                      !event.metaKey &&
                      !event.ctrlKey &&
                      !event.shiftKey &&
                      !event.altKey
                    ) {
                      closeDialog();
                    }
                  }}
                >
                  {label && <span class="search-result-label">{label}</span>}
                  <span class="search-result-title">{result.title}</span>
                  {(snippet.before || snippet.match || snippet.after) && (
                    <span class="search-result-snippet">
                      {snippet.prefix && '…'}
                      {snippet.before}
                      {snippet.match && <mark>{snippet.match}</mark>}
                      {snippet.after}
                      {snippet.suffix && '…'}
                    </span>
                  )}
                </a>
              );
            })}
          </div>

          {loadState === 'loading' && (
            <div class="search-empty">
              <span class="search-loading" aria-hidden="true" />
              <p>Preparing full-text search.</p>
            </div>
          )}
          {loadState === 'error' && (
            <div class="search-empty">
              <p>The index could not be loaded. Check your connection and try again.</p>
              <button
                class="search-retry"
                type="button"
                onClick={() => {
                  inputRef.current?.focus();
                  void loadIndex();
                }}
              >
                Try again
              </button>
            </div>
          )}
          {loadState === 'ready' && !query.trim() && (
            <div class="search-empty">
              <p>Explore the connections across context, memory, learning, and control.</p>
              <p class="search-empty-hint">Try “persistent memory” or “verification”.</p>
            </div>
          )}
          {loadState === 'ready' && query.trim() && results.length === 0 && (
            <div class="search-empty">
              <p>No passages match “{query.trim()}”.</p>
              <p class="search-empty-hint">Try fewer terms or another technical name.</p>
            </div>
          )}
        </div>

        <footer class="search-footer">
          <p id={helpId}>
            <span class="search-sr-only">
              Use the up and down arrow keys to choose a result, Enter to open it, and Escape to close.
            </span>
            <span aria-hidden="true">
              <kbd>↑</kbd> <kbd>↓</kbd> choose <kbd>Enter</kbd> open <kbd>Esc</kbd> close
            </span>
          </p>
          <span class="search-local-note">Search stays in this browser</span>
        </footer>
      </div>
    </dialog>
  );
}

