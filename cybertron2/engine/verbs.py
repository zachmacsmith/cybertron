"""The verbs (spec/agents/actions.md, proposals/verbs.md): each is a composition of primitives at the agent's node, reading only
`Here` and `Mind` (D4-35). Techniques, recipes, blueprints and fittings are data (D4-24): one handler for gathering and work, one
for making, one for building.

Each handler: (here, mind, a) -> result line. Refusals name what is short and cost nothing.
"""
from __future__ import annotations

import math
from cybertron2.engine import buildings as BL, farm as FM, knowledge as KN, modifiers as MOD, perceive as PC, things as TH
from cybertron2.engine.data import BLUEPRINTS, COVERS, FITTINGS, ITEMS, LINES, MONUMENTS, ROOMS, SPACE, TECHNIQUES, TIERS, TRY
from cybertron2.engine.here import Refused, show

# The registry (cybertron 1's action_registry): arguments, cost (units, a physics path, or "craft"), the line in the manual, and
# `when` (only in a world with roads). The prompt's verb list and the reply schema are generated from it.
VERB = {
    "gather": {"args": '{"what", "at"?: place, "for"?: party}', "cost": "craft", "doc": "take from the land: {crafts}"},
    "work": {"args": '{"what", "at"?: place or building, "item"?: the seed to sow (grain, rye, beans: always say which), the beast to slaughter (cow, ox, bull, calf), or food to give a child you care for (with "qty"), "on"?: in a field held in shares, whose plots (a household or person; else your own, then the unclaimed plots), "plots"?: how many plots to sow at most, "pass"?: with care, a sentence for the child to keep, "for"?: party}',
             "cost": "craft", "doc": "{crafts}"},
    "make": {"args": '{"what", "qty"?: times, "for"?: party}', "cost": "craft",
             "doc": "a recipe; the inputs come from what you carry, then from stores here you may take from: {crafts}"},
    "build": {"args": '{"what", "at": a place on built ground or scrub (a new building or a monument; a camp: any place here but water) or a building here (a room added, a fitting), "structure"?: wattle | timber | stone, "storey"?: 2 | 3, "qty"?: beds or stalls, "name"?, "describe"?: a sentence in your words, "how"?: fine | rich | grand, "for"?: party}',
              "cost": 2, "doc": "start or carry on a building, a room, a monument or a fitting: its materials when you start, then the work over days: {crafts}"},
    "move": {"args": '{"item", "qty", "to": store | hands, "at"?: building}', "cost": 0,
             "doc": "between your hands and a store here you may use (your household's)"},
    "take": {"args": '{"item", "qty", "from": a building, someone\'s remains, or a place where you know something lies}', "cost": 1,
             "doc": "from any store you can get into (without the right to it, it is theft, and you may be seen), or from what lies in the "
                    "open (nobody's: whoever takes it holds it)"},
    "give": {"args": '{"to": a person, a household, a building or a place here, "item", "qty", "for"?: your household, to give from its store, "hidden"?}',
             "cost": 0, "doc": "to a person here, into their hands; to a household, or a building you may use, into its store; to a "
                               "building you may not use, or someone not here, left at its door; to a place (a field, a wood), left "
                               "there in the open, where anyone may find it and take it. Leaving, putting down and hiding are giving "
                               "to a place"},
    "accept": {"args": '{"offer": id, "lots"?: n, "for"?: party}', "cost": 0, "doc": "an open offer here: both sides at once, or nothing"},
    "withdraw": {"args": '{"offer": id}', "cost": 0, "doc": "take back an offer of yours"},
    "release": {"args": '{"agreement": id}', "cost": 0,
                "doc": "count what is owed to you (or your household) on an agreement as paid, however it was paid, or forgive it"},
    "host": {"args": '{"person", "at"?: building, "feed"?: true}', "cost": 0,
             "doc": "let someone sleep in a house you may let people into, tonight (and eat from its store, if you feed them)"},
    "grant": {"args": '{"to": person or household or anyone, "at": building, "what": shelter | shelter and food, "days"?: n}', "cost": 0,
              "doc": "let someone use a house you may let people into, until you revoke it (or for some days)"},
    "revoke": {"args": '{"to", "at": building}', "cost": 0, "doc": "end what you granted"},
    "join": {"args": '{"household"}', "cost": 0, "doc": "ask to be taken into a household here; it happens if one who may admit you does so today"},
    "admit": {"args": '{"person"}', "cost": 0, "doc": "take someone into your household, if they ask today (the head, or whoever your household allows)"},
    "leave_household": {"args": "", "cost": 0, "doc": "leave your household (you keep what you carry)"},
    "found": {"args": '{"name"}', "cost": 0, "doc": "start a household of your own, with you at its head"},
    "claim": {"args": '{"thing": a field, building or herd here, "plots"?: of a field, pasture or meadow, how many of its plots (else all of them), "for"?: your household}', "cost": 0,
              "doc": "claim it as yours: others will know, and may agree or dispute it"},
    "drive": {"args": '{"thing": a herd here, "item"?: cows | oxen | bulls | calves | all, "qty"?, "to": a place here}', "cost": 1,
              "when": "herds", "doc": "move beasts to another place here (a bull kept apart from the cows does not breed)"},
    "sleep": {"args": '{"at": building}', "cost": 0, "doc": "sleep there tonight, if you can get in and a bed is free"},
    "set": {"args": '{"thing": door, "to": open | barred, "at"?: building}', "cost": 0, "doc": "the door of a building you manage"},
    "travel": {"args": '{"to": a place, or a way from here as the roads name it, "on trouble"?: push on | wait | turn back | go round, "days"?: how long to wait or stop, "stop at"?: a good place you know on the way, "gather"?: true, "meeting"?: stop | pass by, "searching"?: a herd or a person lost on that road, "lead"?: a herd of yours here with an ox, to lead an ox as a pack ox (a harness in hands; it carries 60)}',
               "cost": 0, "when": "roads", "doc": "the day's last act: you leave at nightfall and arrive on a later morning. On the road "
                                                 "you decide nothing unless something happens (trouble, a meeting, a find); what you "
                                                 "choose here is what you do if the road gives trouble, and whether you stop for "
                                                 "others you meet (pass by: you go on without a word)"},
    "watch": {"args": '{"person"}', "cost": ["watch", "units"], "doc": "spend the day working beside them: you see how they do things"},
    "teach": {"args": '{"to", "what"}', "cost": ["teach", "units_teacher"], "doc": "one session, if they set aside time to learn the same day"},
    "learn": {"args": '{"from", "what"}', "cost": ["teach", "units_learner"], "doc": "one session, if they set aside time to teach the same day"},
    "attack": {"args": '{"target": person or building, "aim": rob | hurt}', "cost": ["combat", "units"], "doc": "settled tonight"},
    "guard": {"args": '{"at"?: building}', "cost": 1, "doc": "stand guard tonight over a building here and anyone set upon"},
    "fire": {"args": "", "cost": 0, "doc": "light a fire in the open tonight if you sleep out (on the road, or with no bed), from timber in your "
                                            "hands, so grain and flour can be boiled; say it before you set off"},
    "partner": {"args": '{"with": a person here}', "cost": 0, "doc": "become partners with someone here, if they choose it too today"},
    "part": {"args": "", "cost": 0, "doc": "end your partnership"},
    "try": {"args": '{"with": a person of the other sex here, "units": 1 or more}', "cost": "units", "when": "children",
            "doc": "try for a child with them, if they try with you today and you both sleep in one place tonight: the more units, "
                   "the better the chance, less with each one more"},
    "name": {"args": '{"heir"?: a person of your household, "head"?: a person of your household}', "cost": 0,
             "doc": "as head, name who heads the household after you; when a head has died, each grown member names the new head"},
    "order": {"args": '{"what": forage | herd | hay | nothing, "at"?: a place here}', "cost": 0, "when": "children",
              "doc": "as head, set your household's children to a small work each day, until you change it"},
    "meet": {"args": '{"at": a building or a place here, "about"?: what it is for}', "cost": 0, "when": "evening",
             "doc": "call a meeting for the start of tomorrow, before the day's work, for everyone at this place: whoever comes gives a "
                    "unit to it; all who come hear what is said there, and witness what is offered"},
    "come": {"args": '{"to"?: the meeting called for this morning}', "cost": 1, "when": "evening",
             "doc": "go to the meeting called for this morning: before the day's work you talk there with all who come, and may change "
                    "your plan"},
    "write": {"args": '{"at": a building or monument here, "text": a sentence (about 30 words), "line"?: which place (its number, or where it is: "over the door"), to replace a line, "how"?: paint | carve (with a tool; in stone, a mason\'s), "description"?: text in place of "text", to replace its description}',
              "cost": "write", "doc": "write a line on a building or monument (each building has so many places: a small room 2, a "
                                      "medium room 4, a hall 8, a monument 3); whoever goes in, or looks it over, reads it. Painting "
                                      "takes 2 units, carving 4 (6 in stone), changing another's words 1 more; it is seen being done"},
    "erase": {"args": '{"at": a building or monument here, "line": which place}', "cost": "write",
              "doc": "scratch out a line written there: the work it took to write, 1 more if it is another's; it is seen being done"},
    "rest": {"args": "", "cost": 0, "doc": ""},
}
VERBS = tuple(VERB)
FM_KINDS = ("sow", "break", "tend", "manure", "crop", "herd", "milk", "slaughter", "works", "select", "fence", "gate")
FREE = tuple(v for v, d in VERB.items() if d["cost"] == 0)


def verb_here(here, verb) -> bool:
    when = VERB[verb].get("when")
    return not when or (when == "roads" and bool(here.roads())) or (when == "herds" and any(FM.head(h) > 0 for h in here.herds().values())) \
        or (when == "children" and here.children_on()) or (when == "evening" and bool(here.setting("evening")))


def verb_units(p, verb):
    c = VERB[verb]["cost"]
    if c in ("craft", "units", "write"):
        return None
    if isinstance(c, list):
        x = p
        for k in c:
            x = x[k]
        return int(x)
    return int(c)


def cost(here, a) -> int:
    v = str((a or {}).get("do", "")).lower().strip()
    if v not in VERB:
        return 0
    n = verb_units(here.p, v)
    if n is not None:
        return n
    if VERB[v]["cost"] == "units":                                            # as many as one chooses to spend (D2-146)
        return _units(a.get("units"))
    if VERB[v]["cost"] == "write":                                            # a line's own engraving (D2-170)
        return max(1, write_units(here, a, erase=v == "erase"))
    tech = KN.resolve(a.get("what"), a.get("do"))
    if tech is None:
        return 1
    tech, a = _as_modified(tech, v, a)
    n = int(TECHNIQUES[tech]["units"])
    if TECHNIQUES[tech].get("units_by") == "bury":                            # by the ground and the cold (D2-96)
        cid = _thing_site(here, a.get("at"))
        if cid:
            n = here.bury_units(cid, cairn=str(a.get("method", "")).lower() == "cairn")
    elif v == "make":
        n *= max(1, int(_qty(a.get("qty"), 1)))
    return n + MOD.units(a, v, tech)


def _as_modified(tech, verb, a):
    """A modifier written as the technique ("dibble") is the technique it modifies, with the modifier set (D2-94)."""
    d = TECHNIQUES.get(tech, {})
    if d.get("modifies"):
        base = next((x.split(":", 1)[1] for x in d["modifies"] if x.startswith(f"{verb}:")), None)
        if base:
            return base, {**a, d["key"]: d["value"]}
    return tech, a


def _thing_site(here, at):
    """A body here by its person's name or its place's name (for burying)."""
    low = str(at or "").strip().lower()
    for cid, c in here.bodies().items():
        names = {c["of"].lower(), here.spot_name(c).lower(), here.spot_name(c).lower().removeprefix("the ")}
        pid = c.get("parcel")
        if pid in here.parcels():                                             # the ground it lies on, or a building on that ground
            names |= {here.parcels()[pid]["name"].lower()} | {b["name"].lower() for b in here.buildings().values() if b["parcel"] == pid}
        if not low or low in names or c["of"].lower() in low:
            return cid
    return None


def do(here, mind, a) -> str:
    v = str((a or {}).get("do", "")).lower().strip()
    if v in ALIASES:                                                          # leaving, putting down and hiding are giving (D2-111)
        a = ALIASES[v](a)
        v = "give"
    try:
        if v not in VERBS:
            raise Refused(f"unknown verb {v!r}; the verbs are {', '.join(VERBS)}")
        if not verb_here(here, v):
            raise Refused(f"there is no {v} in this world")
        party = _party(here, a.get("for")) if a.get("for") and v in ("gather", "work", "make", "build", "give", "accept", "claim") else None
        drew = _drew_reset(here)
        with here.cause(v, party):
            out = HANDLERS[v](here, mind, a, party)
        return out + _drew_words(here, drew)                                   # what it took from the stores (D4-96)
    except Refused as e:
        return f"Refused: {v or 'action'}: {e}"


# ---------------------------------------------------------------------- helpers
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


def item_of(x) -> str:
    i = str(x or "").strip().lower()
    i = {"loaves": "bread", "loaf": "bread", "greens": "wild food", "food": "wild food", "weapon": "crude weapon", "tool": "crude tool",
         "tools": "crude tool", "wood": "timber", "ore": "copper ore", "hides": "hide", "stones": "stone"}.get(i, i)
    if i not in ITEMS:
        raise Refused(f"there is no such thing as {x!r} (goods: {', '.join(ITEMS)})")
    return i


