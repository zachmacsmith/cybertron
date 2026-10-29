"""Package D (37.2's brief 02w §2): partners, trying and conception, pregnancy, birth, infants and children, coming of age, old
age, succession (spec/life/birth_and_death.md: D2-138 to D2-153)."""
import copy

import pytest

from cybertron2.engine import generate as G, life as LF, night as N, run as R
from cybertron2.engine import verbs as V
from cybertron2.engine.data import LIFE
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = load_spec("cybertron2/specs/valley_s5.yaml")
COUPLES = [("Rohese", "Warin"), ("Sibyl", "Edric"), ("Edith", "Simkin")]


def world(seed=None, **patch):
    s = copy.deepcopy(SPEC)
    s["children"] = {"on": True, "dial": "low"}
    if seed is not None:
        s["seed"] = seed
    s.update(patch)
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def home(w, who):
    return next(b for b in w.homes(who) if w.s["buildings"][b]["node"] == w.at(who))


class Fixed:
    def __init__(self, x):
        self.x = x

    def random(self):
        return self.x

    def choice(self, seq):
        return sorted(seq)[0]


def fix_rng(monkeypatch, w, x, kinds=None):
    real = w.rng
    monkeypatch.setattr(w, "rng", lambda *parts: Fixed(x) if kinds is None or parts[0] in kinds else real(*parts))


def night_life(w, missed=(), where=None):
    rec = {"missed": list(missed)}
    where = where or {n: (home(w, n) if w.homes(n) and w.at(n) else None) for n in w.living()}
    return LF.night(w, w.s["today"], rec, where)


def next_day(w):
    w.s["day"] += 1
    w.s["events"] = []
    w.s["today"] = R.blank_today()
    R.dawn(w)


# ---------------------------------------------------------------------- trying (D2-138, D2-146, D2-152)
def test_no_conception_unless_both_try_and_same_sex_or_pregnant_refused(monkeypatch):
    w = world()
    f, m = COUPLES[0]
    assert w.at(f) == w.at(m)
    fix_rng(monkeypatch, w, 0.0, {"conceive"})
    assert do(w, f, do="try", **{"with": m, "units": 2}).startswith("You spent 2 units")
    night_life(w)
    assert w.s["people"][f]["pregnant"] is None                                  # only one of them tried
    w.s["today"] = R.blank_today()
    do(w, f, do="try", **{"with": m, "units": 1})
    do(w, m, do="try", **{"with": f, "units": 1})
    night_life(w)
    assert w.s["people"][f]["pregnant"] == w.d
    other = next(n for n in w.present(w.at(m)) if n != m and w.s["people"][n]["sex"] == "m" and w.s["people"][n]["stage"] == "adult"
                 ) if any(n != m and w.s["people"][n]["sex"] == "m" and w.s["people"][n]["stage"] == "adult" for n in w.present(w.at(m))) else None
    if other:
        assert do(w, m, do="try", **{"with": other}).startswith("Refused")       # same sex
    w.s["day"] += 1                                                                # her pregnancy shows: refused
    assert do(w, m, do="try", **{"with": f}).startswith("Refused")
    w.s["people"][f].update(pregnant=None, gap_until=w.d + 2)
    assert do(w, f, do="try", **{"with": m}).startswith("Refused")               # in the gap after a birth


def test_children_off_has_no_try():
    w = world(children={"on": False})
    f, m = COUPLES[0]
    assert do(w, f, do="try", **{"with": m}).startswith("Refused")


def test_the_chance_a_night_matches_the_formula_and_hungry_or_apart_none(monkeypatch):
    for u, p in ((1, 0.315), (2, 0.506), (3, 0.622), (6, 0.760)):                # D2-162
        assert abs(LF.chance(u) - p) < 0.002
    f, m = COUPLES[0]
    for case in ("hungry", "apart"):
        w = world()
        fix_rng(monkeypatch, w, 0.0, {"conceive"})
        do(w, f, do="try", **{"with": m, "units": 3})
        do(w, m, do="try", **{"with": f, "units": 3})
        where = {n: home(w, n) for n in (f, m)}
        if case == "apart":
            where[m] = None
        night_life(w, missed=[m] if case == "hungry" else [], where=where)
        assert w.s["people"][f]["pregnant"] is None
    w = world()                                                                  # the units: the lesser of the two
    rates = []
    for u in (1, 3):
        hits = 0
        for k in range(400):
            w.s["day"] = k
            w.s["people"][f].update(pregnant=None, gap_until=None)
            w.s["today"] = R.blank_today()
            do(w, f, do="try", **{"with": m, "units": u})
            do(w, m, do="try", **{"with": f, "units": u})
            LF._conceive(w, w.s["today"], {"missed": []}, {f: "x", m: "x"}, {"conceived": []})
            hits += w.s["people"][f]["pregnant"] is not None
        rates.append(hits / 400)
    assert abs(rates[0] - LF.chance(1)) < 0.06 and abs(rates[1] - LF.chance(3)) < 0.07


