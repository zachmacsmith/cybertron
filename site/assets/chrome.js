// The v2 site's header (brand + nav) and footer, plus a few helpers every page uses. Pair with base.css.
//
//   import { chrome } from "./assets/chrome.js";
//   chrome({ active: "runs" });                 // "home" | "experiment" | "runs" | "notes"
//   chrome({ active: "home", over: true });     // the header floats transparent over a hero (home page)

export const GITHUB = "https://github.com/zachmacsmith/cybertron";
export const DATASET_URL = "https://huggingface.co/datasets/zachmacsmith/charter-runs";
export const siteUrl = (p) => new URL("../" + p, import.meta.url).href;   // a path from the v2 site root

export { esc } from "./core/text.js";
import { esc } from "./core/text.js";

// the brand mark: two towers of the town, stone with a shaded side, windows, battlements, one lit window and a door; 12 x 12
// (site/favicon.svg is the same picture)
const CASTLE = ["............", ".T.T.T......", ".TTTTs......", ".TwTws......", ".TYTTs......", ".TTTTs.T.T..",
  ".TwTws.TTTs.", ".TTTTs.TwTs.", ".TTTTs.TTTs.", ".TwTws.TTTs.", ".TTDTs.TwTs.", ".TTDTs.TTTs."];
const HC = { T: "#f0e8dc", s: "#c8b8a0", w: "#8a5a3a", Y: "#e8c060", D: "#6b4423" };
export function brandMark(size = 32) {
  let r = "";
  CASTLE.forEach((row, y) => [...row].forEach((ch, x) => { if (HC[ch]) r += `<rect x="${x}" y="${y}" width="1" height="1" fill="${HC[ch]}"/>`; }));
  return `<svg width="${size}" height="${size}" viewBox="0 0 12 12" shape-rendering="crispEdges" aria-hidden="true">${r}</svg>`;
}

export function chrome({ active = "", over = false, links = {} } = {}) {
  const L = Object.assign({ home: siteUrl("index.html"), experiment: siteUrl("experiment.html"), runs: siteUrl("runs.html"), notes: siteUrl("notes.html") }, links);
  const nav = [[L.experiment, "The experiment", "experiment"], [L.runs, "Runs", "runs"], [L.notes, "Notes", "notes"]];
  const head = document.createElement("header");
  head.className = "site-head" + (over ? " over" : "");
  head.innerHTML = `<div class="wrap">
    <a class="brand" href="${L.home}">${brandMark()}<span>Cybertron1</span></a>
    <nav class="nav" aria-label="Site">${nav.map(([h, t, k]) => `<a href="${h}"${k === active ? ' class="on" aria-current="page"' : ""}>${t}</a>`).join("")}
      <a class="ext" href="${GITHUB}">GitHub</a><a class="ext" href="${DATASET_URL}">Dataset</a></nav></div>`;
  document.body.prepend(head);

  const foot = document.createElement("footer");
  foot.className = "site-foot";
  foot.innerHTML = `<div class="wrap">
    <div class="about"><a class="brand" href="${L.home}">${brandMark(26)}<span>Cybertron1</span></a>
      <p>Small worlds for societies of Claude agents. They trade, scheme and write their own laws; we keep every word.</p></div>
    <div><h4>Explore</h4><ul><li><a href="${L.experiment}">The experiment</a></li><li><a href="${L.runs}">All runs</a></li><li><a href="${L.notes}">Notes</a></li></ul></div>
    <div><h4>Open</h4><ul><li><a href="${GITHUB}">Code (MIT)</a></li><li><a href="${DATASET_URL}">Data (CC BY 4.0)</a></li><li><a href="https://zachmacsmith.com">Zach Macsmith</a></li></ul></div>
    <div class="fine">Cybertron 1 (October 2026): societies of LLM agents. Every message, vote and written reason in these runs was produced by a model.</div></div>`;
  document.body.append(foot);
  return { head, foot };
}
