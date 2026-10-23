"""Variants of a world's spec, engine side: one village cut out of a region (for a single-node run), and a world whose roads hold
nothing (the comparison arm for roads, D2-104).

    python3 -m cybertron2.engine.variants one-node SPEC NODE OUT
    python3 -m cybertron2.engine.variants bare-roads SPEC OUT
"""
from __future__ import annotations

import copy
import sys

import yaml


def one_node(spec: dict, node: str) -> dict:
    """The village `node` alone: its parcels, buildings, herds, the households living there and their people, claims and debts among
    them; the rest of the region stays only in what people remember."""
    s = copy.deepcopy(spec)
    s["nodes"] = {node: s["nodes"][node]}
    parcels = set(s["nodes"][node]["parcels"])
    s["roads"] = []
    s["buildings"] = {b: x for b, x in (s.get("buildings") or {}).items() if x["parcel"] in parcels}
    households = {x.get("household") for x in s["buildings"].values() if x.get("household")}
    s["herds"] = {h: x for h, x in (s.get("herds") or {}).items() if x["parcel"] in parcels}
    s["agents"] = {n: a for n, a in s["agents"].items() if a.get("household") in households}
    people = set(s["agents"])
    keep = parcels | set(s["buildings"]) | set(s["herds"])
    s["claims"] = [c for c in s.get("claims") or [] if c["thing"][1] in keep and (c["claimant"] in households | people | {"anyone"})]
    s["agreements"] = [a for a in s.get("agreements") or [] if set(a["parties"]) <= people]
    s["incidents"] = [i for i in s.get("incidents") or [] if i.get("node") in (None, node)]
    s["signs"] = [g for g in s.get("signs") or [] if g.get("node") in (None, "all", node)]
    for c in s.get("customs") or []:
        if isinstance(c.get("nodes"), list):
            c["nodes"] = [x for x in c["nodes"] if x == node] or "all"
    for a in s["agents"].values():
        if isinstance(a.get("holdings"), dict):
            a["holdings"] = {k: v for k, v in a["holdings"].items() if k in keep}
    s["name"] = f"{s['nodes'][node]['name']} alone (from {spec.get('name', 'a region')})"
    return s


def bare_roads(spec: dict) -> dict:
    """Every road bare, as before Package B: no terrain, no landmarks, nothing on it (D2-104; the switch D2-122 keeps)."""
    s = copy.deepcopy(spec)
    roads = []
    for e in s.get("roads") or []:
        extra = {k: v for k, v in next((x for x in e[3:] if isinstance(x, dict)), {}).items() if k not in ("terrain", "stretches")}
        roads.append(list(e[:3]) + [x for x in e[3:] if not isinstance(x, dict)] + [{**extra, "bare": True}])
    s["roads"] = roads
    return s


def main(argv=None):
    argv = argv or sys.argv[1:]
    if argv[0] == "one-node":
        out = one_node(yaml.safe_load(open(argv[1])), argv[2])
        dst = argv[3]
    elif argv[0] == "bare-roads":
        out = bare_roads(yaml.safe_load(open(argv[1])))
        dst = argv[2]
    else:
        raise SystemExit(__doc__)
    with open(dst, "w") as f:
        yaml.safe_dump(out, f, sort_keys=False, allow_unicode=True, width=140)


if __name__ == "__main__":
    main()
