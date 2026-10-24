// Home page: the night hero with its cast, the stories carousel, featured runs, open data.
import { backdrop, village, villageCfg, PALETTE } from "./scene.js";
import { villagerSvg } from "./core/villagers.js";
import { chrome, esc, siteUrl } from "./chrome.js";
import { DATA, fetchInstance, castCfg, pool } from "./data.js";

const $ = (s, r = document) => r.querySelector(s);
const parse = (v) => { if (typeof v !== "string") return v ?? null; try { return JSON.parse(v); } catch (e) { return null; } };
const modelShort = (m) => String(m || "").replace(/^claude-/, "").replace(/-(\d+)-(\d+)$/, "").replace(/^\w/, (c) => c.toUpperCase());
const local = ["localhost", "127.0.0.1", ""].includes(location.hostname);
const getJson = (p) => fetch(siteUrl(p)).then((r) => { if (!r.ok) throw new Error(`${p}: ${r.status}`); return r.json(); });

chrome({ active: "home", over: true });
$("#cta-runs").href = siteUrl("runs.html");
$("#more-runs").href = siteUrl("runs.html");

// ------------------------------------------------------------------ hero: backdrop + cast on the foreground hill
const CAST = [
  { id: "Hal", cls: "worker", mood: "happy", say: "Workers harvest the camps." },
  { id: "Bjorn", cls: "legislator", mood: "happy", say: "Legislators write the laws, as code." },
  { id: "Soren", cls: "scientist", say: "Scientists know the hidden rules." },
  { id: "Greta", cls: "media", say: "Editors run the newspaper." },
  { id: "Tove", child: true, mood: "happy", say: "Some agents are born mid-run." },
  { id: "Fen", cls: "worker", maker: true, say: "Makers build children, for a fee." },
  { id: "Ilse", cls: "board", say: "The Board can veto any law." },
  { id: "Karin", cls: "fixer", mood: "happy", say: "The Fixer takes on jobs." },
  { id: "Wren", cls: "observer", say: "Someone is always watching." },
];
const ROLE = { worker: "Worker", legislator: "Legislator", scientist: "Scientist", media: "Editor", board: "Board", fixer: "Fixer", observer: "Observer" };
const SAND = new Set(PALETTE.sand.map((h) => parseInt(h.slice(1), 16)));
const hero = $("#hero"), sky = $("#sky"), cast = $("#cast");
let lastKey = "";

function drawHero() {
  const vw = hero.clientWidth, vh = hero.clientHeight, H = 150, s = vh / H, W = Math.ceil(vw / s), key = `${W}x${vh}`;
  if (key === lastKey) return;
  lastKey = key;
  const P = backdrop(sky, "cybertron-home", { width: W, height: H, ground: "sand" });
  sky.style.width = `${W * s}px`;
  // the hill line: the first sand pixel from the top in each column
  const top = (x) => { x = Math.max(0, Math.min(W - 1, Math.round(x))); for (let y = 60; y < H; y++) if (SAND.has(P.get(x, y))) return y; return H - 20; };
  // as many villagers as fit, spaced evenly, keeping clear of the very edges
  const n = Math.max(3, Math.min(CAST.length, Math.floor((W - 12) / (W < 140 ? 17 : 22))));
  const pick = n >= CAST.length ? CAST : CAST.filter((c) => !c.child).slice(0, n);
  const step = (W - 12) / pick.length;
  cast.style.setProperty("--s", `${s}px`);
  cast.innerHTML = pick.map((a, i) => {
    const cx = 6 + step * (i + 0.5) + ((i * 37) % 7 - 3), feet = Math.min(H - 2, top(cx) + 9 + ((i * 53) % 5));
    const role = a.child ? "Child" : a.maker ? "Maker" : ROLE[a.cls];
    const edge = i === 0 ? " edge-l" : i === pick.length - 1 ? " edge-r" : "";
    return `<button class="villager${edge}" style="left:${(cx - 8) * s}px;top:${(feet - 16) * s}px;width:${16 * s}px;height:${16 * s}px;--d:${(i % 4) * -0.6}s"
      aria-label="${esc(a.id)}, ${role}: ${esc(a.say)}"><span class="say"><b>${role}.</b> ${esc(a.say)}</span>
      <div class="bob">${villagerSvg(a, a.mood || "ok", 16)}</div></button>`;
  }).join("");
}
drawHero();
let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(drawHero, 120); });

