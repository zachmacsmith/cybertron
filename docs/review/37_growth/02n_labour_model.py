"""Labour scarcity, grinding and mills, and the plot unit: the model behind docs/review/37_growth/02n_labour.md.

Answers the critique of 23 Oct: at the engine's rates food takes about 8% of a person's units, so nothing makes labour scarce;
D2-44's mill pays at no village size; and the node cap (15-20 people) sits below 02d's thresholds. Four parts:
    1. the plot unit (D4-23: about what one adult can work in a season), rescaled from 02l's seed-sized plots
    2. a household's full labour budget over a year, with the sinks that could make labour bind (grinding, fuel, herding, hay,
       upkeep, tools) and how sensitive food's share is to each
    3. mills: quern, hand millstones, water wheel; thresholds with and without a toll; the toll a holder can charge
    4. a mill serving several nodes (carrying grain one edge and back), and how many people a specialist needs to reach mastery

Units are the engine's work units (cybertron2/engine/data.py PHYSICS: 7 in summer, 6 in spring and autumn, 5 in winter). Engine
rates are marked ENGINE; everything else is a PROPOSAL to calibrate. Deterministic. Run: python docs/review/37_growth/02n_labour_model.py
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------- the world (ENGINE where marked)
YEAR = 24                                   # days a year: ENGINE region spec (season_days 6); a world setting, 16-60 (D4-13)
UNITS = {"spring": 6, "summer": 7, "autumn": 6, "winter": 5}          # ENGINE PHYSICS units
YOUTH_UNITS, ELDER_UNITS = 4, 5                                       # ENGINE
RATION = 1.0                                                          # ENGINE
FUEL = {"normal": 0.5, "cold": 2.0}                                   # ENGINE: timber a house a night
FELL_UNITS, FELL_TIMBER = 2, 3.0                                      # ENGINE: a fell, crude tool; copper x2
BREAKS = {"normal": 0.02, "cold": 0.08}                               # ENGINE: a house's chance of breaking a night
REPAIR_UNITS, REPAIR_TIMBER = 2, 2                                    # ENGINE repair technique
# ENGINE farming: sowing 1 unit puts 3 seed in; the crop returns 5x the seed; reaping is 2 units for 6 grain; weeding adds up to 50%
E_SEED_PER_UNIT, E_RETURN, E_REAP_UNITS, E_REAP_YIELD, E_GROW = 3, 5.0, 2, 6.0, 6

# ---------------------------------------------------------------- 02l's small plot (per crop), for the rescaling
SMALL_SEED = 3.0
SMALL = {   # method: (units a crop slot, net food a crop slot) on one of 02l's small plots, averaged over the rotation (02l's ladder)
    "sow and reap, grain then fallow": (1.00, 2.13),
    "hoe and weeding, grain then fallow": (3.50, 5.96),
    "hoe and weeding, grain then legumes": (7.00, 9.72),
    "ox plough and weeding, grain-legume-grazed fallow": (3.17, 7.62),
    "ox plough, weeding and manure, grain-legume": (5.25, 10.77),
}
FARM_SHARE = 0.5                            # PROPOSAL: a plot is what one adult farms with half its growing-season units


def season_units() -> float:
    """An adult's units in the growing season (three of the four seasons)."""
    return YEAR / 4 * (UNITS["spring"] + UNITS["summer"] + UNITS["autumn"])


def table(rows, head):
    w = [max(len(str(r[i])) for r in rows + [head]) for i in range(len(head))]
    line = lambda r: "| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(r)) + " |"
    return "\n".join([line(head), "|" + "|".join("-" * (x + 2) for x in w) + "|"] + [line(r) for r in rows])


