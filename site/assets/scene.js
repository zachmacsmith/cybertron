// Generated pixel scenery for the Cybertron "night village" design: a backdrop (night sky, two mountain ranges with a pink rim
// light, a cloud bank, a hill town) and a top-down village map per run. Both draw into a <canvas> at low resolution; show the
// canvas scaled up with `image-rendering: pixelated`. The same seed always gives the same picture.
//
//   backdrop(canvas, seed, { width: 320, height: 140, ground: "sand" | "meadow" | undefined })
//   village(canvas, seed, { n: 20, nMax: 26, camps: 4, roles: new Set(["legislator", "worker", ...]), width: 240, height: 150 })
//     n: agents alive now; nMax: the most the run ever has (fixes the plan, so round-by-round maps grow outwards)
//     roles: legislator worker scientist media board fixer maker observer deaths   (deaths: anyone died)
//   villageCfg(run)  -> a cfg for village() from a catalog row (+ optional viewer.json instance)
//   PALETTE          -> the design's colours

export const PALETTE = {
  sky: ["#1b2444", "#202b50", "#26335c"], farLit: "#45417f", farShade: "#36346c", nearLit: "#35316c", nearShade: "#29265a",
  rim: "#c4507a", rim2: "#d0607e", mauve: "#8a4a86", streak: "#5a4f92",
  cloud: ["#d6f0f2", "#9ccfe0", "#6aa6c4"], sand: ["#d9a25e", "#c78f4e", "#e8b878"], meadow: ["#6a9a3a", "#5a8a2e", "#82b24a"],
  cream: "#f6ead0", town: "#f0e8dc", townShade: "#c8b8a0", wheat: "#e8c060", roof: "#c8553d", wood: "#6b4423",
};

