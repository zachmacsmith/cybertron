# Proposal: the parcel graph (where things are inside a node)

> **Decided parts are in the spec:** spec/world/parcel_graph.md (24 Oct).

**Status:** partly accepted: D2-114 to D2-116 (24 Oct); sides, heights and the overview's form to confirm. Design only.
**Owner:** 37.2 (author); places, layout and perception are 37.4's ([layout.md](layout.md), [seeing.md](seeing.md)), so this goes to
them. **Affects:** spec/world/places.md, generation.md; spec/information/noticing.md, perception.md, prompts.md; world/roads.md
(road ends), livestock (wandering), environment (spread, flow).

## Summary

Parcels already list their neighbours in every world file, and the engine makes the lists two-way; they are used for little (a
hedge sign, a feature beside a building, "Next to" in the prompt). Decided (D2-114): a node's parcels form a **graph of
neighbours shaped by the land**, each with **a side and a height**, with no coordinates and no movement decisions inside a node.
Distance is steps on the graph, used for spread, sensing and wandering. **Acting senses along the way** (D2-115). An agent can
**attend to the village** for how it fits together, and gets **a concise overview** of what is noticeable when it arrives (D2-116).

## The proposal

### 1. The graph, from the land (D2-114)

- **Neighbours:** as now (`adj`, two-way). Generation (generation.md) builds them from the land: a river runs through a chain of
  water parcels with the valley's fields beside it, woods on the slopes above, the village's built ground near the water and the
  roads.
- **Side** (proposed: centre, north, east, south, west): where the parcel lies in the node. Road ends leave from a side and its
  parcels (D2-90); a watch stands on a side; raiders by a hidden way arrive on its side.
- **Height** (proposed: a rank, 0 for the river and low wet ground, 1 for the valley floor, 2 for slopes, 3 for hilltops and ridges):
  water and taint flow downhill (environment_state.md, later: L-23); floods reach low parcels first; frost lies in the low ground.
- **Distance** is the number of steps between parcels. No one decides how to walk; anyone at the node can act on any parcel the same
  day (as now).

### 2. Sensing along the way (D2-115)

Whoever acts on a parcel senses (information/noticing.md):

| Parcel | Presence |
|---|---|
| the one it works in | by its activity (hunting 1.0 ... fixed work 0.5) |
| those it passes through, on the shortest path from where it slept to each parcel it works, and back | crossing 0.3 each |
| those next to where it works | 0.1, for things of 0.5 or more own conspicuousness (a herd, smoke, a body in the open) |
| anywhere else at the node | 0.05, for things of 0.8 or more |

Sound and smell reach by the same steps: a very loud sound the whole node (D2-100), smell the spot and its neighbours (D2-101,
later).

### 3. The village as a whole (D2-116)

- **Attending to the village** (`attend {to: the village}`): the agent is shown how it fits together: each parcel with its
  neighbours, sides and heights in words ("the Long Acre runs down from the Green to the beck; Hollow Wood lies above it on the north
  side; the road to Highcombe leaves from the Common, east"), and where the roads leave.
- **Arriving somewhere** (a traveller, a newcomer, a child grown up): a concise overview of what is noticeable there, not positions:
  the biggest features and buildings, what is busy or striking ("a mill on the beck; a green with two farmhouses; barley ripe on the
  slope; smoke from a smithy"), within a small budget (proposed 3 to 5 lines).

## Why

- It keeps the node one place in the game (no walking, any parcel the same day) while letting where things are matter for what
  spreads, flows, wanders and is noticed.
- The neighbours exist already; sides and heights are two small fields that generation can set from the terrain.

## Alternatives considered

- **A plain list** (drop neighbours): breaks adjacency spreading (D2-72, D2-78), wandering herds, fences on borders, smell reach.
- **Coordinates:** distance-graded effects and direction, but every world needs geometry, agents never see it, and the graph covers
  what the decided rules need. Movement inside a node, if nodes grow large, is a later question.

## Open questions

1. Sides as centre and four directions; heights as four ranks?
2. Presence along the way and next door as in §2?
3. The village overview on arrival: 3 to 5 lines of the most noticeable things?

## History

- 24 Oct: Zach: parcels have no coordinates; keep it so? Compared a plain list, a graph with sides and heights, and coordinates;
  the engine already has neighbours. Zach: the graph's shape should come from the environment and terrain; whoever acts senses the
  parcels it is in, nearby, or must pass through, without deciding movement; some way to attend to the village as a whole and
  learn how it fits together; a concise overview on arrival of noticeable things rather than positions (D2-114 to D2-116). Written.

## Sources

[layout.md](layout.md), [seeing.md](seeing.md), [livestock.md](livestock.md), [things_in_places.md](things_in_places.md),
[environment_state.md](environment_state.md); cybertron2/engine/world.py (parcels' `adj`); D2-72, D2-78, D2-90, D2-100, D2-101,
D2-114 to D2-116.
