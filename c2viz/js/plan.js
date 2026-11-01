// c2viz/js/plan.js: a place on a day: where its buildings, herds, things and people stand.
(function (X) {
  "use strict";
  const { D, geom, hstr, model, rng } = X;
  // ---------------------------------------------------------------------------------------------------- a place on a day
  // where its buildings (placed for the run), herds, things and people stand on a day, in close-up pixels; the region's map shows
  // them at the same spots, smaller. People stand on the parcel the engine says they are on (things.spot_of, in the record as
  // `spot`); one who worked nowhere today stands at the door of their home.
  const PLAN = new WeakMap();
  function plan(V, nid, day) {
    let cache = PLAN.get(V); if (!cache) PLAN.set(V, cache = {});
    const key = nid + "|" + day + (V.__at && V.__at.day === day ? "|" + V.__at.key : ""); if (cache[key]) return cache[key];
    const G = geom(V, nid), W = G.W, H = G.H, M = model(V), N = M.nodes[nid], d = D(V, day), occ = new Uint8Array(W * H);
    const out = { W, H, buildings: {}, herds: [], things: [], people: [], occ };
    const mark = (x0, y0, w, h, v) => { for (let y = y0; y < y0 + h; y++) for (let x = x0; x < x0 + w; x++) if (x >= 0 && y >= 0 && x < W && y < H) occ[y * W + x] = v; };
    for (const [bid, b] of Object.entries(d.buildings)) {
      if (b.node !== nid || !G.placeOf[bid]) continue;
      const p = G.placeOf[bid]; out.buildings[bid] = { x: p.x, y: p.y, w: p.w, h: p.h, b }; mark(p.x - 2, p.y - 3, p.w + 6, p.h + 4, 4);
    }
    const free = (x, y, w, h) => { for (let yy = y - h; yy <= y; yy++) for (let xx = x; xx < x + w; xx++) { if (xx < 0 || yy < 0 || xx >= W || yy >= H || occ[yy * W + xx]) return false; } return true; };
    const spot = (i, R, near, rad, w, h) => {
      const cells = G.area[i] || []; if (!cells.length) return null;
      for (let t = 0; t < 80; t++) { const c = near ? [near[0] + (R() - .5) * 2 * rad, near[1] + (R() - .5) * 2 * rad] : cells[(R() * cells.length) | 0], x = c[0] | 0, y = c[1] | 0;
        if (G.reg(x, y) === i && G.reg(x + w, y) === i && G.reg(x, y - h) === i && free(x, y, w, h)) return [x, y]; }
      return null;
    };
    for (const [hid, h] of Object.entries(d.herds)) {                                            // each head by its role
      if (h.node !== nid) continue; const i = N.pids.indexOf(h.parcel); if (i < 0) continue;
      const hR = rng(hstr(hid + "|" + day)), heads = [];
      for (const role of ["cows", "oxen", "bulls", "young"]) for (let k = 0; k < Math.min(h[role] || 0, 20); k++) heads.push(role);
      const c0 = spot(i, hR, null, 0, 8, 5) || G.centre[i], pts = [];
      for (const role of heads) { const s = spot(i, hR, c0, 6 + Math.sqrt(heads.length) * 6, 9, 6); if (s) { pts.push([s[0], s[1], role]); mark(s[0], s[1] - 5, 9, 7, 6); } }
      out.herds.push({ id: hid, h, pts });
    }
    for (const [cid, t] of Object.entries(d.things)) {
      if (t.node !== nid || t.stretch != null) continue;
      if (t.in && !t.door) continue;                                                              // inside a house: not seen from outside
      const i = N.pids.indexOf(t.parcel), Bd = t.door && out.buildings[t.door], tR = rng(hstr(cid));
      let s = Bd ? [Bd.x + (Bd.w >> 1) + 3, Bd.y + Bd.h + 3] : i >= 0 ? spot(i, tR, null, 0, 7, 5) : null; if (!s) s = i >= 0 ? G.centre[i] : G.mid;
      out.things.push({ id: cid, t, x: s[0] | 0, y: s[1] | 0 }); mark((s[0] | 0) - 3, (s[1] | 0) - 6, 9, 8, 6);
    }
    const acts = {}; for (const a of d.acts) if (a.node === nid) (acts[a.actor] = acts[a.actor] || []).push(a);
    const speaking = new Set(d.events.filter((e) => e.kind === "speech" && e.place === nid).map((e) => e.actor));
    const atDoor = {}, anchor = {};
    for (const [name, p] of Object.entries(d.people).filter(([, p]) => p.at === nid && p.alive).sort((a, b) => a[0] < b[0] ? -1 : 1)) {
      const pR = rng(hstr(name + "|" + day)), i = N.pids.indexOf(p.spot), home = (p.homes || []).map((b) => out.buildings[b]).find(Boolean);
      let s = null;
      if (!(p.worked || []).length && home) { const k = atDoor[home.b.name] = (atDoor[home.b.name] || 0) + 1;
        s = [home.x + (home.w >> 1) - 2 + ((k - 1) % 3 - 1) * 7, home.y + home.h + 11 + Math.floor((k - 1) / 3) * 11]; }
      else if (i >= 0) { if (!anchor[i]) anchor[i] = spot(i, rng(hstr(p.spot + "|" + day)), null, 0, 6, 10) || G.centre[i]; s = spot(i, pR, anchor[i], 24, 6, 10) || spot(i, pR, null, 0, 6, 10); }
      if (!s) s = i >= 0 ? G.centre[i] : G.mid;
      s = [s[0] | 0, s[1] | 0]; mark(s[0] - 1, s[1] - 9, 7, 11, 7);
      const mine = acts[name] || [];
      out.people.push({ name, p, a: mine[mine.length - 1], acts: mine, speaking: speaking.has(name), x: s[0], y: s[1] });
    }
    cache[key] = out; return out;
  }
  Object.assign(X, { PLAN, plan });
})(C2X);
