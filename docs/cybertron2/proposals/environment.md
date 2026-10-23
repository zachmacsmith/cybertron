# Proposal: the environment over time (one scheduler for eras, years, spells, incidents and their signs)

**Status:** partly accepted: D2-69 to D2-75 (23 Oct); the catalogue, disease and the details are discussion. Design only: nothing
is to be built yet (Zach). **Owner:** 37.2, who now owns `spec/environment/` (D2-75); 37.4 builds.
**Affects:** spec/environment/scheduler.md, calendar.md, climate_and_eras.md (to write), resources.md; information/signs.md,
perception.md; world/land.md (land kinds' responses); life/ (illness); economy/production.md (crops, herds, forests); conflict/
(fire); core/architecture.md (the scheduler's place in the day). **Model:**
[02q_environment_model.py](../../review/37_growth/02q_environment_model.py).

## Summary

One central scheduler runs every change that comes from outside the people: **eras** (years: a dry, wet, cold or steady
regime), **years** (the fixed calendar with each year's severity), **spells** (days: dry and wet spells, cold snaps, storms),
**incidents** (a day at a place: a fire, a flood, a blight, a fever, wolves, a stray herd, a windfall) and **spreads** (a fire
running from parcel to parcel, a fever from person to person). **Each layer sets the odds of the one below**, so a dry era makes
dry years likelier, dry years longer dry spells, and dry spells more fires, which then spread further. Every layer is drawn from
the seed, the same in every arm (D4-4); an incident fires when a **paired uniform** falls below its hazard, so arms differ only
where their own states differ. Each process has **mechanical consequences**, made through the engine's primitives, and
**observables**: signs with a sense, a range, a salience, a lag and a reliability, read differently by different people
(their concerns, skills and attention). Slow change is never announced; it is inferred from accumulated signs, memories and
records, which gives writing, elders and an almanac their value.

## 1. What exists (surveyed 23 Oct)

| Source | What it gives |
|---|---|
| D4-4 | external change separate from internal consequences; one central scheduler; drawn from the seed, the same in every arm |
| D4-5 | three time scales, each modulating the one below: eras and trends, cycles, incidents |
| D4-6, spec/information/signs.md | a sign is one in-world sentence with an audience, a lag and a reliability, kept apart from its effect |
| D4-7, spec/environment/resources.md | resources by how they come back (finite, fast, threshold, slow, periodic): the internal consequences |
| D4-13, D4-17, spec/environment/calendar.md | a compressed year (16-60 days); daylight by season |
| D4-35 | everything happens in a place; nothing at one node is seen at another except as carried |
| 38.04 §3 | a hidden climate of two axes (temperature, moisture); eras shift both; **land kinds answer differently** ("suffers wet", "suffers dry"), so an era shifts comparative advantage between places; signs are local and kind-specific |
| 37.4's old-engine design (`wp/environment`, 04_environment_design.md) | the criterion (a variation earns its place only if it changes who needs whom); **incidence over frequency**; **legibility** (an almanac); target rules (rich, poor, a role); a foresight office; endogenous against exogenous trends; windfalls as well as shocks |
| seeing.md (proposal) | facts with salience, range and tags; what an agent notices is set by presence, attention, salience and relevance to its concerns |
| fuse_events.md (D2-5) | an event with a detection time and a completion time: precursors give people time to respond |
| the M1 engine | incidents listed by hand in the world file (day, node, kind); two kinds coded (a stray herd, a fire in a store); events carry salience, tags and who they concern |
| missing | floods, droughts, blight, fever, murrain, wildfire: none exist; no eras, no spells, no year severity in the engine |

## 2. Principles

1. **The institution test** (37.4's old design): a variation earns its place only if it creates a holder and a needer, or a
   problem no one solves alone. Small symmetric losses are noise.
2. **Incidence over frequency:** where a shock lands (one household's store, the low fields, the fen) matters more than how often.
3. **External and internal stay apart** (D4-4): the scheduler draws only what no one in the world causes; depletion, soil,
   game collapse and fires people set are the world's own physics and agents' acts.
4. **Paired across arms:** every draw is keyed by what it is about (kind, place, day), never by the order things happen in.
5. **Everything in a place** (D4-35): every incident and sign has a place; slow regimes are regional but felt only locally.
6. **Consequences and experience are separate outputs** of the same event (D4-6): what changes, and what each person can notice.
7. **Slow change is never stated.** No agent is told "the climate is drying"; it sees a dry summer, hears an elder say it is the
   third, or reads it in a chronicle.
8. **Data, not code:** a new kind of incident is a data entry with drivers, effects and signs from small fixed vocabularies.

## 3. The layers

| Layer | Time | Scope | State | Drawn | Sets the odds of |
|---|---|---|---|---|---|
| **era** | years | the region | a regime: moisture and temperature anomalies (steady, dry, wet, cold, ...) | a Markov chain with long dwell times, at generation | the year's severity |
| **year** | the calendar | the region | each year's moisture and temperature (the era's anomaly plus the year's own draw); the seasons are fixed | at generation | spells; season lengths at the edges (an early winter) |
| **spell** | days | the region, felt by land kind | dry, wet, normal, cold snap, storm | a semi-Markov chain: each spell's kind and length drawn given the season and the year | incidents; daily conditions (crop water, fuel dryness, river level) |
| **incident** | a day | a place: a parcel, a building, a node, a herd, a person, a road | a kind and its parameters | each day, a paired uniform against a hazard | spreads; fuse events (D2-5) |
| **spread** | days | from a place to its neighbours | which places are burning, ill, flooded | each day, a paired uniform against a spread hazard | further spreads; aftermath |

**Hidden daily conditions** come from the spell, the season and the land kind: a parcel's **water** (dry, enough, flooded), its
**fuel dryness** (for fire), the **river's level** (for mills, irrigation, fords and floods), **cold** (for the cold rules and the
passes), and **sickness in the air** (damp and crowding, for fever). Other systems read them (a crop's growth, a mill's flow, a
ford's crossing), so the weather reaches the economy without each system rolling its own dice.

## 4. Hazards: how a layer sets the odds of the next

For each kind and each place it can happen at, each day:

**hazard = base x weather(spell) x season x land kind x exposure(local state)**

- **Drivers** come from a small library: a table by spell, by season or by land kind; a curve on a hidden variable (fuel dryness,
  river level); a product. The era acts through the year and the spell, so its effect compounds (§7).
- **Exposure** is the place's own state: a forest's fuel (its stock against capacity), a node's crowding and hunger (fever), the
  crop on a plot (blight), herds on a pasture (wolves, murrain). It is internal, so it can differ between arms.
- **Paired uniforms:** the draw is U(seed, kind, place, day), independent of everything agents do. The incident happens if U is
  below the hazard. Two arms with the same seed meet the same weather and the same draws; an incident differs between them only
  where exposure differs (one arm's forest was felled, so it cannot burn). This keeps common random numbers without freezing
  internal consequences.

## 5. Spreads

A spreading incident tries each neighbour of each burning, sick or flooded place every day, with its own hazard and its own paired
draw, until it burns out or is stopped.

| Spread | Neighbours | Spread hazard rises with | Stopped by |
|---|---|---|---|
| **wildfire** | adjacent forest and scrub parcels; buildings next to them (layout.md) | dry spell, wind (storm), fuel | a wet spell, a firebreak (a cleared parcel), a bucket line at a building (fuse event), stone (D2-49) |
| **fever** | people sharing a house (strong), a node (weaker); travellers carry it along edges | damp, cold snaps, crowding, hunger | recovery and immunity, keeping apart (staying home, closing a gate: D2-5), a healer (later) |
| **blight** | plots with the same crop at the node | wet spells, the same crop twice (D2-53) | rotation, a dry spell |
| **murrain** (cattle sickness) | herds sharing a pasture; herds driven along an edge | wet and warm, crowding on a pasture | keeping herds apart, slaughter |
| **flood** | parcels downstream at the node; nodes downstream on the river | a wet spell upstream | banks and ditches (D2-66), height of the parcel |

The model shows the effect: **spreading kinds amplify an era's difference far more than point hazards do** (§9).

## 6. The first catalogue

*The full catalogue (eras by family, weather by land kind, spreading hazards in six patterns, and how people prepare, respond
and recover) is in [environment_catalogue.md](environment_catalogue.md); the table below is the core.*

| Kind | Layer and scope | Drivers | Consequences (primitives) | Observables: before / during / after | The problem it creates |
|---|---|---|---|---|---|
| **drought** | spell, region | dry era and year, summer | crops lose growth each dry day (water), forage regrows slower, river low (mills slow, fords easy) | "nine days without rain"; "the stream is low, the wheel turns slowly"; cracked fields, thin harvest | storage, sharing, irrigation, migration |
| **wet spell, flood** | spell, region; flood at low parcels and downstream | wet era and year, spring | low plots' crops destroyed, buildings damaged, the ford closed | "the river is rising, brown and fast" (a fuse: hours to move stock); "the low fields are under water"; silt and wreckage | relief, banks and ditches, who holds the high ground |
| **cold snap, hard winter** | spell, region | cold era, winter, the year's temperature | the cold rules (H-5) bite harder; passes close (edges); herds need more fodder | "frost every morning"; "snow on the tops early"; the pass closed | stores, fuel, shelter for the poor |
| **storm** | spell, region; damage at buildings | wet or cold, autumn | roofs damaged (condition), trees down (timber windfall), wildfire spread when dry | "the wind is rising"; roofs torn | repair work, windfall claims |
| **wildfire** | incident at a forest parcel, spreads | dry spell, summer, fuel, a storm | forest stock burnt (regrows slowly: resources.md), game flees, buildings next to it at risk (D2-50) | smoke on the ridge (a fuse event); "the Deep Wood is burning"; a black, open wood for seasons (easy to clear) | firebreaks, a fire crew, who pays for the loss |
| **house fire** (exists) | incident at a building | a lit hearth, dry spell, wattle and thatch | store and roof (as M1), people inside (D2-50) | smoke, shouting (fuse) | neighbours' help, rebuilding |
| **blight** | incident at a plot, spreads to the same crop | wet spell, summer, the same crop twice | the crop fails | "the barley is spotting black"; a failed field | rotation, a granary, help between farms |
| **fever** | incident at a node, spreads among people | damp, cold, crowding, hunger; fen land | the sick: fewer units, a death hazard (with 37.1), contagious | "Wat is coughing and burning hot" (seen by those near); "three houses have fever"; graves | caring for the sick, keeping apart, a healer, orphans |
| **murrain** | incident at a herd, spreads by pasture | wet and warm, crowding | cattle die or give no milk | "the cows are off their feed"; dead beasts | keeping herds apart, a common herd's rules |
| **wolves** | incident at a pasture or herd | cold winters, game scarce, forest nearby | beasts lost at night | tracks at dawn; a carcass | a watch (D2-21), dogs (later), a bounty |
| **stray herd** (exists) | incident at a field | fences down, hunger in the herd | a crop trampled | "the Fenn cattle are in the barley" | claims and damages |
| **windfalls** | incident at a place | season, spell | stray game, a bumper field, a trove in ruins, a storm's fallen oaks | seen by whoever is there first | first finder against holder: claims |

## 7. Observables and experience

**What a person notices is the engine's event log filtered through presence, attention, salience and relevance** (seeing.md); the
scheduler only supplies the facts.

| Property | Meaning | Examples |
|---|---|---|
| **sense** | sight, sound, smell, feel, the body, talk | smoke (sight, smell); the river's roar (sound); "you are feverish" (body) |
| **range** | the parcel, the site, the whole node, the house, the body | a field's spotting is seen only in that field; smoke over the ridge by the whole node; your own fever only by you |
| **salience** | how much it stands out, so whether it is noticed without attending | a fire 0.95; a rising river 0.8; a dry week 0.4; a late spring 0.15 |
| **lag** | how long after the change it shows | blight shows days after it takes hold; a fever's first cough a day before the fever |
| **reliability** | how often a sign is true | a red sky at dawn: storm 1 time in 3 |
| **tags and concerns** | what it bears on (food, shelter, danger, a person, a claim), matched to the observer's holdings, kin and duties | the Fenns' plot flooding is relevant to the Fenns and their creditors; a cough is relevant to the cougher's household |
| **who can read it** | some signs mean something only to a skill (knowledge.md) | a herder reads murrain in the cows' eyes; an elder reads the winter in the geese; a farmer reads blight early |
| **persistence** | aftermath that stays to be seen | a burnt wood for a season; graves; silt on the fields |

**Experience differs across land, people and salience:**
- **Land:** the same dry spell is "the grass is brown" on grassland, "the peat is cracking" on the moor, "the fen is drying, the
  geese are fewer" in the fen, and a good haymaking on the wet valley floor (38.04's responses). An era therefore reads as good
  news in one place and ruin in another.
- **Individuals:** the sick feel it (body), their household sees it (high relevance), the node notices it when salient, other
  nodes hear of it only when someone carries the news (D4-35). Those who hold the flooded plot, owe on it, or are kin to the
  burnt-out family get it as relevant; others as a glimpse.
- **Salience:** precursors are often low-salience and need attention or skill (a smudge of smoke at dawn, a cough); the event
  itself is high-salience; slow signs are the lowest of all.

**Slow change is legible only by accumulation.** An era has no sign of its own on a given day; it is the third dry summer. It
shows through: **memories** (an agent remembers last summer's drought), **elders' stories** in seeded histories ("not since the
great dry, when I was a girl"), **records** (a chronicle of harvests and floods: documents, D2-8; a scribe; 02h), and an
**almanac office** that keeps them (37.4's old design). So writing and record-keeping gain a value that only appears when the
world changes slowly. Some era signs are true and some false (reliability), so who is believed becomes a matter of standing.

**Precursors give time to respond** (D2-5): the river rising, smoke on the ridge and the first cough are the detection time of a
fuse; a watch, a skilled reader or an almanac shortens it.

## 8. A clean, central, extensible scheduler

**Data (in the world file):**

```yaml
environment:
  eras:      {regimes: {steady: {moisture: 0, temp: 0, dwell: 6}, dry: {moisture: -0.5, temp: 0.2, dwell: 4}, ...},
              next: {steady: {dry: 0.4, wet: 0.4, cold: 0.2}, ...}, start: steady}       # or pinned: [steady, dry, dry, ...]
  years:     {moisture_sd: 0.35, temp_sd: 0.3}
  spells:    {kinds: [dry, wet, normal, cold_snap, storm], odds: {...by season, read the year...}, length: {...}}
  kinds:                                   # incidents and spreads: one entry each
    wildfire:
      at: parcel[forest, scrub]
      hazard: {base: 0.004, weather: {dry: 4, wet: 0.2}, season: {summer: 2, winter: 0.2}, kind: {woodland: 1.5}, exposure: fuel}
      spread: {to: adjacent[forest, scrub, building], hazard: {base: 0.5, weather: {dry: 1, wet: 0.05}}, lasts: 2}
      effects: [{destroy: parcel.timber, share: 0.6}, {set: parcel.cover, value: burnt}, {fuse: buildings_adjacent}]
      signs:   [{when: before, text: "smoke on the ridge above {parcel}", sense: sight, range: node, salience: 0.6, lead: 1},
                {when: during, text: "{parcel} is burning", sense: [sight, smell], range: node, salience: 0.95},
                {when: after, text: "{parcel} is black and open", range: parcel, salience: 0.3, lasts: season}]
      tags: [danger, timber, shelter]
  pinned:    [{day: 12, node: millford, kind: flood}]       # hand-placed incidents, as now
  off:       [murrain]                                       # ablations
```

**One `Scheduler`, one place in the day** (dawn, before people look: 05 §1):
1. **At generation:** draw the eras, the years and every day's spell for the run's horizon from the seed (they read nothing
   internal). They are in the record from day 0.
2. **Each dawn:** compute the day's hidden conditions per land kind and parcel (water, fuel, river, cold, damp).
3. **Each dawn:** for every kind and every place it can happen at, compute the hazard and compare it with U(seed, kind, place,
   day); fire what falls below; add hand-placed incidents.
4. **Each dawn:** run the spreads for everything active, in a fixed order (by place id), each try with its own paired draw.
5. **Effects** go through `World.apply` primitives (`destroy`, `set`, `harm`, `draw`; 38.17 §4), so laws and reflexes can hook them
   later and every change is recorded with its cause (`cause: scheduler, kind, incident id`).
6. **Signs** go into the event log at their places, with sense, range, salience, lag, reliability and tags; perception decides
   who sees them (seeing.md).
7. **Truth** (every hidden condition, every draw, every incident) goes to the run's truth log, never to an agent.

**Interfaces:** `conditions(place, day)` (read by crops, mills, fords, the cold), `active(kind, place)` (for fuse events and
reflexes), `truth()` (for analysis). Agents' code reads nothing from it directly (38.17 §1.3): only signs, through perception.

**Extending it:** a new kind is a data entry; its drivers, effects and signs come from fixed vocabularies; a new effect needs one
handler registered by name. Kinds can be turned off for ablations, pinned for experiments, or scaled by a world setting.

**Checks:** determinism (same seed, same truth log); pairing (two arms with different agents get identical eras, years, spells and
draws); statistics in dry runs (incidents a year by kind, era and land kind, against a target table); the institution test per
kind in LLM runs (did anyone help, lend, insure, guard, organise?).

## 9. What the exploration model shows

[02q_environment_model.py](../../review/37_growth/02q_environment_model.py): a three-node region (a river valley, a woodland, a
fen), 40-day years. Holding the era fixed, averaged over 40 seeds:

| Era | Fires started a year | Fire spread (parcels) | Floods | Blights | Fever outbreaks |
|---|---|---|---|---|---|
| steady | 2.8 | 12.2 | 1.1 | 0.9 | 1.0 |
| dry | **4.0** | **25.4** | 0.5 | 0.6 | 0.8 |
| wet | 1.9 | 6.7 | **2.1** | 1.2 | 1.1 |
| cold | 2.4 | 10.2 | 1.4 | 1.0 | 1.1 |

- **The modulation works, but only if the coupling is strong enough.** With a weak pull from the year on the spells, eras barely
  differed (dry 3.3 fires a year against wet 2.0); the coupling had to roughly double before eras felt distinct.
- **Spreading kinds amplify:** a dry era starts about twice as many fires as a wet one but burns nearly four times the forest.
- **Fever is driven by local exposure** (crowding) more than by the era, so it differs between places more than between eras.
- **Land kinds split the same era:** the woodland burns, the fen sickens, the valley floods.

## 10. Time scales in a compressed calendar

A run of 20-30 days is about one year (D4-13). **An era of several years never changes within a run.** Options:
1. **Eras as starting conditions:** a world starts in an era (seeded), with its people remembering past ones (D4-21); within a run
   the era sets the odds but does not move. Its shift is felt across chapters or long runs.
2. **Compressed eras** for long runs: dwell of one to three years (40-120 days).
3. **A scripted shift** for experiments: an era change on a chosen day, the same in every arm.
Proposed: 1 for the first worlds, 2 and 3 available as world settings.

## 11. Risks attached to things (D2-71)

Zach: incidents vary with how a world is set up, and every new object brings its own risks; many emerge from the systems rather
than from the weather. So risks are **data on kinds of things**, not only on the land:

| Thing | Its risks | Raised by | Prevented or reduced by |
|---|---|---|---|
| **a house or any building** | a break (H-5), **collapse** (injures or kills those inside), a chimney fire | missed upkeep (condition low), gales, snow load, wattle | upkeep, stone, mending after a storm |
| **a mill** (D2-61) | the wheel breaks; a flood damages the wheel and leat; the stones crack | missed upkeep, high river, hard use | upkeep by a carpenter and a mason; a sluice to shut in a flood |
| **a store** | rats, damp, theft, fire | full and old stores, wattle, damp | cellars, bins, a lock, a cat (later) |
| **a herd** | strays (fences down), **escapes** onto crops, wolves, murrain, theft | poor fencing, hunger, winter, pasture shared with other herds | fences mended (upkeep), a herder, stalls (D2-45), a watch |
| **a crop** | blight, smut (seed-borne), a **new pest** that attacks one crop kind, hail, frost | the same crop twice, wet spells, seed from elsewhere | rotation, clean seed, seed selection (D2-65) |
| **a road, a bridge, a ford** | washed out, a bridge falls | floods, missed upkeep | upkeep, stone bridges |
| **a mine or quarry** | collapse (injury, the seam closed for days) | a deep seam, wet spells, no props | props (timber), a skilled miner, a miner's pick (D2-48) |
| **a hearth or oven** | fire spreading to the roof | thatch, dry spells, no one watching it | stone, a fire watch |
| **gear and tools** | wear and breaking (D2-46) | use | a smith's mending |

- **The hazard of a thing's risk** uses the same formula (D2-69): base x conditions x **neglect**, where neglect is how far the
  thing's condition has fallen through missed upkeep. So upkeep is the price of lower risk, and a household or institution that
  cannot keep up its buildings carries a growing chance of losing them, or the people inside.
- **Novel risks arrive with novel things:** a new crop kind from the frontier can bring a pest the region has never seen; a herd
  bought at a far market can bring murrain (carriage, environment_catalogue.md §3). The world file and the frontier (37.5) can add
  risk entries with the things that carry them.
- **Emergent incidents** need no scheduler entry beyond the thing's risk: a collapsed house is the house's own risk firing; its
  draw is still keyed (D2-70), so arms stay paired.

## 12. Across edges (D2-72, D2-74)

Zach: fires, and some things people experience, should cross between nodes, depending on the edge: a mountain ridge, a forest
path and a long plain carry different things.

**What the engine needs on an edge** (world/edges.md, 37.4: OPEN Q-17): its **terrain** along the way (open plain, farmland,
woodland, marsh, hills, a ridge or pass, a river valley), its **length** (days, as now), whether it follows a **river**, and its
**height change**. Generation already derives edges from terrain (D4-22), so these come from the same layers.

| Terrain of the edge | Sight (smoke by day, fire at night, a beacon) | Sound (bells, a great noise) | Fire spreading | Disease and pests |
|---|---|---|---|---|
| open plain, farmland | far: smoke seen two or three days' travel off | about a day | grass fire in a dry spell | carried by travellers |
| woodland | hidden: seen only as smoke above the trees, close | short | **carries fire** (a forest fire can run along it) | carried |
| marsh | far over flat ground, hazy | short | stops fire | fever along it |
| hills | partly: from the tops | short | patchy | carried |
| ridge or high pass | **blocks** sight between its two sides, except from the top | blocked | stops fire above the tree line | carried, slowly |
| river valley | along the valley, not over its sides | carries along the water | stops fire (the river) | **floods flow down it**; fever |

- **A sign's reach** = its kind's carrying power (smoke from a burning wood carries far; a house fire's smoke less; a sound little)
  x the edge's terrain factor, shrinking with length. Signs that arrive are weaker (lower salience) and vaguer ("smoke to the
  east, toward Ashwood"), so a far sign says that something is happening, not what.
- **Fire across an edge:** a fire burning several parcels next to a wooded edge tries that edge with a hazard set by its size,
  the spell (dry, windy) and the edge's terrain; if it crosses, it reaches the far node's parcels by that edge a day later.
- **What does not cross** without a carrier: speech, prices, deaths, decisions (D4-35 still holds for everything but signs a kind
  declares as carrying).

## 13. Answers so far (23 Oct)

1-2. The layers, the hazard and paired draws: accepted (D2-69, D2-70). 3. The catalogue: wider than §6 (environment_catalogue.md),
and risks attach to things (D2-71, §11); fires cross edges (D2-72). 4. Eras as starting conditions (D2-73). 5. Signs carry between
nodes as the edge's terrain allows (D2-74, §12). 6. Disease: to flesh out (OPEN Q-16). 7. The environment area moves to 37.2 (D2-75).

## Why

- One scheduler, drawn from the seed, keeps every arm on the same weather (D4-4) and keeps environmental dice out of every other
  module.
- Cross-scale modulation through the spells gives eras real, compounding effects without special cases.
- Paired uniforms keep pairing even where the world has diverged.
- Separating consequences from signs, and routing signs through perception, gives each person their own experience of the same
  event, which is where institutions start (who knew first, who was hit, who was told).

## Alternatives considered

- **Hand-listed incidents only** (M1 now): kept for pinning; insufficient alone (no eras, no odds, no spread).
- **A separate environment module per system** (37.4's old `environment.py` beside subsistence): rejected by D4-4 (one scheduler).
- **Rolling incidents with a shared random stream in order:** breaks pairing as soon as two arms differ; replaced by keyed draws.
- **A full weather simulation:** rejected (the old brief's non-goal); spells and conditions are enough.
- **Announcing eras** ("a dry age begins"): rejected: slow change is inferred.

## Open questions (for Zach)

1. The layers and the hazard formula as above?
2. Paired uniforms keyed by kind, place and day, with exposure from local state (so arms can diverge where their states do)?
3. The first catalogue (§6): which kinds for the first worlds? Proposed: drought, wet spell and flood, cold snap, storm, wildfire,
   house fire, blight, fever, wolves, stray herd, windfalls; murrain with cattle.
4. Eras as starting conditions in the first worlds (§10, option 1)?
5. **Seen from afar:** smoke over a burning wood, or a beacon, is visible from the next node in life; D4-35 forbids seeing another
   node. Allow a narrow class of distant signs (smoke, beacons, a flooding river's water arriving), or keep D4-35 strict?
6. Fever's mortality and the sick's units (with 37.1); a healer later.
7. Ownership of `spec/environment/`: 37.2 drafts and 37.4 compiles, or the area moves to 37.2?

## History

- 22 Oct: 37.4: D4-4, D4-5, D4-6, D4-7; 38.04 §3 (climate axes, land kinds' responses, local signs); the old-engine design on
  `wp/environment` (criterion, incidence, legibility, foresight); spec/environment/scheduler.md written.
- 23 Oct: 37.2 found floods, droughts and blight missing (board, farming.md); M1 coded two hand-listed incidents (stray herd, fire).
- 23 Oct: Zach asked 37.2 to take the environment design: long and short time scales, climatic shifts and eras, smaller events
  (forest fires that spread, diseases), how they fit the world, and a central, general, clean, extensible scheduler where slower
  scales set the odds of faster ones and each has observable signs; both mechanical consequences and experience across land,
  individuals and salience; design only, nothing built. Written: this proposal and the exploration model.

- 23 Oct: Zach answered §Open 1-7 (D2-69 to D2-75): risks attached to things and emerging from the systems (a mill breaking or
  flooding, a neglected house collapsing on its people); fires across edges; signs across edges set by the edge's terrain; disease
  to flesh out; the area moves to 37.2. Added §11-§13.

## Sources

D4-4 to D4-7, D4-13, D4-17, D4-35, D2-5, D2-49, D2-50, D2-53, D2-66; spec/environment/*, spec/information/signs.md;
38.04 §3, 38.05 §1, 38.17 §1, §4; [seeing.md](seeing.md), [fuse_events.md](fuse_events.md), [layout.md](layout.md),
[knowledge.md](knowledge.md); `wp/environment`: docs/review/37_growth/04_environment.md, 04_environment_design.md;
`cybertron2/engine/run.py` (dawn, incidents); [02q_environment_model.py](../../review/37_growth/02q_environment_model.py).
