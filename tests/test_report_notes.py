"""agents/<Name>/working/notes.md: the scratchpad at the end of each round, rebuilt from write_scratchpad actions (the context
module has no "notes" field in replies)."""
import json

from cybertron import report as R


def _w(text, mode=None, key="text"):
    args = {key: text, **({"mode": mode} if mode else {})}
    return {"action": "write_scratchpad", "args_json": json.dumps(args)}


def test_replace_append_and_carry_over():
    turns = [{"round": 0, "phase": "decide", "actions": [{"action": "harvest", "args_json": "{}"}, _w("plan A")]},
             {"round": 1, "phase": "decide", "actions": [_w("and B", "append")]},
             {"round": 2, "phase": "decide", "actions": []},
             {"round": 3, "phase": "decide", "actions": [_w("fresh", key="note")]}]
    assert R.scratchpad_by_round(turns) == {0: "plan A", 1: "plan A\nand B", 2: "plan A\nand B", 3: "fresh"}


def test_final_actions_are_what_ran_and_dm_phases_count():
    turns = [{"round": 0, "phase": "decide", "actions": [_w("planned")], "final_actions": [_w("carried out")]},
             {"round": 0, "phase": "dm_reply_1", "actions": [_w("after the DMs", "append")]}]
    assert R.scratchpad_by_round(turns) == {0: "carried out\nafter the DMs"}


def test_nothing_written_gives_nothing_and_bad_args_are_skipped():
    assert R.scratchpad_by_round([{"round": 0, "actions": [{"action": "write_scratchpad", "args_json": "{not json"}]}]) == {}
    assert R.scratchpad_by_round([{"round": 0, "actions": []}]) == {}
