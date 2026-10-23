"""The night (spec/core/round.md): fights, departures, where each sleeps, fires, eating, the cold, deaths, spoilage, breaks, growth
and crops, offers lapsing. Each node on its own (D4-35); travellers on the road sleep out and eat what they carry (D4-12).

Where one sleeps: where one chose to (`sleep`), if one can get in and a bed is free; else one's home here (D4-36); else a building
one has been given access to (a host: 05 §3), if a bed is free; else out. What one eats: what one carries, then the stores here one
may take from, the one slept in first (38.17 §9: to confirm).
"""
from __future__ import annotations

from cybertron2.engine.data import EDIBLE, ITEMS
from cybertron2.engine.world import Refused


def night(w) -> dict:
    s, p = w.s, w.p
    today = s.get("today") or {}
    cold = w.cold()
    rec = {"day": w.d, "cold": cold, "ate": {}, "short": [], "missed": [], "deaths": [], "cold_falls": [], "breaks": [], "hearth": {},
           "spoiled": {}, "fights": [], "departed": [], "slept": {}}
    from cybertron2.engine import settle as ST
    rec["fights"] = ST.settle_fights(w, today)
    rec["deaths"] += [f["killed"] for f in rec["fights"] if f.get("killed")]
    for name, to in sorted((today.get("travel") or {}).items()):              # departures at nightfall (D4-8)
        a = s["people"][name]
        if a["alive"] and a["at"] is not None:
            here = a["at"]
            road = next(r for r, x in s["roads"].items() if {x["a"], x["b"]} == {here, to})
            homes = w.homes(name)
            h = next((b for b in homes if s["buildings"][b]["node"] == here), None)
            if h:                                                            # the house as last seen (D4-35: not watched from afar)
                a["home_seen"] = {"day": w.d, "building": h, "stock": dict(w.goods(s["buildings"][h]["stock"])),
                                  "condition": s["buildings"][h]["condition"], "door": s["buildings"][h]["door"]}
            w.apply("depart", here, person=name, road=road, to=to)
            rec["departed"].append({"agent": name, "from": here, "to": to})
    where = sleeping_places(w, today)
    rec["slept"] = {n: (s["buildings"][b]["name"] if b else "out") for n, b in where.items()}
    fuel = float(p["fuel"]["cold" if cold else "normal"])
    for bid, b in s["buildings"].items():
        sleepers = [n for n, x in where.items() if x == bid]
        lit = False
        if sleepers and b["fittings"].get("hearth"):
            g = w.goods(b["stock"])
            if g.get("timber", 0.0) + 1e-9 >= fuel:
                w.apply("destroy", b["node"], src=b["stock"], item="timber", qty=fuel, why="fire")
                lit = True
        w.apply("set", b["node"], ref=("building", bid), field="fire", value=lit)
        if sleepers:
            rec["hearth"][bid] = {"sleepers": len(sleepers), "lit": lit}
    for name in w.living():
        a = s["people"][name]
        bid = where.get(name)
        b = s["buildings"][bid] if bid else None
        state = "unsheltered" if b is None or b["condition"] == 0 else ("damaged" if b["condition"] == 1 else "housed")
        if cold and state == "housed" and not b["fire"]:
            state = "no_fuel"
        need = float(p["ration"]) * float((p["shelter_cold"] if cold else p["shelter"]).get(state, 1.0))
        place = w.place_of(("person", name))
        stores = [a["hands"]]
        if place in s["nodes"]:
            mine = w.takeable(name, place)
            stores += sorted((c for c in mine if c != a["hands"]), key=lambda c: 0 if b is not None and c == b["stock"] else 1)
        ate = _eat(w, place, stores, need)
        if ate + 1e-9 >= need:
            a["hunger"], a["missed"] = min(0, a["hunger"] + 1), 0
            rec["ate"][name] = round(ate, 2)
        elif ate + 1e-9 >= float(p["ration"]):
            a["missed"] = 0
            rec["short"].append(name)
            rec["ate"][name] = round(ate, 2)
        else:
            a["hunger"], a["missed"] = max(-2, a["hunger"] - 1), a["missed"] + 1
            rec["missed"].append(name)
            if ate:
                rec["ate"][name] = round(ate, 2)
        if cold and state == "unsheltered" and w.rng("cold", w.d, name).random() < float(p["cold_starving"]):
            a["hunger"] = -2
            rec["cold_falls"].append(name)
    if w.d < w.days - 1:
        for name in w.living():
            a = s["people"][name]
            if a["missed"] >= 3:
                k = a["missed"] - 2
                hz = min(1.0, a["frailty"] + float(p["hazard"]["step"]) * (k - 1))
                if w.rng("hazard", w.d, name).random() < hz or k >= int(p["hazard"]["max_rounds"]):
                    place = w.place_of(("person", name))
                    w.apply("die", place, person=name, cause="starvation")
                    rec["deaths"].append(name)
                    if place in s["nodes"]:
                        w.event(place, "death", f"{name} died in the night, of hunger", target=name, salience=1.0, tags=["death", "food"])
    for cid, c in s["containers"].items():                                    # spoilage
        if c["kind"] == "stock":
            bb = s["buildings"][c["of"]]
            mult = float(p["house_spoil"]) * (float(p["cellar_spoil"]) if bb["fittings"].get("cellar") else 1.0)
        else:
            mult = 1.0
        if c["kind"] == "hands" and not s["people"][c["of"]]["alive"]:
            continue
        for item, q in list(c["goods"].items()):
            r = ITEMS.get(item, {}).get("spoil", 0.0) * mult
            if q > 1e-9 and r > 0:
                place = w.place_of(("container", cid))
                lost = w.apply("destroy", place, src=cid, item=item, qty=round(q * r, 6), why="spoilt")
                rec["spoiled"][item] = round(rec["spoiled"].get(item, 0.0) + lost, 4)
    for bid, b in s["buildings"].items():                                       # breaks (H-5)
        q = float(p["breaks"]["cold" if cold else "p"])
        if not b.get("unfinished") and b["condition"] > 0 and w.rng("break", w.d, bid).random() < q:
            w.apply("set", b["node"], ref=("building", bid), field="condition", value=b["condition"] - 1)
            rec["breaks"].append(bid)
    _grow(w)
    for oid, o in s["offers"].items():                                          # offers lapse (money_and_markets.md)
        if not o["open"]:
            continue
        gone = s["people"][o["by"]]["at"] != o["node"] or not s["people"][o["by"]]["alive"]
        if gone or (o.get("until") is not None and o["until"] <= w.d):         # to a person: at nightfall; to anyone: while
            o["open"] = False                                                  # the offerer stays, or until its day
    s["log"].append(rec)
    return rec


