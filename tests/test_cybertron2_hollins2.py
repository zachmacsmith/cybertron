"""Hollins 2 (Package F woods, three households with their own ways): access gates checked by action before running."""
import copy
import os

import pytest

from cybertron2.engine import capacity as CP, run as R
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

PATH = "cybertron2/specs/hollins2_s8.yaml"
pytestmark = pytest.mark.skipif(not os.path.exists(PATH), reason="hollins2 not generated")


def world():
    w = World(copy.deepcopy(load_spec(PATH)))
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def test_each_household_holds_its_own_way():
    w = world()
    for hh, words in (("Thorne", "land well kept"), ("Webb", "as strong as its children"), ("Hunt", "the wood beyond the wood")):
        for n in w.members(hh):
            seeded = " ".join(w.s["mind"][n]["seeded"])
            assert words in seeded                                   # (one married in also keeps the way of the house it was born in)


def test_firewood_is_had_in_ockley_and_its_woods_keep_it_at_about_two_thirds():
    w = world()
    n = next(x for x in w.members("Webb") if w.s["people"][x]["stage"] == "adult")
    assert do(w, n, do="gather", what="firewood", at="the Hanger").startswith("You took 3 firewood")
    c = CP.node(w, "ockley")
    assert 0.5 <= c["people"] / c["keeps"] <= 0.75


def test_couples_can_try_and_the_deep_forest_is_reached_from_hollins():
    w = world()
    f = next(n for n, a in w.s["people"].items() if a["sex"] == "f" and a["stage"] == "adult" and a.get("partner") in w.s["people"]
             and w.s["people"][a["partner"]]["stage"] == "adult")
    assert do(w, f, do="try", **{"with": w.s["people"][f]["partner"], "units": 1}).startswith("You spent")
    hunt = w.head("Hunt")
    assert len(Here(w, hunt).roads()) == 4
