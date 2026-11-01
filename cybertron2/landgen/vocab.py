"""The generator's data (D2-173, D2-181 to D2-188; stage 1 §11): defaults, the terrain catalogue's scores, covers, paces,
resources, the vocabulary and the named configurations. Every number here is a first value to calibrate (stage 1 §11: tuned by
trial on a few seeds, then fixed). A world file's `generate:` block overrides any default by name."""
from __future__ import annotations

# ---------------------------------------------------------------------- defaults (D2-181, D2-182; all world settings)
DEFAULTS = {
    "size_km": 50.0,              # the window's side (D2-182)
    "km": 0.15,                   # cell spacing: about 2 ha, a unit of size (D2-181)
    "settlements": 4,
    "spacing_km": 17.0,           # sites at least this far apart in a straight line: roads of about a day (D2-182)
    "configuration": None,        # a named configuration (CONFIGS), or none: plain land with noise
    "wind": "west",               # the prevailing wind (wet windward, rain shadow lee)
    "sea_level": 0.0,
    "base_m": 60.0,               # lowland height
    "relief_m": 70.0,             # the noise's height range
    "temperature_c": 9.0,         # a year's mean at sea level
    "lapse_c_km": 6.5,
    "stream_km2": 1.5,            # area drained that starts a stream (a spring at its head)
    "river_km2": 15.0,            # a river
    "medium_km2": 45.0,
    "large_km2": 150.0,
    "incision_m": 5.0,
    "lake_m": 4.0,                # a hollow deeper than this holds a lake; shallower ones drain across
    "tilt_m_km": 0.8,             # the land rises this much a km away from the windward side, so rivers run somewhere            # valleys cut by flow: this much x sqrt(area / river_km2), at most 40 m
    "capacity": [0.6, 0.7],       # D2-161: people at 60 to 70% of what the scarcest flow keeps
    "households": [2, 3],         # a settlement's households, unless pinned
    "household_size": 5,
    "parcels": [6, 15],           # per node (D2-116, D2-181)
    "field_km": 2.5,              # the farthest a settlement's worked land reaches (a few hours out and back is the maximum, D4-11)
    "wild_node_km2": 10.0,        # a wild area large enough for a node of its own (D2-181)
    "wild_node_hours": 4.0,       # ... and at least half a day from any settlement
    "wild_nodes": 1,              # of each kind (deep forest; hills), unless pinned
    "road_day_hours": 8.0,        # a day on the road (stage 1 §11f)
    "deep_forest_km": 12.0,       # woodland this far from any settlement is deep forest (stage 1 §11a: d > 15, scaled to 50 km)
}

# ---------------------------------------------------------------------- terrains (generator.md §10, D2-183; stage 1 §11a)
# Each terrain: conditions on a cell's context, as (weight, test). h height m, s slope degrees, m moisture 0-1, w wetness 0-1,
# tex texture (0 sand, 1 loam, 2 clay, 3 chalk), f height above the nearest river m, river (a river's class 0-3 within 1.5 km),
# c distance to the sea km. The best total wins; a test missed costs half its weight.
SAND, LOAM, CLAY, CHALK = 0, 1, 2, 3
TEXTURE = {SAND: "sand", LOAM: "loam", CLAY: "clay", CHALK: "chalk"}
TERRAINS = {
    "river floodplain": [(2.0, lambda x: x.f < 2), (1.5, lambda x: x.near_river >= 2), (1.0, lambda x: x.s < 2)],
    "river terrace": [(1.5, lambda x: (x.f >= 2) & (x.f < 8)), (1.0, lambda x: x.near_river >= 1), (1.0, lambda x: x.s < 4),
                      (0.5, lambda x: (x.tex == LOAM) | (x.tex == SAND))],
    "clay vale": [(2.0, lambda x: x.tex == CLAY), (1.0, lambda x: x.h < 150), (0.5, lambda x: x.s < 5), (0.5, lambda x: x.m >= 0.4)],
    "lowland loam": [(1.5, lambda x: x.tex == LOAM), (1.0, lambda x: x.h < 200), (1.0, lambda x: x.s < 6)],
    "sandy heath": [(2.0, lambda x: x.tex == SAND), (1.0, lambda x: x.m < 0.45)],
    "chalk down": [(2.5, lambda x: x.tex == CHALK), (0.5, lambda x: (x.h >= 80) & (x.h <= 300)), (0.5, lambda x: (x.s >= 2) & (x.s <= 15))],
    "woodland": [(1.0, lambda x: x.m >= 0.5), (0.5, lambda x: x.s < 15), (0.5, lambda x: x.w < 0.7), (0.6, lambda x: x.wild > 0.3)],
    "hills": [(2.0, lambda x: ((x.h >= 250) & (x.h <= 600)) | (x.s >= 10))],
    "upland pasture": [(2.0, lambda x: x.h >= 450), (0.5, lambda x: x.s < 15)],
    "moor": [(1.0, lambda x: x.h >= 300), (1.0, lambda x: x.m >= 0.6), (1.0, lambda x: x.w >= 0.6)],
    "fen": [(1.5, lambda x: x.h < 50), (2.0, lambda x: x.w >= 0.8), (1.0, lambda x: x.s < 1)],
    "coast": [(2.0, lambda x: x.c < 1), (1.0, lambda x: x.h < 20)],
    "saltmarsh": [(1.5, lambda x: x.c < 2), (1.5, lambda x: x.h < 3), (1.0, lambda x: x.w >= 0.7)],
    "rock": [(4.0, lambda x: x.s >= 30)],
}
# deep forest is woodland far from any settlement, decided after siting (stage 1 §11a)

