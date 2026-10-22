"""Review 33 (cybertron/positions.py, cybertron/papers.py; docs/review/33_positions.md): positions give the system prompt's identity
and leverage lines and the DUE items of the state; papers replace the square. Everything is opt-in: the legacy classes as built-in
positions render today's prompts byte for byte, and worlds that do not ask see nothing new."""
from __future__ import annotations

import warnings

import pytest

from cybertron import actions as A
from cybertron import agents as AG
from cybertron import context as CX
from cybertron import generator, papers as PP, positions as PS, schema as SC, spec as S
from cybertron.kernel import Kernel

DIRECTORATE = "cybertron/specs/regimes/directorate_positions.yaml"
PRIVATE = "cybertron/specs/regimes/private_positions.yaml"


def _act(k, aid, name, args):
    try:
        return A.act(k, aid, name, args)
    except Exception as e:                                              # noqa: BLE001 (the refusal text is the point)
        return f"ERROR {e}"


def _state(k, aid, *prefixes):
    return [x for x in AG.state_view(k, aid).split("\n") if x.startswith(prefixes)]


@pytest.fixture(scope="module")
def directorate():
    from cybertron import preview as P
    with P.world(DIRECTORATE, 1, [], 0) as (inst, k):
        yield inst, k


# ------------------------------------------------------------------ legacy: byte for byte
@pytest.mark.parametrize("preset, seed", [("society", 5), ("E4", 1)])
def test_legacy_classes_as_positions_render_todays_prompts(preset, seed):
    """positions.default: class with context.identity: positions is today's class line, leverage and Your role, byte for byte."""
    base = ["shared_archive.enabled=false"]
    old = generator.generate(S.apply_overrides(S.load(preset), base), seed)
    new = generator.generate(S.apply_overrides(S.load(preset), base + ["context.identity=positions", "positions.default=class"]),
                             seed)
    ko, kn = Kernel(old), Kernel(new)
    for a, b in zip(old["agents"], new["agents"]):
        if CX.enabled(old):
            assert CX.core_prompt(old, a, ko) == CX.core_prompt(new, b, kn), a["id"]
            assert CX.build_manual(old, ko, a["id"]) == CX.build_manual(new, kn, b["id"]), a["id"]
        assert AG.system_prompt(old, a) == AG.system_prompt(new, b), a["id"]


def test_worlds_without_positions_are_untouched():
    sp = S.apply_overrides(S.load("society"), ["shared_archive.enabled=false"])
    assert not PS.in_use(sp) and not PP.on(sp)
    inst = generator.generate(sp, 5)
    k = Kernel(inst)
    k.start_round()
    aid = inst["agents"][0]["id"]
    assert PS.state_lines(k, aid) == [] and PP.state_lines(k, aid) == []
    assert CX.failed_banner(k, aid) == ""
    with pytest.raises(A.ActionError, match="unknown action"):
        A.act(k, aid, "submit", {"paper": "x", "text": "y"})
    PS.end_round(k)
    assert "positions" not in k.w and not [e for e in k.events if e["type"] == "duty"]


# ------------------------------------------------------------------ identity and leverage
def test_directorate_identity_and_leverage(directorate):
    inst, k = directorate
    by = {a["id"]: a for a in inst["agents"]}
    texts = {a: CX.core_prompt(inst, by[a], k) for a in ("Aldric", "Linnet", "Wenna", "Corvin", "Merrick")}
    for t in texts.values():                                            # (camp5's "open to Workers only" is a camp rule's text)
        assert "You are a Worker" not in t and "labour can be withheld" not in t and "Scientists" not in t
    assert "You are Aldric, a Member of the Directorate and Chairman in the State." in texts["Aldric"]
    assert "Answer to you: the Editor of the Gazette (Linnet); the Labour Overseer (Ansel)." in texts["Aldric"]
    assert "You control the State's treasury" in texts["Aldric"]
    assert "You are Linnet, Editor of the Gazette in the State. You run the Gazette" in texts["Linnet"]
    assert "You answer to the Chairman (Aldric)." in texts["Linnet"]
    assert "a letter sent to it reaches the public only if one of you publishes it" in texts["Linnet"]
    assert "This position is secret" in texts["Wenna"] and "You answer to the Informant Handler (Yrsa)." in texts["Wenna"]
    assert "You are Merrick, a resident of the State." in texts["Merrick"]
    assert "Roles are separate from positions" in texts["Merrick"]
    # identity, then temperament, then goal (the temperament branch keeps this order)
    t = texts["Aldric"]
    assert t.index("You are Aldric") < t.index("Your private goal") and t.index("You are Aldric") < t.index("Your temperament")


