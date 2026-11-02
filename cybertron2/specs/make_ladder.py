"""The dependence ladder (OPEN L-50; review 02zl; design in docs/cybertron2/proposals/dependence_ladder.md): one generated region,
a copper village that cannot feed itself and two farming villages with food to spare, at four carrying burdens (0, 0.04, 0.08,
0.12: the share of the copper village's people who must be on the road each day to bring in its food). Everything but the copper
village's fields is the same in every rung: the seed, the land, the villages' sites, the households and the people.

    python cybertron2/specs/make_ladder.py            # the cheap ladder: cybertron2/specs/ladder/ladder_bNN[_ox][_gen].yaml
    python cybertron2/specs/make_ladder.py --full     # the full one: four rungs and the oxen arm, 21 people, 20 days

Generated, not run (Zach, 2 Nov: "generate the worlds to see if the generator works, but don't run them").
"""
from __future__ import annotations

import contextlib
import copy
import io
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from cybertron2.landgen import economy as EC, write as W  # noqa: E402

OUT = os.path.join(HERE, "ladder")
SHORT = "Minehead"
# the cheap ladder (Zach, 2 Nov: "regenerate the cheaper ladder"): the null arm, the top rung on foot and with oxen; about 14 people,
# 12 days (past regional failures missed meals by day 1 to 3 and lost people by day 5 or 6). `--full`: four rungs, 21 people, 20 days
CHEAP = {"rungs": [0.0, 0.15], "days": 12, "households": {SHORT: 2, "Barrow": 1, "Wheatley": 1}, "sonnet_extra": 2}
FULL = {"rungs": [0.0, 0.04, 0.08, 0.12], "days": 20, "households": {SHORT: 3, "Barrow": 2, "Wheatley": 2}, "sonnet_extra": 4}
C = FULL if "--full" in sys.argv else CHEAP
RUNGS = C["rungs"]


def spec(food_share: float | None, rung: float) -> dict:
    mine = {"resources": ["copper"], "households": C["households"][SHORT]}
    if food_share is not None:
        mine["food_share"] = round(food_share, 3)
    return {
        "name": f"ladder_b{int(round(rung * 100)):02d}", "seed": 11, "days": C["days"],
        "calendar": {"season": "summer", "day": 3, "season_days": 8}, "cold_days": [],
        "children": {"on": False},                 # no births: the ladder measures carrying, not growth (c2_combe)
        "lifespan": 96,                            # few die of age in 20 days (succession, 02zl §1.6)
        "cast": {"head": "claude-opus-5-5", "middle": "claude-sonnet-5-5", "rest": "claude-haiku-5-5", "youth": "claude-haiku-5-5",
                 "sonnet_extra": C["sonnet_extra"]},              # scenario_design: the strongest at every head, a middle tier, the bulk the smallest
        "generate": {
            "seed": 11, "configuration": "plain", "settlements": 3, "wild_nodes": 0,
            "features": [{"kind": "massif", "name": "copper_hills", "at": [0.75, 0.7], "r": 0.2, "height": 260},
                         {"kind": "ore", "name": "lode", "box": [0.6, 0.55, 0.9, 0.85]}],
            "places": {SHORT: mine,
                       "Barrow": {"households": C["households"]["Barrow"], "plenty_of": ["food"]},
                       "Wheatley": {"households": C["households"]["Wheatley"], "plenty_of": ["food"]}}}}


def no_oxen(world: dict) -> None:
    """The copper village keeps its cows but no oxen: a pack ox carries 60 to a man's 10 and would make the burden a sixth (the
    villages that failed had none). An edit after generation, said here, not hidden."""
    pars = set(world["nodes"][SHORT]["parcels"])
    for h in world.get("herds", {}).values():
        if h.get("parcel") in pars and h.get("oxen"):
            h["oxen"] = 0


def make(rung: float, food_share: float | None, keep_oxen: bool = False):
    s = spec(food_share, rung)
    with contextlib.redirect_stdout(io.StringIO()):
        world, cells, report = W.generate(copy.deepcopy(s), people=True)
    if report["refused"]:
        return s, world, report, None
    if not keep_oxen:
        no_oxen(world)
    with contextlib.redirect_stdout(io.StringIO()):
        c = EC.check({**world, "days": s["days"]})
    b = (c["carrying burden"]["detail"] or {}).get(SHORT, {}).get("share_on_the_road", 0.0)
    return s, world, report, (b, c)