def _party(here, x):
    """Whom an act is done for (D2-37): a person here, or a household (its own name, or 'my household')."""
    s = str(x or "").strip()
    low = s.lower()
    if low in ("my household", "our household", "household", "home", "my house", "the house"):
        hh = here.household()
        if not hh:
            raise Refused("you belong to no household")
        return hh
    who = here.person(s)
    if who:
        return who
    for iid, h in here.households().items():
        if low in (iid.lower(), iid.lower() + "s", h["name"].lower(), h["name"].lower().removeprefix("the ")):
            return iid
    raise Refused(f"there is no one called {s!r} to act for")


def _out(here, party) -> str:
    """Where an act's output goes: one's hands, or the party's container here, if one may use it (D2-37)."""
    if party is None or party == here.name:
        return here.hands
    cid = here.party_container(party)
    if cid is None:
        if party == here.household():                                       # away from home: one carries it back oneself
            return here.hands
        raise Refused(f"work done for {party} goes into their store, and they have no house or store here, and nobody of theirs "
                      f"is here to take it: do it for yourself and carry it to them, or work where they live")      # D4-95
    return cid                                                              # putting into another's store is a gift (D4-23)


def _full_note(here, out, item, q) -> str:
    """Into a store that cannot hold it all: what went in, and that the rest lies outside its door (D2-155)."""
    if not out.startswith("stock:"):
        return ""
    bid = out[len("stock:"):]
    b = here.buildings()[bid]
    room = BL.room_for(b, here.stock(bid), item)
    if room + 1e-9 >= q:
        return ""
    return f" ({show(room)} {item} went into {b['name']}; it is full ({BL.full_words(b, here.stock(bid), item)}), and the rest lies outside its door)"


def _src(here, party, out):
    """A party's store as a source of inputs: only if one may take from it, or works for the party (D2-37, D2-38)."""
    if out == here.hands or not out.startswith("stock:"):
        return None
    return out if (here.may_take(out) or here.works_for(party)) else None


def _level(mind, tech) -> str:
    lvl = KN.level(mind, tech)
    if lvl is None:
        raise Refused(f"{KN.label(tech)} is not among your crafts: you have never learned it")
    if lvl == "aware":
        raise Refused(f"you know of {KN.label(tech)}, but have no idea how it is done (watch someone, ask to be taught, or have it explained)")
    return lvl


def _consume(here, needs: dict, mult=1.0, extra=None):
    """Take inputs from what one carries, then from stores here one may take from (or a party's, acting for it)."""
    order = [here.hands] + ([extra] if extra and extra != here.hands else []) + [c for c in here.takeable() if c not in (here.hands, extra)]
    needs = KN.pick_inputs(here, needs, mult, extra)
    for item, q in needs.items():                                            # all or nothing: check before taking any
        have = KN.available(here, item, extra=extra)
        if have + 1e-9 < q * mult:
            raise Refused(f"it needs {q * mult:g} {item}; you have {show(have)} to hand" + _short_note(here, item))
    for item, q in needs.items():
        left = round(q * mult, 6)
        for cid in order:
            if left <= 1e-9:
                break
            have = here.contents(cid).get(item, 0.0)                         # hands, a store, or what lies at its door (D4-89)
            take = min(have, left)
            if take > 1e-9:
                here.apply("destroy", src=cid, item=item, qty=take, why="used")
                if cid != here.hands:
                    _drawn(here, cid, item, take)
                left -= take
        if left > 1e-6:
            raise Refused(f"it needs {q * mult:g} {item}")


def _drawn(here, cid, item, q) -> None:
    """Who drew what from a store today, so the next one who finds it gone is told by whom (D4-95)."""
    try:
        today = here.today()
    except KeyError:                                                           # outside a day (a test, a tool): nothing to tell later
        return
    today.setdefault("drawn", []).append({"by": here.name, "cid": cid, "item": item, "qty": round(q, 2)})


def _store_name(here, cid) -> str:
    if cid.startswith("stock:"):
        return f"{here.buildings()[cid[len('stock:'):]]['name']}'s store"
    c = here.thing(cid) or {}
    door = here.buildings().get(c.get("door") or "", {}).get("name")
    return f"what lies at the door of {door}" if door else "what lies here"


def _drew_reset(here) -> int:
    """The mark in today's draws where this act starts."""
    try:
        return len(here.today().get("drawn") or [])
    except KeyError:
        return -1


def _drew_words(here, start) -> str:
    """' (from the Hearne hut's store: 10 flour, 1 timber)': what an act took from the stores rather than one's hands (D4-96)."""
    if start < 0:
        return ""
    got = {}
    for d in (here.today().get("drawn") or [])[start:]:
        if d["by"] == here.name and not d.get("taken"):
            got.setdefault(d["cid"], {}).setdefault(d["item"], 0.0)
            got[d["cid"]][d["item"]] += d["qty"]
    if not got:
        return ""
    return " (from " + "; ".join(f"{_store_name(here, c)}: " + ", ".join(f"{show(q)} {i}" for i, q in g.items()) for c, g in got.items()) + ")"


def _top_up(here, item, q) -> None:
    """Before giving from one's hands: take what is short from the stores here one may take from, as a craft does (D4-96)."""
    short = q - here.carried().get(item, 0.0)
    for cid in [c for c in here.takeable() if c != here.hands]:
        if short <= 1e-9:
            break
        take = min(short, here.contents(cid).get(item, 0.0))
        if take > 1e-9:
            here.apply("transfer", src=cid, dst=here.hands, item=item, qty=round(take, 6))
            _drawn(here, cid, item, take)
            short -= take


def _short_note(here, item) -> str:
    """Why a good is short: who else drew it from the stores one shares today, and where it comes from (D4-95)."""
    mine = set(here.takeable())
    took = {}
    try:
        drawn = here.today().get("drawn") or []
    except KeyError:
        drawn = []
    for d in drawn:
        if d["item"] == item and d["cid"] in mine and d["by"] != here.name:
            took[d["by"]] = took.get(d["by"], 0.0) + d["qty"]
    out = ""
    if took:
        out += "; " + ", ".join(f"{who} took {show(q)} from the store today" for who, q in took.items())
    src = next((t for t, d in TECHNIQUES.items() if isinstance(d.get("gives"), dict) and item in d["gives"] and d.get("inputs")), None)
    if src:                                                                    # where it comes from: the recipe that makes it
        out += f"; {item} is made by {KN.label(src)}"
    return out


def _skill_mult(here, mind, tech) -> float:
    return KN.skill(mind, tech) * here.yield_mult()                           # skill by practice (D2-52), and hunger


def _site(here, mind, tech, at, a=None):
    sites = KN.where(here, tech)
    if sites and sites[0][0] == "thing":
        cid = _thing_site(here, at)
        if cid is None:
            raise Refused(f"there is no body to bury here called {at!r}" if at else "there is no body here to bury")
        return "thing", cid, next(s[2] for s in sites if s[1] == cid)
    if not sites and (TECHNIQUES[tech].get("at") or {}).get("things"):
        raise Refused("there is no one lying unburied here")
    if at:
        key = here.parcel(at) or here.building(at)
        if key is None:
            raise Refused(f"there is no place called {at!r} here")
        where = [s for s in sites if s[0] == "parcel"]
        sites = [s for s in sites if s[1] == key]
        if not sites:                                                          # where here it is done, by the land (D4-95)
            names = list(dict.fromkeys(here.parcels()[s[1]]["name"] for s in where if s[1] in here.parcels()))
            raise Refused(f"{KN.label(tech)} is not done at {at}" + (f"; here it is done at {', '.join(names)}" if names else
                                                                   "; there is nowhere here for it"))
    ok = [s for s in sites if not KN.ready(here, tech, s[0], s[1], a)]
    if not ok:
        why = KN.ready(here, tech, sites[0][0], sites[0][1], a) if sites else f"there is nowhere here for {KN.label(tech)}"
        what = PC.LAND_DRAWS.get(TECHNIQUES[tech].get("draws"))
        if sites and what and sites[0][0] == "parcel" and ("picked bare" in why or "no standing timber" in why):
            PC.remember_land(mind, here.day, sites[0][1], what, "bare", "found")         # found out by trying (D4-50)
        if at and sites and sites[0][0] == "parcel":                           # one went and tried: one sees the place (D4-95)
            try:
                w_ = here.today()["worked"].setdefault(here.name, [])
                if sites[0][1] not in w_:
                    w_.append(sites[0][1])
            except KeyError:
                pass
        raise Refused(why)
    return ok[0]


def _against(here, thing) -> str:
    """Using a thing others hold or claim is allowed and seen (D4-23): the words for it."""
    mine = {here.name, here.household(), "anyone"}
    hh = here.households()
    others = sorted({hh[c["claimant"]]["name"] if c["claimant"] in hh else c["claimant"] for c in here.claims(thing)
                     if "withdrawal" in c["rights"] and c["claimant"] not in mine and c["grounds"] != "granted"})
    if not others:
        return ""
    has = "withdrawal" in here.rights(thing)
    return f" (which {' and '.join(others)} {'also claim' if has else 'hold' + ('s' if len(others) == 1 else '')})"


def _holding_people(here, holder) -> list:
    """Those a holding is whose: the holder, or its household's members (D2-172)."""
    return list(here.institution(holder)["members"]) if holder in here.households() else [holder]


def _holders_people(here, thing) -> list:
    out = []
    for c in here.claims(thing):
        if c["claimant"] in here.households():
            out += [m for m in here.institution(c["claimant"])["members"]]
        elif c["claimant"] != "anyone":
            out.append(c["claimant"])
    return out


# ---------------------------------------------------------------------- gathering and work: one handler, from the data
def _gather(here, mind, a, party):
    return _technique(here, mind, a, party, "gather")


def _work(here, mind, a, party):
    if KN.resolve(a.get("what"), "work") == "care":
        return _care(here, mind, a)
    return _technique(here, mind, a, party, "work")


