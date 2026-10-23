"""The world's data: goods, cover types, techniques, what things give off, and physics. Everything here is a table, so the world grows
by adding rows (D4-24), not code.

ITEMS       name -> {weight, food (value as a meal, 0: not eaten), spoil (share lost a night in hand; x house_spoil in a house)}
COVERS      cover type -> {gather (methods allowed here), work, build (lots per size), risks, becomes, ambient (what it gives off)}
TECHNIQUES  name -> {verb, what (the object agents name), label, needs: {inputs, tools, at (cover | fitting | house), season},
            units, gives, basic (everyone knows it), tags (what it bears on, for relevance)}
PHYSICS     the numbers of the day and the night
"""
from __future__ import annotations

ITEMS = {
    "grain": {"weight": 1, "food": 0.5, "spoil": 0.0},
    "bread": {"weight": 1, "food": 1.0, "spoil": 0.10},
    "pottage": {"weight": 1, "food": 1.0, "spoil": 0.30},
    "greens": {"weight": 1, "food": 1.0, "spoil": 0.25},
    "meat": {"weight": 1, "food": 1.0, "spoil": 0.20},
    "fish": {"weight": 1, "food": 1.0, "spoil": 0.30},
    "timber": {"weight": 2, "food": 0.0, "spoil": 0.0},
    "clay": {"weight": 2, "food": 0.0, "spoil": 0.0},
    "withies": {"weight": 1, "food": 0.0, "spoil": 0.0},
    "pot": {"weight": 1, "food": 0.0, "spoil": 0.0},
    "basket": {"weight": 1, "food": 0.0, "spoil": 0.0},
    "line": {"weight": 0, "food": 0.0, "spoil": 0.0},
    "club": {"weight": 1, "food": 0.0, "spoil": 0.0},
    "knife": {"weight": 0, "food": 0.0, "spoil": 0.0},
    "axe": {"weight": 1, "food": 0.0, "spoil": 0.0},
    "sickle": {"weight": 1, "food": 0.0, "spoil": 0.0},
}
EDIBLE = tuple(i for i, v in ITEMS.items() if v["food"] > 0)
WEAPONS = {"axe": 3.0, "club": 2.0, "knife": 1.5}

COVERS = {
    "forest": {"gather": ["forage", "hunt", "fell"], "work": [], "lots": 0, "risks": ["fire", "wolves"],
               "becomes": "field, when felled and cleared",
               "ambient": [("sound", "birdsong and the creak of trees from {name}", 0.2),
                           ("smell", "leaf mould on the air from {name}", 0.15)]},
    "field": {"gather": ["glean (once reaped)"], "work": ["reap (when ripe, with a sickle)"], "lots": 0, "risks": ["flood if low"], "becomes": "scrub if left; ground to build on",
              "ambient": [("sight", "{name} stretching out beyond the houses", 0.1)]},
    "pasture": {"gather": ["forage"], "work": [], "lots": 0, "risks": ["drought", "fire when dry"], "becomes": "field, if ploughed",
                "ambient": [("sound", "the village cattle lowing on {name}", 0.35), ("smell", "dung and trodden grass from {name}", 0.15)]},
    "meadow": {"gather": ["forage", "cut withies"], "work": [], "lots": 0, "risks": ["flood"], "becomes": "field, if drained",
               "ambient": [("sound", "insects in the long grass of {name}", 0.15)]},
    "water": {"gather": ["fish", "dig clay"], "work": [], "lots": 0, "risks": ["flood", "ice"], "becomes": "",
              "ambient": [("sound", "the brook running over stones", 0.3)]},
    "built": {"gather": [], "work": [], "lots": 6, "risks": ["fire"], "becomes": "",
              "ambient": [("sound", "voices and work about the houses", 0.2)]},
    "scrub": {"gather": ["forage"], "work": [], "lots": 4, "risks": ["fire"], "becomes": "forest if left; field if cleared",
              "ambient": []},
}

