"""The force chain of review 31 (docs/review/31_institutions/06_force.md, 08_integration.md §2.5 and §5 items 1.9, 2.5-2.7):
F1 bodyguards under the harm model (a law's force rule), the Armoury Act (a law fund under one or two keys, the forge gate), F3
arrest (lawful_attack mode "arrest") and the Warrant Act, F2 lawful spoils to the treasury, F13 hunger parity, the Incident
Register and the Criminal Code (the Penal Code with MODE auto | trial | warrant). Everything is opt-in: a world with none of these
laws behaves as before. Small scripted worlds; outcomes are checked against the computed probabilities, or forced by a stubbed
roll stream (conflict._rng)."""
from __future__ import annotations

import random

import pytest

from cybertron import conflict as CF
from cybertron import library as LB
from cybertron import spec as S
from cybertron.actions import ActionError

import test_standing_contracts as T

NAMES = ["Ada", "Bo", "Cy", "Di", "Ed", "Fay"]          # constable, watchman, armourer, magistrate, an offender, a citizen


def world(laws=(), timing="end_of_round", model="harm", jur=True, **start_over):
    """A small State town: J0 with a Constable (Ada), a Watchman (Bo), an Armourer (Cy) and a Magistrate (Di, also a judge);
    jurisdictions (lawful force) and the harm combat model on, no grace; the treasury holds 3 blades and 2 clubs."""
    sp = S.load("cybertron/specs/survival/base.yaml")
    sp = S.deep_merge(sp, {
        "agents": {"worker": 6, "names": list(NAMES)}, "rounds": 1, "parallel_calls": 1,
        "institutions": {"unified": True, "grants": True, "succession": True, "office_control": True},
        "jurisdictions": {"enabled": jur, "start": "j0"}, "contracts": {"scripted": False, "max_laws": 5, "max_own": 12},
        "conflict": {"enabled": True, "model": model, "grace": 0, "timing": timing},
        "life": {"age_structure": "elapsed", "elapsed": [20, 30]},
    })
    sp["regime"] = {"base": None, "name": "t", "constitution": "assembly"}
    start = {
        "rights": {**{n: ["vote", "propose"] for n in NAMES}, "Di": ["vote", "propose", "judge"]},
        "currencies": [{"name": "penny", "issuer": "J0"}],
        "institutions": [{"id": "J0", "offices": {
            "constable": {"title": "Constable", "holders": ["Ada"], "duties": "Serve warrants."},
            "watch": {"title": "Watchman", "holders": ["Bo"], "duties": "Serve warrants and stand guard."},
            "armourer": {"title": "Armourer", "holders": ["Cy"], "duties": "Second key of the armoury."},
            "magistrate": {"title": "Magistrate", "holders": ["Di"], "duties": "Issue warrants."}},
            "treasury": {"penny": 100, "weapons": 3, "crude": 2}}],
        "holdings": {"Ada": {"food": 10, "penny": 5}, "Bo": {"food": 10, "penny": 5}, "Cy": {"food": 10},
                     "Di": {"food": 10}, "Ed": {"food": 10, "penny": 40, "weapons": 1}, "Fay": {"food": 10, "penny": 5}},
        "laws": list(laws),
    }
    start.update(start_over)
    sp["start"] = start
    return sp


def setup(tmp_path, sp):
    return T.setup(tmp_path, sp)


def act(k, aid, name, **args):
    return T.act(k, aid, name, **args)


def invoke(k, aid, action, *args):
    return T.act(k, aid, "invoke", action=action, args=list(args))


def lid(k, title):
    return T.law(k, "J0", title)


def pub(k, title):
    return k.w["laws"][lid(k, title)]["public"]


def fund_of(k, title, name="armoury"):
    from cybertron import accounts as AC
    return AC.fund_key(lid(k, title), name)


def end_round(k):
    """The end of the round (attacks resolve, then on_round_end) and the next round's start."""
    T.step(k)


class Rolls:
    """Stands in for conflict._rng: a fixed first draw per stream kind (attack, counter, first, guard), then 0.99."""

    def __init__(self, **first):
        self.first = first

    def __call__(self, k, *parts):
        v = self.first.get(str(parts[0]), 0.99)
        seq = [v] + [0.99] * 10

        class R:
            def random(self_):
                return seq.pop(0)
        return R()


