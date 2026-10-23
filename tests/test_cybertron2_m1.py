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
