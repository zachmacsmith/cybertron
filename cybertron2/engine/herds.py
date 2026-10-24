"""Herds that nobody holds, fences round a parcel, and herds on the roads (economy/livestock.md: D2-117, D2-123, D2-124, D2-127,
D2-128, D2-130 to D2-132).

Each night, before the herds eat (farm.py), this settles:
- **fences** (D2-130): the day's work on a fence counts (a wall's only if one who knows walling worked on it); a wood fence loses a level
  each season unless mended; mending a gappy one brings it back;
- **splitting** (D2-128, D2-131) wherever a herd is held, by how many head the people with it hold together;
- **wandering on the node** (D2-117, D2-123): a herd nobody herded and no shut fence holds takes 0 to 1 steps when fed on good pasture,
  up to 8 when hungry or drawn by a ripe crop, each toward the most attractive parcel near it; a fence is crossed at its odds; from a
  parcel where a road leaves, a step may take the road; in a crop it eats and tramples 1% of it a head;
- **herds on a road** (D2-124): drift a stretch a day, lose head and may be gone for good, come home or stray to the far node; a herd a
  party accompanies moves with it (D2-127).

Finds of a herd on the road and a split noticed while driving are fuse calls (roads.py registers them); noticing a herd that is out,
an open gate, a fence's state and one's own pasture empty are signs read by the noticing rule (signs.py ASTRAY).
"""
from __future__ import annotations

import math

from cybertron2.engine import farm as FM, layout as LY
from cybertron2.engine.data import FENCES, HERDS

ROLES = ("cows", "oxen", "bulls", "young")


def night(w, rec) -> None:
    rec.setdefault("herds", [])
    _fences(w, rec)
    for hid in sorted(w.s["herds"]):
        h = w.s["herds"].get(hid)
        if not h or FM.head(h) <= 0:
            continue
        if h["node"] in w.s["roads"]:
            if not h.get("with"):
                _on_road(w, hid, rec)
            continue
        split(w, hid, rec)
    for hid in sorted(w.s["herds"]):                                            # the groups that broke off wander their own way
        h = w.s["herds"][hid]
        if FM.head(h) > 0 and h["node"] in w.s["nodes"]:
            wander(w, hid, rec)
    _merge(w, rec)


# ---------------------------------------------------------------------- fences (D2-130)
def through(w, pid) -> float:
    """The chance a day a herd gets through the fence round this parcel, in or out: 1 if there is none, it is down, or its gate open."""
    fc = w.s["parcels"][pid].get("fence") or {}
    if not fc.get("built") or int(fc.get("level", 0)) <= 0 or fc.get("gate") == "open":
        return 1.0
    return float(FENCES[fc["kind"]]["through"].get(int(fc["level"]), 1.0))


def _fences(w, rec):
    new_season = w.calendar(w.d + 1)["season"] != w.calendar()["season"]
    for pid, par in sorted(w.s["parcels"].items()):
        fc = par.get("fence")
        if not fc:
            continue
        fc = dict(fc)
        d = FENCES[fc["kind"]]
        need = FM.fence_need(par, fc["kind"])["units"]
        p = (fc.get("pending") or {}).get(str(w.d))
        if p and p["led"] and not fc.get("built"):
            fc["units"] = round(fc["units"] + p["units"], 3)
            if fc["units"] >= need - 1e-6:
                fc.update(built=True, level=2, gate="shut", mend=0.0, since=w.d)
                w.event(par["node"], "fence", f"the {FM.fence_word(fc['kind'])} round {par['name']} is finished", about=[f"parcel:{pid}"],
                        salience=0.4, tags=["animals", "farming"])
                rec["herds"].append(("fence", pid, fc["kind"]))
        fc["pending"] = {}
        quarter = float(d["mend"]) * need
        if fc.get("built") and 0 < int(fc["level"]) < 2 and float(fc.get("mend", 0.0)) >= quarter - 1e-6:
            fc.update(level=int(fc["level"]) + 1, mend=round(float(fc["mend"]) - quarter, 3))
        if new_season and fc.get("built") and d["decays"] and int(fc["level"]) > 0 and fc.get("since") != w.d:
            if float(fc.get("mend", 0.0)) + 1e-6 < quarter:
                fc["level"] = int(fc["level"]) - 1
                rec["herds"].append(("fence decayed", pid, fc["level"]))
            fc["mend"] = 0.0
        w.apply("set", par["node"], ref=("parcel", pid), field="fence", value=fc)


