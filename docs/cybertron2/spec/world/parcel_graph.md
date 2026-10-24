# The parcel graph: where things are inside a node

## Summary

A node's parcels form a graph of neighbours shaped by the land, each parcel with a side and a height. There are no coordinates and
nobody walks or chooses a route inside a node: anyone at the node can act on any parcel the same day. Distance is steps on the
graph, and it matters for what spreads, flows, wanders and is noticed. Whoever acts senses the parcel it works, the parcels it passes
through on the way, and the ones next door. An agent can attend to the village to learn how it fits together, and gets a short
overview of what is noticeable when it arrives somewhere.

Written by 37.2 at Zach's request (24 Oct), from proposals/parcel_graph.md; the area is 37.4's. It extends world/places.md and the
parcels' `adj` lists already in every world file.

## Decided

- D2-114: the graph of neighbours, shaped by the environment and terrain; a side and a height per parcel; no coordinates; no
  movement inside a node.
- D2-115: acting senses the parcel worked, those passed through, and those next to it.
- D2-116: attending to the village shows how it fits together; arriving gives a concise overview of what is noticeable.
- D4-62: a day is one chain of parcels in the order of one's acts, kept in the day's record.

## Mechanics

### The graph (D2-114)

- **Neighbours:** each parcel's `adj`, two-way (as built). Generation (world/generation.md) makes them from the land: a river is a
  chain of water parcels with fields beside it, woods on the slopes, built ground near the water and the roads.
- **Side:** centre, north, east, south or west. Road ends leave from a side and its parcels (world/roads.md, D2-90).
- **Height:** a rank, 0 (the river, low wet ground), 1 (the valley floor), 2 (slopes), 3 (hilltops, ridges). Read later by water
  and taint flowing downhill (OPEN L-23); read now by nothing else.
- **Distance** is the number of steps between two parcels.
- Existing worlds without sides or heights: side centre and height 1 by default; a world file may set them.

### Sensing along the way (D2-115)

Presence for the noticing rule (information/noticing.md):

| Parcel | Presence |
|---|---|
| the one it works in | by its activity (hunting 1.0, foraging 0.7, herding 0.5, fixed work 0.5) |
| each one on its route that it does not work (below) | crossing, 0.3 |
| each one next to where it works | 0.1, for things of own conspicuousness 0.5 or more |
| anywhere else at the node | 0.05, for things of 0.8 or more |

**The route (D4-62):** one chain in the order of its acts: from where it slept (its house's parcel at this node, else the built
ground), to each parcel it works in turn (a building counts as its parcel; a parcel again if it goes back), to where it ends the
day (the road's end if it sets off tonight, else the bed it chose, else where it slept). Each leg is a shortest way; ties are
broken by a keyed draw (D2-70). The route is worked out at the end of the work step and kept in the day's record as parcels in
order, for the evening's noticing and for the map.

### The village as a whole (D2-116)

- **`attend {to: the village}`:** the agent is shown how the village fits together, in words: each parcel with its neighbours,
  side and height ("Long Acre runs down from the Green to the beck; Hollow Wood lies above it on the north side"), and where the
  roads leave ("the road to Highcombe leaves from the Common, east").
- **On arriving at a node** (a traveller, a newcomer): 3 to 5 lines of what is most noticeable there (the largest features and
  buildings, what is busy or striking): "a mill on the beck; a green with two farmhouses; barley ripe on the slope; smoke from a
  smithy". Not positions.

## Data

Per parcel: its neighbours (as now), side, height.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| presence along the way and next door | above | proposed; calibrate |
| the arrival overview | 3 to 5 lines | proposed |

## What agents see

"Next to ..." in each parcel's line (as now); the overview on arrival; the village's layout when they attend to it.

## Open

- Movement inside a node, if nodes grow large enough that a far wood should take time to reach: later.

## Sources

[proposals/parcel_graph.md](../../proposals/parcel_graph.md); cybertron2/engine/world.py (`adj`).

*Current as of 24 Oct 2026: D2-114, D2-115, D2-116, D4-62.*
