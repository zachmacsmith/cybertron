"""Package A (37.2's brief 02r §3): the day's weather and visibility, things at a spot and the noticing rule, give to a place and
hiding, burying, decay by condition, fuse events (D2-80 to D2-103, D2-111)."""
import copy

from cybertron2.engine import environment as EV, fuse as FU, night as N, perceive as PC, prompt as PR, run as R, things as TH
from cybertron2.engine import verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import World, load_spec

SPEC = load_spec("cybertron2/specs/valley_s5.yaml")


def world(**patch):
    s = copy.deepcopy(SPEC)
    s.update(patch)
    w = World(s)
    w.s["today"] = R.blank_today()
    return w


def do(w, who, **a):
    return V.do(Here(w, who), Mind(w, who), a)


def give(w, who, **goods):
    w.s["containers"][w.hands(who)]["goods"].update({k.replace("_", " "): float(v) for k, v in goods.items()})


# ---------------------------------------------------------------------- the day's weather and visibility (D2-99, D2-103)
def test_the_days_weather_repeats_for_a_seed_differs_by_day_and_snow_lies_until_three_thaw_days():
    a, b = world(), world()
    days = [EV.weather(a, d) for d in range(40)]
    assert days == [EV.weather(b, d) for d in range(40)]
    assert len(set(days)) > 1
    w = world(weather={2: "snow"}, cold_days=[1, 2, 3])
    w.cold_days = {1, 2, 3}
    assert EV.snow_lying(w, 2) and EV.snow_lying(w, 3)                  # frost on day 3: no thaw yet
    assert EV.snow_lying(w, 5) and not EV.snow_lying(w, 6)              # thaw days 4, 5, 6: gone on the third


def test_sight_in_fog_in_woodland_and_at_night_only_for_night_events():
    w = world(weather={1: "fog"})
    assert abs(EV.visibility(w, "millbrook", "alder_copse", "sight") - 0.35 * 0.3) < 1e-9
    assert abs(EV.visibility(w, "millbrook", "alder_copse", "sight", night=True) - 0.35 * 0.3 * 0.1) < 1e-9
    w2 = world(weather={1: "clear"})
    assert EV.visibility(w2, "millbrook", "long_field", "sound", night=True, quiet=False) == 1.2


# ---------------------------------------------------------------------- things at a spot and noticing (D2-85, D2-102)
def _body(w, parcel, who="Odo"):
    w.s["seq"] += 1
    cid = f"remains:{w.s['seq']}"
    w.s["containers"][cid] = {"kind": "remains", "of": who, "node": "millbrook", "parcel": parcel, "goods": {}, "wear": {}, "body": True,
                              "died": w.d}
    return cid


def test_a_body_in_the_open_is_seen_by_one_working_there_far_more_than_one_in_the_wood():
    w = world(weather={1: "clear"})
    assert do(w, "Edric", do="work", what="weed", at="Long Field").startswith("You weeded")
    open_ = TH.chance(w, "Edric", w.s["containers"][_body(w, "long_field")])
    wood = TH.chance(w, "Edric", w.s["containers"][_body(w, "alder_copse")])
    assert open_ > 5 * wood                                                       # (the barley standing high halves the field's sight)


def test_hiding_untaught_is_twice_as_easy_to_see_and_a_buried_pack_is_almost_never_seen():
    w = world(weather={1: "clear"})
    give(w, "Edric", grain=4, coin=10)
    assert "not as well hidden" in do(w, "Edric", do="give", item="grain", qty=4, to="Alder Copse", hidden="under brush")
    pile = next(c for c in w.s["containers"].values() if c["kind"] == "pile")
    assert pile["untaught"] and abs(TH.own(w, pile) - 0.4 * 0.4) < 1e-9          # untaught x0.4, not x0.2
    do(w, "Edric", do="give", item="coin", qty=10, to="Alder Copse", hidden="buried")
    cache = [c for c in w.s["containers"].values() if c["kind"] == "pile" and c.get("hidden") == "buried"][0]
    assert TH.chance(w, "Sibyl", cache) < 0.01
    assert do(w, "Edric", do="hide", item="grain", qty=1, to="Alder Copse").startswith("Refused")      # nothing left to hide


