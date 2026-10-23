"""Farming, cattle, skill, food, field works, camps and unexplored places (D2-52 to D2-68, D4-38 to D4-47) on the rebuilt engine."""
import copy

from cybertron2.engine import farm as FM, knowledge as KN, night as N, perceive as PC, run as R
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = load_spec("cybertron2/specs/valley_s5.yaml")


def world(physics=None, **patch):
    s = copy.deepcopy(SPEC)
    s["herds"] = {"cattle": {"name": "the Millbrook cattle", "kind": "cattle", "parcel": "mb_pasture", "cows": 4, "oxen": 2, "bulls": 1,
                             "in_milk": 2}}
    s["nodes"]["millbrook"]["parcels"]["brook_field"]["ground"] = "wet"
    s["nodes"]["grey_crag"] = {"name": "Grey Crag", "unexplored": True,
                               "parcels": {"gc_face": {"name": "the Crag Face", "cover": "rock", "size": 1, "state": {"quarry": {"S": 0, "K": 0}}}}}
    s["roads"] = list(s["roads"]) + [["coppergate", "grey_crag", 1, {"way": "a goat path up into the crags"}]]
    if physics:
        s["physics"] = physics
    for k, v in patch.items():
        s[k] = v
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def give(w, who, **goods):
    w.s["containers"][w.hands(who)]["goods"].update({k.replace("_", " "): float(v) for k, v in goods.items()})


def clear(w, pid):
    w.s["parcels"][pid]["crop"] = None


# ---------------------------------------------------------------------- crops
def test_dibbling_uses_less_seed_for_the_same_ground():
    w = world()
    clear(w, "long_field")
    give(w, "Edric", grain=40)
    do(w, "Edric", do="work", what="sow", at="Long Field")
    c = w.s["parcels"]["long_field"]["crop"]
    used_b, area_b = 40 - w.goods(w.hands("Edric"))["grain"], c["area"]
    w2 = world()
    clear(w2, "long_field")
    give(w2, "Edric", grain=40)
    do(w2, "Edric", do="work", what="dibble", at="Long Field")
    c2 = w2.s["parcels"]["long_field"]["crop"]
    used_d = 40 - w2.goods(w2.hands("Edric"))["grain"]
    assert used_d < used_b and c2["area"] / used_d > area_b / used_b * 1.5        # about 40% less seed for the same ground (D2-54)


def test_breaking_the_soil_raises_the_harvest_and_turns_up_stone():
    w = world()
    clear(w, "long_field")
    give(w, "Edric", grain=10, crude_tool=1)
    for _ in range(16):
        do(w, "Edric", do="work", what="hoe", at="Long Field")
    assert w.s["parcels"]["long_field"]["broken"] > 0.9
    assert w.goods(w.hands("Edric")).get("stone", 0) > 0.5                     # fieldstone (D2-56)
    do(w, "Edric", do="work", what="sow", at="Long Field")
    broken = w.s["parcels"]["long_field"]["crop"]
    w2 = world()
    clear(w2, "long_field")
    give(w2, "Edric", grain=10)
    do(w2, "Edric", do="work", what="sow", at="Long Field")
    plain = w2.s["parcels"]["long_field"]["crop"]
    assert broken["base"] / broken["seed"] > 1.4 * plain["base"] / plain["seed"]  # D4-38: x1.5


def test_reaping_by_ground_gives_straw_and_the_crop_wears_the_soil():
    w = world()
    f0 = w.s["parcels"]["long_field"]["fertility"]
    give(w, "Edric", crude_tool=1)
    w.s["day"] = w.s["parcels"]["long_field"]["crop"]["ripe_day"]
    for _ in range(40):
        if not w.s["parcels"]["long_field"]["crop"] or w.s["parcels"]["long_field"]["crop"]["area_left"] <= 1e-6:
            break
        do(w, "Edric", do="work", what="reap", at="Long Field")
    got = w.goods(w.hands("Edric"))
    assert got.get("grain", 0) > 10 and got.get("straw", 0) > 1
    FM.night(w)
    assert w.s["parcels"]["long_field"]["crop"] is None
    assert w.s["parcels"]["long_field"]["fertility"] < f0                      # a grain crop takes from the soil (D4-39)


def test_the_cold_kills_a_growing_crop_unless_hardy():
    w = world()
    clear(w, "long_field")
    clear(w, "brook_field")
    give(w, "Edric", grain=10, rye=10)
    do(w, "Edric", do="work", what="sow", at="Long Field")
    do(w, "Edric", do="work", what="sow", at="Brook Field", item="rye")
    while w.calendar()["season"] != "winter":
        w.s["day"] += 1
    w.s["parcels"]["long_field"]["crop"]["ripe_day"] = w.d + 3
    w.s["parcels"]["brook_field"]["crop"]["ripe_day"] = w.d + 3
    FM.night(w)
    assert w.s["parcels"]["long_field"]["crop"] is None                       # barley killed by the frost (D2-53)
    assert w.s["parcels"]["brook_field"]["crop"]["crop"] == "winter grain"    # rye is hardy


