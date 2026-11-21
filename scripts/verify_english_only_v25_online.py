#!/usr/bin/env python3
"""English-only speed/matching regression on real browser and 3 screens."""
import os
from playwright.sync_api import sync_playwright
URL=os.getenv("STARWHIM_URL","https://starwhim-island-ali344s7m-li3173308709-4921.vercel.app")
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel="chrome",headless=True,
                               args=["--autoplay-policy=no-user-gesture-required"])
    for device,width,height,mobile in [
            ("desktop",1440,900,False),("phone390",390,844,True),
            ("phone360",360,780,True)]:
        ctx=browser.new_context(viewport={"width":width,"height":height},
                                is_mobile=mobile,has_touch=mobile)
        page=ctx.new_page()
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.add_init_script("""(()=>{
          window.__rates=[];window.__english=[];
          const native=HTMLMediaElement.prototype.play;
          HTMLMediaElement.prototype.play=function(){
             window.__rates.push(this.playbackRate);
             return native.apply(this,arguments);
          };
          speechSynthesis.speak=(u)=>window.__english.push({text:u.text,rate:u.rate,lang:u.lang});
        })()""")
        page.goto(URL,wait_until="domcontentloaded",timeout=60000)
        page.wait_for_function("""()=>
          window.StarwhimChineseNarratorV23?.exactText &&
          window.StarwhimEnglishLearnFirst?.words===200 &&
          window.StarwhimReadingV22?.hanziCount===200 &&
          Object.keys(window.StarwhimVoicePack?.audio||{}).length===914
        """,timeout=150000)
        page.evaluate("Starwhim.minigames.open('englishquest')")
        page.locator("#miniBody [data-eng=learn]").click()
        page.wait_for_selector("#miniBody .eng-card .eng-meaning",timeout=5000)
        match=page.evaluate("""()=>{
          const n=document.querySelector('#miniBody .eng-meaning');
          return {text:n.textContent,keys:StarwhimChineseNarratorV23.resolve(n),
            exact:StarwhimChineseNarratorV23.exactText};
        }""")
        assert match["text"]=="中文意思是：猫。",(device,match["text"])
        assert match["keys"]==["cn:meaning:cat"],(device,match["keys"])
        assert match["exact"]["cn:meaning:cat"]=="中文意思是：猫。"
        aligned=page.evaluate("""()=>{
          const mapping=StarwhimChineseNarratorV23.exactText;
          const container=document.querySelector('.learnfirst');
          let correct=0,wrong=[];
          for(const [key,text] of Object.entries(mapping)){
            if(!key.startsWith('cn:meaning:'))continue;
            const node=document.createElement('div');
            node.className='eng-meaning';
            node.dataset.voiceWord=key.slice('cn:meaning:'.length);
            node.textContent=text;container.appendChild(node);
            const result=StarwhimChineseNarratorV23.resolve(node);
            if(result.length===1&&result[0]===key)correct++;
            else wrong.push({key,result});
            node.remove();
          }
          const noGuess=document.createElement('p');
          noGuess.className='eng-hint';
          noGuess.textContent='图画是山，看看高山再慢慢试试看。';
          container.appendChild(noGuess);
          const fuzzy=StarwhimChineseNarratorV23.resolve(noGuess);
          noGuess.remove();
          return {correct,wrong:wrong.slice(0,3),fuzzy};
        }""")
        assert aligned["correct"]==200 and not aligned["wrong"],(device,aligned)
        assert aligned["fuzzy"]==[],(device,"unexpected partial word narration",aligned)
        page.locator("#miniBody .eng-meaning .v23-audio-control").first.click()
        page.wait_for_timeout(200)
        rates=page.evaluate("window.__rates")
        assert rates and abs(rates[-1]-.72)<.0001,(device,"English Chinese rate",rates)
        page.locator("#miniBody [data-eng=hear]").click()
        en=page.evaluate("window.__english")
        assert en and en[-1]["text"]=="cat" and en[-1]["lang"]=="en-US",(device,en)
        assert abs(en[-1]["rate"]-.90)<.001,(device,en)
        # Five cards must teach exactly five words before the practice round.
        for n in range(5):
            assert page.locator("#miniBody .eng-card .eng-meaning").count()==1,(device,n)
            page.locator("#miniBody [data-eng=next]").click()
        page.locator("#miniBody [data-eng=practice]").click()
        page.wait_for_selector("#miniBody .eng-question",timeout=6000)
        question=page.evaluate("""()=>{
            let el=document.querySelector('#miniBody .eng-question');
            let keys=StarwhimChineseNarratorV23.resolve(el);
            return {text:el.textContent,keys:keys};
        }""")
        assert question["keys"]==["cn:ui:practice"],(device,question)
        # Hanzi module keeps its original .80 girl-voice playback.
        page.evaluate("Starwhim.minigames.close();Starwhim.minigames.open('hanzi200')")
        page.locator("#miniBody [data-act=learn]").click()
        page.locator("#miniBody [data-act=speak]").click()
        page.wait_for_timeout(170)
        rates=page.evaluate("window.__rates")
        assert abs(rates[-1]-.8)<.0001,(device,"Hanzi rate changed",rates)
        assert not errors,(device,errors[:5])
        print("PASS",device,"200 exact Chinese meaning clips, English .72x, "
              "en-US .90x, Hanzi unchanged .80x; 914 audio clips",flush=True)
        ctx.close()
    browser.close()
