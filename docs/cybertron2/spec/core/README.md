# Spec: core

The engine itself: how state changes, how a day runs, what is recorded. Owner: 37.4.

| File | Covers | Compiled from | State |
|---|---|---|---|
| architecture.md | state, modules, the chokepoint (primitives, apply, hooks), the cause stack | 38.07 | to compile |
| events.md | the event log, causes, audiences derived from presence and room access | 38.07, 38.02 | to compile |
| round.md | the day: dawn, look, decide, talk, work, departures, night, memory; tie rules | 38.05, 02k | to compile |
| randomness.md | seeded streams, common random numbers across arms | 38.README, 37.4 notes | to compile |
| records.md | run files, checkpoints, replay, versioning (when runs start to matter) | 38.07, 00_plan | to compile |
| world_spec.md | the format of a world file and what can be set by hand | 38.04 §4, 38.09 §3c | to compile |
