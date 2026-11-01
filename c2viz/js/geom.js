// c2viz/js/geom.js: each place's ground plan, a presentation choice read from its parcels' sizes, neighbours and sides (ENGINE.md §9): parcels, river courses, the green, the roads out, where each building stands.
(function (X) {
  "use strict";
  const { STOPS, hstr, model, rng, shape, windPath } = X;
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
  const GEOM = new WeakMap();
  function geom(V, nid) {
    let cache = GEOM.get(V); if (!cache) GEOM.set(V, cache = {});
    if (cache[nid]) return cache[nid];
    const ST = V.static, M = model(V), N = M.nodes[nid], pids = N.pids, n = pids.length, R = rng(hstr(nid) ^ M.seed);
    const L = ST.layout.nodes[nid] || { centre: {}, exits: {} }, idx = {}; pids.forEach((p, i) => (idx[p] = i));
    const size = pids.map((p) => Math.max(0.5, +ST.parcels[p].size || 1)), r = size.map((s) => Math.sqrt(s * UNIT / Math.PI));
    const adj = pids.map(() => new Set());
    pids.forEach((p, i) => (ST.parcels[p].adj || []).forEach((q) => { if (q in idx && idx[q] !== i) { adj[i].add(idx[q]); adj[idx[q]].add(i); } }));
    const tot = Math.sqrt(r.reduce((s, x) => s + x * x, 0)) || 40;
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
    }
    // the middle of the land, and each river's course: it runs past the middle, across the whole map
    let mx = 0, my = 0, ms = 0; pids.forEach((p, i) => { mx += pos[i][0] * size[i]; my += pos[i][1] * size[i]; ms += size[i]; }); mx /= ms; my /= ms;
    const dir = pids.map((p, i) => {
      if (!N.river[i]) return null;
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
    const pdist = (i, x, y) => { let dx = x - site[i][0], dy = y - site[i][1]; const F = frame[i];
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
    for (let it = 0; it < 10; it++) {
      const area = new Float64Array(n);
      for (let y = 0; y < H; y += 3) for (let x = 0; x < W; x += 3) { const k = which(x, y); if (k >= 0) area[k] += 9; }
      for (let i = 0; i < n; i++) wt[i] *= Math.max(0.6, Math.min(1.7, Math.pow((size[i] * UNIT) / Math.max(30, area[i]), 0.8)));
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
    // where each road leaves: from its end's parcels (roads.ends), towards its end's side, or towards the other place if the side is
    // the centre; out to the edge of the map
    const Lw = V.static.layout.world || {}, me0 = Lw[nid] || [500, 350], SIDEV = { north: [0, -1], south: [0, 1], east: [1, 0], west: [-1, 0] };
    const exits = Object.entries(ST.roads).filter(([, r]) => r.a === nid || r.b === nid).map(([rid, r]) => {
      const other = r.a === nid ? r.b : r.a, end = (r.ends || {})[nid] || { side: "centre", parcels: [], hidden: false };
      let i = (end.parcels || []).map((p) => idx[p]).find((k) => k != null); if (i == null) i = pids.findIndex((p) => ST.parcels[p].cover === "built");
      const [fx, fy] = i >= 0 ? centre[i] : [W / 2, H / 2], o = Lw[other] || [500, 350];
      let [dx, dy] = SIDEV[end.side] || [o[0] - me0[0], o[1] - me0[1]]; const tw = ((hstr(rid) % 7) - 3) * 0.08, l = Math.hypot(dx, dy) || 1;
      [dx, dy] = [(dx * Math.cos(tw) - dy * Math.sin(tw)) / l, (dx * Math.sin(tw) + dy * Math.cos(tw)) / l];
      let t = 0; while (t < 4 * (W + H)) { const x = fx + dx * t, y = fy + dy * t; if (x < 1 || y < 1 || x > W - 2 || y > H - 2) break; t += 1; }
      return { rid, to: other, end, fx, fy, tx: Math.max(-2, Math.min(W + 1, fx + dx * t)), ty: Math.max(-2, Math.min(H + 1, fy + dy * t)) };
    });
    // the village's green (a presentation choice): the middle of its built ground, where every road starts; houses line the roads
    const bi = pids.findIndex((p) => ST.parcels[p].cover === "built");
    const green = bi >= 0 && area[bi].length ? centre[bi].map(Math.round) : null, greenR = bi >= 0 ? Math.max(6, Math.min(12, Math.sqrt(area[bi].length) * 0.16)) : 0;
    for (const e of exits) { const s0 = green ? windPath(green[0], green[1], e.fx, e.fy, hstr(e.rid + "|in"), 0.06) : []; e.way = s0.concat(windPath(e.fx, e.fy, e.tx, e.ty, hstr(e.rid + nid), 0.12)); }
    const rd = new Int16Array(W * H).fill(999), rq = [];                                        // distance from the roads
    for (const e of exits) for (const [x, y] of e.way) for (let a2 = 0; a2 <= 1; a2++) for (let b2 = 0; b2 <= 1; b2++) { const xx = (x | 0) + a2, yy = (y | 0) + b2; if (xx >= 0 && yy >= 0 && xx < W && yy < H && rd[yy * W + xx]) { rd[yy * W + xx] = 0; rq.push(yy * W + xx); } }
    for (let k2 = 0; k2 < rq.length; k2++) { const i = rq[k2], x = i % W, y = (i / W) | 0; for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const xx = x + dx, yy = y + dy; if (xx < 0 || yy < 0 || xx >= W || yy >= H) continue; const j = yy * W + xx; if (rd[j] > rd[i] + 1) { rd[j] = rd[i] + 1; rq.push(j); } } }
    // buildings: each on its parcel at its footprint (shape(): the spec's rooms), placed once for the run in the order they first
    // stand: its door a few paces off a road, near the green, clear of the roads and the green; one that does not fit is shown
    // overfull beside its parcel
    const ever = {};
    V.days.forEach((d, day) => { for (const [bid, b] of Object.entries(d.buildings)) if (b.node === nid) { const sh = shape(b, bid), e = ever[bid];
      if (!e) ever[bid] = { day, b, w: sh.w, h: sh.h }; else { e.w = Math.max(e.w, sh.w); e.h = Math.max(e.h, sh.h); } } });
    const taken = new Uint8Array(W * H), placeOf = {}, MG = 3;
    const order = Object.keys(ever).sort((a, b) => ever[a].day - ever[b].day || (ever[b].w * ever[b].h) - (ever[a].w * ever[a].h) || (a < b ? -1 : 1));
    for (const bid of order) {
      const e = ever[bid]; let i = idx[e.b.parcel]; if (i == null) i = pids.findIndex((p) => ST.parcels[p].cover === "built"); if (i < 0) i = 0;
      let [cx, cy] = centre[i]; const bR = rng(hstr(bid));
      if ((e.b.fittings || {})["water wheel"]) {                                                   // its site is the water (FITTINGS site: water)
        const wj = pids.findIndex((p, j) => ST.parcels[p].cover === "water" && (j === i || adj[i].has(j)));
        if (wj >= 0) { let bd = 1e18; for (const [x, y] of area[i]) { const dd = (x - centre[wj][0]) ** 2 + (y - centre[wj][1]) ** 2; if (dd < bd) { bd = dd; cx = x; cy = y; } } }
      }
      const wheel = (e.b.fittings || {})["water wheel"], gc = !wheel && green && idx[e.b.parcel] === bi ? green : [cx, cy];
      const front = (x, y) => { const yy = Math.min(H - 1, y + (e.h >> 1) + 3); return rd[yy * W + Math.max(0, Math.min(W - 1, x))]; };
      const cand = area[i].filter(([x, y]) => (x + y) % 2 === 0).map(([x, y]) => [x, y, Math.sqrt((x - gc[0]) ** 2 + (y - gc[1]) ** 2) * (wheel ? 3 : 1) + Math.abs(Math.min(30, front(x, y)) - 4) * 6 + bR() * 12]).sort((p, q) => p[2] - q[2]);
      let spot = null;
      for (const [x, y] of cand) { const x0 = x - (e.w >> 1), y0 = y - (e.h >> 1); let ok = true;
        for (let yy = y0; yy < y0 + e.h && ok; yy += 2) for (let xx = x0; xx < x0 + e.w; xx += 2) if (xx < 0 || yy < 0 || xx >= W || yy >= H || REG[yy * W + xx] !== i) { ok = false; break; }
        for (let yy = y0 - 1; yy < y0 + e.h + 2 && ok; yy++) for (let xx = x0 - 1; xx < x0 + e.w + 1; xx++) if (xx >= 0 && yy >= 0 && xx < W && yy < H && (rd[yy * W + xx] < 2 || (green && Math.hypot(xx - green[0], yy - green[1]) < greenR + 2))) { ok = false; break; }
        for (let yy = y0 - MG; yy < y0 + e.h + MG && ok; yy++) for (let xx = x0 - MG; xx < x0 + e.w + MG; xx++) if (xx >= 0 && yy >= 0 && xx < W && yy < H && taken[yy * W + xx]) { ok = false; break; }
        if (ok) { spot = [x0, y0]; break; } }
      const fits = !!spot;
      if (!spot) {                                                                                  // overfull: on open ground beside its parcel, facing a road
        const near = [];
        for (let y = Math.max(0, gc[1] - 90 | 0); y < Math.min(H, gc[1] + 90); y += 2) for (let x = Math.max(0, gc[0] - 110 | 0); x < Math.min(W, gc[0] + 110); x += 2) if (REG[y * W + x] === -1) near.push([x, y, Math.hypot(x - gc[0], y - gc[1]) + Math.abs(Math.min(30, front(x, y)) - 4) * 6]);
        near.sort((p, q) => p[2] - q[2]);
        for (const [x, y] of near) { const x0 = x - (e.w >> 1), y0 = y - (e.h >> 1); let ok = x0 >= 0 && y0 >= 0 && x0 + e.w < W && y0 + e.h < H;
          for (let yy = y0 - 1; yy < y0 + e.h + 2 && ok; yy++) for (let xx = x0 - 1; xx < x0 + e.w + 1; xx++) { const j = yy * W + xx; if (xx < 0 || yy < 0 || xx >= W || yy >= H) continue;
            if ((REG[j] !== -1 && REG[j] !== i) || rd[j] < 2 || (green && Math.hypot(xx - green[0], yy - green[1]) < greenR + 2)) { ok = false; break; } }
          for (let yy = y0 - MG; yy < y0 + e.h + MG && ok; yy++) for (let xx = x0 - MG; xx < x0 + e.w + MG; xx++) if (xx >= 0 && yy >= 0 && xx < W && yy < H && taken[yy * W + xx]) { ok = false; break; }
          if (ok) { spot = [x0, y0]; break; } }
      }
      if (!spot) spot = [Math.round(cx - e.w / 2), Math.round(cy - e.h / 2)];
      placeOf[bid] = { x: spot[0], y: spot[1], w: e.w, h: e.h, fits };
      for (let yy = spot[1]; yy < spot[1] + e.h; yy++) for (let xx = spot[0]; xx < spot[0] + e.w; xx++) if (xx >= 0 && yy >= 0 && xx < W && yy < H) taken[yy * W + xx] = 1;
    }
    let gx = 0, gy = 0, gs = 0; area.forEach((a) => { for (const [x, y] of a) { gx += x; gy += y; gs++; } }); if (gs) { gx /= gs; gy /= gs; } else { gx = W / 2; gy = H / 2; }
    let land = 0; area.forEach((a) => { for (const [x, y] of a) land = Math.max(land, Math.hypot(x - gx, y - gy)); });
    const g = { W, H, REG, area, centre, adj, site, courses, placeOf, exits, green, greenR, mid: [gx, gy], land: land || 40, reg, inner };
    cache[nid] = g; return g;
  }
  Object.assign(X, { UNIT, MARGIN, JIT, SIDE, fieldAngle, GEOM, geom });
})(C2X);
