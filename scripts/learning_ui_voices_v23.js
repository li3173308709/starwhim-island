/* Recorded girl voice for Chinese text throughout Hanzi and English lessons.
   Uses only recorded MP3 clips; never substitutes the device narrator. */
(function(){
'use strict';
var root=document.getElementById('miniBody');
if(!root)return;
var CN=/[\u3400-\u9fff]/, data=__READING_DATA__;
var clips=function(){return (window.StarwhimVoicePack||{}).audio||{};};
var exactText={"cn:meaning:cat":"中文是：猫。","cn:meaning:dog":"中文是：狗。","cn:meaning:bird":"中文是：鸟。","cn:meaning:fish":"中文是：鱼。","cn:meaning:lion":"中文是：狮子。","cn:meaning:tiger":"中文是：老虎。","cn:meaning:duck":"中文是：鸭子。","cn:meaning:bear":"中文是：熊。","cn:meaning:frog":"中文是：青蛙。","cn:meaning:rabbit":"中文是：兔子。","cn:meaning:apple":"中文是：苹果。","cn:meaning:banana":"中文是：香蕉。","cn:meaning:milk":"中文是：牛奶。","cn:meaning:bread":"中文是：面包。","cn:meaning:cake":"中文是：蛋糕。","cn:meaning:egg":"中文是：鸡蛋。","cn:meaning:rice":"中文是：米饭。","cn:meaning:grape":"中文是：葡萄。","cn:meaning:pear":"中文是：梨。","cn:meaning:cookie":"中文是：饼干。","cn:meaning:red":"中文是：红色。","cn:meaning:blue":"中文是：蓝色。","cn:meaning:green":"中文是：绿色。","cn:meaning:yellow":"中文是：黄色。","cn:meaning:pink":"中文是：粉色。","cn:meaning:purple":"中文是：紫色。","cn:meaning:black":"中文是：黑色。","cn:meaning:white":"中文是：白色。","cn:meaning:orange":"中文是：橙色。","cn:meaning:brown":"中文是：棕色。","cn:meaning:mom":"中文是：妈妈。","cn:meaning:dad":"中文是：爸爸。","cn:meaning:baby":"中文是：宝宝。","cn:meaning:sister":"中文是：姐姐。","cn:meaning:brother":"中文是：哥哥。","cn:meaning:family":"中文是：家庭。","cn:meaning:friend":"中文是：朋友。","cn:meaning:home":"中文是：家。","cn:meaning:grandma":"中文是：奶奶。","cn:meaning:grandpa":"中文是：爷爷。","cn:meaning:sun":"中文是：太阳。","cn:meaning:moon":"中文是：月亮。","cn:meaning:star":"中文是：星星。","cn:meaning:cloud":"中文是：云。","cn:meaning:rain":"中文是：雨。","cn:meaning:snow":"中文是：雪。","cn:meaning:tree":"中文是：树。","cn:meaning:flower":"中文是：花。","cn:meaning:river":"中文是：河流。","cn:meaning:rainbow":"中文是：彩虹。","cn:meaning:book":"中文是：书。","cn:meaning:pen":"中文是：笔。","cn:meaning:pencil":"中文是：铅笔。","cn:meaning:bag":"中文是：书包。","cn:meaning:desk":"中文是：课桌。","cn:meaning:chair":"中文是：椅子。","cn:meaning:school":"中文是：学校。","cn:meaning:paper":"中文是：纸。","cn:meaning:clock":"中文是：时钟。","cn:meaning:ball":"中文是：球。","cn:meaning:run":"中文是：跑。","cn:meaning:jump":"中文是：跳。","cn:meaning:walk":"中文是：走路。","cn:meaning:dance":"中文是：跳舞。","cn:meaning:sing":"中文是：唱歌。","cn:meaning:read":"中文是：阅读。","cn:meaning:write":"中文是：写字。","cn:meaning:swim":"中文是：游泳。","cn:meaning:sleep":"中文是：睡觉。","cn:meaning:smile":"中文是：微笑。","cn:meaning:car":"中文是：汽车。","cn:meaning:bus":"中文是：公交车。","cn:meaning:train":"中文是：火车。","cn:meaning:bike":"中文是：自行车。","cn:meaning:boat":"中文是：船。","cn:meaning:plane":"中文是：飞机。","cn:meaning:road":"中文是：道路。","cn:meaning:park":"中文是：公园。","cn:meaning:house":"中文是：房子。","cn:meaning:bridge":"中文是：桥。","cn:meaning:happy":"中文是：开心。","cn:meaning:sad":"中文是：难过。","cn:meaning:angry":"中文是：生气。","cn:meaning:tired":"中文是：疲倦。","cn:meaning:laugh":"中文是：大笑。","cn:meaning:hello":"中文是：你好。","cn:meaning:goodbye":"中文是：再见。","cn:meaning:please":"中文是：请。","cn:meaning:thank you":"中文是：谢谢。","cn:meaning:sorry":"中文是：对不起。","cn:meaning:head":"中文是：头。","cn:meaning:eye":"中文是：眼睛。","cn:meaning:ear":"中文是：耳朵。","cn:meaning:nose":"中文是：鼻子。","cn:meaning:mouth":"中文是：嘴巴。","cn:meaning:hand":"中文是：手。","cn:meaning:foot":"中文是：脚。","cn:meaning:spring":"中文是：春天。","cn:meaning:summer":"中文是：夏天。","cn:meaning:winter":"中文是：冬天。","cn:meaning:one":"中文是：一。","cn:meaning:two":"中文是：二。","cn:meaning:three":"中文是：三。","cn:meaning:four":"中文是：四。","cn:meaning:five":"中文是：五。","cn:meaning:six":"中文是：六。","cn:meaning:seven":"中文是：七。","cn:meaning:eight":"中文是：八。","cn:meaning:nine":"中文是：九。","cn:meaning:ten":"中文是：十。","cn:meaning:circle":"中文是：圆形。","cn:meaning:square":"中文是：正方形。","cn:meaning:triangle":"中文是：三角形。","cn:meaning:heart":"中文是：心形。","cn:meaning:rectangle":"中文是：长方形。","cn:meaning:oval":"中文是：椭圆形。","cn:meaning:line":"中文是：线。","cn:meaning:dot":"中文是：点。","cn:meaning:diamond":"中文是：菱形。","cn:meaning:cube":"中文是：立方体。","cn:meaning:shirt":"中文是：衬衫。","cn:meaning:dress":"中文是：裙子。","cn:meaning:coat":"中文是：外套。","cn:meaning:hat":"中文是：帽子。","cn:meaning:shoes":"中文是：鞋子。","cn:meaning:socks":"中文是：袜子。","cn:meaning:pants":"中文是：裤子。","cn:meaning:skirt":"中文是：半身裙。","cn:meaning:scarf":"中文是：围巾。","cn:meaning:gloves":"中文是：手套。","cn:meaning:toy":"中文是：玩具。","cn:meaning:doll":"中文是：娃娃。","cn:meaning:teddy":"中文是：泰迪熊。","cn:meaning:kite":"中文是：风筝。","cn:meaning:puzzle":"中文是：拼图。","cn:meaning:robot":"中文是：机器人。","cn:meaning:blocks":"中文是：积木。","cn:meaning:balloon":"中文是：气球。","cn:meaning:drum":"中文是：鼓。","cn:meaning:yo-yo":"中文是：悠悠球。","cn:meaning:watermelon":"中文是：西瓜。","cn:meaning:strawberry":"中文是：草莓。","cn:meaning:cherry":"中文是：樱桃。","cn:meaning:peach":"中文是：桃子。","cn:meaning:lemon":"中文是：柠檬。","cn:meaning:pineapple":"中文是：菠萝。","cn:meaning:carrot":"中文是：胡萝卜。","cn:meaning:corn":"中文是：玉米。","cn:meaning:potato":"中文是：土豆。","cn:meaning:tomato":"中文是：西红柿。","cn:meaning:sunny":"中文是：晴天的。","cn:meaning:rainy":"中文是：下雨的。","cn:meaning:windy":"中文是：有风的。","cn:meaning:cloudy":"中文是：多云的。","cn:meaning:foggy":"中文是：有雾的。","cn:meaning:storm":"中文是：暴风雨。","cn:meaning:warm":"中文是：温暖的。","cn:meaning:cold":"中文是：寒冷的。","cn:meaning:hot":"中文是：炎热的。","cn:meaning:weather":"中文是：天气。","cn:meaning:hospital":"中文是：医院。","cn:meaning:shop":"中文是：商店。","cn:meaning:library":"中文是：图书馆。","cn:meaning:zoo":"中文是：动物园。","cn:meaning:farm":"中文是：农场。","cn:meaning:beach":"中文是：海滩。","cn:meaning:mountain":"中文是：山。","cn:meaning:garden":"中文是：花园。","cn:meaning:station":"中文是：车站。","cn:meaning:museum":"中文是：博物馆。","cn:meaning:eat":"中文是：吃。","cn:meaning:drink":"中文是：喝。","cn:meaning:play":"中文是：玩。","cn:meaning:draw":"中文是：画。","cn:meaning:open":"中文是：打开。","cn:meaning:close":"中文是：关闭。","cn:meaning:listen":"中文是：听。","cn:meaning:look":"中文是：看。","cn:meaning:clap":"中文是：拍手。","cn:meaning:hug":"中文是：拥抱。","cn:meaning:butterfly":"中文是：蝴蝶。","cn:meaning:bee":"中文是：蜜蜂。","cn:meaning:ant":"中文是：蚂蚁。","cn:meaning:elephant":"中文是：大象。","cn:meaning:monkey":"中文是：猴子。","cn:meaning:panda":"中文是：熊猫。","cn:meaning:penguin":"中文是：企鹅。","cn:meaning:dolphin":"中文是：海豚。","cn:meaning:whale":"中文是：鲸鱼。","cn:meaning:turtle":"中文是：乌龟。","cn:meaning:excited":"中文是：兴奋的。","cn:meaning:calm":"中文是：平静的。","cn:meaning:brave":"中文是：勇敢的。","cn:meaning:kind":"中文是：友善的。","cn:meaning:shy":"中文是：害羞的。","cn:meaning:proud":"中文是：自豪的。","cn:meaning:scared":"中文是：害怕的。","cn:meaning:surprised":"中文是：惊讶的。","cn:meaning:curious":"中文是：好奇的。","cn:meaning:friendly":"中文是：友好的。","cn:ui:home":"丁一一，我们先看图片，认识英文和中文。听一听英语发音，学会五个单词，再和小精灵一起闯关。","cn:ui:five":"每次认识五个新单词，学完以后再玩小游戏。","cn:ui:choose":"选择你喜欢的童话主题。","cn:ui:teaching":"今天认识一个新单词。先看图，再听英语发音，记住它的中文。","cn:ui:learn-more":"先学单词，再开启游戏。","cn:ui:unlock":"再认识几个单词，就可以解锁新的挑战啦。","cn:ui:learned":"你已经认识不少单词朋友了，真棒！","cn:ui:review":"我们一起复习刚刚学过的五个单词。","cn:ui:card-next":"如果记住这个单词，就点击下一张图卡吧。","cn:ui:practice":"刚刚认识的单词，现在可以玩一个轻松的小考验啦。","cn:ui:practice-wrong":"再试一次，看看图片，想想这个单词的中文是什么。","cn:ui:practice-right":"答对啦！你真是一个聪明的小探险家！","cn:ui:quiz-picture":"请仔细看看图片，选出对应的英文单词。","cn:ui:quiz-listen":"请听一听英文发音，再找到正确的图片。","cn:ui:quiz-spell":"把刚刚学过的单词按顺序拼出来。","cn:ui:quiz-memory":"找到英文和图片这一对好朋友。","cn:ui:quiz-next":"太棒了，准备挑战下一关！","cn:ui:quiz-end":"恭喜你完成了五个关卡，继续探索更多单词吧！","cn:ui:quiz-help":"如果不确定，可以再听一次发音，慢慢思考。","cn:ui:quiz-stars":"小精灵送来了星星！每一次练习都让你更进步。","cn:ui:quiz-locked":"先学会这些单词，才能打开新关卡哦。","cn:ui:review-none":"你还没有学过这个主题的单词，我们先从第一张图卡开始吧。","cn:ui:topic-done":"这个主题的单词都学过啦，可以换一个主题或者继续复习。","cn:ui:hanzi-home":"欢迎来到汉字寻宝乐园，这里有两百个汉字，先认识汉字和例词，再完成有趣的挑战。","cn:ui:hanzi-lesson":"看看这个汉字和图画，注意拼音的声调，点听一听学习正确的普通话读音。","cn:ui:hanzi-picture":"看看图画，选出对应的汉字。","cn:ui:hanzi-pinyin":"观察拼音和声调，找到正确的汉字。","cn:ui:hanzi-word":"给词语补上缺少的那个汉字。","cn:ui:hanzi-review":"复习之前做错的汉字，一点一点记住它们。","cn:ui:hanzi-right":"回答正确，真棒！我们又认识了一个汉字朋友。","cn:ui:hanzi-wrong":"没关系，再观察一下汉字和图画，慢慢来。","cn:ui:hanzi-done":"本轮识字挑战结束了，继续认识更多汉字吧。","cn:ui:generic-home":"点击学习，先认识新知识，然后再进入游戏。","cn:ui:generic-choose":"请选一个喜欢的选项。","cn:ui:generic-back":"点击返回，回到学习主题。","cn:ui:generic-next":"点击下一张，认识新的朋友。","cn:ui:generic-listen":"点击喇叭，听活泼女孩给你讲一讲。","cn:ui:generic-reward":"完成挑战了！今天你又学到了新本领。","cn:ui:generic-stars":"小星星奖励已经送给你了！","cn:ui:generic-progress":"这是你当前的学习进度。","cn:ui:generic-card":"这是一个学习图卡。先看一看，再点击听一听。","cn:ui:generic-title":"你可以选择听这个页面上的中文说明。","cn:button:学习汉字":"学习汉字。","cn:button:图画选字":"图画选字。","cn:button:拼音挑战":"拼音挑战。","cn:button:词语补全":"词语补全。","cn:button:错题复习":"错题复习。","cn:button:听一听":"听一听。","cn:button:上一个":"上一个。","cn:button:下一个":"下一个。","cn:button:返回主题":"返回主题。","cn:button:再来一轮":"再来一轮。","cn:button:听题目":"听题目。","cn:button:复习学过的词":"复习学过的词。","cn:button:开始学习":"开始学习。","cn:button:返回地图":"返回地图。","cn:button:回到主题地图":"回到主题地图。","cn:button:复习这些词":"复习这些词。","cn:button:听英文跟着读":"听英文跟着读。","cn:button:我认识啦下一张":"我认识啦下一张。","cn:button:去做趣味复习":"去做趣味复习。","cn:button:再认识几个新单词":"再认识几个新单词。","cn:button:继续认识单词":"继续认识单词。","cn:button:打开游戏乐园":"打开游戏乐园。","cn:button:先听一听":"先听一听。","cn:button:进入下一关":"进入下一关。","cn:button:返回主题地图":"返回主题地图。","cn:button:复习更多单词":"复习更多单词。","cn:button:听这个词":"听这个词。","cn:button:听单词":"听单词。","cn:button:撤销一步":"撤销一步。","cn:button:重新拼":"重新拼。","cn:line:汉字寻宝乐园":"汉字寻宝乐园。","cn:line:汉字学习":"汉字学习。","cn:line:本轮识字挑战结束":"本轮识字挑战结束。","cn:line:先学会再去闯关":"先学会再去闯关。","cn:line:选择喜欢的童话主题":"选择喜欢的童话主题。","cn:line:先学单词再开启游戏":"先学单词再开启游戏。","cn:line:还没有学过的词":"还没有学过的词。","cn:line:这个主题的单词都学过啦":"这个主题的单词都学过啦。","cn:line:温习小伙伴今天认识一位单词朋友":"温习小伙伴今天认识一位单词朋友。","cn:line:丁一一真棒":"丁一一真棒。","cn:line:小精灵送来了颗星星":"小精灵送来了颗星星。","cn:line:哪个英文朋友表示":"哪个英文朋友表示。","cn:line:听听单词找到正确的图片图片里的东西对应哪个单词":"听听单词找到正确的图片图片里的东西对应哪个单词。","cn:line:把学过的单词拼出来":"把学过的单词拼出来。","cn:line:找到单词和图片这一对好朋友":"找到单词和图片这一对好朋友。"};
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
 // The spoken text is always visible, so no mismatched narration is mistaken for a verbatim reading.
 if(root.querySelector('.learnfirst'))notice('🔊 正在朗读：'+unique.map(k=>exactText[k]||'').filter(Boolean).join(' '));
 function next(){
   if(id!==token||i>=unique.length)return;
   current=new Audio(clips()[unique[i++]]);
   current.playbackRate=root.querySelector('.learnfirst')?0.72:0.8;current.preservesPitch=true;
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
function educationalGameActive(){return ['hanzi200','englishquest'].includes(window.Starwhim?.minigames?.current);}
function keysFor(node){
 if(!educationalGameActive())return [];
 var t=textOf(node),k=[],cl=''+(node.className||'');
 if(!CN.test(t))return k;
 var spoken=t.replace(/[^\u3400-\u9fff]/g,'');
 if(clips()['cn:line:'+spoken])return ['cn:line:'+spoken];
 if(node.tagName==='BUTTON'&&clips()['cn:button:'+spoken])return ['cn:button:'+spoken];
 var isEnglish=!!node.closest('.learnfirst');
 if(isEnglish){
   // Only speak a sentence if its displayed text matches the recorded script.
   // Never match word meanings via a partial Chinese substring.
   var stripped=v=>String(v||'').replace(/[^\u3400-\u9fffA-Za-z]/g,'');
   var display=stripped(t);
   if(cl.includes('eng-meaning')){
     var wordId=node.dataset.voiceWord || '';
     var word=data.words.find(w=>w.en===wordId);
     if(!word){
       var candidates=data.words.filter(w=>stripped('中文是：'+w.zh+'。')===display);
       if(candidates.length===1)word=candidates[0];
     }
     if(word){
       var mk='cn:meaning:'+word.en;
       if(clips()[mk] && stripped(exactText[mk])===display)k.push(mk);
     }
   }else{
     var matches=Object.keys(exactText).filter(key=>
       (key.startsWith('cn:ui:')||key.startsWith('cn:line:')||key.startsWith('cn:button:')) &&
       !!clips()[key] && stripped(exactText[key])===display);
     if(matches.length===1)k.push(matches[0]);
     else if(matches.length>1){
       // Several recordings with the same spoken Chinese script can share the
       // same display; choose the exact line or teaching phrase, not a guess.
       k.push(matches.find(x=>x.startsWith('cn:ui:'))||matches[0]);
     }
   }
 }else{
   var ch=node.dataset.hanziChar||'';
   var hanzi=data.hanzi.find(x=>x.char===ch);
   var norm=v=>String(v||'').replace(/[^\u3400-\u9fff]/g,'');
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

 }
 return k.filter(function(x){return !!clips()[x]});
}
function blocks(){
 if(!educationalGameActive())return [];
 var pane=root.querySelector('.learnfirst,.v19');if(!pane)return [];
 return [...pane.querySelectorAll(
   '.eng-lead,.eng-question,.eng-meaning,.eng-hint,.eng-top,.eng-topic,.eng-card h3,'+
   '.eng-card p,.eng-pill,.note,.lesson .glyph,.lesson h3,.hanzi-generic,.hanzi-example,.v19>h3,.v19>p'
 )].filter(function(n){return CN.test(textOf(n))&&!n.closest('.v23-voice-status');});
}
function syncEnglishCaptions(){
 var p=root.querySelector('.learnfirst');if(!p)return;
 // Use only the exact teaching recordings that already exist.
 function setText(node,key){
   if(node&&exactText[key]&&node.textContent.trim()!==exactText[key])
     node.textContent=exactText[key];
 }
 var lead=p.querySelector('.eng-lead');
 setText(lead,'cn:ui:home');
 var hint=p.querySelector('.eng-hint');
 if(hint && !hint.dataset.voiceLocked){
   var txt=hint.textContent||'',key='';
   if(txt.includes('每次学习 5 张')||txt.includes('学够'))key='cn:ui:five';
   else if(txt.includes('这个词读作')||txt.includes('跟着念'))key='cn:ui:teaching';
   else if(txt.includes('刚刚都学过')||txt.includes('选错了')||txt.includes('重新选择'))
     key='cn:ui:quiz-help';
   else if(txt.includes('把学过的英文与图片配对'))key='cn:ui:quiz-memory';
   else if(txt.includes('根据图片、意思和发音'))key='cn:ui:quiz-spell';
   if(key)setText(hint,key);
 }
 var question=p.querySelector('.eng-question');
 if(question){
   var q=question.textContent||'';
   if(q.includes('哪个英文朋友表示'))setText(question,'cn:ui:practice');
   else if(q.includes('听听单词'))setText(question,'cn:ui:quiz-listen');
   else if(q.includes('图片里的东西对应'))setText(question,'cn:ui:quiz-picture');
   else if(q.includes('把学过的单词拼出来'))setText(question,'cn:ui:quiz-spell');
   else if(q.includes('找到单词和图片'))setText(question,'cn:ui:quiz-memory');
 }
 p.querySelectorAll('.eng-meaning').forEach(n=>{
   var parent=n.closest('.eng-card');
   var exactWord=parent?.querySelector('.eng-word')?.textContent.trim().toLowerCase();
   var raw=n.textContent.trim().replace(/^(?:意思是|中文意思是|中文是)[：:]?\s*/,'').replace(/[。！!.]$/,'');
   var choices=data.words.filter(w=>w.zh===raw);
   var word=data.words.find(w=>w.en===exactWord&&w.zh===raw);
   if(!word && choices.length===1)word=choices[0];
   if(!word)return;
   n.dataset.voiceWord=word.en;
   var key='cn:meaning:'+word.en;
   setText(n,key);
 });
}
function decorate(){
 queued=false;
 if(!educationalGameActive())return;
 syncEnglishCaptions();
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

root.addEventListener('click',function(event){
 if(!educationalGameActive())return;
 var button=event.target.closest('button');
 if(!button||button.classList.contains('v23-audio-control')||
    button.classList.contains('v23-all')||
    !button.closest('.learnfirst,.v19'))return;
 var label=textOf(button),name=label.replace(/[^\u3400-\u9fff]/g,'');
 // The original "listen to English" button must play the English recording.
 if(!CN.test(name)||label.includes('🔊')||label.includes('听单词')||
    label.includes('听一听'))return;
 var key='cn:button:'+name;
 if(clips()[key])playKeys([key]);
},true);
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
 read:playKeys,stop:stop,refresh:schedule,resolve:keysFor,exactText:exactText};
})();
