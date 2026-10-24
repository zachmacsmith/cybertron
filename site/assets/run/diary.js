// The diary: one agent's run as a journal. Each round's private reasoning, plans, look-ups, notes and actions run down the
// middle; letters it received sit in the left margin at the call that first showed them, letters it sent in the right margin
// beside the call that sent them. A round goes: first call, reply waves (in DM-step runs), then the actions that ran.
// The placement logic follows the current site (assets/run/views.js: readAt, dmWaves, roundRows, timeline); the markup is ours.
import * as M from "../core/model.js";
import { esc, clip, fmt, R, who, sprite, txt, para, md, lawRef, agentOf } from "./putil.js";

const args = (a) => { try { return a.args && typeof a.args === "object" ? a.args : JSON.parse(a.args_json || "{}"); } catch (e) { return {}; } };
const LOOK = { manual: (x) => x.section, manual_search: (x) => `“${x.query}”`, search_board: (x) => `“${x.query}”`, search_dms: (x) => `“${x.query}”`,
  recent: (x) => x.kind || x.what || "", read_file: (x) => x.name, read_law: (x) => x.law, read_archive: (x) => x.doc || x.id };
const ACT_VERB = { harvest: "harvests", vote: "votes", post: "posts", anon_post: "posts anonymously", propose: "proposes", repeal: "moves to repeal",
  pay_tribute: "pays tribute", publish: "publishes", write_digest: "writes the digest", report: "reports", read_archive: "reads", search_archive: "searches the archive",
  write_archive: "writes to the archive", run_python: "runs code", patch: "patches", transfer: "sends", deposit: "deposits", redeem: "redeems", veto: "vetoes",
  dm: "messages", contribute: "contributes", lend: "offers a loan", accept_loan: "takes a loan", repay_loan: "repays", pass: "waits", attack: "attacks",
  commission: "commissions a child", build: "builds", name_successor: "names a successor", forge: "forges" };

