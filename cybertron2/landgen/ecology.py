"""Ecosystems for the temperate envelope (temperate_landscapes.md §2, §3c; ecosystems.md §2, §6): what grows on each cell before
anyone settles, the land as people have used it by how long the region has been settled, and each wood's depth.

Three steps:
- `natural`: the potential natural ecosystem from the base environment (terrain, soil, water, height). Mostly wood, as lowland
  Britain was, except where it is too wet, salt, high or bare.
- `settled`: once the sites are chosen, the wildwood is cleared until the region's wood share matches how long it has been settled.
  Clearing picks good land near villages first; in long settled land good land anywhere, as others beyond the window cleared it too.
  Cleared land becomes what its ground makes of it when grazed and mown: meadow on the floodplain, chalk grassland on the down,
  heath on sand, hill pasture and moor up high.
- the depth of every wood remaining: edge, interior, core. Deep forest is the core of a large wood, wherever it lies.

The engine sees only the cover; the ecosystem, forest type and depth go to the parcels as data, and set their game and forage
stocks.
"""
from __future__ import annotations

import numpy as np

from cybertron2.landgen import field as F, vocab as V

# name: (cover, words for descriptions, colour on the picture)
ECOSYSTEMS = {
    "oak-ash wood": ("forest", "oak and ash over hazel", (55, 110, 55)),
    "beech wood": ("forest", "tall beech, bare beneath", (80, 120, 50)),
    "alder carr": ("forest", "alder and willow standing in wet ground", (70, 120, 100)),
    "birch and pine wood": ("forest", "birch and pine on light sand", (75, 105, 75)),
    "upland oak wood": ("forest", "small oak and birch on the valley sides", (85, 115, 70)),
    "hay meadow": ("meadow", "hay meadow by the river", (170, 205, 110)),
    "wet grassland": ("meadow", "rushy wet grazing", (140, 185, 120)),
    "grassland": ("pasture", "open grazing and old fields", (175, 195, 120)),
    "chalk grassland": ("pasture", "short turf on the down", (205, 215, 160)),
    "hill pasture": ("pasture", "rough hill grazing", (170, 170, 130)),
    "dune grassland": ("pasture", "marram on the dunes", (220, 210, 160)),
    "lowland heath": ("heath", "heather and gorse", (180, 150, 120)),
    "moor": ("moor", "open heather moor", (125, 100, 115)),
    "blanket bog": ("moor", "wet peat bog on the tops", (110, 100, 100)),
    "fen": ("fen", "sedge fen over peat", (115, 150, 135)),
    "reedbed": ("fen", "tall reeds over standing water", (135, 160, 120)),
    "saltmarsh": ("saltmarsh", "salt grass and creeks", (150, 170, 150)),
    "scrub": ("scrub", "thorn and rough grass", (140, 140, 90)),
    "bare rock": ("rock", "bare rock and scree", (130, 125, 120)),
    "water": ("water", "water", (60, 110, 170)),
}
FORESTS = [k for k, v in ECOSYSTEMS.items() if v[0] == "forest"]
OPEN = {k for k, v in ECOSYSTEMS.items() if v[0] not in ("forest", "water")}

# what a cleared wood becomes when grazed and mown, by the base environment
CLEARED = {"river floodplain": "hay meadow", "river terrace": "grassland", "clay vale": "grassland", "lowland loam": "grassland",
           "sandy ground": "lowland heath", "chalk down": "chalk grassland", "hills": "hill pasture", "upland pasture": "hill pasture",
           "coast": "grassland", "fen": "wet grassland", "moor": "moor", "saltmarsh": "saltmarsh", "rock": "bare rock"}
# how good each base environment is to clear for farming (temperate_landscapes.md §3c: woods survived on clay and steep land)
CLEAR_FOR = {"river terrace": 1.0, "lowland loam": 1.0, "river floodplain": 0.8, "chalk down": 0.75, "sandy ground": 0.6,
             "coast": 0.6, "clay vale": 0.45, "hills": 0.3, "upland pasture": 0.25, "fen": 0.3, "moor": 0.1}
