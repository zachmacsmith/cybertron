"""From roots to end uses: every path costed in actions. The model behind docs/review/37_growth/02j_end_uses.md.

Three layers:
    ROOTS      what is taken from the land, with the actions one unit costs (a journeyman with basic tools)
    RECIPES    processing steps: inputs, actions, and the building or skill they need; a good's full cost is the sum of its
               inputs' full costs and the step's actions (computed recursively)
    LADDERS    for each end use (a service people need), the alternative rungs that provide it, each costed per unit of
               service, with the roots it needs, the depth of its chain and its capital; the gain each rung brings over the one
               below, and where a rung needs a root the rung below did not (a qualitative jump)

All numbers are PROPOSALS (rough, historically plausible orders of magnitude), to be calibrated in dry runs; nothing here is from the
old engine except where marked ENGINE. Value of output is priced at its own full cost (an extra grain is worth the actions it would
otherwise take). Deterministic. Run: python docs/review/37_growth/02j_end_uses_model.py
"""
from __future__ import annotations

FOOD_VALUE = 0.5            # actions a ration is worth in an organised economy (02b: 0.4-0.8)
HORIZON = 40                # rounds over which capital is written off
WINTER = 0.25               # share of rounds that are cold

# roots: actions per unit, where found, how it comes back
ROOTS = {
    "wild food": (1.00, "forest, scrub", "fast; game has a threshold"),
    "grain": (0.77, "fields", "yearly"),
    "timber": (0.33, "woods", "slow"),                 # ENGINE fell_timber 3 a fell
    "stone": (0.50, "a quarry", "endless, heavy"),
    "clay": (0.25, "a riverbank", "endless, heavy"),
    "copper ore": (0.33, "a seam in the hills", "finite"),
    "tin ore": (1.00, "one far place", "finite, rare"),
    "iron ore": (0.50, "bogs and hills", "finite, common"),
    "salt": (0.33, "a spring", "endless, one place"),
    "fibre": (0.50, "flax fields", "yearly"),
    "hide": (1.00, "slaughter or the hunt", "a by-product"),
}

# recipes: output -> (inputs {good: qty}, actions, needs)
RECIPES = {
    "charcoal": ({"timber": 5}, 1.0, "a charcoal clamp"),
    "copper": ({"copper ore": 2, "charcoal": 1}, 0.5, "hearth and bellows"),
    "tin": ({"tin ore": 2, "charcoal": 1}, 0.5, "hearth and bellows"),
    "bronze": ({"copper": 0.9, "tin": 0.1, "charcoal": 0.5}, 0.5, "hearth and bellows"),
    "iron": ({"iron ore": 3, "charcoal": 6}, 3.0, "a bloomery; a high skill"),
    "crude tool": ({"timber": 2}, 1.0, "nothing"),
    "copper tool": ({"copper": 1, "timber": 0.5}, 1.0, "a smithy"),
    "bronze tool": ({"bronze": 1, "timber": 0.5}, 1.0, "a smithy"),
    "iron tool": ({"iron": 1, "timber": 0.5}, 1.5, "a smithy; skill"),
    "parchment page": ({"hide": 0.25}, 0.25, "nothing"),
    "paper page": ({"fibre": 0.25}, 0.05, "a paper mill"),
    "pottery jar": ({"clay": 4, "timber": 2}, 1.0, "a kiln"),
    "salted meat": ({"salt": 0.2}, 0.1, "nothing (per unit of meat)"),
    # tools added 23 Oct (Zach: traps, harness and saddle in; armour, nets, boats and the seed drill as later options)
    "trap": ({"timber": 1, "hide": 0.25}, 1.0, "nothing (a snare or deadfall; cord from hide strips)"),
    "harness": ({"timber": 2, "hide": 1}, 2.0, "nothing (a yoke and straps: an ox pulls a plough or a cart)"),
    "saddle": ({"timber": 1, "hide": 2}, 3.0, "a leatherworker's skill (a horse carries a rider)"),
    "hide armour": ({"hide": 4}, 3.0, "a leatherworker's skill"),
    "net": ({"fibre": 4}, 3.0, "fibre (flax): later"),
    "boat": ({"timber": 15, "hide": 1}, 10.0, "a boatwright; a river or coast"),
}


def cost(good, seen=()) -> float:
    if good in ROOTS:
        return ROOTS[good][0]
    ins, acts, _ = RECIPES[good]
    return acts + sum(q * cost(g) for g, q in ins.items())