# natural cover before anyone settles, by terrain (stage 1 §3.6); the engine's covers and D2-185's four new ones
NATURAL = {"river floodplain": "meadow", "river terrace": "pasture", "clay vale": "forest", "lowland loam": "forest",
           "sandy heath": "heath", "chalk down": "pasture", "woodland": "forest", "deep forest": "forest", "hills": "pasture",
           "upland pasture": "pasture", "moor": "moor", "fen": "fen", "coast": "pasture", "saltmarsh": "saltmarsh", "rock": "rock"}

# what a land use may become on each terrain (stage 1 §11b): fields only where they can grow; built ground where it can stand
FIELD_OK = {"river floodplain", "river terrace", "clay vale", "lowland loam", "sandy heath", "chalk down", "hills", "coast"}
BUILT_OK = {"river terrace", "lowland loam", "clay vale", "chalk down", "coast", "hills", "sandy heath"}
MEADOW_OK = {"river floodplain", "fen", "river terrace"}
WOOD_OK = {"woodland", "deep forest", "clay vale", "lowland loam", "hills"}
WASTE_COVER = {"sandy heath": "heath", "moor": "moor", "fen": "fen", "saltmarsh": "saltmarsh", "rock": "rock", "hills": "scrub",
               "upland pasture": "scrub", "chalk down": "scrub", "coast": "scrub"}

# ---------------------------------------------------------------------- roads (stage 1 §11f)
PACE_KMH = {"road": 4.0, "field": 3.5, "built": 3.5, "meadow": 3.0, "pasture": 3.0, "heath": 3.0, "scrub": 2.5, "forest": 2.0,
            "moor": 1.5, "fen": 1.0, "saltmarsh": 1.0, "rock": 0.8}
ROAD_TERRAIN = {"field": "farmland", "built": "farmland", "meadow": "farmland", "pasture": "plain", "heath": "plain",
                "scrub": "plain", "forest": "woodland", "moor": "marsh", "fen": "marsh", "saltmarsh": "marsh", "rock": "hills"}
FORD_MAX = 2                       # a river of class 2 (medium) or less can be forded anywhere it is not a lake; large at a ford
PASS_M = 100.0                     # a pass: the road's high point with land this much lower on both sides
NARROWS_DEG = 20.0

