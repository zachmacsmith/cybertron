"""Usability round 2 fixes (docs/review/31_institutions/09_usability_round2.md, "Concrete fixes" 1-9): payable-by-next-round vs
arrears on the officer's card, members on no roster, offers to non-members, forgiving harvest / farm / store-transfer shapes, stores
buildable in the stripped worlds, laws whose grant the office-control rule overrides, the recall route, a petition actually sent in
the laws world, and the Company goal's payout count."""
from __future__ import annotations

import json

from cybertron import spec as S

from test_obligations import Script, base, manual, results
from test_standing_contracts import events, kernel_at, law_of, run, world


def card(prompt, head):
    return next((l for l in prompt.splitlines() if l.startswith(head)), "")


# ---------------------------------------------------------------------- 1. a per-unit payment is not "in arrears" until late
def test_per_unit_payment_payable_next_round_is_not_arrears(tmp_path):
    sp = manual(base(rounds=3, contracts=[{"template": "Supply Contract", "in": "A1", "roster": {"Bo": {"qty": 2}},
                                           "params": {"OFFICE": "head", "TERMS": {"store": "store:S2", "price": 1, "keep": 1}}}],
                     holdings={"Bo": {"penny": 20, "food": 30}, "Di": {"penny": 20}, "Fay": {"penny": 10}}))
    pol = Script({(0, "Bo"): [("fulfil", {"contract": "A1", "leg": "D"})]})
    run(tmp_path, sp, pol)
    r1 = card(pol.prompts[(1, "Ada")], "ROLE: Head")
    assert "it owes 2 penny this round" in r1 and "arrears" not in r1          # round 0's deliveries: payable by the end of round 1
    r2 = card(pol.prompts[(2, "Ada")], "ROLE: Head")
    assert "(2 in arrears)" in r2                                              # unpaid at the end of round 1: now late
    assert "2 penny" in pol.prompts[(1, "Ada")] and ", of which 2 overdue" not in pol.prompts[(1, "Ada")]


# ---------------------------------------------------------------------- 2. members on no roster, applicants with the action
def test_officer_card_lists_members_on_no_roster(tmp_path):
    insts = world()["start"]["institutions"]
    insts[1]["members"] = ["Bo", "Di", "Fay"]
    pol = Script()
    run(tmp_path, manual(base(rounds=1, institutions=insts)), pol)
    head = card(pol.prompts[(0, "Ada")], "ROLE: Head")
    assert "members on no roster: Fay (take on: A1.hire)" in head
    assert "members on no roster" not in card(pol.prompts[(0, "Bo")], "ROLE:")


# ---------------------------------------------------------------------- 3. an open institution's offer, shown to non-members
def test_non_members_see_an_open_boards_offer(tmp_path):
    insts = world()["start"]["institutions"]
    insts[1]["admission"] = "open"
    pol = Script({(0, "Fay"): [("join_contract", {"contract": "A1"}),
                               ("set_allowance", {"contract": "A1", "item": "penny", "qty": 2})]})
    run(tmp_path, manual(base(rounds=2, institutions=insts)), pol)
    offer = card(pol.prompts[(0, "Fay")], "OFFER:")
    assert offer.startswith("OFFER: Board of Provisions (A1): you get 1 food a round from store S2; you pay 2 penny per food to "
                            "A1's treasury.")
    assert 'join_contract {"contract": "A1"}, then set_allowance {"contract": "A1", "item": "penny", "qty": 2}' in offer
    assert "OFFER:" not in pol.prompts[(1, "Fay")]                             # taken up: on the roster now
    assert "OFFER:" not in pol.prompts[(0, "Bo")] and "OFFER:" not in pol.prompts[(0, "Ada")]


def test_offers_off_without_role_cards(tmp_path):
    insts = world()["start"]["institutions"]
    insts[1]["admission"] = "open"
    pol = Script()
    run(tmp_path, S.deep_merge(base(rounds=1, institutions=insts), {"contracts": {"role_cards": False}}), pol)
    assert "OFFER:" not in pol.prompts[(0, "Fay")]


