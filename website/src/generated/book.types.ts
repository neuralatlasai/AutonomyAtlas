/** Semantic content generated from the accepted manuscript; no UI concerns. */
export interface Section {
  id: string;
  title: string;
  anchor: string;
  /** Relative to chapter: 1=section, 2=subsection, 4=LaTeX paragraph heading. */
  level: number;
  number: string;
}
export interface Figure {
  id: string;
  number: string;
  src: string;
  captionHtml: string;
  captionText: string;
  alt: string;
  sha256: string;
}
export interface Equation {
  id: string;
  number: string;
  numbers: string[];
  labels: string[];
  kind: 'equation' | 'align';
  sourceTex: string;
  /** KaTeX input, with explicit accepted numbers and DOM-owned label anchors. */
  tex: string;
}
export interface Table {
  id: string;
  number: string;
  captionText: string;
  columnCount: number;
  rowCount: number;
}
export interface Chapter {
  id: string;
  number: number;
  slug: string;
  title: string;
  /** Introductory blocks before the first section; already also included in html. */
  leadHtml: string;
  html: string;
  sections: Section[];
  references: { key: string; number: number }[];
  figures: Figure[];
  equations: Equation[];
  tables: Table[];
  searchText: string;
  sourceSha256: string;
  counts: Record<string, number>;
}
export interface Reference {
  id: string;
  key: string;
  number: number;
  html: string;
  text: string;
  urls: string[];
  chapterIds: string[];
}
export interface Label {
  id: string;
  number: string;
  chapterId: string;
  type: string;
  href: string;
}
export interface Book {
  metadata: {
    schemaVersion: '1.0.0';
    title: string;
    subtitle: string;
    literatureCutoff: string;
    latestSourceRetrieval: string;
    editionType: string;
    sourceDigest: string;
    acceptedPdfSha256: string;
    converter: string;
    converterSha256: string;
    pandocVersion: string;
    metrics: Record<string, number>;
    frontMatterHtml: string;
  };
  chapters: Chapter[];
  references: Reference[];
  labels: Record<string, Label>;
}
