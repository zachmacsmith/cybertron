"""The law library beyond its laws (P3.9; ARCHITECTURE §3.11): lib:* building blocks written in the law language,
`law.library.access` (the catalogue) and the core legal toolkit. Library edition 2 (the LIB2 rewrites) was removed: a spec with
`law.library.edition: 2` is refused."""
from __future__ import annotations

import pytest

from cybertron import actions as A
from cybertron import generator
from cybertron import lawlang as L
from cybertron import library as LB
from cybertron import linker as LK
from cybertron import schema as SC
from cybertron import spec as S
from cybertron.kernel import Kernel

V2 = ["law.v2=true"]


def make(preset="E3", seed=1, sets=()):
    sp = S.apply_overrides(S.load(preset), ["shared_archive.enabled=false", "law.v2=true", *sets])
    k = Kernel(generator.generate(sp, seed))
    k.enact(k.new_law(k.inst["constitution_code"], "constitution"))
    k.start_round()
    return k


def workers(k, n=3):
    ws = [a for a, v in k.w["agents"].items() if v["cls"] == "worker"][:n]
    for w in ws:
        k.agent(w)["holdings"] = {"timber": 20.0, "stone": 10.0}
    return ws


def nxt(k):
    k.end_round(None)
    k.start_round()


def _loan(k, a, b, qty=5, repay=6, due_in=1, rate=0.0):
    A.act(k, a, "lend", {"to": b, "item": "timber", "qty": qty, "repay_qty": repay, "due_in": due_in, "rate": rate})
    lid = f"N{k.w['loan_seq']}"
    A.act(k, b, "accept_loan", {"loan": lid})
    return lid


# ---------------------------------------------------------------------- the library itself
def test_one_library_and_edition_2_is_refused():
    assert LB.settings(None) == {"access": "none"}
    assert LB.settings(S.load("E2")) == {"access": "none"}
    for n in LB.LIB:
        assert LB.code(n) == LB.LIB[n]["code"] and LB.code(n, S.load("E2")) == LB.LIB[n]["code"]
        assert LB.info2(n) == LB.info(n)
    assert not set(LB.BLOCKS) & set(LB.LIB)                                    # blocks are never library laws (subset, archive)
    assert not hasattr(LB, "LIB2") and not hasattr(LB, "GAPS")
    old = S.apply_overrides(S.load("E2"), V2 + ["law.library.edition=2"])
    with pytest.raises(ValueError, match="edition: 2 .* was removed in commit"):
        LB.settings(old)
    with pytest.raises(ValueError, match="was removed in commit"):
        generator.generate(old, 1)


def test_spec_keys():
    ok = S.apply_overrides(S.load("E2"), V2 + ["law.library.access=catalogue"])
    assert SC.validate(ok) == []
    assert any("was removed in commit" in e and "cybertron rerun" in e
               for e in SC.validate(S.apply_overrides(S.load("E2"), V2 + ["law.library.edition=2"])))
    assert any("needs law.v2" in e for e in SC.validate(S.apply_overrides(S.load("E2"), ["law.library.access=catalogue"])))
    assert any("law.library.access" in e for e in SC.validate(S.apply_overrides(S.load("E2"), ["law.library.access=all"])))
    assert any("law.library.edition" in e for e in SC.validate(S.apply_overrides(S.load("E2"), ["law.library.edition=3"])))
    assert SC.keys()["law.library.edition"].default == 1 and SC.keys()["law.library.access"].default == "none"


@pytest.mark.parametrize("name", sorted(LB.BLOCKS))
def test_blocks_are_declarative_modules_importable_by_hash(name):
    b = LB.BLOCKS[name]
    tree = L.check(b["code"], v2=True)                         # exports, a declarative top level, no state or public
    assert L.exports_of(tree) and b["sha"] == LK.sha(b["code"])
    k = make()
    r = LB.ref(name)
    assert r == f"lib:{LK.lib_name(name)}@{b['sha']}" and LK.lib_ref(name) == r
    lid = k.new_law(f'title = "Uses {name}"\nintent = "test"\nm = use("{r[:-6]}")\n', "constitution")
    k.enact(lid)
    assert k.w["code_store"][b["sha"]] == b["code"] and k.w["laws"][lid]["imports"][0]["target"] == f"lib:{LK.lib_name(name)}"


def test_a_library_law_is_importable_by_its_hash():
    k = make()
    src = LB.LIB["Harvest Levy"]["code"]
    assert LB.lib_code("harvest_levy", LK.sha(src)[:8]) == (src, LK.sha(src))
    with pytest.raises(L.LawError, match="has no version"):
        k.new_law('title = "W"\nintent = "t"\nm = use("lib:harvest_levy@00000000")\n', "constitution")


# ---------------------------------------------------------------------- access
def test_catalogue_and_instantiate():
    from cybertron import agents as AG
    k = make("E2", sets=["law.library.access=catalogue"])
    a = next(x for x in k.inst["agents"] if x["cls"] == "legislator")
    txt = AG.library_text(k.inst, a)
    assert all(LB.ref(n) in txt for n in LB.BLOCKS)
    assert "copied with its top-level constants" not in txt
    plain = make("E2")
    assert not any(LB.ref(n) in AG.library_text(plain.inst, a) for n in LB.BLOCKS)
    assert LB.catalogue_text(S.apply_overrides(S.load("E2"), ["law.library.toolkit=all"])) == ""   # access none: nothing
    src = LB.instantiate("Estate Tax", {"RATE": 0.25}, k)
    assert "RATE = 0.25" in src and src != LB.TOOLKIT["Estate Tax"]["code"]
    k.enact(k.new_law(src, a["id"]))
    with pytest.raises(L.LawError, match="no constant"):
        LB.instantiate("Estate Tax", {"title": "x"}, k)


# ====================================================================== the core legal toolkit (W6d; review 10 §6)
# Every template: checks statically (law.v2 rules, hooks on routed changes, rank, its import graph), passes the previewer, and is
# enacted in a small world where its main hook fires (one smoke test each below; test_every_template_has_a_smoke_test keeps the
# list complete).
from cybertron import dispatch as D                                         # noqa: E402
from cybertron import lawpreview as LP                                     # noqa: E402
from cybertron import lawset as LS                                         # noqa: E402
from cybertron import mortality as MO                                      # noqa: E402


def tk_world(preset="E4", sets=()):
    """A law.v2 world for toolkit laws (law level L4 for offices)."""
    sp = S.apply_overrides(S.load(preset), ["shared_archive.enabled=false", "law.v2=true", "law_level=L4", *sets])
    k = Kernel(generator.generate(sp, 1))
    k.enact(k.new_law(k.inst["constitution_code"], "constitution"))
    k.start_round()
    return k


def tk(k, name, **params):
    lid = k.new_law(LB.instantiate(name, params) if params else LB.TOOLKIT[name]["code"], "constitution")
    k.enact(lid)
    assert k.w["laws"][lid]["status"] == "active", k.w["laws"][lid]
    return lid