# ---------------------------------------------------------------------- wandering on the node (D2-117, D2-123)
def held(w, h) -> bool:
    """Herded today: someone did herding work with it."""
    return h.get("watched") == w.d


def value(w, h, pid) -> float:
    """How strongly a parcel draws this herd by day: the share of its need it would eat there (grazing, or a crop at the trampling
    rate), a ripe crop's pull beyond that, and water when hungry. Cows in milk go home at dusk (`home_at_dusk`)."""
    dr = HERDS["draw"]
    par = w.s["parcels"][pid]
    n = max(1, FM.head(h))
    hungry = int(h.get("hungry", 0)) > 0
    food = 0.0
    c = par.get("crop")
    if c and c.get("area_left", 0) > 1e-6:
        food += float(c.get("left", 0.0)) * float(HERDS["trample"])
    g = par["res"].get("grass")
    if g and g["K"] > 0:
        food += max(0.0, g["S"] - 0.05 * g["K"]) / n
    v = min(1.0, food)
    if c and c.get("area_left", 0) > 1e-6 and w.d >= int(c["ripe_day"]):
        v += float(dr["ripe"]) * v                                             # a ripe crop pulls while there is much of it left
    if hungry and par["cover"] == "water":
        v += float(dr["water"])
    return v


def drawn(w, h) -> bool:
    """A ripe crop within reach pulls even a fed herd far (D2-123)."""
    reach = LY._layers(w, h["parcel"])
    return any(d <= int(HERDS["steps"]["drawn"]) and (w.s["parcels"][q].get("crop") or {}).get("area_left", 0) > 1e-6
               and w.d >= int(w.s["parcels"][q]["crop"]["ripe_day"]) and q != h["parcel"] for q, d in reach.items())


def target(w, h, pid) -> str:
    """The parcel the herd heads for: the best value, falling off with the steps to it and the fences in the way (keyed ties)."""
    dist = LY._layers(w, pid)
    rng = w.rng("herd-target", w.d, h["name"], pid)
    best = max(dist, key=lambda q: (round(value(w, h, q) * 0.8 ** dist[q] * (1.0 if q == pid else through(w, q)), 6), rng.random()))
    return best


def wander(w, hid, rec) -> list:
    """A day's wandering; returns the parcels it crossed."""
    h = w.s["herds"][hid]
    if held(w, h):
        return []
    node, pid = h["node"], h["parcel"]
    rng = w.rng("herd-wander", w.d, hid)
    if through(w, pid) < 1.0 and rng.random() >= through(w, pid):
        return []                                                             # the fence held them
    hungry = int(h.get("hungry", 0)) > 0
    g = w.s["parcels"][pid]["res"].get("grass")
    good = bool(g and g["K"] > 0 and g["S"] / g["K"] >= float(HERDS["good_grass"]))
    far = hungry or drawn(w, h) or not good
    n = 1 + int(rng.random() * int(HERDS["steps"]["drawn"])) if far else int(rng.random() * (int(HERDS["steps"]["fed"]) + 1))
    road_at = {p: (rid, other) for rid, other, end in LY.road_ends(w, node) if not end.get("hidden") for p in end["parcels"]}
    way = []
    for _ in range(n):
        goal = target(w, h, pid)
        if goal == pid:
            break
        if pid in road_at and rng.random() < float(HERDS["onto_road"]):     # a step from a road-end parcel may take the road
            if way:
                w.apply("set", node, ref=("herd", hid), field="parcel", value=pid)
            onto_road(w, hid, road_at[pid][0], node, rec)
            return way
        step = LY.path(w, pid, goal, (hid,))[1]
        if through(w, step) < 1.0 and rng.random() >= through(w, step):
            break                                                             # the fence round it kept them out
        pid = step
        way.append(pid)
    if way:
        w.apply("set", node, ref=("herd", hid), field="parcel", value=pid)
        rec["herds"].append((hid, "wandered", way))
    trample(w, hid, rec)
    home_at_dusk(w, hid, rec, rng)
    return way


