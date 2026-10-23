"""The world of one node: its parcels, houses, people, the calendar, today's happenings, and the night.

State (World.s, plain JSON):
    day         0-based day of the run
    node        {name, text, parcels: {id: {name, cover, size, side, adj, state}}, features: {id: {name, parcels, text}}}
    fittings    [{kind, parcel, owner, name}] built things that are not houses (a firing pit)
    houses      {id: {name, parcel, household, beds, condition 2|1|0, stock {item: qty}, door "open"|"barred", fire}}
    herds       {id: {name, parcel, count, home}}
    agents      {name: {household, house, model, stage, trade, aim, concerns, holdings, hunger, missed, frailty, attack, defence,
                        alive, died, cause, relations, notes {title: text}, pinned, wounded}}
    know        {name: {tech: {level, skill, seen, tries, wins, source, since}}}   (knowledge.py)
    mind        {name: perception store}                                          (perceive.py)
    offers      {id: {by, to, give, get, day, open}}
    events      today's happenings: [{id, kind, actor, target, parcel, text, salience, tags, sense, concerns}]
    log         one record per night

Random draws: World.rng(*parts) is random.Random("seed|part|..."): a draw depends on the seed and its stream, never on call order.
"""
from __future__ import annotations

import copy
import json
import math
import random

import yaml

from cybertron2.m1.data import COVERS, EDIBLE, ITEMS, PHYSICS, TECHNIQUES

SEASONS = ("spring", "summer", "autumn", "winter")
STAGES = {0: "fed", -1: "hungry", -2: "starving"}
CONDITION = {2: "sound", 1: "damaged", 0: "ruined"}


def show(x) -> str:
    """A quantity as an agent sees it: rounded down to one decimal."""
    return f"{math.floor(float(x) * 10 + 1e-9) / 10:g}"


def merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