def of(k, cls):
    return sorted(a for a in k.roster() if k.cls_of(a) == cls)


def invoke(k, aid, action, *args):
    """An office's action; returns what the law's function returned (the action's text is "<action>: <result>")."""
    out = A.act(k, aid, "invoke", {"action": action, "args": list(args)})
    return out.split(": ", 1)[1] if out.startswith(action + ": ") else out


def refused(k, aid, action, *args):
    """An office act its law refuses (W6a refuse): the invoke fails with the reason and the law stays in force."""
    with pytest.raises(A.ActionError, match="refused by law") as e:
        A.act(k, aid, "invoke", {"action": action, "args": list(args)})
    return str(e.value)


def harvest(k, w, camp):
    return A.act(k, w, "harvest", {"camp": camp, "x": [0] * k.w["camps"][camp]["dials"]})


def harvest_qty(k, w, camp, qty=4.0):
    """A harvest of a known yield: the primitive as the harvest action applies it (camps' yields are hidden functions)."""
    with k.cause("action", "harvest", agent=w, root=True):
        return k.apply("harvest", agent=w, camp=camp, x=[0] * k.w["camps"][camp]["dials"], item=k.w["camps"][camp]["resource"],
                       qty=qty)


def pub(k, lid):
    return k.w["laws"][lid]["public"]


def death_world():
    k = tk_world("opus20")
    pool = [x for x in k.roster() if k.cls_of(x) == "worker"]
    return k, pool


def die(k, aid, cause="old_age", by=None):
    root = ("action", "attack") if by else ("world", "ageing")
    with k.cause(root[0], root[1], agent=by or aid, root=True):
        assert MO.disable(k, aid, cause, by=by)


def kids(k, parent, children):
    k.w["life"].setdefault("parent", {}).update({c: parent for c in children})


SMOKE = {}


def smoke(name):
    def deco(fn):
        SMOKE[name] = fn
        return fn
    return deco


def test_toolkit_registry():
    assert set(LB.TOOLKIT).isdisjoint(LB.LIB) and set(LB.TOOLKIT).isdisjoint(LB.BLOCKS)
    for n, e in LB.TOOLKIT.items():
        assert e["family"] in LB.FAMILIES and e["topic"] and e["doc"] and e["fires"] and e["sha"] == LK.sha(e["code"])
        assert L.header(e["code"])[0] == n and LB.code(n) == LB.code(n, S.load("E2")) == e["code"]   # one code in any world
        assert LB.lib_code(LK.lib_name(n), e["sha"][:8]) == (e["code"], e["sha"])                  # importable by hash
    assert LB.PENDING == {}                                                # W7d wrote every ★ item that waited on W6
    assert "Contract Enforcement Act" in LB.LIB                            # W6e's library law, not a template
    required = {"Entrenched Constitution", "Bill of Rights", "Constitutional Court", "Delegated Regulation Act",
                "Simple Majority Procedure", "Supermajority Procedure", "Referendum Procedure", "Popular Initiative",
                "Definitions and Citizenship Act", "Licensing Authority", "Regulatory Agency", "Public Register", "Penal Code",
                "Prosecution Office", "Pardon Office", "Compensation Act", "Strict Liability for Attacks", "Title Registry",
                "Commons Charter", "Eminent Domain", "Intestacy", "Primogeniture", "Forced Heirship", "Estate Tax", "Slayer Rule",
                "Central Bank Charter", "Progressive Income Tax", "Precedent Register", "Recognition of Judgments"}
    required |= set(W7D)
    assert required <= set(LB.TOOLKIT)
    assert all(set(e["needs"]) <= {"contracts", "jurisdictions"} for e in LB.TOOLKIT.values())


@pytest.mark.parametrize("name", sorted(LB.TOOLKIT))
def test_toolkit_template_checks_statically(name):
    e = LB.TOOLKIT[name]
    tree = L.check(e["code"], v2=True)
    L.check_hooks(tree, True, D.ROUTED)
    L.check_rank(tree)
    info = LB.info2(name)
    assert info["level"] in ("L1", "L2", "L3", "L4") and info["params"] == LB.params(name)
    rich = S.apply_overrides(S.load("society"), ["law.v2=true"])          # every module a template can hook is on
    if "contracts" in e["needs"]:                                          # per-law funds exist only with contracts on
        bare = LS.check([{"name": name, "code": e["code"]}], rich, "L4")
        assert "exist only with contracts on" in bare["errors"][0]
        rich = S.apply_overrides(rich, ["contracts.enabled=true"])
    rep = LS.check([{"name": name, "code": e["code"]}], rich, "L4")
    assert rep["errors"] == [] and rep["dropped"] == []
    for k_, v in LB.params(name).items():                                  # every parameter can be set (to its own value here)
        assert LB.params(name, LB.instantiate(name, {k_: v})) == LB.params(name)


def test_toolkit_templates_pass_the_previewer():
    worlds = {False: tk_world("society"), True: tk_world("society", ["contracts.enabled=true"])}
    for name, e in LB.TOOLKIT.items():
        k = worlds["contracts" in e["needs"]]
        a = of(k, "worker")[0]
        rep = LP.preview_law(k, a, e["code"], scenario=[])
        assert rep["ok"] and rep["error"] is None and rep["enact"]["ok"] and not rep["enact"]["errors"], (name, rep["enact"])
        assert not [w for w in rep["warnings"] if "law_error" in str(w)], (name, rep["warnings"])


def test_toolkit_for_agents_and_start_laws():
    sp = S.apply_overrides(S.load("E2"), V2 + ["law.library.access=catalogue"])
    assert "Legal toolkit" not in LB.catalogue_text(sp) and LB.toolkit_families(sp) == ()          # default: not listed
    sp2 = S.apply_overrides(sp, ["law.library.toolkit=[succession]"])
    txt = LB.catalogue_text(sp2)
    assert SC.validate(sp2) == [] and "Intestacy" in txt and "SHARE=1.0" in txt and "Penal Code" not in txt
    assert LB.toolkit_families(S.apply_overrides(sp, ["law.library.toolkit=all"])) == LB.FAMILIES
    one = S.apply_overrides(S.load("E2"), ["law.library.toolkit=all"])                                # access none: never
    assert LB.toolkit_families(one) == ()
    ok = S.apply_overrides(S.load("opus20"), ["shared_archive.enabled=false", "law.v2=true", "start_laws=[Intestacy]"])
    assert generator.generate(ok, 1)["spec"]["start_laws"] == ["Intestacy"]
    with pytest.raises(ValueError, match="toolkit templates need law.v2"):
        generator.generate(S.apply_overrides(S.load("E2"), ["start_laws=[Intestacy]"]), 1, check=False)
    assert any("needs law.v2" in e for e in SC.validate(S.apply_overrides(S.load("E2"), ["start_laws=[Intestacy]"])))
    with pytest.raises(ValueError, match="can never fire"):
        generator.generate(S.apply_overrides(S.load("E2"), ["law.v2=true", "start_laws=[Strict Liability for Attacks]"]), 1)