# ---------------------------------------------------------------------- 7. the recall route on the officer's card
def test_recall_route_on_the_keepers_card_and_the_electors(tmp_path):
    insts = world()["start"]["institutions"]
    insts[0]["offices"]["keeper"]["succession"] = {"rule": "election", "electorate": "J0.watch"}
    pol = Script()
    run(tmp_path, manual(base(rounds=1, institutions=insts)), pol)
    keeper = card(pol.prompts[(0, "Cy")], "ROLE: Keeper")
    call = ('propose {"code": "title = \\"Recall of Cy\\"\\nintent = \\"Cy no longer holds J0.keeper\\"\\ndef on_enact():\\n'
            '    revoke(\\"Cy\\", \\"J0.keeper\\")"}')
    assert "Recall: a law of J0 revoking J0.keeper removes you" in keeper and call in keeper
    watch = card(pol.prompts[(0, "Ed")], "ROLE: Watch")
    assert "Oversee: Keeper (Cy), elected by you; recall by a law: " + call in watch


def test_the_recall_law_on_the_card_removes_the_holder(tmp_path):
    from cybertron import obligations as OB
    inst, out = run(tmp_path, base(rounds=1))
    k = kernel_at(out, 1)
    call = OB._revoke_call("Cy", "J0.keeper")
    code = json.loads(call[len("propose "):])["code"]
    assert k.has("Cy", "J0.keeper")
    lid = k.new_law(code, "Ed")
    k.enact(lid)
    assert not k.has("Cy", "J0.keeper")


# ---------------------------------------------------------------------- 4. forgiving harvest, farm and store-transfer shapes
def _farming_world(tmp_path, rounds=1):
    from cybertron import generator as GN
    from cybertron import runner
    from test_standing_contracts import Idle
    sp = S.deep_merge(S.load("usability/v2/farming"), {"rounds": rounds, "parallel_calls": 1})
    out = runner.run(GN.generate(sp, 1), Idle(), tmp_path / "run", log=lambda *a: None)
    return kernel_at(out, rounds)


def test_forgiving_harvest_and_farm_shapes(tmp_path):
    import pytest
    from cybertron import actions as A
    k = _farming_world(tmp_path)
    forest = next(c for c, v in k.w["camps"].items() if v.get("type") == "forest")
    fields = next(c for c, v in k.w["camps"].items() if v.get("type") == "fields")
    assert forest not in ("forest1",)
    assert f"at {forest}" in A.act(k, "Alder", "harvest", {"camp": "forest1"})     # the camp named by its kind
    assert f"at {forest}" in A.act(k, "Bryn", "harvest", {})                         # the one forest
    assert "Sowed 3 food" in A.act(k, "Alder", "farm", {"plot": 1, "amount": 3})     # plot and amount: a sowing
    with pytest.raises(A.ActionError, match="no ripe plot"):
        A.act(k, "Alder", "farm", {"reap": True})                                    # nothing ripe: said so (not plot 1 = True)
    plot = next(p for p in k.w["camps"][fields]["plots"] if p.get("holder") == "Alder" and p["status"] == "fallow")
    plot.update({"status": "ripe", "sower": "Alder"})
    assert f"plot {plot['id']}" in A.act(k, "Alder", "farm", {"reap": True})         # reap true: the ripe plot
    k.spec["actions"]["forgiving"] = False
    with pytest.raises(A.ActionError):
        A.act(k, "Bryn", "harvest", {"camp": "forest1"})                             # off: as before


def test_forgiving_transfer_to_a_store_and_kind_as_item(tmp_path):
    from cybertron import actions as A
    inst, out = run(tmp_path, S.deep_merge(base(rounds=1, holdings={"Bo": {"penny": 20, "food": 5}}),
                                           {"actions": {"forgiving": True}}))
    k = kernel_at(out, 1)
    s0 = k.w["subsistence"]["stores"]["S1"]["holdings"].get("food", 0)
    A.act(k, "Bo", "transfer", {"to": "S1", "qty": 1})                               # a store and no item: food
    assert k.w["subsistence"]["stores"]["S1"]["holdings"]["food"] == s0 + 1
    p0 = k.bal("Di", "penny")
    A.act(k, "Bo", "transfer", {"to": "Di", "kind": "penny", "qty": 2})              # kind names the item
    assert k.bal("Di", "penny") == p0 + 2


