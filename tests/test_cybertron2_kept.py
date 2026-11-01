"""Lines kept for good (D4-64; spec/information/memory.md "Kept for good", life/birth_and_death.md "Passing on", seeding/
populations.md "Customs"): places counted from coming of age and opening evenly over adult life; customs seeded as kept lines to
those alive at the start; keep and drop at the memory request; passing on with care, the most food winning."""
import copy
import json

from cybertron2.engine import life as LF, memory as MEM, night as N, run as R
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = load_spec("cybertron2/specs/valley_s5.yaml")


def world(**patch):
    s = copy.deepcopy(SPEC)
    s["children"] = {"on": True, "dial": "low"}
    s.update(patch)
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def adult(w):
    n = next(n for n, a in w.s["people"].items() if a["stage"] == "adult")
    w.s["people"][n].setdefault("born", None)
    if w.s["people"][n]["born"] is None:                                       # this world is undated: a grown woman of 20 days
        w.s["people"][n]["born"] = w.d - 20
    return n


def test_places_start_with_the_lines_held_and_one_more_then_open_evenly():
    w = world()
    n = adult(w)
    L = LF.lifespan(w)
    youth = sum(d for st, d in LF.spans(L) if st in LF.MINOR)
    w.s["people"][n]["born"] = w.d - youth                                     # comes of age today
    k = MEM.kept(w, n)
    k["lines"] = [{"text": "a", "source": "x", "day": 0, "fixed": False}, {"text": "b", "source": "x", "day": 0, "fixed": False}]
    MEM.come_of_age(w, n, day=w.d)
    most, span, d0 = 3 + round(L / 5), L - youth, w.d
    seen = []
    for d in range(0, span + 1):
        w.s["day"] = d0 + d
        seen.append(MEM.places(w, n))
    assert seen[0] == 3 and seen[-1] == most                                   # childhood lines + 1, up to the most at the end
    steps = [b - a for a, b in zip(seen, seen[1:])]
    assert all(s in (0, 1) for s in steps)                                     # one at a time, spread over the whole adult span
    firsts = [i for i, s in enumerate(steps) if s]
    assert firsts[0] < span // 3 and firsts[-1] > 2 * span // 3


def test_customs_are_kept_lines_of_those_alive_at_the_start_and_fixed_ones_cannot_be_dropped():
    w = world(customs=[{"text": "We share the first loaf.", "nodes": "all"}, {"text": "Never sell the ox.", "nodes": "all", "fixed": True}])
    n = adult(w)
    texts = MEM.kept_lines_text(w, n)
    assert "We share the first loaf." in texts and "Never sell the ox." in texts
    assert "We share the first loaf." not in " ".join(w.s["mind"][n]["seeded"])   # no longer among what one always remembers
    assert MEM.places(w, n) >= 3                                                 # a grown adult: places for its age
    out = MEM.kept_apply(w, n, {"drop": [1, 2]})
    assert out["forgot"] == ["We share the first loaf."] and MEM.kept_lines_text(w, n) == ["Never sell the ox."]
    baby = w.apply("born", w.place_of(("person", n)), mother=next(x for x, a in w.s["people"].items() if a.get("sex") == "f" and a["stage"] == "adult"))
    assert MEM.kept_lines_text(w, baby) == []                                    # nobody born in a run is seeded a custom


def test_keep_fills_empty_places_refuses_past_them_and_the_request_says_when_a_place_opened():
    w = world()
    n = adult(w)
    MEM.come_of_age(w, n, day=w.d)
    out = MEM.kept_apply(w, n, {"keep": ["First.", "Second."]})
    assert out["kept"] == ["First."] and out["refused"] == ["Second."]           # one place at first
    ask = MEM.kept_request(w, n)
    assert "## Kept for good (1 of 1 place)" in ask and "found no empty place" in ask and '"drop"' in ask
    w.s["day"] += LF.lifespan(w)                                                 # later in life: more places
    ask = MEM.kept_request(w, n)
    assert "opened since last time" in ask and "(empty)" in ask
    out = MEM.kept_apply(w, n, {"drop": [1], "keep": ["Third."]})
    assert MEM.kept_lines_text(w, n) == ["Third."]                               # an emptied place filled at once
    w.spec.setdefault("memory", {})["kept"] = {"refill": "next", "schedule": "none"}
    MEM.kept(w, n)["start"] = 1
    out = MEM.kept_apply(w, n, {"drop": [1], "keep": ["Fourth."]})
    assert out["refused"] == ["Fourth."] and MEM.kept_lines_text(w, n) == []    # the per-run option: free only from next time


