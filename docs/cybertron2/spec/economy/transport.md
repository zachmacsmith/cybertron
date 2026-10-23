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

## Mechanics

- **Only what is carried crosses an edge** (D4-9): goods, letters, coin and passengers travel with a traveller.
- **In transit** a traveller is at no node and makes no decision until it arrives (D4-8, D4-10).
- **A cart** needs a draught animal with a harness (D2-23).
- A traveller who dies on the road is not announced; those at home know only that it left and what it said it would do (D2-4).
- Weight and carrying capacity: 37.4's mechanism and 02g's numbers, not yet decided (OPEN C-1).

## Data

Per item: weight. Per carrier: its means of travel and capacity. Per traveller in transit: edge, day of arrival, what it carries.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| capacities by means of travel | 02g §3 (on foot 10, pack 20, pack ox 60, handcart 40, ox cart 200) | calibrate (OPEN C-1) |
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

*Current as of 23 Oct 2026: D2-2, D2-4, D2-23, D4-8, D4-9, D4-10.*
