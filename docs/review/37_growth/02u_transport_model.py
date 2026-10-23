"""Do the carrying capacities make sense? The transport ladder costed against the engine as built (24 Oct), replacing 02g's model,
which was written for the old engine (4 actions a round, a round on the road using them all). Behind
docs/review/37_growth/02u_transport_check.md (analysis for Zach; OPEN C-1). Deterministic.
Run: python docs/review/37_growth/02u_transport_model.py

How travel costs in the engine now: travel is the day's last act and costs no work units; a traveller sleeps out on the road (1.5
food a night, 2 in the cold) and arrives at dawn with a full day there (D4-8). So a round trip over a 1-day road costs one day away
from home (the day at the far end, usable there) and two nights out.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------------------------------------------- engine (24 Oct)
UNITS_DAY = 6                    # an adult's units in autumn (agents/work.md)
NIGHT_EXTRA = 0.5                # food a night out beyond a night at home (1.5 against 1.0)
FELL = 1.5                       # timber a unit, crude tools
HAY = 3.0                        # hay a unit, cut in summer
# value of goods in units of work to make them (the cost of a unit of food is set by VALUE_UNIT below)
WEIGHT = {"grain": 1, "bread": 1, "dried meat": 1, "timber": 2, "charcoal": 2, "copper tool": 1, "stone": 3, "hide": 1}


def value(good: str, food_per_unit: float) -> float:
    """What a unit of the good is worth, in food, at its cost to make (D4-43: recipes' numbers)."""
    timber = 1 / FELL * food_per_unit
    return {
        "grain": 1.0,                                            # food by definition (ground)
        "bread": 1.3,
        "dried meat": 3.0,
        "timber": timber,
        "charcoal": 5 * timber + 2 * food_per_unit,              # 5 timber and 2 units
        "copper tool": (3 * 1.0 + 1 + 3 + 3) * food_per_unit + 5 * timber + 0.5 * timber,  # mine 3 ore (3 units), smelt 3, make 3
        "stone": 1.0 * food_per_unit,                            # quarry 2 a 2 units
        "hide": 2.0 * food_per_unit,                             # a by-product of hunting
    }[good]


# ---------------------------------------------------------------------------------------------------------------- rungs (OPEN C-1)
# capacity (weight), needs a track, capital in units, beasts (each eats a fodder a day where it cannot graze)
RUNGS = {
    "on foot": dict(cap=10, track=False, capital=0, beasts=0),
    "pack": dict(cap=20, track=False, capital=1 + 0.67 + 2, beasts=0),            # a hide, a timber, a unit
    "pack ox": dict(cap=60, track=False, capital=None, beasts=1),                 # an ox: its value set below
    "handcart": dict(cap=40, track=True, capital=3 + 6 / FELL, beasts=0),         # 6 timber, 3 units (carpenter)
    "ox cart": dict(cap=200, track=True, capital=None, beasts=2),                 # not built; for comparison
}
OX = {"meat": 50 * 1.5, "plough_saving": 12}    # an ox as meat (50 meat, 1.5 food each); ploughing saves 12 units a plot over the hoe


def cost_per_weight_edge(rung: str, food_per_unit: float, day_used: float = 0.0, grazing: bool = True) -> float:
    """Food per unit of weight per edge, a round trip over a 1-day road at full load out, empty back: the carrier's day away (less
    any share of it used at the far end), two nights out, fodder where the beasts cannot graze."""
    r = RUNGS[rung]
    day = UNITS_DAY * food_per_unit * (1 - day_used)
    nights = 2 * NIGHT_EXTRA
    fodder = 0 if grazing else r["beasts"] * 2 * (1 / HAY) * food_per_unit
    return (day + nights + fodder) / r["cap"]


def row(cells):
    print("| " + " | ".join(str(c) for c in cells) + " |")


if __name__ == "__main__":
    print("## 1. What it costs to carry, food per unit of weight per edge (a round trip, empty back)\n")
    row(["Rung", "Capacity", "A unit of work = 0.5 food", "= 1 food", "= 2 food", "Half the far day used (1 food a unit)"])
    row(["---"] * 6)
    for k in RUNGS:
        row([k, RUNGS[k]["cap"]] + [f"{cost_per_weight_edge(k, f):.3f}" for f in (0.5, 1.0, 2.0)] +
            [f"{cost_per_weight_edge(k, 1.0, day_used=0.5):.3f}"])

    print("\n## 2. How far a good travels before carrying it costs as much as it is worth (edges; a unit of work = 1 food)\n")
    goods = ["timber", "stone", "grain", "bread", "charcoal", "hide", "dried meat", "copper tool"]
    row(["Good", "Worth a unit of weight"] + list(RUNGS))
    row(["---"] * (2 + len(RUNGS)))
    for g in goods:
        per_w = value(g, 1.0) / WEIGHT[g]
        row([g, f"{per_w:.2f}"] + [f"{per_w / cost_per_weight_edge(k, 1.0):.1f}" for k in RUNGS])

    print("\n## 3. When a rung pays for itself (a unit of work = 1 food)\n")
    pack_cost = cost_per_weight_edge("pack", 1.0)
    for k in ("handcart", "pack ox"):
        save_per_trip = (pack_cost - cost_per_weight_edge(k, 1.0)) * RUNGS[k]["cap"]
        capital = RUNGS[k]["capital"] if RUNGS[k]["capital"] is not None else OX["meat"]
        print(f"- {k} over a pack: saves {save_per_trip:.1f} food a full trip; pays back its {capital:.0f} after "
              f"{capital / save_per_trip:.1f} trips" + (" (the ox valued as meat; it is not used up)" if k == "pack ox" else ""))
    ox_plough = OX["plough_saving"] * 16 / 2                       # a pair breaks a farm of 16 plots, per ox
    print(f"- an ox ploughing for a 16-plot farm saves about {ox_plough:.0f} units a season (half a pair's {OX['plough_saving']} a plot): "
          f"an ox lent to carrying gives that up, so a pack ox pays its way only on a route that carries more than about "
          f"{ox_plough / ((pack_cost - cost_per_weight_edge('pack ox', 1.0)) * 60):.0f} full loads in a season")

    print("\n## 4. Ratios against history (rough ranges, not precise figures)\n")
    hist = {"pack": (25, 35), "pack ox": (80, 130), "handcart": (100, 150), "ox cart": (500, 1000)}
    row(["Rung", "Game, x a pack", "History, x a person with a pack (rough)"])
    row(["---"] * 3)
    for k, (lo, hi) in hist.items():
        row([k, f"{RUNGS[k]['cap'] / RUNGS['pack']['cap']:.1f}", f"{lo / 30:.1f} to {hi / 30:.1f}"])
