"""The Wide Country (seven households, four villages, a frontier of eight places): access gates checked by action before running."""
import copy
import os

import pytest

from cybertron2.engine import capacity as CP, run as R
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

PATH = "cybertron2/specs/wide_s7.yaml"
pytestmark = pytest.mark.skipif(not os.path.exists(PATH), reason="wide not generated")
WAYS = {"Wynn": "land well kept", "Cotter": "Cotter way is to have as many", "Ashe": "live by trade", "Rook": "far bigger than anyone knows",
        "Moor": "cattle are wealth that walks", "Fenwick": "largest family in the country", "Reed": "always the ones who went further"}


def world():
    w = World(copy.deepcopy(load_spec(PATH)))
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def test_each_household_has_one_model_its_own_way_and_its_own_aim():
    w = world()
    models = w.spec["household_models"]
    for hh, words in WAYS.items():
        for n in w.members(hh):
            a = w.spec["agents"][n]
            if a["stage"] in ("infant", "child"):
                continue
            assert a["model"] == models[hh]
            assert words in " ".join(w.s["mind"][n]["seeded"])
    for hh in ("Cotter", "Fenwick"):                                   # the family households' aims say children plainly
        assert all("child" in w.spec["agents"][n]["aim"] for n in w.members(hh) if w.spec["agents"][n]["stage"] in ("adult", "youth"))


def test_the_family_couples_can_try():
    w = world()
    for hh in ("Cotter", "Fenwick"):
        f = next(n for n in w.members(hh) if w.s["people"][n]["sex"] == "f" and w.s["people"][n]["stage"] == "adult"
                 and w.s["people"].get(w.s["people"][n].get("partner") or "", {}).get("stage") == "adult")
        assert do(w, f, do="try", **{"with": w.s["people"][f]["partner"], "units": 1}).startswith("You spent")


def test_firewood_is_had_in_every_village_and_each_is_seeded_below_what_it_keeps():
    w = world()
    for hh, wood in (("Wynn", "Wyn Copse"), ("Ashe", "the Coppice"), ("Moor", "the Gill"), ("Reed", "the Carr")):
        n = next(x for x in w.members(hh) if w.s["people"][x]["stage"] == "adult")
        assert do(w, n, do="gather", what="firewood", at=wood).startswith("You took"), hh
    for nid in ("wynford", "holloway", "westmere"):
        c = CP.node(w, nid)
        assert c["people"] / c["keeps"] <= 0.8, nid


def test_the_frontier_is_reached_and_ground_can_be_cleared():
    w = world()
    for hh, n_ways in (("Rook", 3), ("Reed", 2)):
        assert len(Here(w, w.head(hh)).roads()) >= n_ways
    n = next(x for x in w.members("Cotter") if w.s["people"][x]["stage"] == "adult")
    w.s["containers"][w.hands(n)]["goods"]["crude tool"] = 1.0
    assert do(w, n, do="work", what="clear", at="Water Meadow").startswith("You")
