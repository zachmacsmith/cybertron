"""The verbs (spec/agents/actions.md, proposals/verbs.md): each is a composition of primitives at the agent's node, reading only
`Here` and `Mind` (D4-35). Techniques, recipes, blueprints and fittings are data (D4-24): one handler for gathering and work, one
for making, one for building.

Each handler: (here, mind, a) -> result line. Refusals name what is short and cost nothing.
"""
from __future__ import annotations

from cybertron2.engine import farm as FM, knowledge as KN
from cybertron2.engine.data import BLUEPRINTS, COVERS, FITTINGS, ITEMS, TECHNIQUES, TRY
from cybertron2.engine.here import Refused, show

# The registry (cybertron 1's action_registry): arguments, cost (units, a physics path, or "craft"), the line in the manual, and
# `when` (only in a world with roads). The prompt's verb list and the reply schema are generated from it.
VERB = {
    "gather": {"args": '{"what", "at"?: place, "for"?: party}', "cost": "craft", "doc": "take from the land: {crafts}"},
    "work": {"args": '{"what", "at"?: place or building, "item"?: the seed to sow (grain, rye, beans: always say which), or the beast to slaughter (cow, ox, bull, calf), "for"?: party}',
             "cost": "craft", "doc": "{crafts}"},
    "make": {"args": '{"what", "qty"?: times, "for"?: party}', "cost": "craft",
             "doc": "a recipe; the inputs come from what you carry, then from stores here you may take from: {crafts}"},
    "build": {"args": '{"what", "at": a place on built ground or scrub (a new building) or a building here (a fitting), "qty"?: beds, "name"?, "for"?: party}',
              "cost": 2, "doc": "start or carry on a building or a fitting: its materials when you start, then the work over days: {crafts}"},
    "move": {"args": '{"item", "qty", "to": store | hands, "at"?: building}', "cost": 0,
             "doc": "between your hands and a store here you may use (your household's)"},
    "take": {"args": '{"item", "qty", "from": building or someone\'s remains}', "cost": 1,
             "doc": "from any store you can get into; without the right to it, it is theft, and you may be seen"},
    "give": {"args": '{"to": a person or a household here, "item", "qty", "for"?: your household, to give from its store}', "cost": 0,
             "doc": "to anyone here; to a household, it goes into their house's store"},
    "leave": {"args": '{"item", "qty", "at": a building here}', "cost": 0,
              "doc": "put something you carry into a building's store here, for its household (they find it in the morning)"},
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
    "claim": {"args": '{"thing": a field, building or herd here, "for"?: your household}', "cost": 0,
              "doc": "claim it as yours: others will know, and may agree or dispute it"},
    "drive": {"args": '{"thing": a herd here, "item"?: cows | oxen | bulls | calves | all, "qty"?, "to": a place here}', "cost": 1,
              "when": "herds", "doc": "move beasts to another place here (a bull kept apart from the cows does not breed)"},
    "sleep": {"args": '{"at": building}', "cost": 0, "doc": "sleep there tonight, if you can get in and a bed is free"},
    "set": {"args": '{"thing": door, "to": open | barred, "at"?: building}', "cost": 0, "doc": "the door of a building you manage"},
    "travel": {"args": '{"to": a place}', "cost": 0, "when": "roads", "doc": "the day's last act: you leave at nightfall and arrive on a later morning"},
    "watch": {"args": '{"person"}', "cost": ["watch", "units"], "doc": "spend the day working beside them: you see how they do things"},
    "teach": {"args": '{"to", "what"}', "cost": ["teach", "units_teacher"], "doc": "one session, if they set aside time to learn the same day"},
    "learn": {"args": '{"from", "what"}', "cost": ["teach", "units_learner"], "doc": "one session, if they set aside time to teach the same day"},
    "attack": {"args": '{"target": person or building, "aim": rob | hurt}', "cost": ["combat", "units"], "doc": "settled tonight"},
    "guard": {"args": '{"at"?: building}', "cost": 1, "doc": "stand guard tonight over a building here and anyone set upon"},
    "rest": {"args": "", "cost": 0, "doc": ""},
}
VERBS = tuple(VERB)
FM_KINDS = ("sow", "break", "tend", "manure", "crop", "herd", "milk", "slaughter", "works", "select")
FREE = tuple(v for v, d in VERB.items() if d["cost"] == 0)


