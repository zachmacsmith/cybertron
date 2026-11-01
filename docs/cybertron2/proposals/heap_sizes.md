# How much lies there: heaps seen by their bulk, counted when attended, and kept by their house

**Status:** retrospective, accepted: D4-89, D4-90, D4-91 (2 Nov)
**Owner:** 37.4

## Summary

Goods in the open are more conspicuous the more of them there are. They read in three degrees:
- from afar, a size;
- on a close look, a band per good;
- when attended to, a count.

A large spoiling store signs by its bulk, up to rats. Goods that overflow at a door stay the house's, so it can sell them, and
taking them is a theft. A fitting begun shows on its building.

## The proposal

As in the spec: information/noticing.md "How much lies there (D4-90)", world/things_in_places.md "Whose" (D4-89). The building
line reads "a water wheel and leat begun, its materials in (about 150 units of work left)" (D4-91).

Presentation choices:
- The bands are a fixed ladder (1, 2, 3, 5, 8, 12, 20, ...), not a range around the true amount, so the range does not give the
  count away by its midpoint.
- The count rounds to about 1 under 20 and about 5 above.
- Both are deterministic.
- Attending to a thing needs its tag and that one knows of it.

## Why

In the Wenbridge run wb1, about 100 grain from the Hearnes' harvest lay on the Green after their hut filled. Everyone saw "a heap of
grain and straw" with no amount. Zach (2 Nov):
- "Senses like that should scale with number ... it should say like 'a heap of around X to Y'";
- "attending to a heap should give more info about how much";
- "if there is that much rotting food, the sense should be much stronger ... much larger stenches, or rats";
- "the Hearnes should definitely be able to sell it"; "sure they can stay owned".

The overflow was nobody's (D2-87), so Joan took it freely and a buyer had no reason to pay.

The begun wheel was not shown anywhere. The lord and the carpenter planned to gather all of its materials anew, and nobody worked
on it in 14 days.

## Alternatives considered

- **A range centred on the true amount (±25%):** its midpoint gives the count away.
- **Overflow stays nobody's:** Zach first said so, then chose ownership once it was clear an unowned heap cannot be sold.
- **A large heap seen from the next parcel:** not built. Sight already reaches next door through presence; a heap's own above 1
  would need a cap change.

## Open questions

1. Whether covering a heap (with straw, or under brush) should slow its decay. Kit tried this in wb1; there is no such act.
2. Rats as a cause of loss, not only a sign. Today the rats row shows only what spoilage already does.

## Affects

data.py (THINGS heap_k, heap_large, heap_great, bands), things.py (own, band_words, count_words, goods_est, goods_count),
signs.py (THING rows, the count reach), perceive.py (count rows on attending; attending a thing's tag; own by row), world.py
(takeable), verbs.py (_take), buildings.py (space_words); tests/test_cybertron2_heap_senses.py, and two package A tests updated.

## History

- 2 Nov 2026: built at Zach's request during the wb1 pause; written down the same session (retrospective).

## Sources

runs/wb1_wenbridge (days 6 to 14); D2-87, D2-155, D4-23, D4-75, D4-81; docs/cybertron2/guides/senses.md.
