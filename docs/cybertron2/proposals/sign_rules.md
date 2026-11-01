# No invented acts in signs; one's beasts kept short

**Status:** retrospective, accepted: D4-72, D4-73 (2 Nov)
**Owner:** 37.4

## Summary

1. A sign of a person shows their body and what they did, never an act or a feeling they did not choose: the bereavement signs
   ("was heard weeping", "goes about grey-faced and silent") and "is short with everyone" are removed. Signs about a building's
   dwellers apply only to buildings with beds (D4-72).
2. The list of one's household's beasts as one last knew of them drops groups that are no more when one sees the beasts, and shows
   the latest four (D4-73).

## The proposal

As summarised; rules in spec information/signs.md and perception.md; how to write signs in guides/senses.md.

## Why

- Margery was told by Everard on day 67 of c3 "I heard you weeping": the engine's bereavement sign had written a grief she never
  chose (signs.py, 15% a day per observer for five days after a death in the house). Zach (2 Nov): "Where did this sadness come from
  I did not include it?"; then "you can remove the invented behaviors signs".
- "The bins in the Byre look near empty" (172 times over seven runs, never acted on) and "a baby crying in the Byre" (62): the
  building signs counted everyone of the household as living in every household building, the cattle shed too.
- c3: Everard's list of the household's beasts held six groups, three of them empty and three named alike; up to 452 characters,
  in 102 of 251 messages. Zach: "maybe we should do something so it doesn't get spammed full of herd groups".

## Alternatives considered

- **Keep grief signs, chosen by the person:** an act of mourning a person may choose (a verb), shown as a sign of what they did. Not
  built; open.
- **Drop the beasts list:** it is the one place a person sees each group with where and when; 81 of 83 c3 memories track the herd.

## Open questions

1. Whether people get a way to show grief or other feeling by an act of their own.

## Affects

signs.py, perceive.py (remember_beasts), prompt.py (_beast_lines); spec information/signs.md, perception.md; guides/senses.md.

## History

- 2 Nov 2026: built at Zach's request; written down after (retrospective).

## Sources

runs c3_combe_rich, p1_combe_*; guides/senses.md (the measure of which signs are acted on).
