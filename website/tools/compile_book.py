"""Compile the accepted modular LaTeX edition to audited semantic web content.

This is a deliberately bounded adapter for this book, not a general TeX engine.
Unknown AST/raw constructs are fatal. The accepted manuscript is read-only.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BASE = "__BOOK_BASE__"
API: list[int] = []
FILES: dict[str, str] = {}
IGNORED: collections.Counter[str] = collections.Counter()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read(path: Path) -> str:
    FILES[path.relative_to(ROOT).as_posix()] = digest(path.read_bytes())
    return path.read_text(encoding="utf-8")


def group(s: str, pos: int) -> tuple[str, int]:
    while pos < len(s) and s[pos].isspace():
        pos += 1
    if pos >= len(s) or s[pos] != "{":
        raise ValueError(f"Expected braced group at {s[pos:pos+60]!r}")
    start = pos + 1
    depth = 1
    pos += 1
    while pos < len(s):
        if s[pos] == "\\":
            pos += 2
            continue
        depth += (s[pos] == "{") - (s[pos] == "}")
        if depth == 0:
            return s[start:pos], pos + 1
        pos += 1
    raise ValueError("Unclosed braced group")


def uncomment(s: str) -> str:
    # Verbatim-like path/url arguments have their own percent catcodes.
    out: list[str] = []
    i = 0
    while i < len(s):
        m = re.match(r"\\(?:path|url)\s*\{", s[i:])
        if m:
            _, end = group(s, i + m.end() - 1)
            out.append(s[i:end]); i = end
        elif s[i] == "\\" and i + 1 < len(s):
            out.append(s[i:i+2]); i += 2
        elif s[i] == "%":
            end = s.find("\n", i)
            i = len(s) if end < 0 else end
        else:
            out.append(s[i]); i += 1
    return "".join(out)


def expand(path: Path, stack: tuple[Path, ...] = ()) -> tuple[str, list[str]]:
    path = path.resolve()
    if path in stack or not path.is_relative_to(ROOT):
        raise ValueError(f"Invalid include closure: {path}")
    s = uncomment(read(path))
    closure = [path.relative_to(ROOT).as_posix()]
    def replace(m: re.Match[str]) -> str:
        target = ROOT / m[1]
        if not target.suffix:
            target = target.with_suffix(".tex")
        if not target.exists():
            target = path.parent / m[1]
            if not target.suffix:
                target = target.with_suffix(".tex")
        text, nested = expand(target, stack + (path,))
        closure.extend(nested)
        return "\n" + text + "\n"
    return re.sub(r"\\(?:input|include)\s*\{([^}]+)\}", replace, s), closure


def pandoc(source: str) -> dict[str, Any]:
    global API
    p = subprocess.run(["pandoc", "-f", "latex+raw_tex", "-t", "json"],
                       input=source, encoding="utf-8", capture_output=True)
    if p.returncode or p.stderr.strip():
        raise ValueError(f"Pandoc input diagnostic: {p.stderr}")
    result = json.loads(p.stdout)
    API = result["pandoc-api-version"]
    return result


def write_html(blocks: list[dict[str, Any]]) -> str:
    p = subprocess.run(["pandoc", "-f", "json", "-t", "html5", "--wrap=none"],
        input=json.dumps({"pandoc-api-version": API, "meta": {}, "blocks": blocks}),
        encoding="utf-8", capture_output=True)
    if p.returncode or p.stderr.strip():
        raise ValueError(f"Pandoc HTML diagnostic: {p.stderr}")
    return p.stdout.strip()


def plain(node: Any) -> str:
    if isinstance(node, list):
        return "".join(plain(x) for x in node)
    if not isinstance(node, dict):
        return ""
    t, c = node.get("t"), node.get("c")
    if t == "Str": return c
    if t in {"Space", "SoftBreak", "LineBreak"}: return " "
    if t == "Code": return c[1]
    if t == "Math": return c[1]
    if t == "Cite": return ""
    if t in {"RawInline", "RawBlock"}: return re.sub(r"<[^>]+>", " ", html.unescape(c[1]))
    if t == "Image": return plain(c[1])
    if t == "Header": return plain(c[2])
    if t in {"Link", "Quoted", "Span"}: return plain(c[1])
    if t in {"Para", "Plain", "Emph", "Strong", "Superscript", "Subscript", "SmallCaps"}: return plain(c)
    return plain(c)


def raw(text: str, block: bool = False) -> dict[str, Any]:
    return {"t": "RawBlock" if block else "RawInline", "c": ["html", text]}


def attrs(**values: Any) -> str:
    return " ".join(f'{key.replace("_", "-")}="{html.escape(str(value), quote=True)}"' for key, value in values.items())


def math_html(tex: str, display: bool = False) -> str:
    tag = "div" if display else "span"
    return f'<{tag} {attrs(**{"class": "math math-display" if display else "math math-inline", "data-tex": tex, "data-display": str(display).lower()})}>{html.escape(tex)}</{tag}>'


def parse_aux(source: str) -> tuple[dict[str, dict[str, str]], dict[str, int]]:
    labels: dict[str, dict[str, str]] = {}
    for m in re.finditer(r"\\newlabel\s*\{", source):
        key, pos = group(source, m.end()-1)
        value, _ = group(source, pos)
        number, pos = group(value, 0)
        page, pos = group(value, pos)
        title, pos = group(value, pos)
        target, _ = group(value, pos)
        labels[key] = {"number": number, "page": page, "titleTex": title, "target": target}
    return labels, {key: int(n) for key, n in re.findall(r"\\bibcite\{([^}]+)\}\{(\d+)\}", source)}


def row_split(s: str) -> list[str]:
    # Outer align rows; nested aligned/cases do not delimit their parent.
    rows: list[str] = []
    start = i = depth = 0
    env: list[str] = []
    token = re.compile(r"\\(?:begin|end)\{([^}]+)\}|\\\\|[{}]")
    for m in token.finditer(s):
        text = m[0]
        if text.startswith("\\begin"):
            env.append(m[1])
        elif text.startswith("\\end"):
            if not env or env.pop() != m[1]: raise ValueError("Unbalanced math environment")
        elif text == "\\\\" and not env and depth == 0:
            rows.append(s[start:m.start()]); start = m.end()
        elif text == "{" and (m.start() == 0 or s[m.start()-1] != "\\"):
            depth += 1
        elif text == "}" and (m.start() == 0 or s[m.start()-1] != "\\"):
            depth -= 1
    if s[start:].strip(): rows.append(s[start:])
    return rows


def prepare_math(s: str, chapter: int, aux: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    equations: list[dict[str, Any]] = []
    counter = 0
    pattern = re.compile(r"\\begin\{(equation|align)\}([\s\S]*?)\\end\{\1\}")
    def replace(m: re.Match[str]) -> str:
        nonlocal counter
        kind, body = m[1], m[2]
        rows = row_split(body) if kind == "align" else [body]
        rendered: list[str] = []
        numbers: list[str] = []
        found: list[str] = []
        for row in rows:
            if re.search(r"\\(?:notag|nonumber|tag)\b", row):
                raise ValueError("Unexpected source math-numbering override")
            counter += 1
            number = f"{chapter}.{counter}"
            numbers.append(number)
            for label in re.findall(r"\\label\{([^}]+)\}", row):
                if aux[label]["number"] != number:
                    raise ValueError(f"Equation counter differs from accepted AUX: {label} {number} {aux[label]}")
                found.append(label)
            clean = re.sub(r"\\label\{[^}]+\}", "", row).strip()
            rendered.append(clean + f" \\tag{{{number}}}")
        tex = rendered[0] if kind == "equation" else "\\begin{align*}\n" + "\\\\\n".join(rendered) + "\n\\end{align*}"
        ident = found[0] if found else f"equation-{chapter}-{numbers[0].split('.')[-1]}"
        equations.append({"id": ident, "number": numbers[0], "numbers": numbers, "labels": found,
                          "kind": kind, "sourceTex": m[0], "tex": tex})
        return f"\n\n\\texttt{{ATLASDISPLAYX{len(equations)-1:04d}}}\n\n"
    return pattern.sub(replace, s), equations


def normalize_tables(s: str) -> str:
    # The custom L column is a left-aligned wrapping print column. HTML owns widths.
    edits=[]
    for m in re.finditer(r"\\begin\{(?:tabular|longtable)\}",s):
        specification,end=group(s,m.end())
        normalized=re.sub(r"L\{[^{}]*\}","l",specification)
        edits.append((m.end(),end,"{"+normalized+"}"))
    for start,end,replacement in reversed(edits):s=s[:start]+replacement+s[end:]
    def continuation(m: re.Match[str]) -> str:
        start, again = m[1], m[2]
        if re.sub(r"\s+", "", start) != re.sub(r"\s+", "", again):
            raise ValueError("Longtable continuation header differs from first header")
        return start
    return re.sub(r"(\\toprule(?:(?!\\toprule)[\s\S])*?\\midrule)\\endfirsthead([\s\S]*?)\\endhead", continuation, s)


def visible_prose(node: Any) -> str:
    """Private emission diagnostic, without math/citation/reference identifier words."""
    if isinstance(node,list):return "".join(visible_prose(x) for x in node)
    if not isinstance(node,dict):return ""
    if node.get("t") in {"Math","Cite"}:return " "
    if node.get("t") in {"RawInline","RawBlock"}:
        text=node["c"][1]
        if text.startswith("\\path"):
            return group(text,text.index("{"))[0]
        return " "
    if node.get("t")=="Code":
        return " " if node["c"][1].startswith("ATLASDISPLAYX") else node["c"][1]
    if node.get("t")=="Str":return node["c"]
    if node.get("t") in {"Space","SoftBreak","LineBreak"}:return " "
    if node.get("t") in {"Image","Link","Quoted","Span"}:return visible_prose(node["c"][1])
    return visible_prose(node.get("c",[]))


class Renderer:
    def __init__(self, labels: dict[str, Any], bibnums: dict[str, int], equations: list[dict[str, Any]], slug: str):
        self.labels, self.bibnums, self.equations, self.slug = labels, bibnums, equations, slug
        self.cite_keys: list[str] = []; self.ref_keys: list[str] = []; self.paths: list[str] = []
        self.figures: list[dict[str, Any]] = []; self.tables: list[dict[str, Any]] = []
        self.math_count = 0

    def inlines_html(self, items: list[Any]) -> str:
        value = write_html([{"t": "Plain", "c": self.transform(items)}])
        return value

    def transform(self, node: Any) -> Any:
        if isinstance(node, list):
            return [self.transform(x) for x in node]
        if not isinstance(node, dict): return node
        t, c = node.get("t"), node.get("c")
        if t == "Cite":
            links: list[str] = []
            for entry in c[0]:
                key = entry["citationId"]
                if entry["citationPrefix"] or entry["citationSuffix"]: raise ValueError("Unhandled citation affix")
                if key not in self.bibnums: raise ValueError(f"Missing citation {key}")
                self.cite_keys.append(key)
                links.append(f'<a {attrs(href=BASE+"references/#ref-"+key, data_cite_key=key)}>{self.bibnums[key]}</a>')
            return raw('<span class="citation" data-citation="true">[' + ", ".join(links) + "]</span>")
        if t in {"RawInline", "RawBlock"}:
            if c[0] != "latex": raise ValueError(f"Unexpected raw format {c[0]}")
            text = c[1].strip()
            m = re.fullmatch(r"\\(ref|eqref)\{([^}]+)\}", text)
            if m:
                key = m[2]; self.ref_keys.append(key)
                target = self.labels[key]
                value = html.escape(target["number"])
                if m[1] == "eqref": value = "("+value+")"
                return raw(f'<a {attrs(**{"class":"cross-reference","href":target["href"],"data-ref-label":key})}>{value}</a>')
            if text.startswith("\\path"):
                value, end = group(text, text.index("{"))
                if text[end:].strip(): raise ValueError("Unexpected path suffix")
                self.paths.append(value)
                return raw(f'<code {attrs(data_source_path="true")}>{html.escape(value)}</code>')
            if re.fullmatch(r"\\(?:centering|small|begingroup|endgroup|allowbreak)", text):
                IGNORED[text] += 1; return raw("",t=="RawBlock")
            if re.fullmatch(r"\\setlength\{\\tabcolsep\}\{[^{}]+\}|\\bookneedspace\{[^{}]+\}", text):
                IGNORED[text.split("{")[0]] += 1; return raw("",t=="RawBlock")
            raise ValueError(f"Unhandled raw TeX: {text[:250]!r}")
        if t == "Math":
            self.math_count += 1
            if c[0]["t"] != "InlineMath": raise ValueError("Display math escaped source capture")
            return raw(math_html(c[1]))
        if t == "Code" and re.fullmatch(r"ATLASDISPLAYX\d{4}", c[1]):
            e = self.equations[int(c[1][-4:])]
            anchors = "".join(f'<span {attrs(id=x)}></span>' for x in e["labels"] if x != e["id"])
            return raw(f'<div {attrs(**{"class":"equation","id":e["id"],"data-equation-number":e["number"]})}>{anchors}{math_html(e["tex"],True)}</div>')
        if t == "Para" and len(c) == 1 and c[0].get("t") == "Code" and c[0]["c"][1].startswith("ATLASDISPLAYX"):
            v = self.transform(c[0]); v["t"] = "RawBlock"; return v
        if t == "Para" and len(c) == 1 and c[0].get("t") == "Image":
            attr, caption, target = c[0]["c"]
            ident = attr[0]
            if ident not in self.labels: raise ValueError(f"Missing figure label {ident}")
            number = self.labels[ident]["number"]
            caption_text = plain(caption)
            caption_html = self.inlines_html(caption)
            path = (ROOT / target[0]).resolve()
            if not path.is_relative_to(ROOT / "book/figures/assets") or not path.exists(): raise ValueError("Invalid figure source")
            read_bytes = path.read_bytes()
            src = BASE + "figures/" + path.name
            self.figures.append({"id":ident,"number":number,"src":src,"captionHtml":caption_html,"captionText":caption_text,"alt":caption_text,"sha256":digest(read_bytes)})
            return raw(f'<figure {attrs(id=ident)}><a {attrs(href=src,**{"class":"figure-zoom"})}><img {attrs(src=src,alt=caption_text,loading="lazy",decoding="async")} /></a><figcaption><span class="figure-number">Figure {number}:</span> {caption_html}</figcaption></figure>',True)
        if t == "Div" and len(c[1]) == 1 and c[1][0].get("t") == "Table":
            ident = c[0][0]
            if ident not in self.labels: raise ValueError(f"Missing table label {ident}")
            table = c[1][0]
            number = self.labels[ident]["number"]
            caption = table["c"][1][1]
            caption_text = " ".join(plain(x) for x in caption)
            transformed = self.transform(table)
            capblocks = transformed["c"][1][1]
            if not capblocks: raise ValueError("Missing table caption")
            capblocks[0]["c"].insert(0,{"t":"Str","c":f"Table {number}: "})
            cols = len(table["c"][2])
            rows = len(table["c"][3][1]) + sum(len(body[2])+len(body[3]) for body in table["c"][4]) + len(table["c"][5][1])
            self.tables.append({"id":ident,"number":number,"captionText":caption_text,"columnCount":cols,"rowCount":rows})
            markup = write_html([transformed])
            return raw(f'<div {attrs(**{"class":"table-scroll","id":ident,"role":"region","aria-label":"Table "+number,"tabindex":"0"})}>{markup}</div>',True)
        result = dict(node)
        if "c" in result: result["c"] = self.transform(c)
        return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aux", default="build/book/monograph.aux")
    parser.add_argument("--bbl", default="build/book/monograph.bbl")
    args = parser.parse_args()
    version = subprocess.check_output(["pandoc","--version"],encoding="utf-8").splitlines()[0]
    if version.split()[-1] != "2.19.2":
        raise ValueError("This adapter is validated against Pandoc 2.19.2; revalidate its AST contract before upgrading.")
    plan = json.loads(read(ROOT / "book/plan.json"))
    aux_text = (ROOT/args.aux).read_text(encoding="utf-8")
    bbl_text = (ROOT/args.bbl).read_text(encoding="utf-8")
    aux, bibnums = parse_aux(aux_text)
    mathmacros = read(ROOT / "config/notation.tex") + "\n" + "\n".join(
        x for x in read(ROOT / "config/book_layout.tex").splitlines()
        if x.startswith("\\newcommand") and x.count("{")==x.count("}") and "\\@" not in x)
    sources: list[tuple[dict[str,Any],str,list[str]]] = []
    labels: dict[str,Any] = {}
    chapter_metrics: dict[str, Any] = {}
    for chapter in plan["chapters"]:
        source, closure = expand(ROOT / chapter["path"])
        slug = f'{chapter["number"]:02d}-{chapter["slug"]}'
        for label in re.findall(r"\\label\{([^}]+)\}",source):
            if label not in aux or label in labels: raise ValueError(f"Unresolved or duplicate label {label}")
            record = aux[label]
            labels[label] = {"id":label,"number":record["number"],"chapterId":chapter["id"],"type":record["target"].split(".")[0],"href":BASE+f"chapters/{slug}/#{label}"}
        sources.append((chapter,source,closure))
    for key, target in [("book:main:start", plan["chapters"][0]),("book:main:end",plan["chapters"][-1])]:
        labels[key]={"id":key,"number":aux[key]["number"],"chapterId":target["id"],"type":"boundary","href":BASE+f'chapters/{target["number"]:02d}-{target["slug"]}/#{key}'}
    chapters=[]; totals=collections.Counter(); asset_manifest=[]
    for chapter, source, closure in sources:
        number=chapter["number"]; slug=f'{number:02d}-{chapter["slug"]}'
        metrics={"sections":len(re.findall(r"\\section\{",source)),"subsections":len(re.findall(r"\\subsection\{",source)),"paragraphs":len(re.findall(r"\\paragraph\{",source)),"figures":len(re.findall(r"\\includegraphics\b",source)),"tables":len(re.findall(r"\\begin\{(?:table|longtable)\}",source)),"displayEnvironments":len(re.findall(r"\\begin\{(?:equation|align)\}",source)),"labels":len(re.findall(r"\\label\{",source)),"references":len(re.findall(r"\\(?:ref|eqref)\{",source)),"paths":len(re.findall(r"\\path\{",source)),"citationCalls":len(re.findall(r"\\cite\{",source))}
        prepared,equations=prepare_math(source,number,aux)
        ast=pandoc(mathmacros+"\n"+normalize_tables(prepared))
        renderer=Renderer(labels,bibnums,equations,slug)
        sections=[]; section_no=sub_no=paragraph_no=0
        for block in ast["blocks"]:
            if block["t"] != "Header":continue
            level,attr,inlines=block["c"]
            if level==1:continue
            if level==2:section_no+=1;sub_no=0; num=f"{number}.{section_no}"
            elif level==3:sub_no+=1;num=f"{number}.{section_no}.{sub_no}"
            else:paragraph_no+=1;num=""
            ident=attr[0]
            if ident in aux and aux[ident]["number"]!=num:raise ValueError(f"Heading counter differs: {ident}")
            sections.append({"id":ident,"title":plain(inlines),"anchor":ident,"level":level-1,"number":num})
            if num:block["c"][2].insert(0,{"t":"Str","c":num+" "})
        # The page owns its chapter H1; chapter driver text is still represented in title.
        blocks=[x for x in ast["blocks"] if not(x["t"]=="Header" and x["c"][0]==1)]
        emitted=[]; active_section="ch:"+chapter["id"]
        for index,block in enumerate(blocks):
            if block["t"]=="Header":active_section=block["c"][1][0]
            if block["t"]=="Para":
                text=re.sub(r"\s+"," ",visible_prose(block)).strip()
                if text:emitted.append({"blockIndex":index,"sectionId":active_section,"text":text,"sha256":digest(text.encode())})
        transformed=renderer.transform(blocks)
        content_html=f'<span id="ch:{chapter["id"]}"></span>'+write_html(transformed)
        lead=[]
        for block in transformed:
            if block["t"]=="Header":break
            lead.append(block)
        if number==1:content_html='<span id="book:main:start"></span>'+content_html
        if number==34:content_html+='<span id="book:main:end"></span>'
        if len(renderer.figures)!=metrics["figures"] or len(renderer.tables)!=metrics["tables"] or len(renderer.ref_keys)!=metrics["references"] or len(renderer.paths)!=metrics["paths"]:
            raise ValueError(f"Artifact count mismatch {chapter['id']}: {metrics}")
        cite_calls=len(re.findall('data-citation="true"',content_html))
        if cite_calls!=metrics["citationCalls"]:raise ValueError(f"Citation occurrence mismatch {chapter['id']}: {cite_calls}")
        metrics["inlineMath"]=renderer.math_count
        metrics["equationNumbers"]=sum(len(e["numbers"]) for e in equations)
        for key,value in metrics.items():totals[key]+=value
        chapter_metrics[chapter["id"]]={"counts":metrics,"includeOrder":closure,"sourceSha256":digest(source.encode()),"emissionParagraphs":emitted}
        chapters.append({"id":chapter["id"],"number":number,"slug":slug,"title":chapter["title"],"leadHtml":write_html(lead) if lead else "","html":content_html,"sections":sections,"references":[{"key":key,"number":bibnums[key]} for key in sorted(set(renderer.cite_keys),key=lambda x:bibnums[x])],"figures":renderer.figures,"tables":renderer.tables,"equations":equations,"searchText":re.sub(r"\s+"," ",html.unescape(re.sub('<[^>]+>',' ',content_html))).strip(),"sourceSha256":digest(source.encode()),"counts":metrics})
        for fig in renderer.figures:
            filename=fig["src"].split("/")[-1]
            asset_manifest.append({"id":fig["id"],"source":"book/figures/assets/"+filename,"target":"website/public/figures/"+filename,"sha256":fig["sha256"]})
    references=[];entries=[]
    bibmatches=list(re.finditer(r"\\bibitem\{([^}]+)\}",bbl_text))
    for i,m in enumerate(bibmatches):
        key=m[1]; end=bibmatches[i+1].start() if i+1<len(bibmatches) else bbl_text.index("\\end{thebibliography}",m.end())
        entry=bbl_text[m.end():end]
        entry=re.sub(r"\\BIBentry(?:ALT|STD)interwordspacing", "", entry)
        entry=re.sub(r"\\hskip[^\\]*\\relax", " ", entry)
        urls=re.findall(r"\\url\{([^}]+)\}",entry)
        if any(not u.startswith(("https://","http://")) for u in urls):raise ValueError("Unsupported bibliography URL scheme")
        entries.append({"key":key,"source":entry,"urls":urls})
    bibast=pandoc("\n\n".join(f'\\section*{{ATLASBIBX{i:04d}}}\n'+entry["source"] for i,entry in enumerate(entries)))
    bibblocks=[];marker_count=0
    renderer=Renderer(labels,bibnums,[],"references")
    for block in bibast["blocks"]:
        if block["t"]=="Header":
            title=plain(block["c"][2])
            if not re.fullmatch(r"ATLASBIBX\d{4}",title):raise ValueError("Unexpected bibliography heading")
            bibblocks.append(raw("<!--"+title+"-->",True));marker_count+=1
        else:bibblocks.append(renderer.transform(block))
    if marker_count!=len(entries):raise ValueError("Bibliography boundaries were lost")
    compiled_bib=write_html(bibblocks)
    parts=re.split(r"<!--ATLASBIBX(\d{4})-->",compiled_bib)
    if parts[0].strip():raise ValueError("Unassigned bibliography content")
    for offset in range(1,len(parts),2):
        index=int(parts[offset]);entry=entries[index];key=entry["key"];rendered=parts[offset+1].strip()
        references.append({"id":"ref-"+key,"key":key,"number":bibnums[key],"html":rendered,"text":re.sub(r"\s+"," ",html.unescape(re.sub('<[^>]+>',' ',rendered))).strip(),"urls":entry["urls"],"chapterIds":[c["id"] for c in chapters if any(r["key"]==key for r in c["references"])]})
    if len(references)!=356 or set(bibnums)!={r["key"] for r in references}:raise ValueError("Bibliography identity mismatch")
    # Reading front matter, including its evidence and AI-assistance disclosures.
    front=read(ROOT/"book/frontmatter.tex")
    front=front[front.index("\\chapter*{Abstract}"):]
    front_ast=pandoc(mathmacros+"\n"+front)
    front_renderer=Renderer(labels,bibnums,[],"front-matter")
    front_html=write_html(front_renderer.transform(front_ast["blocks"]))
    validation=json.loads(read(ROOT/"book/validation_summary.json"))
    read(ROOT/"monograph.tex")
    read(ROOT/"book/references.bib")
    for bib in sorted((ROOT/"bibliography").glob("*.bib")): read(bib)
    read(Path(__file__).resolve())
    file_records=[{"path":p,"sha256":h} for p,h in sorted(FILES.items())]
    source_digest=digest(json.dumps(file_records,separators=(",",":"),sort_keys=True).encode())
    metrics={"chapters":34,**dict(totals),"uniqueCitedKeys":356,"labelRecords":len(labels)}
    expected={"sections":266,"subsections":39,"figures":35,"tables":37,"displayEnvironments":217,"labels":466,"references":129,"paths":168,"citationCalls":525}
    for key,value in expected.items():
        if metrics[key]!=value:raise ValueError(f"Accepted corpus changed: {key} {metrics[key]} != {value}")
    converter_sha=digest(Path(__file__).read_bytes())
    data={"metadata":{"schemaVersion":"1.0.0","title":plan["title"],"subtitle":plan["subtitle"],"literatureCutoff":plan["literature_cutoff"],"latestSourceRetrieval":plan["literature_cutoff"],"editionType":"Technical Monograph","sourceDigest":source_digest,"acceptedPdfSha256":validation["pdf_sha256"],"converter":"bounded LaTeX/Pandoc content adapter","converterSha256":converter_sha,"pandocVersion":version,"metrics":metrics,"frontMatterHtml":front_html},"chapters":chapters,"references":references,"labels":labels}
    manifest={"schemaVersion":"1.0.0","sourceDigest":source_digest,"files":file_records,"chapters":chapter_metrics,"assets":asset_manifest,"acceptedAux":{"path":args.aux,"sha256":digest((ROOT/args.aux).read_bytes()),"labels":aux,"citationNumbers":bibnums},"acceptedBbl":{"path":args.bbl,"sha256":digest((ROOT/args.bbl).read_bytes()),"entryKeys":[r["key"] for r in references]},"metrics":metrics,"diagnostics":{"converterSha256":converter_sha,"unknownRawTex":[],"ignoredPrintCommands":dict(IGNORED),"tableNormalization":"L wrapping columns become HTML left columns; seven exact repeated continuation headers removed","mathNormalization":"Original 217 display environments preserved in sourceTex; explicit accepted equation/align-row tags; labels become stable DOM anchors","sourceEdits":False}}
    dest=ROOT/"website/src/generated/book.json";dest.parent.mkdir(parents=True,exist_ok=True)
    serialized=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
    manifest["generatedBookSha256"]=digest(serialized.encode())
    dest.write_text(serialized,encoding="utf-8",newline="\n")
    (ROOT/"website/tools/source-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(dest.relative_to(ROOT)),"metrics":metrics,"sourceDigest":source_digest,"bytes":dest.stat().st_size}))


if __name__=="__main__":
    main()
