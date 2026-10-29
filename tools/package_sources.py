#!/usr/bin/env python3
"""Package the current book source, accepted figures, and public research maps."""
from pathlib import Path
import json,hashlib,zipfile,argparse
R=Path(__file__).resolve().parents[1]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='output/source/agentic_state_source.zip');a=ap.parse_args()
 files=set()
 for name in ['monograph.tex','index.md','BOOK.md','README.md','AGENTS.md','LICENSE','publication_format.md','.latexmkrc']:
  p=R/name
  if p.is_file():files.add(p)
 for folder,extensions in [('config',{'.tex'}),('bibliography',{'.bib'}),('tools',{'.py'}),('book/chapters',{'.tex'})]:
  files.update(p for p in (R/folder).rglob('*') if p.is_file() and p.suffix in extensions)
 for p in (R/'book').iterdir():
  if p.is_file() and p.suffix in {'.json','.bib','.csv','.tex','.md'}:files.add(p)
 manifest=R/'book/figures/manifest.json';files.add(manifest)
 for item in json.loads(manifest.read_text(encoding='utf-8'))['figures']:
  asset=R/item['asset'];files.add(asset)
  prompt=R/'book/figures/prompts'/(asset.stem+'.txt')
  if not prompt.exists():raise ValueError('Missing original prompt: '+str(prompt))
  files.add(prompt)
 rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
 dest=R/a.output;dest.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for row in rows:z.write(R/row['path'],row['path'])
  z.writestr('source_manifest.json',json.dumps({'scope':'Current substantive book; excludes supplied corpus, private provenance, rejected drafts, and build intermediates','files':rows},indent=2)+'\n')
 report={'archive':dest.relative_to(R).as_posix(),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'files':len(rows)}
 (dest.parent/'package_manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