export function rng(s) { return function () { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
export function hstr(s) { let h = 2166136261; for (const c of String(s)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }
export function noise(seed) {
  const H = (x, y) => { let h = (seed ^ Math.imul(x, 374761393) ^ Math.imul(y, 668265263)) | 0; h = Math.imul(h ^ h >>> 13, 1274126177); return ((h ^ h >>> 16) >>> 0) / 4294967296; };
  const sm = (t) => t * t * (3 - 2 * t);
  const v = (x, y) => { const ix = Math.floor(x), iy = Math.floor(y), fx = sm(x - ix), fy = sm(y - iy); const a = H(ix, iy), b = H(ix + 1, iy), c = H(ix, iy + 1), d = H(ix + 1, iy + 1); return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy; };
  return (x, y, o = 4) => { let s = 0, a = 1, f = 1, n = 0; for (let i = 0; i < o; i++) { s += v(x * f + i * 17.3, y * f + i * 9.1) * a; n += a; a *= 0.5; f *= 2; } return s / n; };
}
const C = (h) => parseInt(h.slice(1), 16);
export function Px(cv, W, H, bg) {
  cv.width = W; cv.height = H;
  const g = cv.getContext("2d"), img = g.createImageData(W, H), d = img.data, buf = new Uint32Array(W * H).fill(bg ? C(bg) : 0);
  const put = (x, y, c) => { x |= 0; y |= 0; if (x >= 0 && y >= 0 && x < W && y < H) buf[y * W + x] = typeof c === "string" ? C(c) : c; };
  const get = (x, y) => buf[(y | 0) * W + (x | 0)];
  const dark = (x, y, t) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const c = buf[y * W + x]; buf[y * W + x] = ((c >> 16 & 255) * (1 - t) << 16) | ((c >> 8 & 255) * (1 - t) << 8) | ((c & 255) * (1 - t)); };
  const flush = () => { for (let i = 0; i < W * H; i++) { const c = buf[i]; d[i * 4] = c >> 16 & 255; d[i * 4 + 1] = c >> 8 & 255; d[i * 4 + 2] = c & 255; d[i * 4 + 3] = 255; } g.putImageData(img, 0, 0); };
  return { put, get, dark, flush, W, H };
}
export function tree(P, x, y, r, R) {
  const cols = ["#2f7d3a", "#3a8a3e", "#286e34"], c = cols[(R() * 3) | 0];
  for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (dx * dx + dy * dy <= r * r + 0.5) P.dark(x + dx + 1, y + dy + 1, 0.35);
  for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) { if (dx * dx + dy * dy > r * r + 0.5) continue; P.put(x + dx, y + dy, dx + dy < -r + 0.5 ? "#58a648" : dx + dy > r - 0.5 ? "#1f5a2a" : c); }
}

// ------------------------------------------------------------------ backdrop
export function backdrop(cv, seedStr, opts = {}) {
  const W = opts.width || 320, H = opts.height || 140, R = rng(hstr(seedStr)), n = noise(hstr(seedStr) ^ 7), P = Px(cv, W, H);
  const k = H / 140, bands = PALETTE.sky;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const t = y / (95 * k) * 3; let b = Math.min(2, Math.floor(t)); if (t - b > 0.8 && b < 2 && (x + y) % 2) b++; P.put(x, y, bands[b]); }
  for (let i = 0; i < 110 * W / 320; i++) P.put(R() * W, R() * 80 * k, R() < 0.2 ? "#f6c8d8" : R() < 0.5 ? "#ffffff" : "#aab4d8");
  for (let i = 0; i < 8 * W / 320; i++) { const x = R() * W | 0, y = R() * 60 * k | 0; P.put(x, y, "#ffffff"); for (const [a, b] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) P.put(x + a, y + b, "#c8d0f0"); }
  const ridge = (off, base, amp, lit, shade, rim, rim2, streak) => {
    const h = (x) => base + (n(x / 55 + off, off) - 0.5) * amp + (n(x / 13 + off, off + 3) - 0.5) * amp * 0.25;
    for (let x = 0; x < W; x++) {
      const y0 = h(x) | 0, s = h(x - 1) - h(x);
      for (let y = y0; y < H; y++) P.put(x, y, s > 0 ? lit : shade);
      if (s > 0.25) { P.put(x, y0, rim); P.put(x, y0 + 1, rim2); if (R() < 0.18) { let yy = y0 + 3, xx = x; for (let q = 0; q < 6 + R() * 10; q++) { P.put(xx, yy, streak); yy++; if (q % 2) xx++; } } }
    }
  };
  ridge(0, 60 * k, 70 * k, PALETTE.farLit, PALETTE.farShade, PALETTE.rim, PALETTE.mauve, PALETTE.streak);
  const cy = 80 * k;
  for (let i = -10; i < W + 10; i += 6) {
    const cx = i + R() * 5, cyy = cy + R() * 10 - 5, r = 5 + R() * 9;
    for (let y = Math.floor(cyy - r); y < Math.min(cy + 7, cyy + r); y++) for (let x = Math.floor(cx - r); x < cx + r; x++) {
      if ((x - cx) ** 2 + (y - cyy) ** 2 > r * r) continue;
      P.put(x, y, y - (cyy - r) < 2.5 ? PALETTE.cloud[0] : y > cyy + r * 0.3 ? PALETTE.cloud[2] : PALETTE.cloud[1]);
    }
  }
  ridge(40, 96 * k, 48 * k, PALETTE.nearLit, PALETTE.nearShade, PALETTE.rim2, "#7a3e78", "#3f3a7c");
  const green = opts.ground ? opts.ground === "meadow" : R() < 0.5, g = green ? PALETTE.meadow : PALETTE.sand;
  const fh = (x) => 116 * k + (n(x / 70 + 100, 9) - 0.5) * 20 * k;
  for (let x = 0; x < W; x++) for (let y = fh(x) | 0; y < H; y++) { const v = n(x / 4, y / 3, 2); P.put(x, y, v > 0.62 ? g[2] : v < 0.38 ? g[1] : g[0]); }
  if (opts.town !== false) {
    const tx = W * 0.62 + R() * W * 0.19;
    for (let q = 0; q < 26 * W / 320; q++) {
      const w = 4 + R() * 6 | 0, h = 4 + R() * 14 | 0, x0 = tx + (R() - 0.5) * 90 | 0, base = fh(x0 + w / 2) + 3 - Math.abs(x0 - tx) * 0.08, y0 = (base - h) | 0;
      for (let y = y0; y < base; y++) for (let x = x0; x < x0 + w; x++) P.put(x, y, x === x0 + w - 1 ? PALETTE.townShade : PALETTE.town);
      for (let y = y0 + 2; y < base - 1; y += 3) for (let x = x0 + 1; x < x0 + w - 1; x += 2) P.put(x, y, "#8a5a3a");
      for (let x = x0; x < x0 + w; x += 2) P.put(x, y0 - 1, PALETTE.town);
    }
    for (let i = 0; i < 40 * W / 320; i++) { const x = R() * W, y = fh(x) + 4 + R() * 20 * k; if (Math.abs(x - tx) < 40 && R() < 0.6) continue; tree(P, x, y, R() < 0.5 ? 2 : 1.5, R); }
  }
  P.flush();
  return P;
}

