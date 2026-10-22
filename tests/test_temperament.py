"""Temperament and values (cybertron/temperament.py; docs/review/34_temperament.md): personality.model hexaco. Legacy unchanged,
no other draw moves, the sampler reproduces its target correlations, rendering within the budget, explicit profiles, archetypes as
regions, population shifts, goal-free wording, inheritance (pairs and Makers), arrivals and the export column."""
from __future__ import annotations

import json
import math
import random
import re
import statistics
from types import SimpleNamespace

import pytest

from cybertron import generator
from cybertron import spec as S
from cybertron import temperament as T

HEX = ["shared_archive.enabled=false", "personality.model=hexaco", "personality.temperament.norms=uncorrelated"]

# A test fixture standing in for the published norms (NOT the norms): only the sampler's arithmetic is tested against it.
FIXTURE = {
    "factor_corr": [[1.0 if i == j else 0.0 for j in range(6)] for i in range(6)],
    "facet_r": {f: ({h: 0.8} if h else {"H": 0.4, "E": 0.3, "A": 0.4}) for f, h in T.FACETS.items()},
    "value_corr": [[0.5 * (i == j) + 0.5 * math.cos(2 * math.pi * (i - j) / 10) for j in range(10)] for i in range(10)],
    "factor_value_r": {"O": {"self_direction": 0.4}, "H": {"power": -0.3}},
    "pref_r": {"risk": {"fearfulness": -0.4, "prudence": -0.3}, "trust": {"H": 0.3}},
}
FIXTURE["factor_corr"][0][3] = FIXTURE["factor_corr"][3][0] = 0.3            # H-A
FIXTURE["factor_corr"][1][2] = FIXTURE["factor_corr"][2][1] = -0.2           # E-X


@pytest.fixture
def fixture_norms(monkeypatch):
    monkeypatch.setattr(T, "NORMS", FIXTURE)
    monkeypatch.setattr(T, "_MODELS", {})
    return {**T.SETTINGS, "norms": "published"}


def gen(extra=(), preset="E4", seed=1):
    return generator.generate(S.apply_overrides(S.load(preset), ["shared_archive.enabled=false", *extra]), seed)


def draws(c, n, **kw):
    rng = random.Random(7)
    return [T.draw(rng, c, **kw)["pct"] for _ in range(n)]


def pearson(xs, ys):
    return statistics.correlation(xs, ys)


# ---------------------------------------------------------------------- legacy and the other draws
def test_legacy_is_the_default_and_unchanged():
    assert T.on({}) is False
    base, legacy = gen(), gen(["personality.model=legacy"])
    strip = lambda inst: [{k: v for k, v in a.items()} for a in inst["agents"]]                # noqa: E731
    assert strip(base) == strip(legacy) and all("temperament" not in a for a in base["agents"])


def test_hexaco_moves_no_other_draw():
    base, hx = gen(), gen(HEX[1:])
    keep = ("personality", "personality_text", "archetype", "archetype_text", "temperament")
    for a, b in zip(base["agents"], hx["agents"]):
        assert {k: v for k, v in a.items() if k not in keep} == {k: v for k, v in b.items() if k not in keep}
        assert b["personality"] == {} and b["temperament"]["model"] == "hexaco" and b["personality_text"]
    assert {k: v for k, v in base.items() if k not in ("agents", "spec", "spec_source", "settings")} == \
        {k: v for k, v in hx.items() if k not in ("agents", "spec", "spec_source", "settings")}


def test_published_norms_are_refused_until_filled():
    assert T.missing_norms() == ["factor_corr", "facet_r", "value_corr"]
    with pytest.raises(ValueError, match="norms are not filled in yet.*norms: uncorrelated"):
        gen(["personality.model=hexaco"])


# ---------------------------------------------------------------------- the sampler
def test_uncorrelated_percentiles_are_uniform_and_independent():
    c = {**T.SETTINGS, "norms": "uncorrelated"}
    ps = draws(c, 4000)
    for d in ("H", "sincerity", "risk", "power"):
        xs = [p[d] for p in ps]
        assert abs(statistics.mean(xs) - 0.5) < 0.02
        shares = [sum(T.level(x) == lv for x in xs) / len(xs) for lv in range(5)]
        assert all(abs(s - 0.2) < 0.03 for s in shares)
    assert abs(pearson([p["H"] for p in ps], [p["sincerity"] for p in ps])) < 0.05


