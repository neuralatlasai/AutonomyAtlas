#!/usr/bin/env python3
"""Copy only the exact locally reviewed artifact; this does not publish externally."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1]
def main():
 status=json.loads((R/'book/validation_summary.json').read_text(encoding='utf-8'))
 pdf=R/'output/pdf/agentic_ai_systems_draft.pdf'
 if hashlib.sha256(pdf.read_bytes()).hexdigest()!=status['pdf_sha256']:
  raise SystemExit('PDF differs from the locally reviewed artifact. Rebuild and review before copying.')
 if status['layout_pages_screened']!=status['physical_pages'] or not status['mechanical_checks_passed']:
  raise SystemExit('Incomplete artifact checks.')
 for rel,expected in status['publication_input_hashes'].items():
  p=R/rel
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
   raise SystemExit('Publication source changed after review: '+rel)
 destination=R/'output/pdf/agentic_state_monograph.pdf';shutil.copy2(pdf,destination)
 print(str(destination))
if __name__=='__main__':main()
