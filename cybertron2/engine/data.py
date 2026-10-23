"""The world's data (D4-24: the world grows by rows, not code). Numbers follow the spec where decided and recipes.md (a proposal)
where not, marked "calibrate" in the spec.

ITEMS       good -> {weight, food (meals a unit), spoil (share lost a night in hand), tool (grade), weapon (strength), life (uses
            before a tool or weapon is worn out), seen (noticed when carried)}
COVERS      cover -> {words, lots (buildings per size), ambient [(sense, text, salience)]}
RESOURCES   what a parcel can hold -> {regime (D4-7), words by level}
FITTINGS    fitting -> {label, materials, units, needs (another fitting), basic, does}
BLUEPRINTS  building -> {label, materials, units, size (people), structure, basic}
TECHNIQUES  name -> {verb, label, aliases, basic, at {covers | fittings | building}, draws (a resource), yield {kind, ...}, tools
            {grade: multiplier} (bare hands: "bare"; absent grade: refused), weapon, wear (a use), inputs, gives, units, tags}
PHYSICS     the numbers of the day and the night
"""
from __future__ import annotations

ITEMS = {
    "grain": {"weight": 1, "food": 1.0, "spoil": 0.0},                 # porridge at a hearth (D2-44); seed (D2-17)
    "flour": {"weight": 1, "food": 0.0, "spoil": 0.0},
    "bread": {"weight": 1, "food": 1.1, "spoil": 0.05},                # 11 from 10, keeps (D2-44)
    "wild food": {"weight": 1, "food": 1.0, "spoil": 0.15},
    "meat": {"weight": 1, "food": 1.5, "spoil": 0.30},                 # dense, spoils fresh (D2-41)
    "milk": {"weight": 1, "food": 0.5, "spoil": 1.0},                  # the same day (D2-42)
    "timber": {"weight": 2, "food": 0.0, "spoil": 0.0},                # D2-24
    "stone": {"weight": 3, "food": 0.0, "spoil": 0.0},                 # D2-3, D2-24
    "hide": {"weight": 1, "food": 0.0, "spoil": 0.0},                  # D2-24
    "copper ore": {"weight": 3, "food": 0.0, "spoil": 0.0},
    "copper": {"weight": 1, "food": 0.0, "spoil": 0.0},                # D2-19, D2-24
    "coin": {"weight": 0, "food": 0.0, "spoil": 0.0},                  # copper coin, carried (D2-1, D2-28)
    "crude tool": {"weight": 1, "food": 0.0, "spoil": 0.0, "tool": "crude", "life": 10, "seen": True},      # D2-23; recipes.md §6
    "copper tool": {"weight": 1, "food": 0.0, "spoil": 0.0, "tool": "copper", "life": 40, "seen": True},
    "crude weapon": {"weight": 1, "food": 0.0, "spoil": 0.0, "weapon": 2.0, "life": 10, "seen": True},     # D2-46: about 3 fights
    "pack": {"weight": 1, "food": 0.0, "spoil": 0.0, "carry": 10, "seen": True},      # on foot 10, with a pack 20 (02g §3; calibrate)
    "handcart": {"weight": 0, "food": 0.0, "spoil": 0.0, "carry": 30, "track": True, "seen": True},   # 40 in all, on a track (02g §3)
}
EDIBLE = tuple(i for i, v in ITEMS.items() if v["food"] > 0)
TOOLS = tuple(sorted((i for i, v in ITEMS.items() if v.get("tool")), key=lambda i: -("crude", "copper").index(ITEMS[i]["tool"])))
WEAPONS = tuple(i for i, v in ITEMS.items() if v.get("weapon"))

COVERS = {
    "forest": {"words": "woodland", "lots": 0,
               "ambient": [("sound", "birdsong and the creak of trees from {name}", 0.2), ("smell", "leaf mould on the air from {name}", 0.15)]},
    "field": {"words": "fields", "lots": 0, "ambient": [("sight", "{name} stretching out beyond the houses", 0.1)]},
    "pasture": {"words": "pasture", "lots": 0,
                "ambient": [("sound", "cattle lowing on {name}", 0.35), ("smell", "dung and trodden grass from {name}", 0.15)]},
    "meadow": {"words": "meadow", "lots": 0, "ambient": [("sound", "insects in the long grass of {name}", 0.15)]},
    "water": {"words": "water", "lots": 0, "ambient": [("sound", "water running over stones in {name}", 0.3)]},
    "built": {"words": "built ground", "lots": 6, "ambient": [("sound", "voices and work about the houses", 0.2)]},
    "scrub": {"words": "scrub", "lots": 4, "ambient": []},
    "rock": {"words": "rock", "lots": 0, "ambient": [("sound", "the ring of picks from {name}", 0.25)]},
}

