
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Flappy Bird HD 2.2",
    page_icon="🐦",
    layout="centered"
)

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: Arial, sans-serif;
    background: #101d39;
}
#game {
    position: relative;
    width: 100%;
    height: min(720px, 78vh);
    min-height: 480px;
    overflow: hidden;
    border-radius: 16px;
    background: #70d6ff;
    box-shadow: 0 8px 30px #0007;
    touch-action: manipulation;
}
canvas {
    width: 100%;
    height: 100%;
    display: block;
}
#topbar {
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 6px;
    z-index: 3;
}
.pill {
    color: white;
    background: #122b4dcc;
    border: 1px solid #ffffff55;
    border-radius: 12px;
    padding: 7px 10px;
    font-weight: bold;
    font-size: 12px;
    text-shadow: 0 1px 2px #000;
}
#soundBtn {
    cursor: pointer;
    border: 1px solid #ffffff66;
    border-radius: 10px;
    padding: 8px 10px;
    background: #122b4dcc;
    color: white;
    font-weight: bold;
}
#overlay {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 18px;
    background: #07142b66;
    z-index: 5;
}
.panel {
    width: min(360px, 100%);
    text-align: center;
    color: white;
    background: linear-gradient(160deg, #1e4c7cF5, #101c3af5);
    border: 2px solid #ffffff66;
    border-radius: 22px;
    padding: 22px 18px;
    box-shadow: 0 10px 35px #0007;
}
h1 {
    margin: 0 0 7px;
    color: #ffe65a;
    font-size: clamp(26px, 6vw, 38px);
    text-shadow: 0 3px #a94e00;
}
#message {
    margin: 8px 0 15px;
    line-height: 1.5;
    font-size: 14px;
}
.modes {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 12px 0;
}
button {
    cursor: pointer;
    touch-action: manipulation;
}
.mode {
    border: 2px solid #ffffff44;
    border-radius: 11px;
    padding: 11px 5px;
    color: white;
    background: #ffffff18;
    font-weight: bold;
}
.mode.selected {
    border-color: #ffe65a;
    background: #ffe65a30;
    box-shadow: 0 0 12px #ffe65a66;
}
#mainBtn {
    width: 100%;
    margin-top: 10px;
    padding: 14px;
    border: none;
    border-radius: 13px;
    background: linear-gradient(#ffe95e, #ff9f1c);
    color: #432000;
    font-size: 18px;
    font-weight: 900;
    box-shadow: 0 4px #a8540a;
}
#help {
    margin-top: 12px;
    font-size: 12px;
    opacity: .85;
}
#celebrateText {
    position: absolute;
    top: 24%;
    left: 0;
    width: 100%;
    text-align: center;
    pointer-events: none;
    z-index: 4;
    font-size: clamp(20px, 5vw, 34px);
    font-weight: 1000;
    color: #fff34c;
    text-shadow: 0 3px 0 #f45d01, 0 0 18px #ffeb3b;
    display: none;
    animation: pop .3s ease-out;
}
@keyframes pop {
    0% { transform: scale(.4) rotate(-8deg); }
    80% { transform: scale(1.15) rotate(3deg); }
    100% { transform: scale(1); }
}
</style>
</head>
<body>
<div id="game">
    <canvas id="canvas"></canvas>
    <div id="topbar">
        <div class="pill" id="scoreBox">⭐ 0</div>
        <div class="pill" id="bestBox">🏆 BEST 0</div>
        <button id="soundBtn">🔊 SOUND ON</button>
    </div>
    <div id="celebrateText">🎉 AMAZING! 🎉</div>
    <div id="overlay">
        <div class="panel">
            <h1 id="title">FLAPPY BIRD</h1>
            <div id="message">
                Bay qua các đường ống và ghi điểm!<br>
                Cứ mỗi 10 điểm sẽ có ăn mừng.
            </div>
            <div class="modes">
                <button class="mode selected" data-mode="easy">🟢 EASY</button>
                <button class="mode" data-mode="medium">🟡 MEDIUM</button>
                <button class="mode" data-mode="hard">🔥 HARD</button>
                <button class="mode" data-mode="impossible">💀 IMPOSSIBLE</button>
            </div>
            <button id="mainBtn">▶ BẮT ĐẦU CHƠI</button>
            <div id="help">Chạm màn hình hoặc nhấn SPACE để bay</div>
        </div>
    </div>
