// Where the site reads run data: the public Hugging Face dataset, or the local copy (site/_data) with ?data=local.
// Also: a run's cast (agents, camps, observer) without downloading the whole viewer.json, for drawing its village.
import { villageCfg } from "./scene.js";

export const HF = "https://huggingface.co/datasets/zachmacsmith/charter-runs/resolve/main";
export const DATA = new URLSearchParams(location.search).get("data") === "local" ? new URL("../_data", import.meta.url).href : HF;
export const getJson = (url) => fetch(url).then((r) => { if (!r.ok) throw new Error(`${url}: ${r.status}`); return r.json(); });
export const catalog = () => getJson(`${DATA}/catalog.json`).then((c) => c.runs || []);
export const stories = () => getJson(`${DATA}/stories.json`).then((c) => c.stories || c || []);
export const viewerUrl = (row) => `${DATA}/${row.path}/viewer.json`;

// A run's data for the run page. Published runs have viewer-core.json.gz (everything but the agents' private reasoning, ~1/10
// the size) plus reasoning/<agent>.json.gz per agent, loaded when its diary opens; older uploads only have viewer.json.
async function gunzipJson(url) {
  const res = await fetch(url);
  if (!res.ok || !res.body) throw new Error(`${url}: ${res.status}`);
  return JSON.parse(await new Response(res.body.pipeThrough(new DecompressionStream("gzip"))).text());
}
export async function loadRun(row) {
  try { return await gunzipJson(`${DATA}/${row.path}/viewer-core.json.gz`); }
  catch (e) { return getJson(viewerUrl(row)); }
}
export const loadReasoning = (row, agent) => gunzipJson(`${DATA}/${row.path}/reasoning/${encodeURIComponent(agent)}.json.gz`);

// viewer.json files are 0.4 to 19 MB, but "instance" (agents, camps, observer) sits in the first ~130 KB: stream the file, cut the
// instance object out with a tiny brace scanner and cancel the download.
export async function fetchInstance(row) {
  const res = await fetch(viewerUrl(row));
  if (!res.ok || !res.body) throw new Error(`viewer.json ${res.status}`);
  const reader = res.body.getReader(), dec = new TextDecoder();
  let buf = "", start = -1, i = 0, depth = 0, inStr = false, escp = false;
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    if (start < 0) {
      const k = buf.indexOf('"instance"'); if (k < 0) continue;
      const b = buf.indexOf("{", k); if (b < 0) continue;
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
// at most n requests at once
export function pool(n) {
  let active = 0; const q = [];
  const next = () => { if (active >= n || !q.length) return; active++; const [fn, ok, bad] = q.shift(); fn().then(ok, bad).finally(() => { active--; next(); }); };
  return (fn) => new Promise((ok, bad) => { q.push([fn, ok, bad]); next(); });
}
// The instance block has no deaths, so a graveyard comes from the run's tags until the catalog carries a summary.
const DEATH_TAGS = ["lifespans", "violence", "assassination", "collapse", "dynasty", "succession"];
const parse = (v) => { if (v == null || typeof v !== "string") return v ?? null; try { return JSON.parse(v); } catch (e) { return null; } };
export function castCfg(row, inst) {
  const cfg = villageCfg(row, { instance: inst, events: [] });
  const tags = (parse(row.tags_json) || row.tags || []).map((t) => String(t).toLowerCase());
  if (tags.some((t) => DEATH_TAGS.includes(t))) cfg.roles.add("deaths");
  return cfg;
}
