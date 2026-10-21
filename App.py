    border-radius: 6px;
}
</style>
</head>
<body>
<canvas id="game"></canvas>
<div id="score">0</div>
<div id="hint">
    FLAPPY BIRD
    <span id="sub">Chạm nhẹ để bay lên!<br>Tránh các ống cống!</span>
</div>
<button id="sound">🔊</button>
<div id="panel">
    <h2>GAME OVER!</h2>
    <p id="result"></p>
    <button id="again">CHƠI LẠI ↻</button>
</div>

<script>
(() => {
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const hint = document.getElementById("hint");
const panel = document.getElementById("panel");
const result = document.getElementById("result");

let W, H, bird, pipes, particles;
let score = 0, best = 0, frame = 0;
let state = "ready", last = 0;
let sound = true, audio = null, groundH;

const rand = (a,b) => a + Math.random() * (b-a);

function resize() {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    W = canvas.clientWidth || innerWidth;
    H = innerHeight;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
    groundH = Math.max(65,H*.10);
    reset();
}

function reset() {
    bird = {x:W*.27,y:H*.42,vy:0,rot:0};
    pipes = [];
    particles = [];
    score = 0;
    frame = 0;
    state = "ready";
    scoreEl.textContent = "0";
    hint.style.display = "block";
    panel.style.display = "none";
}

function beep(freq=550) {
    if (!sound) return;
    try {
        audio = audio || new AudioContext();
        const o = audio.createOscillator();
        const g = audio.createGain();
        o.connect(g); g.connect(audio.destination);
        o.frequency.value = freq;
        o.type = "triangle";
        g.gain.value = .035;
        o.start();
        g.gain.exponentialRampToValueAtTime(.001,audio.currentTime+.09);
        o.stop(audio.currentTime+.09);
    } catch(e) {}
}

function flap() {
    if (state === "over") {
        reset();
        state = "playing";
    }
    if (state === "ready") state = "playing";

    if (state === "playing") {
        // Chạm nhẹ: lực bay thấp hơn để dễ kiểm soát
        bird.vy = -H * 0.25;
        hint.style.display = "none";
        beep(650);

        for (let i=0;i<5;i++) {
            particles.push({
                x:bird.x-8, y:bird.y,
                vx:rand(-2,-.5), vy:rand(-2,2),
                life:1, size:rand(2,5), color:"#fff1a6"
            });
        }
    }
}

function over() {
    if (state !== "playing") return;
    state = "over";
    best = Math.max(best,score);
    result.textContent = "Điểm: "+score+" | Kỷ lục: "+best;
    panel.style.display = "block";
    beep(150);
}

function rect(x,y,w,h,c) {
    ctx.fillStyle = c;
    ctx.fillRect(x,y,w,h);
}

function background() {
    const sky = ctx.createLinearGradient(0,0,0,H);
    sky.addColorStop(0,"#50bfd6");
    sky.addColorStop(.6,"#9be8dc");
    sky.addColorStop(1,"#e2f7bf");
    rect(0,0,W,H,sky);

    // Mặt trời
    ctx.fillStyle = "#fff1a4";
    ctx.beginPath();
    ctx.arc(W*.82,H*.17,Math.min(W,H)*.055,0,Math.PI*2);
    ctx.fill();

    // Mây pixel
    for (let i=0;i<6;i++) {
        const s=W*.10;
        const x=((i*W*.27-frame*.15)%(W+s*3)+W+s*3)%(W+s*3)-s;
        const y=H*(.16+(i%4)*.11);
        ctx.fillStyle="rgba(255,255,255,.7)";
        ctx.fillRect(x,y,s*2,s*.4);
        ctx.fillRect(x+s*.25,y-s*.3,s*.6,s*.7);
        ctx.fillRect(x+s*.8,y-s*.55,s*.8,s);
    }

    // Đồi xa
    ctx.fillStyle="#b8edb0";
    ctx.beginPath();
    ctx.moveTo(0,H*.7);
    for(let x=0;x<=W;x+=8)
        ctx.lineTo(x,H*.66+Math.sin(x/W*9+frame*.003)*H*.025);
    ctx.lineTo(W,H); ctx.lineTo(0,H);
    ctx.fill();

    // Thành phố
    const base=H-groundH-H*.12;
    for(let i=0;i<12;i++) {
        const bw=W*.065;
        const bh=H*(.06+(i%5)*.012);
        const x=((i*W*.13-frame*.2)%(W+30)+W+30)%(W+30)-15;
        rect(x,base-bh,bw,bh,"#88cec7");
        for(let y=base-bh+8;y<base-4;y+=12)
            for(let xx=x+6;xx<x+bw-3;xx+=11)
                rect(xx,y,4,5,"#c3f1d8");
    }
}

function pipe(p) {
    const x=p.x,w=p.w,t=p.top,b=t+p.gap;
    const bottomH=H-groundH-b;
    const edge="#493747",green="#72c42d";
    const light="#b6f85d",dark="#438e26";

    // Ống trên
    rect(x-4,-3,w+8,t+4,edge);
    rect(x,0,w,t,dark);
    rect(x+4,0,w-8,t,green);
    rect(x+10,0,5,t,light);
    rect(x+w-13,0,5,t,dark);

    // Miệng ống trên
    rect(x-8,t-14,w+16,22,edge);
    rect(x-4,t-10,w+8,14,dark);
    rect(x-2,t-8,w+4,9,green);
    rect(x+5,t-8,5,9,light);

    // Ống dưới
    rect(x-4,b,w+8,bottomH+5,edge);
    rect(x,b,w,bottomH,dark);
    rect(x+4,b,w-8,bottomH,green);
    rect(x+10,b,5,bottomH,light);
    rect(x+w-13,b,5,bottomH,dark);

    // Miệng ống dưới
    rect(x-8,b-5,w+16,22,edge);
    rect(x-4,b,w+8,14,dark);
    rect(x-2,b,w+4,9,green);
    rect(x+5,b,5,9,light);
}

function drawBird() {
    ctx.save();
    ctx.translate(bird.x,bird.y);
    ctx.rotate(bird.rot);

    const s=Math.max(3,Math.min(W,H)*.0065);
    const px=(x,y,w,h,c)=>{
        ctx.fillStyle=c;
        ctx.fillRect(x*s,y*s,w*s,h*s);
    };

    // Quầng sáng
    ctx.fillStyle="rgba(255,240,160,.25)";
    ctx.beginPath();
    ctx.arc(0,0,14*s,0,Math.PI*2);
    ctx.fill();

    // Đuôi và cánh chuyển động
    px(-10,-1,4,3,"#493747");
    px(-9,0,3,2,"#f47c26");
    const wing=Math.sin(frame*.5)*2;
    px(-4,1+wing,7,5,"#493747");
    px(-3,2+wing,5,3,"#e98324");

    // Thân chim
    px(-7,-4,7,7,"#493747");
    px(-6,-3,6,6,"#fff3d7");
    px(-3,-7,8,4,"#493747");
    px(-2,-6,7,3,"#ffcf56");
    px(-1,-3,10,8,"#493747");
    px(0,-2,8,7,"#f5ad35");

    // Mắt và mỏ
    px(3,-6,4,5,"#493747");
    px(4,-5,3,3,"#ffffff");
    px(5,-4,2,2,"#493747");
    px(6,0,5,3,"#493747");
    px(7,1,4,1,"#f46d35");

    // Chân
    px(-1,5,2,6,"#493747");
    px(0,5,2,5,"#f04420");
    px(2,5,2,7,"#493747");
    px(3,5,2,6,"#f04420");

    ctx.restore();
}

function ground() {
    const y=H-groundH;
    rect(0,y,W,groundH,"#ded79a");
    rect(0,y-10,W,10,"#493747");
    rect(0,y-6,W,4,"#c3f76b");
    rect(0,y,W,groundH*.42,"#a4ed50");

    for(let x=-40;x<W+50;x+=80) {
        ctx.fillStyle="#72bf2c";
        ctx.beginPath();
        ctx.moveTo(x,y);
        ctx.lineTo(x+40,y);
        ctx.lineTo(x,y+groundH*.42);
        ctx.lineTo(x-40,y+groundH*.42);
        ctx.closePath();
        ctx.fill();
    }
    rect(0,y+groundH*.42,W,5,"#c9a952");
}

function update(dt) {
    frame+=dt*60;

    particles.forEach(p=>{
        p.x+=p.vx*dt*60;
        p.y+=p.vy*dt*60;
        p.vy+=.04*dt*60;
        p.life-=dt*1.5;
    });
    particles=particles.filter(p=>p.life>0);

    if(state!=="playing") return;

    // Trọng lực nhẹ, giới hạn tốc độ rơi
    bird.vy=Math.min(H*.010,bird.vy+H*.00065*dt*60);
    bird.y+=bird.vy*dt*60;
    bird.rot=Math.max(-.4,Math.min(.7,bird.vy/(H*.035)));

    if(!pipes.length||pipes[pipes.length-1].x<W*.62) {
        const gap=Math.max(H*.25,Math.min(H*.29,230));
        const margin=H*.13;
        const maxTop=Math.max(margin+10,H-groundH-gap-margin);
        pipes.push({
            x:W+10,w:Math.max(48,W*.14),
            gap:gap,top:rand(margin,maxTop),passed:false
        });
    }

    const speed=Math.max(1.8,W*.0028);
    pipes.forEach(p=>p.x-=speed*dt*60);
    pipes=pipes.filter(p=>p.x+p.w>-20);

    const r=Math.max(8,H*.014);
    if(bird.y+r>H-groundH||bird.y-r<0) over();

    for(const p of pipes) {
        const bottom=p.top+p.gap;
        if(bird.x+r>p.x&&bird.x-r<p.x+p.w&&
          (bird.y-r<p.top||bird.y+r>bottom)) over();

        if(!p.passed&&p.x+p.w<bird.x) {
            p.passed=true;
            score++;
            scoreEl.textContent=score;
            beep(850);
            for(let i=0;i<10;i++) particles.push({
                x:bird.x,y:bird.y,vx:rand(-2,2),
                vy:rand(-3,1),life:1,size:rand(2,4),
                color:"#fff18c"
            });
        }
    }
}

function draw() {
    background();
    pipes.forEach(pipe);
    ground();

    particles.forEach(p=>{
        ctx.globalAlpha=Math.max(0,p.life);
        rect(p.x,p.y,p.size||3,p.size||3,p.color);
    });
    ctx.globalAlpha=1;

    if(bird) {
        if(state==="ready")
            bird.y=H*.42+Math.sin(frame*.06)*H*.008;
        drawBird();
    }
}

function loop(t) {
    const dt=Math.min(.035,(t-(last||t))/1000);
    last=t;
    update(dt);
    draw();
    requestAnimationFrame(loop);
}

canvas.addEventListener("pointerdown",e=>{
    e.preventDefault();
    flap();
});

window.addEventListener("keydown",e=>{
    if(e.code==="Space"||e.code==="ArrowUp") {
        e.preventDefault();
        flap();
    }
});

document.getElementById("again").addEventListener("click",e=>{
    e.stopPropagation();
    reset();
});

document.getElementById("sound").addEventListener("click",e=>{
    e.stopPropagation();
    sound=!sound;
    e.target.textContent=sound?"🔊":"🔇";
    if(sound) beep();
});

window.addEventListener("resize",resize);
resize();
requestAnimationFrame(loop);
})();
</script>
</body>
</html>
"""

components.html(game_html, height=780, scrolling=False)
    
