#!/usr/bin/env python3
"""Exercise all 3 new challenges through first win with real browser buttons."""
from pathlib import Path
from playwright.sync_api import sync_playwright
page_url=(Path(__file__).resolve().parent.parent/'index.html').as_uri()
with sync_playwright() as pw:
 browser=pw.chromium.launch(channel='chrome',headless=True,args=['--autoplay-policy=no-user-gesture-required'])
 for name,w,h,mobile in [('desktop',1280,850,False),('phone390',390,844,True),('phone360',360,780,True)]:
  ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile)
  page=ctx.new_page();errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
  page.goto(page_url,wait_until='load')
  ids=page.evaluate("window.StarwhimAdvancedGames?.ids")
  assert ids==['starmaze','starsudoku','elfcode'], ids
  assert len(page.evaluate("Starwhim.MINIGAMES"))==11
  for game in ids:
   page.evaluate("(id)=>Starwhim.minigames.open(id)",game)
   assert not page.locator('#miniBackdrop').get_attribute('class').endswith('hidden')
   if game=='starmaze':
    # Click board in a shortest path from spawn to key.
    for target in ('K','E'):
     coords=page.evaluate("""(target) => {
       const d=Starwhim.minigames.data,b=d.b,Q=[[...d.player]],seen=new Set([d.player.join(',')]);
       let parent={};
       for(let k=0;k<Q.length;k++){
         const [r,c]=Q[k],key=r+','+c;
         if(b[r][c]===target){
           let out=[],cur=key;
           while(cur!==d.player.join(',')){out.push(cur.split(',').map(Number));cur=parent[cur]}
           return out.reverse()
         }
         for(const [dr,dc] of [[1,0],[-1,0],[0,1],[0,-1]]){
           const y=r+dr,x=c+dc,n=y+','+x;
           if(b[y]&&b[y][x]&&b[y][x]!=='#'&&!seen.has(n)){
             seen.add(n);parent[n]=key;Q.push([y,x])
           }
         }
       }return null
     }""",target)
     assert coords,('unreachable maze',name)
     for r,c in coords:page.locator(f'[data-y="{r}"][data-x="{c}"]').click()
    page.wait_for_timeout(700)
    assert '第 2/3 关' in page.locator('#miniBody').inner_text(), 'maze did not advance'
   if game=='starsudoku':
    d=page.evaluate("({answer:Starwhim.minigames.data.answer,locked:Starwhim.minigames.data.locked})")
    for i,(v,locked) in enumerate(zip(d['answer'],d['locked'])):
     if not locked:
      page.locator(f'[data-i="{i}"]').click()
      page.locator(f'[data-n="{v}"]').click()
    page.locator('#sudokuDone').click()
    page.wait_for_timeout(700)
    assert '第 2/3 关' in page.locator('#miniBody').inner_text(), 'sudoku did not advance'
   if game=='elfcode':
    secret=page.evaluate("Starwhim.minigames.data.secret")
    for v in secret:page.locator(f'[data-v="{v}"]').click()
    page.locator('#codeVerify').click()
    page.wait_for_timeout(700)
    assert '第 2/3 关' in page.locator('#miniBody').inner_text(), 'code did not advance'
   page.evaluate('Starwhim.minigames.close()')
  assert not errors, (name,errors)
  x=page.evaluate("Math.max(0,document.documentElement.scrollWidth-innerWidth)")
  assert x<=3,(name,'horizontal overflow',x)
  print(f'PASS {name}: all three games start, accept touch/click, complete stage 1 and advance, no JS errors')
  ctx.close()
 browser.close()