</div>

<script>
(() => {
"use strict";

const game = document.getElementById("game");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const overlay = document.getElementById("overlay");
const titleEl = document.getElementById("title");
const messageEl = document.getElementById("message");
const mainBtn = document.getElementById("mainBtn");
const scoreBox = document.getElementById("scoreBox");
const bestBox = document.getElementById("bestBox");
const soundBtn = document.getElementById("soundBtn");
const celebrateText = document.getElementById("celebrateText");
const modeButtons = [...document.querySelectorAll(".mode")];

const configs = {
    easy: {
        gap: 0.34, spacing: 0.77, speed: 2.8,
        fire: 0, label: "EASY"
    },
    medium: {
        gap: 0.31, spacing: 0.72, speed: 3.3,
        fire: 0, label: "MEDIUM"
    },
    hard: {
        gap: 0.30, spacing: 0.72, speed: 3.6,
        fire: 0.30, label: "HARD"
    },
    impossible: {
        gap: 0.32, spacing: 0.78, speed: 3.9,
        fire: 0.48, label: "IMPOSSIBLE"
    }
};

let W = 400, H = 600, dpr = 1;
let mode = "easy";
let state = "menu";
let score = 0;
let best = 0;
let pipes = [];
let particles = [];
let clouds = [];
let bird = {};
let frame = 0;
let lastTime = 0;
let worldTime = 0;
let celebrationUntil = 0;
let lastCelebration = 0;
let soundOn = true;
let audioCtx = null;
let musicTimer = null;
let musicIndex = 0;
let musicTimeouts = [];
let lastScoreSound = -1;

try {
    best = Number(localStorage.getItem("flappyBirdBest") || 0);
} catch (e) {
    best = 0;
}

function resize() {
    const rect = game.getBoundingClientRect();
    W = Math.max(280, rect.width);
    H = Math.max(480, rect.height);
    dpr = Math.min(window.devicePixelRatio || 1, 2);

    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    clouds = [];
    for (let i = 0; i < 7; i++) {
        clouds.push({
            x: Math.random() * W,
            y: 40 + Math.random() * H * 0.42,
            s: 0.5 + Math.random() * 1.1
        });
    }

    if (state === "menu") resetBird();
}
window.addEventListener("resize", resize);

function resetBird() {
    bird = {
        x: W * 0.27,
        y: H * 0.43,
        vy: 0,
        r: Math.max(12, Math.min(17, W * 0.04)),
        angle: 0,
        flap: 0
    };
}

function resetGame() {
    score = 0;
    pipes = [];
    particles = [];
    frame = 0;
    lastCelebration = 0;
    celebrationUntil = 0;
    lastScoreSound = -1;
    celebrateText.style.display = "none";
    resetBird();

    for (let i = 0; i < 3; i++) {
        makePipe(W + 100 + i * W * configs[mode].spacing);
    }

    updateScore();
}

function makePipe(x) {
    const c = configs[mode];
    const gap = Math.max(150, Math.min(230, H * c.gap));
    const margin = 75;
    const center = margin + gap / 2 +
        Math.random() * Math.max(1, H - 150 - gap);

    pipes.push({
        x,
        w: Math.max(54, Math.min(70, W * 0.16)),
        center,
        gap,
        passed: false,
        hot: Math.random() < c.fire,
        seed: Math.random() * 100
    });
}

function updateScore() {
    scoreBox.textContent = "⭐ " + score;
    bestBox.textContent = "🏆 BEST " + best;
}

function getAudio() {
    if (!soundOn) return null;
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === "suspended") audioCtx.resume();
        return audioCtx;
    } catch (e) {
        return null;
    }
}