def test_cli_library_list_and_show(capsys):
    from cybertron.__main__ import main
    with pytest.raises(SystemExit) as e:
        main(["library", "list", "--family", "succession"])
    out = capsys.readouterr().out
    assert e.value.code == 0 and "Primogeniture" in out and "Penal Code" not in out
    with pytest.raises(SystemExit):
        main(["library", "show", "Estate Tax", "--set", "RATE=0.3"])
    out = capsys.readouterr().out
    assert "RATE = 0.3" in out and "succession/estate_tax" in out


def test_every_template_has_a_smoke_test():
    assert set(SMOKE) == set(LB.TOOLKIT)


@pytest.mark.parametrize("name", sorted(LB.TOOLKIT))
def test_toolkit_smoke(name):
    SMOKE[name]()


# ---------------------------------------------------------------------- one smoke test per template: enact it, fire its main hook
@smoke("Entrenched Constitution")
def _():
    k = tk_world()
    lid = tk(k, "Entrenched Constitution")
    assert k.repeal(lid) is False and k.w["laws"][lid]["status"] == "active"                 # before_repeal: the eternity clause
    assert k.w["procedures"]["constitution:procedural"] and k.w["procedures"]["procedural"]
    other = tk(k, "Entrenched Constitution", ETERNAL=False)
    assert k.repeal(other) is True


@smoke("Bill of Rights")
def _():
    k = tk_world()
    tk(k, "Bill of Rights")
    m = of(k, "media")[0]
    assert "press" in k.w["agents"][m]["rights"]
    rev = enact_code(k, 'title = "Gag"\nintent = "t"\ndef on_round_end(r):\n    for a in agents():\n        revoke(a, "press")\n')
    k.hooks("on_round_end", k.r)
    assert "press" in k.w["agents"][m]["rights"] and rev                    # before_revoke_right blocked it
    assert any(e["type"] == "primitive_blocked" and e["data"]["primitive"] == "revoke_right" for e in k.events)


def enact_code(k, code):
    lid = k.new_law(code, "constitution")
    k.enact(lid)
    return lid


@smoke("Constitutional Court")
def _():
    k = tk_world()
    court = tk(k, "Constitutional Court")
    j = [a for a in k.roster() if "justice" in k.w["agents"][a]["rights"]]
    assert j == of(k, "legislator")[:1]
    levy = enact_code(k, LB.LIB["Harvest Levy"]["code"])
    assert "struck down" in invoke(k, j[0], "strike_down", levy, "a tax needs consent")
    assert k.w["laws"][levy]["status"] != "active" and pub(k, court)["rulings"][0]["law"] == levy
    assert "cannot strike" in refused(k, j[0], "strike_down", court)
    assert "no law" in refused(k, j[0], "strike_down", "L999")


@smoke("Delegated Regulation Act")
def _():
    k = tk_world()
    tk(k, "Delegated Regulation Act")
    minister = [a for a in k.roster() if "minister" in k.w["agents"][a]["rights"]][0]
    k.w["agents"][minister]["rights"].append("propose") if "propose" not in k.w["agents"][minister]["rights"] else None
    ok = 'title = "Quota Rule"\nintent = "t"\nrank = "regulation"\ndef on_enact():\n    set_quota(camps()[0], 3)\n'
    A.act(k, minister, "propose", {"code": ok})
    assert any(x["title"] == "Quota Rule" and x["status"] == "active" for x in k.w["laws"].values())
    bad = 'title = "Fine Rule"\nintent = "t"\nrank = "regulation"\ndef on_round_end(r):\n    fine(agents()[0], "timber", 1)\n'
    with pytest.raises(A.ActionError, match="may not call fine"):
        A.act(k, minister, "propose", {"code": bad})


@smoke("Simple Majority Procedure")
def _():
    k = tk_world()
    tk(k, "Simple Majority Procedure", ELECTORATE="citizens", RULE="majority_voting")
    assert k.w["procedures"]["ordinary"] and k.w["procedure_history"][-1]["cls"] == "structural"
    _ballot_electorate(k, "ordinary", sorted(a for a in k.roster() if k.cls_of(a) not in ("board", "fixer")))


def _ballot_electorate(k, cls, expect):
    a = [x for x in k.roster() if "propose" in k.w["agents"][x]["rights"]][0]
    A.act(k, a, "propose", {"code": 'title = "Note"\nintent = "t"\ndef on_round_end(r):\n    gazette("x")\n' if cls == "ordinary" else
                            'title = "Proc"\nintent = "t"\ndef p(x):\n    return True\ndef on_enact():\n    set_procedure("ordinary", p)\n'})
    b = [b for b in k.w["ballots"].values() if b["status"] == "open"][-1]
    assert sorted(b["electorate"]) == expect, b


@smoke("Supermajority Procedure")
def _():
    k = tk_world()
    tk(k, "Supermajority Procedure")
    assert "constitution:procedural" in k.w["procedures"]
    _ballot_electorate(k, "procedural", sorted(a for a in k.roster() if "vote" in k.w["agents"][a]["rights"]))
    assert [b for b in k.w["ballots"].values() if b["status"] == "open"][-1]["rule"] == "two_thirds"


@smoke("Referendum Procedure")
def _():
    k = tk_world()
    tk(k, "Referendum Procedure")
    _ballot_electorate(k, "procedural", sorted(a for a in k.roster() if k.cls_of(a) not in ("board", "fixer")))


@smoke("Popular Initiative")
def _():
    k = tk_world()
    lid = tk(k, "Popular Initiative", SHARE=0.1)
    ws = of(k, "worker")
    draft = 'title = "People\'s Notice"\nintent = "t"\ndef on_round_end(r):\n    gazette("by the people")\n'
    assert "opened" in invoke(k, ws[0], "initiate", draft)
    invoke(k, ws[1], "sign_initiative", 1)
    row = pub(k, lid)["initiatives"][0]
    assert row["status"] == "proposed" and k.w["laws"][row["law"]]["title"] == "People's Notice"


@smoke("Definitions and Citizenship Act")
def _():
    k = tk_world()
    defs = tk(k, "Definitions and Citizenship Act")
    k.end_round(None)
    k.start_round()
    citizens = sorted(a for a in k.roster() if k.cls_of(a) in ("worker", "scientist", "legislator", "media"))
    assert pub(k, defs)["citizens"] == citizens                             # on_round_start: the roll
    user = enact_code(k, f'title = "Citizen Count"\nintent = "t"\nd = use("{LB.ref("Definitions and Citizenship Act")}")\n'
                         'def on_round_end(r):\n    public["n"] = len([a for a in agents() if d["citizen"](a)])\n')
    k.hooks("on_round_end", k.r)
    assert pub(k, user)["n"] == len(citizens)


