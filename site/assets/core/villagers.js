// Villagers: the pixel-art people of the Harvest design. One flat-block sprite per agent: its class shows in a hat and a prop
// held to one side (fixed colours), its own hair, skin and clothes come from its name. Moods: ok, happy, sad, gone (a grave).
//
// Maps are 12 wide; "." is empty and every other letter a colour (FIX: class props, fixed; H S C D P: the agent's own hair,
// skin, clothes, clothes shadow, trousers). Class overrides are keyed by the bare body's rows; -2 and -1 are the rows above
// the head where hats sit.

const hash = (s) => { let h = 2166136261; for (const c of String(s)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
export const MOODS = ["ok", "happy", "sad", "gone"];

const BODY = ["............", "............", "...HHHHHH...", "..HHHHHHHH..", "..HSSSSSSH..", "..SSSSSSSS..", "..SESSSSES..",
  "..bSSSSSSb..", "...SSMMSS...", "....SSSS....", "...CCCCCC...", "..SCCCCCCS..", "..SCCCCCCS..", "...PPPPPP...", "...PP..PP...",
  "...FF..FF..."];
const CHILD = ["..HHHHHH..", ".HHHHHHHH.", ".HSSSSSSH.", ".SESSSSES.", ".bSSmmSSb.", "..CCCCCC..", ".SCCCCCCS.", "..CCCCCC..",
  "...P..P...", "...F..F..."];
const GRAVE = ["....GGGG....", "...GGGGGG...", "..GGGkkGGG..", "..GGkkkkGG..", "..GGGkkGGG..", "..GGGkkGGG..", "..GGGGGGGG..",
  "..GGGGGGGG..", "..GGGGGGGG..", ".gggggggggg.", ".gXggggggYg."];

const FIX = { E: "#2a1a10", b: "#f2a08a", M: "#c8553d", m: "#7a2a1c", F: "#4a2f17", Y: "#e8c060", y: "#c99a3a", n: "#9aa0a8",
  h: "#8a5a2a", K: "#2b1d14", R: "#c8553d", W: "#f6ead0", I: "#ead2a0", l: "#5a4632", g: "#2a1a10", L: "#e4ecef", G: "#7ac04a",
  o: "#a8dc88", q: "#cdb98e", N: "#4a4a5a", w: "#8a8a92", r: "#a83434", O: "#e8803a", T: "#4a2f17", V: "#e8b83c", A: "#5a9a9a",
  U: "#7a6a8a", B: "#4878c8", Z: "#e8b83c", X: "#34333c", c: "#cfe6f8", j: "#4878c8", p: "#e8905a", a: "#e85a8a", u: "#ffffff",
  v: "#bcdcf4", d: "#7fc4ff" };
const GRAVE_C = { G: "#a8a29a", k: "#7a746c", g: "#6a9a3a", X: "#f2d0e0", Y: "#e8c060" };

const CLASS = {
  worker: { "-2": "....YYYY....", "-1": "...YYYYYY...", 0: ".yyyyyyyyyy.", 4: "..SESSSSESnn", 5: "..bSSSSSSbh.", 6: "...SSMMSS.h.",
    7: "....SSSS..h.", 8: "...CDCCDC.h.", 9: "..SCDCCDCSh.", 10: "..SCCCCCCSh.", 11: "...PPPPPP.h.", 12: "...PP..PP.h.", 13: "...FF..FF.h." },
  legislator: { "-2": "..KK....KK..", "-1": "..KKKKKRKK..", 0: ".KKKKKKKKKK.", 8: "...CCWWIIIII", 9: "..SCCWWIlllI", 10: "..SCCCCIIIII",
    11: "...PPPPIlllI", 12: "...PP..IIrII" },
  scientist: { 0: "..H.HHHH.H..", 4: "..gEgSSgEg..", 5: "..bSSSSSSb.o", 6: "...SSMMSS.o.", 7: "....SSSS..q.", 8: "...LCCCCL.qq",
    9: "..SLCCCCLSGG", 10: "..SLCCCCLSGG", 11: "...LLLLLL..." },
  media: { "-2": "....NNNN....", "-1": "...KKKKWK...", 0: ".NNNNNNNNNN.", 7: "....SSSSXXW.", 8: "...CCCCXXXXX", 9: "..SCCCCXcjXX",
    10: "..SCCCCXjjXX" },
  board: { "-2": "...Z.ZZ.Z...", "-1": "...ZRZZBZ...", 8: "..rCCCCCCr..", 9: ".rSCCZZCCSr.", 10: ".rSCCCCCCSr.", 11: ".rrPPPPPPrr.",
    12: ".rrPP..PPrr." },
  fixer: { "-2": "....OOOO....", "-1": "...OOOOOO...", 0: "..OOOOOOOO..", 1: ".OOOOOOOOOO.", 6: "...SSMMSSw.w", 7: "....SSSS.www",
    8: "...CCCCCC.w.", 9: "..SCCCCCCSw.", 11: "...TTVTTT..." },
  maker: { "-1": "...AAAAAA...", 0: "..AAAAAAAA..", 1: "..AAAAAAAAAA", 2: "..ASSSSSSA..", 5: "..bSSSSSSbp.", 6: "...SSMMSSaaa",
    7: "....SSSS.vvv", 8: "...CCCCCCuuu", 9: "..SCCCCCCSuu", 10: "..SCCCCCCuuu", 11: "...PPPPPPvvv" },
  observer: { "-1": "...UUUUUU...", 0: "..UUUUUUUU..", 1: "..UUUUUUUU..", 2: "..UUSSSSUU..", 3: "..USSSSSSU..", 4: "..UESSSSEU..",
    5: "..USSSSSSU..", 6: "..USSMMSSU..", 7: "..UUSSSSUU..", 8: "..UUUUUUUU..", 9: ".UUUUUUUUUU.", 10: ".UUUUUUUUUU.", 11: "..UUUUUUUU.." },
};
// moods: "_" keeps the pixel underneath
const MOOD = { happy: { 6: "___SMMMMS___" }, sad: { 4: "_d__________", 5: "_d__________", 6: "_____E______" } };
const MOOD_CHILD = { happy: { 4: "___mmmm___" }, sad: { 2: "d_________", 3: "d_________", 4: "____m_____" } };

const HAIR = ["#2a1a10", "#7a4a24", "#c8553d", "#e8c060", "#4a2a5a", "#d8d0c0", "#a0662f", "#5a3a1c"];
const SKIN = ["#f8dcc0", "#f6c99f", "#e0a878", "#c8906a", "#9a6a4a", "#6a4a32"];
const CLOTHES = ["#6a9a3a", "#4878c8", "#c8553d", "#7a5aa0", "#e8a33c", "#3a8a8a", "#a0662f", "#d07aa0", "#8a9a3a"];
const TROUSERS = ["#5a4a3a", "#3a3a4a", "#4a5a8a", "#6a5a4a"];
const dk = (h, t) => "#" + [1, 3, 5].map((i) => Math.round(parseInt(h.substr(i, 2), 16) * (1 - t)).toString(16).padStart(2, "0")).join("");

// which sprite an agent gets: a child of the run, a Maker (a worker with the maker right), else its class
export function kindOf(a) {
  if (!a) return "agent";
  if (a.child) return "child";
  if (a.maker && (a.cls === "worker" || a.cls === "agent")) return "maker";
  return CLASS[a.cls] ? a.cls : "agent";
}
export function looksOf(id) {
  const k = hash(id);
  const C = CLOTHES[(k >>> 8) % CLOTHES.length];
  return { H: HAIR[k % HAIR.length], S: SKIN[(k >>> 4) % SKIN.length], C, D: dk(C, 0.25), P: TROUSERS[(k >>> 12) % TROUSERS.length] };
}

function grid(base, layers, shift) {
  const m = base.map((r) => r.split(""));
  for (const over of layers) for (const r in over) [...over[r]].forEach((ch, x) => { if (ch !== "_") m[Number(r) + shift][x] = ch; });
  return m;
}
// one <rect> per horizontal run of a colour
function rects(m, colours, dx = 0, dy = 0) {
  let out = "";
  m.forEach((row, y) => {
    for (let x = 0; x < row.length;) {
      const col = row[x] === "." ? null : colours[row[x]];
      let w = 1; while (x + w < row.length && row[x + w] === row[x]) w++;
      if (col) out += `<rect x="${x + dx}" y="${y + dy}" width="${w}" height="1" fill="${col}"/>`;
      x += w;
    }
  });
  return out;
}

// the sprite's pixels in a 16 x 16 box (the 12-wide body centred, feet on the bottom row)
export function villagerPixels(a, mood = "ok") {
  if (mood === "gone") return rects(GRAVE.map((r) => r.split("")), GRAVE_C, 2, 5);
  const kind = kindOf(a), colours = Object.assign({}, FIX, looksOf(a ? a.id : "?"));
  if (kind === "child") return rects(grid(CHILD, [MOOD_CHILD[mood] || {}], 0), colours, 3, 6);
  if (kind === "observer") colours.S = "#f6c99f";
  return rects(grid(BODY, [CLASS[kind] || {}, MOOD[mood] || {}], 2), colours, 2, 0);
}
export function villagerSymbol(a, mood, id) {
  return `<symbol id="${id}" viewBox="0 0 16 16" shape-rendering="crispEdges">${villagerPixels(a, mood)}</symbol>`;
}
export function villagerSvg(a, mood = "ok", size = 48, cls = "m") {
  return `<svg class="${cls}" width="${size}" height="${size}" viewBox="0 0 16 16" shape-rendering="crispEdges" aria-hidden="true">${villagerPixels(a, mood)}</svg>`;
}
