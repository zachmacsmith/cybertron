"""The night (spec/core/round.md): fights, departures, where each sleeps, fires, eating, the cold, deaths, spoilage, breaks, growth
and crops, offers lapsing. Each node on its own (D4-35); travellers on the road sleep out and eat what they carry (D4-12).

Where one sleeps: where one chose to (`sleep`), if one can get in and a bed is free; else one's home here (D4-36); else a building
one has been given access to (a host: 05 §3), if a bed is free; else out. What one eats: what one carries, then the stores here one
may take from, the one slept in first (38.17 §9: to confirm).
"""
from __future__ import annotations

from cybertron2.engine import life as LF
from cybertron2.engine.data import DECAY, EDIBLE, FITTINGS, ITEMS, THINGS

FIRE = tuple(f for f, d in FITTINGS.items() if d.get("fire"))
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
    rec["departed"] = today["_departed"] if "_departed" in today else departures(w, today)
    where = sleeping_places(w, today)
    rec["slept"] = {n: (s["buildings"][b]["name"] if b else "out") for n, b in where.items()}
    from cybertron2.engine import forests as FO
    hp = p["heat"]
    for bid, b in s["buildings"].items():                                     # fires in heat (D2-157, D2-159)
        sleepers = [n for n, x in where.items() if x == bid]
        lit, warm = False, 0.0
        if sleepers and any(b["fittings"].get(f_) for f_ in FIRE):
            hearths, rings = int(b["fittings"].get("hearth") or 0), int(b["fittings"].get("fire ring") or 0)
            if b["structure"] == "camp":                                      # a camp's fire (D4-49)
                heat = float(hp["camp"])
            else:
                heat = float(hp["cold" if cold else "normal"]) * max(1, hearths + rings)
            if FO.burn(w, b["node"], b["stock"], heat):
                lit = True
                spaces = float(hp["hearth_spaces"]) * hearths + float(hp["ring_spaces"]) * rings
                warm = 1.0 if b["structure"] == "camp" else min(1.0, spaces / max(1.0, float(b.get("size") or 1)))
                if not hearths and b["structure"] != "camp":
                    warm = min(warm, 0.5)                                     # a fire ring half-warms a house in the cold
        w.apply("set", b["node"], ref=("building", bid), field="fire", value=lit)
        w.apply("set", b["node"], ref=("building", bid), field="warm", value=warm)
        if sleepers:
            rec["hearth"][bid] = {"sleepers": len(sleepers), "lit": lit, "warm": round(warm, 2)}
    fires = open_fires(w, today, where, rec)                                  # fires in the open, shared by 4 (D2-159)
    tents = {}                                                                  # a tent sleeps two (D2-68): who shares whose
    for name in w.living():
        a = s["people"][name]
        bid = where.get(name)
        b = s["buildings"][bid] if bid else None
        state = "unsheltered" if b is None or b["condition"] == 0 else ("damaged" if b["condition"] == 1 else "housed")
        if cold and state == "housed" and not b["fire"]:
            state = "no_fuel"
        need = float(p["ration"]) * float((p["shelter_cold"] if cold else p["shelter"]).get(state, 1.0))
        if cold and state == "housed" and b["structure"] != "camp" and b.get("warm", 1.0) < 1.0:   # partly warmed (D2-159)
            ww = b.get("warm", 1.0)
            if not b["fittings"].get("hearth"):
                need = float(p["ration"]) * float(hp["ring_cold"])
            else:
                need = float(p["ration"]) * (ww + float(p["shelter_cold"]["no_fuel"]) * (1 - ww))
        fall = 1.0
        gear = None
        if state == "housed" and b["structure"] == "camp":                     # a camp (D2-68)
            gear = "camp"
        elif state == "unsheltered":                                            # out, with what one carries (D2-68)
            gear = _gear(w, name, where, tents)
        road = today.get("road") or {}
        if state == "unsheltered" and name in (road.get("camp") or {}):         # stopped at a good place: as in a camp (D2-109)
            gear = gear or "camp"
        if gear:
            out_ = p["camping"][gear]
            need = float(p["ration"]) * float(out_[1] if cold else out_[0])
            fall = float(out_[2])
            if cold and name in fires and gear != "camp":                    # a fire in the open warms (D2-159)
                need, fall = float(p["ration"]) * float(p["camping_fire"].get(gear, out_[1])), 0.0
            if gear == "camp" and cold and b is not None and not b["fire"]:
                need, fall = float(p["ration"]) * float(p["camping"]["out"][1]), 0.0
            rec.setdefault("camped", {})[name] = gear
        if state == "unsheltered" and name in (road.get("fed") or {}):          # fed on the way at a good place (D2-109)
            need = min(need, float(p["ration"]) * float(road["fed"][name]))
        mult, extra = LF.ration_factor(w, name)                                 # an infant, a child, a pregnancy (D2-141, D2-145)
        need = need * mult + extra
        place = w.place_of(("person", name))
        stores = [a["hands"]]
        if place in s["nodes"]:
            mine = w.takeable(name, place)
            stores += sorted((c for c in mine if c != a["hands"]), key=lambda c: 0 if b is not None and c == b["stock"] else 1)
        if a["stage"] in LF.MINOR:                                             # then from its carers' hands (D2-141)
            stores += [w.hands(x) for x in LF.feeders(w, name) if w.hands(x) not in stores]
        hearth = b is not None and any(b["fittings"].get(f_) for f_ in FIRE) and bool(b["fire"])   # grain boiled at a lit fire (D2-60)
        if state == "unsheltered" and name in fires:                          # at a fire in the open (D4-49, D2-159)
            hearth = True
        rawf = sorted({i for cid in stores for i, q in w.goods(cid).items() if q > 1e-9 and ITEMS.get(i, {}).get("cook")}) if not hearth else []
        ate = _eat(w, place, stores, need, hearth)
        if rawf and ate + 1e-9 < need:                                         # food that wants a fire, eaten raw or not (D2-160)
            rec.setdefault("uncooked", {})[name] = rawf
        me = ("person", name)
        if rawf and ate > 1e-9:
            w.apply("set", place, ref=me, field="ate_raw", value=w.d)        # seen on them tomorrow (signs.PERSON)
        full = float(p["ration"]) * mult + extra                                # a short meal is a ration's worth at least
        if ate + 1e-9 >= need:
            w.apply("harm", place, person=name, hunger=min(0, a["hunger"] + 1))
            w.apply("set", place, ref=me, field="missed", value=0)
            rec["ate"][name] = round(ate, 2)
        elif ate + 1e-9 >= full:
            w.apply("set", place, ref=me, field="missed", value=0)
            rec["short"].append(name)
            rec["ate"][name] = round(ate, 2)
        else:
            w.apply("harm", place, person=name, hunger=max(-2, a["hunger"] - 1))
            w.apply("set", place, ref=me, field="missed", value=a["missed"] + 1)
            rec["missed"].append(name)
            if ate:
                rec["ate"][name] = round(ate, 2)
        soaked = name in (today.get("soaked") or [])                           # soaked at a ford: the cold's fall (world/roads.md)
        if (cold or soaked) and state == "unsheltered" and w.rng("cold", w.d, name).random() < float(p["cold_starving"]) * max(fall, 0.5 if soaked else 0):
            w.apply("harm", place, person=name, hunger=-2)
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
    rec["life"] = LF.night(w, today, rec, where)                              # conception, births, the young, old age (D2-138 to D2-150)
    rec["deaths"] += rec["life"]["deaths"] + rec["life"]["old_age"]
    for cid, c in list(s["containers"].items()):                              # spoilage, by condition (D2-58, D2-87)
        if c["kind"] == "hands" and not s["people"][c["of"]]["alive"]:
            continue
        for item, q in list(c["goods"].items()):
            if c["kind"] == "carcass" and item == "meat":                      # a dead beast's meat keeps a day, then goes off (D4-52)
                if q > 1e-9 and w.d - int(c.get("died", w.d)) >= int(THINGS["carcass_fresh_days"]):
                    place = w.place_of(("container", cid))
                    w.apply("destroy", place, src=cid, item="meat", qty=q, why="went off")
                    w.apply("create", place, dst=cid, item="rotting meat", qty=q, why="rot")
                continue
            r, becomes = decay_rate(w, c, item)
            if q > 1e-9 and r > 0:
                place = w.place_of(("container", cid))
                lost = w.apply("destroy", place, src=cid, item=item, qty=round(q * min(1.0, r), 6), why="spoilt")
                rec["spoiled"][item] = round(rec["spoiled"].get(item, 0.0) + lost, 4)
                if becomes and lost > 1e-9:
                    w.apply("create", place, dst=cid, item=becomes, qty=lost, why="rot")
    for bid, b in s["buildings"].items():                                       # a camp falls in after its nights (D2-68)
        if b.get("lasts_until") is not None and w.d >= b["lasts_until"] and b["condition"] > 0:
            w.apply("set", b["node"], ref=("building", bid), field="condition", value=0)
            w.event(b["node"], "build", f"{b['name']} has fallen in", about=[f"building:{bid}"], salience=0.3, tags=["shelter"])
    for bid, b in s["buildings"].items():                                       # breaks (H-5)
        q = float(p["breaks"]["cold" if cold else "p"])
        if not b.get("unfinished") and b["condition"] > 0 and w.rng("break", w.d, bid).random() < q:
            w.apply("set", b["node"], ref=("building", bid), field="condition", value=b["condition"] - 1)
            rec["breaks"].append(bid)
    _grow(w)
    from cybertron2.engine import farm as FM
    rec["farm"] = FM.night(w)
    for oid, o in s["offers"].items():                                          # offers lapse (money_and_markets.md)
        if not o["open"]:
            continue
        gone = s["people"][o["by"]]["at"] != o["node"] or not s["people"][o["by"]]["alive"]
        if gone or (o.get("until") is not None and o["until"] <= w.d):         # to a person: at nightfall; to anyone: while
            w.apply("close_offer", o["node"], offer=oid, why="lapsed")        # the offerer stays, or until its day
    s["log"].append(rec)
    return rec


