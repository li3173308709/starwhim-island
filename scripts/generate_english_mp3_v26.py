#!/usr/bin/env python3
"""Generate one natural English-only recording per word (200 words).

This voice is intentionally English en-US, NOT the Chinese girl's F5 voice.
Requires network on GitHub Actions and edge-tts. Does not change existing game.
"""
import asyncio, json, re, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
JS=(ROOT/'scripts/learning_v22.js').read_text(encoding='utf-8')
WORDS=json.loads(re.search(r'const WORDS=(\[.*?\]);',JS,re.S).group(1))
assert len(WORDS)==200 and len({w['en'] for w in WORDS})==200
OUT=ROOT/'generated-english-v26'
OUT.mkdir(exist_ok=True)
VOICE='en-US-JennyNeural'
async def main():
 import edge_tts
 sem=asyncio.Semaphore(3)
 async def one(i,w):
  name=f"{i:03d}.mp3"
  file=OUT/name
  if file.exists() and file.stat().st_size>1000:return
  async with sem:
   last_error=None
   for retry in range(6):
    try:
     wav=OUT/(name+'.tmp')
     await asyncio.wait_for(
       edge_tts.Communicate(text=w['en'],voice=VOICE,rate='-8%').save(str(wav)),
       timeout=60
     )
     if wav.stat().st_size<1000:raise RuntimeError('Audio too small')
     # Normalize and gently fade in to prevent click artifacts.
     cp=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-loglevel','error',
       '-y','-i',str(wav),'-af','silenceremove=start_periods=1:start_silence=0.04:start_threshold=-42dB:detection=rms,afade=t=in:st=0:d=0.035',
       '-ar','24000','-ac','1','-codec:a','libmp3lame','-b:a','48k',
       str(file)],capture_output=True,text=True)
     if cp.returncode:raise RuntimeError(cp.stderr[-450:])
     if file.stat().st_size<900:raise RuntimeError('Normalized audio too small')
     wav.unlink(missing_ok=True)
     print(f'English {i+1:03d}/200 {w["en"]} {file.stat().st_size} bytes',flush=True)
     return
    except Exception as e:
     last_error=e
     file.unlink(missing_ok=True)
     (OUT/(name+'.tmp')).unlink(missing_ok=True)
     print(f'RETRY {retry+1}/6 {w["en"]}: {str(e)[:120]}',flush=True)
     await asyncio.sleep(min(12,2+retry*2))
   raise RuntimeError(f'Failed to synthesize {w["en"]}: {last_error}')
 await asyncio.gather(*[one(i,w) for i,w in enumerate(WORDS)])
 report={'voice':VOICE,'language':'en-US','words':[w['en'] for w in WORDS],
        'files':[f'{i:03d}.mp3' for i in range(len(WORDS))]}
 (OUT/'manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print('PASS 200 separate natural English MP3s, Mandarin girl voice untouched')
if __name__=='__main__':
 asyncio.run(main())
