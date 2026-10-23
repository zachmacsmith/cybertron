"""Livestock numbers: kinds, breeding, fodder and land, work, products, herding, and what animals are worth. The model behind
docs/review/37_growth/02o_livestock.md.

Units are 38.06's work units (6 a day for an adult); 1 food is about 1 unit (02m's anchor: a coin about a food). The year is a
world setting (D4-13: 16-60 days); YEAR below. Decided in principle: D2-6, D2-18, D2-23, D2-41, D2-42, D2-45, D2-47. Every number
is a PROPOSAL from historical orders of magnitude, scaled to the compressed year; to calibrate in dry runs. Deterministic.
Run: python docs/review/37_growth/02o_livestock_model.py
"""
from __future__ import annotations

import math

DAY = 6
YEAR = 40                    # days a year (world setting)
WINTER = 0.25                # share of the year with no grazing

# ---------------------------------------------------------------- breeding (per year; historical medieval herds)
CATTLE = {"female share": 0.45, "births a female a year": 0.7, "young surviving": 0.85, "years to work or calve": 3,
          "working years": 8, "lifespan years": 12}
HORSES = {"female share": 0.45, "births a female a year": 0.5, "young surviving": 0.85, "years to work or calve": 4,
          "working years": 12, "lifespan years": 18}

# ---------------------------------------------------------------- fodder and land (a "plot" as in 02l; rescale with D4-23)
GRAZE_HEAD_PLOTS = 0.5       # pasture plots one head grazes through the growing season (2 head a plot)
HAY_HEAD_DAY = 1.0           # hay a head eats a winter day (1 hay = a head's winter day)
HAY_PER_PLOT = 12            # hay a meadow plot gives in one summer cut
HAY_UNITS = 1 / 3            # work to cut and stack a hay (02m: 1 unit cuts 3)
STALL_FACTOR = 0.8           # winter fodder in stalls (D2-45), out of the cold
STRAW_PER_PLOT_SLOT = 6      # straw from a grain crop on a plot (a by-product of reaping)
STRAW_AS_HAY = 0.4           # straw is poor fodder: 1 straw = 0.4 hay
GRAIN_PLOT_YEAR = 12         # net food a plot of grain gives a year on the household rung (02l: about 6 a slot, 2 slots)
HORSE_HAY = 1.2              # a horse eats more than a cow
HORSE_GRAIN_WORK = 1.0       # grain a horse eats on a working day (oats; historical: about a person's ration or more)
HORSE_GRAIN_IDLE = 0.2

# ---------------------------------------------------------------- work
TEAM = 2                     # oxen in a team (a light plough or a cart): a pair under a yoke
TEAM_PLOTS_DAY = 8           # plots a team and one ploughman break in a day (02l: 0.75 units a plot)
HOE_UNITS, PLOUGH_UNITS = 3.0, 0.75
TRAIN_OX_UNITS = 6           # a handler's work to yoke-train a steer (technique "yoke an ox"), over several days
BREAK_HORSE_UNITS = 12       # a horse breaker's work to break a horse to saddle (technique), over days
MOUNTED_STRENGTH = 3         # 02g §2b
RIDER_EDGES_DAY = 2.5        # on a track or road

# ---------------------------------------------------------------- products
MILK_FOOD_DAY = 0.8          # food a cow in milk gives a day (historical: 2-3 litres a day for a medieval cow)
LACTATION_SHARE = 0.6        # share of the year a cow is in milk after calving
MILK_UNITS_PER_COW = 1 / 3   # milking work a cow a day (a unit milks 3)
CHEESE_MILK_FOOD = 2.4       # food of milk into one cheese (6 milk at 0.4)
CHEESE_FOOD = 2.0            # food a cheese gives (whey drunk fresh)
SLAUGHTER = {"cow": (40, 2), "ox": (50, 2), "calf": (10, 1), "horse": (40, 2)}   # (meat, hides); meat feeds 1.5 (D2-41)
MEAT_FOOD = 1.5
DUNG_PLOTS_HEAD = 2.0        # plots a head's dung manures a year (02l)

# ---------------------------------------------------------------- herding (02l §5)
HERD_MIN, HERD_PER_HEAD = 1.0, 0.2


def table(rows, head):
    w = [max(len(str(r[i])) for r in rows + [head]) for i in range(len(head))]
    line = lambda r: "| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(r)) + " |"
    return "\n".join([line(head), "|" + "|".join("-" * (x + 2) for x in w) + "|"] + [line(r) for r in rows])


