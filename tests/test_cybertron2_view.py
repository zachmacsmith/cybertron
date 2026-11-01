"""The morning message built from beliefs (view.py; review 38.40 §9): the opening shows the whole of what one believes of here, later
days only what changed; nothing computed for the agent (no "Today you could"); what one works on, one sees (the acting channel);
and the weekly usage stop (run.UsageStop)."""
import json

from cybertron2.engine import api as API, run as R
from cybertron2.engine.world import load_spec

SPEC = "cybertron2/specs/valley_s5.yaml"


def _played(tmp_path, days=4):
    s = load_spec(SPEC)
    s["view"] = "beliefs"
    s["children"] = {"on": True, "dial": "low"}
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(s))
    out = tmp_path / "run"
    real = R.load_spec
    R.load_spec = lambda path: json.loads(open(path).read())
    try:
        R.run(str(p), out, days=days, bots=True, responders={"Rohese": "human"})
        shown = {}
        for _ in range(40):
            st = API.status(out)
            if st["ended"] or not st["waiting"]:
                break
            req = st["waiting"][0]
            ctx = API.context(out, req["key"])
            if req["kind"] == "decision":
                shown[req["key"]] = ctx["message"]
            reply = ({"why": "", "actions": [], "memory": "I worked the hillside."} if req["kind"] == "memory" else
                     {"why": "x", "actions": [{"do": "gather", "what": "forage", "at": "the Hillside"},
                                              {"do": "work", "what": "care", "at": "Piers"}]})
            assert API.answer(out, req["key"], reply) == []
            API.advance(out)
    finally:
        R.load_spec = real
    return out, shown


def test_the_opening_shows_the_whole_and_later_days_only_what_changed(tmp_path):
    out, shown = _played(tmp_path)
    first, second = shown["d0.decide.Rohese.1"], shown["d1.decide.Rohese.1"]
    assert "## Here, as you see it" in first and "Today you could" not in first and "Not yet" not in first
    assert "## Since your last morning" in second and "## Here, as you see it" not in second
    assert len(second) < len(first)
    assert "Looking after a child is work" in first and "Looking after a child is work" not in second
    assert "the Hillside" in second                                            # what she worked, she saw (the acting channel)
    assert R.run(None, out, mode="replay")["mismatches"] == []


def test_a_run_stops_cleanly_before_a_day_when_the_week_is_at_the_stop(tmp_path, monkeypatch):
    from cybertron import llm
    monkeypatch.setattr(llm, "USAGE", {"windows": {"seven_day": 0.5, "five_hour": 0.1}, "status": "allowed"})
    monkeypatch.setenv("CYBERTRON2_WEEK_STOP", "0.4")
    out = tmp_path / "run"
    R.run(SPEC, out, days=3, bots=True)
    assert "weekly window is 50% used" in (out / "STOPPED.md").read_text()
    monkeypatch.setattr(llm, "USAGE", {})
    R.run(None, out, mode="resume")                                            # resumed later, it goes on
    assert not (out / "STOPPED.md").exists() and (out / "state.json").exists()
