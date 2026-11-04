# A fixed data interface for runs: versioned shapes, one read layer, one published layout

**Status:** partly accepted: D4-100 (part 1, built at Zach's request; retrospective). Part 2: discussion.
**Owner:** 37.4, with 37.1 (the run record's spec: record/views.md, exchange.md) and the c2viz session.

## Summary

The journal (`run.db`) is the right fixed base and stays as it is. The layers above it have drifted:
- the world inside its checkpoints had no version;
- readers interpret old checkpoints with today's engine code;
- the side files (`turns`, `days`, `perception`, `memory.jsonl`) grow keys by hand;
- what is published is a mix of layouts.

The proposal fixes five contracts, each with a version number. Nothing reads around them.

| Contract | Version now | Holds | Changes when |
|---|---|---|---|
| the journal's tables | 1 (`meta.schema`) | inputs, requests, responses, changes, events, checkpoints | almost never |
| the world record's shape | 1 (`world_schema`, D4-100) | the fields of every table, the top level, the day's record | every engine change to state, with an upgrade step |
| the view tables | proposed: 1 | the documented tables analyses and c2viz read | rarely; additions only within a version |
| `viz.json` | 2 (c2viz/SCHEMA.md) | what any visualizer reads; written by the run itself (part 2, item 7) | additions within a version; a converter for each new version |
| the side logs | proposed: 1 (`meta.log_format`) | turns, days, perception, memory, derived from the journal | never by hand |

## The proposal

### Part 1, built (D4-100)

- `world_schema` is in every world and checkpoint, and in the journal's meta.
- `cybertron2/engine/schema.py` declares the shape.
- spec/core/world_schema.md is the change log, with the known changes before version 1.
- A test fails on an undeclared field, or on the shape changing without the version.

### Part 2, for discussion

1. **An upgrade chain.**
   - `schema.upgrade(world)` applies one pure step per version (1→2, 2→3, ...) to a checkpoint's world, so every reader sees the
     current shape.
   - Each step is written in the same commit as the engine change that needs it, and tested on a kept sample checkpoint of the
     older version.
   - Version 0 runs (24 Oct to 4 Nov) get one step to version 1 where the change log says what to fill. For example, `routes`
     derived as c2viz does now, and missing optional fields left absent. Otherwise they are read at their own commit (item 6).
2. **The view tables are the read interface.**
   - The export already writes `views/`: `people_days`, `frames`, `holdings`, `buildings`, `parcels`, `claims`, `messages`,
     `calls` and `layout`. These become the documented contract for analyses and for c2viz's model, each with a schema version and
     its columns in record/views.md.
   - Add the tables now missing:
     - `movements`: per person a day, the node, the route of parcels, the parcels worked, where slept, and travel;
     - `things`: piles, bodies, graves and cairns a day;
     - `herds_days`;
     - `acts`: per act, with its units and result.
   - Views are computed from upgraded checkpoints. So they can be rebuilt for any run, and old runs gain new view tables when they
     are added.
   - c2viz's model then reads views and upgraded state. It stops building engine objects from old checkpoints (`c2viz.touch`
     today), which ties it to the current engine code.
3. **The side logs are derived only.**
   - `export --logs` writes `turns`, `days`, `perception` and `memory.jsonl` from the journal, in a fixed format (`log_format` 1).
   - The run loop stops adding keys to them by hand.
   - Analyses move to the views. The logs stay for reading by eye.
4. **One published layout:** `experimental/cybertron2/<run>/{run.json, manifest.json, journal/, views/, logs/}`, with the dataset
   card listing the five versions.
   - The 94 runs now on the Hub are republished to it.
   - The old file publisher (`cybertron2/publish_hf.py`) is retired once part 2 item 5 is done.
5. **Pre-journal runs are converted.**
   - The 41 runs from before the journal (M1, the valleys, the regions, Hollins, the Wide Country) are rebuilt into journals by
     replaying their recorded replies at their own commit, as c2viz/legacy did for the Wide Country (every result matched over 25
     days).
   - They are marked as a `converted` segment, then exported and published like the rest.
   - This costs compute only: no model calls.
6. **Reading at the run's own commit,** for anything the upgrade chain cannot express: a git worktree at the run's `code_sha`,
   with the run's frozen data. It is exact, but slow. It is a fallback for checks, not for everyday reading.
7. **Each run writes its own visual record** (added 4 Nov). The other items keep old runs readable; this keeps them drawn as their
   own engine meant them.
   - **The run writes it.** At the end of each day, the engine running the run computes the day's visual record: c2viz's per-day
     record, from its `extract` and `timeline`. The journal stores it in a new table (`frames`).
   - **Why the run, not the reader.** c2viz does more than read fields. It asks the engine where a person stands, what a parcel or
     crop looks like, the route rule and the signs. A record made by the run's own code is right for that version by construction.
     A record made later by today's code is not.
   - **The record is the one contract for any visualizer** (the map, the site, videos), versioned as `viz.json` is now:
     - within a version, fields are only added, and a missing field means absent;
     - a breaking change makes a new version, with a converter from the old one;
     - a renderer declares the versions it draws, and converts older ones as it loads them.
   - **Runs without the record get one, by the best means available, and say which:**
     - **exact:** the builder reads the run's code version (`provenance` in the journal), builds at that commit in a cached git
       worktree, and stores the record;
     - **approximate:** the upgrade chain and today's engine, marked `derived` and shown as such on the page, as routes inferred
       for runs from before D4-62 are now;
     - **pre-journal runs:** the legacy replay first (item 5), then the exact path.
   - **Cost:** a little time each night, and about 100 KB of record a day, compressed.
   - **Measured on 4 Nov.** Today's c2viz built all 55 journaled runs (days 0 to 2) with a valid `viz.json`. 54 replayed every
     change; d1_duo (24 Oct) left 2 unreplayed. So it works now, by care in `touch.py` and because the engine has mostly added
     fields. This item makes that hold by design.
8. **Fields the tests miss.** At the end of every run the journal records any undeclared world fields in meta
   (`world_unknown_fields`). A live run then shows a field the bot tests never exercised.

## Why

Zach (4 Nov): "Is the way data is saved for each run and published appropriate? ... Ideally, should find a method I can keep it
fixed on that works well and don't change the interface". Then: "Go ahead with the world schema number and changelog and write a
proposal for the rest".

What the audit found (38.58 sweep, and the 4 Nov publishing):
- **c2viz already works around shape drift.** It derives `routes_derived` for runs from before D4-62, and reads checkpoints by
  building engine objects through today's code.
- **The world changed shape a dozen times between 24 Oct and 4 Nov with no version.** On 4 Nov alone, D4-99 added `grave`,
  `cairn_day` and `cairn_by`.
- **The side logs are what most analyses and most of the Hub use,** and their keys grow when convenient. `days.jsonl` gained
  `camped`; `today.drawn` appeared unlisted. The guard test caught that on its first run.
- **Publishing was inconsistent.** The old publisher left out the journals until 4 Nov, so 94 runs were on the Hub with no
  `run.db`. Of those, 55 now have their journals; 41 have none to publish.

## Alternatives considered

- **Freeze the engine's world shape.** Not possible while the engine is being built.
- **Read every run at its own commit** (item 6 for everything). Exact, but slow, and every reader then needs the engine's code
  history.
- **Publish only `viz.json`.** Enough for the renderer, but it loses the analysis and the replay.
- **A full typed schema** (JSON Schema or dataclasses) for the world. Stronger checks, but heavy to keep in step during
  development. A declared field list with a version is enough to stop silent drift.

## Open questions

1. Who owns the views' schema: 37.1 (the record) or 37.4 (the engine)? Proposed: 37.1 owns the contract, and 37.4 keeps the code
   writing it.
2. Should `mind` and `know` (each person's memory and knowledge stores) get their own version? They hold what an agent believed,
   which the views' `beliefs` reads.
3. Checkpoints hold the whole world at every step: 425 MB for 55 runs. Should they be kept as deltas (a full state each day, and
   changes between steps)? This affects storage, not the interface.
4. Parquet (as published) or SQLite (`run.db`) as the long-term form? Proposed: SQLite while running, Parquet published, and
   import between them, as now.
5. For the c2viz session: can `extract` and `timeline` run inside the run loop (they use only `touch`, so yes in principle), and how
   long does a day take on the largest worlds?
6. The order of work. Proposed:
   - item 7 and the views' versions (small);
   - item 2's new tables (`movements` first: c2viz needs it);
   - item 3;
   - items 4 and 5 together;
   - item 1 as each engine change needs a step.

## Affects

- 37.1: record/views.md, exchange.md, journal.md (the meta keys).
- c2viz: its model reads views, and `touch` narrows.
- 37.2: analyses of runs read views.
- 37.4: schema.py, the run loop's logs, exchange.py.
- The Hub layout.

## History

- 4 Nov (later): Zach: "Is there a way to bake this into the design, so each visualiser recognises which engine version / schema
  and then visualises it appropriately?" Added item 7: each run writes its own visual record, a versioned contract for any
  visualizer, with exact or labelled-approximate records for runs without one. The old item 7 is now item 8. Measured that today's
  c2viz builds all 55 journaled runs.
- 4 Nov: part 1 built at Zach's request (D4-100; retrospective): schema.py, the number in worlds and the journal's meta,
  spec/core/world_schema.md, tests/test_cybertron2_schema.py. Part 2 written for discussion.

## Sources

spec/core/world_schema.md; spec/record/; c2viz/SCHEMA.md, c2viz/source.py, c2viz/touch.py, c2viz/legacy/;
cybertron2/engine/exchange.py; review/38_space_engine/34_run_record_r5.md, 58_episodes.md.