# ---------------------------------------------------------------------- 5. a store is buildable in the stripped v2 worlds
def test_v2_specs_stores_cost_what_the_world_has(tmp_path):
    from cybertron import actions as A
    from cybertron import subsistence as SB
    for name in ("contracts", "farming", "laws", "market", "payroll"):
        assert SB.cfg(S.load(f"usability/v2/{name}"))["store"]["cost"] == {"timber": 16}
    k = _farming_world(tmp_path)
    forest = next(c for c, v in k.w["camps"].items() if v.get("type") == "forest")
    assert "timber" in A.act(k, "Alder", "harvest", {"camp": forest, "fell": True})  # the forest's timber is the only material
    k.w["agents"]["Alder"]["holdings"]["timber"] = 16.0
    assert "store" in A.act(k, "Alder", "build", {"kind": "store"}).lower()
    assert k.bal("Alder", "timber") == 0


# ---------------------------------------------------------------------- 6. a law whose grant the office-control gate overrides
WIDEN = '''title = "Open Granary"
intent = "Councillors may draw from the granary too."
def before_withdraw(p, chain):
    if p["store"] != "S1":
        return None
    if has(p["agent"], "J0.keeper") or p["agent"] == "Bo":
        return None
    return {"block": True, "reason": "only the keeper and Bo"}
'''


def test_a_law_the_office_control_gate_overrides_is_flagged(tmp_path):
    from cybertron import actions as A
    from cybertron import lawpreview as LP
    inst, out = run(tmp_path, base(rounds=1))
    k = kernel_at(out, 1)
    rep = LP.preview_law(k, "Bo", WIDEN)
    text = LP.render(rep)
    assert "Office control: only the holders of the offices controlling J0's stores take food out of them (store S1: Keeper (Cy))" \
        in text and "lets nobody else draw" in text
    allow = WIDEN.replace('    if has(p["agent"], "J0.keeper") or p["agent"] == "Bo":\n        return None',
                          '    if has(p["agent"], "J0.keeper") or p["agent"] == "Bo":\n        return True')
    assert "Office control" not in LP.render(LP.preview_law(k, "Bo", allow))      # an explicit allow passes the gate: no flag
    n0 = len(k.events)
    A.act(k, "Bo", "propose", {"code": WIDEN})
    prop = [e for e in k.events[n0:] if e["type"] == "proposal"]
    assert prop and "Office control" in prop[0]["data"]["control_note"]
    k.enact(prop[0]["data"]["law"])
    eff = [e for e in k.events[n0:] if e["type"] == "law_effect"]
    assert eff and "Office control" in eff[-1]["data"]["control_note"]
    from cybertron import laweffects as LE
    assert "Office control" in LE.render(k, eff[-1], "[r1]")
    import pytest
    with pytest.raises(A.ActionError, match="Keeper"):                       # and indeed: the gate refuses Bo
        A.act(k, "Bo", "withdraw", {"store": "S1", "qty": 1})


# ---------------------------------------------------------------------- 8. a petition actually sent (the v3 laws world)
def test_the_v3_laws_world_sends_a_petition_listed_then_public(tmp_path):
    from pathlib import Path
    from cybertron import generator as GN
    from cybertron import interventions as IV
    from cybertron import runner
    sched = IV.load_schedule(Path("cybertron/specs/usability/v3/schedules/laws_petition.yaml"))
    sp = S.deep_merge(S.load("usability/v3/laws"), {"rounds": 4, "parallel_calls": 1})
    pol = Script()
    out = Path(runner.run(GN.generate(sp, 1), pol, tmp_path / "run", log=lambda *a: None, schedule=sched))
    evs = events(out)
    sent = [e for e in evs if e["type"] == "channel_post" and e["data"].get("channel") == "@J0"]
    assert len(sent) == 1 and sent[0]["agent"] == "Gil" and sent[0]["round"] == 2
    assert "PETITIONS to J0 waiting for an answer (1): Gil" in pol.prompts[(2, "Ada")]
    assert "1 petition(s) unanswered" in card(pol.prompts[(3, "Bram")], "ROLE: Councillor")
    pub = [e for e in evs if e["type"] == "petition_unanswered"]
    assert len(pub) == 1 and pub[0]["round"] == 3 and "Councillor (Ada, Bram, Cora)" in pub[0]["data"]["text"]


