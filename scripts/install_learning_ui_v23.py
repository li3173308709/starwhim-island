#!/usr/bin/env python3
"""Install Chinese reading controls after both v22 and v23 MP3 packs pass checks."""
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
index=ROOT/'index.html'
s=index.read_text(encoding='utf-8')
m=re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>',s,re.S)
if not m:raise RuntimeError('Embedded MP3 package not found')
clips=json.loads(m.group(1))['audio']
rows=json.loads((ROOT/'voice-learning-ui-v23-plan.json').read_text(encoding='utf-8'))['lines']
words=json.loads(re.search(r'\bconst WORDS=(\[.*?\]);',
        (ROOT/'scripts/learning_v22.js').read_text(encoding='utf-8'),re.S).group(1))
chars=json.loads(re.search(r'\bconst HANZI=(\[.*?\]);',
        (ROOT/'scripts/learning_v22.js').read_text(encoding='utf-8'),re.S).group(1))
if len(words)!=200 or len(chars)!=200:
    raise RuntimeError('Vocabulary inventory changed')
if not all('english:'+x['en'] in clips and 'hanzi:'+chars[i]['char'] in clips
           for i,x in enumerate(words)):
    raise RuntimeError('v22 word and Hanzi recordings not yet installed')
missing=[r['key'] for r in rows if r['key'] not in clips]
if missing:raise RuntimeError(f'Missing {len(missing)} UI narration files; first: {missing[:4]}')
if len(clips)<605+len(rows):
    raise RuntimeError('Installed MP3 count lower than v22 + v23 expected total')
if 'window.StarwhimReadingV22' not in s or 'window.StarwhimEnglishLearnFirst' not in s:
    raise RuntimeError('v22 teaching game not installed')
template=(ROOT/'scripts/learning_ui_voices_v23.js').read_text(encoding='utf-8')
data={'words':[{'en':x['en'],'zh':x['zh']} for x in words],
      'topics':sorted({x['cat'] for x in words}),
      'hanzi':[{'char':x['char'],'word':x['word']} for x in chars]}
script=template.replace('__READING_DATA__',
                        json.dumps(data,ensure_ascii=False,separators=(',',':')))
assert '__READING_DATA__' not in script and 'speechSynthesis' not in script
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'narrator.js'
    p.write_text(script,encoding='utf-8')
    subprocess.run(['node','--check',str(p)],check=True)
if 'window.StarwhimChineseNarratorV23=' not in s:
    s=s.replace('</body>','<script>\n'+script+'\n</script>\n</body>',1)
index.write_text(s,encoding='utf-8')
assert s.count('</html>')==1
print('PASS: Chinese narration:',len(rows),'UI clips; v22: 400 learning clips; total MP3:',len(clips))
