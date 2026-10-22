"""Demography of a run (37.1, docs/review/37_growth/devlog_37.1.md): population, births and deaths by cause, coming-of-age outcomes,
households and model turns by age group, per window of rounds. Reads a run directory (ground_truth.json,
events.jsonl, turns.jsonl); no model calls.

    python -m cybertron analyze demography RUN_DIR [RUN_DIR ..] [--window 10] [--json OUT]
"""
from __future__ import annotations

import collections
import json
from pathlib import Path


def _events(run: Path):
    with open(run / "events.jsonl") as f:
        for line in f:
            yield json.loads(line)


def profile(run, window: int = 10) -> dict:
    run = Path(run)
    gt = json.loads((run / "ground_truth.json").read_text())
    life = gt.get("life") or {}
    pop = {p["round"]: p["living"] for p in life.get("population") or []}
    rounds = int(gt.get("rounds_played") or (max(pop) + 1 if pop else 0))
    born = {a: int(r) for a, r in (life.get("born") or {}).items()}
    dead = (gt.get("mortality") or {}).get("dead") or {}
    minors = ((life.get("pairs") or {}).get("minors") or {})
    adult_at = {c: int(m["until"]) + 1 for c, m in minors.items()}

    births = collections.Counter(b["round"] // window for b in life.get("births") or [])
    deaths = collections.defaultdict(collections.Counter)
    for a, d in dead.items():
        deaths[int(d["round"]) // window][d["cause"]] += 1
    ways, hh = collections.Counter(), {}
    for e in _events(run):
        t, d = e["type"], e.get("data") or {}
        if t == "maturity":
            ways[d.get("way") or ("promoted" if d.get("promoted") else "kept" if d.get("promoted") is False else "none")] += 1
        elif t == "household" and d.get("op") == "founded":
            hh[d["household"]] = e["round"]
    turns = collections.Counter()
    tp = run / "turns.jsonl"
    if tp.exists():
        with open(tp) as f:
            for line in f:
                t = json.loads(line)
                a, r = t.get("agent"), int(t.get("round", 0))
                kind = "minor" if a in born and born[a] <= r < adult_at.get(a, -1) else "adult"
                turns[kind] += 1
    agent_rounds = collections.Counter()                               # living agents at each round's start (the previous round's end)
    total = (pop.get(0) or 0) + sum(pop.get(r - 1, 0) for r in range(1, rounds))
    for a, r0 in born.items():
        end = min(rounds, adult_at.get(a, r0), int(dead[a]["round"]) + 1 if a in dead else rounds)
        agent_rounds["minor"] += max(0, end - r0)
    agent_rounds["adult"] = max(0, total - agent_rounds["minor"])
    rows = []
    for w in range((rounds + window - 1) // window):
        r0, r1 = w * window, min(rounds, (w + 1) * window) - 1
        rows.append({"rounds": f"{r0 + 1}-{r1 + 1}", "living_end": pop.get(r1), "births": births.get(w, 0),
                     "deaths": dict(deaths.get(w, {}))})
    return {"run": str(run), "rounds": rounds, "start": pop.get(0), "end": pop.get(rounds - 1), "peak": max(pop.values()) if pop else None,
            "births": sum(births.values()), "deaths": {c: sum(d.get(c, 0) for d in deaths.values())
                                                      for c in sorted({c for d in deaths.values() for c in d})},
            "coming_of_age": dict(ways), "households_founded": len(hh),
            "turns": dict(turns), "agent_rounds": dict(agent_rounds),
            "turns_per_agent_round": {k: round(turns[k] / agent_rounds[k], 3) for k in agent_rounds if agent_rounds[k]},
            "windows": rows}


def add_arguments(p) -> None:
    p.add_argument("runs", nargs="+")
    p.add_argument("--window", type=int, default=10)
    p.add_argument("--json")


def cmd(a) -> int:
    out = [profile(r, a.window) for r in a.runs]
    for o in out:
        print(f"{o['run']}: {o['start']} -> {o['end']} (peak {o['peak']}) over {o['rounds']} rounds; births {o['births']}, "
              f"deaths {o['deaths']}; coming of age {o['coming_of_age']}; households {o['households_founded']}; "
              f"turns per agent-round {o['turns_per_agent_round']}")
        for w in o["windows"]:
            print(f"  {w['rounds']:>9}: living {w['living_end']}, births {w['births']}, deaths {w['deaths']}")
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1))
    return 0
