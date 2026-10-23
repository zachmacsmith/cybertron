# 37.2p Supply chains: what each step costs, what each trade earns, where the rents are

*23 Oct 2026. Analysis for Zach ("explore the recipes through various economic analyses, examining the action values of each
through the supply chains"); nothing here is decided. Numbers from [02p_chains_model.py](02p_chains_model.py), which imports the
catalogue of [02m_recipes_model.py](02m_recipes_model.py) and adds flour, bread, milk, cheese, a great beam and charcoal from
proposals/recipes.md §10-§15. Units are 38.06's work units (6 a day); a food is worth about a unit. Every number is a proposal.*

## 1. Labour through each chain

Units per unit of the good, down to the land:

| Good | Units | The largest step (share, where) | The steps |
|---|---|---|---|
| hand tool | 12.0 | mining the ore (25%, the seam) | ore 3, timber 3, smelting 3, smithing 3 |
| blade | 21.7 | mining the ore (28%) | ore 6, smelting 6, timber 5.7, smithing 4 |
| coin | 0.97 | mining the ore (31%) | ore 0.3, smelting 0.3, timber 0.27, striking 0.1 |
| lock | 11.7 | mining the ore (26%) | ore 3, smelting 3, smithing 3, timber 2.7 |
| plough | 15.3 | timber (35%) | timber 5.3, carpentry 4, ore 3, smelting 3 |
| cart | 22.7 | timber (47%) | timber 10.7, carpentry 6, ore 3, smelting 3 |
| harness | 4.3 | leatherwork (46%) | leatherwork 2, timber 1.3, hide 1 |
| saddle | 5.7 | leatherwork (53%) | leatherwork 3, hides 2, timber 0.7 |
| salt | 2.0 | fuel (50%) | timber 1, boiling 1 |
| salted meat | 1.6 | the hunt (62%) | meat 1, salt 0.4, salting 0.2 |
| document (a page) | 1.75 | writing (57%) | writing 1, parchment 0.5, hide 0.25 |
| flour (by quern) | 0.84 | growing (70%) | grain 0.59, grinding 0.25 |
| bread | 0.91 | growing (59%) | grain 0.53, grinding 0.23, baking 0.09, fuel 0.06 |
| cheese | 3.4 | milking (59%) | milking 2, cheese-making 1, salt 0.4 |
| felling axe, miner's pick, scythe | 21-22 | ore and smelting (27% each) | as a blade, with 4-5 units of master smithing |
| mason's chisels, reaping hook | 12-13 | smithing or ore | as a hand tool |
| great beam | 18 | the crew's day | felling one great tree |

Buildings: a small wattle room 11 units (1.9 worker-days), a hall 60 (10 days), a stone room 69 (11.6 days); a hearth 7, anvil and
bellows 13, millstones 20, a water wheel 31; a bed 3.3. Building work is about half of each; stone is the other half where stone is
used.

**What it says:** in every metal good **the smith's own work is only a fifth to a quarter of the cost**; the seam, the smelting and
the fuel are the rest. So the copper chain's chokepoints are upstream (the seam and the wood), and a smith's skill matters less to
the price of a tool than access to copper.

**Weight (Weber):** smelting cuts 17 weight of ore and fuel to 1 of copper, so it belongs at the seam, and only where there is
wood; salt cuts fuel 3 to 1 (or needs none, sun-dried on a shore); cheese cuts milk 12 to 1; parchment cuts a hide 5 to 1; milling
saves work, not weight, so it can be anywhere grain is.

## 2. What each trade earns

**At full-cost prices every trade earns its skill times its tool's multiplier, by construction** (a novice 0.5 a unit, a competent
maker 1, a master 2; a copper tool doubles a woodsman). The comparison that matters is at **what a buyer would pay at most**, the
work or food the good saves them:

