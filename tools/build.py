#!/usr/bin/env python3
"""Compatibility entry point for the substantive book build."""
import sys
from build_book import main
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='book':sys.argv.pop(1)
 main()
