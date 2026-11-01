# Proposal: the generator, stage 1 (a spec for review before it is built)

**Status:** fully specced (3 Nov): scope, input and seas (D2-177), the macro layer and large worlds (D2-178), descriptions
(D2-179), checks (D2-180) and numbers (D2-181) decided. Ready to build when Zach asks (README rule 10). Not to be built until Zach asks (README rule 10). **Owner:** 37.2; to be compiled into
spec/world/generation.md (37.4's) once decided. **Rests on:** D2-173 (fill in around what a world file gives), D2-174 (a mesh as
ground truth), D2-175 (rings by default), D4-22, and generator.md §2, §3, §7 and §10.

## Scope

Stage 1 makes a world from a world file with gaps. It writes:
- **the world file in today's format:** nodes, parcels, roads with stretches and landmarks, resources, buildings, households
  placed as now;
- **the mesh beside it:** the ground truth;
- **a report of what was pinned, what was generated and what was checked.**

**Engine changes:** none. People come from today's generate.py, settled at the generated sites.

**Not in stage 1:**
- the tier 1 environment (year severity, soil moisture, floods, river level): stage 2;
- places covering all land, and travel across country (generator.md §6, §8): stage 3;
- pins for people;
- bridges (L-34);
- water as a need, sickness, wildlife, livestock kinds (L-23, Q-16, L-36, L-37).

## 1. Input: the world file with gaps

A world file gains a `generate:` block. Anything else in the file is pinned. Examples:

```yaml
generate:
  seed: 7
  region: {size_km: 30, climate: temperate, coast: none}          # defaults if absent
  settlements: 4                                                   # or a list, below
  features:
    - {range: north, height: [300, 500]}
    - {river: [the hills, Millford, Barleyfield], flow: large}
    - {pass: [Hollins, Wenmoor]}
  places:
    Barleyfield: {terrain: clay vale, short_of: wood, plots: [12, 16]}
    Millford: {on: river, has: [mill site, ford]}
    Ashwood: {terrain: woodland, days_out: 1, wood: plenty}
    Coppergate: {terrain: hills, resources: [copper, stone]}
  targets: {capacity: [0.6, 0.7], food_share: [0.2, 0.3]}
```

**The vocabulary** maps words to ranges and score boosts, kept as data in one table:
- `short of` and `plenty of` a resource;
- `rich` and `poor` soil;
- `on a river`, `by a ford`, `a mill site`;
- `a hill village`, `a forest hamlet`;
- `wet`, `dry`, `sheltered`, `exposed`;
- `n days out` from a named place.

Any word or pin it can't meet is refused, with the reason.

## 1b. The macro layer: the world the region sits in (proposed, 3 Nov)

Zach: sometimes an island, a bay, a mountain range, or a mix; macro features spread across the world, and pinnable. A coarse
layer comes before everything else.

**The world:**
- A coarse mesh over a large area (a continent or more: cells of about 5 to 10 km).
- What each cell carries:
  - land or sea (with a sea level);
  - large-scale height (ranges, uplands, basins);
  - climate gradients (latitude; maritime against continental; the prevailing wind, so wet windward coasts);
  - the main river basins.
