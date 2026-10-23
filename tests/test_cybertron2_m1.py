"""cybertron2 M1 (one node): a scripted-bot run is deterministic and exercises talk, teaching, perception and the night."""
import json

from cybertron2.m1 import knowledge as KN
from cybertron2.m1.run import run
from cybertron2.m1.world import World, load_spec

SPEC = "cybertron2/specs/m1_founders.yaml"


def test_bot_run_deterministic(tmp_path):
    a = run(SPEC, tmp_path / "a", days=4, bots=True)
    b = run(SPEC, tmp_path / "b", days=4, bots=True)
    sa, sb = json.load(open(a / "state.json")), json.load(open(b / "state.json"))
    assert sa == sb
    turns = [json.loads(x) for x in open(a / "turns.jsonl")]
    assert any(t["talk_prompt"] for t in turns)
    assert any("taught you" in " ".join(t["results"]) for t in turns)
    assert any("## What happened yesterday" in t["prompt"] for t in turns if t["day"] > 0)


def test_knowledge_paths():
    w = World(load_spec(SPEC))
    assert KN.level(w, "Ivy", "milk") == "aware" and KN.level(w, "Wat", "milk") is None
    assert KN.level(w, "Wat", "hunt") == "known"                               # basic (D2-43)
    for _ in range(3):
        KN.saw(w, "Wat", "milk", "Maud")
    assert KN.level(w, "Wat", "milk") == "rough"
    assert KN.explained(w, "Maud", "Tam", "milk") == ""
    assert KN.level(w, "Tam", "milk") == "rough"
    KN.taught(w, "Maud", "Ivy", "milk")
    assert KN.level(w, "Ivy", "milk") == "known"                              # a youth learns faster
    assert KN.rec(w, "Ivy", "milk")["source"] == "Maud taught you"


def test_offer_goods_set_aside_and_returned():
    from cybertron2.m1 import act as AC, run as R
    w = World(load_spec(SPEC))
    w.s["today"] = R._blank_today()
    w.s["agents"]["Osric"]["holdings"]["grain"] = 4
    names = w.agents_acting()
    res = {n: [] for n in names}
    R.talk(w, names, {**{n: {} for n in names}, "Osric": {"offers": [{"to": "Agnes", "give": "4 grain", "get": "1 timber"}],
                                                          "say": [{"to": "Reed House", "text": "grain for timber"}],
                                                          "tell": [{"to": "Agnes", "text": "grain for timber"}]}}, res)
    assert w.s["agents"]["Osric"]["holdings"]["grain"] == 0                  # set aside
    assert any(x.startswith("You said (in Reed House)") for x in res["Osric"]) and any(x.startswith("You told Agnes") for x in res["Osric"])
    oid = next(iter(w.s["offers"]))
    w.s["agents"]["Agnes"]["holdings"]["timber"] = 1
    assert AC.do(w, "Agnes", {"do": "accept", "offer": oid}, w.s["today"]).startswith("You accepted")
    assert w.s["agents"]["Agnes"]["holdings"]["grain"] == 4 and w.s["agents"]["Osric"]["holdings"]["timber"] == 1
    R.talk(w, names, {**{n: {} for n in names}, "Agnes": {"offers": [{"to": "anyone", "give": "2 grain", "get": "1 bread"}]}}, res)
    assert w.s["agents"]["Agnes"]["holdings"]["grain"] == 4                  # an offer to anyone is not set aside
    oid2 = [k for k, o in w.s["offers"].items() if o["to"] is None][0]
    w.night()
    assert w.s["offers"][oid2]["open"]                                       # open today and tomorrow
    w.s["day"] += 1
    w.night()
    assert not w.s["offers"][oid2]["open"]


def test_move_to_named_own_house_stores():
    from cybertron2.m1 import act as AC, run as R
    w = World(load_spec(SPEC))
    today = R._blank_today()
    w.s["agents"]["Osric"]["holdings"]["bread"] = 3
    before = w.s["houses"]["reed_house"]["stock"].get("bread", 0)
    assert AC.do(w, "Osric", {"do": "move", "item": "bread", "qty": 3, "to": "Reed House"}, today).startswith("You put")
    assert w.s["houses"]["reed_house"]["stock"]["bread"] == before + 3
    assert AC.do(w, "Osric", {"do": "move", "item": "bread", "qty": 1, "to": "hands"}, today).startswith("You took")
    assert AC.do(w, "Osric", {"do": "move", "item": "bread", "qty": 1, "to": "Fenn House"}, today).startswith("Refused")


