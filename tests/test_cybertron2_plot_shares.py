"""Plot shares and a crop for each holding (D2-163, D2-172; review 37_growth/02zi): claims in plots, sowing one's own then the
unclaimed plots, working another's holding by naming it (allowed, and seen), fertility kept per holding, herds trampling by plots,
inheritance in whole plots, land changing hands by an agreement's leg, and every world held whole running as it did."""
import copy
import glob
import os

import pytest

from cybertron2.engine import agreements as AG, farm as FM, herds as HD, perceive as PC, prompt as PR, run as R, things as TH
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

PEOPLE = {"Rafe": "Reed", "Rose": "Reed", "Wat": "Webb", "Col": "Cole", "Wyn": "Wynn"}


def spec(claims=(), crops=None, size=6, last="grain", fert=1.0, **extra):
    """A hamlet: the Green with a house for each household, Long Field (6 plots) and a pasture beside it."""
    field = {"name": "Long Field", "cover": "field", "size": size, "text": "the open field", "adj": ["green", "pasture"],
             "fertility": fert, "state": {"last_crop": last}}
    if crops:
        field["state"]["crops"] = crops
    s = {"name": "hamlet", "seed": 7, "days": 10, "calendar": {"season": "spring", "day": 1, "season_days": 8},
         "nodes": {"ham": {"name": "Ham", "parcels": {
             "green": {"name": "the Green", "cover": "built", "size": 3, "text": "houses round a green", "adj": ["long_field"]},
             "long_field": field,
             "pasture": {"name": "the Common", "cover": "pasture", "size": 3, "text": "rough grazing", "adj": ["long_field"]},
             "far_field": {"name": "Far Field", "cover": "field", "size": 2, "text": "a field out by the wood", "adj": ["pasture"]}}}},
         "buildings": {f"{h.lower()}_house": {"name": f"{h} House", "parcel": "green", "household": h, "structure": "wattle",
                                              "fittings": {"beds": 3, "hearth": 1, "bins": 1}, "stock": {"grain": 10}}
                       for h in ("Reed", "Webb", "Cole", "Wynn")},
         "agents": {n: {"household": h, "role": "head" if n != "Rose" else "", "holdings": {"beans": 60, "grain": 100},
                        "knows": {t: {"level": "known", "skill": 1.0} for t in ("sow", "reap", "weed", "hoe", "manure")}}
                    for n, h in PEOPLE.items()},
         "claims": [{"thing": ["parcel", "long_field"], "claimant": c, "rights": "all", "grounds": "seeded", **({"plots": n} if n else {})}
                    for c, n in claims]}
    s.update(extra)
    return s


def world(*a, **k):
    w = World(spec(*a, **k))
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def par(w):
    return w.s["parcels"]["long_field"]


def line(w, who="Rafe"):
    return next(x for x in PR._place_lines(Here(w, who)) if x.startswith("- Long Field"))


def sow_until_refused(w, who, item, **a):
    for _ in range(40):
        r = do(w, who, do="work", what="sow", at="Long Field", item=item, **a)
        if r.startswith("Refused"):
            return r
    raise AssertionError("never stopped")


# ---------------------------------------------------------------------- 1. two holdings each sow their own
def test_two_households_holding_3_and_2_plots_each_sow_their_own_and_the_line_shows_both_crops_and_the_unclaimed_plot():
    w = world(claims=[("Reed", 3), ("Webb", 2)])
    assert FM.unclaimed(par(w)) == 1 and FM.plots_of(par(w), "Reed") == 3 and FM.plots_of(par(w), "Webb") == 2
    sow_until_refused(w, "Rafe", "barley", on="the Reeds")
    sow_until_refused(w, "Wat", "beans", on="the Webbs")
    reed, webb = FM.record(par(w), "Reed")["crop"], FM.record(par(w), "Webb")["crop"]
    assert (reed["kind"], round(reed["area"], 2)) == ("barley", 3.0) and (webb["kind"], round(webb["area"], 2)) == ("beans", 2.0)
    assert par(w)["crop"] is None                                                     # the unclaimed plot lies fallow
    ln = line(w)
    assert "field; 6 plots; barley on 3 (Reeds), beans on 2 (Webbs), 1 fallow; held: Reeds 3, Webbs 2; 1 unclaimed" in ln, ln


