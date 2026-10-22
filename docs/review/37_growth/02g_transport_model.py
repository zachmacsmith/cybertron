"""The transport ladder in actions: the model behind docs/review/37_growth/02g_resources_and_transport.md §4.

Moving goods along an edge costs the carriers' time (an agent on the road spends its whole round there: 4 actions), their food on
the road, the draught animals' fodder, and the capital (the cart, the animals, the boat) written off over a horizon, plus upkeep.
Every rung is costed per unit carried per edge at full load, for a round trip (the carrier comes back), and by the volume a route
must carry each round to keep it busy. All numbers are PROPOSALS to calibrate; deterministic. Run:
python docs/review/37_growth/02g_transport_model.py
"""
from __future__ import annotations

ACTIONS = 4                 # actions in an agent's round (a round on the road uses them all)
FOOD = 0.4                  # actions per ration in an organised economy (02b §4.2)
ROAD_RATION = 1.5           # rations a night on the road without shelter (02e); camping gear: 1.0
HORIZON = 40                # rounds over which capital is written off
FODDER = 0.3                # actions per fodder unit (grazing on the way is free where there is pasture)

# capacity (units of goods), edges a round, crew, animals (each eats 1 fodder a round), capital (actions), upkeep (actions a round),
# what the route needs
RUNGS = [
    ("on foot", 10, 1.0, 1, 0, 0, 0.0, "nothing"),
    ("pack (basket or leather)", 20, 1.0, 1, 0, 3, 0.02, "nothing"),
    ("pack ox, led", 60, 1.0, 1, 1, 30, 0.05, "pasture or fodder"),
    ("handcart", 40, 1.0, 1, 0, 12, 0.05, "a track"),
    ("ox cart (2 oxen)", 200, 1.0, 1, 2, 80, 0.2, "a track"),
    ("wagon (4 horses), on a road", 500, 2.0, 2, 4, 220, 0.6, "a road"),
    ("river boat (crew 2)", 1500, 3.0, 2, 0, 150, 0.5, "a river (downstream; upstream 1 edge a round)"),
    ("railway train", 20000, 8.0, 4, 0, 6000, 25.0, "a railway"),
]


def per_unit_edge(cap, speed, crew, animals, capital, upkeep):
    """Actions per unit per edge, full load, round trip (empty back)."""
    rounds = 2.0 / speed                                         # there and back, per edge
    crew_cost = crew * rounds * (ACTIONS + ROAD_RATION * FOOD)
    beasts = animals * rounds * FODDER
    cap_cost = rounds * (capital / HORIZON + upkeep)
    return (crew_cost + beasts + cap_cost) / cap


def fixed_per_round(capital, upkeep):
    return capital / HORIZON + upkeep


def main():
    print("| Rung | Capacity | Edges a round | Needs | Actions per unit per edge | vs on foot | Capital (actions) |")
    print("|---|---|---|---|---|---|---|")
    foot = per_unit_edge(*RUNGS[0][1:7])
    rows = []
    for name, cap, speed, crew, animals, capital, upkeep, needs in RUNGS:
        c = per_unit_edge(cap, speed, crew, animals, capital, upkeep)
        rows.append((name, c, capital, upkeep))
        print(f"| {name} | {cap} | {speed:g} | {needs} | {c:.4f} | {foot / c:.0f}x cheaper | {capital} |")
    print("\n## What a unit of grain costs to move, against what it cost to grow (0.3-0.5 actions a unit, 02b)\n")
    for name, c, _, _ in rows[:6]:
        print(f"- {name}: one edge {c:.3f}, three edges {3 * c:.3f}")
    print("\n## Break-even volume: units a round a route must carry before a rung beats the one below it\n")
    pairs = [(1, 0), (2, 1), (4, 2), (5, 4), (6, 4)]
    for hi, lo in pairs:
        n_hi, cap_hi, sp_hi, cr_hi, an_hi, k_hi, u_hi, _ = RUNGS[hi]
        n_lo, cap_lo, sp_lo, cr_lo, an_lo, k_lo, u_lo, _ = RUNGS[lo]
        var_hi = (cr_hi * (2 / sp_hi) * (ACTIONS + ROAD_RATION * FOOD) + an_hi * (2 / sp_hi) * FODDER) / cap_hi
        var_lo = (cr_lo * (2 / sp_lo) * (ACTIONS + ROAD_RATION * FOOD) + an_lo * (2 / sp_lo) * FODDER + (2 / sp_lo) * fixed_per_round(k_lo, u_lo)) / cap_lo
        fixed = fixed_per_round(k_hi, u_hi)
        v = fixed / (var_lo - var_hi) if var_lo > var_hi else float("inf")
        print(f"- {n_hi} over {n_lo}: from about {v:.0f} units a round on the route")


if __name__ == "__main__":
    main()
