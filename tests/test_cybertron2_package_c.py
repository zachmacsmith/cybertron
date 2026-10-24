"""Package C (37.2's brief 02s §3): the Q-20 changes (D2-120 to D2-122, D2-129), the parcel graph (D2-114 to D2-116), fences and gates
(D2-130, D2-132), herds wandering, lost on roads, driven and splitting (D2-117, D2-123, D2-124, D2-127, D2-128, D2-131), and hidden
ways (D2-90, D2-92, D2-98)."""
import copy

from cybertron2.engine import agreements as AG, fuse as FU, night as N, roads as RD, run as R, settle as ST
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = load_spec("cybertron2/specs/valley_s5.yaml")


def world(roads=None, **patch):
    s = copy.deepcopy(SPEC)
    if roads is not None:
        s["roads"] = roads
    s.update(patch)
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def next_day(w):
    w.s["day"] += 1
    w.s["events"] = []
    w.s["today"] = R.blank_today()
    R.dawn(w)


def depart(w, who, to, **choices):
    w.s["today"].setdefault("travel", {})[who] = to
    if choices:
        w.s["today"].setdefault("travel_choices", {})[who] = choices


# ---------------------------------------------------------------------- C1: the Q-20 changes
def test_a_road_with_no_terrain_gets_one_and_parties_meet_on_it_but_a_bare_road_holds_nothing(monkeypatch):
    monkeypatch.setitem(RD.TERRAIN["farmland"], "meet", 1.0)
    w = world(roads=[["millbrook", "ashwood", 1]])
    r = w.s["roads"]["road:millbrook-ashwood"]
    assert r["terrain"] == "farmland" and RD.active(r)                                  # D2-122
    depart(w, "Edric", "ashwood")
    depart(w, "Simkin", "millbrook")
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    assert len(w.s["today"]["road"]["meetings"]) == 1
    w2 = world(roads=[["millbrook", "ashwood", 1, {"bare": True}]])
    assert not RD.active(w2.s["roads"]["road:millbrook-ashwood"])
    depart(w2, "Edric", "ashwood")
    depart(w2, "Simkin", "millbrook")
    N.departures(w2, w2.s["today"])
    RD.night(w2, w2.s["today"])
    assert w2.s["today"]["road"]["meetings"] == [] and not w2.s["people"]["Edric"]["transit"].get("notices")


def test_crossing_parties_meet_on_either_stretch_three_times_as_often_at_the_ford():
    w = world(roads=[["millbrook", "ashwood", 2, {"terrain": "plain", "stretches": {2: {"landmarks": ["ford"]}}}]])
    n = {1: 0, 2: 0}
    for i in range(3000):
        n[RD.meeting_stretch(w, "road:millbrook-ashwood", 1, 2, f"a{i}", "b")] += 1
    assert 2.5 < n[2] / n[1] < 3.6                                                       # D2-121


def test_a_promise_made_in_a_meeting_is_an_open_agreement_settled_later_at_a_node(monkeypatch):
    monkeypatch.setitem(RD.TERRAIN["woodland"], "meet", 1.0)
    w = world(roads=[["millbrook", "ashwood", 1, {"terrain": "woodland"}]])
    w.s["containers"][w.hands("Edric")]["goods"].update({"timber": 3.0})
    w.s["containers"][w.hands("Simkin")]["goods"]["coin"] = 0.0
    depart(w, "Edric", "ashwood")
    depart(w, "Simkin", "millbrook")
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    woke = FU.plan(w, w.s["today"])
    e = woke["Edric"]["events"][0]
    _, offers = RD.meeting_talk(w, e, {"Edric": {"offers": [{"to": "Simkin", "give": "1 timber", "get": "2 coin by day 6"}]}})
    oid = offers[0].split(":")[0]
    assert w.s["offers"][oid]["node"] == "road:millbrook-ashwood"                         # the road is the place (D2-120)
    FU.answer(w, w.s["today"], "Simkin", woke["Simkin"], {"actions": [{"do": "accept", "offer": oid}, {"do": "go on"}]})
    assert w.goods(w.hands("Simkin"))["timber"] == 1.0
    ag = next(a for a in w.s["agreements"].values() if a.get("offer") == oid)
    assert ag["status"] == "open" and ag["node"] == "road:millbrook-ashwood"
    assert any("2 coin to Edric, by day 6" in x for x in AG.lines(Here(w, "Simkin", transit=True), Mind(w, "Simkin")))
    N.night(w)
    assert not w.s["offers"][oid]["open"]                                                # offers on the road close when the meeting ends
    for d in range(2, 7):                                                                # Simkin at Millbrook, Edric at Ashwood: no path
        next_day(w)
        AG.settle(w)
    leg = next(l for l in ag["legs"] if l.get("item") == "coin")
    assert leg["arrears"] == 2.0                                                          # due on day 6, nobody to pay: in arrears
    w.s["people"]["Edric"]["at"] = w.at("Simkin")                                         # Edric comes to Millbrook
    w.s["containers"][w.hands("Simkin")]["goods"]["coin"] = 5.0
    next_day(w)
    AG.settle(w)
    assert ag["status"] == "done" and w.goods(w.hands("Edric")).get("coin", 0) >= 2.0


