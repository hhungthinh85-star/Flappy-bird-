
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Flappy Bird HD",
    page_icon="🐤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}
.stApp {
    background: linear-gradient(180deg, #c5f1ff, #83d9ff);
}
header, footer, #MainMenu {
    visibility: hidden;
}
.block-container {
    padding: .5rem .5rem .2rem;
    max-width: 1000px;
}
h1 {
    text-align: center;
    color: #17466d;
    font-weight: 1000;
    margin: 0;
}
.hint {
    text-align: center;
    color: #356681;
    font-weight: 800;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🐤 FLAPPY BIRD HD</h1>", unsafe_allow_html=True)
st.markdown(
    '<div class="hint">Chạm để bay • Né ống • Chinh phục kỷ lục!</div>',
    unsafe_allow_html=True
)

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
*{box-sizing:border-box}
html,body{
 margin:0;width:100%;height:100%;overflow:hidden;
 background:#83d9ff;
 font-family:system-ui,sans-serif;
 touch-action:manipulation
}
#wrap{
 position:relative;width:100%;height: min(76vh,720px);
 min-height:420px;overflow:hidden;border-radius:22px;
 border:4px solid white;
 box-shadow:0 14px 34px rgba(17,76,120,.25);
 background:#87dcff
}
canvas{display:block;width:100%;height:100%;touch-action:manipulation}
#hud{
 position:absolute;top:12px;left:12px;right:12px;
 display:flex;justify-content:space-between;
 pointer-events:none
}
.pill{
 background:rgba(255,255,255,.9);
 border:2px solid white;border-radius:13px;
 padding:7px 11px;color:#17466d;font-weight:900;
 box-shadow:0 3px 0 rgba(23,70,109,.12);font-size:13px
}
#sound{
 pointer-events:auto;border:0;cursor:pointer;
 background:rgba(255,255,255,.92);border-radius:12px;
 padding:7px 10px;font-size:18px
}
#score{
 position:absolute;top:12px;left:50%;
 transform:translateX(-50%);
 font-size:clamp(36px,7vw,55px);font-weight:1000;
 color:white;-webkit-text-stroke:2px #17466d;
 text-shadow:0 4px #17466d;pointer-events:none
}
#overlay{
 position:absolute;inset:0;display:flex;
 align-items:center;justify-content:center;padding:18px;
 background:rgba(16,62,94,.13)
}
.panel{
 width:min(90%,350px);text-align:center;
 background:linear-gradient(#fffdf1,#fff0c6);
 border:4px solid white;border-radius:24px;
 padding:23px 18px 19px;
 box-shadow:0 8px 0 #d79c4d,0 18px 30px #17466d33;
 color:#17466d
}
.panel h2{
 margin:0 0 10px;font-size:clamp(26px,6vw,36px);
 line-height:1.1;font-weight:1000;color:#f28c28;
 text-shadow:0 2px #ffe4a2
}
.panel p{margin:8px 0 17px;font-weight:800;color:#476b7d;line-height:1.45}
#startBtn{
 border:0;border-radius:15px;padding:13px 26px;
 background:linear-gradient(#b5f36a,#65c72c);
 box-shadow:0 5px 0 #3d9824;color:#164b20;
 font-size:18px;font-weight:1000;cursor:pointer
}
#startBtn:active{transform:translateY(3px);box-shadow:0 2px #3d9824}
.small{font-size:12px!important;color:#6e8790!important;margin-bottom:0!important}
@media(max-width:520px){
 #wrap{height:70vh;min-height:420px;border-radius:16px;border-width:3px}
 .pill{font-size:11px;padding:6px 8px}
 .panel{padding:20px 15px}
}
</style>
</head>
<body>
<div id="wrap">
 <canvas id="game"></canvas>
 <div id="hud">
  <div class="pill">🏆 Kỷ lục: <span id="best">0</span></div>
  <button id="sound" aria-label="Âm thanh">🔊</button>
 </div>
 <div id="score">0</div>
 <div id="overlay">
  <div class="panel">
   <h2>FLAPPY BIRD</h2>
   <p>Vỗ cánh bay lên, né những chiếc ống và chinh phục kỷ lục!</p>
   <button id="startBtn">▶ BẮT ĐẦU</button>
   <p class="small">Chạm màn hình hoặc nhấn SPACE để bay</p>
  </div>
 </div>
</div>

<script>
(() => {
"use strict";

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const wrap = document.getElementById("wrap");
const overlay = document.getElementById("overlay");
const scoreEl = document.getElementById("score");
const bestEl = document.getElementById("best");
const soundBtn = document.getElementById("sound");

let W=0,H=0,dpr=1;
let state="menu"; // menu, playing, over
let score=0,best=0,world=0,lastTime=0;
let bird=null,pipes=[],particles=[],clouds=[];
let soundOn=true,audioCtx=null;
let gameToken=0;

try {
 best=Number(localStorage.getItem("flappy-hd-best")||0);
} catch(e) { best=0; }
bestEl.textContent=best;

function random(min,max){return min+Math.random()*(max-min)}

function resize(){
 const rect=wrap.getBoundingClientRect();
 W=Math.max(280,rect.width);
 H=Math.max(420,rect.height);
 dpr=Math.min(window.devicePixelRatio||1,2);
 canvas.width=Math.round(W*dpr);
 canvas.height=Math.round(H*dpr);
 ctx.setTransform(dpr,0,0,dpr,0,0);

 clouds=Array.from({length:7},(_,i)=>({
  x:i*W/6+random(-20,20),
  y:random(35,H*.43),
  s:random(.55,1.05),
  speed:random(.008,.018)
 }));

 if(!bird) resetBird();
 draw();
}

function resetBird(){
 bird={
  x:W*.27,y:H*.43,vy:0,
  r:Math.max(13,Math.min(18,W*.043)),
  rot:0,wing:0
 };
}

function makePipe(x){
 const gap=Math.max(155,Math.min(195,H*.29));
 const topMargin=75;
 const bottomMargin=H*.91-75;
 const center=random(topMargin+gap/2,bottomMargin-gap/2);
 return {
  x,center,gap,
  w:Math.max(54,Math.min(70,W*.15)),
  passed:false
 };
}

function resetGame(){
 score=0;
 scoreEl.textContent="0";
 pipes=[];
 particles=[];
 world=0;
 resetBird();

 // Hai ống đầu cách nhau đủ xa, không đặt ống ngay trên chim.
 pipes.push(makePipe(W*.78));
 pipes.push(makePipe(W*1.42));
 pipes.push(makePipe(W*2.06));
}

function beep(freq=650,duration=.07){
 if(!soundOn)return;
 try{
  audioCtx=audioCtx||new(window.AudioContext||window.webkitAudioContext)();
  if(audioCtx.state==="suspended")audioCtx.resume();
  const osc=audioCtx.createOscillator();
  const gain=audioCtx.createGain();
  osc.type="sine";
  osc.frequency.value=freq;
  gain.gain.setValueAtTime(.045,audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(
   .001,audioCtx.currentTime+duration
  );
  osc.connect(gain);
  gain.connect(audioCtx.destination);
  osc.start();
  osc.stop(audioCtx.currentTime+duration);
 }catch(e){}
}

function spawnParticles(x,y,count,color){
 for(let i=0;i<count;i++){
  particles.push({
   x,y,vx:random(-2.5,2.5),vy:random(-2.8,2.2),
   life:1,size:random(2,5),color
  });
 }
}

function flap(){
 if(state!=="playing")return;
 bird.vy=-H*.012;
 bird.wing=1;
 beep(740,.055);
 spawnParticles(bird.x-bird.r*.7,bird.y+4,4,"#fff5ad");
}

function startGame(){
 // Invalidate any previous game state before creating a fresh game.
 gameToken++;
 resetGame();
 state="playing";
 overlay.style.display="none";
 lastTime=performance.now();
 flap();
}

function endGame(){
 if(state!=="playing")return;
 state="over";
 bird.vy=-H*.003;
 beep(180,.18);

 if(score>best){
  best=score;
  bestEl.textContent=String(best);
  try{localStorage.setItem("flappy-hd-best",String(best));}catch(e){}
 }

 overlay.innerHTML=`
  <div class="panel">
   <h2>GAME OVER</h2>
   <p>Điểm của bạn: <b>${score}</b><br>🏆 Kỷ lục: <b>${best}</b></p>
   <button id="startBtn">↻ CHƠI LẠI</button>
   <p class="small">Cố lên! Hãy thử lại nhé.</p>
  </div>`;
 overlay.style.display="flex";
 document.getElementById("startBtn").addEventListener("click",e=>{
  e.stopPropagation();
  startGame();
 });
}

function drawCloud(x,y,s){
 ctx.save();
 ctx.translate(x,y);
 ctx.scale(s,s);
 ctx.fillStyle="rgba(255,255,255,.82)";
 ctx.beginPath();
 ctx.ellipse(0,5,32,13,0,0,Math.PI*2);
 ctx.ellipse(-17,0,16,14,0,0,Math.PI*2);
 ctx.ellipse(1,-8,20,20,0,0,Math.PI*2);
 ctx.ellipse(20,1,16,13,0,0,Math.PI*2);
 ctx.fill();
 ctx.restore();
}

function drawBackground(dt){
 const sky=ctx.createLinearGradient(0,0,0,H);
 sky.addColorStop(0,"#42c4ff");
 sky.addColorStop(.58,"#a6eaff");
 sky.addColorStop(1,"#f1fcff");
 ctx.fillStyle=sky;
 ctx.fillRect(0,0,W,H);

 const sun=ctx.createRadialGradient(W*.78,H*.16,3,W*.78,H*.16,85);
 sun.addColorStop(0,"rgba(255,255,202,.95)");
 sun.addColorStop(1,"rgba(255,255,202,0)");
 ctx.fillStyle=sun;
 ctx.fillRect(W*.78-85,H*.16-85,170,170);

 clouds.forEach(c=>{
  drawCloud(c.x,c.y,c.s);
  if(state==="playing")c.x-=dt*c.speed;
  if(c.x<-75)c.x=W+75;
 });

 // Far green hills
 ctx.fillStyle="#a3e6a5";
 ctx.beginPath();
 ctx.moveTo(0,H*.74);
 for(let x=0;x<=W+20;x+=16){
  ctx.lineTo(x,H*.68+Math.sin(x*.012+world*.0002)*H*.035);
 }
 ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.fill();

 ctx.fillStyle="#61cd8b";
 ctx.beginPath();
 ctx.moveTo(0,H*.83);
 for(let x=0;x<=W+20;x+=16){
  ctx.lineTo(x,H*.78+Math.sin(x*.018+1+world*.00025)*H*.03);
 }
 ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.fill();

 // Parallax city skyline
 const base=H*.89;
 for(let i=0;i<Math.ceil(W/44)+3;i++){
  const x=i*44-(world*.1%44);
  const bh=28+(i*37%55);
  ctx.fillStyle=["#9acfe0","#b4dfec","#7fbcd6"][i%3];
  ctx.fillRect(x,base-bh,35,bh);
  ctx.fillStyle="rgba(255,255,255,.65)";
  for(let wy=base-bh+8;wy<base-7;wy+=12){
   for(let wx=x+7;wx<x+29;wx+=12)ctx.fillRect(wx,wy,4,5);
  }
 }

 // Ground and grass
 ctx.fillStyle="#d8f19b";
 ctx.fillRect(0,H*.91,W,H*.09);
 ctx.fillStyle="#67c941";
 ctx.fillRect(0,H*.91,W,8);

 for(let x=-(world%28);x<W;x+=28){
  ctx.fillStyle="#a5e765";
  ctx.beginPath();
  ctx.moveTo(x,H*.91);
  ctx.lineTo(x+10,H*.91-5);
  ctx.lineTo(x+20,H*.91);
  ctx.fill();
 }
 ctx.fillStyle="#e8c77c";
 ctx.fillRect(0,H*.935,W,H*.065);
 ctx.fillStyle="rgba(181,127,53,.25)";
 for(let x=-(world%34);x<W;x+=34)ctx.fillRect(x,H*.96,17,3);
}

function drawPipe(p){
 const topH=p.center-p.gap/2;
 const botY=p.center+p.gap/2;
 const groundY=H*.91;
 const bottomH=groundY-botY;
 const x=p.x,w=p.w,cap=17;

 const grad=ctx.createLinearGradient(x,0,x+w,0);
 grad.addColorStop(0,"#08762a");
 grad.addColorStop(.2,"#51dc50");
 grad.addColorStop(.52,"#29bd3d");
 grad.addColorStop(1,"#08732a");

 ctx.fillStyle=grad;

 if(topH>0){
  ctx.fillRect(x,0,w,topH);
  ctx.fillRect(x-5,topH-cap,w+10,cap);
  ctx.fillStyle="rgba(255,255,255,.26)";
  ctx.fillRect(x+8,0,6,Math.max(0,topH-cap));
  ctx.fillStyle="rgba(0,0,0,.12)";
  ctx.fillRect(x+w-7,0,7,Math.max(0,topH-cap));
 }

 if(bottomH>0){
  ctx.fillStyle=grad;
  ctx.fillRect(x,botY,w,bottomH);
  ctx.fillRect(x-5,botY,w+10,cap);
  ctx.fillStyle="rgba(255,255,255,.26)";
  ctx.fillRect(x+8,botY+cap,6,Math.max(0,bottomH-cap));
  ctx.fillStyle="rgba(0,0,0,.12)";
  ctx.fillRect(x+w-7,botY+cap,7,Math.max(0,bottomH-cap));
 }

 ctx.strokeStyle="rgba(0,80,30,.45)";
 ctx.lineWidth=2;
 if(topH>0){
  ctx.strokeRect(x,0,w,topH);
  ctx.strokeRect(x-5,topH-cap,w+10,cap);
 }
 if(bottomH>0){
  ctx.strokeRect(x,botY,w,bottomH);
  ctx.strokeRect(x-5,botY,w+10,cap);
 }
}

function drawBird(){
 ctx.save();
 ctx.translate(bird.x,bird.y);
 ctx.rotate(bird.rot);

 // Soft shadow
 ctx.fillStyle="rgba(29,89,110,.16)";
 ctx.beginPath();
 ctx.ellipse(0,bird.r+10,bird.r*.95,4,0,0,Math.PI*2);
 ctx.fill();

 // Tail
 ctx.fillStyle="#f29a21";
 ctx.beginPath();
 ctx.moveTo(-bird.r+1,2);
 ctx.lineTo(-bird.r-9,-3);
 ctx.lineTo(-bird.r-7,7);
 ctx.closePath();ctx.fill();

 // Body
 const body=ctx.createLinearGradient(-bird.r,-bird.r,bird.r,bird.r);
 body.addColorStop(0,"#fff779");
 body.addColorStop(.55,"#ffd52f");
 body.addColorStop(1,"#f6a51b");
 ctx.fillStyle=body;
 ctx.beginPath();
 ctx.ellipse(0,0,bird.r*1.13,bird.r*.94,0,0,Math.PI*2);
 ctx.fill();
 ctx.strokeStyle="#bd7919";ctx.lineWidth=2;ctx.stroke();

 // Animated wing
 ctx.save();
 ctx.translate(-bird.r*.28,3);
 ctx.rotate(Math.sin(bird.wing*5)*.35+(bird.vy>0?.18:-.15));
 ctx.fillStyle="#f6a722";
 ctx.beginPath();
 ctx.ellipse(-2,2,bird.r*.48,bird.r*.32,-.3,0,Math.PI*2);
 ctx.fill();
 ctx.strokeStyle="#c57c1d";ctx.lineWidth=1.5;ctx.stroke();
 ctx.restore();

 // Cheek
 ctx.fillStyle="#ff9d92";
 ctx.beginPath();
 ctx.ellipse(bird.r*.55,bird.r*.27,bird.r*.2,bird.r*.13,0,0,Math.PI*2);
 ctx.fill();

 // Eye
 ctx.fillStyle="white";
 ctx.beginPath();
 ctx.ellipse(bird.r*.47,-bird.r*.28,bird.r*.28,bird.r*.34,0,0,Math.PI*2);
 ctx.fill();
 ctx.strokeStyle="#a36a1b";ctx.lineWidth=1.3;ctx.stroke();

 ctx.fillStyle="#18384d";
 ctx.beginPath();
 ctx.arc(bird.r*.56,-bird.r*.25,bird.r*.13,0,Math.PI*2);
 ctx.fill();

 ctx.fillStyle="white";
 ctx.beginPath();
 ctx.arc(bird.r*.59,-bird.r*.32,2,0,Math.PI*2);
 ctx.fill();

 // Beak
 ctx.fillStyle="#ff792b";
 ctx.beginPath();
 ctx.moveTo(bird.r*.8,-1);
 ctx.lineTo(bird.r*1.52,3);
 ctx.lineTo(bird.r*.82,7);
 ctx.closePath();ctx.fill();
 ctx.strokeStyle="#b95418";ctx.lineWidth=1.3;ctx.stroke();

 ctx.restore();
}

function draw(){
 if(!W||!H||!bird)return;

 drawBackground(0);
 pipes.forEach(drawPipe);

 particles.forEach(p=>{
  ctx.globalAlpha=Math.max(0,p.life);
  ctx.fillStyle=p.color;
  ctx.beginPath();
  ctx.arc(p.x,p.y,p.size*p.life,0,Math.PI*2);
  ctx.fill();
 });
 ctx.globalAlpha=1;

 drawBird();
}

function hitPipe(p){
 const r=bird.r*.76;
 const bx=bird.x,by=bird.y;
 const top=p.center-p.gap/2;
 const bottom=p.center+p.gap/2;

 return bx+r>p.x-5 && bx-r<p.x+p.w+5 &&
        (by-r<top || by+r>bottom);
}

function update(timestamp){
 const dt=lastTime?Math.min(32,timestamp-lastTime):16;
 lastTime=timestamp;

 if(state==="playing"){
  world+=dt;

  // Stable physics independent of frame rate.
  const step=dt/16.67;
  bird.vy+=H*.00072*step;
  bird.vy=Math.min(bird.vy,H*.013);
  bird.y+=bird.vy*step;
  bird.rot=Math.max(-.45,Math.min(.9,bird.vy/(H*.025)));
  bird.wing+=dt*.012;

  const speed=Math.max(2.8,W*.006)*step;
  pipes.forEach(p=>{
   p.x-=speed;

   if(!p.passed && p.x+p.w<bird.x){
    p.passed=true;
    score++;
    scoreEl.textContent=String(score);
    beep(980,.075);
    spawnParticles(bird.x,bird.y,9,"#fff5ad");
   }
  });

  pipes=pipes.filter(p=>p.x+p.w>-20);

  while(pipes.length<4){
   const lastPipe=pipes[pipes.length-1];
   pipes.push(makePipe(lastPipe?lastPipe.x+W*.64:W+100));
  }

  particles.forEach(p=>{
   p.x+=p.vx*step;
   p.y+=p.vy*step;
   p.life-=dt*.002;
  });
  particles=particles.filter(p=>p.life>0);

  // Only playing state can trigger game over.
  if(
   pipes.some(hitPipe) ||
   bird.y+bird.r>H*.91 ||
   bird.y-bird.r<0
  ){
   endGame();
  }
 }

 draw();
 requestAnimationFrame(update);
}

function pointerAction(e){
 if(e)e.preventDefault();
 if(state==="playing")flap();
}

wrap.addEventListener("pointerdown",e=>{
 if(e.target.closest("button"))return;
 if(state==="playing")pointerAction(e);
});

document.addEventListener("keydown",e=>{
 if(e.code==="Space"||e.code==="ArrowUp"){
  e.preventDefault();
  if(state==="menu"||state==="over")startGame();
  else flap();
 }
});

document.getElementById("startBtn").addEventListener("click",e=>{
 e.stopPropagation();
 startGame();
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
    "Mẹo: Chạm vào vùng game để bay trên điện thoại. "
    "Trên máy tính, nhấn SPACE. Nếu chỉnh sửa code, hãy Commit changes để triển khai lại."
)
