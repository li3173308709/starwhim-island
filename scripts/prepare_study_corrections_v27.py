#!/usr/bin/env python3
"""Prepare 200 natural one-phrase Hanzi reads, 200 Mandarin meaning corrections.

All replacement MP3s use the existing girl reference voice via F5-TTS.
No legacy 'word. word de char' duplicate, no pinyin spelled as English letters.
"""
from pathlib import Path
import hashlib, json, re

ROOT=Path(__file__).resolve().parent.parent
text=(ROOT/'scripts/learning_v22.js').read_text(encoding='utf-8')
def get(name):
 m=re.search(r'\bconst '+name+r'=(\[.*?\]);',text,re.S)
 if not m: raise RuntimeError('Cannot find '+name)
 return json.loads(m.group(1))
hanzi=get('HANZI'); english=get('WORDS')
assert len(hanzi)==200 and len(english)==200
overrides={'二':'二十','短':'长短','大':'大小','小':'大小',
           '慢':'快慢','轻':'轻重'}
for row in hanzi:
 row['word']=overrides.get(row['char'],row['word'])
 if row['char'] not in row['word']:
  raise RuntimeError(f"Word does not contain target Hanzi: {row}")
assert len({x['char'] for x in hanzi})==200
rows=[]
def push(key,sentence,context):
 rows.append(dict(id='study27'+hashlib.sha256(key.encode()).hexdigest()[:17],
                  key=key,text=sentence,context=context,role='narrator',
                  voice_name='用户参考的活泼女孩音色',
                  provider='F5-TTS'))
for row in hanzi:
 push('hanzi:'+row['char'],f"{row['word']}的{row['char']}。",
      '自然普通话儿童识字。只读一遍例词加目标汉字，不要念拼音字母')
for row in english:
 push('cn:meaning:'+row['en'],f"中文是：{row['zh']}。",
      '儿童英语教学中文释义，避免以前意思的思发音异常')
rephrase={
 'cn:ui:home': '丁一一，我们先看图片，认识英文和中文。听一听英语发音，学会五个单词，再和小精灵一起闯关。',
 'cn:ui:teaching': '今天认识一个新单词。先看图，再听英语发音，记住它的中文。',
 'cn:ui:practice-wrong': '再试一次，看看图片，想想这个单词的中文是什么。',
}
for key,sentence in rephrase.items():
 push(key,sentence,'替换“意思”发音不清楚的中文教学引导')
assert len(rows)==403
assert len({r['id'] for r in rows})==403
assert len({r['key'] for r in rows})==403
assert all('意思' not in r['text'] for r in rows)
assert next(r['text'] for r in rows if r['key']=='hanzi:米')=='大米的米。'
assert next(r['text'] for r in rows if r['key']=='hanzi:饭')=='米饭的饭。'
assert next(r['text'] for r in rows if r['key']=='cn:meaning:cat')=='中文是：猫。'
dest=ROOT/'voice-study-corrections-v27-plan.json'
dest.write_text(json.dumps(dict(version=27,count=len(rows),lines=rows),
              ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS 403 new girl-voiced recordings, one word contextual Hanzi per character; 200 Chinese meanings without “意思”')
