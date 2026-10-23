"""Exploring a scheduler where slower scales set the odds of faster ones. Design exploration only, not engine code: the model
behind docs/cybertron2/proposals/environment.md.

Layers, each drawn from the seed and independent of what agents do (D4-4), each reading the one above (D4-5):
    era      years: a climate regime (moisture and temperature anomalies), a Markov chain with long dwell times
    year     the calendar's seasons (fixed) and each year's severity, drawn given the era
    spell    days: dry and wet spells and cold snaps, a semi-Markov chain given the season and the year
    incident a day at a place: a hazard rate = base x drivers (spell, season, era, land kind) x exposure (local state)
    spread   an incident that can spread (fire, fever) tries its neighbours each day with its own odds
Incidents fire when a paired uniform U(seed, kind, place, day) falls below the hazard, so two arms share every draw and differ
only where their local states differ. Every layer also emits signs (observables) with a sense, a range, a salience and a lag.

All rates are PROPOSALS for exploration. Deterministic. Run: python docs/review/37_growth/02q_environment_model.py
"""
from __future__ import annotations

import random
from collections import Counter

YEAR, SEASONS = 40, (("spring", 10), ("summer", 10), ("autumn", 10), ("winter", 10))
ERAS = {  # regime: (moisture anomaly, temperature anomaly, mean dwell in years)
    "steady": (0.0, 0.0, 6), "dry": (-0.5, 0.2, 4), "wet": (0.5, -0.1, 4), "cold": (0.1, -0.6, 3)}
ERA_NEXT = {"steady": {"dry": 0.4, "wet": 0.4, "cold": 0.2}, "dry": {"steady": 0.7, "cold": 0.3},
            "wet": {"steady": 0.7, "cold": 0.3}, "cold": {"steady": 0.6, "wet": 0.4}}


def rng(seed, *parts):
    return random.Random("|".join(str(p) for p in (seed,) + parts))


def eras(seed, years):
    out, era, y = [], "steady", 0
    while y < years:
        dwell = max(1, round(rng(seed, "era", y).expovariate(1 / ERAS[era][2])))
        out += [era] * dwell
        y += dwell
        nxt = ERA_NEXT[era]
        u, acc = rng(seed, "era-next", y).random(), 0.0
        for k, p in nxt.items():
            acc += p
            if u < acc:
                era = k
                break
    return out[:years]


def season_of(day):
    d = day % YEAR
    for name, n in SEASONS:
        if d < n:
            return name
        d -= n


def year_severity(seed, y, era):
    """A year's moisture and temperature: the era's anomaly plus the year's own draw."""
    m, t, _ = ERAS[era]
    r = rng(seed, "year", y)
    return m + r.gauss(0, 0.35), t + r.gauss(0, 0.3)


def spells(seed, years, era_by_year):
    """Each day's weather: 'dry', 'wet', 'normal', or 'cold snap', as spells of several days, odds set by season and year."""
    days, state, left = [], "normal", 0
    for y in range(years):
        ym, yt = year_severity(seed, y, era_by_year[y])
        for d in range(YEAR):
            day = y * YEAR + d
            if left <= 0:
                s = season_of(day)
                r = rng(seed, "spell", day)
                p_dry = max(0.03, 0.25 - 0.45 * ym + (0.15 if s == "summer" else 0))
                p_wet = max(0.03, 0.25 + 0.45 * ym + (0.1 if s in ("spring", "autumn") else 0))
                p_cold = max(0.0, (0.3 if s == "winter" else 0.02) - 0.2 * yt)
                u = r.random()
                state = "dry" if u < p_dry else "wet" if u < p_dry + p_wet else "cold snap" if u < p_dry + p_wet + p_cold else "normal"
                left = max(1, round(r.expovariate(1 / (6 if state in ("dry", "wet") else 3))))
            days.append(state)
            left -= 1
    return days


# places: a small region; each node has parcels of some land kinds; forests can burn; wet places breed fever
NODES = {"Millford": {"kind": "river valley", "forest": 2, "fen": 0, "people": 18},
         "Ashwood": {"kind": "woodland", "forest": 6, "fen": 0, "people": 10},
         "Fenwick": {"kind": "fen", "forest": 1, "fen": 3, "people": 8}}
