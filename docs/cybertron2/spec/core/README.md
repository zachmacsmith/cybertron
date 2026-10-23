# Spec: core

The engine itself: how state changes, how a day runs, what is recorded. Owner: 37.4.

| File | Covers | Compiled from | State |
|---|---|---|---|
| [architecture.md](architecture.md) | state, modules, the chokepoint (primitives, apply, hooks), the cause stack | 38.07 | **written** (D4-1, D4-24, D4-34, D4-35) |
| events.md | the event log, causes, audiences derived from presence and room access | 38.07, 38.02 | to compile |
| [round.md](round.md) | the day: dawn, look, decide, talk, work, departures, night, memory; tie rules | 38.05, 02k | **written** (D4-8, D4-13, D4-14, D4-15, D4-25, D4-28) |
| randomness.md | seeded streams, common random numbers across arms | 38.README, 37.4 notes | to compile |
| records.md | run files, checkpoints, replay, versioning (when runs start to matter) | 38.07, 00_plan | to compile |
| world_spec.md | the format of a world file and what can be set by hand | 38.04 §4, 38.09 §3c | to compile |
