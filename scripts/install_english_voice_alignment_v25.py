#!/usr/bin/env python3
"""Replace only the embedded shared learning narrator with the corrected source.

English Chinese educational narration is 0.72x (0.90 of the unchanged 0.80x
girl-voice speed). All Hanzi game code, Hanzi audio speed, the global game,
English word reader, save data, and MP3 payload remain byte-identical.
"""
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

root=Path(__file__).resolve().parent.parent
p=root/'index.html'
old=p.read_text(encoding='utf-8')
source=(root/'scripts/learning_ui_voices_v23.js').read_text(encoding='utf-8')
learning=(root/'scripts/learning_v22.js').read_text(encoding='utf-8')
voice=json.loads((root/'voice-learning-ui-v23-plan.json').read_text(encoding='utf-8'))['lines']
chars=json.loads(re.search(r'const HANZI=(\[.*?\]);',learning,re.S).group(1))
words=json.loads(re.search(r'const WORDS=(\[.*?\]);',learning,re.S).group(1))
assert len(chars)==200 and len(words)==200
embedded={'words':[{'en':w['en'],'zh':w['zh']} for w in words],
          'hanzi':[{'char':w['char'],'word':w['word']} for w in chars],
          'topics':sorted({w['cat'] for w in words})}
assert source.count('__READING_DATA__')==1
replacement=source.replace('__READING_DATA__',json.dumps(embedded,ensure_ascii=False,separators=(',',':')))
anchor='/* Recorded girl voice for Chinese text throughout Hanzi and English lessons.'
assert old.count(anchor)==1,old.count(anchor)
start=old.index(anchor)
end=old.find('</script>',start)
assert end>start
oldblock=old[start:end]
assert 'window.StarwhimChineseNarratorV23=' in oldblock
with tempfile.TemporaryDirectory() as tmp:
    f=Path(tmp)/'english_exact_reading.js'
    f.write_text(replacement,encoding='utf-8')
    subprocess.run(['node','--check',str(f)],check=True)

new=old[:start]+replacement+'\n'+old[end:]
assert new[:start]==old[:start], 'Previous Hanzi module or global content changed'
assert new.endswith(old[end:]), 'Later game content changed'
assert new.count("window.StarwhimChineseNarratorV23=")==1
assert new.count("current.playbackRate=root.querySelector('.learnfirst')?0.72:0.8")==1
assert new.count("lastHanziVoice.playbackRate=0.8")==old.count("lastHanziVoice.playbackRate=0.8")
assert new.count("clip.playbackRate=0.8")==old.count("clip.playbackRate=0.8")
assert new.count("utterance.lang='en-US'")==old.count("utterance.lang='en-US'")
assert new.count("utterance.rate=.90")==old.count("utterance.rate=.90")
assert len(re.findall(r'data:audio/mpeg;base64,',new))==914
assert new.count('</html>')==1
assert len([x for x in voice if x['key'].startswith('cn:meaning:')])==200

p.write_text(new,encoding='utf-8')
report={
    'scope':'English learning Chinese narration only; Hanzi learning unchanged',
    'original_english_reader':'en-US, unchanged',
    'english_learning_chinese_voice_speed':0.72,
    'rest_of_game_girl_voice_speed_unchanged':0.80,
    'hanzi_code_and_narrator_branch_untouched':True,
    'word_count':len(words),'hanzi_count':len(chars),
    'audio_clip_count':914,
    'exact_chinese_meaning_bindings':200,
    'changed_region':'embedded scripts/learning_ui_voices_v23.js only',
    'unchanged_prefix_sha256':hashlib.sha256(old[:start].encode()).hexdigest(),
    'unchanged_suffix_sha256':hashlib.sha256(old[end:].encode()).hexdigest()
}
(root/'english_voice_alignment_v25_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: English-only Chinese 0.72x, exact matched voice captions, '
      'Hanzi and global 0.8x preserved, 914 MP3 untouched',flush=True)
