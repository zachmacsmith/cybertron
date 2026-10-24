"""A run's days in the engine's own terms, for the renderer (c2viz/ENGINE.md §8).

Reads a run's journal (run.db), rebuilds the World at each day's end (the `d{d}.memory` checkpoint: the day's acts, events and
night are in it) and asks the engine for everything it computes: the calendar and weather, what a parcel, building, person, herd
or thing is like (signs.context and its siblings, the same derivations the agents' signs are made from), where a person is
(things.spot_of), where a traveller is (roads.position), what a landmark's challenge is. Nothing here decides a rule.

Every value is one of: state (read from World.s), engine (an engine function's result), or spec (the spec's end-state model of
buildings, economy/buildings.md, derived until the engine stores rooms: those records carry "derived": true).

    python -m c2viz.model RUN [--out RUN/viz.json]
"""
from __future__ import annotations

import argparse
import json
import math
import sqlite3
from pathlib import Path

from cybertron2.engine import data as DT, environment as EV, farm as FM, journal as JN, life as LF, roads as RD, signs as SG
from cybertron2.engine import things as TH
from cybertron2.engine.here import Here
from cybertron2.engine.world import World

from c2viz.layout import node_layout, world_layout

# The spec's space model (economy/buildings.md, D2-154, D2-155), not yet in the engine: what a fitting takes of a room's floor,
# what ground a unit of a parcel's size gives for buildings, the rooms one may build, what a store holds.
SPACES = {"beds": 1, "bins": 1, "hand mill": 1, "fire ring": 1, "hearth": 1, "oven": 2, "anvil": 2, "granary": 3,
          "millstones": 3, "water wheel": 0, "cellar": 0, "stalls": 2, "woodshed": 0, "vault": 4}
GROUND = {"built": 24, "scrub": 16}
ROOMS = {"small room": 6, "medium room": 12, "hall": 30, "camp": 4}
FLOOR_HOLDS = 30                                     # weight a space of free floor
FITTED_HOLDS = {"bins": 60, "granary": 300}          # bins: food; a granary floor: grain
BLUEPRINT_ROOM = {"small room": "small room", "medium room": "medium room", "hall": "hall", "camp": "camp"}


def r3(x):
    return None if x is None else round(float(x), 3)


# ---------------------------------------------------------------------------------------------------- the journal
def open_run(run) -> dict:
    db = Path(run) / "run.db"
    con = sqlite3.connect(str(db))
    meta = dict(con.execute("SELECT key, value FROM meta").fetchall())
    steps = [r[0] for r in con.execute("SELECT step FROM steps WHERE status = 'committed'").fetchall()]
    con.close()
    days = sorted(int(s.split(".")[0][1:]) for s in steps if s.endswith(".memory"))
    return {"db": db, "spec": json.loads(meta["spec"]), "days": days, "seed": json.loads(meta.get("seed") or "1")}


def world_at(R, step) -> World:
    w = World(R["spec"])
    w.s = JN.checkpoint(R["db"], step)["world"]
    return w


class NodeHere(Here):
    """A view of a node with nobody looking: the engine's own reads (parcels, buildings, herds, events, stock), the world as it is.
    Those present are everyone at the node (World.present), as for anyone standing there."""

    def __init__(self, w, nid):
        self._w, self.name, self.node, self.place = w, None, nid, nid

    def people(self, me=True) -> list:
        return self._w.present(self.node)


def node_view(w, nid) -> Here:
    return NodeHere(w, nid)


# ---------------------------------------------------------------------------------------------------- the spec's rooms
def rooms_for(floor: int, structure: str) -> list:
    """The fewest rooms of 6, 12 and 30 spaces that give `floor` (wattle: small rooms only; a camp: its lean-to)."""
    if structure == "camp":
        return ["camp"]
    out, n = [], max(1, int(math.ceil(floor)))
    if structure == "wattle":
        return ["small room"] * max(1, math.ceil(n / 6))
    while n > 0:
        if n > 24:
            out.append("hall"); n -= 30
        elif n > 12:
            out.append("medium room"); n -= 12
        elif n > 6:
            out.append("medium room"); n -= 12
        else:
            out.append("small room"); n -= 6
    return out


