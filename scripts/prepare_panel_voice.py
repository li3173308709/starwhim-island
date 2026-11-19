#!/usr/bin/env python3
"""Create eleven exact panel audio requests using the reference-voice synthesis."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent.parent
panels=json.loads((root/'scripts/panel_voice_content.json').read_text(encoding='utf-8'))
assert len(panels)==11 and len(set(panels.values()))==11
lines=[]
for title,sentence in panels.items():
    h=hashlib.sha256(sentence.encode('utf-8')).hexdigest()[:16]
    lines.append({'id':h,'text':sentence,'context':'功能面板：'+title,'role':'narrator',
                  'voice_name':'参考MP3相近女孩音色','provider':'F5-TTS',
                  'file':'generated/'+h+'.mp3'})
(root/'voice-panel-plan.json').write_text(json.dumps({'version':1,'count':len(lines),'lines':lines},
                                                      ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared panel voice clips:',len(lines))
