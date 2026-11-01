"""The spec's end-state model of buildings (economy/buildings.md, D2-154, D2-155), not yet in the engine: rooms, spaces, ground.

Read from the state when the engine stores rooms; derived by the spec's seeding rule until then (records say "derived": true).
When the engine builds Package E, `Rooms.get` reads its rooms and the rest of this file can go.
"""
from __future__ import annotations

import math

from c2viz import touch as E

# The spec's space model (economy/buildings.md, D2-154, D2-155), not yet in the engine: what a fitting takes of a room's floor,
# what ground a unit of a parcel's size gives for buildings, the rooms one may build, what a store holds.
SPACES = {"beds": 1, "bins": 1, "hand mill": 1, "fire ring": 1, "hearth": 1, "oven": 2, "anvil": 2, "granary": 3,
          "millstones": 3, "water wheel": 0, "cellar": 0, "stalls": 2, "woodshed": 0, "vault": 4}
GROUND = {"built": 24, "scrub": 16}
ROOMS = {"small room": 6, "medium room": 12, "hall": 30, "camp": 4}
FLOOR_HOLDS = 30                                     # weight a space of free floor
FITTED_HOLDS = {"bins": 60, "granary": 300}          # bins: food; a granary floor: grain
BLUEPRINT_ROOM = {"small room": "small room", "medium room": "medium room", "hall": "hall", "camp": "camp"}



def rooms_for(floor: int, structure: str) -> list:
    """The fewest rooms of 6, 12 and 30 spaces that give `floor` (wattle: small rooms only; a camp: its lean-to)."""
    if structure == "camp":
        return ["camp"]
    out, n = [], max(1, int(math.ceil(floor)))
    if structure == "wattle":
        return ["small room"] * max(1, math.ceil(n / 6))
    while n > 0:
        if n > 24:
            out.append("hall"); n -= 30
        elif n > 12:
            out.append("medium room"); n -= 12
        elif n > 6:
            out.append("medium room"); n -= 12
        else:
            out.append("small room"); n -= 6
    return out


def floor_needed(b: dict, stock: dict) -> dict:
    """What a building's floor must hold (spec, D2-154, D2-155): its beds and fittings, and its stores beyond what fittings keep."""
    fit = b.get("fittings") or {}
    beds = int(fit.get("beds") or 0)
    fitted = sum(SPACES.get(f, 1) * (1 if f != "beds" else 0) for f, n in fit.items() if n)
    weight = sum(q * E.weight(i) for i, q in stock.items() if q > 1e-9)
    kept = sum(FITTED_HOLDS.get(f, 0) for f in fit if fit[f])
    store = max(0.0, weight - kept) / FLOOR_HOLDS
    return {"beds": beds, "fittings": fitted, "store": round(store, 2), "total": beds + fitted + store}


class Rooms:
    """Each building's rooms for the whole run: read when the engine has them; else derived by the spec's seeding rule from the
    first day it stands (floor enough for its beds, fittings and stores), a room added when later fittings outgrow it; a built
    building has its blueprint's room."""

    def __init__(self):
        self.of = {}

    def get(self, bid, b, stock, built_from=None) -> dict:
        if b.get("rooms"):                                                          # the end state: rooms in the state
            rooms = [{"kind": r.get("kind"), "floor": r.get("floor"), "storey": r.get("storey", 1)} for r in b["rooms"]]
            return {"rooms": rooms, "derived": False}
        need = floor_needed(b, stock)
        rec = self.of.get(bid)
        if rec is None:
            kinds = [BLUEPRINT_ROOM[built_from]] if built_from in BLUEPRINT_ROOM else rooms_for(need["total"], b.get("structure"))
            rec = self.of[bid] = {"kinds": kinds}
        have = sum(ROOMS[k] for k in rec["kinds"])
        fixed = need["beds"] + need["fittings"]
        if fixed > have and b.get("structure") != "camp":                        # fittings outgrew it: an adjoining room
            rec["kinds"] = rec["kinds"] + rooms_for(fixed - have, b.get("structure"))
            have = sum(ROOMS[k] for k in rec["kinds"])
        rooms = [{"kind": k, "floor": ROOMS[k], "storey": 1} for k in rec["kinds"]]
        return {"rooms": rooms, "derived": True, "floor": have, "used": round(min(have, need["total"]), 1), "need": need}


