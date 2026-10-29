#!/usr/bin/env python3
"""Build a cumulative reviewed edition, with one bibliography and live internal links."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess
from review_sources import chapter_sources
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--through',required=True,help='Last included chapter, for example C02')
    args=ap.parse_args()
    plan=json.loads((ROOT/'book/plan.json').read_text(encoding='utf-8'))
    last=next(c for c in plan['chapters'] if c['id']==args.through)
    chapters=plan['chapters'][:plan['chapters'].index(last)+1]
    tag=f'ch01-{last["number"]:02d}'
    out=ROOT/'build'/tag;out.mkdir(parents=True,exist_ok=True)
    sources=[p.read_text(encoding='utf-8') for p in chapter_sources(ROOT,chapters)]
    source='\n'.join(sources)
    keys={'atlas_style_control'}
    for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])?\{([^}]+)\}',source):
        keys.update(k.strip() for k in group.split(','))
    target_bib=ROOT/f'book/{tag}_references.bib'
    if (ROOT/'bibliography/references.bib').exists():
        from build_book import combine_bibliography
        combine_bibliography()
    master=ROOT/'book/references.bib'
    bibliography=(master if master.exists() else target_bib).read_text(encoding='utf-8')
    starts=list(re.finditer(r'@\w+\s*\{\s*([^,]+),',bibliography));entries={}
    for i,m in enumerate(starts):
        entries[m[1].strip()]=bibliography[m.start():starts[i+1].start() if i+1<len(starts) else len(bibliography)].strip()
    if missing:=keys-entries.keys():raise ValueError('Missing bibliography records: '+str(sorted(missing)))
    target_bib.write_text('\n\n'.join(entries[k] for k in entries if k in keys)+'\n',encoding='utf-8')
    labels={'ch:'+c['id'] for c in chapters}
    outside=set(re.findall(r'\\ref\{(ch:C\d+)\}',source))-labels
    context=[]
    for label in sorted(outside):
        n=next(c['number'] for c in plan['chapters'] if 'ch:'+c['id']==label)
        context.append(r'\expandafter\def\csname atlascontext@'+label+r'\endcsname{'+str(n)+'}')
    aliases=r'''\makeatletter
\newcommand{\AtlasContextRef}[1]{\ifcsname atlascontext@#1\endcsname
\csname atlascontext@#1\endcsname\else\AtlasOriginalRef{#1}\fi}
\AtBeginDocument{\let\AtlasOriginalRef\ref\let\ref\AtlasContextRef}
\makeatother
'''
    date=max(c.get('literature_cutoff',plan['literature_cutoff']) for c in chapters)
    cover=r'''\begin{titlepage}
\centering\vspace*{24mm}
{\Huge\bfseries Agentic State\par}\vspace{6mm}
{\LARGE Context, Memory, and Control\\in Adaptive AI\par}\vspace{14mm}
{\large A Technical Monograph on Conditioning,\\Tool Execution, Verification, and Self-Improvement\par}
\vfill
{\large Chapters 1--'''+str(last['number'])+r'''\par}\vspace{6mm}
{\normalsize Literature and implementation review: '''+date+r'''\par}
\vspace{8mm}
\begin{minipage}{.93\linewidth}\small
Author-reported findings, analytical deductions, and proposed experiments
are distinguished. Source and code inspection are not experimental reproduction.
OpenAI Codex assisted research, drafting, and technical checks. Original
explanatory figures use the built-in image-generation tool; its exact model
identifier was not exposed. No generated measurements or human expert
endorsement are claimed.
\end{minipage}
\end{titlepage}
'''
    if len(chapters)==len(plan['chapters']):
        cover=r'\input{book/frontmatter}'+'\n'
    tex=r'''\documentclass[11pt,oneside,openany]{book}
\usepackage[paperwidth=165mm,paperheight=241mm,inner=22mm,outer=19mm,top=21mm,bottom=22mm]{geometry}
\input{config/packages}
\input{config/notation}
\input{config/book_layout}
'''+ '\n'.join(context)+'\n'+aliases+r'''\begin{document}
\bstctlcite{atlas_style_control}
\frontmatter
'''+cover+r'''\tableofcontents
\mainmatter\label{book:main:start}
'''+''.join(r'\input{'+c['path']+'}\n' for c in chapters)+r'''
\clearpage\label{book:main:end}
\backmatter\bibliographystyle{IEEEtran}
\bibliography{book/'''+tag+r'''_references}
\end{document}
'''
    driver=ROOT/(tag+'_review.tex');driver.write_text(tex,encoding='utf-8')
    env=os.environ.copy();env['BIBINPUTS']=str(ROOT)+os.pathsep+env.get('BIBINPUTS','')
    env.setdefault('SOURCE_DATE_EPOCH','1793232000');env['FORCE_SOURCE_DATE']='1'
    transcript=[]
    def run(cmd):
        r=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
        transcript.append(r.stdout+r.stderr);(out/'transcript.log').write_text('\n'.join(transcript),encoding='utf-8')
        if r.returncode:raise RuntimeError((r.stdout+r.stderr)[-4500:])
    cmd=[shutil.which('pdflatex'),'--disable-installer','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory',str(out),driver.name]
    run(cmd);run([shutil.which('bibtex'),'--disable-installer',str(out/driver.stem)])
    def sig():return hashlib.sha256(b''.join((out/(driver.stem+s)).read_bytes() if (out/(driver.stem+s)).exists() else b'' for s in ('.aux','.toc','.out','.bbl'))).hexdigest()
    prev=sig();stable=False
    for passes in range(2,9):
        run(cmd);now=sig()
        if passes>=3 and now==prev:stable=True;break
        prev=now
    if not stable:raise RuntimeError('Cumulative references did not stabilize')
    log=(out/(driver.stem+'.log')).read_text(encoding='utf-8',errors='replace')
    defects={'undefined_references_or_citations':bool(re.search(r'There were undefined|Citation .+ undefined|Reference .+ undefined',log)),'missing_glyphs':'Missing character:' in log,'overfull_boxes':len(re.findall('Overfull',log))}
    if any(defects.values()):raise ValueError(defects)
    import fitz
    pdf=out/(driver.stem+'.pdf');doc=fitz.open(pdf)
    aux=(out/(driver.stem+'.aux')).read_text(encoding='utf-8')
    page_labels=dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{[^}]*\}\{([^}]+)\}',aux))
    end=int(page_labels['book:main:end'])-1
    starts={c['id']:int(page_labels['ch:'+c['id']]) for c in chapters}
    ranges={c['id']:[starts[c['id']],starts[chapters[i+1]['id']]-1 if i+1<len(chapters) else end] for i,c in enumerate(chapters)}
    dest=ROOT/f'output/pdf/agentic_state_{tag}_{date.replace("-","")}.pdf';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(pdf,dest)
    report={'through':args.through,'chapters':len(chapters),'reviewed_through':date,'pdf':dest.relative_to(ROOT).as_posix(),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'physical_pages':len(doc),'body_pages':end,'chapter_printed_ranges':ranges,'cited_references':len(keys)-1,'latex_passes':passes,'references_stable':stable,'defects':defects,'contextual_chapter_references':sorted(outside)}
    status=ROOT/'internal'/f'{tag}_build.json';status.parent.mkdir(exist_ok=True);status.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
