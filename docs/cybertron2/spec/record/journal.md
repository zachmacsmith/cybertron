# The journal

## Summary

A run is one journal file holding everything that entered the world from outside, the checkpoints of its state, and the logs of
what happened. Values are JSON; repeated texts are stored once; the file is SQLite.

## Decided

- D1-1: the record supports everything listed in README; nothing it needs may be left only in memory or in text.
- D1-4: the journal holds the run's inputs (code version, frozen data, resolved spec, seed, every answered request, every
  intervention), a checkpoint at each committed step, and every event and change with its cause.
- D1-5: one SQLite file per run (`run.db`, WAL mode); values are JSON text; prompts, schemas and other repeated texts are
  content-addressed and compressed; Parquet only at export.

## Mechanics

- **Inputs** are enough to replay the run under its own code:
  - the code: git sha, dirty flag and diff sha, a sha per `cybertron2` module, python;
  - the frozen data tables: every engine table the run read (PHYSICS, ITEMS, TECHNIQUES, COVERS, fittings, signs, ...), copied
    at the start, with every read during the run going through the copy;
  - the resolved spec (after `base:` merges and generation) and the seed;
  - every answered request (execution.md) and every intervention (branching.md).
- **Checkpoints** hold the whole `World.s` plus the runner's own state (each agent's running conversation: start day, frozen
  system text and schema, messages; the cost so far; the lists carried between steps), as compressed JSON, at every committed step
  (execution.md).
- **Events** are every `World.event` call. Today they are cleared at dawn; they are written to the journal before they are cleared.
- **Changes** are every `World.apply` call: the primitive, place, arguments, cause {actor, verb, for, node} and result, in order.
  Every change of physical state passes through `apply`. The knowledge stores (`mind`, `know`) are written by perception, which is
  a function of the state and the events; they are rebuilt by replay and captured by checkpoints, and are not logged as changes.
- **Writing:** each row is written when it happens, tagged with its step and attempt (execution.md). The file stays readable while
  a run writes.

## Data

| Table | Columns (all JSON values as text) |
|---|---|
| `meta` | key, value: provenance, spec, seed, schema version, log format |
| `data` | table name, frozen content |
| `segments` | id, kind (start, resume, rewind, fork, continue), first step, code sha, parent {run, step}, responders per agent |
| `steps` | step key, attempt, status (open, committed, aborted), started, ended, checkpoint sha |
| `requests` | key, step, attempt, agent, kind, conversation id, index in it, system sha, schema sha, message sha, responder |
| `responses` | key, attempts [{raw text, error, latency}], parsed reply, thinking, usage, transport |
| `blobs` | sha256 (first 16 hex digits), compressed text |
| `checkpoints` | step key, attempt, compressed JSON of the state and the runner's state |
| `events` | id, day, step, attempt, place, kind, actor, target, about, concerns, text, cause, extra |
| `changes` | seq, day, step, attempt, primitive, place, arguments, cause, result |
| `interventions` | id, as submitted, as applied (step, op, arguments, note, state-diff digest) |

## Parameters

| Parameter | Value | Status |
|---|---|---|
| checkpoint at | every committed step | decided (D1-4); a calibrate point: OPEN Q-RR1 |
| compression | zlib (stdlib) | decided |
| blob id | sha256, first 16 hex digits | decided (as cybertron 1's prompts) |

## What agents see

Nothing of the journal. An agent's context is a view of it (views.md).

## Open

- OPEN Q-RR1: checkpoints at every step, or every day plus the step's changes.
- OPEN Q-RR4: the remaining physical writes outside `apply` (hunger, missed meals, offers closing; review 39.01 §5) become
  primitives (37.4).

## Sources

proposals/run_record.md §2, §8; review 39.01 §2, §5; cybertron 1: `cybertron/provenance.py`, `settings.py`.

*Current as of 24 Oct 2026: D1-1, D1-4, D1-5.*