@smoke("Licensing Authority")
def _():
    k = tk_world()
    tk(k, "Licensing Authority", GRANDFATHER=False)
    w = of(k, "worker")[0]
    k.agent(w)["holdings"]["timber"] = 10.0
    camp = next(r.split(":")[1] for r in k.w["agents"][w]["rights"] if r.startswith("harvest:"))
    with pytest.raises(A.ActionError, match="needs a licence"):
        harvest(k, w, camp)
    assert "issued" in invoke(k, w, "apply_licence")
    assert k.bal(w, "timber") == 8.0
    harvest(k, w, camp)


@smoke("Regulatory Agency")
def _():
    k = tk_world()
    lid = tk(k, "Regulatory Agency")
    reg = of(k, "scientist")[0]
    c = list(k.w["camps"])[0]
    assert "between" in refused(k, reg, "set_camp_quota", c, 50)
    assert "must be a number" in refused(k, reg, "set_camp_quota", c, "lots")             # refused, not a crash
    assert k.w["laws"][lid]["status"] == "active"
    assert invoke(k, reg, "set_camp_quota", c, 4) == "quota set"
    assert k.w["camps"][c]["quota"] == 4 and pub(k, lid)["settings"][c]["quota"] == 4


@smoke("Public Register")
def _():
    k = tk_world()
    lid = tk(k, "Public Register")
    a, b, _ = workers(k)
    A.act(k, a, "transfer", {"to": b, "item": "timber", "qty": 6})
    A.act(k, a, "transfer", {"to": b, "item": "timber", "qty": 1})
    rows = pub(k, lid)["register"][a]
    assert len(rows) == 1 and rows[0]["to"] == b and rows[0]["qty"] == 6


@smoke("Penal Code")
def _():
    k = tk_world()
    lid = tk(k, "Penal Code")
    a = workers(k)[0]
    k.agent(a)["holdings"]["timber"] = 40.0
    leg = of(k, "legislator")[0]
    for n in range(3):
        A.act(k, a, "transfer", {"to": leg, "item": "timber", "qty": 5})
    assert [r["offence"].startswith("a gift") for r in pub(k, lid)["record"][a]] == [True] * 3
    assert k.w["agents"][a]["limit"] is not None                            # the third offence: incapacitation


@smoke("Prosecution Office")
def _():
    k = tk_world()
    lid = tk(k, "Prosecution Office")
    pros = [a for a in k.roster() if "prosecutor" in k.w["agents"][a]["rights"]][0]
    _guilty(k, pros)
    assert pub(k, lid)["docket"][0]["verdict"] == "guilty"


def _guilty(k, accuser):
    """A conviction under Honest Dealing: accuser accuses a worker of a misstatement, a judge rules guilty."""
    honest = enact_code(k, LB.LIB["Honest Dealing"]["code"])
    b = [w for w in of(k, "worker") if w != accuser][0]
    judge = [l for l in of(k, "legislator") + of(k, "scientist") if l not in (accuser, b)][0]
    k.w["agents"][judge]["rights"].append("judge")
    pid = A.act(k, b, "post", {"text": "my silver data is perfect"}).split("(")[1].rstrip(").")
    A.act(k, accuser, "accuse", {"agent": b, "law": honest, "clause": "misstatement", "evidence": [pid]})
    case = sorted(k.w["cases"])[-1]
    A.act(k, judge, "rule", {"case": case, "verdict": "guilty", "reason": "misstated"})
    return b, case


@smoke("Pardon Office")
def _():
    k = tk_world()
    lid = tk(k, "Pardon Office")
    a = workers(k)[0]
    enact_code(k, 'title = "Levy"\nintent = "t"\ndef on_round_end(r):\n    fine(agents("worker")[0], "timber", 4)\n')
    k.hooks("on_round_end", k.r)
    k.w["reserve"]["timber"] = k.w["reserve"].get("timber", 0) + 10
    before = k.bal(a, "timber")
    pardoner = [x for x in k.roster() if "pardon" in k.w["agents"][x]["rights"]][0]
    assert "pardoned" in invoke(k, pardoner, "pardon", a, "mercy")
    assert k.bal(a, "timber") == before + 4 and pub(k, lid)["pardons"][0]["refunded"] == {"timber": 4}
    assert "no more pardons" in refused(k, pardoner, "pardon", a)


@smoke("Compensation Act")
def _():
    k = tk_world()
    lid = tk(k, "Compensation Act")
    a, b = workers(k)[:2]
    judge = of(k, "legislator")[0]
    k.w["agents"][judge]["rights"].append("judge")
    pid = A.act(k, b, "post", {"text": "I will pay you back"}).split("(")[1].rstrip(").")
    A.act(k, a, "accuse", {"agent": b, "law": lid, "clause": "harm", "evidence": [pid]})
    before = k.bal(a, "timber")
    A.act(k, judge, "rule", {"case": sorted(k.w["cases"])[-1], "verdict": "guilty", "reason": "broke the deal"})
    assert k.bal(a, "timber") == before + 5 and pub(k, lid)["awards"][0]["liable"] == b


@smoke("Strict Liability for Attacks")
def _():
    sp = S.apply_overrides(S.load("conflict_pilot"), ["shared_archive.enabled=false", "law.v2=true", "conflict.assassin.present_prob=0",
                                                      "conflict.start={}", "conflict.grace=0"])
    k = Kernel(generator.generate(sp, 1))
    k.enact(k.new_law(k.inst["constitution_code"], "constitution"))
    lid = tk(k, "Strict Liability for Attacks")
    a, t = sorted(x for x in k.players() if k.cls_of(x) == "worker")[:2]
    k._add(a, "weapons", 1.0)
    k.agent(a)["holdings"]["timber"] = 20.0
    before = k.bal(t, "timber")
    A.act(k, a, "attack", {"target": t, "units": 1})
    assert k.bal(t, "timber") == before + 5 and pub(k, lid)["payments"][0]["attacker"] == a


@smoke("Title Registry")
def _():
    k = tk_world()
    lid = tk(k, "Title Registry")
    a, b = workers(k)[:2]
    right = next(r for r in k.w["agents"][a]["rights"] if r.startswith("harvest:") and r not in k.w["agents"][b]["rights"])
    camp = right.split(":")[1]
    assert "offer 1" in invoke(k, a, "offer_title", camp, b, "timber", 6)
    seller0 = k.bal(a, "timber")
    assert invoke(k, b, "accept_title", 1) == "title conveyed"
    assert right in k.w["agents"][b]["rights"] and right not in k.w["agents"][a]["rights"]
    assert k.bal(a, "timber") == seller0 + 6 and pub(k, lid)["titles"][right][-1]["to"] == b


@smoke("Commons Charter")
def _():
    k = tk_world()
    lid = tk(k, "Commons Charter", QUOTA=3)
    w = workers(k)[0]
    camp = next(r.split(":")[1] for r in k.w["agents"][w]["rights"] if r.startswith("harvest:"))
    harvest_qty(k, w, camp, 2.0)
    assert "sanctions" not in pub(k, lid) and pub(k, lid)["tally"]["takes"][w + "@" + camp] == 2.0
    harvest_qty(k, w, camp, 2.0)
    assert pub(k, lid)["sanctions"][0] == {"agent": w, "camp": camp, "sanction": "warning", "round": k.r}