def test_give_to_someone_not_here_is_left_at_their_door_and_a_passer_by_can_take_it():
    w = world()
    give(w, "Edric", grain=5)
    out = do(w, "Edric", do="give", to="Elena", item="grain", qty=5)            # Elena lives at Coppergate, not here
    assert out.startswith("Refused")
    w.s["people"]["Hamo"]["at"] = "ashwood"                                      # Hamo away: his house is here
    out = do(w, "Edric", do="give", to="Hamo", item="grain", qty=5)
    assert "door of Hale House" in out and "open" in out or "door" in out
    pile = next(cid for cid, c in w.s["containers"].items() if c["kind"] == "pile")
    TH.remember(w, "Sibyl", pile, "saw")
    assert do(w, "Sibyl", do="take", item="grain", qty=5, **{"from": "the Green"}).startswith("You took")
    give(w, "Edric", grain=3)
    assert do(w, "Edric", do="give", to="Reed House", item="grain", qty=3).startswith("You left 3 grain at Reed House")
    assert w.goods(w.s["buildings"]["reed_house"]["stock"]).get("grain", 0) >= 3


def test_bury_is_offered_only_where_a_body_lies_and_frozen_ground_takes_six():
    from cybertron2.engine import knowledge as KN
    w = world()
    can, near = KN.options(Here(w, "Edric"), Mind(w, "Edric"), limit=99)
    assert not any(x.startswith("work bury") for x in can + near)
    cid = _body(w, "long_field", "Hamo")
    can, _ = KN.options(Here(w, "Edric"), Mind(w, "Edric"), limit=99)
    assert any(x.startswith("work bury") for x in can)
    assert V.cost(Here(w, "Edric"), {"do": "work", "what": "bury", "at": "Hamo"}) == 2
    w.cold_days = {w.d}
    assert V.cost(Here(w, "Edric"), {"do": "work", "what": "bury", "at": "Hamo"}) == 6
    assert do(w, "Edric", do="work", what="bury", at="Hamo").startswith("You buried Hamo")
    assert w.s["containers"][cid]["buried"] == w.d and not TH.bodies(w, "millbrook")


# ---------------------------------------------------------------------- decay by condition (D2-87)
def test_grain_in_the_open_on_a_wet_day_loses_five_percent():
    w = world(weather={1: "rain"})
    w.s["seq"] += 1
    cid = "pile:x"
    w.s["containers"][cid] = {"kind": "pile", "node": "millbrook", "parcel": "long_field", "goods": {"grain": 100.0}, "wear": {}}
    share, becomes = N.decay_rate(w, w.s["containers"][cid], "grain")
    assert abs(share - 0.005 * 10 * 1.2) < 1e-3 or abs(share - 0.05) < 1e-3     # 0.5% x10 (and x1.2 in summer)
    meat = {"kind": "pile", "node": "millbrook", "parcel": "long_field", "goods": {"meat": 10.0}, "wear": {}}
    assert N.decay_rate(w, meat, "meat")[1] == "rotting meat"


# ---------------------------------------------------------------------- fuse events (D2-80 to D2-84)
def _raid(w, structure, by="Warin", house="reed_house"):
    w.s["buildings"][house]["structure"] = structure
    w.s["people"][by]["at"] = "millbrook"
    w.s["today"]["fights"].append({"kind": "raid", "by": by, "building": house, "node": "millbrook"})


def test_a_raid_on_a_hut_gives_no_call_on_timber_one_act_on_stone_up_to_three_and_one_call_a_night(monkeypatch):
    monkeypatch.setitem(FU.FUSE["raid"]["detect"], "watcher", 1.0)
    for structure, acts in (("wattle", 0), ("timber", 1), ("stone", 3)):
        w = world()
        _raid(w, structure)
        w.s["buildings"]["reed_house"]["fittings"]["dog"] = 1
        woke = FU.plan(w, w.s["today"])
        if acts == 0:
            assert woke == {}
        else:
            assert all(x["acts"] == acts for x in woke.values())
    w = world()
    w.s["buildings"]["reed_house"]["structure"] = "stone"
    w.s["buildings"]["hale_house"]["structure"] = "stone"
    w.s["today"]["guards"] = {"Sibyl": "reed_house"}
    _raid(w, "stone")
    w.s["people"]["Osric"]["at"] = "millbrook"
    w.s["today"]["fights"].append({"kind": "raid", "by": "Osric", "building": "reed_house", "node": "millbrook"})
    woke = FU.plan(w, w.s["today"])
    assert "Sibyl" in woke and len(woke["Sibyl"]["events"]) == 2              # one call, seeing both (D2-82)
    assert FU.plan(w, w.s["today"]).get("Sibyl") is None                       # no second call tonight (D2-80)


