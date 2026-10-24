"""Children as a choice, counted in days: what a child costs and gives, how fast a population grows, and what old age does within a
run. The model behind docs/cybertron2/proposals/children.md (exploration for Zach; nothing here is decided beyond D2-138 to D2-144).

Expected values, deterministic: a couple's state each day (free to try, pregnant, nursing gap) is carried as probabilities, and
children grow through infant, child and youth by days. A unit of work is worth about 1 food (02p). Every number is a PROPOSAL.
Run: python docs/review/37_growth/02v_children_model.py
"""
from __future__ import annotations

import math

DAYS = 24


def conceive(units: float, pmax: float = 0.5, k: float = 0.5) -> float:
    """The chance a night of conceiving when both partners spend `units` each trying: diminishing returns."""
    return pmax * (1 - math.exp(-k * units)) if units > 0 else 0.0


SCENARIOS = {
    # tries: share of eligible days the couple tries; units: units each spends; preg: days; gap: nursing days before trying again;
    # infant/child: days; care: units a day of a carer for an infant; infant_death: a day, with care and without; child_eat: ration
    # share; child_work: units a day; preg_food: extra food a day pregnant
    "as proposed (life.md)": dict(tries=1.0, units=1, preg=5, gap=0, infant=2, child=4, care=0, infant_death=(0.02, 0.02),
                                  child_eat=1.0, child_work=1.5, preg_food=0.0, infant_eat=0.5),
    "with Zach's changes": dict(tries=1.0, units=1, preg=5, gap=4, infant=2, child=4, care=0, infant_death=(0.02, 0.08),
                                child_eat=0.7, child_work=1.0, preg_food=0.3, infant_eat=0.5),
    "and care chosen (2 units a day)": dict(tries=1.0, units=1, preg=5, gap=4, infant=2, child=4, care=2, infant_death=(0.02, 0.08),
                                            child_eat=0.7, child_work=1.0, preg_food=0.3, infant_eat=0.5),
    "trying now and then (a third of days)": dict(tries=1 / 3, units=1, preg=5, gap=4, infant=2, child=4, care=0,
                                                  infant_death=(0.02, 0.08), child_eat=0.7, child_work=1.0, preg_food=0.3,
                                                  infant_eat=0.5),
    "trying hard (3 units each, every day)": dict(tries=1.0, units=3, preg=5, gap=4, infant=2, child=4, care=0,
                                                  infant_death=(0.02, 0.08), child_eat=0.7, child_work=1.0, preg_food=0.3,
                                                  infant_eat=0.5),
}


def births_by_day(s: dict) -> list[float]:
    """Expected births each day for one couple that starts free to try on day 0."""
    p = s["tries"] * conceive(s["units"])
    free, preg, gap = 1.0, [0.0] * s["preg"], [0.0] * max(s["gap"], 1)
    out = []
    for _ in range(DAYS):
        born = preg[-1]
        conceived = free * p
        preg = [conceived] + preg[:-1]
        if s["gap"]:
            back = gap[-1]
            gap = [born] + gap[:-1]
        else:
            back = born
        free = free - conceived + back
        out.append(born)
    return out


def child_ledger(s: dict) -> dict:
    """What one child costs and gives from conception to becoming a youth (an agent), and when it has paid back."""
    preg_cost = s["preg"] * s["preg_food"] + 2 * 1.0                       # extra food, and the mother's unit a day for 2 days
    care = s["infant"] * s["care"]
    infant = s["infant"] * s["infant_eat"]
    child = s["child"] * (s["child_eat"] - s["child_work"])
    surv = (1 - s["infant_death"][0 if s["care"] else 1]) ** s["infant"]
    cost = preg_cost + care + infant + child
    youth_net = 4 - 1.0                                                     # a youth works 4 units on 1 food
    return dict(cost=cost, survive=surv, cost_per_youth=cost / surv, payback=cost / surv / youth_net,
                days_to_agent=s["preg"] + s["infant"] + s["child"])


def row(cells):
    print("| " + " | ".join(str(c) for c in cells) + " |")


if __name__ == "__main__":
    print(f"## 1. One couple over a {DAYS}-day run, and a region of 15 couples\n")
    row(["Scenario", "Chance a night when trying", "Births a couple", "Youths (agents) by the end, a couple", "Children (no agent) at the end",
         "Region of 15 couples: new agents", "Cost to an agent (food and units)", "Survives infancy", "Pays back, days of youth work",
         "Conception to agent, days"])
    row(["---"] * 10)
    for name, s in SCENARIOS.items():
        b = births_by_day(s)
        led = child_ledger(s)
        surv = led["survive"]
        to_agent = s["infant"] + s["child"]
        youths = sum(x for d, x in enumerate(b) if d + to_agent < DAYS) * surv
        kids = sum(x for d, x in enumerate(b) if d + to_agent >= DAYS) * surv
        row([name, f"{s['tries'] * conceive(s['units']):.2f}", f"{sum(b):.2f}", f"{youths:.2f}", f"{kids:.2f}", f"{15 * youths:.0f}",
             f"{led['cost']:.1f}", f"{surv:.2f}", f"{led['payback']:.1f}", led["days_to_agent"]])

    print("\n## 2. Diminishing returns to trying (each partner's units a night)\n")
    row(["Units each"] + [str(u) for u in (1, 2, 3, 4, 6)])
    row(["---"] * 6)
    row(["Chance a night"] + [f"{conceive(u):.2f}" for u in (1, 2, 3, 4, 6)])

    print("\n## 3. Old age within a run: the chance an elder dies within the run, by when old age starts and how fast it bites\n")
    row(["Daily risk at the start of old age", "Doubling every", "Elder at the start of old age", "10 days into old age",
         "20 days into old age"])
    row(["---"] * 5)
    for h0 in (0.005, 0.01, 0.02):
        for dbl in (10, 20):
            cells = []
            for into in (0, 10, 20):
                alive = 1.0
                for d in range(DAYS):
                    alive *= 1 - min(1.0, h0 * 2 ** ((into + d) / dbl))
                cells.append(f"{1 - alive:.0%}")
            row([h0, f"{dbl} days"] + cells)
