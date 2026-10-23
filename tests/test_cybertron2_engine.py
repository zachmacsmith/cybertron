"""The rebuilt engine (D4-34, D4-35; review 38.17 §8): the chokepoint's place checks, conservation of goods, the scope canary, the
source check, and the verbs, households, hosting, building, farming, agreements, travel and talk."""
import ast
import copy
import inspect
import json

import pytest

from cybertron2.engine import agreements as AG, knowledge as KN, night as N, perceive as PC, prompt as PR, run as R, settle as ST
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import PlaceError, World, load_spec

SPEC = load_spec("cybertron2/specs/valley_s5.yaml")


def world(**over):
    s = copy.deepcopy(SPEC)
    s.update(over)
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def next_day(w):
    N.night(w)
    w.s["day"] += 1
    w.s["events"] = []
    w.s["today"] = R.blank_today()
    R.dawn(w)


# ---------------------------------------------------------------------- the core
def test_agent_facing_modules_never_read_the_world():
    """D4-35: verbs, prompts and the knowledge views see only Here and Mind (engine-side functions are listed)."""
    engine_side = {KN: {"seed", "_set"}, AG: {"settle", "_due", "_person_for", "_present_for", "install", "_credit"}, V: set(), PR: set()}
    for mod, allowed in engine_side.items():
        tree = ast.parse(inspect.getsource(mod))
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name not in allowed]:
            for node in ast.walk(fn):
                if isinstance(node, ast.Attribute) and node.attr in ("s", "_w"):
                    pytest.fail(f"{mod.__name__}.{fn.name} reads world state ({node.attr})")


def test_a_primitive_cannot_touch_another_place():
    w = world()
    with pytest.raises(PlaceError):                                     # Warin is at Coppergate, Edric at Millbrook
        w.apply("transfer", "millbrook", src=w.hands("Warin"), dst=w.hands("Edric"), item="coin", qty=1)
    with pytest.raises(PlaceError):
        w.event(None, "x", "nowhere")


def test_goods_are_conserved_except_by_create_and_destroy():
    w = world(bot_travel=True)
    delta = {"n": 0.0}

    def total():
        return sum(q for c in w.s["containers"].values() for q in c["goods"].values())
    w.hook("after", "create", lambda w_, call, out: delta.__setitem__("n", delta["n"] + call["kw"]["qty"]))
    w.hook("after", "destroy", lambda w_, call, out: delta.__setitem__("n", delta["n"] - out))
    start = total()
    for d in range(4):
        w.s["day"] = d
        w.s["events"] = []
        w.s["today"] = R.blank_today()
        R.dawn(w)
        for n in w.agents_acting():
            for a in R.bot_plan(w, n)["actions"]:
                if n not in w.s["today"]["travel"] and w.at(n):
                    V.do(Here(w, n), Mind(w, n), a)
        AG.settle(w)
        N.night(w)
    assert abs(total() - (start + delta["n"])) < 1e-4


def test_scope_canary_nothing_from_another_node():
    """D4-35: what happens at Coppergate never reaches the prompt of someone in Millbrook who has no way to know it."""
    w = world()
    w.s["buildings"]["smithy"]["name"] = "ZZCANARY Forge"                 # renamed after seeding: nobody's mind knows it
    w.event("coppergate", "sign", "ZZCANARY smoke over the hill", salience=1.0, dawn=True)
    w.s["containers"]["stock:smith_house"]["goods"]["ZZCANARY"] = 0.0
    PC.dawn(w)
    PC.evening(w, {}, w.s["today"])
    for n in w.agents_acting():
        h, m = Here(w, n), Mind(w, n)
        text = PR.system_prompt(h, m) + PR.turn_prompt(h, m) + json.dumps(PR.schema_for(h, m))
        if w.at(n) == "coppergate":
            assert "ZZCANARY" in text, n
        else:
            assert "ZZCANARY" not in text, n


def test_every_verb_refuses_what_is_at_another_node():
    w = world()
    assert do(w, "Edric", do="give", to="Warin", item="coin", qty=1).startswith("Refused")
    assert do(w, "Edric", do="take", item="copper", qty=1, **{"from": "Smith House"}).startswith("Refused")
    assert do(w, "Edric", do="host", person="Warin").startswith("Refused")
    assert do(w, "Edric", do="attack", target="Smith House").startswith("Refused")
    assert do(w, "Edric", do="gather", what="forage", at="Deep Wood").startswith("Refused")
    assert do(w, "Edric", do="claim", thing="the Seam").startswith("Refused")


# ---------------------------------------------------------------------- the verbs
def test_gathering_and_making_from_data():
    w = world()
    assert do(w, "Warin", do="gather", what="mine").startswith("You took")
    assert do(w, "Warin", do="gather", what="mine", at="the Hillside").startswith("Refused")
    r = do(w, "Osric", do="make", what="smelt")                          # ore and timber from the household's store
    assert r.startswith("You made 1 copper"), r
    assert do(w, "Edric", do="make", what="smelt").startswith("Refused")  # not known, no anvil here


