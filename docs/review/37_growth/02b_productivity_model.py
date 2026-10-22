"""Productivity model for review 37.2b (docs/review/37_growth/02b_productivity.md): what an action is worth in different uses, and
how much of a society's actions its needs take under three ways of organising the same people.

Everything is priced in actions. A unit of a good costs the actions that made it, plus the actions embodied in its inputs, the wear
of the tools used, its share of the buildings it needed (cost over a horizon, plus upkeep), and the transaction actions of moving it
between agents. The society's measure is the share of its actions that its needs take (the "load"); the rest is free for politics,
building, defence, children. No model calls; deterministic. Run: python docs/review/37_growth/02b_productivity_model.py

Numbers marked ENGINE come from today's code (cybertron/camptypes/forest.py, fields.py, review 31.01b §6). Everything else is a
PROPOSAL for 37.2, to be calibrated in dry runs.
"""
from __future__ import annotations

import itertools
import math

ACTIONS = 4                    # actions per agent-round (base 3 + jitter)
HORIZON = 40                   # rounds over which a building's construction is written off


def hill(n, qmax, n0, h):
    """S-curve output of a crew of n (total, per round)."""
    return qmax * n ** h / (n0 ** h + n ** h) if n > 0 else 0.0


def crew_output(n, rel, qmax, n0, h):
    """Expected total output when each of n crew turns up with chance rel."""
    return sum(math.comb(n, j) * rel ** j * (1 - rel) ** (n - j) * hill(j, qmax, n0, h) for j in range(n + 1))


# ---------------------------------------------------------------------- the three organisations
# skill: output multiplier in the agent's trades (generalists split their practice and stay near novice; specialists reach master)
# tool: the multiplier of the tools at hand; wear: uses per tool; spot: actions per trade between agents (both sides) and lot size
CONFIGS = {
    "A autarky": dict(
        skill=0.8, tool="crude", spot=None, mill="quern", mine=None, plough=False, smithy=False, coord=None),
    "B spot specialists": dict(
        skill=1.3, tool="metal", spot=(2.0, 6.0), mill="quern", mine=dict(n=5, rel=0.7, msg=0.5), plough=False, smithy=True,
        coord=None),
    "C institutions": dict(
        skill=1.6, tool="metal", spot=(0.15, 1.0), mill="watermill", mine=dict(n=5, rel=0.95, msg=0.0), plough=True, smithy=True,
        coord=dict(foremen=2, clerks=1)),
}

P = dict(
    ration=1.0,                 # food per agent-round (ENGINE)
    fuel=0.5,                   # timber per agent-round, averaged over the year (winter 2/round a quarter of the time) PROPOSAL
    forest_food=0.3,            # food per agent-round the forest can give sustainably in an agrarian world (fields took most land)
    forage=1.5,                 # food per forage action at half stock (ENGINE: 3 x S/K)
    farm=1.6,                   # grain per farm action, journeyman, basic tools (ENGINE mean field: 1.3-1.8)
    fell=3.0,                   # timber per felling action (ENGINE fell_timber)
    quarry=2.0,                 # stone per action PROPOSAL
    tools={"none": (0.5, 0), "crude": (0.8, 10), "metal": (1.0, 20)},   # (yield multiplier, uses per tool) PROPOSAL
    crude_cost=dict(timber=2.0, work=1.0),                              # a crude tool: 2 timber and an action
    metal_cost=dict(copper=2.0, timber=1.0, work=1.0),                  # a metal tool at the smithy: copper, timber, smith work
    plough=dict(copper=3.0, timber=4.0, work=1.0, uses=20, mult=2.0),   # ENGINE cost and wear (break 5%); one action covers 2 plots
    mine=dict(qmax=14.0, n0=4.0, h=3.0),                                # copper ore per round from a crew (the S-curve)
    quern=dict(grain=4.0, ratio=1.15),                                  # grain ground per action and rations per grain
    watermill=dict(grain=20.0, ratio=1.4, build=dict(stone=30, timber=20, work=40), upkeep=dict(stone=0.5, timber=0.5)),
    smithy=dict(build=dict(stone=10, timber=10, work=10), upkeep=dict(timber=0.2)),
)
# The calibration target of 02b §6: autarky hard (about half the actions), the organised society inside the 30% rule.
TARGET = dict(P, forest_food=0.15, fuel=1.0, farm=1.3)
TARGET_SKILL = 2.0


