# 02zi: build brief for 37.4: plot shares and a crop for each holding

Session 37.2, 3 Nov 2026. **Zach asked for this to be built** (3 Nov: "option C for crops, go ahead with plot shares").
Decisions:
- D2-163: land is held in plot shares within a parcel;
- D2-172: a field carries one crop for each holding on it.

Spec:
- world/holding.md §Plots (37.4's), which already says land is held in whole plots and holdings are divided, never plots; please
  bring its mechanics in line with this brief;
- economy/production.md "Farming" (37.2's, current as of 3 Nov).

Build nothing beyond this brief (README rule 10).

## Why

The engine claims whole parcels. Partible inheritance, land per mouth, encroachment and disputes over "three plots of Long Field"
can't happen. With shares, one field can be farmed by several households, and the old open-field pressures appear on their own.

## 1. Claims in plots

- **Shares:** a claim on a field, pasture or meadow may name a number of its plots (`plots: n`); without one it covers all of them,
  as now.
- **Overlaps are disputes:** claims on one parcel can sum to more than its plots. The engine records both and refuses neither
  (D4-23: the engine enforces only possession).
- **Unclaimed plots** are the parcel's plots less what its claims cover, at least 0.
- **`claim {thing, plots?, for?}`:** claiming unclaimed plots is a claim like any other. Claiming plots others hold is allowed, and
  seen as a dispute.
- **Moving plots:** a new agreement leg moves n plots of a parcel from one party to another (the routed claim primitive, D4-23):
  "2 plots of Long Field". This makes land sale and exchange possible.
- **Inheritance** passes whole plots by the household's rule (D2-143; life.py's rule):
  - partible: whole plots among heirs, eldest first;
  - where there are more heirs than plots, held jointly;
  - eldest: all of them to one heir.
- **Clearing** (D4-60) claims all the cleared parcel's plots, as now.
- **Pasture and meadow:** they hold shares too, but grazing and hay stay whole-parcel for now. Any holder's herd grazes the whole
  pasture.

## 2. A crop for each holding (fields)

**The record.** A field's crop record becomes one record for each holding: holder (a party), plots, kind, seed, broken share,
weeding, sown day, sower, fertility, failed. Plots sown can't exceed the field's plots.

**The acts:**
- **Sowing** (`sow {at, plots?, for?}`) sows the sower's own (or the `for` party's) held plots that are unsown, then unclaimed
  plots. To sow plots another holds, one must name them (`on: <party>`). It is allowed and seen.
- **Breaking, weeding and manuring** apply to one's own holding's crop by default, and to another's when named.
- **Reaping** reaps one's own holding by default. Reaping another's is allowed (a crop is nobody's until reaped, production.md); the
  grain goes to the reaper. It is seen and remembered as reaping the Webbs' plots, and may be disputed.

**Soil and stock:**
- **Fertility** is kept per holding, so a holder who rotates gains. Unclaimed plots carry the parcel's level, and fertility follows
  plots when they move.
- **Herds on a field:** they graze stubble and fallow across the parcel, and trample standing crops in proportion to each
  holding's plots, using today's trampling rate.

**What follows:**
- **Fences** stay round the whole parcel (D2-130), so one holding can't be fenced off.
- **Signs** are per crop record and name the holder where known: "the Reeds' barley in Long Field is ripe".

## 3. What agents see

The parcel's line, as last seen:

"Long Field (field; 6 plots): barley on 4 (Reeds 3, Webbs 1), beans on 1 (Coles), 1 fallow; held: Reeds 3, Webbs 2, Coles 1"

- Claims they know of are in plots.
- A dispute shows as two claims on the same plots: "the Wynns claim 2 of the Reeds' plots".

## Tests

| Test |
|---|
| two households holding 3 and 2 plots of a 6-plot field each sow their own; the line shows both crops and 1 unclaimed plot |
| sowing past one's held plots sows the unclaimed plot, then stops; sowing another's plots needs `on` and is seen |
| reaping another holding's crop gives the grain to the reaper and is noticed by those working the field |
| a holding sown with beans after barley gains fertility while the next holding, barley twice, loses it |
| a herd let onto the field tramples the standing crops in proportion to their plots |
| a partible inheritance of 5 plots by 2 heirs gives 3 and 2; by 6 heirs, 5 single plots and one share held jointly |
| an offer leg of "2 plots of Long Field" accepted moves the claim; the line shows the new holders |
| an existing world with whole-parcel claims runs unchanged (a whole claim is all the plots) |
