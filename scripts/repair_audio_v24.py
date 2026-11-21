#!/usr/bin/env python3
"""Repair the existing game voice audio without changing quest/game content.

- Chinese character/girl MP3 playback: exactly 0.80x, pitch preserved.
- English word practice: original English voice through browser en-US speech engine,
  not the Chinese girl's F5-TTS MP3.
- Remove overlong initial silence / audible codec clicks from Chinese MP3s, with
  small fade-in; do not trim phonemes or delete the written name 丁一一.
- Do not alter game save format or existing 200+200 entries.
"""
import argparse
import base64
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
INDEX=ROOT/'index.html'
ENGLISH_JS=ROOT/'scripts/learning_v22.js'
AUDIO_FILTER='silenceremove=start_periods=1:start_silence=0.035:start_threshold=-39dB:detection=rms,afade=t=in:st=0:d=0.055'

ENGLISH_VOICE = r"""// English words intentionally use the original clear English-language reader.
// Chinese lessons / narrations continue to use recorded girl-voice MP3 clips.
let lastVoice=null;
let lastEnglishUtterance=null;
function speak(word){
  if(!word)return false;
  const synth=window.speechSynthesis;
  if(!synth||typeof window.SpeechSynthesisUtterance!=='function'){
    const hint=$('engStatus');if(hint)hint.textContent='当前浏览器没有英文朗读功能，请使用 Chrome、Edge 或 Safari。';
    return false;
  }
  try{
    if(lastVoice){lastVoice.pause();lastVoice=null;}
    if(synth.speaking||synth.pending)synth.cancel();
    const utterance=new SpeechSynthesisUtterance(String(word));
    utterance.lang='en-US';
    utterance.rate=.90;utterance.pitch=1;utterance.volume=1;
    const available=synth.getVoices()||[];
    const en=available.filter(v=>/^en([-_]|$)/i.test(v.lang||''));
    const preferred=['en-US','en-GB'];
    const best=en.sort((a,b)=>{
      const score=v=>(preferred.findIndex(p=>(v.lang||'').toLowerCase()===p.toLowerCase())===0?100:0)
        +(/jenny|aria|samantha|zira|sara|female|emma/i.test(v.name||'')?10:0)
        +(v.localService?2:0);
      return score(b)-score(a);
    })[0];
    if(best)utterance.voice=best;
    utterance.onerror=()=>{const hint=$('engStatus');if(hint)hint.textContent='英文语音播放失败，请再点击一次。';};
    lastEnglishUtterance=utterance;
    synth.speak(utterance);
    try{synth.resume?.()}catch(e){}
    return true;
  }catch(e){
    console.warn('English reader unavailable',e);
    const hint=$('engStatus');if(hint)hint.textContent='英文朗读暂不可用，请换一个浏览器试试。';
    return false;
  }
}
"""
def patch_one(src, old, new, label):
    count=src.count(old)
    if count!=1:
        raise RuntimeError(f'{label}: expected one matching snippet; found {count}')
    return src.replace(old,new,1)
def replace_voice_block(src):
    begin='let lastVoice=null;\nfunction speak(word){'
    end='\nconst categories='
    start=src.find(begin)
    if start<0:
        if 'let lastEnglishUtterance=null;' in src:
            return src
        raise RuntimeError('Missing original English voice route')
    stop=src.find(end,start)
    if stop<0:
        raise RuntimeError('No English voice route end')
    return src[:start]+ENGLISH_VOICE+src[stop:]

def fix_runtime(html):
    # Matching one module block in the standalone game and one source module.
    html=replace_voice_block(html)
    html=patch_one(html,
        "function stopRecorded(){if(activeAudio){try{activeAudio.pause();activeAudio.currentTime=0;activeAudio.removeAttribute('src');activeAudio.load()}catch(e){}activeAudio=null}}",
        "function stopRecorded(){if(activeAudio){try{activeAudio.volume=0;activeAudio.pause();}catch(e){}activeAudio=null}}",
        'Stop audio smoothly; avoid unload click')
    html=patch_one(html,
        "clip.preload='auto';clip.volume=1;clip.playsInline=true;activeAudio=clip;started=true;",
        "clip.preload='auto';clip.volume=1;clip.playbackRate=0.8;clip.preservesPitch=true;clip.playsInline=true;activeAudio=clip;started=true;",
        'Main girl voice 0.8x')
    html=patch_one(html,
        "lastHanziVoice=new Audio(src);lastHanziVoice.play().catch(()=>{});return true;",
        "lastHanziVoice=new Audio(src);lastHanziVoice.playbackRate=0.8;lastHanziVoice.preservesPitch=true;lastHanziVoice.play().catch(()=>{});return true;",
        'Chinese Hanzi 0.8x')
    html=patch_one(html,
        "current=new Audio(clips()[unique[i++]]);\n   current.volume=.95;",
        "current=new Audio(clips()[unique[i++]]);\n   current.playbackRate=0.8;current.preservesPitch=true;current.volume=.95;",
        'Chinese educational narrator 0.8x')
    return html

