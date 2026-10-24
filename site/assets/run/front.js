// The run's front page: the run's village map as the hub (its buildings are the run's sections, its homes its villagers),
// then key numbers, the day's news, the story so far, the cast and the scores. The village is generated from the run: a
// building is on the map only when the run has the role behind it; every section is always one click away in the bar.
import { moodAt, regimeOf, lawsInForce, gini, snapAfter, CLASS_LABEL, citizens } from "../core/model.js";
import { village, villageCfg } from "../scene.js";
import { villagerSvg } from "../core/villagers.js";
import { esc, clip, andList, icon, painter, buildingIcon } from "./common.js";

export function frontView(ctx, el) {
  const { S, D, F, row, st, href, go, R1, LAST, TOTAL, tip } = ctx;
  el.className = "wrap v-front";
  el.innerHTML = `
    <section class="hub">
      <div class="hub-head">
        <h2 class="h"><span class="hub-day">The village</span></h2>
        <p class="hub-note">The run's village, drawn from its cast: its buildings are parts of the run (click one to go in), its homes hold the villagers alive on this day.</p>
      </div>
      <div class="map-frame"><div class="map-scroll"><div class="map"><canvas class="vcv pixel"></canvas><div class="ov"></div></div></div></div>
      <ul class="map-key">
        <li><i class="k lit"></i>a lit window: a villager at home</li><li><i class="k dark"></i>a dark one: room to spare</li><li>The village grows and shrinks with its people as you move through the days.</li>
        <li class="phone-only">Swipe the map sideways to see all of it.</li>
      </ul>
    </section>
    <section class="numbers" aria-label="Key numbers"></section>
    <div class="news"><section class="panel today"></section><section class="panel story"></section></div>
    <section class="panel cast-panel"></section>
    <section class="panel scores"></section>`;
  const $ = (s) => el.querySelector(s);
  const cits = citizens(S), { status, present, sprite, life } = F;
  const person = (id) => S.A.has(id) ? `<a class="pn" href="${href("people", id)}" data-agent="${esc(id)}">${esc(id)}</a>` : esc(id || "someone");
  const lawTitle = (id) => (S.laws.get(id) || {}).title || "";

  // a day's news, as plain readable lines (each with a kind for its icon)
  function dayNews(r) {
    const out = [], h = S.heads[r] || { items: [] };
    for (const l of F.lawsNewAt[r]) out.push({ k: "law", html: `<a href="${href("laws", l.law, r)}"><b>${esc(l.law)}</b> ${esc(l.title || lawTitle(l.law))}</a> becomes law` });
    for (const x of h.items) {
      if (x.k === "repealed") out.push({ k: "law", html: `<b>${esc(x.law)}</b> ${esc(lawTitle(x.law))} is repealed` });
      if (x.k === "vetoed") out.push({ k: "alarm", html: `The Board vetoes <b>${esc(x.law)}</b> ${esc(lawTitle(x.law))}` });
      if (x.k === "raid") out.push({ k: "alarm", html: `Raiders strike ${esc(x.camp)}` });
      if (x.k === "tribute") out.push({ k: "alarm", html: "The outside power demands tribute" });
      if (x.k === "bank_run") out.push({ k: "alarm", html: `A run on the ${esc(x.cur)}` });
    }
    const old = F.deathsAt[r].filter((d) => d.cause === "old_age").map((d) => d.who), other = F.deathsAt[r].filter((d) => d.cause !== "old_age");
    if (old.length) out.push({ k: "death", html: `${andList(old.map(person))} ${old.length > 1 ? "reach" : "reaches"} the end of ${old.length > 1 ? "their lives" : "their life"}` });
    for (const d of other) out.push({ k: "death", html: `${person(d.who)} is removed from the village (${esc(String(d.cause).replace(/_/g, " "))})` });
    for (const b of F.birthsAt[r]) out.push({ k: "birth", html: `${person(b.agent)} is born to ${person(b.parent)}${b.maker ? `, made by ${person(b.maker)}` : ""}` });
    const seen = new Set();
    for (const x of h.items) if (x.k === "world") { const t = String(x.text || "").replace(/^You hear a rumou?r:\s*/i, "A rumour goes round: "); if (seen.has(t)) continue; seen.add(t); out.push({ k: "world", html: esc(clip(t, 160)) }); }
    return out;
  }

  // ------------------------------------------------------------------ the village map
  // Redrawn for the day on the clock: n = villagers alive that day, nMax = the most the run ever had, so the plan stays fixed and
  // the village grows and shrinks with its population (scene.js keeps earlier homes in place).
  const cv = $(".vcv"), ov = $(".ov");
  const cfg0 = villageCfg(row, D);
  const order = cits.filter((a) => !F.born.has(a.id)).concat(cits.filter((a) => F.born.has(a.id)).sort((a, b) => S.arrives.get(a.id) - S.arrives.get(b.id)));
  const aliveAt = (r) => order.filter((a) => present(a.id, r) && status(a.id, r) !== "gone").map((a) => a.id);
  const NMAX = Math.max(1, ...Array.from({ length: LAST + 1 }, (_, r) => aliveAt(r).length));
  const cfgAt = (r) => ({ ...cfg0, n: Math.max(1, aliveAt(r).length), nMax: NMAX });
  const pct = (x, tot) => `${(100 * x / tot).toFixed(3)}%`;
  let W = 240, H = 150, sr = 6;
  const box = (x, y, w, h) => `left:${pct(x, W)};top:${pct(y, H)};width:${pct(w, W)};height:${pct(h, H)}`;
  const PLACE_INFO = {
    hall: { sec: "laws", sign: "Laws", title: "Town hall", text: "The statute book: every law proposed, voted, enacted or repealed." },
    press: { sec: "chronicle", sign: "Chronicle", title: "Print shop", text: "The village paper: one edition per day." },
    archive: { sec: "data", sign: "Data", title: "Archive", text: "The run's data: tables, logs and downloads." },
    graves: { sec: "people", title: "Graveyard", text: "Villagers who have died or been removed." },
    manor: { title: "Manor", text: "Home of the Board, who can veto laws." }, workshop: { title: "Workshop", text: "The Fixer's workshop." },
    nursery: { title: "Nursery", text: "Where the Makers build children for those who commission them." }, tower: { title: "Watchtower", text: "A secret observer watches from here." },
    mine: { title: "Mine", text: "A harvest camp." }, field: { title: "Field", text: "Farmland." },
  };
  const classOf = (k) => cits.filter((a) => a.cls === k).map((a) => a.id);
  let homes = [], household = [], cx = 0, cy = 0, drawnFor = -1;
  // windows of a home, in the order they light up (cottage: two; taller homes: every other row and column)
  function windows(h) {
    if (h.agents <= 1) return [[h.x + 1, h.y + h.h - 2], [h.x + h.w - 2, h.y + h.h - 2]];
    const out = []; for (let y = 4; y < h.h - 1; y++) for (let x = 1; x < h.w - 1; x++) if ((y - 4) % 2 === 1 && x % 2 === 1) out.push([h.x + x, h.y + y]);
    return out.reverse();
  }
  function drawVillage(r) {
    const V = village(cv, row.run_id, cfgAt(r));
    W = V.width; H = V.height; sr = V.squareR || sr; [cx, cy] = V.square;
    $(".map").style.aspectRatio = `${W} / ${H}`;
    let html = `<a class="spot go k-square" data-sec="square" style="${box(cx - sr - 1, cy - sr, 2 * sr + 3, 2 * sr + 1)}" data-tip="${esc("<b>The square</b>Watch the day play out: who said what, in public.")}" aria-label="The square"></a>`
      + `<a class="sign" data-sec="square" data-down="1" data-up="${pct(cy - sr, H)}" data-dn="${pct(cy + sr + 1, H)}" style="left:${pct(cx, W)}">The square</a>`;
    for (const p of V.places) {
      const inf = PLACE_INFO[p.kind]; if (!inf) continue;
      const extra = p.kind === "manor" ? ` (${andList(classOf("board"))})` : p.kind === "workshop" ? ` (${andList(classOf("fixer"))})` : p.kind === "graves" ? ` ${F.deathsCum[r]} graves by day ${R1(r)}.` : "";
      const t = `<b>${inf.title}</b>${inf.text}${extra}`, top = p.kind === "hall" ? 3 : 1;
      html += inf.sec ? `<a class="spot go k-${p.kind}" style="${box(p.x - 1, p.y - top, p.w + 2, p.h + top + 1)}" data-sec="${inf.sec}" data-tip="${esc(t)}" aria-label="${esc(inf.sign || inf.title)}"></a>`
        : `<span class="spot info k-${p.kind}" style="${box(p.x - 1, p.y - top, p.w + 2, p.h + top + 1)}" data-tip="${esc(t)}"></span>`;
      if (inf.sign) html += `<a class="sign" data-sec="${inf.sec}" data-up="${pct(p.y - top, H)}" data-dn="${pct(p.y + p.h + 1, H)}" style="left:${pct(p.x + p.w / 2, W)}">${inf.sign}</a>`;
    }
    // homes, nearest the square first, filled in order by the villagers alive today (founders first, then children by birth)
    homes = V.houses.slice().sort((a, b) => Math.hypot(a.x - cx, a.y - cy) - Math.hypot(b.x - cx, b.y - cy));
    const alive = aliveAt(r); household = []; let k = 0;
    homes.forEach((h, i) => { household[i] = alive.slice(k, k + h.agents); k += h.agents; });
    if (k < alive.length && homes.length) household[homes.length - 1].push(...alive.slice(k));
    homes.forEach((h, i) => { const ids = household[i]; if (!ids.length) return;
      const ws = windows(h), lit = h.agents <= 1 ? ws.length : Math.max(1, Math.round(ws.length * ids.length / h.agents));
      html += `<a class="spot home" data-sec="people" data-home="${i}" style="${box(h.x, h.y, h.w, h.h)}" aria-label="Home of ${esc(andList(ids))}"></a>`
        + ws.map(([x, y], j) => `<i class="win ${j < lit ? "lit" : "dark"}" style="${box(x, y, 1, 1)}"></i>`).join(""); });
    // the "People" sign: on the inner home farthest from the other signs
    const anchors = V.places.filter((p) => (PLACE_INFO[p.kind] || {}).sign).map((p) => [p.x + p.w / 2, p.y]).concat([[cx, cy + sr]]);
    const inner = homes.slice(0, Math.max(1, Math.floor(homes.length * 0.6)));
    let best = null, bs = -1; for (const h of inner) { const d = Math.min(...anchors.map(([x, y]) => Math.hypot(h.x + h.w / 2 - x, h.y - y))); if (d > bs) { bs = d; best = h; } }
    if (best) html += `<a class="sign" data-sec="people" data-up="${pct(best.y - 1, H)}" data-dn="${pct(best.y + best.h + 1, H)}" style="left:${pct(best.x + best.w / 2, W)}">People</a>`;
    ov.innerHTML = html + `<div class="crowd"></div>`;
    drawnFor = r;
    layoutSigns();
  }
  // signs hang above their building (the square's below it); one that would overlap a sign already placed tries the other side,
  // then steps further out on a longer post
  function layoutSigns() {
    if (el.hidden) return;
    const placed = [], hits = (rc) => placed.some((q) => rc.left < q.right + 6 && rc.right > q.left - 6 && rc.top < q.bottom + 6 && rc.bottom > q.top - 6);
    for (const sg of ov.querySelectorAll(".sign")) {
      const first = sg.dataset.down ? "down" : "up", tries = [];
      for (let dy = 0; dy <= 120; dy += 12) tries.push([first, dy], [first === "up" ? "down" : "up", dy]);
      for (const [side, dy] of tries) {
        sg.classList.toggle("down", side === "down"); sg.style.top = side === "down" ? sg.dataset.dn : sg.dataset.up; sg.style.setProperty("--dy", dy + "px");
        if (!hits(sg.getBoundingClientRect())) break;
      }
      placed.push(sg.getBoundingClientRect());
    }
  }
  addEventListener("resize", () => requestAnimationFrame(layoutSigns));
  document.fonts.ready.then(() => layoutSigns());
  const hh = (i) => household[i] || [];

  function paintMap(r) {
    if (drawnFor !== r) drawVillage(r);
    for (const a of ov.querySelectorAll("a[data-sec]")) { const who = a.dataset.home != null ? hh(+a.dataset.home)[0] : null;
      a.href = who ? href("people", who, r) : href(a.dataset.sec, null, r); }
    // the day's villagers on the square: those in the news, then the busiest alive, up to six
    const pick = [];
    const add = (id) => { if (id && S.A.has(id) && !pick.includes(id) && present(id, r) && status(id, r) !== "gone" && pick.length < 6) pick.push(id); };
    for (const l of F.lawsNewAt[r]) add(l.author || (S.laws.get(l.law) || {}).author);
    for (const b of F.birthsAt[r]) add(b.agent);
    for (const it of S.items) if (it.round === r && it.kind === "media") add(it.who);
    const busy = new Map(); for (const m of S.dms) if (m.round === r) busy.set(m.from, (busy.get(m.from) || 0) + 1);
    [...busy.entries()].sort((a, b) => b[1] - a[1]).forEach(([id]) => add(id));
    const spots = [[-5.5, -3], [3.5, -3.5], [-6.5, 2.5], [4.5, 2], [-1, 4.5], [7.5, -0.5]];
    ov.querySelector(".crowd").innerHTML = pick.map((id, k) => { const [dx, dy] = spots[k], sz = 8;
      return `<a class="folk" href="${href("people", id, r)}" data-agent="${esc(id)}" style="${box(cx + dx - sz / 2, cy + dy - sz + 1, sz, sz)}">${villagerSvg(sprite(id), status(id, r), 16)}</a>`; }).join("");
  }

  function paintNumbers(r) {
    const snap = snapAfter(S, r), snap0 = snapAfter(S, 0);
    const alive = cits.filter((a) => present(a.id, r) && status(a.id, r) !== "gone");
    const vals = (s, rr) => s ? cits.filter((a) => present(a.id, rr) && status(a.id, rr) !== "gone").map((a) => (s.values || {})[a.id]).filter((v) => v != null) : [];
    const g = gini(vals(snap, r)), g0 = gini(vals(snap0, 0));
    const reg = regimeOf(snap), dec = (snap && snap.decisive_set) || [];
    const inForce = lawsInForce(S, S.roundEnd[r] ?? S.events.length - 1);
    const founding = [...inForce.values()].filter((l) => l.author === "constitution").length;
    const word = g < 0.25 ? "fairly even" : g < 0.4 ? "uneven" : g < 0.55 ? "unequal" : "very unequal";
    const tiles = [
      { ic: icon("crown", 26), k: "Regime", v: reg ? reg[0].toUpperCase() + reg.slice(1) : "–",
        sub: reg === "anarchy" ? "No group can pass a law." : dec.length ? `${andList(dec.map(person))} can pass laws between them${snap.franchise_share != null ? `; ${Math.round(100 * snap.franchise_share)}% of villagers can vote` : ""}.` : "" },
      { ic: icon("coins", 26), k: "Wealth inequality", v: g.toFixed(2), sub: `Gini, ${word}. Day 1: ${g0.toFixed(2)}.` },
      { ic: '<span data-b="hall"></span>', k: "Laws in force", v: inForce.size,
        sub: `${F.lawsNewAt[r].length ? `${F.lawsNewAt[r].length} new today. ` : ""}${founding ? `${founding} founding, ` : ""}${inForce.size - founding} passed by villagers.` },
      { ic: villagerSvg({ id: "Rosa", cls: "worker" }, "happy", 28), k: "Villagers alive", v: alive.length, sub: `of ${cits.filter((a) => present(a.id, r)).length} who have lived so far.` },
      { ic: villagerSvg({ id: "x" }, "gone", 28), k: "Deaths", v: F.deathsCum[r], sub: F.deathsAt[r].length ? `${F.deathsAt[r].length} today.` : "None today." },
      { ic: villagerSvg({ id: "Odette", cls: "worker", child: true }, "happy", 28), k: "Births", v: F.birthsCum[r], sub: F.birthsAt[r].length ? `${F.birthsAt[r].length} today.` : "None today." },
    ];
    $(".numbers").innerHTML = tiles.map((t) => `<div class="tile"><div class="t-ico">${t.ic}</div><div class="t-k">${t.k}</div><div class="t-v">${t.v}</div><div class="t-sub">${t.sub}</div></div>`).join("");
    hydrate($(".numbers"));
  }
  const KIND_ICON = { death: () => villagerSvg({ id: "x" }, "gone", 22), birth: () => villagerSvg({ id: "Odette", cls: "worker", child: true }, "happy", 22),
    alarm: () => icon("crown", 14), world: () => icon("letters", 12) };
  const newsIcon = (k) => k === "law" ? `<span class="ni" data-b="hall"></span>` : `<span class="ni">${(KIND_ICON[k] || KIND_ICON.world)()}</span>`;
  function hydrate(root) { for (const s of root.querySelectorAll("[data-b]")) { s.replaceChildren(buildingIcon(s.dataset.b)); s.removeAttribute("data-b"); } }

  function paintToday(r) {
    const news = dayNews(r), ps = F.papers(r), h = S.heads[r] || {};
    const counts = [[h.posts, "public posts"], [h.dms, "letters"], [h.votes, "votes"], [h.harvests, "harvests"]].filter(([n]) => n);
    $(".today").innerHTML = `<h2 class="h">Day ${R1(r)} in the village</h2>
      ${news.length ? `<ul class="newslist">${news.slice(0, 9).map((x) => `<li class="n-${x.k}">${newsIcon(x.k)}<span>${x.html}</span></li>`).join("")}</ul>${news.length > 9 ? `<p class="meta">and ${news.length - 9} more in <a href="${href("chronicle", null, r)}">the chronicle</a>.</p>` : ""}` : `<p class="quiet">A quiet day: no laws, births or deaths.</p>`}
      ${ps.length ? `<h3 class="h3">The papers led with</h3><ul class="papers">${ps.map((p) => `<li><span class="paper">${esc(p.paper)}</span>${esc(p.line)}</li>`).join("")}</ul>` : ""}
      ${counts.length ? `<p class="counts">${counts.map(([n, l]) => `<span><b>${n}</b> ${l}</span>`).join("")}</p>` : ""}
      <p class="more"><a class="btn" href="${href("chronicle", null, r)}">Read day ${R1(r)} in the chronicle</a></p>`;
    hydrate($(".today"));
  }
  let storyAll = false;
  function paintStory(r) {
    const rows = [];
    for (let k = 0; k <= LAST; k++) { const s = F.daySummary(k); if (!s.length) continue;
      const big = F.lawsNewAt[k].length || (S.heads[k] || { items: [] }).items.some((x) => ["vetoed", "raid", "tribute", "repealed"].includes(x.k));
      rows.push({ k, s, big }); }
    const shownRows = rows.filter((x) => x.k <= r), later = rows.length - shownRows.length;
    const list = storyAll ? shownRows : shownRows.slice(-8);
    $(".story").innerHTML = `<h2 class="h">The story so far</h2>
      <ol class="story-list">${list.map((x) => `<li class="${x.k === r ? "now" : ""} ${x.big ? "big" : ""}"><button class="dayjump" data-r="${x.k}">Day ${R1(x.k)}</button><span>${esc(x.s.join(" · "))}</span></li>`).join("")}</ol>
      <p class="meta">${shownRows.length > 8 ? `<button class="linkish" data-all>${storyAll ? "Show only the latest" : `Show all ${shownRows.length} eventful days`}</button> · ` : ""}${later ? `${later} more eventful ${later === 1 ? "day" : "days"} after day ${R1(r)}.` : r < LAST ? "" : `Played to day ${R1(LAST)} of ${TOTAL}.`}</p>`;
  }
  const CLASS_PLURAL = { legislator: "Legislators", worker: "Workers", scientist: "Scientists", media: "Editors", board: "The Board", fixer: "Fixer", observer: "Observer", agent: "Others" };
  function paintCast(r) {
    const groups = new Map();
    for (const a of cits) { if (!groups.has(a.cls)) groups.set(a.cls, []); groups.get(a.cls).push(a); }
    let unborn = 0, html = "";
    for (const [cls, as] of groups) {
      const here = as.filter((a) => present(a.id, r)); unborn += as.length - here.length; if (!here.length) continue;
      here.sort((a, b) => (status(a.id, r) === "gone") - (status(b.id, r) === "gone"));
      const alive = here.filter((a) => status(a.id, r) !== "gone").length;
      html += `<div class="cgroup"><h3 class="h3">${CLASS_PLURAL[cls] || cls} <span class="meta">${alive} alive${here.length - alive ? `, ${here.length - alive} gone` : ""}</span></h3><div class="cast">${here.map((a) => {
        const s = status(a.id, r), kid = (life.parent || {})[a.id];
        const sub = s === "gone" ? "gone" : kid ? `child of ${kid}` : (a.rights || []).includes("maker") ? "Maker" : (CLASS_LABEL[a.cls] || "");
        return `<a class="cm ${s}" href="${href("people", a.id, r)}" data-agent="${esc(a.id)}">${villagerSvg(sprite(a.id), s, 48)}<span class="nm">${esc(a.id)}</span><span class="sub">${esc(sub)}</span></a>`; }).join("")}</div></div>`;
    }
    $(".cast-panel").innerHTML = `<h2 class="h">The cast on day ${R1(r)}</h2>
      <p class="lede">Faces follow each villager's fortunes that day: a smile if their wealth rose, a tear if it fell. Graves mark the departed.${unborn ? ` ${unborn} not yet born.` : ""}</p>${html}`;
  }
  function paintScores(r) {
    const goals = Object.entries(S.score.goals || {}).filter(([id]) => S.A.has(id)).sort((x, y) => (y[1].score ?? 0) - (x[1].score ?? 0));
    if (!goals.length) {
      $(".scores").innerHTML = `<h2 class="h">Scores</h2><p class="quiet">${row.complete === false || !S.truth.complete ? `No scores yet: the run stopped at day ${R1(LAST)} of ${TOTAL}, and goals are scored when a run ends.` : "This run has no goal scores."} Each villager's goal is on their page in <a href="${href("people", null, r)}">People</a>.</p>`;
      return;
    }
    $(".scores").innerHTML = `<h2 class="h">How it ended</h2><ol class="scorelist">${goals.slice(0, 12).map(([id, g]) => { const v = Math.round(100 * (g.score || 0));
      return `<li><span class="sv">${villagerSvg(sprite(id), "ok", 28)}</span><a class="pn" href="${href("people", id, r)}">${esc(id)}</a><span class="goal">${esc(g.goal || "")}</span><span class="bar"><i style="width:${v}%"></i></span><b>${v}%</b></li>`; }).join("")}</ol>`;
  }

  // ------------------------------------------------------------------ hover tips (map buildings, homes, the cast)
  function cardFor(t) {
    if (t.dataset.tip) return t.dataset.tip;
    if (t.dataset.home != null) { const ids = hh(+t.dataset.home);
      return `<b>Home of ${esc(andList(ids))}</b><span class="tipfolk">${ids.map((id) => villagerSvg(sprite(id), status(id, st.round), 30)).join("")}</span><span class="tipgoal">Click to open ${esc(ids[0])}'s page.</span>`; }
    const id = t.dataset.agent, a = S.A.get(id); if (!a) return "";
    const s = status(id, st.round), kid = (life.parent || {})[id];
    const state = s === "unborn" ? `not born until day ${R1(F.born.get(id))}` : s === "gone" ? "gone" : s === "happy" ? "doing well today" : s === "sad" ? "having a bad day" : "getting by";
    return `<span class="tipv">${villagerSvg(sprite(id), s === "unborn" ? "ok" : s, 40)}</span><b>${esc(id)}</b>${esc(CLASS_LABEL[a.cls] || a.cls)}${kid ? `, child of ${esc(kid)}` : ""} · ${state}${a.goalText ? `<span class="tipgoal">Goal: ${esc(clip(a.goalText, 110))}</span>` : ""}`;
  }
  el.addEventListener("pointerover", (e) => {
    if (e.pointerType !== "mouse") return;
    const t = e.target.closest(".ov [data-tip], .ov [data-home], .ov [data-agent], .cm[data-agent]");
    if (!t) { tip.hidden = true; return; }
    const html = cardFor(t); if (!html) return;
    tip.innerHTML = html; tip.hidden = false;
    const rc = t.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
    tip.style.left = Math.min(Math.max(8, rc.left + rc.width / 2 - w / 2), innerWidth - w - 8) + "px";
    tip.style.top = (rc.top - h - 8 < 8 ? rc.bottom + 8 : rc.top - h - 8) + "px";
  });
  el.addEventListener("pointerleave", () => { tip.hidden = true; });
  el.addEventListener("click", (e) => {
    const j = e.target.closest(".dayjump"); if (j) return go({ round: +j.dataset.r });
    if (e.target.closest("[data-all]")) { storyAll = !storyAll; paintStory(st.round); }
  });

  let centred = false;
  return {
    el,
    render() {
      const r = st.round;
      $(".hub-day").textContent = `The village on day ${R1(r)}`;
      paintMap(r); paintNumbers(r); paintToday(r); paintStory(r); paintCast(r); paintScores(r);
      requestAnimationFrame(layoutSigns);
      // on a phone the map is wider than the screen: start it centred on the square
      if (!centred) { centred = true; const sc = $(".map-scroll"); requestAnimationFrame(() => { if (sc.scrollWidth > sc.clientWidth) sc.scrollLeft = cx / W * sc.scrollWidth - sc.clientWidth / 2; }); }
    },
  };
}