// ------------------------------------------------------------------ village map
const ROOFS = [["#c8553d", "#e07a5a", "#9a3a24"], ["#b8643a", "#d8824e", "#8a4424"], ["#a84a3a", "#c8684e", "#7a2e22"]];
function house(P, x0, y0, w, h, roof, wall) {
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    let c; const wy = h - 2;
    if (y === 0) c = roof[2]; else if (y < wy) c = x === 0 ? roof[1] : roof[0]; else c = x === 0 ? "#d8ccb4" : wall;
    if (y === wy && (x === 1 || x === w - 2)) c = "#7aaabe"; if (y === h - 1 && x === (w >> 1)) c = "#6b4423"; P.put(x0 + x, y0 + y, c);
  }
}
// a multi-storey home: roof, then a window on every other row and column
function tall(P, x0, y0, w, h, roof, wall) {
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    let c;
    if (y === 0) c = roof[2]; else if (y < 4) c = x === 0 ? roof[1] : roof[0]; else c = x === 0 ? "#d8ccb4" : wall;
    if (y >= 4 && y < h - 1 && (y - 4) % 2 === 1 && x % 2 === 1 && x < w - 1) c = "#7aaabe";
    if (y === h - 1 && x === (w >> 1)) c = "#6b4423"; P.put(x0 + x, y0 + y, c);
  }
}
// homes for a population: cottages for the first dozen, then taller homes that each count for 3, 5 or 10 agents
export function housing(n) {
  const caps = []; let rest = n - Math.min(n, 12);
  for (const [cap, min] of [[10, 20], [5, 12], [3, 4]]) while (rest >= min) { caps.push(cap); rest -= cap; }
  for (let i = n - caps.reduce((a, b) => a + b, 0); i > 0; i--) caps.push(1);
  return caps;
}
// the buildings a village can have; `role` is what makes one appear
export const BUILDINGS = {
  hall: { w: 9, h: 11, role: "legislator", name: "Town hall", why: "legislators", section: "laws",
    draw(P, x, y) { for (let j = 0; j < 11; j++) for (let i = 0; i < 9; i++) P.put(x + i, y + j, j === 0 ? "#5a5a64" : j < 4 ? (i < 2 ? "#aaaab4" : "#8a8a94") : (j >= 5 && j < 9 && (i === 2 || i === 6)) ? "#5a5a62" : (j >= 8 && i === 4) ? "#6b4423" : "#e0d8c8"); P.put(x + 4, y - 1, "#6b4423"); P.put(x + 4, y - 2, "#6b4423"); P.put(x + 5, y - 2, "#c8553d"); P.put(x + 6, y - 2, "#c8553d"); } },
  press: { w: 9, h: 7, role: "media", name: "Print shop", why: "an editor", section: "chronicle",
    draw(P, x, y) { house(P, x, y, 9, 7, ["#4878c8", "#6a98e0", "#30508a"], "#f2e8d4"); for (let i = 1; i < 8; i++) P.put(x + i, y + 4, i % 2 ? "#2b1d14" : "#f6ead0"); } },
  archive: { w: 10, h: 8, role: "scientist", name: "Archive", why: "scientists", section: "data",
    draw(P, x, y) { for (let j = 0; j < 8; j++) for (let i = 0; i < 10; i++) { if (j < 4) { if (Math.abs(i - 4.5) <= 2 + j) P.put(x + i, y + j, i < 4 ? "#e0e0e8" : "#b8b8c4"); } else P.put(x + i, y + j, j === 4 ? "#a8a29a" : (i % 3 === 1 && j < 7) ? "#8a8a94" : "#e0d8c8"); } } },
  workshop: { w: 8, h: 6, role: "fixer", name: "Workshop", why: "a Fixer",
    draw(P, x, y) { house(P, x, y, 8, 6, ["#e8803a", "#f0a060", "#a85a20"], "#e8dcc4"); P.put(x + 6, y - 1, "#6a6a72"); P.put(x + 6, y - 2, "#6a6a72"); P.put(x + 7, y - 4, "#d8d8d8"); P.put(x + 6, y - 5, "#e8e8e8"); P.put(x + 7, y - 6, "#f0f0f0"); } },
  manor: { w: 13, h: 8, role: "board", name: "Manor", why: "a Board",
    draw(P, x, y) { house(P, x, y, 13, 8, ["#7a5aa0", "#9a7ac0", "#5a3a80"], "#f2e8d4"); for (let i = 2; i < 11; i += 4) P.put(x + i, y, "#e8b83c"); P.put(x + 6, y - 1, "#e8b83c"); P.put(x + 6, y - 2, "#e8b83c"); } },
  nursery: { w: 7, h: 6, role: "maker", name: "Nursery", why: "a Maker",
    draw(P, x, y) { house(P, x, y, 7, 6, ["#e07aa0", "#f0a0c0", "#a84a70"], "#fff0f4"); } },
  tower: { w: 4, h: 12, role: "observer", name: "Watchtower", why: "a secret observer",
    draw(P, x, y) { for (let j = 0; j < 12; j++) for (let i = 0; i < 4; i++) P.put(x + i, y + j, j < 2 ? "#7a2e22" : j === 2 ? "#4a2f17" : (j === 4 && i === 1) ? "#2a1a10" : i === 0 ? "#a0662f" : "#8a5a2a"); } },
  graves: { w: 9, h: 6, role: "deaths", name: "Graveyard", why: "anyone died",
    draw(P, x, y) { for (let j = 0; j < 6; j++) for (let i = 0; i < 9; i++) { const edge = j === 0 || j === 5 || i === 0 || i === 8; P.put(x + i, y + j, edge ? ((i + j) % 2 ? "#6b4423" : "#8a5a2a") : "#6ca63c"); } for (let j = 1; j < 5; j += 2) for (let i = 2; i < 8; i += 2) { P.put(x + i, y + j, "#c8c4bc"); P.put(x + i, y + j + 1, "#8a867e"); } } },
  mine: { w: 5, h: 4, role: "worker", name: "Mine", why: "workers (one per camp)",
    draw(P, x, y) { for (let j = 0; j < 4; j++) for (let i = 0; i < 5; i++) P.put(x + i, y + j, (j >= 1 && i >= 1 && i <= 3) ? "#2a2420" : j === 0 ? "#8a5a2a" : (i === 0 || i === 4) ? "#8a5a2a" : "#2a2420"); P.put(x + 5, y + 3, "#9a9aa0"); P.put(x + 6, y + 3, "#9a9aa0"); } },
};

