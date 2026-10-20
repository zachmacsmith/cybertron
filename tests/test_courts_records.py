"""Courts and records (docs/review/31_institutions/08_integration.md items 0.11, 1.7, 1.8, 2.2, 2.8): sell_to_window, read_register
and read_law with a version, the Bench Act, Recusal Act, Graded Contract Enforcement, Certified Contract Registry and Bill
Certification templates, counsel acting for a client under a retainer (represent), withdraw_case and cases_of. Each template is
enacted in a small scripted world (kernel level: the survival base with institutions, law.v2 and contracts) and its law_effect is
checked to be non-inert. Everything here is opt-in: the last tests check that no existing world gains an action, a lookup or a
documented function."""
from __future__ import annotations

import re

import pytest

from cybertron import accounts as AC
from cybertron import action_registry as AR
from cybertron import actions as A
from cybertron import context as CX
from cybertron import counsel as CN
from cybertron import courts as CO
from cybertron import generator
from cybertron import lawdocs as LD
from cybertron import library as LB
from cybertron import spec as S
from cybertron.actions import ActionError
from cybertron.kernel import Kernel

NAMES = ["Ada", "Bo", "Cy", "Di", "Ed", "Fay"]
TORTS = ('title = "Torts"\nintent = "A tort is heard by a judge."\ndef pen(accused, accuser, remedy):\n'
         '    gazette("tort: " + accused)\ndef on_enact():\n    clause("tort", "a tort", pen)\n')


def make(enforcement="escrow_court"):
    """Six agents in J0 (no jurisdictions), law.v2, contracts (courts hear breaches), institutions, every action (not core-only)."""
    sp = S.load("cybertron/specs/survival/base.yaml")
    sp = S.deep_merge(sp, {
        "agents": {"worker": 6, "names": list(NAMES)}, "rounds": 8, "parallel_calls": 1, "turns": "sequential",
        "institutions": {"unified": True, "grants": True, "succession": True, "office_control": True},
        "jurisdictions": {"enabled": False}, "contracts": {"scripted": False, "enforcement": enforcement},
        "life": {"age_structure": "elapsed", "elapsed": [20, 30]}, "shared_archive": {"enabled": False},
        "actions": {"core_only": False}})
    sp["regime"] = {"base": None, "name": "t", "constitution": "assembly"}
    inst = generator.generate(sp, 1)
    k = Kernel(inst)
    k.enact(k.new_law(inst["constitution_code"], "constitution"))
    k.start_round()
    return k


def enact(k, name, params=None, author="Ada"):
    lid = k.new_law(LB.instantiate(name, params or {}), author)
    k.enact(lid)
    assert k.w["laws"][lid]["status"] == "active", k.w["laws"][lid]["status"]
    return lid


def enact_code(k, code, author="Ada"):
    lid = k.new_law(code, author)
    k.enact(lid)
    return lid


def effect(k, lid):
    return [e["data"] for e in k.events if e["type"] == "law_effect" and e["data"]["law"] == lid][-1]


def act(k, aid, verb, /, **args):
    return A.act(k, aid, verb, args)


def office(k, right, *holders):
    if right not in k.w["rights"]:
        k.apply("create_right", right=right)
    for a in holders:
        k.apply("grant_right", agent=a, right=right)


def judge(k, *who):
    for a in who:
        if "judge" not in k.w["agents"][a]["rights"]:
            k.w["agents"][a]["rights"].append("judge")


def last_case(k):
    return max(k.w["cases"], key=lambda c: int(c[1:]))


def available(k, aid):
    a = next(x for x in k.inst["agents"] if x["id"] == aid)
    return {x.name for x in AR.available(k.inst, k, a)}


def found(k, aid, code, name="C"):
    return re.search(r"A\d+", act(k, aid, "create_contract", name=name, code=code)).group()


def retainer(k, client="Ada", counsel="Bo"):
    cid = found(k, client, LB.instantiate("Retainer", {"PARTIES": {client: "client", counsel: "counsel"}}), "Retainer")
    act(k, counsel, "join_contract", contract=cid)
    return cid