def home_at_dusk(w, hid, rec, rng) -> bool:
    """Cows in milk, fed, drift home at dusk (livestock.md), after a day where they wandered; a shut fence round home lets them back
    in only at its odds."""
    h = w.s["herds"][hid]
    home = h.get("home")
    if h.get("parcel") in (None, home) or home not in w.s["parcels"] or w.s["parcels"][home]["node"] != h["node"]:
        return False
    if float(h.get("in_milk", 0.0)) < 0.5 or int(h.get("hungry", 0)) > 0:
        return False
    way = LY.path(w, h["parcel"], home, (hid, "dusk"))
    if not way or (through(w, home) < 1.0 and rng.random() >= through(w, home)):
        return False
    w.apply("set", h["node"], ref=("herd", hid), field="parcel", value=home)
    rec["herds"].append((hid, "home at dusk", way[1:]))
    return True


def trample(w, hid, rec) -> float:
    """In a field each head eats and tramples about 1% of the standing crop a day (D2-123): recorded with the herd and its holders."""
    h = w.s["herds"][hid]
    par = w.s["parcels"][h["parcel"]]
    c = par.get("crop")
    if not c or c.get("area_left", 0) <= 1e-6 or c.get("left", 0) <= 1e-9:
        return 0.0
    q = round(float(c["left"]) * min(1.0, float(HERDS["trample"]) * FM.head(h)), 4)
    if q <= 1e-9:
        return 0.0
    w.apply("draw", h["node"], parcel=h["parcel"], key="crop", qty=q)
    c = dict(w.s["parcels"][h["parcel"]]["crop"])
    holders = sorted({cl["claimant"] for cl in w.claims_on(("herd", hid))})
    c["trampled"] = {"day": w.d, "by": hid, "holders": holders, "qty": round(float((c.get("trampled") or {}).get("qty", 0.0)) + q, 4)}
    w.apply("set", h["node"], ref=("parcel", h["parcel"]), field="crop", value=c)
    w.apply("set", h["node"], ref=("herd", hid), field="ate", value={"day": w.d, "q": q})    # what it ate there (farm._herds)
    rec["herds"].append((hid, "trampled", h["parcel"], q))
    return q


# ---------------------------------------------------------------------- herds on a road (D2-124, D2-127)
def onto_road(w, hid, rid, node, rec):
    r = w.s["roads"][rid]
    pos = 1 if node == r["a"] else int(r["days"])
    w.apply("set", node, ref=("herd", hid), field="parcel", value=None)
    w.apply("set", node, ref=("herd", hid), field="lost", value={"day": w.d, "from": node, "road": rid})
    w.apply("set", node, ref=("herd", hid), field="pos", value=pos)
    w.apply("set", node, ref=("herd", hid), field="node", value=rid)
    rec["herds"].append((hid, "onto the road", rid))


def off_road(w, hid, node, rec, why="came"):
    """Off an end of the road onto that node: home if it came from there, else a stray at the far node, on the road's end."""
    h = w.s["herds"][hid]
    rid = h["node"]
    end = (w.s["roads"][rid].get("ends") or {}).get(node) or LY.default_end(w, node)
    home = h.get("home") if h.get("home") in w.s["parcels"] and w.s["parcels"][h["home"]]["node"] == node else None
    pid = home or (end["parcels"] or LY.parcels_of(w, node))[0]
    w.apply("set", rid, ref=("herd", hid), field="node", value=node)
    w.apply("set", node, ref=("herd", hid), field="parcel", value=pid)
    for f in ("pos", "with", "lost"):
        w.apply("set", node, ref=("herd", hid), field=f, value=None)
    rec["herds"].append((hid, "home" if home else "strayed to", node))
    if not home:
        w.apply("set", node, ref=("herd", hid), field="strayed_in", value=w.d)
        w.event(node, "herd", f"{FM.herd_words(h)} that nobody here knows wandered in off the road onto {w.s['parcels'][pid]['name']}",
                about=[f"herd:{hid}", f"parcel:{pid}"], salience=0.6, tags=["animals"])


