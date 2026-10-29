#!/usr/bin/env python3
"""Validate the substantive monograph's source graph and compiled artifact.

This is a mechanical validator, not a scientific referee or a visual reviewer.
It never counts planned budgets as completed pages. Run it again after any source
or PDF change. Findings are bound to source and artifact hashes in the report.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INPUT = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")
GRAPHIC = re.compile(r"\\includegraphics\*?(?:\s*\[[^\]]*\])?\s*\{([^{}]+)\}")
CITE = re.compile(r"\\(?:cite[A-Za-z]*|nocite)\*?(?:\s*\[[^\]]*\]){0,2}\s*\{([^{}]+)\}")
REF = re.compile(r"\\(?:ref|eqref|pageref|autoref|nameref|vref|Vref|cref|Cref)\*?\s*\{([^{}]+)\}")
LABEL = re.compile(r"\\label\s*\{([^{}]+)\}")
ENV = re.compile(r"\\(begin|end)\s*\{([^{}]+)\}")
SECTION = re.compile(r"\\section\*?\s*\{([^{}]+)\}")
PROGRAMMING_ENVIRONMENTS = frozenset({
    "verbatim", "verbatim*", "Verbatim", "Verbatim*", "BVerbatim", "LVerbatim",
    "SaveVerbatim", "VerbatimOut", "lstlisting", "lstlisting*", "minted", "minted*",
    "alltt", "algorithm", "algorithm*", "algorithmic", "algorithmic*",
    "algorithm2e", "algorithm2e*", "pseudocode", "pseudocode*", "program", "program*",
    "code", "code*", "listing", "listing*",
})
TEX_CONTROL = re.compile(r"\\([A-Za-z@]+|[^\r\n])")


def programming_environment_starts(text: str) -> list[dict[str, Any]]:
    """Find literal code-environment starts, excluding comments and inline text.

    This is a source-policy gate, not a TeX macro-expansion engine. Exact
    environment names prevent ordinary prose and repository paths from matching.
    """
    def whitespace(pos: int) -> int:
        while pos < len(text):
            if text[pos].isspace():
                pos += 1
            elif text[pos] == "%":
                end = text.find("\n", pos)
                pos = len(text) if end < 0 else end + 1
            else:
                break
        return pos

    def literal_end(pos: int, *, grouped: bool = True) -> int:
        if pos >= len(text):
            return pos
        opener = text[pos]
        if grouped and opener in "{[":
            closer, depth, pos = ("}" if opener == "{" else "]"), 1, pos + 1
            while pos < len(text) and depth:
                if text[pos] == "\\":
                    pos += 2
                    continue
                if text[pos] == opener:
                    depth += 1
                elif text[pos] == closer:
                    depth -= 1
                pos += 1
            return pos
        end = text.find(opener, pos + 1)
        return len(text) if end < 0 else end + 1

    found: list[dict[str, Any]] = []
    pos = 0
    while pos < len(text):
        if text[pos] == "%":
            end = text.find("\n", pos)
            pos = len(text) if end < 0 else end + 1
            continue
        if text[pos] != "\\":
            pos += 1
            continue
        control = TEX_CONTROL.match(text, pos)
        if control is None:
            pos += 1
            continue
        start, command, pos = pos, control.group(1), control.end()
        if command == "string":
            token = TEX_CONTROL.match(text, pos)
            pos = token.end() if token else min(pos + 1, len(text))
        elif command in {"verb", "lstinline", "mintinline", "path", "url", "nolinkurl", "detokenize"}:
            if pos < len(text) and text[pos] == "*":
                pos += 1
            # In \verb the next character is the delimiter, even when it is %.
            # Treating it as a comment would hide active TeX after the literal.
            if command != "verb":
                pos = whitespace(pos)
            if command in {"lstinline", "mintinline"} and pos < len(text) and text[pos] == "[":
                pos = whitespace(literal_end(pos))
            if command == "mintinline":
                pos = whitespace(literal_end(pos))  # Language argument.
            pos = literal_end(pos, grouped=command != "verb")
        elif command == "begin":
            pos = whitespace(pos)
            if pos < len(text) and text[pos] == "{":
                end = text.find("}", pos + 1)
                if end >= 0:
                    name = re.sub(r"%[^\n]*", "", text[pos + 1:end]).strip()
                    if name in PROGRAMMING_ENVIRONMENTS:
                        found.append({"environment": name, "line": text.count("\n", 0, start) + 1})
                    pos = end + 1
    return found


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_comments(text: str) -> str:
    """Strip unescaped TeX comments, preserving verbatim content and line count."""
    lines: list[str] = []
    verbatim = False
    for line in text.splitlines():
        if re.search(r"\\begin\{(?:verbatim\*?|lstlisting|minted)\}", line):
            verbatim = True
        if verbatim:
            lines.append(line)
        else:
            cut = len(line)
            for match in re.finditer("%", line):
                backslashes = len(line[:match.start()]) - len(line[:match.start()].rstrip("\\"))
                if backslashes % 2 == 0:
                    cut = match.start()
                    break
            lines.append(line[:cut])
        if re.search(r"\\end\{(?:verbatim\*?|lstlisting|minted)\}", line):
            verbatim = False
    return "\n".join(lines)


def mask_verbatim(text: str) -> str:
    """Do not parse example code as executable TeX input, citations or labels."""
    def blank(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")
    text = re.sub(
        r"\\begin\{(verbatim\*?|lstlisting|minted)\}.*?\\end\{\1\}",
        blank, text, flags=re.S,
    )
    return re.sub(r"\\verb\*?([^A-Za-z\s]).*?\1", "", text)


def lexical_words(text: str) -> int:
    text = mask_verbatim(strip_comments(text))
    for environment in ("equation", "equation*", "align", "align*", "gather", "gather*", "verbatim"):
        name = re.escape(environment)
        text = re.sub(r"\\begin\{" + name + r"\}.*?\\end\{" + name + r"\}", " ", text, flags=re.S)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\(?:label|cite[A-Za-z]*|ref|eqref|pageref|input|include|includegraphics|path|url)\*?(?:\[[^\]]*\])?\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?", " ", text)
    return len(re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text))


def bib_entries(text: str) -> list[dict[str, Any]]:
    """Read balanced BibTeX records; nested title braces remain intact."""
    records: list[dict[str, Any]] = []
    pos = 0
    start = re.compile(r"@(\w+)\s*([({])")
    while match := start.search(text, pos):
        kind = match.group(1).lower()
        opener = match.group(2)
        closer = "}" if opener == "{" else ")"
        depth, quoted, escaped = 1, False, False
        end = match.end()
        while end < len(text) and depth:
            char = text[end]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted:
                if char == opener:
                    depth += 1
                elif char == closer:
                    depth -= 1
            end += 1
        if depth:
            raise ValueError(f"Unclosed BibTeX {kind} record near offset {match.start()}")
        body = text[match.end():end - 1]
        pos = end
        if kind in {"comment", "preamble", "string"}:
            continue
        key, sep, rest = body.partition(",")
        if not sep:
            raise ValueError(f"BibTeX record has no key separator near offset {match.start()}")
        fields: dict[str, str] = {}
        cursor = 0
        field_start = re.compile(r"(?:^|,)\s*(\w+)\s*=\s*", re.S)
        while field := field_start.search(rest, cursor):
            name = field.group(1).lower()
            i = field.end()
            if i >= len(rest):
                break
            if rest[i] in '{"':
                begin = rest[i]
                finish = "}" if begin == "{" else '"'
                j, n, esc = i + 1, 1, False
                while j < len(rest) and n:
                    char = rest[j]
                    if esc:
                        esc = False
                    elif char == "\\":
                        esc = True
                    elif begin == "{" and char == "{":
                        n += 1
                    elif char == finish:
                        n -= 1
                    j += 1
                value = rest[i + 1:j - 1]
                cursor = j
            else:
                j = rest.find(",", i)
                if j < 0:
                    j = len(rest)
                value, cursor = rest[i:j].strip(), j
            fields[name] = value.strip()
        records.append({"key": key.strip(), "kind": kind, "fields": fields})
    return records


class Audit:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.errors: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.sources: dict[Path, str] = {}
        self.edges: dict[str, list[str]] = {}
        self.source_order: list[Path] = []

    def relative(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path.resolve())

    def finding(self, level: str, code: str, **details: Any) -> None:
        target = self.errors if level == "error" else self.warnings
        target.append({"code": code, **details})

    def resolve(self, raw: str, parent: Path, extensions: tuple[str, ...]) -> Path | None:
        if any(character in raw for character in ("#", "\\")):
            return None
        for base in (self.root, parent.parent):
            candidate = base / raw
            options = [candidate] if candidate.suffix else [candidate.with_suffix(ext) for ext in extensions]
            for path in options:
                if path.is_file():
                    return path.resolve()
        return None

    def walk(self, path: Path, active: tuple[Path, ...] = ()) -> None:
        path = path.resolve()
        if path in active:
            self.finding("error", "include_cycle", chain=[self.relative(p) for p in (*active, path)])
            return
        if path in self.sources:
            return
        if not path.is_file():
            self.finding("error", "missing_tex_input", path=self.relative(path))
            return
        text = path.read_text(encoding="utf-8-sig")
        clean = mask_verbatim(strip_comments(text))
        self.sources[path] = text
        self.source_order.append(path)
        self.edges[self.relative(path)] = []
        for match in INPUT.finditer(clean):
            raw = match.group(1).strip()
            child = self.resolve(raw, path, (".tex",))
            if child is None:
                self.finding("error", "unresolved_tex_input", path=self.relative(path), input=raw,
                             line=clean.count("\n", 0, match.start()) + 1)
                continue
            self.edges[self.relative(path)].append(self.relative(child))
            self.walk(child, (*active, path))

    def source_checks(self, plan: dict[str, Any]) -> dict[str, Any]:
        self.walk(self.root / "monograph.tex")
        # Inspect every chapter file, including orphans, before example masking.
        # A forbidden block must not disappear merely because the general TeX
        # parser correctly ignores its contents as non-executable source.
        chapter_sources = sorted((self.root / "book/chapters").rglob("*.tex"))
        programming_blocks: list[dict[str, Any]] = []
        for path in chapter_sources:
            for occurrence in programming_environment_starts(path.read_text(encoding="utf-8-sig")):
                details = {"path": self.relative(path), **occurrence}
                programming_blocks.append(details)
                self.finding("error", "programming_style_environment", **details,
                             requirement="Present algorithms as mathematical equations, recurrences, feasible sets, or typed transitions.")
        incoming: dict[str, list[str]] = defaultdict(list)
        for parent, children in self.edges.items():
            for child in children:
                incoming[child].append(parent)
        for child, parents in incoming.items():
            if child.startswith("book/chapters/") and len(parents) > 1:
                self.finding("error", "prose_module_included_multiple_times", path=child, parents=parents)
        chapters = plan.get("chapters", [])
        ids = [c.get("id") for c in chapters]
        for cid, count in Counter(ids).items():
            if count > 1:
                self.finding("error", "duplicate_chapter_id", chapter=cid, count=count)
        index = {c["id"]: c for c in chapters}
        visited: set[str] = set()

        def dependency(cid: str, stack: tuple[str, ...]) -> None:
            if cid in stack:
                self.finding("error", "prerequisite_cycle", chain=[*stack, cid])
                return
            if cid in visited:
                return
            for parent in index[cid].get("prerequisites", []):
                if parent not in index:
                    self.finding("error", "unknown_prerequisite", chapter=cid, prerequisite=parent)
                else:
                    if ids.index(parent) >= ids.index(cid):
                        self.finding("error", "prerequisite_after_consumer", chapter=cid, prerequisite=parent)
                    dependency(parent, (*stack, cid))
            visited.add(cid)

        chapter_report: list[dict[str, Any]] = []
        for c in chapters:
            dependency(c["id"], ())
            path = (self.root / c["path"]).resolve()
            if path not in self.sources:
                self.finding("error", "chapter_not_in_publication_graph", chapter=c["id"], path=c["path"])
            directory = (self.root / c.get("directory", str(path.parent))).resolve()
            modules = sorted(directory.rglob("*.tex")) if directory.is_dir() else []
            active = [p.resolve() for p in modules if p.resolve() in self.sources]
            for module in modules:
                if module.resolve() not in self.sources:
                    self.finding("error", "orphan_chapter_module", chapter=c["id"], path=self.relative(module))
            prose_modules = [p for p in active if p != path]
            for module in prose_modules:
                words = lexical_words(self.sources[module])
                if words == 0 and not INPUT.search(self.sources[module]) and not GRAPHIC.search(self.sources[module]):
                    self.finding("error", "empty_prose_module", path=self.relative(module))
                elif words < 80:
                    self.finding("warning", "short_module_requires_editorial_review", path=self.relative(module),
                                 approximate_prose_words=words)
            joined = "\n".join(self.sources[p] for p in active)
            total_words = sum(lexical_words(self.sources[p]) for p in active)
            if total_words < 500:
                self.finding("error", "chapter_lacks_substantive_prose", chapter=c["id"], approximate_prose_words=total_words)
            planned_paths = {str(s.get("path", "")) for s in c.get("sections", [])}
            for name in planned_paths:
                section_path = (self.root / name).resolve()
                if section_path not in self.sources:
                    self.finding("error", "planned_section_not_in_publication_graph", chapter=c["id"], path=name)
            chapter_report.append({"id": c["id"], "path": c["path"], "included_tex_modules": len(active),
                                   "section_headings": len(SECTION.findall(mask_verbatim(strip_comments(joined)))),
                                   "plan_section_records": len(c.get("sections", [])),
                                   "approximate_prose_words": total_words})

        labels: dict[str, list[dict[str, Any]]] = defaultdict(list)
        refs: dict[str, list[dict[str, Any]]] = defaultdict(list)
        cites: set[str] = set()
        figures: list[dict[str, Any]] = []
        for path in self.source_order:
            clean = mask_verbatim(strip_comments(self.sources[path]))
            for pattern, collection in ((LABEL, labels), (REF, refs)):
                for match in pattern.finditer(clean):
                    collection[match.group(1)].append({"path": self.relative(path),
                                                       "line": clean.count("\n", 0, match.start()) + 1})
            for match in re.finditer(r"\\hyperref\[([^\]]+)\]", clean):
                refs[match.group(1)].append({"path": self.relative(path), "line": clean.count("\n", 0, match.start()) + 1})
            for match in CITE.finditer(clean):
                cites.update(key.strip() for key in match.group(1).split(",") if key.strip() != "*")
            for match in GRAPHIC.finditer(clean):
                image = self.resolve(match.group(1), path, (".png", ".jpg", ".jpeg", ".pdf"))
                if image is None:
                    self.finding("error", "missing_figure_input", path=self.relative(path), asset=match.group(1))
                else:
                    figures.append({"source": self.relative(path), "asset": self.relative(image)})
            # Source environment balance catches common editing defects before compilation.
            stack: list[str] = []
            for match in ENV.finditer(clean):
                if match.group(1) == "begin":
                    stack.append(match.group(2))
                elif not stack or stack.pop() != match.group(2):
                    self.finding("error", "environment_mismatch", path=self.relative(path), environment=match.group(2),
                                 line=clean.count("\n", 0, match.start()) + 1)
            if stack:
                self.finding("error", "unclosed_environment", path=self.relative(path), environments=stack)
            if self.relative(path).startswith("book/"):
                self.leakage_checks(path, clean)

        for label, locations in labels.items():
            if len(locations) > 1:
                self.finding("error", "duplicate_label", label=label, locations=locations)
        for label, locations in refs.items():
            if label not in labels:
                self.finding("error", "unresolved_source_reference", label=label, locations=locations)
        bibliography = self.bibliography_checks(cites)
        figure_report = self.figure_checks(figures)
        all_hashes = {self.relative(path): digest(path) for path in self.source_order}
        for name in ("book/plan.json", "book/references.bib", "book/figures/manifest.json"):
            path = self.root / name
            if path.is_file():
                all_hashes[name] = digest(path)
        for record in figure_report:
            if record.get("actual_sha256"):
                all_hashes[record["asset"]] = record["actual_sha256"]
        return {"chapter_count": len(chapters), "chapters": chapter_report,
                "mathematical_presentation": {
                    "checked_chapter_tex_files": len(chapter_sources),
                    "forbidden_environments": sorted(PROGRAMMING_ENVIRONMENTS),
                    "programming_environment_occurrences": programming_blocks,
                    "scope": "Literal environment starts outside comments and inline literal commands; no TeX macro expansion or scientific validation.",
                },
                "included_tex_files": len(self.sources), "include_graph": self.edges,
                "label_count": len(labels), "reference_target_count": len(refs), "citation_key_count": len(cites),
                "bibliography": bibliography, "figures": figure_report,
                "input_hashes": all_hashes,
                "source_tree_sha256": hashlib.sha256(json.dumps(all_hashes, sort_keys=True).encode()).hexdigest()}

    def leakage_checks(self, path: Path, clean: str) -> None:
        # Compilation paths are not printed. Public repository paths in \path{}
        # remain eligible and are not classified as local provenance merely for
        # containing words such as "memory", "context", "internal" or "tools".
        publication = INPUT.sub("", clean)
        publication = GRAPHIC.sub("", publication)
        publication = re.sub(r"\\bibliography\{[^{}]+\}", "", publication)
        rules = {
            "private_absolute_path": r"(?:[A-Za-z]:[/\\]Users[/\\]|/mnt/data/|/home/oai/share/)",
            "private_workspace_identity": r"\b(?:AutonomyAtlas|Agentic_ai_research)\b",
            "private_provenance_path": r"(?:internal[/\\](?:extracted|.*(?:ledger|inventory|audit))|architecture[/\\](?:master_index|context_coverage)|book[/\\]chapters[/\\])",
            "tool_reference_token": r"\bturn\d+(?:search|view|fetch)\d+\b",
            "internal_drafting_instruction": r"\b(?:AGENTS\.md|SKILL\.md|DRAFTING NOTE|INSERT CHAPTER HERE|Lorem ipsum)\b",
        }
        for code, pattern in rules.items():
            for match in re.finditer(pattern, publication, flags=re.I):
                self.finding("error", code, path=self.relative(path),
                             line=publication.count("\n", 0, match.start()) + 1,
                             excerpt=publication[max(0, match.start() - 40):match.end() + 70].replace("\n", " "))

    def bibliography_checks(self, cited: set[str]) -> dict[str, Any]:
        path = self.root / "book/references.bib"
        if not path.is_file():
            self.finding("error", "missing_publication_bibliography", path=self.relative(path))
            return {}
        try:
            records = bib_entries(path.read_text(encoding="utf-8-sig"))
        except ValueError as error:
            self.finding("error", "invalid_bibliography", detail=str(error))
            return {}
        self.leakage_checks(path, strip_comments(path.read_text(encoding="utf-8-sig")))
        keys = Counter(r["key"] for r in records)
        for key, count in keys.items():
            if count > 1:
                self.finding("error", "duplicate_bibliography_key", key=key, count=count)
        for key in sorted(cited - keys.keys()):
            self.finding("error", "unresolved_citation_key", key=key)
        identities: dict[str, list[str]] = defaultdict(list)
        years: Counter[str] = Counter()
        for record in records:
            fields, key = record["fields"], record["key"]
            if record['kind'].lower() == 'ieeetranbstctl':
                continue
            for field in ("title", "author", "year"):
                if not fields.get(field):
                    self.finding("warning", "incomplete_bibliographic_identity", key=key, field=field)
            years[fields.get("year", "unknown")] += 1
            if fields.get("doi"):
                identities["doi:" + fields["doi"].lower().removeprefix("https://doi.org/")].append(key)
            arxiv = re.search(r"\b(\d{4}\.\d{4,5})(?:v\d+)?\b", fields.get("eprint", "") + " " + fields.get("url", ""))
            if arxiv:
                identities["arxiv:" + arxiv.group(1)].append(key)
        duplicates = [{"identifier": identifier, "keys": list(dict.fromkeys(group))}
                      for identifier, group in identities.items() if len(set(group)) > 1]
        if duplicates:
            self.finding("warning", "duplicate_publication_identity_requires_editorial_review", groups=duplicates,
                         meaning="Shared identifiers can be aliases or separate versions; this is not a fabricated-reference finding.")
        control_keys={r['key'] for r in records if r['kind'].lower()=='ieeetranbstctl'}
        return {"records": len(records)-len(control_keys), "style_control_records":len(control_keys), "cited_records": len((cited & keys.keys())-control_keys),
                "uncited_keys": sorted(keys.keys() - cited), "duplicate_identifier_groups": duplicates,
                "year_distribution": dict(sorted(years.items())),
                "scope": "Syntax/basic identity only; titles, authors, dates and source claims require primary-source verification."}

    def figure_checks(self, figures: list[dict[str, Any]]) -> list[dict[str, Any]]:
        path = self.root / "book/figures/manifest.json"
        if not path.is_file():
            self.finding("error", "missing_figure_manifest", path=self.relative(path))
            return []
        manifest = json.loads(path.read_text(encoding="utf-8-sig"))
        entries = manifest.get("figures", [])
        for field in ("id", "asset"):
            for value, count in Counter(f.get(field) for f in entries).items():
                if count > 1:
                    self.finding("error", "duplicate_figure_manifest_" + field, value=value, count=count)
        assets = {f["asset"]: f for f in entries}
        used = {f["asset"] for f in figures}
        for asset in sorted(used - assets.keys()):
            self.finding("error", "unmanifested_publication_figure", asset=asset)
        result: list[dict[str, Any]] = []
        for asset, record in assets.items():
            image = self.root / asset
            row: dict[str, Any] = {"id": record.get("id"), "asset": asset, "used_in_publication": asset in used}
            if not image.is_file():
                self.finding("error", "missing_manifest_asset", asset=asset)
            else:
                row["actual_sha256"] = digest(image)
                row["hash_matches"] = row["actual_sha256"] == record.get("sha256")
                if not row["hash_matches"]:
                    self.finding("error", "figure_hash_mismatch", asset=asset)
                try:
                    from PIL import Image
                    with Image.open(image) as loaded:
                        row["pixel_dimensions"] = list(loaded.size)
                    if record.get("pixel_dimensions") != row["pixel_dimensions"]:
                        self.finding("error", "figure_dimension_mismatch", asset=asset)
                except ImportError:
                    self.finding("warning", "figure_dimensions_not_checked", reason="Pillow unavailable")
                except Exception as error:
                    self.finding("error", "unreadable_figure_asset", asset=asset, detail=str(error))
            if asset not in used:
                self.finding("warning", "manifest_figure_not_in_publication", asset=asset)
            result.append(row)
        return result

    def build_log_checks(self, build_dir: Path) -> dict[str, Any]:
        path = build_dir / "monograph.log"
        if not path.is_file():
            self.finding("error", "missing_build_log", path=self.relative(path))
            return {}
        log = path.read_text(encoding="utf-8", errors="replace")
        patterns = {
            "undefined_citations": r"Citation [^\n]+undefined",
            "undefined_references": r"Reference [^\n]+undefined",
            "missing_glyphs": r"Missing character:[^\n]+",
            "latex_errors": r"(?:^! (?:LaTeX|Package|Emergency)|LaTeX Error:|Fatal error occurred)[^\n]*",
            "overfull_boxes": r"Overfull \\[hv]box[^\n]*",
            "underfull_boxes": r"Underfull \\[hv]box[^\n]*",
            "label_rerun_requests": r"Label\(s\) may have changed[^\n]*",
            "headheight_warnings": r"headheight is too small[^\n]*",
        }
        output: dict[str, Any] = {"path": self.relative(path), "sha256": digest(path)}
        for name, pattern in patterns.items():
            matches = list(re.finditer(pattern, log, flags=re.M))
            output[name] = [{"log_line": log.count("\n", 0, m.start()) + 1,
                             "message": m.group(0),
                             "context": log[max(0, m.start() - 180):m.end() + 220].strip()}
                            for m in matches]
            if matches:
                level = "error" if name in {"undefined_citations", "undefined_references", "missing_glyphs", "latex_errors"} else "warning"
                self.finding(level, "build_" + name, count=len(matches))
        return output

    def pdf_checks(self, pdf: Path, build_dir: Path, plan: dict[str, Any], require_current: bool) -> dict[str, Any]:
        if not pdf.is_file():
            self.finding("error", "missing_compiled_pdf", path=self.relative(pdf))
            return {}
        try:
            import fitz
            from pypdf import PdfReader
        except ImportError as error:
            self.finding("error", "pdf_validation_dependency_missing", detail=str(error))
            return {}
        result: dict[str, Any] = {"path": self.relative(pdf), "sha256": digest(pdf),
                                  "substantive_page_certification": "Not inferred from text density or compilation; requires editorial/visual review."}
        reader = PdfReader(str(pdf))
        labels = reader.page_labels
        result["physical_pages"] = len(reader.pages)
        def label_ranges(node: Any) -> list[dict[str, Any]]:
            if node is None:
                return []
            node = node.get_object() if hasattr(node, "get_object") else node
            output: list[dict[str, Any]] = []
            nums = node.get("/Nums", [])
            for n in range(0, len(nums) - 1, 2):
                rule = nums[n + 1].get_object()
                output.append({"zero_based_physical_start": int(nums[n]),
                               "rule": {str(k): str(v) for k, v in rule.items()}})
            for child in node.get("/Kids", []):
                output.extend(label_ranges(child))
            return output
        result["pdf_page_label_ranges"] = label_ranges(reader.trailer["/Root"].get("/PageLabels"))
        aux = build_dir / "monograph.aux"
        anchors: dict[str, str] = {}
        if aux.is_file():
            raw = aux.read_text(encoding="utf-8", errors="replace")
            anchors = dict(re.findall(r"\\newlabel\{([^}]+)\}\{\{[^}]*\}\{([^}]+)\}", raw))
        first, end = anchors.get("book:main:start"), anchors.get("book:main:end")
        result["aux_main_start_label"], result["aux_main_end_exclusive_label"] = first, end
        candidates = [i for i, label in enumerate(labels) if label == first] if first else []
        after = [i for i, label in enumerate(labels) if label == end and (not candidates or i > candidates[0])] if end else []
        body_start = candidates[0] if len(candidates) == 1 else None
        body_end = after[0] if len(after) == 1 else None
        if body_start is None or body_end is None or body_end <= body_start:
            self.finding("error", "main_text_boundary_not_uniquely_resolved", start_label=first, end_label=end,
                         start_candidates=[p + 1 for p in candidates], end_candidates=[p + 1 for p in after])
        else:
            expected = [str(int(first) + i) for i in range(body_end - body_start)] if str(first).isdigit() else []
            if labels[body_start:body_end] != expected:
                self.finding("error", "main_text_page_label_discontinuity")
            result["main_text_physical_range_inclusive"] = [body_start + 1, body_end]
            result["main_text_numbered_span"] = body_end - body_start
            result["excluded_frontmatter_physical_pages"] = body_start
            result["excluded_backmatter_physical_pages"] = len(labels) - body_end

        document = fitz.open(pdf)
        body_metrics: list[dict[str, Any]] = []
        outside: list[dict[str, Any]] = []
        margin_spills: list[dict[str, Any]] = []
        geometry = self.geometry_options()
        result["geometry_options_mm"] = geometry
        sizes: Counter[tuple[float, float]] = Counter()
        geometry_mismatches: list[dict[str, Any]] = []
        for i, page in enumerate(document):
            rect = page.rect
            sizes[(round(rect.width, 3), round(rect.height, 3))] += 1
            if "paperwidth" in geometry and "paperheight" in geometry:
                expected_width, expected_height = geometry["paperwidth"] * 72 / 25.4, geometry["paperheight"] * 72 / 25.4
                if abs(rect.width - expected_width) > 1 or abs(rect.height - expected_height) > 1:
                    geometry_mismatches.append({"physical_page": i + 1, "actual_size_pt": [rect.width, rect.height],
                                                "expected_size_pt": [expected_width, expected_height]})
            blocks = page.get_text("dict")["blocks"]
            spans = [span for block in blocks if block.get("type") == 0
                     for line in block.get("lines", []) for span in line.get("spans", [])]
            for span in spans:
                if not span.get("text", "").strip():
                    continue
                x0, y0, x1, y1 = span["bbox"]
                if x0 < -1.5 or y0 < -1.5 or x1 > rect.width + 1.5 or y1 > rect.height + 1.5:
                    outside.append({"physical_page": i + 1, "printed_page": labels[i],
                                    "bbox_pt": list(span["bbox"]), "text": span["text"][:160]})
            if body_start is not None and body_end is not None and body_start <= i < body_end:
                top, bottom = geometry.get("top", 21) * 72 / 25.4, rect.height - geometry.get("bottom", 22) * 72 / 25.4
                left, right = geometry.get("inner", geometry.get("left", 22)) * 72 / 25.4, rect.width - geometry.get("outer", geometry.get("right", 19)) * 72 / 25.4
                body = fitz.Rect(left - 3, top - 3, right + 3, bottom + 3)
                text = page.get_text(clip=body)
                words = len(re.findall(r"\b\w+\b", text))
                image_boxes = [block["bbox"] for block in blocks if block.get("type") == 1 and fitz.Rect(block["bbox"]).intersects(body)]
                body_spans = [s for s in spans if top - 3 <= (s["bbox"][1] + s["bbox"][3]) / 2 <= bottom + 3]
                # An empty text page may contain a meaningful image or vector
                # object. Only an empty page with no such object is auto-excluded.
                nontrivial_drawings = [d for d in page.get_drawings()
                                       if d["rect"].intersects(body) and d["rect"].width * d["rect"].height > 16]
                blank = not text.strip() and not image_boxes and not nontrivial_drawings
                row: dict[str, Any] = {"physical_page": i + 1, "printed_page": labels[i],
                                       "body_word_tokens": words, "body_characters": len(text.strip()),
                                       "image_count": len(image_boxes), "objectively_blank": blank}
                if words < 80:
                    row["low_text_review_required"] = not blank
                    row["body_text_preview"] = text[:600].replace("\n", " ")
                    row["classification"] = "blank" if blank else "unclassified: may be a figure, derivation, short chapter tail or title-only page"
                body_metrics.append(row)
                for span in body_spans:
                    x0, _, x1, _ = span["bbox"]
                    if x0 < left - 3 or x1 > right + 3:
                        margin_spills.append({"physical_page": i + 1, "printed_page": labels[i],
                                              "bbox_pt": list(span["bbox"]), "text": span["text"][:180]})
        document.close()
        result["text_spans_outside_page"] = outside
        result["page_size_distribution_pt"] = [{"size": list(size), "pages": count} for size, count in sizes.items()]
        result["page_geometry_mismatches"] = geometry_mismatches
        result["body_margin_spill_candidates"] = margin_spills
        result["main_text_page_metrics"] = body_metrics
        blanks = [row["physical_page"] for row in body_metrics if row["objectively_blank"]]
        low = [row for row in body_metrics if row.get("low_text_review_required")]
        result["objectively_blank_main_text_physical_pages"] = blanks
        result["low_text_main_pages_requiring_individual_review"] = low
        result["nonblank_main_text_pages"] = len(body_metrics) - len(blanks)
        minimum = plan.get("minimum_substantive_pages")
        result["required_substantive_page_minimum"] = minimum
        result["nonblank_span_meets_minimum"] = bool(isinstance(minimum, (int, float)) and len(body_metrics) - len(blanks) >= minimum)
        if isinstance(minimum, (int, float)) and body_metrics and not result["nonblank_span_meets_minimum"]:
            self.finding("error", "nonblank_main_span_below_minimum", actual=len(body_metrics) - len(blanks), minimum=minimum)
        if outside:
            self.finding("error", "pdf_text_outside_media_box", count=len(outside))
        if geometry_mismatches:
            self.finding("error", "pdf_geometry_differs_from_driver", count=len(geometry_mismatches))
        if margin_spills:
            self.finding("warning", "pdf_body_margin_spill_candidates", count=len(margin_spills),
                         meaning="Bounding-box candidates require rendered-page review; optical protrusion is not measured ink.")
        if low:
            self.finding("warning", "low_text_pages_require_individual_review", physical_pages=[r["physical_page"] for r in low],
                         meaning="Not automatically excluded or called padding.")
        newer = [self.relative(path) for path in self.sources if path.stat().st_mtime > pdf.stat().st_mtime + 1]
        asset_names = [self.relative(image) for path in self.source_order
                       for raw in GRAPHIC.findall(mask_verbatim(strip_comments(self.sources[path])))
                       if (image := self.resolve(raw, path, (".png", ".jpg", ".jpeg", ".pdf"))) is not None]
        for name in ("book/references.bib", *asset_names):
            path = self.root / name
            if path.is_file() and path.stat().st_mtime > pdf.stat().st_mtime + 1:
                newer.append(name)
        result["source_files_newer_than_pdf"] = newer
        result["currency_check_limit"] = "Modification times detect common stale builds but do not prove exact source-to-PDF correspondence. Hashes bind this validation snapshot."
        if newer:
            self.finding("error" if require_current else "warning", "source_newer_than_compiled_pdf", paths=newer)
        build_pdf = build_dir / "monograph.pdf"
        if build_pdf.is_file():
            result["matches_build_pdf"] = digest(build_pdf) == result["sha256"]
            if not result["matches_build_pdf"]:
                self.finding("warning", "pdf_differs_from_current_build_artifact")
        return result

    def geometry_options(self) -> dict[str, float]:
        source = self.sources.get((self.root / "monograph.tex").resolve(), "")
        match = re.search(r"\\usepackage\[([^\]]+)\]\{geometry\}", source)
        if not match:
            return {}
        return {name: float(value) for name, value in re.findall(r"(paperwidth|paperheight|inner|outer|left|right|top|bottom)=([\d.]+)mm", match.group(1))}


def self_test() -> None:
    assert strip_comments("a\\%b%c\nx%y") == "a\\%b\nx"
    assert "wrong" not in mask_verbatim("\\begin{verbatim}\n\\input{wrong}\n\\end{verbatim}")
    records = bib_entries('@misc{x,title={{Nested {Title}}},author={A and B},year={2026},url={https://x.test}}\n@book{y,title="Other",author={C},year=2025}')
    assert len(records) == 2 and records[0]["fields"]["title"] == "{Nested {Title}}"
    assert records[1]["fields"]["year"] == "2025"
    assert lexical_words("\\section{A title}\\label{x} Meaningful scientific prose.") >= 3
    for environment in PROGRAMMING_ENVIRONMENTS:
        assert programming_environment_starts("\n\\begin{" + environment + "}\nx\n\\end{" + environment + "}") == [
            {"environment": environment, "line": 2}
        ]
    assert programming_environment_starts("\\begin % explanation\n {algorithmic}\n") == [
        {"environment": "algorithmic", "line": 1}
    ]
    assert programming_environment_starts("\\% still active: \\begin{minted}") == [
        {"environment": "minted", "line": 1}
    ]
    assert programming_environment_starts(r"\verb%literal% \begin{algorithmic}") == [
        {"environment": "algorithmic", "line": 1}
    ]
    for example in (
        "The words verbatim, minted, algorithmic and algorithm2e are ordinary prose.",
        r"\path{src/algorithmic/verbatim.py} and \texttt{minted}.",
        "% \\begin{verbatim}\nText\n% \\end{verbatim}",
        r"\verb|\begin{verbatim}| and \verb*+\begin{minted}+",
        r"\verb%\begin{verbatim}%",
        r"\lstinline[language=TeX]|\begin{algorithmic}|",
        r"\mintinline{latex}{\begin{verbatim}}",
        r"\detokenize{\begin{lstlisting}}",
        r"\string\begin{verbatim}",
        r"\\begin{verbatim}",
        r"\begin{equation} x_{n+1}=f(x_n) \end{equation}",
    ):
        assert not programming_environment_starts(example), example
    print("Validator parser self-checks passed.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--pdf", type=Path, default=Path("output/pdf/agentic_ai_systems_draft.pdf"))
    parser.add_argument("--build-dir", type=Path, default=Path("build/book"))
    parser.add_argument("--report", type=Path, default=Path("internal/book_validation.json"))
    parser.add_argument("--require-current-build", action="store_true", help="Treat a source newer than the PDF as an error.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    root = args.root.resolve()
    audit = Audit(root)
    plan_path = root / "book/plan.json"
    if not plan_path.is_file():
        print("Missing substantive-book plan: " + str(plan_path), file=sys.stderr)
        return 2
    plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    source = audit.source_checks(plan)
    build_dir = args.build_dir if args.build_dir.is_absolute() else root / args.build_dir
    pdf = args.pdf if args.pdf.is_absolute() else root / args.pdf
    report: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "validator": "tools/validate_book.py", "validator_sha256": digest(Path(__file__)),
        "scope": "Mechanical source, build and PDF geometry checks; no scientific, citation-claim, figure-semantic or human-review certification.",
        "literature_cutoff": plan.get("literature_cutoff"), "source": source,
        "build_log": audit.build_log_checks(build_dir),
        "pdf": audit.pdf_checks(pdf, build_dir, plan, args.require_current_build),
    }
    report["errors"], report["warnings"] = audit.errors, audit.warnings
    report["mechanical_checks_passed"] = not audit.errors
    report["release_ready"] = False
    report["release_ready_explanation"] = "This tool cannot certify scientific validity, exhaustive coverage, visual fidelity or substantive editorial quality."
    destination = args.report if args.report.is_absolute() else root / args.report
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"mechanical_checks_passed": not audit.errors, "errors": len(audit.errors), "warnings": len(audit.warnings),
                      "chapters": source["chapter_count"], "bibliographic_records": source["bibliography"].get("records"),
                      "physical_pdf_pages": report["pdf"].get("physical_pages"),
                      "numbered_main_text_span": report["pdf"].get("main_text_numbered_span"),
                      "nonblank_main_text_pages": report["pdf"].get("nonblank_main_text_pages"),
                      "report": audit.relative(destination)}, indent=2))
    return 1 if audit.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
