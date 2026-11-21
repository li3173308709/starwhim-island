#!/usr/bin/env python3
"""Inspect Chinese ASR word boundaries to identify *extra* syllables before Ding Yiyi."""
import re,json,base64,tempfile
from pathlib import Path
from faster_whisper import WhisperModel
s=Path('index.html').read_text()
j=json.loads(re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>',s,re.S).group(1))['audio']
targets=[(k,v) for k,v in j.items() if k.startswith('丁一一小冒险家') or
    k.startswith('小冒险家丁一一') or k.startswith('丁一一小朋友') or
    k.startswith('丁一一，')]
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4)
with tempfile.TemporaryDirectory() as d:
 for i,(key,uri) in enumerate(targets[:9]):
  p=Path(d)/(str(i)+'.mp3');p.write_bytes(base64.b64decode(uri.partition(',')[2]))
  segments,_=model.transcribe(str(p),language='zh',beam_size=5,word_timestamps=True,
     condition_on_previous_text=False,vad_filter=False)
  segs=list(segments)
  words=[{'text':w.word,'start':round(w.start,3),'end':round(w.end,3),
          'probability':round(w.probability,2)}
          for segment in segs for w in segment.words or []]
  print('CLIP',i,repr(key[:30]),'ASR',repr(''.join(x.text for x in segs)[:80]),flush=True)
  print('TOKENS',json.dumps(words[:17],ensure_ascii=False),flush=True)