def verb_here(here, verb) -> bool:
    when = VERB[verb].get("when")
    return not when or (when == "roads" and bool(here.roads())) or (when == "herds" and any(FM.head(h) > 0 for h in here.herds().values()))


def verb_units(p, verb):
    c = VERB[verb]["cost"]
    if c == "craft":
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
    tech = KN.resolve(a.get("what"), a.get("do"))
    if tech is None:
        return 1
    n = int(TECHNIQUES[tech]["units"])
    if v == "make":
        n *= max(1, int(_qty(a.get("qty"), 1)))
    return n


def do(here, mind, a) -> str:
    v = str((a or {}).get("do", "")).lower().strip()
    try:
        if v not in VERBS:
            raise Refused(f"unknown verb {v!r}; the verbs are {', '.join(VERBS)}")
        if not verb_here(here, v):
            raise Refused(f"there is no {v} in this world")
        party = _party(here, a.get("for")) if a.get("for") and v in ("gather", "work", "make", "build", "give", "accept", "claim") else None
        with here.cause(v, party):
            return HANDLERS[v](here, mind, a, party)
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
        raise Refused(f"{party} has nothing here to put it into")
    if cid != here.hands and not here.may_take(cid) and cid.startswith("stock:") and not here.works_for(party):
        raise Refused(f"you may not use {party}'s store (you are not of that household): do it for yourself, then give it to one of "
                      f"them or leave it at their house")
    return cid


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
            raise Refused(f"it needs {q * mult:g} {item}; you have {show(have)} to hand")
    for item, q in needs.items():
        left = round(q * mult, 6)
        for cid in order:
            if left <= 1e-9:
                break
            have = here.carried().get(item, 0.0) if cid == here.hands else here.stock(cid[len("stock:"):]).get(item, 0.0)
            take = min(have, left)
            if take > 1e-9:
                here.apply("destroy", src=cid, item=item, qty=take, why="used")
                left -= take
        if left > 1e-6:
            raise Refused(f"it needs {q * mult:g} {item}")


def _skill_mult(here, mind, tech) -> float:
    return KN.skill(mind, tech) * here.yield_mult()                           # skill by practice (D2-52), and hunger


def _site(here, mind, tech, at):
    sites = KN.where(here, tech)
    if at:
        key = here.parcel(at) or here.building(at)
        if key is None:
            raise Refused(f"there is no place called {at!r} here")
        sites = [s for s in sites if s[1] == key]
        if not sites:
            raise Refused(f"{KN.label(tech)} is not done at {at}")
    ok = [s for s in sites if not KN.ready(here, tech, s[0], s[1])]
    if not ok:
        raise Refused(KN.ready(here, tech, sites[0][0], sites[0][1]) if sites else f"there is nowhere here for {KN.label(tech)}")
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
    return _technique(here, mind, a, party, "work")


