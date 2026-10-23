"""Recipes for the first worlds: the catalogue, costed in work units. The model behind docs/cybertron2/proposals/recipes.md.

Every technique is data for one of 37.4's verbs (gather, make, build, work: proposals/verbs.md) with a card (knowledge.md §4c):
inputs, tools (needed or helping), workplace (a site or a fitting), work units, output, its trade, and whether it is basic (known
by everyone). The model computes each good's full cost in units down to the land, its weight before and after processing (where a
step belongs: Weber), its value per unit of weight (what travels: Von Thunen), output per worker-day, and the chokepoints.

Units are 38.06's work units (6 a day for an adult). Goods the decisions fix: D2-6, D2-11 to D2-18, D2-23, D2-24, D2-28.
Every number is a PROPOSAL to calibrate. Deterministic. Run: python docs/review/37_growth/02m_recipes_model.py
"""
from __future__ import annotations

DAY = 6

# weight per unit (38.06 §3 and 02g §3: a person on foot carries about 10-20)
WEIGHT = {"wild food": 1, "grain": 1, "meat": 1, "salted meat": 1, "hay": 1, "timber": 2, "stone": 3, "copper ore": 3,
          "copper": 1, "salt": 1, "hide": 1, "parchment": 0.05, "document": 0.05, "coin": 0.01, "hand tool": 1,
          "crude tool": 1, "crude weapon": 1, "blade": 1, "trap": 0.5, "harness": 2, "saddle": 3, "pack": 1, "plough": 6,
          "handcart": 15, "cart": 40, "lock": 0.5}

# gathering: (site, units, output qty with a crude tool, the tool that helps, trade, basic). Tool grades (D2-23): bare hands x0.5
# (and no quarrying or mining at all), a crude tool x1, a copper hand tool x1.5
GATHER = {
    "wild food": ("forest, scrub", 1, 1.2, None, "forager", True),          # H-6: stock-limited; a party for game
    "meat": ("forest (game)", 2, 2.0, "crude weapon", "hunter", True),      # hunt: expected catch; hide 1 in 4 (below)
    "timber": ("forest", 2, 3.0, "hand tool", "woodsman", True),            # fell; x1.5 with an axe
    "stone": ("a quarry", 2, 2.0, "hand tool", "mason", False),             # needs a hand tool (D2-23); x1.5 with metal
    "copper ore": ("a seam", 2, 2.0, "hand tool", "miner", False),          # finite seam (D4-7)
    "hay": ("pasture", 1, 3.0, "hand tool", "herder", True),                # cut in summer for winter fodder
}
# grain is from the farm model (02l): about 1.7 food a unit on the household rung; written as its unit cost here
GRAIN_UNITS = 1 / 1.7
HIDE_FROM_HUNT = 0.25                                                      # hides per hunt
TOOL_GAIN = 1.5                                                            # a helping tool's yield multiplier

# making: output -> (qty out, {input: qty}, units, tools needed, workplace, trade, basic)
MAKE = {
    "crude tool":   (1, {"timber": 1, "stone": 0.5}, 1, None, None, "anyone", True),
    "crude weapon": (1, {"timber": 1}, 1, None, None, "anyone", True),
    "trap":         (1, {"timber": 1, "hide": 0.25}, 1, None, None, "trapper", False),
    "salt":         (2, {"timber": 3}, 2, None, "a salt spring or the shore (a boiling pan)", "salter", False),
    "salted meat":  (1, {"meat": 1, "salt": 0.2}, 0.2, None, None, "anyone", True),
    "copper":       (1, {"copper ore": 3, "timber": 4}, 3, None, "a hearth with bellows", "smelter", False),
    "hand tool":    (1, {"copper": 1, "timber": 0.5}, 3, None, "a smithy (anvil, bellows, hearth)", "smith", False),
    "blade":        (1, {"copper": 2, "timber": 0.5}, 4, None, "a smithy (anvil, bellows, hearth)", "smith", False),
    "coin":         (10, {"copper": 1}, 1, None, "a smithy (anvil, bellows, hearth)", "smith", False),
    "lock":         (1, {"copper": 1}, 3, None, "a smithy (anvil, bellows, hearth)", "smith", False),
    "plough":       (1, {"timber": 4, "copper": 1}, 4, "hand tool", None, "carpenter", False),
    "harness":      (1, {"timber": 2, "hide": 1}, 2, None, None, "leatherworker", False),
    "saddle":       (1, {"timber": 1, "hide": 2}, 3, None, None, "leatherworker", False),
    "pack":         (1, {"hide": 1, "timber": 1}, 1, None, None, "leatherworker", True),
    "handcart":     (1, {"timber": 6}, 3, "hand tool", None, "carpenter", False),
    "cart":         (1, {"timber": 12, "copper": 1}, 6, "hand tool", None, "carpenter", False),
    "parchment":    (4, {"hide": 1}, 2, None, None, "parchmenter", False),
    "document":     (1, {"parchment": 1}, 1, None, None, "scribe (literate)", False),   # a page written or copied
}
# cattle (D2-6, D2-18): slaughter an ox or cow
SLAUGHTER = {"meat": 15, "hide": 2, "units": 2}


