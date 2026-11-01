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
    s = spec(configuration="twin bays split by a spur", places={"Northby": {"at": "north_bay.head"}, "Southby": {"at": "south_bay.head"}})
    return W.generate(s)


def test_same_input_same_world(bays):
    world, cells, _ = bays
    s = spec(configuration="twin bays split by a spur", places={"Northby": {"at": "north_bay.head"}, "Southby": {"at": "south_bay.head"}})
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
