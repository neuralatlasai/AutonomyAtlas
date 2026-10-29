/** Server-only KaTeX renderer for the compiler's escaped, source-preserving nodes. */
import katex from 'katex';

const macros = Object.freeze({
  '\\History': '\\mathcal{H}', '\\Context': '\\mathcal{C}',
  '\\Memory': '\\mathcal{M}', '\\Tools': '\\mathcal{T}',
  '\\Versions': '\\mathcal{V}', '\\E': '\\mathbb{E}',
  '\\KL': '\\operatorname{KL}', '\\TV': '\\operatorname{TV}',
  '\\softmax': '\\operatorname{softmax}', '\\FLOPs': '\\operatorname{FLOPs}',
  '\\GiB': '\\operatorname{GiB}', '\\argmax': '\\operatorname*{arg\\,max}',
  '\\argmin': '\\operatorname*{arg\\,min}', '\\Var': '\\operatorname{Var}',
  '\\Cov': '\\operatorname{Cov}', '\\supp': '\\operatorname{supp}',
  '\\diag': '\\operatorname{diag}', '\\tr': '\\operatorname{tr}',
});

function decodeAttribute(value) {
  // Exactly the entities emitted by Python html.escape; decode once, ampersand last.
  return value.replace(/&quot;/g, '"').replace(/&#x27;/g, "'")
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
}

/** Render generated math while retaining its exact input and explicit equation tags. */
export function renderMathHtml(html) {
  return html.replace(
    /<(span|div) class="math math-(inline|display)" data-tex="([^"]*)" data-display="(true|false)">[\s\S]*?<\/\1>/g,
    (match, tag, kind, escaped, display) => {
      if ((kind === 'display') !== (display === 'true')) throw new Error('Math display-mode contract mismatch');
      const rendered = katex.renderToString(decodeAttribute(escaped), {
        displayMode: display === 'true', throwOnError: true, strict: 'error',
        trust: false, output: 'htmlAndMathml', macros: { ...macros },
      });
      return `<${tag} class="math math-${kind}" data-tex="${escaped}" data-display="${display}" data-rendered="katex">${rendered}</${tag}>`;
    },
  );
}

if (process.argv.includes('--check')) {
  const { readFileSync } = await import('node:fs');
  const book = JSON.parse(readFileSync(new URL('../src/generated/book.json', import.meta.url), 'utf8'));
  let inline = 0; let display = 0;
  const owners = [...book.chapters, { id: 'front-matter', html: book.metadata.frontMatterHtml }, ...book.references];
  for (const owner of owners) {
    const source = owner.html;
    inline += [...source.matchAll(/data-display="false"/g)].length;
    display += [...source.matchAll(/data-display="true"/g)].length;
    const rendered = renderMathHtml(source);
    const expected = [...source.matchAll(/class="math math-(?:inline|display)"/g)].length;
    const actual = [...rendered.matchAll(/data-rendered="katex"/g)].length;
    if (expected !== actual) throw new Error(`Math nodes lost for ${owner.id}: ${actual}/${expected}`);
    if (renderMathHtml(rendered) !== rendered) throw new Error(`Non-idempotent math rendering for ${owner.id}`);
  }
  if (display !== book.metadata.metrics.displayEnvironments) throw new Error('Display-environment count changed');
  console.log(JSON.stringify({ katex: katex.version, inline, display, total: inline + display, errors: 0, idempotent: true }));
}
