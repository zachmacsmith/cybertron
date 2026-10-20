"""Legal experts (docs/review/31_institutions/14_legal_experts.md, cybertron/lawguide.py): the lawyer's archive, generated from the
engine, read in a turn and in the DM step; the public guide; every worked example enacts; every document fits the look-up budget;
the draft action and filing by reference; and nothing changes in a world without an archive."""
from __future__ import annotations

import json
import pickle
import re

import pytest

from cybertron import actions as A
from cybertron import action_registry as AR
from cybertron import context as CX
from cybertron import counsel as CN
from cybertron import directories as DR
from cybertron import generator as GN
from cybertron import lawguide as LG
from cybertron import lawlang as L
from cybertron import spec as S
from cybertron.actions import ActionError
from cybertron.kernel import Kernel

SPEC = "cybertron/specs/regimes/private_counsel.yaml"
LAWYER, CLIENT = "Marsh", "Anselm"


def setup_kernel(sp, seed=1):
    """A kernel after the run's setup (default code, constitution, statutes, the start block's round-0 entries), as runner.run
    builds it, without running a round."""
    from cybertron import code as DC
    from cybertron import interventions as IV
    from cybertron import regimes as RG
    from cybertron import runner
    from cybertron import start as STT
    inst = GN.generate(sp, seed)
    k = Kernel(inst)
    k.begin_round_cause(phase="setup")
    DC.seed(k, inst)
    const = k.new_law(inst["constitution_code"], "constitution")
    k.enact(const)
    RG.enact_statutes(k, inst)
    rs = runner.RunState(const=const, agents={a["id"]: a for a in inst["agents"]}, out=None)
    rs.schedule = list(STT.schedule(inst))
    IV.apply_due(k, inst, rs, "setup", round_=0, log=lambda *a: None)
    k.end_round_cause()
    return k


_BASE: dict = {}


@pytest.fixture
def k():
    """The Private world with counsel, after its setup (built once, copied per test)."""
    if "k" not in _BASE:
        k0 = setup_kernel(S.load(SPEC))
        _BASE["k"] = (k0.inst, pickle.dumps(k0.checkpoint_state()))
    inst, st = _BASE["k"]
    k = Kernel(inst)
    k.restore_state(pickle.loads(st))
    k.start_round()
    return k


def act(k, aid, verb, /, **args):
    return A.act(k, aid, verb, args)


def available(k, aid):
    a = next(x for x in k.inst["agents"] if x["id"] == aid)
    return {x.name for x in AR.available(k.inst, k, a)}


def files(k):
    return k.w["dirs"]["legal"]["files"]


# ---------------------------------------------------------------------- the archive
def test_the_setup_is_the_private_world_with_counsel(k):
    assert CN.clients_of(k, LAWYER) == ["Anselm", "Moss"]                # the two retainers of private.yaml (A5, A6)
    assert LG.on(k) and LG.archives_of(k, LAWYER) == ["legal"] and not LG.is_expert(k, CLIENT)
    fs = files(k)
    assert "guide/00-index.md" in fs and "public/legal-help.md" in fs and "guide/presets/retainer.md" in fs
    assert any(p.startswith("ref/") for p in fs)


def test_every_document_fits_the_lookup_budget_as_dir_read_shows_it(k):
    budget = CX.cfg(k)["budgets"]["lookup"]
    assert LG.DOC_BUDGET <= budget
    for p in files(k):
        out = DR.dir_read(k, LAWYER, path=p, dir="legal")
        assert LG.tokens(out) <= LG.DOC_BUDGET, (p, LG.tokens(out))
        assert CX.clip(out, budget)[0] == out, p                        # never cut when fetched as a look-up


def test_the_index_lists_every_document_and_the_whole_archive_is_modest(k):
    fs = files(k)
    idx = fs["guide/00-index.md"]
    for p in fs:
        if not p.startswith("public/") and p != "guide/00-index.md":
            assert f"- {p}:" in idx, p
    assert sum(LG.tokens(t) for t in fs.values()) < 20000


def test_the_archive_is_generated_from_the_engine(k):
    from cybertron import library as LB
    from cybertron import standing as SD
    fs = files(k)
    for name in SD.PRESETS:                                             # a file per preset, with its legs and terms
        doc = fs[f"guide/presets/{LG._slug(name)}.md"]
        assert doc.startswith(f"# Preset: {name}")
        for leg in SD.PRESETS[name]["params"]["LEGS"]:
            assert f"{leg['id']}: " in doc
    for key in SD.BASE:                                                 # every parameter, with its comment from the source
        assert re.search(rf"^- {key} = .+: \S", fs["guide/06-standing.md"], re.M), key
    est = fs["guide/10-templates-laws.md"] + fs["guide/11-templates-contracts.md"]
    for n, e in LB.ESTABLISHED.items():
        if not SD.is_preset(n):
            assert f"- {n} (" in est, n
    assert "set_court_rule" in "".join(t for p, t in fs.items() if p.startswith("ref/court-rules"))