// ------------------------------------------------------------------ experiment icons (tiny pixel maps)
const ICONS = {
  world: { map: ["......ww....", ".....wW.w...", "....wW...w..", "...hh......", "..hh........", ".hh.........", "hh....YY....", "h....YyYY...", "....YYYyYY..", "...yYYYYyy..", "..ggggggggg."],
    c: { w: "#9aa0a8", W: "#d8dce0", h: "#a0662f", Y: "#e8c060", y: "#c99a3a", g: "#6a9a3a" } },
  laws: { map: ["..IIIIIIIIi.", ".IIIIIIIIIii", ".IkkkIkkIIi.", ".IIIIIIIIIi.", ".IkkIkkkkIi.", ".IIIIIIIIIi.", ".IkkkkIkIIi.", ".IIIIIIIIIi.", ".IkkIIIIIIi.", "IIIIIIIIIii.", ".iiiiiiiii.."],
    c: { I: "#ead2a0", i: "#c99a6a", k: "#4878c8" } },
  goals: { map: ["............", "LLLLLLLLLLLL", "LlLLLLLLLLlL", "LLlLLLLLLlLL", "LLLlLLLLlLLL", "LLLLlRRlLLLL", "LLLLRRRRLLLL", "LLLLRrRRLLLL", "LLLLLRRLLLLL", "LLLLLLLLLLLL", "............"],
    c: { L: "#f6ead0", l: "#c8b8a0", R: "#c8553d", r: "#e8c060" } },
};
function icon({ map, c }) {
  let r = "";
  map.forEach((row, y) => [...row].forEach((ch, x) => { if (c[ch]) r += `<rect x="${x}" y="${y}" width="1" height="1" fill="${c[ch]}"/>`; }));
  return `<svg viewBox="0 0 12 11" width="52" height="48" shape-rendering="crispEdges" aria-hidden="true">${r}</svg>`;
}
document.querySelectorAll("[data-icon]").forEach((el) => {
  const k = el.dataset.icon;
  el.innerHTML = k === "agents"
    ? [{ id: "Vesna", cls: "legislator" }, { id: "Hal", cls: "worker" }, { id: "Rhea", cls: "scientist" }].map((a) => villagerSvg(a, "ok", 48)).join("")
    : icon(ICONS[k]);
});

// ------------------------------------------------------------------ data
const [catalogR, storiesR] = await Promise.allSettled([fetch(`${DATA}/catalog.json`).then((r) => r.json()), fetch(`${DATA}/stories.json`).then((r) => r.json())]);
const runs = catalogR.status === "fulfilled" ? catalogR.value.runs || [] : [];
const byId = Object.fromEntries(runs.map((r) => [r.run_id, r]));
const runHref = (id, hash = "") => siteUrl(`run.html?id=${encodeURIComponent(id)}${hash}`);