# ---------------------------------------------------------------------- 0.11 sell_to_window
def test_sell_to_window_turns_a_treasury_s_goods_into_coins():
    k = make()
    enact_code(k, 'title = "Coin"\nintent = "crown, convertible"\ndef on_enact():\n    create_currency("crown")\n'
                  '    set_convertible("crown")\n')
    firm = found(k, "Ada", 'title = "Mine Co"\nintent = "sells its copper"\ndef on_round_end(r):\n'
                           '    q = balance(treasury(), "copper")\n    if q > 0:\n        sell_to_window("crown", "copper", q)\n')
    k._add("Ada", "copper", 10)
    act(k, "Ada", "transfer", to=firm, item="copper", qty=4)
    t = AC.treasury_of(k, firm)
    p = k.price("crown")
    k.end_round()
    k.start_round()
    assert AC.holdings(k, t).get("copper", 0) == 0
    assert AC.holdings(k, t)["crown"] == pytest.approx(4 * k.unit_value("copper") / p)
    sale = [e for e in k.events if e["type"] == "window_sale"][-1]
    assert sale["vis"] == "public" and sale["data"]["treasury"] == t and sale["data"]["qty"] == 4
    # J0's treasury is the reserve itself: nothing to sell, and the failure is told (not inert: it tried and failed loudly)
    lid = enact_code(k, 'title = "Sell"\nintent = "t"\ndef on_enact():\n    sell_to_window("crown", "copper", 1)\n')
    fx = effect(k, lid)
    assert fx["failed_calls"] and fx["failed_calls"][0]["fn"] == "sell_to_window" and "own reserve" in fx["failed_calls"][0]["reason"]
    assert k.api_for(lid)["sell_to_window"]("crown", "copper", 0) == 0


def test_sell_to_window_refuses_a_currency_without_a_window():
    k = make()
    enact_code(k, 'title = "Coin"\nintent = "t"\ndef on_enact():\n    create_currency("crown")\n')
    firm = found(k, "Ada", 'title = "Co"\nintent = "t"\n')
    k._add("Ada", "copper", 3)
    act(k, "Ada", "transfer", to=firm, item="copper", qty=3)
    lid = k.w["contracts"]["assoc"][firm]["laws"][0] if "assoc" in k.w["contracts"] else AC.assocs(k)[firm]["laws"][0]
    assert k.api_for(lid)["sell_to_window"]("crown", "copper", 3) == 0
    assert AC.holdings(k, AC.treasury_of(k, firm))["copper"] == 3


# ---------------------------------------------------------------------- 1.7 read_law with a version
def test_read_law_reads_any_earlier_version_and_a_diff():
    from cybertron import amendment as AM
    k = make()
    v1 = 'title = "Stipend"\nintent = "Ada gets 1 food"\ndef on_round_end(r):\n    move("reserve", "Ada", "food", 1)\n'
    lid = enact_code(k, v1)
    k.enact(AM.amendment_draft(k, lid, v1.replace('"food", 1', '"food", 2').replace("1 food", "2 food"), "Bo", "more"))
    assert len(k.w["laws"][lid]["patches"]) == 1
    old = act(k, "Cy", "read_law", law=lid, version=1)
    assert "version 1 of 2" in old and 'move("reserve", "Ada", "food", 1)' in old
    cur = act(k, "Cy", "read_law", law="Stipend", version=2)
    assert "(current)" in cur and '"food", 2' in cur and "by Bo" in cur
    diff = CX.lookup(k, "Cy", "read_law", {"law": lid, "version": 1, "against": 2})
    assert "-    move(\"reserve\", \"Ada\", \"food\", 1)" in diff and "+    move(\"reserve\", \"Ada\", \"food\", 2)" in diff
    with pytest.raises(ActionError, match="no version 3"):
        act(k, "Cy", "read_law", law=lid, version=3)
    assert act(k, "Cy", "read_law", law=lid) == CX.read_law(k, "Cy", lid)    # without a version: as before


