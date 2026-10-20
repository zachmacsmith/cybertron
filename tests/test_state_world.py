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


# ---------------------------------------------------------------------- 2.10 directories: version log, owners, grants, seals
def dir_world(**store):
    sp = T.world()
    sp["start"]["institutions"][0]["offices"]["president"] = {"title": "President", "holders": ["Di"], "duties": "Preside."}
    sp["start"]["institutions"][0]["offices"]["registrar"] = {"title": "Registrar", "holders": ["Bo"], "duties": "Keep minutes."}
    sp["directories"] = {"enabled": True, "stores": {"minutes": {"owner": "office:J0.registrar", "title": "the council minutes",
                                                                  **store}}}
    sp.setdefault("actions", {})["core_only"] = False
    return sp


def test_directories_without_records_options_are_unchanged(tmp_path):
    from cybertron import directories as DR
    k = T.setup(tmp_path, dir_world())
    assert set(k.w["dirs"]["minutes"]) == {"owner", "scope", "namespace", "max_bytes", "max_file_bytes", "records", "title",
                                           "readonly", "grants", "files"}
    act(k, "Bo", "dir_write", path="r1.md", text="the council met")
    assert "dir_history" not in k.w and not DR.history_on(k)
    with pytest.raises(ActionError, match="unknown action"):
        act(k, "Bo", "dir_history", path="r1.md")
    assert "sha" not in DR.round_record(k)["directories"]["minutes"]["files"]["r1.md"]


def test_office_owner_version_log_and_history_readers(tmp_path):
    from cybertron import directories as DR
    k = T.setup(tmp_path, dir_world(history="full", history_readers="office:J0.president", announce=["council/"]))
    assert DR.is_owner(k, "Bo", k.w["dirs"]["minutes"]) and not DR.is_owner(k, "Di", k.w["dirs"]["minutes"])
    act(k, "Bo", "dir_write", path="council/r1.md", text="the council met; Ada objected")
    T.step(k)
    act(k, "Bo", "dir_edit", path="council/r1.md", find="; Ada objected", replace="")
    rows = DR.versions(k, "minutes", "council/r1.md")
    assert [r["op"] for r in rows] == ["write", "edit"] and rows[1]["text_before"].endswith("Ada objected")
    assert rows[0]["round"] == 0 and rows[1]["round"] == 1 and rows[1]["sha_before"] == rows[0]["sha_after"]
    notices = [e for e in k.events if e["type"] == "dir_changed"]
    assert len(notices) == 2 and notices[1]["vis"] == "public" and notices[1]["data"]["bytes"] < 0
    out = act(k, "Di", "dir_history", dir="minutes", path="council/r1.md")      # the President reads the history, not the file
    assert "v2: round 2, Bo, edit" in out and "Ada objected" in out
    with pytest.raises(ActionError):
        act(k, "Di", "dir_read", dir="minutes", path="council/r1.md")
    with pytest.raises(ActionError):
        act(k, "Bo", "dir_history", dir="minutes", path="council/r1.md")        # the owner is not a history reader here
    assert "sha" in DR.round_record(k)["directories"]["minutes"]["files"]["council/r1.md"]


def test_institution_owner_and_office_and_members_grants(tmp_path):
    from cybertron import directories as DR
    sp = dir_world(grants={"office:J0.keeper": {"": "read"}})
    sp["directories"]["stores"]["books"] = {"owner": "institution:A1", "title": "the shop's books"}
    k = T.setup(tmp_path, sp)
    books = k.w["dirs"]["books"]
    assert {a for a in k.players() if DR.is_owner(k, a, books)} == {"Ada", "Bo", "Di"}   # A1's members and its head
    act(k, "Bo", "dir_write", dir="minutes", path="r1.md", text="minutes")
    assert "minutes" in act(k, "Cy", "dir_read", dir="minutes", path="r1.md")   # the Keeper reads through the office grant
    act(k, "Bo", "dir_grant", dir="minutes", agent="members:A1", path="", access="read")
    assert DR.level(k, "Di", k.w["dirs"]["minutes"], "r1.md") == "read"
    assert DR.level(k, "Fay", k.w["dirs"]["minutes"], "r1.md") == "none"


LAW_SEAL = '''title = "Seal Old Minutes"
intent = "Seals every file of the minutes once it is a round old, and opens the version log to everyone."
rank = "statute"

def on_enact():
    set_dir_policy("minutes", "history_readers", "public")

def on_round_end(r):
    for p, f in dir_files("minutes").items():
        if not f["sealed"] and f["round"] != None and f["round"] < r:
            seal_file("minutes", p)
'''


