// The run page: one page for every section of a run, all on one day clock. The shell (masthead, section bar, day clock) is
// built here; each section is a view module rendered into #view. Routing: run.html?id=<run_id>#section[/target]@day
// (days are 1-based on the page, rounds 0-based in the data), the same shape the old run page used.
import { prepare } from "../core/model.js";
import { chrome } from "../chrome.js";
import { catalog, loadRun, loadReasoning } from "../data.js";
import { backdrop, PALETTE } from "../scene.js";
import { esc, icon, buildingIcon, runFacts } from "./common.js";
import { frontView } from "./front.js";
import { chronicleView } from "./chronicle.js";
import { peopleView } from "./people.js";
import { squareView } from "./square.js";
import { dataView } from "./dataview.js";

const $ = (s, el = document) => el.querySelector(s);
chrome({ active: "runs" });

// ------------------------------------------------------------------ load the run
const params = new URLSearchParams(location.search);
const runs = await catalog();
const row = runs.find((r) => r.run_id === params.get("id")) || runs.find((r) => r.spec === params.get("spec")) || runs.find((r) => r.featured) || runs[0];
if (!params.get("id")) history.replaceState(null, "", `?id=${encodeURIComponent(row.run_id)}${location.hash}`);
let D;
try { D = await loadRun(row); }
catch (e) { $("#view").innerHTML = `<p class="wrap loading-run">This run's data could not be loaded (${esc(e.message)}). <a href="runs.html">All runs</a></p>`; throw e; }
const S = prepare(D), F = runFacts(S, D);
const LAST = S.lastRound, TOTAL = Math.max(S.rounds, LAST + 1);
const R1 = (r) => r + 1;

// ------------------------------------------------------------------ state, links, routing
const SECTIONS = [
  { k: "front", label: "Front page", short: "Front", ico: () => iconEl("front") },
  { k: "chronicle", label: "Chronicle", short: "Paper", ico: () => buildingIcon("press") },
  { k: "people", label: "People", short: "People", ico: () => iconEl("people") },
  { k: "correspondence", label: "Letters", short: "Letters", ico: () => iconEl("letters") },
  { k: "laws", label: "Laws", short: "Laws", ico: () => buildingIcon("hall") },
  { k: "square", label: "The square", short: "Square", ico: () => iconEl("square") },
  { k: "data", label: "Data", short: "Data", ico: () => buildingIcon("archive") },
];
function iconEl(k) { const s = document.createElement("span"); s.innerHTML = icon(k, 14); return s.firstChild; }
// The day a run opens on (when the link names none): the last day, unless most of the village is dead by then, in which case
// the day it was fullest, so the first look is at a living village.
const aliveOn = (r) => S.agents.filter((a) => a.cls !== "observer" && F.status(a.id, r) !== "gone" && F.status(a.id, r) !== "unborn").length;
const aliveBy = Array.from({ length: LAST + 1 }, (_, r) => aliveOn(r)), peak = Math.max(...aliveBy);
const OPEN = aliveBy[LAST] >= peak / 2 ? LAST : aliveBy.lastIndexOf(peak);
const st = { round: OPEN, section: "front", target: null };
const href = (section, target, round = st.round) => `#${section}${target ? "/" + target.split("/").map(encodeURIComponent).join("/") : ""}@${R1(round)}`;
function parse() {
  const m = decodeURIComponent(location.hash.slice(1)).match(/^([a-z]+)?(?:\/([^@]*))?(?:@(\d+))?$/) || [];
  const sec = SECTIONS.some((s) => s.k === m[1]) ? m[1] : m[1] === "letters" ? "correspondence" : "front";
  return { section: sec, target: m[2] || null, round: m[3] ? Math.max(0, Math.min(LAST, +m[3] - 1)) : st.round };
}
// go({round}) moves the clock and keeps the reader's place; a new section or target is a new page in the history
function go(patch) {
  const n = { ...st, ...patch };
  if ("section" in patch && !("target" in patch)) n.target = null;
  const h = href(n.section, n.target, n.round), page = n.section !== st.section || n.target !== st.target;
  if (location.hash === h) return;
  if (page) history.pushState(null, "", h); else history.replaceState(null, "", h);
  route();
}
const ctx = { S, D, F, row, st, href, go, R1, LAST, TOTAL, tip: $("#tip"), loadReasoning: (agent) => loadReasoning(row, agent) };