def _technique(here, mind, a, party, verb):
    tech = KN.resolve(a.get("what"), verb)
    if tech is None or TECHNIQUES[tech]["verb"] != verb:
        names = [t for t, d in TECHNIQUES.items() if d["verb"] == verb]
        raise Refused(f"{a.get('what')!r} is not something you {verb} ({verb}: {', '.join(names)})")
    t = TECHNIQUES[tech]
    if not t.get("crew"):                                                     # crew work: anyone may dig, led by one who knows how
        _level(mind, tech)
    kind, key, place_name = _site(here, mind, tech, a.get("at"))
    why = KN.shortfall(here, mind, tech, 1.0, key)
    if why:
        raise Refused(why)
    out = _out(here, party)
    y = t["yield"]
    m = _skill_mult(here, mind, tech)
    tool, tm = here.best_tool(t["tools"]) if t.get("tools") else (None, 1.0)
    rng = here.rng("act", here.day, here.name, len(here.today()["worked"].get(here.name, [])))
    here.today()["worked"].setdefault(here.name, []).append(key)
    thing = (kind, key)
    note = _against(here, thing) if kind == "parcel" else ""
    got, gives, word, extra_got, suffix = 0.0, t.get("gives"), "", "", ""
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
        if armed and t.get("wear"):
            here.apply("wear", container=here.hands, item=armed, uses=t["wear"])
    elif y["kind"] == "fixed":
        q = y["base"] * m * tm
        got = here.apply("draw", parcel=key, key=t["draws"], qty=round(q, 2)) if t["draws"] in here.parcels()[key]["res"] and \
            here.parcels()[key]["res"][t["draws"]]["K"] > 0 and t["draws"] != "quarry" else round(q, 2)
    elif y["kind"] in FM_KINDS:                                                 # farming and cattle (farm.py)
        got, g, word, thing = FM.act(here, mind, tech, key, place_name, out, m, tm, a)
        gives = g or gives
        note = _against(here, thing) if thing[0] in ("parcel", "herd") else note
        if word and not word.startswith("You"):
            suffix, word = word, ""                                             # a note to the plain result, below
    elif y["kind"] == "repair":
        b = here.buildings()[key]
        _consume(here, t.get("inputs") or {}, extra=b["stock"] if here.may_take(b["stock"]) else None)
        here.apply("set", ref=("building", key), field="condition", value=b["condition"] + 1)
        word = f"You repaired {b['name']}: it is now {('ruined', 'damaged', 'sound')[b['condition']]}."
        thing = ("building", key)
    if got > 0 and gives:
        here.apply("create", dst=out, item=gives, qty=got, why=tech)
    if tool and t.get("wear"):
        here.apply("wear", container=here.hands, item=tool, uses=t["wear"])
    KN.tried(here, mind, tech, got > 0 or y["kind"] in ("sow", "tend", "repair", "slaughter", "break", "manure", "herd"), units=t["units"])
    for_txt = f" for {here.households()[party]['name'] if party in here.households() else party}" if party and party != here.name else ""
    text = f"{here.name} was {KN.label(tech)} at {place_name}{for_txt}{note}"
    here.event("work", text, actor=here.name, about=[f"{thing[0]}:{thing[1]}"], salience=0.35 if note else 0.15, tags=t["tags"],
               tech=tech, concerns=_holders_people(here, thing) if note else [])
    here.record(verb, tech, party, site=key)
    if word:
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
    extra = out if out != here.hands else None
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
            for item, q in t["gives"].items():
                here.apply("create", dst=out, item=item, qty=q, why=tech)
            res.append(f"You made {', '.join(f'{q:g} {it}' for it, q in t['gives'].items())}" + (f" at {site[2]}" if site[1] else "") + "."
                       + (f" (You are now {rose} at it.)" if rose else ""))
        else:
            res.append(f"Your try at {KN.label(tech)} failed and the materials are spoilt." + (f" (You are now {rose} at it.)" if rose else ""))
        here.event("make", f"{here.name} was {KN.label(tech)}" + ("" if ok else ", and it went wrong"), actor=here.name,
                   about=[f"building:{site[1]}"] if site[0] == "building" else [], salience=0.2, tags=t["tags"], tech=tech)
        here.record("make", tech, party)
    return " ".join(res)


