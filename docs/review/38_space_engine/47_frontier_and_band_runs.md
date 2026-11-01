# 38.47: The frontier and wild-band runs (f1_frontier, b1_wild)

Session 37.4, 2 Nov 2026. Zach asked for two small runs: do families that start with only camps build houses ("a few families
starting just with camps"), and can hunter-gatherers live in a large empty world ("Is the current design too biased toward the small
village lifestyle?"). He then added a raiding household ("savage raiders ... another family that starts out with plenty and weapons")
to the frontier. World files: `cybertron2/specs/make_frontier.py` writes `frontier_camps.yaml` and `wild_bands.yaml`.

## f1_frontier (paused at day 38 of 40, $24.73)

Three families in camps on separate nodes (the Ashes, the Brams, the Colds) and the Gorm household, a timber hall with weapons and
stores, as raiders. Evening, tags, ages and the belief view on.

**Building.** Every family built a wattle house within 4 days of the start, and moved out of the camps (the camps stood empty at the end).

| Household | Built | Fittings at day 38 |
|---|---|---|
| Cold (Edwin, Freya) | Coldhouse | 4 beds, bins, a hearth, a granary |
| Bram (Cuthbert; Delia died) | Bram House, a second begun and left unfinished | 3 beds, bins, a hearth |
| Ash (Aldo; Bryony died) | Ash House | 2 beds, bins, a fire ring |
| Gorm (Ulf, Hilde, Ketil; Rurik died) | a second room on the hall, Hilde's new house, two more begun | bins |

**The raiders did not raid.** The Gorm never attacked anyone. They talked themselves into trading, and one agreement was made in the run
(day 9, Cuthbert and Rurik, dried meat). Zero fights.

**Deaths.** Rurik (day 14) and Bryony (day 17) died on the road, of hunger, crossing empty country. The Brams saw Bryony on the road and
nobody spoke to anybody. Delia died in childbirth on day 22, the night Florence was born (housed and helped: the 2% mother's risk).

**Births.** Herbert (Freya, day 15) and Florence (Delia, day 22). 9 alive at day 38, against 10 at the start.

**What it shows.** Houses are built when the materials are at hand and a camp is the alternative: the families did not need
pressing. What failed was moving between places. Long walks with little food killed two of ten. Seeing someone in trouble did not
lead anyone to help.

## b1_wild (finished, 40 days, $10.82)

One band of four adults (Bran, Wren, Tam, Sorrel) in a large empty wild with no fields and no houses.

- **All four adults survived 40 days.** They moved on when the land was picked bare. They built 7 camps over the range (Deepholt,
  Birchlea, Wolfwood, Ashgrove, two of Tam's own) and lived on dried meat. They slept in camps, bedrolls and a tent.
- **Hunger bound without killing.** Missed meals over 40 days: Tam 9, Sorrel 5, Wren 3, Bran 2.
- **Wilmot**, Wren's son, born day 20 (housed, helped), died the next night of the ordinary infant risk. The weather was not cold,
  so where he slept did not change the odds. That night he was logged as sleeping "out" while Wren slept in Wolfwood camp. The
  camp was not his household's dwelling, so the bed rule placed him out. Fixed by D4-87 (a baby sleeps where its mother sleeps).
- **What was passed on.** Bran passed a line to the baby: "The band moves on when the land is picked bare, and never stays where it
  will starve."
- No agreements, no fights: one band, no one to deal with.

**What it shows.** The engine does support a mobile life: camps, fire rings and drying meat are enough to keep a band alive. The
design is not closed to hunter-gatherers. It is thin for them, though: no seasonal rounds, no stores cached along the range, and no
other bands to meet.

## Faults found and fixed

- A baby placed "out" while its mother was housed (b1 day 21): D4-87.
- The partner line told a survivor of a death they had not learned (f1: Aldo, "Bryony no longer shows as my partner"): D4-88.
- Requests for a request act and a clearer hunger sign were declined by Zach ("They are already expressible as is").

## Open

- Whether the frontier's last 2 days are worth running (`python -m cybertron2.engine resume runs/f1_frontier`).
- Houses favouring children, a baby's night risk by shelter, and births in a camp counted as partly housed: proposed, awaiting
  Zach.

*Current as of 2 Nov 2026.*
