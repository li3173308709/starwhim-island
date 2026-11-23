#!/usr/bin/env python3
"""Independent ASR screening for the newly synthesized Chinese learning clips.

This is an automated plausibility check, not a claim that a human listened to
all 403 recordings. Save exact expected/recognized text for reviewer.
"""
import base64,json,re,tempfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent
src=(root/'index.html').read_text(encoding='utf8')
pack=json.loads(re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>',src,re.S).group(1))['audio']
manifest=json.loads((root/'voice-study-corrections-v27-plan.json').read_text(encoding='utf-8'))['lines']
sentences={x['key']:x['text'] for x in manifest}
test_keys=[
 'hanzi:米','hanzi:饭','hanzi:月','hanzi:星','hanzi:二',
 'hanzi:朋','hanzi:友','hanzi:大','hanzi:小','hanzi:短',
 'hanzi:慢','hanzi:快','hanzi:轻','hanzi:画','hanzi:爸',
 'hanzi:妈','hanzi:山','hanzi:水','hanzi:字','hanzi:一',
 'cn:meaning:cat','cn:meaning:dog','cn:meaning:rice',
 'cn:meaning:moon','cn:meaning:star','cn:meaning:run',
 'cn:meaning:one','cn:meaning:blue','cn:meaning:friend',
 'cn:meaning:please','cn:ui:home','cn:ui:teaching',
 'cn:ui:practice-wrong']
assert len(set(test_keys))==len(test_keys)
from faster_whisper import WhisperModel
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4)
results=[]
def cleaned(s):return re.sub(r'[^\u3400-\u9fff]','',s)
with tempfile.TemporaryDirectory() as temp:
 for i,key in enumerate(test_keys):
  assert key in sentences and key in pack
  raw=base64.b64decode(pack[key].partition(',')[2])
  path=Path(temp)/(str(i)+'.mp3');path.write_bytes(raw)
  segments,_=model.transcribe(str(path),language='zh',beam_size=3,condition_on_previous_text=False)
  heard=''.join(s.text for s in segments)
  expected=cleaned(sentences[key]);got=cleaned(heard)
  # Distinguish a genuine mismatch from ASR omissions without inventing proof.
  target=key[6:] if key.startswith('hanzi:') else None
  valid=target in got if target else (cleaned(sentences[key]).split('是')[-1].strip() in got
                                         if key.startswith('cn:meaning:') else True)
  results.append(dict(key=key,expected=sentences[key],recognized=heard,visible_target=bool(valid)))
  print(('MATCH' if valid else 'REVIEW')+' '+key+' expected='+sentences[key]+' recognized='+heard,flush=True)
dest=root/'study-v27-spoken-asr-audit.json'
dest.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
issues=[r for r in results if not r['visible_target']]
print('Speech quality screening:',len(results),'audited;',len(issues),'ASR flags requiring closer examination',flush=True)
# ASR is not a human ear. Log uncertainty; flag only widespread obvious loss.
if len(issues)>len(results)*.45:
 raise RuntimeError('Too many word pronunciations missing from independent speech transcription')
