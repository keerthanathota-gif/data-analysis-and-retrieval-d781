// Minimal data + sparkline renderer
const users = [
  { name: "Emma Wilson", email: "emma.wilson@example.com", role: "Admin", status: "Active" },
  { name: "Sophia Lee", email: "sophia.lee@example.com", role: "Editor", status: "Pending" },
  { name: "Ava Johnson", email: "ava.johnson@example.com", role: "Viewer", status: "Inactive" },
  { name: "Olivia Brown", email: "olivia.brown@example.com", role: "Editor", status: "Active" },
  { name: "Mia Davis", email: "mia.davis@example.com", role: "Viewer", status: "Active" },
  { name: "Isabella Miller", email: "isabella.miller@example.com", role: "Admin", status: "Active" },
  { name: "Charlotte Wilson", email: "charlotte.wilson@example.com", role: "Viewer", status: "Pending" },
  { name: "Amelia Taylor", email: "amelia.taylor@example.com", role: "Editor", status: "Inactive" }
];

function createStatusBadge(status){
  const normalized = status.toLowerCase();
  if(normalized === "active") return `<span class="badge success">Active</span>`;
  if(normalized === "pending") return `<span class="badge pending">Pending</span>`;
  return `<span class="badge inactive">Inactive</span>`;
}

function populateTable(){
  const tbody = document.getElementById("user-rows");
  tbody.innerHTML = users.map(u => `
    <tr>
      <td>${u.name}</td>
      <td>${u.email}</td>
      <td>${u.role}</td>
      <td>${createStatusBadge(u.status)}</td>
      <td class="right">
        <div class="actions">
          <button class="action-btn edit">Edit</button>
          <button class="action-btn delete">Delete</button>
        </div>
      </td>
    </tr>
  `).join("");
}

function drawSparkline(canvasId, data, options={}){
  const canvas = document.getElementById(canvasId);
  if(!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.clientWidth || canvas.width;
  const height = canvas.height;
  // Fix high-DPI rendering
  const dpr = window.devicePixelRatio || 1;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  ctx.scale(dpr, dpr);

  // Clear
  ctx.clearRect(0,0,width,height);

  const paddingX = 6;
  const paddingY = 6;
  const minVal = Math.min(...data);
  const maxVal = Math.max(...data);
  const range = Math.max(maxVal - minVal, 1);

  const stepX = (width - paddingX*2) / (data.length - 1);

  // Gradient stroke
  const grad = ctx.createLinearGradient(0,0,width,0);
  grad.addColorStop(0, "#F9C2D8");
  grad.addColorStop(1, "#C7B3F6");

  ctx.lineWidth = 2;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  ctx.strokeStyle = grad;

  // Optional area fill
  const areaGrad = ctx.createLinearGradient(0,0,0,height);
  areaGrad.addColorStop(0, "rgba(249,194,216,0.35)");
  areaGrad.addColorStop(1, "rgba(199,179,246,0.05)");

  ctx.beginPath();
  data.forEach((v, i) => {
    const x = paddingX + i * stepX;
    const y = paddingY + (1 - (v - minVal) / range) * (height - paddingY*2);
    if(i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // Draw area
  ctx.lineTo(width - paddingX, height - paddingY);
  ctx.lineTo(paddingX, height - paddingY);
  ctx.closePath();
  ctx.fillStyle = areaGrad;
  ctx.fill();

  // Optional points
  if(options.points){
    ctx.fillStyle = "#ffffff";
    data.forEach((v, i) => {
      const x = paddingX + i * stepX;
      const y = paddingY + (1 - (v - minVal) / range) * (height - paddingY*2);
      ctx.beginPath();
      ctx.arc(x, y, 2.5, 0, Math.PI*2);
      ctx.fill();
      ctx.strokeStyle = "rgba(199,179,246,0.8)";
      ctx.stroke();
    });
  }
}

function initSparklines(){
  drawSparkline("spark-users", [12,14,11,16,18,17,21,20,22,24,23,25], { points:false });
  drawSparkline("spark-sessions", [6,7,9,8,11,13,12,14,13,15,16,18], { points:false });
  drawSparkline("spark-performance", [92,93,94,95,94,96,97,98,97,98,99,98], { points:false });
}

window.addEventListener("load", () => {
  populateTable();
  initSparklines();
  // Redraw on resize to maintain crisp lines
  window.addEventListener("resize", initSparklines);
});