# ---------------------------------------------------------------------- building (D2-9, recipes.md §3)
def _build(here, mind, a, party):
    what = str(a.get("what") or "").strip().lower()
    if what not in BLUEPRINTS and what not in FITTINGS:
        raise Refused(f"{a.get('what')!r} is not something you build (buildings: {', '.join(BLUEPRINTS)}; fittings: {', '.join(FITTINGS)})")
    lvl = _level(mind, what)
    owner = party or here.name
    at = a.get("at")
    if what in BLUEPRINTS:
        bp = BLUEPRINTS[what]
        bid = here.building(at) if at else None
        if bid and here.buildings()[bid].get("unfinished"):                      # carry on
            return _build_work(here, mind, bid, lvl)
        pid = here.parcel(at) if at else None
        if pid is None:
            lots = [p for p, x in here.parcels().items() if COVERS[x["cover"]]["lots"] > 0]
            raise Refused(f"say where to build: a place on built ground or scrub here ({', '.join(here.parcels()[p]['name'] for p in lots) or 'none'})")
        par = here.parcels()[pid]
        used = sum(1 for b in here.buildings().values() if b["parcel"] == pid)
        if bp.get("structure") == "camp":                                        # a camp goes up anywhere but on water (D2-68)
            if par["cover"] == "water":
                raise Refused("you cannot camp on water")
        elif used >= COVERS[par["cover"]]["lots"] * par["size"]:
            raise Refused(f"there is no room left to build on {par['name']}")
        _consume(here, bp["materials"], TRY[lvl]["inputs"], here.party_container(party) if party else None)
        who = here.households()[party]['name'] if party in here.households() else here.name
        name = str(a.get("name") or "").strip()[:40] or (f"{who}'s camp on {par['name']}" if bp.get("structure") == "camp" else f"{who}'s new house")
        bid = here.apply("raise", node=here.node, parcel=pid, rec={"name": name, "structure": bp["structure"], "size": bp["size"],
                                                                     "fittings": {}, "unfinished": {"blueprint": what, "units_left": bp["units"]}})
        here.apply("claim", thing=("building", bid), claimant=owner, rights="all", grounds="built")
        here.event("build", f"{here.name} began building {bp['label']} on {par['name']}", actor=here.name, about=[f"building:{bid}"],
                   salience=0.5, tags=["building"])
        return _build_work(here, mind, bid, lvl, started=True)
    # a fitting in a building here
    f = FITTINGS[what]
    bid = here.building(at) if at else (here.homes_here() or [None])[0]
    if bid is None:
        raise Refused("say which building here to put it in")
    b = here.buildings()[bid]
    if b.get("unfinished"):
        raise Refused(f"{b['name']} is not finished")
    if not here.can_enter(bid):
        raise Refused(f"you cannot get into {b['name']}")
    if f.get("needs") and not b["fittings"].get(f["needs"]):
        raise Refused(f"{f['label']} needs {FITTINGS[f['needs']]['label']} first")
    if f.get("site") and not any(here.parcels()[x]["cover"] == f["site"] for x in [b["parcel"]] + here.parcels()[b["parcel"]]["adj"]):
        raise Refused(f"{f['label']} needs a building by {f['site']}")
    n = max(1, int(_qty(a.get("qty"), 1))) if f.get("per") else 1
    if f.get("per"):
        n = min(n, max(0, b["size"] - int(b["fittings"].get(what, 0))))
        if n <= 0:
            raise Refused(f"{b['name']} has as many {f['label']} as it holds people ({b['size']})")
    elif b["fittings"].get(what):
        raise Refused(f"{b['name']} already has {f['label']}")
    _consume(here, f["materials"], TRY[lvl]["inputs"] * n, b["stock"] if here.may_take(b["stock"]) else None)
    ok = here.rng("build", here.day, here.name, what).random() < TRY[lvl]["chance"]
    KN.tried(here, mind, what, ok)
    if not ok:
        return f"Your try at {f['label']} went wrong; the materials are spoilt."
    fit = dict(b["fittings"])
    fit[what] = int(fit.get(what, 0)) + n
    here.apply("set", ref=("building", bid), field="fittings", value=fit)
    here.event("build", f"{here.name} put {n if f.get('per') else ''} {f['label']} into {b['name']}".replace("  ", " "), actor=here.name,
               about=[f"building:{bid}"], salience=0.3, tags=["building"])
    here.record("build", what, party)
    return f"You put {str(n) + ' ' if f.get('per') else ''}{f['label']} into {b['name']}."


