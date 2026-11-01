# Proposal: the landscape generator (a world under the graph)

**Status:**
- **Decided in part (3 Nov):** the generator fills in around what a world file gives (D2-173).
- **For discussion:** the world under the graph (§2 to §5), and the questions at the end.
- Design only. Not to be built until Zach asks (README rule 10).

**Owner:** 37.2, with 37.4. **Affects:**
- spec/world/generation.md (37.4's: to be compiled from this when decided), places.md, parcel_graph.md, roads.md, edges.md;
- spec/environment/ (37.2's);
- seeding/populations.md (people, second);
- the capacity check (capacity.py).

It extends 38.04 §6, which generated one point per node.

## Summary

Generate a **world under the graph**:
- a continuous landscape of land, water and climate, at a resolution finer than parcels;
- then **derive** the abstractions agents act on: nodes as settlements and their reach, parcels as patches of one cover, roads as
  least-cost routes with their landmarks.

The graph stays the way agents and the engine meet the world; the map underneath is the ground truth it is compressed from.

**Configurable (D2-173).** A world file is the input with gaps: what it gives is pinned, and the rest is filled in around it,
reproducibly, without seed searches.

**What the map is for:**
- rivers that run somewhere;
- fords where rivers are shallow;
- passes where ridges are low;
- soil where silt settles;
- floods by height;
- groundwater and wells;
- line of sight;
- room to grow into: wild land not yet in any parcel, cleared and claimed later;
- the map the visualiser draws.

## 1. Decided (D2-173)

- **The world file is the input, with gaps.** What it gives is pinned:
  - exact values;
  - ranges;
  - descriptions from a vocabulary mapped to ranges ("short of wood", "rich bottomland", "on a river", "a hill village").
- **Generation runs in layers around the pins.**
  - Draws are keyed per element (D2-70), so a change touches only what depends on it.
  - Targets (capacity at 60 to 70% of flows, food's share of work, a village short of fuel) are met by adjusting what is unpinned.
- **Pins win where the physics allows.** A pin the physics can't meet is refused, with the reason.
- **Descriptions of places** are written by a model once and frozen into the output.
- **The output** is a complete world file, frozen with the run.
- **Order:** the land and region first; pins for people second.

## 2. The world under the graph (for discussion)

### 2a. What it is

- **The mesh.** A mesh of cells on a hidden plane: about a hectare to a few hectares each, so a parcel is a patch of cells and a
  node is thousands of them.
- **What each cell carries:**
  - elevation;
  - temperature and moisture (climate);
  - drainage: flow, and whether a river or lake runs here;
  - groundwater depth;
  - soil depth and fertility;
  - cover (vegetation);
  - resources: stone, ore, clay, peat, game, fish;
  - exposure to hazards: flood plain, fire-prone heath, avalanche slope.
- **Its relation to the graph.** The mesh is never shown to agents. It is the ground truth that the graph is compressed from, and
  that the visualiser draws.

### 2b. The physical layers, in order

| Layer | From | Gives | Pins it takes |
|---|---|---|---|
| **elevation** | noise shaped by ranges, a coast or lake; no erosion simulation | hills, valleys, ridges, passes (low points on ridges) | "a range to the north", "a pass between Hollins and Wenmoor", a height at a place |
| **climate** | latitude or a north-south gradient, elevation (colder high), prevailing wind (wet windward, rain shadow lee) | temperature and moisture per cell | "a dry east", "a cold upland" |
| **hydrology** | each cell drains to its lowest neighbour; flow accumulates; lakes fill hollows; wetland where flat and wet; springs where groundwater meets a slope | rivers (width and depth by flow), lakes, fens, springs; fords where a river is wide and shallow; narrows where it is deep | "a river from the hills through Barleyfield", "a ford at Millford", "a fen south of the village" |
| **soil** | slope (thin on steep ground), parent material, river silt (deep and rich on flood plains), drainage | depth, fertility, wetness | "rich bottomland", "poor stony soil" |
| **cover** | climate, soil, height (a biome table: 38.04 §2's kinds) | old forest, woodland, heath or moor, grassland, fen, rock | "old forest two days out", "short of wood" |
| **resources** | the terrain: stone on steep and high ground, ore by a geology mask, clay by rivers, peat on wet moor, game in forest, fish in rivers | where each can be got and how much | "copper in the hills", "no stone near the village" |
| **hazards** | height and cover: flood plain, fire-prone heath, avalanche slope | each cell's exposure, read by the scheduler (D2-69) | |

### 2c. The human layer

- **Siting.** Settlement sites are scored on:
  - fresh water;
  - flat fertile land;
  - a river crossing;
  - fuel within reach;
  - shelter and defence.

  Founders take the best. Sites are spaced by a day's walk.
- **Pins:** "four villages", "a market town at the ford", "a forest hamlet".
- **Land use rings** around each site (the von Thünen pattern), from the site outward:
  1. gardens and closes;
  2. fields;
  3. pasture and meadow (meadow by the water);
  4. woodland and waste.

  This is infield and outfield without any distance rule.
- **Roads:**
  - least-cost routes between sites over the terrain: slope, cover and water;
  - fords and bridges where a route crosses a river;
  - passes where it crosses a ridge;
  - narrows where it threads a gorge;
  - minor ways through cover become hidden ways.

### 2d. Deriving the graph

- **Nodes.** A node is a settlement site and its reach: the land within a few hours' walk, out and back in a day (D4-11). Wild
  places people go (a forest a day out, a pass, a camp) are nodes where a road needs a stop.
- **Parcels:**
  - contiguous patches of one cover within a node, merged and capped at about 6 to 15, so the overview stays readable;
  - each with its size, side and height, and its neighbours read from the mesh.
- **Wild land.** Land in a node that is in no worked parcel is **wild land**: the moor, the waste, the deep wood. It is held as a few
  large parcels, which can be split when part is cleared or claimed. This gives the frontier, and growth without re-drawing nodes
  (L-33).
- **Edges.** An edge is a route's length in day stretches, its terrain by stretch from the cells it crosses, and its landmarks where
  it crosses features (D2-104 to D2-107).
- **Per-place state:**
  - each parcel's resources come from the sums over its cells (a wood's trees from its cover and size, D2-156);
  - each parcel's fertility from its soil;
  - each node's groundwater and each river reach from hydrology (environment_state.md, L-23).

### 2e. Through a run

- **The mesh is kept as the ground truth.**
  - Felling and clearing change cells' cover, and the parcels follow.
  - Rivers and hills don't change.
- **Systems that can read it later:**
  - floods by height;
  - sight across ridges (D2-74);
  - bridges by a river's width (L-34);
  - water by groundwater depth;
  - the visualiser's map.

## 3. Pins, targets and checks

- **Pins** are given by place name or by feature, at any layer. Each layer generates only what is unpinned, treating pins as fixed:
  - a river given is laid first and the land shaped so that it runs downhill;
  - a height given is a point the elevation passes through.
- **Targets** are met by monotone adjustment of what is unpinned:
  - capacity of each node at 60 to 70% of flows (D2-161), through wood and plots;
  - fuel or food as the scarce thing in a named village;
  - a road's length in days.
- **Checks** before a world is used: 38.04 §6, plus the scenario_design rules, made automatic:
  - rivers run downhill;
  - land kinds fit their height and moisture;
  - capacity is in range;
  - no node is self-sufficient, and each settlement depends on at least two others;
  - at least one chokepoint;
  - every access gate reachable.

## 4. Descriptions

**What gets written:** each place, parcel, road stretch and landmark gets a description, written by a model from its facts:
- cover;
- height and side;
- soil;
- water;
- what is near;
- what a local would say of it.

**How it stays consistent:** the description is written once and frozen into the output file. The facts are stored beside the
words, so the engine's signs and the text never disagree.

## 5. People (second)

`generate.py` already grows a society from founding couples. With the land generated, founders settle by the siting scores, and
pins name:
- households;
- persons;
- ties;
- trades;
- models (D4-20);
- customs (D4-64).

The generator fills in the rest around them, keyed per element in the same way.

## Open questions (for Zach)

1. A mesh finer than parcels (about a hectare a cell) kept as ground truth, with nodes, parcels and roads derived from it (§2a,
   §2e)?
2. A node's parcels cover all its land, with wild land as a few large parcels that can be split when cleared or claimed (§2d)?
3. Nodes at settlements and at wild places a road needs (a forest a day out, a pass), derived by rule (§2d)?
4. Physics kept simple: noise, flow accumulation, rules and a biome table, with no erosion or climate simulation (§2b)?
5. Land-use rings round settlements as the default layout, overridable (§2c)?

## History

- 3 Nov: Zach: start with the generator; worlds highly configurable for land and people, arbitrary specifics filled in around,
  reproducibly, with no seed search; then pins win where physics allows, a vocabulary of descriptions, model-written descriptions
  frozen, land first (D2-173); then: what to explore, given a broader world with nodes as a compression of it. Written.

## Sources

[38.04 §2, §5, §6](../../review/38_space_engine/04_places_design.md); spec/world/generation.md (D4-22);
[environment_state.md](environment_state.md) (L-23); [parcel_graph.md](parcel_graph.md); [road_layout.md](road_layout.md);
OPEN L-32 to L-34; D2-70, D2-104 to D2-107, D2-156, D2-161, D4-11.
