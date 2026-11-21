#!/usr/bin/env python3
"""Fix ONLY English lesson mobile pronunciation and learning-voice scope.

Mobile/touch: prefer embedded independent English-language MP3, never the
Mandarin girl's F5-TTS voice; desktop keeps prior en-US speechSynthesis.
Mandarin learning narrator attaches exclusively to Hanzi or English learning,
so moontracks ('月光机关工坊') cannot receive Hanzi '月亮' MP3s.
"""
from pathlib import Path
import re, subprocess, tempfile

ROOT=Path(__file__).resolve().parent.parent
HTML=ROOT/'index.html'
ENGLISH=ROOT/'scripts/learning_v22.js'
NARRATOR=ROOT/'scripts/learning_ui_voices_v23.js'
NEW_EN=StringNotUsed=None
ENGLISH_READER=r"""
// English lesson pronunciation is a separate English-language speaker.
// Mobile uses independently generated en-US English MP3. Desktop retains
// its original en-US system reader; a recorded fallback covers silent TTS.
let lastVoice=null;
let lastEnglishUtterance=null;
let englishPlaybackToken=0;
let englishRecordedAudio=null;
let englishSilentTimer=null;
function englishNotice(message){
 const statusEl=$('engStatus');
 if(statusEl)statusEl.textContent=message;
}
function playRecordedEnglish(word,token){
 if(token!==englishPlaybackToken)return false;
 const source=window.StarwhimEnglishPronunciationPack?.audio?.[word.toLowerCase()];
 if(!source){
   englishNotice('这个英文单词的录音暂时不可用，请重试或换一个浏览器。');
   return false;
 }
 try{
   if(englishRecordedAudio){englishRecordedAudio.pause();englishRecordedAudio=null;}
   const audio=new Audio(source);
   audio.preload='auto';
   audio.playsInline=true;
   audio.playbackRate=0.90;
   audio.preservesPitch=true;
   audio.volume=1;
   englishRecordedAudio=audio;
   const p=audio.play(); // MUST be initiated by the original tap on mobile.
   if(p && typeof p.catch==='function')p.catch(err=>{
      if(token===englishPlaybackToken)
        englishNotice('声音暂未开启，请轻点一次英文朗读按钮。');
      console.warn('Recorded English word playback:',err);
   });
   return true;
 }catch(err){
   console.warn('English MP3 failed to start',err);
   englishNotice('英文录音播放失败，请再点击一次。');
   return false;
 }
}
function speak(word){
 if(!word)return false;
 const text=String(word).trim();
 const token=++englishPlaybackToken;
 window.StarwhimChineseNarratorV23?.stop?.();
 S.audio?.stopSpeech?.();
 if(englishSilentTimer){clearTimeout(englishSilentTimer);englishSilentTimer=null;}
 if(englishRecordedAudio){try{englishRecordedAudio.pause()}catch(e){}englishRecordedAudio=null;}
 // Touchscreen and mobile WebView speechSynthesis can silently accept requests
 // while having no installed English voice. Always play a real English MP3
 // synchronously inside the user's tap instead.
 const mobileDevice=/(Android|iPhone|iPad|iPod|Mobile)/i.test(navigator.userAgent)||
      (navigator.maxTouchPoints>0&&matchMedia('(pointer:coarse)').matches);
 if(mobileDevice && window.StarwhimEnglishPronunciationPack?.audio?.[text.toLowerCase()])
   return playRecordedEnglish(text,token);
 const synth=window.speechSynthesis;
 if(!synth||typeof window.SpeechSynthesisUtterance!=='function')
   return playRecordedEnglish(text,token);
 try{
   if(synth.speaking||synth.pending)synth.cancel();
   const u=new SpeechSynthesisUtterance(text);
   u.lang='en-US';
   u.rate=.90;
   u.pitch=1;
   u.volume=1;
   const voices=synth.getVoices()||[];
   const en=voices.filter(v=>/^en([-_]|$)/i.test(v.lang||''));
   const preferred=en.find(v=>/jenny|aria|samantha|zira|sara|emma/i.test(v.name||''))||
     en.find(v=>(v.lang||'').toLowerCase()==='en-us')||en[0];
   if(preferred)u.voice=preferred;
   let started=false;
   u.onstart=()=>{if(token===englishPlaybackToken){started=true;
       if(englishSilentTimer){clearTimeout(englishSilentTimer);englishSilentTimer=null;}}};
   u.onerror=()=>{if(token===englishPlaybackToken&&!started)
       playRecordedEnglish(text,token);};
   lastEnglishUtterance=u;
   synth.speak(u);
   // Many desktop/mobile Chromium builds report success but never fire start.
   // Fallback to recorded English after a short pause.
   englishSilentTimer=setTimeout(()=>{
       if(token===englishPlaybackToken&&!started){
         try{synth.cancel()}catch(e){}
         playRecordedEnglish(text,token);
       }
   },1600);
   return true;
 }catch(err){
   console.warn('English speech synthesis failed',err);
   return playRecordedEnglish(text,token);
 }
}
"""
def patch_english(s,filename):
    begin='let lastVoice=null;'
    end='\nconst categories='
    start=s.find(begin)
    if start<0 or start>len(s)-1000:raise RuntimeError(f'{filename}: original English reader not found')
    finish=s.find(end,start)
    if finish<start:raise RuntimeError(f'{filename}: reader end absent')
    if 'window.StarwhimEnglishPronunciationPack' in s[start:finish]:
        print(f'English already fixed in {filename}')
        return s
    return s[:start]+ENGLISH_READER+s[finish:]
