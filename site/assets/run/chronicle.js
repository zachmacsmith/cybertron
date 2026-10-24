// The chronicle (one edition per day), the statute book (laws as code, with votes and history) and the letters (private
// threads between pairs of villagers), for the run page's "chronicle", "laws" and "correspondence" sections.
import { moodAt, snapAfter, regimeOf, lawsInForce, lawStatus, lawDoes, SECTION_OF, CLASS_LABEL, valueAt } from "../core/model.js";
import { esc, fmt, clip } from "../core/text.js";
import { villagerSvg } from "../core/villagers.js";
import { icon } from "./icons.js";

const R = (r) => r + 1;
const pct = (x) => (x == null ? "–" : Math.round(100 * x) + "%");

export function chronicleView(ctx, el) {
  const { S, st, href } = ctx;
  el.className = "wrap v-chronicle";
  const local = { filter: "", lawFilter: "all" };
  // who is a child (born in the run) and who is a Maker, for the villager sprites
  const born = new Map();
  for (const e of S.events) if (e.type === "birth") born.set(e.data.agent, e.data.parent);
  const sprite = (id) => { const a = S.A.get(id); return a ? { id, cls: a.cls, maker: (a.rights || []).includes("maker"), child: born.has(id) } : { id: id || "?", cls: "observer" }; };
  const vil = (id, r, size = 32) => villagerSvg(sprite(id), id && S.A.has(id) ? moodAt(S, id, r) : "ok", size, "vil");

  // ------------------------------------------------------------------ links (the shell owns the clock and the hash)
  const endIdx = (r = st.round) => S.roundEnd[r] ?? S.events.length - 1;
  function who(id, opts = {}) {
    if (!id || !S.A.has(id)) return `<span class="who anon">${esc(id || "Anonymous")}</span>`;
    const a = S.A.get(id);
    return `<a class="who" href="${href("people", id)}" title="${esc(id)}'s page">${esc(id)}</a>`
      + (opts.role ? ` <span class="role">${esc(CLASS_LABEL[a.cls] || a.cls)}</span>` : "");
  }
  const lawLink = (id, label) => id ? `<a class="lawref" href="${href("laws", id)}">${esc(label || id)}</a>` : "";
  // escape, bold the models' **markdown**, and link law ids
  function txt(s) {
    return esc(s).replace(/\*\*([^*<]+?)\*\*/g, "<b>$1</b>").replace(/\b(L\d{1,3})\b/g, (m) => S.laws.has(m) ? lawLink(m) : m);
  }
  const para = (s) => String(s || "").split(/\n{2,}/).map((p) => `<p>${txt(p).replace(/\n/g, "<br>")}</p>`).join("");
  function longText(s, n = 640) {
    s = String(s || "");
    if (s.length <= n) return para(s);
    const cut = s.slice(0, n).replace(/\s+\S*$/, "");
    return `<div class="clamp">${para(cut + " …")}</div><details class="more"><summary>Read the rest</summary>${para(s)}</details>`;
  }
  const stamp = (status) => `<span class="stamp st-${status.replace(/ /g, "-")}">${esc(status)}</span>`;
  const kicker = (ic, title, extra = "") => `<h3 class="kicker">${icon(ic, 24)}<span>${esc(title)}</span>${extra}</h3>`;

  // ------------------------------------------------------------------ the ballot as villagers
  function tally(b, idx, r) {
    const fin = b.close !== undefined && b.close <= idx;
    const vs = fin ? Object.entries(b.final || {}) : b.votes.filter((v) => v.i <= idx).map((v) => [v.who, v.choice]);
    const by = { yes: [], no: [] }; for (const [w, c] of vs) (by[c] = by[c] || []).push(w);
    const silent = (b.electorate || []).filter((w) => !vs.some((v) => v[0] === w));
    const side = (k, label, ws, cls) => `<div class="side ${cls}"><div class="side-sign">${esc(label)} <b>${ws.length}</b></div>
      <div class="side-crowd">${ws.map((w) => `<span class="voter" title="${esc(w)}">${vil(w, r, 30)}</span>`).join("") || '<span class="nobody">nobody</span>'}</div></div>`;
    const other = Object.keys(by).filter((k) => k !== "yes" && k !== "no");
    return `<div class="tally">${side("yes", "Aye", by.yes, "yes")}${side("no", "Nay", by.no, "no")}
      ${other.map((k) => side(k, k, by[k], "other")).join("")}${silent.length ? side("silent", "Silent", silent, "silent") : ""}</div>`;
  }

  // ------------------------------------------------------------------ public notices (system events)
  const SYS = { ballot_open: ["ballot", "Ballot opens"], vetoed: ["crown", "Vetoed"], veto_window: ["crown", "Veto window"], veto_vote: ["crown", "Veto vote"],
    patched: ["hammer", "Patched"], law_error: ["error", "Law error"], proposal_failed: ["error", "Proposal fails"], rights: ["scroll", "Rights"],
    sanction: ["stamp", "Sanction"], dm_limit: ["sealed", "Message limit"], ruling: ["stamp", "Ruling"], accuse: ["stamp", "Accusation"],
    bank_run: ["coin", "Bank run"], raid: ["torch", "Raid"], tribute_demand: ["coin", "Tribute demanded"], tribute_payment: ["coin", "Tribute paid"],
    tribute_met: ["coin", "Tribute met"], project_open: ["hammer", "Project"], project_failed: ["hammer", "Project fails"], disabled: ["dagger", "Removed"] };
  function sysText(it) {
    const d = it.data || {}, w = it.who ? who(it.who) + " " : "";
    switch (it.type) {
      case "ballot_open": return `Ballot <b>${esc(d.ballot)}</b> opens: ${txt(d.question)} <span class="meta">(${esc(String(d.rule || "").replace(/_/g, " "))}, ${(d.electorate || []).length} voters${d.closes_round != null ? `, closes day ${R(d.closes_round)}` : ""})</span>`;
      case "vetoed": return `The Board vetoes ${lawLink(d.law)}${d.by ? " (" + esc([].concat(d.by).join(", ")) + ")" : ""}`;
      case "veto_window": return `${lawLink(d.law)} enters the Board's veto window${d.until != null ? ` until day ${R(d.until)}` : ""}`;
      case "veto_vote": return `${w}${d.choice ? `votes <b>${esc(d.choice)}</b> on vetoing` : "casts a veto vote on"} ${lawLink(d.law)}`;
      case "patched": return `${w}patches ${lawLink(d.law)}: ${esc(clip(d.reason || "", 220))}`;
      case "law_error": return `${lawLink(d.law)} fails at run time: <code>${esc(clip(d.error, 140))}</code>`;
      case "proposal_failed": return `${w}proposal fails: ${esc(clip(d.reason || d.error || "", 260))}`;
      case "rights": return `${who(d.agent)} ${d.change === "grant" ? "gains" : "loses"} the right <b>${esc(d.right)}</b>${d.law ? " under " + lawLink(d.law) : ""}`;
      case "dm_limit": return `${w}sets the private-message limit to <b>${esc(d.n)}</b>${d.agent ? " for " + who(d.agent) : " for everyone"}`;
      case "bank_run": return `A run on the <b>${esc(d.currency)}</b>`;
      case "raid": return `Raid on <b>${esc(d.camp)}</b>: ${fmt(d.stock_lost)} stock lost${d.seized && Object.keys(d.seized).length ? ", goods seized from " + esc(Object.keys(d.seized).join(", ")) : ""}`;
      case "tribute_demand": return `The outside power demands tribute worth <b>${fmt((d.demand || {}).value)}</b> by day ${R(d.deadline ?? 0)}`;
      case "tribute_payment": return `${w}pays ${fmt(d.qty)} ${esc(d.item)} toward the tribute`;
      case "project_open": return `<b>${esc(d.project)}</b>: ${esc(clip(d.description || d.kind, 260))}`;
      case "disabled": return `${who(d.agent)} is removed from the game${d.cause ? ` (${esc(String(d.cause).replace(/_/g, " "))})` : ""}`;
      default: {
        const short = Object.entries(d).filter(([k, v]) => typeof v !== "object" && k !== "code").map(([k, v]) => `${k} ${v}`).join(" · ");
        return `${w}<b>${esc(it.type.replace(/_/g, " "))}</b> ${txt(clip(short, 260))}`;
      }
    }
  }
  const notice = (it) => { const [ic, lab] = SYS[it.type] || ["lantern", it.type.replace(/_/g, " ")];
    return `<div class="notice">${icon(ic, 24)}<div><span class="label">${esc(lab)}</span> ${sysText(it)}</div></div>`; };

  // ------------------------------------------------------------------ headlines
  function headlines(r) {
    const h = S.heads[r] || { items: [] }, out = [], worldNews = [];
    for (const x of h.items) {
      const e = S.events[x.i] || {}, d = e.data || {};
      switch (x.k) {
        case "enacted": out.push(["scroll", `${lawLink(x.law)} <b>${esc(x.title || "")}</b> becomes law`]); break;
        case "repealed": out.push(["stamp", `${lawLink(x.law)} is repealed`]); break;
        case "vetoed": out.push(["crown", `The Board vetoes ${lawLink(x.law)}`]); break;
        case "raid": out.push(["torch", `Raiders strike ${esc(x.camp)}`]); break;
        case "left": out.push(d.by ? ["dagger", `${who(x.who)} is struck down by ${who(d.by)}`] : x.cause === "old_age" ? ["grave", `${who(x.who)} reaches the end of a long life`]
          : ["dagger", `${who(x.who)} ${["departure", "left"].includes(x.cause) ? "leaves the village" : "is removed from the game"}`]); break;
        case "arrived": out.push(born.has(x.who) ? ["cradle", `${who(x.who)} is born to ${who(born.get(x.who))}`] : ["star", `${who(x.who)} arrives in the village`]); break;
        case "bank_run": out.push(["coin", `A run on the ${esc(x.cur)}`]); break;
        case "tribute": out.push(["coin", "The outside power demands tribute"]); break;
        case "world": if (e.vis === "public" && !/has arrived|newcomer/i.test(x.text)) worldNews.push(["lantern", esc(clip(String(x.text).replace(/^World news:\s*/, ""), 100))]); break;
      }
    }
    out.push(...worldNews);
    const minor = [];
    for (let i = S.roundStart[r] ?? 0; i <= (S.roundEnd[r] ?? -1); i++) {
      const e = S.events[i], d = e.data || {};
      if (e.type === "birth" && !h.items.some((x) => x.k === "arrived" && x.who === d.agent)) out.push(["cradle", `${who(d.agent)} is born to ${who(d.parent)}`]);
      // smaller news, shown when the round has little else: bills tabled and ballots lost
      if (e.type === "proposal") minor.push(["scroll", `${who(e.agent)} tables ${lawLink(d.law)} <b>${esc(d.title || "")}</b>`]);
      if (e.type === "ballot_close" && d.result !== "yes") { const b = S.ballots.get(d.ballot), v = Object.values(d.votes || {});
        minor.push(["ballot", `${b && b.law ? lawLink(b.law) + " is voted down" : `“${esc(clip(b ? b.q : d.ballot, 70))}” fails`} <span class="score">${v.filter((x) => x === "yes").length}–${v.filter((x) => x === "no").length}</span>`]); }
    }
    return out.concat(minor.slice(0, Math.max(0, 4 - out.length)));
  }
  const hlIcon = (ic, r) => ic === "grave" ? villagerSvg({ id: "x" }, "gone", 36, "ico") : icon(ic, 36);

  // ================================================================== chronicle
  function groupItems() { const out = []; for (const it of S.items) (out[it.round] = out[it.round] || []).push(it); return out; }
  function chronicle() {
    const r = st.round, idx = endIdx(r), h = S.heads[r] || { posts: 0, dms: 0, votes: 0, harvests: 0 };
    const its = (S._byRound ||= groupItems())[r] || [];
    const sec = (k) => its.filter((it) => SECTION_OF(it) === k);
    const legis = sec("legislature"), press = sec("press"), letters = sec("letters"), gaz = sec("gazette"), evs = sec("events");
    const turns = its.filter((it) => it.kind === "turn");
    const dmsR = S.dms.filter((m) => m.round === r);
    const pairs = new Map(); for (const m of dmsR) { const k = [m.from, m.to].sort().join("|"); pairs.set(k, (pairs.get(k) || 0) + 1); }
    const snap = snapAfter(S, r), prev = r > 0 ? snapAfter(S, r - 1) : null, hl = headlines(r);
    const papers = press.filter((p) => !/^Official/i.test(p.label || "")), records = press.filter((p) => /^Official/i.test(p.label || ""));
    return `<section class="edition">
      <div class="board">
        <div class="board-top"><span class="board-title">The Notice Board</span><span class="board-date">Day ${R(r)} of ${S.rounds}${snap ? " · " + esc(regimeOf(snap)) : ""}</span></div>
        <div class="board-paper">
          ${hl.length ? hl.map(([ic, t], k) => `<div class="hl${k === 0 ? " lead" : ""}">${hlIcon(ic, r)}<h2>${t}</h2></div>`).join("") : `<div class="hl quiet">${icon("lantern", 36)}<h2>A quiet day in the village</h2></div>`}
          <div class="counts">
            <span title="public letters">${icon("letter", 20)}<b>${h.posts}</b> letters</span>
            <span title="private messages">${icon("sealed", 20)}<b>${h.dms}</b> private</span>
            <span title="votes cast">${icon("ballot", 20)}<b>${h.votes}</b> votes</span>
            <span title="harvests">${icon("wheat", 20)}<b>${h.harvests}</b> harvests</span>
          </div>
        </div>
      </div>
      <div class="ed-grid">
        <div class="ed-main">
          ${legis.length ? `<div class="card">${kicker("scroll", "The legislature")}${legis.map((it) => legisItem(it, idx, r)).join("")}</div>` : ""}
          ${papers.length ? `<div class="card">${kicker("paper", "The press")}${papers.map((it) => `<article class="story">
              <div class="mast"><span class="mast-name">${esc(it.label)}</span><span class="meta">edited by ${who(it.who)}</span></div>
              ${it.head ? `<h4>${txt(it.head)}</h4>` : ""}<div class="body">${longText(it.text)}</div></article>`).join("")}
              ${records.length ? `<details class="records"><summary>${records.length} official record${records.length === 1 ? "" : "s"}</summary>${records.map((it) => `<div class="record"><b>${esc(it.label)}</b>${para(it.text)}</div>`).join("")}</details>` : ""}</div>`
            : records.length ? `<div class="card">${kicker("paper", "Official records")}${records.map((it) => `<div class="record"><b>${esc(it.label)}</b>${para(it.text)}</div>`).join("")}</div>` : ""}
          ${letters.length ? `<div class="card">${kicker("letter", "Letters to the square")}${letters.map((it) => `<div class="post">
              <div class="post-who">${it.anon ? villagerSvg({ id: "anon", cls: "observer" }, "ok", 40, "vil") : vil(it.who, r, 40)}</div>
              <div class="post-body"><div class="post-head">${it.anon ? `<span class="who anon">Anonymous</span>${it.who ? ` <span class="meta">(really ${who(it.who)})</span>` : ""}` : who(it.who, { role: true })}${it.channel ? ` <span class="chan">#${esc(it.channel)}</span>` : ""}</div>
              <div class="post-text">${longText(it.text, 520)}</div></div></div>`).join("")}</div>` : ""}
          ${evs.length ? `<div class="card">${kicker("lantern", "Happenings")}${evs.map((it) => it.kind === "world" ? worldItem(it) : notice(it)).join("")}</div>` : ""}
          ${pairs.size ? `<div class="card dusk">${kicker("sealed", "Behind closed doors")}
              <p class="meta">${dmsR.length} private message${dmsR.length === 1 ? "" : "s"} between ${pairs.size} pair${pairs.size === 1 ? "" : "s"} this round.</p>
              <ul class="pairs">${[...pairs.entries()].sort((a, b) => b[1] - a[1]).map(([k, n]) => { const [a, b] = k.split("|");
                return `<li><a href="${href("correspondence", k)}"><span class="duo">${vil(a, r, 28)}${vil(b, r, 28)}</span><span class="pn">${esc(a)} &amp; ${esc(b)}</span><span class="n">${n}</span></a></li>`; }).join("")}</ul></div>` : ""}
          ${turns.length ? `<details class="card ledger"><summary class="kicker">${icon("hammer", 24)}<span>The day's work: every action (${turns.length} turns)</span></summary>${turns.map((it) => `<div class="turnrow">${vil(it.who, r, 24)}<div>${who(it.who)} ${actsList(it.acts, it.res)}</div></div>`).join("")}</details>` : ""}
        </div>
        <aside class="ed-side">
          ${gaz.length ? `<div class="card gazette">${kicker("bell", "Town crier")}${gaz.map((g) => `<p>${txt(g.text)}</p>`).join("")}</div>` : ""}
          ${stateOfThings(snap, prev, idx, r)}
        </aside>
      </div></section>`;
  }
  function legisItem(it, idx, r) {
    if (it.kind === "proposal") { const does = lawDoes(it.code);
      return `<div class="bill"><div class="label">Bill ${lawLink(it.law)} · ${esc(it.cls || "")} · proposed by ${who(it.who)}</div>
        <h4><a href="${href("laws", it.law)}">${esc(it.title || it.law)}</a></h4><p class="intent">${txt(it.intent)}</p>
        ${does.length ? `<div class="does">${does.map((x) => `<span class="chip">${esc(x)}</span>`).join("")}</div>` : ""}
        ${it.code ? `<details class="codebox"><summary>Read the code</summary>${codeBlock(it.code)}</details>` : ""}</div>`; }
    if (it.kind === "ballot") { const b = S.ballots.get(it.ballot); if (!b) return "";
      return `<div class="ballot-res">${icon("ballot", 28)}<div class="br-body"><div class="label">Ballot ${esc(b.id)} closes ${stamp(b.result === "yes" ? "passed" : "rejected")}</div><p>${txt(b.q)}</p>${tally(b, it.i, r)}</div></div>`; }
    if (it.kind === "law") { const l = S.laws.get(it.law) || {};
      return `<div class="enacted">${icon(it.act === "enacted" ? "scroll" : "stamp", 28)}<div>${stamp(it.act === "enacted" ? "in force" : "repealed")} ${lawLink(it.law)} <b>${esc(it.title || l.title || "")}</b>${l.intent && it.act === "enacted" ? `<p class="meta">${txt(clip(l.intent, 240))}</p>` : ""}</div></div>`; }
    return notice(it);
  }
  function worldItem(it) {
    const t = it.truth, rum = t && t.rumor, arrive = /has arrived|newcomer/i.test(it.text);
    return `<div class="notice world">${icon(arrive ? "star" : "lantern", 24)}<div><span class="label">World news${it.vis !== "public" ? ` · told to ${Array.isArray(it.vis) ? it.vis.length + " agents" : "some"}` : ""}${rum ? ` · rumour, <span class="${t.true ? "yes" : "no"}">${t.true ? "true" : "false"}</span>` : ""}</span>
      ${txt(String(it.text).replace(/^World news:\s*/, ""))}${t && t.truth && rum ? `<div class="meta">In truth: ${esc(t.truth)}</div>` : ""}</div></div>`;
  }
  const ACT_VERB = { harvest: "harvests", vote: "votes", post: "posts", anon_post: "posts anonymously", propose: "proposes", repeal: "moves to repeal",
    pay_tribute: "pays tribute", publish: "publishes", transfer: "sends", dm: "messages", contribute: "contributes", pass: "waits", veto: "vetoes",
    read_archive: "reads", search_archive: "searches the archive", write_archive: "writes to the archive", run_python: "runs code", patch: "patches" };
  function actsList(acts, res) {
    return `<ul class="acts">${acts.map((a, j) => { let x = {}; try { x = a.args && typeof a.args === "object" ? a.args : JSON.parse(a.args_json || "{}"); } catch (e) {}
      const what = { harvest: `at ${esc(x.camp)}`, vote: `<b>${esc(x.choice ?? "")}</b> on ${esc(x.ballot ?? "")}`, transfer: `${esc(x.qty)} ${esc(x.item)} to ${esc(x.to)}`,
        post: `“${txt(clip(x.text, 120))}”`, anon_post: `“${txt(clip(x.text, 120))}”`, propose: x.title ? `“${esc(x.title)}”` : "", repeal: lawLink(x.law), dm: x.to ? esc(x.to) : "" }[a.action];
      const rr = res[j] ? ` <span class="res">${txt(clip(String(res[j]).replace(/^[\w ]+:\s*/, ""), 160))}</span>` : "";
      return `<li><b>${esc(ACT_VERB[a.action] || String(a.action || "").replace(/_/g, " "))}</b> ${what ?? esc(clip(Object.entries(x).filter(([, v]) => typeof v !== "object").map(([k, v]) => `${k} ${v}`).join(" · "), 90))}${rr}</li>`; }).join("")}</ul>`;
  }
  function lawsInForceList(idx) {
    return [...lawsInForce(S, idx).values()].map((l) => { const info = S.laws.get(l.law) || {};
      return `<li>${icon("scroll", 16)}<span>${lawLink(l.law)} ${esc(l.title || info.title || "")}</span></li>`; }).join("");
  }
  function stateOfThings(snap, prev, idx, r) {
    if (!snap) return `<div class="card">${kicker("coin", "The state of things")}<p class="meta">No snapshot for this round.</p></div>`;
    const rows = Object.entries(snap.values || {}).filter(([id]) => S.A.has(id) && S.A.get(id).cls !== "observer").sort((a, b) => b[1] - a[1]);
    const decisive = new Set(snap.decisive_set || []), pv = (prev && prev.values) || S.truth.start_values || {};
    const campRes = S.truth.camp_resource || Object.fromEntries((S.inst.camps || []).map((c) => [c.id, c.resource]));
    const trib = snap.tribute && snap.tribute.current, top = rows.length ? rows[0][1] || 1 : 1;
    return `<div class="card sot">${kicker("coin", "The state of things")}
      <p class="meta">After day ${R(r)}: <b>${esc(regimeOf(snap))}</b>, ${(snap.decisive_set || []).length} in the decisive set, ${pct(snap.franchise_share)} can vote.</p>
      <h5>Purses</h5>
      <ol class="purses">${rows.map(([id, v]) => { const d = pv[id] != null ? v - pv[id] : null;
        return `<li>${vil(id, r, 24)}<span class="pname">${who(id)}${decisive.has(id) ? ` <span title="in the decisive set">${icon("crown", 14)}</span>` : ""}</span>
          <span class="pbar"><i style="width:${Math.max(2, Math.round(100 * v / top))}%"></i></span><span class="num">${fmt(v)}</span>
          <span class="num delta ${d > 0.005 ? "yes" : d < -0.005 ? "no" : "meta"}">${d == null || Math.abs(d) < 0.005 ? "" : (d > 0 ? "+" : "") + fmt(d)}</span></li>`; }).join("")}</ol>
      <h5>Laws in force</h5><ul class="inforce">${lawsInForceList(idx) || '<li class="meta">None yet.</li>'}</ul>
      ${snap.stocks ? `<h5>Camp stocks</h5><div class="stocks">${Object.entries(snap.stocks).map(([c, f]) => `<div class="stock"><span>${esc(c)} <span class="meta">${esc(campRes[c] || "")}</span></span><span class="cells">${Array.from({ length: 10 }, (_, k) => `<i class="${k < Math.round(10 * f) ? "on" : ""}"></i>`).join("")}</span><span class="num">${pct(f)}</span></div>`).join("")}</div>` : ""}
      ${Object.keys(snap.prices || {}).length ? `<h5>Money</h5>${Object.entries(snap.prices).map(([c, p]) => `<p class="meta">${esc(c)}: price ${p.toFixed(3)}, supply ${fmt((snap.supplies || {})[c] || 0)}</p>`).join("")}` : ""}
      ${trib && (trib.demands || trib.raids) ? `<h5>The outside power</h5><p class="meta">${trib.demands || 0} demands, ${trib.paid_in_full || 0} paid in full, ${trib.raids || 0} raids${trib.open ? ", one open now" : ""}</p>` : ""}
    </div>`;
  }

  // ================================================================== statute book
  function codeBlock(code) {
    const lines = String(code || "").replace(/\n$/, "").split("\n");
    return `<pre class="code"><code>${lines.map((l, k) => `<span class="line"><span class="ln">${k + 1}</span><span class="lc">${hiPy(l) || " "}</span></span>`).join("")}</code></pre>`;
  }
  // a light Python highlighter: comments, strings, keywords, numbers, def names
  function hiPy(line) {
    let out = "", m;
    const re = /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|\b(def|return|if|elif|else|for|in|not|and|or|while|import|from|pass|None|True|False|lambda|try|except|break|continue|is|with|as|global)\b|\b(\d+(?:\.\d+)?)\b|([^#"'\w]+|\w+)/g;
    while ((m = re.exec(line))) {
      if (m[1]) out += `<span class="c">${esc(m[1])}</span>`;
      else if (m[2]) out += `<span class="s">${esc(m[2])}</span>`;
      else if (m[3]) out += `<span class="k">${m[3]}</span>`;
      else if (m[4]) out += `<span class="n">${m[4]}</span>`;
      else out += esc(m[5]);
      if (!m[0]) re.lastIndex++;
    }
    return out.replace(/(<span class="k">def<\/span>\s+)(\w+)/, '$1<span class="f">$2</span>');
  }
  function statusOf(id, idx) {
    let s = lawStatus(S, id, idx); const l = S.laws.get(id) || {};
    if (s === "proposed" && l.status === "failed" && l.proposed != null && l.proposed < st.round) s = "failed";
    return s;
  }
  const authorOf = (l) => l.author && S.A.has(l.author) ? who(l.author) : esc(l.author === "constitution" ? "the founding charter" : l.author || "unknown");
  function laws() {
    const idx = endIdx();
    if (st.target && S.laws.has(st.target)) return statute(st.target, idx);
    const rows = [...S.laws.values()].filter((l) => (S.lawTL.get(l.id) || []).some((x) => x.i <= idx))
      .sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
    const later = S.laws.size - rows.length;
    const withS = rows.map((l) => ({ l, s: statusOf(l.id, idx) }));
    const groups = [["all", "All"], ["in force", "In force"], ["pending", "Pending"], ["fell", "Failed or rejected"], ["gone", "Repealed or vetoed"]];
    const grp = (s) => s === "in force" ? "in force" : s === "proposed" || s === "on the ballot" ? "pending" : s === "repealed" || s === "vetoed" ? "gone" : "fell";
    const shown = withS.filter((x) => local.lawFilter === "all" || grp(x.s) === local.lawFilter);
    return `<section class="statutes">
      <div class="hall-sign">${icon("scroll", 40)}<div><h2>The Statute Book</h2><p>Every law proposed up to day ${R(st.round)}: ${rows.length} so far${later > 0 ? `, ${later} more to come` : ""}. Laws are short Python programs; the town hall runs the ones in force each round.</p></div></div>
      <div class="filters" role="group" aria-label="Filter laws">${groups.map(([k, t]) => { const n = k === "all" ? withS.length : withS.filter((x) => grp(x.s) === k).length;
        return `<button data-lf="${k}" class="${local.lawFilter === k ? "on" : ""}" ${n ? "" : "disabled"}>${esc(t)} <b>${n}</b></button>`; }).join("")}</div>
      <div class="scrolls">${shown.map(({ l, s }) => `<a class="scroll-card" href="${href("laws", l.id)}">
          <span class="sc-top"><span class="sc-id">${esc(l.id)}</span>${stamp(s)}</span>
          <span class="sc-title">${esc(l.title || l.id)}</span>
          <span class="sc-intent">${esc(clip(l.intent || "", 150))}</span>
          <span class="sc-foot">${l.author && S.A.has(l.author) ? vil(l.author, st.round, 24) : icon("bell", 20)}<span>${l.author === "constitution" ? "founding" : esc(l.author || "")}${l.cls ? ` · ${esc(l.cls)}` : ""}</span>
            <span class="meta">${l.proposed != null ? "round " + R(l.proposed) : "founding"}</span></span></a>`).join("") || '<p class="meta">No laws here yet.</p>'}</div></section>`;
  }
  function statute(id, idx) {
    const l = S.laws.get(id), does = lawDoes(l.code), status = statusOf(id, idx);
    const ids = [...S.laws.keys()].sort((a, b) => a.localeCompare(b, undefined, { numeric: true })), k = ids.indexOf(id);
    const TL = { proposed: "scroll", ballot: "ballot", enacted: "stamp", veto_window: "crown", vetoed: "crown", repealed: "stamp", patched: "hammer", error: "error" };
    const tl = (S.lawTL.get(id) || []).map((x) => { const rr = S.roundAt[x.i], fut = x.i > idx ? " later" : "";
      const when = `<a class="when" href="${href("chronicle", null, rr)}">Day ${R(rr)}</a>`;
      let body = "";
      switch (x.kind) {
        case "proposed": body = `Proposed by ${who(x.who)}`; break;
        case "ballot": { const b = x.b; body = `Ballot ${esc(b.id)} <span class="meta">(${esc(String(b.rule || "").replace(/_/g, " "))})</span>${b.close !== undefined && b.close <= idx ? " " + stamp(b.result === "yes" ? "passed" : "rejected") : ""}${x.i <= idx ? tally(b, Math.min(idx, b.close ?? idx), rr) : ""}`; break; }
        case "enacted": body = `<b>Enacted</b>${x.who === "constitution" ? " (a founding law)" : ""}`; break;
        case "veto_window": body = `The Board may veto it until day ${R(x.until ?? 0)}`; break;
        case "vetoed": body = `<b>Vetoed</b>${x.by ? " by " + esc([].concat(x.by).join(", ")) : ""}`; break;
        case "repealed": body = "<b>Repealed</b>"; break;
        case "patched": body = `Patched by ${who(x.who)}: ${esc(clip(x.reason, 260))}${x.diff ? `<details class="codebox"><summary>The change</summary><pre class="code diff"><code>${esc(x.diff)}</code></pre></details>` : ""}`; break;
        case "error": body = `Failed at run time: <code>${esc(clip(x.error, 140))}</code>`; break;
      }
      return `<li class="${fut}">${icon(TL[x.kind] || "lantern", 24)}<div>${when}${fut ? ' <span class="meta">(later)</span>' : ""}<div>${body}</div></div></li>`; }).join("");
    return `<section class="statute">
      <nav class="law-nav"><a href="${href("laws")}">◂ Statute book</a><span>${k > 0 ? `<a href="${href("laws", ids[k - 1])}">${esc(ids[k - 1])}</a>` : ""}${k < ids.length - 1 ? `<a href="${href("laws", ids[k + 1])}">${esc(ids[k + 1])} ▸</a>` : ""}</span></nav>
      <article class="decree">
        <div class="roll"></div>
        <div class="decree-body">
          <div class="label">Law ${esc(id)}${l.cls ? " · " + esc(l.cls) + " law" : ""}${l.jurisdiction ? " · " + esc(l.jurisdiction) : ""}</div>
          <h2>${esc(l.title || id)}</h2>
          <div class="decree-status">${stamp(status)}<span>as of day ${R(st.round)}</span><span class="by">${l.author && S.A.has(l.author) ? vil(l.author, st.round, 28) : ""}by ${authorOf(l)}</span></div>
          ${l.intent ? `<p class="intent big">${txt(l.intent)}</p>` : ""}
          ${does.length ? `<div class="does">${does.map((x) => `<span class="chip">${esc(x)}</span>`).join("")}</div>` : ""}
          ${l.code ? `<h3 class="kicker plain">The code</h3>${codeBlock(l.code)}` : '<p class="meta">No code recorded.</p>'}
        </div>
        <div class="roll"></div>
      </article>
      <div class="card">${kicker("bell", "Its history")}<ol class="history">${tl || '<li class="meta">No recorded history.</li>'}</ol></div>
    </section>`;
  }

  // ================================================================== letters
  const lastBefore = (c, idx) => { let x = -1; for (const m of c.msgs) if (m.i <= idx) x = m.i; return x; };
  function correspondence() {
    const idx = endIdx(), key = st.target;
    const convs = [...S.convs.values()].map((c) => ({ c, n: c.msgs.filter((m) => m.i <= idx).length, last: lastBefore(c, idx) }))
      .filter((x) => x.n > 0).sort((x, y) => y.last - x.last);
    const f = local.filter.toLowerCase(), shown = f ? convs.filter((x) => (x.c.a + " " + x.c.b).toLowerCase().includes(f)) : convs;
    const open = key && S.convs.get(key) ? S.convs.get(key) : null, show = open || (shown[0] || {}).c;
    const total = S.dms.filter((m) => m.i <= idx).length;
    return `<section class="letters${open ? " has-open" : ""}">
      <div class="hall-sign">${icon("sealed", 40)}<div><h2>Letters</h2><p>${total} private notes in ${convs.length} exchanges up to day ${R(st.round)}. Only the two villagers saw these; forgeries and sealed notes are marked.</p></div></div>
      <div class="convo">
        <div class="clist"><label class="filter">${icon("letter", 16)}<input id="convfilter" placeholder="Find a villager" value="${esc(local.filter)}" aria-label="Filter conversations by name"></label>
          <div class="citems">${shown.map(({ c, n }) => `<a class="citem${show && c.key === show.key ? " on" : ""}" href="${href("correspondence", c.key)}">
            <span class="duo">${vil(c.a, st.round, 30)}${vil(c.b, st.round, 30)}</span>
            <span class="cn"><span><b>${esc(c.a)}</b> &amp; <b>${esc(c.b)}</b></span><span class="meta">${n} note${n === 1 ? "" : "s"}</span></span></a>`).join("") || '<p class="meta pad">No exchanges yet.</p>'}</div></div>
        <div class="thread">${show ? thread(show, idx) : '<p class="meta pad">Pick an exchange.</p>'}</div>
      </div></section>`;
  }
  function thread(c, idx) {
    const msgs = c.msgs.filter((m) => m.i <= idx), later = c.msgs.length - msgs.length;
    const nA = msgs.filter((m) => m.from === c.a).length;
    let out = `<a class="back" href="${href("correspondence")}">◂ All exchanges</a>
      <div class="th-head">
        <div class="th-side">${vil(c.a, st.round, 72)}<div>${who(c.a, { role: true })}<div class="meta">${nA} sent</div></div></div>
        <div class="th-mid">${icon("letter", 28)}</div>
        <div class="th-side r"><div>${who(c.b, { role: true })}<div class="meta">${msgs.length - nA} sent</div></div>${vil(c.b, st.round, 72)}</div>
      </div><div class="notes">`;
    let rr = -1;
    for (const m of msgs) {
      if (m.round !== rr) { out += `<div class="rnd"><a href="${href("chronicle", null, m.round)}">Day ${R(m.round)}</a></div>`; rr = m.round; }
      const tags = [];
      if (m.enc) tags.push(["sealed", "sealed (encrypted)"]);
      if (m.shownAs) tags.push(["error", `forged: shown as from ${m.shownAs}`]);
      if (m.shownTo) tags.push(["letter", `meant for ${m.shownTo}`]);
      if (m.pay) tags.push(["coin", `with ${m.pay.qty} ${m.pay.item}`]);
      const side = m.from === c.a ? "l" : "r";
      out += `<div class="note ${side}"><div class="nv">${vil(m.from, m.round, 36)}</div>
        <div class="nb"><div class="nh"><b>${esc(m.from)}</b> to ${esc(m.to)}</div>${longText(m.text || (m.enc ? "(sealed)" : ""), 900)}
        ${tags.length ? `<div class="ntags">${tags.map(([ic, t]) => `<span>${icon(ic, 14)}${esc(t)}</span>`).join("")}</div>` : ""}</div></div>`;
    }
    out += "</div>";
    if (later) out += `<p class="later">${icon("lantern", 20)} ${later} more note${later === 1 ? "" : "s"} after day ${R(st.round)}. <a href="${href("correspondence", c.key, S.lastRound)}">Read to the end</a></p>`;
    return out;
  }


  el.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-lf]"); if (b) { local.lawFilter = b.dataset.lf; render(); }
  });
  el.addEventListener("input", (e) => {
    if (e.target.id !== "convfilter") return;
    local.filter = e.target.value; const pos = e.target.selectionStart; render();
    const i = el.querySelector("#convfilter"); i.focus(); i.setSelectionRange(pos, pos);
  });
  function render() {
    el.innerHTML = st.section === "laws" ? laws() : st.section === "correspondence" ? correspondence() : chronicle();
  }
  return { el, render };
}