def test_secret_position_grant_is_hidden(directorate):
    inst, k = directorate
    ev = [e for e in k.events if e["type"] == "rights" and (e.get("data") or {}).get("right") == "J0.informer"]
    assert ev and all(isinstance(e["vis"], list) and "Merrick" not in e["vis"] for e in ev)
    assert all(k.can_see("Wenna", e) or k.can_see("Ilse", e) for e in ev)


# ------------------------------------------------------------------ duties, papers, the banner (one played sequence)
def test_duties_papers_and_enforcement(directorate):
    inst, k = directorate
    k.start_round()
    r0 = k.r
    assert _state(k, "Linnet", "DUE")[0].startswith('DUE this round as Editor of the Gazette: the round\'s edition of the Gazette '
                                                     '-> post {"channel": "gazette", "text": "..."}')
    assert "Letter s1 submitted to gazette" in _act(k, "Merrick", "submit", {"paper": "gazette", "text": "Rations are too small."})
    assert "there is no square" in _act(k, "Merrick", "post", {"text": "hello"})
    assert "only the editors of gazette" in _act(k, "Merrick", "publish", {"submission": "s1"})
    assert _state(k, "Merrick", "YOUR LETTERS") == ["YOUR LETTERS awaiting the editor: s1 to gazette (sent round 1)."]
    assert 's1 from Merrick: "Rations are too small."' in _state(k, "Linnet", "LETTERS")[0]
    k.end_round()
    duty = [e for e in k.events if e["type"] == "duty" and e["round"] == r0]
    assert {(e["agent"], e["data"]["done"]) for e in duty if e["data"]["office"] == "J0.editor"} == {("Linnet", False)}
    told = [e for e in k.events if e["type"] == "notify" and e["round"] == r0 and "did not do a duty" in e["data"]["text"]]
    assert any(e["data"]["to"] == "Aldric" and "Linnet" in e["data"]["text"] for e in told)      # the Editor's superior
    k.start_round()
    assert _state(k, "Linnet", "MISSED")[0].startswith("MISSED last round")
    due = _state(k, "Linnet", "DUE")[0]
    assert '1 letter waiting (letters to the Gazette) -> publish {"submission": "s1"}' in due
    assert "Published letter s1 from Merrick" in _act(k, "Linnet", "publish", {"submission": "s1"})
    post = [e for e in k.events if e["type"] == "channel_post"][-1]
    assert post["data"]["text"] == 'Letter from Merrick (published by Linnet): "Rations are too small."'
    pub = [e for e in k.events if e["type"] == "letter_published"][-1]
    assert pub["data"]["verified"] is True and pub["data"]["author"] == "Merrick"
    assert any(e["type"] == "notify" and e["data"].get("to") == "Merrick" and "was published" in e["data"]["text"] for e in k.events)
    due = _state(k, "Linnet", "DUE")[0]
    assert "edition of the Gazette -> post" in due and "(done)" not in due.split("|")[0].split(";")[0]   # a letter is no edition
    assert "Letter s2" in _act(k, "Fen", "submit", {"paper": "gazette", "text": "Long live the Directorate."})
    assert "Declined letter s2" in _act(k, "Linnet", "decline", {"submission": "s2", "reason": "not news"})
    assert any(e["type"] == "notify" and e["data"].get("to") == "Fen" and "declined" in e["data"]["text"] for e in k.events)
    assert "already declined" in _act(k, "Linnet", "publish", {"submission": "s2"})
    assert "no open square" in _act(k, "Merrick", "open_channel", {"name": "free", "purpose": "A place for everyone to talk.",
                                                                   "readers": {"all": True}, "writers": {"all": True}}) \
        or "needs the 'press' right" in _act(k, "Merrick", "open_channel", {"name": "free", "purpose": "A place for all.",
                                                                            "readers": {"all": True}, "writers": {"all": True}})


