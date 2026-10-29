/** Independent, Node-only audit of this edition's accepted TeX and web data.
 * This bounded parser verifies known book constructs; it is not a TeX engine.
 * The publication check additionally validates actual static output and links.
 */
import { readFile, readdir, lstat } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { resolve, dirname, relative, sep } from 'node:path';
import { parse, parseFragment } from 'parse5';

const root = resolve(import.meta.dirname, '../..');
const site = resolve(root, 'website');
const failures = [];
const assert = (ok, message) => { if (!ok) failures.push(message); };
const hash = value => createHash('sha256').update(value).digest('hex');
const read = path => readFile(resolve(root, path), 'utf8');
const json = async path => JSON.parse(await read(path));
const norm = text => text.normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const count = (text, expression) => [...text.matchAll(expression)].length;
const numericLiterals = text => [...text.matchAll(/[+\-\u2212]?\d+(?:,\d{3})*(?:\.\d+)?(?:[eE][+\-]?\d+)?%?/g)].map(m => m[0]);
const confirmedAuthor = 'Hemanth Kandimalla';

// Read the effective Info dictionary through the final classic cross-reference
// table, rather than accepting an arbitrary /Author string elsewhere in a PDF.
// This is deliberately bounded to the accepted pdfTeX output format; it fails
// closed on unsupported PDF layouts and is not a general-purpose PDF validator.
function pdfAuthorInfo(bytes) {
  const text = bytes.toString('latin1');
  const final = /startxref\s+(\d+)\s+%%EOF\s*$/.exec(text);
  if (!final) throw new Error('Missing final PDF cross-reference pointer');
  const xrefOffset = Number(final[1]);
  if (text.slice(xrefOffset, xrefOffset + 4) !== 'xref') throw new Error('Unsupported non-classic PDF cross-reference table');
  const trailerStart = text.indexOf('trailer', xrefOffset);
  const trailer = text.slice(trailerStart, final.index);
  const info = /\/Info\s+(\d+)\s+(\d+)\s+R\b/.exec(trailer);
  if (!info || /\/Prev\b/.test(trailer)) throw new Error('Missing or unsupported incremental PDF Info reference');
  const objectNumber = Number(info[1]), generation = Number(info[2]);
  const lines = text.slice(xrefOffset + 4, trailerStart).trim().split(/\r?\n/);
  let objectOffset;
  for (let i = 0; i < lines.length;) {
    const range = /^(\d+)\s+(\d+)$/.exec(lines[i++].trim());
    if (!range) throw new Error('Unsupported PDF cross-reference subsection');
    const first = Number(range[1]), length = Number(range[2]);
    if (objectNumber >= first && objectNumber < first + length) {
      const entry = /^(\d{10})\s+(\d{5})\s+([fn])\s*$/.exec(lines[i + objectNumber - first]);
      if (!entry || entry[3] !== 'n' || Number(entry[2]) !== generation) throw new Error('Invalid PDF Info cross-reference entry');
      objectOffset = Number(entry[1]);
    }
    i += length;
  }
  if (objectOffset === undefined) throw new Error('Unresolved PDF Info object');
  const object = text.slice(objectOffset, text.indexOf('endobj', objectOffset));
  if (!object.startsWith(`${objectNumber} ${generation} obj`)) throw new Error('PDF Info object offset does not match its reference');
  const authorToken = /\/Author\b\s*/.exec(object);
  if (!authorToken) throw new Error('Missing PDF Author metadata');
  let at = authorToken.index + authorToken[0].length, raw;
  if (object[at] === '<' && object[at + 1] !== '<') {
    const end = object.indexOf('>', at + 1), hex = object.slice(at + 1, end).replace(/\s+/g, '');
    if (end < 0 || !/^(?:[\da-f]{2})*$/i.test(hex)) throw new Error('Malformed PDF Author hexadecimal string');
    raw = Buffer.from(hex, 'hex');
  } else if (object[at] === '(') {
    const output = []; let depth = 1; at++;
    while (at < object.length && depth) {
      let code = object.charCodeAt(at++);
      if (code === 92) {
        const escaped = object[at++];
        if (escaped === '\r' || escaped === '\n') { if (escaped === '\r' && object[at] === '\n') at++; continue; }
        if (/[0-7]/.test(escaped ?? '')) {
          let octal = escaped;
          while (octal.length < 3 && /[0-7]/.test(object[at] ?? '')) octal += object[at++];
          code = parseInt(octal, 8);
        } else code = ({ n: 10, r: 13, t: 9, b: 8, f: 12 })[escaped] ?? escaped?.charCodeAt(0);
      } else if (code === 40) depth++;
      else if (code === 41 && --depth === 0) break;
      output.push(code);
    }
    if (depth) throw new Error('Unclosed PDF Author literal string');
    raw = Buffer.from(output);
  } else throw new Error('Unsupported PDF Author value');
  let author;
  if (raw[0] === 0xfe && raw[1] === 0xff) {
    if (raw.length % 2) throw new Error('Malformed PDF Author UTF-16 string');
    author = Buffer.from(raw.subarray(2)).swap16().toString('utf16le');
  } else if (raw[0] === 0xff && raw[1] === 0xfe) author = raw.subarray(2).toString('utf16le');
  else {
    if ([...raw].some(b => b > 127)) throw new Error('Unsupported non-ASCII PDFDocEncoding Author string');
    author = raw.toString('ascii');
  }
  return { author, infoObject: `${objectNumber} ${generation} R`, objectOffset };
}

function group(text, pos) {
  while (/\s/.test(text[pos] ?? '') && pos < text.length) pos++;
  if (text[pos] !== '{') throw new Error(`Expected TeX group at ${text.slice(pos, pos + 70)}`);
  let depth = 1;
  const start = ++pos;
  for (; pos < text.length; pos++) {
    if (text[pos] === '\\') { pos++; continue; }
    if (text[pos] === '{') depth++;
    // A braced argument may itself contain nested braced arguments.
    if (text[pos] === '}') { depth--; if (!depth) return [text.slice(start, pos), pos + 1]; }
  }
  throw new Error('Unclosed TeX group');
}

