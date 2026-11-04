"""The world record's shape is declared and versioned (spec/core/world_schema.md, D4-100): every world and every checkpoint carries
its version; a field the engine writes that the declared shape does not list fails here; and the declared shape cannot change without
its version moving."""
import json
import sqlite3
import zlib

import pytest

from cybertron2.engine import run as R, schema as S

SPECS = ("cybertron2/specs/valley_s5.yaml", "cybertron2/specs/combe.yaml", "cybertron2/specs/wenbridge.yaml",
         "cybertron2/specs/goal_probe/harm_none.yaml", "cybertron2/specs/goal_probe/food_none.yaml")


def test_the_declared_shape_matches_its_version():
    assert S.FINGERPRINTS.get(S.WORLD_SCHEMA) == S.fingerprint(), (
        f"the declared world shape changed (fingerprint {S.fingerprint()}): bump WORLD_SCHEMA, add the new fingerprint to "
        "FINGERPRINTS, and write the change in spec/core/world_schema.md")
    assert sorted(S.FINGERPRINTS) == list(range(1, S.WORLD_SCHEMA + 1))


@pytest.mark.parametrize("spec", SPECS)
def test_every_checkpoint_of_a_bot_run_holds_only_declared_fields_and_its_version(spec, tmp_path):
    out = tmp_path / "run"
    R.run(spec, out, days=3, bots=True)
    con = sqlite3.connect(str(out / "run.db"))
    meta = dict(con.execute("SELECT key, value FROM meta"))
    assert json.loads(meta["world_schema"]) == S.WORLD_SCHEMA
    for step, z in con.execute("SELECT step, z FROM checkpoints"):
        w = json.loads(zlib.decompress(z))["world"]
        assert S.version(w) == S.WORLD_SCHEMA
        assert not S.unknown(w), (f"{spec} {step}: fields not in the declared world shape: {S.unknown(w)}; list them in "
                                  "cybertron2/engine/schema.py, bump WORLD_SCHEMA and write them in spec/core/world_schema.md")
