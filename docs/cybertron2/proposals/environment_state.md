# Proposal: the hidden state of places and things (shared variables that interact)

**Status:** discussion (23 Oct). Design only. **Owner:** 37.2. A companion to [environment.md](environment.md) (the scheduler)
and [environment_catalogue.md](environment_catalogue.md) (what can happen). **Affects:** spec/environment/ (a new file:
state.md), world/ (parcels, wells and waters: with 37.4), economy/ (buildings, livestock, production), life/ (health),
information/ (signs). **Model:** [02q_environment_model.py](../../review/37_growth/02q_environment_model.py) ("a cascade").

## Summary

Zach: risks should draw on **shared state that can interact**, so effects cascade: a flood raises the water table, latrines seep
into the well, a fever spreads. Proposed: every parcel, water, building, herd, person and node carries **a few hidden
variables** (a parcel's water table, a well's cleanness, a building's damp, a herd's health). Each relaxes toward a baseline and
is pushed by the weather, by incidents and by what people do. **Hazards read them** (the exposure term of D2-69), and incidents
**write them**, so one change reaches others through the state, one step a day. Each variable can show itself as **signs**, mostly
of low salience ("the bucket rope reaches less far"; "the grain smells musty"), noticed by attention or skill. It is realistic
and achievable with a small, fixed set of variables, damped updates and no same-day loops.

## 1. Is it realistic and achievable?

