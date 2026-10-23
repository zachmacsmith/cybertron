# Proposal: the run record (every point rebuildable; resume, replay, fork; easy to analyse)

**Status:** discussion. **Owner:** 37.1 (the run record and its tools); 37.4 owns the engine code it touches
(`cybertron2/engine/run.py`, `world.py`), so building it needs 37.4's agreement on the board (README rule 6).

## Summary

A cybertron2 run should be **its inputs plus checkpoints**:
- inputs: the code version, frozen data tables, the resolved spec, the seed, every model reply keyed for replay, every
  intervention;
- checkpoints: a JSON checkpoint of the state at the end of every day, with append-only logs of events and changes.

From those, every day's state is a file, every point within a day can be rebuilt, every prompt can be rebuilt and verified, and a
run can be resumed, replayed, rewound, or forked with interventions and replicates. A History reads it for analysis, and export and
publish turn it into tables and an archive that others can continue. The analysis behind this, with measurements, is review 39.01.

## The proposal

### 1. The run directory

| File | What | New or changed |
|---|---|---|
| `run.json` | provenance:<br>- git sha, dirty flag and diff sha, a sha per `cybertron2` module, python;<br>- backend and models;<br>- spec sha, seed, `log_format`;<br>- **segments**: start, resume, rewind and fork, each with its first day, its code and its parent {run, day} | extended |
| `spec.json` | the resolved spec (after `base:` merges and generation) | new |
| `data.json` | the engine's data tables as the run read them (PHYSICS, ITEMS, TECHNIQUES, COVERS, fittings, signs, ...), frozen; every read during the run goes through it | new |
| `calls.jsonl` | one row per model call, keyed `d<day>:<step>:<wave>:<agent>:<n>` (step: decide, talk, lighten, fuse, memory):<br>- system and message sha (texts content-addressed under `prompts/`, once each);<br>- the raw text of every attempt, with errors;<br>- the parsed reply, thinking, usage and transport (session, flattened) | new; `turns.jsonl` stays as the readable view |
| `state/dNNNN.json.gz` | the whole `World.s` at the end of each day (after memory), plus the runner's own state: conversations (messages, start day, frozen system and schema), cost, the day's carried lists | new |
| `state/index.json` | per day, the byte offsets of every append-only log at that checkpoint (as cybertron 1's `checkpoints/index.json`), so a rewind cuts every log to the day | new |
| `events.jsonl` | every event, appended when the day's events are cleared at dawn: id, day, place, kind, actor, target, about, concerns, text, **cause** | new (today they are dropped) |
| `changes.jsonl` | every primitive applied through `World.apply`: seq, day, step, primitive, place, arguments, **cause** {actor, verb, for, node}, result | new |
| `interventions.yaml` / `.jsonl` | as submitted / as applied (day, step, op, arguments, note, state-diff digest) | new |
| `turns.jsonl`, `days.jsonl`, `perception.jsonl`, `memory.jsonl` | the readable views, as today | unchanged |

### 2. What "every point is rebuildable" means

- **Any day:** `state/dNNNN.json.gz` holds the world, including every agent's knowledge store, so "what did X believe on day d"
  is a lookup.
- **Any point within a day:** the previous day's checkpoint plus `changes.jsonl` up to that seq. This needs every change to pass
  through `World.apply`. Review 39.01 §5 found three that do not: hunger, missed meals and offers closing. They become primitives
  (`p_hunger` or `p_set`, `p_close_offer`). The knowledge stores stay written by perception, which is a pure function of the
  state and events, so a replay rebuilds them exactly; they need no change log.
- **Any prompt:** rebuilt from the state at that point (`PR.turn_prompt(Here, Mind)` is a function of it) and checked against the
  sha in `calls.jsonl`.

### 3. Commands (cybertron 1's names and meanings)

```
python -m cybertron2.engine resume RUN                         # from the latest day checkpoint, conversations restored
python -m cybertron2.engine replay RUN [--to D]                # recorded replies only; byte-compare every checkpoint and log
python -m cybertron2.engine rewind RUN --to D --out NEW        # logs cut to day D's offsets; then resume NEW
python -m cybertron2.engine fork RUN --at D [--apply iv.yaml] [--replicates K] [--out DIR] [--replay strict|none]
python -m cybertron2.engine branches RUN                        # the lineage tree from run.json parents
```

- **Replay** uses a replay policy that answers each call from `calls.jsonl` by key.
  - `strict`: the message sha must match.
  - `none`: take the recorded reply whatever was asked.
- **Fork** restores day D-1's checkpoint and applies the interventions at their step. It answers calls before D from the parent's
  record and plays from D with the live policy (models, or bots for a dry run).
- **Replicates** differ only by a salt added to the seed from day D, so the world's own draws after the fork differ while
  everything before is shared.
- **Interventions** are typed ops on primitives, applied through `World.apply` inside an `intervention` cause. They are recorded
  and never applied twice. The spec's `script:` and `incidents:` become the day-0 case of the same thing.
- **Replay holds within one code version** (the same sha and frozen data). Across versions, `continue` plays a published or old
  run forward under current code from a checkpoint, recorded as a segment with both shas, and claims no byte identity (the lesson
  of cybertron 1's engine versions).

### 4. Analysis

A `History2` (read-only, over a run directory):
- `state(day)`;
- `at(day, seq)`: the state after a given change;
- `series(path, who)`;
- `events(kind, place, actor, day range)`;
- `changes(primitive, actor, cause)`;
- `beliefs(agent, day)`: the knowledge store;
- `calls(agent, day)`;
- `caused(event or change)`: what followed from it, through the causes;
- `window(d0, d1)`.

`analyze` reports (population, economy, information spread: who learned what, from whom, how many days late) are written on it.

### 5. Export and publish

**Export:** long typed tables with a manifest, as cybertron 1's schema 2 but for cybertron2's shape:
- `people_days` (stage, hunger, place, alive), `holdings` (container, item, qty, day), `claims`, `buildings`, `parcels`;
- `events`, `changes`, `acts`;
- `beliefs` (agent, day, about, what, as of), `messages` (said, told, heard by whom, where);
- `calls`.

**Publish:** `publish_hf.py` is updated to the engine's files, and the raw archive holds what a replay and a `continue` need: run,
spec, data, calls, checkpoints, logs. Runs stay in `experimental/cybertron2/` until Zach decides otherwise.

### 6. Order of work

| Step | What | Size |
|---|---|---|
| R1 | Record completeness: `calls.jsonl` with keys and raw text; `events.jsonl`; `changes.jsonl`; daily JSON checkpoints with log offsets; provenance and frozen `data.json` | S-M |
| R2 | `resume` and `replay`; a test that a scripted run replays byte-identically, and that a run killed mid-way resumes to the same end | M |
| R3 | The three writes outside `apply` become primitives; a test that checkpoint plus changes equals the next state at every seq | S |
| R4 | `rewind`, `fork`, `--replicates`, interventions as ops on primitives | M |
| R5 | `History2`, export tables, `publish_hf` updated | M |

## Why

- **A crashed run is lost today.** Cloud sessions are reclaimed and usage limits stop runs mid-way.
- **Counterfactuals are the method.** The takeover benchmark's shock forks, interventions, and replicates that separate model
  noise from effect all need fork.
- **cybertron2's central object is information in place.** Who knew what, and when, is exactly what is overwritten every day
  unless days are kept.
- **It is cheap now.**
  - The state is plain JSON: 47-184 KB a day compressed in the measured worlds.
  - The engine is deterministic given its replies (measured).
  - The chokepoint and its cause context exist.
  - Doing it before the engine grows avoids cybertron 1's retrofit (review 09's primitive layer).

## Alternatives considered

- **Changes only, no checkpoints** (event sourcing). Rejected: perception writes the knowledge stores outside the chokepoint by
  design, and rebuilding a day from day 0 makes every query slow. Checkpoints plus changes is both fast and exact.
- **Checkpoints only, no change log.** Simpler, and enough for resume, rewind and fork. It loses state within a day and the causes
  of changes. A reasonable first step (R1 without `changes.jsonl`) if R3 waits.
- **Pickle checkpoints, as cybertron 1.** Rejected: they tie a checkpoint to the code that wrote it; JSON does not.
- **Byte-identical replay across code versions, as cybertron 1 promised.** Rejected (38.07 §3; docs/engine_versions.md): it
  multiplied code paths and still failed. Replay within a version, freeze data, and continue across versions without promising
  identity.

## Open questions

- Do conversations need their raw replies kept to resume a session mid-stretch, or can a resume restart every conversation at
  that day with the memory written so far? The second is simpler, but it is a behaviour change at a resume point.
- Do fuse calls at night and calls to travellers on the road get their own step names, or wave numbers under `talk`?
- Retention: full checkpoints every day, or every k days with changes between? The measured sizes say every day is affordable.
- Should a thread-order test run with randomised completion order, to show nothing depends on `as_completed`?

## Affects

`spec/measurement/measures.md` (what runs record: owner 37.4, to compile); `spec/core/architecture.md` (the chokepoint records
its calls); `cybertron2/engine/run.py`, `world.py`, `publish_hf.py` (37.4's code).

## History

- 23 Oct 2026: proposed by 37.1 at Zach's request, from review 39.01.

## Sources

Review 39.01; cybertron 1: `cybertron/provenance.py`, `replay.py`, `interventions.py`, `history.py`, `export.py`, `publish.py`,
`settings.py`, docs/ARCHITECTURE.md §8, docs/data_format.md, docs/engine_versions.md; review 38.07 §2 item 7 and §3; review 38.14
§1.