def test_exactly_one_person_in_a_seeded_world_knows_dibbling_and_teaching_spreads_it():
    w = world()
    knows = [n for n in w.living() if (w.s["know"].get(n) or {}).get("method: dibble", {}).get("level") == "known"]
    assert len(knows) == 1                                                               # D2-129
    t = knows[0]
    other = next(n for n in w.present(w.at(t)) if n != t and w.s["people"][n]["stage"] == "adult")
    do(w, t, do="teach", to=other, what="dibble")
    do(w, other, do="learn", **{"from": t, "what": "dibble"})
    ST.settle_teaching(w, w.s["today"])
    assert w.s["know"][other]["method: dibble"]["level"] in ("capable", "known")


# ---------------------------------------------------------------------- C2: the parcel graph (D2-114 to D2-116)
BF = load_spec("cybertron2/specs/barleyfield_a.yaml")


def barleyfield(**patch):
    s = copy.deepcopy(BF)
    s.update(patch)
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def test_a_farmer_working_a_far_field_passes_through_the_parcels_between_and_notices_from_next_door():
    from cybertron2.engine import layout as LY, things as TH
    w = barleyfield()
    name = next(n for n in w.living() if LY.slept_at(w, n) == "bf_green")
    assert LY.path(w, "bf_green", "south_field") == ["bf_green", "north_field", "east_field", "south_field"]
    w.s["today"]["worked"][name] = ["south_field"]
    assert {"north_field", "east_field"} <= LY.passed(w, name) and "south_field" not in LY.passed(w, name)
    assert TH.presence(w, name, "east_field", 0.4) == 0.3                                  # a pack on the way (D2-115)
    assert TH.presence(w, name, "brook_field", 0.95) == 0.1                                # a herd next door
    assert TH.presence(w, name, "brook_field", 0.4) == 0.0                                 # a pack next door: not seen from there
    assert TH.presence(w, name, "barley_wood", 0.4) == 0.0


def test_ties_between_shortest_ways_are_broken_by_a_keyed_draw():
    from cybertron2.engine import layout as LY
    w = barleyfield()
    w.s["parcels"]["bf_green"]["adj"].append("east_field")                                # two ways of 2 steps to south_field? no:
    w.s["parcels"]["east_field"]["adj"].append("bf_green")                                # green-east-south is now the only shortest
    assert LY.path(w, "bf_green", "south_field") == ["bf_green", "east_field", "south_field"]
    w.s["parcels"]["north_field"]["adj"].append("south_field")
    w.s["parcels"]["south_field"]["adj"].append("north_field")
    ways = {tuple(LY.path(w, "bf_green", "south_field", (k,))) for k in range(40)}
    assert ways == {("bf_green", "east_field", "south_field"), ("bf_green", "north_field", "south_field")}
    assert LY.path(w, "bf_green", "south_field", ("x",)) == LY.path(w, "bf_green", "south_field", ("x",))


