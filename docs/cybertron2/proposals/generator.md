# Proposal: the landscape generator (a world under the graph)

**Status:**
- **Decided in part (3 Nov):** the generator fills in around what a world file gives (D2-173); a mesh kept as ground truth
  with the graph derived from it (D2-174); land-use rings as the default layout (D2-175).
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

## 7. Where nodes come from: the world or the observer (discussion, 3 Nov)

Zach: "the node being a property of the observer, not the world?" The extreme form: travel can go to any point, and each agent's
node is what lies within a day's reach of where it stands.

**What the node does today:**
- who is together;
- who hears speech to the town;
- who can trade face to face;
- the overview of a place;
- the seat of an institution;
- the scope of incidents and of the capacity check;
- arrive-then-decide;
- the names people know places by.

**What an observer's node would break:**
- **Co-presence:** reaches overlap without being equal, so A can be "here" for B while B is not for A.
- **Speech to the town, and face-to-face offers:** they lose a shared audience.
- **Names:** "Barleyfield" still needs to be one shared place, or people can't agree to meet there, claim there or remember it.
- **The safeguards:** the bounded overview, arrive-then-decide and the checked worlds are built on fixed nodes.

**Proposed middle:**
- **Places are the world's.** The mesh's land is all in places: worked parcels, and wild land as large parcels, everywhere. They are
  joined by links with travel times: about none inside a settlement, days along a road, slower across country.
- **Reach is the observer's.** What one can get to and back from today is computed from where one stands, the links and one's means
  of travel (L-33).
- **A node is a derived label:** a settlement and the places within its day, used for:
  - names;
  - the overview;
  - institutions' seats;
  - the capacity check and incidents.

  It never draws the line of who is present: that is the place (parcel, building).
- **Off the graph, places appear where people go.** The whole land already exists in the mesh, so when someone sets off across
  country in a new direction, the place they reach is derived from the mesh on demand, keyed so it is always the same place. It is
  then an unexplored place made known (D4-47). Nothing is invented and nothing re-drawn.
- **It reduces to today's worlds** while everyone stays on the roads. A hand-made world is the same graph, with links of about
  nothing inside a node and days along an edge.

**The cost:**
- the engine's "same node" rules move to place and reach (L-33's refactor);
- more, larger wild parcels to show.

So: the generator outputs this general form now, with today's nodes derived from it. The engine keeps its node rules until that
refactor is wanted.

## 8. How much physics: only what bottoms out in leverage (discussion, 3 Nov)

Zach: terrain matters for leverage (which land is most useful, where the best resources are), so complexity that does not end in
tangible differences is not worth much.

**What a full erosion and climate simulation would add:**
- dendritic valleys and ridges that look carved;
- floodplains and alluvial fans with deep soil;
- sediment in rivers;
- rain shadows and climate belts that follow the terrain.

**What it would cost:**
- **Time:** hydraulic erosion on a mesh of about 100,000 cells takes seconds to minutes in numpy, once per world, frozen. Time is
  not the problem.
- **Design and tuning:** many parameters, with outcomes hard to steer.
- **Pins:** erosion moves terrain, so a pinned height or river can be worn away, and honouring pins gets much harder.
- **Readability:** the causes of a valley become hard to trace.

**What leverage needs from terrain:**
- the best farmland concentrated and contested (silt-rich valley floors, fens worth draining);
- crossings and passes as chokepoints;
- resources unevenly spread (stone, ore, clay, old wood);
- water reliable in some places and not others (springs, the water table);
- distance trade-offs (near fields against far woods).

**Proposed: cheap approximations** that give all of these and keep pins:
- flow accumulation for rivers;
- one incision pass, cutting valleys in proportion to flow;
- rule-based soils: deep and rich where low and flat beside a large river, thin on slopes;
- one wind sweep for moisture and a rain shadow.

