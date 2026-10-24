# Branching: rewind, fork, replicates, interventions

## Summary

Any committed step of a run, local or fetched, can start a new run: the same history to that point, then other answers, other
interventions, or other draws.

## Decided

- D1-1: fork, rerun and continuing from any point, as cybertron 1 could.
- D1-4: as below.

## Mechanics

- **Rewind** `--to STEP`: a new run whose journal holds the parent's record up to that step's commit. The parent is never changed.
- **Fork** `--at STEP`:
  - restores the checkpoint at that step;
  - answers earlier requests from the parent's record;
  - applies the interventions at their steps;
  - plays on with the chosen responders.

  The new run's `segments` row names its parent and step.
- **Replicates** `--replicates K`: K forks that differ only by a salt added to the seed for draws after the fork point, so the
  history before is shared and the world's own chances after it differ. Model sampling differs naturally.
- **Interventions** are typed ops on primitives, applied through `World.apply` inside a cause of kind `intervention`, recorded
  as submitted and as applied (with a state-diff digest), and never applied twice. The spec's `script:` and `incidents:` are the
  same ops scheduled from day 0.
- **Under other code.** `continue RUN --at STEP` plays on from a checkpoint under the current code, recorded as a segment with
  both shas, with no claim that a replay would match. To reproduce under the run's own code, the runner checks out its sha in a
  temporary worktree (as cybertron 1's `rerun`).

## Commands

```
python -m cybertron2.engine rewind RUN --to STEP --out NEW
python -m cybertron2.engine fork RUN --at STEP [--apply iv.yaml] [--replicates K] [--as NAME=...] --out DIR
python -m cybertron2.engine continue RUN --at STEP --out DIR
python -m cybertron2.engine branches RUN
```

## Parameters

| Parameter | Value | Status |
|---|---|---|
| replicate seed salt | `rep<k>` appended to the seed's parts from the fork step | decided |

## What agents see

Nothing of the branching. An intervention is seen only as what it does in the world, where it happens.

## Open

None.

## Sources

proposals/run_record.md §7; cybertron 1: `cybertron/replay.py` (rewind, fork), `interventions.py`, `rerun.py`, `fetch.py`.

*Current as of 24 Oct 2026: D1-1, D1-4.*
