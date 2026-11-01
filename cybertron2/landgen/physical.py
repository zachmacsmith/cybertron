"""The physical layers (generator.md §2b, §7, §10; stage 1 §3, §11a): elevation, climate, water, soil, terrain and natural cover,
each a field over the grid. Physics is kept cheap and only where it ends in leverage (generator.md §7): noise and the large shapes
for elevation, one wind sweep for rain and its shadow, depression filling and flow accumulation for rivers and lakes, one pass of
valley cutting, rules for soil, and a scored table for terrain."""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field as dfield

import numpy as np

from cybertron2.landgen import field as F, keyed, macro as M, vocab as V
from cybertron2.landgen.field import Grid

TERRAIN_NAMES = list(V.TERRAINS) + ["deep forest", "water"]
WATER = TERRAIN_NAMES.index("water")


@dataclass
class Land:
    g: Grid
    conf: dict
    h: np.ndarray                  # height, m
    sea: np.ndarray                # bool
    lake: np.ndarray               # bool
    slope: np.ndarray              # degrees
    temp: np.ndarray               # a year's mean, C
    moist: np.ndarray              # 0 to 1
    acc: np.ndarray                # km2 drained (weighted by rain)
    recv: np.ndarray               # flat index of the cell each drains to, -1 at an outlet
    river: np.ndarray              # 0 none, 1 river, 2 medium, 3 large
    spring: np.ndarray             # bool: a stream's head
    wet: np.ndarray                # 0 to 1
    tex: np.ndarray                # vocab.SAND, LOAM, CLAY, CHALK
    depth: np.ndarray              # 0 to 1
    fert: np.ndarray               # a multiplier on a plot's harvest
    f: np.ndarray                  # height above the nearest river of class 2 or more, m (99 if none within 3 km)
    near_river: np.ndarray         # the largest river class within 1.5 km
    c: np.ndarray                  # distance to the sea, km (99 beyond 3 km)
    wild: np.ndarray               # the frontier's preference, 0 to 1
    terrain: np.ndarray            # index into TERRAIN_NAMES
    cover: np.ndarray              # natural cover (str)
    anchors: dict
    rivers: list = dfield(default_factory=list)   # rivers laid by the world file: [{name, through (km), flow}]

    def tname(self, r, c) -> str:
        return TERRAIN_NAMES[int(self.terrain[r, c])]


def elevation(g: Grid, conf: dict, mf: dict) -> np.ndarray:
    s = g.seed
    h = (conf["base_m"] + conf["relief_m"] * F.warped(s, "relief", g.x, g.y, 12.0, 4.0)
         + 0.35 * conf["relief_m"] * F.fbm(s, "detail", g.x, g.y, 3.0, octaves=4))
    h = h + mf["add"] * (1 + 0.08 * F.fbm(s, "rough", g.x, g.y, 2.0, octaves=3))
    tilt = conf["tilt_m_km"] * {"west": g.x, "east": g.size_km - g.x, "south": g.y, "north": g.size_km - g.y}[conf["wind"]]
    h = h + tilt                                                           # land rises away from the windward side: rivers run to it
    h = mf["land"] * np.maximum(h, conf["sea_level"] + 2) + (1 - mf["land"]) * (conf["sea_level"] - 30 + 8 * F.fbm(s, "seabed", g.x, g.y, 6.0))
    h = h * (1 - mf["flat"]) + mf["flat"] * (conf["sea_level"] + 4 + 2 * F.fbm(s, "fen", g.x, g.y, 2.0, octaves=3))
    for rv in mf["rivers"]:                                                # a laid river: a channel that runs downhill all the way
        pts = [[a / g.size_km, b / g.size_km] for a, b in rv["through"]]
        d, along = M._poly_dist(mf["px"], mf["py"], pts)                    # in the same bent space as the shapes
        dk = d * g.size_km
        r0, c0 = g.cell(*rv["through"][0])
        r1, c1 = g.cell(*rv["through"][-1])
        top = max(float(h[r0, c0]), conf["sea_level"] + 10)
        low = min(float(h[r1, c1]), conf["sea_level"] + 1)
        prof = top + (low - top) * along
        h = np.where(dk < 0.25, np.minimum(h, prof - 2), h)
        h = np.where((dk >= 0.25) & (dk < 1.5), np.minimum(h, prof + (h - prof).clip(0) * (dk / 1.5)), h)
    return h


