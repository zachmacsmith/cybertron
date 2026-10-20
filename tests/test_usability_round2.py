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
