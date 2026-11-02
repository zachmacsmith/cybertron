// c2viz/js/node.js: one place close up, at the end of a day; things lying about; the labels of hotspots.
(function (X) {
  "use strict";
  const { D, PAL, Px, QUIET_EVENTS, beast, bonesBig, drawBuilding, drawTrees, geom, graveBig, hstr, model, nodeRelief, noise, paintLand, paintPath, paintRoad, peaks, person, plan, rng, sackBig, smoke, toolFor, verges, villager, weatherOver } = X;
  // ---------------------------------------------------------------------------------------------------- one place, close up
  function node(cv, V, nid, day, opts = {}) {
    const G = geom(V, nid), W = G.W, H = G.H, M = model(V), N = M.nodes[nid], d = D(V, day), ST = V.static, R = rng(hstr(nid) ^ M.seed ^ day);
    const P = Px(cv, W, H, "#6ca63c"), out = { width: W, height: H, hotspots: [] }, pl = plan(V, nid, day);
    const cellNode = new Int16Array(W * H).fill(0), occ = new Uint8Array(W * H);
    const NR = nodeRelief(V, nid);
    const ctx = paintLand(P, V, day, W, H, [nid], cellNode, G.REG, 1, rng(hstr(nid) ^ M.seed), occ, { scale: "node", courses: G.courses.concat(NR.rivers), relief: NR });
    const n2 = noise(M.seed ^ 5), paint = paintRoad(P, occ, ctx.LV, W, H, ctx.face);
    for (const e of G.exits) {                                                                       // roads leaving, from their ends' parcels
      const r = ST.roads[e.rid], worn = ((d.roads[e.rid] || {}).ends || {})[nid]?.worn || 0, faint = e.end.hidden && worn < 0.8;
      for (const way of e.draw) {                                                                   // each stretch it does not share
        if (faint) paintPath(paint, way, 0, PAL.lane, (x, y) => ((x | 0) * 7 + (y | 0) * 3) % 10 < 3 + worn * 8);
        else paintPath(paint, way, r && r.track ? 2 : 1, r && r.track ? PAL.road : PAL.lane); }
      const lx = Math.max(10, Math.min(W - 10, e.tx)), ly = Math.max(8, Math.min(H - 8, e.ty)), to = ST.nodes[e.to];
      out.hotspots.push({ kind: "exit", id: e.rid, to: e.to, x: lx - 8, y: ly - 8, w: 16, h: 16, label: "→ " + (to?.name || e.to) + " · " + (r?.days ?? "?") + " day" + ((r?.days ?? 1) > 1 ? "s" : "") + (e.end.hidden ? (faint ? " (a hidden way)" : " (a worn path)") : "") });
    }
    if (G.green) { const [gx0, gy0] = G.green, r0 = G.greenR;                                    // the green, and its well
      for (let y = -r0; y <= r0; y++) for (let x = -r0 - 2; x <= r0 + 2; x++) { if (x * x / ((r0 + 2) ** 2) + y * y / (r0 * r0) > 1) continue; const i = ctx.at(gx0 + x, gy0 + y); if (i < 0 || occ[i] === 3) continue;
        P.put(gx0 + x, gy0 + y, ctx.snow ? PAL.snow[0] : ((gx0 + x) * 3 + (gy0 + y) * 5) % 7 ? "#9cd05a" : "#8cc04c"); occ[i] = 2; }
      for (let y = -2; y <= 2; y++) for (let x = -2; x <= 2; x++) { const r_ = Math.hypot(x, y); if (r_ > 2.5) continue; P.put(gx0 + x, gy0 + y, r_ < 1.3 ? "#4e94a8" : (x + y) % 2 ? "#9a9aa0" : "#b4b4ba"); }
      P.dark(gx0 + 3, gy0 + 1, 0.3); P.dark(gx0 + 3, gy0 + 2, 0.3); P.put(gx0 - 2, gy0 - 3, "#6b4423"); P.put(gx0 + 2, gy0 - 3, "#6b4423"); for (let x = -2; x <= 2; x++) P.put(gx0 + x, gy0 - 4, "#8a5a2a"); }
    const B = Object.entries(pl.buildings);
    for (const [, p] of B) for (let y = p.y - 2; y < p.y + p.h + 1; y++) for (let x = p.x - 1; x < p.x + p.w + 1; x++) if (x >= 0 && y >= 0 && x < W && y < H) occ[y * W + x] = 4;
    for (const [bid, p] of B) {                                                                       // a yard before each door; a lane to the nearest road
      for (let y = p.y + p.h - 1; y < p.y + p.h + 6; y++) for (let x = p.x - 2; x < p.x + p.w + 2; x++) { const i = ctx.at(x, y); if (i < 0 || ctx.LV[i] <= 0 || occ[i]) continue;
        const dx = Math.max(p.x - x, x - (p.x + p.w - 1), 0), dy = Math.max(0, y - (p.y + p.h - 1)); if (dx + dy <= 2 + 2.5 * n2(x / 4, y / 4, 2)) { P.put(x, y, ctx.snow ? PAL.snow[2] : n2(x / 2, y / 2, 1) > 0.6 ? PAL.ground[1] : PAL.ground[0]); occ[i] = 2; } }
      let x = p.x + (p.w >> 1), y = p.y + p.h + 1, best = null, bd = 1e9;
      for (let yy = 0; yy < H; yy += 2) for (let xx = 0; xx < W; xx += 2) if (occ[yy * W + xx] === 3) { const dd = (xx - x) ** 2 + (yy - y) ** 2; if (dd < bd) { bd = dd; best = [xx, yy]; } }
      if (best && bd < 90 * 90) for (let s = 0; s < 200; s++) { if (Math.abs(best[0] - x) + Math.abs(best[1] - y) < 1) break; if (Math.abs(best[0] - x) > Math.abs(best[1] - y)) x += Math.sign(best[0] - x); else y += Math.sign(best[1] - y); const i = y * W + x; if (occ[i] !== 4) { P.put(x, y, ctx.snow ? PAL.snow[2] : PAL.lane); if (!occ[i]) occ[i] = 5; } }
    }
    if (!opts.noPeople) for (const q of pl.people) for (let y = q.y - 9; y <= q.y + 1; y++) for (let x = q.x - 1; x < q.x + 7; x++) { const i = ctx.at(x, y); if (i >= 0 && !occ[i]) occ[i] = 1; }
    for (const h of pl.herds) for (const [x0, y0] of h.pts) for (let y = y0 - 5; y <= y0 + 1; y++) for (let x = x0; x < x0 + 9; x++) { const i = ctx.at(x, y); if (i >= 0 && !occ[i]) occ[i] = 1; }
    drawTrees(P, ctx.trees, ctx, occ, W, H, R);
    peaks(P, NR, G.REG, occ, W, H, ctx.snow || ctx.season === "winter", 2);
    for (const [k, x, y] of ctx.marks) if (k === "stook" && !occ[y * W + x]) { P.put(x, y, "#d8b850"); P.put(x, y - 1, "#e8c860"); P.put(x + 1, y, "#c4a03c"); P.dark(x + 1, y + 1, .3); }
    for (const [pid, dp] of Object.entries(d.parcels)) if (dp.smoky && N.pids.includes(pid)) { const i = N.pids.indexOf(pid), [cx, cy] = G.centre[i]; smoke(P, cx | 0, cy | 0); smoke(P, (cx | 0) + 3, (cy | 0) - 2); }
    // everything that stands, back to front
    verges(P, occ, ctx.LV, W, H, 0.18);
    const items = [];
    for (const [bid, p] of B) items.push({ y: p.y + p.h, f: () => { drawBuilding(P, p.x, p.y, p.b, rng(hstr(bid)), bid);
      const pf = G.placeOf[bid]; out.hotspots.push({ kind: "building", id: bid, x: p.x, y: p.y, w: p.w, h: p.h, label: buildingLabel(p.b, d) + (pf && !pf.fits ? " · does not fit its parcel's ground (spec: built 24, scrub 16 spaces a unit of size)" : "") }); } });
    for (const h of pl.herds) { const hR = rng(hstr(h.id + day)); for (const [x, y, role] of h.pts) items.push({ y, f: () => beast(P, x, y, role, hR, h.h.hungry >= 2) });
      if (h.pts.length) { const xs = h.pts.map((q) => q[0]), ys = h.pts.map((q) => q[1]); out.hotspots.push({ kind: "herd", id: h.id, x: Math.min(...xs), y: Math.min(...ys) - 5, w: Math.max(...xs) - Math.min(...xs) + 9, h: Math.max(...ys) - Math.min(...ys) + 7, label: herdLabel(h.h, V) }); } }
    for (const t of pl.things) items.push({ y: t.y, f: () => { drawThing(P, t.x, t.y, t.t, day);
      out.hotspots.push({ kind: "thing", id: t.id, x: t.x - 3, y: t.y - 6, w: 9, h: 8, label: thingLabel(t.t, day) }); } });
    if (!opts.noPeople) for (const q of pl.people) items.push({ y: q.y, f: () => {
      villager(P, q.x, q.y, q.name, { child: q.p.stage === "child" || q.p.stage === "infant", wounded: q.p.wounded, hungry: q.p.hunger <= -1 ? -q.p.hunger : 0,
        speak: q.speaking && !q.a, tool: toolFor(q.a), pregnant: q.p.pregnant, load: (q.p.gear || []).length || Object.keys(q.p.carried || {}).some((i) => i !== "coin") });
      out.hotspots.push({ kind: "person", id: q.name, x: q.x - 1, y: q.y - 9, w: 7, h: 11, label: personLabel(q, d, V) }); } });
    items.sort((a, b) => a.y - b.y).forEach((it) => it.f());
    weatherOver(P, W, H, d.weather, rng(hstr("weather|" + day)), false);
    for (const e of d.events) {                                                                        // marks for what happened, by how far it reaches
      if (e.place !== nid || QUIET_EVENTS.includes(e.kind)) continue;
      let xy = null;
      const bid = (e.about || []).map((x) => String(x).split(":")).find(([k]) => k === "building")?.[1], pid = (e.about || []).map((x) => String(x).split(":")).find(([k]) => k === "parcel")?.[1];
      const who = pl.people.find((q) => q.name === (e.target || e.actor));
      if (bid && pl.buildings[bid]) xy = [pl.buildings[bid].x + pl.buildings[bid].w / 2, pl.buildings[bid].y - 3];
      else if (who) xy = [who.x + 2, who.y - 11];
      else if (pid && N.pids.includes(pid)) xy = G.centre[N.pids.indexOf(pid)];
      else xy = G.mid;
      out.hotspots.push({ kind: "event", id: e.id, x: (xy[0] | 0) - 4, y: (xy[1] | 0) - 4, w: 9, h: 9, label: e.text, event: e.kind, extent: e.extent });
    }
    N.pids.forEach((pid, i) => { if (!G.area[i].length) return; const [cx, cy] = G.centre[i]; let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1; for (const [x, y] of G.area[i]) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
      out.hotspots.push({ kind: "parcel", id: pid, x: x0, y: y0, w: x1 - x0, h: y1 - y0, cx, cy, label: ST.parcels[pid].name, info: parcelLabel(V, pid, d, pl) }); });
    out.biome = N.biome; out.season = ctx.season; out.focus = (() => { const i = N.pids.findIndex((p) => ST.parcels[p].cover === "built"); return i >= 0 ? G.centre[i] : G.mid; })();
    P.flush(); out.P = P;
    return out;
  }

  function drawThing(P, x, y, t, day) {
    if (t.kind === "remains") {
      if (t.buried != null) { if (t.cairn) { for (const [a, b, c] of [[-2, 0, "#9a9aa0"], [-1, 0, "#b4b4ba"], [0, 0, "#9a9aa0"], [1, 0, "#b4b4ba"], [2, 0, "#9a9aa0"], [-1, -1, "#c8c8c8"], [0, -1, "#9a9aa0"], [1, -1, "#b4b4ba"], [0, -2, "#c8c8c8"]]) P.put(x + a, y + b, c); return; }
        if (day - t.buried >= 7) { for (let dx = -2; dx <= 2; dx++) P.mix(x + dx, y, "#7a5a3a", 0.5); return; }   // a sunk mound
        graveBig(P, x, y); return; }
      if (t.body === "bones") { bonesBig(P, x, y); return; }
      villager(P, x, y, t.of || "?", { dead: true });
      if (t.rotting) { P.put(x + 1, y - 3, "#2a2a2a"); P.put(x + 4, y - 2, "#2a2a2a"); }
      return;
    }
    if (t.kind === "carcass") {
      if (t.bones) { bonesBig(P, x, y); return; }
      for (let dx = 0; dx < 6; dx++) { P.put(x + dx - 2, y, t.fresh ? "#a0663a" : "#7a5a3a"); P.put(x + dx - 2, y - 1, t.fresh ? "#b8794a" : "#6a4a2a"); }
      P.put(x - 3, y, "#e0dccc"); P.put(x + 4, y + 1, "#4a2f17"); if (!t.fresh) { P.put(x, y - 3, "#2a2a2a"); P.put(x + 2, y - 2, "#2a2a2a"); }
      return;
    }
    if (t.hidden === "under brush") { for (const [a, b] of [[-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0], [-1, -1], [0, -1], [1, -1], [0, -2]]) P.put(x + a, y + b, (a + b) & 1 ? "#5c7a34" : "#7a6a3a"); return; }
    if (t.hidden === "buried") { for (let dx = -2; dx <= 2; dx++) P.put(x + dx, y, (dx & 1) ? "#8a6a48" : "#7a5a3a"); return; }
    sackBig(P, x, y, t.goods); if (t.heap) { sackBig(P, x + 3, y, t.goods); sackBig(P, x + 1, y - 2, t.goods); }
  }
  function buildingLabel(b, d) {
    const fit = Object.entries(b.fittings || {}).map(([k, v]) => k === "beds" ? `${v} beds` : k), rooms = (b.rooms || []).map((r) => r.kind).join(" and ");
    return `${b.name}: ${b.unfinished ? `being built (${Math.round(b.unfinished.done * 100)}%), ` : ""}${b.structure || ""}${b.condition === 1 ? ", damaged" : b.condition === 0 ? ", in ruins" : ""}`
      + `; ${rooms}${b.derived ? " (rooms derived)" : ""}, ${b.footprint} spaces of ground${b.floor ? `, floor ${b.used}/${b.floor}` : ""}`
      + `${fit.length ? "; " + fit.join(", ") : ""}${b.fire ? "; fire lit last night" : ""}${b.door === "barred" ? "; door barred" : ""}`
      + `${(b.made || []).length ? "; worked today: " + b.made.join(", ") : ""}${b.sleepers.length ? "; slept here: " + b.sleepers.join(", ") : ""}${b.holders.length ? "; held by " + b.holders.join(", ") : ""}`;
  }
  function herdLabel(h, V) {
    const roles = ["cows", "oxen", "bulls", "young"].filter((r) => h[r]).map((r) => `${h[r]} ${r === "young" ? "calves" : r}`).join(", ");
    return `${h.name || "a herd"}: ${roles}${h.in_milk >= 0.5 ? `, ${Math.round(h.in_milk)} in milk` : ""}${h.hungry ? `, hungry ${h.hungry} nights` : ""}${h.watched ? ", herded today" : ""}${h.parcel !== h.home && h.home ? ", off its home ground" : ""}${(h.holders || []).length ? " (" + h.holders.join(", ") + ")" : ""}`;
  }
  function thingLabel(t, day) {
    const goods = Object.entries(t.goods || {}).map(([k, v]) => `${Math.round(v * 10) / 10} ${k}`).join(", ");
    const what = t.kind === "remains" ? (t.buried != null ? (t.cairn ? `a cairn over ${t.of}` : `the grave of ${t.of}`) : `the body of ${t.of}${t.body === "bones" ? " (bones)" : t.rotting ? " (rotting)" : ""}`)
      : t.kind === "carcass" ? `the carcass of ${t.of || "a beast"}${t.bones ? " (bones)" : t.fresh ? " (fresh)" : " (gone off)"}` : t.hidden ? `goods ${t.hidden}` : t.heap ? "a heap of goods" : "goods left lying";
    return what + (goods ? ": " + goods : "");
  }
  function personLabel(q, d, V) {
    const p = q.p, bits = [q.name];
    if (!p.alive) bits.push("dead" + (p.cause ? ` (${p.cause})` : ""));
    if (q.acts && q.acts.length) bits.push(q.acts.map((a) => `${a.verb}${a.tech ? " " + a.tech : ""}${a.for ? " for " + a.for : ""}`).join(", "));
    else if (q.speaking) bits.push("spoke");
    if (p.spot) bits.push("on " + (V.static.parcels[p.spot]?.name || p.spot));
    if (p.hunger <= -1) bits.push(p.hunger <= -2 ? `starving (${p.missed} missed)` : `hungry (${p.missed} missed)`);
    if (p.wounded) bits.push("wounded"); if (p.pregnant) bits.push("pregnant");
    if (p.stage && p.stage !== "adult") bits.push(p.stage);
    const hands = Object.entries(p.carried || {}).map(([k, v]) => `${Math.round(v * 10) / 10} ${k}`).slice(0, 5);
    if (hands.length) bits.push("carrying " + hands.join(", "));
    if (p.slept) bits.push("slept: " + (d.buildings[p.slept]?.name || p.slept));
    return bits.join(" · ");
  }
  function parcelLabel(V, pid, d, pl) {
    const S0 = V.static.parcels[pid], dp = d.parcels[pid] || {}, bits = [`${dp.cover || S0.cover}${dp.was ? ` (was ${dp.was})` : ""}, size ${S0.size}`];
    const c = dp.crop; if (c) bits.push(`${c.kind}: ${c.stage}, ${Math.round(c.sown * 100)}% sown${c.reaped ? `, ${Math.round(c.reaped * 100)}% reaped` : ""}${c.weeds ? ", weedy" : ""}`);
    else if (dp.cover === "field") bits.push(dp.broken > 0.05 ? `${Math.round(dp.broken * 100)}% dug` : dp.last_crop && dp.last_crop !== "fallow" ? `after ${dp.last_kind || dp.last_crop}` : "fallow");
    for (const [k, v] of Object.entries(dp.res || {})) bits.push(`${k} ${Math.round(v * 100)}%`);
    if (dp.cover === "field" || dp.soil) bits.push(`soil ${dp.soil}`);
    if (dp.works) bits.push(`${dp.works.ground === "wet" ? "ditched" : "terraced"} ${Math.round(dp.works.done * 100)}%`);
    if (dp.fence) bits.push(`${dp.fence.kind === "stone" ? "walled" : "fenced"} (${["down", "gappy", "whole"][dp.fence.level]}, gate ${dp.fence.gate})`);
    if (dp.clearing) bits.push(`being cleared ${Math.round(dp.clearing * 100)}%`);
    if (dp.ground_spaces) { const used = Object.values(d.buildings).filter((b) => b.parcel === pid).reduce((s, b) => s + (b.footprint || 0), 0); bits.push(`ground ${used}/${dp.ground_spaces} spaces`); }
    if (dp.felled) bits.push("felled"); if (dp.smoky) bits.push("smoke today");
    if ((dp.holders || []).length) bits.push("held by " + dp.holders.join(", "));
    const nb = (S0.adj || []).map((q) => V.static.parcels[q]?.name).filter(Boolean); bits.push(nb.length ? "next to " + nb.join(", ") : "next to nothing");
    return bits.join("; ");
  }
  Object.assign(X, { node, drawThing, buildingLabel, herdLabel, thingLabel, personLabel, parcelLabel });
})(C2X);
