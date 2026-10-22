# 37.4 Environment over time

## Goal
A world that changes, so that institutions face new problems over long runs: seasons that matter, small events that create local
winners and losers, and long trends that force adaptation.

## What exists
- Subsistence draws a season each round that sets plant regrowth (`seasons: {lean: ...}`), scheduled shocks (blights on forests),
  rare forest shocks.
- World events (`events.py`, off by default in the regime worlds): camps discovered, camp functions changing, camps destroyed,
  blights, agents arriving and departing, rumours and delayed visibility.
- Outside power demands and raids.
- Interventions schedules for scripted events.

## Design
1. **Seasons with consequences:** a cycle (sowing, growing, harvest, winter) that sets farming windows, hunting yields, spoilage and
   need for clothing and stores (37.2). The lean season is predictable, so storage and granaries pay (37.7).
2. **Micro-events**, frequent and local, drawn per round from a seeded schedule: a fire in one store, a good harvest on one farm, a
   sick worker, a lost tool, a stray herd, a traveller with news, a broken road. Each creates a small local imbalance someone can
   exploit or relieve.
3. **Long-term trends:** soil depletion on overworked fields, game decline under hunting pressure, a drift in climate (more lean
   seasons over 100 rounds), a slowly rising outside threat, depleting mines. They force institutions to change, not just react.
4. **Information about events:** public, rumoured, delayed or known to the discoverer only (as world events already allow), so
   knowing first is leverage.
5. **Paired across arms:** the whole schedule is drawn from the seed at generation, so every arm of an experiment sees the same
   events (common random numbers), and its record is exported.

## Spec keys (sketch)
`environment.calendar {season_length, phases}`, `environment.micro {rate, types}`, `environment.trends {soil, game, climate,
threat}`, all with explicit per-world overrides and an intervention-style schedule for hand-placed events.

## Acceptance (dry runs)
- Over 120 rounds a world sees its seasons, about one micro-event per 2 rounds, and its trends visible in the flows check.
- The same seed gives the same schedule in every arm; the schedule is in the run's record.
- Subsistence stays ≤ 30% of actions outside lean seasons.

## Non-goals
Weather simulation; anything spatial.
