# Proposal: recipes for the first worlds

**Status:** discussion (23 Oct). **Owner:** 37.2 (the content); 37.4 owns the verbs and the technique record (verbs.md,
knowledge.md), which these recipes are data for. **Affects:** spec/economy/production.md, goods.md, buildings.md; knowledge.md's
basic set (37.2's open question there). **Model:** [02m_recipes_model.py](../../review/37_growth/02m_recipes_model.py).

## Summary

About 40 techniques make the first worlds' goods (D2-24) from the land: 7 ways of gathering, 18 recipes, 15 building blueprints and
a handful of working methods. Each is a card for one of four verbs (`gather`, `make`, `build`, `work`): inputs, tools, workplace,
work units, output. About a third are **basic** (everyone knows them); the rest belong to **ten trades**. Costed down to the land,
the anchors are: **a coin is about a food, a day's work about 6 coin, a copper tool about 2 days, a blade about 3.5, a cart about
4.** Smelting cuts the weight to carry from 17 to 1, so it belongs at the seam; salt is boiled at the spring. Copper, tools, blades,
documents and coin travel; timber, stone, ore and grain stay near where they are got.

## The proposal

### 1. Gathering (`gather {site}`)

Yields with a crude tool; **bare hands x0.5** (and no quarrying or mining at all); **a copper hand tool x1.5** (D2-23).

| Good | Site | Units | Yield | Units a unit | A worker-day | Trade | Basic |
|---|---|---|---|---|---|---|---|
| wild food | forest, scrub (stock-limited) | 1 | 1.2 | 0.83 | 7 | forager | yes |
| meat (and a hide 1 time in 4) | forest game (threshold; parties) | 2 | 2 | 1.00 | 6 | hunter | yes |
| timber | forest | 2 | 3 | 0.67 | 9 | woodsman | yes |
| stone | a quarry | 2 | 2 | 1.00 | 6 | mason | no |
| copper ore | a seam (finite) | 2 | 2 | 1.00 | 6 | miner | no |
| hay | pasture, in summer | 1 | 3 | 0.33 | 18 | herder | yes |
| grain | fields (production.md; 02l) | per stage | | 0.59 | 10 | farmer | yes (sow, reap) |

Livestock (D2-6): **slaughter** an ox or cow (`work`, 2 units): about 15 meat and 2 hides, and the animal is gone.

### 2. Recipes (`make {what, qty}`)

| Good | Makes | Inputs | Units | Tool needed | Workplace | Full cost a unit | Trade | Basic |
|---|---|---|---|---|---|---|---|---|
| crude tool | 1 | 1 timber, 0.5 stone | 1 | | anywhere | 2.2 | | yes |
| crude weapon | 1 | 1 timber | 1 | | anywhere | 1.7 | | yes |
| pack | 1 | 1 hide, 1 timber | 1 | | anywhere | 2.7 | | yes |
| salted meat | 1 | 1 meat, 0.2 salt | 0.2 | | anywhere | 1.6 | | yes |
| trap | 1 | 1 timber, 0.25 hide | 1 | | anywhere | 1.9 | trapper | |
| salt | 2 | 3 timber (fuel) | 2 | | a salt spring or the shore | 2.0 | salter | |
| copper | 1 | 3 ore, 4 timber (charcoal folded in) | 3 | | a smithy's hearth with bellows | 8.7 | smelter | |
| hand tool | 1 | 1 copper, 0.5 timber | 3 | | a smithy | 12.0 | smith | |
| blade | 1 | 2 copper, 0.5 timber | 4 | | a smithy | 21.7 | smith | |
| coin | 10 | 1 copper | 1 | | a smithy | 1.0 | smith | |
| lock | 1 | 1 copper | 3 | | a smithy | 11.7 | smith | |
| plough | 1 | 4 timber, 1 copper | 4 | hand tool | anywhere | 15.3 | carpenter | |
| handcart | 1 | 6 timber | 3 | hand tool | anywhere | 7.0 | carpenter | |
| cart | 1 | 12 timber, 1 copper | 6 | hand tool | anywhere | 22.7 | carpenter | |
| harness | 1 | 2 timber, 1 hide | 2 | | anywhere | 4.3 | leatherworker | |
| saddle | 1 | 1 timber, 2 hides | 3 | | anywhere | 5.7 | leatherworker | |
| parchment | 4 sheets | 1 hide | 2 | | anywhere | 0.75 | parchmenter | |
| document | 1 page | 1 sheet | 1 | | anywhere | 1.75 | scribe (literate) | |

### 3. Building (`build {what, at}`)

02i's fittings re-costed without clay, fibre, iron or leather (not in the first worlds, D2-24):

| Blueprint | Materials | Units | Worker-days in all | Needs | Gives |
|---|---|---|---|---|---|
| small room, wattle and timber | 8 timber | 6 | 1.9 | a lot | a roof for 4 |
| medium room, timber on stone | 15 timber, 4 stone | 15 | 4.8 | a lot | a roof for 10 |
| hall, timber on stone | 30 timber, 10 stone | 30 | 10 | a lot; a carpenter | a roof for 25 |
| medium room, stone | 30 stone, 5 timber | 36 | 11.6 | a lot; a mason | a roof for 10; x2 defence (D2-20); can carry a storey (D2-3) |
| beds (each) | 2 timber, 1 hide | 1 | 0.6 | a room | housed when sleeping here |
| hearth | 4 stone | 3 | 1.2 | a room | warmth (burns fuel); cooking |
| bins | 3 timber | 1 | 0.5 | a room | about 20 food at the house rate |
| benches and a table | 3 timber | 1 | 0.5 | a room | the room holds its full size for a meeting |
| shelves | 3 timber | 1 | 0.5 | a room | an archive of about 50 documents |
| lock | 1 lock | 1 | 2.1 | a room or a box | access by key |
| anvil and bellows | 6 stone, 2 hides, 1 timber | 4 | 2.1 | a hearth | a smithy |
| millstones | 10 stone | 10 | 3.3 | a room; a mason | milling by hand (if milling is in: Open 2) |
| water wheel | 15 timber, 1 copper | 12 | 5.1 | millstones; a river site; a carpenter | milling at full batch |
| cellar | 8 stone | 8 | 2.7 | a ground floor; a mason | a quarter of the spoilage (Open 4) |
| stalls (each) | 3 timber | 1 | 0.5 | a ground-floor room | stabling an animal (Open 4) |

Larger rooms cost less per person (D2-9; 02i §2b's curve); storeys cost more and need stone (D2-3).

### 4. Working methods (`work {what, at}`)

| Method | On | Basic | Notes |
|---|---|---|---|
| sow, weed, reap | a plot | yes | production.md (D2-11 to D2-17) |
| hoe | a plot | yes | needs a hand tool |
| plough with oxen | a plot | no (ox handling) | a yoked ox with harness and a plough (D2-18) |
| manure | a plot | yes | dung from cattle |
| herd | animals at pasture | yes | 02l §5: one herder watches about 30 head |
| slaughter | an animal | yes | 15 meat, 2 hides |
| yoke an ox; break a horse | an animal | no (animal handling) | gives the animal its use with harness or saddle (D2-23) |
| repair | a building | yes | upkeep (H-5) |

### 5. Basic and trades (37.2's answer to knowledge.md's open question 1)

**Basic** (everyone knows): forage, hunt, fell, cut hay, sow, hoe, weed, reap, manure, herd, slaughter, make a crude tool, a crude
weapon or a pack, salt meat (given salt), build a small wattle room, bins, benches, shelves, beds, repair.

**Ten trades**, each a group of techniques a household passes on:

| Trade | Techniques | Where it sits in the first region (02f §4) |
|---|---|---|
| farmer and herder | plough with oxen, yoke an ox, (milling) | Barleyfield |
| woodsman and carpenter | plough, handcart, cart, medium rooms and halls, water wheel | Ashwood |
| trapper | traps | Ashwood |
| miner and smelter | mine ore; smelt copper | Coppergate |
| smith | hand tools, blades, coin, locks, anvil and bellows | Coppergate, Millford |
| mason | quarry stone; stone rooms, hearths, cellars, millstones | wherever the quarry is |
| salter | boil salt | at the spring or shore (one place, possibly outside the region) |
| leatherworker | harness, saddle | Millford |
| parchmenter and scribe | parchment; writing and reading (literacy) | Millford |
| horse breaker | break a horse | where wild herds are (D2-6) |

### 6. Skill, wear and the levels

- **Levels** (knowledge.md §4c): aware, rough idea, capable, known. **Skill** within "known" follows the practice curve (02c §5):
  shown as novice, competent, skilled, master; it raises gathering yields and cuts the units of making, up to about x1.5 and x0.7.
- **Wear:** a crude tool 10 uses; a copper hand tool 40; a plough 60; a trap 20 nights; harness 80 days, saddle 160, pack 60. **A
  crude weapon lasts about 3 fights and a blade about 10** (the engine as built uses a weapon up in every fight: Open 5).

### 7. What the costs say

- **Copper tools now pay well:** on a fell, a copper tool gives about 1 unit more timber a use for 0.08 more wear than a crude one,
  so it repays its 12 units in about 12 uses. (02j found copper tools weak against crude ones because it gave them x1.0 against
  x0.8; with copper the only metal (D2-19), it is the step up.) **That makes the smith a chokepoint** for every gathering trade.
- **Where steps belong (Weber):** smelting turns 17 weight of ore and fuel into 1 of copper, so it happens at the seam, and only
  where there is wood too; salt (6 weight of fuel into 2) at the spring.
- **What travels (Von Thunen):** full cost per unit of weight: timber, stone and ore about 0.3; grain 0.6; meat and hides 1; salt 2;
  copper 8.7; tools 12; blades 22; documents 35; coin 97. On foot an edge costs about 0.9 units per unit of weight (02g §3), so
  timber, stone, ore and grain stay within a node or one edge; **salt needs pack animals or a cart to go far**, which gives the
  transport ladder a job; copper, tools, blades, documents and coin travel anywhere.
- **Price anchors** at about 1 unit a food: a coin about 1 food; a day's work about 6 coin; salt 2; copper 9; a hand tool 12; a
  plough 16; a blade 22; a cart 23; a page 2.

### 8. Tools by method: what a tool changes, and what it cannot (23 Oct, b)

**A tool never adds to a site's stock.** Where the land holds a stock (plants, game, a forest's timber, a seam), a better tool takes
the same stock faster: more per unit of work, and the site runs down sooner (copper axes speed deforestation). Where the source is
endless (a quarry, a salt spring) or is a plot's soil, it simply cuts the work. One hand tool good (D2-23), with an effect that
differs by method (data on each method's card):

| Method | Bare hands | Crude | Copper | Wear a use | Draws on | Why |
|---|---|---|---|---|---|---|
| forage | x1 | x1 | x1 | 0 | plants (stock) | picking by hand: no tool helps (a pack helps carry) |
| fell | x0.25 | x1 | **x2** | 1 | forest timber (slow stock) | metal axes cut about twice as fast as stone ones (experimental archaeology: steel about 3x) |
| quarry | none | x1 | x1.5 | 2 | a quarry (endless) | wedges and hammers; hard on tools |
| mine | none | x1 | x1.5 | 2 | a seam (finite) | picks; no tool, no mining |
| cut hay | x0.3 | x1 | x1.5 | 0.5 | pasture | sickle or scythe |
| hoe | x0.5 | x1 | x1.5 | 1 | the plot's soil | breaking ground |
| reap | x0.6 | x1 | x1.5 | 0.5 | the crop | a sickle |
| hunt | x0.3 | x1 (spear) | x1.3 (blade) | 0.3 | game (threshold stock) | the weapon, a separate good |

**Is a copper tool worth it?** For a household of 5 in a 40-day year (felling 24 units, hoeing 72, reaping 36, hay 4): it saves
about 49 units a year (8 worker-days), and wears out about one tool a year (11 units) against 12.6 for the crude tools it replaces.
**It pays back in about 10 days of use.** So every household should want one, and the smith is the chokepoint.

**Is it worth having different tools (an axe, a pick, a sickle) instead of one?** Not as separate goods. Wear is per use, so four
tools cost the same per use as one; they only add a fourfold purchase up front and four goods to list. The heterogeneity that
matters, how much a tool helps each kind of work, is kept as data on each method. Separate goods are justified only where the
dependence differs: the plough (an ox), weapons (force), traps (work while away), harness and saddle (animals).

### 9. Weapon wear from one wear scale

The engine as built uses a weapon up in every fight: about 22 units for a blade, more than three days' work per fight. A principled
alternative: **one wear scale for every tool.** A tool's life is counted in standard uses (about 2 units of work); each method has a
wear factor (above: reaping 0.5, felling 1, mining 2). A fight is heavy use: **factor 4**. A copper blade then lasts 40 / 4 = **10
fights**; a crude weapon (10 uses, factor about 3) lasts **3**. The factor 4 is the one choice; it sits at twice mining's. A smith
can mend a worn blade for less than a new one (about 1 unit and a fifth of a copper). Alternative: a chance of breaking per fight,
higher for the losing side.

### 10. Bread (Zach: slightly better; keeps meaningfully longer)

| Step | Recipe | Work |
|---|---|---|
| porridge | grain eaten at a hearth | none beyond the hearth (as now) |
| flour by hand | a quern (basic: stone): 4 grain an unit of work | about 0.25 units a ration |
| flour at a mill | millstones turned by hand: 12 grain a unit; with a water wheel: 40 a unit | 0.08 or 0.025 a ration |
| bread | 10 flour, 1 timber, 1 unit at a hearth: **11 bread** | a batch |

- **Better in three ways:** a little more food (11 loaves from 10 grain: grain plus water); **eaten anywhere, without a hearth**
  (travel, the fields, a raid, a market day), while grain must be cooked at a hearth; and **keeps about 5% a day carried**, against
  15% for wild food and 30% for fresh meat (grain in a store keeps better still).
- **By hand it is not worth it for eating at home** (0.25 units of grinding a loaf for a tenth more food); **at a mill it is**, and
  it is always worth it for travel. That makes **the mill a chokepoint** (whoever holds it can charge a share of the grain, as mills
  did), and bread the merchant's and the traveller's food, with salted meat.

### 11. Meat and milk (decided: D2-41, D2-42)

- **Meat** (D2-41): from the hunt and slaughter; **one meat feeds 1.5** (dense food), but fresh meat loses about 30% a day; salted,
  2%. A slaughter (15 meat) feeds a household for days or a feast for many at once.
- **Milk** (D2-42): a technique (milking), not basic: an agent must learn or try it (knowledge.md). It needs **a cow in milk** (one
  that has calved this season) at the node and fed; 1 unit a day gives about 3 milk (0.5 food each), which spoils within the day.
  **Cheese** would keep it (6 milk, 0.2 salt, 1 unit: 1 cheese worth 2 food, keeping like salted meat), a second use for salt (Open).

### 12. Cellar and stalls: what they are for

- **A cellar** (8 stone, a mason): a stone storeroom on the ground floor where food (grain, meat, cheese, bread) loses a quarter of
  what it loses in the house. 02j: it pays only for a large store (a village granary), not a household's.
- **Stalls** (3 timber each, a ground-floor room): an animal housed for the winter **eats less fodder** (it is out of the cold),
  **its dung is kept** for the fields (manure), and it is **safe from rustling** behind walls and a lock. Horses and oxen alike.

### 13. The worth of things (what agents should rationally want)

A year's worth against a year's cost (capital written off over its life, plus upkeep), in units, for a household and at scale:

| Thing | Cost a year | Worth a year, household | Ratio | Worth a year, at scale | Ratio | Basis |
|---|---|---|---|---|---|---|
| hearth | 0.7 | 25 | 36 | 25 | 36 | winter without it: x1.5-2 food and the cold (H-5) |
| copper hand tool | 10.9 | 49 | 4.5 | 49 | 4.5 | §8 |
| beds for 5 | 2.5 | 10 | 4.0 | 10 | 4.0 | housed sleep (02e) |
| stalls for 2 oxen | 1.0 | 4 | 4.0 | 4 | 4.0 | §12 |
| bins | 0.5 | 1.5 | 3.0 | 1.5 | 3.0 | 02j |
| salt for 2 slaughters | 12 | 24 | 2.0 | 24 | 2.0 | keeps 30 meat |
| lock | 1.3 | 2 | 1.5 | 8 | 6.2 | the theft it stops: much on a store or treasury |
| plough and ox | 11.7 | 6 | 0.5 | 60 | 5.1 | 02l: a village shares the herd |
| cellar | 1.1 | 0.4 | 0.4 | 5 | 4.7 | 02j: a granary |
| trap line of 6 | 19 | 7 | 0.4 | 7 | 0.4 | barely beats foraging at full plants; pays where plants are short |
| cart | 5.7 | 0 | 0 | 60 | 10.6 | 02g: a merchant's |

- **The household wants:** a hearth, beds, a copper tool, bins, salt when it slaughters. **The village or a specialist wants:**
  the herd and ploughs, a granary cellar, locks on stores, carts. So the things that pay at scale are what institutions and
  specialists are for.
- **Traps barely pay** at these numbers; they become worth it where plants are short or game is close to home.
- **This answers part of 37.4's run C finding** (38.12 §4.4: food stayed 85-90% of work because nothing else was worth units): a
  world needs goods like these on offer, at prices agents can reach, before slack has a use. Productive goods alone may not be
  enough: agents also need things they value for themselves (comfort, safety, standing: a better house, a feast, a lock).

## Why

- Each good in D2-24 has a reason to be made, a place it is made and a reason to travel; no good is single-use (02g §1f).
- Interlocking chokepoints (scenario_design): the seam and the smithy (copper, tools, blades, coin, locks), the spring (salt), the
  quarry and the mason (stone, hearths, cellars, millstones), the scribe (documents), the ox (ploughing).
- The cards fit 37.4's verbs and technique record with no new verb.

## Alternatives considered

- **Charcoal, planks, leather as goods:** folded into recipes (02g §1f).
- **02i's fittings with clay, fibre and iron:** re-costed in the first worlds' goods.
- **Copper tools left out** (02j's suggestion): rejected here: copper is the only metal, so it is the tool step.

## Open questions (for Zach)

Answered 23 Oct: meat in (D2-41); milk in as a technique (D2-42); the basic set and ten trades (D2-43).

1. **Bread** as in §10: porridge needs nothing; flour by quern or mill; 11 bread from 10 grain, eaten without a hearth, keeping 5% a
   day; the mill a chokepoint?
2. **Cheese** (§11): milk and salt into a food that keeps; a second use for salt. Now or later?
3. **Cellar and stalls** (§12) in the fittings list?
4. **Weapon wear** from one wear scale (§9: a fight is factor 4; a blade lasts about 10 fights, a crude weapon 3; a smith mends),
   or a chance of breaking per fight?
5. **Tool effects by method** (§8) as data on one hand tool, with no separate axe, pick or sickle?
6. Food's share of work: the open calibration (and 38.12: it is also about what else is worth wanting).

## History

- 22 Oct: 02j costed the end uses with roots and recipes (in old-engine actions); 02g §1f pruned the goods and fittings.
- 23 Oct: D2-24 fixed the first-world goods. Zach: work on recipes. Written: the catalogue in 38.06's work units for 37.4's verbs,
  basics and trades, tool grades and wear, re-costed fittings, weight and travel, price anchors.

- 23 Oct (b): Zach: tools for every method, differing by resource; do tools take more from capacity or create from nothing; meat
  yes; bread slightly better and keeping longer; milk now if they learn it; what cellar and stalls are for; how the weapon number
  was got; more analysis of the worth of things and of different tools. Added §8-§13; decisions D2-41 to D2-43.

## Sources

[02m_recipes_model.py](../../review/37_growth/02m_recipes_model.py), [02j](../../review/37_growth/02j_end_uses.md),
[02g §1f, §3](../../review/37_growth/02g_resources_and_transport.md), [02i §2-3](../../review/37_growth/02i_buildings.md),
[02l](../../review/37_growth/02l_farming.md), [verbs.md](verbs.md), [knowledge.md](knowledge.md), 38.06 §3; D2-3, D2-6, D2-9,
D2-18, D2-19, D2-20, D2-23, D2-24.
