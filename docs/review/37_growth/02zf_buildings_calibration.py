"""Are the buildings and fittings calibrated? Every scoped building and fitting priced in units of work (materials at the engine's
gathering rates plus the work), against a household's yearly surplus, rough real-world labour, and what it returns. Behind the
3 Nov conversation (analysis for Zach; nothing decided). Numbers from cybertron2/engine/data.py (built) and spec/economy/buildings.md
(specced for Package E). Deterministic. Run: python docs/review/37_growth/02zf_buildings_calibration.py

Conversions:
- a unit of work: an adult works about 6 a day, 144 a 24-day year; a plot is one adult's season (D4-40), so a unit is about 1.7
  real person-days;
- materials at crude-tool rates: timber 1.5 a unit felled (0.67 units each), stone 1 a unit quarried (1 unit each; fieldstone from
  breaking a field is a by-product), straw and hides by-products (counted at 0.2 and 0.5), copper about 8 units (mining, charcoal,
  smelting);
- carrying left out (it adds for stone, weight 3, and for timber from a wood a day away).

The real-world figures are my rough orders of magnitude, not sourced: read them as "about right" or "several times off", no finer.
"""
from __future__ import annotations

UNIT_DAYS = 1.7
COST = {"timber": 1 / 1.5, "stone": 1.0, "straw": 0.2, "hide": 0.5, "copper": 8.0}

# (name, materials, work, built?, real person-days low-high, what it gives)
ITEMS = [
    ("camp (lasts 10 nights)", {"timber": 3}, 1, "built", (2, 5), "shelter for 4"),
    ("small room, wattle", {"timber": 8}, 6, "built", (10, 40), "a cottage for 4"),
    ("small room, timber", {"timber": 8, "stone": 2}, 6, "spec", (30, 80), "a cottage for 4"),
    ("small room, stone", {"stone": 12, "timber": 3}, 10, "spec", (100, 300), "a cottage for 4"),
    ("medium room, timber", {"timber": 15, "stone": 4}, 15, "built", (60, 150), "a family house for 10"),
    ("medium room, stone", {"stone": 24, "timber": 5}, 22, "spec", (200, 500), "a family house for 10"),
    ("hall, timber", {"timber": 30, "stone": 10}, 30, "built", (500, 2000), "a hall for 25"),
    ("hall, stone", {"stone": 50, "timber": 10}, 40, "spec", (1000, 4000), "a hall for 25"),
    ("beds (one)", {"timber": 2, "straw": 2}, 1, "built", (1, 3), "one sleeps housed"),
    ("bins", {"timber": 3}, 1, "built", (2, 5), "60 food at half the spoilage"),
    ("hand mill (quern)", {"stone": 2}, 2, "built", (3, 10), "8 grain a unit ground"),
    ("fire ring", {"stone": 1}, 1, "built", (1, 2), "cooking; half-warm on a cold night"),
    ("hearth", {"stone": 4}, 3, "built", (5, 15), "warmth, cooking, baking"),
    ("oven", {"stone": 6}, 4, "built", (15, 30), "bread in batches of 40"),
    ("granary floor", {"timber": 6}, 4, "built", (15, 30), "300 grain at a fifth of the spoilage"),
    ("anvil and bellows", {"stone": 6, "hide": 2, "timber": 1}, 4, "built", (10, 30), "a smithy"),
    ("cellar (as built: 8 stone, 8 units, put in in 2)", {"stone": 8}, 8, "built", (30, 60), "food at a quarter of the spoilage"),
    ("cellar (D2-155: 4 stone, 6 units)", {"stone": 4}, 6, "spec", (30, 60), "food at a quarter of the spoilage"),
    ("dressed millstones (ox mill)", {"stone": 10}, 10, "built", (30, 100), "16 grain a unit, with an ox"),
    ("water wheel (on the millstones)", {"timber": 15, "copper": 1}, 12, "built", (300, 1500), "40 grain a unit"),
    ("stalls (one beast)", {"timber": 1}, 1, "spec", (2, 5), "fodder x0.8, dung x1.5"),
    ("woodshed", {"timber": 2}, 1, "spec", (3, 8), "40 timber kept dry"),
    ("vault (a stone room)", {"stone": 16}, 12, "spec", (100, 300), "goods that do not burn"),
]

