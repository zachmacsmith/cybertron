"""The world: places, people, houses, and what happens at the end of every round.

State (World.s, plain JSON so a round can be saved and read back):
    round       0-based round number
    nodes       {id: {name, text, plants: {S, K, K0, r, yield, refuge} | None, game: {G, K, r} | None, timber: bool}}
    edges       {id: [neighbour ids]}
    agents      {name: {household, house, model, role, age, aim, at, holdings: {food, timber}, stage, missed, frailty,
                        alive, died, cause, notes}}
    houses      {id: {name, node, household, beds, condition (2 sound, 1 damaged, 0 ruined), stock: {food, timber}, work}}
    hunts       this round's hunting effort: {node: {party: {agent: units}}}
    gathered    this round's gathering actions per agent (forage, hunt and fell count toward physics.gather_per_round)
    log         per-round records (what the report reads)

Random streams are seeded strings, as in the old engine: random.Random(f"{seed}|<stream>|<round>|<who>"), so a draw depends only
on the seed and the round, never on call order.

The end of the round (end_of_round), in order:
    1. hunts      each party's effort at its node draws catches (the old engine's individual mode: every effort unit draws, a
                  bigger party raises the chance of bigger game, crowding thins it, the game stock caps it)
    2. regrowth   plants and game regrow logistically; in a cold round plants x cold.plants, game x cold.game
    3. hearth     each house with an occupant sleeping there burns fuel (timber) from its stock: physics.fuel normal or cold
    4. ration     each living agent needs ration x its shelter multiplier (02e §3.2); it eats from its hands, then (when it
                  sleeps at its own house) from the house stock; short of the full need it eats nothing (the old engine's rule)
                  and misses a meal: stage down one; a full meal: stage up one
    5. hazard     from 3 missed meals in a row: death with chance frailty + 0.15 per further miss, certain at 4 more
    6. the cold   an unsheltered agent in a cold round falls straight to starving with chance cold.starving (after the ration,
                  so it bites next round; it counts no missed meal: 02e §3.3)
    7. spoilage   food in hands loses spoil.hands, in a house spoil.house
    8. breaks     each house drops a level with chance breaks.p (breaks.cold in a cold round)
"""
from __future__ import annotations

import copy
import json
import math
import random

import yaml

STAGES = {0: "fed", -1: "hungry", -2: "starving"}
CONDITION = {2: "sound", 1: "damaged", 0: "ruined"}
ITEMS = ("food", "timber")

PHYSICS = {
    "actions": 4,                                   # actions a turn when fed; hungry one fewer, starving at most 2
    "gather_per_round": 2,                          # forage, hunt and fell actions an agent may take a round
    "ration": 1.0,
    "shelter": {"housed": 1.0, "damaged": 1.2, "unsheltered": 1.5},            # ration multiplier, normal round
    "shelter_cold": {"housed": 1.0, "no_fuel": 1.3, "damaged": 1.5, "unsheltered": 2.0},
    "cold": {"plants": 0.25, "game": 0.5, "starving": 0.3},
    "fuel": {"normal": 0.5, "cold": 2.0},           # timber a house burns a round when someone sleeps there
    "spoil": {"hands": 0.15, "house": 0.05},
    "breaks": {"p": 0.02, "cold": 0.08},
    "repair": {"timber": 5.0, "work": 3},           # one level: timber in the house stock and work actions there
    "fell": {"timber": 3.0, "k_loss": 0.01, "floor": 0.5},   # timber a fell; plant capacity lost a fell (x K0), down to floor x K0
    "hunger_yield": {0: 1.0, -1: 0.75, -2: 0.5},
    "frailty": [0.25, 0.55],
    "hazard": {"step": 0.15, "max_rounds": 4},
    "hunt": {"large": {"p": 0.07, "food": 20.0, "scale": 5.0, "shape": 3.0},
             "medium": {"p": 0.32, "food": 5.0, "scale": 2.5, "shape": 2.0},
             "small": {"p": 0.95, "food": 1.0}, "crowd": 12.0},
}


def show(x) -> str:
    """A quantity as an agent sees it: rounded down to one decimal, so any amount it reads is there to use."""
    return f"{math.floor(float(x) * 10 + 1e-9) / 10:g}"


def merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


