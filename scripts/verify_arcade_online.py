#!/usr/bin/env python3
"""Validate live Vercel game has 14 playable minigames and 200 real girl MP3 clips."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,os
root=Path(__file__).resolve().parent.parent
url=os.getenv("STARWHIM_URL","https://starwhim-island.vercel.app")
plan=json.loads((root/"voice-arcade-plan.json").read_text(encoding="utf-8"))["lines"]
with sync_playwright() as pw:
 browser=pw.chromium.launch(channel="chrome",headless=True,args=["--autoplay-policy=no-user-gesture-required"])
 for name,w,h,mobile in [("desktop",1440,900,False),("phone390",390,844,True),("phone360",360,780,True)]:
  context=browser.new_context(viewport={"width":w,"height":h},is_mobile=mobile,has_touch=mobile)
  page=context.new_page()
  errors=[]
  page.on("pageerror",lambda e:errors.append(str(e)))
  page.goto(url,wait_until="domcontentloaded",timeout=60000)
  page.wait_for_function("Object.keys(window.StarwhimVoicePack?.audio||{}).length>=200 && window.StarwhimArcade?.ids.length===3",timeout=110000)
  count=page.evaluate("Object.keys(window.StarwhimVoicePack.audio).length")
  assert count==200,("unexpected voice pack",count)
  assert page.evaluate("window.Starwhim.MINIGAMES.length")==14
  expected=page.evaluate("(texts)=>texts.map(x=>Object.hasOwn(window.StarwhimVoicePack.audio,x))",[x["text"] for x in plan])
  assert all(expected),f"{name}: voice missing {expected}"
  assert page.locator("button:has-text('待配音')").count()==0
  for game,selector in [("rainbowdash","#dashLeft"),("starmerge","#mLeft"),("spriteguard","[data-lane='0']")]:
   page.evaluate("(id)=>window.Starwhim.minigames.open(id)",game)
   page.locator("#miniBody "+selector).first.wait_for(timeout=15000)
   page.locator("#miniBody "+selector).first.click(timeout=5000)
   page.wait_for_timeout(150)
   page.evaluate("window.Starwhim.minigames.close()")
  # This verifies actual Chrome media decoding, not merely data URLs.
  playback=page.evaluate("""async () => {
   const src=Object.values(window.StarwhimVoicePack.audio)[0];
   const player=new Audio(src);
   await player.play();
   await new Promise(r=>setTimeout(r,500));
   const time=player.currentTime,duration=player.duration;
   player.pause();return {time,duration};
  }""")
  assert playback["time"]>.1 and playback["duration"]>1,playback
  assert not errors,f"{name} JS exceptions: {errors[:4]}"
  width_overflow=page.evaluate("Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)")
  assert width_overflow<=3,f"{name} horizontal scroll {width_overflow}"
  page.screenshot(path=str(root/("arcade-live-"+name+".png")),full_page=True)
  print(f"PASS LIVE {name}: 14 games / 200 MP3; 3 new modes; audio playing {playback['time']:.2f}s; no runtime errors; overflow {width_overflow}px",flush=True)
  context.close()
 browser.close()
