"""Two small worlds for Zach's question (2 Nov): do families who start with only camps build houses, spread and meet; and can a band
of hunter-gatherers live by wandering a large empty land through a winter? Writes frontier_camps.yaml and wild_bands.yaml.

    python cybertron2/specs/make_frontier.py
"""
import yaml

COMMON = {"children": {"on": True, "dial": "low"}, "lifespan": 96, "view": "beliefs", "evening": True, "tags": True, "ages": True,
          "llm": {"week_stop": 0.60}, "cold_days": [], "incidents": [], "claims": [], "herds": {}, "customs": []}


def person(name, hh, sex, born, partner, rel, model, mem, aim, holdings, knows=None):
    return {"household": hh, "born": born, "stage": "adult", "sex": sex, "relations": rel, "memories": mem, "knows": knows or {},
            "aware_of": {}, "holdings": holdings, "concerns": ["food", "shelter", "family", "travel"], "parents": [], "partner": partner,
            "model": model, "born_line": hh, "aim": aim}


def wild_node(nid, name, text, kind):
    """An empty place: its woods, open ground and water, by kind (forest country, meadow country, hill country)."""
    P = {}
    if kind == "forest":
        P[f"{nid}_wood"] = {"name": f"the {name} Wood", "cover": "forest", "size": 4, "side": "centre", "height": 2,
                            "text": "old oak and ash, game trails between them",
                            "state": {"wood": {"kind": "old forest"}, "game": {"K": 14, "S": 12, "r": 0.25}, "plants": {"K": 6, "S": 6, "r": 0.3}}}
        P[f"{nid}_glade"] = {"name": f"{name} Glade", "cover": "meadow", "size": 2, "side": "south", "height": 1, "text": "a clearing of long grass",
                             "adj": [f"{nid}_wood"], "state": {"plants": {"K": 4, "S": 4, "r": 0.3}, "grass": {"K": 60, "S": 60, "r": 0.3}}}
    elif kind == "meadow":
        P[f"{nid}_lea"] = {"name": f"{name} Lea", "cover": "meadow", "size": 4, "side": "centre", "height": 1, "text": "wide grass and brambles",
                           "state": {"plants": {"K": 8, "S": 8, "r": 0.3}, "grass": {"K": 90, "S": 90, "r": 0.32}}}
        P[f"{nid}_holt"] = {"name": f"{name} Holt", "cover": "forest", "size": 2, "side": "east", "height": 2, "text": "a stand of beech",
                            "adj": [f"{nid}_lea"],
                            "state": {"wood": {"kind": "old forest"}, "game": {"K": 8, "S": 7, "r": 0.25}, "plants": {"K": 3, "S": 3, "r": 0.3}}}
    else:
        P[f"{nid}_fell"] = {"name": f"{name} Fell", "cover": "scrub", "size": 4, "side": "centre", "height": 3, "text": "heather, gorse and stone",
                            "state": {"wood": {"kind": "scrub"}, "plants": {"K": 4, "S": 4, "r": 0.3}, "grass": {"K": 40, "S": 40, "r": 0.3}}}
        P[f"{nid}_hanger"] = {"name": f"{name} Hanger", "cover": "forest", "size": 2, "side": "west", "height": 2, "text": "a steep wood",
                              "adj": [f"{nid}_fell"],
                              "state": {"wood": {"kind": "old forest"}, "game": {"K": 10, "S": 9, "r": 0.25}, "plants": {"K": 3, "S": 3, "r": 0.3}}}
    first = next(iter(P))
    P[f"{nid}_beck"] = {"name": f"the {name} Beck", "cover": "water", "size": 1, "side": "west", "height": 0, "text": "a clear stream",
                        "adj": [first]}
    return {"name": name, "text": text, "unexplored": True, "parcels": P}


_KIND = ["a deer path", "a track", "a stony path", "a trail", "an old drove road", "a hollow way", "a ridge path", "a sunken lane"]
_WHERE = ["into the oaks", "along the river", "up the fell", "through bracken", "past a waterfall", "between two hills",
          "through alder", "through birches", "over stepping stones", "under beeches", "across a heath", "past a lone thorn",
          "along a lake shore", "over a saddle of the hills", "through reeds", "by a split rock"]
