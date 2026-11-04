"""c2viz against the engine as it is now: what c2viz uses still exists, a short run builds to the data contract and replays, and
the renderer's modules load in order. When the engine changes, these say where c2viz must follow.

    python -m pytest c2viz/tests -q
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from c2viz import model as MD, schema, touch

ROOT = Path(__file__).resolve().parents[2]


def test_the_engine_still_has_what_c2viz_touches():
    assert touch.check() == []


@pytest.fixture(scope="module")
def short_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("run")
    subprocess.run([sys.executable, "-m", "cybertron2.engine", "run", str(ROOT / "cybertron2/specs/hamlet_s1.yaml"), "--out", str(out), "--bots",
                    "--days", "2"], check=True, cwd=ROOT, capture_output=True)
    return out


def test_a_run_builds_to_the_contract_and_replays(short_run):
    viz = json.loads(MD.build(short_run).read_text())
    assert viz["meta"]["schema"] == schema.SCHEMA_VERSION
    assert schema.validate(viz) == []
    state = MD.world_at(MD.open_run(short_run), "d0.memory").s
    assert touch.check(state) == []
    for d in viz["days"]:
        assert d["timeline"]["unreplayed"] == 0                  # every journaled change replays through the engine's chokepoint
        assert all(0 <= a["t0"] <= a["t1"] <= 1 for a in d["timeline"]["acts"])


def test_the_renderer_modules_load_in_order():
    js = ROOT / "c2viz/js"
    names = (js / "MANIFEST").read_text().split()
    defined = set()
    for n in names:
        src = (js / f"{n}.js").read_text()
        m = re.search(r"const \{ ([^}]*) \} = X;", src)
        needs = [x.strip() for x in m.group(1).split(",")] if m else []
        missing = [x for x in needs if x not in defined]
        assert not missing, f"{n}.js needs {missing} before it is defined (js/MANIFEST order)"
        e = re.search(r"Object\.assign\(X, \{ ([^}]*) \}\);", src)
        defined |= {x.strip() for x in e.group(1).split(",")} if e else set()
    assert "api" in names[-1:]


def test_a_generated_world_is_drawn_from_its_ground_truth(tmp_path):
    """A generated world's cells are packed for the renderer, and every road recovered by the generator's own rule leaves by the
    parcels the world file says (c2viz/ground.py)."""
    import yaml
    from c2viz import ground as GR
    from cybertron2.landgen import write as LW
    from cybertron2.engine.world import World
    spec = yaml.safe_load((ROOT / "cybertron2/specs/twin_bays_gen.yaml").read_text())
    world, cells, report = LW.generate(spec, str(ROOT / "cybertron2/specs/twin_bays_gen.yaml"))
    LW.write(world, cells, report, str(tmp_path / "w.yaml"))
    w = World({**world, "agents": world.get("agents") or {}})            # the land and roads; no people needed
    land = GR.pack(tmp_path, world, w.s["roads"], tmp_path / "w.cells.npz")
    assert land and land["roads_check"]["roads"] == len(w.s["roads"]) and land["roads_check"]["unmatched"] == []
    assert set(land["sites"]) == set(w.s["nodes"]) and land["rivers"]
    assert schema.validate({"meta": {k: 0 for k in schema.META}, "tables": {}, "static": {k: 0 for k in schema.STATIC}, "days": [],
                            "land": land}) == []


def test_the_site_builds_a_run_in_parts_the_same_as_whole(short_run):
    """The site builds a run's head and each day on its own (model.RunModel); together they are the whole build."""
    whole = json.loads(MD.build(short_run).read_text())
    RM = MD.RunModel(short_run)
    head = RM.head()
    assert set(head["static"]["buildings_ever"]) >= {b for d in whole["days"] for b in d["buildings"]}
    for d in RM.days:
        assert json.dumps(RM.day(d), sort_keys=True, default=str) == json.dumps(whole["days"][d], sort_keys=True, default=str)
