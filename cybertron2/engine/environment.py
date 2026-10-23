"""The environment of a day (environment/scheduler.md "The day's weather", environment/visibility.md; D2-69, D2-99 to D2-103): the
day's weather drawn within its spell, snow lying, and how much each place lets the senses through. Nothing here is stored: every value
is computed from the seed, the spec and the state of the land (D2-103), so it repeats for the same seed and day.

Other systems read it: perception and noticing (visibility), decay (wet or dry, frozen, warm), fuse events (sound at night), roads
(a ford high after heavy rain).
"""
from __future__ import annotations

from cybertron2.engine.data import COVERS, ENV, SPELLS, TERRAIN, WEATHER

WET = tuple(k for k, v in WEATHER.items() if v["wet"])


def spell(w, day=None) -> str:
    """The spell a day falls in: from the world's spec (`spells`, days counted from 1), else normal."""
    day = w.d if day is None else day
    for sp in w.spec.get("spells") or []:
        if int(sp["from"]) - 1 <= day <= int(sp["to"]) - 1:
            return sp["kind"]
    return "normal"


def weather(w, day=None) -> str:
    """The day's weather for the region (keyed: weather, day). A spec may fix a day's weather (`weather`: {day: kind}) for a scripted
    run. Rain falls as snow in winter and on cold days."""
    day = w.d if day is None else day
    fixed = (w.spec.get("weather") or {}).get(day + 1) or (w.spec.get("weather") or {}).get(str(day + 1))
    if fixed:
        return fixed
    table = SPELLS[spell(w, day)]
    u = w.rng("weather", day).random()
    kind = next(iter(table))
    acc = 0.0
    for k, p in table.items():
        acc += p
        if u < acc:
            kind = k
            break
    if kind in ("rain", "heavy rain") and w.cold(day):
        kind = "snow"
    return kind


def wet(w, day=None) -> bool:
    return weather(w, day) in WET


def snow_lying(w, day=None) -> bool:
    """Snow lies after a snow day until three days without frost."""
    day = w.d if day is None else day
    thaw = 0
    for d in range(day, -1, -1):
        if weather(w, d) == "snow":
            return thaw < int(ENV["snow_melt"])
        if not w.cold(d):
            thaw += 1
            if thaw >= int(ENV["snow_melt"]):
                return False
    return False


def since_heavy_rain(w, day=None, horizon=10):
    """Days since the last heavy rain, or None within the horizon (a ford is high for a while after: world/roads.md)."""
    day = w.d if day is None else day
    for d in range(day, max(-1, day - horizon), -1):
        if weather(w, d) == "heavy rain":
            return day - d
    return None


# ---------------------------------------------------------------------- visibility (computed per place and day: D2-103)
def _today_events(w, node):
    return [e for e in w.s.get("events", []) if e.get("place") == node and e.get("day", w.d) == w.d]


def _worked_techs(w, node, parcel) -> set:
    return {e.get("tech") for e in _today_events(w, node) if e.get("kind") == "work" and f"parcel:{parcel}" in (e.get("about") or [])}


def crop_high(w, parcel) -> bool:
    p = w.s["parcels"][parcel]
    c = p.get("crop")
    if not c or c.get("area_left", 0) <= 1e-6 or p["cover"] != "field":
        return False
    sown, ripe = int(c.get("sown", c.get("day", 0)) or 0), int(c.get("ripe_day", 0))
    return w.d >= sown + float(ENV["crop_high_from"]) * max(1, ripe - sown)


def smoky(w, node, parcel) -> bool:
    for e in _today_events(w, node):
        if f"parcel:{parcel}" not in (e.get("about") or []):
            continue
        if e.get("tech") in ENV["smoke_techs"] or set(e.get("tags") or []) & set(ENV["smoke_tags"]) or e.get("kind") == "fire":
            return True
    return False


def loudness(w, node, parcel=None) -> str:
    """'very', 'loud' or '' for what is making noise at a place today (D2-100)."""
    level = WEATHER[weather(w)].get("loud", "")
    for e in _today_events(w, node):
        if parcel and e.get("about") and f"parcel:{parcel}" not in e["about"] and e.get("kind") not in ENV["loud_kinds"]:
            continue
        x = ENV["loud_kinds"].get(e.get("kind")) or ENV["loud_techs"].get(e.get("tech")) or next(
            (ENV["loud_tags"][t] for t in e.get("tags") or [] if t in ENV["loud_tags"]), "")
        if x == "very":
            return "very"
        level = level or x
    return level


def visibility(w, node, parcel=None, sense="sight", night=False, moon=False, quiet=True, cover=None) -> float:
    """How much a place lets a sense through today (D2-99): the cover's base x the land's state x the day's weather (x night).
    `cover` names a cover or road terrain directly (roads); `quiet` applies masking to a quiet sound (D2-100)."""
    if sense not in ("sight", "sound"):
        return 1.0                                                          # smell: its own salience, no multipliers (D2-101)
    cov = cover or (w.s["parcels"][parcel]["cover"] if parcel else "built")
    base = float((COVERS.get(cov) or TERRAIN.get(cov) or {}).get(sense, 1.0))
    wx = WEATHER[weather(w)]
    v = base * float(wx[sense])
    if sense == "sight" and parcel and not cover:
        if crop_high(w, parcel):
            v *= float(ENV["crop_high"])
        if smoky(w, node, parcel):
            v *= float(ENV["smoke"])
    if night:
        v *= float(ENV["night"]["moon"] if moon else ENV["night"]["sight"]) if sense == "sight" else float(ENV["night"]["sound"])
    if sense == "sound" and quiet and node:
        m = loudness(w, node, parcel)
        if m:
            v *= float(ENV["mask"][m])
    return round(v, 4)


def ground_factor(w) -> float:
    """Things lying on the ground under snow (D2-99)."""
    return float(ENV["snow_ground"]) if snow_lying(w) else 1.0


def words(w, day=None) -> str:
    return WEATHER[weather(w, day)]["words"] + ("; snow lies on the ground" if snow_lying(w, day) and weather(w, day) != "snow" else "")
