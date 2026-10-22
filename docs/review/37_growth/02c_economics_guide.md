# 37.2c The economics of this world: a design guide

*22 Oct 2026. How to design resources, techniques, buildings and chains so that a society is worth organising. It is the reference
for 37.2 and for anyone writing a world. The analyses behind it are in [02b_productivity.md](02b_productivity.md) (value per action
under three organisations) and [02d_ladders.md](02d_ladders.md) (technique ladders, the extent of the market, space). Numbers not
marked ENGINE are proposals to calibrate in dry runs.*

**Space.** Everything here is written for the graph of places (board Post 2, review 17). Every stock, plot, building and worker is
at a node; a one-node world is the special case. Where space changes a rule, the rule says so.

## 1. The two scarce things

1. **Actions.** About 4 an agent a round. Every unit of every good costs some, and the economy is the art of making each one go
   further.
2. **Attention.** An agent decides a handful of things a turn, and every line in its prompt costs reading. A design that needs an
   agent to decide something every round about every flow fails even if it has the actions.

Land and stocks are scarce too, but they bind through actions: a poor plot is one that takes more actions per ration.

The unit of account is the **action**. The **load** of a society is the share of its actions that its needs take. Everything else
(politics, building, defence, children) lives in what is left.

## 2. The full cost of a unit

A unit's cost in actions is the sum of:

| Term | What it is | Typical size (organised economy) |
|---|---|---|
| production | 1 / (yield per action) | 0.2-0.5 a ration |
| inputs | the actions embodied in its inputs | |
| tool wear | the actions to replace what using a tool wears out, per unit | 0.01-0.1 |
| capital | its share of the buildings it needed: construction over a horizon, plus upkeep | 0.01-0.2, falling with volume |
| handling | moving it between hands (store, delivery, trade) | must be below about a tenth of production (§7) |
| transport | carrying it between nodes: units x edges x actions per unit-edge | 0 at one node; the limit on range (§9) |

A technique is worth adopting when its full cost per unit, at the volume it will actually run at, beats the alternative.

## 3. Production functions: the five shapes

Use these shapes, not ad hoc formulas. Each has a known behaviour and a place where it belongs.

| Shape | Formula | Behaviour | Use for |
|---|---|---|---|
| **flat** | q = y x skill x tool | constant returns; one agent is as good as a crowd | felling, quarrying, simple gathering |
| **stock-limited** | q = y x S/K, stock regrows logistically | high yield when little used, falls as use rises; the stock's regrowth caps the node's total; overuse destroys it | foraging, game, fish, wild timber: the commons |
| **crew S-curve** | Q(n) = Qmax n^h / (n0^h + n^h) | a small crew loses; output per worker peaks at the best crew size (where average product is highest, not total); crowding after | hunting parties, mines, harvest teams, construction gangs |
| **batch** | one action handles B units (B large); a fixed cost per round | the cost per unit falls with volume until B is filled; below a threshold volume it does not pay | mills, ovens, smithies, stores, carts: every processing and handling layer |
| **delayed** | output arrives g rounds after the input | a pipeline: latency at start-up and after a shock, steady flow once full | crops, herds, construction, training |

Multipliers sit on top: **skill** (§5) and **tools and capital** (a factor on yield, worn out with use).

## 4. Technique ladders: every need has a degenerate rung and deeper ones

Every need can be met in several ways, from the **degenerate rung** (no layers, no capital, no partners) up to deep pipelines. The
rules:

1. **The degenerate rung always exists and always works**, but it is poor and capped. It is the survival floor, the exit option and
   what a small group lives on.
2. **Every rung pays at its own minimum scale.** No rung loses value where it is first viable: there is no dead jump.
3. **Each deeper rung is much better per unit, but only at scale.** It has a threshold (§8) below which the shallower rung wins.
4. **Fewer layers suit smaller groups.** A hamlet of 5 forages and farms in households; a village of 20 has a store and a smith; a
   town of 80 bakes bread at a mill.

**Food, the reference ladder:**

| Rung | Layers | Per action | Limit | Who uses it |
|---|---|---|---|---|
| forage | none | **1-1.5 food** (1-2 actions for 1-3 food; ENGINE today is 3.0 at full stock, too generous) | the node's plant regrowth (a fixed flow: does not grow with the people) | anyone; lone agents, outcasts, the first rounds of a frontier |
| hunt | a party | 0.8 food per effort alone, 1.6-1.8 in a party of 4-6 (ENGINE shape) | the node's game regrowth | small groups; the first team production |
| household farm | 1 (the farm) | about 1 ration (raw grain), journeyman, crude tools | land; delay g | households of 4 |
| specialist farms with a store | 2 (farm, store) | 3-5 rations with master skill and the plough | metal tools need a mine and smith (a threshold of about 12 people) | villages |
| mill and bakery | 4 (farm, granary, mill, bakery) | x1.4 rations per grain, handled in batches of 30-40 | a threshold of 25-70 people, by design (02d §3) | towns |

