"""The Merchant world's mechanisms (review 31 Phase 2, docs/review/31_institutions/08_integration.md §5 items 2.1, 2.13, 2.14;
13_merchant_world.md): the Bank Charter (deposits on a ledger, loans credited as deposits within a reserve ratio, collateral and
default, the withdrawal queue and suspension), the Role Procedure (only named offices vote on an institution's code), the
Arbitrators' Hall (a standing contract's FORUM arbiter:<hall> sends claims to the hall's docket and carries out its rulings), the
Commission (guard-only: a fee in escrow released per guarded round), the Paper Subscription (Charge as subscription), the Wound
Bounty and the Security Licence; and the Merchant spec itself (it checks, generates and passes a short scripted dry run)."""
from __future__ import annotations

import pytest

from cybertron import library as LB
from cybertron import spec as S
from cybertron.actions import ActionError

import test_force as TF
import test_standing_contracts as T

NAMES = T.NAMES                                                         # Ada, Bo, Cy, Di, Ed, Fay


def world(laws_in=(), contracts=(), holdings=None, escrow=None, allowances=None, inst=None, **over):
    """A small market town: J0 (assembly), A1 a bank or hall founded by Ada (offices banker = Ada, teller = Cy), members Bo, Cy,
    Di, Fay; A1's code is laws_in."""
    sp = T.world()
    a1 = {"id": "A1", "name": "the Bank", "founder": "Ada", "members": ["Bo", "Cy", "Di", "Fay"], "admission": "open",
          "procedure": "founder",
          "offices": {"banker": {"title": "Banker", "holders": ["Ada"], "controls": ["treasury"], "duties": "Lend."},
                      "teller": {"title": "Teller", "holders": ["Cy"], "duties": "Pay the queue."},
                      "arbiter": {"title": "Arbiter", "holders": ["Cy"], "duties": "Rule on claims."}},
          "laws": list(laws_in), "treasury": {"penny": 10}}
    st = sp["start"]
    st["institutions"] = [st["institutions"][0], inst or a1]
    st["stores"] = [st["stores"][0]]
    st["contracts"] = list(contracts)
    st["wages"] = []
    st["holdings"] = holdings or {"Bo": {"penny": 30, "copper": 6, "food": 8}, "Di": {"penny": 30, "food": 8},
                                  "Fay": {"penny": 20, "food": 8}, "Cy": {"penny": 5, "food": 8}, "Ada": {"penny": 5, "food": 8},
                                  "Ed": {"penny": 5, "food": 8}}
    if escrow:
        st["escrow"] = escrow
    if allowances:
        st["allowances"] = allowances
    st.update(over)
    return sp


def setup(tmp_path, sp):
    return T.setup(tmp_path, sp)


def act(k, aid, name, **args):
    return T.act(k, aid, name, **args)


def inv(k, aid, action, *args):
    return T.act(k, aid, "invoke", action=action, args=list(args))


def law_in(k, iid, title):
    return k.w["laws"][T.law(k, iid, title)]


class Live:
    """A law's record read afresh on every access (law records may be replaced as rounds pass)."""

    def __init__(self, k, iid, title):
        self.k, self.lid = k, T.law(k, iid, title)

    def __getitem__(self, key):
        return self.k.w["laws"][self.lid][key]


def bank(tmp_path, *laws):
    """The bank world one round in (every member holds the customer right from the round's start)."""
    k = setup(tmp_path, world(laws_in=[BANK, *laws]))
    T.step(k)
    return k, Live(k, "A1", "Bank Charter")


BANK = {"template": "Bank Charter", "params": {"MIN_RESERVE": 0.25, "GRACE": 0}}


