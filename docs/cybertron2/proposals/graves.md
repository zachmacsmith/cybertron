# Graves dug by many, over days; a cairn after burial; an unfinished grave's signs

**Status:** retrospective, accepted: D4-99 (4 Nov)
**Owner:** 37.4

## Summary

- A grave is now work that builds up on the body, like a building begun. Each `bury` act puts in up to 2 units, the share keeps
  between days, and anyone may add to it.
- The ground still sets the whole grave: 2 units soft, 4 stony, 6 frozen (D2-96).
- A cairn can be raised over a grave after the burial.
- An unfinished grave has signs.

## The proposal

As in the spec: world/things_in_places.md, "Burying" and the two items after it. Code:
- things.py: `graves`, `grave_done`, `grave_left`, `bury_need`, `grave_words`;
- verbs.py: `_bury`, `cost`, `_site`, `_thing_site`;
- knowledge.py: `where(graves=)`, `ready`;
- signs.py: THING rows for an unfinished grave and a new cairn; BURIAL rows for unfinished digging and for raising a cairn;
- here.py: `graves`, `grave_left`.

Presentation choices:
- The share is shown in words (barely begun, about a third, about half, two-thirds or more, nearly deep enough).
- Units left are shown only on a close look and in the digger's own result line.

## Why

The sweep of every run (38.58) found that a grave could not be dug in winter. Burial was one person's work in one act, a frozen
grave takes 6 units, and a winter day gives 5.
- In r1 about fifteen people pledged for five days to bury Sabina "while the crows are at her". Wilmot worked out why: "A burial
  takes 6 units in one day and winter only gives me 5, so I can't do it."
- In wb2 the starving party at the Holm stayed to dig Margery's grave, and three of them died there.

Zach: "do the burial fix. Do both: multiple people can contribute and it can be done over days. Add some senses for looking at an
unfinished grave as well", then "they should be able to add a cairn to the grave after burial". Osric's mother in h2 is the case for
the second: he was given stone for her cairn and could not raise it, because she was already buried.

## Alternatives considered

- **Lower the frozen cost to 5 or less.** That keeps one-person, one-day burial, but frost would no longer make burial a hardship
  shared by the village.
- **Only allow several people on the same day** (a crew). A lone survivor could still not bury anyone in winter.
- **Keep the body until the thaw** (a winter store for the dead, as was done historically). Left for later: it needs a building
  fitting and a rule for rot in the cold.

## Open questions

- Should hunger slow digging? Now one unit of work is one unit of grave, whoever digs.
- Should an open grave fill back in over time, or be dug out by beasts?
- Should a grave dug and then abandoned (the body taken away) remain as a pit?

## Affects

37.2: D2-96's numbers are unchanged; the act's share (2 units) is a new parameter marked calibrate. 37.1: the grave's progress is on
the remains container, as `grave: {done, by, day, began}`, with `cairn_day` and `cairn_by` for a cairn's signs.

## History

- 4 Nov: built at Zach's request, with tests: package A (a grave dug by two over two days, a thaw, a cairn after burial) and the
  sign bundles (an unfinished grave's signs; the digger's "not deep enough yet").

## Sources

review/38_space_engine/58_episodes.md; OPEN.md L-66; proposals/sign_bundles.md; guides/senses.md.
