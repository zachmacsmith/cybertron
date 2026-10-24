# Production: foraging, farming and tools

## Summary

Food comes from foraging (the bottom rung) and from fields. Farming has a short minimum (sow, reap) and optional stages that cost
work and raise the return. Crops ripen into a harvest window. Seed is kept back. Cattle pull the plough and dung the soil. Tools are
a small set chosen by what each depends on. The rest of production (recipes, the production shapes, workshops)
is in proposals.

## Decided

- H-6: foraging is the degenerate case: 1-2 actions for 1-3 food, more with hunting parties.
- D2-11: the minimum is sow and reap; breaking the soil, weeding, manure, rotation and grazing the fallow are optional stages, each
  costing work and giving a better return (more food per plot, or soil that does not wear out).
- D2-12: a ripe crop not reaped within its window rots.
- D2-13: worlds start with crops in the ground and last year's grain and seed in store.
- D2-14: first worlds farm with the hoe and the ox plough only.
- D2-15: more hands on a plot raise its yield on a saturating curve.
- D2-16: nodes differ in land pressure.
- D2-17: seed is kept back from each harvest.
- D2-18: the plough needs an ox; fodder takes land; dung keeps the soil.
- D2-19: first worlds have a short metal ladder.
- D2-23: the tool set below.
- D2-43: the basic techniques and the ten trades below.
- D2-52: skill by practice on all work. D2-53: crops from the sowing day; the cold kills what is not hardy. D2-54: sowing work per
  unit of seed; broadcast or dibble.
- D2-156, D2-157: wood: felling, cutting young growth, gathering firewood.
- D2-58: grain spoils a little (house, bins, cellar). D2-59: the plot takes about 16 seed a sowing.
- D2-60: the food ladder (whole 0.7, ground 1.0, bread 1.3). D2-61: the mill ladder. D2-62: dried meat.
- D2-66: field works (ditches and banks on wet ground, terraces on hills). D2-67: irrigation later.
- D2-46: weapons wear, with a small chance of breaking. D2-47: cheese. D2-48: specialised tools.

## Mechanics

### Farming

| Stage | Required | Effect | Needs |
|---|---|---|---|
| sow | yes | puts seed on a plot; the crop starts growing | seed from the sower's stock |
| break the soil | no | a better seed bed: a larger harvest | a hoe, or an ox with a plough and harness |
| weed and guard | no | a larger harvest, each further unit of work adding less | work |
| manure | no | restores the plot's fertility | dung (cattle) |
| choose the next crop, graze the fallow | no | restores fertility; varying the crop lowers the chance it fails | seed of another crop; cattle to graze |
| reap | yes | the crop becomes grain carried by the reaper (D4-23: a crop belongs to nobody until reaped) | the crop ripe and within its window |

- **Crops** (D2-53): grain, winter grain (hardy), legumes (restore the soil; less food), a garden (fast; spoils) and hay (fodder).
  A crop ripens a fixed number of days after the day it is sown; one still growing when winter comes dies unless it is hardy.
  The same crop sown twice running on a plot is likelier to fail.
- **Sowing** (D2-54) costs work per unit of seed, so a day sows only so much. **Broadcasting** is fast and wastes seed;
  **dibbling** takes about three times the work and about 40% less seed for the same harvest.
- Each plot has a **fertility** that multiplies its harvest; cropping lowers it; the optional stages restore it.
- A crop that is ripe and not reaped within the window loses part of what is left each day.
- A harvest returns several times the seed; keeping seed for the next sowing is the holder's choice (D2-17), and a household that
  eats its seed cannot sow.

### Tools (D2-23)