# a wood's game and forage by its type and its depth (written as the parcel's stocks; calibrate)
GAME_BY_TYPE = {"oak-ash wood": 1.0, "beech wood": 0.8, "alder carr": 0.6, "birch and pine wood": 0.6, "upland oak wood": 0.8}
GAME_BY_BAND = {1: 0.8, 2: 1.0, 3: 1.5}
PLANTS_BY_BAND = {1: 1.2, 2: 1.0, 3: 0.6}
BAND_NAMES = {0: "", 1: "edge", 2: "interior", 3: "core"}


def _tn(L):
    from cybertron2.landgen.physical import TERRAIN_NAMES
    return np.array(TERRAIN_NAMES, dtype=object)[L.terrain]


def _set_cover(L):
    cov = {k: v[0] for k, v in ECOSYSTEMS.items()}
    L.cover = np.vectorize(lambda e: cov.get(e, "scrub"), otypes=[object])(L.eco)


def natural(L) -> None:
    """The ecosystem before anyone settles, from the base environment."""
    tn = _tn(L)
    eco = np.full(L.g.shape, "oak-ash wood", dtype=object)
    wet, h, sl = L.wet, L.h, L.slope
    eco[tn == "river floodplain"] = np.where(wet[tn == "river floodplain"] >= 0.85, "alder carr", "oak-ash wood")
    eco[tn == "chalk down"] = "beech wood"
    eco[tn == "sandy ground"] = "birch and pine wood"
    eco[tn == "hills"] = "upland oak wood"
    up = tn == "upland pasture"
    eco[up] = np.where(h[up] >= 520, "moor", "upland oak wood")
    mo = tn == "moor"
    eco[mo] = np.where((wet[mo] >= 0.75) & (sl[mo] < 4), "blanket bog", "moor")
    fe = tn == "fen"
    near_water = F.box_mean((L.lake | (L.river >= 2)).astype(float), 2) > 0
    eco[fe] = np.where((wet[fe] >= 0.95) | near_water[fe], "reedbed", "fen")
    fen_edge = (L._sys["fen"] > 0.3) & ~fe & (wet >= 0.55) & (tn != "water")
    eco[fen_edge] = "alder carr"
    co = tn == "coast"
    eco[co] = np.where((L.tex[co] == V.SAND) | (L.c[co] < 0.4), "dune grassland", "grassland")
    sy = L.system if L.system is not None else np.full(L.g.shape, "river country", dtype=object)
    sea0 = float(L.conf["sea_level"])
    # a landscape system sets its own palette (temperate_landscapes.md §2)
    in_fen = (sy == "fen") & ~fe & (L.h < sea0 + 8) & (tn != "water")              # the fen's drier margins: carr (islands stay dry)
    eco[in_fen] = "alder carr"
    upl = (sy == "upland") & np.isin(eco, ["oak-ash wood", "beech wood", "birch and pine wood"])
    eco[upl] = "upland oak wood"
    tops = (sy == "upland") & (h >= 450) & (tn != "water") & (tn != "rock")        # the open tops: moor above about 450 m
    eco[tops] = np.where((wet[tops] >= 0.7) & (sl[tops] < 4), "blanket bog", "moor")
    tidal = (h < sea0 + 3) & (L.c < 1.0) & ~L.sea & (tn != "water") & ((wet >= 0.6) | (sy == "fen"))   # flats the tide reaches
    eco[tidal] = "saltmarsh"
    eco[tn == "saltmarsh"] = "saltmarsh"
    eco[tn == "rock"] = "bare rock"
    eco[(tn == "water") | L.sea | L.lake] = "water"
    L.eco = eco
    L.band = np.zeros(L.g.shape, dtype=np.int8)
    _set_cover(L)


def natural_forest(terrain: str) -> str:
    """The wood a base environment grows, for a village wood planted or kept where the map had none."""
    return {"chalk down": "beech wood", "sandy ground": "birch and pine wood", "hills": "upland oak wood",
            "upland pasture": "upland oak wood", "river floodplain": "alder carr", "fen": "alder carr"}.get(terrain, "oak-ash wood")


