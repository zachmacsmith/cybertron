"""Goods in the open are seen by their bulk; a close look judges how much within a band, one who attends to them counts them; a large
store spoiling in the open smells, then draws rats; a fitting begun shows on its building (heap-sizes proposal)."""
from cybertron2.engine import buildings as BL, perceive as PC, run as R, signs as SG, things as TH
from cybertron2.engine.here import Here
from cybertron2.engine.world import World, load_spec

SPEC = "cybertron2/specs/wenbridge.yaml"


def _heap(w, qty, item="grain", parcel="wb_green"):
    cid = w.apply("new_thing", "wenbridge", node="wenbridge", parcel=parcel, kind="pile", by=None)
    w.apply("create", "wenbridge", dst=cid, item=item, qty=qty, why="test")
    return cid


def _w():
    w = World(load_spec(SPEC))
    w.s["today"] = R.blank_today()
    return w


def test_a_heap_is_more_conspicuous_the_more_there_is():
    w = _w()
    own = [TH.own(w, w.s["containers"][_heap(w, q)]) for q in (1, 2, 10, 50)]
    assert own == sorted(own) and abs(own[1] - 0.37) < 0.02 and abs(own[2] - 0.9) < 0.01 and own[3] > 0.99


def test_band_and_count_words():
    assert TH.band_words(95) == "perhaps 80 to 120" and TH.band_words(4) == "perhaps 3 to 5" and TH.band_words(0.4) == "a little"
    assert TH.count_words(96) == "about 95" and TH.count_words(13.4) == "about 13"


def _texts(w, cid):
    rows, x = SG.bundle(w, w.s["containers"][cid])
    return {r: [row["text"](x) for _, row in SG.true_rows(rows, x) if row.get("reach", "rule") == r] for r in ("rule", "near", "count")}


def test_far_a_size_near_a_band_attended_a_count():
    w = _w()
    t = _texts(w, _heap(w, 96))
    assert any(s.startswith("a large heap of something at the Green") for s in t["rule"])
    assert any("a large heap of grain (perhaps 80 to 120) lies at the Green" in s for s in t["near"])
    assert any(s.endswith("about 95 grain") for s in t["count"])
    assert any(s.startswith("a great heap") for s in _texts(w, _heap(w, 150))["rule"])


def test_counting_is_only_for_one_attending_to_it():
    w = _w()
    cid = _heap(w, 60)
    tag = w.s["containers"][cid]["tag"]
    attend = {n: None for n in w.living()}
    attend["Tom"] = "the Green"
    attend["Wat"] = tag                                                          # one may attend to a thing one knows of
    TH.remember(w, "Wat", cid, "saw", text="a large heap of something at the Green")
    PC.evening(w, attend, R.blank_today())
    m = w.s["mind"]
    notice = lambda n: " ".join(m[n]["today"]["notice"] + (m[n]["today"]["attended"] or {}).get("lines", []))
    assert "about 60 grain" in notice("Tom")
    assert m["Wat"]["today"]["attended"]["target"] == f"what lies there ({tag})" and "about 60 grain" in notice("Wat")
    assert all("about 60 grain" not in " ".join(m[n]["today"]["notice"]) for n in w.living())


def test_a_large_wet_store_left_out_smells_then_draws_rats():
    w = _w()
    cid = _heap(w, 80)
    rows, x = SG.bundle(w, w.s["containers"][cid])
    x.rained, x.age = True, 3
    texts = [row["text"](x) for _, row in SG.true_rows(rows, x)]
    assert any("musty smell of something wet going bad" in s for s in texts) and any(s.startswith("rats run in and out") for s in texts)
    small = _heap(w, 12)
    rows, x = SG.bundle(w, w.s["containers"][small])
    x.rained, x.age = True, 3
    assert not any("rats" in row["text"](x) for _, row in SG.true_rows(rows, x))


def test_a_fitting_begun_shows_on_its_building():
    w = _w()
    b = w.s["buildings"]["mill_house"]
    assert "a water wheel and leat begun, its materials in (about 150 units of work left)" in BL.space_words(b, w.goods(b["stock"]))


def test_goods_left_at_a_door_stay_the_houses_to_use_sell_and_lose_by_theft():
    from cybertron2.engine import knowledge as KN, verbs as V
    from cybertron2.engine.here import Mind
    w = _w()
    cid = w.apply("new_thing", "wenbridge", node="wenbridge", parcel="wb_green", kind="pile", by=None, door="hearne_hut")
    w.apply("create", "wenbridge", dst=cid, item="grain", qty=50, why="test")
    assert cid in w.takeable("Tom") and cid not in w.takeable("Wat")              # the Hearnes' (D4-89)
    assert KN.available(Here(w, "Tom"), "grain") >= 50                             # so they may offer and sell it
    TH.remember(w, "Wat", cid, "saw", text="a heap of something at the Green")
    out = V.do(Here(w, "Wat"), Mind(w, "Wat"), {"do": "take", "item": "grain", "qty": 5, "from": "the Green"})
    assert "not yours to take from" in out and w.s["today"]["thefts"][-1]["building"] == "hearne_hut"
    out = V.do(Here(w, "Tom"), Mind(w, "Tom"), {"do": "take", "item": "grain", "qty": 5, "from": "the Green"})
    assert out.startswith("You took 5 grain") and "not yours" not in out
