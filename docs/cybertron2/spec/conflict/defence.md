# Defence: walls, the watch, gates and time to respond

## Summary

Defence is people, multiplied by what they stand behind and by how early they know. Walls multiply the defence of those inside; a
watcher stays awake to detect first and wake the others. Events that take time (a break-in, a fire) can be detected before they
finish, and those who detect them get one urgent decision. A gate checks arrivals by its rule first, and otherwise the keeper and
the arrivals talk on the day they arrive.

## Decided

- D2-20: walls multiply the defence of those inside; a stone building is less likely to be picked in a node raid and stronger when
  it is.
- D2-21: the watch: a watcher skips the night's sleep and eats more for it, detects first and can wake the others; households
  rotate it; children can keep it.
- D2-5: fuse events (rare; only a subset of people woken); gates check arrivals automatically first, otherwise the keeper and the
  arrivals talk on the day they arrive.
- D2-49, D2-50: stone resists fire; fire kills those who do not get out, so waking in time is the defence (raids.md).

## Mechanics

- **Walls:** the structure of a building multiplies the strength of those inside who defend it; an empty building has only its
  break-in (D2-20).
- **The watch:** `watch` for the night (no sleep; eats more); the watcher detects a fuse event at once and may wake the others
  (D2-21). A child can keep it (D4-19's menial tasks).
- **Fuse events** (D2-5, D2-80 to D2-84): conflict/fuse_events.md. A raid is detected only by chance (a watcher, a dog, those
  inside, neighbours who hear it); a hut gives no call, a timber house one act, a stone one up to three; one call an agent a night,
  appended to its own conversation. No detection: the default applies (those inside defend asleep).
- **Gates** (D2-5): an enclosure's entry rule is checked at dawn; those it does not admit wait outside and talk with the keeper in
  the talk step; admitting takes effect at once.

## Data

Per building: structure (its multiplier). Per night: who watches where. Per gate: its rule and keeper.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| multipliers by structure | timber x1, stone x2 (proposed) | calibrate |
| the watcher's food | as working late, x1.5 (proposed) | calibrate |
| urgent calls per agent a night | 1 (conflict/fuse_events.md) | decided (D2-80) |

## What agents see

Whether they keep the watch tonight; being woken by something (smoke, noise, the watcher) with the choices it allows; a gate's rule
and its keeper as they know them.

## Open

- Overlapping events in depth (OPEN Q-19).
- Gate rules beyond the check (tokens, tolls, passes): proposals/gates.md.

## Sources

proposals/attacks_and_walls.md, fuse_events.md, gates.md; 02k.

*Current as of 24 Oct 2026: D2-5, D2-20, D2-21, D2-49, D2-50, D2-80 to D2-84.*
