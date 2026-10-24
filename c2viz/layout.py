"""Layouts for the map (presentation only; agents never see them; docs/cybertron2/spec/record/views.md).

The world has no coordinates (world/parcel_graph.md): nodes are joined by roads measured in days, and a node's parcels are a graph
of neighbours, each with a side (centre, north, east, south, west) and a height (0 water and low ground .. 3 hilltops). So:

- `world_layout`: node positions from the road graph, distances in days (stress layout, seeded, deterministic), fitted to a
  1000 x 700 box.
- `node_layout`: parcel sites from side (a compass direction), spread within a side, relaxed along adjacency; then cells as a
  power diagram (a Voronoi diagram weighted by parcel size) clipped to a rounded outline; lots inside each cell for buildings; where
  each road leaves the node.

Pure Python, no dependencies; the same input always gives the same layout.
"""
from __future__ import annotations

import heapq
import math
import random

W, H = 1000.0, 700.0
SIDE = {"centre": (0.0, 0.0), "north": (0.0, -1.0), "south": (0.0, 1.0), "east": (1.0, 0.0), "west": (-1.0, 0.0)}


# ---------------------------------------------------------------------------------------------------------------- the world
def _days(nodes, roads):
    """All-pairs shortest travel days (Dijkstra from each node)."""
    adj = {n: [] for n in nodes}
    for r in roads.values():
        if r["a"] in adj and r["b"] in adj:
            d = float(r.get("days") or 1)
            adj[r["a"]].append((r["b"], d))
            adj[r["b"]].append((r["a"], d))
    out = {}
    for s in nodes:
        dist = {s: 0.0}
        q = [(0.0, s)]
        while q:
            d, u = heapq.heappop(q)
            if d > dist.get(u, 1e18):
                continue
            for v, w in adj[u]:
                if d + w < dist.get(v, 1e18):
                    dist[v] = d + w
                    heapq.heappush(q, (d + w, v))
        out[s] = dist
    return out


def world_layout(nodes, roads, seed=1) -> dict:
    ids = sorted(nodes)
    n = len(ids)
    if n == 0:
        return {}
    if n == 1:
        return {ids[0]: [W / 2, H / 2]}
    D = _days(ids, roads)
    far = max((d for row in D.values() for d in row.values()), default=1.0) + 1.0
    dist = {(a, b): D[a].get(b, far) for a in ids for b in ids}
    rng = random.Random(f"{seed}|c2viz|world")
    pos = {a: [math.cos(2 * math.pi * i / n) + rng.uniform(-.05, .05), math.sin(2 * math.pi * i / n) + rng.uniform(-.05, .05)]
           for i, a in enumerate(ids)}
    scale = far / 2.0
    for a in ids:
        pos[a] = [pos[a][0] * scale, pos[a][1] * scale]
    for it in range(600):                                          # stress majorisation by gradient steps, cooling
        step = 0.1 * (1 - it / 600) + 0.01
        for a in ids:
            gx = gy = 0.0
            for b in ids:
                if a == b:
                    continue
                dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
                cur = math.hypot(dx, dy) or 1e-6
                want = dist[(a, b)]
                wgt = 1.0 / (want * want)
                gx += wgt * (cur - want) * dx / cur
                gy += wgt * (cur - want) * dy / cur
            pos[a][0] -= step * gx * far
            pos[a][1] -= step * gy * far
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    if max(ys) - min(ys) > max(xs) - min(xs):                      # landscape: the long axis across
        pos = {a: [p[1], p[0]] for a, p in pos.items()}
        xs, ys = ys, xs
    m = 110.0
    sx = (W - 2 * m) / max(1e-6, max(xs) - min(xs))
    sy = (H - 2 * m) / max(1e-6, max(ys) - min(ys))
    s = min(sx, sy)
    ox = (W - s * (max(xs) - min(xs))) / 2 - s * min(xs)
    oy = (H - s * (max(ys) - min(ys))) / 2 - s * min(ys)
    return {a: [round(ox + s * p[0], 1), round(oy + s * p[1], 1)] for a, p in pos.items()}