// ------------------------------------------------------------------ stories carousel
function shuffle(xs) { const a = xs.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function storyCard(st, i) {
  const run = byId[st.run_id];
  const who = [st.agent, [st.model, st.class === "media" ? "editor" : st.class].filter(Boolean).join(" ")].filter(Boolean).join(", ");
  const href = runHref(st.run_id, `#people/${encodeURIComponent(st.agent)}${st.round ? `@${st.round}` : ""}`);
  const mood = ["ok", "happy", "sad"].includes(st.mood) ? st.mood : "ok";
  const stars = [[10, 8], [58, 14], [30, 22], [70, 4]].map(([x, y]) => `<i class="star" style="left:${(x + i * 13) % 76}px;top:${y}px"></i>`).join("");
  return `<article class="panel story" aria-roledescription="slide" aria-label="${i + 1}">
    <div class="story-top"><div class="portrait pixel">${stars}${villagerSvg({ id: st.agent, cls: st.class }, mood, 72)}</div>
      <div><h3>${esc(st.title)}</h3></div></div>
    <p class="sub">${esc(st.subtitle)}</p>
    <blockquote class="quote">“${esc(st.quote)}”</blockquote>
    <div class="story-foot"><cite>${esc(who)}</cite><a href="${href}">${esc(run ? run.title : st.run_id)} →</a></div></article>`;
}
(function stories() {
  const root = $("#stories");
  if (storiesR.status !== "fulfilled") { root.innerHTML = '<p class="loading">Stories could not be loaded.</p>'; return; }
  const list = shuffle((storiesR.value.stories || []).filter((s) => s.title && s.quote && s.agent && s.run_id));
  if (!list.length) { root.innerHTML = '<p class="loading">No stories yet.</p>'; return; }
  root.innerHTML = list.map(storyCard).join("");
  const ctl = $("#car-ctl"), cards = [...root.children];
  const pageBy = (dir) => { const w = cards[0].getBoundingClientRect().width + parseFloat(getComputedStyle(root).columnGap || 0);
    const per = Math.max(1, Math.round(root.clientWidth / w));
    const atEnd = root.scrollLeft + root.clientWidth >= root.scrollWidth - 4, atStart = root.scrollLeft <= 4;
    if (dir > 0 && atEnd) root.scrollTo({ left: 0, behavior: "smooth" });
    else if (dir < 0 && atStart) root.scrollTo({ left: root.scrollWidth, behavior: "smooth" });
    else root.scrollBy({ left: dir * per * w, behavior: "smooth" }); };
  $("#prev").onclick = () => pageBy(-1);
  $("#next").onclick = () => pageBy(1);
  const fit = () => { ctl.hidden = root.scrollWidth <= root.clientWidth + 4; };
  fit(); addEventListener("resize", fit);
  root.addEventListener("keydown", (e) => { if (e.key === "ArrowRight") pageBy(1); if (e.key === "ArrowLeft") pageBy(-1); });
  root.tabIndex = 0;
})();

// ------------------------------------------------------------------ featured runs, each with its generated village
const limit = pool(3);
(function featured() {
  const root = $("#runs");
  if (!runs.length) { root.innerHTML = '<p class="loading">Runs could not be loaded.</p>'; return; }
  const list = runs.filter((r) => r.featured).slice(0, 6);
  root.innerHTML = list.map((r) => {
    const models = (parse(r.models_list_json) || []).map(modelShort);
    return `<a class="panel run" href="${runHref(r.run_id)}"><canvas class="thumb pixel" data-id="${esc(r.run_id)}" aria-hidden="true"></canvas>
      <div class="body"><div class="label">${esc(r.spec)}</div><h3>${esc(r.title)}</h3><p>${esc(r.description || "")}</p>
      <div class="facts"><span class="chip gold">${r.n_agents} agents</span><span class="chip">${r.rounds_played ?? r.rounds} rounds</span>${models.map((m) => `<span class="chip">${esc(m)}</span>`).join("")}</div></div></a>`;
  }).join("");
  root.querySelectorAll("canvas.thumb").forEach((cv) => {
    const row = byId[cv.dataset.id];
    // each village from the run's real cast (its classes, Makers, camps and observer), read from the start of its viewer.json
    limit(() => fetchInstance(row)).then((inst) => castCfg(row, inst), () => villageCfg(row))
      .then((cfg) => { try { village(cv, row.run_id, Object.assign(cfg, { width: 160, height: 100 })); } catch (e) { console.warn("village", row.run_id, e); } });
  });
})();


