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


def _evening_run(tmp_path, days, reply):
    s = load_spec(SPEC)
    s.update(evening=True, tags=True, ages=True)
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
