#!/usr/bin/env python3
"""Validate and inject synthesized clips into the standalone game HTML."""
import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / 'index.html'
SOURCE = INDEX.read_text(encoding='utf-8')
PLAN = json.loads((ROOT / 'voice-plan.json').read_text(encoding='utf-8'))['lines']
match = re.search(r'(window\.StarwhimVoicePack\s*=\s*)({.*?})(;\s*</script>)', SOURCE, re.S)
if not match:
    raise SystemExit('Cannot locate standalone voice pack')
pack = json.loads(match.group(2))
original = pack['audio']
if not any('data:audio/mpeg;base64,' in v for v in original.values()):
    raise SystemExit('Refusing to replace missing original audio')
clips = {}
for row in PLAN:
    f = ROOT / 'generated' / (row['id'] + '.mp3')
    if not f.is_file() or f.stat().st_size < 500:
        raise SystemExit(f'Missing synthesized voice clip: {f}')
    clips[row['text']] = 'data:audio/mpeg;base64,' + base64.b64encode(f.read_bytes()).decode('ascii')
if len(clips) != len(PLAN):
    raise SystemExit(f'Duplicate voice texts in plan, found {len(clips)} of {len(PLAN)}')
pack['audio'] = {**original, **clips}
pack['available'] = len(pack['audio'])
pack['planned'] = len(PLAN)
pack['provider'] = 'F5-TTS noncommercial AI clone from user supplied sample'
pack['voiceName'] = '活泼女孩参考音色 · AI相近声线（非语界官方合成）'
text = SOURCE[:match.start(2)] + json.dumps(pack, ensure_ascii=False, separators=(',', ':')) + SOURCE[match.end(2):]
text = text.replace('欢迎语可播放。其他台词需按相同音色合成后导入；不会播放机械音。', '优先任务语音已经制作；不会调用机械朗读。')
if text.count('</html>') != 1 or '送给丁一一小朋友' not in text:
    raise SystemExit('Corrupted HTML during voice packaging')
INDEX.write_text(text, encoding='utf-8')
print(f'Packed {len(clips)} generated clips, {len(pack["audio"])} recordings total, HTML bytes={INDEX.stat().st_size}')