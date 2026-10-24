// The runs catalog: every published run drawn as its own village.

import { backdrop, village, villageCfg, BUILDINGS, Px } from "./scene.js";
import { chrome } from "./chrome.js";
import { villagerSvg } from "./core/villagers.js";
import { esc } from "./core/text.js";

const parseJson = (v) => { if (v == null || typeof v !== "string") return v ?? null; try { return JSON.parse(v); } catch (e) { return null; } };
const modelShort = (m) => String(m || "").replace(/^claude-/, "").replace(/-(\d+)-(\d+)$/, " $1.$2").replace(/^\w/, (c) => c.toUpperCase());
const runFacts = (r) => ({ models: (parseJson(r.models_list_json) || []).map(modelShort), rounds: r.rounds_played ?? r.rounds, tags: parseJson(r.tags_json) || [] });

import { DATA } from "./data.js";
const $ = (s, r = document) => r.querySelector(s);

// ------------------------------------------------------------------ the instance block of a viewer.json, without downloading the rest
// viewer.json files are 0.4 to 19 MB, but "instance" (agents, camps, observer) sits in the first ~130 KB. Stream the file, cut the
// instance object out with a tiny brace scanner and cancel the download.
async function fetchInstance(path) {
  const res = await fetch(`${DATA}/${path}/viewer.json`);
  if (!res.ok || !res.body) throw new Error(`viewer.json ${res.status}`);
  const reader = res.body.getReader(), dec = new TextDecoder();
  let buf = "", start = -1, i = 0, depth = 0, inStr = false, escp = false;
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    if (start < 0) {
      const k = buf.indexOf('"instance"');
      if (k < 0) continue;
      const b = buf.indexOf("{", k);
      if (b < 0) continue;
      start = i = b;
    }
    for (; i < buf.length; i++) {
      const c = buf[i];
      if (inStr) { if (escp) escp = false; else if (c === "\\") escp = true; else if (c === '"') inStr = false; continue; }
      if (c === '"') inStr = true;
      else if (c === "{") depth++;
      else if (c === "}" && --depth === 0) { reader.cancel().catch(() => {}); return JSON.parse(buf.slice(start, i + 1)); }
    }
  }
  throw new Error("no instance block");
}
// a small pool so 17 streams don't all start at once
function pool(n) {
  let active = 0; const q = [];
  const next = () => { if (active >= n || !q.length) return; active++; const [fn, ok, bad] = q.shift(); fn().then(ok, bad).finally(() => { active--; next(); }); };
  return (fn) => new Promise((ok, bad) => { q.push([fn, ok, bad]); next(); });
}
const limit = pool(4);

// ------------------------------------------------------------------ buildings: legend order, what they mean, the class that fills them
const KINDS = [
  { k: "hall", cls: "legislator", one: "legislator", many: "legislators" },
  { k: "manor", cls: "board", one: "Board member", many: "Board members" },
  { k: "press", cls: "media", one: "editor", many: "editors" },
  { k: "archive", cls: "scientist", one: "scientist", many: "scientists" },
  { k: "workshop", cls: "fixer", one: "Fixer", many: "Fixers" },
  { k: "nursery", cls: "maker", one: "Maker", many: "Makers" },
  { k: "tower", cls: "observer", one: "secret observer", many: "secret observers" },
  { k: "graves", cls: null, one: "", many: "" },
  { k: "mine", cls: "worker", one: "worker", many: "workers" },
];
const MEANING = { hall: "legislators", manor: "a Board", press: "a newspaper editor", archive: "scientists", workshop: "a Fixer",
  nursery: "a Maker (births)", tower: "a secret observer", graves: "lifespans or deaths", mine: "workers, one per camp" };

// a building drawn on a grass tile, as an <img> data URL (drawn once, reused on every card)
const ICON = {};
function iconOf(k) {
  if (ICON[k]) return ICON[k];
  const b = BUILDINGS[k], cv = document.createElement("canvas"), W = 14, H = 14;
  const P = Px(cv, W, H, "#6ca63c");
  b.draw(P, (W - b.w) >> 1, Math.max(H - b.h - 1, 6) - (k === "tower" ? 5 : 0));
  P.flush();
  return (ICON[k] = cv.toDataURL());
}