The forest is the degenerate rung for food: a fixed flow per node, so the more people live at a node the smaller each one's share.
That is what pushes a growing population (37.1) up the ladder.

## 5. Skill

Today only farming has skills (rotation and seed selection in `fields.py`: on-off techniques after a few practice units, teachable).
There is no proficiency in any trade. Proposal:

- **One number per trade, one meaning everywhere:** a multiplier on what one action does. Extraction: output per action.
  Processing: units handled per action (the batch size). Building: work units per action.
- **Learning by doing, in steady state:** multiplier = 0.5 + 1.5 (1 - exp(-p / 1.5)), where p is the actions a round the agent
  spends in the trade. 0 actions: novice x0.5; 1: x1.23; 2: x1.6; 3: x1.8; 4: x1.9. Implemented as experience that accumulates
  with practice and decays slowly when unused, so the steady state is this curve.
- **It produces specialisation by itself.** An agent who does five trades spends under one action a round on each and stays near
  journeyman. A specialist kept busy becomes a master. No cap on trades is needed.
- **It ties specialisation to the size of the market** (Smith: "the division of labour is limited by the extent of the market"). A
  specialist is a master only if there is enough work to keep them practising. A smith in a hamlet of 6 is a part-time journeyman.
- **Apprenticeship:** working at the same site as a master learns twice as fast. It is a contract, and it is how the order passes to
  the next generation (37.1).
- **Seeded:** agents start with an occupation and a skill level (37.6), fixed by hand when a spec wants.
- **Visible:** "Milling: master (x2.0)" in the agent's own state; the trade on the roster.
- **Leverage:** a master cannot be replaced quickly. Losing the only master miller costs the town about ten rounds of hand-milling.

## 6. Tools and capital

- **Tools multiply a trade's output and wear out** (uses per tool). Wear is what makes tool demand recurring; tools that never wear
  give the smith one sale.
- **Crude tools are the degenerate rung** (timber and an action, x0.8, 10 uses); metal tools (copper, timber, the smith, x1.0,
  20 uses) and heavy tools (the plough, x2 for a farmer) need the mine and the smithy, so they exist only above their thresholds.
- **Buildings are capital at a node:** owner (agent, household or institution), condition (decays without upkeep), capacity (crew
  places or batch size), the recipes they enable, an access rule (owner, members, allow list, a toll or share), as farms already
  have. Construction is a project: materials from the owner, work from anyone, builders' skill raising work per action.
- **Upkeep is the recurring sink.** Without it construction is a one-off demand and the material trades die once the town is built.

## 7. Handling, exchange and automation

**The rule:** handling a unit (storing, delivering, trading) must cost no more than about a tenth of producing it. With production
at 0.2-0.5 actions a ration, handling must be 0.02-0.05 actions a unit: batches of 20-50 per action, or no actions at all.

A spot trade costs about 2 actions for a lot (offer and accept): 0.33 actions a unit for a lot of 6. That erases the gain from
specialising (02b §4.4: at 0.5 actions a unit moved, institutions do no better than autarky). So goods must move by standing
arrangements, not by one-off trades.

**What to automate.** Automate the carrying out of a standing decision, never the decision.

| Kind | Examples | Costs actions? | Exists |
|---|---|---|---|
| payments and transfers | rent, wages, dues, gifts every round | no | `standing_order`, Payroll |
| subscriptions (standing trades) | "3 bread a round for 2 coin, until cancelled" | no | the Supply contract (per-round legs, escrow, could-not vs would-not, priced notice); missing: a one-action offer and subscribe |
| standing work | a household's members tend its plots; the miller grinds what arrives | **yes**, committed actions shown in the turn | new (board Post 1, rule C) |
| not automated | prices and terms, starting and ending arrangements, laws, votes, rationing, force | | |

Moving goods and coin is bookkeeping: free. Work spends actions: labour stays scarce and skill stays valuable. Automation removes
attention cost, never labour cost.

**Subscriptions on the market board.**

- A seller posts a standing offer in one action: good, quantity a round, price, notice, capacity.
- A buyer subscribes in one action, which makes a bilateral Supply contract.
- It runs until cancelled, until either side cannot pay or deliver (both are told), or until notice ends.
- The board shows each offer's subscribers and the capacity left.
- A good's **price** (board Post 1) is the volume-weighted average of its active subscriptions and its recent spot trades.

