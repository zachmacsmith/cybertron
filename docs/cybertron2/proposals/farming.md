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

### Raising what a plot can produce (23 Oct, discussion)

Zach: skill should raise some production, not only cut work; and something (infrastructure or skill) should raise a plot's total
capacity. What already does: weeding raises the harvest; manure and a grazed fallow lift fertility above the soil's natural level
(to about 1.15). What is missing is anything **permanent**. Proposed for the first worlds:

| Lever | What it does to a plot | Cost | Who it belongs to |
|---|---|---|---|
| **a master farmer's skill** (D2-52) | yield x1.2 at mastery, and the work x0.7 | a season's practice | the farmer |
| **ditches and banks** (field works) | the plot's natural fertility rises from 1.0 to about 1.2; less loss to wet years and straying animals | about 20 units of a crew's work a plot, and upkeep each season | **the plot**: it stays with the land when it changes hands |
| **terraces** (hill land) | a hill plot yields like a valley plot | about 30 units a plot, stone | the plot |
| **seed selection** (a technique, learned by practice) | the sower's crops ripen about 15% sooner, so more harvests fit in a season | practice over several harvests | the farmer |
| irrigation (later: D2-14) | a much larger rise on river land | a crew, a channel, an institution to share the water | the plot and the channel |

**Decided:** master skill (D2-64), seed selection (D2-65). **Field works, worked out (23 Oct):**

