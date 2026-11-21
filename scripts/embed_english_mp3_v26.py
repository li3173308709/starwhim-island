#!/usr/bin/env python3
"""Embed 200 independent English-language MP3s for reliable mobile playback.

Hanzi/girl audio (914 existing clips), story scripts, language lesson
parameters, and save data remain untouched.
"""
import base64,hashlib,json,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
HTML=ROOT/'index.html'
MP3S=ROOT/'generated-english-v26'
source=(ROOT/'scripts/learning_v22.js').read_text(encoding='utf-8')
words=json.loads(re.search(r'const WORDS=(\[.*?\]);',source,re.S).group(1))
assert len(words)==200
report=json.loads((MP3S/'manifest.json').read_text(encoding='utf-8'))
assert report['words']==[w['en'] for w in words]
mapping={}
for i,w in enumerate(words):
 data=(MP3S/f'{i:03d}.mp3').read_bytes()
 if len(data)<900 or not (data[:3]==b'ID3' or data[:2] in (b'\xff\xf3',b'\xff\xfb',b'\xff\xf2')):
  raise RuntimeError(f"Not an MP3: {w['en']} ({len(data)} bytes)")
 mapping[w['en']]='data:audio/mpeg;base64,'+base64.b64encode(data).decode('ascii')
assert len(mapping)==200
pack={'version':26,'language':'en-US','voice':'English en-US Jenny neural (separate from Mandarin girl voice)',
      'count':200,'audio':mapping}
data='window.StarwhimEnglishPronunciationPack='+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+';'
with tempfile.TemporaryDirectory() as tmp:
    f=Path(tmp)/'english-pack-v26.js'
    f.write_text(data,encoding='utf-8')
    subprocess.run(['node','--check',str(f)],check=True)
out=(ROOT/'english-pronunciations-v26.js')
out.write_text(data+'\n',encoding='utf-8')
html=HTML.read_text(encoding='utf-8')
assert 'window.StarwhimEnglishPronunciationPack=' not in html
assert html.count('StarwhimVoicePack=')==1
assert html.count('lastHanziVoice.playbackRate=0.8')==1
assert html.count('data:audio/mpeg;base64,')==914
assert html.count('</body>')==1
html=html.replace('</body>','<script>\n'+data+'\n</script>\n</body>',1)
assert html.count('data:audio/mpeg;base64,')==1114
assert html.count("window.StarwhimEnglishPronunciationPack=")==1
assert html.count("current.playbackRate=root.querySelector('.learnfirst')?0.72:0.8")==1
assert 'function educationalGameActive()' in html
assert 'lastHanziVoice.playbackRate=0.8' in html
HTML.write_text(html,encoding='utf-8')
(Path(ROOT/'english-mobile-v26-audit.json')).write_text(json.dumps({
 'version':26,'english_recordings':200,'girl_recordings':914,
 'total_recordings':1114,'unchanged_chinese_girl_speed':0.8,
 'english_chinese_lesson_speed':0.72,'english_en_us_recording_speed':0.9,
 'english_neural_voice':report['voice'],
 'mp3_bytes':sum((MP3S/f'{i:03d}.mp3').stat().st_size for i in range(200)),
 'standalone_html_bytes':HTML.stat().st_size,
 'standalone_html_sha256':hashlib.sha256(HTML.read_bytes()).hexdigest(),
 'moonworkshop_hanzi_narrator_scoped':True
},indent=2,ensure_ascii=False)+'\n')
print('PASS standalone HTML:',HTML.stat().st_size,'bytes; 914 girl MP3 + 200 en-US English MP3; mobile fallback embedded')
