"""The world: places, people, houses, and what happens at the end of every round.

State (World.s, plain JSON so a round can be saved and read back):
    round       0-based round number
    nodes       {id: {name, text, plants: {S, K, K0, r, yield, refuge} | None, game: {G, K, r, inflow} | None, timber: bool,
                      copper: float (copper per mine action, 0: no mine), forge: bool}}
    edges       {id: [neighbour ids]}
    agents      {name: {household, house, model, role, age, aim, at, holdings: {food, timber, copper, blade, crude}, stage,
                        missed, frailty, attack, defence, cannot, alive, died, cause, notes}}
    houses      {id: {name, node, household, beds, condition (2 sound, 1 damaged, 0 ruined), stock: {...}, work}}
    hunts       this round's hunting effort: {node: {party: {agent: units}}}
    fights      this round's attacks and raids, settled at night (combat.py)
    guards      agents standing guard tonight
    gathered    this round's gathering actions per agent (forage, hunt, fell and mine count toward physics.gather_per_round)
    know        each agent's knowledge (perceive.py): what it has seen, heard and remembers
    log         per-round records (what the report reads)

Random streams are seeded strings, as in the old engine: random.Random(f"{seed}|<stream>|<round>|<who>"), so a draw depends only
on the seed and the round, never on call order.

The end of the round (end_of_round), in order:
    1. hunts      each party's effort at its place draws catches (the old engine's individual mode; every effort unit draws, a
                  bigger party raises the chance of bigger game, crowding thins it, the game stock caps it)
    2. fights     raids on houses, then attacks on people, against whoever is at the place at night (combat.py)
    3. regrowth   plants and game regrow logistically, game also by inflow x (K - G) (animals walking in: the old engine's
                  inflow); in a cold round plants x cold.plants, game x cold.game
    4. hearth     each house with an occupant sleeping there burns fuel (timber) from its stock
    5. ration     each living agent needs ration x its shelter multiplier; it eats from its hands, then (sleeping at its own house)
                  from the house stock. ration_rule "partial" (the default here): it eats what it can up to the need; below the
                  base ration it misses a meal (stage down one); at least the base ration but short of the need, its stage
                  holds; the full need moves it up one. "all_or_nothing": the old engine's rule (short of the need, nothing)
    6. hazard     from 3 missed meals in a row: death with chance frailty + 0.15 per further miss, certain at 4 more
    7. the cold   an unsheltered agent in a cold round falls straight to starving with chance cold.starving (after the ration,
                  so it bites next round; it counts no missed meal)
    8. spoilage   food in hands loses spoil.hands, in a house spoil.house
    9. breaks     each house drops a level with chance breaks.p (breaks.cold in a cold round)
"""
from __future__ import annotations

import copy
import json
import math
import random

import yaml

STAGES = {0: "fed", -1: "hungry", -2: "starving"}
CONDITION = {2: "sound", 1: "damaged", 0: "ruined"}
ITEMS = ("food", "timber", "copper", "blade", "crude")
ITEM_WORDS = {"blade": "blades", "crude": "crude weapons"}