def climate(g: Grid, conf: dict, h: np.ndarray, sea: np.ndarray, mf: dict) -> tuple[np.ndarray, np.ndarray]:
    """Temperature by height and a north-south gradient; moisture from one sweep along the prevailing wind: rain on windward
    slopes, a shadow beyond, recharge over the sea."""
    temp = conf["temperature_c"] - conf["lapse_c_km"] * np.clip(h, 0, None) / 1000.0 - 1.5 * (g.y / g.size_km - 0.5)
    k = {"west": 0, "south": 1, "east": 2, "north": 3}[conf["wind"]]
    hh, ss = np.rot90(h, k), np.rot90(sea, k)
    smooth = F.box_mean(hh, 8)
    rain = np.zeros(hh.shape)
    v = np.full(hh.shape[0], 1.0)
    prev = smooth[:, 0]
    for j in range(hh.shape[1]):
        lift = np.clip(smooth[:, j] - prev, 0, None) / 30.0
        r = np.clip(0.18 * v + lift * v, 0, v)
        rain[:, j] = r
        v = np.where(ss[:, j], np.minimum(1.3, v + 0.08), np.clip(v - 0.35 * r + 0.004, 0.2, 1.3))
        prev = smooth[:, j]
    rain = np.rot90(rain, -k)
    lo, hi = np.percentile(rain, 2), np.percentile(rain, 98)
    m = 0.4 + 0.4 * np.clip((rain - lo) / max(hi - lo, 1e-9), 0, 1) + 0.12 * F.fbm(g.seed, "moist", g.x, g.y, 15.0, octaves=3)
    return temp, np.clip(m + mf["moist"], 0, 1)


def flood(g: Grid, h: np.ndarray, outlet: np.ndarray) -> tuple[np.ndarray, np.ndarray, list]:
    """Priority-Flood (Barnes and others): fill hollows from the outlets (the sea and the window's edge) inward, a millimetre a
    step on flats so everything drains; each cell drains to the cell it was reached from. Returns the filled surface, each cell's
    receiver (flat index, -1 at an outlet) and the order cells were reached (downstream first)."""
    ny, nx = g.shape
    H = h.ravel()
    Z = H.copy()
    eps = 0.001 + 0.02 * keyed.nprng(g.seed, "flood-eps").random(H.size)  # uneven steps on flats, so a drained hollow meanders
    recv = np.full(H.size, -1, dtype=np.int64)
    done = np.zeros(H.size, dtype=bool)
    heap, order = [], []
    edge = np.zeros(g.shape, dtype=bool)
    edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = True
    for i in np.flatnonzero((edge | outlet).ravel()):
        heapq.heappush(heap, (float(Z[i]), int(i)))
        done[i] = True
    while heap:
        z, i = heapq.heappop(heap)
        order.append(i)
        r, c = divmod(i, nx)
        for dr, dc in F.N8:
            rr, cc = r + dr, c + dc
            if 0 <= rr < ny and 0 <= cc < nx:
                j = rr * nx + cc
                if not done[j]:
                    done[j] = True
                    Z[j] = max(H[j], z + eps[j])
                    recv[j] = i
                    heapq.heappush(heap, (float(Z[j]), j))
    return Z.reshape(g.shape), recv, order


def accumulate(g: Grid, recv, order, rain_km2: np.ndarray, outlet: np.ndarray) -> np.ndarray:
    acc = rain_km2.ravel().copy()
    acc[outlet.ravel()] = 0.0
    for i in reversed(order):
        j = recv[i]
        if j >= 0 and not outlet.flat[i]:
            acc[j] += acc[i]
    return acc.reshape(g.shape)


def _spread(g: Grid, src: np.ndarray, val: np.ndarray, steps: int, how="max"):
    """For each cell within `steps` cells of a source, the value of the nearest (how='near') or the largest (how='max'), and the
    distance in cells (np.inf beyond)."""
    dist = np.where(src, 0.0, np.inf)
    out = np.where(src, val, np.nan if how == "near" else 0.0)
    for _ in range(steps):
        for (dr, dc), d in zip(F.N8, F.D8):
            nd = g.shifted(dist, dr, dc, fill=np.inf) + d
            nv = g.shifted(out, dr, dc, fill=np.nan if how == "near" else 0.0)
            if how == "near":
                better = nd < dist
                out = np.where(better, nv, out)
                dist = np.where(better, nd, dist)
            else:
                ok = nd < np.inf
                out = np.where(ok & (np.nan_to_num(nv) > out), nv, out)
                dist = np.minimum(dist, nd)
    return out, dist