// ------------------------------------------------------------------ masthead
document.title = `${row.title} · Cybertron`;
$(".run-title").textContent = row.title;
$(".spec").textContent = `${row.spec} · seed ${row.seed ?? (row.run_id.match(/seed(\d+)/) || [])[1] ?? "?"} · ${S.agents.filter((a) => a.cls !== "observer").length} villagers`;
$(".standfirst").textContent = row.description || "";
if (!row.description) $(".standfirst").hidden = true;
if (row.validity) { const n = $(".notice"); n.hidden = false; n.innerHTML = `${icon("home", 14)} ${esc(row.validity.replace(/\*\*/g, ""))}`; }
backdrop($(".mast-bg"), row.run_id, { width: 320, height: 110, ground: "meadow", town: true });

// ------------------------------------------------------------------ section bar
const nav = $(".secnav");
for (const s of SECTIONS) {
  const a = document.createElement("a"); a.dataset.k = s.k; a.title = s.k === "correspondence" ? "Letters: every private message" : s.label;
  const ic = document.createElement("span"); ic.className = "ico"; ic.append(s.ico());
  a.append(ic); a.insertAdjacentHTML("beforeend", `<span class="lab"><span class="long">${s.label}</span><span class="short">${s.short}</span></span>`);
  nav.append(a);
}
// the bar's height, for anything else that sticks under it
new ResizeObserver(() => document.documentElement.style.setProperty("--runbar-h", $("#runbar").offsetHeight + "px")).observe($("#runbar"));

// ------------------------------------------------------------------ the day clock
const SEASONS = [["Spring", "#82b24a"], ["Summer", "#e8c060"], ["Autumn", "#d8824e"], ["Winter", "#9ccfe0"]];
const seasonOf = (r) => SEASONS[Math.min(3, Math.floor(4 * r / TOTAL))];
ctx.seasonOf = seasonOf;
function drawMoon(cv, r) {
  const g = cv.getContext("2d"); g.clearRect(0, 0, 12, 12);
  const t = (r % 8) / 8, s = t <= 0.5 ? 22 * t : -22 * (1 - t);
  for (let y = 0; y < 12; y++) for (let x = 0; x < 12; x++) { const dx = x - 5.5, dy = y - 5.5; if (dx * dx + dy * dy > 30) continue;
    const lit = (dx - s) ** 2 + dy * dy > 30; g.fillStyle = lit ? (dx + dy < -4 ? "#ffffff" : PALETTE.cream) : "#3a4570"; g.fillRect(x, y, 1, 1); }
}
const MOON_NAMES = ["new moon", "waxing crescent", "first quarter", "waxing gibbous", "full moon", "waning gibbous", "last quarter", "waning crescent"];
const daysEl = $(".days");
const act = S.heads.map((h) => (h ? h.posts + h.dms : 0)), amax = Math.max(1, ...act);
daysEl.setAttribute("aria-valuemin", 1); daysEl.setAttribute("aria-valuemax", R1(LAST));
daysEl.innerHTML = Array.from({ length: LAST + 1 }, (_, r) => {
  const pips = [F.lawsNewAt[r].length ? "law" : "", F.deathsAt[r].length ? "death" : ""].filter(Boolean);
  const hgt = Math.round(30 + 70 * (act[r] || 0) / amax);
  return `<button data-r="${r}" tabindex="-1" style="--h:${hgt}%;--season:${seasonOf(r)[1]}" title="${esc(`Day ${R1(r)} · ${seasonOf(r)[0]}${F.daySummary(r).length ? "\n" + F.daySummary(r).join(" · ") : ""}`)}"><i></i>${pips.map((p) => `<em class="${p}"></em>`).join("")}</button>`; }).join("");
