"""Package F (37.2's brief 02zb §2): forests as three stocks, fuel in heat, shelter and fire, eating raw, seeding by flows
(D2-156 to D2-161)."""
import copy

from cybertron2.engine import capacity as CP, forests as FO, night as N, run as R
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = load_spec("cybertron2/specs/valley_s5.yaml")


def world(**parcels):
    s = copy.deepcopy(SPEC)
    for pid, x in parcels.items():
        node = next(n for n, v in s["nodes"].items() if pid in v["parcels"])
        s["nodes"][node]["parcels"][pid].update(x)
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def days(w, n):
    for _ in range(n):
        FO.night(w)
        w.s["day"] += 1


COPSE = {"cover": "forest", "size": 1, "state": {"wood": {"kind": "copse"}}}


def test_a_copse_left_alone_keeps_its_trees_and_sheds_firewood_felled_it_turns_to_scrub():
    w = world(alder_copse=COPSE)
    res = w.s["parcels"]["alder_copse"]["res"]
    assert res["wood"]["S"] == 300 and res["young"]["K"] == 40 and res["dead"]["S"] == 50
    assert abs(CP.wood_flow(w.s["parcels"]["alder_copse"]) - 18) < 0.5                # about 18 firewood a year
    days(w, 24)
    assert res["wood"]["S"] >= 299
    w2 = world(alder_copse=COPSE)
    p2 = w2.s["parcels"]["alder_copse"]
    p2["res"]["wood"]["S"] = 90                                                        # felled to 30%
    days(w2, 1)
    assert p2["cover"] == "scrub" and CP.wood_flow(p2) < CP.wood_flow(w.s["parcels"]["alder_copse"]) - 6


def test_young_growth_regrows_ungrazed_and_not_under_a_herd():
    w = world(alder_copse=COPSE)
    y = w.s["parcels"]["alder_copse"]["res"]["young"]
    y["S"] = 10
    days(w, 6)
    grown = y["S"]
    assert grown > 11
    w2 = world(alder_copse=COPSE)
    y2 = w2.s["parcels"]["alder_copse"]["res"]["young"]
    y2["S"] = 10
    hid = next(iter(w2.s["herds"]))
    w2.s["herds"][hid].update(parcel="alder_copse", node="millbrook")
    days(w2, 6)
    assert y2["S"] == 10


def test_a_hearth_burns_heat_by_the_order():
    w = world()
    cid = w.s["buildings"]["reed_house"]["stock"]
    w.s["containers"][cid]["goods"] = {"firewood": 10.0, "timber": 5.0}
    assert FO.burn(w, "millbrook", cid, 1.0) and abs(w.goods(cid)["firewood"] - 8.0) < 1e-6            # a normal night: 2 firewood
    w.s["containers"][cid]["goods"] = {"timber": 5.0}
    assert FO.burn(w, "millbrook", cid, 4.0) and abs(w.goods(cid)["timber"] - 3.0) < 1e-6              # a cold one: 2 timber
    w.s["containers"][cid]["goods"] = {"firewood": 8.0}
    assert FO.burn(w, "millbrook", cid, 4.0) and w.goods(cid)["firewood"] < 1e-6                         # or 8 firewood


def test_charcoal_gives_six_heat():
    w = world()
    cid = w.s["buildings"]["reed_house"]["stock"]
    w.s["containers"][cid]["goods"] = {"charcoal": 1.0}
    assert FO.burn(w, "millbrook", cid, 4.0) and abs(w.goods(cid)["charcoal"] - 1 / 3) < 1e-6            # two-thirds of one


