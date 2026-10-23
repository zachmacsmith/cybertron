# The scheduler: external change

## Summary

External change is drawn from the seed by one central scheduler, the same in every arm of an experiment, and kept apart from the
internal consequences of what people do. It runs in layers (eras, years, spells, incidents, spreads), each setting the odds of the
next. Every draw is keyed by kind, place and day. Things carry their own risks, raised by neglect. Fires and some signs can cross
edges, as the edge's terrain allows.

## Decided

- D4-4: external change is separate from internal consequences: eras, cycles and incidents drawn from the seed, the same in every
  arm, one central scheduler; depletion, exhaustion and collapse are the resources' own physics (environment/resources.md).
- D4-5: three time scales, each modulating the one below: eras and trends, cycles, incidents.
- D4-6: signs are kept separate from effects (information/signs.md).
- D2-69: the layers (eras, years, spells, incidents, spreads), each setting the odds of the next; hazard = base x weather x season
  x land kind x exposure.
- D2-70: draws keyed by kind, place and day; exposure from local state.
- D2-71: risks attach to things and rise with neglect; incidents also emerge from the systems.
- D2-72: fires spread with the node's conditions, and between nodes when large and the edge suits.
- D2-73: eras are starting conditions in the first worlds.
- D2-74: some signs carry between nodes, as the edge's terrain allows (amends D4-35).

## Mechanics

- **One scheduler** draws every external change from the world's seed, so two arms of an experiment meet the same weather and the
  same draws on the same days (D4-4).
- **Layers** (D2-69): an **era** (a regime of moisture and temperature, and of disease, ecology and outside pressure) sets the odds
  of each **year's** severity; the year and the season set the odds of each day's **spell** (dry, wet, normal, cold snap, storm);
  the spell, the season, the land kind and the place's own state set the odds of **incidents**; an active incident can **spread**
  to neighbouring places with its own odds. Eras, years and spells read nothing agents do and are drawn for the whole run at
  generation. In the first worlds the era is a starting condition and does not change within a run (D2-73).
- **Hazard** (D2-69): for each kind and each place it can happen at, each day: base x weather x season x land kind x exposure. An
  incident happens when the draw U(seed, kind, place, day) falls below it (D2-70).
- **Risks of things** (D2-71): a kind of object (a building, a fitting, a store, a herd, a crop, a road, a mine) may carry risks in
  its data, each with a hazard that rises with missed upkeep and with conditions (a flood for a mill's wheel; a gale for a roof).
  A neglected house can collapse and injure those inside. A new object brings its own risks.
- **Across edges** (D2-72, D2-74): a large fire can spread along an edge whose terrain carries it (woodland), not one that stops it
  (a river, bare ground, a ridge above the tree line); a sign may carry to the far end of an edge if its kind carries (smoke,
  flames at night, a beacon) and the edge's terrain lets it (far on open plains, not over a ridge or through forest).
- **Incidents happen at a place** (D4-35) and make their changes through the engine's primitives (core/architecture.md), each
  recorded with the scheduler as its cause; signs go to the event log at their places and reach people through perception.
- A world file may pin eras, years, spells and incidents by hand, scale or turn off any kind.

## Data

Eras, years and spells for the run (drawn at generation, in the record). Per kind (data): where it can happen, its hazard's base
and drivers, how it spreads (adjacency, contact, carriage, flow, track, place-bound), its effects and its signs. Per object kind:
its risks. Per incident: day, place, kind, parameters, cause. Per edge: what it carries (terrain), from world/edges.md.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| eras, dwell times, the year's spread, spell odds and lengths, every kind's base and drivers | proposals/environment.md; 02q | calibrate |

## Open

- The catalogue of kinds for the first worlds (proposals/environment_catalogue.md).
- Edge terrain data (world/edges.md, 37.4) for fires and signs across edges.
- Disease: mortality, units of the sick, immunity, nursing (with 37.1): to flesh out.

## Sources

38.04 §3; devlog 37.4 #4-#6; proposals/environment.md, environment_catalogue.md; 02q_environment_model.py.

*Current as of 23 Oct 2026: D4-4 to D4-6, D2-69 to D2-74.*