def test_attending_to_the_village_lists_neighbours_sides_and_road_ends_and_an_arrival_gets_an_overview():
    from cybertron2.engine import perceive as PC
    s = copy.deepcopy(SPEC)
    s["roads"] = [["millbrook", "ashwood", 1, {"ends": {"millbrook": {"side": "east"}}}]]
    w = World(s)
    w.s["today"] = R.blank_today()
    name = next(n for n in w.living() if w.at(n) == "millbrook")
    pid = next(p for p in w.s["parcels"] if w.s["parcels"][p]["node"] == "millbrook" and w.s["parcels"][p]["adj"])
    w.s["parcels"][pid].update(side="north", height=2)
    here = Here(w, name)
    assert PC.resolve_target(here, "the village")[0] == "village"
    lines = here.layout()
    p = w.s["parcels"][pid]
    assert any(x.startswith(p["name"]) and "on the north side" in x and "on the slope" in x and "next to" in x for x in lines)
    assert any("leaves from" in x and "on the east side" in x for x in lines)
    PC.evening(w, {name: "the village"}, w.s["today"])
    att = w.s["mind"][name]["today"]["attended"]
    assert att["target"].startswith("how") and any("next to" in x for x in att["lines"])
    ov = here.overview()
    assert 3 <= len(ov) <= 5


# ---------------------------------------------------------------------- C3 to C6: fences, wandering, roads, splitting
def _fence(w, pid, kind="wood", level=2, gate="shut"):
    w.s["parcels"][pid]["fence"] = {"kind": kind, "units": 99.0, "level": level, "built": True, "gate": gate, "mend": 0.0, "pending": {}}


def _escapes(w, hid, days, **h):
    """Over many days, how often the herd leaves its parcel (each day from the same state)."""
    from cybertron2.engine import herds as HD
    start = dict(w.s["herds"][hid])
    out = 0
    for d in range(days):
        w.s["herds"][hid] = {**start, **h}
        w.s["day"] = 10 + d
        HD.wander(w, hid, {"herds": []})
        out += w.s["herds"][hid].get("parcel") != start["parcel"]
    w.s["herds"][hid] = start
    return out / days


def test_a_fenced_pasture_holds_its_herd_at_the_fences_odds_and_an_opened_gate_lets_it_out():
    w = barleyfield()
    w.s["parcels"]["bf_pasture"]["res"]["grass"]["S"] = 0.0                       # bare: they want to go
    _fence(w, "bf_pasture", "wood")
    assert 0.24 < _escapes(w, "cattle", 600, hungry=2) < 0.36                       # wood: 0.3 a day (D2-130)
    _fence(w, "bf_pasture", "stone")
    assert _escapes(w, "cattle", 600, hungry=2) < 0.09                              # stone: 0.05
    w.s["day"] = 3
    who = "Bennet"
    assert V.cost(Here(w, who), {"do": "work", "what": "open the gate", "at": "the Common"}) == 0
    r = do(w, who, do="work", what="open the gate", at="the Common")
    assert r.startswith("You opened the gate"), r
    assert any(e["kind"] == "gate" and e["actor"] == who for e in w.s["events"])     # seen by whoever is about (D2-132)
    assert _escapes(w, "cattle", 50, hungry=2) > 0.95


def test_a_household_that_notices_its_open_gate_shuts_it():
    from cybertron2.engine import perceive as PC
    w = barleyfield()
    _fence(w, "west_field", gate="open")                                            # the Barrows' field
    barrows = [n for n in w.living() if w.household_of(n) == "Barrow" and w.s["people"][n]["stage"] == "adult"]
    for d in range(6):                                                              # each day some notice it, by the rule
        w.s["today"] = R.blank_today()
        for n in barrows:
            w.s["today"]["worked"][n] = ["west_field"]
        PC.evening(w, {}, w.s["today"])
        if w.s["parcels"]["west_field"]["fence"]["gate"] == "shut":
            break
        w.s["day"] += 1
    assert w.s["parcels"]["west_field"]["fence"]["gate"] == "shut"
    assert any("you shut the gate of West Field" in w.s["mind"][n]["today"]["notice"] for n in barrows)


def test_a_wood_fence_unmended_loses_a_level_a_season_and_a_finished_fence_needs_its_materials():
    from cybertron2.engine import farm as FM, herds as HD
    w = barleyfield()
    w.s["containers"][w.hands("Bennet")]["goods"]["timber"] = 20.0
    r = do(w, "Bennet", do="work", what="fence", at="West Field")
    assert "worked on a fence round West Field" in r
    need = FM.fence_need(w.s["parcels"]["west_field"], "wood")
    used = 20.0 - w.goods(w.hands("Bennet"))["timber"]                              # in proportion to the work done (bare hands: half)
    assert 0 < used <= need["inputs"]["timber"] / need["units"] + 1e-6
    HD._fences(w, {"herds": []})
    assert w.s["parcels"]["west_field"]["fence"]["units"] > 0
    _fence(w, "west_field")
    w.s["day"] = w.calendar()["left"] - 1 + w.d if False else w.s["day"]
    while w.calendar(w.d + 1)["season"] == w.calendar()["season"]:
        w.s["day"] += 1
    HD._fences(w, {"herds": []})
    assert w.s["parcels"]["west_field"]["fence"]["level"] == 1                      # a season unmended


