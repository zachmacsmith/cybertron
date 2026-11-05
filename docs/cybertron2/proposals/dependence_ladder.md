# The dependence ladder (OPEN L-50)

**Status:** designed and generated, not run (the cheap ladder: 3 worlds, regenerated 3 Nov). Zach, 2 Nov: "design but don't build
yet. Like generate the worlds to see if the generator works, but don't run them". **Owner:** 37.2 (design); the runs would be
37.4's once Zach says go. Current as of 3 Nov.

## The question

Can a village that cannot feed itself buy its food from its neighbours, and at what point does it stop managing?

Review 02zl found that every past world with a village needing 13% or more of its people on the road each day to bring in food
failed. No past world had a short village that held, so we do not know whether the agents can carry any food dependence at all, or
where the line is. D2-190 makes dependence a warning, because some food specialisation matters, more so as societies grow. That
makes the line worth knowing.

## The design

A copper village (Minehead) with too little farmland, and two farming villages (Barrow and Wheatley) with food to spare. The
farmers have no stone or metal, so dependence runs both ways: Minehead needs food, the farmers need what only Minehead makes.
Wheatley sits between the other two: the junction, and the only way from Minehead to Barrow.

The worlds differ only in Minehead's fields (and, in the oxen arm, its oxen). The seed, the land, the sites, the roads, the
households, the people, their models, crafts and aims are identical in every world (checked: the casts match exactly).

### The cheap ladder (generated; Zach, 2 Nov: "regenerate the cheaper ladder")

`python cybertron2/specs/make_ladder.py` writes three worlds to cybertron2/specs/ladder/. They ask the main question first: can the
agents sustain food trade at all, and does transport help?

| | Minehead | Barrow | Wheatley |
| --- | --- | --- | --- |
| Households, people | 2, 7 | 1, 2 | 1, 4 (13 in all) |
| Models | 2 Opus, 1 Sonnet, 4 Haiku | 1 Opus, 1 Haiku | 1 Opus, 1 Sonnet, 2 Haiku |
| Holds | the copper seam (a rock parcel) | farmland at 0.42 of capacity | farmland at 0.42 of capacity |

| World | Minehead's people against what its land feeds | Carrying burden |
| --- | --- | --- |
| ladder_b00 | 0.61 (self-sufficient: the null arm) | 0 |
| ladder_b13 | 1.79 | 0.13 on foot: the lowest past failure (wb1) |
| ladder_b13_ox | 1.79, the same land as b13 | 0.02 by the measure: Minehead keeps its 2 oxen, and the head of the household that holds them is given a harness |

- **The top rung lands at 0.13, not the 0.15 asked for.** Fields come in whole plots, so a plot moves this small village a few
  hundredths, and the files are named by the burden they have.
- **12 days**, from summer day 3, with 8-day seasons (winter from day 14). In past regional failures, missed meals began by day 1 to
  3 and deaths by day 5 or 6; Minehead's harvest is on day 5.
- **Children off**, so births don't confound. **Lifespan 96**, so few die of age; the succession check flags nobody.
- **Opus at every village's head** (4: Minehead has two households); Sonnet and Haiku for the rest.
- **One replicate each at first: 3 runs.**
  - Cost by the published runs' records: about 13 people × 12 days × $0.15 to $0.20 a person-day, so roughly $25 to $30 a run and
    $75 to $90 in all.
  - That rate comes from the runs' `cost_usd`, which under the Claude Code backend may be a list-price figure. 37.4's Wenbridge
    figures imply less.
- **Its limit:** with one replicate it shows only a large effect, which way to look rather than where the line is.

### The full ladder (`--full`; generated on demand)

Four rungs (asked 0, 0.04, 0.08, 0.12; they land at 0, 0.04, 0.09, 0.15) and the oxen arm on the top rung:
- 21 people (households 3, 2, 2) over 20 days;
- 7 Opus, 4 Sonnet, 10 Haiku;
- two replicates each, 10 runs, roughly $1,250 by the same records (about $0.30 a person-day at 20 days).

It is worth running only once the cheap ladder shows something worth placing a line on.

### Both ladders

- **No pack oxen in Minehead's rungs on foot.** The copper village keeps its cows, but its oxen are removed after generation
  (`make_ladder.no_oxen`). An ox carries 60 to a person's 10, and the villages that failed had none.
- **The oxen arm** keeps them and gives a harness to the head of the household that holds them. An ox is led as a pack ox only with
  a harness in hand (`travel {lead}`, D2-136), and generated households hold none. What each outcome would mean:
  - **It holds where the rung on foot fails:** transport is the lever, and carts, caravans and traders (OPEN L-53) are what
    dependence at scale needs.
  - **Both fail:** the agents are not organising deliveries at all, and the fix is coordination (standing agreements, a carrier's
    role), not carriage.
  - **Both hold:** that much carrying on foot was not the line, and the past failures had another cause.
- **Region food:** about half of what the land keeps, so the food exists.

## Running it (when Zach says go)

```
python cybertron2/specs/make_ladder.py         # the cheap ladder (or --full)
python -m cybertron2.engine run cybertron2/specs/ladder/ladder_bNN.yaml --days 12 --out runs/ladder_bNN_rR
```

Read each run with `02zk_run_economics.py` and 37.4's `changes` audit:
- missed meals and hunger deaths in Minehead, against the null arm;
- grain moved into Minehead (agreements and gives);
- what went the other way (copper, tools, stone, coin);
- whether the junction village (Wheatley) took a cut;
- a qualitative reading of the end state, as scenario_design asks.

## What the full ladder's results would mean

- **Minehead holds at 0.09 and 0.15:** the agents can sustain dependence when both sides need each other. The past failures were
  about one-way dependence or worlds without something to sell, and the warning line moves up.
- **It holds at 0.04 and fails above:** a working line near 0.05 to 0.1. Generated worlds should keep food dependence under it
  unless a world means hardship.
- **It fails even at 0.04 while the null arm holds:** the agents do not sustain food trade at all, which is an agent finding. The
  fix is in perception, memory or agreements (standing deliveries), not in the land.

## Known weaknesses

- **The farmers' pull is weak within 12 or 20 days.** Copper tools raise yields by about half, but nothing forces a farmer to want them
  before the harvest. Coin and aims carry most of the incentive. A stronger arm would give the farmers a need only Minehead meets,
  such as a broken plough share; that could come later if the first ladder fails on demand rather than carrying.
- **There is one land.** A second seed would separate the rung from the geography (two seeds × four rungs × one replicate gives the
  same 8 runs).
- **Two replicates are few** for a curve with 4 points. The full ladder can show a step, not fit a threshold.
- **The cheap ladder's farming villages are small** (2 and 4 people). Barrow's two may have little time to spare for carrying or
  trading.

## Found while generating (fixed)

The ladder was the first world to pin a resource and a food share together. That exposed four generator bugs, now fixed and tested:
1. **A world file's own `features:` and `configuration_params:` were silently dropped.** The merge kept only keys that have
   defaults.
2. **Fields were sized as if waste ground gave food and woods did not.** capacity.py counts the reverse, so villages came out short
   of their target.
3. **A `resources:` pin allowed a site up to about 4 km from its ore, past the 2.5 km a village's land reaches, so no mine was
   made.** Two causes: `_spread` reaches farther than its steps (OPEN L-51), and the mine was taken after the farmland. The pin now
   tests the distance, the seam is taken first, and a pin not met is refused.
4. **The capacity check's tolerance was absolute.** It was too tight for high targets and for small villages, where one plot is a
   tenth of the land.

New: `food_share` and `heat_share` pins set a village's people against its land exactly.