# How each resource comes back (D4-7) and how it is seen (in words, never numbers: environment/resources.md).
RESOURCES = {
    "plants": {"regime": "fast", "low": "{name} has been picked over: little wild food left", "high": "{name} is thick with berries, nuts and greens"},
    "game": {"regime": "threshold", "low": "few fresh tracks in {name}: the game is thin", "high": "fresh deer slots and droppings along the rides of {name}"},
    "wood": {"regime": "slow", "low": "{name} is thinned out: stumps where the big trees stood", "high": ""},
    "seam": {"regime": "finite", "low": "the seam at {name} is nearly worked out", "high": "a green-stained seam in {name}"},
    "quarry": {"regime": "endless", "low": "", "high": "a face of good stone at {name}"},
}

# Fittings and blueprints: recipes.md §3 (a proposal; calibrate). A building is its structure and its fittings (D2-9).
FITTINGS = {
    "beds": {"label": "beds", "materials": {"timber": 2, "hide": 1}, "units": 1, "per": "bed", "basic": True,
             "does": "housed when sleeping here, one a bed"},
    "hearth": {"label": "a hearth", "materials": {"stone": 4}, "units": 3, "basic": False, "trade": "mason",
               "does": "warmth (burns timber), porridge and baking"},
    "bins": {"label": "bins", "materials": {"timber": 3}, "units": 1, "basic": True, "does": "a store for food"},
    "quern": {"label": "a quern", "materials": {"stone": 2}, "units": 1, "basic": True, "does": "grinding grain by hand"},  # calibrate
    "anvil": {"label": "an anvil and bellows", "materials": {"stone": 6, "hide": 2, "timber": 1}, "units": 4, "needs": "hearth",
              "basic": False, "trade": "smith", "does": "a smithy: smelting and smithing"},
    "cellar": {"label": "a cellar", "materials": {"stone": 8}, "units": 8, "basic": False, "trade": "mason",
               "does": "food keeps at a quarter of the house rate"},
    "millstones": {"label": "millstones", "materials": {"stone": 10}, "units": 10, "basic": False, "trade": "mason",
                   "does": "milling: grain to flour by the dozen (D2-44)"},
}
BLUEPRINTS = {
    "small room": {"label": "a small room, wattle and timber", "materials": {"timber": 8}, "units": 6, "size": 4, "structure": "wattle",
                   "basic": True},
    "medium room": {"label": "a medium room, timber on stone", "materials": {"timber": 15, "stone": 4}, "units": 15, "size": 10,
                    "structure": "timber", "basic": False, "trade": "carpenter"},
    "hall": {"label": "a hall, timber on stone", "materials": {"timber": 30, "stone": 10}, "units": 30, "size": 25,
             "structure": "timber", "basic": False, "trade": "carpenter"},
}

