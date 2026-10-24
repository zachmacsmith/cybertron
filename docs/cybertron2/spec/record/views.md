# Views of a run

## Summary

Everything people look at is built from the journal and is never authoritative: the state at any point, what an agent knew, the
exact context it saw, the map through the history, the analysis API, the chronicle, and live views of a run in progress.

## Decided

- D1-1: a map that plays through the world's history (places, buildings, acts, travel, each day); the exact context an agent saw
  at any point; analysis as cybertron 1's.
- D1-2: a run in progress is visible step by step, and what happened up to a crash is readable.
- D1-4: the views below.

## Mechanics

| View | Built from | Gives |
|---|---|---|
| `state(step)` | the checkpoint at that step; with `at(step, seq)`, plus the changes up to a change | the world at any point |
| `beliefs(agent, step)` | the checkpoint's `mind` and `know` | what the agent knew and believed, and as of when |
| `context(agent, key)` | requests and blobs | the exact input to that request (below) |
| `frames(day[, step])` | checkpoints, changes, events, `layout` | the map (below) |
| `history` | all of the above | the analysis API |
| `chronicle` | the same | the readable page (`cybertron2/engine/chronicle.py`) |

- **An agent's context** is what the answerer was given, in order:
  - the system text;
  - the reply schema;
  - every earlier message and reply in the agent's running conversation (a stretch of days, spec/information/memory.md), with
    each reply as its raw text;
  - the new message.

  It is rebuilt from the record, not recomputed, so it is exact by construction. It is the same whichever responder answered.
  When the CLI continued a cached session, the record is still the full sequence; transport notes how it was sent.
- **The map.** The world has no coordinates (world/parcel_graph.md), so a layout is computed once per run and stored with it
  (presentation only, never seen by agents):
  - nodes by a seeded layout of the road graph, weighted by days;
  - parcels inside a node by side (a compass sector), height (shading) and adjacency;
  - buildings on their parcels.

  A frame places people at their node or parcel, or on a road between its ends by days travelled. It marks the day's acts where
  they happened and the night's events (fights, thefts, deaths) at their place, and highlights what changed. The viewer is a
  static page (a day slider and play) that reads exported frames, for the site and for a local run.
- **History** (as cybertron 1's): `state(step)`, `at(step, seq)`, `series(path, who)`, `events(kind, place, actor, days)`,
  `changes(primitive, actor, cause)`, `beliefs(agent, step)`, `calls(agent, days)`, `caused(event or change)`,
  `window(d0, d1)`. Analyses (`analyze ...`) are written on it.
- **Live and aborted.** Views read committed attempts by default. A live view also reads the open attempt, marked provisional;
  `--with-aborted` reads aborted attempts (what happened up to a crash).

## Commands

```
python -m cybertron2.engine context RUN --agent NAME --at STEP|KEY
python -m cybertron2.engine frames RUN --out DIR          # and: view RUN (a local map viewer)
python -m cybertron2.engine dump RUN [--table events]     # JSONL out of the journal, for grep and jq
```

## Parameters

| Parameter | Value | Status |
|---|---|---|
| frame granularity | one frame per day, with the work step's acts in order | proposed |

## What agents see

Only their own context, which this view reproduces; agents never see the map, the layout or other agents' views.

## Open

None beyond journal.md.

## Sources

proposals/run_record.md §3, §4; cybertron 1: `cybertron/history.py`, `site/assets/run/square.js` (the animated map).

*Current as of 24 Oct 2026: D1-1, D1-2, D1-4.*