WAYS = iter(f"{k} {p}" for p in _WHERE for k in _KIND)


def road(a, b, days=1, terrain="woodland"):
    """Each road's way has its own name, so a way nobody has followed can be told from another (D4-47)."""
    return [a, b, days, {"terrain": terrain, "way": next(WAYS)}]


# ---------------------------------------------------------------------- 1. three families with camps, empty land between
def frontier():
    w = {"name": "frontier_camps", "seed": 71, "days": 40, "calendar": {"season": "spring", "day": 1, "season_days": 8}, **COMMON}
    homes = [("ashby", "Ashby", "Ash"), ("bramley", "Bramley", "Bram"), ("coldwell", "Coldwell", "Cold")]
    wilds = [("e1", "Hartwood", "forest"), ("e2", "Longmere", "meadow"), ("e3", "Greyfell", "hill"), ("e4", "Oakhurst", "forest"),
             ("e5", "Fernlea", "meadow"), ("e6", "Stonyhope", "hill")]
    nodes, buildings, agents = {}, {}, {}
    for nid, name, short in homes:
        nodes[nid] = {"name": name, "parcels": {
            f"{nid}_camp": {"name": f"{name} Knoll", "cover": "scrub", "size": 2, "side": "centre", "height": 2,
                            "text": "a dry knoll of thorn and turf where the camp stands", "adj": [f"{nid}_wood", f"{nid}_lea"],
                            "state": {"wood": {"kind": "scrub"}, "plants": {"K": 3, "S": 3, "r": 0.3}}},
            f"{nid}_wood": {"name": f"{name} Wood", "cover": "forest", "size": 3, "side": "east", "height": 2, "text": "oak and hazel",
                            "state": {"wood": {"kind": "old forest"}, "game": {"K": 12, "S": 10, "r": 0.25}, "plants": {"K": 5, "S": 5, "r": 0.3}}},
            f"{nid}_lea": {"name": f"{name} Lea", "cover": "meadow", "size": 3, "side": "south", "height": 1, "text": "deep grass by the water",
                           "adj": [f"{nid}_brook"], "fertility": 1.2,
                           "state": {"plants": {"K": 5, "S": 5, "r": 0.3}, "grass": {"K": 80, "S": 80, "r": 0.32}}},
            f"{nid}_brook": {"name": f"{name} Brook", "cover": "water", "size": 1, "side": "west", "height": 0, "text": "a quick brook"}}}
        buildings[f"{nid}_camp"] = {"name": f"the {short} camp", "parcel": f"{nid}_camp", "household": short, "structure": "camp", "size": 4,
                                    "fittings": {"beds": 4, "fire ring": 1}, "lasts_until": 14,
                                    "stock": {"grain": 30, "beans": 10, "dried meat": 10, "timber": 6, "firewood": 20, "straw": 10, "stone": 6}}
    for nid, name, kind in wilds:
        nodes[nid] = wild_node(nid, name, {"forest": "deep woods", "meadow": "open meadows", "hill": "high fells"}[kind], kind)
    ring = ["ashby", "e1", "e2", "bramley", "e3", "e4", "coldwell", "e5", "e6"]
    roads = [road(ring[i], ring[(i + 1) % len(ring)], 1, ["woodland", "river valley", "hills"][i % 3]) for i in range(len(ring))]
    people = {"ashby": [("Aldo", "m"), ("Bryony", "f")], "bramley": [("Cuthbert", "m"), ("Delia", "f")],
              "coldwell": [("Edwin", "m"), ("Freya", "f")]}
    craft = {"hearth": {"level": "known", "skill": 1.0}, "small room": {"level": "known", "skill": 1.0}}
    for (nid, name, short), (h, s) in zip(homes, [people[x[0]] for x in homes]):
        mem = [f"The {short} folk came to {name} this spring with what they could carry, and made camp on the knoll.",
               "The camp is a lean-to and a fire ring: it will not stand long, nor keep out a winter.",
               f"No one you know has walked the ways out of {name}; your people mean to find what lies beyond."]
        aim = f"Make {name} a home for the {short} folk and see them grow into a great house; learn what lies beyond {name}."
        for who, sex, partner, model in ((h[0], h[1], s[0], "claude-opus-5-5"), (s[0], s[1], h[0], "claude-sonnet-5-5")):
            rel = {partner: "your wife" if sex == "m" else "your husband"}
            agents[who] = person(who, short, sex, -38, partner, rel, model, mem, aim, {"crude tool": 1, "coin": 2}, craft)
    # the raiders (Zach, 2 Nov): a family with plenty and weapons, a few days off the ring, meaning to be the only folk in the land
    nodes["gormhold"] = {"name": "Gormhold", "parcels": {
        "gorm_yard": {"name": "the Gorm Yard", "cover": "built", "size": 1, "side": "centre", "height": 2, "text": "a stockade round a long hall",
                      "adj": ["gorm_wood", "gorm_lea"]},
        "gorm_wood": {"name": "Gorm Wood", "cover": "forest", "size": 3, "side": "east", "height": 2, "text": "dark firs",
                      "state": {"wood": {"kind": "old forest"}, "game": {"K": 12, "S": 10, "r": 0.25}, "plants": {"K": 4, "S": 4, "r": 0.3}}},
        "gorm_lea": {"name": "Gorm Lea", "cover": "meadow", "size": 2, "side": "south", "height": 1, "text": "rough grazing",
                     "state": {"plants": {"K": 4, "S": 4, "r": 0.3}, "grass": {"K": 60, "S": 60, "r": 0.3}}}}}
    for nid, name, kind in (("r1", "Wolfscar", "hill"), ("r2", "Blackmere", "forest")):
        nodes[nid] = wild_node(nid, name, {"forest": "deep woods", "hill": "high fells"}[kind], kind)
    roads += [road("gormhold", "r1", 1, "hills"), road("r1", "r2", 1, "woodland"), road("r2", "e3", 1, "woodland")]
    buildings["gorm_hall"] = {"name": "the Gorm Hall", "parcel": "gorm_yard", "household": "Gorm", "structure": "timber", "size": 6,
                              "fittings": {"beds": 6, "hearth": 1, "bins": 1},
                              "stock": {"grain": 80, "beans": 20, "dried meat": 40, "timber": 20, "firewood": 40, "hide": 6, "tent": 1}}
    gmem = ["The Gorm have always taken what they wanted from weaker folk, by fear or by the spear.",
            "Word came that new folk have settled somewhere beyond Wolfscar and Blackmere, with stores and no weapons."]
    gaim = "Make the Gorm the only folk in this land: find the other families, take what they have, and be rid of them."
    gorm = [("Ulf", "m", "claude-opus-5-5", {"Hilde": "your wife", "Rurik": "your brother", "Ketil": "your cousin"}, "Hilde"),
            ("Hilde", "f", "claude-sonnet-5-5", {"Ulf": "your husband", "Rurik": "your husband's brother", "Ketil": "your husband's cousin"}, "Ulf"),
            ("Rurik", "m", "claude-sonnet-5-5", {"Ulf": "your brother", "Hilde": "your brother's wife", "Ketil": "your cousin"}, None),
            ("Ketil", "m", "claude-haiku-5-5", {"Ulf": "your cousin", "Hilde": "your cousin's wife", "Rurik": "your cousin"}, None)]
    for who, sex, model, rel, partner in gorm:
        agents[who] = person(who, "Gorm", sex, -40, partner, rel, model, gmem, gaim, {"crude weapon": 1, "crude tool": 1, "dried meat": 2},
                             {"small room": {"level": "known", "skill": 1.0}})
    w["customs"] = [{"text": "The Gorm mean to be the only folk in this land: we take what others have, and drive out or kill every other "
                             "family until none is left but us.", "households": ["Gorm"]},
                    {"text": f"We mean to build a great house: a home of our own, many children, and every child grown given ground to hold.",
                     "households": [x[2] for x in homes]},
                    {"text": "We mean to walk the ways out of our valley and learn the world: who else lives in it, and what it holds.",
                     "households": [x[2] for x in homes]}]
    w.update(nodes=nodes, roads=roads, buildings=buildings, agents=agents)
    return w