def _build_work(here, mind, bid, lvl, started=False):
    b = here.buildings()[bid]
    u = dict(b["unfinished"])
    done = round(2 * KN.skill(mind, u["blueprint"]) * here.yield_mult(), 2)
    u["units_left"] = round(max(0.0, u["units_left"] - done), 2)
    here.record("build", u["blueprint"], None)
    if u["units_left"] <= 1e-9:
        bp = BLUEPRINTS[u["blueprint"]]
        here.apply("set", ref=("building", bid), field="unfinished", value=None)
        if bp.get("fittings"):                                                 # a blueprint that comes fitted (a camp: D2-68)
            here.apply("set", ref=("building", bid), field="fittings", value=dict(bp["fittings"]))
        if bp.get("lasts"):
            here.apply("set", ref=("building", bid), field="lasts_until", value=here.day + int(bp["lasts"]))
        here.event("build", f"{here.name} finished {b['name']}", actor=here.name, about=[f"building:{bid}"], salience=0.6, tags=["building", "shelter"])
        KN.tried(here, mind, u["blueprint"], True)
        if bp.get("fittings"):
            return f"You made {b['name']}: shelter for {bp['size']} with a fire, for about {bp['lasts']} nights."
        return f"You finished {b['name']}. It has no fittings yet: beds, a hearth and bins make it a house."
    here.apply("set", ref=("building", bid), field="unfinished", value=u)
    return ("You began " if started else "You worked on ") + f"{b['name']}: about {show(u['units_left'])} units of work left."


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
    if have <= 1e-9:
        raise Refused(f"there is no {item} " + ("in your hands" if verb == "put" else f"in {b['name']}"))
    q = round(min(_qty(a.get("qty"), have), have), 6)
    here.apply("transfer", src=src, dst=dst, item=item, qty=q)
    here.event("store", f"{here.name} {verb} {item} {'into' if verb == 'put' else 'from'} {b['name']}", actor=here.name,
               about=[f"building:{bid}"], salience=0.1, tags=["food"] if ITEMS[item]["food"] else [])
    return f"You {verb} {show(q)} {item} {'into' if verb == 'put' else 'from'} {b['name']} (it holds {show(here.stock(bid).get(item, 0.0))})."


def _take(here, mind, a, party):
    item = item_of(a.get("item"))
    src_name = str(a.get("from") or "")
    rem = next((cid for cid, c in here.remains().items() if c["of"].lower() in src_name.lower()), None)
    if rem:
        src, label, theft = rem, f"what {here.remains()[rem]['of']} left", False
        have = here.remains()[rem]["goods"].get(item, 0.0)
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
        raise Refused(f"you find no {item} in {label}")
    here.apply("transfer", src=src, dst=here.hands, item=item, qty=q)
    if theft:
        here.today()["thefts"].append({"by": here.name, "building": bid, "item": item, "qty": round(q, 2)})
        here.record("take", None, None, theft=True)
        return f"You took {show(q)} {item} from {label}, which is not yours to take from. Whether anyone saw, you will learn."
    here.event("take", f"{here.name} took {item} from {label}", actor=here.name, salience=0.3, tags=["food"] if ITEMS[item]["food"] else [])
    return f"You took {show(q)} {item} from {label}."


def _give(here, mind, a, party):
    to = here.person(a.get("to"))
    if to is None:                                                          # to a household: into its house's store here
        try:
            hh = _party(here, a.get("to"))
        except Refused:
            hh = None
        house = here.party_container(hh) if hh in here.households() else None
        if house and house.startswith("stock:"):
            item, q = item_of(a.get("item")), _qty(a.get("qty"))
            if here.carried().get(item, 0.0) + 1e-9 < q:
                raise Refused(f"you carry only {show(here.carried().get(item, 0.0))} {item}")
            bid = house[len("stock:"):]
            here.apply("transfer", src=here.hands, dst=house, item=item, qty=q)
            name = here.households()[hh]["name"]
            here.event("give", f"{here.name} gave {q:g} {item} to {name}, into {here.buildings()[bid]['name']}", actor=here.name,
                       about=[f"building:{bid}"], salience=0.35, tags=["food"] if ITEMS[item]["food"] else [],
                       concerns=list(here.institution(hh)["members"]))
            here.record("give", None, party, to=hh, item=item, qty=q)
            return f"You gave {q:g} {item} to {name}: it is in {here.buildings()[bid]['name']}."
    if to is None or to == here.name:
        raise Refused(f"there is nobody called {a.get('to')!r} here")
    item, q = item_of(a.get("item")), _qty(a.get("qty"))
    if party and party != here.name and party != here.household() and not here.works_for(party):
        raise Refused(f"'for' gives from that household's store, which is not yours: to give to {party}, give with 'to' instead")
    src = here.hands if not party or party == here.name else _out(here, party)
    have = here.carried().get(item, 0.0) if src == here.hands else here.stock(src[len("stock:"):]).get(item, 0.0)
    if have + 1e-9 < q:
        raise Refused(f"there is only {show(have)} {item} to give")
    here.apply("transfer", src=src, dst=here.hands_of(to), item=item, qty=q)
    here.event("give", f"{here.name} gave {q:g} {item} to {to}", actor=here.name, target=to, about=[f"person:{to}"], salience=0.35,
               tags=["food"] if ITEMS[item]["food"] else [], concerns=[to])
    here.record("give", None, party, to=to, item=item, qty=q)
    return f"You gave {q:g} {item} to {to}."


