# Agentic State

**Context, Memory, and Control in Adaptive AI**  
A Technical Monograph on Conditioning, Tool Execution, Verification, and Self-Improvement

The complete edition contains 34 chapters and 482 main-text pages (536 physical PDF pages), reviewed through 29 October 2026. It contains 266 sections, 39 subsections, 356 cited references and 35 original image-generated figures. The [connected index](index.md) records objectives, prerequisites and the actual section hierarchy. The [coverage map](book/coverage.csv) and [current source crosswalk](book/current_source_review_20261029.csv) retain paper-specific limits. No independent experimental reproduction or human expert endorsement is claimed.

[Full PDF](output/pdf/agentic_state_monograph.pdf) · [Source archive](output/source/agentic_state_source.zip) · [Validation](book/validation_summary.json)

## Modular source

`book/plan.json` records chapter order, prerequisites and section inventory. Each chapter has a driver and separate section modules under `book/chapters/`. Shared notation, packages and layout are in `config/`; the front matter is in `book/frontmatter.tex`. Bibliography inputs remain separate under `bibliography/`, with combined and cited-only versions under `book/`. Generated scientific assets, prompts and their provenance are under `book/figures/`.

The archive excludes the supplied corpus, private research ledgers, rejected drafts, caches and prior output artifacts. It contains every active chapter include, cited bibliography, shared configuration, figure and declared generated edit input required by its build.

## Rebuild and edit

Reproduce the dated cumulative edition from the extracted source root:

```powershell
python tools/build_review.py --through C34
python tools/package_review.py --through C34
```

The conventional full-book driver is also provided:

```powershell
python tools/build_book.py
python tools/validate_book.py --require-current-build
```

Python 3.10+, pdfLaTeX, BibTeX, IEEEtran bibliography style, Latin Modern and the declared TeX packages are required. The Python tools use PyMuPDF, pypdf and Pillow. The build requires no API credentials or network service. Install dependencies before building; automatic TeX package installation is disabled. The tools create output directories and iterate until contents and references stabilize.

Edit chapter prose in its section module, preserving citation keys and cross-reference labels. Present algorithms as mathematical recurrences, distributions, feasible sets or typed transitions, with brief explanations. Refresh the index with `python tools/render_index.py`; its actual-page display additionally requires a completed audit. The distributed inventory is already synchronized. The legacy `sync_book.py` migration helper rewrites drivers and is unnecessary for rebuilding this edition. Use `package_review.py` to retain generated figure edit-input provenance.

## Page and evidence accounting

The fixed layout is 165 by 241 mm with 11-point body type and 124 mm text width. Planned section budgets total 370 pages; actual pagination comes from the compiled main-text range. Front matter and references are excluded. Short chapter tails are disclosed and screened rather than filled or stretched. Exact numerical evidence is typeset in tables; conceptual illustrations contain no generated benchmark results.

Claims preserve primary-source scope, versions, populations and analytical assumptions. Pinned code inspection does not establish runtime behavior under an untested configuration. The source crosswalk includes explicit limits where current chapter-specific full-method revalidation is not established. Mechanical checks, visual inspection and scientific validity are separate judgments; [validation](book/validation_summary.json) states the performed checks.

## Scientific figures and publication

Every scientific illustration was authored or edited with the built-in image-generation tool. Its model identifier was unavailable; no exact model version is claimed. No plotting, SVG, TikZ or code-to-image figure authoring was used. PDF rasterization and contact sheets serve layout QA only. The [figure plan](book/figures/chapter_figure_plan.csv), prompts, assets, captions and hashes accompany the source.

The master is a monograph with IEEE-style references, numbered equations, units and cross-referenced figures. A journal derivative requires a selected venue, a narrowed contribution and named human authors; [publication format](publication_format.md) records that boundary. Physical paper proof and independent experimental reproduction were not performed.