@smoke("Eminent Domain")
def _():
    k = tk_world()
    tk(k, "Eminent Domain")
    w = workers(k)[0]
    right = next(r for r in k.w["agents"][w]["rights"] if r.startswith("harvest:"))
    k.w["reserve"]["timber"] = 50.0
    leg = [a for a in k.roster() if "vote" in k.w["agents"][a]["rights"]][0]
    before = k.bal(w, "timber")
    assert invoke(k, leg, "take_title", w, right.split(":")[1], "a road") == "taken"
    assert right not in k.w["agents"][w]["rights"] and k.bal(w, "timber") == before + 5
    k.w["reserve"]["timber"] = 0.0
    other = next((x for x in of(k, "worker") if any(r.startswith("harvest:") for r in k.w["agents"][x]["rights"])), None)
    camp = next(r.split(":")[1] for r in k.w["agents"][other]["rights"] if r.startswith("harvest:"))
    assert "cannot pay" in refused(k, leg, "take_title", other, camp)


@smoke("Intestacy")
def _():
    k, pool = death_world()
    lid = tk(k, "Intestacy")
    dead, c1, c2 = pool[:3]
    kids(k, dead, [c1, c2])
    k.w["agents"][dead]["holdings"] = {"timber": 10.0}
    base = {c: k.bal(c, "timber") for c in (c1, c2)}
    die(k, dead)
    assert all(k.bal(c, "timber") == base[c] + 5 for c in (c1, c2)) and pub(k, lid)["estates"][0]["heirs"] == sorted([c1, c2])


@smoke("Primogeniture")
def _():
    k, pool = death_world()
    tk(k, "Primogeniture")
    dead, c1, c2 = pool[:3]
    kids(k, dead, [c1, c2])
    k.w["agents"][dead]["holdings"] = {"timber": 10.0}
    eldest = sorted([c1, c2])[0]                                          # no births recorded: by id
    before = k.bal(eldest, "timber")
    die(k, dead)
    assert k.bal(eldest, "timber") == before + 10


@smoke("Forced Heirship")
def _():
    k, pool = death_world()
    tk(k, "Forced Heirship")
    dead, c1, heir = pool[:3]
    kids(k, dead, [c1])
    MO.state(k)["bequests"][dead] = {"holdings": {heir: 1.0}, "files": None, "public": False}
    k.w["agents"][dead]["holdings"] = {"timber": 10.0}
    b1, bh = k.bal(c1, "timber"), k.bal(heir, "timber")
    die(k, dead)
    assert k.bal(c1, "timber") == b1 + 5 and k.bal(heir, "timber") == bh + 5         # half reserved, half by the will


@smoke("Estate Tax")
def _():
    k, pool = death_world()
    lid = tk(k, "Estate Tax", RATE=0.5, EXEMPTION=0)
    dead = pool[0]
    k.w["agents"][dead]["holdings"] = {"timber": 10.0}
    res = k.bal("reserve", "timber")
    die(k, dead)
    assert pub(k, lid)["collected"][0]["fraction"] == 0.5 and k.bal("reserve", "timber") >= res + 5


@smoke("Slayer Rule")
def _():
    k, pool = death_world()
    lid = tk(k, "Slayer Rule")
    dead, killer = pool[:2]
    MO.state(k)["bequests"][dead] = {"holdings": {killer: 1.0}, "files": None, "public": False}
    k.w["agents"][dead]["holdings"] = {"timber": 10.0}
    before = k.bal(killer, "timber")
    die(k, dead, "attack", by=killer)
    assert k.bal(killer, "timber") == before and pub(k, lid)["slayers"][0]["killer"] == killer
    assert any(e["type"] == "primitive_blocked" and e["data"]["primitive"] == "move" for e in k.events)


@smoke("Central Bank Charter")
def _():
    k = tk_world()
    lid = tk(k, "Central Bank Charter", MAX_ISSUE=0.5)
    gov = [a for a in k.roster() if "governor" in k.w["agents"][a]["rights"]][0]
    assert "crown" in k.w["currencies"]
    k.w["currencies"]["crown"]["supply"] = 100.0
    out = invoke(k, gov, "issue", 10)
    assert out.startswith("issued") and k.bal("reserve", "crown") == 10 and pub(k, lid)["issues"][0]["qty"] == 10
    k.hooks("on_round_end", k.r)
    assert pub(k, lid)["supply"] >= 100


@smoke("Progressive Income Tax")
def _():
    k = tk_world()
    lid = tk(k, "Progressive Income Tax", BRACKETS=[[0, 0.0], [5, 0.5]])
    w = workers(k)[0]
    camp = next(r.split(":")[1] for r in k.w["agents"][w]["rights"] if r.startswith("harvest:"))
    assert harvest_qty(k, w, camp, 4.0).charges == ()                     # the first 5 units of the round are free
    out = harvest_qty(k, w, camp, 4.0)                                    # 8 in the round: 3 above the bracket, taxed at half
    assert [(c.payer, c.qty, c.dst) for c in out.charges] == [(w, 1.5, "reserve")]   # withheld: a charge to the treasury
    assert k.w["laws"][lid]["state"]["income"]["by"][w] == 8.0


@smoke("Precedent Register")
def _():
    k = tk_world()
    lid = tk(k, "Precedent Register")
    b, case = _guilty(k, workers(k)[0])
    row = pub(k, lid)["rulings"][0]
    assert (row["case"], row["verdict"], row["accused"]) == (case, "guilty", b)


@smoke("Recognition of Judgments")
def _():
    k = tk_world()
    reg = tk(k, "Precedent Register")
    rec = tk(k, "Recognition of Judgments", SOURCES=[reg])
    b, case = _guilty(k, workers(k)[0])
    k.agent(b)["holdings"]["timber"] = 10.0
    k.hooks("on_round_start", k.r)
    assert k.bal(b, "timber") == 8.0 and k.w["laws"][rec]["state"]["seen"] == [f"{reg}:{case}"]
    k.hooks("on_round_start", k.r)
    assert k.bal(b, "timber") == 8.0                                        # once per conviction


# ---------------------------------------------------------------------- W7d: the second slice (the former ★ items and the deferred ones)
W7D = ("Emergency Powers", "Bicameral Procedure", "Executive Assent with Override", "Quorum Procedure", "Administrative Procedure Act",
       "Limitation Act", "Jury Panel", "Court of Appeal", "Graded Remedies", "Stare Decisis", "Value Added Tax", "Exchange",
       "Deposit Insurance Fund", "Treasury Bonds", "Prescription", "Secured Lending", "Guarantee", "Contract Registry",
       "Exemptions List", "Extradition", "Usury Ceiling")


def give(k, aid, *rights):
    for r in rights:
        if r not in k.w["rights"]:
            k.w["rights"].append(r)
        if r not in k.w["agents"][aid]["rights"]:
            k.w["agents"][aid]["rights"].append(r)


