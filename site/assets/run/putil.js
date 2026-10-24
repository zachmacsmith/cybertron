// Helpers for the People section: agent links, law links and villager sprites.
import { villagerSvg } from "../core/villagers.js";
import { CLASS_LABEL } from "../core/model.js";

import { esc } from "../core/text.js";
export { esc, fmt, clip } from "../core/text.js";
export const R = (r) => r + 1;                                   // rounds are 0-based in the data, 1-based on the page
export const modelShort = (m) => { const s = String(m || "").replace(/^claude-/, "").replace(/-\d{8}$/, "").replace(/-(\d+)-(\d+)$/, " $1.$2");
  return s ? s[0].toUpperCase() + s.slice(1) : ""; };

// what villagerSvg needs to know about an agent: its class, whether it is a Maker, whether it was born in the run
export function agentOf(S, id) {
  S._vill = S._vill || new Map();
  if (S._vill.has(id)) return S._vill.get(id);
  const a = S.A.get(id), life = S.truth.life || {};
  const v = a ? { id, cls: a.cls, maker: (a.rights || []).includes("maker"), child: !!(life.parent || {})[id] } : { id, cls: "agent" };
  S._vill.set(id, v);
  return v;
}
export const sprite = (S, id, size = 32, mood = "ok") => villagerSvg(agentOf(S, id), mood, size, "vg");
export function classLabel(S, id) {
  const v = agentOf(S, id), a = S.A.get(id);
  if (v.child) return "Child";
  if (v.maker && a.cls === "worker") return "Maker";
  return CLASS_LABEL[a ? a.cls : "agent"] || "Agent";
}
export const who = (st, id) => st.S.A.has(id) ? `<a class="who" href="${st.href("people", id)}">${esc(id)}</a>` : `<span class="who anon">${esc(id || "Anonymous")}</span>`;
export function lawRef(st, id, label) {
  if (!id) return "";
  const l = st.S.laws.get(id) || {};
  return `<a class="lawref" href="${st.href("laws", id)}" title="${esc(l.title || id)}">${esc(label || id)}</a>`;
}
// escape, then mark law ids and law titles in free text
export function txt(st, s) {
  const S = st.S;
  const h = esc(s);
  if (!S._lawRx) {
    const alts = [...S.titleLaw.keys()].sort((a, b) => b.length - a.length).map((t) => esc(t).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    S._lawRx = new RegExp(`\\b(L\\d{1,3})\\b${alts.length ? "|(" + alts.join("|") + ")" : ""}`, "g");
  }
  return h.replace(S._lawRx, (m, id, title) => {
    const lid = id || S.titleLaw.get(title.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"'));
    return lid && S.laws.has(lid) ? lawRef(st, lid, m) : m;
  });
}
export const para = (st, s) => String(s || "").split(/\n{2,}/).map((p) => `<p>${txt(st, p).replace(/\n/g, "<br>")}</p>`).join("");
export const md = (h) => h.replace(/\*\*([^*<]+?)\*\*/g, "<b>$1</b>").replace(/(^|<p>|<br>)#{1,4}\s*/g, "$1");