def test_law_seals_files_and_sets_the_policy(tmp_path):
    from cybertron import directories as DR
    sp = dir_world(history="meta")
    sp["start"]["laws"] = [{"code": LAW_SEAL}]
    k = T.setup(tmp_path, sp)
    assert k.w["dirs"]["minutes"]["history_readers"] == "public"
    assert any(e["type"] == "dir_policy" for e in k.events)
    act(k, "Bo", "dir_write", path="r1.md", text="the council met")
    T.step(k)                                                           # round 0 ends: r1.md (written in round 0) is not older yet
    T.step(k)
    d = k.w["dirs"]["minutes"]
    assert "r1.md" in d["sealed"] and any(e["type"] == "dir_sealed" for e in k.events)
    with pytest.raises(ActionError, match="sealed"):
        act(k, "Bo", "dir_edit", path="r1.md", find="met", replace="did not meet")
    assert "sealed in round" in act(k, "Fay", "dir_history", dir="minutes", path="r1.md")


# ---------------------------------------------------------------------- 2.10 the Registry Act and the Archives Act
def invoke(k, aid, action, *args):
    return act(k, aid, "invoke", action=action, args=list(args))


def test_registry_act_files_certifies_corrects_and_registers_late_entries(tmp_path):
    from cybertron import registers as RG
    sp = dir_world()
    sp["start"]["laws"] = [{"template": "Registry Act", "params": {"FEE": 1, "AUTO_AFTER": 2,
                                                                   "OFFICES": ["J0.registrar", "J0.president"]}}]
    k = T.setup(tmp_path, sp)
    lid = T.law(k, "J0", "Registry Act")
    pub = k.w["laws"][lid]["public"]
    assert [r["office"] for r in pub["roll"]] == ["J0.registrar", "J0.president"]
    t0 = k.bal("Fay", "penny")
    assert "pending" in invoke(k, "Fay", "file_entry", "title", "Fay holds the east plot")
    assert k.bal("Fay", "penny") == pytest.approx(t0 - 1)
    with pytest.raises(ActionError):
        invoke(k, "Fay", "certify_entry", 1, "ok")                      # only the Registrar certifies
    invoke(k, "Bo", "certify_entry", 1, "seen")
    invoke(k, "Bo", "correct_entry", 1, "the plot is the north-east plot")
    assert pub["register"][0]["text"] == "Fay holds the east plot" and pub["errata"][0]["n"] == 1   # errata, never edits
    invoke(k, "Di", "file_entry", "notice", "Di is a candidate")
    with pytest.raises(ActionError, match="reason"):
        invoke(k, "Bo", "refuse_entry", 2)
    T.step(k, 2)                                                        # nobody decides entry 2: registered automatically
    pub = k.w["laws"][lid]["public"]
    assert pub["register"][1]["status"] == "registered" and "automatic" in pub["register"][1]["decided_by"]
    assert invoke(k, "Ed", "extract_entry", 1).endswith("extract sent")
    note = [e for e in k.events if e["type"] == "notify" and "Certified extract" in str(e["data"])]
    assert note and "north-east" in str(note[-1]["data"])
    assert "Fay holds" in RG.read_register(k, "Ed", {"law": lid, "book": "register"})


def test_archives_act_seals_sets_history_readers_and_audits(tmp_path):
    sp = dir_world(history="full")
    sp["start"]["institutions"][0]["offices"]["auditor"] = {"title": "Auditor", "holders": ["Ed"], "duties": "Audit."}
    sp["start"]["laws"] = [{"template": "Archives Act", "params": {"DIR": "minutes", "SEAL_AFTER": 2,
                                                                   "HISTORY_READERS": "office:J0.president",
                                                                   "AUDITOR": "J0.auditor"}}]
    k = T.setup(tmp_path, sp)
    lid = T.law(k, "J0", "Archives Act")
    assert k.w["laws"][lid]["rank"] == "constitution" and k.w["dirs"]["minutes"]["history_readers"] == "office:J0.president"
    act(k, "Bo", "dir_write", path="r1.md", text="the council met; Ada objected")
    T.step(k)
    act(k, "Bo", "dir_edit", path="r1.md", find="; Ada objected", replace="")   # the 1984 edit, before sealing
    assert "not sealed yet" in invoke(k, "Ed", "audit_record", "r1.md")
    T.step(k, 3)
    pub = k.w["laws"][lid]["public"]
    assert [r["path"] for r in pub["sealed"]] == ["r1.md"]
    with pytest.raises(ActionError, match="sealed"):
        act(k, "Bo", "dir_write", path="r1.md", text="again")
    assert invoke(k, "Ed", "audit_record", "r1.md").endswith("intact since sealing")
    pub = k.w["laws"][lid]["public"]
    assert pub["audits"][-1]["changes"] == 1 and pub["audits"][-1]["versions"] == 2   # the audit sees the edit in the log
    assert "Ada objected" in act(k, "Di", "dir_history", dir="minutes", path="r1.md")
    with pytest.raises(ActionError):
        invoke(k, "Fay", "audit_record", "r1.md")
