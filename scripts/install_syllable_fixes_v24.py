#!/usr/bin/env python3
"""Merge only the ASR-confirmed leading-syllable fixes into 914-clip game."""
import base64
import json
import re
from pathlib import Path
root=Path(__file__).resolve().parent.parent
index=root/'index.html'
s=index.read_text(encoding='utf-8')
m=re.search(r'(window\.StarwhimVoicePack\s*=\s*)({.*?})(;\s*</script>)',s,re.S)
assert m
pack=json.loads(m.group(2))
audio=pack['audio']
assert len(audio)==914,len(audio)
folder=root/'generated'/'syllable-fixes'
reports=[]
for n in range(5):
    p=folder/f'report-{n}.json'
    if not p.is_file():raise RuntimeError(f'Missing ASR report {n}')
    reports.append(json.loads(p.read_text(encoding='utf-8')))
total=sum(j['examined'] for j in reports)
assert total==714,total
changed=0
summary=[]
for j in reports:
 for r in j['patches']:
    key=r['key']
    p=folder/r['file']
    if not p.is_file() or p.stat().st_size<1300:raise RuntimeError(f'Invalid fixed MP3 {p}')
    if key not in audio:raise RuntimeError(f'Missing original MP3 {key}')
    audio[key]='data:audio/mpeg;base64,'+base64.b64encode(p.read_bytes()).decode()
    summary.append({k:v for k,v in r.items() if k!='file'})
    changed+=1
assert changed>0, 'ASR reported no extra syllable; investigate recognizer results'
pack['available']=len(audio)
updated=s[:m.start(2)]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]
assert updated.count('</html>')==1
assert len(audio)==914
assert 'window.StarwhimEnglishLearnFirst' in updated
assert "utterance.lang='en-US'" in updated
assert updated.count('playbackRate=0.8')==3
index.write_text(updated,encoding='utf-8')
(root/'voice-syllable-cleanup-report.json').write_text(json.dumps({
 'scanned':total,'patched':changed,'entries':summary,
 'method':'low-confidence extra Hanzi or grouped 一 + forced ASR timestamp, never trim first matching syllable',
 'warning':'Automated Mandarin ASR is fallible; human listening is recommended for uncommon names'
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: examined',total,'Chinese recordings; removed',changed,
      'high-confidence excess opening syllables; maintained',len(audio),'MP3s.')