# ---------------------------------------------------------------------- pregnancy and birth (D2-141, D2-147)
def test_pregnancy_food_units_birth_on_the_second_night_and_the_gap(monkeypatch):
    """D2-162: 2 days, the last one a unit lighter; refused while pregnant and for 1 day after the birth."""
    w = world()
    f, m = COUPLES[0]
    w.s["people"][f].update(pregnant=0, father=m)
    assert LF.ration_factor(w, f) == (1.0, 0.3)
    pen, shows = [], []
    for d in range(1, 3):
        w.s["day"] = d
        pen.append(LF.unit_penalty(w, f))
        shows.append(LF.showing(w, f))
        assert do(w, f, do="try", **{"with": m}).startswith("Refused")           # with child
    assert pen == [0, 1] and shows == [True, True]                              # its last day; signs from the day after
    fix_rng(monkeypatch, w, 0.99, {"birth", "born", "young"})
    w.s["day"] = 1
    night_life(w)
    assert w.s["people"][f]["pregnant"] == 0                                    # not yet
    w.s["day"] = 2
    out = night_life(w)
    assert len(out["births"]) == 1 and w.s["people"][f]["pregnant"] is None
    baby = out["births"][0]["child"]
    b = w.s["people"][baby]
    assert b["stage"] == "infant" and b["parents"] == [f, m] and w.household_of(baby) == w.household_of(f) and w.at(baby) == w.at(f)
    assert w.s["people"][f]["relations"][baby].startswith("your ") and baby in w.s["mind"][m]["kin"]
    assert baby not in w.agents_acting()
    w.s["day"] = 3
    assert do(w, f, do="try", **{"with": m}).startswith("Refused")               # the gap: 1 day
    w.s["day"] = 4
    assert do(w, f, do="try", **{"with": m}).startswith("You spent")


def test_birth_risks_halve_with_another_adult_and_are_worse_out(monkeypatch):
    def mother_dies(x, helped, housed=True):
        w = world()
        f, m = COUPLES[0]
        w.s["day"] = 5
        w.s["people"][f].update(pregnant=0, father=m)
        where = {n: "elsewhere" for n in w.living()}
        where[f] = home(w, f) if housed else None
        if helped:
            where[m] = where[f]
        fix_rng(monkeypatch, w, x, {"birth"})
        LF._birth(w, f, where, {"missed": []}, {"births": [], "deaths": []})
        return not w.s["people"][f]["alive"]
    assert mother_dies(0.015, helped=False) and not mother_dies(0.015, helped=True)     # 0.02 against 0.01
    assert mother_dies(0.05, helped=False, housed=False) and not mother_dies(0.05, helped=False)   # out: 0.06


# ---------------------------------------------------------------------- infants and children (D2-142, D2-145, D2-150)
def _infant(w, mother="Rohese"):
    w.s["people"][mother].update(pregnant=w.d - 5)
    out = {"births": [], "deaths": []}
    import random
    real = w.rng
    w.rng = lambda *p: Fixed(0.99) if p[0] == "birth" else real(*p)
    LF._birth(w, mother, {mother: home(w, mother)}, {"missed": []}, out)
    w.rng = real
    return out["births"][0]["child"]


def test_an_uncared_infant_dies_at_four_times_and_hunger_and_cold_double_it(monkeypatch):
    w = world()
    baby = _infant(w)
    w.s["day"] += 1
    where = {baby: home(w, "Rohese")}

    def dies(x, care, missed=(), cold=False):
        w.s["people"][baby].update(alive=True)
        w.s["today"] = R.blank_today()
        if care:
            w.s["today"]["care"] = {baby: 1}
        monkeypatch.setattr(w, "cold", lambda day=None: cold)
        fix_rng(monkeypatch, w, x, {"young"})
        LF._young(w, w.s["today"], {"missed": list(missed)}, where, {"deaths": []})
        return not w.s["people"][baby]["alive"]
    assert dies(0.05, care=False) and not dies(0.05, care=True)                  # 0.08 against 0.02
    assert dies(0.03, care=True, missed=[baby]) and not dies(0.03, care=True)    # hungry: x2
    assert dies(0.03, care=True, cold=True)                                      # a cold night without a fire: x2


