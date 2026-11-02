# One room, one fire; the night says what fuel was missing; a theft at a door told as one

**Status:** retrospective, accepted: D4-93 (2 Nov)
**Owner:** 37.4

## Summary

A house's fire burns 1 heat a normal night and 4 a cold one for each hearth. A fire ring alone counts as one; a ring beside a
hearth adds nothing. The prompt shows the figure the night uses. An unlit fire's night line names what it lacked. A theft from
goods left at a door is told as that, not as slipping into the house.

## The proposal

As summarised: night.house_heat; prompt._heat; run.py's night line; settle.py's theft event and the thief's "you think you were
seen".

## Why

From the Wenbridge run wb2 (review 38.49):
- Wat built a hearth beside his cottage's fire ring. The night then burned 2 heat, while the prompt said 1. With 0.7 timber
  (1.4 heat) the fire went out.
- The night line read "fire went out: no timber in its store" whatever the fuel. Wat pinned "Put timber in the store each night:
  our fire went out twice with only firewood", and timber was a day away.
- The Masons ate raw grain for days. Raw eating cost the village about 170 meals in all.
- Wat's theft from the heap at the Hearnes' door was seen as "Wat slipped into the Hearne hut", so the Hearnes barred a door that
  guarded nothing.

Zach: "yes" to the fixes.

## Alternatives considered

- **Each fitting its own fire, with the prompt showing the sum:** a ring beside a hearth would then only cost fuel and do nothing.

## Open questions

1. A large house with several hearths burns for each. Whether a hall should warm by its hearths' spaces only (D2-159 already does
   that for warmth).

## Affects

night.py, prompt.py, run.py, settle.py, verbs.py (the theft record notes a door); tests in test_cybertron2_heap_senses.py; OPEN
L-44 for 37.2's heat spec.

## History

- 2 Nov 2026: built after the wb2 run, at Zach's request; written down the same session (retrospective).

## Sources

runs/wb2_wenbridge; D2-157, D2-159, D4-81, D4-89.
