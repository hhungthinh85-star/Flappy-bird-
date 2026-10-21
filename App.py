
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Flappy Bird Pixel",
    page_icon="🐤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    background: #55bec5;
}
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], footer, #MainMenu {
    display: none !important;
}
.block-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}
iframe { display: block; border: 0; }
</style>
""", unsafe_allow_html=True)

game_html = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport"
content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
* { box-sizing: border-box; }
html, body {
    margin: 0; padding: 0; width: 100%; height: 100%;
    overflow: hidden; background: #55bec5;
    font-family: Arial, sans-serif;
    touch-action: manipulation;
}
#wrap {
    position: relative; width: 100%; height: 100vh;
    min-height: 500px; overflow: hidden;
    background: #55bec5;
}
canvas {
    display: block; width: 100%; height: 100%;
    image-rendering: pixelated;
}
#hint {
    position: absolute; left: 0; right: 0; top: 18%;
    text-align: center; color: white; font-weight: 900;
    text-shadow: 2px 3px #47737a;
    font-size: clamp(22px, 5vw, 38px);
    pointer-events: none;
}
#sub {
    font-size: clamp(13px, 3vw, 18px);
    display: block; margin-top: 12px;
}
#score {
    position: absolute; top: 5%; left: 0; right: 0;
    text-align: center; font-size: clamp(42px, 10vw, 68px);
    color: white; text-shadow: 3px 3px #47737a;
    pointer-events: none;
}
#best {
    position: absolute; top: calc(5% + 65px);
    left: 0; right: 0; text-align: center;
    color: white; font-size: 14px;
    text-shadow: 1px 2px #47737a;
    pointer-events: none;
}
#sound {
    position: absolute; top: 12px; right: 12px;
    border: 2px solid #34464a; background: #ffffffcc;
    border-radius: 10px; padding: 8px 10px;
    font-size: 18px; cursor: pointer;
}
#overlay {
    position: absolute; inset: 0;
    display: flex; align-items: center;
    justify-content: center; pointer-events: none;
}
#panel {
    pointer-events: auto; display: none;
    text-align: center; background: #fff3d8;
    border: 4px solid #604453;
    box-shadow: 0 7px 0 #604453;
    padding: 22px 28px; max-width: 86%; color: #34464a;
}
#panel h2 { margin: 0 0 8px; font-size: 30px; }
#panel p { margin: 8px 0 16px; }
button.play {
    border: 3px solid #604453; background: #7cc52d;
    color: white; font-weight: 900; font-size: 19px;
    padding: 10px 24px; box-shadow: 0 4px 0 #604453;
    cursor: pointer;
}
button.play:active {
    transform: translateY(3px);
    box-shadow: 0 1px 0 #604453;
}
</style>
</head>
<body>
<div id="wrap">
    <canvas id="game"></canvas>
    <div id="score">0</div>
    <div id="best"></div>

    <div id="hint">
        FLAPPY BIRD
        <span id="sub">Chạm màn hình hoặc nhấn SPACE để bay</span>
    </div>

    <button id="sound">🔊</button>

    <div id="overlay">
        <div id="panel">
            <h2>GAME OVER!</h2>
            <p id="result">Điểm: 0</p>
            <button class="play" id="again">Chơi lại ↻</button>
        </div>
    </div>
</div>

<script>
(() => {
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const scoreEl = document.getElementById("score");
const bestEl = document.getElementById("best");
const hint = document.getElementById("hint");
const panel = document.getElementById("panel");
const result = document.getElementById("result");
const soundBtn = document.getElementById("sound");

let W = 0, H = 0, dpr = 1;
let bird, pipes = [], score = 0, best = 0;
let state = "ready", frame = 0, last = 0;
let sound = true, audioCtx = null;

let groundH = Math.max(70, window.innerHeight * 0.105);

const rand = (a, b) => a + Math.random() * (b - a);

function resize() {
    const r = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = r.width;
    H = r.height;
    groundH = Math.max(70, H * 0.105);

    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    if (!bird) reset();
}

function reset() {
    bird = { x: W * 0.27, y: H * 0.42, vy: 0, rot: 0 };
    pipes = [];
    score = 0;
    frame = 0;
    state = "ready";

    scoreEl.textContent = "0";
    bestEl.textContent = best ? "Kỷ lục: " + best : "";
    hint.style.display = "block";
    panel.style.display = "none";
}

function beep(freq = 520, dur = 0.07) {
    if (!sound) return;

    try {
        audioCtx = audioCtx ||
            new (window.AudioContext || window.webkitAudioContext)();

        const o = audioCtx.createOscillator();
        const g = audioCtx.createGain();

        o.connect(g);
        g.connect(audioCtx.destination);

        o.frequency.value = freq;
        o.type = "square";
        g.gain.value = 0.035;

        o.start();
        g.gain.exponentialRampToValueAtTime(
            0.001, audioCtx.currentTime + dur
        );
        o.stop(audioCtx.currentTime + dur);
    } catch (e) {}
}

function flap() {
    if (state === "over") {
        reset();
        state = "playing";
        hint.style.display = "none";
        bird.vy = -H * 0.43;
        beep(650);
        return;
    }

    if (state === "ready") {
        state = "playing";
        hint.style.display = "none";
    }

    if (state === "playing") {
        bird.vy = -H * 0.43;
        beep(650);
    }
}

function gameOver() {
    if (state !== "playing") return;

    state = "over";
    beep(130, 0.18);
    best = Math.max(best, score);

    bestEl.textContent = "Kỷ lục: " + best;
    result.textContent =
        "Điểm: " + score + " • Kỷ lục: " + best;

    panel.style.display = "block";
}

function rect(x, y, w, h, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
}

function drawCloud(x, y, s) {
    ctx.fillStyle = "#e9ffd9";
    ctx.fillRect(x, y, s * 2.2, s * 0.55);
    ctx.fillRect(x + s * 0.25, y - s * 0.35, s * 0.7, s * 0.9);
    ctx.fillRect(x + s * 0.85, y - s * 0.7, s * 0.85, s * 1.25);
    ctx.fillRect(x + s * 1.45, y - s * 0.25, s * 0.55, s * 0.8);

    ctx.fillStyle = "#d4f5cf";
    ctx.fillRect(x, y + s * 0.42, s * 2.2, s * 0.13);
}

function drawCity() {
    const base = H - groundH - H * 0.16;
    ctx.fillStyle = "#a9dfd9";

    for (let i = 0; i < 9; i++) {
        const bw = W * 0.075;
        const x = (
            (i * W * 0.17 - frame * 0.22) % (W * 0.17)
            + W * 2
        ) % (W + W * 0.1) - bw;

        const bh = H * (0.07 + ((i * 7) % 5) * 0.012);

        ctx.fillRect(x, base - bh, bw, bh);

        for (let yy = base - bh + bh * 0.3; yy < base - 5; yy += 13) {
            for (let xx = x + 5; xx < x + bw - 3; xx += 12) {
                ctx.fillRect(xx, yy, 4, 6);
            }
        }
    }
}

function drawPipe(p) {
    const x = p.x, w = p.w;
    const topH = p.top;
    const bottomY = topH + p.gap;
    const bottomH = H - groundH - bottomY;

    const outline = "#493b4d";
    const dark = "#579d25";
    const green = "#76c42d";
    const light = "#b0f45b";

    // Ống phía trên
    rect(x - 3, -4, w + 6, topH + 3, outline);
    rect(x, 0, w, topH, dark);
    rect(x + 5, 0, w - 10, topH, green);
    rect(x + 10, 0, 5, topH, light);
    rect(x + w - 14, 0, 5, topH, "#5ca52a");

    rect(x - 7, topH - 13, w + 14, 17, outline);
    rect(x - 3, topH - 10, w + 6, 11, green);
    rect(x + 5, topH - 10, 5, 11, light);

    // Ống phía dưới
    rect(x - 3, bottomY, w + 6, bottomH + 5, outline);
    rect(x, bottomY, w, bottomH, dark);
    rect(x + 5, bottomY, w - 10, bottomH, green);
    rect(x + 10, bottomY, 5, bottomH, light);
    rect(x + w - 14, bottomY, 5, bottomH, dark);

    rect(x - 7, bottomY - 3, w + 14, 17, outline);
    rect(x - 3, bottomY, w + 6, 11, green);
    rect(x + 5, bottomY, 5, 11, light);
}

function drawBird() {
    ctx.save();
    ctx.translate(bird.x, bird.y);
    ctx.rotate(bird.rot);

    const s = Math.max(3, Math.min(W, H) * 0.0065);

    function px(x, y, w, h, color) {
        ctx.fillStyle = color;
        ctx.fillRect(x * s, y * s, w * s, h * s);
    }

    // Chim pixel màu vàng cam
    px(-7, -4, 7, 7, "#493b4d");
    px(-6, -3, 6, 6, "#fff3d7");
    px(-3, -7, 8, 4, "#493b4d");
    px(-2, -6, 7, 3, "#ffcf56");
    px(-1, -3, 10, 8, "#493b4d");
    px(0, -2, 8, 7, "#f5ad35");
    px(3, -6, 4, 5, "#fff3d7");
    px(4, -5, 3, 3, "#ffffff");
    px(5, -4, 2, 2, "#493b4d");
    px(6, 0, 5, 3, "#493b4d");
    px(7, 1, 4, 1, "#f46d35");
    px(-5, 2, 6, 5, "#493b4d");
    px(-4, 3, 5, 3, "#e98128");
    px(-1, 5, 2, 6, "#493b4d");
    px(0, 5, 2, 5, "#f04420");
    px(2, 5, 2, 7, "#493b4d");
    px(3, 5, 2, 6, "#f04420");
    px(-2, 0, 4, 3, "#fff3d7");
    px(-1, 1, 2, 1, "#493b4d");

    ctx.restore();
}

function drawGround() {
    const y = H - groundH;

    rect(0, y, W, groundH, "#dfd99a");
    rect(0, y - 10, W, 10, "#493b4d");
    rect(0, y - 6, W, 5, "#b6f05b");
    rect(0, y, W, groundH * 0.45, "#a1e94f");

    for (let x = -40; x < W + 60; x += 80) {
        ctx.fillStyle = "#70bd2c";
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + 40, y);
        ctx.lineTo(x, y + groundH * 0.42);
        ctx.lineTo(x - 40, y + groundH * 0.42);
        ctx.closePath();
        ctx.fill();
    }

    rect(0, y + groundH * 0.45, W, 5, "#d2b55f");
}

function update(dt) {
    frame += dt * 60;

    if (state !== "playing") return;

    bird.vy += H * 0.00165 * dt * 60;
    bird.y += bird.vy * dt * 60;
    bird.rot = Math.min(
        0.9, Math.max(-0.55, bird.vy / (H * 0.025))
    );

    if (!pipes.length || pipes[pipes.length - 1].x < W * 0.58) {
        const gap = Math.max(H * 0.19, Math.min(H * 0.24, 180));

        pipes.push({
            x: W + 10,
            w: W * 0.145,
            gap: gap,
            top: rand(H * 0.12, H * 0.52),
            passed: false
        });
    }

    const speed = W * 0.0048;
    pipes.forEach(p => p.x -= speed * dt * 60);
    pipes = pipes.filter(p => p.x + p.w > -20);

    const groundY = H - groundH;
    const br = H * 0.018;

    if (bird.y + br > groundY || bird.y - br < 0) {
        gameOver();
    }

    for (const p of pipes) {
        const gapBottom = p.top + p.gap;

        if (
            bird.x + br > p.x &&
            bird.x - br < p.x + p.w &&
            (bird.y - br < p.top || bird.y + br > gapBottom)
        ) {
            gameOver();
        }

        if (!p.passed && p.x + p.w < bird.x) {
            p.passed = true;
            score++;
            scoreEl.textContent = score;
            beep(820, 0.06);
        }
    }
}

function draw() {
    rect(0, 0, W, H, "#55bec5");

    for (let i = 0; i < 5; i++) {
        const x = (
            (i * W * 0.29 - frame * 0.35) % (W + W * 0.3)
            + W + W * 0.3
        ) % (W + W * 0.3) - W * 0.1;

        drawCloud(x, H * 0.53 + (i % 2) * H * 0.025, W * 0.12);
    }

    drawCity();

    rect(0, H - groundH - H * 0.16, W, H * 0.16, "#58d96d");

    for (let i = 0; i < 40; i++) {
        const x = (
            (i * 97 - frame * 0.7) % (W + 30) + W + 30
        ) % (W + 30) - 15;

        const y = H - groundH - H * 0.16 + ((i * 19) % 60);
        rect(x, y, 14, 7, i % 2 ? "#4fcf68" : "#66df73");
    }

    pipes.forEach(drawPipe);
    drawGround();

    if (bird) {
        if (state === "ready") {
            bird.y = H * 0.42 + Math.sin(frame * 0.06) * H * 0.008;
        }
        drawBird();
    }
}

function loop(t) {
    const dt = Math.min(0.035, (t - (last || t)) / 1000);
    last = t;
    update(dt);
    draw();
    requestAnimationFrame(loop);
}

canvas.addEventListener("pointerdown", e => {
    e.preventDefault();
    flap();
});

window.addEventListener("keydown", e => {
    if (e.code === "Space" || e.code === "ArrowUp") {
        e.preventDefault();
        flap();
    }
});

document.getElementById("again").addEventListener("click", e => {
    e.stopPropagation();
    reset();
});

soundBtn.addEventListener("click", e => {
    e.stopPropagation();
    sound = !sound;
    soundBtn.textContent = sound ? "🔊" : "🔇";
    if (sound) beep();
});

window.addEventListener("resize", resize);

resize();
reset();
requestAnimationFrame(loop);
})();
</script>
</body>
</html>
"""

components.html(game_html, height=780, scrolling=False)