def floor_needed(b: dict, stock: dict) -> dict:
    """What a building's floor must hold (spec, D2-154, D2-155): its beds and fittings, and its stores beyond what fittings keep."""
    fit = b.get("fittings") or {}
    beds = int(fit.get("beds") or 0)
    fitted = sum(SPACES.get(f, 1) * (1 if f != "beds" else 0) for f, n in fit.items() if n)
    weight = sum(q * DT.ITEMS.get(i, {}).get("weight", 1) for i, q in stock.items() if q > 1e-9)
    kept = sum(FITTED_HOLDS.get(f, 0) for f in fit if fit[f])
    store = max(0.0, weight - kept) / FLOOR_HOLDS
    return {"beds": beds, "fittings": fitted, "store": round(store, 2), "total": beds + fitted + store}


class Rooms:
    """Each building's rooms for the whole run: read when the engine has them; else derived by the spec's seeding rule from the
    first day it stands (floor enough for its beds, fittings and stores), a room added when later fittings outgrow it; a built
    building has its blueprint's room."""

    def __init__(self):
        self.of = {}

    def get(self, bid, b, stock, built_from=None) -> dict:
        if b.get("rooms"):                                                          # the end state: rooms in the state
            rooms = [{"kind": r.get("kind"), "floor": r.get("floor"), "storey": r.get("storey", 1)} for r in b["rooms"]]
            return {"rooms": rooms, "derived": False}
        need = floor_needed(b, stock)
        rec = self.of.get(bid)
        if rec is None:
            kinds = [BLUEPRINT_ROOM[built_from]] if built_from in BLUEPRINT_ROOM else rooms_for(need["total"], b.get("structure"))
            rec = self.of[bid] = {"kinds": kinds}
        have = sum(ROOMS[k] for k in rec["kinds"])
        fixed = need["beds"] + need["fittings"]
        if fixed > have and b.get("structure") != "camp":                        # fittings outgrew it: an adjoining room
            rec["kinds"] = rec["kinds"] + rooms_for(fixed - have, b.get("structure"))
            have = sum(ROOMS[k] for k in rec["kinds"])
        rooms = [{"kind": k, "floor": ROOMS[k], "storey": 1} for k in rec["kinds"]]
        return {"rooms": rooms, "derived": True, "floor": have, "used": round(min(have, need["total"]), 1), "need": need}


