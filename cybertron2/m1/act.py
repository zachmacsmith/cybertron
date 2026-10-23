"""The verbs (docs/cybertron2/proposals/verbs.md), the single-node subset. Each action is a verb and its object; techniques are data
(data.TECHNIQUES). Every refusal says what is short and costs nothing.

    gather {what, at}            forage, cut withies, dig clay, glean, hunt, fell, fish, at a parcel
    make {what, qty?}            a recipe (bread, pottage, pot, basket, line, club)
    build {what, at}             a fitting on built ground (a firing pit)
    work {what, at}              reap (a ripe field), repair (your house)
    move {item, qty, to}         between your hands and your house's stock ("house" or "hands")
    give {to, item, qty}         to someone here
    accept {offer}               an open offer made to you (or to anyone): both sides at once, or nothing
    set {thing: door, to}        your house's door: open or barred
    attack {target, aim}         a person (aim: rob or hurt) or a house (aim: rob): settled at night
    guard                        stand guard tonight
    steal {item, qty, from}      from a house's stock, unseen if you can be
    watch {person}               spend the day working beside them (learning by watching)
    teach {to, what} / learn {from, what}   one session, both the same day
    rest
"""
from __future__ import annotations

from cybertron2.m1 import knowledge as KN
from cybertron2.m1.data import EDIBLE, ITEMS, TECHNIQUES, TRY, WEAPONS
from cybertron2.m1.world import World, show

VERBS = ("gather", "make", "build", "work", "move", "give", "accept", "set", "attack", "guard", "steal", "watch", "teach", "learn",
         "rest")
FREE = ("move", "give", "accept", "set", "rest")


class Refused(Exception):
    pass


def _qty(x, default=1.0) -> float:
    if x is None:
        return default
    try:
        q = float(x)
    except (TypeError, ValueError):
        raise Refused("qty must be a number")
    if q <= 0:
        raise Refused("qty must be positive")
    return q


def _item(x) -> str:
    i = str(x or "").strip().lower()
    i = {"pots": "pot", "baskets": "basket", "clubs": "club", "loaves": "bread", "loaf": "bread", "lines": "line"}.get(i, i)
    if i not in ITEMS:
        raise Refused(f"there is no such thing as {x!r} here (goods: {', '.join(ITEMS)})")
    return i


def cost(w: World, name, a) -> int:
    v = str((a or {}).get("do", "")).lower().strip()
    if v in FREE:
        return 0
    if v in ("gather", "make", "build", "work"):
        tech = KN.resolve(a.get("what"))
        if tech is None:
            return 1
        n = int(TECHNIQUES[tech]["units"])
        if v == "make":
            n *= max(1, int(_qty(a.get("qty"), 1)))
        return n
    return {"attack": int(w.p["combat"]["units"]), "guard": 1, "steal": 1, "watch": int(w.p["watch"]["units"]),
            "teach": int(w.p["teach"]["units_teacher"]), "learn": int(w.p["teach"]["units_learner"])}.get(v, 1)


def do(w: World, name: str, a: dict, today: dict) -> str:
    """Carry out one action; returns the agent's result line. Happenings are logged with w.happen."""
    v = str((a or {}).get("do", "")).lower().strip()
    try:
        if v not in VERBS:
            raise Refused(f"unknown verb {v!r}; the verbs are {', '.join(VERBS)}")
        return globals()["_" + v](w, name, a, today)
    except Refused as e:
        return f"Refused: {v or 'action'}: {e}"


def _parcel(w, x, what=""):
    pid = w.parcel_by_name(x)
    if pid is None:
        raise Refused(f"there is no place called {x!r} here" + (f" to {what}" if what else ""))
    return pid


def _skill_mult(w, name, tech) -> float:
    return (0.6 + 0.4 * KN.skill(w, name, tech)) * w.yield_mult(name)


def _level_or_refuse(w, name, tech):
    lvl = KN.level(w, name, tech)
    if lvl is None:
        raise Refused(f"{TECHNIQUES[tech]['label'].split(' (')[0]} is not among your crafts: you have never learned it")
    if lvl == "aware":
        raise Refused(f"you know of {TECHNIQUES[tech]['label'].split(' (')[0]}, but have no idea how it is done (watch someone, ask to "
                      f"be taught, or have it explained)")
    return lvl


