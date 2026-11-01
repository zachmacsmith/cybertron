"""A slaughter shows itself (D4-71): hard to miss on the parcel, heard beside it and, less often, across the place; the ground shows it
the next day; the doer feels it, and is seen bloodied."""
from cybertron2.engine import perceive as PC, run as R, things as TH, verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = "cybertron2/specs/combe.yaml"


def _slaughter_day():
    w = World(load_spec(SPEC))
    w.s["today"] = R.blank_today()
    out = V.do(Here(w, "Ivo"), Mind(w, "Ivo"), {"do": "work", "what": "slaughter", "at": "the Common", "item": "cow"})
    assert out.startswith("You slaughtered a cow"), out
    assert V.do(Here(w, "Margery"), Mind(w, "Margery"), {"do": "work", "what": "herd", "at": "the Common"}).startswith("You watched")
    assert V.do(Here(w, "Everard"), Mind(w, "Everard"), {"do": "gather", "what": "firewood", "at": "Combe Copse"}).startswith("You took")
    return w


def _slaughter_facts(w, name):
    return [f for f in PC.facts(Here(w, name)) if "#slaughter" in str(f.get("sign"))]


def _chance(w, name, f):
    """One person's chance of a spot sign, as perceive.evening reads it (no knack rows here)."""
    if f.get("only") is not None and name not in f["only"]:
        return 0.0
    sp, reach = f["spot"], f.get("reach", "rule")
    if reach == "node":
        return min(1.0, f["salience"])
    if reach in ("near", "around"):
        return min(1.0, f["salience"]) if TH.near_spot(w, name, sp["parcel"], around=reach == "around") else 0.0
    return min(1.0, f["salience"] * TH.spot_chance(w, name, sp["node"], sp["parcel"], sp["own"], sense=f["sense"]))


def _any(w, name, F):
    miss = 1.0
    for f in F:
        miss *= 1.0 - _chance(w, name, f)
    return 1.0 - miss


def test_the_slaughter_is_recorded_on_the_parcel():
    w = _slaughter_day()
    rec = w.s["parcels"]["cb_common"]["slaughter"]
    assert rec["day"] == w.d and rec["kills"] == [{"beast": "cow", "herd": "the Hobb cattle", "by": "Ivo"}]


def test_one_working_there_can_hardly_miss_it_and_one_elsewhere_at_the_place_seldom_notices():
    w = _slaughter_day()
    F = _slaughter_facts(w, "Margery")
    kill = next(f for f in F if f["text"].startswith("Ivo killed a cow of the Hobb cattle on the Common"))
    assert _chance(w, "Margery", kill) == 1.0                                        # working on the parcel: certain
    assert _any(w, "Margery", F) > 0.99
    assert _chance(w, "Everard", kill) == 0.0                                        # in the copse: the kill itself unseen
    far = _any(w, "Everard", F)
    assert 0.2 < far < 0.7, far                                                      # a bellow cut short, the crows: sometimes
    assert {f["sense"] for f in F} >= {"sight", "sound", "smell", "touch"}
    PC.evening(w, {}, w.s["today"])
    assert any("Ivo killed a cow" in t for t in w.s["mind"]["Margery"]["today"]["notice"])


def test_next_door_hears_it_and_the_doer_feels_it_but_is_not_told_of_it_as_a_stranger():
    w = _slaughter_day()
    w.s["today"]["worked"]["Everard"] = ["cb_infield"]                              # next to the Common
    F = _slaughter_facts(w, "Everard")
    bellow = next(f for f in F if f.get("reach") == "around")
    assert _chance(w, "Everard", bellow) > 0.9
    felt = [f for f in F if f["sense"] == "touch"]
    assert felt and felt[0]["only"] == ["Ivo"] and _chance(w, "Ivo", felt[0]) == 1.0
    assert all("Ivo" not in (f.get("only") or ["Ivo"]) for f in F if f["text"].startswith("Ivo killed"))
    person = [f for f in PC.facts(Here(w, "Margery")) if f["about"] == ["person:Ivo"] and "blood" in f["text"]]
    assert person, "the doer is seen bloodied"


def test_the_ground_shows_it_the_next_day_and_not_after():
    w = _slaughter_day()
    w.s["day"] = w.d + 1
    w.s["today"] = R.blank_today()
    texts = [f["text"] for f in _slaughter_facts(w, "Margery")]
    assert texts and not any("killed a cow" in t for t in texts)
    assert any("blood" in t for t in texts)
    w.s["day"] = w.d + 1
    assert not _slaughter_facts(w, "Margery")
