"""Documents (cybertron/documents.py, docs/review/32_documents.md): literacy gating, personal stores, copies with provenance
(doc_send), live read and write grants, confined access for non-literate agents, and that it is all off by default. Offline:
no model is called (scripted bots for the run)."""
from __future__ import annotations

import pytest

from cybertron import actions as A
from cybertron import action_registry as AR
from cybertron import agents as AG
from cybertron import directories as DR
from cybertron import documents as DOC
from cybertron import generator, runner
from cybertron import replay as RP
from cybertron import schema as SC
from cybertron import spec as S
from cybertron.kernel import Kernel

QUIET = dict(log=lambda *a: None)
LEG_ONLY = "documents.literate={classes: [legislator]}"


def _spec(*extra):
    return S.apply_overrides(S.load("society"), ["shared_archive.enabled=false", "rounds=2", "documents.enabled=true", *extra])


def _world(*extra):
    inst = generator.generate(_spec(*extra), 1)
    k = Kernel(inst)
    by = lambda c: [a["id"] for a in inst["agents"] if a["cls"] == c]
    return k, by("legislator"), by("worker")


def act(k, aid, name, **args):
    return A.act(k, aid, name, args)


def verbs(k, aid):
    return {a.name for a in AR.available(k.inst, k, k.w["agents"][aid]) if a.module == "directories"}


# ------------------------------------------------------------------ off by default
@pytest.mark.parametrize("preset", ["E2", "society"])
def test_off_by_default(preset):
    sp = S.apply_overrides(S.load(preset), ["shared_archive.enabled=false"])
    assert not DOC.on(sp) and not DR.enabled(sp)
    k = Kernel(generator.generate(sp, 1))
    assert "dirs" not in k.w and "doc_stores" not in k.w
    aid = k.roster()[0]
    with pytest.raises(A.ActionError, match="unknown action"):
        act(k, aid, "doc_send", path="x", to=k.roster()[1])


def test_chronicle_world_without_documents_has_no_doc_send():
    sp = S.apply_overrides(S.load("society"), ["shared_archive.enabled=false", "rounds=2"])
    inst = generator.generate(sp, 1)
    hist = [a["id"] for a in inst["agents"] if a["cls"] == "worker"][0]
    sp["roles"]["explicit"] = {"historian": [hist]}
    k = Kernel(generator.generate(sp, 1))
    assert "doc_send" not in verbs(k, hist) and "dir_write" in verbs(k, hist)
    act(k, hist, "dir_write", path="r.md", text="x")
    assert "copy of" not in DR.turn_section(k, hist) and "meta" not in k.w["dirs"]["chronicle"]


# ------------------------------------------------------------------ literacy
def test_literacy_gates_owning_a_store():
    k, legs, workers = _world(LEG_ONLY)
    L, W = legs[0], workers[0]
    assert k.w["doc_stores"][L] == L and k.w["dirs"][W]["personal"] == W        # everyone has a store; only some own it
    assert DOC.literate(k, L) and not DOC.literate(k, W)
    assert {"dir_write", "dir_grant", "doc_send"} <= verbs(k, L) and verbs(k, W) == set()
    assert DR.turn_section(k, W) == ""                                          # nothing given yet: nothing shown
    with pytest.raises(A.ActionError):
        act(k, W, "dir_write", dir=W, path="note.md", text="x")
    assert "your documents" in DR.turn_section(k, L) and "You can write documents" in DR.turn_section(k, L)
    stat = {a.name for a in AR.available(k.inst, None, next(x for x in k.inst["agents"] if x["id"] == L))}
    assert "dir_write" in stat and "doc_send" in stat                           # the system prompt written before a kernel
    stat_w = {a.name for a in AR.available(k.inst, None, next(x for x in k.inst["agents"] if x["id"] == W))}
    assert not stat_w & set(DR.ACTIONS)


def test_literacy_is_live_rights_with_a_prefix():
    k, legs, workers = _world('documents.literate={rights: ["J0.*"]}')
    W = workers[0]
    assert not DOC.literate(k, W)
    k.w["agents"][W]["rights"].append("J0.clerk")                              # took an office
    assert DOC.literate(k, W) and "dir_write" in verbs(k, W)
    k.w["agents"][W]["rights"].remove("J0.clerk")                              # lost it: confined to what it holds
    assert not DOC.literate(k, W)


@pytest.mark.parametrize("sel, ok", [("all", True), ("none", True), ({"classes": ["worker"]}, True),
                                     ({"clases": ["worker"]}, False), ("some", False)])
def test_literate_selector_is_validated(sel, ok):
    sp = _spec()
    sp["documents"]["literate"] = sel
    errs = SC.validate(sp)
    assert (errs == []) == ok, errs


