"""Shadowed law effects (cybertron/laweffects.py: shadows): a change that is real in the world's tables but decides nothing because a
rule of higher precedence wins. The Thornby pilot (W1, L11 "Workers' Review Act"): set_procedure without a rank after the base law
set rank-specific procedures; law_effect said "procedures: ordinary: L2 -> L11" and statute drafts still went to the full council.
And the usability round 2 granary amendment: a before_withdraw that lets councillors through by not blocking them, on a store the
keeper's office controls. Reporting only: what decides is unchanged."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from cybertron import actions as A
from cybertron import agents as AG
from cybertron import dispatch as D
from cybertron import generator as GN
from cybertron import laweffects as LE
from cybertron import lawpreview as LP
from cybertron import runner
from cybertron import start as STT

import test_established_worlds as TW


def _world(tmp, name, ranks):
    sp = TW.village(rounds=1)
    sp["regime"]["laws"][0]["params"]["RANKS"] = ranks
    inst = GN.generate(sp, 1)
    return Path(runner.run(inst, AG.ScriptedPolicy(1), tmp / name, log=lambda *a: None))


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("shadow")
    return {"ranked": _world(tmp, "ranked", ["statute", "constitution"]),     # Thornby's L2: RANKS [statute, constitution]
            "plain": _world(tmp, "plain", [])}


def kernel(runs, name="ranked"):
    return STT._kernel_at(runs[name], 0)[1]


def events(k, t, since=0):
    return [e for e in k.events[since:] if e["type"] == t]


def smp(k):
    return next(l["id"] for l in k.active_laws() if l["title"] == "Simple Majority Procedure")


REVIEW = '''title = "Workers' Review Act"
intent = "Laws are decided by the Review: Ada alone."

def review(p):
    return {"electorate": ["Ada"], "rule": "majority", "closes_in": 1}

def on_enact():
    set_procedure("ordinary", review)
    set_procedure("structural", review)
    set_procedure("procedural", review)
'''
RANKED = REVIEW.replace('review)\n', 'review, rank="statute")\n')


def test_thornby_unranked_procedure_is_shadowed(runs):
    k = kernel(runs)
    base = smp(k)
    assert D.procedure_lookup(k.w["procedures"], "ordinary", "statute").split("#")[0] == base
    n = len(k.events)
    lid = k.new_law(REVIEW, "Ada")
    k.enact(lid)
    fx = events(k, "law_effect", n)[-1]
    d = fx["data"]
    assert f"procedures: ordinary: {base} -> {lid}" in d["changes"]           # the table did change ...
    assert D.procedure_lookup(k.w["procedures"], "ordinary", "statute").split("#")[0] == base   # ... but statute drafts did not
    sh = {s["rule"]: s for s in d["shadowed"]}
    assert set(sh) == {"ordinary", "structural", "procedural"}
    for s in sh.values():
        assert s["kind"] == "procedure" and s["law"] == lid
        assert s["shadowed_for"] == ["constitution", "statute"] and s["applies_to"] == ["regulation", "bylaw"]
        assert {b["law"] for b in s["by"]} == {base}
    assert sh["ordinary"]["by"][0]["rule"] in ("statute:ordinary", "constitution:ordinary")
    assert d["n_effective"] == d["n_changes"] and d["inert"] is False      # still decides regulation and bylaw drafts
    line = AG.render_event(k, fx, "[t]")
    assert "SHADOWED: the procedures" in line and "do not apply to statute or constitution drafts (statute is every draft's default rank)" in line
    assert f"{base} 'Simple Majority Procedure' set rank-specific procedures" in line
    assert f"{lid}'s apply only to regulation and bylaw drafts" in line and 'set_procedure(cls, fn, rank="statute")' in line


def test_thornby_proposal_preview_and_proposer_are_told(runs):
    k = kernel(runs)
    n = len(k.events)
    res = A.act(k, "Ada", "propose", {"code": REVIEW})
    assert "SHADOWED" in res and "do not apply to statute or constitution drafts" in res
    prop = events(k, "proposal", n)[-1]
    assert prop["data"]["shadowed"] and "SHADOWED" in AG.render_event(k, prop, "[t]")
    k = kernel(runs)
    before = copy.deepcopy(k.w)
    rep = LP.preview_law(k, "Ada", REVIEW, scenario="none", rounds=1)
    assert rep["enact"]["shadowed"] and k.w == before
    txt = LP.render(rep)
    assert "SHADOWED: the procedure" in txt and "statute drafts" in txt


def test_ranked_procedure_is_not_shadowed(runs):
    k = kernel(runs)
    n = len(k.events)
    lid = k.new_law(RANKED, "Ada")
    k.enact(lid)
    d = events(k, "law_effect", n)[-1]["data"]
    assert f"procedures: statute:ordinary: {smp(k)} -> {lid}" in d["changes"]
    assert "shadowed" not in d and "n_effective" not in d and "shadow_notes" not in d
    assert D.procedure_lookup(k.w["procedures"], "ordinary", "statute").split("#")[0] == lid
    assert "SHADOWED" not in AG.render_event(k, events(k, "law_effect", n)[-1], "[t]")


def test_plain_world_unranked_procedure_is_unchanged(runs):
    k = kernel(runs, "plain")
    n = len(k.events)
    lid = k.new_law(REVIEW, "Ada")
    k.enact(lid)
    fx = events(k, "law_effect", n)[-1]
    assert "shadowed" not in fx["data"] and set(fx["data"]) == {"law", "title", "act", "changes", "n_changes", "inert", "failed_calls"}
    line = AG.render_event(k, fx, "[t]")
    assert (f"{lid} 'Workers' Review Act' passed; it changed: procedures: ordinary: L2 -> {lid}; " in line) and "SHADOWED" not in line
    rep = LP.preview_law(kernel(runs, "plain"), "Ada", REVIEW, scenario="none", rounds=1)
    assert "shadowed" not in rep["enact"] and "SHADOWED" not in LP.render(rep)


def test_fully_shadowed_procedure_counts_as_inert():
    ranked = {f"{r}:{c}": "L2" for r in ("constitution", "statute", "regulation", "bylaw") for c in D.CLASSES}
    before = {"procedures": {**ranked, "ordinary": "L2"}, "rules": {}}
    after = {"procedures": {**ranked, "ordinary": "L9"}, "rules": {}}
    sh = LE.procedure_shadows(before, after)
    assert len(sh) == 1 and sh[0]["applies_to"] == [] and sh[0]["change"] == "procedures: ordinary: L2 -> L9"
    diff = ["procedures: ordinary: L2 -> L9"]
    assert LE.ineffective(diff, sh) == set(diff)
    assert LE.inert("enact", [x for x in diff if x not in LE.ineffective(diff, sh)], None, 'title = "x"\n')
    assert "L9's decide no draft at all" in LE.shadow_texts(None, sh)[0]
    assert LE.procedure_shadows(before, {"procedures": {**ranked, "ordinary": "L2", "statute:ordinary": "L9"}, "rules": {}}) == []


def _granary(k):
    return next(l for l in k.active_laws() if l["title"] == "Granary Ration")


def test_office_control_shadows_a_councillor_draw(runs):
    k = kernel(runs, "plain")
    g = _granary(k)
    assert LE.control_shadows(k, g["id"]) == []                         # the keeper's own ration: nothing overridden
    code = g["code"].replace('if not has(p["agent"], OFFICE)', 'if not (has(p["agent"], OFFICE) or has(p["agent"], "J0.council"))')
    assert code != g["code"]
    from cybertron import amendment as AM
    n = len(k.events)
    lid = AM.amendment_draft(k, g["id"], code, "Ada", "councillors draw too")
    k.enact(lid)
    fx = events(k, "law_effect", n)[-1]
    sh = fx["data"]["shadowed"]
    assert sh == [{"kind": "office_control", "hook": "before_withdraw", "store": "S1", "owner": "J0", "admits": ["J0.council"],
                   "offices": ["Keeper (J0.keeper)"], "change": "before_withdraw on store S1"}]
    line = AG.render_event(k, fx, "[t]")
    assert "SHADOWED: its before_withdraw lets holders of J0.council through" in line and "return True" in line
    allow = code.replace("    return None\n\ndef after_withdraw", "    return True\n\ndef after_withdraw")
    assert allow != code and LE.control_shadows(k, lid, allow) == []    # an explicit allow passes the control gate