def test_the_sampler_reproduces_the_norms_correlations(fixture_norms):
    """Against a synthetic fixture: factor intercorrelations, facet-domain r, interstitial altruism, the value circumplex,
    factor-value and preference correlations, all within 0.04 over 6000 draws (correlations of normal scores)."""
    m = T.model("published")
    rng = random.Random(3)
    zs = [m.observe(m.draw_latent(rng)) for _ in range(6000)]
    col = lambda d: [z[d] for z in zs]                                                     # noqa: E731
    targets = [("H", "A", 0.3), ("E", "X", -0.2), ("H", "X", 0.0), ("sincerity", "H", 0.8), ("prudence", "C", 0.8),
               ("altruism", "H", 0.4), ("altruism", "E", 0.3), ("altruism", "A", 0.4), ("self_direction", "O", 0.4),
               ("power", "H", -0.3), ("power", "achievement", FIXTURE["value_corr"][0][1]),
               ("power", "universalism", FIXTURE["value_corr"][0][5]), ("risk", "fearfulness", -0.4),
               ("risk", "prudence", -0.3), ("trust", "H", 0.3)]
    for x, y, r in targets:
        assert abs(pearson(col(x), col(y)) - r) < 0.04, (x, y, pearson(col(x), col(y)), r)
    for d in ("sincerity", "altruism", "risk", "H", "power"):
        assert abs(statistics.pstdev(col(d)) - 1.0) < 0.04
    assert m.shrunk == 1.0


def test_population_shift_moves_the_world_and_the_levels_stay_the_references():
    c = {**T.SETTINGS, "norms": "uncorrelated", "shift": {"conformity": 1.0}, "spread": {"risk": 0.0}}
    ps = draws(c, 2000)
    assert abs(statistics.mean(p["conformity"] for p in ps) - 0.76) < 0.02          # E[Phi(Z + 1)] = Phi(1 / sqrt 2)
    assert {p["risk"] for p in ps} == {0.5}                                          # spread 0: everyone at the median


# ---------------------------------------------------------------------- rendering
def test_rendering_budget_order_and_wording():
    c = {**T.SETTINGS, "norms": "uncorrelated"}
    rng = random.Random(11)
    for i in range(400):
        prof = T.draw(rng, c, archetype=random.Random(i).choice([None, *T.REGIONS]))
        text = T.render(prof, c)
        sents = [s for s in re.split(r"(?<=\.) ", text) if s]
        assert len(sents) <= c["budget"]
        assert sum(d in T.VALUES for d in prof["shown"]) <= c["values_max"]
        assert all(T.level(prof["pct"][d]) != 2 for d in prof["shown"])
        ext = [abs(prof["pct"][d] - 0.5) for d in prof["shown"]]
        assert ext == sorted(ext, reverse=True) or any(d in T.VALUES for d in prof["shown"])
        if prof["archetype"]:
            assert text.startswith(T.REGIONS[prof["archetype"]][1].split("{")[0].split(":")[0])
    words = " ".join([s for v in T.SENTENCES.values() for s in v] + [r[1] for r in T.REGIONS.values()] + list(T.EXAMPLES.values()))
    assert not re.search(r"\b(goal|goals|payoff|score|scores)\b", words, re.I)       # goalless worlds need no rewording
    assert all(len(v) == 4 for v in T.SENTENCES.values()) and set(T.SENTENCES) == set(T.FACETS) | set(T.PREFS) | set(T.VALUES)


def test_examples_are_appended_only_at_the_extremes():
    prof = {"pct": {**{d: 0.5 for d in T.DIMENSIONS}, "trust": 0.95, "sincerity": 0.3}, "archetype": None}
    plain = T.render(dict(prof), {"examples": False})
    ex = T.render(dict(prof), {"examples": True})
    assert T.EXAMPLES["trust"] in ex and T.EXAMPLES["sincerity"] not in ex and T.EXAMPLES["trust"] not in plain


