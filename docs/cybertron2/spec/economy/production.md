# Production: foraging, farming and tools

## Summary

Food comes from foraging (the bottom rung) and from fields. Farming has a short minimum (sow, reap) and optional stages that cost
work and raise the return. Crops ripen into a harvest window. Seed is kept back. Cattle pull the plough and dung the soil. Tools are
a small set chosen by what each depends on. The rest of production (recipes, the production shapes, skill by practice, workshops)
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
- D2-44: bread. D2-46: weapons wear, with a small chance of breaking. D2-47: cheese. D2-48: specialised tools.

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

### Bread (D2-44)

- Grain is eaten as porridge at a hearth, with no other work.
- Flour: grain ground by hand at a quern, or at a mill (millstones turned by hand, faster with a water wheel).
- Bread: flour, fuel and work at a hearth make a little more bread than the grain put in (11 from 10); bread is eaten without a
  hearth and keeps longer than other carried food. A mill's holder may charge for milling.

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
| tools' effect, wear and cost | 02j model | calibrate |
| the share of work food takes | binding, at most 30% (scenario_design) | calibrate |

## What agents see

Their plots by name, what is growing and roughly when it ripens ("the barley in the Long Field will be ready in about three days"),
the soil in words ("tired", "good"), their seed in store, their tools and whether they are wearing out.

## Open

- Crops, their cycles, and growth from the day sown: proposals/farming.md.
- Sowing work per unit of seed; broadcasting or dibbling: proposals/farming.md.
- The plot unit against D4-23's definition: board, 23 Oct.
- Recipes, production shapes, skills, workshops: proposals/resources_and_goods.md, proposals/economy_plan.md.

## Sources

[02l_farming.md](../../../review/37_growth/02l_farming.md), [02j_end_uses.md](../../../review/37_growth/02j_end_uses.md),
[02d_ladders.md](../../../review/37_growth/02d_ladders.md); proposals/farming.md, proposals/tools.md.

*Current as of 23 Oct 2026: H-6, D2-11 to D2-19, D2-23, D2-42, D2-43, D2-44, D2-46, D2-47, D2-48.*
