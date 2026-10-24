"""The next region world (02t, D2-137): every access gate verified by action before running (02t §5, scenario_design.md §4)."""
import copy
import os

import pytest

from cybertron2.engine import run as R, roads as RD
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

PATH = "cybertron2/specs/region_c1.yaml"
pytestmark = pytest.mark.skipif(not os.path.exists(PATH), reason="region_c not generated")


def world(path=PATH, **patch):
    s = copy.deepcopy(load_spec(path))
    s.update(patch)
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def adult_at(w, node, household=None):
    return next(n for n in w.living() if w.at(n) == node and w.s["people"][n]["stage"] == "adult"
                and (household is None or w.household_of(n) == household))


def test_barleyfield_cannot_fell_more_than_its_copse():
    w = world()
    n = adult_at(w, "barleyfield")
    w.s["containers"][w.hands(n)]["goods"]["crude tool"] = 1.0
    got = 0.0
    for d in range(40):
        w.s["day"] = d
        r = do(w, n, do="gather", what="fell", at="Barley Copse")
        if r.startswith("Refused"):
            break
        got = w.goods(w.hands(n)).get("timber", 0.0)
    assert got <= 14 and r.startswith("Refused")


def test_ashwood_has_no_field_to_farm():
    w = world()
    n = adult_at(w, "ashwood")
    w.s["containers"][w.hands(n)]["goods"]["grain"] = 20.0
    assert do(w, n, do="work", what="sow").startswith("Refused")


def test_the_handcart_refuses_the_holloway_and_goes_by_the_track():
    w = world()
    n = adult_at(w, "barleyfield")
    w.s["containers"][w.hands(n)]["goods"].update({"handcart": 1.0, "grain": 35.0})
    assert do(w, n, do="travel", to="Ashwood").startswith("Refused")           # no track: on foot, 10
    assert do(w, n, do="travel", to="Millford").startswith("You set off")      # the cart road


def test_the_pass_is_snowed_in_deep_winter():
    w = world()
    rid = next(r for r, x in w.s["roads"].items() if {x["a"], x["b"]} == {"coppergate", "millford"})
    pos, lm = next((k + 1, l) for k, s in enumerate(w.s["roads"][rid]["stretches"]) for l in s["landmarks"] if l["kind"] == "pass")
    w.s["day"] = next(d for d in range(w.days) if w.calendar(d)["season"] == "winter")
    w.spec.setdefault("weather", {})[w.d + 1] = "snow"
    assert RD.challenge(w, rid, pos, lm) == "snowed"


def test_the_merchant_can_lead_the_pack_ox_and_carry_60():
    w = world()
    m = adult_at(w, "millford", "Merchant")
    w.s["containers"][w.hands(m)]["goods"].update({"harness": 1.0, "grain": 55.0})
    assert do(w, m, do="travel", to="Barleyfield").startswith("Refused")       # 55 is too heavy without the ox
    assert do(w, m, do="travel", to="Barleyfield", lead="the ox").startswith("You set off")


def test_the_null_arm_has_the_same_people_and_can_keep_itself():
    w1, w0 = world(), world("cybertron2/specs/region_c0.yaml")
    assert sorted(w1.living()) == sorted(w0.living())
    assert w0.s["parcels"]["aw_field"]["crop"] and w0.s["parcels"]["bf_copse"]["res"]["wood"]["S"] >= 100