def build(conf: dict, g: Grid, prims: list) -> Land:
    mf = M.compose(g, prims)
    h = elevation(g, conf, mf)
    sea = h < conf["sea_level"]
    temp, moist = climate(g, conf, h, sea, mf)
    area = g.km * g.km
    rain = moist / 0.6 * area
    for cut in (True, False):                                              # flow once, cut valleys by flow, flow again
        Z, recv, order = flood(g, h, sea)
        acc = accumulate(g, recv, order, rain, sea)
        if cut:
            riv = acc >= conf["river_km2"]
            cut_m = np.clip(conf["incision_m"] * np.sqrt(acc / conf["river_km2"]), 0, 40) * riv
            side = np.maximum.reduce([g.shifted(cut_m, dr, dc, 0.0) for dr, dc in F.N8]) * (~riv)   # the valley's sides
            h = h - cut_m - 0.4 * side
    lake = (Z - h > conf["lake_m"]) & ~sea                                 # a hollow deeper than this holds water; shallower ones drain
    river = np.select([acc >= conf["large_km2"], acc >= conf["medium_km2"], acc >= conf["river_km2"]], [3, 2, 1], 0) * ~sea * ~lake
    stream = (acc >= conf["stream_km2"]) & ~sea & ~lake
    up = np.zeros(h.size, dtype=bool)
    flat_stream = stream.ravel()
    for i in np.flatnonzero(flat_stream):
        j = recv[i]
        if j >= 0:
            up[j] = True
    slope = F.slope_deg(g, h)
    spring = stream & ~up.reshape(g.shape) & (slope >= 1.0)
    edge = np.zeros(g.shape, dtype=bool)
    edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = True
    spring &= ~edge
    twi = np.log(np.maximum(acc, 1e-6) * 1e6 / (g.km * 1000.0) / (np.tan(np.radians(slope)) + 0.0005))
    lo, hi = np.percentile(twi[~sea], 2), np.percentile(twi[~sea], 99.5)
    wet = np.clip((twi - lo) / max(hi - lo, 1e-9), 0, 1)
    wet = np.clip(np.maximum(wet, mf["wet"]), 0, 1)
    wet[lake | (river >= 2) | sea] = 1.0
    rh, rd = _spread(g, river >= 2, Z, 20, how="near")
    f = np.where(np.isfinite(rd), h - np.nan_to_num(rh), 99.0)
    f = np.clip(f, 0, 99)
    near, _ = _spread(g, river > 0, river.astype(float), 10, how="max")
    _, cd = _spread(g, sea, np.ones(g.shape), 20, how="near")
    c = np.where(np.isfinite(cd), cd * g.km, 99.0)
    # soil: texture by belt, else by rules; depth by slope; fertility by texture, river silt, wetness, depth and height
    n = F.fbm(g.seed, "geology", g.x, g.y, 6.0, octaves=3)
    tex = np.full(g.shape, V.LOAM)
    tex = np.where((h < 130) & (moist >= 0.5) & (n > 0.15), V.CLAY, tex)
    tex = np.where((moist < 0.42) & (n < -0.2), V.SAND, tex)
    tex = np.where(mf["tex"] >= 0, mf["tex"], tex)
    depth = np.clip(1 - slope / 25.0, 0.1, 1.0)
    base = np.select([tex == V.SAND, tex == V.CLAY, tex == V.CHALK], [0.7, 1.1, 0.75], 1.0)
    silt = np.where((f < 2) & (near >= 2), 1.25, 1.0)
    fert = base * silt * np.where(wet > 0.85, 0.8, 1.0) * (0.8 + 0.2 * depth) * (1 - np.clip((h - 300) / 600, 0, 0.5))
    land = Land(g, conf, h, sea, lake, slope, temp, moist, acc, recv, river.astype(int), spring, wet, tex.astype(int), depth,
                np.round(fert, 3), f, near.astype(int), c, mf["wild"], np.zeros(g.shape, dtype=int), np.zeros(g.shape, dtype=object),
                mf["anchors"], mf["rivers"])
    terrains(land)
    return land


class _Ctx:
    def __init__(self, L: Land):
        self.h, self.s, self.m, self.w, self.tex, self.f = L.h, L.slope, L.moist, L.wet, L.tex, L.f
        self.near_river, self.c, self.wild = L.near_river, L.c, L.wild


def terrains(L: Land, pins: dict | None = None) -> None:
    """Each cell's terrain by the catalogue's scores (stage 1 §11a), ties broken by keyed noise; water where there is water.
    `pins` maps a terrain name to a boost field (a pin tilting the choice: RimWorld's way, generator.md §9)."""
    x = _Ctx(L)
    names = list(V.TERRAINS)
    jitter = 0.05 * F.fbm(L.g.seed, "terrain-ties", L.g.x, L.g.y, 1.0, octaves=2)
    scores = []
    for nm in names:
        sc = np.zeros(L.g.shape)
        for wgt, test in V.TERRAINS[nm]:
            ok = test(x)
            sc += np.where(ok, wgt, -0.5 * wgt)
        if pins and nm in pins:
            sc += pins[nm]
        scores.append(sc + jitter * (1 + names.index(nm) % 3))
    L.terrain = np.argmax(np.stack(scores), axis=0)
    L.terrain[L.sea | L.lake | (L.river >= 3)] = WATER
    L.cover = np.array([V.NATURAL.get(TERRAIN_NAMES[t], "water") if t != WATER else "water" for t in L.terrain.ravel()],
                       dtype=object).reshape(L.g.shape)


def deep_forest(L: Land, sites: list) -> None:
    """Wild woodland far from every settlement is deep forest (stage 1 §11a), decided once the sites are chosen."""
    if not sites:
        return
    wood = (L.cover == "forest") & (L.terrain != WATER)
    far = np.full(L.g.shape, True)
    for (r, c) in sites:
        far &= np.hypot(L.g.x - L.g.x[r, c], L.g.y - L.g.y[r, c]) > L.conf["deep_forest_km"]
    L.terrain[wood & far] = TERRAIN_NAMES.index("deep forest")
