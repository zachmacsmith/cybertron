"""Modifiers: ways of doing an act (agents/modifiers.md; D2-93, D2-94, D2-111, D2-112).

A modifier is a technique (data.TECHNIQUES with `modifies`) written on an action as `key: value` ("hidden": "under brush", "method":
"dibble", "for": a party). `resolve` finds the modifiers an action uses, checks the agent may use each (known, or tryable untaught),
and returns their merged `changes` for the verb to read. The verb decides what a change means (`hidden`, `yield`, `inputs`, `units`,
`word`); a new modifier is a data row, and a verb that should honour a new kind of change reads one more key.
"""
from __future__ import annotations

from cybertron2.engine import knowledge as KN
from cybertron2.engine.data import MODIFIERS, TECHNIQUES
from cybertron2.engine.world import Refused


def _targets(verb, tech=None, place=False) -> set:
    out = {verb}
    if tech:
        out.add(f"{verb}:{tech}")
    if place:
        out.add(f"{verb}:place")
    return out


def available(verb, tech=None, place=False) -> list:
    """The modifiers that can attach to a verb (and technique, or a give to a place)."""
    tg = _targets(verb, tech, place)
    return [m for m in sorted(MODIFIERS) if set(TECHNIQUES[m]["modifies"]) & tg]


def _match(m, key, value) -> bool:
    d = TECHNIQUES[m]
    return d["key"] == key and (d["value"] == "*" or str(value).strip().lower() in (d["value"], *d.get("aliases", [])))


def keys() -> set:
    return {TECHNIQUES[m]["key"] for m in MODIFIERS}


def resolve(here, mind, verb, a, tech=None, place=False) -> dict:
    """The changes the action's modifiers make, merged; raises Refused for one the agent may not use. `_untaught` lists those tried
    untaught (done worse: the verb reads `untaught`); trying one makes the agent aware of it (rough, if tryable)."""
    out = {"_used": [], "_untaught": []}
    tg = _targets(verb, tech, place)
    for key in keys():
        if key == "for" or a.get(key) in (None, "", False):
            continue
        cands = [m for m in MODIFIERS if TECHNIQUES[m]["key"] == key and set(TECHNIQUES[m]["modifies"]) & tg]
        if not cands:
            continue
        m = next((c for c in cands if _match(c, key, a[key])), None)
        if m is None:
            vals = ", ".join(TECHNIQUES[c]["value"] for c in cands)
            raise Refused(f"{key} can be {vals} here")
        d = TECHNIQUES[m]
        lvl = KN.level(mind, m)
        if lvl in (None, "aware"):
            if d.get("untaught") != "tryable":
                if lvl is None:
                    here.apply("learn", person=mind.name, tech=m, level="aware", source="you thought of it")
                raise Refused(f"you do not know how to do it by {d['label']}; someone could show you")
            here.apply("learn", person=mind.name, tech=m, level="rough", source="you tried it untaught")
            out["_untaught"].append(m)
        elif lvl == "rough":
            out["_untaught"].append(m)
        for k, v in (d.get("changes") or {}).items():
            out[k] = {**out.get(k, {}), **v} if isinstance(v, dict) and isinstance(out.get(k), dict) else v
        out["_used"].append(m)
    return out


def practise(here, mind, mods: dict) -> None:
    """Using a modifier is practice at it (D2-52), as for any technique."""
    for m in mods.get("_used", []):
        if not KN.basic(m):
            KN.tried(here, mind, m, True, units=max(1, int(TECHNIQUES[m].get("units") or 1)))


def units(a, verb, tech=None, place=False) -> int:
    """Extra work the action's modifiers take (hiding: 1 or 2 units), for the day's budget."""
    n = 0
    for m in available(verb, tech, place):
        d = TECHNIQUES[m]
        if d["key"] != "for" and a.get(d["key"]) not in (None, "") and _match(m, d["key"], a[d["key"]]):
            n += int((d.get("changes") or {}).get("units", 0))
    return n


def lines(mind, verb, tech=None, place=False, limit=4) -> list:
    """The modifiers an agent knows (or knows of and could try), for its verb line."""
    out = []
    for m in available(verb, tech, place):
        d = TECHNIQUES[m]
        if d["key"] == "for":
            continue
        lvl = KN.level(mind, m)
        if lvl in ("rough", "capable", "known") or d.get("untaught") == "tryable":
            extra = f", {d['changes']['units']} unit{'s' if d['changes']['units'] > 1 else ''}" if (d.get("changes") or {}).get("units") else ""
            out.append(f'"{d["key"]}": "{d["value"]}" ({d["label"]}{extra})')
    return out[:limit]
