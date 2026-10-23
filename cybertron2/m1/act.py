"""The verbs (docs/cybertron2/proposals/verbs.md), the single-node subset. Each action is a verb and its object; techniques are data
(data.TECHNIQUES). Every refusal says what is short and costs nothing.

    gather {what, at}            forage, hunt, fell, at a parcel (felling and reaping by tool: recipes.md §9)
    make {what, qty?}            grind (grain to flour at the house's quern), bread, crude weapon
    work {what, at}              reap (a ripe field), milk (a cow in milk), repair (your house)
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
from cybertron2.m1.data import EDIBLE, ITEMS, TECHNIQUES, TOOL_MULT, TOOLS, TRY, WEAPONS
from cybertron2.m1.world import World, show

# The verb registry (cybertron 1's action_registry): each verb's arguments, its cost and its line in the manual, declared once.
# The prompt's verb list (prompt.verb_lines), the schema's verbs and cost() come from here. cost: a number of units, a physics
# key path (a list), or "craft" (the technique's units, times qty for make). doc may name {crafts}: the techniques of this verb
# the agent knows of (D4-24: what it has not heard of is not listed).
VERB = {
    "travel": {"args": '{"to": a place}', "cost": 0, "when": "roads",
               "doc": "the day's last act: you leave at nightfall and arrive on a later morning"},
    "welcome": {"args": '{"person"}', "cost": 0, "when": "roads", "doc": "let a visitor sleep in your house tonight"},
    "gather": {"args": '{"what", "at": place}', "cost": "craft", "doc": "take from the land: {crafts}"},
    "make": {"args": '{"what", "qty"?: how many times}', "cost": "craft", "doc": "a recipe: {crafts}"},
    "work": {"args": '{"what", "at"?: place}', "cost": "craft", "doc": "{crafts}"},
    "move": {"args": '{"item", "qty", "to": house | hands}', "cost": 0,
             "doc": '"house" puts it in your house\'s store, "hands" takes it out (at home)'},
    "give": {"args": '{"to": person, "item", "qty"}', "cost": 0, "doc": "to someone here"},
    "accept": {"args": '{"offer": id}', "cost": 0, "doc": "an open offer made to you or to anyone here: both sides at once, or nothing"},
    "set": {"args": '{"thing": door, "to": open | barred}', "cost": 0, "doc": "your house's door"},
    "watch": {"args": '{"person"}', "cost": ["watch", "units"], "doc": "spend the day working beside them: you see how they do things"},
    "teach": {"args": '{"to", "what"}', "cost": ["teach", "units_teacher"], "doc": "one session, if they set aside time to learn the same day"},
    "learn": {"args": '{"from", "what"}', "cost": ["teach", "units_learner"], "doc": "one session, if they set aside time to teach the same day"},
    "attack": {"args": '{"target": person | house, "aim": rob | hurt}', "cost": ["combat", "units"], "doc": "settled tonight"},
    "guard": {"args": "", "cost": 1, "doc": "stand guard tonight over your house and anyone set upon"},
    "steal": {"args": '{"from": house, "item", "qty"}', "cost": 1, "doc": "from a house whose door is not barred; you may be seen"},
    "rest": {"args": "", "cost": 0, "doc": ""},
}
VERBS = tuple(VERB)
FREE = tuple(v for v, d in VERB.items() if d["cost"] == 0)


def verb_here(w, name, verb) -> bool:
    """Whether a verb exists for this agent in this world (cybertron 1's `when`): travel and welcome only where there are roads."""
    when = VERB[verb].get("when")
    return not when or (when == "roads" and bool(w.s["edges"].get(w.at(name)) or len(w.s["nodes"]) > 1))


def verb_units(w, verb):
    """A verb's fixed cost in units, or None when it depends on the craft."""
    c = VERB[verb]["cost"]
    if c == "craft":
        return None
    if isinstance(c, list):
        x = w.p
        for k in c:
            x = x[k]
        return int(x)
    return int(c)


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
    i = {"loaves": "bread", "loaf": "bread", "greens": "wild food", "food": "wild food", "weapon": "crude weapon",
         "tool": "crude tool", "tools": "crude tool"}.get(i, i)
    if i not in ITEMS:
        raise Refused(f"there is no such thing as {x!r} here (goods: {', '.join(ITEMS)})")
    return i


def cost(w: World, name, a) -> int:
    v = str((a or {}).get("do", "")).lower().strip()
    if v not in VERB:
        return 0
    n = verb_units(w, v)
    if n is not None:
        return n
    tech = KN.resolve(a.get("what"))
    if tech is None:
        return 1
    n = int(TECHNIQUES[tech]["units"])
    if v == "make":
        n *= max(1, int(_qty(a.get("qty"), 1)))
    return n


def do(w: World, name: str, a: dict, today: dict) -> str:
    """Carry out one action; returns the agent's result line. Happenings are logged with w.happen."""
    v = str((a or {}).get("do", "")).lower().strip()
    try:
        if v in VERB and not verb_here(w, name, v):
            raise Refused(f"there is no {v} in this world")
        if v not in VERBS:
            raise Refused(f"unknown verb {v!r}; the verbs are {', '.join(VERBS)}")
        return globals()["_" + v](w, name, a, today)
    except Refused as e:
        return f"Refused: {v or 'action'}: {e}"


def _parcel(w, x, what="", name=None):
    pid = w.parcel_by_name(x, w.at(name) if name else None)
    if pid is None:
        raise Refused(f"there is no place called {x!r} here" + (f" to {what}" if what else ""))
    return pid


def _near(w, name, x):
    """A living person at the same node, or None."""
    who = w.person(x)
    return who if who and who != name and w.s["agents"][who]["alive"] and w.at(who) == w.at(name) else None


def _here_house(w, name, x):
    hid = w.house_by_name(x)
    return hid if hid and w.node_of(w.s["houses"][hid]["parcel"]) == w.at(name) else None


def _at_home(w, name):
    h = w.home(name)
    if h is None:
        raise Refused("you have no house")
    if w.node_of(h["parcel"]) != w.at(name):
        raise Refused(f"{h['name']} is at {w.s['nodes'][w.node_of(h['parcel'])]['name']}; you are not there")
    return h


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


def tool_of(me, tech):
    """The best hand tool it carries, and its multiplier for this method (recipes.md §9; bare hands below a crude tool)."""
    tool = next((t for t in TOOLS if me["holdings"].get(t, 0.0) >= 1), None)
    return tool, TOOL_MULT[tech][tool or "bare"]


def _add(store, item, q):
    store[item] = round(store.get(item, 0.0) + q, 6)


# ---------------------------------------------------------------------- gather and work on land
def _gather(w, name, a, today):
    tech = KN.resolve(a.get("what"))
    if tech is None or TECHNIQUES[tech]["verb"] != "gather":
        raise Refused(f"{a.get('what')!r} is not something you gather (gathering: forage, hunt, fell, mine)")
    lvl = _level_or_refuse(w, name, tech)
    pid = _parcel(w, a.get("at") or "", tech, name) if a.get("at") else None
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
        _add(me["holdings"], "wild food", got)
        word = f"You foraged {show(got)} wild food at {p['name']}."
    elif tech == "hunt":
        g = st.get("game")
        if not g:
            raise Refused(f"there is no game at {p['name']}")
        armed = any(me["holdings"].get(x, 0) >= 1 for x in WEAPONS)
        if rng.random() < pp["hunt"]["p"] * g["S"] / g["K"]:
            got = round(min(g["S"], rng.uniform(*pp["hunt"]["food"]) * m * (1.0 if armed else 0.3)), 2)   # recipes.md §9
            g["S"] = round(g["S"] - got, 4)
            _add(me["holdings"], "meat", got)
            word = f"You hunted in {p['name']} and brought down game: {show(got)} meat."
        else:
            word = f"You hunted in {p['name']} and caught nothing."
    elif tech == "fell":
        tool, tm = tool_of(me, "fell")
        got = round(pp["fell"]["timber"] * m * tm, 2)
        _add(me["holdings"], "timber", got)
        st["felled"] = int(st.get("felled", 0)) + 1
        word = f"You felled {show(got)} timber in {p['name']}" + (f" with your {tool}." if tool else " with your bare hands.")
    if tech == "mine":
        tool, tm = tool_of(me, "mine")
        if not tool:
            raise Refused("you cannot mine with your bare hands: you need a tool")
        seam = st.get("seam")
        if not seam or seam.get("left", 0) <= 1e-9:
            raise Refused(f"there is no ore left to mine at {p['name']}")
        got = round(min(seam["left"], pp["mine"]["ore"] * m * tm), 2)
        seam["left"] = round(seam["left"] - got, 4)
        _add(me["holdings"], "copper ore", got)
        word = f"You mined {show(got)} copper ore at {p['name']} with your {tool}."
    KN.tried(w, name, tech, got > 0)
    w.happen("work", f"{name} was {TECHNIQUES[tech]['label'].split(' (')[0]} at {p['name']}", actor=name, parcel=pid,
             salience=0.15, tags=TECHNIQUES[tech]["tags"], extra={"tech": tech})
    return word


def _work(w, name, a, today):
    tech = KN.resolve(a.get("what"))
    if tech not in ("reap", "repair", "milk"):
        raise Refused(f"{a.get('what')!r} is not work you can do (work: reap a ripe field, milk a cow in milk, repair your house)")
    me = w.s["agents"][name]
    if tech == "milk":
        _level_or_refuse(w, name, tech)
        hd = next((h for h in w.s["herds"].values() if int(h.get("in_milk", 0)) > 0
                   and w.parcels()[h["parcel"]]["cover"] == "pasture"), None)
        if hd is None:
            raise Refused("there is no cow in milk on the pasture")
        if hd.get("milked_day") != w.d:
            hd["milked_day"], hd["milked"] = w.d, 0
        if hd["milked"] >= int(hd["in_milk"]):
            raise Refused(f"the cows in milk have all been milked today ({hd['in_milk']} of them)")
        hd["milked"] += 1
        got = round(float(w.p["milk"]) * _skill_mult(w, name, tech), 2)
        _add(me["holdings"], "milk", got)
        KN.tried(w, name, tech, True)
        w.happen("work", f"{name} was milking a cow on {w.parcels()[hd['parcel']]['name']}", actor=name, parcel=hd["parcel"],
                 salience=0.2, tags=["animals", "food"], extra={"tech": tech})
        return f"You milked a cow: {show(got)} milk (it will not keep past tonight)."
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
    pid = _parcel(w, a.get("at"), "reap", name) if a.get("at") else next((x[1] for x in KN._where(w, name, tech) if KN._crop_ripe(w, x[1])), None)
    if pid is None:
        raise Refused("no field here has a ripe crop")
    why = KN.shortfall(w, name, tech, 1.0, pid)
    if why:
        raise Refused(why)
    c = w.parcels()[pid]["state"]["crop"]
    tool, tm = tool_of(me, "reap")
    got = round(min(float(c["left"]), w.p["reap"]["grain"] * _skill_mult(w, name, tech) * tm), 2)
    c["left"] = round(c["left"] - got, 4)
    c["reaped"] = True
    _add(me["holdings"], "grain", got)
    today["worked"].setdefault(name, []).append(pid)
    KN.tried(w, name, tech, True)
    w.happen("work", f"{name} was reaping {w.parcels()[pid]['name']}", actor=name, parcel=pid, salience=0.25,
             tags=["farming", "harvest", "food"], extra={"tech": tech})
    left = " That field is now reaped bare." if c["left"] <= 1e-9 else ""
    return f"You reaped {show(got)} grain from {w.parcels()[pid]['name']}" + (f" with your {tool}" if tool else " by hand") + f".{left}"


# ---------------------------------------------------------------------- make and build
def _make(w, name, a, today):
    tech = KN.resolve(a.get("what"))
    if tech is None or TECHNIQUES[tech]["verb"] != "make":
        raise Refused(f"{a.get('what')!r} is not something you make (recipes: grind, bread, crude weapon, smelt, copper tool, coin)")
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
    pid = _parcel(w, a.get("at"), "build", name) if a.get("at") else next((x[1] for x in KN._where(w, name, tech)), None)
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
    h = _at_home(w, name)
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
    to = _near(w, name, a.get("to"))
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
    if w.at(by) != w.at(name):
        raise Refused(f"{by} is not here; an offer is taken face to face")
    A, B = w.s["agents"][by]["holdings"], w.s["agents"][name]["holdings"]
    hb = w.home(by)
    theirs = hb["stock"] if hb is not None and w.node_of(hb["parcel"]) == w.at(by) else {}   # their store, if they are at home
    for item, q in o["give"].items():
        if not o.get("held") and A.get(item, 0.0) + theirs.get(item, 0.0) + 1e-9 < q:
            raise Refused(f"{by} no longer has {q:g} {item}; nothing was exchanged")
    hm = w.home(name)
    mine = hm["stock"] if hm is not None and w.node_of(hm["parcel"]) == w.at(name) else {}   # pays from hand, then its store at home
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
            a_ = min(q, A.get(item, 0.0))
            A[item] = round(A.get(item, 0.0) - a_, 6)
            if q - a_ > 1e-9:
                theirs[item] = round(theirs[item] - (q - a_), 6)
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
    who = _near(w, name, tgt)
    hid = _here_house(w, name, tgt)
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
    hid = _here_house(w, name, a.get("from"))
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
    who = _near(w, name, a.get("person") or a.get("to") or a.get("target"))
    if who is None or who == name or not w.s["agents"][who]["alive"]:
        raise Refused(f"there is nobody called {a.get('person')!r} here to watch")
    today["watch"][name] = who
    return f"You spend the day working beside {who}, watching how they do things."


def _teach(w, name, a, today):
    to = _near(w, name, a.get("to"))
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
    frm = _near(w, name, a.get("from"))
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


def _travel(w, name, a, today):
    """The day's last act (D4-8): the agent leaves at nightfall and arrives at the start of a later day (D4-10)."""
    here = w.at(name)
    x = str(a.get("to") or "").strip().lower().removeprefix("the ")
    to = next((nid for nid, n in w.s["nodes"].items() if x in (nid.lower(), n["name"].lower())), None)
    if to is None or to not in w.s["edges"].get(here, {}):
        ways = ", ".join(f"{w.s['nodes'][b]['name']} ({k} day{'s' if k > 1 else ''})" for b, k in w.s["edges"].get(here, {}).items())
        raise Refused(f"there is no way from here to {a.get('to')!r}; from here you can go to {ways or 'nowhere'}")
    load = sum(ITEMS[i]["weight"] * q for i, q in w.s["agents"][name]["holdings"].items() if q > 1e-9)
    cap = float(w.p["carry"]["foot"])
    if load > cap + 1e-9:
        raise Refused(f"you carry {show(load)} weight; on foot you can carry {cap:g}: leave something behind")
    today.setdefault("travel", {})[name] = to
    days = w.s["edges"][here][to]
    w.happen("depart", f"{name} set off toward {w.s['nodes'][to]['name']}", actor=name, salience=0.6, tags=["travel"],
             extra={"node": here})
    return (f"You set off for {w.s['nodes'][to]['name']} at the end of the day: {days} day{'s' if days > 1 else ''} on the road, "
            f"sleeping out; you arrive on the morning of day {w.d + days + 1}. Nothing more is done today.")


def _welcome(w, name, a, today):
    """A host lets a visitor sleep in its house tonight (spec/economy/lodging.md): sheltered as the household is."""
    who = _near(w, name, a.get("person") or a.get("to"))
    if who is None:
        raise Refused(f"there is nobody called {a.get('person') or a.get('to')!r} here to welcome")
    h = _at_home(w, name)
    today.setdefault("guests", {})[who] = w.s["agents"][name]["house"]
    w.happen("welcome", f"{name} took {who} in for the night at {h['name']}", actor=name, target=who, salience=0.4,
             tags=["shelter"], concerns=[who])
    return f"You welcome {who} to sleep at {h['name']} tonight."


def _rest(w, name, a, today):
    return "You rested."