def _add(store, item, q):
    store[item] = round(store.get(item, 0.0) + q, 6)


# ---------------------------------------------------------------------- gather and work on land
def _gather(w, name, a, today):
    tech = KN.resolve(a.get("what"))
    if tech is None or TECHNIQUES[tech]["verb"] != "gather":
        raise Refused(f"{a.get('what')!r} is not something you gather (gathering: forage, cut withies, dig clay, glean, hunt, fell, fish)")
    lvl = _level_or_refuse(w, name, tech)
    pid = _parcel(w, a.get("at") or "", tech) if a.get("at") else None
    if pid is None:
        opts = [x for x in KN._where(w, name, tech) if x[0] == "parcel"]
        if not opts:
            raise Refused(f"there is nowhere here to {tech}")
        pid = opts[0][1]
    why = KN.shortfall(w, name, tech, 1.0, pid)
    if why:
        raise Refused(why)
    me = w.s["agents"][name]
    p = w.parcels()[pid]
    st = p["state"]
    pp = w.p
    m = _skill_mult(w, name, tech)
    today["worked"].setdefault(name, []).append(pid)
    got, word = 0.0, ""
    rng = w.rng("gather", w.d, name, len(today["worked"][name]))
    if tech == "forage":
        pl = st.get("plants")
        if not pl:
            raise Refused(f"there is nothing to forage at {p['name']}")
        y = pp["forage"]["yield"] * pl["S"] / pl["K"] * m
        got = round(max(0.0, min(y, pl["S"] - pp["forage"]["refuge"] * pl["K"])), 2)
        pl["S"] = round(pl["S"] - got, 4)
        _add(me["holdings"], "greens", got)
        word = f"You foraged {show(got)} greens at {p['name']}."
    elif tech == "hunt":
        g = st.get("game")
        if not g:
            raise Refused(f"there is no game at {p['name']}")
        if rng.random() < pp["hunt"]["p"] * g["S"] / g["K"]:
            got = round(min(g["S"], rng.uniform(*pp["hunt"]["food"]) * m), 2)
            g["S"] = round(g["S"] - got, 4)
            _add(me["holdings"], "meat", got)
            word = f"You hunted in {p['name']} and brought down game: {show(got)} meat."
        else:
            word = f"You hunted in {p['name']} and caught nothing."
    elif tech == "fell":
        got = round(pp["fell"]["timber"] * m, 2)
        _add(me["holdings"], "timber", got)
        st["felled"] = int(st.get("felled", 0)) + 1
        word = f"You felled {show(got)} timber in {p['name']}."
    elif tech == "fish":
        f = st.get("fish")
        if not f:
            raise Refused(f"there are no fish at {p['name']}")
        if rng.random() < pp["fish"]["p"] * f["S"] / f["K"]:
            got = round(min(f["S"], rng.uniform(*pp["fish"]["food"]) * m), 2)
            f["S"] = round(f["S"] - got, 4)
            _add(me["holdings"], "fish", got)
            word = f"You fished {p['name']}: {show(got)} fish."
        else:
            word = f"You fished {p['name']} and caught nothing."
    elif tech == "dig clay":
        got = pp["clay"]
        _add(me["holdings"], "clay", got)
        word = f"You dug {show(got)} clay from the bank of {p['name']}."
    elif tech == "cut withies":
        got = pp["withies"]
        _add(me["holdings"], "withies", got)
        word = f"You cut {show(got)} withies at {p['name']}."
    elif tech == "glean":
        c = st.get("crop")
        if not c or not c.get("reaped"):
            raise Refused(f"{p['name']} has not been reaped; there is nothing to glean")
        got = round(min(pp["glean"]["grain"] * m, float(c.get("gleanings", 0.0))), 2)
        if got <= 0:
            raise Refused(f"{p['name']} has been gleaned bare")
        c["gleanings"] = round(c["gleanings"] - got, 4)
        _add(me["holdings"], "grain", got)
        word = f"You gleaned {show(got)} grain from {p['name']}."
    KN.tried(w, name, tech, got > 0)
    w.happen("work", f"{name} was {TECHNIQUES[tech]['label'].split(' (')[0]} at {p['name']}", actor=name, parcel=pid,
             salience=0.15, tags=TECHNIQUES[tech]["tags"], extra={"tech": tech})
    return word


