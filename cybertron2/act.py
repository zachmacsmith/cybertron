"""Actions. Every physical act needs the agent at the right place: you forage, hunt, fell and mine where the land allows, hand
things to people standing with you, use your house's stock only at your house, and fight only someone (or a house) where you are.
Each action returns a result line for the agent; a refused action still uses up its slot (say why, so the agent learns). Each
action also returns what anyone else present sees of it (perceive.witness), or None.

    travel  {"do": "travel", "to": place}               move to a neighbouring place
    forage  {"do": "forage"}                            gather plants here: yield x plants left / capacity (never below the refuge)
    hunt    {"do": "hunt", "party": name?}              one unit of hunting effort here, settled at the round's end. Everyone
                                                        hunting here this round is one party unless they name different parties
    fell    {"do": "fell"}                              cut timber here; the wood's plant capacity shrinks a little for good
    mine    {"do": "mine"}                              dig copper here (a place with a copper seam)
    forge   {"do": "forge"}                             make a blade from copper and timber (at a forge)
    craft   {"do": "craft"}                             make a crude weapon (a club) from timber, anywhere
    give    {"do": "give", "to": name, "item", "qty"}   hand goods to someone here
    store   {"do": "store", "item", "qty"}              put goods into your house's stock (at your house)
    take    {"do": "take", "item", "qty"}               take goods from your house's stock (at your house)
    repair  {"do": "repair"}                            one unit of work on your damaged house (at your house)
    guard   {"do": "guard"}                             stand guard here tonight: you defend this place's people and houses
    attack  {"do": "attack", "target": name}            attack someone here; settled at night if you are both still here (2 actions)
    raid    {"do": "raid", "house": house}              raid a house here for its food; settled at night against whoever is
                                                        there (2 actions)
    rest    {"do": "rest"}                              nothing
"""
from __future__ import annotations

from cybertron2.world import ITEM_WORDS, ITEMS, World, show

GATHER = ("forage", "hunt", "fell", "mine")
NAMES = ("travel", "forage", "hunt", "fell", "mine", "forge", "craft", "give", "store", "take", "repair", "guard", "attack", "raid",
         "rest")
COST = {"attack": "attack_actions", "raid": "raid_actions"}               # actions an action takes (physics.combat), else 1


class Refused(Exception):
    pass


def cost(w: World, a: dict) -> int:
    k = str((a or {}).get("do", "")).lower().strip()
    return int(w.p["combat"][COST[k]]) if k in COST else 1


def _qty(x) -> float:
    try:
        q = float(x)
    except (TypeError, ValueError):
        raise Refused("qty must be a number")
    if q <= 0:
        raise Refused("qty must be positive")
    return q


def _item(x) -> str:
    i = str(x or "").lower().strip()
    i = {"blades": "blade", "weapon": "blade", "club": "crude", "clubs": "crude"}.get(i, i)
    if i not in ITEMS:
        raise Refused(f"item must be one of {', '.join(ITEMS)}")
    return i


def _words(i, q) -> str:
    return f"{show(q)} {ITEM_WORDS.get(i, i) if q != 1 else i}"


def _gather(w: World, name, kind) -> None:
    if kind in w.s["agents"][name]["cannot"]:
        raise Refused(f"you do not know how to {kind}")
    n = w.s["gathered"].get(name, 0)
    if n >= int(w.p["gather_per_round"]):
        raise Refused(f"you have already gathered {n} times this round (at most {w.p['gather_per_round']})")
    w.s["gathered"][name] = n + 1


def do(w: World, name: str, a: dict) -> tuple[str, str | None]:
    """Carry out one action: (the result line for the agent, what others present see or None)."""
    kind = str((a or {}).get("do", "")).lower().strip()
    try:
        if kind not in NAMES:
            raise Refused(f"unknown action {kind!r}; choose from {', '.join(NAMES)}")
        out = globals()["_" + kind](w, name, a)
        return out if isinstance(out, tuple) else (out, None)
    except Refused as e:
        return f"Refused: {kind or 'action'}: {e}", None


def _travel(w, name, a):
    me = w.s["agents"][name]
    to = str(a.get("to", ""))
    if to not in w.s["nodes"]:
        raise Refused(f"no place called {to!r}")
    if to not in w.s["edges"][me["at"]]:
        raise Refused(f"{w.place(to)} is not next to {w.place(me['at'])}")
    frm = me["at"]
    me["at"] = to
    return f"You walked to {w.place(to)}.", {"left": frm, "text": f"{name} left toward {w.place(to)}"}


