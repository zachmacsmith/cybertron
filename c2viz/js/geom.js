// c2viz/js/geom.js: each place's ground plan of parcels, a presentation choice read from their sizes, neighbours and sides (ENGINE.md §9): parcels and river courses. The roads, the green and the buildings are laid on it in village.js.
(function (X) {
  "use strict";
  const { STOPS, hstr, model, rng } = X;
  // ---------------------------------------------------------------------------------------------------- a place's ground plan
  // Parcels have no coordinates; they have neighbours (`adj`), a side, a height and a size. The plan reads those and nothing else:
  //  - area: every unit of size is the same ground (UNIT pixels close up), so a field of 5 is five times a copse of 1;
  //  - the graph: neighbours are pulled together until they share a border, parcels that are not neighbours are pushed apart, and
  //    where two that are not neighbours would still touch, a strip of wild ground is left between them;
  //  - the side pulls a parcel that way (a north parcel lies to the north), a river is a long band through the land;
  //  - lots: a parcel holds buildings in lots (data.py COVERS: built ground 6 a unit of size), spread through it from its middle.
  // The same plan is drawn close up and, smaller, on the region's map.
  const UNIT = 2600, MARGIN = 36;
  const JIT = { field: 2.5, built: 3, pasture: 5, meadow: 6, forest: 9, scrub: 8, rock: 7, water: 4 };
  const SIDE = { north: [0, -1], south: [0, 1], east: [1, 0], west: [-1, 0], centre: [0, 0] };
  const fieldAngle = (pid) => ((hstr(pid) >>> 3) & 1 ? Math.PI / 2 : 0) + ((hstr(pid) >>> 5) % 7 - 3) * 0.07;
  // the radius a place's land will have, from its parcels' sizes alone (before its plan is laid): a generated world's place is
  // moved off open water by this, so its plan and the region's map agree on where it stands
  const landEstimate = (V, nid) => { let t = 0; for (const p of Object.values(V.static.parcels)) if (p.node === nid) t += Math.max(0.5, +p.size || 1) * UNIT / Math.PI; return 1.35 * Math.sqrt(t) || 40; };
  const GEOM = new WeakMap();
  function parcelPlan(V, nid) {
    let cache = GEOM.get(V); if (!cache) GEOM.set(V, cache = {});
    if (cache[nid]) return cache[nid];
    const ST = V.static, M = model(V), N = M.nodes[nid], pids = N.pids, n = pids.length, R = rng(hstr(nid) ^ M.seed);
    const L = ST.layout.nodes[nid] || { centre: {}, exits: {} }, idx = {}; pids.forEach((p, i) => (idx[p] = i));
    const size = pids.map((p) => Math.max(0.5, +ST.parcels[p].size || 1)), r = size.map((s) => Math.sqrt(s * UNIT / Math.PI));
    const adj = pids.map(() => new Set());
    pids.forEach((p, i) => (ST.parcels[p].adj || []).forEach((q) => { if (q in idx && idx[q] !== i) { adj[i].add(idx[q]); adj[idx[q]].add(i); } }));
    const tot = Math.sqrt(r.reduce((s, x) => s + x * x, 0)) || 40;
    // a generated world's river parcel lies on the generator's own river through its cells (ground.js), relative to the place's site
    const realRiver = pids.map((p) => null);
    if (V.land && X.groundLayers && N.river.some(Boolean)) {
      const Lg = X.groundLayers(V), PXg = X.GROUND_PX, f = X.WORLD_SCALE, s0 = V.land.sites[nid], nx = Lg.nx;
      const spot = X.groundSpots ? X.groundSpots(V)[nid] : null;                                   // where the region has it (moved off water)
      if (s0) { const sx = spot ? spot[0] : (s0[0] + 0.5) * PXg, sy = spot ? spot[1] : (s0[1] + 0.5) * PXg, near = {};
        Lg.place.forEach((v, ci) => { if (!v) return; const k = idx[Lg.places[v]]; if (k == null || !N.river[k]) return; (near[k] = near[k] || new Set()).add(ci); });
        for (const [k, cells] of Object.entries(near)) { let best = null, bn = 0;
          for (const rv of V.land.rivers || []) { let m = 0; for (const [rr, cc] of rv.cells) for (let a = -2; a <= 2; a++) for (let b = -2; b <= 2; b++) if (cells.has((rr + a) * nx + cc + b)) m++;
            if (m > bn) { bn = m; best = rv; } }
          if (best) realRiver[k] = best.cells.map(([rr, cc]) => { const i_ = rr * nx + cc; return [((cc + Lg.jx[i_] / 100 + 0.5) * PXg - sx) / f, ((rr + Lg.jy[i_] / 100 + 0.5) * PXg - sy) / f]; }); } }
    }
    const nearOn = (line, x, y) => { let bd = 1e18, bp = null, bk = 0; line.forEach(([a, b], k) => { const dd = (a - x) ** 2 + (b - y) ** 2; if (dd < bd) { bd = dd; bp = [a, b]; bk = k; } }); return [bp, bk]; };
    // start from layout.py's sites (each on its side), then let the graph settle
    const pos = pids.map((p) => { const c = L.centre[p] || [500 + (R() - .5) * 300, 350 + (R() - .5) * 200]; return [(c[0] - 500) / 500 * tot * 1.3, (c[1] - 350) / 350 * tot * 0.9]; });
    for (let it = 0; it < 500; it++) {
      const a = 0.12 * (1 - it / 500) + 0.02;
      for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
        let dx = pos[j][0] - pos[i][0], dy = pos[j][1] - pos[i][1], d = Math.hypot(dx, dy);
        if (d < 0.5) { dx = R() - .5; dy = R() - .5; d = Math.hypot(dx, dy); }
        const nb = adj[i].has(j), want = nb ? (r[i] + r[j]) * 0.8 : (r[i] + r[j]) * 1.08 + 12;
        if (!nb && d >= want) continue;
        const f = (d - want) / d * a * 0.5; pos[i][0] += dx * f; pos[i][1] += dy * f; pos[j][0] -= dx * f; pos[j][1] -= dy * f;
      }
      for (let i = 0; i < n; i++) { const s = SIDE[ST.parcels[pids[i]].side] || SIDE.centre;
        pos[i][0] += (s[0] * tot * 0.9 - pos[i][0]) * (s[0] ? 0.01 : 0.003); pos[i][1] += (s[1] * tot * 0.7 - pos[i][1]) * (s[1] ? 0.01 : 0.003); }
      if (realRiver.some(Boolean)) { let cx = 0, cy = 0, cs = 0; for (let i = 0; i < n; i++) { cx += pos[i][0] * size[i]; cy += pos[i][1] * size[i]; cs += size[i]; } cx /= cs; cy /= cs;
        for (let i = 0; i < n; i++) if (realRiver[i]) { const [q] = nearOn(realRiver[i], pos[i][0] - cx, pos[i][1] - cy); pos[i][0] += (q[0] + cx - pos[i][0]) * 0.08; pos[i][1] += (q[1] + cy - pos[i][1]) * 0.08; } }
    }
    // the middle of the land, and each river's course: it runs past the middle, across the whole map
    let mx = 0, my = 0, ms = 0; pids.forEach((p, i) => { mx += pos[i][0] * size[i]; my += pos[i][1] * size[i]; ms += size[i]; }); mx /= ms; my /= ms;
    const dir = pids.map((p, i) => {
      if (!N.river[i]) return null;
      if (realRiver[i]) { const L_ = realRiver[i], [, k] = nearOn(L_, pos[i][0] - mx, pos[i][1] - my), a_ = L_[Math.max(0, k - 6)], b_ = L_[Math.min(L_.length - 1, k + 6)], l_ = Math.hypot(b_[0] - a_[0], b_[1] - a_[1]) || 1;
        return [(b_[0] - a_[0]) / l_, (b_[1] - a_[1]) / l_]; }
      const wn = [...adj[i]].filter((j) => N.river[j]);                                     // along a chain of water parcels
      let ux, uy;
      if (wn.length) { ux = pos[wn[0]][0] - pos[i][0]; uy = pos[wn[0]][1] - pos[i][1]; }
      else { const vx = pos[i][0] - mx, vy = pos[i][1] - my; if (Math.hypot(vx, vy) < 5) { const t = (hstr(p) % 628) / 100; ux = Math.cos(t); uy = Math.sin(t); } else { ux = -vy; uy = vx; } }
      const l = Math.hypot(ux, uy) || 1; return [ux / l, uy / l];
    });
    const STRETCH = 2.4;
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    pids.forEach((p, i) => { const e = dir[i] ? r[i] * STRETCH : r[i]; x0 = Math.min(x0, pos[i][0] - e); y0 = Math.min(y0, pos[i][1] - e * (dir[i] ? Math.abs(dir[i][1]) + .3 : 1)); x1 = Math.max(x1, pos[i][0] + e); y1 = Math.max(y1, pos[i][1] + e * (dir[i] ? Math.abs(dir[i][1]) + .3 : 1)); });
    if (!n) { x0 = y0 = -60; x1 = y1 = 60; }
    const W = Math.max(240, Math.ceil(x1 - x0 + 2 * MARGIN)), H = Math.max(150, Math.ceil(y1 - y0 + 2 * MARGIN));
    const ox = W / 2 - (x0 + x1) / 2, oy = H / 2 - (y0 + y1) / 2, site = pos.map(([x, y]) => [x + ox, y + oy]);
    const wt = r.map((x) => x * x), jit = N.jit;
    const frame = pids.map((p, i) => dir[i] ? [dir[i][0], dir[i][1], STRETCH, 2] : ST.parcels[p].cover === "field" ? [Math.cos(fieldAngle(p)), Math.sin(fieldAngle(p)), 1.15, 5]
      : ST.parcels[p].cover === "built" ? [1, 0, 1.2, 3] : ST.parcels[p].cover === "water" ? null
      : [Math.cos((hstr(p) % 314) / 100), Math.sin((hstr(p) % 314) / 100), 1 + (hstr(p) % 30) / 100, 3]);
    const LOBE = { water: 0.3, forest: 0.26, scrub: 0.22, rock: 0.2, pasture: 0.14, meadow: 0.14 };
    const lobe = pids.map((p, i) => { const A = dir[i] ? 0 : LOBE[ST.parcels[p].cover] || 0, h = hstr(p + "|lobe"), ph = [h % 628, (h >>> 10) % 628, (h >>> 20) % 628].map((v) => v / 100);
      return A ? (t) => 1 + A * (0.55 * Math.sin(2 * t + ph[0]) + 0.3 * Math.sin(3 * t + ph[1]) + 0.15 * Math.sin(5 * t + ph[2])) : null; });
    const pdist = (i, x, y) => { let dx = x - site[i][0], dy = y - site[i][1]; const F = frame[i];
      if (lobe[i]) { const k = lobe[i](Math.atan2(dy, dx)); dx /= k; dy /= k; }
      if (!F) return dx * dx + dy * dy - wt[i];
      const a = Math.abs((dx * F[0] + dy * F[1]) / F[2]), b = Math.abs((-dx * F[1] + dy * F[0]) * F[2]), q = F[3];
      return q === 2 ? a * a + b * b - wt[i] : Math.pow(Math.pow(a, q) + Math.pow(b, q), 2 / q) - wt[i]; };
    const which = (x, y) => {
      let k0 = 0, b = 1e18; for (let i = 0; i < n; i++) { const v = pdist(i, x, y); if (v < b) { b = v; k0 = i; } }
      const A = JIT[ST.parcels[pids[k0]]?.cover] ?? 5;
      const jx = x + (jit(x / 22, y / 22, 3) - .5) * 2 * A, jy = y + (jit(x / 22 + 40, y / 22, 3) - .5) * 2 * A;
      let k = -1, v1 = 1e18, k2 = -1, v2 = 1e18;
      for (let i = 0; i < n; i++) { const v = pdist(i, jx, jy); if (v < v1) { v2 = v1; k2 = k; v1 = v; k = i; } else if (v < v2) { v2 = v; k2 = i; } }
      if (k < 0 || v1 > 0) return -1;                                                          // in no parcel: wild ground
      if (k2 >= 0 && v2 < 0 && !adj[k].has(k2) && (v2 - v1) < 7 * Math.hypot(site[k][0] - site[k2][0], site[k][1] - site[k2][1])) return -1;   // not neighbours: a strip between
      return k;
    };
    // fit each parcel's ground to its size (a few rounds on a coarse grid)
    // (damped: neighbours trade ground, so full steps swing a small parcel between all and nothing and it ends on whichever side)
    for (let it = 0; it < 40; it++) {
      const area = new Float64Array(n);
      for (let y = 1; y < H; y += 4) for (let x = 1; x < W; x += 4) { const k = which(x, y); if (k >= 0) area[k] += 16; }
      const step = 0.5 * Math.pow(0.95, it);
      for (let i = 0; i < n; i++) wt[i] *= Math.max(0.8, Math.min(1.3, Math.pow((size[i] * UNIT) / Math.max(30, area[i]), step)));
    }
    const REG = new Int16Array(W * H); for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) REG[y * W + x] = which(x, y);
    const area = pids.map(() => []); for (let i = 0; i < W * H; i++) if (REG[i] >= 0) area[REG[i]].push([i % W, (i / W) | 0]);
    const centre = area.map((a, i) => { if (!a.length) return site[i].slice(); let sx = 0, sy = 0; for (const [x, y] of a) { sx += x; sy += y; } return [sx / a.length, sy / a.length]; });
    const reg = (x, y) => (x < 0 || y < 0 || x >= W || y >= H) ? -2 : REG[(y | 0) * W + (x | 0)];
    const inner = (i, mx_, my_) => area[i].filter(([x, y]) => x % 2 === 0 && y % 2 === 0 && reg(x - mx_, y - my_) === i && reg(x + mx_, y - my_) === i && reg(x - mx_, y + my_) === i && reg(x + mx_, y + my_) === i);
    // rivers: one course for each chain of river parcels, through their sites, on to the map's edges; it stops where it would run
    // into a dry parcel
    const courses = [], seen = new Set();
    pids.forEach((p, i) => {
      if (!dir[i] || seen.has(i)) return;
      const chain = [], st = [i]; seen.add(i); while (st.length) { const j = st.pop(); chain.push(j); for (const k of adj[j]) if (dir[k] && !seen.has(k)) { seen.add(k); st.push(k); } }
      const [ux, uy] = dir[chain[0]], pr = (j) => site[j][0] * ux + site[j][1] * uy;
      chain.sort((a, b) => pr(a) - pr(b));
      const a0 = site[chain[0]], a1 = site[chain[chain.length - 1]], far = W + H;
      const knots = [[a0[0] - ux * far, a0[1] - uy * far], ...chain.map((j) => site[j]), [a1[0] + ux * far, a1[1] + uy * far]];
      const sz = Math.max(...chain.map((j) => size[j])), amp = Math.max(3, Math.sqrt(sz * UNIT) * 0.12), lam = Math.max(45, Math.sqrt(sz * UNIT) * 0.9), ph = (hstr(p) % 628) / 100;
      let line = [], arc = 0;
      for (let k = 0; k + 1 < knots.length; k++) { const [x0_, y0_] = knots[k], [x1_, y1_] = knots[k + 1], L = Math.hypot(x1_ - x0_, y1_ - y0_) || 1, nx = -(y1_ - y0_) / L, ny = (x1_ - x0_) / L;
        for (let t = 0; t < L; t += 1, arc += 1) { const s_ = Math.sin(arc / lam * Math.PI + ph) * amp, x = x0_ + (x1_ - x0_) * t / L + nx * s_, y = y0_ + (y1_ - y0_) * t / L + ny * s_;
          if (x < -8 || y < -8 || x > W + 8 || y > H + 8) continue; line.push([x, y]); } }
      const dry = ([x, y]) => { const k = reg(x, y); return k >= 0 && STOPS.has(ST.parcels[pids[k]].cover); };
      let m = 0, bd = 1e18; line.forEach(([x, y], k) => { const dd = (x - site[chain[0]][0]) ** 2 + (y - site[chain[0]][1]) ** 2; if (dd < bd) { bd = dd; m = k; } });
      let lo = m, hi = m, out_ = false; while (lo > 0) { const w_ = dry(line[lo - 1]); if (!w_ && reg(line[lo - 1][0], line[lo - 1][1]) === -1) out_ = true; if (w_ && out_) break; lo--; }
      out_ = false; while (hi < line.length - 1) { const w_ = dry(line[hi + 1]); if (!w_ && reg(line[hi + 1][0], line[hi + 1][1]) === -1) out_ = true; if (w_ && out_) break; hi++; }
      line = line.slice(lo, hi + 1);
      courses.push({ pid: p, pids: chain.map((j) => pids[j]), line, half: Math.max(2.5, 2 + Math.sqrt(sz) * 2.2), n: 0 });
    });
    let gx = 0, gy = 0, gs = 0; area.forEach((a) => { for (const [x, y] of a) { gx += x; gy += y; gs++; } }); if (gs) { gx /= gs; gy /= gs; } else { gx = W / 2; gy = H / 2; }
    let land = 0; area.forEach((a) => { for (const [x, y] of a) land = Math.max(land, Math.hypot(x - gx, y - gy)); });
    for (const c of courses) { const k = c.pids.map((p) => idx[p]).find((j) => realRiver[j]); if (k == null) continue;
      c.line = realRiver[k].map(([a, b]) => [gx + a, gy + b]).filter(([x, y]) => x > -8 && y > -8 && x < W + 8 && y < H + 8); c.real = true; }
    const g = { W, H, REG, area, centre, adj, site, courses, mid: [gx, gy], land: land || 40, reg, inner, pids, idx, size, frame };
    cache[nid] = g; return g;
  }
  Object.assign(X, { UNIT, MARGIN, JIT, SIDE, fieldAngle, GEOM, landEstimate, parcelPlan });
})(C2X);
