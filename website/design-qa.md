# Online edition review — 29 October 2026

## Design direction

The interface is independently authored. The previous publication's landing
page informed its editorial restraint; its reader and interface code were not
reused. This edition uses copper and charcoal, a new generated agent mark,
Source Serif 4 reading typography, an unobstructed main column, a contextual
right-hand contents panel and a separate complete-book drawer. Original
scientific figures illustrate mechanisms rather than supply decorative imagery.

## Rendered review

Reviewed in Chrome at desktop width (1280 × 720 window capture) and with a
390-pixel responsive phone viewport. Examined the home page, chapter heading
and prose, section navigation reached through search, search results, mobile
reader and contents, dark theme, and reference filtering. The search keyboard
path opened the selected memory section with its original anchor. The mobile
drawer exposes all four publication destinations as well as chapter groups.
The agent mark and reading text remain legible in dark mode.

Review captures were retained separately from the published artifact. The
review is representative browser inspection, rather than a claim that every
browser, assistive technology or viewport has been tested.

## Resolved findings

- Corrected Fontsource stylesheet entry points.
- Included every semantic table wrapper in the horizontal-scroll style.
- Preserved the search icon when hiding the mobile text label.
- Added narrow-header spacing and publication links in the mobile drawer.
- Added labelled, keyboard-focusable display-equation scroll regions.
- Kept citation links inline inside scientific figure captions.
- Queued search requests arriving before island hydration.
- Restricted reader highlighting to headings represented in its contents.
- Decoded search snippets without exposing HTML entity escapes.
- Added live filter counts and a theme button naming its next action.
- Kept front-matter headings subordinate to the online edition heading.
- Retained third-party notices with shipped fonts and interface libraries.

## Mechanical evidence

TypeScript and Astro checks pass. The independent source and final-HTML audit
passes all 34 chapters, 2,169 ordered prose paragraphs, 37 semantic tables,
35 original figure assets, 356 references, 217 display environments and all
468 original label targets. It checks actual rendered MathML and exact source
expressions, numeric table literals, local destinations, download bytes and
the static-publication file boundary. No supplied corpus or private research
ledger is included in the deployed artifact.

No unresolved blocking visual or functional issue was identified in this
review. Scientific claims and experimental reproduction are outside UI QA.
