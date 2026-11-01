"""Every perceived line about the world comes from the one noticing rule (D4-75): sound and smell carry by steps in the parcel graph;
the eye reads sight only; a body in one's own house is still found; a frost is still felt by everyone; what happens to one, or in
one's house, is read in full and the rest by the rule; an attended subject is mostly seen; dawn lines go through the rule."""
import pytest

from cybertron2.engine import perceive as PC, run as R, things as TH
from cybertron2.engine.data import NOTICING
from cybertron2.engine.here import Here
from cybertron2.engine.world import World, load_spec

SPEC = "cybertron2/specs/combe.yaml"


@pytest.fixture(autouse=True)
def _ordinary_eye(monkeypatch):
    monkeypatch.setattr(TH, "eye_level", lambda w, name: "ordinary")


def _world(weather="clear"):
    s = load_spec(SPEC)
    s["weather"] = {1: weather, 2: weather}
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def _at(w, name, parcels):
    w.s["today"]["worked"][name] = list(parcels)
    w.s["today"].setdefault("route", {})[name] = list(parcels)


def test_sound_and_smell_carry_by_steps_sight_does_not():
    w = _world()
    _at(w, "Everard", ["cb_copse"])                                                  # the Common is two steps off
    assert TH.steps(w, "Everard", "cb_common") == 2 and TH.steps(w, "Everard", "cb_copse") == 0
    sound = TH.spot_chance(w, "Everard", "combe", "cb_common", 1.0, sense="sound")
    smell = TH.spot_chance(w, "Everard", "combe", "cb_common", 1.0, sense="smell")
    sight = TH.spot_chance(w, "Everard", "combe", "cb_common", 1.0, sense="sight")
    assert sound == NOTICING["carry"]["sound"][2] and smell == NOTICING["carry"]["smell"][2]
    assert sight == NOTICING["presence"]["elsewhere"]
    assert TH.spot_chance(w, "Everard", "combe", "cb_common", 1.0, sense="touch") == 0.0   # touch: only where one is


def test_night_and_fog_lower_sight_and_leave_sound():
    w, fog = _world(), _world("fog")
    _at(w, "Ivo", ["cb_common"])
    _at(fog, "Ivo", ["cb_common"])
    day = TH.spot_chance(w, "Ivo", "combe", "cb_common", 1.0, sense="sight")
    assert TH.spot_chance(w, "Ivo", "combe", "cb_common", 1.0, sense="sight", night=True) < 0.2 * day
    assert TH.spot_chance(fog, "Ivo", "combe", "cb_common", 1.0, sense="sight") < 0.5 * day
    snd = TH.spot_chance(w, "Ivo", "combe", "cb_common", 1.0, sense="sound")
    assert TH.spot_chance(fog, "Ivo", "combe", "cb_common", 1.0, sense="sound") == snd
    assert TH.spot_chance(w, "Ivo", "combe", "cb_common", 1.0, sense="sound", night=True) >= snd


def test_a_body_in_ones_own_house_is_still_found_and_a_frost_felt_by_everyone():
    w = _world()
    cid = w.apply("new_thing", "combe", node="combe", parcel="cb_green", kind="remains", of="Odo", body=True, died=w.d,
                  **{"in": "hobb_house"})
    assert TH.chance(w, "Margery", w.s["containers"][cid]) == 1.0
    frost = {"about": ["sky"], "salience": 0.85, "sense": "touch", "spot": {"node": "combe", "parcel": None, "own": 1.0, "everyone": True}}
    assert PC.chance_of(w, "Everard", frost) == 0.85


def test_what_happened_in_ones_house_is_read_in_full_and_the_rest_by_the_rule():
    w = _world()
    loss = {"about": ["building:hobb_house"], "concerns": ["Margery"], "actor": None}
    assert PC.happened_to(w, "Margery", loss)
    field = {"about": ["parcel:cb_infield"], "concerns": ["Margery"], "actor": "Ivo"}
    assert not PC.happened_to(w, "Margery", field)
    hit = {"about": ["person:Ivo", "person:Margery"], "concerns": ["Margery"], "actor": "Ivo"}
    assert PC.happened_to(w, "Margery", hit) and not PC.happened_to(w, "Ivo", hit)


def test_an_attended_subject_is_mostly_seen():
    w = _world()
    _at(w, "Margery", ["cb_infield"])
    f = {"about": ["herd:hobb_cattle"], "salience": 0.3, "sense": "sight", "spot": {"node": "combe", "parcel": "cb_common", "own": 1.0}}
    plain = PC.chance_of(w, "Margery", f)
    sought = PC.chance_of(w, "Margery", f, attending=True)
    assert sought > 0.6 and sought > 5 * plain
