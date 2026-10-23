"""Review 38.19: the region's economics from the engine's own numbers (cybertron2/engine/data.py), not from 37.2's model.

    python docs/review/38_space_engine/19_region_model.py [spec.yaml]

Part 1 prints what a unit of work buys by each method, what carrying costs, and what a harvest window asks of a household.
Part 2 (given a generated spec) balances each node over the run: food and fuel needed against what its land, stores and herds give,
and the labour its own people have, so the imports each node depends on, and the carriers they need, are visible before a run.
"""
from __future__ import annotations

import sys

import yaml

from cybertron2.engine.data import ITEMS, PHYSICS as P, TECHNIQUES as T

F = P["farming"]
UNITS = sum(P["units"].values()) / 4                       # a working person's units a day, averaged over the year


def per_unit():
    """Food (rations) or goods per unit of work, by method and tool."""
    rows = []
    sow_units = 1 / (F["seed_per_unit"] * F["return"])       # units of sowing per grain grown (one unit sows 3 seed -> 15 grain)
    weed = (1 + F["weed_max"]) / (1 + F["weed_max"] / F["weed_step"] / (F["seed_per_unit"] * F["return"]))   # rough: weeding pays
    for tool, m in T["reap"]["tools"].items():
        reap = T["reap"]["yield"]["base"] * m / T["reap"]["units"]
        net = 1 - 1 / F["return"]                             # a fifth of the crop goes back as seed
        rows.append((f"grain, reaped {tool}", round(net / (sow_units + 1 / reap), 2), "rations a unit (sow + reap, seed kept)"))
    rows.append(("wild food, a full stand", T["forage"]["yield"]["base"], "rations a unit, falling with the stand (x S/K)"))
    rows.append(("wild food, a stand held at half", T["forage"]["yield"]["base"] / 2, "rations a unit, where regrowth is fastest"))
    for tool, m in T["fell"]["tools"].items():
        rows.append((f"timber, felled {tool}", round(T["fell"]["yield"]["base"] * m / T["fell"]["units"], 2), "timber a unit"))
    return rows


def regrowth(res: dict) -> float:
    """The most a stand gives back a day, held at half (logistic, plus the engine's small fast-regime term)."""
    return res["r"] * res["K"] / 4 + 0.005 * res["K"]


def carrying():
    """Units of work per unit carried one edge, out and back (a day on the road each way)."""
    out = []
    day = UNITS
    for how, cap in (("on foot", P["carry"]["foot"]), ("with a pack", P["carry"]["foot"] + ITEMS["pack"]["carry"]),
                     ("with a handcart (track)", P["carry"]["foot"] + ITEMS["handcart"]["carry"])):
        out.append((how, cap, round(2 * day / cap, 2), round(day / cap, 2)))
    return out


def harvest(size, adults, tool="crude"):
    """A field sown full: the grain at stake, and the units it takes to reap it inside the window."""
    grain = size * F["seed_per_unit"] * 2 * F["return"] * (1 + F["weed_max"])
    units = grain / (T["reap"]["yield"]["base"] * T["reap"]["tools"][tool] / T["reap"]["units"])
    have = adults * P["units"]["summer"] * F["window"]
    return round(grain), round(units), have


def balance(spec: dict):
    days = int(spec.get("days", 20))
    cold = len(spec.get("cold_days") or [])
    people = {}
    for n, a in (spec.get("agents") or {}).items():
        hh = a["household"]
        node = next(b["parcel"] for b in spec["buildings"].values() if b.get("household") == hh and (b.get("fittings") or {}).get("beds"))
        node = next(k for k, v in spec["nodes"].items() if node in v["parcels"])
        people.setdefault(node, []).append(a["stage"])
    print(f"\n## Each node over {days} days ({cold} cold nights)\n")
    print("| Node | People (working) | Food needed | Stores | Crops standing | Field room a cycle | Forage + game a day | Timber needed | Wood standing |")
    print("|---|---|---|---|---|---|---|---|---|")
    for k, v in spec["nodes"].items():
        ppl = people.get(k, [])
        work = sum(s in ("adult", "youth", "elder") for s in ppl)
        need = len(ppl) * days * P["ration"]
        stores = sum(q * ITEMS[i]["food"] for b in spec["buildings"].values() if b["parcel"] in v["parcels"]
                     for i, q in (b.get("stock") or {}).items() if i in ITEMS)
        crops = sum((p.get("state") or {}).get("crop", {}).get("left", 0) for p in v["parcels"].values())
        room = sum(p["size"] * F["seed_per_unit"] * 2 * F["return"] for p in v["parcels"].values() if p["cover"] == "field")
        wild = sum(regrowth(r) * (1.5 if key == "game" else 1.0) for p in v["parcels"].values()
                   for key, r in (p.get("state") or {}).items() if key in ("plants", "game"))
        hearths = sum(1 for b in spec["buildings"].values() if b["parcel"] in v["parcels"] and (b.get("fittings") or {}).get("beds"))
        fuel = hearths * (P["fuel"]["normal"] * (days - cold) + P["fuel"]["cold"] * cold)
        wood = sum(r["S"] for p in v["parcels"].values() for key, r in (p.get("state") or {}).items() if key == "wood")
        print(f"| {v['name']} | {len(ppl)} ({work}) | {need:g} | {stores:g} | {crops:g} | {room:g} | {wild:.1f} | {fuel:g} | {wood:g} |")


def main():
    print("## What a unit of work buys (engine numbers)\n")
    print("| Method | Yield | |")
    print("|---|---|---|")
    for r in per_unit():
        print(f"| {r[0]} | {r[1]:g} | {r[2]} |")
    print(f"\nA working person has about {UNITS:g} units a day; eating takes {P['ration']:g} ration a day.")
    print("\n## Carrying one edge (a day's walk), in units of work per unit carried\n")
    print("| How | Load | Out and back empty | With a load both ways |")
    print("|---|---|---|---|")
    for how, cap, a, b in carrying():
        print(f"| {how} | {cap} | {a} | {b} |")
    print("\n## A harvest window (sown full and weeded, crude tools)\n")
    print("| Field size | Adults | Grain at stake | Units to reap it | Units the household has in the window |")
    print("|---|---|---|---|---|")
    for size, ad in ((3, 3), (4, 3), (6, 4), (6, 6)):
        g, u, h = harvest(size, ad)
        print(f"| {size} | {ad} | {g} | {u} | {h} |")
    if len(sys.argv) > 1:
        balance(yaml.safe_load(open(sys.argv[1])))


if __name__ == "__main__":
    main()
