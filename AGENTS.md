# Research monograph maintenance

Read `BOOK.md` and `book/plan.json` before editing. The substantive rewrite supersedes the rejected architecture scaffold. Preserve user-provided corpus files. Use `book/plan.json` as the source of truth for chapter order and `index.md` as its public research index. Do not count outlines, previews, references, or blank pages as substantive manuscript pages.

Keep substantive prose in `book/chapters/NN-topic/sections/`. Chapter drivers include these modules. Never run legacy scaffold generators against the substantive book. Keep notation centralized, labels stable, bibliography keys unique, and chapter dependencies acyclic. Separate internal provenance from publication content.

Present algorithms as mathematical equations, recurrences, conditional distributions, feasible sets, or typed transition relations throughout the manuscript. Do not insert programming-style pseudocode blocks. Define symbols, operators, domains, stopping conditions, and invalid cases; brief explanatory comments are permitted. Retain actual repository identifiers in surrounding prose for implementation traceability.

Every quantitative claim needs a primary source version and claim location or actual reproduction evidence. Do not inherit prior verification labels or rankings. State source, implementation, experimental, and affiliation uncertainty separately. No invented experiments, results, references, capabilities, or author metadata.

Scientific figures must be generated with image-generation models. Never create them with plotting, diagram, SVG, TikZ, Mermaid, or Python code. Exact numerical evidence belongs in typeset tables. Check every generated label and arrow; disclose the actual tool/model only when known. Rendering PDF pages for QA is allowed.

Build with `python tools/build_book.py`. After index changes synchronize titles and section inventories without overwriting prose. Review the final rendered PDF after layout changes. Do not mark audits passed without supporting evidence. A compiled PDF is not evidence of human expert endorsement or independent experimental reproduction.