// ------------------------------------------------------------------ run facts
// The catalog has no death summary and the instance block has no lifespans, so the graveyard comes from the run's tags here.
const DEATH_TAGS = ["lifespans", "violence", "assassination", "collapse", "dynasty", "succession"];
function residents(row, inst) {
  const count = {}; let makers = 0; const camps = new Set();
  for (const a of inst.agents || []) {
    count[a.cls] = (count[a.cls] || 0) + 1;
    for (const r of a.rights || []) { if (r === "maker") makers++; if (String(r).startsWith("harvest:")) camps.add(r); }
  }
  if (makers) count.maker = makers;
  if (inst.observer) count.observer = 1;
  const tags = runFacts(row).tags;
  const deaths = tags.some((t) => DEATH_TAGS.includes(String(t).toLowerCase()));
  return { count, camps: camps.size || (inst.camps ? Object.keys(inst.camps).length : 0), deaths };
}
function buildingList(res) {
  const out = [];
  for (const d of KINDS) {
    if (d.k === "graves") { if (res.deaths) out.push({ k: d.k, label: "Graveyard", sub: "agents age and die" }); continue; }
    const n = res.count[d.cls]; if (!n) continue;
    let sub = `${n} ${n === 1 ? d.one : d.many}`;
    if (d.k === "mine" && res.camps) sub += `, ${res.camps} camp${res.camps === 1 ? "" : "s"}`;
    if (d.k === "tower") sub = "a secret observer";
    out.push({ k: d.k, cls: d.cls, label: d.k === "mine" ? "Mines" : BUILDINGS[d.k].name, sub, n });
  }
  return out;
}
function roundsText(row) {
  const played = row.rounds_played ?? row.rounds, of = row.rounds;
  return { n: played, sub: of && played < of ? `of ${of} planned` : "rounds", usable: row.usable_rounds };
}

// ------------------------------------------------------------------ state
const state = { q: "", spec: "", models: new Set(), featured: false, has: new Set(), view: "grid" };
let RUNS = [];

async function main() {
  drawSky();
  addEventListener("resize", debounce(drawSky, 200));
  const cat = await (await fetch(`${DATA}/catalog.json`)).json();
  RUNS = cat.runs.map((row) => ({ row, fx: runFacts(row), inst: null, res: null, card: null, drawn: false }))
    .sort((a, b) => (b.row.featured - a.row.featured) || (b.row.n_agents - a.row.n_agents));
  buildLegend(); buildFilters(); buildCards();
  render();
  for (const r of RUNS) limit(() => fetchInstance(r.row.path)).then((inst) => ready(r, inst), (e) => failed(r, e));
}

function drawSky() {
  const cv = $("#sky"), w = document.documentElement.clientWidth, s = w < 700 ? 2 : 3, W = Math.ceil(w / s), H = w < 700 ? 100 : 84;
  backdrop(cv, "cybertron-runs", { width: W, height: H, ground: "meadow" });
  cv.style.height = `${(H * w) / W}px`;
}
const debounce = (f, ms) => { let t; return () => { clearTimeout(t); t = setTimeout(f, ms); }; };

// ------------------------------------------------------------------ legend (doubles as the "has building" filter)
function buildLegend() {
  $("#legend").innerHTML = KINDS.map((d) => `<button class="lg" data-k="${d.k}" aria-pressed="false">
    <img src="${iconOf(d.k)}" alt="" width="42" height="42"><span><b>${esc(d.k === "mine" ? "Mines" : BUILDINGS[d.k].name)}</b>
    <small>${esc(MEANING[d.k])}</small></span></button>`).join("");
  $("#legend").addEventListener("click", (e) => {
    const b = e.target.closest(".lg"); if (!b) return;
    const k = b.dataset.k; state.has.has(k) ? state.has.delete(k) : state.has.add(k); render();
  });
}

// ------------------------------------------------------------------ filters
function buildFilters() {
  const specs = {}; for (const r of RUNS) specs[r.row.spec] = (specs[r.row.spec] || 0) + 1;
  $("#spec").insertAdjacentHTML("beforeend", Object.keys(specs).sort((a, b) => a.localeCompare(b))
    .map((s) => `<option value="${esc(s)}">${esc(s)} (${specs[s]})</option>`).join(""));
  const models = [...new Set(RUNS.flatMap((r) => r.fx.models))].sort();
  $("#models").innerHTML = models.map((m) => `<button class="chip" data-m="${esc(m)}" aria-pressed="false">${esc(m)}</button>`).join("");
  $("#q").addEventListener("input", (e) => { state.q = e.target.value.trim().toLowerCase(); render(); });
  $("#spec").addEventListener("change", (e) => { state.spec = e.target.value; render(); });
  $("#feat").addEventListener("click", () => { state.featured = !state.featured; render(); });
  $("#models").addEventListener("click", (e) => {
    const b = e.target.closest("[data-m]"); if (!b) return;
    const m = b.dataset.m; state.models.has(m) ? state.models.delete(m) : state.models.add(m); render();
  });
  $("#active").addEventListener("click", (e) => {
    const b = e.target.closest("[data-x]"); if (!b) return;
    const [t, v] = b.dataset.x.split(":");
    if (t === "q") { state.q = ""; $("#q").value = ""; } else if (t === "spec") { state.spec = ""; $("#spec").value = ""; }
    else if (t === "feat") state.featured = false; else if (t === "m") state.models.delete(v); else if (t === "has") state.has.delete(v);
    render();
  });
  const setView = (v) => { state.view = v; $("#runs").classList.toggle("list", v === "list");
    for (const [id, on] of [["#v-grid", v === "grid"], ["#v-list", v === "list"]]) { $(id).classList.toggle("on", on); $(id).setAttribute("aria-pressed", on); } };
  $("#v-grid").onclick = () => setView("grid"); $("#v-list").onclick = () => setView("list");
  $("#reset").onclick = () => { state.q = ""; state.spec = ""; state.featured = false; state.models.clear(); state.has.clear();
    $("#q").value = ""; $("#spec").value = ""; render(); };
}