def test_a_hungry_unherded_herd_crosses_several_parcels_and_tramples_a_field_while_a_fed_one_stays():
    from cybertron2.engine import herds as HD
    w = barleyfield()
    w.s["day"] = 3                                                                  # the barley in North Field is ripe
    w.s["parcels"]["bf_pasture"]["res"]["grass"]["S"] = 0.0
    w.s["herds"]["cattle"]["hungry"] = 2
    before = w.s["parcels"]["north_field"]["crop"]["left"]
    way = HD.wander(w, "cattle", {"herds": []})
    assert len(way) >= 2 and w.s["herds"]["cattle"]["parcel"] == "north_field"
    c = w.s["parcels"]["north_field"]["crop"]
    assert abs(before - c["left"] - before * 0.01 * 8) < 0.01 and c["trampled"]["by"] == "cattle"   # 1% a head (D2-123)
    w2 = barleyfield()
    w2.s["parcels"]["north_field"]["crop"]["ripe_day"] = 60
    assert _escapes(w2, "cattle", 100, hungry=0) < 0.25                             # fed on good pasture: mostly stays (D2-123)


def test_a_herd_on_a_road_drifts_loses_head_and_a_searcher_finds_it_far_more_often(monkeypatch):
    from cybertron2.engine import herds as HD
    from cybertron2.engine.data import HERDS
    w = world(roads=[["millbrook", "ashwood", 3, {"terrain": "woodland"}]])
    rid = "road:millbrook-ashwood"
    HD.onto_road(w, "cattle", rid, "millbrook", {"herds": []})
    w.apply("set", rid, ref=("herd", "cattle"), field="pos", value=2)
    monkeypatch.setitem(HERDS["road"], "gone", 0.0)
    start = dict(w.s["herds"]["cattle"], cows=10, oxen=0, bulls=0, young=0)
    lost, moved = {"winter": [], "else": []}, 0
    for d in range(800):
        w.s["herds"]["cattle"] = dict(start)
        w.s["day"] = 10 + d
        HD._on_road(w, "cattle", {"herds": []})
        h = w.s["herds"]["cattle"]
        lost["winter" if w.calendar()["season"] == "winter" else "else"].append(10 - FM_head(h))
        moved += h.get("pos") != 2
    mean = {k: sum(v) / len(v) for k, v in lost.items()}
    assert 1.3 < mean["else"] < 1.7 and 2.6 < mean["winter"] < 3.4 and moved == 800   # 0.15 a head a day, 0.3 in winter (D2-124)
    w.s["herds"]["cattle"] = dict(start)
    depart(w, "Edric", "ashwood", searching="the Millbrook cattle")
    depart(w, "Sibyl", "ashwood")
    from cybertron2.engine import roads as RD
    N.departures(w, w.s["today"])
    assert RD.searching_for(w, "Edric", "cattle") and not RD.searching_for(w, "Sibyl", "cattle")
    assert RD.herd_chance(w, "Edric", "cattle", 2) >= 3 * RD.herd_chance(w, "Sibyl", "cattle", 2)   # x5, capped at 1 (D2-125)


def FM_head(h):
    from cybertron2.engine import farm as FM
    return FM.head(h)


def test_a_found_herd_taken_along_arrives_with_the_party_and_is_held_by_the_taker(monkeypatch):
    from cybertron2.engine import herds as HD, roads as RD
    w = world(roads=[["millbrook", "ashwood", 1, {"terrain": "plain"}]])
    rid = "road:millbrook-ashwood"
    HD.onto_road(w, "cattle", rid, "millbrook", {"herds": []})
    monkeypatch.setattr(RD.TH, "eye", lambda w, n, on="things": 3.0)
    depart(w, "Simkin", "millbrook")                                                # from Ashwood
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    woke = FU.plan(w, w.s["today"])
    assert woke["Simkin"]["events"][0]["kind"] == "herd"
    FU.answer(w, w.s["today"], "Simkin", woke["Simkin"], {"actions": [{"do": "accompany"}]})
    assert w.s["herds"]["cattle"]["with"] == "Simkin"
    assert any(c["claimant"] in ("Simkin", w.household_of("Simkin")) and c["grounds"] == "found" for c in w.claims_on(("herd", "cattle")))
    next_day(w)
    assert w.at("Simkin") == "millbrook" and w.s["herds"]["cattle"]["node"] == "millbrook" and w.s["herds"]["cattle"]["parcel"]


