"""The run's journal, R1 of the run record (spec/record/journal.md, execution.md; D1-1 to D1-5): written alongside a run's other files,
changing nothing the run does."""
import json

import pytest

from cybertron2.engine import journal as JN, run as R

SPEC = "cybertron2/specs/valley_s5.yaml"
STEPS = ("dawn", "decide", "talk.0", "work", "settle", "night", "memory")


@pytest.fixture(scope="module")
def bot_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("journal_bots")
    R.run(SPEC, out, days=3, bots=True)
    return out


def test_every_step_is_committed_in_order_with_a_checkpoint(bot_run):
    db = bot_run / "run.db"
    rows = JN.read(db, "SELECT step, attempt, status, checkpoint FROM steps ORDER BY started")
    names = [r[0] for r in rows]
    assert names[:2] == ["d0.dawn", "d0.decide"] and names[-1] == "d2.memory"
    assert all(r[1] == 1 and r[2] == "committed" and r[3] for r in rows)
    assert {n.split(".", 1)[1] for n in names} <= set(STEPS) | {"talk.1"}
    assert len(JN.read(db, "SELECT step FROM checkpoints")) == len(rows)


def test_the_last_checkpoint_is_the_saved_state(bot_run):
    cp = JN.checkpoint(bot_run / "run.db", "d2.memory")
    saved = json.loads((bot_run / "state.json").read_text())
    assert json.loads(json.dumps(cp["world"])) == json.loads(json.dumps(saved))
    assert set(cp["runner"]) == {"cost", "conversations", "carry"} and "results" in cp["runner"]["carry"]


def test_inputs_requests_events_and_changes_are_kept(bot_run):
    db = bot_run / "run.db"
    meta = dict(JN.read(db, "SELECT key, value FROM meta"))
    prov = json.loads(meta["provenance"])
    assert prov["modules"]["cybertron2/engine/world.py"] and "python" in prov and json.loads(meta["seed"]) is not None
    assert {"PHYSICS", "ITEMS", "TECHNIQUES"} <= {r[0] for r in JN.read(db, "SELECT name FROM data")}
    turns = [json.loads(l) for l in (bot_run / "turns.jsonl").read_text().splitlines()]
    reqs = JN.read(db, "SELECT key, step, agent, kind, responder FROM requests WHERE kind = 'decision'")
    assert len(reqs) == sum(1 for t in turns if not t.get("on_road"))
    assert all(k == f"{s}.{a}.1" and r == "bot" for k, s, a, _, r in reqs)
    assert len(JN.read(db, "SELECT key FROM responses")) == len(JN.read(db, "SELECT key FROM requests"))
    prims = dict(JN.read(db, "SELECT primitive, COUNT(*) FROM changes GROUP BY primitive"))
    assert prims.get("set_res") and prims.get("harm")                       # nature's night and eating go through apply now
    ev = JN.read(db, "SELECT id, step FROM events")
    assert ev and all(s for _, s in ev)
    assert json.loads(meta["journal_failures"]) == 0


def test_a_models_request_records_what_it_was_given(tmp_path, monkeypatch):
    from cybertron import llm
    seen = []

    def api(model, system, user, schema, thinking_budget, max_tokens):
        seen.append(str(user))
        raw = json.dumps({"why": "test", "actions": []})
        return raw, json.loads(raw), "", {"input_tokens": 1}
    monkeypatch.setattr(llm, "_api", api)
    R.run(SPEC, tmp_path, backend="api", days=1)
    db = tmp_path / "run.db"
    rows = JN.read(db, "SELECT key, conversation, idx, system_sha, schema_sha, message_sha, responder FROM requests WHERE kind = 'decision'")
    assert rows and len(rows) == len(seen)
    key, conv, idx, sys_sha, schema_sha, msg_sha, responder = rows[0]
    assert key.startswith("d0.decide.") and conv.endswith("@0") and idx == 0 and responder.startswith("model:")
    assert "## " in JN.unblob(db, msg_sha) and JN.unblob(db, sys_sha) and json.loads(JN.unblob(db, schema_sha))["type"] == "object"
    parsed = JN.read(db, "SELECT parsed, attempts FROM responses WHERE key = ?", (key,))[0]
    assert json.loads(parsed[0])["why"] == "test" and json.loads(parsed[1])[0]["raw"]


