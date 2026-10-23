# 02t: the next region world, designed from dependence and checked with transport

Session 37.2, 24 Oct 2026. Zach: start the region world design and its transport check while 37.4 builds Package C. Design only;
37.4 writes the world file (cybertron2/specs/ is its code) and runs it. Model: [02t_region_model.py](02t_region_model.py). Built on
[38.23](../38_space_engine/23_region_run.md) (the region run: 27 of 51 died, fuel out of reach), scenario_design.md, and the
mechanics now built (roads with stretches and landmarks, meetings and promises on the road, herds, fences, things in places).

## 1. What this world is for

To test whether villages that need each other trade, when trade is clearly possible, using the roads and the economy as built. The
region run could not answer this: its fuel could not be carried in time, so deaths said nothing about whether agents trade. Here the
model checks, before any run, that every village's needs **can** be carried over its roads in the days available by the people free
to carry them; whether they **are** carried is the result.

**What it would look like if dependence did not drive trade:** the dependent arm moves little more across villages than the
comparison arm (§5), and its deaths fall on the villages that needed imports. **If it does:** goods flow early (before the cold),
agreements and promises cross villages, carriers and the merchant become central, and deaths are few and concentrated where trade
failed.

## 2. The world

Four villages and five roads, 24 days from late summer (the harvest under way) through one winter (days 9 to 14) into spring.

| Village | People (adults/youths/children) | Has | Lacks | Holds the chokepoint |
|---|---|---|---|---|
| **Barleyfield** (farms) | 10/3/3 in four households: Reed, Barrow, Hale, Lowe | 16 plots, 760 grain standing, a granary of 150, two herds (15 head) on an open Common beside the fields | wood: a copse of 12 and woodpiles of 24 for 4 hearths that burn 84 | the granary (Barrow), the ox team and bull (Reed) |
| **Ashwood** (wood) | 6/1/2: Fenn, Ash | Deep Wood (400 timber felled sustainably), game and forage (about 2.4 food a day), charcoal burning | grain: 113 food against 216 eaten | wood and charcoal (Fenn) |
| **Coppergate** (ore) | 5/1/2: Moor, Cole | the seam, the quarry, the forge; copper tools (felling x2, last 4x as long); a store of 120 grain | fuel for its hearths, charcoal for smelting; some grain | the seam and the forge (Moor) |
| **Millford** (market) | 9/2/3: Miller, Merchant, Bell (the inn), Smith | the water mill (40 grain a unit against a hand mill's 8), the inn's beds, the merchant's two handcarts, 5 plots | wood (10 there, woodpiles 20 for 4 hearths), some grain | the mill, the handcarts and the inn (Merchant, Miller) |

**Roads** (every road has a terrain, D2-122):

| Road | Days | Track (carts) | Landmarks | What it does |
|---|---|---|---|---|
| Barleyfield to Millford | 1 | yes | a ford (high after heavy rain) | grain to market by cart |
| Millford to Ashwood | 1 | yes | | timber to market by cart |
| Barleyfield to Ashwood | 1 | no (on foot) | the Holloway, a narrows in the wood; wild apples (a good place) | the short way for grain and timber, on foot |
| Ashwood to Coppergate | 2 | no | a ford | charcoal and timber to the forge |
| Coppergate to Millford | 2 | no | the Pass (snowed in deep winter) | tools and coin to market; grain back |

**Seeded custom (D2-30):** a market at Millford every fourth day, so travellers have a day to aim for (the region run's families
passed each other for want of one).

**Herds:** Barleyfield's two herds on the unfenced Common, next to the standing barley (strays: Package C), one with a road end on
its side; the Reeds' own pasture fenced in wood.

**No aims** (D4-29): survival, kin and what each household holds are the only pressure.

## 3. The check (02t model)

Engine numbers: a ration of 1 a night; grain counted ground (1.0; whole grain at a hearth only 0.7); a hearth burns 0.5 timber a
night, 2 on a cold night, 21 over the run and 16.5 by the last cold night; on foot with a pack 20 weight (10 timber or 20 grain), a
handcart 40 on a track; a night out 1.5 food; felling 1.5 timber a unit with crude tools, 3 with copper.

| Village | Food supply | Eaten | x | Timber needed | Woodpile and wood | Timber to bring (by the end of winter) | Charcoal | Food to bring | Food work |
|---|---|---|---|---|---|---|---|---|---|
| Barleyfield | 851 | 384 | 2.22 | 84 | 36 | 48 (30) | | | 16% |
| Ashwood | 113 | 216 | 0.52 | 42 | 420 | | | 103 | 8% |
| Coppergate | 166 | 192 | 0.86 | 42 | 30 | 12 (3) | 6 | 26 | 3% |
| Millford | 282 | 336 | 0.84 | 84 | 30 | 54 (36) | | 54 | 5% |
| **region** | **1411** | **1128** | **1.25** | | | | | | |

Food supply counts stores, the standing crop less the seed for the spring sowing, what the land gives back, and milk.
**Food binds without dominating:** the region holds 1.25 times what it eats (scenario_design.md §4), all of the surplus in
Barleyfield.

**What must move, and what it costs:**

| Flow | Qty | By | Trips | Days away a trip | Carrier-days |
|---|---|---|---|---|---|
| timber, Ashwood to Barleyfield (by the end of winter) | 30 | pack, the Holloway | 3 | 1 | 3 |
| timber, Ashwood to Millford | 36 | handcart | 2 | 1 | 2 |
| timber and charcoal, Ashwood to Coppergate | 3 and 6 | pack | 2 | 3 | 6 |
| grain, Barleyfield to Ashwood (over the run) | 103 | pack, the Holloway | 6 | 1 | 6 |
| grain, Barleyfield to Millford | 54 | handcart | 2 | 1 | 2 |
| grain, Barleyfield to Coppergate, through Millford | 26 | pack | 2 | 6 | 12 |

**31 carrier-days in all, against 218 free adult-days before the first cold night**: fuel carrying is about 5% of them. Ashwood
fells 186 timber, 13% of its work with crude tools, 6% with copper ones. So **trade is clearly possible**; nothing here repeats the
region run's impossibility. The two trades that carry the world are **grain for timber** between Barleyfield and Ashwood (by the
Holloway on foot, or round by Millford with a cart), and **the merchant's carts** between Millford and both.

