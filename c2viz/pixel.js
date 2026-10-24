// c2viz pixel renderer: the cybertron2 world as a pixel-art map in the site's night-village style (wp/site-v2:
// site/assets/scene.js for the low-resolution canvas, value noise, trees, houses and terraces with cliff faces; the villagers'
// colours from site/assets/core/villagers.js). Everything is drawn from the run's data for one day.
//
//   C2Pixel.world(canvas, viz, day, opts)        the region: every place in its own territory, its ground plan at one scale for
//                                                all places, its buildings as small houses, its people as small figures; roads
//                                                between places, travellers on them. Unexplored places are drawn as they are.
//   C2Pixel.node(canvas, viz, nodeId, day)        one place close up (a canvas sized to the place: pan it): parcels as land
//                                                (height, crops in strips, fences, woods, rivers), buildings in their lots
//                                                (structure, condition, fire, fittings, a yard and a garden), herds by kind and
//                                                count, things lying about, people where they worked with their tools and state
//
// One ground plan serves both scales (geom): it is read from what the world has, the parcels' sizes, neighbours and sides and
// the lots buildings stand in, so a place looks the same from the region as close up. Each place has a character (farmland, woodland, riverside, upland, moor) from its parcels, which
// sets its grass, trees and wild country; the season colours the trees and brings snow.
//
// Both return { width, height, hotspots: [{kind, id, x, y, w, h, label, ...}] } in canvas pixels. Show the canvas scaled up with
// `image-rendering: pixelated`. The same data always gives the same picture.
(function (G) {
  "use strict";
  // ---------------------------------------------------------------------------------------------------- toolkit (scene.js)
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

  // ---------------------------------------------------------------------------------------------------- palettes
  const PAL = {
    water: { deep: "#4e94a8", deep2: "#5aa2b4", shore: "#7cc0c8", foam: "#d8f0f0" },
    face: ["#e6e2d6", "#d2ccbc", "#bdb5a2", "#a69c88"], rim: "#b0dc6a", rimShade: "#5a9030",
    road: "#d8b47a", lane: "#e2c896", ground: ["#d8c48e", "#c8b07a", "#ccb684"], hedge: "#4f8a34", balk: "#a8cc62",
    soil: ["#9a6e46", "#b8865a"], stubble: ["#dccb8a", "#cdb878"], sprout: ["#9a7a50", "#86b44a"], growing: ["#a8d050", "#8cb83e"],
    ripe: ["#e8c840", "#d4ac30"], failed: ["#a89c84", "#8f846e"], bush: ["#5c7a34", "#4e6a2c"], rock: ["#a8a49a", "#bcb8ae", "#948f84"],
    flowers: ["#ffffff", "#f6e27a", "#f2a0c0", "#c8b8f0"], fenceWood: ["#6b4423", "#8a5a2a"], fenceStone: ["#8a8a92", "#b4b4ba"],
    copper: "#5ab09a", fog: "#1b2444", reed: "#8aa86a", snow: ["#f4f6fa", "#e2e8f0", "#cfd8e4"],
  };
  // a place's character, from its parcels: grass by height (1..3), its trees, how wooded its wild country is
  const BIOMES = {
    farmland:  { grass: [["#9cc44e", "#acd45c", "#8cb444"], ["#8cba48", "#9cca56", "#7caa3e"], ["#7cae40", "#8cbe4e", "#6c9e36"]], trees: ["oak"], wild: 0.28 },
    woodland:  { grass: [["#6ca63c", "#7cb64a", "#5c9632"], ["#5f9a36", "#6fac44", "#528a2c"], ["#548e30", "#64a03c", "#487e28"]], trees: ["oak", "oak", "birch"], wild: 0.78 },
    riverside: { grass: [["#7cc04c", "#8cd05a", "#6cb042"], ["#74b446", "#84c454", "#64a43c"], ["#6ca63c", "#7cb64a", "#5c9632"]], trees: ["willow", "oak"], wild: 0.4 },
    upland:    { grass: [["#9aaa58", "#aab866", "#8a9a4e"], ["#8e9e52", "#9eae60", "#7e8e48"], ["#82924c", "#92a25a", "#728242"]], trees: ["pine", "pine", "birch"], wild: 0.42 },
    moor:      { grass: [["#8e8a5a", "#9a7a7a", "#7e7a50"], ["#867c56", "#946e78", "#76704c"], ["#7e7652", "#8a6670", "#6e6a48"]], trees: ["pine"], wild: 0.06 },
    meadow:    { grass: [["#8cc04c", "#9cd05a", "#7cb042"], ["#7cb444", "#8cc452", "#6ca43a"], ["#6ca63c", "#7cb64a", "#5c9632"]], trees: ["oak", "birch"], wild: 0.45 },
  };
  function biomeOf(V, nid) {
    const share = {}; let tot = 0, hsum = 0;
    for (const p of Object.values(V.static.parcels)) if (p.node === nid) { const s = +p.size || 1; share[p.cover] = (share[p.cover] || 0) + s; tot += s; hsum += (p.height ?? 1) * s; }
    const f = (c) => (share[c] || 0) / (tot || 1), h = hsum / (tot || 1), name = (V.static.nodes[nid].name + " " + (V.static.nodes[nid].text || "")).toLowerCase();
    if (/moor|heath/.test(name)) return "moor";
    if (f("rock") + f("scrub") >= 0.4 || h >= 2.2 || /crag|pass|hill|fell/.test(name)) return "upland";
    if (f("field") >= 0.35) return "farmland";
    if (f("water") >= 0.25) return "riverside";
    if (f("forest") >= 0.35) return "woodland";
    return "meadow";
  }
  // villagers' colours (site/assets/core/villagers.js)
  const HAIR = ["#2a1a10", "#7a4a24", "#c8553d", "#e8c060", "#4a2a5a", "#d8d0c0", "#a0662f", "#5a3a1c"];
  const SKIN = ["#f8dcc0", "#f6c99f", "#e0a878", "#c8906a", "#9a6a4a", "#6a4a32"];
  const CLOTHES = ["#6a9a3a", "#4878c8", "#c8553d", "#7a5aa0", "#e8a33c", "#3a8a8a", "#a0662f", "#d07aa0", "#8a9a3a"];
  const TROUSERS = ["#5a4a3a", "#3a3a4a", "#4a5a8a", "#6a5a4a"];
  const looks = (name) => { const h = hstr(name); return { hair: HAIR[h % 8], skin: SKIN[(h >>> 3) % 6], clothes: CLOTHES[(h >>> 6) % 9], trousers: TROUSERS[(h >>> 10) % 4] }; };
  const ROOF = { timber: ["#c8553d", "#e07a5a", "#9a3a24"], stone: ["#7a7a86", "#9a9aa6", "#55555f"], wattle: ["#c8a050", "#e0bc68", "#9a7838"], camp: ["#a07a4a", "#c09a62", "#7a5a32"] };
  const WALL = { timber: "#f2e8d4", stone: "#d6d0c4", wattle: "#e8d4a8", camp: "#cdb48a" };

  // ---------------------------------------------------------------------------------------------------- trees, by kind and season
  const LEAF = {
    summer: [["#2f7d3a", "#3a8a3e", "#286e34"], "#58a648", "#1f5a2a"],
    spring: [["#3a8a3e", "#4a9a44", "#348036"], "#6ab858", "#24643a"],
    autumn: [["#c8782a", "#d8a03a", "#a8502a", "#6a8a3a", "#b86a2a"], "#e8c060", "#6a3a1c"],
  };
  function tree(P, x, y, r, R, kind, season) {
    x = Math.round(x); y = Math.round(y);
    const snow = season === "winter";
    if (kind === "pine") {                                                       // a conifer: tiers, always green
      const h = Math.round(r * 2 + 1);
      for (let k = 0; k <= h; k++) for (let dx = -Math.floor(k / 2) - 0; dx <= Math.floor(k / 2); dx++) P.dark(x + dx + 1, y - h + k + 2, 0.3);
      for (let k = 0; k <= h; k++) { const w = Math.floor(k / 2); for (let dx = -w; dx <= w; dx++) P.put(x + dx, y - h + k + 1, snow && k % 3 === 0 ? PAL.snow[1] : dx === -w ? "#3a7a4a" : dx === w ? "#1a4a2e" : "#2a5e3a"); }
      P.put(x, y + 2, "#5a3a1c");
      return;
    }
    if (snow) {                                                                   // bare branches in winter
      P.put(x, y + 1, "#5a3a24"); P.put(x, y, "#5a3a24"); P.put(x - 1, y - 1, "#6b4a32"); P.put(x + 1, y - 1, "#6b4a32"); P.put(x, y - 2, "#6b4a32");
      if (r > 2) { P.put(x - 2, y - 2, "#7a5a3c"); P.put(x + 2, y - 2, "#7a5a3c"); }
      return;
    }
    const pal = LEAF[season === "autumn" && kind !== "willow" ? "autumn" : season === "spring" ? "spring" : "summer"];
    const body = kind === "willow" ? ["#7aa84a", "#8cbc58", "#6a9a40"] : pal[0], c = body[(R() * body.length) | 0];
    for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (dx * dx + dy * dy <= r * r + 0.5) P.dark(x + dx + 1, y + dy + 1, 0.35);
    for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) { if (dx * dx + dy * dy > r * r + 0.5) continue; P.put(x + dx, y + dy, dx + dy < -r + 0.5 ? (kind === "willow" ? "#a8d070" : pal[1]) : dx + dy > r - 0.5 ? pal[2] : c); }
    if (kind === "willow") for (let dx = -r; dx <= r; dx += 2) P.put(x + dx, y + r + 1, "#6a9a40");          // hanging fronds
    if (kind === "birch") { P.put(x, y + r + 1, "#f0f0e8"); P.put(x, y + r, "#f0f0e8"); }
    if (season === "spring" && kind === "oak" && R() < 0.4) { P.put(x - 1, y - 1, "#f8e0ec"); P.put(x + 1, y, "#ffffff"); }       // blossom
  }

  // ---------------------------------------------------------------------------------------------------- sprites
  // a person on a place's map: 3 x 6 (a child 2 x 4), villager colours, holding a tool to one side
  function person(P, x, y, name, o = {}) {
    const L = looks(name); x |= 0; y |= 0;
    if (o.dead) { P.put(x - 1, y, "#d8d2c4"); P.put(x, y, "#d8d2c4"); P.put(x + 1, y, "#d8d2c4"); P.put(x + 2, y, L.skin); P.dark(x - 1, y + 1, .3); P.dark(x, y + 1, .3); P.dark(x + 1, y + 1, .3); return; }
    if (o.child) { P.put(x, y - 3, L.hair); P.put(x + 1, y - 3, L.hair); P.put(x, y - 2, L.skin); P.put(x + 1, y - 2, L.skin); P.put(x, y - 1, L.clothes); P.put(x + 1, y - 1, L.clothes); P.put(x, y, L.trousers); P.put(x + 1, y, L.trousers); P.dark(x + 2, y, .3); return; }
    for (const [dx, dy, c] of [[0, -5, L.hair], [1, -5, L.hair], [-1, -4, L.hair], [0, -4, L.skin], [1, -4, L.skin], [0, -3, L.clothes], [1, -3, L.clothes],
      [-1, -3, L.skin], [2, -3, L.skin], [0, -2, L.clothes], [1, -2, L.clothes], [0, -1, L.trousers], [1, -1, L.trousers], [0, 0, "#4a2f17"], [1, 0, "#4a2f17"]]) P.put(x + dx, y + dy, c);
    P.dark(x + 2, y, .35); P.dark(x + 2, y - 1, .25);
    if (o.hungry) P.put(x + 1, y - 6, o.hungry > 1 ? "#e85a5a" : "#f0c060");
    if (o.tool) tool(P, x + 3, y - 3, o.tool);
  }
  // a person on the region's map: 1 x 2, hair over clothes
  function dot(P, x, y, name) { const L = looks(name); P.put(x, y - 1, L.hair); P.put(x, y, L.clothes); P.dark(x + 1, y, .3); }
  const TOOLS = {
    fell: [[0, 0, "#8a5a2a"], [0, 1, "#8a5a2a"], [0, 2, "#8a5a2a"], [1, 0, "#c8c8d0"], [1, -1, "#c8c8d0"]],
    reap: [[0, 1, "#8a5a2a"], [0, 2, "#8a5a2a"], [0, 0, "#c8c8d0"], [1, -1, "#c8c8d0"], [2, -1, "#c8c8d0"]],
    forage: [[0, 1, "#a0662f"], [1, 1, "#a0662f"], [0, 0, "#c8553d"], [1, 0, "#7ab04a"]],
    hunt: [[0, -1, "#8a5a2a"], [0, 0, "#8a5a2a"], [0, 1, "#8a5a2a"], [1, -2, "#c8c8d0"]],
    mine: [[0, 0, "#8a5a2a"], [0, 1, "#8a5a2a"], [-1, -1, "#9aa0a8"], [0, -1, "#9aa0a8"], [1, -1, "#9aa0a8"]],
    milk: [[0, 0, "#c8c8d0"], [1, 0, "#c8c8d0"], [0, 1, "#9aa0a8"], [1, 1, "#9aa0a8"]],
    dig: [[0, -1, "#8a5a2a"], [0, 0, "#8a5a2a"], [0, 1, "#9aa0a8"], [1, 1, "#9aa0a8"]],
    make: [[0, 0, "#8a5a2a"], [0, 1, "#8a5a2a"], [-1, -1, "#6a6a72"], [0, -1, "#6a6a72"], [1, -1, "#6a6a72"]],
    herd: [[0, -2, "#8a5a2a"], [0, -1, "#8a5a2a"], [0, 0, "#8a5a2a"], [0, 1, "#8a5a2a"], [1, -2, "#8a5a2a"]],
    sow: [[0, 0, "#c8a46a"], [1, 0, "#c8a46a"], [1, 1, "#9a7a50"]],
    carry: [[0, 0, "#c9b38a"], [1, 0, "#c9b38a"], [0, 1, "#a8946a"], [1, 1, "#a8946a"]],
    speak: [[0, -3, "#ffffff"], [1, -3, "#ffffff"], [2, -3, "#ffffff"], [0, -2, "#ffffff"], [1, -2, "#ffffff"], [2, -2, "#ffffff"], [0, -1, "#ffffff"]],
  };
  const TECH_TOOL = { fell: "fell", reap: "reap", forage: "forage", hay: "reap", hunt: "hunt", mine: "mine", quarry: "mine", milk: "milk",
    ditch: "dig", bury: "dig", fence: "make", wall: "make", herd: "herd", sow: "sow", dibble: "sow", plough: "dig", hoe: "dig", weed: "dig",
    dung: "carry", smelt: "make", charcoal: "make", coin: "make" };
  const toolFor = (a) => !a ? null : TECH_TOOL[a.tech] || (a.verb === "make" || a.verb === "build" ? "make" : a.verb === "gather" ? "forage" : a.verb === "work" ? "dig" : a.verb === "give" || a.verb === "take" ? "carry" : null);
  function tool(P, x, y, k) { for (const [dx, dy, c] of TOOLS[k] || []) P.put(x + dx, y + dy, c); }
  function cow(P, x, y, R, kind) {
    const body = kind === "oxen" || R() < 0.3 ? "#a0663a" : "#f4efe6", spot = body === "#f4efe6" ? "#2a2420" : "#6b4423";
    for (let dx = 0; dx < 4; dx++) for (let dy = 0; dy < 2; dy++) P.put(x + dx, y + dy, (dx === 1 && dy === 0 && R() < .7) ? spot : body);
    P.put(x + 4, y - 1, body); P.put(x + 4, y, body); P.put(x, y + 2, "#4a2f17"); P.put(x + 3, y + 2, "#4a2f17"); P.dark(x + 4, y + 2, .3); P.dark(x + 1, y + 2, .25);
  }
  function grave(P, x, y) { P.put(x, y - 2, "#c8c4bc"); P.put(x - 1, y - 1, "#c8c4bc"); P.put(x, y - 1, "#c8c4bc"); P.put(x + 1, y - 1, "#c8c4bc"); P.put(x, y, "#a8a29a"); P.put(x - 1, y + 1, "#7a5a3a"); P.put(x, y + 1, "#7a5a3a"); P.put(x + 1, y + 1, "#7a5a3a"); }
  function sack(P, x, y) { P.put(x, y - 1, "#a8946a"); P.put(x - 1, y, "#c9b38a"); P.put(x, y, "#c9b38a"); P.put(x + 1, y, "#b8a278"); P.dark(x + 2, y, .3); }
  function bones(P, x, y) { P.put(x - 1, y, "#f0ece0"); P.put(x, y, "#f0ece0"); P.put(x + 1, y, "#f0ece0"); P.put(x, y - 1, "#e0dccc"); }
  // a building: by structure, its fittings, smoke when the fire is lit, the damage, the frame of one being built
  function building(P, x0, y0, w, h, b, R) {
    const st = b.structure || "timber", roof = ROOF[st] || ROOF.timber, wall = WALL[st] || WALL.timber;
    for (let y = y0 + 1; y <= y0 + h; y++) P.dark(x0 + w, y, 0.38);
    for (let x = x0 + 1; x <= x0 + w; x++) P.dark(x, y0 + h, 0.38);
    if (b.unfinished) { for (let x = x0; x < x0 + w; x++) { P.put(x, y0 + h - 1, "#8a5a2a"); if (x % 2 === 0) P.put(x, y0 + h - 3, "#a0662f"); } for (let y = y0 + 1; y < y0 + h; y++) { P.put(x0, y, "#8a5a2a"); P.put(x0 + w - 1, y, "#8a5a2a"); } return; }
    if (st === "camp") { for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (Math.abs(x - (w - 1) / 2) <= y * w / (2 * h) + 0.3) P.put(x0 + x, y0 + y, x < w / 2 ? roof[1] : roof[0]); P.put(x0 + (w >> 1), y0 + h - 1, "#3a2414"); P.put(x0 + w + 1, y0 + h - 1, "#e8803a"); P.put(x0 + w + 1, y0 + h - 2, "#f0c060"); return; }
    const wy = h - 2 - (h > 7 ? 1 : 0);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      if (st === "wattle" && y < wy && Math.abs(x - (w - 1) / 2) > (y + 1.5) * w / (2 * wy)) continue;
      let c; if (y === 0) c = roof[2]; else if (y < wy) c = x === 0 ? roof[1] : roof[0]; else c = x === 0 ? "#d8ccb4" : wall;
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
    if (b.condition === 0) { for (let x = x0; x < x0 + w; x++) for (let y = y0; y < y0 + wy; y++) if (R() < 0.6) P.put(x, y, "#5a4a3a"); for (let k = 0; k < w; k++) P.put(x0 - 1 + ((R() * (w + 2)) | 0), y0 + h + ((R() * 2) | 0), "#8a8478"); }
  }
  // a building on the region's map: a small roof over a wall, a door
  function hut(P, x, y, w, h, b) {
    const roof = ROOF[b.structure] || ROOF.timber, wall = WALL[b.structure] || WALL.timber;
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) P.put(x + i, y + j, j === h - 1 ? (b.unfinished ? "#a0662f" : i === (w >> 1) ? "#6b4423" : wall) : j === 0 ? roof[1] : roof[0]);
    for (let i = 1; i <= w; i++) P.dark(x + i, y + h, .35); for (let j = 1; j < h; j++) P.dark(x + w, y + j, .35);
    if (b.fire) { P.put(x + w - 2, y - 1, "#e8e8e8"); P.put(x + w - 1, y - 2, "#f4f4f4"); }
  }
  function dims(b) {
    const s = Math.max(2, +b.size || 4), st = b.structure || "timber";
    if (st === "camp") return [7, 6];
    const w = Math.max(9, Math.min(18, Math.round(5 + Math.sqrt(s) * 2.6))), h = Math.max(7, Math.min(13, Math.round(4 + Math.sqrt(s) * 1.8)));
    return st === "wattle" ? [w - 1, h - 1] : [w, h];
  }

  // ---------------------------------------------------------------------------------------------------- close-up sprites
  // a villager close up: 5 x 9 (a child 5 x 6) in the site's colours, feet at (x..x+4, y). What is drawn on it is its state that
  // day: hunger over the head (amber: a meal missed; red: two or more), a wound, the tool of its work, a speech bubble, lying dead
  const BODY5 = [".HHH.", "HSSSH", ".ESE.", ".SSS.", "CCCCC", "SCCCS", ".CCC.", ".P.P.", ".F.F."];
  const CHILD5 = [".HHH.", ".ESE.", ".CCC.", "SCCCS", ".P.P.", ".F.F."];
  function villager(P, x, y, name, o = {}) {
    const L = looks(name), K = { H: L.hair, S: L.skin, E: "#2a1a10", C: L.clothes, P: L.trousers, F: "#4a2f17" };
    x |= 0; y |= 0;
    if (o.dead) {
      for (let dx = -1; dx < 7; dx++) P.dark(x + dx, y + 1, 0.3);
      for (const [dx, dy, c] of [[-1, -1, L.hair], [-1, 0, L.hair], [0, -1, L.skin], [0, 0, L.skin], [1, -1, L.clothes], [2, -1, L.clothes], [3, -1, L.clothes], [1, 0, L.clothes],
        [2, 0, L.clothes], [3, 0, L.clothes], [4, -1, L.trousers], [4, 0, L.trousers], [5, -1, "#4a2f17"], [5, 0, "#4a2f17"]]) P.put(x + dx, y + dy, c);
      return;
    }
    const rows = o.child ? CHILD5 : BODY5, top = y - rows.length + 1;
    for (let dx = 0; dx < 5; dx++) P.dark(x + dx + 1, y + 1, 0.28);
    rows.forEach((r, j) => { for (let i = 0; i < 5; i++) if (r[i] !== ".") P.put(x + i, top + j, K[r[i]]); });
    if (o.wounded) { P.put(x + 1, top + (o.child ? 2 : 4), "#d83a3a"); P.put(x + 2, top + (o.child ? 2 : 5), "#d83a3a"); }
    if (o.hungry) { const c = o.hungry > 1 ? "#e85a5a" : "#f0c060"; P.put(x + 2, top - 5, c); P.put(x + 2, top - 4, c); P.put(x + 2, top - 2, c); }
    if (o.speak) bubble(P, x + 4, top - 4);
    else if (o.tool) tool(P, x + 5, y - 3, o.tool);
  }
  function bubble(P, x, y) {
    for (let dy = 0; dy < 3; dy++) for (let dx = 0; dx < 5; dx++) if (!((dx === 0 || dx === 4) && (dy === 0 || dy === 2))) P.put(x + dx, y + dy, "#ffffff");
    P.put(x + 1, y + 1, "#6a6a7a"); P.put(x + 3, y + 1, "#6a6a7a"); P.put(x, y + 3, "#ffffff");
  }
  // a beast of a herd, by kind
  function beast(P, x, y, kind, R) {
    kind = String(kind || "cattle"); x |= 0; y |= 0;
    const put = (pts, c) => { for (const [dx, dy] of pts) P.put(x + dx, y + dy, c); };
    if (/sheep/.test(kind)) {
      for (let dx = 0; dx < 5; dx++) P.dark(x + dx + 1, y + 1, .25);
      put([[0, -2], [1, -2], [2, -2], [3, -2], [0, -1], [1, -1], [2, -1], [3, -1]], "#f4f2ea"); put([[1, -3], [2, -3]], "#e4e0d4");
      put([[4, -2], [4, -1]], "#3a3430"); put([[0, 0], [3, 0]], "#3a3430"); return;
    }
    if (/goat/.test(kind)) {
      for (let dx = 0; dx < 5; dx++) P.dark(x + dx + 1, y + 1, .25);
      put([[0, -2], [1, -2], [2, -2], [3, -2], [0, -1], [1, -1], [2, -1], [3, -1]], "#c8b090"); put([[4, -3], [4, -2]], "#a89070"); put([[4, -4], [5, -4]], "#6a5a4a"); put([[0, 0], [3, 0]], "#5a4a3a"); return;
    }
    if (/pig|swine|hog/.test(kind)) {
      for (let dx = 0; dx < 5; dx++) P.dark(x + dx + 1, y + 1, .25);
      put([[0, -2], [1, -2], [2, -2], [3, -2], [0, -1], [1, -1], [2, -1], [3, -1]], "#f0b0a8"); put([[4, -1]], "#d88a84"); put([[0, 0], [3, 0]], "#c87a74"); return;
    }
    const body = /ox/.test(kind) || R() < 0.3 ? "#a0663a" : "#f4efe6", spot = body === "#f4efe6" ? "#2a2420" : "#6b4423";
    for (let dx = 0; dx < 7; dx++) P.dark(x + dx + 1, y + 1, .28);
    for (let dx = 0; dx < 5; dx++) for (let dy = -2; dy < 0; dy++) P.put(x + dx, y + dy, body);
    if (R() < 0.8) { P.put(x + 1 + ((R() * 2) | 0), y - 2, spot); P.put(x + 3, y - 1, spot); }
    put([[5, -3], [5, -2], [6, -2]], body); P.dark(x + 6, y - 2, .25); put([[4, -3], [6, -4]], "#d8d0c0");
    put([[0, 0], [1, 0], [3, 0], [4, 0]], "#4a2f17");
  }
  function graveBig(P, x, y) { for (let dx = -2; dx <= 2; dx++) { P.put(x + dx, y, "#7a5a3a"); P.put(x + dx, y - 1, dx === -2 ? "#8a6a48" : "#7a5a3a"); } for (let dy = -5; dy <= -2; dy++) P.put(x, y + dy, "#c8c4bc"); P.put(x - 1, y - 4, "#c8c4bc"); P.put(x + 1, y - 4, "#c8c4bc"); P.dark(x + 1, y - 2, .3); }
  function sackBig(P, x, y, goods) {
    const g = Object.keys(goods || {}), col = g.some((k) => /timber|wood/.test(k)) ? "#8a5a2a" : g.some((k) => /stone|ore|copper/.test(k)) ? "#9a9aa0" : "#c9b38a";
    P.put(x, y - 3, "#a8946a"); for (let dx = -1; dx <= 1; dx++) { P.put(x + dx, y - 2, col); P.put(x + dx, y - 1, col); P.put(x + dx, y, col); } P.dark(x + 2, y, .3); P.dark(x + 2, y - 1, .2);
  }
  function bonesBig(P, x, y) { for (let dx = -2; dx <= 2; dx++) P.put(x + dx, y, "#f0ece0"); P.put(x - 1, y - 1, "#e0dccc"); P.put(x + 1, y - 1, "#e0dccc"); P.put(x + 3, y - 1, "#f0ece0"); P.put(x + 3, y, "#e0dccc"); }

  // ---------------------------------------------------------------------------------------------------- the land model
  const D = (V, day) => V.days[Math.max(0, Math.min(V.days.length - 1, day))];
  const cropState = (c, day) => !c ? null : c.failed ? "failed" : c.ripe ? "ripe" : (day - (c.sown ?? day)) <= 1 ? "sprout" : "growing";
  const RIVER = /river|brook|stream|leat|beck|burn|creek|race/i;
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
  const LOTS = { built: 6 }, STOPS = new Set(["built", "field", "rock"]);
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
      : ST.parcels[p].cover === "built" ? [1, 0, 1.2, 3] : null);
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
    // lots: every building the place ever has gets one, and keeps it
    const ever = {};
    V.days.forEach((d, day) => { for (const [bid, b] of Object.entries(d.buildings)) if (b.node === nid && !ever[bid]) ever[bid] = { day, b }; });
    const byPar = {}; for (const [bid, e] of Object.entries(ever)) { let i = idx[e.b.parcel]; if (i == null || (ST.parcels[pids[i]].cover === "water")) i = pids.findIndex((p) => ST.parcels[p].cover === "built"); if (i < 0) i = 0; (byPar[i] = byPar[i] || []).push(bid); }
    const lotOf = {}, lots = {};
    for (const [ik, bids] of Object.entries(byPar)) {
      const i = +ik, cov = ST.parcels[pids[i]].cover, count = Math.max(bids.length, Math.round((LOTS[cov] || 0) * size[i]));
      let cells = inner(i, 8, 6); if (!cells.length) cells = area[i].length ? area[i] : [centre[i]];
      const [cx, cy] = centre[i], got = [];
      for (let k = 0; k < count; k++) { let best = null, bs = -1e18;
        for (const [x, y] of cells) { let m = 1e9; for (const [gx, gy] of got) m = Math.min(m, (x - gx) ** 2 + (y - gy) ** 2); const s = got.length ? m - 0.02 * ((x - cx) ** 2 + (y - cy) ** 2) : -((x - cx) ** 2 + (y - cy) ** 2); if (s > bs) { bs = s; best = [x, y]; } }
        got.push(best); }
      lots[pids[i]] = got;
      bids.sort((a, b) => ever[a].day - ever[b].day || (+ever[b].b.size || 0) - (+ever[a].b.size || 0) || (a < b ? -1 : 1)).forEach((bid, k) => (lotOf[bid] = got[k]));
    }
    // where each road leaves: from the parcel it leaves by, out to the edge of the map that way
    const exits = Object.entries(L.exits || {}).map(([rid, ex]) => {
      const i = ex.parcels && ex.parcels.length && idx[ex.parcels[0]] != null ? idx[ex.parcels[0]] : pids.findIndex((p) => ST.parcels[p].cover === "built");
      const [fx, fy] = i >= 0 ? centre[i] : [W / 2, H / 2], [dx, dy] = ex.dir || [1, 0];
      let t = 0; while (t < 4 * (W + H)) { const x = fx + dx * t, y = fy + dy * t; if (x < 1 || y < 1 || x > W - 2 || y > H - 2) break; t += 1; }
      return { rid, ex, fx, fy, tx: Math.max(-2, Math.min(W + 1, fx + dx * t)), ty: Math.max(-2, Math.min(H + 1, fy + dy * t)) };
    });
    let gx = 0, gy = 0, gs = 0; area.forEach((a) => { for (const [x, y] of a) { gx += x; gy += y; gs++; } }); if (gs) { gx /= gs; gy /= gs; } else { gx = W / 2; gy = H / 2; }
    let land = 0; area.forEach((a) => { for (const [x, y] of a) land = Math.max(land, Math.hypot(x - gx, y - gy)); });
    const g = { W, H, REG, area, centre, adj, site, courses, lotOf, lots, exits, mid: [gx, gy], land: land || 40, reg, inner };
    cache[nid] = g; return g;
  }

  // paint the land: ground, terraces, each parcel's surface, rivers, the wild country's trees. `cellNode` and `cellPar` give, per
  // pixel, the place (an index into nids) and the parcel (an index into that place's parcels, -1 the wild); `sc` is pixels per
  // close-up pixel (1 close up, smaller on the region's map)
  function paintLand(P, V, day, W, H, nids, cellNode, cellPar, sc, R, occ, opts) {
    const M = model(V), d = D(V, day), season = (d.calendar || {}).season || "summer", snow = season === "winter";
    const n2 = noise(M.seed ^ 2), n3 = noise(M.seed ^ 3), small = sc < 0.5;
    const LV = new Int8Array(W * H), at = (x, y) => (x < 0 || y < 0 || x >= W || y >= H) ? -1 : (y | 0) * W + (x | 0);
    const parcelOf = (i) => { const n = cellNode[i]; if (n < 0 || cellPar[i] < 0) return null; return M.nodes[nids[n]].pids[cellPar[i]]; };
    const area = {}; for (let i = 0; i < W * H; i++) { const p = parcelOf(i); if (p) (area[p] = area[p] || []).push([i % W, (i / W) | 0]); }
    // rivers: water along each course, in its own parcel, other water and the wild; reeds along the banks
    const wet = new Uint8Array(W * H);
    for (const c of opts.courses || []) {
      const reed = small ? 0.6 : 1.8, rr = c.half + reed, e = Math.ceil(rr);
      for (const [lx, ly] of c.line) for (let dy = -e; dy <= e; dy++) for (let dx = -e; dx <= e; dx++) {
        const x = Math.round(lx + dx), y = Math.round(ly + dy), i = at(x, y); if (i < 0 || cellNode[i] !== c.n) continue;
        const p = parcelOf(i); if (p && !(c.pids || [c.pid]).includes(p) && STOPS.has(V.static.parcels[p].cover)) continue;
        const dd = Math.hypot(x - lx, y - ly); if (dd <= c.half) wet[i] = 1; else if (dd <= rr && !wet[i]) wet[i] = 2;
      }
    }
    for (let i = 0; i < W * H; i++) {
      const p = parcelOf(i);
      if (!p) { LV[i] = wet[i] === 1 ? 0 : 1; continue; }
      const P0 = V.static.parcels[p], N = M.nodes[P0.node];
      LV[i] = P0.cover === "water" ? (N.river[N.pids.indexOf(p)] ? (wet[i] === 1 ? 0 : 1) : 0) : wet[i] === 1 ? 0 : Math.max(1, Math.min(3, P0.height ?? 1));
    }
    const lv = (x, y) => { const i = at(x, y); return i < 0 ? -1 : LV[i]; };
    const grassOf = (n, l, v) => { const B = BIOMES[n >= 0 ? M.nodes[nids[n]].biome : "meadow"]; return B.grass[Math.max(0, Math.min(2, l - 1))][v > 0.62 ? 1 : v < 0.36 ? 2 : 0]; };
    // ground
    for (let i = 0; i < W * H; i++) {
      const x = i % W, y = (i / W) | 0, p = parcelOf(i), cov = p ? V.static.parcels[p].cover : "wild", v = n3(x / 3, y / 3, 2), l = LV[i], n = cellNode[i];
      let col;
      if (l === 0) { let shore = false; for (const [a, b] of [[2, 0], [-2, 0], [0, 2], [0, -2], [1, 1], [-1, -1]]) if (lv(x + a, y + b) > 0) shore = true;
        col = shore ? (n3(x / 2, y / 2, 1) > 0.6 ? PAL.water.foam : PAL.water.shore) : (n3(x / 6, y / 3, 2) > 0.6 ? PAL.water.deep2 : PAL.water.deep); }
      else if (cov === "rock") col = PAL.rock[v > 0.7 ? 1 : v < 0.3 ? 2 : 0];
      else col = grassOf(n, l, v);
      if (wet[i] === 2 && l > 0) col = n3(x * 1.5, y * 1.5, 1) > 0.45 ? PAL.reed : col;
      P.put(x, y, col);
      if (!p && l > 0) { P.dark(x, y, 0.13 + 0.06 * (n2(x / 20, y / 20) > .5)); if (!small && n3(x * 1.9, y * 1.9, 1) > 0.8) P.dark(x, y, .16); }
      else if (p && l > 0) { if (cov === "meadow") P.light(x, y, .07); else if (cov === "pasture") P.light(x, y, .03);
        else if (cov === "built") { P.mix(x, y, PAL.ground[0], 0.16); if (n2(x / 6 + 3, y / 6, 2) > 0.62) P.mix(x, y, PAL.ground[(x + y) & 1], 0.55); } }
      if (snow && l > 0) P.mix(x, y, PAL.snow[(x + y) % 3 === 0 ? 1 : 0], n3(x / 4 + 7, y / 4) > 0.3 ? 0.85 : 0.5);
    }
    // terraces (scene.js): a lip and a cliff face where the ground steps down to the south
    if (!small) for (let y = 0; y < H - 1; y++) for (let x = 0; x < W; x++) {
      const l = LV[y * W + x]; if (l <= 1) continue;
      if (lv(x, y + 1) < l && lv(x, y + 1) > 0) { P.put(x, y, snow ? PAL.snow[0] : PAL.rim); for (let k = 1; k <= 3; k++) { if (lv(x, y + k) >= l || y + k >= H) break; P.put(x, y + k, PAL.face[Math.min(3, k - 1 + (x % 3 === 0 ? 1 : 0))]); } }
    }
    // each parcel's surface
    const trees = [];
    const border = (x, y, p) => { for (const [a, b] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const j = at(x + a, y + b); if (j < 0 || parcelOf(j) !== p) return true; } return false; };
    const wildNext = (x, y) => { for (const [a, b] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const j = at(x + a, y + b); if (j >= 0 && cellPar[j] < 0 && LV[j] > 0) return true; } return false; };
    for (const [pid, pts] of Object.entries(area)) {
      if (!small && !["field", "water"].includes(V.static.parcels[pid].cover)) for (const [x, y] of pts) if (LV[y * W + x] > 0 && wildNext(x, y)) { P.dark(x, y, .28); P.dark(x, y + 1, .12); }
      const P0 = V.static.parcels[pid], dp = d.parcels[pid] || {}, res = dp.res || {}, c = P0.cover, N = M.nodes[P0.node], B = BIOMES[N.biome], pR = rng(hstr(pid + "|" + (opts.scale || "")));
      if (c === "field") {
        const st = cropState(dp.crop, day), left = dp.crop ? (dp.crop.left ?? 1) : 1, ang = fieldAngle(pid);
        const ux = Math.cos(ang), uy = Math.sin(ang), sw = small ? Math.max(1.5, 7 * sc) : 7 + (hstr(pid) >>> 9) % 3;
        let u0 = 1e9, u1 = -1e9; for (const [x, y] of pts) { const u = x * ux + y * uy; u0 = Math.min(u0, u); u1 = Math.max(u1, u); }
        const nstrip = Math.max(1, Math.ceil((u1 - u0) / sw));
        for (const [x, y] of pts) {
          if (LV[y * W + x] === 0) continue;
          if (border(x, y, pid)) { if (n3(x / 2 + 9, y / 2) < 0.75) P.put(x, y, PAL.hedge); if (!small && pR() < 0.025) trees.push([x, y, 1.5, "oak"]); continue; }
          const u = x * ux + y * uy - u0, s = Math.floor(u / sw), v = -x * uy + y * ux;
          if (!small && u - s * sw < 1) { P.put(x, y, PAL.balk); continue; }                                   // the balk between strips
          let pal = st === "ripe" ? PAL.ripe : st === "growing" ? PAL.growing : st === "failed" ? PAL.failed : st === "sprout" ? PAL.sprout : PAL.soil;
          if (st && (s + 0.5) / nstrip > left) pal = PAL.stubble;                                                  // strips already reaped
          P.put(x, y, pal[Math.floor(v / (small ? 1 : 2)) & 1]);
          if (!small && st === "ripe" && (Math.floor(v) % 3 === 0) && (x + y) % 2 === 0) P.dark(x, y, .12);        // ears
          const sh = ((hstr(pid + s) % 5) - 2) * 0.03; if (sh > 0) P.dark(x, y, sh); else if (sh < 0) P.light(x, y, -sh);
          if (snow) P.mix(x, y, PAL.snow[0], 0.7);
        }
      } else if (c === "pasture" || c === "meadow") {
        for (const [x, y] of pts) { if (LV[y * W + x] === 0) continue; const v = n3(x * 1.3, y * 1.3, 1);
          if (!snow && c === "meadow" && v > 0.84 && !small) P.put(x, y, PAL.flowers[(hstr(x + "," + y) >>> 3) % 4]);
          else if (v > 0.8 && !small) P.dark(x, y, .12);
          if (c === "pasture" && !small && border(x, y, pid) && n3(x / 2, y / 2 + 5) < 0.5) P.dark(x, y, .18);
          if (!snow && res.grass != null && res.grass < 0.35 && n3(x / 3 + 5, y / 3) < 0.6 - res.grass) P.mix(x, y, "#b8a868", 0.55); }
      } else if (c === "forest") {
        const w0 = ((V.days[0].parcels[pid] || {}).res || {}).wood, base = w0 > 0.05 ? Math.min(1, 0.45 + w0) : 0.4, wood = w0 > 0.05 ? Math.min(1, (res.wood ?? w0) / w0) * base : base;
        const step = small ? 2 : 3, nz = small ? 3 : 7;
        for (const [x, y] of pts) if (x % step === 0 && y % step === 0) { const tx = x + pR() * (step - 1), ty = y + pR() * (step - 1), v = n2(tx / nz, ty / nz);
          if (v < 0.15 + 0.85 * wood) trees.push([tx, ty, small ? 1 : (pR() < 0.6 ? 2 : 3), B.trees[(pR() * B.trees.length) | 0]]);
          else if (!small && v < 0.15 + 0.85 * base) { P.put(tx, ty, "#8a6a42"); P.put(tx + 1, ty, "#6b4423"); P.dark(tx, ty + 1, .25); } }   // stumps where it was felled
        for (const [x, y] of pts) if (!small && n3(x * 1.1, y * 1.1, 1) > 0.8) P.dark(x, y, .15);
      } else if (c === "scrub") {
        for (const [x, y] of pts) { if (pR() > (small ? 0.12 : 0.05) || n2(x / 9 + 3, y / 9, 2) < 0.45) continue;
          if (small) { P.put(x, y, PAL.bush[0]); continue; }
          for (const [a, b] of [[0, 0], [1, 0], [-1, 0], [0, -1], [1, -1]]) P.put(x + a, y + b, (a + b) < 0 ? "#6c8a40" : PAL.bush[(a + 1) & 1]); P.dark(x + 2, y, .3); P.dark(x, y + 1, .3); P.dark(x + 1, y + 1, .3); }
      } else if (c === "rock") {
        const st = small ? 3 : 6;
        for (const [x, y] of pts) { if (x % st || y % st || pR() > 0.45) continue; const bx = x + (pR() * 3 | 0), by = y + (pR() * 3 | 0);
          if (small) { P.put(bx, by, "#e8e8e0"); P.dark(bx + 1, by, .3); continue; }
          const bw = 3 + (pR() * 3 | 0), bh = 2 + (pR() * 2 | 0);
          for (let dy = 0; dy < bh; dy++) for (let dx = 0; dx < bw; dx++) P.put(bx + dx, by + dy, dy === 0 ? "#e8e8e0" : dx === bw - 1 || dy === bh - 1 ? "#9a9a92" : "#c8c8c0");
          for (let dx = 1; dx <= bw; dx++) P.dark(bx + dx, by + bh, .3); }
        if (res.seam != null) for (const [x, y] of pts) if (n2(x / 3, y / 3) > 0.8 - 0.2 * res.seam) P.put(x, y, PAL.copper);
      } else if (c === "water" && !N.river[N.pids.indexOf(pid)]) {
        for (const [x, y] of pts) if (n3(x / 2 + 3, y, 1) > 0.97) P.put(x, y, PAL.water.foam);
      }
      if (dp.fence && dp.fence.built !== false && !small) {                                                      // a fence or a wall round it
        const col = dp.fence.kind === "stone" ? PAL.fenceStone : PAL.fenceWood; let k = 0;
        for (const [x, y] of pts) if (border(x, y, pid)) { k++; if (dp.fence.level === 0 || (dp.fence.level === 1 && k % 5 === 0)) continue; P.put(x, y, col[(x + y) & 1]); }
      }
    }
    // the wild country's trees, by each place's character
    const wildStep = small ? 2 : 4;
    for (let gy = 0; gy < H; gy += wildStep) for (let gx = 0; gx < W; gx += wildStep) {
      const x = gx + R() * (wildStep - 1), y = gy + R() * (wildStep - 1), i = at(x, y); if (i < 0 || cellPar[i] >= 0 || LV[i] <= 0 || wet[i]) continue;
      const n = cellNode[i], B = BIOMES[n >= 0 ? M.nodes[nids[n]].biome : "meadow"], z = 26 * Math.max(0.4, Math.min(1, sc * 2)), wild = small || B === BIOMES.woodland ? B.wild : B.wild * 0.6;
      if (n2(x / z, y / z, 3) < 1 - wild) { if (!small && B === BIOMES.moor && R() < 0.15) { P.put(x, y, "#8a5a7a"); P.put(x + 1, y, "#9a6a8a"); } continue; }
      trees.push([x, y, small ? 1 : (R() < 0.6 ? 2 : 3), B.trees[(R() * B.trees.length) | 0] || "oak"]);
    }
    return { LV, area, trees, season, snow, lv, at, parcelOf, wet };
  }

  function drawTrees(P, trees, ctx, occ, W, H, R) {
    trees.sort((a, b) => a[1] - b[1]);
    for (const [x, y, r, kind] of trees) {
      const i = ctx.at(x, y); if (i < 0 || occ[i] || ctx.LV[i] <= 0) continue;
      let ok = true; for (let k = -1; k <= 1; k++) { const j = ctx.at(x + k, y + 2); if (j >= 0 && (occ[j] >= 3 || ctx.LV[j] <= 0)) ok = false; }
      if (ok) tree(P, x, y, r, R, kind, ctx.season);
    }
  }
  const paintRoad = (P, occ, LV, W, H) => (x, y, col) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const i = y * W + x; P.put(x, y, LV[i] === 0 ? "#a0662f" : col); occ[i] = 3; };
  function wind(paint, x, y, tx, ty, n, wide, col, dashed, out) {
    let hd = Math.atan2(ty - y, tx - x);
    for (let s = 0; s < 3000; s++) {
      if (Math.hypot(tx - x, ty - y) < 1.5) break;
      let dd = Math.atan2(ty - y, tx - x) - hd; dd = Math.atan2(Math.sin(dd), Math.cos(dd));
      hd += Math.max(-0.09, Math.min(0.09, dd)) + (n(x / 14 + 40, y / 14) - 0.5) * 0.14; x += Math.cos(hd); y += Math.sin(hd);
      if (out) out.push([x, y]);
      if (dashed && s % 3 === 2) continue;
      const w_ = +wide || 0; for (let a = 0; a <= w_; a++) for (let b = 0; b <= w_; b++) paint(x + a, y + b, col);
    }
  }

  // ---------------------------------------------------------------------------------------------------- a place on a day
  // where its buildings (in their lots), herds, things and people stand, in close-up pixels; the region's map shows them at the
  // same spots, smaller
  const PLAN = new WeakMap();
  function plan(V, nid, day) {
    let cache = PLAN.get(V); if (!cache) PLAN.set(V, cache = {});
    const key = nid + "|" + day; if (cache[key]) return cache[key];
    const G = geom(V, nid), W = G.W, H = G.H, M = model(V), N = M.nodes[nid], d = D(V, day), ST = V.static, occ = new Uint8Array(W * H);
    const out = { W, H, buildings: {}, herds: [], things: [], people: [], occ };
    const mark = (x0, y0, w, h, v) => { for (let y = y0; y < y0 + h; y++) for (let x = x0; x < x0 + w; x++) if (x >= 0 && y >= 0 && x < W && y < H) occ[y * W + x] = v; };
    for (const [bid, b] of Object.entries(d.buildings)) {
      if (b.node !== nid || !G.lotOf[bid]) continue;
      const [w, h] = dims(b), [lx, ly] = G.lotOf[bid], x = Math.round(lx - w / 2), y = Math.round(ly - h / 2);
      out.buildings[bid] = { x, y, w, h, b }; mark(x - 1, y - 2, w + 2, h + 3, 4);
    }
    const free = (x, y, w, h) => { for (let yy = y - h; yy <= y; yy++) for (let xx = x; xx < x + w; xx++) { if (xx < 0 || yy < 0 || xx >= W || yy >= H || occ[yy * W + xx]) return false; } return true; };
    const spot = (i, R, near, rad, w, h) => {                                        // a free spot in parcel i, near a point if given
      const cells = G.area[i] || []; if (!cells.length) return null;
      for (let t = 0; t < 80; t++) { const c = near ? [near[0] + (R() - .5) * 2 * rad, near[1] + (R() - .5) * 2 * rad] : cells[(R() * cells.length) | 0], x = c[0] | 0, y = c[1] | 0;
        if (G.reg(x, y) === i && G.reg(x + w, y) === i && G.reg(x, y - h) === i && free(x, y, w, h)) return [x, y]; }
      return null;
    };
    for (const [hid, h] of Object.entries(d.herds)) {
      if (h.node !== nid) continue; const i = N.pids.indexOf(h.parcel); if (i < 0) continue;
      const hR = rng(hstr(hid + "|" + day)), n = Math.max(1, Math.min(16, Math.round(h.count || 1))), c0 = spot(i, hR, null, 0, 7, 4) || G.centre[i], pts = [];
      for (let k = 0; k < n; k++) { const s = spot(i, hR, c0, 6 + Math.sqrt(n) * 6, 7, 4); if (s) { pts.push(s); mark(s[0], s[1] - 4, 8, 6, 6); } }
      out.herds.push({ id: hid, h, pts });
    }
    for (const [cid, t] of Object.entries(d.things)) {
      if (t.node !== nid || t.on_road) continue;
      const i = N.pids.indexOf(t.parcel), B = t.in && out.buildings[t.in], tR = rng(hstr(cid));
      let s = B ? [B.x + B.w + 2, B.y + B.h] : i >= 0 ? spot(i, tR, null, 0, 6, 5) : null; if (!s) s = i >= 0 ? G.centre[i] : G.mid;
      out.things.push({ id: cid, t, x: s[0] | 0, y: s[1] | 0 }); mark((s[0] | 0) - 2, (s[1] | 0) - 5, 8, 7, 6);
    }
    const acts = {}; for (const a of d.acts) if (a.node === nid) acts[a.actor] = a;
    const atDoor = {}, anchor = {}, built = N.pids.findIndex((p) => ST.parcels[p].cover === "built");
    for (const [name, p] of Object.entries(d.people).filter(([, p]) => p.node === nid && (p.alive || p.died === d.day)).sort((a, b) => a[0] < b[0] ? -1 : 1)) {
      const a = acts[name], pR = rng(hstr(name + "|" + day));
      let pid = (a && a.site) || p.parcel; if (pid && !ST.parcels[pid]) pid = (d.things[pid] || d.buildings[pid] || {}).parcel || null;
      const i = N.pids.indexOf(pid), home = p.slept && out.buildings[p.slept], homeI = home ? N.pids.indexOf(home.b.parcel) : -2;
      let s = null;
      if (home && (!a || i < 0 || i === homeI)) { const k = atDoor[p.slept] = (atDoor[p.slept] || 0) + 1; s = [home.x + (home.w >> 1) - 1 + ((k - 1) % 3 - 1) * 6, home.y + home.h + 10 + Math.floor((k - 1) / 3) * 11]; }
      else if (i >= 0) { if (!anchor[i]) anchor[i] = spot(i, rng(hstr(pid + "|" + day)), null, 0, 6, 10) || G.centre[i]; s = spot(i, pR, anchor[i], 22, 6, 10) || spot(i, pR, null, 0, 6, 10); }
      if (!s) { const c = built >= 0 ? G.centre[built] : G.mid; s = [c[0] + (pR() - .5) * 30, c[1] + (pR() - .5) * 20]; }
      s = [s[0] | 0, s[1] | 0]; mark(s[0] - 1, s[1] - 9, 7, 11, 7);
      out.people.push({ name, p, a, x: s[0], y: s[1] });
    }
    cache[key] = out; return out;
  }

  // ---------------------------------------------------------------------------------------------------- one place, close up
  function node(cv, V, nid, day) {
    const G = geom(V, nid), W = G.W, H = G.H, M = model(V), N = M.nodes[nid], d = D(V, day), ST = V.static, R = rng(hstr(nid) ^ M.seed);
    const P = Px(cv, W, H, "#6ca63c"), out = { width: W, height: H, hotspots: [] }, pl = plan(V, nid, day);
    const cellNode = new Int16Array(W * H).fill(0), occ = new Uint8Array(W * H);
    const ctx = paintLand(P, V, day, W, H, [nid], cellNode, G.REG, 1, R, occ, { scale: "node", courses: G.courses });
    const n2 = noise(M.seed ^ 5), paint = paintRoad(P, occ, ctx.LV, W, H);
    for (const e of G.exits) {                                                                       // roads leaving the place
      const r = ST.roads[e.rid];
      wind(paint, e.fx, e.fy, e.tx, e.ty, n2, !r || !r.track ? 2 : 1, e.ex.hidden ? PAL.lane : PAL.road, false);
      const lx = Math.max(10, Math.min(W - 10, e.tx)), ly = Math.max(8, Math.min(H - 8, e.ty));
      out.hotspots.push({ kind: "exit", id: e.rid, to: e.ex.to, x: lx - 8, y: ly - 8, w: 16, h: 16, label: "→ " + (ST.nodes[e.ex.to]?.name || e.ex.to) + " · " + (r?.days ?? "?") + " day" + ((r?.days ?? 1) > 1 ? "s" : "") });
    }
    const B = Object.entries(pl.buildings);
    for (const [, p] of B) for (let y = p.y - 1; y < p.y + p.h + 1; y++) for (let x = p.x - 1; x < p.x + p.w + 1; x++) if (x >= 0 && y >= 0 && x < W && y < H) occ[y * W + x] = 4;
    // a yard of packed earth before each door, a kitchen garden beside each house, a lane to the nearest road
    for (const [bid, p] of B) {
      for (let y = p.y + p.h - 2; y < p.y + p.h + 6; y++) for (let x = p.x - 2; x < p.x + p.w + 2; x++) { const i = ctx.at(x, y); if (i < 0 || ctx.LV[i] <= 0 || occ[i]) continue;
        const dx = Math.max(p.x - x, x - (p.x + p.w - 1), 0), dy = Math.max(0, y - (p.y + p.h - 1)); if (dx + dy <= 2 + 2.5 * n2(x / 4, y / 4, 2)) { P.put(x, y, ctx.snow ? PAL.snow[2] : n2(x / 2, y / 2, 1) > 0.6 ? PAL.ground[1] : PAL.ground[0]); occ[i] = 2; } }
      const dwelling = (p.b.sleepers || []).length || /house|cottage|hut|hall|steading|farm/i.test(p.b.name || "");
      if (dwelling && p.b.structure !== "camp") { const gx = (hstr(bid) & 1) ? p.x + p.w + 2 : p.x - 9, gy = p.y + 1; let ok = true;
        for (let y = gy - 1; y < gy + 7 && ok; y++) for (let x = gx - 1; x < gx + 8; x++) { const i = ctx.at(x, y); if (i < 0 || occ[i] || ctx.LV[i] <= 0) { ok = false; break; } }
        if (ok) for (let y = gy; y < gy + 6; y++) for (let x = gx; x < gx + 7; x++) { const edge = y === gy || y === gy + 5 || x === gx || x === gx + 6;
          P.put(x, y, edge ? PAL.fenceWood[(x + y) & 1] : ctx.snow ? PAL.snow[1] : ctx.season === "autumn" || ctx.season === "winter" ? PAL.soil[(y & 1)] : (y & 1) ? "#5a9a3a" : PAL.soil[0]); occ[y * W + x] = 2; } }
    }
    for (const [, p] of B) {
      let x = p.x + (p.w >> 1), y = p.y + p.h + 1, best = null, bd = 1e9;
      for (let yy = 0; yy < H; yy += 2) for (let xx = 0; xx < W; xx += 2) if (occ[yy * W + xx] === 3) { const dd = (xx - x) ** 2 + (yy - y) ** 2; if (dd < bd) { bd = dd; best = [xx, yy]; } }
      if (best && bd < 70 * 70) for (let s = 0; s < 140; s++) { if (Math.abs(best[0] - x) + Math.abs(best[1] - y) < 1) break; if (Math.abs(best[0] - x) > Math.abs(best[1] - y)) x += Math.sign(best[0] - x); else y += Math.sign(best[1] - y); const i = y * W + x; if (occ[i] !== 4) { P.put(x, y, PAL.lane); if (!occ[i]) occ[i] = 5; } }
    }
    for (const q of pl.people) for (let y = q.y - 9; y <= q.y + 1; y++) for (let x = q.x - 1; x < q.x + 7; x++) { const i = ctx.at(x, y); if (i >= 0 && !occ[i]) occ[i] = 1; }
    for (const h of pl.herds) for (const [x0, y0] of h.pts) for (let y = y0 - 4; y <= y0 + 1; y++) for (let x = x0; x < x0 + 8; x++) { const i = ctx.at(x, y); if (i >= 0 && !occ[i]) occ[i] = 1; }
    drawTrees(P, ctx.trees, ctx, occ, W, H, R);
    // everything that stands, back to front
    const items = [];
    for (const [bid, p] of B) items.push({ y: p.y + p.h, f: () => { building(P, p.x, p.y, p.w, p.h, p.b, rng(hstr(p.b.name)));
      out.hotspots.push({ kind: "building", id: bid, x: p.x, y: p.y, w: p.w, h: p.h, label: buildingLabel(p.b) }); } });
    for (const h of pl.herds) { const hR = rng(hstr(h.id + day)); for (const [x, y] of h.pts) items.push({ y, f: () => beast(P, x, y, h.h.kind, hR) });
      if (h.pts.length) { const xs = h.pts.map((q) => q[0]), ys = h.pts.map((q) => q[1]); out.hotspots.push({ kind: "herd", id: h.id, x: Math.min(...xs), y: Math.min(...ys) - 4, w: Math.max(...xs) - Math.min(...xs) + 8, h: Math.max(...ys) - Math.min(...ys) + 6,
        label: `${h.h.name || h.id}: ${h.h.count} ${h.h.kind || ""}${h.h.hungry ? ", hungry" : ""}${h.h.in_milk ? `, ${Math.round(h.h.in_milk)} in milk` : ""}${(h.h.holders || []).length ? " (" + h.h.holders.join(", ") + ")" : ""}` }); } }
    for (const t of pl.things) items.push({ y: t.y, f: () => {
      if (t.t.kind === "body") (t.t.buried != null ? graveBig(P, t.x, t.y) : villager(P, t.x, t.y, t.t.of || t.id, { dead: true })); else if (t.t.kind === "carcass") bonesBig(P, t.x, t.y); else sackBig(P, t.x, t.y, t.t.goods);
      const goods = Object.entries(t.t.goods || {}).map(([k, v]) => `${Math.round(v * 10) / 10} ${k}`).join(", ");
      out.hotspots.push({ kind: "thing", id: t.id, x: t.x - 3, y: t.y - 6, w: 8, h: 8, label: (t.t.kind === "body" ? (t.t.buried != null ? `the grave of ${t.t.of}` : `the body of ${t.t.of}`) : t.t.kind === "carcass" ? "a carcass" : "goods left lying") + (goods ? ": " + goods : "") }); } });
    for (const q of pl.people) items.push({ y: q.y, f: () => {
      const said = d.said && d.said[q.name] && (d.said[q.name].say || []).length;
      villager(P, q.x, q.y, q.name, { child: q.p.stage === "child", dead: !q.p.alive, wounded: q.p.wounded, hungry: q.p.hunger <= -1 ? -q.p.hunger : 0, speak: said && !q.a, tool: toolFor(q.a) });
      out.hotspots.push({ kind: "person", id: q.name, x: q.x - 1, y: q.y - 9, w: 7, h: 11, label: personLabel(q, d) }); } });
    items.sort((a, b) => a.y - b.y).forEach((it) => it.f());
    for (const e of d.events) {
      if (e.place !== nid || !["death", "fight", "raid", "fire", "alarm", "theft"].includes(e.kind)) continue;
      const hs = out.hotspots.find((h) => h.kind === "person" && h.id === (e.target || e.actor));
      const bid = (e.about || []).map((x) => String(x).split(":")).find(([k]) => k === "building")?.[1], Bq = bid && pl.buildings[bid];
      const xy = Bq ? [Bq.x + Bq.w / 2, Bq.y - 3] : hs ? [hs.x + 3, hs.y - 2] : G.mid;
      out.hotspots.push({ kind: "event", id: e.kind, x: (xy[0] | 0) - 4, y: (xy[1] | 0) - 4, w: 9, h: 9, label: e.text, event: e.kind });
    }
    N.pids.forEach((pid, i) => { if (!G.area[i].length) return; const [cx, cy] = G.centre[i]; let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1; for (const [x, y] of G.area[i]) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
      out.hotspots.push({ kind: "parcel", id: pid, x: x0, y: y0, w: x1 - x0, h: y1 - y0, cx, cy, label: ST.parcels[pid].name, info: parcelLabel(V, pid, d, day) }); });
    out.biome = N.biome; out.season = ctx.season; out.focus = (() => { const i = N.pids.findIndex((p) => ST.parcels[p].cover === "built"); return i >= 0 ? G.centre[i] : G.mid; })();
    P.flush();
    return out;
  }
  function buildingLabel(b) {
    const fit = Object.keys(b.fittings || {}), sl = b.sleepers || [];
    return `${b.name}: ${b.unfinished ? "being built, " : ""}${b.structure || ""}${b.condition === 1 ? ", damaged" : b.condition === 0 ? ", in ruins" : ""}${b.fire ? ", fire lit" : ""}${fit.length ? "; " + fit.join(", ") : ""}${sl.length ? "; slept here: " + sl.join(", ") : ""}${(b.holders || []).length ? "; held by " + b.holders.join(", ") : ""}`;
  }
  function personLabel(q, d) {
    const p = q.p, bits = [q.name];
    if (!p.alive) bits.push("dead" + (p.cause ? ` (${p.cause})` : ""));
    if (q.a) bits.push(`${q.a.verb}${q.a.tech ? " " + q.a.tech : ""}${q.a.for ? " for " + q.a.for : ""}`);
    else if (d.said && d.said[q.name] && (d.said[q.name].say || []).length) bits.push("speaking");
    if (p.hunger <= -1) bits.push(`hungry (${-p.hunger} missed)`);
    if (p.wounded) bits.push("wounded");
    if (p.stage && p.stage !== "adult") bits.push(p.stage);
    const hands = Object.entries(p.hands || {}).filter(([, v]) => v > 0.05).map(([k, v]) => `${Math.round(v * 10) / 10} ${k}`).slice(0, 5);
    if (hands.length) bits.push("carrying " + hands.join(", "));
    return bits.join(" · ");
  }
  function parcelLabel(V, pid, d, day) {
    const P0 = V.static.parcels[pid], dp = d.parcels[pid] || {}, bits = [`${P0.cover}, size ${P0.size}`];
    const st = cropState(dp.crop, day); if (st) bits.push(`${dp.crop.kind || "crop"} ${st}${dp.crop.left != null && dp.crop.left < 1 ? `, ${Math.round(dp.crop.left * 100)}% left` : ""}`);
    if (dp.fence) bits.push("fenced"); if ((dp.holders || []).length) bits.push("held by " + dp.holders.join(", "));
    const nb = (P0.adj || []).map((q) => V.static.parcels[q]?.name).filter(Boolean); if (nb.length) bits.push("next to " + nb.join(", "));
    return bits.join("; ");
  }

  // ---------------------------------------------------------------------------------------------------- the region
  // each place's ground plan at one scale for all places (so a big place looks big), in its own territory; its buildings as
  // small houses, its people as the small figures, roads between places, travellers on them. Unexplored places are drawn as they
  // are: the world exists before anyone finds it.
  function world(cv, V, day, opts = {}) {
    const M = model(V), d = D(V, day), ST = V.static, WL = ST.layout.world, nids = Object.keys(ST.nodes).sort();
    const W = opts.width || 400, H = opts.height || 260, R = rng(M.seed ^ 77), P = Px(cv, W, H, "#6ca63c"), out = { width: W, height: H, hotspots: [] };
    const pos = {}; for (const n of nids) pos[n] = [(WL[n] || [500, 350])[0] * W / 1000, (WL[n] || [500, 350])[1] * H / 700];
    const G = {}; for (const n of nids) G[n] = geom(V, n);
    let md = 1e9; for (const a of nids) for (const b of nids) if (a < b) md = Math.min(md, Math.hypot(pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]));
    if (md > 1e8) md = Math.min(W, H) * 0.8;
    const f = Math.min(0.6, ...nids.map((n) => 0.52 * md / G[n].land));                            // region pixels a close-up pixel
    const toWorld = (n, x, y) => [pos[n][0] + (x - G[n].mid[0]) * f, pos[n][1] + (y - G[n].mid[1]) * f];
    const n1 = noise(M.seed ^ 11);
    const cellNode = new Int16Array(W * H).fill(-1), cellPar = new Int16Array(W * H).fill(-1), occ = new Uint8Array(W * H);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const jx = x + (n1(x / 24, y / 24, 3) - .5) * 26, jy = y + (n1(x / 24 + 7, y / 24, 3) - .5) * 26; let best = -1, bd = 1e18;
      for (let i = 0; i < nids.length; i++) { const dd = (jx - pos[nids[i]][0]) ** 2 + (jy - pos[nids[i]][1]) ** 2; if (dd < bd) { bd = dd; best = i; } }
      cellNode[y * W + x] = best;                                                                       // the territory
      const n = nids[best], g = G[n], lx = Math.round(g.mid[0] + (x - pos[n][0]) / f), ly = Math.round(g.mid[1] + (y - pos[n][1]) / f);
      if (lx >= 0 && ly >= 0 && lx < g.W && ly < g.H) cellPar[y * W + x] = g.REG[ly * g.W + lx];
    }
    const courses = [];
    nids.forEach((n, ni) => { for (const c of G[n].courses) courses.push({ pid: c.pid, pids: c.pids, n: ni, half: Math.max(0.7, c.half * f), line: c.line.filter((_, k) => k % 2 === 0).map(([x, y]) => toWorld(n, x, y)) }); });
    const ctx = paintLand(P, V, day, W, H, nids, cellNode, cellPar, f, R, occ, { scale: "world", courses });
    // territory borders: a faint line of darker ground where two places' lands meet in the wild
    for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) { const i = y * W + x; if (cellPar[i] >= 0) continue; if (cellNode[i] !== cellNode[i + 1] || cellNode[i] !== cellNode[i + W]) if ((x + y) % 3 !== 0) P.dark(x, y, 0.16); }
    // roads: from the parcel each leaves a place by, winding to the other place
    const n2 = noise(M.seed ^ 5), paint = paintRoad(P, occ, ctx.LV, W, H), roadPts = {};
    const exitPt = (n, rid) => { const e = G[n].exits.find((q) => q.rid === rid); return e ? toWorld(n, e.fx, e.fy) : pos[n]; };
    for (const [rid, r] of Object.entries(ST.roads)) {
      if (!pos[r.a] || !pos[r.b]) continue;
      const a = exitPt(r.a, rid), b = exitPt(r.b, rid), pts = [];
      wind(paint, a[0], a[1], b[0], b[1], n2, r.track ? 0 : 1, r.track ? PAL.lane : PAL.road, false, pts);
      roadPts[rid] = pts;
      const mid = pts[pts.length >> 1] || a;
      out.hotspots.push({ kind: "road", id: rid, x: (mid[0] | 0) - 4, y: (mid[1] | 0) - 4, w: 8, h: 8, label: `${ST.nodes[r.a]?.name} — ${ST.nodes[r.b]?.name}: ${r.days} day${r.days > 1 ? "s" : ""}${r.terrain ? ", " + r.terrain : ""}` });
      (r.stretches || []).forEach((st, i, all) => (st.landmarks || []).forEach((lm, j) => { const p = pts[Math.min(pts.length - 1, Math.floor(pts.length * (i + .5) / all.length) + j * 6)]; if (!p) return;
        P.put(p[0] + 2, p[1] - 2, "#e8e8e0"); P.put(p[0] + 2, p[1] - 1, "#a8a29a"); out.hotspots.push({ kind: "landmark", id: rid + ":" + i + ":" + j, x: (p[0] | 0), y: (p[1] | 0) - 4, w: 5, h: 5, label: String(lm.kind || lm.words || lm) }); }));
    }
    // each place's buildings, herds, things and people where they are in its own plan
    const items = [];
    for (const n of nids) {
      const pl = plan(V, n, day); let tx = 0, ty = 0, tn = 0;
      for (const [, p] of Object.entries(pl.buildings)) { const [x, y] = toWorld(n, p.x + p.w / 2, p.y + p.h / 2), w = Math.max(4, Math.round(p.w * f * 1.3)), h = Math.max(3, Math.round(p.h * f * 1.3)), bx = Math.round(x - w / 2), by = Math.round(y - h / 2);
        items.push({ y: by + h, f: () => hut(P, bx, by, w, h, p.b) }); tx += x; ty += y; tn++;
        for (let yy = by - 1; yy < by + h + 2; yy++) for (let xx = bx - 1; xx < bx + w + 1; xx++) { const i = ctx.at(xx, yy); if (i >= 0) { occ[i] = 4; if (ctx.LV[i] > 0) P.put(xx, yy, ctx.snow ? PAL.snow[2] : PAL.ground[(xx + yy) & 1]); } } }
      for (const h of pl.herds) for (const [x0, y0] of h.pts.slice(0, 8)) { const [x, y] = toWorld(n, x0, y0); items.push({ y, f: () => { P.put(x, y, "#f4efe6"); P.put(x + 1, y, "#f4efe6"); P.put(x + 2, y - 1, "#f4efe6"); P.dark(x + 2, y, .3); } }); }
      for (const t of pl.things) { const [x, y] = toWorld(n, t.x, t.y); items.push({ y, f: () => t.t.kind === "body" ? (P.put(x, y - 1, "#c8c4bc"), P.put(x, y, "#7a5a3a")) : P.put(x, y, "#c9b38a") }); }
      for (const q of pl.people) { const [x, y] = toWorld(n, q.x + 2, q.y); items.push({ y, f: () => person(P, x, y, q.name, { child: q.p.stage === "child", dead: !q.p.alive, hungry: q.p.hunger <= -1 ? -q.p.hunger : 0 }) });
        out.hotspots.push({ kind: "person", id: q.name, x: (x | 0) - 2, y: (y | 0) - 6, w: 5, h: 7, label: personLabel(q, d), node: n }); }
      const pop = Object.values(d.people).filter((p) => p.alive && p.node === n).length, [cx, cy] = tn ? [tx / tn, ty / tn] : pos[n];
      out.hotspots.push({ kind: "node", id: n, x: (pos[n][0] - G[n].land * f * 0.7) | 0, y: (pos[n][1] - G[n].land * f * 0.6) | 0, w: G[n].land * f * 1.4, h: G[n].land * f * 1.2, cx, cy: Math.min(H - 12, cy + 8), label: ST.nodes[n].name, pop,
        unexplored: !!ST.nodes[n].unexplored, biome: M.nodes[n].biome, deaths: d.events.filter((e) => e.place === n && e.kind === "death").length });
    }
    drawTrees(P, ctx.trees, ctx, occ, W, H, R);
    items.sort((a, b) => a.y - b.y).forEach((it) => it.f());
    for (const [name, t] of Object.entries(d.travellers || {})) {
      const r = ST.roads[t.road], pts = roadPts[t.road]; if (!r || !pts || !pts.length) continue;
      const fr = t.from === r.a ? t.progress : 1 - t.progress, p = pts[Math.max(0, Math.min(pts.length - 1, Math.round((0.08 + 0.84 * fr) * (pts.length - 1))))];
      person(P, p[0], p[1] - 1, name, { tool: "carry" });
      out.hotspots.push({ kind: "person", id: name, x: (p[0] | 0) - 2, y: (p[1] | 0) - 7, w: 6, h: 8, label: `${name} → ${ST.nodes[t.to]?.name || t.to}` });
    }
    out.season = ctx.season; out.scale = f;
    P.flush();
    return out;
  }

  G.C2Pixel = { world, node, plan, geom, biomeOf, looks, hstr, rng, noise, PAL, BIOMES };
})(typeof window !== "undefined" ? window : globalThis);
