"""Manual obligations and the accountability layer (docs/review/31_institutions/00_framework.md §1-2; cybertron/obligations.py,
cybertron/standing.py leg modes): under contracts.legs_default manual nothing moves by itself; an obligation is met by fulfil or by
any matching transfer within the round; the state shows what is due with the exact action; a defaulter is reminded at the top of
its next turn and the counterparty told of the miss; the contract's terms escalate (grace, bond penalty); role cards; petitions;
forgiving arguments. Off by default: the flows stay automatic and fulfil is unknown."""
from __future__ import annotations

import json

from cybertron import spec as S

from test_standing_contracts import NAMES, events, kernel_at, law_of, run, world

DM_PHASE = "private messages have arrived before anyone's actions"


def manual(sp, **contracts):
    return S.deep_merge(sp, {"contracts": {"legs_default": "manual", "obligations": True, "role_cards": True, **contracts}})


def base(rounds=2, **start_over):
    """world() without J0's wages: A1 (Ada heads it) runs a Board (S2 -> Bo, Di at 2 penny a ration) and a Payroll (Bo 3, Di 2)."""
    return world(rounds=rounds, wages=[], **start_over)


class Script:
    """Scripted turns: {(round, agent): [(action, args), ...]}; every other turn passes. Records each agent's turn prompts."""

    def __init__(self, plan=None):
        self.plan = plan or {}
        self.prompts = {}

    def act(self, k, a, system, user, n_actions, final):
        acts = []
        if DM_PHASE not in user:
            self.prompts.setdefault((k.r, a["id"]), user)
            acts = [{"action": n, "args_json": json.dumps(x)} for n, x in self.plan.get((k.r, a["id"]), ())]
        return ({"reasoning": "", "actions": acts, "notes": "", "goal_guesses_json": "{}"}, "", {})


def law_moves(evs, lid):
    return [e for e in evs if e["type"] == "move" and e["data"].get("why") == f"law:{lid}"]


def results(run_dir, aid):
    """{round: [result text, ...]} of aid's actions (turns.jsonl)."""
    out = {}
    for line in (run_dir / "turns.jsonl").read_text().splitlines():
        t = json.loads(line)
        if t.get("agent") == aid:
            out.setdefault(t["round"], []).extend(str(r) for r in (t.get("results") or ()))
    return out


def test_defaults_off_flows_stay_automatic_and_fulfil_is_unknown(tmp_path):
    from cybertron import contracts as KC
    from cybertron import schema as SC
    assert KC.DEFAULTS["legs_default"] == "auto" and KC.DEFAULTS["obligations"] is False and KC.DEFAULTS["role_cards"] is False
    assert SC.EXTRA["actions.forgiving"] is False and SC.EXTRA["institutions.petition_public_after"] == 0
    pol = Script({(0, "Ada"): [("fulfil", {"contract": "A1"})]})
    inst, out = run(tmp_path, base(rounds=1), pol)
    k = kernel_at(out, 1)
    assert law_moves(events(out), law_of(k, "A1", "Board")["id"])          # the Board fed its subscribers by itself
    assert "OBLIGATIONS" not in pol.prompts[(0, "Ada")] and "ROLE:" not in pol.prompts[(0, "Ada")]
    assert any("unknown" in r.lower() or "not" in r.lower() for r in results(out, "Ada")[0])


def test_manual_legs_do_not_pay_unless_fulfilled(tmp_path):
    inst, out = run(tmp_path, manual(base(rounds=2)), Script())
    evs = events(out)
    k = kernel_at(out, 2)
    board, pay = law_of(k, "A1", "Board"), law_of(k, "A1", "Payroll")
    assert not law_moves(evs, board["id"]) and not law_moves(evs, pay["id"])
    assert k.w["agents"]["Bo"]["holdings"].get("penny") == 20                # no wage, no charge
    last = pay["state"]["last"]["Bo"]["W"]
    assert last["late"] == 6 and last["overdue"] == 6                         # two rounds of a 3-penny wage owed
    assert pay["state"]["book"]["Bo"]["W"][1] == 2                            # two misses on the record


