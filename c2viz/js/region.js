// c2viz/js/region.js: the region's landscape built from the engine's land facts (ENGINE.md §9): places laid out by their roads, heights, woods, rivers at fords, peaks; the same landscape sampled close up.
(function (X) {
  "use strict";
  const { BIOMES, TERRAIN_LAND, geom, hstr, model, noise, rng, windPath } = X;
  // ---------------------------------------------------------------------------------------------------- the region's landscape
  // A presentation choice built from what the engine says about the land between places (ENGINE.md §9): each place stands at the
  // height of its parcels (or, where a world sets no heights, its rock and its name: a crag, a tor, a pass, a moor, a mere); each
  // day's stretch of road stands at its terrain's height and carries its terrain (woodland grows forest, marsh is wet, a river
  // valley is low); a pass is a ridge of mountains with a saddle where the road goes over; narrows are rocks close by the road; a
  // ford or a bridge is a river crossing the road, traced downhill. Between these the land eases from one to the next, with a
  // little noise; it is shaded by its relief. Places are drawn at a fixed scale and roads at a fixed length a day, so a larger
  // world is a larger map to explore, not a smaller drawing.
  const REGION = new WeakMap(), PERDAY = 60, WORLD_SCALE = 0.5;
  const levelOf = (e) => e > 0.78 ? 5 : 1 + Math.max(0, Math.min(3, Math.floor((e - 0.2) / 0.15)));
                                                      // [height, forest, wet]
  function regionPlan(V) {
    let RP = REGION.get(V); if (RP) return RP;
    if (V.land && X.groundPlan) { RP = X.groundPlan(V); REGION.set(V, RP); return RP; }   // a generated world: its ground truth (ground.js)
    const M = model(V), ST = V.static, WL = ST.layout.world || {}, nids = Object.keys(ST.nodes).sort(), G = {};
    for (const n of nids) G[n] = geom(V, n);
    const f = WORLD_SCALE, rad = (n) => G[n].land * f, rds = Object.entries(ST.roads).filter(([, r]) => r.a in G && r.b in G);
    const pos = {}; for (const n of nids) pos[n] = [(WL[n] || [500, 350])[0] * 1.6, (WL[n] || [500, 350])[1] * 1.6];
    for (let it = 0; it < 600; it++) {
      for (const [, r] of rds) { const a = pos[r.a], b = pos[r.b], dx = b[0] - a[0], dy = b[1] - a[1], dd = Math.hypot(dx, dy) || 1, k = (dd - (rad(r.a) + rad(r.b) + PERDAY * r.days)) / dd * 0.15;
        a[0] += dx * k; a[1] += dy * k; b[0] -= dx * k; b[1] -= dy * k; }
      for (const x of nids) for (const y of nids) { if (x >= y) continue; const a = pos[x], b = pos[y], dx = b[0] - a[0], dy = b[1] - a[1], dd = Math.hypot(dx, dy) || 0.01, want = rad(x) + rad(y) + 30;
        if (dd < want) { const k = (dd - want) / dd * 0.5; a[0] += dx * k; a[1] += dy * k; b[0] -= dx * k; b[1] -= dy * k; } }
    }
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const n of nids) { const r = rad(n); x0 = Math.min(x0, pos[n][0] - r); y0 = Math.min(y0, pos[n][1] - r); x1 = Math.max(x1, pos[n][0] + r); y1 = Math.max(y1, pos[n][1] + r); }
    const MGN = 70, W = Math.max(420, Math.ceil(x1 - x0 + 2 * MGN)), H = Math.max(280, Math.ceil(y1 - y0 + 2 * MGN));
    const ox = W / 2 - (x0 + x1) / 2, oy = H / 2 - (y0 + y1) / 2; for (const n of nids) pos[n] = [pos[n][0] + ox, pos[n][1] + oy];
    // the anchors: [x, y, sigma, height, forest, wet]
    const A = [], nodeE = {};
    for (const n of nids) {
      const ps = Object.values(ST.parcels).filter((p) => p.node === n), tot = ps.reduce((s, p) => s + (+p.size || 1), 0) || 1;
      const share = (c) => ps.filter((p) => p.cover === c).reduce((s, p) => s + (+p.size || 1), 0) / tot, name = (ST.nodes[n].name + " " + (ST.nodes[n].text || "")).toLowerCase();
      const set = ps.some((p) => (p.height ?? 1) !== 1); let e;
      if (set) e = 0.12 + 0.2 * ps.reduce((s, p) => s + (p.height ?? 1) * (+p.size || 1), 0) / tot;
      else e = 0.32 + 0.3 * share("rock") + 0.1 * share("scrub") + (/crag|tor\b|fell|pass|peak|mount|scar/.test(name) ? 0.32 : 0) + (/moor|heath|high/.test(name) ? 0.15 : 0) - (/mere|fen|marsh|carr|salt|mead|ford/.test(name) ? 0.1 : 0);
      const wet = Math.min(1, share("water") * 1.2 + (/mere|fen|marsh|carr|salt/.test(name) ? 0.5 : 0));
      A.push([pos[n][0], pos[n][1], rad(n) * 0.9 + 12, Math.min(0.95, e), share("forest") * 1.4, wet]); nodeE[n] = Math.min(0.95, e);
      if (e > 0.55) {
        const out = rds.filter(([, r]) => r.a === n || r.b === n).map(([, r]) => { const o = pos[r.a === n ? r.b : r.a]; return Math.atan2(o[1] - pos[n][1], o[0] - pos[n][0]); });
        for (let k = 0; k < 7; k++) { const t = k * 0.8976 + (hstr(n) % 100) / 50; if (out.some((a) => Math.abs(Math.atan2(Math.sin(t - a), Math.cos(t - a))) < 0.55)) continue;
          const rr = rad(n) + 26 + (hstr(n + k) % 20); A.push([pos[n][0] + Math.cos(t) * rr, pos[n][1] + Math.sin(t) * rr, 18, Math.min(1, e + 0.18), 0, 0]); }
      }
    }
    const feats = [], paths = {}, sidx = {};                                                 // each road's way, its stretches on it
    const toW = (n, x, y) => [pos[n][0] + (x - G[n].mid[0]) * f, pos[n][1] + (y - G[n].mid[1]) * f];
    const exitPt = (n, rid) => { const e = G[n].exits.find((q) => q.rid === rid); return e ? toW(n, e.fx, e.fy) : pos[n]; };
    for (const [rid, r] of rds) {
      const A0 = exitPt(r.a, rid), B0 = exitPt(r.b, rid), way = paths[rid] = windPath(A0[0], A0[1], B0[0], B0[1], hstr(rid), 0.1);
      let i0 = way.findIndex(([x, y]) => Math.hypot(x - pos[r.a][0], y - pos[r.a][1]) > rad(r.a)); if (i0 < 0) i0 = 0;
      let i1 = way.length - 1; while (i1 > i0 && Math.hypot(way[i1][0] - pos[r.b][0], way[i1][1] - pos[r.b][1]) <= rad(r.b)) i1--;
      const all = r.stretches && r.stretches.length ? r.stretches : [{ terrain: r.terrain }];
      sidx[rid] = all.map((_, k) => Math.round(i0 + (i1 - i0) * (k + 0.5) / all.length));
      all.forEach((st, k) => {
        const j = sidx[rid][k], [x, y] = way[j], q0 = way[Math.max(0, j - 4)], q1 = way[Math.min(way.length - 1, j + 4)], L = Math.hypot(q1[0] - q0[0], q1[1] - q0[1]) || 1, ux = (q1[0] - q0[0]) / L, uy = (q1[1] - q0[1]) / L;
        const T = TERRAIN_LAND[st.terrain || r.terrain || "farmland"] || TERRAIN_LAND.farmland;
        A.push([x, y, 28, T[0], T[1], T[2]]);
        for (const lm of st.landmarks || []) { const kd = lm.kind || lm, h = (hstr(rid + kd) % 2) ? 1 : -1;
          if (kd === "pass") { A.push([x - uy * 30, y + ux * 30, 20, 1.0, 0, 0], [x + uy * 30, y - ux * 30, 20, 1.0, 0, 0], [x - uy * 55, y + ux * 55, 18, 0.9, 0, 0], [x + uy * 55, y - ux * 55, 18, 0.9, 0, 0]); }
          if (kd === "narrows") { A.push([x - uy * 9, y + ux * 9, 6, 0.75, 0, 0], [x + uy * 9, y - ux * 9, 6, 0.75, 0, 0]); }
          if (kd === "hollow") A.push([x + uy * 10 * h, y - ux * 10 * h, 10, 0.12, 0.4, 0.4]);
          feats.push({ rid, k, kind: kd, x, y, ux, uy, state: lm.state }); }
      });
    }
    // the fields: height, forest, wet, and the kind of wild land
    const E = new Float32Array(W * H), F = new Float32Array(W * H), Wt = new Float32Array(W * H), kind = new Uint8Array(W * H);
    const nA = noise(M.seed ^ 31), nB = noise(M.seed ^ 37), nC = noise(M.seed ^ 41), nU = noise(M.seed ^ 43);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      let sw = 0.12, se = 0.12 * 0.3, sf = 0.12 * 0.15, sx = 0.12 * 0.1;
      for (const [ax, ay, sg, e, fo, we] of A) { const dd = (x - ax) ** 2 + (y - ay) ** 2; if (dd > 25 * sg * sg) continue; const w = Math.exp(-dd / (2 * sg * sg)); sw += w; se += w * e; sf += w * fo; sx += w * we; }
      let e = se / sw + (nA(x / 70, y / 70, 3) - 0.5) * 0.14 + (nU(x / 170, y / 170, 2) - 0.5) * 0.34;
      if (e > 0.6) e += (1 - Math.abs(nB(x / 16, y / 16, 3) * 2 - 1) - 0.5) * 0.3 * Math.min(1, (e - 0.6) / 0.3);   // ridged peaks
      const i = y * W + x; E[i] = e; F[i] = sf / sw + (nC(x / 40, y / 40, 2) - 0.5) * 0.5; Wt[i] = sx / sw + (nC(x / 30 + 9, y / 30, 2) - 0.5) * 0.3;
    }
    for (const n of nids) { const r = rad(n), [px, py] = pos[n];                                 // a place stands level on its own ground
      for (let y = Math.max(0, py - r * 1.4 | 0); y < Math.min(H, py + r * 1.4); y++) for (let x = Math.max(0, px - r * 1.4 | 0); x < Math.min(W, px + r * 1.4); x++) {
        const dd = Math.hypot(x - px, y - py) * (0.8 + 0.4 * nA(x / 25 + 3, y / 25, 2)), t = Math.max(0, Math.min(1, (r * 1.35 - dd) / (r * 0.4))); if (t <= 0) continue; const i = y * W + x, sm = t * t * (3 - 2 * t); E[i] = E[i] * (1 - sm) + nodeE[n] * sm; } }
    const level = new Int8Array(W * H);
    for (let i = 0; i < W * H; i++) { const e = E[i]; level[i] = levelOf(e); kind[i] = e > 0.78 ? 2 : e > 0.56 ? 1 : (Wt[i] > 0.55 && e < 0.35) ? 3 : 0; }
    // territories and the parcels of each place at its spot
    const n1 = noise(M.seed ^ 11), cellNode = new Int16Array(W * H).fill(-1), cellPar = new Int16Array(W * H).fill(-1);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const jx = x + (n1(x / 40, y / 40, 3) - .5) * 80, jy = y + (n1(x / 40 + 7, y / 40, 3) - .5) * 80; let best = -1, bd = 1e18;
      for (let i = 0; i < nids.length; i++) { const dd = ((jx - pos[nids[i]][0]) ** 2 + (jy - pos[nids[i]][1]) ** 2) / (rad(nids[i]) + 40); if (dd < bd) { bd = dd; best = i; } }
      cellNode[y * W + x] = best;
      const n = nids[best], g = G[n], lx = Math.round(g.mid[0] + (x - pos[n][0]) / f), ly = Math.round(g.mid[1] + (y - pos[n][1]) / f);
      if (lx >= 0 && ly >= 0 && lx < g.W && ly < g.H) cellPar[y * W + x] = g.REG[ly * g.W + lx];
      if (Math.hypot(x - pos[n][0], y - pos[n][1]) < rad(n) * 1.15) F[y * W + x] -= 0.35;   // open ground round a place
    }
    // rivers where roads cross water (a ford, a bridge), traced downhill from the crossing, and a little way up to their source
    const rivers = [], sinks = [];
    for (const n of nids) for (const [pid, P0] of Object.entries(ST.parcels)) if (P0.node === n && P0.cover === "water") { const i = M.nodes[n].pids.indexOf(pid); if (i >= 0 && G[n].area[i].length) { const [cx, cy] = G[n].centre[i]; sinks.push([pos[n][0] + (cx - G[n].mid[0]) * f, pos[n][1] + (cy - G[n].mid[1]) * f]); } }
    for (const a of A) if (a[5] >= 0.9) sinks.push([a[0], a[1]]);
    for (const ft of feats) if (ft.kind === "ford" || ft.kind === "bridge") {
      const tR = rng(hstr(ft.rid + ft.k)), px0 = -ft.uy, py0 = ft.ux;
      const target = (sgn) => { let best = null, bd = 1e18; for (const [sx, sy] of sinks) { const v = (sx - ft.x) * px0 + (sy - ft.y) * py0, dd = Math.hypot(sx - ft.x, sy - ft.y); if (sgn * v > 4 && dd < bd && dd > 20) { bd = dd; best = [sx, sy]; } }
        return best || [ft.x + sgn * px0 * 400, ft.y + sgn * py0 * 400]; };
      const run = (sgn, steps) => { const out = [], [tx, ty] = target(sgn); let x = ft.x, y = ft.y, hd = Math.atan2(sgn * py0, sgn * px0);
        for (let s = 0; s < steps; s++) { let dd = Math.atan2(ty - y, tx - x) - hd; dd = Math.atan2(Math.sin(dd), Math.cos(dd));
          hd += Math.max(-0.12, Math.min(0.12, dd * 0.15)) + (tR() - 0.5) * 0.35; x += Math.cos(hd) * 1.5; y += Math.sin(hd) * 1.5;
          if (x < 1 || y < 1 || x > W - 2 || y > H - 2 || Math.hypot(tx - x, ty - y) < 6) break; out.push([x, y]); }
        return out; };
      const down = run(1, 260), up = run(-1, 50);
      rivers.push({ pid: null, pids: [], n: null, half: 1.8, line: up.reverse().concat([[ft.x, ft.y]], down) });
    }
    const tint = new Uint32Array(W * H), rgb = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
    const base = nids.map((n) => rgb(BIOMES[M.nodes[n].biome].grass[0][0]));
    for (let y = 0; y < H; y += 1) for (let x = 0; x < W; x += 1) { let sw = 0, r = 0, g = 0, b = 0;
      nids.forEach((n, k) => { const sg = rad(n) + 90, w = Math.exp(-((x - pos[n][0]) ** 2 + (y - pos[n][1]) ** 2) / (2 * sg * sg)) + 1e-6; sw += w; r += w * base[k][0]; g += w * base[k][1]; b += w * base[k][2]; });
      tint[y * W + x] = (Math.round(r / sw) << 16) | (Math.round(g / sw) << 8) | Math.round(b / sw); }
    const wood = new Uint8Array(W * H), nW = noise(M.seed ^ 2);                                  // woods: masses where the land is wooded
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const i = y * W + x; wood[i] = nW(x / 30, y / 30, 3) < 0.2 + F[i] * 0.55 ? 1 : 0; }
    RP = { W, H, pos, f, G, nids, A, feats, E, F, Wt, kind, level, cellNode, cellPar, rivers, rad, tint, paths, sidx, wood };
    REGION.set(V, RP); return RP;
  }
  const NREL = new WeakMap();
  function nodeRelief(V, nid) {
    let cache = NREL.get(V); if (!cache) NREL.set(V, cache = {}); if (cache[nid]) return cache[nid];
    const RP = regionPlan(V), G = geom(V, nid), W = G.W, H = G.H, f = RP.f, [px, py] = RP.pos[nid], M = model(V), nW = noise(M.seed ^ 2);
    const E = new Float32Array(W * H), F = new Float32Array(W * H), Wt = new Float32Array(W * H), kind = new Uint8Array(W * H), level = new Int8Array(W * H), tint = new Uint32Array(W * H), wood = new Uint8Array(W * H);
    const at = (A, x, y) => A[Math.max(0, Math.min(RP.H - 1, y | 0)) * RP.W + Math.max(0, Math.min(RP.W - 1, x | 0))];
    const bil = (A, x, y) => { const x0 = Math.floor(x), y0 = Math.floor(y), fx = x - x0, fy = y - y0; return at(A, x0, y0) * (1 - fx) * (1 - fy) + at(A, x0 + 1, y0) * fx * (1 - fy) + at(A, x0, y0 + 1) * (1 - fx) * fy + at(A, x0 + 1, y0 + 1) * fx * fy; };
    const own = levelOf(bil(RP.E, px, py));
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const i = y * W + x, rx = px + (x - G.mid[0]) * f, ry = py + (y - G.mid[1]) * f, e = bil(RP.E, rx, ry);
      E[i] = e; F[i] = bil(RP.F, rx, ry); Wt[i] = bil(RP.Wt, rx, ry); tint[i] = at(RP.tint, rx, ry);
      const wx = rx + (nW(x / 6 + 2, y / 6, 2) - 0.5) * 9 * f, wy = ry + (nW(x / 6, y / 6 + 2, 2) - 0.5) * 9 * f;   // shores broken at this scale
      level[i] = G.REG[i] >= 0 ? own : at(RP.level, wx, wy) === 0 ? 0 : levelOf(e);          // open water (a generated world's sea, lakes) as the region has it
      if (RP.ground) tint[i] = at(RP.tint, wx, wy);
      kind[i] = RP.ground ? at(RP.kind, wx, wy) : e > 0.78 ? 2 : e > 0.56 ? 1 : (Wt[i] > 0.55 && e < 0.35) ? 3 : 0;   // the ground truth's terrain, or as derived
      wood[i] = nW(rx / 30, ry / 30, 3) < 0.2 + F[i] * 0.55 ? 1 : 0;
    }
    const rivers = RP.rivers.map((c) => ({ pid: null, pids: [], n: null, half: Math.max(2, c.half / f * 0.8), line: c.line.map(([x, y]) => [G.mid[0] + (x - px) / f, G.mid[1] + (y - py) / f]).filter(([x, y]) => x > -30 && y > -30 && x < W + 30 && y < H + 30) })).filter((c) => c.line.length > 2);
    return (cache[nid] = { E, F, Wt, kind, level, tint, wood, rivers, ground: !!RP.ground, tintW: RP.tintW });
  }
  function peaks(P, RL, cellPar, occ, W, H, snowy, k) {                                          // peaks where the land is mountain
    const pk = [], sx = Math.round(9 * k), sy = Math.round(7 * k);
    for (let y = sy; y < H - 2; y += sy) for (let x = sx; x < W - sx; x += sx) { const i = y * W + x; if (RL.kind[i] !== 2 || cellPar[i] >= 0 || occ[i]) continue;
      const e = RL.E[i]; if ([[-sx * 0.7, 0], [sx * 0.7, 0], [0, -sy * 0.7], [0, sy * 0.7]].some(([a, b]) => RL.E[Math.round(y + b) * W + Math.round(x + a)] > e)) continue;
      pk.push([x, y, Math.round((8 + Math.min(1, (e - 0.78) / 0.25) * 10) * k)]); }
    pk.sort((a, b) => a[1] - b[1]).forEach(([x, y, h]) => peak(P, x, y, h, h > 13 * k || snowy));
  }
  // a mountain peak (the night village's ranges: a lit side and a shaded one), snow on its top when high or in winter
  function peak(P, x, y, h, snow) {
    x |= 0; y |= 0; const w = Math.round(h * 1.1);
    for (let k = 0; k < h; k++) { const half = Math.round(k * w / (2 * h)); for (let dx = -half; dx <= half; dx++) {
      const lit = dx < 0, top = k < h * 0.35 && snow, c = top ? (lit ? "#f4f6fa" : "#cfd8e4") : lit ? (k % 3 ? "#a8a49a" : "#b8b4aa") : (k % 3 ? "#7e7a70" : "#8a867c");
      P.put(x + dx, y - h + k, c); } }
    for (let dx = -Math.round(w / 2); dx <= Math.round(w / 2); dx++) P.dark(x + dx, y, 0.2);
  }
  Object.assign(X, { REGION, PERDAY, WORLD_SCALE, levelOf, regionPlan, NREL, nodeRelief, peaks, peak });
})(C2X);
