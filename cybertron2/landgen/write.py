"""From a world file with gaps to a complete world file (stage 1 §1, §6 to §8; D2-173, D2-177, D2-179, D2-180, D2-184, D2-186,
D2-187): the land, settlements and roads become nodes, parcels, roads, buildings, herds, claims and lines in today's format; the
people come from generate.py, unchanged; descriptions are templates from facts, or written once by a model and frozen; the checks
run; the cells are saved beside the world.

What the world file gives is pinned. Under `generate:`: seed, size_km, km, settlements, configuration, configuration_params,
features (primitives), places ({name: pins}), require (design checks that refuse), allow (economic checks a designed hardship may
fail: economy.py, review 02zl), and any default in vocab.DEFAULTS. Everything else
in the file (calendar, lifespan, children, cast, `base:`) is kept as written and is what the generated parts sit in (stage 1 §11j).
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os

import numpy as np
import yaml

from cybertron2.landgen import field as F, keyed, macro as M, names as NM, physical as P, roads as R, settle as ST, vocab as V

SURNAMES = ["Reed", "Barrow", "Hale", "Cole", "Moor", "Webb", "Thorne", "Hunt", "Fenn", "Ash", "Lowe", "Bell", "Wynn", "Cotter",
            "Rook", "Hobb", "Fletcher", "Cooper", "Carter", "Dyer", "Wright", "Brook", "Hayward", "Shepherd", "Gale", "Marsh", "Holt",
            "Ward", "Pike", "Crane", "Hart", "Lamb", "Kemp", "Sayer", "Tanner", "Fowler", "Mason", "Wood", "Field", "Croft"]
FARMING = ["sow", "reap", "hoe", "weed", "milk", "select seed"]
TRADES = {"smith": ["smelt", "copper tool", "coin"], "mason": ["quarry"], "carpenter": ["medium room"], "trapper": ["hunt"],
          "miller": ["mill"]}
RES_R = {"plants": 0.3, "grass": 0.32, "game": 0.25}


def _conf(gen: dict) -> dict:
    conf = dict(V.DEFAULTS)
    conf.update({k: v for k, v in gen.items() if k in V.DEFAULTS})
    return conf


def _base_settings(spec: dict, path: str | None) -> dict:
    """The settings the generated world sits in: the file's own keys over its `base:` (read, not copied)."""
    if spec.get("base") and path:
        from cybertron2.engine.world import load_spec, merge
        b = spec["base"]
        bp = b if os.path.exists(b) else os.path.join(os.path.dirname(path), os.path.basename(b))
        return merge(load_spec(bp), {k: v for k, v in spec.items() if k not in ("base", "generate")})
    return {k: v for k, v in spec.items() if k != "generate"}


def _state(p, seam: bool = False) -> dict:
    """A parcel's resources in the engine's form, per unit of size from the hand-made worlds (vocab.PER_UNIT, stage 1 §11b)."""
    st = {}
    for k, v in V.PER_UNIT.get(p.cover, {}).items():
        K = round(v * p.size, 1)
        st[k] = {"K": K, "S": K, "r": RES_R[k]}
    if p.wood_kind:
        st["wood"] = {"kind": p.wood_kind}
    g = V.GAME_PER_UNIT.get(p.wood_kind or "")
    if g:
        K = round(g * p.size, 1)
        st["game"] = {"K": K, "S": K, "r": RES_R["game"]}
    if seam and p.cover == "rock":
        st["seam"] = dict(V.SEAM)
    return st


def _words(p) -> dict:
    """A parcel's facts in words, as a model is given them to describe (no numbers; only what is there)."""
    f = p.facts
    out = {"what": _text(p, ""), "land": p.terrain, "soil": {"clay": "heavy clay", "sand": "light sand", "chalk": "thin chalk",
                                                             "loam": "loam"}.get(p.soil, p.soil),
           "lie": {0: "low by the water", 1: "on the level", 2: "on a slope", 3: "up on the tops"}[p.height],
           "size": "small" if p.size <= 2 else ("middling" if p.size <= 6 else "large")}
    wet = f.get("wet", 0)
    if wet > 0.75:
        out["ground"] = "wet underfoot"
    elif wet < 0.3:
        out["ground"] = "dry"
    if f.get("river", 0) >= 2:
        out["water"] = "a river beside it"
    elif f.get("river", 0) == 1:
        out["water"] = "a brook running through it"
    if f.get("spring"):
        out["spring"] = "a spring rises here"
    if f.get("slope", 0) > 8:
        out["slope"] = "steep"
    return out