def test_fulfil_by_action_and_by_matching_transfer(tmp_path):
    plan = {(0, "Ada"): [("fulfil", {"contract": "A1"})],                   # rations to Bo and Di, wages to Bo and Di
            (1, "Bo"): [("transfer", {"to": "A1", "item": "penny", "qty": 2})],   # Bo pays its ration with a plain transfer
            (1, "Di"): [("fulfil", {"contract": "A1", "leg": "P"})]}
    pol = Script(plan)
    inst, out = run(tmp_path, manual(base(rounds=2)), pol)
    k = kernel_at(out, 2)
    pay, board = law_of(k, "A1", "Payroll"), law_of(k, "A1", "Board")
    tagged = [e["data"] for e in events(out) if e["round"] == 0 and (e.get("data") or {}).get("fulfil")]
    assert {(d.get("to"), d["item"], d["qty"]) for d in tagged} >= {("Bo", "penny", 3.0), ("Di", "penny", 2.0), ("Bo", "food", 1.0),
                                                                    ("Di", "food", 1.0)}
    assert pay["state"]["book"]["Bo"]["W"][0] == 1                            # round 0's wage kept
    assert "Fulfilled" in " ".join(results(out, "Ada")[0])
    for who in ("Bo", "Di"):                                                  # the ration's price, paid in round 1 (a per leg may wait
        assert board["state"]["last"][who]["P"]["late"] == 0                  # to the end of the next round): nothing left late
        assert not board["state"].get("overdue", {}).get(who, {}).get("P")
    assert pol.prompts[(1, "Bo")].count("OWED TO YOU") <= 1


def test_due_lines_role_cards_and_reminder_at_the_top_of_the_next_turn(tmp_path):
    pol = Script()
    inst, out = run(tmp_path, manual(base(rounds=2)), pol)
    p0, p1 = pol.prompts[(0, "Ada")], pol.prompts[(1, "Ada")]
    assert 'OBLIGATIONS: nothing moves unless you act.' in p0 and 'fulfil {"contract": "A1", "leg": "W"}' in p0
    assert "ROLE: Head of Provisions (A1)." in p0 and "Decisions:" in p0 and "A1.set_wage" in p0
    assert "workers (Payroll) Bo, Di" in p0                                  # who answers to the head
    assert "ROLE: worker in Payroll (A1). You answer to the Head of A1 (Ada). You get: 3 penny a round" in pol.prompts[(0, "Bo")]
    assert "OWED TO YOU this round" in pol.prompts[(0, "Bo")]
    state = p1.split("## State", 1)[1].split("\n", 1)[1].split("\n")
    top = state[1:6]                                                          # right after the round line (and food)
    assert any(l.startswith("OBLIGATIONS:") and "Missed last round:" in l for l in top)
    evs = events(out)
    note = [e["data"]["text"] for e in evs if e["type"] == "notify" and e["round"] == 0]
    assert any("You missed Payroll (A1) leg W" in t and 'fulfil {"contract": "A1", "leg": "W"}' in t for t in note)   # the defaulter
    assert any(t.startswith("Provisions (A1) did not pay 3 penny to Bo") for t in note)                                # the counterparty
    assert "Obligations still due this round" in p0                          # the closing block repeats it


