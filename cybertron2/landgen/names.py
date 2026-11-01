"""Names from parts chosen by the land (D2-186; stage 1 §11g): a settlement's or wild place's name is a first part from its land
and an ending from its site, as English place names formed, so a name says something true (a -ford has a ford); parcels take plain
patterns by cover, shape, side and feature. Chosen by keyed draws; no name repeats within a world."""
from __future__ import annotations

from cybertron2.landgen import keyed

FIRST = {
    "wood": ["Ash", "Oak", "Birch", "Hazel", "Elm", "Holt", "Thorn"],
    "stone": ["Stan", "Crag", "Scar", "Flint"],
    "water": ["Brook", "Mar", "Wel", "Fleet", "Wat"],
    "low": ["Holl", "Dun", "Mere"],
    "wet": ["Fen", "Reed", "Sedge", "Moss"],
    "meadow": ["Hay", "Lea", "Mead"],
    "high": ["Cold", "High", "Hart", "Wether"],
    "sea": ["Salt", "Sea", "Strand"],
    "plain": ["Barley", "Wheat", "Rye", "Wyn", "Ald", "Ken", "Brad"],
    "mill": ["Mill"],
}
ENDING = {
    "ford": ["ford"], "lake": ["mere"], "wood": ["ley", "hurst", "holt"], "valley": ["den", "combe", "dale"],
    "hidden": ["hope"], "pasture": ["wick", "worth"], "sea": ["mouth", "haven"], "high": ["low", "don"],
    "settlement": ["ton", "ham", "by", "thorpe", "stead"],
}
RIVERS = ["Wen", "Lyde", "Ouse", "Tame", "Arrow", "Leven", "Dove", "Isel", "Brue", "Cale", "Wharf", "Nene"]


class Namer:
    def __init__(self, seed):
        self.seed = seed
        self.used = set()

    def pick(self, key, options: list, *more: list) -> str:
        rg = keyed.rng(self.seed, "name", key)
        pool = list(options)
        rg.shuffle(pool)
        for extra in more:
            e = list(extra)
            rg.shuffle(e)
            pool += e
        for x in pool:
            if x not in self.used:
                self.used.add(x)
                return x
        n = 2
        while f"{pool[0]} {n}" in self.used:
            n += 1
        self.used.add(f"{pool[0]} {n}")
        return f"{pool[0]} {n}"

    def place(self, key: str, facts: dict) -> str:
        """facts: ford, lake, wood, valley, hidden, pasture, sea, high, stone, wet, meadow, mill (booleans)."""
        first = [w for k in ("mill", "stone", "wet", "sea", "high", "water", "wood", "meadow", "low") if facts.get(k) for w in FIRST[k]]
        first = first or FIRST["plain"]
        ends = [w for k in ("ford", "lake", "sea", "hidden", "valley", "wood", "pasture", "high") if facts.get(k) for w in ENDING[k]]
        ends = (ends or []) + ENDING["settlement"]
        rg = keyed.rng(self.seed, "place-name", key)
        for _ in range(60):
            f, e = rg.choice(first[:4] if len(first) > 4 and rg.random() < 0.7 else first), rg.choice(ends[:3] if rg.random() < 0.7 else ends)
            nm = (f + e).capitalize() if not f.endswith(e[0]) else (f + e[1:]).capitalize()
            if nm not in self.used:
                self.used.add(nm)
                return nm
        return self.pick(key, [f + "ton" for f in FIRST["plain"]])

    def river(self, key: str) -> str:
        return self.pick(f"river:{key}", RIVERS)

    def parcel(self, node_name: str, p, river: str | None) -> str:
        """Plain names: the Green, North Field, Brook Meadow, the Common, the Hanger, the Moss."""
        c, side, key = p.cover, p.side, f"{node_name}:{p.pid}"
        sidew = {"north": "North", "south": "South", "east": "East", "west": "West", "centre": "Middle"}[side]
        long_ = p.size >= 4 and _elongated(p.cells)
        if c == "built":
            return self.pick(key, ["the Green", f"{node_name} Green", "the Street"])
        if c == "field":
            opts = [f"{sidew} Field"] + (["Long Field"] if long_ else []) + (["Brook Field"] if p.facts.get("river") else [])
            opts += ["Clay Field" if p.soil == "clay" else "Sand Field" if p.soil == "sand" else "Broad Field", f"{node_name} Field"]
            return self.pick(key, opts, [f"{sidew} Field {k}" for k in ("Upper", "Lower")])
        if c == "meadow":
            return self.pick(key, ([f"{river} Meadow"] if river else []) + ["Brook Meadow", "Mill Meadow", f"{node_name} Meadow", "the Ham"])
        if c == "pasture":
            return self.pick(key, ["the Common", f"{sidew} Pasture", "the Leaze", "Cow Close", f"{node_name} Common"])
        if c == "forest":
            if p.wood_kind == "old forest":
                return self.pick(key, ["the Holt", "the Deep Wood", "the Old Wood", f"{node_name} Wood"])
            steep = p.facts.get("slope", 0) > 6
            return self.pick(key, (["the Hanger"] if steep else []) + [f"{node_name} Copse", f"{sidew} Wood", "the Spinney", "Hazel Copse"])
        if c == "heath":
            return self.pick(key, [f"{node_name} Heath", "the Heath", "Furze Common"])
        if c == "moor":
            return self.pick(key, ["the Moss", f"{node_name} Moor", "the High Moor"])
        if c == "fen":
            return self.pick(key, [f"{node_name} Fen", "the Carr", "the Sedge"])
        if c == "saltmarsh":
            return self.pick(key, ["the Saltings", f"{node_name} Marsh"])
        if c == "scrub":
            return self.pick(key, [f"{node_name} Moor", "the Rough", "Thorn Bank", "the Brakes"])
        if c == "rock":
            return self.pick(key, ["the Scar", "the Crags", f"{node_name} Scar"])
        if c == "water":
            return self.pick(key, ([f"the {river}"] if river else []) + ["the Brook", "the Mere", f"{node_name} Water"])
        return self.pick(key, [f"{sidew} {c.title()}"])


def _elongated(cells) -> bool:
    rs = [r for r, _ in cells]
    cs = [c for _, c in cells]
    a, b = max(rs) - min(rs) + 1, max(cs) - min(cs) + 1
    return max(a, b) >= 2.5 * min(a, b)
