"""Things at a spot (world/things_in_places.md; D2-85, D2-87, D2-93, D2-96, D2-111) and the one rule for noticing them
(information/noticing.md; D2-85, D2-91, D2-102).

A thing at a spot is a container with a place: goods put down or hidden (`pile`), a body and what it carried (`remains`); the roads
package adds traces and things on a stretch. Every kind is read the same way: its own conspicuousness (by what it is and how it is
hidden), the place's visibility that day (environment.py), where the observer was and what it did, its attention, its eye for the
land, and (later) fresh traces. A new kind of thing is a kind name, a conspicuousness and its signs.
"""
from __future__ import annotations

from cybertron2.engine import environment as EV, knowledge as KN
from cybertron2.engine.data import COVERS, ITEMS, NOTICING, TECHNIQUES, THINGS

KINDS = ("pile", "remains", "carcass")


# ---------------------------------------------------------------------- where things are
def spot_of(w, name):
    """The parcel a person is at: where it last worked today, else its house's ground here, else the node's built ground."""
    a = w.s["people"][name]
    node = a["at"]
    if node is None:
        return None
    for key in reversed((w.s.get("today") or {}).get("worked", {}).get(name, [])):
        if key in w.s["parcels"]:
            return key
        if key in w.s["buildings"]:
            return w.s["buildings"][key]["parcel"]
    homes = [b for b in w.homes(name) if w.s["buildings"][b]["node"] == node]
    if homes:
        return w.s["buildings"][homes[0]]["parcel"]
    built = [pid for pid, p in w.s["parcels"].items() if p["node"] == node and p["cover"] == "built"]
    return built[0] if built else next((pid for pid, p in w.s["parcels"].items() if p["node"] == node), None)


def house_at_death(w, name, spot):
    """The house one died in, if one died at home or abed (no work yet today): its household finds the body there."""
    a = w.s["people"][name]
    if a["at"] is None or (w.s.get("today") or {}).get("worked", {}).get(name):
        return None
    homes = [b for b in w.homes(name) if w.s["buildings"][b]["node"] == a["at"] and w.s["buildings"][b]["parcel"] == spot]
    return homes[0] if homes else None


def at_node(w, node) -> dict:
    """Things lying at a node: piles with goods, bodies (buried or not), remains with goods."""
    out = {}
    for cid, c in w.s["containers"].items():
        if c["kind"] in KINDS and c.get("node") == node and (c.get("body") or any(q > 1e-9 for q in c["goods"].values())
                                                             or (c.get("beast") and w.d - int(c.get("died", w.d)) <= 3 * int(THINGS["carcass_bones_after"]))):
            out[cid] = c
    return out


def parcel_name(w, c) -> str:
    if c.get("in") in w.s["buildings"]:
        return w.s["buildings"][c["in"]]["name"]
    pid = c.get("parcel")
    if pid in w.s["parcels"]:
        return w.s["parcels"][pid]["name"]
    return w.s["nodes"][c["node"]]["name"] if c.get("node") in w.s["nodes"] else "the side of the road"


def goods_words(goods: dict) -> str:
    items = [i for i, q in sorted(goods.items(), key=lambda kv: -kv[1]) if q > 1e-9]
    return " and ".join(items[:3]) if items else ""


# ---------------------------------------------------------------------- what a thing is like
def body_state(w, c) -> str:
    """'' if not a body or buried; else 'fresh', 'days' (dead some days) or 'bones' (D2-96)."""
    if not c.get("body") or c.get("buried") is not None:
        return ""
    age = w.d - int(c.get("died", w.d))
    if age < 1:
        return "fresh"
    return "days" if age <= int(THINGS["body_days"]) else "bones"


def rotting(w, c) -> bool:
    """A body unburied some days, or rotting food lying out (D2-96: signs only, no health effect yet)."""
    if c.get("buried") is not None:
        return False
    if c.get("body") and w.d - int(c.get("died", w.d)) >= int(THINGS["rot_after"]) and body_state(w, c) != "bones":
        return True
    return any(ITEMS.get(i, {}).get("rot") and q > 0.2 for i, q in c["goods"].items())


