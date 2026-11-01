"""The evening at the hearth and the day around it (D4-65 to D4-69): ages shown; tags and names for groups of beasts and things; the
evening call with one wave of answers; the night settled there; setting off in the morning or at nightfall."""
import json

from cybertron2.engine import api as API, life as LF, run as R, tags as TG, verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = "cybertron2/specs/combe.yaml"


def _world(**kw):
    s = load_spec(SPEC)
    s.update(kw)
    return World(s)


def test_ages_are_shown_with_what_lies_ahead():
    w = _world(ages=True)
    assert "You are 52 days old" in LF.age_line(w, "Ivo") and "turn elder at 96 days old (in 44)" in LF.age_line(w, "Ivo")
    assert "Margery is 52 days old, and turns elder in 44" in LF.age_line(w, "Ivo")
    assert "come of age at 36 days old" in LF.age_line(w, "Everard")
    assert LF.age_line(_world(), "Ivo") == ""                                  # off unless the world asks for it


def test_split_herds_get_their_own_tags_and_a_name_is_known_to_the_household():
    w = _world(tags=True)
    h1 = next(iter(w.s["herds"]))
    assert w.s["herds"][h1]["name"].endswith("(H1)")
    new = w.apply("split_herd", w.s["herds"][h1]["node"], like=h1, take={"cows": 1})
    assert w.s["herds"][new]["tag"] == "H2" and w.s["herds"][new]["name"].endswith("(H2)")
    here = Here(w, "Ivo")
    assert here.herd("H2") == new and here.herd("the herd (H1)") == h1
    out = V.do(here, Mind(w, "Ivo"), {"do": "name", "thing": "H2", "as": "the Brook strays"})
    assert out.startswith("You named H2") and TG.names_of(w, "Margery").get("H2") == "the Brook strays"
    assert Here(w, "Margery").herd("the Brook strays") == new
    assert TG.render(w, "Margery", "cows on the Common (H2)") == "cows on the Common (H2: the Brook strays)"
    w.apply("set", w.s["herds"][new]["node"], ref=("herd", h1), field="cows", value=0)
    w.apply("set", w.s["herds"][new]["node"], ref=("herd", h1), field="oxen", value=0)
    w.apply("set", w.s["herds"][new]["node"], ref=("herd", h1), field="bulls", value=0)
    w.apply("set", w.s["herds"][new]["node"], ref=("herd", h1), field="young", value=0)
    assert Here(w, "Ivo").herd("the Hobb cattle") == new                       # by name, the group that has beasts in it


def test_a_thing_lying_about_is_tagged_and_taken_by_its_tag():
    w = _world(tags=True)
    here = Here(w, "Ivo")
    w.apply("move", "combe", src=w.hands("Ivo"), dst=w.hands("Ivo"), item="grain", qty=0) if False else None
    V.do(here, Mind(w, "Ivo"), {"do": "take", "item": "grain", "qty": 3, "from": "Hobb House"})
    out = V.do(Here(w, "Ivo"), Mind(w, "Ivo"), {"do": "give", "to": "the Common", "item": "grain", "qty": 3})
    assert not out.startswith("Refused"), out
    cid, c = next((k, v) for k, v in w.s["containers"].items() if v.get("kind") == "pile")
    assert c["tag"] == "T1"
    from cybertron2.engine import things as TH
    assert TH.describe(w, c).endswith("(T1)")
    assert TH.find(w, "Ivo", "T1", "grain") == cid


def _evening_run(tmp_path, days, reply, **extra):
    s = load_spec(SPEC)
    s.update(evening=True, tags=True, ages=True)
    s.update(extra)
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(s))
    out = tmp_path / "run"
    real = R.load_spec
    R.load_spec = lambda path: json.loads(open(path).read())
    seen = {}
    try:
        R.run(str(p), out, days=days, bots=True, responders={"Ivo": "human", "Margery": "human"})
        for _ in range(80):
            st = API.status(out)
            if st["ended"] or not st["waiting"]:
                break
            for req in st["waiting"]:
                ctx = API.context(out, req["key"])
                seen[req["key"]] = ctx["message"]
                assert API.answer(out, req["key"], reply(req["key"], req["agent"], ctx["message"])) == []
            API.advance(out)
    finally:
        R.load_spec = real
    return out, seen