def test_care_by_work_and_the_dial(monkeypatch):
    w = world()
    baby = _infant(w)
    assert do(w, "Warin", do="work", what="care", at=baby).startswith("You looked after")
    assert w.s["today"]["care"][baby] == 1 and "Warin" in w.s["today"]["care_by"][baby]
    assert LF.ration_factor(w, baby) == (0.5, 0.0)
    w.s["people"][baby]["stage"] = "child"
    assert LF.ration_factor(w, baby)[0] == 0.7 and LF.dial(w)["child_works"] == 1.0
    hi = world(children={"on": True, "dial": "high"})
    assert LF.dial(hi)["infant_care"] == 3 and LF.ration_factor(hi, "Piers")[0] == 1.0


def test_a_child_does_the_heads_standing_order():
    w = world()
    head = w.head(w.household_of("Piers"))
    assert do(w, head, do="order", what="forage").startswith("Your household's children will")
    assert do(w, "Piers", do="order", what="forage").startswith("Refused") if "Piers" in w.agents_acting() else True
    got = LF.children_work(w)
    assert "Piers" in got and not got["Piers"].startswith("Refused: work") and not got["Piers"].startswith("Refused: gather: you")


# ---------------------------------------------------------------------- coming of age (D4-20, D2-144)
def test_a_child_becomes_a_youth_agent_after_six_days_with_memories(monkeypatch):
    w = world()
    baby = _infant(w)
    w.s["today"]["care_by"] = {baby: ["Warin"]}
    w.event(w.at(baby), "death", "Odo died in the night", salience=1.0, tags=["death"])
    LF._childhood(w, w.s["today"], {"missed": []})
    born = w.s["people"][baby]["born"]
    for d in range(born + 1, born + 6):
        w.s["day"] = d
        LF.dawn(w)
        assert baby not in w.agents_acting()
    w.s["day"] = born + 6
    LF.dawn(w)
    a = w.s["people"][baby]
    assert a["stage"] == "youth" and baby in w.agents_acting() and a["model"]
    lasting = " ".join(w.s["mind"][baby]["lasting"])
    assert "Warin looked after you" in lasting and "Odo died" in lasting


# ---------------------------------------------------------------------- days everywhere (D2-139, D2-153)
def test_the_stages_follow_days_since_birth_and_scale_with_the_lifespan():
    assert LF.spans() == [("infant", 2), ("child", 4), ("youth", 6), ("adult", 20)]
    assert LF.spans(16) == [("infant", 1), ("child", 2), ("youth", 3), ("adult", 10)]
    w = world(agents={**SPEC["agents"], "Piers": {**SPEC["agents"]["Piers"], "born": -7}})
    assert w.s["people"]["Piers"]["stage"] == "youth"
    w.s["day"] = 6
    LF.dawn(w)
    assert w.s["people"]["Piers"]["stage"] == "adult"


def test_a_generated_world_is_dated_in_days():
    base = load_spec("cybertron2/specs/valley.yaml") if __import__("os").path.exists("cybertron2/specs/valley.yaml") else None
    if base is None:
        pytest.skip("no valley base")
    spec = G.build(copy.deepcopy(base), 5)
    for n, a in spec["agents"].items():
        assert isinstance(a["born"], int) and a["born"] <= 0
        assert LF.stage_of(-a["born"], LF.lifespan()) == a["stage"]
    assert not any("age" in a for a in spec["agents"].values())


# ---------------------------------------------------------------------- old age and succession (D2-143, D2-149)
def test_old_age_rises_with_days_into_old_age(monkeypatch):
    w = world()
    w.s["people"]["Odo"]["born"] = -32 - 40                                      # 40 days into old age: 0.01 x 4
    fix_rng(monkeypatch, w, 0.035, {"old-age"})
    out = {"old_age": []}
    LF._old_age(w, out)
    assert "Odo" in out["old_age"]


