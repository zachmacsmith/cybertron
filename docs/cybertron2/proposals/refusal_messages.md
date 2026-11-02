# What a refusal says

**Status:** retrospective, accepted: D4-95, D4-96 (2 Nov)
**Owner:** 37.4

## Summary

Refusals say enough to choose differently, never more than one could sense. The rules are in agents/actions.md, "What a refusal
says".

## Why

The audit of every refusal (review 38.50: 6,776 of 47,397 acts in 56 runs) found messages that were true but left agents
repeating the same act. Zach answered item by item (2 Nov):
- "picked bare" is valid: "they can figure that out";
- the missing good should say where it is, and "X is already being used by Y";
- the beasts: "say who already did it today";
- bread: "needs flour from a mill";
- "not done at" should list "you can do it at: X, Y, Z";
- ripeness: "Don't tell them when it will be ripe ... failures should still see senses about the place";
- the unclear messages need "more specificity so they know why it's going wrong";
- "Pinning a note by text should be possible";
- "Dead members cannot be head of a household".

## The proposal

As summarised. A store's draws are recorded for the day (today["drawn"]) so that the next one to find it short is told who took it.
A refused act at a place, or one refused by its site, puts the person on that parcel for the day's noticing (today["worked"]).

## Alternatives considered

- **Where else to forage, and when a place comes back:** declined by Zach. They find it themselves.
- **Refusing to name a dead member in every case:** that would tell the namer of a death they had not learned (the senses guide).
  So the act refuses only the known dead, and succession has always counted only the living.

## Open questions

1. Whether a refused act should cost a unit (it costs none now). Repeats of one refused act in a day (2,567 in all runs) cost nothing
   but clutter the results.

## Affects

verbs.py (_consume, _drawn, _short_note, _store_name, _move, _take, _out, _site, _set, _name, _work), knowledge.py (shortfall),
farm.py (herders and milkers by name), agreements.py (_pay), perceive.py (apply_notes); tests in test_cybertron2_act_fixes.py.

## History

- 2 Nov 2026: built at Zach's request after the audit; written down the same session (retrospective).
- 2 Nov 2026: D4-96 added. Zach asked that goods in the store be used automatically at home, with the agent told. Making, building and paying already drew on the stores, so `give` now does too, and every act says what it took from which store (verbs._top_up, _drew_words; a test in test_cybertron2_act_fixes.py; a package A test empties the store first).

## Sources

docs/review/38_space_engine/50_refusal_audit.md.