// returns { square:[x,y], places:[{kind, x, y, w, h}], houses:[{x, y, w, h, agents}] } in canvas pixels, so pages can put
// hotspots on it. cfg.n is the population to house now; cfg.nMax (default n) the most the run ever has, which fixes the plan,
// so drawing round by round with the same nMax shows the village growing outwards with earlier buildings kept.
export function village(cv, seedStr, cfg) {
  const N = cfg.n, roles = cfg.roles instanceof Set ? cfg.roles : new Set(cfg.roles || []), W = cfg.width || 240, H = cfg.height || 150;
  const h0 = hstr(seedStr), R = rng(h0), n1 = noise(h0 ^ 1), n2 = noise(h0 ^ 2), n3 = noise(h0 ^ 3), P = Px(cv, W, H);
  const sea = Math.floor(R() * 5), L = new Int8Array(W * H), occ = new Uint8Array(W * H), at = (x, y) => (x < 0 || y < 0 || x >= W || y >= H) ? -1 : L[(y | 0) * W + (x | 0)];
  const out = { places: [], houses: [], square: null, width: W, height: H };
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { let e = (n1(x / 75, y / 75, 4) - 0.5) * 1.7 + 0.55; const de = [y, W - 1 - x, H - 1 - y, x][sea]; if (sea < 4) e -= Math.max(0, 1 - de / 50) * 0.65; L[y * W + x] = e < 0.3 ? 0 : e < 0.5 ? 1 : e < 0.66 ? 2 : 3; }
  const GR = [null, ["#8cc04c", "#9cd05a", "#7cb042"], ["#7cb444", "#8cc452", "#6ca43a"], ["#6ca63c", "#7cb64a", "#5c9632"]];
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const l = L[y * W + x];
    if (l === 0) { let s = false; for (const [a, b] of [[2, 0], [-2, 0], [0, 2], [0, -2], [1, 1], [-1, -1]]) if (at(x + a, y + b) > 0) s = true; P.put(x, y, s ? (n3(x / 2, y / 2, 1) > 0.6 ? "#d8f0f0" : "#7cc0c8") : (n3(x / 6, y / 3, 2) > 0.6 ? "#5aa2b4" : "#4e94a8")); continue; }
    const v = n3(x / 3, y / 3, 2); P.put(x, y, GR[l][v > 0.62 ? 1 : v < 0.36 ? 2 : 0]);
  }
  const FACE = ["#e6e2d6", "#d2ccbc", "#bdb5a2", "#a69c88"], cliffTops = [];
  for (let y = 0; y < H - 1; y++) for (let x = 0; x < W; x++) {
    const l = L[y * W + x]; if (l <= 0) continue;
    if (at(x, y + 1) < l && at(x, y + 1) > 0) { let k = 1; for (; k <= 4; k++) { if (at(x, y + k) >= l || y + k >= H) break; } if (k > 4) cliffTops.push([x, y]); }
    if (at(x, y + 1) < l) { P.put(x, y, "#b0dc6a"); for (let k = 1; k <= 4; k++) { if (at(x, y + k) >= l || y + k >= H) break; P.put(x, y + k, FACE[Math.min(3, k - 1 + (x % 3 === 0 ? 1 : 0))]); } }
    else if (at(x + 1, y) < l || at(x - 1, y) < l) P.put(x, y, "#5a9030");
  }
  // The layout is planned for the largest population the run reaches (cfg.nMax), and a village drawn for an earlier round
  // shows a prefix of the same plan: earlier buildings stay, and it grows outwards from the square.
  const NM = Math.max(N, cfg.nMax || N);
  let best = null, bs = -1;
  for (let i = 0; i < 300; i++) { const x = W / 6 + R() * W * 2 / 3 | 0, y = H / 5 + R() * H * 0.6 | 0, l = at(x, y); if (l < 1) continue; let s = 0; for (let dy = -22; dy <= 22; dy += 3) for (let dx = -22; dx <= 22; dx += 3) if (at(x + dx, y + dy) === l) s++; if (s > bs) { bs = s; best = [x, y, l]; } }
  const [cx, cy, vl] = best, VR = 8 + Math.sqrt(Math.min(NM, 40)) * 4.4;
  out.square = [cx, cy];
  // a plot is free when it sits on one terrace (lv), clear of everything planned, and not on a cliff edge
  const free = (x0, y0, w, h, pad = 1, lv = vl) => { for (let y = y0 - pad; y < y0 + h + pad; y++) for (let x = x0 - pad; x < x0 + w + pad; x++) { if (at(x, y) !== lv || occ[y * W + x]) return false; if (at(x, y + 2) !== lv) return false; } return true; };
  const mark = (x0, y0, w, h, v) => { for (let y = y0; y < y0 + h; y++) for (let x = x0; x < x0 + w; x++) if (x >= 0 && y >= 0 && x < W && y < H) occ[y * W + x] = v; };
  const shadow = (x0, y0, w, h) => { for (let y = y0 + 1; y <= y0 + h; y++) P.dark(x0 + w, y, 0.38); for (let x = x0 + 1; x <= x0 + w; x++) P.dark(x, y0 + h, 0.38); };
  const mines = [];
  if (roles.has("worker")) {
    const cand = cliffTops.filter(([x, y]) => { const d = Math.hypot(x - cx, y - cy); return d > VR + 8 && d < VR + 60; }).sort(() => R() - 0.5);
    for (const [x, y] of cand) { if (mines.length >= (cfg.camps || 3)) break; if (mines.some(([a, b]) => Math.hypot(a - x, b - y) < 22)) continue; BUILDINGS.mine.draw(P, x - 2, y + 1); mark(x - 4, y - 2, 10, 8, 6); mines.push([x, y + 5]); out.places.push({ kind: "mine", x: x - 2, y: y + 1, w: 5, h: 4 }); }
  }
  // roads: a main street through the square from one edge of the map to the other (and a cross street in a bigger
  // village), each turning gently; the fields and mines join the nearest road, not the square
  const ROAD = C("#d8b47a"), LANE = C("#e2c896"), RAMP = C("#ece6d6");
  const paint = (x, y, col) => { if (at(x, y) < 1) return; const o = occ[y * W + x]; if (o === 2 || o === 6) return; const g = P.get(x, y);
    P.put(x, y, g >= C("#a69c88") && g <= C("#e6e2d6") ? RAMP : (o === 3 && col === LANE) ? ROAD : col); occ[y * W + x] = 3; };
  const road = (x, y, tx, ty, wide, join) => {
    let hd = Math.atan2(ty - y, tx - x);
    for (let s = 0; s < 700; s++) {
      if (Math.hypot(tx - x, ty - y) < 1.5) break;
      let d = Math.atan2(ty - y, tx - x) - hd; d = Math.atan2(Math.sin(d), Math.cos(d));
      hd += Math.max(-0.09, Math.min(0.09, d)) + (n2(x / 14 + 40, y / 14) - 0.5) * 0.14;
      let nx = x + Math.cos(hd), ny = y + Math.sin(hd), k = 0;
      while (at(nx, ny) === 0 && k < 12) { hd += k % 2 ? -0.3 * k : 0.3 * k; nx = x + Math.cos(hd); ny = y + Math.sin(hd); k++; }
      if (at(nx, ny) < 1) break;
      x = nx; y = ny;
      if (join && s > 3 && occ[(y | 0) * W + (x | 0)] === 3) break;
      paint(x | 0, y | 0, wide ? ROAD : LANE); if (wide) { paint((x | 0) + 1, y | 0, ROAD); paint(x | 0, (y | 0) + 1, ROAD); paint((x | 0) + 1, (y | 0) + 1, ROAD); }
    }
  };
  // distance to the nearest road over land, so fields and homes can line the streets
  const rd = new Int16Array(W * H);
  const roadDist = () => { rd.fill(999); const q = []; for (let i = 0; i < W * H; i++) if (occ[i] === 3) { rd[i] = 0; q.push(i); }
    for (let qi = 0; qi < q.length; qi++) { const i = q[qi], x = i % W, y = (i / W) | 0; for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const xx = x + dx, yy = y + dy; if (at(xx, yy) < 1) continue; const j = yy * W + xx; if (rd[j] > rd[i] + 1) { rd[j] = rd[i] + 1; q.push(j); } } } };
  const edgeAt = (a) => { let x = cx, y = cy; while (x > 1 && y > 1 && x < W - 2 && y < H - 2) { x += Math.cos(a); y += Math.sin(a); } return [x, y]; };
  const a0 = R() * Math.PI, streets = NM >= 15 ? [a0, a0 + Math.PI, a0 + Math.PI / 2 + (R() - 0.5) * 0.6] : [a0, a0 + Math.PI];
  if (NM >= 30) streets.push(a0 - Math.PI / 2 + (R() - 0.5) * 0.6);
  for (const a of streets) { const [ex, ey] = edgeAt(a); road(cx, cy, ex, ey, true, false); }
  roadDist();
  // fields: patchworks of two or three crops behind a hedge, laid against a road at the edge of the village
  const FC = [["#e8c840", "#d4ac30"], ["#a8d050", "#8cb83e"], ["#b8865a", "#9a6e46"], ["#c8dc60", "#b0c448"], ["#d8c060", "#bca44a"]], fields = [], hedgeTrees = [];
  const nf = roles.has("worker") ? Math.min(7, 1 + Math.round(NM / 6)) : 1, HEDGE = "#4f8a34";
  for (let t = 0, k = 0; t < 900 && k < nf; t++) {
    const a = R() * 6.28, r = VR + 2 + R() * 40, w = 14 + R() * 16 | 0, h = 10 + R() * 8 | 0, x0 = cx + Math.cos(a) * r * 1.2 - w / 2 | 0, y0 = cy + Math.sin(a) * r - h / 2 | 0;
    const lv = at(x0, y0); if (lv < 1 || !free(x0, y0, w, h, 1, lv)) continue;
    let near = false;
    for (let x = x0; x < x0 + w; x += 2) if (rd[Math.max(0, y0 - 2) * W + x] <= 1 || rd[Math.min(H - 1, y0 + h + 1) * W + x] <= 1) near = true;
    for (let y = y0; y < y0 + h; y += 2) if (rd[y * W + Math.max(0, x0 - 2)] <= 1 || rd[y * W + Math.min(W - 1, x0 + w + 1)] <= 1) near = true;
    if (!near) continue;
    const long = w >= h, span = long ? w : h, nplots = 1 + (R() * 3 | 0), cut = [], crops = [], rows = [];
    for (let i = 1; i < nplots; i++) cut.push(Math.round(span * i / nplots + (R() - 0.5) * 3));
    for (let i = 0; i < nplots; i++) { crops.push(FC[R() * FC.length | 0]); rows.push(R() < 0.5); }
    for (let y = y0; y < y0 + h; y++) for (let x = x0; x < x0 + w; x++) {
      const ex = x === x0 || x === x0 + w - 1, ey = y === y0 || y === y0 + h - 1;
      if (ex && ey) continue;                                                       // rounded corners
      const u = long ? x - x0 : y - y0, plot = cut.filter((c) => u >= c).length;
      if (ex || ey) { if (n3(x / 2 + 9, y / 2) < 0.68) P.put(x, y, HEDGE); if (R() < 0.05) hedgeTrees.push([x, y]); continue; }
      if (cut.includes(u)) { P.put(x, y, HEDGE); continue; }
      const c = crops[plot], v = rows[plot] ? x : y, sp = n3(x * 1.7, y * 1.7, 1);
      P.put(x, y, (v % 2) ? c[1] : sp > 0.78 ? c[1] : c[0]);
    }
    mark(x0 - 1, y0 - 1, w + 2, h + 2, 2); fields.push([x0 + w / 2, y0 + h / 2]); out.places.push({ kind: "field", x: x0, y: y0, w, h }); k++;
  }
  const nearestRoad = (x, y) => { let bd = 1e9, bp = [cx, cy]; for (let yy = 0; yy < H; yy += 2) for (let xx = 0; xx < W; xx += 2) if (occ[yy * W + xx] === 3) { const d = (xx - x) ** 2 + (yy - y) ** 2; if (d < bd) { bd = d; bp = [xx, yy]; } } return bp; };
  for (const [tx, ty] of mines) { const [rx, ry] = nearestRoad(tx, ty); road(tx, ty, rx, ry, false, true); }
  roadDist();
  const sr = 4 + Math.round(Math.sqrt(Math.min(NM, 40)) * 0.7);
  out.squareR = sr;
  for (let y = -sr; y <= sr; y++) for (let x = -sr - 1; x <= sr + 1; x++) if (x * x / ((sr + 1) ** 2) + y * y / (sr * sr) <= 1) occ[(cy + y) * W + cx + x] = 5;
  // plan: the institutions next to the square, then the homes, biggest first, each at the nearest free plot to the square
  const plan = [];
  const place = (b, rMin, anyLevel) => {
    for (let r = rMin; r < Math.max(W, H); r += 1.5) for (let t = 0; t < 28; t++) {
      const a = R() * 6.28, x0 = cx + Math.cos(a) * r * 1.2 - b.w / 2 | 0, y0 = cy + Math.sin(a) * r - b.h / 2 | 0;
      const lv = anyLevel && r > VR ? at(x0, y0 + b.h - 1) : vl;
      if (lv < 1 || !free(x0, y0, b.w, b.h, 1, lv)) continue;
      if (b.kind === "home" && !b.anywhere && rd[Math.min(H - 1, y0 + b.h + 1) * W + Math.min(W - 1, x0 + (b.w >> 1))] > 3 + (r - rMin) / 5) continue;
      mark(x0 - 1, y0 - (b.top || 1), b.w + 2, b.h + (b.top || 1) + 1, 4); const p = { ...b, x: x0, y: y0, r }; plan.push(p); return p;
    }
    return null;
  };
  for (const k of ["hall", "manor", "archive", "press", "workshop", "nursery"]) if (roles.has(BUILDINGS[k].role)) place({ kind: k, w: BUILDINGS[k].w, h: BUILDINGS[k].h, top: 3 }, sr + 3, false);
  const homes = [];
  const dims = (cap, wide) => cap === 10 ? [11, 15] : cap === 5 ? [9, 12] : cap === 3 ? [8, 9] : [wide ? 9 : 7, 6];
  for (const cap of housing(NM)) { const wide = R() < 0.3, [w, h] = dims(cap, wide); const b = { kind: "home", cap, w, h, wide, roof: ROOFS[R() * 3 | 0] }, p = place(b, sr + 2, true) || place({ ...b, anywhere: true }, sr + 2, true); if (p) homes.push(p); }
  const edge = Math.max(VR * 0.9, ...homes.map((p) => p.r)) + 3;
  for (const k of ["tower", "graves"]) if (roles.has(BUILDINGS[k].role)) place({ kind: k, w: BUILDINGS[k].w, h: BUILDINGS[k].h }, edge, true);
  // what stands now: every institution, and homes in plan order until they house today's population
  // the plots are sized for the biggest population; a smaller one fills the same plots in order with smaller homes (a cottage
  // where a tall house will later stand), so the centre grows taller and the edge grows outwards as the run grows
  const caps = housing(N); let housed = 0, hi = 0;
  const shown = plan.filter((p) => p.kind !== "home");
  for (const p of homes) {
    if (housed >= N) break;
    const cap = Math.min(caps[hi++] || 1, p.cap), [w, h] = dims(cap, p.wide);
    shown.push({ ...p, cap, w, h, x: p.x + ((p.w - w) >> 1), y: p.y + p.h - h }); housed += cap;
  }
  // the village ground under what stands, the square, its well and market
  for (const p of shown) for (let y = p.y - 3; y < p.y + p.h + 3; y++) for (let x = p.x - 3; x < p.x + p.w + 3; x++) {
    const o = occ[y * W + x], g = P.get(x, y); if (at(x, y) !== at(p.x, p.y + p.h - 1) || o === 2 || o === 3 || o === 6 || g === C("#b0dc6a")) continue;
    const dx = Math.max(p.x - x, x - (p.x + p.w - 1), 0), dy = Math.max(p.y - y, y - (p.y + p.h - 1), 0);
    if (dx + dy <= 1 + 2.2 * n2(x / 5, y / 5, 2)) P.put(x, y, n3(x / 2, y / 2, 1) > 0.6 ? "#c8b07a" : "#d8c48e");
  }
  for (let y = -sr; y <= sr; y++) for (let x = -sr - 1; x <= sr + 1; x++) if (x * x / ((sr + 1) ** 2) + y * y / (sr * sr) <= 1) P.put(cx + x, cy + y, "#cdb88a");
  for (let y = -1; y <= 1; y++) for (let x = -1; x <= 1; x++) P.put(cx + x, cy + y, x || y ? "#9a9aa0" : "#4e94a8");
  if (N >= 15) for (let k = 0; k < Math.min(4, Math.floor(N / 8)); k++) { const a = k * 1.57 + 0.6, x0 = cx + Math.cos(a) * (sr - 2) - 1 | 0, y0 = cy + Math.sin(a) * (sr - 2) | 0; for (let i = 0; i < 4; i++) { P.put(x0 + i, y0, i % 2 ? "#f6ead0" : "#c8553d"); P.put(x0 + i, y0 + 1, "#8a5a2a"); } }
  for (const p of shown.slice().sort((a, b) => (a.y + a.h) - (b.y + b.h))) {
    shadow(p.x, p.y, p.w, p.h);
    if (p.kind === "home") { if (p.cap === 1) house(P, p.x, p.y, p.w, p.h, p.roof, "#f2e8d4"); else tall(P, p.x, p.y, p.w, p.h, p.cap === 10 ? ["#8a8a94", "#aaaab4", "#5a5a64"] : p.roof, p.cap === 10 ? "#e0d8c8" : "#f2e8d4"); out.houses.push({ x: p.x, y: p.y, w: p.w, h: p.h, agents: p.cap }); }
    else { BUILDINGS[p.kind].draw(P, p.x, p.y); out.places.push({ kind: p.kind, x: p.x, y: p.y, w: p.w, h: p.h }); }
  }
  // a lane from each home's door down to the nearest road
  for (const p of shown) {
    if (p.kind !== "home") continue;
    let x = p.x + (p.w >> 1), y = p.y + p.h; if (rd[y * W + x] > 10) continue;
    for (let s = 0; s < 12 && rd[y * W + x] > 0; s++) {
      if (occ[y * W + x] !== 4) paint(x, y, LANE);
      let bx = x, by = y; for (const [dx, dy] of [[0, 1], [1, 0], [-1, 0], [0, -1]]) { const xx = x + dx, yy = y + dy; if (at(xx, yy) >= 1 && rd[yy * W + xx] < rd[by * W + bx]) { bx = xx; by = yy; } }
      if (bx === x && by === y) break; x = bx; y = by;
    }
  }
  // a palisade around a big village: just outside its outermost buildings, angle by angle
  if (N >= 25) {
    const bins = new Array(90).fill(0);
    for (const p of shown) for (const [x, y] of [[p.x, p.y], [p.x + p.w, p.y], [p.x, p.y + p.h], [p.x + p.w, p.y + p.h]]) { const b = Math.floor(((Math.atan2(y - cy, (x - cx) / 1.2) + Math.PI) / (2 * Math.PI)) * 90) % 90; bins[b] = Math.max(bins[b], Math.hypot((x - cx) / 1.2, y - cy)); }
    const rad = bins.map((_, i) => Math.max(...[-2, -1, 0, 1, 2].map((d) => bins[(i + d + 90) % 90])) + 4);
    for (let a = 0; a < 6.283; a += 0.01) { const i = Math.floor(((a) / (2 * Math.PI)) * 90) % 90, r = rad[i], x = cx + Math.cos(a - Math.PI) * r * 1.2 | 0, y = cy + Math.sin(a - Math.PI) * r | 0, o = occ[y * W + x];
      if (at(x, y) < 1 || at(x, y + 1) !== at(x, y) || (o && o !== 4) || o === 4) continue; P.put(x, y, "#6b4423"); P.put(x, y - 1, "#8a5a2a"); occ[y * W + x] = 7; }
  }
  // forests, cleared around everything the village has planned
  const core = homes.length ? homes.map((p) => p.r).sort((a, b) => a - b)[Math.floor(homes.length * 0.6)] + 4 : sr + 6;
  const clear = (x, y) => (Math.hypot((x - cx) / 1.2, y - cy) < core && at(x, y) === vl) || plan.some((p) => x > p.x - 6 && x < p.x + p.w + 6 && y > p.y - 6 && y < p.y + p.h + 6);
  const trees = [];
  for (let gy = 0; gy < H; gy += 3) for (let gx = 0; gx < W; gx += 3) { const x = gx + R() * 2, y = gy + R() * 2, l = at(x, y); if (l < 1 || occ[(y | 0) * W + (x | 0)] || clear(x, y)) continue; if (n2(x / 30, y / 30, 3) > 0.54 || R() < 0.008) trees.push([x, y]); }
  trees.push(...hedgeTrees);
  trees.sort((a, b) => a[1] - b[1]);
  for (const [x, y] of trees) { let ok = true; for (let k = -3; k <= 3; k++) if (at(x + k, y + 3) < 1 || occ[((y + 3) | 0) * W + ((x + k) | 0)] >= 4) ok = false; if (ok) tree(P, x, y, R() < 0.6 ? 2 : 2.6, R); }
  for (let k = 0; k < 12; k++) { const x = R() * W | 0, y = R() * H | 0; if (at(x, y) < 1 || occ[y * W + x]) continue; for (let dy = 0; dy < 3; dy++) for (let dx = 0; dx < 4; dx++) P.put(x + dx, y + dy, dx + dy === 0 ? "#e8e8e0" : dx + dy >= 4 ? "#9a9a92" : "#c8c8c0"); P.dark(x + 4, y + 2, 0.35); }
  for (const [fx, fy] of fields.slice(0, 3)) for (let k = 0; k < 3; k++) { const x = fx + (R() - 0.5) * 30 | 0, y = fy + (R() - 0.5) * 20 | 0; if (at(x, y) < 1 || occ[y * W + x]) continue; P.put(x, y, "#ffffff"); P.put(x + 1, y, "#ffffff"); P.put(x + 2, y, "#3a2a2a"); }
  P.flush();
  return out;
}

// a village() cfg from a catalog row, plus the run's viewer.json instance if you have it (for roles, camps and deaths)
export function villageCfg(row, viewer) {
  const roles = new Set();
  let n = row.n_agents || 12, camps = 3;
  if (viewer) {
    const ags = viewer.instance.agents || [];
    for (const a of ags) { roles.add(a.cls); if ((a.rights || []).includes("maker")) roles.add("maker"); }
    if (viewer.instance.observer) roles.add("observer");
    const cs = new Set(); for (const a of ags) for (const r of a.rights || []) if (String(r).startsWith("harvest:")) cs.add(r); camps = Math.max(1, Math.min(6, cs.size || 3));
    if ((viewer.events || []).some((e) => e.type === "disabled" || e.type === "depart")) roles.add("deaths");   // a death is a "disabled" event
  } else ["legislator", "worker", "scientist"].forEach((r) => roles.add(r));
  return { n, camps, roles };
}
