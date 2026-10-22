"""Institutions acting on each other (review 37.3, gap G-3; cybertron/cross.py): the permission model (charters, treaties,
memberships), the gated law API and its in-world refusals, hierarchy (a charter incorporates its child), the closed raid, veto by
hook, the templates (Charter, Treaty, Guild Levy), land tenures and labour service, the prompt lines, the spec check, and the flag
off (byte-identical: no state, no functions, no docs, no lines)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from cybertron import accounts as AC
from cybertron import actions as A
from cybertron import cross as CR
from cybertron import generator as GN
from cybertron import institutions as IN
from cybertron import lawdocs as LD
from cybertron import library as LB
from cybertron import schema as SC
from cybertron import spec as S

NAMES = ["Ada", "Bo", "Cy", "Di", "Ed", "Fay"]
CHARTER = {"kind": "charter", "id": "C1", "name": "Charter of the Weavers", "parent": "J0", "child": "A1",
           "powers": ["read", {"power": "levy", "item": "penny", "qty": 5}, "appoint", "remove", "enact"]}


def world(cross=True, instruments=(), rounds=1, a1_laws=(), j0_laws=(), a2_laws=(), extra=None):
    """A small town: J0 (the council: Cy its reeve, a granary S1), A1 the Weavers' guild (Ada its head; Bo, Di members; its store
    S2), A2 the Dyers (Ed, Fay). law.v2, unified institutions with offices, jurisdictions off."""
    sp = S.load("cybertron/specs/survival/base.yaml")
    sp = S.deep_merge(sp, {
        "agents": {"worker": 6, "names": list(NAMES)}, "rounds": rounds, "parallel_calls": 1,
        "institutions": {"unified": True, "grants": True, "succession": True, "office_control": True},
        "jurisdictions": {"enabled": False, "j0_name": "the Council"}, "contracts": {"scripted": False, "max_laws": 6},
        "law": {"v2": True}, "goals": {"explicit": {"Ada": "Wealth"}},
        "life": {"age_structure": "elapsed", "elapsed": [20, 30]},
    })
    if cross is not None:
        sp["institutions"]["cross"] = {"instruments": [copy.deepcopy(x) for x in instruments]} if cross is True else cross
    sp["regime"] = {"base": None, "name": "t", "constitution": "assembly"}
    sp["start"] = {
        "rights": {n: ["vote", "propose"] for n in NAMES},
        "currencies": [{"name": "penny", "issuer": "J0"}],
        "institutions": [
            {"id": "J0", "offices": {"reeve": {"title": "Reeve", "holders": ["Cy"], "controls": ["store:S1"]}},
             "treasury": {"penny": 100}, "laws": list(j0_laws)},
            {"id": "A1", "name": "the Weavers", "founder": "Ada", "members": ["Bo", "Di"], "procedure": "founder",
             "offices": {"head": {"title": "Head", "holders": ["Ada"], "controls": ["treasury", "store:S2"]}},
             "treasury": {"penny": 50}, "laws": list(a1_laws)},
            {"id": "A2", "name": "the Dyers", "founder": "Ed", "members": ["Fay"], "procedure": "founder",
             "offices": {"master": {"title": "Master", "holders": ["Ed"]}}, "treasury": {"penny": 30}, "laws": list(a2_laws)},
        ],
        "stores": [{"id": "S1", "owner": "J0", "food": 30, "capacity": 200},
                   {"id": "S2", "owner": "A1", "food": 40, "capacity": 200}],
    }
    for key, v in (extra or {}).items():
        sp = S.set_path(sp, key, v)
    return sp


class Idle:
    def act(self, k, a, system, user, n_actions, final):
        return ({"reasoning": "", "actions": [], "notes": "", "goal_guesses_json": "{}"}, "", {})


def run(tmp_path, sp, schedule=None):
    from cybertron import runner
    inst = GN.generate(sp, 1)
    out = runner.run(inst, Idle(), tmp_path / "run", log=lambda *a: None, schedule=schedule)
    return inst, Path(out)


def kernel(tmp_path, sp, n=0):
    from cybertron import start as STT
    _, rd = run(tmp_path, sp)
    return STT._kernel_at(rd, n)[1]


def law(title, body):
    return f'title = "{title}"\nintent = "test"\n' + body


def enact(k, code, author="Cy"):
    lid = k.new_law(code, author)
    k.enact(lid)
    assert k.w["laws"][lid]["status"] == "active", k.w["laws"][lid]
    return lid


def assoc_law(k, cid, code, by):
    """A change to an association's code by its founder (procedure founder: adopted at once)."""
    from cybertron import contracts as CT
    out = CT.act_propose_contract_change(k, by, cid, code=code)
    assert "adopted" in out, out
    return next(l["id"] for l in reversed(list(k.w["laws"].values())) if l.get("jurisdiction") == cid)