HOUSEHOLD_SURPLUS = 140      # units a year: 2 adults x 144, less food for 4 (about 96 food at 0.6 to 0.77 a food), fuel (about 14)


def units(mats: dict, work: float) -> float:
    return sum(COST[m] * q for m, q in mats.items()) + work


def row(cells):
    print("| " + " | ".join(str(c) for c in cells) + " |")


if __name__ == "__main__":
    print("## 1. What each costs, against a household's year and real labour\n")
    row(["Building or fitting", "State", "Units (materials + work)", "Share of a household's yearly surplus",
         "Real person-days it equals", "Rough real person-days", "Engine against real"])
    row(["---"] * 7)
    for name, mats, work, state, (lo, hi), _ in ITEMS:
        u = units(mats, work)
        pd = u * UNIT_DAYS
        verdict = "about right" if lo / 2 <= pd <= hi * 1.5 else (f"{lo / pd:.0f}-{hi / pd:.0f}x cheap" if pd < lo / 2 else "dear")
        row([name, state, f"{u:.0f}", f"{u / HOUSEHOLD_SURPLUS:.0%}", f"{pd:.0f}", f"{lo}-{hi}", verdict])

    print("\n## 2. The mill ladder: who would build a mill?\n")
    grain = 96                      # grain a household of 4 eats a year if it all goes to flour (1 a person a day, 24 days)
    hand = units({"stone": 2}, 2)
    mill = units({"stone": 10}, 10) + units({"timber": 15, "copper": 1}, 12)
    row(["Way of grinding", "Grain a unit", "Units a year, one household", "Units a year, a village of 6", "Cost to build"])
    row(["---"] * 5)
    for label, rate, cost in (("hand mill", 8, hand), ("ox mill", 16, units({"stone": 10}, 10)), ("water mill", 40, mill)):
        row([label, rate, f"{grain / rate:.1f}", f"{6 * grain / rate:.0f}", f"{cost:.0f}"])
    save = 6 * grain / 8 - 6 * grain / 40
    print(f"\nA water mill saves a village of 6 households about {save:.0f} units a year over hand mills, so at {mill:.0f} units it"
          f" pays back in {mill / save:.1f} years, and one household could build it from about {mill / HOUSEHOLD_SURPLUS:.0%} of a"
          " year's surplus. But a household saves only"
          f" {grain / 8 - grain / 40:.0f} units a year by not grinding by hand, against a hand mill that costs {hand:.0f}: nobody needs"
          " the mill, so it is no chokepoint (38.22). And bread is made from any flour in the engine, while recipes.md §16 says mill"
          " flour.")
    for rate in (4, 3, 2):
        h = grain / rate
        print(f"- With a hand mill at {rate} grain a unit, a household grinds for {h:.0f} units a year ({h / 144:.0%} of an adult's"
              f" year); a water mill saves a village of 6 {6 * (h - grain / 40):.0f} a year.")

    print("\n## 3. Wear: every structure breaks at the same rate\n")
    p, cold = 0.02, 0.08
    for label, cold_nights in (("a 24-day year, 6 cold nights", 6), ("a 32-day year, 8 cold nights", 8)):
        days = 24 if cold_nights == 6 else 32
        breaks = (days - cold_nights) * p + cold_nights * cold
        print(f"- {label}: about {breaks:.2f} breaks a year for any building (2 breaks from sound to ruin, about"
              f" {2 / breaks:.1f} years unheld); repair is 2 timber and 2 units a break, whatever the building:"
              f" about {breaks * units({'timber': 2}, 2):.1f} units a year for a cottage or a hall alike.")