def test_inputs_are_all_or_nothing():
    w = world()
    before = dict(w.goods("stock:reed_house"))
    assert do(w, "Edric", do="build", what="small room", at="the Green").startswith("Refused")
    assert w.goods("stock:reed_house") == before


def test_taking_without_the_right_is_theft_and_using_against_a_claim_is_seen():
    w = world()
    r = do(w, "Sibyl", do="take", item="grain", qty=1, **{"from": "Hale House"})
    assert "not yours" in r and w.s["today"]["thefts"]
    w.s["parcels"]["long_field"]["crop"]["ripe_day"] = 0
    r = do(w, "Tiffany", do="work", what="reap", at="Long Field")
    assert "Reeds also claim" in r                                       # the Hales claim it too: a dispute, seen


def test_farming_sow_ripen_reap_and_rot():
    w = world()
    w.s["parcels"]["brook_field"]["crop"] = None
    w.s["containers"][w.hands("Hamo")]["goods"]["grain"] = 6
    assert do(w, "Hamo", do="work", what="sow", at="Brook Field").startswith("You sowed")
    c = w.s["parcels"]["brook_field"]["crop"]
    assert c["ripe_day"] == w.d + int(w.p["farming"]["grow_days"])
    assert do(w, "Hamo", do="work", what="reap", at="Brook Field").startswith("Refused")
    left = c["left"]
    w.s["day"] = c["ripe_day"] + c["window"]
    N._grow(w)
    assert w.s["parcels"]["brook_field"]["crop"]["left"] < left          # rotting after the window (D2-12)


def test_building_a_house_and_living_in_it():
    w = world()
    me = w.hands("Osric")
    w.s["containers"][me]["goods"].update({"timber": 20, "hide": 2})
    assert do(w, "Osric", do="found", name="Osric").startswith("You are now the head")
    assert w.homes("Osric") == []
    r = do(w, "Osric", do="build", what="small room", at="the Yard", name="Osric's House")
    assert r.startswith("You began"), r
    bid = next(b for b, x in w.s["buildings"].items() if x["name"] == "Osric's House")
    while w.s["buildings"][bid].get("unfinished"):
        do(w, "Osric", do="build", what="small room", at="Osric's House")
    assert do(w, "Osric", do="build", what="beds", at="Osric's House", qty=2).startswith("You put")
    assert bid in w.homes("Osric")
    assert N.sleeping_places(w, w.s["today"])["Osric"] == bid


# ---------------------------------------------------------------------- households and hosting (09 §2d, 05 §3; D4-36)
def test_joining_a_household_by_asking_and_being_admitted():
    w = world()
    w.s["people"]["Warin"]["at"] = "ashwood"
    assert do(w, "Warin", do="join", household="Fenn").startswith("You asked")
    assert do(w, "Edith", do="admit", person="Warin").startswith("Refused")   # only the head admits, by default
    assert do(w, "Simkin", do="admit", person="Warin").startswith("You agreed")
    ST.settle_joins(w, w.s["today"])
    assert w.household_of("Warin") == "Fenn" and "fenn_house" in w.homes("Warin")
    assert "Warin" not in w.s["institutions"]["Smith"]["members"] and w.head("Smith") != "Warin"


def test_hosting_shelters_and_feeds_only_if_asked():
    w = world()
    for x in ("Warin", "Osric"):
        w.s["people"][x]["at"] = "ashwood"
        w.s["containers"][w.hands(x)]["goods"] = {}
    assert do(w, "Simkin", do="host", person="Warin", feed=True).startswith("You let")
    assert do(w, "Simkin", do="host", person="Osric").startswith("You let")
    rec = N.night(w)
    assert rec["slept"]["Warin"] == "Fenn House" and rec["slept"]["Osric"] == "Fenn House"
    assert "Warin" not in rec["missed"] and "Osric" in rec["missed"]


def test_a_guest_needs_a_free_bed():
    w = world()
    w.s["buildings"]["hale_house"]["fittings"]["beds"] = 2
    w.s["people"]["Warin"]["at"] = "millbrook"
    assert do(w, "Hamo", do="host", person="Warin").startswith("You let")
    assert N.sleeping_places(w, w.s["today"])["Warin"] is None           # Hamo and Tiffany fill both beds
    w.s["buildings"]["hale_house"]["fittings"]["beds"] = 3
    assert N.sleeping_places(w, w.s["today"])["Warin"] == "hale_house"


# ---------------------------------------------------------------------- offers and agreements (D2-25 to D2-40)
def test_a_promise_is_paid_where_both_are_and_falls_into_arrears_apart():
    w = world()
    h = Here(w, "Edric")
    line = AG.make_offer(h, Mind(w, "Edric"), {"to": "anyone", "give": "2 grain", "get": "1 timber by day 2"})
    oid = line.split()[2].rstrip(":")
    w.s["containers"][w.hands("Hamo")]["goods"]["timber"] = 0
    w.s["containers"]["stock:hale_house"]["goods"]["timber"] = 0
    assert do(w, "Hamo", do="accept", offer=oid).startswith("You accepted")
    aid = next(a for a, x in w.s["agreements"].items() if x.get("offer") == oid)
    w.s["day"] = 1
    AG.settle(w)
    assert w.s["agreements"][aid]["legs"][1]["arrears"] == 1                # Hamo had no timber
    w.s["containers"][w.hands("Hamo")]["goods"]["timber"] = 2
    w.s["day"] = 2
    AG.settle(w)
    assert w.s["agreements"][aid]["status"] == "done"