def own(w, c) -> float:
    """A thing's own conspicuousness (information/noticing.md), times how it is hidden (taught, or tried untaught)."""
    x = 0.0
    if c.get("beast") and c.get("buried") is None:                         # a dead beast (D4-52)
        old = w.d - int(c.get("died", w.d)) >= int(THINGS["carcass_bones_after"])
        x = float(THINGS["carcass_bones" if old else "carcass"])
    if c.get("body") and c.get("buried") is None:
        built = w.s["parcels"].get(c.get("parcel"), {}).get("cover") == "built"
        x = float(THINGS["body_built"] if built else THINGS["body"])
    qty = sum(q * max(1, ITEMS.get(i, {}).get("weight", 1)) for i, q in c["goods"].items() if q > 1e-9)
    if qty > 1e-9:
        x = max(x, float(THINGS["heap"] if qty >= float(THINGS["heap_min"]) else THINGS["pack"]))
    how = c.get("hidden")
    if how:
        taught, untaught = THINGS["hidden"][how]
        x *= float(untaught if c.get("untaught") else taught)
    return x


def describe(w, c) -> str:
    """The thing as one who notices it sees it (its signs, D4-48)."""
    where = parcel_name(w, c)
    g = goods_words(c["goods"])
    if c.get("beast"):
        return f"a dead {c['beast']} lies at {where}" + (": past eating" if not carcass_fresh(w, c) else "")
    if c.get("hidden") == "buried" and not c.get("body"):
        return f"a patch of turned earth at {where}, as if something were buried there"
    if c.get("hidden") == "under brush":
        return f"something hidden under brush at {where}" + (f": {g}" if g else "")
    st = body_state(w, c)
    if c.get("body") and c.get("buried") is not None:
        return f"a grave at {where}: {c['of']} lies buried there" + (" under a cairn" if c.get("cairn") else "")
    if st == "fresh":
        return f"the body of {c['of']} lies at {where}" + (f", with {g} beside it" if g else "")
    if st == "days":
        return f"the body of {c['of']}, dead some days, lies at {where}" + (f", with {g} beside it" if g else "")
    if st == "bones":
        return f"bones lie at {where}: all that is left of {c['of']}"
    qty = sum(c["goods"].values())
    return (f"a heap of {g} lies at {where}" if qty >= float(THINGS["heap_min"]) else f"a pack lies at {where}, with {g} in it")


def carcass_fresh(w, c) -> bool:
    """A dead beast is fit to eat for about a day after it died (D4-52)."""
    return w.d - int(c.get("died", w.d)) <= int(THINGS["carcass_fresh_days"]) and c["goods"].get("meat", 0.0) > 1e-9


def leave_carcass(w, place, beast, herd_name, holders, cause, role_meat, parcel=None, stretch=None, hidden=None) -> str:
    """A beast that died leaves its carcass where it fell (D4-52): meat by how it died (a share of slaughter's), its hide."""
    share = float(THINGS["carcass_meat"].get(cause, THINGS["carcass_meat"]["other"]))
    fields = {"beast": beast, "of": f"a {beast} of {herd_name}", "holders": list(holders), "cause": cause, "died": w.d}
    if stretch is not None:
        fields["stretch"] = stretch
    if hidden:
        fields["hidden"] = hidden
    cid = w.apply("new_thing", place, node=place, parcel=parcel, kind="carcass", **fields)
    for item, q in role_meat.items():
        q = round(q * share, 2) if item == "meat" else q
        if q > 0:
            w.apply("create", place, dst=cid, item=item, qty=q, why=f"a dead {beast}")
    return cid


