"""Settlement (stage 1 §4, §5, §11e; D2-175, D2-181, D2-184): sites scored on the land, pinned ones first; each settlement's
land taken outward in rings and sized by its capacity target, not by its reach; the land grouped into parcels.

A settlement's people are its households x their size; the land it is given keeps them at 60 to 70% of what its scarcest flow
could keep (D2-161), food from its fields and wild land as capacity.py counts it, heat from its woods' yearly flow
(capacity.wood_flow). A pin (`short of wood`, `land-pressed`) moves that settlement's targets (stage 1 §11c)."""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field as dfield

import numpy as np

from cybertron2.engine import capacity as CAP, forests as FO
from cybertron2.engine.data import PHYSICS
from cybertron2.landgen import field as F, keyed, physical as P, vocab as V
from cybertron2.landgen.physical import Land

FORBIDDEN = {"water", "rock", "fen", "moor", "saltmarsh"}


class Refused(Exception):
    """A pin the land cannot meet (a physics check: D2-180)."""


@dataclass
class Parcel:
    pid: str
    use: str                       # built, field, meadow, pasture, wood, waste, water
    cover: str
    cells: list
    size: int = 1
    side: str = "centre"
    height: int = 1
    adj: list = dfield(default_factory=list)
    fertility: float = 1.0
    terrain: str = ""
    soil: str = ""
    wood_kind: str | None = None
    facts: dict = dfield(default_factory=dict)
    eco: str = ""                  # its ecosystem (ecology.py): the commonest among its cells
    band: int = 0                  # a wood's depth: 1 edge, 2 interior, 3 core


@dataclass
class Settlement:
    key: str
    site: tuple
    pin: dict
    households: int
    people: int
    targets: dict                  # food and heat: the share of capacity the people use (D2-161)
    parcels: list = dfield(default_factory=list)
    name: str = ""
    kind: str = "village"          # village, stop, wild
    facts: dict = dfield(default_factory=dict)


def hearth_heat(base: dict) -> float:
    """Heat a hearth needs in a year with the base world's calendar (capacity.hearth_heat, without a World)."""
    sd = int((base.get("calendar") or {}).get("season_days", 6))
    year = 4 * sd
    return (year - sd) * float(PHYSICS["heat"]["normal"]) + sd * float(PHYSICS["heat"]["cold"])


def wood_flow(kind: str, size: int = 1) -> float:
    return CAP.wood_flow({"res": FO.seed("forest" if kind != "scrub" else "scrub", size, {"wood": {"kind": kind}})})


# ---------------------------------------------------------------------- sites
def site_score(L: Land) -> np.ndarray:
    g = L.g
    water = (L.river >= 1) | L.spring | L.lake | (L.c < 0.4)
    _, wd = P._spread(g, water, np.ones(g.shape), 3, how="near")
    near_water = np.isfinite(wd)
    tn = np.array(P.TERRAIN_NAMES, dtype=object)[L.terrain]
    field_ok = np.isin(tn, list(V.FIELD_OK))
    fertile = F.box_mean(np.where(field_ok, L.fert, 0.0), 7)
    _, xd = P._spread(g, (L.river >= 1) & (L.river <= 2), np.ones(g.shape), 3, how="near")
    fuel = F.box_mean((L.cover == "forest").astype(float), 15)
    kinds = sum((F.box_mean((L.terrain == i).astype(float), 10) > 0.05).astype(int) for i in range(len(P.TERRAIN_NAMES) - 1))
    score = (2.0 * near_water + 1.0 * (L.slope < 4) + 3.0 * fertile + 0.8 * np.isfinite(xd) + 1.5 * np.minimum(fuel * 4, 1)
             + 1.0 * (L.f >= 2) + 0.3 * np.minimum(kinds, 4))
    bad = np.isin(tn, list(FORBIDDEN)) | ~np.isin(tn, list(V.BUILT_OK)) | L.sea | L.lake | (L.river >= 2)
    margin = int(2.0 / g.km)
    bad[:margin, :] = bad[-margin:, :] = bad[:, :margin] = bad[:, -margin:] = True
    return np.where(bad, -np.inf, score)


