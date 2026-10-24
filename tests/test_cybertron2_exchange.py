"""R5 of the run record (spec/record/exchange.md, views.md): views, export to Parquet, import, publish through the privacy gate."""
import json
import sqlite3

import pytest

pytest.importorskip("pyarrow")

from cybertron2.engine import exchange as EX, journal as JN, run as R, views as VW   # noqa: E402

SPEC = "cybertron2/specs/valley_s5.yaml"
SECRET = "SESSION-5ec2e7-id"


@pytest.fixture(scope="module")
def model_run(tmp_path_factory):
    """A 3-day run with a stubbed model whose usage carries a private id (as a CLI session id would)."""
    from cybertron import llm
    out = tmp_path_factory.mktemp("mrun")
    seen = []
    real = llm._api

    def api(model, system, user, schema, thinking_budget, max_tokens):
        seen.append(str(user))
        raw = json.dumps({"why": "steady", "actions": [{"do": "gather", "what": "forage"}],
                          "tell": [{"to": "Edric", "text": "Meet me at the copse."}]})
        return raw, json.loads(raw), "", {"input_tokens": 3, "session": SECRET}
    llm._api = api
    try:
        R.run(SPEC, out, backend="api", days=3)
    finally:
        llm._api = real
    return out, seen


def _tables(db):
    con = sqlite3.connect(str(db))
    out = {t: con.execute(f"SELECT * FROM {t} ORDER BY rowid").fetchall() for t in JN.TABLES}
    con.close()
    return out


def test_export_import_and_replay_reproduce_the_run(model_run, tmp_path):
    run, _ = model_run
    exp = EX.export(run, tmp_path / "exp")
    man = json.loads((exp / "manifest.json").read_text())
    assert man["journal"]["checkpoints"]["rows"] == len(VW.steps(run))
    back = EX.import_(exp, tmp_path / "back")
    assert _tables(back / "run.db") == _tables(run / "run.db")             # exactly
    rep = R.run(None, back, backend="api", mode="replay")
    assert rep["mismatches"] == [] and rep["checked"] == len(VW.steps(run))
    (exp / "journal" / "events.parquet").write_bytes(b"tampered")
    with pytest.raises(SystemExit):
        EX.import_(exp, tmp_path / "bad")


def test_an_agents_context_is_its_conversation_as_sent(model_run):
    run, seen = model_run
    reqs = [r for r in VW.requests(run) if r["kind"] == "decision"]
    ctxs = [VW.context(run, r["key"]) for r in reqs if r["step"] == "d1.decide"]
    ctx = next(c for c in ctxs if c["conversation"].endswith("@0"))        # a conversation begun on day 0 (they start staggered)
    assert ctx["system"] and ctx["schema"]["type"] == "object" and ctx["turns"]                 # day 0's exchange came first
    assert ctx["turns"][0]["reply"].startswith('{"why": "steady"') and ctx["answer"]["why"] == "steady"
    assert any(ctx["message"] in s for s in seen)                                                # what the model was sent
    assert VW.requests(run, pending=True) == []


def test_the_view_tables(model_run):
    run, _ = model_run
    v = EX.view_tables(run)
    people = {r["name"] for r in v["people_days"] if r["day"] == 0}
    assert len(v["people_days"]) == 3 * len(people)
    assert {r["id"] for r in v["layout"] if r["kind"] == "node"} == set(VW.state(run, "d0.dawn")["nodes"])
    assert any(r["kind"] == "person" for r in v["frames"]) and v["calls"] and v["holdings"]
    assert any(m["to"] == "Edric" and "copse" in m["text"] for m in v["messages"])


def test_publish_redacts_this_machines_ids_and_the_gate_checks(model_run, tmp_path, monkeypatch):
    run, _ = model_run
    assert EX.scan(EX.export(run, tmp_path / "raw"), [SECRET])            # unredacted, the gate would refuse
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", SECRET)
    root = EX.publish([run], staging=tmp_path / "stage")
    assert (root / run.name / "journal" / "responses.parquet").exists() and (root / "README.md").exists()
    assert EX.scan(root, [SECRET]) == []