KIND = {  # how a land kind answers the weather: multipliers on hazards
    "river valley": {"flood": 1.0, "fire": 0.6, "fever": 0.8, "blight": 1.0},
    "woodland": {"flood": 0.2, "fire": 1.5, "fever": 0.6, "blight": 0.8},
    "fen": {"flood": 0.6, "fire": 0.3, "fever": 2.0, "blight": 1.2}}
BASE = {"fire": 0.004, "flood": 0.01, "fever": 0.004, "blight": 0.006}       # a day, per forest parcel / node / node / node
WEATHER = {  # driver: hazard multiplier by the day's spell
    "fire": {"dry": 4.0, "wet": 0.2, "normal": 1.0, "cold snap": 0.3},
    "flood": {"dry": 0.0, "wet": 5.0, "normal": 0.3, "cold snap": 0.2},
    "fever": {"dry": 0.6, "wet": 1.8, "normal": 1.0, "cold snap": 1.3},
    "blight": {"dry": 0.5, "wet": 2.5, "normal": 1.0, "cold snap": 0.5}}
SEASON = {"fire": {"summer": 2.0, "winter": 0.2}, "flood": {"spring": 2.0, "summer": 0.3}, "fever": {"autumn": 1.5, "winter": 1.3},
          "blight": {"summer": 1.5, "winter": 0.0}}


def simulate(seed, years=6):
    ebys = eras(seed, years)
    days = spells(seed, years, ebys)
    log, by_year = [], [Counter() for _ in range(years)]
    burning = {}                                     # (node, parcel) -> days left
    ill = {n: 0 for n in NODES}
    for day, weather in enumerate(days):
        y, s = day // YEAR, season_of(day)
        for n, node in NODES.items():
            k = KIND[node["kind"]]
            # fire: per forest parcel, plus spread to neighbouring parcels while one burns
            for p in range(node["forest"]):
                h = BASE["fire"] * WEATHER["fire"][weather] * SEASON["fire"].get(s, 1.0) * k["fire"]
                if (n, p) not in burning and rng(seed, "fire", n, p, day).random() < h:
                    burning[(n, p)] = 2
                    by_year[y]["fire started"] += 1
            for (bn, bp), left in list(burning.items()):
                if bn != n:
                    continue
                for q in (bp - 1, bp + 1):                                  # neighbours in a line of parcels
                    if 0 <= q < node["forest"] and (n, q) not in burning:
                        spread = 0.5 * WEATHER["fire"][weather] / 4
                        if rng(seed, "fire-spread", n, q, day).random() < spread:
                            burning[(n, q)] = 2
                            by_year[y]["fire spread"] += 1
                burning[(bn, bp)] = left - 1
                if left - 1 <= 0:
                    del burning[(bn, bp)]
            for kind in ("flood", "blight"):
                h = BASE[kind] * WEATHER[kind][weather] * SEASON[kind].get(s, 1.0) * k[kind]
                if rng(seed, kind, n, day).random() < h:
                    by_year[y][kind] += 1
            # fever: an outbreak starts with the hazard, then spreads within the node (exposure: crowding) and burns out
            h = BASE["fever"] * WEATHER["fever"][weather] * SEASON["fever"].get(s, 1.0) * k["fever"]
            if ill[n] == 0 and rng(seed, "fever", n, day).random() < h:
                ill[n] = 1
                by_year[y]["fever outbreak"] += 1
            elif ill[n] > 0:
                sus = node["people"] - ill[n]
                new = sum(1 for i in range(sus) if rng(seed, "infect", n, i, day).random() < 0.04 * ill[n] / node["people"] * 10)
                rec = sum(1 for i in range(ill[n]) if rng(seed, "recover", n, i, day).random() < 0.2)
                by_year[y]["fever cases"] += new
                ill[n] = max(0, ill[n] + new - rec)
    return ebys, days, by_year