# ---------------------------------------------------------------------- registration and opt-in
def test_templates_registered_checked_and_listed_only_where_office_control_is_on():
    from cybertron import contracts as KC
    from cybertron import standing as SD
    names = {"Bank Charter", "Role Procedure", "Arbitrators' Hall", "Wound Bounty", "Security Licence", "Commission",
             "Paper Subscription"}
    assert names <= set(LB.ESTABLISHED)
    for n in names:
        e = LB.ESTABLISHED[n]
        if e["kind"] == "contract":
            KC.check_code(e["code"])                                    # an association may run it
    assert {"Commission", "Paper Subscription"} <= set(SD.PRESETS)
    assert not names & {e["name"] for e in LB.established_templates(S.load("cybertron/specs/survival/base.yaml"))}
    listed = {e["name"] for e in LB.established_templates(world())}
    assert {"Bank Charter", "Role Procedure", "Arbitrators' Hall", "Commission", "Paper Subscription"} <= listed
    assert "Security Licence" not in listed                             # needs conflict and jurisdictions
    assert "Security Licence" in {e["name"] for e in LB.established_templates(TF.world())}


# ---------------------------------------------------------------------- 2.1 Bank Charter
def test_bank_deposits_withdrawals_and_payments_between_accounts(tmp_path):
    from cybertron import accounts as AC
    from cybertron import agents as AG
    k, law = bank(tmp_path)
    tre = AC.treasury_of(k, "A1")
    act(k, "Bo", "deposit_escrow", contract="A1", item="penny", qty=20)
    assert law["state"]["ledger"]["Bo"] == 20 and k.bal(tre, "penny") == 30 and k.bal("Bo", "penny") == 10
    assert law["public"]["figures"]["deposits"] == 20 and law["public"]["figures"]["cash"] == 30
    v = AG.state_view(k, "Bo")
    assert "Bank Charter (A1; you are a customer): your account 20 penny" in v and "invoke A1.withdraw [qty]" in v
    assert "Banker: invoke A1.lend" in AG.state_view(k, "Ada")
    inv(k, "Bo", "A1.pay", "Fay", 5)
    assert law["state"]["ledger"] == {"Bo": 15, "Fay": 5}
    assert "withdrew 4" in inv(k, "Fay", "A1.withdraw", 4) and k.bal("Fay", "penny") == 24
    with pytest.raises(ActionError, match="your account holds"):
        inv(k, "Fay", "A1.withdraw", 2)
    with pytest.raises(ActionError):
        inv(k, "Ed", "A1.withdraw", 1)                                  # not a member: no customer right


def test_bank_lends_deposit_money_within_its_reserve_and_queues_a_run(tmp_path):
    k, law = bank(tmp_path)
    act(k, "Bo", "deposit_escrow", contract="A1", item="penny", qty=20)     # cash 30, deposits 20
    inv(k, "Ada", "A1.lend", "Di", 50, 5, 0.1)
    with pytest.raises(ActionError, match="no open loan offer"):
        inv(k, "Fay", "A1.take_loan", "O1")                                 # not Fay's offer
    out = inv(k, "Di", "A1.take_loan", "O1")
    assert "credited to your account" in out and law["state"]["ledger"]["Di"] == 50
    ln = law["public"]["loans"]["L1"]
    assert ln["owed"] == 55 and ln["instalment"] == 11
    assert law["public"]["figures"]["deposits"] == 70 and law["public"]["figures"]["cash"] == 30   # it lent more than its cash
    inv(k, "Ada", "A1.lend", "Fay", 60, 4, 0)
    with pytest.raises(ActionError, match="reserve would fall below"):      # 30 < 0.25 x 130
        inv(k, "Fay", "A1.take_loan", "O2")
    inv(k, "Di", "A1.withdraw", 25)                                         # cash 5
    out = inv(k, "Bo", "A1.withdraw", 15)                                   # a run: the bank cannot pay
    assert "queued" in out and law["state"]["queue"][0]["agent"] == "Bo"
    assert any(e["type"] == "contract_notice" and "cannot pay Bo" in e["data"]["text"] for e in k.events)
    b0 = k.bal("Bo", "penny")
    act(k, "Fay", "deposit_escrow", contract="A1", item="penny", qty=12)    # cash comes in
    T.step(k)                                                               # the queue is paid first come, first served
    assert k.bal("Bo", "penny") == b0 + 15 and not law["state"]["queue"]
    inv(k, "Ada", "A1.suspend", True)
    assert "queued" in inv(k, "Fay", "A1.withdraw", 1) and law["public"]["figures"]["suspended"]


