// Shared pieces of the run page: tiny pixel art, the village buildings as icons, and per-day facts about the run (laws,
// births, deaths, headlines) that the shell's clock and the front page both use.
import { moodAt } from "../core/model.js";
import { BUILDINGS } from "../scene.js";

import { esc, clip } from "../core/text.js";
export { esc, clip };
export const andList = (xs) => xs.length < 2 ? xs.join("") : xs.slice(0, -1).join(", ") + " and " + xs[xs.length - 1];

// ------------------------------------------------------------------ tiny pixel art (rows of letters -> inline svg)
export function pix(rows, pal, size, cls = "px") {
  const w = rows[0].length, h = rows.length; let r = "";
  rows.forEach((row, y) => { for (let x = 0; x < w;) { let n = 1; while (x + n < w && row[x + n] === row[x]) n++; if (pal[row[x]]) r += `<rect x="${x}" y="${y}" width="${n}" height="1" fill="${pal[row[x]]}"/>`; x += n; } });
  return `<svg class="${cls}" width="${size * w / h}" height="${size}" viewBox="0 0 ${w} ${h}" shape-rendering="crispEdges" aria-hidden="true">${r}</svg>`;
}
const ICONS = {
  front: [["....ff....", "...fRR....", "...f......", "..LLLL....", ".LRRRRL.LL", "LRRRRRRLRR", ".wbwwbw.wb", ".wwwdww.ww", "gggggggggg"],
    { f: "#6b4423", R: "#c8553d", L: "#e07a5a", w: "#f2e8d4", b: "#7aaabe", d: "#6b4423", g: "#6a9a3a" }],
  people: [["...rrrr...", "..rRRRRr..", ".rRRRRRRr.", "rRRRRRRRRr", ".wwwwwwww.", ".wbwwwwbw.", ".wwwddwww.", ".wwwddwww."],
    { r: "#9a3a24", R: "#c8553d", w: "#f2e8d4", b: "#ffd27a", d: "#6b4423" }],
  letters: [["eeeeeeeeee", "eEeeeeeeEe", "eeEeeeeEee", "eeeEeeEeee", "eeeeEEeeee", "eeeeeeeeee", "eeeeeeeeee"], { e: "#f6ead0", E: "#c8553d" }],
  square: [["RWRWRWRWRW", "RWRWRWRWRW", ".h......h.", ".h.yyoo.h.", ".hwwwwwwh.", ".h......h.", "gggggggggg"],
    { R: "#c8553d", W: "#f6ead0", h: "#8a5a2a", y: "#e8c060", o: "#e8803a", w: "#b8865a", g: "#cdb88a" }],
  crown: [["Y.Y..Y.Y", "YYY.YYYY", "YYYYYYYY", "YrYYbYYY", "YYYYYYYY", "yyyyyyyy"], { Y: "#e8c060", y: "#c99a3a", r: "#c8553d", b: "#4878c8" }],
  coins: [["..yyyy....", ".yYYYYy...", ".yyyyyy...", ".yYYYYy.yy", ".yyyyyyyYY", ".yYYYYyyyy", ".yyyyyyyYY", "..yyyy..yy"], { Y: "#e8c060", y: "#c99a3a" }],
  scroll: [[".wwwwwww.", "wWWWWWWWw", ".WkkkkkW.", ".WWWWWWW.", ".WkkkkWW.", ".WWWWWWW.", ".WkkkkkW.", "wWWWWWWWw", ".wwwwwww."], { w: "#b8865a", W: "#f6ead0", k: "#6b4423" }],
  home: [["...rr...", "..rRRr..", ".rRRRRr.", "rRRRRRRr", ".wbwwbw.", ".wwddww."], { r: "#9a3a24", R: "#c8553d", w: "#f2e8d4", b: "#ffd27a", d: "#6b4423" }],
  data: [["kkkkkkkk", "kWWWWWWk", "kWkkWkkk", "kWWWWWWk", "kWkWkkWk", "kWWWWWWk", "kkkkkkkk"], { k: "#8a8a94", W: "#e0d8c8" }],
};
export const icon = (k, size) => pix(ICONS[k][0], ICONS[k][1], size);
// a P (put/get/dark/flush) over an existing canvas, so the shared BUILDINGS can be drawn on top of a generated map or alone
export function painter(cv) {
  const g = cv.getContext("2d", { willReadFrequently: true }), W = cv.width, H = cv.height, img = g.getImageData(0, 0, W, H), d = img.data;
  const put = (x, y, c) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const n = parseInt(c.slice(1), 16), i = (y * W + x) * 4; d[i] = n >> 16 & 255; d[i + 1] = n >> 8 & 255; d[i + 2] = n & 255; d[i + 3] = 255; };
  const get = (x, y) => { const i = ((y | 0) * W + (x | 0)) * 4; return (d[i] << 16) | (d[i + 1] << 8) | d[i + 2]; };
  const dark = (x, y, t) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const i = (y * W + x) * 4; for (let k = 0; k < 3; k++) d[i + k] *= 1 - t; };
  return { put, get, dark, flush: () => g.putImageData(img, 0, 0), W, H };
}
// one of the village buildings drawn into a small canvas (the section icons are the buildings themselves)
export function buildingIcon(kind, w = 14, h = 14) {
  const cv = document.createElement("canvas"); cv.width = w; cv.height = h; cv.className = "bico";
  const P = painter(cv), b = BUILDINGS[kind]; b.draw(P, (w - b.w) >> 1, h - b.h - 1); P.flush(); return cv;
}

