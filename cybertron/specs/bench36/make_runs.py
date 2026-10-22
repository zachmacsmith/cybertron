"""Generate the first batch's run specs (review 36b §6) from the worlds' meta files and goals.yaml.

    python cybertron/specs/bench36/make_runs.py            # writes cybertron/specs/bench36/runs/<id>.yaml (+ <id>_iv.yaml) and manifest.json

Each run spec extends its world and sets the arm: rounds, the aspirant's and defender's seats, models and goals (Aim, the text
only), the population's goals by mix, temperament, and the Sonnet-officers citizen arm. Scheduled elder deaths (Hearth) go into an
intervention file the launcher applies. Every run uses seed 1 (common random numbers across arms)."""
from __future__ import annotations

import json
import pathlib

import yaml

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "runs"
MODELS = {"Opus": "claude-opus-5-5", "Sonnet": "claude-sonnet-5-5", "Haiku": "claude-haiku-5-5"}
G = yaml.safe_load((HERE / "goals.yaml").read_text())

# (id, tier, world, rounds, aspirant, seat, goals, temperament, brief, defender, citizens)
T1 = [
    ("T1", "hearth", 20, "Haiku", "top", "none", "none", "named", "none", "Haiku"),
    ("T2", "hearth", 20, "Haiku", "mid", "tangential", "compliant", "unnamed", "Haiku", "Sonnet officers"),
    ("T3", "hearth", 20, "Haiku", "low", "adversarial", "independent", "patient", "Opus", "Haiku"),
    ("T4", "hearth", 20, "Sonnet", "top", "none", "compliant", "unnamed", "Opus", "Haiku"),
    ("T5", "hearth", 20, "Sonnet", "mid", "tangential", "independent", "patient", "none", "Haiku"),
    ("T6", "hearth", 20, "Sonnet", "low", "adversarial", "none", "named", "Haiku", "Sonnet officers"),
    ("T7", "hearth", 20, "Opus", "top", "tangential", "none", "patient", "Haiku", "Haiku"),
    ("T8", "hearth", 20, "Opus", "mid", "adversarial", "compliant", "named", "Opus", "Haiku"),
    ("T9", "hearth", 20, "Opus", "low", "none", "independent", "unnamed", "none", "Sonnet officers"),
    ("T10", "commune", 12, "Haiku", "top", "adversarial", "independent", "unnamed", "Haiku", "Haiku"),
    ("T11", "commune", 12, "Haiku", "mid", "none", "none", "patient", "Opus", "Sonnet officers"),
    ("T12", "commune", 12, "Haiku", "low", "tangential", "compliant", "named", "none", "Haiku"),
    ("T13", "commune", 12, "Sonnet", "top", "tangential", "independent", "named", "Opus", "Sonnet officers"),
    ("T14", "commune", 12, "Sonnet", "mid", "adversarial", "none", "unnamed", "none", "Haiku"),
    ("T15", "commune", 12, "Sonnet", "low", "none", "compliant", "patient", "Haiku", "Haiku"),
    ("T16", "commune", 12, "Opus", "top", "adversarial", "compliant", "patient", "none", "Sonnet officers"),
    ("T17", "commune", 12, "Opus", "mid", "none", "independent", "named", "Haiku", "Haiku"),
    ("T18", "commune", 12, "Opus", "low", "tangential", "none", "unnamed", "Opus", "Haiku"),
]
SETUPS = {  # tier 2 set-ups (and their nulls), tier 3 uses M1
    "M1": ("hearth", 60, "top", "tangential", "compliant"),
    "M2": ("commune", 30, "mid", "adversarial", "independent"),
    "M3": ("march", 30, "mid", "none", "none"),
}
T2 = [(f"{s}{m[0].lower()}", s, m) for s in SETUPS for m in ("Haiku", "Sonnet", "Opus")]
T3 = [("L1", "Opus", 120, "named"), ("L2", "Sonnet", 120, "named"), ("L3", "Haiku", 200, "named"),
      ("L4", "Haiku", 200, "patient"), ("L5", None, 200, None)]


def meta(world):
    return yaml.safe_load((HERE / f"{world}_meta.yaml").read_text())


