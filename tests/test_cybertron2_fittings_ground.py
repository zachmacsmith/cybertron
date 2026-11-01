"""A fitting's work charged over days (02zg 1), and each parcel's ground shown used and free (D2-164; 02zg 2)."""
from cybertron2.engine import night as N, prompt as PR, run as R, verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = "cybertron2/specs/combe.yaml"


def _w():
    w = World(load_spec(SPEC))
    w.s["today"] = R.blank_today()
    stock = w.s["buildings"]["hobb_house"]["stock"]
    w.apply("create", "combe", dst=stock, item="timber", qty=200, why="test")
    w.apply("create", "combe", dst=stock, item="stone", qty=50, why="test")
    w.apply("create", "combe", dst=stock, item="straw", qty=50, why="test")
    w.apply("learn", "combe", person="Ivo", tech="cellar", level="known", source="test")
    for t in ("cellar", "beds", "bins"):                                         # an ordinary hand: 2 units of work an action
        if t not in w.s["know"]["Ivo"]:
            w.apply("learn", "combe", person="Ivo", tech=t, level="known", source="test")
        w.s["know"]["Ivo"][t]["skill"] = 1.0
    return w


def _build(w, what, qty=None):
    a = {"do": "build", "what": what, "at": "Hobb House"}
    if qty:
        a["qty"] = qty
    return V.do(Here(w, "Ivo"), Mind(w, "Ivo"), a)


def _fits(w):
    return w.s["buildings"]["hobb_house"]["fittings"]


def test_bins_take_one_action_and_a_cellar_four_counting_only_when_finished():
    w = _w()
    w.apply("set", "combe", ref=("building", "hobb_house"), field="fittings", value={k: v for k, v in _fits(w).items() if k != "bins"})
    assert _build(w, "bins").startswith("You put bins into Hobb House") and _fits(w).get("bins") == 1
    stock = w.s["containers"][w.s["buildings"]["hobb_house"]["stock"]]
    base = N.decay_rate(w, stock, "grain")[0]
    outs = [_build(w, "cellar") for _ in range(4)]
    assert all(not o.startswith("Refused") for o in outs), outs
    assert outs[0].startswith("You began a cellar") and outs[1].startswith("You worked on a cellar") and outs[3].startswith("You put a cellar")
    w2 = _w()
    for _ in range(3):
        _build(w2, "cellar")
    assert not _fits(w2).get("cellar") and N.decay_rate(w2, w2.s["containers"][w2.s["buildings"]["hobb_house"]["stock"]], "grain")[0] == base
    assert _fits(w).get("cellar") == 1 and N.decay_rate(w, stock, "grain")[0] < base


def test_three_beds_take_two_actions_and_a_second_start_carries_on_without_more_materials():
    w = _w()
    w.apply("set", "combe", ref=("building", "hobb_house"), field="fittings", value={k: v for k, v in _fits(w).items() if k != "beds"})
    timber = w.goods(w.s["buildings"]["hobb_house"]["stock"])["timber"]
    first = _build(w, "beds", 3)
    used = timber - w.goods(w.s["buildings"]["hobb_house"]["stock"])["timber"]
    assert first.startswith("You began 3 beds") and not _fits(w).get("beds")
    second = _build(w, "beds", 3)
    assert second.startswith("You put 3 beds") and _fits(w).get("beds") == 3
    assert timber - w.goods(w.s["buildings"]["hobb_house"]["stock"])["timber"] == used       # the carry-on took nothing more


def test_ground_is_shown_used_and_free_and_fields_by_their_plots():
    w = World(load_spec(SPEC))
    lines = PR._place_lines(Here(w, "Ivo"), Mind(w, "Ivo"))
    green = next(x for x in lines if x.startswith("- the Green ("))
    assert "built ground; 2 buildings, room for 4 more" in green
    assert any(x.startswith("- the Infield (field; 2 plots") for x in lines)
    for i in range(4):
        w.apply("raise", "combe", node="combe", parcel="cb_green", rec={"name": f"Hut {i}", "structure": "wattle", "size": 2,
                                                                      "fittings": {}, "unfinished": None})
    lines = PR._place_lines(Here(w, "Ivo"), Mind(w, "Ivo"))
    assert "built ground; 6 buildings, no room left" in next(x for x in lines if x.startswith("- the Green ("))
    w.s["today"] = R.blank_today()
    w.apply("create", "combe", dst=w.s["buildings"]["hobb_house"]["stock"], item="timber", qty=20, why="test")
    out = V.do(Here(w, "Ivo"), Mind(w, "Ivo"), {"do": "build", "what": "small room", "at": "the Green"})
    assert out == "Refused: build: there is no room left to build on the Green"