def test_twenty_head_split_about_a_tenth_a_day_with_one_drover_almost_never_with_two_and_shares_peak_near_a_quarter():
    import random
    from cybertron2.engine import herds as HD
    assert abs(HD.split_chance(20, 10) - 0.1) < 1e-9 and HD.split_chance(20, 20) == 0.01           # D2-128
    rng = random.Random(7)
    xs = [HD.share(rng) for _ in range(20000)]
    bins = [sum(a < x <= b for x in xs) / len(xs) for a, b in ((0, 1 / 16), (1 / 16, 1 / 8), (1 / 8, 1 / 5), (1 / 5, 1 / 3), (1 / 3, 1 / 2))]
    assert max(xs) <= 0.5 and 0.40 < bins[3] < 0.50 and 0.20 < bins[2] < 0.28 and bins[0] < 0.05      # D2-131
    w = world()
    h = w.s["herds"]["cattle"]
    h.update(cows=20, oxen=0, bulls=0, young=0, count=20, with_=None)
    splits = 0
    for d in range(300):
        w.s["day"] = d
        w.s["herds"] = {"cattle": dict(h)}
        splits += bool(HD.split(w, "cattle", {"herds": []}, drove=1))
    assert 0.06 < splits / 300 < 0.15


# ---------------------------------------------------------------------- C7: hidden ways (D2-90, D2-92, D2-98)
def test_a_hidden_way_in_a_wood_is_found_by_hunters_over_weeks_and_felling_the_wood_exposes_it():
    from cybertron2.engine import layout as LY
    roads = [["millbrook", "ashwood", 1, {"ends": {"millbrook": {"parcels": ["alder_copse"], "side": "north", "hidden": True}}}]]
    w = world(roads=roads, weather={d: "clear" for d in range(1, 400)})
    rid = "road:millbrook-ashwood"
    hunters = ["Edric", "Hamo", "Odo"]
    assert all(not any(r[0] == "ashwood" for r in Here(w, n).roads()) for n in hunters)   # not in "Roads from here" (D2-90)
    first = None
    for d in range(1, 300):
        w.s["day"] = d
        w.s["events"] = [{"actor": n, "kind": "work", "day": d, "about": ["parcel:alder_copse"], "tech": "hunt"} for n in hunters]
        found = [n for n in hunters if LY.find_ways(w, n, w.rng("test-way", d, n))]
        if found:
            first = d
            break
    assert first is not None and first > 5                                         # weeks, not days (own 0.03 x the wood's sight)
    assert any(r[0] == "ashwood" for r in Here(w, found[0]).roads())
    assert not any(r[0] == "ashwood" for r in Here(w, "Sibyl").roads())             # the others do not know it
    w2 = world(roads=roads, weather={d: "clear" for d in range(1, 400)})
    w2.s["parcels"]["alder_copse"]["res"]["wood"]["S"] = 0.1 * w2.s["parcels"]["alder_copse"]["res"]["wood"]["K"]
    assert LY.way_own(w2, rid, "millbrook") == 0.8 and LY.opened(w2, "alder_copse")
    days = []
    for n in hunters:
        for d in range(1, 30):
            w2.s["day"] = d
            w2.s["events"] = [{"actor": n, "kind": "work", "day": d, "about": ["parcel:alder_copse"], "tech": "fell"}]
            if LY.find_ways(w2, n, w2.rng("test-way2", d, n)):
                days.append(d)
                break
    assert days and max(days) <= 6                                                 # felled, it shows to anyone working there


