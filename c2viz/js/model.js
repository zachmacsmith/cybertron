// c2viz/js/model.js: per run: each place's parcels and character, and which day's record is drawn (D).
(function (X) {
  "use strict";
  const { RIVER, biomeOf, hstr, noise } = X;
  // ---------------------------------------------------------------------------------------------------- the land model
  const D = (V, day) => (V.__at && V.__at.day === day) ? V.__at.rec : V.days[Math.max(0, Math.min(V.days.length - 1, day))];
  const MODEL = new WeakMap();
  function model(V) {
    let M = MODEL.get(V); if (M) return M;
    M = { nodes: {}, seed: hstr(String(V.meta.seed ?? 1) + "|" + V.meta.name) };
    for (const nid of Object.keys(V.static.nodes)) {
      const pids = Object.keys(V.static.parcels).filter((p) => V.static.parcels[p].node === nid).sort();
      M.nodes[nid] = { pids, biome: biomeOf(V, nid), jit: noise(hstr(nid) ^ M.seed),
        river: pids.map((p) => RIVER.test((V.static.parcels[p].name || "") + " " + (V.static.parcels[p].text || "")) && V.static.parcels[p].cover === "water") };
    }
    MODEL.set(V, M); return M;
  }
  Object.assign(X, { D, MODEL, model });
})(C2X);
