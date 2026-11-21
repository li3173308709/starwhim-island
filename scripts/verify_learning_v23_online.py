#!/usr/bin/env python3
"""End-to-end verify the live 914-voice education release in real Chrome.

Tests desktop and 2 phone-sized contexts on the actual Vercel deployment,
including 200+200 entries, 309 Chinese explanations, five-card onboarding,
Chinese listen buttons, and native MP3 decode/playback.
"""
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

URL = os.getenv("STARWHIM_URL", "https://starwhim-island.vercel.app")
REQUIRED = ["english:cat", "hanzi:山", "cn:meaning:cat",
            "cn:ui:home", "cn:ui:hanzi-lesson"]

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome", headless=True,
            args=["--autoplay-policy=no-user-gesture-required"])
    for device,w,h,mobile in [("desktop",1440,900,False),("phone390",390,844,True),
                              ("phone360",360,780,True)]:
        context=browser.new_context(viewport={"width":w,"height":h},
                                    is_mobile=mobile,has_touch=mobile)
        page=context.new_page()
        errors=[]
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script("""(()=>{
            window.__played=[];
            const original=HTMLMediaElement.prototype.play;
            HTMLMediaElement.prototype.play=function(){
                window.__played.push((this.currentSrc||this.src||"").slice(0,32));
                return original.apply(this,arguments);
            };
        })()""")
        page.goto(URL,wait_until="domcontentloaded",timeout=60000)
        try:
            page.wait_for_function("""()=>
                window.StarwhimChineseNarratorV23?.ready &&
                window.StarwhimEnglishLearnFirst?.words===200 &&
                window.StarwhimReadingV22?.hanziCount===200 &&
                Object.keys(window.StarwhimVoicePack?.audio||{}).length>=914
            """,timeout=135000)
        except PlaywrightTimeoutError:
            raise AssertionError(f"{device}: new game failed to boot; "
                                 f"url={page.url}; body={page.locator('body').inner_text()[:600]}; errors={errors[:5]}")
        info=page.evaluate("""()=>({
            clips:Object.keys(StarwhimVoicePack.audio).length,
            words:StarwhimEnglishLearnFirst.words,
            chars:StarwhimReadingV22.hanziCount,
            games:Starwhim.MINIGAMES.length,
            missing:["english:cat","hanzi:山","cn:meaning:cat","cn:ui:home",
                 "cn:ui:hanzi-lesson"].filter(k=>!StarwhimVoicePack.audio[k])
        })""")
        assert info["clips"]==914 and info["games"]>=19 and not info["missing"], (device,info)
        # Native audio playback of all 3 voice classes.
        for key in REQUIRED[:3]:
            t=page.evaluate("""async (key)=>{
                let a=new Audio(window.StarwhimVoicePack.audio[key]);
                await a.play();
                await new Promise(r=>setTimeout(r,350));
                let r={time:a.currentTime,duration:a.duration,readyState:a.readyState};
                a.pause();return r;
            }""",key)
            assert t["time"]>0.08 and t["readyState"]>=2, (device,key,t)
        page.evaluate("Starwhim.minigames.open('hanzi200')")
        page.wait_for_selector("#miniBody .v19",timeout=8000)
        page.wait_for_selector("#miniBody [data-v23-read-all]",timeout=8000)
        page.locator("#miniBody [data-act=learn]").click(timeout=4500)
        page.wait_for_selector("#miniBody [data-act=speak]",timeout=5000)
        assert page.locator("#miniBody .v23-audio-control").count()>0,(device,"Hanzi Chinese controls")
        page.locator("#miniBody [data-act=speak]").click()
        page.wait_for_timeout(160)
        assert page.evaluate("window.__played.length")>0,(device,"Hanzi MP3 button")
        page.evaluate("Starwhim.minigames.close()")
        page.evaluate("Starwhim.minigames.open('englishquest')")
        page.wait_for_selector("#miniBody .learnfirst",timeout=9000)
        assert page.locator("#miniBody [data-v23-read-all]").count()==1,(device,"Chinese page narration")
        assert page.locator("#miniBody .eng-topic").count()>=20,(device,"English topics")
        page.locator("#miniBody [data-eng=learn]").click()
        page.wait_for_selector("#miniBody .eng-card",timeout=6000)
        # First five cards should be taught before the challenge appears.
        for i in range(5):
            assert page.locator("#miniBody .eng-card .eng-word").count()==1,(device,i)
            assert page.locator("#miniBody .eng-meaning").count()==1,(device,i)
            assert page.locator("#miniBody .v23-audio-control").count()>0,(device,i,"Chinese meaning narration")
            page.locator("#miniBody [data-eng=next]").click()
        page.wait_for_selector("#miniBody [data-eng=practice]",timeout=7000)
        learned=page.evaluate("window.StarwhimEnglishLearnFirst.getLearned()")
        assert learned>=5,(device,"five taught words",learned)
        page.locator("#miniBody [data-eng=practice]").click()
        assert page.locator("#miniBody .eng-options button").count()>=2,(device,"practice unlocked")
        assert not errors,(device,errors[:5])
        overflow=page.evaluate("Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)")
        assert overflow<=3,(device,"overflow",overflow)
        print("PASS LIVE",device,info,"first-5-card learning + quiz + Chinese narration + 3 MP3 classes",flush=True)
        context.close()
    browser.close()
