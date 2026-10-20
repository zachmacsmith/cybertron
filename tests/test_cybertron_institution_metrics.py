"""Institution metrics (cybertron/analysis/institutions.py, review 31 item 1.11) on small synthetic run directories: the market
parser, money velocity, hoard ratio and arrears, food stores and keeper draws, channel use, inert laws, role adherence, obligations
read defensively (absent, present), older layouts, and the CLI (nothing written into the run directory)."""
from __future__ import annotations

import json
from pathlib import Path

from cybertron import __main__ as M
from cybertron import report
from cybertron.analysis import institutions as INS

AGENTS = ["Ann", "Bob", "Cat"]
OFFICES = ("title = 'Offices Act'\noffices = {'keeper': {'title': 'Keeper of the Granary', 'holders': ['Ann'], 'duties': 'keep S1'},"
           " 'council': {'title': 'Councillor', 'powers': ['speak'], 'holders': ['Bob']}}\n")
GRANARY = "title = 'Granary Ration'\nSTORE = 'S1'\nOFFICE = 'J0.keeper'\nCAP = 6\n"


def ev(i, r, t, who=None, **data):
    return {"id": f"e{i}", "round": r, "type": t, "agent": who, "data": data, "vis": "public"}


def snap(r, pennies, food, s1, rights=None, contracts=None):
    return {"round": r, "values": {a: 1.0 + pennies[a] for a in AGENTS},
            "holdings": {a: {"penny": pennies[a]} for a in AGENTS}, "supplies": {"penny": 100.0},
            "rights": rights or {"Ann": ["J0.keeper"], "Bob": ["J0.council", "vote"], "Cat": []},
            "channels": {"market": {"owner": "world"}, "council": {"owner": "J0"}},
            "contracts": contracts or {}, "conflict": {"dead": {}},
            "subsistence": {"food": dict(food), "stores": {"S1": {"owner": "J0", "food": s1}, "S9": {"owner": "Cat", "food": 4.0}}}}