| Tool | Used in | Effect | Grades |
|---|---|---|---|
| hand tools (one good) | farming by hand, felling, quarrying, mining, reaping | raise yield or cut the work of these actions; wear out with use | crude, then metal (D2-19: one metal rung first) |
| plough | breaking the soil | far less work a plot than the hoe | needs an ox and a harness |
| harness | an ox pulling a plough or a cart | gives the ox its use | |
| saddle | a horse carrying a rider | gives the horse its use | |
| cart | transport (transport.md) | | |
| weapons | fighting and hunting | strength in a fight; a better catch hunting | crude, blade |
| trap | at a forest site | catches game overnight while the trapper is elsewhere; checked by a visit; depletes game like hunting; can be emptied by whoever checks it | |

### Wood (D2-156, D2-157)

| Technique | Where | Takes | Work | Gives |
|---|---|---|---|---|
| gather firewood | a forest or scrub parcel | dead wood | 1 unit, no tool; basic; children may | about 3 firewood (fewer as the dead wood thins) |
| cut young growth | a forest or scrub parcel | young growth | 1 unit, a tool | about 5 firewood |
| fell | a forest parcel | trees | 2 units, a tool (crude 1.0, copper 2.0) | 3 timber; 3 firewood of brash left as dead wood |
| burn charcoal | at a wood | 5 timber | 2 units (woodsman) | 1 charcoal |

### Field works (D2-66)

| Work | Ground | Effect | Labour | Materials | Upkeep |
|---|---|---|---|---|---|
| ditches and banks | wet (valley floors, fen edges) | the plot yields x1.0 instead of x0.75 | about 40 units | none; hand tools | about 1.5 units a season |
| terraces | hill | the plot yields x1.0 instead of x0.6 | about 60 units | about 6 stone (fieldstone) | about 1.5 units a season |

- A field work is a **project on a plot**: work added over days by anyone (`work {what, at}`), with at least one person in the crew
  who knows the technique (a farmer's: field works). When finished it is **part of the plot** and passes with it (world/holding.md).
- **Upkeep:** each season the holder's side must put in the upkeep or the work loses half its effect, and all of it the season
  after.
- The fixed penalties for wet and hill ground stand in for weather: when 37.4's wet and dry spells, floods and erosion exist, the
  works act on those instead (D2-66).
- Agents see the ground and the works on the plot in words ("wet ground; ditched and banked; the banks need mending").

- **Fences** round a parcel (wood, or stone led by a mason) are field works too (D2-130): livestock.md, "Fences and gates".

### Grain as food, mills and bread (D2-60, D2-61)

| Eaten as | Food a grain | Needs |
|---|---|---|
| whole grain, boiled | 0.7 | a hearth |
| ground grain (porridge) | 1.0 | a mill |
| bread | 1.3; keeps about 5% a day; eaten without a hearth | flour, fuel, a hearth or an oven |

- **Mills, built by adding parts:** a hand mill (two small stones turned by hand, any room); an ox mill (dressed millstones made
  by a mason, turned by an ox) by upgrading it; a water mill (a wheel and a leat) only at a river site, usually a new building,
  which can reuse dressed millstones carried there. Each rung grinds more grain per unit of work. A mill's holder may charge for
  milling.
- **Bread** is baked from flour at a hearth or, in batches, at a stone oven.

### Specialised tools (D2-48)

| Tool | Better at | What it alone can do |
|---|---|---|
| felling axe | felling | fells great trees (the great beams a hall for more than 25 needs) |
| miner's pick | mining | works a deep seam |
| scythe | cutting hay | one person cuts a pasture's hay inside the summer window |
| mason's chisels | quarrying | dressed stone: millstones, arches, a third storey |
| reaping hook | reaping | loses less grain at the harvest |

Each is a master smith's recipe (knowledge.md: not basic), made at a smithy with more copper than a hand tool; better and
longer-lived at its method; no better than a crude tool at other work.

### Cheese (D2-47)

Milk, a little salt and work make cheese, which must age in a cool room or a cellar; it keeps about as well as salted meat and is
worth carrying.

### Wear (D2-46)

Tools and weapons wear by use on one scale: each method has a wear factor (reaping light, mining heavy); a fight is the heaviest
use, so a blade lasts about 10 fights and a crude weapon about 3, with a small chance of breaking in any fight. A smith can mend a
worn metal tool or blade.

### Skill by practice (D2-52)

- Every kind of work, basic work included, has a skill per agent that rises with practice (days spent at that work) and fades
  slowly without it; skill multiplies the yield of gathering and farming and cuts the work of making.
- An ordinary adult is about x1.0 at basic work, a master about x1.5. In farming a master's skill raises yield about x1.2 and
  cuts the work about x0.7 (D2-64). Seed selection, a learned technique, makes the sower's crops ripen about 15% sooner (D2-65). A learned trade (knowledge.md's levels: once "known") runs
  from about x0.5 for a novice to x2.0 for a master. Youth learn faster (D4-19). Seeded specialists start skilled (D4-21).