# ---------------------------------------------------------------- 1. the plot unit
def plot_unit():
    crops = 3 * (YEAR / 4) / E_GROW                              # crop slots in the growing season (a crop takes E_GROW days)
    adult = season_units() * FARM_SHARE                          # one adult's farming units in a season
    hoe_units, _ = SMALL["hoe and weeding, grain then fallow"]
    scale = adult / (crops * hoe_units)                           # small plots in one plot: one adult by hoe works one plot
    print(f"## 1. The plot unit (year {YEAR} days; {crops:g} crop slots in the growing season; an adult farms "
          f"{adult:.0f} units a season)\n")
    print(f"One plot = {scale:.1f} of 02l's seed-sized plots: seed {SMALL_SEED * scale:.1f} grain a sowing.\n")
    need = 5 * RATION * YEAR                                      # a household of 5 for a year (seed kept back is inside net)
    rows = []
    for m, (u, f) in SMALL.items():
        u_crop = u * scale                                        # units a crop slot on one plot
        f_crop = f * scale
        u_year = u_crop * crops
        f_year = f_crop * crops
        adults = u_year / adult
        rows.append([m, f"{u_crop:.1f}", f"{f_crop:.1f}", f"{f_year:.0f}", f"{1 / adults:.1f}", f"{need / f_year:.1f}",
                     f"{u_year / f_year:.2f}"])
    print(table(rows, ["method", "units a crop slot", "net food a crop slot", "net food a year", "plots one adult can work",
                       "plots a household of 5 needs", "units a ration"]))
    print(f"\nENGINE today: sow 1 unit (3 seed) -> 15 grain; reap 2 units a 6 grain: {E_RETURN * E_SEED_PER_UNIT:g} grain "
          f"for {1 + E_RETURN * E_SEED_PER_UNIT / E_REAP_YIELD * E_REAP_UNITS:.0f} units = "
          f"{(1 + E_RETURN * E_SEED_PER_UNIT / E_REAP_YIELD * E_REAP_UNITS) / (E_RETURN * E_SEED_PER_UNIT - E_SEED_PER_UNIT):.2f} "
          "units a net ration, with no breaking of the soil and no limit on plots but the land.")
    return scale


# ---------------------------------------------------------------- 2. the household's labour budget
HH = {"adults": 3, "youths": 1, "elders": 1}                         # a household of 5
CATTLE = 2                                                           # an ox and a cow
FOOD_UNITS_PER_RATION = 0.55                                         # growing the grain (engine 0.5; 02l hoe 0.58)
GRIND = {"none": 0.0, "coarse meal (6 a unit)": 1 / 6, "quern flour (4 a unit)": 0.25}
HERD_MIN = 1.0                                                       # 02l: any herd needs watching, 1 unit a day (a youth can)
HAY_PER_HEAD_WINTER = 1.0                                            # hay a head a winter day; 3 hay a unit cut
TOOL_UPKEEP = 3.0                                                    # units a year making and replacing tools (02m: crude tools)


def units_a_year() -> float:
    a = YEAR / 4 * sum(UNITS.values())
    return HH["adults"] * a + HH["youths"] * YEAR * YOUTH_UNITS + HH["elders"] * YEAR * ELDER_UNITS


def budget(grind="none", copper_axe=False, cattle=CATTLE, food_units=FOOD_UNITS_PER_RATION):
    mouths = sum(HH.values())
    rations = mouths * RATION * YEAR
    winter = YEAR / 4
    fuel = (YEAR - winter) * FUEL["normal"] + winter * FUEL["cold"]
    fell = fuel / (FELL_TIMBER * (2 if copper_axe else 1)) * FELL_UNITS
    breaks = (YEAR - winter) * BREAKS["normal"] + winter * BREAKS["cold"]
    lines = {
        "growing food": rations * food_units,
        "grinding": rations * GRIND[grind],
        "fuel (felling)": fell,
        "herding": HERD_MIN * YEAR if cattle else 0.0,
        "hay for winter": cattle * HAY_PER_HEAD_WINTER * winter / 3,
        "house upkeep": breaks * (REPAIR_UNITS + REPAIR_TIMBER / FELL_TIMBER * FELL_UNITS),
        "tools": TOOL_UPKEEP,
    }
    return lines, units_a_year()


