"""Package B (37.2's brief 02r §3): roads with stretches and landmarks, trouble and choices at departure, experience, meetings with a
conversation, finds, "On the way", and an edge with no landmarks behaving as before (D2-81, D2-86, D2-97, D2-104 to D2-113)."""
import copy
import json

from cybertron2.engine import fuse as FU, night as N, roads as RD, run as R
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


def next_night(w):
    """Dawn of the next day (arrivals), then nightfall: departures, the roads."""
    w.s["day"] += 1
    w.s["events"] = []
    w.s["today"] = R.blank_today()
    R.dawn(w)


def depart(w, who, to, **choices):
    w.s["today"].setdefault("travel", {})[who] = to
    if choices:
        w.s["today"].setdefault("travel_choices", {})[who] = choices


WOOD = {"terrain": "woodland"}


def test_a_one_day_road_two_parties_leaving_opposite_ends_meet_on_stretch_1(monkeypatch):
    monkeypatch.setitem(RD.TERRAIN["woodland"], "meet", 1.0)
    w = world(roads=[["millbrook", "ashwood", 1, WOOD]])
    depart(w, "Edric", "ashwood")
    depart(w, "Simkin", "millbrook")
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    m = w.s["today"]["road"]["meetings"]
    assert len(m) == 1 and m[0]["pos"] == 1 and sorted(sum(m[0]["parties"], [])) == ["Edric", "Simkin"]


def test_a_three_day_road_parties_leaving_days_apart_cross_on_the_right_stretch(monkeypatch):
    monkeypatch.setitem(RD.TERRAIN["woodland"], "meet", 1.0)
    w = world(roads=[["millbrook", "ashwood", 3, WOOD]])
    depart(w, "Edric", "ashwood")                                   # day 1 from the a end
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    assert w.s["today"]["road"]["meetings"] == []
    next_night(w)
    depart(w, "Simkin", "millbrook")                                # day 2 from the b end
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])                                       # Edric on 2, Simkin on 3 (from a): not yet
    assert w.s["today"]["road"]["meetings"] == []
    next_night(w)
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])                                       # Edric on 3, Simkin on 2: they crossed
    m = w.s["today"]["road"]["meetings"]
    assert len(m) == 1 and m[0]["pos"] == 3


FORD = {"terrain": "river valley", "stretches": {1: {"landmarks": ["ford"]}}}


def test_a_high_ford_with_no_choice_waits_a_day_and_says_so_on_arrival(monkeypatch):
    monkeypatch.setitem(RD.ROADS["call"], "minor", 0.0)
    w = world(roads=[["millbrook", "ashwood", 1, FORD]], weather={1: "heavy rain"})
    depart(w, "Edric", "ashwood")
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    t = w.s["people"]["Edric"]["transit"]
    assert t["arrive"] == 2 and any("ford was high" in x for x in t["notices"])
    next_night(w)
    assert w.at("Edric") is None                                    # still waiting at the ford
    for _ in range(4):                                              # high two days after heavy rain (world/roads.md)
        N.departures(w, w.s["today"])
        RD.night(w, w.s["today"])
        next_night(w)
        if w.at("Edric"):
            break
    assert w.at("Edric") == "ashwood"
    assert any("ford was high" in x for x in w.s["mind"]["Edric"]["on_the_way"]["lines"])


def test_pushing_on_at_a_high_ford_with_a_cart_risks_a_fifth_of_the_load(monkeypatch):
    monkeypatch.setitem(RD.ROADS["call"], "minor", 0.0)
    monkeypatch.setitem(RD.LANDMARKS["ford"]["push"], "cart_loss", [1.0, 0.2])
    w = world(roads=[["millbrook", "ashwood", 1, FORD]], weather={1: "heavy rain"})
    w.s["containers"][w.hands("Edric")]["goods"].update({"handcart": 1.0, "grain": 20.0})
    depart(w, "Edric", "ashwood", **{"on trouble": "push on"})
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    assert abs(w.goods(w.hands("Edric"))["grain"] - 16.0) < 1e-6
    assert w.s["people"]["Edric"]["transit"]["arrive"] == 1