def _pin_mask(L: Land, pin: dict, name: str) -> np.ndarray:
    g = L.g
    ok = np.ones(g.shape, dtype=bool)
    if pin.get("at") is not None:
        at = pin["at"]
        if isinstance(at, str):
            if at not in L.anchors:
                raise Refused(f"{name}: no anchor called {at!r} (anchors: {', '.join(sorted(L.anchors)) or 'none'})")
            at = L.anchors[at]
        ok &= np.hypot(g.x - at[0], g.y - at[1]) <= 4.0
    if pin.get("terrain"):
        t = pin["terrain"]
        if t not in P.TERRAIN_NAMES:
            raise Refused(f"{name}: no terrain called {t!r}")
        near = F.box_mean((L.terrain == P.TERRAIN_NAMES.index(t)).astype(float), 6) > 0.3
        ok &= near
    on = pin.get("on")
    if on == "river":
        _, d = P._spread(g, L.river >= 2, np.ones(g.shape), 4, how="near")
        ok &= np.isfinite(d)
    elif on == "sea":
        ok &= L.c < 1.5
    elif on == "lake":
        _, d = P._spread(g, L.lake, np.ones(g.shape), 4, how="near")
        ok &= np.isfinite(d)
    for res in pin.get("resources") or []:                                 # "copper in the hills", "stone": the ore or the rock near
        src = L.ore if res == "copper" else np.isin(L.terrain, [P.TERRAIN_NAMES.index(t) for t in ("hills", "rock", "chalk down")])
        lim = 0.9 * float(L.conf["field_km"]) / g.km                      # within the land's reach, so the seam can be its own
        _, d = P._spread(g, src, np.ones(g.shape), int(lim), how="near")   # (_spread's steps can chain several cells, so the
        ok &= d <= lim                                                     # distance itself is the test: it was 4 km, and no mine)
    soil = pin.get("soil")                                                 # the vocabulary (stage 1 §11c)
    if soil in V.WORDS["soil"]:
        lo, hi = V.WORDS["soil"][soil]
        fert = F.box_mean(L.fert, 5)
        ok &= (fert >= lo - 0.15) if soil == "rich" else (fert <= hi + 0.05)
    land_ = ~(L.sea | L.lake)
    for word in ("wet", "dry", "sheltered", "exposed"):
        if pin.get(word) or word in (pin.get("is") or []):
            if word in ("wet", "dry"):
                mm = F.box_mean(L.moist, 6)
                cut = np.percentile(mm[land_], 70 if word == "wet" else 30)
                ok &= (mm >= cut) if word == "wet" else (mm <= cut)
            else:
                rel = L.h - F.box_mean(L.h, 15)                            # below its surroundings: a hollow; above: open ground
                ok &= (rel <= -5) if word == "sheltered" else ((rel >= 5) & (L.h >= np.percentile(L.h[land_], 60)))
    for h in pin.get("has") or []:
        if h == "ford":
            _, d = P._spread(g, (L.river >= 1) & (L.river <= V.FORD_MAX), np.ones(g.shape), 4, how="near")
            ok &= np.isfinite(d)
        elif h == "mill site":
            _, d = P._spread(g, (L.river >= 2) & (L.slope >= 0.6), np.ones(g.shape), 6, how="near")
            ok &= np.isfinite(d)
    return ok