PHYSICS = {
    "actions": 4,                                   # actions a turn when fed; hungry one fewer, starving at most 2
    "gather_per_round": 2,                          # forage, hunt, fell and mine actions an agent may take a round
    "ration": 1.0,
    "ration_rule": "partial",                       # partial | all_or_nothing (the old engine's)
    "shelter": {"housed": 1.0, "damaged": 1.2, "unsheltered": 1.5},            # ration multiplier, normal round
    "shelter_cold": {"housed": 1.0, "no_fuel": 1.3, "damaged": 1.5, "unsheltered": 2.0},
    "cold": {"plants": 0.25, "game": 0.5, "starving": 0.3},
    "fuel": {"normal": 0.5, "cold": 2.0},           # timber a house burns a round when someone sleeps there
    "spoil": {"hands": 0.15, "house": 0.05},
    "breaks": {"p": 0.02, "cold": 0.08},
    "repair": {"timber": 5.0, "work": 3},           # one level: timber in the house stock and work actions there
    "fell": {"timber": 3.0, "k_loss": 0.01, "floor": 0.5},   # timber a fell; plant capacity lost a fell (x K0), down to floor x K0
    "forge": {"copper": 6.0, "timber": 1.0},        # a blade
    "craft": {"timber": 2.0},                       # a crude weapon (a club)
    "hunger_yield": {0: 1.0, -1: 0.75, -2: 0.5},
    "frailty": [0.25, 0.55],
    "hazard": {"step": 0.15, "max_rounds": 4},
    "hunt": {"large": {"p": 0.07, "food": 20.0, "scale": 5.0, "shape": 3.0},
             "medium": {"p": 0.32, "food": 5.0, "scale": 2.5, "shape": 2.0},
             "small": {"p": 0.95, "food": 1.0}, "crowd": 12.0},
    # combat (combat.py; a simplified port of the old engine's harm model, docs/review/21_combat.md)
    "combat": {"base": [0.5, 1.5], "weapon": {"blade": 5.0, "crude": 2.0}, "guard": 2.0, "asleep": 0.5,
               "attack_actions": 2, "raid_actions": 2, "food_cost": 1.0, "raid_share": 0.6, "counter": 0.3},
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
        s = {"round": 0, "nodes": {}, "edges": {}, "agents": {}, "houses": {}, "hunts": {}, "fights": [], "guards": [],
             "gathered": {}, "know": {}, "log": [], "gifts": []}
        for nid, n in spec["nodes"].items():
            node = {"name": n.get("name", nid), "text": n.get("text", ""), "plants": None, "game": None,
                    "timber": bool(n.get("timber", False)), "copper": float(n.get("copper", 0.0)), "forge": bool(n.get("forge", False))}
            if n.get("plants"):
                pl = n["plants"]
                node["plants"] = {"K": float(pl["K"]), "K0": float(pl["K"]), "S": float(pl["K"]) * float(pl.get("start", 0.8)),
                                  "r": float(pl["r"]), "yield": float(pl.get("yield", 2.0)), "refuge": float(pl.get("refuge", 0.1))}
            if n.get("game"):
                g = n["game"]
                node["game"] = {"K": float(g["K"]), "G": float(g["K"]) * float(g.get("start", 0.8)), "r": float(g["r"]),
                                "inflow": float(g.get("inflow", 0.01))}
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
        blo, bhi = self.p["combat"]["base"]
        hh_cannot = {name: list(v.get("cannot") or []) for name, v in (spec.get("households") or {}).items()}
        for name, a in spec["agents"].items():
            hh = a["household"]
            s["agents"][name] = {
                "household": hh, "house": house_of.get(hh), "model": a.get("model"), "role": a.get("role", ""),
                "age": a.get("age"), "aim": a.get("aim", ""), "at": a.get("at") or s["houses"][house_of[hh]]["node"],
                "holdings": {i: float((a.get("holdings") or {}).get(i, 0.0)) for i in ITEMS},
                "stage": 0, "missed": 0, "frailty": round(random.Random(f"{self.seed}|frailty|{name}").uniform(lo, hi), 4),
                "attack": round(random.Random(f"{self.seed}|attack|{name}").uniform(blo, bhi), 4),
                "defence": round(random.Random(f"{self.seed}|defence|{name}").uniform(blo, bhi), 4),
                "cannot": sorted(set(a.get("cannot") or []) | set(hh_cannot.get(hh, []))),
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

    def place(self, node) -> str:
        return self.s["nodes"][node]["name"]

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
        """housed | no_fuel | damaged | unsheltered: where the agent ends the round decides."""
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
        return "plentiful" if f > 0.6 else "fair" if f > 0.3 else "scarce" if f > 0.1 else "almost gone"

    def condition_word(self, name) -> str:
        """How a person looks to someone beside them: their hunger, and a wound or the cold this round shows as their stage."""
        return {0: "well", -1: "hungry", -2: "starving"}[self.s["agents"][name]["stage"]]

    def load_word(self, name) -> str:
        """What a person visibly carries, coarsely: food, timber, copper, weapons."""
        h = self.s["agents"][name]["holdings"]
        out = []
        f = h["food"]
        if f >= 6:
            out.append("a lot of food")
        elif f >= 2:
            out.append("some food")
        elif f > 0.2:
            out.append("a little food")
        if h["timber"] >= 0.5:
            out.append("timber")
        if h["copper"] >= 0.5:
            out.append("copper")
        if h["blade"] >= 1:
            out.append("a blade" if h["blade"] < 2 else "blades")
        elif h["crude"] >= 1:
            out.append("a club")
        return ", ".join(out) if out else "empty-handed"

    def stock_word(self, hid) -> str:
        """Another household's stock as a visitor judges it: never numbers."""
        f = self.s["houses"][hid]["stock"]["food"]
        return "well stocked" if f >= 20 else "stocked" if f >= 10 else "poorly stocked" if f >= 3 else "nearly bare"

    def rng(self, *parts) -> random.Random:
        return random.Random("|".join([str(self.seed)] + [str(p) for p in parts]))

    # ------------------------------------------------------------------ the end of the round
    def end_of_round(self) -> dict:
        from cybertron2 import combat
        s, p, rnd = self.s, self.p, self.r
        rec = {"round": rnd, "cold": self.cold(), "hunts": [], "fights": [], "ate": {}, "short": [], "missed": [], "deaths": [],
               "cold_falls": [], "breaks": [], "shelter": {}, "hearth": {}, "spoiled": 0.0}
        self._hunts(rec)
        rec["fights"] = combat.resolve(self)                                # 2. raids and attacks at night
        rec["deaths"] += [f["killed"] for f in rec["fights"] if f.get("killed")]
        for nid, n in s["nodes"].items():                                   # 3. regrowth
            if n["plants"]:
                pl = n["plants"]
                r = pl["r"] * (p["cold"]["plants"] if self.cold() else 1.0)
                pl["S"] = round(min(pl["K"], pl["S"] + r * pl["S"] * (1 - pl["S"] / pl["K"])), 6)
            if n["game"]:
                g = n["game"]
                r = g["r"] * (p["cold"]["game"] if self.cold() else 1.0)
                g["G"] = round(min(g["K"], g["G"] + r * g["G"] * (1 - g["G"] / g["K"]) + g["inflow"] * (g["K"] - g["G"])), 6)
        fuel_ok = {}
        for hid, h in s["houses"].items():                                  # 4. hearth
            sleepers = [n for n in self.living() if s["agents"][n]["house"] == hid and self.sleeps_home(n)]
            need = float(p["fuel"]["cold" if self.cold() else "normal"]) if sleepers else 0.0
            ok = h["stock"]["timber"] + 1e-9 >= need
            if ok:
                h["stock"]["timber"] = round(h["stock"]["timber"] - need, 6)
            fuel_ok[hid] = ok
            rec["hearth"][hid] = {"sleepers": len(sleepers), "burnt": need if ok else 0.0, "lit": ok}
        base = float(p["ration"])
        for name in self.living():                                          # 5. ration
            a = s["agents"][name]
            state = self.shelter(name, fuel_ok.get(a["house"], True))
            rec["shelter"][name] = state
            need = round(base * self.shelter_mult(state), 6)
            h = self.home(name) if self.sleeps_home(name) else None
            have = a["holdings"]["food"] + (h["stock"]["food"] if h else 0.0)
            if p["ration_rule"] == "all_or_nothing" and have + 1e-9 < need:
                eat = 0.0
            else:
                eat = round(min(need, have), 6)
            own = min(eat, a["holdings"]["food"])
            a["holdings"]["food"] = round(a["holdings"]["food"] - own, 6)
            if eat - own > 1e-9:
                h["stock"]["food"] = round(h["stock"]["food"] - (eat - own), 6)
            if eat + 1e-9 >= need:
                a["stage"], a["missed"] = min(0, a["stage"] + 1), 0
                rec["ate"][name] = need
            elif eat + 1e-9 >= base:                                         # partial: fed enough to hold, not to recover
                a["missed"] = 0
                rec["ate"][name] = eat
                rec["short"].append(name)
            else:
                a["stage"], a["missed"] = max(-2, a["stage"] - 1), a["missed"] + 1
                if eat > 0:
                    rec["ate"][name] = eat
                rec["missed"].append(name)
        if rnd < self.rounds - 1:                                           # 6. hazard (never in the last round)
            for name in self.living():
                a = s["agents"][name]
                if a["missed"] >= 3:
                    n = a["missed"] - 2
                    h = min(1.0, a["frailty"] + float(p["hazard"]["step"]) * (n - 1))
                    if self.rng("hazard", rnd, name).random() < h or n >= int(p["hazard"]["max_rounds"]):
                        self.die(name, "starvation")
                        rec["deaths"].append(name)
        if self.cold():                                                     # 7. the cold
            for name in self.living():
                if rec["shelter"].get(name) == "unsheltered" and self.rng("cold", rnd, name).random() < float(p["cold"]["starving"]):
                    s["agents"][name]["stage"] = -2
                    rec["cold_falls"].append(name)
        for name in self.living():                                          # 8. spoilage
            f = s["agents"][name]["holdings"]
            lost = f["food"] * float(p["spoil"]["hands"])
            f["food"] = round(f["food"] - lost, 6)
            rec["spoiled"] += lost
        for h in s["houses"].values():
            lost = h["stock"]["food"] * float(p["spoil"]["house"])
            h["stock"]["food"] = round(h["stock"]["food"] - lost, 6)
            rec["spoiled"] += lost
        rec["spoiled"] = round(rec["spoiled"], 4)
        for hid, h in s["houses"].items():                                  # 9. breaks
            q = float(p["breaks"]["cold" if self.cold() else "p"])
            if h["condition"] > 0 and self.rng("break", rnd, hid).random() < q:
                h["condition"] -= 1
                rec["breaks"].append(hid)
        rec["stocks"] = {nid: {"plants": round(n["plants"]["S"], 2) if n["plants"] else None,
                               "plants_K": round(n["plants"]["K"], 2) if n["plants"] else None,
                               "game": round(n["game"]["G"], 2) if n["game"] else None} for nid, n in s["nodes"].items()}
        rec["agents"] = {n: {"at": a["at"], "stage": a["stage"], "missed": a["missed"],
                             **{i: round(a["holdings"][i], 2) for i in ITEMS}, "alive": a["alive"]} for n, a in s["agents"].items()}
        rec["houses"] = {hid: {"condition": h["condition"], **{i: round(h["stock"][i], 2) for i in ITEMS}}
                         for hid, h in s["houses"].items()}
        s["log"].append(rec)
        s["hunts"], s["gathered"], s["fights"], s["guards"] = {}, {}, [], []
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
                members = {a: u for a, u in self.s["hunts"][nid][party].items() if self.s["agents"][a]["alive"]}
                if not members:
                    continue
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

    def die(self, name, cause, to=None) -> None:
        """A death: what the agent carried goes to `to` (killers' shares) or else to its household's house."""
        a = self.s["agents"][name]
        a["alive"], a["died"], a["cause"] = False, self.r, cause
        h = self.home(name)
        for i in ITEMS:
            q = a["holdings"][i]
            if to:
                for b, share in to.items():
                    self.s["agents"][b]["holdings"][i] = round(self.s["agents"][b]["holdings"][i] + q * share, 6)
            elif h is not None:
                h["stock"][i] = round(h["stock"][i] + q, 6)
            a["holdings"][i] = 0.0

    def save(self, path) -> None:
        with open(path, "w") as f:
            json.dump(self.s, f)


def load_spec(path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
