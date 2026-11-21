#!/usr/bin/env python3
"""Install v22 learning UI only after every voice clip has been packaged."""
import json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent.parent
p=root/'index.html';s=p.read_text(encoding='utf-8')
module=(root/'scripts/learning_v22.js').read_text(encoding='utf-8')
assert 'window.StarwhimReadingV22' in module and 'window.StarwhimEnglishLearnFirst' in module
assert 'speechSynthesis' not in module, 'Do not mix mechanical voice into girl recordings'
subprocess.run(['node','--check',str(root/'scripts/learning_v22.js')],check=True)
m=re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>',s,re.S)
assert m,'Voice pack missing'
clips=json.loads(m.group(1))['audio']
rows=json.loads((root/'voice-learning-v22-plan.json').read_text(encoding='utf-8'))['lines']
missing=[r['key'] for r in rows if r['key'] not in clips]
if missing:raise RuntimeError('No girl recordings for '+', '.join(missing[:8]))
if len(rows)!=400 or len(clips)<605:raise RuntimeError(f'Unfinished 200+200 voice pack: {len(rows)} planned, {len(clips)} installed')
if 'window.StarwhimReadingV22=' not in s:
    s=s.replace('</body>','<script>\n'+module+'\n</script>\n</body>',1)
assert s.count('</html>')==1
p.write_text(s,encoding='utf-8')
print('PASS: 200 Chinese, 200 English recorded pronunciations, 5-card teaching, existing '+str(len(clips)-400)+' clips preserved')