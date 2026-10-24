// c2viz pixel renderer: the cybertron2 world as a pixel-art map, in the look of the site's night-village design (wp/site-v2:
// site/assets/scene.js: the low-resolution canvas, value noise, the palette, trees, houses, terraces with cliff faces; the
// villagers' colours from site/assets/core/villagers.js). Everything is drawn from the run's data for one day:
//
//   C2Pixel.world(canvas, viz, day, opts)       the region: places in a landscape made from their parcels, roads between them,
//                                               travellers on the roads, fog over unexplored places
//   C2Pixel.node(canvas, viz, nodeId, day, opts) one place: its parcels as land (cover, height, crops, fences, resources), its
//                                               buildings (structure, condition, fire, fittings), herds, things lying about,
//                                               people where they worked with what they did, roads leaving the map
//
// Both return { width, height, hotspots: [{kind, id, x, y, w, h, label}] } in canvas pixels, so a page can label and click.
// Show the canvas scaled up with `image-rendering: pixelated`. The same data always gives the same picture.
(function (G) {
  "use strict";
  // ---------------------------------------------------------------------------------------------------- the toolkit (scene.js)
  function rng(s) { return function () { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function hstr(s) { let h = 2166136261; for (const c of String(s)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }
  function noise(seed) {
    const H = (x, y) => { let h = (seed ^ Math.imul(x, 374761393) ^ Math.imul(y, 668265263)) | 0; h = Math.imul(h ^ h >>> 13, 1274126177); return ((h ^ h >>> 16) >>> 0) / 4294967296; };
    const sm = (t) => t * t * (3 - 2 * t);
    const v = (x, y) => { const ix = Math.floor(x), iy = Math.floor(y), fx = sm(x - ix), fy = sm(y - iy); const a = H(ix, iy), b = H(ix + 1, iy), c = H(ix, iy + 1), d = H(ix + 1, iy + 1); return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy; };
    return (x, y, o = 4) => { let s = 0, a = 1, f = 1, n = 0; for (let i = 0; i < o; i++) { s += v(x * f + i * 17.3, y * f + i * 9.1) * a; n += a; a *= 0.5; f *= 2; } return s / n; };
  }
  const C = (h) => parseInt(h.slice(1), 16);
  function Px(cv, W, H, bg) {
    cv.width = W; cv.height = H;
    const g = cv.getContext("2d"), img = g.createImageData(W, H), d = img.data, buf = new Uint32Array(W * H).fill(bg ? C(bg) : 0);
    const put = (x, y, c) => { x |= 0; y |= 0; if (x >= 0 && y >= 0 && x < W && y < H) buf[y * W + x] = typeof c === "string" ? C(c) : c; };
    const get = (x, y) => buf[(y | 0) * W + (x | 0)];
    const shade = (x, y, t) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const c = buf[y * W + x];
      const f = (v) => Math.max(0, Math.min(255, Math.round(t >= 0 ? v * (1 - t) : v + (255 - v) * -t)));
      buf[y * W + x] = (f(c >> 16 & 255) << 16) | (f(c >> 8 & 255) << 8) | f(c & 255); };
    const mix = (x, y, col, t) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const a = buf[y * W + x], b = typeof col === "string" ? C(col) : col;
      const m = (s) => Math.round((a >> s & 255) * (1 - t) + (b >> s & 255) * t); buf[y * W + x] = (m(16) << 16) | (m(8) << 8) | m(0); };
    const flush = () => { for (let i = 0; i < W * H; i++) { const c = buf[i]; d[i * 4] = c >> 16 & 255; d[i * 4 + 1] = c >> 8 & 255; d[i * 4 + 2] = c & 255; d[i * 4 + 3] = 255; } g.putImageData(img, 0, 0); };
    return { put, get, dark: (x, y, t) => shade(x, y, t), light: (x, y, t) => shade(x, y, -t), mix, flush, W, H };
  }
  function tree(P, x, y, r, R, cols) {
    cols = cols || ["#2f7d3a", "#3a8a3e", "#286e34"]; const c = cols[(R() * cols.length) | 0];
    for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (dx * dx + dy * dy <= r * r + 0.5) P.dark(x + dx + 1, y + dy + 1, 0.35);
    for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) { if (dx * dx + dy * dy > r * r + 0.5) continue; P.put(x + dx, y + dy, dx + dy < -r + 0.5 ? "#58a648" : dx + dy > r - 0.5 ? "#1f5a2a" : c); }
  }

  // ---------------------------------------------------------------------------------------------------- the palette
  const PAL = {
    grass: [["#8cc04c", "#9cd05a", "#7cb042"], ["#7cb444", "#8cc452", "#6ca43a"], ["#6ca63c", "#7cb64a", "#5c9632"], ["#5f9a36", "#6fac44", "#528a2c"]],
    water: { deep: "#4e94a8", deep2: "#5aa2b4", shore: "#7cc0c8", foam: "#d8f0f0" },
    face: ["#e6e2d6", "#d2ccbc", "#bdb5a2", "#a69c88"], rim: "#b0dc6a", rimShade: "#5a9030",
    road: "#d8b47a", lane: "#e2c896", ramp: "#ece6d6", ground: ["#d8c48e", "#c8b07a", "#ccb684"], hedge: "#4f8a34",
    soil: ["#9a6e46", "#b8865a", "#a87a50"], stubble: ["#dccb8a", "#cdb878"], sprout: ["#9a7a50", "#7cb444"],
    growing: ["#a8d050", "#8cb83e"], ripe: ["#e8c840", "#d4ac30"], failed: ["#a89c84", "#8f846e"],
    scrub: ["#9aa45a", "#8a9450", "#a8ae66"], bush: ["#5c7a34", "#4e6a2c"], rock: ["#a8a49a", "#bcb8ae", "#948f84"],
    meadowFlower: ["#ffffff", "#f6e27a", "#f2a0c0", "#c8b8f0"], fenceWood: ["#6b4423", "#8a5a2a"], fenceStone: ["#8a8a92", "#b4b4ba"],
    copper: "#5ab09a", fog: "#1b2444",
  };
  const ROOF = { timber: ["#c8553d", "#e07a5a", "#9a3a24"], stone: ["#7a7a86", "#9a9aa6", "#55555f"], wattle: ["#c8a050", "#e0bc68", "#9a7838"],
    camp: ["#a07a4a", "#c09a62", "#7a5a32"] };
  const WALL = { timber: "#f2e8d4", stone: "#d6d0c4", wattle: "#e8d4a8", camp: "#cdb48a" };
  // villagers' colours (site/assets/core/villagers.js)
  const HAIR = ["#2a1a10", "#7a4a24", "#c8553d", "#e8c060", "#4a2a5a", "#d8d0c0", "#a0662f", "#5a3a1c"];
  const SKIN = ["#f8dcc0", "#f6c99f", "#e0a878", "#c8906a", "#9a6a4a", "#6a4a32"];
  const CLOTHES = ["#6a9a3a", "#4878c8", "#c8553d", "#7a5aa0", "#e8a33c", "#3a8a8a", "#a0662f", "#d07aa0", "#8a9a3a"];
  const TROUSERS = ["#5a4a3a", "#3a3a4a", "#4a5a8a", "#6a5a4a"];
  const looks = (name) => { const h = hstr(name); return { hair: HAIR[h % 8], skin: SKIN[(h >>> 3) % 6], clothes: CLOTHES[(h >>> 6) % 9], trousers: TROUSERS[(h >>> 10) % 4] }; };

  // ---------------------------------------------------------------------------------------------------- small sprites
  // a person 3 wide and 6 tall (a child 3 x 4), from the villager palette; facing a tool held to one side
  function person(P, x, y, name, o = {}) {
    const L = looks(name); x |= 0; y |= 0;
    if (o.dead) { // a body on the ground
      P.put(x - 1, y, "#d8d2c4"); P.put(x, y, "#d8d2c4"); P.put(x + 1, y, "#d8d2c4"); P.put(x + 2, y, L.skin); P.dark(x - 1, y + 1, .3); P.dark(x, y + 1, .3); P.dark(x + 1, y + 1, .3); return;
    }
    if (o.child) { P.put(x, y - 3, L.hair); P.put(x + 1, y - 3, L.hair); P.put(x, y - 2, L.skin); P.put(x + 1, y - 2, L.skin); P.put(x, y - 1, L.clothes); P.put(x + 1, y - 1, L.clothes); P.put(x, y, L.trousers); P.put(x + 1, y, L.trousers); P.dark(x + 2, y, .3); return; }
    for (const [dx, dy, c] of [[0, -5, L.hair], [1, -5, L.hair], [-1, -4, L.hair], [0, -4, L.skin], [1, -4, L.skin], [0, -3, L.clothes], [1, -3, L.clothes],
      [-1, -3, L.skin], [2, -3, L.skin], [0, -2, L.clothes], [1, -2, L.clothes], [0, -1, L.trousers], [1, -1, L.trousers], [0, 0, "#4a2f17"], [1, 0, "#4a2f17"]]) P.put(x + dx, y + dy, c);
    P.dark(x + 2, y, .35); P.dark(x + 2, y - 1, .25);
    if (o.hungry) P.put(x + 1, y - 6, o.hungry > 1 ? "#e85a5a" : "#f0c060");
    if (o.tool) tool(P, x + 3, y - 3, o.tool);
  }
  // what one is doing, as a tool held out: a few pixels each
  const TOOLS = {
    fell: [[0, 0, "#8a5a2a"], [0, 1, "#8a5a2a"], [0, 2, "#8a5a2a"], [1, 0, "#c8c8d0"], [1, -1, "#c8c8d0"]],                       // an axe
    reap: [[0, 1, "#8a5a2a"], [0, 2, "#8a5a2a"], [0, 0, "#c8c8d0"], [1, -1, "#c8c8d0"], [2, -1, "#c8c8d0"]],                       // a sickle
    forage: [[0, 1, "#a0662f"], [1, 1, "#a0662f"], [0, 0, "#c8553d"], [1, 0, "#7ab04a"]],                                         // a basket
    hunt: [[0, -1, "#8a5a2a"], [0, 0, "#8a5a2a"], [0, 1, "#8a5a2a"], [1, -2, "#c8c8d0"]],                                          // a spear
    mine: [[0, 0, "#8a5a2a"], [0, 1, "#8a5a2a"], [-1, -1, "#9aa0a8"], [0, -1, "#9aa0a8"], [1, -1, "#9aa0a8"]],                     // a pick
    milk: [[0, 0, "#c8c8d0"], [1, 0, "#c8c8d0"], [0, 1, "#9aa0a8"], [1, 1, "#9aa0a8"]],                                            // a pail
    dig: [[0, -1, "#8a5a2a"], [0, 0, "#8a5a2a"], [0, 1, "#9aa0a8"], [1, 1, "#9aa0a8"]],                                            // a spade
    make: [[0, 0, "#8a5a2a"], [0, 1, "#8a5a2a"], [-1, -1, "#6a6a72"], [0, -1, "#6a6a72"], [1, -1, "#6a6a72"]],                     // a hammer
    herd: [[0, -2, "#8a5a2a"], [0, -1, "#8a5a2a"], [0, 0, "#8a5a2a"], [0, 1, "#8a5a2a"], [1, -2, "#8a5a2a"]],                      // a crook
    sow: [[0, 0, "#c8a46a"], [1, 0, "#c8a46a"], [1, 1, "#9a7a50"]],                                                                // a seed bag
    carry: [[0, 0, "#c9b38a"], [1, 0, "#c9b38a"], [0, 1, "#a8946a"], [1, 1, "#a8946a"]],                                           // a sack
    speak: [[0, -3, "#ffffff"], [1, -3, "#ffffff"], [2, -3, "#ffffff"], [0, -2, "#ffffff"], [1, -2, "#ffffff"], [2, -2, "#ffffff"], [0, -1, "#ffffff"]],
  };
  const TECH_TOOL = { fell: "fell", reap: "reap", forage: "forage", hay: "reap", hunt: "hunt", mine: "mine", quarry: "mine", milk: "milk",
    ditch: "dig", bury: "dig", fence: "make", wall: "make", herd: "herd", sow: "sow", dibble: "sow", plough: "dig", hoe: "dig", weed: "dig",
    dung: "carry", smelt: "make", charcoal: "make", coin: "make" };
  function toolFor(a) { if (!a) return null; return TECH_TOOL[a.tech] || (a.verb === "make" || a.verb === "build" ? "make" : a.verb === "gather" ? "forage" : a.verb === "work" ? "dig" : a.verb === "give" || a.verb === "take" ? "carry" : null); }
  function tool(P, x, y, k) { for (const [dx, dy, c] of TOOLS[k] || []) P.put(x + dx, y + dy, c); }
  function cow(P, x, y, R, kind) {
    const body = kind === "oxen" || R() < 0.3 ? "#a0663a" : "#f4efe6", spot = body === "#f4efe6" ? "#2a2420" : "#6b4423";
    for (let dx = 0; dx < 4; dx++) for (let dy = 0; dy < 2; dy++) P.put(x + dx, y + dy, (dx === 1 && dy === 0 && R() < .7) ? spot : body);
    P.put(x + 4, y - 1, body); P.put(x + 4, y, body); P.put(x, y + 2, "#4a2f17"); P.put(x + 3, y + 2, "#4a2f17"); P.dark(x + 4, y + 2, .3); P.dark(x + 1, y + 2, .25);
  }
  function grave(P, x, y) { P.put(x, y - 2, "#c8c4bc"); P.put(x - 1, y - 1, "#c8c4bc"); P.put(x, y - 1, "#c8c4bc"); P.put(x + 1, y - 1, "#c8c4bc"); P.put(x, y, "#a8a29a"); P.put(x - 1, y + 1, "#7a5a3a"); P.put(x, y + 1, "#7a5a3a"); P.put(x + 1, y + 1, "#7a5a3a"); }
  function sack(P, x, y) { P.put(x, y - 1, "#a8946a"); P.put(x - 1, y, "#c9b38a"); P.put(x, y, "#c9b38a"); P.put(x + 1, y, "#b8a278"); P.dark(x + 2, y, .3); }
  function bones(P, x, y) { P.put(x - 1, y, "#f0ece0"); P.put(x, y, "#f0ece0"); P.put(x + 1, y, "#f0ece0"); P.put(x, y - 1, "#e0dccc"); }

  // a building: walls and roof by structure, its fittings, smoke when the fire is lit, the damage, the frame of one being built
  function building(P, x0, y0, w, h, b, R) {
    const st = b.structure || "timber", roof = ROOF[st] || ROOF.timber, wall = WALL[st] || WALL.timber;
    for (let y = y0 + 1; y <= y0 + h; y++) P.dark(x0 + w, y, 0.38);
    for (let x = x0 + 1; x <= x0 + w; x++) P.dark(x, y0 + h, 0.38);
    if (b.unfinished) {
      for (let x = x0; x < x0 + w; x++) { P.put(x, y0 + h - 1, "#8a5a2a"); if (x % 2 === 0) P.put(x, y0 + h - 3, "#a0662f"); }
      for (let y = y0 + 1; y < y0 + h; y++) { P.put(x0, y, "#8a5a2a"); P.put(x0 + w - 1, y, "#8a5a2a"); }
      return;
    }
    if (st === "camp") {
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (Math.abs(x - (w - 1) / 2) <= y * w / (2 * h) + 0.3) P.put(x0 + x, y0 + y, x < w / 2 ? roof[1] : roof[0]);
      P.put(x0 + (w >> 1), y0 + h - 1, "#3a2414"); P.put(x0 + w + 1, y0 + h - 1, "#e8803a"); P.put(x0 + w + 1, y0 + h - 2, "#f0c060");
      return;
    }
    const wy = h - 2 - (h > 7 ? 1 : 0);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      let c;
      if (st === "wattle" && y < wy && Math.abs(x - (w - 1) / 2) > (y + 1.5) * w / (2 * wy)) continue;     // a round thatch
      if (y === 0) c = roof[2]; else if (y < wy) c = x === 0 ? roof[1] : roof[0]; else c = x === 0 ? "#d8ccb4" : wall;
      if (st === "stone" && y >= wy && (x + y) % 3 === 0) c = "#c4beb2";
      if (y === wy && (x === 1 || x === w - 2) && w > 4) c = "#7aaabe";
      if (y === h - 1 && x === (w >> 1)) c = b.door === "open" ? "#2a1a10" : "#6b4423";
      P.put(x0 + x, y0 + y, c);
    }
    const fit = b.fittings || {};
    if (fit["water wheel"]) { const cx = x0 - 3, cy = y0 + h - 3; for (let a = 0; a < 8; a++) P.put(cx + Math.round(2 * Math.cos(a * .785)), cy + Math.round(2 * Math.sin(a * .785)), "#8a5a2a"); P.put(cx, cy, "#6b4423"); }
    if (fit.anvil) { P.put(x0 + w - 2, y0 - 1, "#4a4a52"); P.put(x0 + w - 2, y0 - 2, "#4a4a52"); P.put(x0 + w - 1, y0 + h - 2, "#f08a3a"); }
    if (fit.oven) { P.put(x0 + w, y0 + h - 2, "#9a6b47"); P.put(x0 + w + 1, y0 + h - 2, "#9a6b47"); P.put(x0 + w, y0 + h - 1, "#7a4b2f"); P.put(x0 + w + 1, y0 + h - 1, "#7a4b2f"); }
    if (fit.granary) { P.put(x0 - 2, y0 + h - 4, "#c8a050"); P.put(x0 - 3, y0 + h - 4, "#c8a050"); P.put(x0 - 2, y0 + h - 3, "#8a5a2a"); P.put(x0 - 3, y0 + h - 1, "#8a5a2a"); P.put(x0 - 2, y0 + h - 1, "#8a5a2a"); }
    if (fit.millstones && !fit["water wheel"]) { P.put(x0 - 2, y0 + h - 2, "#9a9aa0"); P.put(x0 - 3, y0 + h - 2, "#9a9aa0"); }
    if (b.fire) { const sx = x0 + w - 2; P.put(sx, y0 - 1, "#6a6a72"); P.put(sx, y0 - 3, "#d8d8d8"); P.put(sx + 1, y0 - 4, "#e8e8e8"); P.put(sx, y0 - 5, "#f0f0f0"); P.put(sx + 1, y0 - 7, "#f4f4f4"); }
    if (b.condition === 1) for (let k = 0; k < Math.max(2, w >> 1); k++) P.put(x0 + 1 + ((R() * (w - 2)) | 0), y0 + 1 + ((R() * Math.max(1, wy - 1)) | 0), "#2a1a10");
    if (b.condition === 0) { for (let x = x0; x < x0 + w; x++) for (let y = y0; y < y0 + wy; y++) P.put(x, y, R() < 0.5 ? "#5a4a3a" : P.get(x, y + wy) ); for (let k = 0; k < w; k++) P.put(x0 - 1 + ((R() * (w + 2)) | 0), y0 + h + ((R() * 2) | 0), "#8a8478"); }
  }
  function dims(b) {
    const s = Math.max(2, +b.size || 4), st = b.structure || "timber";
    if (st === "camp") return [5, 4];
    const w = Math.max(5, Math.min(13, Math.round(4 + Math.sqrt(s) * 2))), h = Math.max(5, Math.min(10, Math.round(3 + Math.sqrt(s) * 1.4)));
    return st === "wattle" ? [Math.max(5, w - 1), Math.max(5, h - 1)] : [w, h];
  }

  // ---------------------------------------------------------------------------------------------------- shared reading of a day
  const D = (V, day) => V.days[Math.max(0, Math.min(V.days.length - 1, day))];
  const crops = (c, day) => !c ? null : c.failed ? "failed" : c.ripe ? "ripe" : (day - (c.sown ?? day)) <= 1 ? "sprout" : "growing";

  // ---------------------------------------------------------------------------------------------------- one place
  function node(cv, V, nid, day, opts = {}) {
    const W = opts.width || 256, H = opts.height || 160, d = D(V, day), ST = V.static, Lyt = ST.layout.nodes[nid];
    const seed = hstr((V.meta.seed ?? 1) + "|" + nid), R = rng(seed), n1 = noise(seed ^ 1), n2 = noise(seed ^ 2), n3 = noise(seed ^ 3);
    const P = Px(cv, W, H, "#6ca63c"), out = { width: W, height: H, hotspots: [] };
    const sx = W / 1000, sy = H / 700;
    const pids = Object.keys(Lyt.centre).sort();
    const site = pids.map((p) => [Lyt.centre[p][0] * sx, Lyt.centre[p][1] * sy]);
    const wt = pids.map((p) => Math.sqrt(+ST.parcels[p].size || 1) * 26);
    // the place's edge: its outline from the layout, roughened; outside it the wild country around
    const ol = Lyt.outline.map(([x, y]) => [x * sx, y * sy]);
    const inside = (x, y) => { let c = false; for (let i = 0, j = ol.length - 1; i < ol.length; j = i++) { const [xi, yi] = ol[i], [xj, yj] = ol[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / ((yj - yi) || 1e-9) + xi) c = !c; } return c; };
    const REG = new Int16Array(W * H).fill(-1), LV = new Int8Array(W * H), occ = new Uint8Array(W * H);
    const reg = (x, y) => (x < 0 || y < 0 || x >= W || y >= H) ? -2 : REG[(y | 0) * W + (x | 0)];
    const lv = (x, y) => (x < 0 || y < 0 || x >= W || y >= H) ? -1 : LV[(y | 0) * W + (x | 0)];
    const cov = (i) => i < 0 ? "wild" : ST.parcels[pids[i]].cover;
    const level = (i) => { if (i < 0) return 1; const p = ST.parcels[pids[i]]; return p.cover === "water" ? 0 : Math.max(1, Math.min(3, (p.height ?? 1))); };
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const jx = x + (n1(x / 11, y / 11, 3) - 0.5) * 18, jy = y + (n1(x / 11 + 40, y / 11, 3) - 0.5) * 18;
      let k = -1;
      if (inside(jx, jy)) { let best = 1e18; for (let i = 0; i < site.length; i++) { const v = (jx - site[i][0]) ** 2 + (jy - site[i][1]) ** 2 - wt[i] * wt[i]; if (v < best) { best = v; k = i; } } }
      REG[y * W + x] = k; LV[y * W + x] = k < 0 ? 1 + (n2(x / 60, y / 60, 3) > 0.68 ? 1 : 0) : level(k);
    }
    // the wild country: woodland and rough grass by the place's own covers
    const share = {}; let tot = 0;
    for (const p of pids) { const c = ST.parcels[p].cover; share[c] = (share[c] || 0) + (+ST.parcels[p].size || 1); tot += +ST.parcels[p].size || 1; }
    const wildWood = Math.min(0.75, 0.3 + (share.forest || 0) / (tot || 1));
    // ground
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const i = REG[y * W + x], c = cov(i), l = LV[y * W + x], v = n3(x / 3, y / 3, 2);
      let col;
      if (c === "water") { let shore = false; for (const [a, b] of [[2, 0], [-2, 0], [0, 2], [0, -2], [1, 1], [-1, -1]]) if (lv(x + a, y + b) > 0) shore = true;
        col = shore ? (n3(x / 2, y / 2, 1) > 0.6 ? PAL.water.foam : PAL.water.shore) : (n3(x / 6, y / 3, 2) > 0.6 ? PAL.water.deep2 : PAL.water.deep); }
      else if (c === "built") col = PAL.grass[Math.min(3, l)][v > 0.62 ? 1 : v < 0.36 ? 2 : 0];
      else if (c === "rock") col = PAL.rock[v > 0.7 ? 1 : v < 0.3 ? 2 : 0];
      else if (c === "scrub") col = v < 0.3 ? PAL.scrub[1] : PAL.grass[Math.min(3, l)][v > 0.62 ? 2 : 0];
      else col = PAL.grass[Math.min(3, l)][v > 0.62 ? 1 : v < 0.36 ? 2 : 0];
      P.put(x, y, col);
      if (i < 0) P.dark(x, y, 0.12 + 0.1 * (n2(x / 20, y / 20) > .5));                                        // the wild, a little darker
    }
    // terraces: a lip and a cliff face where the ground steps down to the south (scene.js)
    for (let y = 0; y < H - 1; y++) for (let x = 0; x < W; x++) {
      const l = LV[y * W + x]; if (l <= 0) continue;
      if (lv(x, y + 1) < l && lv(x, y + 1) > 0) { P.put(x, y, PAL.rim); for (let k = 1; k <= 3; k++) { if (lv(x, y + k) >= l || y + k >= H) break; P.put(x, y + k, PAL.face[Math.min(3, k - 1 + (x % 3 === 0 ? 1 : 0))]); } }
      else if ((lv(x + 1, y) < l || lv(x - 1, y) < l) && lv(x + 1, y) > 0 && lv(x - 1, y) > 0) P.put(x, y, PAL.rimShade);
    }
    // each parcel's surface
    const area = pids.map(() => []);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const i = REG[y * W + x]; if (i >= 0) area[i].push([x, y]); }
    const bbox = area.map((a) => a.length ? a.reduce((b, [x, y]) => [Math.min(b[0], x), Math.min(b[1], y), Math.max(b[2], x), Math.max(b[3], y)], [1e9, 1e9, -1, -1]) : null);
    const border = (x, y, i) => reg(x + 1, y) !== i || reg(x - 1, y) !== i || reg(x, y + 1) !== i || reg(x, y - 1) !== i;
    const trees = [];
    pids.forEach((pid, i) => {
      const P0 = ST.parcels[pid], dp = d.parcels[pid] || {}, c = P0.cover, res = dp.res || {};
      if (c === "field") {
        const st = crops(dp.crop, day), bb = bbox[i], along = (hstr(pid) & 1) === 1, left = dp.crop ? (dp.crop.left ?? 1) : 1;
        const span = bb ? (along ? bb[2] - bb[0] : bb[3] - bb[1]) : 1;
        for (const [x, y] of area[i]) {
          if (border(x, y, i)) { if (n3(x / 2 + 9, y / 2) < 0.7) P.put(x, y, PAL.hedge); continue; }
          if (LV[y * W + x] !== level(i)) continue;
          const u = along ? x - bb[0] : y - bb[1], row = (along ? y : x) % 2;
          let pal = st === "ripe" ? PAL.ripe : st === "growing" ? PAL.growing : st === "failed" ? PAL.failed : st === "sprout" ? PAL.sprout : PAL.soil;
          if (st && u > span * left) pal = PAL.stubble;                                    // the part already reaped
          P.put(x, y, pal[row]);
        }
      } else if (c === "pasture" || c === "meadow") {
        for (const [x, y] of area[i]) { const v = n3(x * 1.3, y * 1.3, 1);
          if (c === "meadow" && v > 0.86) P.put(x, y, PAL.meadowFlower[(hstr(x + "," + y) >>> 3) % 4]);
          else if (v > 0.8) P.put(x, y, "#5a8a2e");
          if (res.grass != null && res.grass < 0.35 && n3(x / 3 + 5, y / 3) < 0.6 - res.grass) P.mix(x, y, "#b8a868", 0.55); }   // grazed bare
      } else if (c === "forest") {
        // trees by what is left of this wood's own timber since day 1; a stand that never had timber (a thin willow holt) stays thin
        const w0 = ((V.days[0].parcels[pid] || {}).res || {}).wood, wood = w0 > 0.05 ? Math.min(1, (res.wood ?? w0) / w0) * Math.min(1, 0.4 + w0) : 0.35;
        const fR = rng(hstr(pid));
        for (const [x, y] of area[i]) if (x % 3 === 0 && y % 3 === 0) { const tx = x + fR() * 2, ty = y + fR() * 2;
          if (n2(tx / 7, ty / 7) < 0.15 + 0.85 * wood) trees.push([tx, ty, fR() < 0.6 ? 2 : 2.6]); else { P.put(tx, ty, "#8a6a42"); P.put(tx + 1, ty, "#6b4423"); } }   // a stump where it was felled
        if (res.plants != null && res.plants > 0.5) for (const [x, y] of area[i]) if (n3(x * 2.1, y * 2.1, 1) > 0.97) P.put(x, y, "#c8553d");   // berries
      } else if (c === "scrub") {
        for (const [x, y] of area[i]) if (n3(x * 1.7, y * 1.7, 1) > 0.86) { P.put(x, y, PAL.bush[0]); P.put(x + 1, y, PAL.bush[1]); P.dark(x + 1, y + 1, .3); }
      } else if (c === "rock") {
        const rR = rng(hstr(pid + "rocks"));
        for (const [x, y] of area[i]) { if (x % 5 || y % 4 || rR() > 0.35) continue; const bx = x + (rR() * 3 | 0), by = y + (rR() * 2 | 0);   // boulders (scene.js)
          for (let dy = 0; dy < 2; dy++) for (let dx = 0; dx < 3; dx++) P.put(bx + dx, by + dy, dx + dy === 0 ? "#e8e8e0" : dx + dy >= 3 ? "#9a9a92" : "#c8c8c0"); P.dark(bx + 3, by + 1, .3); P.dark(bx + 1, by + 2, .3); }
        if (res.seam != null) for (const [x, y] of area[i]) if (n2(x / 3, y / 3) > 0.78 - 0.2 * res.seam) P.put(x, y, PAL.copper);
        if (res.quarry != null) { const [x0, y0] = [((bbox[i][0] + bbox[i][2]) / 2) | 0, ((bbox[i][1] + bbox[i][3]) / 2) | 0]; for (let a = 0; a < 7; a++) for (let b = 0; b < 3; b++) P.put(x0 + a, y0 + b, b === 0 ? "#f0eee6" : "#a8a49a"); }
      } else if (c === "water") {
        for (const [x, y] of area[i]) if (n3(x / 2 + 3, y, 1) > 0.97) P.put(x, y, PAL.water.foam);
      }
      if (dp.fence && dp.fence.built !== false) {                                              // a fence or wall round it
        const col = dp.fence.kind === "stone" ? PAL.fenceStone : PAL.fenceWood, gap = dp.fence.level === 1 ? 5 : 1e9;
        let k = 0; for (const [x, y] of area[i]) if (border(x, y, i) && reg(x, y + 1) !== -2) { k++; if (dp.fence.level === 0 || k % gap === 0) continue; P.put(x, y, col[(x + y) & 1]); }
      }
    });
    // the wild country's trees
    for (let gy = 0; gy < H; gy += 3) for (let gx = 0; gx < W; gx += 3) { const x = gx + R() * 2, y = gy + R() * 2; if (reg(x, y) !== -1) continue; if (n2(x / 26, y / 26, 3) < 1 - wildWood) continue; trees.push([x, y, R() < 0.6 ? 2 : 2.6]); }
    // roads leaving the place: from their parcel to the edge, winding (scene.js road)
    const paint = (x, y, col) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; if (LV[y * W + x] === 0) { P.put(x, y, "#a0662f"); occ[y * W + x] = 3; return; } P.put(x, y, col); occ[y * W + x] = 3; };
    const road = (x, y, tx, ty, wide, col) => {
      let hd = Math.atan2(ty - y, tx - x);
      for (let s = 0; s < 900; s++) {
        if (Math.hypot(tx - x, ty - y) < 1.5 || x < 0 || y < 0 || x >= W || y >= H) break;
        let dd = Math.atan2(ty - y, tx - x) - hd; dd = Math.atan2(Math.sin(dd), Math.cos(dd));
        hd += Math.max(-0.09, Math.min(0.09, dd)) + (n2(x / 14 + 40, y / 14) - 0.5) * 0.14;
        x += Math.cos(hd); y += Math.sin(hd);
        paint(x, y, col); if (wide) { paint(x + 1, y, col); paint(x, y + 1, col); paint(x + 1, y + 1, col); }
      }
    };
    for (const [rid, ex] of Object.entries(Lyt.exits || {})) {
      const from = ex.parcels.length ? Lyt.centre[ex.parcels[0]] : [500, 350], [dx, dy] = ex.dir;
      const fx = from[0] * sx, fy = from[1] * sy, tx = Math.max(-2, Math.min(W + 2, W / 2 + dx * W * 0.62)), ty = Math.max(-2, Math.min(H + 2, H / 2 + dy * H * 0.62));
      const r = ST.roads[rid];
      road(fx, fy, tx, ty, !r || !r.track, ex.hidden ? PAL.lane : PAL.road);
      const lx = Math.max(6, Math.min(W - 6, tx)), ly = Math.max(6, Math.min(H - 6, ty));
      out.hotspots.push({ kind: "exit", id: rid, to: ex.to, x: lx - 6, y: ly - 6, w: 12, h: 12, label: "→ " + (ST.nodes[ex.to]?.name || ex.to) + " · " + (r?.days ?? "?") + " day" + ((r?.days ?? 1) > 1 ? "s" : "") });
    }
    // buildings: on their parcel, nearest its middle first (scene.js place), with a lane to the road
    const centreOf = (i) => { const a = area[i]; if (!a.length) return [W / 2, H / 2]; let sxx = 0, syy = 0; for (const [x, y] of a) { sxx += x; syy += y; } return [sxx / a.length, syy / a.length]; };
    const free = (x0, y0, w, h, i) => { for (let y = y0 - 1; y < y0 + h + 1; y++) for (let x = x0 - 1; x < x0 + w + 1; x++) { if (reg(x, y) !== i || occ[y * W + x]) return false; if (lv(x, y + 2) !== lv(x0, y0 + h - 1)) return false; } return true; };
    const bpos = {};
    const bs = Object.entries(d.buildings).filter(([, b]) => b.node === nid).sort((a, b) => (b[1].size || 0) - (a[1].size || 0) || (a[0] < b[0] ? -1 : 1));
    for (const [bid, b] of bs) {
      const i = pids.indexOf(b.parcel); const [w, h] = dims(b); const [cx, cy] = centreOf(Math.max(0, i));
      const bR = rng(hstr(bid)); let spot = null;
      for (let r = 0; r < 60 && !spot; r += 1.5) for (let t = 0; t < 24; t++) { const a = bR() * 6.283, x0 = (cx + Math.cos(a) * r * 1.3 - w / 2) | 0, y0 = (cy + Math.sin(a) * r - h / 2) | 0; if (free(x0, y0, w, h, i)) { spot = [x0, y0]; break; } }
      if (!spot) spot = [(cx - w / 2) | 0, (cy - h / 2) | 0];
      for (let y = spot[1] - 1; y < spot[1] + h + 1; y++) for (let x = spot[0] - 1; x < spot[0] + w + 1; x++) if (x >= 0 && y >= 0 && x < W && y < H) occ[y * W + x] = 4;
      bpos[bid] = { x: spot[0], y: spot[1], w, h, b };
      out.hotspots.push({ kind: "building", id: bid, x: spot[0], y: spot[1], w, h, label: b.name });
    }
    // packed earth round what stands, with a ragged edge (scene.js), and a lane from each door to the nearest road
    for (const p of Object.values(bpos)) for (let y = p.y - 3; y < p.y + p.h + 4; y++) for (let x = p.x - 3; x < p.x + p.w + 4; x++) {
      if (lv(x, y) <= 0 || occ[y * W + x] === 3) continue;
      const dx = Math.max(p.x - x, x - (p.x + p.w - 1), 0), dy = Math.max(p.y - y, y - (p.y + p.h - 1), 0);
      if (dx + dy <= 1 + 2.4 * n2(x / 5, y / 5, 2)) P.put(x, y, n3(x / 2, y / 2, 1) > 0.6 ? PAL.ground[1] : PAL.ground[0]);
    }
    for (const p of Object.values(bpos)) {
      let x = p.x + (p.w >> 1), y = p.y + p.h; let best = null, bd = 1e9;
      for (let yy = 0; yy < H; yy += 2) for (let xx = 0; xx < W; xx += 2) if (occ[yy * W + xx] === 3) { const dd = (xx - x) ** 2 + (yy - y) ** 2; if (dd < bd) { bd = dd; best = [xx, yy]; } }
      if (best && bd < 40 * 40) for (let s = 0; s < 60; s++) { if (Math.abs(best[0] - x) + Math.abs(best[1] - y) < 1) break; if (Math.abs(best[0] - x) > Math.abs(best[1] - y)) x += Math.sign(best[0] - x); else y += Math.sign(best[1] - y); if (occ[y * W + x] !== 4) { P.put(x, y, PAL.lane); if (!occ[y * W + x]) occ[y * W + x] = 5; } }
    }
    // trees after the buildings claimed their plots, drawn back to front
    trees.sort((a, b) => a[1] - b[1]);
    for (const [x, y, r] of trees) { if (occ[(y | 0) * W + (x | 0)] || lv(x, y) <= 0) continue; let ok = true; for (let k = -2; k <= 2; k++) if (lv(x + k, y + 2) <= 0 || occ[((y + 2) | 0) * W + ((x + k) | 0)] >= 3) ok = false; if (ok) tree(P, x, y, r, R); }
    Object.values(bpos).sort((a, b) => (a.y + a.h) - (b.y + b.h)).forEach((p) => building(P, p.x, p.y, p.w, p.h, p.b, rng(hstr(p.b.name))));
    // herds on their parcel
    for (const [hid, h] of Object.entries(d.herds)) {
      if (h.node !== nid) continue; const i = pids.indexOf(h.parcel); if (i < 0) continue;
      const hR = rng(hstr(hid + day)), cells = area[i].filter(([x, y]) => !occ[y * W + x] && reg(x + 5, y + 3) === i);
      const n = Math.max(1, Math.min(14, Math.round(h.count || 1))), pts = [];
      for (let k = 0; k < n && cells.length; k++) { const [x, y] = cells[(hR() * cells.length) | 0]; cow(P, x, y, hR, h.kind); pts.push([x, y]); }
      if (pts.length) { const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]); out.hotspots.push({ kind: "herd", id: hid, x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs) + 6, h: Math.max(...ys) - Math.min(...ys) + 4, label: `${h.name || hid} (${h.count})` }); }
    }
    // things lying about: bodies (graves once buried), carcasses, goods left
    Object.entries(d.things).filter(([, t]) => t.node === nid && !t.on_road).forEach(([cid, t], k) => {
      const i = pids.indexOf(t.parcel); const [cx, cy] = t.in && bpos[t.in] ? [bpos[t.in].x + bpos[t.in].w + 2, bpos[t.in].y + bpos[t.in].h] : centreOf(Math.max(0, i));
      const x = (cx + ((hstr(cid) % 15) - 7)) | 0, y = (cy + ((hstr(cid) >>> 5) % 9) - 4) | 0;
      if (t.kind === "body") { t.buried != null ? grave(P, x, y) : person(P, x, y, t.of || cid, { dead: true }); }
      else if (t.kind === "carcass") bones(P, x, y); else sack(P, x, y);
      out.hotspots.push({ kind: "thing", id: cid, x: x - 2, y: y - 3, w: 6, h: 6, label: t.kind === "body" ? `the body of ${t.of}` : t.kind === "carcass" ? "a carcass" : "goods left" });
    });
    // people: where they worked today (their last act's parcel), else by the house they slept in; a tool for what they did
    const acts = {}; for (const a of d.acts) if (a.node === nid) acts[a.actor] = a;
    const placed = {};
    const people = Object.entries(d.people).filter(([, p]) => p.node === nid && (p.alive || p.died === d.day)).sort((a, b) => a[0] < b[0] ? -1 : 1);
    for (const [name, p] of people) {
      let x, y; const a = acts[name], i = pids.indexOf(p.parcel);
      const pR = rng(hstr(name + "|" + day));
      if (p.slept && bpos[p.slept] && (!a || !a.site || p.parcel === bpos[p.slept].b.parcel)) { const b = bpos[p.slept]; const k = placed[p.slept] = (placed[p.slept] || 0) + 1; x = b.x + b.w + 1 + ((k - 1) % 4) * 4; y = b.y + b.h + 2 + Math.floor((k - 1) / 4) * 7; }
      else if (i >= 0) { const cells = area[i].filter(([xx, yy]) => !occ[yy * W + xx] && lv(xx, yy) > 0); const c = cells.length ? cells[(pR() * cells.length) | 0] : centreOf(i); x = c[0]; y = c[1]; }
      else { const [cx, cy] = centreOf(Math.max(0, pids.findIndex((q) => ST.parcels[q].cover === "built"))); x = cx + (pR() - .5) * 20; y = cy + (pR() - .5) * 12; }
      const said = d.said && d.said[name] && (d.said[name].say || []).length;
      person(P, x, y, name, { child: p.stage === "child", dead: !p.alive, hungry: p.hunger <= -1 ? -p.hunger : 0, tool: !p.alive ? null : said && !a ? "speak" : toolFor(a) });
      out.hotspots.push({ kind: "person", id: name, x: (x | 0) - 2, y: (y | 0) - 6, w: 6, h: 8, label: name + (a ? ` · ${a.verb}${a.tech ? " " + a.tech : ""}` : said ? " · speaking" : "") });
    }
    // what the night brought, at its place: a death, a fight, a break-in (a small marker the page can pulse)
    for (const e of d.events) {
      if (e.place !== nid || !["death", "fight", "raid", "fire", "alarm", "theft"].includes(e.kind)) continue;
      const who = e.target || e.actor, hs = out.hotspots.find((h) => h.kind === "person" && h.id === who);
      const bid = (e.about || []).map((x) => String(x).split(":")).find(([k]) => k === "building")?.[1];
      const at = bid && bpos[bid] ? [bpos[bid].x + bpos[bid].w / 2, bpos[bid].y - 3] : hs ? [hs.x + 3, hs.y - 2] : [W / 2, H / 2];
      out.hotspots.push({ kind: "event", id: e.kind, x: (at[0] | 0) - 3, y: (at[1] | 0) - 3, w: 7, h: 7, label: e.text, event: e.kind });
    }
    // the parcels themselves, for labels and clicks
    pids.forEach((pid, i) => { if (!area[i].length) return; const [cx, cy] = centreOf(i); out.hotspots.push({ kind: "parcel", id: pid, x: bbox[i][0], y: bbox[i][1], w: bbox[i][2] - bbox[i][0], h: bbox[i][3] - bbox[i][1], cx, cy, label: ST.parcels[pid].name }); });
    P.flush();
    return out;
  }

  // ---------------------------------------------------------------------------------------------------- the region
  function world(cv, V, day, opts = {}) {
    const W = opts.width || 400, H = opts.height || 260, d = D(V, day), ST = V.static, WL = ST.layout.world;
    const seed = hstr("world|" + (V.meta.seed ?? 1) + "|" + V.meta.name), R = rng(seed), n1 = noise(seed ^ 1), n2 = noise(seed ^ 2), n3 = noise(seed ^ 3);
    const P = Px(cv, W, H, "#6ca63c"), out = { width: W, height: H, hotspots: [] };
    const nodes = Object.keys(ST.nodes).sort();
    // (fog over an unexplored place is drawn in the night's blue, as the site's sky)
    const pos = {}; for (const n of nodes) pos[n] = [(WL[n] || [500, 350])[0] * W / 1000, (WL[n] || [500, 350])[1] * H / 700];
    // each place's covers, as shares, decide the country around it
    const mix = {};
    for (const n of nodes) { const m = {}; let t = 0; for (const p of Object.values(ST.parcels)) if (p.node === n) { m[p.cover] = (m[p.cover] || 0) + (+p.size || 1); t += +p.size || 1; } for (const k in m) m[k] /= t || 1; mix[n] = m; }
    const LV = new Int8Array(W * H), KIND = new Array(W * H), occ = new Uint8Array(W * H);
    const lv = (x, y) => (x < 0 || y < 0 || x >= W || y >= H) ? -1 : LV[(y | 0) * W + (x | 0)];
    const nearest = (x, y) => { let b = null, bd = 1e18; for (const n of nodes) { const dd = (x - pos[n][0]) ** 2 + (y - pos[n][1]) ** 2; if (dd < bd) { bd = dd; b = n; } } return [b, Math.sqrt(bd)]; };
    const order = ["built", "field", "pasture", "meadow", "scrub", "forest", "rock", "water"];
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const [n, dist] = nearest(x + (n1(x / 20, y / 20) - .5) * 30, y + (n1(x / 20 + 9, y / 20) - .5) * 30), m = mix[n] || {};
      const inner = Math.max(0, 1 - dist / 46);                                                    // the place's own land near it
      let kind;
      if (dist < 9) kind = "built";
      else if (inner > 0) {                                                                         // a ring of its covers by share
        const v = n2(x / 14, y / 14, 3), cum = []; let s = 0;
        for (const c of order.slice(1)) if (m[c]) { s += m[c]; cum.push([s, c]); }
        kind = "meadow"; for (const [t, c] of cum) if (v * s <= t) { kind = c; break; }
      } else kind = n2(x / 30 + 50, y / 30, 3) > 0.55 ? "forest" : n3(x / 50, y / 50, 3) > 0.7 ? "rock" : "meadow";
      const e = n3(x / 60, y / 60, 4);
      KIND[y * W + x] = kind;
      LV[y * W + x] = kind === "water" ? 0 : kind === "rock" || e > 0.72 ? 3 : e > 0.58 ? 2 : 1;
    }
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const k = KIND[y * W + x], l = LV[y * W + x], v = n3(x / 3, y / 3, 2); let col;
      if (k === "water") { let shore = false; for (const [a, b] of [[2, 0], [-2, 0], [0, 2], [0, -2]]) if (lv(x + a, y + b) > 0) shore = true; col = shore ? PAL.water.shore : (n3(x / 6, y / 3, 2) > 0.6 ? PAL.water.deep2 : PAL.water.deep); }
      else if (k === "rock") col = PAL.rock[v > 0.62 ? 1 : v < 0.36 ? 2 : 0];
      else if (k === "scrub") { col = PAL.grass[Math.min(3, l)][v > 0.62 ? 1 : v < 0.36 ? 2 : 0]; if (n3(x * 1.6, y * 1.6, 1) > 0.72) col = PAL.bush[(x + y) & 1]; else if (v < 0.3) col = PAL.scrub[1]; }
      else col = PAL.grass[Math.min(3, l)][v > 0.62 ? 1 : v < 0.36 ? 2 : 0];
      P.put(x, y, col);
    }
    for (let y = 0; y < H - 1; y++) for (let x = 0; x < W; x++) { const l = LV[y * W + x]; if (l <= 0) continue;
      if (lv(x, y + 1) < l && lv(x, y + 1) > 0) { P.put(x, y, PAL.rim); for (let k = 1; k <= 3; k++) { if (lv(x, y + k) >= l || y + k >= H) break; P.put(x, y + k, PAL.face[Math.min(3, k - 1 + (x % 3 === 0 ? 1 : 0))]); } } }
    // fields as patchworks behind hedges, close to each place
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (KIND[y * W + x] === "field") {
      const fx = x + (n1(x / 9, y / 9) - .5) * 6, fy = y + (n1(x / 9 + 3, y / 9) - .5) * 4;
      const cell = (Math.floor(fx / 11) * 31 + Math.floor(fy / 7) * 17) >>> 0, edge = Math.floor(fx / 11) !== Math.floor((fx + 1) / 11) || Math.floor(fy / 7) !== Math.floor((fy + 1) / 7);
      if (edge) { if (n3(x / 2, y / 2) < .7) P.put(x, y, PAL.hedge); continue; }
      const [n] = nearest(x, y), crop = Object.entries(ST.parcels).filter(([pid, p]) => p.node === n && p.cover === "field").map(([pid]) => d.parcels[pid]?.crop).filter(Boolean)[cell % 3];
      const st = crops(crop, day), pal = st === "ripe" ? PAL.ripe : st === "growing" ? PAL.growing : st === "sprout" ? PAL.sprout : st === "failed" ? PAL.failed : PAL.soil;
      P.put(x, y, pal[(cell & 1 ? x : y) % 2]);
    }
    // roads between the places (scene.js road), wider on a road than a track; a bridge where one crosses water
    const paint = (x, y, col) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; P.put(x, y, LV[y * W + x] === 0 ? "#a0662f" : col); occ[y * W + x] = 3; };
    const roadPts = {};
    for (const [rid, r] of Object.entries(ST.roads)) {
      const a = pos[r.a], b = pos[r.b]; if (!a || !b) continue;
      const rr = rng(hstr(rid)), pts = []; let [x, y] = a, hd = Math.atan2(b[1] - y, b[0] - x);
      const unx = ST.nodes[r.a]?.unexplored || ST.nodes[r.b]?.unexplored, col = unx ? PAL.lane : PAL.road;
      for (let s = 0; s < 1500; s++) {
        if (Math.hypot(b[0] - x, b[1] - y) < 1.5) break;
        let dd = Math.atan2(b[1] - y, b[0] - x) - hd; dd = Math.atan2(Math.sin(dd), Math.cos(dd));
        hd += Math.max(-0.08, Math.min(0.08, dd)) + (n2(x / 16 + rr() * 0.01, y / 16) - 0.5) * 0.16; x += Math.cos(hd); y += Math.sin(hd);
        if (unx && s % 3 === 2) { pts.push([x, y]); continue; }                                      // a faint way to an unexplored place
        paint(x, y, col); if (!r.track) paint(x + 1, y, col); pts.push([x, y]);
      }
      roadPts[rid] = pts;
      const mid = pts[pts.length >> 1] || a;
      out.hotspots.push({ kind: "road", id: rid, x: (mid[0] | 0) - 4, y: (mid[1] | 0) - 4, w: 8, h: 8, label: `${ST.nodes[r.a]?.name} — ${ST.nodes[r.b]?.name}: ${r.days} day${r.days > 1 ? "s" : ""}${r.terrain ? ", " + r.terrain : ""}`, pts: pts.filter((_, i) => i % 6 === 0).map(([x, y]) => [Math.round(x), Math.round(y)]) });
      // landmarks along the way: a stone marker at each
      (r.stretches || []).forEach((st, i, all) => (st.landmarks || []).forEach((lm, j) => { const p = pts[Math.min(pts.length - 1, Math.floor(pts.length * (i + .5) / all.length) + j * 6)]; if (!p) return; P.put(p[0] + 2, p[1] - 2, "#e8e8e0"); P.put(p[0] + 2, p[1] - 1, "#a8a29a");
        out.hotspots.push({ kind: "landmark", id: rid + ":" + i + ":" + j, x: (p[0] | 0), y: (p[1] | 0) - 4, w: 5, h: 5, label: String(lm.kind || lm.words || lm) }); }));
    }
    // each place: a village of its buildings round a square, sized by what stands today
    for (const n of nodes) {
      const [cx, cy] = pos[n], bs = Object.entries(d.buildings).filter(([, b]) => b.node === n).sort((a, b) => a[0] < b[0] ? -1 : 1);
      for (let y = -4; y <= 4; y++) for (let x = -6; x <= 6; x++) if (x * x / 36 + y * y / 16 <= 1) P.put(cx + x, cy + y, "#cdb88a");
      P.put(cx, cy, "#4e94a8");
      const nR = rng(hstr(n));
      bs.forEach(([bid, b], k) => {
        const a = k * 2.39996 + nR(), r = 8 + 3.2 * Math.sqrt(k + 1), [w, h] = (() => { const [ww, hh] = dims(b); return [Math.max(4, ww - 3), Math.max(4, hh - 2)]; })();
        const x0 = (cx + Math.cos(a) * r * 1.4 - w / 2) | 0, y0 = (cy + Math.sin(a) * r - h / 2) | 0;
        building(P, x0, y0, w, h, { ...b, fittings: {} }, nR);
      });
      if (ST.nodes[n].unexplored) for (let y = -26; y <= 26; y++) for (let x = -34; x <= 34; x++) { const dd = x * x / (34 * 34) + y * y / (26 * 26); if (dd > 1) continue; if ((x + y) % 2 === 0 || dd < 0.7) P.mix(cx + x, cy + y, PAL.fog, 0.55 * (1 - dd * 0.4)); }
      const pop = Object.values(d.people).filter((p) => p.alive && p.node === n).length;
      out.hotspots.push({ kind: "node", id: n, x: (cx | 0) - 16, y: (cy | 0) - 12, w: 32, h: 24, cx, cy, label: ST.nodes[n].name, pop, unexplored: !!ST.nodes[n].unexplored,
        deaths: d.events.filter((e) => e.place === n && e.kind === "death").length });
    }
    // trees in the wild country and round each place's woods, kept off roads and villages
    const trees = [];
    for (let gy = 0; gy < H; gy += 3) for (let gx = 0; gx < W; gx += 3) { const x = gx + R() * 2, y = gy + R() * 2; if (KIND[(y | 0) * W + (x | 0)] !== "forest") continue; if (n2(x / 9, y / 9) < 0.3) continue; trees.push([x, y]); }
    trees.sort((a, b) => a[1] - b[1]);
    for (const [x, y] of trees) { let ok = true; for (let k = -2; k <= 2; k++) for (let j = -2; j <= 3; j++) if (occ[((y + j) | 0) * W + ((x + k) | 0)] || lv(x + k, y + j) <= 0) ok = false; for (const n of nodes) if (Math.hypot(x - pos[n][0], y - pos[n][1]) < 16) ok = false; if (ok) tree(P, x, y, R() < 0.6 ? 2 : 2.6, R); }
    // travellers on the roads, at how far they have come
    for (const [name, t] of Object.entries(d.travellers || {})) {
      const r = ST.roads[t.road], pts = roadPts[t.road]; if (!r || !pts || !pts.length) continue;
      const f = t.from === r.a ? t.progress : 1 - t.progress, p = pts[Math.max(0, Math.min(pts.length - 1, Math.round(f * 0.85 * (pts.length - 1) + 0.075 * (pts.length - 1))))];
      person(P, p[0], p[1] - 1, name, { tool: "carry" });
      out.hotspots.push({ kind: "person", id: name, x: (p[0] | 0) - 2, y: (p[1] | 0) - 7, w: 6, h: 8, label: `${name} → ${ST.nodes[t.to]?.name || t.to}` });
    }
    P.flush();
    return out;
  }

  G.C2Pixel = { world, node, looks, hstr, rng, noise, PAL };
})(typeof window !== "undefined" ? window : globalThis);
