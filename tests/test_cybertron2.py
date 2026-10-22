"""cybertron2 phase 0 (docs/review/38_space_engine/00_plan.md): presence gates, the ration from the house stock, shelter by where
an agent sleeps, the cold's fall to starving, determinism of a scripted run."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from cybertron2 import act, run as R
from cybertron2.world import World, load_spec

SPEC = Path(__file__).resolve().parents[1] / "cybertron2" / "specs" / "forest_households.yaml"


HILLS = SPEC.parent / "hills_and_forest.yaml"


def do(w, name, a):
    return act.do(w, name, a)[0]


def world(**over):
    sp = copy.deepcopy(load_spec(over.pop("spec", SPEC)))
    sp.update(over)
    return World(sp)


def test_presence_gates():
    w = world()
    assert do(w, "Gil", {"do": "forage"}).startswith("Refused")            # nothing to forage in the clearing
    assert do(w, "Gil", {"do": "travel", "to": "deep_wood"}).startswith("Refused")   # not next to the clearing
    assert not do(w, "Gil", {"do": "travel", "to": "near_wood"}).startswith("Refused")
    assert do(w, "Gil", {"do": "give", "to": "Fay", "item": "food", "qty": 1}).startswith("Refused")   # Fay is not here
    assert do(w, "Gil", {"do": "take", "item": "food", "qty": 1}).startswith("Refused")   # not at his house
    assert do(w, "Gil", {"do": "hunt"}).startswith("Refused")               # no game in the near wood
    assert not do(w, "Gil", {"do": "forage"}).startswith("Refused")
    assert not do(w, "Gil", {"do": "fell"}).startswith("Refused")
    assert do(w, "Gil", {"do": "forage"}).startswith("Refused")             # at most 2 gathering actions a round


def test_partial_ration_holds_the_stage():
    w = world()
    w.s["agents"]["Gil"]["at"] = "near_wood"                                    # out in the open: needs 1.5
    w.s["agents"]["Gil"]["holdings"]["food"] = 1.2
    rec = w.end_of_round()
    assert "Gil" in rec["short"] and "Gil" not in rec["missed"] and w.s["agents"]["Gil"]["stage"] == 0


def test_ration_and_shelter():
    w = world()
    for n in w.living():
        w.s["agents"][n]["holdings"]["food"] = 0.0
    w.s["agents"]["Gil"]["at"] = "near_wood"
    w.s["houses"]["wynn_house"]["stock"]["food"] = 12.0                     # Gil sleeps out: no house stock, 1.5 needed
    rec = w.end_of_round()
    assert rec["shelter"]["Gil"] == "unsheltered" and "Gil" in rec["missed"]
    assert rec["shelter"]["Fay"] == "housed" and rec["ate"]["Fay"] == 1.0      # Fay eats from Wynn House's stock


def test_quantity_is_not_rounded_up():
    w = world()
    w.s["agents"]["Gil"]["holdings"]["food"] = 3.4255
    assert not do(w, "Gil", {"do": "store", "item": "food", "qty": 3.4255}).startswith("Refused")


def test_cold_drops_the_unsheltered_to_starving_without_a_missed_meal():
    w = world(cold_rounds=[1])
    for n in w.living():
        w.s["agents"][n]["at"] = "near_wood"
        w.s["agents"][n]["holdings"]["food"] = 10.0
    rec = w.end_of_round()
    assert rec["cold"] and not rec["missed"]                                    # everyone ate 2 (out in the cold)
    assert all(rec["ate"][n] == 2.0 for n in rec["ate"])
    fell = set(rec["cold_falls"])
    assert fell and all(w.s["agents"][n]["stage"] == -2 and w.s["agents"][n]["missed"] == 0 for n in fell)


def test_scripted_run_is_deterministic(tmp_path):
    sp = copy.deepcopy(load_spec(SPEC))
    for a in sp["agents"].values():
        a["model"] = "bot"
    sp["rounds"] = 8
    import yaml
    (tmp_path / "s.yaml").write_text(yaml.safe_dump(sp))
    a = R.run(str(tmp_path / "s.yaml"), str(tmp_path / "a"))
    b = R.run(str(tmp_path / "s.yaml"), str(tmp_path / "b"))
    assert (a / "rounds.jsonl").read_text() == (b / "rounds.jsonl").read_text()
    assert json.loads((a / "state.json").read_text())["round"] == 8


def test_raid_needs_presence_and_is_settled_at_night():
    w = world(spec=HILLS)
    assert do(w, "Torvald", {"do": "raid", "house": "alder_house"}).startswith("Refused")   # not at the Meadow
    for n in ("Torvald", "Brenna"):
        w.s["agents"][n]["at"] = "meadow"
    assert not do(w, "Torvald", {"do": "raid", "house": "alder_house"}).startswith("Refused")
    assert not do(w, "Brenna", {"do": "raid", "house": "alder_house"}).startswith("Refused")
    assert do(w, "Bram", {"do": "raid", "house": "alder_house"}).startswith("Refused")      # your own house
    before = w.s["houses"]["alder_house"]["stock"]["food"]
    rec = w.end_of_round()
    raid = rec["fights"][0]
    assert raid["kind"] == "raid" and raid["outcome"] in ("taken", "repelled") and set(raid["defenders"]) == {"Bram", "Cela", "Dara", "Eoin"}
    assert w.s["agents"]["Torvald"]["holdings"]["blade"] == 0                   # the blade is used up, win or lose
    if raid["outcome"] == "taken":
        assert w.s["houses"]["alder_house"]["stock"]["food"] < before


def test_the_iron_household_cannot_gather_food():
    w = world(spec=HILLS)
    w.s["agents"]["Ulf"]["at"] = "deep_wood"
    assert do(w, "Ulf", {"do": "forage"}).startswith("Refused")
    assert do(w, "Ulf", {"do": "hunt"}).startswith("Refused")
    assert not do(w, "Ulf", {"do": "fell"}).startswith("Refused")


def test_witnessing_and_beliefs_with_ages():
    from cybertron2 import perceive as PC, prompt as P
    w = world(spec=HILLS)
    PC.observe_all(w)
    res, seen = act.do(w, "Gil", {"do": "forage"})
    PC.witness(w, "Gil", "near_wood", seen)
    assert any("Gil foraged" in x["text"] for x in PC.store(w, "Fay")["seen"])        # Fay is at the Near Wood with him
    assert not PC.store(w, "Bram")["seen"]                                             # Bram, at the Meadow, saw nothing
    w.s["agents"]["Wynn"]["at"] = "deep_wood"                                          # Wynn walks away; her house changes
    w.s["houses"]["wynn_house"]["stock"]["food"] = 3.0
    w.s["round"] = 3
    text = P.turn_prompt(w, "Wynn")
    assert "as you last saw it 3 rounds ago" in text and "12 food" in text                # her belief, not the truth
