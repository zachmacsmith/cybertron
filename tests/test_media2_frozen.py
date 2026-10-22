"""media2 is frozen (docs/ARCHITECTURE.md, "media2 is frozen"): channels v2 is the canonical press, and no new spec may turn media2
on. Loading a spec with media2 on warns (FrozenModuleWarning), never fails: the specs below, and the published runs made from them,
still run. A new spec with media2 on fails test_no_new_media2_specs; move it to channels.v2 instead."""
from __future__ import annotations

import warnings

import pytest

from cybertron import spec as S

# The specs that turned media2 on when it was frozen. This list may only shrink.
MEDIA2_SPECS = {
    "explore15.yaml", "grand35.yaml", "haiku100.yaml", "media2_pilot.yaml", "opus20.yaml", "scientists.yaml", "society.yaml",
    "pilot2/base.yaml", "pilot2/control.yaml", "pilot2/duel.yaml", "pilot2/historian_clerks.yaml", "pilot2/revolution.yaml",
    "pilot2/usurpers.yaml", "pilot2/usurpers_historian.yaml",
}


def _media2_specs() -> set:
    on = set()
    for p in sorted(S.SPEC_DIR.rglob("*.yaml")):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", S.FrozenModuleWarning)
            sp = S.load(str(p))
        if (sp.get("media2") or {}).get("enabled") not in (None, False):
            on.add(p.relative_to(S.SPEC_DIR).as_posix())
    return on


def test_no_new_media2_specs():
    on = _media2_specs()
    assert not on - MEDIA2_SPECS, f"new spec(s) with media2 on: {sorted(on - MEDIA2_SPECS)}; media2 is frozen, use channels.v2"
    assert not MEDIA2_SPECS - on, f"no longer on media2 (drop them from MEDIA2_SPECS): {sorted(MEDIA2_SPECS - on)}"


def test_loading_a_media2_spec_warns_and_still_loads():
    with pytest.warns(S.FrozenModuleWarning, match="media2 is frozen"):
        sp = S.load("media2_pilot")
    assert sp["media2"]["enabled"] is True
    with warnings.catch_warnings():
        warnings.simplefilter("error", S.FrozenModuleWarning)
        S.load("E2")                                                    # media2 off: no warning