def solve(cfg, n_agents=24, p=P):
    """Actions per unit of each good under cfg, then the society's load. Returns a dict of results."""
    sk = cfg["skill"]
    tmult, tuses = p["tools"][cfg["tool"]]
    t_cost, l_cost = cfg["spot"] if cfg["spot"] else (0.0, 1.0)
    trade = t_cost / l_cost                       # actions per unit moved between agents (0 in autarky: nothing moves)
    A = {k: 1.0 for k in ("food_grain", "timber", "stone", "copper", "tool", "plough", "work")}

    for _ in range(200):                          # the system is linear with feedback through tool wear: iterate to a fixed point
        tool_wear = (A["tool"] / tuses) if tuses else 0.0          # actions per producing action, for tool wear
        A_new = {}
        A_new["work"] = 1.0 / sk + tool_wear                        # one unit of building work
        A_new["timber"] = (1.0 + tool_wear) / (p["fell"] * sk * tmult) + trade
        A_new["stone"] = (1.0 + tool_wear) / (p["quarry"] * sk * tmult) + trade
        if cfg["tool"] == "metal":
            m = p["metal_cost"]
            A_new["tool"] = m["copper"] * A["copper"] + m["timber"] * A["timber"] + m["work"] / sk + trade
        else:
            m = p["crude_cost"]
            A_new["tool"] = m["timber"] * A["timber"] + m["work"] / sk
        if cfg["mine"]:
            mm = cfg["mine"]
            q = crew_output(mm["n"], mm["rel"], **p["mine"])
            A_new["copper"] = (mm["n"] * (1 + mm["msg"]) + mm["n"] * mm["rel"] * tool_wear) / (q * sk / 1.0) + trade
        else:
            A_new["copper"] = float("inf")
        if cfg["plough"]:
            pl = p["plough"]
            A_new["plough"] = pl["copper"] * A["copper"] + pl["timber"] * A["timber"] + pl["work"] / sk + trade
            per_action = p["farm"] * sk * tmult * pl["mult"]
            A_new["food_grain"] = (1.0 + tool_wear + A["plough"] / pl["uses"]) / per_action + trade
        else:
            A_new["food_grain"] = (1.0 + tool_wear) / (p["farm"] * sk * tmult) + trade
        if all(abs(A_new[k] - A[k]) < 1e-12 for k in A_new if math.isfinite(A_new[k])):
            A = A_new
            break
        A = A_new

    def building_per_round(name):
        b = p[name]
        build = sum(q * A[g if g != "work" else "work"] for g, q in b["build"].items()) / HORIZON
        upkeep = sum(q * A[g] for g, q in b["upkeep"].items())
        return build + upkeep

    # food: the forest first (capped), then fields, milled
    forest = min(p["forest_food"], p["ration"]) * n_agents
    forest_actions = forest / (p["forage"] * min(1.0, sk))       # foraging takes little skill: capped at journeyman
    rest = p["ration"] * n_agents - forest
    if cfg["mill"] == "quern":
        q_ = p["quern"]
        per_ration = (A["food_grain"] + 1.0 / (q_["grain"] * sk)) / q_["ratio"]
        mill_fixed = 0.0
    else:
        w = p["watermill"]
        per_ration = (A["food_grain"] + 1.0 / (w["grain"] * sk) + trade) / w["ratio"]
        mill_fixed = building_per_round("watermill")
    food_actions = forest_actions + rest * per_ration + mill_fixed
    fuel_actions = p["fuel"] * n_agents * A["timber"]
    smithy_actions = building_per_round("smithy") if cfg["smithy"] else 0.0
    coord_actions = (cfg["coord"]["foremen"] + cfg["coord"]["clerks"]) * 1.0 if cfg["coord"] else 0.0
    if cfg["mine"] and cfg["mine"]["msg"]:
        pass                                    # crew messaging is already inside A["copper"]
    total = food_actions + fuel_actions + smithy_actions + coord_actions
    budget = ACTIONS * n_agents
    return dict(A=A, per_ration=per_ration, food=food_actions, fuel=fuel_actions, fixed=smithy_actions + mill_fixed,
                coord=coord_actions, total=total, load=total / budget, free=(budget - total) / n_agents,
                support=(budget - total) / ACTIONS)


