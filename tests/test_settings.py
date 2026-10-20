"""Frozen settings (cybertron/settings.py, D-43): a run keeps the code defaults it was generated under; old runs get them inferred
from their git sha, or are refused."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from cybertron import __main__ as M
from cybertron import agents as AG
from cybertron import context as CX
from cybertron import generator, provenance as PV, runner
from cybertron import settings as ST
from cybertron import spec as S

QUIET = dict(log=lambda *a: None)
SETS = ["rounds=3", "shared_archive.enabled=false",
        "context.history.enabled=false"]   # history mode restarts its conversations at a resume (by design): compared with it off


def _inst():
    inst = generator.generate(S.apply_overrides(S.load("society"), SETS), 1)
    inst["run_id"] = "r"                                             # as run_one sets it (resume regenerates and compares)
    return inst


def _prompts(out: Path) -> list:
    """Every prompt of the run: the user prompts (reasoning.jsonl) and the system/user prompt hashes of every call."""
    rows = [json.loads(x) for x in (out / "reasoning.jsonl").read_text().splitlines()]
    calls = [json.loads(x) for x in (out / "calls.jsonl").read_text().splitlines()]
    return [(r.get("round"), r.get("agent"), r.get("phase"), r.get("prompt")) for r in rows] + \
           [(c["key"], c["system_sha"], c["user_sha"]) for c in calls]


def _flip(monkeypatch):
    """Today's code with the review 20 defaults flipped back (as a later commit might flip any default)."""
    monkeypatch.setitem(CX.DEFAULTS, "dm_delta", False)
    monkeypatch.setitem(CX.DEFAULTS["history"], "enabled", False)


def _resume(out, *extra):
    M.main(["resume", str(out), "--sandbox", "off", *extra])


@pytest.fixture(scope="module")
def reference(tmp_path_factory):
    """A whole run under the code's defaults, and a copy paused after round 1."""
    d = tmp_path_factory.mktemp("settings")
    ref = runner.run(_inst(), AG.ScriptedPolicy(1), d / "ref", **QUIET)
    part = runner.run(_inst(), AG.ScriptedPolicy(1), d / "part", until=1, **QUIET)
    return ref, part


def _copy(src: Path, dst: Path) -> Path:
    import shutil
    shutil.copytree(src, dst)
    return dst


def test_instance_freezes_every_default():
    inst = _inst()
    s = inst["settings"]
    assert s["engine_version"] == PV.ENGINE_VERSION
    assert set(s["defaults"]) == set(ST.targets())
    assert s["defaults"]["cybertron.context.DEFAULTS"]["memory_text"] == "v2"
    assert s["defaults"]["cybertron.schema.EXTRA"]["dm_step.capacity"] == "legacy"
    assert not ST.patches(s)                                          # today's code: nothing to install


def test_every_module_defaults_dict_is_registered():
    """A new *DEFAULTS dict must be frozen too: register it in settings.TARGETS."""
    pkg = Path(ST.__file__).parent
    found = set()
    for p in pkg.rglob("*.py"):
        mod = ".".join(("cybertron",) + p.relative_to(pkg).with_suffix("").parts)
        for m in re.finditer(r"^([A-Z_]*DEFAULTS)\s*(?::[^=]*)?=\s*\{", p.read_text(), re.M):
            if m.group(1) != "FEATURE_DEFAULTS":                         # schema's table of getters, not values
                found.add(f"{mod}.{m.group(1)}")
    assert found - set(ST.TARGETS) == set()


def test_resume_after_a_default_flip_plays_the_run_as_it_began(reference, tmp_path, monkeypatch):
    ref, part = reference
    run = _copy(part, tmp_path / "run")
    _flip(monkeypatch)
    _resume(run)
    assert _prompts(run) == _prompts(ref)                              # byte-identical prompts despite the flip
    assert CX.DEFAULTS["dm_delta"] is False                           # the code's defaults are back after the run
    seg = PV.read(run)["segments"][-1]
    assert seg["kind"] == "resume" and seg["settings"]["engine_version"] == PV.ENGINE_VERSION


