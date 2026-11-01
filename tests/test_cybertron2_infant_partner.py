"""A baby sleeps where its mother sleeps; a partner's death far away does not show in one's partner line till it is learned."""
from cybertron2.engine import night as N, prompt as PR, run as R
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = "cybertron2/specs/wenbridge.yaml"


def _w():
    spec = load_spec(SPEC)
    spec["agents"]["Nell"] = {"household": "Newcome", "stage": "infant", "sex": "f", "model": "bot", "parents": ["Rob", "Mary"]}
    w = World(spec)
    w.s["today"] = R.blank_today()
    return w


def test_a_baby_sleeps_where_its_mother_sleeps():
    w = _w()
    today = R.blank_today()
    where = N.sleeping_places(w, today)
    assert where["Nell"] == where["Mary"] == "new_camp"
    today = R.blank_today()
    today["travel"] = {"Mary": "holm"}                                          # she sleeps out: so does the baby, beside her
    where = N.sleeping_places(w, today)
    assert where["Mary"] is None and where["Nell"] is None


def test_the_partner_line_keeps_a_partner_whose_death_is_not_yet_known():
    w = _w()
    w.apply("die", "wenbridge", person="Rob", cause="cold")                     # nothing yet perceived of it
    assert w.s["people"]["Mary"]["partner"] is None                              # free to partner again (D2-140)
    lines = PR._family_lines(Here(w, "Mary"), Mind(w, "Mary"))
    assert "Your partner: Rob." in lines
    Mind(w, "Mary").kin()["Rob"]["alive"] = False                                # once she has learned it
    assert not any(x.startswith("Your partner") for x in PR._family_lines(Here(w, "Mary"), Mind(w, "Mary")))
