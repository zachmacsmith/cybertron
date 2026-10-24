"""The world: its state by place, the chokepoint every change goes through, rights read from claims, and the night
(review 38.17; spec/core/architecture.md: D4-34, D4-35).

State (World.s, plain JSON):
    day, seq
    nodes        {id: {name, text}}
    roads        {id: {a, b, days}}
    parcels      {id: {node, name, cover, size, adj, text, res: {plants|game|wood|seam|quarry: {S, K, r}}, crop?, fertility}}
    buildings    {id: {node, parcel, name, structure, size, fittings {name: n}, condition, door, fire, stock (container id),
                       unfinished?: {blueprint, units_left, materials_left, by}}}
    herds        {id: {node, parcel, home, name, kind, count, in_milk, milked: {day, n}}}
    containers   {id: {kind: hands|stock|remains, of, node?, goods {item: qty}, wear {item: uses}}}
    people       {name: {stage, sex, model, hunger, missed, frailty, attack, defence, wounded, alive, died, cause, hands, at,
                         transit, relations, notes, pinned, interests, messages, home_seen}}
    institutions {id: {kind, name, members, offices {head}, rules {admit, grant}}}
    claims       {id: {thing: [kind, id], claimant, rights, grounds, since, until, by}}
    offers       {id: {node, by, to, give, get, lots, taken, until, open}}
    agreements   {id: {parties, legs, node, day, witnesses, status}}
    know, mind   per person (knowledge.py, perceive.py)
    events       today's events, each at a place (a node or a road)
    acts         the action record: {day, actor, verb, tech, for, node}
    log          one record per night

Place: every entity has one (D4-35). `place_of(ref)` gives it; `apply` refuses (PlaceError: an engine fault, never an agent's) any
primitive whose entities are not all at the place it acts in.
"""
from __future__ import annotations

import contextlib
import copy
import os
import json
import math
import random

import yaml

from cybertron2.engine.data import EDIBLE, FITTING_ALIAS, ITEMS, PHYSICS, RESOURCES, TOOLS, WEAPONS

SEASONS = ("spring", "summer", "autumn", "winter")
STAGES = {0: "fed", -1: "hungry", -2: "starving"}
CONDITION = {2: "sound", 1: "damaged", 0: "ruined"}
ALL_RIGHTS = ("access", "withdrawal", "management", "exclusion", "alienation")
MEMBER_RIGHTS = ("access", "withdrawal")                        # holding.md: members work it; the head manages it


class Refused(Exception):
    """An act the world does not allow (the agent is told why)."""


class PlaceError(Exception):
    """A primitive touched something not at the place it acts in: an engine fault (D4-35)."""


def show(x) -> str:
    return f"{math.floor(float(x) * 10 + 1e-9) / 10:g}"


def merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


def load_spec(path) -> dict:
    """A world's spec; `base: <path>` makes it a variant: the base, with this file's keys merged over it (a comparison arm, a dry
    run). Lists replace; tables merge."""
    with open(path) as f:
        spec = yaml.safe_load(f)
    if spec.get("base"):
        base = spec.pop("base")
        if not os.path.exists(base):
            base = os.path.join(os.path.dirname(path), os.path.basename(base))
        spec = merge(load_spec(base), spec)
    return spec