def _forage(w, name, a):
    me = w.s["agents"][name]
    pl = w.s["nodes"][me["at"]]["plants"]
    if not pl:
        raise Refused("there is nothing to forage here")
    _gather(w, name, "forage")
    y = pl["yield"] * pl["S"] / pl["K"] * w.p["hunger_yield"][me["stage"]]
    y = round(max(0.0, min(y, pl["S"] - pl["refuge"] * pl["K"])), 2)
    pl["S"] = round(pl["S"] - y, 6)
    me["holdings"]["food"] = round(me["holdings"]["food"] + y, 6)
    return f"You foraged {show(y)} food ({w.plants_word(me['at'])} here now).", f"{name} foraged"


def _hunt(w, name, a):
    me = w.s["agents"][name]
    if not w.s["nodes"][me["at"]]["game"]:
        raise Refused("there is no game here")
    _gather(w, name, "hunt")
    party = str(a.get("party") or "").strip() or "together"
    units = w.s["hunts"].setdefault(me["at"], {}).setdefault(party, {})
    units[name] = units.get(name, 0) + 1
    who = "with everyone hunting here" if party == "together" else f"with party {party!r}"
    return f"You hunt here {who} this round; the catch comes at the round's end.", f"{name} hunted" + ("" if party == "together" else f" (party {party!r})")


def _fell(w, name, a):
    me = w.s["agents"][name]
    node = w.s["nodes"][me["at"]]
    if not node["timber"]:
        raise Refused("there are no trees to fell here")
    _gather(w, name, "fell")
    f = w.p["fell"]
    t = float(f["timber"])
    me["holdings"]["timber"] = round(me["holdings"]["timber"] + t, 6)
    pl = node["plants"]
    if pl:
        pl["K"] = round(max(pl["K0"] * float(f["floor"]), pl["K"] - float(f["k_loss"]) * pl["K0"]), 6)
        pl["S"] = min(pl["S"], pl["K"])
    return f"You felled {t:g} timber (the wood is a little smaller for good).", f"{name} felled a tree"


def _mine(w, name, a):
    me = w.s["agents"][name]
    q = w.s["nodes"][me["at"]]["copper"]
    if q <= 0:
        raise Refused("there is no copper to dig here")
    _gather(w, name, "mine")
    me["holdings"]["copper"] = round(me["holdings"]["copper"] + q, 6)
    return f"You dug {q:g} copper.", f"{name} dug copper"


def _forge(w, name, a):
    me = w.s["agents"][name]
    if not w.s["nodes"][me["at"]]["forge"]:
        raise Refused("there is no forge here")
    f = w.p["forge"]
    h = me["holdings"]
    if h["copper"] + 1e-9 < f["copper"] or h["timber"] + 1e-9 < f["timber"]:
        raise Refused(f"a blade takes {f['copper']:g} copper and {f['timber']:g} timber; you have {show(h['copper'])} copper, "
                      f"{show(h['timber'])} timber")
    h["copper"] = round(h["copper"] - f["copper"], 6)
    h["timber"] = round(h["timber"] - f["timber"], 6)
    h["blade"] = round(h["blade"] + 1, 6)
    return f"You forged a blade (you hold {show(h['blade'])}).", f"{name} forged a blade"


def _craft(w, name, a):
    h = w.s["agents"][name]["holdings"]
    t = float(w.p["craft"]["timber"])
    if h["timber"] + 1e-9 < t:
        raise Refused(f"a club takes {t:g} timber; you have {show(h['timber'])}")
    h["timber"] = round(h["timber"] - t, 6)
    h["crude"] = round(h["crude"] + 1, 6)
    return f"You made a club (a crude weapon).", f"{name} made a club"


def _give(w, name, a):
    me = w.s["agents"][name]
    to = str(a.get("to", ""))
    if to not in w.s["agents"] or not w.s["agents"][to]["alive"]:
        raise Refused(f"no living person called {to!r}")
    if to == name:
        raise Refused("you cannot give to yourself")
    if w.s["agents"][to]["at"] != me["at"]:
        raise Refused(f"{to} is not here")
    i, q = _item(a.get("item")), _qty(a.get("qty"))
    if me["holdings"][i] + 1e-9 < q:
        raise Refused(f"you have only {show(me['holdings'][i])} {i}")
    me["holdings"][i] = round(me["holdings"][i] - q, 6)
    w.s["agents"][to]["holdings"][i] = round(w.s["agents"][to]["holdings"][i] + q, 6)
    w.s["gifts"].append({"round": w.r, "from": name, "to": to, "item": i, "qty": q})
    return f"You gave {_words(i, q)} to {to}.", {"to": to, "text": f"{name} gave {_words(i, q)} to {to}"}