No erosion or climate simulation. And a **leverage check** on every generated world:
- the share of the best land in a few places;
- the chokepoints;
- the spread of each resource;
- which village needs which.

That check, not realism, is the generator's measure of success.

## 6. Prior work to build on

From 37.2's knowledge, not checked against the sources on 3 Nov.

| Generator | What it does | What to take | What to avoid |
|---|---|---|---|
| **Minecraft (1.18+)**, multi-noise | the biome is the nearest match on a few axes (continentalness, erosion, weirdness from which peaks and valleys come, temperature, humidity); every value keyed by coordinates | cover from a few axes; coordinate-keyed draws, so an edit stays local | rivers carved by noise, with no drainage |
| **Red Blob Games, Polygonal Map Generation** (mapgen2, mapgen4) | a mesh of polygons; rivers downhill along its edges; moisture from water; a biome lookup; mapgen4 adds wind and rain shadow, and painted mountains and valleys filled in live | the mesh and hydrology layers; painting as the model for pins | |
| **Azgaar's Fantasy Map Generator** (open source) | mesh, heightmap templates, climate, rivers, biomes, then cultures, states, towns placed by suitability, routes; each layer editable and regenerable alone | a layered pipeline regenerable layer by layer; settlement scoring; routes | its political layers are lore |
| **Dwarf Fortress** | user-set fields (elevation, rainfall, temperature, drainage), erosion, then a simulated history | land first, history second (D4-21's society with a past) | rejecting and regenerating worlds that miss their parameters: a seed search |
| **RimWorld** | biomes by per-biome scoring functions, not hard thresholds | scores let pins tilt a choice smoothly ("short of wood" lowers forest's score) | |
| **Civilization map scripts** | balanced starting positions with guaranteed resources near | targets per settlement enforced by placement, not luck | |

**Methods underneath:**
- **Water:** depression filling (Priority-Flood, Barnes and others), then flow accumulation, as in GIS: rivers reach an outlet, and
  lakes fill hollows.
- **Biome tables:** the Whittaker diagram (temperature against rainfall); Holdridge life zones as a finer alternative.
- **Terrain shape:** layered and domain-warped noise; ridged noise for mountains.
- **Fill-in for discrete layouts:** constraint solvers (answer set programming for content generation, Smith and Mateas) and Wave
  Function Collapse. For fields, pins act as control points the noise blends through.
- **Settlement geography:** von Thünen's land-use rings; Christaller's central place theory (spacing, and which place becomes the
  market); least-cost paths for roads.

## Open questions (for Zach)

1. ~~A mesh kept as ground truth~~: decided (D2-174).
2. A node's parcels covering all its land, with wild land as large parcels split when cleared or claimed (§2d). Zach: to address
   with 3.
3. Places as the world's, reach as the observer's, nodes as a derived label, places appearing where people go off the graph (§7)?
4. Cheap approximations and a leverage check in place of erosion and climate simulation (§8)?
5. ~~Land-use rings as the default~~: decided (D2-175).

## History

- 3 Nov: Zach: start with the generator; worlds highly configurable for land and people, arbitrary specifics filled in around,
  reproducibly, with no seed search; then pins win where physics allows, a vocabulary of descriptions, model-written descriptions
  frozen, land first (D2-173); then: what to explore, given a broader world with nodes as a compression of it. Written.
- 3 Nov: Zach: a mesh as ground truth (D2-174); rings by default (D2-175); add the prior work (§6); is the node the observer's
  or the world's (§7); what would erosion and climate simulation add, given that terrain matters for leverage (§8). Written.

## Sources

[38.04 §2, §5, §6](../../review/38_space_engine/04_places_design.md); spec/world/generation.md (D4-22);
[environment_state.md](environment_state.md) (L-23); [parcel_graph.md](parcel_graph.md); [road_layout.md](road_layout.md);
OPEN L-32 to L-34; D2-70, D2-104 to D2-107, D2-156, D2-161, D4-11.
