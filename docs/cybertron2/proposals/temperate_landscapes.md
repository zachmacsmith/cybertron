# Proposal: landscapes that make sense, within one environmental envelope

Status: **design, for Zach's decision; nothing to build yet**. Zach, 2 Nov: "select a subset of the most relevant parts of the
planet and larger terrain systems / ecosystems that we think would make sense, and then design within that for now ... rn the
environments generated don't make a whole bunch of sense". Owner 37.2. It narrows ecosystems.md (the wide design, kept for later)
to what the generator should do now, and answers the review of the generated worlds below. Current as of 2 Nov.

## 1. What the review found, checked

Another session reviewed 17 generated worlds; 37.2 re-measured all 17 configurations (seed 7) and confirms every finding.

**What holds:**
- rivers drain, and wind 1.2 to 1.6 times their straight length;
- temperature falls sensibly with height;
- wet ground and meadow follow the rivers, and hills are open grazing.

**What fails:**

| Finding | Measured (seed 7) | Cause in the code |
| --- | --- | --- |
| **Configurations don't make their own landscape** | Fen with islands: 0% fen (deep forest 36%, loam 23%). Delta: no saltmarsh or floodplain to speak of. Ring basin: one round lake, 32% of the land. | A primitive only **nudges** the physics (a wetness bump, a flattening), and terrain is then re-scored from the physics. The fen's flattening sets the ground to sea level + 4 m inside land at about 55 m, so it becomes a pit, filled as lake or terrace, and only 9% of its land reaches the fen's wetness. The ring basin has no outlet cut deep enough, so the fill makes it a lake. The delta is a straight laid river and a small fen bump. |
| **Far too many lakes** | 53 to 261 per world; 228 in the plain lowland | Every hollow in the random height surface deeper than 4 m is filled as a lake. Real river country has almost no closed hollows: erosion cuts them an outlet. Many lakes belong to glaciated or limestone ground. |
| **Forest everywhere** | 39 to 83% forest cover | The natural-cover rule maps the two commonest terrains (loam and clay) to forest. That is the wildwood with no people at all, not land settled for generations. |
| **Heath as blobs** | sandy heath 7 to 12%, scattered | Heath follows sand alone, and sand is a noise threshold. Lowland heath is made by people: sandy, acid soil cleared, then grazed and burnt for centuries. |
| **Circles** (G-34) | the ring basin's lake, the isthmus's round landmasses, deep forest's arcs, domed hills | Shapes are radial bumps with a 3.5% warp; deep forest is a fixed radius from villages. |
| **Ruler-smooth coasts and laid rivers** | a coast is a straight line bent about 3.5%; laid rivers near-straight | A coast is a half-plane; a laid river is a polyline carved as it stands. |

## 2. The envelope: temperate oceanic lowland and upland, settled

Design for one climate zone now, the one the engine, the agents' world knowledge and every hand-made world already share:
- **climate:** mild, wet, westerly winds, winters cold but rarely deep (Köppen Cfb, roughly lowland Britain and the near Continent at
  50 to 56°);
- **no planet:** the zone is fixed, with two dials: west-wet against east-dry, and how high the uplands reach.

**In:**

| Landscape system | What it is | Ecosystems in it (the palette) |
| --- | --- | --- |
| **Lowland river country** | a vale with terraces, a floodplain, a river and its tributaries; drains, few lakes | oak-ash wood, alder carr on the floodplain, hay meadow, pasture, arable on terraces |
| **Scarp and vale** (chalk or limestone) | a dry down above a clay vale, springs along the foot | chalk grassland, beech hangers on the scarp, oak on the clay; spring-line villages |
| **Sand country** | sand and gravel ridges, acid soils | birch and pine, heath where grazed and burnt, poor arable |
| **Upland and moor** | hills rising to open moor, steep valleys | sessile oak and birch in the valleys, hill pasture, moor and blanket bog on the tops, glacial lakes (tarns) only here |
| **Fen and estuary** | a basin of peat and silt by an estuary | reedbed, fen, carr, wet grazing, saltmarsh at the coast, meres |
| **Coast** | cliffs, dunes, shingle and saltmarsh | dune grassland, saltmarsh grazing, a sheltered harbour |
| **Wildwood frontier** | the land beyond settlement | old oak-ash and lime wood, with its depth bands |