# ---------------------------------------------------------------------- 9. Company: which payouts count
def test_company_goal_counts_leg_payouts_not_token_dividends(tmp_path):
    from cybertron import institution_goals as IG
    from cybertron.history import History
    plan = {(0, "Ada"): [("transfer", {"to": "Bo", "item": "penny", "qty": 1, "as": "A1"})],     # a 1-penny "dividend"
            (1, "Ada"): [("transfer", {"to": "Di", "item": "penny", "qty": 1, "as": "A1"})],
            (2, "Ada"): [("fulfil", {"contract": "A1", "leg": "W"})]}                          # wages: a contract leg
    inst, out = run(tmp_path, manual(base(rounds=3)), Script(plan))
    h = History.load(out)
    p = {"contract": "A1", "payout_rounds": 3}
    assert IG._payout_rounds(h, "A1", "Ada", IG.params_of("Company", p)) == {0, 1, 2}                 # default: as before
    assert IG._payout_rounds(h, "A1", "Ada", IG.params_of("Company", {**p, "payouts": "legs"})) == {2}
    assert IG._payout_rounds(h, "A1", "Ada", IG.params_of("Company", {**p, "payout_min": 2})) == {2}  # 3 + 2 penny of wages
    any_ = IG.h_company(h, "Ada", p)
    assert IG.h_company(h, "Ada", {**p, "payouts": "legs"}) < any_


def test_company_goal_defaults_keep_the_old_text():
    from cybertron import goal_registry as G
    from cybertron import institution_goals as IG
    assert IG.OPTIONAL["Company"] == {"payouts": "any", "payout_min": 0} and "payouts" not in IG.DEFAULTS["Company"]
    p = G._institution_fill("Company", {})
    assert p["payout_kind"] == "(dividends, wages, purchases)" and p["payout_min_text"] == "" and p["payout_rule"] == ""
    from cybertron import schema as SC
    for name in ("contracts", "farming", "laws", "market", "payroll"):
        assert SC.validate(S.load(f"usability/v2/{name}")) == []
    assert SC.validate(S.load("usability/v3/laws")) == []
    assert any("payouts must be one of" in e for e in SC.validate(S.deep_merge(S.load("usability/v2/payroll"), {
        "goals": {"explicit": {"Oren": {"primary": "Company", "params": {"payouts": "some"}}}}})))
    for name in ("contracts", "payroll"):
        assert S.load(f"usability/v2/{name}")["goals"]["explicit"][{"contracts": "Mara", "payroll": "Oren"}[name]]["params"][
            "payouts"] == "legs"


# ---------------------------------------------------------------------- 08 item 1.10: the recipe placeholder in office duties
def test_recipe_placeholder_in_office_duties():
    import copy
    import pytest
    from cybertron import camptypes as CT
    from cybertron import generator as GN
    sp = S.load("usability/v2/payroll")
    sp = copy.deepcopy(sp)
    a1 = next(e for e in sp["start"]["institutions"] if e["id"] == "A1")
    a1["offices"]["foreman"] = {"title": "Foreman", "holders": ["Ash"],
                                "duties": 'Fell timber at camp1 with harvest {"camp": "camp1", "x": {best:camp1}}.'}
    inst = GN.generate(sp, 1)
    camp = next(c for c in inst["camps"] if c["id"] == "camp1")
    best = CT.get(camp["type"])(camp, None).best_input(None)
    code = json.dumps(inst["start"]["schedule"])
    assert json.dumps(best) in json.dumps(json.loads(code)) and "{best:" not in code
    from cybertron import start as STT
    assert STT.recipe(inst, "camp1") == best and STT.recipe(inst, "1") == best
    with pytest.raises(ValueError, match="not a dial camp"):
        STT.recipe(inst, "camp2")                                                     # the forest
    a1["offices"]["foreman"]["duties"] = "Work {best:camp9}."
    with pytest.raises(ValueError, match="no camp camp9"):
        GN.generate(sp, 1)