# ---------------------------------------------------------------------------------------------------------------- a node
def _clip(poly, a, b, c):
    """The part of a polygon where a*x + b*y <= c (Sutherland-Hodgman against one half-plane)."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fp <= 0:
            out.append(p)
        if (fp < 0 < fq) or (fq < 0 < fp):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def _area(poly):
    return abs(sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1] for i in range(len(poly)))) / 2


def _centroid(poly):
    a = cx = cy = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i - 1]
        x1, y1 = poly[i]
        f = x0 * y1 - x1 * y0
        a += f
        cx += (x0 + x1) * f
        cy += (y0 + y1) * f
    if abs(a) < 1e-9:
        return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
    return (cx / (3 * a), cy / (3 * a))


def _inside(poly, x, y):
    c = False
    for i in range(len(poly)):
        x0, y0 = poly[i - 1]
        x1, y1 = poly[i]
        if (y1 > y) != (y0 > y) and x < (x0 - x1) * (y - y1) / ((y0 - y1) or 1e-12) + x1:
            c = not c
    return c


def node_layout(nid, parcels, roads, seed=1, w=W, h=H) -> dict:
    """{cells: {pid: [[x,y],..]}, centre: {pid: [x,y]}, lots: {pid: [[x,y],..]}, outline: [[x,y],..], exits: {road: {...}}}."""
    mine = {pid: p for pid, p in parcels.items() if p["node"] == nid}
    ids = sorted(mine)
    if not ids:
        return {"cells": {}, "centre": {}, "lots": {}, "outline": [], "exits": {}}
    rng = random.Random(f"{seed}|c2viz|node|{nid}")
    by_side = {}
    for pid in ids:
        by_side.setdefault(mine[pid].get("side") or "centre", []).append(pid)
    pos = {}
    for side, ps in by_side.items():
        dx, dy = SIDE.get(side, (0.0, 0.0))
        for k, pid in enumerate(ps):
            off = (k - (len(ps) - 1) / 2) * 0.55
            if side == "centre":
                ang = 2 * math.pi * k / max(1, len(ps))
                pos[pid] = [0.35 * math.cos(ang) * (len(ps) > 1), 0.35 * math.sin(ang) * (len(ps) > 1)]
            else:
                pos[pid] = [dx + (-dy) * off + rng.uniform(-.05, .05), dy + dx * off + rng.uniform(-.05, .05)]
    anchor = {pid: list(pos[pid]) for pid in ids}
    adj = {pid: [q for q in (mine[pid].get("adj") or []) if q in mine] for pid in ids}
    for it in range(300):                                          # springs on neighbours, repulsion, a pull to the side
        f = {pid: [0.0, 0.0] for pid in ids}
        for a in ids:
            for b in ids:
                if a >= b:
                    continue
                dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
                d = math.hypot(dx, dy) or 1e-6
                rep = 0.06 / (d * d)
                f[a][0] += rep * dx / d
                f[a][1] += rep * dy / d
                f[b][0] -= rep * dx / d
                f[b][1] -= rep * dy / d
            for b in adj[a]:
                dx, dy = pos[b][0] - pos[a][0], pos[b][1] - pos[a][1]
                d = math.hypot(dx, dy) or 1e-6
                k = 0.08 * (d - 0.7)
                f[a][0] += k * dx / d
                f[a][1] += k * dy / d
            f[a][0] += 0.12 * (anchor[a][0] - pos[a][0])
            f[a][1] += 0.12 * (anchor[a][1] - pos[a][1])
        for a in ids:
            pos[a][0] += max(-.1, min(.1, f[a][0]))
            pos[a][1] += max(-.1, min(.1, f[a][1]))
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
    R = min(w, h) * 0.40
    S = (R * 1.45) / span
    P = {pid: (w / 2 + (pos[pid][0] - cx) * S, h / 2 + (pos[pid][1] - cy) * S) for pid in ids}
    rx, ry = w * 0.46, h * 0.44                                    # the node's outline: a wobbly ellipse
    outline = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        wob = 1 + 0.05 * math.sin(3 * t + rng.uniform(0, 6.28)) + 0.03 * math.sin(7 * t)
        outline.append((w / 2 + rx * wob * math.cos(t), h / 2 + ry * wob * math.sin(t)))
    weight = {pid: (float(mine[pid].get("size") or 1) ** 0.5) * 900.0 for pid in ids}
    cells = {}
    for a in ids:
        poly = list(outline)
        ax, ay = P[a]
        for b in ids:
            if a == b:
                continue
            bx, by = P[b]
            # power bisector: |x-a|^2 - wa <= |x-b|^2 - wb  ->  2(b-a).x <= |b|^2 - |a|^2 - wb + wa
            c = (bx * bx + by * by) - (ax * ax + ay * ay) - weight[b] + weight[a]
            poly = _clip(poly, 2 * (bx - ax), 2 * (by - ay), c)
            if not poly:
                break
        cells[a] = poly
    centre, lots, label = {}, {}, {}
    for pid, poly in cells.items():
        if len(poly) < 3:
            centre[pid] = list(P[pid])
            lots[pid] = []
            label[pid] = list(P[pid])
            continue
        c = _centroid(poly)
        centre[pid] = [round(c[0], 1), round(c[1], 1)]
        pts = []
        step = max(18.0, math.sqrt(_area(poly)) / 5)
        x0, x1 = min(p[0] for p in poly), max(p[0] for p in poly)
        y0, y1 = min(p[1] for p in poly), max(p[1] for p in poly)
        y = y0 + step / 2
        while y < y1:
            x = x0 + step / 2
            while x < x1:
                if _inside(poly, x, y) and all(_inside(poly, x + dx, y + dy) for dx, dy in ((12, 0), (-12, 0), (0, 12), (0, -12))):
                    pts.append((x, y))
                x += step
            y += step
        pts.sort(key=lambda p: (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2)  # lots nearest the middle first
        ly = y0 + 0.2 * (y1 - y0) + 10
        lx = c[0]
        if not _inside(poly, lx, ly):
            ly = c[1] - 0.25 * (c[1] - y0)
        label[pid] = [round(lx, 1), round(ly, 1)]
        lots[pid] = [[round(x, 1), round(y, 1)] for x, y in pts[:24]]
    exits = {}
    for rid, r in sorted(roads.items()):
        if nid not in (r["a"], r["b"]):
            continue
        end = (r.get("ends") or {}).get(nid) or {}
        other = r["b"] if r["a"] == nid else r["a"]
        dx, dy = SIDE.get(end.get("side") or "centre", (0.0, 0.0))
        if (dx, dy) == (0.0, 0.0):                                  # a road from the middle: aim it at the other node later
            dx, dy = 0.0, 0.0
        ps = [p for p in end.get("parcels") or [] if p in centre]
        exits[rid] = {"to": other, "side": end.get("side") or "centre", "parcels": ps, "dir": [dx, dy],
                      "from": centre[ps[0]] if ps else [w / 2, h / 2], "hidden": bool(end.get("hidden"))}
    rnd = lambda poly: [[round(x, 1), round(y, 1)] for x, y in poly]
    return {"cells": {k: rnd(v) for k, v in cells.items()}, "centre": centre, "lots": lots, "label": label, "outline": rnd(outline),
            "exits": exits}