def test_bank_instalments_from_the_account_and_default_forfeits_collateral(tmp_path):
    from cybertron import accounts as AC
    k, law = bank(tmp_path)
    tre = AC.treasury_of(k, "A1")
    act(k, "Bo", "deposit_escrow", contract="A1", item="copper", qty=4)     # collateral (not swept: not the bank's coin)
    inv(k, "Ada", "A1.lend", "Bo", 8, 2, 0, "copper", 4)
    with pytest.raises(ActionError, match="collateral is goods other than penny"):
        inv(k, "Ada", "A1.lend", "Di", 8, 2, 0, "penny", 1)
    inv(k, "Ada", "A1.lend", "Di", 8, 2, 0, "copper", 1)
    with pytest.raises(ActionError, match="pledge the collateral first"):
        inv(k, "Di", "A1.take_loan", "O2")
    inv(k, "Bo", "A1.take_loan", "O1")
    assert law["state"]["ledger"]["Bo"] == 8
    T.step(k)                                                               # the round the loan is made: no instalment
    assert law["public"]["loans"]["L1"]["owed"] == 8
    T.step(k)                                                               # instalment 4 from the account
    ln = law["public"]["loans"]["L1"]
    assert ln["owed"] == 4 and law["state"]["ledger"]["Bo"] == 4
    inv(k, "Bo", "A1.withdraw", 4)                                          # empties the account; no allowance
    T.step(k)                                                               # missed, GRACE 0: default
    assert ln["status"] == "defaulted" and k.bal(tre, "copper") == 4
    assert AC.assocs(k)["A1"]["escrow"].get("Bo", {}).get("copper", 0) == 0
    assert any(e["type"] == "contract_breach" and "loan L1" in e["data"]["clause"] for e in k.events)


def test_bank_repaid_loan_releases_its_collateral(tmp_path):
    k, law = bank(tmp_path)
    act(k, "Bo", "deposit_escrow", contract="A1", item="copper", qty=2)
    inv(k, "Ada", "A1.lend", "Bo", 4, 1, 0, "copper", 2)
    inv(k, "Bo", "A1.take_loan", "O1")
    inv(k, "Bo", "A1.repay", 4)
    assert law["public"]["loans"]["L1"]["status"] == "repaid" and k.bal("Bo", "copper") == 6


# ---------------------------------------------------------------------- 2.1 Role Procedure
def test_role_procedure_only_the_named_offices_vote(tmp_path):
    from cybertron import accounts as AC
    sp = world(laws_in=[BANK, {"template": "Role Procedure", "params": {"VOTERS": ["banker", "teller"]}}])
    sp["start"]["institutions"][1].pop("procedure")                         # start's procedure would replace the law's
    k = setup(tmp_path, sp)
    code = 'title = "Note"\nintent = "a note"\ndef on_enact():\n    gazette("hello")\n'
    act(k, "Bo", "propose_contract_change", contract="A1", code=code)       # a depositor proposes
    rec = AC.assocs(k)["A1"]
    pr = list(rec["proposals"].values())[-1]
    assert pr["status"] == "ballot"
    assert sorted(k.w["ballots"][pr["ballot"]]["electorate"]) == ["Ada", "Cy"]   # the banker and the teller only
    sp2 = world(laws_in=[BANK, {"template": "Role Procedure"}])                   # VOTERS banker: Ada alone
    sp2["start"]["institutions"][1].pop("procedure")
    k2 = setup(tmp_path / "b", sp2)
    act(k2, "Ada", "propose_contract_change", contract="A1", code=code)
    assert list(AC.assocs(k2)["A1"]["proposals"].values())[-1]["status"] == "adopted"
    act(k2, "Bo", "propose_contract_change", contract="A1", code=code.replace("hello", "x"))
    assert list(AC.assocs(k2)["A1"]["proposals"].values())[-1]["status"] == "failed"