def test_the_most_food_feeds_the_child_and_its_giver_passes_on_the_line():
    w = world()
    kid = None
    for n, a in w.s["people"].items():
        if a["stage"] == "adult" and a.get("sex") == "f":
            kid = w.apply("born", w.place_of(("person", n)), mother=n)
            break
    w.s["people"][kid]["stage"] = "infant"
    here = w.at(kid)
    carers = [x for x in w.present(here) if w.s["people"][x]["stage"] == "adult"][:2]
    big, small = carers
    for x, q in ((big, 3.0), (small, 1.0)):
        w.s["containers"][w.hands(x)]["goods"]["bread"] = q
    assert "you passed on" in do(w, small, do="work", what="care", at=kid, item="bread", qty=1, **{"pass": "Small says this."})
    assert "you mean to give" in do(w, big, do="work", what="care", at=kid, item="bread", qty=3, **{"pass": "Big says this."})
    rec = N.night(w)
    from cybertron2.engine.data import ITEMS
    assert abs(rec["care"]["fed"][kid] - 3.0 * ITEMS["bread"]["food"]) < 1e-9     # all of the largest care's food, and only it
    assert w.goods(w.hands(big)).get("bread", 0) < 1e-9
    assert MEM.kept(w, kid)["lines"][0]["text"] == "Big says this." and MEM.kept(w, kid)["lines"][0]["source"] == f"from {big}"
    lines = R.night_lines(w, rec)
    assert any("will keep what you passed on" in x for x in lines[big])
    assert any(f"what {big} passed on" in x for x in lines[small])


def test_childhood_lines_add_places_up_to_the_limit_and_coming_of_age_counts_from_them():
    w = world()
    mom = next(n for n, a in w.s["people"].items() if a["stage"] == "adult" and a.get("sex") == "f")
    kid = w.apply("born", w.place_of(("person", mom)), mother=mom)
    for i in range(6):
        w.s["today"] = R.blank_today()
        w.s["people"][kid]["stage"] = "infant"
        do(w, mom, do="work", what="care", at=kid, **{"pass": f"Line {i}."})
        LF.care_gifts(w, w.s["today"])
    assert len(MEM.kept(w, kid)["lines"]) == MEM.KEPT["childhood"]               # four, then no more
    w.s["people"][kid]["stage"] = "youth"
    LF.come_of_age(w, kid)
    assert MEM.kept(w, kid)["start"] == MEM.KEPT["childhood"] + 1 and MEM.places(w, kid) == MEM.KEPT["childhood"] + 1


def test_in_a_run_the_memory_request_asks_and_the_opening_shows_what_is_kept(tmp_path, monkeypatch):
    from cybertron import llm
    calls = []

    def api(model, system, user, schema, thinking_budget, max_tokens):
        u = str(user)
        calls.append(u)
        if "## Kept for good (" in u:
            raw = json.dumps({"why": "", "actions": [], "memory": "The barley is late.", "keep": ["The river floods in spring."]})
        else:
            raw = json.dumps({"why": "steady", "actions": [{"do": "gather", "what": "forage"}]})
        return raw, json.loads(raw), "", {}
    monkeypatch.setattr(llm, "_api", api)
    spec = copy.deepcopy(SPEC)
    spec["memory"] = {"mode": "rewrite", "chunk": 2}
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    monkeypatch.setattr(R, "load_spec", lambda path: json.loads(open(path).read()))
    R.run(str(p), tmp_path / "run", backend="api", days=5)
    asks = [c for c in calls if "## Kept for good (" in c]
    assert asks and all(c.rstrip().endswith("Reply with JSON only.") for c in asks)
    st = json.loads((tmp_path / "run" / "state.json").read_text())
    held = [m for m in st["mind"].values() if any(x["text"] == "The river floods in spring." for x in (m.get("kept") or {}).get("lines", []))]
    assert held
    assert any("## Kept for good\n- The river floods in spring." in c for c in calls)