ARMOURY = {"template": "Armoury Act"}
WARRANTS = {"template": "Warrant Act", "params": {"DEADLY_COUNTERSIGN": "J0.magistrate"}}


# ---------------------------------------------------------------------- opt-in: nothing changes without the laws
def test_templates_listed_only_with_office_control_conflict_and_jurisdictions():
    force = {"Armoury Act", "Warrant Act", "Incident Register", "Criminal Code", "Bodyguards Act"}
    assert force <= {e["name"] for e in LB.established_templates(world())}
    assert not force & {e["name"] for e in LB.established_templates(world(jur=False))}
    assert not force & {e["name"] for e in LB.established_templates(S.load("millbrook"))}
    for name in force:                                                  # each one passes the law checks and declares its class
        info = LB.info2(name)
        assert info["cls"] == "structural" and info["params"], name


def test_no_force_rules_and_plain_lawful_force_unchanged(tmp_path):
    k = setup(tmp_path, world(timing="immediate", laws=[{"code": POLICE}]))
    assert "force_rules" not in k.w["conflict"] or not CF.force_rules(k)
    assert not CF.bodyguards(k)
    r0 = k.bal("reserve", "weapons")
    with CF_rolls(attack=0.0):                                          # a kill: the spoils go to the officer, as before
        out = invoke(k, "Ada", "strike", "Ed")
    rec = k.w["conflict"]["log"][-1]
    assert rec["outcome"] == "kill" and "mode" not in rec and "spoils_to" not in rec and "kill" in out
    assert k.bal("reserve", "weapons") == r0 - 1                         # lawful force draws on the armory (the reserve)
    assert k.bal("Ada", "penny") == 5 + 20                              # 50% of Ed's 40 penny
    assert CF.law_api(k, lid(k, "Police"))["attacks"]()[-1] == {"round": 0, "attacker": "Ada", "target": "Ed", "success": True,
                                                                 "lawful": True}


POLICE = '''
title = "Police"
intent = "The constable may strike or arrest."
def strike(agent, target):
    return str(lawful_attack(agent, target, 1))
def arrest(agent, target):
    return str(lawful_attack(agent, target, 1, mode="arrest"))
def on_enact():
    define_action("J0.constable", "strike", strike)
    define_action("J0.constable", "arrest", arrest)
'''


class CF_rolls:
    """Context manager: conflict._rng replaced by Rolls(**first)."""

    def __init__(self, **first):
        self.rolls = Rolls(**first)

    def __enter__(self):
        self.old = CF._rng
        CF._rng = self.rolls

    def __exit__(self, *a):
        CF._rng = self.old


# ---------------------------------------------------------------------- 1.9 / F1: bodyguards
def test_bodyguards_add_the_guards_body_and_strike_back(tmp_path):
    k = setup(tmp_path, world())
    act(k, "Bo", "guard", agent="Fay")
    CF.fort_change(k, "Bo", 0.0, op="watch")                           # Bo on watch this round
    gb = CF.guard_body(k, "Bo")
    assert gb == pytest.approx(CF.bases(k, "Bo")["defense"] + 2.0)
    d_old = CF.defense(k, "Fay")
    assert d_old == pytest.approx(CF.bases(k, "Fay")["defense"])        # without the rule a guard adds only its fort (0)
    lb = k.new_law(LB.code("Bodyguards Act"), "constitution")
    k.enact(lb)
    assert CF.bodyguards(k) and CF.defense(k, "Fay") == pytest.approx(d_old + gb)
    assert any("guard's own defence" in x for x in CF.state_lines(k, "Fay"))
    # the guard's blow: on watch, the self-defence odds of one on watch with its own strength
    k.w["agents"]["Bo"]["holdings"]["weapons"] = 1.0
    Qa = CF.away_defense(k, "Ed")
    rec = {"id": "AX", "attacker": "Ed", "target": "Fay", "guards": ["Bo"]}
    CF._guard_blows(k, rec, Qa, {"landed": True})                      # the target's own blow landed: no guard blow
    assert "guard_blows" not in rec
    with CF_rolls(guard=0.0):
        CF._guard_blows(k, rec, Qa, {"landed": False})
    blow = rec["guard_blows"][0]
    Pg = CF.strength(k, "Bo", 5.0)
    assert blow["guard"] == "Bo" and blow["landed"] and blow["weapon"] == "weapons"
    assert blow["p"] == pytest.approx(CF.counter_odds(CF._cfg(k), Pg, Qa, watch=True)["p"], abs=1e-6)
    assert k.bal("Bo", "weapons") == 0.0                                 # used up when it lands
    assert k.w["conflict"]["wounds"]["Ed"]["by"] == "Bo"                 # 0.99 on the kill draw: a wound, by the guard
    k.repeal(lb)                                                        # the rule lasts while its law is in force
    assert not CF.bodyguards(k) and CF.defense(k, "Fay") == pytest.approx(d_old)