- **How it's made, in two ways:**
  1. **Templates** (Azgaar's heightmap templates): parametric shapes (an island, an archipelago, a peninsula, a bay, a range, a
     lake district, a basin, a delta) placed and blended. Controllable.
  2. **Plates** (the Experilous planet generator's method): Voronoi plates with motions, mountains where plates meet. More natural
     placement of ranges, less control.

  Decided: templates and noise (D2-178). Plates are flagged for later, probably deferred indefinitely (OPEN L-39). For what
  we need (a coast, a range, a river system, a climate gradient) they would be overkill.

**The window:** the region played is a window on the macro world. The fine mesh (§2) takes the macro height, upsampled smoothly,
plus fine noise, so a coast or range runs through the window as part of something larger. It's chosen in one of two ways:
- **pinned macro features:** "on a coast to the west", "a bay to the south", "inland in a range", "an island", "a river mouth",
  each placing a template;
- **scanning the macro world:** scan for the window that best fits the pins. This is a deterministic scan of one generated world,
  not a seed search.

**Seas, coasts and lakes** (D2-177):
- sea is land below sea level;
- coasts come from the macro shape plus fine noise;
- lakes come from filled hollows (§3);
- rivers run to the sea or a lake;
- estuaries and deltas form where large rivers meet the sea.

The mesh records navigability (a river's flow and depth, a coast's shelter) for travel by water later (OPEN L-38).

## 1c. Configurable and large

**Every number is a world setting with a default** (D2-177): cell spacing, region size, settlement count and spacing, ring radius,
parcels per node, thresholds.

**Larger worlds:**
- the fine mesh grows with area: 100 km square at 150 m is about 450,000 cells, seconds to a minute in numpy;
- beyond that, the fine mesh is made only where it's needed (the windows played, round settlements and along routes), each part
  keyed by place so it's the same whenever made;
- the macro layer covers the rest coarsely.

So a world can be a continent without building it all in detail.

## 2. The mesh

- **Points:** about 150 m apart, Poisson-disc spaced, from a keyed draw. Each cell is about 2 ha, the land of one plot (a unit of
  size). A 30 km region is about 40,000 cells.
- **Cells:** Voronoi cells, with neighbours from the Delaunay graph.
- **Reproducibility:** every draw is keyed by (seed, layer, cell or feature), so a pin changes only what depends on it.

## 3. The physical layers

1. **Elevation** (metres):
   - layered noise, domain-warped;
   - ridged noise along any range;
   - a coast or lake as a sink;
   - pinned heights and features as control points the noise blends through.
2. **Climate:**
   - **temperature:** a base, less a lapse with height, along a gradient;
   - **moisture:** one sweep along the prevailing wind, raining on windward slopes and leaving a rain shadow beyond.
3. **Water:**
   - **flow:** hollows filled (Priority-Flood), with a lake wherever the fill is deep; flow by steepest descent, accumulated
     downstream and weighted by moisture;
   - **rivers:** wherever flow passes a threshold, with width and depth from flow;
   - **valleys:** one incision pass lowers river cells in proportion to the square root of flow, and the slopes are recomputed;
   - **wetness:** a wetness index from area drained and slope;
   - **springs:** where wetness is high at a break of slope;
   - **pinned rivers** are laid first, and the land is shaped so that they run downhill.
4. **Soil:**
   - **texture** from a geology mask (regions of sand, loam, clay and chalk; pinnable);
   - **depth:** thin on slopes;
   - **fertility** from texture, and from alluvium on the floodplain (low cells by a large river), less where waterlogged;
   - **flood exposure** from height above the nearest river.
5. **Terrain:** each terrain in generator.md §10's catalogue is a score over height, slope, moisture, temperature, wetness, texture,
   flood exposure and distance to the coast. Each cell takes the best score, with ties broken by keyed noise. A pin is a boost, or
   sets the terrain outright.
6. **Natural cover** comes from terrain (§10's covers) before anyone settles: old forest, woodland, heath, grassland, fen, moor,
   saltmarsh, rock.
7. **Resources** per cell:

| Resource | Where |
|---|---|
| timber stocks | by cover (D2-156's magnitudes) |
| stone | on steep, high, chalk or limestone ground and rock |
| ore | by a geology mask in the hills |
| clay | in clay vales and on river banks |
| peat | on wet moor |
| reeds | in fen |
| fish | in rivers and lakes, by flow |
| salt | on saltmarsh |
| game | in forest, less near settlements |

## 4. Settlement

1. **Sites** are scored on:
   - water within a cell (a river or spring);
   - flat fertile land within the ring radius;
   - a river crossing;
   - fuel within reach;
   - safety from floods (terraces score);
   - lying on the line between two terrains.

   Pinned settlements are placed first. The rest are placed greedily by score, at least a day's walk apart unless pinned.
2. **Land use in rings** (D2-175), outward by distance and suitability:
   - built ground (houses);
   - gardens and closes;
   - fields on the best soil within about 2 km;
   - meadow on wet flat land by water;
   - pasture;
   - managed wood (coppice);
   - waste and wild.
3. **Sizes are set by targets** (§7): the plots and woods each settlement needs.

## 5. Deriving today's world

1. **Node territory:** the cells nearer, in travel time, to a settlement than to any other, within a few hours' walk out and back
   (D4-11).
2. **Wild nodes:** a connected wild area with a resource of note (old forest, ore, peat) is given a node at its most reachable
   point, if it is at least about 10 km² and more than half a day from any settlement.
3. **Parcels:**
   - contiguous cells of one land use within a node, merged smallest first into their most similar neighbour, until there are 6 to
     15;
   - each with its size (cells, in units of size), side (bearing from the centre), height class (0 river and wet low ground, 1 the
     floor, 2 slopes, 3 tops), neighbours, cover, resources (sums over cells) and fertility (the mean);
   - each also gets a terrain and soil texture as data. The engine ignores them until stage 2.
4. **Roads:**
   - least-cost paths between settlements over the mesh, costed by slope, cover and water;
   - rivers crossed only at fords: wide, shallow and slow;
   - later roads reuse earlier ones;
   - an edge's length is its travel time in days, with stretches and their terrain from the cells crossed;
   - landmarks where the route crosses a feature: a ford, a pass (a saddle), a narrows (a gorge), a spring near the way, a good
     place (a meadow, fruit trees);
   - hidden ways: the next-cheapest paths through cover between places not joined by a road, and to wild nodes (D2-90, D2-92).
5. **Buildings and households:** generate.py settles founders and grows the society as now, given each settlement's site, built
   ground, fields and woods.

## 6. Descriptions

Each node, parcel, stretch and landmark gets a description written by a model from its facts as JSON:
- terrain;
- cover;
- height and side;
- soil;
- water;
- what lies next to it;
- what a local would say of it.

**How they're kept:**
- written by the current Sonnet model (`describe.model`), at temperature 0: a parcel, stretch or landmark in one sentence (at most
  about 25 words), a node in two or three (D2-179);
- each is cached by the hash of its facts and frozen into the output (D2-173);
- the facts are stored beside the words, so signs and text never disagree;
- re-generating with the same facts reuses the text.

## 7. Targets and checks

**Targets** are met by adjusting what is unpinned, not by searching:
- capacity at 60 to 70% of yearly flows for each settlement (capacity.py, D2-161), through plots and wood sizes;
- a named scarcity ("short of wood");
- food's share of work, in range;
- road lengths in days, where pinned.

**Checks** in two kinds (D2-180):
- **Physics checks refuse** a world that fails them.
- **Design checks warn** unless the world file requires them (`require: [dependence, chokepoint, ...]`), so a null arm such as
  D2-137's dependence null can break them on purpose. By default, access gates and capacity are required.

| Check | Kind |
|---|---|
| every river runs downhill to a lake, the sea or the edge | physics |
| each terrain fits its height, moisture and soil | physics |
| every pin met | physics |
| capacity in range for each settlement | design (required by default) |
| every access gate reachable (scenario_design's dry run, by bots) | design (required by default) |
| no settlement is self-sufficient: each lacks at least one of food, fuel, stone or metal that another has (scenario_design §1) | design |
| each supply chain's links lie in different places, and at least one junction of two chains is worth holding (generator.md §10) | design |
| at least one chokepoint (a ford, a pass, a narrows) on the roads between settlements | design |
| 6 to 15 parcels per node | design |

## 8. Output

- **`<world>.yaml`:** today's format, complete.
- **`<world>.mesh.parquet`:** the cells, with every layer's values and the place and parcel each belongs to.
- **`<world>.generation.json`:** the input, seed, code version, each pin and how it was met, each target and its result, the
  checks, and the description cache keys.

The run journal freezes the yaml as now. The mesh travels with it for the visualiser, and for stage 2.

## 9. Tests

| Test |
|---|
| the same file and seed give byte-identical output |
| changing one settlement's wood pin changes that settlement's woods and its capacity, and nothing else outside what depends on it |
| a pinned river through three named places runs through them, downhill |
| a pin the physics can't meet (a river uphill, a coast inland) is refused with the reason |
| a clay vale's parcels carry heavy soil; a floodplain's fields carry high fertility and height class 0 |
| "short of wood" gives that settlement the region's lowest wood flow per head |
| every check in §7 has a failing example that it catches |
| a 30 km region of 4 settlements generates in under a minute, descriptions cached |
| the output runs in today's engine unchanged |

## Numbers (D2-181; all world settings)

| Number | Default |
|---|---|
| cell spacing | about 150 m (about 2 ha, a unit of size) |
| region | about 70 km square, 4 settlements, temperate; a coast only where the macro layer or a pin puts one |
| a road day | about 25 to 30 km on a road, slower across country by terrain |
| settlement spacing | at least a day's walk, unless pinned |
| a settlement's land | sized by its capacity target (D2-161), in rings outward; the rest is wild |
| a wild node | at least about 10 km², more than half a day from a settlement |
| parcels per node | 6 to 15 |
| macro cells | about 5 to 10 km |
| river, incision, wetness and spring thresholds | by trial on a few seeds, then fixed |

## 10. Checked against the earlier designs (3 Nov)

| Number | The earlier reasoning | Holds? |
|---|---|---|
| cells of about 2 ha | a unit of size is about 2 ha, the land of one plot of 16 seed (02z; D4-40, D2-59) | yes: one cell is one unit of size |
| villages a day or more apart | travel binds trade between villages, so they need each other (scenario_design §1; D4-9; 02t: roads of 1 to 3 days, a forest a day out) | yes |
| a region of 30 km (first proposed) | 02t's region has roads of up to 3 days (Coppergate to Ashwood) | **no:** 3 days is about 75 to 90 km, so the default is now about 70 km |
| fields within about 2 km (first proposed) | the seeded villages hold about 25 to 30 units of size in all (Barleyfield: 28, about 56 ha, for about 16 people), and capacity is set at 60 to 70% of flows (D2-161) | **no:** 2 km round a village is about 1,250 ha. With no cost to distance inside a node, all of it would count, and food and fuel would stop binding. So a settlement's land is sized by its target, and the rest is wild |
| wild nodes of at least 10 km², more than half a day out | 02t's Ashwood forest a day out; camps (D2-68) | yes |
| 6 to 15 parcels per node | Barleyfield has 12; the overview must stay readable (D2-116) | yes |
| node = there and back before nightfall (D4-11) | a maximum for routine places, not a territory | yes, read as a maximum |

**What this shows.** The earlier designs describe a sparse world:
- small villages, each farming tens of hectares;
- a day or more of wild land between them.

That is far sparser than a medieval countryside, where villages stood 2 to 5 km apart. The sparseness is what makes travel bind and
villages need each other.

**A realistic-density world** would put several villages within one node's day. Trade between them would then be free, unless
distance inside a node had a cost (OPEN L-35). So realistic density is a later option that waits on L-35, not a default.

## Open questions (for Zach)

1. ~~Scope~~ and 2. ~~input~~: decided (D2-177).
3. ~~The numbers~~ (D2-181, with the two changes in §10) and 4. ~~the checks~~ (D2-180): decided.
5. ~~Descriptions~~ (D2-179), 6. ~~the macro layer~~ and 7. ~~large worlds~~ (D2-178): decided.

## Sources

[generator.md](generator.md) §2, §3, §6, §7, §10; spec/world/generation.md (D4-22), parcel_graph.md (D2-114), roads.md (D2-104 to
D2-107), holding.md; cybertron2/engine/capacity.py, generate.py; docs/scenario_design.md; D2-90, D2-92, D2-156, D2-161,
D2-173 to D2-175.