function tone(freq, duration, type = "sine", volume = 0.04, delay = 0) {
    const audio = getAudio();
    if (!audio) return;

    try {
        const osc = audio.createOscillator();
        const gain = audio.createGain();
        const start = audio.currentTime + delay;

        osc.type = type;
        osc.frequency.setValueAtTime(freq, start);
        gain.gain.setValueAtTime(0.001, start);
        gain.gain.linearRampToValueAtTime(volume, start + 0.025);
        gain.gain.exponentialRampToValueAtTime(
            0.001, start + Math.max(0.06, duration)
        );

        osc.connect(gain);
        gain.connect(audio.destination);
        osc.start(start);
        osc.stop(start + duration + 0.04);
    } catch (e) {}
}

function startMusic() {
    stopMusic();
    if (!soundOn) return;

    const melody = [
        523.25, 659.25, 783.99, 659.25,
        587.33, 698.46, 880.00, 698.46,
        523.25, 659.25, 783.99, 1046.5,
        880.00, 783.99, 659.25, 587.33
    ];
    musicIndex = 0;

    function tick() {
        if (state !== "playing" || !soundOn) {
            musicTimer = null;
            return;
        }

        const note = melody[musicIndex % melody.length];
        tone(note, 0.19, "triangle", 0.018);
        if (musicIndex % 4 === 0) {
            tone(note / 2, 0.25, "sine", 0.009);
        }
        musicIndex++;
        musicTimer = setTimeout(tick, 240);
    }
    tick();
}

function stopMusic() {
    if (musicTimer) clearTimeout(musicTimer);
    musicTimer = null;
}

function flapSound() {
    tone(620, 0.08, "triangle", 0.025);
}

function scoreSound() {
    tone(880, 0.12, "sine", 0.045);
    tone(1175, 0.15, "sine", 0.035, 0.08);
}

function loseSound() {
    stopMusic();
    if (!soundOn) return;
    tone(330, 0.22, "sawtooth", 0.045);
    tone(247, 0.32, "sawtooth", 0.04, 0.18);
    tone(165, 0.55, "triangle", 0.05, 0.43);
}

function winSound() {
    if (!soundOn) return;
    [523.25, 659.25, 783.99, 1046.5, 1318.5].forEach((f, i) => {
        tone(f, 0.24, "triangle", 0.055, i * 0.09);
    });
}

function toggleSound() {
    soundOn = !soundOn;
    soundBtn.textContent = soundOn ? "🔊 SOUND ON" : "🔇 SOUND OFF";
    if (!soundOn) {
        stopMusic();
    } else if (state === "playing") {
        getAudio();
        startMusic();
    }
}

soundBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleSound();
});

function addBurst(x, y, count = 65) {
    for (let i = 0; i < count; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = 1.5 + Math.random() * 5;
        particles.push({
            x, y,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            life: 0.8 + Math.random() * 0.7,
            maxLife: 1.5,
            size: 2 + Math.random() * 4,
            color: `hsl(${Math.random() * 360},100%,60%)`,
            gravity: 0.08 + Math.random() * 0.07
        });
    }
}

function celebrate() {
    if (score <= 0 || score % 10 !== 0 || score === lastCelebration) return;

    lastCelebration = score;
    celebrationUntil = performance.now() + 2400;
    celebrateText.textContent = "🎉 " + score + " POINTS! 🎉";
    celebrateText.style.display = "block";
    celebrateText.style.animation = "none";
    void celebrateText.offsetWidth;
    celebrateText.style.animation = "pop .3s ease-out";

    addBurst(W * 0.5, H * 0.32, 90);
    addBurst(W * 0.22, H * 0.43, 35);
    addBurst(W * 0.78, H * 0.43, 35);
    winSound();
}