def _work(w, name, a, today):
    tech = KN.resolve(a.get("what"))
    if tech not in ("reap", "repair"):
        raise Refused(f"{a.get('what')!r} is not work you can do (work: reap a ripe field, repair your house)")
    me = w.s["agents"][name]
    if tech == "repair":
        h = w.home(name)
        if h is None:
            raise Refused("you have no house")
        if h["condition"] >= 2:
            return f"{h['name']} is sound: nothing to repair."
        need = 2.0
        have = me["holdings"].get("timber", 0.0) + h["stock"].get("timber", 0.0)
        if have + 1e-9 < need:
            raise Refused(f"a repair needs 2 timber; you and your house have {show(have)}")
        take = min(need, me["holdings"].get("timber", 0.0))
        me["holdings"]["timber"] = round(me["holdings"].get("timber", 0.0) - take, 6)
        h["stock"]["timber"] = round(h["stock"].get("timber", 0.0) - (need - take), 6)
        h["condition"] += 1
        w.happen("work", f"{name} repaired {h['name']}", actor=name, parcel=h["parcel"], salience=0.3, tags=["building", "shelter"])
        return f"You repaired {h['name']}: it is now {('ruined', 'damaged', 'sound')[h['condition']]}."
    _level_or_refuse(w, name, tech)
    pid = _parcel(w, a.get("at"), "reap") if a.get("at") else next((x[1] for x in KN._where(w, name, tech) if KN._crop_ripe(w, x[1])), None)
    if pid is None:
        raise Refused("no field here has a ripe crop")
    why = KN.shortfall(w, name, tech, 1.0, pid)
    if why:
        raise Refused(why)
    c = w.parcels()[pid]["state"]["crop"]
    got = round(min(float(c["left"]), w.p["reap"]["grain"] * _skill_mult(w, name, tech)), 2)
    c["left"] = round(c["left"] - got, 4)
    c["reaped"] = True
    c["gleanings"] = round(float(c.get("gleanings", 0.0)) + got * 0.08, 4)
    _add(me["holdings"], "grain", got)
    today["worked"].setdefault(name, []).append(pid)
    KN.tried(w, name, tech, True)
    w.happen("work", f"{name} was reaping {w.parcels()[pid]['name']}", actor=name, parcel=pid, salience=0.25,
             tags=["farming", "harvest", "food"], extra={"tech": tech})
    left = " That field is now reaped bare." if c["left"] <= 1e-9 else ""
    return f"You reaped {show(got)} grain from {w.parcels()[pid]['name']}.{left}"


# ---------------------------------------------------------------------- make and build
def _make(w, name, a, today):
    tech = KN.resolve(a.get("what"))
    if tech is None or TECHNIQUES[tech]["verb"] != "make":
        raise Refused(f"{a.get('what')!r} is not something you make (recipes: bread, pottage, pot, basket, line, club)")
    lvl = _level_or_refuse(w, name, tech)
    qty = max(1, int(_qty(a.get("qty"), 1)))
    t = TECHNIQUES[tech]
    mult = TRY[lvl]["inputs"]
    me = w.s["agents"][name]
    out = []
    for i in range(qty):
        why = KN.shortfall(w, name, tech, mult)
        if why:
            out.append(f"Refused: make {tech}: {why}")
            break
        for item, q in (t["needs"].get("inputs") or {}).items():
            me["holdings"][item] = round(me["holdings"][item] - q * mult, 6)
        ok = w.rng("make", w.d, name, tech, i).random() < TRY[lvl]["chance"]
        rose = KN.tried(w, name, tech, ok)
        if ok:
            for item, q in t["gives"].items():
                _add(me["holdings"], item, q)
            out.append(f"You made {', '.join(f'{q:g} {it}' for it, q in t['gives'].items())}." + (f" (You are now {rose} at it.)" if rose else ""))
        else:
            out.append(f"Your try at {t['label'].split(' (')[0]} failed and the materials are spoilt." + (f" (You are now {rose} at it.)" if rose else ""))
        w.happen("make", f"{name} was {t['label'].split(' (')[0]}" + ("" if ok else ", and it went wrong"), actor=name,
                 parcel=w.home(name)["parcel"] if w.home(name) else None, salience=0.2, tags=t["tags"], extra={"tech": tech})
    return " ".join(out)