def test_travellers_sleeping_out_share_a_fire_of_two_timber_five_need_two():
    w = world()
    out = [n for n in w.living() if w.at(n) == "millbrook" and w.s["people"][n]["stage"] in ("adult", "elder", "youth")][:5]
    for n in out:
        w.s["containers"][w.hands(n)]["goods"]["timber"] = 2.0
    where = {n: ("elsewhere" if n not in out else None) for n in w.living()}
    rec = {}
    w.s["today"]["fire"] = {out[0]: True, out[1]: True}
    warmed = N.open_fires(w, w.s["today"], where, rec)
    assert set(out[:2]) <= warmed and len(warmed) == 4 and rec["open_fire"] == [out[0]]                  # one fire for four
    assert w.goods(w.hands(out[1]))["timber"] == 2.0
    w.s["today"]["fire"] = {n: True for n in out}
    for n in out:
        w.s["containers"][w.hands(n)]["goods"]["timber"] = 2.0
    rec = {}
    assert len(N.open_fires(w, w.s["today"], where, rec)) == 5 and len(rec["open_fire"]) == 2               # five need two


def test_a_hearth_warms_twelve_spaces_a_hall_is_partly_cold():
    w = world()
    b = w.s["buildings"]["reed_house"]
    b["size"] = 12
    w.s["containers"][b["stock"]]["goods"]["timber"] = 10.0
    w.cold_days = {0}
    rec = N.night(w)
    assert rec["hearth"]["reed_house"]["warm"] == 1.0
    w2 = world()
    b2 = w2.s["buildings"]["reed_house"]
    b2["size"] = 30
    w2.s["containers"][b2["stock"]]["goods"]["timber"] = 10.0
    w2.cold_days = {0}
    assert N.night(w2)["hearth"]["reed_house"]["warm"] < 0.5


def test_food_raw():
    w = world()
    h = w.hands("Edric")
    for item, fed in (("grain", 20), ("flour", 50), ("beans", 0)):
        w.s["containers"][h]["goods"] = {item: 100.0}
        assert abs(N._eat(w, "millbrook", [h], 1000.0, hearth=False) - fed) < 1e-6
    w.s["containers"][h]["goods"] = {"bread": 10.0}
    assert abs(N._eat(w, "millbrook", [h], 1000.0, hearth=False) - 13.0) < 1e-6                             # bread full


def test_firewood_needs_no_tool_and_a_child_may_gather_it_felling_bare_handed_is_poor():
    w = world(alder_copse=COPSE)
    n = "Edric"
    w.s["containers"][w.hands(n)]["goods"] = {}
    r = do(w, n, do="gather", what="firewood", at="Alder Copse")
    assert r.startswith("You took 3 firewood"), r
    from cybertron2.engine.data import LIFE
    assert "firewood" in LIFE["children_work"]
    before = w.s["parcels"]["alder_copse"]["res"]["dead"]["S"]
    w.s["containers"][w.hands(n)]["goods"] = {"crude tool": 1.0}
    r = do(w, n, do="gather", what="fell", at="Alder Copse")
    assert "3 timber" in r and w.s["parcels"]["alder_copse"]["res"]["dead"]["S"] > before - 0.01            # brash left
    w.s["containers"][w.hands(n)]["goods"] = {}
    r = do(w, n, do="gather", what="fell", at="Alder Copse")                                              # bare hands: a quarter
    assert float(r.split("You took ")[1].split(" timber")[0]) < 1.0
    assert do(w, n, do="gather", what="cut", at="Alder Copse").startswith("Refused")                        # young growth: a tool


def test_the_capacity_check_for_a_small_village():
    s = copy.deepcopy(SPEC)
    s["nodes"] = {"vill": {"name": "Vill", "parcels": {
        "g": {"name": "the Green", "cover": "built", "size": 1},
        "f": {"name": "Fields", "cover": "field", "size": 8},
        "m": {"name": "the Coppice", "cover": "forest", "size": 2, "state": {"wood": {"kind": "managed wood"}}},
        "c": {"name": "the Copse", "cover": "forest", "size": 1, "state": {"wood": {"kind": "copse"}}}}}}
    s["roads"], s["buildings"], s["herds"], s["agents"], s["households"] = [], {}, {}, {}, {}
    s.pop("claims", None)
    c = CP.node(World(s), "vill")
    assert abs(c["food_people"] - 17) < 1 and abs(c["heat_people"] - 14) < 1