def test_defending_wakes_the_house_and_a_hand_over_ends_the_raid_without_a_fight(monkeypatch):
    monkeypatch.setitem(FU.FUSE["raid"]["detect"], "watcher", 1.0)
    w = world()
    _raid(w, "stone")
    w.s["today"]["guards"] = {"Sibyl": "reed_house"}
    woke = FU.plan(w, w.s["today"])
    x = woke["Sibyl"]
    lines = FU.answer(w, w.s["today"], "Sibyl", x, {"actions": [{"do": "alarm"}, {"do": "defend"}, {"do": "stay"}, {"do": "flee"}]})
    assert any("woke the house" in y for y in lines) and "There was time for only 3 things." in lines
    assert "Edric" in w.s["today"]["awake"]
    w2 = world()
    _raid(w2, "stone")
    w2.s["containers"][w2.s["buildings"]["reed_house"]["stock"]]["goods"]["grain"] = 20.0
    w2.s["today"]["guards"] = {"Sibyl": "reed_house"}
    x = FU.plan(w2, w2.s["today"])["Sibyl"]
    FU.answer(w2, w2.s["today"], "Sibyl", x, {"actions": [{"do": "hand over", "item": "grain", "qty": 5}]})
    rec = N.night(w2)
    assert any(f["outcome"] == "handed" for f in rec["fights"])


def test_the_urgent_call_is_appended_to_the_agents_conversation(tmp_path, monkeypatch):
    from cybertron import llm
    sent = []

    def fake_call(backend, model, system, user, schema, **kw):
        sent.append(str(user))
        text = str(user)
        out = {"why": "x", "actions": [{"do": "defend"}]} if "## In the night" in text.split("Plan your day")[-1] else {"why": "x", "actions": []}
        return out, None, {"cc_equiv_usd": 0.0}
    monkeypatch.setattr(llm, "call", fake_call)
    spec = copy.deepcopy(SPEC)
    spec["days"] = 1
    for n, a in spec["agents"].items():
        if a.get("model"):
            a["model"] = "bot"
    spec["agents"]["Sibyl"]["model"] = "claude-haiku-5-5"
    spec["script"] = [{"day": 1, "who": "Hamo", "do": {"do": "attack", "target": "Reed House", "aim": "rob"}},
                      {"day": 1, "who": "Sibyl", "do": {"do": "guard", "at": "Reed House"}}]
    spec["buildings"]["reed_house"]["structure"] = "stone"
    monkeypatch.setitem(FU.FUSE["raid"]["detect"], "watcher", 1.0)
    import yaml, pathlib
    p = pathlib.Path(tmp_path) / "s.yaml"
    p.write_text(yaml.safe_dump(spec))
    R.run(str(p), str(tmp_path / "out"), backend="api", workers=2)
    night = [x for x in sent if "## In the night" in x]
    assert night and "Plan your day" in night[0]                               # the day's turn is before it, in one conversation


def test_a_thing_is_a_bundle_of_signs_a_glimpse_from_afar_and_its_contents_only_close(monkeypatch):
    from cybertron2.engine import signs as SG
    w = world(weather={1: "clear"})
    w.s["containers"]["pile:x"] = {"kind": "pile", "node": "millbrook", "parcel": "alder_copse", "goods": {"coin": 5.0, "hide": 1.0},
                                   "wear": {}, "hidden": "under brush", "day": 0}
    x = SG.thing_context(w, w.s["containers"]["pile:x"])
    rng = w.rng("t")
    far = SG.roll(SG.THING, x, rng, mult=1.0, near=False)
    assert far and not any("coin" in t for t in far)                    # a glimpse: heaped brush, no contents
    close = [r for _, r in SG.true_rows(SG.THING, x) if r.get("reach") == "near" and "coin" in r["text"](x)]
    assert close                                                          # a close look names what is there ...
    assert abs(TH.hidden_factor(w.s["containers"]["pile:x"]) - 0.2) < 1e-9     # ... found only as hiding allows (perceive: p x this)
    assert SG.readable({"knows": "hunt"}, set()) is False and SG.readable({"lay": "hunt"}, set()) is True


