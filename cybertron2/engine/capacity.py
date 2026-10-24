"""What a node keeps for good (D2-161; 02za's method): the people its land feeds and its woods keep warm each year from their flows,
not their stocks; worlds are seeded at about 60 to 70% of the scarcest. Used by the capacity check (review 38.21) and world design.
"""
from __future__ import annotations

from cybertron2.engine.data import FORESTS

PLOT = {"grain": 64, "seed": 16}          # a plot of size 1 broken and weeded: about 64 grain a year from 16 seed (02l, D4-38)
WILD = 10                                 # food a year a unit of forest or scrub, forage and game (02za)
PEOPLE_A_HEARTH = 4.5
FIREWOOD_HEAT = 0.5


def hearth_heat(w) -> float:
    """Heat a hearth needs in a year: normal nights at 1, the season's cold nights at 4 (D2-157)."""
    year = w.year_days()
    cold = w.season_len                                                          # winter's nights
    return (year - cold) * float(w.p["heat"]["normal"]) + cold * float(w.p["heat"]["cold"])


def wood_flow(par) -> float:
    """Firewood a year a parcel's woods give without running down: what its trees shed, and its young growth's best regrowth (02z)."""
    res = par["res"]
    out = 0.0
    t = res.get("wood")
    if t and t["K"] > 0:
        out += FORESTS["shed"] * t["S"] * FORESTS["per_timber"]
    y = res.get("young")
    if y and y["K"] > 0:
        out += y["r"] * 24.0 * y["K"] / 4.0
    return out


def node(w, nid) -> dict:
    """{food, heat, food_people, heat_people, people, binds} for a node, a year."""
    pars = [p for p in w.s["parcels"].values() if p["node"] == nid]
    fields = sum(p["size"] for p in pars if p["cover"] == "field")
    woods = sum(p["size"] for p in pars if p["cover"] in ("forest", "scrub"))
    food = fields * (PLOT["grain"] - PLOT["seed"]) + woods * WILD
    heat = sum(wood_flow(p) for p in pars) * FIREWOOD_HEAT
    year = w.year_days()
    fp = food / year
    hp = heat / hearth_heat(w) * PEOPLE_A_HEARTH
    people = sum(1 for a in w.s["people"].values() if a["alive"] and a["at"] == nid)
    return {"food": round(food, 1), "heat": round(heat, 1), "food_people": round(fp, 1), "heat_people": round(hp, 1), "people": people,
            "binds": "fuel" if hp < fp else "food", "keeps": round(min(fp, hp), 1)}
