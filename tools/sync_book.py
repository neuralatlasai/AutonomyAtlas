#!/usr/bin/env python3
"""Synchronize actual section inventories without synthesizing chapter prose.

Multi-section modules are split once into independent modules. Originals remain
untouched and are listed for a separately verified archival move. Section labels
are stable; planned pages are never interpreted as completed pages.
"""
from pathlib import Path
import json,re,csv
R=Path(__file__).resolve().parents[1]

def main():
 p=R/'book/plan.json';d=json.loads(p.read_text(encoding='utf-8'));retired=[]
 for c in d['chapters']:
  driver=R/c['path'];s=driver.read_text(encoding='utf-8')
  s=re.sub(r'\\chapter\{[^}]*\}',lambda m:r'\chapter{'+c['title']+'}',s,count=1)
  for include in list(re.finditer(r'\\input\{([^}]+)\}',s)):
   path=R/include[1];path=path if path.suffix else path.with_suffix('.tex')
   text=path.read_text(encoding='utf-8')
   if len(re.findall(r'\\section\{',text))<=1:continue
   # Move a chapter overview from a monolithic file's tail to the first actual
   # section, where it can share a page with the following scientific analysis.
   figure=re.search(r'\n% SCIENTIFIC_FIGURE_C\d+\n.*?\\end\{figure\}\s*',text,re.S)
   ftext=figure[0] if figure else ''
   if figure:text=text[:figure.start()]+text[figure.end():]
   pieces=re.split(r'(?=\\section\{)',text);prefix=pieces.pop(0);inputs=[]
   for i,part in enumerate(pieces,1):
    target=path.parent/f'section-{i:02d}.tex'
    body=(prefix if i==1 else '')+part+(ftext if i==1 else '')
    if target.exists() and target.read_text(encoding='utf-8')!=body:
     raise ValueError('Refusing to overwrite an independent module: '+str(target))
    target.write_text(body,encoding='utf-8')
    inputs.append(r'\input{'+target.relative_to(R).as_posix()+'}')
   s=s.replace(include[0],'\n'.join(inputs));retired.append(path.relative_to(R).as_posix())
  driver.write_text(s,encoding='utf-8')
  sections=[]
  for include in re.finditer(r'\\input\{([^}]+)\}',s):
   q=R/include[1];q=q if q.suffix else q.with_suffix('.tex');t=q.read_text(encoding='utf-8')
   for match in re.finditer(r'\\section\{([^}]+)\}',t):
    after=t[match.end():];label=re.search(r'\\label\{(sec:[^}]+)\}',after)
    subheads=[x[1] for x in re.finditer(r'\\subsection\{([^}]+)\}',after)]
    sections.append({'id':f'{c["id"]}.{len(sections)+1}','title':match[1],'path':q.relative_to(R).as_posix(),'label':label[1] if label else None,'subsections':subheads})
  c['sections']=sections
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 out=R/'internal';out.mkdir(exist_ok=True)
 (out/'superseded_section_modules.json').write_text(json.dumps(retired,indent=2)+'\n',encoding='utf-8')
 # Budgets preserve the 370-page editorial target and are explicitly prospective.
 with (R/'book/section_budgets.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(['chapter','section','title','editorial_page_budget','budget_status'])
  for c in d['chapters']:
   weights=[max(1,len((R/x['path']).read_text(encoding='utf-8').split())) for x in c['sections']]
   total=sum(weights);remaining=round(c['target_pages']*100)
   for i,(x,weight) in enumerate(zip(c['sections'],weights)):
    points=remaining if i==len(weights)-1 else round(c['target_pages']*100*weight/total)
    remaining-=points
    w.writerow([c['id'],x['label'],x['title'],f'{points/100:.2f}','Editorial allocation only; actual PDF pages counted independently'])
 print(json.dumps({'chapters':len(d['chapters']),'sections':sum(len(c['sections']) for c in d['chapters']),'old_modules_for_verified_archival_move':retired},indent=2))
if __name__=='__main__':main()