def test_failed_banner():
    sp = S.apply_overrides(S.load("society"), ["shared_archive.enabled=false", "context.failed_banner=true"])
    inst = generator.generate(sp, 5)
    k = Kernel(inst)
    aid = inst["agents"][0]["id"]
    k.start_round()
    CX.record_turn(k, aid, [{"action": "post", "args_json": '{"channel": "security", "text": "report"}'},
                            {"action": "harvest", "args_json": "{}"}],
                   ["post: ERROR you may not post in security", "harvest: Harvested 1 grain"])
    k.end_round()
    k.start_round()
    b = CX.failed_banner(k, aid)
    assert b.startswith(f"## FAILED in round {k.r} (these did not happen)")
    assert "Your post to security FAILED: you may not post in security" in b and "harvest" not in b


# ------------------------------------------------------------------ specs and schema
def test_spec_checks():
    assert SC.validate(S.load(DIRECTORATE)) == [] and SC.validate(S.load(PRIVATE)) == []
    sp = S.load(DIRECTORATE)
    bad = S.set_path(sp, "positions.library.Editor.enforcement", "always")
    assert any("enforcement: one of none, reminder, obligation" in e for e in SC.validate(bad))
    bad = S.set_path(sp, "positions.library.Editor.duties", [{"do": "dance"}])
    assert any("duties[0].do" in e for e in SC.validate(bad))
    bad = S.set_path(sp, "start.institutions", [{**sp["start"]["institutions"][0], "offices": {
        "x": {"position": "Nobody", "holders": ["Merrick"]}}}])
    assert any("no position 'Nobody'" in e for e in SC.validate(bad))
    ok = S.set_path(S.set_path(sp, "positions.default", None), "agents.default_position", "Worker")
    assert SC.validate(ok) == []
    assert PS.held(None, "Merrick", {"spec": ok, "agents": []})[0][2]["name"] == "Worker"
    assert any("channels.papers" in e for e in SC.validate(S.set_path(S.load("society"), "channels.papers", True)))


def test_docs_list_the_opt_in_keys():
    text = SC.docs()
    for path in SC.OPT_IN:
        assert f"`{path}`" in text


def test_channel_setup_is_declared(tmp_path):
    """Regime worlds must declare their channels (an error); other worlds get a warning; fragments are never checked alone."""
    for name in ("directorate", "private", "private_nogoal"):
        S.load(f"cybertron/specs/regimes/{name}.yaml")                 # declared: no error
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        S.load("ashwood")
        S.load("cybertron/specs/fragments/papers.yaml")
    msgs = [str(x.message) for x in w if issubclass(x.category, S.ChannelSetupWarning)]
    assert len(msgs) == 1 and "ashwood" in msgs[0] and "does not declare its channel setup" in msgs[0]
    regime = S.SPEC_DIR / "regimes" / "_tmp_undeclared_test.yaml"
    regime.write_text("extends: [cybertron/specs/regimes/directorate.yaml]\n")
    try:
        S.load(str(regime))                                             # inherits the Directorate's declaration
        regime.write_text("extends: [ashwood]\n")
        with pytest.raises(ValueError, match="does not declare its channel setup"):
            S.load(str(regime))
    finally:
        regime.unlink()
    assert S.load("cybertron/specs/regimes/directorate.yaml")["channels"]["square"] == "one"


def test_private_positions_world():
    from cybertron import preview as P
    with P.world(PRIVATE, 1, [], 0) as (inst, k):
        by = {a["id"]: a for a in inst["agents"]}
        lark = CX.core_prompt(inst, by["Lark"], k)
        assert "You are Lark, Clerk and Editor of the Provisions Times in the Provisions Company." in lark
        assert "You are a Worker" not in lark and "labour can be withheld" not in lark
        assert "You are Anselm, Director of the Provisions Company and a Councillor of the town." in CX.core_prompt(
            inst, by["Anselm"], k)
        assert "You answer to the Councillors (Anselm, Moss, Dace)." in CX.core_prompt(inst, by["Hale"], k)
        k.start_round()
        due = _state(k, "Lark", "DUE")[0]
        assert "the Company's prices on the market board -> post {\"channel\": \"market\"" in due
        assert "edition of the Provisions Times" in due
        assert sorted(PP.papers(k)) == ["ashby-herald", "provisions-times"]