def _technique(here, mind, a, party, verb):
    tech = KN.resolve(a.get("what"), verb)
    if tech is None or TECHNIQUES[tech]["verb"] != verb:
        names = [t for t, d in TECHNIQUES.items() if d["verb"] == verb]
        raise Refused(f"{a.get('what')!r} is not something you {verb} ({verb}: {', '.join(names)})")
    tech, a = _as_modified(tech, verb, a)
    t = TECHNIQUES[tech]
    if not t.get("crew"):                                                     # crew work: anyone may dig, led by one who knows how
        _level(mind, tech)
    a = {**a, "_mods": MOD.resolve(here, mind, verb, a, tech=tech)}           # ways of doing it (D2-93)
    kind, key, place_name = _site(here, mind, tech, a.get("at"), a)
    why = KN.shortfall(here, mind, tech, 1.0, key, a=a)
    if why:
        if kind == "parcel":                                                   # one went and tried: one sees the place (D4-95)
            w_ = here.today()["worked"].setdefault(here.name, [])
            if key not in w_:
                w_.append(key)
        raise Refused(why)
    out = _out(here, party)
    y = t["yield"]
    m = _skill_mult(here, mind, tech)
    tool, tm = here.best_tool(t["tools"]) if t.get("tools") else (None, 1.0)
    rng = here.rng("act", here.day, here.name, len(here.today()["worked"].get(here.name, [])))
    here.today()["worked"].setdefault(here.name, []).append(key)
    thing = (kind, key)
    note = _against(here, thing) if kind == "parcel" and t.get("draws") != "dead" else ""   # dead wood is anyone's (D2-158)
    got, gives, word, extra_got, suffix = 0.0, t.get("gives"), "", "", ""
    holding = None
    if y["kind"] == "stock":
        r = here.parcels()[key]["res"][t["draws"]]
        want = y["base"] * r["S"] / r["K"] * m * tm
        got = here.apply("draw", parcel=key, key=t["draws"], qty=round(max(0.0, min(want, r["S"] - here.p["refuge"] * r["K"])), 2))
    elif y["kind"] == "chance":
        r = here.parcels()[key]["res"][t["draws"]]
        armed = here.weapon()
        if rng.random() < y["p"] * r["S"] / r["K"]:
            q = rng.uniform(*y["range"]) * m * (t["weapon"]["armed"] if armed else t["weapon"]["none"])
            got = here.apply("draw", parcel=key, key=t["draws"], qty=round(min(r["S"], q), 2))
            for by, pr in (y.get("by") or {}).items():
                if rng.random() < pr:
                    here.apply("create", dst=out, item=by, qty=1, why=tech)
                    extra_got = f" and a {by}"
            if got > 0:                                                         # the day's kills on this ground, for its signs (D4-74)
                rec = here.parcels()[key].get("hunted") or {}
                kills = list(rec.get("kills") or []) if rec.get("day") == here.day else []
                kills.append({"by": here.name, "meat": got, "hide": bool(extra_got)})
                here.apply("set", ref=("parcel", key), field="hunted", value={"day": here.day, "kills": kills})
        if armed and t.get("wear"):
            here.apply("wear", container=here.hands, item=armed, uses=t["wear"])
    elif y["kind"] == "fixed":
        q = y["base"] * m * tm
        got = here.apply("draw", parcel=key, key=t["draws"], qty=round(q, 2)) if t["draws"] in here.parcels()[key]["res"] and \
            here.parcels()[key]["res"][t["draws"]]["K"] > 0 and t["draws"] != "quarry" else round(q, 2)
        if tech == "fell" and got > 0:                                         # its branches left as dead wood (D2-156)
            here.apply("add_res", parcel=key, key="dead", qty=got)
    elif y["kind"] == "clear":                                                # new ground for a field (CLEARING)
        word = _clear(here, key, place_name, m * tm, party)
    elif y["kind"] == "pool":                                                 # dead wood: less to find as it thins (D2-156)
        r = here.parcels()[key]["res"][t["draws"]]
        q = y["base"] * m * min(1.0, r["S"] / max(r["K"], 1e-9)) ** 0.5
        got = here.apply("draw", parcel=key, key=t["draws"], qty=round(min(q, r["S"]), 2))
    elif y["kind"] in FM_KINDS:                                                 # farming and cattle (farm.py)
        got, g, word, thing = FM.act(here, mind, tech, key, place_name, out, m, tm, a)
        gives = g or gives
        note = _against(here, thing) if thing[0] in ("parcel", "herd") else note
        if "_on" in a and FM.named(here.parcels()[key]):                       # a field held in shares: whose plots (D2-172)
            note = FM.against(here, key, a["_on"])
            holding = a["_on"]
        if word and not word.startswith("You"):
            suffix, word = word, ""                                             # a note to the plain result, below
    elif y["kind"] == "bury":                                                 # D2-96
        c = here.thing(key)
        cairn = "method: cairn" in a["_mods"]["_used"]
        if cairn:
            _consume(here, a["_mods"].get("inputs") or {})
        here.apply("set_thing", cid=key, field="buried", value=here.day)
        here.apply("set_thing", cid=key, field="cairn", value=cairn)
        word = f"You buried {c['of']} at {here.spot_name(c)}" + (" under a cairn of stones." if cairn else ".")
        thing = ("parcel", c["parcel"]) if c.get("parcel") else thing
    elif y["kind"] == "repair":                                              # by its size and structure (D2-168)
        if here.buildings()[key]["structure"] == "stone":
            _mason(mind)                                                       # mending stone is walling (D4-97)
        word = _repair(here, key, m)
        thing = ("building", key)
    elif y["kind"] == "clear_built":                                          # new ground for building (02zh §8)
        word = _clear_built(here, key, place_name, m * tm, party)
    what = PC.LAND_DRAWS.get(t.get("draws")) if kind == "parcel" and y["kind"] in ("stock", "chance") else None
    if what:                                                                    # what working it showed of the place (D4-50)
        if y["kind"] == "chance":
            PC.remember_land(mind, here.day, key, what, "good" if got > 0 else "nothing caught", "found")
        else:
            PC.remember_land(mind, here.day, key, what, "thin" if got < 0.5 * y["base"] else "good", "found")
    if got > 0 and gives:
        suffix = _full_note(here, out, gives, got) + suffix
        here.apply("create", dst=out, item=gives, qty=got, why=tech)
    if tool and t.get("wear"):
        here.apply("wear", container=here.hands, item=tool, uses=t["wear"])
    KN.tried(here, mind, tech, got > 0 or y["kind"] in ("sow", "tend", "repair", "slaughter", "break", "manure", "herd", "bury", "fence", "gate"),
             units=t["units"])
    MOD.practise(here, mind, a["_mods"])
    for_txt = f" for {here.households()[party]['name'] if party in here.households() else party}" if party and party != here.name else ""
    text = f"{here.name} was {KN.label(tech)} at {place_name}{for_txt}{note}"
    here.event("work", text, actor=here.name, about=[f"{thing[0]}:{thing[1]}"], salience=0.35 if note else 0.15, tags=t["tags"],
               tech=tech, concerns=(_holding_people(here, holding) if holding is not None else _holders_people(here, thing)) if note else [],
               **({"holding": holding} if holding is not None else {}))
    here.record(verb, tech, party, site=key)
    if word:
        if y["kind"] == "slaughter":                                          # where the meat and hide went (D4-70)
            word = word.rstrip(".") + (" (now in your hands)." if out == here.hands else
                                       f" (put into {here.buildings()[out[len('stock:'):]]['name']})." if out.startswith("stock:") else ".")
        return word if not for_txt else word.rstrip(".") + for_txt + "."
    if y["kind"] == "chance" and got <= 0:
        return f"You hunted in {place_name}{note} and caught nothing{extra_got}."
    via = f" with your {tool}" if tool else (" with your bare hands" if t.get("tools") else "")
    dest = "" if out == here.hands else f" into {here.buildings()[out[len('stock:'):]]['name']}" if out.startswith("stock:") else f" to {party}"
    return (f"You {verb}ed {show(got)} {gives}{extra_got} at {place_name}{note}{via}{dest}.{suffix}".replace("You gathered", "You took")
            .replace("You worked", "You got"))


# ---------------------------------------------------------------------- making
def _make(here, mind, a, party):
    tech = KN.resolve(a.get("what"), "make")
    if tech is None or TECHNIQUES[tech]["verb"] != "make":
        names = [t for t, d in TECHNIQUES.items() if d["verb"] == "make"]
        raise Refused(f"{a.get('what')!r} is not something you make (recipes: {', '.join(names)})")
    lvl = _level(mind, tech)
    t = TECHNIQUES[tech]
    out = _out(here, party)
    extra = _src(here, party, out)
    qty = max(1, int(_qty(a.get("qty"), 1)))
    res = []
    for i in range(qty):
        why = KN.shortfall(here, mind, tech, TRY[lvl]["inputs"], extra=extra)
        if why:
            res.append(f"Refused: make {tech}: {why}")
            break
        sites = KN.where(here, tech)                                           # one's own house's fitting first
        site = sorted(sites, key=lambda x: (x[0] != "building" or x[1] not in here.homes_here(),
                                            x[0] != "building" or not here.may_take(here.buildings()[x[1]]["stock"])))[0]
        _consume(here, t.get("inputs") or {}, TRY[lvl]["inputs"], extra)
        ok = here.rng("make", here.day, here.name, tech, i).random() < TRY[lvl]["chance"]
        rose = KN.tried(here, mind, tech, ok, units=t["units"])
        if ok:
            full = ""
            for item, q in t["gives"].items():
                full += _full_note(here, out, item, q)
                here.apply("create", dst=out, item=item, qty=q, why=tech)
            res.append(f"You made {', '.join(f'{q:g} {it}' for it, q in t['gives'].items())}" + (f" at {site[2]}" if site[1] else "") + full + "."
                       + (f" (You are now {rose} at it.)" if rose else ""))
        else:
            res.append(f"Your try at {KN.label(tech)} failed and the materials are spoilt." + (f" (You are now {rose} at it.)" if rose else ""))
        here.event("make", f"{here.name} was {KN.label(tech)}" + ("" if ok else ", and it went wrong"), actor=here.name,
                   about=[f"{site[0]}:{site[1]}"] if site[0] in ("building", "parcel") else [], salience=0.2, tags=t["tags"], tech=tech)
        here.record("make", tech, party)
    return " ".join(res)


# ---------------------------------------------------------------------- building (D2-9, recipes.md §3; review 02zh, D2-154 to D2-171)
STRUCTURE_WORDS = {"wattle": "wattle", "wattle and daub": "wattle", "timber": "timber", "wood": "timber", "wooden": "timber",
                   "stone": "stone", "masonry": "stone"}
MONUMENT_ALIAS = {x: k for k, d in MONUMENTS.items() for x in [k] + d.get("aliases", [])}
UPGRADE = ("upgrade", "rebuild", "raise", "improve")


def _mason(mind):
    """Building in stone is stone walling (D2-3, D4-97): stone rooms, storeys and upgrades, mending stone, carving in stone, and a
    mason's fitting one has not learned itself; the level is one's walling."""
    lv = KN.level(mind, "wall")
    if lv not in ("rough", "capable", "known"):
        raise Refused("building in stone is stone walling, a mason's craft you have not learned (watch a mason, be taught, or have it "
                      "explained)")
    return lv


def _lvl_for(mind, tech, structure=None):
    """The level one works at: in stone, as a mason; a mason's fitting or monument by that craft, or else as a mason; otherwise
    the technique itself (a carpenter's for a timber medium room or hall)."""
    if structure == "stone":
        return _mason(mind)
    if TECHNIQUES.get(tech, {}).get("trade") == "mason":
        lv = KN.level(mind, tech)
        return lv if lv in ("rough", "capable", "known") else _mason(mind)
    return _level(mind, tech)


def _how(here, mind, a):
    if str(a.get("how") or "").strip().lower() in ("plain", "none", ""):
        a = {k: v for k, v in a.items() if k != "how"}
    mods = MOD.resolve(here, mind, "build", a)
    return mods.get("tier") or "plain", mods


def _ground_check(here, pid, need, what):
    par = here.parcels()[pid]
    total = BL.ground_total(par)
    if total <= 0:
        raise Refused(f"{par['name']} is {par['cover']}, not ground for building: build on built ground or scrub, or clear it first "
                      "(work clear for building)")
    free = BL.ground_free(pid, par, here.buildings())
    if free < need:
        raise Refused(f"there is no room left to build on {par['name']}: {total - free} of its {total} spaces are taken, and {what} "
                      f"needs {need} (build up in stone, build elsewhere, or clear more ground)")


def _build(here, mind, a, party):
    what = str(a.get("what") or "").strip().lower()
    what = MONUMENT_ALIAS.get(what, what)
    if what in UPGRADE:
        return _upgrade(here, mind, a, party)
    if what in ("storey", "upper storey", "second storey", "third storey"):
        what = str(a.get("room") or "small room").strip().lower()
        a = {**a, "storey": a.get("storey") or (3 if "third" in str(a.get("what")) else 2)}
    if what not in BLUEPRINTS and what not in FITTINGS and what not in MONUMENTS:
        raise Refused(f"{a.get('what')!r} is not something you build (rooms: {', '.join(r for r in BLUEPRINTS)}; fittings: "
                      f"{', '.join(FITTINGS)}; monuments: {', '.join(MONUMENTS)}; or upgrade a building)")
    owner = party or here.name
    at = a.get("at")
    if what in BLUEPRINTS or what in MONUMENTS:
        bid = here.building(at) if at else None
        if bid and here.buildings()[bid].get("unfinished"):                      # carry on
            u = here.buildings()[bid]["unfinished"]
            return _build_work(here, mind, bid, _lvl_for(mind, u["blueprint"], here.buildings()[bid]["structure"]))
        if bid and what in BLUEPRINTS and what != "camp":
            return _add_room(here, mind, a, party, bid, what)
        if bid:
            raise Refused(f"{at} is a building: say a place on built ground or scrub here to put up a new one")
        pid = here.parcel(at) if at else None
        if pid is None:
            lots = [p for p, x in here.parcels().items() if BL.ground_total(x) > 0]
            raise Refused(f"say where to build: a place on built ground or scrub here ({', '.join(here.parcels()[p]['name'] for p in lots) or 'none'})"
                          " or, to add a room, a building here")
        if what in MONUMENTS:
            return _monument(here, mind, a, party, pid, what)
        return _new_building(here, mind, a, party, pid, what, owner)
    return _fitting(here, mind, a, party, what)


def _new_building(here, mind, a, party, pid, what, owner):
    bp = BLUEPRINTS[what]
    par = here.parcels()[pid]
    who = here.households()[party]['name'] if party in here.households() else here.name
    if bp.get("structure") == "camp":                                        # a camp goes up anywhere but on water (D2-68)
        lvl = _level(mind, what)
        if par["cover"] == "water":
            raise Refused("you cannot camp on water")
        if BL.ground_total(par) > 0 and BL.ground_free(pid, par, here.buildings()) < int(SPACE["camp_floor"]):
            raise Refused(f"there is no room left to camp on {par['name']}")
        _consume(here, bp["materials"], TRY[lvl]["inputs"], here.party_container(party) if party else None)
        name = str(a.get("name") or "").strip()[:40] or f"{who}'s camp on {par['name']}"
        bid = here.apply("raise", node=here.node, parcel=pid, rec={"name": name, "structure": "camp", "fittings": {},
                                                                     "unfinished": {"blueprint": what, "units_left": bp["units"]}})
        here.apply("claim", thing=("building", bid), claimant=owner, rights="all", grounds="built")
        here.event("build", f"{here.name} began building {bp['label']} on {par['name']}", actor=here.name, about=[f"building:{bid}"],
                   salience=0.5, tags=["building"])
        return _build_work(here, mind, bid, lvl, started=True)
    structure = STRUCTURE_WORDS.get(str(a.get("structure") or bp["structure"]).strip().lower())
    if structure is None:
        raise Refused(f"a building is wattle, timber or stone, not {a.get('structure')!r}")
    if structure not in ROOMS[what]:
        raise Refused(f"a {what} is too large for wattle: build it in timber (on a stone footing) or in stone")
    how, mods = _how(here, mind, a)
    lvl = _lvl_for(mind, what, structure)
    floor = int(ROOMS[what]["floor"])
    _ground_check(here, pid, floor, f"a {what}")
    cost = BL.room_cost(what, structure, how=how)
    _consume(here, cost["materials"], TRY[lvl]["inputs"], here.party_container(party) if party else None)
    name = str(a.get("name") or "").strip()[:40] or f"{who}'s new house"
    rec = {"name": name, "structure": structure, "fittings": {}, "tier": how, "rooms": [{"kind": what, "floor": floor, "storey": 1}],
           "unfinished": {"blueprint": what, "units_left": cost["units"]}}
    bid = here.apply("raise", node=here.node, parcel=pid, rec=rec)
    if a.get("describe"):                                                     # the description, written with the build (D2-169)
        here.apply("set", ref=("building", bid), field="description",
                   value={"text": BL.cap_text(a["describe"], "description"), "by": here.name, "day": here.day})
    here.apply("claim", thing=("building", bid), claimant=owner, rights="all", grounds="built")
    tw = TIERS[how]["words"]
    here.event("build", f"{here.name} began building a {what} in {structure}" + (f", {tw}" if tw and how != "grand" else
                                                                                      (", on a grand scale" if how == "grand" else ""))
               + f", on {par['name']}", actor=here.name, about=[f"building:{bid}"], salience=0.5, tags=["building"])
    MOD.practise(here, mind, mods)
    return _build_work(here, mind, bid, lvl, started=True)