// ------------------------------------------------------------------ per-day facts
export function runFacts(S, D) {
  const life = (D.truth && D.truth.life) || {}, LAST = S.lastRound;
  const born = new Map(), birthsAt = [], deathsAt = [], lawsNewAt = [];
  for (let r = 0; r <= LAST; r++) { birthsAt[r] = []; deathsAt[r] = []; lawsNewAt[r] = []; }
  for (const [id, i] of S.arrives) born.set(id, S.roundAt[i]);
  S.events.forEach((e, i) => { const r = S.roundAt[i], d = e.data || {};
    if (r == null || r > LAST) return;
    if (e.type === "birth") birthsAt[r].push(d);
    if (e.type === "disabled" || e.type === "departure") deathsAt[r].push({ who: d.agent || e.agent, cause: d.cause || e.type });
    if (e.type === "enact" && e.agent !== "constitution") lawsNewAt[r].push(d); });
  const cum = (arr) => { let s = 0; return arr.map((x) => (s += x.length)); };
  const status = (id, r) => born.has(id) && born.get(id) > r ? "unborn" : moodAt(S, id, r);
  const present = (id, r) => !(born.has(id) && born.get(id) > r);
  const sprite = (id) => { const a = S.A.get(id); return a ? { id, cls: a.cls, maker: (a.rights || []).includes("maker"), child: !!(life.parent || {})[id] } : { id: id || "?", cls: "observer" }; };
  // what the papers led with that day: the first real line of each edition
  function papers(r) {
    const out = [];
    for (const it of S.items) { if (it.round !== r || it.kind !== "media") continue;
      if (/official record/i.test(it.label || "")) continue;
      let line = it.head; if (!line) { const ls = String(it.text || "").split("\n").map((s) => s.replace(/^[-•*\s]+/, "").trim()).filter((s) => /[a-z]/.test(s));
        line = ls.find((s, k) => k > 0 && !/^(headlines?|round \d+)$/i.test(s)) || ls[0]; }
      if (line && !out.some((o) => o.paper === (it.label || "Paper"))) out.push({ paper: it.label === "Front page" ? `${it.who}'s notice` : it.label || "Paper", who: it.who, line: clip(line, 170) }); }
    return out.slice(0, 3);
  }
  // one-line summary of a day for the story so far, the ticker and the strip's tooltips
  function daySummary(r) {
    const parts = [];
    if (lawsNewAt[r].length) parts.push(`${lawsNewAt[r].length === 1 ? lawsNewAt[r][0].law + " " + (lawsNewAt[r][0].title || "") + " becomes law" : lawsNewAt[r].length + " new laws"}`);
    const h = S.heads[r] || { items: [] };
    if (h.items.some((x) => x.k === "vetoed")) parts.push("a Board veto");
    if (h.items.some((x) => x.k === "raid")) parts.push("a raid");
    if (h.items.some((x) => x.k === "tribute")) parts.push("tribute demanded");
    if (deathsAt[r].length) parts.push(`${deathsAt[r].length} ${deathsAt[r].length === 1 ? "death" : "deaths"}`);
    if (birthsAt[r].length) parts.push(`${birthsAt[r].length} ${birthsAt[r].length === 1 ? "birth" : "births"}`);
    return parts;
  }
  return { life, born, birthsAt, deathsAt, lawsNewAt, birthsCum: cum(birthsAt), deathsCum: cum(deathsAt), status, present, sprite, papers, daySummary };
}