A world is one or more of these systems, joined: most real regions are two or three, a vale under a down, uplands above river
country, a fen inland of a coast.

**Out, for now** (in ecosystems.md for later):
- the other climate zones and the planet;
- glaciated mountains above the moor;
- karst;
- deltas (rare in this zone: an estuary instead);
- rifts;
- archipelagos.

## 3. The three changes the review asks for

### 3a. Landscape systems as templates that guarantee their land

A system is laid as a **template**: a sequence across its gradient (ecosystems.md §3: a catena, a zonation), placed by the macro
layer. The physics still gives height, wetness and soil, but within a template the ecosystem is assigned by position along it, not
scored independently. Examples:
- a fen system makes its basin flat and wet, joined to the estuary, so it drains to the sea, not into a pit;
- a scarp's foot gets springs and its villages;
- a river country's floodplain is as wide as its river's size says.

**Every configuration then carries a check that it makes its own landscape.** A fen world must be mostly fen and wet grazing, a
scarp world must show its down, scarp and vale, and so on, each with the share it promises. A configuration that fails it is not
offered. Today's 17 configurations become the systems above and their joins. Those outside the envelope (delta, rift) go to
waiting with the others.

### 3b. Water that drains

- **Hollows are breached, not filled.** The default is to cut an outlet through the lowest rim (depression breaching, the standard
  method), so river country drains as real river country does.
- **Lakes come only from what makes lakes here:**
  - meres in fen systems;
  - tarns in upland systems;
  - a laid lake;
  - a hollow both large and deep that no template explains, kept as a rare exception.
- **Check:** lakes per 1,000 km² in river country under about 1; in uplands a few small tarns.

### 3c. Land as people have used it: the state layer, by how long a place has been settled

Natural cover (the wildwood) is the starting point. Settlement then turns land around villages in rings by their age and size:

| Ring | What it becomes |
| --- | --- |
| infield | arable and meadow |
| outfield and commons | pasture; heath where the soil is sand; wood-pasture |
| managed woods | coppice with standards on the clay and the steep land, which is where real woods survived |
| beyond | the wildwood, with its depth bands, or scrub where it was cut and abandoned |

A world dial, **how long settled**, sets the region's wood share:
- about 10 to 25% for long-settled lowland (Domesday England was about 15%);
- 40 to 70% for a frontier.

Heath then appears where sand meets grazing near people, as it did historically, not as noise blobs. Deep forest becomes the core
band of large woods (ecosystems.md §6), so a village can sit at a forest's edge.

### 3d. Shapes that are not circles or rulers

- **Coasts:** the half-plane plus fractal noise at several scales, with headlands and bays where hard and soft rock alternate.
- **Laid rivers:** meander between their anchor points (noise along the course, with amplitude scaled to the river's size), and
  braid or wander across wide floodplains.
- **Bumps** (hills, basins, islands): an angular profile and a stronger, multi-scale warp, so a hill is a ridge with spurs, not a
  dome.
- **Woods' edges:** by hours of travel with noise, not straight distance (G-34).

## 4. What it costs

| Part | Size |
| --- | --- |
| templates for the seven systems, their joins, and the "makes its own landscape" checks | M |
| breaching hollows; lakes by system | S |
| the state layer by settlement age, and the "how long settled" dial | M |
| coasts, rivers, bumps, woods' edges | S-M |
| the ecosystem palette for this zone (the forest types of ecosystems.md §6) and depth bands, written as data | S-M |

About one to two weeks in all. The engine needs nothing new: every ecosystem still maps to today's covers, and its own properties
(forest type, depth) are written as data the engine ignores until it reads them.

## Open questions (for Zach)

1. The envelope: temperate oceanic, lowland to moor, settled, with the seven systems above. Anything to add or drop?
2. Templates that guarantee their landscape, with a check for each configuration?
3. "How long settled" as the dial for the land's state (wood share from about 15% to 70%)?
4. Build it once decided: before the cheap ladder runs, or after? The ladder's world is plain lowland, and it would look different
   (fewer lakes, less forest) but play the same.