# verb, the object agents name, and what it needs. "at": a cover type, "house" (one's own house, its hearth), or a fitting name.
TECHNIQUES = {
    "forage": {"verb": "gather", "label": "foraging (greens, roots, berries)", "basic": True, "needs": {"at": ["forest", "meadow", "pasture", "scrub"]},
               "units": 1, "gives": "greens", "tags": ["food"]},
    "cut withies": {"verb": "gather", "label": "cutting withies", "basic": True, "needs": {"at": ["meadow"]}, "units": 1, "gives": "withies",
                    "tags": ["craft"]},
    "dig clay": {"verb": "gather", "label": "digging clay from the bank", "basic": True, "needs": {"at": ["water"]}, "units": 1,
                 "gives": "clay", "tags": ["craft", "pottery"]},
    "glean": {"verb": "gather", "label": "gleaning a reaped field", "basic": True, "needs": {"at": ["field"], "crop": "reaped"}, "units": 1, "gives": "grain",
              "tags": ["food", "farming"]},
    "hunt": {"verb": "gather", "label": "hunting game", "needs": {"at": ["forest"]}, "units": 2, "gives": "meat", "tags": ["food", "hunting", "animals"]},
    "fell": {"verb": "gather", "label": "felling timber", "needs": {"at": ["forest"], "tools": ["axe"]}, "units": 2, "gives": "timber",
             "tags": ["timber", "woodland"]},
    "fish": {"verb": "gather", "label": "fishing the brook", "needs": {"at": ["water"], "tools": ["line"]}, "units": 2, "gives": "fish",
             "tags": ["food", "water"]},
    "reap": {"verb": "work", "label": "reaping grain", "needs": {"at": ["field"], "tools": ["sickle"], "crop": "ripe"}, "units": 2,
             "gives": "grain", "tags": ["food", "farming", "harvest"]},
    "bread": {"verb": "make", "label": "baking bread", "needs": {"inputs": {"grain": 2, "timber": 0.5}, "at": ["house"]}, "units": 1,
              "gives": {"bread": 2}, "tags": ["food", "cooking"]},
    "pottage": {"verb": "make", "label": "cooking pottage", "needs": {"inputs": {"grain": 1, "greens": 1, "timber": 0.5}, "tools": ["pot"],
                "at": ["house"]}, "units": 1, "gives": {"pottage": 3}, "tags": ["food", "cooking"]},
    "pot": {"verb": "make", "label": "firing pots", "needs": {"inputs": {"clay": 2, "timber": 1}, "at": ["firing pit"]}, "units": 2,
            "gives": {"pot": 1}, "tags": ["craft", "pottery"]},
    "basket": {"verb": "make", "label": "weaving baskets", "needs": {"inputs": {"withies": 3}}, "units": 2, "gives": {"basket": 1},
               "tags": ["craft"]},
    "line": {"verb": "make", "label": "twisting a fishing line", "needs": {"inputs": {"withies": 1}}, "units": 1, "gives": {"line": 1},
             "tags": ["craft", "water"]},
    "club": {"verb": "make", "label": "shaping a club", "basic": True, "needs": {"inputs": {"timber": 2}}, "units": 1,
             "gives": {"club": 1}, "tags": ["weapons"]},
    "firing pit": {"verb": "build", "label": "building a firing pit", "needs": {"inputs": {"clay": 3, "timber": 2}, "at": ["built"]},
                   "units": 3, "gives": "firing pit", "tags": ["craft", "pottery", "building"]},
    "repair": {"verb": "work", "label": "repairing a house", "basic": True, "needs": {"inputs": {"timber": 2}, "at": ["house"]}, "units": 2,
               "gives": "repair", "tags": ["building", "shelter"]},
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
    "forage": {"yield": 2.0, "refuge": 0.1},
    "hunt": {"p": 0.35, "food": [2, 6]},
    "fish": {"p": 0.5, "food": [1, 3]},
    "fell": {"timber": 3.0},
    "reap": {"grain": 6.0},
    "glean": {"grain": 0.7},
    "clay": 2.0,
    "withies": 3.0,
    "combat": {"base": [0.5, 1.5], "guard": 2.0, "asleep": 0.5, "units": 3, "raid_share": 0.5, "counter": 0.3},
    "teach": {"units_teacher": 2, "units_learner": 2, "skill_share": 0.3},
    "watch": {"units": 4},
    "notes": {"max": 8, "words": 150, "open": 2},
    "felt_watched": 0.3,
    "glimpse": 3,
}