# ---------------------------------------------------------------------- 1.8 the Certified Contract Registry and read_register
def test_certified_registry_needs_the_clerk_and_read_register_respects_read():
    k = make()
    assert "read_register" in CN.world_hidden(k)                        # no law declares READ yet: the look-up does not exist
    with pytest.raises(ActionError, match="unknown action 'read_register'"):
        act(k, "Ada", "read_register")
    office(k, "J0.clerk", "Cy")
    judge(k, "Ed")
    lid = enact(k, "Certified Contract Registry", {"DAMAGES_ITEM": "food", "DAMAGES": 2})
    assert not effect(k, lid)["inert"]
    act(k, "Ada", "invoke", action="register_agreement", args=["Bo", "Bo delivers 2 food a round"])
    act(k, "Bo", "invoke", action="confirm_agreement", args=[1])
    with pytest.raises(ActionError):                                    # only the clerk certifies
        act(k, "Ada", "invoke", action="certify_agreement", args=[1])
    k.w["agents"]["Bo"]["holdings"]["food"] = 10.0
    act(k, "Ada", "accuse", agent="Bo", law=lid, clause="registered_agreement", evidence=[])
    act(k, "Ed", "rule", case=last_case(k), verdict="guilty", reason="before certification")
    assert k.bal("Bo", "food") == 10                                    # an uncertified agreement binds nobody
    act(k, "Cy", "invoke", action="certify_agreement", args=[1])
    assert "read_register" not in CN.world_hidden(k) and "read_register" in available(k, "Di")
    assert "read_register" in CX.lookup_names(k)
    act(k, "Ada", "accuse", agent="Bo", law=lid, clause="registered_agreement", evidence=[])
    act(k, "Ed", "rule", case=last_case(k), verdict="guilty", reason="certified", remedy=4)
    assert k.bal("Bo", "food") == 6                                     # the judge's remedy, within the cap
    # read_register: the register for all, the agreements (with terms) for their parties and the clerk
    assert "Bo delivers 2 food" in act(k, "Ada", "read_register", law=lid, book="agreements")
    assert "Bo delivers 2 food" in act(k, "Cy", "read_register", law=lid, book="agreements")
    with pytest.raises(ActionError, match="open only to its parties"):
        act(k, "Di", "read_register", law=lid, book="agreements")
    reg = act(k, "Di", "read_register", law="Certified Contract Registry", book="register")
    assert '"status": "registered"' in reg and "terms" not in reg
    books = act(k, "Di", "read_register", law=lid)
    assert "register" in books and "breaches" in books and "only the rows that name you" in books
    assert lid in act(k, "Di", "read_register")
    k.repeal(lid)
    assert "registered" in act(k, "Di", "read_register", law=lid, book="register")   # a repealed law's register stays readable
    with pytest.raises(ActionError, match="declares no readable register"):
        act(k, "Di", "read_register", law=k.w["law_order"][0])


# ---------------------------------------------------------------------- 1.8 the Bench Act
def test_bench_act_ties_the_judge_right_to_the_office():
    k = make()
    office(k, "J0.judge", "Ada")
    judge(k, "Bo")
    lid = enact(k, "Bench Act")
    fx = effect(k, lid)
    assert not fx["inert"] and "Ada gains right judge" in fx["changes"] and "Bo loses right judge" in fx["changes"]
    assert k.holders("judge") == ["Ada"] and CO.rules(k, "J0")["judges"] == "J0.judge"
    assert CO.opt_rule(k, "J0", "withdrawal") is True
    k.apply("grant_right", agent="Cy", right="J0.judge")               # appointed: judges at once
    k.apply("revoke_right", agent="Ada", right="J0.judge")             # removed: no longer judges
    assert k.holders("judge") == ["Cy"]
    k.w["agents"]["Di"]["rights"].append("judge")                      # a judge right outside the office ...
    k.end_round()
    k.start_round()
    assert k.holders("judge") == ["Cy"]                                 # ... is revoked at the next round start


# ---------------------------------------------------------------------- 1.8 the Recusal Act
def test_recusal_act_blocks_a_party_or_a_paid_judge():
    k = make()
    judge(k, "Di", "Ed")
    lid = enact(k, "Recusal Act", {"GIFT_LIMIT": 3, "LOOKBACK": 2})
    assert not effect(k, lid)["inert"]
    torts = enact_code(k, TORTS)
    k._add("Ada", "food", 5)
    act(k, "Ada", "transfer", to="Di", item="food", qty=3)              # a gift to a judge
    act(k, "Ada", "accuse", agent="Bo", law=torts, clause="tort", evidence=[])
    case = last_case(k)
    with pytest.raises(ActionError, match="Recusal Act: Di received 3"):
        act(k, "Di", "rule", case=case, verdict="guilty", reason="x")
    act(k, "Ed", "rule", case=case, verdict="guilty", reason="x")       # another judge hears it
    act(k, "Bo", "accuse", agent="Ed", law=torts, clause="tort", evidence=[])
    with pytest.raises(ActionError, match="Ed is a party to the case"):
        act(k, "Ed", "rule", case=last_case(k), verdict="not guilty", reason="me")
    rec = k.w["laws"][lid]["public"]["recusals"]
    assert [r["judge"] for r in rec] == ["Di", "Ed"]
    assert "Di received 3" in act(k, "Fay", "read_register", law=lid, book="recusals")
    for _ in range(2):                                                  # the gift ages out after LOOKBACK rounds
        k.end_round()
        k.start_round()
    act(k, "Ada", "accuse", agent="Cy", law=torts, clause="tort", evidence=[])
    act(k, "Di", "rule", case=last_case(k), verdict="not guilty", reason="clean")


