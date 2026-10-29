#!/usr/bin/env python3
"""Package a cumulative edition and its exact public source/figure provenance.

C34 also supports the conventional full-book workflow. --dry-run audits selected
payloads without writing an archive or changing manuscript source.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PARTS = {"internal", "context", "private", "build", "output", "tmp", ".git", "__pycache__",
                 "rejected", "rejected_drafts", "superseded"}
INPUT = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")
GRAPHIC = re.compile(r"\\includegraphics\*?(?:\s*\[[^\]]*\])?\s*\{([^{}]+)\}")
PUBLIC_MAPS = (
    "index.md", "BOOK.md", "publication_format.md", "LICENSE", ".latexmkrc",
    "book/coverage.csv", "book/revision_summary.md", "book/chapter_review_status.json",
    "book/chapter_review_sources.csv", "book/current_source_review_20261029.csv",
    "book/section_budgets.csv", "book/validation_summary.json",
    "book/figures/chapter_figure_plan.csv",
)

def public_file(root: Path, rel: str | Path) -> Path:
    path = (root / rel).resolve()
    try:
        name = path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Archive input leaves source root: {rel}") from exc
    if any(part.lower() in PRIVATE_PARTS for part in name.parts):
        raise ValueError(f"Private/generated input cannot enter source archive: {name}")
    if path.suffix.lower() in {".zip", ".pyc", ".pyo"}:
        raise ValueError(f"Archive/cache input cannot enter source archive: {name}")
    if not path.is_file():
        raise FileNotFoundError(path)
    return path

def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines(keepends=True):
        for index, char in enumerate(line):
            if char != "%":
                continue
            previous = index - 1
            while previous >= 0 and line[previous] == "\\":
                previous -= 1
            if (index - previous - 1) % 2 == 0:
                line = line[:index] + ("\n" if line.endswith("\n") else "")
                break
        lines.append(line)
    return "".join(lines)

def active_sources(root: Path, chapters: list[dict]) -> list[Path]:
    result, seen, active = [], set(), set()
    def visit(rel: str | Path) -> None:
        rel = Path(rel)
        if not rel.suffix:
            rel = rel.with_suffix(".tex")
        path = public_file(root, rel)
        if path in active:
            raise ValueError(f"Cyclic chapter include: {path.relative_to(root)}")
        if path in seen:
            return
        seen.add(path)
        active.add(path)
        result.append(path)
        for child in INPUT.findall(strip_comments(path.read_text(encoding="utf-8"))):
            visit(child)
        active.remove(path)
    for chapter in chapters:
        visit(chapter["path"])
    return result

def archive_readme(last: dict, date: str, full: bool) -> str:
    if full:
        workflow = """python tools/build_book.py
python tools/validate_book.py --require-current-build

# Alternatively rebuild the dated cumulative edition:
python tools/build_review.py --through C34
python tools/package_review.py --through C34"""
        contents = ("All 34 chapters, the conventional monograph driver, combined and input bibliographies, "
                    "public build/validation/package tools, configuration, research maps, active figures, "
                    "original prompts and declared generated edit inputs are included.")
        note = ("The distributed section inventory is already synchronized. The normal rebuild starts "
                "with build_book.py. The legacy sync_book.py migration helper can write chapter drivers "
                "and modules; it is not needed to rebuild this archive. Source packaging with "
                "package_review.py follows a build_review.py run and retains declared figure edit inputs.")
    else:
        workflow = f"python tools/build_review.py --through {last['id']}"
        contents = ("Only the included chapter prefix, its cited bibliography, configuration, "
                    "cumulative-build tools and active figure provenance are included. Other chapter "
                    "bodies and full-book bibliography inputs are excluded.")
        note = ("The plan retains contextual chapter identities. References outside this prefix print "
                "contextual chapter numbers without misleading local destinations.")
    workflow = "\n".join("    " + line if line else "" for line in workflow.splitlines())
    return f"""# Agentic State: cumulative Chapters 1-{last['number']}

Literature and implementation review: {date}. {contents}

Build from the extracted source root:

{workflow}

Requirements: Python 3.10+, pdfLaTeX, BibTeX, IEEEtran bibliography style, Latin Modern and the declared TeX packages. Python tooling uses PyMuPDF, pypdf and Pillow. Compilation uses no network service or API credentials; install external dependencies before building.

{note}

Generated output directories are created by the tools. Prior PDFs, archives, build intermediates, supplied corpus, private research ledgers and caches are not distributed. The source manifest hashes the exact bytes of every payload member except itself, including prompts, edit inputs and the scoped figure manifest.

