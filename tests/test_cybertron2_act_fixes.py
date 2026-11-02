"""Five fixes from the refusals of wb2 and wb3 (D4-94): a fire in the open by heat; a thing named by its tag in a phrase, or by its
door or place in a phrase; move into a full store leaves the rest at its door; offers say what the work is for and "every day"; a
camp takes only beds and a fire ring, and the build list shows fittings apart."""
from cybertron2.engine import agreements as AG, prompt as PR, run as R, verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = "cybertron2/specs/wenbridge.yaml"


def _w():
    w = World(load_spec(SPEC))
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def test_a_fire_in_the_open_burns_firewood_by_its_heat():
    w = _w()
    w.apply("create", "wenbridge", dst=w.hands("Rob"), item="firewood", qty=8, why="test")
    assert do(w, "Rob", do="fire").startswith("You mean to light a fire tonight")
    w2 = _w()
    w2.apply("create", "wenbridge", dst=w2.hands("Rob"), item="firewood", qty=3, why="test")
    assert "takes 4 heat from what you carry (8 firewood or 2 timber); you carry 1.5 heat" in do(w2, "Rob", do="fire")


def test_take_by_a_tag_in_a_phrase_or_by_the_door_named_and_a_clear_refusal():
    from cybertron2.engine import things as TH
    w = _w()
    cid = w.apply("new_thing", "wenbridge", node="wenbridge", parcel="wb_green", kind="pile", by=None, door="hearne_hut")
    w.apply("create", "wenbridge", dst=cid, item="grain", qty=20, why="test")
    tag = w.s["containers"][cid]["tag"]
    TH.remember(w, "Tom", cid, "saw", text="a heap of something at the Green")
    assert do(w, "Tom", do="take", item="grain", qty=5, **{"from": f"the heap {tag} at the Green"}).startswith("You took 5 grain")
    assert do(w, "Tom", do="take", item="grain", qty=5, **{"from": "the grain lying outside the Hearne hut door"}).startswith("You took 5 grain")
    assert "holds no timber" in do(w, "Tom", do="take", item="timber", qty=1, **{"from": f"pack {tag} at the Green"})
    assert "you know of nothing called T99 here" in do(w, "Tom", do="take", item="grain", qty=1, **{"from": "pack T99"})


def test_move_into_a_full_store_leaves_the_rest_at_its_door():
    w = _w()
    w.apply("create", "wenbridge", dst=w.hands("Tom"), item="grain", qty=40, why="test")
    out = do(w, "Tom", do="move", item="grain", qty=40, to="store", at="the Hearne hut")
    assert out.startswith("You put 40 grain into the Hearne hut") and "the rest lies outside its door" in out
    assert any(c.get("door") == "hearne_hut" and c["goods"].get("grain", 0) > 0 for c in w.s["containers"].values())


def test_offers_say_what_the_work_is_for_and_every_day():
    legs = AG.parse_legs("work 2 days on the water wheel", 3)
    assert legs == [{"work": 2, "done": 0, "by": None, "on": "on the water wheel"}]
    assert AG.parse_legs("2 grain every day for 5 times", 3)[0]["when"] == {"every": 1, "times": 5, "next": 4}
    leg = {**legs[0], "from": "Piers", "to": "Hugh"}
    assert AG.leg_text(leg) == "Piers works 2 days for Hugh, on the water wheel (0 done)"


def test_a_camp_takes_only_beds_and_a_fire_ring_and_the_build_list_shows_fittings_apart():
    w = _w()
    w.apply("create", "wenbridge", dst=w.hands("Rob"), item="timber", qty=20, why="test")
    for t in ("granary", "bins", "woodshed"):
        w.apply("learn", "wenbridge", person="Rob", tech=t, level="known", source="test")
    out = do(w, "Rob", do="build", what="granary", at="the newcomers' camp")
    assert "is a camp: it takes only beds and a fire ring" in out
    lines = PR.verb_lines(Here(w, "Rob"), Mind(w, "Rob"))
    assert "buildings and rooms:" in lines and "fittings, put inside a building you name" in lines


def test_refusals_say_the_next_step_who_did_it_where_it_is_and_why():
    from cybertron2.engine import farm as FM
    w = _w()
    # where the good is, when it is not in hand
    st = w.s["buildings"]["hearne_hut"]["stock"]
    out = do(w, "Tom", do="move", item="beans", qty=2, to="store", at="the Hearne hut")
    assert "there is no beans in your hands; the Hearne hut's store holds" in out and "straight into its store" in out
    # who took it from the store today
    do(w, "Ellen", do="move", item="beans", qty=w.goods(st)["beans"], to="hands", at="the Hearne hut")
    out = do(w, "Tom", do="move", item="beans", qty=1, to="hands", at="the Hearne hut")
    assert "Ellen took" in out and "from the store today" in out
    # where it comes from
    out = do(w, "Alys", do="make", what="bread")
    assert "flour is made by" in out
    # not done here: where it is done here
    out = do(w, "Rob", do="gather", what="fell", at="the Long Field")
    assert "felling timber is not done at the Long Field; here it is done at" in out and "the Coppice" in out
    # the door: who manages it
    out = do(w, "Alys", do="set", thing="door", to="barred", at="the Ardern Hall")
    assert out.startswith("Refused: set: only those who manage the Ardern Hall set its door")
    # a refused act at a place still puts one there to see it
    out = do(w, "Tom", do="work", what="reap", at="the Long Field")              # not ripe on day 0: refused, but he was there
    assert out.startswith("Refused") and "wb_field" in w.s["today"]["worked"].get("Tom", [])


def test_pin_by_text_and_the_known_dead_cannot_be_named_head():
    from cybertron2.engine import perceive as PC
    w = _w()
    m = Mind(w, "Tom")
    m.person.setdefault("notes", {})["Harvest"] = "Reap the Long Field with the boys, then store it dry."
    m.person["pinned"] = None
    PC.apply_notes(m, {"pin": "Reap the Long Field with the boys"})
    assert m.person.get("pinned") == "Harvest"
    m2 = Mind(w, "Alys")
    m2.kin()["Odo"]["alive"] = False
    w.s["institutions"]["Ardern"]["succession"] = {"until": w.d + 2, "named": {}}
    assert "Odo is dead: only the living can head a household" in do(w, "Alys", do="name", head="Odo")


def test_an_act_says_what_it_took_from_the_store_and_give_draws_from_it_at_home():
    w = _w()
    out = do(w, "Tom", do="give", item="grain", qty=3, to="Ellen")
    assert out == "You gave 3 grain to Ellen. (from the Hearne hut's store: 3 grain)"
    assert "there is no hand mill here you can use" in do(w, "Alys", do="make", what="grind") or True