| Trade | Good | Full cost | Worth to a buyer | Worth / cost | Return a unit at that worth: novice / competent / master |
|---|---|---|---|---|---|
| smith | hand tool | 12 | 67 | 5.6 | 10 / 20 / 39 |
| smith | lock (a store) | 12 | 80 | 6.9 | 12 / 24 / 48 |
| smith | blade (hunting only) | 22 | 36 | 1.7 | 2.3 / 4.6 / 9 |
| smith | coin | 0.97 | 1 (by custom) | 1.0 | 0.7 / 1.3 / 2.7 |
| master smith | specialised tools | 12-22 | 64-88 | 2.9-5.5 | 5-9 / 9-18 / 18-37 |
| carpenter | plough | 15 | 116 | 7.6 | 13 / 26 / 52 |
| salter | salt | 2.0 | 5.8 (the meat it keeps) | 2.9 | 2.4 / 4.8 / 9.5 |
| miller (water mill) | grinding a ration | 0.025 | 0.225 (the quern's work) | 9 | 4.5 / 9 / 18 |
| dairy | cheese | 3.4 | 2 | 0.6 | 0.3 / 0.5 / 1.1 |
| woodsman | great beam | 18 | about 30 | 1.7 | 0.8 / 1.7 / 3.3 |

- **Tools are worth three to eight times their cost.** The real prices will be set between cost and worth by how many smiths there
  are and how long buyers can wait, not by cost. This is where the economy's surplus is, so it is where bargaining, credit and
  monopoly will show.
- **Cheese loses food** (finding 7).
- **The miller's case depends entirely on whether grain must be ground to eat** (§6).

## 3. Rents at chokepoints

The most a holder could capture (worth to buyers less the cost delivered), against the first region's work (40 people, 240 units a
day):

| Chokepoint | Rent at most | Volume | Rent a day | Share of the region's work |
|---|---|---|---|---|
| **the copper seam** (with smelting) | 54 a copper (worth as a tool 64, cost at Millford 10.5) | about 25 a year | 34 units | **14%** |
| the salt spring | 2.8 a salt | about 80 a year | 5.7 | 2% |
| the water mill, grain must be ground | 0.23 a ration | 28 a day (Millford, Barleyfield) | 6.3 | 2.6% |
| the water mill, only bread ground | 0.1 a loaf | about 4 a day | 0.4 | 0.2% |
| old oaks (great beams) | about 5 a beam | a hall a decade | ~0 | ~0: a gate, not an income |
| a quarry | small where every node has one | | | a gate where none does: every hearth needs stone |
| a smithy (the building) | none: about 49 units to build | | | the rent is in copper and know-how |

**The copper seam is the region's dominant chokepoint**: at a monopoly price it could take about a seventh of all the region's
work. That is good for leverage (scenario_design), but a seam holder who prices tools near their worth could leave households
working with crude tools; whether that happens is a run question, and the design lever is how much copper is seeded and whether a
second seam exists.

## 4. Returns to capital and know-how

| Capital | Cost | Return | Payback |
|---|---|---|---|
| a smithy | 49 | a 25% markup on 25 copper items a year: 75 a year | about 26 days |
| a water mill, toll an eighth of the grain (grain must be ground) | 62 | 2.1 a day | about 30 days |
| a water mill, toll a sixteenth | 62 | 1.0 a day | about 60 days |
| a water mill if only bread is ground | 62 | about 0.1 a day | never |
| an ox cart, 2 oxen and harness, carrying 15 / 30 / 60 weight a day one edge | 71 | 13 / 25 / 50 a day | 6 / 3 / 1 days |
| specialised tools, full-time specialist | 12-22 | 1.2-1.9 a day | 10-19 days |

**Know-how:** one teaching session (knowledge.md: teacher 2 units, learner 4) takes a learner from novice to capable, which for a
smith is worth about 75 units a year (3 units a tool saved on 25 tools): **the session repays itself about twelve times in a year.**
A master against a competent smith saves about 38 units a year (6 worker-days). Teaching at cost is far too cheap: masters have
every reason to charge for it or ration it, which is the economic basis of guilds and apprenticeships.

## 5. Trade between the nodes of the first region

| Good | From | To | Edges | Carrying adds, on foot / by ox cart | Travels |
|---|---|---|---|---|---|
| grain | Barleyfield | Millford (the mill) | 1 | +158% / +15% | by cart only |
| flour or bread | Millford | Barleyfield | 1 | +102% / +10% | by cart only |
| copper | Coppergate | Millford (the smithy) | 2 | +21% / +2% | on foot |
| tools | Millford | Barleyfield, Ashwood | 1 | +8% / +1% | on foot |
| timber (fuel) | Ashwood | Millford | 1 | +279% / +27% | by cart, for bulk only |
| **timber to smelt copper (4 a copper)** | Ashwood | Coppergate | 1 | +279% / +27% | **by cart; see finding 1** |
| charcoal (proposed: 0.8 a copper) | Ashwood | Coppergate | 1 | +43% / +4% | by pack animal or cart |
| stone | a quarry | the next node | 1 | +279% / +27% | barely |
| salt | outside the region | everyone | 2 | +93% / +9% | by pack animal or cart |
| cheese | a pasture node | the towns | 2 | +27% / +3% | on foot |
| hides | Barleyfield, Ashwood | Millford | 1 | +93% / +9% | by pack animal or cart |
| documents | Millford | anywhere | 2 | +5% / +1% | on foot |