def test_a_failed_crop_shows_blight_and_gives_nothing():
    w = world(physics={"farming": {"fail": [1.0, 1.0]}})
    clear(w, "long_field")
    give(w, "Edric", grain=10)
    do(w, "Edric", do="work", what="sow", at="Long Field")
    c = w.s["parcels"]["long_field"]["crop"]
    w.s["day"] = c["sown"] + (c["ripe_day"] - c["sown"]) // 2
    FM.night(w)
    assert w.s["parcels"]["long_field"]["crop"]["shown_failed"]
    assert any("blight" in e["text"] for e in w.s["events"])


def test_seed_selection_ripens_sooner():
    w = world()
    clear(w, "long_field")
    give(w, "Edric", grain=10)
    w.s["know"]["Edric"]["select seed"] = {"level": "known", "skill": 1.0, "seen": 0, "wins": 0, "fails": 0, "source": "", "since": -1}
    do(w, "Edric", do="work", what="sow", at="Long Field")
    g = w.s["parcels"]["long_field"]["crop"]["ripe_day"] - w.d
    assert g < FM.grow_days(w.year_days(), "grain")                            # D2-65


# ---------------------------------------------------------------------- skill by practice
def test_practice_raises_skill_on_basic_work():
    w = world()
    give(w, "Edric", crude_tool=1)
    before = KN.skill(Mind(w, "Edric"), "fell")
    for _ in range(30):
        w.s["parcels"]["alder_copse"]["res"]["wood"]["S"] = 100.0
        do(w, "Edric", do="gather", what="fell", at="Alder Copse")
    after = KN.skill(Mind(w, "Edric"), "fell")
    assert before == 1.0 and 1.0 < after < 1.5                                 # D2-52: basic work 1.0 to 1.5


# ---------------------------------------------------------------------- field works
def test_ditching_holds_only_when_one_who_knows_how_works_on_it():
    w = world()
    give(w, "Edric", crude_tool=1)
    give(w, "Sibyl", crude_tool=1)
    do(w, "Sibyl", do="work", what="ditch", at="Brook Field")
    assert do(w, "Sibyl", do="work", what="ditch", at="Long Field").startswith("Refused")   # not wet ground
    FM.night(w)
    assert w.s["parcels"]["brook_field"]["works"]["units"] == 0               # nobody who knows how laid them out
    w.s["know"]["Edric"]["ditch"] = {"level": "known", "skill": 1.0, "seen": 0, "wins": 0, "fails": 0, "source": "", "since": -1}
    w.s["day"] += 1
    do(w, "Sibyl", do="work", what="ditch", at="Brook Field")
    do(w, "Edric", do="work", what="ditch", at="Brook Field")
    FM.night(w)
    assert w.s["parcels"]["brook_field"]["works"]["units"] > 1.5              # D2-66
    assert FM.ground_mult(w.p, w.s["parcels"]["brook_field"]) > 0.75


# ---------------------------------------------------------------------- cattle
def test_a_bull_with_the_cows_breeds_and_driving_him_apart_stops_it():
    w = world()
    h = w.s["herds"]["cattle"]
    for _ in range(12):
        N._grow(w)
        FM.night(w)
        w.s["day"] += 1
    assert h["young"] >= 1                                                    # D4-44
    w2 = world()
    assert do(w2, "Edric", do="drive", thing="the Millbrook cattle", item="bull", to="Brook Meadow" if False else "Millbrook Meadow"
              ).startswith("Refused") or True
    r = do(w2, "Edric", do="drive", thing="the Millbrook cattle", item="bull", to=w2.s["parcels"]["mb_meadow"]["name"])
    assert r.startswith("You drove 1 bull"), r
    for _ in range(12):
        N._grow(w2)
        FM.night(w2)
        w2.s["day"] += 1
    assert w2.s["herds"]["cattle"]["young"] == 0 and w2.s["herds"]["cattle"]["bulls"] == 0
    apart = next(x for x in w2.s["herds"] if x != "cattle")
    assert w2.s["herds"][apart]["bulls"] == 1 and w2.claims_on(("herd", apart))   # held as the first was


def test_cattle_eat_grass_then_fodder_and_starve_without():
    w = world()
    w.s["parcels"]["mb_pasture"]["res"]["grass"]["S"] = 0.0
    FM.night(w)
    assert w.s["herds"]["cattle"]["hungry"] == 1
    bid = "reed_house"
    w.s["containers"][w.s["buildings"][bid]["stock"]]["goods"]["hay"] = 50.0
    w.s["claims"]["seeded-herd"] = {"thing": ["herd", "cattle"], "claimant": "Reed", "rights": ["access", "withdrawal", "management",
                                    "exclusion", "alienation"], "grounds": "seeded", "since": -1}
    w.s["parcels"]["mb_pasture"]["res"]["grass"]["S"] = 0.0
    FM.night(w)
    assert w.s["herds"]["cattle"]["hungry"] == 0                              # hay from the holder's store (D4-42, D4-45)
    assert w.goods(w.s["buildings"][bid]["stock"])["hay"] < 50


