"""Technique ladders, the extent of the market, and space: the model behind docs/review/37_growth/02d_ladders.md.

One node's economy of n agents, 4 actions each, needing 1 ration and 1 fuel (timber) a round. It is organised in one of four ways:

    solo        every agent alone: forages and hunts alone, farms with crude tools it makes, eats raw grain or hand-mills it
    household   households of 4 pool food and split the trades among their members; hunt as a party of 4; crude tools
    village     the node is one economy: specialists in every trade where demand keeps them busy; hunting parties of up to 6; a
                mine crew and a smithy (metal tools, the plough) once there are enough people; mill and bakery when they pay;
                goods move by standing arrangements through a store keeper (handling batched)
    spot        the village's specialists, but every unit that changes hands costs spot-trade actions

Skill is learnt by practice (02c §5): a trade's multiplier rises with the actions a round its practitioner spends on it, from
novice x0.5 to master x2.0. Solo agents split their practice over every trade and stay near novice; specialists who are kept busy
become masters. So the gain from specialising depends on how much work the market gives a specialist: Smith's "the division of
labour is limited by the extent of the market".

The forest is a fixed flow per node (it does not grow with the people on it): small groups can live on it, large ones must farm.

All numbers are PROPOSALS for 37.2 except those marked ENGINE. Deterministic; run:
python docs/review/37_growth/02d_ladder_model.py
"""
from __future__ import annotations

import math

TURN = 4                    # actions per agent-round
RATION, FUEL = 1.0, 1.0     # needs per agent-round (fuel averaged over the year)
HORIZON = 40                # rounds a building's construction is written off over

SKILL = dict(novice=0.5, master=2.0, tau=1.5)        # multiplier = novice + (master - novice)(1 - exp(-practice / tau))


def skill(practice):
    return SKILL["novice"] + (SKILL["master"] - SKILL["novice"]) * (1 - math.exp(-max(practice, 0.0) / SKILL["tau"]))


# the degenerate rung: the forest (per node, whatever the population)
FOREST = dict(plants_flow=6.0, forage=1.0,          # food a round the plants regrow at the managed stock; food per forage action
              game_flow=4.0,                         # food a round the game regrows
              hunt={1: 0.8, 2: 1.1, 3: 1.4, 4: 1.6, 5: 1.7, 6: 1.8})   # food per hunting effort by party size (ENGINE shape)
FARM = dict(grain=1.3)                               # grain per farm action, journeyman, metal tools
FELL = dict(timber=3.0)                              # ENGINE fell_timber
TOOLS = dict(crude=dict(mult=0.8, uses=10, timber=2.0, work=1.0),
             metal=dict(mult=1.0, uses=20, copper=2.0, timber=1.0, work=1.0),
             plough=dict(mult=2.0, uses=20, copper=3.0, timber=4.0, work=1.0))    # plough cost and wear ENGINE
MINE = dict(qmax=14.0, n0=4.0, h=3.0, crew=5, min_people=12)                       # copper a round from a crew (S-curve)
RAW = dict(ratio=1.0)                                # rations per grain eaten as porridge
QUERN = dict(grain=4.0, ratio=1.15)                  # hand-milling: grain per action, rations per grain
MILL = dict(grain=30.0, ratio=1.4, build=dict(stone=30, timber=20, work=40), upkeep=dict(stone=0.5, timber=0.5))
BAKERY = dict(bread=40.0, build=dict(stone=10, timber=10, work=10), upkeep=dict(timber=0.5))   # bread per baking action
SMITHY = dict(build=dict(stone=10, timber=10, work=10), upkeep=dict(timber=0.2))
STORE = dict(per_action=50.0, build=dict(timber=10, stone=6, work=4))              # ENGINE store cost; units handled per action
STONE = dict(per_action=2.0)
SPOT = 0.33                                          # actions per unit changing hands by spot trade (2 actions per lot of 6)


def hill(n, qmax, n0, h, **_):
    return qmax * n ** h / (n0 ** h + n ** h) if n > 0 else 0.0