# ---------------------------------------------------------------------- 2. one's own, then the unclaimed; another's by name
def test_sowing_past_ones_held_plots_sows_the_unclaimed_plot_then_stops_and_anothers_plots_need_on_and_are_seen():
    w = world(claims=[("Reed", 3), ("Webb", 2)])
    why = sow_until_refused(w, "Rafe", "barley")
    assert round(FM.record(par(w), "Reed")["crop"]["area"], 2) == 3.0
    assert round(par(w)["crop"]["area"], 2) == 1.0 and par(w)["crop"]["sower"] == "Rafe"       # the unclaimed plot, then it stops
    assert FM.record(par(w), "Webb")["crop"] is None
    assert '"on"' in why or "sown as thick" in why, why
    r = do(w, "Rafe", do="work", what="sow", at="Long Field", item="barley")
    assert r.startswith("Refused") and FM.record(par(w), "Webb")["crop"] is None
    r = do(w, "Rafe", do="work", what="sow", at="Long Field", item="barley", on="the Webbs")
    assert r.startswith("You sowed") and "the Webbs' plots" in r, r
    c = FM.record(par(w), "Webb")["crop"]
    assert c and c["sower"] == "Rafe"                                                  # allowed: possession (D4-23)
    e = [e for e in w.s["events"] if e["kind"] == "work" and "on the Webbs' plots" in e["text"]]
    assert e and e[-1]["actor"] == "Rafe" and "Wat" in e[-1]["concerns"]                # and seen, by the rule (concerning the Webbs)


# ---------------------------------------------------------------------- 3. reaping another's holding
def test_reaping_another_holdings_crop_gives_the_grain_to_the_reaper_and_is_noticed_by_those_working_the_field(monkeypatch):
    monkeypatch.setattr(TH, "eye_level", lambda w, name: "ordinary")
    w = world(claims=[("Reed", 3), ("Webb", 3)],
              crops=[{"holder": "Reed", "kind": "barley", "left": 120, "ripe_day": 0}, {"holder": "Webb", "kind": "barley", "left": 120, "ripe_day": 0}])
    before = w.goods(w.hands("Rafe")).get("grain", 0.0)
    webb_left = FM.record(par(w), "Webb")["crop"]["left"]
    assert do(w, "Wat", do="work", what="reap", at="Long Field").startswith("You ")          # Wat reaps his own: there today
    assert FM.record(par(w), "Reed")["crop"]["left"] == 120
    r = do(w, "Rafe", do="work", what="reap", at="Long Field", on="the Webbs")
    got = w.goods(w.hands("Rafe")).get("grain", 0.0) - before
    assert got > 0 and "on the Webbs' plots" in r, r                                 # the grain is the reaper's
    assert FM.record(par(w), "Reed")["crop"]["left"] == 120                          # his own stands untouched
    assert FM.record(par(w), "Webb")["crop"]["left"] < webb_left - got + 1e-6
    F = [f for f in PC.facts(Here(w, "Wat")) if f.get("event") and "Rafe was reaping" in f["text"]]
    assert F and "the Webbs' plots" in F[0]["text"]
    w.s["today"]["worked"]["Col"] = ["far_field"]                                      # one at work out by the wood
    w.s["today"].setdefault("route", {})["Col"] = ["far_field"]
    there, away = PC.chance_of(w, "Wat", F[0]), PC.chance_of(w, "Col", F[0])
    assert there > away > 0, (there, away)                                             # by the one rule: more to one working there
    watching = PC.chance_of(w, "Wat", F[0], "Long Field")
    assert watching > 4 * there, (watching, there)                                     # the more to one minding the field
    import random

    class Sure(random.Random):                                                         # every draw passes: the line reaches him by the rule
        def random(self):
            return 0.0
    monkeypatch.setattr(Here, "rng", lambda self, *parts: Sure(1))
    PC.evening(w, {"Wat": "Long Field"}, w.s["today"])
    t = w.s["mind"]["Wat"]["today"]
    assert any("Rafe was reaping" in x and "the Webbs' plots" in x for x in t["concerned"] + t["notice"]), t
    signs = [f["text"] for f in PC.facts(Here(w, "Col")) if f.get("sign")]
    assert any("the swish of sickles in the Webbs' barley" in x for x in signs)       # signs name the holding
    assert not any("sickles in the Reeds' barley" in x for x in signs)                 # and only the holding reaped


