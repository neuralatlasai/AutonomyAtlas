# Accepted manuscript content pipeline

The checked-in `src/generated/book.json` is the semantic web edition. Normal Astro/Pages builds require Node and npm only. They do not require Pandoc or TeX.

To regenerate after an intentional manuscript update, first produce the accepted conventional LaTeX build, then run from the repository root:

```powershell
python website/tools/compile_book.py
cd website
node tools/render-math.mjs --check
npm run check:content
```

The generator was validated with Python 3.12.8 and Pandoc 2.19.2, AST API 1.22.2.1. It reads `book/plan.json`, recursively expands every chapter driver in actual include order, and uses `build/book/monograph.aux` and `.bbl` for accepted label numbers and the exact 356 IEEE bibliography entries. The two build-derived inputs are not needed in CI: the generated source manifest records their hashes, label map, and citation-number map. `--aux` and `--bbl` can select equivalent accepted build artifacts.

The bounded adapter preserves prose, inline code, math expressions, table cells, captions, citation keys, and canonical case-sensitive labels. Print-only column widths and spacing controls become semantic HTML structure. Exact repeated `longtable` continuation headers are removed only after equality checks; unique header and body contents remain. The original 217 numbered display environments are retained in equation records, with explicit tags for all 231 accepted equation numbers. The 35 PNG scientific figures are referenced with exact-byte hashes; the asset manifest tells the separate asset-sync build step which originals to copy.

Unsupported raw TeX, source-counter/AUX disagreement, unresolved identities, missing figures, and accepted-corpus count changes stop generation. A changed `L{...}` table-column declaration is adapted only within a table's column specification. All text, formula, and table content is still supplied by the manuscript; the generator does not summarize or rewrite it.

`source-manifest.json` records exact input hashes, actual chapter include order, per-chapter counts and expanded-source hashes, private paragraph-emission diagnostics, accepted numbering maps, original figure hashes, converter hash, and generated JSON hash. Preserve input bytes across Git checkout, or deliberately coordinate a new newline-hash convention before regenerating. A normal website build should reject stale generated content through the independent checker.

The server-only `renderMathHtml(html)` helper renders `.math[data-tex][data-display]` nodes with pinned KaTeX 0.18.7, strict errors, `trust: false`, and accessible HTML plus MathML. It retains each escaped source expression and is idempotent. The current corpus passes all 2,394 nodes: 217 display environments, 2,166 chapter-inline nodes, ten front-matter nodes, and one bibliography node. It does not generate scientific illustrations.

All internal chapter and reference URLs, and original-figure URLs, use `__BOOK_BASE__`; the Astro renderer replaces this with its configured base URL. Chapter routes are `chapters/01-system/` through `chapters/34-synthesis/`. References use `references/#ref-<citation-key>`. Canonical label IDs, including colons and original case, are preserved verbatim. Each chapter's `html` includes its `leadHtml`; do not render the lead twice. Original paragraph headings are `h5`, with relative section level four.

This pipeline proves scoped content correspondence through structural, identity, source-hash, strict math-rendering, and independent prose/table audits. It does not imply a universal lossless TeX converter or reproduce scientific experiments. Responsive layout, keyboard interaction, accessible reading order, equation overflow, and figure legibility still require rendered browser review.