The one hard route is Coppergate's: three days each way through Millford, or two to Ashwood. Its needs are small (26 grain, 9 fuel),
and it has what everyone wants (copper tools halve felling and last four times as long), so it can draw goods to itself.

## 4. Chokepoints and leverage

Several, interlocking (scenario_design.md §1): Barleyfield's granary and grain surplus; Ashwood's wood and charcoal; Coppergate's
seam, forge and copper tools; Millford's mill, carts, inn and market day; the ford on the cart road after rain; the Pass in deep
winter; the Holloway (the short way, where travellers meet, and later an ambush). The cold (days 9 to 14) is the deadline: a hearth
needs 12 timber for the winter's six nights.

## 5. Runs

**Cast** (scenario_design.md §2): Opus at each pole: the Barrow head (granary), the Reed head (oxen, bull), the Fenn head (wood),
the Moor head (forge), the Merchant; Sonnet for the other household heads (Hale, Lowe, Ash, Cole, Miller, Bell, Smith); Haiku for
the rest; children as the engine has them.

**Arms, paired by seed:**

- **Arm 1: dependent** (the world above).
- **Arm 0: the dependence null:** the same people, land, roads and custom, but each village able to keep itself (woodlots at
  Barleyfield, Millford and Coppergate; fields at Ashwood; a larger store at Coppergate). Region food 1.59 times what it eats. Trade
  there is optional, so cross-village flows in Arm 1 beyond Arm 0's are what dependence produced.

**Before running:** the engine's capacity check (38.21's script) on the world file, this model's transport check, and a dry run that
verifies every access gate by action (scenario_design.md §4): Barleyfield cannot fell more than its copse, Ashwood cannot farm,
the handcart refuses the Holloway, the Pass is shut in deep winter.

**Read:** goods moved between villages by flow and by day (before the cold or after); agreements, promises and arrears across
villages; meetings on the roads and their trades; deaths by cause and village (cold without fire, hunger, the road); cold nights
without a fire, by hearth; the share of actions on food and on carrying; herd strays and fences built; and a qualitative reading of
the end state: who holds the grain, the timber and the tools, what prices were witnessed, who became carriers, whether the merchant
and the market day became the centre.

**Cost:** the region run cost $23.64 for 51 people over 20 days; about $25 a run here, $50 for one seed of each arm, $100 for two.

## 6. Open (for Zach)

1. This world, or changes to its villages, roads or numbers?
2. The comparison: the dependence null (recommended), roads made bare, or both?
3. One seed of each arm first, then more if the difference is unclear?
4. A market day at Millford every fourth day as a seeded custom?