def departures(w, today) -> list:
    """Departures at nightfall (D4-8), with the traveller's choices for the road (world/roads.md, D2-105). Run before the roads'
    night and the fuse sub-step, so those leaving tonight are on their first stretch."""
    s = w.s
    out = []
    for name, to in sorted((today.get("travel") or {}).items()):
        a = s["people"][name]
        if a["alive"] and a["at"] is not None:
            here = a["at"]
            road = next(r for r, x in s["roads"].items() if {x["a"], x["b"]} == {here, to})
            homes = w.homes(name)
            h = next((b for b in homes if s["buildings"][b]["node"] == here), None)
            if h:                                                            # the house as last seen (D4-35: not watched from afar)
                w.apply("set", here, ref=("person", name), field="home_seen", value={
                    "day": w.d, "building": h, "stock": dict(w.goods(s["buildings"][h]["stock"])),
                    "condition": s["buildings"][h]["condition"], "door": s["buildings"][h]["door"]})
            lead = ((today.get("travel_choices") or {}).get(name) or {}).get("lead")
            from cybertron2.engine import herds as HD
            ox = HD.pack_ox_for(w, name, lead) if lead else None               # the pack ox chosen at departure (D2-136)
            w.apply("depart", here, person=name, road=road, to=to)
            from cybertron2.engine import layout as LY
            LY.wear_way(w, road, here)                                       # a hidden end worn by use (D2-92)
            w.apply("transit", road, person=name, fields={"choices": dict((today.get("travel_choices") or {}).get(name) or {})})
            if ox:                                                           # one ox goes with the party, carrying (D2-136)
                from cybertron2.engine import roads as RD
                HD.lead_ox(w, name, ox, road, RD.position(w, a["transit"]))
            from cybertron2.engine import life as LF
            for baby in LF.infants_of(w, name, here):                        # her infants go with her (D2-141)
                w.apply("depart", here, person=baby, road=road, to=to)
                w.apply("transit", road, person=baby, fields={"carried_by": name})
            out.append({"agent": name, "from": here, "to": to})
    today["_departed"] = out
    return out


