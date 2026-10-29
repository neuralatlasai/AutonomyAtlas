#!/usr/bin/env python3
"""Package only a selected chapter and the files needed for its standalone build."""
from pathlib import Path
import argparse,hashlib,json,re,zipfile
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--chapter',default='C01');args=parser.parse_args()
    plan=json.loads((ROOT/'book/plan.json').read_text(encoding='utf-8'))
    c=next(x for x in plan['chapters'] if x['id']==args.chapter);ident=args.chapter.lower();date=c.get('literature_cutoff',plan['literature_cutoff'])
    files={ROOT/'tools/build_chapter.py',ROOT/'tools/package_chapter.py',ROOT/'book/plan.json',ROOT/f'book/{ident}_references.bib',ROOT/c['path']}
    files.update((ROOT/'config').glob('*.tex'))
    driver=(ROOT/c['path']).read_text(encoding='utf-8')
    sources=[]
    for rel in re.findall(r'\\input\{([^}]+)\}',driver):
        p=ROOT/rel;p=p if p.suffix else p.with_suffix('.tex');files.add(p);sources.append(p.read_text(encoding='utf-8'))
    for text in sources:
        for rel in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',text):
            p=ROOT/rel;files.add(p);files.add(ROOT/'book/figures/prompts'/(p.stem+'.txt'))
    for rel in ('book/chapter_review_sources.csv','book/figures/visual_grammar.md','book/figures/chapter_figure_plan.csv',f'book/{ident}_validation_summary.json',f'book/figures/{ident}_manifest.json'):
        p=ROOT/rel
        if p.exists():files.add(p)
    figure_manifest=ROOT/f'book/figures/{ident}_manifest.json'
    if figure_manifest.exists():
        for figure in json.loads(figure_manifest.read_text(encoding='utf-8'))['figures']:
            for rel in figure.get('referenced_assets',[])+figure.get('referenced_prompts',[]):
                files.add(ROOT/rel)
    rows=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
    name=f'chapter_{c["number"]:02d}_source_{date.replace("-","")}.zip';dest=ROOT/'output/source'/name;dest.parent.mkdir(parents=True,exist_ok=True)
    readme=f'''# Chapter {c["number"]}: {c["title"]}

Literature and implementation review: {date}. This archive contains only the selected chapter, its cited bibliography, two original image-generated illustrations and prompts, shared LaTeX configuration, and the standalone build tools. The book plan supplies contextual chapter numbers; other chapter bodies are excluded.

Build from the extracted directory:

```powershell
python tools/build_chapter.py --chapter {args.chapter}
```

Requirements: Python 3.10+, pdfLaTeX, BibTeX, IEEEtran bibliography style, Latin Modern and declared TeX packages; PyMuPDF for PDF inspection. The build uses no network service or API key. It runs until references stabilize and writes the selected chapter under output/pdf.

External chapter references are printed as contextual chapter numbers, without misleading local PDF links. Internal references and the chapter's own bibliography remain active. Source/code inspection is not independent experimental reproduction. The built-in image-generation tool created both figures; its exact model identifier was not exposed. The source manifest binds the actual packaged files.
'''
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for row in rows:z.write(ROOT/row['path'],row['path'])
        z.writestr('README.md',readme)
        z.writestr('source_manifest.json',json.dumps({'scope':f'Standalone {args.chapter} only; other chapter source excluded','files':rows},indent=2)+'\n')
    report={'archive':dest.relative_to(ROOT).as_posix(),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'files':len(rows),'scope':args.chapter+' only'}
    (dest.parent/(dest.stem+'_manifest.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
