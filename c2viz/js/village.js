// c2viz/js/village.js: what is laid on a place's parcel plan (geom.js): its roads, its green and where each building stands. Roads are laid in steps so they fit the land and agree with the region's map (ENGINE.md §13).
(function (X) {
  "use strict";
  const { STOPS, hstr, model, nodeRelief, parcelPlan, rng, roadOut, shape } = X;
  // ---------------------------------------------------------------------------------------------------- the village's roads
  // 1. where each road leaves: the one heading the region's map has for it (region.js roadOut), and the point where that heading
  //    meets the edge of this plan, which is where the road goes on on the region's map;
  // 2. its way inside the place: the cheapest way over the plan from the green (a hidden way: from its own parcel), through the
  //    parcel the engine says it leaves by (roads.ends), to that point. Going is cheap on the green, built ground and open grass,
  //    and along the edges of parcels (hedges, the margins of fields and woods); dear across a field's crop, through a wood, over
  //    rock; a river is crossed where it is narrowest (a ford), and open water (a lake, a mere, the sea) is gone round. Each road
  //    laid makes its own ground cheap, so the next joins it rather than running beside it or across it: a network, not a tangle;
  // 3. the way smoothed into a curve that keeps to it, and drawn only where no road before it was drawn, meeting it at a junction.
  const C = 2;                                                                                   // the grid the ways are found on (px)
  const COST = { built: 1, pasture: 1.6, meadow: 1.6, field: 9, forest: 5, scrub: 3.5, rock: 7, water: 400, wild: 1.8 };
  const EDGE = { field: 1.25, pasture: 1.2, meadow: 1.2, forest: 1.6, scrub: 1.6, rock: 3, built: 1, water: 400 };
  function heapPush(h, k, v) { h.push([k, v]); let i = h.length - 1; while (i) { const p = (i - 1) >> 1; if (h[p][0] <= h[i][0]) break; [h[p], h[i]] = [h[i], h[p]]; i = p; } }
  function heapPop(h) { const top = h[0], last = h.pop(); if (h.length) { h[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i;
    if (l < h.length && h[l][0] < h[m][0]) m = l; if (r < h.length && h[r][0] < h[m][0]) m = r; if (m === i) break; [h[m], h[i]] = [h[i], h[m]]; i = m; } } return top; }
  const N8 = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1], [1, 1, 1.4142], [1, -1, 1.4142], [-1, 1, 1.4142], [-1, -1, 1.4142]];
  function reach(cost, gw, gh, src) {
    const dist = new Float64Array(gw * gh).fill(Infinity), prev = new Int32Array(gw * gh).fill(-1), h = [];
    dist[src] = 0; heapPush(h, 0, src);
    while (h.length) { const [d, i] = heapPop(h); if (d > dist[i]) continue; const x = i % gw, y = (i / gw) | 0;
      for (const [dx, dy, l] of N8) { const xx = x + dx, yy = y + dy; if (xx < 0 || yy < 0 || xx >= gw || yy >= gh) continue; const j = yy * gw + xx;
        const nd = d + l * 0.5 * (cost[i] + cost[j]); if (nd < dist[j]) { dist[j] = nd; prev[j] = i; heapPush(h, nd, j); } } }
    return { dist, prev };
  }
  const walk = (prev, to) => { const out = [to]; while (prev[out[out.length - 1]] >= 0) out.push(prev[out[out.length - 1]]); return out.reverse(); };
  function smooth(pts) {                                                                         // corners cut twice, then every 0.7 px
    let p = pts; for (let it = 0; it < 3; it++) { if (p.length < 3) break; const q = [p[0]];
      for (let k = 0; k + 1 < p.length; k++) { const [a, b] = [p[k], p[k + 1]]; q.push([a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25], [a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75]); }
      q.push(p[p.length - 1]); p = q; }
    const out = []; for (let k = 0; k + 1 < p.length; k++) { const [a, b] = [p[k], p[k + 1]], L = Math.hypot(b[0] - a[0], b[1] - a[1]); for (let t = 0; t < L; t += 0.7) out.push([a[0] + (b[0] - a[0]) * t / L, a[1] + (b[1] - a[1]) * t / L]); }
    if (p.length) out.push(p[p.length - 1].slice()); return out;
  }
  const VGEOM = new WeakMap();
  function geom(V, nid) {
    let cache = VGEOM.get(V); if (!cache) VGEOM.set(V, cache = {});
    if (cache[nid]) return cache[nid];
    const P0 = parcelPlan(V, nid), ST = V.static, M = model(V), { W, H, REG, area, centre, adj, pids, idx } = P0;
    // the ground's cost on a coarse grid: each parcel by its cover, cheaper along its edges; rivers dear to cross, open water dearer
    const gw = Math.ceil(W / C), gh = Math.ceil(H / C), cost = new Float32Array(gw * gh), NR = nodeRelief(V, nid);
    const cov = (k) => k < 0 ? "wild" : ST.parcels[pids[k]].cover, river = new Uint8Array(gw * gh);
    for (const c of P0.courses.concat(NR.rivers)) { const rr = c.half + 1.5; for (const [lx, ly] of c.line) for (let dy = -rr; dy <= rr; dy += 1) for (let dx = -rr; dx <= rr; dx += 1) {
      if (dx * dx + dy * dy > rr * rr) continue; const gx = Math.floor((lx + dx) / C), gy = Math.floor((ly + dy) / C); if (gx >= 0 && gy >= 0 && gx < gw && gy < gh) river[gy * gw + gx] = 1; } }
    for (let gy = 0; gy < gh; gy++) for (let gx = 0; gx < gw; gx++) {
      const x = Math.min(W - 1, gx * C + 1), y = Math.min(H - 1, gy * C + 1), i = y * W + x, k = REG[i], c = cov(k), riv = k >= 0 && ST.parcels[pids[k]].cover === "water" && M.nodes[nid].river[k];
      let edge = false; for (const [dx, dy] of [[4, 0], [-4, 0], [0, 4], [0, -4], [3, 3], [-3, -3], [3, -3], [-3, 3]]) { const xx = x + dx, yy = y + dy; if (xx >= 0 && yy >= 0 && xx < W && yy < H && REG[yy * W + xx] !== k) { edge = true; break; } }
      let v = edge ? (EDGE[c] ?? 1.5) : (COST[c] ?? 2);
      if (k < 0 && NR.level[i] === 0) v = 400;                                                     // open water round the place (the region's)
      if (river[gy * gw + gx] || riv) v = Math.max(v, 30);                                         // a river: crossed, not followed
      cost[gy * gw + gx] = v;
    }
    const gi = (x, y) => Math.max(0, Math.min(gh - 1, Math.floor(y / C))) * gw + Math.max(0, Math.min(gw - 1, Math.floor(x / C)));
    const gp = (i) => [(i % gw) * C + C / 2, ((i / gw) | 0) * C + C / 2];
    // the green (a presentation choice): the middle of its built ground, where every road starts; houses line the roads
    const bi = pids.findIndex((p) => ST.parcels[p].cover === "built");
    const green = bi >= 0 && area[bi].length ? centre[bi].map(Math.round) : null, greenR = bi >= 0 ? Math.max(6, Math.min(12, Math.sqrt(area[bi].length) * 0.16)) : 0;
    const roads = Object.entries(ST.roads).filter(([, r]) => r.a === nid || r.b === nid)
      .map(([rid, r]) => ({ rid, r, end: (r.ends || {})[nid] || { side: "centre", parcels: [], hidden: false } }))
      .sort((a, b) => (!!a.end.hidden - !!b.end.hidden) || (b.r.track ? 1 : 0) - (a.r.track ? 1 : 0) || (a.r.days - b.r.days) || (a.rid < b.rid ? -1 : 1));
    const laid = new Uint8Array(gw * gh), exits = [];
    for (const { rid, r, end } of roads) {
      const other = r.a === nid ? r.b : r.a, out = roadOut(V, nid, rid), [tx, ty] = out.edge;
      let k = (end.parcels || []).map((p) => idx[p]).find((q) => q != null); if (k == null) k = bi;
      let via = k != null && k >= 0 ? area[k].filter(([x, y]) => x % C === 1 && y % C === 1).map(([x, y]) => gi(x, y)) : [];
      if (k != null && k >= 0 && cov(k) === "water") {                                         // it leaves by water: along its shore, not across it
        const inK = new Set(via), shore = new Set();
        for (const v of via) { const vx = v % gw, vy = (v / gw) | 0; for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) { const xx = vx + dx, yy = vy + dy, j = yy * gw + xx;
          if (xx >= 0 && yy >= 0 && xx < gw && yy < gh && !inK.has(j) && cost[j] < 30) shore.add(j); } }
        via = [...shore];
      }
      const dry = pids.map((_, j) => j).filter((j) => cov(j) !== "water" && area[j].length).sort((a, b) => (COST[cov(a)] ?? 2) - (COST[cov(b)] ?? 2) || area[b].length - area[a].length);
      const home = k != null && k >= 0 && cov(k) !== "water" ? k : dry.length ? dry[0] : null;          // a place with no green: from dry ground
      const s = end.hidden || !green ? (home != null ? gi(...centre[home]) : gi(W / 2, H / 2)) : gi(green[0], green[1]), t = gi(tx, ty);
      const A = reach(cost, gw, gh, s), B = reach(cost, gw, gh, t);
      let q = t, best = A.dist[t];
      for (const v of via) { const dd = A.dist[v] + B.dist[v]; if (dd < best) { best = dd; q = v; } }    // through its own parcel, at the cheapest point
      const cells = walk(A.prev, q).concat(walk(B.prev, q).reverse().slice(1));
      const pts = cells.map(gp); pts[0] = end.hidden || !green ? pts[0] : green.slice(); pts[pts.length - 1] = [tx, ty];
      const way = smooth(pts);
      // drawn only where it is its own, each stretch from the junction where it leaves a road laid before it to where it meets one
      const draw = []; let run = null;
      cells.forEach((c, j) => { const own = !laid[c] || j === cells.length - 1;
        if (own) { if (!run) run = [j ? gp(cells[j - 1]) : pts[0]]; run.push(j === cells.length - 1 ? pts[j] : gp(c)); }
        else if (run) { run.push(gp(c)); draw.push(smooth(run)); run = null; } });
      if (run && run.length > 1) draw.push(smooth(run));
      for (const c of cells) { laid[c] = 1; cost[c] = Math.min(cost[c], 0.4); }
      const [fx, fy] = gp(q);
      exits.push({ rid, to: other, end, fx, fy, tx, ty, way, draw, dir: out.dir });
    }
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

    const g = { ...P0, exits, green, greenR, placeOf };
    cache[nid] = g; return g;
  }
  Object.assign(X, { VGEOM, geom });
})(C2X);
