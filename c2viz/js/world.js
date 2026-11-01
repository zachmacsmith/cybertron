// c2viz/js/world.js: the region's map for a day.
(function (X) {
  "use strict";
  const { D, PAL, Px, drawBuilding, drawTrees, hstr, model, node, noise, paintLand, paintPath, paintRoad, peaks, person, personLabel, plan, regionPlan, rng, styleOf, verges, weatherOver } = X;
  // ---------------------------------------------------------------------------------------------------- the region
  // each place's ground plan at one scale for all places (so a big place looks big), in its own territory; its buildings at their
  // footprint, smaller, its people as small figures, roads between places from their ends, travellers at the middle of the stretch
  // they are on, landmarks on their stretches. Unexplored places are drawn as they are: the world exists before anyone finds it.
  function world(cv, V, day, opts = {}) {
    const M = model(V), d = D(V, day), ST = V.static, WL = ST.layout.world, nids = Object.keys(ST.nodes).sort();
    const RP = regionPlan(V), W = RP.W, H = RP.H, G = RP.G, pos = RP.pos, f = RP.f, R = rng(M.seed ^ 77), P = Px(cv, W, H, "#6ca63c"), out = { width: W, height: H, hotspots: [] };
    const toWorld = (n, x, y) => [pos[n][0] + (x - G[n].mid[0]) * f, pos[n][1] + (y - G[n].mid[1]) * f];
    const cellNode = RP.cellNode, cellPar = RP.cellPar, occ = new Uint8Array(W * H);
    const courses = RP.rivers.slice();
    nids.forEach((n, ni) => { for (const c of G[n].courses) courses.push({ pid: c.pid, pids: c.pids, n: ni, half: Math.max(1, c.half * f), line: c.line.map(([x, y]) => toWorld(n, x, y)) }); });
    const ctx = paintLand(P, V, day, W, H, nids, cellNode, cellPar, f, R, occ, { scale: "world", courses, relief: RP });
    const n2 = noise(M.seed ^ 5), paint = paintRoad(P, occ, ctx.LV, W, H, ctx.face), roadPts = {};
    for (const [rid, r] of Object.entries(ST.roads)) {
      if (!RP.paths[rid]) continue;
      const pts = RP.paths[rid], a = pts[0], hid = Object.values(r.ends || {}).some((e) => e.hidden);
      paintPath(paint, pts, r.track ? 1 : 0, r.track ? PAL.road : PAL.lane, hid ? (x, y) => (Math.round(x) + Math.round(y)) % 3 : null);
      roadPts[rid] = pts;
      const mid = pts[pts.length >> 1] || a;
      out.hotspots.push({ kind: "road", id: rid, x: (mid[0] | 0) - 4, y: (mid[1] | 0) - 4, w: 8, h: 8, label: `${ST.nodes[r.a]?.name} — ${ST.nodes[r.b]?.name}: ${r.days} day${r.days > 1 ? "s" : ""}${r.track ? ", a cart track" : ""}${r.terrain ? ", " + r.terrain : ""}` });
      const ch = (d.roads[rid] || {}).challenges || {};
      (r.stretches || []).forEach((st, i, all) => (st.landmarks || []).forEach((lm, j) => {               // landmarks on their stretch
        const p = pts[Math.min(pts.length - 1, RP.sidx[rid][i] + j * 8)]; if (!p) return;
        const k = lm.kind || lm, x = p[0] | 0, y = p[1] | 0, c = ch[`${i + 1}:${k}`];
        if (k === "ford") { for (let a = -2; a <= 2; a++) { P.put(x + a, y, c ? "#4e94a8" : "#7cc0c8"); P.put(x + a, y + 1, c ? "#3e8498" : "#5aa2b4"); } }
        else if (k === "bridge") { for (let a = -2; a <= 2; a++) { P.put(x + a, y - 1, c ? "#6b4423" : "#8a5a2a"); P.put(x + a, y + 1, "#5aa2b4"); } P.put(x - 2, y, "#6b4423"); P.put(x + 2, y, "#6b4423"); if (c) P.put(x, y - 1, "#2a1a10"); }
        else if (k === "pass") { for (let a = -2; a <= 2; a++) P.put(x + a, y - 1 + Math.abs(a) - 2, "#9a9aa0"); P.put(x, y - 3, c ? "#ffffff" : "#b4b4ba"); }
        else if (k === "spring") { P.put(x + 2, y - 1, "#7cc0c8"); P.put(x + 3, y - 1, "#5aa2b4"); }
        else if (k === "fruit trees") { P.put(x + 2, y - 2, "#3a8a3e"); P.put(x + 3, y - 2, "#c8553d"); P.put(x + 2, y - 1, "#5a3a24"); }
        else { P.put(x + 2, y - 2, "#e8e8e0"); P.put(x + 2, y - 1, "#a8a29a"); P.put(x + 3, y - 1, "#c8c4bc"); }
        out.hotspots.push({ kind: "landmark", id: rid + ":" + i + ":" + j, x: x - 2, y: y - 3, w: 6, h: 6, label: `${k} on day ${i + 1} of the road${c ? ` (${c})` : ""}` }); }));
    }
    for (const n of nids) for (const e of G[n].exits) { const k0 = e.way.findIndex(([x, y]) => Math.hypot(x - e.fx, y - e.fy) < 1.5);   // the village's own ways
      paintPath(paint, e.way.slice(0, k0 > 0 ? k0 : 0).map(([x, y]) => toWorld(n, x, y)), 0, PAL.lane); }
    verges(P, occ, ctx.LV, W, H, 0.18);
    const items = [];
    for (const n of nids) {
      const pl = plan(V, n, day); let tx = 0, ty = 0, tn = 0;
      const KW = 0.6;                                                                       // houses on the region's map: larger than its scale
      const hs = Object.entries(pl.buildings).map(([bid, p]) => { const [x, y] = toWorld(n, p.x + p.w / 2, p.y + p.h / 2), S = styleOf(bid, p.b, KW); return { x, y, x0: x, y0: y, w: S.w, h: S.h, b: p.b, bid }; });
      for (let it = 0; it < 60; it++) { for (const a of hs) for (const c of hs) { if (a === c) continue; const ox = (a.w + c.w) / 2 + 2 - Math.abs(a.x - c.x), oy = (a.h + c.h) / 2 + 2 - Math.abs(a.y - c.y);
          if (ox > 0 && oy > 0) { if (ox < oy) { const s_ = Math.sign(a.x - c.x || 1) * ox / 2; a.x += s_; c.x -= s_; } else { const s_ = Math.sign(a.y - c.y || 1) * oy / 2; a.y += s_; c.y -= s_; } } }
        for (const a of hs) { a.x += (a.x0 - a.x) * 0.02; a.y += (a.y0 - a.y) * 0.02; } }
      for (const q of hs) { const bx = Math.round(q.x - q.w / 2), by = Math.round(q.y - q.h / 2), w = q.w, h = q.h, x = q.x, y = q.y;
        items.push({ y: by + h, f: () => drawBuilding(P, bx, by, q.b, R, q.bid, KW) }); tx += x; ty += y; tn++;
        for (let yy = by + h - 3; yy < by + h + 3; yy++) for (let xx = bx - 2; xx < bx + w + 2; xx++) { const i = ctx.at(xx, yy); if (i >= 0 && ctx.LV[i] > 0 && occ[i] !== 3) P.put(xx, yy, ctx.snow ? PAL.snow[2] : PAL.ground[(xx + yy) & 1]); }
        for (let yy = by - 1; yy < by + h + 2; yy++) for (let xx = bx - 1; xx < bx + w + 1; xx++) { const i = ctx.at(xx, yy); if (i >= 0) occ[i] = 4; } }
      for (const h of pl.herds) for (const [x0, y0, role] of h.pts.slice(0, 10)) { const [x, y] = toWorld(n, x0, y0), col = role === "oxen" ? "#a0663a" : role === "bulls" ? "#4a3428" : "#f4efe6";
        items.push({ y, f: () => { P.put(x, y, col); P.put(x + 1, y, col); P.dark(x + 2, y, .3); } }); }
      for (const t of pl.things) { const [x, y] = toWorld(n, t.x, t.y); items.push({ y, f: () => t.t.kind === "remains" ? (P.put(x, y - 1, t.t.buried != null ? "#c8c4bc" : "#d8d2c4"), P.put(x, y, "#7a5a3a")) : P.put(x, y, "#c9b38a") }); }
      for (const q of pl.people) { const [x, y] = toWorld(n, q.x + 2, q.y); items.push({ y, f: () => person(P, x, y, q.name, { child: q.p.stage === "child" || q.p.stage === "infant", hungry: q.p.hunger <= -1 ? -q.p.hunger : 0 }) });
        out.hotspots.push({ kind: "person", id: q.name, x: (x | 0) - 2, y: (y | 0) - 6, w: 5, h: 7, label: personLabel(q, d, V), node: n }); }
      const pop = Object.values(d.people).filter((p) => p.alive && p.at === n).length, [cx, cy] = tn ? [tx / tn, ty / tn] : pos[n];
      out.hotspots.push({ kind: "node", id: n, x: (pos[n][0] - G[n].land * f * 0.7) | 0, y: (pos[n][1] - G[n].land * f * 0.6) | 0, w: G[n].land * f * 1.4, h: G[n].land * f * 1.2, cx, cy: Math.min(H - 12, cy + 6), label: ST.nodes[n].name, pop,
        unexplored: !!ST.nodes[n].unexplored, biome: M.nodes[n].biome, deaths: d.events.filter((e) => e.place === n && e.kind === "death").length });
    }
    drawTrees(P, ctx.trees, ctx, occ, W, H, R);
    peaks(P, RP, cellPar, occ, W, H, ctx.snow || ctx.season === "winter", 1);
    items.sort((a, b) => a.y - b.y).forEach((it) => it.f());
    for (const [name, p] of Object.entries(d.people)) {                                             // travellers, at the middle of their stretch
      const t = p.transit; if (!t || !p.alive) continue; const r = ST.roads[t.road], pts = roadPts[t.road]; if (!r || !pts || !pts.length) continue;
      const q = pts[RP.sidx[t.road][Math.max(0, Math.min(RP.sidx[t.road].length - 1, t.pos - 1))] ?? 0], k = Object.keys(d.people).filter((m) => d.people[m].transit && d.people[m].transit.road === t.road && d.people[m].transit.pos === t.pos).indexOf(name);
      person(P, q[0] + k * 4, q[1] - 1, name, { tool: "carry" });
      out.hotspots.push({ kind: "person", id: name, x: (q[0] | 0) - 2 + k * 4, y: (q[1] | 0) - 7, w: 6, h: 8, label: `${name} on the road to ${ST.nodes[t.to]?.name || t.to}, day ${t.pos} of ${t.days}` });
    }
    weatherOver(P, W, H, d.weather, rng(hstr("weather|" + day)), true);
    out.season = ctx.season; out.scale = f;
    { let best = null, bp = -1; for (const h of out.hotspots) if (h.kind === "node" && h.pop > bp) { bp = h.pop; best = h; } if (best) out.focus = [best.cx, best.cy]; }
    P.flush();
    return out;
  }
  Object.assign(X, { world });
})(C2X);