def test_succession_heir_else_most_named_else_eldest():
    w = world()
    hh = w.household_of("Edric")
    head = w.head(hh)
    heir = next(x for x in w.members(hh) if x != head and w.s["people"][x]["stage"] == "adult")
    assert do(w, head, do="name", heir=heir).startswith("You named")
    w.apply("die", w.at(head), person=head, cause="old age")
    assert w.head(hh) == heir
    w2 = world()
    head = w2.head(hh)
    w2.apply("die", w2.at(head), person=head, cause="old age")
    sc = w2.s["institutions"][hh]["succession"]
    assert sc and w2.head(hh) is not None                                          # the eldest for now
    grown = [x for x in w2.members(hh) if w2.s["people"][x]["alive"] and w2.s["people"][x]["stage"] in ("adult", "elder")]
    pick = sorted(grown)[-1]
    for x in grown:
        assert do(w2, x, do="name", head=pick).startswith("You named")
    w2.s["day"] = sc["until"]
    LF.dawn(w2)
    assert w2.head(hh) == pick and not w2.s["institutions"][hh].get("succession")


# ---------------------------------------------------------------------- the whole: births near 02ze's
def _births_a_woman(share, seeds=24):
    """Births to each woman over an adult span at the default lifespan, the couple trying (1 unit each) on `share` of the nights."""
    import random
    adult = dict(LF.spans(LIFE["lifespan"]))["adult"]
    births, n = 0, 0
    for seed in range(seeds):
        w, pick = world(seed=seed), random.Random(seed)
        for d in range(adult):
            w.s["day"] = d
            w.s["today"] = R.blank_today()
            LF.dawn(w)
            for f, m in COUPLES:
                if pick.random() < share:
                    for a, b in ((f, m), (m, f)):
                        do(w, a, do="try", **{"with": b, "units": 1})
            out = {"conceived": [], "lost": [], "births": [], "deaths": [], "old_age": []}
            LF._conceive(w, w.s["today"], {"missed": []}, {x: "same" for x in w.living()}, out)
            for x in w.living():                                                    # births, without the risks
                a = w.s["people"][x]
                if a.get("pregnant") is not None and d - a["pregnant"] >= LF.pregnancy_days(w):
                    a["pregnant"], a["gap_until"] = None, d + 1 + LIFE["gap"]
                    births += 1
        n += len(COUPLES)
    return births / n


def test_couples_who_try_have_births_near_the_model():
    """D2-162 (02ze): about 3.0 births a woman trying every night, about 1.96 trying half the nights."""
    assert 2.7 <= _births_a_woman(1.0) <= 3.3
    assert 1.65 <= _births_a_woman(0.5) <= 2.25


def test_nothing_is_paid_to_the_dead():
    from cybertron2.engine import agreements as AG
    w = world()
    a, b = "Warin", "Edric"
    w.s["containers"][w.hands(a)]["goods"]["grain"] = 5.0
    w.apply("agree", w.at(a), node=w.at(a), rec={"parties": [a, b], "legs": [{"from": a, "to": b, "item": "grain", "qty": 2, "when": {"by": 0}, "paid": 0, "arrears": 0}]})
    w.s["people"][b]["at"] = w.at(a)
    w.apply("die", w.at(b), person=b, cause="old age")
    AG.settle(w)
    assert w.goods(w.hands(a))["grain"] == 5.0


def test_the_mother_and_father_are_told_of_a_birth_and_a_mother_of_a_loss():
    """Seen in w1: Lucy was never told she had given birth and went on believing she was with child (review 38.36)."""
    import copy as _copy
    from cybertron2.engine import run as _R
    from cybertron2.engine.world import World as _World, load_spec as _load
    w = _World(_copy.deepcopy(_load("cybertron2/specs/wide_s7.yaml")))
    w.s["today"] = _R.blank_today()
    mother = next(n for n, a in w.s["people"].items() if a["sex"] == "f" and a["stage"] == "adult" and a.get("partner"))
    father = w.s["people"][mother]["partner"]
    child = w.apply("born", w.at(mother), mother=mother, father=father)
    rec = {"missed": [], "short": [], "ate": {}, "cold_falls": [], "deaths": [], "hearth": {}, "breaks": [],
           "life": {"births": [{"mother": mother, "child": child}], "lost": [mother]}}
    lines = _R.night_lines(w, rec)
    assert any(f"you gave birth to" in x and child in x for x in lines[mother])
    assert any(f"{mother} gave birth to your" in x for x in lines[father])
    assert "You lost the child you were carrying." in lines[mother]