class World:
    def __init__(self, spec: dict):
        self.spec = spec
        self.seed = int(spec.get("seed", 1))
        self.rounds = int(spec["rounds"])
        self.p = merge(PHYSICS, spec.get("physics") or {})
        self.cold_rounds = {int(r) - 1 for r in spec.get("cold_rounds") or ()}   # spec 1-based, state 0-based
        s = {"round": 0, "nodes": {}, "edges": {}, "agents": {}, "houses": {}, "hunts": {}, "gathered": {}, "log": []}
        for nid, n in spec["nodes"].items():
            node = {"name": n.get("name", nid), "text": n.get("text", ""), "plants": None, "game": None,
                    "timber": bool(n.get("timber", False))}
            if n.get("plants"):
                pl = n["plants"]
                node["plants"] = {"K": float(pl["K"]), "K0": float(pl["K"]), "S": float(pl["K"]) * float(pl.get("start", 0.8)),
                                  "r": float(pl["r"]), "yield": float(pl.get("yield", 2.0)), "refuge": float(pl.get("refuge", 0.1))}
            if n.get("game"):
                g = n["game"]
                node["game"] = {"K": float(g["K"]), "G": float(g["K"]) * float(g.get("start", 0.8)), "r": float(g["r"])}
            s["nodes"][nid] = node
            s["edges"][nid] = []
        for a, b in spec["edges"]:
            s["edges"][a].append(b)
            s["edges"][b].append(a)
        for hid, h in spec["houses"].items():
            s["houses"][hid] = {"name": h.get("name", hid), "node": h["node"], "household": h["household"],
                                "beds": int(h.get("beds", 5)), "condition": int(h.get("condition", 2)),
                                "stock": {i: float((h.get("stock") or {}).get(i, 0.0)) for i in ITEMS}, "work": 0}
        house_of = {h["household"]: hid for hid, h in s["houses"].items()}
        lo, hi = self.p["frailty"]
        for name, a in spec["agents"].items():
            hh = a["household"]
            s["agents"][name] = {
                "household": hh, "house": house_of.get(hh), "model": a.get("model"), "role": a.get("role", ""),
                "age": a.get("age"), "aim": a.get("aim", ""), "at": a.get("at") or s["houses"][house_of[hh]]["node"],
                "holdings": {i: float((a.get("holdings") or {}).get(i, 0.0)) for i in ITEMS},
                "stage": 0, "missed": 0, "frailty": round(random.Random(f"{self.seed}|frailty|{name}").uniform(lo, hi), 4),
                "alive": True, "died": None, "cause": None, "notes": ""}
        self.s = s

    # ------------------------------------------------------------------ reads
    @property
    def r(self) -> int:
        return self.s["round"]

    def cold(self, rnd=None) -> bool:
        return (self.r if rnd is None else rnd) in self.cold_rounds

    def living(self) -> list:
        return sorted(n for n, a in self.s["agents"].items() if a["alive"])

    def at(self, node) -> list:
        return [n for n in self.living() if self.s["agents"][n]["at"] == node]

    def actions_for(self, name) -> int:
        st = self.s["agents"][name]["stage"]
        n = int(self.p["actions"])
        return n if st == 0 else (max(2, n - 1) if st == -1 else min(2, n))

    def home(self, name) -> dict | None:
        hid = self.s["agents"][name]["house"]
        return self.s["houses"].get(hid) if hid else None

    def sleeps_home(self, name) -> bool:
        a, h = self.s["agents"][name], self.home(name)
        return h is not None and a["at"] == h["node"]

    def shelter(self, name, fuel_ok: bool = True) -> str:
        """housed | no_fuel | damaged | unsheltered (02e §3.2): where the agent ends the round decides."""
        h = self.home(name)
        if h is None or not self.sleeps_home(name) or h["condition"] == 0:
            return "unsheltered"
        sleepers = [n for n in self.living() if self.s["agents"][n]["house"] == self.s["agents"][name]["house"] and self.sleeps_home(n)]
        if h["condition"] == 1 or len(sleepers) > h["beds"]:
            return "damaged"
        if self.cold() and not fuel_ok:
            return "no_fuel"
        return "housed"

    def shelter_mult(self, state: str) -> float:
        if self.cold():
            return float(self.p["shelter_cold"][state])
        return float(self.p["shelter"]["housed" if state == "no_fuel" else state])

    def plants_word(self, node) -> str:
        pl = self.s["nodes"][node]["plants"]
        if not pl:
            return ""
        f = pl["S"] / pl["K"] if pl["K"] else 0.0
        return "plentiful" if f > 0.7 else "fair" if f > 0.45 else "thin" if f > 0.25 else "nearly stripped"

    def game_word(self, node) -> str:
        g = self.s["nodes"][node]["game"]
        if not g:
            return ""
        f = g["G"] / g["K"] if g["K"] else 0.0
        return "plentiful" if f > 0.6 else "fair" if f > 0.3 else "scarce" if f > 0.1 else "very scarce"

    def rng(self, *parts) -> random.Random:
        return random.Random("|".join([str(self.seed)] + [str(p) for p in parts]))

    # ------------------------------------------------------------------ the end of the round
    def end_of_round(self) -> dict:
        s, p, rnd = self.s, self.p, self.r
        rec = {"round": rnd, "cold": self.cold(), "hunts": [], "ate": {}, "missed": [], "deaths": [], "cold_falls": [],
               "breaks": [], "shelter": {}, "hearth": {}, "spoiled": 0.0}
        self._hunts(rec)
        for nid, n in s["nodes"].items():                                   # 2. regrowth
            if n["plants"]:
                pl = n["plants"]
                r = pl["r"] * (p["cold"]["plants"] if self.cold() else 1.0)
                pl["S"] = round(min(pl["K"], pl["S"] + r * pl["S"] * (1 - pl["S"] / pl["K"])), 6)
            if n["game"]:
                g = n["game"]
                r = g["r"] * (p["cold"]["game"] if self.cold() else 1.0)
                g["G"] = round(min(g["K"], g["G"] + r * g["G"] * (1 - g["G"] / g["K"])), 6)
        fuel_ok = {}
        for hid, h in s["houses"].items():                                  # 3. hearth
            sleepers = [n for n in self.living() if s["agents"][n]["house"] == hid and self.sleeps_home(n)]
            need = float(p["fuel"]["cold" if self.cold() else "normal"]) if sleepers else 0.0
            ok = h["stock"]["timber"] + 1e-9 >= need
            if ok:
                h["stock"]["timber"] = round(h["stock"]["timber"] - need, 6)
            fuel_ok[hid] = ok
            rec["hearth"][hid] = {"sleepers": len(sleepers), "burnt": need if ok else 0.0, "lit": ok}
        for name in self.living():                                          # 4. ration
            a = s["agents"][name]
            state = self.shelter(name, fuel_ok.get(a["house"], True))
            rec["shelter"][name] = state
            need = round(float(p["ration"]) * self.shelter_mult(state), 6)
            h = self.home(name) if self.sleeps_home(name) else None
            have = a["holdings"]["food"] + (h["stock"]["food"] if h else 0.0)
            if have + 1e-9 >= need:
                own = min(need, a["holdings"]["food"])
                a["holdings"]["food"] = round(a["holdings"]["food"] - own, 6)
                if need - own > 1e-9:
                    h["stock"]["food"] = round(h["stock"]["food"] - (need - own), 6)
                a["stage"], a["missed"] = min(0, a["stage"] + 1), 0
                rec["ate"][name] = need
            else:
                a["stage"], a["missed"] = max(-2, a["stage"] - 1), a["missed"] + 1
                rec["missed"].append(name)
        if rnd < self.rounds - 1:                                           # 5. hazard (never in the last round)
            for name in self.living():
                a = s["agents"][name]
                if a["missed"] >= 3:
                    n = a["missed"] - 2
                    h = min(1.0, a["frailty"] + float(p["hazard"]["step"]) * (n - 1))
                    if self.rng("hazard", rnd, name).random() < h or n >= int(p["hazard"]["max_rounds"]):
                        self.die(name, "starvation")
                        rec["deaths"].append(name)
        if self.cold():                                                     # 6. the cold
            for name in self.living():
                if rec["shelter"].get(name) == "unsheltered" and self.rng("cold", rnd, name).random() < float(p["cold"]["starving"]):
                    s["agents"][name]["stage"] = -2
                    rec["cold_falls"].append(name)
        for name in self.living():                                          # 7. spoilage
            f = s["agents"][name]["holdings"]
            lost = f["food"] * float(p["spoil"]["hands"])
            f["food"] = round(f["food"] - lost, 6)
            rec["spoiled"] += lost
        for h in s["houses"].values():
            lost = h["stock"]["food"] * float(p["spoil"]["house"])
            h["stock"]["food"] = round(h["stock"]["food"] - lost, 6)
            rec["spoiled"] += lost
        rec["spoiled"] = round(rec["spoiled"], 4)
        for hid, h in s["houses"].items():                                  # 8. breaks
            q = float(p["breaks"]["cold" if self.cold() else "p"])
            if h["condition"] > 0 and self.rng("break", rnd, hid).random() < q:
                h["condition"] -= 1
                rec["breaks"].append(hid)
        rec["stocks"] = {nid: {"plants": round(n["plants"]["S"], 2) if n["plants"] else None,
                               "plants_K": round(n["plants"]["K"], 2) if n["plants"] else None,
                               "game": round(n["game"]["G"], 2) if n["game"] else None} for nid, n in s["nodes"].items()}
        rec["agents"] = {n: {"at": a["at"], "stage": a["stage"], "missed": a["missed"], "food": round(a["holdings"]["food"], 2),
                             "timber": round(a["holdings"]["timber"], 2), "alive": a["alive"]} for n, a in s["agents"].items()}
        rec["houses"] = {hid: {"condition": h["condition"], "food": round(h["stock"]["food"], 2),
                               "timber": round(h["stock"]["timber"], 2)} for hid, h in s["houses"].items()}
        s["log"].append(rec)
        s["hunts"], s["gathered"] = {}, {}
        s["round"] += 1
        return rec

    def _hunts(self, rec) -> None:
        """The old engine's individual hunt (camptypes/forest.py, engine 14): every effort unit of every member is one draw, in an
        order shuffled per party, at the game density left by the draws before it; a bigger party raises each draw's chance of
        bigger game, crowding thins every draw; each hunter keeps its own catch, scaled by its hunger."""
        hp = self.p["hunt"]
        for nid in sorted(self.s["hunts"]):
            g = self.s["nodes"][nid]["game"]
            for party in sorted(self.s["hunts"][nid]):
                members = self.s["hunts"][nid][party]
                E = sum(members[a] * self.p["hunger_yield"][self.s["agents"][a]["stage"]] for a in members)
                c = 1.0 / (1.0 + E / float(hp["crowd"]))
                draws = [a for a in sorted(members) for _ in range(int(members[a]))]
                rng = self.rng("hunt", self.r, nid, party)
                rng.shuffle(draws)
                caught = {a: 0.0 for a in members}
                for a in draws:
                    dens = g["G"] / g["K"] if g["K"] else 0.0
                    pl = min(.95, hp["large"]["p"] * dens * c * (1 - math.exp(-(E / hp["large"]["scale"]) ** hp["large"]["shape"])))
                    pm = min(.95, hp["medium"]["p"] * dens * c * (1 - math.exp(-(E / hp["medium"]["scale"]) ** hp["medium"]["shape"])))
                    ps = min(.95, hp["small"]["p"] * dens * c)
                    u = rng.random()
                    food = hp["large"]["food"] if u < pl else hp["medium"]["food"] if u < pl + pm else hp["small"]["food"] if u < pl + pm + ps else 0.0
                    food = min(food, g["G"])
                    g["G"] = round(g["G"] - food, 6)
                    got = food * self.p["hunger_yield"][self.s["agents"][a]["stage"]]
                    caught[a] += got
                    self.s["agents"][a]["holdings"]["food"] = round(self.s["agents"][a]["holdings"]["food"] + got, 6)
                rec["hunts"].append({"node": nid, "party": party, "effort": E, "caught": {a: round(v, 2) for a, v in caught.items()}})

    def die(self, name, cause) -> None:
        a = self.s["agents"][name]
        a["alive"], a["died"], a["cause"] = False, self.r, cause
        h = self.home(name)
        for i in ITEMS:                                                     # the household keeps what it held
            if h is not None:
                h["stock"][i] = round(h["stock"][i] + a["holdings"][i], 6)
            a["holdings"][i] = 0.0

    def save(self, path) -> None:
        with open(path, "w") as f:
            json.dump(self.s, f)


def load_spec(path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
