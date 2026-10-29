import { mkdir, copyFile, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

const root = resolve(import.meta.dirname, '../..');
const output = resolve(root, 'website/public');
const manifest = JSON.parse(await readFile(resolve(root, 'book/figures/manifest.json'), 'utf8'));
for (const figure of manifest.figures) {
  const target = resolve(output, 'figures', figure.asset.split('/').at(-1));
  await mkdir(dirname(target), { recursive: true });
  await copyFile(resolve(root, figure.asset), target);
}
await mkdir(resolve(output, 'downloads'), { recursive: true });
await copyFile(resolve(root, 'output/pdf/agentic_state_monograph.pdf'), resolve(output, 'downloads/agentic-state.pdf'));
await copyFile(resolve(root, 'output/source/agentic_state_source.zip'), resolve(output, 'downloads/agentic-state-source.zip'));
await copyFile(resolve(root, 'book/validation_summary.json'), resolve(output, 'downloads/validation.json'));
await copyFile(resolve(root, 'book/current_source_review_20261029.csv'), resolve(output, 'downloads/source-crosswalk.csv'));
await writeFile(resolve(output, '.nojekyll'), '');
await mkdir(resolve(output, 'licenses'), { recursive: true });
await copyFile(resolve(root, 'website/brand-source/et-book-LICENSE.txt'), resolve(output, 'licenses/et-book.txt'));
for (const [pkg,name,license] of [
  ['@fontsource-variable/inter','inter','LICENSE'],
  ['@fontsource-variable/source-serif-4','source-serif-4','LICENSE'],
  ['@phosphor-icons/core','phosphor','LICENSE'],
  ['katex','katex','LICENSE'],
  ['astro','astro','LICENSE'],
  ['preact','preact','LICENSE'],
  ['minisearch','minisearch','LICENSE.txt'],
]) {
  await copyFile(resolve(root, 'website/node_modules', pkg, license), resolve(output, `licenses/${name}.txt`));
}