# ---------------------------------------------------------------------------------------------------- one day
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
    p = w.s["parcels"][pid]
    x = SG.context(h, pid)
    size = max(1, int(p["size"]))
    out = {"cover": p["cover"], "was": p.get("was"), "fertility": r3(p.get("fertility", 1.0)),
           "soil": FM.soil_word(float(p.get("fertility", 1.0))),
           "res": {k: r3(v["S"] / v["K"]) for k, v in (p.get("res") or {}).items() if k != "dung" and float(v.get("K") or 0) > 0},
           "dung": r3(x.dung) if x.dung else 0, "felled": EV.felled(w, pid), "smoky": EV.smoky(w, p["node"], pid),
           "high": EV.crop_high(w, pid), "sight": r3(EV.visibility(w, p["node"], pid, "sight")),
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
        need = DT.CLEARING.get(p["cover"], 0) * size
        out["clearing"] = r3(min(1.0, float(p["clearing"]) / need)) if need else None
    if p["cover"] in GROUND:
        out["ground_spaces"] = GROUND[p["cover"]] * size
    return out


def building_day(w, h, bid, rooms: Rooms, slept_in: dict) -> dict:
    b = w.s["buildings"][bid]
    st = {i: q for i, q in w.s["containers"].get(b.get("stock"), {}).get("goods", {}).items() if q > 1e-9}
    x = SG.building_context(h, bid)
    unf = b.get("unfinished")
    R = rooms.get(bid, b, st, (unf or {}).get("blueprint") or b.get("blueprint"))
    made = sorted({e.get("tech") for e in w.s["events"] if e.get("kind") == "make" and f"building:{bid}" in (e.get("about") or [])} - {None})
    out = {"node": b["node"], "parcel": b["parcel"], "name": b["name"], "structure": b.get("structure"), "condition": b.get("condition", 2),
           "door": b.get("door"), "fire": bool(b.get("fire")), "warm": r3(b.get("warm")), "fittings": {k: v for k, v in (b.get("fittings") or {}).items() if v},
           "new": bool(x.new), "crowded": bool(x.crowded), "worked_on": bool(x.worked_on), "made": made,
           "sleepers": sorted(slept_in.get(bid, [])), "holders": w.holders(("building", bid)),
           "stock": {"food": r3(x.food_left), "timber": r3(st.get("timber", 0)), "firewood": r3(st.get("firewood", 0)),
                     "weight": r3(sum(q * DT.ITEMS.get(i, {}).get("weight", 1) for i, q in st.items()))},
           "seen_as": next((DT.LAYOUT["seen"][f] for f in DT.LAYOUT["seen"] if (b.get("fittings") or {}).get(f)), None)}
    out.update(R)
    out["footprint"] = sum(r["floor"] for r in R["rooms"] if r.get("storey", 1) == 1) + (2 if (b.get("fittings") or {}).get("woodshed") else 0)
    if unf:
        units = DT.BLUEPRINTS.get(unf.get("blueprint"), {}).get("units") or 1
        out["unfinished"] = {"blueprint": unf.get("blueprint"), "done": r3(1 - float(unf.get("units_left", units)) / units)}
    if b.get("lasts_until") is not None:
        out["nights_left"] = int(b["lasts_until"]) - w.d
    return out


def herd_day(w, hid) -> dict | None:
    g = w.s["herds"][hid]
    if FM.head(g) <= 0:
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
    weight = sum(q * DT.ITEMS.get(i, {}).get("weight", 1) for i, q in goods.items())
    out = {"kind": c["kind"], "node": c.get("node"), "parcel": c.get("parcel"), "in": c.get("in"), "door": c.get("door"),
           "of": c.get("of"), "beast": c.get("beast"), "goods": goods, "weight": r3(weight),
           "heap": weight >= DT.THINGS["heap_min"], "hidden": c.get("hidden"), "buried": c.get("buried"), "cairn": bool(c.get("cairn")),
           "body": TH.body_state(w, c) if c.get("body") else None, "rotting": TH.rotting(w, c), "died": c.get("died")}
    if c["kind"] == "carcass":
        out["fresh"] = TH.carcass_fresh(w, c)
        out["bones"] = w.d - int(c.get("died", w.d)) >= DT.THINGS["carcass_bones_after"]
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
           "spot": TH.spot_of(w, name) if a["alive"] and a.get("at") else None, "carried": carried,
           "gear": [i for i, q in carried.items() if q >= 1 and DT.ITEMS.get(i, {}).get("seen")],
           "arrived": a.get("arrived") == w.d, "pregnant": bool(a.get("pregnant") is not None and a["alive"] and LF.showing(w, name))}
    t = a.get("transit")
    if t:
        r = w.s["roads"].get(t["road"], {})
        out["transit"] = {"road": t["road"], "from": t["from"], "to": t["to"], "pos": RD.position(w, t), "days": int(r.get("days", 1))}
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
    rec = {"day": d, "calendar": cal, "cold": w.cold(), "weather": EV.weather(w), "words": EV.words(w), "wet": EV.wet(w),
           "snow": EV.snow_lying(w),
           "parcels": {pid: parcel_day(w, views[p["node"]], pid) for pid, p in w.s["parcels"].items()},
           "buildings": {bid: building_day(w, views[b["node"]], bid, rooms, slept_in) for bid, b in w.s["buildings"].items()},
           "herds": {hid: x for hid in w.s["herds"] if (x := herd_day(w, hid))},
           "things": {}, "people": {}, "roads": {}, "traces": list(w.s.get("traces") or []),
           "events": [], "acts": [a for a in w.s["acts"] if a.get("day") == d], "fights": list(log.get("fights") or [])}
    for nid in w.s["nodes"]:
        for cid, c in TH.at_node(w, nid).items():
            rec["things"][cid] = thing_day(w, cid, c)
    for cid, c in w.s["containers"].items():                                    # things lying on the roads
        if c["kind"] in TH.KINDS and c.get("node") in w.s["roads"] and (c.get("body") or any(q > 1e-9 for q in c["goods"].values())):
            rec["things"][cid] = thing_day(w, cid, c)
    for n, a in w.s["people"].items():
        if a["alive"] or a.get("died") == d:
            rec["people"][n] = person_day(w, n, slept_at)
    for rid, r in w.s["roads"].items():
        rec["roads"][rid] = {"ends": {n: {"worn": r3(e.get("worn", 0)), "used": e.get("used")} for n, e in (r.get("ends") or {}).items()},
                             "challenges": {f"{i + 1}:{lm.get('kind')}": RD.challenge(w, rid, i + 1, lm)
                                            for i, s in enumerate(r.get("stretches") or []) for lm in s.get("landmarks") or []
                                            if RD.challenge(w, rid, i + 1, lm)}}
    extent = {k: ext for ext, kinds in DT.EVENT_EXTENT.items() for k in kinds}
    for e in w.s["events"]:
        rec["events"].append({k: e.get(k) for k in ("id", "place", "kind", "actor", "target", "about", "text", "salience", "tech", "dawn")}
                             | {"extent": extent.get(e.get("kind"), "parcel")})
    return rec


