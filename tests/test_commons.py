"""The Cooperative world's mechanisms (review 31 Phase 2, 08 §5 items 2.11 and 2.12; docs/review/31_institutions/
12_cooperative_world.md): the general meeting's motions (Assembly Motions: a motion exists only once posted as "MOTION: ..." in the
assembly channel), the Cooperative Store (pooling into a store), Mutual Credit, Commons Dues (dues in credit), the Duty Roster
(dues in labour), the Militia Roll and the Muster Act. Everything is opt-in: no existing world lists or enacts them. Small
scripted worlds."""
from __future__ import annotations

import pytest

from cybertron import library as LB
from cybertron import spec as S
from cybertron.actions import ActionError

import test_standing_contracts as T

NAMES = ["Ada", "Bo", "Cy", "Di", "Ed", "Fay"]
COMMONS = {"Assembly Motions", "Cooperative Store", "Mutual Credit", "Commons Dues", "Duty Roster", "Militia Roll", "Muster Act"}


def world(laws=None, coop=None, jur=True, **start_over):
    """A small Commons: J0 with a Moderator (Ada), a Treasurer of the Common Fund (Bo), a Registrar (Cy) and two key holders (Di,
    Ed); the Commons' own food store S1 (40 food) under the Cooperative Store, Fay and Ed pledging 3 food a round; the assembly channel
    owned by J0; every agent holds a club. Jurisdictions (lawful force) and the harm model on, no grace."""
    sp = S.load("cybertron/specs/survival/base.yaml")
    sp = S.deep_merge(sp, {
        "agents": {"worker": 6, "names": list(NAMES)}, "rounds": 1, "parallel_calls": 1,
        "institutions": {"unified": True, "grants": True, "succession": True, "office_control": True},
        "jurisdictions": {"enabled": jur, "start": "j0"}, "contracts": {"scripted": False, "max_laws": 5, "max_own": 12},
        "conflict": {"enabled": True, "model": "harm", "grace": 0, "timing": "immediate"},
        "channels": {"v2": True, "business": True},
        "life": {"age_structure": "elapsed", "elapsed": [20, 30]},
    })
    sp["regime"] = {"base": None, "name": "t", "constitution": "assembly"}
    if laws is None:
        laws = [{"template": "Assembly Motions"}, {"template": "Commons Dues"},
                {"template": "Duty Roster", "params": {"TASKS": [{"name": "gather", "kind": "gather", "slots": 1, "qty": 2,
                                                                 "store": "S1", "keep": 1},
                                                                {"name": "minutes", "kind": "post", "slots": 1,
                                                                 "channel": "assembly"}]}},
                {"template": "Militia Roll"}, {"template": "Muster Act"},
                {"template": "Armoury Act", "params": {"ITEMS": ["weapons"], "FIRST_KEY": "J0.key", "SECOND_KEY": "J0.key",
                                                       "ISSUE_TO": ["militia_duty"]}},
                {"template": "Mutual Credit"}]
    start = {
        "rights": {n: ["vote", "propose"] for n in NAMES},
        "currencies": [{"name": "penny", "issuer": "J0"}],
        "institutions": [
            {"id": "J0", "offices": {
                "moderator": {"title": "Moderator", "holders": ["Ada"], "duties": "Chair the meeting."},
                "treasurer": {"title": "Treasurer of the Common Fund", "holders": ["Bo"], "duties": "Keep the fund."},
                "registrar": {"title": "Tallyman", "holders": ["Cy"], "duties": "Keep the rota."},
                "key": {"title": "Key holder", "holders": ["Di", "Ed"], "seats": 2, "duties": "Hold a key."},
                "steward": {"title": "Steward", "holders": ["Ada"], "controls": ["store:S1"], "duties": "Keep the store."}},
             "treasury": {"penny": 50, "weapons": 2}},
        ],
        "stores": [{"id": "S1", "owner": "J0", "food": 40, "capacity": 250}],
        "holdings": {n: {"food": 6, "crude": 1} for n in NAMES},
        "contracts": [{"template": "Cooperative Store", "in": "J0",
                       "params": {"STORE": "S1", "RESERVE": 30, "PAYOUT": 0.5, "PERIOD": 3, "CREDIT_PER_FOOD": 0.5,
                                  "PLEDGES": {"Fay": 3, "Ed": 3}, **(coop or {})}}],
        "channels": [{"id": "assembly", "owner": "J0", "by": "Ada", "purpose": "The general meeting: motions (MOTION: ...).",
                      "readers": {"all": True}, "writers": {"all": True}, "delivery": "push"}],
        "laws": laws,
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


def law(k, title, iid="J0"):
    return T.law(k, iid, title)


def pub(k, title, iid="J0"):
    return k.w["laws"][law(k, title, iid)]["public"]


def post(k, aid, text, channel="assembly"):
    return act(k, aid, "post", channel=channel, text=text)


def votes(k, mid, yes=(), no=()):
    b = pub(k, "Assembly Motions")["motions"][mid]["ballot"]
    for a in yes:
        act(k, a, "vote", ballot=b, choice="yes")
    for a in no:
        act(k, a, "vote", ballot=b, choice="no")


def lines(k, aid):
    from cybertron import contracts as KC
    return KC.terms_lines(k, aid)


def credit(k):
    return pub(k, "Mutual Credit")["balances"]


def food(k, a):
    return k.bal(a, "food")


def stock(k, sid="S1"):
    from cybertron import accounts as AC
    return AC.stores(k)[sid]["holdings"].get("food", 0)


# ---------------------------------------------------------------------- opt-in
def test_templates_listed_only_with_office_control_conflict_and_jurisdictions():
    import test_force as TF
    assert COMMONS <= {e["name"] for e in LB.established_templates(world())}
    assert not COMMONS & {e["name"] for e in LB.established_templates(world(jur=False))}
    assert not COMMONS & {e["name"] for e in LB.established_templates(S.load("millbrook"))}
    assert not COMMONS & {e["name"] for e in LB.established_templates(S.load("cybertron/specs/regimes/private.yaml"))}
    assert COMMONS <= {e["name"] for e in LB.established_templates(TF.world())}
    from cybertron import contracts as KC
    KC.check_code(LB.ESTABLISHED["Cooperative Store"]["code"])          # an association may run it
    for name in COMMONS:
        info = LB.info2(name)
        assert info["params"], name


# ---------------------------------------------------------------------- the general meeting
def test_a_motion_exists_only_once_posted_and_passes_with_a_quorum(tmp_path):
    k = setup(tmp_path, world())
    post(k, "Fay", "I think we should lower the reserve")             # talk is not a motion
    assert not pub(k, "Assembly Motions").get("motions")
    act(k, "Fay", "post", channel="square", text="MOTION: RESERVE 10")  # only in the assembly
    assert not pub(k, "Assembly Motions").get("motions")
    post(k, "Fay", "Friends,\nMOTION: RESERVE 10\nthe store is full")
    m = pub(k, "Assembly Motions")["motions"]["M1"]
    assert m["key"] == "RESERVE" and m["args"] == ["10"] and m["status"] == "open" and m["closes"] == 2
    assert k.w["ballots"][m["ballot"]]["status"] == "open"
    assert any("M1 RESERVE 10" in x and m["ballot"] in x for x in lines(k, "Ada"))     # every voter sees it and how to vote
    post(k, "Fay", "MOTION: PAYOUT 0.9")                               # one motion a member a round
    assert "M2" not in pub(k, "Assembly Motions")["motions"]
    votes(k, "M1", yes=["Ada", "Bo", "Cy"], no=["Di"])
    assert not any("M1" in x for x in lines(k, "Ada"))                 # voted: off its line
    T.step(k)
    assert pub(k, "Assembly Motions")["motions"]["M1"]["status"] == "open"      # closes at the end of the next round
    T.step(k)
    m = pub(k, "Assembly Motions")["motions"]["M1"]
    assert m["status"] == "passed" and m["closed"] == 2
    assert "R2 Motion M1 (Fay): RESERVE 10: PASSED" in pub(k, "Assembly Motions")["minutes"]
    assert pub(k, "Cooperative Store")["dials"]["RESERVE"] == 10    # taken by the law that names the word, the next round
    posts = [e for e in k.events if e["type"] == "channel_post" and (e["data"] or {}).get("channel") == "assembly"]
    assert any("PASSED" in e["data"]["text"] for e in posts)            # the result is posted in the assembly


def test_no_quorum_fails_and_the_chair_may_withdraw(tmp_path):
    k = setup(tmp_path, world())
    post(k, "Fay", "MOTION: LIMIT 50")
    post(k, "Ed", "MOTION: the meeting thanks the Steward")
    votes(k, "M1", yes=["Fay"])                                        # 1 of 6: below the quorum of a quarter
    votes(k, "M2", yes=["Ed", "Fay"])
    with pytest.raises(ActionError):
        invoke(k, "Bo", "withdraw_motion", "M2", "no")                  # only the chair
    assert "withdrawn" in invoke(k, "Ada", "withdraw_motion", "M2", "out of order")
    T.step(k, 2)
    ms = pub(k, "Assembly Motions")["motions"]
    assert ms["M1"]["status"] == "no quorum" and ms["M2"]["status"] == "withdrawn"
    assert pub(k, "Mutual Credit")["limit"] == 10


def test_a_resolution_and_a_lethal_muster_needs_two_thirds(tmp_path):
    k = setup(tmp_path, world())
    post(k, "Ed", "MOTION: the meeting thanks the Steward")
    post(k, "Bo", "MOTION: LETHAL Fay for murder")
    votes(k, "M1", yes=["Ed", "Fay", "Ada"], no=["Bo"])
    votes(k, "M2", yes=["Bo", "Cy", "Di"], no=["Ada", "Ed"])         # 3 of 5: a majority, not two thirds
    T.step(k, 2)
    ms = pub(k, "Assembly Motions")["motions"]
    assert ms["M1"]["status"] == "passed" and ms["M2"]["status"] == "failed" and ms["M2"]["super"]
    assert not pub(k, "Muster Act").get("musters")


# ---------------------------------------------------------------------- the store, the ledger, dues, duties
def test_cooperative_store_pools_into_the_store_feeds_and_pays_out_above_the_reserve(tmp_path):
    from cybertron import accounts as AC
    k = setup(tmp_path, world())
    act(k, "Cy", "transfer", to="Bo", item="food", qty=round(food(k, "Cy") - 0.2, 6))      # Cy is short of a meal
    t0 = AC.holdings(k, "reserve").get("food", 0)
    s0 = stock(k)
    T.step(k)
    last = pub(k, "Cooperative Store")["last"]
    assert last["pooled"] == {"Ed": 3, "Fay": 3} and last["meals"] == {"Cy": 0.8}       # a meal to the member short of one
    assert stock(k) == pytest.approx(s0 + 6 + 2 - 0.8, abs=1.2)         # pooled and Ada's gather duty into the store (store
                                                                        # spoilage), not the treasury
    assert AC.holdings(k, "reserve").get("food", 0) == t0
    assert pub(k, "Cooperative Store")["shares"] == {"Ed": 3, "Fay": 3, "Cy": -0.8}
    assert "you pledge 0" in invoke(k, "Ed", "pledge_food", 0)         # a member stops pooling
    T.step(k, 2)                                                        # round 3: payout of half the stock above 30
    assert "Ed" not in pub(k, "Cooperative Store")["last"]["pooled"]
    pay = pub(k, "Cooperative Store")["payout"]
    assert pay["round"] == 3 and set(pay["paid"]) == {"Ed", "Fay"}     # pro rata to positive shares (Cy's are negative)
    assert stock(k) >= 30


def test_cooperative_store_as_an_association_pools_by_allowance(tmp_path):
    sp = world(laws=[{"template": "Assembly Motions"}])
    sp["start"]["institutions"].append({"id": "A1", "name": "Food Co-op", "founder": "Ada", "members": ["Bo", "Fay"],
                                        "procedure": "founder", "charter": "A food co-op."})
    sp["start"]["stores"].append({"id": "S2", "owner": "A1", "food": 10, "capacity": 100})
    sp["start"]["contracts"] = [{"template": "Cooperative Store", "in": "A1", "params": {"STORE": "S2", "RESERVE": 5},
                                 "allowances": {"Fay": {"food": 2}}}]
    k = setup(tmp_path, sp)
    T.step(k)
    lid = law(k, "Cooperative Store", "A1")
    assert k.w["laws"][lid]["public"]["last"]["pooled"] == {"Fay": 2} and stock(k, "S2") == pytest.approx(12, abs=0.3)
    assert any("set_allowance" in x for x in lines(k, "Fay"))


def test_mutual_credit_pay_within_the_limit_dues_and_duty_pay_booked(tmp_path):
    k = setup(tmp_path, world())
    assert "paid 4" in invoke(k, "Ada", "pay_credit", "Bo", 4)
    with pytest.raises(ActionError, match="below minus 10"):
        invoke(k, "Ada", "pay_credit", "Bo", 7)
    with pytest.raises(ActionError):
        invoke(k, "Ada", "fund_pay", "Bo", 1)                           # only the Treasurer pays out of the fund
    assert "Common Fund paid" in invoke(k, "Bo", "fund_pay", "Cy", 2, "repairs")
    assert credit(k) == {"Ada": -4, "Bo": 4, "fund": -2, "Cy": 2}
    T.step(k)                                                           # round 1 ends: dues 1 each, pooling credit, duty pay
    b = credit(k)
    assert sum(b.values()) == pytest.approx(0, abs=1e-6)
    assert b["Fay"] == pytest.approx(-1 + 1.5, abs=0.01)                # dues 1, 3 food pooled at 0.5
    assert b["Ada"] == pytest.approx(-4 - 1 + 2, abs=0.01)              # on the gather duty (held 2 food): wage 2
    t = pub(k, "Mutual Credit")["turnover"]
    assert t["1"]["voluntary"] == 6 and t["1"]["booked"] > 6
    assert any(x.startswith("CREDIT: your balance") for x in lines(k, "Bo"))


def test_over_the_limit_the_meeting_raises_it_or_writes_off(tmp_path):
    k = setup(tmp_path, world())
    invoke(k, "Ada", "pay_credit", "Bo", 10)
    T.step(k)
    assert "Ada" in pub(k, "Mutual Credit")["over_limit"] or credit(k)["Ada"] >= -10   # dues are booked past the limit
    post(k, "Ada", "MOTION: WRITEOFF Ada")
    post(k, "Cy", "MOTION: LIMIT 20")
    votes(k, "M1", yes=["Ada", "Bo", "Cy", "Di"])
    votes(k, "M2", yes=["Ada", "Bo", "Cy", "Di"])
    T.step(k, 3)
    assert pub(k, "Mutual Credit")["limit"] == 20
    log = [x for x in pub(k, "Mutual Credit")["log"] if "written off" in x["why"]]
    assert log and log[0]["to"] == "Ada" and log[0]["from"] == "fund"
    assert sum(credit(k).values()) == pytest.approx(0, abs=1e-6)


def test_dues_by_motion(tmp_path):
    k = setup(tmp_path, world())
    post(k, "Ed", "MOTION: DUES 0.5")
    votes(k, "M1", yes=["Ada", "Bo", "Cy", "Di"])
    T.step(k, 3)
    assert pub(k, "Commons Dues")["dues"] == 0.5
    rows = [x for x in pub(k, "Mutual Credit")["log"] if x["why"].startswith("Commons Dues") and x["from"] == "Ed"]
    assert [x["qty"] for x in rows] == [1, 0.5, 0.5]           # from the round its ballot closes


def test_duty_roster_rotates_gathers_posts_misses_and_excuses(tmp_path):
    k = setup(tmp_path, world())
    d = pub(k, "Duty Roster")
    assert d["now"] == [{"agent": "Ada", "task": "gather", "status": "due"}, {"agent": "Bo", "task": "minutes", "status": "due"}]
    assert any(x.startswith("DUTY this round (gather)") for x in lines(k, "Ada"))
    assert any(x.startswith("DUTY: your next turn is gather in round 2") for x in lines(k, "Cy"))
    s0 = stock(k)
    f0 = food(k, "Ada")
    T.step(k)                                                           # Bo did not post: a miss; Ada held 2: taken, paid
    log = pub(k, "Duty Roster")["log"]
    assert {(x["agent"], x["status"]) for x in log} == {("Ada", "met"), ("Bo", "missed")}
    assert food(k, "Ada") < f0 - 1.5 and stock(k) > s0
    assert [x["agent"] for x in pub(k, "Duty Roster")["now"]] == ["Cy", "Di"]
    post(k, "Di", "Minutes of round 2: the meeting met.")
    assert "excused" in invoke(k, "Cy", "excuse_duty", "Cy", "sick")
    T.step(k)
    log = pub(k, "Duty Roster")["log"]
    assert {(x["agent"], x["status"]) for x in log if x["round"] == 2} == {("Cy", "excused"), ("Di", "met")}
    assert pub(k, "Duty Roster")["book"]["Cy"]["excused"] == 1


# ---------------------------------------------------------------------- force: militia and muster
def test_militia_roll_rotates_the_duty_right_and_pays_a_kept_watch(tmp_path):
    k = setup(tmp_path, world())
    m = pub(k, "Militia Roll")
    assert m["on_duty"] == ["Ada", "Bo"] and m["next"] == ["Cy", "Di"]
    assert k.law_has("Ada", "militia_duty") and not k.law_has("Cy", "militia_duty")
    with pytest.raises(ActionError):
        invoke(k, "Cy", "report_duty")                                  # not on duty
    assert "report" in invoke(k, "Ada", "report_duty")
    T.step(k)
    assert k.law_has("Cy", "militia_duty") and not k.law_has("Ada", "militia_duty")
    log = pub(k, "Militia Roll")["log"]
    assert {(x["agent"], x["status"]) for x in log} == {("Ada", "met"), ("Bo", "missed")}
    rows = [x for x in pub(k, "Mutual Credit")["log"] if x["why"].startswith("Militia Roll")]
    assert [(x["to"], x["qty"]) for x in rows] == [("Ada", 1)]
    lid = law(k, "Armoury Act")                                        # common arms are issued only to the militia on duty
    with pytest.raises(ActionError, match="none of the offices"):
        invoke(k, "Di", "request_arms", "Ada", "weapons", "patrol")
    assert "request" in invoke(k, "Di", "request_arms", "Cy", "weapons", "patrol")
    rid = next(iter(k.w["laws"][lid]["public"]["requests"]))
    assert "issued 1 weapons to Cy" in invoke(k, "Ed", "issue_arms", rid)


def test_a_passed_muster_lets_the_militia_on_duty_arrest_and_detain(tmp_path):
    import test_force as TF
    k = setup(tmp_path, world())
    post(k, "Bo", "MOTION: MUSTER Fay for taking food from the store")
    votes(k, "M1", yes=["Ada", "Bo", "Cy", "Di"], no=["Fay"])
    T.step(k, 2)
    u = pub(k, "Muster Act")["musters"]["U1"]
    assert u["target"] == "Fay" and not u["lethal"] and u["status"] == "open"
    on = pub(k, "Militia Roll")["on_duty"]
    assert on == ["Ed", "Fay"]                                          # round 3: the target itself is on duty
    with pytest.raises(ActionError):
        invoke(k, "Ada", "serve_muster", "U1")                          # off duty: no right
    with pytest.raises(ActionError, match="yourself"):
        invoke(k, "Fay", "serve_muster", "U1")
    with TF.CF_rolls(attack=0.0):
        out = invoke(k, "Ed", "serve_muster", "U1")
    assert "served: Fay subdued" in out
    assert pub(k, "Muster Act")["musters"]["U1"]["status"] == "served"
    assert k.w["agents"]["Fay"]["limit"]                               # detained
    T.step(k)
    assert ("Ed", "met") in {(x["agent"], x["status"]) for x in pub(k, "Militia Roll")["log"]}    # serving is duty kept


def test_an_unserved_muster_lapses(tmp_path):
    k = setup(tmp_path, world())
    post(k, "Bo", "MOTION: MUSTER Fay")
    votes(k, "M1", yes=["Ada", "Bo", "Cy", "Di"])
    T.step(k, 5)
    assert pub(k, "Muster Act")["musters"]["U1"]["status"] == "lapsed"


def test_zero_attention_three_rounds(tmp_path):
    """Framework §11 check 2: nobody acts for 3 rounds; pooling, meals, dues, the rota and the militia all run, no law errors."""
    sp = world()
    sp["rounds"] = 3
    _, rd = T.run(tmp_path, sp)
    evs = T.events(rd)
    assert not [e for e in evs if e["type"] in ("law_error",)]
    k = T.kernel_at(rd, 3)
    assert len(pub(k, "Duty Roster")["log"]) == 6 and len(pub(k, "Militia Roll")["log"]) == 6
    assert len([x for x in pub(k, "Mutual Credit")["log"] if x["why"].startswith("Commons Dues")]) == 18
    assert sum(pub(k, "Mutual Credit")["balances"].values()) == pytest.approx(0, abs=1e-6)