def trim_mp3(raw,key):
    cp=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error',
        '-i','pipe:0','-af',AUDIO_FILTER,
        '-codec:a','libmp3lame','-ar','24000','-ac','1','-b:a','56k',
        '-f','mp3','pipe:1'],input=raw,stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,check=False)
    if cp.returncode or len(cp.stdout)<500:
        print(f'WARN: trim failed for {key[:55]} code={cp.returncode}; '
              f'retrying fade only',flush=True)
        cp=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error',
            '-i','pipe:0','-af','afade=t=in:st=0:d=0.055',
            '-codec:a','libmp3lame','-ar','24000','-ac','1','-b:a','56k',
            '-f','mp3','pipe:1'],input=raw,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,check=False)
        if cp.returncode or len(cp.stdout)<500:
            print(f'WARN: retaining original unprocessable MP3: {key[:55]}',flush=True)
            return raw
    return cp.stdout

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--skip-audio',action='store_true')
    args=parser.parse_args()
    s=INDEX.read_text(encoding='utf-8')
    m=re.search(r'(window\.StarwhimVoicePack\s*=\s*)({.*?})(;\s*</script>)',s,re.S)
    if not m:raise RuntimeError('Girl-voice pack missing')
    pack=json.loads(m.group(2))
    audio=pack['audio']
    assert len(audio)==914, len(audio)
    assert not any('一丁一一' in k for k in audio), 'Unexpected wrong name in the script'
    original_sizes=0
    processed=0
    changed={}
    if not args.skip_audio:
        for key,uri in audio.items():
            # The English learner now uses the previous English-language voice engine.
            # Retain all existing English MP3s for backward compatibility, unmodified.
            if key.startswith('english:'):continue
            if not uri.startswith('data:audio/mpeg;base64,'):continue
            raw=base64.b64decode(uri.partition(',')[2])
            original_sizes+=len(raw)
            updated=trim_mp3(raw,key)
            # No output is allowed to be absurdly short.
            if len(updated)<max(900,int(len(raw)*.13)):
                raise RuntimeError(f'Audio became too short: {key[:48]}')
            changed[key]='data:audio/mpeg;base64,'+base64.b64encode(updated).decode('ascii')
            processed+=1
            if processed%100==0:print(f'Processed {processed} Chinese recorded clips',flush=True)
        if processed<680:raise RuntimeError(f'Chinese audio count unexpectedly low: {processed}')
        audio.update(changed)
    out=s[:m.start(2)]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]
    out=fix_runtime(out)
    source=ENGLISH_JS.read_text(encoding='utf-8')
    source=replace_voice_block(source)
    if 'window.StarwhimChineseNarratorV23' not in out or 'window.StarwhimEnglishLearnFirst' not in out:
        raise RuntimeError('Lost language learning modules')
    assert out.count('</html>')==1
    assert len(audio)==914
    assert source.count("utterance.lang='en-US'")==1
    assert out.count("playbackRate=0.8")==3, out.count("playbackRate=0.8")
    assert "一丁一一" not in ''.join(k for k in audio)
    if not args.dry_run:
        INDEX.write_text(out,encoding='utf-8')
        ENGLISH_JS.write_text(source,encoding='utf-8')
    print(f'PASS: 914 entries; processed {processed} Chinese clips; original audio={original_sizes}B; '
          f'Chinese 0.80x pitch-preserved; English en-US separate; removed extra leading silence; '
          f'dry_run={args.dry_run}',flush=True)

if __name__=='__main__':main()
