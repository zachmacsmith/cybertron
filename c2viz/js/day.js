// c2viz/js/day.js: one place close up through a day as it happened (ENGINE.md §11): talk, the acts in the journal's order, routes, dusk and night.
(function (X) {
  "use strict";
  const { D, Px, geom, hstr, model, node, person, rng, toolFor, villager } = X;
  // ---------------------------------------------------------------------------------------------------- a day, as it happened
  // The day's acts in the journal's order (c2viz/model.py: timeline): the land as it was before the work, each act's change landing
  // when the act ends; each person walking the engine's route (layout.route, D4-62) from where they slept, through the parcels of
  // their acts in order, to where the day ends; talk first, the night last. When in the day an act falls and how long a walk across
  // the place takes are presentation (the engine has no clock inside a day and no time to cross a place): an act starts where the
  // actor's earlier acts' units end, against the units they had that day; the walk takes the first part of the act's time.
  const ANIM = new WeakMap();
  function dayRec(V, day, t) {
    const d = V.days[day], T = d.timeline; if (!T || t >= 1) return d;
    const rec = Object.assign({}, d, { parcels: Object.assign({}, T.morning.parcels), buildings: Object.assign({}, T.morning.buildings), herds: Object.assign({}, T.morning.herds), things: Object.assign({}, T.morning.things) });
    for (const a of T.acts) if (a.t1 <= t) for (const k of ["parcels", "buildings", "herds", "things"]) if (a.delta[k]) Object.assign(rec[k], a.delta[k]);
    return rec;
  }
  function anim(V, nid, day) {
    let c = ANIM.get(V); if (!c) ANIM.set(V, c = {}); const key = nid + "|" + day; if (c[key]) return c[key];
    const d = V.days[day], T = d.timeline, G = geom(V, nid), M = model(V), N = M.nodes[nid], ST = V.static;
    const acts = T ? T.acts.filter((a) => a.node === nid) : [], people = T ? Object.entries(T.morning.people).filter(([, p]) => p.at === nid && p.alive) : [];
    const blocked = (x, y) => Object.values(G.placeOf).some((b) => x > b.x - 3 && x < b.x + b.w + 3 && y > b.y - 2 && y < b.y + b.h + 3);
    const spotIn = (pid, name, salt) => { const i = N.pids.indexOf(pid); if (i < 0 || !G.area[i].length) return G.mid.slice(); const R = rng(hstr(name + "|" + pid + "|" + salt + "|" + day));
      for (let k = 0; k < 30; k++) { const [x, y] = G.area[i][(R() * G.area[i].length) | 0]; if (!blocked(x, y) && G.reg(x + 5, y) === i && G.reg(x, y - 9) === i) return [x, y]; } return G.centre[i].slice(); };
    const parcelOfSite = (s_) => !s_ ? null : ST.parcels[s_] ? s_ : (G.placeOf[s_] && d.buildings[s_]) ? d.buildings[s_].parcel : (d.things[s_] || (T && T.morning.things[s_]) || {}).parcel || null;
    const out = { people: [], cache: {}, acts };
    for (const [name, p] of people) {
      const home = (p.homes || []).map((b) => G.placeOf[b]).find(Boolean), door = home ? [home.x + (home.w >> 1) - 2, home.y + home.h + 4] : null;
      const route = (T.routes || {})[name] || [], mine = acts.filter((a) => a.actor === name).sort((a, b) => a.t0 - b.t0);
      const start = door || (route[0] ? spotIn(route[0], name, "s") : G.mid.slice()), keys = [[-1, start[0], start[1]]], work = [];
      let ri = 0, at = start;
      for (const a of mine) {
        const tgt = parcelOfSite(a.site), j = tgt ? route.indexOf(tgt, ri) : -1;
        if (j > ri || (tgt && j === -1 && route[ri] !== tgt)) {                              // walk the route's parcels to the site
          const legs = j > ri ? route.slice(ri + 1, j + 1) : [tgt], wd = Math.min(0.45 * (a.t1 - a.t0), 0.03 * legs.length);
          keys.push([a.t0, at[0], at[1]]);
          legs.forEach((pid, k) => { const pt = k === legs.length - 1 ? spotIn(pid, name, a.t0) : spotIn(pid, name, "pass" + k); keys.push([a.t0 + wd * (k + 1) / legs.length, pt[0], pt[1]]); at = pt; });
          work.push([a.t0 + wd, a.t1, a]); if (j > ri) ri = j;
        } else { if (tgt && route[ri] === tgt && keys.length === 1) { const pt = spotIn(tgt, name, a.t0); keys.push([a.t0, at[0], at[1]], [a.t0 + 0.03, pt[0], pt[1]]); at = pt; } work.push([a.t0, a.t1, a]); }
        keys.push([a.t1, at[0], at[1]]);
      }
      const last = mine.length ? mine[mine.length - 1].t1 : 0, tail = route.slice(ri + 1);
      if (tail.length) { keys.push([last, at[0], at[1]]); tail.forEach((pid, k) => { const end = k === tail.length - 1 && pid === route[0] && door ? door : spotIn(pid, name, "pass" + k); keys.push([last + 0.1 * (k + 1) / tail.length, end[0], end[1]]); at = end; }); }
      const indoors = door && Math.abs(at[0] - door[0]) + Math.abs(at[1] - door[1]) < 2;
      const said = (T.talk || []).filter((e) => e.actor === name && e.place === nid).length;
      out.people.push({ name, p, keys, work, said, indoors, end: (d.people[name] || p) });
    }
    return (c[key] = out);
  }
  function posAt(keys, t) {
    if (t <= keys[0][0]) return [keys[0][1], keys[0][2], false];
    for (let k = 1; k < keys.length; k++) if (t <= keys[k][0]) { const [t0, x0, y0] = keys[k - 1], [t1, x1, y1] = keys[k], f = t1 > t0 ? (t - t0) / (t1 - t0) : 1;
      return [x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, Math.abs(x1 - x0) + Math.abs(y1 - y0) > 0.5]; }
    const k = keys[keys.length - 1]; return [k[1], k[2], false];
  }
  // one frame of the day at time t (-0.1 the talk before work, 0 to 1 the work, past 1 dusk and night)
  function nodeAt(cv, V, nid, day, t) {
    const A = anim(V, nid, day), done = t >= 1 ? "night" : A.acts.filter((a) => a.t1 <= t).length;
    if (!A.cache[done]) { V.__at = { day, key: done, rec: dayRec(V, day, t) }; try { const o = node(cv, V, nid, day, { noPeople: true }); A.cache[done] = { buf: o.P.save(), out: o }; } finally { V.__at = null; } }
    const C0 = A.cache[done], o = C0.out, W = o.width, H = o.height, P = Px(cv, W, H); P.restore(C0.buf);
    const hot = o.hotspots.filter((h) => h.kind !== "person"), dark = t >= 1 ? Math.min(0.55, 0.25 + (t - 1) * 3) : t > 0.9 ? (t - 0.9) * 2.5 : 0;
    const ppl = A.people.map((q) => { const [x, y, moving] = posAt(q.keys, t), w_ = q.work.find(([a, b]) => t >= a && t < b); return { q, x: x | 0, y: y | 0, moving, act: w_ && w_[2] }; })
      .filter((r) => !(t >= 1.02 && (r.q.indoors || (r.q.end.slept && r.q.end.slept !== "out") || r.q.end.alive === false || r.q.end.at !== nid))).sort((a, b) => a.y - b.y);   // night: the night log's beds, the dead as their bodies, those gone on the road
    for (const r of ppl) { const p = r.q.p, bob = r.moving && ((t * 400) | 0) % 2 ? 1 : 0;
      villager(P, r.x, r.y - bob, r.q.name, { child: p.stage === "child" || p.stage === "infant", wounded: p.wounded, hungry: p.hunger <= -1 ? -p.hunger : 0, speak: t < 0.02 && r.q.said,
        tool: r.act ? toolFor(r.act) : null, pregnant: p.pregnant });
      hot.push({ kind: "person", id: r.q.name, x: r.x - 1, y: r.y - 9, w: 7, h: 11, label: r.q.name + (r.act ? ` · ${r.act.verb}${r.act.tech ? " " + r.act.tech : ""}${r.act.for ? " for " + r.act.for : ""}` : r.moving ? " · walking" : t < 0 ? " · talking" : "") }); }
    if (dark > 0) { for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) P.mix(x, y, "#1b2444", dark);
      if (t >= 1) for (const b of Object.values(D(V, day).buildings)) { const pl_ = geom(V, nid).placeOf[Object.keys(D(V, day).buildings).find((k) => D(V, day).buildings[k] === b)]; if (!pl_ || !(b.sleepers || []).length) continue;
        const dx = pl_.x + (pl_.w >> 1), dy = pl_.y + pl_.h - 2; for (const [a, c] of [[0, 0], [1, 0], [0, -1], [1, -1]]) P.put(dx + a, dy + c, "#f0c060"); P.mix(dx - 1, dy + 1, "#f0c060", 0.4); P.mix(dx + 2, dy + 1, "#f0c060", 0.4); } }
    P.flush();
    return Object.assign({}, o, { hotspots: hot, t, phase: t < 0 ? "talk" : t < 0.3 ? "morning" : t < 0.6 ? "midday" : t < 0.9 ? "afternoon" : t < 1 ? "dusk" : "night", acts: A.acts.length });
  }
  Object.assign(X, { ANIM, dayRec, anim, posAt, nodeAt });
})(C2X);
