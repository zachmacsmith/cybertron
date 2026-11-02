// c2viz/js/ground.js: the region's landscape from a generated world's ground truth (viz.json `land`, c2viz/ground.py; ENGINE.md §12): height, sea and lakes, rivers, terrain, cover and the roads' own cells, in the same plan the derived landscape gives (region.js), so everything drawn on it is unchanged.
(function (X) {
  "use strict";
  const { BIOMES, TERRAIN_KIND, TERRAIN_TINT, WORLD_SCALE, geom, hstr, levelOf, model, noise, splinePath } = X;
  // Presentation choices (ENGINE.md §12): PX pixels a cell (a cell is 150 m, so a 50 km window is 1336 px); heights in bands of
  // M_PER_E metres to the renderer's 0..1 (a terrace every 105 m); places drawn at the region's one scale (WORLD_SCALE of their close
  // up), much larger than their real few cells, at their real site, moved off open water only as far as their drawing needs.
  const PX = 4, M_PER_E = 700, GROUND = new WeakMap();
  function decode(b64, T) { const s = atob(b64), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return new T(u.buffer); }
  function layers(V) {
    let Lg = GROUND.get(V); if (Lg) return Lg;
    const LD = V.land, Ly = LD.layers;
    Lg = { nx: LD.grid.nx, ny: LD.grid.ny, km: LD.grid.km, h: decode(Ly.h, Int16Array), cover: decode(Ly.cover, Uint8Array), covers: Ly.covers,
      terrain: decode(Ly.terrain, Uint8Array), terrains: Ly.terrains, river: decode(Ly.river, Uint8Array), water: decode(Ly.water, Uint8Array),
      wet: decode(Ly.wet, Uint8Array), place: decode(Ly.place, Uint16Array), places: Ly.places, jx: decode(Ly.jx, Int8Array), jy: decode(Ly.jy, Int8Array) };
    GROUND.set(V, Lg); return Lg;
  }
  // a cell's point in pixels (the generator's jittered point, so lines through cells are not on a lattice)
  const cellPx = (Lg, r, c) => { const i = r * Lg.nx + c; return [(c + Lg.jx[i] / 100 + 0.5) * PX, (r + Lg.jy[i] / 100 + 0.5) * PX]; };

  function groundPlan(V) {
    const M = model(V), ST = V.static, LD = V.land, Lg = layers(V), nids = Object.keys(ST.nodes).sort(), G = {};
    for (const n of nids) G[n] = geom(V, n);
    const f = WORLD_SCALE, rad = (n) => G[n].land * f, nx = Lg.nx, ny = Lg.ny, W = nx * PX, H = ny * PX, N = W * H;
    const n1 = noise(M.seed ^ 11), nA = noise(M.seed ^ 31), nW = noise(M.seed ^ 2);
    // per pixel: the cell under it (nearest, its edge broken by noise so shores and woods are not squares), and heights bilinear
    const cellAt = new Int32Array(N), hm = new Float32Array(N), wm = new Uint8Array(N);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const jx = (n1(x / 9, y / 9, 2) - 0.5) * PX * 1.1, jy = (n1(x / 9 + 5, y / 9, 2) - 0.5) * PX * 1.1;
      const c = Math.max(0, Math.min(nx - 1, Math.floor((x + jx) / PX))), r = Math.max(0, Math.min(ny - 1, Math.floor((y + jy) / PX)));
      cellAt[y * W + x] = r * nx + c;
      const fx = x / PX - 0.5, fy = y / PX - 0.5, c0 = Math.max(0, Math.min(nx - 2, Math.floor(fx))), r0 = Math.max(0, Math.min(ny - 2, Math.floor(fy))), tx = Math.max(0, Math.min(1, fx - c0)), ty = Math.max(0, Math.min(1, fy - r0));
      const H0 = Lg.h[r0 * nx + c0], H1 = Lg.h[r0 * nx + c0 + 1], H2 = Lg.h[(r0 + 1) * nx + c0], H3 = Lg.h[(r0 + 1) * nx + c0 + 1];
      hm[y * W + x] = (H0 * (1 - tx) * (1 - ty) + H1 * tx * (1 - ty) + H2 * (1 - tx) * ty + H3 * tx * ty) / 10;
      const w_ = (k) => (Lg.water[k] & 3) ? 1 : 0, ws = w_(r0 * nx + c0) * (1 - tx) * (1 - ty) + w_(r0 * nx + c0 + 1) * tx * (1 - ty) + w_((r0 + 1) * nx + c0) * (1 - tx) * ty + w_((r0 + 1) * nx + c0 + 1) * tx * ty;
      wm[y * W + x] = ws + (n1(x / 6 + 3, y / 6, 2) - 0.5) * 0.5 > 0.5 ? 1 : 0;             // open water: its share between cells, a shore not a lattice
    }
    const waterAt = (i) => wm[i];
    // places at their sites; one whose drawing would stand in open water is moved to the nearest ground that holds it
    const pos = {};
    for (const n of nids) {
      const s = LD.sites[n]; let p;
      if (s) p = [(s[0] + 0.5) * PX, (s[1] + 0.5) * PX];
      else { let sx = 0, sy = 0, k = 0; Lg.place.forEach((v, i) => { if (v && ST.parcels[Lg.places[v]]?.node === n) { sx += i % nx; sy += (i / nx) | 0; k++; } }); p = k ? [(sx / k + 0.5) * PX, (sy / k + 0.5) * PX] : [W / 2, H / 2]; }
      const r = rad(n), wetShare = (cx, cy) => { let w = 0, t = 0; for (let a = 0; a < 24; a++) for (const q of [0.35, 0.7, 1.05]) { const x = Math.round(cx + Math.cos(a / 24 * 6.283) * r * q), y = Math.round(cy + Math.sin(a / 24 * 6.283) * r * q); if (x < 0 || y < 0 || x >= W || y >= H) { w++; t++; continue; } t++; if (waterAt(y * W + x)) w++; } return w / t; };
      let best = p, bc = wetShare(p[0], p[1]) * 10;
      if (bc > 0.5) for (let dd = PX * 2; dd <= r * 2.5; dd += PX * 2) for (let a = 0; a < 16; a++) { const q = [p[0] + Math.cos(a / 16 * 6.283) * dd, p[1] + Math.sin(a / 16 * 6.283) * dd], c = wetShare(q[0], q[1]) * 10 + dd / r; if (c < bc) { bc = c; best = q; } }
      pos[n] = best;
    }
    // the fields the painter reads: height (E), forest (F), wet (Wt), the wild land's kind, terrace level (0 open water), tint, woods
    const E = new Float32Array(N), F = new Float32Array(N), Wt = new Float32Array(N), kind = new Uint8Array(N), level = new Int8Array(N), tint = new Uint32Array(N), wood = new Uint8Array(N);
    const tints = Lg.terrains.map((t) => parseInt((TERRAIN_TINT[t] || "#7cb444").slice(1), 16)), kinds = Lg.terrains.map((t) => TERRAIN_KIND[t] ?? 0);
    const coverIx = (name) => Lg.covers.indexOf(name), FOREST = coverIx("forest"), HEATH = coverIx("heath"), DEEP = Lg.terrains.indexOf("deep forest");
    for (let i = 0; i < N; i++) {
      const ci = cellAt[i], x = i % W, y = (i / W) | 0, t = Lg.terrain[ci], cv = Lg.cover[ci];
      E[i] = 0.15 + Math.max(0, hm[i]) / M_PER_E;
      Wt[i] = Lg.wet[ci] / 255;
      F[i] = cv === FOREST ? (t === DEEP ? 1.2 : 1) : 0;
      kind[i] = E[i] > 0.78 ? 2 : (cv === HEATH && kinds[t] === 0) ? 4 : kinds[t];
      tint[i] = tints[t];
      wood[i] = cv === FOREST && nW(x / 14, y / 14, 3) < 0.92 ? 1 : 0;
      level[i] = waterAt(i) ? 0 : levelOf(E[i]);
    }
    // a place stands level on its own ground, at its site's height; its drawing pushes back water it would stand in
    for (const n of nids) { const r = rad(n), [px, py] = pos[n], e0 = E[Math.max(0, Math.min(H - 1, py | 0)) * W + Math.max(0, Math.min(W - 1, px | 0))];
      for (let y = Math.max(0, py - r * 1.4 | 0); y < Math.min(H, py + r * 1.4); y++) for (let x = Math.max(0, px - r * 1.4 | 0); x < Math.min(W, px + r * 1.4); x++) {
        const dd = Math.hypot(x - px, y - py) * (0.8 + 0.4 * nA(x / 25 + 3, y / 25, 2)), t = Math.max(0, Math.min(1, (r * 1.35 - dd) / (r * 0.4))); if (t <= 0) continue;
        const i = y * W + x, sm = t * t * (3 - 2 * t); E[i] = E[i] * (1 - sm) + e0 * sm; if (sm > 0.5 || level[i] > 0) level[i] = levelOf(E[i]); } }
    // territories and the parcels of each place at its spot (as region.js)
    const cellNode = new Int16Array(N).fill(-1), cellPar = new Int16Array(N).fill(-1);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const jx = x + (n1(x / 40, y / 40, 3) - .5) * 80, jy = y + (n1(x / 40 + 7, y / 40, 3) - .5) * 80; let best = -1, bd = 1e18;
      for (let i = 0; i < nids.length; i++) { const dd = ((jx - pos[nids[i]][0]) ** 2 + (jy - pos[nids[i]][1]) ** 2) / (rad(nids[i]) + 40); if (dd < bd) { bd = dd; best = i; } }
      cellNode[y * W + x] = best;
      const n = nids[best], g = G[n], lx = Math.round(g.mid[0] + (x - pos[n][0]) / f), ly = Math.round(g.mid[1] + (y - pos[n][1]) / f);
      if (lx >= 0 && ly >= 0 && lx < g.W && ly < g.H) cellPar[y * W + x] = g.REG[ly * g.W + lx];
      if (Math.hypot(x - pos[n][0], y - pos[n][1]) < rad(n) * (0.95 + 0.4 * nA(x / 18 + 9, y / 18, 3))) { F[y * W + x] -= 0.35; wood[y * W + x] = 0; }   // open ground round a place, its edge ragged
    }
    // rivers: the generator's river cells as lines, downstream along their flow, wider by class
    const HALF = [0, 0.9, 1.4, 2.2], rivers = [];
    for (const rv of LD.rivers || []) {
      let run = [], cls = rv.class[0] || 1;
      const flush = () => { if (run.length > 1) rivers.push({ pid: null, pids: [], n: null, half: HALF[cls] || 0.9, line: splinePath(run) }); };
      rv.cells.forEach(([r, c], k) => { const k2 = rv.class[k] || cls; const p = cellPx(Lg, r, c);
        if (k2 !== cls && run.length) { run.push(p); flush(); run = [p]; cls = k2; } else run.push(p); });
      flush();
    }
    // roads: their own cells (the generator's rule, recovered by c2viz/ground.py), from each end's exit of the drawing
    const paths = {}, sidx = {};
    const toW = (n, x, y) => [pos[n][0] + (x - G[n].mid[0]) * f, pos[n][1] + (y - G[n].mid[1]) * f];
    const exitPt = (n, rid) => { const e = G[n].exits.find((q) => q.rid === rid); return e ? toW(n, e.fx, e.fy) : pos[n]; };
    for (const [rid, r] of Object.entries(ST.roads)) {
      const lr = (LD.roads || {})[rid]; if (!lr || !(r.a in G) || !(r.b in G)) continue;
      const pts = lr.cells.map(([rr, cc]) => cellPx(Lg, rr, cc));
      const out = (p) => Math.hypot(p[0] - pos[r.a][0], p[1] - pos[r.a][1]) > rad(r.a) * 1.05 && Math.hypot(p[0] - pos[r.b][0], p[1] - pos[r.b][1]) > rad(r.b) * 1.05;
      const keep = pts.map((p, k) => [p, k]).filter(([p]) => out(p)), A0 = exitPt(r.a, rid), B0 = exitPt(r.b, rid);
      const way = splinePath([A0, ...keep.map(([p]) => p), B0]); paths[rid] = way;
      const b = lr.stretches || [];
      sidx[rid] = Array.from({ length: (r.stretches && r.stretches.length) || 1 }, (_, k) => {
        const lo = b[k] ?? 0, hi = b[k + 1] ?? (pts.length - 1), mid = pts[Math.round((lo + hi) / 2)] || pts[0]; let bi = 0, bd = 1e18;
        way.forEach((q, j) => { const d2 = (q[0] - mid[0]) ** 2 + (q[1] - mid[1]) ** 2; if (d2 < bd) { bd = d2; bi = j; } }); return bi; });
    }
    return { W, H, pos, f, G, nids, A: [], feats: [], E, F, Wt, kind, level, cellNode, cellPar, rivers, rad, tint, tintW: 0.7, paths, sidx, wood, ground: true, PX };
  }
  Object.assign(X, { groundPlan, groundLayers: layers, GROUND_PX: PX });
})(C2X);