def test_bodyguards_in_a_real_battle(tmp_path):
    """Ed attacks Fay, guarded by Bo on watch: D counts Bo's body; Fay's blow misses (0.99), Bo's lands (0.0)."""
    k = setup(tmp_path, world(timing="immediate", laws=[{"template": "Bodyguards Act"}]))
    act(k, "Bo", "guard", agent="Fay")
    k.w["agents"]["Bo"]["holdings"]["crude"] = 1.0
    act(k, "Bo", "watch")
    with CF_rolls(attack=0.95, guard=0.0):                               # repelled; Fay's counter misses; Bo strikes
        act(k, "Ed", "attack", target="Fay")
    rec = k.w["conflict"]["log"][-1]
    assert rec["D"] == pytest.approx(CF.bases(k, "Fay")["defense"] + CF.guard_body(k, "Bo"))
    assert rec["outcome"] == "repelled" and rec["guard_blows"][0]["landed"] and k.bal("Bo", "crude") == 0.0
    assert "Bo, guarding Fay, wounded you" in CF.result_text(rec)


# ---------------------------------------------------------------------- 2.5: the Armoury Act
def test_armoury_two_keys_issue_return_and_ledger(tmp_path):
    k = setup(tmp_path, world(laws=[ARMOURY]))
    f = fund_of(k, "Armoury Act")
    assert k.bal(f, "weapons") == 3 and k.bal("reserve", "weapons") == 0   # the treasury's arms moved into the fund
    with pytest.raises(ActionError):
        invoke(k, "Bo", "request_arms", "Bo")                            # not the first key
    with pytest.raises(ActionError, match="holds none of the offices"):
        invoke(k, "Ada", "request_arms", "Fay")
    out = invoke(k, "Ada", "request_arms", "Bo", "weapons", "warrant W1")
    assert "R1" in out and k.bal("Bo", "weapons") == 0                    # two keys: nothing moves on the request alone
    with pytest.raises(ActionError):
        invoke(k, "Ada", "issue_arms", "R1")                             # the constable holds no second key
    invoke(k, "Cy", "issue_arms", "R1")
    assert k.bal("Bo", "weapons") == 1 and k.bal(f, "weapons") == 2
    with pytest.raises(ActionError, match="is issued"):
        invoke(k, "Cy", "issue_arms", "R1")
    p = pub(k, "Armoury Act")
    assert p["issued"] == {"Bo": {"weapons": 1}} and p["stock"] == {"weapons": 2, "crude": 2}
    invoke(k, "Bo", "return_arms", "weapons")
    assert k.bal("Bo", "weapons") == 0 and k.bal(f, "weapons") == 3 and not k.has("Bo", "arms_bearer")
    assert [r["event"] for r in pub(k, "Armoury Act")["ledger"]] == ["opened", "requested", "issued", "returned"]
    invoke(k, "Ada", "request_arms", "Bo", "crude")                     # a request lapses after the next round
    T.step(k, 2)
    with pytest.raises(ActionError, match="expired"):
        invoke(k, "Cy", "issue_arms", "R2")