def test_experience_halves_trouble_and_a_call_comes_only_when_the_risk_is_serious(monkeypatch):
    w = world(roads=[["millbrook", "ashwood", 1, FORD]])
    key = RD.landmark_key("road:millbrook-ashwood", 1, "ford")
    w.s["mind"]["Edric"]["landmarks"] = {key: {"crossed": 5, "words": "a ford", "road": "road:millbrook-ashwood", "pos": 1, "kind": "ford"}}
    assert abs(RD.experience(w, "Edric", key) - 0.5) < 1e-9
    assert RD.experience(w, "Sibyl", key) == 1.0
    w2 = world(roads=[["millbrook", "ashwood", 1, {"terrain": "hills", "stretches": {1: {"landmarks": ["pass"]}}}]],
               weather={1: "snow"}, calendar={"season": "winter", "day": 1, "season_days": 6})
    monkeypatch.setitem(RD.ROADS["call"], "minor", 0.0)
    depart(w2, "Edric", "ashwood")
    N.departures(w2, w2.s["today"])
    RD.night(w2, w2.s["today"])
    calls = w2.s["today"]["road"]["crossings"]
    assert (calls and calls[0]["risk"]["death"] >= 0.05) or any("turned back" in x for x in w2.s["people"]["Edric"]["transit"]["notices"])


def test_a_meeting_gives_each_one_call_a_conversation_and_an_offer_settles_from_hands(monkeypatch):
    monkeypatch.setitem(RD.TERRAIN["woodland"], "meet", 1.0)
    w = world(roads=[["millbrook", "ashwood", 1, WOOD]])
    w.s["containers"][w.hands("Edric")]["goods"].update({"grain": 5.0})
    w.s["containers"][w.hands("Simkin")]["goods"].update({"timber": 4.0})
    depart(w, "Edric", "ashwood")
    depart(w, "Simkin", "millbrook")
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    woke = FU.plan(w, w.s["today"])
    assert set(woke) == {"Edric", "Simkin"} and all(x["acts"] == 3 for x in woke.values())
    e = woke["Edric"]["events"][0]
    said, offers = RD.meeting_talk(w, e, {"Edric": {"say": [{"to": "everyone", "text": "Good day."}],
                                                     "offers": [{"to": "Simkin", "give": "3 grain", "get": "2 timber"}]}})
    assert said == ["Edric: Good day."] and offers and offers[0].startswith("R1")
    out = FU.answer(w, w.s["today"], "Simkin", woke["Simkin"], {"actions": [{"do": "accept", "offer": "R1"}, {"do": "turn back"}]})
    assert w.goods(w.hands("Simkin"))["grain"] == 3.0 and w.goods(w.hands("Edric"))["timber"] == 2.0
    t = w.s["people"]["Simkin"]["transit"]
    assert t["to"] == "ashwood" and t["arrive"] == w.d + 1                    # turned back: home at the next dawn
    assert FU.plan(w, w.s["today"]) == {}                                      # one call a day on the road


def test_a_find_on_the_road_is_a_call_only_if_noticed_and_the_finder_can_take_it(monkeypatch):
    w = world(roads=[["millbrook", "ashwood", 1, {"terrain": "plain"}]])
    w.s["containers"]["remains:x"] = {"kind": "remains", "of": "Hugh", "node": "road:millbrook-ashwood", "stretch": 1, "goods": {"grain": 6.0},
                                      "wear": {}, "body": True, "died": 0, "parcel": None}
    monkeypatch.setattr(RD.TH, "eye", lambda w, n, on="things": 3.0)
    depart(w, "Edric", "ashwood")
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    woke = FU.plan(w, w.s["today"])
    assert "Edric" in woke
    FU.answer(w, w.s["today"], "Edric", woke["Edric"], {"actions": [{"do": "take"}]})
    assert w.goods(w.hands("Edric")).get("grain", 0) >= 6.0


def test_an_edge_with_no_landmarks_behaves_exactly_as_before(tmp_path, monkeypatch):
    """D2-104: a road without terrain or landmarks holds nothing; a run is the same as with the roads step switched off."""
    spec = copy.deepcopy(SPEC)
    spec["days"] = 6
    for a in spec["agents"].values():
        if a.get("model"):
            a["model"] = "bot"
    import yaml
    p = tmp_path / "s.yaml"
    p.write_text(yaml.safe_dump(spec))
    R.run(str(p), str(tmp_path / "a"), workers=2)
    monkeypatch.setattr(RD, "night", lambda w, today: {"trouble": [], "meetings": [], "finds": [], "good": []})
    R.run(str(p), str(tmp_path / "b"), workers=2)
    strip = lambda f: [json.dumps({k: v for k, v in json.loads(l).items() if k != "road"}) for l in open(f)]
    assert strip(tmp_path / "a" / "days.jsonl") == strip(tmp_path / "b" / "days.jsonl")
    assert any(d["departed"] for d in map(json.loads, open(tmp_path / "a" / "days.jsonl")))


