/* Recorded girl voice for Chinese text throughout Hanzi and English lessons.
   No speechSynthesis, and no substitution with a different narrator. */
(function(){
'use strict';
var root=document.getElementById('miniBody');
if(!root)return;
var CN=/[\u3400-\u9fff]/, data=__READING_DATA__;
var clips=function(){return (window.StarwhimVoicePack||{}).audio||{};};
var current=null,token=0,queued=false;
function stop(){token++;if(current){try{current.pause()}catch(e){}}current=null;}
function notice(msg){
 var node=document.getElementById('v23-narrator-notice');
 if(!node){node=document.createElement('p');node.id='v23-narrator-notice';
 node.className='v23-voice-status';(root.querySelector('.learnfirst,.v19')||root).prepend(node);}
 node.textContent=msg;
}
function playKeys(keys){
 var unique=[...new Set(keys)].filter(function(k){return k&&clips()[k];});
 if(!unique.length){notice('这一段的女孩配音尚未生成，暂时不能朗读。');return false;}
 stop();var id=token,i=0;
 function next(){
   if(id!==token||i>=unique.length)return;
   current=new Audio(clips()[unique[i++]]);
   current.volume=.95;
   current.onended=next;
   current.onerror=function(){notice('录音播放失败，可以再试一次。')};
   var result=current.play();
   if(result&&result.catch)result.catch(function(){if(id===token)notice('请先点击页面允许声音播放。')});
 }
 next();return true;
}
function textOf(node){
 return [...node.childNodes].filter(function(n){return !(n.classList&&n.classList.contains('v23-audio-control'));})
 .map(function(n){return n.textContent||''}).join(' ').replace(/\s+/g,' ').trim();
}
function meaning(text){
 return data.words.filter(function(w){return text.includes(w.zh);})
 .sort(function(a,b){return b.zh.length-a.zh.length})[0];
}
function keysFor(node){
 var t=textOf(node),k=[],cl=''+(node.className||'');
 if(!CN.test(t))return k;
 var isEnglish=!!node.closest('.learnfirst');
 if(isEnglish){
   var w=meaning(t),card=node.closest('.eng-card');
   var cardWord=card&&card.querySelector('.eng-word');
   if(cardWord){var found=data.words.find(function(v){return v.en===cardWord.textContent.trim().toLowerCase()});if(found)w=found;}
   if(cl.includes('eng-meaning')&&w)k.push('cn:meaning:'+w.en);
   else if(cl.includes('eng-topic')){
     var match=data.topics.find(function(x){return t.includes(x.replace(/[^\u4e00-\u9fff]/g,''));});
     if(match)k.push('cn:topic:'+match);
   }else if(cl.includes('eng-lead'))k.push('cn:ui:home','cn:ui:five');
   else if(cl.includes('eng-question')){
     k.push(t.includes('听听')?'cn:ui:quiz-listen':t.includes('图片')?'cn:ui:quiz-picture':
       t.includes('拼')?'cn:ui:quiz-spell':'cn:ui:practice');
     if(w)k.push('cn:meaning:'+w.en);
   }else if(cl.includes('eng-hint')){
     k.push(t.includes('不对')||t.includes('再试')?'cn:ui:practice-wrong':
       t.includes('答对')||t.includes('棒')?'cn:ui:practice-right':
       t.includes('锁')?'cn:ui:unlock':'cn:ui:quiz-help');
     if(w)k.push('cn:meaning:'+w.en);
   }else if(cl.includes('eng-top')||cl.includes('eng-pill'))k.push('cn:ui:generic-progress');
   else if(t.includes('先学会')||t.includes('先学单词'))k.push('cn:ui:learn-more');
   else if(t.includes('五关')||t.includes('挑战成功'))k.push('cn:ui:quiz-end');
   else if(t.includes('复习'))k.push('cn:ui:review');
   else if(t.includes('认识'))k.push('cn:ui:teaching');
   else k.push('cn:ui:generic-listen');
 }else{
   if(cl.includes('phonetic'))return [];
   var hz=data.hanzi.find(function(x){return t===x.char;})||
     data.hanzi.find(function(x){return x.word.length>1&&t.includes(x.word)});
   if(hz)k.push('hanzi:'+hz.char);
   else if(t.includes('选字'))k.push('cn:ui:hanzi-picture');
   else if(t.includes('拼音'))k.push('cn:ui:hanzi-pinyin');
   else if(t.includes('词语'))k.push('cn:ui:hanzi-word');
   else if(t.includes('复习'))k.push('cn:ui:hanzi-review');
   else if(t.includes('答对'))k.push('cn:ui:hanzi-right');
   else if(t.includes('再试'))k.push('cn:ui:hanzi-wrong');
   else k.push('cn:ui:hanzi-lesson');
 }
 return k.filter(function(x){return !!clips()[x]});
}
function blocks(){
 var pane=root.querySelector('.learnfirst,.v19');if(!pane)return [];
 return [...pane.querySelectorAll(
   '.eng-lead,.eng-question,.eng-meaning,.eng-hint,.eng-top,.eng-topic,.eng-card h3,'+
   '.eng-card p,.eng-pill,.note,.lesson .glyph,.lesson h3,.v19>h3,.v19>p,#hanziFeedback'
 )].filter(function(n){return CN.test(textOf(n))&&!n.closest('.v23-voice-status');});
}
function decorate(){
 queued=false;
 var pane=root.querySelector('.learnfirst,.v19');if(!pane)return;
 if(!pane.querySelector('[data-v23-read-all]')){
   var all=document.createElement('button');all.type='button';all.dataset.v23ReadAll='1';
   all.className='v23-all';all.textContent='🔊 听本页中文';
   all.onclick=function(e){e.preventDefault();e.stopPropagation();
     var sequence=blocks().slice(0,12).flatMap(keysFor);
     if(!sequence.length)sequence=[pane.classList.contains('learnfirst')?'cn:ui:home':'cn:ui:hanzi-home'];
     if(playKeys(sequence))notice('正在播放这一页的中文说明。');
   };
   pane.prepend(all);
 }
 for(var n of blocks()){
   if(n.dataset.v23Decorated)continue;
   n.dataset.v23Decorated='1';
   if(!keysFor(n).length)continue;
   var b=document.createElement('button');b.type='button';b.className='v23-audio-control';
   b.textContent='🔊';b.title='听活泼女孩朗读中文';
   b.setAttribute('aria-label','听活泼女孩朗读这段中文');
   (function(target,btn){btn.onclick=function(e){e.stopPropagation();e.preventDefault();playKeys(keysFor(target));};})(n,b);
   if(n.tagName==='BUTTON')n.insertAdjacentElement('afterend',b);else n.append(b);
 }
}
function schedule(){if(queued)return;queued=true;queueMicrotask(decorate);}
new MutationObserver(function(m){
 if(m.some(function(r){return [...r.addedNodes].some(function(n){
   return n.nodeType===1&&!n.classList?.contains('v23-audio-control')&&
   !n.classList?.contains('v23-voice-status')&&!n.classList?.contains('v23-all');
 });}))schedule();
}).observe(root,{childList:true,subtree:true});
var css=document.createElement('style');
css.textContent='#miniBody .v23-audio-control{display:inline-flex;align-items:center;justify-content:center;'+
 'margin:2px 5px;min-width:36px;min-height:36px;padding:5px 8px;border-radius:30px;'+
 'border:1px solid #dfc5ef;background:#fff4fb;color:#8452a3;font-size:16px;cursor:pointer;touch-action:manipulation}'+
 '#miniBody .v23-all{position:sticky;top:2px;z-index:3;display:block;margin:3px 0 9px auto;'+
 'border:1px solid #d5b7ed;border-radius:25px;background:#fff4fc;color:#764f92;padding:8px 12px;'+
 'font-size:14px;min-height:42px;font-weight:800}'+
 '#miniBody .v23-voice-status{margin:7px auto;padding:8px;border-radius:12px;'+
 'background:#fff7e3;color:#725d81;text-align:center;font-size:13px}';
document.head.appendChild(css);
schedule();
window.StarwhimChineseNarratorV23={ready:true,meaningCount:data.words.length,
 read:playKeys,stop:stop,refresh:schedule};
})();
