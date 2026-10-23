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
    assert any(t["prompt"].count("## Yesterday") for t in turns if t["day"] > 0)


def test_knowledge_paths():
    w = World(load_spec(SPEC))
    assert KN.level(w, "Wat", "hunt") == "aware"
    for _ in range(3):
        KN.saw(w, "Wat", "hunt", "Agnes")
    assert KN.level(w, "Wat", "hunt") == "rough"
    assert KN.explained(w, "Maud", "Tam", "bread") == ""
    assert KN.level(w, "Tam", "bread") == "rough"
    KN.taught(w, "Tam", "Ivy", "pot")
    assert KN.level(w, "Ivy", "pot") == "known"                      # a youth learns faster
    assert KN.shortfall(w, "Wat", "fell") == "you need an axe; you have none"


def test_offer_goods_set_aside_and_returned():
    from cybertron2.m1 import act as AC, run as R
    w = World(load_spec(SPEC))
    w.s["today"] = R._blank_today()
    w.s["agents"]["Osric"]["holdings"]["grain"] = 4
    names = w.agents_acting()
    res = {n: [] for n in names}
    R.talk(w, names, {**{n: {} for n in names}, "Osric": {"offers": [{"to": "Agnes", "give": "4 grain", "get": "1 timber"}],
                                                          "tell": [{"to": "the Fenns", "text": "grain for timber"}]}}, res)
    assert w.s["agents"]["Osric"]["holdings"]["grain"] == 0                  # set aside
    assert any(x.startswith("You told Agnes, Ivy, Tam") for x in res["Osric"])
    oid = next(iter(w.s["offers"]))
    w.s["agents"]["Agnes"]["holdings"]["timber"] = 1
    assert AC.do(w, "Agnes", {"do": "accept", "offer": oid}, w.s["today"]).startswith("You accepted")
    assert w.s["agents"]["Agnes"]["holdings"]["grain"] == 4 and w.s["agents"]["Osric"]["holdings"]["timber"] == 1
    R.talk(w, names, {**{n: {} for n in names}, "Agnes": {"offers": [{"to": "anyone", "give": "2 grain", "get": "1 bread"}]}}, res)
    assert w.s["agents"]["Agnes"]["holdings"]["grain"] == 2
    w.night()
    assert w.s["agents"]["Agnes"]["holdings"]["grain"] > 3                  # returned at nightfall (less what she ate)