*How they work.* A field work is a **project on a plot** (like a building: a total of work, done over days by one or several
people with `work {what: "ditch and bank", at: "<plot>"}`), and when done it is **part of the plot** (it stays with the land when
the plot changes hands: claims, D4-23). It needs **upkeep** each season or it decays a level. A crew needs **one person who knows
the technique** (field works: a farmer's technique, D2-43); the others can be anyone working for the plot's holder (D2-37).

*What agents see.* On the plot: "the Long Field, plot 3: wet ground; ditched and banked (the banks need mending: about half a
day's work)". On a project: "the ditches round plot 3 are about half dug". The soil word improves ("well drained").

| Work | Where it pays | Labour (units) | Materials | Tools | Upkeep a year | Gain a year (food) | Pays back, land plentiful | land short |
|---|---|---|---|---|---|---|---|---|
| **ditches and banks** | **wet land** (valley floors, fen edges): yield +35%, less flood loss | 40 (a crew of 4: under 2 days) | none (optional hedge stakes) | hand tools (digging wears them: factor 1.5) | 6 | about 56 | about 40-66 days | about 19-32 days |
| ditches and banks | ordinary land: +10% | 40 | none | hand tools | 6 | about 16 | about a year to 600 days: **does not pay** | about 96-160 days |
| **terraces** | **hill land** (yields x0.6 untreated): brought to a valley plot's yield, erosion stopped | 60 | about 6 stone (fieldstone) | hand tools | 6 | about 64 | about 55-92 days | about 27-45 days |

So ditches are for wet ground and terraces for hills, and neither is worth it on ordinary land unless land is short. Both pay back
over more days than one run, so they test whether agents invest for their heirs; seeded worlds start with some plots improved.

**What the works protect against does not exist yet (checked 23 Oct).** Neither the engine nor the spec has floods, droughts or crop
disease: the scheduler (spec/environment/scheduler.md) names a flood only as an example of an incident kind, and none is defined;
"a fever" appears only as a cause of death in generated family histories. The old engine's 5% blight was not ported. D2-53 says a
crop sown twice running is likelier to fail, which needs a failure draw that does not exist. So ditches (wet years), terraces
(erosion) and irrigation (dry spells) need **37.4's incidents and cycles first**: wet and dry spells by season and land kind
(38.04's climate axes: a valley "suffers wet", grassland "suffers dry"), river floods, and a crop-failure (blight) draw.

**Irrigation: what it does.** Crops need water while they grow. Proposed, with 37.4's weather: each growing day a plot is wet
enough, dry, or flooded, from the season, the spell (dry or wet, drawn by the scheduler) and its land kind. A dry day cuts the
crop's eventual harvest a little; a run of dry days can ruin it. **An irrigated plot is never dry while the channel runs**, so:
1. **it is safe in a drought**, the main reason irrigation was built: the harvest does not fail when the rain does;
2. **it yields more in an ordinary year** wherever rain is short of what the crop wants (about +30-50% on dry land kinds, little
   on wet ones);
3. **it can grow a crop in the dry season,** when unwatered plots lie idle, so more harvests a year;
4. **it can turn dry grassland into fields** that would otherwise not be worth sowing.

**How it works.**
- **Parts:** a weir and headgate at the river (about 10 stone, 6 timber, 20 units; a mason and a carpenter), a main channel (about
  120 units: a crew of 6 for three or four days), and a field channel to each plot (about 15 units each). One channel serves about
  8 plots on the river side, more on flat land.
- **Water is finite.** The river gives the channel a flow that falls in a dry spell; in a dry spell the channel cannot water every
  plot at once, so plots take **turns**. Whoever controls the headgate (`set {thing: headgate, setting: open | shut | turns}`)
  controls the water: an office (a water bailiff) or a holder.
- **Upkeep:** silt cleared each season (about 30 units, shared); a flood can breach the weir (repair work); a gate left open in a
  flood lets the river into the fields.
- **Knowledge:** water works is a rare technique (a master's, often from elsewhere), so building one depends on finding or
  hiring someone who knows it.
- **What agents see:** "the river channel: running, low (dry spell); the Reed and Fenn plots take turns, the Reeds' day today";
  on a plot, "watered" or "dry".
- **Institutions it needs:** water shares (a claim on the channel, D4-23), turns, upkeep as dues in work (agreements), and a way to
  settle quarrels (upstream against downstream; the mill's leat against the fields).
- **Payback:** each served plot's share (about 34 units) pays back in about 11-35 days when dry spells are common; where rain is
  reliable it hardly pays. Its value is set by the weather, as it should be.

Together these lift the ceiling by about x1.7 on top of the methods, mill and bread (food ladder, recipes.md §16). **Works that
belong to the plot make tenure matter:** who pays for the ditches, and who gains if the land is let or inherited (D4-23; a lease's
terms in agreements). That is the old engine's lesson (review 15 §2.7) carried over.

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

## Decided since (23 Oct)

- D2-53: crops from the sowing day, the cold as the limit (proposal 2 above). D2-54: sowing work per unit of seed; broadcast or
  dibble (proposal 5). The plot unit (3) is being rescaled in 02n; the garden (4) is still open.

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

- 23 Oct: Zach moved crops and the cold (D2-53) and sowing per seed (D2-54) from proposal to spec.

- 23 Oct (analyses): [02n_labour.md](../../review/37_growth/02n_labour.md): a plot as D4-23 defines it is about 5.4 of 02l's
  small plots (about 16 seed a sowing); by hoe and weeding one adult works 1.0 plot; the ox reaches 1.5-2 plots an adult only
  without weeding (weeding and reaping dominate). At the engine's rates a net ration costs about 0.5 units (the critique's 8% holds);
  food reaches 25-30% only with grinding (0.2-0.25 a ration), grain costing about 0.85 units a ration (a lower return than the
  engine's 5x), and a real dependency ratio. Recommended for Zach: the plot unit, grain's cost, grain spoiling about 1% a day.

- 23 Oct: Zach: skill should raise some production; something should raise a plot's total capacity. Proposed: master skill x1.2
  yield and x0.7 work; ditches and banks, terraces (works that belong to the plot); seed selection; irrigation later.

- 23 Oct: Zach: master skill yes (D2-64); seed selection yes (D2-65); how would field works and irrigation actually work? Worked
  out: field works as projects on a plot with upkeep, led by someone who knows the technique; ditches pay only on wet land, terraces
  on hills; irrigation's parts, costs and the institution it needs.

- 23 Oct: Zach: do floods and crop disease exist now (no: they need 37.4's incidents); flesh out irrigation and say what it does.
  Added: irrigation's effects through a plot's water each growing day, finite water and turns, the headgate's controller, upkeep,
  knowledge, what agents see, and the institutions.

## Sources

[02l_farming.md](../../review/37_growth/02l_farming.md), [02l_farm_model.py](../../review/37_growth/02l_farm_model.py),
[02d_ladders.md](../../review/37_growth/02d_ladders.md), [02b_productivity.md](../../review/37_growth/02b_productivity.md);
cybertron 1's `cybertron/camptypes/fields.py`; D2-11 to D2-18, D4-23, H-6.
