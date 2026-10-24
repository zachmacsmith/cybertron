# 38.31: the Wide Country, run w1 (24 good days, then the usage limit)

Session 37.4, 24 Oct 2026. World: cybertron2/specs/wide_s7.yaml (seven households, four villages, a frontier of eight places;
one model per household). Run: runs/w1_wide.

## 1. The run ended on the usage limit, not in the world

On day 25 (about 13:10 UTC) every model call began failing with "You've hit your session limit · resets 2:20pm (UTC)". The engine
took each failure as an empty reply, so the days went on with nobody acting: all 23 starved by day 73, within minutes of wall
time. **Only days 1 to 24 are a run;** nothing after day 24 says anything about the agents.

Fixed (d9e9448): a call that hits a usage or rate limit waits for the reset the error names (or 10 minutes) and is asked again; the
world does not move meanwhile. After 12 hours of waiting the run stops after saving. Test: test_cybertron2_journal.py. w1 began
on the code before R1 (38.29), so it has no journal and cannot be resumed from day 24.

Cost to day 24: $98 (API-equivalent). By model: Opus 4.7 $36 (Fenwick), Sonnet 4.6 $24 (Moor, two people), Opus 4.5 $12 (Wynn),
Opus 5.5 $8 (Rook), Haiku 4.5 $7, Sonnet 4.5 $4, Haiku 5.5 $0.3. Sonnet 4.6 and Opus 4.7 cost about three times as much a turn as
Opus 4.5 and 5.5.

## 2. Days 1 to 24

| | |
|---|---|
| People | 23, one birth (Helewise, Lucy Fenwick's, day 16), one death (Rose Rook, day 23, the adult nightly risk, then labelled "old age"; now "a sudden illness") |
| Food and fuel | 15 missed meals; 6 nights a lived-in house had no fire; winter came on day 14 |
| Agreements | 21 |
| Building | the Fenwicks built a cellar and then a new house at Stannick (room for the family they mean to have) |
| Clearing (D4-60) | first use: Rose cleared the Glade at Holloway into a field and the Rooks claimed and fenced it; Gunnild Reed was clearing Fen Meadow |

**The family households.** Only the Fenwicks (Opus 4.7) tried for children: 24 times, every day from day 0; Jory told his son
"If you and Lucy can, try for a child today too. We need the numbers before autumn turns." Lucy conceived on day 5. The Cotters
(Haiku 4.5) held the same kind of custom and never tried; they cared for their infant (43 care actions) and fenced and foraged.
The difference is the model, not the custom: both customs say "try for a child every day you can".

**The explorers.** The Rooks (Opus 5.5) and Reeds (Haiku 5.5) did what the others did, more hunting and foraging, and then turned
to land at home: the Rooks cleared and fenced the Glade, the Reeds cleared Fen Meadow. Of the frontier, only Payn Reed went to
Alder Carr (day 21). Simkin Rook went into the Weald (known country) and back. Nobody took the deer path to Deepdene, the drove road
to Riversmeet, or the pass. As in Hollins 2, a custom to go further did not survive winter food pressure.

**The others.** The Wynns (Opus 4.5) manured, weeded and selected seed, as their custom says; the Moors (Sonnet 4.6) cut hay,
fenced and herded; the Ashes (Sonnet 4.5) felled and made charcoal and moved goods (72 moves), their custom of trade.

## 3. For the next run

- Every run now keeps a journal (38.29) and waits out a usage limit; a run like this one could be resumed from its last step.
- A 120-day run of this world costs about $500 at this rate and is enough to hit a session limit; the limit, not the world, ended
  this one. Cheaper household models (Opus 4.5 or 5.5 instead of 4.7, Sonnet 4.5 instead of 4.6) would cut it by about a third.
- Explorers settle at home in winter. Starting in spring, or giving the frontier a visible reason (the old strips at Riversmeet
  can be seen from the drove road), would test whether they go.

*Current as of 24 Oct 2026.*
