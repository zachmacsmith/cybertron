"""The world's data: goods, cover types, techniques, what things give off, and physics. Everything here is a table, so the world grows
by adding rows (D4-24), not code.

ITEMS       name -> {weight, food (value as a meal, 0: not eaten), spoil (share lost a night in hand; x house_spoil in a house)}
COVERS      cover type -> {gather (methods allowed here), work, build (lots per size), risks, becomes, ambient (what it gives off)}
TECHNIQUES  name -> {verb, what (the object agents name), label, needs: {inputs, tools, at (cover | fitting | house), season},
            units, gives, basic (everyone knows it), tags (what it bears on, for relevance)}
PHYSICS     the numbers of the day and the night
"""
from __future__ import annotations

# Goods, techniques and tools follow the decided economy (spec/economy: D2-23 tools, D2-41 meat, D2-42 milk, D2-43 the basic set,
# D2-44 bread) with recipes.md's numbers (a proposal: "calibrate"). Simplifications for one node: tools do not wear yet; no traps
# (they need hides); the quern is in every house.
ITEMS = {
    "grain": {"weight": 1, "food": 1.0, "spoil": 0.0},        # eaten as porridge at a hearth (D2-44)
    "flour": {"weight": 1, "food": 0.0, "spoil": 0.0},
    "bread": {"weight": 1, "food": 1.1, "spoil": 0.05},       # 11 from 10 grain, eaten anywhere, keeps (D2-44)
    "wild food": {"weight": 1, "food": 1.0, "spoil": 0.15},
    "meat": {"weight": 1, "food": 1.5, "spoil": 0.30},        # dense, spoils fast fresh (D2-41)
    "milk": {"weight": 1, "food": 0.5, "spoil": 1.0},         # spoils within the day (D2-42)
    "timber": {"weight": 2, "food": 0.0, "spoil": 0.0},
    "crude tool": {"weight": 1, "food": 0.0, "spoil": 0.0},
    "copper tool": {"weight": 1, "food": 0.0, "spoil": 0.0},
    "crude weapon": {"weight": 1, "food": 0.0, "spoil": 0.0},
}
EDIBLE = tuple(i for i, v in ITEMS.items() if v["food"] > 0)
WEAPONS = {"crude weapon": 2.0}
TOOLS = ("copper tool", "crude tool")                          # best first
TOOL_MULT = {                                                   # recipes.md §9: bare hands, crude, copper
    "fell": {"bare": 0.25, "crude tool": 1.0, "copper tool": 2.0},
    "reap": {"bare": 0.6, "crude tool": 1.0, "copper tool": 1.5},
}

COVERS = {
    "forest": {"gather": ["forage", "hunt", "fell"], "work": [], "lots": 0, "risks": ["fire", "wolves"],
               "becomes": "field, when felled and cleared",
               "ambient": [("sound", "birdsong and the creak of trees from {name}", 0.2),
                           ("smell", "leaf mould on the air from {name}", 0.15)]},
    "field": {"gather": [], "work": ["reap (when ripe)"], "lots": 0, "risks": ["flood if low"], "becomes": "scrub if left",
              "ambient": [("sight", "{name} stretching out beyond the houses", 0.1)]},
    "pasture": {"gather": ["forage"], "work": ["milk (a cow in milk)"], "lots": 0, "risks": ["drought", "fire when dry"],
                "becomes": "field, if ploughed",
                "ambient": [("sound", "the village cattle lowing on {name}", 0.35), ("smell", "dung and trodden grass from {name}", 0.15)]},
    "meadow": {"gather": ["forage"], "work": [], "lots": 0, "risks": ["flood"], "becomes": "field, if drained",
               "ambient": [("sound", "insects in the long grass of {name}", 0.15)]},
    "water": {"gather": [], "work": [], "lots": 0, "risks": ["flood", "ice"], "becomes": "",
              "ambient": [("sound", "the brook running over stones", 0.3)]},
    "built": {"gather": [], "work": [], "lots": 6, "risks": ["fire"], "becomes": "",
              "ambient": [("sound", "voices and work about the houses", 0.2)]},
    "scrub": {"gather": ["forage"], "work": [], "lots": 4, "risks": ["fire"], "becomes": "forest if left; field if cleared",
              "ambient": []},
}