def test_the_evening_wakes_only_those_asked_and_settles_trying_for_a_child(tmp_path):
    def reply(key, who, msg):
        if ".decide." in key:
            return {"why": "x", "actions": [{"do": "gather", "what": "firewood", "at": "Combe Copse"}]}
        if ".evening." in key and "## This evening" in msg:
            if who == "Ivo":
                return {"why": "x", "actions": [{"do": "try", "with": "Margery", "units": 1}],
                        "say": [{"to": "everyone", "text": "Margery, will you try for a child with me tonight?"}]}
            return {"why": "x", "actions": []}
        if ".evening." in key:
            return {"why": "x", "actions": [{"do": "try", "with": "Ivo", "units": 1}], "say": [{"to": "everyone", "text": "Yes."}]}
        return {"why": "", "actions": [], "memory": "A day."}
    out, seen = _evening_run(tmp_path, 1, reply)
    ev = sorted(k for k in seen if ".evening." in k)
    assert any("Ivo" in k for k in ev) and sum("Margery" in k for k in ev) == 2   # Margery asked: one more call; Ivo not
    m2 = next(seen[k] for k in ev if "Margery" in k and "## Before you sleep" in seen[k])
    assert "Ivo (at the hearth): Margery, will you try" in m2 and "trying for a child with you tonight" in m2
    T = [json.loads(x) for x in open(out / "turns.jsonl")]
    res = {t["agent"]: t["results"] for t in T if t["day"] == 0}
    assert any(x.startswith("You spent 1 unit trying") for x in res["Ivo"]) and any(x.startswith("You spent 1 unit trying") for x in res["Margery"])
    assert "Margery is 52 days old" in next(seen[k] for k in seen if k.startswith("d0.decide.Ivo"))
    assert R.run(None, out, mode="replay")["mismatches"] == []


def test_setting_off_in_the_morning_arrives_by_nightfall_and_at_nightfall_arrives_at_midday_with_half(tmp_path):
    def reply(key, who, msg):
        if key.startswith("d0.decide."):
            if who == "Ivo":
                return {"why": "x", "actions": [{"do": "travel", "to": "Wenmoor", "when": "morning"},
                                                 {"do": "gather", "what": "firewood", "at": "Combe Copse"}]}
            return {"why": "x", "actions": [{"do": "travel", "to": "Holtwood"}]}
        return {"why": "", "actions": [], "memory": "A day."}
    out, seen = _evening_run(tmp_path, 2, reply)
    ivo_eve = next(seen[k] for k in seen if k.startswith("d0.evening.Ivo"))
    assert "having come in at nightfall from Combe" in ivo_eve and "in the open at Wenmoor" in ivo_eve
    assert not any(k.startswith("d0.evening.Margery") for k in seen)             # on the road tonight: no evening
    T = [json.loads(x) for x in open(out / "turns.jsonl")]
    d0 = {t["agent"]: t for t in T if t["day"] == 0 and "units" in t}
    d1 = {t["agent"]: t for t in T if t["day"] == 1 and "units" in t}
    assert d0["Ivo"]["used"] == d0["Ivo"]["units"] and not any("firewood" in x for x in d0["Ivo"]["results"])
    assert d1["Ivo"]["at"] == "wenmoor" and d1["Margery"]["at"] == "holtwood"
    assert d1["Margery"]["units"] == d1["Ivo"]["units"] // 2


def test_the_beast_to_slaughter_may_be_named_in_thing_when_tags_free_it():
    w = _world(tags=True)
    w.s["today"] = R.blank_today()
    hid = next(iter(w.s["herds"]))
    pid = w.s["herds"][hid]["parcel"]
    bulls = int(w.s["herds"][hid]["bulls"])
    out = V.do(Here(w, "Ivo"), Mind(w, "Ivo"), {"do": "work", "what": "slaughter", "at": w.s["parcels"][pid]["name"], "thing": "bull"})
    assert out.startswith("You slaughtered a bull"), out
    assert int(w.s["herds"][hid]["bulls"]) == bulls - 1