def test_the_archive_is_deterministic(k):
    k2 = Kernel(GN.generate(S.load(SPEC), 1))                           # written at install, before any setup
    assert files(k2) == files(k)


def _blocks(text):
    return re.findall(r"```python\n(.*?)```", text, re.S)


def test_every_code_example_in_the_archive_is_a_listed_example(k):
    fs = files(k)
    shown = [b for t in fs.values() for b in _blocks(t)]
    c = LG.Ctx(k, "legal", {"name": LG.SEED})
    ex = [e["code"] for e in LG.examples(c)]
    assert shown and all(b in ex for b in shown) and all(e in shown for e in ex)


def test_every_law_example_enacts_and_does_what_it_says(k):
    c = LG.Ctx(k, "legal", {"name": LG.SEED})
    for e in LG.examples(c):
        L.check(e["code"], v2=True)
        if e["kind"] != "law":
            continue
        lid = k.new_law(e["code"], LAWYER)
        k.enact(lid)
        assert k.w["laws"][lid]["status"] == "active", (e["id"], k.w["laws"][lid]["status"])
        effects = [x["data"] for x in k.events if x["type"] == "law_effect" and x["data"]["law"] == lid]
        assert effects and not effects[-1]["failed_calls"], (e["id"], effects)
        assert not [x for x in k.events if x["type"] == "law_expectation_failed" and x["data"].get("law") == lid], e["id"]
    from cybertron import institutions as IN
    assert IN.holders(k, "J0", c.office) == [c.appointee]                 # the reseat example moved the office
    assert any(cid.endswith(":store_theft") for cid in k.w["clauses"])   # the clause example declared a clause
    assert any(key == "statute:ordinary" for key in k.w["procedures"])   # the procedure example set a ranked procedure


def test_the_guild_example_founds_an_institution_with_an_office(k):
    c = LG.Ctx(k, "legal", {"name": LG.SEED})
    guild = next(e for e in LG.examples(c) if e["id"] == "guild")
    out = act(k, "Orrin", "create_contract", name="Carters Guild", code=guild["code"])
    cid = re.search(r"A\d+", out).group()
    from cybertron import institutions as IN
    assert IN.holders(k, cid, "warden") == ["Orrin"]


def test_the_allow_example_opens_an_office_controlled_store():
    """The pitfall it fixes (usability round 2): with office control, a councillor is refused until a law of the store's owner
    returns an explicit allow."""
    sp = S.load("cybertron/specs/usability/v3/laws.yaml")
    sp["directories"] = {"enabled": True, "stores": {"legal": {"owner": "agent:Ada", "seed": "legal_archive"}}}
    k = setup_kernel(sp)
    k.start_round()
    from cybertron import institutions as IN
    council = IN.holders(k, "J0", "council")
    who = next(a for a in council if a not in IN.holders(k, "J0", "keeper"))
    c = LG.Ctx(k, "legal", {"name": LG.SEED})
    assert c.council == "council" and c.store_id == "S1"
    allow = next(e for e in LG.examples(c) if e["id"] == "allow")

    def enact(code):
        lid = k.new_law(code, "Ada")
        k.enact(lid)
        assert k.w["laws"][lid]["status"] in ("active", "enacted_repeal"), k.w["laws"][lid]["status"]
        return lid

    def repeal(target):
        enact(f'title = "Repeal of {target}"\nintent = "r"\ndef on_enact():\n    repeal("{target}")\n')

    lid = enact(allow["code"])
    with pytest.raises(ActionError, match="Granary Ration"):          # another law's block still wins (any_block): pitfall 7
        act(k, who, "withdraw", store="S1", qty=1)
    repeal(lid)
    repeal("Granary Ration")
    with pytest.raises(ActionError, match="office controlling store S1"):   # the office-control gate alone refuses
        act(k, who, "withdraw", store="S1", qty=1)
    enact(allow["code"])
    before = k.bal(who, "food")
    act(k, who, "withdraw", store="S1", qty=1)                          # with the explicit allow the councillor draws
    assert k.bal(who, "food") > before


# ---------------------------------------------------------------------- reading: the lawyer in a turn and in the DM step
def test_the_lawyer_reads_the_archive_as_an_action_a_lookup_and_in_the_dm_step(k):
    assert {"dir_read", "dir_list", "dir_search", "draft"} <= available(k, LAWYER)
    assert act(k, LAWYER, "dir_read", dir="legal", path="guide/01-system.md").startswith("legal/guide/01-system.md")
    assert "Ranks, highest first" in CX.lookup(k, LAWYER, "dir_read", {"dir": "legal", "path": "guide/01-system.md"})
    out = CX.dm_step_lookup(k, LAWYER, {"lookup": "dir_read", "args_json": json.dumps({"dir": "legal", "path": "guide/09-pitfalls.md"})})
    assert "Common pitfalls" in out
    assert "bond" in CX.lookup(k, LAWYER, "dir_search", {"dir": "legal", "query": "bond"}).lower()
    turn = DR.turn_section(k, LAWYER)
    assert "legal (the legal archive; yours" in turn and "guide/00-index.md" in turn


