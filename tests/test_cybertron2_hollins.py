"""Hollins (a village, huts in a wood, and a forest several places deep): every access gate checked by action before running
(scenario_design.md §4)."""
import copy
import os

import pytest

from cybertron2.engine import night as N, run as R
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

PATH = "cybertron2/specs/hollins_s7.yaml"
pytestmark = pytest.mark.skipif(not os.path.exists(PATH), reason="hollins not generated")


def world(**patch):
    s = copy.deepcopy(load_spec(PATH))
    s.update(patch)
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def adult_at(w, node, k=0):
    return [n for n in w.living() if w.at(n) == node and w.s["people"][n]["stage"] == "adult"][k]


def test_hollin_wood_runs_out_and_ockley_has_almost_no_wood():
    w = world()
    n = adult_at(w, "hollins")
    w.s["containers"][w.hands(n)]["goods"]["crude tool"] = 1.0
    got = 0.0
    for d in range(60):
        w.s["day"] = d
        r = do(w, n, do="gather", what="fell", at="Hollin Wood")
        if r.startswith("Refused"):
            break
        got = w.goods(w.hands(n)).get("timber", 0.0)
    assert 50 <= got <= 72 and r.startswith("Refused")
    assert w.s["parcels"]["ok_copse"]["res"]["wood"]["S"] <= 10


def test_the_deep_forest_is_reached_only_from_hollins_and_shows_its_next_way_on_arrival():
    w = world()
    assert [x[1] for x in Here(w, adult_at(w, "ockley")).roads()] == ["Hollins"]
    n = adult_at(w, "hollins")
    ways = [x[1] for x in Here(w, n).roads()]
    assert "a deer track down into the ferns" in ways and len(ways) == 4
    assert do(w, n, do="travel", to="a deer track down into the ferns").startswith("You set off")
    w.s["today"]["travel"] = {n: "fern_hollow"}
    N.departures(w, w.s["today"])
    w.s["day"] += 1
    w.s["today"] = R.blank_today()
    R.dawn(w)
    assert w.at(n) == "fern_hollow"
    assert [x[1] for x in Here(w, n).roads()] == ["Hollins", "a climb north out of the hollow under big trees"]


def test_a_couple_can_try_for_a_child_and_a_child_is_fed_from_the_store():
    w = world()
    f = next(n for n, a in w.s["people"].items() if a["sex"] == "f" and a["stage"] == "adult" and a.get("partner") in w.s["people"]
             and w.s["people"][a["partner"]]["stage"] == "adult" and w.at(n) == w.at(a["partner"]))
    m = w.s["people"][f]["partner"]
    assert do(w, f, do="try", **{"with": m, "units": 2}).startswith("You spent")
    kid = next(n for n, a in w.s["people"].items() if a["stage"] == "child")
    assert kid not in w.agents_acting()


def test_the_reply_schema_lets_one_name_an_unexplored_way():
    from cybertron2.engine import prompt as PR
    w = world()
    n = adult_at(w, "hollins")
    to = PR.schema_for(Here(w, n), Mind(w, n))["properties"]["actions"]["items"]["properties"]["to"]
    assert "enum" not in to                                                       # free text: any way as the roads name it