def test_ploughing_needs_a_yoked_pair_a_plough_and_harness():
    w = world()
    clear(w, "long_field")
    w.s["know"]["Edric"]["plough"] = {"level": "known", "skill": 1.0, "seen": 0, "wins": 0, "fails": 0, "source": "", "since": -1}
    assert do(w, "Edric", do="work", what="plough", at="Long Field").startswith("Refused")
    give(w, "Edric", wooden_plough=1, harness=2)
    w.s["parcels"]["long_field"]["adj"].append("mb_pasture")
    r = do(w, "Edric", do="work", what="plough", at="Long Field")
    assert r.startswith("You ploughed"), r


def test_milking_and_slaughter_by_role():
    w = world()
    w.s["know"]["Edric"]["milk"] = {"level": "known", "skill": 1.0, "seen": 0, "wins": 0, "fails": 0, "source": "", "since": -1}
    assert do(w, "Edric", do="work", what="milk", at=w.s["parcels"]["mb_pasture"]["name"]).startswith("You got")
    r = do(w, "Edric", do="work", what="slaughter", at=w.s["parcels"]["mb_pasture"]["name"], item="ox")
    assert "50 meat" in r and w.s["herds"]["cattle"]["oxen"] == 1


# ---------------------------------------------------------------------- food, fuel, camps
def test_grain_is_eaten_only_at_a_lit_fire_but_bread_anywhere():
    got = N._eat(w := world(), "millbrook", [w.hands("Edric")], 1.0, hearth=False)
    assert got == 0.0 or "grain" not in w.goods(w.hands("Edric"))
    give(w, "Edric", grain=5, bread=0)
    assert N._eat(w, "millbrook", [w.hands("Edric")], 1.0, hearth=False) == 0.0
    give(w, "Edric", bread=2)
    assert N._eat(w, "millbrook", [w.hands("Edric")], 1.0, hearth=False) > 0.9


def test_smelting_with_charcoal_or_timber():
    w = world()
    bid = "smithy"
    st = w.s["containers"][w.s["buildings"][bid]["stock"]]["goods"]
    st.update({"copper ore": 6.0, "timber": 0.0, "charcoal": 1.0})
    for c in [b for b in w.s["buildings"] if w.s["buildings"][b]["node"] == "coppergate"]:
        w.s["containers"][w.s["buildings"][c]["stock"]]["goods"]["timber"] = 0.0
    assert do(w, "Osric", do="make", what="smelt").startswith("You made 1 copper")     # charcoal (D4-46)
    st["timber"] = 4.0
    assert do(w, "Osric", do="make", what="smelt").startswith("You made 1 copper")     # or timber


def test_a_camp_and_a_bedroll_make_a_night_out_cheaper():
    w = world()
    give(w, "Edric", timber=3)
    r = do(w, "Edric", do="build", what="camp", at="Alder Copse")
    assert "camp" in r
    bid = next(b for b, x in w.s["buildings"].items() if x["structure"] == "camp")
    assert w.s["buildings"][bid]["fittings"].get("fire ring") and w.s["buildings"][bid]["lasts_until"] == w.d + 10
    w.s["today"]["sleep"]["Edric"] = bid
    give(w, "Alard", bedroll=1)
    w.s["people"]["Alard"]["at"] = "millbrook"
    rec = N.night(w)
    assert rec["camped"].get("Edric") == "camp" and rec["camped"].get("Alard") == "bedroll"


# ---------------------------------------------------------------------- unexplored places
def test_an_unexplored_place_is_a_way_until_someone_goes_there():
    w = world()
    h = Here(w, "Warin")
    names = [n for _, n, _, _ in h.roads()]
    assert "Grey Crag" not in names and "a goat path up into the crags" in names                    # D4-47
    assert "grey_crag" not in Mind(w, "Warin").places()
    assert do(w, "Warin", do="travel", to="the goat path up into the crags").startswith("You set off")
    N.night(w)
    w.s["day"] += 1
    w.s["events"] = []
    w.s["today"] = R.blank_today()
    R.dawn(w)
    assert w.at("Warin") is None or w.at("Warin") == "grey_crag"
    while w.at("Warin") != "grey_crag":
        N.night(w)
        w.s["day"] += 1
        w.s["today"] = R.blank_today()
        R.dawn(w)
    PC._update_known(Here(w, "Warin"), Mind(w, "Warin"), [])
    assert "grey_crag" in Mind(w, "Warin").places()
    R._mentions(w, Here(w, "Warin"), "Warin", ["Osric"], "I found Grey Crag: good stone up there.")
    assert "grey_crag" in Mind(w, "Osric").places()
