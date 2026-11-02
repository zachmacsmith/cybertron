"""Every place c2viz touches the engine, and nothing else does (c2viz/README.md, "Where the engine is touched").

The engine is changing quickly; when it does, this file (and the record builders that read World.s, extract.py and timeline.py)
is what changes, never the renderer. Each name here is one engine function, table or class used by c2viz; `check()` lists any that
the engine no longer has, and the tests run it.
"""
from __future__ import annotations

from cybertron2.engine import data as _DT, environment as _EV, farm as _FM, journal as _JN, layout as _LY, life as _LF, roads as _RD, signs as _SG
from cybertron2.engine import things as _TH, verbs as _VB
from cybertron2.engine.here import Here as _Here
from cybertron2.engine.world import World as _World

# ---------------------------------------------------------------------------------------------------- tables
ITEMS, CLEARING, BLUEPRINTS, THINGS, EVENT_EXTENT = _DT.ITEMS, _DT.CLEARING, _DT.BLUEPRINTS, _DT.THINGS, _DT.EVENT_EXTENT
SEEN = _DT.LAYOUT["seen"]
THING_KINDS = _TH.KINDS


def weight(item) -> float:
    return ITEMS.get(item, {}).get("weight", 1)


def item_seen(item) -> bool:
    return bool(ITEMS.get(item, {}).get("seen"))


def tables() -> dict:
    """The engine's tables the renderer may read (never its own copies)."""
    pick = lambda d, keys: {k: {kk: v.get(kk) for kk in keys if kk in v} for k, v in d.items()}
    return {"covers": pick(_DT.COVERS, ("words", "lots", "sight", "sound", "dig")), "crops": pick(_DT.CROPS, ("seed", "share", "hardy", "names")),
            "fittings": pick(_DT.FITTINGS, ("label", "does", "fire", "needs", "site", "spoil")),
            "blueprints": pick(_DT.BLUEPRINTS, ("label", "units", "size", "structure", "lasts")),
            "fences": pick(_DT.FENCES, ("words",)), "weather": _DT.WEATHER, "seen": SEEN, "height": _DT.LAYOUT["height"],
            "things": {k: v for k, v in THINGS.items() if not isinstance(v, dict)}, "terrain": _DT.TERRAIN,
            "landmarks": {k: {kk: vv for kk, vv in v.items() if isinstance(vv, (str, int, float, bool))} for k, v in _DT.LANDMARKS.items()},
            "event_extent": EVENT_EXTENT}


# ---------------------------------------------------------------------------------------------------- the world at a step
def checkpoint(db, step) -> dict:
    return _JN.checkpoint(db, step)


def world(spec, state) -> _World:
    w = _World(spec)
    w.s = state
    return w


class NodeHere(_Here):
    """A view of a node with nobody looking: the engine's own reads (parcels, buildings, herds, events, stock), the world as it is.
    Those present are everyone at the node (World.present), as for anyone standing there."""

    def __init__(self, w, nid):
        self._w, self.name, self.node, self.place = w, None, nid, nid

    def people(self, me=True) -> list:
        return self._w.present(self.node)


def node_view(w, nid):
    return NodeHere(w, nid)


# ---------------------------------------------------------------------------------------------------- what the engine computes
parcel_signs = _SG.context                         # (here, pid): what a parcel is like, as its signs are derived
building_signs = _SG.building_context              # (here, bid)
weather, words, wet, snow_lying = _EV.weather, _EV.words, _EV.wet, _EV.snow_lying
felled, smoky, crop_high, visibility = _EV.felled, _EV.smoky, _EV.crop_high, _EV.visibility
soil_word, herd_head = _FM.soil_word, _FM.head
showing = _LF.showing
spot_of, at_node, body_state, rotting, carcass_fresh = _TH.spot_of, _TH.at_node, _TH.body_state, _TH.rotting, _TH.carcass_fresh
road_position, challenge = _RD.position, _RD.challenge


def clearing_work(cover) -> float:
    return CLEARING.get(cover, 0)


def blueprint_units(bp) -> float:
    return BLUEPRINTS.get(bp, {}).get("units") or 1


def act_units(w, act) -> int:
    """What an act cost (verbs.cost): a verb's own units, else its technique's (a make record is one of its batch)."""
    n = _VB.verb_units(w.p, act.get("verb")) if act.get("verb") in _VB.VERB else None
    if n is not None:
        return int(n)
    tech = _DT.TECHNIQUES.get(act.get("tech") or "")
    return int(tech["units"]) if tech else 1


def route(w, name) -> list:
    """One's day as a chain of parcels by the engine's rule (layout.route, D4-62), for a run made before the engine kept it; [] when
    the engine has no such rule."""
    fn = getattr(_LY, "route", None)
    return list(fn(w, name)) if fn else []


def replay(w, prim, place, kw):
    """One journaled change applied again, through the engine's own chokepoint."""
    return w.apply(prim, place, **kw)


# ---------------------------------------------------------------------------------------------------- the contract with the engine
TOUCHPOINTS = {
    "tables": ["ITEMS", "CLEARING", "BLUEPRINTS", "THINGS", "EVENT_EXTENT", "COVERS", "CROPS", "FITTINGS", "FENCES", "WEATHER", "LAYOUT", "TERRAIN",
               "LANDMARKS", "TECHNIQUES"],
    "functions": [(_SG, "context"), (_SG, "building_context"), (_EV, "weather"), (_EV, "words"), (_EV, "wet"), (_EV, "snow_lying"), (_EV, "felled"),
                  (_EV, "smoky"), (_EV, "crop_high"), (_EV, "visibility"), (_FM, "soil_word"), (_FM, "head"), (_LF, "showing"), (_TH, "spot_of"),
                  (_TH, "at_node"), (_TH, "body_state"), (_TH, "rotting"), (_TH, "carcass_fresh"), (_TH, "KINDS"), (_RD, "position"), (_RD, "challenge"),
                  (_VB, "verb_units"), (_VB, "VERB"), (_JN, "checkpoint"), (_LY, "route")],
    "world": ["apply", "calendar", "cold", "units_for", "agents_acting", "present", "holders", "household_of", "homes"],
    "state": ["parcels", "buildings", "herds", "containers", "people", "nodes", "roads", "events", "acts", "log", "today"],
}


def check(state: dict | None = None) -> list:
    """What c2viz uses that the engine (or a state) no longer has: empty when all is well."""
    missing = [f"data.{t}" for t in TOUCHPOINTS["tables"] if not hasattr(_DT, t)]
    missing += [f"{m.__name__}.{f}" for m, f in TOUCHPOINTS["functions"] if not hasattr(m, f)]
    missing += [f"World.{f}" for f in TOUCHPOINTS["world"] if not hasattr(_World, f)]
    if state is not None:
        missing += [f"World.s[{k!r}]" for k in TOUCHPOINTS["state"] if k not in state and k != "today"]
    return missing