def cost(good: str) -> float:
    """Full cost in units down to the land."""
    if good == "grain":
        return GRAIN_UNITS
    if good in GATHER:
        _, units, out, tool, _, _ = GATHER[good]
        return units / out
    if good == "hide":
        # hides come with the hunt or a slaughter: priced at their share of a slaughter's work and the animal (rough: 1 unit)
        return 1.0
    q, ins, units, *_ = MAKE[good]
    return (units + sum(n * cost(g) for g, n in ins.items())) / q


def depth(good: str) -> int:
    if good not in MAKE:
        return 0
    return 1 + max(depth(g) for g in MAKE[good][1])


def table(rows, head):
    w = [max(len(str(r[i])) for r in rows + [head]) for i in range(len(head))]
    line = lambda r: "| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(r)) + " |"
    return "\n".join([line(head), "|" + "|".join("-" * (x + 2) for x in w) + "|"] + [line(r) for r in rows])


def gathering():
    rows = []
    for g, (site, units, out, tool, trade, basic) in GATHER.items():
        rows.append([g, site, units, f"{out:g}", tool or "-", f"{units / out:.2f}", f"{out / units * DAY:.0f}", trade,
                     "yes" if basic else "no"])
    rows.append(["grain", "fields (02l)", "-", "-", "hoe, plough", f"{GRAIN_UNITS:.2f}", f"{DAY / GRAIN_UNITS:.0f}", "farmer",
                 "yes (sow, reap)"])
    print("## Gathering: from the land (yields with a crude tool; bare hands x0.5, a copper hand tool x1.5)\n")
    print(table(rows, ["good", "site", "units", "yield", "tool helps", "units a unit", "a worker-day", "trade", "basic"]))


def making():
    rows = []
    for g, (q, ins, units, tool, place, trade, basic) in MAKE.items():
        inp = ", ".join(f"{n:g} {k}" for k, n in ins.items())
        rows.append([g, f"{q:g}", inp, units, tool or "-", place or "anywhere", f"{cost(g):.2f}", depth(g), trade,
                     "yes" if basic else "no"])
    print("\n## Making: recipes (make)\n")
    print(table(rows, ["good", "makes", "inputs", "units", "tool needed", "workplace", "full cost a unit", "depth", "trade",
                       "basic"]))


# building (build): blueprint -> ({material: qty}, units, needs, what it gives). Clay, fibre, iron and leather are not in the
# first worlds (D2-24), so 02i's fittings are re-costed in timber, stone, copper and hides.
BUILD = {
    "small room (wattle and timber)":  ({"timber": 8}, 6, "a lot", "a roof for 4; a speech scope"),
    "medium room (timber on stone)":   ({"timber": 15, "stone": 4}, 15, "a lot", "a roof for 10"),
    "large room, a hall (timber on stone)": ({"timber": 30, "stone": 10}, 30, "a lot; a carpenter", "a roof for 25"),
    "stone room, medium":              ({"stone": 30, "timber": 5}, 36, "a lot; a mason", "a roof for 10; x2 defence; may carry a storey (D2-3)"),
    "beds (each)":                     ({"timber": 2, "hide": 1}, 1, "a room", "a bed: housed when sleeping here"),
    "hearth":                          ({"stone": 4}, 3, "a room", "warmth in winter (burns fuel); cooking"),
    "bins":                            ({"timber": 3}, 1, "a room", "storage: about 20 food at the house rate"),
    "cellar":                          ({"stone": 8}, 8, "a ground floor; a mason", "storage at a quarter of the spoilage"),
    "benches and a table":             ({"timber": 3}, 1, "a room", "seats: the room holds its full size for a meeting"),
    "shelves":                         ({"timber": 3}, 1, "a room", "an archive: about 50 documents kept safe"),
    "lock":                            ({"lock": 1}, 1, "a room or a box", "access by key"),
    "anvil and bellows":               ({"stone": 6, "hide": 2, "timber": 1}, 4, "a hearth", "a smithy: smelting and smithing"),
    "stalls (each)":                   ({"timber": 3}, 1, "a ground-floor room", "stabling one animal"),
    "millstones":                      ({"stone": 10}, 10, "a room; a mason", "milling by hand"),
    "water wheel":                     ({"timber": 15, "copper": 1}, 12, "millstones; a river site; a carpenter", "milling at full batch"),
}


