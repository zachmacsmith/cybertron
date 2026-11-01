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