def pub(k, lid):
    return k.w["laws"][lid].get("public") or {}


def evs(k, kind):
    return [e["data"] for e in k.events if e["type"] == kind]


def file_events(rd, kind):
    return [e for e in map(json.loads, (rd / "events.jsonl").read_text().splitlines()) if e["type"] == kind]


# ---------------------------------------------------------------------- off: byte-identical
def test_off_writes_nothing_adds_no_function_doc_line_or_template(tmp_path):
    sp = world(cross=None)
    assert not SC.validate(sp)
    k = kernel(tmp_path, sp)
    assert "cross" not in k.w and not CR.on(k)
    api = k.api_for("L1")
    assert not set(api) & set(CR.law_api(k, "L1")), "no cross function without the flag"
    assert all(CR.state_lines(k, a) == [] for a in NAMES)
    assert "levy_on" not in LD.resolve(k.spec)["mapping"] and not LB.cross_templates(k.inst)
    off = copy.deepcopy(sp)
    off["institutions"]["cross"] = False                               # an explicit false is the same world
    assert LD.api_doc(LD.resolve(off), "") == LD.api_doc(LD.resolve(sp), "") and not CR.on_spec(off)


def test_off_the_raid_is_still_open_on_it_is_closed(tmp_path):
    """Off (as before): a J0 law takes from an association's treasury unchecked. On: refused, in world terms."""
    raid = law("Raid", 'def on_enact():\n    public["ok"] = move("assoc:A1", "reserve", "penny", 10)\n')
    k = kernel(tmp_path / "off", world(cross=None))
    lid = enact(k, raid)
    assert pub(k, lid)["ok"] is True and AC.bal(k, "assoc:A1", "penny") == 40
    k = kernel(tmp_path / "on", world())
    lid = enact(k, raid)
    assert pub(k, lid)["ok"] is False and AC.bal(k, "assoc:A1", "penny") == 50
    assert "belongs to A1 (the Weavers)" in (k.__dict__.get("_lcf_reason") or "")


# ---------------------------------------------------------------------- acceptance: a council levies a guild only under its charter
def test_council_levies_the_guild_only_while_the_charter_grants_it(tmp_path):
    k = kernel(tmp_path, world(instruments=[CHARTER]))
    assert CR.powers_over(k, "J0", "A1") == ["read", "levy", "appoint", "remove", "enact"]
    lid = enact(k, law("Levy", 'def on_enact():\n    public["a"] = levy_on("A1", "penny", 3)\n'
                                 '    public["b"] = levy_on("A1", "penny", 3)\n    public["c"] = levy_on("A1", "food", 1, "S2")\n'))
    assert pub(k, lid) == {"a": 3.0, "b": 2.0, "c": False}            # within the limit of 5 a round; no levy of food granted
    assert AC.bal(k, "assoc:A1", "penny") == 45 and k.bal("reserve", "penny") == 105
    acts = evs(k, "cross_act")
    assert [(a["power"], a["qty"], a["instrument"]) for a in acts] == [("levy", 3.0, "C1"), ("levy", 2.0, "C1")]
    assert "holds no power to levy" in evs(k, "cross_refused")[-1]["why"]
    k.w["round"] += 1                                                  # a new period: the limit resets
    lid = enact(k, law("Revoke", 'def on_enact():\n    public["x"] = levy_on("A1", "penny", 2)\n'
                                  '    public["end"] = end_instrument("C1", "the guild defied the council")\n'
                                  '    public["y"] = levy_on("A1", "penny", 2)\n'))
    assert pub(k, lid) == {"x": 2.0, "end": True, "y": False}
    why = evs(k, "cross_refused")[-1]["why"]
    assert why == "J0 (the Council) holds no power to levy on the treasury and stores of A1 (the Weavers) (the charter C1 ended in round 2)"
    ended = [e for e in evs(k, "cross_instrument") if e["what"] == "ended"][-1]
    assert ended["by"] == "J0" and ended["reason"] == "the guild defied the council"