function startGame() {
    getAudio();
    resetGame();
    state = "playing";
    overlay.style.display = "none";
    celebrateText.style.display = "none";
    startMusic();
    bird.vy = -5.5;
    flapSound();
}

function gameOver() {
    if (state !== "playing") return;

    state = "over";
    stopMusic();
    loseSound();

    if (score > best) {
        best = score;
        try {
            localStorage.setItem("flappyBirdBest", String(best));
        } catch (e) {}
    }
    updateScore();

    titleEl.textContent = "💥 GAME OVER";
    messageEl.innerHTML =
        "Điểm của bạn: <b>" + score + "</b><br>" +
        "Điểm cao nhất: <b>" + best + "</b><br>" +
        "Chọn chế độ rồi thử lại nhé!";
    mainBtn.textContent = "🔄 CHƠI LẠI";
    overlay.style.display = "flex";
}

mainBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    startGame();
});

modeButtons.forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        mode = btn.dataset.mode;
        modeButtons.forEach(b => b.classList.toggle("selected", b === btn));

        if (state === "playing") {
            resetGame();
            startMusic();
        }
    });
});

function flap() {
    if (state === "playing") {
        bird.vy = -5.4;
        bird.angle = -0.45;
        bird.flap = 1;
        flapSound();
    }
}

game.addEventListener("pointerdown", (e) => {
    if (e.target.closest("button") || e.target.closest(".panel")) return;

    if (state === "playing") {
        flap();
    } else if (state === "menu" || state === "over") {
        // Buttons remain the reliable way to start/restart.
    }
});

window.addEventListener("keydown", (e) => {
    if (e.code === "Space" || e.code === "ArrowUp") {
        e.preventDefault();
        if (state === "playing") flap();
        else if (state === "menu" || state === "over") startGame();
    }
});

function roundRect(x, y, w, h, r) {
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, r);
}

function drawCloud(x, y, scale) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);
    ctx.fillStyle = "#ffffffbd";
    ctx.beginPath();
    ctx.arc(0, 7, 15, 0, Math.PI * 2);
    ctx.arc(18, 0, 20, 0, Math.PI * 2);
    ctx.arc(39, 8, 14, 0, Math.PI * 2);
    ctx.arc(20, 13, 18, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
}

function drawBackground(dt) {
    const sky = ctx.createLinearGradient(0, 0, 0, H);
    sky.addColorStop(0, "#42b9f5");
    sky.addColorStop(0.65, "#b6efff");
    sky.addColorStop(1, "#f4fcff");
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = "#fff5a8";
    ctx.beginPath();
    ctx.arc(W * 0.79, H * 0.16, Math.min(34, W * 0.09), 0, Math.PI * 2);
    ctx.fill();

    clouds.forEach(c => {
        drawCloud(c.x, c.y, c.s);
        if (state === "playing") c.x -= dt * 0.018 * c.s;
        if (c.x < -80) {
            c.x = W + 70;
            c.y = 40 + Math.random() * H * 0.4;
        }
    });

    // Distant city
    const baseY = H - 70;
    for (let i = 0; i < 14; i++) {
        const bw = W / 10;
        const x = (i * bw - (worldTime * 0.012) % bw);
        const bh = 25 + ((i * 37) % 60);
        ctx.fillStyle = i % 2 ? "#7dc8da" : "#8bd7df";
        ctx.fillRect(x, baseY - bh, bw + 2, bh);

        ctx.fillStyle = "#eaffb8";
        for (let j = 0; j < 3; j++) {
            ctx.fillRect(x + 5 + j * 9, baseY - bh + 9, 4, 5);
            ctx.fillRect(x + 5 + j * 9, baseY - bh + 22, 4, 5);
        }
    }

    ctx.fillStyle = "#67c95b";
    ctx.fillRect(0, H - 48, W, 48);

    ctx.fillStyle = "#a5e86a";
    ctx.fillRect(0, H - 48, W, 9);

    ctx.fillStyle = "#d6a65e";
    ctx.fillRect(0, H - 38, W, 38);

    ctx.strokeStyle = "#b78647";
    ctx.lineWidth = 2;
    for (let x = -20; x < W + 20; x += 25) {
        const xx = x - (worldTime * 0.07) % 25;
        ctx.beginPath();
        ctx.moveTo(xx, H - 28);
        ctx.lineTo(xx + 12, H - 20);
        ctx.stroke();
    }
}

