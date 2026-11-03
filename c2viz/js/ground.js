// c2viz/js/ground.js: the region's landscape from a generated world's ground truth (viz.json `land`, c2viz/ground.py; ENGINE.md §12): height, sea and lakes, rivers, terrain, cover and the roads' own cells, in the same plan the derived landscape gives (region.js), so everything drawn on it is unchanged.
(function (X) {
  "use strict";
  const { BIOMES, ECO_KIND, ECO_TINT, ECO_TREE, TERRAIN_KIND, TERRAIN_TINT, TREES, snowLies, WORLD_SCALE, edgeOf, parcelPlan, roadOut, hstr, levelOf, model, noise, splinePath } = X;
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
      wet: decode(Ly.wet, Uint8Array), place: decode(Ly.place, Uint16Array), places: Ly.places, jx: decode(Ly.jx, Int8Array), jy: decode(Ly.jy, Int8Array),
      temp: Ly.temp ? decode(Ly.temp, Int8Array) : null, eco: Ly.eco ? decode(Ly.eco, Uint8Array) : null, ecos: Ly.ecos || [], band: Ly.band ? decode(Ly.band, Uint8Array) : null };
    GROUND.set(V, Lg); return Lg;
  }
  // a cell's point in pixels (the generator's jittered point, so lines through cells are not on a lattice)
  const cellPx = (Lg, r, c) => { const i = r * Lg.nx + c; return [(c + Lg.jx[i] / 100 + 0.5) * PX, (r + Lg.jy[i] / 100 + 0.5) * PX]; };

  // the ground per pixel: the cell under it (nearest, its edge broken by noise), heights bilinear, open water by its share
  const BASE = new WeakMap();
  function groundBase(V) {
    let B = BASE.get(V); if (B) return B;
    const M = model(V), Lg = layers(V), nx = Lg.nx, ny = Lg.ny, W = nx * PX, H = ny * PX, N = W * H, n1 = noise(M.seed ^ 11);
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
    B = { Lg, W, H, N, cellAt, hm, wm, n1 }; BASE.set(V, B); return B;
  }
  // places at their sites; one whose drawing would stand in open water is moved to the nearest ground that holds it
  const GPOS = new WeakMap();
  const SPOTS = new WeakMap();
  function groundSpots(V) {                                                                    // where each place stands: needs no plan
    let pos = SPOTS.get(V); if (pos) return pos;
    const ST = V.static, LD = V.land, { Lg, W, H, wm } = groundBase(V), nx = Lg.nx, nids = Object.keys(ST.nodes).sort(), f = WORLD_SCALE, waterAt = (i) => wm[i];
    // places at their sites; one whose drawing would stand in open water is moved to the nearest ground that holds it
    pos = {};
    for (const n of nids) {
      const s = LD.sites[n]; let p;
      if (s) p = [(s[0] + 0.5) * PX, (s[1] + 0.5) * PX];
      else { let sx = 0, sy = 0, k = 0; Lg.place.forEach((v, i) => { if (v && ST.parcels[Lg.places[v]]?.node === n) { sx += i % nx; sy += (i / nx) | 0; k++; } }); p = k ? [(sx / k + 0.5) * PX, (sy / k + 0.5) * PX] : [W / 2, H / 2]; }
      const r = X.landEstimate(V, n) * f, wetShare = (cx, cy) => { let w = 0, t = 0; for (let a = 0; a < 24; a++) for (const q of [0.35, 0.7, 1.05]) { const x = Math.round(cx + Math.cos(a / 24 * 6.283) * r * q), y = Math.round(cy + Math.sin(a / 24 * 6.283) * r * q); if (x < 0 || y < 0 || x >= W || y >= H) { w++; t++; continue; } t++; if (waterAt(y * W + x)) w++; } return w / t; };
      let best = p, bc = wetShare(p[0], p[1]) * 10;
      if (bc > 0.5) for (let dd = PX * 2; dd <= r * 2.5; dd += PX * 2) for (let a = 0; a < 16; a++) { const q = [p[0] + Math.cos(a / 16 * 6.283) * dd, p[1] + Math.sin(a / 16 * 6.283) * dd], c = wetShare(q[0], q[1]) * 10 + dd / r; if (c < bc) { bc = c; best = q; } }
      pos[n] = best;
    }
    SPOTS.set(V, pos); return pos;
  }
  function groundPos(V) {
    let RS = GPOS.get(V); if (RS) return RS;
    const { W, H } = groundBase(V), pos = groundSpots(V), nids = Object.keys(V.static.nodes).sort(), G = {}, f = WORLD_SCALE;
    for (const n of nids) G[n] = parcelPlan(V, n);
    RS = { W, H, pos, G, nids, f, rad: (n) => G[n].land * f }; GPOS.set(V, RS); return RS;
  }
  // where a road leaves a place: the heading of its own cells (the generator's road rule) where they leave the place's drawing
  function groundOut(V, nid, rid) {
    const lr = (V.land.roads || {})[rid], r = V.static.roads[rid]; if (!lr || !r) return null;
    const { Lg } = groundBase(V), RS = groundPos(V), p = RS.pos[nid], P0 = RS.G[nid], f = RS.f;
    let pts = lr.cells.map(([rr, cc]) => cellPx(Lg, rr, cc)); if (r.b === nid) pts = pts.slice().reverse();
    const at = (d) => pts.find((q) => Math.hypot(q[0] - p[0], q[1] - p[1]) >= d) || pts[pts.length - 1];
    let d = RS.rad(nid) * 1.1, dir = [1, 0];
    for (let k = 0; k < 3; k++) {                                                                   // the heading where it crosses the plan's edge
      const q = at(d), l = Math.hypot(q[0] - p[0], q[1] - p[1]) || 1; dir = [(q[0] - p[0]) / l, (q[1] - p[1]) / l];
      const e = edgeOf(P0, dir[0], dir[1]); d = Math.hypot(e[0] - P0.mid[0], e[1] - P0.mid[1]) * f;
    }
    return { dir, cells: pts, from: d };
  }
  function groundPlan(V) {
    const M = model(V), ST = V.static, LD = V.land, { Lg, W, H, N, cellAt, hm, wm, n1 } = groundBase(V), { pos, G, nids, f, rad } = groundPos(V);
    const nx = Lg.nx, ny = Lg.ny, nA = noise(M.seed ^ 31), nW = noise(M.seed ^ 2), waterAt = (i) => wm[i];
    // the fields the painter reads: height (E), forest (F), wet (Wt), the wild land's kind, terrace level (0 open water), tint, woods
    const E = new Float32Array(N), F = new Float32Array(N), Wt = new Float32Array(N), kind = new Uint8Array(N), level = new Int8Array(N), tint = new Uint32Array(N), wood = new Uint8Array(N);
    const tree = new Uint8Array(N), temp = new Float32Array(N), hex = (h) => parseInt(h.slice(1), 16);
    const tints = Lg.terrains.map((t) => hex(TERRAIN_TINT[t] || "#7cb444")), kinds = Lg.terrains.map((t) => TERRAIN_KIND[t] ?? 0);
    // each ecosystem (newer cells, D2-191): its colour, its look, its trees; else the terrain's
    const eTint = Lg.ecos.map((e) => ECO_TINT[e] ? hex(ECO_TINT[e]) : null), eKind = Lg.ecos.map((e) => ECO_KIND[e]), eTree = Lg.ecos.map((e) => (ECO_TREE[e] || []).map((k) => TREES.indexOf(k)));
    const coverIx = (name) => Lg.covers.indexOf(name), FOREST = coverIx("forest"), HEATH = coverIx("heath"), DEEP = Lg.terrains.indexOf("deep forest"), nT = noise(M.seed ^ 13);
    const DENSE = [0.92, 0.72, 0.92, 1.01];                                                       // a wood's edge thinner, its core unbroken
    for (let i = 0; i < N; i++) {
      const ci = cellAt[i], x = i % W, y = (i / W) | 0, t = Lg.terrain[ci], cv = Lg.cover[ci], ec = Lg.eco ? Lg.eco[ci] : 0, band = Lg.band ? Lg.band[ci] : 0;
      E[i] = 0.15 + Math.max(0, hm[i]) / M_PER_E;
      Wt[i] = Lg.wet[ci] / 255;
      temp[i] = Lg.temp ? Lg.temp[ci] / 4 : 9 - Math.max(0, hm[i]) * 0.0065;
      F[i] = cv === FOREST ? (t === DEEP || band === 3 ? 1.25 : band === 1 ? 0.85 : 1) : 0;
      const k0 = ec ? (eKind[ec] ?? 0) : (cv === HEATH && kinds[t] === 0) ? 4 : kinds[t];
      kind[i] = k0 === 0 && cv !== FOREST && hm[i] > 650 ? 2 : k0;                                    // bare tops only well up
      tint[i] = (ec && eTint[ec] != null) ? eTint[ec] : tints[t];
      if (band === 3) tint[i] = ((tint[i] >> 16 & 255) * 0.85 << 16) | ((tint[i] >> 8 & 255) * 0.85 << 8) | ((tint[i] & 255) * 0.85);   // a wood's core, darker
      wood[i] = cv === FOREST && nW(x / 14, y / 14, 3) < DENSE[band] ? 1 : 0;
      if (wood[i] && ec && eTree[ec].length) tree[i] = eTree[ec][Math.floor(nT(x / 6, y / 6, 2) * eTree[ec].length * 0.999)];
      level[i] = waterAt(i) ? 0 : levelOf(E[i]);
    }
    // territories and the parcels of each place at its spot (as region.js)
    const cellNode = new Int16Array(N).fill(-1), cellPar = new Int16Array(N).fill(-1);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const jx = x + (n1(x / 40, y / 40, 3) - .5) * 80, jy = y + (n1(x / 40 + 7, y / 40, 3) - .5) * 80; let best = -1, bd = 1e18;
      for (let i = 0; i < nids.length; i++) { const dd = ((jx - pos[nids[i]][0]) ** 2 + (jy - pos[nids[i]][1]) ** 2) / (rad(nids[i]) + 40); if (dd < bd) { bd = dd; best = i; } }
      cellNode[y * W + x] = best;
      const n = nids[best], g = G[n], lx = Math.round(g.mid[0] + (x - pos[n][0]) / f), ly = Math.round(g.mid[1] + (y - pos[n][1]) / f);
      if (lx >= 0 && ly >= 0 && lx < g.W && ly < g.H) cellPar[y * W + x] = g.REG[ly * g.W + lx];
    }
    // a place stands level on its own drawing's ground (its parcels, and a little round them), at its site's height, its drawing
    // pushing back any water under it; trees stand up to its edge, not in a ring round it
    const LEV = 14, dist = new Uint8Array(N).fill(255), q = [];
    for (let i = 0; i < N; i++) if (cellPar[i] >= 0) { dist[i] = 0; q.push(i); }
    for (let k = 0; k < q.length; k++) { const i = q[k], x = i % W, d0 = dist[i]; if (d0 >= LEV) continue;
      for (const j of [x > 0 ? i - 1 : -1, x < W - 1 ? i + 1 : -1, i - W, i + W]) if (j >= 0 && j < N && dist[j] > d0 + 1) { dist[j] = d0 + 1; q.push(j); } }
    const e0 = {}; for (const n of nids) { const [px, py] = pos[n]; e0[n] = E[Math.max(0, Math.min(H - 1, py | 0)) * W + Math.max(0, Math.min(W - 1, px | 0))]; }
    for (let i = 0; i < N; i++) { const d = dist[i]; if (d > LEV) continue; const n = nids[cellNode[i]], t = 1 - d / LEV, sm = t * t * (3 - 2 * t);
      E[i] = E[i] * (1 - sm) + e0[n] * sm; if (sm > 0.5 || level[i] > 0) level[i] = levelOf(E[i]); if (d <= 2) { wood[i] = 0; F[i] = Math.min(F[i], 0.3); } }
    // rivers: the generator's river cells as lines, downstream along their flow, wider by class
    const HALF = [0, 0.9, 1.4, 2.2], rivers = [];
    for (const rv of LD.rivers || []) {
      let run = [], cls = rv.class[0] || 1;
      const flush = () => { if (run.length > 1) rivers.push({ pid: null, pids: [], n: null, half: HALF[cls] || 0.9, line: splinePath(run) }); };
      rv.cells.forEach(([r, c], k) => { const k2 = rv.class[k] || cls; const p = cellPx(Lg, r, c);
        if (k2 !== cls && run.length) { run.push(p); flush(); run = [p]; cls = k2; } else run.push(p); });
      flush();
    }
    // roads: their own cells (the generator's rule, recovered by c2viz/ground.py), from where each end's village roads reach the
    // edge of its drawing (roadOut: the same point close up) on along the cells
    const paths = {}, sidx = {};
    const toW = (n, x, y) => [pos[n][0] + (x - G[n].mid[0]) * f, pos[n][1] + (y - G[n].mid[1]) * f];
    for (const [rid, r] of Object.entries(ST.roads)) {
      const lr = (LD.roads || {})[rid]; if (!lr || !(r.a in G) || !(r.b in G)) continue;
      const pts = lr.cells.map(([rr, cc]) => cellPx(Lg, rr, cc)), oa = roadOut(V, r.a, rid), ob = roadOut(V, r.b, rid);
      const A0 = toW(r.a, oa.edge[0], oa.edge[1]), B0 = toW(r.b, ob.edge[0], ob.edge[1]);
      const out = (p) => Math.hypot(p[0] - pos[r.a][0], p[1] - pos[r.a][1]) > (oa.from || rad(r.a)) * 1.08 && Math.hypot(p[0] - pos[r.b][0], p[1] - pos[r.b][1]) > (ob.from || rad(r.b)) * 1.08;
      const keep = pts.map((p, k) => [p, k]).filter(([p]) => out(p));
      const way = splinePath([A0, ...keep.map(([p]) => p), B0]); paths[rid] = way;
      const b = lr.stretches || [];
      sidx[rid] = Array.from({ length: (r.stretches && r.stretches.length) || 1 }, (_, k) => {
        const lo = b[k] ?? 0, hi = b[k + 1] ?? (pts.length - 1), mid = pts[Math.round((lo + hi) / 2)] || pts[0]; let bi = 0, bd = 1e18;
        way.forEach((q, j) => { const d2 = (q[0] - mid[0]) ** 2 + (q[1] - mid[1]) ** 2; if (d2 < bd) { bd = d2; bi = j; } }); return bi; });
    }
    return { W, H, pos, f, G, nids, A: [], feats: [], E, F, Wt, kind, level, cellNode, cellPar, rivers, rad, tint, tintW: 0.7, paths, sidx, wood, tree, temp, snowy: (i, cal) => snowLies(temp[i], cal), ground: true, PX };
  }
  Object.assign(X, { groundBase, groundSpots, groundPos, groundOut, groundPlan, groundLayers: layers, GROUND_PX: PX });
})(C2X);
