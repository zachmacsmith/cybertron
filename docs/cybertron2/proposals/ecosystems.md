# Proposal: environments, ecosystems and how they cluster

**Status:** discussion; the wide design, kept for later. Its narrowed part is decided and built as
[temperate_landscapes.md](temperate_landscapes.md) (D2-191, 2 Nov): layers 2 to 4 (base environment, ecosystem, state by how long
settled) and depth bands, within one temperate envelope and with no planet (landgen/ecology.py, physical.py, macro.py, vocab.py);
§8 step 1 is done and step 2 begun (a wood's game by its type and depth, its forage by depth: landgen/write.py). §1 describes the
generator before D2-191. Still open: 3 questions (Q3, Q4 in part, Q1's climate zone beyond the envelope); Q2 settled for the
envelope, Q5 deferred by D2-191.
**Owner:** 37.2.

What the generator does now is narrowed to one envelope in [temperate_landscapes.md](temperate_landscapes.md) (Zach, 2 Nov: "design
within certain environmental types"). (Zach, 2 Nov: "what are all the different core environmental / terrain types we might want to
explore ... biomes should come in ecosystem clusters, no? What would be a good way to do this?"). ~~Nothing decided, nothing to
build.~~ (The narrowed part: D2-191.) Current as of 2 Nov. Owner 37.2. It extends generator.md §7 (only physics that ends in
leverage) and §10 (the temperate terrain catalogue).

## 1. The problem with what exists

Today one **terrain** per cell mixes three things. Each terrain is chosen by scoring a cell's conditions (vocab.TERRAINS) and maps
to one engine cover:

| Thing mixed in | Terrains |
| --- | --- |
| landform and soil | clay vale, chalk down, river terrace |
| vegetation | woodland, heath, moor |
| distance from people | deep forest |

The consequences:
- **There is no ecosystem layer.** Every forest is the same forest, every heath the same heath, and game and plants are one generic
  stock each.
- **Climate does nothing.** Temperature is computed and used by nothing; moisture only nudges a few scores.
- **The palette is fixed.** Every world is lowland England, which is why worlds can only differ in arrangement, not in kind.

## 2. Four layers instead of one

| Layer | Scale | What it is | Set by |
| --- | --- | --- | --- |
| 1. **Climate zone** | the region (macro) | temperature, rainfall, seasonality (how wet and dry, hot and cold the seasons are), variability from year to year | the world file or the macro layer: a zone, or a latitude and a distance from the sea |
| 2. **Base environment** | cells | landform (floodplain, terrace, vale, plain, down, hills, upland, coast, cliff), substrate (sand, loam, clay, chalk, peat, rock, volcanic), water regime (dry, moist, waterlogged, seasonal flood, tidal) | the physical layers, mostly as now |
| 3. **Ecosystem** | patches | the living community: its structure (open, scrub, wood), its dominant plants, its resources, its wildlife, its hazards | the climate zone's **palette**, placed along **gradients** by catena and zonation templates (§4) |
| 4. **State** | parcels | where the patch is in its succession and how people use it: old growth, coppiced, wood-pasture, cut over, grazed short, burnt, drained | disturbance and history; the engine's four forest kinds already are this layer |

**Depth** belongs to a patch's geometry, not to a terrain: how far inside a block of one ecosystem a place is. See §6.

## 3. Why ecosystems cluster, and the ways to generate that

Ecosystems co-occur because they sit on shared gradients: water, height, salt, exposure, soil depth, time since disturbance. Ecology
names the recurring patterns:

| Pattern | What it is | Example |
| --- | --- | --- |
| **catena** (toposequence) | soils and plants changing down one slope | dry heath on the crest, oak on the slope, farmed terrace, wet meadow, alder carr by the river |
| **zonation** | bands along one strong gradient | coast: shingle, dune, dune slack, saltmarsh, mudflat. Mountain: valley farms, forest, the treeline, alpine pasture, scree, snow |
| **hydrosere** | water filling in over time | open water, reedbed, fen, carr, wet woodland |
| **mosaic** | patches of different ages after disturbance | heath burnt in rotation; windthrow gaps; old fields going back to scrub |
| **ecotone** | the edge between two systems, often the richest place | wood edge, river bank, the spring line at the foot of a down |

Four ways to generate this:

| Method | Gives | Fails at |
| --- | --- | --- |
| A. Score each cell independently (today) | smooth fields give some grouping | sharp, structured clusters; climate-driven variety; everything scores against the same fixed list |
| B. A biome lookup from temperature and rainfall (Whittaker, Holdridge) | a believable biome for the region | anything local: one biome everywhere |
| C. **A palette per climate zone, placed along gradients by templates, then disturbance and succession** | biomes from climate; clusters from catenas and zonation; mosaics from history | needs tables written by hand (the palettes, the templates), which is data work, not code |
| D. Simulate vegetation (cellular automata, dispersal, competition) | emergent realism | slow to tune, hard to steer, breaks pins, and fails generator.md §7's test |

**Recommended: C.** It keeps the generator's pattern of rules as data, honours pins (a pinned ecosystem fixes a template's position),
and every table row can be read and argued with.

1. **The palette.** The climate zone gives a palette: the ecosystems that can exist there, each with the conditions it wants.
2. **The templates.** Each template is a sequence along a gradient: a valley catena, a coastal zonation, a mountain's belts, a
   hydrosere around lakes, a wadi in dry land. The generator lays the template that fits each landform, so neighbours are
   ecologically consistent rather than independently scored.
3. **Disturbance and succession.** These then age patches into a mosaic: fire on heath and dry pine, floods on floodplains, windthrow
   in old forest, grazing near villages, cutting near settlements. Each ecosystem has a succession graph (bare, grass, scrub, young
   wood, old wood) that the engine's forest growth and scrub rule already half implement.

## 4. Base environments to explore: the palette by climate zone

Each zone is worth having only for the behaviour its constraint produces. The last column is what the engine would need for that
constraint to bind; without it, the zone is scenery.

| Climate zone | Ecosystem palette | The binding constraint | Behaviour it should produce | Engine needs |
| --- | --- | --- | --- | --- |
| **Temperate lowland** (today) | oak-ash and beech wood, alder carr, meadow, heath, fen, chalk grassland, saltmarsh | land, labour, winter fuel | mixed farming, commons, fuel management | exists |
| **Temperate upland** | sessile oak and birch, pine, moor, blanket bog, summer pasture | a short season; winter | transhumance; peat fuel; herders' commons | moving herds with the seasons (L-36); peat (D2-185) |
| **Mediterranean** (dry summer, wet winter) | evergreen oak, maquis and garrigue scrub, pine, terraces, olive and vine | summer water; fire season | storage; terracing as collective, lasting capital; long-term crops (an olive takes years); fire risk shared | water as a need (L-23); tree crops; fire (environment_catalogue) |
| **Steppe and semi-desert** | grass steppe, salt flats, river forest strips, oases | water and grazing | the classic farmer and nomad dependence; wells and oases as chokepoints; raiding and protection; caravans | water as a need; herds that move; transport (L-53) |
| **Hot desert with oases and wadis** | oasis palm groves, wadi scrub, bare desert | water, extremely | wells held by a few; water rights as law; trade or die | water as a need; wells; heat |
| **Great river floodplain** (an annual flood) | flood-recession fields, levee woods, reed marsh, desert beyond | the flood's height; canal upkeep | irrigation works needing many hands; managing the canals as an institution; a bad flood year as a shared shock | the flood scheduler (stage 2); canals as works (L-34's kind) |
| **Boreal** (long winter) | spruce, pine and birch forest, bog, lakes | winter food and fuel | storage above all; hunting and trapping; furs traded south; frozen rivers and lakes as winter roads | seasonal edges (a road that exists only in winter); snow |
| **High mountain** | belts: valley fields, montane forest, treeline, alpine meadow, scree | passes closed by snow; little flat land | isolated valleys; a pass as a seasonal chokepoint; avalanches; summer-only pasture | seasonal edges; hazards on roads |
| **Tropical forest** | rainforest, swamp forest, rivers | poor soils; disease | swidden: fields that move every few years, so land tenure means something else; rivers as roads | fields that wear out and regrow (D4-39 partly); boats (L-38); sickness (Q-16) |
| **Savanna and monsoon** | grassland with scattered trees, gallery forest, seasonal wetlands | whether the rains come | herds against crops; years of drought and plenty; pooling risk, credit, granaries | year severity (stage 2); herds that move |
| **Wetland and delta** | reedbed, fen, carr, channels, islands | dry ground; boats | the marsh people: fish, fowl, reeds; draining as a project; a people the drained land would displace | boats; draining as works |
| **Archipelago and coast** | island woods, dunes, saltmarsh, rocky shore, the sea | land; the sea | boats as capital; fishing; island autarky against trade; who holds the harbour | boats (L-38); tides |
| **Karst and volcanic** (overlays on others) | limestone pavement, sinkholes, caves; rich volcanic soils | hidden water; rare catastrophe | springs held by a few; caves as refuge; a rare eruption remembered or forgotten | water as a need; rare events in the scheduler |

## 4b. Where the climate zone comes from: large-scale position (Zach, 2 Nov)

Zach: "usually this depends on large scale climate, like latitude, deserts, mangroves, tropical coasts". That is right: the zone is
set by where the region sits on the planet, not by local conditions. The drivers, in order of strength:

| Driver | Effect | Examples |
| --- | --- | --- |
| **latitude** | sets warmth and, through the global circulation, the rain belts: wet near the equator, dry near 30°, wet westerlies at 40 to 60°, cold beyond | rainforest at the equator; the great deserts near 30°; temperate wet coasts; boreal forest at 50 to 65° |
| **distance from the sea** (continentality) | inland: hotter summers, colder winters, drier | steppe deep in continents; mild oceanic coasts |
| **prevailing wind and mountains** | wet on the windward side, a rain shadow behind | a wet western coast with a dry basin beyond its range |
| **ocean currents** | warm currents make coasts wet and mild; cold currents make coastal deserts | a mild, wet north-western coast; deserts on west coasts beside cold currents |
| **elevation** | about 6 °C cooler a km up, so zones repeat as belts up a mountain | an alpine belt above a temperate valley; cool highlands in the tropics |

**Coasts follow the zone too:**
- temperate coasts have saltmarsh, dunes and shingle;
- tropical coasts have mangroves, coral reefs and lagoons;
- desert coasts have bare shores and salt pans;
- cold coasts have rock, ice and kelp.

So each zone's palette includes its own coastal template, not a shared one.

**What the generator has, and what it would take.** The macro layer already composes the land around the window (D2-178), the
physical layers sweep one prevailing wind for moisture and a rain shadow, and temperature falls with height and slightly toward the
north. To make the zone follow position:
- a world gives a **latitude** (or a zone by name), and the macro layer says how far the window is from the open sea and which way
  the wind and any current run;
- from these come the window's temperature, rainfall, seasonality and variability, and so its zone and palette;
- within the window, height and the rain shadow still vary it: mountain belts, a dry basin behind a range.

**One limit.** A 50 km window sits inside one zone; only mountains add belts within it. A world that spans zones (desert to forest,
coast to steppe) needs continent-scale worlds: the macro window scanned across a larger generated land, with places that cover all
land (stage 3) and perhaps plates (L-39). Until then a world is one zone with its local belts, which is enough for every contrast in
§4.

## 4c. A coarse planet, and a detailed window where the society lives (Zach, 2 Nov)

Zach: "How hard would it be to generate a planet coarsely, and then some small selection of it in detail where I place the actual
society". It is a well-trodden pattern (Azgaar's map generator, Experilous's planet generator, WorldEngine). The estimate is two to
three weeks of build for a decent version, almost all of it design and tuning; the computing is trivial.

| Part | How | Size |
| --- | --- | --- |
| a sphere mesh | an icosahedron subdivided about 6 times: about 40,000 cells of about 100 km; pure numpy (scipy is not installed) | S |
| continents and relief | noise-shaped continents first; plates later, if ever (L-39) | S (M with plates) |
| climate | temperature from latitude and height; wind in latitude bands (trade winds, westerlies, polar easterlies); moisture carried from the oceans along the wind, dropped on windward slopes, with rain shadows; currents by rule (warm along continents' east coasts, cold along west coasts in the subtropics) | M |
| zones | each cell classified from temperature, rainfall and seasonality (Köppen) | S |
| rivers | flow accumulation on the sphere | S |
| **the handoff to the window** | pick a place; turn the coarse cells around it into what the window generator already takes (§ below) | M, and the hard part |

**The handoff.** The coarse cells around the chosen place become the window's inputs:
- its latitude and temperature;
- its wind direction and moisture;
- which side the coast is on;
- where ranges cross;
- where large rivers enter, and how big they are;
- its climate zone.

The cleanest form is primitives (coast, ridge, river, with their anchors), which `macro.py` already composes, so the window
generator stays as it is and pins keep working. The alternative, upscaling the coarse heights with added noise, makes it hard to keep
a river entering where the planet says.

**What it would buy:**
- **The climate stops being an authoring choice.** A world can say "a river valley near 35° on a west coast", or the planet can be
  searched for a place that matches.
- **There is something beyond the map's edge** for the frontier, migration and long-distance trade (05_frontier).
- **Later:** several societies on one planet, and continent-scale worlds (stage 3).

**What it does not buy on its own.** Agents feel a planet only through:
- the window's zone, which means nothing without the ecosystem palettes (§4, §6);
- the engine systems that make the zone's constraint bind (§4's last column).

A zone chosen by name, with the existing macro layer, gives nearly the same window for a fraction of the work. So the planet comes
after the ecosystem layer and the first non-temperate engine system, not before.

**Status:** possible later. Recommended deferred until at least one zone beyond temperate has its engine system (§9).

## 5. Extremes, as axes

It may be cleaner to explore by axis than by named biome. Each axis is a dial a world can turn, and each extreme pushes a different
behaviour:

| Axis | Low extreme | High extreme | What the extreme tests |
| --- | --- | --- | --- |
| Scarcity of one input (water, fuel, flat land, salt) | | one input held in very few places | monopoly, rent, raiding, law over a resource |
| Seasonality | an even year | most of the year unproductive | storage, planning, migration, credit across the year |
| Variability between years | the same every year | boom and bust | insurance, granaries, kinship, hoarding |
| Rare catastrophe | none | a flood or eruption once a generation | memory, records, elders, whether lessons survive |
| Isolation | open plains | islands, closed valleys | autarky against trade; divergent customs |
| Abundance | bare subsistence | a rich surplus | specialisation, status, display, the first towns |
| Disturbance | stable | frequent fire or flood | mobility, shared risk, rebuilding |

A world could be described as a zone plus a few dial settings, for example temperate lowland with high variability and one scarce
input.

## 6. Ecosystems as data, and depth

One row per ecosystem: the forest table (and every other table) the engine would read. **Fields:**
- **structure** (open, scrub, wood) and **dominant plants**, as a short phrase for descriptions;
- **resources per unit:**
  - timber (and its quality: oak for building, pine for masts, beech poor outdoors);
  - firewood;
  - coppice (hazel and ash coppice well; beech and pine barely);
  - mast for pigs (acorns, beech mast);
  - forage plants;
  - grazing;
  - fish and fowl;
  - reeds, peat, salt;
- **wildlife guilds** (§7) and their densities;
- **hazards:** fire, flood, windthrow, disease;
- **travel:** the pace through it, how hidden it keeps a traveller, sight;
- **succession:** what it becomes if left, and what cutting, grazing, burning or draining turn it into;
- **depth profile:** how its properties change from edge to core.

**Depth:** for each patch of one ecosystem, the distance inward from its edge (or the hours from the nearest settlement, whichever is
less), banded edge, interior and core. The depth profile then scales the row's values by band. For a typical wood:
- the core has more old timber, bigger game, slower travel, less light and so fewer greens;
- the edge has more forage, more small game, and is easier to work.

Each type has its own profile:
- a pine wood's core is open and walkable;
- a rainforest's interior is dark and poor in forage;
- a fen's core is impassable without a boat.

"Deep forest" becomes the core band of any large wood, so a village can sit at the edge of one.

**Example rows, temperate lowland palette:**

| Ecosystem | Where (in the valley catena) | Character | Resources that differ |
| --- | --- | --- | --- |
| oak-ash wood | slopes and loam | the ordinary wood | good building timber, coppice, acorns, deer |
| beech hanger | chalk scarps | shady, little underwood | poor coppice, beech mast, little forage |
| alder and willow carr | wet floodplain, lake edges | wet, hard going | poles, little timber, wildfowl, fish nearby |
| birch and pine heath wood | sand, acid uplands | open, fire-prone | poor timber, resin, little game |
| wood-pasture | near villages | grazed wood with old trees | grazing and pannage together, few young trees |

## 7. Wildlife by guild, not species

Hunting, pests and danger come from guilds. The ecosystem row gives densities, and the depth band scales them:
- large browsers: deer, elk;
- rooters: boar;
- small game: hare, rabbit;
- wildfowl;
- fish;
- predators: wolf, bear, big cats;
- pests: rats, birds on crops, locusts in dry zones.

This is OPEN L-37's design.

## 8. What would change, and when

| Step | What | Size | When |
| --- | --- | --- | --- |
| 1 | Split terrain into base environment and ecosystem, still temperate, with depth bands. The generator writes ecosystem and depth as data the engine ignores for now (as soil type is today). Catena templates replace independent scoring. | M (generator, data) | could go with the G-34 fix |
| 2 | Engine reads the ecosystem: the forest table by type × state; mast; game by guild; depth effects | M-L (engine) | with L-37, or stage 2 |
| 3 | Climate zones beyond temperate, each with its palette and templates | S each in data, but each needs its engine constraint (§4's last column) | one at a time, when its system exists |

## 9. A critical note

The risk is building scenery. generator.md §7's test applies: a biome is worth having only if it changes who needs whom.
- **Most of the extreme zones need one engine system each** before they mean anything: water as a need, seasonal edges, boats,
  moving herds, a flood scheduler.
- **The generator can describe a desert today, but nothing in the engine would make water scarce.**

The order to explore zones should therefore follow the engine systems, not the other way round. The cheapest high-value contrasts:
1. **Temperate upland:** needs moving herds and peat.
2. **Great river floodplain:** needs the stage 2 flood scheduler, which is planned anyway.
3. **Steppe with oases:** needs water as a need, and it pairs with the transport work (L-53).

## Open questions (for Zach)

1. The four layers (climate zone, base environment, ecosystem, state) with depth: is that the right split? And the zone set by
   latitude, distance from the sea, wind and currents (§4b), with a zone by name as a shortcut? — the split and depth: decided and
   built for the envelope (D2-191; landgen/ecology.py: base environment as terrain, 20 ecosystems, clearing by `settled`, edge,
   interior and core); **still open:** the climate zone and how it is set, as D2-191 fixes one zone (temperate_landscapes.md §2)
2. Method C (palettes, templates, succession), or another? — decided for the envelope (D2-191): palettes per landscape system,
   built as rules by conditions rather than explicit template sequences (temperate_landscapes.md §5); explicit catenas only if the
   rules stop sufficing (OPEN L-100); disturbance and succession into a mosaic not built beyond the engine's forest growth and scrub
3. Which zones to explore first, given each needs its engine system? — **still open**; none beyond the envelope until its engine
   system exists (D2-191; §9)
4. Should worlds be described as a zone plus dial settings (§5)? — in part: within the envelope a world has dials (`settled`, the
   prevailing `wind`: D2-191, landgen/vocab.py); **still open:** §5's other axes (variability between years and rare catastrophe
   need the scheduler's years, not built)
5. The coarse planet (§4c): now, or deferred until a second zone has its engine system? — ~~open~~ deferred by D2-191 (one envelope,
   "no planet": temperate_landscapes.md §2), as §4c recommends

## History

- 2 Nov: Zach asked for the core environmental and terrain types and how biomes cluster, then for a coarse planet; written. The
  same day he narrowed the generator to one envelope (temperate_landscapes.md, built: D2-191).
- 5 Nov: Swept against DECISIONS, the spec and what is built (37.2): Q2 settled and Q5 deferred by D2-191, Q1 settled for the
  envelope; the zone beyond it, which zone next and zone plus dials still open. Owner line and History added.
