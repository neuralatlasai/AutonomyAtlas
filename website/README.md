# Agentic State online

The complete technical monograph, presented as a static research publication at
https://neuralatlasai.github.io/AutonomyAtlas/.

The interface is an original Astro and TypeScript implementation with a small
Preact search island. It provides chapter navigation, full-text search, reading
paths, an illustrated index, linked numeric references, light and dark themes,
and the complete PDF and modular LaTeX source. Scientific content is supplied by
the accepted manuscript, rather than rewritten for the website.

## Local development

Use Node.js 24 and the committed npm lockfile:

```powershell
cd website
npm ci
npm run build
npm run preview
```

Open http://127.0.0.1:4173/AutonomyAtlas/. The production base path is configured
in `astro.config.mjs`. For interactive development use `npm run dev` after the
first build has synchronized the original figures and downloads.

## Checks and publication

```powershell
npm run check
npm run check:content
npm run build
npm run check:links
```

The content audit binds the generated content to exact source hashes, checks
ordered prose, formulas, numeric table evidence, citations and labels, and
verifies the final publication's local links, accessible math, original assets
and public-file boundaries. These checks do not establish scientific validity
or reproduce the papers' experiments. Browser review is a separate check.

The GitHub Actions workflow builds and checks the static artifact before
deploying only `website/dist` to GitHub Pages. The supplied research corpus,
private review notes, caches and build directories are excluded.

## Source organization

- `src/pages`, `src/layouts`, `src/styles`: independent publication interface.
- `src/components`: standard interface icons and the full-text search island.
- `src/generated`: committed, audited semantic manuscript export.
- `tools`: bounded manuscript compiler, provenance manifest and math renderer.
- `scripts`: asset synchronization and independent publication audits.
- `brand-source`: original agent-mark prompt; only the finished PNG is published.

Read [the conversion contract](tools/README.md) before changing manuscript
conversion. A normal website build uses committed generated data and needs no
Pandoc, TeX installation, external API or credentials. Retain the exact source
bytes required by `.gitattributes` when regenerating the export.

## Attribution

Source Serif 4 and Inter are self-hosted under their font licenses; Phosphor
supplies interface icons and KaTeX renders mathematics with MathML. Their
license notices are copied into the publication. Scientific PNG illustrations
and the original agent mark were produced with an image-generation tool whose
exact model identifier was unavailable. Reference websites informed broad
editorial direction; their interface code and scientific content were not used.
