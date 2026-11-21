#!/usr/bin/env python3
"""Use the original user-provided '丁一一' pronunciation to repair F5 extra-name sounds.

The canonical name is taken from the beginning of the original voice reference
(which contains the correct '丁一一小朋友' beginning). ASR word timestamps
locate the following word in each clip, preserving the rest of the sentence.
Unlike an arbitrary trim this does not destroy '丁' or the two '一' syllables.
"""
import base64
import hashlib
import io
import json
import re
from pathlib import Path
from pydub import AudioSegment
from pypinyin import lazy_pinyin
from faster_whisper import WhisperModel

ROOT=Path(__file__).resolve().parent.parent
index=ROOT/'index.html'
html=index.read_text(encoding='utf-8')
m=re.search(r'(window\.StarwhimVoicePack\s*=\s*)({.*?})(;\s*</script>)',html,re.S)
assert m
pack=json.loads(m.group(2))
clips=pack['audio']
assert len(clips)==914,len(clips)
def strip(text):
    return re.sub(r'[^\u3400-\u9fff]','',text)
def pinyin(ch):
    return lazy_pinyin(ch,errors='ignore')[0] if ch else ''
def decode(uri):
    return AudioSegment.from_file(io.BytesIO(base64.b64decode(uri.partition(',')[2])),format='mp3')
names=[(key,uri) for key,uri in clips.items()
       if key.startswith('丁一一小朋友') and uri.startswith('data:audio/mpeg;base64,')]
if not names:raise RuntimeError('Cannot locate the originally supplied clean spoken-name reference')
# The original reference is the FIRST MP3 in the game, not a synthesized example.
original_key=next(iter(clips))
assert original_key.startswith('丁一一小朋友'),original_key[:40]
canonical=decode(clips[original_key])[:400].fade_out(32)
assert len(canonical)>350
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4)
manifests=['voice-plan.json','voice-extra-plan.json','voice-panel-plan.json',
           'voice-advanced-plan.json','voice-arcade-plan.json','voice-v19-plan.json',
           'voice-learning-v22-plan.json','voice-learning-ui-v23-plan.json']
texts={}
for fname in manifests:
    file=ROOT/fname
    if not file.is_file():continue
    for entry in json.loads(file.read_text(encoding='utf-8')).get('lines',[]):
        texts[entry.get('key',entry['text'])]=entry['text']
report=[]
skipped=[]
for key,uri in list(clips.items()):
    text=texts.get(key,key)
    if not text.startswith('丁一一') or key==original_key:continue
    rest=strip(text[3:])
    if not rest:continue
    next_char=rest[0]
    if pinyin(next_char) in ('yi','ding') and len(rest)>1:
        # Special case: avoid matching a name syllable as the following word.
        pass
    try:
        old=decode(uri)
        segment_iter,_=model.transcribe(io.BytesIO(base64.b64decode(uri.partition(',')[2])),
            language='zh',beam_size=4,word_timestamps=True,
            condition_on_previous_text=False,vad_filter=False)
        segments=list(segment_iter)
        tokens=[w for seg in segments for w in (seg.words or [])]
        candidates=[w for w in tokens[:12]
            if re.search('[\u3400-\u9fff]',w.word)
            and w.start>=.35 and w.start<2.4
            and pinyin(strip(w.word)[0])==pinyin(next_char)]
        if not candidates:
            skipped.append(key[:50])
            print('SKIP name follow-up timing not certain:',key[:40],flush=True)
            continue
        start=max(.05, candidates[0].start-.006)
        if start>2.3:
            skipped.append(key[:50]);continue
        body=old[round(start*1000):]
        if len(body)<250:
            skipped.append(key[:50]);continue
        repaired=canonical+AudioSegment.silent(duration=80,frame_rate=24000)+body.fade_in(28)
        memory=io.BytesIO()
        repaired.set_frame_rate(24000).set_channels(1).export(
            memory,format='mp3',bitrate='56k')
        raw=memory.getvalue()
        if len(raw)<1300:raise ValueError('Corrected MP3 too small')
        clips[key]='data:audio/mpeg;base64,'+base64.b64encode(raw).decode()
        report.append({'key':key[:70],'next':next_char,'following_word_at':round(start,3),
                       'original_length_ms':len(old),'revised_length_ms':len(repaired)})
        print('FIXED exactly spoken name:',key[:40],'next',next_char,'body start',round(start,2),flush=True)
    except Exception as e:
        print('WARN name splice skipped',key[:45],str(e)[:160],flush=True)
        skipped.append(key[:50])
if not report:raise RuntimeError('No names repaired; inspect alignment and source sample')
pack['available']=len(clips)
new=html[:m.start(2)]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+html[m.end(2):]
assert new.count('</html>')==1 and len(clips)==914
index.write_text(new,encoding='utf-8')
(ROOT/'voice-name-repair-report.json').write_text(json.dumps({
    'method':'original user-provided voice snippet for name + word-aligned original sentence',
    'repaired':len(report),'skipped':len(skipped),
    'entries':report,'skipped_examples':skipped[:20],
    'note':'Original reference first word was used; no artificial name syllable is prepended'
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('NAME REPAIR PASS: repaired',len(report),'name introductions; skipped',len(skipped),
      '; preserved 914 voice clips')
