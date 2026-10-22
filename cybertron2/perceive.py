"""What each agent knows (docs/review/38_space_engine/02_perception.md): what it sees where it is, what it remembers of elsewhere and
how old that is, what it witnessed and heard, and the memories that last. Written by the engine at the moment of observation, never
by the model; the model's own notes stay separate.

The store, w.s["know"][agent]:
    places      {place: {round, plants, game, people: [names], houses: {house: word}}}: the last time it was there
    people      {name: {round, at, condition, load}}: the last time it saw them
    house       its own house as it last saw it: {round, condition, stock: {item: qty}}
    seen        acts it witnessed this round: [{round, place, text}] (each step and the night)
    heard       speech it heard this round: [text]
    rounds      one line per past round: [{round, line}]: the summary band (the old engine's history mode, review 20 §4)
    full        the last rounds in full: [{round, did: [lines], seen: [lines], heard: [lines]}] (FULL_ROUNDS kept)
    memories    salient things that last: [{round, text}] (deaths, fights, gifts, wounds, the cold, a house breaking; at most
                LONG_MEMORIES, oldest dropped first)

Observation points (run.py): the start of every round, after every interleaved step, and the night (after the end of round).
Witnessing: an act is seen by everyone else at the place where it happened at that step; a departure by those left behind and an
arrival by those at the destination; a night fight by everyone at that place at night.
"""
from __future__ import annotations

FULL_ROUNDS = 2
SUMMARY_ROUNDS = 8
LONG_MEMORIES = 14
ELSEWHERE_ROUNDS = 6                    # an observation older than this drops out of "Elsewhere" (it stays in the store)


def store(w, name) -> dict:
    return w.s["know"].setdefault(name, {"places": {}, "people": {}, "house": None, "seen": [], "heard": [], "rounds": [],
                                         "full": [], "memories": []})


def observe(w, name) -> None:
    """Record what the agent perceives where it is now."""
    if not w.s["agents"][name]["alive"]:
        return
    k = store(w, name)
    here = w.s["agents"][name]["at"]
    present = [n for n in w.at(here) if n != name]
    old = k["places"].get(here)
    if old and old["round"] < w.r:
        k.setdefault("prev_places", {})[here] = old                 # the last sight from an earlier round: what "changed" compares to
    k["places"][here] = {"round": w.r, "plants": w.plants_word(here), "game": w.game_word(here), "people": present,
                         "houses": {hid: w.stock_word(hid) for hid, h in w.s["houses"].items() if h["node"] == here}}
    for n in present:
        k["people"][n] = {"round": w.r, "at": here, "condition": w.condition_word(n), "load": w.load_word(n)}
    h = w.home(name)
    if h is not None and h["node"] == here:
        if k["house"] and k["house"]["round"] < w.r:
            k["prev_house"] = k["house"]
        k["house"] = {"round": w.r, "condition": h["condition"], "stock": dict(h["stock"])}


def observe_all(w) -> None:
    for n in w.living():
        observe(w, n)


def witness(w, actor, place, seen, before=None) -> None:
    """An act by `actor` at `place`: everyone else there sees `seen` (a str, or {text, left, to}). before: who was at the place
    before a departure (they see it leave)."""
    if not seen:
        return
    if isinstance(seen, str):
        seen = {"text": seen}
    if "left" in seen:                                              # a departure: the people left behind see it; the arrivals see it come
        for n in before or ():
            if n != actor:
                store(w, n)["seen"].append({"round": w.r, "place": w.place(seen["left"]), "text": seen["text"]})
        for n in w.at(place):
            if n != actor:
                store(w, n)["seen"].append({"round": w.r, "place": w.place(place),
                                            "text": f"{actor} arrived from {w.place(seen['left'])}"})
        return
    for n in w.at(place):
        if n != actor:
            store(w, n)["seen"].append({"round": w.r, "place": w.place(place), "text": seen["text"]})
    if seen.get("to") in w.s["agents"] and seen["to"] != actor:
        remember(w, seen["to"], seen["text"])                       # what is done to you lasts


def remember(w, name, text, rnd=None) -> None:
    m = store(w, name)["memories"]
    m.append({"round": w.r if rnd is None else rnd, "text": text})
    del m[:-LONG_MEMORIES]


def night(w, rec) -> None:
    """The night's events, as the agents at each place saw them: fights, deaths, the cold, breaks. Called after the end of the
    round (w.r has moved on: the round is rec["round"])."""
    rnd = rec["round"]
    def see(place, text):
        for n in w.at(place):
            store(w, n)["seen"].append({"round": rnd, "place": w.place(place), "text": text})
            remember(w, n, f"{text} (round {rnd + 1}, {w.place(place)})", rnd)
    for f in rec["fights"]:
        if f.get("outcome") == "fizzled":
            continue
        if f["kind"] == "raid":
            house = w.s["houses"][f["house"]]["name"]
            if f["outcome"] == "taken":
                text = f"At night {', '.join(f['raiders'])} raided {house} and took {f['took']:g} food"
                if f.get("wounded"):
                    text += f"; {f['wounded'][0]} was wounded and robbed"
            else:
                text = f"At night {', '.join(f['raiders'])} raided {house} and were driven off"
                if f.get("wounded"):
                    text += f" ({', '.join(f['wounded'])} wounded)"
            if f.get("guards"):
                text += f"; on guard: {', '.join(f['guards'])}"
        else:
            t = f["target"]
            text = {"killed": f"At night {', '.join(f['attackers'])} killed {t}",
                    "wounded": f"At night {', '.join(f['attackers'])} wounded {t} and robbed them",
                    "repelled": f"At night {', '.join(f['attackers'])} attacked {t} and were driven off"}[f["outcome"]]
            if f["outcome"] == "repelled" and f.get("wounded"):
                text += f" ({', '.join(f['wounded'])} wounded)"
        see(f["node"], text)
    for d in rec["deaths"]:
        a = w.s["agents"][d]
        if a.get("cause") == "attack":
            continue                                                    # already told as the fight
        see(a["at"], f"{d} died ({a['cause']})")
    for n in rec["cold_falls"]:
        remember(w, n, f"A night out in the cold in round {rnd + 1} left you starving", rnd)
    for hid in rec["breaks"]:
        h = w.s["houses"][hid]
        see(h["node"], f"{h['name']} was damaged in the night")


def close_round(w, name, did, rec) -> None:
    """Move this round's experience into memory: the full band, and a one-line summary for the summary band."""
    if name not in w.s["know"]:
        return
    rnd = rec["round"]
    k = store(w, name)
    k["full"].append({"round": rnd, "did": did, "seen": [dict(x) for x in k["seen"]], "heard": list(k["heard"])})
    a = w.s["agents"][name]
    ate = rec["ate"].get(name, 0.0)
    meal = ("went without" if name in rec["missed"] else f"short of food (ate {ate:g})" if name in rec["short"] else f"ate {ate:g}")
    acts = [d.split(":")[0] + ": " + d.split(":")[1].strip() if d.startswith("Refused") else d for d in did if not d.startswith(("You ate", "You could not"))]
    k["rounds"].append({"round": rnd, "line": f"slept at {w.place(a['at'])}; {meal}; " + " / ".join(x.rstrip('.') for x in acts[:6])})
    del k["rounds"][:-SUMMARY_ROUNDS - FULL_ROUNDS]
    del k["full"][:-FULL_ROUNDS]
    k["seen"], k["heard"] = [], []


def age(w, rnd) -> str:
    d = w.r - rnd
    return "this round" if d <= 0 else "last round" if d == 1 else f"{d} rounds ago"
