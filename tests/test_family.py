"""37.1 family (cybertron/pairs.py raising mode family, life.age, life.labour): ages, the labour factor, the food each parent gives
a child, coming of age as loyal (Ally of a parent), own way or estranged (Foil), the frailty of an underfed minor, and the
prompt lines. No model calls."""
from __future__ import annotations

import pytest

from cybertron import goal_registry as GR
from cybertron import life as LF
from cybertron import pairs as PR
from cybertron import subsistence as SB

from test_subsistence_reproduction import adults, born_child, conceive, end_round, pair, set_food, world

FAMILY = ["life.reproduction.raising.mode=family", "life.reproduction.maturity=2"]


def family_child(extra=()):
    inst, k = world(extra=[*FAMILY, *extra])
    a, b = pair(k)
    conceive(k, a, b)
    ch = born_child(k)
    return inst, k, a, b, ch, next(x for x in inst["agents"] if x["id"] == ch)


def mature(k, ch, feed=None):
    """Play until ch comes of age; feed: {parent: qty} moved to the child each round (counted as that parent's food)."""
    for _ in range(4):
        if not PR.is_minor(k, ch):
            return next(e for e in k.events if e["type"] == "maturity" and e["agent"] == ch)["data"]
        for p, q in (feed or {}).items():
            set_food(k, p, 50)
            assert k.move(p, ch, "food", q, why="gift")
        end_round(k)
    raise AssertionError("never matured")


# ---------------------------------------------------------------------- ages and labour
def test_age_counts_from_entry():
    inst, k, a, b, ch, rec = family_child()
    st = LF.state(k)
    assert LF.age(k, a) == int(st["elapsed"][a]) + k.r
    assert LF.age(k, ch) == k.r - st["born"][ch]
    end_round(k)
    assert LF.age(k, ch) == k.r - st["born"][ch]


def test_labour_minor_adult_and_too_young():
    inst, k, a, b, ch, rec = family_child()
    assert LF.labour(k, a) == 1.0
    assert LF.labour(k, ch) == SB.cfg(k.spec)["minor_yield"]
    inst, k, a, b, ch, rec = family_child(["life.labour.minor=0.3"])
    assert LF.labour(k, ch) == 0.3
    inst, k, a, b, ch, rec = family_child(["life.labour.from_age=5"])
    assert LF.labour(k, ch) == 0.0 and SB.yield_mult(k, ch) == 0.0


def test_law_reads_age_and_labour():
    inst, k, a, b, ch, rec = family_child()
    api = LF.law_api(k, None)
    assert api["age"](ch) == LF.age(k, ch) and api["labour"](ch) == LF.labour(k, ch)


# ---------------------------------------------------------------------- what each parent gave
def test_the_ledger_counts_each_parents_food():
    inst, k, a, b, ch, rec = family_child()
    m = PR.state(k)["minors"][ch]
    start = dict(m["by"])
    assert set(start) == {a, b} and all(v > 0 for v in start.values())
    set_food(k, a, 50)
    assert k.move(a, ch, "food", 3.0, why="gift")
    end_round(k)
    assert m["by"][a] == pytest.approx(start[a] + 3.0) and m["by"][b] == pytest.approx(start[b])
    assert PR.family_target(k, m) == a


def test_no_child_gets_an_inherited_value_in_family_mode():
    inst, k, a, b, ch, rec = family_child()
    assert "provisional" not in rec["goal"]


