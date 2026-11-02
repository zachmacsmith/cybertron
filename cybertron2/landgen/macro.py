"""The land's large shapes: primitives composed in order, and the named configurations built from them (D2-178, D2-188; stage 1
§1b, §11d, §11k). A primitive is a dict with a kind, a name and its parameters in window fractions (0 to 1 across, 0 south to 1
north). Composing gives fields the physical layers start from, and the anchors (named points) that pins may use:
"Ashby: {at: north_bay.head}"."""
from __future__ import annotations

import numpy as np

from cybertron2.landgen import field as F, vocab as V
from cybertron2.landgen.field import Grid

SIDES = {"west": (1.0, 0.0), "east": (-1.0, 0.0), "south": (0.0, 1.0), "north": (0.0, -1.0)}   # inward normals


def _seg_dist(px, py, a, b):
    """Distance (fractions) from points to segment ab, and where along it (0 to 1)."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1e-9
    t = np.clip(((px - ax) * dx + (py - ay) * dy) / L2, 0, 1)
    return np.hypot(px - (ax + t * dx), py - (ay + t * dy)), t


def _poly_dist(px, py, pts):
    best, along = np.full(px.shape, np.inf), np.zeros(px.shape)
    lens = [np.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    tot, acc = sum(lens) or 1e-9, 0.0
    for (a, b), L in zip(zip(pts, pts[1:]), lens):
        d, t = _seg_dist(px, py, a, b)
        closer = d < best
        best = np.where(closer, d, best)
        along = np.where(closer, (acc + t * L) / tot, along)
        acc += L
    return best, along


def _bump(d, w):
    return np.exp(-0.5 * (d / max(w, 1e-6)) ** 2)


SYSTEMS = ("river country", "scarp and vale", "sand country", "upland", "fen", "coast", "wildwood")   # temperate_landscapes.md §2


def _ragged(g, key, d, r, amount=0.35):
    """A distance stretched by noise, so a shape's edge is irregular, not a circle (G-34): features at about the shape's own size
    and a third of it."""
    sc = max(r * g.size_km, 1.0)
    n = 0.7 * F.fbm(g.seed, f"ragged-{key}", g.x, g.y, sc * 0.9, octaves=3) + 0.3 * F.fbm(g.seed, f"ragged2-{key}", g.x, g.y, sc * 0.3, octaves=3)
    return d / np.clip(1 + amount * n, 0.4, None)


def _inbox(g, key, px, py, box, amount=0.03):
    """Inside a box whose edges wander (noise at two scales), so a frontier or a geology belt never ends in a ruled line."""
    x0, y0, x1, y1 = box
    n = amount * (F.fbm(g.seed, f"box-{key}", g.x, g.y, 6.0, octaves=4) + 0.5 * F.fbm(g.seed, f"box2-{key}", g.x, g.y, 2.0, octaves=3))
    m = amount * (F.fbm(g.seed, f"boy-{key}", g.x, g.y, 6.0, octaves=4) + 0.5 * F.fbm(g.seed, f"boy2-{key}", g.x, g.y, 2.0, octaves=3))
    qx, qy = px + n, py + m
    return (qx >= x0) & (qx <= x1) & (qy >= y0) & (qy <= y1)


def _meander(g, key, pts, flow):
    """A laid river's course: its anchor points kept, bends between them (noise along the course, across it), more for a bigger
    river; returns points in window fractions."""
    amp = {"large": 0.022, "medium": 0.016}.get(flow, 0.011)
    out = []
    for k, (a, b) in enumerate(zip(pts, pts[1:])):
        (ax, ay), (bx, by) = a, b
        L_ = max(np.hypot(bx - ax, by - ay), 1e-9)
        nx_, ny_ = -(by - ay) / L_, (bx - ax) / L_
        n = max(8, int(L_ * g.size_km / 0.4))
        t = np.linspace(0, 1, n + 1)[:-1] if k < len(pts) - 2 else np.linspace(0, 1, n + 1)
        along = (k + t) * 1.7
        wob = (F.fbm(g.seed, f"meander-{key}", along * 6.0, np.zeros_like(along), 1.0, octaves=3)
               + 0.4 * F.fbm(g.seed, f"meander2-{key}", along * 19.0, np.zeros_like(along), 1.0, octaves=2))
        off = amp * wob * np.sin(np.pi * t) * min(1.0, L_ / 0.15)
        out += [[float(ax + (bx - ax) * u + nx_ * o), float(ay + (by - ay) * u + ny_ * o)] for u, o in zip(t, off)]
    return out


def compose(g: Grid, prims: list) -> dict:
    """Fields from primitives, applied in order: land (0 sea to 1 land), height to add (m), texture by belt (-1 none), a wild
    preference (0 to 1), wetness and moisture boosts, rivers laid (polylines in km), lakes, and the anchors."""
    from cybertron2.landgen import field as F
    warp = 0.05                                                            # shapes bent by noise at two scales, so no shape is a ruled
    px = g.x / g.size_km + warp * (F.fbm(g.seed, "macro-wx", g.x, g.y, 12.0, octaves=3)        # line or a circle (G-34)
                                   + 0.35 * F.fbm(g.seed, "macro-wx2", g.x, g.y, 3.5, octaves=3))
    py = g.y / g.size_km + warp * (F.fbm(g.seed, "macro-wy", g.x, g.y, 12.0, octaves=3)
                                   + 0.35 * F.fbm(g.seed, "macro-wy2", g.x, g.y, 3.5, octaves=3))
    rough = 0.7 + 0.6 * F.fbm(g.seed, "macro-ridged", g.x, g.y, 4.0, octaves=4, ridged=True)   # crests and saddles along a ridge
    land = np.ones(g.shape)
    add = np.zeros(g.shape)
    tex = np.full(g.shape, -1, dtype=int)
    wild, wet, moist, flat = np.zeros(g.shape), np.zeros(g.shape), np.zeros(g.shape), np.zeros(g.shape)
    ore = np.zeros(g.shape, dtype=bool)
    systems = {k: np.zeros(g.shape) for k in SYSTEMS}
    lake_ok = np.zeros(g.shape, dtype=bool)
    rivers, anchors = [], {}
    A = lambda name, key, pt: anchors.__setitem__(f"{name}.{key}" if key else name, [float(pt[0]), float(pt[1])])
    for p in prims:
        k, nm = p["kind"], p.get("name", p["kind"])
        if k == "sea":
            land = np.zeros(g.shape)
        elif k == "coast":
            nx_, ny_ = SIDES[p.get("side", "west")]
            at = float(p.get("at", 0.15))
            dist = px * nx_ + py * ny_ + (1 if nx_ < 0 else 0) + (1 if ny_ < 0 else 0) - at   # signed, + inland (east and north
                                                                           # coasts added 2 here, not 1, and so had no sea at all)
            dist = dist + float(p.get("ragged", 0.035)) * (F.fbm(g.seed, f"coast-{nm}", g.x, g.y, 8.0, octaves=5, gain=0.6)
                                                           + 0.5 * F.fbm(g.seed, f"coast2-{nm}", g.x, g.y, 2.5, octaves=3))   # headlands, bays
            land = np.minimum(land, np.clip(0.5 + dist / 0.02, 0, 1))
            mid = {"west": [at, 0.5], "east": [1 - at, 0.5], "south": [0.5, at], "north": [0.5, 1 - at]}[p.get("side", "west")]
            A(nm, None, mid)
        elif k == "inlet":
            d, _ = _seg_dist(px, py, p["from"], p["to"])
            d = _ragged(g, nm, d, p.get("width", 0.06), 0.3)
            land = np.minimum(land, np.clip((d - p.get("width", 0.06)) / 0.02 + 0.5, 0, 1))
            if p.get("tidal"):                                             # an estuary: mudflats and saltmarsh along its banks
                flat = np.maximum(flat, np.clip(1 - (d - p.get("width", 0.06) - 0.015) / 0.02, 0, 1))
                wet = np.maximum(wet, 0.7 * np.clip(1 - (d - p.get("width", 0.06) - 0.015) / 0.02, 0, 1))
            (fx, fy), (tx, ty) = p["from"], p["to"]
            L_ = max(np.hypot(tx - fx, ty - fy), 1e-9)
            w_ = p.get("width", 0.06) + 0.02                                 # the shore just past the inlet's end
            A(nm, "head", [tx + (tx - fx) / L_ * w_, ty + (ty - fy) / L_ * w_]), A(nm, "mouth", p["from"])
        elif k == "landmass":
            if "from" in p:
                d, _ = _seg_dist(px, py, p["from"], p["to"])
                A(nm, None, [(p["from"][0] + p["to"][0]) / 2, (p["from"][1] + p["to"][1]) / 2])
            else:
                d = np.hypot(px - p["at"][0], py - p["at"][1])
                A(nm, None, p["at"])
            d = _ragged(g, nm, d, p["r"], 0.4)
            land = np.maximum(land, np.clip((p["r"] - d) / 0.03 + 0.5, 0, 1))
        elif k in ("ridge", "ring"):
            if k == "ring":
                rr = _ragged(g, nm, np.hypot(px - p["at"][0], py - p["at"][1]), p["r"], 0.22)   # a ragged ring, not a circle
                d = np.abs(rr - p["r"])
                t = (np.arctan2(py - p["at"][1], px - p["at"][0]) / (2 * np.pi)) % 1.0
            else:
                d, t = _seg_dist(px, py, p["from"], p["to"])
                A(nm, "end_a", p["from"]), A(nm, "end_b", p["to"])
            prof = _bump(d, p.get("width", 0.06) / 2)
            cut = np.ones(g.shape)
            for i, gp in enumerate(p.get("gaps") or []):
                gw = p.get("gap_width", 0.04)
                cut *= 1 - float(p.get("gap_depth", 0.7)) * _bump(np.minimum(np.abs(t - gp), 1 - np.abs(t - gp)), gw)
                if k == "ring":
                    ang = 2 * np.pi * gp
                    pt = [p["at"][0] + p["r"] * np.cos(ang), p["at"][1] + p["r"] * np.sin(ang)]
                else:
                    pt = [p["from"][0] + gp * (p["to"][0] - p["from"][0]), p["from"][1] + gp * (p["to"][1] - p["from"][1])]
                A(nm, "pass" if len(p.get("gaps")) == 1 else f"pass_{i + 1}", pt)
                if k == "ring":
                    A(nm, "gate", pt)
            add += float(p["height"]) * prof * cut * rough
        elif k == "massif":
            d = _ragged(g, nm, np.hypot(px - p["at"][0], py - p["at"][1]), p["r"], 0.45)
            spurs = 0.5 + 0.9 * F.fbm(g.seed, f"spurs-{nm}", g.x, g.y, max(p["r"] * g.size_km / 3, 1.0), octaves=4, ridged=True)
            add += float(p["height"]) * _bump(d, p["r"] / 2) * rough * spurs          # a ridge with spurs, not a dome
            A(nm, None, p["at"])
        elif k == "plateau":
            d = np.hypot(px - p["at"][0], py - p["at"][1])
            step = 1 / (1 + np.exp((d - p["r"]) / p.get("edge", 0.02)))
            ang = (np.arctan2(py - p["at"][1], px - p["at"][0]) / (2 * np.pi)) % 1.0
            ramp = np.zeros(g.shape)
            for i, c in enumerate(p.get("climbs") or []):
                near = _bump(np.minimum(np.abs(ang - c), 1 - np.abs(ang - c)), 0.012) * _bump(np.abs(d - p["r"]), 0.05)
                ramp = np.maximum(ramp, near)
                a = 2 * np.pi * c
                A(nm, f"climb_{i + 1}", [p["at"][0] + p["r"] * np.cos(a), p["at"][1] + p["r"] * np.sin(a)])
            soft = 1 / (1 + np.exp((d - p["r"]) / 0.09))                      # a long gentle ramp where a climb is
            add += float(p["height"]) * (step * (1 - ramp) + soft * ramp)
            A(nm, None, p["at"])
        elif k == "scarp":
            ax, ay = p["from"]
            bx, by = p["to"]
            nx_, ny_ = -(by - ay), (bx - ax)                                     # a normal to the line, turned to the high side
            want = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}[p.get("high", "north")]
            if nx_ * want[0] + ny_ * want[1] < 0:
                nx_, ny_ = -nx_, -ny_
            n = np.hypot(nx_, ny_) or 1.0
            sd = ((px - ax) * nx_ + (py - ay) * ny_) / n                          # + on the high side
            add += float(p["height"]) / (1 + np.exp(-sd / p.get("width", 0.02)))
            A(nm, "foot", [(ax + bx) / 2, (ay + by) / 2])
        elif k in ("basin", "lake", "fen"):
            d = _ragged(g, nm, np.hypot(px - p["at"][0], py - p["at"][1]), p["r"], 0.4)
            b = _bump(d, p["r"] / 1.6)
            if k == "basin":
                add -= float(p.get("depth", 25)) * b
            elif k == "lake":
                add -= 25.0 * b
                wet += b
                lake_ok |= b > 0.3
            else:                                                              # a fen: flat, wet peat, its own system
                flat = np.maximum(flat, np.clip(1.6 * b, 0, 1))
                wet += 0.95 * b
                moist += 0.3 * b
                systems["fen"] = np.maximum(systems["fen"], np.clip(1.5 * b, 0, 1))
            A(nm, None, p["at"])
        elif k == "geology":
            inside = _inbox(g, nm, px, py, p["box"])
            code = {v: c for c, v in V.TEXTURE.items()}[p["texture"]]
            tex = np.where(inside, code, tex)
        elif k == "ore":                                                   # a belt of copper ore (stage 1 §11k: geology)
            x0, y0, x1, y1 = p["box"]
            ore |= (px >= x0) & (px <= x1) & (py >= y0) & (py <= y1)
            A(nm, None, [(x0 + x1) / 2, (y0 + y1) / 2])
        elif k == "wild":
            x0, y0, x1, y1 = p["box"]
            inside = _inbox(g, nm, px, py, p["box"], 0.05)
            wild = np.maximum(wild, inside.astype(float))
            systems["wildwood"] = np.maximum(systems["wildwood"], inside.astype(float))
            moist += 0.15 * inside
            A(nm, None, [(x0 + x1) / 2, (y0 + y1) / 2])
        elif k == "system":                                                # a landscape system over a box or round a point
            if "box" in p:
                inside = _inbox(g, nm, px, py, p["box"], 0.04).astype(float)
            else:
                inside = (_ragged(g, nm, np.hypot(px - p["at"][0], py - p["at"][1]), p["r"], 0.35) <= p["r"]).astype(float)
            if p["system"] not in systems:
                raise ValueError(f"unknown landscape system {p['system']!r}; known: {', '.join(SYSTEMS)}")
            systems[p["system"]] = np.maximum(systems[p["system"]], inside)
            if p["system"] in ("fen", "upland"):
                lake_ok |= inside > 0.5
            A(nm, None, p.get("at") or [(p["box"][0] + p["box"][2]) / 2, (p["box"][1] + p["box"][3]) / 2])
        elif k == "river":
            pts = [[float(a), float(b)] for a, b in p["through"]]
            course = _meander(g, nm, pts, p.get("flow", "large")) if p.get("meander", True) else pts
            rivers.append({"name": nm, "through": [[a * g.size_km, b * g.size_km] for a, b in course], "flow": p.get("flow", "large"),
                           "anchors": [[a * g.size_km, b * g.size_km] for a, b in pts]})
            A(nm, "source", pts[0]), A(nm, "mouth", pts[-1])
            for i, pt in enumerate(pts[1:-1]):
                A(nm, f"point_{i + 1}", pt)
        else:
            raise ValueError(f"unknown primitive kind {k!r}")
    lake_ok |= systems["fen"] > 0.5
    return {"px": px, "py": py, "ore": ore, "systems": systems, "lake_ok": lake_ok, "land": land, "add": add, "tex": tex, "wild": np.clip(wild, 0, 1), "wet": np.clip(wet, 0, 1),
            "moist": np.clip(moist, 0, 1), "flat": np.clip(flat, 0, 1), "rivers": rivers,
            "anchors": {k: [v[0] * g.size_km, v[1] * g.size_km] for k, v in anchors.items()}}


def primitives(gen: dict) -> list:
    """The primitives of a world: its named configuration (with any overrides), then its own features, in that order."""
    out = []
    name = gen.get("configuration")
    if name:
        if name in V.WAITING:
            raise ValueError(f"the configuration {name!r} waits for a later system (D2-188)")
        if name not in V.CONFIGS:
            raise ValueError(f"no configuration called {name!r}; known: {', '.join(sorted(V.CONFIGS))}")
        over = gen.get("configuration_params") or {}
        for p in V.CONFIGS[name]:
            out.append({**p, **(over.get(p.get("name")) or {})})
    out += list(gen.get("features") or [])
    return out
