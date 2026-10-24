"""Do the costs of buildings and fittings make sense? Houses and fittings costed against what they save, with the engine's numbers
as of 24 Oct (cybertron2/engine/data.py, night.py). Behind the housing section of the conversation of 24 Oct (analysis for Zach;
nothing decided). A unit of work is worth about 1 food (02p); timber 1/1.5 units to fell, stone 1 unit to quarry, straw nearly free
(a by-product of the harvest), copper about 11 (ore, charcoal, smelting). Deterministic.
Run: python docs/review/37_growth/02x_housing_model.py
"""
from __future__ import annotations

VAL = {"timber": 1 / 1.5, "stone": 1.0, "straw": 0.1, "hide": 2.0, "copper": 11.0}
# night costs (food a person a night): housed 1.0; damaged 1.2 (cold 1.5); unsheltered 1.5 (cold 2.0, and a 0.3 chance of waking
# starving, valued here at 1 food); a camp 1.2 (cold 1.5); a house's fire 0.5 timber a night (2 cold); a camp's 1 timber
NIGHT = {"housed": (1.0, 1.0), "out": (1.5, 2.0 + 0.3 * 1.0), "camp": (1.2, 1.5)}
FIRE = {"house": (0.5, 2.0), "camp": (1.0, 1.0)}
BREAK = (0.02, 0.08)                    # a building's chance a night of a break (normal, cold)
REPAIR = 2 * VAL["timber"] + 2          # 2 timber, 2 units
COLD_SHARE = 6 / 24                     # a quarter of nights are cold (one winter in 24 days)

BLUEPRINTS = {"small room": ({"timber": 8}, 6, 4), "medium room": ({"timber": 15, "stone": 4}, 15, 10),
              "hall": ({"timber": 30, "stone": 10}, 30, 25), "camp": ({"timber": 3}, 1, 4)}
FITTINGS = {"beds": ({"timber": 2, "straw": 2}, 1), "hearth": ({"stone": 4}, 3), "bins": ({"timber": 3}, 1),
            "hand mill": ({"stone": 2}, 2), "granary": ({"timber": 6}, 4), "fire ring": ({"stone": 1}, 1),
            "oven": ({"stone": 6}, 4), "cellar": ({"stone": 8}, 8), "millstones": ({"stone": 10}, 10),
            "water wheel": ({"timber": 15, "copper": 1}, 12)}


def cost(materials: dict, units: float) -> float:
    return sum(VAL[m] * q for m, q in materials.items()) + units


def fitting(name: str, n: int = 1, built: bool = False) -> float:
    """A fitting's cost; built=True charges what the engine charges now (one 2-unit build action), not its listed work."""
    mats, units = FITTINGS[name]
    return n * cost(mats, 0) + (2 if built else n * units)


def house(room: str, people: int, fire: str, built: bool = False) -> float:
    mats, units, _ = BLUEPRINTS[room]
    return cost(mats, units) + fitting("beds", people, built) + fitting(fire, 1, built) + fitting("bins", 1, built)


def per_night(kind: str, people: int) -> float:
    """Food a night for the household, averaged over normal and cold nights, fire and breaks included."""
    n = NIGHT[kind]
    food = people * ((1 - COLD_SHARE) * n[0] + COLD_SHARE * n[1])
    if kind == "housed":
        fire = (1 - COLD_SHARE) * FIRE["house"][0] + COLD_SHARE * FIRE["house"][1]
        brk = ((1 - COLD_SHARE) * BREAK[0] + COLD_SHARE * BREAK[1]) * (REPAIR + people * 0.2)
        return food + fire * VAL["timber"] + brk
    if kind == "camp":
        camps = -(-people // 4)                                                   # a camp sleeps 4, lasts 10 nights
        return food + camps * (FIRE["camp"][0] * VAL["timber"] + cost({"timber": 3}, 1) / 10)
    return food


def row(cells):
    print("| " + " | ".join(str(c) for c in cells) + " |")


if __name__ == "__main__":
    print("## 1. What a house costs, and how fast it pays for itself\n")
    row(["House", "People", "Cost (listed work)", "Cost (as the engine charges now)", "A night housed", "A night in camps",
         "A night out", "Pays back against sleeping out (nights)", "against camps (nights)"])
    row(["---"] * 9)
    for label, room, ppl, fire in [("small room, fire ring", "small room", 4, "fire ring"), ("small room, hearth", "small room", 4, "hearth"),
                                   ("medium room, hearth", "medium room", 10, "hearth"), ("hall, hearth", "hall", 25, "hearth")]:
        c, cb = house(room, ppl, fire), house(room, ppl, fire, built=True)
        h, cp, out = per_night("housed", ppl), per_night("camp", ppl), per_night("out", ppl)
        row([label, ppl, f"{c:.0f}", f"{cb:.0f}", f"{h:.1f}", f"{cp:.1f}", f"{out:.1f}", f"{c / (out - h):.0f}", f"{c / (cp - h):.0f}"])
    beds = fitting("beds", 4)
    room = cost(*BLUEPRINTS["small room"][:2])
    print(f"\nIn a small house for 4, the beds cost {beds:.1f} against the room's {room:.1f}: the beds are {beds / room:.0%} of the room.")

    print("\n## 2. What each fitting saves, and when it pays back\n")
    row(["Fitting", "Cost (listed work)", "Saves", "Pays back"])
    row(["---"] * 4)
    spoil = 0.0167 * 0.3                      # grain a day in a house (D2-58)
    for f, keep, stock in [("bins", 0.5, 50), ("granary", 0.2, 150), ("cellar", 0.25, 100)]:
        save = spoil * (1 - keep) * stock
        row([f, f"{fitting(f):.0f}", f"{save:.2f} grain a day on {stock} stored", f"{fitting(f) / save:.0f} days"])
    row(["hand mill", f"{fitting('hand mill'):.0f}", "0.3 food a grain over eating it whole, less 1/8 unit", f"{fitting('hand mill') / (0.3 - 1 / 8):.0f} grain"])
    row(["millstones (ox mill)", f"{fitting('millstones'):.0f}", "1/8 - 1/16 unit a grain over a hand mill", f"{fitting('millstones') / (1 / 8 - 1 / 16):.0f} grain"])
    ww = fitting("millstones") + fitting("water wheel")
    row(["water wheel with millstones", f"{ww:.0f}", "1/8 - 1/40 unit a grain over a hand mill", f"{ww / (1 / 8 - 1 / 40):.0f} grain"])
    oven_save = (4 * VAL["timber"] + 4) - (2 * VAL["timber"] + 2)
    row(["oven", f"{fitting('oven'):.0f}", f"{oven_save:.1f} a batch of 40 bread over a hearth's four of 10", f"{fitting('oven') / oven_save * 40:.0f} bread"])
    row(["hearth against a fire ring", f"{fitting('hearth'):.0f} against {fitting('fire ring'):.0f}", "nothing for warmth or cooking (the engine treats both as a fire); a hearth only adds baking and smithing", ""])
    print("\nA region of about 45 eats about 1,100 grain in 24 days.")