# ---------------------------------------------------------------------- 1.8 Graded Contract Enforcement
def test_graded_contract_enforcement_awards_the_judge_s_remedy_once():
    k = make()
    cid = found(k, "Ada", 'title = "Rules"\nintent = "t"\ndef on_round_start(r):\n    if r == 1:\n'
                          '        breach("Bo", "dues", "none", "Ada")\n        breach("Bo", "dues2", "none", "Ada")\n')
    act(k, "Bo", "join_contract", contract=cid)
    lid = enact(k, "Graded Contract Enforcement", {"ITEM": "food", "DAMAGES_CAP": 5, "DEFAULT": 1})
    fx = effect(k, lid)
    assert not fx["inert"] and any("breach_of_contract" in c for c in fx["changes"])
    k.end_round()
    k.start_round()                                                     # round 1: two breaches recorded, Ada the victim
    judge(k, "Cy")
    k.w["agents"]["Bo"]["holdings"]["food"] = 20.0
    a0 = k.bal("Ada", "food")
    act(k, "Ada", "accuse", agent="Bo", law=lid, clause="breach_of_contract", evidence=[])
    act(k, "Cy", "rule", case=last_case(k), verdict="guilty", reason="the record", remedy=9)
    assert k.bal("Bo", "food") == 15 and k.bal("Ada", "food") - a0 == 5    # 9 asked, capped at 5, paid to the victim
    award = k.w["laws"][lid]["public"]["awards"][-1]
    assert award["breaches"] == [f"{cid}:1", f"{cid}:2"] and award["to"] == "Ada" and award["paid"] == 5
    act(k, "Ada", "accuse", agent="Bo", law=lid, clause="breach_of_contract", evidence=[])
    act(k, "Cy", "rule", case=last_case(k), verdict="guilty", reason="again")
    assert k.bal("Bo", "food") == 15                                    # each breach once


def test_graded_contract_enforcement_without_a_remedy_awards_the_default_per_breach():
    k = make()
    cid = found(k, "Ada", 'title = "Rules"\nintent = "t"\ndef on_round_start(r):\n    if r == 1:\n'
                          '        breach("Bo", "dues", "none", "Ada")\n        breach("Bo", "dues2", "none", "Ada")\n')
    act(k, "Bo", "join_contract", contract=cid)
    lid = enact(k, "Graded Contract Enforcement", {"ITEM": "food", "DAMAGES_CAP": 5, "DEFAULT": 1})
    k.end_round()
    k.start_round()
    judge(k, "Cy")
    k.w["agents"]["Bo"]["holdings"]["food"] = 20.0
    act(k, "Ada", "accuse", agent="Bo", law=lid, clause="breach_of_contract", evidence=[])
    act(k, "Cy", "rule", case=last_case(k), verdict="guilty", reason="the record")
    assert k.bal("Bo", "food") == 18


# ---------------------------------------------------------------------- 2.8 Bill Certification
def _citizens(k):
    for a in ("Ada", "Bo", "Cy", "Di"):
        for r in ("propose", "vote"):
            if r not in k.w["agents"][a]["rights"]:
                k.w["agents"][a]["rights"].append(r)


def _pass_ballots(k):
    for b in [b for b in k.w["ballots"].values() if b["status"] == "open"]:
        for a in ("Ada", "Bo", "Cy", "Di"):
            act(k, a, "vote", ballot=b["id"], choice="yes")
    for _ in range(2):
        k.end_round()
        k.start_round()


