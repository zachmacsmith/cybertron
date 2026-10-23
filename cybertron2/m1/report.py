"""A summary of an M1 run from its logs: per agent, what it attended to, its notes, look-ups, what it learned and how, refusals,
teaching, talk and offers; per day, food and deaths; prompt sizes and cost by model.

    python -m cybertron2.m1.report <run dir>
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path


def load(run):
    run = Path(run)
    turns = [json.loads(x) for x in open(run / "turns.jsonl")]
    days = [json.loads(x) for x in open(run / "days.jsonl")]
    state = json.load(open(run / "state.json")) if (run / "state.json").exists() else None
    meta = json.load(open(run / "run.json"))
    return turns, days, state, meta


def summary(run) -> str:
    turns, days, state, meta = load(run)
    spec = meta["spec"]
    L = [f"# {spec['name']}: {len(days)} days, {len({t['agent'] for t in turns})} acting agents", ""]
    by = collections.defaultdict(list)
    for t in turns:
        by[t["agent"]].append(t)
    L.append("| agent | model | units used | attend | notes (pin) | opened / looked up | says / tells | offers / accepted | "
             "watch / teach / learn | refusals | first-level -> last |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for n, ts in by.items():
        model = (ts[0]["model"] or "").replace("claude-", "")
        units = f"{sum(t['used'] for t in ts)}/{sum(t['units'] for t in ts)}"
        att = collections.Counter(str(t.get("attend") or "-") for t in ts)
        replies = [t["reply"] for t in ts] + [t["talk_reply"] for t in ts if t.get("talk_reply")]
        notes = sum(len(r.get("note") or []) for r in replies)
        pins = sum(1 for r in replies if r.get("pin"))
        opened = sum(len(r.get("open") or []) for r in replies)
        looked = sum(len(r.get("look_up") or []) for r in replies)
        says = sum(len(r.get("say") or []) for r in replies)
        tells = sum(len(r.get("tell") or []) for r in replies)
        offers = sum(len(r.get("offers") or []) for r in replies)
        res = [x for t in ts for x in t["results"]]
        accepted = sum(1 for x in res if x.startswith("You accepted"))
        watch = sum(1 for p in (t["plan"] for t in ts) for a in p if a.get("do") == "watch")
        teach = sum(1 for x in res if x.startswith("You taught"))
        learn = sum(1 for x in res if " taught you " in x)
        refused = collections.Counter(x.split(":")[1].strip() for x in res if x.startswith("Refused"))
        k0 = spec["agents"][n].get("knows") or {}
        k1 = (state or {}).get("know", {}).get(n, {})
        changed = [f"{tech}: {('-' if tech not in k0 else (k0[tech] if isinstance(k0[tech], str) else k0[tech].get('level')))}->{r['level']}"
                   for tech, r in k1.items() if r["since"] >= 0]
        L.append(f"| {n} | {model} | {units} | {', '.join(f'{k} x{v}' for k, v in att.most_common(3))} | {notes} ({pins}) | "
                 f"{opened} / {looked} | {says} / {tells} | {offers} / {accepted} | {watch} / {teach} / {learn} | "
                 f"{sum(refused.values())}: {', '.join(f'{k} {v}' for k, v in refused.most_common(3))} | {'; '.join(changed) or '-'} |")
    L += ["", "| day | missed | short | deaths | fights | talked | offers | steals | cost $ |", "|---|---|---|---|---|---|---|---|---|"]
    for d in days:
        L.append(f"| {d['day'] + 1} | {', '.join(d['missed']) or '-'} | {', '.join(d['short']) or '-'} | {', '.join(d['deaths']) or '-'} | "
                 f"{len(d['fights'])} | {len(d['talked'])} | {len(d['offers'])} | {len(d['steals'])} | {d['cost_usd']:.2f} |")
    sizes = collections.defaultdict(list)
    cost = collections.Counter()
    for t in turns:
        m = (t["model"] or "").replace("claude-", "")
        sizes[m].append(len(t["prompt"]))
        for u in (t.get("usage") or {}, t.get("talk_usage") or {}):
            cost[m] += float(u.get("cc_equiv_usd") or 0)
    L += ["", "| model | turn prompt chars (mean, max) | cost $ |", "|---|---|---|"]
    for m, v in sizes.items():
        L.append(f"| {m} | {sum(v) // len(v)}, {max(v)} | {cost[m]:.2f} |")
    sysl = {n: len(s) for n, s in meta["systems"].items()}
    L.append(f"\nSystem prompt chars: mean {sum(sysl.values()) // max(1, len(sysl))}, max {max(sysl.values(), default=0)}.")
    if state:
        L.append("\nEnd: " + "; ".join(f"{n} {'dead (' + a['cause'] + ')' if not a['alive'] else ['starving', 'hungry', 'fed'][a['hunger'] + 2]}"
                                       for n, a in state["agents"].items()))
        L.append("Stores: " + "; ".join(f"{h['name']}: " + ", ".join(f"{q:.1f} {i}" for i, q in h["stock"].items() if q > 0.05)
                                        for h in state["houses"].values()))
        L.append("Fittings: " + (", ".join(f"{f['name']} (day {f['day'] + 1})" for f in state["fittings"]) or "none"))
    return "\n".join(L)


if __name__ == "__main__":
    print(summary(sys.argv[1]))
