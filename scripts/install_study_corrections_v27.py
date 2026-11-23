#!/usr/bin/env python3
"""Install v27: accurate one-phrase Hanzi examples and English meanings."""
from pathlib import Path
import base64,json,re,subprocess,tempfile
root=Path(__file__).resolve().parent.parent
index=root/'index.html'; src=root/'scripts/learning_v22.js'
nfile=root/'scripts/learning_ui_voices_v23.js'
manifest=root/'voice-study-corrections-v27-plan.json'
html=index.read_text(encoding='utf-8');js=src.read_text(encoding='utf-8')
n=nfile.read_text(encoding='utf-8')
rows=json.loads(manifest.read_text(encoding='utf-8'))['lines']
assert len(rows)==403
scripts={r['key']:r['text'] for r in rows}
override={'二':'二十','短':'长短','大':'大小','小':'大小','慢':'快慢','轻':'轻重'}
def strict(t,old,new,count=1):
 found=t.count(old)
 if found!=count:raise RuntimeError('Expected '+str(count)+' found '+str(found)+' for '+repr(old[:130]))
 return t.replace(old,new)
def fix(t):
 matches=list(re.finditer(r'const HANZI=(\[.*?\]);',t,re.S))
 if not matches:raise RuntimeError('HANZI inventory missing')
 # Older v19 module also embeds a dataset; v22 overrides it later.
 # Edit the LAST (active learning) module only.
 m=matches[-1];data=json.loads(m.group(1))
 assert len(data)==200
 for x in data:
  x['word']=override.get(x['char'],x['word'])
  assert x['char'] in x['word']
  assert scripts['hanzi:'+x['char']]==x['word']+'的'+x['char']+'。'
 t=t[:m.start(1)]+json.dumps(data,ensure_ascii=False,separators=(',',':'))+t[m.end(1):]
 t=strict(t,'<div class="note">已补上全部汉字的可点击朗读功能。点“🔊 听一听”朗读标准普通话汉字和例词；拼音只显示声调，不会作为英文字母朗读。</div>','')
 t=strict(t,'<p class="note">正式配音将朗读汉字和例词，拼音只用于认读和辨认声调。</p>',
   '<p class="note hanzi-example" data-hanzi-char="${a.char}">${a.word}的${a.char}。</p>')
 old_glyph='<div class="glyph">${a.char}</div>'
 new_glyph='<div class="glyph" data-hanzi-char="${a.char}">${a.char}</div>'
 assert old_glyph in t
 at=t.rfind(old_glyph)
 t=t[:at]+new_glyph+t[at+len(old_glyph):]
 t=strict(t,"b('🔊 听题目','hear','main')","b('🔊 听本字示范','hear','main')")
 t=strict(t,'<p class="note" id="hanziFeedback">认真观察，找到正确的汉字。</p>',
   """<p class="note" id="hanziFeedback" data-voice-key="${mode==='pinyin'?'cn:ui:hanzi-pinyin':mode==='word'?'cn:ui:hanzi-word':mode==='review'?'cn:ui:hanzi-review':'cn:ui:hanzi-picture'}">${mode==='pinyin'?'观察拼音和声调，找到正确的汉字。':mode==='word'?'给词语补上缺少的那个汉字。':mode==='review'?'复习之前做错的汉字，一点一点记住它们。':'看看图画，选出对应的汉字。'}</p>""")
 t=strict(t, 'fb.textContent='+chr(96)+'✅ 答对了！${a.char} · ${a.py} · ${a.word}'+chr(96)+';',
    'fb.innerHTML='+chr(96)+'<span class="hanzi-generic" data-voice-key="cn:ui:hanzi-right">回答正确，真棒！我们又认识了一个汉字朋友。</span> <span class="hanzi-example" data-hanzi-char="${a.char}">${a.word}的${a.char}。</span>'+chr(96)+';')
 t=strict(t, 'fb.textContent='+chr(96)+'再试一次！提示：${a.py}，词语“${a.word}”。'+chr(96)+';',
    'fb.innerHTML='+chr(96)+'<span class="hanzi-generic" data-voice-key="cn:ui:hanzi-wrong">没关系，再观察一下汉字和图画，慢慢来。</span> <span class="hanzi-example" data-hanzi-char="${a.char}">${a.word}的${a.char}。</span>'+chr(96)+';')
 t=strict(t,'class="eng-meaning">意思是：${escapeHTML(w.zh)}</div>',
   'class="eng-meaning">中文是：${escapeHTML(w.zh)}。</div>')
 t=strict(t,'class="eng-meaning">${w.zh}</div>',
   'class="eng-meaning">中文是：${w.zh}。</div>',3)
 t=strict(t,'先看图理解意思，再听发音，然后和小精灵一起闯关！',
   '先看图认识中文，再听英语发音，然后和小精灵一起闯关！')
 t=strict(t,'根据图片、意思和发音按顺序拼出字母。',
   '根据图片、中文和英语发音，按顺序拼出字母。')
 return t