def write_run(d: Path, events, snaps, laws, start=True):
    d.mkdir(parents=True, exist_ok=True)
    (d / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n")
    (d / "snapshots.json").write_text(json.dumps(snaps))
    (d / "ground_truth.json").write_text(json.dumps({"laws": laws, "currencies": ["penny"]}))
    inst = {"agents": [{"id": a} for a in AGENTS], "start": {"schedule": [{"id": "start:store:S1"}]} if start else {}}
    (d / "instance.json").write_text(json.dumps(inst))
    return d


def base_run(d: Path, extra=(), laws=None, contracts=None):
    E = [
        ev(1, 0, "turn", "Ann", actions=[{"action": "withdraw", "args_json": "{}"}]),
        ev(2, 0, "turn", "Bob", actions=[{"action": "post", "args_json": "{}"}, {"action": "harvest", "args_json": "{}"}]),
        ev(3, 0, "turn", "Cat", actions=[{"action": "transfer", "args_json": json.dumps({"item": "food", "qty": 1, "to": "Ann"})}]),
        ev(4, 0, "channel_post", "Bob", channel_id="market", text="SELL 3 food @ 2 penny"),
        ev(5, 0, "channel_post", "Cat", channel_id="market", text="BUY 1 food @ 1 penny"),
        ev(6, 0, "channel_post", "Bob", channel_id="market", text="anyone selling?"),
        ev(7, 0, "dm", "Cat", to="Ann", text="I can give 2 food for 4 penny"),
        ev(8, 0, "dm", "Cat", to="Bob", text="I can give 2 food for 4 penny"),
        ev(9, 0, "move", "Cat", src="Cat", dst="Ann", item="penny", qty=10.0, why="transfer"),
        ev(10, 0, "move", None, src="assoc:A1", dst="Bob", item="penny", qty=5.0, why="law:L5"),
        ev(11, 0, "move", None, src="world", dst="Ann", item="penny", qty=50.0, why="intervention"),
        ev(12, 0, "move", "Cat", src="store:S9", dst="Cat", item="food", qty=2.0, why="withdraw"),   # own store: not a flow
        ev(13, 0, "store_withdrawal", "Ann", store="S1", owner="J0", qty=3.0),
        ev(14, 0, "move", "Ann", src="store:S1", dst="Ann", item="food", qty=3.0, why="withdraw"),
        ev(15, 0, "law_effect", None, law="L7", title="Empty Act", act="enact", changes=[], n_changes=0, inert=True),
        ev(16, 0, "law_effect", None, law="L8", title="Real Act", act="enact", changes=["x"], n_changes=1, inert=False),
        ev(17, 0, "law_call_failed", None, law="L8", fn="fine", reason="short"),
        ev(18, 0, "channel_read", "Cat", agent="Cat", channel="market", unread_before=2),
        ev(19, 0, "vote", "Bob", ballot="B1", choice="Bob"),
        ev(20, 1, "forest_shock", None, camp="c1"),
        ev(21, 1, "turn", "Ann", actions=[{"action": "harvest", "args_json": "{}"}]),
        ev(22, 1, "channel_post", "Bob", channel_id="market", text="SELL 1 food @ 4 penny"),
        ev(23, 1, "channel_post", "Bob", channel_id="council", text="the council decides"),
        *extra]
    S = [snap(0, {"Ann": 60.0, "Bob": 5.0, "Cat": 0.0}, {"Ann": 4.0, "Bob": 1.0, "Cat": 1.0}, 20.0, contracts=contracts),
         snap(1, {"Ann": 60.0, "Bob": 5.0, "Cat": 0.0}, {"Ann": 3.0, "Bob": 1.0, "Cat": 1.0}, 17.0, contracts=contracts),
         snap(2, {"Ann": 60.0, "Bob": 5.0, "Cat": 0.0}, {"Ann": 2.0, "Bob": 1.0, "Cat": 1.0}, 15.0, contracts=contracts)]
    L = {"L7": {"title": "Empty Act", "author": "Bob", "status": "active", "enacted_round": 0},
         "L8": {"title": "Real Act", "author": "constitution", "status": "active", "enacted_round": 0},
         "L11": {"title": "Offices Act", "author": "constitution", "status": "active", "code": OFFICES},
         "L13": {"title": "Granary Ration", "author": "constitution", "status": "active", "code": GRANARY},
         "L5": {"title": "Wage Roll", "author": "Cat", "status": "active", "jurisdiction": "A1",
                "public": {"owed": {"Bob": 2.5, "Cat": 1.0}, "payroll": {}}}}
    L.update(laws or {})
    return write_run(d, E, S, L)


def test_market_money_food_channels_laws(tmp_path):
    res = INS.analyse(base_run(tmp_path / "run"))
    mk = res["market"]
    assert mk["parsed"] == 3 and mk["market_posts"] == 4 and mk["market_parse_share"] == 0.75
    assert mk["median_ask"] == 3.0 and mk["median_bid"] == 1.0
    assert mk["series"][0]["spread"] == 1.0 and mk["price_ratio_after_shock"] == round(4 / 1.5, 3)   # before: 2, 1; after: 4
    assert mk["loose_quotes"] == 2 and mk["loose_median_price"] == 2.0
    pen = res["money"]["currencies"]["penny"]
    r0 = pen["series"][0]
    assert r0["voluntary"] == 10.0 and r0["auto"] == 5.0 and r0["velocity"] == 0.15     # the intervention is not a flow
    assert pen["voluntary_share"] == round(10 / 15, 3)
    # round 0: Cat paid (holds 0), Ann and Bob made no outgoing payment and hold 65 of 65
    assert r0["hoard_ratio"] == 1.0
    ar = res["money"]["arrears"]
    assert ar["total"] == 3.5 and ar["creditors"] == 2 and "L5" in ar["by_law"]
    f = res["food"]
    assert f["keeper_draws"] == 3.0 and f["series"][0]["voluntary"] == 3.0               # the keeper's draw moves J0's food to Ann
    assert f["shock_round"] == 1 and f["hoarding_index"]["polity"] == -5.0             # S1 20 -> 15 from round 0 to round 2
    assert f["survival_share_before"] == round(3 / 4, 3) and f["survival_share_after"] == 1.0
    c = res["channels"]
    assert c["per_channel"]["market"]["posts"] == 4 and c["per_channel"]["market"]["authors"] == 2
    assert c["dms"] == 2 and c["broadcast_by_dm_groups"] == 1 and c["dm_share"] == round(2 / 7, 3)
    assert c["reads"] == 1 and c["reads_with_unread"] == 1
    lw = res["laws"]
    assert lw["enacted_acts"] == 2 and lw["inert"] == 1 and lw["agent_inert"] == 1 and lw["inert_by_author"] == {"Bob": 1}
    assert lw["call_failed"] == 1
    h = res["headline"]
    assert h["inert_laws"] == 1 and h["currency"] == "penny"


def test_role_adherence(tmp_path):
    res = INS.analyse(base_run(tmp_path / "run"))
    o = res["offices"]["offices"]
    keeper, council = o["J0.keeper"], o["J0.council"]
    assert keeper["duties"] == ["store"]                                # the Granary Ration names the keeper's store
    assert keeper["held_rounds"] == 3 and keeper["performed_rounds"] == 1 and keeper["adherence"] == round(1 / 3, 3)
    assert keeper["food_drawn_and_kept"] == 3.0
    assert council["duties"] == ["speak", "legislate"]
    assert council["performed_rounds"] == 2 and council["by_duty"]["legislate"] == round(1 / 3, 3)
    assert res["offices"]["adherence"] == round(3 / 6, 3)


def test_obligations_absent_then_present(tmp_path):
    res = INS.analyse(base_run(tmp_path / "plain"))
    ob = res["obligations"]
    assert ob["obligations_system"] is False and ob["breaches"] == 0 and ob["fulfil_actions"] == 0
    assert ob["legs_run"]["A1"]["moves"] == 1                           # the Wage Roll's leg (law of A1)
    extra = [ev(30, 1, "turn", "Cat", actions=[{"action": "fulfil", "args_json": json.dumps({"contract": "A2"})}]),
             ev(31, 1, "transfer", "Cat", to="Bob", item="penny", qty=1.0, fulfil="A2:D:Cat"),
             ev(32, 1, "notify", None, to="Bob", text="You missed Supply Contract (A2) leg D: 2 food to Ann; 2 overdue.", by="law:L40"),
             ev(33, 1, "contract_breach", "Bob", contract="A2", clause="Supply D", remedy="penalty 2 penny to Ann"),
             ev(34, 1, "contract_left", "Bob", contract="A2", why="left")]
    laws = {"L40": {"title": "Supply Contract", "author": "Ann", "status": "active", "jurisdiction": "A2",
                    "state": {"missed": {"Bob": {"D": 1}}, "could": {"Cat": {"D": 2}}, "owed": {"Ann": {"penny": 4.0}}}}}
    res = INS.analyse(base_run(tmp_path / "obl", extra=extra, laws=laws))
    ob = res["obligations"]
    assert ob["obligations_system"] is True
    assert ob["fulfil_actions"] == 1 and ob["fulfil_payments"] == 1 and ob["missed_notices"] == {"A2": 1}
    assert ob["breaches"] == 1 and ob["left"] == 1 and ob["missed_would_not"] == 1 and ob["missed_could_not"] == 2
    assert res["money"]["arrears"]["total"] == 7.5 and res["headline"]["missed_obligations"] == 1


def test_older_layout_and_missing_files(tmp_path):
    d = base_run(tmp_path / "old")
    lines = [json.loads(x) for x in (d / "events.jsonl").read_text().splitlines()]
    turns = [{"round": e["round"], "agent": e["agent"], "actions": e["data"]["actions"]} for e in lines if e["type"] == "turn"]
    keep = [e for e in lines if e["type"] not in ("turn", "law_effect")]
    (d / "events.jsonl").write_text("\n".join(json.dumps(e) for e in keep) + "\n")
    (d / "turns.jsonl").write_text("\n".join(json.dumps(t) for t in turns) + "\n")
    gt = json.loads((d / "ground_truth.json").read_text())
    gt["laws"]["L9"] = {"title": "Dead Letter", "author": "Bob", "status": "active", "enacted_round": 1}
    (d / "ground_truth.json").write_text(json.dumps(gt))
    res = INS.analyse(d)
    lw = res["laws"]
    assert lw["law_effect_recorded"] is False and lw["inert"] is None
    assert lw["fallback"]["enacted_agent_laws_without_recorded_effect"] == ["L9"]
    assert res["food"]["survival_share_before"] == 0.75                 # read from turns.jsonl
    assert "older log" in INS.markdown(res)
    empty = tmp_path / "empty"
    empty.mkdir()
    assert INS.analyse(empty)["available"] is False
    (empty / "events.jsonl").write_text(json.dumps(ev(1, 0, "dm", "X", to="Y", text="hi")) + "\n")
    res = INS.analyse(empty)                                            # no snapshots, no ground truth: sections degrade
    assert res["offices"]["available"] is False and res["food"]["available"] is False
    assert res["channels"]["dms"] == 0 or res["channels"]["available"]
    assert not any("error" in (v or {}) for v in res.values() if isinstance(v, dict))


def test_cli_and_report_write_nothing_else(tmp_path):
    d = base_run(tmp_path / "run")
    before = sorted(p.name for p in d.iterdir())
    out = tmp_path / "out.json"
    md = tmp_path / "out.md"
    try:
        M.main(["institutions", str(d), "--json", str(out), "--md", str(md)])
    except SystemExit as e:
        assert e.code == 0
    assert sorted(p.name for p in d.iterdir()) == before
    res = json.loads(out.read_text())
    assert res["run"] == "run" and res["headline"]["inert_laws"] == 1
    assert "## Role adherence" in md.read_text()
    report._institutions_md(d, json.loads((d / "instance.json").read_text()))
    assert (d / "institutions.md").read_text().startswith("# Institutions: run")
    plain = base_run(tmp_path / "plain")
    report._institutions_md(plain, {"start": {}})                       # no start block: no file
    assert not (plain / "institutions.md").exists()
