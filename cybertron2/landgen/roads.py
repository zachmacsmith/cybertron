"""Roads (stage 1 §5, §11f; D2-182): least-cost routes over the cells between neighbouring places, each about a day; a stopping
place on any road of more than a day and a half; wild nodes for large wild areas half a day out (D2-181); landmarks where a road
crosses a feature; hidden ways where a short way through cover joins places no road joins (D2-90, D2-92).

Travel is in hours: a cell's crossing time is its size over the pace of its cover, slowed by slope (stage 1 §11f); the sea, lakes
and large rivers cannot be crossed except a large river at a ford (a broad flat reach)."""
from __future__ import annotations

import heapq
import math

import numpy as np

from cybertron2.landgen import ecology as EC
from cybertron2.landgen import field as F, keyed, physical as P, vocab as V
from cybertron2.landgen.physical import Land
from cybertron2.landgen.settle import Parcel, Settlement


def cover_map(L: Land, settlements: list) -> np.ndarray:
    cov = L.cover.copy()
    for s in settlements:
        for p in s.parcels:
            for rc in p.cells:
                cov[rc] = p.cover
    return cov


def fords(L: Land) -> set:
    """Fords on large rivers: broad flat reaches, at least 6 km apart, chosen by keyed draws."""
    cells = list(zip(*np.nonzero((L.river >= 3) & ~L.lake)))
    rg = keyed.rng(L.g.seed, "fords")
    rg.shuffle(cells)
    flat = F.box_mean(L.slope, 3)
    out = []
    for r, c in cells:
        if flat[r, c] < 2.0 and all(math.hypot(L.g.x[r, c] - L.g.x[a], L.g.y[r, c] - L.g.y[a]) > 6.0 for a in out):
            out.append((r, c))
    return set(out)


def hours_grid(L: Land, cov: np.ndarray, ford: set) -> np.ndarray:
    g = L.g
    pace = np.vectorize(lambda k: V.PACE_KMH.get(k, 2.5))(cov)
    h = g.km / pace * (1 + L.slope / 10.0)
    h = h + np.where(L.river == 1, 0.1, 0.0) + np.where(L.river == 2, 0.3, 0.0)
    block = L.sea | L.lake | (L.river >= 3)
    for rc in ford:
        block[rc] = False
        h[rc] += 0.3
    return np.where(block, np.inf, h)


def dijkstra(L: Land, H: np.ndarray, src, limit: float):
    """Hours from src to every cell within `limit` hours, and each cell's predecessor."""
    g = L.g
    dist = np.full(g.shape, np.inf)
    prev = {}
    dist[src] = 0.0
    heap = [(0.0, src)]
    while heap:
        t, (r, c) = heapq.heappop(heap)
        if t > dist[r, c] or t > limit:
            continue
        for (dr, dc), d in zip(F.N8, F.D8):
            rr, cc = r + dr, c + dc
            if 0 <= rr < g.ny and 0 <= cc < g.nx:
                nt = t + d * 0.5 * (H[r, c] + H[rr, cc])
                if nt < dist[rr, cc]:
                    dist[rr, cc] = nt
                    prev[(rr, cc)] = (r, c)
                    heapq.heappush(heap, (nt, (rr, cc)))
    return dist, prev


def path_to(prev, src, dst) -> list:
    out = [dst]
    while out[-1] != src:
        out.append(prev[out[-1]])
    return out[::-1]


