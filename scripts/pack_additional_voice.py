#!/usr/bin/env python3
"""Append exact contextual speech MP3 clips to the game, preserving older audio."""
from pathlib import Path
import base64, json, re, subprocess, argparse, shutil
parser=argparse.ArgumentParser()
parser.add_argument('--manifest',default='voice-extra-plan.json')
args=parser.parse_args()

ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'index.html'
s=p.read_text(encoding='utf-8')
m=re.search(r'(window\.StarwhimVoicePack\s*=\s*)({.*?})(;\s*</script>)',s,re.S)
if not m:
    raise RuntimeError('Embedded voice pack missing')
pack=json.loads(m.group(2))
rows=json.loads((ROOT/args.manifest).read_text(encoding='utf-8'))['lines']
assert len(pack.get('audio',{}))>=79
missing=[]
added=0
for row in rows:
    filename=ROOT/'generated'/f"{row['id']}.mp3"
    if not filename.is_file() or filename.stat().st_size<1000:
        missing.append(row['id'])
        continue
    # Validate the actual MP3, even on runners without the ffprobe executable.
    if shutil.which('ffprobe'):
        result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                               '-of','default=noprint_wrappers=1:nokey=1',str(filename)],
                               check=True,capture_output=True,text=True)
        if float(result.stdout.strip())<=0:
            raise RuntimeError(f'Empty MP3 duration: {filename}')
    else:
        from mutagen.mp3 import MP3
        info=MP3(str(filename)).info
        if info.length<=0 or info.bitrate<=0:
            raise RuntimeError(f'Invalid MP3: {filename}')
    if row.get('key',row['text']) not in pack['audio']:
        pack['audio'][row.get('key',row['text'])]='data:audio/mpeg;base64,'+base64.b64encode(filename.read_bytes()).decode()
        added+=1
if missing:
    raise RuntimeError(f'Missing {len(missing)} of {len(rows)} supplemental clips: {missing[:10]}')
pack['available']=len(pack['audio'])
pack['supplemental']=len(rows)
new=s[:m.start(2)]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]
assert new.count('</html>')==1 and len(new)>len(s)
p.write_text(new,encoding='utf-8')
print(f'Additional voice clips {added}; total installed {pack["available"]}')