# ------------------------------------------------------------------ copies
def test_copy_lands_with_provenance_and_notice():
    k, legs, workers = _world(LEG_ONLY)
    L, W, W2 = legs[0], workers[0], workers[1]
    act(k, L, "dir_write", path="contract.md", text="Contract: W delivers 5 timber to L by round 4.")
    out = act(k, L, "doc_send", path="contract.md", to=W)
    dest = f"received/{L}/contract.md"
    assert f"{W}/{dest}" in out and k.w["dirs"][W]["files"][dest].startswith("Contract:")
    assert any("sent you a copy" in str(n) and "5 timber" in str(n) for n in _notices(k, W))
    sec = DR.turn_section(k, W)
    assert "documents given to you" in sec and f"a copy of {L}/contract.md, written by {L}, sent by {L}" in sec
    assert verbs(k, W) == {"dir_list", "dir_read", "dir_search", "doc_send"}        # confined: read and pass on
    assert "5 timber" in act(k, W, "dir_read", path=dest)
    act(k, W, "doc_send", path=dest, to=W2)                                      # handed on by a non-literate agent
    assert f"written by {L}, sent by {W}" in DR.turn_section(k, W2)
    act(k, L, "dir_delete", path="contract.md")                                  # a copy cannot be taken back
    assert dest in k.w["dirs"][W]["files"]
    act(k, L, "dir_write", path="contract.md", text="v2")
    act(k, L, "doc_send", path="contract.md", to=W)
    assert f"received/{L}/contract-2.md" in k.w["dirs"][W]["files"]             # a second copy does not overwrite the first


def test_a_literate_recipients_altered_copy_is_marked():
    k, legs, _ = _world(LEG_ONLY)
    L1, L2 = legs[0], legs[1]
    act(k, L1, "dir_write", path="memo.md", text="Pay 3 grain.")
    act(k, L1, "doc_send", path="memo.md", to=L2)
    p = f"received/{L1}/memo.md"
    assert "altered" not in DR.turn_section(k, L2)
    act(k, L2, "dir_edit", path=p, find="3 grain", replace="30 grain")
    assert "altered since it was received" in DR.turn_section(k, L2)
    act(k, L2, "dir_move", path=p, to="kept/memo.md")
    assert "a copy of" in DR.turn_section(k, L2) and k.w["dirs"][L2]["meta"].get("kept/memo.md")


def test_copy_refusals_and_limits():
    k, legs, workers = _world(LEG_ONLY, "documents.max_bytes=100")
    L, W = legs[0], workers[0]
    act(k, L, "dir_write", path="a.md", text="x" * 80)
    for to in (L, "Nobody"):
        with pytest.raises(A.ActionError, match="unknown recipient"):
            act(k, L, "doc_send", path="a.md", to=to)
    act(k, L, "doc_send", path="a.md", to=W)
    with pytest.raises(A.ActionError, match="cannot take this copy"):
        act(k, L, "doc_send", path="a.md", to=W)                                # the recipient's store is full


def test_copy_is_routed_through_dir_write():
    k, legs, workers = _world(LEG_ONLY)
    L, W = legs[0], workers[0]
    act(k, L, "dir_write", path="a.md", text="x")
    seen = []
    real = k.apply
    k.apply = lambda name, **p: (seen.append((name, p.get("agent"), p.get("dir"))), real(name, **p))[1]
    act(k, L, "doc_send", path="a.md", to=W)
    assert seen == [("dir_write", L, W)]


# ------------------------------------------------------------------ live shares
def test_grant_gives_confined_live_access_and_revokes():
    k, legs, workers = _world(LEG_ONLY)
    L, W = legs[0], workers[0]
    act(k, L, "dir_write", path="contract.md", text="Deliver 5 timber.")
    act(k, L, "dir_write", path="private.md", text="my notes")
    act(k, L, "dir_grant", agent=W, path="contract.md", access="write")
    assert "dir_edit" in verbs(k, W) and f"{L}'s documents; shared with you: write" in DR.turn_section(k, W)
    act(k, W, "dir_edit", dir=L, path="contract.md", find="5", replace="4")      # edits the live document
    assert k.w["dirs"][L]["files"]["contract.md"] == "Deliver 4 timber."
    for bad in (lambda: act(k, W, "dir_read", dir=L, path="private.md"),
                lambda: act(k, W, "dir_write", dir=L, path="new.md", text="x"),
                lambda: act(k, W, "dir_grant", dir=L, agent=workers[1], path="", access="read")):
        with pytest.raises(A.ActionError):
            bad()
    assert "private.md" not in DR.turn_section(k, W)
    act(k, L, "dir_grant", agent=W, path="contract.md", access="none")
    assert verbs(k, W) == set() and DR.turn_section(k, W) == ""


# ------------------------------------------------------------------ a scripted run
def test_scripted_run_and_exact_replay(tmp_path):
    inst = generator.generate(_spec(LEG_ONLY), 1)
    out = runner.run(inst, AG.ScriptedPolicy(1), tmp_path / "run", **QUIET)
    import json
    snap = json.loads((out / "snapshots.json").read_text())[-1]["directories"]
    legs = [a["id"] for a in inst["agents"] if a["cls"] == "legislator"]
    assert any(snap[x]["files"] for x in legs)                                   # the owners' bots wrote documents
    assert all(not snap[a["id"]]["owners"] for a in inst["agents"] if a["cls"] == "worker")
    assert any(p.startswith("received/") for x in snap.values() for p in x["files"])   # the bots' doc_send copies landed
    res = RP.replay(out, tmp_path / "rep", **QUIET)
    assert res["identical"], res


def _notices(k, aid):
    return [e["data"]["text"] for e in k.events if e.get("type") == "notify" and e["data"].get("to") == aid]