def _build(w, name, a, today):
    tech = KN.resolve(a.get("what"))
    if tech is None or TECHNIQUES[tech]["verb"] != "build":
        raise Refused(f"{a.get('what')!r} is not something you build (building: firing pit)")
    lvl = _level_or_refuse(w, name, tech)
    pid = _parcel(w, a.get("at"), "build") if a.get("at") else next((x[1] for x in KN._where(w, name, tech)), None)
    if pid is None or w.parcels()[pid]["cover"] not in TECHNIQUES[tech]["needs"].get("at", []):
        raise Refused(f"a {tech} is built on built ground (the green and the houses)")
    mult = TRY[lvl]["inputs"]
    why = KN.shortfall(w, name, tech, mult, pid)
    if why:
        raise Refused(why)
    me = w.s["agents"][name]
    for item, q in (TECHNIQUES[tech]["needs"].get("inputs") or {}).items():
        me["holdings"][item] = round(me["holdings"][item] - q * mult, 6)
    ok = w.rng("build", w.d, name, tech).random() < TRY[lvl]["chance"]
    KN.tried(w, name, tech, ok)
    if not ok:
        w.happen("build", f"{name} tried to build a {tech} on {w.parcels()[pid]['name']}, and it fell in", actor=name, parcel=pid,
                 salience=0.4, tags=TECHNIQUES[tech]["tags"], extra={"tech": tech})
        return f"Your {tech} fell in before it was done; the materials are spoilt."
    w.s["fittings"].append({"kind": tech, "parcel": pid, "owner": name, "name": f"{name}'s {tech}", "day": w.d})
    w.happen("build", f"{name} built a {tech} on {w.parcels()[pid]['name']}", actor=name, parcel=pid, salience=0.6,
             tags=TECHNIQUES[tech]["tags"], extra={"tech": tech})
    return f"You built a {tech} on {w.parcels()[pid]['name']}."


# ---------------------------------------------------------------------- goods
def _move(w, name, a, today):
    me = w.s["agents"][name]
    h = w.home(name)
    if h is None:
        raise Refused("you have no house")
    item = _item(a.get("item"))
    to = str(a.get("to") or "house").strip().lower().removeprefix("the ").removeprefix("my ").removeprefix("your ")
    hid = w.house_by_name(to)
    if to in ("hands", "hand", "me", "myself", "self", "pack", "carried", "carry"):
        src, dst, verb = h["stock"], me["holdings"], "took"
    elif to in ("house", "store", "home", "the store", "house store", "stock") or hid == w.s["agents"][name]["house"]:
        src, dst, verb = me["holdings"], h["stock"], "put"
    elif hid:
        raise Refused(f"you can store only in your own house ({h['name']}); to hand goods to someone, use give")
    else:
        raise Refused('move {"item", "qty", "to": "house"} to store, or "to": "hands" to take from your store')
    have = src.get(item, 0.0)
    q = _qty(a.get("qty"), have)
    if have <= 1e-9:
        raise Refused(f"there is no {item} " + ("in your hands" if verb == "put" else f"in {h['name']}"))
    q = round(min(q, have), 6)                                             # as much as there is
    src[item] = round(src[item] - q, 6)
    _add(dst, item, q)
    w.happen("store" if verb == "put" else "take", f"{name} {verb} {item} {'into' if verb == 'put' else 'from'} {h['name']}", actor=name,
             parcel=h["parcel"], salience=0.1, tags=["food"] if item in EDIBLE else [], extra={"house": w.s["agents"][name]["house"]})
    return f"You {verb} {show(q)} {item} {'into' if verb == 'put' else 'from'} {h['name']} (it holds {show(h['stock'].get(item, 0.0))})."