def test_the_guild_levy_template_levies_each_round_until_the_charter_is_revoked(tmp_path):
    sp = world(instruments=[CHARTER], rounds=4,
               j0_laws=[{"template": "Guild Levy", "params": {"GUILD": "A1", "RATE": 0.1, "CAP": 4}}])
    sched = [{"id": "revoke", "at": {"round": 2, "phase": "round_start"}, "op": "enact_law",
              "args": {"code": law("Revocation", 'def on_enact():\n    end_instrument("C1", "revoked")\n')}}]
    inst, rd = run(tmp_path, sp, schedule=sched)
    levies = [(e["round"], e["data"]["qty"]) for e in file_events(rd, "cross_act") if e["data"]["power"] == "levy"]
    assert levies == [(0, 4.0), (1, 4.0)]                              # min(CAP, 10% of 50, then of 46); none after round 2's revocation
    from cybertron import start as STT
    k = STT._kernel_at(rd, 4)[1]
    lev = next(l for l in k.w["laws"].values() if l["title"] == "Guild Levy")
    assert [r.get("levied") for r in lev["public"]["register"]] == [4.0, 4.0, 0, 0]
    assert lev["public"]["register"][2]["why"] == "no levy power over A1"
    assert AC.bal(k, "assoc:A1", "penny") == 42


# ---------------------------------------------------------------------- acceptance: a guild cannot act on the council's store
def test_the_guild_cannot_touch_the_council_store_without_a_power(tmp_path):
    k = kernel(tmp_path, world())
    lid = assoc_law(k, "A1", law("Grab", 'def on_enact():\n    public["levy"] = levy_on("J0", "food", 2, "S1")\n'
                                          '    public["move"] = move("store:S1", "treasury", "food", 2)\n'
                                          '    public["pay"] = pay_out_of("J0", "Ada", "penny", 2)\n'), "Ada")
    assert pub(k, lid) == {"levy": False, "move": False, "pay": False}
    assert AC.bal(k, "store:S1", "food") == 30
    assert {r["fn"] for r in evs(k, "cross_refused")} == {"levy_on", "pay_out_of"}
    # a treaty: J0 grants the guild a levy of food from its granary (2 a round), the guild accepts
    t = enact(k, law("Treaty", 'def on_enact():\n    public["t"] = offer_treaty("A1", [{"power": "levy", "item": "food", "qty": 2}], [])\n'))
    tid = pub(k, t)["t"]
    assert CR.state(k)["instruments"][tid]["status"] == "offered"
    assert CR.holds(k, "A1", "J0", "levy") is None                    # not before the guild accepts
    lid = assoc_law(k, "A1", law("Accept", f'def on_enact():\n    public["ok"] = accept_instrument("{tid}")\n'
                                            '    public["got"] = levy_on("J0", "food", 3, "S1", "S2")\n'), "Ada")
    assert pub(k, lid) == {"ok": True, "got": 2.0}
    assert AC.bal(k, "store:S1", "food") == 28 and AC.bal(k, "store:S2", "food") == 42


