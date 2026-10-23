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