# ---------------------------------------------------------------------- coming of age
@pytest.mark.parametrize("loyal,estranged,fed,way,goal", [
    ("[1.0, 1.0]", 0.0, True, "loyal", "parent"),
    ("[0.0, 0.0]", 1.0, False, "estranged", "Foil"),                 # neglect: nothing beyond the provisions
    ("[0.0, 0.0]", 0.0, True, "own", None),
])
def test_coming_of_age_ways(loyal, estranged, fed, way, goal):
    from cybertron import events as EV
    inst, k, a, b, ch, rec = family_child([f"life.reproduction.raising.loyal={loyal}",
                                           f"life.reproduction.raising.estranged={estranged}"])
    first = rec["goal"]["primary"]
    d = mature(k, ch, feed={b: 2.0} if fed else None)
    t = b if fed else a                                                # a tie goes to the parent whose offer was accepted
    assert d["way"] == way and d["target"] == t
    g = rec["goal"]
    bounds = [x for x in EV.state(k)["boundaries"] if x["agent"] == ch]
    if goal is None:
        assert g["primary"] == first and bounds == []
        return
    assert g["secondary"] == first and bounds and bounds[0]["why"] == "maturity"
    if goal == "Foil":
        assert g["primary"] == "Foil" and g["params"] == {"target": t, "slot": "primary", "family": True}
        assert GR.FAMILY_TEXTS["Foil"].format(target=t) in g["text"] and "secretly" not in g["text"].split(".")[0]
    else:                                                              # loyal: the parent's own goal, copied
        pg = next(x for x in inst["agents"] if x["id"] == t)["goal"]
        want = PR.parent_goal(k, t, ch)
        assert (g["primary"], g["params"]) == want
        if pg["primary"] != "Mirror" and ch not in {pg.get("params", {}).get("target"), pg.get("params", {}).get("partner")}:
            assert want == (pg["primary"], pg.get("params") or {})


def test_odds_follow_the_food_given():
    inst, k, a, b, ch, rec = family_child()
    m = PR.state(k)["minors"][ch]
    pl0, pe0 = PR.family_odds(k, m)
    assert (pl0, pe0) == pytest.approx((0.2, 0.3))                    # nothing beyond the provisions
    m["invested"] += 2 * 1.0 * 2                                       # maturity x ration beyond the provisions
    pl1, pe1 = PR.family_odds(k, m)
    assert (pl1, pe1) == pytest.approx((0.8, 0.0))


def test_parents_are_told_only_that_it_came_of_age_by_default():
    inst, k, a, b, ch, rec = family_child(["life.reproduction.raising.loyal=[1.0, 1.0]"])
    mature(k, ch)
    notes = [e["data"]["text"] for e in k.events if e["type"] == "notify" and e["data"]["to"] in (a, b) and " comes of age" in e["data"]["text"] and e["data"]["text"].startswith("Your child")]
    assert len(notes) == 2 and all(t.endswith("comes of age.") for t in notes)


def test_a_dead_parents_cause_falls_to_the_living_one():
    from cybertron import mortality as MO
    inst, k, a, b, ch, rec = family_child(["life.reproduction.raising.loyal=[1.0, 1.0]"])
    m = PR.state(k)["minors"][ch]
    m["by"][a] = 99.0
    MO.disable(k, a, "old_age")
    assert PR.family_target(k, m) == b


# ---------------------------------------------------------------------- frailty and prompts
def test_minor_frailty_raises_the_hazard_base():
    inst, k, a, b, ch, rec = family_child(["life.reproduction.raising.minor_frailty=1.0", "life.reproduction.maturity=6"])
    st = SB.state(k)
    st["missed"][ch] = 3                                               # the hazard's first round
    rec_ = {"deaths": []}
    SB._hazard(k, ch, SB.cfg(k.spec), rec_)
    assert rec_["deaths"] == [ch]


def test_prompt_lines_in_world_terms():
    inst, k, a, b, ch, rec = family_child(["life.reproduction.maturity=6"])
    pa = " ".join(PR.state_lines(k, a))
    pc = " ".join(PR.state_lines(k, ch))
    assert "take up your aims as its own" in pa and "score" not in pa
    assert "take up their cause" in pc
    assert "How a child is raised matters" in PR.rules_text(k.spec)


def test_inherit_mode_texts_are_unchanged():
    inst, k = world()
    assert "A goal both parents name" in PR.rules_text(k.spec) and "How a child is raised" not in PR.rules_text(k.spec)
    a, b = adults(k)[:2]
    assert not PR.family_on(k)


# ---------------------------------------------------------------------- children's work and turns
def test_a_minors_surplus_goes_to_its_parents():
    inst, k, a, b, ch, rec = family_child(["life.labour.surplus=household", "life.labour.keep=2", "life.reproduction.maturity=6"])
    set_food(k, a, 10)
    set_food(k, b, 10)
    set_food(k, ch, 9.0)                                               # eats 1, spoils a little, keeps 2, passes the rest on
    end_round(k)
    assert k.bal(ch, "food") == pytest.approx(2.0, abs=1e-6)
    moved = [e["data"] for e in k.events if e["type"] == "move" and e["data"].get("why") == "household"]
    assert sorted(d["dst"] for d in moved) == sorted([a, b]) and moved[0]["qty"] == pytest.approx(moved[1]["qty"]) and moved[0]["qty"] > 1.0