def value_per_action(cfg, p=P):
    """Food-equivalent made by one action in each use, before inputs (the gross view an agent sees)."""
    sk = cfg["skill"]
    tm = p["tools"][cfg["tool"]][0]
    out = {"forage (half stock)": p["forage"], "farm grain": p["farm"] * sk * tm}
    if cfg["plough"]:
        out["farm grain, plough"] = p["farm"] * sk * tm * p["plough"]["mult"]
    if cfg["mine"]:
        mm = cfg["mine"]
        out[f"mine copper, crew {mm['n']} (ore/worker)"] = crew_output(mm["n"], mm["rel"], **p["mine"]) * sk / mm["n"]
    return out


def table(rows, head):
    w = [max(len(str(r[i])) for r in rows + [head]) for i in range(len(head))]
    line = lambda r: "| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(r)) + " |"
    return "\n".join([line(head), "|" + "|".join("-" * (x + 2) for x in w) + "|"] + [line(r) for r in rows])


def main():
    print("## Crew S-curve (copper ore per round; crew turns up with chance 1 / 0.7)\n")
    rows = []
    for n in range(1, 11):
        q1, q7 = hill(n, **P["mine"]), crew_output(n, 0.7, **P["mine"])
        rows.append([n, f"{q1:.1f}", f"{q1 / n:.2f}", f"{q1 - hill(n - 1, **P['mine']):.2f}", f"{q7 / n:.2f}"])
    print(table(rows, ["crew", "total", "per worker", "marginal", "per worker, rel 0.7"]))

    for label, pp, msk in (("today's numbers", P, None), ("the calibration target", TARGET, TARGET_SKILL)):
        print(f"\n## Actions per unit, and the society's load (24 agents, 4 actions each): {label}\n")
        load_table(pp, msk)
    main_rest()


def load_table(pp, master=None):
    rows = []
    res = {name: solve(dict(cfg, skill=master) if master and name.startswith("C") else cfg, p=pp) for name, cfg in CONFIGS.items()}
    for name, r in res.items():
        A = r["A"]
        cu = "n/a" if not math.isfinite(A["copper"]) else f"{A['copper']:.2f}"
        rows.append([name, f"{r['per_ration']:.2f}", f"{A['timber']:.2f}", cu, f"{A['tool']:.2f}", f"{r['food']:.1f}",
                     f"{r['fuel']:.1f}", f"{r['fixed'] + r['coord']:.1f}", f"{r['total']:.1f}", f"{100 * r['load']:.0f}%",
                     f"{r['free']:.2f}", f"{r['support']:.1f}"])
    print(table(rows, ["organisation", "actions/ration", "actions/timber", "actions/copper", "actions/tool", "food", "fuel",
                       "buildings+coord", "total", "load", "free actions/agent", "free, in agents' full time"]))