# ---------------------------------------------------------------------- acceptance: a league court's ruling binds a member's office
def _court_world(tmp_path, member):
    ins = [{"kind": "membership", "id": "M1", "league": "J0", "member": "A1", "powers": ["remove", "appoint"]}] if member else []
    k = kernel(tmp_path, world(instruments=ins, extra={"actions.core_only": False}))
    lid = enact(k, law("League Court", '''
def misrule(accused, accuser):
    public["removed"] = remove_from("A1", "head", accused)
    public["seated"] = appoint_to("A1", "head", accuser)

def on_enact():
    clause("misrule", "an officer of a member institution misrules it", misrule)
'''))
    k.w["agents"]["Cy"]["rights"].append("judge")
    if "judge" not in k.w["rights"]:
        k.w["rights"].append("judge")
    A.act(k, "Bo", "accuse", {"agent": "Ada", "law": lid, "clause": "misrule", "evidence": []})
    A.act(k, "Cy", "rule", {"case": f"C{k.w['case_seq']}", "verdict": "guilty", "reason": "seen"})
    return k, lid


def test_a_league_court_ruling_binds_a_member_office(tmp_path):
    k, lid = _court_world(tmp_path / "m", member=True)
    assert pub(k, lid) == {"removed": True, "seated": True}
    assert IN.holders(k, "A1", "head") == ["Bo"]
    assert [(a["power"], a["agent"]) for a in evs(k, "cross_act")] == [("remove", "Ada"), ("appoint", "Bo")]
    k, lid = _court_world(tmp_path / "x", member=False)               # no membership: the ruling binds nobody's office
    assert pub(k, lid) == {"removed": False, "seated": False} and IN.holders(k, "A1", "head") == ["Ada"]
    assert "holds no power to remove the officers of A1 (the Weavers)" in evs(k, "cross_refused")[0]["why"]


# ---------------------------------------------------------------------- hierarchy, enact, read, veto
def test_a_charter_incorporates_its_child_while_in_force(tmp_path):
    k = kernel(tmp_path, world(instruments=[CHARTER]))
    assert IN.get(k, "A1")["parent"] == "J0"
    lid = enact(k, law("Code", 'def on_enact():\n    public["l"] = enact_in("A1", "title = \\"Guild Rule\\"\\nintent = \\"x\\"\\n")\n'
                                '    public["s"] = state_of("A1")["offices"]\n    public["d"] = state_of("A2")\n'))
    new = pub(k, lid)["l"]
    assert k.w["laws"][new]["jurisdiction"] == "A1" and k.w["laws"][new]["status"] == "active" and new in IN.get(k, "A1")["laws"]
    assert pub(k, lid)["s"] == {"head": ["Ada"]} and pub(k, lid)["d"] is None   # no read power over the Dyers
    CR.end(k, CR.state(k)["instruments"]["C1"], "A1", reason="renounced")      # the child renounces: it is free again
    assert IN.get(k, "A1")["parent"] is None and CR.powers_over(k, "J0", "A1") == []


def test_a_veto_lets_another_institutions_laws_block_its_acts(tmp_path):
    block = law("Embargo", '''
def before_move(p, chain):
    if p["src"] == "assoc:A1" and p["qty"] > 10:
        return {"block": True, "reason": "the Dyers forbid it"}
''')
    pay = law("Pay", 'def on_enact():\n    public["ok"] = move("treasury", "Ada", "penny", 20)\n')
    k = kernel(tmp_path / "none", world())
    assoc_law(k, "A2", block, "Ed")
    lid = assoc_law(k, "A1", pay, "Ada")
    assert pub(k, lid)["ok"] is True                                   # without a veto the Dyers' law never sees the Weavers' acts
    tr = {"kind": "treaty", "id": "T1", "parties": ["A1", "A2"], "grants": {"A2": ["veto"]}}
    k = kernel(tmp_path / "veto", world(instruments=[tr]))
    assoc_law(k, "A2", block, "Ed")
    lid = assoc_law(k, "A1", pay, "Ada")
    assert pub(k, lid)["ok"] is False and AC.bal(k, "assoc:A1", "penny") == 50
    v = evs(k, "cross_act")[-1]
    assert v["power"] == "veto" and v["holder"] == "A2" and v["over"] == "A1" and v["instrument"] == "T1"


