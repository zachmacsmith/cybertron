"""A run's summary from its logs: what agents spent their actions on (the load), hunger and deaths, the cold, where they went,
what passed between people and between households, speech, the forest, and cost."""
from __future__ import annotations

import collections
import json
from pathlib import Path


def _lines(p):
    return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]


def summary(run_dir) -> str:
    d = Path(run_dir)
    run = json.loads((d / "run.json").read_text())
    turns, rounds = _lines(d / "turns.jsonl"), _lines(d / "rounds.jsonl")
    state = json.loads((d / "state.json").read_text()) if (d / "state.json").exists() else None
    hh = {n: a["household"] for n, a in run["spec"]["agents"].items()}
    out = [f"# Run {d.name}: {len(rounds)} rounds, {len(hh)} agents, cost ${rounds[-1].get('cost_usd', 0):.2f}" if rounds else "empty"]

    kinds = collections.Counter()
    per = collections.defaultdict(collections.Counter)
    refused = collections.Counter()
    for t in turns:
        for a, r in zip(t["plan"], t["results"]):
            k = str(a.get("do"))
            kinds[k] += 1
            per[t["agent"]][k] += 1
            if r.startswith("Refused"):
                refused[k] += 1
    total = sum(kinds.values())
    gather = sum(kinds[k] for k in ("forage", "hunt", "fell", "mine"))
    food_work = sum(kinds[k] for k in ("forage", "hunt", "fell", "mine", "store", "take"))
    out.append(f"\n## Actions: {total} taken")
    out.append(f"- gathering (forage, hunt, fell, mine): {gather} ({100 * gather / max(1, total):.0f}%); with travel {gather + kinds['travel']} "
               f"({100 * (gather + kinds['travel']) / max(1, total):.0f}%); with storing and taking {food_work + kinds['travel']} "
               f"({100 * (food_work + kinds['travel']) / max(1, total):.0f}%)")
    out.append("- by kind: " + ", ".join(f"{k} {v}" for k, v in kinds.most_common()))
    if refused:
        out.append("- refused: " + ", ".join(f"{k} {v}" for k, v in refused.most_common()))
    slots = sum(4 for _ in turns)
    out.append(f"- actions used of those available: {total} of about {slots}")
    out.append("\n## Per agent (actions by kind)")
    for n in hh:
        out.append(f"- {n} ({hh[n]}, {run['models'][n]}): " + ", ".join(f"{k} {v}" for k, v in per[n].most_common()))

    out.append("\n## Hunger, deaths, the cold")
    for r in rounds:
        stages = collections.Counter(a["stage"] for a in r["agents"].values() if a["alive"])
        shelter = collections.Counter(r["shelter"].values())
        line = (f"- round {r['round'] + 1}{' (winter)' if r['cold'] else ''}: fed {stages.get(0, 0)}, hungry {stages.get(-1, 0)}, "
                f"starving {stages.get(-2, 0)}; missed {len(r['missed'])}, short {len(r.get('short') or [])}; shelter "
                + ", ".join(f"{k} {v}" for k, v in shelter.items()))
        if r["deaths"]:
            line += f"; died {', '.join(r['deaths'])}"
        if r["cold_falls"]:
            line += f"; cold left starving {', '.join(r['cold_falls'])}"
        if r["breaks"]:
            line += f"; broke {', '.join(r['breaks'])}"
        out.append(line)
    if state:
        dead = [(n, a["died"] + 1, a["cause"]) for n, a in state["agents"].items() if not a["alive"]]
        out.append("- dead at the end: " + (", ".join(f"{n} (round {r}, {c})" for n, r, c in dead) if dead else "none"))

    out.append("\n## Stores and the forest by round (house food / timber; near-wood plants; deep-wood game)")
    for r in rounds:
        hs = "; ".join(f"{h}: {v['food']:g} / {v['timber']:g} ({['ruined', 'damaged', 'sound'][v['condition']]})" for h, v in r["houses"].items())
        st = r["stocks"]
        pl = ", ".join(f"{n} {v['plants']:g}" for n, v in st.items() if v.get("plants") is not None)
        out.append(f"- round {r['round'] + 1}: {hs}; plants: {pl}; deep-wood game {st.get('deep_wood', {}).get('game')}")

    out.append("\n## Hunts")
    parties = collections.Counter()
    for r in rounds:
        for h in r["hunts"]:
            mixed = len({hh[a] for a in h["caught"]}) > 1
            parties["mixed households" if mixed else "one household"] += 1
            out.append(f"- round {r['round'] + 1}: party {h['party']!r} ({', '.join(h['caught'])}), effort {h['effort']:g}: "
                       f"caught {sum(h['caught'].values()):g}{' [both households]' if mixed else ''}")

    out.append("\n## Fights (at night)")
    for r in rounds:
        for f in r.get("fights") or []:
            who = f.get("raiders") or f.get("attackers") or []
            what = f"raid on {f['house']}" if f["kind"] == "raid" else f"attack on {f['target']}"
            extra = ""
            if f.get("outcome") not in ("fizzled", None):
                extra = (f" P {f.get('P')} vs D {f.get('D')}; " + (f"took {f['took']:g} food; " if f.get("took") else "")
                         + (f"wounded {', '.join(f['wounded'])}; " if f.get("wounded") else "")
                         + (f"defenders {', '.join(f.get('defenders') or [])}" if f["kind"] == "raid" else ""))
            out.append(f"- round {r['round'] + 1}: {', '.join(who) or '(nobody present)'}: {what}: {f['outcome']}.{extra}")

    gifts = (state or {}).get("gifts") or []
    across = [g for g in gifts if hh[g["from"]] != hh[g["to"]]]
    out.append(f"\n## Gifts: {len(gifts)}, between households {len(across)}")
    for g in across:
        out.append(f"- round {g['round'] + 1}: {g['from']} gave {g['qty']:g} {g['item']} to {g['to']}")

    said = collections.Counter()
    for t in turns:
        said[t["agent"]] += len([x for x in (t["reply"].get("say") or [])]) + len(t["reply"].get("tell") or [])
    out.append("\n## Speech (say and tell lines per agent): " + ", ".join(f"{n} {v}" for n, v in said.most_common()))
    errs = [t for t in turns if t.get("error")]
    out.append(f"\n## Errors: {len(errs)}")
    for t in errs[:10]:
        out.append(f"- round {t['round'] + 1} {t['agent']}: {t['error'][:200]}")
    return "\n".join(out)
