"""Actions. Every physical act needs the agent at the right place: you forage, hunt and fell where the forest is, hand things to
people standing with you, and use your house's stock only at your house. Each action returns a result line for the agent; a
refused action still uses up its slot (say why, so the agent learns).

    travel  {"do": "travel", "to": node}                 move to a neighbouring place
    forage  {"do": "forage"}                             gather plants here: yield x plants left / capacity (never below the refuge)
    hunt    {"do": "hunt", "party": "name"?}             one unit of hunting effort here, settled at the round's end; everyone here
                                                         who names the same party hunts with you
    fell    {"do": "fell"}                               cut timber here; the wood's plant capacity shrinks a little for good
    give    {"do": "give", "to": name, "item", "qty"}    hand food or timber to someone here
    store   {"do": "store", "item", "qty"}               put food or timber into your house's stock (at your house)
    take    {"do": "take", "item", "qty"}                take food or timber from your house's stock (at your house)
    repair  {"do": "repair"}                             one unit of work on your damaged house (at your house; needs the timber in
                                                         its stock when the work completes)
    rest    {"do": "rest"}                               nothing
"""
from __future__ import annotations

from cybertron2.world import ITEMS, World, show

GATHER = ("forage", "hunt", "fell")
NAMES = ("travel", "forage", "hunt", "fell", "give", "store", "take", "repair", "rest")


class Refused(Exception):
    pass


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
    if i not in ITEMS:
        raise Refused(f"item must be one of {', '.join(ITEMS)}")
    return i


def _gather(w: World, name) -> None:
    n = w.s["gathered"].get(name, 0)
    if n >= int(w.p["gather_per_round"]):
        raise Refused(f"you have already gathered {n} times this round (at most {w.p['gather_per_round']})")
    w.s["gathered"][name] = n + 1


def do(w: World, name: str, a: dict) -> str:
    """Carry out one action; returns the result line (a refusal starts with "Refused:")."""
    kind = str((a or {}).get("do", "")).lower().strip()
    try:
        if kind not in NAMES:
            raise Refused(f"unknown action {kind!r}; choose from {', '.join(NAMES)}")
        return globals()["_" + kind](w, name, a)
    except Refused as e:
        return f"Refused: {kind or 'action'}: {e}"


def _travel(w, name, a):
    me = w.s["agents"][name]
    to = str(a.get("to", ""))
    if to not in w.s["nodes"]:
        raise Refused(f"no place called {to!r}")
    if to not in w.s["edges"][me["at"]]:
        raise Refused(f"{w.s['nodes'][to]['name']} is not next to {w.s['nodes'][me['at']]['name']}")
    me["at"] = to
    return f"You walked to {w.s['nodes'][to]['name']}."


def _forage(w, name, a):
    me = w.s["agents"][name]
    pl = w.s["nodes"][me["at"]]["plants"]
    if not pl:
        raise Refused("there is nothing to forage here")
    _gather(w, name)
    y = pl["yield"] * pl["S"] / pl["K"] * w.p["hunger_yield"][me["stage"]]
    y = round(max(0.0, min(y, pl["S"] - pl["refuge"] * pl["K"])), 2)
    pl["S"] = round(pl["S"] - y, 6)
    me["holdings"]["food"] = round(me["holdings"]["food"] + y, 6)
    return f"You foraged {show(y)} food ({w.plants_word(me['at'])} here now)."


def _hunt(w, name, a):
    me = w.s["agents"][name]
    if not w.s["nodes"][me["at"]]["game"]:
        raise Refused("there is no game here")
    _gather(w, name)
    party = str(a.get("party") or name)
    units = w.s["hunts"].setdefault(me["at"], {}).setdefault(party, {})
    units[name] = units.get(name, 0) + 1
    return f"You hunt here with party {party!r} this round; the catch comes at the round's end."


def _fell(w, name, a):
    me = w.s["agents"][name]
    node = w.s["nodes"][me["at"]]
    if not node["timber"]:
        raise Refused("there are no trees to fell here")
    _gather(w, name)
    f = w.p["fell"]
    t = float(f["timber"])
    me["holdings"]["timber"] = round(me["holdings"]["timber"] + t, 6)
    pl = node["plants"]
    if pl:
        pl["K"] = round(max(pl["K0"] * float(f["floor"]), pl["K"] - float(f["k_loss"]) * pl["K0"]), 6)
        pl["S"] = min(pl["S"], pl["K"])
    return f"You felled {t:g} timber (the wood is a little smaller for good)."


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
    w.s.setdefault("gifts", []).append({"round": w.r, "from": name, "to": to, "item": i, "qty": q})
    return f"You gave {q:g} {i} to {to}."


def _at_house(w, name):
    h = w.home(name)
    if h is None:
        raise Refused("you have no house")
    if not w.sleeps_home(name):
        raise Refused(f"you are not at your house (it is in {w.s['nodes'][h['node']]['name']})")
    return h


def _store(w, name, a):
    me, h = w.s["agents"][name], _at_house(w, name)
    i, q = _item(a.get("item")), _qty(a.get("qty"))
    if me["holdings"][i] + 1e-9 < q:
        raise Refused(f"you have only {show(me['holdings'][i])} {i}")
    me["holdings"][i] = round(me["holdings"][i] - q, 6)
    h["stock"][i] = round(h["stock"][i] + q, 6)
    return f"You put {q:g} {i} into {h['name']} (it holds {show(h['stock'][i])})."


def _take(w, name, a):
    me, h = w.s["agents"][name], _at_house(w, name)
    i, q = _item(a.get("item")), _qty(a.get("qty"))
    if h["stock"][i] + 1e-9 < q:
        raise Refused(f"{h['name']} holds only {show(h['stock'][i])} {i}")
    h["stock"][i] = round(h["stock"][i] - q, 6)
    me["holdings"][i] = round(me["holdings"][i] + q, 6)
    return f"You took {q:g} {i} from {h['name']} (it holds {show(h['stock'][i])})."


def _repair(w, name, a):
    h = _at_house(w, name)
    if h["condition"] >= 2:
        raise Refused(f"{h['name']} is sound")
    rp = w.p["repair"]
    h["work"] += 1
    if h["work"] < int(rp["work"]):
        return f"You worked on {h['name']} ({h['work']} of {rp['work']} units of work for this repair)."
    if h["stock"]["timber"] + 1e-9 < float(rp["timber"]):
        h["work"] = int(rp["work"]) - 1
        raise Refused(f"the repair needs {rp['timber']:g} timber in {h['name']}'s stock; it holds {show(h['stock']['timber'])}")
    h["stock"]["timber"] = round(h["stock"]["timber"] - float(rp["timber"]), 6)
    h["condition"] += 1
    h["work"] = 0
    return f"You finished a repair: {h['name']} is now {('damaged', 'sound')[h['condition'] - 1]}."


def _rest(w, name, a):
    return "You rested."