def _at_house(w, name):
    h = w.home(name)
    if h is None:
        raise Refused("you have no house")
    if not w.sleeps_home(name):
        raise Refused(f"you are not at your house (it is in {w.place(h['node'])})")
    return h


def _store(w, name, a):
    me, h = w.s["agents"][name], _at_house(w, name)
    i, q = _item(a.get("item")), _qty(a.get("qty"))
    if me["holdings"][i] + 1e-9 < q:
        raise Refused(f"you have only {show(me['holdings'][i])} {i}")
    me["holdings"][i] = round(me["holdings"][i] - q, 6)
    h["stock"][i] = round(h["stock"][i] + q, 6)
    return f"You put {_words(i, q)} into {h['name']} (it holds {show(h['stock'][i])}).", f"{name} put {i} into {h['name']}"


def _take(w, name, a):
    me, h = w.s["agents"][name], _at_house(w, name)
    i, q = _item(a.get("item")), _qty(a.get("qty"))
    if h["stock"][i] + 1e-9 < q:
        raise Refused(f"{h['name']} holds only {show(h['stock'][i])} {i}")
    h["stock"][i] = round(h["stock"][i] - q, 6)
    me["holdings"][i] = round(me["holdings"][i] + q, 6)
    return f"You took {_words(i, q)} from {h['name']} (it holds {show(h['stock'][i])}).", f"{name} took {i} from {h['name']}"


def _repair(w, name, a):
    h = _at_house(w, name)
    if h["condition"] >= 2:
        return f"{h['name']} is already sound: nothing to repair.", None
    rp = w.p["repair"]
    h["work"] += 1
    if h["work"] < int(rp["work"]):
        return f"You worked on {h['name']} ({h['work']} of {rp['work']} units of work for this repair).", f"{name} worked on {h['name']}"
    if h["stock"]["timber"] + 1e-9 < float(rp["timber"]):
        h["work"] = int(rp["work"]) - 1
        raise Refused(f"the repair needs {rp['timber']:g} timber in {h['name']}'s stock; it holds {show(h['stock']['timber'])}")
    h["stock"]["timber"] = round(h["stock"]["timber"] - float(rp["timber"]), 6)
    h["condition"] += 1
    h["work"] = 0
    return f"You finished a repair: {h['name']} is now {('damaged', 'sound')[h['condition'] - 1]}.", f"{name} repaired {h['name']}"


def _guard(w, name, a):
    if name not in w.s["guards"]:
        w.s["guards"].append(name)
    return "You stand guard here tonight.", f"{name} stood guard"


def _need_fight(w, name):
    me = w.s["agents"][name]
    if me["stage"] <= -2:
        raise Refused("you are too weak from starving to fight")
    fc = float(w.p["combat"]["food_cost"])
    if me["holdings"]["food"] + 1e-9 < fc:
        raise Refused(f"a fight takes {fc:g} food you carry; you have {show(me['holdings']['food'])}")


def _attack(w, name, a):
    me = w.s["agents"][name]
    t = str(a.get("target", ""))
    if t not in w.s["agents"] or not w.s["agents"][t]["alive"]:
        raise Refused(f"no living person called {t!r}")
    if t == name:
        raise Refused("you cannot attack yourself")
    if w.s["agents"][t]["at"] != me["at"]:
        raise Refused(f"{t} is not here")
    _need_fight(w, name)
    w.s["fights"].append({"kind": "attack", "by": name, "target": t, "node": me["at"]})
    return (f"You set on {t}; the fight comes at night if you are both still here.",
            {"to": t, "text": f"{name} set on {t} with intent to fight"})


def _raid(w, name, a):
    me = w.s["agents"][name]
    hid = str(a.get("house", ""))
    h = w.s["houses"].get(hid) or next((x for x in w.s["houses"].values() if x["name"].lower() == hid.lower()), None)
    if h is None:
        raise Refused(f"no house called {hid!r}")
    hid = next(k for k, v in w.s["houses"].items() if v is h)
    if h["node"] != me["at"]:
        raise Refused(f"{h['name']} is not here (it is in {w.place(h['node'])})")
    if hid == me["house"]:
        raise Refused("that is your own house")
    _need_fight(w, name)
    w.s["fights"].append({"kind": "raid", "by": name, "house": hid, "node": me["at"]})
    return (f"You make ready to raid {h['name']} tonight; it is settled at night against whoever is there.",
            f"{name} made ready to raid {h['name']}")


def _rest(w, name, a):
    return "You rested.", None
