# 37.2l Farming: optional stages, crops and rotations, cattle, and the harvest peak

*22 Oct 2026, with Zach. Design for cybertron2 (economy area, production). Numbers from [02l_farm_model.py](02l_farm_model.py): all
proposals; only the ratios between methods matter, and the absolute level is calibrated to food's share of work. Units are 38.06's
work units (6 a day for an adult; forage 1).*

## 1. What Zach decided (22 Oct)

| # | Decision |
|---|---|
| 1 | **The minimum is short; the other stages are optional.** Sow and reap is enough to get a crop. Each further stage costs work and gives a better return: more food per plot, or soil that does not wear out. The full process is worth much more to those who can do it, and more at scale |
| 2 | **A harvest window:** a ripe crop not reaped in time rots |
| 3 | **Worlds start with farming under way:** crops in the ground, last year's grain in store |
| 3b | Different crops with different cycles; growth counted **from the day sown**, so plots can be rotated (Zach's question; §3 is the proposal) |
| 4 | First worlds: **the hoe and the ox plough** only |
| 5 | **More hands on a plot raise its yield**, on a saturating curve; cattle add to it; part of the return to labour comes from doing the further stages |
| 6 | **Nodes differ in land pressure** (some short of land, some of people) |
| 7 | **Seed is kept back** from the harvest |
| 8 | **Cattle on the farm:** the plough needs an ox, fodder takes land, dung keeps the soil; households need **land to live on**, with a capacity |

## 2. The stages

| Stage | Optional? | Work (a plot) | What it does | Needs |
|---|---|---|---|---|
| **sow** | no | 0.5 | puts seed in the ground (3 grain a plot); the crop's cycle starts that day | seed |
| break the soil | yes | hoe 3; ox plough 0.75 | a seed bed: harvest +1.5x the seed | a hoe (hand tool); or an ox and a plough |
| weed and guard | yes | any amount | up to +50% of the harvest, on a saturating curve (1 unit +24%, 2 +37%, 3 +43%) | hands |
| manure | yes | 1 | restores the soil toward above its natural level | dung: cattle |
| choose the next crop | yes (a choice, not work) | 0 | legumes or fallow restore the soil; the same crop twice raises the chance it fails (5% to 15%) | seed of that crop |
| graze the fallow | yes | herding | the herd's dung restores a fallow plot fastest | cattle |
| **reap** | no | 1.5 with a sickle, 2.5 bare-handed | brings the crop in as grain (threshing folded in); straw as a by-product (winter fodder) | the window |

**Soil.** Fertility multiplies the harvest. Each grain crop takes 15% of it; legumes, fallow, grazing and dung restore it toward a
level, in proportion to how far below that level it is. So every rotation settles at its own level: grain every time at about 0.43,
grain then fallow 0.85, a rotation with grazed fallow about 1.04, manure about 0.97.

**The harvest window.** A crop is ripe for two days; after that it loses a quarter of what is left each day.

## 3. Crops, cycles and rotations (proposal for Zach's 3b)

**Growth is counted from the day sown, not from a fixed season.** That lets a household stagger its sowing, which spreads the
harvest peak (§5), and rotate plots freely. **The season still matters through the cold:** a crop that is growing when winter comes
dies unless it is hardy. That keeps 37.4's calendar meaningful (D4-17, daylight by season) without fixing sowing dates.

| Crop | Cycle (share of the year) | Food | Soil | Keeps | Role |
|---|---|---|---|---|---|
| **grain** (barley, wheat) | about 1/4 | the staple | takes 15% | well (stores, carries) | food and seed; straw for winter fodder |
| **winter grain** (rye) | about 1/3, sown before winter | a little less | takes 15% | well | the only crop that survives the cold: a way to use winter land |
| **legumes** (beans, peas) | about 1/6 | 60% of grain's | restores (40% of the gap) | fairly well | the rotation crop: food while the soil recovers |
| **garden** (roots, greens) | about 1/10 | small | neutral | spoils fast | on the house lot (§6): fills spare units, eaten fresh |
| **hay** (cut from pasture) | regrows | none for people | none | well, dry | winter fodder for cattle |

**Why rotations differ in value**, with only two pieces of state per plot (fertility, and the crop grown last):
- **grain every time** wears the soil down to about 0.43 and fails three times as often;
- **grain, then legumes** keeps the soil and gives food in the rest year;
- **grain, legumes, grazed fallow** (the three-field system) keeps it highest, but only with cattle to graze it.

Five crops are the most this needs; first worlds could start with grain, legumes and hay, with the garden on the house lot.

## 4. The ladder (one plot, per crop slot; a slot is one crop's time on the plot, fallow included)

| Method | Work a slot | Net food a slot | Food per unit | Soil at grain |
|---|---|---|---|---|
| sow and reap, fresh land (the first years) | 2.00 | 4.65 | 2.32 | 1.00 |
| sow and reap, grain every time (worn soil) | 2.00 | 0.26 | 0.13 | 0.43 |
| sow and reap, grain then fallow | 1.00 | 2.13 | 2.13 | 0.85 |
| + hoe | 2.50 | 3.95 | 1.58 | 0.85 |
| + hoe + weeding (2 units) | 3.50 | 5.96 | 1.70 | 0.85 |
| + hoe + weeding, grain then legumes | 7.00 | 9.72 | 1.39 | 0.85 |
| ox plough + weeding, grain, legumes, grazed fallow | 3.17 | 7.62 | 2.41 | 1.04 |
| ox plough + weeding + manure, grain then legumes | 5.25 | 10.77 | 2.05 | 0.97 |

**The finding: the further stages raise food per plot about fivefold (2.1 to 10.8), but by hand they lower food per unit of
work.** Hoeing and weeding make the land yield more and the farmer work more for each food. Cattle are what raise both: the ox
plough with grazed fallow is the best per unit and among the best per plot. This is Boserup's pattern: people intensify when land
runs short, not because it is easier.

## 5. Which method wins depends on land per person, and on scale

The method that feeds everyone with the least work per person a day, including the cattle (hay, the ox's and plough's capital, and
herding: any herd needs watching, at least 1 unit a day; one herder watches about 30 head). Year of 40 days, two crop slots a plot
a year:

| Plots a person | Household of 4 | Units a person a day | Village of 20 (a common herd) | Units a person a day |
|---|---|---|---|---|
| 1.5 | cannot feed itself | - | cannot feed itself | - |
| 2 | ox plough + manure, grain-legume | 0.81 | ox plough + manure, grain-legume | **0.56** |
| 3 | hoe + weeding, grain-legume | 0.72 | ox plough, grain-legume-grazed fallow | **0.51** |
| 5 | hoe + weeding | 0.59 | ox plough, three fields | 0.53 |
| 8 | hoe + weeding | 0.59 | ox plough, three fields | 0.58 |
| 12 | sow and reap, grain then fallow | 0.47 | sow and reap, grain then fallow | 0.47 |

What follows:
- **Where land is plentiful, the minimum wins:** sow, reap, leave half the land fallow. No one should bother with the full process.
- **Where land is short, the full process is the only way to eat,** and a village does it with about 30% less work per person than a
  household alone, because it shares a herd: one herder for everyone's cattle, against each household watching its own one or two
  animals. That is the scale Zach asked for, and it is a real one: the common herd and the open field.
- **The common herd brings a commons problem:** who herds, whose animals graze where, overgrazing. Rules for it are an institution.
- **Children change the household's sums.** Herding is the classic child's work; if children's units are cheap (37.1, D4-19's
  menial tasks), a household's own ox becomes viable sooner. That is a deliberate link to demography.