def building():
    rows = []
    for b, (mat, units, needs, gives) in BUILD.items():
        c = units + sum(n * cost(g) for g, n in mat.items())
        rows.append([b, ", ".join(f"{n:g} {g}" for g, n in mat.items()), units, f"{c:.0f}", f"{c / DAY:.1f}", needs, gives])
    print("\n## Building: rooms and fittings (build)\n")
    print(table(rows, ["blueprint", "materials", "units of work", "full cost", "worker-days", "needs", "gives"]))


TOOLS = {   # good: (uses before it wears out, x yield on the work it helps)
    "crude tool": (10, 1.0), "hand tool": (40, 1.5), "plough": (60, None), "trap": (20, None), "harness": (80, None),
    "saddle": (160, None), "pack": (60, None), "crude weapon": (3, None), "blade": (10, None),
}


def tools():
    rows = []
    for g, (uses, mult) in TOOLS.items():
        rows.append([g, uses, f"{cost(g) / uses:.2f}", f"x{mult:g}" if mult else "-"])
    print("\n## Tools: wear (uses, or days in use for harness, saddle, pack; fights for weapons)\n")
    print(table(rows, ["good", "uses", "cost a use", "yield"]))
    gain = (1.5 - 1.0) * 2 / 2 * 3 * cost("timber")      # a fell: 2 units, 3 timber; +50% timber
    print(f"\nA copper hand tool on a fell: +{gain:.2f} units of timber a use for {cost('hand tool') / 40 - cost('crude tool') / 10:.2f} "
          "more wear than a crude one: it pays wherever it is used often.")


def weight_and_travel():
    """Where a step belongs (weight lost) and what travels (value per weight)."""
    rows = []
    for g in ["grain", "wild food", "meat", "salted meat", "timber", "stone", "copper ore", "copper", "salt", "hide",
              "parchment", "document", "coin", "hand tool", "blade", "plough", "harness", "saddle", "cart"]:
        c = cost(g)
        rows.append([g, f"{WEIGHT[g]:g}", f"{c:.2f}", f"{c / WEIGHT[g]:.1f}"])
    rows.sort(key=lambda r: float(r[3]))
    print("\n## What travels: full cost per unit of weight (on foot an edge costs about 0.9 units a unit of weight, 02g §3)\n")
    print(table(rows, ["good", "weight", "full cost", "cost per weight"]))
    ore_w = 3 * WEIGHT["copper ore"] + 4 * WEIGHT["timber"]
    print(f"\nSmelting turns {ore_w:g} weight of ore and fuel into {WEIGHT['copper']:g} of copper: it belongs at the seam "
          f"(and where the wood is). Salt: 3 timber (6 weight) boiled into 2 salt (2): at the spring.")


def anchors():
    c = cost("coin")
    print("\n## Anchors (prices a world would start near, in food at about 1 unit a food)\n")
    for g in ("coin", "copper", "salt", "hand tool", "blade", "plough", "harness", "cart", "document"):
        print(f"- {g}: about {cost(g):.1f} units ({cost(g) / c:.0f} coin)")
    print(f"- a slaughtered ox: {SLAUGHTER['meat']} meat and {SLAUGHTER['hide']} hides for {SLAUGHTER['units']} units (and the animal)")


if __name__ == "__main__":
    gathering()
    making()
    building()
    tools()
    weight_and_travel()
    anchors()