js=fix(js);html=fix(html)
m=re.search(r'(window\.StarwhimVoicePack\s*=\s*)({.*?})(;\s*</script>)',html,re.S)
assert m
pack=json.loads(m.group(2));oldkeys=set(pack['audio']);assert len(oldkeys)==914
other_before={k:v for k,v in pack['audio'].items() if k not in scripts}
for r in rows:
 p=root/'generated'/(r['id']+'.mp3')
 if not p.exists() or p.stat().st_size<950:raise RuntimeError('Missing '+str(p))
 d=p.read_bytes()
 if d[:3]!=b'ID3' and d[:2] not in (b'\xff\xfb',b'\xff\xf3'):raise RuntimeError('Bad MP3 '+r['key'])
 pack['audio'][r['key']]='data:audio/mpeg;base64,'+base64.b64encode(d).decode()
assert set(pack['audio'])==oldkeys
assert all(pack['audio'][k]==v for k,v in other_before.items()), 'Unrelated girl recordings changed!'
html=html[:m.start(2)]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+html[m.end(2):]
# Exact text→MP3 map: no partial sentence or Hanzi word guessing.
p=re.search(r'var exactText=({.*?});',n,re.S)
assert p
exact=json.loads(p.group(1))
for key,val in scripts.items():
 if key.startswith('cn:'):exact[key]=val
n=n[:p.start(1)]+json.dumps(exact,ensure_ascii=False,separators=(',',':'))+n[p.end(1):]
old=" }else{\n   if(cl.includes('phonetic'))"
start=n.index(old,n.index('function keysFor(node){'))
end=n.index("\n }\n return k.filter",start)
new=""" }else{
   var ch=node.dataset.hanziChar||'';
   var hanzi=data.hanzi.find(x=>x.char===ch);
   var norm=v=>String(v||'').replace(/[^\\u3400-\\u9fff]/g,'');
   if(hanzi && clips()['hanzi:'+ch] &&
      ((cl.includes('glyph')&&t===ch)||
       (cl.includes('hanzi-example')&&norm(t)===norm(hanzi.word+'的'+ch+'。'))))
     k.push('hanzi:'+ch);
   var vkey=node.dataset.voiceKey||'';
   if(vkey && clips()[vkey] && exactText[vkey] &&
      norm(exactText[vkey])===norm(t)) k.push(vkey);
   if(!k.length){
     var exact=Object.keys(exactText).filter(v=>v.startsWith('cn:ui:hanzi-')
        && clips()[v] && norm(exactText[v])===norm(t));
     if(exact.length===1)k.push(exact[0]);
   }
"""
n=n[:start]+new+n[end:]
n=strict(n,".eng-pill,.note,.lesson .glyph,.lesson h3,.v19>h3,.v19>p,#hanziFeedback", ".eng-pill,.note,.lesson .glyph,.lesson h3,.hanzi-generic,.hanzi-example,.v19>h3,.v19>p")
n=strict(n,"stripped('中文意思是：'+w.zh+'。')","stripped('中文是：'+w.zh+'。')")
n=strict(n,"replace(/^意思是[：:]?\\s*/,'')",
         "replace(/^(?:意思是|中文意思是|中文是)[：:]?\\s*/,'')")
words=json.loads(re.search(r'const WORDS=(\[.*?\]);',js,re.S).group(1))
hz=json.loads(re.search(r'const HANZI=(\[.*?\]);',js,re.S).group(1))
data={'words':[{'en':x['en'],'zh':x['zh']} for x in words],
      'hanzi':[{'char':x['char'],'word':x['word']} for x in hz],
      'topics':sorted({x['cat'] for x in words})}
embedded=n.replace('__READING_DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':')))
anchor='/* Recorded girl voice for Chinese text throughout Hanzi and English lessons.'
assert html.count(anchor)==1
start=html.index(anchor);end=html.index('</script>',start)
html=html[:start]+embedded+'\n'+html[end:]
with tempfile.TemporaryDirectory() as tmp:
 for k,content in [('learn.js',js),('narrator.js',embedded)]:
  p=Path(tmp)/k;p.write_text(content,encoding='utf-8')
  subprocess.run(['node','--check',str(p)],check=True)
assert html.count('data:audio/mpeg;base64,')==1114
assert html.count('window.StarwhimEnglishPronunciationPack=')==1
assert html.count('lastHanziVoice.playbackRate=0.8')==1
assert html.count("current.playbackRate=root.querySelector('.learnfirst')?0.72:0.8")==1
assert html.count('</html>')==1
src.write_text(js,encoding='utf-8');nfile.write_text(n,encoding='utf-8')
index.write_text(html,encoding='utf-8')
(root/'study-v27-audit.json').write_text(json.dumps({
 'version':27,'replaced_audio':403,'hanzi_count':200,'english_meaning_count':200,
 'girl_mp3':914,'separate_english_mp3':200,
 'one_phrase_hanzi_example':'大米的米。','english_meaning_example':'中文是：猫。',
 'topic_note_removed':True,'hanzi_hint_bound_by_explicit_id':True
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 403 new clips; 200 Hanzi phrases and 200 English meanings; fixed hints')