def test_a_hidden_way_is_worn_by_use_and_told():
    from cybertron2.engine import layout as LY
    roads = [["millbrook", "ashwood", 1, {"ends": {"millbrook": {"parcels": ["alder_copse"], "hidden": True}}}]]
    w = world(roads=roads)
    rid = "road:millbrook-ashwood"
    base = LY.way_own(w, rid, "millbrook")
    LY.wear_way(w, rid, "millbrook")
    assert abs(LY.way_own(w, rid, "millbrook") - base - 0.05) < 1e-9
    LY.learn_way(w, "Edric", rid, "millbrook", "found")
    R._mentions(w, Here(w, "Edric"), "Edric", ["Sibyl"], "There is a path out through Alder Copse, north.")
    assert LY.way_known(w, "Sibyl", rid, "millbrook")


def test_an_arriving_traveller_gets_an_overview_in_its_turn():
    from cybertron2.engine import prompt as PR
    w = world(roads=[["millbrook", "ashwood", 1, {"terrain": "plain"}]])
    depart(w, "Edric", "ashwood")
    N.departures(w, w.s["today"])
    next_day(w)
    assert w.at("Edric") == "ashwood"
    text = PR.turn_prompt(Here(w, "Edric"), Mind(w, "Edric"))
    line = next(x for x in text.splitlines() if "Arriving, what you see first" in x or "Arriving, what you see first" in x)
    assert 3 <= line.count(";") + 1 <= 5                                          # D2-116


def test_a_finder_knows_its_own_beasts_and_its_neighbours_but_not_strangers():
    from cybertron2.engine import roads as RD
    w = world()
    hid = "cattle"
    holder = w.claims_on(("herd", hid))[0]["claimant"]
    own = next(n for n in w.living() if holder in (n, w.household_of(n)))
    assert "your own" in RD.whose_herd(w, own, hid)
    neighbour = next(n for n in w.living() if w.at(n) == w.at(own) and holder not in (n, w.household_of(n)))
    assert "You know them" in RD.whose_herd(w, neighbour, hid)
    stranger = next(n for n in w.living() if w.at(n) != w.at(own))
    assert "cannot tell" in RD.whose_herd(w, stranger, hid)


# ---------------------------------------------------------------------- dead beasts (D4-52)
def test_a_beast_that_starves_leaves_a_carcass_fit_to_eat_for_a_day_then_gone_off():
    from cybertron2.engine import farm as FM, things as TH
    w = world()
    h = w.s["herds"]["cattle"]
    h.update(hungry=9, watched=w.d)                                                # herded on a bare pasture: it starves there
    w.s["parcels"][h["parcel"]]["res"]["grass"]["S"] = 0.0
    FM.night(w)
    cs = [c for c in w.s["containers"].values() if c["kind"] == "carcass"]
    assert len(cs) == 1 and cs[0]["parcel"] == h["parcel"] and cs[0]["beast"] == "cow"
    assert abs(cs[0]["goods"]["meat"] - 40 * 0.25) < 1e-9                         # starved: a quarter of slaughter's meat (calibrate)
    assert cs[0]["kind"] in TH.KINDS and TH.carcass_fresh(w, cs[0])
    w.s["day"] += 1
    assert TH.carcass_fresh(w, cs[0])                                               # the next day: still good
    N.night(w)
    assert cs[0]["goods"].get("meat", 0) == 0 and cs[0]["goods"].get("rotting meat", 0) > 0 and not TH.carcass_fresh(w, cs[0])


def test_beasts_dying_on_the_road_leave_nothing_a_hidden_carcass_or_one_by_the_road():
    from cybertron2.engine import herds as HD
    w = world(roads=[["millbrook", "ashwood", 2, {"terrain": "plain"}]])
    rid = "road:millbrook-ashwood"
    out = {"none": 0, "hidden": 0, "open": 0}
    for k in range(600):
        cid = HD._road_carcass(w, "cattle", "cows", rid, 1, w.rng("t-carcass", k))
        if not cid:
            out["none"] += 1
        else:
            out["hidden" if w.s["containers"][cid].get("hidden") else "open"] += 1
    assert 0.25 < out["none"] / 600 < 0.35 and 0.25 < out["hidden"] / 600 < 0.35       # D4-52 (calibrate)
    c = next(c for c in w.s["containers"].values() if c["kind"] == "carcass" and not c.get("hidden"))
    h = next(c for c in w.s["containers"].values() if c["kind"] == "carcass" and c.get("hidden"))
    from cybertron2.engine import things as TH
    assert TH.own(w, h) < TH.own(w, c) * 0.3
    assert c in RD_things(w, rid, 1)