function matches(r) {
  const { row, fx } = r;
  if (state.featured && !row.featured) return false;
  if (state.spec && row.spec !== state.spec) return false;
  for (const m of state.models) if (!fx.models.includes(m)) return false;
  if (state.has.size) { if (!r.res) return false; const ks = new Set(buildingList(r.res).map((b) => b.k)); for (const k of state.has) if (!ks.has(k)) return false; }
  if (state.q) { const hay = [row.title, row.description, row.spec, ...fx.tags, ...fx.models].join(" ").toLowerCase(); if (!hay.includes(state.q)) return false; }
  return true;
}

function render() {
  let shown = 0;
  for (const r of RUNS) { const on = matches(r); r.card.hidden = !on; if (on) shown++; }
  const total = RUNS.length, agents = RUNS.reduce((s, r) => s + (r.row.n_agents || 0), 0);
  $("#count").textContent = shown === total ? `${total} villages, ${agents} agents in all` : `${shown} of ${total} villages`;
  $("#empty").hidden = shown > 0;
  $("#feat").setAttribute("aria-pressed", state.featured); $("#feat").classList.toggle("on", state.featured);
  document.querySelectorAll("#models [data-m]").forEach((b) => { const on = state.models.has(b.dataset.m); b.classList.toggle("on", on); b.setAttribute("aria-pressed", on); });
  document.querySelectorAll("#legend .lg").forEach((b) => { const on = state.has.has(b.dataset.k); b.classList.toggle("on", on); b.setAttribute("aria-pressed", on); });
  const act = [];
  if (state.q) act.push(["q:", `“${state.q}”`]);
  if (state.featured) act.push(["feat:", "Featured"]);
  if (state.spec) act.push(["spec:", `Spec ${state.spec}`]);
  for (const m of state.models) act.push([`m:${m}`, m]);
  for (const k of state.has) act.push([`has:${k}`, `Has ${k === "mine" ? "mines" : BUILDINGS[k].name.toLowerCase()}`]);
  $("#active").innerHTML = act.length ? act.map(([x, t]) => `<button data-x="${esc(x)}">${esc(t)} <span aria-hidden="true">×</span><span class="sr">remove filter</span></button>`).join("") : "";
}

// ------------------------------------------------------------------ cards
function buildCards() {
  const host = $("#runs");
  for (const r of RUNS) {
    const { row, fx } = r, href = `run.html?id=${encodeURIComponent(row.run_id)}`, rt = roundsText(row);
    const el = document.createElement("article");
    el.className = "run" + (row.featured ? " featured" : "");
    el.innerHTML = `
      <a class="map" href="${href}" tabindex="-1" aria-hidden="true">
        <canvas class="px" width="240" height="150"></canvas>
        <span class="loading">Surveying…</span>
        ${row.featured ? `<span class="ribbon">★ Featured</span>` : ""}
      </a>
      <div class="plaque">
        <div class="spec">${esc(row.spec)}</div>
        <h3><a href="${href}">${esc(row.title)}</a></h3>
        <div class="stats">
          <span class="stat"><b>${row.n_agents}</b><small>agents</small></span>
          <span class="stat"><b>${rt.n}</b><small>${esc(rt.sub)}</small></span>
          <span class="stat models"><small>${fx.models.map((m) => `<span>${esc(m)}</span>`).join("")}</small></span>
        </div>
        ${rt.usable && rt.usable !== `1-${rt.n}` ? `<p class="usable">Usable rounds ${esc(rt.usable)}</p>` : ""}
        <p class="desc">${esc(row.description || "")}</p>
        <ul class="has" aria-label="Buildings in this village"><li class="ph">Counting houses…</li></ul>
        <div class="tags">${fx.tags.map((t) => `<span>${esc(t)}</span>`).join("")}</div>
      </div>`;
    host.append(el);
    r.card = el;
  }
  // draw villages only when they come near the screen, one per frame
  const io = new IntersectionObserver((ents) => {
    for (const e of ents) if (e.isIntersecting) { const r = RUNS.find((x) => x.card === e.target); r.visible = true; queueDraw(r); io.unobserve(e.target); }
  }, { rootMargin: "300px 0px" });
  RUNS.forEach((r) => io.observe(r.card));
}