def test_non_lawyers_read_only_the_public_guide(k):
    assert "draft" not in available(k, CLIENT) and "dir_read" in available(k, CLIENT)
    assert "Getting legal help" in CX.lookup(k, CLIENT, "dir_read", {"dir": "legal", "path": "public/legal-help.md"})
    with pytest.raises(ActionError, match="no read access"):
        act(k, CLIENT, "dir_read", dir="legal", path="guide/01-system.md")
    assert "guide/" not in DR.dir_list(k, CLIENT, dir="legal")
    with pytest.raises(ActionError):
        act(k, CLIENT, "draft", template="Retainer")
    with pytest.raises(ActionError, match="read-only"):
        act(k, LAWYER, "dir_write", dir="legal", path="guide/01-system.md", text="x")
    a = next(x for x in k.inst["agents"] if x["id"] == CLIENT)
    assert DR.static_access(k.inst, a)                                  # the public grant is known before the kernel exists
    assert not AR._need(k.inst, a, a.get("rights", []), "lawyer:expert")


# ---------------------------------------------------------------------- the draft action and filing by reference
def test_a_retainer_drafted_for_a_new_client_is_founded_by_reference_and_makes_counsel(k):
    out = act(k, LAWYER, "draft", template="Retainer", parties={"Orrin": "client", LAWYER: "counsel"}, terms={"fee": 1},
              **{"for": "Orrin"})
    ref = re.search(r"legal/drafts/\S+\.py", out).group()
    assert "Shared (read) with Orrin" in out and "create_contract" in out and "8," not in out.split("Draft saved")[0]
    assert "preview_law" in out and "fee=1" in out
    assert LG.with_draft(k, "Orrin", {"draft": ref, "scenario": "none"})["code"].startswith("title = 'Retainer'")
    with pytest.raises(ActionError, match="cannot read"):
        act(k, "Hale", "create_contract", name="x", draft=ref)          # not shared with Hale
    got = act(k, "Orrin", "create_contract", name="Retainer (Orrin)", draft=ref)
    cid = re.search(r"A\d+", got).group()
    act(k, LAWYER, "join_contract", contract=cid)
    assert "Orrin" in CN.clients_of(k, LAWYER) and "represent" in available(k, LAWYER)


def test_a_template_law_is_drafted_and_proposed_by_reference(k):
    out = act(k, LAWYER, "draft", template="recall act", params={"RIGHT": "J0.judge", "ACTION": "petition_recall_judge"},
              **{"for": [CLIENT]})
    ref = re.search(r"legal/drafts/\S+\.py", out).group()
    assert "Recall Act, a law" in out and "propose {\"draft\"" in out
    prev = CX.lookup(k, CLIENT, "preview_law", {"draft": ref, "scenario": "none"})   # preview_law reads a draft too
    assert prev.startswith("Preview of 'Recall Act'"), prev[:200]
    res = act(k, CLIENT, "propose", draft=ref, intent="recall the judge by petition")
    lid = max((x for x in k.w["laws"] if x.startswith("L")), key=lambda x: int(x[1:]))
    assert "Recall Act" in k.w["laws"][lid]["code"] and "petition_recall_judge" in k.w["laws"][lid]["code"], res


def test_a_roster_preset_is_drafted_with_the_world_s_leg_mode(k):
    out = act(k, LAWYER, "draft", template="Supply Contract", roster={"Bryn": {"qty": 2}}, params={"OFFICE": "director"},
              name="extra supply")
    ref = re.search(r"legal/drafts/\S+\.py", out).group()
    code = LG.read_draft(k, LAWYER, ref)
    assert "MODE = 'manual'" in code and "'Bryn': {'qty': 2}" in code and "propose_contract_change" in out
    with pytest.raises(ActionError, match="no template"):
        act(k, LAWYER, "draft", template="Nonesuch")
    with pytest.raises(ActionError, match="presets"):
        act(k, LAWYER, "draft", template="Recall Act", terms={"fee": 1})


# ---------------------------------------------------------------------- opt-in: nothing changes without an archive
def test_without_an_archive_nothing_exists():
    k = Kernel(GN.generate(S.load("cybertron/specs/regimes/private.yaml"), 1))
    k.start_round()
    assert not LG.on(k) and "draft" not in available(k, LAWYER)
    with pytest.raises(ActionError, match="unknown action 'draft'") as e:
        act(k, LAWYER, "draft", template="Retainer")
    assert "draft" not in str(e.value).split("Actions:")[1].split(", ")
    with pytest.raises(ActionError):                                    # a "draft" argument is not read as a file
        act(k, CLIENT, "create_contract", name="x", draft="legal/drafts/x.py")
    assert "dirs" not in k.w
