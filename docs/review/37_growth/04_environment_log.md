# 37.4 Environment over time: work log

Branch `wp/environment`. The brief is [04_environment.md](04_environment.md); the rules for every package are in the
[README](README.md) and `docs/scenario_design.md`. Newest entries at the top of the log. Pushed after each step.

## Status

Paused at Zach's question, waiting on whether to go on with the engine wiring or settle the design first. Step 3 in progress:
`cybertron/environment.py` drafted (committed as work in progress; registered only in settings.TARGETS, not yet in features,
schema, event types, the generator or the subsistence hooks, so nothing calls it and every world is unchanged).

## Plan

1. Read the engine where 37.4 attaches.
2. Revise the design (a section in this file, then folded into 04_environment.md): every kind of variation is chosen for the
   institution it calls for, not added for colour.
3. The event interface first (targets, visibility, record, pairing across arms), since 37.5 and 37.7 build on it.
4. Then the content: a calendar, micro-events, trends, foresight.
5. Dry runs with scripted bots: a strategy suited to each kind of variation must beat a myopic one; the 30% subsistence check per
   season.

## Working position (from the review of the brief, 22 Oct)

- **Test for every event type:** it changes who needs whom (a holder and a needer), or poses a problem one agent cannot solve
  alone. Random, small, symmetric losses are noise.
- **The kind of variation decides the institution it calls for:**

  | Variation | Rewards | Institutions |
  |---|---|---|
  | idiosyncratic (one agent, one plot) | pooling risk | mutual aid, credit, patronage, reciprocity |
  | covariate (everyone at once) | storage, outside trade | granaries, rationing, a keyholder |
  | predictable cycle | timing | stores, calendars, seasonal labour |
  | endogenous damage (soil, game) | restraint | commons rules, enforcement, blame |
  | exogenous drift (climate, threat) | reform | rule change, the frontier (37.5) |

- **Incidence matters more than frequency:** a shock that falls on a faction's holdings makes politics; a random one does not.
- **Windfalls** (a stray herd, a traveller's offer, a find) raise "whose is it?", a contest over property rules.
- **Trends must be legible** (a record of past seasons), or they are a parameter agents never see. Thresholds (the game's Allee
  effect already exists) beat linear drift.
- **Foresight as a chokepoint:** an office that gets an early, noisy signal of the next season or shock.
- **Pairing across arms** only works for exogenous draws, and targets must be drawn as a uniform mapped onto what exists, not by id.
- **Acceptance** should test that the variation matters (a suited scripted strategy beats a myopic one), not only that it occurs.

## Log

- **22 Oct.** Draft of `cybertron/environment.py`: the schedule drawn at generation (year severities, micro-events with a rank
  draw `u`, a hash of the paired part), the calendar (12-round year, timing known, severity announced in autumn; winter ration
  x1.25, spoilage x0.6, no sowing in autumn or winter), five micro-events (illness, store_loss, bumper_crop, stray_herd, flood),
  the foresight right, the almanac state line and law reads, the climate trend (off by default). Not wired or tested yet. Open
  choices it fixes for now: a 12-round year; the calendar replaces the random lean/plentiful season.

- **22 Oct.** Revised design written ([04_environment_design.md](04_environment_design.md)). Main decisions: one module
  `environment.py` behind its own feature row, off by default; the whole schedule drawn at generation from streams that read
  nothing about agents or arms; targets drawn as a uniform and resolved by rank at fire time; a calendar where timing is known and
  each year's severity is not; foresight as a grantable right (an office can hold it); micro-events limited to five types that pass
  the who-needs-whom test; trends split into exogenous (paired) and endogenous (not paired); acceptance by contrasts between
  scripted strategies. Engine read: seasons are drawn in `subsistence._next_season` from their own stream; world events in
  `events.py` pick targets with `rng.choice` over the current pool, which does not pair across arms that differ in population.

- **22 Oct.** Branch and this log created. Review of the brief written (the working position above).
