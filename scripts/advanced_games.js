/* Starwhim Island: advanced puzzles, compatible with existing save and rewards */
(function(){
'use strict';
const S=window.Starwhim,M=S&&S.minigames;if(!M)return;
const defs=[
{id:'starmaze',emoji:'🗺️',name:'星光迷宫探险',desc:'找钥匙、规划路线，连续闯过三座迷宫',tag:'路线策略 · 进阶'},
{id:'starsudoku',emoji:'🔮',name:'魔法数独学院',desc:'推理每行、每列和魔法宫格的图案',tag:'逻辑推理 · 进阶'},
{id:'elfcode',emoji:'🧪',name:'精灵密码实验室',desc:'根据颜色与位置线索破解精灵密码',tag:'密码推理 · 进阶'}];
defs.forEach(g=>{if(!S.MINIGAMES.some(x=>x.id===g.id))S.MINIGAMES.push(g)});
const panel=()=>document.getElementById('miniBody');
const print=html=>panel().innerHTML='<div class="challenge-wrap">'+html+'</div>';
const heading=(text,lv,extra)=>'<p class="mini-instruction">'+text+'</p><div class="challenge-meta"><span>🏅 第 '+lv+'/3 关</span><span>'+extra+'</span></div>';
const style=document.createElement('style');
style.textContent='.challenge-wrap{max-width:660px;margin:auto;text-align:center;color:#66577c}.challenge-meta{display:flex;justify-content:center;flex-wrap:wrap;gap:12px;margin:10px auto 18px}.challenge-meta span{border-radius:30px;padding:7px 12px;background:#f6eaff;font-weight:700;font-size:13px}.challenge-board{display:grid;gap:5px;max-width:min(90vw,420px);margin:14px auto}.challenge-board button{border:2px solid #e5d4ef;border-radius:12px;background:#fff8ff;aspect-ratio:1;min-width:0;display:grid;place-items:center;font-size:clamp(17px,4.5vw,28px);touch-action:manipulation}.challenge-board button:focus-visible,.challenge-selected{outline:3px solid #f2a1d5}.challenge-wall{background:#d7caec!important}.challenge-hero{background:#fff4b6!important;border-color:#ffd276!important}.challenge-locked{background:#e9def3!important}.challenge-controls{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin:14px auto}.challenge-controls button,.challenge-options button{border:2px solid #ecc8e8;border-radius:14px;min-height:45px;min-width:45px;background:#fff4fb;font-size:23px}.challenge-options{display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin:14px auto}.challenge-hint{font-size:13px;color:#846a99;line-height:1.6}.challenge-history{max-height:195px;overflow:auto}.challenge-history div{padding:6px;background:#f9efff;margin:5px;border-radius:10px;font-size:17px}.challenge-history small{font-size:12px}.challenge-controls button:disabled{opacity:.5}.challenge-status{min-height:25px;color:#9d629d;font-size:13px;margin:10px auto}@media(max-width:400px){.challenge-board{gap:3px}.challenge-board button{border-radius:8px}.challenge-meta span{font-size:11px}}';
document.head.appendChild(style);
const complete=(id,lv,msg,stars)=>{if(lv===3){M.win(id,msg,stars,11);return true}S.audio.collect();return false};
// Three handcrafted, verified traversable maps: 1 cell per step, K before E.
const mazes=[
['S.....','.####.','......','.####.','......','#####.','K....E'],
['S......','.#####.','.......','######.','.......','.######','K.....E'],
['S.......','.######.','........','#######.','........','.#######','........','K......E']
];
M.starmazeStart=function(){
let level=1;
const setup=()=>{
const b=mazes[level-1].map(row=>row.split(''));
this.data={b,player:[0,0],key:false,steps:0,level};
const move=(dr,dc)=>{
if(this.current!=='starmaze')return;
const d=this.data,r=d.player[0]+dr,c=d.player[1]+dc;
if(!b[r]||!b[r][c]||b[r][c]==='#'){S.audio.fail();return}
d.player=[r,c];d.steps++;S.audio.pop();
if(b[r][c]==='K'&&!d.key){d.key=true;S.audio.collect()}
if(b[r][c]==='E'&&d.key){if(complete('starmaze',level,'你穿过了三座星光迷宫，成功找到彩虹宝藏！',32))return;level++;print('<div class="win-box">🎉 这一关完成了！准备下一座迷宫……</div>');this.later(setup,450);return}
render();
};
const render=()=>{
const d=this.data;
let tiles=b.map((row,r)=>row.map((v,c)=>{
const hero=d.player[0]===r&&d.player[1]===c;
const icon=hero?'🐰':v==='#'?'☁️':v==='K'?(d.key?'·':'🔑'):v==='E'?'🚪':'·';
return '<button data-y="'+r+'" data-x="'+c+'" class="'+(v==='#'?'challenge-wall ':'')+(hero?'challenge-hero':'')+'" '+(v==='#'?'disabled':'')+'>'+icon+'</button>';
}).join('')).join('');
print(heading('陪泡泡寻找钥匙🔑，避开云朵墙，最后走到彩虹门🚪。可点相邻格子或方向键。',level,'👣 '+d.steps+' 步 · '+(d.key?'🔑 已找到钥匙':'正在找钥匙'))+
'<div class="challenge-board" style="grid-template-columns:repeat('+b[0].length+',1fr)">'+tiles+'</div>'+
'<div class="challenge-controls"><button data-d="-1,0">⬆️</button><button data-d="1,0">⬇️</button><button data-d="0,-1">⬅️</button><button data-d="0,1">➡️</button></div><p class="challenge-hint">碰到墙可以换一条路，没有时间限制。</p>');
panel().querySelectorAll('[data-d]').forEach(el=>el.onclick=()=>move(...el.dataset.d.split(',').map(Number)));
panel().querySelectorAll('[data-y]').forEach(el=>el.onclick=()=>{const y=+el.dataset.y,x=+el.dataset.x;const [r,c]=d.player;if(Math.abs(y-r)+Math.abs(x-c)===1)move(y-r,x-c)});
};
this.data.move=move;render();
};
setup();
};
const base=[1,2,3,4,3,4,1,2,2,1,4,3,4,3,2,1],symbol=['🌸','🌙','⭐','🍀'];
const masks=['1110100011001011','1100001000010110','1000001000010010'];
M.starsudokuStart=function(){
let lv=1;
const setup=()=>{
const perm=[0,1,2,3].sort(()=>Math.random()-.5);
const answer=base.map(x=>perm[x-1]+1);
const grid=answer.map((v,i)=>masks[lv-1][i]==='1'?v:0);
const locked=grid.map(Boolean);
this.data={grid,locked,answer,selected:0,hints:0};
const d=this.data;
const valid=(i,v)=>{
if(!v)return true;const row=Math.floor(i/4),col=i%4;
for(let k=0;k<4;k++){if(k!==col&&grid[row*4+k]===v)return false;if(k!==row&&grid[k*4+col]===v)return false}
const ry=row&~1,cx=col&~1;
for(let r=ry;r<ry+2;r++)for(let c=cx;c<cx+2;c++)if(r*4+c!==i&&grid[r*4+c]===v)return false;
return true;
};
const render=()=>{
if(this.current!=='starsudoku')return;
print(heading('把花、月亮、星星、四叶草填入魔法阵：每行、每列、每个2×2宫格都不能重复。',lv,'已填 '+grid.filter(Boolean).length+'/16 · 提示 '+d.hints)+
'<div class="challenge-board" style="grid-template-columns:repeat(4,1fr);max-width:340px">'+grid.map((v,i)=>
'<button data-i="'+i+'" class="'+(locked[i]?'challenge-locked ':'')+(i===d.selected?'challenge-selected':'')+'" style="'+(i%4===1?'border-right:4px solid #c89ddd;':'')+(Math.floor(i/4)===1?'border-bottom:4px solid #c89ddd;':'')+'">'+(v?symbol[v-1]:'✧')+'</button>'
).join('')+'</div><div class="challenge-options">'+symbol.map((x,i)=>'<button data-n="'+(i+1)+'">'+x+'</button>').join('')+
'<button data-n="0">✖️</button></div><div class="challenge-controls"><button id="sudokuHelp" class="small-button">💡 提示一格</button><button id="sudokuDone" class="primary-button">✅ 检查</button></div><div id="sudokuState" class="challenge-status">先点击一个空格，再点击下面的图案。</div>');
panel().querySelectorAll('[data-i]').forEach(btn=>btn.onclick=()=>{d.selected=+btn.dataset.i;S.audio.pop();render()});
panel().querySelectorAll('[data-n]').forEach(btn=>btn.onclick=()=>{const i=d.selected;if(locked[i]){document.getElementById('sudokuState').textContent='淡紫色是已经固定的提示格。';return}grid[i]=+btn.dataset.n;S.audio.pop();render()});
document.getElementById('sudokuHelp').onclick=()=>{const i=grid.findIndex((v,k)=>!locked[k]&&v!==answer[k]);if(i<0)return;grid[i]=answer[i];locked[i]=true;d.hints++;S.audio.collect();render()};
document.getElementById('sudokuDone').onclick=()=>{
if(grid.every(Boolean)&&grid.every((v,i)=>valid(i,v))){if(complete('starsudoku',lv,'三座魔法阵全部恢复了彩虹魔力！',34))return;lv++;print('<div class="win-box">✨ 推理成功！下一关会更复杂。</div>');this.later(setup,450)}
else{S.audio.fail();document.getElementById('sudokuState').textContent='还有空格或重复的图案，仔细再观察一下！'}
};
};
render();
};
setup();
};
const icons=['🌸','🌙','🍀','⭐','🍓','🦋'];
M.elfcodeStart=function(){
let lv=1;
const setup=()=>{
const len=lv===1?3:4,max=lv===1?9:lv===2?8:7;
const secret=[0,1,2,3,4,5].sort(()=>Math.random()-.5).slice(0,len);
this.data={guess:[],history:[],secret,len,max,lv};const d=this.data;
const render=()=>{
if(this.current!=='elfcode')return;
print(heading('破解精灵的秘密密码：图案不能重复。粉心表示图案及位置都对，黄心表示图案对但位置不对。',lv,'还可尝试 '+(max-d.history.length)+' 次')+
'<div class="challenge-options">'+Array.from({length:len},(_,i)=>'<span class="challenge-code">'+(d.guess[i]===undefined?'❔':icons[d.guess[i]])+'</span>').join('')+'</div>'+
'<div class="challenge-options">'+icons.map((v,i)=>'<button data-v="'+i+'" '+(d.guess.includes(i)?'disabled':'')+'>'+v+'</button>').join('')+'</div>'+
'<div class="challenge-controls"><button id="codeUndo">↩️ 撤销</button><button id="codeClear">🔄 清空</button><button id="codeVerify" '+(d.guess.length!==len?'disabled':'')+'>🪄 验证</button></div>'+
'<div class="challenge-hint">💗 位置正确　💛 图案正确但位置不同；线索不按位置排列。</div>'+
'<div class="challenge-history">'+d.history.slice().reverse().map(x=>'<div>'+x.guess.map(n=>icons[n]).join(' ')+'　<small>💗'+x.exact+'　💛'+x.near+'</small></div>').join('')+'</div>');
panel().querySelectorAll('[data-v]').forEach(btn=>btn.onclick=()=>{let v=+btn.dataset.v;if(d.guess.length<len&&!d.guess.includes(v)){d.guess.push(v);S.audio.pop();render()}});
document.getElementById('codeUndo').onclick=()=>{d.guess.pop();render()};
document.getElementById('codeClear').onclick=()=>{d.guess=[];render()};
document.getElementById('codeVerify').onclick=()=>{
if(d.guess.length!==len)return;
const exact=d.guess.filter((v,i)=>v===secret[i]).length;
const near=d.guess.filter(v=>secret.includes(v)).length-exact;
d.history.push({guess:d.guess.slice(),exact,near});d.guess=[];
if(exact===len){if(complete('elfcode',lv,'所有精灵密码都被破解，你获得了彩虹研究员称号！',36))return;lv++;print('<div class="win-box">🎊 密码正确！下一关更难啦。</div>');this.later(setup,450);return}
if(d.history.length>=max){print(heading('尝试次数用完啦！',lv,'可以重新挑战')+'<div class="win-box"><p>正确密码：'+secret.map(v=>icons[v]).join(' ')+'</p><button class="primary-button" id="codeRetry">🔄 再试一次</button></div>');document.getElementById('codeRetry').onclick=setup;S.audio.fail();return}
S.audio.pop();render();
};
};render();
};
setup();
};
const open=M.open;M.open=function(id){const out=open.call(this,id);if(defs.some(g=>g.id===id)&&S.game?.state?.settings?.speech!==false){
// Use only previously bundled recorded female-voice lines until new F5-TTS recordings land.
// No system TTS substitution is ever used.
const ref={starmaze:'星光迷宫探险。丁一一，先找到金钥匙，再带着泡泡走向彩虹门。每一关的路线都会更复杂，仔细想一想再出发！',
starsudoku:'魔法数独学院。每一行、每一列和每一个小方格，都需要不同的魔法图案。先观察，再推理，你一定能找到答案！',
elfcode:'精灵密码实验室。猜一猜隐藏的精灵密码。粉色爱心代表位置和图案都正确，黄色爱心代表只有图案正确。根据线索不断缩小范围吧！'};
S.audio.speak(ref[id],{role:'bubble'});
}return out;};
window.StarwhimAdvancedGames={version:1,ids:defs.map(x=>x.id)};
})();