# ---------------------------------------------------------------------- resources by cover (stage 1 §11b), {K, S, r} a parcel's
# unit of size, from the hand-made worlds (combe_base, hollins2: plants about 1 a unit, grass about 30 a unit on pasture and
# meadow, 10 on scrub, game about 1.3 a unit in a managed wood and 3.5 in old forest); wood by kind is D2-156's (data.FORESTS)
PER_UNIT = {
    "pasture": {"plants": 1.0, "grass": 30.0},
    "meadow": {"plants": 1.3, "grass": 27.0},
    "scrub": {"plants": 1.0, "grass": 10.0},
    "heath": {"plants": 0.6, "grass": 6.0},
    "moor": {"plants": 0.5, "grass": 8.0},
    "fen": {"plants": 1.0, "grass": 10.0},
    "saltmarsh": {"plants": 0.5, "grass": 12.0},
    "forest": {"plants": 1.2},
}
GAME_PER_UNIT = {"managed wood": 1.3, "copse": 0.5, "old forest": 3.5}
SEAM = {"S": 60, "K": 60}          # copper ore in a seam (region_c's Coppergate size)

# ---------------------------------------------------------------------- the vocabulary (D2-173; stage 1 §11c)
WORDS = {
    "short_of": "the settlement's share of that flow in the region's bottom quarter",
    "plenty_of": "the settlement's share of that flow in the region's top quarter",
    "soil": {"rich": [1.2, 1.4], "poor": [0.6, 0.8]},
    "land": {"land-pressed": [0.8, 0.9], "land-rich": [0.4, 0.5]},     # its capacity target (D2-16)
}

