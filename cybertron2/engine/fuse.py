"""Fuse events: time to respond (conflict/fuse_events.md; D2-5, D2-80 to D2-84, D2-86, D2-110).

A sub-step of the night, after the day's work and before the night's settlement: events with a fuse are gathered from their
sources, each is detected (or not) by those who could, and whoever detects one before it finishes gets one urgent call, appended to
its own conversation (D2-84). The fuse's length sets how many acts the call allows. Undetected events take their default.

Event kinds are a registry: a kind has a data row (data.FUSE: sense, detection chances, acts by structure, choices) and code in three
places, each registered by kind: `SOURCES` (which events tonight), `DETECT` (who notices, with what signs) and `CHOICES` (what an
answer does). The roads package adds meetings, finds and crossings the same way; fire waits for the scheduler's house fire.
"""
from __future__ import annotations

from cybertron2.engine import environment as EV
from cybertron2.engine.data import FUSE, ITEMS
from cybertron2.engine.world import Refused

SOURCES, DETECT, CHOICES, WORDS = {}, {}, {}, {}


def source(kind):
    def reg(fn):
        SOURCES[kind] = fn
        return fn
    return reg


def detector(kind):
    def reg(fn):
        DETECT[kind] = fn
        return fn
    return reg


def choice(kind, name):
    def reg(fn):
        CHOICES[(kind, name)] = fn
        return fn
    return reg


# ---------------------------------------------------------------------- the night sub-step
def gather(w, today) -> list:
    """Tonight's events with a fuse, in order of their start (ties by a keyed draw: D2-82)."""
    evs = []
    for kind, fn in SOURCES.items():
        evs += fn(w, today)
    for e in evs:
        e.setdefault("start", w.rng("fuse-start", w.d, e["kind"], e.get("id")).random())
    return sorted(evs, key=lambda e: (e["start"], e["id"]))


def acts_for(e) -> int:
    d = FUSE[e["kind"]]
    n = int(d["acts"].get(e.get("structure"), max(d["acts"].values())))
    if e.get("riders"):
        n = min(n, int(d["riders"]["acts"]))
    return n


def plan(w, today) -> dict:
    """Who is woken tonight, and by what: {name: {"events": [...], "signs": [...], "acts": n}}. One call an agent a night (D2-80);
    events at one node share one wave and each woken agent sees every event it detected (D2-82)."""
    called = w.s.setdefault("fuse_calls", {})
    out = {}
    evs = gather(w, today)
    today["fuse"] = evs
    for e in evs:
        if acts_for(e) <= 0:
            e["woken"] = []
            continue
        seen = DETECT[e["kind"]](w, today, e)
        e["woken"] = sorted(seen)
        for name, sign in sorted(seen.items()):
            if called.get(name) == w.d and name not in out:
                continue
            x = out.setdefault(name, {"events": [], "signs": [], "acts": 0})
            x["events"].append(e)
            x["signs"].append(sign)
            x["acts"] = max(x["acts"], acts_for(e))
    for name in out:
        called[name] = w.d
    return out


def record(today) -> list:
    """What tonight's fuse events were and who was woken, for the day's log."""
    return [{"kind": e["kind"], "id": e["id"], "at": e.get("label"), "acts": acts_for(e), "woken": e.get("woken", []),
             "alarm": bool(e.get("alarm")), "handed": (e.get("fight") or {}).get("handed")} for e in today.get("fuse", [])]


def answer(w, today, name, x, reply) -> list:
    """Do what the woken agent chose, up to its acts. Choices of the event's kind act on the event; ordinary verbs (taking a weapon
    into one's hands) go through the verbs as by day. Returns the result lines."""
    from cybertron2.engine import verbs as V
    from cybertron2.engine.here import Here, Mind
    acts = [a for a in (reply.get("actions") or []) if isinstance(a, dict)][: x["acts"]]
    lines = []
    for a in acts:
        do = str(a.get("do", "")).strip().lower()
        e = _event_for(x["events"], a)
        fn = CHOICES.get((e["kind"], do))
        if fn:
            try:
                lines.append(fn(w, today, name, e, a))
            except Refused as err:
                lines.append(f"Refused: {do}: {err}")
        elif do in FUSE[e["kind"]].get("also", []):
            lines.append(V.do(Here(w, name), Mind(w, name), a))
        else:
            lines.append(f"Refused: {do}: in the night you can only {', '.join(FUSE[e['kind']]['choices'] + FUSE[e['kind']].get('also', []))}")
    if not acts:
        lines.append("You did nothing.")
    if len([a for a in (reply.get("actions") or []) if isinstance(a, dict)]) > x["acts"]:
        lines.append(f"There was time for only {x['acts']} thing{'s' if x['acts'] > 1 else ''}.")
    return lines