- Agents see their skill as a word (novice, competent, skilled, master), never a number.

### Basic techniques and trades (D2-43)

- **Basic** (everyone knows): forage, hunt, fell, cut hay, sow, hoe, weed, reap, manure, herd, slaughter; make a crude tool, a crude
  weapon or a pack; salt meat (given salt); build a small wattle room, bins, benches, shelves, beds; repair.
- **Trades** (techniques a household passes on; knowledge.md's levels): farmer and herder (plough with oxen, yoke an ox; milking,
  D2-42); woodsman and carpenter (plough, handcart, cart, framed rooms and halls, water wheel); trapper (traps); miner and smelter
  (mine ore, smelt copper); smith (hand tools, blades, coin, locks, anvil and bellows); mason (quarry; stone rooms, hearths,
  cellars, millstones); salter (boil salt); leatherworker (harness, saddle); parchmenter and scribe (parchment; reading and
  writing); horse breaker (break a horse).

## Data

Per plot: fertility, the crop growing (kind, day sown), the last crop grown. Tools are items in holdings with wear.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| seed a plot, harvest per seed, work per stage, fertility changes, the weeding curve | 02l model's values as the starting point | calibrate |
| the harvest window and the loss a day after it | 2 days; a quarter of what is left a day | calibrate |
| field works: labour, materials, upkeep; the wet and hill penalties | above | calibrate |
| grain spoilage a day: house, bins, cellar or granary | 0.5%, 0.25%, 0.1% | decided (D2-58) |
| seed a plot (one adult's season by hoe) | about 16; about a fifth of the harvest | decided (D2-59); yields calibrate |
| crop cycles (days from sowing to ripe) | about a quarter of the year for grain, a third for winter grain, a sixth for legumes, a tenth for a garden | calibrate |
| sowing work and seed: broadcast against dibbling | dibbling about 3x the work, about 0.6x the seed | calibrate |
| the skill curve: practice to mastery; fading | 02c §5 (multiplier 0.5 + 1.5(1 - exp(-p/tau))); tau so mastery takes about a season of full-time work | calibrate |
| tools' effect, wear and cost | 02j model | calibrate |
| the share of work food takes | binding, at most 30% (scenario_design) | calibrate |

## What agents see

Their plots by name, what is growing and roughly when it ripens ("the barley in the Long Field will be ready in about three days"),
the soil in words ("tired", "good"), their seed in store, their tools and whether they are wearing out.

## Open

- The plot unit against D4-23's definition: board, 23 Oct.
- Recipes, production shapes, skills, workshops: proposals/resources_and_goods.md, proposals/economy_plan.md.

## Sources

[02l_farming.md](../../../review/37_growth/02l_farming.md), [02j_end_uses.md](../../../review/37_growth/02j_end_uses.md),
[02d_ladders.md](../../../review/37_growth/02d_ladders.md); proposals/farming.md, proposals/tools.md.

*Current as of 23 Oct 2026: H-6, D2-11 to D2-19, D2-23, D2-42, D2-43, D2-46, D2-47, D2-48, D2-52, D2-53, D2-54, D2-58, D2-59, D2-60, D2-61, D2-62, D2-64, D2-65, D2-66, D2-67, D2-130, D2-156, D2-157.*
