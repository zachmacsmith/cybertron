"""Records in the engine's terms, built from a World (c2viz/SCHEMA.md): one day's parcels, buildings, herds, things, people, roads
and events. Reads World.s and calls the engine only through c2viz.touch. Nothing here decides a rule.
"""
from __future__ import annotations

from c2viz import touch as E
from c2viz.spec_rooms import GROUND, Rooms


def r3(x):
    return None if x is None else round(float(x), 3)


def node_view(w, nid):
    return E.node_view(w, nid)


def crop_stage(x, c) -> str:
    """The engine's crop states (signs.context): blighted, killed, rotting, ripe, high, new, green."""
    if x.failed:
        return "blighted"
    if c.get("killed"):
        return "killed"
    if x.rotting:
        return "rotting"
    if x.ripe:
        return "ripe"
    if c.get("crop") != "legumes" and x.progress >= 0.6:
        return "high"
    if x.progress < 0.25:
        return "new"
    return "green"


def parcel_day(w, h, pid) -> dict:
    x = E.parcel_signs(h, pid)
    p = x.p                                    # a field as its main holding shows it (the engine's plot shares: signs.context)
    size = max(1, int(p["size"]))
    out = {"cover": p["cover"], "was": p.get("was"), "fertility": r3(p.get("fertility", 1.0)),
           "soil": E.soil_word(float(p.get("fertility", 1.0))),
           "res": {k: r3(v["S"] / v["K"]) for k, v in (p.get("res") or {}).items() if k != "dung" and float(v.get("K") or 0) > 0},
           "dung": r3(x.dung) if x.dung else 0, "felled": E.felled(w, pid), "smoky": E.smoky(w, p["node"], pid),
           "high": E.crop_high(w, pid), "sight": r3(E.visibility(w, p["node"], pid, "sight")),
           "broken": r3(min(1.0, float(p.get("broken") or 0) / size)), "last_crop": p.get("last_crop"), "last_kind": p.get("last_kind"),
           "fallow_since": p.get("fallow_since"), "holders": w.holders(("parcel", pid))}
    c = p.get("crop")
    if c:
        area = max(1e-9, float(c.get("area") or 0))
        out["crop"] = {"kind": c.get("kind"), "family": c.get("crop"), "stage": crop_stage(x, c), "progress": r3(x.progress),
                       "sown": r3(min(1.0, area / size)), "reaped": r3(max(0.0, 1 - float(c.get("area_left", area)) / area)),
                       "weeds": bool(x.weeds), "trampled": x.trampled_days}
    wk = p.get("works") or {}
    if wk:
        out["works"] = {"ground": wk.get("ground"), "done": r3(x.works_done), "begun": x.works_begun, "unkept": x.works_unkept}
    if p.get("ground"):
        out["ground"] = p["ground"]
    fc = p.get("fence")
    if fc:
        out["fence"] = {"kind": fc.get("kind"), "level": int(fc.get("level", 0)), "built": bool(fc.get("built")), "gate": fc.get("gate")}
    if p.get("clearing"):
        need = E.clearing_work(p["cover"]) * size
        out["clearing"] = r3(min(1.0, float(p["clearing"]) / need)) if need else None
    if p["cover"] in GROUND:
        out["ground_spaces"] = GROUND[p["cover"]] * size
    return out


