#!/usr/bin/env python3
"""Idempotently install expanded v1.9 game modes into the existing single-file game."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent
page=ROOT/'index.html'
s=page.read_text(encoding='utf-8')
mod=(ROOT/'scripts/expansion_v19.js').read_text(encoding='utf-8')
if 'window.StarwhimExpansion19=' in s:
    print('Expansion v1.9 already present; not duplicating scripts')
else:
    anchor='</body></html>'
    if s.count(anchor)!=1 or len(s)<11_000_000:
        raise SystemExit('Unexpected game HTML layout: abort')
    s=s.replace(anchor,'<script>\n'+mod+'\n</script>\n'+anchor)
    page.write_text(s,encoding='utf-8')
assert 'window.StarwhimExpansion19=' in s
print('Expanded game HTML length',len(s))