def test_escalation_by_the_contracts_terms_penalty_after_grace(tmp_path):
    """A supplier who holds the food and does not deliver: a would-not miss within GRACE, then a breach and the penalty from its
    bond, each step said to the defaulter."""
    sp = manual(base(rounds=3, contracts=[{"template": "Supply Contract", "in": "A1", "roster": {"Bo": {"qty": 2}},
                                           "params": {"OFFICE": "head", "TERMS": {"store": "store:S2", "price": 1, "keep": 1}},
                                           "escrow": {"Bo": {"penny": 5}}}],
                     holdings={"Bo": {"penny": 20, "food": 30}, "Di": {"penny": 20}, "Fay": {"penny": 10}}))
    inst, out = run(tmp_path, sp, Script())
    evs = events(out)
    note = {e["round"]: e["data"]["text"] for e in evs if e["type"] == "notify" and e["data"]["to"] == "Bo" and "Supply" in e["data"]["text"]}
    assert "You held it at your turn and did not act: a penalty of 2 penny from your bond after 1 more miss" in note[0]
    assert "That is a breach: penalty 2 penny from your bond" in note[1]
    assert [e for e in evs if e["type"] == "contract_breach" and e["round"] == 1]


def test_could_not_miss_is_not_a_breach(tmp_path):
    sp = manual(base(rounds=2, contracts=[{"template": "Supply Contract", "in": "A1", "roster": {"Bo": {"qty": 2}},
                                           "params": {"OFFICE": "head", "TERMS": {"store": "store:S2", "price": 1, "keep": 1}},
                                           "escrow": {"Bo": {"penny": 5}}}],
                     holdings={"Bo": {"penny": 20}, "Di": {"penny": 20}, "Fay": {"penny": 10}}))
    inst, out = run(tmp_path, S.deep_merge(sp, {"subsistence": {"start_food": [0, 0]}}), Script())
    evs = events(out)
    assert not [e for e in evs if e["type"] == "contract_breach"]
    assert any("a could-not miss" in e["data"]["text"] for e in evs if e["type"] == "notify" and e["data"]["to"] == "Bo")


def test_forgiving_arguments(tmp_path):
    plan = {(0, "Ada"): [("fulfil", {"institution": "@A1", "leg_id": "W", "qty": 99, "to": "Bo"}),   # aliases, ignored qty
                         ("transfer", {"to": "@A1", "item": "penny", "qty": 1, "note": "a gift"}),    # an inbox address
                         ("withdraw", {"item": "food", "qty": 1})],                                  # the one store Ada may draw
            (0, "Bo"): [("transfer", {"item": "penny"})]}                                             # missing arguments
    sp = S.deep_merge(manual(base(rounds=1, holdings={"Ada": {"penny": 5}, "Bo": {"penny": 20}, "Di": {"penny": 20}})),
                      {"actions": {"forgiving": True}})
    inst, out = run(tmp_path, sp, Script(plan))
    ada, bo = results(out, "Ada")[0], results(out, "Bo")[0]
    assert "Fulfilled: W 3 penny to Bo" in ada[0] and "Di" not in ada[0]
    assert "into A1's treasury" in ada[1]
    assert "error" not in ada[2].lower() and "food" in ada[2]
    assert any("transfer needs" in r and "to" in r for r in bo)


def test_petitions_listed_to_officers_then_public(tmp_path):
    plan = {(0, "Fay"): [("send", {"to": "A1", "text": "Please take me on as a worker."})]}
    sp = S.deep_merge(manual(base(rounds=3)), {"institutions": {"petition_public_after": 2}})
    pol = Script(plan)
    inst, out = run(tmp_path, sp, pol)
    assert "PETITIONS to A1 waiting for an answer (1): Fay" in pol.prompts[(1, "Ada")]
    assert "1 petition(s) unanswered" in pol.prompts[(1, "Ada")]
    pub = [e for e in events(out) if e["type"] == "petition_unanswered"]
    assert len(pub) == 1 and pub[0]["round"] == 1 and pub[0]["data"]["by"] == "Fay" and "Head (Ada)" in pub[0]["data"]["text"]