def building_day(w, h, bid, rooms: Rooms, slept_in: dict) -> dict:
    b = w.s["buildings"][bid]
    st = {i: q for i, q in w.s["containers"].get(b.get("stock"), {}).get("goods", {}).items() if q > 1e-9}
    x = E.building_signs(h, bid)
    unf = b.get("unfinished")
    R = rooms.get(bid, b, st, (unf or {}).get("blueprint") or b.get("blueprint"))
    made = sorted({e.get("tech") for e in w.s["events"] if e.get("kind") == "make" and f"building:{bid}" in (e.get("about") or [])} - {None})
    out = {"node": b["node"], "parcel": b["parcel"], "name": b["name"], "structure": b.get("structure"), "condition": b.get("condition", 2),
           "door": b.get("door"), "fire": bool(b.get("fire")), "warm": r3(b.get("warm")), "fittings": {k: v for k, v in (b.get("fittings") or {}).items() if v},
           "new": bool(x.new), "crowded": bool(x.crowded), "worked_on": bool(x.worked_on), "made": made,
           "sleepers": sorted(slept_in.get(bid, [])), "holders": w.holders(("building", bid)),
           "stock": {"food": r3(x.food_left), "timber": r3(st.get("timber", 0)), "firewood": r3(st.get("firewood", 0)),
                     "weight": r3(sum(q * E.weight(i) for i, q in st.items()))},
           "seen_as": next((E.SEEN[f] for f in E.SEEN if (b.get("fittings") or {}).get(f)), None)}
    out.update(R)
    out["footprint"] = sum(r["floor"] for r in R["rooms"] if r.get("storey", 1) == 1) + (2 if (b.get("fittings") or {}).get("woodshed") else 0)
    if unf:
        units = E.blueprint_units(unf.get("blueprint"))
        out["unfinished"] = {"blueprint": unf.get("blueprint"), "done": r3(1 - float(unf.get("units_left", units)) / units)}
    if b.get("lasts_until") is not None:
        out["nights_left"] = int(b["lasts_until"]) - w.d
    return out


def herd_day(w, hid) -> dict | None:
    g = w.s["herds"][hid]
    if E.herd_head(g) <= 0:
        return None
    out = {"node": g["node"], "parcel": g.get("parcel"), "home": g.get("home"), "name": g.get("name"), "kind": g.get("kind", "cattle"),
           "cows": int(g.get("cows", 0)), "oxen": int(g.get("oxen", 0)), "bulls": int(g.get("bulls", 0)), "young": int(g.get("young", 0)),
           "in_milk": r3(g.get("in_milk", 0)), "hungry": int(g.get("hungry", 0)), "watched": g.get("watched") == w.d,
           "holders": w.holders(("herd", hid)), "with": g.get("with"), "pack": bool(g.get("pack"))}
    if g.get("pos") is not None and g["node"] in w.s["roads"]:
        out["road"], out["pos"] = g["node"], int(g["pos"])
    return out


def thing_day(w, cid, c) -> dict:
    goods = {i: r3(q) for i, q in c["goods"].items() if q > 1e-9}
    weight = sum(q * E.weight(i) for i, q in goods.items())
    out = {"kind": c["kind"], "node": c.get("node"), "parcel": c.get("parcel"), "in": c.get("in"), "door": c.get("door"),
           "of": c.get("of"), "beast": c.get("beast"), "goods": goods, "weight": r3(weight),
           "heap": weight >= E.THINGS["heap_min"], "hidden": c.get("hidden"), "buried": c.get("buried"), "cairn": bool(c.get("cairn")),
           "body": E.body_state(w, c) if c.get("body") else None, "rotting": E.rotting(w, c), "died": c.get("died")}
    if c["kind"] == "carcass":
        out["fresh"] = E.carcass_fresh(w, c)
        out["bones"] = w.d - int(c.get("died", w.d)) >= E.THINGS["carcass_bones_after"]
    if c.get("stretch") is not None:
        out["stretch"] = c["stretch"]
    return out