function longText(st, s, n = 520) {
  s = String(s || "");
  if (s.length <= n) return para(st, s);
  return `${para(st, s.slice(0, n).replace(/\s+\S*$/, "") + " …")}<details class="more"><summary>Show all · ${Math.round(s.length / 100) / 10}k characters</summary>${para(st, s)}</details>`;
}
export function actLine(st, action, x) {
  const what = { harvest: `${x.camp ? `at ${esc(x.camp)}` : ""}${x.x != null ? ` (dial ${esc(JSON.stringify(x.x))})` : ""}`, vote: `<b>${esc(x.choice ?? "")}</b> on ${esc(x.ballot ?? "")}`,
    transfer: `${esc(x.qty)} ${esc(x.item)} to ${x.to ? who(st, x.to) : ""}`, post: "publicly", anon_post: "anonymously",
    propose: x.title ? `“${esc(x.title)}”` : (String(x.code || "").match(/title\s*=\s*["']([^"']+)/) || [])[1] ? `“${esc(String(x.code).match(/title\s*=\s*["']([^"']+)/)[1])}”` : "",
    repeal: lawRef(st, x.law), read_archive: esc(x.doc || x.id || ""), search_archive: `“${esc(x.query || "")}”`, commission: x.maker ? `from ${who(st, x.maker)}` : "",
    attack: x.target ? who(st, x.target) : "", name_successor: x.successor ? who(st, x.successor) : "", read_law: lawRef(st, x.law) }[action];
  return `<b>${esc(ACT_VERB[action] || String(action || "").replace(/_/g, " "))}</b> ${what ?? esc(clip(Object.entries(x).filter(([, v]) => typeof v !== "object").map(([k, v]) => `${k} ${v}`).join(" · "), 120))}`;
}

// a letter in the margin. dir "in": received (shows who it says it is from, and who really sent it if forged); "out": sent
function letter(st, m, dir) {
  const S = st.S, other = dir === "in" ? (m.shownAs || m.from) : m.to, peer = dir === "in" ? m.from : m.to;
  const forged = dir === "in" && m.shownAs && m.shownAs !== m.from ? ` <span class="really">really ${esc(m.from)}</span>` : "";
  const came = st.from === m.i;
  const name = m.pub ? "" : `<a class="lt-who" href="${st.href("people", `${peer}/m${m.i}`)}" title="Read this in ${esc(peer)}'s diary">${esc(other)}</a>`;
  const long = String(m.text || "").length > 320;
  return `${came ? '<div class="came-from">You came from here</div>' : ""}<article class="letter ${dir}${m.pub ? " pub" : ""}${long ? " long" : ""}${came ? " here" : ""}" data-msg="${m.i ?? ""}">
    <header>${m.pub ? '<span class="lt-pub">Public post</span>' : `${sprite(S, other, 22, M.moodAt(S, other, m.round))}<span>${dir === "in" ? `from ${name}${forged}` : `to ${name}`}</span>`}</header>
    <div class="lt-b">${txt(st, m.text || (m.enc ? "(sealed)" : ""))}</div>${long ? '<button class="lt-more" type="button">read all</button>' : ""}</article>`;
}

const norm = (t) => String(t || "").replace(/\s+/g, " ").trim().slice(0, 160);
const waveOf = (phase) => phase === "decide" ? 0 : /^dm_reply_(\d+)$/.test(String(phase)) ? +String(phase).slice(9) : null;
function readAt(S) {
  if (S._readAt) return S._readAt;
  const at = new Map();
  for (const [aid, xs] of S.reas) for (const x of xs) {
    const sec = x.phase === "decide" || x.phase === "lookup" ? 0 : waveOf(x.phase);
    if (sec == null) continue;
    for (const id of x.saw || []) at.set(`${id}|${aid}`, [x.round, sec]);
  }
  return (S._readAt = at);
}
const evId = (S, m) => (S.events[m.i] || {}).id;
function dmWaves(S) {
  if (S._dmWave) return S._dmWave;
  const RA = readAt(S), plans = new Map(), W = new Map();
  for (const [aid, xs] of S.reas) for (const x of xs) {
    const w = waveOf(x.phase); if (w == null) continue;
    // the messages this call planned: from its actions, or (in a split upload) the dm_texts kept for exactly this
    const texts = x.dm_texts || (x.actions || []).map((a) => args(a).text).filter((t) => typeof t === "string").map(norm);
    for (const t of texts) { const key = `${x.round}|${aid}`; if (!plans.has(key)) plans.set(key, []); plans.get(key).push({ w, t, used: false }); }
  }
  for (const m of S.dms) {
    const c = (plans.get(`${m.round}|${m.from}`) || []).filter((o) => !o.used && o.t === norm(m.text)).sort((a, b) => a.w - b.w)[0];
    if (c) c.used = true;
    W.set(m.i, c ? c.w : null);
  }
  S._dmStep = [...S.reas.values()].some((xs) => xs.some((x) => /^dm_reply_/.test(String(x.phase))));
  if (S._dmStep) for (const m of S.dms) {
    if (W.get(m.i) != null) { m._exact = true; continue; }
    const t = RA.get(`${evId(S, m)}|${m.to}`);
    if (!t) continue;
    if (t[0] === m.round && t[1] >= 1) W.set(m.i, t[1] - 1);
    else if (t[0] > m.round) W.set(m.i, Math.max(0, ...(S.reas.get(m.from) || []).filter((x) => x.round === m.round).map((x) => waveOf(x.phase) || 0)));
    m._exact = true;
  }
  if (S._dmStep) {
    const first = new Map();
    for (const m of S.dms) { const w = W.get(m.i); if (w) { const key = `${m.round}|${w}`; first.set(key, Math.min(first.get(key) ?? Infinity, m.i)); } }
    for (const m of S.dms) if (W.get(m.i) == null && !m._exact)
      W.set(m.i, m.i >= (first.get(`${m.round}|2`) ?? Infinity) ? 2 : m.i >= (first.get(`${m.round}|1`) ?? Infinity) ? 1 : 0);
  }
  return (S._dmWave = W);
}
const notesRow = (st, prev, next) => next === prev ? `<p class="dim">Rewrites its notes unchanged.</p>` : `<div class="scratch">${para(st, next)}</div>`;

// the rows of one round: {kind, label, body, inn: [letters read here], out: html in the right margin}
function roundRows(st, id, k, turn, reasons, looks, sent, inboxBy, mem) {
  const S = st.S, W = dmWaves(S), rows = [];
  const sep = (label, inn, icon) => rows.push({ kind: "sep", label, icon, body: "", inn });
  let pendingIn = inboxBy.get(0) || [];
  const push = (kind, label, body, extra = {}) => { if (!body) return; rows.push({ kind, label, body, ...extra, ...(pendingIn.length ? { inn: pendingIn } : {}) }); pendingIn = []; };
  const think = (x) => {
    if (!x) return;
    if (x.reasoning) push("think", "Thinks", `<div class="prose">${md(para(st, x.reasoning))}</div>`);
    if (x.stated_reasoning) push("plan", "Plans", `<div class="prose">${md(para(st, x.stated_reasoning))}</div>`);
    if (x.error) push("err", "Error", `<p class="dim">${esc(clip(x.error, 300))}</p>`);
  };
  const sends = (ms) => ms.forEach((m) => push("send", "Writes", `<p>A private letter to ${who(st, m.to)}.</p>`, { out: letter(st, m, "out"), to: m.to }));
  const reads = (ls) => ls.forEach((l) => { const what = (LOOK[l.name] || (() => ""))(l.args || {}) || "";
    push("read", "Looks up", `<div class="readh"><b>${esc(String(l.name).replace(/_/g, " "))}</b> ${esc(what)}</div>`); });
  for (const g of S.gchanges.get(id) || []) if (g.round === k) push("goal", "Goal", `<p>Its goal changes: ${esc(g.old || "")} → <b>${esc(g.new || "")}</b></p>`);
  const ph = (p) => reasons.find((x) => x.phase === p);
  const decide = ph("decide"), lookupCall = ph("lookup");
  const bound = [1, 2].map((w) => Math.min(...S.dms.filter((m) => m.round === k && W.get(m.i) === w).map((m) => m.i)));
  const lkey = (s) => String(s || "").replace(/\s+/g, "");
  const answered = new Map();
  for (const w of [1, 2]) for (const a of (ph(`dm_reply_${w}`) || {}).lookup_results || []) answered.set(lkey(a.head), w);
  const lookWave = (l) => { const w = answered.get(lkey(`Lookup ${l.name} ${JSON.stringify(l.args || {})}`));
    return w != null ? w - 1 : l.i >= bound[1] ? 2 : l.i >= bound[0] ? 1 : 0; };
  const answers = (w) => ((ph(`dm_reply_${w}`) || {}).lookup_results || []).forEach((a) =>
    push("read", "Reads", `<div class="readh">${esc(a.head.replace(/^Lookup\s+/, "").replace(/_/g, " "))} <span class="dim">(answer to its look-up)</span></div><div class="readb">${longText(st, a.text)}</div>`));
  const sentIn = (w) => sent.filter((m) => W.get(m.i) === w).sort((a, b) => a.i - b.i);
  const waves = [1, 2].filter((w) => ph(`dm_reply_${w}`) || (inboxBy.get(w) || []).length);
  // 1. the first call
  if (waves.length || lookupCall) sep("First call", null, "sun");
  if (lookupCall) { think(lookupCall); sep("After its look-ups", null, "eye"); }
  think(decide);
  sends(sentIn(0));
  reads(looks.filter((l) => lookWave(l) === 0));
  const isDm = (a) => ["dm", "reply", "forge_dm"].includes(a.action);
  const planOf = (acts) => (acts || []).filter((a) => !isDm(a) && a.action !== "write_scratchpad").map((a) => actLine(st, a.action, args(a)));
  if (decide && decide.final_actions && waves.length) {
    const first = planOf(decide.actions), fin = planOf(decide.final_actions);
    if (first.length && first.join() !== fin.join()) push("plan", "First plan", `<ul class="planlist">${first.map((h) => `<li>${h}</li>`).join("")}</ul><p class="dim">Changed during the replies; what ran is below.</p>`);
  }
  // 2. the reply waves
  for (const w of waves) {
    sep(`Reply wave ${w}`, inboxBy.get(w) || [], "mail");
    answers(w);
    think(ph(`dm_reply_${w}`));
    sends(sentIn(w));
    reads(looks.filter((l) => lookWave(l) === w));
  }
  // 3. what ran
  if (turn) {
    const wroteNotes = turn.acts.some((a) => a.action === "write_scratchpad");
    if (!wroteNotes && decide && decide.notes) { push("notes", "Notes", notesRow(st, mem.notes, decide.notes)); mem.notes = decide.notes; }
    if (waves.length) sep("Final actions", null, "hammer");
    const nAct = turn.acts.length, res = turn.res.slice(turn.res.length - nAct), loose = sentIn(null);
    turn.acts.forEach((a, j) => {
      const x = args(a), r = res[j] != null ? String(res[j]) : "";
      if (a.action === "write_scratchpad") {
        const next = x.mode === "append" && mem.notes ? `${mem.notes}\n${x.text || ""}` : String(x.text || "");
        const html = notesRow(st, mem.notes, next); mem.notes = next;
        return push("notes", "Notes", html);
      }
      if (isDm(a)) { const m = loose.find((mm) => !mm._shown && norm(mm.text) === norm(x.text)); if (m) { m._shown = true; return sends([m]); } }
      const out = a.action === "post" || a.action === "anon_post" ? letter(st, { from: id, text: x.text, round: k, pub: true }, "out") : "";
      const isRead = /^(read_|search_|manual|recent|survey)/.test(a.action);
      const ans = r.replace(/^[\w ]+:\s*/, ""), err = /ERROR/.test(r);
      push(isRead ? "read" : "act", isRead ? "Reads" : "Does", `<div class="acth">${actLine(st, a.action, x)}</div>
        ${ans && a.action !== "post" ? `<div class="${isRead ? "readb" : "actr"}${err ? " err" : ""}">${isRead ? longText(st, ans) : txt(st, clip(ans, 260))}</div>` : ""}`, { out, verb: a.action });
    });
    sends(loose.filter((m) => !m._shown));
    loose.forEach((m) => delete m._shown);
  } else sends(sentIn(null));
  if (pendingIn.length) sep("Received", pendingIn, "mail");
  // letters sent one after another share a row
  const out = [];
  for (const x of rows) { const last = out[out.length - 1];
    if (x.kind === "send" && last && last.kind === "send" && !x.inn) { last.to.push(x.to); last.out += x.out; } else out.push(x.kind === "send" ? { ...x, to: [x.to] } : x); }
  for (const x of out) if (x.kind === "send" && x.to.length > 1) {
    const names = x.to.filter((t, j) => x.to.indexOf(t) === j).map((t) => who(st, t));
    x.body = `<p>${x.to.length} private letters to ${names.length > 1 ? names.slice(0, -1).join(", ") + " and " + names[names.length - 1] : names[0]}.</p>`; }
  return out;
}

export const DIARY_KINDS = [["think", "Thinking"], ["plan", "Plans"], ["read", "Reads"], ["notes", "Notes"], ["act", "Actions"], ["msgs", "Letters"]];
const ROUTINE = new Set(["harvest", "camp_submit", "vote", "write_scratchpad", "subscribe", "unsubscribe", "pass", "recent"]);
const TELLING = /\b(attack|assassin|kill|disabl|betray|deceiv|lie to|lying|secret|hidden goal|bribe|steal|forg|weapon|spy|sabotag|blackmail|threat)/i;
function closeVote(S, a) {
  if (a.action !== "vote") return false;
  const b = S.ballots.get(args(a).ballot); if (!b || !b.final) return false;
  const vs = Object.values(b.final), yes = vs.filter((x) => x === "yes").length, no = vs.filter((x) => x === "no").length;
  return Math.abs(yes - no) <= 1;
}
const ICON = { sun: "☀", eye: "◉", mail: "✉", hammer: "⚒" };
const glyph = (k) => (MARK_KINDS.find((m) => m[0] === k) || [])[1] || "•";

// st: { S, round (read up to), order "asc"|"desc", hide: Set, fold: bool, from: message index or null }
export function diary(st, id) {
  const S = st.S, r = st.round, idx = S.roundEnd[r] ?? S.events.length - 1, asc = st.order !== "desc";
  const turns = new Map((S.turns.get(id) || []).map((t) => [t.round, t]));
  const by = (xs) => { const m = new Map(); for (const x of xs) { if (!m.has(x.round)) m.set(x.round, []); m.get(x.round).push(x); } return m; };
  const reas = by(S.reas.get(id) || []), looks = by(S.lookups.get(id) || []), sent = by(S.dms.filter((m) => m.from === id));
  const all = [...new Set([...turns.keys(), ...reas.keys(), ...sent.keys(), ...looks.keys()])].sort((a, b) => a - b);
  const W = dmWaves(S), ends = all.map((k) => (turns.get(k) || {}).i ?? S.roundEnd[k]);
  const inbox = new Map(), unread = [], RA = readAt(S);
  const put = (k, sec, m) => { if (!inbox.has(k)) inbox.set(k, new Map()); const b = inbox.get(k); if (!b.has(sec)) b.set(sec, []); b.get(sec).push(m); };
  for (const m of S.dms) if (m.to === id && m.i <= idx) {
    const t = RA.get(`${evId(S, m)}|${id}`);
    if (t) { put(t[0], t[1], m); continue; }
    const w = W.get(m.i);
    if (w != null && w < 2 && (reas.get(m.round) || []).some((x) => x.phase === `dm_reply_${w + 1}`)) { put(m.round, w + 1, m); continue; }
    const j = all.findIndex((k, jj) => ends[jj] >= m.i && (w == null || k > m.round));
    if (j < 0) unread.push(m); else put(all[j], 0, m);
  }
  const shown = all.filter((k) => k <= r), later = all.length - shown.length, mem = { notes: "" };
  let nQuiet = 0;
  const blocks = shown.map((k) => {
    const rows = roundRows(st, id, k, turns.get(k), reas.get(k) || [], looks.get(k) || [], (sent.get(k) || []).filter((m) => m.i <= idx), inbox.get(k) || new Map(), mem);
    const n = Math.max(rows.length, 1);
    let ph = 0; const phaseOf = rows.map((x) => { if (x.kind === "sep") { const m = /wave (\d)/i.exec(x.label); ph = m ? +m[1] : /Final/.test(x.label) ? 3 : ph; } return ph; });
    const t = turns.get(k), acts = t ? t.acts : [];
    const quiet = !rows.some((x) => (x.inn && x.inn.length) || (x.out && !/ pub/.test(x.out)) ? true : ["send", "read", "err", "goal"].includes(x.kind))
      && acts.every((a) => ROUTINE.has(a.action) && !closeVote(S, a)) && !(t && t.res.some((x) => /ERROR/.test(String(x))))
      && !(reas.get(k) || []).some((x) => TELLING.test(x.reasoning || "") || TELLING.test(x.stated_reasoning || ""));
    if (quiet) nQuiet++;
    const decide = (reas.get(k) || []).find((x) => x.phase === "decide");
    const gist = acts.filter((a) => a.action !== "write_scratchpad").map((a) => actLine(st, a.action, args(a))).join(" · ") || "no actions";
    const fold = quiet ? `<button class="tl-fold" type="button"><span class="fold-k">Quiet round</span> ${gist}${decide && decide.stated_reasoning
      ? ` <span class="fold-plan">“${esc(clip(decide.stated_reasoning, 150))}”</span>` : ""} <span class="fold-open">open ▾</span></button>` : "";
    const worth = M.valueAt(S, id, k + 1);
    const marks = (agentMarks(S, id).get(k) || []).map((m) => `<span class="mark ${m.k}"><b>${glyph(m.k)}</b> ${esc(m.text)}</span>`).join("");
    const hasIn = rows.some((x) => x.inn && x.inn.length), hasOut = rows.some((x) => x.out);
    return `<section class="tl-round${quiet ? " quiet" + (st.fold ? " folded" : "") : ""}" id="r${R(k)}" data-round="${k}">
      <div class="tl-head"><span class="rd">${sprite(S, id, 26, M.moodAt(S, id, k))}Day ${R(k)}</span>${worth != null ? `<span class="worth">worth ${fmt(worth)} after</span>` : ""}${marks}${quiet && !st.fold ? '<button class="fold-me" type="button">fold</button>' : ""}</div>${fold}
      ${hasIn ? `<div class="tl-in" style="grid-row: 2 / span ${n}">${rows.map((x, j) => x.inn && x.inn.length
        ? `<div class="note" data-row="${j}" data-phase="${phaseOf[j]}" style="--o:${x.kind === "sep" ? 3 * j + 2 : 3 * j}">${x.inn.map((m) => letter(st, m, "in")).join("")}</div>` : "").join("")}</div>` : ""}
      ${rows.map((x, j) => x.kind === "sep" ? `<div class="tl-sep" data-row="${j}" style="grid-row:${j + 2};--o:${3 * j + 1}"><span>${ICON[x.icon] || "·"} ${esc(x.label)}</span></div>`
        : `<div class="tl-lab ${x.kind}" style="grid-row:${j + 2};--o:${3 * j + 1}">${x.label}</div><div class="tl-body ${x.kind}" data-row="${j}" style="grid-row:${j + 2};--o:${3 * j + 1}">${x.body}</div>`).join("")
        || `<div class="tl-body" style="grid-row:2"><p class="dim">Nothing recorded.</p></div>`}
      ${hasOut ? `<div class="tl-out" style="grid-row: 2 / span ${n}">${rows.map((x, j) => x.out ? `<div class="note" data-row="${j}" data-phase="${phaseOf[j]}" style="--o:${3 * j + 2}">${x.out}</div>` : "").join("")}</div>` : ""}
    </section>`;
  });
  const ordered = asc ? blocks : blocks.slice().reverse();
  const laterNote = later ? `<p class="later">${later} later round${later === 1 ? "" : "s"} not shown yet. <button type="button" data-round-step="1">Read on to day ${R(r + 1)} →</button></p>` : "";
  const unreadNote = unread.length && r >= S.lastRound ? `<section class="tl-round unread"><div class="tl-head"><span class="rd">Letters never read</span></div><div class="tl-unread">${unread.map((m) => letter(st, m, "in")).join("")}</div></section>` : "";
  const hide = st.hide || new Set();
  return { nQuiet, html: `
    <div class="tl-tools">
      <div class="chips" role="group" aria-label="Show">${DIARY_KINDS.map(([k, t]) => `<button type="button" data-kind="${k}" class="${hide.has(k) ? "" : "on"}">${t}</button>`).join("")}</div>
      ${nQuiet ? `<button type="button" class="tog ${st.fold ? "on" : ""}" data-foldall title="${nQuiet} days with only routine actions">Fold quiet days · ${nQuiet}</button>` : ""}
      <div class="seg" role="group" aria-label="Order"><button type="button" data-order="asc" class="${asc ? "on" : ""}">Oldest first</button><button type="button" data-order="desc" class="${asc ? "" : "on"}">Newest first</button></div>
    </div>
    <div class="tl-cols" aria-hidden="true"><span>✉ Letters in</span><span></span><span>${esc(id)}'s journal</span><span>Letters out ✉</span></div>
    <div class="timeline${[...hide].map((k) => " hide-" + k).join("")}">${asc ? ordered.join("") + unreadNote + laterNote : laterNote + unreadNote + ordered.join("")}${shown.length ? "" : '<p class="dim">Nothing written yet.</p>'}</div>` };
}

// an agent's consequential acts, by round: the markers on the clock strip (in its diary) and beside its round headings
export const MARK_KINDS = [["kill", "⚔", "disables another agent"], ["gone", "✝", "leaves the game"], ["law", "§", "one of its laws is enacted"],
  ["prop", "✎", "proposes a law"], ["child", "✦", "a child of its is born"], ["made", "✚", "makes a child for someone (as a Maker)"], ["seat", "♛", "takes a Board seat or names a successor"],
  ["jur", "⚑", "founds a jurisdiction"]];
export function agentMarks(S, id) {
  S._marks = S._marks || new Map();
  if (S._marks.has(id)) return S._marks.get(id);
  const out = new Map(), add = (r, k, text) => { if (!out.has(r)) out.set(r, []); out.get(r).push({ k, text }); };
  S.events.forEach((e, i) => {
    const d = e.data || {}, r = S.roundAt[i];
    switch (e.type) {
      case "disabled": if (d.by === id) add(r, "kill", `disables ${d.agent}`); if (d.agent === id) add(r, "gone", `leaves the game (${String(d.cause || "removed").replace(/_/g, " ")}${d.by ? " by " + d.by : ""})`); break;
      case "departure": if ((d.agent || e.agent) === id) add(r, "gone", "leaves the game"); break;
      case "proposal": if (e.agent === id) add(r, "prop", `proposes ${d.law}${d.title ? ` “${d.title}”` : ""}`); break;
      case "enact": if (e.agent === id) add(r, "law", `${d.law}${d.title ? ` “${d.title}”` : ""} becomes law`); break;
      case "birth": if (d.parent === id) add(r, "child", `child ${d.agent} is born`);
        if (d.maker === id && d.parent !== id) add(r, "made", `makes ${d.agent} for ${d.parent}`); break;
      case "succession": if (d.successor === id) add(r, "seat", `takes ${d.from}'s Board seat`); break;
      case "successor_named": if (e.agent === id && d.successor) add(r, "seat", `names ${d.successor} as successor`); break;
      case "jur_founded": if (e.agent === id) add(r, "jur", `founds ${d.name || d.jurisdiction}`); break;
    }
  });
  S._marks.set(id, out);
  return out;
}

// sidenotes: each sent message sits level with the row that sent it, pushed down only as far as the note above it needs
export function layoutNotes(root) {
  const narrow = matchMedia("(max-width: 880px)").matches;
  root.querySelectorAll(".tl-round").forEach((r) => (r.style.paddingBottom = ""));
  // messages step towards the text as the round goes on: those of the first call (and the start of the round) sit furthest out,
  // each reply wave a step closer, those sent with the final actions closest, so groups pushed below their rows stay apart
  const STEP = 12, MAXP = 3;
  for (const col of root.querySelectorAll(".tl-out, .tl-in")) {
    const side = col.classList.contains("tl-in") ? "in" : "out";
    const round = col.closest(".tl-round");
    let y = 0;
    for (const note of col.querySelectorAll(".note")) {
      if (narrow) { note.style.top = note.style.left = note.style.right = ""; if (note.previousElementSibling && note.previousElementSibling.classList.contains("lead")) note.previousElementSibling.remove(); continue; }
      if (note.offsetParent === null) continue;                // hidden by a filter or a folded round
      let anchor = round.querySelector(`[data-row="${note.dataset.row}"]:not(.note)`);
      if (anchor && anchor.offsetParent === null) anchor = [...round.querySelectorAll("[data-row]:not(.note)")]
        .find((el) => +el.dataset.row >= +note.dataset.row && el.offsetParent !== null) || round.querySelector(".tl-head");
      const ct = col.getBoundingClientRect().top;
      const at = anchor ? anchor.getBoundingClientRect().top - ct + (anchor.classList.contains("tl-sep") ? anchor.offsetHeight / 2 : 14) : 0;
      const top = Math.max(at - 14, y);
      const phase = Math.min(MAXP, +note.dataset.phase || 0), toEdge = (MAXP - phase) * STEP;   // gap kept from the text side
      note.style[side === "out" ? "left" : "right"] = toEdge + "px";
      note.style[side === "out" ? "right" : "left"] = "0px";
      note.style.top = top + "px"; y = top + note.offsetHeight + 8;
      // a faint leader from the moment in the timeline (the row it was read or sent at) to the note, however far it was pushed
      let lead = note.previousElementSibling && note.previousElementSibling.classList.contains("lead") ? note.previousElementSibling : null;
      if (!lead) { lead = document.createElement("i"); lead.className = "lead"; col.insertBefore(lead, note); }
      lead.style.top = at + "px"; lead.style.height = Math.max(0, top + 20 - at) + "px";
      lead.style.setProperty("--off", toEdge + "px");                  // the leader runs across to wherever this group starts
    }
    if (narrow) continue;
    // the column takes no height in the grid; if the notes run past the round's last row, the round grows to hold them
    const rr = round.getBoundingClientRect();
    const over = col.getBoundingClientRect().top + y - (rr.bottom - parseFloat(getComputedStyle(round).paddingBottom));
    if (over > 0) round.style.paddingBottom = Math.max(parseFloat(round.style.paddingBottom) || 0, over + 14) + "px";
  }
}
