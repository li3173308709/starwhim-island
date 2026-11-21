#!/usr/bin/env python3
"""Acceptance of 0.8x Chinese narrator, separate en-US word reader,
and smooth MP3 start against a real deployed game.
"""
import os
from playwright.sync_api import sync_playwright
URL=os.getenv('STARWHIM_URL','https://starwhim-island.vercel.app')
with sync_playwright() as pw:
  browser=pw.chromium.launch(channel='chrome',headless=True,
    args=['--autoplay-policy=no-user-gesture-required'])
  for device,width,height,mobile in [
      ('desktop',1440,900,False),('phone390',390,844,True),('phone360',360,780,True)]:
    context=browser.new_context(viewport={'width':width,'height':height},
                                is_mobile=mobile,has_touch=mobile)
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda err: errors.append(str(err)))
    page.add_init_script("""(()=>{
      window.__voiceAudit={recorded:[],english:[]};
      const original=HTMLMediaElement.prototype.play;
      HTMLMediaElement.prototype.play=function(...args){
        window.__voiceAudit.recorded.push({
          rate:this.playbackRate,
          url:String(this.currentSrc||this.src||'').slice(0,40)
        });
        return original.apply(this,args);
      };
      const source=speechSynthesis.speak.bind(speechSynthesis);
      speechSynthesis.speak=function(u){
        window.__voiceAudit.english.push({text:u.text,lang:u.lang,rate:u.rate,
          voice:u.voice?.name||''});
        // No need to wait for OS speech in headless test; capture exact request.
        return;
      };
    })()""")
    page.goto(URL,wait_until='domcontentloaded',timeout=60000)
    page.wait_for_function("""() =>
      window.StarwhimChineseNarratorV23?.ready &&
      window.StarwhimEnglishLearnFirst?.words===200 &&
      Object.keys(window.StarwhimVoicePack?.audio||{}).length===914
    """,timeout=130000)
    # The original English card reader must request native en-US speech.
    page.evaluate("Starwhim.minigames.open('englishquest')")
    page.locator("#miniBody [data-eng=learn]").click()
    page.locator("#miniBody [data-eng=hear]").click()
    en=page.evaluate("window.__voiceAudit.english")
    assert en and en[-1]['lang']=='en-US' and en[-1]['rate']==0.9,(device,en)
    assert en[-1]['text'] in ['cat','dog','bird','fish','lion'],(device,en)
    # It must not play a recorded Chinese F5 voice when the English button is used.
    after_english=page.evaluate("window.__voiceAudit.recorded.length")
    assert after_english==0,(device,"English erroneously routed through recorded girl voice",after_english)
    # The meaning should be a girl narration at 0.8x.
    page.locator("#miniBody .eng-meaning .v23-audio-control").first.click()
    page.wait_for_timeout(180)
    recordings=page.evaluate("window.__voiceAudit.recorded")
    assert recordings and all(abs(a['rate']-.8)<.00001 for a in recordings),(device,recordings)
    # Hanzi single-character/word girl voice must also be .8 and pitch-preserved.
    page.evaluate("Starwhim.minigames.close();Starwhim.minigames.open('hanzi200')")
    page.locator("#miniBody [data-act=learn]").click()
    page.locator("#miniBody [data-act=speak]").click()
    page.wait_for_timeout(160)
    recordings=page.evaluate("window.__voiceAudit.recorded")
    assert len(recordings)>=2 and all(abs(a['rate']-.8)<.00001 for a in recordings),(device,recordings)
    # Decoding the reprocessed MP3 should show an intentional quiet/faded onset.
    info=page.evaluate("""async()=>{
      const src=window.StarwhimVoicePack.audio['hanzi:日'];
      let res=await fetch(src),buff=await res.arrayBuffer();
      let context=new (window.AudioContext||window.webkitAudioContext)();
      let data=await context.decodeAudioData(buff);
      let a=data.getChannelData(0);
      let n=Math.min(Math.round(data.sampleRate*.025),a.length),peak=0;
      for(let i=0;i<n;i++)peak=Math.max(peak,Math.abs(a[i]));
      await context.close();
      return {peak,duration:data.duration};
    }""")
    assert info['duration']>0.5 and info['peak']<.055,(device,'MP3 audio onset not smoothed',info)
    assert not errors,(device,errors[:5])
    overflow=page.evaluate("Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)")
    assert overflow<=3,(device,'horizontal overflow',overflow)
    print('PASS',device,'English original reader en-US',en[-1]['text'],
      'Chinese rate .8x',len(recordings),'clean onset',info,flush=True)
    context.close()
  browser.close()