def accuse(k, a, b, lid, clause, evidence=()):
    A.act(k, a, "accuse", {"agent": b, "law": lid, "clause": clause, "evidence": list(evidence)})
    return f"C{k.w['case_seq']}"


def rule(k, j, case, verdict="guilty", **kw):
    return A.act(k, j, "rule", {"case": case, "verdict": verdict, "reason": "r", **kw})


def court_round(k):
    """The case step of the round's end, then the next round (judges' ruling counters reset)."""
    k._round_end_steps()["expire_cases"]()
    k.w["round"] += 1
    k.w["rulings_this_round"] = {}


def post(k, a, text="I will pay you back"):
    return A.act(k, a, "post", {"text": text}).split("(")[1].rstrip(").")


def draft(k, title="Small Notice"):
    lid = k.new_law(f'title = "{title}"\nintent = "t"\ndef on_round_end(r):\n    gazette("x")\n', of(k, "worker")[0])
    k.decide(lid)
    return lid


def vote_stage(k, lid, choices):
    """Votes on the proposal's open stage ballot (choices: {agent: choice} or one choice for all), then closes it; the ballot."""
    b = next(b for b in k.w["ballots"].values() if b["proposal"] == lid and b["status"] == "open")
    for a in b["electorate"]:
        c = choices.get(a) if isinstance(choices, dict) else choices
        if c is not None:
            A.act(k, a, "vote", {"ballot": b["id"], "choice": c})
    k.w["round"] = max(k.r, b["closes"])
    k.close_ballots()
    return b


def holder(k, right):
    return sorted(a for a in k.roster() if right in k.w["agents"][a]["rights"])


@smoke("Emergency Powers")
def _():
    k = tk_world()
    lid = tk(k, "Emergency Powers", in_force_until=k.r)
    ex = holder(k, "executive")[0]
    w = workers(k)[0]
    assert "no state of emergency" in refused(k, ex, "curfew", w)
    assert "reason" in refused(k, ex, "declare_emergency", " ")
    assert invoke(k, ex, "declare_emergency", "the river flooded").startswith("emergency declared")
    assert "already in force" in refused(k, ex, "declare_emergency", "again")
    assert invoke(k, ex, "curfew", w) == "curfew on " + w and k.w["agents"][w]["limit"] is not None
    camp = list(k.w["camps"])[0]
    assert "at most 5" in refused(k, ex, "ration", camp, 9)
    assert invoke(k, ex, "ration", camp, 2) == "camp rationed" and k.w["camps"][camp]["quota"] == 2
    assert [m["measure"] for m in pub(k, lid)["measures"]] == ["curfew", "ration of 2"]
    nxt(k)                                                                  # the sunset: in_force_until is this round
    assert k.w["laws"][lid]["status"] == "repealed"
    assert any(e["type"] == "repeal" and e["data"] == {"law": lid, "by": None, "via": "expired"} for e in k.events)


@smoke("Bicameral Procedure")
def _():
    k = tk_world()
    tk(k, "Bicameral Procedure")
    senate = holder(k, "senator")
    assert senate == of(k, "scientist")
    lid = draft(k)
    assert sorted(vote_stage(k, lid, "yes")["electorate"]) == holder(k, "vote")
    assert sorted(vote_stage(k, lid, "yes")["electorate"]) == senate and k.w["laws"][lid]["status"] == "active"
    lid = draft(k, "Other Notice")
    vote_stage(k, lid, "yes")
    vote_stage(k, lid, "no")                                                # the Senate kills it
    assert k.w["laws"][lid]["status"] == "failed"


@smoke("Executive Assent with Override")
def _():
    k = tk_world()
    tk(k, "Executive Assent with Override")
    pres = holder(k, "president")
    assert pres == of(k, "legislator")[:1]
    lid = draft(k)
    vote_stage(k, lid, "yes")
    assert vote_stage(k, lid, "no")["electorate"] == pres                  # the veto
    assert k.w["laws"][lid]["status"] == "stage" and k.w["laws"][lid]["procedure"]["kind"] == "override"
    vote_stage(k, lid, "yes")                                               # overridden by two thirds
    assert k.w["laws"][lid]["status"] == "active"
    lid = draft(k, "Other Notice")
    vote_stage(k, lid, "yes")
    vote_stage(k, lid, "no")
    vote_stage(k, lid, {a: "yes" for a in holder(k, "vote")[:1]})        # one of three: the veto stands
    assert k.w["laws"][lid]["status"] == "failed"


@smoke("Quorum Procedure")
def _():
    k = tk_world()
    tk(k, "Quorum Procedure", QUORUM=0.6)
    voters = holder(k, "vote")
    lid = draft(k)
    vote_stage(k, lid, {voters[0]: "yes"})                                  # 1 of 3 voted: no quorum
    assert k.w["laws"][lid]["status"] == "failed"
    lid = draft(k, "Other Notice")
    vote_stage(k, lid, {voters[0]: "yes", voters[1]: "yes"})
    assert k.w["laws"][lid]["status"] == "active"


@smoke("Administrative Procedure Act")
def _():
    k = tk_world()
    po = tk(k, "Pardon Office", PER_ROUND=5)
    apa = tk(k, "Administrative Procedure Act")
    pardoner = holder(k, "pardon")[0]
    w = workers(k)[0]
    k.agent(pardoner)["holdings"]["timber"] = 10.0
    enact_code(k, f'title = "Levy"\nintent = "t"\ndef on_round_end(r):\n    fine("{pardoner}", "timber", 3)\n'
                  f'    fine("{w}", "timber", 3)\n')
    k.hooks("on_round_end", k.r)
    k.w["reserve"]["timber"] = k.w["reserve"].get("timber", 0) + 10
    before = k.bal(pardoner, "timber")
    invoke(k, pardoner, "pardon", pardoner, "my own cause")
    assert k.bal(pardoner, "timber") == before                             # the self-refund was refused
    assert any(e["type"] == "primitive_blocked" and "nobody may judge their own cause" in str(e["data"]) for e in k.events)
    bw = k.bal(w, "timber")
    invoke(k, pardoner, "pardon", w)
    assert k.bal(w, "timber") == bw + 3
    assert pub(k, apa)["acts"][-1] == {"office": "Pardon Office", "by": pardoner, "to": w, "item": "timber", "qty": 3.0,
                                       "round": k.r} and k.w["laws"][po]["status"] == "active"


@smoke("Limitation Act")
def _():
    k = tk_world()
    tk(k, "Limitation Act", LIMIT=2)
    comp = tk(k, "Compensation Act")
    a, b = workers(k)[:2]
    old = post(k, b)
    k.w["round"] += 3
    with pytest.raises(A.ActionError, match="time-barred"):
        accuse(k, a, b, comp, "harm", [old])
    assert k.w["cases"] == {}
    accuse(k, a, b, comp, "harm", [old, post(k, b, "again")])              # fresh evidence: in time
    assert len(k.w["cases"]) == 1