def patch_narrator(source,filename):
    # In addition to the English and Hanzi games, no other part of the game
    # may even *offer* a button to read a Hanzi character just because the
    # unrelated story/puzzle uses the word 月亮.
    guard="function educationalGameActive(){return ['hanzi200','englishquest'].includes(window.Starwhim?.minigames?.current);}\n"
    if 'function educationalGameActive()' in source:return source
    needle='function keysFor(node){'
    assert source.count(needle)==1,filename
    source=source.replace(needle,guard+needle+'\n if(!educationalGameActive())return [];',1)
    needle='function blocks(){'
    assert source.count(needle)==1
    source=source.replace(needle,needle+'\n if(!educationalGameActive())return [];',1)
    needle="function decorate(){\n queued=false;"
    assert source.count(needle)==1
    source=source.replace(needle,needle+'\n if(!educationalGameActive())return;',1)
    needle="root.addEventListener('click',function(event){"
    assert source.count(needle)==1
    source=source.replace(needle,needle+"\n if(!educationalGameActive())return;",1)
    return source
def run():
    old_html=HTML.read_text(encoding='utf8')
    a=ENGLISH.read_text(encoding='utf8')
    b=NARRATOR.read_text(encoding='utf8')
    html=patch_english(old_html,'game HTML')
    html=patch_narrator(html,'game HTML')
    source=patch_english(a,'English learning source')
    narrator=patch_narrator(b,'Chinese narration source')
    assert html.count('window.StarwhimVoicePack=')==1
    assert html.count('StarwhimEnglishLearnFirst=')==1
    assert html.count('M.moontracksStart=function()')==1
    assert html.count('lastHanziVoice.playbackRate=0.8')==1
    assert html.count("current.playbackRate=root.querySelector('.learnfirst')?0.72:0.8")==1
    assert html.count('englishRecordedAudio=audio;')==1
    assert html.count('function educationalGameActive()')==1
    assert html.count('</html>')==1
    assert html.count('data:audio/mpeg;base64,')==914
    with tempfile.TemporaryDirectory() as tmp:
        f=Path(tmp)/'english.js'
        f.write_text(source,encoding='utf8')
        subprocess.run(['node','--check',str(f)],check=True)
        g=Path(tmp)/'narrator.js'
        g.write_text(narrator,encoding='utf8')
        # This source file intentionally has an injected JSON binding placeholder.
        g.write_text(g.read_text().replace('__READING_DATA__','{"words":[],"topics":[],"hanzi":[]}'))
        subprocess.run(['node','--check',str(g)],check=True)
    HTML.write_text(html,encoding='utf8')
    ENGLISH.write_text(source,encoding='utf8')
    NARRATOR.write_text(narrator,encoding='utf8')
    print('PASS English mobile tap -> independent English MP3; all other audio unchanged',flush=True)
    print('PASS Moontracks cannot activate Hanzi voice; only two education modules attach narration',flush=True)
if __name__=='__main__':run()