def test_new_run_after_a_default_flip_takes_the_new_default(reference, tmp_path, monkeypatch):
    ref, _ = reference
    _flip(monkeypatch)
    inst = _inst()
    assert inst["settings"]["defaults"]["cybertron.context.DEFAULTS"]["dm_delta"] is False
    out = runner.run(inst, AG.ScriptedPolicy(1), tmp_path / "new", **QUIET)
    assert _prompts(out) != _prompts(ref)
    assert PV.read(out)["dm_delta"] is False


def test_without_frozen_settings_the_flip_would_leak_and_is_refused(reference, tmp_path, monkeypatch):
    """An old run (no settings, unknown sha) is refused; --allow-code-drift plays it under today's defaults, recorded."""
    ref, part = reference
    run = _copy(part, tmp_path / "old")
    inst = json.loads((run / "instance.json").read_text())
    inst.pop("settings")
    (run / "instance.json").write_text(json.dumps(inst, indent=1, default=str))
    PV.annotate(run, git={"sha": None})
    _flip(monkeypatch)
    with pytest.raises(ST.CodeDrift, match="cybertron rerun"):
        _resume(run)
    _resume(run, "--allow-code-drift")
    assert _prompts(run) != _prompts(ref)                              # the drift the frozen settings prevent
    meta = PV.read(run)
    assert meta["settings_inferred"]["code_drift"] and meta["segments"][-1]["settings"]["code_drift"]


def _have(sha):
    return ST._git("cat-file", "-e", f"{sha}^{{commit}}") is not None


@pytest.mark.skipif(not all(_have(e["commits"][0]) for e in PV.ENGINE_FLIPS.values()), reason="needs the git history")
def test_infer_version_from_git_history():
    for v, e in PV.ENGINE_FLIPS.items():
        assert ST.infer_version(e["commits"][0]) == v
        assert ST.infer_version(e["commits"][0] + "^") == {2: 1, 3: 1, 10: 7, 11: 1, 16: 14, 17: 14}.get(v, v - 1)   # 2, 3, 10, 11, 16 and 17 were made on parallel branches
    s = ST.infer(PV.ENGINE_FLIPS[3]["commits"][0])                       # version 3 without version 2's flip
    assert s["engine_version"] == 3 and s["defaults"] == {}           # flips before MIN_ENGINE are no longer set back
    s = ST.infer(PV.ENGINE_FLIPS[10]["commits"][0])                      # version 10 (wp/survival-exp) without 8's or 9's flips
    assert s["engine_version"] == 10 and s["defaults"] == {}
    assert ST.infer_version("HEAD") == PV.ENGINE_VERSION
    assert ST.infer_version("0" * 40) is None


CON17 = {"pay_institutions": False, "applicant_lines": False}                # engine 17: economic plumbing
EXTRA15 = {"law.effects": False, "law.call_failures": False, "law.expects": False,    # engine 15: laws that fail loudly
           "institutions.amend_offices": False}
SUB14 = {"game": {"hunt_mode": "shared"}, "forest": {"clearing": 5},                     # engine 14: farming, the individual hunt
         "fields": {"plots_per_agent": 0.4, "plots_max_per_agent": 0.8, "mult": 3.5}}