# verb, the object agents name, and what it needs. "at": a cover type or "house" (one's own house: its hearth and quern).
TECHNIQUES = {
    "forage": {"verb": "gather", "label": "foraging (greens, roots, berries, nuts)", "basic": True,
               "needs": {"at": ["forest", "meadow", "pasture", "scrub"]}, "units": 1, "gives": "wild food", "tags": ["food"]},
    "hunt": {"verb": "gather", "label": "hunting game", "basic": True, "needs": {"at": ["forest"]}, "units": 2, "gives": "meat",
             "tags": ["food", "hunting", "animals"]},
    "fell": {"verb": "gather", "label": "felling timber", "basic": True, "needs": {"at": ["forest"]}, "units": 2, "gives": "timber",
             "tags": ["timber", "woodland"]},
    "reap": {"verb": "work", "label": "reaping grain", "basic": True, "needs": {"at": ["field"], "crop": "ripe"}, "units": 2,
             "gives": "grain", "tags": ["food", "farming", "harvest"]},
    "milk": {"verb": "work", "label": "milking (a cow in milk)", "needs": {"at": ["pasture"], "herd": "in milk"}, "units": 1,
             "gives": "milk", "tags": ["food", "animals"]},
    "grind": {"verb": "make", "label": "grinding flour at a quern", "basic": True, "needs": {"inputs": {"grain": 4}, "at": ["house"]},
              "units": 1, "gives": {"flour": 4}, "tags": ["food", "cooking"]},
    "bread": {"verb": "make", "label": "baking bread", "basic": True, "needs": {"inputs": {"flour": 10, "timber": 1}, "at": ["house"]},
              "units": 1, "gives": {"bread": 11}, "tags": ["food", "cooking"]},
    "crude weapon": {"verb": "make", "label": "making a crude weapon", "basic": True, "needs": {"inputs": {"timber": 1}}, "units": 1,
                     "gives": {"crude weapon": 1}, "tags": ["weapons"]},
    "repair": {"verb": "work", "label": "repairing a house", "basic": True, "needs": {"inputs": {"timber": 2}, "at": ["house"]},
               "units": 2, "gives": "repair", "tags": ["building", "shelter"]},
}
LEVELS = ("aware", "rough", "capable", "known")
LEVEL_WORDS = {"aware": "know of", "rough": "have a rough idea of", "capable": "are capable of", "known": "know"}
TRY = {"rough": {"inputs": 1.7, "chance": 0.5}, "capable": {"inputs": 1.3, "chance": 0.75}, "known": {"inputs": 1.0, "chance": 1.0}}
SKILL_WORDS = ((1.6, "master"), (1.2, "skilled"), (0.8, "competent"), (0.0, "novice"))

PHYSICS = {
    "units": {"summer": 7, "autumn": 6, "winter": 5, "spring": 6},
    "youth_units": 4,
    "elder_units": 5,
    "ration": 1.0,
    "shelter": {"housed": 1.0, "damaged": 1.2, "unsheltered": 1.5},
    "shelter_cold": {"housed": 1.0, "no_fuel": 1.3, "damaged": 1.5, "unsheltered": 2.0},
    "cold_starving": 0.3,
    "fuel": {"normal": 0.5, "cold": 2.0},
    "house_spoil": 0.3,
    "breaks": {"p": 0.02, "cold": 0.08},
    "hunger_yield": {"0": 1.0, "-1": 0.75, "-2": 0.5},
    "frailty": [0.25, 0.55],
    "hazard": {"step": 0.15, "max_rounds": 4},
    "forage": {"yield": 1.2, "refuge": 0.1},
    "hunt": {"p": 0.35, "food": [2, 6]},
    "milk": 3.0,
    "fell": {"timber": 3.0},
    "reap": {"grain": 6.0},
    "combat": {"base": [0.5, 1.5], "guard": 2.0, "asleep": 0.5, "units": 3, "raid_share": 0.5, "counter": 0.3},
    "teach": {"units_teacher": 2, "units_learner": 2, "skill_share": 0.3},
    "watch": {"units": 4},
    "notes": {"max": 8, "words": 150, "open": 2},
    "felt_watched": 0.3,
    "glimpse": 3,
    "messages": {"per_day": 3, "jitter": {0: 37, 1: 37, 2: 18, 3: 8}, "max": 10},   # private messages a day (cybertron 1's DM limit)
    "say_units": 1,                                                                     # a say (public or in a building) takes 1 unit
}
