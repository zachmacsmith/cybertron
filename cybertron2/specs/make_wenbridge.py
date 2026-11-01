"""Wenbridge (review 38.46; Zach approved the design, 2 Nov): a river village made to test whether people build. Writes
cybertron2/specs/wenbridge.yaml.

    python cybertron2/specs/make_wenbridge.py
"""
import yaml

K = lambda *t: {x: {"level": "known", "skill": 1.0} for x in t}
FARM = K("sow", "reap", "hoe", "weed", "select seed")


def person(hh, sex, born, partner, rel, model, mem, aim, holdings, knows):
    return {"household": hh, "born": born, "stage": "adult", "sex": sex, "relations": rel, "memories": mem, "knows": knows,
            "aware_of": {}, "holdings": holdings, "concerns": ["food", "shelter", "family", "building"], "parents": [],
            "partner": partner, "model": model, "born_line": hh, "aim": aim}


def world():
    w = {"name": "wenbridge", "seed": 91, "days": 30, "calendar": {"season": "summer", "day": 3, "season_days": 8},
         "children": {"on": True, "dial": "low"}, "lifespan": 96, "view": "beliefs", "evening": True, "tags": True, "ages": True,
         "llm": {"week_stop": 0.9}, "cold_days": [], "incidents": [], "herds": {}}
    w["nodes"] = {
        "wenbridge": {"name": "Wenbridge", "parcels": {
            "wb_green": {"name": "the Green", "cover": "built", "size": 1, "side": "centre", "height": 1,
                         "text": "a trodden green with the village houses close round it", "adj": ["wb_field", "wb_bank", "wb_garth", "wb_hall"]},
            "wb_hall": {"name": "the Hall Garth", "cover": "built", "size": 2, "side": "north", "height": 2, "holder": "Ardern",
                        "text": "a walled yard before the lord's stone hall", "adj": ["wb_mead"]},
            "wb_garth": {"name": "Mill Garth", "cover": "built", "size": 1, "side": "west", "height": 0, "holder": "Ardern",
                         "text": "the mill yard on the river bank", "adj": ["wb_wen"]},
            "wb_wen": {"name": "the Wen", "cover": "water", "size": 1, "side": "west", "height": 0, "text": "a broad river, quick at the weir"},
            "wb_field": {"name": "the Long Field", "cover": "field", "size": 4, "side": "south", "height": 1, "holder": "Hearne",
                         "fertility": 1.1, "text": "the village's one field, in strips", "adj": ["wb_mead"],
                         "state": {"crop": {"kind": "barley", "left": 200, "ripe_day": 5}, "last_crop": "beans"}},
            "wb_mead": {"name": "Mill Mead", "cover": "meadow", "size": 3, "side": "east", "height": 1, "holder": "Ardern",
                        "text": "the lord's hay meadow", "state": {"plants": {"K": 4, "S": 4, "r": 0.3}, "grass": {"K": 80, "S": 80, "r": 0.32}}},
            "wb_bank": {"name": "Gorse Bank", "cover": "scrub", "size": 2, "side": "east", "height": 2,
                        "text": "a gorse slope above the village that nobody holds", "adj": ["wb_quarry"],
                        "state": {"wood": {"kind": "scrub"}, "plants": {"K": 3, "S": 3, "r": 0.3}}},
            "wb_quarry": {"name": "the Quarry", "cover": "rock", "size": 1, "side": "east", "height": 3, "holder": "Mason",
                          "text": "a grey stone face worked by the Masons", "state": {"quarry": {"K": 200, "S": 200, "r": 0.0}}}}},
        "holm": {"name": "Holm Wood", "parcels": {
            "hm_wood": {"name": "the Holm", "cover": "forest", "size": 4, "side": "centre", "height": 2, "text": "old oak and ash",
                        "state": {"wood": {"kind": "old forest"}, "game": {"K": 14, "S": 12, "r": 0.25}, "plants": {"K": 6, "S": 6, "r": 0.3}}},
            "hm_glade": {"name": "Holm Glade", "cover": "meadow", "size": 2, "side": "south", "height": 1, "text": "a clearing",
                         "adj": ["hm_wood"], "state": {"plants": {"K": 4, "S": 4, "r": 0.3}, "grass": {"K": 50, "S": 50, "r": 0.3}}}}},
        "copperhill": {"name": "Copperhill", "unexplored": True, "parcels": {
            "ch_scar": {"name": "the Green Scar", "cover": "rock", "size": 2, "side": "centre", "height": 3,
                        "text": "a cliff stained green, copper in the rock"}}}}
    w["roads"] = [["wenbridge", "holm", 1, {"terrain": "woodland", "way": "the track east into the oaks"}],
                  ["holm", "copperhill", 1, {"terrain": "hills", "way": "a stony path north up the hills"}]]
    w["buildings"] = {
        "ardern_hall": {"name": "the Ardern Hall", "parcel": "wb_hall", "household": "Ardern", "structure": "stone",
                        "rooms": [{"kind": "hall"}], "fittings": {"beds": 3, "hearth": 1, "bins": 2},
                        "stock": {"grain": 120, "beans": 30, "timber": 20, "firewood": 40, "copper": 2, "coin": 0}},
        "mill_house": {"name": "the Mill House", "parcel": "wb_garth", "household": "Ardern", "structure": "timber",
                       "rooms": [{"kind": "medium room"}], "fittings": {"millstones": 1},
                       "fitting_work": {"water wheel": {"n": 1, "units_left": 150}}, "stock": {}},
        "wright_house": {"name": "Wright's House", "parcel": "wb_green", "household": "Wright", "structure": "timber",
                         "rooms": [{"kind": "medium room"}], "fittings": {"beds": 2, "hearth": 1, "bins": 1},
                         "stock": {"grain": 10, "timber": 10, "firewood": 20}},
        "hearne_hut": {"name": "the Hearne hut", "parcel": "wb_green", "household": "Hearne", "structure": "wattle",
                       "rooms": [{"kind": "small room"}], "fittings": {"beds": 3, "hearth": 1, "bins": 1},
                       "stock": {"grain": 20, "beans": 6, "straw": 4, "firewood": 20}},
        "mason_cottage": {"name": "the Masons' cottage", "parcel": "wb_green", "household": "Mason", "structure": "wattle", "condition": 1,
                          "rooms": [{"kind": "small room"}], "fittings": {"beds": 2, "fire ring": 1}, "stock": {"grain": 8, "stone": 10}},
        "new_camp": {"name": "the newcomers' camp", "parcel": "wb_bank", "household": "Newcome", "structure": "camp", "size": 4,
                     "fittings": {"beds": 4, "fire ring": 1}, "lasts_until": 10, "stock": {"firewood": 6, "beans": 4}}}
    w["claims"] = []
    A = {"Hugh": "your wife", "Odo": "your steward"}
    agents = {
        "Hugh": person("Ardern", "m", -55, "Alys", {"Alys": "your wife", "Odo": "your steward"}, "claude-opus-5-5",
                       ["The Arderns have held Wenbridge for four lifetimes; the hall is the only stone house in the valley.",
                        "Your father began the mill and died before its wheel was hung: the millstones are in, the wheel half made.",
                        "Without the wheel the village grinds by hand and eats meal, not bread."],
                       "Finish the mill, so Wenbridge grinds its own bread, and raise the Ardern hall into the grandest house in the valley, "
                       "its deeds cut in stone over the door.", {"coin": 30, "crude tool": 1}, K("small room")),
        "Alys": person("Ardern", "f", -50, "Hugh", {"Hugh": "your husband", "Odo": "your husband's steward"}, "claude-sonnet-5-5",
                       ["You came to the Ardern hall as a bride; it is cold and too big for three."],
                       "See the Ardern hall full of children and warm through the winter.", {"coin": 4}, K("small room")),
        "Odo": person("Ardern", "m", -60, None, {"Hugh": "your lord", "Alys": "your lord's wife"}, "claude-haiku-5-5",
                      ["You have served the Arderns all your life and keep their stores."],
                      "Serve the Arderns well and keep their stores full.", {"crude tool": 1}, K("small room", "sow", "reap")),
        "Wat": person("Mason", "m", -48, "Joan", {"Joan": "your wife"}, "claude-opus-5-5",
                      ["You are the only mason in the valley: hearths, ovens, cellars, vaults and stone walls are your craft.",
                       "Your cottage is wattle and leaking; the cobbler's son has a better roof than the mason."],
                      "Build a stone house of your own, the first in Wenbridge outside the hall, and be paid fairly for your craft.",
                      {"crude tool": 2, "coin": 3}, K("hearth", "oven", "cellar", "vault", "quarry", "small room", "fire ring")),
        "Joan": person("Mason", "f", -45, "Wat", {"Wat": "your husband"}, "claude-sonnet-5-5",
                       ["The roof drips on the beds when it rains."], "A dry house and children to fill it.", {}, K("small room")),
        "Piers": person("Wright", "m", -44, None, {}, "claude-opus-5-5",
                        ["You are the only carpenter in the valley: rooms of timber, halls, mill wheels.",
                         "You helped the old lord's wright frame the mill house; you know how the wheel should go."],
                        "Be the man who built the Wenbridge mill, and take a wife.", {"crude tool": 2, "coin": 6},
                        K("medium room", "hall", "water wheel", "small room", "granary", "bins", "beds")),
        "Tom": person("Hearne", "m", -50, "Ellen", {"Ellen": "your wife", "Will": "your son", "Kit": "your son"}, "claude-sonnet-5-5",
                      ["The Hearnes farm the Long Field; the hut was built for two and holds four."],
                      "Get the harvest in and kept, and make room for the children still to come.", {"crude tool": 1}, FARM),
        "Ellen": person("Hearne", "f", -47, "Tom", {"Tom": "your husband", "Will": "your son", "Kit": "your son"}, "claude-sonnet-5-5",
                        ["Two of us sleep on the floor; there is no straw to spare for another bed until harvest."],
                        "Room enough for the family, and more children.", {}, FARM),
        "Will": person("Hearne", "m", -20, None, {"Tom": "your father", "Ellen": "your mother", "Kit": "your brother"}, "claude-haiku-5-5",
                       ["You sleep on the floor by the hearth."], "Help the family and one day have a house of your own.", {}, FARM),
        "Kit": person("Hearne", "m", -19, None, {"Tom": "your father", "Ellen": "your mother", "Will": "your brother"}, "claude-haiku-5-5",
                      ["You sleep on the floor by the hearth."], "Help the family and learn a trade.", {}, FARM),
        "Rob": person("Newcome", "m", -40, "Mary", {"Mary": "your wife"}, "claude-sonnet-5-5",
                      ["You and Mary came to Wenbridge this summer from a burned-out farm, with tools and a little grain.",
                       "Your camp on Gorse Bank will not stand into the winter."],
                      "Make a home in Wenbridge before winter, and ground of your own.", {"crude tool": 1, "grain": 8},
                      K("small room", "sow", "reap", "hoe", "weed")),
        "Mary": person("Newcome", "f", -38, "Rob", {"Rob": "your husband"}, "claude-haiku-5-5",
                       ["Gorse Bank is nobody's; the Green is full of houses."], "A roof and a hearth of your own before the snow.",
                       {"grain": 8, "beans": 2}, K("small room", "sow", "reap")),
    }
    for a in agents.values():                                                  # the youths are youths
        if a["born"] > -36:
            a["stage"] = "youth"
    w["agents"] = agents
    w["customs"] = [{"text": "In Wenbridge the lord holds the mill and the meadow, the Masons the quarry, the Hearnes the Long Field; "
                             "Gorse Bank is nobody's, and whoever builds on it holds what they build.", "nodes": "all"},
                    {"text": "Work is paid in grain or coin, as agreed before it is done.", "nodes": "all"}]
    return w


if __name__ == "__main__":
    with open("cybertron2/specs/wenbridge.yaml", "w") as f:
        f.write("# Written by cybertron2/specs/make_wenbridge.py (review 38.46, approved by Zach 2 Nov).\n")
        yaml.safe_dump(world(), f, sort_keys=False, width=140, allow_unicode=True)
    print("wrote cybertron2/specs/wenbridge.yaml")