# ---------------------------------------------------------------------- templates
def test_the_charter_and_treaty_templates_offer_and_accept(tmp_path):
    k = kernel(tmp_path, world())
    j = enact(k, _inst("Charter", {"CHILD": "A1", "NAME": "Weavers' Charter"}))
    cid = pub(k, j)["charter"]
    assert CR.state(k)["instruments"][cid]["status"] == "offered"
    assoc_law(k, "A1", _inst("Charter", {"CHILD": "A1"}), "Ada")
    rec = CR.state(k)["instruments"][cid]
    assert rec["status"] == "active" and rec["name"] == "Weavers' Charter" and IN.get(k, "A1")["parent"] == "J0"
    assert CR.powers_over(k, "J0", "A1") == ["read", "levy", "appoint", "remove"]
    k.repeal(j)                                                        # repealing the parent's copy revokes it
    assert rec["status"] == "ended" and rec["ended_by"] == "J0"
    t1 = assoc_law(k, "A1", _inst("Treaty", {"OTHER": "A2", "GIVE": ["read"], "TAKE": ["read", "veto"]}), "Ada")
    tid = pub(k, t1)["treaty"]
    assoc_law(k, "A2", _inst("Treaty", {"OTHER": "A1", "GIVE": ["read", "veto"], "TAKE": ["read"]}), "Ed")
    assert CR.state(k)["instruments"][tid]["status"] == "active"
    assert CR.powers_over(k, "A1", "A2") == ["read", "veto"] and CR.powers_over(k, "A2", "A1") == ["read"]


def _inst(name, params):
    return LB.instantiate(name, params)


# ---------------------------------------------------------------------- land and labour (coordination board, loops 2 and 4)
def _fields_world(tmp_path):
    sp = world(extra={"subsistence.fields.enabled": True})
    sp["start"]["farms"] = [{"owner": "J0", "camp": "fields", "plots": 2}]
    k = kernel(tmp_path, sp)
    camp = next(c for c, v in k.w["camps"].items() if v.get("plots"))
    return k, camp


def test_plots_granted_as_tenures_with_service_and_seized(tmp_path):
    k, camp = _fields_world(tmp_path)
    pid = next(p["id"] for p in k.w["camps"][camp]["plots"] if p.get("holder") == "J0")
    lid = enact(k, law("Manor", f'def on_enact():\n    public["g"] = grant_plot("{camp}", {pid}, "Bo", '
                                f'{{"work": "harvest", "qty": 1}})\n'
                                '    public["d"] = demand_service("Bo", "harvest", 2)\n'
                                '    public["x"] = demand_service("Fay", "harvest", 1)\n'))
    assert pub(k, lid)["g"] is True and pub(k, lid)["x"].startswith("W")   # J0 compels its members (everyone, jurisdictions off)
    no = assoc_law(k, "A2", law("Corvee", 'def on_enact():\n    public["x"] = demand_service("Bo", "harvest", 1)\n'), "Ed")
    assert pub(k, no)["x"] is False and "owes A2 (the Dyers) no service" in evs(k, "cross_refused")[-1]["why"]
    plot = next(p for p in k.w["camps"][camp]["plots"] if p["id"] == pid)
    assert plot["holder"] == "Bo"
    lines = CR.state_lines(k, "Bo")
    assert any(f"You hold {camp} plot {pid} of J0 (the Council)" in x for x in lines)
    assert any(x.startswith("DUE: service to J0 (the Council): harvest 2 more time(s)") for x in lines)
    forest = next(c for c, v in k.w["camps"].items() if v.get("resource") == "food" and not v.get("plots"))
    A.act(k, "Bo", "harvest", {"camp": forest})
    sid = pub(k, lid)["d"]
    assert CR.state(k)["services"][sid]["done"] == 1.0
    CR.end_round(k)                                                    # one short at the round's end: missed
    assert CR.service_status(k, CR.state(k)["services"][sid]) == "missed" and evs(k, "service_missed")
    lid = enact(k, law("Evict", f'def on_enact():\n    public["s"] = seize_plot("{camp}", {pid})\n'))
    assert pub(k, lid)["s"] is True and plot["holder"] == "J0"
    assert [t["status"] for t in CR.state(k)["tenures"]] == ["seized"]


