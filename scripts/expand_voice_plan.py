#!/usr/bin/env python3
"""Build supplemental F5-TTS requests from actual game data.

This covers finite quest/zone combinations and the static dialogue and toast strings
that were not in the initial 79-clip plan. Re-running is deterministic.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
s = (ROOT / 'index.html').read_text(encoding='utf-8')
# Avoid examining the large base64 audio payload as game code.
s = re.sub(r'window\.StarwhimVoicePack\s*=\s*{.*?};\s*</script>', '', s, count=1, flags=re.S)
base = json.loads((ROOT / 'voice-plan.json').read_text(encoding='utf-8'))['lines']
known = {r['text'] for r in base}
out = {}

def add(t, context, role='bubble'):
    t = str(t).strip()
    if not t or t in known or t in out or len(t) > 230:
        return
    if not re.search('[\u4e00-\u9fff]', t):
        return
    digest = hashlib.sha256(t.encode('utf-8')).hexdigest()[:16]
    out[t] = {'id': digest, 'role': role, 'text': t, 'context': context,
              'voice_name': '参考MP3相近女孩音色', 'provider': 'F5-TTS',
              'file': 'generated/' + digest + '.mp3'}

def section(prefix, closing):
    m = re.search(re.escape(prefix) + r'(.*?)' + re.escape(closing), s, re.S)
    if not m:
        raise RuntimeError('Cannot find game data section ' + prefix)
    return m.group(1)

quests = re.findall(r"name:'((?:\\'|[^'])+)',hint:'((?:\\'|[^'])+)'",
                    section('S.QUESTS=[', '];'))
zones_raw = section('S.ZONES={', '};')
zones = re.findall(r"\b(?:plaza|garden|forest|valley|lake|academy):\{name:'([^']+)'", zones_raw)
if len(quests) < 10 or len(zones) != 6:
    raise RuntimeError(f'Incomplete story data quests={len(quests)}, zones={len(zones)}')

# Read-current builds its sentence from the zone and quest; include all combinations.
for z in ['星绒岛'] + zones:
    for name, hint in quests:
        add('丁一一小冒险家，你现在在'+z+'。接下来的小任务是：'+name+'。'+hint,
            '当前场景与任务', 'bubble')
    add('丁一一小冒险家，你现在在'+z+'。你可以随意探索，照顾精灵，或者挑一个喜欢的小游戏。',
        '当前场景自由探索', 'bubble')

# The quest panel and default completion states can show these text variations.
for t in ['你完成了星光旅程，现在可以自由探索啦！',
          '星光故事已经完成，尽情自由探索吧！',
          '丁一一，你真棒！我们又收集到闪闪的小星光啦！']:
    add(t, '任务/通关', 'bubble')

# Direct dialogue messages, dynamic event stories, and fixed sound triggers.
for t in re.findall(r"\b(?:S\.UI\.say|this\.say)\(\s*'[^']+'\s*,\s*'((?:\\'|[^'])+)'",s):
    add(t, '互动角色', 'narrator')
for t in re.findall(r"\bstory:'((?:\\'|[^'])+)'",section('S.EVENTS=[', '];')):
    add(t, '探索随机事件', 'narrator')
for t in re.findall(r"\b(?:S\.UI\.toast|this\.toast)\(\s*'((?:\\'|[^'])+)'",s):
    if re.search(r'欢迎来到|点一下小岛|小花还在|种子用光|还差一些|收获了|需要.*邮票|陪你冒险|和你一起|再看一眼|休息一下',t):
        add(t, '系统鼓励提示', 'bubble')

# Explicit narration / panel titles from game markup.
for t in re.findall(r"\b(?:this\.panel|S\.UI\.panel)\(\s*'((?:\\'|[^'])+)'", s):
    add(t, '功能面板标题', 'narrator')
for t in re.findall(r"\b(?:this\.celebrate|S\.UI\.celebrate)\(\s*'((?:\\'|[^'])+)'", s):
    add(t, '庆典标题', 'narrator')

# Source voice snippets may be inserted as a separate game-text lookup rather
# than falsely reporting a missing line as fully dubbed.
payload = {'version': 1, 'description': 'Supplemental exact game messages',
           'count': len(out), 'lines': list(out.values())}
(ROOT / 'voice-extra-plan.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Original clips: {len(known)}; supplemental clips: {len(out)}')
print(f'Quest/zone combinations: {len(quests)} x {len(zones)+1}')