Compilation and mechanical validation do not establish visual fidelity or scientific validity. Body-page accounting excludes front matter and references and requires final review. Source/code inspection is not experimental reproduction. Original explanatory illustrations use the built-in image-generation tool; its exact model identifier was not exposed.
"""

def collect_payload(root: Path, plan: dict, chapters: list[dict], build: dict) -> tuple[dict[str, bytes], dict]:
    root = root.resolve()
    last = chapters[-1]
    full = len(chapters) == len(plan["chapters"])
    tag = f'ch01-{last["number"]:02d}'
    files: set[Path] = set()
    def add(rel: str | Path) -> None:
        files.add(public_file(root, rel))
    for rel in ("tools/build_review.py", "tools/review_sources.py", "tools/package_review.py",
                "book/plan.json", f"book/{tag}_references.bib"):
        add(rel)
    for path in (root / "config").glob("*.tex"):
        add(path)
    sources = active_sources(root, chapters)
    files.update(sources)
    if full:
        for rel in ("monograph.tex", "book/frontmatter.tex", "book/references.bib",
                    "bibliography/references.bib", "tools/build_book.py", "tools/validate_book.py",
                    "tools/package_sources.py"):
            add(rel)
        for path in (root / "tools").glob("*.py"):
            add(path)
        for path in (root / "bibliography").glob("*.bib"):
            add(path)
        for rel in PUBLIC_MAPS:
            if (root / rel).is_file():
                add(rel)
        # Follow the actual conventional driver too, including nested frontmatter/config inputs.
        for source in active_sources(root, [{"path": "monograph.tex"}]):
            files.add(source)
            if source not in sources:
                sources.append(source)
    for rel in (f"book/{tag}_validation.json", "book/figures/visual_grammar.md"):
        if (root / rel).is_file():
            add(rel)
    manifest_path = public_file(root, "book/figures/manifest.json")
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    entries = manifest.get("figures", [])
    by_asset = {entry["asset"]: entry for entry in entries}
    if len(by_asset) != len(entries):
        raise ValueError("Duplicate asset in figure manifest")
    graphics = set()
    for source in sources:
        for raw in GRAPHIC.findall(strip_comments(source.read_text(encoding="utf-8"))):
            normalized = Path(raw).as_posix()
            if normalized not in by_asset and not Path(raw).suffix:
                candidates = [name for name in by_asset if str(Path(name).with_suffix("")) == normalized]
                if len(candidates) == 1:
                    normalized = candidates[0]
            graphics.add(normalized)
    if missing := graphics - by_asset.keys():
        raise ValueError("Unmanifested publication figures: " + str(sorted(missing)))
    selected = [entry for entry in entries if entry["asset"] in graphics]
    expected_hashes, visited, edit_inputs, active_inputs = {}, set(), set(), set()
    def include_figure(entry: dict) -> None:
        asset = entry["asset"]
        if asset in active_inputs:
            raise ValueError("Cyclic figure-generation input: " + asset)
        if asset in visited:
            return
        active_inputs.add(asset)
        add(asset)
        expected = entry.get("sha256")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
            raise ValueError("Figure lacks a valid recorded hash: " + asset)
        expected_hashes[asset] = expected.lower()
        add(entry.get("prompt") or f"book/figures/prompts/{Path(asset).stem}.txt")
        for rel in entry.get("referenced_prompts", []):
            add(rel)
        for rel in entry.get("referenced_assets", []):
            edit_inputs.add(rel)
            if rel in by_asset:
                include_figure(by_asset[rel])
            else:
                add(rel)
                prompt = f"book/figures/prompts/{Path(rel).stem}.txt"
                if (root / prompt).is_file():
                    add(prompt)
        active_inputs.remove(asset)
        visited.add(asset)
    for entry in selected:
        include_figure(entry)
    scoped = deepcopy(manifest)
    scoped["figures"] = selected
    # Preserve exact reviewed manifest bytes when every recorded figure is active.
    scoped_bytes = manifest_raw if selected == entries else (json.dumps(scoped, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    payload = {path.relative_to(root).as_posix(): path.read_bytes() for path in sorted(files)}
    payload["README.md"] = archive_readme(last, build["reviewed_through"], full).encode("utf-8")
    payload["book/figures/manifest.json"] = scoped_bytes
    for asset, expected in expected_hashes.items():
        if hashlib.sha256(payload[asset]).hexdigest() != expected:
            raise ValueError("Figure changed from manifest hash: " + asset)
    summary = {"through": last["id"], "full_book": full, "active_figures": len(selected),
               "declared_edit_input_assets": len(edit_inputs),
               "public_tools": sum(name.startswith("tools/") for name in payload),
               "bibliography_inputs": sum(name.startswith("bibliography/") for name in payload),
               "current_source_review_map_included": "book/current_source_review_20261029.csv" in payload}
    return payload, summary

def manifest_rows(payload: dict[str, bytes]) -> list[dict]:
    return [{"path": name, "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}
            for name, blob in sorted(payload.items())]

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", required=True)
    parser.add_argument("--dry-run", action="store_true", help="Audit payload selection/hashes without writing an archive.")
    args = parser.parse_args()
    plan = json.loads((ROOT / "book/plan.json").read_text(encoding="utf-8"))
    last = next(chapter for chapter in plan["chapters"] if chapter["id"] == args.through)
    chapters = plan["chapters"][:plan["chapters"].index(last) + 1]
    tag = f'ch01-{last["number"]:02d}'
    build = json.loads((ROOT / "internal" / f"{tag}_build.json").read_text(encoding="utf-8"))
    if build.get("through") != args.through:
        raise ValueError("Build metadata does not match selected chapter prefix")
    payload, summary = collect_payload(ROOT, plan, chapters, build)
    rows = manifest_rows(payload)
    if args.dry_run:
        print(json.dumps({**summary, "archive_written": False, "payload_files": len(rows),
                          "files": [row["path"] for row in rows]}, indent=2))
        return
    source_manifest = {"through": args.through,
                       "scope": "Public cumulative source; excludes output artifacts, private provenance, corpus and caches.",
                       "reviewed_through": build["reviewed_through"],
                       "review_pdf_sha256": build.get("pdf_sha256"), "files": rows}
    destination = ROOT / f'output/source/agentic_state_{tag}_{build["reviewed_through"].replace("-", "")}_source.zip'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        # Write the exact byte snapshot that was hashed, even if source files later change.
        for name, blob in sorted(payload.items()):
            archive.writestr(name, blob)
        archive.writestr("source_manifest.json", json.dumps(source_manifest, indent=2) + "\n")
    report = {**summary, "archive": destination.relative_to(ROOT).as_posix(),
              "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
              "bytes": destination.stat().st_size, "payload_files": len(rows)}
    (destination.parent / (destination.stem + "_manifest.json")).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