def _on_road(w, hid, rec):
    h = w.s["herds"][hid]
    rid = h["node"]
    r = w.s["roads"][rid]
    rd = HERDS["road"]
    rng = w.rng("herd-road", w.d, hid)
    if rng.random() < float(rd["gone"]):                                      # wandered beyond finding (D2-124)
        for role in ROLES:
            w.apply("set", rid, ref=("herd", hid), field=role, value=0)
        w.apply("set", rid, ref=("herd", hid), field="count", value=0)
        w.apply("set", rid, ref=("herd", hid), field="gone", value=w.d)
        rec["herds"].append((hid, "gone", rid))
        return
    die = float(rd["die_winter" if w.calendar()["season"] == "winter" else "die"])
    for role in ROLES:
        n = int(h.get(role, 0))
        dead = sum(1 for _ in range(n) if rng.random() < die)
        if dead:
            w.apply("set", rid, ref=("herd", hid), field=role, value=n - dead)
            rec["herds"].append((hid, "died on the road", role, dead))
            for k in range(dead):                                               # by the road, off it out of sight, or nowhere (D4-52)
                _road_carcass(w, hid, role, rid, int(h["pos"]), w.rng("carcass", w.d, hid, role, k))
    w.apply("set", rid, ref=("herd", hid), field="count", value=FM.head(w.s["herds"][hid]))
    if FM.head(w.s["herds"][hid]) <= 0:
        return
    pos = int(h["pos"]) + (1 if rng.random() < 0.5 else -1)                 # a stretch a day, either way (keyed)
    if pos < 1:
        off_road(w, hid, r["a"], rec)
    elif pos > int(r["days"]):
        off_road(w, hid, r["b"], rec)
    else:
        w.apply("set", rid, ref=("herd", hid), field="pos", value=pos)


def _road_carcass(w, hid, role, rid, pos, rng) -> str:
    from cybertron2.engine import things as TH
    from cybertron2.engine.data import TECHNIQUES, THINGS
    cr = THINGS["carcass_road"]
    u = rng.random()
    if u < float(cr["none"]):
        return ""                                                               # it wandered off to die where nobody will find it
    h = w.s["herds"][hid]
    holders = [c["claimant"] for c in w.claims_on(("herd", hid))]
    return TH.leave_carcass(w, rid, FM.ROLE_WORD[role][0], h.get("base_name") or h["name"], holders, "road",
                            TECHNIQUES["slaughter"]["yield"]["gives"][role], stretch=pos,
                            hidden="off the road" if u < float(cr["none"]) + float(cr["hidden"]) else None)


def on_stretch(w, rid, pos) -> dict:
    return {hid: h for hid, h in w.s["herds"].items() if h["node"] == rid and int(h.get("pos") or 0) == pos and FM.head(h) > 0}


def drive_stretch(w, hid, toward) -> None:
    """Driven a stretch toward a node and left there (D2-127); off the end, onto that node."""
    h = w.s["herds"][hid]
    r = w.s["roads"][h["node"]]
    pos = int(h["pos"]) + (1 if toward == r["b"] else -1)
    if pos < 1 or pos > int(r["days"]):
        off_road(w, hid, toward, {"herds": []})
    else:
        w.apply("set", h["node"], ref=("herd", hid), field="pos", value=pos)


def accompany(w, hid, lead) -> None:
    w.apply("set", w.s["herds"][hid]["node"], ref=("herd", hid), field="with", value=lead)


def follow(w) -> None:
    """Herds a party accompanies are where the party is tonight (D2-127)."""
    from cybertron2.engine import roads as RD
    for hid, h in w.s["herds"].items():
        lead = h.get("with")
        if not lead or h["node"] not in w.s["roads"]:
            continue
        t = w.s["people"][lead].get("transit")
        if t and t["road"] == h["node"] and w.s["people"][lead]["alive"]:
            w.apply("set", h["node"], ref=("herd", hid), field="pos", value=RD.position(w, t))
        elif not t or not w.s["people"][lead]["alive"]:
            w.apply("set", h["node"], ref=("herd", hid), field="with", value=None)


