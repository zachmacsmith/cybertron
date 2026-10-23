# 37.2n Labour scarcity, grinding and mills, and the plot unit

*23 Oct 2026. Analysis for Zach; nothing here is decided. It answers the critique that at the engine's rates food takes about 8% of
a person's units, so nothing makes labour scarce; that D2-44's mill pays at no village size; and that the node cap (15-20 people)
sits below 02d's thresholds. Numbers from [02n_labour_model.py](02n_labour_model.py); engine rates from
`cybertron2/engine/data.py` (PHYSICS, TECHNIQUES) and `cybertron2/specs/region.yaml`; everything else is a proposal.*

## 0. The engine's rates today

| Rate | Value |
|---|---|
| units a day | 7 summer, 6 spring and autumn, 5 winter; youths 4, elders 5 |
| a year | 24 days in the region spec (seasons of 6) |
| farming | sowing 1 unit puts in 3 seed; the crop returns 5x the seed in 6 days; reaping is 2 units for 6 grain; weeding up to +50% |
| a net ration of grain | about **0.5 units** of work |
| fuel | 0.5 timber a house a night, 2 in the cold; a fell is 2 units for 3 timber |
| grain | eaten as porridge at a hearth with no grinding (D2-44); **it never spoils** (spoil 0.0) |

So the critique is right on its main point: a person's food costs about 0.5 units a day of a 6-unit day, about 8%.

## 1. The plot unit (D4-23: about what one adult can work in a season)

Taking a plot as the land one adult farms with half its growing-season units by hoe and weeding (the other half goes to grinding,
fuel, herding, building), a plot is about **5.4 of 02l's seed-sized plots**: **about 16 grain of seed a sowing**, three crop slots in
the growing season of a 24-day year.

| Method | Units a crop slot | Net food a slot | Net food a year | Plots one adult can work | Plots a household of 5 needs | Units a ration |
|---|---|---|---|---|---|---|
| sow and reap, grain then fallow | 5.4 | 11.6 | 35 | 3.5 | 3.5 | 0.47 |
| hoe and weeding, grain then fallow | 19.0 | 32.4 | 97 | **1.0** | 1.2 | 0.59 |
| hoe and weeding, grain then legumes | 38.0 | 52.8 | 158 | 0.5 | 0.8 | 0.72 |
| ox plough and weeding, three fields | 17.2 | 41.4 | 124 | 1.1 | 1.0 | 0.42 |
| ox plough, weeding and manure, grain-legume | 28.5 | 58.5 | 175 | 0.7 | 0.7 | 0.49 |

- **The ox lets one adult work 1.5-2 plots only if weeding is dropped** (it is optional, D2-11): weeding and reaping, not
  breaking the soil, are most of the work per plot. With weeding kept, the ox mainly raises food per unit (0.42 against 0.59).
- **Land per mouth:** a household of 5 needs about 1-1.5 plots under the household methods, 3.5 under the minimum.

## 2. A household's year: what absorbs the work

A household of 5 (3 adults, a youth, an elder: 648 units a year), with an ox and a cow:

| Grinding for porridge | Growing food | Grinding | Fuel | Herding | Hay | House | Tools | Food + grinding | All sinks | Left free |
|---|---|---|---|---|---|---|---|---|---|---|
| none (D2-44 as decided) | 66 | 0 | 14 | 24 | 4 | 3 | 3 | 10% | 18% | 82% |
| coarse meal (6 grain a unit) | 66 | 20 | 14 | 24 | 4 | 3 | 3 | 13% | 21% | 79% |
| quern flour (4 a unit) | 66 | 30 | 14 | 24 | 4 | 3 | 3 | 15% | 22% | 78% |

**Grinding alone does not get there.** It adds 5 points. What brings food and its processing to 25-30%:

| Household | Units to grow a ration | Grinding | Food + grinding | All sinks |
|---|---|---|---|---|
| 3 adults, a youth, an elder | 0.55 | none | 10% | 18% |
| 3 adults, a youth, an elder | 0.85 | quern | 20% | 28% |
| 2 adults, a youth, 2 children | 0.55 | quern | 20% | 30% |
| 2 adults, a youth, 2 children | 0.85 | quern | **28%** | 37% |

