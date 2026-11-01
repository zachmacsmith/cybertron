"""A day as it happened (c2viz/ENGINE.md §11): the journal's changes for the work step replayed act by act through the engine's own
chokepoint (c2viz.touch.replay), with what each act changed, the engine's route (D4-62) and the talk.
"""
from __future__ import annotations

import json

from c2viz import source as S, touch as E
from c2viz.extract import building_day, day_record, herd_day, node_view, parcel_day, r3, thing_day
from c2viz.spec_rooms import Rooms


def _touched(w, kw, out) -> dict:
    """What a change touched, from its arguments and result: parcels, buildings, herds, things, people (by their hands)."""
    t = {"parcels": set(), "buildings": set(), "herds": set(), "things": set(), "people": set()}
    vals = list(kw.values()) + [out]
    while vals:
        v = vals.pop()
        if isinstance(v, (list, tuple)):
            if len(v) == 2 and isinstance(v[0], str) and v[0] in ("parcel", "building", "herd", "person") and isinstance(v[1], str):
                vals.append(v[1])
            else:
                vals.extend(v)
            continue
        if not isinstance(v, str):
            continue
        if v in w.s["parcels"]:
            t["parcels"].add(v)
        elif v in w.s["buildings"]:
            t["buildings"].add(v)
        elif v in w.s["herds"]:
            t["herds"].add(v)
        elif v in w.s["people"]:
            t["people"].add(v)
        elif v in w.s["containers"]:
            c = w.s["containers"][v]
            if c["kind"] == "hands":
                t["people"].add(c.get("of") or v.split(":", 1)[1])
            elif c["kind"] == "stock":
                t["buildings"].add(c.get("of") or v.split(":", 1)[1])
            else:
                t["things"].add(v)
    return t


def timeline(R, d, rooms: Rooms) -> dict | None:
    """The day's work as it happened (the journal's changes in order, spec/record): the world just before the work step, then
    each act replayed through the engine's own primitives (World.apply), with what it changed. When in the day an act falls is a
    presentation choice (the engine has no clock inside a day): an act starts where the actor's earlier acts' units end, against
    the units the actor had that day (World.units_for). Where each one went is the engine's route (layout.route, D4-62)."""
    steps = S.day_steps(R, d)
    if f"d{d}.work" not in steps:
        return None
    pre = steps[steps.index(f"d{d}.work") - 1]
    rows = S.changes(R, f"d{d}.work")
    talk = S.speech(R, d)
    after = S.world_at(R, f"d{d}.work")
    routes = dict((after.s.get("today") or {}).get("route") or {})
    acted = [a for a in after.s["acts"] if a.get("day") == d]
    w = S.world_at(R, pre)
    budget = {n: max(1, w.units_for(n)) for n in w.agents_acting()}
    morning = day_record(w, rooms)
    groups, cur = [], None
    for seq, prim, place, args, cause in rows:
        c = json.loads(cause) if cause else {}
        if c.get("within"):
            continue                                                            # made inside another primitive: replayed with it
        key = (c.get("actor"), c.get("verb"), c.get("for"))
        if cur is None or cur["key"] != key:
            cur = {"key": key, "rows": []}
            groups.append(cur)
        cur["rows"].append((prim, place, json.loads(args)))
    queue = {}
    for a in acted:
        queue.setdefault(a["actor"], []).append(a)
    used, acts, failed = {}, [], 0
    for g in groups:
        actor, verb, party = g["key"]
        touched = {"parcels": set(), "buildings": set(), "herds": set(), "things": set(), "people": set()}
        for prim, place, kw in g["rows"]:
            try:
                out = E.replay(w, prim, place, kw)
            except Exception:                                                   # noqa: BLE001 (a change that will not replay is counted)
                failed += 1
                out = None
            for k, v in _touched(w, kw, out).items():
                touched[k] |= v
        rec = None
        for i, a in enumerate(queue.get(actor, [])):
            if a.get("verb") == verb:
                rec = queue[actor].pop(i)
                break
        u = E.act_units(w, rec or {"verb": verb})
        b = budget.get(actor, 7)
        t0 = used.get(actor, 0) / b
        used[actor] = used.get(actor, 0) + u
        views = {}
        view = lambda nid: views.setdefault(nid, node_view(w, nid))
        delta = {"parcels": {p: parcel_day(w, view(w.s["parcels"][p]["node"]), p) for p in touched["parcels"]},
                 "buildings": {b_: building_day(w, view(w.s["buildings"][b_]["node"]), b_, rooms, {}) for b_ in touched["buildings"]},
                 "herds": {h: x for h in touched["herds"] if (x := herd_day(w, h))},
                 "things": {c: thing_day(w, c, w.s["containers"][c]) for c in touched["things"] if c in w.s["containers"]},
                 "carried": {n: {i: r3(q) for i, q in w.s["containers"].get(f"hands:{n}", {}).get("goods", {}).items() if q > 1e-9}
                             for n in touched["people"] if n in w.s["people"]}}
        delta = {k: v for k, v in delta.items() if v}
        acts.append({"actor": actor, "verb": verb, "for": party, "tech": (rec or {}).get("tech"), "site": (rec or {}).get("site"),
                     "node": (rec or {}).get("node") or (g["rows"][0][1] if g["rows"] else None), "units": u,
                     "t0": round(min(1.0, t0), 3), "t1": round(min(1.0, used[actor] / b), 3), "delta": delta})
    return {"from": pre, "morning": {k: morning[k] for k in ("parcels", "buildings", "herds", "things", "people")},
            "acts": acts, "routes": routes, "budget": budget, "talk": talk, "unreplayed": failed}


