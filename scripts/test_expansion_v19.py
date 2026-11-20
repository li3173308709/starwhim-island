#!/usr/bin/env python3
"""Desktop and touch-viewport smoke tests for five new games.

Requires Chrome channel and Playwright. The script tests actual clicks, DOM,
new registry count, 200 distinct characters, 80 English words and JS errors.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel='chrome',headless=True,args=['--autoplay-policy=no-user-gesture-required'])
    for name,w,h,mobile in [('desktop',1440,900,False),('phone390',390,844,True),('phone360',360,780,True)]:
        ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile)
        page=ctx.new_page()
        errors=[]
        page.on('pageerror',lambda exc: errors.append(str(exc)))
        page.goto((ROOT/'index.html').as_uri(),wait_until='load',timeout=60000)
        page.wait_for_function('window.Starwhim?.minigames && window.StarwhimExpansion19',timeout=15000)
        info=page.evaluate('''() => ({
            count: Starwhim.MINIGAMES.length,
            hanzi: StarwhimExpansion19.hanziCount,
            english: StarwhimExpansion19.englishCount,
            oldVoices: Object.keys(window.StarwhimVoicePack.audio).length,
            ids: StarwhimExpansion19.games
        })''')
        assert info['count']>=19 and info['hanzi']==200 and info['english']==80, (name,info)
        assert info['oldVoices']>=200, (name,info)
        for game in info['ids']:
            page.evaluate('(id) => Starwhim.minigames.open(id)',game)
            page.wait_for_timeout(300)
            assert page.locator('#miniBody .v19').count()==1, (name,game,'missing main UI')
            if game=='bubblebreaker':
                page.locator('#v19-ball').click(position={'x':200,'y':130})
                page.locator('[data-act=pause]').click()
                page.locator('[data-act=pause]').click()
            elif game=='moontracks':
                page.locator('[data-tile]').first.click()
                page.locator('[data-act=test]').click()
            elif game=='cloudrunner':
                page.locator('[data-act=jump]').click()
                page.locator('[data-act=pause]').click()
                page.locator('[data-act=pause]').click()
            elif game=='hanzi200':
                page.locator('[data-act=learn]').click()
                assert page.locator('.v19 .glyph').inner_text()!=''
                page.locator('[data-act=mark]').click()
                page.locator('[data-act=home]').click()
                page.locator('[data-act=pinyin]').click()
                page.locator('[data-choice]').first.click()
            elif game=='englishquest':
                page.locator('[data-act=picture]').click()
                page.locator('[data-en]').first.click()
                page.evaluate("Starwhim.minigames.open('englishquest')")
                page.locator('[data-act=spell]').click()
                page.locator('[data-letter]').first.click()
                page.evaluate("Starwhim.minigames.open('englishquest')")
                page.locator('[data-act=memory]').click()
                page.locator('[data-card]').first.click()
                page.locator('[data-card]').nth(1).click()
            assert not errors, (name,game,errors[:4])
            page.screenshot(path=str(ROOT/f'newgames-{name}-{game}.png'),full_page=False)
            page.evaluate('Starwhim.minigames.close()')
        overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
        assert overflow<=3,(name,overflow)
        print('PASS',name,info,'no JS errors',flush=True)
        ctx.close()
    browser.close()