**Guards against autopilot:**

- Fixed-price subscriptions go stale when prices move, and shocks break flows: renegotiating is where the decisions are.
- Failures are loud.
- Each agent sees its flows summed ("in: 20 grain a round from 6 farms; out: 28 bread to 9 households; hopper 40, lasts 2
  rounds"), not one line per contract.

## 8. Thresholds, payback and where to put scale economies

- **Threshold (break-even scale):** the smallest volume, or the population that generates it, at which a technique's full cost per
  unit beats the rung below. For a batch layer it is roughly fixed cost a round / saving per unit. Compute it for every layer (02d
  §3 does it for the mill).
- **Payback:** at its threshold plus a margin, a building repays its construction within about a third of the run.
- **Amdahl's rule:** a scale economy improves the society only in proportion to the share of total cost its step carries (02b §4.3:
  the crew mine and the watermill moved the load by a point or two because copper only made tools and milling saved a little of
  something already cheap). Put the scale economies on the big costs: the harvest (a team or a plough team), fuel, tools that every
  trade wears out fast. A mill is a real chokepoint only if bread is most of the food and the alternatives are poor.

## 9. Space: range, threshold and the shape of settlements

Classic spatial economics applies directly once goods and buildings sit on nodes.

- **Land types decide which techniques exist at a node.** Forest: forage, hunt, fell. Arable: fields. Hills: stone, ore. River: the
  watermill (water power: a bigger batch). Techniques are tied to land, buildings to nodes.
- **Transport cost** = units x edges x actions per unit-edge. A porter carries L units an action along an edge; carts and pack
  animals (a recipe and a wheelwright) raise L, roads (a building on an edge) lower the actions per edge. That is a transport
  ladder of its own.
- **Range** (Christaller): a layer's customers can be at most d = (saving per unit) / (transport cost per unit-edge) edges away, or
  they do better at the rung below. **Threshold:** the volume it needs. A layer exists at a node only if the population within its
  range reaches its threshold. That gives a hierarchy of places: hamlets (forage, household farms), villages (store, smithy), towns
  (mill, market).
- **Nucleation:** specialisation pays only if goods move cheaply, so people gather near the store and the mill. In 02d §4, carrying
  food and fuel at 0.2 actions a unit makes a village of 24 do worse than households of 4.
- **Von Thünen rings:** what spoils or is bulky for its value is produced near the centre (bread, fresh food, fuel); what keeps and
  is dear for its weight travels (grain, metal, tools, cloth).
- **Shocks travel with goods:** delay grows with pipeline depth, buffer size and distance. Whoever holds the buffer nearest the
  shortage sees it first.
- **Accounts must be located** (review 17, condition 3): goods in a treasury or an escrow are at a node, or a global ledger
  teleports them.

## 10. Pipelines, buffers and spoilage

- **A seeded world starts with every pipeline full:** crops planted at staggered stages so some field is reaped every round, every
  buffer stocked. Food flows from round 1; latency matters only when something breaks.
- **Spoilage decides where buffers sit:** grain keeps (the granary holds grain), bread rots (bake every round). That makes the
  granary a chokepoint and its keeper the first to see a shortage.
- **Depth sets the delay and the amplification.** In a deep chain, a shortage seen late leads to over-ordering upstream, so swings
  grow toward the source (the beer-game effect). Three or four layers from field to mouth are enough.

## 11. Needs and value

- **Every good traces through recipes to a need:** food, fuel, shelter or security. A good with no path to a need is worthless
  (today's copper makes only blades).
- **Durable goods bought once create no dependence:** wear and spoilage make demand recurring.
- **Unit values are scoring numbers, not prices.** What a good is worth is what it becomes; prices come from trades and
  subscriptions.

## 12. Design checklist (at spec load and in dry runs)

1. Every good reaches a need; every recipe's inputs have a producer.
2. Every need has a degenerate rung that works, capped and poor.
3. Every rung beats the one below at its own threshold; no dead jumps.
4. Handling per unit is at most about a tenth of production per unit.
5. Every building repays its construction within a third of the run, at the volume the world will give it.
6. Scale economies sit on large shares of the cost of needs.
7. For each layer, threshold and range are computed on the map, and the seeded world has a node where each layer is viable.
8. Calibration targets (02b §4.2): autarky about 50-60% of actions, spot trade 40-45%, the organised society at or below 30%.
9. Every stock has a node, a spoilage rate and a buffer placed by spoilage.
10. Autarky arm and cut test (02a §5): breaking an institution moves the load by the amount the model predicts.