def test_bill_certification_registers_bills_and_can_require_the_certificate():
    k = make()
    office(k, "J0.clerk", "Cy")
    _citizens(k)
    lid = enact(k, "Bill Certification", {"REQUIRE": True})
    assert not effect(k, lid)["inert"]
    stip = 'title = "Stipend {n}"\nintent = "{a} gets 1 food a round"\ndef on_round_end(r):\n    move("reserve", "{a}", "food", 1)\n'
    act(k, "Ada", "propose", code=stip.format(n=1, a="Ada"))
    act(k, "Bo", "propose", code=stip.format(n=2, a="Bo"))
    bills = k.w["laws"][lid]["public"]["bills"]
    one, two = bills[0]["law"], bills[1]["law"]
    assert [b["status"] for b in bills] == ["pending", "pending"]
    with pytest.raises(ActionError):
        act(k, "Ada", "invoke", action="certify_bill", args=[one, "mine is fine"])   # not the clerk
    act(k, "Cy", "invoke", action="certify_bill", args=[one, "pays Ada as its intent says"])
    _pass_ballots(k)
    assert k.w["laws"][one]["status"] == "active"
    assert k.w["laws"][two]["status"] != "active"                       # passed its ballot, but has no certificate
    assert any(e["type"] == "primitive_blocked" and e["data"].get("law") == two for e in k.events)
    reg = act(k, "Di", "read_register", law=lid, book="bills")
    assert '"status": "certified"' in reg and '"status": "pending"' in reg


def test_bill_certification_only_marks_bills_by_default():
    k = make()
    office(k, "J0.clerk", "Cy")
    _citizens(k)
    lid = enact(k, "Bill Certification")
    act(k, "Ada", "propose", code='title = "Stipend"\nintent = "Ada gets food"\ndef on_round_end(r):\n    move("reserve", "Ada", "food", 1)\n')
    bill = k.w["laws"][lid]["public"]["bills"][0]["law"]
    act(k, "Cy", "invoke", action="refuse_bill", args=[bill, "it pays from the reserve without a cap"])
    _pass_ballots(k)
    assert k.w["laws"][bill]["status"] == "active"
    assert k.w["laws"][lid]["public"]["bills"][0]["status"] == "refused"


# ---------------------------------------------------------------------- 2.2 counsel, cases_of, withdraw_case
def test_counsel_acts_for_a_client_under_a_retainer():
    k = make()
    torts = enact_code(k, TORTS)
    judge(k, "Ed")
    assert "represent" in CN.world_hidden(k)                            # no retainer: the action does not exist
    with pytest.raises(ActionError, match="unknown action 'represent'"):
        act(k, "Bo", "represent", client="Ada", action="accuse")
    retainer(k, "Ada", "Bo")
    assert CN.counsel_of(k, "Ada") == ["Bo"] and CN.clients_of(k, "Bo") == ["Ada"]
    assert "represent" in available(k, "Bo") and "represent" not in available(k, "Cy")
    act(k, "Ada", "post", text="Cy took my food")
    eid = [e for e in k.events if e["type"] in ("post", "channel_post")][-1]["id"]
    out = act(k, "Bo", "represent", client="Ada", action="accuse", agent="Cy", law=torts, clause="tort", evidence=[eid])
    case = last_case(k)
    c = k.w["cases"][case]
    assert out.startswith(f"Case {case} filed for Ada") and c["accuser"] == "Ada" and c["counsel"] == {"Ada": "Bo"}
    assert c["evidence"] == [eid]
    ev = [e for e in k.events if e["type"] == "counsel_acted"][-1]
    assert ev["vis"] == "public" and ev["agent"] == "Bo" and ev["data"]["client"] == "Ada"
    with pytest.raises(ActionError, match="not Ada's counsel"):
        act(k, "Cy", "represent", client="Ada", action="accuse", agent="Di", law=torts, clause="tort", evidence=[])
    with pytest.raises(ActionError, match="cannot respond"):
        act(k, "Bo", "represent", client="Ada", action="respond", case=case, evidence=[])
    # cases_of: public data for any law (a retainer paid per case)
    views = k.api_for(torts)["cases_of"]("Bo")
    assert [v["id"] for v in views] == [case] and views[0]["counsel"] == {"Ada": "Bo"}
    assert "counsel" not in k.api_for(torts)["case"](case) or k.api_for(torts)["case"](case)["counsel"] == {"Ada": "Bo"}
    # the accused retains counsel too, who answers and appeals
    retainer(k, "Cy", "Di")
    act(k, "Di", "represent", client="Cy", action="respond", case=case, evidence=[eid])
    assert k.w["cases"][case]["counsel"] == {"Ada": "Bo", "Cy": "Di"}
    enact_code(k, 'title = "Appeals"\nintent = "t"\ndef on_enact():\n    create_right("appellate")\n'
                  '    set_court_rule("appeal_judges", "appellate")\n    set_court_rule("appeal_window", 2)\n')
    k.apply("grant_right", agent="Fay", right="appellate")
    act(k, "Ed", "rule", case=case, verdict="guilty", reason="the post")
    assert "Appeal for Cy of" in act(k, "Di", "represent", client="Cy", action="appeal", case=case, reason="hearsay")
    assert k.w["cases"][case]["stage"] == 2
    # a polity may forbid counsel in its courts
    enact_code(k, 'title = "No Counsel"\nintent = "t"\ndef on_enact():\n    set_court_rule("counsel", False)\n')
    with pytest.raises(ActionError, match="counsel may not act"):
        act(k, "Bo", "represent", client="Ada", action="accuse", agent="Cy", law=torts, clause="tort", evidence=[])


