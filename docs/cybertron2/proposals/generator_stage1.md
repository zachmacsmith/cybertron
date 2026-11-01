# Proposal: the generator, stage 1 (a spec for review before it is built)

**Status:** fully specced (3 Nov): scope, input and seas (D2-177), the macro layer and large worlds (D2-178), descriptions
(D2-179), checks (D2-180) and numbers (D2-181) decided. Builder's tables in §11 (D2-183 to D2-187). Ready to build when Zach asks (README rule 10). Not to be built until Zach asks (README rule 10). **Owner:** 37.2; to be compiled into
spec/world/generation.md (37.4's) once decided. **Rests on:** D2-173 (fill in around what a world file gives), D2-174 (a mesh as
ground truth), D2-175 (rings by default), D4-22, and generator.md §2, §3, §7 and §10.

## Scope

Stage 1 makes a world from a world file with gaps. It writes:
- **the world file in today's format:** nodes, parcels, roads with stretches and landmarks, resources, buildings, households
  placed as now;
- **the mesh beside it:** the ground truth;
- **a report of what was pinned, what was generated and what was checked.**

**Engine changes:** data only (four new covers, D2-185). People come from generate.py, extended to several nodes and settled at the
generated sites (§11e).

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
  size). A 50 km region is about 110,000 cells; fine detail is made only where needed (§1c).
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
   - fields on the best soil nearest the village, as many as the target needs (§7, D2-181);
   - meadow on wet flat land by water;
   - pasture;
   - managed wood (coppice);
   - waste and wild.
3. **Sizes are set by targets** (§7): the plots and woods each settlement needs.

## 5. Deriving today's world

1. **Node territory:** the settlement's land from the rings (§4), sized by its capacity target (D2-181), together with any land
   pinned to it. Wild land beyond it is not part of the node: it lies in wild nodes or in road stretches, at a day's remove (D4-11
   is read as a maximum).
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
   - roads join neighbouring places only, each about a day long (D2-182); a route between places further apart passes through
     those between;
   - where a day's road would cross wild land with no settlement, a stopping place is put on it: a hamlet where the site allows,
     else a wild stop at a spring, a ford or a meadow (proposed); a two-day road only where the land gives nowhere to stop;
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
| a 50 km region of 4 settlements generates in a few minutes at most, descriptions cached |
| no road is longer than two days, and fewer than one road in five is two days |
| the output runs in today's engine unchanged |

## Numbers (D2-181; all world settings)

| Number | Default |
|---|---|
| cell spacing | about 150 m (about 2 ha, a unit of size) |
| region | about 50 km square, 4 settlements, temperate; a coast only where the macro layer or a pin puts one (D2-182) |
| a road day | about 25 to 30 km on a road, slower across country by terrain |
| settlement spacing | about a day's walk, unless pinned |
| road length | about one day; two days rare (a moor, a pass); longer journeys pass through places on the way (D2-182) |
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
| a region of 30 km (first proposed) | 02t's longest route is 3 days, but through Millford: its roads are 1 to 2 days | **adjusted (D2-182):** roads mostly a day, longer routes through places on the way; about 50 km for 4 settlements |
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

## 11. Tables for the builder (3 Nov)

Every value here is data and marked calibrate. First values are to be tuned by trial on a few seeds, then fixed. Where a magnitude
already exists in the engine or the hand-made worlds, the generator takes it from there rather than inventing it.

### 11a. Terrain scores

**Inputs per cell:**
- h: height in metres;
- s: slope in degrees;
- m: moisture, 0 to 1;
- w: wetness, 0 to 1;
- tex: soil texture (sand, loam, clay, chalk);
- f: height above the nearest large river, in metres;
- c: distance to the sea, in km;
- d: distance from the nearest settlement, in km (after siting).

Each terrain scores 1 for each of its conditions met and loses for each missed, weighted. The best score wins, and a pin adds or
sets.

| Terrain | Conditions (first values) |
|---|---|
| river floodplain | f < 2; beside a river of large flow; s < 2 |
| river terrace | 2 ≤ f < 8; within 1.5 km of a river; s < 4; tex loam or sand |
| clay vale | tex clay; h < 150; s < 5; m ≥ 0.4 |
| lowland loam | tex loam; h < 200; s < 6 |
| sandy heath | tex sand; m < 0.45 |
| chalk or limestone down | tex chalk; 80 ≤ h ≤ 300; 3 ≤ s ≤ 15 |
| woodland | m ≥ 0.5; s < 15; w < 0.7 |
| deep forest | woodland's conditions, and d > 15 (decided after siting) |
| hills | 250 ≤ h ≤ 600, or s ≥ 10 |
| upland summer pasture | h ≥ 450; s < 15 |
| moor | h ≥ 300; m ≥ 0.6; w ≥ 0.6 |
| fen | h < 50; w ≥ 0.8; s < 1 |
| coast | c < 1; h < 20 |
| saltmarsh | c < 2; h < 3; w ≥ 0.7 |
| rock | s ≥ 30 |