# ---------------------------------------------------------------------- explicit profiles and archetypes
def test_explicit_profiles_archetypes_and_none():
    x, y = (a["id"] for a in gen()["agents"][:2])
    inst = gen([*HEX[1:], "personality.archetypes.enabled=false",
                f"personality.explicit={{{x}: {{sincerity: 0.05, conformity: 0.97, archetype: paranoid}}, {y}: none}}"])
    a = {z["id"]: z for z in inst["agents"]}
    t = a[x]["temperament"]
    assert t["facets"]["sincerity"] == 0.05 and t["values"]["conformity"] == 0.97
    assert t["archetype"] == "paranoid" and a[x]["archetype"] == "paranoid" and "paranoid" in t["regions"]
    assert a[x]["personality_text"].startswith("You assume others are watching you")
    assert a[y]["personality_text"] == "" and a[y]["temperament"] is None


def test_natural_archetypes_name_the_region_and_leave_the_population_alone():
    nat, off = gen(HEX[1:]), gen([*HEX[1:], "personality.archetypes.enabled=false"])
    for a, b in zip(nat["agents"], off["agents"]):
        assert a["temperament"]["latent"] == b["temperament"]["latent"]                       # the same profiles either way
        t = a["temperament"]
        assert t["conditioned"] is None and (t["archetype"] is None or t["archetype"] in t["regions"])
        assert b["temperament"]["archetype"] is None
    named = [a for a in nat["agents"] if a["archetype"]]
    assert all(a["personality_text"].startswith(T.REGIONS[a["archetype"]][1].split("{")[0][:20]) for a in named)


def test_drawn_archetypes_lie_in_their_regions():
    inst = gen([*HEX[1:], "personality.archetypes.prob=1.0", "personality.temperament.archetypes=drawn"])
    archs = [a["temperament"] for a in inst["agents"] if a["temperament"]["archetype"]]
    assert len(archs) == len(inst["agents"])
    for t in archs:
        assert T.in_region(t["archetype"], T._pct_of(t)) and t["archetype"] in t["regions"]
    assert all(t["archetype"] not in ("aggressor",) for t in archs)                    # gated: conflict off in E4


def test_goalless_worlds_use_the_same_sentences():
    inst = gen([*HEX[1:], "goals.none=true"])
    assert all(not re.search(r"goal|payoff|score", a["personality_text"], re.I) for a in inst["agents"])


def test_schema_accepts_hexaco_explicit_keys_and_rejects_unknown_ones():
    from cybertron import schema as SC
    sp = S.apply_overrides(S.load("E4"), [*HEX, "personality.explicit={A01: {prudence: 0.9, archetype: zealot}}"])
    assert SC.validate(sp) == []
    bad = S.apply_overrides(S.load("E4"), [*HEX, "personality.explicit={A01: {prudense: 0.9, archetype: saint}}"])
    errs = SC.validate(bad)
    assert any("prudense" in e for e in errs) and any("saint" in e for e in errs)


# ---------------------------------------------------------------------- inheritance, arrivals, export
def _k(spec, agents, mutation=True):
    spec = {**spec, "life": {"mutation": {"enabled": mutation}}}
    return SimpleNamespace(inst={"spec": spec, "seed": 5, "agents": agents}, spec=spec)


def test_inheritance_blends_the_parents_latent():
    c = {**T.SETTINGS, "norms": "uncorrelated"}
    rng = random.Random(2)
    pa, pb = ({"temperament": T.public(T.draw(rng, c))} for _ in range(2))
    spec = {"personality": {"model": "hexaco", "temperament": {"norms": "uncorrelated"}}}
    child = T.inherit(_k(spec, [pa, pb], mutation=False), [pa, pb], "pair:G1")
    for x, v in child["latent"].items():
        lo, hi = sorted((pa["temperament"]["latent"][x], pb["temperament"]["latent"][x]))
        assert lo - 1e-3 <= v <= hi + 1e-3
    assert child == T.inherit(_k(spec, [pa, pb], mutation=False), [pa, pb], "pair:G1")    # deterministic
    one = T.inherit(_k(spec, [pa], mutation=False), [pa], "made:C1")
    assert one["latent"] == pytest.approx(pa["temperament"]["latent"], abs=1e-3)
    assert T.inherit(_k(spec, [{}]), [{}], "x") is None
    drawn = {"personality": {"model": "hexaco", "temperament": {"norms": "uncorrelated", "archetypes": "drawn"}}}
    cond = T.inherit(_k(drawn, [pa, pb]), [pa, pb], "pair:G2", archetype="paranoid")
    assert T.in_region("paranoid", cond["pct"]) and cond["conditioned"] in (None, "clamped")
    nat = T.inherit(_k(spec, [pa, pb]), [pa, pb], "pair:G2", archetype="paranoid")         # natural: not imposed
    assert nat["latent"] == cond["latent"] and nat["conditioned"] is None
    assert nat["archetype"] is None or nat["archetype"] in nat["regions"]


