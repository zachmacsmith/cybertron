"""The world's data (D4-24: the world grows by rows, not code). Numbers follow the spec where decided and recipes.md (a proposal)
where not, marked "calibrate" in the spec.

ITEMS       good -> {weight, food (meals a unit), spoil (share lost a night in hand), tool (grade), weapon (strength), life (uses
            before a tool or weapon is worn out), seen (noticed when carried), cook (eaten only at a lit hearth), fodder (a beast's
            day of feed a unit)}
CROPS       crop -> {seed (the good sown), gives, share (of the year it grows), hardy, takes and restores (the soil), names}
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
    "grain": {"weight": 1, "food": 0.7, "spoil": 0.0167, "cook": True, "decay": "grain"},  # boiled whole at a hearth (D2-60); seed (D2-17); spoils
                                                                       # 0.5% a day in a house, less in bins, a cellar, a granary (D2-58)
    "rye": {"weight": 1, "food": 0.7, "spoil": 0.0167, "cook": True, "decay": "grain"},    # winter grain (D2-53)
    "beans": {"weight": 1, "food": 0.6, "spoil": 0.0167, "cook": True, "decay": "grain"},  # legumes: less food, restore the soil (D2-53)
    "flour": {"weight": 1, "food": 1.0, "spoil": 0.0167, "cook": True, "decay": "grain"},  # ground grain, eaten as porridge (D2-60)
    "bread": {"weight": 1, "food": 1.3, "spoil": 0.05, "decay": "bread"},                # keeps, eaten without a hearth (D2-60)
    "dried meat": {"weight": 1, "food": 3.0, "spoil": 0.02, "decay": "dried meat"},           # meat dried to half its weight (D2-62)
    "cheese": {"weight": 1, "food": 2.5, "spoil": 0.02, "decay": "cheese"},               # 6 milk (D2-47, D2-56)
    "salt": {"weight": 1, "food": 0.0, "spoil": 0.0},                  # D2-24, D2-56
    "hay": {"weight": 1, "food": 0.0, "spoil": 0.0, "fodder": 1.0},    # cut from pasture in summer (D4-42)
    "straw": {"weight": 1, "food": 0.0, "spoil": 0.0, "fodder": 1.0},  # from the grain harvest (D4-42)
    "dung": {"weight": 1, "food": 0.0, "spoil": 0.0},                  # manure (D2-18, D4-39)
    "charcoal": {"weight": 2, "food": 0.0, "spoil": 0.0},              # from 5 timber, made at the wood (D2-56)
    "wild food": {"weight": 1, "food": 1.0, "spoil": 0.15},
    "meat": {"weight": 1, "food": 1.5, "spoil": 0.30, "decay": "fresh meat"},                 # dense, spoils fresh (D2-41)
    "milk": {"weight": 1, "food": 0.5, "spoil": 1.0},                  # the same day (D2-42)
    "timber": {"weight": 2, "food": 0.0, "spoil": 0.0},                # D2-24
    "stone": {"weight": 3, "food": 0.0, "spoil": 0.0},                 # D2-3, D2-24
    "hide": {"weight": 1, "food": 0.0, "spoil": 0.0, "decay": "hide"},                  # D2-24
    "copper ore": {"weight": 3, "food": 0.0, "spoil": 0.0},
    "copper": {"weight": 1, "food": 0.0, "spoil": 0.0},                # D2-19, D2-24
    "coin": {"weight": 0, "food": 0.0, "spoil": 0.0},                  # copper coin, carried (D2-1, D2-28)
    "crude tool": {"weight": 1, "food": 0.0, "spoil": 0.0, "tool": "crude", "life": 10, "seen": True},      # D2-23; recipes.md §6
    "copper tool": {"weight": 1, "food": 0.0, "spoil": 0.0, "tool": "copper", "life": 40, "seen": True},
    "crude weapon": {"weight": 1, "food": 0.0, "spoil": 0.0, "weapon": 2.0, "life": 10, "seen": True},     # D2-46: about 3 fights
    "pack": {"weight": 1, "food": 0.0, "spoil": 0.0, "carry": 10, "seen": True},      # on foot 10, with a pack 20 (02g §3; calibrate)
    "handcart": {"weight": 0, "food": 0.0, "spoil": 0.0, "carry": 30, "track": True, "seen": True},   # 40 in all, on a track (02g §3)
    "wooden plough": {"weight": 4, "food": 0.0, "spoil": 0.0, "life": 60, "seen": True},       # D2-23; recipes.md §2 (60 plots)
    "harness": {"weight": 1, "food": 0.0, "spoil": 0.0, "life": 80, "seen": True},             # D2-23; 80 days' use
    "bedroll": {"weight": 1, "food": 0.0, "spoil": 0.0, "life": 40, "seen": True, "camp": "bedroll"},    # D2-68: about 40 nights
    "tent": {"weight": 6, "food": 0.0, "spoil": 0.0, "life": 30, "seen": True, "camp": "tent"},          # D2-68: sleeps 2
    "rotting meat": {"weight": 1, "food": 0.0, "spoil": 0.3, "rot": True},  # what fresh meat becomes in the open (D2-87); signs, no health yet
}

# Decay by condition (economy/goods.md "Decay", D2-87; calibrate): multipliers on an item's rate in a house, for a thing at a spot
# (open, dry or wet; buried), and for the season and the frost; `abs` is a share lost a day where the house rate is none (hides);
# `becomes` is what the lost share turns into in the open.
DECAY = {
    "grain": {"open_dry": 4, "open_wet": 10, "buried": 2, "warm": 1.2, "frozen": 0.5},
    "bread": {"open_dry": 3, "open_wet": 8, "buried": 3, "warm": 1.5, "frozen": 0.2},
    "fresh meat": {"open_dry": 2, "open_wet": 2.5, "buried": 1, "warm": 1.5, "frozen": 0.1, "becomes": "rotting meat"},
    "dried meat": {"open_dry": 2, "open_wet": 6, "buried": 2, "warm": 1.2, "frozen": 0.5},
    "cheese": {"open_dry": 3, "open_wet": 5, "buried": 1, "warm": 1.5, "frozen": 0.3},
    "hide": {"abs": {"open_dry": 0.01, "open_wet": 0.03, "buried": 0.02}},
    "default": {"open_dry": 2, "open_wet": 4, "buried": 1, "warm": 1.2, "frozen": 0.5},   # goods the table does not name (37.4; calibrate)
}

# Crops (D2-53, D4-38, D4-39; 02l §2-§3, calibrate): grow for a share of the year from the day sown; the cold kills what is still
# growing unless it is hardy; each takes from the soil and restores it toward a level.
CROPS = {
    "grain": {"seed": "grain", "gives": "grain", "share": 0.25, "hardy": False, "takes": 0.15, "restores": [0.10, 1.0], "straw": True,
              "names": ["barley", "oats", "wheat", "grain"]},
    "winter grain": {"seed": "rye", "gives": "rye", "share": 0.33, "hardy": True, "takes": 0.15, "restores": [0.10, 1.0], "straw": True,
                     "names": ["rye", "winter grain"]},
    "legumes": {"seed": "beans", "gives": "beans", "share": 0.17, "hardy": False, "takes": 0.0, "restores": [0.40, 1.0], "straw": False,
                "names": ["beans", "peas", "legumes"]},
}
CROP_OF = {n: c for c, d in CROPS.items() for n in d["names"]}
SEED_CROP = {d["seed"]: c for c, d in CROPS.items()}
EDIBLE = tuple(i for i, v in ITEMS.items() if v["food"] > 0)
TOOLS = tuple(sorted((i for i, v in ITEMS.items() if v.get("tool")), key=lambda i: -("crude", "copper").index(ITEMS[i]["tool"])))
WEAPONS = tuple(i for i, v in ITEMS.items() if v.get("weapon"))

COVERS = {
    "forest": {"words": "woodland", "lots": 0, "sight": 0.35, "sound": 0.7, "dig": "soft",
               "ambient": [("sound", "birdsong and the creak of trees from {name}", 0.2), ("smell", "leaf mould on the air from {name}", 0.15)]},
    "field": {"words": "fields", "lots": 0, "sight": 1.0, "sound": 1.0, "dig": "soft", "ambient": [("sight", "{name} stretching out beyond the houses", 0.1)]},
    "pasture": {"words": "pasture", "lots": 0, "sight": 1.0, "sound": 1.0, "dig": "soft",
                "ambient": [("sound", "cattle lowing on {name}", 0.35), ("smell", "dung and trodden grass from {name}", 0.15)]},
    "meadow": {"words": "meadow", "lots": 0, "sight": 1.0, "sound": 1.0, "dig": "soft", "ambient": [("sound", "insects in the long grass of {name}", 0.15)]},
    "water": {"words": "water", "lots": 0, "sight": 1.0, "sound": 1.0, "dig": "soft", "ambient": [("sound", "water running over stones in {name}", 0.3)]},
    "built": {"words": "built ground", "lots": 6, "sight": 0.7, "sound": 1.0, "dig": "soft", "ambient": [("sound", "voices and work about the houses", 0.2)]},
    "scrub": {"words": "scrub", "lots": 4, "sight": 0.5, "sound": 0.9, "dig": "stony", "ambient": []},
    "rock": {"words": "rock", "lots": 0, "sight": 0.5, "sound": 0.9, "dig": "stony", "ambient": [("sound", "the ring of picks from {name}", 0.25)]},
}

# How each resource comes back (D4-7) and how it is seen (in words, never numbers: environment/resources.md).
RESOURCES = {
    "plants": {"regime": "fast", "low": "{name} has been picked over: little wild food left", "high": "{name} is thick with berries, nuts and greens"},
    "game": {"regime": "threshold", "low": "few fresh tracks in {name}: the game is thin", "high": "fresh deer slots and droppings along the rides of {name}"},
    "wood": {"regime": "slow", "low": "{name} is thinned out: stumps where the big trees stood", "high": ""},
    "seam": {"regime": "finite", "low": "the seam at {name} is nearly worked out", "high": "a green-stained seam in {name}"},
    "quarry": {"regime": "endless", "low": "", "high": "a face of good stone at {name}"},
    "grass": {"regime": "fast", "low": "{name} is grazed bare", "high": "good grass on {name}"},             # D4-45
    "dung": {"regime": "accrues", "low": "", "high": "dung lies thick where the beasts have been on {name}"},
}

# Fittings and blueprints: recipes.md §3 (a proposal; calibrate). A building is its structure and its fittings (D2-9).
FITTINGS = {
    "beds": {"label": "beds", "materials": {"timber": 2, "straw": 2}, "units": 1, "per": "bed", "basic": True,
             "does": "housed when sleeping here, one a bed"},                                                  # D2-56
    "hearth": {"label": "a hearth", "materials": {"stone": 4}, "units": 3, "basic": False, "trade": "mason", "fire": True,
               "does": "warmth (burns timber), porridge and baking"},
    "bins": {"label": "bins", "materials": {"timber": 3}, "units": 1, "basic": True, "does": "a store for food", "spoil": 0.5},
    "hand mill": {"label": "a hand mill", "materials": {"stone": 2}, "units": 2, "basic": True, "does": "grinding grain by hand",
                  "aliases": ["quern"]},                                                                     # D2-61
    "granary": {"label": "a granary floor", "materials": {"timber": 6}, "units": 4, "basic": True, "spoil": 0.2,
                "does": "grain keeps longest, raised and dry"},                                              # D2-58
    "fire ring": {"label": "a fire ring", "materials": {"stone": 1}, "units": 1, "basic": True, "fire": True,
                  "does": "a fire in the open for warmth and cooking (burns timber)"},                              # D2-68: a camp's fire
    "oven": {"label": "a stone oven", "materials": {"stone": 6}, "units": 4, "basic": False, "trade": "mason",
             "does": "baking bread in batches"},                                                             # D2-60
    "anvil": {"label": "an anvil and bellows", "materials": {"stone": 6, "hide": 2, "timber": 1}, "units": 4, "needs": "hearth",
              "basic": False, "trade": "smith", "does": "a smithy: smelting and smithing"},
    "cellar": {"label": "a cellar", "materials": {"stone": 8}, "units": 8, "basic": False, "trade": "mason", "spoil": 0.25,
               "does": "food keeps at a quarter of the house rate"},
    "millstones": {"label": "dressed millstones", "materials": {"stone": 10}, "units": 10, "basic": False, "trade": "mason",
                   "does": "an ox mill: an ox turns them (D2-61)"},
    "water wheel": {"label": "a water wheel", "materials": {"timber": 15, "copper": 1}, "units": 12, "needs": "millstones", "site": "water",
                    "basic": False, "trade": "carpenter", "does": "a water mill: the river turns the millstones (D2-61)"},
}
FITTING_ALIAS = {a: f for f, d in FITTINGS.items() for a in d.get("aliases", [])}
BLUEPRINTS = {
    "small room": {"label": "a small room, wattle and timber", "materials": {"timber": 8}, "units": 6, "size": 4, "structure": "wattle",
                   "basic": True},
    "medium room": {"label": "a medium room, timber on stone", "materials": {"timber": 15, "stone": 4}, "units": 15, "size": 10,
                    "structure": "timber", "basic": False, "trade": "carpenter"},
    "hall": {"label": "a hall, timber on stone", "materials": {"timber": 30, "stone": 10}, "units": 30, "size": 25,
             "structure": "timber", "basic": False, "trade": "carpenter"},
    "camp": {"label": "a camp (a lean-to and a fire ring)", "materials": {"timber": 3}, "units": 1, "size": 4, "structure": "camp",
             "basic": True, "fittings": {"beds": 4, "fire ring": 1}, "lasts": 10},                                  # D2-68
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
    # Farming (D2-53, D2-54, D2-59, D4-38 to D4-40; 02l §2 scaled to the plot of about 16 seed, calibrate)
    "sow": {"verb": "work", "label": "sowing a field broadcast (seed thrown)", "aliases": ["sowing", "plant", "broadcast"], "basic": True,
            "at": {"covers": ["field"]}, "draws": "plot", "yield": {"kind": "sow", "seed": 6.0, "worth": 1.0}, "units": 1, "gives": "",
            "tags": ["farming"]},
    "hoe": {"verb": "work", "label": "breaking the soil with a hoe", "aliases": ["hoeing", "dig", "break the soil"], "basic": True,
            "at": {"covers": ["field"]}, "draws": "plot", "yield": {"kind": "break", "plots": 0.0625, "stone": 1.0},
            "tools": {"bare": 0.5, "crude": 1.0, "copper": 1.5}, "wear": 0.5, "units": 1, "gives": "", "tags": ["farming"]},
    "plough": {"verb": "work", "label": "ploughing with a yoked pair of oxen", "aliases": ["ploughing", "plow"], "at": {"covers": ["field"]},
               "draws": "plot", "yield": {"kind": "break", "plots": 0.25, "stone": 1.0}, "animals": {"oxen": 2},
               "uses": {"wooden plough": 1, "harness": 2}, "units": 1, "gives": "", "tags": ["farming", "animals"], "trade": "farmer"},
    "ditch": {"verb": "work", "label": "ditching and banking wet ground", "aliases": ["ditches", "drain", "ditch and bank"],
              "at": {"covers": ["field"]}, "draws": "plot", "yield": {"kind": "works", "ground": "wet", "units": 40.0, "upkeep": 1.5},
              "tools": {"bare": 0.5, "crude": 1.0, "copper": 1.5}, "wear": 0.75, "units": 1, "gives": "", "tags": ["farming"],
              "trade": "farmer", "crew": True},                                     # D2-66: 40 units a plot by a crew led by one who knows how
    "terrace": {"verb": "work", "label": "terracing hill ground", "aliases": ["terraces", "terracing"], "at": {"covers": ["field"]},
                "draws": "plot", "yield": {"kind": "works", "ground": "hill", "units": 60.0, "upkeep": 1.5, "stone": 6.0},
                "tools": {"bare": 0.5, "crude": 1.0, "copper": 1.5}, "wear": 0.75, "units": 1, "gives": "", "tags": ["farming"],
                "trade": "farmer", "crew": True},                                   # D2-66: 60 units and 6 stone a plot
    "select seed": {"verb": "work", "label": "selecting seed from the best of a ripe crop", "aliases": ["seed selection"],
                    "at": {"covers": ["field"]}, "draws": "crop", "yield": {"kind": "select"}, "units": 1, "gives": "", "tags": ["farming"],
                    "trade": "farmer"},                               # D2-65: one who knows it sows crops that ripen 15% sooner
    "weed": {"verb": "work", "label": "weeding a growing crop", "aliases": ["weeding", "tend"], "basic": True, "at": {"covers": ["field"]},
             "draws": "crop", "yield": {"kind": "tend"}, "units": 1, "gives": "", "tags": ["farming"]},
    "manure": {"verb": "work", "label": "manuring a field", "aliases": ["manuring", "spread dung"], "basic": True, "at": {"covers": ["field"]},
               "draws": "plot", "yield": {"kind": "manure", "plots": 0.1875}, "inputs": {"dung": 1.9}, "units": 1, "gives": "",
               "tags": ["farming", "animals"]},
    "reap": {"verb": "work", "label": "reaping a crop", "aliases": ["reaping", "harvest"], "basic": True, "at": {"covers": ["field"]},
             "draws": "crop", "yield": {"kind": "crop", "plots": 0.125, "straw": 4.7}, "tools": {"bare": 0.6, "crude": 1.0, "copper": 1.5},
             "wear": 0.25, "units": 1, "gives": "grain", "tags": ["food", "farming", "harvest"]},
    "hay": {"verb": "gather", "label": "cutting hay", "aliases": ["cut hay", "haymaking", "mow"], "basic": True, "at": {"covers": ["pasture", "meadow"]},
                "draws": "grass", "yield": {"kind": "fixed", "base": 3.0}, "tools": {"bare": 0.3, "crude": 1.0, "copper": 1.5}, "wear": 0.5,
                "seasons": ["summer"], "units": 1, "gives": "hay", "tags": ["animals", "farming"]},
    # Cattle (D2-63, D4-41, D4-44, D4-45; 02o, calibrate)
    "herd": {"verb": "work", "label": "herding (watching the beasts)", "aliases": ["herding", "watch the herd", "tend the herd"], "basic": True,
             "at": {"covers": ["pasture", "meadow", "field"]}, "draws": "herd", "yield": {"kind": "herd"}, "units": 1, "gives": "",
             "tags": ["animals"]},
    # Fences round a parcel and gates (livestock.md "Fences and gates": D2-130, D2-132): a field work on the parcel; FENCES has the numbers
    "fence": {"verb": "work", "label": "fencing a parcel round (wattle or post and rail)", "basic": True,
              "aliases": ["fencing", "put up a fence", "wattle fence", "mend the fence", "build a fence", "a fence"],
              "at": {"covers": ["pasture", "meadow", "field", "scrub"]}, "draws": "plot", "yield": {"kind": "fence", "fence": "wood"},
              "tools": {"bare": 0.5, "crude": 1.0, "copper": 1.5}, "wear": 0.5, "units": 1, "gives": "", "tags": ["animals", "farming", "timber"]},
    "wall": {"verb": "work", "label": "walling a parcel round (a dry-stone wall)", "basic": False, "trade": "mason", "crew": True,
             "aliases": ["walling", "dry wall", "dry-stone wall", "stone wall", "build a wall", "mend the wall", "a wall"],
             "at": {"covers": ["pasture", "meadow", "field", "scrub"]}, "draws": "plot", "yield": {"kind": "fence", "fence": "stone"},
             "tools": {"bare": 0.5, "crude": 1.0, "copper": 1.5}, "wear": 0.75, "units": 1, "gives": "", "tags": ["animals", "farming", "building"]},
    "open the gate": {"verb": "work", "label": "opening a gate and leaving it open", "basic": True, "aliases": ["open gate", "leave the gate open"],
                      "at": {"covers": ["pasture", "meadow", "field", "scrub"]}, "draws": "plot", "yield": {"kind": "gate", "gate": "open"},
                      "units": 0, "gives": "", "tags": ["animals"]},
    "shut the gate": {"verb": "work", "label": "shutting a gate", "basic": True, "aliases": ["shut gate", "close the gate", "close gate"],
                      "at": {"covers": ["pasture", "meadow", "field", "scrub"]}, "draws": "plot", "yield": {"kind": "gate", "gate": "shut"},
                      "units": 0, "gives": "", "tags": ["animals"]},
    "dung": {"verb": "gather", "label": "gathering dung", "aliases": ["gather dung", "collect dung"], "basic": True,
                    "at": {"covers": ["pasture", "meadow", "field"]}, "draws": "dung", "yield": {"kind": "fixed", "base": 5.0}, "units": 1,
                    "gives": "dung", "tags": ["animals", "farming"]},
    "milk": {"verb": "work", "label": "milking (a cow in milk)", "aliases": ["milking"], "at": {"covers": ["pasture", "meadow", "field"]},
             "draws": "herd", "yield": {"kind": "milk", "cows": 3, "each": 1.6}, "units": 1, "gives": "milk", "tags": ["food", "animals"],
             "trade": "herder"},
    "slaughter": {"verb": "work", "label": "slaughtering a beast", "aliases": ["butcher", "kill a cow"], "basic": True,
                  "at": {"covers": ["pasture", "meadow", "field", "built"]}, "draws": "herd",
                  "yield": {"kind": "slaughter", "gives": {"cows": {"meat": 40, "hide": 2}, "oxen": {"meat": 50, "hide": 2},
                                                          "bulls": {"meat": 50, "hide": 2}, "young": {"meat": 10, "hide": 1}}},
                  "units": 2, "gives": "meat", "tags": ["food", "animals"]},
    "repair": {"verb": "work", "label": "repairing a building", "aliases": ["mend"], "basic": True, "at": {"building": True},
               "yield": {"kind": "repair"}, "inputs": {"timber": 2}, "units": 2, "gives": "", "tags": ["building", "shelter"]},
    # Grinding and the mill ladder (D2-60, D2-61; recipes.md §16, 02n §3, calibrate): a hand mill, an ox mill, a water mill
    "grind": {"verb": "make", "label": "grinding grain at a hand mill", "aliases": ["grinding", "hand mill", "quern"], "basic": True,
              "at": {"fittings": ["hand mill"]}, "inputs": {"grain": 8}, "units": 1, "gives": {"flour": 8}, "tags": ["food", "cooking"]},
    "mill": {"verb": "make", "label": "milling grain at dressed millstones turned by an ox", "aliases": ["milling", "ox mill"], "basic": True,
             "at": {"fittings": ["millstones"]}, "animals": {"oxen": 1}, "inputs": {"grain": 16}, "units": 1, "gives": {"flour": 16},
             "tags": ["food", "cooking"]},
    "water mill": {"verb": "make", "label": "milling grain at a water mill", "aliases": ["water milling"], "basic": True,
                   "at": {"fittings": ["water wheel"]}, "inputs": {"grain": 40}, "units": 1, "gives": {"flour": 40}, "tags": ["food", "cooking"]},
    "pack": {"verb": "make", "label": "making a pack", "aliases": ["backpack"], "basic": True, "inputs": {"hide": 1, "timber": 1},
             "units": 1, "gives": {"pack": 1}, "tags": ["travel"]},                                                    # recipes.md §2
    "handcart": {"verb": "make", "label": "making a handcart", "aliases": ["cart"], "inputs": {"timber": 6}, "tools": {"crude": 1.0, "copper": 1.0},
                 "units": 3, "gives": {"handcart": 1}, "tags": ["travel", "craft"], "trade": "carpenter"},              # recipes.md §2
    "bread": {"verb": "make", "label": "baking bread at a hearth", "aliases": ["baking", "bake"], "basic": True, "at": {"fittings": ["hearth"]},
              "inputs": {"flour": 10, "timber": 1}, "units": 1, "gives": {"bread": 10}, "tags": ["food", "cooking"]},          # D2-60
    "oven bread": {"verb": "make", "label": "baking bread in a stone oven", "aliases": ["oven baking"], "basic": True,
                   "at": {"fittings": ["oven"]}, "inputs": {"flour": 40, "timber": 2}, "units": 2, "gives": {"bread": 40},
                   "tags": ["food", "cooking"]},
    "dry meat": {"verb": "make", "label": "drying meat over a fire", "aliases": ["drying meat", "cure meat"], "basic": True,
                 "at": {"fittings": ["hearth", "fire ring"]}, "inputs": {"meat": 2}, "units": 1, "gives": {"dried meat": 1}, "tags": ["food", "cooking"]},
    "cheese": {"verb": "make", "label": "making cheese", "aliases": ["cheesemaking"], "at": {"fittings": ["cellar"]},
               "inputs": {"milk": 6, "salt": 0.2}, "units": 1, "gives": {"cheese": 1}, "tags": ["food", "animals"], "trade": "herder"},
    "charcoal": {"verb": "make", "label": "burning charcoal", "aliases": ["charcoal burning"], "at": {"covers": ["forest"]},
                 "inputs": {"timber": 5}, "units": 2, "gives": {"charcoal": 1}, "tags": ["timber", "craft"], "trade": "woodsman"},
    "wooden plough": {"verb": "make", "label": "making a plough", "aliases": ["make a plough"], "inputs": {"timber": 4, "copper": 1},
                      "tools": {"crude": 1.0, "copper": 1.0}, "units": 4, "gives": {"wooden plough": 1}, "tags": ["farming", "craft"],
                      "trade": "carpenter"},
    "bedroll": {"verb": "make", "label": "making a bedroll", "aliases": ["blanket roll"], "basic": True, "inputs": {"hide": 1}, "units": 1,
                "gives": {"bedroll": 1}, "tags": ["travel"]},                                                           # D2-68
    "tent": {"verb": "make", "label": "making a tent", "aliases": [], "basic": True, "inputs": {"hide": 3, "timber": 2}, "units": 2,
             "gives": {"tent": 1}, "tags": ["travel"]},                                                                 # D2-68
    "harness": {"verb": "make", "label": "making a harness", "aliases": ["yoke"], "inputs": {"timber": 2, "hide": 1}, "units": 2,
                "gives": {"harness": 1}, "tags": ["animals", "craft"], "trade": "leatherworker"},
    "crude tool": {"verb": "make", "label": "making a crude hand tool", "aliases": ["tool"], "basic": True, "inputs": {"timber": 1, "stone": 0.5},
                   "units": 1, "gives": {"crude tool": 1}, "tags": ["craft"]},
    "crude weapon": {"verb": "make", "label": "making a crude weapon", "aliases": ["club", "spear", "weapon"], "basic": True,
                     "inputs": {"timber": 1}, "units": 1, "gives": {"crude weapon": 1}, "tags": ["weapons"]},
    "smelt": {"verb": "make", "label": "smelting copper", "aliases": ["smelting"], "at": {"fittings": ["anvil"]},
              "inputs": {"copper ore": 3, "fuel": {"charcoal": 1, "timber": 4}}, "units": 3, "gives": {"copper": 1}, "tags": ["mining", "craft"],
              "trade": "smelter"},                                  # one of the fuels (D4-46): charcoal, or timber as before
    "copper tool": {"verb": "make", "label": "making a copper hand tool", "aliases": ["hand tool", "metal tool"], "at": {"fittings": ["anvil"]},
                    "inputs": {"copper": 1, "timber": 0.5}, "units": 3, "gives": {"copper tool": 1}, "tags": ["craft", "smithing"], "trade": "smith"},
    "coin": {"verb": "make", "label": "striking coin", "aliases": ["strike coin", "minting"], "at": {"fittings": ["anvil"]},
             "inputs": {"copper": 1}, "units": 1, "gives": {"coin": 10}, "tags": ["craft", "smithing"], "trade": "smith"},
}
# Modifiers (agents/modifiers.md; D2-93, D2-94, D2-111, D2-112): techniques with `modifies` (verb, or verb:technique), the action
# argument they are written as (`key`: `value`; "*" any value), and what they change, read by the verb they modify. `untaught`:
# tryable (done worse, and one becomes aware of it) or no (refused, and one becomes aware it exists). Basic ones everyone knows.
TECHNIQUES.update({
    "for": {"verb": "modifier", "label": "doing it for someone (into their store, from it by right or agreement)", "aliases": [],
            "basic": True, "modifies": ["gather", "work", "make", "build", "give", "accept", "offer"], "key": "for", "value": "*",
            "changes": {"destination": "party"}, "units": 0, "gives": "", "tags": []},                                     # D2-37, D2-94
    "hidden: under brush": {"verb": "modifier", "label": "hiding something under brush", "aliases": ["hide", "under brush", "brush"],
                            "modifies": ["give:place"], "key": "hidden", "value": "under brush", "untaught": "tryable",
                            "changes": {"hidden": "under brush", "units": 1}, "units": 1, "gives": "", "tags": ["hiding"]},
    "hidden: buried": {"verb": "modifier", "label": "burying something to hide it", "aliases": ["bury it", "buried", "cache"],
                       "modifies": ["give:place"], "key": "hidden", "value": "buried", "untaught": "tryable",
                       "changes": {"hidden": "buried", "units": 2}, "units": 2, "gives": "", "tags": ["hiding"]},
    "method: dibble": {"verb": "modifier", "label": "dibbling seed (set by hand, seed by seed)", "aliases": ["dibble", "dibbling", "set seed"],
                       "modifies": ["work:sow"], "key": "method", "value": "dibble", "untaught": "no",
                       "changes": {"yield": {"seed": 2.0, "worth": 1.67}, "word": "dibbled"}, "units": 0, "gives": "",
                       "tags": ["farming"], "trade": "farmer"},                                      # D2-54, D2-94: 3x the work, 0.6x the seed
    "method: cairn": {"verb": "modifier", "label": "raising a cairn of stones over the dead", "aliases": ["cairn"], "basic": True,
                      "modifies": ["work:bury"], "key": "method", "value": "cairn", "changes": {"inputs": {"stone": 3}},
                      "units": 2, "gives": "", "tags": ["death"]},                                    # D2-96
    "bury": {"verb": "work", "label": "burying the dead", "aliases": ["burial", "bury the dead", "bury the body"], "basic": True,
             "at": {"things": "body"}, "yield": {"kind": "bury"}, "units": 2, "units_by": "bury", "gives": "", "tags": ["death"]},   # D2-96
})
MODIFIERS = {t for t, d in TECHNIQUES.items() if d.get("modifies")}

# Building and fitting are techniques too, for knowledge (basic or a trade), with their costs in BLUEPRINTS and FITTINGS.
for _k, _b in list(BLUEPRINTS.items()) + list(FITTINGS.items()):
    TECHNIQUES.setdefault(_k, {"verb": "build", "label": "building " + _b["label"], "aliases": [], "basic": _b.get("basic", False),
                               "units": _b["units"], "gives": "", "tags": ["building", "shelter"], "trade": _b.get("trade")})

# Techniques at least one person in the world knows (D2-129): when no one in a world file does, one is chosen by a keyed draw among the
# adults whose trade has one of these words (else among all adults), and knows it from its upbringing.
KNOWN_SOMEWHERE = {"method: dibble": ["sow", "seed", "reap", "plough", "hoe", "field", "farm"]}
LEVELS = ("aware", "rough", "capable", "known")
TRY = {"rough": {"inputs": 1.7, "chance": 0.5}, "capable": {"inputs": 1.3, "chance": 0.75}, "known": {"inputs": 1.0, "chance": 1.0}}
SKILL_WORDS = ((0.85, "master"), (0.5, "skilled"), (0.2, "competent"), (0.0, "novice"))   # by the share of the way to a master
SKILL = {"trade": [0.5, 2.0], "basic": [1.0, 1.5], "tau": 50.0}     # D2-52 (02n §4): skill by practice, units of work; calibrate

PHYSICS = {
    "units": {"summer": 7, "autumn": 6, "winter": 5, "spring": 6},      # agents/work.md (calibrate)
    "youth_units": 4,
    "elder_units": 5,
    "ration": 1.0,
    "shelter": {"housed": 1.0, "damaged": 1.2, "unsheltered": 1.5},     # D4-12, H-5
    "shelter_cold": {"housed": 1.0, "no_fuel": 1.3, "damaged": 1.5, "unsheltered": 2.0},
    "cold_starving": 0.3,                                                # H-5
    "fuel": {"normal": 0.5, "cold": 2.0, "camp": 1.0, "open": 2.0},     # D4-49: a camp's fire 1 a night; a fire in the open 2 (calibrate)
    "land_blind": 0.25,                                                  # D4-50: share with no eye for how bare a place is (calibrate)
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
    "ground": {"wet": 0.75, "hill": 0.6},                                # D2-66: until weather exists; field works bring each to 1.0
    "master_yield": 0.2,                                                 # D2-64: a master farmer's crops yield x1.2
    "seed_selection": 0.85,                                              # D2-65: ripen 15% sooner
    "camping": {"out": [1.5, 2.0, 1.0], "bedroll": [1.35, 1.75, 0.5], "tent": [1.2, 1.4, 0.0], "camp": [1.2, 1.5, 0.0]},
                                                                         # D2-68: food a night, in the cold, the cold's fall (share)
    "farming": {"plot_seed": 16.0, "ratio": 3.0, "break_gain": 1.5, "weed_max": 0.5, "weed_tau": 8.0, "window": 2, "rot": 0.25,
                "fail": [0.05, 0.15], "fallow": 0.40, "grazed": [0.50, 1.15], "manure": [0.35, 1.15], "dung_per_plot": 10.0},
                # D2-59 (16 seed a plot), D4-38 (02l: harvest 3x the seed, +1.5 broken, weeding to +50% on a curve of tau 1.5 small
                # plots = 8 units a plot), D4-39 (soil), D2-53 (failure 5%, 15% the same crop twice); calibrate
    "cattle": {"births": 0.7, "survive": 0.85, "in_milk_share": 0.6, "dung": 20.0, "grass_per_plot": 25.0, "grass_r": 0.32,
               "stray": 0.2, "hungry_milk": 0.7, "starve_nights": 4},
               # 02o (calibrate): births a cow a year, a cow in milk 0.6 of the year, dung for 2 plots a head a year, 2 head a plot of
               # pasture in summer, an unwatched herd strays
    "repair": {"timber": 2},
    "bury": {"soft": 2, "stony": 4, "frozen": 6},                        # D2-96: units of work by the ground and the cold (calibrate)
    "untaught": 0.5,                                                     # D2-93: an untaught try works half as well (calibrate)
}

# ---------------------------------------------------------------------------------------------------- the environment (37.2's spec)
# The day's weather by spell (environment/scheduler.md, D2-69, D2-99; calibrate): the chances of each kind of day within a spell.
# A spell comes from the world's spec (`spells`: [{kind, from, to}], days counted from 1); otherwise `normal`. Rain falls as snow in
# winter and on cold days. Each kind's effect on the senses (environment/visibility.md, D2-99) and whether it wets what lies out.
WEATHER = {
    "clear": {"sight": 1.0, "sound": 1.0, "wet": False, "words": "a clear day"},
    "rain": {"sight": 0.8, "sound": 0.7, "wet": True, "words": "rain all day"},
    "heavy rain": {"sight": 0.6, "sound": 0.5, "wet": True, "words": "heavy rain, the ground running with water"},
    "fog": {"sight": 0.3, "sound": 1.0, "wet": False, "words": "a thick fog lying on the land"},
    "snow": {"sight": 0.5, "sound": 0.7, "wet": True, "words": "snow falling"},
    "gale": {"sight": 0.9, "sound": 0.5, "wet": False, "words": "a gale tearing at the roofs", "loud": "loud"},
}
SPELLS = {
    "normal": {"clear": 0.55, "rain": 0.25, "heavy rain": 0.05, "fog": 0.10, "gale": 0.05},
    "wet": {"clear": 0.20, "rain": 0.45, "heavy rain": 0.20, "fog": 0.15},
    "dry": {"clear": 0.85, "rain": 0.03, "fog": 0.07, "gale": 0.05},
    "cold snap": {"clear": 0.50, "fog": 0.15, "snow": 0.30, "gale": 0.05},
    "storm": {"clear": 0.05, "rain": 0.25, "heavy rain": 0.40, "gale": 0.30},
}
ENV = {
    "night": {"sight": 0.1, "moon": 0.25, "sound": 1.2},            # D2-99: light only for night events
    "snow_melt": 3,                                                 # snow lies until three days without frost
    "snow_ground": 0.5,                                             # things on the ground under lying snow
    "crop_high": 0.5,                                               # a grain crop standing high: that field's sight
    "crop_high_from": 0.6,                                          # ... from this share of its growing time until reaped
    "smoke": 0.7,                                                   # a parcel with smoke that day
    "felled": {"below": 0.3, "sight": 0.8},                         # a wood felled below this share of its timber is open ground
    "smoke_tags": ["smithing"], "smoke_techs": ["charcoal", "smelt", "dry meat"],
    "mask": {"very": 0.3, "loud": 0.6},                             # D2-100: quieter sounds near something very loud, or loud
    "loud_kinds": {"fight": "very", "raid": "very", "threat": "very"},
    "loud_tags": {"smithing": "loud"}, "loud_techs": {"mill": "loud", "water mill": "loud", "grind": "loud"},
    "inside_sound": 0.5,                                            # walls
    "ford_high_after": 2,                                           # a ford is high for 2 days after heavy rain (world/roads.md)
}

# ------------------------------------------------------------------------------------ things at a spot and noticing them (D2-85)
# Own conspicuousness (information/noticing.md; calibrate); hiding multiplies it (taught, untaught).
THINGS = {
    "body": 0.9, "body_built": 1.0, "heap": 0.9, "heap_min": 10, "pack": 0.4, "camp": 0.7, "trace": 0.3,
    "hidden": {"under brush": [0.2, 0.4], "buried": [0.03, 0.06]},
    "body_days": 10,                                                # "dead some days", then bones to the season's end
    "rot_after": 2,                                                 # a body unburied this many days smells of rot
}
# Fences round a parcel (livestock.md, D2-130; calibrate): what a build takes for a parcel of size s (x the square root of s), the chance a
# day a herd gets through by its level (whole, gappy; down is no fence), and its upkeep: a wood fence loses a level each season unless
# a quarter of the build's work is spent mending it; a stone wall keeps.
FENCES = {
    "wood": {"inputs": {"timber": 4.0}, "units": 10.0, "through": {2: 0.3, 1: 0.6}, "decays": True, "mend": 0.25,
             "words": ("fence", "a wattle fence")},
    "stone": {"inputs": {"stone": 8.0}, "units": 20.0, "through": {2: 0.05, 1: 0.2}, "decays": False, "mend": 0.25, "led": "wall",
              "words": ("wall", "a dry-stone wall")},
}

# Herds that are not held (livestock.md: D2-117, D2-123, D2-124, D2-128, D2-131; calibrate where the spec says so).
HERDS = {
    "steps": {"fed": 1, "drawn": 8},             # a day: a fed herd on good pasture 0 to 1 steps; hungry or drawn up to 8 (D2-123)
    "good_grass": 0.3,                           # grazing above this share of the pasture's best counts as good
    "draw": {"ripe": 1.0, "water": 0.3},         # beyond the food a parcel offers: a ripe crop's pull, water when hungry
    "trample": 0.01,                             # of the standing crop, a head a day
    "onto_road": 0.1,                            # a step from a parcel where a road leaves
    "own": 0.95,                                 # a herd's own conspicuousness (information/noticing.md)
    "road": {"die": 0.15, "die_winter": 0.3, "gone": 0.15, "search": 5.0},   # D2-124, D2-125
    "capacity": {"drover": 10, "herder": 30, "unherded": 6},                 # D2-128
    "split": {"under": 0.01, "over": 0.1, "max": 0.6},                       # D2-128
    "share": {"centre": 0.25, "sd": 1.0, "max": 0.5},                        # D2-131: a quarter x 2^z, z Laplace (sd 1 doubling)
    "call": {"share": 0.25, "head": 3},          # a split while driving calls a drover who notices it, if this big (D2-127)
}

# The parcel graph (world/parcel_graph.md; D2-114 to D2-116): heights in words; the fittings that strike an arriving eye; the overview's
# length.
LAYOUT = {
    "height": ("down by the water", "on the valley floor", "on the slope", "up on the hilltop"),
    "seen": {"water wheel": "a water mill", "millstones": "a mill", "anvil": "a smithy", "oven": "a bake oven", "granary": "a granary"},
    "overview": (3, 5),
}

NOTICING = {
    # presence: where the observer was and what it did, by what its work draws on (D2-85); passing through 0.3, next door 0.1 (D2-115)
    "presence": {"game": 1.0, "plants": 0.7, "herd": 0.5, "work": 0.5, "about": 0.5, "crossing": 0.3, "next door": 0.1,
                 "elsewhere": 0.05, "road": 1.0},
    "next_door_min": 0.5,                                           # only things this conspicuous are seen from next door
    "elsewhere_min": 0.8,                                           # only things this conspicuous are seen from elsewhere at the node
    "attention": {"place": 3.0, "search": 5.0},
    "eye": {"none": 0.5, "ordinary": 1.0, "keen": 3.0},             # D2-91 on things
    "eye_bare": {"none": 0.0, "ordinary": 1.0, "keen": 2.0},        # D4-50 on how bare a place is (none: only by failing)
    "eye_keen": 0.15,                                               # the share born keen (the share with none is `land_blind`)
    "eye_practice": {"techs": ["hunt", "forage"], "find": 5.0, "steps": [30.0, 120.0]},   # units of roaming work (and finds) to rise
}

# ---------------------------------------------------------------------------------------------- fuse events (conflict/fuse_events.md)
# Each kind: its sense, who can detect it and with what chance, how long the fuse is by the building's structure (acts in the call),
# the choices offered, and what happens with no call. Road kinds (meetings, finds, crossings) are added by the roads package.
FUSE = {
    "raid": {"sense": "sound", "label": "a break-in",
             "detect": {"watcher": 0.9, "dog": 0.6, "inside": {"wattle": 0.3, "timber": 0.3, "stone": 0.5, "camp": 0.3},
                        "neighbour": 0.15},
             "acts": {"camp": 0, "wattle": 0, "timber": 1, "stone": 3},     # hut: none; timber: 1; stone: up to 3 (D2-81)
             "riders": {"detect": 0.5, "acts": 1},                          # D2-83
             "choices": ["defend", "flee", "hand over", "alarm", "stay"],
             "also": ["move", "take", "give"]},
}

# ---------------------------------------------------------------------------------------------------------- roads (world/roads.md)
# Terrain of a road's stretches (D2-104): sight and sound (environment/visibility.md) and the chance two parties on it meet (D2-110).
TERRAIN = {
    "plain": {"sight": 1.0, "sound": 1.0, "meet": 0.6}, "farmland": {"sight": 1.0, "sound": 1.0, "meet": 0.9},
    "woodland": {"sight": 0.35, "sound": 0.7, "meet": 0.7}, "marsh": {"sight": 0.6, "sound": 1.0, "meet": 0.6},
    "hills": {"sight": 0.5, "sound": 0.9, "meet": 0.6}, "mountain": {"sight": 0.5, "sound": 0.9, "meet": 0.6},
    "river valley": {"sight": 1.0, "sound": 1.0, "meet": 0.8},
}
# Landmarks (D2-107, D2-109): what each is, the trouble it can give (`challenge`: when, the default, what crossing anyway costs), the
# chance parties meet there, and good places' effect on a traveller. New kinds are rows here and, for a new kind of trouble, one
# function in roads.CHALLENGES.
LANDMARKS = {
    "ford": {"words": "a ford", "meet": 0.95, "challenge": "high", "default": "wait",
             "push": {"cart_loss": [0.3, 0.2], "herd_loss": 0.05, "foot": "soaked"}},
    "bridge": {"words": "a bridge", "meet": 0.95, "challenge": "down", "default": "go round"},
    "pass": {"words": "a pass", "meet": 0.95, "challenge": "snowed", "default": "turn back", "cold_night": True,
             "push": {"death": 0.1}},
    "narrows": {"words": "a narrows", "meet": 0.95, "sight": 0.2},
    "spring": {"words": "a spring", "meet": 0.8},
    "meadow": {"words": "a meadow by the road", "good": True, "seasons": ["summer", "autumn"]},
    "fruit trees": {"words": "wild fruit trees", "good": True, "seasons": ["autumn"]},
    "hollow": {"words": "a sheltered hollow", "good": True, "seasons": ["spring", "summer", "autumn", "winter"]},
}
ROADS = {
    "experience": 5.0,                      # crossings of a landmark that halve one's trouble there (D2-106)
    "call": {"death": 0.05, "loss": 0.5, "minor": 0.1},   # the thresholds for an urgent call (D2-105)
    "good": {"fed": 1.0, "gather": [1.0, 2.0], "known": 2.0, "camp": 1.2},   # D2-109
    "flee": 0.5,
    "waves": 3,                             # a meeting's conversation (D2-110)
    "notices": 5,                           # "On the way" lines on arrival (D2-97)
    "trace_days": {"tracks": 3, "ashes": 10, "ruts": 60},   # D2-88
    # hidden ways (D2-90, D2-92, D2-98): a hidden end shows only while its parcel's sight is this or less; its own conspicuousness, and
    # how much each party passing wears it; open land (or a wood felled below `felled` of its standing timber) shows it at `exposed`;
    # unused it grows back over about a season in forest or scrub; worn to `exposed` it is a path everyone at the node knows
    "hidden": {"hides": 0.5, "own": 0.03, "wear": 0.05, "exposed": 0.8, "regrows": ["forest", "scrub"]},
    "meet_landmark": 3.0,                   # crossing parties meet three times likelier on a stretch with a landmark (D2-121)
    "terrain": "farmland",                  # every road's terrain unless its world gives one (D2-122: a farm track)
}
FUSE.update({
    "meeting": {"sense": "sight", "label": "a meeting on the road", "acts": {"road": 3},
                "choices": ["go on", "turn back", "change course", "attack", "flee"], "also": ["give", "accept"]},
    "find": {"sense": "sight", "label": "something lying by the road", "acts": {"road": 2},
             "choices": ["take", "bury", "go on"], "also": []},
    "crossing": {"sense": "sight", "label": "trouble on the road", "acts": {"road": 1},
                 "choices": ["push on", "wait", "turn back", "go round"], "also": []},
    # a herd found loose on the road, and a group breaking off a herd one drives (livestock.md: D2-124, D2-127)
    "herd": {"sense": "sight", "label": "beasts loose on the road", "acts": {"road": 2},
             "choices": ["drive on", "drive back", "accompany", "leave"], "also": []},
    "split": {"sense": "sight", "label": "beasts breaking away", "acts": {"road": 1}, "choices": ["go after them", "let them go"], "also": []},
})
# Travel's choices at departure (D2-105, D2-109, D2-113) are modifiers known to all.
TECHNIQUES.update({
    "on trouble": {"verb": "modifier", "label": "what to do if the road gives trouble", "basic": True, "modifies": ["travel"],
                   "key": "on trouble", "value": "*", "changes": {}, "units": 0, "gives": "", "tags": ["travel"],
                   "values": ["push on", "wait", "turn back", "go round"]},
    "stop at": {"verb": "modifier", "label": "stopping at a good place one knows on the way", "basic": True, "modifies": ["travel"],
                "key": "stop at", "value": "*", "changes": {}, "units": 0, "gives": "", "tags": ["travel"]},
    "meeting": {"verb": "modifier", "label": "whether to stop for others met on the road", "basic": True, "modifies": ["travel"],
                "key": "meeting", "value": "*", "changes": {}, "units": 0, "gives": "", "tags": ["travel"],
                "values": ["stop", "pass by"]},                                                                      # D4-51
    "gather on the way": {"verb": "modifier", "label": "gathering at good places one passes", "basic": True, "modifies": ["travel"],
                          "key": "gather", "value": "*", "changes": {}, "units": 0, "gives": "", "tags": ["travel"]},
    "searching": {"verb": "modifier", "label": "searching the road for a herd or a person", "basic": True, "modifies": ["travel"],
                  "key": "searching", "value": "*", "changes": {}, "units": 0, "gives": "", "tags": ["travel", "animals"]},   # D2-125
})
MODIFIERS = {t for t, d in TECHNIQUES.items() if d.get("modifies")}
