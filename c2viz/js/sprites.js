// c2viz/js/sprites.js: trees by kind and season; people (a small figure for the region, a villager close up, with their state and the tool of their act); tools; graves, goods, bones.
(function (X) {
  "use strict";
  const { PAL, looks } = X;
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
  function tool(P, x, y, k) { for (const [dx, dy, c] of TOOLS[k] || []) P.put(x + dx, y + dy, c); }
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
  Object.assign(X, { LEAF, tree, person, dot, TOOLS, tool, BODY5, CHILD5, villager, bubble, graveBig, sackBig, bonesBig });
})(C2X);
