#!/usr/bin/env python3
"""Verify production URL actually boots the 194-MP3 game, not the loading shell."""
from pathlib import Path
import json,os
from playwright.sync_api import sync_playwright,TimeoutError as PWTimeout

URL=os.getenv('STARWHIM_URL','https://starwhim-island.vercel.app')
root=Path(__file__).resolve().parent.parent
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel='chrome',headless=True,args=['--autoplay-policy=no-user-gesture-required'])
    for label,width,height,is_mobile in [('desktop',1440,900,False),('phone-390',390,844,True),('phone-360',360,780,True)]:
        ctx=browser.new_context(viewport={'width':width,'height':height},is_mobile=is_mobile,has_touch=is_mobile)
        page=ctx.new_page()
        errors=[]
        page.on('pageerror',lambda error: errors.append(str(error)))
        page.add_init_script("""(() => {
           window.__voiceEvents=[];
           const orig=HTMLMediaElement.prototype.play;
           HTMLMediaElement.prototype.play=function() {
             window.__voiceEvents.push(this.currentSrc||this.src||'');
             return Promise.resolve();
           };
        })()""")
        page.goto(URL,wait_until='domcontentloaded',timeout=60000)
        try:
            page.wait_for_function("Object.keys(window.StarwhimVoicePack?.audio||{}).length>=194",timeout=110000)
        except PWTimeout:
            raise AssertionError(f'{label} production not loaded: title={page.title()} body={page.locator("body").inner_text()[:450]} errors={errors[-3:]}')
        count=page.evaluate("Object.keys(window.StarwhimVoicePack.audio).length")
        decoded=page.evaluate("""async () => {
          const uri=Object.values(window.StarwhimVoicePack.audio)[0];
          const audio=new Audio(uri);
          audio.preload='auto';
          await audio.play();
          await new Promise(resolve=>setTimeout(resolve,650));
          const result={currentTime:audio.currentTime,duration:audio.duration,readyState:audio.readyState};
          audio.pause();
          return result;
        }""")
        assert decoded['currentTime']>0.15 and decoded['readyState']>=2, f'{label} MP3 playback stalled: {decoded}'
        print(f"{label} MP3 playback progressed {decoded['currentTime']:.2f}s of {decoded['duration']:.2f}s",flush=True)
        assert not errors, f'{label} runtime errors {errors[:4]}'
        assert page.locator('button:has-text("待配音")').count()==0, f'{label} outstanding voice placeholders'
        # On the game's welcome screen the user-gesture audio replay control is invoked when visible.
        if page.locator('#voiceReplayBtn:visible').count():
            page.locator('#voiceReplayBtn').click(timeout=3500)
            page.wait_for_timeout(250)
            events=page.evaluate('window.__voiceEvents')
            assert any(x.startswith('data:audio/mpeg;base64,') for x in events),f'{label} no real MP3 triggered by replay'
        overflow=page.evaluate("Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)")
        assert overflow<=3,f'{label} horizontal overflow={overflow}px'
        page.screenshot(path=str(root/f'live-game-{label}.png'),full_page=True)
        print(f'PASS LIVE {label}: {count} real embedded MP3; no missing voice buttons; no JS error; overflow={overflow}px',flush=True)
        ctx.close()
    browser.close()
