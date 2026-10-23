# Visibility: what a place and the day let the senses reach

## Summary

Every place has a visibility for each sense: how much it lets through. It is not stored: it is computed each day from the
environment (the land's cover and state, smoke, what is making noise, the weather), and multiplies every sign of that sense noticed
there. Light enters only for what happens at night, since the day's notices are taken by day. Smell comes later.

## Decided

- D2-99: visibility per place and sense (sight, sound) multiplies every sign; set by cover, changed by the land's state and by rain,
  snow and fog; light only for night events, the watch and working late.
- D2-100: loud things mask quieter sounds near them and carry further.
- D2-101: smell later, simple: its own salience and a short reach, no multipliers, no wind direction (OPEN L-3, L-4).
- D2-102: a thing's conspicuousness is its own x the place's sight (information/noticing.md).
- D2-103: visibility is computed each day from the environment, not stored.

## Mechanics

**sight = cover base x the land's state x the day's weather (x light, at night only)**
**sound = land base x the day's weather x masking (x1.2 at night)**

### Cover base (data on each cover kind and road terrain)

| Cover | Sight | Sound |
|---|---|---|
| open field, pasture, open plain, farmland | 1.0 | 1.0 |
| built ground | 0.7 | 1.0 |
| marsh | 0.6 | 1.0 |
| scrub, hills | 0.5 | 0.9 |
| woodland | 0.35 | 0.7 |
| dense forest, a gorge | 0.2 | 0.7 |
| inside a building | its room only | walls x0.5 |

### The land's state

| State | Effect |
|---|---|
| a wood felled or burned | to scrub (0.5), then open (1.0) when cleared |
| land left to regrow | back over seasons: field, scrub, wood |
| a grain crop standing high (late summer to reaping) | that field's sight 0.5 |
| snow lying | things on the ground x0.5; tracks x3 (information/noticing.md) |
| smoke (a fire, a burning, charcoal burners, a smithy at work): a state that lasts the day | sight x0.7 in that parcel |

### The day's weather (environment/scheduler.md, "The day's weather")

| Weather | Sight | Sound |
|---|---|---|
| clear | x1 | x1 |
| rain | x0.8 | x0.7 |
| heavy rain | x0.6 | x0.5 |
| fog | x0.3 | x1 |
| snow falling | x0.5 | x0.7 |
| gale | x0.9 | x0.5 |
| **at night only** | x0.1 (x0.25 under a full moon; near a fire, its light) | x1.2 |

### Masking (D2-100)

Each place has a loudness from what is there that day: **very loud** (a waterfall or weir, a fight, a horn, a crowd at a fair) or
**loud** (a mill or smithy at work, a market, a gale). Quieter sounds there are heard x0.3 near something very loud, x0.6 near
something loud. A very loud sound is heard across the node, and at the far end of an edge if its kind carries (D2-74).

## Data

Per cover kind and road terrain: sight and sound bases. Per place and day: computed, not stored (D2-103). Per sign: its sense.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| bases, state effects, weather, night, masking | above | proposed (D2-99); calibrate |

## What agents see

Nothing of the numbers: only what they notice, and the weather and land as signs ("a thick fog lies on the valley").

## Open

- Smell (OPEN L-3); wind direction (OPEN L-4).

## Sources

[proposals/visibility.md](../../proposals/visibility.md), [environment_state.md](../../proposals/environment_state.md).

*Current as of 23 Oct 2026: D2-99 to D2-103.*