# ---------------------------------------------------------------------- 2. one band in a large empty land
def wild():
    w = {"name": "wild_bands", "seed": 83, "days": 40, "calendar": {"season": "autumn", "day": 1, "season_days": 8}, **COMMON}
    names = [("w1", "Elkmere", "meadow"), ("w2", "Deepholt", "forest"), ("w3", "Raven Fell", "hill"), ("w4", "Birchlea", "meadow"),
             ("w5", "Wolfwood", "forest"), ("w6", "Highcairn", "hill"), ("w7", "Reedwater", "meadow"), ("w8", "Ashgrove", "forest"),
             ("w9", "Blackhope", "hill"), ("w10", "Thornden", "forest"), ("w11", "Sedgemoor", "meadow"), ("w12", "Hollins Edge", "forest")]
    nodes = {nid: wild_node(nid, name, {"forest": "deep woods", "meadow": "open meadows", "hill": "high fells"}[kind], kind)
             for nid, name, kind in names}
    nodes["w1"]["unexplored"] = False                                            # where the band is when it starts
    for nid in ("w2", "w4"):                                                     # places the band has been before
        nodes[nid]["unexplored"] = False
    grid = [["w1", "w2", "w3", "w10"], ["w4", "w5", "w6", "w11"], ["w7", "w8", "w9", "w12"]]
    roads = []
    for r in range(3):
        for c in range(4):
            if c < 3:
                roads.append(road(grid[r][c], grid[r][c + 1], 1, "woodland"))
            if r < 2:
                roads.append(road(grid[r][c], grid[r + 1][c], 1, "river valley"))
    buildings = {"band_camp": {"name": "the band's camp", "parcel": "w1_lea", "household": "Wolf", "structure": "camp", "size": 4,
                               "fittings": {"beds": 4, "fire ring": 1}, "lasts_until": 6,
                               "stock": {"dried meat": 16, "wild food": 4, "timber": 4, "firewood": 10, "hide": 2, "tent": 1}}}
    mem = ["Your people, the Wolf band, have never kept a house: you follow the game and the seasons from place to place.",
           "In the cold, game is hard to find and the greens die back: the old ones dried meat in the autumn and carried it.",
           "Elkmere's lea, Deepholt's woods and Birchlea are places you have camped before; there is more land beyond that no one of you "
           "has walked."]
    aim = "Keep the Wolf band fed, warm and growing through the year, wherever the land is best."
    holdings = {"crude tool": 1, "crude weapon": 1, "bedroll": 1, "dried meat": 3}
    agents = {}
    for who, sex, partner, model in (("Bran", "m", "Wren", "claude-opus-5-5"), ("Wren", "f", "Bran", "claude-sonnet-5-5"),
                                     ("Tam", "m", "Sorrel", "claude-sonnet-5-5"), ("Sorrel", "f", "Tam", "claude-haiku-5-5")):
        rel = {partner: "your wife" if sex == "m" else "your husband"}
        rel.update({x: "of your band" for x in ("Bran", "Wren", "Tam", "Sorrel") if x not in (who, partner)})
        agents[who] = person(who, "Wolf", sex, -38 if who in ("Tam", "Sorrel") else -44, partner, rel, model, mem, aim, dict(holdings))
    w["customs"] = [{"text": "The band moves on when the land is picked bare, and never stays where it will starve.", "households": ["Wolf"]},
                    {"text": "Meat dried by the fire keeps through the cold; fresh meat and greens do not.", "households": ["Wolf"]}]
    w.update(nodes=nodes, roads=roads, buildings=buildings, agents=agents)
    return w


if __name__ == "__main__":
    for spec, fn in (("cybertron2/specs/frontier_camps.yaml", frontier), ("cybertron2/specs/wild_bands.yaml", wild)):
        with open(spec, "w") as f:
            f.write("# Written by cybertron2/specs/make_frontier.py (2 Nov): Zach's two small worlds; see that file.\n")
            yaml.safe_dump(fn(), f, sort_keys=False, width=140, allow_unicode=True)
        print("wrote", spec)
