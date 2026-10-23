"""The parcel graph inside a node (world/parcel_graph.md; D2-114 to D2-116).

A node's parcels are a graph of neighbours (each parcel's `adj`, two-way), each with a side (centre, north, east, south, west) and a
height (0 the river and low wet ground, 1 the valley floor, 2 slopes, 3 hilltops). No coordinates and no movement inside a node:
distance is steps on the graph. What it is read for: the parcels one passes through between where one slept and where one worked
(presence 0.3 for the noticing rule) and the ones next door (0.1); where a road leaves the node (a side and parcels, D2-90); what
herds wander across (farm.py); the village's layout when one attends to it and a short overview on arriving.

Engine side: agents see it only through `Here` (layout lines, the overview).
"""
from __future__ import annotations

from collections import deque

from cybertron2.engine.data import COVERS, LAYOUT

SIDES = ("centre", "north", "east", "south", "west")


def side(w, pid) -> str:
    return w.s["parcels"][pid].get("side") or "centre"


def height(w, pid) -> int:
    return int(w.s["parcels"][pid].get("height", 1))


def parcels_of(w, node) -> list:
    return sorted(pid for pid, p in w.s["parcels"].items() if p["node"] == node)


# ---------------------------------------------------------------------- distance and the way between (D2-114, D2-115)
def _layers(w, a) -> dict:
    """Steps from parcel a to every parcel it reaches."""
    dist = {a: 0}
    q = deque([a])
    while q:
        x = q.popleft()
        for y in w.s["parcels"][x]["adj"]:
            if y not in dist and y in w.s["parcels"]:
                dist[y] = dist[x] + 1
                q.append(y)
    return dist


def steps(w, a, b):
    """The number of steps between two parcels, or None if the land gives no way between them."""
    return _layers(w, a).get(b)


def path(w, a, b, key=()) -> list:
    """A shortest way from a to b, both ends included ([] if none); ties between shortest ways broken by a keyed draw (D2-70)."""
    if a == b:
        return [a]
    dist = _layers(w, a)
    if b not in dist:
        return []
    out = [b]
    rng = w.rng("way", w.d, a, b, *key)
    while out[-1] != a:
        x = out[-1]
        prev = sorted(y for y in w.s["parcels"][x]["adj"] if dist.get(y) == dist[x] - 1)
        out.append(prev[int(rng.random() * len(prev))])
    return out[::-1]


def slept_at(w, name):
    """The parcel one set out from this morning: one's house at this node, else the node's built ground."""
    node = w.at(name)
    if node is None:
        return None
    homes = [b for b in w.homes(name) if w.s["buildings"][b]["node"] == node]
    if homes:
        return w.s["buildings"][homes[0]]["parcel"]
    built = [pid for pid in parcels_of(w, node) if w.s["parcels"][pid]["cover"] == "built"]
    return built[0] if built else None


def worked_parcels(w, name) -> list:
    out = []
    for key in (w.s.get("today") or {}).get("worked", {}).get(name, []):
        pid = key if key in w.s["parcels"] else (w.s["buildings"][key]["parcel"] if key in w.s["buildings"] else None)
        if pid and pid not in out:
            out.append(pid)
    return out


def passed(w, name) -> set:
    """The parcels one crossed today: on the way from where one slept to each parcel one worked, and back (D2-115); not the worked
    parcels themselves."""
    start = slept_at(w, name)
    work = worked_parcels(w, name)
    if start is None or not work:
        return set()
    out = set()
    for pid in work:
        out |= set(path(w, start, pid, (name,)))
    return out - set(work)


def next_door(w, name) -> set:
    """The parcels next to where one worked today (D2-115)."""
    work = set(worked_parcels(w, name))
    return {y for pid in work for y in w.s["parcels"][pid]["adj"] if y in w.s["parcels"]} - work


# ---------------------------------------------------------------------- road ends (D2-90)
def road_ends(w, node) -> list:
    """[(road id, other node, end)] for the roads leaving this node; end = {side, parcels, hidden, ...}."""
    out = []
    for rid, r in sorted(w.s["roads"].items()):
        if node in (r["a"], r["b"]):
            out.append((rid, r["b"] if r["a"] == node else r["a"], (r.get("ends") or {}).get(node) or default_end(w, node)))
    return out


def default_end(w, node) -> dict:
    built = [pid for pid in parcels_of(w, node) if w.s["parcels"][pid]["cover"] == "built"] or parcels_of(w, node)[:1]
    return {"side": side(w, built[0]) if built else "centre", "parcels": built[:1], "hidden": False}