def test_a_pair_child_inherits_its_parents_temperament():
    import test_subsistence_reproduction as R
    inst, k = R.world(extra=HEX[1:])
    a, b = R.pair(k)
    R.conceive(k, a, b)
    ch = R.born_child(k)
    rec = {x["id"]: x for x in inst["agents"]}
    assert rec[ch]["temperament"]["model"] == "hexaco" and rec[ch]["personality"] == {} and rec[ch]["personality_text"]
    la, lb, lc = (rec[x]["temperament"]["latent"] for x in (a, b, ch))
    near = sum(min(la[x], lb[x]) - 1.5 <= lc[x] <= max(la[x], lb[x]) + 1.5 for x in lc) / len(lc)
    assert near > 0.95                                                               # a blend plus Normal(0, 0.3)


def test_an_arrival_draws_a_fresh_profile():
    from cybertron import events as EV
    from cybertron.kernel import Kernel
    inst = gen(HEX[1:])
    k = Kernel(inst)
    a = EV.draw_agent(k, inst, cls="worker")
    assert a["temperament"]["model"] == "hexaco" and a["personality"] == {} and a["personality_text"]


def test_the_export_carries_the_profile():
    from cybertron import export as X
    cols = {c.name for c in X.SCHEMA["agents"]}
    assert {"temperament_json", "personality_json"} <= cols and X.SCHEMA_MINOR >= 8
    inst = gen(HEX[1:])
    assert json.loads(json.dumps(inst["agents"][0]["temperament"]))["facets"]["sincerity"] >= 0


def test_set_temperament_reprofiles_one_seat():
    from cybertron import interventions as IV
    from cybertron.kernel import Kernel
    inst = gen(HEX[1:])
    k = Kernel(inst)
    aid = inst["agents"][0]["id"]
    before = dict(inst["agents"][0]["temperament"])
    res = IV.OPS["set_temperament"].fn(k, inst, None, aid, {"fairness": 0.02, "archetype": "opportunist"})
    t = inst["agents"][0]["temperament"]
    assert t["facets"]["fairness"] == 0.02 and t["archetype"] == "opportunist" and T.in_region("opportunist", T._pct_of(t))
    assert t["latent"] == before["latent"] and t["factors"] == before["factors"]                 # the rest kept
    assert inst["agents"][0]["personality_text"].startswith("You switch sides whenever it pays")
    assert [e[1] for e in res["inst_edits"]] == ["temperament", "personality_text", "archetype"]
    with pytest.raises(IV.InterventionError, match="unknown temperament"):
        IV.OPS["set_temperament"].fn(k, inst, None, aid, {"fairnes": 0.1})


def test_explicit_dimensions_win_over_a_kept_archetype_and_contradict_a_given_one():
    c = {**T.SETTINGS, "norms": "uncorrelated"}
    t = T.public(T.draw(random.Random(4), c, archetype="opportunist"))
    assert T.reprofile(t, {"fairness": 0.95}, c)["archetype"] is None                          # kept archetype dropped
    with pytest.raises(ValueError, match="contradicts the archetype opportunist"):
        T.reprofile(t, {"fairness": 0.95, "archetype": "opportunist"}, c)
    with pytest.raises(ValueError, match="contradicts"):
        T.draw(random.Random(1), c, {"fairness": 0.95}, "opportunist", latent=t["latent"])