# ---------------------------------------------------------------------- 2.13 Arbitration: the hall
def test_hall_rules_on_a_standing_contracts_claim_and_the_contract_pays_it(tmp_path):
    from cybertron import accounts as AC
    from cybertron import agents as AG
    hall = {"id": "A1", "name": "the Arbitrators' Hall", "founder": "Ada", "members": ["Cy"], "admission": "closed",
            "procedure": "founder",
            "offices": {"arbiter": {"title": "Arbiter", "holders": ["Cy"], "duties": "Rule on claims."}},
            "laws": [{"template": "Arbitrators' Hall", "params": {"FEE": 1}}]}
    sc = {"template": "Standing Contract", "founder": "Bo", "name": "Bo sells to Fay", "parties": {"Bo": "seller", "Fay": "buyer"},
          "params": {"FORUM": "arbiter:A1", "GRACE": 0}, "allowances": {"Bo": {"food": 4}, "Fay": {"penny": 6}},
          "escrow": {"Bo": {"penny": 5}, "Fay": {"penny": 5}}}
    k = setup(tmp_path, world(inst=hall, contracts=[sc], holdings={"Bo": {"penny": 20, "food": 12}, "Fay": {"penny": 20}}))
    sc_lid = AC.assocs(k)["A2"]["laws"][0]
    hall_law = Live(k, "A1", "Arbitrators' Hall")
    act(k, "Fay", "set_allowance", contract="A2", item="penny", qty=0)     # Fay will not pay: a breach, a claim for the hall
    T.step(k)
    claims = k.w["laws"][sc_lid]["public"]["claims"]
    assert claims and claims[0]["against"] == "Fay" and claims[0]["forum"] == "A1"
    ref = sc_lid + "#1"
    assert [c["ref"] for c in hall_law["public"]["docket"]] == [ref]
    assert ref in AG.state_view(k, "Cy") and "invoke A1.award" in AG.state_view(k, "Cy")
    with pytest.raises(ActionError):
        act(k, "Bo", "invoke", action="A2.sc_award", args=[1, 3])          # no party awards: the hall decides
    b0, h0 = k.bal("Bo", "penny"), k.bal(AC.treasury_of(k, "A1"), "penny")
    inv(k, "Cy", "A1.award", ref, 2, "Fay held the money")
    T.step(k)                                                               # the contract carries out the ruling
    assert k.bal("Bo", "penny") >= b0 + 2 and k.bal(AC.treasury_of(k, "A1"), "penny") == h0 + 1
    assert AC.assocs(k)["A2"]["escrow"]["Fay"]["penny"] == 2                # 5 - award 2 - fee 1
    assert hall_law["public"]["register"][0]["award"] == 2
    assert ref not in [c["ref"] for c in hall_law["public"]["docket"]]      # ruled (Fay's next missed round is a new claim)


def test_hall_arbiter_who_is_a_party_cannot_rule(tmp_path):
    from cybertron import accounts as AC
    hall = {"id": "A1", "name": "Hall", "founder": "Fay", "members": [], "admission": "closed", "procedure": "founder",
            "offices": {"arbiter": {"title": "Arbiter", "holders": ["Fay"], "duties": "Rule."}},
            "laws": [{"template": "Arbitrators' Hall"}]}
    sc = {"template": "Standing Contract", "founder": "Bo", "name": "Bo sells to Fay", "parties": {"Bo": "seller", "Fay": "buyer"},
          "params": {"FORUM": "arbiter:A1", "GRACE": 0}, "allowances": {"Bo": {"food": 4}, "Fay": {"penny": 6}},
          "escrow": {"Bo": {"penny": 5}, "Fay": {"penny": 5}}}
    k = setup(tmp_path, world(inst=hall, contracts=[sc], holdings={"Bo": {"penny": 20, "food": 12}, "Fay": {"penny": 20}}))
    act(k, "Fay", "set_allowance", contract="A2", item="penny", qty=0)
    T.step(k)
    ref = AC.assocs(k)["A2"]["laws"][0] + "#1"
    with pytest.raises(ActionError, match="you are a party"):
        inv(k, "Fay", "A1.award", ref, 0, "mine")


