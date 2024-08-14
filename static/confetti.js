// Confetti Animation Script
var canvas = document.getElementById("confetti");
var ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

var particles = [];
var particleCount = 150;
var colors = ["#ff4081", "#ffd700", "#ff5722", "#4caf50", "#1e88e5"];

for (var i = 0; i < particleCount; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height - canvas.height,
        r: Math.random() * 10 + 1,
        d: Math.random() * particleCount,
        color: colors[Math.floor(Math.random() * colors.length)],
        tilt: Math.random() * 10 - 10
    });
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (var i = 0; i < particleCount; i++) {
        var p = particles[i];
        ctx.beginPath();
        ctx.lineWidth = p.r / 2;
        ctx.strokeStyle = p.color;
        ctx.moveTo(p.x + p.tilt + p.r / 3, p.y);
        ctx.lineTo(p.x + p.tilt, p.y + p.r / 2);
        ctx.stroke();
    }

    update();
}

function update() {
    for (var i = 0; i < particleCount; i++) {
        var p = particles[i];
        p.y += Math.cos(p.d) + 1 + p.r / 2;
        p.x += Math.sin(1);
        p.tilt = Math.sin(p.d) * 15;

        if (p.y > canvas.height) {
            particles[i] = {
                x: Math.random() * canvas.width,
                y: -20,
                r: p.r,
                d: p.d,
                color: p.color,
                tilt: p.tilt
            };
        }
    }
}

setInterval(draw, 20);