Passes and gorges aren't cell terrains. They're found on routes (11f).

### 11b. Terrain and land use to the engine's covers and resources

**Covers.** The engine's eight covers, plus heath, moor, fen and saltmarsh as data (D2-185). The land use from the rings (§4)
chooses the cover, and the terrain limits which are possible:

| Land use | Cover | Terrains it may sit on |
|---|---|---|
| built ground | built | terrace, loam, vale, down, coast (scrub where cleared) |
| fields | field | floodplain, terrace, vale, loam; poor on heath, down and hills |
| meadow | meadow | floodplain; the edges of fen |
| pasture | pasture | any not waterlogged; downs, hills, upland (summer) |
| managed wood, copse | forest (`managed wood`, `copse`) | woodland, near the settlement |
| wild wood | forest (`old forest`) | woodland, deep forest |
| waste | scrub, heath, moor, fen, saltmarsh, rock | by terrain |
| water | water | rivers, lakes, the sea |

**Resources:**
- **Magnitudes** per unit of size come from the engine's tables (data.FORESTS for wood; RESOURCES' regimes) and from the averages,
  by cover and kind, of the hand-made worlds (hollins2, region_c, wide). The builder computes these once into a reference table.
- **Plants, game and grass:** {K, S, r} per parcel, as those worlds have them.
- **Stone:** `quarry` (endless) on rock, downs and hills.
- **Ore:** `seam` (finite) on hills, within the geology mask's ore belts, at region_c's Coppergate seam size.
- **The new covers in stage 1:** low plants and grass only. Peat, reeds and salt come in stage 2.

### 11c. The vocabulary

| Word | What it does |
|---|---|
| `plenty of`, `short of` *wood / food / stone / grazing / water* | the settlement's share of that flow: the region's top quarter, or its bottom quarter |
| `rich`, `poor` *soil* | fertility at about 1.2 to 1.4, or 0.6 to 0.8 |
| `wet`, `dry` | moisture and wetness raised or lowered for the settlement's land |
| `sheltered`, `exposed` | a site in a hollow, or on open high ground |
| `on a river`, `by a ford`, `a mill site` | the site placed on a river; a ford on its road; a river with a drop within its land |
| `by the sea`, `on an island`, `in the hills` | a macro template (11d) placed to make it so |
| `a hill village`, `a forest hamlet`, `a fen village` | the settlement's terrain set |
| `at a crossroads`, `remote` | the most roads meet there; at least two days from the others |
| `n days out` *from a place* | road length to it |
| `land-pressed`, `land-rich` | its capacity target at 0.8 to 0.9, or 0.4 to 0.5 (D2-16) |

### 11d. Macro templates (D2-178)

| Template | Parameters | Shape |
|---|---|---|
| coast | side, how jagged | sea beyond a line |
| island, archipelago | size, count | land blobs in sea |
| peninsula | side, width | land with sea on three sides |
| bay | side, depth | sea cut into a coast |
| range | line, height, width | a ridge; passes at its low points |
| upland | area, height | a plateau |
| basin | area, depth | low land ringed by higher |
| lake district | area, number of lakes | many hollows that fill |
| river mouth or delta | river, coast | a large river reaching the sea, with a low wet fan |
| plain | area | low and gentle |

**How they combine:**
- templates blend by taking the highest of the shapes, plus noise;
- every parameter has a default, and any can be pinned.

### 11e. People and things (D2-184)

- **Population:** each settlement's people follow its capacity target (§7). Households are about 4 to 6 people.
- **Settling:** generate.py settles founders and grows the tree. Stage 1 extends it from one node to several, with marriages and kin
  between neighbouring villages (D4-21: one tree for the whole population).
- **Houses:**
  - a house for each household, with a bed for each member (D4-86) and the free floor of D4-85;
  - a hearth and bins;
  - other fittings by trade.
- **Stores and crops** as in the hand-made worlds (D2-13): last year's grain and seed, fuel, crops in the ground for the season.
- **Herds:** as pasture and hay can carry (D4-45), with oxen where the soil is heavy.
- **Claims:** fields in plot shares to households (D2-163); the common pasture to the village, or held by none.
- **Trades where their resources are:**
  - a smith within a day of a seam, with an anvil;
  - a mason by a quarry;
  - a carpenter by managed wood;
  - a trapper by forest;
  - a miller at a mill site.