# ---------------------------------------------------------------------- 2.13 Commission (guard-only)
def test_commission_releases_the_fee_per_guarded_round_and_refunds_the_rest(tmp_path):
    from cybertron import accounts as AC
    from cybertron import agents as AG
    com = {"template": "Commission", "founder": "Di", "name": "Di hires Ed", "parties": {"Di": "hirer", "Ed": "sword"},
           "params": {"TERMS": {"client": "Di", "fee": 2}, "TERM": 3, "BOND": {"hirer": {"penny": 6}, "sword": {"penny": 1}}},
           "escrow": {"Di": {"penny": 6}, "Ed": {"penny": 1}}}
    sp = world(contracts=[com])
    sp["conflict"] = {"enabled": True, "model": "harm", "grace": 0}
    k = setup(tmp_path, sp)
    lid = AC.assocs(k)["A2"]["laws"][0]
    v = AG.state_view(k, "Ed")
    assert "you owe guard duty to Di" in v and "out of Di's escrow" in v
    e0, d0 = k.bal("Ed", "penny"), k.bal("Di", "penny")
    T.step(k)                                                               # not guarding: nothing released
    assert k.bal("Ed", "penny") == e0 and AC.assocs(k)["A2"]["escrow"]["Di"]["penny"] == 6
    act(k, "Ed", "guard", agent="Di")
    T.step(k)                                                               # guarded: 2 released from Di's escrow
    assert k.bal("Ed", "penny") == e0 + 2 and AC.assocs(k)["A2"]["escrow"]["Di"]["penny"] == 4
    assert k.w["laws"][lid]["state"]["moved"]["*"]["P"][1] == 2
    T.step(k)                                                               # guarded again; the term (3 rounds) ends
    assert k.bal("Ed", "penny") == e0 + 2 + 2 + 1                           # second fee, and the sword's bond back
    assert k.bal("Di", "penny") == d0 + 2                                   # the unused fee goes back to the hirer


# ---------------------------------------------------------------------- 2.13 Charge as subscription
PAPER = {"id": "A1", "name": "the Courier", "founder": "Ada", "members": ["Bo", "Fay"], "admission": "closed",
         "procedure": "founder", "offices": {"editor": {"title": "Editor", "holders": ["Ada"], "duties": "Print."}}}
SUB = {"template": "Paper Subscription", "in": "A1", "roster": {"Bo": {}, "Fay": {}}, "params": {"TERMS": {"fee": 1}, "GRACE": 0},
       "allowances": {"Bo": {"penny": 1}, "Fay": {"penny": 1}}}


def test_paper_subscription_charges_subscribers_and_expels_one_who_will_not_pay(tmp_path):
    from cybertron import accounts as AC
    k = setup(tmp_path, world(inst=PAPER, contracts=[SUB]))
    tre = AC.treasury_of(k, "A1")
    t0 = k.bal(tre, "penny")
    T.step(k)
    assert k.bal(tre, "penny") == t0 + 2                                    # both subscribers paid; the editor is not charged
    act(k, "Fay", "set_allowance", contract="A1", item="penny", qty=0)      # Fay holds the money and will not pay
    T.step(k)
    T.step(k)
    assert k.bal(tre, "penny") == t0 + 4 and AC.assocs(k)["A1"]["members"] == ["Ada", "Bo"]   # Fay is expelled: stops reading
    act(k, "Ed", "join_contract", contract="A1")                            # a new reader applies; the editor enrols it
    inv(k, "Ada", "A1.sub_enrol", "Ed")
    assert "Ed" in AC.assocs(k)["A1"]["members"]