def labour_budget():
    print(f"\n## 2. A household's year (3 adults, a youth, an elder; {units_a_year():.0f} units a year)\n")
    rows = []
    for g in GRIND:
        lines, total = budget(grind=g)
        food = lines["growing food"] + lines["grinding"]
        rows.append([g] + [f"{lines[k]:.0f}" for k in lines] + [f"{food / total:.0%}", f"{sum(lines.values()) / total:.0%}",
                                                             f"{1 - sum(lines.values()) / total:.0%}"])
    print(table(rows, ["grinding for porridge", "growing food", "grinding", "fuel", "herding", "hay", "house", "tools",
                       "food + grinding", "all sinks", "left free"]))
    print("\nSensitivity (food + grinding as a share of units, quern flour for all grain):\n")
    rows = []
    for fu in (0.4, 0.5, 0.55, 0.7, 0.9):
        lines, total = budget(grind="quern flour (4 a unit)", food_units=fu)
        rows.append([f"{fu:g}", f"{(lines['growing food'] + lines['grinding']) / total:.0%}", f"{sum(lines.values()) / total:.0%}"])
    print(table(rows, ["units to grow a ration", "food + grinding", "all sinks"]))


# ---------------------------------------------------------------- 3. mills
GRAIN_VALUE = 0.55                                                   # units a ration of grain is worth (its cost to grow)
MILLS = {   # name: (grain ground a unit, capital in units, upkeep a year, needs)
    "quern (household)": (4, 3, 0.2, "2 stone: basic"),
    "hand millstones": (12, 20 + 11, 2.0, "10 stone, a mason, a room"),
    "water mill": (40, 20 + 31 + 11, 3.0, "millstones, a wheel (15 timber, 1 copper), a river site, a room"),
}
LIFE = 10                                                            # years a mill lasts


def sensitivity():
    """What it takes to bring food and its processing to 25-30% of a household's units."""
    global HH
    keep = dict(HH)
    rows = []
    for label, hh in (("3 adults, a youth, an elder", {"adults": 3, "youths": 1, "elders": 1}),
                      ("2 adults, a youth, 2 children", {"adults": 2, "youths": 1, "elders": 0, "children": 2})):
        HH = {k: v for k, v in hh.items() if k != "children"}
        kids = hh.get("children", 0)
        for fu in (0.55, 0.85):
            for g in ("none", "quern flour (4 a unit)"):
                lines, total = budget(grind=g, food_units=fu)
                mouths = sum(hh.values())
                extra = (mouths - sum(HH.values())) * RATION * YEAR * (fu + GRIND[g])   # the children eat too
                total += kids * YEAR * CHILD_UNITS
                food = lines["growing food"] + lines["grinding"] + extra
                rows.append([label, f"{fu:g}", g, f"{food / total:.0%}", f"{(sum(lines.values()) + extra) / total:.0%}"])
    HH = keep
    print("\nWhat brings food to 25-30% (food and grinding as a share of the household's units):\n")
    print(table(rows, ["household", "units to grow a ration", "grinding", "food + grinding", "all sinks"]))


CHILD_UNITS = 2                                                      # PROPOSAL: a child's menial work (D4-19), units a day


def mills():
    print(f"\n## 3. Mills (year {YEAR} days; a ration of grain worth {GRAIN_VALUE} units)\n")
    q = 1 / MILLS["quern (household)"][0]
    rows = []
    for name, (rate, cap, upkeep, needs) in MILLS.items():
        if name.startswith("quern"):
            continue
        saved = q - 1 / rate                                         # units saved a ration against the quern
        yearly = cap / LIFE + upkeep
        n_star = yearly / (YEAR * RATION * saved)
        toll = q / GRAIN_VALUE                                        # the share of the grain a household would give up rather than grind
        rows.append([name, needs, f"{1 / rate:.3f}", f"{saved:.3f}", f"{cap:g}", f"{yearly:.1f}", f"{n_star:.1f}",
                     f"{min(toll, 1):.0%}", f"{yearly / (15 * YEAR * GRAIN_VALUE):.1%}"])
    print(table(rows, ["mill", "needs", "units a ration", "saved a ration", "capital", "cost a year", "people to pay (no toll)",
                       "most toll before querns win", "toll that covers it at 15 people"]))
    # bread only (D2-44 as decided): the mill's only gain is bread's tenth over porridge, and porridge needs no grinding
    gain = 0.1 * GRAIN_VALUE                                         # a tenth more food a loaf
    for name, (rate, cap, upkeep, needs) in MILLS.items():
        cost_loaf = 1 / rate + 0.1 + 0.1 * FELL_UNITS / FELL_TIMBER  # grinding + baking + fuel, a loaf
        print(f"- bread only, {name}: a loaf costs {cost_loaf:.2f} units of work for {gain:.3f} units of extra food: "
              f"{'pays' if gain > cost_loaf else 'never pays'} for eating at home")