def growth(k: dict) -> float:
    births = k["female share"] * k["births a female a year"] * k["young surviving"]
    return births - 1 / k["lifespan years"]


def breeding():
    rows = []
    for name, k in (("cattle", CATTLE), ("horses", HORSES)):
        g = growth(k)
        rows.append([name, f"{g:.0%}", f"{g / YEAR:.2%}", f"{k['years to work or calve'] * YEAR}",
                     f"{(1 + g / YEAR) ** 25 - 1:.0%}", f"{20 * ((1 + g / YEAR) ** 25 - 1):.1f}"])
    print("## Breeding: a herd's growth, and what it means in a run\n")
    print(table(rows, ["kind", "growth a year (no slaughter)", "a day", "days to work or breed",
                       "growth in a 25-day run", "young in a run, herd of 20"]))
    print("\nNo animal born in a run grows up in it: herds and their ages are set by seeding; breeding matters across years.")


def land_and_fodder():
    winter_days = WINTER * YEAR
    rows = []
    for name, hay_day in (("cow or ox, outdoors", HAY_HEAD_DAY), ("cow or ox, in stalls", HAY_HEAD_DAY * STALL_FACTOR),
                          ("horse, in stalls", HORSE_HAY * STALL_FACTOR)):
        hay = hay_day * winter_days
        meadow = hay / HAY_PER_PLOT
        land = GRAZE_HEAD_PLOTS + meadow
        rows.append([name, f"{hay:.0f}", f"{hay * HAY_UNITS:.1f}", f"{meadow:.2f}", f"{land:.2f}",
                     f"{land * GRAIN_PLOT_YEAR:.0f}"])
    print("\n## Fodder and land a head (a year)\n")
    print(table(rows, ["animal", "winter hay", "units to cut it", "meadow plots", "land in all (plots)",
                       "grain given up if land is short (food)"]))
    straw = STRAW_PER_PLOT_SLOT * 2 * STRAW_AS_HAY
    print(f"\nStraw: a grain plot gives about {straw:.1f} hay-equivalent a year, so about {winter_days * STALL_FACTOR / straw:.1f} "
          "grain plots' straw winters one stalled head: mixed farms need less meadow.")


def upkeep(alone: bool, land_short: bool, kind="cattle") -> float:
    """Units a head a year: hay cutting, herding, and (where land is short) the grain its land could have grown."""
    winter_days = WINTER * YEAR
    hay = (HORSE_HAY if kind == "horse" else HAY_HEAD_DAY) * STALL_FACTOR * winter_days
    herd = HERD_MIN * YEAR if alone else HERD_PER_HEAD * YEAR
    land = (GRAZE_HEAD_PLOTS + hay / HAY_PER_PLOT) * GRAIN_PLOT_YEAR if land_short else 0.0
    grain = HORSE_GRAIN_IDLE * YEAR * 0.59 if kind == "horse" else 0.0     # 0.59 units a grain (02m)
    return hay * HAY_UNITS + herd + land + grain


def values():
    """What an animal costs to raise to working age, its yearly upkeep, and what it yields: a price range."""
    rows = []
    for name, kind, years, train in (("ox (trained)", "cattle", 3, TRAIN_OX_UNITS), ("cow (first calf)", "cattle", 3, 0),
                                     ("horse (broken)", "horse", 4, BREAK_HORSE_UNITS)):
        for land_short in (False, True):
            u = upkeep(alone=False, land_short=land_short, kind=kind)
            raise_cost = years * u * 0.6 + train          # a young beast eats and needs watching about 0.6 of an adult
            rows.append([name, "short" if land_short else "plentiful", f"{u:.0f}", f"{raise_cost:.0f}"])
    print("\n## Upkeep and raising (common herd; land plentiful or short)\n")
    print(table(rows, ["animal", "land", "upkeep a year", "cost to raise to work"]))
    milk = MILK_FOOD_DAY * LACTATION_SHARE * YEAR
    calf = CATTLE["births a female a year"] * CATTLE["young surviving"]
    print(f"\nA cow a year: about {milk:.0f} food of milk (for {MILK_UNITS_PER_COW * LACTATION_SHARE * YEAR:.0f} units of milking), "
          f"{calf:.2f} calves, dung for {DUNG_PLOTS_HEAD:g} plots. Slaughtered: {SLAUGHTER['cow'][0]} meat "
          f"({SLAUGHTER['cow'][0] * MEAT_FOOD:.0f} food, most of it lost unless salted or eaten at once) and {SLAUGHTER['cow'][1]} hides.")
    print(f"Milk over a cow's {CATTLE['working years']} working years: about {milk * CATTLE['working years']:.0f} food against "
          f"{SLAUGHTER['cow'][0] * MEAT_FOOD:.0f} for its meat now: keeping pays, eating the herd is a famine's choice.")
    print(f"Cheese keeps {CHEESE_FOOD / CHEESE_MILK_FOOD:.0%} of the milk's food and keeps for weeks: a summer's surplus milk becomes winter food.")