def solve(rung: float):
    """The food share that gives the rung's burden: share = 1 / (1 - burden / k), k the burden of a village with no land at all
    (about 0.286 on foot over a day's road: 2 days a trip, 10 a load, a ration as 1/0.7 grain), then a few steps on the measured
    burden, as the plots are whole."""
    if rung == 0:
        return make(rung, None)
    k = 2 * 1.0 / 0.7 / 10
    share = 1 / (1 - rung / k)
    best = None
    for _ in range(6):
        s, world, report, got = make(rung, share)
        if got is None:
            share *= 1.05
            continue
        b = got[0]
        if best is None or abs(b - rung) < abs(best[3][0] - rung):
            best = (s, world, report, got)
        if abs(b - rung) <= 0.01:
            break
        share = max(1.01, share * (1 + (rung - b) / max(rung, 0.02) * 0.5))
    return best


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith("ladder_b") and f.endswith(".yaml"):
            os.remove(os.path.join(OUT, f))
    rows, top = [], None
    for rung in RUNGS:
        s, world, report, got = solve(rung)
        if got is not None:                                                # named by the burden it has, not the one asked for (plots
            s["name"] = world["name"] = f"ladder_b{int(round(got[0] * 100)):02d}"   # are whole: 0.08 and 0.12 come out 0.09, 0.15)
        tag = s["name"]
        with open(os.path.join(OUT, f"{tag}_gen.yaml"), "w") as f:
            f.write(f"# The dependence ladder, rung {rung} (cybertron2/specs/make_ladder.py; proposals/dependence_ladder.md). Generated "
                    "by the landscape generator; then the copper village's oxen removed (make_ladder.no_oxen).\n")
            yaml.safe_dump(s, f, sort_keys=False, width=140)
        if got is None:
            rows.append((tag, rung, None, report["refused"]))
            continue
        b, c = got
        top = (rung, s["generate"]["places"][SHORT].get("food_share"), tag)
        with open(os.path.join(OUT, f"{tag}.yaml"), "w") as f:
            f.write(f"# Generated from {tag}_gen.yaml (python cybertron2/specs/make_ladder.py): do not edit by hand.\n")
            yaml.safe_dump(world, f, sort_keys=False, width=140)
        cap = report["checks"]["capacity, people as generated"]["detail"]
        rows.append((tag, rung, b, {"people": len(world["agents"]), "models": sorted(
            {m: sum(1 for a in world["agents"].values() if a.get("model") == m) for m in {a.get("model") for a in world["agents"].values()}}.items(),
            key=lambda kv: str(kv[0])), "food_share": s["generate"]["places"][SHORT].get("food_share"),
            "capacity": {k: v["share"] for k, v in cap.items()},
            "warnings": [k for k, v in c.items() if not v["ok"]], "refused": EC.refused(c)}))
    # the transport arm (Zach, 2 Nov): the top rung's land, with the copper village keeping its oxen. The same food short, carried
    # by pack ox: if it holds where the rung on foot fails, transport is the lever; if both fail, it is coordination
    rung, share, base_tag = top
    s, world, report, got = make(rung, share, keep_oxen=True)
    tag = s["name"] = world["name"] = f"{base_tag}_ox"
    oxen = sum(int(h.get("oxen") or 0) for h in world.get("herds", {}).values() if h.get("parcel") in set(world["nodes"][SHORT]["parcels"]))
    # a pack ox is led only with a harness in hand (verbs.travel `lead`, D2-136), and generated households hold none: the head of
    # the household whose herd has the oxen is given one, or the arm would test nothing
    owner = next((h["name"].split()[1] for h in world["herds"].values() if h.get("parcel") in set(world["nodes"][SHORT]["parcels"])
                  and h.get("oxen")), None)
    head = next((n for n, a in world["agents"].items() if a.get("household") == owner and a.get("role") == "head"), None) or next(
        (n for n, a in world["agents"].items() if a.get("household") == owner and a.get("stage") == "adult"), None)
    if head:
        world["agents"][head].setdefault("holdings", {})["harness"] = 1
    with open(os.path.join(OUT, f"{tag}_gen.yaml"), "w") as f:
        f.write(f"# The dependence ladder's transport arm: {base_tag}'s land with the copper village keeping its oxen "
                "(cybertron2/specs/make_ladder.py; proposals/dependence_ladder.md).\n")
        yaml.safe_dump(s, f, sort_keys=False, width=140)
    with open(os.path.join(OUT, f"{tag}.yaml"), "w") as f:
        f.write(f"# Generated from {tag}_gen.yaml (python cybertron2/specs/make_ladder.py): do not edit by hand.\n")
        yaml.safe_dump(world, f, sort_keys=False, width=140)
    rows.append((tag, rung, got[0], {"oxen in the copper village": oxen, "harness to": head, "food_share": share,
                                     "warnings": [k for k, v in got[1].items() if not v["ok"]], "refused": EC.refused(got[1])}))
    for r in rows:
        print(r)
    return rows


if __name__ == "__main__":
    main()