function drawPipe(p) {
    const topH = p.center - p.gap / 2;
    const bottomY = p.center + p.gap / 2;
    const bottomH = H - 48 - bottomY;
    const x = p.x, w = p.w;
    const metal = p.hot && (mode === "hard" || mode === "impossible");

    const grad = ctx.createLinearGradient(x, 0, x + w, 0);
    if (metal) {
        grad.addColorStop(0, "#45515e");
        grad.addColorStop(0.22, "#e1e7ed");
        grad.addColorStop(0.48, "#737f8a");
        grad.addColorStop(0.72, "#d9e0e6");
        grad.addColorStop(1, "#3e4955");
    } else {
        grad.addColorStop(0, "#087c36");
        grad.addColorStop(0.25, "#46ed61");
        grad.addColorStop(0.55, "#16b83f");
        grad.addColorStop(1, "#05652b");
    }

    // Top pipe
    ctx.fillStyle = grad;
    ctx.fillRect(x, 0, w, topH);
    ctx.fillStyle = metal ? "#263744" : "#08782f";
    ctx.fillRect(x - 5, topH - 22, w + 10, 22);
    ctx.fillStyle = metal ? "#bdc9d3" : "#62f578";
    ctx.fillRect(x + 5, 0, 5, Math.max(0, topH - 23));

    // Bottom pipe
    ctx.fillStyle = grad;
    ctx.fillRect(x, bottomY, w, Math.max(0, bottomH));
    ctx.fillStyle = metal ? "#263744" : "#08782f";
    ctx.fillRect(x - 5, bottomY, w + 10, 22);
    ctx.fillStyle = metal ? "#bdc9d3" : "#62f578";
    ctx.fillRect(x + 5, bottomY + 22, 5, Math.max(0, bottomH - 22));

    if (metal) {
        ctx.strokeStyle = "#f4f7fa";
        ctx.lineWidth = 2;
        for (let yy = 20; yy < topH - 28; yy += 35) {
            ctx.beginPath();
            ctx.moveTo(x + 10, yy);
            ctx.lineTo(x + w - 8, yy);
            ctx.stroke();
        }
        for (let yy = bottomY + 35; yy < H - 48; yy += 35) {
            ctx.beginPath();
            ctx.moveTo(x + 10, yy);
            ctx.lineTo(x + w - 8, yy);
            ctx.stroke();
        }

        if (p.hot) {
            // Warning signs
            ctx.fillStyle = "#ffb000";
            ctx.strokeStyle = "#4a2810";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(x + w / 2, Math.max(28, topH - 52));
            ctx.lineTo(x + w / 2 - 13, Math.max(50, topH - 27));
            ctx.lineTo(x + w / 2 + 13, Math.max(50, topH - 27));
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
            ctx.fillStyle = "#4a2810";
            ctx.font = "bold 17px Arial";
            ctx.textAlign = "center";
            ctx.fillText("!", x + w / 2, Math.max(47, topH - 32));

            drawFlame(x + w / 2, topH + 4, -1);
            drawFlame(x + w / 2, bottomY - 4, 1);
        }
    }
}