function uncomment(text) {
  let output = '';
  for (let i = 0; i < text.length;) {
    const verbatim = /^\\(?:path|url)\s*\{/.exec(text.slice(i));
    if (verbatim) { const [, end] = group(text, i + verbatim[0].length - 1); output += text.slice(i, end); i = end; }
    else if (text[i] === '\\' && i + 1 < text.length) { output += text.slice(i, i + 2); i += 2; }
    else if (text[i] === '%') { const end = text.indexOf('\n', i); i = end < 0 ? text.length : end; }
    else output += text[i++];
  }
  return output;
}

async function expand(path, stack = []) {
  const full = resolve(root, path);
  if (!full.startsWith(root + sep) || stack.includes(full)) throw new Error(`Invalid source include ${path}`);
  const text = uncomment((await readFile(full, 'utf8')).replace(/\r\n?/g, '\n'));
  const includeOrder = [relative(root, full).split(sep).join('/')];
  let output = '', last = 0;
  for (const match of text.matchAll(/\\(?:input|include)\s*\{([^}]+)\}/g)) {
    output += text.slice(last, match.index);
    let next = match[1].endsWith('.tex') ? match[1] : match[1] + '.tex';
    try { await lstat(resolve(root, next)); } catch { next = relative(root, resolve(dirname(full), next)); }
    const child = await expand(next, [...stack, full]);
    output += '\n' + child.text + '\n';
    includeOrder.push(...child.includeOrder); last = match.index + match[0].length;
  }
  output += text.slice(last);
  return { text: output, includeOrder };
}

// Use the HTML5 parsing rules, including SVG and MathML foreign content. A
// regex-based HTML stack can mis-scope actual browser DOM around those nodes.
function htmlTree(html) {
  const convert = node => node.nodeName === '#text' ? node.value : {
    tag: node.tagName ?? '#root', attrs: Object.fromEntries((node.attrs ?? []).map(a => [a.name, a.value])),
    children: (node.childNodes ?? []).filter(n => n.nodeName !== '#comment' && n.nodeName !== '#documentType').map(convert),
  };
  return convert(/^\s*<!doctype\b/i.test(html) ? parse(html) : parseFragment(html));
}
function elements(node) { return typeof node === 'string' ? [] : [node, ...node.children.flatMap(elements)]; }
function textOf(node, prose = false) {
  if (typeof node === 'string') return node;
  const classes = (node.attrs.class ?? '').split(/\s+/);
  if (prose && (['script', 'style'].includes(node.tag) || classes.some(c => ['math', 'citation', 'cross-reference', 'figure-number'].includes(c)))) return '';
  let value = node.children.map(n => textOf(n, prose)).join(' ');
  if (prose && (/^h[1-6]$/.test(node.tag) || node.tag === 'caption')) value = value.replace(/^\s*(?:(?:Figure|Table)\s+)?\d+(?:\.\d+)*\s*:?\s*/u, '');
  return value;
}

function commandArguments(text, command) {
  const result = [];
  for (const m of text.matchAll(new RegExp('\\\\(?:' + command + ')\\s*\\{', 'g'))) result.push(group(text, m.index + m[0].length - 1)[0]);
  return result;
}
function displays(text) { return [...text.matchAll(/\\begin\{(equation|align)\}[\s\S]*?\\end\{\1\}/g)].map(m => m[0]); }

// Extract only visible prose. Formulae are audited separately, byte-for-byte.
// Every nonempty normalized prose paragraph must occur in source order.
const unknownTextCommands = new Set();
function prose(text) {
  text = text.replace(/\\begin\{(equation|align)\}[\s\S]*?\\end\{\1\}/g, '')
    .replace(/\\\([\s\S]*?\\\)/g, '').replace(/\\\[[\s\S]*?\\\]/g, '')
    .replace(/\$[^$]*\$/g, '').replace(/\\endfirsthead[\s\S]*?\\endhead/g, '');
  const invisible = new Set(['label', 'cite', 'ref', 'eqref', 'input', 'include', 'includegraphics', 'bookneedspace']);
  const bare = new Set(['centering', 'small', 'footnotesize', 'begingroup', 'endgroup', 'allowbreak', 'toprule', 'midrule', 'bottomrule', 'endfirsthead', 'endhead', 'endfoot', 'endlastfoot', 'hfill', 'noindent', 'tabularnewline']);
  const visible = new Set(['section', 'subsection', 'subsubsection', 'paragraph', 'caption', 'emph', 'textit', 'textbf', 'texttt', 'textsc', 'textrm', 'textnormal', 'textsuperscript', 'mbox', 'underline']);
  let out = '';
  for (let i = 0; i < text.length;) {
    if (text[i] !== '\\') { if (!'{}'.includes(text[i])) out += text[i]; i++; continue; }
    const m = /^\\([A-Za-z]+|[^A-Za-z])\*?/.exec(text.slice(i));
    if (!m) { i++; continue; }
    i += m[0].length; const name = m[1];
    while (text[i] === '[') { const end = text.indexOf(']', i); if (end < 0) throw new Error('Unclosed optional TeX argument'); i = end + 1; }
    const arg = () => { const g = group(text, i); i = g[1]; return g[0]; };
    if (name === 'begin' || name === 'end') {
      const env = arg();
      if (name === 'begin') {
        while (text[i] === '[') { const end = text.indexOf(']', i); if (end < 0) throw new Error('Unclosed environment placement'); i = end + 1; }
        if (['tabular', 'longtable'].includes(env)) arg();
      }
      continue;
    }
    if (name === 'chapter') { arg(); continue; }
    if (invisible.has(name)) { arg(); continue; }
    if (name === 'setlength') { arg(); arg(); continue; }
    if (bare.has(name)) continue;
    if (name === 'href') { arg(); out += prose(arg()); continue; }
    if (name === 'multicolumn') { arg(); arg(); out += prose(arg()); continue; }
    if (['path', 'url'].includes(name)) { out += arg(); continue; }
    if (visible.has(name)) { out += prose(arg()); continue; }
    if (['LaTeX', 'TeX'].includes(name)) { out += name; continue; }
    if (['%', '&', '_', '#', '$', '{', '}'].includes(name)) { out += name; continue; }
    if (['\\', ',', ';', ':', '!', ' '].includes(name)) { out += ' '; continue; }
    if (['textendash', 'textemdash', 'textasciitilde', 'textbackslash'].includes(name)) { out += ' '; continue; }
    unknownTextCommands.add(name);
  }
  return out;
}