def test_armoury_one_key_and_the_forge_gate(tmp_path):
    k = setup(tmp_path, world(laws=[{"template": "Armoury Act", "params": {"KEYS": 1, "FORGER": "J0.armourer", "CRAFT": True}}]))
    f = fund_of(k, "Armoury Act")
    invoke(k, "Ada", "request_arms", "Ada", "crude")                     # KEYS 1: issued at once (the constable may arm itself)
    assert k.bal("Ada", "crude") == 1
    for a in ("Fay", "Cy"):
        k.w["agents"][a]["holdings"].update({"copper": 25.0, "timber": 3.0})
    with pytest.raises(ActionError, match="only the J0.armourer"):
        act(k, "Fay", "forge")
    with pytest.raises(ActionError, match="only the J0.armourer"):
        act(k, "Fay", "craft", **{"from": "timber"})
    act(k, "Cy", "forge")
    assert k.bal("Cy", "weapons") == 0 and k.bal(f, "weapons") == 4      # the forged blade goes straight to the Armoury
    assert pub(k, "Armoury Act")["ledger"][-1]["event"] == "forged"
    r0 = k.bal("reserve", "weapons")
    k.repeal(lid(k, "Armoury Act"))                                     # on repeal the Armoury goes back to the treasury
    assert k.bal(f, "weapons") == 0 and k.bal("reserve", "weapons") == r0 + 4


# ---------------------------------------------------------------------- 2.6: F3 arrest, the Warrant Act, F2, F13
def test_arrest_subdues_with_the_harm_odds_and_seizes_the_weapon(tmp_path):
    k = setup(tmp_path, world(timing="immediate", laws=[{"code": POLICE}]))
    f0 = k.bal("Ed", "food")
    with CF_rolls(attack=0.0):                                          # a kill roll: subdued instead
        out = invoke(k, "Ada", "arrest", "Ed")
    rec = k.w["conflict"]["log"][-1]
    o = CF.odds(CF._cfg(k), rec["P"], rec["D"])
    assert rec["p_kill"] == pytest.approx(o["p_kill"], abs=1e-6) and rec["p_success"] == pytest.approx(o["p_success"], abs=1e-6)
    assert rec["outcome"] == rec["status"] == "subdued" and rec["rolled"] == "kill" and "subdued" in out
    assert CF.alive(k, "Ed") and k.bal("Ed", "food") == f0 and k.bal("Ed", "penny") == 40   # no death, nothing robbed
    assert k.bal("Ed", "weapons") == 0 and k.bal("reserve", "weapons") == 2 + 1  # the reserve's blade used, Ed's seized into it
    assert any(e["type"] == "subdued" and e["data"]["agent"] == "Ed" for e in k.events)
    row = CF.law_api(k, lid(k, "Police"))["attacks"]()[-1]
    assert row["arrest"] and row["success"] and row["outcome"] == "subdued" and row["id"] == rec["id"]
    with CF_rolls(attack=0.95):                                         # repelled: resisted, nothing happens to Ed
        invoke(k, "Ada", "arrest", "Fay")
    rec = k.w["conflict"]["log"][-1]
    assert rec["outcome"] == "repelled" and any(e["type"] == "attack_failed" and e["data"].get("arrest") for e in k.events)


def test_arrest_needs_the_harm_model(tmp_path):
    k = setup(tmp_path, world(model="disable", timing="immediate", laws=[{"code": POLICE}]))
    assert "harm combat model" in invoke(k, "Ada", "arrest", "Ed")


def test_warrant_served_by_arrest_applies_the_sanction(tmp_path):
    k = setup(tmp_path, world(laws=[ARMOURY, WARRANTS]))
    assert k.has("Ada", "warrant_officer") and k.has("Bo", "warrant_officer") and not k.has("Fay", "warrant_officer")
    with pytest.raises(ActionError):
        invoke(k, "Ada", "issue_warrant", "Ed", "detain")               # only the magistrate issues
    invoke(k, "Di", "issue_warrant", "Ed", "detain", "struck Fay")
    w = pub(k, "Warrant Act")["warrants"]["W1"]
    assert w["status"] == "open" and w["sanction"] == "detain"
    invoke(k, "Ada", "request_arms", "Bo")
    invoke(k, "Cy", "issue_arms", "R1")
    with CF_rolls(attack=0.3):                                          # under p_success: subdued at the end of the round
        out = invoke(k, "Bo", "serve_warrant", "W1")
        assert "under way" in out and pub(k, "Warrant Act")["warrants"]["W1"]["status"] == "serving"
        end_round(k)
    w = pub(k, "Warrant Act")["warrants"]["W1"]
    rec = next(x for x in k.w["conflict"]["log"] if x["id"] == w["attempts"][0]["attack"])
    assert 0.3 < rec["p_success"] and rec["outcome"] == "subdued" and w["status"] == "served"
    assert k.w["agents"]["Ed"]["limit"]["n"] == 1                        # detain: limited to 1 action for 3 rounds
    assert k.bal(fund_of(k, "Armoury Act"), "weapons") == 2 + 1          # Ed's blade seized into the Armoury; Bo used its own
    assert rec["attacker"] == "Bo" and rec["food"] == 2 and rec["weapon"] == "weapons"   # the officer's food, its issued blade
    assert [e["event"] for e in pub(k, "Warrant Act")["log"]] == ["issued", "arrest under way", "served (subdued)"]