# ---------------------------------------------------------------------- named configurations (D2-188; stage 1 §11k), as data:
# primitives in window fractions (0 to 1 across, 0 south to 1 north), each with a name whose anchors pins can use
CONFIGS = {
    "plain": [],
    "coast": [{"kind": "coast", "name": "coast", "side": "west", "at": 0.15}],
    "twin bays split by a spur": [
        {"kind": "coast", "name": "coast", "side": "west", "at": 0.12},
        {"kind": "inlet", "name": "north_bay", "from": [0.0, 0.70], "to": [0.46, 0.66], "width": 0.07},
        {"kind": "inlet", "name": "south_bay", "from": [0.0, 0.30], "to": [0.46, 0.34], "width": 0.07},
        {"kind": "ridge", "name": "spur", "from": [0.02, 0.5], "to": [0.64, 0.5], "height": 380, "width": 0.05, "gaps": [0.78]},
        {"kind": "massif", "name": "east_hills", "at": [0.86, 0.5], "r": 0.16, "height": 220}],
    "gated valley": [
        {"kind": "ridge", "name": "north_wall", "from": [0.0, 0.82], "to": [1.0, 0.82], "height": 450, "width": 0.07},
        {"kind": "ridge", "name": "south_wall", "from": [0.0, 0.18], "to": [1.0, 0.18], "height": 450, "width": 0.07},
        {"kind": "ridge", "name": "east_wall", "from": [0.9, 0.18], "to": [0.9, 0.82], "height": 420, "width": 0.07},
        {"kind": "ridge", "name": "gate_wall", "from": [0.18, 0.18], "to": [0.18, 0.82], "height": 420, "width": 0.05,
         "gaps": [0.5], "gap_width": 0.02, "gap_depth": 0.97},
        {"kind": "river", "name": "valley_river", "through": [[0.86, 0.52], [0.5, 0.5], [0.18, 0.5], [0.0, 0.48]]}],
    "two valleys over a pass": [
        {"kind": "ridge", "name": "divide", "from": [0.0, 0.5], "to": [1.0, 0.5], "height": 520, "width": 0.09, "gaps": [0.5],
         "gap_depth": 0.45},
        {"kind": "river", "name": "north_river", "through": [[0.0, 0.78], [0.5, 0.74], [1.0, 0.76]]},
        {"kind": "river", "name": "south_river", "through": [[1.0, 0.24], [0.5, 0.26], [0.0, 0.22]]}],
    "river through a range": [
        {"kind": "ridge", "name": "range", "from": [0.5, 0.0], "to": [0.5, 1.0], "height": 520, "width": 0.08, "gaps": [0.5],
         "gap_width": 0.025, "gap_depth": 0.95},
        {"kind": "river", "name": "river", "through": [[1.0, 0.56], [0.5, 0.5], [0.0, 0.44]]}],
    "scarp and vale": [
        {"kind": "scarp", "name": "scarp", "from": [0.0, 0.56], "to": [1.0, 0.56], "height": 170, "width": 0.03, "high": "north"},
        {"kind": "geology", "name": "downs", "texture": "chalk", "box": [0.0, 0.56, 1.0, 1.0]},
        {"kind": "geology", "name": "vale", "texture": "clay", "box": [0.0, 0.0, 1.0, 0.5]}],
    "plateau with few ascents": [
        {"kind": "plateau", "name": "plateau", "at": [0.5, 0.55], "r": 0.3, "height": 300, "edge": 0.025,
         "climbs": [0.1, 0.45, 0.78]}],
    "fen with islands": [
        {"kind": "fen", "name": "fen", "at": [0.5, 0.5], "r": 0.36},
        {"kind": "massif", "name": "island_1", "at": [0.38, 0.6], "r": 0.05, "height": 18},
        {"kind": "massif", "name": "island_2", "at": [0.62, 0.55], "r": 0.05, "height": 18},
        {"kind": "massif", "name": "island_3", "at": [0.5, 0.36], "r": 0.05, "height": 18}],
    "confluence plain": [
        {"kind": "river", "name": "north_river", "through": [[0.0, 0.85], [0.3, 0.65], [0.5, 0.5]]},
        {"kind": "river", "name": "south_river", "through": [[0.0, 0.15], [0.3, 0.35], [0.5, 0.5]]},
        {"kind": "river", "name": "confluence", "through": [[0.5, 0.5], [0.75, 0.5], [1.0, 0.48]]}],
    "isthmus": [
        {"kind": "sea", "name": "sea"},
        {"kind": "landmass", "name": "west_land", "at": [0.24, 0.5], "r": 0.22},
        {"kind": "landmass", "name": "east_land", "at": [0.76, 0.5], "r": 0.22},
        {"kind": "landmass", "name": "neck", "from": [0.24, 0.5], "to": [0.76, 0.5], "r": 0.035}],
    "coastal strip under mountains": [
        {"kind": "coast", "name": "coast", "side": "west", "at": 0.14},
        {"kind": "ridge", "name": "mountains", "from": [0.4, 0.0], "to": [0.4, 1.0], "height": 560, "width": 0.1,
         "gaps": [0.3, 0.75], "gap_depth": 0.5}],
    "basin in a ring of hills": [
        {"kind": "ring", "name": "ring", "at": [0.5, 0.5], "r": 0.38, "height": 360, "width": 0.07, "gaps": [0.25]},
        {"kind": "basin", "name": "basin", "at": [0.5, 0.5], "r": 0.3, "depth": 25}],
    "rift": [
        {"kind": "scarp", "name": "west_scarp", "from": [0.36, 0.0], "to": [0.36, 1.0], "height": 160, "width": 0.02, "high": "west"},
        {"kind": "scarp", "name": "east_scarp", "from": [0.64, 0.0], "to": [0.64, 1.0], "height": 160, "width": 0.02, "high": "east"},
        {"kind": "lake", "name": "north_lake", "at": [0.5, 0.72], "r": 0.06},
        {"kind": "lake", "name": "south_lake", "at": [0.5, 0.3], "r": 0.07}],
    "watershed divide": [
        {"kind": "ridge", "name": "divide", "from": [0.0, 0.5], "to": [1.0, 0.5], "height": 300, "width": 0.14}],
    "settled lowland and frontier": [
        {"kind": "wild", "name": "frontier", "box": [0.55, 0.0, 1.0, 1.0]},
        {"kind": "massif", "name": "frontier_hills", "at": [0.85, 0.6], "r": 0.2, "height": 160}],
    "delta": [
        {"kind": "coast", "name": "coast", "side": "south", "at": 0.15},
        {"kind": "river", "name": "river", "through": [[0.5, 1.0], [0.48, 0.5], [0.5, 0.1]]},
        {"kind": "fen", "name": "delta", "at": [0.5, 0.18], "r": 0.12}],
}
# waiting for later systems (D2-188): a tidal island (tides), a karst plateau (water as a need, L-23), a mountain lake above a valley
# (floods), a fjord coast and an archipelago (water travel, L-38)
WAITING = {"tidal island", "karst plateau", "mountain lake", "fjord coast", "archipelago"}