def _thing(w, cid, **c):
    from cybertron2.engine import signs as SG
    base = {"kind": "pile", "node": "millbrook", "parcel": "alder_copse", "goods": {}, "wear": {}, "day": 0}
    base.update(c)
    w.s["containers"][cid] = base
    return SG.thing_context(w, base)


def test_no_glimpse_of_a_thing_names_what_it_holds_or_whose_body_it_is():
    import re
    from cybertron2.engine import signs as SG
    from cybertron2.engine.data import ITEMS
    w = world(weather={1: "clear", 2: "rain", 3: "snow", 4: "clear"}, cold_days=[3, 4])
    w.cold_days = {2, 3}
    w.s["people"]["Odo"]["cause"] = "attack"
    goods = {"coin": 4.0, "hide": 1.0, "grain": 12.0, "meat": 2.0, "rotting meat": 1.0}
    states = [dict(kind="remains", of="Odo", body=True, died=0, goods=dict(goods)), dict(kind="remains", of="Odo", body=True, died=0, buried=1),
              dict(goods=dict(goods)), dict(goods={"bread": 2.0, "copper": 1.0}), dict(goods=dict(goods), hidden="under brush", untaught=True),
              dict(goods=dict(goods), hidden="buried"), dict(goods={"timber": 3.0}, door=next(iter(w.s["buildings"])))]
    seen = 0
    for day in (0, 1, 3, 13):
        w.s["day"] = day
        for k, st in enumerate(states):
            x = _thing(w, f"t{k}", **st)
            for _, row in SG.true_rows(SG.THING, x):
                if row.get("reach", "rule") == "near":
                    continue
                text = row["text"](x)
                seen += 1
                assert "Odo" not in text, text
                assert not any(re.search(rf"\b{re.escape(i)}\b", text) for i in ITEMS if i in x.goods), text
    assert seen > 20


def test_a_things_signs_follow_the_weather_the_season_and_who_reads_them():
    from cybertron2.engine import signs as SG
    w = world(weather={1: "clear", 2: "clear", 3: "clear", 4: "clear"})
    w.s["day"] = 3
    warm = [r["text"](x) for x in [_thing(w, "b", kind="remains", of="Odo", body=True, died=0)] for _, r in SG.true_rows(SG.THING, x)]
    assert any("flies" in t for t in warm) and any("crows" in t for t in warm)
    w.cold_days = {3}
    cold = [r["text"](x) for x in [_thing(w, "b", kind="remains", of="Odo", body=True, died=0)] for _, r in SG.true_rows(SG.THING, x)]
    assert not any("flies" in t for t in cold) and any("frozen hard" in t for t in cold)   # flies in the warm, nothing in frost
    x = SG.thing_context(w, w.s["containers"]["b"])
    crows = [r for _, r in SG.true_rows(SG.THING, x) if "crows" in r["text"](x)]
    assert crows and all(r["reach"] == "node" for r in crows)                           # seen from anywhere at the place
    cache = _thing(w, "c", goods={"coin": 5.0}, hidden="under brush")
    rng = w.rng("t")
    hunter = SG.roll(SG.THING, cache, rng, mult=1.0, know={"hunt"})
    lay = SG.roll(SG.THING, cache, rng, mult=1.0, know=set())
    assert any("someone has hidden something" in t for t in hunter) and not any("someone has hidden something" in t for t in lay)


def test_tracks_are_plain_in_snow_and_a_hunter_counts_them():
    from cybertron2.engine import signs as SG
    w = world(weather={1: "snow", 2: "clear", 3: "clear"}, cold_days=[1, 2, 3])
    w.cold_days = {0, 1, 2}
    w.s["day"] = 2
    tr = {"road": "r", "pos": 1, "day": 1, "kind": "tracks", "n": 3, "toward": "Ashwood", "by": []}
    x = SG.trace_context(w, tr)
    texts = {r.get("knows"): r["text"](x) for _, r in SG.true_rows(SG.TRACE, x)}
    assert "plain in the snow" in texts[None] and "three people" in texts["hunt"]
    assert "three" not in " ".join(SG.roll(SG.TRACE, x, w.rng("t"), know=set()))