def _text(p, node_name: str) -> str:
    """A template description from a parcel's facts (the fallback when no model writes it, D2-179)."""
    words = {"built": "houses round a trodden green", "field": "ploughland", "meadow": "hay meadow", "pasture": "grazing",
             "forest": {"old forest": "old oak and beech, deep and dim", "copse": "a small copse of ash and hazel",
                        "managed wood": "coppiced hazel under oak standards"}.get(p.wood_kind or "", "woodland"),
             "heath": "heather and gorse on thin sand", "moor": "wet peaty moor", "fen": "reed and sedge over standing water",
             "saltmarsh": "salt grass and creeks", "scrub": "thorn and rough grass", "rock": "bare rock and scree",
             "water": "running water"}.get(p.cover, p.cover)
    soil = {"clay": "heavy clay", "sand": "light sand", "chalk": "thin chalky soil", "loam": "good loam"}.get(p.soil, p.soil)
    where = {0: "low by the water", 1: "", 2: "on the slope", 3: "up on the tops"}[p.height]
    bits = [words] + ([f"on {soil}"] if p.cover in ("field", "meadow", "pasture") else []) + ([where] if where else [])
    return ", ".join(bits)


class Describer:
    """Descriptions written once by a model from facts and frozen (D2-179), cached by the hash of the facts; without a model,
    templates."""

    def __init__(self, model: str | None, backend: str | None, cache_path: str | None):
        self.model, self.backend, self.cache_path = model, backend, cache_path
        self.cache = {}
        if cache_path and os.path.exists(cache_path):
            with open(cache_path) as f:
                self.cache = json.load(f)
        self.calls = 0
        self.failed = 0

    def __call__(self, kind: str, facts: dict, fallback: str) -> str:
        if not self.model:
            return fallback
        key = hashlib.sha256(json.dumps([kind, facts, self.model], sort_keys=True).encode()).hexdigest()[:16]
        if key in self.cache:
            return self.cache[key]
        from cybertron import llm
        length = "one sentence of at most 25 words" if kind != "node" else "two or three short sentences"
        system = ("You write short descriptions of places for a world of medieval villages, as a local would see them: plain and "
                  "concrete. Say only what is there: never mention what is absent, never give numbers or measurements, no names of "
                  "people, no invented history, nothing the facts do not support.")
        user = f"Describe this {kind} in {length}. Facts: {json.dumps(facts, sort_keys=True)}"
        schema = {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
        try:
            out, _, _ = llm.call(self.backend or os.environ.get("LLM_BACKEND") or "claude_code", self.model, system, user, schema)
            text = str((out or {}).get("text") or "").strip() or fallback
            self.calls += 1
        except Exception:                                                  # a failed call keeps the template; the report counts it
            text, self.failed = fallback, self.failed + 1
        self.cache[key] = text
        return text

    def save(self):
        if self.cache_path and self.model:
            with open(self.cache_path, "w") as f:
                json.dump(self.cache, f, indent=0, sort_keys=True)


def _place_facts(L, s, roads) -> dict:
    """What a settlement's name may say of it (D2-186)."""
    r, c = s.site
    g = L.g
    rad = lambda km: max(1, int(km / g.km))
    win = lambda a, km: a[max(0, r - rad(km)):r + rad(km) + 1, max(0, c - rad(km)):c + rad(km) + 1]
    tn = np.array(P.TERRAIN_NAMES, dtype=object)
    ford = any("ford" in (st.get("landmarks") or []) for rd in roads if s.key in rd[:2] for st in (rd[3].get("stretches") or {}).values())
    return {"ford": ford or bool((win(L.river, 0.5) == 1).any() or (win(L.river, 0.5) == 2).any()),
            "lake": bool(win(L.lake, 1.0).any()), "wood": bool((win(L.cover, 1.5) == "forest").mean() > 0.3),
            "valley": bool(F.box_mean(L.h, 20)[r, c] - L.h[r, c] > 15), "pasture": any(p.cover == "pasture" and p.size >= 3 for p in s.parcels),
            "sea": bool(L.c[r, c] < 2), "high": bool(L.h[r, c] > 250), "stone": bool(np.isin(win(tn[L.terrain], 2.0), ["hills", "rock"]).any()),
            "wet": bool(np.isin(win(tn[L.terrain], 1.5), ["fen", "saltmarsh"]).any()), "meadow": any(p.cover == "meadow" for p in s.parcels),
            "water": bool((win(L.river, 0.5) >= 1).any()), "mill": "mill site" in (s.pin.get("has") or []),
            "hidden": s.kind == "wild"}


def generate(spec: dict, path: str | None = None, people: bool = False, describe: bool = False, out_path: str | None = None) -> tuple[dict, dict, dict]:
    """A world file with gaps in; (the complete world file, the cells as arrays, the report) out. With people, twice: the land is
    sized first for households of the default size, then again for the people generate.py actually made (its tree depends on the
    lines and the seed, not the land, so the people are the same both times: D2-161 holds for them)."""
    if not people:
        return _generate(spec, path, False, describe, out_path)
    world, cells, report = _generate(spec, path, True, False, None, provisional=True)
    if "capacity, people as generated" not in report["checks"]:
        return world, cells, report                                        # refused on the first pass: the report says why
    counts = {k: v["people"] for k, v in report["checks"]["capacity, people as generated"]["detail"].items()}
    by_key = {v["name"]: k for k, v in report["nodes"].items()}
    spec2 = copy.deepcopy(spec)
    spec2.setdefault("generate", {})["_people"] = {by_key[n]: c for n, c in counts.items() if c}
    return _generate(spec2, path, True, describe, out_path)


def _generate(spec: dict, path, people: bool, describe: bool, out_path, provisional: bool = False) -> tuple[dict, dict, dict]:
    gen = dict(spec.get("generate") or {})
    conf = _conf(gen)
    conf["_people"] = gen.get("_people") or {}
    seed = int(gen.get("seed", spec.get("seed", 1)))
    settings = _base_settings(spec, path)
    report = {"seed": seed, "pins": {}, "targets": {}, "checks": {}, "generated": [], "deviations": [
        "cells on a jittered square grid, not Poisson-disc points with Delaunay neighbours (scipy not installed)",
        "cells saved as .npz, not parquet (pyarrow not installed)",
        "people: generate.py once for the region as it stands (no kin between villages yet: 37.4's, later)"]}
    g = F.grid(seed, conf["size_km"], conf["km"])
    prims = M.primitives(conf)
    kinds = {p_["kind"] for p_ in prims}
    pins = [dict(v or {}) for v in (gen.get("places") or {}).values()]
    if any(p_.get("on") == "sea" or "by the sea" in (p_.get("is") or []) for p_ in pins) and not kinds & {"sea", "coast"}:
        prims.append({"kind": "coast", "name": "coast", "side": gen.get("coast_side", "west"), "at": 0.12})   # words that place a shape
    if any(p_.get("terrain") in ("hills", "upland pasture") or "in the hills" in (p_.get("is") or []) for p_ in pins) \
            and not kinds & {"ridge", "massif", "plateau", "ring"}:
        prims.append({"kind": "massif", "name": "hills", "at": [0.72, 0.62], "r": 0.22, "height": 340})
    if any("on an island" in (p_.get("is") or []) for p_ in pins) and "sea" not in kinds:
        prims = [{"kind": "sea", "name": "sea"}, {"kind": "landmass", "name": "island", "at": [0.5, 0.5], "r": 0.36}] + prims
    L = P.build(conf, g, prims)
    places = {k: dict(v or {}) for k, v in (gen.get("places") or {}).items()}
    settlements = ST.settle(L, conf, settings, places)
    extra, roads, pic = R.build(L, conf, settlements)
    allnodes = settlements + extra
    # names (D2-186): pinned places keep the name they were given
    namer = NM.Namer(seed)
    for k in places:
        namer.used.add(k)
    for s in allnodes:
        s.name = s.key if s.key in places else namer.place(s.key, _place_facts(L, s, roads))
    model = None
    if describe:
        cast = settings.get("cast") or {}
        model = describe if isinstance(describe, str) else ((settings.get("describe") or {}).get("model") or cast.get("middle"))
    out_dir = os.path.dirname(out_path) if out_path else None
    describer = Describer(model, (settings.get("describe") or {}).get("backend"),
                          os.path.join(out_dir, os.path.basename(out_path).split(".")[0] + ".descriptions.json") if out_path else None)
    nodes = {}
    river_name = {s.key: namer.river(s.key) for s in allnodes if any(p.cover == "water" for p in s.parcels)}
    for s in allnodes:
        pars = {}
        for p in s.parcels:
            p.name = namer.parcel(s.name, p, river_name.get(s.key))
            facts = _words(p)
            entry = {"name": p.name, "cover": p.cover, "size": int(p.size), "side": p.side, "height": int(p.height),
                     "text": describer("parcel", facts, _text(p, s.name)), "adj": list(p.adj)}
            if p.cover == "field":
                lo_hi = V.WORDS["soil"].get(s.pin.get("soil", ""))           # `soil: rich | poor` sets the fields' fertility in range
                entry["fertility"] = float(min(max(p.fertility, lo_hi[0]), lo_hi[1]) if lo_hi else p.fertility)
            st = _state(p, seam=bool(s.facts.get("seam")) or (p.use == "mine" and bool(p.facts.get("seam"))))
            if st:
                entry["state"] = st
            entry["terrain"], entry["soil"] = p.terrain, p.soil              # data for stage 2; the engine ignores them now
            pars[p.pid] = entry
        kind_words = {"village": f"a village of {s.households} households", "stop": "a stopping place on the road",
                      "wild": {"forest": "old forest, far from any village", "hills": "broken hill country, stony"}.get(s.facts.get("wild"), "wild country")}
        terr = max((p.terrain for p in s.parcels), key=[p.terrain for p in s.parcels].count) if s.parcels else ""
        where = {"river floodplain": "on the river flats", "river terrace": "on a terrace above the river", "clay vale": "in a clay vale",
                 "lowland loam": "in rolling lowland", "sandy heath": "on the heath's edge", "chalk down": "under the downs",
                 "woodland": "in the woods", "deep forest": "deep in the forest", "hills": "in the hills", "upland pasture": "up on the tops",
                 "moor": "on the moor", "fen": "in the fens", "coast": "by the sea", "saltmarsh": "by the salt marshes"}.get(terr, "")
        node = {"name": s.name, "text": describer("node", {"kind": s.kind, "terrain": terr, "households": s.households},
                                                  " ".join(x for x in (kind_words.get(s.kind, s.kind), where) if x)), "parcels": pars}
        if s.kind == "wild":
            node["unexplored"] = True                                       # D2-187: wild nodes off the roads start unexplored (D4-47)
        nodes[s.key] = node
    # households, houses, herds, claims, lines (D2-184)
    rg = keyed.rng(seed, "lines")
    surnames = list(SURNAMES)
    rg.shuffle(surnames)
    buildings, herds, lines = {}, {}, {}
    near_seam = {}
    for rd in roads:
        a, b = rd[0], rd[1]
        for x, y in ((a, b), (b, a)):
            if any(w.key == y and w.facts.get("seam") for w in extra):
                near_seam[x] = True
    for s in settlements:
        built = next((p for p in s.parcels if p.cover == "built"), s.parcels[0])
        fields = [p for p in s.parcels if p.cover == "field"]
        pastures = sorted((p for p in s.parcels if p.cover == "pasture"), key=lambda p: -p.size)
        heavy = any(p.soil == "clay" for p in fields)
        trades = []
        if near_seam.get(s.key) or any(p.use == "mine" and p.facts.get("seam") for p in s.parcels):
            trades.append("smith")
        if any(p.cover in ("rock",) or p.terrain in ("hills", "chalk down") for p in s.parcels):
            trades.append("mason")
        if any(p.wood_kind == "managed wood" for p in s.parcels):
            trades.append("carpenter")
        if "mill site" in (s.pin.get("has") or []):
            trades.append("miller")
        hh_lines = []
        for i in range(s.households):
            line = surnames.pop(0)
            hh_lines.append(line)
            crafts = list(FARMING) + (["plough"] if heavy or i == 0 else [])
            trade = trades[i] if i < len(trades) else None
            if trade:
                crafts += TRADES[trade]
            lines[line] = {"place": s.name, "acting": [1, 4], "min_adults": 1, "crafts": crafts, "tools": {"crude tool": 1},
                           "holdings": {"coin": 2}}
            buildings[f"{line.lower()}_house"] = {"name": f"{line} House", "parcel": built.pid, "household": line, "structure": "wattle",
                                                  "size": 6, "fittings": {"beds": 6, "hearth": 1, "bins": 1},
                                                  "stock": {"grain": 30, "beans": 6, "timber": 8, "firewood": 30}}
            if trade == "smith":
                buildings[f"{line.lower()}_forge"] = {"name": f"{line}'s Forge", "parcel": built.pid, "household": line, "structure": "timber",
                                                      "size": 4, "fittings": {"hearth": 1, "anvil": 1}, "stock": {"charcoal": 4}}
            if trade == "miller":
                buildings[f"{s.key}_mill"] = {"name": f"{s.name} Mill", "parcel": built.pid, "household": line, "structure": "stone",
                                              "size": 4, "fittings": {"millstones": 1, "water wheel": 1, "bins": 1}, "stock": {}}
        if pastures:
            first = hh_lines[0]
            herds[f"{first.lower()}_cattle"] = {"name": f"the {first} cattle", "kind": "cattle", "parcel": pastures[0].pid,
                                                "cows": 2, "oxen": 2, "bulls": 1, "young": 1, "in_milk": 1, "holder": first}
            buildings[f"{first.lower()}_byre"] = {"name": f"the {first} Byre", "parcel": built.pid, "household": first, "structure": "wattle",
                                                  "size": 4, "fittings": {"bins": 1},
                                                  "stock": {"hay": 20, "straw": 10, "dung": 10, "wooden plough": 1, "harness": 2}}
            for line in hh_lines[1:]:
                herds[f"{line.lower()}_cattle"] = {"name": f"the {line} cows", "kind": "cattle", "parcel": pastures[-1].pid, "cows": 2,
                                                   "young": 1, "in_milk": 1, "holder": line}
        for i, p in enumerate(sorted(fields + [p for p in s.parcels if p.cover == "meadow"], key=lambda p: p.pid)):
            nodes[s.key]["parcels"][p.pid]["holder"] = hh_lines[i % len(hh_lines)]
        for i, p in enumerate(fields):                                      # farming under way (D2-13): the first field in crop
            if i == 0:
                nodes[s.key]["parcels"][p.pid].setdefault("state", {})["crop"] = {"kind": "barley", "left": 48 * p.size, "ripe_day": 5}
            else:
                nodes[s.key]["parcels"][p.pid].setdefault("state", {})["last_crop"] = "fallow" if i % 2 else "legumes"
        report["targets"][s.name] = {"households": s.households, "people": s.people, **{k: round(v, 2) for k, v in s.targets.items()},
                                     **s.facts}
    world = {k: v for k, v in spec.items() if k != "generate"}
    world["generated"] = {"by": "cybertron2.landgen", "seed": seed, "configuration": conf.get("configuration")}
    world["nodes"] = nodes
    world["roads"] = roads
    world["buildings"] = buildings
    world["herds"] = herds
    world.setdefault("claims", [])
    world["lines"] = lines
    n = len(lines)
    world.setdefault("bounds", {"acting": [2 * n, 5 * n], "children_max": 3 * n, "youths_min": 0, "per_min": 1, "per_spread": 5})
    world.setdefault("sim", {"start": -36, "fertility": 0.24, "leave": 0.5})   # as the generated wide world: a short past
    describer.save()
    report["descriptions"] = {"model": model, "written": describer.calls, "failed": describer.failed}
    report["checks"] = checks(L, conf, gen, settlements, extra, roads, world, settings)
    report["nodes"] = {s.key: {"name": s.name, "kind": s.kind, "site_km": [round(float(g.x[s.site]), 2), round(float(g.y[s.site]), 2)],
                               "parcels": len(s.parcels)} for s in allnodes}
    report["anchors"] = {k: [round(v[0], 2), round(v[1], 2)] for k, v in L.anchors.items()}
    failed = [k for k, v in report["checks"].items() if v["kind"] == "physics" and not v["ok"]]
    required = set(gen.get("require") or []) | {"capacity", "access gates"}
    if not provisional:                                                    # a first pass, sized for planned people, refuses only on physics
        failed += [k for k, v in report["checks"].items() if v["kind"] == "design" and not v["ok"] and k in required]
    report["refused"] = failed
    if people and not failed:
        from cybertron2.engine import generate as GEN
        built = GEN.build(_merged_for_people(world, settings), seed)
        for k in ("agents", "tree", "history", "generated"):
            if k in built:
                world[k] = built[k] if k != "generated" else {**world["generated"], "people": built[k]}
        world.pop("lines", None)
        world.pop("bounds", None)
        world.pop("sim", None)
        members = {}
        for a in world.get("agents", {}).values():
            members[a.get("household")] = members.get(a.get("household"), 0) + 1
        _seed_ways(world, settlements, seed)
        report["checks"]["capacity, people as generated"] = _capacity_as_generated(world, settings, settlements)
        for b in world["buildings"].values():                              # a house holds its household: a bed each and one spare
            n = members.get(b.get("household"), 0)                         # (D4-86), and stores for a week or so (D2-13)
            if (b.get("fittings") or {}).get("beds") and n:
                b["size"] = b["fittings"]["beds"] = max(4, n + 1)
                b["stock"] = {"grain": 8 * n, "beans": 2 * n, "timber": 8, "firewood": 6 * n}
        # the economic checks, on the world as it will run (review 02zl): a refuse-level failure refuses the world unless the file
        # allows it as a designed hardship (`allow: [carrying burden]`); the rest are warnings in the report
        from cybertron2.landgen import economy as EC
        allowed = set(gen.get("allow") or [])
        for k, v in EC.check(world).items():
            report["checks"][f"economy: {k}"] = {"kind": "economy", "level": v["level"], "ok": v["ok"], "detail": v["detail"]}
            if not v["ok"] and v["level"] == "refuse" and k not in allowed:
                report["refused"].append(f"economy: {k}")
    cells = {"x": g.x, "y": g.y, "h": L.h, "sea": L.sea, "lake": L.lake, "slope": L.slope, "temp": L.temp, "moist": L.moist,
             "acc": L.acc, "river": L.river, "spring": L.spring, "wet": L.wet, "tex": L.tex, "fert": L.fert, "f": L.f, "c": L.c,
             "terrain": L.terrain, "terrain_names": np.array(P.TERRAIN_NAMES), "cover": L.cover.astype(str),
             "place": _place_grid(g, allnodes)}
    report["_picture"] = {"cover_of": {rc: p.cover for s in allnodes for p in s.parcels for rc in p.cells},
                          "sites": [s.site for s in allnodes], "road_cells": pic["road_cells"]}
    report["_land"] = L
    return world, cells, report


def _seed_ways(world: dict, settlements: list, seed: int) -> None:
    """Each hidden way known at the start to one or two grown people of the village at its end, those whose crafts would take them
    there first (a hunter, a woodcutter), by keyed draws (D2-187)."""
    keys = {s.key for s in settlements}
    by_node = {}
    for name, a in world.get("agents", {}).items():
        if a.get("stage") in ("adult", "elder", "youth"):
            house = next((b for b in world["buildings"].values() if b.get("household") == a.get("household")), None)
            node = next((k for k, n in world["nodes"].items() if house and house["parcel"] in n["parcels"]), None)
            if node:
                by_node.setdefault(node, []).append(name)
    for rd in world["roads"]:
        for node, end in rd[3]["ends"].items():
            if not end.get("hidden") or node not in keys or not by_node.get(node):
                continue
            rg = keyed.rng(seed, "ways", rd[0], rd[1], node)
            folk = sorted(by_node[node], key=lambda n: (-int("hunt" in (world["agents"][n].get("knows") or {})), rg.random()))
            for name in folk[: rg.choice([1, 2])]:
                world["agents"][name].setdefault("ways", []).append({"road": [rd[0], rd[1]], "end": node})


def _capacity_as_generated(world: dict, settings: dict, settlements: list) -> dict:
    """The capacity check again, with the people generate.py actually made (D2-161): a warning if a village's people are far from
    its land's target."""
    from cybertron2.engine import capacity as CAP
    from cybertron2.engine.world import World
    w = World({**settings, **copy.deepcopy(world), "days": int(settings.get("days", 24))})
    out = {}
    for s in settlements:
        people = sum(1 for n in w.s["people"] if w.homes(n) and w.s["buildings"][w.homes(n)[0]]["node"] == s.key)
        cap = CAP.node(w, s.key)
        out[s.name] = {"people": people, "share": round(people / max(1e-9, min(cap["food_people"], cap["heat_people"])), 2),
                       "target": round(max(s.targets.values()), 2)}
    ok = all(v["share"] <= v["target"] + 0.2 for v in out.values())
    return {"kind": "design", "ok": ok, "detail": out}


def _merged_for_people(world: dict, settings: dict) -> dict:
    """What generate.build reads: the world's nodes and houses with the base's settings (lifespan, calendar, cast)."""
    m = copy.deepcopy(settings)
    m.update(copy.deepcopy(world))
    return m


def _place_grid(g, allnodes) -> np.ndarray:
    out = np.full(g.shape, "", dtype=object)
    for s in allnodes:
        for p in s.parcels:
            for rc in p.cells:
                out[rc] = p.pid
    return out.astype(str)


def checks(L, conf, gen, settlements, extra, roads, world, settings) -> dict:
    """The checks in two kinds (D2-180; stage 1 §7, §11i). Physics fail: the world is refused. Design: a warning unless the world
    file requires it (`require:`); access gates and capacity are required by default (the gates by the bot dry run, outside)."""
    out = {}
    # physics: every river runs downhill (each cell's receiver no higher on the filled surface), every laid river is a river
    Zf = L.h.ravel()
    riv = np.flatnonzero((L.river.ravel() >= 1))
    up = [i for i in riv if L.recv[i] >= 0 and Zf[L.recv[i]] > Zf[i] + 25.0]   # filled flats may rise a little; a climb is a fault
    out["rivers run downhill"] = {"kind": "physics", "ok": len(up) == 0, "detail": f"{len(up)} river cells drain uphill"}
    laid_ok = True
    for rv in L.rivers:
        pts = rv["through"]
        hits = sum(1 for a, b in zip(pts, pts[1:]) for t in np.linspace(0, 1, 12)
                   for r, c in [L.g.cell(a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))]
                   if (L.river[max(0, r - 6):r + 7, max(0, c - 6):c + 7] >= 1).any() or L.lake[r, c] or L.sea[r, c])
        laid_ok &= hits >= 0.7 * 12 * (len(pts) - 1)
    out["laid rivers run where laid"] = {"kind": "physics", "ok": bool(laid_ok), "detail": f"{len(L.rivers)} laid"}
    out["every pin met"] = {"kind": "physics", "ok": True, "detail": "a pin not met is refused when it is placed"}
    # design
    want = int(conf["settlements"])
    out["settlements placed"] = {"kind": "design", "ok": len(settlements) >= want,
                                 "detail": f"{len(settlements)} of {want} at {conf['spacing_km']} km apart"}
    caps = {}
    try:
        from cybertron2.engine import capacity as CAP
        from cybertron2.engine.world import World
        w = World({**settings, **{k: v for k, v in world.items() if k not in ("lines", "bounds", "sim")}, "agents": {},
                   "days": int(settings.get("days", 24))})
        for s in settlements:
            cap = CAP.node(w, s.key)
            caps[s.name] = round(s.people / max(1e-9, min(cap["food_people"], cap["heat_people"])), 2)
    except Exception as e:                                                 # noqa: BLE001 (reported, not raised)
        caps = {"error": f"{type(e).__name__}: {e}"}
    want = {s.name: max(s.targets.values()) for s in settlements}        # the scarcest flow's target (D2-161, or the pin's)
    small = {s.name for s in settlements if s.people <= 6}                 # a household alone: its least land (2 plots, a wood) rounds up
    cap_ok = "error" not in caps and all((want[k] - 0.15 <= v or k in small) and v <= want[k] + 0.05 for k, v in caps.items())   # a little
                                                                                                            # more slack below
    out["capacity"] = {"kind": "design", "ok": bool(cap_ok), "detail": caps}
    lacks = {}
    for s in settlements:
        has_stone = any(p.cover == "rock" for p in s.parcels)
        has_metal = any(p.use == "mine" and p.facts.get("seam") for p in s.parcels)
        lacks[s.name] = [x for x, ok in (("stone", has_stone), ("metal", has_metal)) if not ok]
    metal = any(w.facts.get("seam") for w in extra) or any(p.use == "mine" and p.facts.get("seam") for s in settlements for p in s.parcels)
    out["dependence"] = {"kind": "design", "ok": all(lacks.values()) and metal, "detail": lacks}
    keys = [s.key for s in settlements]
    adj = {}
    for rd in roads:
        adj.setdefault(rd[0], set()).add(rd[1])
        adj.setdefault(rd[1], set()).add(rd[0])
    seen, todo = ({keys[0]}, [keys[0]]) if keys else (set(), [])
    while todo:
        for y in adj.get(todo.pop(), ()):
            if y not in seen:
                seen.add(y)
                todo.append(y)
    out["reachable by land"] = {"kind": "design", "ok": all(k in seen for k in keys), "detail": sorted(set(keys) - seen)}
    choke = [f"{rd[0]}-{rd[1]}: {lm}" for rd in roads for st in (rd[3].get("stretches") or {}).values() for lm in st["landmarks"]
             if lm in ("ford", "pass", "narrows")]
    out["chokepoint"] = {"kind": "design", "ok": bool(choke), "detail": choke}
    days = [rd[2] for rd in roads if not any((e or {}).get("hidden") for e in rd[3]["ends"].values())]
    out["roads about a day"] = {"kind": "design", "ok": bool(days) and max(days) <= 2 and sum(d == 2 for d in days) <= len(days) / 5,
                                "detail": {d: days.count(d) for d in sorted(set(days))}}
    plo, phi = conf["parcels"]
    counts = {s.name: len(s.parcels) for s in settlements}
    out["parcels per node"] = {"kind": "design", "ok": all(plo <= n <= phi for n in counts.values()), "detail": counts}
    out["access gates"] = {"kind": "design", "ok": True, "detail": "the bot dry run checks them once the people exist (scenario_design)"}
    return out


def write(world: dict, cells: dict, report: dict, out_path: str, picture: str | None = None) -> None:
    head = (f"# Generated by cybertron2.landgen (stage 1; docs/cybertron2/proposals/generator_stage1.md), seed {report['seed']}.\n"
            f"# The cells it was drawn from: {os.path.basename(out_path).rsplit('.', 1)[0]}.cells.npz; the report: .report.json.\n")
    with open(out_path, "w") as f:
        f.write(head)
        yaml.safe_dump(world, f, sort_keys=False, allow_unicode=True, width=140)
    stem = out_path.rsplit(".", 1)[0]
    np.savez_compressed(stem + ".cells.npz", **cells)
    rep = {k: v for k, v in report.items() if not k.startswith("_")}
    with open(stem + ".report.json", "w") as f:
        json.dump(rep, f, indent=1, sort_keys=False, default=str)
    if picture:
        from cybertron2.landgen import picture as PIC
        PIC.render(report["_land"], picture, report["_picture"], scale=2)
