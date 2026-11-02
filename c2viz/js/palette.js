// c2viz/js/palette.js: colours: land, water, rock, the places' characters (biomes, read from their parcels), villagers' looks (site/assets/core/villagers.js).
(function (X) {
  "use strict";
  const { hstr } = X;
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
  // the ground's colour by the generator's terrain (a generated world's ground truth, ENGINE.md §12)
  const TERRAIN_TINT = { "river floodplain": "#7cc04c", "river terrace": "#8cc452", "clay vale": "#6ca43a", "lowland loam": "#86ba48", "sandy heath": "#a89a5c",
    "chalk down": "#a8c878", woodland: "#5f9a36", hills: "#8e9a58", "upland pasture": "#9aaa58", moor: "#8a7a5a", fen: "#6a9a6a", coast: "#d8c890",
    saltmarsh: "#8aa080", rock: "#9a958a", "deep forest": "#4e8a30", water: "#3a7aa0" };
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
  Object.assign(X, { PAL, BIOMES, TERRAIN_TINT, biomeOf, HAIR, SKIN, CLOTHES, TROUSERS, looks, ROOF, WALL });
})(C2X);