def _leave(here, mind, a, party):
    bid = here.building(a.get("at"))
    if bid is None:
        raise Refused(f"there is no building called {a.get('at')!r} here; the buildings here: " + ", ".join(b["name"] for b in here.buildings().values()))
    b = here.buildings()[bid]
    if not here.can_enter(bid):
        raise Refused(f"{b['name']}'s door is barred")
    item, q = item_of(a.get("item")), _qty(a.get("qty"))
    if here.carried().get(item, 0.0) + 1e-9 < q:
        raise Refused(f"you carry only {show(here.carried().get(item, 0.0))} {item}")
    here.apply("transfer", src=here.hands, dst=b["stock"], item=item, qty=q)
    here.today()["left"].append({"by": here.name, "item": item, "qty": q, "building": bid})
    return f"You left {q:g} {item} at {b['name']}."


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
    if "management" not in here.rights(("building", bid)):
        raise Refused(f"you do not manage {here.buildings()[bid]['name']}")
    to = str(a.get("to") or "").lower()
    if to not in ("open", "barred"):
        raise Refused('set {"thing": "door", "to": "open" or "barred"}')
    here.apply("set", ref=("building", bid), field="door", value=to)
    return f"{here.buildings()[bid]['name']}'s door is now {to}."


# ---------------------------------------------------------------------- travel (D4-8, D4-32)
def _travel(here, mind, a, party):
    r = here.road_to(a.get("to"))
    if r is None:
        ways = ", ".join(f"{n} ({k} day{'s' if k > 1 else ''})" for _, n, k, _t in here.roads())
        raise Refused(f"there is no way from here to {a.get('to')!r}; from here you can go to {ways or 'nowhere'}")
    to, days, track = r
    load, cap = here.load(), here.capacity(track)
    if load > cap + 1e-9:
        cart = any(ITEMS[i].get("track") for i, q in here.carried().items() if q >= 1)
        raise Refused(f"you carry {show(load)} weight; you can carry {cap:g} on this road"
                      + (" (a cart needs a road with a track, and this one has none)" if cart and not track else ""))
    here.today()["travel"][here.name] = to
    here.event("depart", f"{here.name} set off on the road", actor=here.name, salience=0.6, tags=["travel"])
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
    return "You stand guard tonight" + (f" over {here.buildings()[bid]['name']}." if bid else ".")


def _rest(here, mind, a, party):
    return "You rested."


def _accept(here, mind, a, party):
    from cybertron2.engine import agreements as AG
    return AG.accept(here, mind, a, party)


def _release(here, mind, a, party):
    from cybertron2.engine import agreements as AG
    return AG.release(here, mind, a)


def _withdraw(here, mind, a, party):
    from cybertron2.engine import agreements as AG
    return AG.withdraw(here, a)


HANDLERS = {"gather": _gather, "work": _work, "make": _make, "build": _build, "move": _move, "take": _take, "give": _give, "leave": _leave,
            "accept": _accept, "withdraw": _withdraw, "release": _release, "host": _host, "grant": _grant, "revoke": _revoke, "join": _join, "admit": _admit,
            "leave_household": _leave_household, "found": _found, "claim": _claim, "sleep": _sleep, "set": _set, "travel": _travel,
            "watch": _watch, "teach": _teach, "learn": _learn, "attack": _attack, "guard": _guard, "rest": _rest,
            "drive": lambda here, mind, a, party: FM.drive(here, a, party)}
assert set(HANDLERS) == set(VERB)