**Yes, within limits.** Games that do this well (Dwarf Fortress's contaminants and miasma, RimWorld's temperature, dirt and
infection, Banished's nutrition and disease) keep each variable simple and let the variety come from couplings. The risks are
runaway loops, untraceable chains, and a cost in prompts. The guardrails (§6) address each. The demo below runs one cascade in
about 40 lines.

## 2. The variables

Each is a number in a small range with a baseline it relaxes toward. Proposed first set (about six per kind of thing):

**A parcel (land):**

| Variable | Moved by | Read by (hazards, systems) | Signs (salience) |
|---|---|---|---|
| **water table** | wet and dry spells, floods, drainage (ditches, D2-66) | floods on low ground, crops' water, wells, foot rot | "the bucket rope reaches less far" (0.1); "the ditches are full" (0.3); standing water (0.6) |
| **surface water** (dry, damp, flooded) | the water table, rain, the river | crops drown, buildings damp, fords, flux | "the low field is under water" (0.8) |
| **fertility** (exists) | cropping, manure, silt after a flood | yields | a crop's look (0.3) |
| **fuel dryness** (woods, scrub, grass) | dry spells, season | wildfire | "the bracken is brittle" (0.2) |
| **vegetation** (plants, pasture: exists as stock) | growth, grazing, fire, felling | forage, grazing, erosion | "the grass is grazed to the earth" (0.4) |
| **soil cover against erosion** (slopes) | vegetation, felling, fire, terraces | landslides, silt in streams | "the slope is gullied" (0.3) |
| **pest load** (per crop kind) | season, the same crop twice, wet, a new pest's arrival | blight, crop pests | "a few beetles on the beans" (0.15), then "the leaves are eaten through" (0.5) |
| **contamination** (spores, a carcass's taint) | dead beasts left, blight, a flood's mud | anthrax, blight returning, flux | none until harm: a smell near a carcass (0.3) |

**A water (a well, a spring, a stretch of river at a node):**

| Variable | Moved by | Read by | Signs |
|---|---|---|---|
| **level** | the water table, spells, upstream floods | mills (flow), irrigation, wells running dry, fords, floods | "the river is high and brown" (0.6); "the well is low" (0.2) |
| **cleanness** | latrines and middens nearby (people's choices), floods mixing water, carcasses upstream, burials upstream | flux, fever, cattle health | "the water tastes off" (0.2); a sheen or smell (0.3) |

**A building:**

| Variable | Moved by | Read by | Signs |
|---|---|---|---|
| **condition** (exists) | upkeep, gales, snow load, age, fire | breaks, collapse (D2-71) | "the roof sags" (0.4); "a crack in the wall" (0.3) |
| **damp** | surface water, wet spells, a lit hearth dries it, stone or wattle | spoilage of stores, rats, coughs | "the grain smells musty" (0.25) |
| **vermin** (rats, mice) | full stores, damp, wattle, time | store losses, plague in a pestilence era | "droppings in the bins" (0.2); rats seen by day (0.5) |
| **filth** (waste, crowding) | people sleeping there, cleaning (work), a midden by the door | coughs, fever, flux | "the house stinks" (0.3) |
| **heat** (exists as the fire lit) | the hearth and fuel | the cold rules (H-5) | warmth felt (0.5) |

**A herd:**

| Variable | Moved by | Read by | Signs |
|---|---|---|---|
| **condition** (fed and fit) | grazing, fodder, winter, work | milk, breeding (D4-44), murrain, wolves' choice of prey | "the cows are thin" (0.4) |
| **sickness** (infection) | contact with sick herds, wet pasture, crowding, a bought beast | murrain, foot rot, death | "the cows are off their feed" (0.3, a herder sees it at 0.1) |
| **restlessness** | hunger, fences down, wolves near | straying and escapes | "the cattle are pressing at the fence" (0.4) |

**A person** (with 37.1's life): **health** (sickness and immunity per disease), **hunger** (exists), **exhaustion** (exists:
working late), **wounds** (exists), **exposure** (a night out in the wet or cold). Signs: their own body ("you are feverish",
salience 0.9 to them), seen by others ("Wat is coughing", 0.5 to those near).

**A node:** **crowding** (people for its houses), **waste** (grows with people and time; cleared by work), **contact** (travellers
and markets: how much comes in from elsewhere). These are mostly sums of the above.

## 3. How the state moves

- **Once a day, in a fixed order** (the scheduler's dawn step, environment.md §8): each variable relaxes toward its baseline
  (`v += rate x (baseline - v)`), then takes its pushes (the day's spell, the season, incidents of the day before, what people did),
  then is capped to its range.
- **Effects travel one step a day.** A change made today is read tomorrow, so a cascade unfolds over days (the flood, then the
  seep, then the fever), never in a loop inside one day. That keeps it deterministic, traceable and stable.
- **Each process declares what it reads and writes**, so the couplings form a graph the engine can print and check.
- **Hazards read variables** as their exposure term (D2-69): a flood's hazard on a parcel reads its water table; flux reads the
  well's cleanness and the house's filth; murrain reads herd sickness and contact; a collapse reads condition.
- **Incidents write variables:** a flood raises surface water and lays silt (fertility up) and mud (cleanness down); a fire sets
  vegetation and fuel to nothing and condition down; a dead beast left lying raises contamination.
- **People's acts write them too** (internal consequences, D4-4): where a latrine or midden is dug, felling a slope, overgrazing,
  burying the dead upstream, cleaning a house, ditching a field, salting meat, mending a fence.

## 4. Cascades it gives without special rules

| Start | Through the state | End |
|---|---|---|
| a wet spell | water table up, then latrines seep into the well (cleanness down) | flux in the households that draw from it |
| a wet spell | damp in the stores, then vermin up | store losses; plague in a pestilence era |
| a drought | fuel dryness up | wildfire; then soil cover down on burnt slopes; then the next wet spell washes silt into the river; then the mill's leat silts up |
| a drought | pasture down, then herd condition down, herds moved to shared wet pasture (contact up) | murrain spreads; hungry wolves take the weak beasts |
| a growing village | crowding and waste up, cleanness down | coughs and flux in winter, until someone organises a midden and a clean well (an institution) |
| a neglected roof and a snow spell | condition low, snow load | collapse on the sleepers (D2-71) |
| a flood | silt (fertility up) and mud (cleanness down) | a good harvest next season and a sick summer |

**The demo** (02q, "a cascade"): the same 10-day wet spell at a node of 18.

| Case | Water table (peak) | Days flooded | The well at worst (1 = clean) | Flux at its peak |
|---|---|---|---|---|
| latrine near the well | 0.91 | 5 | 0.64 | 4 sick of 18 |
| latrine away from the well | 0.91 | 5 | 0.93 | 1 sick of 18 |
| a dry spell instead | 0.29 | 0 | 1.00 | none |

The weather is identical in the first two rows; the difference is a choice people made about where to dig. That is the point of
shared state: **the environment and people's choices meet in the same variables.**

## 5. What people notice

- **Every variable may have signs** at thresholds or on change, with a sense, a range and a salience (environment.md §7). Most are
  low: who notices that the water table rose? The bucket rope does (0.1). The fever is not low.
- **Skill reads low signs** (knowledge.md): a well-digger reads the water table, a herder the herd's sickness, a farmer pests, a
  mason a crack. Attention to a thing (seeing.md) raises what is seen.
- **People can make low signs legible:** a flood mark on a post, a tally of the well's depth, an elder who remembers the last
  murrain, a written record. These are small practices and offices, and they matter only because the state is hidden.
- **What is never shown:** the numbers. An agent hears "the well water tastes off", never "cleanness 0.64".

## 6. Guardrails (what keeps it achievable)

1. **Few variables:** about six per kind of thing in the first worlds; a new one only with a hazard that reads it and a sign.
2. **Damped:** every variable relaxes toward its baseline, so no loop runs away; caps on every range.
3. **One step a day:** reads see yesterday's values; no same-day loops.
4. **Declared couplings:** each process lists what it reads and writes; the engine prints the graph and refuses a cycle within a
   day.
5. **Tested:** each variable has a unit test (it relaxes, it is pushed, it is capped); dry runs report each variable's range and
   each cascade's frequency against a target; sensitivity runs perturb one coupling at a time.
6. **Traced:** the truth log records every variable each day and every hazard's inputs, so a death from flux can be traced back to
   the wet spell and the latrine.
7. **Cheap in prompts:** variables never reach the prompt; only signs, through perception's budget.

## 7. Layers below people's reach (explored 23 Oct)

Zach: should there be layers people cannot touch directly, such as groundwater and river systems, that still drive causes? Yes:
the hidden state sits on **carriers** at several scales, and some carriers are below anyone's reach. People change them only
indirectly (a well draws on the groundwater; clearing a slope speeds the runoff).

| Layer | Carrier | Hidden variables | People reach it by | Links to other layers |
|---|---|---|---|---|
| **the sky** | the region (eras, years, spells: environment.md) | moisture, temperature, wind, storminess | never | rain feeds the soil, the groundwater and the river; dry spells dry the fuel |
| **groundwater** | each node (one aquifer; parcels sit higher or lower on it) | water table, recharge, cleanness | wells (drawing), latrines and graves (fouling it), drainage ditches (lowering it) | feeds springs, wells and the river's low flow; floods low parcels when high; carries a latrine's filth into a well |
| **the river** | a reach for each node it runs through, joined downstream along edges (generation's drainage, D4-22) | level and flow, silt, cleanness | mills, weirs and leats (taking flow), waste and carcasses thrown in, fords and bridges | its level floods the low parcels; its flow turns mills; what goes in upstream arrives downstream a day later (D2-78: flow) |
| **wetland** (fen, marsh) | its parcels | how wet, how far it holds water back | drainage (a works project) | holds flood water back (a drained fen floods the land below); breeds fen fever while wet |
| **soil** | each parcel | moisture, fertility, depth on slopes, salt (after a sea flood), spores and taint | ploughing, manure, rotation, terraces, burning | moisture from rain and groundwater; erosion when cover is lost; silt to the river |
| **living things** | parcels and nodes | vegetation (biomass, fuel dryness), game, predators (wolves as a moving population), pests per crop kind, pathogens and their reservoirs | felling, grazing, hunting, burning, rotation, killing wolves | fuel to fire; game to hunting; pests to crops; reservoirs to disease |
| **the built** | buildings, fittings, wells, latrines, middens, channels | condition, damp, vermin, filth, heat; a well's depth; a latrine's fullness | building, upkeep, cleaning | damp from groundwater and rain; vermin from stores; filth from crowding |
| **animals** | herds | condition, sickness, restlessness | herding, feeding, keeping apart, slaughter | sickness from contact and wet pasture; some sicknesses reach people (anthrax from carcasses, fever from sick cows' milk) |
| **people** | persons | health and immunity per disease, nutrition (how varied their food is), hunger, exhaustion, wounds, exposure | eating, resting, nursing, keeping apart | disease from water, air, contact, vermin and animals |
| **the node** | each node | crowding, waste, contact with outsiders | building houses, clearing waste, gates | sums of the above |

**Causal paths that cross layers** (none needs a special rule):
- rain, then the soil, then the groundwater, then **springs and wells**, then the river's low flow; in a drought the chain runs
  dry from the top: **wells fail before the river does**;
- clearing or burning a slope, then faster runoff, then **higher floods downstream** and silt in the river and the mill's leat;
- draining a fen, then a lower water table: **less fever here, more flooding below**;
- a tanner or a slaughterhouse upstream, then a fouled river downstream: **a dispute between nodes**;
- latrines and graves near the well, then the groundwater, then **flux**;
- a varied diet (milk, meat, legumes, bread), then better health (resistance to coughs and fever); a winter on grain alone weakens.

## 8. Water: a need people do not have yet

**It is an oversight that no one needs water.** Not as a labour cost: fetching water for a household of 5 costs about 0.1 units a
day from a well at the house, 0.2 from the village well, 0.4 from the river below the village and 0.8 from a spring a kilometre
off (0-4% of three adults' work). It matters through:

1. **where people can live:** a node or a house needs a source; sites with water are worth more;
2. **reliability:** in a drought wells and springs fail (the water table falls below them), so people walk farther, deepen the
   well, or move;
3. **cleanness:** the main road for disease (flux, fever) runs through water;
4. **what it enables:** bucket lines against fire need water near (D2-50), herds need water on their pasture, mills and irrigation
   need flow.

**Proposed:** water is **not an item carried about**. Each household (and herd) draws on a **source** it can use at its node (a well,
a spring, the river), paying a small daily cost in units by distance, and drinking whatever that source's cleanness is. If its
source fails, it must use another (farther) or go without (thirst: worse than hunger, a few days). This adds no daily decisions
unless something goes wrong.

| Source | What it is | Cost to make | Fails when | Cleanness |
|---|---|---|---|---|
| **a well** (a fitting on a lot or a site) | a shaft down to the water table, best lined with stone | digging by depth (the water table: about 10-40 units), a stone lining (about 4 stone) | the water table falls below its bottom (a drought): deepen it | from the groundwater; fouled by latrines, middens and graves within reach; an unlined well also by surface water |
| **a spring** | where groundwater meets the surface (the foot of a hill) | none | a long drought | usually clean |
| **the river** | always there at a river node | none | almost never | whatever comes from upstream |
| (later) a cistern | rainwater stored | stone, a roof | a dry spell | clean if kept covered |

**A shared well is a commons:** who digs it, who keeps it clean, who may draw, and what happens to whoever fouls it (or poisons it:
a crime with a cause the engine records) are for people to settle.

## 9. Latrines and middens

| Thing | What it is | Cost | What it does | Risks |
|---|---|---|---|---|
| **a latrine** | a pit, a small build at a lot | about 2-3 units; dug anew when full (about a season for a household) | keeps waste off the ground: without one, the node's **filth** rises, and with it flies and flux | it **seeps into the groundwater** within reach, more when the water table is high: placement against the well is what matters (the demo) |
| **a midden** | a heap of scraps, ash and dung at a lot | none: it grows by itself | **manure:** carted to the fields it raises fertility (a source of dung besides cattle) | rats and flies (vermin, disease), smell; fouls a well nearby |

So waste is both a hazard and a resource: carting the midden to the fields is a job, and who may take a village's waste, where
latrines may be dug, and where the tanner and the butcher may work are the first rules of a village's sanitation, an institution
the engine does not need to name.

## 10. The first set of variables

About sixteen in all, chosen because each has a hazard that reads it and a sign:

| Carrier | Variables |
|---|---|
| region | moisture, temperature, wind (from the spell) |
| node | water table, groundwater cleanness, crowding, waste |
| river reach | level, cleanness, silt |
| parcel | soil moisture, fertility (exists), fuel dryness, vegetation (exists), pest load |
| building | condition (exists), damp, vermin |
| well, latrine, midden | depth or fullness; distance to the well (fixed by placement) |
| herd | condition, sickness |
| person | health and immunity per disease, nutrition |

## Why

- It gives cascading, interacting effects from a few general rules, which is what makes a world feel alive and makes foresight,
  skill and institutions (a clean well, a midden, a flood mark, a herd kept apart) pay.
- It puts the environment and people's choices in the same state, so consequences are partly earned.
- It fits the scheduler (D2-69: exposure) and the separation of external and internal change (D4-4): the scheduler draws the
  weather and incidents; the state is the world's physics.

## Alternatives considered

- **Independent hazards with fixed odds:** simpler, but no cascades and no reason for prevention.
- **A full physical simulation** (hydrology, epidemiology): far more than needed, and untraceable.
- **Many variables per thing:** richer but unstable and costly; start small and add with evidence.

## Open questions (for Zach)

1. The carriers and layers of §7, including groundwater per node and the river as reaches joined downstream?
2. Water as a need met by a source (well, spring, river) at a small daily cost by distance, drinking the source's cleanness; no
   water item (§8)?
3. Wells, latrines and middens as things people place (§8-§9), with the midden as manure?
4. The first sixteen variables (§10)?
5. Effects one step a day, damped and capped, with declared couplings (§3, §6)?
6. Nutrition from a varied diet as a health factor (§7)?

## History

- 23 Oct: Zach: risks should draw on shared state that can interact (a flood raising water levels, contamination, infection);
  parcels, buildings and cattle with many often-invisible parameters; cascades; is it realistic and achievable; signs, some very
  low salience. Written: this proposal and the cascade demo in 02q.

- 23 Oct: Zach: which hidden variables and which carriers (nodes, parcels); layers people cannot touch (groundwater, rivers) that
  still drive causes; wells, latrines and middens; no one needs water, an oversight? Added §7 (layers and cross-layer paths), §8
  (water as a need through sources), §9 (latrines and middens), §10 (the first sixteen variables).

## Sources

[environment.md](environment.md) (D2-69 to D2-75), [environment_catalogue.md](environment_catalogue.md), [seeing.md](seeing.md),
[knowledge.md](knowledge.md), [layout.md](layout.md); spec/environment/resources.md (D4-7), D4-4, D2-66, D2-71;
[02q_environment_model.py](../../review/37_growth/02q_environment_model.py).