def test_answered_petition_leaves_the_list(tmp_path):
    plan = {(0, "Fay"): [("send", {"to": "A1", "text": "Please take me on as a worker."})],
            (1, "Ada"): [("send", {"to": "Fay", "text": "Not this season."})]}
    sp = S.deep_merge(manual(base(rounds=3)), {"institutions": {"petition_public_after": 2}})
    pol = Script(plan)
    inst, out = run(tmp_path, sp, pol)
    assert "PETITIONS" not in pol.prompts[(2, "Ada")]
    assert not [e for e in events(out) if e["type"] == "petition_unanswered"]


def test_scripted_bots_perform_or_neglect(tmp_path):
    from cybertron import obligations as OB
    from cybertron import start as STT
    inst, out = run(tmp_path, manual(base(rounds=1)), Script())
    k = kernel_at(out, 1)
    acts = OB.scripted_actions(k, k.w["agents"]["Ada"] | {"id": "Ada"})
    assert acts == [{"action": "fulfil", "args_json": json.dumps({"contract": "A1"})}]
    k.spec["contracts"]["bot_obligations"] = "neglect"
    assert OB.scripted_actions(k, {"id": "Ada"}) == []
    assert STT is not None and NAMES


def test_a_manual_duty_leg_is_recorded_and_its_miss_told(tmp_path):
    """A duty leg (done by acting: check act:<event type>) under manual mode: the miss is on the record, the defaulter and the counterparty
    are told, and a round in which the party acts keeps it."""
    sp = manual(base(rounds=2, contracts=[{"template": "Standing Contract", "founder": "Bo", "parties": {"Bo": "seller", "Di": "buyer"},
                                           "params": {"LEGS": [{"id": "G", "kind": "duty", "from": "seller", "to": "buyer",
                                                                "check": "act:post"}], "BOND": {}, "GRACE": 3}}]))
    pol = Script({(1, "Bo"): [("send", {"to": "square", "text": "On watch for Di this round."})]})
    inst, out = run(tmp_path, sp, pol)
    evs = events(out)
    note = [(e["round"], e["data"]["to"], e["data"]["text"]) for e in evs if e["type"] == "notify" and "leg G" in e["data"]["text"]]
    assert any(r == 0 and to == "Bo" and "You missed" in t and "act:post duty for Di" in t for r, to, t in note)
    assert any(r == 0 and to == "Di" and "Bo did not perform its act:post duty" in t for r, to, t in note)
    assert not any(r == 1 for r, _, _ in note)
    k = kernel_at(out, 2)
    law = next(l for l in k.w["laws"].values() if l["status"] == "active" and "G" in json.dumps((l.get("state") or {}).get("book", {})))
    assert [v["G"] for v in law["state"]["book"].values()] == [[1, 1]]                # kept once, missed once


# ---------------------------------------------------------------------- engine 19: misses judged at the payer's turn
def _supply(rounds, holdings, **contracts):
    sp = manual(base(rounds=rounds, contracts=[{"template": "Supply Contract", "in": "A1", "roster": {"Bo": {"qty": 2}},
                                                "params": {"OFFICE": "head", "TERMS": {"store": "store:S2", "price": 1, "keep": 1}},
                                                "escrow": {"Bo": {"penny": 5}}}],
                     holdings=holdings), **contracts)
    return S.deep_merge(sp, {"subsistence": {"start_food": [0, 0]}, "turns": "sequential"})


class GiveAfterBo:
    """Every agent whose turn comes after Bo's in round 0 gives Bo 5 food (simultaneous: everyone but Bo gives, decided before
    any action ran)."""

    def __init__(self, simultaneous=False):
        self.simultaneous, self.after_bo = simultaneous, False

    def act(self, k, a, system, user, n_actions, final):
        acts = []
        if a["id"] == "Bo":                                               # sequential: Bo decides, then its turn runs
            self.after_bo = True
        elif k.r == 0 and DM_PHASE not in user and (self.simultaneous or self.after_bo) \
                and k.w["agents"][a["id"]]["holdings"].get("food", 0) >= 5:
            acts = [{"action": "transfer", "args_json": json.dumps({"to": "Bo", "item": "food", "qty": 5})}]
        return ({"reasoning": "", "actions": acts, "notes": "", "goal_guesses_json": "{}"}, "", {})


