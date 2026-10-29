#!/usr/bin/env python3
"""Build the substantive rewrite; unfinished chapters remain visibly unavailable.

This command does not use planned budgets as actual pages. It creates a draft PDF,
records physical chapter ranges from LaTeX labels, and checks citation resolution.
"""
from pathlib import Path
import argparse,subprocess,shutil,os,json,re,hashlib,time
R=Path(__file__).resolve().parents[1]

def combine_bibliography():
 parts=[R/'bibliography/references.bib']+sorted((R/'bibliography').glob('rewrite_*.bib'))
 keys=set();entries={};order=[]
 def version(s):
  v=re.findall(r'arxiv\.org/(?:abs|html)/\d{4}\.\d+(?:v(\d+))?',s)
  return max([int(x) if x else 1 for x in v] or [0])
 for p in parts:
  text=p.read_text(encoding='utf-8-sig')
  matches=list(re.finditer(r'@\w+\s*\{\s*([^,]+),',text))
  for i,m in enumerate(matches):
   key=m[1].strip();entry=text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)].strip()
   if key in entries:
    a=set(re.findall(r'\d{4}\.\d{4,5}',entries[key]));b=set(re.findall(r'\d{4}\.\d{4,5}',entry))
    if not (a and a==b):raise ValueError('Conflicting duplicate key '+key)
    if version(entry)>version(entries[key]):entries[key]=entry
   else:order.append(key);entries[key]=entry
   keys.add(key)
 # Detailed inspection notes stay in the source ledgers; publication references
 # retain identity/version through exact URLs and one uniform access date.
 out=[]
 for k in order:
  raw=entries[k]
  access='29' if re.search(r'2026-10-29|29 October 2026',raw) else '28'
  entry=re.sub(r'\bnote\s*=\s*\{[^\n]*\}',lambda m:'note={Accessed '+access+' October 2026.}',raw)
  # Decorative webpage-title emoji have no bibliographic semantic role and are
  # not supported by pdfLaTeX. Preserve original titles in provenance inputs.
  entry=''.join(c for c in entry if ord(c)<=0xFFFF)
  out.append(entry)
 dest=R/'book/references.bib';dest.write_text('\n\n'.join(out)+'\n',encoding='utf-8')
 return keys

def make_driver():
 plan=json.loads((R/'book/plan.json').read_text(encoding='utf-8'))
 body=[r'''\documentclass[11pt,oneside,openany]{book}
\usepackage[paperwidth=165mm,paperheight=241mm,inner=22mm,outer=19mm,top=21mm,bottom=22mm]{geometry}
\input{config/packages}
\input{config/notation}
\input{config/book_layout}
\begin{document}
\bstctlcite{atlas_style_control}
\frontmatter
\input{book/frontmatter}
\tableofcontents
\mainmatter
\label{book:main:start}
''']
 for c in plan['chapters']:
  p=R/c['path']
  if p.exists():body.append(f'\\input{{{c["path"]}}}\n')
  else:body.append(f'% Chapter {c["id"]} not yet written; excluded from draft.\n')
 body.append(r'''\clearpage\label{book:main:end}
\backmatter
\bibliographystyle{IEEEtran}
\bibliography{book/references}
\end{document}
''')
 (R/'monograph.tex').write_text(''.join(body),encoding='utf-8')
 return plan

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--passes',type=int,default=3);ap.add_argument('--no-compile',action='store_true');a=ap.parse_args()
 keys=combine_bibliography();plan=make_driver()
 if a.no_compile:print('Generated driver and',len(keys),'bibliographic records');return
 out=R/'build/book';out.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env['BIBINPUTS']=str(R)+os.pathsep+env.get('BIBINPUTS','');env.setdefault('SOURCE_DATE_EPOCH','1793145600');env['FORCE_SOURCE_DATE']='1'
 commands=[];cmd=[shutil.which('pdflatex'),'--disable-installer','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory',str(out),'monograph.tex']
 log=[]
 def run(c):
  x=subprocess.run(c,cwd=R,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120);log.append(x.stdout+x.stderr);(out/'transcript.log').write_text('\n'.join(log),encoding='utf-8')
  if x.returncode:print('\n'.join((x.stdout+x.stderr).splitlines()[-30:]));raise SystemExit(x.returncode)
 # Refresh a stale bibliography before a first pass can encounter old invalid TeX.
 aux=out/'monograph.aux'
 # A failed TeX pass can leave a truncated auxiliary file. Only pre-refresh
 # BibTeX when its complete input declarations survived that pass.
 aux_text=aux.read_text(encoding='utf-8',errors='replace') if aux.exists() else ''
 if all(marker in aux_text for marker in ('\\citation','\\bibdata','\\bibstyle')):run([shutil.which('bibtex'),'--disable-installer',str(aux.with_suffix(''))])
 run(cmd)
 if '\\citation' in aux.read_text(encoding='utf-8',errors='replace'):run([shutil.which('bibtex'),'--disable-installer',str(aux.with_suffix(''))])
 def reference_signature():
  h=hashlib.sha256()
  for suffix in ('.aux','.toc','.out','.bbl'):
   f=out/('monograph'+suffix)
   h.update(suffix.encode());h.update(f.read_bytes() if f.exists() else b'')
  return h.hexdigest()
 previous=reference_signature();converged=False;latex_passes=1
 for latex_passes in range(2,max(8,a.passes)+1):
  run(cmd);current=reference_signature()
  if latex_passes>=max(3,a.passes) and current==previous:
   converged=True;break
  previous=current
 if not converged:raise RuntimeError('LaTeX references did not stabilize; inspect auxiliary files and log.')
 pdf=out/'monograph.pdf'
 dest=R/'output/pdf/agentic_ai_systems_draft.pdf';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(pdf,dest)
 from pypdf import PdfReader
 reader=PdfReader(str(pdf));pagecount=len(reader.pages)
 labels={m[0]:m[1] for m in re.findall(r'\\newlabel\{([^}]+)\}\{\{[^}]*\}\{([^}]+)\}',aux.read_text(encoding='utf-8',errors='replace'))}
 text=(out/'monograph.log').read_text(encoding='utf-8',errors='replace')
 report={'physical_pdf_pages':pagecount,'main_text_end_page':labels.get('book:main:end'),'chapter_start_pages':{c['id']:labels.get('ch:'+c['id']) for c in plan['chapters']},'bibliographic_records':len(keys-{'atlas_style_control'}),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'undefined_citations_or_refs':bool(re.search(r'There were undefined|Citation .+ undefined|Reference .+ undefined',text)),'missing_glyphs':bool(re.search('Missing character:',text)),'overfull_boxes':len(re.findall('Overfull',text)),'latex_passes':latex_passes,'reference_files_stable':converged,'stage':'Substantive manuscript; release review not inferred from compilation'}
 (R/'internal').mkdir(exist_ok=True)
 (R/'internal/book_build_status.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
