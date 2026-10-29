#!/usr/bin/env python3
"""Render the index from plan metadata without changing manuscript source.

--actual-pages PATH accepts a final audit with validation_status="complete",
body_pages, and pdf_sha256. Actual pagination is not displayed by default.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def readable_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return f"{parsed.day} {parsed.strftime('%B %Y')}"


def child_lines(entries: list[dict], depth: int = 1) -> list[str]:
    result = []
    for entry in entries:
        result.append("   " * depth + f'- [{entry["title"]}]({entry["path"]})')
        result.extend(child_lines(entry.get("subsection_entries", []), depth + 1))
    return result


def read_actual_audit(path: Path | None) -> dict | None:
    if path is None:
        return None
    audit = json.loads(path.read_text(encoding="utf-8"))
    if audit.get("validation_status") != "complete":
        raise ValueError("Actual-page display requires a completed final pagination audit.")
    pages = audit.get("body_pages")
    if isinstance(pages, bool) or not isinstance(pages, int) or pages < 1:
        raise ValueError("Pagination audit body_pages must be a positive integer.")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", audit.get("pdf_sha256", "")):
        raise ValueError("Pagination audit requires the final PDF SHA-256.")
    return audit


def render(plan: dict, actual: dict | None = None) -> str:
    cutoff = readable_date(plan["literature_cutoff"])
    retrieval_text = " to ".join(readable_date(day) for day in plan.get("retrieval_interval", []))
    chapters = plan["chapters"]
    illustration_state = plan.get("illustration_validation_status", "pending")
    pdf_state = plan.get("final_pdf_validation_status", "pending")
    if illustration_state == pdf_state == "complete":
        validation_text = "Final illustration and PDF validation are complete."
    elif illustration_state == pdf_state == "pending":
        validation_text = "Final illustration and PDF validation remain pending."
    else:
        validation_text = (
            f"Illustration validation: {illustration_state}; "
            f"final PDF validation: {pdf_state}."
        )
    lines = [
        "# " + plan["title"], "", plan["subtitle"], "",
        f'Literature cutoff and source review: **{cutoff}** for all {len(chapters)} chapters. '
        f'Primary-source inspection: **{retrieval_text}**. '
        f'Source review is complete. {validation_text}', "",
        f'Planned substantive allocation: **{plan["target_substantive_pages"]} pages** '
        f'(minimum {plan["minimum_substantive_pages"]}). '
        'These are editorial page budgets, not actual pagination.', "",
    ]
    if actual is not None:
        lines.extend([
            f'Final audited body pages: **{actual["body_pages"]}**. '
            f'Pagination audit is bound to PDF SHA-256 {actual["pdf_sha256"]}.', "",
        ])
    lines.extend([
        '## Contribution and evidence boundary', "", plan["organizing_contribution"], "",
        'Three separate obligations organize the analysis: preserve decision-relevant conditioning, '
        'prevent unauthorized expansion of executable actions, and retain the evidence needed to '
        'reconstruct external effects. The manuscript derives their non-implication, connects them '
        'to current implementations, and proposes experiments that can reject claims about their '
        'composition. It does not claim new empirical measurements, unrestricted AGI, or indefinite '
        'recursive improvement.', "",
        '## Connected research threads', "",
        '| Thread | Connected chapters | Boundary examined |', '|---|---|---|',
        '| Representation to decision | C03 &rarr; C05 &rarr; C06 &rarr; C10 &rarr; C11 | Decision-relevant distinctions under intervention. |',
        '| Context to learning | C08 &rarr; C11 &rarr; C12 &rarr; C17 &rarr; C30 | Behavior conditioning and co-adaptation. |',
        '| Memory to execution | C13 &rarr; C14 &rarr; C15 &rarr; C16 &rarr; C18 &rarr; C20 | Provenance, validity, applicability, and effect identity. |',
        '| Authority to effects | C18 &rarr; C19 &rarr; C20 &rarr; C28 &rarr; C29 &rarr; C32 | Permission, enforcement, commitment, and recovery. |',
        '| Measurement to improvement | C25 &rarr; C26 &rarr; C27 &rarr; C30 &rarr; C33 | Verifier error, leakage, longitudinal effects, and transfer. |',
        '| Physical to semantic state | C04 &rarr; C12 &rarr; C17 &rarr; C31 &rarr; C32 | Computational cache identity and state migration. |', "",
        '## Hierarchical chapter index', "",
    ])
    parts = {
        1: 'System semantics and scientific identification',
        3: 'Model computation and interactive learning',
        11: 'Context, sessions, memory, and conditioning',
        18: 'Tools, protocols, execution, and domain systems',
        25: 'Inspection, evaluation, security, and alignment',
        30: 'Adaptation, infrastructure, and cross-layer synthesis',
    }
    by_id = {chapter["id"]: chapter for chapter in chapters}
    for chapter in chapters:
        if chapter["number"] in parts:
            lines.extend(['### ' + parts[chapter["number"]], ""])
        prerequisites = ', '.join(
            f'[{ident}]({by_id[ident]["path"]})' for ident in chapter["prerequisites"]
        ) or 'System-level problem formulation.'
        lines.extend([
            f'#### {chapter["id"]} [{chapter["title"]}]({chapter["path"]})', "",
            '**Objective and analytical output.** ' + chapter["technical_output"], "",
            '**Contemporary evidence anchor.** ' + chapter["frontier_anchor"], "",
            '**Prerequisites.** ' + prerequisites, "",
            f'**Planned allocation.** {chapter["target_pages"]} substantive pages. '
            f'**Source review.** {readable_date(chapter["last_source_review"])}.', "",
        ])
        for number, section in enumerate(chapter["sections"], 1):
            lines.append(f'{number}. [{section["title"]}]({section["path"]})')
            if "subsection_entries" in section:
                lines.extend(child_lines(section["subsection_entries"]))
            else:
                lines.extend('   - ' + title for title in section.get("subsections", []))
        lines.append("")
    lines.extend([
        '## Companion research maps', "",
        '- [Topic-to-source and passage coverage](book/coverage.csv). This distinguishes mechanism coverage from unresolved paper-specific evidence.',
        '- [Section-level editorial page budgets](book/section_budgets.csv). The 370-page target is an allocation, not an actual page count.',
        '- [Versioned bibliography](book/references.bib). Source verification does not imply experimental reproduction.',
        '- [Chapter review status](book/chapter_review_status.json) records source completion separately from final illustration and PDF validation.',
        '- [Chapter 1 source crosswalk](book/chapter_review_sources.csv) supplies its detailed source-to-claim mapping.',
        '- [Figure manifest](book/figures/manifest.json) and [original prompts](book/figures/prompts). Scientific images use image generation; numerical evidence is typeset in tables.', "",
        'The analytical contribution is the cross-layer synthesis, explicit counterexamples, resource '
        'accounting, and discriminating experimental designs. Existing concepts and mechanisms retain '
        'their prior-art attribution.',
    ])
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--actual-pages', type=Path, help='Completed final pagination-audit JSON; omitted by default.')
    args = parser.parse_args()
    plan = json.loads((ROOT / 'book/plan.json').read_text(encoding='utf-8'))
    (ROOT / 'index.md').write_text(render(plan, read_actual_audit(args.actual_pages)), encoding='utf-8')
    print(f'Rendered connected index for {len(plan["chapters"])} chapters.')


if __name__ == '__main__':
    main()