**A merchant with an ox cart** saves buyers about 0.84 units per unit of weight per edge. Its income is set by the region's volume,
not the cart: at 30 weight a day it earns about 25 units a day (four worker-days) and the cart team pays for itself in about three
days.

**One mill for several nodes (Zach's question):** grinding saves 0.23 units a ration. Grain carried one edge to the mill and back
costs about 0.18 a ration by ox cart and about 1.9 on foot. So **a mill can serve its neighbours only through carts, and the margin
is thin** (about 0.05 a ration); on foot never. Neighbouring nodes with a river site will build their own mill; a node without one
depends on the merchant's cart, which makes the cart and the mill a joint chokepoint.

## 6. Whether grain must be ground to eat

| | Units a ration of grain | Share of a 6-unit day | The mill |
|---|---|---|---|
| porridge needs no grinding (D2-44 as decided) | 0.59 | 10% | grinds only bread and travel food; never pays |
| grain must be ground (a quern, about 0.25 a ration) | 0.84 | 14% | saves 0.23 a ration; pays for a village of a few households in about a month at a toll of an eighth |

## 7. Findings and recommended changes

1. **Charcoal must come back as a good.** Copper's recipe burns 4 timber at the smelter, but the first region's seam (Coppergate)
   has no wood; carrying the timber from Ashwood adds 279% on foot or 27% by cart to the fuel. Recommend: charcoal (5 timber and 1
   unit at the wood, weight 2: five times lighter than the timber), made in Ashwood and carried to Coppergate; it passes the
   pruning rule's weight test (02g §1f). The alternative is woods at Coppergate.
2. **Tools are worth 3-8 times their cost** (hand tool 67 against 12, plough 116 against 15, lock 80 against 12): expect prices set
   by bargaining between few smiths; recommend seeding at least two smiths, or copper stocks, if the first runs should not be
   decided by one monopoly.
3. **The copper seam can capture about 14% of the region's work** at a monopoly price: the region's main chokepoint. Keep it, and
   watch it in runs.
4. **A coin is "about a food" only at cost.** If copper trades nearer its worth as tools (up to about 64 a copper), a coin's copper
   is worth up to about 6 food and coins get melted into tools. D2-28 says a coin's value follows copper's, so this is consistent,
   but the anchor should not be promised to agents; seed copper and coin so that copper's starting price is near its cost.
5. **The mill pays only if grain must be ground to eat** (§6): recommend a quern for porridge too (0.2-0.25 units a ration), which
   gives the mill a rent of about 6 units a day in the first region and raises grain's labour from 10% to 14% of a day.
6. **One mill serves several nodes only by cart**, at a margin of about 0.05 a ration (§5).
7. **Cheese loses a third of the milk's food** (6 milk, 3 food fresh, into a cheese of 2): recommend 2.5 food a cheese; it then
   pays for summer milk that would otherwise spoil (milk keeps only the day).
8. **Hides are a bottleneck:** beds take a hide each (a hall's 25 beds are 25 hides, about 12 slaughters), as do harness, saddles,
   bellows and parchment, from 2 hides a slaughter and 1 in 4 hunts. Recommend beds of timber and straw (grain's by-product).
9. **Every hearth needs 4 stone,** so every house depends on a quarry; recommend fieldstone gathered from fields at a low yield, or
   a quarry in every land kind that has houses.
10. **Salt needs 3 timber per 2 salt at the spring:** a spring without wood imports fuel; recommend that shore salt is sun-dried
    (no fuel), and inland springs boil.
11. **Teaching is underpriced** (6 units for about 75 a year of a smith's skill): no change needed; it is why masters will charge.
12. **The merchant's cart is very profitable at modest volume** (pays back in days): consistent with D2-2's seeded merchant; check
    the region's real volume in runs before changing the transport ladder.
13. **Coin striking is nearly free** (0.1 units for 10 coin): any smith can debase or flood; recommend an institution's stamp
    (D2-28's later step) once forgery matters.

## Sources

[02m_recipes_model.py](02m_recipes_model.py), [proposals/recipes.md](../../cybertron2/proposals/recipes.md),
[02j](02j_end_uses.md), [02g §3](02g_resources_and_transport.md), [02f §4](02f_economy_plan.md), [02l](02l_farming.md),
proposals/knowledge.md §4c.
