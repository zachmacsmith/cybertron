# 38.32: R2 of the run record built (resume, pause, cancel, replay)

Session 37.4, 24 Oct 2026. From spec/record/execution.md (D1-1, D1-2, D1-4); after R1 (38.29). Code: journal.py, run.py,
`__main__.py`. Tests: tests/test_cybertron2_journal.py (8); 160 cybertron2 tests pass.

## What was built

| execution.md | Built |
|---|---|
| answered requests are never asked again | `decide` looks the key up first; a recorded answer (or a recorded failure the run took as one) is reused, and the agent's conversation is rebuilt from it as it was |
| resume | `python -m cybertron2.engine resume RUN [--until STEP]`: the world is built from the journal's resolved spec and played again from day 0 with recorded answers; every committed step is checked against its checkpoint, not written again; the first step not committed is run live as a new attempt, earlier open attempts marked `aborted`; a `resume` segment is recorded with its first step and code sha |
| pause | `run ... --until STEP` and `resume ... --until STEP` stop after that step's commit |
| cancel | Ctrl-C or a kill leaves the open attempt `open` (marked `aborted` at the next resume); calls in flight finish and their answers are kept; nothing partial is committed |
| replay | `python -m cybertron2.engine replay RUN [--to STEP]`: in a scratch copy, the run is played from its record alone and every committed step's world state is compared byte for byte with its checkpoint, and every request's message with the one recorded; it reports the steps checked and the paths that differ |
| determinism | two causes found and fixed: Python's per-process string hashing (sets of names in world setup came out in a different order in each process; engine processes now run with `PYTHONHASHSEED=0`), and key-sorted JSON in the journal (a world rebuilt from a sorted copy of its spec iterates its people in another order; the journal now keeps dicts in the engine's order) |

Tests: a run killed in the night of day 3 resumes to the same state, days and memory files as an uninterrupted run, with that
step's attempts `aborted` then `committed`; a model run paused after `d1.decide` and resumed asks exactly as many calls as an
uninterrupted one and ends the same; replay checks every committed step and stops where asked.

## Differences from the spec, for 37.1

- Resume replays from day 0 rather than loading the last checkpoint: the checkpoints serve as the check that the replay is the same
  run. It costs only engine time (no calls), and needs no restoring of the runner's carried state. Loading a checkpoint directly is
  for fork (R4), where earlier answers are not all reused.
- A resumed agent's conversation is rebuilt from its recorded messages; on the CLI the next live call starts a new session with
  the whole conversation sent once (the conversation text is the same; the cache is not).

## Not yet

R3 (`context`, `play --as`), R4 (fork, rewind, replicates, interventions), R5 (views, export and import, publish), R6 (the site).

*Current as of 24 Oct 2026.*