def test_surplus_off_by_default():
    inst, k, a, b, ch, rec = family_child(["life.reproduction.maturity=6"])
    set_food(k, ch, 9.0)
    end_round(k)
    assert not [e for e in k.events if e["type"] == "move" and e["data"].get("why") == "household"]


def test_minors_rest_between_turns():
    inst, k, a, b, ch, rec = family_child(["life.reproduction.raising.turn_every=3", "life.reproduction.maturity=9"])
    born = PR.state(k)["minors"][ch]["born"]
    seen = {}
    for _ in range(6):
        seen[k.r] = PR.rests(k, ch)
        end_round(k)
    assert seen == {r: (r - born) % 3 != 0 for r in seen} and not all(seen.values()) and any(seen.values())
    assert not PR.rests(k, a)
    assert "You act every 3 rounds" in " ".join(PR.state_lines(k, ch))


# ---------------------------------------------------------------------- households
from cybertron import households as HH  # noqa: E402

HOUSE = ["life.households.enabled=true", "contracts.enabled=true"]


def test_households_off_by_default():
    inst, k, a, b, ch, rec = family_child()
    assert not HH.on(k) and HH.household_of(k, ch) is None and LF.law_api(k, None)["households"]() == []


def test_a_first_birth_founds_a_household():
    inst, k, a, b, ch, rec = family_child([*HOUSE, "life.reproduction.maturity=6"])
    iid = HH.household_of(k, a)
    assert iid and HH.household_of(k, b) == iid and HH.household_of(k, ch) == iid and HH.head_of(k, iid) == a
    r = LF.law_api(k, None)["households"]()
    assert [x["id"] for x in r] == [iid] and {m["agent"] for m in r[0]["members"]} == {a, b, ch} and r[0]["head"] == a
    assert any(e["type"] == "household" and e["data"]["op"] == "founded" for e in k.events)
    assert f"Your household: {a}'s household ({iid})" in " ".join(LF.state_lines(k, ch))


def test_a_second_child_joins_the_same_household():
    inst, k, a, b, ch, rec = family_child([*HOUSE, "life.reproduction.maturity=6"])
    iid = HH.household_of(k, a)
    end_round(k)
    for x in (a, b):
        set_food(k, x, 30)
    conceive(k, a, b)
    ch2 = born_child(k, "G2")
    assert HH.household_of(k, ch2) == iid and len(HH.state(k)["ids"]) == 1


def test_the_pot_feeds_a_hungry_child():
    inst, k, a, b, ch, rec = family_child([*HOUSE, "life.reproduction.maturity=6", "life.labour.surplus=household"])
    iid = HH.household_of(k, a)
    pot = HH.pot_of(k, ch)
    assert pot == HH._rec(k, iid)["treasury"]
    set_food(k, ch, 9.0)
    end_round(k)
    assert k.bal(pot, "food") > 1.0                                    # the child's surplus went into the pot


def test_the_head_passes_to_the_coparent():
    from cybertron import mortality as MO
    inst, k, a, b, ch, rec = family_child([*HOUSE, "life.reproduction.maturity=6"])
    iid = HH.household_of(k, a)
    MO.disable(k, a, "old_age")
    assert HH.head_of(k, iid) == b
    MO.disable(k, b, "old_age")
    assert HH.head_of(k, iid) == ch


# ---------------------------------------------------------------------- inheritance
def _landed(extra, n_plots=4):
    """A family with two children (the second younger), the father holding n_plots plots of the first fields camp."""
    inst, k, a, b, ch, rec = family_child(["subsistence.fields.enabled=true", "life.reproduction.maturity=6", *extra])
    end_round(k)
    for x in (a, b):
        set_food(k, x, 30)
    conceive(k, a, b)
    ch2 = born_child(k, "G2")
    cid = SB.fields_camps(k)[0]
    plots = k.w["camps"][cid]["plots"][:n_plots]
    for p in plots:
        p["holder"] = a
    return k, a, b, ch, ch2, cid, [p["id"] for p in plots]


def _holders(k, cid, ids):
    return [p["holder"] for p in k.w["camps"][cid]["plots"] if p["id"] in ids]


