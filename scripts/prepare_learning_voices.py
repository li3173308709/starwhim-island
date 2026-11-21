#!/usr/bin/env python3
"""Generate fixed voice manifest from the audited educational game module."""
from pathlib import Path
import json,re,hashlib
root=Path(__file__).resolve().parent.parent
src=(root/'scripts/learning_v22.js').read_text(encoding='utf-8')
def collection(name):
    m=re.search(r'\bconst '+name+r'=(\[.*?\]);',src,re.S)
    if not m:raise RuntimeError('Missing '+name)
    return json.loads(m.group(1))
hanzi=collection('HANZI'); words=collection('WORDS')
assert len(hanzi)==200 and len({x['char'] for x in hanzi})==200
assert len(words)==200 and len({x['en'] for x in words})==200
items=[]
for x in hanzi:
    spoken=f"{x['word']}。{x['word']}的{x['char']}。"
    items.append(dict(id='hz'+hashlib.sha256(x['char'].encode()).hexdigest()[:14],role='bubble',text=spoken,key='hanzi:'+x['char'],context='普通话识字，拼音仅用于屏幕显示 '+x['py']))
for x in words:
    w=x['en']
    items.append(dict(id='en'+hashlib.sha256(w.encode()).hexdigest()[:14],role='bubble',text=w,key='english:'+w,context='English word pronunciation '+x['cat']))
assert len(items)==400 and len({x['id'] for x in items})==400 and len({x['key'] for x in items})==400
(root/'voice-learning-v22-plan.json').write_text(json.dumps(dict(version=22,count=len(items),lines=items),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared',len(hanzi),'Mandarin characters,',len(words),'English words,',len(items),'independent recorded-girl audio clips')