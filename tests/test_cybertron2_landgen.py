"""The landscape generator, stage 1 (docs/cybertron2/proposals/generator_stage1.md §9): reproducible, pins met or refused, a
change kept to what depends on it, the checks, and a world today's engine loads."""
import copy

import numpy as np
import pytest

from cybertron2.landgen import field as F, macro as M, physical as P, settle as ST, vocab as V, write as W

SMALL = {"size_km": 30.0, "km": 0.2, "settlements": 2, "spacing_km": 12.0}


def spec(**gen):
    return {"name": "t", "seed": 3, "days": 10, "calendar": {"season": "summer", "day": 3, "season_days": 6},
            "generate": {"seed": 3, **SMALL, **gen}}


@pytest.fixture(scope="module")
def bays():
    s = spec(configuration="twin bays split by a spur", spacing_km=8.0,      # the bays' heads are about 10 km apart in a 30 km world
             places={"Northby": {"at": "north_bay.head"}, "Southby": {"at": "south_bay.head"}})
    return W.generate(s)


def test_same_input_same_world(bays):
    world, cells, _ = bays
    s = spec(configuration="twin bays split by a spur", spacing_km=8.0,
             places={"Northby": {"at": "north_bay.head"}, "Southby": {"at": "south_bay.head"}})
    w2, c2, _ = W.generate(s)
    assert w2["nodes"] == world["nodes"] and w2["roads"] == world["roads"]
    assert np.array_equal(c2["h"], cells["h"])


def test_pins_are_met(bays):
    world, _, report = bays
    assert {"Northby", "Southby"} <= set(world["nodes"])
    north = report["anchors"]["north_bay.head"]
    site = report["nodes"]["Northby"]["site_km"]
    assert np.hypot(site[0] - north[0], site[1] - north[1]) <= 4.0 + 1e-6


def test_a_pin_the_land_cannot_meet_is_refused():
    with pytest.raises(ST.Refused):
        W.generate(spec(places={"Nowhere": {"at": "no_such_anchor"}}))
    with pytest.raises(ST.Refused):
        W.generate(spec(places={"Wetley": {"terrain": "saltmarsh"}}))          # no sea, so no saltmarsh


def test_unknown_or_waiting_configuration_is_refused():
    with pytest.raises(ValueError):
        M.primitives({"configuration": "archipelago"})
    with pytest.raises(ValueError):
        M.primitives({"configuration": "no such shape"})


def test_physics_checks_pass_and_roads_are_about_a_day(bays):
    _, _, report = bays
    for k, v in report["checks"].items():
        if v["kind"] == "physics":
            assert v["ok"], (k, v)
    assert report["checks"]["roads about a day"]["ok"], report["checks"]["roads about a day"]
    assert report["checks"]["reachable by land"]["ok"]
    assert not report["refused"]


def test_parcels_per_node_and_graph_connected(bays):
    world, _, _ = bays
    for nid, n in world["nodes"].items():
        pars = n["parcels"]
        if n.get("unexplored") or len(pars) < 3:
            continue
        assert 3 <= len(pars) <= V.DEFAULTS["parcels"][1]
        seen, todo = {next(iter(pars))}, [next(iter(pars))]
        while todo:
            for q in pars[todo.pop()]["adj"]:
                if q not in seen:
                    seen.add(q)
                    todo.append(q)
        assert seen == set(pars), nid


def test_a_laid_river_runs_where_laid():
    s = spec(configuration="river through a range")
    _, _, report = W.generate(s)
    assert report["checks"]["laid rivers run where laid"]["ok"]
    assert report["checks"]["rivers run downhill"]["ok"]