@pytest.mark.parametrize("rule", ["partible", "eldest"])
def test_inheritance_of_plots(rule):
    from cybertron import mortality as MO
    k, a, b, ch, ch2, cid, ids = _landed([f"life.households.inheritance={rule}"])
    assert LF.age(k, ch) > LF.age(k, ch2)
    MO.disable(k, a, "old_age")
    hs = _holders(k, cid, ids)
    if rule == "partible":
        assert hs == [ch, ch2, ch, ch2]
    else:
        assert hs == [ch] * 4


def test_inheritance_to_the_household():
    from cybertron import mortality as MO
    k, a, b, ch, ch2, cid, ids = _landed([*HOUSE, "life.households.inheritance=household"])
    iid = HH.household_of(k, ch)
    MO.disable(k, a, "old_age")
    assert _holders(k, cid, ids) == [iid] * 4
    assert HH.roster(k)[0]["plots"] == [{"camp": cid, "plot": x} for x in ids]


def test_inheritance_none_is_as_before():
    from cybertron import mortality as MO
    k, a, b, ch, ch2, cid, ids = _landed([])
    MO.disable(k, a, "old_age")
    assert len(set(_holders(k, cid, ids))) == 1


def test_a_new_head_takes_the_dead_heads_stronger_model():
    from cybertron import mortality as MO
    inst, k, a, b, ch, rec = family_child([*HOUSE, "life.reproduction.maturity=6", "life.households.head_model=inherit"])
    ag = {x["id"]: x for x in inst["agents"]}
    ag[a]["model"], ag[b]["model"] = "claude-opus-5-5", "claude-haiku-5-5"
    MO.disable(k, a, "old_age")
    assert HH.head_of(k, HH.household_of(k, b)) == b and ag[b]["model"] == "claude-opus-5-5"
    inst, k, a, b, ch, rec = family_child([*HOUSE, "life.reproduction.maturity=6"])
    ag = {x["id"]: x for x in inst["agents"]}
    ag[a]["model"], ag[b]["model"] = "claude-opus-5-5", "claude-haiku-5-5"
    MO.disable(k, a, "old_age")
    assert ag[b]["model"] == "claude-haiku-5-5"                         # keep (default)


def test_start_households_are_set_by_hand():
    """start.households compiles to a round-0 entry; its handler founds the household (the runner applies the schedule)."""
    from cybertron import generator, spec as S
    from cybertron import start as ST
    from cybertron.kernel import Kernel
    sp = S.apply_overrides(S.load("nature_pairs"), ["rounds=5", "shared_archive.enabled=false",
                                                    "agents={worker: 4, scientist: 0, legislator: 0, media: 0, board: 0, fixer: 0, "
                                                    "names: [Ada, Bo, Cy, Di]}", *HOUSE,
                                                    "start={households: [{head: Ada, members: [Bo, Cy], name: House Ada}]}"])
    inst = generator.generate(sp, 1)
    k = Kernel(inst)
    e = next(x for x in inst["start"]["schedule"] if x["args"]["kind"] == "household")
    assert e["args"]["spec"] == {"head": "Ada", "members": ["Bo", "Cy"], "name": "House Ada"}
    iid = ST.h_household(k, inst, e["args"]["spec"])["household"]
    assert HH.household_of(k, "Bo") == iid and HH.head_of(k, iid) == "Ada" and HH._rec(k, iid)["name"] == "House Ada"
    assert HH.household_of(k, "Di") is None


def test_a_loyal_child_copies_the_parents_goal_or_falls_back_to_ally():
    inst, k, a, b, ch, rec = family_child()
    ag = {x["id"]: x for x in inst["agents"]}
    ag[b]["goal"]["primary"], ag[b]["goal"]["params"] = "Hoard", {"resource": "food"}
    assert PR.parent_goal(k, b, ch) == ("Hoard", {"resource": "food"})
    ag[b]["goal"]["primary"], ag[b]["goal"]["params"] = "Rival", {"target": ch}
    assert PR.parent_goal(k, b, ch) == ("Ally", {"target": b, "slot": "primary", "family": True})
    ag[b]["goal"]["primary"], ag[b]["goal"]["params"] = "Mirror", {"partner": a}
    assert PR.parent_goal(k, b, ch)[0] == "Ally"
