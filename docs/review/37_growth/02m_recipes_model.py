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


# ---------------------------------------------------------------- 23 Oct (b): tools by method, and the worth of things

# What one hand tool (D2-23: one good, two grades) does in each method. A tool never adds to a site's stock: on a stock-limited site
# it takes the same stock faster (more per unit of work, and the site runs down sooner); on land it changes the work a plot takes.
# Multipliers are on output per unit of work (gathering) or divide the units (work on a plot). Wear: uses of tool life per use.
METHODS = {
    # method:      (bare hands, crude, copper, wear per use, draws on, why)
    "forage":      (1.0, 1.0, 1.0, 0.0, "plants (stock)", "picking by hand: no tool helps (a pack helps carry)"),
    "fell":        (0.25, 1.0, 2.0, 1.0, "forest timber (slow stock)", "metal axes cut about 2x stone ones (copper; steel ~3x)"),
    "quarry":      (0.0, 1.0, 1.5, 2.0, "a quarry (endless)", "wedges and hammers; hard on tools"),
    "mine":        (0.0, 1.0, 1.5, 2.0, "a seam (finite)", "picks; hard on tools; no tool, no mining"),
    "cut hay":     (0.3, 1.0, 1.5, 0.5, "pasture (regrows)", "a sickle or scythe"),
    "hoe":         (0.5, 1.0, 1.5, 1.0, "the plot's soil", "breaking ground by hand"),
    "reap":        (0.6, 1.0, 1.5, 0.5, "the crop", "a sickle"),
    "hunt":        (0.3, 1.0, 1.3, 0.3, "game (threshold stock)", "the weapon: crude spear 1, copper blade 1.3"),
}


def tool_methods():
    rows = [[m, f"x{b:g}", f"x{c:g}", f"x{k:g}", f"{w:g}", d, why] for m, (b, c, k, w, d, why) in METHODS.items()]
    print("\n## One hand tool, different effects by method (output per unit of work, or units divided)\n")
    print(table(rows, ["method", "bare hands", "crude", "copper", "wear a use", "draws on", "why"]))


# A household of 5 (3 working adults) in a 40-day year: how often it does each method (units a year with a crude tool)
HOUSEHOLD_UNITS = {"fell": 24, "hoe": 72, "reap": 36, "cut hay": 4, "quarry": 0, "mine": 0, "forage": 30, "hunt": 16}


def worth_of_tools():
    """Units a year a copper tool saves a household against crude ones, against what the tools cost it."""
    rows = []
    saved = uses_c = uses_k = 0.0
    for m, u in HOUSEHOLD_UNITS.items():
        b, c, k, w, *_ = METHODS[m]
        if m == "hunt":
            continue                                           # weapons are a separate good
        s = u - u * c / k                                      # units saved for the same output
        saved += s
        uses_c += u / 2 * w                                    # a use is about 2 units of work
        uses_k += u * c / k / 2 * w
        rows.append([m, u, f"{s:.0f}"])
    cost_c = uses_c / TOOLS["crude tool"][0] * cost("crude tool")
    cost_k = uses_k / TOOLS["hand tool"][0] * cost("hand tool")
    print("\n## Is a copper tool worth it to a household of 5 (40-day year)?\n")
    print(table(rows, ["method", "units a year (crude)", "saved with copper"]))
    print(f"\nSaved: {saved:.0f} units a year. Tools worn: crude {cost_c:.1f} units a year, copper {cost_k:.1f}. "
          f"Net gain from copper: {saved - (cost_k - cost_c):.0f} units a year, about {(saved - (cost_k - cost_c)) / DAY:.0f} "
          "worker-days: a household should want one, and buy it from a smith.")


# What owning a thing is worth a year against what it costs a year (capital written off over its life, plus upkeep), for a
# household and, where it differs, for a village or a specialist. Worth is in units saved or food kept (1 food = 1 unit).
WORTH = [
    # thing, cost to have, life (years), worth a year to a household, worth a year at scale, why
    ("copper hand tool", 12, 1.1, 49, 49, "worksheet above: wears about one tool a year; saves 49 units"),
    ("plough and ox", 15 + 20, 3, 6, 60, "02l: worth it above about 4-8 plots; a village shares the herd"),
    ("trap line of 6, 40 nights", 9.5, 0.5, 7, 7, "54 food for 41 units of checking, against 45 units to forage it: barely pays at full plants; pays where plants are short"),
    ("salt for 2 slaughters (6 salt)", 12, 1, 24, 24, "keeps 2 x 15 meat: about 12 of each would rot fresh"),
    ("bins", 3, 6, 1.5, 1.5, "02j: the household's best store"),
    ("cellar", 16, 15, 0.4, 5, "02j: pays only at village scale (a granary)"),
    ("beds for 5", 15, 6, 10, 10, "housed sleep: less food a night (02e)"),
    ("hearth", 7, 10, 25, 25, "winter: without it the household eats x1.5-2 and risks starving (H-5)"),
    ("lock", 13, 10, 2, 8, "worth the theft it stops: little in a household, much on a store or a treasury"),
    ("cart", 22.7, 4, 0, 60, "02g: pays only above about 16 units a day on a route: a merchant's"),
    ("stalls for 2 oxen", 6, 6, 4, 4, "winter: less fodder, dung kept for the fields, safe from rustling"),
]


def worth_table():
    rows = []
    for name, c, life, w_h, w_s, why in WORTH:
        a = c / life
        rows.append([name, f"{c:g}", f"{life:g}", f"{a:.1f}", f"{w_h:g}", f"{w_h / a:.1f}" if a else "-", f"{w_s:g}",
                     f"{w_s / a:.1f}" if a else "-", why])
    print("\n## The worth of things: a year's worth against a year's cost (units)\n")
    print(table(rows, ["thing", "cost", "life (years)", "cost a year", "worth a year, household", "ratio",
                       "worth a year, at scale", "ratio", "why"]))


if __name__ == "__main__":
    tool_methods()
    worth_of_tools()
    worth_table()