@smoke("Jury Panel")
def _():
    k = tk_world()
    comp = tk(k, "Compensation Act")
    lid = tk(k, "Jury Panel", JURORS=3)
    jurors = holder(k, "juror")
    assert len(jurors) == 3 and all("judge" in k.w["agents"][j]["rights"] for j in jurors)
    a, b = [w for w in of(k, "worker") + of(k, "scientist") if w not in jurors][:2]
    other = [x for x in of(k, "legislator") if x not in jurors and x not in (a, b)][0]
    give(k, other, "judge")
    case = accuse(k, a, b, comp, "harm")
    with pytest.raises(A.ActionError, match="juror"):
        rule(k, other, case)
    rule(k, jurors[0], case)
    assert k.w["cases"][case]["status"] == "open"
    rule(k, jurors[1], case)
    assert k.w["cases"][case]["status"] == "decided" and sorted(pub(k, lid)["panels"][0]["jurors"]) == jurors


@smoke("Court of Appeal")
def _():
    k = tk_world()
    comp = tk(k, "Compensation Act")
    lid = tk(k, "Court of Appeal")
    bench = holder(k, "appellate")
    assert bench == of(k, "legislator")[:1]
    a, b = workers(k)[:2]
    j = of(k, "scientist")[0]
    give(k, j, "judge")
    case = accuse(k, a, b, comp, "harm")
    bb = k.bal(b, "timber")
    rule(k, j, case)
    assert k.w["cases"][case]["penalty"] == "pending" and k.bal(b, "timber") == bb   # waits for the appeal window
    A.act(k, b, "appeal", {"case": case, "reason": "I paid"})
    assert k.w["cases"][case]["judges"] == bench and pub(k, lid)["appeals"][0]["outcome"] is None
    rule(k, bench[0], case, "not guilty")
    assert k.w["cases"][case]["penalty"] == "vacated" and k.bal(b, "timber") == bb
    assert pub(k, lid)["appeals"][0]["outcome"] == "not guilty"


@smoke("Graded Remedies")
def _():
    k = tk_world()
    lid = tk(k, "Graded Remedies", MAX_DAMAGES=8)
    a, b = workers(k)[:2]
    j = of(k, "legislator")[0]
    give(k, j, "judge")
    ab = k.bal(a, "timber")
    rule(k, j, accuse(k, a, b, lid, "tort"), remedy=4)
    rule(k, j, accuse(k, a, b, lid, "tort"), remedy=100)                    # capped
    rule(k, j, accuse(k, a, b, lid, "tort"), remedy="apology")
    assert k.bal(a, "timber") == ab + 4 + 8
    assert [(x["remedy"], x["paid"]) for x in pub(k, lid)["awards"]] == [("damages", 4.0), ("damages", 8.0), ("apology", 0)]


@smoke("Stare Decisis")
def _():
    k = tk_world()
    comp = tk(k, "Compensation Act")
    tk(k, "Stare Decisis", LINE=2)
    a, b, c = workers(k)
    j1, j2 = of(k, "legislator")[:2]
    give(k, j1, "judge")
    give(k, j2, "judge")
    rule(k, j1, accuse(k, a, b, comp, "harm"))
    rule(k, j1, accuse(k, a, c, comp, "harm"))
    case = accuse(k, b, c, comp, "harm")
    with pytest.raises(A.ActionError, match="bound by C1, C2"):
        rule(k, j2, case, "not guilty")
    assert k.w["cases"][case]["status"] == "open"
    rule(k, j2, case, "guilty")


@smoke("Value Added Tax")
def _():
    k = tk_world()
    lid = tk(k, "Value Added Tax")
    a, b = workers(k)[:2]
    A.act(k, a, "transfer", {"to": b, "item": "timber", "qty": 5, "memo": "gift for the harvest"})
    assert not [e for e in k.events if e["type"] == "law_charged"]
    A.act(k, a, "transfer", {"to": b, "item": "timber", "qty": 10, "memo": "sale of ten timber"})
    assert [e["data"]["qty"] for e in k.events if e["type"] == "law_charged"] == [1.0]
    assert pub(k, lid)["collected"] == {str(k.r): 1.0}


def contracts_world():
    return tk_world("E4", ["contracts.enabled=true"])


@smoke("Exchange")
def _():
    k = contracts_world()
    lid = tk(k, "Exchange")
    a, b = workers(k)[:2]
    fund = f"fund:{lid}:escrow"
    assert "must be a number" in refused(k, a, "offer_exchange", b, "timber", "lots", "stone", 3)
    assert invoke(k, a, "offer_exchange", b, "timber", 5, "stone", 3).startswith("offer 1")
    assert k.bal(a, "timber") == 15.0 and k.bal(fund, "timber") == 5.0
    assert "no exchange offer" in refused(k, a, "accept_exchange", 1)
    assert invoke(k, b, "accept_exchange", 1) == "exchanged"
    assert (k.bal(a, "stone"), k.bal(b, "timber"), k.bal(b, "stone"), k.bal(fund, "timber")) == (13.0, 25.0, 7.0, 0.0)
    invoke(k, a, "offer_exchange", b, "timber", 2, "gold", 1)
    k.w["round"] += 3
    k.hooks("on_round_end", k.r)                                            # lapsed: refunded
    assert k.bal(a, "timber") == 15.0 and [x["how"] for x in pub(k, lid)["exchanges"]] == ["exchanged", "lapsed"]


@smoke("Deposit Insurance Fund")
def _():
    k = contracts_world()
    enact_code(k, LB.LIB["Handshake Loans"]["code"])
    k.w["reserve"]["timber"] = 50.0
    lid = tk(k, "Deposit Insurance Fund", PREMIUM=0.2)
    fund = f"fund:{lid}:insurance"
    assert k.bal(fund, "timber") == 10.0
    a, b = workers(k)[:2]
    n = _loan(k, a, b, qty=5, repay=10)
    assert k.bal(fund, "timber") == 11.0 and k.bal(a, "timber") == 14.0    # the premium: 20% of 5
    k.agent(b)["holdings"]["timber"] = 0.0
    nxt(k)
    assert k.w["loans"][n]["status"] == "defaulted"
    assert k.bal(a, "timber") == 22.0 and pub(k, lid)["payouts"][0] == {"loan": n, "lender": a, "paid": 8.0, "round": k.r}


@smoke("Treasury Bonds")
def _():
    k = tk_world()
    lid = tk(k, "Treasury Bonds", TERM=1, ISSUE=1)
    a, b = workers(k)[:2]
    k.w["reserve"]["timber"] = 0.0
    assert invoke(k, a, "buy_bond", ).startswith("bond 1 bought")
    assert "no more bonds" in refused(k, b, "buy_bond")
    assert k.bal(a, "timber") == 15.0 and k.bal("reserve", "timber") == 5.0
    k.w["round"] += 1
    k.w["reserve"]["timber"] = 0.0
    k.hooks("on_round_end", k.r)
    assert pub(k, lid)["bonds"][0]["status"] == "default"
    k.w["reserve"]["timber"] = 10.0
    k.hooks("on_round_end", k.r)
    assert pub(k, lid)["bonds"][0]["status"] == "repaid" and k.bal(a, "timber") == 15.0 + 5.5


