#!/usr/bin/env python3
"""Detect and conservatively remove F5-TTS invented first syllables.

Unlike a fixed front cut, this uses Mandarin ASR timestamps, expected text,
pinyin similarity and low-confidence gating. It never cuts a first character
that plausibly matches the expected opening.
"""
import argparse
import base64
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
def inventory():
    text=(ROOT/'index.html').read_text(encoding='utf-8')
    m=re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>',text,re.S)
    if not m:raise RuntimeError('Voice package absent')
    pack=json.loads(m.group(1))['audio']
    assert len(pack)==914,len(pack)
    expected={}
    plans=['voice-plan.json','voice-extra-plan.json','voice-panel-plan.json',
           'voice-advanced-plan.json','voice-arcade-plan.json','voice-v19-plan.json',
           'voice-learning-v22-plan.json','voice-learning-ui-v23-plan.json']
    for file in plans:
        p=ROOT/file
        if not p.is_file():continue
        for row in json.loads(p.read_text(encoding='utf-8')).get('lines',[]):
            expected[row.get('key',row['text'])]=row['text']
    items=[(key,uri,expected.get(key,key.split('\n')[-1])) for key,uri in pack.items()
           if not key.startswith('english:') and uri.startswith('data:audio/mpeg;base64,')]
    return items

def sound(ch):
    from pypinyin import lazy_pinyin,Style
    return lazy_pinyin(ch,style=Style.NORMAL,errors='ignore')[0] if ch else ''

def first_hanzi(text):
    m=re.search(r'[\u3400-\u9fff]',text)
    return m.group(0) if m else None

def decide(expected,words):
    if not words:return None
    head=first_hanzi(expected)
    if not head:return None
    valid=[]
    for w in words[:4]:
        chinese=re.sub(r'[^\u3400-\u9fff]','',w.word)
        if chinese:valid.append((chinese,w))
    if len(valid)<2:return None
    first,token=valid[0]
    second,nextword=valid[1]
    # Never discard the first sound when it matches the expected character.
    if sound(first[0])==sound(head):
        return None
    # Conclusive case: low-confidence leading one-syllable phantom,
    # followed immediately by the desired starting character.
    if(len(first)==1 and sound(second[0])==sound(head) and
       token.end<=.33 and token.start<=.07 and token.probability<.64
       and nextword.probability>.20):
        t=max(.01,min(.30,token.end-.012))
        return {'start':round(t,3),'phantom':first,
                'confidence':round(token.probability,3),
                'following':second}
    # Sometimes Whisper groups an extra '一' with '定' as '一定'.
    # Only remove it when there are two following yi syllables, proving
    # that the recorded name has more syllables than written.
    if(head=='丁' and first in ('一定','一丁') and len(valid)>=3
       and sound(valid[1][0][0])=='yi' and sound(valid[2][0][0])=='yi'
       and token.start<=.07 and token.end<=.42):
        t=max(.06,min(.22,token.start+(token.end-token.start)*.49))
        return {'start':round(t,3),'phantom':'一 (grouped)',
                'confidence':round(token.probability,3),
                'following':'丁'}
    return None

def cut_mp3(raw,start):
    cp=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error',
       '-i','pipe:0','-af',f'atrim=start={start:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=.04',
       '-ar','24000','-ac','1','-codec:a','libmp3lame','-b:a','56k','-f','mp3','pipe:1'],
       input=raw,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode or len(cp.stdout)<1300:
        raise RuntimeError(cp.stderr.decode(errors='replace')[:180])
    return cp.stdout

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--shard',type=int,default=0)
    parser.add_argument('--shards',type=int,default=5)
    args=parser.parse_args()
    items=inventory()
    selected=[(i,*entry) for i,entry in enumerate(items) if i%args.shards==args.shard]
    from faster_whisper import WhisperModel
    model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4)
    output=ROOT/'generated'/'syllable-fixes'
    output.mkdir(parents=True,exist_ok=True)
    report=[]
    with tempfile.TemporaryDirectory() as tmp:
        for position,(i,key,uri,expected) in enumerate(selected,1):
            raw=base64.b64decode(uri.partition(',')[2])
            temp=Path(tmp)/'speech.mp3';temp.write_bytes(raw)
            try:
                segments,_=model.transcribe(str(temp),language='zh',beam_size=3,
                     word_timestamps=True,vad_filter=False,
                     condition_on_previous_text=False)
                seg=list(segments)
                words=[w for s in seg for w in (s.words or [])]
                correction=decide(expected,words)
                if correction:
                    revised=cut_mp3(raw,correction['start'])
                    path=output/(hashlib.sha256(key.encode()).hexdigest()[:24]+'.mp3')
                    path.write_bytes(revised)
                    result={'key':key,'file':path.name,'expected':expected[:55],
                            'heard':''.join(x.text for x in seg)[:65],**correction}
                    report.append(result)
                    print('FIXED',position,'/',len(selected),key[:35],result['phantom'],
                          result['start'],'s',flush=True)
            except Exception as e:
                print('WARN',key[:40],str(e)[:180],flush=True)
            if position%30==0:
                print('Scanned',position,'/',len(selected),'in shard',args.shard,flush=True)
    (output/f'report-{args.shard}.json').write_text(json.dumps(
        {'shard':args.shard,'examined':len(selected),'fixed':len(report),'patches':report},
        ensure_ascii=False,indent=2),encoding='utf-8')
    print('Finished shard',args.shard,'scanned',len(selected),'conservative fixes',len(report),flush=True)

if __name__=='__main__':main()