def wood_target(conf) -> float:
    s = conf.get("settled", "settled")
    return float(s) if isinstance(s, (int, float)) else V.WOOD_SHARE[s]


def settled(L, sites: list) -> None:
    """Clear the wildwood until the land's wood share is the region's (by how long settled), good land near villages first; then
    each remaining wood's depth."""
    conf = L.conf
    tn = _tn(L)
    land = ~L.sea & (tn != "water")
    wild = L._sys["wildwood"] > 0.5                                       # a frontier box keeps its wildwood; the share is the rest's
    wood = np.isin(L.eco, FORESTS) & land & ~wild
    target = wood_target(conf)
    word = conf.get("settled", "settled")
    near_w = V.NEAR_WEIGHT.get(word, 0.8) if isinstance(word, str) else (2.5 if target >= 0.5 else 0.8 if target >= 0.25 else 0.3)
    g = L.g
    if sites:
        src = np.zeros(g.shape, dtype=bool)
        for r, c in sites:
            src[r, c] = True
        pace = np.where(L.eco == "water", 0.5, np.where(wood, 2.0, 3.0)) / (1 + L.slope / 10.0)
        cost = 1.0 / pace * (1 + 0.5 * F.fbm(g.seed, "clearing", g.x, g.y, 4.0, octaves=4))     # uneven, not circles (G-34)
        hours = F.travel(g, src, np.clip(cost, 0.05, None))
        near = np.minimum(np.where(np.isfinite(hours), hours, 99.0) / float(conf["road_day_hours"]), 1.0)   # in days; past a
                                                                           # day's walk nearness stops mattering (no frame of woods)
    else:
        near = np.zeros(g.shape)
    suit = np.vectorize(lambda t: CLEAR_FOR.get(t, 0.0), otypes=[float])(tn)
    suit = suit - L.slope / 25.0 + 0.15 * F.fbm(g.seed, "clear-patch", g.x, g.y, 2.5, octaves=4)
    score = suit - near_w * near
    n_land = int((land & ~wild).sum())
    keep = int(round(target * n_land))
    n_wood = int(wood.sum())
    if n_wood > keep:
        idx = np.flatnonzero(wood.ravel())
        order = idx[np.argsort(-score.ravel()[idx], kind="stable")]
        cut = order[: n_wood - keep]
        flat = L.eco.ravel()
        tflat = tn.ravel()
        sflat = L.system.ravel()
        for i in cut:
            e = flat[i]
            flat[i] = ("wet grassland" if e == "alder carr" or sflat[i] == "fen"
                       else "hill pasture" if sflat[i] == "upland" else CLEARED.get(tflat[i], "grassland"))
        L.eco = flat.reshape(g.shape)
    # wet cleared grass by rivers stays wet grassland; the floodplain's meadow wetter than this is rushy
    hm = (L.eco == "hay meadow") & (L.wet >= 0.85)
    L.eco[hm] = "wet grassland"
    moorish = (L.eco == "hill pasture") & (L.h >= 300) & (L.moist >= 0.65)
    L.eco[moorish] = "moor"
    _set_cover(L)
    depth(L)
    L.wood_target = target
    L.wood_share = float((np.isin(L.eco, FORESTS) & land & ~wild).sum() / max(n_land, 1))


def depth(L) -> None:
    """Each wood cell's depth: its distance inside the wood's edge, in bands (edge, interior, core)."""
    g = L.g
    wood = np.isin(L.eco, FORESTS)
    km_in = F.travel(g, ~wood, np.ones(g.shape), limit=float(L.conf["core_km"]) * 3)
    km_in = np.where(np.isfinite(km_in), km_in, float(L.conf["core_km"]) * 3)
    band = np.zeros(g.shape, dtype=np.int8)
    band[wood] = 1
    band[wood & (km_in >= float(L.conf["edge_km"]))] = 2
    band[wood & (km_in >= float(L.conf["core_km"]))] = 3
    L.band = band
    L.km_in = km_in
