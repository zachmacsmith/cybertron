"""The 18 bundles of review 38.43 (D4-74), every row by the one noticing rule (D4-75): who reads each (the doer, those near, those far
off), what lingers on later days, and what shows only under its conditions (snow, rain, frost, the dark, dogs kept)."""
import pytest

from cybertron2.engine import farm as FM, perceive as PC, run as R, settle as ST, things as TH, verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

VALLEY = "cybertron2/specs/valley_s5.yaml"


@pytest.fixture(autouse=True)
def _ordinary_eye(monkeypatch):
    monkeypatch.setattr(TH, "eye_level", lambda w, name: "ordinary")


def _world(weather="clear", spec=VALLEY, cold=False):
    s = load_spec(spec)
    s["weather"] = {d: weather for d in range(1, 8)}
    if cold:
        s["cold_days"] = list(range(0, 8))
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def _at(w, name, parcels):
    w.s["today"]["worked"][name] = list(parcels)
    w.s["today"].setdefault("route", {})[name] = list(parcels)


def _facts(w, tag, who="Odo"):
    return [f for f in PC.facts(Here(w, who)) if f"#{tag}" in str(f.get("sign"))]


def _p(w, name, f):
    if f.get("only") is not None and name not in f["only"]:
        return 0.0
    return PC.chance_of(w, name, f)


def _one(F, word):
    return next(f for f in F if word in f["text"])


def _next_day(w, n=1):
    w.s["day"] = w.d + n
    w.s["today"] = R.blank_today()


# ---- 1. a fight in the night; a raid on a house
def _fight(w, by="Hamo", target="Edric"):
    w.s["today"]["fights"].append({"kind": "attack", "by": by, "target": target, "aim": "rob", "node": "millbrook"})
    return ST.settle_fights(w, w.s["today"])


def test_a_fight_is_heard_in_the_dark_felt_by_who_struck_and_marks_the_ground():
    w = _world()
    _fight(w)
    rec = w.s["parcels"]["mb_green"]["fight"]
    assert rec["fights"][0]["by"] == "Hamo"
    F = _facts(w, "fight")
    sound = _one(F, "scuffle")
    assert _p(w, "Odo", sound) > 0.9                                                # asleep in Reed House on the Green
    _at(w, "Hamo", ["mb_green"])
    assert _p(w, "Hamo", sound) == 0.0 and _p(w, "Hamo", _one(F, "knuckles")) == 1.0
    assert _p(w, "Edric", sound) == 0.0                                             # the one set upon knows it in the body
    sight = _one(F, "shapes struggling")
    _at(w, "Cecily", ["mb_pasture"])                                                # not of the house; worked next door
    assert _p(w, "Cecily", sight) < 0.15 < _p(w, "Cecily", sound)                   # in the dark: heard, hardly seen
    _next_day(w)
    assert any("scuffed and trampled" in f["text"] for f in _facts(w, "fight"))     # lingering
    _next_day(w)
    assert not _facts(w, "fight")


def test_a_fight_in_the_snow_and_a_raid_leave_their_marks():
    w = _world("snow", cold=True)
    _fight(w)
    assert any("snow by the Green is trampled" in f["text"] for f in _facts(w, "fight"))
    w.s["today"]["fights"].append({"kind": "raid", "by": "Hamo", "building": "reed_house", "node": "millbrook"})
    ST.settle_fights(w, w.s["today"])
    F = _facts(w, "raided")
    assert any("footprints in the snow" in f["text"] for f in F)


# ---- 2. a hunting kill
def test_a_hunting_kill_is_felt_seen_gutted_and_draws_the_crows():
    w = _world()
    got = ""
    for d in range(30):
        w.s["day"] = d
        w.s["today"] = R.blank_today()
        got = do(w, "Edric", do="gather", what="hunt", at="Alder Copse")
        if "caught nothing" not in got and not got.startswith("Refused"):
            break
    assert w.s["parcels"]["alder_copse"].get("hunted", {}).get("day") == w.d, got
    F = _facts(w, "hunted")
    assert _p(w, "Edric", _one(F, "warm weight")) == 1.0
    _at(w, "Sibyl", ["alder_copse"])
    gut = _one(F, "gutting")
    assert _p(w, "Sibyl", gut) > _p(w, "Odo", gut)                                 # in the wood, against at home
    assert any("blood to the elbows" in f["text"] for f in PC.facts(Here(w, "Odo")) if f["about"] == ["person:Edric"])
    _next_day(w)
    assert any("crows" in f["text"] for f in _facts(w, "hunted"))


