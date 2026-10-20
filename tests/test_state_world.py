"""Review 31 Phase 2 for the State world (docs/review/31_institutions/08_integration.md §3.3, §5 items 2.9, 2.10, 2.15;
11_state_world.md): the pull wiretap (channels.surveillance), the directory version log, institution owners and office grants,
the Registry Act and the Archives Act, and the State world spec. Everything is opt-in: a world without the keys and laws is
unchanged."""
from __future__ import annotations

import pytest

from cybertron import spec as S
from cybertron.actions import ActionError

import test_standing_contracts as T


def act(k, aid, name, **args):
    return T.act(k, aid, name, **args)


def dm(k, frm, to, text, encrypted=False):
    from cybertron.dispatch.changes import speech
    return k.apply("dm", sender=frm, recipient=to, text=text, encrypted=encrypted)


# ---------------------------------------------------------------------- 2.9 the pull wiretap
def tap_world(surv):
    sp = T.world()
    sp["start"]["rights"]["Ada"] = ["vote", "propose", "surveil"]
    sp.setdefault("channels", {})["surveillance"] = surv
    sp.setdefault("actions", {})["core_only"] = False
    return sp


def test_push_surveillance_unchanged(tmp_path):
    k = T.setup(tmp_path, tap_world(True))
    e = k.events[-1]
    eid = dm(k, "Bo", "Cy", "meet at dawn")
    ev = next(x for x in k.events if x["type"] == "dm")
    assert k.can_see("Ada", ev) and not k.can_see("Di", ev)
    with pytest.raises(ActionError):
        act(k, "Ada", "wiretap", agent="Bo")                            # no wiretap under push: an unknown action


def test_pull_wiretap_limits_and_visibility(tmp_path):
    from cybertron import surveillance as SV
    k = T.setup(tmp_path, tap_world({"mode": "pull", "targets": 1}))
    dm(k, "Bo", "Cy", "meet at dawn")
    dm(k, "Di", "Ed", "secret plan", encrypted=True)
    ev = next(x for x in k.events if x["type"] == "dm")
    assert not k.can_see("Ada", ev)                                     # nothing pushed to the surveiller
    out = act(k, "Ada", "wiretap", agent="Bo")
    assert "meet at dawn" in out and "1 of 1 taps" in out
    assert k.can_see("Ada", ev)                                         # read through a tap: visible (evidence) from now on
    assert act(k, "Ada", "wiretap", agent="Bo")                         # the same target again: free
    with pytest.raises(ActionError, match="the most a round"):
        act(k, "Ada", "wiretap", agent="Di")
    with pytest.raises(ActionError, match="only a holder of surveil"):
        act(k, "Bo", "wiretap", agent="Cy")
    taps = [e for e in k.events if e["type"] == "wiretap"]
    assert len(taps) == 1 and taps[0]["vis"] == "monitor" and taps[0]["data"]["target"] == "Bo"
    T.step(k)
    out = act(k, "Ada", "wiretap", agent="Di")                          # a new round, a new tap; encrypted messages stay out
    assert "secret plan" not in out and "no unencrypted" in out
    assert SV.taps_by_round(k) == {0: 1, 1: 1}