def person_day(w, name, slept: dict) -> dict:
    a = w.s["people"][name]
    hands = w.s["containers"].get(a.get("hands") or f"hands:{name}", {}).get("goods", {})
    carried = {i: r3(q) for i, q in hands.items() if q > 1e-9}
    out = {"at": a.get("at"), "alive": a["alive"], "died": a.get("died"), "cause": a.get("cause"), "stage": a.get("stage"),
           "sex": a.get("sex"), "hunger": a.get("hunger", 0), "missed": a.get("missed", 0), "wounded": bool(a.get("wounded")),
           "household": w.household_of(name), "homes": w.homes(name) if a["alive"] else [],
           "slept": slept.get(name), "worked": list((w.s.get("today") or {}).get("worked", {}).get(name, [])),
           "spot": E.spot_of(w, name) if a["alive"] and a.get("at") else None, "carried": carried,
           "gear": [i for i, q in carried.items() if q >= 1 and E.item_seen(i)],
           "arrived": a.get("arrived") == w.d, "pregnant": bool(a.get("pregnant") is not None and a["alive"] and E.showing(w, name))}
    t = a.get("transit")
    if t:
        r = w.s["roads"].get(t["road"], {})
        out["transit"] = {"road": t["road"], "from": t["from"], "to": t["to"], "pos": E.road_position(w, t), "days": int(r.get("days", 1))}
    return out


def day_record(w, rooms: Rooms) -> dict:
    d, cal = w.d, w.calendar()
    log = (w.s.get("log") or [{}])[-1] if w.s.get("log") else {}
    slept = dict(log.get("slept") or {})
    by_name = {}                                                                # a building's name at its node -> its id
    for bid, b in w.s["buildings"].items():
        by_name.setdefault((b["node"], b["name"]), bid)
    slept_in, slept_at = {}, {}
    for n, where in slept.items():
        node = w.s["people"].get(n, {}).get("at")
        bid = by_name.get((node, where))
        slept_at[n] = bid or where
        if bid:
            slept_in.setdefault(bid, []).append(n)
    views = {nid: node_view(w, nid) for nid in w.s["nodes"]}
    rec = {"day": d, "calendar": cal, "cold": w.cold(), "weather": E.weather(w), "words": E.words(w), "wet": E.wet(w),
           "snow": E.snow_lying(w),
           "parcels": {pid: parcel_day(w, views[p["node"]], pid) for pid, p in w.s["parcels"].items()},
           "buildings": {bid: building_day(w, views[b["node"]], bid, rooms, slept_in) for bid, b in w.s["buildings"].items()},
           "herds": {hid: x for hid in w.s["herds"] if (x := herd_day(w, hid))},
           "things": {}, "people": {}, "roads": {}, "traces": list(w.s.get("traces") or []),
           "events": [], "acts": [a for a in w.s["acts"] if a.get("day") == d], "fights": list(log.get("fights") or [])}
    for nid in w.s["nodes"]:
        for cid, c in E.at_node(w, nid).items():
            rec["things"][cid] = thing_day(w, cid, c)
    for cid, c in w.s["containers"].items():                                    # things lying on the roads
        if c["kind"] in E.THING_KINDS and c.get("node") in w.s["roads"] and (c.get("body") or any(q > 1e-9 for q in c["goods"].values())):
            rec["things"][cid] = thing_day(w, cid, c)
    for n, a in w.s["people"].items():
        if a["alive"] or a.get("died") == d:
            rec["people"][n] = person_day(w, n, slept_at)
    for rid, r in w.s["roads"].items():
        rec["roads"][rid] = {"ends": {n: {"worn": r3(e.get("worn", 0)), "used": e.get("used")} for n, e in (r.get("ends") or {}).items()},
                             "challenges": {f"{i + 1}:{lm.get('kind')}": E.challenge(w, rid, i + 1, lm)
                                            for i, s in enumerate(r.get("stretches") or []) for lm in s.get("landmarks") or []
                                            if E.challenge(w, rid, i + 1, lm)}}
    extent = {k: ext for ext, kinds in E.EVENT_EXTENT.items() for k in kinds}
    for e in w.s["events"]:
        rec["events"].append({k: e.get(k) for k in ("id", "place", "kind", "actor", "target", "about", "text", "salience", "tech", "dawn")}
                             | {"extent": extent.get(e.get("kind"), "parcel")})
    return rec


