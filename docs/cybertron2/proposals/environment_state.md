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

1. Shared hidden variables on parcels, waters, buildings, herds, people and nodes, as in §2?
2. The first set of variables (about six per kind)?
3. Effects one step a day, damped and capped, with declared couplings (§3, §6)?
4. Wells, latrines and middens as things people place (a well a fitting or a site; a latrine a small build), so their placement
   matters?
5. Which cascades to aim for in the first worlds (proposed: water to flux, damp to vermin, drought to fire to silt, drought to herds
   to murrain, crowding to coughs)?

## History

- 23 Oct: Zach: risks should draw on shared state that can interact (a flood raising water levels, contamination, infection);
  parcels, buildings and cattle with many often-invisible parameters; cascades; is it realistic and achievable; signs, some very
  low salience. Written: this proposal and the cascade demo in 02q.

## Sources

[environment.md](environment.md) (D2-69 to D2-75), [environment_catalogue.md](environment_catalogue.md), [seeing.md](seeing.md),
[knowledge.md](knowledge.md), [layout.md](layout.md); spec/environment/resources.md (D4-7), D4-4, D2-66, D2-71;
[02q_environment_model.py](../../review/37_growth/02q_environment_model.py).