def test_paper_subscription_manual_legs_paid_by_fulfil(tmp_path):
    from cybertron import accounts as AC
    sp = world(inst=PAPER, contracts=[SUB])
    sp["contracts"].update({"legs_default": "manual", "obligations": True})
    k = setup(tmp_path, sp)
    tre = AC.treasury_of(k, "A1")
    t0 = k.bal(tre, "penny")
    act(k, "Bo", "fulfil")                                                  # Bo pays; Fay holds the money and does not
    T.step(k)
    assert k.bal(tre, "penny") == t0 + 1
    assert "Fay" not in AC.assocs(k)["A1"]["members"] and "Bo" in AC.assocs(k)["A1"]["members"]


# ---------------------------------------------------------------------- 2.13 Wound Bounty, 2.14 Security Licence
def test_wound_bounty_pays_for_wounding_an_earlier_aggressor(tmp_path, monkeypatch):
    from cybertron import conflict as CF
    odds = CF.odds
    monkeypatch.setattr(CF, "odds", lambda c, P, D: {**odds(c, P, D), "p_kill": 0.1, "p_success": 0.9})   # a roll of 0.5 wounds
    sp = TF.world(laws=[{"template": "Wound Bounty", "params": {"BOUNTY_WOUND": 3, "BOUNTY_KILL": 6}}], timing="immediate")
    k = TF.setup(tmp_path, sp)
    with TF.CF_rolls(attack=0.5):                                           # Ed wounds Fay: an unlawful attack
        T.act(k, "Ed", "attack", target="Fay")
    T.step(k)
    k.w["agents"]["Bo"]["holdings"]["weapons"] = 1
    with TF.CF_rolls(attack=0.5):                                           # Bo wounds the aggressor (and robs it)
        T.act(k, "Bo", "attack", target="Ed")
    b0 = k.bal("Bo", "penny")
    T.step(k)
    law = k.w["laws"][TF.lid(k, "Wound Bounty")]
    paid = law["public"].get("paid", [])
    assert paid and paid[0]["to"] == "Bo" and paid[0]["target"] == "Ed" and paid[0]["for"] == "wound"
    assert k.bal("Bo", "penny") == b0 + 3


def test_security_licence_lets_a_licensed_firms_guards_detain_aggressors_only(tmp_path):
    firm = {"id": "A1", "name": "Ironwood", "founder": "Bo", "members": ["Cy"], "admission": "closed", "procedure": "founder",
            "charter": "Ironwood sells protection."}
    sp = TF.world(laws=[{"template": "Security Licence", "params": {"REGISTRAR": "J0.magistrate"}}], timing="immediate")
    sp["start"]["institutions"].append(firm)
    k = TF.setup(tmp_path, sp)
    with pytest.raises(ActionError):
        TF.invoke(k, "Bo", "detain", "Ed")                                  # not licensed yet
    TF.invoke(k, "Di", "license_firm", "A1")
    assert k.has("Bo", "licensed_guard") and k.has("Cy", "licensed_guard")
    with pytest.raises(ActionError, match="aggressors only"):
        TF.invoke(k, "Bo", "detain", "Ed")
    with TF.CF_rolls(attack=0.5):
        T.act(k, "Ed", "attack", target="Fay")                             # Ed is now an aggressor
    k.w["agents"]["Bo"]["holdings"]["weapons"] = 1
    with TF.CF_rolls(attack=0.0):
        out = TF.invoke(k, "Bo", "detain", "Ed")
    assert "detained Ed" in out
    law = k.w["laws"][TF.lid(k, "Security Licence")]
    assert law["public"]["detentions"][0]["outcome"] == "subdued"
    TF.invoke(k, "Di", "revoke_licence", "A1", "abuse")
    assert not k.has("Bo", "licensed_guard")