def test_traces_left_by_a_party_fade_and_are_read_by_a_later_traveller(monkeypatch):
    w = world(roads=[["millbrook", "ashwood", 2, {"terrain": "plain"}]], weather={1: "clear", 2: "clear", 3: "clear"})
    w.s["containers"][w.hands("Edric")]["goods"]["handcart"] = 1.0
    depart(w, "Edric", "ashwood")
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    assert {x["kind"] for x in w.s["traces"]} == {"tracks", "ruts"}
    next_night(w)
    depart(w, "Sibyl", "ashwood")
    monkeypatch.setattr(RD.TH, "eye", lambda w, n, on="things": 3.0)
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    assert any("going toward Ashwood, a day old" in x for x in w.s["people"]["Sibyl"]["transit"]["notices"])


def test_a_meeting_on_the_road_calls_llm_agents_in_their_own_conversation(tmp_path, monkeypatch):
    from cybertron import llm
    sent = []

    def fake_call(backend, model, system, user, schema, **kw):
        text = str(user).split("Plan your day")[-1]
        sent.append(text)
        if "## On the road" in text and "meeting goes on" not in text:
            return {"why": "x", "actions": [{"do": "go on"}], "say": [{"to": "everyone", "text": "Well met."}]}, None, {"cc_equiv_usd": 0.0}
        return {"why": "x", "actions": [{"do": "travel", "to": "Ashwood"}] if "Millbrook" in text else []}, None, {"cc_equiv_usd": 0.0}
    monkeypatch.setattr(llm, "call", fake_call)
    monkeypatch.setitem(RD.TERRAIN["woodland"], "meet", 1.0)
    spec = copy.deepcopy(SPEC)
    spec["days"] = 2
    spec["roads"] = [["millbrook", "ashwood", 1, {"terrain": "woodland"}]]
    for n, a in spec["agents"].items():
        if a.get("model"):
            a["model"] = "bot"
    spec["agents"]["Edric"]["model"] = "claude-haiku-5-5"
    spec["agents"]["Simkin"]["model"] = "claude-haiku-5-5"
    spec["script"] = [{"day": 1, "who": "Edric", "do": {"do": "travel", "to": "Ashwood"}},
                      {"day": 1, "who": "Simkin", "do": {"do": "travel", "to": "Millbrook"}}]
    import yaml
    p = tmp_path / "s.yaml"
    p.write_text(yaml.safe_dump(spec))
    R.run(str(p), str(tmp_path / "out"), backend="api", workers=2)
    rows = [json.loads(l) for l in open(tmp_path / "out" / "turns.jsonl")]
    calls = [x for r in rows if r["agent"] in ("Edric", "Simkin") for x in r.get("talk", []) if x.get("wave") == "fuse"]
    assert calls and all(not x.get("error") for x in calls)
    assert any("meeting goes on" in t for t in sent)                   # a second wave: what the other said


def test_in_one_call_a_take_goes_to_the_find_not_the_meeting(monkeypatch):
    monkeypatch.setitem(RD.TERRAIN["plain"], "meet", 1.0)
    monkeypatch.setattr(RD.TH, "eye", lambda w, n, on="things": 3.0)
    w = world(roads=[["millbrook", "ashwood", 1, {"terrain": "plain"}]])
    w.s["containers"]["pile:r"] = {"kind": "pile", "node": "road:millbrook-ashwood", "stretch": 1, "goods": {"grain": 4.0}, "wear": {},
                                   "parcel": None, "day": 0}
    depart(w, "Edric", "ashwood")
    depart(w, "Simkin", "millbrook")
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    woke = FU.plan(w, w.s["today"])
    n = next(k for k, x in woke.items() if len(x["events"]) == 2)
    out = FU.answer(w, w.s["today"], n, woke[n], {"actions": [{"do": "take"}, {"do": "go on"}]})
    assert out[0].startswith("You took") and w.goods(w.hands(n)).get("grain", 0) >= 4.0


def test_a_party_that_chose_not_to_stop_passes_a_meeting_on_its_own(monkeypatch):
    monkeypatch.setitem(RD.TERRAIN["woodland"], "meet", 1.0)
    w = world(roads=[["millbrook", "ashwood", 1, WOOD]], weather={1: "clear"})
    depart(w, "Edric", "ashwood", meeting="pass by")
    depart(w, "Simkin", "millbrook")
    N.departures(w, w.s["today"])
    RD.night(w, w.s["today"])
    assert w.s["today"]["road"]["meetings"] == [] and FU.plan(w, w.s["today"]) == {}         # no call (D4-51)
    e, s = w.s["people"]["Edric"]["transit"]["notices"], w.s["people"]["Simkin"]["transit"]["notices"]
    assert any("you passed Simkin" in x or "Simkin" in x for x in e)
    assert any("Edric" in x and ("without stopping" in x or "did not stop" in x or "far side" in x or "loads" in x) for x in s)