class World:
    def __init__(self, spec: dict):
        self.spec = spec
        self.seed = int(spec.get("seed", 1))
        self.days = int(spec["days"])
        self.p = merge(PHYSICS, spec.get("physics") or {})
        cal = spec.get("calendar") or {}
        self.season_len = int(cal.get("season_days", 6))
        self.start = (SEASONS.index(cal.get("season", "summer")), int(cal.get("day", 1)) - 1)
        self.cold_days = {int(d) - 1 for d in spec.get("cold_days") or ()}
        self.hooks = {}                                                    # (when, primitive) -> [fn]
        self._cause = []
        s = self.s = {"day": 0, "seq": 0, "nodes": {}, "roads": {}, "parcels": {}, "buildings": {}, "herds": {}, "containers": {},
                      "people": {}, "institutions": {}, "claims": {}, "offers": {}, "agreements": {}, "know": {}, "mind": {},
                      "events": [], "acts": [], "log": [], "left": []}
        for nid, n in spec["nodes"].items():
            s["nodes"][nid] = {"name": n["name"], "text": n.get("text", ""), "unexplored": bool(n.get("unexplored"))}      # D4-47
            for pid, p in (n.get("parcels") or {}).items():
                st = copy.deepcopy(p.get("state") or {})
                from cybertron2.engine import forests as FO
                woods = FO.seed(p["cover"], int(p.get("size", 1)), st)                 # trees, young growth, dead wood (D2-156)
                if isinstance(st.get("wood"), dict) and st["wood"].get("kind"):
                    st.pop("wood")
                res = {k: {"S": float(v["S"]), "K": float(v["K"]), "r": float(v.get("r", 0.3))} if k != "seam" else
                       {"S": float(v.get("S", v.get("left", 0))), "K": float(v.get("K", v.get("S", v.get("left", 0)))), "r": 0.0}
                       for k, v in st.items() if k in RESOURCES}
                res.update(woods)
                if p["cover"] in ("pasture", "meadow") and "grass" not in res:            # grazing (D4-45; 02o: 2 head a plot)
                    cp = self.p["cattle"]
                    res["grass"] = {"S": float(cp["grass_per_plot"]) * int(p.get("size", 1)), "K": float(cp["grass_per_plot"]) * int(p.get("size", 1)),
                                    "r": float(cp["grass_r"])}
                par = {"node": nid, "name": p.get("name", pid), "cover": p["cover"], "size": int(p.get("size", 1)),
                       "adj": list(p.get("adj") or []), "text": p.get("text", ""), "res": res, "crop": None,
                       "fertility": float(p.get("fertility", 1.0)), "broken": float(st.get("broken", 0.0)),
                       "last_crop": st.get("last_crop"), "last_kind": st.get("last_kind"), "ground": p.get("ground"),
                       "works": None, "side": p.get("side", "centre"), "height": int(p.get("height", 1))}   # D2-114
                if p.get("fence"):                                                   # a fence round it (D2-130): {kind, level, gate}
                    fz = p["fence"]
                    from cybertron2.engine import farm as FM
                    need = FM.fence_need(par, fz.get("kind", "wood"))["units"]
                    par["fence"] = {"kind": fz.get("kind", "wood"), "units": need, "level": int(fz.get("level", 2)), "built": True,
                                    "gate": fz.get("gate", "shut"), "mend": float(fz.get("mended", 0.25)) * need,   # kept this season
                                    "pending": {}, "since": -1}
                if st.get("works"):                                                  # seeded field works (D2-66): {done: plots}
                    gw = st["works"]
                    tech_y = 40.0 if p.get("ground") == "wet" else 60.0
                    par["works"] = {"ground": p.get("ground"), "done": float(gw.get("done", par["size"])), "kept": 0.0, "pending": {},
                                    "units": float(gw.get("done", par["size"])) * tech_y}
                if st.get("crop"):
                    from cybertron2.engine import farm as FM
                    fam = FM.CROP_OF.get(str(st["crop"].get("kind", "grain")).lower(), "grain")
                    par["crop"] = FM.normalise_crop(par, st["crop"], 0, FM.grow_days(self.year_days(), fam))
                s["parcels"][pid] = par
        for a, b in [(a, b) for a, p in s["parcels"].items() for b in p["adj"]]:
            if a not in s["parcels"][b]["adj"]:
                s["parcels"][b]["adj"].append(a)
        for i, e in enumerate(spec.get("roads") or spec.get("edges") or []):
            a, b, k = e[0], e[1], int(e[2]) if len(e) > 2 else 1
            extra = next((x for x in e[3:] if isinstance(x, dict)), {})
            from cybertron2.engine import roads as RD
            s["roads"][f"road:{a}-{b}"] = {"a": a, "b": b, "days": k, "track": "track" in e[3:],     # a track lets carts pass
                                           "way": extra.get("way", "an unexplored way"),             # seen from the known end (D4-47)
                                           **RD.build(extra, k)}                                    # terrain, stretches (D2-104)
            from cybertron2.engine import layout as LY
            s["roads"][f"road:{a}-{b}"]["ends"] = LY.build_ends(self, extra, a, b)                   # a side and parcels (D2-90)
        for bid, b in (spec.get("buildings") or {}).items():
            self._new_building(bid, b)
        for hid, h in (spec.get("herds") or {}).items():                       # cattle by role (D2-63); a bare count is cows
            roles = {r: int(h.get(r, 0)) for r in ("cows", "oxen", "bulls", "young")}
            if not any(roles.values()):
                roles["cows"] = int(h.get("count", 6))
            if h.get("road"):                                                   # a herd lost on a road: {road: [a, b], stretch, home}
                a, b = h["road"]
                rid = f"road:{a}-{b}" if f"road:{a}-{b}" in s["roads"] else f"road:{b}-{a}"
                s["herds"][hid] = {"node": rid, "parcel": None, "home": h.get("home"), "pos": int(h.get("stretch", 1)),
                                   "lost": {"day": -1, "from": a, "road": rid}, "name": h.get("name", hid), "kind": h.get("kind", "cattle"),
                                   **roles, "count": sum(roles.values()), "in_milk": float(min(roles["cows"], int(h.get("in_milk", 0)))),
                                   "milked": {"day": -1, "n": 0}, "births": 0.0, "hungry": 0, "watched": -1}
                continue
            s["herds"][hid] = {"node": self.node_of(h["parcel"]), "parcel": h["parcel"], "home": h["parcel"], "name": h.get("name", hid),
                               "kind": h.get("kind", "cattle"), **roles, "count": sum(roles.values()),
                               "in_milk": float(min(roles["cows"], int(h.get("in_milk", 0)))), "milked": {"day": -1, "n": 0},
                               "births": 0.0, "hungry": 0, "watched": -1}
        for iid, h in (spec.get("households") or {}).items():
            s["institutions"][iid] = {"kind": "household", "name": h.get("name", f"the {iid}s"), "members": [],
                                      "offices": {"head": h.get("head")}, "rules": {"admit": "head", "grant": "members", **(h.get("rules") or {})}}
        for name, a in spec["agents"].items():
            self._person(name, a)
            hh = a.get("household")
            if hh:
                s["institutions"].setdefault(hh, {"kind": "household", "name": f"the {hh}s", "members": [], "offices": {"head": None},
                                                  "rules": {"admit": "head", "grant": "members"}})["members"].append(name)
                if a.get("role") == "head":
                    s["institutions"][hh]["offices"]["head"] = name
        for c in spec.get("claims") or []:                                     # seeded claims (D4-21, D4-23)
            self._claim(tuple(c["thing"]), c["claimant"], c.get("rights", "all"), c.get("grounds", "seeded"), since=-1)
        for kind, table in (("parcel", {p: x for n in spec.get("nodes", {}).values() for p, x in (n.get("parcels") or {}).items()}),
                            ("herd", spec.get("herds") or {})):                 # `holder:` on a parcel or herd: a seeded claim
            for key, x in table.items():
                if (x or {}).get("holder") and not self.claims_on((kind, key)):
                    self._claim((kind, key), x["holder"], "all", "seeded", since=-1)
        for bid, b in s["buildings"].items():                                  # a house claimed by its household unless given
            hh = (spec["buildings"][bid] or {}).get("household")
            if hh and not self.claims_on(("building", bid)):
                self._claim(("building", bid), hh, "all", "seeded", since=-1)
        for name, a in spec["agents"].items():                                 # everyone starts at its house's node
            home = self.homes(name)
            s["people"][name]["at"] = a.get("at") or (s["buildings"][home[0]]["node"] if home else next(iter(s["nodes"])))
        for iid, h in s["institutions"].items():                               # a head by default: the eldest adult member
            if not h["offices"].get("head") and h["members"]:
                h["offices"]["head"] = self._eldest(h["members"])
        for t in spec.get("things") or []:                                     # things lying at a spot from the start (D2-85)
            if t.get("road"):                                                  # on a stretch of road (world/roads.md)
                rid = next(r for r, x in s["roads"].items() if {x["a"], x["b"]} == set(t["road"]))
                cid = p_new_thing(self, rid, None, t.get("kind", "pile"), by=t.get("by"), hidden=t.get("hidden"),
                                  stretch=int(t.get("stretch", 1)))
            else:
                node = s["parcels"][t["parcel"]]["node"]
                cid = p_new_thing(self, node, t["parcel"], t.get("kind", "pile"), by=t.get("by"), hidden=t.get("hidden"),
                                  untaught=bool(t.get("untaught")))
            for k in ("of", "body", "died", "cause"):                         # a body lying there (seeded remains)
                if k in t:
                    self.s["containers"][cid][k] = t[k] if k != "died" else -int(t[k])
            self.s["containers"][cid]["goods"] = {k: float(v) for k, v in (t.get("goods") or {}).items()}
            self.s["containers"][cid]["day"] = -int(t.get("age", 1))
            for who in t.get("known_by") or []:
                self.s.setdefault("_seed_things", []).append((who, cid))
        for ag in spec.get("agreements") or []:                               # seeded debts (D4-21): open legs in arrears
            p_agree(self, None, {k: v for k, v in ag.items() if k != "status"})
        from cybertron2.engine import agreements as AG, knowledge as KN, perceive as PC
        AG.install(self)
        for name, a in spec["agents"].items():
            KN.seed(self, name, a)
            PC.seed(self, name, a)
        KN.seed_world(self)                                                    # dibbling known to someone (D2-129)
        PC.seed_knowledge(self)
        from cybertron2.engine import things as TH
        for who, cid in self.s.pop("_seed_things", []):                        # who knows where a seeded thing lies
            TH.remember(self, who, cid, "put")

    def _person(self, name, a):
        """A person's record and hands (D2-139: `born` a day, negative before the run; the stage follows it when given)."""
        s = self.s
        lo, hi = self.p["frailty"]
        blo, bhi = self.p["combat"]["base"]
        cid = f"hands:{name}"
        s["containers"][cid] = {"kind": "hands", "of": name, "goods": {k: float(v) for k, v in (a.get("holdings") or {}).items()}, "wear": {}}
        born = a.get("born")
        stage = a.get("stage", "adult")
        if born is not None:
            from cybertron2.engine import life as LF
            stage = LF.stage_of(-int(born), LF.lifespan(self))
        s["people"][name] = {
            "stage": stage, "sex": a.get("sex", ""), "model": a.get("model"), "role": a.get("role", ""),
            "born_line": a.get("born_line") or a.get("household"), "trade": a.get("trade", ""), "aim": a.get("aim", ""),
            "concerns": list(a.get("concerns") or []), "hands": cid, "hunger": 0, "missed": 0, "wounded": False, "alive": True,
            "died": None, "cause": None, "relations": dict(a.get("relations") or {}), "notes": {}, "pinned": None,
            "frailty": round(random.Random(f"{self.seed}|frailty|{name}").uniform(lo, hi), 4),
            "attack": round(random.Random(f"{self.seed}|attack|{name}").uniform(blo, bhi), 4),
            "defence": round(random.Random(f"{self.seed}|defence|{name}").uniform(blo, bhi), 4),
            "messages": self._message_limit(name), "at": None, "transit": None, "home_seen": None,
            "born": None if born is None else int(born), "parents": list(a.get("parents") or []), "partner": a.get("partner"),
            "pregnant": a.get("pregnant"), "gap_until": a.get("gap_until"), "order": None}

    def _new_building(self, bid, b):
        s = self.s
        cid = f"stock:{bid}"
        s["containers"][cid] = {"kind": "stock", "of": bid, "goods": {k: float(v) for k, v in (b.get("stock") or {}).items()}, "wear": {}}
        s["buildings"][bid] = {"node": self.node_of(b["parcel"]), "parcel": b["parcel"], "name": b.get("name", bid),
                               "structure": b.get("structure", "wattle"), "size": int(b.get("size", b.get("beds", 4))),
                               "fittings": {FITTING_ALIAS.get(k, k): v for k, v in (b.get("fittings") or {}).items()},
                               "condition": int(b.get("condition", 2)),
                               "door": b.get("door", "open"), "fire": False, "stock": cid, "unfinished": b.get("unfinished")}

    def _eldest(self, members):
        order = {"elder": 0, "adult": 1, "youth": 2, "child": 3, "infant": 4}
        live = [m for m in members if self.s["people"][m]["alive"] and self.s["people"][m]["stage"] in ("adult", "elder")]
        return sorted(live, key=lambda m: (order[self.s["people"][m]["stage"]], self.s["people"][m].get("born") or 0))[0] if live else None

    def _message_limit(self, name) -> int:
        m = self.p["messages"]
        w = {int(k): float(v) for k, v in m["jitter"].items()}
        extra = random.Random(f"{self.seed}|messages|{name}").choices(list(w), weights=list(w.values()))[0]
        return min(int(m["max"]), int(m["per_day"]) + extra)

    # ------------------------------------------------------------------ time and chance
    @property
    def d(self) -> int:
        return self.s["day"]

    def rng(self, *parts) -> random.Random:
        return random.Random("|".join([str(self.seed)] + [str(p) for p in parts]))

    def calendar(self, day=None) -> dict:
        day = self.d if day is None else day
        k = self.start[0] * self.season_len + self.start[1] + day
        at = k % self.season_len
        return {"season": SEASONS[(k // self.season_len) % 4], "day": at + 1, "left": self.season_len - at - 1, "year_day": k}

    def knows_place(self, name, nid) -> bool:
        """An unexplored place is known only to those who have been there or were told of it (D4-47)."""
        return not self.s["nodes"][nid].get("unexplored") or nid in self.s["mind"][name]["places"]

    def year_days(self) -> int:
        return 4 * self.season_len

    def cold(self, day=None) -> bool:
        day = self.d if day is None else day
        return day in self.cold_days or self.calendar(day)["season"] == "winter"

    # ------------------------------------------------------------------ places
    def node_of(self, pid):
        return self.s["parcels"][pid]["node"]

    def at(self, name):
        return self.s["people"][name]["at"]

    def place_of(self, ref):
        """The place of an entity: a node id, or a road id for a traveller and its hands (D4-35)."""
        kind, key = ref
        s = self.s
        if kind == "person":
            p = s["people"][key]
            return p["at"] if p["at"] is not None else (p["transit"] or {}).get("road")
        if kind == "container":
            c = s["containers"][key]
            if c["kind"] == "hands":
                return self.place_of(("person", c["of"]))
            if c["kind"] == "stock":
                return s["buildings"][c["of"]]["node"]
            return c["node"]
        if kind in ("parcel", "building", "herd", "offer"):
            return s[{"parcel": "parcels", "building": "buildings", "herd": "herds", "offer": "offers"}[kind]][key]["node"]
        raise PlaceError(f"no place for {ref}")

    def living(self) -> list:
        return sorted(n for n, a in self.s["people"].items() if a["alive"])

    def present(self, node) -> list:
        return [x for x in self.living() if self.s["people"][x]["at"] == node]

    def company(self, name) -> list:
        """Who is with someone: those at its node; on the road, its party and any party it is meeting tonight (D2-110, D2-120)."""
        if self.at(name) is not None:
            return self.present(self.at(name))
        t = self.s["people"][name]["transit"] or {}
        key = lambda n: tuple((self.s["people"][n]["transit"] or {}).get(k) for k in ("road", "from", "to", "left", "arrive"))
        out = {n for n in self.living() if self.s["people"][n]["transit"] and key(n) == key(name)}
        for m in ((self.s.get("today") or {}).get("road") or {}).get("meetings", []):
            if any(name in p for p in m["parties"]):
                out |= {n for p in m["parties"] for n in p if self.s["people"][n]["alive"]}
        return sorted(out | {name}) if t else [name]

    def agents_acting(self) -> list:
        return [n for n in self.living() if self.s["people"][n]["stage"] not in ("infant", "child") and self.s["people"][n]["at"] is not None]

    # ------------------------------------------------------------------ the chokepoint
    @contextlib.contextmanager
    def cause(self, actor=None, verb=None, for_=None, node=None):
        self._cause.append({"actor": actor, "verb": verb, "for": for_, "node": node})
        try:
            yield
        finally:
            self._cause.pop()

    def hook(self, when, prim, fn):
        self.hooks.setdefault((when, prim), []).append(fn)

    def apply(self, prim, place, **kw):
        """Every change of state (core/architecture.md): place check, before-hooks (may refuse), the change, after-hooks."""
        fn, refs = PRIMITIVES[prim]
        for ref in refs(kw):
            if ref is not None and self.place_of(ref) != place:
                raise PlaceError(f"{prim}: {ref} is at {self.place_of(ref)}, not {place}")
        call = {"prim": prim, "place": place, "kw": kw, "cause": self._cause[-1] if self._cause else None, "day": self.d}
        for h in self.hooks.get(("before", prim), []):
            h(self, call)
        out = fn(self, **kw)
        for h in self.hooks.get(("after", prim), []):
            h(self, call, out)
        return out

    def event(self, place, kind, text, actor=None, target=None, about=(), salience=0.3, tags=(), sense="sight", concerns=(), **extra):
        """Something that happened, at a place (D4-35): a node or a road. Perception reads it there."""
        if place is None or (place not in self.s["nodes"] and place not in self.s["roads"]):
            raise PlaceError(f"event {kind!r} without a place")
        self.s["seq"] += 1
        e = {"id": f"E{self.s['seq']}", "day": self.d, "place": place, "kind": kind, "actor": actor, "target": target,
             "about": list(about), "text": text, "salience": salience, "tags": list(tags), "sense": sense, "concerns": sorted(set(concerns))}
        e.update(extra)
        self.s["events"].append(e)
        return e

    def record(self, actor, verb, tech=None, for_=None, node=None, **extra):
        """The action record: what each did and for whom (D2-39 duties are checked against it)."""
        self.s["acts"].append({"day": self.d, "actor": actor, "verb": verb, "tech": tech, "for": for_, "node": node or self.at(actor), **extra})

    # ------------------------------------------------------------------ goods
    def goods(self, cid) -> dict:
        return self.s["containers"][cid]["goods"]

    def hands(self, name) -> str:
        return self.s["people"][name]["hands"]

    def food_value(self, goods) -> float:
        return sum(float(goods.get(i, 0.0)) * ITEMS[i]["food"] for i in EDIBLE)

    def capacity(self, name, track=False, oxen=None) -> float:
        """On foot, more with a pack, more again with a cart on a road with a track, a pack ox led (transport.md, D2-135, D2-136; the
        best one counts)."""
        g = self.goods(self.hands(name))
        cap = float(self.p["carry"]["foot"]) + max((ITEMS[i].get("carry", 0) for i in g if g[i] >= 1 and ITEMS[i].get("carry")
                                                    and (track or not ITEMS[i].get("track"))), default=0)
        if oxen is None:
            from cybertron2.engine import herds as HD
            oxen = HD.pack_oxen(self, name)
        if oxen:
            from cybertron2.engine.data import HERDS
            cap = max(cap, float(HERDS["pack_ox"]["carry"]) * oxen)
        return cap

    def load(self, name) -> float:
        from cybertron2.engine import life as LF                              # an infant carried weighs 2 (D2-141)
        return sum(ITEMS[i]["weight"] * q for i, q in self.goods(self.hands(name)).items() if q > 1e-9) + LF.carried_weight(self, name)

    def best_tool(self, name, table):
        """The carried tool with the best multiplier in this table (recipes.md §8), or bare hands."""
        g = self.goods(self.hands(name))
        best = (None, table.get("bare")) if "bare" in table else (None, None)
        for t in TOOLS:
            if g.get(t, 0) >= 1 and ITEMS[t]["tool"] in table and (best[1] is None or table[ITEMS[t]["tool"]] > best[1]):
                best = (t, table[ITEMS[t]["tool"]])
        return best

    def weapon(self, name):
        g = self.goods(self.hands(name))
        return max((w for w in WEAPONS if g.get(w, 0) >= 1), key=lambda w: ITEMS[w]["weapon"], default=None)

    # ------------------------------------------------------------------ institutions and claims (D4-18, D4-23, D4-36)
    def household_of(self, name):
        return next((iid for iid, h in self.s["institutions"].items() if h["kind"] == "household" and name in h["members"]), None)

    def members(self, iid) -> list:
        return [m for m in self.s["institutions"][iid]["members"] if self.s["people"].get(m, {}).get("alive")]

    def head(self, iid):
        h = self.s["institutions"][iid]["offices"].get("head")
        return h if h and self.s["people"].get(h, {}).get("alive") else None

    def claims_on(self, thing) -> list:
        thing = tuple(thing)
        return [c for c in self.s["claims"].values() if tuple(c["thing"]) == thing and (c.get("until") is None or c["until"] >= self.d)]

    def _claim(self, thing, claimant, rights, grounds, since=None, until=None, by=None):
        self.s["seq"] += 1
        cid = f"C{self.s['seq']}"
        self.s["claims"][cid] = {"thing": list(thing), "claimant": claimant, "rights": list(ALL_RIGHTS) if rights == "all" else list(rights),
                                 "grounds": grounds, "since": self.d if since is None else since, "until": until, "by": by}
        return cid

    def rights(self, name, thing) -> set:
        """What this person may do with a thing, by the claims on it (D4-23): its own, its household's (members: access and
        withdrawal; the head: all the household holds), or a grant to anyone."""
        out = set()
        hh = self.household_of(name)
        for c in self.claims_on(thing):
            if c["claimant"] in (name, "anyone"):
                out |= set(c["rights"])
            elif c["claimant"] == hh:
                out |= set(c["rights"]) if self.head(hh) == name else set(c["rights"]) & set(MEMBER_RIGHTS)
        return out

    def may_grant(self, name, thing) -> bool:
        """Exclusion is the right to let others in: the household's rule says whether any member may use it (05 §3)."""
        if "exclusion" in self.rights(name, thing):
            return True
        hh = self.household_of(name)
        rule = self.s["institutions"][hh]["rules"].get("grant") if hh else None
        return bool(hh and rule == "members" and any(c["claimant"] == hh and "exclusion" in c["rights"] for c in self.claims_on(thing)))

    def holders(self, thing) -> list:
        return [c["claimant"] for c in self.claims_on(thing) if "alienation" in c["rights"] or "exclusion" in c["rights"]]

    def homes(self, name) -> list:
        """The buildings one may use as a member of its household, or by its own claim (D4-36: home is not fixed)."""
        hh = self.household_of(name)
        held = [bid for bid, b in self.s["buildings"].items() if not b.get("unfinished")
                and any(c["claimant"] in (name, hh) and "access" in c["rights"] and c["grounds"] != "granted"
                        for c in self.claims_on(("building", bid)))]
        return sorted(held, key=lambda b: -int(self.s["buildings"][b]["fittings"].get("beds", 0)))     # dwellings first

    def dwellings(self, name) -> list:
        """Homes one can sleep in: held buildings with beds."""
        return [b for b in self.homes(name) if self.s["buildings"][b]["fittings"].get("beds")]

    def may_take(self, name, cid) -> bool:
        c = self.s["containers"][cid]
        if c["kind"] == "hands":
            return c["of"] == name
        if c["kind"] == "stock":
            return "withdrawal" in self.rights(name, ("building", c["of"]))
        return False

    def takeable(self, name, node=None) -> list:
        """Containers at this node one may take from: one's hands, then stores where one has withdrawal."""
        node = node or self.at(name)
        out = [self.hands(name)]
        for bid, b in self.s["buildings"].items():
            if b["node"] == node and self.may_take(name, b["stock"]):
                out.append(b["stock"])
        return out

    def can_enter(self, name, bid) -> bool:
        """Physics (D4-23): an open door lets anyone at the node in; a barred one only those with access."""
        b = self.s["buildings"][bid]
        return b["node"] == self.at(name) and (b["door"] != "barred" or "access" in self.rights(name, ("building", bid)))

    # ------------------------------------------------------------------ the day's budget
    def units_for(self, name) -> int:
        a = self.s["people"][name]
        base = int(self.p["units"][self.calendar()["season"]])
        if a["stage"] in ("youth", "elder"):
            base = min(base, int(self.p[f"{a['stage']}_units"]))
        if a["hunger"] == -1:
            base = max(2, base - 1)
        elif a["hunger"] == -2:
            base = min(2, base)
        if a["wounded"]:
            base = max(1, base - 2)
        from cybertron2.engine import life as LF
        return max(1, base - LF.unit_penalty(self, name))                     # late in a pregnancy, a unit fewer (D2-141)

    def yield_mult(self, name) -> float:
        return float(self.p["hunger_yield"][str(self.s["people"][name]["hunger"])])

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.s, f)


# ---------------------------------------------------------------------------------------------------------------- primitives
def _add(goods, item, q):
    goods[item] = round(goods.get(item, 0.0) + q, 6)


def p_transfer(w, src, dst, item, qty):
    g = w.goods(src)
    if g.get(item, 0.0) + 1e-9 < qty:
        raise Refused(f"there is only {show(g.get(item, 0.0))} {item} there")
    g[item] = round(g[item] - qty, 6)
    _add(w.goods(dst), item, qty)
    wear = w.s["containers"][src]["wear"]
    if item in wear and g[item] < 1 - 1e-9:                                # the worn tool goes with the last of them
        w.s["containers"][dst]["wear"][item] = wear.pop(item)
    return qty


def p_create(w, dst, item, qty, why=""):
    _add(w.goods(dst), item, qty)
    return qty


def p_destroy(w, src, item, qty, why=""):
    g = w.goods(src)
    q = min(qty, g.get(item, 0.0))
    g[item] = round(g.get(item, 0.0) - q, 6)
    return q


def p_draw(w, parcel, key, qty):
    if key == "crop":                                                          # taken from the standing crop: its ground with it
        c = w.s["parcels"][parcel]["crop"]
        q = min(qty, c["left"])
        if c["left"] > 1e-9 and "area_left" in c:
            c["area_left"] = round(c["area_left"] * (1 - q / c["left"]), 6)
        c["left"] = round(c["left"] - q, 4)
        c["reaped"] = True
        return q
    r = w.s["parcels"][parcel]["res"][key]
    q = min(qty, r["S"])
    r["S"] = round(r["S"] - q, 4)
    return q


def p_wear(w, container, item, uses):
    """Wear on a tool or weapon (D2-46): a use's wear in standard uses; at its life the tool breaks and one is gone."""
    c = w.s["containers"][container]
    c["wear"][item] = round(c["wear"].get(item, 0.0) + uses, 4)
    if c["wear"][item] >= ITEMS[item]["life"] - 1e-9:
        c["wear"][item] = 0.0
        p_destroy(w, container, item, 1, "worn out")
        return True
    return False


def p_set(w, ref, field, value):
    kind, key = ref
    table = {"building": "buildings", "parcel": "parcels", "herd": "herds", "person": "people", "offer": "offers"}[kind]
    w.s[table][key][field] = value
    return value


def p_new_herd(w, like, parcel):
    """A herd split off another (beasts driven apart: D4-44), at a parcel of the same node, with no beasts yet."""
    h = w.s["herds"][like]
    k = 2
    while f"{like}-{k}" in w.s["herds"]:
        k += 1
    hid = f"{like}-{k}"
    pname = w.s["parcels"][parcel]["name"]
    w.s["herds"][hid] = {**{x: v for x, v in h.items() if x not in ("cows", "oxen", "bulls", "young", "in_milk", "count", "births")},
                         "parcel": parcel, "home": parcel, "name": f"{h['name']} on {pname}", "cows": 0, "oxen": 0, "bulls": 0, "young": 0,
                         "in_milk": 0.0, "count": 0, "births": 0.0, "milked": {"day": -1, "n": 0}, "hungry": 0, "watched": -1}
    return hid


def p_split_herd(w, like, take):
    """A group broken off a herd (D2-128, D2-131), where the herd is (a parcel, or a stretch of road): the owner's still."""
    h = w.s["herds"][like]
    base = h.get("base_name") or h["name"]
    k = 2
    while f"{like}-{k}" in w.s["herds"]:
        k += 1
    hid = f"{like}-{k}"
    n = sum(int(v) for v in take.values())
    milk = min(float(h.get("in_milk", 0.0)), float(take.get("cows", 0)))
    w.s["herds"][hid] = {**{x: v for x, v in h.items() if x not in ("cows", "oxen", "bulls", "young", "in_milk", "count", "births")},
                         "name": f"{base}: {n} strays", "base_name": base, "split_of": like, "split_day": w.d, "cows": 0, "oxen": 0, "bulls": 0, "young": 0,
                         "in_milk": milk, "births": 0.0, "milked": {"day": -1, "n": 0}, "watched": -1, "with": None}
    for r, q in take.items():
        w.s["herds"][hid][r] = int(q)
        h[r] = int(h.get(r, 0)) - int(q)
    h["in_milk"] = round(float(h.get("in_milk", 0.0)) - milk, 4)
    h["count"] = sum(int(h.get(r, 0)) for r in ("cows", "oxen", "bulls", "young"))
    w.s["herds"][hid]["count"] = n
    return hid


def p_admit(w, person, inst):
    old = w.household_of(person)
    if old and old != inst:
        w.s["institutions"][old]["members"].remove(person)
        if w.s["institutions"][old]["offices"].get("head") == person:
            w.s["institutions"][old]["offices"]["head"] = w._eldest(w.members(old))
    if person not in w.s["institutions"][inst]["members"]:
        w.s["institutions"][inst]["members"].append(person)
    return inst


def p_leave(w, person, inst):
    h = w.s["institutions"][inst]
    if person in h["members"]:
        h["members"].remove(person)
    if h["offices"].get("head") == person:
        h["offices"]["head"] = w._eldest(w.members(inst))
    return inst


def p_found(w, person, name):
    iid = name
    n = 1
    while iid in w.s["institutions"]:
        n += 1
        iid = f"{name} {n}"
    w.s["institutions"][iid] = {"kind": "household", "name": f"the {name}s", "members": [], "offices": {"head": person},
                                "rules": {"admit": "head", "grant": "members"}}
    p_admit(w, person, iid)
    w.s["institutions"][iid]["offices"]["head"] = person
    return iid


def p_claim(w, thing, claimant, rights, grounds, until=None, by=None):
    return w._claim(tuple(thing), claimant, rights, grounds, until=until, by=by)


def p_end_claim(w, claim):
    w.s["claims"][claim]["until"] = w.d - 1
    return claim


def p_depart(w, person, road, to):
    a = w.s["people"][person]
    r = w.s["roads"][road]
    a["transit"] = {"road": road, "from": a["at"], "to": to, "left": w.d, "arrive": w.d + r["days"]}
    a["at"] = None
    return a["transit"]


def p_arrive(w, person):
    a = w.s["people"][person]
    t = a["transit"]
    a["at"], a["transit"] = t["to"], None
    return t


def p_harm(w, person, wounded=None, hunger=None):
    a = w.s["people"][person]
    if wounded is not None:
        a["wounded"] = wounded
    if hunger is not None:
        a["hunger"] = hunger
    return a


def p_die(w, person, cause, to=None):
    """Death (09 §2d, D2-87, D2-96): the body lies where one died, at a parcel of the node or on the road, with what one carried (or
    a killer takes what one carried)."""
    from cybertron2.engine import things as TH
    a = w.s["people"][person]
    place = w.place_of(("person", person))
    spot = TH.spot_of(w, person) if a["at"] is not None else None
    house = TH.house_at_death(w, person, spot)
    a["alive"], a["died"], a["cause"] = False, w.d, cause
    hands = w.goods(a["hands"])
    left = {i: q for i, q in hands.items() if q > 1e-9}
    if to:
        for i, q in left.items():
            _add(w.goods(w.hands(to)), i, q)
        left = {}
    if place is not None:                                                     # at a node, or on the road where one fell
        w.s["seq"] += 1
        cid = f"remains:{w.s['seq']}"
        w.s["containers"][cid] = {"kind": "remains", "of": person, "node": place, "parcel": spot, "goods": dict(left), "wear": {},
                                  "on_road": place not in w.s["nodes"], "body": True, "died": w.d, "in": house,
                                  "stretch": _stretch_of(w, a) if place not in w.s["nodes"] else None}
    for i in list(hands):
        hands[i] = 0.0
    from cybertron2.engine import life as LF
    LF.on_death(w, person)                                                    # the household's rules: head and heirs (D2-143)
    if a.get("partner") in w.s["people"]:
        w.s["people"][a["partner"]]["partner"] = None
    return place


def p_add_res(w, parcel, key, qty):
    """A resource stock added to (brash left as dead wood: D2-156)."""
    r = w.s["parcels"][parcel]["res"].get(key)
    if r is None:
        return 0.0
    r["S"] = round(r["S"] + float(qty), 4)
    r["K"] = max(r["K"], r["S"])
    return qty


def p_set_res(w, parcel, key, fields, init=None):
    """A resource stock's fields set by nature's night (regrowth, shedding, rot, dung): D4-7, D2-156; `init` makes it if missing."""
    res = w.s["parcels"][parcel]["res"]
    if key not in res:
        res[key] = dict(init or {"S": 0.0, "K": 0.0, "r": 0.0})
    res[key].update(fields)
    return dict(res[key])


def p_transit(w, person, fields):
    """A traveller's journey record updated (its choices, where it was last, what it noticed: world/roads.md)."""
    w.s["people"][person]["transit"].update(fields)
    return fields


def p_traces(w, add, day):
    """Traces left on a road (D2-88), and those older than they last faded."""
    from cybertron2.engine.data import ROADS
    w.s.setdefault("traces", []).extend(dict(x) for x in add)
    w.s["traces"] = [x for x in w.s["traces"] if day - x["day"] <= int(ROADS["trace_days"][x["kind"]])]
    return len(w.s["traces"])


def p_born(w, mother, father=None):
    """A child born (spec/life/birth_and_death.md, D2-141): a new person, an infant, where its mother is, in her household, named
    from its line's names (one of its forebears' not in use, else a name nobody here has), with both parents in the family tree."""
    from cybertron2.engine import generate as G, knowledge as KN, perceive as PC
    m = w.s["people"][mother]
    rng = w.rng("born", w.d, mother)
    sex = rng.choice("mf")
    hh = w.household_of(mother)
    used = set(w.s["people"])
    line = m.get("born_line") or hh
    forebears = [x["name"] for x in (w.spec.get("tree") or []) if x.get("sex") == sex and line in (x.get("line"), x.get("line_born"))]
    pool = [n for n in forebears if n not in used] or [n for n in (G.MALE if sex == "m" else G.FEMALE) if n not in used]
    name = rng.choice(sorted(pool)) if pool else f"{mother}'s child {w.d}"
    while name in used:
        name += " the younger"
    w._person(name, {"sex": sex, "household": hh, "born_line": hh, "born": w.d, "parents": [x for x in (mother, father) if x]})
    a = w.s["people"][name]
    a["at"], a["transit"] = m["at"], (dict(m["transit"]) if m.get("transit") else None)
    if hh:
        w.s["institutions"][hh]["members"].append(name)
    from cybertron2.engine.data import LIFE
    KN.seed(w, name, {"knows": {t: {"level": "known", "skill": LIFE["child_skill"]} for t in LIFE["children_work"]}})
    PC.seed(w, name, {})
    w.s["mind"][name]["places"] = copy.deepcopy(w.s["mind"][mother]["places"])   # it grows up knowing the places its mother knows
    sib = [x for x, y in w.s["people"].items() if x != name and y["alive"] and set(y.get("parents") or []) & {mother}]
    kin = {mother: ("your mother", "your son" if sex == "m" else "your daughter")}
    if father in w.s["people"]:
        kin[father] = ("your father", "your son" if sex == "m" else "your daughter")
    for x in sib:
        kin[x] = ("your brother" if w.s["people"][x]["sex"] == "m" else "your sister", "your brother" if sex == "m" else "your sister")
    for x in (w.members(hh) if hh else []):
        if x != name and x not in kin:
            kin[x] = ("of your household", f"{mother}'s child, of your household")
    for x, (theirs, mine) in kin.items():
        a["relations"][x] = theirs
        w.s["people"][x]["relations"][name] = mine
        homes = w.homes(x)
        lives = f"{w.s['buildings'][homes[0]]['name']}, {w.s['nodes'][w.s['buildings'][homes[0]]['node']]['name']}" if homes else "no house"
        w.s["mind"][name]["kin"][x] = {"rel": theirs, "lives": lives, "household": w.household_of(x), "alive": True, "seen": w.d}
        w.s["mind"][x]["kin"][name] = {"rel": mine, "lives": lives, "household": hh, "alive": True, "seen": w.d}
    return name


def p_partner(w, person, other, on=True):
    """A partnership made (both chose it) or ended (D2-140); it is in the family tree."""
    a, b = w.s["people"][person], w.s["people"][other]
    if on:
        for x in (a, b):
            if x.get("partner") in w.s["people"]:
                w.s["people"][x["partner"]]["partner"] = None
        a["partner"], b["partner"] = other, person
    else:
        a["partner"] = b["partner"] = None
    return on


def p_office(w, inst, field, value, by=None):
    """A household's heir, its standing order for its children, or a member's naming of the next head (D2-143, D2-148)."""
    h = w.s["institutions"][inst]
    if field == "named":
        h["succession"].setdefault("named", {})[by] = value
    elif field == "head":                                                      # the head the members named (D2-143)
        h["offices"]["head"] = value
    elif field == "succession" and value is None:                              # the naming over
        h.pop("succession", None)
    else:
        h[field] = value
    return value


def _stretch_of(w, a):
    from cybertron2.engine import roads as RD
    return RD.position(w, a["transit"]) if a.get("transit") else None


def p_new_thing(w, node, parcel, kind, **fields):
    """A thing at a spot (world/things_in_places.md): an empty container at a parcel (or, on the road, a stretch), filled by transfer."""
    w.s["seq"] += 1
    cid = f"{kind}:{w.s['seq']}"
    w.s["containers"][cid] = {"kind": kind, "node": node, "parcel": parcel, "goods": {}, "wear": {}, "day": w.d, **fields}
    return cid


def p_set_thing(w, cid, field, value):
    w.s["containers"][cid][field] = value
    return value


def p_learn(w, person, tech, level, source):
    from cybertron2.engine import knowledge as KN
    return KN._set(w, person, tech, level, source)


def p_raise(w, node, parcel, rec):
    """A new building on a lot (D2-9): unfinished until its work is done."""
    w.s["seq"] += 1
    bid = f"b{w.s['seq']}"
    w._new_building(bid, {"parcel": parcel, **rec})
    return bid


def p_offer(w, by, rec):
    w.s["seq"] += 1
    oid = f"O{w.s['seq']}"
    w.s["offers"][oid] = {"node": w.place_of(("person", by)), "by": by, **rec}
    return oid


def p_close_offer(w, offer, why=""):
    w.s["offers"][offer]["open"] = False
    w.s["offers"][offer]["closed"] = why
    return offer


def p_agree(w, node, rec):
    w.s["seq"] += 1
    aid = f"A{w.s['seq']}"
    w.s["agreements"][aid] = {"node": node, "day": w.d, "status": "open", **rec}
    return aid


def p_close_agreement(w, agreement, status):
    w.s["agreements"][agreement]["status"] = status
    return status


def p_leg(w, agreement, leg, **fields):
    w.s["agreements"][agreement]["legs"][leg].update(fields)
    return fields


def _r(kind, *keys):
    return lambda kw: [(kind, kw[k]) for k in keys if kw.get(k) is not None]


def _rc(*keys):
    return lambda kw: [("container", kw[k]) for k in keys]


PRIMITIVES = {
    "transfer": (p_transfer, _rc("src", "dst")),
    "create": (p_create, _rc("dst")),
    "destroy": (p_destroy, _rc("src")),
    "draw": (p_draw, _r("parcel", "parcel")),
    "add_res": (p_add_res, _r("parcel", "parcel")),
    "wear": (p_wear, _rc("container")),
    "set": (p_set, lambda kw: [tuple(kw["ref"])]),
    "new_herd": (p_new_herd, lambda kw: [("herd", kw["like"]), ("parcel", kw["parcel"])]),
    "split_herd": (p_split_herd, lambda kw: [("herd", kw["like"])]),
    "admit": (p_admit, _r("person", "person")),
    "leave": (p_leave, _r("person", "person")),
    "found": (p_found, _r("person", "person")),
    "claim": (p_claim, lambda kw: [tuple(kw["thing"])] if kw["thing"][0] in ("parcel", "building", "herd") else []),
    "end_claim": (p_end_claim, lambda kw: []),
    "depart": (p_depart, _r("person", "person")),
    "arrive": (p_arrive, lambda kw: []),                                   # checked by arrival: the person is on the road
    "harm": (p_harm, _r("person", "person")),
    "die": (p_die, _r("person", "person")),
    "born": (p_born, _r("person", "mother")),
    "partner": (p_partner, lambda kw: [("person", kw["person"]), ("person", kw["other"])]),
    "office": (p_office, _r("person", "by")),
    "learn": (p_learn, _r("person", "person")),
    "new_thing": (p_new_thing, _r("parcel", "parcel")),
    "set_thing": (p_set_thing, _rc("cid")),
    "raise": (p_raise, _r("parcel", "parcel")),
    "offer": (p_offer, _r("person", "by")),
    "close_offer": (p_close_offer, _r("offer", "offer")),
    "agree": (p_agree, lambda kw: []),                                     # made at a node by parties present (checked by the verb)
    "leg": (p_leg, lambda kw: []),
    "close_agreement": (p_close_agreement, lambda kw: []),
    "set_res": (p_set_res, _r("parcel", "parcel")),
    "transit": (p_transit, _r("person", "person")),
    "traces": (p_traces, lambda kw: []),                                   # at the road the party is on (checked by the caller)
}