def decay_rate(w, c, item) -> tuple:
    """A good's loss tonight in its container (economy/goods.md "Decay", D2-87): its rate in a house, times the keeping fittings (D2-45,
    D2-58) in a store, the conditions of a thing at a spot (open, dry or wet; buried) and the season and the frost; and what the lost
    share becomes in the open. Hands keep the rate in hand. Returns (share, becomes)."""
    from cybertron2.engine import environment as EV, things as TH
    p = w.p
    base = float(ITEMS.get(item, {}).get("spoil", 0.0))
    table = DECAY.get(ITEMS.get(item, {}).get("decay") or "default", DECAY["default"])
    season = 1.0
    if w.cold():
        season *= float(table.get("frozen", 1.0))
    elif w.calendar()["season"] == "summer":
        season *= float(table.get("warm", 1.0))
    if c["kind"] == "stock":
        bb = w.s["buildings"][c["of"]]
        keep = min([1.0] + [float(FITTINGS[f_].get("spoil", 1.0)) for f_, n in bb["fittings"].items() if n and f_ in FITTINGS])
        return base * float(p["house_spoil"]) * keep * season, None
    if c["kind"] in TH.KINDS:
        cond = "buried" if c.get("hidden") == "buried" or c.get("buried") is not None else ("open_wet" if EV.wet(w) else "open_dry")
        if base <= 0:
            return float((table.get("abs") or {}).get(cond, 0.0)), None
        return base * float(p["house_spoil"]) * float(table.get(cond, 1.0)) * season, table.get("becomes")
    return base * season, None


