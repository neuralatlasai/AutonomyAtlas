import source from '../generated/book.json';
import type { Book } from '../generated/book.types';
import { renderMathHtml } from '../../tools/render-math.mjs';

export const book = source as Book;
export const base = import.meta.env.BASE_URL.replace(/\/?$/, '/');
export const href = (path = '') => base + path.replace(/^\//, '');
export const chapterHref = (slug: string) => href(`chapters/${slug}/`);
export const renderContent = (html: string) => renderMathHtml(html)
  .replaceAll('__BOOK_BASE__', base)
  .replace(/class="equation"/g, 'class="equation" tabindex="0" role="region" aria-label="Mathematical equation; scroll horizontally when needed"');
export const groups = [
  { name: 'Foundations & models', subtitle: 'From system boundaries to learned representations', range: [1, 7], icon: 'stack' },
  { name: 'Learning & inference', subtitle: 'Training, reasoning, planning, and context', range: [8, 12], icon: 'sparkle' },
  { name: 'Memory & execution', subtitle: 'The persistent systems around a policy', range: [13, 23], icon: 'cpu' },
  { name: 'Evidence & assurance', subtitle: 'Verification, evaluation, security, and alignment', range: [24, 29], icon: 'shield' },
  { name: 'Adaptation & deployment', subtitle: 'Improvement, serving, recovery, and synthesis', range: [30, 34], icon: 'arrows' },
];
export const groupFor = (n: number) => groups.find(g => n >= g.range[0] && n <= g.range[1])!;
export const paths = [
  { title: 'Context becomes a decision', summary: 'Follow the information boundary from representation and long context to an action.', chapters: [2, 5, 11, 12, 17], icon: 'stack' },
  { title: 'Memory that survives execution', summary: 'Trace sessions, persistent records, reusable skills, retrieval, and durable effects.', chapters: [13, 14, 15, 16, 20], icon: 'cpu' },
  { title: 'From evidence to improvement', summary: 'Connect verification and evaluation to adaptation without confusing selection with progress.', chapters: [25, 26, 27, 30, 33], icon: 'sparkle' },
  { title: 'Authority at the boundary', summary: 'Study tool contracts, stateful attacks, alignment, and recovery around external effects.', chapters: [18, 19, 28, 29, 32], icon: 'shield' },
];
