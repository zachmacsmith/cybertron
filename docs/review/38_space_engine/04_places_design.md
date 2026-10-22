# Review 38.04: places (node scale and kinds of land)

*22 Oct 2026, 37.4 session, with Zach. Design only: nothing built. Decisions and the running log are in
[devlog_37.4.md](devlog_37.4.md).*

## 1. The scale of a node

**The rule: if you could go there and be back before nightfall, it is the same node.** A node is a village, a valley or a camp:
a few households and the land they work. The places people use every day (their fields, the wood, the well, the stream, a
neighbour's house) are **sites inside the node**, used without travelling. An **edge** joins places far enough apart that whoever
crosses it sleeps at the other end.

Why this scale:

- **Presence is the node.** Who sees what (witnessing), who can talk in the round's message step, and who can hand goods to whom
  are all "at the same node". The node must be small enough that seeing everyone there is believable and fits the prompt (the
  Here section lists everyone present: about 15-20 people at most), and large enough that daily work needs no walking (run 1 lost
  40% of its actions walking between places that should have been one node).
- **Time.** A round is a day (the calendar compressed, as games do: devlog). Travel is the last act of a day; the traveller
  arrives the next morning, sees the place, and decides there. So an edge is a day's journey or more, and a node is everything
  within an easy walk of home.
- **Hierarchy.** A larger settlement is a **cluster of nodes** joined by one-day edges (hamlets around a market), not one big
  node; a region is a cluster of clusters.

Size, as a rule of thumb: **2-5 households, up to about 15-20 people, a handful of buildings** (houses, a store, a workshop, an
inn), plus its land. A market or crossroads node can hold more buildings and more passing people, which is what makes it
different.

### Buildings on a node

What limits a node is **people present** (about 15-20, for witnessing, the message step and the prompt), not buildings: the
prompt can list buildings briefly ("four houses, a store, a smithy, an inn"). So buildings are capped by **land**, as slots set
by the node's kind, and different buildings take different room:

| Building | Slots | Needs |
|---|---|---|
| House (a household: 4-6 beds) | 1 | |
| Store or granary | 1 (granary 2) | |
| Workshop (smithy, carpenter, tannery) | 1 | the trade's site (a forge needs fuel; a tannery water) |
| Inn | 2 | |
| Mill | 2 | a river or wind (valley, moor) |
| Hall or shrine | 2 | |
| Wall or palisade | none (it encloses the node) | upkeep scales with what it encloses |

Slots by kind, as a starting point: river valley 10-12, woodland 6-8, hills 4-6, moor and fen 3-4 (fen more once drained),
crossroads 14-20, deep forest and pass 0-1 (a camp or a toll post). So an ordinary node holds **about 5-12 buildings**, of which
2-5 are houses; a market node up to about 20. Plots are land too but counted apart (a kind's plots). Whether the limit is a
hard cap or a rising cost (crowding: thinner forage, more fever) is open question 4.

### Nights away

A night away from home is the cost of an edge:

| Where the traveller sleeps | Food that night | Other |
|---|---|---|
| Out in the open, mild season | 1.5 (the unsheltered ration, as built) | none |
| Out in the open, winter | 2 | the chance of waking starving (the cold) |
| With camping gear (a good, a few uses) | close to housed | gear wears out |
| As a guest in another household's house | as housed | uses a bed; the host's fire burns for them too |
| At an inn | as housed | paid; the innkeeper's business |

**Hosts and inns are part of the design, not an extra:** hospitality is a choice (or a norm, or a business), and a merchant's
route is a chain of hosts and inns.

## 2. Kinds of land

A node has a **kind**. The kind sets what the node can hold and how it behaves; a spec or the generator then places actual sites
and draws their hidden quality within the kind's ranges. The kind decides:

1. **Resources:** which can exist here, each with its regeneration regime (finite, renewable, renewable with a threshold, slow,
   periodic) and a range for its size and quality.
2. **What it lacks:** no kind is self-sufficient (scenario_design §1). This is where comparative advantage and dependence come
   from.
3. **Settlement:** how many households and buildings it can hold, how many plots.
4. **Climate response:** how its yields and hazards respond to the hidden climate (two axes, §3) and to the season.
5. **Incidents:** base rates of the local events that can strike it (floods, fire, fever, rockfall, storms, predators).
6. **Travel:** what crossing it or reaching it costs (slow, risky, closed in some seasons).
7. **Signs:** the in-world sentences its hidden state produces ("the river is running high for spring").

### The catalogue (first draft)

| Kind | Plentiful | Lacks | Settlement | Hazards | Climate: does well in / suffers in |
|---|---|---|---|---|---|
| **River valley** | rich soil (many plots), forage, fish, water | timber, stone, metal | many households | floods (spring, wet eras), fever | dry-warm; suffers wet |
| **Woodland** | timber (slow), game (threshold), forage (nuts, mushrooms), clearable into poor plots | good soil, stone | a few households | fire (dry eras), wolves | wet-mild; suffers dry (fire) |
| **Deep forest** | big game, old timber | everything else; no settlement | none (camps) | getting lost, predators; slow to cross | little change; a barrier |
| **Hills** | copper (finite seams), stone (quarry), pasture | grain, much forage | a few | rockfall, mine collapse, harsher cold | warm; suffers cold (early, long winters) |
| **Moor** | peat (fuel), pasture, heather | soil, timber | one or two households | storms, exposure (nights out cost more) | wet; suffers dry (peat fires) |
| **Fen** | fish, wildfowl, reeds (thatch, baskets); very fertile once drained (a works project) | dry land, timber, stone | few until drained | fever (high), floods | dry eras open it (drainable); suffers wet |
| **Coast or lakeshore** | fish (seasonal runs), salt (to preserve food: travel food, winter stores) | timber, metal | several | storms | stable; storms in wet eras |
| **Grassland** | herds (meat, hides, wool: clothing), open grazing | timber, stone, grain | several | drought, raids (open ground) | wet; suffers dry |
| **Crossroads** | position: traffic, merchants, room for many buildings (market, inn) | everything physical | many | thieves, fever (crowds), raids | none of its own; prospers with its neighbours |
| **Pass** | access to what lies beyond | everything; no settlement | none (a toll post at most) | avalanches; closed in winter | a cold era closes it longer |
| **Ruins** | salvage (finite: dressed stone, old tools), stories | everything living | none until rebuilt | collapse | none |

Goods the kinds give, and what needs them (37.2's goods): food (grain, fish, meat, forage), fuel (timber, peat), building
materials (timber, stone, reeds), metal (copper; later iron), salt (preserved food for journeys and winter), hides and wool
(clothing for winter), salvage. Each consumed need has to come from somewhere else for most households, so the map is the
dependency graph.

## 3. The environment on top of the kinds

**The hidden climate has two axes, temperature (cold to warm) and moisture (dry to wet).** The calendar moves temperature through
the year; eras shift both axes for many years; incidents draw their rates from the kind, the season and the era. Because kinds
respond differently (the table's last column), **an era does not hit everyone equally**: a dry era ruins the grassland and the
moor's peat but opens the fen for drainage and spares the valley; a cold era shortens the hills' working year and closes the pass.
So an era **shifts comparative advantage between places, and so between the households and institutions that hold them**. That
is the long-term-shift mechanism of the environment design (devlog decisions 4-5) made concrete.

| Layer | Drawn | Acts on a node through |
|---|---|---|
| Era (years) | from the seed; the same in every arm | the climate axes: yields, regrowth, hazard rates, season lengths |
| Season (the calendar) | fixed cycle, per-year severity from the seed | regrowth, the cold, sowing and harvest windows, edges closed |
| Incident (a day) | from the seed: a rate per kind x season x era | a flood, a fire, a fever, a rockfall, a storm, a stray herd |
| Internal consequences | the node's own state | depletion of seams, soil exhaustion, game below its threshold, felling |

**Signs are local.** Each kind has its own sentences for its hidden state, seen by the people at the node (and passed on by
travellers): the valley sees the river, the hills see snow on the tops early, the fen sees fewer geese, the moor sees the peat
crack. A traveller arriving from elsewhere carries news of other places' signs: one more reason merchants matter.

## 4. A node in a spec (sketch)

```yaml
nodes:
  millbrook:
    kind: river_valley              # defaults for everything below; any field can be set by hand
    sites:
      fields:  {plots: 12}                                  # quality drawn within the kind's range unless given
      meadow:  {forage: {K: 30, r: 0.6}}
      river:   {fish: {K: 40, r: 0.4, runs: [spring]}}      # periodic
      alder_house: {house: {household: Alder, beds: 5}}
      inn:     {inn: {beds: 4, keeper: Maud}}
  greystone:
    kind: hills
    sites:
      seam:   {copper: {S: 400}}                            # finite
      quarry: {stone: {S: 2000}}
      forge:  {forge: true}
edges:
  - {a: millbrook, b: greystone, days: 1}
  - {a: greystone, b: the_high_pass, days: 2, closed: [winter]}
```

## 5. Land cover and soil

A node's land is **divided among covers**: forest, fields, pasture, marsh, waste. The kind sets the starting mix; people change it,
and it changes back slowly when left alone.

| Change | Done by | Gains | Loses |
|---|---|---|---|
| Felling | work at a forest | timber | forest grows back slowly (as built: felling shrinks plant capacity) |
| Clearing | more work, after felling | plots (fields or pasture) | forage and game for good, unless abandoned |
| Draining | a works project at a fen | very fertile plots | fish, fowl, reeds |
| Abandonment | nobody works the land for years | forest returns (scrub first) | the plots |

**Soil fertility differs by kind** (river valley high, from the river's silt; fen very high once drained; grassland good but dry;
woodland moderate; hills poor) and by site within the kind (drawn). Cropping wears it down and fallow restores it (the internal
consequence of devlog decision 4). So clearing the woodland next to the village is a real choice: timber and fields now, against
the forage, the game and, if it is upstream, the river below (§6).

## 6. Generating a landscape

Not node by node at random: a random draw per node gives a map with no logic, no rivers that go anywhere and no reason for a town
to stand where it does. **Generate the physical world first, then derive the graph and the kinds from it, then settle it**, as
map generators do (Red Blob Games' polygon maps, Azgaar's fantasy map generator; Dwarf Fortress generates elevation, rainfall,
temperature and drainage, then rivers, then history). The plane is hidden; agents only ever see the graph.

1. **Points on a hidden plane** (well spaced), one per future node; neighbours joined (a Delaunay-style graph, thinned).
2. **Elevation** (a range or two, a coast on one side) and **moisture** (more near water and on the windward side of the hills,
   a rain shadow beyond them).
3. **Rivers:** from wet high ground, each point drains to its lowest neighbour; flow accumulates downstream; enough flow makes a
   river. A river runs **along edges, through nodes**, to the sea or a lake.
4. **Kinds** from elevation, moisture and rivers (a biome table): high and dry hills, high and wet moor, low and wet fen, low on a
   river valley, middle and wet woodland, middle and dry grassland, at the sea coast; a low edge across a range is a pass.
5. **Resources** from the terrain: seams in hills, salt on the coast, peat on the moor, fish in rivers, soil by kind and river.
6. **Edges and their costs** from the terrain: uphill and through forest slower, a river crossed only at a ford or a bridge, a pass
   closed in winter, along a river faster downstream once there are boats.
7. **Settlement:** founders take the best sites (soil, water, defence); a market grows where routes meet (a confluence, a ford, the
   node most paths pass through); then 37.6's generated population and history fill the houses.
8. **Checks** before a world is used: no node self-sufficient, every settlement depending on at least two others, the settled core
   compact (two or three days across), at least one chokepoint (a ford, a pass, a bridge).

**Rivers are worth the trouble** because they connect places causally, not just as paths:

- **Downstream externalities.** Felling upstream raises floods downstream; irrigating upstream leaves less water downstream; a mill
  dam changes the flow below. Villages on one river have problems no single village can solve: water rights, treaties, blame.
- **Transport.** A river is a road for goods once there are boats (faster downstream, slow or impossible upstream), so river towns
  trade, and the confluence is where the market grows.
- **Chokepoints:** a ford or a bridge is a place someone can hold and toll.
- **Fertility and danger together:** the river's silt makes the valley rich, and its floods make it risky.

**Hand-crafting stays possible at every layer** (README rule): a spec can give the whole graph by hand, or sketch the features
("a river from the hills to the sea through these three nodes", "a range here with a pass") and let the generator fill in the
rest, or fix any single node's kind, sites or resources. The first worlds should be hand-made and small; the generator is for scale
and for drawing many comparable worlds.

## 7. Open questions

1. **How many kinds for the first worlds.** Proposed: river valley, woodland, hills and crossroads first (they already give food,
   timber, metal and a market, and each lacks what another has); the rest when their goods exist.
2. **How exact resources are.** Exact stocks in the state, coarse words in the prompt (as `cybertron2` does now: "plentiful",
   "thin"), with the hidden quality of each site drawn within its kind's range.
3. **Whether the climate axes are shown at all.** Proposed: never as numbers; only through signs, yields and the almanac.
4. **Settlement capacity as a hard cap or a crowding cost.** A cap is simple; a cost (more households, thinner forage, more
   fever) is what drives people outward.