def _wild_parcels(L: Land, key: str, cells: list, kind: str) -> list:
    """A wild node's parcels: a way in (a clearing or the scar's foot) and the wild itself (old forest, or rock with a seam)."""
    ps = []
    if kind == "forest":
        r, c = cells[0]
        terr = P.TERRAIN_NAMES[int(L.terrain[r, c])]
        ecos = [L.eco[rc] for rc in cells[1:7] if L.eco[rc] in EC.FORESTS] or ["oak-ash wood"]
        ps.append(Parcel(f"{key}_0", "wild", "meadow", cells[:1], size=1, side="south", height=1, terrain=terr, soil="loam",
                         eco="grassland"))
        ps.append(Parcel(f"{key}_1", "wild", "forest", cells[1:7], size=min(6, max(3, len(cells) - 1)), side="centre", height=2,
                         terrain=terr, soil="loam", wood_kind="old forest", eco=max(set(ecos), key=ecos.count), band=3))
    else:
        ps.append(Parcel(f"{key}_0", "wild", "rock", cells[:2], size=2, side="centre", height=3, terrain="hills", soil="loam"))
        ps.append(Parcel(f"{key}_1", "wild", "scrub", cells[2:4], size=2, side="south", height=2, terrain="hills", soil="loam",
                         wood_kind="scrub"))
    ps[0].adj, ps[1].adj = [ps[1].pid], [ps[0].pid]
    for p in ps:
        p.facts = {"terrain": p.terrain}
    return ps


def wild_nodes(L: Land, conf: dict, settlements: list, H: np.ndarray, dists: dict) -> list:
    """Large wild areas (deep forest; hills) at least half a day from every settlement get a node at their most reachable cell,
    at most two of each kind."""
    g = L.g
    near = np.minimum.reduce([d for d in dists.values()]) if dists else np.full(g.shape, np.inf)
    out = []
    taken = np.zeros(g.shape, dtype=bool)
    for kind, mask in (("forest", L.band == 3),                         # deep forest: the core of a large wood (ecology.depth)
                       ("hills", np.isin(L.terrain, [P.TERRAIN_NAMES.index("hills"), P.TERRAIN_NAMES.index("upland pasture")]))):
        big = F.box_mean(mask.astype(float), 10) > 0.6                     # the heart of a large area
        if kind == "hills" and L.ore.any():                                # hill country is entered where its ore is
            ore_near = F.box_mean(L.ore.astype(float), 6) > 0.02
            big = big & ore_near if (big & ore_near).any() else big
        cand = big & np.isfinite(near) & (near >= conf["wild_node_hours"]) & (near <= 2.2 * conf["road_day_hours"]) & ~taken
        n = 0
        while cand.any() and n < conf["wild_nodes"] and len(out) < conf["wild_nodes"] * 2:
            idx = np.argmin(np.where(cand, near, np.inf))
            r, c = divmod(int(idx), g.nx)
            area = float(F.box_mean(mask.astype(float), 10)[r, c]) * (21 * g.km) ** 2
            if area < conf["wild_node_km2"] * 0.3:
                break
            key = f"w{len(out) + 1}"
            cells = [(r, c)] + [(r + dr, c + dc) for dr, dc in F.N8 if 0 <= r + dr < g.ny and 0 <= c + dc < g.nx][:7]
            s = Settlement(key, (r, c), {}, 0, 0, {}, kind="wild")
            s.parcels = _wild_parcels(L, key, cells, kind)
            s.facts = {"wild": kind, "seam": kind == "hills" and bool(L.ore[max(0, r - 6):r + 7, max(0, c - 6):c + 7].any())}
            out.append(s)
            taken |= np.hypot(g.x - g.x[r, c], g.y - g.y[r, c]) < 8.0
            cand &= ~taken
            n += 1
    return out


def _stop(L: Land, key: str, path: list, hrs: list) -> Settlement:
    """A stopping place on a long road (D2-182): at the path's middle by time, by a spring or a meadow if one is near."""
    half = hrs[-1] / 2
    i = min(range(len(path)), key=lambda i: abs(hrs[i] - half))
    lo, hi = max(0, i - 15), min(len(path), i + 16)
    best = max(range(lo, hi), key=lambda j: (L.spring[path[j]] * 2 + (L.cover[path[j]] in ("meadow", "pasture")) - abs(j - i) * 0.05))
    r, c = path[best]
    s = Settlement(key, (r, c), {}, 0, 0, {}, kind="stop")
    p = Parcel(f"{key}_0", "wild", "meadow", [(r, c)], size=1, side="centre", height=1, terrain=L.tname(r, c), soil="loam")
    p.facts = {"terrain": p.terrain, "spring": bool(L.spring[r, c])}
    s.parcels = [p]
    s.facts = {"stop": True, "spring": bool(L.spring[r, c])}
    return s