# ---------------------------------------------------------------------- the eye for the land (D4-50, D2-91)
def eye_level(w, name) -> str:
    """none, ordinary or keen: drawn once, raised a step by enough roaming work (hunting, foraging) and finds."""
    u = w.rng("eye", name).random()
    blind, keen = float(w.p["land_blind"]), float(NOTICING["eye_keen"])
    base = 0 if u < blind else (2 if u > 1 - keen else 1)
    pr = NOTICING["eye_practice"]
    know = w.s["know"].get(name, {})
    practice = sum(KN.practice_of_skill(t, float(know[t].get("skill", KN.curve(t)[0]))) for t in pr["techs"] if t in know)
    practice += float(pr["find"]) * len((w.s["mind"].get(name) or {}).get("found", []))
    base += sum(1 for s in pr["steps"] if practice >= float(s))
    return ("none", "ordinary", "keen")[min(2, base)]


def eye(w, name, on="things") -> float:
    return float(NOTICING["eye" if on == "things" else "eye_bare"][eye_level(w, name)])


# ---------------------------------------------------------------------- the noticing rule (D2-85, D2-102)
def presence(w, name, parcel, own_x=1.0) -> float:
    """Where the observer was and what it did there today."""
    pr = NOTICING["presence"]
    best = 0.0
    for e in w.s.get("events", []):
        if e.get("actor") != name or e.get("kind") != "work" or e.get("day", w.d) != w.d or f"parcel:{parcel}" not in (e.get("about") or []):
            continue
        d = TECHNIQUES.get(e.get("tech"), {}).get("draws")
        best = max(best, float(pr.get(d, pr["work"])))
    if best:
        return best
    if spot_of(w, name) == parcel:
        return float(pr["about"])
    a = w.s["people"][name]
    if any(w.s["buildings"][b]["parcel"] == parcel for b in w.homes(name) if w.s["buildings"][b]["node"] == a["at"]):
        return float(pr["crossing"])                                       # one's own ground is crossed every day
    from cybertron2.engine import layout as LY
    if parcel in LY.passed(w, name):                                       # on the way to where one worked, and back (D2-115)
        return float(pr["crossing"])
    if parcel in LY.next_door(w, name) and own_x >= float(NOTICING["next_door_min"]):
        return float(pr["next door"])
    return float(pr["elsewhere"]) if own_x >= float(NOTICING["elsewhere_min"]) else 0.0


def attention(w, name, parcel, target) -> float:
    """Attending to the place x3; attending to it and working in it (a search) x5."""
    t = str(target or "").strip().lower()
    pname = w.s["parcels"][parcel]["name"].lower() if parcel in w.s["parcels"] else ""
    if not pname or t not in (pname, pname.removeprefix("the ")):
        return 1.0
    worked = parcel in (w.s.get("today") or {}).get("worked", {}).get(name, [])
    return float(NOTICING["attention"]["search" if worked else "place"])


def hidden_factor(c) -> float:
    """How much hiding keeps even a close look from finding a thing (THINGS hidden, taught or untaught); 1 if not hidden."""
    how = c.get("hidden")
    if not how:
        return 1.0
    taught, untaught = THINGS["hidden"][how]
    return float(untaught if c.get("untaught") else taught)


def close(w, name, c, target=None) -> bool:
    """A close look: one worked at the spot today, searched it, or it lies in (or at the door of) one's own house."""
    if c.get("in") and c["in"] in w.homes(name):
        return True
    if c.get("door") and c["door"] in w.homes(name):
        return True
    pid = c.get("parcel")
    if pid not in w.s["parcels"]:
        return False
    return presence(w, name, pid, 1.0) >= 0.5 and spot_of(w, name) == pid or attention(w, name, pid, target) > 1.0


