/* Starwhim Island v1.8 - three replayable arcade/strategy modes. */
(()=>{
'use strict';
const S=window.Starwhim,M=S?.minigames;if(!M)return;
const by=id=>document.getElementById(id);
const entries=[
 {id:'rainbowdash',name:'彩虹飞行大冒险',emoji:'🛼',desc:'切换跑道，躲开乌云，收集连击星星',tag:'实时闯关 · 反应力'},
 {id:'starmerge',name:'星星合成研究所',emoji:'🌠',desc:'滑动合成星星，从2点亮到128',tag:'数字策略 · 可反复挑战'},
 {id:'spriteguard',name:'精灵花园守卫战',emoji:'🏰',desc:'种植魔法花塔，抵挡不断来袭的小怪',tag:'塔防策略 · 三波敌人'}
];
entries.forEach(e=>{if(!S.MINIGAMES.some(x=>x.id===e.id))S.MINIGAMES.push(e)});
const css=document.createElement('style');css.textContent=`
.arcade-wrap{max-width:650px;margin:auto;text-align:center;color:#625477;user-select:none}.arcade-top{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:center;margin:9px auto}.arcade-pill{background:#f3e7ff;border-radius:20px;padding:7px 11px;font-size:13px;font-weight:800}.arcade-desc{font-size:14px;line-height:1.7;margin:8px auto;max-width:570px}.arcade-buttons{display:flex;gap:9px;justify-content:center;flex-wrap:wrap;margin:15px auto}.arcade-buttons button,.arcade-button{border-radius:15px;padding:12px 18px;background:linear-gradient(140deg,#fce1f2,#e6dcff);color:#644a80;border:2px solid #edccf4;font-weight:800;font-size:15px;touch-action:manipulation;min-height:46px}.arcade-buttons button:active,.arcade-button:active{transform:scale(.96)}.arcade-buttons button:disabled{opacity:.4}.arcade-alert{margin:12px auto;min-height:27px;font-weight:700;color:#9e5689}.arcade-dash{width:min(96%,440px);margin:8px auto;display:grid;grid-template-columns:repeat(3,1fr);gap:7px;padding:8px;background:#d4effc;border-radius:19px;border:3px solid #f7d1f0;touch-action:manipulation}.arcade-dash .dash-cell{height:clamp(47px,9.5vw,65px);border-radius:15px;background:linear-gradient(170deg,#fbf8ff,#e9f5ff);display:grid;place-items:center;font-size:clamp(23px,6vw,35px);box-shadow:inset 0 1px 2px #fff}.arcade-dash .dash-hero{background:#fff0ae;outline:3px solid #f9cb67}.arcade-merge{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:10px;border-radius:20px;background:#e3d7ee;width:min(94%,360px);margin:10px auto;touch-action:none}.arcade-merge .merge-tile{display:grid;place-items:center;aspect-ratio:1;border-radius:13px;font-size:clamp(18px,5vw,28px);font-weight:900;color:#745388;background:#f8f4fb}.arcade-merge .merge-tile[data-n="2"]{background:#fff6ce}.arcade-merge .merge-tile[data-n="4"]{background:#fce3be}.arcade-merge .merge-tile[data-n="8"]{background:#ffd5cf}.arcade-merge .merge-tile[data-n="16"]{background:#f7c7e5}.arcade-merge .merge-tile[data-n="32"]{background:#e4c7fc}.arcade-merge .merge-tile[data-n="64"]{background:#b7e9f9}.arcade-merge .merge-tile[data-n="128"],.arcade-merge .merge-tile[data-n="256"]{background:#ffde87}.arcade-tower{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:5px;max-width:530px;margin:14px auto}.arcade-tower button,.arcade-tower .tower-cell{aspect-ratio:1;min-width:0;border-radius:11px;background:#f0ebff;border:1px solid #ddc9ee;display:grid;place-items:center;font-size:clamp(17px,4vw,27px);padding:0;position:relative}.arcade-tower button{background:#dcf4dc;border:2px solid #a9dfaf}.arcade-tower button:disabled{opacity:.6;cursor:not-allowed}.arcade-tower .tower-base{background:#f8ebbc}.arcade-tower .tower-enemy{background:#fee1e8}.arcade-tower small{position:absolute;right:1px;bottom:0px;font-size:9px;font-weight:bold;color:#933b65}.arcade-tier{padding:7px 10px;border-radius:18px;font-size:13px;background:#fff1d3;display:inline-block}.arcade-hint{font-size:12px;opacity:.75}.arcade-turn{outline:2px solid #b892dd}.arcade-final{max-width:430px;margin:15px auto}
@media(max-width:390px){.arcade-tower{gap:3px}.arcade-tower button,.arcade-tower .tower-cell{border-radius:7px}.arcade-buttons button{font-size:13px;padding:11px 12px}}
`;document.head.appendChild(css);
const print=h=>{if(by('miniBody'))by('miniBody').innerHTML='<div class="arcade-wrap">'+h+'</div>'};
const top=(title,items)=>`<h3>${title}</h3><div class="arcade-top">${items.map(x=>`<span class="arcade-pill">${x}</span>`).join('')}</div>`;
const btn=(id,label)=>`<button id="${id}" class="arcade-button">${label}</button>`;
const audio=(type='pop')=>{try{S.audio[type]()}catch(e){}};
function complete(id,text,stars){M.win(id,text,stars,10)}
// Each timer is held by the existing mini-game controller; closing cancels every tick.
M.rainbowdashStart=function(){
 let stage=1,d,ended=false;
 const dispose=()=>{document.removeEventListener('keydown',onkey)};
 const onkey=e=>{if(M.current!=='rainbowdash')return;if(['ArrowLeft','a','A'].includes(e.key)){e.preventDefault();shift(-1)}else if(['ArrowRight','d','D'].includes(e.key)){e.preventDefault();shift(1)}};
 if(M._rainbowKeyListener)document.removeEventListener('keydown',M._rainbowKeyListener);
 M._rainbowKeyListener=onkey;document.addEventListener('keydown',onkey);
 if(!M._arcadeCloseWrapped){const originalClose=M.close;M.close=function(){for(const key of ['_rainbowKeyListener','_mergeKeyListener'])if(this[key]){document.removeEventListener('keydown',this[key]);this[key]=null}return originalClose.call(this)};M._arcadeCloseWrapped=true}
 function shift(n){if(M.current!=='rainbowdash'||ended||!d)return;d.lane=Math.max(0,Math.min(2,d.lane+n));render()}
 const begin=()=>{ended=false;d={stage,tick:0,lane:1,hp:4,score:0,combo:0,objects:[],best:0};render();M.later(tick,520)};
 const tick=()=>{
  if(M.current!=='rainbowdash'||ended)return;
  d.tick++;
  for(const o of d.objects)o.row++;
  for(const o of d.objects.filter(o=>o.row===4&&o.lane===d.lane)){
    if(o.kind==='cloud'){d.hp--;d.combo=0;audio('fail')}else{d.score+=2+Math.min(6,d.combo);d.combo++;d.best=Math.max(d.best,d.combo);audio('collect')}
  }
  d.objects=d.objects.filter(o=>o.row<4);
  if(d.tick%2===0&&d.tick<20+stage*4){const lane=Math.floor(Math.random()*3);d.objects.push({lane,row:0,kind:Math.random()<(0.26+stage*.085)?'cloud':'star'})}
  if(d.hp<=0){ended=true;print(top('🌧️ 乌云把彩虹挡住啦！',[`本次积分 ${d.score}`])+`<p class="arcade-desc">试着提前观察乌云的位置，再切换跑道。</p><div class="arcade-buttons">${btn('dashRetry','再试一次 🔁')}${btn('dashHome','返回小游戏')}</div>`);by('dashRetry').onclick=begin;by('dashHome').onclick=()=>M.close();return}
  if(d.tick>=24+stage*4){ended=true;
    if(stage>=3){complete('rainbowdash',`你完成了三段彩虹竞速，最高连击 ${d.best} 次！`,32);dispose();return}
    stage++;print(top('🎉 彩虹赛段完成！',[`得分 ${d.score}`,`下段难度 ${stage}/3`])+`<p class="arcade-desc">下一段乌云更多，反应要更快啦！</p><div class="arcade-buttons">${btn('dashNext','继续飞行 🚀')}</div>`);by('dashNext').onclick=begin;audio('success');return}
  render();M.later(tick,Math.max(320,560-stage*55));
 };
 const render=()=>{
   if(M.current!=='rainbowdash'||ended)return;
   let cells='';for(let row=0;row<5;row++)for(let col=0;col<3;col++){
    const obj=d.objects.find(x=>x.lane===col&&x.row===row);
    const hero=row===4&&col===d.lane;
    cells+=`<div class="dash-cell ${hero?'dash-hero':''}" data-col="${col}">${hero?'🦄':obj?(obj.kind==='star'?'⭐':'🌧️'):'·'}</div>`;
   }
   print(top('🌈 彩虹飞行大冒险',[`赛段 ${stage}/3`,`❤️ ${d.hp}`,`⭐ ${d.score}`,`🔥 ${d.combo} 连击`])+`<p class="arcade-desc">提前躲开乌云 🌧️，接住星星 ⭐。左右按钮、方向键或左右滑动都可以移动。</p><div class="arcade-dash" id="dashBoard">${cells}</div><div class="arcade-buttons">${btn('dashLeft','⬅️ 左移')}${btn('dashRight','右移 ➡️')}</div><p class="arcade-hint">提示：星星连续接中，分数会更高</p>`);
   by('dashLeft').onclick=()=>shift(-1);by('dashRight').onclick=()=>shift(1);
   let start=0;const field=by('dashBoard');field.ontouchstart=e=>{start=e.changedTouches[0].clientX};field.ontouchend=e=>{const dx=e.changedTouches[0].clientX-start;if(Math.abs(dx)>20)shift(Math.sign(dx))};
   field.querySelectorAll('[data-col]').forEach(el=>el.onclick=()=>shift(Math.sign(Number(el.dataset.col)-d.lane)));
 };
 begin();
};
// 2048-like sliding stars with persistent three-milestone progression.
M.starmergeStart=function(){
 let board=Array(16).fill(0),total=0,step=0,stage=1,locked=false;
 const goal=()=>[32,64,128][stage-1];
 const free=()=>board.map((v,i)=>v?-1:i).filter(x=>x>=0);
 const spawn=()=>{const a=free();if(a.length){board[a[Math.floor(Math.random()*a.length)]]=Math.random()<.88?2:4;return true}return false};
 const apply=(dir)=>{
  if(M.current!=='starmerge'||locked)return;
  let next=board.slice(),gain=0;
  for(let a=0;a<4;a++){
   let ids=[];for(let b=0;b<4;b++)ids.push(dir==='left'?a*4+b:dir==='right'?a*4+3-b:dir==='up'?b*4+a:(3-b)*4+a);
   const v=ids.map(i=>board[i]).filter(Boolean),out=[];
   for(let k=0;k<v.length;k++){if(k+1<v.length&&v[k]===v[k+1]){out.push(v[k]*2);gain+=v[k]*2;k++}else out.push(v[k])}
   ids.forEach((id,j)=>next[id]=out[j]||0);
  }
  if(next.every((v,i)=>v===board[i]))return;
  board=next;step++;total+=gain;spawn();if(gain)audio('collect');else audio('pop');
  if(board.some(v=>v>=goal())){
   locked=true;const target=goal();if(stage===3){complete('starmerge','你合出了闪耀的128点星星！今天是星光合成大师！',36);return}
   stage++;render(`🎉 成功合成 ${target} 点！下一目标：${goal()} 点。`,true);return;
  }
  const moves=['left','right','up','down'];if(!free().length&&!moves.some(d=>canMove(d))){locked=true;render('棋盘放满了！重新挑战会生成新地图。',true,true);return}
  render();
 };
 const canMove=d=>{for(let i=0;i<4;i++)for(let j=0;j<4;j++){
   const x=i*4+j;if(!board[x])return true;
   if(j<3&&board[x]===board[x+1])return true;
   if(i<3&&board[x]===board[x+4])return true;
  }return false};
 const restart=()=>{board=Array(16).fill(0);total=0;step=0;stage=1;locked=false;spawn();spawn();render()};
 const render=(status='',paused=false,failed=false)=>{
  const tiles=board.map(v=>`<div class="merge-tile" data-n="${v}">${v?v>=128?'🌟'+v:v:'·'}</div>`).join('');
  print(top('🌠 星星合成研究所',[`目标 ${goal()}`,`分数 ${total}`,`移动 ${step} 次`])+`<p class="arcade-desc">滑动棋盘或点击方向按钮；两个相同数字相撞会合成更大的星星。别把棋盘填满！</p><div class="arcade-merge" id="mergeGrid">${tiles}</div><p class="arcade-alert">${status}</p><div class="arcade-buttons">${failed?btn('mergeReset','重新开始 🔁'):paused?btn('mergeContinue','继续挑战 ⭐'):`${btn('mUp','⬆️')}${btn('mLeft','⬅️')}${btn('mDown','⬇️')}${btn('mRight','➡️')}`}${btn('mergeRestart','重置棋盘')}</div>`);
  if(!paused&&!failed){[['mUp','up'],['mLeft','left'],['mRight','right'],['mDown','down']].forEach(([id,dir])=>by(id).onclick=()=>apply(dir))}
  const field=by('mergeGrid');let sx=0,sy=0;field.ontouchstart=e=>{sx=e.changedTouches[0].clientX;sy=e.changedTouches[0].clientY};field.ontouchend=e=>{const dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;if(Math.max(Math.abs(dx),Math.abs(dy))<24)return;apply(Math.abs(dx)>Math.abs(dy)?(dx>0?'right':'left'):(dy>0?'down':'up'))};
  if(by('mergeContinue'))by('mergeContinue').onclick=()=>{locked=false;render()};
  if(by('mergeReset'))by('mergeReset').onclick=restart;
  by('mergeRestart').onclick=restart;
 };
 // Scoped key listener: never leak to the rest of the main game.
 if(M._mergeKeyListener)document.removeEventListener('keydown',M._mergeKeyListener);
 M._mergeKeyListener=e=>{if(M.current!=='starmerge')return;const k={ArrowUp:'up',ArrowDown:'down',ArrowLeft:'left',ArrowRight:'right'}[e.key];if(k){e.preventDefault();apply(k)}};
 document.addEventListener('keydown',M._mergeKeyListener);
 restart();
};
// Build/upgrade flower turrets in three lanes. Deterministic tick and wave structure.
M.spriteguardStart=function(){
 let lv=1,d;
 const init=()=>{d={wave:lv,tick:0,sun:12,hp:5,kill:0,towers:[0,0,0],foes:[],ended:false};render();M.later(tick,850)};
 const build=lane=>{
  if(M.current!=='spriteguard'||d.ended)return;
  const cost=d.towers[lane]?8:5;if(d.towers[lane]>=3||d.sun<cost){audio('fail');return}
  d.sun-=cost;d.towers[lane]++;audio('collect');render();
 };
 const tick=()=>{
  if(M.current!=='spriteguard'||d.ended)return;
  d.tick++;d.sun+=d.tick%2===0?3:1;
  if(d.tick<=22&&d.tick%2===0){const lane=(d.tick/2+lv)%3;d.foes.push({lane,x:6,hp:lv+1+Math.floor(d.tick/13)})}
  for(const e of d.foes){if(d.towers[e.lane]>0){e.hp-=d.towers[e.lane];}if(e.hp>0)e.x--;}
  const dead=d.foes.filter(e=>e.hp<=0),escaped=d.foes.filter(e=>e.hp>0&&e.x<=0);
  d.kill+=dead.length;if(dead.length)audio('collect');if(escaped.length){d.hp-=escaped.length;audio('fail')}
  d.foes=d.foes.filter(e=>e.hp>0&&e.x>0);
  if(d.hp<=0){d.ended=true;print(top('🌧️ 花园需要重新守护',[`击退 ${d.kill} 只小怪`])+`<p class="arcade-desc">先给三条道路都种上一株魔法花，再升级花塔提高攻击力。</p><div class="arcade-buttons">${btn('guardRetry','重新守护 🌸')}</div>`);by('guardRetry').onclick=init;return}
  if(d.tick>=24&&d.foes.length===0){d.ended=true;if(lv===3){complete('spriteguard','三波小怪全部退散！你是精灵花园最勇敢的守护者！',40);return}
    lv++;print(top('🌈 守护成功！',[`击退 ${d.kill} 只`,`下一波 ${lv}/3`])+`<p class="arcade-desc">下一波小怪的生命值更高，记得合理升级花塔！</p><div class="arcade-buttons">${btn('guardNext','迎接下一波 🌷')}</div>`);by('guardNext').onclick=init;audio('success');return}
  render();M.later(tick,Math.max(560,850-(lv-1)*100));
 };
 const render=()=>{
  if(M.current!=='spriteguard'||!d||d.ended)return;
  const cells=[];for(let lane=0;lane<3;lane++){
   for(let x=0;x<7;x++){
    const foe=d.foes.find(e=>e.lane===lane&&e.x===x);
    if(x===0)cells.push(`<div class="tower-cell tower-base">🏠</div>`);
    else if(x===1)cells.push(`<button data-lane="${lane}" title="${d.towers[lane]?'升级花塔':'种花塔'}">${d.towers[lane]?'🌺':'➕'}${d.towers[lane]?`<small>Lv.${d.towers[lane]}</small>`:''}</button>`);
    else cells.push(`<div class="tower-cell ${foe?'tower-enemy':''}">${foe?'🐛':'🌱'}${foe?`<small>♥${foe.hp}</small>`:''}</div>`);
   }
  }
  print(top('🏰 精灵花园守卫战',[`第 ${lv}/3 波`,`☀️ ${d.sun}`,`❤️ ${d.hp}`,`🐛 已击退 ${d.kill}`])+`<p class="arcade-desc">点击每条路的 ➕ 种植花塔（5 阳光），再次点击升级（8 阳光）；保护左侧小屋！</p><div class="arcade-tower">${cells.join('')}</div><div class="arcade-tier">🌺 花塔射击自动进行　·　阳光随时间增长</div><p class="arcade-hint">先覆盖所有道路，再升级有更多小怪的道路。</p>`);
  by('miniBody').querySelectorAll('[data-lane]').forEach(el=>{const lane=Number(el.dataset.lane);el.onclick=()=>build(lane);el.disabled=d.towers[lane]>=3});
 };
 init();
};
const oldOpen=M.open;
M.open=function(id){const out=oldOpen.call(this,id);if(entries.some(e=>e.id===id)&&S.game?.state?.settings?.speech!==false){
 const text={rainbowdash:'彩虹飞行大冒险。左右移动躲开乌云，接住星星。连续接中就会得到更多分数！',starmerge:'星星合成研究所。滑动魔法棋盘，把相同的星星合在一起。一路合成闪耀的一百二十八点星星！',spriteguard:'精灵花园守卫战。种下魔法花朵，守护三条小路。先照顾每一条路，再把花朵升级！'}[id];
 if(window.StarwhimVoicePack?.audio?.[text])S.audio.speak(text,{role:'bubble'});
 }return out};
window.StarwhimArcade={version:1,ids:entries.map(e=>e.id),voiceTexts:{rainbowdash:'彩虹飞行大冒险。左右移动躲开乌云，接住星星。连续接中就会得到更多分数！',starmerge:'星星合成研究所。滑动魔法棋盘，把相同的星星合在一起。一路合成闪耀的一百二十八点星星！',spriteguard:'精灵花园守卫战。种下魔法花朵，守护三条小路。先照顾每一条路，再把花朵升级！'}};
})();

