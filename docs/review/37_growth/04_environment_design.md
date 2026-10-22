# 37.4 Environment over time: revised design

*22 Oct 2026, branch `wp/environment`. Revises the brief [04_environment.md](04_environment.md) after reading the engine
(`subsistence.py`, `events.py`, `camptypes/fields.py`, `outside.py`, `interventions.py`, `features.py`). Progress is in
[04_environment_log.md](04_environment_log.md).*

## 1. The criterion

The brief lists things that happen. The project's rule (`scenario_design.md` §1) is that a mechanic earns its place only if it
changes who needs whom. So every piece of environmental variation here is chosen for **the institution it calls for**, and has to
pass one test: it creates a holder and a needer, or a problem one agent cannot solve alone. Random, small, symmetric losses fail the
test and are left out.

| Kind of variation | What it rewards | Institutions it calls for | Here |
|---|---|---|---|
| Predictable cycle | timing, storage | stores and granaries, a keyholder, seasonal labour | calendar (§3) |
| Covariate severity (a hard winter for everyone) | storage, rationing, foresight | granary rules, rationing, an almanac office | year draws (§3), foresight (§5) |
| Idiosyncratic shocks (one agent, one store, one plot) | pooling risk | mutual aid, credit, patronage, audits | micro-events (§4) |
| Windfalls | claiming | property rules, first-finder vs polity | micro-events (§4) |
| Endogenous damage (soil, game) | restraint | commons rules, enforcement, blame | trends (§6) |
| Exogenous drift (climate, threat) | reform | rule change, the frontier (37.5) | trends (§6) |

Two further principles shape the details:

- **Incidence over frequency.** Where a shock lands (on a holding, a faction, a role) matters more than how often shocks come. A
  shock that lands on one group's holdings makes politics; one that lands at random makes, at most, sympathy.
- **Legibility.** A trend agents cannot see is a parameter, not a problem. The world keeps an almanac agents can read.

## 2. Shape in the engine

One new module `cybertron/environment.py`, a feature row `environment` (spec key `environment`, off by default, `skip_off`), its
own RNG streams (`environment`, `environment-bot`). Off, it draws nothing, writes nothing and adds no prompt text, so every existing
world replays byte-identically. It needs `subsistence` (it acts on food, forests, fields and stores); a spec with environment on and
subsistence off is refused at generation.

**The schedule is drawn at generation** (`generate(sp, seed, inst)`) into `inst["environment"]`: the calendar's years and their
severity, every micro-event (round, type, parameters, a target draw `u`), and the exogenous trend paths. It is drawn from
`f"{seed}|environment|<part>"` streams that read nothing about the agents, the laws or the arm, so **every arm of an experiment with
the same seed gets the same schedule** (common random numbers). It is in the instance, so it is in the run's record.

**Targets are drawn as a uniform, not an id.** A micro-event stores `u` and a target rule (§4); at fire time the rule ranks the
candidates that exist and `u` picks one. Arms with the same population and holdings hit the same target; arms that differ hit the
corresponding rank (the richest store, the poorest agent). Exact pairing holds only for exogenous draws: endogenous trends (soil,
game) diverge between arms by design, and the record says which parts are paired.

**Hand-placed events** use the same entries: `environment.schedule: [{round, type, target: {...} | id, ...}]` is merged into the
drawn schedule (a hand-placed entry may name its target by id, by holding or by role). `environment.draw: false` keeps only the
hand-placed ones.

**Integration points** (each guarded by `environment` being on, so nothing moves when off):

- `subsistence._next_season`: with the calendar on, the season comes from the calendar instead of the random lean/normal/plentiful
  draw (its stream is not touched, so it is not consumed differently).
- `subsistence` ration and spoilage: a phase's `ration` and `spoil` multipliers.
- `camptypes/fields.py`: the sowing window (a gate on sow) and soil exhaustion (§6).
- `outside.py`: the threat trend scales demands.
- the round end: micro-events fire at round start (as world events do); the calendar advances at round end with the season.

## 3. The calendar (predictable cycle, covariate severity)

```yaml
environment:
  enabled: true
  calendar:
    year: 12                       # rounds per year; the run starts at `start` (a phase name)
    start: spring
    phases:                        # in order; rounds per phase sum to `year`
      spring: {rounds: 3, plants: 1.1, game: 1.0, sow: true}
      summer: {rounds: 3, plants: 1.3, game: 1.2, sow: true}
      autumn: {rounds: 3, plants: 0.9, game: 1.1, sow: false}
      winter: {rounds: 3, plants: 0.15, game: 0.5, sow: false, ration: 1.25, spoil: 0.6}
    years: {hard: 0.3, mild: 0.2}  # each year's severity, drawn at generation: hard / normal / mild
    severity: {hard: 0.6, mild: 1.3}   # multiplies every phase's plant and game regrowth in that year
```

- Plant and game regrowth follow the phase (through the existing `r` of each forest and the game multiplier). Crops can be sown
  only in `sow` phases; a crop sown late may not ripen before winter.
- Winter costs more food (`ration` 1.25) and food keeps better (`spoil` x 0.6). With 37.2's clothing or shelter, a `relief` item
  can bring the ration back to 1 (a hook, off until 37.2 lands).
- The cycle is predictable, so storing food through autumn pays; the year's severity is not, so how much to store is a real
  question, and knowing it early is worth something (§5).
- This replaces the brief's "lean season is predictable" with a cleaner split: **timing is known, severity is not.**

The ≤ 30% subsistence rule (`scenario_design.md` §4) is checked per phase: ≤ 30% outside winter, and winter has its own stated
ceiling (proposed 45%), or the calendar recreates the first batch's famines.

## 4. Micro-events (idiosyncratic shocks and windfalls)

