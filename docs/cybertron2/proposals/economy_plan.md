# Proposal: the economy plan for cybertron2

**Status:** partly accepted and built (swept 5 Nov). The first region was adopted as the target world (38.08 §1), then replaced by
02t's four villages (D2-137; cybertron2/specs/region.yaml, with the inn at Millford). Built in part: E1 (offers and agreements, D2-25
to D2-40), E2 (skill by practice, D2-52; standing orders only for children, D2-148; the fallback, D4-76), E3 (farming, buildings,
mills and ovens), E4 (pack, handcart and pack ox, D2-135, D2-136), E5 (copper coin, D2-28). Not built: ledgers, letters, consignment,
tolls, ox carts (L-53). E6 is under way (the dependence ladder, L-50: designed, not run). Still open: 2 questions (3, and salt in 4).
**Owner:** 37.2. **Affects:** the build plan (37.4's milestone M4); spec/economy/ (all files); seeding/ (the first region, with
37.4); measurement/ (economic measures).

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

1. ~~Carrying capacities and weights (OPEN C-1: 02g's numbers proposed), calibrated so grain travels one edge at a profit, not
   three.~~ Decided: D2-135 (C-1 resolved 24 Oct, 02u); built in data.py (pack, handcart, the pack ox of D2-136).
2. ~~Skill by practice (0.5 novice to 2.0 master, decay) and the automation rule (transfers and standing offers free, routine work
   spends units, decisions never automated).~~ Skill decided: D2-52 (D2-64 for farming); built (data.SKILL, knowledge.py), except
   fading without practice, which the spec has and the engine does not. The automation rule in parts: offers cost no units (D2-25),
   routine work by standing orders (D4-16) and the fallback (D4-76); no decision states the whole rule.
3. The levers for a 2-2.5x organised advantage (02d §5b). Still open (38.20 C6 was never answered). Since then D2-55 (land binds, not
   labour), the mill ladder (D2-61, D2-166, D2-167) and the master farmer (D2-64) each give part of it; no target is decided.
4. ~~Inns and hosts in the first region (02g §7.4)~~ (decided with the region: D2-137, the Bell household's inn at Millford;
   spec/economy/lodging.md); salt's place (02g §7.5): still open. No world has a source of salt: data.py has salt as an item, used
   only by cheese, and no technique makes it.

## History

- 22 Oct: 02a §3 and P1-P6 planned the economy on the old engine.
- 22 Oct: Zach: space is a new engine; then: rewrite the plan for cybertron2, with merchants, transport and households. 02f written.
- 22 Oct: D2-1 (coin carried), D2-2 (one merchant household).
- 22 Oct: 02g extended it: resources, livestock, the transport ladder, inns, the society-scale layers.
- 22 Oct: 37.4's build plan (38.08) adopted the first region as the target world and placed the economy at M4.
- 23 Oct: 02l added farming to E3.
- 5 Nov: Swept against DECISIONS, the spec and what is built (37.2): questions 1, 2 and the inn decided (D2-135, D2-52, D2-137); the
  organised advantage and salt's place still open; the Status line records what of E1-E6 is built.

## Sources

[02f](../../review/37_growth/02f_economy_plan.md), [02g §5](../../review/37_growth/02g_resources_and_transport.md),
[02b](../../review/37_growth/02b_productivity.md), [02d](../../review/37_growth/02d_ladders.md),
[02l](../../review/37_growth/02l_farming.md), [38.08](../../review/38_space_engine/08_build_plan.md); D2-1, D2-2, D4-11.
