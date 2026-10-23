"""A run as a readable chronicle (one self-contained HTML page): the cast, then each day: what happened at dawn, everything said
(to whom, in which building), each agent's stated reasoning, what it did and what the night brought, the memories written that
night; every prompt, reply and talk-step exchange behind an expander. Works on a run in progress (it reads what is logged so far).

    python -m cybertron2.engine.chronicle <run dir> [--out file.html]
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

CSS = """
:root{--bg:#faf9f6;--fg:#1d1d1b;--mute:#6b6a65;--line:#e4e1d8;--card:#fff;--h0:#7a5c1e;--h1:#2f5d3a;--h2:#2d4f7a;--h3:#8a3b2e;--h4:#6b4a7a}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--fg:#ecebe6;--mute:#a3a29b;--line:#34332f;--card:#1f1f1c;--h0:#d8b46a;--h1:#8fc79b;--h2:#93b4e0;--h3:#e59a8a;--h4:#c5a3d6}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:16px;max-width:980px;margin-inline:auto}
h1{font-size:22px;margin:4px 0}h2{font-size:18px;margin:28px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px}
.mute{color:var(--mute)}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:4px 6px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:8px 0}
.who{font-weight:600}.h0{color:var(--h0)}.h1{color:var(--h1)}.h2{color:var(--h2)}.h3{color:var(--h3)}.h4{color:var(--h4)}
h3{font-size:16px;margin:16px 0 4px}
.talk li{margin:2px 0}.res{font-size:13.5px;margin:4px 0 0 0;padding-left:18px}.res li.ref{color:var(--mute)}
details{margin-top:6px}summary{cursor:pointer;color:var(--mute);font-size:13px}pre{white-space:pre-wrap;font-size:12.5px;background:var(--bg);padding:8px;border-radius:6px;overflow-x:auto}
.mem{border-left:3px solid var(--line);padding-left:10px;margin:6px 0}.tag{font-size:12px;color:var(--mute);margin-left:6px}
"""


def esc(x) -> str:
    return html.escape(str(x))


def build(run: Path) -> str:
    meta = json.load(open(run / "run.json"))
    spec = meta["spec"]
    turns = [json.loads(x) for x in open(run / "turns.jsonl")] if (run / "turns.jsonl").exists() else []
    days = [json.loads(x) for x in open(run / "days.jsonl")] if (run / "days.jsonl").exists() else []
    mems = [json.loads(x) for x in open(run / "memory.jsonl")] if (run / "memory.jsonl").exists() else []
    agents = spec["agents"]
    house = {n: a.get("household", "") for n, a in agents.items()}
    for t in turns:                                                     # households change (D4-36): the latest known
        if t.get("household"):
            house[t["agent"]] = t["household"]
    holds = sorted(set(house.values()))
    nodes = spec.get("nodes") or {"home": spec.get("node") or {}}
    vname = {k: v.get("name", k) for k, v in nodes.items()}
    home = {}                                                            # each household's village, from its house's parcel
    for h in list((spec.get("houses") or {}).values()) + list((spec.get("buildings") or {}).values()):
        if h.get("household"):
            home.setdefault(h["household"], next((k for k, v in nodes.items() if h["parcel"] in (v.get("parcels") or {})), None))

    def who(n):
        h = house.get(n, "")
        return f'<span class="who h{holds.index(h) % 5 if h in holds else 4}">{esc(n)}</span>'

    out = [f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
           f"<title>{esc(spec.get('name', 'run'))} chronicle</title><style>{CSS}</style></head><body>"]
    cost = days[-1]["cost_usd"] if days else 0
    out.append(f"<h1>{esc(spec.get('name', run.name))}</h1><div class='mute'>{len(days)} of {spec.get('days')} days logged · "
               f"${cost:.2f} so far · {esc(', '.join(vname.values()))}</div>")
    if len(nodes) > 1:
        roads = "; ".join(f"{vname.get(a, a)} to {vname.get(b, b)}: {d} day{'s' if d != 1 else ''}" for a, b, d in spec.get("roads") or spec.get("edges") or [])
        out.append(f"<div class='mute'>Roads: {esc(roads)}</div>")
    out.append("<h2>The people</h2><table><tr><th>Name</th><th>House</th><th>Village</th><th>Stage</th><th>Model</th><th>Knows, holds</th></tr>")
    for n, a in agents.items():
        knows = ", ".join(k for k in (a.get("knows") or {})) or ""
        holds = ", ".join(f"{k}" for k in (a.get("holdings") or {})) or ""
        out.append(f"<tr><td>{who(n)}{' (head)' if a.get('role') == 'head' else ''}</td><td>{esc(a.get('household'))}</td><td>{esc(vname.get(home.get(a.get('household')), ''))}</td>"
                   f"<td>{esc(a.get('stage'))}</td><td>{esc((a.get('model') or '-').replace('claude-', ''))}</td>"
                   f"<td class='mute'>{esc('; '.join(x for x in (knows, holds) if x))}</td></tr>")
    out.append("</table>")
    by_day = {}
    for t in turns:
        by_day.setdefault(t["day"], []).append(t)
    for d in sorted(by_day):
        ts = sorted(by_day[d], key=lambda t: (t.get("at") or "", house.get(t["agent"], ""), t["agent"]))
        rec = next((x for x in days if x["day"] == d), {})
        now = ts[0]["prompt"].split("## Now\n", 1)[-1].split("\n", 1)[0].split(".")[0] if ts else ""
        out.append(f"<h2>Day {d + 1} <span class='tag'>{esc(now)}</span></h2>")
        dawn = sorted({line for t in ts for line in t["prompt"].split("## This morning\n", 1)[-1].split("\n\n")[0].splitlines()
                       if "## This morning" in t["prompt"] and line.startswith("- ")})
        if dawn:
            out.append("<div class='card'><b>At dawn</b><ul>" + "".join(f"<li>{esc(x[2:])}</li>" for x in dawn) + "</ul></div>")
        groups = {}
        for t in ts:
            groups.setdefault(t.get("at"), []).append(t)
        for at, ts_all in groups.items():
            ts = ts_all
            if len(nodes) > 1:
                out.append(f"<h3>{esc(vname.get(at, at or 'on the road'))} <span class='tag'>{', '.join(t['agent'] for t in ts)}</span></h3>")
            speech = [(t["agent"], x) for t in ts for x in t["results"] if x.startswith(("You told ", "You said ("))]
            if speech:
                items = []
                for n, x in speech:
                    if x.startswith("You told "):
                        to, text = x[len("You told "):].split(":", 1)
                        items.append(f"<li>{who(n)} → {who(to.strip())}: {esc(text.strip())}</li>")
                    else:
                        scope, text = x[len("You said ("):].split("):", 1)
                        items.append(f"<li>{who(n)} <span class='tag'>{esc(scope)}</span>: {esc(text.strip())}</li>")
                woken = [t["agent"] for t in ts if t.get("talk")]
                out.append(f"<div class='card talk'><b>Talk before work</b> <span class='tag'>woken: {', '.join(woken) or 'nobody'}</span>"
                           f"<ul>{''.join(items)}</ul></div>")
            for t in ts:
                n = t["agent"]
                final = (t.get("talk") or [{}])[-1].get("reply") or t["reply"]
                why = final.get("why") or t["reply"].get("why") or ""
                acts = [x for x in t["results"] if not x.startswith(("You told ", "You said (", "You noted"))]
                notes = [x for x in t["results"] if x.startswith("You noted")]
                out.append(f"<div class='card'>{who(n)} <span class='tag'>{esc(t['model'].replace('claude-', ''))} · "
                           f"{t['used']}/{t['units']} units · attends {esc(t.get('attend') or '-')}</span>"
                           f"<div>{esc(why)}</div><ul class='res'>"
                           + "".join(f"<li class='{'ref' if x.startswith(('Refused', 'Not done', 'You left')) else ''}'>{esc(x)}</li>"
                                     for x in acts + notes + [f'Night: {y}' for y in t.get('night') or []]) + "</ul>")
                parts = [("Morning message" + (" (opening a new stretch)" if t.get("opening") else ""), t["prompt"]),
                         ("First reply", json.dumps(t["reply"], indent=1, ensure_ascii=False))]
                for k, x in enumerate(t.get("talk") or []):
                    parts.append((f"Talk step, wave {k + 1}: what reached them", x["prompt"]))
                    parts.append((f"Talk step, wave {k + 1}: reply", json.dumps(x["reply"], indent=1, ensure_ascii=False)))
                out.append("<details><summary>Prompts and replies</summary>"
                           + "".join(f"<p class='mute'>{esc(h)}</p><pre>{esc(b)}</pre>" for h, b in parts) + "</details></div>")
        ms = [m for m in mems if m["day"] == d and m.get("memory")]
        if ms:
            out.append("<div class='card'><b>Memories written tonight</b>" + "".join(
                f"<div class='mem'>{who(m['agent'])} <span class='tag'>{esc(m['span'])}</span><div>{esc(m['memory'])}</div></div>" for m in ms)
                + "</div>")
        if rec:
            bits = [f"missed meals: {', '.join(rec['missed'])}" if rec.get("missed") else "",
                    f"deaths: {', '.join(rec['deaths'])}" if rec.get("deaths") else "",
                    f"fights: {len(rec['fights'])}" if rec.get("fights") else ""]
            bits = [b for b in bits if b]
            out.append(f"<div class='mute'>Night: {esc('; '.join(bits) or 'everyone ate')}{' · cold' if rec.get('cold') else ''}</div>")
    out.append("</body></html>")
    return "".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cybertron2.engine.chronicle")
    ap.add_argument("run")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    run = Path(a.run)
    path = Path(a.out) if a.out else run / "chronicle.html"
    path.write_text(build(run))
    print(path)


if __name__ == "__main__":
    main()
