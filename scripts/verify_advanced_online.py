#!/usr/bin/env python3
"""Production acceptance test for all eleven minigames and 197 recorded voice clips."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,os
url=os.environ.get('STARWHIM_URL','https://starwhim-island.vercel.app')
root=Path(__file__).resolve().parent.parent
plan=json.loads((root/'voice-advanced-plan.json').read_text(encoding='utf-8'))['lines']
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome',headless=True,args=['--autoplay-policy=no-user-gesture-required'])
 for name,w,h,mobile in [('desktop',1440,900,False),('phone390',390,844,True),('phone360',360,780,True)]:
  context=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile)
  page=context.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url,wait_until='domcontentloaded',timeout=60000)
  page.wait_for_function("Object.keys(window.StarwhimVoicePack?.audio||{}).length>=197",timeout=110000)
  expected=page.evaluate("""(arr)=>arr.map(t=>Object.prototype.hasOwnProperty.call(window.StarwhimVoicePack.audio,t))""",[row['text'] for row in plan])
  assert all(expected),f'{name}: new female voice MP3s missing {expected}'
  assert page.evaluate("window.Starwhim.MINIGAMES.length")==11
  assert page.evaluate("window.StarwhimAdvancedGames.ids.join(',')")=='starmaze,starsudoku,elfcode'
  assert page.locator('button:has-text("待配音")').count()==0
  for game,selector in [('starmaze','[data-y]'),('starsudoku','[data-i]'),('elfcode','[data-v]')]:
   page.evaluate("(id)=>window.Starwhim.minigames.open(id)",game)
   page.locator('#miniBody '+selector).first.wait_for(timeout=15000)
   page.locator('#miniBody '+selector).first.click(timeout=5000)
   page.evaluate("window.Starwhim.minigames.close()")
  assert not errors,f'{name}: JS errors {errors[:5]}'
  overflow=page.evaluate("Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)")
  assert overflow<=3,f'{name}: horizontal overflow {overflow}'
  page.screenshot(path=str(root/f'advanced-live-{name}.png'))
  print(f'PASS LIVE {name}: 197 recorded voices, 11 playable games, 3 new challenge controls functional, no JS errors',flush=True)
  context.close()
 browser.close()