function ready(r, inst) {
  r.inst = inst; r.res = residents(r.row, inst);
  const list = buildingList(r.res);
  $(".has", r.card).innerHTML = list.map((b) => `<li class="b-${b.k}" title="${esc(b.label)}: ${esc(b.sub)}"><img src="${iconOf(b.k)}" alt="" width="28" height="28">
    <span><b>${esc(b.label)}</b> ${esc(b.sub)}</span>${b.cls ? villagerSvg({ id: r.row.run_id + b.cls, cls: b.cls === "maker" ? "worker" : b.cls, maker: b.cls === "maker" }, "ok", 26) : ""}</li>`).join("");
  queueDraw(r);
  if (state.has.size) render();
}
function failed(r, e) {
  console.warn("instance for", r.row.path, e);
  r.res = { count: {}, camps: 0, deaths: false };
  $(".has", r.card).innerHTML = `<li class="ph">Village plan unavailable</li>`;
  r.inst = { agents: [] }; queueDraw(r);
}

// Villages are drawn in two module workers (OffscreenCanvas) so scrolling never stalls; without worker support they are drawn
// here, one per frame.
const drawQ = [];
const WORKERS = [];
try {
  if (typeof OffscreenCanvas !== "undefined" && "transferToImageBitmap" in OffscreenCanvas.prototype)
    for (let i = 0; i < 2; i++) { const w = new Worker(new URL("./village-worker.js", import.meta.url), { type: "module" }); w.busy = null; w.onmessage = onDrawn; w.onerror = () => workerDied(w); WORKERS.push(w); }
} catch (e) { WORKERS.length = 0; }
function workerDied(w) { // e.g. module workers unsupported: fall back to the main thread for everything
  const i = WORKERS.indexOf(w); if (i < 0) return; WORKERS.splice(i, 1);
  if (w.busy) { w.busy.drawn = false; drawQ.unshift(w.busy); }
  pump();
}
function queueDraw(r) {
  if (!r.visible || !r.inst || r.drawn || drawQ.includes(r)) return;
  drawQ.push(r); pump();
}
function cfgFor(r) {
  const cfg = villageCfg(r.row, { instance: r.inst, events: [] });
  if (r.res.deaths) cfg.roles.add("deaths");
  return cfg;
}
let mainBusy = false;
function pump() {
  if (WORKERS.length) {
    for (const w of WORKERS) {
      if (w.busy || !drawQ.length) continue;
      const r = drawQ.shift(); r.drawn = true; w.busy = r;
      const cfg = cfgFor(r);
      w.postMessage({ id: r.row.run_id, seed: r.row.run_id, cfg: { ...cfg, roles: [...cfg.roles] } });
    }
    return;
  }
  if (mainBusy || !drawQ.length) return;
  mainBusy = true;
  requestAnimationFrame(() => {
    const r = drawQ.shift(); r.drawn = true;
    const cv = $("canvas", r.card);
    try { finish(r, village(cv, r.row.run_id, cfgFor(r))); } catch (e) { fail(r, e); }
    mainBusy = false; pump();
  });
}
function onDrawn(e) {
  const w = e.target, r = w.busy; w.busy = null;
  const { out, bmp, error } = e.data;
  if (error) fail(r, error);
  else { const cv = $("canvas", r.card); cv.width = bmp.width; cv.height = bmp.height; cv.getContext("2d").drawImage(bmp, 0, 0); bmp.close(); finish(r, out); }
  pump();
}
function finish(r, out) {
  const cv = $("canvas", r.card);
  if (out.square) cv.style.objectPosition = `${(out.square[0] / out.width) * 100}% ${(out.square[1] / out.height) * 100}%`; // list view crops around the square
  addSpots(r, out);
  $(".loading", r.card)?.remove();
  r.card.classList.add("drawn");
}
function fail(r, e) {
  console.warn("village() failed for", r.row.path, e);
  const l = $(".loading", r.card); if (l) l.textContent = "This village's map could not be drawn";
}
// hover labels on the map's named buildings
function addSpots(r, out) {
  const map = $(".map", r.card), W = out.width, H = out.height;
  const named = out.places.filter((p) => BUILDINGS[p.kind] && p.kind !== "mine");
  map.insertAdjacentHTML("beforeend", named.map((p) => `<span class="spot" style="left:${(p.x / W) * 100}%;top:${(p.y / H) * 100}%;width:${(p.w / W) * 100}%;height:${(p.h / H) * 100}%"><i>${esc(BUILDINGS[p.kind].name)}</i></span>`).join(""));
}

chrome({ active: "runs" });
main().catch((e) => { console.error(e); $("#count").textContent = "Could not load the catalog."; });