def RD_things(w, rid, pos):
    from cybertron2.engine import roads as RD
    return list(RD.things_on(w, rid, pos).values())


def test_a_trampled_field_shows_it_after_the_beasts_have_gone_home():
    from cybertron2.engine import herds as HD, perceive as PC
    w = barleyfield()
    w.s["day"] = 3
    w.s["parcels"]["bf_pasture"]["res"]["grass"]["S"] = 0.0
    w.s["herds"]["cattle"]["hungry"] = 2
    HD.wander(w, "cattle", {"herds": []})
    assert w.s["parcels"]["north_field"]["crop"]["trampled"]["day"] == 3
    texts = [f["text"] for f in PC.facts(Here(w, "Ancel"))]
    assert any("hoof-marks and flattened barley in North Field" in t for t in texts)


# ---------------------------------------------------------------------- the pack ox (D2-135, D2-136)
def test_a_pack_ox_carries_60_goes_with_its_leader_grazes_or_eats_hay_and_comes_in_with_it():
    from cybertron2.engine import herds as HD, roads as RD
    w = world(roads=[["millbrook", "ashwood", 2, {"terrain": "woodland", "stretches": {2: {"terrain": "farmland"}}}]])
    holder = w.claims_on(("herd", "cattle"))[0]["claimant"]
    lead = next(n for n in w.living() if w.at(n) == "millbrook" and holder in (n, w.household_of(n)) and w.s["people"][n]["stage"] == "adult")
    g = w.s["containers"][w.hands(lead)]["goods"]
    g.update(harness=1.0, hay=2.0, grain=40.0)
    w.s["herds"]["cattle"]["oxen"] = 2
    assert do(w, lead, do="travel", to="ashwood").startswith("Refused")               # 40 grain is too heavy on foot
    oxen_before = w.s["herds"]["cattle"]["oxen"]
    r = do(w, lead, do="travel", to="ashwood", lead="the cattle")
    assert r.startswith("You set off"), r
    N.departures(w, w.s["today"])
    ox = next(hid for hid, h in w.s["herds"].items() if h.get("pack"))
    assert w.s["herds"]["cattle"]["oxen"] == oxen_before - 1 and w.s["herds"][ox]["with"] == lead
    assert w.capacity(lead) == 60
    RD.night(w, w.s["today"])                                                       # woodland: no grass, so 1 hay
    assert abs(w.goods(w.hands(lead))["hay"] - 1.0) < 1e-9
    next_day(w)
    w.s["today"] = R.blank_today()
    RD.night(w, w.s["today"])                                                       # farmland: it grazes
    assert abs(w.goods(w.hands(lead))["hay"] - 1.0) < 1e-9
    next_day(w)
    assert w.at(lead) == "ashwood" and w.s["herds"][ox]["node"] == "ashwood" and w.s["herds"][ox]["pack_of"] == lead
    assert ox in w.s["mind"][lead].get("beasts", {})                                # its leader knows it came in, and where it is
    assert w.capacity(lead) < 60 and do(w, lead, do="travel", to="millbrook", lead="the cattle").startswith("You set off")   # to lead on


def test_an_offer_to_a_child_goes_to_the_childs_parent():
    from cybertron2.engine.world import World, load_spec
    w = World(load_spec("cybertron2/specs/region_c1.yaml"))
    w.s["today"] = R.blank_today()
    child = "Walter"
    kin = w.s["mind"][child]["kin"]
    parent = next(m for rel in ("your mother", "your father") for m, k in kin.items() if k["rel"] == rel and w.at(m) == w.at(child))
    offerer = next(n for n in w.living() if w.at(n) == w.at(child) and w.s["people"][n]["stage"] == "adult" and w.household_of(n) != w.household_of(child))
    w.s["containers"][w.hands(offerer)]["goods"]["grain"] = 5.0
    names = [n for n in w.living() if w.s["people"][n]["stage"] != "child"]
    replies = {n: {} for n in names}
    replies[offerer] = {"offers": [{"to": child, "give": "2 grain", "get": "1 timber"}]}
    results = {n: [] for n in names}
    box = R.talk(w, names, replies, results)
    assert any("goes to" in x and child in x for x in results[offerer])
    assert box[parent]["offers"] and any(o["to"] in (parent,) for o in w.s["offers"].values() if o["by"] == offerer)
