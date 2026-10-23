"""Farming: stages, methods, rotations, cattle and the harvest peak, costed in work units. The model behind
docs/review/37_growth/02l_farming.md.

A plot is the unit of field land. A crop on a plot runs: (break the soil) -> sow -> (weed) -> reap, with (manure) and the choice of
crop (rotation) as further optional steps. The minimum path is sow and reap. Each optional step costs units and raises the
harvest or protects the soil; some (the ox plough, manure) need cattle, so they pay only above a scale.

Units are 38.06's work units (6 a day for an adult; forage 1). 02j's "actions" are on the same scale (wild food 1 unit a food).
Every number is a PROPOSAL for calibration; only the ratios between rungs matter here: the absolute level is scaled at the end so
that food takes its target share of work (scenario_design: binding, at most 30%). Deterministic.
Run: python docs/review/37_growth/02l_farm_model.py
"""
from __future__ import annotations

import math

SEED = 3.0                  # grain sown on a plot
RATIO = 3.0                 # harvest / seed on unbroken soil, fertility 1, no weeding (the old engine's mult)
UNITS_DAY = 6               # an adult's day (38.06 §3)

# the steps: units per plot per crop
SOW, REAP, REAP_BARE = 0.5, 1.5, 2.5            # reaping with a sickle (hand tool) or bare-handed
HOE, PLOUGH = 3.0, 0.75                          # breaking the soil by hand, or with an ox and a plough (8 plots an ox-day)
BREAK_GAIN = 1.5                                 # + harvest/seed from a broken seed bed
WEED_MAX, WEED_TAU = 0.5, 1.5                    # weeding: + up to 50% of the harvest, a saturating curve per plot
MANURE = 1.0                                     # units to spread a plot's manure (needs the dung: cattle)

# soil: fertility multiplies the harvest. A grain crop takes a share of it; legumes, fallow and dung restore it toward a level, in
# proportion to how far below it the soil is (so every rotation settles at its own level, not at a floor or a ceiling)
NATURAL = 1.0
TAKE = {"grain": 0.15, "legume": 0.0}
RESTORE = {"grain": (0.10, NATURAL), "legume": (0.40, NATURAL), "fallow": (0.40, NATURAL), "grazed fallow": (0.50, 1.15)}
MANURE_GAIN = (0.35, 1.15)                       # manure on a grain plot: restores 35% of the gap to 1.15
BLIGHT, BLIGHT_REPEAT = 0.05, 0.15               # a crop's chance of failing; higher when the plot grew the same crop last time
LEGUME_FOOD = 0.6                                # a legume crop's food, as a share of a grain crop's

# cattle (an ox: draught and dung)
OX_UPKEEP_DAY = 0.3                              # herding and winter hay, averaged over the year (ox_threshold's simple case)
HAY_DAY = 0.1                                    # winter hay per head, averaged over the year, in units
HERD_MIN, HERD_PER_HEAD = 1.0, 0.2               # watching animals: at least 1 unit a day for any herd; a herder (6) watches 30
OX_CAPITAL, OX_LIFE = 20.0, 5                    # units to raise one (bred from the herd), years of work
PLOUGH_CAPITAL, PLOUGH_LIFE = 6.0, 2
DUNG_PLOTS = 2.0                                 # plots one head manures a year (plus whatever grazes the fallow)


def weed_gain(units: float) -> float:
    return WEED_MAX * (1 - math.exp(-units / WEED_TAU))


def step(f: float, crop: str, manure: bool) -> float:
    f *= 1 - TAKE.get(crop, 0.0)
    r, level = RESTORE[crop]
    f += r * max(0.0, level - f)
    if manure and crop == "grain":
        f += MANURE_GAIN[0] * max(0.0, MANURE_GAIN[1] - f)
    return f