def landmarks(L: Land, cells: list) -> list:
    """What a stretch crosses (data.LANDMARKS), at most two (D2-104)."""
    out = []
    hs = [float(L.h[rc]) for rc in cells]
    if any(L.river[rc] >= 2 for rc in cells):
        out.append("ford")
    if hs and max(hs) - min(hs[0], hs[-1]) >= V.PASS_M:
        out.append("pass")
    steep = [rc for rc in cells if L.slope[rc] >= V.NARROWS_DEG]
    if len(steep) >= 3 and "pass" not in out:
        out.append("narrows")
    mid = cells[len(cells) // 3: 2 * len(cells) // 3] or cells
    if len(out) < 2 and any(L.spring[rc] for rc in mid):                   # a spring on the way, where one would stop
        out.append("spring")
    if len(out) < 2 and sum(L.cover[rc] == "meadow" for rc in mid) >= 3:
        out.append("meadow")
    return out[:2]


def _terrain(L: Land, cov, cells: list) -> str:
    if max(float(L.h[rc]) for rc in cells) >= 600:
        return "mountain"
    by_river = sum(any(0 <= rc[0] + dr < L.g.ny and 0 <= rc[1] + dc < L.g.nx and L.river[rc[0] + dr, rc[1] + dc] >= 2
                       for dr, dc in F.N8) for rc in cells)
    if by_river >= 0.3 * len(cells):
        return "river valley"
    if np.mean([L.slope[rc] for rc in cells]) > 6:
        return "hills"
    kinds = [V.ROAD_TERRAIN.get(cov[rc], "plain") for rc in cells]
    return max(set(kinds), key=kinds.count)


def _end(s: Settlement, path: list, from_start: bool) -> dict:
    """The parcel a road leaves a settlement by: the last of its parcels the path passes on the way out."""
    owner = {rc: p for p in s.parcels for rc in p.cells}
    walk = path if from_start else path[::-1]
    last = s.parcels[0]
    for rc in walk:
        if rc in owner:
            last = owner[rc]
        elif any((rc[0] + dr, rc[1] + dc) in owner for dr, dc in F.N8):
            continue
        else:
            break
    return {"parcels": [last.pid], "side": last.side if last.side != "centre" else "north"}


WAY = {"farmland": "the track between the fields", "woodland": "the path under the trees", "plain": "the open road",
       "marsh": "the causeway through the wet", "hills": "the hill road", "mountain": "the high road", "river valley": "the valley road"}


def build(L: Land, conf: dict, settlements: list) -> tuple[list, list, dict]:
    """Roads, stopping places and wild nodes. Returns (the new nodes, the roads in the world file's form, the cells of each road
    for the picture)."""
    cov = cover_map(L, settlements)
    ford = fords(L)
    H = hours_grid(L, cov, ford)
    day = conf["road_day_hours"]
    nodes = {s.key: s for s in settlements}
    reach = {}
    for s in settlements:
        reach[s.key] = dijkstra(L, H, s.site, 3.2 * day)
    wild = wild_nodes(L, conf, settlements, H, {k: d for k, (d, _) in reach.items()})
    for w in wild:
        nodes[w.key] = w
        reach[w.key] = dijkstra(L, H, w.site, 3.2 * day)
    keys = [s.key for s in settlements]
    t = lambda a, b: float(reach[a][0][nodes[b].site])
    # a tree joining the settlements by the shortest roads, then extra roads where a direct one is much shorter than the tree's way
    edges, inside = [], {keys[0]} if keys else set()
    while len(inside) < len(keys):
        best = min(((a, b) for a in inside for b in keys if b not in inside), key=lambda ab: t(*ab))
        if not math.isfinite(t(*best)):
            break                                                          # unreachable by land: the reachability check says so
        edges.append(best)
        inside.add(best[1])

    def via(a, b, es):
        adj = {}
        for x, y in es:
            adj.setdefault(x, []).append(y)
            adj.setdefault(y, []).append(x)
        best = {a: 0.0}
        heap = [(0.0, a)]
        while heap:
            d, x = heapq.heappop(heap)
            for y in adj.get(x, []):
                nd = d + t(x, y)
                if nd < best.get(y, math.inf):
                    best[y] = nd
                    heapq.heappush(heap, (nd, y))
        return best.get(b, math.inf)

    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if (a, b) in edges or (b, a) in edges or t(a, b) > 1.6 * day:
                continue
            if t(a, b) < 0.75 * via(a, b, edges):
                edges.append((a, b))
    for w in wild:                                                         # a wild node joins its nearest settlement
        b = min(keys, key=lambda k: t(w.key, k))
        if math.isfinite(t(w.key, b)):
            edges.append((b, w.key))
    roads, cells_of, stops = [], [], []
    todo = list(edges)
    while todo:
        a, b = todo.pop(0)
        dist, prev = reach[a]
        path = path_to(prev, nodes[a].site, nodes[b].site)
        hrs = [float(dist[rc]) for rc in path]
        total = hrs[-1]
        if total > 1.5 * day and nodes[b].kind != "wild":
            st = _stop(L, f"t{len(stops) + 1}", path, hrs)
            stops.append(st)
            nodes[st.key] = st
            reach[st.key] = dijkstra(L, H, st.site, 3.2 * day)
            todo += [(a, st.key), (st.key, b)]
            continue
        days = max(1, int(round(total / day)))
        cells_of.append(path)
        per = []
        for k in range(days):
            lo, hi = total * k / days, total * (k + 1) / days
            per.append([rc for rc, h in zip(path, hrs) if lo <= h <= hi] or path[:1])
        stretches = {}
        for k, cs in enumerate(per):
            lm = landmarks(L, cs)
            if lm:
                stretches[k + 1] = {"landmarks": lm}
        terr = _terrain(L, cov, path)
        ends = {a: _end(nodes[a], path, True), b: _end(nodes[b], path, False)}
        extra = {"terrain": terr, "way": WAY.get(terr, "the road"), "ends": ends}
        if stretches:
            extra["stretches"] = stretches
        roads.append([a, b, days, extra])
    # hidden ways: short ways through cover between places no road joins directly (D2-90, D2-92)
    joined = {frozenset((r[0], r[1])) for r in roads}
    allk = [k for k in nodes if nodes[k].kind != "stop"]
    for i, a in enumerate(allk):
        for b in allk[i + 1:]:
            if frozenset((a, b)) in joined or a not in reach:
                continue
            d = float(reach[a][0][nodes[b].site])
            if not math.isfinite(d) or d > 1.2 * day:
                continue
            path = path_to(reach[a][1], nodes[a].site, nodes[b].site)
            covered = sum(cov[rc] in ("forest", "scrub", "heath", "moor") for rc in path) / len(path)
            if covered >= 0.5:
                ends = {a: {**_end(nodes[a], path, True), "hidden": True}, b: {**_end(nodes[b], path, False), "hidden": True}}
                roads.append([a, b, max(1, int(round(d / day))), {"terrain": _terrain(L, cov, path), "way": "a way through the cover",
                                                                   "ends": ends}])
                cells_of.append(path)
                joined.add(frozenset((a, b)))
    return wild + stops, roads, {"road_cells": cells_of, "fords": sorted(ford)}