# ---------------------------------------------------------------------- the prompt, the spec check
def test_prompt_lines_are_short_in_world_terms_and_reach_only_those_concerned(tmp_path):
    k = kernel(tmp_path, world(instruments=[CHARTER]))
    line = CR.state_lines(k, "Ada")
    assert line == ["Charter C1 'Charter of the Weavers' between J0 (the Council) and A1 (the Weavers). J0 over A1: read records, "
                    "levy up to 5 penny a round, appoint officers, remove officers, enact laws (laws use these powers: read_law for "
                    "the calls)."]
    assert CR.state_lines(k, "Cy") == line and CR.state_lines(k, "Bo") == line    # J0's officer; a guild member
    assert CR.state_lines(k, "Fay") == [] and CR.state_lines(k, "Ed") == []       # the Dyers are not concerned
    from cybertron import agents as AG
    assert line[0] in AG.state_view(k, "Ada")
    enact(k, law("Offer", 'def on_enact():\n    offer_treaty("A2", ["read"], ["read"])\n'))
    assert CR.state_lines(k, "Ed")[-1].endswith('In force once A2 accepts by a law calling accept_instrument("T1").')
    m = LD.resolve(k.spec)["mapping"]
    assert m["levy_on"] == "prompt" and "Institutions: " in LD.api_doc(LD.resolve(k.spec), "")
    assert "Charter" in A.library_index(k.inst)


def test_spec_check():
    sp = world(instruments=[CHARTER])
    assert not SC.validate(sp)
    bad = world(instruments=[{"kind": "charter", "parent": "J0", "child": "A1", "powers": ["rule", {"power": "read", "qty": 3}]},
                             {"kind": "treaty", "parties": ["A1"], "grants": {}}, {"kind": "alliance"}])
    errs = SC.validate(bad)
    assert any("unknown power 'rule'" in e for e in errs) and any("only levy and pay take" in e for e in errs)
    assert any("parties: two institution ids" in e for e in errs) and any("kind charter, treaty or membership" in e for e in errs)
    nov2 = world()
    nov2["law"] = {"v2": False}
    assert any("needs law.v2: true" in e for e in SC.validate(nov2))
    assert "institutions.cross" in SC.OPT_IN


def test_an_instrument_naming_no_institution_fails_before_the_first_round(tmp_path):
    with pytest.raises(ValueError, match="institutions.cross.instruments"):
        run(tmp_path, world(instruments=[{"kind": "membership", "league": "J0", "member": "A9", "powers": ["remove"]}]))


def test_a_refused_invocation_rolls_back_a_levy(tmp_path):
    """law.atomic: the journal's image holds k.w["cross"] like any key, so a refusal undoes the levy and its use of the limit."""
    k = kernel(tmp_path, world(instruments=[CHARTER]))
    enact(k, law("Levy Then Refuse", 'def on_enact():\n    levy_on("A1", "penny", 4)\n    refuse("changed my mind")\n'))
    assert AC.bal(k, "assoc:A1", "penny") == 50 and CR.state(k)["used"] == {}
    assert not [e for e in evs(k, "cross_act") if e["power"] == "levy"]
    lid = enact(k, law("Levy", 'def on_enact():\n    public["got"] = levy_on("A1", "penny", 9)\n'))
    assert pub(k, lid)["got"] == 5.0                                   # the whole limit is still there