# ---------------------------------------------------------------------------------------------------- the whole run
def static(w0: World, seed) -> dict:
    s = w0.s
    nodes = {nid: {"name": n["name"], "text": n.get("text"), "unexplored": bool(n.get("unexplored"))} for nid, n in s["nodes"].items()}
    parcels = {pid: {k: p.get(k) for k in ("node", "name", "cover", "size", "side", "height", "adj", "text", "ground")} for pid, p in s["parcels"].items()}
    roads = {rid: {"a": r["a"], "b": r["b"], "days": r["days"], "track": bool(r.get("track")), "way": r.get("way"), "terrain": r.get("terrain"),
                   "stretches": r.get("stretches") or [],
                   "ends": {n: {"side": e.get("side"), "parcels": e.get("parcels") or [], "hidden": bool(e.get("hidden"))} for n, e in (r.get("ends") or {}).items()}}
             for rid, r in s["roads"].items()}
    wl = world_layout(s["nodes"], s["roads"], seed)
    nl = {nid: node_layout(nid, s["parcels"], s["roads"], seed) for nid in s["nodes"]}
    return {"nodes": nodes, "parcels": parcels, "roads": roads, "layout": {"world": wl, "nodes": nl}}


def tables() -> dict:
    """The engine's tables the renderer reads (never its own copies), and the spec's space model until the engine has it."""
    pick = lambda d, keys: {k: {kk: v.get(kk) for kk in keys if kk in v} for k, v in d.items()}
    return {"covers": pick(DT.COVERS, ("words", "lots", "sight", "sound", "dig")), "crops": pick(DT.CROPS, ("seed", "share", "hardy", "names")),
            "fittings": pick(DT.FITTINGS, ("label", "does", "fire", "needs", "site", "spoil")),
            "blueprints": pick(DT.BLUEPRINTS, ("label", "units", "size", "structure", "lasts")),
            "fences": pick(DT.FENCES, ("words",)), "weather": DT.WEATHER, "seen": DT.LAYOUT["seen"], "height": DT.LAYOUT["height"],
            "things": {k: v for k, v in DT.THINGS.items() if not isinstance(v, dict)}, "terrain": DT.TERRAIN,
            "landmarks": {k: {kk: vv for kk, vv in v.items() if isinstance(vv, (str, int, float, bool))} for k, v in DT.LANDMARKS.items()},
            "event_extent": DT.EVENT_EXTENT,
            "spec": {"spaces": SPACES, "ground": GROUND, "rooms": ROOMS, "source": "economy/buildings.md D2-154, D2-155 (not yet in the engine)"}}


def build(run, out=None, days=None) -> Path:
    R = open_run(run)
    want = R["days"] if days is None else [d for d in R["days"] if d < days]
    rooms = Rooms()
    w0 = world_at(R, "d0.dawn")
    st = static(w0, R["seed"])
    recs = []
    for d in want:
        recs.append(day_record(world_at(R, f"d{d}.memory"), rooms))
    people = {n: {"household": w0.household_of(n), "model": p.get("model")} for n, p in w0.s["people"].items()}
    meta = {"name": R["spec"].get("name") or Path(run).name, "days": len(recs), "seed": R["seed"], "source": str(Path(run).resolve()),
            "people": people, "season_days": w0.season_len}
    out = Path(out) if out else Path(run) / "viz.json"
    out.write_text(json.dumps({"meta": meta, "tables": tables(), "static": st, "days": recs}, separators=(",", ":"), default=str))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run")
    ap.add_argument("--out")
    ap.add_argument("--days", type=int)
    a = ap.parse_args(argv)
    p = build(a.run, a.out, a.days)
    print(p, f"{p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