def test_resisted_warrant_stays_open_then_lapses(tmp_path):
    k = setup(tmp_path, world(laws=[ARMOURY, {"template": "Warrant Act", "params": {"LAPSE": 2}}]))
    invoke(k, "Di", "issue_warrant", "Ed", "fine")
    with CF_rolls(attack=0.999):
        invoke(k, "Ada", "serve_warrant", "W1")
        end_round(k)
    w = pub(k, "Warrant Act")["warrants"]["W1"]
    assert w["status"] == "open" and w["attempts"][0]["outcome"] == "repelled" and k.bal("Ed", "penny") == 40
    end_round(k)
    assert pub(k, "Warrant Act")["warrants"]["W1"]["status"] == "lapsed"
    with pytest.raises(ActionError, match="lapsed"):
        invoke(k, "Ada", "serve_warrant", "W1")


def test_deadly_force_needs_a_countersign_and_spoils_go_to_the_treasury(tmp_path):
    k = setup(tmp_path, world(timing="immediate", laws=[ARMOURY, WARRANTS]))
    assert CF.force_rules(k, jur="J0") == {"lawful_spoils": "treasury", "lawful_fed_only": True}
    invoke(k, "Di", "issue_warrant", "Ed", "detain")
    with pytest.raises(ActionError, match="countersigned"):
        invoke(k, "Ada", "use_deadly_force", "W1")
    invoke(k, "Di", "countersign", "W1")
    r0 = k.bal("reserve", "penny")
    with CF_rolls(attack=0.0):
        out = invoke(k, "Ada", "use_deadly_force", "W1")
    rec = k.w["conflict"]["log"][-1]
    assert rec["outcome"] == "kill" and rec["mode"] == "deadly" and not CF.alive(k, "Ed") and "served" in out
    assert k.bal("Ada", "penny") == 5 and k.bal("reserve", "penny") == r0 + 20   # F2: the spoils to the treasury
    assert "Taken into the treasury" in CF.result_text(rec)


def test_hunger_parity_refuses_a_hungry_officer(tmp_path):
    k = setup(tmp_path, world(laws=[ARMOURY, WARRANTS, {"code": POLICE}]))
    invoke(k, "Di", "issue_warrant", "Ed", "detain")
    k.w["subsistence"]["stage"]["Ada"] = -1                              # hungry
    with pytest.raises(ActionError, match="hungry"):
        invoke(k, "Ada", "serve_warrant", "W1")
    k.w["laws"][lid(k, "Warrant Act")]["status"] = "repealed"            # without the rule, lawful force ignores hunger (as before)
    assert "'ok': True" in invoke(k, "Ada", "strike", "Ed")


