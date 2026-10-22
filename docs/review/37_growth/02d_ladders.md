# 37.2d Technique ladders, the extent of the market, and space

*22 Oct 2026. Analysis for 37.2. Numbers from [02d_ladder_model.py](02d_ladder_model.py) (deterministic, no model calls); the
principles are in [02c_economics_guide.md](02c_economics_guide.md). All parameters are proposals except those marked ENGINE.*

## 0. What this adds to 02b

02b compared three organisations at one size (24 agents). This model asks how the best organisation and the best technique change
with the **number of people at a node**. Two changes make that question meaningful:

- **Skill is learnt by practice** (guide §5): a trade's multiplier depends on the actions a round its practitioner spends on it. A
  specialist is a master only if the market keeps them busy.
- **The forest is a fixed flow per node** (6 food a round from plants, 4 from game, foraging at 1 food per action): its share per
  head falls as the node fills.

Needs: 1 ration and 1 fuel (timber) per agent a round. Four organisations:

| | What it is |
|---|---|
| solo | every agent alone: forages and hunts alone, farms with crude tools it makes |
| households of 4 | food pooled, one member per trade, hunting as a party of 4, crude tools |
| village | the node is one economy: specialists where demand keeps them busy; hunting parties up to 6; a mine crew, smithy and metal tools (the plough) from 12 people; mill and bakery when they pay; goods moved by standing arrangements through a store keeper (50 units an action) |
| village, spot trade | the village's specialists, but every unit changing hands costs 0.33 actions |

## 1. The best organisation depends on size

Load (share of all actions spent on needs; best food technique in brackets):

| Agents at the node | solo | households of 4 | village | village, spot trade |
|---|---|---|---|---|
| 1 | 40% | - | 49% | 57% |
| 4 | 40% | **35%** | 37% | 46% |
| 8 | 41% | **32%** | 35% | 43% |
| 12 | 44% | 32% | **31%** | 41% |
| 16 | 44% | 30% | **26%** | 38% |
| 24 | 42% | 29% | **22%** | 35% |
| 48 | 40% | 27% | **16%** | 31% |
| 96 | 39% | 26% | **14%** (bread) | 29% (bread) |

- **Small groups do best with few layers.** Below about 11 people households beat the village, whose store, keeper and clerk are
  fixed costs a small group cannot carry.
- **The village wins at every size from 11 agents**, and its lead grows with size: 22% at 24 and 14% at 96, against households'
  26-29%. More people keep more specialists busy, so more trades reach master skill.
- **Solo gets worse as the node fills.** Its forest share falls and it farms as a novice.
- **Spot trade never beats households** in this range. Specialisation without cheap exchange is worse than none (02b §4.4 again).

## 2. Skill and the extent of the market

| Agents | Forest actions a round | Farm actions a round | Farmer's skill | Metal tools |
|---|---|---|---|---|
| 4 | 4.0 | 0 | - | no |
| 8 | 7.1 | 0 | - | no |
| 12 | 8.2 | 0.7 | x1.07 | yes |
| 16 | 8.2 | 1.6 | x1.47 | yes |
| 24 | 8.2 | 3.0 | x1.80 | yes |
| 48 | 8.2 | 7.7 | x1.89 | yes |

Up to about 10 people the forest feeds the node. Above that, the extra people are fed from fields. The farmer becomes a master only
when there is about three actions a round of farming to do (about 24 people at one node). Skill by practice:

| Practice (actions a round in the trade) | 0 | 0.25 | 0.5 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|---|
| Multiplier | 0.50 | 0.73 | 0.93 | 1.23 | 1.60 | 1.80 | 1.90 |

## 3. The food ladder and the mill's threshold

Village load by food technique:

| Agents | raw grain (porridge) | hand-milled | mill and bakery |
|---|---|---|---|
| 4 | 37% | 37% | 48% |
| 12 | 31% | 32% | 34% |
| 24 | 22% | 23% | 23% |
| 48 | 16% | 19% | 17% |
| 96 | 14% | 16% | 14% |

The mill and bakery carry a fixed cost (construction and upkeep). They win only once the grain flow fills their batches. How the
**threshold**, the population from which bread pays at every larger size, moves with the design:

| Design | Threshold (agents at the node) |
|---|---|
| porridge feeds 1.0 a grain, mill 1.4, construction 40 work | 69 |
| cheaper mill (half the construction) | 67 |
| better mill (1.6 rations a grain) | 49 |
| porridge feeds less (0.8 a grain) | 41 |
| porridge 0.8 and mill 1.6 | **25** |