def evaluate(org, n, food="best", transport=0.0):
    """Actions a round the node's needs take under `org`, with the food technique `food` (raw | quern | bread | best).
    transport: extra actions per unit of food and fuel moved to the eaters (space: 02d §5)."""
    if food == "best":
        options = ["raw", "quern"] + (["bread"] if org in ("village", "spot") else [])
        return min((evaluate(org, n, f, transport) for f in options), key=lambda r: r["total"])
    group = {"solo": 1, "household": 4}.get(org, n)              # the unit that shares work and food
    groups = n / group
    village = org in ("village", "spot")
    metal = village and n >= MINE["min_people"]
    tool = TOOLS["metal" if metal else "crude"]
    party = min(6, group) if org != "solo" else 1

    # demand per group
    food_need = RATION * group
    fuel_need = FUEL * group
    # the forest's share: plants and game are per node, split among groups
    plants = min(FOREST["plants_flow"] / groups, food_need)
    game = min(FOREST["game_flow"] / groups, food_need - plants)
    grain_rations = food_need - plants - game
    ratio = {"raw": RAW["ratio"], "quern": QUERN["ratio"], "bread": MILL["ratio"]}[food]
    grain_need = grain_rations / ratio

    # fixed point over skills (practice per practitioner) and tool wear
    T = {t: 1.0 for t in ("farm", "fell", "mill", "bake", "smith", "mine", "stone", "keep")}
    for _ in range(300):
        def practitioners(t):
            if org == "solo":
                return 1.0
            if org == "household":
                return 1.0                                  # one member takes each trade
            return max(1.0, math.ceil(T[t] / TURN - 1e-9))   # village: enough full-time specialists, at least one
        def m(t):
            return skill(T[t] / practitioners(t))
        wear = 1.0 / tool["uses"]                           # tools used up per producing action
        plough = metal                                      # farmers get the plough once metal exists
        farm_yield = FARM["grain"] * m("farm") * tool["mult"] * (TOOLS["plough"]["mult"] if plough else 1.0)
        T_farm = grain_need / farm_yield
        T_hand = 0.0
        if food == "quern":
            T_hand = grain_need / (QUERN["grain"] * m("mill"))
        T_mill = grain_need / (MILL["grain"] * m("mill")) if food == "bread" else T_hand
        T_bake = grain_rations / (BAKERY["bread"] * m("bake")) if food == "bread" else 0.0
        T_forage = plants / FOREST["forage"] + game / FOREST["hunt"][party]
        # tools and their inputs
        producing = T_farm + T_mill + T_bake + T_forage * 0.5 + 0.0    # foraging wears tools at half the rate
        tools_needed = producing * wear
        ploughs = (T_farm * (1.0 / TOOLS["plough"]["uses"])) if plough else 0.0
        if metal:
            copper = tools_needed * tool["copper"] + ploughs * TOOLS["plough"]["copper"]
            smith_work = (tools_needed * tool["work"] + ploughs * TOOLS["plough"]["work"]) / m("smith")
        else:
            copper = 0.0
            smith_work = tools_needed * tool["work"] / m("smith")
        timber_tools = tools_needed * tool["timber"] + ploughs * TOOLS["plough"]["timber"]
        # buildings (village only; per node, shared by the groups: a group's share is 1/groups)
        b_stone = b_timber = b_work = 0.0
        def add(b):
            nonlocal b_stone, b_timber, b_work
            b_stone += (b["build"].get("stone", 0) / HORIZON + b.get("upkeep", {}).get("stone", 0)) / groups
            b_timber += (b["build"].get("timber", 0) / HORIZON + b.get("upkeep", {}).get("timber", 0)) / groups
            b_work += b["build"].get("work", 0) / HORIZON / groups
        if village:
            add(STORE)
            if metal:
                add(SMITHY)
            if food == "bread":
                add(MILL)
                add(BAKERY)
        timber_need = fuel_need + timber_tools + b_timber
        T_fell = timber_need / (FELL["timber"] * m("fell") * tool["mult"])
        T_stone = b_stone / (STONE["per_action"] * m("stone") * tool["mult"])
        T_build = b_work / m("stone")                       # builders: the stone workers build (one trade, for brevity)
        T_mine = 0.0
        if metal:
            crew = MINE["crew"]
            per_round = hill(crew, **MINE) * m("mine")
            T_mine = crew * copper / per_round if per_round else float("inf")   # crew-actions per round, pro rata
        moved = (grain_rations + fuel_need) if village else 0.0             # units that reach eaters through others
        T_keep = moved / STORE["per_action"] if village else 0.0
        new = dict(farm=T_farm, fell=T_fell, mill=T_mill, bake=T_bake, smith=smith_work, mine=T_mine, stone=T_stone + T_build,
                   keep=T_keep)
        done = all(abs(new[t] - T[t]) < 1e-10 for t in new)
        T = new
        if done:
            break
    overhead = 0.0
    if village:
        overhead += (1.0 if metal else 0.0) / groups        # the mine's foreman
        overhead += (1.0 if n >= 8 else 0.0) / groups       # a clerk running the arrangements
    trade = SPOT * moved if org == "spot" else 0.0
    carry = transport * (grain_rations + fuel_need)
    total_group = sum(T.values()) + T_forage + overhead + trade + carry
    total = total_group * groups
    skills = {t: round(skill(T[t] / (1.0 if org in ("solo", "household") else max(1.0, math.ceil(T[t] / TURN - 1e-9)))), 2)
              for t in ("farm", "fell")}
    return dict(org=org, n=n, food=food, total=total, load=total / (TURN * n), forage=T_forage * groups,
                farm=T["farm"] * groups, skills=skills, metal=metal)