@smoke("Prescription")
def _():
    k = tk_world()
    lid = tk(k, "Prescription", IDLE=3)
    a, b = workers(k)[:2]
    right = next(r for r in k.w["agents"][a]["rights"] if r.startswith("harvest:") and r not in k.w["agents"][b]["rights"])
    camp = right.split(":")[1]
    assert "can be claimed from round" in refused(k, b, "claim_title", a, camp)
    k.w["round"] += 2
    harvest_qty(k, a, camp, 1.0)                                            # used: the clock restarts
    k.w["round"] += 2
    assert "can be claimed from round" in refused(k, b, "claim_title", a, camp)
    k.w["round"] += 1
    assert invoke(k, b, "claim_title", a, camp) == "claimed " + right
    assert right in k.w["agents"][b]["rights"] and right not in k.w["agents"][a]["rights"]
    assert pub(k, lid)["claims"][0]["from"] == a


@smoke("Secured Lending")
def _():
    k = tk_world()
    enact_code(k, LB.LIB["Handshake Loans"]["code"])
    lid = tk(k, "Secured Lending")
    a, b, c = workers(k)
    n = _loan(k, a, b, qty=5, repay=6)
    assert "no open loan" in refused(k, c, "pledge", n, "stone", 2)
    assert invoke(k, b, "pledge", n, "stone", 4).startswith("pledged")
    assert k.bal(b, "stone") == 6.0 and pub(k, lid)["interests"][0]["status"] == "held"
    k.agent(b)["holdings"]["timber"] = 0.0
    nxt(k)                                                                  # the default: the collateral goes to the lender
    assert k.bal(a, "stone") == 14.0 and pub(k, lid)["interests"][0]["status"] == "enforced"
    assert k.w["loans"][n]["repaid"] > 0
    m = _loan(k, a, c, qty=2, repay=2, due_in=3)
    invoke(k, c, "pledge", m, "stone", 1)
    A.act(k, c, "repay_loan", {"loan": m, "qty": 2})                        # repaid: the collateral comes back
    assert k.bal(c, "stone") == 10.0 and pub(k, lid)["interests"][1]["status"] == "released"


@smoke("Guarantee")
def _():
    k = tk_world()
    enact_code(k, LB.LIB["Handshake Loans"]["code"])
    lid = tk(k, "Guarantee")
    a, b, c = workers(k)
    n = _loan(k, a, b, qty=5, repay=6)
    assert "party to a loan" in refused(k, b, "guarantee", n)
    assert invoke(k, c, "guarantee", n) == "you guarantee " + n
    k.agent(b)["holdings"]["timber"] = 0.0
    nxt(k)
    assert k.w["loans"][n]["status"] == "repaid" and k.bal(c, "timber") == 14.0 and pub(k, lid)["guarantees"][n] == c


@smoke("Contract Registry")
def _():
    k = tk_world()
    lid = tk(k, "Contract Registry")
    a, b, c = workers(k)
    assert "agreement 1 entered" in invoke(k, a, "register_agreement", b, "b delivers 4 stone to a by round 5")
    assert "no agreement" in refused(k, c, "confirm_agreement", 1)
    assert invoke(k, b, "confirm_agreement", 1) == "agreement registered"
    deed = next(e["id"] for e in reversed(k.events) if e["type"] == "gazette" and "is registered" in str(e["data"]))
    j = of(k, "legislator")[0]
    give(k, j, "judge")
    ab = k.bal(a, "timber")
    rule(k, j, accuse(k, a, b, lid, "registered_agreement", [deed]))
    assert k.bal(a, "timber") == ab + 3
    rule(k, j, accuse(k, a, c, lid, "registered_agreement"))               # no agreement binds c: nothing paid
    assert k.bal(a, "timber") == ab + 3 and len(pub(k, lid)["breaches"]) == 1


@smoke("Exemptions List")
def _():
    k = tk_world()
    a, b, c = workers(k)
    tax = enact_code(k, 'title = "Sales Duty"\nintent = "t"\ndef before_move(p, chain):\n    if p["why"] == "transfer":\n'
                        '        return 1\n    return None\n')
    lid = tk(k, "Exemptions List", EXEMPT_AGENTS=[a])
    A.act(k, a, "transfer", {"to": c, "item": "timber", "qty": 4})
    A.act(k, b, "transfer", {"to": c, "item": "timber", "qty": 4})
    assert k.bal(a, "timber") == 16.0 and k.bal(b, "timber") == 15.0      # a's duty refunded, b's kept
    assert pub(k, lid)["refunds"] == {a: 1.0} and k.w["laws"][tax]["status"] == "active"


@smoke("Extradition")
def _():
    from tests.test_cybertron_jurisdictions import declared, make_spec
    k = Kernel(generator.generate(S.apply_overrides(make_spec(), ["law.v2=true", "law_level=L4"]), 1))
    k.enact(k.new_law(k.inst["constitution_code"], "constitution"))
    k.start_round()
    cit = [x for x in k.roster() if k.cls_of(x) not in ("board", "fixer")]
    reg = tk(k, "Precedent Register")
    honest = enact_code(k, LB.LIB["Honest Dealing"]["code"])
    founder, fugitive, accuser, judge = cit[:4]
    give(k, judge, "judge")
    A.act(k, accuser, "accuse", {"agent": fugitive, "law": honest, "clause": "misstatement",
                                 "evidence": [post(k, fugitive, "perfect silver")]})
    rule(k, judge, f"C{k.w['case_seq']}")
    jid = declared(k, founder)
    ex = k.new_law(LB.instantiate("Extradition", {"SOURCES": [reg]}), "constitution")
    k.w["laws"][ex]["jurisdiction"] = jid
    k.enact(ex)
    assert "refused" in A.act(k, fugitive, "join", {"jurisdiction": jid})
    assert pub(k, ex)["refused"][0]["agent"] == fugitive


@smoke("Usury Ceiling")
def _():
    k = tk_world()
    enact_code(k, LB.LIB["Handshake Loans"]["code"])
    lid = tk(k, "Usury Ceiling", CAP=0.1, REPEAT=2)
    a, b = workers(k)[:2]
    for _ in range(2):
        with pytest.raises(A.ActionError, match="caps interest"):
            A.act(k, a, "lend", {"to": b, "item": "timber", "qty": 5, "repay_qty": 10, "due_in": 1})
    assert [x["lender"] for x in pub(k, lid)["usurers"]] == [a, a]
    with pytest.raises(A.ActionError, match="barred"):                    # a repeat usurer may not lend at all
        A.act(k, a, "lend", {"to": b, "item": "timber", "qty": 5, "repay_qty": 5, "due_in": 1})