Three things together reach the target: **grinding** (quern, about 0.25 units a ration), **dearer grain** (about 0.85 units a
ration instead of 0.5: the engine's farming is too generous, with no soil work, a 5x return and 3 grain a reaping unit), and **a
real dependency ratio** (children eat before they work: 37.1, D4-19). Fewer units a day is the blunt alternative; the sinks are
better because each one makes something worth buying (a mill, a copper axe, a child's herding).

Two further points:
- **Grain that never spoils** removes storage as a cost and a reason for bins, cellars and granaries. A small rate in a house
  (about 1% a day), less in bins and cellars, restores it.
- **Labour does bind at the peaks already** (region.yaml: about 60 units of reaping in a two-day window; cold nights at 2 timber a
  house), so tools that save work at the peaks (the sickle at harvest) are worth something even now. On average it does not.

## 3. Mills

| Mill | Needs | Units a ration | Saved against a quern | Capital | Cost a year | People to pay it, no toll | Most toll before querns win | Toll that covers it at 15 people |
|---|---|---|---|---|---|---|---|---|
| hand millstones | 10 stone, a mason, a room | 0.083 | 0.167 | 31 | 5.1 | **1.3** | 45% | 2.6% |
| water mill | millstones, a wheel, a river site, a room | 0.025 | 0.225 | 62 | 9.2 | **1.7** | 45% | 4.6% |

- **With bread only (D2-44 as decided), no mill pays at any size:** a loaf costs 0.19-0.42 units of grinding, baking and fuel for
  0.055 units of extra food. The critique is right.
- **If all grain must be ground to eat, any mill pays from about two people,** because it saves the grinding on every ration.
  Mills then appear wherever a mason (and for a wheel, a river and a carpenter) is found, as they did. The chokepoint is no longer
  the threshold but **the site and the toll**: a holder can charge up to about 45% of the grain before households go back to their
  querns, and about 3-5% covers the mill at 15 people (historical multure was about 6%). Between those lies the rent a mill's holder
  can take, and the reason a lord wants the mill and households keep querns.
- **Recommendation for D2-44:** grain must be ground before it is eaten: coarse meal for porridge (or flour), by quern at home or
  at a mill; bread from flour stays as decided (11 from 10, eaten without a hearth, keeps). The mill's value is the grinding it
  saves, not bread's tenth.

## 4. One mill for several nodes, and mastery

**Carrying grain to a water mill and flour back** (02g §3's costs a unit an edge):

| Carried by | Edges away | Carrying a ration both ways | Worth it against a quern (saves 0.225) | Against hand millstones at home (0.058) |
|---|---|---|---|---|
| on foot | 1 | 1.84 | no | no |
| pack ox | 1 | 0.38 | no | no |
| ox cart | 1 | 0.15 | **yes** | no |
| ox cart | 2 | 0.30 | no | no |

**A mill serves its own node, and a neighbour one edge away by ox cart, not more.** Within a node, moving between sites is free,
so everyone at the node uses one mill. A cluster of nodes (D4-11) shares a mill only if they are one cart-edge apart on a track;
otherwise each node with a mason builds hand millstones. So the society is distributed across nodes for bulky staples only at the
range of an ox cart. Goods that are dear for their weight (tools, blades, coin, documents, cheese) are what a region shares.

**Mastery** (trade curve 0.5 + 1.5(1 - e^(-p/tau)), x1.8 counted as master; basic work 1.0 to 1.5):

| Trade | Work a person needs a season | People to keep one full-time | People for mastery in one season (tau 50) |
|---|---|---|---|
| farmer | 9.9 | 9 | **10** |
| woodsman | 4.3 | 21 | 23 |
| miller | 1.5 | 61 | 67 |
| smith | 1.5 | 61 | 67 |

| tau | Practice to master | People a master farmer needs | A part-timer (a third of its season) on the trade curve | On the basic curve |
|---|---|---|---|---|
| 25 | 50 | 5 | x1.56 | x1.35 |
| 50 | 101 | 10 | x1.18 | x1.23 |
| 100 | 201 | 20 | x0.89 | x1.13 |

- **At tau about 50, a master farmer needs about 10 people,** inside a node of 15. 02d's "about 24" came from the old engine,
  where the forest fed the first 10 people; with fields feeding most mouths the threshold falls.
- **Smiths and millers can never be kept busy by one node, or reach mastery from its demand:** each person needs only about 1.5
  units of their work a season. They are regional trades: seeded as masters (D4-21, D4-33), serving several nodes through goods
  that carry well (tools travel at about 12 units of value a unit of weight; 02m). That fits the first region (Coppergate's forge,
  Millford's mill).

## 5. Where the critique is wrong or overstated

- **"Nothing makes labour scarce":** on average, yes; at the peaks (the harvest window, the cold nights), labour already binds.
- **"Any tool that only saves work is worth little":** not at the peaks: the sickle's x1.5 at harvest and the axe's x2 on cold
  days matter now.
- **"The mill pays at no village size":** true for D2-44 as decided; false once grinding is needed to eat grain (about two people).
- **The node cap against 02d's thresholds:** 02d's thresholds were in old-engine actions with a forest that fed the first 10. In
  cybertron2's units the master farmer needs about 10 people and the mill about 2; only the low-volume trades (smith, miller as a
  full-time job) exceed a node, and those should be regional by design.

## 6. Recommended decisions

1. A plot is the land one adult works by hoe and weeding with half its growing-season units: about 16 grain of seed a sowing.
2. Grain must be ground before it is eaten (porridge from meal, bread from flour): quern about 0.2-0.25 units a ration, hand
   millstones about 0.08, a water mill about 0.025.
3. Growing grain should cost about 0.85 units a net ration (the engine's 0.5 is too generous): require breaking the soil, and lower
   the return or the grain a reaping unit brings in.
4. Grain spoils a little in a house (about 1% a day), less in bins and a cellar.
5. Skill by practice on all work with tau about 50 units: trades from x0.5 to x2.0, basic work from x1.0 to x1.5.
6. Smiths and millers are regional trades, seeded as masters; a node's own demand cannot make them.
7. A mill serves its node and neighbours one ox-cart edge away; clusters of nodes share staples only on tracks.

## Sources

[02n_labour_model.py](02n_labour_model.py), [02l](02l_farming.md), [02m](02m_recipes_model.py), [02d](02d_ladders.md),
[02g §3](02g_resources_and_transport.md); `cybertron2/engine/data.py`, `cybertron2/specs/region.yaml`; D2-11, D2-44, D4-11,
D4-13, D4-17, D4-19, D4-21, D4-23, D4-33.
