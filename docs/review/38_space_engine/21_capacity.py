"""Review 38.21: what a world can feed, by node, if its people farm and eat competently (scenario_design.md §4: capacity at least
1.25 times demand, with food binding). Reads a generated world through the engine and its data.

    python docs/review/38_space_engine/21_capacity.py <world.yaml> [...]

Supply over the run, in rations: food in stores and hands (grain ground: 1.0 a grain, as a hand mill gives); standing crops (ground);
one more crop on every field that can be sown and ripen before winter, from seed at hand, at the field's fertility and ground; milk
from cows in milk; what forage and game give back a day. Slaughter is shown apart: it is the herd's capital, not its income.
Demand: everyone alive (children too) eats a ration a night, more out in the cold; fuel shown as timber against wood.
"""
from __future__ import annotations

import sys

from cybertron2.engine import farm as FM
from cybertron2.engine.data import CROPS, ITEMS
from cybertron2.engine.world import World, load_spec


def food_value(item, q):
    if item in ("grain", "rye"):
        return q * 1.0                                                          # ground (D2-60)
    return q * ITEMS.get(item, {}).get("food", 0.0)


def capacity(path):
    w = World(load_spec(path))
    days = w.days
    f = w.p["farming"]
    year = w.year_days()
    winter_day = next((d for d in range(days) if w.calendar(d)["season"] == "winter"), None)
    rows = []
    for nid, n in w.s["nodes"].items():
        ppl = [x for x, a in w.s["people"].items() if a["at"] == nid and a["alive"]]
        demand = len(ppl) * days * float(w.p["ration"])
        stores = 0.0
        for b in w.s["buildings"].values():
            if b["node"] == nid:
                stores += sum(food_value(i, q) for i, q in w.goods(b["stock"]).items())
        stores += sum(food_value(i, q) for x in ppl for i, q in w.goods(w.hands(x)).items())
        standing, resow, seed_need = 0.0, 0.0, 0.0
        for pid, p in w.s["parcels"].items():
            if p["node"] != nid or p["cover"] != "field":
                continue
            c = p.get("crop")
            ready = int(c["ripe_day"]) if c else 0
            if c:
                standing += c["left"] * (0.6 if c["crop"] == "legumes" else 1.0)
            g = FM.grow_days(year, "grain")
            sow_day = max(ready, 0) + 1
            if winter_day is None or sow_day + g < winter_day:                 # another crop before the frost
                seed = float(p["size"]) * float(f["plot_seed"])
                seed_need += seed
                resow += seed * float(f["ratio"]) * p["fertility"] * FM.ground_mult(w.p, p) - seed
        milk = sum(min(h["in_milk"], h["cows"]) * 0.8 for h in w.s["herds"].values() if h["node"] == nid) * days
        wild = 0.0
        for p in w.s["parcels"].values():
            if p["node"] != nid:
                continue
            for key, r in p["res"].items():
                if key in ("plants", "game") and r["K"] > 0:
                    wild += (r["r"] * r["K"] / 4 + (0.005 * r["K"] if key == "plants" else 0)) * (1.5 if key == "game" else 1.0)
        wild *= days * 0.7                                                        # winter slows regrowth
        herd_meat = sum(h["cows"] * 40 + h["oxen"] * 50 + h["bulls"] * 50 for h in w.s["herds"].values() if h["node"] == nid) * 1.5
        supply = stores + standing + resow + milk + wild
        timber_need = sum(1 for b in w.s["buildings"].values() if b["node"] == nid and any(b["fittings"].get(x) for x in ("hearth", "fire ring"))
                          and b["fittings"].get("beds")) * sum(2.0 if w.cold(d) else 0.5 for d in range(days))
        wood = sum(p["res"]["wood"]["S"] for p in w.s["parcels"].values() if p["node"] == nid and "wood" in p["res"])
        timber_held = sum(w.goods(b["stock"]).get("timber", 0) for b in w.s["buildings"].values() if b["node"] == nid)
        rows.append((n["name"], len(ppl), demand, stores, standing, resow, milk, wild, supply, herd_meat, timber_need, timber_held, wood))
    print(f"\n## {w.spec.get('name', path)}: {days} days, winter from day {winter_day}\n")
    print("| Node | People | Eat | Stores | Standing | One more crop | Milk | Wild | Supply | x demand | Herd as meat | Fuel need | Timber held | Wood standing |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    tot = [0.0] * 3
    for r in rows:
        ratio = r[8] / r[2] if r[2] else 0
        tot[0] += r[2]
        tot[1] += r[8]
        tot[2] += r[9]
        print(f"| {r[0]} | {r[1]} | {r[2]:.0f} | {r[3]:.0f} | {r[4]:.0f} | {r[5]:.0f} | {r[6]:.0f} | {r[7]:.0f} | {r[8]:.0f} | "
              f"{ratio:.2f} | {r[9]:.0f} | {r[10]:.0f} | {r[11]:.0f} | {r[12]:.0f} |")
    print(f"| all | | {tot[0]:.0f} | | | | | | {tot[1]:.0f} | {tot[1] / tot[0]:.2f} | {tot[2]:.0f} | | | |")
    from cybertron2.engine import capacity as CP                              # what the land gives back a year (D2-161, 02za)
    print("\nA year, by flows (D2-161: seed at about 60-70% of the scarcer):\n")
    print("| Node | People now | Its food keeps | Its woods keep warm | Binds | People now / what it keeps |")
    print("|---|---|---|---|---|---|")
    for nid, n in w.s["nodes"].items():
        c = CP.node(w, nid)
        share = f"{c['people'] / c['keeps']:.0%}" if c["keeps"] > 0.05 else ("none kept" if c["people"] else "")
        print(f"| {n['name']} | {c['people']} | {c['food_people']:.1f} | {c['heat_people']:.1f} | {c['binds']} | {share} |")


if __name__ == "__main__":
    for path in sys.argv[1:]:
        capacity(path)