def test_work_legs_are_met_by_work_done_for_the_payee():
    w = world()
    h = Here(w, "Edric")
    line = AG.make_offer(h, Mind(w, "Edric"), {"to": "Cecily", "give": "1 bread", "get": "work 1 days"})
    oid = line.split()[2].rstrip(":")
    assert do(w, "Cecily", do="accept", offer=oid).startswith("You accepted")
    assert do(w, "Cecily", do="gather", what="fell", at="Alder Copse", **{"for": "Edric"}).startswith("You took")
    assert w.goods(w.hands("Edric")).get("timber", 0) > 0
    AG.settle(w)
    aid = next(a for a, x in w.s["agreements"].items() if x.get("offer") == oid)
    assert w.s["agreements"][aid]["status"] == "done"


# ---------------------------------------------------------------------- travel, talk, a run
def test_travel_arrive_and_leave_goods_when_too_heavy():
    w = world()
    w.s["containers"][w.hands("Simkin")]["goods"]["timber"] = 6
    assert do(w, "Simkin", do="travel", to="Coppergate").startswith("Refused: travel: you carry")
    assert do(w, "Simkin", do="leave", item="timber", qty=3, at="Fenn House").startswith("You left")
    assert do(w, "Simkin", do="travel", to="Coppergate").startswith("You set off")
    w.s["left"] = [{**x, "day": w.d} for x in w.s["today"]["left"]]
    next_day(w)
    assert w.at("Simkin") == "coppergate"
    assert any(e["kind"] == "left" and e["place"] == "ashwood" for e in w.s["events"])


def test_only_direct_speech_wakes_and_messages_are_rationed():
    w = world()
    names = w.agents_acting()
    replies = {n: {} for n in names}
    replies["Edric"] = {"say": [{"to": "everyone", "text": "hello"}], "tell": [{"to": "Sibyl", "text": "x"}] * 3}
    results = {n: [] for n in names}
    woken = R.talk(w, names, replies, results)
    assert set(woken) == {"Sibyl"}
    w.s["people"]["Edric"]["messages"] = 2
    results = {n: [] for n in names}
    R.talk(w, names, replies, results)
    assert sum(x.startswith("You told") for x in results["Edric"]) == 2


def test_bot_run_is_deterministic(tmp_path):
    for k in ("a", "b"):
        R.run("cybertron2/specs/valley_s5.yaml", tmp_path / k, days=4, bots=True)
    assert (tmp_path / "a" / "days.jsonl").read_text() == (tmp_path / "b" / "days.jsonl").read_text()


def test_accepting_reads_the_offerers_goods_not_ones_own():
    w = world()
    w.s["people"]["Warin"]["at"] = "ashwood"
    line = AG.make_offer(Here(w, "Warin"), Mind(w, "Warin"), {"to": "anyone", "give": "1 copper tool", "get": "4 wild food"})
    oid = line.split()[2].rstrip(":")
    w.s["containers"][w.hands("Simkin")]["goods"]["wild food"] = 4
    assert do(w, "Simkin", do="accept", offer=oid).startswith("You accepted")
    assert w.goods(w.hands("Simkin")).get("copper tool") == 1


def test_a_tool_in_the_store_is_named_when_refused():
    w = world()
    w.s["containers"]["stock:smith_house"]["goods"]["crude tool"] = 1
    r = do(w, "Osric", do="gather", what="mine")
    assert "Smith House's store" in r


def test_giving_or_leaving_goods_pays_a_debt():
    w = world()
    w.s["people"]["Simkin"]["at"] = "coppergate"
    aid = w.apply("agree", None, node="coppergate", rec={"parties": ["Simkin", "Elena"], "status": "open",
                  "legs": [{"from": "Simkin", "to": "Elena", "item": "wild food", "qty": 8, "when": {"by": 3}, "paid": 0, "arrears": 0.0}]})
    w.s["containers"][w.hands("Simkin")]["goods"]["wild food"] = 10
    assert do(w, "Simkin", do="leave", item="wild food", qty=5, at="Smith House").startswith("You left")
    assert w.s["agreements"][aid]["legs"][0]["prepaid"] == 5
    assert do(w, "Simkin", do="give", to="Elena", item="wild food", qty=3).startswith("You gave")
    assert w.s["agreements"][aid]["status"] == "done"


def test_promises_read_season_dates():
    w = world()
    legs = AG.parse_legs("1 copper tool by autumn day 3", 0, w.calendar)
    c = w.calendar(legs[0]["when"]["by"])
    assert (c["season"], c["day"]) == ("autumn", 3)