def test_patches_revert_later_flips_only_where_the_snapshot_is_silent():
    """Flips of versions before provenance.MIN_ENGINE are no longer set back (those runs are refused for play); version 10's
    scoring flip still is (scoring an older run after the fact)."""
    p = ST.patches({"engine_version": 3, "defaults": {}})
    assert p == {"cybertron.context.DEFAULTS": {"world_name": "Charter", "budgets": {"state": 800}}, "cybertron.goals.SCORING_DEFAULTS": {"fixes": False}, "cybertron.subsistence.DEFAULTS": SUB14, "cybertron.schema.EXTRA": EXTRA15, "cybertron.channels.DEFAULTS": {"business": False}, "cybertron.contracts.DEFAULTS": CON17}
    p = ST.patches({"engine_version": 9, "defaults": {}})
    assert p == {"cybertron.context.DEFAULTS": {"world_name": "Charter", "budgets": {"state": 800}}, "cybertron.goals.SCORING_DEFAULTS": {"fixes": False}, "cybertron.subsistence.DEFAULTS": SUB14, "cybertron.schema.EXTRA": EXTRA15, "cybertron.channels.DEFAULTS": {"business": False}, "cybertron.contracts.DEFAULTS": CON17}
    assert ST.patches({"engine_version": 10, "defaults": {}}) == {"cybertron.context.DEFAULTS": {"world_name": "Charter", "budgets": {"state": 800}}, "cybertron.subsistence.DEFAULTS": SUB14, "cybertron.schema.EXTRA": EXTRA15, "cybertron.channels.DEFAULTS": {"business": False}, "cybertron.contracts.DEFAULTS": CON17}
    with ST.use({"engine_version": 1, "defaults": {}}):
        assert CX.DEFAULTS["world_name"] == "Charter" and CX.DEFAULTS["memory_text"] == "v2" and CX.cfg({})["dm_delta"] is True
    assert CX.DEFAULTS["world_name"] == ""


def test_runs_before_min_engine_are_not_played():
    for v in (1, 9, PV.MIN_ENGINE - 1):
        with pytest.raises(ST.TooOld, match="cybertron rerun"):
            ST.check_playable({"engine_version": v, "defaults": {}})
    ST.check_playable({"engine_version": PV.MIN_ENGINE, "defaults": {}})
    ST.check_playable({"engine_version": 1, "defaults": {}, "code_drift": True})      # --allow-code-drift: today's defaults
    ST.check_playable(None)


@pytest.mark.skipif(not _have(PV.ENGINE_FLIPS[3]["commits"][0]), reason="needs the git history")
def test_old_run_from_before_min_engine_is_refused_and_pointed_to_rerun(reference, tmp_path):
    """A run made at engine version 3 without frozen settings: its resume infers version 3 from run.json's sha and is refused
    (pre-13 runs do not replay in place: `cybertron rerun` plays them under their own code)."""
    _, part = reference
    old = _copy(part, tmp_path / "old")
    inst = json.loads((old / "instance.json").read_text())
    inst.pop("settings")
    (old / "instance.json").write_text(json.dumps(inst, indent=1, default=str))
    PV.annotate(old, git={"sha": PV.ENGINE_FLIPS[3]["commits"][0], "dirty": False})
    with pytest.raises(ST.TooOld, match="engine version 3.*cybertron rerun"):
        _resume(old)
    assert PV.read(old)["settings_inferred"]["engine_version"] == 3


def test_export_has_the_engine_version(reference, tmp_path):
    from cybertron import export as X
    ref, _ = reference
    X.export([ref], tmp_path / "ds", fmt="csv")
    runs = X.load(tmp_path / "ds")["runs"]
    assert [int(r["engine_version"]) for r in runs] == [PV.ENGINE_VERSION]
    assert PV.read(ref)["engine_version"] == PV.ENGINE_VERSION


def test_engine_versions_doc_lists_every_version():
    doc = (Path(PV.__file__).parents[1] / "docs" / "engine_versions.md").read_text()
    rows = {int(m.group(1)) for m in re.finditer(r"^\| (\d+) \|", doc, re.M)}
    assert rows == set(range(1, PV.ENGINE_VERSION + 1)) and set(PV.ENGINE_FLIPS) <= rows
    for e in PV.ENGINE_FLIPS.values():
        assert e["commits"][0][:7] in doc
