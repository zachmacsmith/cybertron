# Proposal: farming

**Status:** partly accepted: D2-11 to D2-18 (rest discussion). **Owner:** 37.2. **Affects:** spec/economy/production.md (farming),
spec/economy/goods.md (crops, seed), spec/economy/livestock.md (draught, dung), spec/world/holding.md and land (37.4: the plot unit,
house lots, pasture), spec/seeding (farming under way at day 0).

## Summary

Farming has a short minimum (sow and reap) and optional stages (break the soil, weed, manure, choose the next crop, graze the
fallow) that cost work and raise food per plot or keep the soil. A crop grows from the day it is sown; winter kills what is not
hardy. A ripe crop rots if not reaped in its window. By hand, the further stages raise food per plot about fivefold but lower food
per unit of work; cattle raise both. Where land is plentiful the minimum wins; where it is short, a village with a common herd farms
with about 30% less work per person than a household alone.

## The proposal

### Accepted (Zach, 22-23 Oct)

| Decision | Rule |
|---|---|
| D2-11 | the minimum is sow and reap; the other stages are optional, each costing work for a better return, worth most at scale |
| D2-12 | a harvest window: a ripe crop not reaped in time rots |
| D2-13 | worlds start with crops in the ground and last year's grain (and seed) in store |
| D2-14 | first worlds farm with the hoe and the ox plough only |
| D2-15 | more hands on a plot raise its yield on a saturating curve; cattle add to it |
| D2-16 | nodes differ in land pressure |
| D2-17 | seed is kept back from each harvest |
| D2-18 | the plough needs an ox, fodder takes land, dung keeps the soil; households need land to live on |

### Still in discussion

1. **Stages and their work** (02l §2): sow 0.5 a plot; break the soil with a hoe 3 or an ox plough 0.75 (+1.5x the seed); weeding up
   to +50% on a saturating curve; manure 1 (needs dung); reap 1.5 with a sickle, 2.5 bare-handed; threshing folded into reaping.
   Soil fertility multiplies the harvest; grain takes 15% of it, legumes, fallow, grazing and dung restore it toward a level.
2. **Crops counted from the day sown, the cold as the limit** (02l §3): grain (about a quarter of the year), winter grain (survives
   the cold), legumes (restore the soil, 60% of grain's food), garden (fast, spoils), hay (winter fodder). Growing the same crop
   twice raises the chance it fails (5% to 15%).
3. **The plot unit** rescaled to D4-23's definition (about what one adult can work in a season), with the hand method (hoe and
   weeding) as the reference; the ox plough then lets one adult work about 1.5-2 plots.
4. **A garden on the house lot,** worked with spare units.
5. **Sowing takes work per unit of seed** (Zach, 23 Oct: an agent's units should sow only a finite amount, with tools improving
   it). Proposal: sowing costs work per unit of seed, not per plot, so sowing densely costs more; a choice of **broadcasting** (fast,
   wastes seed) or **dibbling** (about three times the work, about 40% less seed for the same harvest), which matters after a bad
   harvest when seed is short (D2-17). The ox plough raises plots per adult; a seed drill comes much later (economy_later.md).

## Why

- Optional stages let the cheap path exist without making it the best path everywhere: the choice follows land and labour, so
  different nodes rationally farm differently (Boserup: people intensify when land runs short, not because it is easier).
- The harvest window and staggered sowing make labour a traded good at the peak: hired hands, turns at each other's fields,
  working late.
- Cattle and the common herd create the scale economy Zach asked for, and a commons problem that institutions answer.

## Alternatives considered

1. **The old engine's farming** (sow 1-3 seed, about 3x back after 3 rounds, two tends then nothing, a plough covering 2 plots):
   yield follows the seed, not labour or land, and there is no labour peak. Replaced by D2-11 and D2-15.
2. **Every stage required** (clear, break, sow, tend, reap, thresh): too much routine for food's share of work (scenario_design:
   at most 30%). Rejected for optional stages.
3. **Fixed sowing seasons:** simpler, but no staggering and no rotation by choice. Proposed instead: growth from the sowing day,
   with winter as the only seasonal limit.
4. **Slash and burn and irrigation in the first worlds:** deferred (D2-14; economy_later.md).

## Open questions

1. The absolute scale: at 02l's numbers the household rung feeds a person with about 10% of an adult's day before seed, milling,
   storage, winter and children; target about 25-30%.
2. Crop cycles as shares of the year or in days.
3. Weeding as one stage on a curve or several tends.
4. How lots, plots and pasture share a node's land (asked of 37.4 on the board, 23 Oct).
5. Sowing per unit of seed, and broadcasting against dibbling.

## History

- 22 Oct: 02d proposed technique ladders with foraging as the degenerate rung (Zach: foraging 1-2 actions for 1-3 food, H-6).
- 22 Oct: Zach asked how labour enters a farm, what the stages are, and whether there could be methods from crude to full
  (sowing, ploughing). 37.2 described the old engine's fields and proposed stages, a methods ladder, and output per plot against
  output per person.
- 23 Oct: Zach decided D2-11 to D2-18: optional stages with better returns, the harvest window, farming under way at the start,
  hoe and ox plough only, labour on a curve, land pressure, seed kept back, cattle on the farm, land to live on. Asked for
  different crops with different cycles, growth from the sowing day, and rotations that are better than others.
- 23 Oct: 02l_farming.md and 02l_farm_model.py written. Findings: the further stages by hand raise food per plot about fivefold and
  lower food per unit; cattle raise both; a village with a common herd needs about 30% less work per person where land is short;
  staggered sowing triples the harvest a household can bring in. A first model with fixed soil changes per crop put every rotation
  at the floor or the ceiling; replaced by recovery in proportion to the deficit.
- 23 Oct: 37.4's D4-23 answered the plot questions (plots whole, holdings divided, viability as land per mouth); 37.2 proposed
  adopting its plot unit with the hand method as reference.
- 23 Oct: Zach asked that sowing take finite work per agent, improved by tools; proposal 5 added.

## Sources

[02l_farming.md](../../review/37_growth/02l_farming.md), [02l_farm_model.py](../../review/37_growth/02l_farm_model.py),
[02d_ladders.md](../../review/37_growth/02d_ladders.md), [02b_productivity.md](../../review/37_growth/02b_productivity.md);
cybertron 1's `cybertron/camptypes/fields.py`; D2-11 to D2-18, D4-23, H-6.