# Techniques: one handler reads these (38.17 §5). Tool multipliers by grade (recipes.md §8); "bare" is bare hands; a grade missing
# from `tools` means the work cannot be done with it (no mining bare-handed).
TECHNIQUES = {
    "forage": {"verb": "gather", "label": "foraging (greens, roots, berries, nuts)", "aliases": ["foraging", "gather food"], "basic": True,
               "at": {"covers": ["forest", "meadow", "pasture", "scrub"]}, "draws": "plants", "yield": {"kind": "stock", "base": 1.2},
               "units": 1, "gives": "wild food", "tags": ["food"]},
    "hunt": {"verb": "gather", "label": "hunting game", "aliases": ["hunting"], "basic": True, "at": {"covers": ["forest"]},
             "draws": "game", "yield": {"kind": "chance", "p": 0.35, "range": [2, 6], "by": {"hide": 0.25}},
             "weapon": {"none": 0.3, "armed": 1.0}, "wear": 0.3, "units": 2, "gives": "meat", "tags": ["food", "hunting", "animals"]},
    "fell": {"verb": "gather", "label": "felling timber", "aliases": ["felling", "chop timber", "cut wood"], "basic": True,
             "at": {"covers": ["forest"]}, "draws": "wood", "yield": {"kind": "fixed", "base": 3.0},
             "tools": {"bare": 0.25, "crude": 1.0, "copper": 2.0}, "wear": 1, "units": 2, "gives": "timber", "tags": ["timber", "woodland"]},
    "mine": {"verb": "gather", "label": "mining copper ore", "aliases": ["mining", "dig ore"], "at": {"covers": ["rock"]}, "draws": "seam",
             "yield": {"kind": "fixed", "base": 2.0}, "tools": {"crude": 1.0, "copper": 1.5}, "wear": 2, "units": 2, "gives": "copper ore",
             "tags": ["mining", "craft"], "trade": "miner"},
    "quarry": {"verb": "gather", "label": "quarrying stone", "aliases": ["quarrying", "cut stone"], "at": {"covers": ["rock"]},
               "draws": "quarry", "yield": {"kind": "fixed", "base": 2.0}, "tools": {"crude": 1.0, "copper": 1.5}, "wear": 2, "units": 2,
               "gives": "stone", "tags": ["building", "craft"], "trade": "mason"},
    "sow": {"verb": "work", "label": "sowing a field", "aliases": ["sowing", "plant"], "basic": True, "at": {"covers": ["field"]},
            "draws": "plot", "yield": {"kind": "sow"}, "units": 1, "gives": "", "tags": ["farming"]},
    "weed": {"verb": "work", "label": "weeding a growing crop", "aliases": ["weeding", "tend"], "basic": True, "at": {"covers": ["field"]},
             "draws": "crop", "yield": {"kind": "tend"}, "units": 1, "gives": "", "tags": ["farming"]},
    "reap": {"verb": "work", "label": "reaping grain", "aliases": ["reaping", "harvest"], "basic": True, "at": {"covers": ["field"]},
             "draws": "crop", "yield": {"kind": "crop", "base": 6.0}, "tools": {"bare": 0.6, "crude": 1.0, "copper": 1.5}, "wear": 0.5,
             "units": 2, "gives": "grain", "tags": ["food", "farming", "harvest"]},
    "milk": {"verb": "work", "label": "milking (a cow in milk)", "aliases": ["milking"], "at": {"covers": ["pasture"]}, "draws": "herd",
             "yield": {"kind": "milk", "base": 3.0}, "units": 1, "gives": "milk", "tags": ["food", "animals"], "trade": "herder"},
    "slaughter": {"verb": "work", "label": "slaughtering a beast", "aliases": ["butcher", "kill a cow"], "basic": True,
                  "at": {"covers": ["pasture", "meadow", "built"]}, "draws": "herd", "yield": {"kind": "slaughter", "gives": {"meat": 15, "hide": 2}},
                  "units": 2, "gives": "meat", "tags": ["food", "animals"]},
    "repair": {"verb": "work", "label": "repairing a building", "aliases": ["mend"], "basic": True, "at": {"building": True},
               "yield": {"kind": "repair"}, "inputs": {"timber": 2}, "units": 2, "gives": "", "tags": ["building", "shelter"]},
    "grind": {"verb": "make", "label": "grinding flour at a quern", "aliases": ["grinding", "mill"], "basic": True, "at": {"fittings": ["quern"]},
              "inputs": {"grain": 4}, "units": 1, "gives": {"flour": 4}, "tags": ["food", "cooking"]},
    "mill": {"verb": "make", "label": "milling grain at millstones", "aliases": ["milling"], "basic": True, "at": {"fittings": ["millstones"]},
             "inputs": {"grain": 12}, "units": 1, "gives": {"flour": 12}, "tags": ["food", "cooking"]},                  # recipes.md §10
    "pack": {"verb": "make", "label": "making a pack", "aliases": ["backpack"], "basic": True, "inputs": {"hide": 1, "timber": 1},
             "units": 1, "gives": {"pack": 1}, "tags": ["travel"]},                                                    # recipes.md §2
    "handcart": {"verb": "make", "label": "making a handcart", "aliases": ["cart"], "inputs": {"timber": 6}, "tools": {"crude": 1.0, "copper": 1.0},
                 "units": 3, "gives": {"handcart": 1}, "tags": ["travel", "craft"], "trade": "carpenter"},              # recipes.md §2
    "bread": {"verb": "make", "label": "baking bread", "aliases": ["baking", "bake"], "basic": True, "at": {"fittings": ["hearth"]},
              "inputs": {"flour": 10, "timber": 1}, "units": 1, "gives": {"bread": 11}, "tags": ["food", "cooking"]},
    "crude tool": {"verb": "make", "label": "making a crude hand tool", "aliases": ["tool"], "basic": True, "inputs": {"timber": 1, "stone": 0.5},
                   "units": 1, "gives": {"crude tool": 1}, "tags": ["craft"]},
    "crude weapon": {"verb": "make", "label": "making a crude weapon", "aliases": ["club", "spear", "weapon"], "basic": True,
                     "inputs": {"timber": 1}, "units": 1, "gives": {"crude weapon": 1}, "tags": ["weapons"]},
    "smelt": {"verb": "make", "label": "smelting copper", "aliases": ["smelting"], "at": {"fittings": ["anvil"]},
              "inputs": {"copper ore": 3, "timber": 4}, "units": 3, "gives": {"copper": 1}, "tags": ["mining", "craft"], "trade": "smelter"},
    "copper tool": {"verb": "make", "label": "making a copper hand tool", "aliases": ["hand tool", "metal tool"], "at": {"fittings": ["anvil"]},
                    "inputs": {"copper": 1, "timber": 0.5}, "units": 3, "gives": {"copper tool": 1}, "tags": ["craft", "smithing"], "trade": "smith"},
    "coin": {"verb": "make", "label": "striking coin", "aliases": ["strike coin", "minting"], "at": {"fittings": ["anvil"]},
             "inputs": {"copper": 1}, "units": 1, "gives": {"coin": 10}, "tags": ["craft", "smithing"], "trade": "smith"},
}
# Building and fitting are techniques too, for knowledge (basic or a trade), with their costs in BLUEPRINTS and FITTINGS.
for _k, _b in list(BLUEPRINTS.items()) + list(FITTINGS.items()):
    TECHNIQUES.setdefault(_k, {"verb": "build", "label": "building " + _b["label"], "aliases": [], "basic": _b.get("basic", False),
                               "units": _b["units"], "gives": "", "tags": ["building", "shelter"], "trade": _b.get("trade")})