# ---------------------------------------------------------------------- 4. fertility by holding
def test_a_holding_sown_with_beans_after_barley_gains_fertility_while_the_next_holding_barley_twice_loses_it():
    w = world(claims=[("Reed", 3), ("Webb", 3)], fert=0.8)
    for h in ("Reed", "Webb"):
        assert FM.record(par(w), h)["fertility"] == 0.8 and FM.record(par(w), h)["last_crop"] == "grain"
    sow_until_refused(w, "Rafe", "beans", on="the Reeds")
    sow_until_refused(w, "Wat", "barley", on="the Webbs")
    for h in ("Reed", "Webb"):                                                         # both reaped to the last ear
        c = dict(FM.record(par(w), h)["crop"])
        c.update(area_left=0.0, ripe_day=w.d)
        FM.record(par(w), h)["crop"] = c
    FM.night(w)
    reed, webb = FM.record(par(w), "Reed"), FM.record(par(w), "Webb")
    assert reed["crop"] is None and webb["crop"] is None
    assert reed["fertility"] > 0.8 > webb["fertility"], (reed["fertility"], webb["fertility"])
    assert reed["last_crop"] == "legumes" and webb["last_crop"] == "grain"
    assert par(w)["fertility"] == 0.8                                                  # nobody's plots: untouched


# ---------------------------------------------------------------------- 5. a herd in the field
def test_a_herd_let_onto_the_field_tramples_the_standing_crops_in_proportion_to_their_plots():
    w = world(claims=[("Reed", 3), ("Webb", 1)],
              crops=[{"holder": "Reed", "kind": "barley", "left": 120, "ripe_day": 9}, {"holder": "Webb", "kind": "barley", "left": 40, "ripe_day": 9}],
              herds={"cattle": {"name": "the Ham cattle", "parcel": "long_field", "cows": 6}})
    rec = {"crops": [], "herds": []}
    q = HD.trample(w, "cattle", rec)
    lost = {h: (120 if h == "Reed" else 40) - FM.record(par(w), h)["crop"]["left"] for h in ("Reed", "Webb")}
    assert q > 0 and abs(lost["Reed"] + lost["Webb"] - q) < 1e-3
    assert abs(lost["Reed"] / lost["Webb"] - 3.0) < 0.01, lost                       # 3 plots to 1
    assert all(FM.record(par(w), h)["crop"]["trampled"]["by"] == "cattle" for h in ("Reed", "Webb"))
    assert w.s["herds"]["cattle"]["ate"]["q"] == q


# ---------------------------------------------------------------------- 6. partible inheritance in whole plots
def _family(heirs):
    s = spec(claims=[], crops=None)
    s["agents"]["Old"] = {"household": "Reed", "born": -400, "stage": "elder", "holdings": {}}
    for i in range(heirs):
        s["agents"][f"Kid{i + 1}"] = {"household": "Reed", "born": -200 + i * 10, "parents": ["Old"]}
    s["agents"]["Rafe"]["role"] = "head"
    s["households"] = {"Reed": {"name": "the Reeds", "head": "Rafe", "rules": {"inheritance": "partible"}}}
    s["claims"] = [{"thing": ["parcel", "long_field"], "claimant": "Old", "rights": "all", "grounds": "seeded", "plots": 5}]
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def test_partible_inheritance_of_5_plots_gives_3_and_2_to_two_heirs_and_to_six_five_single_plots_one_held_jointly():
    w = _family(2)
    FM.record(par(w), "Old")["crop"] = FM.normalise_crop({**par(w), "size": 5}, {"kind": "barley", "left": 100, "ripe_day": 9}, 0, 8)
    w.apply("die", "ham", person="Old", cause="old age")
    held = {c["claimant"]: c.get("plots") for c in w.claims_on(("parcel", "long_field"))}
    assert held == {"Kid1": 3, "Kid2": 2}, held                                        # whole plots, eldest first
    assert FM.record(par(w), "Old") is None
    assert [round(FM.record(par(w), k)["crop"]["left"], 1) for k in ("Kid1", "Kid2")] == [60.0, 40.0]   # the crop goes with the plots
    w = _family(6)
    w.apply("die", "ham", person="Old", cause="old age")
    cl = w.claims_on(("parcel", "long_field"))
    single = sorted(c["claimant"] for c in cl if not c.get("joint"))
    joint = [c for c in cl if c.get("joint")]
    assert single == ["Kid1", "Kid2", "Kid3", "Kid4"] and all(c["plots"] == 1 for c in cl)
    assert len(joint) == 1 and joint[0]["joint"] == ["Kid5", "Kid6"] and joint[0]["plots"] == 1   # five plots; the fifth held jointly
    assert sum(c["plots"] for c in cl) == 5 and FM.unclaimed(par(w)) == 1
    assert "withdrawal" in w.rights("Kid6", ("parcel", "long_field"))                  # a co-heir holds it too
    assert FM.record(par(w), "Kid1")["fertility"] == 1.0


