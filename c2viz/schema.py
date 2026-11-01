"""The contract between the model (Python, the engine's side) and the renderer (JS): what viz.json holds. The renderer reads only
this; when the engine changes, the model changes to keep it, or SCHEMA_VERSION goes up and c2viz/SCHEMA.md says what changed.
`validate` lists what a viz.json lacks; the tests and the build run it.
"""
from __future__ import annotations

SCHEMA_VERSION = 1

TOP = {"meta": dict, "tables": dict, "static": dict, "days": list}
META = ("name", "days", "seed", "people", "season_days", "schema")
STATIC = ("nodes", "parcels", "roads", "layout")
DAY = ("day", "calendar", "cold", "weather", "words", "wet", "snow", "parcels", "buildings", "herds", "things", "people", "roads", "traces",
       "events", "acts", "fights")
PARCEL = ("cover", "res", "holders")
BUILDING = ("node", "parcel", "name", "structure", "condition", "door", "fire", "fittings", "rooms", "footprint", "sleepers", "holders", "stock", "made")
HERD = ("node", "parcel", "cows", "oxen", "bulls", "young", "hungry", "watched")
THING = ("kind", "node", "parcel", "goods")
PERSON = ("at", "alive", "stage", "hunger", "wounded", "homes", "spot", "carried")
TIMELINE = ("from", "morning", "acts", "routes", "budget", "talk")
ACT = ("actor", "verb", "t0", "t1", "delta")


def validate(viz: dict) -> list:
    out = []
    need = lambda rec, keys, where: out.extend(f"{where}: no {k!r}" for k in keys if k not in rec)
    for k, t in TOP.items():
        if not isinstance(viz.get(k), t):
            out.append(f"top: {k!r} missing or not a {t.__name__}")
    if out:
        return out
    need(viz["meta"], META, "meta")
    need(viz["static"], STATIC, "static")
    for d in viz["days"][:1] + viz["days"][-1:]:
        where = f"day {d.get('day')}"
        need(d, DAY, where)
        for kind, keys in (("parcels", PARCEL), ("buildings", BUILDING), ("herds", HERD), ("things", THING), ("people", PERSON)):
            for i, rec in list((d.get(kind) or {}).items())[:3]:
                need(rec, keys, f"{where} {kind} {i}")
        T = d.get("timeline")
        if T:
            need(T, TIMELINE, f"{where} timeline")
            for a in T.get("acts", [])[:3]:
                need(a, ACT, f"{where} act")
    return out