def mean_fertility_at_grain(rotation: list, manure: bool) -> float:
    """Fertility when grain is sown, once the rotation has settled (iterated from fresh land until it stops moving)."""
    f = 1.0
    for _ in range(300):
        for crop in rotation:
            f = step(f, crop, manure)
    seen = []
    for crop in rotation:
        if crop == "grain":
            seen.append(f)
        f = step(f, crop, manure)
    return sum(seen) / len(seen)


def crop(break_with=None, weed=0.0, manure=False, rotation=("grain",), tool=True, fresh=False) -> dict:
    """One rotation cycle on one plot, averaged per crop slot: units, net food, food per unit, food per plot-slot."""
    rotation = list(rotation)
    units = food = 0.0
    f_grain = 1.0 if fresh else mean_fertility_at_grain(rotation, manure)
    for i, c in enumerate(rotation):
        if c in ("fallow", "grazed fallow"):
            continue
        prev = rotation[i - 1] if len(rotation) > 1 else c
        fail = BLIGHT_REPEAT if prev == c else BLIGHT
        ratio = RATIO + (BREAK_GAIN if break_with else 0.0)
        harvest = SEED * ratio * (f_grain if c == "grain" else 1.0) * (1 + weed_gain(weed)) * (1 - fail)
        if c == "legume":
            harvest *= LEGUME_FOOD
        food += harvest - SEED
        units += SOW + (REAP if tool else REAP_BARE) + weed
        units += {None: 0.0, "hoe": HOE, "plough": PLOUGH}[break_with]
        if manure and c == "grain":
            units += MANURE
    slots = len(rotation)
    return {"units": units / slots, "food": food / slots, "per_unit": food / units if units else 0.0,
            "fert": f_grain}


def table(rows, head):
    w = [max(len(str(r[i])) for r in rows + [head]) for i in range(len(head))]
    line = lambda r: "| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(r)) + " |"
    return "\n".join([line(head), "|" + "|".join("-" * (x + 2) for x in w) + "|"] + [line(r) for r in rows])


RUNGS = [
    ("sow and reap, fresh land (the first years)", dict(fresh=True)),
    ("sow and reap, grain every time (worn soil)", dict()),
    ("sow and reap, grain then fallow", dict(rotation=("grain", "fallow"))),
    ("+ hoe", dict(break_with="hoe", rotation=("grain", "fallow"))),
    ("+ hoe + weeding (2 units)", dict(break_with="hoe", weed=2, rotation=("grain", "fallow"))),
    ("+ hoe + weeding, grain then legumes", dict(break_with="hoe", weed=2, rotation=("grain", "legume"))),
    ("ox plough + weeding, grain-legume-grazed fallow", dict(break_with="plough", weed=2,
                                                            rotation=("grain", "legume", "grazed fallow"))),
    ("ox plough + weeding + manure, grain-legume", dict(break_with="plough", weed=2, manure=True, rotation=("grain", "legume"))),
]


def ladder():
    rows = []
    for name, kw in RUNGS:
        r = crop(**kw)
        rows.append([name, f"{r['units']:.2f}", f"{r['food']:.2f}", f"{r['per_unit']:.2f}", f"{r['fert']:.2f}"])
    print("## The ladder: one plot, per crop slot (a slot is one crop's time on the plot, fallow included)\n")
    print(table(rows, ["method", "units a slot", "net food a slot (per plot)", "food per unit", "fertility at grain"]))


def dung_value() -> float:
    """Extra food a plot-slot gains from manure, net of the units to spread it (at 1 food a unit), on a grain-legume rotation."""
    a = crop(break_with="plough", weed=2, manure=True, rotation=("grain", "legume"))
    b = crop(break_with="plough", weed=2, rotation=("grain", "legume"))
    return (a["food"] - b["food"]) - (a["units"] - b["units"])


