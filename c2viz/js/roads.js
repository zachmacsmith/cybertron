// c2viz/js/roads.js: roads' winding ways and how they are painted (ramps over cliff faces, planks over water, a verge).
(function (X) {
  "use strict";
  const { rng } = X;
  // a road's way between two points: a curve through waypoints set off to either side (a presentation choice), every 0.7 px
  function windPath(x0, y0, x1, y1, seed, amp) {
    const R = rng(seed), L = Math.hypot(x1 - x0, y1 - y0) || 1, nx = -(y1 - y0) / L, ny = (x1 - x0) / L, k = Math.max(2, Math.min(7, Math.round(L / 40)));
    const pts = [[x0, y0]];
    for (let j = 1; j < k; j++) { const t = j / k, o = (R() - 0.5) * 2 * amp * L * Math.sin(Math.PI * t); pts.push([x0 + (x1 - x0) * t + nx * o, y0 + (y1 - y0) * t + ny * o]); }
    pts.push([x1, y1]);
    const out = [];
    for (let j = 0; j + 1 < pts.length; j++) { const p0 = pts[Math.max(0, j - 1)], p1 = pts[j], p2 = pts[j + 1], p3 = pts[Math.min(pts.length - 1, j + 2)], seg = Math.hypot(p2[0] - p1[0], p2[1] - p1[1]) || 1;
      for (let q = 0; q < seg; q += 0.7) { const t = q / seg, t2 = t * t, t3 = t2 * t, cr = (a, b, c, d) => 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
        out.push([cr(p0[0], p1[0], p2[0], p3[0]), cr(p0[1], p1[1], p2[1], p3[1])]); } }
    out.push([x1, y1]); return out;
  }
  function paintPath(paint, pts, wide, col, keep) { for (const [x, y] of pts) { if (keep && !keep(x, y)) continue; for (let a = 0; a <= wide; a++) for (let b = 0; b <= wide; b++) paint(x + a, y + b, col); } }
  const paintRoad = (P, occ, LV, W, H, face) => (x, y, col) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const i = y * W + x;
    P.put(x, y, LV[i] === 0 ? ((x + y) % 2 ? "#a0662f" : "#8a5a2a") : face && face[i] ? "#e6dcc4" : col); occ[i] = 3; };
  // a dark verge along every road painted (occ 3), so roads read as the backbone
  function verges(P, occ, LV, W, H, t) { for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) { const i = y * W + x; if (occ[i] === 3 || LV[i] <= 0) continue;
    if (occ[i - 1] === 3 || occ[i + 1] === 3 || occ[i - W] === 3 || occ[i + W] === 3) P.dark(x, y, t); } }
  function wind(paint, x, y, tx, ty, n, wide, col, dashed, out) {
    let hd = Math.atan2(ty - y, tx - x);
    for (let s = 0; s < 3000; s++) {
      if (Math.hypot(tx - x, ty - y) < 1.5) break;
      let dd = Math.atan2(ty - y, tx - x) - hd; dd = Math.atan2(Math.sin(dd), Math.cos(dd));
      hd += Math.max(-0.09, Math.min(0.09, dd)) + (n(x / 14 + 40, y / 14) - 0.5) * 0.14; x += Math.cos(hd); y += Math.sin(hd);
      if (out) out.push([x, y]);
      if (dashed && s % 3 === 2) continue;
      const w_ = +wide || 0; for (let a = 0; a <= w_; a++) for (let b = 0; b <= w_; b++) paint(x + a, y + b, col);
    }
  }
  Object.assign(X, { windPath, paintPath, paintRoad, verges, wind });
})(C2X);