def _give(w, name, a, today):
    to = w.person(a.get("to"))
    if to is None or not w.s["agents"][to]["alive"]:
        raise Refused(f"there is nobody called {a.get('to')!r} here")
    if to == name:
        raise Refused("you cannot give to yourself")
    item, q = _item(a.get("item")), _qty(a.get("qty"))
    me = w.s["agents"][name]
    if me["holdings"].get(item, 0.0) + 1e-9 < q:
        raise Refused(f"you carry only {show(me['holdings'].get(item, 0.0))} {item}")
    me["holdings"][item] = round(me["holdings"][item] - q, 6)
    _add(w.s["agents"][to]["holdings"], item, q)
    w.happen("give", f"{name} gave {q:g} {item} to {to}", actor=name, target=to, salience=0.35, tags=["food"] if item in EDIBLE else [],
             concerns=[to])
    return f"You gave {q:g} {item} to {to}."


def _accept(w, name, a, today):
    oid = str(a.get("offer", "")).strip()
    o = w.s["offers"].get(oid)
    if o is None or not o["open"]:
        raise Refused(f"there is no open offer {oid!r}")
    if o["to"] not in (None, name):
        raise Refused(f"offer {oid} was made to {o['to']}, not you")
    by = o["by"]
    if by == name:
        raise Refused("that is your own offer")
    A, B = w.s["agents"][by]["holdings"], w.s["agents"][name]["holdings"]
    for item, q in o["give"].items():
        if not o.get("held") and A.get(item, 0.0) + 1e-9 < q:
            raise Refused(f"{by} no longer has {q:g} {item}; nothing was exchanged")
    mine = (w.home(name) or {}).get("stock", {})                         # the taker pays from hand, then its own house's store
    for item, q in o["get"].items():
        if B.get(item, 0.0) + mine.get(item, 0.0) + 1e-9 < q:
            raise Refused(f"you and your house's store have only {show(B.get(item, 0.0) + mine.get(item, 0.0))} {item}; nothing was exchanged")
    for item, q in o["get"].items():
        short = q - B.get(item, 0.0)
        if short > 1e-9:
            mine[item] = round(mine[item] - short, 6)
            _add(B, item, short)
    for item, q in o["give"].items():
        if not o.get("held"):
            A[item] = round(A[item] - q, 6)
        _add(B, item, q)
    for item, q in o["get"].items():
        B[item] = round(B[item] - q, 6)
        _add(A, item, q)
    o["open"] = False
    o["taken_by"] = name
    w.happen("trade", f"{name} and {by} exchanged {_goods(o['get'])} for {_goods(o['give'])}", actor=name, target=by, salience=0.35,
             tags=["trade"], concerns=[by])
    return f"You accepted {by}'s offer: you gave {_goods(o['get'])} and received {_goods(o['give'])}."


def _goods(d) -> str:
    return ", ".join(f"{q:g} {i}" for i, q in d.items()) or "nothing"


def _set(w, name, a, today):
    h = w.home(name)
    if h is None:
        raise Refused("you have no house")
    to = str(a.get("to") or a.get("setting") or "").lower()
    if to not in ("open", "barred"):
        raise Refused('set {"thing": "door", "to": "open" or "barred"}')
    h["door"] = to
    return f"{h['name']}'s door is now {to}."


# ---------------------------------------------------------------------- force
def _attack(w, name, a, today):
    tgt = str(a.get("target", ""))
    aim = str(a.get("aim", "rob")).lower()
    who = w.person(tgt)
    hid = w.house_by_name(tgt)
    if who and who != name and w.s["agents"][who]["alive"]:
        today["fights"].append({"kind": "attack", "by": name, "target": who, "aim": "hurt" if aim == "hurt" else "rob"})
        w.happen("threat", f"{name} squared up to {who}", actor=name, target=who, salience=0.7, tags=["danger"], concerns=[who])
        return f"You set on {who} ({aim}); it is settled tonight."
    if hid:
        if hid == w.s["agents"][name]["house"]:
            raise Refused("that is your own house")
        today["fights"].append({"kind": "raid", "by": name, "house": hid})
        return f"You make ready to raid {w.s['houses'][hid]['name']} tonight."
    raise Refused(f"no person or house called {tgt!r} here")


def _guard(w, name, a, today):
    if name not in today["guards"]:
        today["guards"].append(name)
    return "You stand guard tonight."