# ---------------------------------------------------------------------- 7. land changes hands by an agreement
def test_an_offer_leg_of_2_plots_of_long_field_accepted_moves_the_claim_and_the_line_shows_the_new_holders():
    w = world(claims=[("Reed", 3), ("Webb", 2)])
    FM.record(par(w), "Reed")["fertility"], FM.record(par(w), "Webb")["fertility"] = 1.3, 0.9
    assert AG.parse_legs("2 plots of Long Field", 0)[0]["plots"] == 2
    line_ = AG.make_offer(Here(w, "Rafe"), Mind(w, "Rafe"), {"to": "Wat", "give": "2 plots of Long Field", "get": "10 grain", "for": "my household"})
    assert line_.startswith("You offered"), line_
    oid = line_.split()[2].rstrip(":")
    r = do(w, "Wat", do="accept", offer=oid, **{"for": "my household"})
    assert r.startswith("You accepted") and "2 plots of Long Field" in r, r
    assert FM.holdings(w.claims_on(("parcel", "long_field")), 6) == {"Reed": 1, "Webb": 4}
    assert FM.record(par(w), "Webb")["fertility"] == 1.1                              # the soil goes with the plots
    assert "held: Reeds 1, Webbs 4; 1 unclaimed" in line(w), line(w)
    with pytest.raises(Exception, match="may not part"):                              # a member may not sell the household's land
        AG.make_offer(Here(w, "Rose"), Mind(w, "Rose"), {"to": "Wat", "give": "1 plot of Long Field", "get": "1 grain", "for": "my household"})


# ---------------------------------------------------------------------- 8. worlds held whole run as they did
WORLDS = sorted(glob.glob("cybertron2/specs/*.yaml") + glob.glob("cybertron2/specs/ladder/*.yaml"))


def _runnable(path):
    s = load_spec(path)
    fields = [p for n in s.get("nodes", {}).values() for p in (n.get("parcels") or {}).values() if p.get("cover") == "field"]
    return s if "agents" in s and fields else None


@pytest.mark.parametrize("path", [p for p in WORLDS if _runnable(p)], ids=os.path.basename)
def test_every_world_held_whole_loads_with_its_fields_as_before(path):
    """A whole claim is all the plots: the field's own record is its holders' (crop and soil where they always were), with no part
    holdings and nothing unclaimed; the seeded crop stands on the parcel as before."""
    s = _runnable(path)
    w = World(copy.deepcopy(s))
    for nd in s["nodes"].values():
        for pid, p in (nd.get("parcels") or {}).items():
            if p.get("cover") != "field":
                continue
            par_ = w.s["parcels"][pid]
            whole = [c["claimant"] for c in w.claims_on(("parcel", pid)) if c.get("plots") is None and c["grounds"] != "granted"]
            assert FM.shares(par_) == [] and FM.whole(par_) == list(dict.fromkeys(whole))
            assert FM.plots_of(par_, None) == par_["size"] and FM.unclaimed(par_) == (0 if whole else par_["size"])
            if (p.get("state") or {}).get("crop"):
                assert par_["crop"] and par_["crop"]["kind"] == p["state"]["crop"]["kind"]
            assert not FM.named(par_)


@pytest.mark.parametrize("path", ["cybertron2/specs/valley_s5.yaml", "cybertron2/specs/hollins_s7.yaml"], ids=os.path.basename)
def test_a_world_held_whole_runs_and_replays_with_its_fields_kept_whole(path, tmp_path):
    R.run(path, tmp_path / "r", days=4, bots=True)
    import json
    st = json.loads((tmp_path / "r" / "state.json").read_text())
    for pid, p in st["parcels"].items():
        if p["cover"] == "field":
            assert not p.get("shares"), pid                                            # nothing held in part, as before
    rep = R.run(None, tmp_path / "r", mode="replay")
    assert rep["mismatches"] == []
