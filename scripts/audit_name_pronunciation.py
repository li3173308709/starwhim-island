#!/usr/bin/env python3
"""Targeted QA for unwanted leading syllable before 丁一一.

Transcribes a reproducible selection of recorded passages and reports any
recording that sounds like '一丁一一' rather than the intended '丁一一'.
This is an ASR screening, not a substitute for a parent listening to the audio.
"""
import base64
import json
import re
import tempfile
from pathlib import Path

root=Path(__file__).resolve().parent.parent
s=(root/'index.html').read_text(encoding='utf-8')
m=re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>',s,re.S)
pack=json.loads(m.group(1))['audio']
items=[(k,v) for k,v in pack.items() if
  ('丁一一' in k or k in ['cn:ui:home','cn:button:丁一一真棒','cn:ui:teaching'])]
assert len(items)>25,len(items)
intro=[x for x in items if x[0].startswith('丁一一') or x[0].startswith('cn:ui:')]
other=[x for x in items if x not in intro]
picked=(intro[:16]+other[:14])[:30]
from faster_whisper import WhisperModel
model=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=4)
rows=[]
with tempfile.TemporaryDirectory() as tmp:
 for i,(key,uri) in enumerate(picked,1):
  mp3=Path(tmp)/(str(i)+'.mp3')
  mp3.write_bytes(base64.b64decode(uri.partition(',')[2]))
  segments,_=model.transcribe(str(mp3),language="zh",beam_size=3,
      vad_filter=False,condition_on_previous_text=False)
  heard=''.join(z.text for z in segments).replace(' ','').replace('，','').replace('。','')
  suspicious='一丁一一' in heard or '一丁一' in heard[:5]
  rows.append({'key':key[:65],'heard':heard[:100],'suspicious':suspicious})
  print('SUSPECT' if suspicious else 'CHECK',i,'source:',key[:38],'heard:',heard[:80],flush=True)
(Path('name-pronunciation-qa.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('NAME QA: transcribed',len(rows),'clips; suspected extra leading yi:',
      sum(r['suspicious'] for r in rows))