function drawFlame(x, y, direction) {
    const flick = Math.sin(worldTime * 0.025 + x) * 5;
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(1, direction);

    ctx.fillStyle = "#ff3b14";
    ctx.beginPath();
    ctx.moveTo(-15, 0);
    ctx.quadraticCurveTo(-21, -17 - flick, -4, -31 - flick);
    ctx.quadraticCurveTo(-5, -15, 7, -28 - flick);
    ctx.quadraticCurveTo(21, -14, 15, 0);
    ctx.closePath();
    ctx.fill();

    ctx.fillStyle = "#ffb51b";
    ctx.beginPath();
    ctx.moveTo(-8, 0);
    ctx.quadraticCurveTo(-10, -13 - flick / 2, 0, -21 - flick);
    ctx.quadraticCurveTo(14, -10, 8, 0);
    ctx.closePath();
    ctx.fill();

    ctx.fillStyle = "#fff2a1";
    ctx.beginPath();
    ctx.ellipse(0, -6, 4, 8, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
}

function drawBird() {
    const r = bird.r;
    ctx.save();
    ctx.translate(bird.x, bird.y);
    ctx.rotate(bird.angle);

    // Glow
    ctx.shadowColor = "#ffe34a";
    ctx.shadowBlur = 13;

    // Tail
    ctx.fillStyle = "#ff8b24";
    ctx.beginPath();
    ctx.moveTo(-r * 0.75, 1);
    ctx.lineTo(-r * 1.55, -r * 0.45);
    ctx.lineTo(-r * 1.35, r * 0.55);
    ctx.closePath();
    ctx.fill();

    // Body gradient
    const body = ctx.createRadialGradient(-r * 0.3, -r * 0.4, 2, 0, 0, r * 1.4);
    body.addColorStop(0, "#fff88b");
    body.addColorStop(0.45, "#ffdf38");
    body.addColorStop(1, "#ff9e1c");
    ctx.fillStyle = body;
    ctx.beginPath();
    ctx.ellipse(0, 0, r * 1.23, r, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.shadowBlur = 0;

    // Belly
    ctx.fillStyle = "#fff3b2";
    ctx.beginPath();
    ctx.ellipse(r * 0.13, r * 0.36, r * 0.69, r * 0.48, -0.1, 0, Math.PI * 2);
    ctx.fill();

    // Wing
    ctx.save();
    ctx.rotate(Math.sin(worldTime * 0.035) * 0.35);
    ctx.fillStyle = "#f99b20";
    ctx.beginPath();
    ctx.ellipse(-r * 0.25, r * 0.12, r * 0.58, r * 0.34, -0.4, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#d66c16";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(-r * 0.55, r * 0.15);
    ctx.lineTo(-r * 0.05, r * 0.27);
    ctx.stroke();
    ctx.restore();

    // Crest
    ctx.fillStyle = "#ff5835";
    ctx.beginPath();
    ctx.moveTo(-r * 0.25, -r * 0.7);
    ctx.quadraticCurveTo(-r * 0.5, -r * 1.45, 0, -r * 1.05);
    ctx.quadraticCurveTo(r * 0.2, -r * 1.35, r * 0.3, -r * 0.8);
    ctx.closePath();
    ctx.fill();

    // Eye
    ctx.fillStyle = "#fff";
    ctx.beginPath();
    ctx.arc(r * 0.52, -r * 0.3, r * 0.33, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#162033";
    ctx.beginPath();
    ctx.arc(r * 0.62, -r * 0.28, r * 0.16, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#fff";
    ctx.beginPath();
    ctx.arc(r * 0.65, -r * 0.34, r * 0.055, 0, Math.PI * 2);
    ctx.fill();

    // Beak
    ctx.fillStyle = "#ff6b22";
    ctx.beginPath();
    ctx.moveTo(r * 0.95, -r * 0.03);
    ctx.lineTo(r * 1.65, r * 0.16);
    ctx.lineTo(r * 0.94, r * 0.4);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = "#d94a15";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Cheek
    ctx.fillStyle = "#ff986f";
    ctx.beginPath();
    ctx.arc(r * 0.48, r * 0.13, r * 0.15, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
}

function update(dt) {
    worldTime += dt;
    frame++;

    if (state === "playing") {
        bird.vy += 0.28 * (dt / 16.67);
        bird.y += bird.vy * (dt / 16.67);
        bird.angle = Math.min(1.15, Math.max(-0.55, bird.vy * 0.075));
        bird.flap *= 0.88;

        const speed = configs[mode].speed * (dt / 16.67);

        pipes.forEach(p => {
            p.x -= speed;

            if (!p.passed && p.x + p.w < bird.x) {
                p.passed = true;
                score++;
                scoreSound();
                updateScore();
                celebrate();

                if (score > best) {
                    best = score;
                    try {
                        localStorage.setItem("flappyBirdBest", String(best));
                    } catch (e) {}
                    updateScore();
                }
            }

            const bx = bird.x, by = bird.y, r = bird.r * 0.72;
            const top = p.center - p.gap / 2;
            const bottom = p.center + p.gap / 2;

            const overlapsX = bx + r > p.x - 5 && bx - r < p.x + p.w + 5;
            if (overlapsX && (by - r < top || by + r > bottom)) {
                gameOver();
            }

            if (p.hot && overlapsX) {
                const flameZone = 20;
                if (
                    (by - r < top + flameZone && by + r > top - 2) ||
                    (by + r > bottom - flameZone && by - r < bottom + 2)
                ) {
                    gameOver();
                }
            }
        });

        pipes = pipes.filter(p => p.x + p.w > -20);

        const spacing = W * configs[mode].spacing;
        while (pipes.length < 3) {
            const lastX = pipes.length
                ? Math.max(...pipes.map(p => p.x))
                : W;
            makePipe(Math.max(W + 30, lastX + spacing));
        }

        if (bird.y - bird.r < 0 || bird.y + bird.r > H - 48) {
            gameOver();
        }
    }

    particles.forEach(p => {
        p.x += p.vx * (dt / 16.67);
        p.y += p.vy * (dt / 16.67);
        p.vy += p.gravity * (dt / 16.67);
        p.life -= dt / 1000;
    });
    particles = particles.filter(p => p.life > 0);

    if (performance.now() > celebrationUntil) {
        celebrateText.style.display = "none";
    }
}

function drawParticles() {
    particles.forEach(p => {
        ctx.globalAlpha = Math.max(0, Math.min(1, p.life / p.maxLife));
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
    });
    ctx.globalAlpha = 1;
}

function draw() {
    drawBackground(16.67);
    pipes.forEach(drawPipe);
    drawBird();
    drawParticles();

    if (state === "menu") {
        ctx.fillStyle = "#ffffffdd";
        ctx.font = "bold 17px Arial";
        ctx.textAlign = "center";
        ctx.fillText("CHỌN CHẾ ĐỘ RỒI NHẤN BẮT ĐẦU", W / 2, H * 0.76);
    }

    if (state === "playing" && frame % 2 === 0) {
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 32px Arial";
        ctx.textAlign = "center";
        ctx.strokeStyle = "#22513c";
        ctx.lineWidth = 4;
        ctx.strokeText(String(score), W / 2, 80);
        ctx.fillText(String(score), W / 2, 80);
    }
}

function loop(now) {
    if (!lastTime) lastTime = now;
    const dt = Math.min(35, now - lastTime);
    lastTime = now;

    update(dt);
    draw();
    requestAnimationFrame(loop);
}

function init() {
    resize();
    resetBird();
    resetGame();

    state = "menu";
    overlay.style.display = "flex";
    titleEl.textContent = "FLAPPY BIRD HD";
    messageEl.innerHTML =
        "Bay qua các đường ống để ghi điểm!<br>" +
        "🎵 Nhạc nền • 💥 Nhạc khi thua<br>" +
        "🎉 Ăn mừng mỗi 10 điểm";
    mainBtn.textContent = "▶ BẮT ĐẦU CHƠI";
    updateScore();

    requestAnimationFrame(loop);
}

init();
})();
</script>
</body>
</html>
"""

components.html(game_html, height=760, scrolling=False)
