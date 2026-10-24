"""Forests and fuel (spec/environment/resources.md "Forests", economy/goods.md "Fuel, in heat", economy/lodging.md "Shelter and
fire": D2-156, D2-157, D2-159). Engine side.

A forest or scrub parcel holds three stocks: its trees (`wood`, in timber), young growth (`young`) and dead wood (`dead`), both in
firewood. The trees grow slowly toward their capacity and shed dead wood in proportion to their number; felling takes trees and
leaves brash as dead wood; young growth regrows fast but not while beasts are on the parcel; dead wood rots. Under 40% of its trees
a forest's cover turns to scrub. Fuel is counted in heat: timber 2, firewood 0.5, charcoal 6; a fire draws by the household's order.
"""
from __future__ import annotations

from cybertron2.engine.data import FORESTS, ITEMS

KINDS = FORESTS["kinds"]


# ---------------------------------------------------------------------- seeding
def seed(cover: str, size: int, state: dict) -> dict:
    """The forest stocks for a parcel from its world-file state: `wood: {kind, trees?: share standing, young?, dead?: shares}`, or an
    older world's `wood: {S, K, r}` read as its trees (young growth and dead wood in a copse's proportions); scrub with no wood
    state gets scrub's. Returns {key: {S, K, r, ...}} to merge into the parcel's resources."""
    w = state.get("wood")
    out = {}
    year = 24.0
    if isinstance(w, dict) and w.get("kind"):
        k = KINDS[w["kind"]]
        if k["trees"]:
            K = k["trees"] * size
            out["wood"] = {"S": round(K * float(w.get("trees", 1.0)), 4), "K": float(K), "r": k["grow"] / year, "kind": w["kind"]}
        for key in ("young", "dead"):
            K = k[key] * size
            out[key] = {"S": round(K * float(w.get(key, 1.0)), 4), "K": float(K), "r": k["regrow"] / year if key == "young" else 0.0}
        return out
    if isinstance(w, dict) and "K" in w:                                       # an older world: its trees as given
        c = KINDS["copse"]
        K = float(w["K"])
        out["young"] = {"S": round(K * c["young"] / c["trees"], 4), "K": round(K * c["young"] / c["trees"], 4), "r": c["regrow"] / year}
        out["dead"] = {"S": round(K * c["dead"] / c["trees"], 4), "K": round(K * c["dead"] / c["trees"], 4), "r": 0.0}
        return out
    if cover == "scrub":
        k = KINDS["scrub"]
        out["young"] = {"S": float(k["young"] * size), "K": float(k["young"] * size), "r": k["regrow"] / year}
        out["dead"] = {"S": float(k["dead"] * size), "K": float(k["dead"] * size), "r": 0.0}
    return out


# ---------------------------------------------------------------------- the night
def night(w) -> list:
    """Each night: trees grow, young growth regrows where no beasts are, trees shed dead wood and it rots, a gale throws trees; a
    forest thinned under 40% of its trees turns to scrub (and back above it). Returns the parcels whose cover changed."""
    year = float(w.year_days())
    winter = w.calendar()["season"] == "winter"
    slow = float(w.p["regrow_winter"]) if winter else 1.0
    from cybertron2.engine import environment as EV
    gale = EV.weather(w) == "gale"
    grazed = {h.get("parcel") for h in w.s["herds"].values() if h.get("count", 0) > 0}
    changed = []
    for pid, par in w.s["parcels"].items():
        res = par["res"]
        t, y, d = res.get("wood"), res.get("young"), res.get("dead")
        if t and t["K"] > 0:
            t["S"] = round(min(t["K"], t["S"] + t["r"] * slow * t["S"] * (1 - t["S"] / t["K"])), 4)
        if y and y["K"] > 0 and pid not in grazed:
            y["S"] = round(min(y["K"], y["S"] + y["r"] * slow * max(y["S"], 0.05 * y["K"]) * (1 - y["S"] / y["K"])), 4)
        if d is not None:
            shed = FORESTS["shed"] / year * (t["S"] if t else 0.0) * FORESTS["per_timber"]
            d["S"] = round(max(0.0, d["S"] + shed - FORESTS["rot"] / year * d["S"]), 4)
            if t and gale:
                down = t["S"] * FORESTS["gale"]
                t["S"] = round(t["S"] - down, 4)
                d["S"] = round(d["S"] + down * FORESTS["per_timber"], 4)
            d["K"] = max(d["K"], d["S"])
        if t and t["K"] > 0 and par["cover"] in ("forest", "scrub") and t.get("kind") != "scrub":
            share = t["S"] / t["K"]
            if par["cover"] == "forest" and share < FORESTS["scrub_below"]:
                par["cover"], par["was"] = "scrub", "forest"
                changed.append(pid)
            elif par["cover"] == "scrub" and par.get("was") == "forest" and share >= FORESTS["scrub_below"] + 0.05:
                par["cover"] = "forest"
                changed.append(pid)
    return changed


def brash(w, parcel, timber) -> None:
    """Felling leaves its branches as dead wood: 1 firewood a timber (D2-156)."""
    d = w.s["parcels"][parcel]["res"].get("dead")
    if d is not None and timber > 0:
        d["S"] = round(d["S"] + float(FORESTS["brash"]) * timber, 4)
        d["K"] = max(d["K"], d["S"])


# ---------------------------------------------------------------------- fuel in heat
def heat_of(goods: dict, order=None) -> float:
    return sum(float(goods.get(i, 0.0)) * float(ITEMS[i]["heat"]) for i in (order or fuel_order()) if i in ITEMS)


def fuel_order() -> list:
    from cybertron2.engine.data import PHYSICS
    return list(PHYSICS["heat"]["order"])


def burn(w, place, cid, heat, why="fire", order=None) -> float:
    """Burn fuel from a container for `heat`, by the order (firewood, then timber, then charcoal: D2-157); all or nothing. Returns
    the heat got (0 if there was not enough)."""
    g = w.goods(cid)
    order = order or fuel_order()
    if heat_of(g, order) + 1e-9 < heat:
        return 0.0
    left = heat
    for item in order:
        if left <= 1e-9:
            break
        h = float(ITEMS[item]["heat"])
        q = min(g.get(item, 0.0), left / h)
        if q > 1e-9:
            w.apply("destroy", place, src=cid, item=item, qty=round(q, 6), why=why)
            left -= q * h
    return heat


def fuel_words(heat) -> str:
    """'2 firewood or 0.5 timber': what a heat takes, in the cheap fuels."""
    return " or ".join(f"{float(heat) / float(ITEMS[i]['heat']):g} {i}" for i in ("firewood", "timber"))