const alternate = process.argv.find(a => a.startsWith('--book-data='))?.slice('--book-data='.length);
const bookPath = alternate || 'website/src/generated/book.json';
const bookBytes = await readFile(resolve(root, bookPath));
const book = JSON.parse(bookBytes.toString('utf8'));
const manifest = await json('website/tools/source-manifest.json');
const plan = await json('book/plan.json');
const validation = await json('book/validation_summary.json');
const figureManifest = await json('book/figures/manifest.json');
const expected = { chapters: 34, sections: 266, subsections: 39, paragraphs: 6, figures: 35, tables: 37,
  displayEnvironments: 217, labels: 466, references: 129, paths: 168, citationCalls: 525,
  inlineMath: 2166, equationNumbers: 231, uniqueCitedKeys: 356, labelRecords: 468 };
assert(book.metadata.schemaVersion === '1.0.0' && manifest.schemaVersion === '1.0.0', 'Unsupported web-data schema');
assert(hash(bookBytes) === manifest.generatedBookSha256, 'Generated JSON bytes differ from the converter emission');
const converterHash = hash(await readFile(resolve(root, 'website/tools/compile_book.py')));
assert(converterHash === book.metadata.converterSha256 && converterHash === manifest.diagnostics.converterSha256, 'Converter changed without regenerating web data');
assert(book.metadata.title === plan.title && book.metadata.subtitle === plan.subtitle, 'Title/subtitle differs from accepted plan');
assert(book.metadata.literatureCutoff === plan.literature_cutoff, 'Literature cutoff differs from accepted plan');
assert(book.metadata.acceptedPdfSha256 === validation.pdf_sha256, 'Web data belongs to another accepted PDF');
const acceptedPdf = await readFile(resolve(root, 'output/pdf/agentic_state_monograph.pdf'));
assert(hash(acceptedPdf) === validation.pdf_sha256, 'Canonical PDF bytes do not match the accepted validation');
let pdfAuthor = null;
try { pdfAuthor = pdfAuthorInfo(acceptedPdf); }
catch (error) { failures.push(`Cannot independently read accepted PDF author: ${error.message}`); }
assert(pdfAuthor?.author === confirmedAuthor, 'Accepted PDF Author metadata differs from the confirmed human author');
assert(validation.validation_status === 'complete', 'Accepted PDF audit is incomplete');
assert(same(book.metadata.metrics, manifest.metrics), 'JSON/manifest counters disagree');
for (const [key, n] of Object.entries(expected)) assert(book.metadata.metrics[key] === n, `Accepted ${key}: expected ${n}, got ${book.metadata.metrics[key]}`);
assert(hash(JSON.stringify(manifest.files)) === manifest.sourceDigest && manifest.sourceDigest === book.metadata.sourceDigest, 'Source digest does not bind the manifested input hashes');
const filePaths = new Set();
for (const file of manifest.files) {
  assert(!filePaths.has(file.path), `Duplicate source manifest path ${file.path}`); filePaths.add(file.path);
  assert(!/(?:^|\/)(?:context|internal|tmp|build)(?:\/|$)/.test(file.path), `Private source input ${file.path}`);
  try { assert(hash(await readFile(resolve(root, file.path))) === file.sha256, `Stale generated content: ${file.path}`); }
  catch { failures.push(`Missing accepted source input ${file.path}`); }
}
assert(!manifest.diagnostics.unknownRawTex.length && !manifest.diagnostics.sourceEdits, 'Converter diagnostics contain unsupported raw TeX or source edits');
const authorSourcePath = 'config/book_layout.tex';
const authorSourceBytes = await readFile(resolve(root, authorSourcePath));
const authorDeclarations = [];
for (const settings of commandArguments(uncomment(authorSourceBytes.toString('utf8')), 'hypersetup')) {
  for (const match of settings.matchAll(/\bpdfauthor\s*=\s*\{/g)) authorDeclarations.push(group(settings, match.index + match[0].length - 1)[0]);
}
assert(authorDeclarations.length === 1 && authorDeclarations[0] === confirmedAuthor, 'Accepted layout must declare the single confirmed literal PDF author');
assert(book.metadata.author === confirmedAuthor && book.metadata.author === authorDeclarations[0], 'Web author differs from the confirmed accepted source author');
assert(manifest.authorBinding?.path === authorSourcePath && manifest.authorBinding?.sha256 === hash(authorSourceBytes)
  && manifest.authorBinding?.command === 'hypersetup' && manifest.authorBinding?.key === 'pdfauthor'
  && manifest.authorBinding?.kind === 'explicit braced literal' && manifest.authorBinding?.value === confirmedAuthor,
  'Generated author binding does not identify the accepted literal and its source hash');
assert(manifest.files.some(f => f.path === authorSourcePath && f.sha256 === hash(authorSourceBytes)), 'Accepted author source is not hash-bound in the input manifest');
const frontSourceRaw = (await read('book/frontmatter.tex')).replace(/\r\n?/g, '\n');
const titlePage = uncomment(frontSourceRaw.slice(0, frontSourceRaw.indexOf('\\end{titlepage}')));
assert(titlePage.split(confirmedAuthor).length === 2, 'Accepted title page must display the confirmed author once');
const frontSource = uncomment(frontSourceRaw.slice(frontSourceRaw.indexOf('\\chapter*{Abstract}')));
const frontTree = htmlTree(book.metadata.frontMatterHtml), frontNodes = elements(frontTree);
const frontProse = norm(textOf(frontTree, true));
const frontParagraphs = prose(frontSource).split(/\n\s*\n/).map(p => norm(p)).filter(Boolean);
let frontPosition = 0;
for (const paragraph of frontParagraphs) {
  const found = frontProse.indexOf(paragraph, frontPosition);
  assert(found >= 0, 'Front-matter prose/disclosure coverage differs from accepted source');
  if (found >= 0) frontPosition = found + paragraph.length;
}
const frontMath = [...frontSource.matchAll(/\\\(([\s\S]*?)\\\)|(?<!\\)\$([^$]*)(?<!\\)\$/g)].map(m => (m[1] ?? m[2]).replace(/\s+/g, ''));
assert(same(frontMath, frontNodes.filter(n => n.attrs['data-tex']).map(n => n.attrs['data-tex'].replace(/\s+/g, ''))), 'Front-matter mathematics differs');
const references = new Map(book.references.map(r => [r.key, r]));
assert(references.size === 356 && book.references.length === 356, 'Bibliographic identities are missing or duplicated');
assert(same(book.references.map(r => r.number), Array.from({ length: 356 }, (_, i) => i + 1)), 'Bibliographic numbers are not contiguous');
assert(same(book.references.map(r => r.key), manifest.acceptedBbl.entryKeys), 'Accepted bibliography entry order changed');
const documentTrees = new Map(), chapterReports = [], allCites = new Set(), totals = {};
const chapterParagraphs = new Map();
assert(book.chapters.length === plan.chapters.length, 'Chapter count differs from accepted plan');
for (let ci = 0; ci < plan.chapters.length; ci++) {
  const accepted = plan.chapters[ci], chapter = book.chapters[ci];
  assert(chapter.id === accepted.id && chapter.number === accepted.number && chapter.title === accepted.title, `Chapter identity/order differs: ${accepted.id}`);
  const expanded = await expand(accepted.path), text = expanded.text;
  const sourceHash = hash(text);
  assert(sourceHash === chapter.sourceSha256 && sourceHash === manifest.chapters[chapter.id].sourceSha256, `Expanded accepted source differs: ${chapter.id}`);
  assert(same(expanded.includeOrder, manifest.chapters[chapter.id].includeOrder), `Include traversal differs: ${chapter.id}`);
  for (const path of expanded.includeOrder) assert(filePaths.has(path), `Unmanifested chapter input ${path}`);
  const tree = htmlTree(chapter.html), nodes = elements(tree);
  documentTrees.set(`chapters/${chapter.slug}/`, tree);
  const sourceCites = commandArguments(text, 'cite').flatMap(x => x.split(',').map(k => k.trim()));
  const sourceRefs = commandArguments(text, 'ref|eqref'), sourcePaths = commandArguments(text, 'path');
  const ids = nodes.filter(n => n.attrs.id).map(n => n.attrs.id);
  assert(new Set(ids).size === ids.length, `Duplicate chapter DOM IDs: ${chapter.id}`);
  const citeNodes = nodes.filter(n => n.attrs['data-cite-key']), refNodes = nodes.filter(n => n.attrs['data-ref-label']);
  assert(same(sourceCites, citeNodes.map(n => n.attrs['data-cite-key'])), `Citation occurrence/order mismatch: ${chapter.id}`);
  assert(same(sourceRefs, refNodes.map(n => n.attrs['data-ref-label'])), `Cross-reference occurrence/order mismatch: ${chapter.id}`);
  assert(same(sourcePaths, nodes.filter(n => n.attrs['data-source-path'] === 'true').map(n => textOf(n))), `Repository path text loss: ${chapter.id}`);
  for (const node of citeNodes) {
    const ref = references.get(node.attrs['data-cite-key']);
    assert(ref && node.attrs.href === `__BOOK_BASE__references/#${ref.id}` && textOf(node) === String(ref.number), `Incorrect citation destination/number in ${chapter.id}`);
    allCites.add(node.attrs['data-cite-key']);
  }
  for (const node of refNodes) {
    const record = book.labels[node.attrs['data-ref-label']];
    assert(record && record.href === node.attrs.href && textOf(node).replace(/[()]/g, '') === record.number, `Incorrect cross-reference destination/number: ${node.attrs['data-ref-label']}`);
  }
  const sourceLabels = commandArguments(text, 'label');
  for (const id of sourceLabels) assert(ids.includes(id) && book.labels[id]?.chapterId === chapter.id, `Missing label/anchor ${id}`);
  const sourceDisplays = displays(text);
  assert(same(sourceDisplays, chapter.equations.map(e => e.sourceTex)), `Display equation source loss: ${chapter.id}`);
  const math = nodes.filter(n => (n.attrs.class ?? '').split(/\s+/).includes('math'));
  const displaysHtml = math.filter(n => n.attrs['data-display'] === 'true');
  assert(same(displaysHtml.map(n => n.attrs['data-tex']), chapter.equations.map(e => e.tex)), `Displayed TeX mismatch: ${chapter.id}`);
  const inlineCount = count(text, /\\\(/g) + count(text, /(?<!\\)\$(?!\$)/g) / 2;
  const sourceInline = [...text.matchAll(/\\\(([\s\S]*?)\\\)|(?<!\\)\$([^$]*)(?<!\\)\$/g)].map(m => (m[1] ?? m[2]).replace(/\s+/g, ''));
  const emittedInline = math.filter(n => n.attrs['data-display'] === 'false').map(n => n.attrs['data-tex'].replace(/\s+/g, ''));
  assert(same(sourceInline, emittedInline), `Inline mathematics expression/order mismatch: ${chapter.id}`);
  assert(math.filter(n => n.attrs['data-display'] === 'false').length === inlineCount, `Inline mathematics count mismatch: ${chapter.id}`);
  const computed = { sections: commandArguments(text, 'section').length, subsections: commandArguments(text, 'subsection').length,
    paragraphs: commandArguments(text, 'paragraph').length, figures: count(text, /\\includegraphics\b/g),
    tables: count(text, /\\begin\{(?:table|longtable)\}/g), displayEnvironments: sourceDisplays.length,
    labels: sourceLabels.length, references: sourceRefs.length, paths: sourcePaths.length,
    citationCalls: commandArguments(text, 'cite').length, inlineMath: inlineCount,
    equationNumbers: chapter.equations.reduce((n, e) => n + e.numbers.length, 0) };
  for (const [key, n] of Object.entries(computed)) { totals[key] = (totals[key] ?? 0) + n; assert(chapter.counts[key] === n && manifest.chapters[chapter.id].counts[key] === n, `Independent ${key} count mismatch: ${chapter.id}`); }
  assert(nodes.filter(n => n.attrs['data-citation'] === 'true').length === computed.citationCalls, `Citation cluster loss: ${chapter.id}`);
  assert(nodes.filter(n => n.tag === 'figure').length === computed.figures && chapter.figures.length === computed.figures, `Figure loss: ${chapter.id}`);
  assert(nodes.filter(n => n.tag === 'table').length === computed.tables && chapter.tables.length === computed.tables, `Table loss: ${chapter.id}`);
  assert(chapter.sections.filter(s => s.level === 1).length === computed.sections && chapter.sections.filter(s => s.level === 2).length === computed.subsections, `Heading hierarchy loss: ${chapter.id}`);
  for (const section of chapter.sections) assert(ids.includes(section.anchor), `Missing section destination ${section.anchor}`);
  let equationIndex = 0;
  for (const equation of chapter.equations) {
    assert(same(equation.numbers, [...equation.tex.matchAll(/\\tag\{([^}]+)\}/g)].map(m => m[1])), `Equation tags changed: ${equation.id}`);
    for (const number of equation.numbers) assert(number === `${chapter.number}.${++equationIndex}`, `Equation counter changed: ${equation.id}`);
    for (const id of equation.labels) assert(ids.includes(id) && equation.numbers.includes(book.labels[id]?.number), `Equation label number/anchor mismatch: ${id}`);
  }
  for (const figure of chapter.figures) {
    const record = manifest.assets.find(a => a.id === figure.id), source = figureManifest.figures.find(f => f.asset === record?.source);
    assert(record && source && figure.sha256 === source.sha256 && figure.sha256 === record.sha256, `Unbound figure identity/hash ${figure.id}`);
    if (record) assert(hash(await readFile(resolve(root, record.source))) === record.sha256, `Changed figure bytes ${figure.id}`);
    assert(figure.captionHtml.length > 20 && figure.alt.trim().length > 20, `Missing figure description ${figure.id}`);
  }
  for (const table of chapter.tables) {
    const wrapper = nodes.find(n => n.attrs.id === table.id), tableNode = wrapper && elements(wrapper).find(n => n.tag === 'table');
    assert(tableNode && elements(tableNode).filter(n => n.tag === 'tr').length === table.rowCount, `Table row loss ${table.id}`);
    if (tableNode) for (const row of elements(tableNode).filter(n => n.tag === 'tr')) assert(row.children.filter(n => typeof n !== 'string' && ['td', 'th'].includes(n.tag)).reduce((n, cell) => n + +(cell.attrs.colspan ?? 1), 0) === table.columnCount, `Table column/cell loss ${table.id}`);
  }
  const sourceTables = [...text.matchAll(/\\begin\{(table|longtable)\}[\s\S]*?\\end\{\1\}/g)].map(m => m[0]);
  assert(sourceTables.length === chapter.tables.length, `Independent table extraction differs: ${chapter.id}`);
  for (let ti = 0; ti < sourceTables.length; ti++) {
    const table = chapter.tables[ti], wrapper = nodes.find(n => n.attrs.id === table.id);
    assert(norm(prose(sourceTables[ti])) === norm(textOf(wrapper, true)), `Table caption/cell text mismatch ${table.id}`);
    assert(same(numericLiterals(prose(sourceTables[ti])), numericLiterals(textOf(wrapper, true))), `Table numeric literal mismatch ${table.id}`);
  }
  const visibleHtml = norm(textOf(tree, true));
  const paragraphs = prose(text).split(/\n\s*\n/).map(p => p.trim()).filter(p => norm(p).length);
  chapterParagraphs.set(chapter.id, paragraphs.map(norm));
  let position = 0, matched = 0;
  for (const paragraph of paragraphs) {
    const needle = norm(paragraph); if (!needle) continue;
    const found = visibleHtml.indexOf(needle, position);
    assert(found >= 0, `Prose coverage ${chapter.id}: ${paragraph.replace(/\s+/g, ' ').slice(0, 180)}`);
    if (found >= 0) { position = found + needle.length; matched++; }
  }
  chapterReports.push({ id: chapter.id, counts: computed, proseParagraphs: paragraphs.length, proseMatched: matched });
}
for (const [key, n] of Object.entries(totals)) assert(n === expected[key], `Independent global ${key} count differs`);
assert(allCites.size === 356 && same([...allCites].sort(), [...references.keys()].sort()), 'Cited/reference identity sets differ');
assert(!unknownTextCommands.size, `Unclassified prose TeX commands: ${[...unknownTextCommands].join(', ')}`);
for (const ref of book.references) {
  assert(ref.text.length > 20 && ref.html.length > 20 && ref.id === `ref-${ref.key}`, `Empty or malformed bibliography record ${ref.key}`);
  assert(manifest.acceptedAux.citationNumbers[ref.key] === ref.number, `Accepted citation numbering differs ${ref.key}`);
  const links = elements(htmlTree(ref.html)).filter(n => n.tag === 'a').map(n => n.attrs.href);
  assert(ref.urls.every(u => /^https?:\/\//.test(u) && links.includes(u)), `Bibliography URL loss ${ref.key}`);
}
documentTrees.set('references/', htmlTree(book.references.map(r => `<div id="${r.id}">${r.html}</div>`).join('')));
for (const [id, label] of Object.entries(book.labels)) {
  const route = label.href.split('__BOOK_BASE__')[1]?.split('#')[0], target = documentTrees.get(route);
  assert(target && elements(target).some(n => n.attrs.id === id), `Unresolved global target ${id}`);
}

// A repository source checkout may contain public TeX, but never private corpus,
// research ledgers, build caches, or an accidental pile of old output artifacts.
const tracked = execFileSync('git', ['ls-files', '-z'], { cwd: root, encoding: 'utf8' }).split('\0').filter(Boolean);
for (const file of tracked) {
  assert(!/(?:^|\/)(?:context|internal|tmp|build|node_modules)(?:\/|$)/i.test(file), `Private/cache file is tracked: ${file}`);
  assert(!file.startsWith('output/') || ['output/pdf/agentic_state_monograph.pdf', 'output/source/agentic_state_source.zip'].includes(file), `Unrequested output is tracked: ${file}`);
}

async function filesUnder(path) {
  const output = [];
  for (const item of await readdir(path, { withFileTypes: true })) {
    const full = resolve(path, item.name);
    const stat = await lstat(full);
    assert(!stat.isSymbolicLink(), `Published symlink ${full}`);
    if (item.isDirectory()) output.push(...await filesUnder(full)); else output.push(full);
  }
  return output;
}

let publication = null;
if (process.argv.includes('--dist')) {
  const dist = resolve(site, 'dist'), files = await filesUnder(dist), byPath = new Map(files.map(f => [relative(dist, f).split(sep).join('/'), f]));
  // Unmodified ET Book files from edwardtufte/et-book revision
  // 24d3a3bbfc880095d3df2b9e9d60d05819138e89. Admit exact files,
  // rather than opening the publication allowlist to an entire font directory.
  const pinnedPublicAssets = new Map([
    ['fonts/et-book/et-book-roman-line-figures.woff', { bytes: 44016, sha256: 'be0f2c061cd8c57b38b5edd8c03dac72ca7d87fb5c3f7f5c32ed72dede39a601' }],
    ['fonts/et-book/et-book-italic.woff', { bytes: 43780, sha256: 'e5bae09f1cb8391fcd35b903fefd306d5294456872af87674b376fa897ded416' }],
    ['fonts/et-book/et-book-bold-line-figures.woff', { bytes: 45364, sha256: 'ea6efd96090dc2d0be0a826d1f2b79b07ca9af21f6483f2f96694b761d669ddc' }],
    ['licenses/et-book.txt', { bytes: 1089, sha256: '5ce4d24bc1aeed06dd19a43588702f434392ea79df28111f3149bb809504fa26' }],
  ]);
  const base = '/AutonomyAtlas/';
  const targets = new Map();
  let htmlAuthorMetaChecked = 0;
  let htmlBookAuthorSchemaChecked = 0;
  for (const [path, full] of byPath) if (path.endsWith('.html')) {
    const html = await readFile(full, 'utf8'), tree = htmlTree(html), nodes = elements(tree);
    targets.set(path, { tree, nodes });
    const ids = nodes.filter(n => n.attrs.id).map(n => n.attrs.id);
    assert(new Set(ids).size === ids.length, `Duplicate static DOM IDs ${path}`);
    assert(nodes.filter(n => n.attrs['data-tex']).every(n => n.attrs['data-rendered'] === 'katex' && elements(n).some(e => e.tag === 'math')), `Unrendered or inaccessible mathematics in published page ${path}`);
    assert(!html.includes('__BOOK_BASE__'), `Unresolved site-base token ${path}`);
    assert(!/(?:C:\\Users\\|file:\/\/)/i.test(html), `Private/local publication path ${path}`);
    const authorMeta = nodes.filter(n => n.tag === 'meta' && n.attrs.name?.toLowerCase() === 'author');
    assert(authorMeta.length === 1 && authorMeta[0].attrs.content === confirmedAuthor, `Missing/incorrect human-author metadata ${path}`);
    if (authorMeta.length === 1 && authorMeta[0].attrs.content === confirmedAuthor) htmlAuthorMetaChecked++;
    const schemas = [];
    for (const node of nodes.filter(n => n.tag === 'script' && n.attrs.type === 'application/ld+json')) {
      try {
        const parsed = JSON.parse(textOf(node));
        schemas.push(...(Array.isArray(parsed) ? parsed : [parsed]));
      } catch { failures.push(`Malformed publication JSON-LD ${path}`); }
    }
    const bookSchemas = schemas.flatMap(s => s['@graph'] ?? [s]).filter(s => s['@type'] === 'Book' || (Array.isArray(s['@type']) && s['@type'].includes('Book')));
    const validBookAuthor = bookSchemas.length === 1 && bookSchemas[0].name === book.metadata.title
      && bookSchemas[0].author?.['@type'] === 'Person' && bookSchemas[0].author.name === confirmedAuthor;
    assert(validBookAuthor, `Missing/incorrect human-author Book schema ${path}`);
    if (validBookAuthor) htmlBookAuthorSchemaChecked++;
  }
  for (const chapter of book.chapters) assert(targets.has(`chapters/${chapter.slug}/index.html`), `Missing built chapter ${chapter.id}`);
  assert(targets.has('index.html') && targets.has('references/index.html'), 'Missing built book or references index');
  for (const path of ['index.html', 'about/index.html']) {
    const page = targets.get(path);
    const credits = page?.nodes.filter(n => n.attrs['data-author-credit'] !== undefined) ?? [];
    assert(credits.length === 1 && textOf(credits[0]).replace(/\s+/g, ' ').trim() === confirmedAuthor
      && !Object.hasOwn(credits[0].attrs, 'hidden') && credits[0].attrs['aria-hidden'] !== 'true', `Missing/incorrect visible author byline ${path}`);
  }
  for (const chapter of book.chapters) {
    const published = targets.get(`chapters/${chapter.slug}/index.html`);
    if (!published) continue;
    const content = published.nodes.find(n => (n.attrs.class ?? '').split(/\s+/).includes('prose'));
    assert(content, `Missing rendered chapter-content container ${chapter.id}`);
    if (!content) continue;
    const tree = content, nodes = elements(content);
    assert(published.nodes.some(n => n.tag === 'h1' && norm(textOf(n)) === norm(chapter.title)), `Built chapter title differs ${chapter.id}`);
    const visible = norm(textOf(tree, true));
    let at = 0;
    for (const paragraph of chapterParagraphs.get(chapter.id)) {
      const found = visible.indexOf(paragraph, at);
      assert(found >= 0, `Built chapter lost/reordered source prose: ${chapter.id}: ${paragraph.slice(0, 100)}`);
      if (found >= 0) at = found + paragraph.length;
    }
    const original = elements(documentTrees.get(`chapters/${chapter.slug}/`));
    for (const attr of ['data-cite-key', 'data-ref-label', 'data-source-path']) {
      assert(same(nodes.filter(n => n.attrs[attr]).map(n => n.attrs[attr] === 'true' ? textOf(n) : n.attrs[attr]), original.filter(n => n.attrs[attr]).map(n => n.attrs[attr] === 'true' ? textOf(n) : n.attrs[attr])), `Built chapter occurrence loss/duplication ${chapter.id}: ${attr}`);
    }
    const renderedMath = nodes.filter(n => n.attrs['data-tex']);
    assert(same(renderedMath.map(n => n.attrs['data-tex']), original.filter(n => n.attrs['data-tex']).map(n => n.attrs['data-tex'])), `Built chapter mathematics loss/duplication ${chapter.id}`);
    assert(renderedMath.every(n => n.attrs['data-rendered'] === 'katex' && elements(n).some(e => e.tag === 'math')), `Unrendered or inaccessible mathematics ${chapter.id}`);
    const equationRegions = nodes.filter(n => (n.attrs.class ?? '').split(/\s+/).includes('equation'));
    assert(equationRegions.length === chapter.equations.length && equationRegions.every(n => n.attrs.tabindex === '0' && n.attrs.role === 'region' && n.attrs['aria-label']?.trim() && elements(n).filter(e => e.attrs['data-display'] === 'true').length === 1), `Missing keyboard-accessible display-equation region ${chapter.id}`);
    for (const figure of chapter.figures) {
      const fig = nodes.find(n => n.attrs.id === figure.id);
      assert(fig && norm(textOf(fig, true)) === norm(textOf(original.find(n => n.attrs.id === figure.id), true)), `Built figure caption loss ${figure.id}`);
    }
    for (const table of chapter.tables) {
      const actual = nodes.find(n => n.attrs.id === table.id), expectedTable = original.find(n => n.attrs.id === table.id);
      assert(actual && norm(textOf(actual, true)) === norm(textOf(expectedTable, true)), `Built table caption/cell text loss ${table.id}`);
      assert(actual && same(numericLiterals(textOf(actual, true)), numericLiterals(textOf(expectedTable, true))), `Built table numeric literal change ${table.id}`);
    }
  }
  const referencePage = targets.get('references/index.html');
  if (referencePage) for (const ref of book.references) {
    const row = referencePage.nodes.find(n => n.attrs.id === ref.id);
    assert(row && norm(textOf(row, true)).includes(norm(textOf(htmlTree(ref.html), true))), `Built bibliography entry missing/truncated ${ref.key}`);
  }
  const aboutPage = targets.get('about/index.html');
  assert(aboutPage, 'Missing published front matter and evidence disclosures');
  if (aboutPage) {
    const visible = norm(textOf(aboutPage.tree, true)); let at = 0;
    for (const paragraph of frontParagraphs) {
      const found = visible.indexOf(paragraph, at);
      assert(found >= 0, 'Built about page lost/reordered accepted front-matter prose/disclosures');
      if (found >= 0) at = found + paragraph.length;
    }
  }
  let localLinks = 0;
  for (const [path, { nodes }] of targets) for (const node of nodes) {
    for (const attr of ['href', 'src', 'poster']) {
      const href = node.attrs[attr]; if (!href || /^(?:https?:|mailto:|tel:|data:)/i.test(href)) continue;
      assert(!/^(?:javascript|file):/i.test(href), `Disallowed URL scheme ${path}: ${href}`);
      if (/^[a-z][a-z0-9+.-]*:/i.test(href)) continue;
      const current = new URL(base + path.replace(/index\.html$/, ''), 'https://neuralatlasai.github.io');
      const url = new URL(href, current);
      if (url.origin !== current.origin) continue;
      localLinks++;
      assert(url.pathname.startsWith(base), `Internal URL escapes deployment base ${path}: ${href}`);
      let target = decodeURIComponent(url.pathname.slice(base.length));
      if (!target || target.endsWith('/')) target += 'index.html';
      else if (!byPath.has(target) && byPath.has(target + '/index.html')) target += '/index.html';
      assert(byPath.has(target), `Missing local URL ${path}: ${href}`);
      if (url.hash && targets.has(target)) {
        const anchor = decodeURIComponent(url.hash.slice(1));
        assert(targets.get(target).nodes.some(n => n.attrs.id === anchor), `Missing local anchor ${path}: ${href}`);
      }
    }
  }
  const allowedFigures = new Set(manifest.assets.map(a => a.source.split('/').at(-1)));
  const allowedHtml = new Set(['index.html', 'book/index.html', 'about/index.html', 'licenses/index.html', 'references/index.html', 'figures/index.html', 'reading-paths/index.html', '404.html', ...book.chapters.map(c => `chapters/${c.slug}/index.html`)]);
  const allowedLicenses = new Set(['inter', 'source-serif-4', 'phosphor', 'katex', 'astro', 'preact', 'minisearch', 'et-book'].map(name => `licenses/${name}.txt`));
  const unexpected = [];
  for (const [path] of byPath) {
    const allowed = allowedHtml.has(path) || path.startsWith('_astro/') || path === '.nojekyll' || path === 'robots.txt' || path === 'search.json' || /^sitemap[^/]*\.xml$/.test(path)
      || /^brand\/[^/]+\.(?:png|webp|svg)$/.test(path) || allowedLicenses.has(path) || pinnedPublicAssets.has(path)
      || ['downloads/agentic-state.pdf', 'downloads/agentic-state-source.zip', 'downloads/validation.json', 'downloads/source-crosswalk.csv'].includes(path)
      || (path.startsWith('figures/') && allowedFigures.has(path.slice(8)));
    assert(allowed, `Unexpected published file ${path}`);
    if (!allowed) unexpected.push(path);
    assert(!/(?:^|\/)(?:context|internal|tmp|build|node_modules)(?:\/|$)|\.(?:tex|bib|aux|bbl|blg|py|ts|mjs|map)$/i.test(path), `Private/source/cache file published ${path}`);
  }
  for (const [path, expectedAsset] of pinnedPublicAssets) {
    assert(byPath.has(path), `Missing pinned public asset ${path}`);
    if (byPath.has(path)) {
      const bytes = await readFile(byPath.get(path));
      assert(bytes.length === expectedAsset.bytes && hash(bytes) === expectedAsset.sha256, `Modified pinned public asset ${path}`);
    }
  }
  if (byPath.has('search.json')) {
    const records = JSON.parse(await readFile(byPath.get('search.json'), 'utf8'));
    const expectedSearch = new Map(book.chapters.flatMap(c => [
      [c.id, { title: c.title, number: String(c.number), url: base + `chapters/${c.slug}/` }],
      ...c.sections.filter(s => s.level === 1).map(s => [s.id, { title: s.title, number: s.number, url: base + `chapters/${c.slug}/#${s.anchor}` }])
    ]));
    assert(Array.isArray(records) && records.length === expectedSearch.size, 'Search index chapter/section coverage differs');
    if (Array.isArray(records)) assert(new Set(records.map(r => r.id)).size === records.length, 'Duplicate search entries');
    if (Array.isArray(records)) for (const record of records) {
      assert(['id', 'title', 'chapter', 'number', 'url', 'text'].every(k => typeof record[k] === 'string'), `Malformed search entry ${record.id}`);
      const expected = expectedSearch.get(record.id);
      assert(expected && record.title === expected.title && record.number === expected.number && record.url === expected.url, `Search index source identity mismatch ${record.id}`);
      assert(record.url.startsWith(base) && record.text.trim().length > 0, `Unscoped or empty search entry ${record.id}`);
      const u = new URL(record.url, 'https://neuralatlasai.github.io');
      let target = decodeURIComponent(u.pathname.slice(base.length)); if (target.endsWith('/')) target += 'index.html';
      assert(targets.has(target) && (!u.hash || targets.get(target).nodes.some(n => n.attrs.id === decodeURIComponent(u.hash.slice(1)))), `Broken search destination ${record.id}`);
    }
  } else failures.push('Missing published search index');
  for (const asset of manifest.assets) {
    const path = 'figures/' + asset.source.split('/').at(-1);
    assert(byPath.has(path) && hash(await readFile(byPath.get(path))) === asset.sha256, `Missing/stale published figure ${asset.id}`);
  }
  for (const [source, target] of [['output/pdf/agentic_state_monograph.pdf', 'downloads/agentic-state.pdf'], ['output/source/agentic_state_source.zip', 'downloads/agentic-state-source.zip'], ['book/validation_summary.json', 'downloads/validation.json'], ['book/current_source_review_20261029.csv', 'downloads/source-crosswalk.csv']]) {
    assert(byPath.has(target) && hash(await readFile(byPath.get(target))) === hash(await readFile(resolve(root, source))), `Stale/missing published download ${target}`);
  }
  publication = { htmlPages: targets.size, files: files.length, localLinksChecked: localLinks, pinnedPublicAssetsChecked: pinnedPublicAssets.size, htmlAuthorMetaChecked, htmlBookAuthorSchemaChecked, unexpectedPublishedFiles: unexpected };
}

const report = { status: failures.length ? 'failed' : 'passed', acceptedPdfSha256: book.metadata.acceptedPdfSha256,
  authorBinding: { confirmedAuthor, source: authorSourcePath, pdfInfo: pdfAuthor, generatedAuthor: book.metadata.author ?? null,
    scope: 'Human authorship credit and source/PDF/web identity binding; no claim of scientific endorsement or independent experimental reproduction.' },
  sourceDigest: manifest.sourceDigest, manifestedSourceFiles: manifest.files.length, chapters: chapterReports,
  frontMatter: { proseParagraphs: frontParagraphs.length, inlineMath: frontMath.length },
  counts: expected, publication, scope: 'Known-construct source and static-publication parity audit; no claim of independent scientific experimental reproduction.',
  failures };
console.log(JSON.stringify(report, null, 2));
if (failures.length) process.exitCode = 1;
