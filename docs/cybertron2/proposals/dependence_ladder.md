# The dependence ladder (OPEN L-50)

Status: **designed and generated, not run** (Zach, 2 Nov: "design but don't build yet. Like generate the worlds to see if the
generator works, but don't run them"). The proposal is 37.2's; the runs would be 37.4's once Zach says go. Current as of 2 Nov.

## The question

Can a village that cannot feed itself buy its food from its neighbours, and at what point does it stop managing?

Review 02zl found that every past world with a village needing 13% or more of its people on the road each day to bring in food
failed. No past world had a short village that held, so we do not know whether the agents can carry any food dependence at all, or
where the line is. D2-190 makes dependence a warning, because some food specialisation matters, more so as societies grow. That
makes the line worth knowing.

## The design

A copper village (Minehead) with too little farmland, and two farming villages (Barrow and Wheatley) with food to spare. The
farmers have no stone or metal, so dependence runs both ways: Minehead needs food, the farmers need what only Minehead makes.

| | Minehead | Barrow | Wheatley |
| --- | --- | --- | --- |
| Households, people | 3, 8 | 2, 6 | 2, 7 (21 in all) |
| Holds | the copper seam (a rock parcel) | farmland at 0.6 of capacity | farmland at 0.47 of capacity |
| Trades | smelters (Cotters, copper tools); quarrymen (Haywards); builders (Bells) | farming | farming |
| Roads | Wheatley, 1 day (a stopping place on it) | Wheatley, 1 day | both |

Wheatley sits between the other two: the junction, and the only way from Minehead to Barrow.

The rungs differ only in Minehead's fields. The seed, the land, the sites, the roads, the households, the people, their models,
crafts and aims are identical in every rung (checked: the casts match exactly).

| World | Minehead's people against what its land feeds | Carrying burden |
| --- | --- | --- |
| ladder_b00 | 0.62 (self-sufficient: the null arm) | 0 |
| ladder_b04 | 1.16 | 0.04 |
| ladder_b09 | 1.48 | 0.09 |
| ladder_b15 | 2.05 | 0.15 (above every past failure) |

0.08 and 0.12 were asked for; fields come in whole plots, so a plot moves this village about 0.05, and the files are named by the
burden they have.

- **Settings:**
  - 20 days, from summer day 3, with 8-day seasons (winter from day 14);
  - children off, so births don't confound;
  - lifespan 96, so few die of age; the succession check flags nobody.
- **Models:** 7 Opus (every household head), 4 Sonnet (one per household, spread), 10 Haiku.
- **No pack oxen in Minehead.** The copper village keeps its cows but its oxen are removed after generation (`make_ladder.no_oxen`).
  An ox carries 60 to a person's 10, and with one the burden at the top rung falls from 0.15 to about 0.03. The villages that
  failed had none.
- **Region food:** about 0.5 to 0.65 of what the land keeps, so the food exists.

## Running it (when Zach says go)

```
python cybertron2/specs/make_ladder.py         # regenerates cybertron2/specs/ladder/
python -m cybertron2.engine run cybertron2/specs/ladder/ladder_bNN.yaml --days 20 --out runs/ladder_bNN_rR
```

- Two replicates each, so 8 runs. Rough cost: wb2 cost $17 for 14 people over 30 days. This cast is larger but mostly Haiku, so
  about $15 to $20 a run, or $120 to $160 in all. That figure is a guess.
- Read each run with `02zk_run_economics.py` and 37.4's `changes` audit:
  - missed meals and hunger deaths in Minehead, against the null arm;
  - grain moved into Minehead (agreements and gives);
  - what went the other way (copper, tools, stone, coin);
  - whether the junction village (Wheatley) took a cut.
- A qualitative reading of the end state, as scenario_design asks.

## What each result would mean

- **Minehead holds at 0.09 and 0.15:** the agents can sustain dependence when both sides need each other. The past failures were
  about one-way dependence or worlds without something to sell, and the warning line moves up.
- **It holds at 0.04 and fails above:** a working line near 0.05 to 0.1. Generated worlds should keep food dependence under it
  unless a world means hardship.
- **It fails even at 0.04 while the null arm holds:** the agents do not sustain food trade at all, which is an agent finding. The
  fix is in perception, memory or agreements (standing deliveries), not in the land.

## Known weaknesses

- **The farmers' pull is weak within 20 days.** Copper tools raise yields by about half, but nothing forces a farmer to want them
  before the harvest. Coin and aims carry most of the incentive. A stronger arm would give the farmers a need only Minehead meets,
  such as a broken plough share; that could come later if the first ladder fails on demand rather than carrying.
- **There is one land.** A second seed would separate the rung from the geography (two seeds × four rungs × one replicate gives the
  same 8 runs).
- **Two replicates are few** for a curve with 4 points. The ladder can show a step, not fit a threshold.

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
