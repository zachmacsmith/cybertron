"""The ground truth of a generated world, for the renderer (c2viz/ENGINE.md §12): the cells the landscape generator drew the world
from (cybertron2/landgen: elevation, water, soil, terrain, cover, and which parcel each cell is), packed for viz.json.

The only reader of a world's `.cells.npz` and `.report.json`. A world made by hand, or a run from before the generator, has none:
the renderer then derives its landscape from the engine's land facts, as before (ENGINE.md §9).

What the generator does not save is recovered with its own rule, not drawn freely:
- **roads:** each road's cells, by the generator's road rule (landgen.roads: hours by cover and slope, fords, least-cost paths),
  asked again through c2viz.touch; each road is checked against the parcels the world file says it leaves by;
- **rivers:** as lines, following each river cell downstream along its flow (the cells' accumulated flow).
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from c2viz import touch as E

N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def find(run, spec, given=None) -> Path | None:
    """The cells of the run's world: as given; beside the run; or beside the world file in cybertron2/specs by the world's name."""
    if given:
        return Path(given)
    if not (spec.get("generated") or {}).get("by"):
        return None
    for d in (Path(run), Path(__file__).resolve().parents[1] / "cybertron2" / "specs"):
        for p in sorted(d.glob("*.cells.npz")):
            if p.name == f"{spec.get('name')}.cells.npz" or d == Path(run):
                return p
    return None


def _b64(a, dtype) -> str:
    return base64.b64encode(np.ascontiguousarray(a, dtype=dtype).tobytes()).decode()


def _grid_km(x) -> float:
    """The cell spacing: points are (column + jitter of at most 0.35) times the spacing (landgen.field.grid)."""
    nx = x.shape[1]
    return float(round(np.mean(x[:, -1]) / (nx - 1), 4))


def _rivers(z) -> list:
    """Each river as a line of cells from its head down to where it ends (the sea, a lake, the edge, or a larger river)."""
    river, acc, h = z["river"], z["acc"], z["h"]
    ny, nx = river.shape
    down = {}
    for r, c in zip(*np.nonzero(river > 0)):
        best, ba = None, acc[r, c]
        for dr, dc in N8:
            rr, cc = r + dr, c + dc
            if 0 <= rr < ny and 0 <= cc < nx and acc[rr, cc] > ba:
                best, ba = (rr, cc), acc[rr, cc]
        down[(r, c)] = best
    has_up = {v for v in down.values() if v is not None}
    heads = [k for k in down if k not in has_up]
    seen, lines = set(), []
    for k in sorted(heads, key=lambda k: acc[k]):
        line, cur = [], k
        while cur is not None and cur not in seen:
            line.append(cur)
            seen.add(cur)
            nxt = down.get(cur)
            if nxt is None and cur in down:                                  # leaves the river cells: one step into what it joins
                rr, cc = cur
                ok = [(rr + a, cc + b) for a, b in N8 if 0 <= rr + a < ny and 0 <= cc + b < nx]
                tgt = max(ok, key=lambda q: acc[q])
                if acc[tgt] > acc[cur]:
                    line.append(tgt)
            cur = nxt
        if cur is not None:
            line.append(cur)                                                 # joins a river already drawn
        if len(line) >= 2:
            lines.append({"cells": [[int(r), int(c)] for r, c in line], "class": [int(river[q]) if q in down else 0 for q in map(tuple, line)]})
    return lines


def _roads(z, spec, roads_in, report, gseed, km, size_km) -> tuple[dict, dict]:
    """Each road's cells by the generator's road rule, from the end it was routed from; a check against the world file's road ends."""
    nodes = report.get("nodes") or {}
    kind = {k: v.get("kind") for k, v in nodes.items()}
    place = z["place"]
    par_node, par_cover = {}, {}
    for nid, n in spec["nodes"].items():
        for pid, p in (n.get("parcels") or {}).items():
            par_node[pid], par_cover[pid] = nid, p.get("cover")
    g = E.land_grid(gseed, size_km, km, z["x"], z["y"])
    L = SimpleNamespace(g=g, slope=z["slope"], river=z["river"], lake=z["lake"], sea=z["sea"], cover=z["cover"].astype(object))
    cov = L.cover.copy()
    for r, c in zip(*np.nonzero(place != "")):                               # the villages' parcels, as when the roads were made
        pid = str(place[r, c])
        if kind.get(par_node.get(pid)) == "village" and par_cover.get(pid):
            cov[r, c] = par_cover[pid]
    H = E.road_hours(L, cov, E.road_fords(L))
    day = float(E.land_defaults().get("road_day_hours", 8.0))
    site = {}
    for k, v in nodes.items():
        sx, sy = v["site_km"]
        d = (z["x"] - sx) ** 2 + (z["y"] - sy) ** 2
        site[k] = tuple(int(i) for i in np.unravel_index(np.argmin(d), d.shape))
    reach = {}
    out, check = {}, {"roads": 0, "match": 0, "unmatched": []}

    def owner_walk(path, nid):
        """The last of a place's parcels a path passes on its way out (landgen.roads._end, read from the cells)."""
        last = None
        for rc in path:
            pid = str(place[rc])
            if pid and par_node.get(pid) == nid:
                last = pid
            elif any(0 <= rc[0] + a < place.shape[0] and 0 <= rc[1] + b < place.shape[1] and par_node.get(str(place[rc[0] + a, rc[1] + b])) == nid
                     for a, b in N8):
                continue
            else:
                break
        return last

    for rid, r in roads_in.items():
        a, b = r["a"], r["b"]
        if a not in site or b not in site:
            continue
        best = None
        for s, t in ((a, b), (b, a)):
            if s not in reach:
                reach[s] = E.road_reach(L, H, site[s], 3.2 * day)
            dist, prev = reach[s]
            if not np.isfinite(dist[site[t]]):
                continue
            path = E.road_path(prev, site[s], site[t])
            if s == b:
                path = path[::-1]
            ends = r.get("ends") or {}
            ok = all((owner_walk(path if n == a else path[::-1], n) in ((ends.get(n) or {}).get("parcels") or [None])) for n in (a, b)
                     if kind.get(n) == "village")
            hrs = [float(dist[q]) for q in (path if s == a else path[::-1])]
            hrs = hrs if s == a else [hrs[-1] - x for x in hrs]
            if best is None or (ok and not best[1]):
                best = (path, ok, hrs)
            if ok:
                break
        if best is None:
            continue
        path, ok, hrs = best
        days = max(1, int(r.get("days") or 1))
        total = hrs[-1] or 1.0
        bounds = [next((i for i, x in enumerate(hrs) if x >= total * k / days), len(path) - 1) for k in range(days + 1)]
        out[rid] = {"cells": [[int(p[0]), int(p[1])] for p in path], "stretches": bounds, "matches_ends": ok}
        check["roads"] += 1
        check["match"] += int(ok)
        if not ok:
            check["unmatched"].append(rid)
    return out, check