**The threshold is set by the gap between the rungs, not by the building's cost.** Halving the construction barely moves it,
because once spread over 40 rounds it is small. What moves it is how much better bread is than porridge. To make the mill a
chokepoint in a town of about 25, raw grain must be a poor food (0.8) and the mill a good one (1.6). That is a design decision about
the food itself.

## 4. Space: carrying goods to the eaters

The same village of 24, with every ration and fuel unit carried to the eater at a cost per unit:

| Actions per unit carried | Village load | Extra actions a round | Still beats households of 4? |
|---|---|---|---|
| 0 | 22% | 0 | yes |
| 0.02 | 22% | 0.8 | yes |
| 0.05 | 24% | 1.9 | yes |
| 0.1 | 26% | 3.8 | yes |
| 0.2 | 29% | 7.6 | no |
| 0.4 | 37% | 15.2 | no |

The organised village's advantage over households is about 7 actions a round. Transport above about 0.2 actions per unit eats all of
it.

**For the map:** if a porter carries 10 units an action along an edge (0.1 actions per unit-edge), a village's specialists can serve
eaters about one edge away and no further. A cart that doubles the load doubles the range. So:

- villages are nucleated around their store and mill;
- the transport ladder (porter, cart, road) decides how large an area one town can organise;
- distance limits the reach of an institution's economy, as it will limit the reach of its enforcement.

## 5. Conclusions for the 37.2 design

1. **Size decides the organisation.** Design seeded worlds with nodes of different sizes, and expect hamlets, villages and towns to
   run different ladders: a hierarchy of places, not one economy.
2. **Make the forest a fixed flow per node with poor yields:** about 1 food per action, capped by regrowth (Zach: 1-2 actions for
   1-3 food). It stays the survival floor and the exit option, and a full node cannot live on it.
3. **Skill by practice is what makes size pay:** the multiplier curve and its time constant are the main calibration of how
   strongly a society rewards organisation.
4. **Each layer's threshold comes from the gap between rungs.** Set the gaps on purpose (porridge vs bread, crude vs metal tools)
   to place each chokepoint at the town size where it should appear.
5. **Transport is the limit on range.** Calibrate the porter's load and the cart and road ladder with the map, so a town's economy
   reaches about as far as its institutions should.

## 5b. Widening the village's advantage (22 Oct, Zach: it should be bigger)

Households vs village at 24 and 48 agents, one change at a time (the model with its globals changed):

| Change | 24 agents | 48 agents |
|---|---|---|
| as calibrated | 29% vs 22% (1.33x) | 27% vs 16% (1.63x) |
| master skill 3.0 / 4.0 | 1.32x / 1.28x | 1.62x / 1.57x |
| metal tools x1.6 | 1.57x | 2.04x |
| crude tools x0.6 | 1.54x | 1.95x |
| plough x3 | 1.40x | 1.77x |
| forest food halved | 1.41x | 1.70x |
| porridge 0.8, mill 1.6 | 1.37x | 1.77x |
| master 3, metal x1.5, crude x0.7, porridge 0.8, mill 1.6, forest halved | **1.87x** (25% vs 13%) | **2.46x** (24% vs 10%) |

- **A larger skill multiplier does not widen the gap**, and can narrow it: a household of 4 also divides its trades, so it gains
  from skill too.
- **What widens it is what a household cannot have:** techniques whose threshold is above household size (metal tools, the plough,
  the mill), and poorer degenerate rungs (crude tools, porridge, a thin forest).
- **The needs bundle sets the level, the gaps set the ratio.** The combination makes everything cheap, so a deeper need (shelter,
  02e) keeps the organised society near 25% while widening the ratio.
- **Design for about 2-2.5x at 24-48 agents.** LLM agents' coordination losses fall harder on the village than on the household, so
  a designed 1.3x may vanish in play.

## 6. What the model leaves out

- **Steady state:** no learning time, no construction period, no start-up latency. A seeded world starts in steady state; a frontier
  settlement does not.
- **Integer people:** specialists are full-time when demand allows, otherwise one part-time practitioner. Real assignments are lumpier.
- **One node at a time,** with carrying cost as a flat per-unit charge. No graph, no edges of different lengths.
- **Behaviour:** LLM agents waste actions and forget orders. The model gives capacity, not behaviour; the dry runs and the first live
  rounds give the real numbers.