def ox_team():
    """When a team of two oxen and a plough pays against the hoe, a household's own against a common herd's."""
    rows = []
    for alone in (True, False):
        for land_short in (False, True):
            u = TEAM * upkeep(alone=alone, land_short=land_short)
            if alone:
                u -= (TEAM - 1) * HERD_MIN * YEAR      # one minder watches both
            capital = TEAM * (3 * upkeep(False, land_short) * 0.6 + TRAIN_OX_UNITS) / CATTLE["working years"]
            plough = 15.3 / 3 + 2 * 4.3 / 2              # 02m: plough over 3 years, two harnesses over 2
            cost = u + capital + plough
            for slots in (1, 2):
                save = (HOE_UNITS - PLOUGH_UNITS) * slots
                dung = TEAM * DUNG_PLOTS_HEAD * slots * 1.5            # about 1.5 food a manured plot-slot (02l)
                rows.append(["own team" if alone else "in a common herd", "short" if land_short else "plentiful", slots,
                             f"{cost:.0f}", f"{(cost - dung) / save:.0f}"])
    print("\n## A team of two oxen: plots it must break a year to beat the hoe (40-day year)\n")
    print(table(rows, ["kept", "land", "crops a plot a year", "team's cost a year", "plots to pay"]))
    print(f"\nA team breaks {TEAM_PLOTS_DAY} plots a day, so even 40 plots take 5 days: one team serves a village.")


def horses():
    work_days = 0.3 * YEAR
    u = upkeep(False, True, "horse") + HORSE_GRAIN_WORK * work_days * 0.59
    print("\n## Horses\n")
    print(f"- Upkeep a year, worked about {work_days:.0f} days, land short: about {u:.0f} units (grain on working days alone "
          f"{HORSE_GRAIN_WORK * work_days:.0f} food: horses eat what people eat).")
    print(f"- A rider covers about {RIDER_EDGES_DAY:g} edges a day (on foot 1) and fights at +{MOUNTED_STRENGTH} (02g §2b).")
    print(f"- A troop of 10 riders costs about {10 * u:.0f} units a year: the work of about {10 * u / (DAY * YEAR):.1f} full-time "
          "adults, before saddles and blades: cavalry is a society's, not a household's.")


def check_02l_02m():
    old = 0.3 * YEAR + 20 / 5 + 6 / 2
    new_low = TEAM * upkeep(False, False) + TEAM * (3 * upkeep(False, False) * 0.6 + TRAIN_OX_UNITS) / 8 + 15.3 / 3 + 4.3
    new_high = TEAM * upkeep(False, True) + TEAM * (3 * upkeep(False, True) * 0.6 + TRAIN_OX_UNITS) / 8 + 15.3 / 3 + 4.3
    print("\n## Against 02l and 02m\n")
    print(f"- 02l priced one ox and a plough at about {old:.0f} units a year, with no land and a 20-unit ox. A team of two in a "
          f"common herd costs about {new_low:.0f} with land plentiful and {new_high:.0f} with land short.")
    print("- So 02l's thresholds rise: with land short, a team pays only for a village's ploughing (tens of plots), never for a "
          "household's few. That strengthens 02l's result (the common herd and the shared team) rather than reversing it.")
    print("- 02m's worth table: 'plough and ox' should be a team at the costs above; 'cart' should carry its team (about the same "
          "again); 02g's ox cart (capital 80, fodder only) understates the team by a factor of about 2-3, so its break-even "
          "traffic rises.")


if __name__ == "__main__":
    breeding()
    land_and_fodder()
    values()
    ox_team()
    horses()
    check_02l_02m()
