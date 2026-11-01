// c2viz/js/buildings.js: buildings by what they are made of and their rooms (the spec's model, economy/buildings.md), their state and fittings as seen outside; beasts by role.
(function (X) {
  "use strict";
  const { FIRES, hstr, tool } = X;
  // ---------------------------------------------------------------------------------------------------- buildings
  // A building is drawn from what it is made of (the engine's structure: wattle, timber, stone, camp) and from its rooms (the spec's
  // model, economy/buildings.md D2-154: a small room 6 spaces, a medium 12, a hall 30, at SPACE pixels a space): seen from above
  // and a little in front, its roof (thatch on wattle; thatch or oak shingles on timber; stone slates, now and then thatch, on
  // stone) and its front wall (clay daub on woven hazel with corner posts; a dark oak frame with pale infill on a stone footing;
  // coursed rubble with quoins). Upper storeys (stone only) raise the wall. Its state: fresh straw when new, old thatch with holes
  // and fallen daub when damaged, a roofless shell when ruined, posts and rafters filling with walls as it is built, a barred
  // door. Its fittings as they show outside: a chimney for a hearth, an oven or a forge (smoke through the thatch for a wattle
  // house), the oven's dome, an anvil, a water wheel on the race, millstones, a granary on staddle stones, a woodpile from its
  // store. The roof's form (gabled, hipped, a gable to the front) and the roofing where there is a choice are presentation:
  // each village leans to one form and one roofing, and each house varies, by a hash of its id (ENGINE.md §9).
  const SPACE = 54;
  const hsh = (a, b, s) => { let h = (a * 374761393 + b * 668265263 + s * 2246822519) | 0; h = Math.imul(h ^ h >>> 13, 1274126177); return ((h ^ h >>> 16) >>> 0) / 4294967296; };
  const ROOFS = {
    thatch: { lit: "#e2be72", mid: "#c9a45a", shade: "#a8863e", deep: "#7e6230", ridge: ["#8a6a30", "#a07a38"], tex: (x, y, s) => (y % 2 === 0 && hsh(x >> 1, y, s) > 0.55) ? -0.12 : (hsh(x, y, s + 9) > 0.93 ? 0.1 : 0) },
    thatchNew: { lit: "#f0d48a", mid: "#dcbc6c", shade: "#bc9a4c", deep: "#8e7038", ridge: ["#a07e3a", "#b88e44"], tex: (x, y, s) => (y % 2 === 0 && hsh(x >> 1, y, s) > 0.6) ? -0.08 : 0 },
    thatchOld: { lit: "#a89a6a", mid: "#8e8256", shade: "#726842", deep: "#544c30", ridge: ["#5e5234", "#6e6040"], tex: (x, y, s) => (hsh(x, y, s) > 0.8 ? 0.1 : 0) + ((y % 2 === 0 && hsh(x >> 1, y, s) > 0.5) ? -0.1 : 0) + (hsh(x >> 2, y >> 1, s + 4) > 0.85 ? -0.12 : 0) },
    shingle: { lit: "#a08060", mid: "#8a6a4c", shade: "#6e523a", deep: "#4e3a28", ridge: ["#5a4430", "#6e543c"], tex: (x, y, s) => (y % 2 === 1 ? -0.16 : 0) + (((x + (y >> 1) * 2) % 4 === 0 && y % 2 === 0) ? -0.14 : 0) },
    slate: { lit: "#a4a4ac", mid: "#8c8c96", shade: "#70707c", deep: "#54545e", ridge: ["#5e5e68", "#7a7a84"], tex: (x, y, s) => (y % 3 === 2 ? -0.18 : 0) + (((x + Math.floor(y / 3) * 3) % 6 === 0 && y % 3 !== 2) ? -0.15 : 0) + (hsh(x >> 1, y, s) > 0.9 ? 0.06 : 0) },
  };
  const WALLS = {
    wattle: (x, y, w, h, s) => { const c = hsh(x >> 1, y >> 1, s) > 0.7 ? "#cdb07a" : hsh(x, y, s + 3) > 0.85 ? "#e6d2a0" : "#d9c18c"; return (x === 0 || x === w - 1) ? "#6e4a28" : c; },
    timber: (x, y, w, h, s) => {
      if (y === h - 1) return (x % 3 === 0) ? "#8a857a" : "#a8a296";
      const bay = 5, bx = x % bay, panel = Math.floor(x / bay);
      if (x === 0 || x === w - 1 || bx === 0 || y === 0 || y === Math.floor((h - 1) / 2)) return "#4a2f1c";
      if (panel % 2 === 0 && y < Math.floor((h - 1) / 2) && bx === y) return "#4a2f1c";
      return hsh(x, y, s) > 0.88 ? "#e4d8bc" : "#f0e6cc";
    },
    stone: (x, y, w, h, s) => {
      if (x <= 1 || x >= w - 2) return (Math.floor(y / 2) % 2 === (x <= 1 ? 0 : 1)) ? "#d0cabc" : "#b8b2a4";
      const course = Math.floor(y / 2), off = course * 3 + Math.floor(hsh(course, 0, s) * 3), joint = (x + off) % 4 === 0 || y % 2 === 1 && hsh(x, y, s) > 0.5;
      if (joint) return "#857f72";
      const v = hsh(Math.floor((x + off) / 4), course, s); return v > 0.66 ? "#c4beb0" : v > 0.33 ? "#b2ac9e" : "#a29c8e";
    },
  };
  const FORMS = ["gable", "hip", "front"];
  // a building's look for the run: its rooms' boxes, its roof's form and roofing (presentation, by village and by house)
  function styleOf(bid, b, scale) {
    const v = hstr("village|" + (b.node || "")), h = hstr(bid), st = b.structure || "timber", k = scale || 1;
    const form = (h % 10) < 6 ? FORMS[v % 3] : FORMS[(h >>> 4) % 3];
    let roofing = st === "stone" ? ((h >>> 8) % 6 === 0 ? "thatch" : "slate") : st === "timber" ? (((h >>> 6) % 10) < 7 ? ((v >>> 3) % 2 ? "shingle" : "thatch") : ((v >>> 3) % 2 ? "thatch" : "shingle")) : "thatch";
    if (roofing === "thatch") roofing = b.condition === 1 ? "thatchOld" : b.new ? "thatchNew" : "thatch";
    const wallH = Math.max(3, Math.round((st === "wattle" ? 6 : 8) * k)), byre = /byre|barn|stall|shed/i.test(b.name || "") || (b.fittings || {}).stalls;
    const rooms = (b.rooms || [{ floor: 6, storey: 1 }]).filter((r) => (r.storey || 1) === 1).slice().sort((a, c) => c.floor - a.floor);
    const storeys = st === "stone" ? 1 + Math.min(2, (b.rooms || []).filter((r) => (r.storey || 1) > 1).length ? 1 : 0) : 1;
    const parts = []; let x = 0, H = 0;
    rooms.forEach((r, i) => {
      const fw = Math.max(9, Math.round(Math.sqrt(r.floor * SPACE * (byre ? 2.4 : 1.35)))), fh = Math.max(7, Math.round(r.floor * SPACE / fw));
      const w = Math.max(5, Math.round(fw * k)), wall = byre ? Math.max(3, wallH - 1) : wallH, d = Math.max(4, Math.round(fh * k) - Math.round(wall * 0.55));
      const pf = i === 0 ? form : (hstr(bid + i) % 2 ? "front" : form);
      parts.push({ x, w, d, wall, storeys: i === 0 ? storeys : 1, form: pf, seed: (h >>> 3) + i }); x += w - 1; H = Math.max(H, d + wall * (i === 0 ? storeys : 1));
    });
    const left = (b.fittings || {})["water wheel"] ? Math.round(9 * k) : 0, right = ((b.fittings || {}).anvil || (b.fittings || {}).oven) ? Math.round(8 * k) : 0;
    return { w: x + 1 + left + right, h: H + Math.round(2 * k), left, right, H, parts, roofing, form, k };
  }
  function shape(b, bid) { const S = styleOf(bid || b.name || "", b); return { w: S.w, h: S.h }; }
  // one room's box: front wall below, roof above
  function box(P, x0, y0, p, b, R, Wf, k) {
    const w = p.w, d = p.d, st = p.storeys, wallH = p.wall * st, s = p.seed, H = d + wallH, ruined = b.condition === 0, form = p.form;
    for (let y = 2; y <= H + 1; y++) P.dark(x0 + w + 1, y0 + y, 0.3);
    for (let x = 2; x <= w + 1; x++) P.dark(x0 + x, y0 + H + 1, 0.3);
    for (let y = 0; y < wallH; y++) for (let x = 0; x < w; x++) {
      if (ruined && y < wallH * 0.5 && hsh(x >> 1, y, s) > 0.35 + y / wallH) continue;
      P.put(x0 + x, y0 + d + y, Wf(x, y % p.wall, w, p.wall, s + Math.floor(y / p.wall)));
    }
    if (!ruined) for (let x = 0; x < w; x++) { P.dark(x0 + x, y0 + d, 0.38); P.dark(x0 + x, y0 + d + 1, 0.16); }
    if (b.condition === 1 && !ruined && b.structure === "wattle") { const cx = (w * 0.3) | 0; for (let y = 1; y < p.wall - 1; y++) { P.put(x0 + cx + (y & 1), y0 + d + y, "#8a6a40"); P.put(x0 + cx + 1 + (y & 1), y0 + d + y, "#a07e4a"); } }
    if (k >= 0.8) for (let f = 0; f < st; f++) { const wy = y0 + d + f * p.wall + 1;                                  // windows, shuttered
      for (let wx = 2; wx < w - 3; wx += 7) { if (p.door != null && Math.abs(wx - p.door) < 3 && f === st - 1) continue;
        if (b.structure === "wattle") { P.put(x0 + wx, wy, "#3a2c20"); P.put(x0 + wx + 1, wy, "#3a2c20"); }
        else { P.put(x0 + wx, wy, "#2a2018"); P.put(x0 + wx + 1, wy, "#2a2018"); P.put(x0 + wx, wy + 1, "#3a2c20"); P.put(x0 + wx + 1, wy + 1, "#3a2c20"); P.put(x0 + wx - 1, wy, "#7a5a3a"); P.put(x0 + wx + 2, wy, "#7a5a3a"); } } }
    else for (let f = 0; f < st; f++) P.put(x0 + 1 + (w >> 2), y0 + d + f * p.wall + 1, "#3a2c20");
    if (p.door != null && !ruined) { const dh = Math.max(2, Math.min(4, p.wall - 1)), dw = k >= 0.8 ? 2 : 1;
      for (let y = 0; y < dh; y++) for (let x = 0; x < dw; x++) P.put(x0 + p.door + x, y0 + H - 1 - y, y === dh - 1 ? "#4a2f1c" : (x ? "#6b4423" : "#7e5430"));
      if (b.door === "barred") for (let x = -1; x <= dw; x++) P.put(x0 + p.door + x, y0 + H - 2, "#3a2414"); }
    if (ruined) { for (let y = 0; y < d; y++) for (let x = 0; x < w; x++) { const edge = x === 0 || x === w - 1 || y === d - 1 || y === 0;
        P.put(x0 + x, y0 + y, edge ? Wf(x, 1, w, p.wall, s) : hsh(x, y, s) > 0.75 ? "#8a8478" : "#5a4a3a"); } return H; }
    roof(P, x0, y0, w, d, form, b, R, Wf, s, p.wall);
    if (b.condition === 1) for (let n = 0; n < Math.max(1, w >> 3); n++) { const hx = x0 + 2 + Math.floor(hsh(n, 1, s) * (w - 5)), hy = y0 + 1 + Math.floor(hsh(n, 2, s) * (d - 3)); P.put(hx, hy, "#3a2a1a"); P.put(hx + 1, hy, "#4a3a28"); P.put(hx, hy + 1, "#5a4a30"); }
    return H;
  }
  function roof(P, x0, y0, w, d, form, b, R, Wf, s, wall) {
    const ridge = Math.floor(d * 0.4), thatch = R === ROOFS.thatch || R === ROOFS.thatchNew || R === ROOFS.thatchOld;
    const put = (x, y, base, t2) => { const t = R.tex(x, y, s) + (t2 || 0); P.put(x0 + x, y0 + y, base); if (t > 0) P.light(x0 + x, y0 + y, t); else if (t < 0) P.dark(x0 + x, y0 + y, -t); };
    const ov = thatch ? 1 : 0;
    for (let y = 0; y < d; y++) for (let x = -ov; x < w + ov; x++) {
      if (thatch && (y === 0 || y === d - 1) && (x === -ov || x === w - 1 + ov)) continue;
      let base, t2 = 0;
      if (form === "front") {
        const mid = (w - 1) / 2, side = x - mid;
        if (Math.abs(side) < 0.6) { base = R.ridge[1]; t2 = 0.05; }
        else if (side < 0) { base = R.lit; t2 = -0.1 * (Math.abs(side) / mid); }
        else { base = R.shade; t2 = -0.1 * (side / mid); }
        if (Math.abs(side) >= mid - 0.5 + ov) base = R.deep;
      } else {
        const e = Math.min(x, w - 1 - x) + ov, k = Math.abs(y - ridge), hipEnd = form === "hip" && e < k * 1.1 + 1, seam = form === "hip" && Math.abs(e - (k * 1.1 + 1)) < 0.75 && y !== ridge;
        if (seam) { base = R.deep; t2 = 0.05; }
        else if (hipEnd) { base = x < w / 2 ? R.lit : R.shade; t2 = x < w / 2 ? 0.22 : -0.12; }
        else if (y === ridge) base = R.ridge[0];
        else if (y === ridge - 1) { base = R.ridge[1]; t2 = 0.06; }
        else if (y < ridge) { base = R.lit; t2 = 0.04 * (ridge - y) / Math.max(1, ridge) - 0.04; }
        else { base = R.mid; t2 = -0.16 * (y - ridge) / Math.max(1, d - ridge); }
        if (!hipEnd && form === "gable" && (x === -ov || x === w - 1 + ov)) { base = x <= 0 ? R.lit : R.shade; t2 = x <= 0 ? 0.08 : -0.1; }
      }
      if (y === d - 1) { base = R.deep; t2 = 0; }
      put(x, y, base, t2);
    }
    if (form === "front" && d >= 6) {
      const mid = (w - 1) / 2, gh = Math.min(4, d - 2);
      for (let y = 0; y < gh; y++) for (let x = 0; x < w; x++) { const half = (y + 1) * w / 9; if (Math.abs(x - mid) < half) P.put(x0 + x, y0 + d - gh + y, Wf(x, y + 1, w, wall, s)); }
      for (let y = 0; y < gh; y++) { const half = Math.ceil((y + 1) * w / 9); P.put(x0 + Math.round(mid - half), y0 + d - gh + y, R.deep); P.put(x0 + Math.round(mid + half), y0 + d - gh + y, R.deep); }
    }
    if (thatch) for (let x = 0; x < w; x++) if (hsh(x, 7, s) > 0.55) P.put(x0 + x, y0 + d, R.deep);
  }
  function frameOf(P, x0, y0, p, done, stone) {                                                 // being built: posts, rails, rafters, walls by the work done
    const w = p.w, d = p.d, H = d + p.wall;
    for (let x = 0; x < w; x += 4) for (let y = d - 1; y < H; y++) P.put(x0 + x, y0 + y, "#6e4a28");
    for (let x = 0; x < w; x++) { P.put(x0 + x, y0 + d - 1, "#7e5430"); P.put(x0 + x, y0 + H - 1, "#a8a296"); }
    const fill = Math.round((H - d) * done); for (let y = H - 1 - fill; y < H - 1; y++) for (let x = 1; x < w - 1; x++) if (x % 4) P.put(x0 + x, y0 + y, stone ? WALLS.stone(x, y, w, p.wall, 3) : (x + y) % 2 ? "#a07e4a" : "#8a6a40");
    for (let x = 1; x < w; x += 3) for (let y = 0; y < d - 1; y++) P.put(x0 + x, y0 + y, "#8a6038");
    for (let x = 0; x < w; x++) P.put(x0 + x, y0 + Math.floor(d * 0.4), "#6e4a28");
  }
  function smoke(P, x, y, sparks) { for (let k = 0; k < 6; k++) { const xx = x + Math.round(Math.sin(k * 0.9) * 1.2) + (k > 3 ? 1 : 0), yy = y - k; P.mix(xx, yy, "#e8e8e8", 0.75 - k * 0.09); }
    if (sparks) { P.put(x - 1, y + 1, "#f0c060"); P.put(x + 1, y, "#f08a3a"); } }
  // the whole building at (x0, y0), the top left of its box (shape()); k: its scale (1 close up, about half on the region's map)
  function drawBuilding(P, x0, y0, b, R, bid, k = 1) {
    const S = styleOf(bid, b, k), fit = b.fittings || {}, made = new Set(b.made || []), st = b.structure || "timber", Rf = ROOFS[S.roofing], Wf = WALLS[st] || WALLS.timber;
    const bx = x0 + S.left;
    if (st === "camp") { campOf(P, bx, y0 + S.h - Math.round(10 * k), b.fire, k, b.nights_left); return S; }
    const raised = fit.granary && !fit.beds ? Math.round(2 * k) : 0;
    if (raised) for (let x = 1; x < S.parts[0].w; x += 4) { P.put(bx + x, y0 + S.h - 1, "#b4b4ba"); P.put(bx + x - 1, y0 + S.h - 2, "#c8c8c8"); P.put(bx + x + 1, y0 + S.h - 2, "#c8c8c8"); }
    S.parts.forEach((p, i) => { const py = y0 + S.H - (p.d + p.wall * p.storeys) - raised;
      if (i === 0) p.door = Math.max(2, Math.min(p.w - 4, (p.w >> 1) + ((hstr(bid) % 5) - 2)));
      if (b.unfinished) frameOf(P, bx + p.x, py, p, b.unfinished.done || 0, st === "stone");
      else box(P, bx + p.x, py, p, b, Rf, Wf, k); });
    if (b.unfinished) { for (let j = 0; j < 5; j++) { P.put(bx + S.w - S.left - S.right + 1 + j, y0 + S.H - 1, "#8a6038"); P.put(bx + S.w - S.left - S.right + 2 + j, y0 + S.H - 2, "#a07a48"); } return S; }
    if (b.condition === 0) return S;
    const main = S.parts[0], my = y0 + S.H - (main.d + main.wall * main.storeys) - raised, lit = b.fire || ["bread", "oven bread", "dry meat", "smelt", "copper tool", "coin"].some((t) => made.has(t));
    const fires = FIRES.filter((f) => fit[f]);
    if (fires.length && st !== "wattle") fires.slice(0, 2).forEach((f, j) => { const cx = bx + main.x + (j ? 3 : main.w - 5), cy = my + Math.floor(main.d * 0.4) - 2;
      for (let y = 0; y < 4; y++) { P.put(cx, cy + y, "#9a958a"); P.put(cx + 1, cy + y, "#7a766c"); } P.put(cx, cy, "#b8b2a4"); P.put(cx + 1, cy, "#8a857a");
      if (lit) smoke(P, cx, cy - 2, f === "anvil" && made.has("smelt")); });
    else if (lit) for (let j = 0; j < 4; j++) P.mix(bx + (main.w >> 1) + (j > 1 ? 1 : 0), my + Math.floor(main.d * 0.4) - 1 - j, "#e8e8e8", 0.6 - j * 0.1);   // smoke through the thatch
    if (fit["water wheel"]) { const r = Math.max(3, Math.round(5 * k)), cx = x0 + Math.round(4 * k), cy = y0 + S.H - r - 2, turning = made.has("water mill");
      for (let y = -r - 2; y <= r + 3; y++) for (let x = -3; x <= 3; x++) P.put(cx + x, cy + y, y > r ? "#4e94a8" : "#5aa2b4");
      for (let a = 0; a < 16; a++) { const t = a * Math.PI / 8; P.put(cx + Math.round(r * Math.cos(t)), cy + Math.round(r * Math.sin(t)), "#6e4a28"); P.put(cx + Math.round((r + 1) * Math.cos(t)), cy + Math.round((r + 1) * Math.sin(t)), a % 2 ? "#8a6038" : "#5a3a20"); }
      for (let a = 0; a < 4; a++) { const t = a * Math.PI / 4 + (turning ? 0.3 : 0); for (let q = -r; q <= r; q++) P.put(cx + Math.round(q * Math.cos(t)), cy + Math.round(q * Math.sin(t)), "#7e5430"); }
      P.put(cx, cy, "#3a2414"); if (turning) for (let q = 0; q < 4; q++) P.put(cx - 2 + q * 2, cy + r + 2, "#e8f8f8"); }
    else if (fit.millstones) { const x = bx + main.x + (main.door || 2) + 3, y = y0 + S.H; P.put(x, y, "#b4b4ba"); P.put(x + 1, y, "#9a9aa0"); P.put(x, y - 1, "#9a9aa0"); P.put(x + 1, y - 1, "#b4b4ba"); }
    const rx = bx + S.w - S.left - S.right + 1;
    if (fit.anvil) { const x = rx + 1, y = y0 + S.H - 3, hot = ["smelt", "copper tool", "coin"].some((t) => made.has(t));
      P.put(x, y, "#3a3a42"); P.put(x + 1, y, "#3a3a42"); P.put(x + 2, y, "#4a4a52"); P.put(x + 1, y + 1, "#2a2a32"); P.put(x + 1, y + 2, "#5a3a20"); if (hot) { P.put(x + 1, y - 1, "#f08a3a"); P.put(x + 3, y - 2, "#f0c060"); P.put(x - 1, y - 2, "#f0c060"); } }
    else if (fit.oven) { const x = rx, y = y0 + S.H - Math.round(5 * k), on = made.has("oven bread");
      for (let dy = 0; dy < 5; dy++) for (let dx = 0; dx < 7; dx++) { const r = Math.hypot(dx - 3, (dy - 4) * 1.4); if (r > 3.6) continue; P.put(x + dx, y + dy, r > 2.8 ? "#9a5a3a" : dy < 2 ? "#c8805a" : "#b06a48"); }
      P.put(x + 3, y + 4, on ? "#f08a3a" : "#2a1a10"); if (on) smoke(P, x + 3, y - 1); }
    const wood = ((b.stock || {}).timber || 0) + ((b.stock || {}).firewood || 0);
    if (wood > 0.5 && k >= 0.8) { const n = Math.min(14, Math.max(2, Math.round(Math.log2(1 + wood) * 3))), x = bx + S.parts[S.parts.length - 1].x + S.parts[S.parts.length - 1].w + 1, y = y0 + S.H - 1;
      for (let q = 0; q < n; q++) { const xx = x + (q % 5), yy = y - Math.floor(q / 5); P.put(xx, yy, q % 3 === 0 ? "#c09060" : q % 2 ? "#8a5a2a" : "#a0703a"); } }
    return S;
  }
  function campOf(P, x, y, fire, k, nightsLeft) {
    const n = Math.max(5, Math.round(9 * k)), sag = nightsLeft != null && nightsLeft <= 2 ? 1 : 0;
    for (let q = 0; q < n; q++) for (let j = 0; j <= q; j++) { if (j > q * 0.9) continue; P.put(x + j, y + q + sag, (j + q) % 3 ? "#7a6a3a" : "#5c7a34"); }
    for (let q = 0; q < n + 1; q++) P.put(x + q, y + q - 1, "#5a3a20");
    const fx = x + n + 3, fy = y + n - 2; for (const [a, c] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-2, 0], [2, 0]]) P.put(fx + a, fy + c, "#8a8a8a");
    if (fire) { P.put(fx, fy, "#f08a3a"); P.put(fx, fy - 1, "#f0c060"); smoke(P, fx, fy - 3); } else P.put(fx, fy, "#3a2a1a");
  }
  // a beast close up, by its role in the herd (farm.py ROLES: cows, oxen, bulls, young); hungry ones show their ribs
  function beast(P, x, y, role, R, hungry) {
    x |= 0; y |= 0;
    const put = (pts, c) => { for (const [dx, dy] of pts) P.put(x + dx, y + dy, c); };
    if (role === "young") {
      for (let dx = 0; dx < 4; dx++) P.dark(x + dx + 1, y + 1, .25);
      put([[0, -1], [1, -1], [2, -1], [0, -2], [1, -2], [2, -2]], "#d8b88a"); put([[3, -2], [3, -3]], "#d8b88a"); put([[0, 0], [2, 0]], "#6b4423"); return;
    }
    const body = role === "oxen" ? "#a0663a" : role === "bulls" ? "#4a3428" : (R() < 0.35 ? "#b8794a" : "#f4efe6"), spot = body === "#f4efe6" ? "#2a2420" : "#6b4423";
    const L = role === "oxen" || role === "bulls" ? 6 : 5;
    for (let dx = 0; dx < L + 2; dx++) P.dark(x + dx + 1, y + 1, .28);
    for (let dx = 0; dx < L; dx++) for (let dy = -3; dy < 0; dy++) P.put(x + dx, y + dy, body);
    for (let dx = 0; dx < L; dx++) P.dark(x + dx, y - 1, .12);
    if (role === "cows" && body === "#f4efe6") { P.put(x + 1 + ((R() * 2) | 0), y - 3, spot); P.put(x + 3, y - 2, spot); }
    if (hungry) for (let dx = 1; dx < L - 1; dx += 2) P.dark(x + dx, y - 2, .3);
    put([[L, -4], [L, -3], [L + 1, -3]], body); P.dark(x + L + 1, y - 3, .2);
    if (role !== "cows") { P.put(x + L - 1, y - 5, "#e8e0d0"); P.put(x + L + 1, y - 5, "#e8e0d0"); } else P.put(x + L - 1, y - 4, "#e8e0d0");
    put([[0, 0], [1, 0], [L - 2, 0], [L - 1, 0]], "#4a2f17");
    if (role === "cows") P.put(x + 2, y, "#f0b0a8");                                                   // the udder
  }
  Object.assign(X, { SPACE, hsh, ROOFS, WALLS, FORMS, styleOf, shape, box, roof, frameOf, smoke, drawBuilding, campOf, beast });
})(C2X);
