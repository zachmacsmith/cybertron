# Acts made to work as they read

**Status:** retrospective, accepted: D4-94 (2 Nov)
**Owner:** 37.4

## Summary

Five fixes from an analysis of every refusal in wb2 (269 of 1,070 acts, 25%) and wb3 (76 of 609, 12%). The spec text is in
agents/actions.md "Acts made to work as they read".

## Why

Zach (2 Nov): "How many actions are being refused then?? Can you analyse ... see if there is something wrong with the actions?",
then "Fix 1-5". The analysis (review 38.49) sorted refusals into three groups: faults of the engine, misreadings the prompt invites,
and the world's constraints. These five were the faults and the worst misreadings:

| Fix | Refusals | What was wrong |
|---|---|---|
| A fire in the open | 21 (wb2) | it took only timber, though the night burns firewood first; people at Holm Wood with firewood were refused |
| `take` by tag or description | 19 | "no building called 'pack T7 at Gorse Bank'" when the thing was not here or held no such good |
| `move` into a full store | 41 | refused, where `give` leaves the rest at the door |
| Work legs | 10 | "work 2 days on the water wheel" could not be read |
| Fittings on open ground; a camp | 7, and a granary accepted in a camp | the build list mixed rooms and fittings; a camp took store fittings that did nothing |

## Alternatives considered

- **For work legs, checking the work is done where named:** the engine enforces only possession (D4-23), so the words stay a note.

## Open questions

1. Whether a hearth in a camp should be allowed (refused for now with the stores).
2. Whether to accept a note's text in `pin` (item 6 of the analysis; not asked for).

## Affects

verbs.py (_fire, _take, the move put, _fitting), things.py (find), agreements.py (parse_legs, leg_text), prompt.py (verb_lines);
tests/test_cybertron2_act_fixes.py, two tests updated (the farm fire message; the cottage's grain); OPEN L-45.

## History

- 2 Nov 2026: built at Zach's request; written down the same session (retrospective).

## Sources

runs/wb2_wenbridge, runs/wb3_wenbridge; the analysis script in the session scratchpad (refusals.py).