$(".ck-rest").innerHTML = LAST + 1 < TOTAL ? `<span title="${esc(row.validity || "")}">${icon("home", 10)} ${TOTAL - LAST - 1} days unplayed</span>` : "";
function setTicker(r) {
  const s = F.daySummary(r), n = F.papers(r)[0];
  $(".ticker").innerHTML = `<b>Day ${R1(r)}</b> ${s.length ? esc(s.join(" · ")) : "A quiet day."}${n && !s.length ? ` <span class="tk-paper">${esc(n.paper)}: ${esc(n.line)}</span>` : ""}`;
}
function paintClock() {
  const r = st.round, [sname, scol] = seasonOf(r);
  $(".ck-n").textContent = `Day ${R1(r)}`;
  $(".ck-of").textContent = ` of ${TOTAL} · ${sname}`;
  $(".ck-day").style.setProperty("--season", scol);
  $(".moon").title = MOON_NAMES[r % 8];
  drawMoon($(".moon"), r);
  daysEl.querySelectorAll("button").forEach((b) => { const k = +b.dataset.r; b.classList.toggle("on", k === r); b.classList.toggle("later", k > r); });
  daysEl.setAttribute("aria-valuenow", R1(r)); daysEl.setAttribute("aria-valuetext", `Day ${R1(r)} of ${TOTAL}`);
  setTicker(r);
  nav.querySelectorAll("a").forEach((a) => { const on = a.dataset.k === st.section; a.classList.toggle("on", on); on ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"); a.href = href(a.dataset.k, null); });
}
const dayAt = (x) => { const rc = daysEl.getBoundingClientRect(); return Math.max(0, Math.min(LAST, Math.floor((x - rc.left) / rc.width * (LAST + 1)))); };
let drag = false;
daysEl.addEventListener("pointerdown", (e) => { drag = true; daysEl.setPointerCapture(e.pointerId); go({ round: dayAt(e.clientX) }); e.preventDefault(); });
daysEl.addEventListener("pointermove", (e) => { if (drag) { const k = dayAt(e.clientX); if (k !== st.round) go({ round: k }); } else if (e.pointerType === "mouse") setTicker(dayAt(e.clientX)); });
daysEl.addEventListener("pointerup", () => { drag = false; });
daysEl.addEventListener("pointerleave", () => { if (!drag) setTicker(st.round); });
daysEl.addEventListener("keydown", (e) => { if (e.key === "Home") { go({ round: 0 }); e.preventDefault(); } if (e.key === "End") { go({ round: LAST }); e.preventDefault(); } });
$(".ck-prev").onclick = () => go({ round: Math.max(0, st.round - 1) });
$(".ck-next").onclick = () => go({ round: Math.min(LAST, st.round + 1) });
let playT = null;
function togglePlay() {
  if (st.section === "square" && current && current.togglePlay) return current.togglePlay();
  const b = $(".ck-play");
  if (playT) { clearInterval(playT); playT = null; b.textContent = "▶"; b.setAttribute("aria-label", "Play"); return; }
  if (st.round >= LAST) go({ round: 0 });
  b.textContent = "❚❚"; b.setAttribute("aria-label", "Pause");
  playT = setInterval(() => { if (st.round >= LAST) return togglePlay(); go({ round: st.round + 1 }); }, 1400);
}
$(".ck-play").onclick = togglePlay;
addEventListener("keydown", (e) => {
  if (e.target.closest("input, textarea, select") || e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "ArrowLeft") { go({ round: Math.max(0, st.round - 1) }); e.preventDefault(); }
  else if (e.key === "ArrowRight") { go({ round: Math.min(LAST, st.round + 1) }); e.preventDefault(); }
  else if (e.key === " " && !e.target.closest("a, button, summary")) { togglePlay(); e.preventDefault(); }
});

// ------------------------------------------------------------------ views
const viewRoot = $("#view");
viewRoot.innerHTML = "";
const VIEWS = { front: frontView, chronicle: chronicleView, laws: chronicleView, correspondence: chronicleView, people: peopleView, square: squareView, data: dataView };
const made = new Map();
function viewFor(section) {
  const make = VIEWS[section];
  if (!made.has(make)) {
    const el = document.createElement("div");
    viewRoot.append(el);
    made.set(make, make(ctx, el));
  }
  return made.get(make);
}
let current = null, shown = null;
function route() {
  const p = parse(), page = p.section !== st.section || p.target !== st.target || !shown;
  Object.assign(st, p);
  paintClock();
  const v = viewFor(st.section);
  if (v !== current) {
    if (current && current.leave) current.leave();
    for (const x of made.values()) x.el.hidden = x !== v;
    document.body.classList.remove("indoor");
    current = v;
  }
  v.render({ page });
  if (page && shown) { const m = $(".run-mast"), top = m.offsetTop + m.offsetHeight; if (scrollY > top) scrollTo({ top, behavior: "instant" }); }
  shown = true;
  ctx.tip.hidden = true;
}
addEventListener("hashchange", route);
addEventListener("scroll", () => {
  ctx.tip.hidden = true;
  const mast = $(".run-mast");                       // (a stuck bar's own offsetTop moves with it, so measure from the masthead)
  $("#runbar").classList.toggle("compact", scrollY > mast.offsetTop + mast.offsetHeight + 240);
}, { passive: true });
route();