def main_rest():
    print("\n## Gross value per action as an agent sees it\n")
    for name, cfg in CONFIGS.items():
        print(name, {k: round(v, 2) for k, v in value_per_action(cfg).items()})

    print("\n## Scale: load by population (C institutions; A autarky)\n")
    rows = []
    for n in (6, 8, 12, 16, 24, 48):
        a = solve(CONFIGS["A autarky"], n)
        c = dict(CONFIGS["C institutions"])
        crew = min(5, max(1, n // 4))
        c["mine"] = dict(n=crew, rel=0.95, msg=0.0)
        c["coord"] = dict(foremen=1 if n < 12 else 2, clerks=1)
        rc = solve(c, n)
        # below about 12 agents a watermill does not pay its fixed cost: compare with the quern
        cq = dict(c, mill="quern")
        rq = solve(cq, n)
        best = min(rc, rq, key=lambda r: r["load"])
        rows.append([n, crew, f"{100 * a['load']:.0f}%", f"{100 * rq['load']:.0f}%", f"{100 * rc['load']:.0f}%",
                     "watermill" if best is rc else "quern"])
    print(table(rows, ["agents", "mine crew", "A load", "C load, quern", "C load, watermill", "C's best mill"]))

    print("\n## Sensitivity (C institutions vs A autarky, 24 agents): one parameter moved at a time\n")
    base_a, base_c = solve(CONFIGS["A autarky"])["load"], solve(CONFIGS["C institutions"])["load"]
    rows = [["base", "", f"{100 * base_a:.0f}%", f"{100 * base_c:.0f}%", f"{base_a / base_c:.2f}x"]]
    cases = [
        ("master skill", "skill", [1.0, 1.3, 2.0]),
        ("forest food per head", "forest_food", [0.0, 0.6, 1.0]),
        ("fuel per head", "fuel", [0.0, 1.0]),
        ("farm grain per action", "farm", [1.0, 2.4]),
    ]
    for label, key, vals in cases:
        for v in vals:
            if key == "skill":
                c = dict(CONFIGS["C institutions"], skill=v)
                ra, rc = solve(CONFIGS["A autarky"]), solve(c)
            else:
                pp = dict(P, **{key: v})
                ra, rc = solve(CONFIGS["A autarky"], p=pp), solve(CONFIGS["C institutions"], p=pp)
            rows.append([label, v, f"{100 * ra['load']:.0f}%", f"{100 * rc['load']:.0f}%", f"{ra['load'] / rc['load']:.2f}x"])
    for tc in (0.5, 2.0, 4.0):
        c = dict(CONFIGS["C institutions"], spot=(tc, 1.0))
        rc = solve(c)
        rows.append(["C trade cost (actions/unit)", tc, f"{100 * base_a:.0f}%", f"{100 * rc['load']:.0f}%", f"{base_a / rc['load']:.2f}x"])
    print(table(rows, ["moved", "value", "A load", "C load", "A / C"]))

    print("\n## Who can take the surplus (C, 24 agents)\n")
    a, c = solve(CONFIGS["A autarky"]), solve(CONFIGS["C institutions"])
    surplus = a["total"] - c["total"]
    print(f"actions a round the organised economy saves over autarky: {surplus:.1f} "
          f"({surplus / 24:.2f} per agent; {surplus / ACTIONS:.1f} agents' full time)")


if __name__ == "__main__":
    main()


def decomposition(pp=TARGET, master=TARGET_SKILL):
    """C at the calibration target, with one of its advantages taken away at a time."""
    c = dict(CONFIGS["C institutions"], skill=master)
    cases = [
        ("C institutions", c),
        ("  without master skill (journeyman 1.0)", dict(c, skill=1.0)),
        ("  without the plough", dict(c, plough=False)),
        ("  with spot trade instead of standing contracts", dict(c, spot=(2.0, 6.0), coord=dict(foremen=2, clerks=0))),
        ("  with an ad hoc mine crew (turns up 0.7, messages 0.5)", dict(c, mine=dict(n=5, rel=0.7, msg=0.5))),
        ("  with a quern instead of the watermill", dict(c, mill="quern")),
        ("A autarky", CONFIGS["A autarky"]),
    ]
    rows = []
    for label, cfg in cases:
        r = solve(cfg, p=pp)
        rows.append([label, f"{r['total']:.1f}", f"{100 * r['load']:.0f}%"])
    print("\n## Where C's advantage comes from (calibration target, 24 agents)\n")
    print(table(rows, ["case", "actions a round on needs", "load"]))
    a, cc = solve(CONFIGS["A autarky"], p=pp), solve(c, p=pp)
    s = a["total"] - cc["total"]
    print(f"\nsurplus over autarky at the target: {s:.1f} actions a round ({s / ACTIONS:.1f} agents' full time)")
    rows = []
    for n in (8, 12, 16, 24, 48):
        a = solve(CONFIGS["A autarky"], n, p=pp)
        crew = min(5, max(1, n // 4))
        cn = dict(c, mine=dict(n=crew, rel=0.95, msg=0.0), coord=dict(foremen=1 if n < 12 else 2, clerks=1))
        rq, rw = solve(dict(cn, mill="quern"), n, p=pp), solve(cn, n, p=pp)
        rows.append([n, f"{100 * a['load']:.0f}%", f"{100 * rq['load']:.0f}%", f"{100 * rw['load']:.0f}%"])
    print("\n## Scale at the calibration target\n")
    print(table(rows, ["agents", "A load", "C load, quern", "C load, watermill"]))


if __name__ == "__main__":
    decomposition()