def depth(good) -> int:
    if good in ROOTS:
        return 0
    return 1 + max(depth(g) for g in RECIPES[good][0])


def roots_of(good) -> set:
    if good in ROOTS:
        return {good}
    out = set()
    for g in RECIPES[good][0]:
        out |= roots_of(g)
    return out


def table(rows, head):
    w = [max(len(str(r[i])) for r in rows + [head]) for i in range(len(head))]
    line = lambda r: "| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(r)) + " |"
    return "\n".join([line(head), "|" + "|".join("-" * (x + 2) for x in w) + "|"] + [line(r) for r in rows])


def tools():
    """Tools on a field: bare hands x0.5 of a journeyman's yield (02d); each tool multiplies it and wears out."""
    base = 1.3                                                      # grain per farm action, journeyman, basic tools
    rungs = [("bare hands", None, 0.5, None), ("crude tool (wood, stone)", "crude tool", 0.8, 10),
             ("copper tool", "copper tool", 1.0, 20), ("bronze tool", "bronze tool", 1.25, 40),
             ("iron tool", "iron tool", 1.5, 100)]
    rows, prev = [], None
    for name, good, mult, uses in rungs:
        if good is None:
            rows.append([name, "-", "-", "-", f"{mult:g}", "-", "-", "-", "-"])
            prev = set()
            continue
        c = cost(good)
        per_use = c / uses
        gain = base * (mult - 0.5) * ROOTS["grain"][0]               # the extra grain a use brings, priced at its cost
        r = roots_of(good)
        jump = ", ".join(sorted(r - prev)) if prev is not None and r - prev else ""
        rows.append([name, f"{c:.1f}", depth(good), uses, f"{mult:g}", f"{per_use:.3f}", f"{gain:.2f}", f"{gain / per_use:.1f}x",
                     jump])
        prev = prev | r if prev is not None else r
    print("## Tools: what one tool costs, and what each use of it returns on a field\n")
    print(table(rows, ["rung", "actions to make", "chain depth", "uses", "yield x", "cost per use", "gain per use",
                       "return", "new roots needed"]))


def shelter():
    """A person-night in shelter, against sleeping out (02e: food x1.5, x2 in the cold, and a 30% chance of starving)."""
    value = ((1 - WINTER) * 0.5 + WINTER * 1.0) * FOOD_VALUE + WINTER * 0.3 * 2.0   # food saved, plus starving's lost actions
    t, s, cl = ROOTS["timber"][0], ROOTS["stone"][0], ROOTS["clay"][0]
    hearth = 4 * s + 2 * cl + 2
    fuel = ((1 - WINTER) * 0.5 + WINTER * 2.0) * t                      # a hearth's timber a round
    rungs = [
        ("a lean-to", 3 * t + 1, 0.0, 0.10, 2, 0.6, "timber"),         # a roof only: half the benefit
        ("wattle hut with a hearth", 8 * t + 4 + hearth, fuel, 0.02, 4, 1.0, "timber, stone, clay"),
        ("timber frame on stone, hearth", 15 * t + 4 * s + 8 + hearth, fuel, 0.01, 10, 1.0, "timber, stone, clay"),
        ("stone house, hearth", 30 * s + 5 * t + 16 + hearth, fuel, 0.005, 10, 1.0, "stone (and a mason)"),
    ]
    rows = []
    for name, build, fuel_r, brk, people, share, needs in rungs:
        per_round = build / HORIZON + brk * 0.25 * build + fuel_r
        per_person = per_round / people
        rows.append([name, f"{build:.0f}", people, f"{per_person:.3f}", f"{value * share:.2f}", f"{value * share / per_person:.0f}x", needs])
    print("\n## Shelter: a person-night under a roof, against sleeping out\n")
    print(table(rows, ["rung", "actions to build", "people", "cost a person-night", "worth a person-night", "return", "needs"]))