FED = {"Bo": {"penny": 20}, "Di": {"penny": 20, "food": 20}, "Fay": {"penny": 10, "food": 20}, "Cy": {"food": 20},
       "Ed": {"food": 20}, "Ada": {"food": 20}}


def test_food_received_after_the_turn_is_a_could_not_miss(tmp_path):
    """Bo holds nothing at its turn; agents later in the round give it food. Under engine 18 (miss_judged round_end) the end-of-round
    holdings made that a would-not miss; now it is could-not, and the record says what Bo held at its turn and at the end."""
    inst, out = run(tmp_path / "turn", _supply(1, FED), GiveAfterBo())
    k = kernel_at(out, 1)
    rec = law_of(k, "A1", "Supply Contract")["state"]["last"]["Bo"]["D"]
    order = next(e["data"]["order"] for e in events(out) if e["type"] == "round_start")
    assert order[-1] != "Bo"                                                  # someone gave after Bo's turn
    assert rec["why"] == "could" and rec["held"] == 0 and rec["held_end"] >= 5 and rec["held_turn"] == order.index("Bo") + 1
    assert not [e for e in events(out) if e["type"] == "contract_breach"]
    notes = [e["data"]["text"] for e in events(out) if e["type"] == "notify" and e["data"]["to"] == "Bo" and "Supply" in e["data"]["text"]]
    assert any("You lacked it at your turn (a could-not miss)" in t for t in notes)
    # the old judgement, kept for runs of engine <= 18 (their frozen settings lack the key: settings.use sets it back)
    inst, out = run(tmp_path / "end", _supply(1, FED, miss_judged="round_end"), GiveAfterBo())
    rec = law_of(kernel_at(out, 1), "A1", "Supply Contract")["state"]["last"]["Bo"]["D"]
    assert rec["why"] == "would" and "held" not in rec


def test_simultaneous_turns_do_not_count_what_others_gave_after_the_decisions(tmp_path):
    sp = S.deep_merge(_supply(1, FED), {"turns": "simultaneous"})
    inst, out = run(tmp_path, sp, GiveAfterBo(simultaneous=True))
    rec = law_of(kernel_at(out, 1), "A1", "Supply Contract")["state"]["last"]["Bo"]["D"]
    assert rec["why"] == "could" and rec["held"] == 0 and rec["held_end"] >= 10


def test_held_at_the_end_of_its_turn_and_did_not_deliver_is_would_not(tmp_path):
    inst, out = run(tmp_path, _supply(1, {**FED, "Bo": {"penny": 20, "food": 30}}), Script())
    rec = law_of(kernel_at(out, 1), "A1", "Supply Contract")["state"]["last"]["Bo"]["D"]
    assert rec["why"] == "would" and rec["held"] == 30 and rec["misses"] == 1
    notes = [e["data"]["text"] for e in events(out) if e["type"] == "notify" and e["data"]["to"] == "Bo" and "Supply" in e["data"]["text"]]
    assert any("You held it at your turn and did not act" in t for t in notes)


def test_miss_judged_flip_is_engine_19():
    from cybertron import contracts as KC
    from cybertron import provenance as PV
    assert KC.DEFAULTS["miss_judged"] == "turn"
    assert ("cybertron.contracts.DEFAULTS", ("miss_judged",), "round_end", "turn") in PV.ENGINE_FLIPS[19]["flips"]
    from cybertron import settings as ST
    with ST.use({"engine_version": 18, "defaults": {}}):                # an engine-18 run replays with end-of-round judgement
        assert KC.DEFAULTS["miss_judged"] == "round_end"
    assert KC.DEFAULTS["miss_judged"] == "turn"