def test_accept_pays_from_own_store():
    from cybertron2.m1 import act as AC, run as R
    w = World(load_spec(SPEC))
    w.s["today"] = R._blank_today()
    names = w.agents_acting()
    w.s["agents"]["Agnes"]["holdings"]["meat"] = 2
    w.s["houses"]["reed_house"]["stock"]["grain"] = 5
    R.talk(w, names, {**{n: {} for n in names}, "Agnes": {"offers": [{"to": "Osric", "give": "2 meat", "get": "3 grain"}]}}, {n: [] for n in names})
    oid = next(iter(w.s["offers"]))
    assert w.s["agents"]["Osric"]["holdings"].get("grain", 0) < 3 <= w.s["agents"]["Osric"]["holdings"].get("grain", 0) + w.s["houses"]["reed_house"]["stock"]["grain"]
    assert AC.do(w, "Osric", {"do": "accept", "offer": oid}, w.s["today"]).startswith("You accepted")
    assert w.s["agents"]["Osric"]["holdings"]["meat"] == 2


def test_only_direct_speech_wakes():
    from cybertron2.m1 import run as R
    w = World(load_spec(SPEC))
    w.s["today"] = R._blank_today()
    names = w.agents_acting()
    res = {n: [] for n in names}
    woken, quiet = R.talk(w, names, {**{n: {} for n in names}, "Osric": {
        "say": [{"to": "everyone", "text": "the barley is ripe"}, {"to": "Reed House", "text": "reap with me"}],
        "tell": [{"to": "Agnes", "text": "timber for grain?"}]}}, res)
    assert set(woken) == {"Agnes"}                                       # told directly
    assert any("in Reed House" in x for x in quiet["Maud"]) and not any("in Reed House" in x for x in quiet["Tam"])
    assert any("to everyone" in x for x in quiet["Tam"])


def test_say_in_any_building_by_access():
    from cybertron2.m1 import run as R
    spec = load_spec(SPEC)
    spec["buildings"] = {"hall": {"name": "the Hall", "parcel": "green", "access": "public"},
                         "barn": {"name": "the Barn", "parcel": "green", "access": ["Osric", "Tam"]}}
    spec["houses"]["fenn_house"]["access"] = ["Wat"]                         # a neighbour's boy let into Fenn House
    w = World(spec)
    w.s["today"] = R._blank_today()
    names = w.agents_acting()
    res = {n: [] for n in names}
    _, quiet = R.talk(w, names, {**{n: {} for n in names}, "Osric": {"say": [{"to": "the Barn", "text": "barn"},
                                                                            {"to": "the Hall", "text": "hall"},
                                                                            {"to": "Fenn House", "text": "fenn"}]},
                                  "Agnes": {"say": [{"to": "Fenn House", "text": "home"}]}}, res)
    assert any("the Barn" in x for x in quiet["Tam"]) and not any("the Barn" in x for x in quiet["Maud"])
    assert all(any("the Hall" in x for x in quiet[m]) for m in names if m != "Osric")
    assert any(x.startswith("Refused: say: you have no access to Fenn House") for x in res["Osric"])
    assert any("home" in x for x in quiet["Wat"]) and any("home" in x for x in quiet["Ivy"]) and not any("home" in x for x in quiet["Maud"])


def test_milking_needs_a_cow_in_milk_and_the_craft():
    from cybertron2.m1 import act as AC, run as R
    w = World(load_spec(SPEC))
    today = R._blank_today()
    assert w.s["herds"]["cattle"]["in_milk"] == 2
    assert "milk" in " ".join(KN.options(w, "Maud")[0])
    assert AC.do(w, "Maud", {"do": "work", "what": "milk"}, today).startswith("You milked")
    assert AC.do(w, "Osric", {"do": "work", "what": "milk"}, today).startswith("Refused")      # does not know it


