# A herd seen: its sighting at the spec's own, and presence next door raised

**Status:** retrospective, accepted: D4-98 (3 Nov)
**Owner:** 37.4

## Summary

Two changes to how a herd and things next door are seen:
- **The herd's sighting row** ("the Croft cattle (H1) on Croft Pasture: 4 cows, 1 ox, 2 calves") reads at own 0.95 with base 1, as
  information/noticing.md already said. It had carried a base chance of 0.15.
- **Presence next door** (a parcel next to where one worked or slept) rises from 0.1 to 0.3, for things of own 0.5 or more. That is
  the same as passing through a parcel on the way, and below being on it (0.5).

## The proposal

As in the spec: world/parcel_graph.md (presence table), information/noticing.md (presence), information/signs.md (the slaughter
table's crows row). Code: signs.py (HERD row 0), data.NOTICING["presence"]["next door"].

## Why

The food probe (review 38.55) found that the Ashbys never saw the Croft cattle in seven runs: seven beasts on the pasture beside the
Green where they live. Zach: "This definitely shouldn't be true because the perception system definitely includes a bunch about the
herds", then "increase the next door from 0.1 (next parcel should be much higher) I imagine?"

The sighting row's 0.15 was a hand-set value left from the first sign bundles (cc81e73), from before the one noticing rule (D4-75).
It was never decided. The rule multiplied it with the herd's own, so even one attending to the herd saw it only 37% of the time.
With that fixed, someone on the Green still saw the herd next door about 1 day in 10 (0.95 x 0.1). At 0.3 it is about 0.29 a day,
about 87% over six clear days.

| Who, where (clear day) | Before | Row fixed | And next door 0.3 |
|---|---|---|---|
| attending to the herd | 0.38 | 1.00 | 1.00 |
| herding or milking it | 0.45 | 1.00 | 1.00 |
| foraging on the pasture | 0.08 | 0.48 | 0.48 |
| on the Green, next door | 0.015 | 0.095 | 0.285 |

**The load on the prompt.** Measured on the worlds' first day, with each person working where they sleep (scratchpad
`nextdoor.py`): the expected signs noticed per person-day rise by about 0.4. Wenbridge goes from 1.52 to 1.92, the food probe from
1.19 to 1.58, Combe from 1.12 to 1.55. The cap is 5 lines (NOTICE_MAX), so nothing is crowded out on a quiet day.

## Alternatives considered

- **Presence next door by size** (rising with own from 0.1 at 0.5 to 0.3 at 1). Most rows leave own at 1 and set their plainness
  by base chance, so this comes to almost the same as a flat 0.3, with an extra rule.
- **Higher (0.5).** It would equal being on the parcel, so being next door would be worth as much as going there.
- **Naming the herd in the place's layout** (a standing fact shown once, senses guide rule 3). Not done; still open (OPEN.md L-63a).

## Open questions

- L-63a: whether a herd standing in its pasture belongs in "Here, as you see it", as a crop does.
- Whether the presence of next door should depend on the cover between (a wood blocks the view, open fields do not). Visibility
  is now the observed parcel's own; the parcel one looks from is not read.

## Affects

Every sign of own 0.5 or more on a parcel next to where one was: crops, fields, herds, buildings, people at work, fights, crows.
Night presence at one step (a sign in the night, from where one sleeps) uses the same factor.

## History

- 3 Nov: built at Zach's request, both parts, with tests (test_cybertron2_sign_bundles.py). The food probe's seven versions were
  rerun with the row fixed and next door still 0.1 (runs/gp_food2_*), from a snapshot of that code.

## Sources

review/38_space_engine/55_food_probe.md; guides/senses.md (rules 3 and 5).