def _steal(w, name, a, today):
    hid = w.house_by_name(a.get("from"))
    if hid is None:
        raise Refused(f"no house called {a.get('from')!r} here")
    h = w.s["houses"][hid]
    if hid == w.s["agents"][name]["house"]:
        raise Refused("that is your own house's stock; use move")
    if h["door"] == "barred":
        raise Refused(f"{h['name']}'s door is barred")
    item, q = _item(a.get("item")), _qty(a.get("qty"))
    q = min(q, h["stock"].get(item, 0.0))
    if q <= 1e-9:
        raise Refused(f"you find no {item} in {h['name']}")
    h["stock"][item] = round(h["stock"][item] - q, 6)
    _add(w.s["agents"][name]["holdings"], item, q)
    today["steals"].append({"by": name, "house": hid, "item": item, "qty": round(q, 2)})
    return f"You took {show(q)} {item} from {h['name']}. Whether anyone saw, you will learn."


def settle_fights(w) -> list:
    """Attacks and raids queued today, settled at night (a simplified harm model, as cybertron2/combat.py)."""
    today = w.s.get("today") or {}
    fights, guards = today.get("fights", []), set(today.get("guards", []))
    cc = w.p["combat"]
    out = []

    def strength(n, base):
        x = w.s["agents"][n]
        weapon = max((WEAPONS[i] for i in WEAPONS if x["holdings"].get(i, 0.0) >= 1), default=0.0)
        return x[base] * w.yield_mult(n) + weapon

    def rob(victim_store, takers, share=1.0):
        took = 0.0
        for item in EDIBLE:
            q = round(victim_store.get(item, 0.0) * share, 6)
            if q > 0:
                victim_store[item] = round(victim_store[item] - q, 6)
                for t in takers:
                    _add(w.s["agents"][t]["holdings"], item, q / len(takers))
                took += q * ITEMS[item]["food"]
        return round(took, 2)

    for f in fights:
        rng = w.rng("fight", w.d, f["by"], f.get("target") or f.get("house"))
        if not w.s["agents"][f["by"]]["alive"]:
            continue
        P = strength(f["by"], "attack")
        if f["kind"] == "raid":
            h = w.s["houses"][f["house"]]
            defenders = [n for n in w.living() if (w.s["agents"][n]["house"] == f["house"] or n in guards) and n != f["by"]]
            D = sum(strength(d, "defence") + (cc["guard"] if d in guards else 0.0) * 1.0 if d in guards else cc["asleep"] * strength(d, "defence")
                    for d in defenders)
            X = 2 * (D + 1)
            if rng.random() < P ** 2 / (P ** 2 + (X / 2) ** 2):
                took = rob(h["stock"], [f["by"]], cc["raid_share"])
                rec = {"kind": "raid", "by": f["by"], "house": f["house"], "outcome": "taken", "took": took}
                w.happen("raid", f"In the night {h['name']} was raided and food taken", actor=f["by"], parcel=h["parcel"], salience=0.95,
                         tags=["danger", "food"], concerns=[n for n in w.living() if w.s["agents"][n]["house"] == f["house"]],
                         extra={"house": f["house"]})
            else:
                rec = {"kind": "raid", "by": f["by"], "house": f["house"], "outcome": "repelled"}
                w.happen("raid", f"In the night someone tried to break into {h['name']} and was driven off by {', '.join(defenders) or 'nobody'}",
                         actor=f["by"], parcel=h["parcel"], salience=0.95, tags=["danger"], concerns=defenders)
            out.append(rec)
            continue
        t = f["target"]
        if not w.s["agents"][t]["alive"]:
            continue
        helpers = [g for g in guards if g not in (t, f["by"])]
        D = strength(t, "defence") + (cc["guard"] if t in guards else 0.0) + sum(strength(g, "defence") for g in helpers)
        X = 2 * (D + 1)
        p_kill = P ** 2 / (P ** 2 + X ** 2) if f["aim"] == "hurt" else 0.0
        p_wound = P ** 2 / (P ** 2 + (X / 2) ** 2)
        u = rng.random()
        if u < p_kill:
            w.die(t, "attack", to={f["by"]: 1.0})
            rec = {"kind": "attack", "by": f["by"], "target": t, "outcome": "killed", "killed": t}
            w.happen("death", f"{t} was killed by {f['by']}", actor=f["by"], target=t, salience=1.0, tags=["danger", "death"])
        elif u < p_wound:
            took = rob(w.s["agents"][t]["holdings"], [f["by"]])
            w.s["agents"][t]["wounded"] = True
            w.s["agents"][t]["hunger"] = -2
            rec = {"kind": "attack", "by": f["by"], "target": t, "outcome": "wounded", "took": took}
            w.happen("fight", f"{f['by']} beat {t} and took what food {t} carried", actor=f["by"], target=t, salience=0.95,
                     tags=["danger"], concerns=[t])
        else:
            rec = {"kind": "attack", "by": f["by"], "target": t, "outcome": "repelled"}
            w.happen("fight", f"{f['by']} set on {t} and was beaten off", actor=f["by"], target=t, salience=0.9, tags=["danger"],
                     concerns=[t])
        out.append(rec)
    return out