Each type declares its kind, its target rule, its effect and its visibility; the existing visibility modes of `events.py` are
reused (public, discoverer, subset, delayed, rumour, none).

| Type | Kind | Target | Effect | Default visibility | What it calls for |
|---|---|---|---|---|---|
| `illness` | idiosyncratic | an eater (rank by `even`, or `poor`: the hungry fall ill more) | for `rounds` (2-4): one action fewer, forage and hunt x0.5 | public | mutual aid, sick relief, credit |
| `store_loss` | idiosyncratic | a store (rank by contents) | rats or damp: `loss` (20-40%) of its food | the owner or keyholders only | audits, the keyholder problem: the one who knows can hide it |
| `bumper_crop` | windfall | a growing crop (rank by holder) | its yield x2 when it ripens | the holder, at sowing's ripening | inequality between farms, a tithe |
| `stray_herd` | windfall | a forest | `food` (20-40) of large game there for `rounds`, first hunters take it | discoverer | knowing first, a claim: whose game is it? |
| `flood` | covariate, local | a fields camp | standing crops there lose `loss`; irrigated plots lose half | public | relief between farms, works (37.7) |

Target rules: `even` (uniform rank), `rich` / `poor` (weighted towards the top or bottom by a holding: food, plots, stores), `role`
(a class or office), `camp`. The default rate is about one micro-event per 2 rounds across all types, as the brief asked; the
dry runs will say whether that is noise at 16 agents (an agent is hit about once in 30 rounds).

Deferred to a second pass: a `traveller` (an outside trader offering a price for a few rounds: needs a trade action against the
outside, which 37.2's market may provide), contagion (illness spreading along trade or talk), a broken road (needs 37.5's roads).

## 5. Foresight (information as a chokepoint)

```yaml
environment:
  foresight: {right: foresight, lead: 4, accuracy: 0.8, events: [flood, store_loss]}
```

An agent holding the right `foresight` (granted in the spec, by a position, or by a law: so it can be an office) learns each year's
severity `lead` rounds before the year begins, correct with chance `accuracy` (else a wrong severity), and the covariate events
listed in `events` `lead` rounds before they strike. Everyone else learns severity as the year unfolds. This is the brief's "knowing
first is leverage", made into a seat someone can hold, sell, misuse or be removed from.

## 6. Trends

| Trend | Kind | Mechanism | Paired across arms |
|---|---|---|---|
| `climate` | exogenous | the chance of a hard year moves from `p` to `p_end` over the run | yes (drawn at generation) |
| `threat` | exogenous | the outside power's demand x (1 + `rate` x round) | yes |
| `soil` | endogenous | a plot harvested while its fertility is below `exhaust_below` loses `exhaust` of its fertility floor for good; recovers only with `rest` rounds of fallow | no |
| `game` | endogenous | the existing Allee threshold (`subsistence.game.allee`) switched on in environment presets: below it the herd collapses | no |

Endogenous damage can be pinned on someone, so it calls for restraint and blame; exogenous drift has no culprit and calls for
reform. A threshold (the Allee collapse) beats a linear decline: prevention has to be paid for before the damage shows.

**The almanac** makes trends legible: one state line (about 25 tokens) with the phase, rounds to winter and the last few years'
severity ("Winter in 4 rounds. Past winters: hard, mild, hard."), and a law read `almanac()` (phase, year, past severities and
harvest totals) so a law can, for example, raise a granary levy after two hard years.

## 7. Record

- `inst["environment"]`: the drawn schedule (years, events with their `u`, trend paths), so it is in the run's instance file.
- A monitor-only `environment_round` event per round: phase, severity, events fired with their resolved targets, trend values.
- `world_event_truth`-style entries for each micro-event (who was told, what is true), as world events already do.

## 8. Acceptance (dry runs, scripted bots, no model calls)

1. **Off is byte-identical:** the golden cases replay unchanged.
2. **Pairing:** the same seed under two arms that differ in laws and cast gives the same schedule hash; targets resolve to the same
   rank.
3. **Occurrence:** over 120 rounds, the phases, about one micro-event per 2 rounds, and the trends show in the flows check.
4. **It matters** (the README's "measure what the mechanic is for"), each a contrast between two scripted strategies on the same
   schedule:
   - calendar: a bot that stores in autumn against a myopic bot: fewer hungry winter rounds and deaths, by a stated margin;
   - illness: bots with a sick-relief rule against none: lower variance of hunger, fewer deaths;
   - foresight: a holder who stores by the forecast against one who does not;
   - soil: rotation or rest against continuous cropping over 60 rounds.
   If a contrast is not there, the mechanic does nothing and is recalibrated or cut.
5. **Subsistence share** ≤ 30% outside winter, ≤ the stated winter ceiling in winter.
6. **Prompt cost:** the environment's lines in a Haiku seat's view ≤ about 40 tokens.

## 9. Order of work

1. The feature skeleton, the schedule, pairing and the record (the interface 37.5 and 37.7 build on).
2. The calendar and the almanac, with the subsistence hooks.
3. Foresight.
4. Micro-events.
5. Trends.
6. Scripted strategies and the dry-run contrasts.

## 10. Open questions

- **Year length.** Runs are 30-120 rounds. A 12-round year gives 2.5-10 winters; an 8-round year gives more cycles but phases of 2
  rounds, which agents may not register. Proposed: 12, configurable.
- **Calendar replaces the random season** when on (the year's severity is the random part). The alternative, layering the random
  season on the calendar, adds variance without adding an institution it calls for.
- **Is the environment a treatment or noise?** As designed, it is noise held equal across arms (common random numbers). Varying
  harshness between arms (mild against harsh worlds) is a spec choice on top of this, not a separate mechanism.