def report(seed=7, years=6):
    ebys, days, by_year = simulate(seed, years)
    print(f"## One region, {years} years of {YEAR} days (seed {seed})\n")
    kinds = ["fire started", "fire spread", "flood", "blight", "fever outbreak", "fever cases"]
    print("| year | era | moisture | dry days | wet days | cold days | " + " | ".join(kinds) + " |")
    print("|" + "---|" * (6 + len(kinds)))
    for y in range(years):
        m, _ = year_severity(seed, y, ebys[y])
        c = Counter(days[y * YEAR:(y + 1) * YEAR])
        print(f"| {y + 1} | {ebys[y]} | {m:+.2f} | {c['dry']} | {c['wet']} | {c['cold snap']} | " +
              " | ".join(str(by_year[y][k]) for k in kinds) + " |")


def era_contrast(seeds=range(40)):
    """The same machinery under each era held fixed: incidents a year, averaged over seeds."""
    print("\n## Incidents a year by era (era held fixed; averages over 40 seeds)\n")
    kinds = ["fire started", "fire spread", "flood", "blight", "fever outbreak", "fever cases"]
    print("| era | " + " | ".join(kinds) + " |")
    print("|" + "---|" * (1 + len(kinds)))
    global eras
    real = eras
    for era in ERAS:
        tot = Counter()
        eras = lambda seed, years, e=era: [e] * years                       # noqa: E731
        for sd in seeds:
            _, _, by_year = simulate(sd, years=1)
            tot.update(by_year[0])
        print(f"| {era} | " + " | ".join(f"{tot[k] / len(seeds):.1f}" for k in kinds) + " |")
    eras = real


if __name__ == "__main__":
    report()
    era_contrast()


# ---------------------------------------------------------------- 23 Oct (b): shared hidden state and a cascade
# A node's low ground has a water table; its latrines sit on it; its well draws from it. Each variable relaxes toward a baseline
# and is pushed by the day's spell; hazards read the variables. Effects propagate one step a day (no loops within a day).
def cascade(seed, weather_days, people=18, latrine_near_well=True):
    table, well, sick, immune, flooded_days, log = 0.3, 1.0, 0, 0, 0, []    # water table 0..1; well quality 0..1 (1 clean)
    for day, w in enumerate(weather_days):
        push = {"wet": 0.08, "dry": -0.05, "normal": -0.01, "cold snap": 0.0}[w]
        table = min(1.0, max(0.0, table + push - 0.05 * (table - 0.3)))         # relax toward 0.3
        flooded = table > 0.8
        flooded_days += flooded
        # latrines overflow into the well when the table is high; the well clears slowly
        seep = (0.25 if latrine_near_well else 0.05) * max(0.0, table - 0.6)
        well = min(1.0, max(0.0, well - seep + 0.08 * (1 - well)))
        # flux: each healthy, non-immune drinker falls ill with a chance from the well's dirt; and from the sick (contact)
        dirt = 1 - well
        new = 0
        for i in range(people - sick - immune):
            p = 0.03 * dirt + 0.01 * sick / people
            if rng(seed, "flux", i, day).random() < p:
                new += 1
        rec = sum(1 for i in range(sick) if rng(seed, "flux-rec", i, day).random() < 0.15)
        sick, immune = sick + new - rec, immune + rec
        log.append((day, w, round(table, 2), round(well, 2), sick))
    return log, flooded_days


def cascade_report(seed=3):
    print("\n## A cascade from shared hidden state: wet spell -> water table -> latrines into the well -> flux\n")
    wet = ["normal"] * 5 + ["wet"] * 10 + ["normal"] * 15
    dry = ["normal"] * 5 + ["dry"] * 10 + ["normal"] * 15
    for name, days, near in (("a wet spell, latrine near the well", wet, True), ("a wet spell, latrine away from the well", wet, False),
                             ("a dry spell", dry, True)):
        log, fd = cascade(seed, days, latrine_near_well=near)
        peak = max(x[4] for x in log)
        worst_well = min(x[3] for x in log)
        total = sum(1 for i in range(1, len(log)) if log[i][4] > log[i - 1][4])
        print(f"- {name}: water table peaks at {max(x[2] for x in log):.2f}, flooded {fd} days, the well falls to {worst_well:.2f} "
              f"clean, flux peaks at {peak} sick of 18")


if __name__ == "__main__":
    cascade_report()
