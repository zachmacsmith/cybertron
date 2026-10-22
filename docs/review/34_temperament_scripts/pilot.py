"""The controlled pilot of review 34 §5.2: one seat of a played run, forked with its temperament varied one dimension at a time.

    python -I pilot.py RUN_DIR --at N --agent A [--dims fairness,sincerity,...] [--levels 0.05,0.95] [--replicates K]
                       [--out DIR] [--archetype NAME] [--keep-archetype]

RUN_DIR is a run of a personality.model hexaco world (e.g. cybertron/specs/temperament_pilot.yaml) that has played past round N.
For each dimension and level the script writes a schedule (DIR/<dim>_<level>.yaml: one set_temperament entry at round N,
round_start, for the seat, with that dimension at that percentile and every other dimension as drawn) plus a control
(DIR/control.yaml: the seat's own profile re-applied, so every arm goes through the same op). Every arm, the control included,
drops the seat's archetype unless --keep-archetype. The script prints one fork command per arm; every arm forks from the same
checkpoint with the same --replicates, so the arms differ only in the seat's profile and in post-fork sampling (ARCHITECTURE §8.4).

Measure the seat's decisions in the forked rounds (actions, votes, gifts, offers accepted or refused, in events.jsonl), not its
text: section 2 of the review found that text moves with the sentence while behaviour often does not.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("run")
    p.add_argument("--at", type=int, required=True, help="the fork round (0-based)")
    p.add_argument("--agent", required=True)
    p.add_argument("--dims", default="fairness,sincerity,forgiveness,trust,reciprocity,altruism,conformity",
                   help="comma-separated dimensions of cybertron/temperament.py")
    p.add_argument("--levels", default="0.05,0.95", help="comma-separated percentiles")
    p.add_argument("--archetype", default=None, help="also an arm with this archetype")
    p.add_argument("--keep-archetype", action="store_true", help="keep the seat's drawn archetype in every arm (default: none in "
                   "every arm, so an arm whose dimension leaves the archetype's region does not differ in two ways)")
    p.add_argument("--replicates", type=int, default=5)
    p.add_argument("--out", default="temperament_pilot")
    a = p.parse_args(argv)
    inst = json.loads((Path(a.run) / "instance.json").read_text())
    rec = next((x for x in inst["agents"] if x["id"] == a.agent), None)
    if rec is None or not rec.get("temperament"):
        sys.exit(f"{a.agent}: no temperament profile in {a.run} (needs personality.model hexaco)")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    base = {} if a.keep_archetype else {"archetype": "none"}
    arms = {"control": dict(base)}
    for d in [x for x in a.dims.split(",") if x]:
        for lv in [float(x) for x in a.levels.split(",")]:
            arms[f"{d}_{lv:g}"] = {**base, d: lv}
    if a.archetype:
        arms[f"archetype_{a.archetype}"] = {"archetype": a.archetype}
    for name, prof in arms.items():
        sched = [{"id": f"pilot:{name}", "at": {"round": a.at, "phase": "round_start"}, "op": "set_temperament",
                  "args": {"agent": a.agent, "profile": prof}, "note": f"review 34 pilot arm {name}"}]
        path = out / f"{name}.yaml"
        path.write_text(json.dumps(sched, indent=1) + "\n")              # JSON is YAML
        print(f"python -m cybertron fork {a.run} --at {a.at} --apply {path} --replicates {a.replicates} --out {out / name}")


if __name__ == "__main__":
    main()
