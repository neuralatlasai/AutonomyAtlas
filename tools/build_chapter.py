#!/usr/bin/env python3
"""Build one selected chapter with its cited references and shared book layout."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chapter',default='C01')
    args=parser.parse_args()
    plan=json.loads((ROOT/'book/plan.json').read_text(encoding='utf-8'))
    chapter=next(c for c in plan['chapters'] if c['id']==args.chapter)
    ident=args.chapter.lower();number=chapter['number'];out=ROOT/'build'/ident;out.mkdir(parents=True,exist_ok=True)
    driver=ROOT/chapter['path'];modules=[driver]
    for rel in re.findall(r'\\input\{([^}]+)\}',driver.read_text(encoding='utf-8')):
        path=ROOT/rel;modules.append(path if path.suffix else path.with_suffix('.tex'))
    source='\n'.join(p.read_text(encoding='utf-8') for p in modules)
    keys={'atlas_style_control'}
    for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])?\{([^}]+)\}',source):keys.update(x.strip() for x in group.split(','))
    target_bib=ROOT/f'book/{ident}_references.bib'
    master=ROOT/'book/references.bib'
    bibliography=(master if master.exists() else target_bib).read_text(encoding='utf-8')
    starts=list(re.finditer(r'@\w+\s*\{\s*([^,]+),',bibliography));entries={}
    for i,m in enumerate(starts):entries[m[1].strip()]=bibliography[m.start():starts[i+1].start() if i+1<len(starts) else len(bibliography)].strip()
    if missing:=keys-entries.keys():raise ValueError('Missing bibliography records: '+str(sorted(missing)))
    target_bib.write_text('\n\n'.join(entries[k] for k in entries if k in keys)+'\n',encoding='utf-8')
    context_refs=set(re.findall(r'\\ref\{(ch:C\d+)\}',source))-{'ch:'+args.chapter}
    contexts=[]
    for label in sorted(context_refs):
        target=next(c for c in plan['chapters'] if 'ch:'+c['id']==label)
        contexts.append(r'\expandafter\def\csname atlascontext@'+label+r'\endcsname{'+str(target['number'])+'}')
    # Other chapters are contextual numeric references, not local PDF destinations.
    aliases=r'''\makeatletter
\newcommand{\AtlasContextRef}[1]{\ifcsname atlascontext@#1\endcsname
\csname atlascontext@#1\endcsname\else\AtlasOriginalRef{#1}\fi}
\AtBeginDocument{\let\AtlasOriginalRef\ref\let\ref\AtlasContextRef}
\makeatother
'''
    date=chapter.get('literature_cutoff',plan['literature_cutoff'])
    text=r'''\documentclass[11pt,oneside,openany]{book}
\usepackage[paperwidth=165mm,paperheight=241mm,inner=22mm,outer=19mm,top=21mm,bottom=22mm]{geometry}
\input{config/packages}
\input{config/notation}
\input{config/book_layout}
'''+ '\n'.join(contexts)+'\n'+aliases+r'''\begin{document}
\bstctlcite{atlas_style_control}
\frontmatter
\begin{titlepage}
\centering\vspace*{22mm}
{\LARGE\bfseries Agentic State\par}\vspace{6mm}
{\large Context, Memory, and Control in Adaptive AI\par}\vspace{17mm}
{\large Chapter '''+str(number)+r'''\par}\vspace{5mm}
{\LARGE\bfseries '''+chapter['title']+r'''\par}
\vfill
{\normalsize Literature and implementation review: '''+date+r'''\par}
\vspace{8mm}
\begin{minipage}{.93\linewidth}\small
This chapter distinguishes author-reported findings, analytical deductions,
and proposed experiments. Source and code inspection are not experimental
reproduction. OpenAI Codex assisted research, drafting, and technical checks.
The original explanatory figures use the built-in image-generation tool;
its exact model identifier was not exposed. No generated measurements or
human expert endorsement are claimed.
\end{minipage}
\end{titlepage}
\mainmatter
\setcounter{chapter}{'''+str(number-1)+r'''}
\input{'''+chapter['path']+r'''}
\clearpage\label{chapter:body:end}
\backmatter
\bibliographystyle{IEEEtran}
\bibliography{book/'''+ident+r'''_references}
\end{document}
'''
    tex=ROOT/(ident+'_review.tex');tex.write_text(text,encoding='utf-8')
    env=os.environ.copy();env['BIBINPUTS']=str(ROOT)+os.pathsep+env.get('BIBINPUTS','');env.setdefault('SOURCE_DATE_EPOCH','1793232000');env['FORCE_SOURCE_DATE']='1'
    transcript=[]
    def run(command):
        result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
        transcript.append(result.stdout+result.stderr);(out/'transcript.log').write_text('\n'.join(transcript),encoding='utf-8')
        if result.returncode:print((result.stdout+result.stderr)[-5000:]);raise SystemExit(result.returncode)
    cmd=[shutil.which('pdflatex'),'--disable-installer','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory',str(out),tex.name]
    run(cmd);run([shutil.which('bibtex'),'--disable-installer',str(out/tex.stem)])
    def signature():return hashlib.sha256(b''.join((out/(tex.stem+s)).read_bytes() if (out/(tex.stem+s)).exists() else b'' for s in ('.aux','.out','.bbl'))).hexdigest()
    previous=signature();stable=False
    for passes in range(2,9):
        run(cmd);current=signature()
        if passes>=3 and current==previous:stable=True;break
        previous=current
    if not stable:raise RuntimeError('Chapter references did not stabilize')
    import fitz
    pdf=out/(tex.stem+'.pdf');doc=fitz.open(pdf)
    log=(out/(tex.stem+'.log')).read_text(encoding='utf-8',errors='replace')
    defects={'undefined_references_or_citations':bool(re.search(r'There were undefined|Citation .+ undefined|Reference .+ undefined',log)),'missing_glyphs':'Missing character:' in log,'overfull_boxes':len(re.findall('Overfull',log))}
    auxiliary=(out/(tex.stem+'.aux')).read_text(encoding='utf-8')
    end=int(re.search(r'\\newlabel\{chapter:body:end\}\{\{[^}]*\}\{(\d+)\}',auxiliary)[1])
    body_start=next(i for i,p in enumerate(doc) if p.get_label()=='1')
    report={'chapter':args.chapter,'reviewed_through':date,'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'physical_pages':len(doc),'body_pages':end-1,'body_physical_range_inclusive':[body_start+1,body_start+end-1],'cited_references':len(keys)-1,'latex_passes':passes,'references_stable':stable,'defects':defects,'contextual_chapter_references':sorted(context_refs)}
    if any(defects.values()):raise ValueError('Chapter build defects: '+str(defects))
    dest=ROOT/f'output/pdf/chapter_{number:02d}_review_{date.replace("-","")}.pdf';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(pdf,dest)
    status=ROOT/'internal'/f'{ident}_standalone_build.json';status.parent.mkdir(exist_ok=True);status.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
