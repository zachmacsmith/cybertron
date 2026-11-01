"""A slaughter shows itself (D4-71), every sign by the one noticing rule (D4-75): certain on the parcel in clear daylight, heard next
door and, less often, two steps off; fog lowers the sight of it and not the sound; distance lowers the sound and the smell; one who
worked there sees more than one passing; the ground shows it the next day; the doer feels it, and is seen bloodied."""
import pytest

from cybertron2.engine import perceive as PC, run as R, things as TH, verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = "cybertron2/specs/combe.yaml"


@pytest.fixture(autouse=True)
def _ordinary_eye(monkeypatch):
    monkeypatch.setattr(TH, "eye_level", lambda w, name: "ordinary")


def _slaughter_day(weather="clear"):
    s = load_spec(SPEC)
    s["weather"] = {1: weather}
    w = World(s)
    w.s["today"] = R.blank_today()
    out = V.do(Here(w, "Ivo"), Mind(w, "Ivo"), {"do": "work", "what": "slaughter", "at": "the Common", "item": "cow"})
    assert out.startswith("You slaughtered a cow"), out
    assert V.do(Here(w, "Margery"), Mind(w, "Margery"), {"do": "work", "what": "herd", "at": "the Common"}).startswith("You watched")
    return w


def _facts(w):
    return [f for f in PC.facts(Here(w, "Margery")) if "#slaughter" in str(f.get("sign"))]


def _chance(w, name, f):
    if f.get("only") is not None and name not in f["only"]:
        return 0.0
    return PC.chance_of(w, name, f)


def _kill(F):
    return next(f for f in F if f["text"].startswith("Ivo killed a cow of the Hobb cattle on the Common"))


def _bellow(F):
    return next(f for f in F if f["sense"] == "sound")


def _at(w, name, parcels):
    """Put `name` on these parcels today, and nowhere else (its route)."""
    w.s["today"]["worked"][name] = list(parcels)
    w.s["today"].setdefault("route", {})[name] = list(parcels)


def test_the_slaughter_is_recorded_on_the_parcel():
    w = _slaughter_day()
    rec = w.s["parcels"]["cb_common"]["slaughter"]
    assert rec["day"] == w.d and rec["kills"] == [{"beast": "cow", "herd": "the Hobb cattle", "by": "Ivo"}]


def test_on_the_parcel_it_is_certain_next_door_heard_two_steps_off_heard_less():
    w = _slaughter_day()
    F = _facts(w)
    assert _chance(w, "Margery", _kill(F)) == 1.0                                    # worked on the parcel, clear day
    _at(w, "Everard", ["cb_infield"])
    assert _chance(w, "Everard", _kill(F)) == 0.0                                    # the close look is for those on it
    near = _chance(w, "Everard", _bellow(F))
    _at(w, "Everard", ["cb_copse"])                                                  # two steps off (the Copse, by the Green)
    far = _chance(w, "Everard", _bellow(F))
    assert near > 0.85 and 0.3 < far < 0.5, (near, far)
    smell = next(f for f in F if f["sense"] == "smell")
    assert _chance(w, "Everard", smell) == 0.0                                       # the smell of guts: no further than next door
    assert {f["sense"] for f in F} >= {"sight", "sound", "smell", "touch"}
    PC.evening(w, {}, w.s["today"])
    assert any("Ivo killed a cow" in t for t in w.s["mind"]["Margery"]["today"]["notice"])


def test_fog_lowers_the_sight_of_it_not_the_sound():
    clear, fog = _slaughter_day("clear"), _slaughter_day("fog")
    Fc, Ff = _facts(clear), _facts(fog)
    assert _chance(fog, "Margery", _kill(Ff)) < 0.5 * _chance(clear, "Margery", _kill(Fc))
    assert _chance(fog, "Margery", _bellow(Ff)) == _chance(clear, "Margery", _bellow(Fc))
    gale = _slaughter_day("gale")
    assert _chance(gale, "Margery", _bellow(_facts(gale))) < 0.5                    # a gale drowns it


def test_one_who_worked_there_sees_more_than_one_passing():
    w = _slaughter_day()
    F = _facts(w)
    crows = next(f for f in F if "crows" in f["text"])
    _at(w, "Everard", ["cb_moor"])                                                  # the Moor lies beyond the Common: crossed
    w.s["today"]["route"]["Everard"] = ["cb_common", "cb_moor"]
    passing = _chance(w, "Everard", crows)
    assert 0 < passing < _chance(w, "Margery", crows)


def test_the_doer_feels_it_and_is_seen_bloodied_but_not_told_of_it():
    w = _slaughter_day()
    F = _facts(w)
    felt = [f for f in F if f["sense"] == "touch"]
    assert felt and felt[0]["only"] == ["Ivo"] and _chance(w, "Ivo", felt[0]) == 1.0
    assert _chance(w, "Ivo", _kill(F)) == 0.0 and _chance(w, "Ivo", _bellow(F)) == 0.0
    person = [f for f in PC.facts(Here(w, "Margery")) if f["about"] == ["person:Ivo"] and "blood" in f["text"]]
    assert person and max(_chance(w, "Margery", f) for f in person) >= 0.6       # his household sees him come in


def test_the_ground_shows_it_the_next_day_and_not_after():
    w = _slaughter_day()
    w.s["day"] = w.d + 1
    w.s["today"] = R.blank_today()
    texts = [f["text"] for f in _facts(w)]
    assert texts and not any("killed a cow" in t for t in texts)
    assert any("blood" in t for t in texts)
    w.s["day"] = w.d + 1
    assert not _facts(w)
