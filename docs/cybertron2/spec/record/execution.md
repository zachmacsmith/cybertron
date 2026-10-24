# Running a run: steps, requests and commits

## Summary

The runner is a state machine. It advances step by step; everything it needs from outside is a keyed request answered once;
everything that happens is written at once; a step's commit makes it official. Crash, cancel and pause all stop after the last
commit, and resume picks up from there without asking anything twice.

## Decided

- D1-1: running is idempotent, resumable and cancellable; a run can be paused at a chosen point.
- D1-2: everything is written as it happens; the commit only makes a step official; what happened up to a crash stays readable.
- D1-4: steps, attempts, keyed requests, responders, commits and replay as below.

## Mechanics

- **Steps.** A day is the fixed sequence of spec/core/round.md: `dawn`, `decide`, `talk.<wave>`, `work`, `settle`, `night`
  (with `fuse` calls), `memory`. A step key is `d<day>.<step>`.
- **Attempts.** Each run of a step is an attempt, numbered from 1. Its rows (requests, responses, events, changes) carry
  `(step, attempt)`.
- **Requests.** Everything the engine needs from outside is a request with the key `d<day>.<step>.<agent>.<n>`, where n counts
  that agent's requests within the step: a decision, a talk-step reply, a lighten reply, a fuse call, a memory. A request records
  exactly what the answerer is given (views.md: context). Requests and responses are written the moment they exist.
- **Responders.** A responder answers requests; the engine never knows which one did. Responders are assigned per agent, and per
  range of steps in a fork:
  - `recorded`: from a journal;
  - `model`: an LLM backend;
  - `bot`: scripted, for smoke tests;
  - `human`: human_play.md.
- **Idempotency.** Before asking, the runner looks the key up; an answered request is never asked again, whatever attempt asked
  it. The engine is deterministic given its answers (review 39.01 §5), so re-running a step reproduces it.
- **Commit.** At a step's end, one transaction writes the checkpoint and marks the attempt `committed`.
- **Crash or cancel.** The open attempt is marked `aborted` at the next start, and its rows stay. Resume loads the last committed
  checkpoint and runs the step as a new attempt, reusing every answer received. Cancel stops issuing requests, lets in-flight
  calls finish (their answers are kept) or drops them, and never commits a partial step.
- **Pause.** `--until <step key>` stops after that step's commit; `resume` continues. Waiting for a human is a pause.
- **Determinism rules** (checked by the replay test):
  - randomness only from `World.rng(seed, parts...)`;
  - answers are applied in key order, never in arrival order;
  - no wall-clock time, thread order or process state reaches the world's state.
- **Replay.** `replay` runs the record with the `recorded` responder and compares every checkpoint, event and change byte for
  byte. It also recomputes each request's message from the state and checks it against the recorded sha, which tests that the
  prompt code reads only the state.
- **Replay is promised within one code version** (the same sha and frozen data). Under other code see branching.md, `continue`.

## Commands

```
python -m cybertron2.engine run SPEC --out RUN [--until STEP] [--as NAME=model|bot|human]
python -m cybertron2.engine resume RUN [--until STEP]
python -m cybertron2.engine replay RUN [--to STEP]
```

## Parameters

| Parameter | Value | Status |
|---|---|---|
| step names | as above, from core/round.md | decided |
| in-flight calls at cancel | kept if they finish within a grace period | calibrate |

## What agents see

Nothing of this. A resume restores each agent's running conversation exactly, so an agent cannot tell a run was interrupted
(OPEN Q-RR2 for the alternative).

## Open

- OPEN Q-RR2: restore conversations exactly on resume (the default), or restart them at the resume day.
- OPEN Q-RR5: a test with shuffled completion order, to show nothing depends on arrival order.

## Sources

proposals/run_record.md §1, §7; review 39.01 §3, §5; cybertron 1: `cybertron/replay.py`, `runner.py`.

*Current as of 24 Oct 2026: D1-1, D1-2, D1-4.*
