// People: the run's villagers (directory), one villager's character sheet (dossier) and its diary, read indoors.
// Targets: (none) the directory · Fen  Fen's dossier and diary · Fen/m123  the same, at letter (event) 123, marked
// "You came from here". The day comes from the shell's clock.
import { valueAt, moodAt, snapAfter, contacts, parseGoalText, TRAITS } from "../core/model.js";
import { backdrop } from "../scene.js";
import { esc, fmt, clip, R, modelShort, sprite, agentOf, classLabel, who, txt } from "./putil.js";
import { diary, layoutNotes, agentMarks, MARK_KINDS } from "./diary.js";

const store = { get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} } };

export function peopleView(ctx, el) {
  const { S, href } = ctx;
  el.className = "wrap v-people";
  const app = el;
  // the diary's own state; st.round follows the shell's clock
  const st = { S, href, round: S.lastRound, order: store.get("ppl-order", "asc"), hide: new Set(store.get("ppl-hide", [])), fold: store.get("ppl-fold", true), from: null };
  const life = S.truth.life || {}, dead = (S.truth.mortality || {}).dead || {};
  const bornAt = (id) => (life.born || {})[id] ?? 0;
  const goneBy = (id, r) => S.departs.has(id) && S.roundAt[S.departs.get(id)] <= r;
  const deathOf = (id) => dead[id] || (S.departs.has(id) ? { round: S.roundAt[S.departs.get(id)], cause: "left" } : null);
  const causeText = (d) => !d ? "" : d.cause === "old_age" ? "died of old age" : d.cause === "attack" || d.cause === "assassin" ? `disabled${d.by ? " by " + d.by : ""}` : String(d.cause || "left").replace(/_/g, " ");
  const glyph = (k) => (MARK_KINDS.find((m) => m[0] === k) || [])[1] || "•";

  // ------------------------------------------------------------------ directory
  function villagerTile(id) {
    const r = st.round, gone = goneBy(id, r), mood = moodAt(S, id, r), d = gone ? deathOf(id) : null;
    const v = gone ? null : valueAt(S, id, r + 1), a = S.A.get(id);
    return `<a class="vill${gone ? " gone" : ""}" href="${href("people", id, r)}" title="${esc(a.goalText ? "Secret goal: " + clip(a.goalText, 160) : id)}">
      <span class="vill-sp">${sprite(S, id, 64, mood)}${gone ? `<span class="mini">${sprite(S, id, 30, "ok")}</span>` : ""}</span>
      <b class="vill-nm">${esc(id)}</b>
      <span class="vill-cl">${esc(classLabel(S, id))}</span>
      <span class="vill-v">${gone ? `† day ${R(d.round)}` : `<i class="coin"></i>${fmt(v)}`}</span></a>`;
  }
  function directory() {
    const r = st.round;
    const here = S.agents.filter((a) => bornAt(a.id) <= r);
    const founders = here.filter((a) => !agentOf(S, a.id).child);
    const nGone = here.filter((a) => goneBy(a.id, r)).length, nBorn = here.length - founders.length;
    const label = (id) => classLabel(S, id);
    const groups = new Map();
    const order = ["Legislator", "Worker", "Maker", "Scientist", "Editor", "Board", "Fixer", "Secret observer", "Child", "Agent"];
    for (const a of here) { const k = label(a.id); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(a); }
    const body = [...groups.entries()].sort((x, y) => order.indexOf(x[0]) - order.indexOf(y[0])).map(([k, xs]) =>
        `<section class="cgroup"><h3 class="kick">${esc(xs.length > 1 ? ({ Child: "Children", Board: "Board members", "Secret observer": "Secret observers" }[k] || k + "s") : k === "Board" ? "Board member" : k)} <span>${xs.length}</span></h3>
          <div class="hrow">${xs.map((a) => villagerTile(a.id)).join("")}</div></section>`).join("");
    return `<section class="dir">
      <div class="dir-top">
        <div><h2 class="h2">The villagers</h2>
          <p class="lede">${founders.length} founders${nBorn ? `, ${nBorn} born since` : ""}${nGone ? ` · <b>${nGone} gone</b> by day ${R(r)}` : ""}. Faces show how each one's fortunes moved in this round; graves mark the gone.</p></div>
      </div>
      ${body}
      <p class="legend"><span>${sprite(S, "Kasper", 26, "happy")} richer this round</span><span>${sprite(S, "Kasper", 26, "ok")} steady</span><span>${sprite(S, "Kasper", 26, "sad")} poorer</span><span>${sprite(S, "Kasper", 26, "gone")} gone</span></p>
    </section>`;
  }

  // ------------------------------------------------------------------ dossier (character sheet)
  const card = (title, body, cls = "") => body ? `<section class="sheet px ${cls}"><h3 class="kick">${title}</h3>${body}</section>` : "";
  const pct = (x) => (x == null ? "–" : Math.round(100 * x) + "%");
  function goalsCard(a) {
    const idx = S.roundEnd[st.round] ?? S.events.length - 1, g = a.goal || {}, ch = S.gchanges.get(a.id) || [];
    if (g.fixed || !a.goalText) return `<p>${esc(a.goalText || g.primary || "No private goal recorded.")}</p>`;
    const sc = (S.score.goals || {})[a.id] || {};
    const past = ch.filter((c) => c.i <= idx), future = ch.filter((c) => c.i > idx);
    let text = a.goalText; const names = { primary: g.primary, secondary: g.secondary, tertiary: g.tertiary };
    if (past.length) { const c = past[past.length - 1]; text = c.new_text || text; names.primary = c.new || names.primary; }
    else if (future.length && future[0].old_text) { text = future[0].old_text; names.primary = future[0].old || names.primary; }
    const scores = { primary: sc.primary, secondary: sc.secondary_score, tertiary: sc.tertiary_score };
    return `${past.map((c) => `<p class="dim">Until day ${R(c.round)}: <s>${esc(c.old || "an earlier goal")}</s></p>`).join("")}
      ${parseGoalText(text || "").map((p) => `<div class="goal"><div class="goal-h"><b>${esc(names[p.label] || p.label)}</b><span class="tag">${p.pct}%</span></div>
        <p>${txt(st, p.text)}</p>${scores[p.label] != null ? `<div class="meter" title="Final score"><i style="width:${pct(scores[p.label])}"></i></div><span class="dim small">final score ${pct(scores[p.label])}</span>` : ""}</div>`).join("")}
      ${future.length ? `<p class="dim">This goal changes in day ${R(future[0].round)}.</p>` : ""}`;
  }
  function temperCard(a) {
    if (!a.personality) return "";
    return `<div class="traits">${TRAITS.filter(([k]) => a.personality[k] != null).map(([k, lo, hi]) => { const x = a.personality[k], cell = Math.min(9, Math.floor(x * 10));
      return `<span class="tl">${lo}</span><span class="cells" title="${k} ${Math.round(100 * x)}%">${Array.from({ length: 10 }, (_, j) => `<i class="${j === cell ? "on" : ""}"></i>`).join("")}</span><span class="tr">${hi}</span>`; }).join("")}</div>
      ${a.atext || a.ptext ? `<p class="quote">“${esc(a.ptext || a.atext)}”</p>` : ""}`;
  }
  const ITEM_COL = { stone: "#a8a29a", timber: "#a0662f", copper: "#e8803a", silver: "#d6f0f2", gold: "#e8c060", coin: "#e8c060" };
  function fortunesCard(id) {
    const L = S.lastRound, d = deathOf(id), lastK = d ? d.round : L + 1, b = bornAt(id);
    const vals = []; for (let k = 1; k <= L + 1; k++) vals.push(k <= lastK && k > b ? (valueAt(S, id, k) ?? null) : null);
    const hi = Math.max(1, ...vals.filter((x) => x != null));
    const v0 = valueAt(S, id, b), peak = Math.max(...vals.filter((x) => x != null)), peakR = vals.indexOf(peak);
    const bars = vals.map((v, k) => `<i class="${k === st.round ? "now" : ""}${v == null ? " none" : ""}" style="height:${v == null ? 0 : Math.max(4, Math.round(100 * v / hi))}%" title="Round ${k + 1}: ${v == null ? "–" : fmt(v)}"></i>`).join("");
    const snap = snapAfter(S, Math.min(st.round, d ? Math.max(0, d.round - 1) : st.round));
    const hold = Object.entries(((snap || {}).holdings || {})[id] || (st.round < 0 ? {} : {})).filter(([, q]) => q > 0.0005);
    const vNow = valueAt(S, id, st.round + 1);
    return `<p class="big"><i class="coin"></i>${goneBy(id, st.round) ? `${fmt(valueAt(S, id, lastK))} <span class="dim small">when gone</span>` : fmt(vNow)} <span class="dim small">${goneBy(id, st.round) ? "" : `worth after day ${R(st.round)}`}</span></p>
      <div class="bars" aria-label="Worth after each round">${bars}</div>
      <p class="dim small">${v0 != null ? `Started with ${fmt(v0)}` : ""}${isFinite(peak) ? `, peaked at ${fmt(peak)} (round ${peakR + 1})` : ""}.</p>
      <h4 class="sub">${goneBy(id, st.round) ? `Holdings when gone (day ${R(d.round)})` : `Holdings, day ${R(st.round)}`}</h4>
      <p class="chips-row">${hold.map(([k, q]) => `<span class="item"><i style="background:${ITEM_COL[k] || "#9ccfe0"}"></i>${esc(k)} <b>${fmt(q)}</b></span>`).join("") || '<span class="dim">nothing</span>'}</p>`;
  }
  function rightsCard(a) {
    const log = []; S.events.forEach((e, k) => { const d = e.data || {}; if (e.type === "rights" && d.agent === a.id && S.roundAt[k] <= st.round)
      log.push(`<li><span class="tag">r${R(S.roundAt[k])}</span> ${d.change === "grant" ? "gains" : "loses"} <b>${esc(String(d.right).replace(/_/g, " "))}</b></li>`); });
    return `<p class="chips-row">${(a.rights || []).map((x) => `<span class="chip">${esc(x.replace(/_/g, " "))}</span>`).join("") || '<span class="dim">none</span>'}</p>
      ${log.length ? `<ul class="log">${log.join("")}</ul>` : ""}`;
  }
  function lifeCard(id) {
    const b = bornAt(id), dies = (life.dies_at || {})[id], d = deathOf(id), L = S.lastRound, r = st.round;
    const raw = (S.inst.agents || []).concat(S.truth.arrived_agents || []).find((x) => x.id === id) || {};
    const kids = Object.entries(life.parent || {}).filter(([c, p]) => p === id && bornAt(c) <= r).map(([c]) => c);
    const made = Object.entries(life.maker_of || {}).filter(([c, m]) => m === id && bornAt(c) <= r).map(([c]) => c);
    const victims = Object.entries(dead).filter(([, x]) => x.by === id && x.round <= r);
    const face = (x, mood) => `<a class="face${!mood && goneBy(x, r) ? " ghost" : ""}" href="${href("people", x)}" title="${esc(x)}">${sprite(S, x, 34, mood ?? (goneBy(x, r) ? "ok" : moodAt(S, x, r)))}<span>${esc(x)}</span></a>`;
    const rowv = (k, v) => v ? `<div class="kv"><dt>${k}</dt><dd>${v}</dd></div>` : "";
    const sent = S.dms.filter((m) => m.from === id && m.round <= r), got = S.dms.filter((m) => m.to === id && m.round <= r);
    const dml = ((snapAfter(S, Math.min(r, L)) || {}).dm_limit || {})[id];
    return `<dl class="kvs">
        ${rowv("Born", b ? `day ${R(b)}${(life.parent || {})[id] ? `, child of ${who(st, life.parent[id])}${(life.maker_of || {})[id] ? `, made by ${who(st, life.maker_of[id])}` : ""}` : ""}` : "at the start")}
        ${rowv("Lifespan", dies != null ? (dies > L ? "outlives the game" : `to the end of day ${R(dies)}`) : "")}
        ${rowv("Ended", d && d.round <= r ? `<b>day ${R(d.round)}</b>, ${esc(causeText(d))}` : d ? "" : "in play to the end")}
        ${rowv("Each turn", `${raw.actions ?? "?"} actions${dml != null ? ` · ${dml} letters a round` : ""}`)}
        ${rowv("Letters", `${sent.length} sent to ${new Set(sent.map((m) => m.to)).size} · ${got.length} received`)}
      </dl>
      ${kids.length ? `<h4 class="sub">Children</h4><div class="faces">${kids.map((x) => face(x)).join("")}</div>` : ""}
      ${made.length ? `<h4 class="sub">Made, as a Maker</h4><div class="faces">${made.map((x) => face(x)).join("")}</div>` : ""}
      ${victims.length ? `<h4 class="sub danger">Disabled</h4><div class="faces">${victims.map(([x, v]) => face(x, "gone").replace("</span></a>", ` · r${R(v.round)}</span></a>`)).join("")}</div>` : ""}`;
  }
  const face30 = (p) => sprite(S, p, 30, goneBy(p, st.round) ? "ok" : moodAt(S, p, st.round));
  function friendsCard(id) {
    const idx = S.roundEnd[st.round] ?? S.events.length - 1;
    const cs = contacts(S, id, idx).slice(0, 8);
    if (!cs.length) return `<p class="dim">Has not written to or traded with anyone yet.</p>`;
    const max = Math.max(1, ...cs.map(([, c]) => c.out + c.in));
    return `<ul class="friends">${cs.map(([p, c]) => `<li><a href="${href("people", p)}"${goneBy(p, st.round) ? ' class="ghost" title="gone"' : ""}>${face30(p)}<b>${esc(p)}</b></a>
      <span class="fbar" title="${c.out} sent · ${c.in} received"><i class="o" style="width:${Math.round(100 * c.out / max)}%"></i><i class="n" style="width:${Math.round(100 * c.in / max)}%"></i></span>
      <span class="dim small">${c.out}↗ ${c.in}↙${c.tx || c.rx ? ` · gifts ${c.tx}/${c.rx}` : ""}</span></li>`).join("")}</ul>
      <p class="key"><span><i class="o"></i>sent</span><span><i class="n"></i>received</span></p>`;
  }
  function momentsCard(id) {
    const ms = [...agentMarks(S, id).entries()].filter(([k]) => k <= st.round).sort((a, b) => a[0] - b[0]);
    if (!ms.length) return "";
    return `<ol class="moments">${ms.map(([k, xs]) => xs.map((m) => `<li class="${m.k}"><a href="#r${R(k)}" data-goto-round="${R(k)}"><span class="tag">r${R(k)}</span><b>${glyph(m.k)}</b> ${esc(m.text)}</a></li>`).join("")).join("")}</ol>`;
  }
  function dossier(id) {
    const a = S.A.get(id), r = st.round, d = deathOf(id), gone = goneBy(id, r), unborn = bornAt(id) > r;
    const status = unborn ? `<span class="pill">born in day ${R(bornAt(id))}</span>` : gone ? `<span class="pill grave">gone · day ${R(d.round)} · ${esc(causeText(d))}</span>`
      : `<span class="pill ok">alive in day ${R(r)}</span>`;
    const g = parseGoalText(a.goalText || "")[0];
    const dia = unborn ? { html: `<p class="dim">${esc(id)} is not born yet in day ${R(r)}.</p>` } : diary(st, id);
    return `<nav class="crumbs"><a href="${href("people", null, r)}">← All villagers</a></nav>
    <section class="dossier">
      <aside class="portrait px">
        <div class="stage"><canvas class="stage-sky" data-seed="${esc(id)}" aria-hidden="true"></canvas><span class="stage-sp">${sprite(S, id, 112, unborn || gone ? "ok" : moodAt(S, id, r))}</span>${gone ? `<span class="stage-grave">${sprite(S, id, 56, "gone")}</span>` : ""}</div>
        <h2 class="name">${esc(id)}</h2>
        <p class="cls">${esc(classLabel(S, id))}${a.archetype ? ` · <span>${esc(a.archetype)}</span>` : ""}</p>
        <p class="model"><span class="tag">${esc(modelShort(a.model))}</span>${a.tier ? ` <span class="dim small">${esc(a.tier)} tier</span>` : ""}</p>
        ${status}
        <a class="btn" href="#diary">Read the diary ↓</a>
      </aside>
      <div class="sheets">
        ${card("Secret goals", goalsCard(a), "wide")}
        ${card("Fortunes", fortunesCard(id))}
        ${card("Life &amp; family", lifeCard(id))}
        ${card("Temperament", temperCard(a))}
        ${card("Closest contacts", friendsCard(id))}
        ${card("Key moments", momentsCard(id))}
        ${card("Rights", rightsCard(a))}
      </div>
    </section>
    <section class="diary" id="diary">
      <div class="band px"><span class="band-sp">${sprite(S, id, 34, unborn || gone ? "ok" : moodAt(S, id, r))}</span>
        <div class="band-who"><b>${esc(id)}'s diary</b><span class="dim small">${esc(classLabel(S, id))} · ${esc(modelShort(a.model))}</span></div>
        <div class="band-goal">${g ? `<span class="dim small">Goal${g.pct < 100 ? ` (${g.pct}%)` : ""}</span> ${esc(clip(g.text, 140))}` : ""}</div>
        <div class="band-now">to day <b>${R(r)}</b></div></div>
      <p class="intro">What ${esc(id)} read, thought, did and wrote, day by day. Its private reasoning runs down the middle; letters it received are pinned in the left margin where it first read them, letters it sent in the right margin beside the call that sent them.</p>
      ${dia.html}
    </section>`;
  }


  function relayout() { const tl = app.querySelector(".timeline"); if (tl) layoutNotes(tl); }
  let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => { if (!el.hidden) relayout(); }, 120); });
  let last = null, pending = null;
  function render(opts = {}) {
    const t = ctx.st.target || "", m = /^([^/]*)(?:\/m(\d+))?$/.exec(t) || [];
    const id = m[1] || "", msg = m[2] ? +m[2] : null, page = opts.page || last !== id;
    st.round = ctx.st.round; st.from = msg;
    const y = window.scrollY;
    const agent = id && S.A.has(id);
    document.body.classList.toggle("indoor", !!agent);   // an agent's page is read indoors: warm paper, not the night sky
    // its private reasoning comes in its own file (split uploads): fetch it once, then draw the page
    if (agent && !S.fullReasoning.has(id)) {
      if (pending !== id) {
        pending = id;
        app.innerHTML = `<p class="loading">Opening ${esc(id)}'s diary…</p>`;
        ctx.loadReasoning(id).then((xs) => S.setReasoning(id, xs), (e) => { console.warn("reasoning", id, e); S.fullReasoning.add(id); })
          .then(() => { pending = null; if ((ctx.st.target || "").split("/")[0] === id && !el.hidden) render({ page: true }); });
      }
      return;
    }
    app.innerHTML = agent ? dossier(id) : directory();
    app.dataset.view = agent ? "agent" : "dir";
    last = id;
    const cv = app.querySelector(".stage-sky");
    if (cv) backdrop(cv, cv.dataset.seed, { width: 120, height: 64, ground: "meadow", town: false });
    relayout();
    if (msg != null && page) {
      const lt = app.querySelector(`.letter[data-msg="${msg}"]`);
      if (lt) { const rd = lt.closest(".tl-round"); if (rd) rd.classList.remove("folded"); relayout(); setTimeout(() => lt.scrollIntoView({ block: "center" }), 30); }
    } else if (!page) window.scrollTo(0, y);
  }
  app.addEventListener("click", (e) => {
    const t = e.target;
    const kind = t.closest("[data-kind]");
    if (kind) { const k = kind.dataset.kind; st.hide.has(k) ? st.hide.delete(k) : st.hide.add(k); store.set("ppl-hide", [...st.hide]);
      kind.classList.toggle("on", !st.hide.has(k)); app.querySelector(".timeline").classList.toggle("hide-" + k, st.hide.has(k)); return relayout(); }
    if (t.closest("[data-foldall]")) { st.fold = !st.fold; store.set("ppl-fold", st.fold); return render(); }
    const ord = t.closest("[data-order]"); if (ord) { st.order = ord.dataset.order; store.set("ppl-order", st.order); return render(); }
    const fold = t.closest(".tl-fold"); if (fold) { fold.closest(".tl-round").classList.remove("folded"); return relayout(); }
    const fm = t.closest(".fold-me"); if (fm) { fm.closest(".tl-round").classList.add("folded"); return relayout(); }
    const more = t.closest(".lt-more"); if (more) { const l = more.closest(".letter"); l.classList.toggle("open"); more.textContent = l.classList.contains("open") ? "fold" : "read all"; return relayout(); }
    const step = t.closest("[data-round-step]"); if (step) { e.preventDefault(); return ctx.go({ round: Math.max(0, Math.min(S.lastRound, st.round + +step.dataset.roundStep)) }); }
    const go = t.closest("[data-goto-round]");
    if (go) { e.preventDefault(); const sec = document.getElementById("r" + go.dataset.gotoRound); if (sec) { sec.classList.remove("folded"); relayout(); sec.scrollIntoView({ behavior: "smooth", block: "start" }); } return; }
    const anchor = t.closest('a[href="#diary"]');
    if (anchor) { e.preventDefault(); document.getElementById("diary").scrollIntoView({ behavior: "smooth" }); }
  });
  app.addEventListener("toggle", () => relayout(), true);   // a "Show all" opened inside the journal
  return { el, render, leave() { document.body.classList.remove("indoor"); } };
}
