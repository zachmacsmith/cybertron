// Data: what the run publishes on Hugging Face (typed tables and raw logs), with a DuckDB query to start from.
import { DATA, HF, getJson } from "../data.js";
import { esc } from "./common.js";

const HUB = "https://huggingface.co/datasets/zachmacsmith/charter-runs";

export function dataView(ctx, el) {
  const { S, row } = ctx;
  el.className = "wrap v-data";
  let done = false;
  return {
    el,
    async render() {
      if (done) return; done = true;
      el.innerHTML = `<p class="loading-run">Opening the archive…</p>`;
      let m = null; try { m = await getJson(`${DATA}/${row.path}/manifest.json`); } catch (e) {}
      const tables = Object.entries((m && m.tables) || {});
      el.innerHTML = `<section class="panel data-panel">
        <h2 class="h">The archive</h2>
        <p>Everything on these pages comes from this run's published data: typed tables${m ? ` (export schema ${esc(m.schema_version)})` : ""} and the raw logs,
          under CC BY 4.0.</p>
        <p class="links"><a class="btn" href="${HUB}/tree/main/${esc(row.path)}">Files on Hugging Face</a>${row.raw ? ` <a class="btn ghost" href="${HF}/${esc(row.raw)}">Raw archive (.tar.gz)</a>` : ""}</p>
        ${tables.length ? `<table class="tbl"><thead><tr><th>Table</th><th class="num">Rows</th></tr></thead><tbody>
          ${tables.map(([t, v]) => `<tr><td><a href="${DATA}/${esc(row.path)}/${esc(v.file)}">${esc(t)}</a></td><td class="num">${Number(v.rows).toLocaleString()}</td></tr>`).join("")}</tbody></table>` : `<p class="meta">No table list for this run.</p>`}
        <h3 class="h3">Query it</h3>
        <pre class="code">-- this run's events, straight from the Hub (DuckDB)
SELECT round, type, agent, data_json
FROM 'hf://datasets/zachmacsmith/charter-runs/${esc(row.path)}/events.parquet'
LIMIT 20;</pre>
        <p class="meta">${S.events.length.toLocaleString()} events · ${S.dms.length.toLocaleString()} private messages · ${S.laws.size} laws · ${S.agents.length} agents · run id <code>${esc(row.run_id)}</code></p>
      </section>`;
    },
  };
}