def build_ends(w, extra, a, b) -> dict:
    """A road's two ends from its spec (`ends: {node: {side, parcels, hidden}}`), defaulting to each node's built ground."""
    given = extra.get("ends") or {}
    out = {}
    for node in (a, b):
        g = given.get(node) or {}
        d = default_end(w, node)
        ps = [p for p in (g.get("parcels") or ([g["parcel"]] if g.get("parcel") else d["parcels"])) if p in w.s["parcels"]]
        out[node] = {"side": g.get("side") or (side(w, ps[0]) if ps else d["side"]), "parcels": ps, "hidden": bool(g.get("hidden")),
                     "worn": 0.0, "used": None}
    return out


# ---------------------------------------------------------------------- words (D2-116)
def side_words(s) -> str:
    return "in the middle" if s == "centre" else f"on the {s} side"


def height_words(h) -> str:
    return LAYOUT["height"][max(0, min(3, int(h)))]


def layout_lines(w, name) -> list:
    """How the village fits together, in words: each parcel with its neighbours, side and height, and where the roads leave."""
    node = w.at(name)
    out = []
    names = {pid: w.s["parcels"][pid]["name"] for pid in parcels_of(w, node)}
    for pid in sorted(names, key=lambda p: (height(w, p), SIDES.index(side(w, p)) if side(w, p) in SIDES else 0, names[p])):
        p = w.s["parcels"][pid]
        nb = [names[x] for x in p["adj"] if x in names]
        what = COVERS.get(p["cover"], {}).get("words", p["cover"])
        where = [side_words(side(w, pid))] if side(w, pid) != "centre" else []
        where += [height_words(height(w, pid))] if height(w, pid) != 1 else []      # a world that sets none: no words for them
        out.append(f"{names[pid]} ({what})" + (" lies " + ", ".join(where) if where else "")
                   + (f"; next to {_and(nb)}" if nb else "; set apart from the rest"))
    for rid, other, end in road_ends(w, node):
        if end.get("hidden") and rid not in ((w.s["mind"].get(name) or {}).get("ways") or {}):
            continue
        where = _and([names.get(p, p) for p in end["parcels"]]) or "the village"
        to = w.s["nodes"][other]["name"] if w.knows_place(name, other) else w.s["roads"][rid].get("way", "an unexplored way")
        out.append(f"the way to {to} leaves from {where}" + (f", {side_words(end['side'])}" if end["side"] != "centre" else ""))
    return out


def overview(w, node) -> list:
    """What strikes one first on arriving: 3 to 5 lines, the largest and busiest things, not positions (D2-116)."""
    cands = []
    for bid, b in w.s["buildings"].items():
        if b["node"] != node or b.get("unfinished"):
            continue
        fit = [f for f in b["fittings"] if f in LAYOUT["seen"]]
        if fit:
            cands.append((3.0, f"{LAYOUT['seen'][fit[0]]} at {w.s['parcels'][b['parcel']]['name']}"))
        if b.get("fire"):
            cands.append((1.5, f"smoke from {b['name']}"))
    for pid in parcels_of(w, node):
        p = w.s["parcels"][pid]
        houses = [b for b in w.s["buildings"].values() if b["parcel"] == pid and not b.get("unfinished")]
        if p["cover"] == "built" and houses:
            cands.append((2.5 + 0.1 * len(houses), f"{p['name']}, with {_count(len(houses), 'house')}"))
        c = p.get("crop")
        if c and c.get("area_left", 0) > 1e-6:
            stage = "ripe" if w.d >= int(c.get("ripe_day", 10 ** 9)) else ("green" if w.d - int(c.get("sown", w.d)) > 3 else "new sown")
            cands.append((1.0 + 0.2 * p["size"] + (1.0 if stage == "ripe" else 0.0), f"{c.get('kind', 'a crop')} {stage} on {p['name']}"))
        elif p["cover"] in ("forest", "water", "rock") and p["size"] >= 2:
            cands.append((0.8 + 0.1 * p["size"], f"{COVERS[p['cover']]['words']}: {p['name']}"))
    for hid, h in w.s["herds"].items():
        if h["node"] == node and h.get("parcel") and int(h.get("count", 0)) > 0:
            cands.append((1.2 + 0.05 * int(h["count"]), f"{_count(int(h['count']), h.get('kind', 'cattle'))} on {w.s['parcels'][h['parcel']]['name']}"))
    cands.sort(key=lambda x: -x[0])
    lines = list(dict.fromkeys(t for _, t in cands))
    lo, hi = LAYOUT["overview"]
    return lines[:hi] if len(lines) >= lo else lines


def _count(n, word) -> str:
    if word == "cattle":
        return f"{n} head of cattle"
    return f"{n} {word}{'s' if n != 1 and not word.endswith('s') else ''}"


def _and(xs) -> str:
    xs = list(xs)
    return xs[0] if len(xs) == 1 else (", ".join(xs[:-1]) + " and " + xs[-1]) if xs else ""