def _monument(here, mind, a, party, pid, what):
    d = MONUMENTS[what]
    par = here.parcels()[pid]
    if par["cover"] == "water":
        raise Refused("a monument cannot stand in water")
    how, mods = _how(here, mind, a)
    lvl = _lvl_for(mind, what)
    if BL.ground_total(par) > 0:
        _ground_check(here, pid, int(SPACE["monument_ground"]), d["label"])
    t = TIERS[how]
    _consume(here, {i: q * float(t["materials"]) for i, q in d["materials"].items()}, TRY[lvl]["inputs"],
             here.party_container(party) if party else None)
    name = str(a.get("name") or "").strip()[:40] or f"the {what} on {par['name']}"
    bid = here.apply("raise", node=here.node, parcel=pid, rec={"name": name, "structure": d["structure"], "fittings": {}, "rooms": [],
                                                                 "monument": what, "tier": how,
                                                                 "unfinished": {"blueprint": what, "units_left": float(d["units"]) * float(t["work"])}})
    if a.get("describe"):
        here.apply("set", ref=("building", bid), field="description",
                   value={"text": BL.cap_text(a["describe"], "description"), "by": here.name, "day": here.day})
    here.apply("claim", thing=("building", bid), claimant=party or here.name, rights="all", grounds="built")
    here.event("build", f"{here.name} began raising {d['label']} on {par['name']}", actor=here.name, about=[f"building:{bid}"],
               salience=0.5, tags=["building"])
    MOD.practise(here, mind, mods)
    return _build_work(here, mind, bid, lvl, started=True)


def _usable(here, bid):
    b = here.buildings()[bid]
    if b.get("unfinished"):
        raise Refused(f"{b['name']} is not finished")
    if not here.can_enter(bid):
        raise Refused(f"you cannot get into {b['name']}")
    return b


def _add_room(here, mind, a, party, bid, what):
    """A room added to a building: a quarter less (D2-154); on an upper storey in stone only, at 1.5 and 2 times (D2-3)."""
    b = _usable(here, bid)
    if b.get("monument"):
        raise Refused(f"{b['name']} is a monument: it has no rooms")
    if b["structure"] == "camp":
        raise Refused(f"{b['name']} is a camp: build a house to add rooms to")
    storey = max(1, int(_qty(a.get("storey"), 1)))
    wk = b.get("works")
    if wk:
        if wk.get("kind") == "room" and wk.get("room") == what and int(wk.get("storey", 1)) == storey:
            return _works_progress(here, mind, bid)
        raise Refused(f"{_works_words(wk)} is under way at {b['name']}: finish it first")
    if what not in ROOMS or b["structure"] not in ROOMS[what]:
        raise Refused(f"a {what} is too large for a wattle building: upgrade {b['name']} to timber or stone first")
    floor = int(ROOMS[what]["floor"])
    if storey > 1:
        if b["structure"] != "stone":
            raise Refused(f"only a stone building takes an upper storey (D2-3): {b['name']} is {b['structure']}; upgrade it to stone first")
        if storey > max(SPACE["storeys"]):
            raise Refused(f"a building stands at most {max(SPACE['storeys'])} storeys")
        below = BL.floor(b, storey - 1)
        if BL.floor(b, storey) + floor > below:
            raise Refused(f"storey {storey} of {b['name']} can hold no more floor than the one below it ({below} spaces; "
                          f"{BL.floor(b, storey)} built)")
    else:
        _ground_check(here, b["parcel"], floor, f"a {what}")
    how = BL.tier(b)
    lvl = _lvl_for(mind, what, b["structure"])
    cost = BL.room_cost(what, b["structure"], added=True, storey=storey, how=how)
    _consume(here, cost["materials"], TRY[lvl]["inputs"], b["stock"] if here.may_take(b["stock"]) else
             (here.party_container(party) if party else None))
    here.apply("set", ref=("building", bid), field="works", value={"kind": "room", "room": what, "floor": floor, "storey": storey,
                                                                     "units_left": cost["units"], "tech": what, "by": here.name})
    here.record("build", what, party)
    return _works_progress(here, mind, bid, started=True)


def _upgrade(here, mind, a, party):
    """A building's structure raised (wattle to timber, timber to stone), or its tier raised by the difference (02zh §2, D2-171)."""
    at = a.get("at")
    bid = here.building(at) if at else (here.homes_here() or [None])[0]
    if bid is None:
        raise Refused("say which building here to upgrade (\"at\")")
    b = _usable(here, bid)
    if b["structure"] == "camp":
        raise Refused(f"{b['name']} is a camp: it cannot be rebuilt")
    wk = b.get("works")
    to = STRUCTURE_WORDS.get(str(a.get("to") or a.get("structure") or "").strip().lower())
    how = str(a.get("how") or "").strip().lower() or None
    if wk:
        if wk.get("kind") in ("upgrade", "tier"):
            return _works_progress(here, mind, bid)
        raise Refused(f"{_works_words(wk)} is under way at {b['name']}: finish it first")
    if to and how:
        raise Refused("one thing at a time: a new structure (\"to\") or a finer tier (\"how\")")
    if how:
        mods = MOD.resolve(here, mind, "build", a)
        how = mods.get("tier") or how
        if how not in TIERS or not BL.tier_up(how, BL.tier(b)):
            raise Refused(f"{b['name']} is already {BL.tier(b)}; it can be raised to " +
                          (", ".join(t for t in TIERS if BL.tier_up(t, BL.tier(b))) or "nothing finer"))
        cost = BL.tier_cost(b, how)
        tech = b.get("monument") or (b["rooms"][0]["kind"] if b.get("rooms") else "small room")
        lvl = _lvl_for(mind, tech, b["structure"] if b["structure"] == "stone" else None)
        _consume(here, cost["materials"], TRY[lvl]["inputs"], b["stock"] if here.may_take(b["stock"]) else None)
        here.apply("set", ref=("building", bid), field="works", value={"kind": "tier", "to": how, "units_left": cost["units"],
                                                                         "tech": tech, "by": here.name})
        here.record("build", "upgrade", party)
        return _works_progress(here, mind, bid, started=True)
    if b.get("monument"):
        raise Refused(f"{b['name']} is a monument: raise its tier (\"how\") instead")
    order = SPACE["order"]
    if to is None:
        nxt = order[order.index(b["structure"]) + 1] if b["structure"] in order[:-1] else None
        raise Refused(f"say what to upgrade {b['name']} to: \"to\": " + (nxt or "nothing: it is stone already")
                      + "; or \"how\": fine, rich or grand")
    if order.index(to) <= order.index(b["structure"]):
        raise Refused(f"{b['name']} is {b['structure']} already")
    cost = BL.upgrade_cost(b, to)
    big = next((r["kind"] for r in b["rooms"] if r["kind"] in ("hall", "medium room")), "small room")
    lvl = _mason(mind) if to == "stone" else _level(mind, big)
    _consume(here, cost["materials"], TRY[lvl]["inputs"], b["stock"] if here.may_take(b["stock"]) else None)
    here.apply("set", ref=("building", bid), field="works", value={"kind": "upgrade", "to": to, "units_left": cost["units"],
                                                                     "tech": big, "by": here.name})
    here.record("build", "upgrade", party)
    return _works_progress(here, mind, bid, started=True)


def _works_words(wk) -> str:
    if wk["kind"] == "room":
        return f"a {wk['room']}" + (f" on storey {wk['storey']}" if int(wk.get("storey", 1)) > 1 else "")
    if wk["kind"] == "upgrade":
        return f"rebuilding in {wk['to']}"
    return f"work to make it {TIERS[wk['to']]['words']}"


def _at_work(here, bid):
    """Building work, writing: a day's work at the building (its parcel: presence, glimpses, the day's route)."""
    here.today()["worked"].setdefault(here.name, []).append(bid)


def _works_progress(here, mind, bid, started=False):
    """Work on a room, a rebuilding or a finer finish, two units an action (more with skill), until done; it counts when done."""
    _at_work(here, bid)
    b = here.buildings()[bid]
    wk = dict(b["works"])
    done = round(2 * KN.skill(mind, wk.get("tech") or "small room") * here.yield_mult(), 2)
    wk["units_left"] = round(max(0.0, float(wk["units_left"]) - done), 2)
    words = _works_words(wk)
    if wk["units_left"] > 1e-9:
        here.apply("set", ref=("building", bid), field="works", value=wk)
        here.event("build", f"{here.name} was working on {words} at {b['name']}", actor=here.name, about=[f"building:{bid}"],
                   salience=0.25, tags=["building"])
        return ("You began " if started else "You worked on ") + f"{words} at {b['name']}: about {show(wk['units_left'])} units of work left."
    here.apply("set", ref=("building", bid), field="works", value=None)
    if wk["kind"] == "room":
        rooms = BL.rooms(b) + [{"kind": wk["room"], "floor": int(wk["floor"]), "storey": int(wk.get("storey", 1))}]
        here.apply("set", ref=("building", bid), field="rooms", value=rooms)
        here.apply("set", ref=("building", bid), field="size", value=sum(int(r["floor"]) for r in rooms))
        out = f"You finished {words} at {b['name']}: it has {BL.floor(here.buildings()[bid])} spaces of floor now."
    elif wk["kind"] == "upgrade":
        here.apply("set", ref=("building", bid), field="structure", value=wk["to"])
        out = f"You finished rebuilding {b['name']} in {wk['to']}: its rooms, fittings, stores and writing are as they were."
    else:
        here.apply("set", ref=("building", bid), field="tier", value=wk["to"])
        out = f"You finished the work on {b['name']}: it is {TIERS[wk['to']]['words']} now."
    KN.tried(here, mind, wk.get("tech") or "small room", True)
    here.event("build", f"{here.name} finished {words} at {b['name']}", actor=here.name, about=[f"building:{bid}"], salience=0.5,
               tags=["building"])
    return out


