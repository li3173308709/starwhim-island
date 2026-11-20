#!/usr/bin/env python3
"""Install or update the v1.9 module while preserving the complete existing game."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent.parent
page=ROOT/'index.html'
s=page.read_text(encoding='utf-8')
mod=(ROOT/'scripts/expansion_v19.js').read_text(encoding='utf-8')
anchor='</body></html>'
if s.count(anchor)!=1 or len(s)<11_000_000:raise SystemExit('Unexpected game HTML')
pattern=r'<script>\s*/\* Starwhim Island: advanced-play and learning expansion \(standalone, offline\)\. \*/.*?</script>'
new_script='<script>\n'+mod+'\n</script>'
if re.search(pattern,s,re.S):
    s,count=re.subn(pattern,lambda _:new_script,s,count=1,flags=re.S)
    assert count==1
    print('Updated v1.9 extension')
else:
    s=s.replace(anchor,new_script+'\n'+anchor)
    print('Installed v1.9 extension')
assert 'window.StarwhimExpansion19=' in s and s.count('window.StarwhimExpansion19=')==1
page.write_text(s,encoding='utf-8')
print('Game HTML chars',len(s))
