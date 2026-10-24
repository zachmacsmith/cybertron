"""R4 of the run record (spec/record/branching.md): rewind, fork with interventions and other responders, replicates, continue."""
import json

import pytest

from cybertron2.engine import branch as BR, journal as JN, run as R

SPEC = "cybertron2/specs/valley_s5.yaml"


@pytest.fixture(scope="module")
def parent(tmp_path_factory):
    out = tmp_path_factory.mktemp("parent")
    R.run(SPEC, out, days=5, bots=True)
    return out


def _end(d):
    return (d / "state.json").read_text()


def test_rewind_keeps_the_record_to_the_step_and_resumes_to_the_same_end(parent, tmp_path):
    before = (parent / "run.db").stat().st_size
    BR.rewind(parent, "d2.work", tmp_path / "rw")
    steps = [s for (s,) in JN.read(tmp_path / "rw" / "run.db", "SELECT step FROM steps")]
    assert steps[-1] == "d2.work" and all(BR.order(s) <= BR.order("d2.work") for s in steps)
    assert not JN.read(tmp_path / "rw" / "run.db", "SELECT key FROM requests WHERE step = 'd2.settle' OR step LIKE 'd3.%'")
    R.run(None, tmp_path / "rw", mode="resume")
    assert _end(tmp_path / "rw") == _end(parent) and (parent / "run.db").stat().st_size == before
    kinds = [k for (k,) in JN.read(tmp_path / "rw" / "run.db", "SELECT kind FROM segments ORDER BY id")]
    assert kinds == ["start", "rewind", "resume"]


def test_a_fork_with_an_intervention_goes_its_own_way_and_replays(parent, tmp_path):
    w0 = JN.checkpoint(parent / "run.db", "d1.memory")["world"]
    bid = next(b for b, x in w0["buildings"].items() if x.get("stock") and w0["containers"][x["stock"]]["goods"].get("grain", 0) > 1)
    cid, node = w0["buildings"][bid]["stock"], w0["buildings"][bid]["node"]
    q = w0["containers"][cid]["goods"]["grain"]
    iv = [{"op": "destroy", "place": node, "args": {"src": cid, "item": "grain", "qty": q, "why": "a fire"}, "note": "the store burns"}]
    BR.fork(parent, "d1.memory", tmp_path / "f", interventions=iv)
    R.run(None, tmp_path / "f", mode="resume")
    db = tmp_path / "f" / "run.db"
    assert _end(tmp_path / "f") != _end(parent)
    assert JN.checkpoint(db, "d2.dawn")["world"]["containers"][cid]["goods"].get("grain", 0) < 1e-6
    applied = JN.read(db, "SELECT applied FROM interventions")
    assert len(applied) == 1 and json.loads(applied[0][0])["step"] == "d1.memory"
    assert JN.read(db, "SELECT COUNT(*) FROM changes WHERE cause LIKE '%intervention%'")[0][0] == 1
    rep = R.run(None, tmp_path / "f", mode="replay")
    assert rep["mismatches"] == []                                         # played again, the intervention is played again
    assert len(JN.read(db, "SELECT applied FROM interventions WHERE applied IS NOT NULL")) == 1


def test_replicates_share_the_past_and_differ_after(parent, tmp_path):
    outs = BR.replicates(parent, "d1.memory", tmp_path / "reps", 2)
    for o in outs:
        R.run(None, o, mode="resume")
    a, b = (JN.checkpoint(o / "run.db", "d1.memory")["world"] for o in outs)
    assert a == b == JN.checkpoint(parent / "run.db", "d1.memory")["world"]
    assert _end(outs[0]) != _end(outs[1])
    assert json.loads(_end(outs[0]))["salt"] == "rep1"


def test_continue_from_the_end_of_a_day_under_this_code(parent, tmp_path):
    BR.continue_(parent, "d2.memory", tmp_path / "c")
    R.run(None, tmp_path / "c", mode="continue")
    assert _end(tmp_path / "c") == _end(parent)                            # the same code: the same end
    with pytest.raises(SystemExit):
        BR.continue_(parent, "d2.work", tmp_path / "c2")                   # only from the end of a day
    found = BR.branches(parent)["branches"]
    assert any(b["kind"] == "continue" and b["at"] == "d2.memory" for b in found)