def test_a_usage_limit_is_waited_out_not_taken_for_an_answer(tmp_path, monkeypatch):
    import datetime as dt
    from cybertron import llm
    now = dt.datetime(2026, 10, 24, 13, 10, tzinfo=dt.timezone.utc)
    msg = 'CallError: claude -p error (exit 1): {"result": "You\'ve hit your session limit · resets 2:20pm (UTC)", "api_error_status": 429}'
    assert R.limit_wait(msg, now) == 70 * 60 + 120
    assert R.limit_wait("ValueError: no JSON in the reply", now) is None
    calls, slept = [], []

    def api(model, system, user, schema, thinking_budget, max_tokens):
        calls.append(1)
        if len(calls) <= 2:                                                # the first call and its own retry hit the limit
            raise RuntimeError(msg)
        raw = json.dumps({"why": "after the wait", "actions": []})
        return raw, json.loads(raw), "", {}
    monkeypatch.setattr(llm, "_api", api)
    monkeypatch.setattr(R.time, "sleep", lambda s: slept.append(s))
    from cybertron2.engine.world import World, load_spec
    from cybertron2.engine.converse import Conversations
    w = World(load_spec(SPEC))
    w.s["today"] = R.blank_today()
    n = w.agents_acting()[0]
    out, meta = R.decide(w, n, "hello", "hello", "system", "api", Conversations(tmp_path, backend="api"))
    assert out["why"] == "after the wait" and len(slept) == 1


# ---------------------------------------------------------------------- R2: resume, pause, replay (execution.md)
def _same_end(a, b):
    for f in ("state.json", "days.jsonl", "memory.jsonl"):
        assert (a / f).read_text() == (b / f).read_text(), f


def test_a_run_killed_mid_step_resumes_to_the_same_end(tmp_path, monkeypatch):
    R.run(SPEC, tmp_path / "full", days=5, bots=True)
    real, hit = R.N.night, []

    def crash(w):
        if w.d == 2 and not hit:
            hit.append(1)
            raise KeyboardInterrupt("killed in the night")
        return real(w)
    monkeypatch.setattr(R.N, "night", crash)
    with pytest.raises(KeyboardInterrupt):
        R.run(SPEC, tmp_path / "killed", days=5, bots=True)
    assert JN.read(tmp_path / "killed" / "run.db", "SELECT step FROM steps WHERE status = 'open'") == [("d2.night",)]
    R.run(None, tmp_path / "killed", mode="resume")
    _same_end(tmp_path / "full", tmp_path / "killed")
    steps = JN.read(tmp_path / "killed" / "run.db", "SELECT step, attempt, status FROM steps WHERE step = 'd2.night' ORDER BY attempt")
    assert steps == [("d2.night", 1, "aborted"), ("d2.night", 2, "committed")]


def test_paused_and_resumed_a_models_answers_are_never_asked_twice(tmp_path, monkeypatch):
    from cybertron import llm
    asked = []

    def api(model, system, user, schema, thinking_budget, max_tokens):
        asked.append(str(user)[:200])
        raw = json.dumps({"why": "steady", "actions": [{"do": "gather", "what": "forage"}]})
        return raw, json.loads(raw), "", {"input_tokens": 1}
    monkeypatch.setattr(llm, "_api", api)
    R.run(SPEC, tmp_path / "full", backend="api", days=2)
    whole = len(asked)
    asked.clear()
    R.run(SPEC, tmp_path / "paused", backend="api", days=2, until="d1.decide")
    R.run(None, tmp_path / "paused", backend="api", mode="resume")
    assert len(asked) == whole
    _same_end(tmp_path / "full", tmp_path / "paused")


def test_replay_checks_every_committed_step(tmp_path):
    R.run(SPEC, tmp_path, days=3, bots=True)
    rep = R.run(None, tmp_path, mode="replay")
    assert rep["mismatches"] == [] and rep["checked"] == len(JN.read(tmp_path / "run.db", "SELECT step FROM steps"))
    rep = R.run(None, tmp_path, mode="replay", until="d1.work")
    assert rep["at"] == "d1.work"