def table(rows, head):
    w = [max(len(str(r[i])) for r in rows + [head]) for i in range(len(head))]
    line = lambda r: "| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(r)) + " |"
    return "\n".join([line(head), "|" + "|".join("-" * (x + 2) for x in w) + "|"] + [line(r) for r in rows])


def main():
    sizes = (1, 2, 4, 6, 8, 12, 16, 24, 48, 96)
    print("## Load by population and organisation (best food technique for each)\n")
    rows = []
    for n in sizes:
        row = [n]
        for org in ("solo", "household", "village", "spot"):
            if org == "household" and n < 4:
                row.append("-")
                continue
            r = evaluate(org, n)
            row.append(f"{100 * r['load']:.0f}% ({r['food']})")
        rows.append(row)
    print(table(rows, ["agents on the node", "solo", "households of 4", "village", "village, spot trade"]))

    print("\n## The food ladder in the village: load by technique\n")
    rows = []
    for n in sizes:
        rows.append([n] + [f"{100 * evaluate('village', n, f)['load']:.0f}%" for f in ("raw", "quern", "bread")])
    print(table(rows, ["agents", "raw grain", "hand-milled", "mill and bakery"]))

    print("\n## How the forest's share falls as the node fills (village, best technique)\n")
    rows = []
    for n in sizes:
        r = evaluate("village", n)
        rows.append([n, f"{r['forage']:.1f}", f"{r['farm']:.1f}", r["skills"]["farm"], "yes" if r["metal"] else "no"])
    print(table(rows, ["agents", "forest actions a round", "farm actions a round", "farmer skill", "metal tools"]))

    print("\n## Skill: the multiplier by practice (actions a round in the trade)\n")
    print(table([[p, f"{skill(p):.2f}"] for p in (0, 0.25, 0.5, 1, 2, 3, 4)], ["practice", "multiplier"]))

    print("\n## Space: carrying food and fuel to the eaters (village of 24, best technique)\n")
    rows = []
    base = evaluate("village", 24)["total"]
    solo = evaluate("household", 24)["total"]
    for c in (0.0, 0.02, 0.05, 0.1, 0.2, 0.4):
        r = evaluate("village", 24, transport=c)
        rows.append([c, f"{100 * r['load']:.0f}%", f"{r['total'] - base:.1f}", "yes" if r["total"] < solo else "no"])
    print(table(rows, ["actions per unit carried", "village load", "extra actions a round", "still beats households of 4"]))


def threshold(lo="raw", hi="bread", org="village"):
    """The smallest population from which technique `hi` beats `lo` at every larger size (up to 400)."""
    wins = [evaluate(org, n, hi)["total"] < evaluate(org, n, lo)["total"] for n in range(2, 401)]
    for i in range(len(wins)):
        if all(wins[i:]):
            return i + 2
    return None


def thresholds():
    print("\n## Threshold population of the mill and bakery (village), by design choice\n")
    rows = []
    saved = (dict(RAW), dict(MILL), dict(BAKERY))
    cases = [("as above (porridge 1.0, mill 1.4, build 40 work)", {}, {}),
             ("porridge feeds less (0.8 a grain)", {"ratio": 0.8}, {}),
             ("cheaper mill (half the build)", {}, {"build": dict(stone=15, timber=10, work=20)}),
             ("better mill (1.6 a grain)", {}, {"ratio": 1.6}),
             ("porridge 0.8 and mill 1.6", {"ratio": 0.8}, {"ratio": 1.6})]
    for label, raw, mill in cases:
        RAW.update(saved[0]); MILL.update(saved[1]); BAKERY.update(saved[2])
        RAW.update(raw); MILL.update(mill)
        rows.append([label, threshold() or "> 400"])
    RAW.update(saved[0]); MILL.update(saved[1]); BAKERY.update(saved[2])
    print(table(rows, ["design", "agents on the node before bread pays"]))
    print("\n## Threshold population of the village over households of 4\n")
    wins = [evaluate("village", n)["total"] < evaluate("household", n)["total"] for n in range(4, 201)]
    first = next(i + 4 for i in range(len(wins)) if all(wins[i:]))
    print(f"the village beats households of 4 at every size from {first} agents (the mine crew and metal tools arrive at "
          f"{MINE['min_people']})")


if __name__ == "__main__":
    main()
    thresholds()
