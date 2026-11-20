#!/usr/bin/env python3
"""Fail final build if any declared voice line lacks its MP3 or runtime route."""
import base64
import json
import re
import subprocess
import tempfile
from pathlib import Path

root=Path(__file__).resolve().parent.parent
s=(root/'index.html').read_text(encoding='utf-8')
m=re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>',s,re.S)
if not m:
    raise SystemExit('No embedded voice resources found')
pack=json.loads(m.group(1))
clips=pack.get('audio',{})
manifests=['voice-plan.json','voice-extra-plan.json','voice-panel-plan.json']
for extra in ('voice-advanced-plan.json','voice-arcade-plan.json'):
    if (root/extra).is_file(): manifests.append(extra)
all_lines=[]
for file in manifests:
    rows=json.loads((root/file).read_text(encoding='utf-8'))['lines']
    all_lines.extend(rows)
    missing=[x['text'] for x in rows if x['text'] not in clips]
    if missing:
        raise SystemExit(f'{file}: {len(missing)} missing recordings, e.g. {missing[:4]}')
# The original reference sample can share a spoken-text key with a generated clip.
# Require every distinct planned line, not a fabricated extra dictionary entry.
unique_planned = {row['text'] for row in all_lines}
if len(clips) < len(unique_planned):
    raise SystemExit(f'Expected {len(unique_planned)} distinct planned lines; found {len(clips)}')
if len(clips)<190:
    raise SystemExit('Insufficient voices for all mandatory gameplay contexts')
for name in ('findVoiceClip(', 'const PANEL_VOICE_SCRIPTS=', 'panelVoiceScript('):
    if name not in s:
        raise SystemExit('Playback route missing: '+name)
if '📖 待配音' in s:
    raise SystemExit('Unresolved inactive dubbing placeholders remain')
for label in ('泡泡','星光故事书','奇妙小游戏','魔法世界地图'):
    if label not in s:
        raise SystemExit('Essential game UI content missing: '+label)

# All final inputs are actual MP3 containers, not fabricated URLs or titles.
bad=[]
total_bytes=0
for label,uri in clips.items():
    if not isinstance(uri,str) or not uri.startswith('data:audio/mpeg;base64,'):
        bad.append(label)
        continue
    try:
        raw=base64.b64decode(uri.partition(',')[2],validate=True)
    except Exception:
        bad.append(label)
        continue
    if len(raw)<1000 or not (raw[:3]==b'ID3' or raw[0]==255):
        bad.append(label)
    total_bytes+=len(raw)
if bad:
    raise SystemExit(f'Undecodable or missing audio: {bad[:5]}')
with tempfile.TemporaryDirectory() as d:
    for i,part in enumerate(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S)):
        if not part.strip() or part.lstrip().startswith('window.StarwhimVoicePack'):
            continue
        f=Path(d)/f'inline-{i}.js'
        f.write_text(part,encoding='utf-8')
        subprocess.run(['node','--check',str(f)],check=True,capture_output=True)

print(f'PASS: {len(all_lines)} mandatory recordings, {len(clips)} MP3 entries, '
      f'{total_bytes/1048576:.1f} MiB audio; eleven narrated panels; JS syntax valid')
