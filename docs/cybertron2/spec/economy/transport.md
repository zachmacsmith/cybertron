# Transport

## Summary

Goods, letters and people cross between nodes only by being carried, over edges that take days. What one carrier can take depends
on how it travels. Merchants are the carriers of trade. Shared file: 37.4 owns the mechanism (travel, carrying, transit), 37.2 the
numbers (capacities, costs).

## Decided

- D4-8: travel is the last act of a day; the traveller arrives at the start of a later day and decides there.
- D4-9: transport and communication between nodes are delayed and carried; merchants carry trade, messages and passengers.
- D4-10: edges have a length in days; waypoint nodes are real nodes.
- D2-2: one merchant household with a cart is seeded in the first region.
- D2-4: a death on the road is never announced; the household saw the departure and remembers the stated plan.
- D2-23: carts, harness (an ox pulls) and saddle (a horse carries a rider).
- D2-135: carrying capacities (below).
- D2-136: the pack ox.
- D2-134: riders in a cart sleep as in a damaged house (lodging.md).
- D4-32: a traveller too heavy to set off is told and chooses what to leave, with a person or at a house.

## Mechanics

- **Only what is carried crosses an edge** (D4-9): goods, letters, coin and passengers travel with a traveller.
- **In transit** a traveller is at no node and makes no decision until it arrives (D4-8, D4-10).
- **A cart** needs a draught animal with a harness (D2-23).
- A traveller who dies on the road is not announced; those at home know only that it left and what it said it would do (D2-4).
- **Carrying capacity** (D2-135), in weight, the best one carried counting:

  | Means | Carries | Needs |
  |---|---|---|
  | on foot | 10 | nothing |
  | a pack | 20 | a pack (a hide and a timber) |
  | a pack ox | 60 | an ox with a harness, led (D2-136) |
  | a handcart | 40 | a road with a track |
  | an ox cart (later) | 300 to 400 | two oxen with harness, a track |

- **The pack ox** (D2-136): an ox with a harness carries 60 on any road, led by someone of its household; it travels with that
  person's party (as an accompanied herd: livestock.md); it grazes on stretches that pass grass (farmland, plain, river valley, a
  meadow: world/roads.md), and otherwise eats 1 hay a day from its load; it stays part of its owner's herd, can stray if left
  unwatched at a node, and can be taken (D4-23). An ox that carries is not ploughing.
- **Too heavy to set off** (D4-32): a traveller over its capacity is told its load and asked what to leave; it may give goods to someone
  at the node or leave them at a house there (`leave`), whose household finds them the next morning; then it sets off, or stays.

## Data

Per item: weight. Per carrier: its means of travel and capacity. Per traveller in transit: edge, day of arrival, what it carries.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| capacities by means of travel | above | decided (D2-135); calibrate |
| a pack ox's hay a day off grass | 1 | decided (D2-136); calibrate |
| weights by good | 02g §3, 38.06 §3 | calibrate |

## What agents see

What they carry against what they can carry ("you can carry about 4 more timber"); travellers leaving and arriving, and what they
visibly carry.

## Open

- The transport ladder (costs per unit per edge, break-evens, people, rest and danger by means of travel; later rungs):
  proposals/transport_and_lodging.md.
- OPEN C-1 (capacities), C-6 (danger per edge).

## Sources

[02g §3](../../../review/37_growth/02g_resources_and_transport.md), [02g_transport_model.py](../../../review/37_growth/02g_transport_model.py),
38.05 §2, 38.06 §3; proposals/transport_and_lodging.md.

*Current as of 24 Oct 2026: D2-2, D2-4, D2-23, D2-134 to D2-136, D4-8 to D4-10, D4-32.*