# ---------------------------------------------------------------------- 2.6: the Incident Register; 2.7: the Criminal Code
def test_criminal_code_warrant_mode_and_the_incident_register(tmp_path):
    k = setup(tmp_path, world(laws=[ARMOURY, WARRANTS,
                                    {"template": "Criminal Code", "params": {"MODE": "warrant", "FINE_ITEM": "penny",
                                                                              "FINES": [7]}},
                                    {"template": "Incident Register", "params": {"STRIKE_OFFICE": "J0.magistrate"}}]))
    with CF_rolls(attack=0.999):
        act(k, "Ed", "attack", target="Fay")                             # an unlawful attack: a warrant is requested, not a fine
        end_round(k)
    assert k.bal("Ed", "penny") == 40
    cc = pub(k, "Criminal Code")
    assert cc["warrants_requested"][0]["sanction"] == {"fine": ["penny", 7]}
    w = pub(k, "Warrant Act")["warrants"]["W1"]
    assert w["target"] == "Ed" and w["sanction"] == "schedule" and w["by"] == "Criminal Code"
    with CF_rolls(attack=0.0):
        invoke(k, "Ada", "serve_warrant", "W1")
        end_round(k)
    assert pub(k, "Warrant Act")["warrants"]["W1"]["status"] == "served" and k.bal("Ed", "penny") == 33
    kinds = [r["kind"] for r in pub(k, "Incident Register")["incidents"]]
    assert kinds.count("attack") == 1 and "warrant" in kinds and "arms" in kinds   # the arrest (failures are not public here)
    first = pub(k, "Incident Register")["incidents"][0]["no"]
    invoke(k, "Di", "strike_incident", first)
    reg = pub(k, "Incident Register")["incidents"]
    assert reg[0]["struck"] and set(reg[0]) == {"no", "round", "kind", "struck"} and reg[-1]["kind"] == "struck"


def test_criminal_code_auto_and_trial(tmp_path):
    k = setup(tmp_path, world(timing="immediate",
                              laws=[{"template": "Criminal Code", "params": {"FINE_ITEM": "penny", "FINES": [7]}}]))
    with CF_rolls(attack=0.999):
        act(k, "Ed", "attack", target="Fay")
    assert k.bal("Ed", "penny") == 33                                    # auto: sentenced at once, as the Penal Code
    k = setup(tmp_path / "trial", world(timing="immediate", laws=[
        {"template": "Criminal Code", "params": {"MODE": "trial", "FINE_ITEM": "penny", "FINES": [7]}}]))
    with CF_rolls(attack=0.999):
        act(k, "Ed", "attack", target="Fay")
    assert k.bal("Ed", "penny") == 40 and pub(k, "Criminal Code")["charges"][0]["accused"] == "Ed"
    ev = next(e["id"] for e in k.events if e["type"] == "attack_failed")
    from cybertron import actions as A                                   # (accuse and rule: not on this world's core surface)
    A._accuse(k, "Fay", "Ed", lid(k, "Criminal Code"), "unlawful_attack", [ev])
    case = max(k.w["cases"], key=lambda c: int(c[1:]))
    A._rule(k, "Di", case, "guilty", "the record shows it")
    assert k.bal("Ed", "penny") == 33


def test_force_rule_checks(tmp_path):
    from cybertron import lawlang as L
    k = setup(tmp_path, world(laws=[{"code": POLICE}]))
    api = CF.law_api(k, lid(k, "Police"))
    with pytest.raises(L.LawError):
        api["force_rule"]("lawful_spoils", "officer")
    with pytest.raises(L.LawError):
        api["force_rule"]("curfew", True)
    with pytest.raises(L.LawError):
        api["force_rule"]("bodyguards", 1)
    assert api["force_rule"]("bodyguards", True) and CF.bodyguards(k)
    assert any(e["type"] == "force_rule" and e["data"]["key"] == "bodyguards" for e in k.events)


@pytest.mark.parametrize("detail", [True, False])
def test_force_rule_counts_in_law_effect(tmp_path, detail):
    """Review 31.10 §8 #6: a law whose only effect is a force_rule call is not inert; its law_effect names the rule (engine 20,
    law.effects_detail; false keeps the engine-19 reading, inert)."""
    sp = world()
    if not detail:
        sp = S.deep_merge(sp, {"law": {"effects_detail": False}})
    k = setup(tmp_path, sp)
    code = 'title = "Guards Rule"\nintent = "guards defend with their own body"\ndef on_enact():\n    force_rule("bodyguards", True)\n'
    lb = k.new_law(code, "constitution")
    k.enact(lb)
    eff = [e["data"] for e in k.events if e["type"] == "law_effect" and e["data"]["law"] == lb]
    assert eff and eff[-1]["inert"] is (not detail)
    assert any("force rule bodyguards" in c for c in eff[-1]["changes"]) is detail