LEVELS = ("aware", "rough", "capable", "known")
TRY = {"rough": {"inputs": 1.7, "chance": 0.5}, "capable": {"inputs": 1.3, "chance": 0.75}, "known": {"inputs": 1.0, "chance": 1.0}}
SKILL_WORDS = ((1.6, "master"), (1.2, "skilled"), (0.8, "competent"), (0.0, "novice"))

PHYSICS = {
    "units": {"summer": 7, "autumn": 6, "winter": 5, "spring": 6},      # agents/work.md (calibrate)
    "youth_units": 4,
    "elder_units": 5,
    "ration": 1.0,
    "shelter": {"housed": 1.0, "damaged": 1.2, "unsheltered": 1.5},     # D4-12, H-5
    "shelter_cold": {"housed": 1.0, "no_fuel": 1.3, "damaged": 1.5, "unsheltered": 2.0},
    "cold_starving": 0.3,                                                # H-5
    "fuel": {"normal": 0.5, "cold": 2.0},
    "house_spoil": 0.3,
    "cellar_spoil": 0.25,                                                # D2-45: a quarter of the house rate
    "breaks": {"p": 0.02, "cold": 0.08},
    "hunger_yield": {"0": 1.0, "-1": 0.75, "-2": 0.5},
    "frailty": [0.25, 0.55],
    "hazard": {"step": 0.15, "max_rounds": 4},
    "refuge": 0.1,                                                       # the share of a stock foraging never takes
    "regrow_winter": 0.25,
    "game_threshold": 0.15,                                              # below this share of capacity game does not come back
    "combat": {"base": [0.5, 1.5], "guard": 2.0, "asleep": 0.5, "units": 3, "raid_share": 0.5, "fight_wear": 4},
    "teach": {"units_teacher": 2, "units_learner": 2, "skill_share": 0.3},
    "watch": {"units": 4},
    "notes": {"max": 8, "words": 150, "open": 2},
    "felt_watched": 0.3,
    "glimpse": 3,
    "messages": {"per_day": 3, "jitter": {0: 37, 1: 37, 2: 18, 3: 8}, "max": 10},     # D4-31
    "say_units": 1,                                                                       # D4-31
    "carry": {"foot": 10},                                                                # transport.md (calibrate, OPEN C-1)
    "farming": {"seed_per_unit": 3, "return": 5.0, "grow_days": 6, "window": 2, "rot": 0.25, "weed_max": 0.5, "weed_step": 0.2},  # 02l (calibrate)
    "repair": {"timber": 2},
}
