#!/usr/bin/env python3
"""Chrome smoke testing three new playable arcade games at desktop/phone sizes."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
url=(ROOT/"index.html").as_uri()
with sync_playwright() as pw:
 browser=pw.chromium.launch(channel="chrome",headless=True,args=["--autoplay-policy=no-user-gesture-required"])
 for name,w,h,mobile in [("desktop",1440,900,False),("mobile390",390,844,True),("mobile360",360,780,True)]:
  context=browser.new_context(viewport={"width":w,"height":h},is_mobile=mobile,has_touch=mobile)
  page=context.new_page()
  errors=[]
  page.on("pageerror",lambda e:errors.append(str(e)))
  page.goto(url,wait_until="domcontentloaded",timeout=60000)
  page.wait_for_function("window.StarwhimArcade?.ids?.length===3",timeout=30000)
  assert page.evaluate("window.Starwhim.MINIGAMES.length")==14
  for game in ("rainbowdash","starmerge","spriteguard"):
   page.evaluate("(id)=>window.Starwhim.minigames.open(id)",game)
   page.wait_for_timeout(200)
   assert page.locator("#miniBackdrop:not(.hidden)").count()==1
   assert page.locator("#miniBody .arcade-wrap").count()==1
   if game=="rainbowdash":
    assert page.locator("#dashBoard .dash-cell").count()==15
    page.locator("#dashLeft").click()
    page.locator("#dashRight").click()
    page.wait_for_timeout(800)
   if game=="starmerge":
    assert page.locator(".arcade-merge .merge-tile").count()==16
    for move in ("mLeft","mUp","mRight","mDown"):
     if page.locator("#"+move).count():page.locator("#"+move).click()
    assert "移动" in page.locator("#miniBody").inner_text()
   if game=="spriteguard":
    assert page.locator(".arcade-tower .tower-cell, .arcade-tower button").count()==21
    page.locator("[data-lane='0']").click()
    page.locator("[data-lane='1']").click()
    page.wait_for_timeout(1100)
    assert page.locator(".arcade-tower button").count()==3
   assert not errors,(name,game,errors)
   assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=3
   page.screenshot(path=str(ROOT/("arcade-"+name+"-"+game+".png")),full_page=True)
   print("PASS",name,game,flush=True)
   page.evaluate("window.Starwhim.minigames.close()")
  context.close()
 browser.close()
