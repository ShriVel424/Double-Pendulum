let socket;
let ctx;
let canvas;
let running = false;

// Load star images
const star1 = new Image();
const star2 = new Image();
star1.src = "star1.png"; // You can use a different file for star2 if needed
star2.src = "star1.png"; // Currently using the same filename

function drawPendulum(x1, y1, x2, y2) {
  if (!ctx) return;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const cx = canvas.width / 2;
  const cy = 0; // Pendulum hangs from top center

  const px1 = cx + x1 * 200;
  const py1 = cy + y1 * 200;

  const px2 = px1 + x2 * 200;
  const py2 = py1 + y2 * 200;

  // Draw rods with glowing shooting star effect
  const gradient = ctx.createLinearGradient(cx, cy, px2, py2);
  gradient.addColorStop(0, "rgba(255, 255, 255, 0.9)");
  gradient.addColorStop(1, "rgba(255, 255, 255, 0.1)");

  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(px1, py1);
  ctx.lineTo(px2, py2);
  ctx.strokeStyle = gradient;
  ctx.lineWidth = 3;
  ctx.shadowColor = "#ffffff"; // Glow color
  ctx.shadowBlur = 10;
  ctx.stroke();

  // Reset shadow to avoid affecting stars
  ctx.shadowBlur = 0;
  ctx.shadowColor = "transparent";

  // Draw stars only if loaded
  const starSize = 48; // Increased size
  if (star1.complete && star1.naturalWidth !== 0) {
    ctx.drawImage(star1, px1 - starSize / 2, py1 - starSize / 2, starSize, starSize);
  }

  if (star2.complete && star2.naturalWidth !== 0) {
    ctx.drawImage(star2, px2 - starSize / 2, py2 - starSize / 2, starSize, starSize);
  }
}

function start() {
  if (running) return;
  running = true;

  if (!socket) {
    socket = io();

    socket.on("pendulum_data", (data) => {
      const { x1, y1, x2, y2 } = data;
      drawPendulum(x1, y1, x2, y2);
    });
  }

  socket.emit("start");
}

function stop() {
  if (!running) return;
  running = false;
  socket.emit("stop");
}

window.onload = () => {
  canvas = document.getElementById("pendulumCanvas");
  ctx = canvas.getContext("2d");
};