def test_withdraw_case_needs_a_law_that_allows_it():
    k = make()
    torts = enact_code(k, TORTS)
    judge(k, "Ed")
    act(k, "Ada", "accuse", agent="Bo", law=torts, clause="tort", evidence=[])
    case = last_case(k)
    assert "withdraw_case" in CN.world_hidden(k)
    with pytest.raises(ActionError, match="unknown action 'withdraw_case'"):
        act(k, "Ada", "withdraw_case", case=case)
    office(k, "J0.judge", "Ed")
    enact(k, "Bench Act")                                               # WITHDRAWAL True sets the court rule
    assert "withdraw_case" in available(k, "Ada") and "withdraw_case" not in available(k, "Bo")
    with pytest.raises(ActionError, match="not a case Bo filed"):
        act(k, "Bo", "withdraw_case", case=case)
    assert act(k, "Ada", "withdraw_case", case=case, reason="settled") == f"Case {case} withdrawn."
    c = k.w["cases"][case]
    assert c["status"] == "dismissed" and c["withdrawn"]["by"] == "Ada"
    with pytest.raises(ActionError, match="no open case"):
        act(k, "Ed", "rule", case=case, verdict="guilty", reason="late")
    assert [e for e in k.events if e["type"] == "case_withdrawn"][-1]["vis"] == "public"
    retainer(k, "Ada", "Bo")                                            # counsel may withdraw for its client
    act(k, "Ada", "accuse", agent="Cy", law=torts, clause="tort", evidence=[])
    act(k, "Bo", "represent", client="Ada", action="withdraw_case", case=last_case(k))
    assert k.w["cases"][last_case(k)]["withdrawn"]["counsel"] == "Bo"


# ---------------------------------------------------------------------- opt-in: no existing world changes
@pytest.mark.parametrize("preset", ["E6", "society", "cybertron/specs/millbrook.yaml"])
def test_existing_worlds_have_none_of_it(preset):
    inst = generator.generate(S.apply_overrides(S.load(preset), ["shared_archive.enabled=false"]), 1)
    k = Kernel(inst)
    assert CN.world_hidden(k) == {"represent", "withdraw_case", "read_register"}
    assert "read_register" not in CX.lookup_names(k)
    for a in inst["agents"][:4]:
        assert not {"represent", "withdraw_case", "read_register"} & {x.name for x in AR.available(inst, k, a)}
    with pytest.raises(ActionError) as e:
        A.act(k, inst["agents"][0]["id"], "no_such_action", {})
    assert not re.search(r"\b(represent|withdraw_case|read_register)\b", str(e.value))
    mapping = LD.resolve(inst["spec"])["mapping"]
    assert "sell_to_window" not in mapping and "cases_of" not in mapping


def test_the_new_law_functions_are_documented_where_a_world_starts_with_them():
    sp = S.load("cybertron/specs/millbrook.yaml")
    assert not LD.REQUIRES["cases_of"](sp)
    sp2 = S.deep_merge(sp, {"start": {"contracts": [{"template": "Retainer", "founder": "Ada"}]}})
    assert LD.REQUIRES["cases_of"](sp2)
    sp3 = S.deep_merge(sp, {"start": {"laws": [{"code": 'title = "x"\nintent = "y"\ndef on_round_end(r):\n'
                                                        '    sell_to_window("penny", "copper", 1)\n'}]}})
    assert LD.REQUIRES["sell_to_window"](sp3) and not LD.REQUIRES["sell_to_window"](sp)


def test_the_new_templates_are_established_templates_that_check():
    for name in ("Bench Act", "Recusal Act", "Graded Contract Enforcement", "Certified Contract Registry", "Bill Certification"):
        e = LB.ESTABLISHED[name]
        assert e["kind"] == "law" and "law.v2" in e["needs"] and e["doc"]
    assert LB.TOOLKIT["Contract Registry"]["code"].count("CLERK") == 0         # the toolkit's registry is unchanged