def test_private_message_ration_and_say_cost():
    from cybertron2.m1 import run as R
    w = World(load_spec(SPEC))
    w.s["today"] = R._blank_today()
    names = w.agents_acting()
    lim = w.s["agents"]["Osric"]["messages"]
    assert 3 <= lim <= 6
    res = {n: [] for n in names}
    tells = [{"to": "Agnes", "text": f"m{i}"} for i in range(3)]
    for _ in range(3):                                                         # three replies of 3 tells each
        R.talk(w, names, {**{n: {} for n in names}, "Osric": {"tell": tells}}, res)
    sent = sum(1 for x in res["Osric"] if x.startswith("You told "))
    assert sent == lim and any(x.startswith("Refused: tell: you have sent your") for x in res["Osric"])
    R.talk(w, names, {**{n: {} for n in names}, "Osric": {"say": [{"to": "everyone", "text": "a"}, {"to": "Reed House", "text": "b"}]}}, res)
    assert sum(1 for x in res["Osric"] if x.startswith("You said (")) == 2   # each takes a unit, deducted before work


def test_travel_is_the_last_act_and_arrives_next_morning():
    from cybertron2.m1 import act as AC, run as R
    w = World(load_spec("cybertron2/specs/m2_valley_s5.yaml"))
    w.s["today"] = today = R._blank_today()
    who = next(n for n, a in w.s["agents"].items() if w.at(n) == "millbrook" and a["stage"] == "adult")
    assert AC.do(w, who, {"do": "travel", "to": "Coppergate"}, today).startswith("You set off")      # 2 days
    assert AC.do(w, who, {"do": "travel", "to": "Nowhere"}, today).startswith("Refused")
    w.night()
    assert w.at(who) is None and w.s["agents"][who]["transit"]["arrive"] == 2
    assert who not in w.agents_acting()
    w.s["day"] = 1; w.s["today"] = R._blank_today(); w.arrive(); w.night()
    assert w.at(who) is None                                                   # still on the road
    w.s["day"] = 2; w.s["today"] = R._blank_today(); w.arrive()
    assert w.at(who) == "coppergate" and who in w.agents_acting()
    host = next(n for n in w.agents_acting() if w.s["agents"][n]["household"] == "Smith" and n != who)
    assert AC.do(w, host, {"do": "welcome", "person": who}, w.s["today"]).startswith("You welcome")
    assert w.sleeps(who) == ("smith_house", False)


def test_too_heavy_to_leave_then_leave_goods_at_a_house_found_next_morning():
    from cybertron2.m1 import act as AC, run as R, prompt as PR
    w = World(load_spec("cybertron2/specs/m2_valley_s5.yaml"))
    w.s["today"] = today = R._blank_today()
    who = next(n for n, a in w.s["agents"].items() if w.at(n) == "ashwood" and a["stage"] == "adult")
    w.s["agents"][who]["holdings"]["timber"] = 6.0                             # 12 weight
    assert AC.do(w, who, {"do": "travel", "to": "Coppergate"}, today).startswith("Refused: travel: you carry")
    assert "weight" in PR.turn_prompt(w, who) and "timber 2" in PR.system_prompt(w, who)
    assert "leave" in PR.lighten_prompt(w, who, {"to": "Coppergate"}, [])
    before = w.s["houses"]["fenn_house"]["stock"].get("timber", 0)
    assert AC.do(w, who, {"do": "leave", "item": "timber", "qty": 2, "at": "Fenn House"}, today).startswith("You left")
    assert w.s["houses"]["fenn_house"]["stock"]["timber"] == before + 2
    assert AC.do(w, who, {"do": "leave", "item": "timber", "qty": 1, "at": "Smith House"}, today).startswith("Refused")   # not here
    assert AC.do(w, who, {"do": "travel", "to": "Coppergate"}, today).startswith("You set off")
    w.night()
    w.s["day"] = 1; w.s["today"] = R._blank_today(); R.dawn(w)
    e = [x for x in w.s["events"] if x["kind"] == "left"]
    assert e and e[0]["dawn"] and e[0]["node"] == "ashwood" and f"{who} left 2 timber at Fenn House" == e[0]["text"]