def spot_chance(w, name, node, parcel, own_x, target=None, sense="sight", inside=(), everyone=False, eye_on="things") -> float:
    """The noticing rule (information/noticing.md, D4-53): own x visibility x presence x attention x eye, for every sign. `inside`:
    those always there (who live in the house, the household); `everyone`: open to all at the node (the sky)."""
    if own_x <= 0:
        return 0.0
    e = eye(w, name, on=eye_on)
    if everyone or name in inside:
        return min(1.0, own_x * e if eye_on != "things" else own_x)
    if parcel not in w.s["parcels"]:
        return 0.0
    vis = EV.visibility(w, node, parcel, sense if sense in ("sight", "sound") else "sight")
    return min(1.0, own_x * vis * presence(w, name, parcel, own_x) * attention(w, name, parcel, target) * e)


def chance(w, name, c, target=None) -> float:
    """One person's chance today of noticing a thing at its spot (information/noticing.md)."""
    x = own(w, c)
    if x <= 0:
        return 0.0
    if c.get("in") and c["in"] in w.homes(name):                          # in one's own house: found at once
        return 1.0
    pid = c.get("parcel")
    vis = EV.visibility(w, c.get("node"), pid, "sight") if pid in w.s["parcels"] else 1.0
    if not c.get("body") or c.get("buried") is not None:
        vis *= EV.ground_factor(w)                                         # things on the ground under lying snow
    p = x * vis * presence(w, name, pid, x) * attention(w, name, pid, target) * eye(w, name)
    return min(1.0, p)


# ---------------------------------------------------------------------- what one knows of things
def known(mind) -> dict:
    return mind.store.setdefault("things", {})


def remember(w, name, cid, how, text=None, close=False) -> None:
    """One knows a thing is there: it put it there, or noticed it (with the day and the words it saw). What it shows in "Lying
    about" is its closest look so far, not merely the last line noticed."""
    c = w.s["containers"][cid]
    k = w.s["mind"][name].setdefault("things", {})
    r = k.get(cid) or {"texts": []}
    text = text or describe(w, c)
    near = close or how in ("put", "took")
    if near or not r.get("close"):                                             # a later glimpse does not undo a close look
        r.update(text=text, close=bool(near or r.get("close")))
    r.update(day=w.d, how=how, node=c.get("node"), parcel=c.get("parcel"))
    r["texts"] = list(dict.fromkeys(r.get("texts", []) + [text]))[-6:]
    k[cid] = r


def known_here(w, name, node) -> dict:
    return {cid: r for cid, r in (w.s["mind"].get(name) or {}).get("things", {}).items() if r.get("node") == node}


def find(w, name, where, item=None):
    """A thing one knows of here, by its place's name or its dead person's name (and holding `item`, if named)."""
    low = str(where or "").strip().lower()
    for cid, r in sorted(known_here(w, name, w.at(name)).items(), key=lambda kv: -kv[1]["day"]):
        c = w.s["containers"].get(cid)
        if not c or c.get("node") != w.at(name):
            continue
        pname = w.s["parcels"].get(c.get("parcel"), {}).get("name", "").lower()
        names = {pname, pname.removeprefix("the "), w.s["buildings"].get(c.get("in"), {}).get("name", "").lower()} - {""}
        if low and low not in names and (c.get("of") or "").lower() not in low:
            continue
        if item and c["goods"].get(item, 0.0) <= 1e-9:
            continue
        return cid
    return None


# ---------------------------------------------------------------------- burying (D2-96)
def bodies(w, node) -> dict:
    return {cid: c for cid, c in at_node(w, node).items() if c.get("body") and c.get("buried") is None}


def bury_units(w, cid, cairn=False) -> int:
    if cairn:
        return int(TECHNIQUES["method: cairn"]["units"])
    c = w.s["containers"][cid]
    b = w.p["bury"]
    if w.cold():
        return int(b["frozen"])
    cov = w.s["parcels"].get(c.get("parcel"), {}).get("cover", "field")
    hill = w.s["parcels"].get(c.get("parcel"), {}).get("ground") == "hill"
    return int(b["stony" if hill or COVERS.get(cov, {}).get("dig") == "stony" else "soft"])
