"""The next region world, checked with transport: what each village must bring in over its roads, in the days it has, by the
people free to carry it. The model behind docs/review/37_growth/02t_region_design.md (design for Zach and 37.4; nothing here is
decided). It is the check review 38.23 lacked: there, wood was enough in total and out of reach in practice.

Engine numbers are copied from cybertron2/engine/data.py (PHYSICS, ITEMS, TECHNIQUES) as of 24 Oct and marked ENGINE; the world's
numbers are this design's and marked WORLD. A day is a round (D4-13); work units by season (agents/work.md). Deterministic.
Run: python docs/review/37_growth/02t_region_model.py
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------------------------------------------------------- ENGINE
RATION = 1.0                                         # food a person a night
FOOD = {"grain": 1.0, "flour": 1.0, "bread": 1.3, "dried meat": 3.0, "beans": 0.6, "wild": 1.0, "milk": 0.5}
#   grain counted ground (1.0): every village here has a hand mill or the mill; whole grain at a hearth is only 0.7 (D2-60)
WEIGHT = {"grain": 1, "timber": 2, "charcoal": 2, "bread": 1, "copper tool": 1}
CARRY = {"foot": 10, "pack": 20, "handcart": 40}     # weight; a handcart only on a road with a track
FUEL = {"normal": 0.5, "cold": 2.0}                  # timber a hearth a night (D4-49)
NIGHT_OUT = {"normal": 1.5, "cold": 2.0}             # food a night on the road, no gear (D4-12)
UNITS = {"summer": 7, "autumn": 6, "winter": 5, "spring": 6}
YOUTH_UNITS = 4
FELL = {"crude": 1.5, "copper": 3.0}                 # timber a unit of work (fell: 3 for 2 units, copper x2)
REAP_UNITS, PLOUGH_UNITS, SOW_UNITS = 8, 4, 16 / 6   # a plot: reaping with a tool; ox plough; sowing 16 seed at 6 a unit
HAND_MILL, WATER_MILL = 8, 40                        # grain ground a unit
PLOT_SEED = 16
CHARCOAL = 5                                         # timber a charcoal (2 units)
SMELT = {"ore": 3, "charcoal": 1}                    # a copper: 3 ore and 1 charcoal (or 4 timber), 3 units
LIFE = {"crude": 10, "copper": 40}                   # a tool's life in wear
WEAR = {"fell": 1.0, "reap": 0.25, "hoe": 0.5, "mine": 2.0}   # wear a use (fell: 2 units, 3 timber; reap, hoe: 1 unit; mine: 2 units)
HOE_UNITS = 16                                       # a plot broken by hoe

# ---------------------------------------------------------------------------------------------------------------- calendar
DAYS = 24
START = ("summer", 4)                                # WORLD: the harvest under way at day 0
SEASON_DAYS = 6
SEASONS = ("spring", "summer", "autumn", "winter")


def season(day: int) -> str:
    k = SEASONS.index(START[0]) * SEASON_DAYS + START[1] - 1 + day
    return SEASONS[(k // SEASON_DAYS) % 4]


COLD = [d for d in range(DAYS) if season(d) == "winter"]
FIRST_COLD = COLD[0]
HEARTH_FUEL = sum(FUEL["cold" if season(d) == "winter" else "normal"] for d in range(DAYS))

# ---------------------------------------------------------------------------------------------------------------- WORLD
# people: (adults, youths, children); stores in goods; wild: food a day the land gives back at a sustainable take (forage and game);
# crop: grain standing at day 0 (all reaped in the window); plots: fields; sow: plots sown in spring within the run (seed held back);
# wood: timber that can be felled there over the run without stripping it; herds: (owner, head, in milk)
VILLAGES = {
    "Barleyfield": dict(kind="farms", people={"Reed": (3, 1, 1), "Barrow": (3, 0, 1), "Hale": (2, 1, 1), "Lowe": (2, 1, 0)},
                        hearths=4, stores={"grain": 150, "beans": 20}, crop=760, plots=16, sow=10, wild=0.5, wood=12, woodpile=24,
                        herds=[("Reed", 10, 3), ("Barrow", 5, 1)], tools="crude", mill="hand",
                        kit={"crude": 7, "copper": 0}, hoe_plots=4),
    "Ashwood": dict(kind="wood", people={"Fenn": (3, 1, 1), "Ash": (3, 0, 1)}, hearths=2,
                    stores={"grain": 25, "dried meat": 10}, crop=0, plots=0, sow=0, wild=2.4, wood=400, woodpile=20,
                    herds=[], tools="crude", mill="hand", kit={"crude": 4, "copper": 0}, hoe_plots=0),
    "Coppergate": dict(kind="ore", people={"Moor": (3, 1, 1), "Cole": (2, 0, 1)}, hearths=2,
                       stores={"grain": 120, "dried meat": 12}, crop=0, plots=0, sow=0, wild=0.4, wood=20, woodpile=10,
                       herds=[], tools="copper", mill="hand", smelt=6, kit={"crude": 3, "copper": 2}, hoe_plots=0),
    "Millford": dict(kind="market", people={"Miller": (2, 1, 1), "Merchant": (3, 0, 1), "Bell": (2, 1, 0), "Smith": (2, 0, 1)},
                     hearths=4, stores={"grain": 60, "flour": 16, "bread": 50, "dried meat": 4}, crop=170, plots=5, sow=3,
                     wild=0.3, wood=10, woodpile=20, herds=[], tools="crude", mill="water", handcarts=2,
                     kit={"crude": 5, "copper": 1}, hoe_plots=3),
}
# roads: (a, b, days, track, landmarks)
ROADS = [
    ("Barleyfield", "Millford", 1, True, "a ford on stretch 1"),
    ("Millford", "Ashwood", 1, True, ""),
    ("Barleyfield", "Ashwood", 1, False, "the Holloway, a narrows in the wood; wild apples (a good place)"),
    ("Ashwood", "Coppergate", 2, False, "a ford on stretch 1"),
    ("Coppergate", "Millford", 2, False, "the Pass on stretch 1 (snowed in deep winter)"),
]


def road(a: str, b: str):
    for r in ROADS:
        if {r[0], r[1]} == {a, b}:
            return r
    return None


# ---------------------------------------------------------------------------------------------------------------- budgets
def headcount(v):
    a = sum(x[0] for x in v["people"].values())
    y = sum(x[1] for x in v["people"].values())
    c = sum(x[2] for x in v["people"].values())
    return a, y, c


def units_total(v) -> float:
    a, y, _ = headcount(v)
    return sum(a * UNITS[season(d)] + y * YOUTH_UNITS for d in range(DAYS))


def food_supply(v) -> float:
    s = sum(FOOD.get(i, 0) * q for i, q in v["stores"].items())
    s += v["crop"] - v["sow"] * PLOT_SEED                   # seed for the spring sowing is held back
    s += v["wild"] * DAYS
    s += sum(m * 1.6 * FOOD["milk"] for _, _, m in v["herds"]) * DAYS
    return s


def food_demand(v) -> float:
    return sum(headcount(v)) * DAYS * RATION


def fuel_demand(v) -> float:
    """Timber for the hearths over the run (smelting's charcoal is counted apart: charcoal_demand)."""
    return v["hearths"] * HEARTH_FUEL


def charcoal_demand(v) -> float:
    return v.get("smelt", 0) * SMELT["charcoal"]


def fuel_by_cold(v) -> float:
    """Timber that must be at the village by the end of the winter: the hearths' nights to the last cold night."""
    return v["hearths"] * sum(FUEL["cold" if season(d) == "winter" else "normal"] for d in range(COLD[-1] + 1))


def food_labour(v) -> float:
    """Units of work on food: reaping, ploughing and sowing in spring, grinding, foraging and hunting what the land gives, herding."""
    u = v["plots"] * REAP_UNITS + v["sow"] * (PLOUGH_UNITS + SOW_UNITS)
    u += food_demand(v) * 0.6 / (HAND_MILL if v["mill"] == "hand" else WATER_MILL)   # about 60% of what is eaten is grain
    u += v["wild"] * DAYS                                                          # about 1 food a unit, forage and hunting
    u += len(v["herds"]) * DAYS * 1.0                                              # a herder's unit a day, unfenced
    return u


# ---------------------------------------------------------------------------------------------------------------- carrying
def trip(a: str, b: str, mode: str, cold: bool = False):
    """(days away from home for a round trip, nights out, weight carried each way). Travel is the day's last act (D4-8): a road of
    n days is n nights out each way; the days between are on the road; the day at the far end is spent there."""
    r = road(a, b)
    if r is None or (mode == "handcart" and not r[3]):
        return None
    n = r[2]
    away = 2 * (n - 1) + 1
    nights = 2 * n
    return away, nights, CARRY[mode]


def route(src: str, dst: str):
    """The best route: direct, or through Millford; returns legs."""
    d = road(src, dst)
    options = []
    if d:
        options.append([(src, dst)])
    if src != "Millford" and dst != "Millford" and road(src, "Millford") and road("Millford", dst):
        options.append([(src, "Millford"), ("Millford", dst)])
    return options


def plan(src: str, dst: str, good: str, qty: float, mode: str):
    """Trips needed to move qty of good from src to dst by one mode over the best route that allows it; the carrier's days and food."""
    best = None
    for legs in route(src, dst):
        ts = [trip(a, b, mode) for a, b in legs]
        if any(t is None for t in ts):
            continue
        days_one_way = sum(road(a, b)[2] for a, b in legs)
        away = 2 * days_one_way - 1 if len(legs) == 1 else 2 * days_one_way
        nights = 2 * days_one_way
        per = CARRY[mode] / WEIGHT[good]
        n = math.ceil(qty / per)
        food = n * nights * (NIGHT_OUT["normal"] - RATION)   # what a night out costs beyond a night at home
        c = (n, away, nights, per, food, " via Millford" if len(legs) == 2 else "")
        if best is None or n * away < best[0] * best[1]:
            best = c
    return best


# ---------------------------------------------------------------------------------------------------------------- report
def row(cells):
    print("| " + " | ".join(str(c) for c in cells) + " |")


def free_days_before_cold(v) -> float:
    """Person-days an adult is free before the first cold night, after the harvest (3 days for a farm village) and the food work
    of those days."""
    a, _, _ = headcount(v)
    harvest = 3 if v["plots"] else 0
    food_days = food_labour(v) * FIRST_COLD / DAYS / UNITS["autumn"]         # food work spread evenly, in adult-days
    return max(0.0, a * (FIRST_COLD - harvest) - food_days - (v["plots"] * REAP_UNITS / UNITS["summer"] - a * harvest
                                                               if v["plots"] else 0))


def needs(villages, title):
    print(f"\n## {title}\n")
    print(f"{DAYS} days from {START[0]} day {START[1]}; winter (cold) days {COLD[0]} to {COLD[-1]}; a hearth burns "
          f"{HEARTH_FUEL:g} timber over the run, {fuel_by_cold(list(villages.values())[0]) / list(villages.values())[0]['hearths']:g} "
          f"of it by the last cold night.\n")
    row(["Village", "People (a/y/c)", "Food supply", "Demand", "x demand", "Timber need", "Woodpile + wood there",
         "Timber to bring (by the end of winter)", "Charcoal to bring", "Food to bring", "Food work share"])
    row(["---"] * 11)
    tot_s = tot_d = 0.0
    out = {}
    for name, v in villages.items():
        a, y, c = headcount(v)
        s, d = food_supply(v), food_demand(v)
        tot_s, tot_d = tot_s + s, tot_d + d
        own = v["woodpile"] + v["wood"]
        timber_in = max(0.0, fuel_demand(v) - own) if v["wood"] < 100 else 0.0
        timber_cold = max(0.0, fuel_by_cold(v) - own) if v["wood"] < 100 else 0.0
        char_in = charcoal_demand(v) if v["wood"] < 100 else 0.0
        food_in = max(0.0, d - s)
        out[name] = dict(food=food_in, timber=timber_in, timber_cold=timber_cold, charcoal=char_in, surplus=s - d)
        row([name, f"{a}/{y}/{c}", f"{s:.0f}", f"{d:.0f}", f"{s / d:.2f}", f"{fuel_demand(v):.0f}", f"{own:.0f}",
             f"{timber_in:.0f} ({timber_cold:.0f})", f"{char_in:.0f}", f"{food_in:.0f}", f"{food_labour(v) / units_total(v):.0%}"])
    row(["region", "", f"{tot_s:.0f}", f"{tot_d:.0f}", f"{tot_s / tot_d:.2f}", "", "", "", "", "", ""])
    return out


def flows(plan_rows):
    row(["Flow", "Qty", "By", "Trips", "Days away a trip", "Nights out a trip", "Carrier-days", "Extra food on the road"])
    row(["---"] * 8)
    total = 0
    for src, dst, good, qty, mode in plan_rows:
        if qty <= 0:
            continue
        p = plan(src, dst, good, qty, mode)
        if p is None:
            row([f"{good} {src} to {dst}", f"{qty:.0f}", mode, "no route", "", "", "", ""])
            continue
        n, away, nights, per, food, via = p
        total += n * away
        row([f"{good}, {src} to {dst}{via}", f"{qty:.0f}", f"{mode} ({per:g} a trip)", n, away, nights, n * away, f"{food:.0f}"])
    return total


def tool_wear(v, felled=0.0) -> dict:
    """Wear over the run from the work that uses tools: felling (what is felled there), reaping every plot, breaking by hoe the
    plots not ploughed, mining the ore smelting needs; against the tool lives the village starts with."""
    wear = felled / 3 * WEAR["fell"] + v["plots"] * REAP_UNITS * WEAR["reap"] + v["hoe_plots"] * HOE_UNITS * WEAR["hoe"]
    wear += v.get("smelt", 0) * SMELT["ore"] / 2 * WEAR["mine"]
    have = v["kit"]["crude"] * LIFE["crude"] + v["kit"]["copper"] * LIFE["copper"]
    return dict(wear=wear, have=have, short_crude=max(0.0, wear - have) / LIFE["crude"])


if __name__ == "__main__":
    need = needs(VILLAGES, "Arm 1: villages that need each other")

    print("\n### What must move before the cold ends (fuel), and over the run (food)\n")
    fuel_rows = [
        ("Ashwood", "Barleyfield", "timber", need["Barleyfield"]["timber_cold"], "pack"),
        ("Ashwood", "Millford", "timber", need["Millford"]["timber_cold"], "handcart"),
        ("Ashwood", "Coppergate", "timber", need["Coppergate"]["timber_cold"], "pack"),
        ("Ashwood", "Coppergate", "charcoal", need["Coppergate"]["charcoal"], "pack"),
    ]
    fuel_days = flows(fuel_rows)
    print()
    food_rows = [
        ("Barleyfield", "Ashwood", "grain", need["Ashwood"]["food"], "pack"),
        ("Barleyfield", "Millford", "grain", need["Millford"]["food"], "handcart"),
        ("Barleyfield", "Coppergate", "grain", need["Coppergate"]["food"], "pack"),
    ]
    food_days = flows(food_rows)

    free = {k: free_days_before_cold(v) for k, v in VILLAGES.items()}
    print(f"\nCarrier-days: fuel {fuel_days} (before the cold ends, day {COLD[-1]}), food {food_days} (over the run). Free adult-days "
          f"before the first cold night (day {FIRST_COLD}): " + ", ".join(f"{k} {v:.0f}" for k, v in free.items()) +
          f"; {sum(free.values()):.0f} in all.")
    print(f"Fuel carrying is {fuel_days / sum(free.values()):.0%} of the region's free adult-days before the cold "
          f"(a carrier's day at the far end can also be spent felling or trading there).")

    aw = VILLAGES["Ashwood"]
    felled = fuel_demand(aw) + need["Barleyfield"]["timber"] + need["Millford"]["timber"] + need["Coppergate"]["timber"] + \
        need["Coppergate"]["charcoal"] * CHARCOAL
    for g in ("crude", "copper"):
        print(f"Ashwood fells {felled:.0f} timber (its own, what it sends, and the charcoal's): {felled / FELL[g]:.0f} units with {g} "
              f"tools, {felled / FELL[g] / units_total(aw):.0%} of its {units_total(aw):.0f}.")
    print("\nTools (wear over the run against the lives of the tools each village starts with):\n")
    row(["Village", "Wear from work", "Tool life held", "Short, in crude tools"])
    row(["---"] * 4)
    for k, v in VILLAGES.items():
        tw = tool_wear(v, felled if k == "Ashwood" else min(v["wood"], fuel_demand(v)))
        row([k, f"{tw['wear']:.0f}", f"{tw['have']:.0f}", f"{tw['short_crude']:.1f}"])
    print(f"Barleyfield's surplus over its own eating and its spring seed: {need['Barleyfield']['surplus']:.0f} grain; the others need "
          f"{sum(need[k]['food'] for k in need):.0f}.")

    null = {k: dict(v) for k, v in VILLAGES.items()}
    for k in ("Barleyfield", "Millford", "Coppergate"):
        null[k]["wood"] = fuel_demand(VILLAGES[k]) + charcoal_demand(VILLAGES[k]) * CHARCOAL + 20 - VILLAGES[k]["woodpile"]
    null["Ashwood"]["plots"], null["Ashwood"]["crop"] = 4, 4 * 40
    null["Coppergate"]["stores"] = {"grain": 210, "dried meat": 12}
    null["Millford"]["crop"] = 300
    for k in null:
        null[k]["wood"] = max(null[k]["wood"], 100)
    needs(null, "Arm 0 (comparison): the same villages, each able to keep itself")