def ox_threshold():
    """How many plots an ox and plough must break a year before they beat the hoe, by crops a year."""
    print("\n## When the ox pays: plots it must work, against breaking the soil by hand\n")
    rows = []
    for year in (24, 40, 60):
        for slots_per_year in (1, 2, 3):
            cost = OX_UPKEEP_DAY * year + OX_CAPITAL / OX_LIFE + PLOUGH_CAPITAL / PLOUGH_LIFE
            save = (HOE - PLOUGH) * slots_per_year
            dung = DUNG_PLOTS * slots_per_year * dung_value()          # its dung: the manured plots' extra food, net of spreading
            rows.append([year, slots_per_year, f"{cost:.1f}", f"{save:.2f}", f"{cost / save:.1f}",
                         f"{(cost - dung) / save:.1f}"])
    print(table(rows, ["year (days)", "crops a plot a year", "ox + plough a year", "units saved a plot a year",
                       "plots to pay (draught only)", "plots to pay (with its dung)"]))


OX_PLOTS = 24                                    # plots one ox can break in a sowing window (8 an ox-day, 3 days)


def best_by_land(year=40, slots_per_year=2):
    """For land per person L (plots), the rung that feeds its people on that land with the fewest units per person a day,
    including cattle: hay, the ox's and plough's capital, and herding (any herd needs watching, at least HERD_MIN a day; one
    herder watches about 30 head), so a household of 4 keeps its own ox and a village of 20 shares a common herd."""
    print(f"\n## Which method is cheapest at a given land per person (year {year} days, {slots_per_year} crop slots a plot a year)\n")
    rows = []
    for land in (1.5, 2, 3, 5, 8, 12):
        row = [f"{land:g}"]
        for people in (4, 20):
            plots = people * land
            best = None
            for name, kw in RUNGS[1:]:                                   # fresh land excluded: it does not last
                r = crop(**kw)
                if r["food"] * slots_per_year * plots < people * year:
                    continue
                units = people * year / r["per_unit"]                    # a year's food for everyone
                if kw.get("break_with") == "plough" or "grazed fallow" in kw.get("rotation", ()) or kw.get("manure"):
                    oxen = max(1, math.ceil(plots / OX_PLOTS))
                    herding = max(HERD_MIN, HERD_PER_HEAD * oxen) * year
                    units += oxen * (HAY_DAY * year + OX_CAPITAL / OX_LIFE + PLOUGH_CAPITAL / PLOUGH_LIFE) + herding
                per_day = units / (people * year)
                if best is None or per_day < best[1]:
                    best = (name, per_day)
            row += [best[0] if best else "cannot feed itself", f"{best[1]:.2f}" if best else "-"]
        rows.append(row)
    print(table(rows, ["plots a person", "household of 4: cheapest", "units a person a day", "village of 20: cheapest",
                       "units a person a day"]))


def harvest_peak():
    """Plots a household can reap inside the window, all sown on one day or staggered."""
    print(f"\n## The harvest peak: plots a household can bring in before the crop rots (window 2 days, reaping {REAP:g} units a plot)\n")
    rows = []
    for adults in (1, 2, 4):
        for late in (0, 2):
            per_day = adults * (UNITS_DAY + late) / REAP
            rows.append([adults, f"+{late}" if late else "no", f"{per_day * 2:.0f}", f"{per_day * 2 * 3:.0f}"])
    print(table(rows, ["adults", "working late", "plots, sown on one day", "plots, sown on three days a window apart"]))


def scale_check(target_share=0.25):
    """The factor that puts the household rung (hoe + weeding, grain-fallow) at the target share of an adult's work."""
    r = crop(break_with="hoe", weed=2, rotation=("grain", "fallow"))
    need = 1.0 / UNITS_DAY                      # a ration a day, as a share of one adult's units, at 1 food a unit
    share = need / r["per_unit"]
    print(f"\nAt these numbers the household rung feeds a person with {share:.0%} of an adult's day (target about "
          f"{target_share:.0%} once seed, milling, storage, winter and children are added; scale RATIO to calibrate).")


if __name__ == "__main__":
    ladder()
    ox_threshold()
    best_by_land()
    best_by_land(slots_per_year=1)
    harvest_peak()
    scale_check()
