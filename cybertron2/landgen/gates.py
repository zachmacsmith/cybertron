"""The access-gate probe (scenario_design §4: "verify every access gate in a dry run, per action"), for any world file with people.

    python -m cybertron2.landgen.gates <world.yaml> [out.json]

For each place and each gather or work technique, the best-suited person there tries it once, on a fresh copy of the world: someone
who knows the craft if anyone there does; at an unexplored place, someone who knows the place walks in (else anyone). Then every
road is tried from each end, and each unexplored place both by name (by one who knows it) and by its way (by a stranger, D4-47).
It reports what works where and every refusal's reason, so a gate that is shut for everyone (no one knows mining; rock with no
stone) shows before a run, which a bot run does not show: bots wander and starve whatever the world (review 02zn).
"""
from __future__ import annotations

import collections
import contextlib
import copy
import io
import json
import sys

from cybertron2.engine import run as R, verbs as V
from cybertron2.engine.data import ITEMS, TECHNIQUES
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SKIP = {"care", "herd"}                     # need a child or a herd named; checked by their own tests
ARGS = {"sow": {"item": "grain", "qty": 2}}  # what a technique needs said to be tried at all
# refusals that are the moment or the inputs, not a shut gate: a crop not ripe or standing, no seed or dung to hand, no such ground
SITUATIONAL = ("not ripe", "has a crop in it", "say which", "you have 0.0 to hand", "there is no dung", "nowhere here",
               "sown as thick", "say whose", "needs", "no gate", "no fence", "nothing to", "no one lying", "not wet ground",
               "not hill ground", "is sound", "no ripe crop", "need a tool")


def _ok(out: str) -> bool:
    return not out.startswith(("Refused", "CRASH", "Not done"))


def probe(spec: dict) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        base = World(copy.deepcopy(spec))
    base.s["today"] = R.blank_today()
    agents = spec.get("agents") or {}
    knows = lambda n, t: t in ((agents.get(n) or {}).get("knows") or {})
    grown = lambda w, n: w.s["people"][n].get("stage") in ("adult", "elder", "youth") and w.s["people"][n].get("alive", True)
    techs = sorted(k for k, t in TECHNIQUES.items() if t.get("verb") in ("gather", "work") and k not in SKIP)

    def attempt(w, who, a):
        try:
            return V.do(Here(w, who), Mind(w, who), a)
        except Exception as e:                                             # noqa: BLE001 (a crash is a finding)
            return f"CRASH {type(e).__name__}: {e}"

    gates = collections.defaultdict(dict)
    for nid, node in base.s["nodes"].items():
        covers_here = {p["cover"] for p in base.s["parcels"].values() if p["node"] == nid}
        for tech in techs:
            want = set((TECHNIQUES[tech].get("at") or {}).get("covers") or [])
            if want and not want & covers_here:                            # no such ground here: nothing to gate
                gates[node["name"]][tech] = {"who": None, "walked in": False, "result": "Refused: nowhere here: no such ground"}
                continue
            w = copy.deepcopy(base)
            tool = lambda n: any(q >= 1 and (ITEMS.get(i) or {}).get("tool") for i, q in w.goods(w.hands(n)).items())
            folk = sorted((n for n, a in w.s["people"].items() if a.get("at") == nid and grown(w, n)),
                          key=lambda n: (not knows(n, tech), not tool(n), n))     # one who knows it and holds a tool, as one would send
            moved = False
            if not folk:
                knowers = [n for n, a in agents.items() if nid in (a.get("places") or []) and n in w.s["people"] and grown(w, n)]
                folk = sorted(knowers, key=lambda n: (not knows(n, tech), n)) or sorted(n for n in w.s["people"] if grown(w, n))
                if not folk:
                    continue
                w.s["people"][folk[0]]["at"] = nid
                moved = True
            who = folk[0]
            if tech == "reap":                                             # try reaping on the day the first crop here ripens
                ripe = [int(c["ripe_day"]) for pid, par in w.s["parcels"].items() if par["node"] == nid
                        for c in ([par.get("crop")] + [sh.get("crop") for sh in par.get("shares") or []]) if c and c.get("ripe_day") is not None]
                if ripe:
                    w.s["day"] = max(w.s["day"], min(ripe))
            out = attempt(w, who, {"do": TECHNIQUES[tech]["verb"], "what": tech, **ARGS.get(tech, {})})
            gates[node["name"]][tech] = {"who": who, "walked in": moved, "result": out}
    roads = []
    names = {n["name"] for n in base.s["nodes"].values()}
    for rd in base.s["roads"].values():
        for a, b in ((rd["a"], rd["b"]), (rd["b"], rd["a"])):
            if base.s["nodes"][a].get("unexplored"):
                continue
            folk = [n for n, p in base.s["people"].items() if p.get("at") == a and grown(base, n)]
            if not folk:
                continue
            tries = []
            if base.s["nodes"][b].get("unexplored"):
                knowers = [n for n in folk if b in ((agents.get(n) or {}).get("places") or [])]
                strangers = [n for n in folk if n not in knowers]
                if knowers:
                    tries.append((knowers[0], base.s["nodes"][b]["name"]))
                if strangers:
                    w = copy.deepcopy(base)
                    way = next((n for _, n, d, t in Here(w, strangers[0]).roads() if n not in names), "an unexplored way")
                    tries.append((strangers[0], way))
            else:
                tries.append((folk[0], base.s["nodes"][b]["name"]))
            for who, to in tries:
                w = copy.deepcopy(base)
                roads.append({"from": base.s["nodes"][a]["name"], "to": base.s["nodes"][b]["name"], "as": to, "who": who,
                              "result": attempt(w, who, {"do": "travel", "to": to})})
    return {"gates": gates, "roads": roads}


def summary(res: dict) -> dict:
    """What works where; the techniques no one can do anywhere; crashes; roads that refuse."""
    works = {node: sorted(t for t, r in g.items() if _ok(r["result"])) for node, g in res["gates"].items()}
    anywhere = set().union(*works.values()) if works else set()
    every = set(t for g in res["gates"].values() for t in g)
    situational = {t for g in res["gates"].values() for t, r in g.items() if any(k in r["result"] for k in SITUATIONAL)}
    nowhere = every - anywhere
    return {"works": works, "shut everywhere": sorted(nowhere - situational), "only the moment or inputs": sorted(nowhere & situational),
            "crashes": [(n, t, r["result"]) for n, g in res["gates"].items() for t, r in g.items() if r["result"].startswith("CRASH")],
            "roads refused": [(r["from"], r["to"], r["as"], r["result"]) for r in res["roads"] if not _ok(r["result"])]}


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    res = probe(load_spec(argv[0]))
    s = summary(res)
    for node, ts in s["works"].items():
        print(f"{node}: {', '.join(ts)}")
    print("shut everywhere:", ", ".join(s["shut everywhere"]) or "none")
    print("not now (the moment or inputs):", ", ".join(s["only the moment or inputs"]) or "none")
    print("crashes:", s["crashes"] or "none")
    print("roads refused:", s["roads refused"] or "none")
    if len(argv) > 1:
        with open(argv[1], "w") as f:
            json.dump(res, f, indent=1)
    return 1 if s["crashes"] or s["roads refused"] or s["shut everywhere"] else 0


if __name__ == "__main__":
    sys.exit(main())