def pack(run, spec, roads, given=None) -> dict | None:
    """viz.json's `land` (SCHEMA.md), or None when the world has no cells. `roads` are the world's, as the engine keeps them."""
    p = find(run, spec, given)
    if p is None or not p.exists():
        return None
    z = dict(np.load(p, allow_pickle=False))
    rp = p.with_name(p.name.replace(".cells.npz", ".report.json"))
    report = json.loads(rp.read_text()) if rp.exists() else {}
    ours = {pid for n in spec["nodes"].values() for pid in (n.get("parcels") or {})}
    theirs = set(np.unique(z["place"])) - {""}
    if not theirs <= ours:                                                   # cells of another world
        print(f"c2viz ground: {p} is not this world's ({len(theirs - ours)} parcels unknown); drawn without it")
        return None
    ny, nx = z["h"].shape
    km = _grid_km(z["x"])
    gseed = int((spec.get("generated") or {}).get("seed") or report.get("seed") or spec.get("seed") or 1)
    size_km = round(km * (nx - 1), 3)
    covers = sorted(set(np.unique(z["cover"])))
    terr = [str(t) for t in z["terrain_names"]]
    pids = [""] + sorted(theirs)
    pidx = {k: i for i, k in enumerate(pids)}
    water = z["sea"].astype(np.uint8) | (z["lake"].astype(np.uint8) << 1) | (z["spring"].astype(np.uint8) << 2)
    roads, rcheck = _roads(z, spec, roads, report, gseed, km, size_km)      # on the generator's own cells, as it made them
    rivers = _rivers(z)
    # then north up: the generator's y is northing, the screen's rows run down
    flip = lambda r: ny - 1 - int(r)
    for x in roads.values():
        x["cells"] = [[flip(r), c] for r, c in x["cells"]]
    for x in rivers:
        x["cells"] = [[flip(r), c] for r, c in x["cells"]]
    z = {k: (np.flipud(v) if getattr(v, "ndim", 0) == 2 else v) for k, v in z.items()}
    z["y"] = (ny - 1) * km - z["y"]
    water = np.flipud(water)
    sites = {}
    for k, v in (report.get("nodes") or {}).items():
        sx, sy = v["site_km"]
        sites[k] = [round(sx / km, 2), round(ny - 1 - sy / km, 2)]
    return {
        "source": str(p.resolve()), "by": (spec.get("generated") or {}).get("by"), "seed": gseed, "north": "up",
        "grid": {"nx": nx, "ny": ny, "km": km},
        "layers": {
            "h": _b64(np.round(z["h"] * 10), "<i2"),                         # decimetres
            "cover": _b64(np.searchsorted(covers, z["cover"]), "u1"), "covers": covers,
            "terrain": _b64(z["terrain"], "u1"), "terrains": terr,
            "river": _b64(z["river"], "u1"),
            "water": _b64(water, "u1"),                                      # 1 sea, 2 lake, 4 a spring
            "wet": _b64(np.round(np.clip(z["wet"], 0, 1) * 255), "u1"),
            "place": _b64(np.vectorize(pidx.get)(z["place"]), "<u2"), "places": pids,
            "jx": _b64(np.round((z["x"] / km - np.arange(nx)[None, :]) * 100), "i1"),   # each cell's point off its grid place, in
            "jy": _b64(np.round((z["y"] / km - np.arange(ny)[:, None]) * 100), "i1"),   # hundredths of a cell
        },
        "sites": sites, "kinds": {k: v.get("kind") for k, v in (report.get("nodes") or {}).items()},
        "rivers": rivers, "roads": roads, "roads_check": rcheck,
    }