# ---------------------------------------------------------------- 4. one mill for several nodes; specialists' mastery
CARRY = {"on foot": 0.92, "pack ox": 0.19, "ox cart": 0.074}         # units a unit an edge (02g §3)


def mill_for_nodes():
    print("\n## 4a. Carrying grain to a water mill and flour back, against grinding at home\n")
    q = 1 / MILLS["quern (household)"][0]
    w = 1 / MILLS["water mill"][0]
    rows = []
    for how, c in CARRY.items():
        for edges in (1, 2):
            trip = 2 * c * edges                                     # grain there, flour back
            hm = 1 / 12 - w                                          # against hand millstones at one's own node
            rows.append([how, edges, f"{trip:.2f}", f"{q - w:.3f}", "pays" if trip < q - w else "no",
                         f"{hm:.3f}", "pays" if trip < hm else "no"])
    print(table(rows, ["carried by", "edges away", "carrying a ration, both ways", "saved against a quern",
                       "worth it", "saved against hand millstones at home", "worth it"]))


TAU = 50.0                                                           # PROPOSAL: practice (units of that work) for the curve


def skill(p, trade=True, tau=TAU):
    if trade:
        return 0.5 + 1.5 * (1 - math.exp(-p / tau))
    return 1.0 + 0.5 * (1 - math.exp(-p / tau))


def mastery():
    master_p = -TAU * math.log(1 - (1.8 - 0.5) / 1.5)               # practice to reach x1.8 on the trade curve
    season = season_units()
    full_time = season * 0.8
    print(f"\n## 4b. Mastery: practice to reach x1.8 (tau {TAU:g}) is {master_p:.0f} units; a full-time specialist puts in about "
          f"{full_time:.0f} in a growing season\n")
    demand = {   # units of that trade's work a person needs a growing season
        "farmer (grain by hoe)": RATION * YEAR * 0.75 * FOOD_UNITS_PER_RATION,
        "miller (hand millstones)": RATION * YEAR * 0.75 / 12,
        "smith (tools, blades, coin)": 2.0 * 0.75,                   # about 2 units a person a year (02m: a tool a household a year)
        "woodsman (fuel and building timber)": 0.6 * YEAR * 0.75 / 5 * 2,
    }
    rows = []
    for t, d in demand.items():
        people_full = full_time / d
        people_master = master_p / d
        rows.append([t, f"{d:.1f}", f"{people_full:.0f}", f"{people_master:.0f}"])
    print(table(rows, ["trade", "work a person needs a season", "people to keep one full-time", "people for mastery in one season"]))
    rows = []
    for tau in (25, 50, 100):
        need = -tau * math.log(1 - 1.3 / 1.5)
        rows.append([tau, f"{need:.0f}", f"{need / demand['farmer (grain by hoe)']:.0f}",
                     f"{skill(full_time / 3, True, tau):.2f}", f"{skill(full_time / 3, False, tau):.2f}"])
    print("\nThe curve's tau against node size (a part-timer farms a third of its season):\n")
    print(table(rows, ["tau", "practice to master", "people a master farmer needs", "part-timer on a trade curve",
                       "part-timer on the basic curve"]))


if __name__ == "__main__":
    plot_unit()
    labour_budget()
    sensitivity()
    mills()
    mill_for_nodes()
    mastery()