def load_spec(path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


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
        n = spec["node"]
        s = {"day": 0, "node": {"name": n["name"], "text": n.get("text", ""), "parcels": {}, "features": {}},
             "fittings": [], "houses": {}, "herds": {}, "agents": {}, "know": {}, "mind": {}, "offers": {}, "events": [], "log": [],
             "seq": 0}
        for pid, p in n["parcels"].items():
            st = copy.deepcopy(p.get("state") or {})
            s["node"]["parcels"][pid] = {"name": p.get("name", pid), "cover": p["cover"], "size": p.get("size", 1),
                                         "side": p.get("side", ""), "adj": list(p.get("adj") or []), "text": p.get("text", ""),
                                         "state": st}
        for a, b in [(a, b) for a, p in s["node"]["parcels"].items() for b in p["adj"]]:
            if a not in s["node"]["parcels"][b]["adj"]:
                s["node"]["parcels"][b]["adj"].append(a)
        for fid, f in (n.get("features") or {}).items():
            s["node"]["features"][fid] = {"name": f.get("name", fid), "parcels": list(f.get("parcels") or []), "text": f.get("text", "")}
        for f in spec.get("fittings") or []:
            s["fittings"].append(dict(f))
        for hid, h in spec["houses"].items():
            s["houses"][hid] = {"name": h.get("name", hid), "parcel": h["parcel"], "household": h["household"], "beds": int(h.get("beds", 5)),
                                "condition": int(h.get("condition", 2)), "stock": {k: float(v) for k, v in (h.get("stock") or {}).items()},
                                "door": h.get("door", "open"), "fire": False, "access": h.get("access", "household")}
        s["buildings"] = {bid: {"name": b.get("name", bid), "parcel": b["parcel"], "access": b.get("access", "public")}
                          for bid, b in (spec.get("buildings") or {}).items()}   # other buildings (a hall); houses are buildings too
        for hid, h in (spec.get("herds") or {}).items():
            s["herds"][hid] = {"name": h.get("name", hid), "parcel": h["parcel"], "count": int(h.get("count", 6)), "home": h["parcel"],
                               "in_milk": int(h.get("in_milk", 0))}
        house_of = {h["household"]: hid for hid, h in s["houses"].items()}
        lo, hi = self.p["frailty"]
        blo, bhi = self.p["combat"]["base"]
        for name, a in spec["agents"].items():
            s["agents"][name] = {
                "household": a["household"], "house": house_of.get(a["household"]), "model": a.get("model"),
                "stage": a.get("stage", "adult"), "sex": a.get("sex", ""), "trade": a.get("trade", ""), "role": a.get("role", ""),
                "aim": a.get("aim", ""), "concerns": list(a.get("concerns") or []),
                "holdings": {k: float(v) for k, v in (a.get("holdings") or {}).items()},
                "hunger": 0, "missed": 0, "wounded": False, "alive": True, "died": None, "cause": None,
                "frailty": round(random.Random(f"{self.seed}|frailty|{name}").uniform(lo, hi), 4),
                "attack": round(random.Random(f"{self.seed}|attack|{name}").uniform(blo, bhi), 4),
                "defence": round(random.Random(f"{self.seed}|defence|{name}").uniform(blo, bhi), 4),
                "relations": dict(a.get("relations") or {}), "notes": {}, "pinned": None,
                "messages": self._message_limit(name)}
        self.s = s
        from cybertron2.m1 import knowledge as KN, perceive as PC
        for name, a in spec["agents"].items():
            KN.seed(self, name, a)
            PC.seed(self, name, a)

    def _message_limit(self, name) -> int:
        """Private messages a day: the base plus a personal jitter drawn once, capped (cybertron 1's dms_per_round, D4-31)."""
        m = self.p["messages"]
        w = {int(k): float(v) for k, v in m["jitter"].items()}
        extra = random.Random(f"{self.seed}|messages|{name}").choices(list(w), weights=list(w.values()))[0]
        return min(int(m["max"]), int(m["per_day"]) + extra)

    # ------------------------------------------------------------------ reads
    @property
    def d(self) -> int:
        return self.s["day"]

    def rng(self, *parts) -> random.Random:
        return random.Random("|".join([str(self.seed)] + [str(p) for p in parts]))

    def calendar(self, day=None) -> dict:
        day = self.d if day is None else day
        k = self.start[0] * self.season_len + self.start[1] + day
        season = SEASONS[(k // self.season_len) % 4]
        at = k % self.season_len
        return {"season": season, "day": at + 1, "left": self.season_len - at - 1, "year_day": k}

    def cold(self, day=None) -> bool:
        day = self.d if day is None else day
        return day in self.cold_days or self.calendar(day)["season"] == "winter"

    def living(self) -> list:
        return sorted(n for n, a in self.s["agents"].items() if a["alive"])

    def agents_acting(self) -> list:
        return [n for n in self.living() if self.s["agents"][n]["stage"] != "child"]

    def parcels(self) -> dict:
        return self.s["node"]["parcels"]

    def parcel_by_name(self, x):
        x = str(x or "").strip().lower()
        for pid, p in self.parcels().items():
            if x in (pid.lower(), p["name"].lower(), p["name"].lower().removeprefix("the ")):
                return pid
        return None

    def buildings(self) -> dict:
        """Every building: houses and the rest, {id: record}."""
        return {**self.s["houses"], **self.s.get("buildings", {})}

    def building_by_name(self, x):
        x = str(x or "").strip().lower().removeprefix("the ")
        for bid, b in self.buildings().items():
            if x in (bid.lower(), b["name"].lower(), b["name"].lower().removeprefix("the ")):
                return bid
        return None

    def has_access(self, name, bid) -> bool:
        """Access is data on each building (D2-7, D4-30): "household" (its household), "public" (everyone at the node), or a list
        of names; a house's household always has it."""
        b = self.buildings()[bid]
        acc = b.get("access", "household")
        if bid in self.s["houses"] and self.s["agents"][name]["house"] == bid:
            return True
        if acc == "public":
            return True
        return isinstance(acc, list) and name in acc

    def house_by_name(self, x):
        x = str(x or "").strip().lower()
        for hid, h in self.s["houses"].items():
            if x in (hid.lower(), h["name"].lower()):
                return hid
        return None

    def person(self, x):
        x = str(x or "").strip().lower()
        for n in self.s["agents"]:
            if n.lower() == x:
                return n
        return None

    def home(self, name):
        hid = self.s["agents"][name]["house"]
        return self.s["houses"].get(hid) if hid else None

    def fittings_at(self, kind) -> list:
        return [f for f in self.s["fittings"] if f["kind"] == kind]

    def units_for(self, name) -> int:
        a = self.s["agents"][name]
        base = int(self.p["units"][self.calendar()["season"]])
        if a["stage"] in ("youth", "elder"):
            base = min(base, int(self.p[f"{a['stage']}_units"]))
        if a["hunger"] == -1:
            base = max(2, base - 1)
        elif a["hunger"] == -2:
            base = min(2, base)
        if a["wounded"]:
            base = max(1, base - 2)
        return base

    def food_value(self, holdings) -> float:
        return sum(float(holdings.get(i, 0.0)) * ITEMS[i]["food"] for i in EDIBLE)

    def yield_mult(self, name) -> float:
        return float(self.p["hunger_yield"][str(self.s["agents"][name]["hunger"])])

    # ------------------------------------------------------------------ happenings
    def happen(self, kind, text, actor=None, target=None, parcel=None, salience=0.3, tags=(), sense="sight", concerns=(), extra=None):
        """Something that happened today, for perception: who did it, to whom, where, how much it stands out, what it bears on."""
        self.s["seq"] += 1
        e = {"id": f"E{self.s['seq']}", "day": self.d, "kind": kind, "actor": actor, "target": target, "parcel": parcel, "text": text,
             "salience": salience, "tags": list(tags), "sense": sense, "concerns": sorted(set(concerns))}
        if extra:
            e.update(extra)
        self.s["events"].append(e)
        return e

    # ------------------------------------------------------------------ the night
    def night(self) -> dict:
        s, p = self.s, self.p
        rec = {"day": self.d, "cold": self.cold(), "ate": {}, "short": [], "missed": [], "deaths": [], "cold_falls": [], "breaks": [],
               "hearth": {}, "spoiled": {}, "fights": []}
        from cybertron2.m1 import act as AC
        rec["fights"] = AC.settle_fights(self)
        rec["deaths"] += [f["killed"] for f in rec["fights"] if f.get("killed")]
        self._regrow()
        fuel = float(p["fuel"]["cold" if self.cold() else "normal"])
        for hid, h in s["houses"].items():
            sleepers = [n for n in self.living() if s["agents"][n]["house"] == hid]
            need = fuel if sleepers else 0.0
            ok = h["stock"].get("timber", 0.0) + 1e-9 >= need
            if ok and need:
                h["stock"]["timber"] = round(h["stock"]["timber"] - need, 6)
            h["fire"] = bool(ok and need)
            rec["hearth"][hid] = {"sleepers": len(sleepers), "lit": h["fire"]}
        for name in self.living():
            a = s["agents"][name]
            h = self.home(name)
            state = "unsheltered" if h is None or h["condition"] == 0 else ("damaged" if h["condition"] == 1 else "housed")
            if self.cold() and state == "housed" and h is not None and not h["fire"]:
                state = "no_fuel"
            need = float(p["ration"]) * float((p["shelter_cold"] if self.cold() else p["shelter"]).get(state, 1.0))
            ate = self._eat(name, need, h)
            if ate + 1e-9 >= need:
                a["hunger"], a["missed"] = min(0, a["hunger"] + 1), 0
                rec["ate"][name] = round(ate, 2)
            elif ate + 1e-9 >= float(p["ration"]):
                a["missed"] = 0
                rec["short"].append(name)
                rec["ate"][name] = round(ate, 2)
            else:
                a["hunger"], a["missed"] = max(-2, a["hunger"] - 1), a["missed"] + 1
                rec["missed"].append(name)
                if ate:
                    rec["ate"][name] = round(ate, 2)
            if self.cold() and state == "unsheltered" and self.rng("cold", self.d, name).random() < float(p["cold_starving"]):
                a["hunger"] = -2
                rec["cold_falls"].append(name)
        if self.d < self.days - 1:
            for name in self.living():
                a = s["agents"][name]
                if a["missed"] >= 3:
                    k = a["missed"] - 2
                    hz = min(1.0, a["frailty"] + float(p["hazard"]["step"]) * (k - 1))
                    if self.rng("hazard", self.d, name).random() < hz or k >= int(p["hazard"]["max_rounds"]):
                        self.die(name, "starvation")
                        rec["deaths"].append(name)
        for name in self.living():
            self._spoil(s["agents"][name]["holdings"], 1.0, rec)
        for h in s["houses"].values():
            self._spoil(h["stock"], float(p["house_spoil"]), rec)
        for hid, h in s["houses"].items():
            q = float(p["breaks"]["cold" if self.cold() else "p"])
            if h["condition"] > 0 and self.rng("break", self.d, hid).random() < q:
                h["condition"] -= 1
                rec["breaks"].append(hid)
        for o in s["offers"].values():
            if o["open"] and o.get("until", o["day"]) <= self.d:
                o["open"] = False                                            # offers last until nightfall; set-aside goods go back
                if o.get("held") and s["agents"][o["by"]]["alive"]:
                    for item, q in o["give"].items():
                        s["agents"][o["by"]]["holdings"][item] = round(s["agents"][o["by"]]["holdings"].get(item, 0.0) + q, 6)
        s["log"].append(rec)
        return rec

    def _eat(self, name, need, h) -> float:
        """Eat up to `need` in food value: from hands first, then the house stock, most perishable first."""
        a = self.s["agents"][name]
        got = 0.0
        for store in (a["holdings"], h["stock"] if h is not None else {}):
            for item in sorted(EDIBLE, key=lambda i: -ITEMS[i]["spoil"]):
                v = ITEMS[item]["food"]
                while got + 1e-9 < need and store.get(item, 0.0) > 1e-9:
                    q = min(store[item], (need - got) / v)
                    store[item] = round(store[item] - q, 6)
                    got += q * v
        return round(got, 6)

    def _spoil(self, store, mult, rec):
        for item, q in list(store.items()):
            r = ITEMS.get(item, {}).get("spoil", 0.0) * mult
            if q > 1e-9 and r > 0:
                lost = round(q * r, 6)
                store[item] = round(q - lost, 6)
                rec["spoiled"][item] = round(rec["spoiled"].get(item, 0.0) + lost, 4)

    def _regrow(self):
        winter = self.calendar()["season"] == "winter"
        for p in self.parcels().values():
            st = p["state"]
            for key in ("plants", "game", "fish"):
                if key in st:
                    x = st[key]
                    r = float(x.get("r", 0.3)) * (0.25 if winter else 1.0)
                    x["S"] = round(min(x["K"], x["S"] + r * x["S"] * (1 - x["S"] / x["K"]) + 0.01 * (x["K"] - x["S"])), 4)

    def die(self, name, cause, to=None):
        a = self.s["agents"][name]
        a["alive"], a["died"], a["cause"] = False, self.d, cause
        h = self.home(name)
        for item, q in list(a["holdings"].items()):
            if q <= 0:
                continue
            if to:
                for b, share in to.items():
                    hb = self.s["agents"][b]["holdings"]
                    hb[item] = round(hb.get(item, 0.0) + q * share, 6)
            elif h is not None:
                h["stock"][item] = round(h["stock"].get(item, 0.0) + q, 6)
            a["holdings"][item] = 0.0

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.s, f)