def _event_for(events, a):
    tgt = str(a.get("at") or a.get("target") or "").lower()
    for e in events:
        if tgt and tgt in str(e.get("label", "")).lower():
            return e
    return events[0]


# ---------------------------------------------------------------------- a raid on a building (D2-81: only sometimes detected)
@source("raid")
def _raids(w, today) -> list:
    out = []
    for f in today.get("fights", []):
        if f["kind"] != "raid" or not w.s["people"][f["by"]]["alive"] or w.at(f["by"]) != f["node"]:
            continue
        b = w.s["buildings"][f["building"]]
        out.append({"id": f"raid:{f['by']}:{f['building']}", "kind": "raid", "node": f["node"], "building": f["building"], "by": f["by"],
                    "structure": b["structure"], "riders": bool(f.get("riders")), "label": b["name"], "fight": f})
    return out


@detector("raid")
def _detect_raid(w, today, e) -> dict:
    """A chance only: a watcher, a dog, those inside, neighbours who hear it; heard through the night's sound (D2-99)."""
    from cybertron2.engine.night import sleeping_places
    d = FUSE["raid"]["detect"]
    bid, node = e["building"], e["node"]
    b = w.s["buildings"][bid]
    where = sleeping_places(w, today)
    sound = EV.visibility(w, node, b["parcel"], "sound", night=True, quiet=False)
    riders = float(FUSE["raid"]["riders"]["detect"]) if e.get("riders") else 1.0
    out = {}
    for n in w.present(node):
        if n == e["by"] or w.s["people"][n]["stage"] == "child" or n in (today.get("travel") or {}):
            continue
        if (today.get("guards") or {}).get(n) == bid:
            p, sign = float(d["watcher"]), f"from your watch at {b['name']}: a shape at the door in the dark, someone trying the bar"
        elif where.get(n) == bid:
            p = float(d["dog"]) if b["fittings"].get("dog") else float(d["inside"].get(b["structure"], 0.3))
            sign = f"a crash at the door of {b['name']}, where you sleep; someone is breaking in"
        elif where.get(n) and w.s["buildings"][where[n]]["node"] == node:
            p = float(d["neighbour"]) * sound
            sign = f"a noise in the night from {b['name']}: wood splitting, a muffled voice"
        else:
            continue
        if w.rng("fuse-detect", w.d, e["id"], n).random() < min(1.0, p * riders):
            out[n] = sign
    return out


@choice("raid", "defend")
def _defend(w, today, name, e, a) -> str:
    today.setdefault("guards", {})[name] = e["building"]
    today.setdefault("awake", []).append(name)
    return f"You went to the door of {e['label']} to fight off whoever was there."


@choice("raid", "flee")
def _flee(w, today, name, e, a) -> str:
    today.setdefault("fled", []).append(name)
    return f"You slipped out of {e['label']} into the dark and kept away until it was over."


@choice("raid", "alarm")
def _alarm(w, today, name, e, a) -> str:
    from cybertron2.engine.night import sleeping_places
    where = sleeping_places(w, today)
    woke = [n for n in w.present(e["node"]) if where.get(n) == e["building"] and n != e["by"]]
    today.setdefault("awake", []).extend(woke)
    e["alarm"] = True
    w.event(e["node"], "alarm", f"a shout in the night: someone raised the alarm at {e['label']}", actor=name, about=[f"building:{e['building']}"],
            salience=0.9, tags=["danger"], sense="sound")
    return f"You shouted and woke the house: {', '.join(x for x in woke if x != name) or 'nobody else was there'}."


@choice("raid", "hand over")
def _hand_over(w, today, name, e, a) -> str:
    b = w.s["buildings"][e["building"]]
    item = str(a.get("item") or "").strip().lower() or next((i for i, q in w.goods(b["stock"]).items() if q > 1e-9 and ITEMS[i]["food"] > 0), "")
    have = w.goods(b["stock"]).get(item, 0.0)
    if have <= 1e-9:
        raise Refused(f"there is no {item or 'food'} in {b['name']} to hand over")
    q = min(have, float(a.get("qty") or have))
    w.apply("transfer", e["node"], src=b["stock"], dst=w.hands(e["by"]), item=item, qty=round(q, 6))
    e["fight"]["handed"] = {"by": name, "item": item, "qty": round(q, 2)}
    return f"You handed {q:g} {item} out of {b['name']} to whoever was at the door; they took it and went."


@choice("raid", "stay")
def _stay(w, today, name, e, a) -> str:
    return "You lay still and waited."
