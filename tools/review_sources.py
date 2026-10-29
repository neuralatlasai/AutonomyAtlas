"""Ordered recursive LaTeX include closure for cumulative editions."""
from pathlib import Path
import re
INPUT=re.compile(r'\\(?:input|include)\s*\{([^{}]+)\}')

def chapter_sources(root:Path,chapters:list[dict])->list[Path]:
    root=root.resolve();result=[];seen=set();active=set()
    def visit(path):
        path=path.resolve()
        if not path.suffix:path=path.with_suffix('.tex')
        if root not in path.parents:raise ValueError('Chapter include leaves the source root')
        if path in active:raise ValueError('Cyclic chapter include: '+str(path))
        if path in seen:return
        if not path.is_file():raise FileNotFoundError(path)
        seen.add(path);active.add(path);result.append(path)
        for rel in INPUT.findall(path.read_text(encoding='utf-8')):visit(root/rel)
        active.remove(path)
    for c in chapters:visit(root/c['path'])
    return result