# ---- 3. a fire in a house
def test_a_fire_glows_across_the_place_smokes_out_those_inside_and_leaves_a_burnt_roof():
    w = _world()
    w.apply("set", "millbrook", ref=("building", "hale_house"), field="fire_hit", value={"day": w.d})
    F = _facts(w, "fire_hit")
    glow, smoke = _one(F, "glow"), _one(F, "smoke thick")
    assert _p(w, "Hamo", smoke) == 1.0 and _p(w, "Odo", smoke) == 0.0              # those who sleep there
    _at(w, "Edric", ["alder_copse"])                                                # three steps off: still the glow
    assert _p(w, "Edric", glow) > 0.1
    w2 = _world("rain")
    w2.apply("set", "millbrook", ref=("building", "hale_house"), field="fire_hit", value={"day": w2.d})
    _next_day(w2, 2)
    texts = [f["text"] for f in _facts(w2, "fire_hit")]
    assert any("charred" in t for t in texts) and any("rain dripping" in t for t in texts)
    _next_day(w2, 2)
    assert not _facts(w2, "fire_hit")


# ---- 4. a birth
def test_a_birth_is_heard_in_the_night_and_the_mother_is_seen_after():
    w = _world()
    child = w.apply("born", "millbrook", mother="Sibyl")
    w.event("millbrook", "birth", f"Sibyl gave birth to a child, {child}", actor="Sibyl", target=child, about=["building:reed_house"])
    cry = _one(_facts(w, "birth"), "newborn")
    assert _p(w, "Odo", cry) == 1.0 and 0 < _p(w, "Hamo", cry) < 1.0 and _p(w, "Sibyl", cry) == 0.0
    _next_day(w)
    assert any("childbed" in f["text"] for f in PC.facts(Here(w, "Odo")) if f["about"] == ["person:Sibyl"])


# ---- 5. food rotting in a store
def test_rotting_meat_in_a_store_stinks_for_those_who_live_there_and_carries_a_little():
    w = _world()
    w.apply("create", "millbrook", dst=w.s["buildings"]["reed_house"]["stock"], item="rotting meat", qty=4)
    F = [f for f in PC.facts(Here(w, "Odo")) if "stink of rotting meat" in f["text"]]
    assert F and _p(w, "Odo", F[0]) >= 0.8
    _at(w, "Hamo", ["alder_copse"])
    assert 0 <= _p(w, "Hamo", F[0]) < _p(w, "Odo", F[0])
    cold = _world(cold=True)
    cold.apply("create", "millbrook", dst=cold.s["buildings"]["reed_house"]["stock"], item="rotting meat", qty=4)
    assert not [f for f in PC.facts(Here(cold, "Odo")) if "stink of rotting meat" in f["text"]]   # frost keeps it


# ---- 6. a guard posted
def test_a_guard_is_seen_by_those_inside_hardly_in_the_dark_and_feels_the_night():
    w = _world()
    assert do(w, "Sibyl", do="guard", at="Reed House").startswith("You stand guard")
    F = _facts(w, "guard")
    watch = _one(F, "kept watch")
    assert _p(w, "Odo", watch) == 1.0 and _p(w, "Hamo", watch) < 0.1             # the household; a neighbour in the dark
    assert _p(w, "Sibyl", _one(F, "sitting up")) == 1.0
    assert any("heavy-eyed" in f["text"] for f in PC.facts(Here(w, "Odo")) if f["about"] == ["person:Sibyl"])


# ---- 7. beasts driven
def test_beasts_driven_are_heard_and_leave_a_track_churned_in_the_wet():
    w = _world("rain")
    out = do(w, "Edric", do="drive", thing="the Millbrook cattle", to="Long Field")
    assert out.startswith("You drove"), out
    F = _facts(w, "driven")
    hooves = _one(F, "thud of hooves")
    _at(w, "Hamo", ["alder_copse"])                                                 # next to Long Field
    assert _p(w, "Hamo", hooves) > 0.3 and _p(w, "Edric", hooves) == 0.0
    _next_day(w, 2)
    assert any("churned to mud" in f["text"] for f in _facts(w, "driven"))
    _next_day(w)
    assert not _facts(w, "driven")


# ---- 8. a weapon made; 14. a house mended or breaking
def test_woodwork_and_a_weapon_made_and_mending_are_heard_at_the_house():
    w = _world()
    w.event("millbrook", "make", "Edric was making a crude weapon", actor="Edric", about=["building:reed_house"], tech="crude weapon")
    w.event("millbrook", "work", "Odo was repairing", actor="Odo", about=["building:reed_house"], tech="repair")
    texts = {f["text"]: f for f in PC.facts(Here(w, "Hamo")) if "building:reed_house" in f["about"]}
    assert any("shaping a club" in t for t in texts) and any("knock and scrape" in t for t in texts)
    assert any("mallets knocking" in t for t in texts)