def _gear(w, name, where, tents):
    """What someone sleeping out has to sleep in: a tent of one's own, a place in another's tent here, or a bedroll (D2-68)."""
    a = w.s["people"][name]
    g = w.goods(a["hands"])
    place = w.place_of(("person", name))
    if g.get("tent", 0) >= 1:
        tents.setdefault(place, []).append([name, 1])
        w.apply("wear", place, container=a["hands"], item="tent", uses=1)
        return "tent"
    for t in tents.get(place, []):
        if t[1] < 2:
            t[1] += 1
            return "tent"
    if g.get("bedroll", 0) >= 1:
        w.apply("wear", place, container=a["hands"], item="bedroll", uses=1)
        return "bedroll"
    return None


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
        home = next((b for b in w.dwellings(name) if s["buildings"][b]["node"] == a["at"]), None)
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


def open_fires(w, today, where, rec) -> set:
    """Fires in the open (D4-49, D2-159): those sleeping out at one place (a node, or a party on the road) share a fire; whoever chose
    to light one burns 4 heat from their hands (2 timber, or firewood or charcoal by the order), and it warms up to 4 there, those
    who chose a fire first. Returns who slept by a fire."""
    from cybertron2.engine import forests as FO
    hp = w.p["heat"]
    want = today.get("fire") or {}
    out = [n for n in w.living() if where.get(n) is None]
    groups = {}
    for n in out:
        a = w.s["people"][n]
        key = ("node", a["at"]) if a["at"] is not None else ("road",) + tuple((a["transit"] or {}).get(k) for k in ("road", "from", "to", "left", "arrive"))
        groups.setdefault(key, []).append(n)
    warmed = set()
    for key, ppl in groups.items():
        lighters = [n for n in ppl if want.get(n)]
        rest = [n for n in ppl if not want.get(n)]
        queue = lighters + rest
        for n in lighters:
            if not queue or n in warmed:
                continue
            place = w.place_of(("person", n))
            if FO.burn(w, place, w.hands(n), float(hp["open"]), why="fire"):
                rec.setdefault("open_fire", []).append(n)
                by = [n] + [x for x in queue if x != n and x not in warmed][: int(hp["share"]) - 1]
                warmed.update(by)
                queue = [x for x in queue if x not in warmed]
    return warmed


def _eat(w, place, stores, need, hearth=True) -> float:
    """Up to `need` in food value, from the stores in order, most perishable first; what is better cooked is eaten raw, for less,
    without a lit fire (D2-160: grain 0.2, flour 0.5, beans nothing, fresh meat 0.8), after what needs no fire."""
    got = 0.0
    raw = lambda i: float(ITEMS[i].get("raw", ITEMS[i]["food"])) if ITEMS[i].get("cook") and not hearth else ITEMS[i]["food"]
    for cid in stores:
        g = w.goods(cid)
        for item in sorted(EDIBLE, key=lambda i: (raw(i) < ITEMS[i]["food"], -ITEMS[i]["spoil"])):
            v = raw(item)
            if v <= 0:
                continue
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
            reg = {"plants": "fast", "grass": "fast", "game": "threshold"}.get(key)     # woods: forests.night (D2-156)
            if not reg or r["K"] <= 0:
                continue
            if reg == "threshold" and r["S"] < float(p["game_threshold"]) * r["K"]:
                continue
            rate = r["r"] * (float(p["regrow_winter"]) if winter else 1.0)
            S = round(min(r["K"], r["S"] + rate * r["S"] * (1 - r["S"] / r["K"]) + (0.01 * (r["K"] - r["S"]) if reg == "fast" else 0)), 4)
            if S != r["S"]:
                w.apply("set_res", par["node"], parcel=pid, key=key, fields={"S": S})
        # crops: farm.night (D2-53, D4-39)
    from cybertron2.engine import forests as FO
    FO.night(w)