def storage():
    """Keeping food through a 6-round winter, for a household (20 food) and a village store (120 food). Capital is shared by
    capacity: bins hold 20, a jar 10, a cellar 40; each is written off over 6 winters."""
    rounds, winters = 6, 6
    t, s, = ROOTS["timber"][0], ROOTS["stone"][0]
    rungs = [("grain carried (15% a round)", 0.15, None, 0.0, "nothing"),
             ("grain in the house stock (5%)", 0.05, None, 0.0, "a house"),
             ("grain in bins (2.5%)", 0.025, 20, 3 * t + 1, "timber"),
             ("grain in pottery jars (2%)", 0.02, 10, cost("pottery jar"), "clay, a kiln"),
             ("grain in a cellar (1.25%)", 0.0125, 40, 8 * s + 6, "stone"),
             ("fresh meat (25%)", 0.25, None, 0.0, "nothing"),
             ("salted meat (2%)", 0.02, None, None, "salt")]
    rows = []
    for name, rate, cap, capital, needs in rungs:
        row = [name]
        for keep in (20.0, 120.0):
            lost = keep * (1 - (1 - rate) ** rounds)
            if capital is None:                                         # salting: a cost per unit kept, every time
                c = keep * cost("salted meat")
            elif cap:
                c = -(-keep // cap) * capital / winters
            else:
                c = 0.0
            row += [f"{lost:.1f}", f"{lost * FOOD_VALUE + c:.1f}"]
        row.append(needs)
        rows.append(row)
    print("\n## Storage: keeping food through a 6-round winter (loss, and loss plus the storage's cost, in actions)\n")
    print(table(rows, ["rung", "20 food: lost", "20: total cost", "120 food: lost", "120: total cost", "needs"]))


def writing():
    """A page written, and a page copied; parchment against paper against a press."""
    rows = []
    for name, sheet, copy_act, needs in [("parchment, copied by hand", cost("parchment page"), 1.0, "hides"),
                                         ("paper, copied by hand", cost("paper page") + 0.03, 1.0, "fibre, a paper mill"),
                                         ("paper, printed", cost("paper page") + 0.03, 0.05, "fibre, a paper mill, a press (later)")]:
        rows.append([name, f"{sheet:.2f}", f"{1.0 + sheet:.2f}", f"{copy_act + sheet:.2f}", needs])
    print("\n## Writing: the cost of a page (actions)\n")
    print(table(rows, ["rung", "a sheet", "an original page (write it)", "a copy", "needs"]))


def burdens():
    """What the new tools cost to make, over their life, against what they serve (proposals, 23 Oct)."""
    g = ROOTS["wild food"][0]                       # a food's worth, at the cost of foraging it
    rows = []
    # trap: a line of n traps checked once a day at the site (1 unit a visit + 0.1 a trap); each catches with chance p x the
    # game's share of its capacity, about 1.5 food; a trap lasts about 20 nights
    for n, game in ((1, 1.0), (6, 1.0), (6, 0.5), (6, 0.2)):
        food = n * 0.3 * game * 1.5
        units = 1.0 + 0.1 * n + n * cost("trap") / 20
        rows.append([f"trapline of {n}, game at {game:.0%} of capacity", f"{n * cost('trap'):.1f}", "20 nights",
                     f"{units:.2f} a day", f"{food:.2f} food a day", f"{food / units:.2f} food a unit"])
    print("\n## Traps: a trapline, checked once a day (forage gives about 1 food a unit; hunting about the same, with a party)\n")
    print(table(rows, ["case", "units to make", "life", "work", "catch", "return"]))
    rows = []
    year = 40
    for name, good, life, serves, upkeep in (
            ("harness (ox)", "harness", 2, "an ox", 0.1 * year + 20 / 5 + 1.0 * year),
            ("saddle (horse)", "saddle", 4, "a horse: grain 1 a working day, herding", 0.8 * year * 0.77 + 1.0 * year),
            ("hide armour", "hide armour", 3, "a fighter", 0.0)):
        c = cost(good)
        rows.append([name, f"{c:.1f}", f"{life} years", f"{c / life:.1f}", serves, f"{upkeep:.0f}" if upkeep else "-"])
    print("\n## Equipment: cost to make, a year, and the yearly upkeep of what it serves (a 40-day year, one animal kept alone)\n")
    print(table(rows, ["good", "units to make", "life", "units a year", "serves", "upkeep of what it serves, a year"]))


def goods():
    rows = [[g, f"{cost(g):.2f}", depth(g), ", ".join(sorted(roots_of(g))), RECIPES[g][2]] for g in RECIPES]
    print("\n## Every processed good: full cost, chain depth, roots\n")
    print(table(rows, ["good", "actions", "depth", "roots", "needs"]))


if __name__ == "__main__":
    tools()
    shelter()
    storage()
    writing()
    burdens()
    goods()
