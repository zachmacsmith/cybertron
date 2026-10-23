# Edges and travel

## Summary

Nodes are joined by edges with a length in days. Travel is the last act of a day; the traveller is on the road until the morning it
arrives, and decides there. Waypoints are real nodes.

## Decided

- D4-3: travel takes time; there is no moving as a pre-action (replaced in part by D4-8).
- D4-8: arrive, then decide: travel is the last act of a day; the traveller arrives at the start of a later round and decides there.
- D4-10: both kinds of distance: edges with a length (travellers in transit make no call) and real waypoint nodes.
- D4-12: a night out costs 1.5 food (2 in winter, and the cold) (economy/lodging.md).
- D4-32: a traveller too heavy to set off is told and chooses what to leave (economy/transport.md).
- D4-47: some places start unexplored: from where its road starts the way is seen only as an unexplored way; whoever follows it
  learns the place, and others learn it by being told or led there.

## Mechanics

- **An edge** joins two nodes and has a length in days. A traveller leaves at nightfall, is on the road for that many nights, and
  arrives at dawn (D4-8, D4-10).
- **On the road** a traveller is at no node: it makes no decision, sees no node, and sleeps out (D4-10, D4-12).
- **Waypoints**: a longer journey passes through real nodes, where the traveller arrives and decides (D4-10).
- **Unexplored ways** (D4-47): an edge to an unexplored node is named, to those who do not know the node, by a description of the
  way ("a goat path up into the crags"); travelling along it is how the node is found.

## Data

Per edge: the two nodes and the days. Per traveller: from, to, the day it left and the day it arrives.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| an edge's length | per edge, in days | decided (world file) |

## Open

- Danger on edges by terrain and season (OPEN C-6); fords, passes and roads (38.04 §6).

## Sources

38.05 §2; 38.04 §6.

*Current as of 23 Oct 2026: D4-3, D4-8, D4-10, D4-12, D4-32, D4-47.*