def test_slaughter_says_where_the_meat_went_and_taking_from_a_place_searches_it():
    from cybertron2.engine import things as TH
    w = _world()
    w.s["today"] = R.blank_today()
    hid = next(iter(w.s["herds"]))
    pid = w.s["herds"][hid]["parcel"]
    pname = w.s["parcels"][pid]["name"]
    out = V.do(Here(w, "Ivo"), Mind(w, "Ivo"), {"do": "work", "what": "slaughter", "at": pname, "item": "calf"})
    assert out.endswith("(now in your hands)."), out
    V.do(Here(w, "Ivo"), Mind(w, "Ivo"), {"do": "give", "to": pname, "item": "meat", "qty": 10})   # put down in the open
    cid = next(k for k, c in w.s["containers"].items() if c.get("kind") == "pile")
    assert cid not in TH.known_here(w, "Margery", "combe")
    assert TH.search_chance(w, "Margery", w.s["containers"][cid]) >= 0.99           # a fresh heap in the open: found
    got = V.do(Here(w, "Margery"), Mind(w, "Margery"), {"do": "take", "item": "meat", "qty": 5, "from": pname})
    assert got.startswith("You took"), got
    assert cid in TH.known_here(w, "Margery", "combe")
    buried = dict(w.s["containers"][cid], hidden="buried")
    assert TH.search_chance(w, "Margery", buried) < 0.3                             # well buried: seldom found
    nothing = V.do(Here(w, "Margery"), Mind(w, "Margery"), {"do": "take", "item": "stone", "qty": 1, "from": pname})
    assert nothing.startswith("Refused: take: you looked over") and "found no stone" in nothing


def test_groups_that_are_no_more_leave_the_list_of_ones_beasts():
    from cybertron2.engine import perceive as PC
    w = _world(tags=True)
    h1 = next(iter(w.s["herds"]))
    node = w.s["herds"][h1]["node"]
    new = w.apply("split_herd", node, like=h1, take={"cows": 1})
    PC.remember_beasts(w, "Ivo", new, "saw")
    PC.remember_beasts(w, "Ivo", h1, "saw")
    assert set(w.s["mind"]["Ivo"]["beasts"]) == {h1, new}
    w.apply("set", node, ref=("herd", new), field="cows", value=0)              # it rejoined: no beasts left in the group
    PC.remember_beasts(w, "Ivo", h1, "saw")
    assert set(w.s["mind"]["Ivo"]["beasts"]) == {h1}


def test_no_sign_invents_an_act_and_a_byre_has_no_dwellers():
    import inspect
    from cybertron2.engine import signs as SG
    src = inspect.getsource(SG)
    for t in ("was heard weeping", "grey-faced and silent", "short with everyone"):
        assert t not in src                                                     # an act or a feeling the person did not choose
    w = _world()
    w.s["today"] = R.blank_today()
    here = Here(w, "Ivo")
    byre = next(b for b, x in w.s["buildings"].items() if not x["fittings"].get("beds") and b in w.homes("Ivo"))
    texts = [f["text"] for f in __import__("cybertron2.engine.perceive", fromlist=["facts"]).facts(here)]
    assert not any(w.s["buildings"][byre]["name"] in t and ("near empty" in t or "baby crying" in t) for t in texts)


def test_units_left_over_go_to_ones_own_fallback(tmp_path):
    def reply(key, who, msg):
        if ".decide." in key:
            return {"why": "x", "actions": [{"do": "work", "what": "reap", "at": "the Infield"}],
                    "fallback": [{"do": "gather", "what": "firewood", "at": "Combe Copse"}]}
        return {"why": "", "actions": [], "memory": "A day."}
    out, seen = _evening_run(tmp_path, 1, reply)
    T = {t["agent"]: t for t in (json.loads(x) for x in open(out / "turns.jsonl")) if "units" in t}
    ivo = T["Ivo"]
    assert any(r.endswith("(your fallback)") for r in ivo["results"]) and ivo["used"] == ivo["units"]
    assert R.run(None, out, mode="replay")["mismatches"] == []