def _fitting(here, mind, a, party, what):
    f = FITTINGS[what]
    at = a.get("at")
    bid = here.building(at) if at else (here.homes_here() or [None])[0]
    if bid is None:
        inside = ", ".join(x["name"] for x in here.buildings().values() if not x.get("unfinished"))
        raise Refused(f"{f['label']} is fitted inside a building, not built on open ground: say which building in \"at\""
                      + (f" ({inside})" if inside else " (there is none here yet: build a small room first)"))
    b = _usable(here, bid)
    if b.get("monument"):
        raise Refused(f"{b['name']} is a monument: nothing is fitted in it")
    lvl = _lvl_for(mind, what)
    if f.get("needs") and not b["fittings"].get(f["needs"]):
        raise Refused(f"{f['label']} needs {FITTINGS[f['needs']]['label']} first")
    if f.get("structure") and b["structure"] != f["structure"]:                # an oven only in stone, for its fire (D4-97)
        raise Refused(f"{f['label']} is built only in a {f['structure']} building ({b['name']} is {b['structure']}): "
                      f"build it in one, or raise one")
    if f.get("site") and not any(here.parcels()[x]["cover"] == f["site"] for x in [b["parcel"]] + here.parcels()[b["parcel"]]["adj"]
                                 if x in here.parcels()):
        raise Refused(f"{f['label']} needs a building by {f['site']}")
    under = dict(b.get("fitting_work") or {})
    if what in under:                                                          # carry on one under way: no more materials (02zg)
        return _fitting_work(here, mind, bid, what, lvl)
    camp = b["structure"] == "camp"
    if camp and what not in ("beds", "fire ring"):                             # a lean-to keeps 10 weight: no stores, no hearth (D4-94)
        raise Refused(f"{b['name']} is a camp: it takes only beds and a fire ring (a store or a hearth needs a building)")
    sp = int(f.get("spaces", 0)) - int(f.get("room", 0))                       # a vault brings its own room
    free = BL.free_floor(b, here.stock(bid)) if not camp else 99
    n = max(1, int(_qty(a.get("qty"), 1))) if f.get("per") else 1
    if f.get("per"):
        n = min(n, free // sp) if sp > 0 else n
        if n <= 0:
            raise Refused(f"{b['name']} has no free floor for {f['label']} ({sp} space{'s' if sp != 1 else ''} a {f['per']}): "
                          f"{BL.space_words(b, here.stock(bid))}. Add a room, or make room")
    elif b["fittings"].get(what):
        raise Refused(f"{b['name']} already has {f['label']}")
    elif sp > free:
        raise Refused(f"{b['name']} has no free floor for {f['label']} (it takes {sp} space{'s' if sp != 1 else ''}): "
                      f"{BL.space_words(b, here.stock(bid))}. Add a room, or make room")
    if f.get("heavy") and not camp and BL.fitting_spaces(b, heavy=True) + int(f.get("spaces", 0)) * n > BL.footprint(b) + int(f.get("room", 0)):
        raise Refused(f"{f['label']} goes on the ground floor, and {b['name']}'s ground floor has no room for it")
    if f.get("ground") or f.get("room"):
        _ground_check(here, b["parcel"], int(f.get("ground", 0)) + int(f.get("room", 0)) * n, f["label"])
    _consume(here, f["materials"], TRY[lvl]["inputs"] * n, b["stock"] if here.may_take(b["stock"]) else None)
    ok = here.rng("build", here.day, here.name, what).random() < TRY[lvl]["chance"]
    KN.tried(here, mind, what, ok)
    if not ok:
        return f"Your try at {f['label']} went wrong; the materials are spoilt."
    under[what] = {"n": n, "units_left": float(f["units"]) * n}                  # its work charged over days, as a building's
    here.apply("set", ref=("building", bid), field="fitting_work", value=under)
    here.record("build", what, party)
    return _fitting_work(here, mind, bid, what, lvl, started=True)


def _fitting_work(here, mind, bid, what, lvl, started=False):
    """A fitting's work, two units an action (more with skill), until it is done; it counts only when finished (02zg)."""
    _at_work(here, bid)
    f = FITTINGS[what]
    b = here.buildings()[bid]
    under = dict(b.get("fitting_work") or {})
    u = dict(under[what])
    done = round(2 * KN.skill(mind, what) * here.yield_mult(), 2)
    u["units_left"] = round(max(0.0, float(u["units_left"]) - done), 2)
    n = int(u["n"])
    words = f"{str(n) + ' ' if f.get('per') else ''}{f['label']}"
    if u["units_left"] > 1e-9:
        under[what] = u
        here.apply("set", ref=("building", bid), field="fitting_work", value=under)
        here.event("build", f"{here.name} was working on {words} in {b['name']}", actor=here.name, about=[f"building:{bid}"],
                   salience=0.2, tags=["building"])
        return ("You began " if started else "You worked on ") + f"{words} in {b['name']}: about {show(u['units_left'])} units of work left."
    under.pop(what)
    here.apply("set", ref=("building", bid), field="fitting_work", value=under or None)
    fit = dict(b["fittings"])
    fit[what] = int(fit.get(what, 0)) + n
    here.apply("set", ref=("building", bid), field="fittings", value=fit)
    if f.get("room"):                                                          # a vault: a stone room of its own (02zh §4)
        rooms = BL.rooms(b) + [{"kind": what, "floor": int(f["room"]), "storey": 1} for _ in range(n)]
        here.apply("set", ref=("building", bid), field="rooms", value=rooms)
        here.apply("set", ref=("building", bid), field="size", value=sum(int(r["floor"]) for r in rooms))
    here.event("build", f"{here.name} put {words} into {b['name']}", actor=here.name, about=[f"building:{bid}"], salience=0.3, tags=["building"])
    return f"You put {words} into {b['name']}."


def _build_work(here, mind, bid, lvl, started=False):
    _at_work(here, bid)
    b = here.buildings()[bid]
    u = dict(b["unfinished"])
    done = round(2 * KN.skill(mind, u["blueprint"]) * here.yield_mult(), 2)
    u["units_left"] = round(max(0.0, u["units_left"] - done), 2)
    here.record("build", u["blueprint"], None)
    if u["units_left"] > 1e-9:                                                 # heard and seen at work (signs.BUILDING)
        here.event("build", f"{here.name} was working on {b['name']}", actor=here.name, about=[f"building:{bid}"], salience=0.2,
                   tags=["building"])
    if u["units_left"] <= 1e-9:
        bp = BLUEPRINTS.get(u["blueprint"]) or MONUMENTS.get(u["blueprint"]) or {}
        here.apply("set", ref=("building", bid), field="unfinished", value=None)
        here.apply("set", ref=("building", bid), field="built_day", value=here.day)
        if bp.get("fittings"):                                                 # a blueprint that comes fitted (a camp: D2-68)
            here.apply("set", ref=("building", bid), field="fittings", value=dict(bp["fittings"]))
        if bp.get("lasts"):
            here.apply("set", ref=("building", bid), field="lasts_until", value=here.day + int(bp["lasts"]))
        here.event("build", f"{here.name} finished {b['name']}", actor=here.name, about=[f"building:{bid}"], salience=0.6, tags=["building", "shelter"])
        KN.tried(here, mind, u["blueprint"], True)
        if bp.get("fittings"):
            return f"You made {b['name']}: shelter for {bp['size']} with a fire, for about {bp['lasts']} nights."
        if b.get("monument"):
            return (f"You finished {b['name']}. It has room for {BL.places(b)} lines written on it (write {{\"at\": \"{b['name']}\", "
                    "\"text\"}).")
        return (f"You finished {b['name']}: {BL.floor(b)} spaces of floor, all free. It has no fittings yet: beds, a hearth and bins "
                "make it a house.")
    here.apply("set", ref=("building", bid), field="unfinished", value=u)
    return ("You began " if started else "You worked on ") + f"{b['name']}: about {show(u['units_left'])} units of work left."


# ---------------------------------------------------------------------- writing on buildings (D2-169, D2-170; building_lines.md)
def _writing_site(here, at):
    bid = here.building(at) if at else None
    if bid is None:
        names = ", ".join(b["name"] for b in here.buildings().values() if not b.get("unfinished")) or "none"
        raise Refused(f"say which building or monument here to write on (\"at\": {names})")
    b = here.buildings()[bid]
    if b.get("unfinished"):
        raise Refused(f"{b['name']} is not finished")
    if b["condition"] <= 0:
        raise Refused(f"{b['name']} is a ruin: there is nothing left to write on")
    if b["structure"] == "camp":
        raise Refused(f"{b['name']} is a lean-to of branches: there is nothing to write on")
    return bid, b


def _slot_of(b, x):
    """A line's place: its number (1 up) or where it is ("over the door")."""
    if x is None or str(x).strip() == "":
        return None
    s = str(x).strip().lower()
    try:
        k = int(float(s)) - 1
        return k if 0 <= k < BL.places(b) else -1
    except ValueError:
        pass
    for k in range(BL.places(b)):
        if BL.spot_words(b, k) in s or s in BL.spot_words(b, k):
            return k
    return -1


def _write_how(b, a):
    how = str(a.get("how") or "paint").strip().lower()
    how = {"painted": "paint", "painting": "paint", "carved": "carve", "carving": "carve", "cut": "carve", "engrave": "carve"}.get(how, how)
    if how not in ("paint", "carve"):
        raise Refused("a line is painted (\"how\": \"paint\") or carved (\"how\": \"carve\", with a tool)")
    return "stone" if how == "carve" and b["structure"] == "stone" else how


def write_units(here, a, erase=False) -> int:
    """The work of a line (D2-170): painting 2, carving 4, in stone 6; another's line, or the description, the same plus 1."""
    try:
        bid, b = _writing_site(here, a.get("at"))
    except Refused:
        return 0
    if erase:
        k = _slot_of(b, a.get("line"))
        ln = next((x for x in b.get("lines") or [] if int(x["slot"]) == k), None)
        if ln is None:
            return 0
        return int(LINES["units"][ln.get("how", "paint")]) + (int(LINES["other"]) if ln.get("by") != here.name else 0)
    if a.get("description") is not None and a.get("text") is None:
        d = b.get("description") or {}
        return int(LINES["units"]["paint"]) + (int(LINES["other"]) if d and d.get("by") != here.name else 0)
    try:
        how = _write_how(b, a)
    except Refused:
        return 0
    k = _slot_of(b, a.get("line"))
    ln = next((x for x in b.get("lines") or [] if int(x["slot"]) == k), None) if k is not None else None
    return int(LINES["units"][how]) + (int(LINES["other"]) if ln and ln.get("by") != here.name else 0)


def _write(here, mind, a, party):
    bid, b = _writing_site(here, a.get("at"))
    if a.get("description") is not None and a.get("text") is None:           # the description replaced (D2-169)
        text = BL.cap_text(a["description"], "description")
        if not text:
            raise Refused("say what to write (\"description\": text)")
        old = b.get("description") or {}
        _at_work(here, bid)
        here.apply("set", ref=("building", bid), field="description",
                   value={"text": text, "by": here.name, "day": here.day, "was": old.get("text")})
        if old and old.get("by") != here.name:
            _changed(here, bid, b, f"the words describing {b['name']} have been changed")
        here.event("write", f"{here.name} was painting new words on {b['name']}", actor=here.name, about=[f"building:{bid}"],
                   salience=0.6, tags=["building"], own=3.0)
        here.record("write", "description", party, site=bid)
        return f"You wrote on {b['name']}: “{text}”."
    text = BL.cap_text(a.get("text"), "line")
    if not text:
        raise Refused("say what to write (\"text\")")
    how = _write_how(b, a)
    lines = [dict(x) for x in b.get("lines") or []]
    k = _slot_of(b, a.get("line"))
    if k == -1:
        raise Refused(f"{b['name']} has {BL.places(b)} places for lines: say one by its number (1 to {BL.places(b)}) or where it is")
    if k is None:
        used = {int(x["slot"]) for x in lines}
        k = next((i for i in range(BL.places(b)) if i not in used), None)
        if k is None:
            raise Refused(f"every place on {b['name']} is written on ({BL.places(b)}): replace one (\"line\": its number) or erase one")
    if how in ("carve", "stone"):
        tool, m = here.best_tool(LINES["carve_tools"])
        if tool is None:
            raise Refused("carving needs a tool in your hands")
        if how == "stone":
            _mason(mind)
        here.apply("wear", container=here.hands, item=tool, uses=float(LINES["carve_wear"]))
    old = next((x for x in lines if int(x["slot"]) == k), None)
    _at_work(here, bid)
    lines = [x for x in lines if int(x["slot"]) != k] + [{"slot": k, "text": text, "by": here.name, "day": here.day, "how": how,
                                                          "was": old["text"] if old else None, "was_by": old["by"] if old else None}]
    here.apply("set", ref=("building", bid), field="lines", value=sorted(lines, key=lambda x: int(x["slot"])))
    spot = BL.spot_words(b, k)
    verb = {"paint": "painting", "carve": "carving", "stone": "cutting"}[how]
    if old and old.get("by") != here.name:
        _changed(here, bid, b, f"the line {spot} of {b['name']} has been " + ("painted over" if how == "paint" else "cut away")
                 + " and new words put there")
    here.event("write", f"{here.name} was {verb} words {spot} of {b['name']}", actor=here.name, about=[f"building:{bid}"],
               salience=0.6 if not old else 0.8, tags=["building"], own=3.0)
    here.record("write", how, party, site=bid)
    return f"You {'painted' if how == 'paint' else 'carved'} {spot} of {b['name']}: “{text}”."


def _erase(here, mind, a, party):
    bid, b = _writing_site(here, a.get("at"))
    k = _slot_of(b, a.get("line"))
    ln = next((x for x in b.get("lines") or [] if int(x["slot"]) == k), None) if k is not None else None
    if ln is None:
        have = "; ".join(f"{int(x['slot']) + 1}: {BL.spot_words(b, int(x['slot']))}" for x in b.get("lines") or []) or "none"
        raise Refused(f"say which line of {b['name']} to scratch out (\"line\": {have})")
    if ln.get("how") in ("carve", "stone"):
        tool, m = here.best_tool(LINES["carve_tools"])
        if tool is None:
            raise Refused("scratching out a carved line needs a tool in your hands")
        here.apply("wear", container=here.hands, item=tool, uses=float(LINES["carve_wear"]))
    _at_work(here, bid)
    here.apply("set", ref=("building", bid), field="lines", value=[x for x in b["lines"] if int(x["slot"]) != k])
    spot = BL.spot_words(b, k)
    if ln.get("by") != here.name:
        _changed(here, bid, b, f"the line {spot} of {b['name']} has been scratched out")
    here.event("write", f"{here.name} was scratching out the words {spot} of {b['name']}", actor=here.name, about=[f"building:{bid}"],
               salience=0.9, tags=["building"], own=3.0)
    here.record("erase", ln.get("how"), party, site=bid, was=ln["text"], was_by=ln.get("by"))
    return f"You scratched out the line {spot} of {b['name']} (it said: “{ln['text']}”)."


def _changed(here, bid, b, text):
    """What its people will notice the next time they see it (building_lines.md §3)."""
    ch = list(b.get("changes") or []) + [{"day": here.day, "text": text, "by": here.name}]
    here.apply("set", ref=("building", bid), field="changes", value=ch[-20:])


# ---------------------------------------------------------------------- goods
def _store_here(here, at=None) -> str:
    if at:
        bid = here.building(at)
        if bid is None:
            raise Refused(f"there is no building called {at!r} here")
    else:
        mine = [b for b in here.homes_here()] or [b for b in here.buildings() if here.may_take(here.buildings()[b]["stock"])]
        if not mine:
            raise Refused("there is no store here that is yours to use")
        bid = mine[0]
    if not here.may_take(here.buildings()[bid]["stock"]):
        raise Refused(f"{here.buildings()[bid]['name']}'s store is not yours to use (to take without the right is theft; to put, leave)")
    return bid


def _move(here, mind, a, party):
    item = item_of(a.get("item"))
    to = str(a.get("to") or "store").strip().lower()
    bid = _store_here(here, a.get("at"))
    b = here.buildings()[bid]
    if to in ("hands", "hand", "me", "myself", "carry", "carried", "pack"):
        src, dst, verb, have = b["stock"], here.hands, "took", here.stock(bid).get(item, 0.0)
    else:
        src, dst, verb, have = here.hands, b["stock"], "put", here.carried().get(item, 0.0)
    if have <= 1e-9:                                                           # where it is, or who took it (D4-95)
        if verb == "put":
            where = [(c, here.contents(c).get(item, 0.0)) for c in here.takeable() if c != here.hands]
            where = [(c, q) for c, q in where if q > 1e-9]
            raise Refused(f"there is no {item} in your hands" + (
                "; " + ", ".join(f"{_store_name(here, c)} holds {show(q)}" for c, q in where)
                + " (work done for your household puts what it gives straight into its store)" if where else _short_note(here, item)))
        raise Refused(f"there is no {item} in {b['name']}" + _short_note(here, item))
    q = round(min(_qty(a.get("qty"), have), have), 6)
    full = _full_note(here, b["stock"], item, q) if verb == "put" else ""      # what does not fit lies at its door (D2-155, D4-94)
    here.apply("transfer", src=src, dst=dst, item=item, qty=q)
    if verb == "took":
        _drawn(here, src, item, q)
    here.event("store", f"{here.name} {verb} {item} {'into' if verb == 'put' else 'from'} {b['name']}", actor=here.name,
               about=[f"building:{bid}"], salience=0.1, tags=["food"] if ITEMS[item]["food"] else [])
    return (f"You {verb} {show(q)} {item} {'into' if verb == 'put' else 'from'} {b['name']}" + full
            + f" (it holds {show(here.stock(bid).get(item, 0.0))}).")


def _take(here, mind, a, party):
    item = item_of(a.get("item"))
    src_name = str(a.get("from") or "")
    rem = here.find_thing(src_name, item)                        # what one knows lies here (D2-87: nobody's)
    from cybertron2.engine import tags as TG
    tag = TG.tag_in(src_name) if here.setting("tags") else None
    if rem is None and tag and here.building(src_name) is None:              # a thing named by its tag: say why not (D4-94)
        if not here.tagged_here(tag):
            raise Refused(f"you know of nothing called {tag} here")
        raise Refused(f"{tag} holds no {item}" if item else f"{tag} holds nothing")
    if rem is None and here.parcel(src_name) is not None and here.building(src_name) is None:
        rem = here.search_thing(src_name, item)                  # not known of: one looks, as it is seen or hidden (D4-70)
        if rem is None:
            raise Refused(f"you looked over {here.parcels()[here.parcel(src_name)]['name']} and found no {item} lying there")
    if rem:
        c = here.thing(rem)
        door = c.get("door") if c.get("door") in here.buildings() else None         # left at a door: the house's (D4-89)
        src, theft = rem, bool(door) and not here.may_take(here.buildings()[door]["stock"])
        bid = door
        label = f"what {c['of']} left" if c.get("body") else f"what lay at {here.spot_name(c)}"
        have = c["goods"].get(item, 0.0)
        if c.get("by") != here.name:
            f = mind.store.setdefault("found", [])
            if rem not in f:
                f.append(rem)                                                   # finding things trains the eye (D2-91)
    else:
        bid = here.building(src_name)
        if bid is None:
            raise Refused(f"there is no building called {src_name!r} here")
        b = here.buildings()[bid]
        if not here.can_enter(bid):
            raise Refused(f"{b['name']}'s door is barred")
        src, label, theft = b["stock"], b["name"], not here.may_take(b["stock"])
        have = here.stock(bid).get(item, 0.0)
    q = round(min(_qty(a.get("qty"), have), have), 6)
    if q <= 1e-9:
        raise Refused(f"you find no {item} in {label}" + (_short_note(here, item) if not rem else ""))
    here.apply("transfer", src=src, dst=here.hands, item=item, qty=q)
    if not rem:
        _drawn(here, src, item, q)
    if theft:
        here.today()["thefts"].append({"by": here.name, "building": bid, "item": item, "qty": round(q, 2), "door": bool(rem)})
        here.record("take", None, None, theft=True)
        return f"You took {show(q)} {item} from {label}, which is not yours to take from. Whether anyone saw, you will learn."
    c = here.thing(src) or {"kind": "stock"}
    here.event("take", f"{here.name} took {item} from {label}", actor=here.name, salience=0.4 if c["kind"] in TH.KINDS else 0.3,
               about=[f"parcel:{c['parcel']}"] if c.get("parcel") else [], tags=["food"] if ITEMS[item]["food"] else [])
    if c["kind"] in TH.KINDS:
        here.remember_thing(src, "took")
    return f"You took {show(q)} {item} from {label}."


def _give(here, mind, a, party):
    """Giving (D2-111, world/things_in_places.md): to a person here, into their hands; to a household or a building one may use, into
    its store; to a building one may not use, or someone not here, at its door, in the open; to a place, left there (hidden, with the
    `hidden` modifier)."""
    to_raw = a.get("to") or a.get("at")
    to = here.person(to_raw)
    item, q = item_of(a.get("item")), _qty(a.get("qty"))
    if to and to != here.name:
        if party and party != here.name and party != here.household() and not here.works_for(party):
            raise Refused(f"'for' gives from that household's store, which is not yours: to give to {party}, give with 'to' instead")
        src = here.hands if not party or party == here.name else _out(here, party)
        if src == here.hands:
            _top_up(here, item, q)                                             # from the stores here one may use (D4-96)
        have = here.carried().get(item, 0.0) if src == here.hands else here.stock(src[len("stock:"):]).get(item, 0.0)
        if have + 1e-9 < q:
            raise Refused(f"there is only {show(have)} {item} to give" + _short_note(here, item))
        here.apply("transfer", src=src, dst=here.hands_of(to), item=item, qty=q)
        here.event("give", f"{here.name} gave {q:g} {item} to {to}", actor=here.name, target=to, about=[f"person:{to}"], salience=0.35,
                   tags=["food"] if ITEMS[item]["food"] else [], concerns=[to])
        here.record("give", None, party, to=to, item=item, qty=q)
        return f"You gave {q:g} {item} to {to}."
    if party and party != here.name and party != here.household() and not here.works_for(party):
        raise Refused(f"'for' gives from that household's store, which is not yours")
    src = here.hands if not party or party == here.name else _out(here, party)      # from one's household's store (D2-37)
    if src == here.hands and here.person(to_raw) is None and here.building(to_raw) is None:
        _top_up(here, item, q)                                                 # left at a place: from the stores here too (D4-96)
    have = here.carried().get(item, 0.0) if src == here.hands else here.stock(src[len("stock:"):]).get(item, 0.0)
    if have + 1e-9 < q:
        raise Refused(f"you carry only {show(have)} {item}" if src == here.hands else f"there is only {show(have)} {item} in the store")
    if src != here.hands:                                                     # into one's hands first, then given on
        here.apply("transfer", src=src, dst=here.hands, item=item, qty=q)
    pid = here.parcel(to_raw)
    bid = here.building(to_raw)
    if pid is not None and bid is None:
        return _put_down(here, mind, a, item, q, pid)
    hh = None
    if bid is None:
        try:
            hh = _party(here, to_raw)
        except Refused:
            hh = here.someone(to_raw)
        if hh in here.households():
            house = here.party_container(hh)
            if house and house.startswith("stock:") and here.can_enter(house[len("stock:"):]):
                return _into_store(here, house[len("stock:"):], item, q, party, hh)
            bid = here.house_of(hh)
        elif hh:                                                                   # someone not here: left at their door (D2-111)
            bid = here.house_of(hh)
            if bid is not None:
                return _put_down(here, mind, a, item, q, here.buildings()[bid]["parcel"], door=bid)
        if bid is None:
            raise Refused(f"there is nobody, no household's house and no place called {to_raw!r} here")
    b = here.buildings()[bid]
    if here.may_take(b["stock"]) or here.can_enter(bid):
        return _into_store(here, bid, item, q, party, hh)
    return _put_down(here, mind, a, item, q, b["parcel"], door=bid)


def _into_store(here, bid, item, q, party, hh):
    b = here.buildings()[bid]
    full = _full_note(here, b["stock"], item, q)                              # what does not fit lies at its door (D2-155)
    here.apply("transfer", src=here.hands, dst=b["stock"], item=item, qty=q)
    owners = here.households()[hh]["name"] if hh else None
    here.event("give", f"{here.name} put {q:g} {item} into {b['name']}" + (f", for {owners}" if owners else ""), actor=here.name,
               about=[f"building:{bid}"], salience=0.35, tags=["food"] if ITEMS[item]["food"] else [],
               concerns=list(here.institution(hh)["members"]) if hh else [])
    here.today()["left"].append({"by": here.name, "item": item, "qty": q, "building": bid})   # its household finds it in the morning
    here.record("give", None, party, to=hh or bid, item=item, qty=q)
    return (f"You gave {q:g} {item} to {owners}: it is in {b['name']}" if owners else f"You left {q:g} {item} at {b['name']}") + full + "."


def _put_down(here, mind, a, item, q, pid, door=None):
    """Left at a spot, in the open (D2-87): nobody's; hidden with the `hidden` modifier (D2-93)."""
    mods = MOD.resolve(here, mind, "give", a, place=True)
    how = mods.get("hidden")
    untaught = bool(how) and any(TECHNIQUES[m]["key"] == "hidden" for m in mods["_untaught"])
    cid = here.apply("new_thing", node=here.node, parcel=pid, kind="pile", by=here.name, hidden=how, untaught=untaught, door=door)
    here.apply("transfer", src=here.hands, dst=cid, item=item, qty=q)
    here.remember_thing(cid, "put")
    MOD.practise(here, mind, mods)
    pname = here.parcels()[pid]["name"]
    where = f"at the door of {here.buildings()[door]['name']}" if door else f"at {pname}"
    verb = {"under brush": "hid", "buried": "buried"}.get(how, "left")
    tail = {"under brush": " under brush", "buried": " in the ground"}.get(how, "")
    here.event("put", f"{here.name} {verb} {item} {where}{tail}", actor=here.name,
               about=[f"parcel:{pid}"] + ([f"building:{door}"] if door else []), salience=0.25 if how else 0.4,
               tags=["food"] if ITEMS[item]["food"] else [], concerns=here.living_in(door) if door else [])
    here.record("give", None, None, to=f"parcel:{pid}", item=item, qty=q, hidden=how)
    out = f"You {verb} {q:g} {item} {where}" + (tail or ", in the open")
    if door:
        out += " (you could not put it inside)"
    if untaught:
        out += ". You have never been shown how to hide things well; it is not as well hidden as it might be"
    return out + "."


def _alias_give(hidden=None):
    def f(a):
        b = {**a, "to": a.get("to") or a.get("at")}
        if hidden and not b.get("hidden"):
            b["hidden"] = hidden
        return b
    return f


ALIASES = {"leave": _alias_give(), "put": _alias_give(), "drop": _alias_give(), "hide": _alias_give("under brush")}


# ---------------------------------------------------------------------- hosting and grants (05 §3; D4-23 rights)
def _house_for_grant(here, at):
    bid = here.building(at) if at else (here.homes_here() or [None])[0]
    if bid is None:
        raise Refused("say which house here")
    if not here.may_grant(("building", bid)):
        raise Refused(f"you may not let people into {here.buildings()[bid]['name']}")
    return bid


def _host(here, mind, a, party):
    who = here.person(a.get("person") or a.get("to"))
    if who is None or who == here.name:
        raise Refused(f"there is nobody called {a.get('person') or a.get('to')!r} here")
    bid = _house_for_grant(here, a.get("at"))
    feed = str(a.get("feed", "")).lower() in ("true", "yes", "1")
    here.apply("claim", thing=("building", bid), claimant=who, rights=["access", "withdrawal"] if feed else ["access"], grounds="granted",
               until=here.day, by=here.name)
    b = here.buildings()[bid]
    here.event("host", f"{here.name} took {who} in for the night at {b['name']}" + (", at the household's table" if feed else ""),
               actor=here.name, target=who, salience=0.4, tags=["shelter"], concerns=[who])
    return f"You let {who} sleep at {b['name']} tonight" + (" and eat from its store." if feed else " (a bed, if one is free; not its food).")


def _grant(here, mind, a, party):
    bid = _house_for_grant(here, a.get("at"))
    to_raw = str(a.get("to") or "").strip()
    who = "anyone" if to_raw.lower() in ("anyone", "everyone", "all") else (here.person(to_raw) or _party(here, to_raw))
    what = str(a.get("what") or "shelter").lower()
    rights = ["access", "withdrawal"] if "food" in what or "store" in what else ["access"]
    days = a.get("days")
    until = here.day + int(_qty(days)) - 1 if days else None
    here.apply("claim", thing=("building", bid), claimant=who, rights=rights, grounds="granted", until=until, by=here.name)
    b = here.buildings()[bid]
    here.event("grant", f"{here.name} let {who} use {b['name']}" + (" and its store" if "withdrawal" in rights else ""), actor=here.name,
               salience=0.4, tags=["shelter"], concerns=[who] if who in here.people() else [])
    return f"{who} may now use {b['name']}" + (" and its store" if "withdrawal" in rights else "") + (f" for {days} days." if days else ", until you revoke it.")


def _revoke(here, mind, a, party):
    bid = _house_for_grant(here, a.get("at"))
    to_raw = str(a.get("to") or "").strip()
    who = "anyone" if to_raw.lower() in ("anyone", "everyone", "all") else (here.person(to_raw) or to_raw)
    ended = [cid for cid, c in here.claim_records(("building", bid)) if c["claimant"] == who and c["grounds"] == "granted"]
    if not ended:
        raise Refused(f"{who} has no grant to {here.buildings()[bid]['name']}")
    for cid in ended:
        here.apply("end_claim", claim=cid)
    return f"You ended {who}'s use of {here.buildings()[bid]['name']}."


# ---------------------------------------------------------------------- households (09 §2d; D4-36)
def _join(here, mind, a, party):
    hh = _party(here, a.get("household"))
    if hh not in here.households():
        raise Refused(f"{a.get('household')!r} is not a household")
    if hh == here.household():
        raise Refused("you already belong to it")
    here.today()["joins"].append({"by": here.name, "household": hh})
    return f"You asked to be taken into {here.households()[hh]['name']}; it happens if one of them who may admit you does so today."


def _admit(here, mind, a, party):
    who = here.person(a.get("person") or a.get("to"))
    hh = here.household()
    if who is None or hh is None:
        raise Refused("there is nobody by that name here, or you have no household")
    rule = here.institution(hh)["rules"].get("admit", "head")
    if rule == "head" and here.head(hh) != here.name:
        raise Refused(f"only the head of {here.institution(hh)['name']} may take someone in")
    here.today()["admits"].append({"by": here.name, "person": who, "household": hh})
    return f"You agreed to take {who} into {here.institution(hh)['name']}, if {who} asks today."


def _leave_household(here, mind, a, party):
    hh = here.household()
    if hh is None:
        raise Refused("you belong to no household")
    here.apply("leave", person=here.name, inst=hh)
    here.event("household", f"{here.name} left {here.institution(hh)['name']}", actor=here.name, salience=0.6, tags=["household"],
               concerns=here.institution(hh)["members"])
    return f"You left {here.institution(hh)['name']}. You keep what you carry."


def _found(here, mind, a, party):
    name = str(a.get("name") or here.name).strip()[:30]
    old = here.household()
    iid = here.apply("found", person=here.name, name=name)
    here.event("household", f"{here.name} set up a household of their own", actor=here.name, salience=0.6, tags=["household"],
               concerns=here.institution(old)["members"] if old else [])
    return f"You are now the head of {here.institution(iid)['name']}. You have no house yet: claim an empty one, build one, or be let into one."


def _claim(here, mind, a, party):
    x = a.get("thing") or a.get("what")
    key = here.parcel(x)
    kind = "parcel"
    if key is None:
        key, kind = here.building(x), "building"
    if key is None:
        key, kind = here.herd(x) if x else None, "herd"
    if key is None:
        raise Refused(f"there is no field, building or herd called {x!r} here")
    claimant = party or here.name
    plots = a.get("plots")
    if plots not in (None, "") and kind == "parcel":                          # plots of a field, pasture or meadow (D2-163)
        return _claim_plots(here, key, claimant, plots)
    if plots not in (None, ""):
        raise Refused("only a field, pasture or meadow is held in plots")
    here.apply("claim", thing=(kind, key), claimant=claimant, rights="all", grounds="claimed")
    name = {"parcel": here.parcels, "building": here.buildings, "herd": here.herds}[kind]()[key]["name"]
    own = {claimant, here.household(), "anyone"}
    hh = here.households()
    others = sorted({hh[c["claimant"]]["name"] if c["claimant"] in hh else c["claimant"] for c in here.claims((kind, key))
                     if c["claimant"] not in own and c["grounds"] != "granted"})
    who = hh[claimant]["name"] if claimant in hh else claimant
    here.event("claim", f"{here.name} claimed {name}" + ("" if claimant == here.name else f" for {who}") + (f", which {', '.join(others)} also claim" if others else ""),
               actor=here.name, about=[f"{kind}:{key}"], salience=0.7 if others else 0.5, tags=["land"], concerns=_holders_people(here, (kind, key)))
    return f"You claimed {name}" + ("" if claimant == here.name else f" for {who}") + "." + (f" {', '.join(others)} claim it too: a dispute." if others else "")


def _claim_plots(here, key, claimant, plots) -> str:
    """A claim of n plots of a field, pasture or meadow (D2-163): of the unclaimed plots first; any more overlaps what others hold,
    which is recorded as a dispute, never refused (D4-23). The overlap is counted against the holder with the most plots there."""
    par = here.parcels()[key]
    if par["cover"] not in FM.LAND:
        raise Refused(f"{par['name']} is not held in plots; claim it whole")
    try:
        n = int(float(plots))
    except (TypeError, ValueError):
        raise Refused("plots must be a whole number")
    size = int(par["size"])
    if n < 1:
        raise Refused("claim at least one plot")
    n = min(n, size)
    hold = FM.holdings(here.claims(("parcel", key)), size)
    free = max(0, size - sum(hold.values()))
    over = max(0, n - free)
    mine = {claimant, here.household(), here.name}
    others = sorted(((h, k) for h, k in hold.items() if h not in mine), key=lambda hk: -hk[1])
    of = others[0][0] if over and others else None
    over = min(over, hold.get(of, 0)) if of else 0
    here.apply("claim", thing=("parcel", key), claimant=claimant, rights="all", grounds="claimed", plots=n,
               **({"of": of, "over": over} if of else {}))
    names = FM.names_of(here)
    who = names.get(claimant, claimant)
    what = f"{n} plot{'s' if n != 1 else ''} of {par['name']}"
    clash = f", {over} of them {FM.possessive(names, of)}" if of else ""
    here.event("claim", f"{here.name} claimed {what}" + ("" if claimant == here.name else f" for {who}") + clash, actor=here.name,
               about=[f"parcel:{key}"], salience=0.7 if of else 0.5, tags=["land"], concerns=_holders_people(here, ("parcel", key)))
    return (f"You claimed {what}" + ("" if claimant == here.name else f" for {who}") + "."
            + (f" {over} of them {'is' if over == 1 else 'are'} {FM.possessive(names, of)}: a dispute." if of else ""))


def _sleep(here, mind, a, party):
    bid = here.building(a.get("at"))
    if bid is None:
        raise Refused(f"there is no building called {a.get('at')!r} here")
    if not here.can_enter(bid):
        raise Refused(f"{here.buildings()[bid]['name']}'s door is barred")
    here.today()["sleep"][here.name] = bid
    note = "" if "access" in here.rights(("building", bid)) else " (nobody let you in: those who hold it will know)"
    return f"You mean to sleep at {here.buildings()[bid]['name']} tonight, if a bed is free{note}."


def _set(here, mind, a, party):
    bid = here.building(a.get("at")) if a.get("at") else (here.homes_here() or [None])[0]
    if bid is None:
        raise Refused("say which building")
    if "management" not in here.rights(("building", bid)):                   # who does, by the claims (D4-95)
        b = here.buildings()[bid]
        who = [x for x in here.people() if "management" in here.rights(("building", bid), x)]
        hh = here.households().get(b.get("household") or "", {}).get("name") if b.get("household") else None
        raise Refused(f"only those who manage {b['name']} set its door: its holder's head"
                      + (f" ({hh})" if hh else "") + (f"; here today: {', '.join(who)}" if who else "; none of them is here")
                      + ". A member may use it but not bar or open it")
    to = str(a.get("to") or "").lower()
    if to not in ("open", "barred"):
        raise Refused('set {"thing": "door", "to": "open" or "barred"}')
    here.apply("set", ref=("building", bid), field="door", value=to)
    return f"{here.buildings()[bid]['name']}'s door is now {to}."


# ---------------------------------------------------------------------- travel (D4-8, D4-32)
def _travel(here, mind, a, party):
    if not str(a.get("to") or "").strip() and here.road_to(a.get("stop at")) is not None:
        a = {**{k: v for k, v in a.items() if k != "stop at"}, "to": a["stop at"]}   # a way named as the stop: it is where one goes
    if not str(a.get("to") or "").strip():
        ways = ", ".join(f"{n} ({k} day{'s' if k > 1 else ''})" for _, n, k, _t in here.roads())
        raise Refused(f'say where in "to" (a place, or a way as the roads name it); from here: {ways or "nowhere"}')
    r = here.road_to(a.get("to"))
    if r is None:
        ways = ", ".join(f"{n} ({k} day{'s' if k > 1 else ''})" for _, n, k, _t in here.roads())
        raise Refused(f"there is no way from here to {a.get('to')!r}; from here you can go to {ways or 'nowhere'}")
    to, days, track = r
    ox = None
    if a.get("lead") not in (None, "", False):                                # a pack ox (D2-136)
        ox = here.pack_ox(a.get("lead"))
        if ox is None:
            raise Refused("to lead a pack ox you need an ox of your household's here and a harness in your hands")
    load, cap = here.load(), here.capacity(track, oxen=1 if ox else None)
    if load > cap + 1e-9:
        cart = any(ITEMS[i].get("track") for i, q in here.carried().items() if q >= 1)
        raise Refused(f"you carry {math.ceil(load * 10 - 1e-9) / 10:g} weight; you can carry {cap:g} on this road, so set down "
                      f"at least {math.ceil((load - cap) * 10 - 1e-9) / 10:g}"
                      + (" (a cart needs a road with a track, and this one has none)" if cart and not track else ""))
    morning = bool(here.setting("evening")) and str(a.get("when") or "").lower() == "morning"
    if morning:                                                               # set off in the morning, in by nightfall (D4-67)
        here.today().setdefault("travel_morning", {})[here.name] = to
    else:
        here.today()["travel"][here.name] = to
    choices = {k: a[k] for k in ("on trouble", "stop at", "gather", "days", "meeting", "searching", "lead") if a.get(k) not in (None, "", False)}
    if choices:                                                               # the choices for the road (D2-105, D2-109, D2-113)
        here.today().setdefault("travel_choices", {})[here.name] = choices
    here.event("depart", f"{here.name} set off on the road", actor=here.name, salience=0.6, tags=["travel"])
    if morning:
        return (f"You set off this morning: you walk all day" + (f", {days - 1} night{'s' if days > 2 else ''} out on the road," if days > 1 else "")
                + f" and come in at {here.place_name(to)} by nightfall" + (f" of day {here.day + days}" if days > 1 else "")
                + ". Nothing more is done today.")
    if here.setting("evening"):
        return (f"You set off at nightfall: {days} night{'s' if days > 1 else ''} on the road, sleeping out; you come in at midday on day "
                f"{here.day + days + 1}, with half that day's units left. Nothing more is done today.")
    return (f"You set off at the end of the day: {days} day{'s' if days > 1 else ''} on the road, sleeping out; you arrive on the morning "
            f"of day {here.day + days + 1}. Nothing more is done today.")


# ---------------------------------------------------------------------- learning from others, force, rest
def _watch(here, mind, a, party):
    who = here.person(a.get("person") or a.get("to") or a.get("target"))
    if who is None or who == here.name:
        raise Refused(f"there is nobody called {a.get('person')!r} here to watch")
    here.today()["watch"][here.name] = who
    return f"You spend the day working beside {who}, watching how they do things."


def _teach(here, mind, a, party):
    to = here.person(a.get("to"))
    tech = KN.resolve(a.get("what"))
    if to is None or to == here.name:
        raise Refused(f"there is nobody called {a.get('to')!r} here to teach")
    if tech is None:
        raise Refused(f"{a.get('what')!r} is not something you can teach")
    if KN.level(mind, tech) != "known":
        raise Refused(f"you do not know {KN.label(tech)} well enough to teach it")
    here.today()["teach"].append({"by": here.name, "to": to, "tech": tech})
    return f"You set aside time to teach {to} {KN.label(tech)}; it happens if {to} also sets aside time to learn."


def _learn(here, mind, a, party):
    frm = here.person(a.get("from"))
    tech = KN.resolve(a.get("what"))
    if frm is None or frm == here.name:
        raise Refused(f"there is nobody called {a.get('from')!r} here to learn from")
    if tech is None:
        raise Refused(f"{a.get('what')!r} is not something you can learn")
    here.today()["learn"].append({"by": here.name, "from": frm, "tech": tech})
    return f"You set aside time to learn {KN.label(tech)} from {frm}; it happens if {frm} also sets aside time to teach."


def _attack(here, mind, a, party):
    tgt = str(a.get("target", ""))
    aim = "hurt" if str(a.get("aim", "rob")).lower() == "hurt" else "rob"
    who = here.person(tgt)
    if who and who != here.name:
        here.today()["fights"].append({"kind": "attack", "by": here.name, "target": who, "aim": aim, "node": here.node})
        here.event("threat", f"{here.name} squared up to {who}", actor=here.name, target=who, salience=0.7, tags=["danger"], concerns=[who])
        return f"You set on {who} ({aim}); it is settled tonight."
    bid = here.building(tgt)
    if bid:
        if bid in here.homes_here():
            raise Refused("that is your own house")
        here.today()["fights"].append({"kind": "raid", "by": here.name, "building": bid, "node": here.node})
        return f"You make ready to break into {here.buildings()[bid]['name']} tonight."
    raise Refused(f"no person or building called {tgt!r} here")


def _guard(here, mind, a, party):
    bid = here.building(a.get("at")) if a.get("at") else (here.homes_here() or [None])[0]
    here.today()["guards"][here.name] = bid
    here.apply("set", ref=("person", here.name), field="guarded", value={"day": here.day, "at": bid})   # for its signs (D4-74)
    return "You stand guard tonight" + (f" over {here.buildings()[bid]['name']}." if bid else ".")


def _rest(here, mind, a, party):
    return "You rested."


def _fire(here, mind, a, party):
    """A fire in the open for one night (D4-49): cooking where one sleeps out, from carried fuel by its heat, firewood first, as the
    night burns it (D2-157; D4-94)."""
    from cybertron2.engine import forests as FO
    need, have = float(here.p["heat"]["open"]), FO.heat_of(here.carried())
    if have + 1e-9 < need:
        raise Refused(f"a fire in the open takes {need:g} heat from what you carry ({FO.fuel_words(need)}); "
                      f"you carry {show(have)} heat of fuel")
    here.today().setdefault("fire", {})[here.name] = True
    return f"You mean to light a fire tonight if you sleep out ({need:g} heat: {FO.fuel_words(need)})."


def _accept(here, mind, a, party):
    from cybertron2.engine import agreements as AG
    return AG.accept(here, mind, a, party)


def _release(here, mind, a, party):
    from cybertron2.engine import agreements as AG
    return AG.release(here, mind, a)


def _withdraw(here, mind, a, party):
    from cybertron2.engine import agreements as AG
    return AG.withdraw(here, a)


def _repair(here, bid, m) -> str:
    """A break mended (D2-168): its materials when the mending starts (1 timber, stone for stone, for every 4 spaces of floor, at
    least 2), then its work, two units an action, until it is mended a step."""
    b = here.buildings()[bid]
    md = dict(b.get("mending") or {})
    if not md:
        need = BL.repair_need(b)
        _consume(here, need["materials"], extra=b["stock"] if here.may_take(b["stock"]) else None)
        md = {"units_left": float(need["units"]), "day": here.day}
    md["units_left"] = round(max(0.0, float(md["units_left"]) - 2 * m), 2)
    if md["units_left"] > 1e-9:
        here.apply("set", ref=("building", bid), field="mending", value=md)
        return f"You worked on mending {b['name']}: about {show(md['units_left'])} units of work left."
    here.apply("set", ref=("building", bid), field="mending", value=None)
    here.apply("set", ref=("building", bid), field="condition", value=b["condition"] + 1)
    return f"You repaired {b['name']}: it is now {('ruined', 'damaged', 'sound')[b['condition']]}."


def _clear_built(here, pid, name, done, party) -> str:
    """A unit of clearing for building (02zh §8): a field, pasture or meadow (4 units a unit of size), or scrub (10: grubbing out the
    roots of a felled wood) becomes built ground, and stops being farmland; held by whoever cleared it if nobody held it (D4-60)."""
    from cybertron2.engine.data import CLEARING
    p = here.parcels()[pid]
    need = float(CLEARING["built"][p["cover"]]) * float(p["size"])
    got = round(float(p.get("clearing_built") or 0.0) + done, 2)
    if got + 1e-9 < need:
        here.apply("set", ref=("parcel", pid), field="clearing_built", value=got)
        return f"You cleared ground for building at {name}: about {max(0, round(need - got, 1)):g} units of work left before it is built ground."
    cover = p["cover"]
    for f, v in (("cover", "built"), ("clearing_built", None), ("clearing", None), ("was", cover), ("crop", None), ("shares", None)):
        here.apply("set", ref=("parcel", pid), field=f, value=v)
    if "grass" in p["res"]:
        here.apply("set_res", parcel=pid, key="grass", fields={"S": 0.0, "K": 0.0})
    who = party or here.household() or here.name
    held = bool(here.claims(("parcel", pid)))
    if not held:
        here.apply("claim", thing=("parcel", pid), claimant=who, rights="all", grounds="cleared")
    total = BL.ground_total(here.parcels()[pid])
    here.event("work", f"{here.name} finished clearing {name} for building: it is built ground now", actor=here.name,
               about=[f"parcel:{pid}"], salience=0.6, tags=["building"])
    return (f"You finished clearing {name}: it is built ground now, {total} spaces for building"
            + ("." if held else ", and yours: you cleared it."))


# ---------------------------------------------------------------------- clearing new ground (Zach, 24 Oct)
def _clear(here, pid, name, done, party) -> str:
    """A unit of clearing: progress on the parcel; when its work is done it is a field, fallow, held by whoever cleared it by the
    custom of the land if nobody held it (a claim, grounds "cleared")."""
    from cybertron2.engine.data import CLEARING
    p = here.parcels()[pid]
    need = float(CLEARING[p["cover"]]) * float(p["size"])
    got = round(float(p.get("clearing") or 0.0) + done, 2)
    if got + 1e-9 < need:
        here.apply("set", ref=("parcel", pid), field="clearing", value=got)
        return f"You cleared ground at {name}: about {max(0, round(need - got))} units of work left before it is a field."
    cover = p["cover"]
    for f, v in (("cover", "field"), ("clearing", None), ("was", cover), ("crop", None), ("last_crop", "fallow"), ("broken", 0.0),
                 ("fertility", p.get("fertility") if p.get("fertility", 1.0) != 1.0 else float(CLEARING["fertility"][cover]))):
        here.apply("set", ref=("parcel", pid), field=f, value=v)
    who = party or here.household() or here.name
    held = bool(here.claims(("parcel", pid)))
    if not held:
        here.apply("claim", thing=("parcel", pid), claimant=who, rights="all", grounds="cleared")   # all its plots (D2-163)
    else:
        here.apply("shares", parcel=pid)                                      # its holders' plots become field holdings
    here.event("work", f"{here.name} finished clearing {name}: it is a field now, ready to be sown", actor=here.name,
               about=[f"parcel:{pid}"], salience=0.6, tags=["farming", "building"])
    return f"You finished clearing {name}: it is a field now, ready to be broken and sown" + ("." if held else ", and yours: you cleared it.")


# ---------------------------------------------------------------------- partners, children, the household's offices (D2-138 to D2-153)
def _units(x) -> int:
    try:
        return max(1, int(float(x if x is not None else 1)))
    except (TypeError, ValueError):
        raise Refused("units must be a number")


def _here_person(here, x, what="person"):
    who = here.person(x)
    if who is None or who == here.name:
        raise Refused(f"there is nobody called {x!r} here")
    return who


def _grown(here, who) -> bool:
    return here.body(who)["stage"] in ("youth", "adult", "elder")


def _partner(here, mind, a, party):
    who = _here_person(here, a.get("with") or a.get("person"))
    if not _grown(here, here.name) or not _grown(here, who):
        raise Refused(f"{who} is a child")
    if here.body(here.name)["partner"] == who:
        raise Refused(f"{who} is your partner already")
    here.today().setdefault("partner", []).append({"by": here.name, "with": who})
    return f"You chose {who} as your partner; it is so if {who} chooses you too today."


def _part(here, mind, a, party):
    who = here.body(here.name)["partner"]
    if not who:
        raise Refused("you have no partner")
    here.apply("partner", person=here.name, other=who, on=False)
    here.event("household", f"{here.name} and {who} have parted", actor=here.name, target=who, salience=0.6, tags=["family"],
               concerns=[who])
    return f"You and {who} are no longer partners."


def _try(here, mind, a, party):
    who = _here_person(here, a.get("with") or a.get("person"))
    me, them = here.body(here.name), here.body(who)
    if not me["sex"] or me["sex"] == them["sex"]:
        raise Refused("a child needs a man and a woman")
    if me["stage"] != "adult" or them["stage"] != "adult":
        raise Refused("you must both be grown adults")
    woman = here.name if me["sex"] == "f" else who
    if here.body(woman)["with_child"]:
        raise Refused(f"{'you are' if woman == here.name else woman + ' is'} with child already")
    if woman == here.name and here.life()["gap"]:
        raise Refused("you gave birth lately and cannot conceive yet")
    units = _units(a.get("units"))
    here.today().setdefault("try", []).append({"by": here.name, "with": who, "units": units})
    return f"You spent {units} unit{'s' if units > 1 else ''} trying for a child with {who}; it counts only if {who} tries with you today."


def _care(here, mind, a):
    x = a.get("at") or a.get("person") or a.get("child")
    who = here.person(x)
    young = [n for n in here.people(me=False) if here.body(n)["stage"] in ("infant", "child")]
    if who is None and len(young) == 1 and not x:
        who = young[0]
    if who not in young:
        raise Refused(f"there is no child called {x!r} here" + (f"; the children here: {', '.join(young)}" if young else ""))
    gift, bits = {"by": here.name}, []                                         # food from one's hands, and a sentence passed on (D4-64)
    item = a.get("item")
    if item:
        if item not in ITEMS or not float(ITEMS[item]["food"]):
            raise Refused(f"{item!r} is not food")
        have = float(here.carried().get(item, 0.0))
        if have <= 1e-9:
            raise Refused(f"you carry no {item}")
        qty = min(have, float(a.get("qty") or have))
        gift.update(item=item, qty=qty)
        bits.append(f"you mean to give {who} {show(qty)} {item} tonight")
    said = " ".join(str(a.get("pass") or "").split())
    if said:
        gift["pass"] = said
        bits.append(f"you passed on to {who}: “{said}”")
    t = here.today()
    t.setdefault("care", {})[who] = t.setdefault("care", {}).get(who, 0) + 1
    t.setdefault("care_by", {}).setdefault(who, [])
    if here.name not in t["care_by"][who]:
        t["care_by"][who].append(here.name)
    here.record("work", "care", who)
    if len(gift) > 1:
        gifts = t.setdefault("care_gift", {}).setdefault(who, [])
        gifts[:] = [g for g in gifts if g["by"] != here.name] + [gift]
    return f"You looked after {who} (fed, minded and kept warm)" + ("; " + "; ".join(bits) if bits else "") + "."


def _tags(here) -> bool:
    return bool(here.setting("tags"))


def _name_thing(here, a):
    """Naming a group of beasts or a thing by its tag (D4-68): the name is known to the namer, everyone here and the household."""
    new = " ".join(str(a.get("as") or "").split())[:40]
    if not new:
        raise Refused('say the name in "as"')
    x = a.get("thing") or a.get("what") or a.get("at")
    tag = here.tag_of(x)
    if not tag or not here.tagged_here(tag):
        raise Refused(f"there is nothing here tagged or called {x!r} that you know of; name a group of beasts or a thing here by its tag")
    who = here.give_name(tag, new)
    here.event("name", f"{here.name} named {tag} {new}", actor=here.name, salience=0.2, sense="sound")
    others = [m for m in who if m != here.name]
    return f"You named {tag} “{new}”" + (f"; {', '.join(others)} will know it by that name." if others else ".")


def _name(here, mind, a, party):
    if a.get("as"):
        return _name_thing(here, a)
    hh = here.household()
    if hh is None:
        raise Refused("you belong to no household")
    members = here.institution(hh)["members"]
    pick = lambda x: next((m for m in members if m.lower() == str(x or "").strip().lower()), None)
    dead = lambda x: (mind.kin().get(x) or {}).get("alive") is False             # dead, as one knows it (D4-95; the engine's
                                                                                # succession counts only the living either way)
    if a.get("heir"):
        if here.head(hh) != here.name:
            raise Refused(f"only the head of {here.institution(hh)['name']} names its heir")
        who = pick(a["heir"])
        if who is None or who == here.name:
            raise Refused(f"{a['heir']!r} is not of your household")
        if dead(who):
            raise Refused(f"{who} is dead: only the living can head a household")
        here.apply("office", inst=hh, field="heir", value=who, by=here.name)
        return f"You named {who} to head {here.institution(hh)['name']} after you."
    if a.get("head"):
        sc = here.life()["succession"]
        if not sc:
            raise Refused("the household has a head; only when a head has died do its members name the next")
        if not _grown(here, here.name) or here.body(here.name)["stage"] == "youth":
            raise Refused("only the grown members name the head")
        who = pick(a["head"])
        if who is None:
            raise Refused(f"{a['head']!r} is not of your household")
        if dead(who):
            raise Refused(f"{who} is dead: only the living can head a household")
        here.apply("office", inst=hh, field="named", value=who, by=here.name)
        return f"You named {who} as the head of {here.institution(hh)['name']}; the one most named heads it."
    raise Refused('say "heir" or "head"' + (', or "thing" and "as" to name a group of beasts or a thing' if _tags(here) else ""))


def _meet(here, mind, a, party):
    """Call a meeting for tomorrow morning at a building or a place here (D4-77)."""
    at = a.get("at") or a.get("to")
    bid = here.building(at)
    pid = None if bid else here.parcel(at)
    if bid is None and pid is None:
        raise Refused(f"say where to meet: a building or a place here, not {at!r}")
    name = here.buildings()[bid]["name"] if bid else here.parcels()[pid]["name"]
    about = " ".join(str(a.get("about") or "").split())[:160]
    here.apply("set", ref=("building", bid) if bid else ("parcel", pid), field="meeting",
               value={"day": here.day + 1, "by": here.name, "about": about, "at": name})
    here.event("meeting", f"{here.name} called a meeting at {name} for tomorrow morning" + (f" about {about}" if about else ""),
               actor=here.name, salience=0.5, sense="sound", tags=["talk"])
    return f"You called a meeting at {name} for tomorrow morning, before the day's work" + (f", about {about}" if about else "") + \
        ": everyone here will hear of it, and whoever comes gives a unit to it."


def _come(here, mind, a, party):
    m = here.meeting_today()
    if m is None:
        raise Refused("no meeting has been called here for this morning")
    return f"You went to the meeting at {m['at']} this morning."


def _order(here, mind, a, party):
    from cybertron2.engine.data import LIFE
    hh = here.household()
    if hh is None or here.head(hh) != here.name:
        raise Refused("only the head of a household sets its children's work")
    what = str(a.get("what") or "").strip().lower()
    if what in ("nothing", "none", "rest", ""):
        here.apply("office", inst=hh, field="order", value=None, by=here.name)
        return "Your household's children do no work now."
    tech = KN.resolve(what, None)
    if tech not in LIFE["children_work"]:
        raise Refused(f"children can do only {', '.join(LIFE['children_work'])}")
    at = a.get("at")
    if at:
        _site(here, mind, tech, at)                                           # a place here it can be done
    here.apply("office", inst=hh, field="order", value={"what": tech, "at": at, "node": here.node}, by=here.name)
    return f"Your household's children will {TECHNIQUES[tech]['label'].split(' (')[0]} each day" + (f" at {at}." if at else ".")


HANDLERS = {"gather": _gather, "work": _work, "make": _make, "build": _build, "move": _move, "take": _take, "give": _give,
            "accept": _accept, "withdraw": _withdraw, "release": _release, "host": _host, "grant": _grant, "revoke": _revoke, "join": _join, "admit": _admit,
            "leave_household": _leave_household, "found": _found, "claim": _claim, "sleep": _sleep, "set": _set, "travel": _travel,
            "watch": _watch, "teach": _teach, "learn": _learn, "attack": _attack, "guard": _guard, "fire": _fire, "rest": _rest,
            "drive": lambda here, mind, a, party: FM.drive(here, a, party), "partner": _partner, "part": _part, "try": _try,
            "name": _name, "order": _order, "meet": _meet, "come": _come, "write": _write, "erase": _erase}
assert set(HANDLERS) == set(VERB)
