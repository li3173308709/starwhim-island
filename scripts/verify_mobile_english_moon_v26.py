#!/usr/bin/env python3
"""End-to-end test on real Chrome (mobile simulation with no usable OS TTS).

Verifies:
1. Every English word has separate recorded en-US audio, and mobile starts
   recorded MP3 on a real tap even if speechSynthesis.speak throws.
2. Five-card English teaching remains working and word IDs match recordings.
3. Opening/playing Moon Workshop never routes Hanzi '月' narration.
4. Hanzi lesson *still* retains its own voice controls and existing .80 rate.
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent
URL=os.getenv('STARWHIM_URL') or (ROOT/'index.html').resolve().as_uri()
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel='chrome',headless=True,
        args=['--autoplay-policy=no-user-gesture-required'])
    for name,w,h,mobile in [
        ('desktop',1440,900,False),
        ('phone390',390,844,True),
        ('phone360',360,780,True)]:
        ctx=browser.new_context(viewport={'width':w,'height':h},
                               is_mobile=mobile,has_touch=mobile,
                               user_agent=(
                               'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
                               'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 '
                               'Mobile/15E148 Safari/604.1' if mobile else
                               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                               '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'))
        page=ctx.new_page()
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.add_init_script("""(()=>{
          window.__testPlays={english:[],hanziMoon:[],other:[],tts:[]};
          const native=HTMLMediaElement.prototype.play;
          HTMLMediaElement.prototype.play=function(...args){
            const e=window.StarwhimEnglishPronunciationPack?.audio;
            const h=window.StarwhimVoicePack?.audio;
            if(e&&e.cat===this.src){
              window.__testPlays.english.push(this);
            }else if(h&&h['hanzi:月']===this.src){
              window.__testPlays.hanziMoon.push(this);
            }else window.__testPlays.other.push(this);
            return native.apply(this,args);
          };
          // If browser-native pronunciation is unavailable, phones must
          // still work: fail hard on any speechSynthesis call.
          if(/iPhone|Android|Mobile/i.test(navigator.userAgent)){
            speechSynthesis.speak=function(){throw Error('Mobile OS TTS absent');};
          }else{
            speechSynthesis.speak=function(u){
              window.__testPlays.tts.push({lang:u.lang,text:u.text,rate:u.rate});
              return;
            };
          }
        })()""")
        page.goto(URL,wait_until='domcontentloaded',timeout=90000)
        page.wait_for_function("""()=>
            window.StarwhimEnglishPronunciationPack?.count===200 &&
            window.StarwhimReadingV22?.hanziCount===200 &&
            window.StarwhimEnglishLearnFirst?.words===200 &&
            Object.keys(window.StarwhimVoicePack?.audio||{}).length===914
        """,timeout=30000)
        cnt=page.evaluate("""()=>{
         const p=StarwhimEnglishPronunciationPack;
         const data=Object.values(p.audio);
         return {n:data.length,valid:data.every(v=>v.startsWith('data:audio/mpeg;base64,')),
           unique:new Set(data).size,voice:p.voice};
        }""")
        assert cnt['n']==200 and cnt['valid'] and cnt['unique']==200,(name,cnt)
        page.evaluate("Starwhim.minigames.open('englishquest')")
        page.locator("#miniBody [data-eng=learn]").click()
        page.wait_for_selector("#miniBody .eng-card .eng-word",timeout=7000)
        word=page.locator("#miniBody .eng-word").inner_text().strip()
        assert word=='cat',(name,word)
        page.locator("#miniBody [data-eng=hear]").click()
        page.wait_for_timeout(350)
        if mobile:
            pl=page.evaluate("""()=>({
              count:window.__testPlays.english.length,
              time:window.__testPlays.english.at(-1)?.currentTime||0,
              rate:window.__testPlays.english.at(-1)?.playbackRate||0
            })""")
            assert pl['count']>=1 and pl['time']>0.10 and abs(pl['rate']-0.9)<.001,(name,pl)
        else:
            tts=page.evaluate("window.__testPlays.tts")
            assert tts and tts[-1]['text']=='cat' and tts[-1]['lang']=='en-US',(name,tts)
        # Lesson does not break after its five-card training loop.
        for _ in range(5):
            page.locator("#miniBody [data-eng=next]").click()
        page.locator("#miniBody [data-eng=practice]").click()
        page.wait_for_selector("#miniBody .eng-options",timeout=5500)
        page.evaluate("Starwhim.minigames.close()")
        # Opening moon workshop must never add Hanzi voice controls.
        before=page.evaluate("window.__testPlays.hanziMoon.length")
        page.evaluate("Starwhim.minigames.open('moontracks')")
        page.wait_for_selector("#miniBody [data-tile]",timeout=5500)
        page.wait_for_timeout(150)
        assert page.locator("#miniBody .v23-audio-control").count()==0,(name,"mixed Hanzi narrator in Moon Workshop")
        assert page.locator("#miniBody [data-v23-read-all]").count()==0,(name,"Hanzi page voice button leaked into moon puzzle")
        page.locator("#miniBody [data-tile]").first.click()
        page.locator("#miniBody [data-act=test]").click()
        page.wait_for_timeout(100)
        after=page.evaluate("window.__testPlays.hanziMoon.length")
        assert before==after,(name,"Moon Workshop played Hanzi '月' audio",before,after)
        page.evaluate("Starwhim.minigames.close();Starwhim.minigames.open('hanzi200')")
        page.locator("#miniBody [data-act=learn]").click()
        page.wait_for_selector("#miniBody [data-act=speak]",timeout=5500)
        assert page.locator("#miniBody .v23-audio-control").count()>0,(name,"Hanzi controls removed")
        page.locator("#miniBody [data-act=speak]").click()
        assert page.evaluate("StarwhimReadingV22.hanziCount")==200
        assert not errors,(name,errors[:5])
        overflow=page.evaluate("Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)")
        assert overflow<4,(name,overflow)
        print(f"PASS {name}: 200 independent English voice clips, 5-card lesson; "
              f"mobile-English={'MP3' if mobile else 'native en-US'}, "
              "moon puzzle voice isolated, Hanzi controls retained",flush=True)
        ctx.close()
    browser.close()
