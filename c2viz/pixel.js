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
    return { put, get, dark: (x, y, t) => shade(x, y, t), light: (x, y, t) => shade(x, y, -t), mix, flush, W, H, save: () => buf.slice(), restore: (b) => buf.set(b) };
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
    if (snow) {                                                                   // bare in winter: a haze of twigs over a trunk
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (dx * dx + dy * dy <= r * r + 0.5) P.mix(x + dx, y + dy - 1, "#7a6656", 0.42);
      P.put(x, y + 1, "#5a3a24"); P.put(x, y, "#6b4a32"); if (R() < 0.6) P.put(x + (R() < 0.5 ? -1 : 1), y - 1, "#6b4a32");
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
  const FIRES = ["hearth", "oven", "anvil", "fire ring"];
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
    if (o.pregnant && !o.child) P.put(x + 3, top + 6, L.clothes), P.dark(x + 3, top + 6, .15);
    if (o.load && !o.child) { P.put(x - 1, top + 4, "#a8946a"); P.put(x - 1, top + 5, "#c9b38a"); P.put(x - 1, top + 6, "#b8a278"); }
    if (o.wounded) { P.put(x + 1, top + (o.child ? 2 : 4), "#d83a3a"); P.put(x + 2, top + (o.child ? 2 : 5), "#d83a3a"); }
    if (o.hungry) { const c = o.hungry > 1 ? "#e85a5a" : "#f0c060"; P.put(x + 2, top - 5, c); P.put(x + 2, top - 4, c); P.put(x + 2, top - 2, c); }
    if (o.speak) bubble(P, x + 4, top - 4);
    else if (o.tool) tool(P, x + 5, y - 3, o.tool);
  }
  function bubble(P, x, y) {
    for (let dy = 0; dy < 3; dy++) for (let dx = 0; dx < 5; dx++) if (!((dx === 0 || dx === 4) && (dy === 0 || dy === 2))) P.put(x + dx, y + dy, "#ffffff");
    P.put(x + 1, y + 1, "#6a6a7a"); P.put(x + 3, y + 1, "#6a6a7a"); P.put(x, y + 3, "#ffffff");
  }
  function graveBig(P, x, y) { for (let dx = -2; dx <= 2; dx++) { P.put(x + dx, y, "#7a5a3a"); P.put(x + dx, y - 1, dx === -2 ? "#8a6a48" : "#7a5a3a"); } for (let dy = -5; dy <= -2; dy++) P.put(x, y + dy, "#c8c4bc"); P.put(x - 1, y - 4, "#c8c4bc"); P.put(x + 1, y - 4, "#c8c4bc"); P.dark(x + 1, y - 2, .3); }
  function sackBig(P, x, y, goods) {
    const g = Object.keys(goods || {}), col = g.some((k) => /timber|wood/.test(k)) ? "#8a5a2a" : g.some((k) => /stone|ore|copper/.test(k)) ? "#9a9aa0" : "#c9b38a";
    P.put(x, y - 3, "#a8946a"); for (let dx = -1; dx <= 1; dx++) { P.put(x + dx, y - 2, col); P.put(x + dx, y - 1, col); P.put(x + dx, y, col); } P.dark(x + 2, y, .3); P.dark(x + 2, y - 1, .2);
  }
  function bonesBig(P, x, y) { for (let dx = -2; dx <= 2; dx++) P.put(x + dx, y, "#f0ece0"); P.put(x - 1, y - 1, "#e0dccc"); P.put(x + 1, y - 1, "#e0dccc"); P.put(x + 3, y - 1, "#f0ece0"); P.put(x + 3, y, "#e0dccc"); }

  // ---------------------------------------------------------------------------------------------------- the land model
  const D = (V, day) => (V.__at && V.__at.day === day) ? V.__at.rec : V.days[Math.max(0, Math.min(V.days.length - 1, day))];
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

  // paint the land from the day's record (c2viz/model.py): each parcel by its cover that day and its stocks (S/K), crops by the
  // engine's stage and their sown and reaped shares, works, fences, clearing; snow when it lies. `cellNode` and `cellPar` give, per
  // pixel, the place (an index into nids) and the parcel (an index into that place's parcels, -1 the wild); `sc` is pixels per
  // close-up pixel (1 close up, smaller on the region's map)
  const CROP_PAL = {
    grain: { new: ["#9a7a50", "#86b44a"], green: ["#a8d050", "#8cb83e"], high: ["#c0d050", "#a8b838"], ripe: ["#e8c840", "#d4ac30"] },
    "winter grain": { new: ["#9a7a50", "#7aa848"], green: ["#98c858", "#80b048"], high: ["#b8c460", "#a0ac48"], ripe: ["#d8b850", "#c4a03c"] },
    legumes: { new: ["#9a7a50", "#6aa040"], green: ["#5f9a3a", "#4e8a30"], high: ["#5f9a3a", "#4e8a30"], ripe: ["#8a8a3a", "#7a6e30"] },
  };
  const STAGE_PAL = { rotting: ["#a88a30", "#8a7028"], blighted: ["#a89c84", "#8f846e"], killed: ["#9aa0a0", "#868c8c"] };
  function paintLand(P, V, day, W, H, nids, cellNode, cellPar, sc, R, occ, opts) {
    const M = model(V), d = D(V, day), season = (d.calendar || {}).season || "summer", snow = !!d.snow, sdays = V.meta.season_days || 6;
    const n2 = noise(M.seed ^ 2), n3 = noise(M.seed ^ 3), small = sc < 0.5, RL = opts.relief || null;
    const LV = new Int8Array(W * H), at = (x, y) => (x < 0 || y < 0 || x >= W || y >= H) ? -1 : (y | 0) * W + (x | 0);
    const parcelOf = (i) => { const n = cellNode[i]; if (n < 0 || cellPar[i] < 0) return null; return M.nodes[nids[n]].pids[cellPar[i]]; };
    const cov = (pid) => (d.parcels[pid] || {}).cover || V.static.parcels[pid].cover;
    const area = {}; for (let i = 0; i < W * H; i++) { const p = parcelOf(i); if (p) (area[p] = area[p] || []).push([i % W, (i / W) | 0]); }
    // rivers: water along each course, in its own chain, other water, and the wild; reeds on the banks
    const wet = new Uint8Array(W * H);
    for (const c of opts.courses || []) {
      const reed = small ? 0.6 : 1.8, rr = c.half + reed, e = Math.ceil(rr);
      for (const [lx, ly] of c.line) for (let dy = -e; dy <= e; dy++) for (let dx = -e; dx <= e; dx++) {
        const x = Math.round(lx + dx), y = Math.round(ly + dy), i = at(x, y); if (i < 0 || (c.n != null && cellNode[i] !== c.n)) continue;
        const p = parcelOf(i); if (p && !(c.pids || [c.pid]).includes(p) && STOPS.has(cov(p))) continue;
        const dd = Math.hypot(x - lx, y - ly); if (dd <= c.half) wet[i] = 1; else if (dd <= rr && !wet[i]) wet[i] = 2;
      }
    }
    for (let i = 0; i < W * H; i++) {
      const p = parcelOf(i);
      if (!p) { LV[i] = wet[i] === 1 ? 0 : RL ? RL.level[i] : 1; continue; }
      const P0 = V.static.parcels[p], N = M.nodes[P0.node];
      LV[i] = cov(p) === "water" ? (N.river[N.pids.indexOf(p)] ? (wet[i] === 1 ? 0 : RL ? RL.level[i] : 1) : 0) : wet[i] === 1 ? 0 : RL ? RL.level[i] : Math.max(1, Math.min(3, P0.height ?? 1));
    }
    const lv = (x, y) => { const i = at(x, y); return i < 0 ? -1 : LV[i]; };
    const grassOf = (n, l, v) => { const B = BIOMES[n >= 0 ? M.nodes[nids[n]].biome : "meadow"]; return B.grass[Math.max(0, Math.min(2, l - 1))][v > 0.62 ? 1 : v < 0.36 ? 2 : 0]; };
    // ground
    for (let i = 0; i < W * H; i++) {
      const x = i % W, y = (i / W) | 0, p = parcelOf(i), c = p ? cov(p) : "wild", v = n3(x / 3, y / 3, 2), l = LV[i], n = cellNode[i];
      let col;
      if (l === 0) { let shore = false; for (const [a, b] of [[2, 0], [-2, 0], [0, 2], [0, -2], [1, 1], [-1, -1]]) if (lv(x + a, y + b) > 0) shore = true;
        col = shore ? (n3(x / 2, y / 2, 1) > 0.6 ? PAL.water.foam : PAL.water.shore) : (n3(x / 6, y / 3, 2) > 0.6 ? PAL.water.deep2 : PAL.water.deep); }
      else if (c === "rock") col = PAL.rock[v > 0.7 ? 1 : v < 0.3 ? 2 : 0];
      else col = grassOf(n, l, v);
      if (wet[i] === 2 && l > 0) col = n3(x * 1.5, y * 1.5, 1) > 0.45 ? PAL.reed : col;
      P.put(x, y, col);
      if (!p && l > 0 && RL) {                                                                       // the region's wild land by its kind
        const k = RL.kind[i], moor = n >= 0 && M.nodes[nids[n]].biome === "moor";
        if (k === 2) { P.put(x, y, v > 0.66 ? "#aaa59a" : v < 0.33 ? "#8a857a" : "#9a958a"); if (n3(x * 1.7, y * 1.7, 1) > 0.82) P.put(x, y, "#c4c0b4"); }
        else if (k === 1) { P.mix(x, y, moor ? "#8a7068" : "#8e9a58", moor ? 0.45 : 0.4); if (n3(x * 1.5, y * 1.5, 1) > 0.9) P.put(x, y, "#b8b4aa"); }
        else if (k === 3) { P.put(x, y, RL.tint[i]); P.mix(x, y, "#6a8a5a", 0.45); const pv = n3(x / 12 + 3, y / 12, 2); if (pv > 0.7) P.put(x, y, pv > 0.76 ? "#4e7e94" : "#5a8aa0"); else if (pv > 0.64 && n3(x * 2, y * 2, 1) > 0.5) P.put(x, y, PAL.reed); }
        else { P.put(x, y, RL.tint[i]); if (v > 0.62) P.light(x, y, .06); else if (v < 0.36) P.dark(x, y, .06);
          const tg = [null, ["#8cc04c", "#9cd05a", "#7cb042"], ["#7cb444", "#8cc452", "#6ca43a"], ["#6ca63c", "#7cb64a", "#5c9632"], ["#8a9a52", "#9aaa5e", "#7a8a48"]][Math.min(4, l)];
          if (tg) { P.put(x, y, tg[v > 0.62 ? 1 : v < 0.36 ? 2 : 0]); P.mix(x, y, RL.tint[i], 0.3); } if (moor) P.mix(x, y, "#8a6a7a", 0.3);
          if (n3(x / 5 + 1, y / 5, 2) > 0.7) P.dark(x, y, 0.06); }
      }
      else if (!p && l > 0) { P.dark(x, y, 0.13 + 0.06 * (n2(x / 20, y / 20) > .5)); if (!small && n3(x * 1.9, y * 1.9, 1) > 0.8) P.dark(x, y, .16); }
      else if (p && l > 0) { if (c === "meadow") P.light(x, y, .07); else if (c === "pasture") P.light(x, y, .03);
        else if (c === "built") { P.mix(x, y, PAL.ground[0], 0.16); if (n2(x / 6 + 3, y / 6, 2) > 0.62) P.mix(x, y, PAL.ground[(x + y) & 1], 0.55); } }
    }
    if (RL) for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) {                              // the relief's light from the north-west
      const i = y * W + x; if (LV[i] <= 0) continue; const s = (RL.E[i - W - 1] - RL.E[i + W + 1]) * 3;
      if (s > 0) P.light(x, y, Math.min(0.2, s)); else P.dark(x, y, Math.min(0.32, -s));
      if (RL.kind[i] === 2 && cellPar[i] < 0 && (RL.E[i] > 0.93 || season === "winter")) P.mix(x, y, PAL.snow[0], RL.E[i] > 0.93 ? 0.85 : 0.6);
    }
    // terraces from height (a word in the engine; drawn as a step down to the south)
    const face = new Uint8Array(W * H), fh = RL ? 4 : 3;
    if (!small) for (let y = 0; y < H - 1; y++) for (let x = 0; x < W; x++) {
      const l = LV[y * W + x]; if (l <= 1) continue;
      if (lv(x, y + 1) < l && lv(x, y + 1) > 0) { P.put(x, y, snow ? PAL.snow[0] : PAL.rim); for (let k = 1; k <= fh; k++) { if (lv(x, y + k) >= l || y + k >= H) break; P.put(x, y + k, PAL.face[Math.min(3, k - 1 + (x % 3 === 0 ? 1 : 0))]); face[(y + k) * W + x] = 1; } }
      else if (RL && ((lv(x + 1, y) < l && lv(x + 1, y) > 0) || (lv(x - 1, y) < l && lv(x - 1, y) > 0))) P.put(x, y, "#5a9030");
    }
    const trees = [], marks = [];
    const border = (x, y, p) => { for (const [a, b] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const j = at(x + a, y + b); if (j < 0 || parcelOf(j) !== p) return true; } return false; };
    const wildNext = (x, y) => { for (const [a, b] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const j = at(x + a, y + b); if (j >= 0 && cellPar[j] < 0 && LV[j] > 0) return true; } return false; };
    for (const [pid, pts] of Object.entries(area)) {
      const dp = d.parcels[pid] || {}, res = dp.res || {}, c = cov(pid), P0 = V.static.parcels[pid], N = M.nodes[P0.node], B = BIOMES[N.biome], pR = rng(hstr(pid + "|" + (opts.scale || "")));
      const land = pts.filter(([x, y]) => LV[y * W + x] > 0);
      if (!small && ["meadow", "pasture", "built"].includes(c)) for (const [x, y] of land) if (wildNext(x, y)) P.dark(x, y, .14);
      if (c === "field") paintField(P, V, d, pid, dp, land, sc, small, border, n3, pR, trees, marks, sdays, day);
      else if (c === "pasture" || c === "meadow") {
        const g = res.grass ?? 1, flowers = c === "meadow" && (season === "summer" || season === "spring") && g > 0.5;
        for (const [x, y] of land) { const v = n3(x * 1.3, y * 1.3, 1);
          if (flowers && v > 0.84 && !small) P.put(x, y, PAL.flowers[(hstr(x + "," + y) >>> 3) % 4]);
          else if (v > 0.8 && !small) P.dark(x, y, .12);
          if (g < 0.6 && n3(x / 3 + 5, y / 3) < 0.75 - g) P.mix(x, y, "#b8a868", 0.6 * (0.6 - g) / 0.6 + 0.15); }
        if (!small && dp.dung > 5) for (const [x, y] of land) if (pR() < Math.min(0.02, dp.dung / 4000)) { P.put(x, y, "#6b4a2a"); P.put(x + 1, y, "#5a3a20"); }
      } else if (c === "forest" || c === "scrub") {
        // standing trees in proportion to the wood's stock (S/K); where it was felled, stumps; fallen wood by the dead stock;
        // scrub's bushes by its young growth
        const wood = res.wood ?? (c === "forest" ? 0.8 : 0), was = dp.was === "forest" || c === "forest", step = small ? 2 : 3, nz = small ? 3 : 7;
        for (const [x, y] of land) if (x % step === 0 && y % step === 0) { const tx = x + pR() * (step - 1), ty = y + pR() * (step - 1), v = n2(tx / nz, ty / nz);
          if (v < wood) trees.push([tx, ty, small ? 1 : (pR() < 0.6 ? 2 : 3), B.trees[(pR() * B.trees.length) | 0]]);
          else if (!small && was && v < Math.max(wood, 0.85) && pR() < 0.5) { P.put(tx, ty, "#8a6a42"); P.put(tx + 1, ty, "#6b4423"); P.dark(tx, ty + 1, .25); } }
        if (!small) { const dead = res.dead ?? 0, young = res.young ?? (c === "scrub" ? 0.5 : 0);
          for (const [x, y] of land) { const r = pR();
            if (r < 0.006 * dead) { P.put(x, y, "#7a5a3a"); P.put(x + 1, y, "#6b4a2a"); P.put(x + 2, y, "#7a5a3a"); }
            else if (r < 0.006 * dead + (c === "scrub" ? 0.05 : 0.01) * (0.2 + young) && n2(x / 9 + 3, y / 9, 2) > 0.4) {
              for (const [a, b] of [[0, 0], [1, 0], [-1, 0], [0, -1], [1, -1]]) P.put(x + a, y + b, (a + b) < 0 ? "#6c8a40" : PAL.bush[(a + 1) & 1]); P.dark(x + 2, y, .3); P.dark(x, y + 1, .3); } } }
        else if (c === "scrub") for (const [x, y] of land) if (pR() < 0.1) P.put(x, y, PAL.bush[0]);
        for (const [x, y] of land) if (!small && c === "forest" && n3(x * 1.1, y * 1.1, 1) > 0.8) P.dark(x, y, .15);
      } else if (c === "rock") {
        const st = small ? 3 : 6;
        for (const [x, y] of land) { if (x % st || y % st || pR() > 0.45) continue; const bx = x + (pR() * 3 | 0), by = y + (pR() * 3 | 0);
          if (small) { P.put(bx, by, "#e8e8e0"); P.dark(bx + 1, by, .3); continue; }
          const bw = 3 + (pR() * 3 | 0), bh = 2 + (pR() * 2 | 0);
          for (let yy = 0; yy < bh; yy++) for (let xx = 0; xx < bw; xx++) P.put(bx + xx, by + yy, yy === 0 ? "#e8e8e0" : xx === bw - 1 || yy === bh - 1 ? "#9a9a92" : "#c8c8c0");
          for (let xx = 1; xx <= bw; xx++) P.dark(bx + xx, by + bh, .3); }
        if (res.seam != null) for (const [x, y] of land) if (n2(x / 3, y / 3) > 0.92 - 0.25 * res.seam) P.put(x, y, PAL.copper);
      } else if (c === "water" && !N.river[N.pids.indexOf(pid)]) {
        for (const [x, y] of pts) if (n3(x / 2 + 3, y, 1) > 0.97) P.put(x, y, PAL.water.foam);
      }
      if (dp.clearing && !small) for (const [x, y] of land) if (n2(x / 5 + 11, y / 5) < dp.clearing) { P.mix(x, y, PAL.soil[(x + y) & 1], 0.6); if (pR() < 0.01) { P.put(x, y, "#8a6a42"); P.put(x + 1, y, "#6b4423"); } }
      if (dp.fence && dp.fence.built && !small && dp.fence.level > 0) {                              // a fence or a wall round it, by its level
        const col = dp.fence.kind === "stone" ? PAL.fenceStone : PAL.fenceWood; let k = 0, gate = null;
        for (const [x, y] of pts) if (border(x, y, pid)) { k++; if (!gate) gate = [x, y]; if (dp.fence.level === 1 && k % 4 === 0) continue;
          if (gate && Math.abs(x - gate[0]) + Math.abs(y - gate[1]) < 3) { if (dp.fence.gate === "open") continue; P.put(x, y, "#a0703a"); continue; }
          P.put(x, y, col[(x + y) & 1]); }
      }
      if (snow) for (const [x, y] of land) P.mix(x, y, PAL.snow[(x + y) % 3 === 0 ? 1 : 0], n3(x / 4 + 7, y / 4) > 0.3 ? 0.82 : 0.55);
    }
    if (snow) for (let i = 0; i < W * H; i++) if (cellPar[i] < 0 && LV[i] > 0) { const x = i % W, y = (i / W) | 0; P.mix(x, y, PAL.snow[(x + y) % 3 === 0 ? 1 : 0], n3(x / 4 + 7, y / 4) > 0.3 ? 0.8 : 0.5); }
    // the wild country's trees, by each place's character
    const wildStep = small ? 2 : 4;
    for (let gy = 0; gy < H; gy += wildStep) for (let gx = 0; gx < W; gx += wildStep) {
      const x = gx + R() * (wildStep - 1), y = gy + R() * (wildStep - 1), i = at(x, y); if (i < 0 || cellPar[i] >= 0 || LV[i] <= 0 || wet[i]) continue;
      const n = cellNode[i], B = BIOMES[n >= 0 ? M.nodes[nids[n]].biome : "meadow"], z = 26 * Math.max(0.4, Math.min(1, sc * 2)), wild = small || B === BIOMES.woodland ? B.wild : B.wild * 0.6;
      if (RL) { const k = RL.kind[i], fo = RL.F[i];
        if (k === 2 || (k === 3 && R() > 0.08)) continue;
        if (!RL.wood[i] && R() > 0.0015) continue;
        trees.push([x, y, R() < 0.6 ? 2 : 3, LV[i] >= 4 || k === 1 ? "pine" : k === 3 ? "willow" : B.trees[(R() * B.trees.length) | 0] || "oak"]); continue; }
      if (n2(x / z, y / z, 3) < 1 - wild) { if (!small && B === BIOMES.moor && R() < 0.15) { P.put(x, y, "#8a5a7a"); P.put(x + 1, y, "#9a6a8a"); } continue; }
      trees.push([x, y, small ? 1 : (R() < 0.6 ? 2 : 3), B.trees[(R() * B.trees.length) | 0] || "oak"]);
    }
    return { LV, area, trees, marks, season, snow, lv, at, parcelOf, wet, face };
  }
  // a field: strips along its length; the sown share in the crop's colours by stage, the reaped share as stubble with stooks, the
  // rest dug or lying fallow; ditches or terraces for the works done; hoof-marks where a herd trampled it lately
  function paintField(P, V, d, pid, dp, land, sc, small, border, n3, pR, trees, marks, sdays, day) {
    const ang = fieldAngle(pid), ux = Math.cos(ang), uy = Math.sin(ang), sw = small ? Math.max(1.5, 7 * sc) : 7 + (hstr(pid) >>> 9) % 3;
    let u0 = 1e9, u1 = -1e9; for (const [x, y] of land) { const u = x * ux + y * uy; u0 = Math.min(u0, u); u1 = Math.max(u1, u); }
    const n = Math.max(1, Math.ceil((u1 - u0) / sw)), crop = dp.crop, sownN = crop ? Math.round((crop.sown ?? 1) * n) : 0, reapN = crop ? Math.round((crop.reaped || 0) * sownN) : 0;
    const brokenN = Math.round((dp.broken || 0) * n), stubble = !crop && dp.last_crop && dp.last_crop !== "fallow" && dp.fallow_since != null && day - dp.fallow_since <= sdays;
    const pal = crop ? (STAGE_PAL[crop.stage] || (CROP_PAL[crop.family] || CROP_PAL.grain)[crop.stage] || CROP_PAL.grain.green) : null;
    for (const [x, y] of land) {
      if (border(x, y, pid)) { if (n3(x / 2 + 9, y / 2) < 0.75) P.put(x, y, PAL.hedge); if (!small && pR() < 0.02) trees.push([x, y, 1.5, "oak"]); continue; }
      const u = x * ux + y * uy - u0, s = Math.min(n - 1, Math.floor(u / sw)), v = -x * uy + y * ux;
      if (!small && u - s * sw < 1) { P.put(x, y, PAL.balk); continue; }                                     // the balk between strips
      let c;
      if (crop && s < reapN) { c = PAL.stubble[Math.floor(v / 2) & 1]; if (!small && (Math.floor(v) % 6 === 0) && Math.floor(u - s * sw) === 3) marks.push(["stook", x, y]); }
      else if (crop && s < sownN) { c = pal[Math.floor(v / (small ? 1 : 2)) & 1];
        if (!small && crop.stage === "new" && (x * 7 + y * 3) % 5) c = PAL.soil[Math.floor(v / 2) & 1];
        if (!small && (crop.stage === "high" || crop.stage === "ripe") && Math.floor(v) % 3 === 0 && (x + y) % 2 === 0) c = null, P.put(x, y, pal[0]), P.dark(x, y, .14);
        if (!small && crop.weeds && n3(x * 2.1, y * 2.1, 1) > 0.88) c = "#6a9a3a"; }
      else if (s < (crop ? sownN : 0) + brokenN) c = PAL.soil[Math.floor(v / 2) & 1];
      else if (stubble) c = PAL.stubble[Math.floor(v / 2) & 1];
      else { c = n3(x / 2 + 5, y / 2, 1) > 0.5 ? "#9cb860" : "#a8a070"; }                                     // lying fallow: rough grass
      if (c) P.put(x, y, c);
      const sh = ((hstr(pid + s) % 5) - 2) * 0.03; if (sh > 0) P.dark(x, y, sh); else if (sh < 0) P.light(x, y, -sh);
    }
    if (crop && crop.trampled != null && crop.trampled <= 3 && !small) for (const [x, y] of land) if (pR() < 0.01) { P.dark(x, y, .35); P.dark(x + 1, y + 1, .3); }
    const wk = dp.works;
    if (wk && wk.done > 0 && !small) {                                                                      // ditches on wet ground, terraces on hill ground
      const k = Math.round(wk.done * n);
      for (const [x, y] of land) { const u = x * ux + y * uy - u0, s = Math.floor(u / sw);
        if (s >= k) continue;
        if (wk.ground === "wet" && Math.abs(u - s * sw - sw / 2) < 0.6) P.put(x, y, "#5a8aa0");
        if (wk.ground === "hill" && u - s * sw < 1.2) P.put(x, y, "#b8b0a0"); }
    }
  }
  // the day's weather over everything drawn (environment.weather; one for the whole world)
  function weatherOver(P, W, H, kind, R, small) {
    if (!kind || kind === "clear") return;
    if (kind === "fog") { const nz = noise(77); for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) P.mix(x, y, "#e8ecf0", 0.28 + 0.22 * nz(x / 30, y / 18, 2)); return; }
    const n = (W * H) / (kind === "heavy rain" ? 30 : kind === "snow" ? 40 : kind === "gale" ? 90 : 70);
    if (kind === "heavy rain" || kind === "rain") for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) P.dark(x, y, kind === "heavy rain" ? 0.12 : 0.06);
    for (let k = 0; k < n; k++) { const x = (R() * W) | 0, y = (R() * H) | 0;
      if (kind === "snow") { P.put(x, y, "#ffffff"); continue; }
      if (kind === "gale") { for (let j = 0; j < 4; j++) P.mix(x + j, y, "#ffffff", 0.35); continue; }
      const L = small ? 2 : 3; for (let j = 0; j < L; j++) P.mix(x - j, y + j, "#c8dcf0", 0.4); }
  }

  function drawTrees(P, trees, ctx, occ, W, H, R) {
    trees.sort((a, b) => a[1] - b[1]);
    for (const [x, y, r, kind] of trees) {
      const i = ctx.at(x, y); if (i < 0 || occ[i] || ctx.LV[i] <= 0) continue;
      let ok = true; for (let k = -1; k <= 1; k++) { const j = ctx.at(x + k, y + 2); if (j >= 0 && (occ[j] >= 3 || ctx.LV[j] <= 0)) ok = false; }
      if (ok) tree(P, x, y, r, R, kind, ctx.season);
    }
  }
  // a road's way between two points: a curve through waypoints set off to either side (a presentation choice), every 0.7 px
  function windPath(x0, y0, x1, y1, seed, amp) {
    const R = rng(seed), L = Math.hypot(x1 - x0, y1 - y0) || 1, nx = -(y1 - y0) / L, ny = (x1 - x0) / L, k = Math.max(2, Math.min(7, Math.round(L / 40)));
    const pts = [[x0, y0]];
    for (let j = 1; j < k; j++) { const t = j / k, o = (R() - 0.5) * 2 * amp * L * Math.sin(Math.PI * t); pts.push([x0 + (x1 - x0) * t + nx * o, y0 + (y1 - y0) * t + ny * o]); }
    pts.push([x1, y1]);
    const out = [];
    for (let j = 0; j + 1 < pts.length; j++) { const p0 = pts[Math.max(0, j - 1)], p1 = pts[j], p2 = pts[j + 1], p3 = pts[Math.min(pts.length - 1, j + 2)], seg = Math.hypot(p2[0] - p1[0], p2[1] - p1[1]) || 1;
      for (let q = 0; q < seg; q += 0.7) { const t = q / seg, t2 = t * t, t3 = t2 * t, cr = (a, b, c, d) => 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
        out.push([cr(p0[0], p1[0], p2[0], p3[0]), cr(p0[1], p1[1], p2[1], p3[1])]); } }
    out.push([x1, y1]); return out;
  }
  function paintPath(paint, pts, wide, col, keep) { for (const [x, y] of pts) { if (keep && !keep(x, y)) continue; for (let a = 0; a <= wide; a++) for (let b = 0; b <= wide; b++) paint(x + a, y + b, col); } }
  const paintRoad = (P, occ, LV, W, H, face) => (x, y, col) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const i = y * W + x;
    P.put(x, y, LV[i] === 0 ? ((x + y) % 2 ? "#a0662f" : "#8a5a2a") : face && face[i] ? "#e6dcc4" : col); occ[i] = 3; };
  // a dark verge along every road painted (occ 3), so roads read as the backbone
  function verges(P, occ, LV, W, H, t) { for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) { const i = y * W + x; if (occ[i] === 3 || LV[i] <= 0) continue;
    if (occ[i - 1] === 3 || occ[i + 1] === 3 || occ[i - W] === 3 || occ[i + W] === 3) P.dark(x, y, t); } }
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
      const way = e.way;
      if (faint) paintPath(paint, way, 0, PAL.lane, (x, y) => ((x | 0) * 7 + (y | 0) * 3) % 10 < 3 + worn * 8);
      else paintPath(paint, way, r && r.track ? 2 : 1, r && r.track ? PAL.road : PAL.lane);
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
      if (e.place !== nid || ["speech", "work", "store", "make", "build", "give", "take", "trade"].includes(e.kind)) continue;
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
  function at(keys, t) {
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
    const ppl = A.people.map((q) => { const [x, y, moving] = at(q.keys, t), w_ = q.work.find(([a, b]) => t >= a && t < b); return { q, x: x | 0, y: y | 0, moving, act: w_ && w_[2] }; })
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

  // ---------------------------------------------------------------------------------------------------- the region's landscape
  // A presentation choice built from what the engine says about the land between places (ENGINE.md §9): each place stands at the
  // height of its parcels (or, where a world sets no heights, its rock and its name: a crag, a tor, a pass, a moor, a mere); each
  // day's stretch of road stands at its terrain's height and carries its terrain (woodland grows forest, marsh is wet, a river
  // valley is low); a pass is a ridge of mountains with a saddle where the road goes over; narrows are rocks close by the road; a
  // ford or a bridge is a river crossing the road, traced downhill. Between these the land eases from one to the next, with a
  // little noise; it is shaded by its relief. Places are drawn at a fixed scale and roads at a fixed length a day, so a larger
  // world is a larger map to explore, not a smaller drawing.
  const REGION = new WeakMap(), PERDAY = 60, WORLD_SCALE = 0.5;
  const levelOf = (e) => e > 0.78 ? 5 : 1 + Math.max(0, Math.min(3, Math.floor((e - 0.2) / 0.15)));
  const TERRAIN_LAND = { plain: [0.3, 0, 0.1], farmland: [0.3, 0.1, 0.1], woodland: [0.38, 1, 0.2], marsh: [0.1, 0.25, 1], "river valley": [0.15, 0.2, 0.5],
    hills: [0.62, 0.2, 0.1], mountain: [0.88, 0.05, 0] };                                                       // [height, forest, wet]
  function regionPlan(V) {
    let RP = REGION.get(V); if (RP) return RP;
    const M = model(V), ST = V.static, WL = ST.layout.world || {}, nids = Object.keys(ST.nodes).sort(), G = {};
    for (const n of nids) G[n] = geom(V, n);
    const f = WORLD_SCALE, rad = (n) => G[n].land * f, rds = Object.entries(ST.roads).filter(([, r]) => r.a in G && r.b in G);
    const pos = {}; for (const n of nids) pos[n] = [(WL[n] || [500, 350])[0] * 1.6, (WL[n] || [500, 350])[1] * 1.6];
    for (let it = 0; it < 600; it++) {
      for (const [, r] of rds) { const a = pos[r.a], b = pos[r.b], dx = b[0] - a[0], dy = b[1] - a[1], dd = Math.hypot(dx, dy) || 1, k = (dd - (rad(r.a) + rad(r.b) + PERDAY * r.days)) / dd * 0.15;
        a[0] += dx * k; a[1] += dy * k; b[0] -= dx * k; b[1] -= dy * k; }
      for (const x of nids) for (const y of nids) { if (x >= y) continue; const a = pos[x], b = pos[y], dx = b[0] - a[0], dy = b[1] - a[1], dd = Math.hypot(dx, dy) || 0.01, want = rad(x) + rad(y) + 30;
        if (dd < want) { const k = (dd - want) / dd * 0.5; a[0] += dx * k; a[1] += dy * k; b[0] -= dx * k; b[1] -= dy * k; } }
    }
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const n of nids) { const r = rad(n); x0 = Math.min(x0, pos[n][0] - r); y0 = Math.min(y0, pos[n][1] - r); x1 = Math.max(x1, pos[n][0] + r); y1 = Math.max(y1, pos[n][1] + r); }
    const MGN = 70, W = Math.max(420, Math.ceil(x1 - x0 + 2 * MGN)), H = Math.max(280, Math.ceil(y1 - y0 + 2 * MGN));
    const ox = W / 2 - (x0 + x1) / 2, oy = H / 2 - (y0 + y1) / 2; for (const n of nids) pos[n] = [pos[n][0] + ox, pos[n][1] + oy];
    // the anchors: [x, y, sigma, height, forest, wet]
    const A = [], nodeE = {};
    for (const n of nids) {
      const ps = Object.values(ST.parcels).filter((p) => p.node === n), tot = ps.reduce((s, p) => s + (+p.size || 1), 0) || 1;
      const share = (c) => ps.filter((p) => p.cover === c).reduce((s, p) => s + (+p.size || 1), 0) / tot, name = (ST.nodes[n].name + " " + (ST.nodes[n].text || "")).toLowerCase();
      const set = ps.some((p) => (p.height ?? 1) !== 1); let e;
      if (set) e = 0.12 + 0.2 * ps.reduce((s, p) => s + (p.height ?? 1) * (+p.size || 1), 0) / tot;
      else e = 0.32 + 0.3 * share("rock") + 0.1 * share("scrub") + (/crag|tor\b|fell|pass|peak|mount|scar/.test(name) ? 0.32 : 0) + (/moor|heath|high/.test(name) ? 0.15 : 0) - (/mere|fen|marsh|carr|salt|mead|ford/.test(name) ? 0.1 : 0);
      const wet = Math.min(1, share("water") * 1.2 + (/mere|fen|marsh|carr|salt/.test(name) ? 0.5 : 0));
      A.push([pos[n][0], pos[n][1], rad(n) * 0.9 + 12, Math.min(0.95, e), share("forest") * 1.4, wet]); nodeE[n] = Math.min(0.95, e);
      if (e > 0.55) {
        const out = rds.filter(([, r]) => r.a === n || r.b === n).map(([, r]) => { const o = pos[r.a === n ? r.b : r.a]; return Math.atan2(o[1] - pos[n][1], o[0] - pos[n][0]); });
        for (let k = 0; k < 7; k++) { const t = k * 0.8976 + (hstr(n) % 100) / 50; if (out.some((a) => Math.abs(Math.atan2(Math.sin(t - a), Math.cos(t - a))) < 0.55)) continue;
          const rr = rad(n) + 26 + (hstr(n + k) % 20); A.push([pos[n][0] + Math.cos(t) * rr, pos[n][1] + Math.sin(t) * rr, 18, Math.min(1, e + 0.18), 0, 0]); }
      }
    }
    const feats = [], paths = {}, sidx = {};                                                 // each road's way, its stretches on it
    const toW = (n, x, y) => [pos[n][0] + (x - G[n].mid[0]) * f, pos[n][1] + (y - G[n].mid[1]) * f];
    const exitPt = (n, rid) => { const e = G[n].exits.find((q) => q.rid === rid); return e ? toW(n, e.fx, e.fy) : pos[n]; };
    for (const [rid, r] of rds) {
      const A0 = exitPt(r.a, rid), B0 = exitPt(r.b, rid), way = paths[rid] = windPath(A0[0], A0[1], B0[0], B0[1], hstr(rid), 0.1);
      let i0 = way.findIndex(([x, y]) => Math.hypot(x - pos[r.a][0], y - pos[r.a][1]) > rad(r.a)); if (i0 < 0) i0 = 0;
      let i1 = way.length - 1; while (i1 > i0 && Math.hypot(way[i1][0] - pos[r.b][0], way[i1][1] - pos[r.b][1]) <= rad(r.b)) i1--;
      const all = r.stretches && r.stretches.length ? r.stretches : [{ terrain: r.terrain }];
      sidx[rid] = all.map((_, k) => Math.round(i0 + (i1 - i0) * (k + 0.5) / all.length));
      all.forEach((st, k) => {
        const j = sidx[rid][k], [x, y] = way[j], q0 = way[Math.max(0, j - 4)], q1 = way[Math.min(way.length - 1, j + 4)], L = Math.hypot(q1[0] - q0[0], q1[1] - q0[1]) || 1, ux = (q1[0] - q0[0]) / L, uy = (q1[1] - q0[1]) / L;
        const T = TERRAIN_LAND[st.terrain || r.terrain || "farmland"] || TERRAIN_LAND.farmland;
        A.push([x, y, 28, T[0], T[1], T[2]]);
        for (const lm of st.landmarks || []) { const kd = lm.kind || lm, h = (hstr(rid + kd) % 2) ? 1 : -1;
          if (kd === "pass") { A.push([x - uy * 30, y + ux * 30, 20, 1.0, 0, 0], [x + uy * 30, y - ux * 30, 20, 1.0, 0, 0], [x - uy * 55, y + ux * 55, 18, 0.9, 0, 0], [x + uy * 55, y - ux * 55, 18, 0.9, 0, 0]); }
          if (kd === "narrows") { A.push([x - uy * 9, y + ux * 9, 6, 0.75, 0, 0], [x + uy * 9, y - ux * 9, 6, 0.75, 0, 0]); }
          if (kd === "hollow") A.push([x + uy * 10 * h, y - ux * 10 * h, 10, 0.12, 0.4, 0.4]);
          feats.push({ rid, k, kind: kd, x, y, ux, uy, state: lm.state }); }
      });
    }
    // the fields: height, forest, wet, and the kind of wild land
    const E = new Float32Array(W * H), F = new Float32Array(W * H), Wt = new Float32Array(W * H), kind = new Uint8Array(W * H);
    const nA = noise(M.seed ^ 31), nB = noise(M.seed ^ 37), nC = noise(M.seed ^ 41), nU = noise(M.seed ^ 43);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      let sw = 0.12, se = 0.12 * 0.3, sf = 0.12 * 0.15, sx = 0.12 * 0.1;
      for (const [ax, ay, sg, e, fo, we] of A) { const dd = (x - ax) ** 2 + (y - ay) ** 2; if (dd > 25 * sg * sg) continue; const w = Math.exp(-dd / (2 * sg * sg)); sw += w; se += w * e; sf += w * fo; sx += w * we; }
      let e = se / sw + (nA(x / 70, y / 70, 3) - 0.5) * 0.14 + (nU(x / 170, y / 170, 2) - 0.5) * 0.34;
      if (e > 0.6) e += (1 - Math.abs(nB(x / 16, y / 16, 3) * 2 - 1) - 0.5) * 0.3 * Math.min(1, (e - 0.6) / 0.3);   // ridged peaks
      const i = y * W + x; E[i] = e; F[i] = sf / sw + (nC(x / 40, y / 40, 2) - 0.5) * 0.5; Wt[i] = sx / sw + (nC(x / 30 + 9, y / 30, 2) - 0.5) * 0.3;
    }
    for (const n of nids) { const r = rad(n), [px, py] = pos[n];                                 // a place stands level on its own ground
      for (let y = Math.max(0, py - r * 1.4 | 0); y < Math.min(H, py + r * 1.4); y++) for (let x = Math.max(0, px - r * 1.4 | 0); x < Math.min(W, px + r * 1.4); x++) {
        const dd = Math.hypot(x - px, y - py) * (0.8 + 0.4 * nA(x / 25 + 3, y / 25, 2)), t = Math.max(0, Math.min(1, (r * 1.35 - dd) / (r * 0.4))); if (t <= 0) continue; const i = y * W + x, sm = t * t * (3 - 2 * t); E[i] = E[i] * (1 - sm) + nodeE[n] * sm; } }
    const level = new Int8Array(W * H);
    for (let i = 0; i < W * H; i++) { const e = E[i]; level[i] = levelOf(e); kind[i] = e > 0.78 ? 2 : e > 0.56 ? 1 : (Wt[i] > 0.55 && e < 0.35) ? 3 : 0; }
    // territories and the parcels of each place at its spot
    const n1 = noise(M.seed ^ 11), cellNode = new Int16Array(W * H).fill(-1), cellPar = new Int16Array(W * H).fill(-1);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const jx = x + (n1(x / 40, y / 40, 3) - .5) * 80, jy = y + (n1(x / 40 + 7, y / 40, 3) - .5) * 80; let best = -1, bd = 1e18;
      for (let i = 0; i < nids.length; i++) { const dd = ((jx - pos[nids[i]][0]) ** 2 + (jy - pos[nids[i]][1]) ** 2) / (rad(nids[i]) + 40); if (dd < bd) { bd = dd; best = i; } }
      cellNode[y * W + x] = best;
      const n = nids[best], g = G[n], lx = Math.round(g.mid[0] + (x - pos[n][0]) / f), ly = Math.round(g.mid[1] + (y - pos[n][1]) / f);
      if (lx >= 0 && ly >= 0 && lx < g.W && ly < g.H) cellPar[y * W + x] = g.REG[ly * g.W + lx];
      if (Math.hypot(x - pos[n][0], y - pos[n][1]) < rad(n) * 1.15) F[y * W + x] -= 0.35;   // open ground round a place
    }
    // rivers where roads cross water (a ford, a bridge), traced downhill from the crossing, and a little way up to their source
    const rivers = [], sinks = [];
    for (const n of nids) for (const [pid, P0] of Object.entries(ST.parcels)) if (P0.node === n && P0.cover === "water") { const i = M.nodes[n].pids.indexOf(pid); if (i >= 0 && G[n].area[i].length) { const [cx, cy] = G[n].centre[i]; sinks.push([pos[n][0] + (cx - G[n].mid[0]) * f, pos[n][1] + (cy - G[n].mid[1]) * f]); } }
    for (const a of A) if (a[5] >= 0.9) sinks.push([a[0], a[1]]);
    for (const ft of feats) if (ft.kind === "ford" || ft.kind === "bridge") {
      const tR = rng(hstr(ft.rid + ft.k)), px0 = -ft.uy, py0 = ft.ux;
      const target = (sgn) => { let best = null, bd = 1e18; for (const [sx, sy] of sinks) { const v = (sx - ft.x) * px0 + (sy - ft.y) * py0, dd = Math.hypot(sx - ft.x, sy - ft.y); if (sgn * v > 4 && dd < bd && dd > 20) { bd = dd; best = [sx, sy]; } }
        return best || [ft.x + sgn * px0 * 400, ft.y + sgn * py0 * 400]; };
      const run = (sgn, steps) => { const out = [], [tx, ty] = target(sgn); let x = ft.x, y = ft.y, hd = Math.atan2(sgn * py0, sgn * px0);
        for (let s = 0; s < steps; s++) { let dd = Math.atan2(ty - y, tx - x) - hd; dd = Math.atan2(Math.sin(dd), Math.cos(dd));
          hd += Math.max(-0.12, Math.min(0.12, dd * 0.15)) + (tR() - 0.5) * 0.35; x += Math.cos(hd) * 1.5; y += Math.sin(hd) * 1.5;
          if (x < 1 || y < 1 || x > W - 2 || y > H - 2 || Math.hypot(tx - x, ty - y) < 6) break; out.push([x, y]); }
        return out; };
      const down = run(1, 260), up = run(-1, 50);
      rivers.push({ pid: null, pids: [], n: null, half: 1.8, line: up.reverse().concat([[ft.x, ft.y]], down) });
    }
    const tint = new Uint32Array(W * H), rgb = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
    const base = nids.map((n) => rgb(BIOMES[M.nodes[n].biome].grass[0][0]));
    for (let y = 0; y < H; y += 1) for (let x = 0; x < W; x += 1) { let sw = 0, r = 0, g = 0, b = 0;
      nids.forEach((n, k) => { const sg = rad(n) + 90, w = Math.exp(-((x - pos[n][0]) ** 2 + (y - pos[n][1]) ** 2) / (2 * sg * sg)) + 1e-6; sw += w; r += w * base[k][0]; g += w * base[k][1]; b += w * base[k][2]; });
      tint[y * W + x] = (Math.round(r / sw) << 16) | (Math.round(g / sw) << 8) | Math.round(b / sw); }
    const wood = new Uint8Array(W * H), nW = noise(M.seed ^ 2);                                  // woods: masses where the land is wooded
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const i = y * W + x; wood[i] = nW(x / 30, y / 30, 3) < 0.2 + F[i] * 0.55 ? 1 : 0; }
    RP = { W, H, pos, f, G, nids, A, feats, E, F, Wt, kind, level, cellNode, cellPar, rivers, rad, tint, paths, sidx, wood };
    REGION.set(V, RP); return RP;
  }
  const NREL = new WeakMap();
  function nodeRelief(V, nid) {
    let cache = NREL.get(V); if (!cache) NREL.set(V, cache = {}); if (cache[nid]) return cache[nid];
    const RP = regionPlan(V), G = geom(V, nid), W = G.W, H = G.H, f = RP.f, [px, py] = RP.pos[nid], M = model(V), nW = noise(M.seed ^ 2);
    const E = new Float32Array(W * H), F = new Float32Array(W * H), Wt = new Float32Array(W * H), kind = new Uint8Array(W * H), level = new Int8Array(W * H), tint = new Uint32Array(W * H), wood = new Uint8Array(W * H);
    const at = (A, x, y) => A[Math.max(0, Math.min(RP.H - 1, y | 0)) * RP.W + Math.max(0, Math.min(RP.W - 1, x | 0))];
    const bil = (A, x, y) => { const x0 = Math.floor(x), y0 = Math.floor(y), fx = x - x0, fy = y - y0; return at(A, x0, y0) * (1 - fx) * (1 - fy) + at(A, x0 + 1, y0) * fx * (1 - fy) + at(A, x0, y0 + 1) * (1 - fx) * fy + at(A, x0 + 1, y0 + 1) * fx * fy; };
    const own = levelOf(bil(RP.E, px, py));
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const i = y * W + x, rx = px + (x - G.mid[0]) * f, ry = py + (y - G.mid[1]) * f, e = bil(RP.E, rx, ry);
      E[i] = e; F[i] = bil(RP.F, rx, ry); Wt[i] = bil(RP.Wt, rx, ry); tint[i] = at(RP.tint, rx, ry);
      level[i] = G.REG[i] >= 0 ? own : levelOf(e); kind[i] = e > 0.78 ? 2 : e > 0.56 ? 1 : (Wt[i] > 0.55 && e < 0.35) ? 3 : 0;
      wood[i] = nW(rx / 30, ry / 30, 3) < 0.2 + F[i] * 0.55 ? 1 : 0;
    }
    const rivers = RP.rivers.map((c) => ({ pid: null, pids: [], n: null, half: Math.max(2, c.half / f * 0.8), line: c.line.map(([x, y]) => [G.mid[0] + (x - px) / f, G.mid[1] + (y - py) / f]).filter(([x, y]) => x > -30 && y > -30 && x < W + 30 && y < H + 30) })).filter((c) => c.line.length > 2);
    return (cache[nid] = { E, F, Wt, kind, level, tint, wood, rivers });
  }
  function peaks(P, RL, cellPar, occ, W, H, snowy, k) {                                          // peaks where the land is mountain
    const pk = [], sx = Math.round(9 * k), sy = Math.round(7 * k);
    for (let y = sy; y < H - 2; y += sy) for (let x = sx; x < W - sx; x += sx) { const i = y * W + x; if (RL.kind[i] !== 2 || cellPar[i] >= 0 || occ[i]) continue;
      const e = RL.E[i]; if ([[-sx * 0.7, 0], [sx * 0.7, 0], [0, -sy * 0.7], [0, sy * 0.7]].some(([a, b]) => RL.E[Math.round(y + b) * W + Math.round(x + a)] > e)) continue;
      pk.push([x, y, Math.round((8 + Math.min(1, (e - 0.78) / 0.25) * 10) * k)]); }
    pk.sort((a, b) => a[1] - b[1]).forEach(([x, y, h]) => peak(P, x, y, h, h > 13 * k || snowy));
  }
  // a mountain peak (the night village's ranges: a lit side and a shaded one), snow on its top when high or in winter
  function peak(P, x, y, h, snow) {
    x |= 0; y |= 0; const w = Math.round(h * 1.1);
    for (let k = 0; k < h; k++) { const half = Math.round(k * w / (2 * h)); for (let dx = -half; dx <= half; dx++) {
      const lit = dx < 0, top = k < h * 0.35 && snow, c = top ? (lit ? "#f4f6fa" : "#cfd8e4") : lit ? (k % 3 ? "#a8a49a" : "#b8b4aa") : (k % 3 ? "#7e7a70" : "#8a867c");
      P.put(x + dx, y - h + k, c); } }
    for (let dx = -Math.round(w / 2); dx <= Math.round(w / 2); dx++) P.dark(x + dx, y, 0.2);
  }

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

  G.C2Pixel = { world, node, nodeAt, plan, geom, biomeOf, looks, hstr, rng, noise, PAL, BIOMES };
})(typeof window !== "undefined" ? window : globalThis);