# ---------------------------------------------------------------------- learning from others
def _watch(w, name, a, today):
    who = w.person(a.get("person") or a.get("to") or a.get("target"))
    if who is None or who == name or not w.s["agents"][who]["alive"]:
        raise Refused(f"there is nobody called {a.get('person')!r} here to watch")
    today["watch"][name] = who
    return f"You spend the day working beside {who}, watching how they do things."


def _teach(w, name, a, today):
    to = w.person(a.get("to"))
    tech = KN.resolve(a.get("what"))
    if to is None or to == name:
        raise Refused(f"there is nobody called {a.get('to')!r} here to teach")
    if tech is None:
        raise Refused(f"{a.get('what')!r} is not something you can teach")
    if KN.level(w, name, tech) != "known":
        raise Refused(f"you do not know {TECHNIQUES[tech]['label'].split(' (')[0]} well enough to teach it")
    today["teach"].append({"by": name, "to": to, "tech": tech})
    return f"You set aside time to teach {to} {TECHNIQUES[tech]['label'].split(' (')[0]}; it happens if {to} also sets aside time to learn."


def _learn(w, name, a, today):
    frm = w.person(a.get("from"))
    tech = KN.resolve(a.get("what"))
    if frm is None or frm == name:
        raise Refused(f"there is nobody called {a.get('from')!r} here to learn from")
    if tech is None:
        raise Refused(f"{a.get('what')!r} is not something you can learn here")
    today["learn"].append({"by": name, "from": frm, "tech": tech})
    return f"You set aside time to learn {TECHNIQUES[tech]['label'].split(' (')[0]} from {frm}; it happens if {frm} also sets aside time to teach."


def settle_teaching(w, today) -> dict:
    """Teaching happens when a teach and a learn match the same day. Returns {agent: [result lines]}."""
    out = {}
    for t in today["teach"]:
        match = next((l for l in today["learn"] if l["by"] == t["to"] and l["from"] == t["by"] and l["tech"] == t["tech"]), None)
        label = TECHNIQUES[t["tech"]]["label"].split(" (")[0]
        target = "known" if w.s["agents"][t["to"]]["stage"] == "youth" else "capable"
        if match and KN.LEVELS.index(KN.level(w, t["to"], t["tech"]) or "aware") >= KN.LEVELS.index(target):
            out.setdefault(t["by"], []).append(f"{t['to']} already has {label} as well as a day's teaching can give; you lost the day's time.")
            out.setdefault(t["to"], []).append(f"{t['by']} had nothing more to teach you of {label} that a day could give; practice is what you need.")
        elif match:
            res = KN.taught(w, t["by"], t["to"], t["tech"])
            out.setdefault(t["by"], []).append(f"You taught {t['to']} {label}.")
            out.setdefault(t["to"], []).append(f"{t['by']} taught you {label} ({res}).")
            w.happen("teach", f"{t['by']} spent the day teaching {t['to']} {label}", actor=t["by"], target=t["to"], salience=0.3,
                     tags=TECHNIQUES[t["tech"]]["tags"], concerns=[t["to"]])
        else:
            out.setdefault(t["by"], []).append(f"You meant to teach {t['to']} {label}, but {t['to']} did not set aside time to learn.")
    for l in today["learn"]:
        if not any(t["by"] == l["from"] and t["to"] == l["by"] and t["tech"] == l["tech"] for t in today["teach"]):
            out.setdefault(l["by"], []).append(f"You meant to learn from {l['from']}, but {l['from']} did not set aside time to teach you.")
    return out


def _rest(w, name, a, today):
    return "You rested."