def sleeping_places(w, today) -> dict:
    """{name: building id or None}: members at home always; others need a free bed (05 §3)."""
    s = w.s
    out, beds_used = {}, {}
    chosen = today.get("sleep") or {}
    living = w.living()
    for name in living:                                                         # members sleep at home
        a = s["people"][name]
        if a["at"] is None or name in (today.get("travel") or {}):
            out[name] = None
            continue
        if name in chosen:
            continue
        home = next((b for b in w.homes(name) if s["buildings"][b]["node"] == a["at"]), None)
        if home:
            out[name] = home
            beds_used[home] = beds_used.get(home, 0) + 1
    for name in living:                                                         # then guests and those who chose a place
        if name in out:
            continue
        a = s["people"][name]
        cands = []
        if name in chosen:
            cands.append(chosen[name])
        cands += [bid for bid, b in s["buildings"].items() if b["node"] == a["at"] and not b.get("unfinished")
                  and "access" in w.rights(name, ("building", bid)) and bid not in cands]
        out[name] = None
        for bid in cands:
            b = s["buildings"][bid]
            if b.get("unfinished") or not w.can_enter(name, bid):
                continue
            free = int(b["fittings"].get("beds", 0)) - beds_used.get(bid, 0)
            if free > 0:
                out[name] = bid
                beds_used[bid] = beds_used.get(bid, 0) + 1
                break
    return out


def _eat(w, place, stores, need) -> float:
    """Up to `need` in food value, from the stores in order, most perishable first."""
    got = 0.0
    for cid in stores:
        g = w.goods(cid)
        for item in sorted(EDIBLE, key=lambda i: -ITEMS[i]["spoil"]):
            v = ITEMS[item]["food"]
            if got + 1e-9 < need and g.get(item, 0.0) > 1e-9:
                q = min(g[item], (need - got) / v)
                got += w.apply("destroy", place, src=cid, item=item, qty=q, why="eaten") * v
    return round(got, 6)


def _grow(w):
    """Resources come back by regime (D4-7); crops ripen from the sowing day and rot after the window (D2-12)."""
    winter = w.calendar()["season"] == "winter"
    p = w.p
    for pid, par in w.s["parcels"].items():
        for key, r in par["res"].items():
            reg = {"plants": "fast", "game": "threshold", "wood": "slow"}.get(key)
            if not reg or r["K"] <= 0:
                continue
            if reg == "threshold" and r["S"] < float(p["game_threshold"]) * r["K"]:
                continue
            rate = r["r"] * (float(p["regrow_winter"]) if winter else 1.0)
            r["S"] = round(min(r["K"], r["S"] + rate * r["S"] * (1 - r["S"] / r["K"]) + (0.01 * (r["K"] - r["S"]) if reg == "fast" else 0)), 4)
        c = par.get("crop")
        if c and c.get("left", 0) > 1e-9:
            ripe = int(c.get("ripe_day", 0))
            window = int(c.get("window", p["farming"]["window"]))
            if w.d >= ripe + window:
                c["left"] = round(c["left"] * (1 - float(p["farming"]["rot"])), 4)
                c["rotting"] = True
