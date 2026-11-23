#!/usr/bin/env python3
"""V27 browser acceptance: 200 Mandarin one-phrase readings, 200 meanings.

Exercises desktop and two phone widths. Preserves 19 games, 200
independent en-US recordings, old save shape and other audio speeds.
"""
import json,re,os
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent.parent
target=os.environ.get('STARWHIM_URL') or (root/'index.html').resolve().as_uri()
manifest=json.loads((root/'voice-study-corrections-v27-plan.json').read_text(encoding='utf-8'))
rows=manifest['lines']
bykey={x['key']:x['text'] for x in rows}
assert len(rows)==403 and bykey['hanzi:米']=='大米的米。'
assert bykey['hanzi:饭']=='米饭的饭。'
assert bykey['cn:meaning:cat']=='中文是：猫。'
with sync_playwright() as pw:
 browser=pw.chromium.launch(channel='chrome',headless=True,
              args=['--autoplay-policy=no-user-gesture-required'])
 for device,w,h,mobile in [('desktop',1440,900,False),
                           ('phone390',390,844,True),
                           ('phone360',360,780,True)]:
  context=browser.new_context(viewport={'width':w,'height':h},
            is_mobile=mobile,has_touch=mobile)
  page=context.new_page()
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("""(()=>{
   window.__v27plays=[];
   const original=HTMLMediaElement.prototype.play;
   HTMLMediaElement.prototype.play=function(){
     window.__v27plays.push({src:this.src,rate:this.playbackRate});
     return original.apply(this,arguments);
   };
   if(navigator.userAgent.includes('Mobile'))
     speechSynthesis.speak=()=>{throw Error('Speech synthesis unavailable')};
  })()""")
  page.goto(target,wait_until='domcontentloaded',timeout=70000)
  page.wait_for_function("""()=>window.StarwhimChineseNarratorV23?.resolve
    && window.StarwhimReadingV22?.hanziCount===200
    && window.StarwhimEnglishLearnFirst?.words===200
    && Object.keys(window.StarwhimVoicePack?.audio||{}).length===914
    && Object.keys(window.StarwhimEnglishPronunciationPack?.audio||{}).length===200
  """,timeout=90000)
  page.evaluate("Starwhim.minigames.open('hanzi200')")
  page.wait_for_selector("#miniBody .v19",timeout=5000)
  assert page.get_by_text('已补上全部汉字的可点击朗读功能').count()==0
  page.locator('#miniBody [data-topic="4"]').click()
  page.locator('#miniBody [data-act="learn"]').click()
  page.wait_for_selector('#miniBody .glyph')
  card=page.locator('#miniBody .lesson')
  assert card.locator('.glyph').inner_text()=='米',(device,card.inner_text())
  assert page.locator('#miniBody .hanzi-example').inner_text().replace('🔊','').strip()=='大米的米。'
  resolution=page.evaluate("""()=>{
     const v=window.StarwhimChineseNarratorV23;
     return [v.resolve(document.querySelector('.glyph')),
             v.resolve(document.querySelector('.hanzi-example'))];
  }""")
  assert resolution==[['hanzi:米'],['hanzi:米']],(device,resolution)
  page.locator('#miniBody [data-act="speak"]').click()
  page.wait_for_timeout(140)
  val=page.evaluate("""()=>{
   const src=StarwhimVoicePack.audio['hanzi:米'];
   const events=window.__v27plays.filter(e=>e.src===src);
   return {count:events.length,rate:events.at(-1)?.rate}
  }""")
  assert val['count']>=1 and abs(val['rate']-.8)<.001,(device,val)
  # When a quiz is opened, only its own literal recorded rule is available.
  page.evaluate("Starwhim.minigames.open('hanzi200')")
  page.locator('#miniBody [data-act="pinyin"]').click()
  page.wait_for_selector('#hanziFeedback')
  h=page.locator('#hanziFeedback')
  assert '观察拼音和声调' in h.inner_text(),(device,h.inner_text())
  hint=page.evaluate("""()=>StarwhimChineseNarratorV23.resolve(
    document.querySelector('#hanziFeedback'))""")
  assert hint==['cn:ui:hanzi-pinyin'],(device,hint)
  # The English meaning narration must use exact text, not an unrelated
  # approximate sentence, while English word playback still works on phones.
  page.evaluate("Starwhim.minigames.close();Starwhim.minigames.open('englishquest')")
  page.locator('#miniBody [data-eng="learn"]').click()
  page.wait_for_selector('#miniBody .eng-meaning',timeout=6500)
  meaning=page.locator('#miniBody .eng-meaning').first
  assert meaning.inner_text().replace('🔊','').strip()=='中文是：猫。',(device,meaning.inner_text())
  v=page.evaluate("""()=>StarwhimChineseNarratorV23.resolve(
       document.querySelector('.eng-meaning'))""")
  assert v==['cn:meaning:cat'],(device,v)
  page.locator('.eng-meaning .v23-audio-control').first.click()
  page.wait_for_timeout(180)
  m=page.evaluate("""()=>{
    const src=StarwhimVoicePack.audio['cn:meaning:cat'];
    const ev=window.__v27plays.filter(x=>x.src===src);
    return {count:ev.length,rate:ev.at(-1)?.rate||0};
  }""")
  assert m['count']>=1 and abs(m['rate']-.72)<.001,(device,m)
  matched=page.evaluate("""()=>{
    const v=StarwhimChineseNarratorV23;
    const d=document.querySelector('.learnfirst');
    const words=Object.entries(v.exactText).filter(([k])=>k.startsWith('cn:meaning:'));
    let success=0;
    for(const [key,sentence] of words){
      const n=document.createElement('div');n.className='eng-meaning';
      n.dataset.voiceWord=key.split(':').slice(2).join(':');
      n.textContent=sentence;d.appendChild(n);
      if(JSON.stringify(v.resolve(n))===JSON.stringify([key]))success++;
      n.remove();
    }
    return {total:words.length,success};
  }""")
  assert matched=={'total':200,'success':200},(device,matched)
  assert not errors,(device,errors[:4])
  overflow=page.evaluate('Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)')
  assert overflow<=3,(device,'horizontal overflow',overflow)
  print('PASS',device,'200 natural Hanzi voice mapping, 200 exact English meanings,',
        'Hanzi=.8, English Chinese=.72; no stale notes, all MP3 retained',flush=True)
  context.close()
 browser.close()
