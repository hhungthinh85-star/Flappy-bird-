
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Flappy Bird HD 2.1",
    page_icon="🐤",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@800;900;1000&display=swap');
.stApp {
    background: linear-gradient(#d7f6ff, #8bdcff);
    font-family: Nunito, sans-serif;
}
header, footer, #MainMenu {visibility: hidden}
.block-container {padding:.4rem .4rem .2rem;max-width:1000px}
h1 {text-align:center;color:#17466d;font-weight:1000;margin:0}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🐤 FLAPPY BIRD HD 2.1</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#356681;font-weight:900'>"
    "Chọn độ khó • Né ống • Tránh lửa!</p>",
    unsafe_allow_html=True
)

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;overflow:hidden;font-family:system-ui,sans-serif;background:#8bdcff;touch-action:manipulation}
#wrap{position:relative;width:100%;height:min(76vh,720px);min-height:430px;overflow:hidden;border-radius:20px;border:4px solid white;box-shadow:0 12px 32px #17466d35}
canvas{width:100%;height:100%;display:block;touch-action:manipulation}
#hud{position:absolute;top:10px;left:10px;right:10px;display:flex;justify-content:space-between;align-items:center;pointer-events:none;gap:6px}
.pill{background:#ffffffdf;border:2px solid white;border-radius:12px;padding:6px 10px;font-size:12px;font-weight:900;color:#17466d}
#sound{pointer-events:auto;border:0;border-radius:12px;padding:7px;background:#ffffffed;font-size:18px}
#score{position:absolute;top:8px;left:50%;transform:translateX(-50%);font-size:clamp(34px,7vw,54px);font-weight:1000;color:white;-webkit-text-stroke:2px #17466d;text-shadow:0 4px #17466d;pointer-events:none}
#overlay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:12px;background:#16476720;overflow:auto}
.panel{width:min(94%,380px);text-align:center;background:linear-gradient(#fffef5,#fff0c9);border:4px solid white;border-radius:23px;padding:18px 15px;box-shadow:0 7px 0 #d49b4c,0 14px 28px #17466d35;color:#17466d}
.panel h2{margin:0 0 7px;font-size:clamp(26px,6vw,35px);font-weight:1000;color:#f28c28;text-shadow:0 2px #ffe6a7}
.panel p{font-size:14px;font-weight:800;line-height:1.4;color:#476b7d;margin:8px 0 13px}
.modes{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0}
.mode{border:3px solid #d5e6e9;border-radius:13px;padding:10px 4px;background:white;color:#28516a;font-weight:1000;cursor:pointer}
.mode.selected{border-color:#59c738;background:#e9ffd9;box-shadow:0 3px 0 #72c951}
.mode small{display:block;font-size:10px;font-weight:800;margin-top:3px}
#startBtn{border:0;border-radius:14px;padding:12px 25px;background:linear-gradient(#b5f36a,#65c72c);box-shadow:0 5px 0 #3d9824;color:#164b20;font-size:18px;font-weight:1000;cursor:pointer}
#startBtn:active{transform:translateY(3px);box-shadow:0 2px #3d9824}
.small{font-size:11px!important;margin-bottom:0!important}
@media(max-width:520px){#wrap{height:70vh;min-height:430px;border-radius:15px}.pill{font-size:10px;padding:6px 7px}.panel{padding:15px 12px}.mode{padding:8px 3px}}
</style>
</head>
<body>
<div id="wrap">
<canvas id="game"></canvas>
<div id="hud">
 <div class="pill">🏆 Kỷ lục: <span id="best">0</span></div>
 <div class="pill" id="modeLabel">EASY</div>
 <button id="sound">🔊</button>
</div>
<div id="score">0</div>
<div id="overlay">
 <div class="panel" id="panel">
  <h2>FLAPPY BIRD</h2>
  <p>Chọn chế độ chơi của bạn!</p>
  <div class="modes">
   <button class="mode selected" data-mode="easy">🟢 EASY<small>Dễ • Khe rộng</small></button>
   <button class="mode" data-mode="medium">🔵 MEDIUM<small>Trung bình</small></button>
   <button class="mode" data-mode="hard">🔥 HARD<small>Ống thép phun lửa</small></button>
   <button class="mode" data-mode="impossible">💀 IMPOSSIBLE<small>Cực khó • Nhiều lửa</small></button>
  </div>
  <button id="startBtn">▶ BẮT ĐẦU</button>
  <p class="small">Chạm màn hình hoặc nhấn SPACE để bay</p>
 </div>
</div>
</div>
<script>
(()=>{
"use strict";

const canvas=document.getElementById("game");
const ctx=canvas.getContext("2d");
const wrap=document.getElementById("wrap");
const overlay=document.getElementById("overlay");
const scoreEl=document.getElementById("score");
const bestEl=document.getElementById("best");
const modeLabel=document.getElementById("modeLabel");
const soundBtn=document.getElementById("sound");

let W=0,H=0,dpr=1,state="menu",mode="easy";
let score=0,best=0,world=0,last=0;
let bird=null,pipes=[],particles=[],clouds=[];
let soundOn=true,audioCtx=null;

const configs={
 easy:{gap:.32,spacing:.72,speed:.0049,fire:0,label:"EASY"},
 medium:{gap:.29,spacing:.68,speed:.0055,fire:0,label:"MEDIUM"},
 hard:{gap:.28,spacing:.68,speed:.0059,fire:.35,label:"HARD"},
 impossible:{gap:.30,spacing:.80,speed:.0062,fire:.58,label:"IMPOSSIBLE"}
};

try{best=Number(localStorage.getItem("flappy-hd-best")||0)}catch(e){}
bestEl.textContent=best;

function rand(a,b){return a+Math.random()*(b-a)}

function resize(){
 const r=wrap.getBoundingClientRect();
 W=Math.max(280,r.width);
 H=Math.max(430,r.height);
 dpr=Math.min(window.devicePixelRatio||1,2);
 canvas.width=Math.round(W*dpr);
 canvas.height=Math.round(H*dpr);
 ctx.setTransform(dpr,0,0,dpr,0,0);
 clouds=Array.from({length:7},(_,i)=>({
  x:i*W/6,y:rand(35,H*.42),s:rand(.55,1.05)
 }));
 if(!bird)resetBird();
 draw();
}

function resetBird(){
 bird={
  x:W*.27,y:H*.42,vy:0,
  r:Math.max(14,Math.min(19,W*.045)),
  rot:0,wing:0
 };
}

function makePipe(x){
 const c=configs[mode];
 const ground=H*.91;
 const gap=Math.max(145,Math.min(220,H*c.gap));

 // Tạo khe hở trong vùng an toàn, tránh ống quá sát trần/sàn.
 const minCenter=70+gap/2;
 const maxCenter=Math.max(minCenter,ground-70-gap/2);
 const center=rand(minCenter,maxCenter);

 // Impossible vẫn có nhiều ống lửa, nhưng không phải ống nào cũng có lửa.
 const hot=Math.random()<c.fire;

 return {
  x,center,gap,
  w:Math.max(55,Math.min(72,W*.15)),
  passed:false,
  metal:hot,
  fire:hot,
  phase:Math.random()*6.28
 };
}

function resetGame(){
 score=0;
 world=0;
 particles=[];
 pipes=[];
 resetBird();
 scoreEl.textContent="0";

 // Ống đầu tiên luôn đủ xa để người chơi chuẩn bị.
 const spacing=W*configs[mode].spacing;
 pipes.push(makePipe(W*.90));
 pipes.push(makePipe(W*.90+spacing));
 pipes.push(makePipe(W*.90+spacing*2));
}

function beep(freq=650,dur=.07){
 if(!soundOn)return;
 try{
  audioCtx=audioCtx||new(window.AudioContext||window.webkitAudioContext)();
  if(audioCtx.state==="suspended")audioCtx.resume();
  const o=audioCtx.createOscillator();
  const g=audioCtx.createGain();
  o.type="sine";
  o.frequency.value=freq;
  g.gain.setValueAtTime(.04,audioCtx.currentTime);
  g.gain.exponentialRampToValueAtTime(.001,audioCtx.currentTime+dur);
  o.connect(g);g.connect(audioCtx.destination);
  o.start();o.stop(audioCtx.currentTime+dur);
 }catch(e){}
}

function burst(x,y,n,color){
 for(let i=0;i<n;i++){
  particles.push({
   x,y,vx:rand(-2.6,2.6),vy:rand(-2.8,2.3),
   life:1,size:rand(2,5),color
  });
 }
}

function flap(){
 if(state!=="playing")return;
 bird.vy=-H*.012;
 bird.wing=1;
 beep(740,.05);
 burst(bird.x-bird.r*.6,bird.y+4,5,"#fff4a0");
}

function startGame(){
 resetGame();
 state="playing";
 overlay.style.display="none";
 last=performance.now();
 flap();
}

function showMenu(){
 state="menu";
 overlay.style.display="flex";
 overlay.innerHTML=`
 <div class="panel">
  <h2>FLAPPY BIRD</h2>
  <p>Chọn chế độ chơi của bạn!</p>
  <div class="modes">
   <button class="mode ${mode==="easy"?"selected":""}" data-mode="easy">🟢 EASY<small>Dễ • Khe rộng</small></button>
   <button class="mode ${mode==="medium"?"selected":""}" data-mode="medium">🔵 MEDIUM<small>Trung bình</small></button>
   <button class="mode ${mode==="hard"?"selected":""}" data-mode="hard">🔥 HARD<small>Ống thép phun lửa</small></button>
   <button class="mode ${mode==="impossible"?"selected":""}" data-mode="impossible">💀 IMPOSSIBLE<small>Cực khó • Nhiều lửa</small></button>
  </div>
  <button id="startBtn">▶ BẮT ĐẦU</button>
  <p class="small">Chạm màn hình hoặc nhấn SPACE để bay</p>
 </div>`;

 overlay.querySelectorAll(".mode").forEach(b=>{
  b.addEventListener("click",e=>{
   e.stopPropagation();
   mode=b.dataset.mode;
   modeLabel.textContent=configs[mode].label;
   showMenu();
  });
 });
 document.getElementById("startBtn").addEventListener("click",e=>{
  e.stopPropagation();
  startGame();
 });
}

function endGame(){
 if(state!=="playing")return;
 state="over";
 beep(170,.18);

 if(score>best){
  best=score;
  bestEl.textContent=String(best);
  try{localStorage.setItem("flappy-hd-best",String(best))}catch(e){}
 }

 overlay.style.display="flex";
 overlay.innerHTML=`
 <div class="panel">
  <h2>GAME OVER</h2>
  <p>Chế độ: <b>${configs[mode].label}</b><br>
  Điểm: <b>${score}</b><br>🏆 Kỷ lục: <b>${best}</b></p>
  <button id="startBtn">↻ CHƠI LẠI</button><br>
  <button id="menuBtn" style="margin-top:12px;border:0;border-radius:12px;padding:9px 15px;background:#d8efff;color:#17466d;font-weight:900">☰ MENU</button>
 </div>`;

 document.getElementById("startBtn").addEventListener("click",e=>{
  e.stopPropagation();startGame();
 });
 document.getElementById("menuBtn").addEventListener("click",e=>{
  e.stopPropagation();showMenu();
 });
}

function cloud(x,y,s){
 ctx.save();
 ctx.translate(x,y);ctx.scale(s,s);
 ctx.fillStyle="#ffffffd9";
 ctx.beginPath();
 ctx.ellipse(0,5,32,13,0,0,Math.PI*2);
 ctx.ellipse(-17,0,16,14,0,0,Math.PI*2);
 ctx.ellipse(1,-8,20,20,0,0,Math.PI*2);
 ctx.ellipse(20,1,16,13,0,0,Math.PI*2);
 ctx.fill();ctx.restore();
}

function background(dt){
 const sky=ctx.createLinearGradient(0,0,0,H);
 sky.addColorStop(0,"#35bdff");
 sky.addColorStop(.58,"#a7eaff");
 sky.addColorStop(1,"#f3fdff");
 ctx.fillStyle=sky;ctx.fillRect(0,0,W,H);

 const sun=ctx.createRadialGradient(W*.78,H*.15,3,W*.78,H*.15,85);
 sun.addColorStop(0,"#fff9b9");
 sun.addColorStop(1,"rgba(255,249,185,0)");
 ctx.fillStyle=sun;
 ctx.fillRect(W*.78-85,H*.15-85,170,170);

 clouds.forEach(c=>{
  cloud(c.x,c.y,c.s);
  if(state==="playing")c.x-=dt*.012*c.s;
  if(c.x<-75)c.x=W+75;
 });

 ctx.fillStyle="#a1e4a5";
 ctx.beginPath();ctx.moveTo(0,H*.75);
 for(let x=0;x<=W+20;x+=16)
  ctx.lineTo(x,H*.69+Math.sin(x*.012+world*.0002)*H*.03);
 ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.fill();

 ctx.fillStyle="#61cd89";
 ctx.beginPath();ctx.moveTo(0,H*.84);
 for(let x=0;x<=W+20;x+=16)
  ctx.lineTo(x,H*.79+Math.sin(x*.018+world*.0003)*H*.03);
 ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.fill();

 for(let i=0;i<Math.ceil(W/44)+3;i++){
  const x=i*44-(world*.1%44);
  const bh=28+(i*37%52);
  ctx.fillStyle=["#9acfe0","#b4dfec","#7fbcd6"][i%3];
  ctx.fillRect(x,H*.89-bh,35,bh);
  ctx.fillStyle="rgba(255,255,255,.65)";
  for(let yy=H*.89-bh+8;yy<H*.88;yy+=12)
   for(let xx=x+7;xx<x+29;xx+=12)ctx.fillRect(xx,yy,4,5);
 }

 ctx.fillStyle="#d8f19b";ctx.fillRect(0,H*.91,W,H*.09);
 ctx.fillStyle="#67c941";ctx.fillRect(0,H*.91,W,8);
 for(let x=-(world%28);x<W;x+=28){
  ctx.fillStyle="#a5e765";
  ctx.beginPath();ctx.moveTo(x,H*.91);ctx.lineTo(x+10,H*.91-5);
  ctx.lineTo(x+20,H*.91);ctx.fill();
 }
 ctx.fillStyle="#e8c77c";ctx.fillRect(0,H*.935,W,H*.065);
 ctx.fillStyle="rgba(181,127,53,.24)";
 for(let x=-(world%34);x<W;x+=34)ctx.fillRect(x,H*.96,17,3);
}

function metalGradient(x,w){
 const g=ctx.createLinearGradient(x,0,x+w,0);
 g.addColorStop(0,"#424e5b");
 g.addColorStop(.2,"#c8d5df");
 g.addColorStop(.45,"#778895");
 g.addColorStop(.7,"#e2ebf0");
 g.addColorStop(1,"#4a5864");
 return g;
}

function flame(x,y,dir,phase){
 const flick=Math.sin(world*.035+phase)*5;
 ctx.save();ctx.translate(x,y);ctx.scale(1,dir);
 const g=ctx.createLinearGradient(0,0,0,34+flick);
 g.addColorStop(0,"#fff48b");
 g.addColorStop(.4,"#ffb21e");
 g.addColorStop(1,"#ff4c18");
 ctx.fillStyle=g;
 ctx.beginPath();
 ctx.moveTo(-10,0);
 ctx.quadraticCurveTo(-18,12,-7,24+flick);
 ctx.lineTo(0,34+flick);ctx.lineTo(7,22);
 ctx.quadraticCurveTo(18,11,10,0);
 ctx.closePath();ctx.fill();
 ctx.fillStyle="#fff9b1";
 ctx.beginPath();ctx.moveTo(-4,2);
 ctx.quadraticCurveTo(-7,13,0,22);
 ctx.quadraticCurveTo(7,12,4,2);ctx.fill();
 ctx.restore();
}

function warning(x,y,w){
 ctx.save();
 ctx.fillStyle="#ffcf35";ctx.strokeStyle="#262c32";ctx.lineWidth=2;
 ctx.beginPath();
 ctx.moveTo(x+w/2,y);ctx.lineTo(x+w/2+13,y+23);
 ctx.lineTo(x+w/2-13,y+23);ctx.closePath();
 ctx.fill();ctx.stroke();
 ctx.fillStyle="#222";ctx.font="bold 17px sans-serif";
 ctx.textAlign="center";ctx.fillText("!",x+w/2,y+18);
 ctx.restore();
}

function drawPipe(p){
 const top=p.center-p.gap/2;
 const bot=p.center+p.gap/2;
 const ground=H*.91,cap=17,x=p.x,w=p.w;
 const grad=p.metal?metalGradient(x,w):(()=>{
  const g=ctx.createLinearGradient(x,0,x+w,0);
  g.addColorStop(0,"#08762a");g.addColorStop(.2,"#51dc50");
  g.addColorStop(.55,"#29bd3d");g.addColorStop(1,"#08732a");
  return g;
 })();

 ctx.fillStyle=grad;
 ctx.fillRect(x,0,w,Math.max(0,top));
 ctx.fillRect(x-5,top-cap,w+10,cap);
 ctx.fillRect(x,bot,w,Math.max(0,ground-bot));
 ctx.fillRect(x-5,bot,w+10,cap);

 if(p.metal){
  ctx.strokeStyle="#263541";ctx.lineWidth=2;
  ctx.strokeRect(x,0,w,top);
  ctx.strokeRect(x-5,top-cap,w+10,cap);
  ctx.strokeRect(x,bot,w,ground-bot);
  ctx.strokeRect(x-5,bot,w+10,cap);

  ctx.fillStyle="#f1f5f7";
  for(let yy=30;yy<top-10;yy+=38){
   ctx.beginPath();ctx.arc(x+w/2,yy,2.4,0,Math.PI*2);ctx.fill();
  }
  for(let yy=bot+28;yy<ground-10;yy+=38){
   ctx.beginPath();ctx.arc(x+w/2,yy,2.4,0,Math.PI*2);ctx.fill();
  }
  warning(x,Math.max(28,top-cap-25),w);
 }else{
  ctx.fillStyle="rgba(255,255,255,.25)";
  ctx.fillRect(x+8,0,6,Math.max(0,top-cap));
  ctx.fillRect(x+8,bot+cap,6,Math.max(0,ground-bot-cap));
  ctx.strokeStyle="#176e2f";ctx.lineWidth=1.5;
  ctx.strokeRect(x,0,w,top);
  ctx.strokeRect(x-5,top-cap,w+10,cap);
  ctx.strokeRect(x,bot,w,ground-bot);
  ctx.strokeRect(x-5,bot,w+10,cap);
 }

 if(p.fire){
  const active=(Math.sin(world*.025+p.phase)+1)/2;
  if(active>.48){
   flame(x+w/2,top+cap,1,p.phase);
   flame(x+w/2,bot-cap,-1,p.phase+2);
  }
 }
}

function drawBird(){
 ctx.save();ctx.translate(bird.x,bird.y);ctx.rotate(bird.rot);
 const r=bird.r;

 const glow=ctx.createRadialGradient(0,0,r*.2,0,0,r*1.8);
 glow.addColorStop(0,"rgba(255,248,169,.33)");
 glow.addColorStop(1,"rgba(255,248,169,0)");
 ctx.fillStyle=glow;ctx.beginPath();ctx.arc(0,0,r*1.8,0,Math.PI*2);ctx.fill();

 for(let i=0;i<3;i++){
  ctx.fillStyle=["#ff9f22","#ffbd2e","#ffdb46"][i];
  ctx.beginPath();ctx.ellipse(-r-5-i*2,i*3-2,r*.35,r*.13,-.35,0,Math.PI*2);ctx.fill();
 }

 const body=ctx.createLinearGradient(-r,-r,r,r);
 body.addColorStop(0,"#fffda1");body.addColorStop(.3,"#ffe64b");
 body.addColorStop(.68,"#ffc52b");body.addColorStop(1,"#ed8e19");
 ctx.fillStyle=body;
 ctx.beginPath();ctx.ellipse(0,0,r*1.12,r*.98,0,0,Math.PI*2);ctx.fill();
 ctx.strokeStyle="#d18a1e";ctx.lineWidth=1.7;ctx.stroke();

 ctx.fillStyle="#fff2b6";
 ctx.beginPath();ctx.ellipse(r*.12,r*.38,r*.63,r*.43,.1,0,Math.PI*2);ctx.fill();

 ctx.strokeStyle="#e9b337";ctx.lineWidth=1.2;
 for(let i=0;i<3;i++){
  ctx.beginPath();ctx.moveTo(-r*.25+i*5,r*.38);
  ctx.quadraticCurveTo(-r*.1+i*5,r*.47,r*.04+i*5,r*.38);
  ctx.stroke();
 }

 ctx.save();ctx.translate(-r*.28,3);
 ctx.rotate(Math.sin(bird.wing*5)*.48+(bird.vy>0?.2:-.15));
 ctx.fillStyle="#e99a20";ctx.beginPath();
 ctx.ellipse(-2,3,r*.53,r*.35,-.3,0,Math.PI*2);ctx.fill();
 ctx.fillStyle="#ffbd32";ctx.beginPath();
 ctx.ellipse(0,0,r*.42,r*.27,-.35,0,Math.PI*2);ctx.fill();
 ctx.strokeStyle="#d78c1e";ctx.lineWidth=1.2;ctx.stroke();
 ctx.strokeStyle="#ffe77c";ctx.beginPath();
 ctx.moveTo(-r*.22,0);ctx.lineTo(r*.12,3);ctx.stroke();
 ctx.restore();

 ctx.fillStyle="#ff9d27";
 ctx.beginPath();ctx.moveTo(-r*.12,-r*.77);
 ctx.quadraticCurveTo(-r*.18,-r*1.3,r*.06,-r*.92);
 ctx.quadraticCurveTo(r*.18,-r*1.25,r*.24,-r*.7);ctx.fill();

 ctx.fillStyle="#ff998b";
 ctx.beginPath();ctx.ellipse(r*.57,r*.23,r*.21,r*.14,0,0,Math.PI*2);ctx.fill();

 ctx.fillStyle="white";
 ctx.beginPath();ctx.ellipse(r*.45,-r*.28,r*.29,r*.35,0,0,Math.PI*2);ctx.fill();
 ctx.strokeStyle="#9c671d";ctx.lineWidth=1.2;ctx.stroke();

 ctx.fillStyle="#1b3447";ctx.beginPath();
 ctx.arc(r*.53,-r*.25,r*.145,0,Math.PI*2);ctx.fill();
 ctx.fillStyle="white";ctx.beginPath();
 ctx.arc(r*.58,-r*.33,r*.06,0,Math.PI*2);ctx.fill();

 const beak=ctx.createLinearGradient(r*.7,0,r*1.55,0);
 beak.addColorStop(0,"#ffb02d");beak.addColorStop(1,"#ff6324");
 ctx.fillStyle=beak;ctx.beginPath();
 ctx.moveTo(r*.77,-1);ctx.lineTo(r*1.52,3);ctx.lineTo(r*.82,8);
 ctx.closePath();ctx.fill();
 ctx.strokeStyle="#c8531a";ctx.lineWidth=1.2;ctx.stroke();

 ctx.restore();
}

function draw(){
 if(!W||!H||!bird)return;
 background(0);
 pipes.forEach(drawPipe);
 particles.forEach(p=>{
  ctx.globalAlpha=Math.max(0,p.life);
  ctx.fillStyle=p.color;
  ctx.beginPath();ctx.arc(p.x,p.y,p.size*p.life,0,Math.PI*2);ctx.fill();
 });
 ctx.globalAlpha=1;
 drawBird();
}

function pipeCollision(p){
 const r=bird.r*.74,bx=bird.x,by=bird.y;
 const top=p.center-p.gap/2,bot=p.center+p.gap/2;

 if(bx+r>p.x-5&&bx-r<p.x+p.w+5&&
    (by-r<top||by+r>bot))return true;

 // Chỉ vùng lửa đang hoạt động mới gây va chạm.
 if(p.fire){
  const active=(Math.sin(world*.025+p.phase)+1)/2;
  if(active>.48&&bx+r>p.x+8&&bx-r<p.x+p.w-8){
   const topFlame=top+17+25;
   const bottomFlame=bot-17-25;
   if((by+r>top+17&&by-r<topFlame)||
      (by+r>bottomFlame&&by-r<bot-17))return true;
  }
 }
 return false;
}

function update(ts){
 const dt=last?Math.min(32,ts-last):16;
 last=ts;

 if(state==="playing"){
  world+=dt;
  const step=dt/16.67;

  bird.vy+=H*.00072*step;
  bird.vy=Math.min(bird.vy,H*.013);
  bird.y+=bird.vy*step;
  bird.rot=Math.max(-.45,Math.min(.9,bird.vy/(H*.025)));
  bird.wing+=dt*.012;

  const speed=Math.max(2.8,W*configs[mode].speed)*step;
  pipes.forEach(p=>{
   p.x-=speed;
   if(!p.passed&&p.x+p.w<bird.x){
    p.passed=true;
    score++;
    scoreEl.textContent=String(score);
    beep(980,.07);
    burst(bird.x,bird.y,9,"#fff5ad");
   }
  });

  pipes=pipes.filter(p=>p.x+p.w>-30);

  // Khoảng cách riêng từng chế độ. IMPOSSIBLE không chồng ống.
  const spacing=W*configs[mode].spacing;
  while(pipes.length<4){
   const lastPipe=pipes[pipes.length-1];
   pipes.push(makePipe(lastPipe?lastPipe.x+spacing:W+100));
  }

  particles.forEach(p=>{
   p.x+=p.vx*step;p.y+=p.vy*step;p.life-=dt*.002;
  });
  particles=particles.filter(p=>p.life>0);

  if(pipes.some(pipeCollision)||
     bird.y+bird.r>H*.91||
     bird.y-bird.r<0){
   endGame();
  }
 }

 draw();
 requestAnimationFrame(update);
}

wrap.addEventListener("pointerdown",e=>{
 if(e.target.closest("button"))return;
 if(state==="playing"){e.preventDefault();flap();}
});

document.addEventListener("keydown",e=>{
 if(e.code==="Space"||e.code==="ArrowUp"){
  e.preventDefault();
  if(state==="menu")startGame();
  else if(state==="playing")flap();
  else if(state==="over")startGame();
 }
});

document.getElementById("startBtn").addEventListener("click",e=>{
 e.stopPropagation();startGame();
});

document.querySelectorAll(".mode").forEach(b=>{
 b.addEventListener("click",e=>{
  e.stopPropagation();
  mode=b.dataset.mode;
  modeLabel.textContent=configs[mode].label;
  document.querySelectorAll(".mode").forEach(m=>{
   m.classList.toggle("selected",m.dataset.mode===mode);
  });
 });
});

soundBtn.addEventListener("click",e=>{
 e.stopPropagation();
 soundOn=!soundOn;
 soundBtn.textContent=soundOn?"🔊":"🔇";
 if(soundOn)beep();
});

window.addEventListener("resize",resize);
resize();
resetBird();
requestAnimationFrame(update);
})();
</script>
</body>
</html>
"""

components.html(game_html, height=740, scrolling=False)
st.caption(
    "Điện thoại: chạm để bay. Máy tính: nhấn SPACE. "
    "Sau khi dán code, nhấn Commit changes trên GitHub."
)