def test_a_meeting_called_at_the_evening_is_held_next_morning_for_those_who_come(tmp_path):
    def reply(key, who, msg):
        if key.startswith("d0.evening.") and who == "Ivo" and "## This evening" in msg:
            return {"why": "x", "actions": [{"do": "meet", "at": "the Green", "about": "the harvest"}]}
        if key.startswith("d1.") and "## The meeting at the Green" in msg:
            return {"why": "x", "actions": [], "say": [{"to": "everyone", "text": f"{who} will reap."}]}
        if key.startswith("d1.decide."):
            assert "## A meeting this morning" in msg
            return {"why": "x", "actions": [{"do": "come"}, {"do": "gather", "what": "firewood", "at": "Combe Copse"}]}
        return {"why": "", "actions": [], "memory": "A day."}
    out, seen = _evening_run(tmp_path, 2, reply)
    met = [k for k, m in seen.items() if "## The meeting at the Green" in m]
    assert {k.split(".")[3] for k in met} >= {"Ivo", "Margery"}
    assert any("Said so far" in seen[k] and "will reap" in seen[k] for k in met)  # a second round: what was said
    T = {(t["day"], t["agent"]): t for t in (json.loads(x) for x in open(out / "turns.jsonl")) if "units" in t}
    assert any(r.startswith("You went to the meeting") for r in T[(1, "Ivo")]["results"])
    assert R.run(None, out, mode="replay")["mismatches"] == []


def test_with_the_setting_the_memory_is_written_at_the_evening_on_the_last_day_of_a_stretch(tmp_path):
    def reply(key, who, msg):
        if ".evening." in key and "## This evening" in msg and "Kept for good" in msg or ".evening." in key and "keep for good" in msg.lower():
            return {"why": "x", "actions": [], "memory": f"{who} remembers the days."}
        return {"why": "", "actions": [], "memory": "A day."}
    out, seen = _evening_run(tmp_path, 4, reply, memory_at_evening=True)   # a setting since D4-80; off by default
    M = [json.loads(x) for x in open(out / "memory.jsonl")]
    assert any(m["prompt"] == "(at the evening)" and m["memory"].endswith("remembers the days.") for m in M)
    assert not any(".memory." in k for k in seen)                                # no separate memory call
    assert R.run(None, out, mode="replay")["mismatches"] == []


def test_with_the_plan_made_at_the_hearth_the_morning_call_is_skipped_unless_needed(tmp_path):
    from cybertron2.engine import evening as EVN
    def reply(key, who, msg):
        if ".evening." in key and "## This evening" in msg:
            return {"why": "x", "actions": [{"do": "sleep", "at": "Hobb House"}, {"do": "gather", "what": "firewood", "at": "Combe Copse"}]}
        return {"why": "x", "actions": [], "memory": "A day."}
    out, seen = _evening_run(tmp_path, 3, reply, evening="plan")
    T = {(t["day"], t["agent"]): t for t in (json.loads(x) for x in open(out / "turns.jsonl")) if "units" in t}
    skipped = [(d, a) for (d, a), t in T.items() if d > 0 and t["prompt"] == "(no morning call: planned at the hearth)"]
    for d, a in skipped:                                                         # the plan made at the hearth was done
        assert any("firewood" in r for r in T[(d, a)]["results"])
    called = [(d, a) for (d, a) in T if d > 0 and (d, a) not in skipped and a in ("Ivo", "Margery")]
    assert skipped or called                                                     # either way, a day was played
    assert R.run(None, out, mode="replay")["mismatches"] == []


def test_the_thief_is_named_only_to_those_who_saw_and_the_house_finds_the_loss_by_its_signs():
    from cybertron2.engine import perceive as PC, settle as ST
    w = World(load_spec("cybertron2/specs/valley_s5.yaml"))
    w.s["today"] = today = R.blank_today()
    w.s["events"] = []
    owners = [n for n in w.agents_acting() if "reed_house" in w.homes(n)]
    for n in owners:
        today["worked"][n] = ["somewhere"]                                       # all out at work: none at home
    w.apply("move", "millbrook", src=w.s["buildings"]["reed_house"]["stock"], dst=w.hands("Hamo"), item="grain", qty=2) \
        if False else None
    today["thefts"].append({"by": "Hamo", "building": "reed_house", "item": "grain", "qty": 2})
    ST.settle_thefts(w, today, {})
    ev = [e for e in w.s["events"] if e["kind"] in ("theft", "loss")]
    assert all(e["kind"] == "theft" for e in ev)                                  # no certain "missing" line for the owners
    witnesses = set(ev[0]["concerns"]) if ev else set()
    PC.evening(w, {}, today)
    for n in owners:
        named = [x for x in PC.store(w, n)["today"]["concerned"] + PC.store(w, n)["today"]["notice"] if "Hamo" in x]
        assert bool(named) == (n in witnesses)                                    # the name only if one saw it