### 11f. Roads in detail (D2-182)

- **Pace by cover** (km an hour):

| Cover | Pace |
|---|---|
| road | 4 |
| field, built | 3.5 |
| pasture, heath, down | 3 |
| woodland | 2 |
| moor, fen, saltmarsh | 1.5 |

  Slope multiplies the time by (1 + s / 10).
- **A road day** is 8 hours of walking. An edge's days are its hours / 8, rounded, at least 1.
- **Rivers** are crossed only at a ford: a reach no wider than about 30 m and no deeper than about 1 m, from its flow.
- **An edge's terrain** (data.TERRAIN) comes from the cells most crossed:
  - farmland, woodland or plain;
  - marsh for fen, moor and saltmarsh;
  - hills where the slope is steep;
  - mountain at h ≥ 600;
  - river valley along a river.
- **Landmarks** (data.LANDMARKS):

| Landmark | Where it's found |
|---|---|
| ford | where a road crosses a river (as above) |
| pass | the highest point of a road over a ridge, with land at least 100 m lower on both sides |
| narrows | slopes of at least 20° on both sides within 200 m |
| spring | a spring cell within 300 m of the road |
| meadow, fruit trees | a good place near mid-day on the road |
| hollow | a sheltered low point |

- **Hidden ways:**
  - between neighbouring places with no road, a path is made when it is no more than 1.2 times a road's time and at least half
    under cover;
  - wild nodes get one or two each.

### 11g. Names (D2-186)

**Settlements and landmarks** take a first part and an ending from lists in data, chosen by their facts:
- **endings by site:**
  - -ford (a ford), -ley (a woodland clearing), -den (a valley pasture), -mere (a lake), -wick (a dairy farm);
  - -ton or -ham (a settlement), -by, -hope (a hidden valley), -combe (a short valley), -holt (a wood);
- **first parts by the land:** Ash-, Oak-, Birch-, Stan- (stone), Mar- (mere), Brook-, Holl- (hollow), Fen-, Hay-, Mill-, Salt-,
  Cold-, Wether- (sheep).

**Parcels** take patterns by cover, shape, side and feature:
- the Long Field, North Field, Brook Meadow;
- the Common, the Hanger (a wood on a steep slope);
- the Moss (a moor), Holloway.

**Landmarks** are named from their place: "the Ford at X", "X Pass".

**The rules:**
- names are chosen by keyed draws;
- no name repeats within a world;
- the style is a world setting.

### 11h. What each settlement knows at the start (D2-187)

- road neighbours, fully;
- villages two roads away, by name and a line;
- stopping places on roads;
- wild nodes off the roads, unexplored (D4-47), except to the households whose trade uses them (a hunter its hunting ground, a
  woodcutter its wood);
- hidden ways, known to one or two of those who would use them.

### 11i. How the checks are computed (D2-180)

| Check | Computed as |
|---|---|
| dependence | for each settlement, each of food, fuel, stone and metal: its own land's supply against its need; it must lack at least one that another settlement within two roads has in surplus |
| supply chains | for each chain (grain, mill, bread; timber, charcoal, ore, smith; stone, building; salt, keeping food), the nodes holding its links are not all one node |
| a junction worth holding | a node or landmark on the cheapest routes of at least two chains' goods, between their suppliers and their users |
| chokepoint | a landmark or node whose loss cuts the roads between two settlements, or lengthens the route by a day or more |
| capacity | capacity.py for each node, at 60 to 70% of its scarcest flow |
| access gates | the bot dry run of scenario_design |
| parcels per node | 6 to 15 |

### 11j. The base file

A generated world extends a chosen base world file (as specs can already: `extends`) for the calendar, lifespan, children setting
and the rest. The generator writes only places, roads, resources, buildings and people.

## Open questions (for Zach)

1. ~~Scope~~ and 2. ~~input~~: decided (D2-177).
3. ~~The numbers~~ (D2-181, with the two changes in §10) and 4. ~~the checks~~ (D2-180): decided.
5. ~~Descriptions~~ (D2-179), 6. ~~the macro layer~~ and 7. ~~large worlds~~ (D2-178): decided.

## Sources

[generator.md](generator.md) §2, §3, §6, §7, §10; spec/world/generation.md (D4-22), parcel_graph.md (D2-114), roads.md (D2-104 to
D2-107), holding.md; cybertron2/engine/capacity.py, generate.py; docs/scenario_design.md; D2-90, D2-92, D2-156, D2-161,
D2-173 to D2-175.
