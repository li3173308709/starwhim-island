#!/usr/bin/env python3
"""Prepare exact new game narration lines for matching F5-TTS female voice."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
lines={
 'starmaze':'星光迷宫探险。丁一一，先找到金钥匙，再带着泡泡走向彩虹门。每一关的路线都会更复杂，仔细想一想再出发！',
 'starsudoku':'魔法数独学院。每一行、每一列和每一个小方格，都需要不同的魔法图案。先观察，再推理，你一定能找到答案！',
 'elfcode':'精灵密码实验室。猜一猜隐藏的精灵密码。粉色爱心代表位置和图案都正确，黄色爱心代表只有图案正确。根据线索不断缩小范围吧！'
}
js=(root/'scripts/advanced_games.js').read_text(encoding='utf-8')
assert all(t in js for t in lines.values()),'New game narration text changed without changing synthesis plan'
items=[]
for key,text in lines.items():
 h=hashlib.sha256(text.encode()).hexdigest()[:16]
 items.append({'id':h,'role':'bubble','text':text,'context':key,
               'voice_name':'用户参考女孩 MP3 的 F5-TTS 相近声线',
               'provider':'F5-TTS','file':f'generated/{h}.mp3'})
(root/'voice-advanced-plan.json').write_text(json.dumps({'version':1,'count':len(items),'lines':items},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared original voice lines for new games:',len(items))
