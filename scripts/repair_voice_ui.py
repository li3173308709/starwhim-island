#!/usr/bin/env python3
"""Repair game voice routing and disabled controls without touching embedded MP3 bytes."""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parent.parent
target = root / "index.html"
s = target.read_text(encoding="utf-8")
before = s

# Keep the original MP3 payload unchanged. The pack is embedded as a JSON object.
m = re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>', s, re.S)
if not m:
    raise SystemExit("Voice pack not found: refuse unsafe edit")
pack = json.loads(m.group(1))
if len(pack.get("audio", {})) < 79:
    raise SystemExit("Audio pack unexpectedly incomplete; refuse unsafe edit")

lookup = """function findVoiceClip(words,role='bubble'){
 const audio=voicePack.audio||{};
 if(audio[words])return audio[words];
 if(audio[role+'\\n'+words])return audio[role+'\\n'+words];
 const normalize=x=>String(x||'').normalize('NFKC').replace(/[\\s\\u200b-\\u200d\\ufeff]/g,'').replace(/[，,。.!！?？：:；;、“”‘’\\"'（）()—–…·]/g,'');
 const key=normalize(words);
 if(!key)return null;
 // Normalization only: never play a different dialogue just to hide an absent MP3.
 for(const [text,path] of Object.entries(audio)){
  if(normalize(text)===key || normalize(text.replace(/^(bubble|narrator)\\n/,''))===key)return path;
 }
 return null;
}
"""
anchor="function speak(phrase,{force=false,speaker='',role=''}={}){"
if "function findVoiceClip(" not in s:
    assert s.count(anchor)==1, "speech function not unique"
    s=s.replace(anchor,lookup+anchor,1)
old="const recordedPath=voicePack.audio?.[words] || voicePack.audio?.[selectedRole+'\\n'+words];"
new="const recordedPath=findVoiceClip(words,selectedRole);"
assert old in s or new in s, "voice lookup changed unexpectedly"
s=s.replace(old,new,1)
# Remove baked-in disabled placeholders for both panel and mini-game voice controls.
old="btn.textContent='📖 待配音';btn.disabled=true;btn.title='这部分尚未生成相同音色的录音';"
new="btn.textContent='🔊 听本页';btn.disabled=false;btn.title='播放已收录的女孩配音；缺失台词会明确提示';"
assert old in s or new in s, "panel button pattern missing"
s=s.replace(old,new,1)
old="const available=!!voicePack.audio?.[toText(words)];"
new="const available=!!findVoiceClip(toText(words),voiceRole(name));"
assert old in s or new in s, "dialogue availability check missing"
s=s.replace(old,new,1)
s=s.replace("btn.textContent=available?'🔊 再听':'📖 待配音';","btn.textContent=available?'🔊 再听':'📖 暂无录音';",1)
# narrator test uses the same embedded girl's voice pack, never device speechSynthesis.
s=s.replace("el('narratorTestButton').textContent='📖 旁白音频待补充';el('narratorTestButton').disabled=true;",
"""el('narratorTestButton').textContent='🔊 试听女孩旁白';el('narratorTestButton').disabled=false;
    el('narratorTestButton').onclick=()=>{resumeAudio();speak(NARRATOR_TEST,{force:true,role:'narrator'})};""",1)
# Remove misleading claims that a missing recording will use a system voice.
s=s.replace("已安装 '+voicePack.available+' 句 MP3，未命中时暂用设备朗读。", "已安装 '+voicePack.available+' 句女孩音频，缺失录音会明确提示。")
s=s.replace("尚未导入语界 MP3；试听暂用设备朗读，声音与选定音色不同。", "尚未安装录音；不会使用系统机械朗读替代。")
s=s.replace("btn.setAttribute('aria-label','此页正式配音待补充');", "btn.setAttribute('aria-label','播放本页已安装的女孩配音');")
# Existing status is stale after AI clip pack; show actual verified installed count.
s=s.replace("'已安装 '+voicePack.available+'/'+voicePack.planned+' 句真实「活泼女孩 2.0」配音：欢迎语可播放。其他台词需按相同音色合成后导入；不会播放机械音。'",
"""'已安装 '+Object.keys(voicePack.audio||{}).length+' 段女孩声音；未收录的台词会提示缺失，绝不切换为系统机械朗读。'""",1)
assert s.count("</html>")==1
assert len(s)>4_000_000 and len(before)>4_000_000, "Unexpected game truncation"
target.write_text(s,encoding="utf-8")
print("Voice repair:", "updated" if s!=before else "already applied")
print("Voice audio entries:",len(pack["audio"]))
print("Remaining disabled placeholder phrases:",s.count("📖 待配音"))
