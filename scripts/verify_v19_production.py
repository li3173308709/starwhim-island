#!/usr/bin/env python3
"""Verify deployed v1.9 game, its learning library, MP3 and touch UI in Chrome."""
import os
from playwright.sync_api import sync_playwright
TARGET=os.getenv('STARWHIM_URL','https://starwhim-island.vercel.app')
with sync_playwright() as pw:
    chrome=pw.chromium.launch(channel='chrome',headless=True,args=['--autoplay-policy=no-user-gesture-required'])
    for device,w,h,mobile in [('desktop',1440,900,False),('phone390',390,844,True),('phone360',360,780,True)]:
        context=chrome.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile)
        page=context.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(TARGET,wait_until='domcontentloaded',timeout=60000)
        page.wait_for_function('window.StarwhimExpansion19 && Object.keys(window.StarwhimVoicePack?.audio||{}).length>=205',timeout=110000)
        facts=page.evaluate('''() => ({
            games: Starwhim.MINIGAMES.length,
            added: StarwhimExpansion19.games,
            chinese: StarwhimExpansion19.hanziCount,
            english: StarwhimExpansion19.englishCount,
            voices: Object.keys(StarwhimVoicePack.audio).length
        })''')
        assert facts['games']>=19 and len(facts['added'])==5 and facts['chinese']==200 and facts['english']==80,facts
        assert facts['voices']>=205,facts
        for name in facts['added']:
            page.evaluate('(name)=>Starwhim.minigames.open(name)',name)
            page.wait_for_timeout(250)
            assert page.locator('#miniBody .v19').count()==1, (device,name)
            assert not errors, (device,name,errors)
            page.evaluate('Starwhim.minigames.close()')
        progress=page.evaluate('''async () => {
            const audio=new Audio(Object.values(StarwhimVoicePack.audio)[0]);
            await audio.play();
            await new Promise(done=>setTimeout(done,650));
            const t=audio.currentTime;
            audio.pause();
            return t;
        }''')
        assert progress>0.15,(device,progress)
        assert page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')<=3
        print('PASS ONLINE',device,facts,'MP3 progressed',round(progress,2),flush=True)
        context.close()
    chrome.close()