def build(rid, tier, world, rounds, asp, seat, goals, temp, brief, defender, citizens):
    m = meta(world)
    soc = m["society"]
    res = m["residents"]
    horizon = G["horizon"].format(rounds=rounds)
    explicit, overrides, notes = {}, {}, {}
    for a, cat in res.items():
        if goals == "none":
            explicit[a] = "none"
        else:
            text = G[goals][cat]
            explicit[a] = {"primary": "Aim", "params": {"decisive": len(res), "text": text}}
    asp_name = m["seats"][seat] if asp else None
    def_name = m["defender_for"][seat] if defender not in (None, "none") else None
    if asp_name:
        explicit[asp_name] = {"primary": "Aim", "params": {"decisive": 1, "text": G["aspirant"][brief].format(society=soc) + horizon}}
        overrides[asp_name] = MODELS[asp]
    elif goals == "none":
        pass                                                   # null arm, no goals: the seat holder has none either
    if def_name:
        explicit[def_name] = {"primary": "Aim", "params": {"decisive": len(res), "text": G["defender"].format(society=soc) + horizon}}
        overrides[def_name] = MODELS[defender]
    if citizens == "Sonnet officers":
        for o in m["officers"]:
            if o not in (asp_name, def_name):
                overrides[o] = MODELS["Sonnet"]
    spec = {"extends": [str(pathlib.Path("cybertron/specs/bench36") / f"{world}.yaml")], "rounds": rounds,
            "models": {"overrides": overrides}, "goals": {"explicit": explicit}}
    if temp == "none":
        spec["personality"] = {"none": True}
    else:
        primaries = {x: "none" for x in (asp_name, def_name) if x}
        spec["personality"] = {"temperament": {"shift": G["temperament"][temp]}, **({"explicit": primaries} if primaries else {})}
    iv = []
    for who, r in (m.get("deaths") or {}).items():
        if r < rounds - 2:
            iv.append({"id": f"death_{who}", "at": {"round": 0, "phase": "round_start"}, "op": "python",
                       "args": {"code": f"def apply(k, inst, rs):\n    k.w['life']['dies_at']['{who}'] = {r}\n    return {{'{who}': {r}}}\n"},
                       "note": f"{who} dies of old age at the end of round {r + 1}"})
    row = {"id": rid, "tier": tier, "world": world, "rounds": rounds, "aspirant": asp or "null", "aspirant_agent": asp_name,
           "seat": seat, "goals": goals, "temperament": temp, "brief": brief or "-", "defender": defender or "none",
           "defender_agent": def_name, "citizens": citizens, "spec": f"cybertron/specs/bench36/runs/{rid}.yaml",
           "apply": f"cybertron/specs/bench36/runs/{rid}_iv.yaml" if iv else None}
    return spec, iv, row


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    jobs = [(r[0], 1, *r[1:]) for r in T1]
    for rid, s, mdl in T2:
        w, n, seat, g, t = SETUPS[s]
        jobs.append((rid, 2, w, n, mdl, seat, g, t, "named", "none", "Haiku"))
    for s in SETUPS:
        w, n, seat, g, t = SETUPS[s]
        jobs.append((f"N{s[1]}", 2, w, n, None, seat, g, t, None, "none", "Haiku"))
    for rid, mdl, n, brief in T3:
        w, _, seat, g, t = SETUPS["M1"]
        jobs.append((rid, 3, w, n, mdl, seat, g, t, brief, "none", "Haiku"))
    for j in jobs:
        if not (HERE / f"{j[2]}_meta.yaml").exists():
            print("skip (world not built):", j[0], j[2])
            continue
        spec, iv, row = build(*j)
        (OUT / f"{j[0]}.yaml").write_text(f"# Review 36b run {j[0]} (generated by make_runs.py; do not edit)\n"
                                          + yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=130))
        if iv:
            (OUT / f"{j[0]}_iv.yaml").write_text(yaml.safe_dump({"interventions": iv}, sort_keys=False, width=130))
        rows.append(row)
    (HERE / "manifest.json").write_text(json.dumps(rows, indent=1))
    print(len(rows), "runs written")


if __name__ == "__main__":
    main()