def test_scarp_and_vale_gives_clay_below_and_chalk_above():
    conf = {**V.DEFAULTS, **SMALL, "configuration": "scarp and vale"}
    g = F.grid(3, conf["size_km"], conf["km"])
    L = P.build(conf, g, M.primitives(conf))
    south = L.tex[: g.ny // 3]
    north = L.tex[2 * g.ny // 3:]
    assert (south == V.CLAY).mean() > 0.6
    assert (north == V.CHALK).mean() > 0.6


def test_a_pin_changes_only_what_depends_on_it():
    a = W.generate(spec(households=[2, 2]))[0]
    b = W.generate(spec(households=[2, 2], places={}, settlements=2))[0]
    assert a["nodes"] == b["nodes"]                                         # the same file says the same world
    c = W.generate(spec(households=[2, 2], wild_nodes=0))[0]
    villages = [k for k, n in a["nodes"].items() if not n.get("unexplored") and k.startswith("s")]
    for k in villages:                                                      # wild nodes off: the villages' land is untouched
        assert c["nodes"][k]["parcels"].keys() == a["nodes"][k]["parcels"].keys()


def test_the_engine_loads_the_land(bays):
    from cybertron2.engine.world import World
    world, _, _ = bays
    w = World({**{k: v for k, v in world.items() if k not in ("lines", "bounds", "sim")}, "agents": {}})
    assert set(w.s["nodes"]) == set(world["nodes"])
    assert all(p["cover"] in ("built", "field", "meadow", "pasture", "forest", "water", "scrub", "rock", "heath", "moor", "fen",
                              "saltmarsh") for p in w.s["parcels"].values())


def test_people_settle_and_the_world_runs_a_day():
    from cybertron2.engine.world import World
    s = spec(households=[1, 1], wild_nodes=0)
    world, _, report = W.generate(s, people=True)
    assert world.get("agents") and not report["refused"]
    w = World(copy.deepcopy(world))
    assert len(w.s["people"]) == len(world["agents"])


def test_words_place_and_pin():
    w, c, r = W.generate(spec(places={"Port": {"on": "sea"}}, settlements=2))       # "by the sea" with no sea: a coast is placed
    assert c["sea"].any() and "Port" in w["nodes"]
    w, c, r = W.generate(spec(places={"Home": {}, "Far": {"days_out": {"from": "Home", "days": 1}}}, settlements=3))
    a, b = r["nodes"]["Home"]["site_km"], r["nodes"]["Far"]["site_km"]
    assert 0.55 * 24 <= np.hypot(a[0] - b[0], a[1] - b[1]) <= 24 + 1e-6
    w, c, r = W.generate(spec(places={"Rich": {"soil": "rich"}}, settlements=2))
    assert all(p["fertility"] >= 1.2 for p in w["nodes"]["Rich"]["parcels"].values() if p["cover"] == "field")


def test_hidden_ways_are_known_to_a_few_and_capacity_holds_for_the_people_made():
    w, c, r = W.generate(spec(households=[2, 2]), people=True)
    knowers = [n for n, a in w["agents"].items() if a.get("ways")]
    hidden = [rd for rd in w["roads"] if any(e.get("hidden") for e in rd[3]["ends"].values())]
    assert (not hidden) or 1 <= len(knowers) <= 2 * 2 * len(hidden)
    cap = r["checks"]["capacity, people as generated"]
    assert cap["ok"], cap


def test_economic_checks_run_on_the_people_made_and_pass_a_generated_world():
    w, c, r = W.generate(spec(households=[2, 2]), people=True)
    econ = {k: v for k, v in r["checks"].items() if v["kind"] == "economy"}
    assert "economy: food over the run" in econ and "economy: carrying burden" in econ
    assert not [k for k in r["refused"] if k.startswith("economy")], r["refused"]


def _village(days=20, stock=None, fields=4, people=6, second=None):
    """A hand world: one village (and a second, short one if asked) for the economic checks."""
    def parcels(prefix, n_fields):
        out = {f"{prefix}_house": {"cover": "built", "size": 1, "adj": [f"{prefix}_f0"] if n_fields else []}}
        for i in range(n_fields):
            out[f"{prefix}_f{i}"] = {"cover": "field", "size": 1, "fertility": 1.0, "adj": [f"{prefix}_house"]}
        return out
    nodes = {"a": {"name": "Ash", "parcels": parcels("a", fields)}}
    buildings = {"a_home": {"name": "the Ash house", "node": "a", "parcel": "a_house", "structure": "timber", "size": 8,
                            "fittings": {"hearth": 1, "beds": 8}, "household": "h_ash",
                            "stock": stock if stock is not None else {"grain": 60, "firewood": 40}}}
    agents = {f"P{i}": {"stage": "adult", "sex": "m" if i % 2 else "f", "household": "h_ash", "home": "a_home", "at": "a"}
              for i in range(people)}
    roads = []
    if second:
        nodes["b"] = {"name": "Birch", "parcels": parcels("b", 0)}
        buildings["b_home"] = {"name": "the Birch house", "node": "b", "parcel": "b_house", "structure": "timber", "size": 8,
                               "fittings": {"hearth": 1, "beds": 8}, "household": "h_birch", "stock": {"grain": 10, "firewood": 20}}
        agents.update({f"Q{i}": {"stage": "adult", "sex": "m", "household": "h_birch", "home": "b_home", "at": "b"}
                       for i in range(second)})
        roads = [["a", "b", 1, {}]]
    return {"name": "t", "seed": 1, "days": days, "calendar": {"season": "summer", "day": 1, "season_days": 6},
            "nodes": nodes, "buildings": buildings, "agents": agents, "roads": roads}


def test_economy_refuses_a_short_village_that_must_carry_its_food():
    from cybertron2.landgen import economy as EC
    c = EC.check(_village(second=6))
    assert c["carrying burden"]["level"] == "refuse" and not c["carrying burden"]["ok"]
    assert "carrying burden" in EC.refused(c)


def test_economy_refuses_a_run_its_food_cannot_reach():
    from cybertron2.landgen import economy as EC
    c = EC.check(_village(days=30, stock={"firewood": 40}, fields=0, people=6))
    assert "food over the run" in EC.refused(c)
    ok = EC.check(_village(days=4, stock={"grain": 60, "firewood": 40}, fields=4, people=6))
    assert "food over the run" not in EC.refused(ok)