def test_a_house_breaking_in_the_night_is_heard_and_its_roof_seen_in():
    w = _world()
    w.apply("set", "millbrook", ref=("building", "hale_house"), field="broke", value={"day": w.d, "to": 0})
    F = _facts(w, "broke")
    crack = _one(F, "long crack")
    assert _p(w, "Hamo", crack) == 1.0 and 0 < _p(w, "Odo", crack)
    _next_day(w, 2)
    assert any("roof has come in" in f["text"] for f in _facts(w, "broke"))


# ---- 9. sleeping out
def test_one_who_slept_out_in_the_frost_is_seen_so():
    w = _world(cold=True)
    w.apply("set", "millbrook", ref=("person", "Edric"), field="slept_out", value={"day": w.d, "cold": True})
    rows = [f for f in PC.facts(Here(w, "Odo")) if f["about"] == ["person:Edric"] and "frost" in f["text"]]
    assert rows and _p(w, "Odo", rows[0]) >= 0.8                                    # his household


# ---- 10. ploughing and reaping; 11. quarrying
def test_ploughing_reaping_and_picks_are_heard_beyond_the_field():
    w = _world(cold=True)
    w.event("millbrook", "work", "Edric was ploughing", actor="Edric", about=["parcel:long_field"], tech="plough")
    F = [f for f in PC.facts(Here(w, "Odo")) if "plough" in f["text"]]
    creak = _one(F, "creak of the plough")
    assert "frozen clods" in creak["text"]
    _at(w, "Hamo", ["mb_pasture"])                                                  # two steps off
    assert 0 < _p(w, "Hamo", creak) < 0.5
    c = _world()
    c.s["parcels"]["long_field"]["crop"] = {"kind": "barley", "crop": "grain", "area": 2, "area_left": 2, "ripe_day": 0, "sown": -10,
                                             "seed": 1, "left": 10, "broken": 2}
    c.event("millbrook", "work", "Edric was reaping", actor="Edric", about=["parcel:long_field"], tech="reap")
    assert any("swish of sickles" in f["text"] for f in PC.facts(Here(c, "Odo")))
    q = _world(spec="cybertron2/specs/valley_s5.yaml")
    q.event("coppergate", "work", "Osric was quarrying", actor="Osric", about=["parcel:cg_quarry"], tech="quarry")
    assert any("ring of picks on stone" in f["text"] for f in PC.facts(Here(q, "Rohese")))


# ---- 12. a theft from a store
def test_a_theft_shows_in_the_store_and_in_the_snow():
    w = _world("snow", cold=True)
    out = do(w, "Edric", do="take", item="grain", qty=2, **{"from": "Hale House"})
    assert "not yours" in out, out
    ST.settle_thefts(w, w.s["today"], {})
    F = _facts(w, "theft", who="Hamo")
    lower = _one(F, "less than there was")
    assert _p(w, "Hamo", lower) >= 0.8 and _p(w, "Odo", lower) == 0.0
    assert any("footprints in the snow" in f["text"] for f in F)


# ---- 13. calving; 18. milking and minding
def test_calving_is_heard_and_leaves_the_afterbirth_and_minding_shows():
    w = _world()
    w.apply("set", "millbrook", ref=("herd", "cattle"), field="last_calf", value=w.d)
    w.apply("set", "millbrook", ref=("herd", "cattle"), field="watched", value=w.d)
    texts = [f["text"] for f in PC.facts(Here(w, "Odo")) if "herd:cattle" in f["about"]]
    assert any("lowing low to her new calf" in t for t in texts) and any("afterbirth" in t for t in texts)
    assert any("minding the Millbrook cattle" in t for t in texts)


# ---- 15. a burial
def test_a_burial_is_seen_and_heard_and_the_frozen_ground_felt_by_the_digger():
    w = _world(cold=True)
    w.apply("die", "millbrook", person="Odo", cause="old age")
    cid = w.apply("new_thing", "millbrook", node="millbrook", parcel="mb_pasture", kind="remains", of="Odo", body=True, died=w.d)
    TH.remember(w, "Edric", cid, "saw", close=True)
    out = do(w, "Edric", do="work", what="bury", at="Odo")
    assert out.startswith("You buried"), out
    F = _facts(w, "burial", who="Hamo")
    assert _p(w, "Edric", _one(F, "hacked out")) == 1.0
    _at(w, "Hamo", ["mb_green"])                                                    # next door: the spade heard on frozen ground
    assert _p(w, "Hamo", _one(F, "scrape of a spade")) > 0.2
