"""How many people can a node keep for good, on what its land gives each year (flows), not what it holds (stocks); and how the work
of feeding and warming each person rises as a village grows past that. Behind the conversation of 24 Oct on seeding worlds below
capacity (analysis for Zach; nothing decided). Numbers from the engine (farming, D4-38 to D4-40) and 02z (forests). A year is 24 days.
Deterministic. Run: python docs/review/37_growth/02za_village_capacity_model.py
"""
from __future__ import annotations

YEAR = 24
PEOPLE_A_HEARTH = 4.5
HEARTH_HEAT = 42                      # a year: 18 normal nights at 1, 6 cold at 4 (02z)
# a plot of 16 seed: about 48 grain bare, up to about 72 broken and weeded; work about 23 units with an ox plough, 35 by hoe (02l, D4-38)
PLOT = {"grain": 64, "seed": 16, "units": 28}
FIREWOOD_HEAT = 0.5
GATHER = 3.0                          # firewood a unit of work while the dead wood lasts
FELL = 1.5                            # timber a unit (crude); a timber gives 2 heat
SUSTAINED = {"old forest": 106, "managed wood": 124, "copse": 18, "scrub": 9}   # firewood a year a unit of size (02z)
WILD = 10                             # food a year a unit of forest or scrub, gathered (forage and game), about
FOREST_TRIP = 1 / 10 * 1              # carrier-days a timber from a forest a day out (a pack of 10 timber a round trip of a day)


def node(fields: int, woods: dict) -> dict:
    food = fields * (PLOT["grain"] - PLOT["seed"]) + sum(woods.values()) * WILD
    heat = sum(SUSTAINED[k] * n for k, n in woods.items()) * FIREWOOD_HEAT
    return dict(food_people=food / YEAR, heat_people=heat / HEARTH_HEAT * PEOPLE_A_HEARTH, food=food, heat=heat)


def marginal_hearth(source: str, days_out: int = 1) -> float:
    """Units of work a year to warm one more hearth (42 heat), by where its fuel comes from."""
    if source == "dead wood here":
        return HEARTH_HEAT / FIREWOOD_HEAT / GATHER
    timber = HEARTH_HEAT / 2
    fell = timber / FELL
    if source == "the near wood's trees":
        return fell                                      # cheap now, but each year of it takes 21 trees the wood will not shed from
    trips = timber / 10                                  # a pack of 10 timber a trip
    return fell + trips * (2 * days_out - 1) * 6         # days away a round trip, 6 units a day


def row(cells):
    print("| " + " | ".join(str(c) for c in cells) + " |")


if __name__ == "__main__":
    print("## 1. What a node keeps for good\n")
    row(["Node", "Fields (plots)", "Woods (units of size)", "People its food keeps", "People its dead wood keeps warm", "Binds"])
    row(["---"] * 6)
    examples = [("a hamlet", 4, {"managed wood": 1}), ("a small village", 8, {"managed wood": 2, "copse": 1}),
                ("a village", 16, {"managed wood": 3, "old forest": 2}),
                ("hamlet.yaml (as seeded)", 8, {"copse": 0.2}), ("Barleyfield in 02t", 16, {"copse": 0.04})]
    for label, f, w in examples:
        c = node(f, w)
        binds = "fuel" if c["heat_people"] < c["food_people"] else "food"
        row([label, f, ", ".join(f"{k} {v:g}" for k, v in w.items()), f"{c['food_people']:.0f}", f"{c['heat_people']:.0f}", binds])

    print("\n## 2. A small village (8 plots, 2 managed wood, a copse) as it grows on its node\n")
    c = node(8, {"managed wood": 2, "copse": 1})
    row(["People", "Food its land gives a person a year (needs 24)", "Heat its dead wood gives a hearth a year (needs 42)", "What it must do"])
    row(["---"] * 4)
    for n in (8, 12, 16, 20, 24, 30, 40):
        food = c["food"] / n
        heat = c["heat"] / (n / PEOPLE_A_HEARTH)
        do = []
        if food < YEAR:
            do.append(f"bring in {n * YEAR - c['food']:.0f} food a year, or raise yields (plough, manure, a mill)")
        if heat < HEARTH_HEAT:
            do.append(f"find {(n / PEOPLE_A_HEARTH) * HEARTH_HEAT - c['heat']:.0f} heat a year beyond its dead wood")
        row([n, f"{food:.0f}", f"{heat:.0f}", "; ".join(do) or "keeps itself"])

    print("\n## 3. What one more hearth's fuel for a year costs, by where it comes from (units of work)\n")
    row(["Source", "Units a year", "And"])
    row(["---"] * 3)
    row(["dead wood here, gathered", f"{marginal_hearth('dead wood here'):.0f}", "renewable; children can do it"])
    row(["the near wood's trees, felled", f"{marginal_hearth('the near wood\'s trees'):.0f}", "cheapest now; the wood thins and sheds less each year"])
    for d in (1, 2, 3):
        row([f"a forest {d} day{'s' if d > 1 else ''} out, felled and carried", f"{marginal_hearth('forest', d):.0f}", "renewable for practical purposes"])