- With one crop slot a year instead of two, every threshold doubles: a cold world (a short season) needs twice the land per person.

**When an ox pays on its own** (draught only, against the hoe): it must break about 3-11 plots a year, depending on the year's
length and crops a year (the model's table). Its dung lowers that a little.

## 6. Land to live on (Zach's 8)

A household needs a **house lot** on the node's land (37.4's lots: buildings by kind), which also holds a **garden** (a fraction of a
plot, fast crops, worked with spare units). Lots and fields come out of the same land: a growing village either builds on fields,
clears forest, or builds upward (02i §2c: storeys need stone). That is the land-pressure link between housing and food. The
interface (how a node's land divides between covers, lots and plots) is 37.4's: asked on the board.

## 7. The harvest peak

Plots a household can reap within the two-day window (1.5 units a plot):

| Adults | Working late | Plots, sown on one day | Plots, sown on three days a window apart |
|---|---|---|---|
| 1 | no | 8 | 24 |
| 2 | no | 16 | 48 |
| 2 | +2 units | 21 | 64 |
| 4 | no | 32 | 96 |

- **Staggered sowing triples what a household can bring in.** That is why growth counted from sowing (§3) matters: it is a skill
  agents can discover.
- **Beyond that, they need help:** hired hands, households reaping each other's fields in turn, working late (38.06). The peak is
  where labour is traded.

## 8. Starting a world with farming under way (Zach's 3)

At day 0 each field plot has: its holder; its last crops (so its fertility is what its past rotation left); a crop growing (sown on
a drawn day, so some ripen early in the run and the peak is spread); and each household has last year's grain in store (seed
included) and its cattle. Agents learn their plots' state as seeded knowledge (D4-21).

## 9. Open

1. The absolute scale: one plot's size, seed and yields, set so that food takes its target share of work (the model's
   household rung feeds a person with about 10% of an adult's day before seed, milling, storage, winter and children; target
   about 25-30%). Calibrated in dry runs.
2. Crop cycles as shares of the year (proposed above) or in days.
3. Whether the garden is on every house lot.
4. The land interface: lots, plots, pasture, house land (37.4, board).
5. Whether weeding counts as one stage with a curve (proposed) or several tends.
