#!/usr/bin/env python3
"""Wire every main panel to a deliberately authored exact spoken narration."""
from pathlib import Path
import json

root=Path(__file__).resolve().parent.parent
p=root/'index.html'
s=p.read_text(encoding='utf-8')
panels=json.loads((root/'scripts/panel_voice_content.json').read_text(encoding='utf-8'))
assert len(panels)==11
insert="""const PANEL_VOICE_SCRIPTS=__PANELMAP__;
function panelVoiceScript(title){
 const label=String(title||'').trim();
 return PANEL_VOICE_SCRIPTS[label] ||
        (label.startsWith('送给')&&label.endsWith('的礼物')?PANEL_VOICE_SCRIPTS['魔法礼物工坊']:null) ||
        null;
}
""".replace('__PANELMAP__',json.dumps(panels,ensure_ascii=False,separators=(',',':')))
anchor="S.audio.readCurrent=()=>{"
if "const PANEL_VOICE_SCRIPTS=" not in s:
    if s.count(anchor)!=1:raise RuntimeError("Unexpected runtime layout for main panel")
    s=s.replace(anchor,insert+anchor,1)
old="return speak(el('panelTitle').textContent+'。'+desc,{force:true,role:'narrator'});"
new="return speak(panelVoiceScript(el('panelTitle').textContent)||el('panelTitle').textContent+'。'+desc,{force:true,role:'narrator'});"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise RuntimeError("Main panel manual read route missing")
old="else{const intro=el('panelBody')?.querySelector('.section-desc,.wish-letter p,.card-note')?.textContent||kicker;speak(title+'。'+intro,{role:'narrator'})}"
new="else{const intro=el('panelBody')?.querySelector('.section-desc,.wish-letter p,.card-note')?.textContent||kicker;speak(panelVoiceScript(title)||title+'。'+intro,{role:'narrator'})}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise RuntimeError("Panel automatic narration route missing")
# A celebration has changing numbers, badges, and stickers. The main hero voice
# reliably reads an authored congratulation; no mechanical TTS is invoked.
old="speak(title+'。'+text,{role:'narrator'});return result"
new="speak(findVoiceClip(title+'。'+text,'narrator')?title+'。'+text:'丁一一，你真棒！我们又收集到闪闪的小星光啦！',{role:'narrator'});return result"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise RuntimeError("Celebration voice route missing")
old="if(allowed()&&/欢迎来到|点一下小岛|小花还在|种子用光|还差一些|收获了|需要.*邮票|陪你冒险|和你一起|再看一眼|休息一下/.test(message))speak(message);"
new="if(allowed()&&/欢迎来到|点一下小岛|小花还在|种子用光|还差一些|收获了|需要.*邮票|陪你冒险|和你一起|再看一眼|休息一下/.test(message))speak(findVoiceClip(message)?message:'真棒！丁一一，今天又有新发现啦！');"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise RuntimeError("Toast voice route missing")
# The replay button in celebration scenes uses the same audible congratulations.
old="if(visible('celebration'))return speak(el('celebTitle').textContent+'。'+el('celebText').textContent,{force:true,role:'narrator'});"
new="if(visible('celebration')){const line=el('celebTitle').textContent+'。'+el('celebText').textContent;return speak(findVoiceClip(line,'narrator')?line:'丁一一，你真棒！我们又收集到闪闪的小星光啦！',{force:true,role:'bubble'});}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise RuntimeError("Celebration replay route missing")
if s.count('</html>')!=1 or len(s)<4_000_000:raise RuntimeError("Unexpected output page size")
p.write_text(s,encoding='utf-8')
print('Updated all main panel voice routes:',len(panels))