def choose_sites(L: Land, conf: dict, places: dict) -> list:
    """Pinned places first, each where its pins allow and the land scores best; then the rest by score, at least spacing_km
    apart (D2-182). A pin no cell can meet is refused with the reason (D2-180)."""
    g = L.g
    score = site_score(L)
    sites, keys = [], []
    taken = np.zeros(g.shape, dtype=bool)

    def take(r, c, key):
        sites.append((r, c))
        keys.append(key)
        nonlocal taken
        taken |= np.hypot(g.x - g.x[r, c], g.y - g.y[r, c]) < conf["spacing_km"]

    day_km = conf["road_day_hours"] * 3.0                                  # a day's walk, about 24 km on mixed ground
    is_ = lambda pin, w: bool(pin.get(w) or w in (pin.get("is") or []))
    first = {k: p for k, p in places.items() if p.get("kind") != "wild" and not is_(p, "at a crossroads") and not p.get("days_out")}
    later = {k: p for k, p in places.items() if p.get("kind") != "wild" and k not in first}
    site_of = {}

    def place(name, pin, extra=None):
        nonlocal taken
        m = _pin_mask(L, pin, name) & np.isfinite(score) & ~taken
        if extra is not None:
            m &= extra
        if not m.any():
            raise Refused(f"{name}: no site meets its pins {pin} at least {conf['spacing_km']} km from the others")
        idx = np.argmax(np.where(m, score, -np.inf))
        r, c = divmod(int(idx), g.nx)
        take(r, c, name)
        site_of[name] = (r, c)
        if is_(pin, "remote"):                                             # at least two days from the rest: keep the others off
            taken |= np.hypot(g.x - g.x[r, c], g.y - g.y[r, c]) < 2 * day_km * 0.75

    for name, pin in first.items():
        place(name, pin)
    n = int(conf["settlements"]) - len(later)
    while len(sites) < n:
        free = np.isfinite(score) & ~taken
        if not free.any():
            break                                                          # the land holds no more at this spacing: the report says so
        idx = np.argmax(np.where(free, score, -np.inf))
        take(*divmod(int(idx), g.nx), f"s{len(sites) + 1}")
    for name, pin in later.items():
        extra = None
        if pin.get("days_out"):                                            # `days_out: {from: Name, days: n}`
            src = site_of.get(pin["days_out"]["from"])
            if src is None:
                raise Refused(f"{name}: days_out from {pin['days_out']['from']!r}, which is not a pinned place placed before it")
            d = np.hypot(g.x - g.x[src], g.y - g.y[src])
            days = float(pin["days_out"]["days"])
            extra = (d >= 0.55 * days * day_km) & (d <= 1.0 * days * day_km)
        if is_(pin, "at a crossroads") and sites:                          # where the others' roads would meet: the most central site
            dsum = sum(np.hypot(g.x - g.x[s_], g.y - g.y[s_]) for s_ in sites)
            central = dsum <= np.percentile(dsum[np.isfinite(score)], 25)
            extra = central if extra is None else extra & central
            nonlocal_taken = taken.copy()
            taken = np.zeros(g.shape, dtype=bool)                          # a crossroads may stand nearer its neighbours
            for s_ in sites:
                taken |= np.hypot(g.x - g.x[s_], g.y - g.y[s_]) < 0.45 * conf["spacing_km"]
            place(name, pin, extra)
            taken |= nonlocal_taken
            continue
        place(name, pin, extra)
    return list(zip(keys, sites))


# ---------------------------------------------------------------------- land in rings
def _cost_from(L: Land, site, radius_km: float) -> dict:
    """Hours to each cell within radius_km of a site, by the pace of its cover and its slope (stage 1 §11f), never across the sea,
    a lake or a large river."""
    g = L.g
    r0, c0 = site
    lim = int(radius_km / g.km)
    best = {(r0, c0): 0.0}
    heap = [(0.0, r0, c0)]
    while heap:
        t, r, c = heapq.heappop(heap)
        if t > best.get((r, c), math.inf):
            continue
        for (dr, dc), d in zip(F.N8, F.D8):
            rr, cc = r + dr, c + dc
            if not (0 <= rr < g.ny and 0 <= cc < g.nx) or abs(rr - r0) > lim or abs(cc - c0) > lim:
                continue
            if L.sea[rr, cc] or L.lake[rr, cc] or L.river[rr, cc] >= 3:
                continue
            pace = V.PACE_KMH.get(L.cover[rr, cc], 2.5)
            nt = t + d * g.km / pace * (1 + L.slope[rr, cc] / 10.0)
            if nt < best.get((rr, cc), math.inf):
                best[(rr, cc)] = nt
                heapq.heappush(heap, (nt, rr, cc))
    return best