def arrive_with(w, name, node) -> list:
    """A party that arrives brings the herd it accompanied onto the node (D2-127)."""
    out = []
    for hid, h in list(w.s["herds"].items()):
        if h.get("with") == name and h["node"] in w.s["roads"]:
            off_road(w, hid, node, {"herds": []})
            out.append(hid)
    return out


def drovers(w, h) -> list:
    lead = h.get("with")
    if not lead:
        return []
    t = w.s["people"][lead].get("transit") or {}
    key = lambda n: tuple((w.s["people"][n].get("transit") or {}).get(k) for k in ("road", "from", "to", "left", "arrive"))
    return [n for n in w.living() if w.s["people"][n].get("transit") and key(n) == key(lead)] if t else []


# ---------------------------------------------------------------------- size and splitting (D2-128, D2-131)
def split_chance(head, cap) -> float:
    sp = HERDS["split"]
    if head <= cap:
        return float(sp["under"])
    return min(float(sp["max"]), float(sp["over"]) * (head / cap - 1))


def share(rng) -> float:
    """The share that breaks off (D2-131): a quarter x 2^z, z Laplace centred on 0 with a standard deviation of one doubling, drawn
    again if above half."""
    sh = HERDS["share"]
    b = float(sh["sd"]) / math.sqrt(2)
    while True:
        u = rng.random() - 0.5
        z = -b * math.copysign(1, u) * math.log(1 - 2 * abs(u))
        x = float(sh["centre"]) * 2 ** z
        if x <= float(sh["max"]):
            return x


def split(w, hid, rec, drove=0) -> str:
    """A day's chance that a group breaks off, by how many head the people with it hold (D2-128). Returns the new herd's id, or ''."""
    h = w.s["herds"][hid]
    n = FM.head(h)
    if n < 2:
        return ""
    cap = FM.herd_capacity(w.p, h, w.d, drovers=drove)
    rng = w.rng("herd-split", w.d, hid)
    if rng.random() >= split_chance(n, cap):
        return ""
    k = max(1, min(n - 1, round(share(rng) * n)))
    take, left = {}, k
    for role in ("young", "cows", "oxen", "bulls"):                            # the young and the cows go first
        q = min(int(h.get(role, 0)), left)
        if q:
            take[role] = q
            left -= q
    new = w.apply("split_herd", w.place_of(("herd", hid)), like=hid, take=take)
    for cl in w.claims_on(("herd", hid)):
        w.apply("claim", w.place_of(("herd", hid)), thing=("herd", new), claimant=cl["claimant"], rights=cl["rights"], grounds=cl["grounds"])
    rec["herds"].append((hid, "split", new, k))
    return new


def _merge(w, rec):
    """A group that split off and its herd on the same parcel again, held the same way, are one herd."""
    for hid, h in sorted(w.s["herds"].items()):
        of = h.get("split_of")
        g = w.s["herds"].get(of)
        if not of or not g or FM.head(h) <= 0 or int(h.get("split_day", -1)) >= w.d or h["node"] != g["node"] or h.get("parcel") is None or h.get("parcel") != g.get("parcel"):
            continue
        node = h["node"]
        for role in ROLES:
            w.apply("set", node, ref=("herd", of), field=role, value=int(g.get(role, 0)) + int(h.get(role, 0)))
            w.apply("set", node, ref=("herd", hid), field=role, value=0)
        w.apply("set", node, ref=("herd", of), field="in_milk", value=round(float(g.get("in_milk", 0)) + float(h.get("in_milk", 0)), 4))
        w.apply("set", node, ref=("herd", hid), field="in_milk", value=0.0)
        w.apply("set", node, ref=("herd", of), field="count", value=FM.head(w.s["herds"][of]))
        w.apply("set", node, ref=("herd", hid), field="count", value=0)
        rec["herds"].append((hid, "rejoined", of))
