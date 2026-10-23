# Proposal: the economy plan for cybertron2

**Status:** discussion (23 Oct); the first region adopted by 37.4 as the target world (38.08 §1). **Owner:** 37.2. **Affects:** the
build plan (37.4's milestone M4); spec/economy/ (all files); seeding/ (the first region, with 37.4); measurement/ (economic measures).

## Summary

The economy works at **two scales**: inside a node (households, mostly generalists, one or two specialists the node's size can
carry) and between nodes (comparative advantage by node kind, with the deep layers at the place that serves several nodes, and
merchants carrying everything). It is built in six phases, E1-E6, on 37.4's core (M1-M3), as 37.4's milestone M4, and calibrated on a
seeded four-node region of about 40 people. Layers only a society can afford (mill, granary, smithy, roads, mint) appear where
the population within their range meets their threshold.

## The proposal

### Two scales (02f §2)

- **Inside a node:** moving goods between sites is free; households beat a village below about 11 people (02d), so a hamlet of
  15-20 holds mostly generalist households, a smith or a keeper at most.
- **Between nodes:** central place theory. Each layer has a threshold (the population it needs) and a range (how far its customers
  can be); a node hosts it only if the population within its range meets the threshold. Merchants make the range larger than a node.

### Phases (02f §3)

| Phase | What |
|---|---|
| E1 | exchange at a node: escrowed swaps, standing offers, prices per node (exchange_and_money.md) |
| E2 | households at work: standing work orders, the house pot, skill by practice, tools |
| E3 | production and buildings: sites with the five production shapes, recipes, buildings from parts (buildings.md), farming (02l) |
| E4 | transport and merchants: carrying capacity and weight (02g §3's ladder), goods in transit, consignment, letters |
| E5 | money and credit: carried coin, debts as records, ledgers, tolls and levies |
| E6 | calibration and acceptance on the first region: organised load at or below 30% of work, a node cut off at about 50-60%; the cut test per route |

In 37.4's build plan (38.08) these are M4, after the core (M1), the environment (M2) and institutions (M3); 37.2 designs and may build
against M1's interfaces after posting on the board.

### The first region (02f §4)

| Node | People | Has | Lacks |
|---|---|---|---|
| Millford (market town, river) | 2 households and a merchant house (about 14) | mill, smithy, market, store | grain of its own, ore, much timber |
| Barleyfield (farm village) | 3 households (about 14) | fields, granary | tools, metal, timber beyond fuel |
| Ashwood (wood hamlet) | 2 households (about 8) | timber, game, charcoal | fields |
| Coppergate (hill camp) | 1 household (about 4) | copper seam, forge | any food |

Edges: Barleyfield-Millford 1 day, Ashwood-Millford 1, Coppergate-Ashwood 1, Coppergate-Millford by the pass 2 (with a waypoint).
Chokepoints: the mill, the smithy, the pass, the merchant house's cart and ledger. 38.08 scales it down for the first runs (3 nodes,
about 12 agents).

### Layers only a society can afford (02g §5)

| Layer | Threshold (rough) | Chokepoint |
|---|---|---|
| watermill | 25-70 people | the miller's toll |
| ox team and plough | 3 or more households (02l: a common herd) | who gets the team first |
| granary | a village | who is fed in a famine |
| smithy | about 20 people within reach | tools for everyone |
| salt works | one site per region | the region's salt |
| ox carts | about 16 units a day on a route | the route |
| roads and bridges | about 115 units a day | tolls |
| inn and stables | 3-5 travellers a day | who travels, and what they know |
| market days | a town | stalls, dues |
| mint and ledger house | a region | money itself |

Each must sit on a large share of what people need, or it moves little (Amdahl, 02b §4.3).

### What to measure (02f §5)

Load per node against the same node cut off; trade volume, prices and the price gap between nodes; information lag on prices;
defaults and their cost; the cut test per route.

## Why

The old-engine plan (P1-P6, an opt-in `economy` block) assumed one place. In cybertron2 a node holds 15-20 people, too few for the
deep layers, so the economy's depth must come from several nodes linked by carriers. The phases put the cheapest general fix first
(safe exchange), then what makes specialisation pay (households, skill, tools), then the chains, transport and money.

## Alternatives considered

- **The old-engine plan P1-P6:** superseded by this plan (22 Oct).
- **A single large settlement:** rejected by node scale (D4-11); a larger settlement is a cluster of nodes.
- **A 12-agent, 4-node hamlet as the first LLM run** (an earlier draft): replaced by 38.08's scaled-down region.

## Open questions

1. Carrying capacities and weights (OPEN C-1: 02g's numbers proposed), calibrated so grain travels one edge at a profit, not three.
2. Skill by practice (0.5 novice to 2.0 master, decay) and the automation rule (transfers and standing offers free, routine work
   spends units, decisions never automated).
3. The levers for a 2-2.5x organised advantage (02d §5b).
4. Inns and hosts in the first region (02g §7.4); salt's place (02g §7.5).

## History

- 22 Oct: 02a §3 and P1-P6 planned the economy on the old engine.
- 22 Oct: Zach: space is a new engine; then: rewrite the plan for cybertron2, with merchants, transport and households. 02f written.
- 22 Oct: D2-1 (coin carried), D2-2 (one merchant household).
- 22 Oct: 02g extended it: resources, livestock, the transport ladder, inns, the society-scale layers.
- 22 Oct: 37.4's build plan (38.08) adopted the first region as the target world and placed the economy at M4.
- 23 Oct: 02l added farming to E3.

## Sources

[02f](../../review/37_growth/02f_economy_plan.md), [02g §5](../../review/37_growth/02g_resources_and_transport.md),
[02b](../../review/37_growth/02b_productivity.md), [02d](../../review/37_growth/02d_ladders.md),
[02l](../../review/37_growth/02l_farming.md), [38.08](../../review/38_space_engine/08_build_plan.md); D2-1, D2-2, D4-11.
