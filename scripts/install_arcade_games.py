#!/usr/bin/env python3
"""Safely inject replayable arcade games after original 11 games and voice pack."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/"index.html"
game=p.read_text(encoding="utf-8")
arcade=(ROOT/"scripts/arcade_games.js").read_text(encoding="utf-8")
assert len(game)>10_000_000 and game.count("</body></html>")==1
assert "window.StarwhimAdvancedGames" in game
assert all(k in arcade for k in ("rainbowdashStart","starmergeStart","spriteguardStart"))
if "window.StarwhimArcade" not in game:
    game=game.replace("</body></html>","<script>\n"+arcade+"\n</script>\n</body></html>",1)
    p.write_text(game,encoding="utf-8")
print("Arcade integrated:",game.count("window.StarwhimArcade"),"size",len(game),
      "sha256",hashlib.sha256(p.read_bytes()).hexdigest())

voice=[
("rainbowdash","彩虹飞行大冒险。左右移动躲开乌云，接住星星。连续接中就会得到更多分数！"),
("starmerge","星星合成研究所。滑动魔法棋盘，把相同的星星合在一起。一路合成闪耀的一百二十八点星星！"),
("spriteguard","精灵花园守卫战。种下魔法花朵，守护三条小路。先照顾每一条路，再把花朵升级！")]
rows=[]
for key,text in voice:
    id=hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    assert text in arcade
    rows.append({"id":id,"role":"bubble","text":text,"context":key+"新游戏介绍",
                 "file":"generated/"+id+".mp3","voice_name":"女孩参考音色 F5-TTS"})
(ROOT/"voice-arcade-plan.json").write_text(json.dumps({"version":1,"count":len(rows),"lines":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Arcade voice sentences:",len(rows))