def allocate(L: Land, conf: dict, base: dict, s: Settlement, claimed: np.ndarray) -> dict:
    """The settlement's land, cell by cell, nearest first: built ground, fields to its food target, meadow, pasture, woods to its
    heat target, a little waste. Returns {cell: use}."""
    cost = _cost_from(L, s.site, conf["field_km"])
    order = sorted(cost, key=lambda k: (cost[k], k))
    tn = lambda rc: P.TERRAIN_NAMES[int(L.terrain[rc])]
    out = {}
    free = lambda rc: rc not in out and not claimed[rc] and not L.sea[rc] and not L.lake[rc] and L.river[rc] < 2

    def take(use, n, ok, key=None):
        """n cells for a use, grown as one piece where the land allows: from the best free cell next to land already given (or the
        nearest), adding the best free neighbour each step; a new piece starts only when the old one can grow no more."""
        key = key or (lambda rc: cost[rc])
        got, frontier = [], []
        seen = set()

        def push(rc):
            if rc in cost and rc not in seen and free(rc) and ok(rc):
                seen.add(rc)
                heapq.heappush(frontier, (key(rc), rc))

        for rc in out:
            for dr, dc in F.N8:
                push((rc[0] + dr, rc[1] + dc))
        while len(got) < n:
            if not frontier:
                start = next((rc for rc in order if rc not in seen and free(rc) and ok(rc)), None)
                if start is None:
                    break
                push(start)
                continue
            _, rc = heapq.heappop(frontier)
            if not free(rc):
                continue
            out[rc] = use
            got.append(rc)
            for dr, dc in F.N8:
                push((rc[0] + dr, rc[1] + dc))
        return len(got)

    hh = s.households
    take("built", max(1, math.ceil(hh / 3)), lambda rc: tn(rc) in V.BUILT_OK)
    for res in s.pin.get("resources") or []:                                # a pinned seam or quarry first, as it cannot move: the nearest such ground
        want = (lambda rc: bool(L.ore[rc])) if res == "copper" else (lambda rc: tn(rc) in ("hills", "rock", "chalk down"))
        s.facts[f"mine_{res}"] = take("mine", 2, want)
        if not s.facts[f"mine_{res}"]:                                       # a pin not met is refused, never dropped (D2-180)
            raise Refused(f"{s.key}: its {res} is beyond the land it can work ({conf['field_km']} km)")
    keep_food = s.people / s.targets["food"]
    keep_heat = s.people / s.targets["heat"]
    waste_units = 2 + hh // 2
    heat_need = keep_heat / CAP.PEOPLE_A_HEARTH * hearth_heat(base) / CAP.FIREWOOD_HEAT
    units = max(1, math.ceil(heat_need / wood_flow("managed wood")))
    # the wild food capacity.node counts is the woods' (WILD a unit of forest or scrub), so the fields are what the woods leave; the
    # waste (heath, moor, fen) is not counted there and so not here (it was, and the woods were not: villages came out short of
    # their target, and a food_share above 1 could not be met)
    wild_food = units * CAP.WILD
    year = 4 * int((base.get("calendar") or {}).get("season_days", 6))   # a ration a day for the world's year (capacity.node)
    exact = s.pin.get("food_share") is not None                         # a pinned share is met as near as a plot allows, not rounded up
    plots = max(2, (round if exact else math.ceil)((keep_food * year - wild_food) / (CAP.PLOT["grain"] - CAP.PLOT["seed"])))
    s.facts["plots_wanted"] = plots
    s.facts["fields"] = take("field", plots, lambda rc: tn(rc) in V.FIELD_OK, key=lambda rc: cost[rc] - 2.0 * L.fert[rc])
    take("meadow", max(1, hh // 2), lambda rc: tn(rc) in V.MEADOW_OK or L.wet[rc] > 0.75)
    take("pasture", hh + 1, lambda rc: tn(rc) not in ("rock",))
    s.facts["wood_wanted"] = units
    s.facts["woods"] = take("wood", units, lambda rc: L.cover[rc] == "forest" or tn(rc) in V.WOOD_OK)
    s.facts["waste"] = take("waste", waste_units, lambda rc: tn(rc) in V.WASTE_COVER or L.cover[rc] in ("heath", "moor", "fen"))
    near_water = [rc for rc in order[:400] if (L.river[rc] >= 2 or L.lake[rc]) and not claimed[rc]]
    for rc in near_water[:2]:
        out[rc] = "water"
    return out


# ---------------------------------------------------------------------- parcels
def _components(cells: set) -> list:
    left, comps = set(cells), []
    while left:
        start = left.pop()
        comp, todo = [start], [start]
        while todo:
            r, c = todo.pop()
            for dr, dc in F.N8:
                n = (r + dr, c + dc)
                if n in left:
                    left.remove(n)
                    comp.append(n)
                    todo.append(n)
        comps.append(sorted(comp))
    return comps


def parcels(L: Land, conf: dict, s: Settlement, land: dict) -> list:
    """Cells grouped into parcels by use: connected pieces, the smallest merged into a neighbour until there are no more than the
    most a node may have, the largest field split until there are at least the fewest (stage 1 §5, D2-116)."""
    lo, hi = conf["parcels"]
    groups = []
    for use in ("built", "field", "meadow", "pasture", "wood", "waste", "mine", "water"):
        for comp in _components({rc for rc, u in land.items() if u == use}):
            groups.append([use, comp])

    def neighbours(i):
        cells = set(groups[i][1])
        out = set()
        for j, (_, comp) in enumerate(groups):
            if j != i and any((r + dr, c + dc) in cells for r, c in comp for dr, dc in F.N8):
                out.add(j)
        return out

    def merge_once(force=False):
        """Merge the smallest piece into a neighbour of the same use; when forced (too many parcels), into its largest neighbour
        that is not built ground or water."""
        order = sorted(range(len(groups)), key=lambda i: (len(groups[i][1]), groups[i][0], groups[i][1][0]))
        for i in order:
            if groups[i][0] in ("built", "water", "mine"):
                continue
            nb = neighbours(i)
            same = [j for j in nb if groups[j][0] == groups[i][0]]
            other = sorted((j for j in nb if groups[j][0] not in ("built", "water")), key=lambda j: -len(groups[j][1]))
            j = same[0] if same else (other[0] if force and other else None)
            if j is None:
                continue
            groups[j][1] = sorted(groups[j][1] + groups[i][1])
            del groups[i]
            return True
        return False

    while merge_once():
        pass

    def centre(cs):
        return (sum(r for r, _ in cs) / len(cs), sum(c for _, c in cs) / len(cs))

    for i in sorted(range(len(groups)), key=lambda i: -len(groups[i][1])):          # a lone small piece joins the nearest piece of
        if i >= len(groups) or len(groups[i][1]) > 1 or groups[i][0] in ("built", "water"):   # its use, even if apart (one parcel
            continue                                                                  # may lie in two places, as fields do)
        same = [j for j in range(len(groups)) if j != i and groups[j][0] == groups[i][0]]
        if same:
            ci = centre(groups[i][1])
            j = min(same, key=lambda j: math.dist(ci, centre(groups[j][1])))
            groups[j][1] = sorted(groups[j][1] + groups[i][1])
            del groups[i]
    while len(groups) > hi and merge_once(force=True):
        pass
    big = lambda: [i for i, (u, cs) in enumerate(groups) if u == "field" and len(cs) > 8]
    while big() and len(groups) < hi:                                      # large arable in two or three great fields, as open fields
        i = max(big(), key=lambda i: len(groups[i][1]))                     # were (generator.md §10; D2-172's holdings sit in them)
        cs = groups[i][1]
        rs, cl = [r for r, _ in cs], [c for _, c in cs]
        axis = 0 if (max(rs) - min(rs)) >= (max(cl) - min(cl)) else 1
        cs = sorted(cs, key=lambda rc: rc[axis])
        groups[i][1] = cs[: len(cs) // 2]
        groups.append(["field", cs[len(cs) // 2:]])
    while len(groups) < lo:
        fields = [i for i, (u, cs) in enumerate(groups) if u in ("field", "pasture", "wood") and len(cs) >= 4]
        if not fields:
            break
        i = max(fields, key=lambda i: len(groups[i][1]))
        cs = groups[i][1]
        rs, cl = [r for r, _ in cs], [c for _, c in cs]
        axis = 0 if (max(rs) - min(rs)) >= (max(cl) - min(cl)) else 1
        cs = sorted(cs, key=lambda rc: rc[axis])
        groups[i][1] = cs[: len(cs) // 2]
        groups.append([groups[i][0], cs[len(cs) // 2:]])
    out = []
    sr, sc = s.site
    for k, (use, cs) in enumerate(groups):
        p = Parcel(f"{s.key}_{k}", use, "", cs, size=len(cs))
        rr = np.array([r for r, _ in cs])
        cc = np.array([c for _, c in cs])
        mx, my = float(L.g.x[rr, cc].mean()), float(L.g.y[rr, cc].mean())
        dx, dy = mx - L.g.x[sr, sc], my - L.g.y[sr, sc]
        p.side = "centre" if math.hypot(dx, dy) < 0.2 else (("east" if dx > 0 else "west") if abs(dx) > abs(dy) else ("north" if dy > 0 else "south"))
        wet, f, h, sl = float(L.wet[rr, cc].mean()), float(L.f[rr, cc].mean()), float(L.h[rr, cc].mean()), float(L.slope[rr, cc].mean())
        p.height = 0 if (use == "water" or f < 2 or wet > 0.8) else (3 if h > L.h[sr, sc] + 60 else (2 if sl > 5 else 1))
        ts = [P.TERRAIN_NAMES[int(L.terrain[r, c])] for r, c in cs]
        p.terrain = max(set(ts), key=ts.count)
        texs = [V.TEXTURE[int(L.tex[r, c])] for r, c in cs]
        p.soil = max(set(texs), key=texs.count)
        p.fertility = round(float(L.fert[rr, cc].mean()), 2)
        ecos = [L.eco[r, c] for r, c in cs] if L.eco is not None else []
        p.eco = max(set(ecos), key=ecos.count) if ecos else ""
        from cybertron2.landgen import ecology as EC
        waste = EC.ECOSYSTEMS.get(p.eco, ("scrub",))[0]                    # the waste as its ground has become (heath, moor, fen ...)
        if waste in ("forest", "field", "built", "water", "meadow"):          # grassland waste is the common's rough grazing
            waste = V.WASTE_COVER.get(p.terrain, "scrub")
        p.cover = {"built": "built", "field": "field", "meadow": "meadow", "pasture": "pasture", "wood": "forest", "water": "water",
                   "waste": waste, "mine": "rock"}[use]
        if use == "wood":
            p.wood_kind = "managed wood"                                   # a village's own wood is worked (coppiced), whatever its size
            forests = [e for e in ecos if e in EC.FORESTS]
            p.eco = max(set(forests), key=forests.count) if forests else EC.natural_forest(p.terrain)
            bands = [int(L.band[r, c]) for r, c in cs if L.band is not None]
            p.band = max(1, min(2, max(bands) if bands else 1))           # a village's wood is worked: edge or interior, never core
        if p.cover == "scrub":
            p.wood_kind = "scrub"
        p.facts = {"terrain": p.terrain, "soil": p.soil, "height_m": round(h), "slope": round(sl, 1), "wet": round(wet, 2),
                   "river": int(L.river[rr, cc].max()), "spring": bool(L.spring[rr, cc].any()), "seam": bool(L.ore[rr, cc].any())}
        out.append(p)
    cell_of = {rc: i for i, p in enumerate(out) for rc in p.cells}
    adj = {i: set() for i in range(len(out))}
    for i, p in enumerate(out):
        for r, c in p.cells:
            for dr, dc in F.N8:
                j = cell_of.get((r + dr, c + dc), i)
                if j != i:
                    adj[i].add(j)
                    adj[j].add(i)
    cen = [centre(p.cells) for p in out]
    while True:                                                            # the parcel graph is connected: a piece that touches none
        comp, todo = {0}, [0]                                              # of the rest is next to the nearest parcel of the rest
        while todo:
            for j in adj[todo.pop()]:
                if j not in comp:
                    comp.add(j)
                    todo.append(j)
        rest = [j for j in range(len(out)) if j not in comp]
        if not rest:
            break
        a, b = min(((a, b) for a in comp for b in rest), key=lambda ab: math.dist(cen[ab[0]], cen[ab[1]]))
        adj[a].add(b)
        adj[b].add(a)
    for i, p in enumerate(out):
        p.adj = sorted(out[j].pid for j in adj[i])
    return out


def settle(L: Land, conf: dict, base: dict, places: dict) -> list:
    """Sites, households, targets, land and parcels for every settlement, in order (pinned first)."""
    chosen = choose_sites(L, conf, places)
    P.deep_forest(L, [rc for _, rc in chosen])
    claimed = np.zeros(L.g.shape, dtype=bool)
    out = []
    for key, site in chosen:
        pin = places.get(key) or {}
        rg = keyed.rng(L.g.seed, "households", key)
        lo, hi = conf["households"]
        hh = int(pin.get("households") or rg.randint(lo, hi))
        clo, chi = conf["capacity"]
        food = heat = rg.uniform(clo, chi)
        land_word = V.WORDS["land"].get(pin.get("land", ""))
        if land_word:
            food = heat = rg.uniform(*land_word)
        for x in (pin.get("short_of") or []):
            if x == "wood":
                heat = 0.9
            elif x == "food":
                food = 0.9
        for x in (pin.get("plenty_of") or []):
            if x == "wood":
                heat = 0.4
            elif x == "food":
                food = 0.45
        if pin.get("food_share") is not None:                              # people / what its land feeds, exactly: above 1 a village
            food = float(pin["food_share"])                                # that must buy food (L-50's ladder)
        if pin.get("heat_share") is not None:
            heat = float(pin["heat_share"])
        people = int((conf.get("_people") or {}).get(key) or hh * int(conf["household_size"]))   # the people generated, on a second pass
        s = Settlement(key, site, pin, hh, people, {"food": food, "heat": heat})
        land = allocate(L, conf, base, s, claimed)
        for rc in land:
            claimed[rc] = True
        s.parcels = parcels(L, conf, s, land)
        out.append(s)
    return out
