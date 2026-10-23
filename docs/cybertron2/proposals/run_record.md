# Proposal: the run record and the run backend

**Status:** discussion. **Owner:** 37.1 (the run record, the runner's journal, the views and tools); 37.4 owns the engine code it
touches (`cybertron2/engine/run.py`, `world.py`), so building needs 37.4's agreement on the board (README rule 6).

## Summary

A run is an **append-only journal** of everything that entered the world from outside, plus **checkpoints** of the state at each
step's commit:
- what entered the world: model replies, human replies, interventions, the frozen spec and data tables, the code version;
- the checkpoints are what make the run cheap to resume, rewind and fork.

Everything is written to the journal as it happens, so a run can be watched layer by layer and read up to a crash; a commit only
makes a step official. Everything people look at is a **view** derived from the journal: the state at any point, exactly what an agent saw in its context,
frames of the world for a map that plays through the history, analysis, export tables, and the website. None of these views is
authoritative; any of them can be rebuilt.

The runner is a **resumable, idempotent state machine**: it advances step by step, every answer it needs is a keyed request, and
every step commits atomically. Crash, cancel and pause are therefore the same thing (stop after the last commit), resume replays
nothing it has already paid for, and a human player is one more way of answering requests.

The journal is **one SQLite file per run**; values stay JSON, checkpoints are compressed JSON, prompt texts are content-addressed.
Publishing and analysis use **Parquet**, which the site already reads. The analysis and measurements behind this are in review
39.01.

## What it must support (Zach, 23 Oct)

Everything cybertron 1 could do:
- the website generated from published data;
- analysis;
- fork, pause, resume and rerun.

Beyond that:
- visualisations that play through a world's history on a map: places, buildings, acts and travel each day;
- reconstructing exactly what an agent saw in its context at any point;
- a human playing in-world as an agent with the same context, answering with the same verbs;
- idempotent, resumable and cancellable running.

These are examples; the design should make such things easy, not just these.

## The proposal

### 1. The execution model: steps, requests and commits

- **Steps.** A day is a fixed sequence of steps (dawn, decide, talk waves, work, settle, night with its fuse calls, memory;
  spec/core/round.md). Commit points are the ends of steps, so a run can stop between any two of them.
- **Written as it happens, made official at the commit.** Nothing waits for the commit to be written:
  - every request and response, event and change is written to the journal the moment it happens, tagged with its step and an
    attempt number;
  - the commit only marks the step's attempt official and stores its checkpoint;
  - a live view (chronicle, map, a human's screen) shows the open step's rows as they come in, marked provisional, layer by layer
    through the day: who decided what, what was said in each talk wave, each act of the work step as it is done.

  After a crash or a cancel, the open step's rows stay in the journal as an **aborted attempt**, readable like any other: you see
  everything that happened up to the crash. Resume then re-runs the step as a new attempt from the last checkpoint, reusing every
  answer already received. Views of the official history read committed attempts only. A view of "what happened up to the crash"
  reads the aborted attempt too. Committing whole matters for what counts as the state, not for what can be seen.
- **Requests.** Everything the engine needs from outside is a request with a deterministic key
  `d<day>.<step>.<wave>.<agent>.<n>`: a model call, a human's turn, a fuse call at night. A request carries what the answerer
  sees: the conversation id and index, the system text, the schema, the new message. Its response is the raw text and the parsed
  reply. Requests and responses are written to the journal the moment they exist, independently of commits.
- **Responders** answer requests:
  - `Recorded`: from a journal (replay, a fork's prefix, a resume of a step cut short);
  - `Model` (the LLM backends);
  - `Bot` (scripted, for smoke tests);
  - `Human` (§5).

  A run assigns a responder per agent (and per day range, for forks). The engine never knows which one answered.
- **Idempotency.** Before asking, the runner looks the key up in the journal: an answered request is never asked again. Re-running
  a step from its checkpoint with the journal's answers gives the same result byte for byte (the engine is deterministic given its
  answers: measured, review 39.01 §5). So:
  - **resume after a crash** reloads the last commit and re-runs the open step; model calls already answered are reused, not
    paid twice;
  - **cancel** (Ctrl-C, a budget, a usage limit) stops asking, lets in-flight calls finish or drop, and never commits half a step;
  - **pause** stops at a chosen step (`--until d12.talk`) and is a resume later.
- **Determinism rules** (enforced by a replay test):
  - randomness only from `World.rng(seed, parts...)`;
  - answers are consumed in key order, not arrival order;
  - no wall-clock time or thread order reaches the state.

### 2. The journal (`run.db`, SQLite, one file per run)

| Table | Rows | Notes |
|---|---|---|
| `meta` | provenance: git sha, dirty flag and diff sha, a sha per module, python, backend; spec (resolved), seed, schema version, `log_format` | one row each |
| `data` | the engine's data tables as the run read them (PHYSICS, ITEMS, TECHNIQUES, COVERS, fittings, signs, ...), frozen at the start; every read during the run goes through them | so a run keeps its own physics whatever the code later says |
| `segments` | start, resume, rewind, fork: first step, code sha, parent {run, step}, responders per agent | the lineage of a run |
| `requests` | key, step, agent, conversation id and index, system sha, schema sha, message sha, responder | the exact input to each answer |
| `responses` | key, attempts (raw text, error), parsed reply, thinking, usage, transport, latency | written as each arrives |
| `blobs` | sha -> compressed text (system prompts, messages, schemas) | a prompt repeated across days is stored once |
| `steps` | step key, attempt, status (open, committed, aborted), the checkpoint's sha | the commit log; aborted attempts are kept |
| `checkpoints` | step -> the whole `World.s` plus the runner's own state (conversations, cost), compressed JSON | at every step commit, or every day plus step deltas (§7) |
| `events` | id, day, step, place, kind, actor, target, about, concerns, text, cause | every event; today they are dropped at dawn |
| `changes` | seq, day, step, primitive, place, arguments, cause {actor, verb, for, node}, result | every application of `World.apply` |
| `interventions` | as submitted and as applied (step, op, arguments, note, state-diff digest) | never applied twice |

**Rows are durable as they are written:** each request, response, event and change is its own small transaction, tagged with
`(step, attempt)`. **A commit** writes the step's checkpoint and marks its attempt committed, in one transaction. So the official
history is the committed attempts. An aborted attempt (a crash, a cancel) stays for inspection, and answers are reused whichever
attempt asked for them. Readers (the live chronicle, a map, a
human's screen) open the file while the run writes (WAL mode).

### 3. Views (derived, rebuildable, never authoritative)

| View | Built from | Gives |
|---|---|---|
| `state(step)` | checkpoints (+ changes within a step) | the world at any point: who held what, where everyone was, every claim |
| `beliefs(agent, step)` | checkpoints (`mind`, `know`) | what the agent knew and believed, and as of when |
| `context(agent, request key)` | requests + blobs | **exactly what the agent saw**: the system text, the schema, every earlier message and reply in its running conversation, and the new message, in order; the same text whether a model or a human answered |
| `frames(day[, step])` | checkpoints + changes + events + `layout` | the map: places and roads, parcels, buildings, herds, people at places or on roads, the day's acts and events, for an animated view |
| `history` | all of the above | a read-only analysis API (as cybertron 1's History): series, events by kind, place and actor, causes (`caused(x)`), windows |
| `chronicle` | the same | the readable HTML page that exists today |
| `export` | the same | Parquet tables for analysis and the site (§6) |

`context()` is rebuilt from the record, not recomputed from state, so it is exact by construction. A replay also recomputes each
message from the state (the prompt functions read only `Here` and `Mind`) and checks it against the recorded sha, which tests that
the prompt code and the state agree.

### 4. The map (visualising the world's history)

The world has no coordinates (world/parcel_graph.md: parcels are a graph with a side and a height; nodes are joined by roads
measured in days). The map needs a **layout**, computed once per run and stored with it (presentation only; agents never see it).
- **Nodes:** placed by a seeded layout of the road graph weighted by days.
- **Parcels inside a node:** placed by side (a compass sector), height (shading or rings) and adjacency.
- **Buildings:** on their parcels.

Each frame then places:
- people at their node, or on a road between its ends by days travelled (transit: left and arrive);
- the day's acts as marks at the parcel or building where they happened, and the night's events (fights, thefts, deaths) at their
  place;
- what changed, highlighted.

The viewer is a static page (SVG or canvas, a day slider and play button) reading exported frames, so it works on the site and on a
local run in progress.

### 5. A human playing as an agent

A `Human` responder answers an agent's requests. When the runner reaches one, it records the request, commits, and waits, or exits
to be resumed: waiting on a person is a pause.
- **The player is shown `context(agent, key)`:** the same system text, conversation and new message the model would get, and
  nothing else (no map, no other agents' views unless the world gives them).
- **The player answers in the same reply schema and verbs.** A form may help write them, but what is stored is the same JSON a
  model returns, checked and refused in the same way.

Interfaces: a terminal command first (`python -m cybertron2.engine play RUN --as NAME`), a web page later on the same journal. A
world can mix humans, models and bots per agent. The record says which responder answered each request, so analysis can tell them
apart.

### 6. Export, publish and the website

- **Export:** long, typed Parquet tables with a manifest, as cybertron 1's schema 2, for cybertron2's shape:
  - `people_days`, `holdings` (container, item, qty), `claims`, `buildings`, `parcels`;
  - `events`, `changes`, `acts`;
  - `beliefs` (agent, day, about, what, as of), `messages` (said, told, heard by whom, where), `calls`;
  - `frames` and `layout` for the map;
  - `contexts`: the blobs and the requests that reference them, loaded lazily.
- **Two kinds of exported table.**
  - **Journal tables** mirror `run.db` one to one and lose nothing: meta, data, segments, requests, responses, blobs, steps,
    checkpoints (compressed JSON), events, changes, interventions.
  - **View tables** (people_days, holdings, beliefs, frames, ...) are derived for analysis and the site, and can be regenerated
    from the journal tables.
- **Publish:** both kinds, a catalog row and a manifest with each table's checksum, through the privacy gate. `publish_hf.py` is
  rewritten to it. Runs stay under `experimental/cybertron2/` until Zach decides otherwise.
- **The inverse of publish:**
  - `fetch RUN_ID` downloads a published run's journal tables and rebuilds `run.db` exactly (`import`, the inverse of `export`).
    The result is a local run like any other: replay it, view it, fork or continue it from any committed step.
  - Checkpoints are JSON, so publishing them is safe. cybertron 1 never published its pickled checkpoints, because loading a
    downloaded pickle can run arbitrary code, and had to rebuild them by replaying (`cybertron fetch`, `continue`). Here a fetched
    run can be forked at any step at once.
  - Replay and fork need the run's code: `fetch` checks the recorded git sha, and either runs under it in a temporary worktree (as
    cybertron 1's `rerun`) or continues under current code as a new segment that claims no identity.
  - A round-trip test guards the inverse: export, import and replay must reproduce the run byte for byte.
- **Website:** the site already reads Parquet from the Hub (`site/lib/cybertron-data.js`, hyparquet). A cybertron2 run page adds
  the map, per-agent context ("what X saw on day 12") and the chronicle, from those tables.

### 7. Commands

```
python -m cybertron2.engine run SPEC --out RUN [--until STEP] [--as NAME=human|bot|model]
python -m cybertron2.engine resume RUN [--until STEP]          # crash, cancel, pause: all resume the same way
python -m cybertron2.engine replay RUN [--to STEP]             # recorded answers only; byte-compare checkpoints and logs
python -m cybertron2.engine fork RUN --at STEP [--apply iv.yaml] [--replicates K] [--as NAME=...] --out DIR
python -m cybertron2.engine play RUN --as NAME                  # answer NAME's pending requests by hand
python -m cybertron2.engine context RUN --agent NAME --at STEP  # print exactly what NAME saw
python -m cybertron2.engine frames RUN --out DIR                # map frames; view RUN for a local viewer
python -m cybertron2.engine export RUN... --out DIR             # Parquet; publish RUN... [--push]
python -m cybertron2.engine import DIR --out RUN                # Parquet journal tables -> run.db (exact)
python -m cybertron2.engine fetch RUN_ID [--revision vX.Y] --out RUN   # download a published run, then import
python -m cybertron2.engine dump RUN [--table events]           # JSONL out of the journal, for grep and jq
```

- **Fork:** restores the checkpoint at the step, answers earlier requests from the parent, applies the interventions, and plays on
  with the chosen responders.
- **Replicates:** differ by a seed salt from the fork point.
- **Replay is promised only within one code version.** Across versions, `continue` plays forward from a checkpoint under current
  code, recorded as a new segment, with no claim of identity (cybertron 1's lesson: docs/engine_versions.md).

### 8. The format: JSON, SQLite and Parquet, each for what it is good at

- **Values stay JSON.** The state is a plain-JSON dict already, and the volume is small: 47-184 KB a day compressed in the measured
  worlds, so a 100-day run of 50 agents is tens of MB. A binary encoding (msgpack, protobuf) saves bytes we do not need to save,
  and loses jq, diffs and readability. Not worth it.
- **The journal is SQLite** rather than a directory of JSONL files, because of what the runner must guarantee:
  - atomic step commits (one transaction, where cybertron 1 needed hand-kept byte offsets and log truncation);
  - idempotent writes (insert by request key);
  - safe concurrent readers (a map or a human's screen while the run writes);
  - indexed queries (events by place, day or actor) without loading the run;
  - one file to copy, fork, publish or delete.

  It is in Python's standard library. The cost is a binary file not readable with grep, which `dump` covers, and a schema to
  version (the `meta` row).
- **Prompts and other repeated text are content-addressed** (`blobs`). In cybertron 1, `reasoning.jsonl` was 54 MB of 150 rounds,
  mostly repeated prompt text.
- **Analysis and the website read Parquet**, written by `export`. DuckDB can also query `run.db` directly while a run is live.

## Why

- **A crashed run is lost today, and there is no fork or replay** (review 39.01 §4). This design gets them back.
- **One mechanism serves every requirement.** Pause, cancel, resume, fork, replay and human play are all "stop at a commit, then
  answer the next requests from somewhere", rather than five features.
- **The journal is the single source.** The website, the map, the context viewer and analysis cannot disagree.
- **It is cheap now:** a small engine, JSON state, one chokepoint with causes, measured determinism.

## Alternatives considered

- **A directory of JSONL files with byte offsets, as cybertron 1.** It works (cybertron 1 proves it) and is grep-able. Rejected
  for the live record because atomic commits, idempotent writes and concurrent readers would all be hand-built again. `dump` keeps
  the JSONL view.
- **Event sourcing only (changes, no checkpoints).** Rejected:
  - perception writes the knowledge stores outside the chokepoint by design;
  - three physical writes bypass it today (review 39.01 §5);
  - every query would replay from day 0.

  Checkpoints plus changes is fast and exact.
- **Checkpoints only, no change log.** Enough for resume, fork and the daily map. It loses within-day state and the causes of
  changes. A valid first cut if routing the remaining writes through primitives waits.
- **Pickle checkpoints.** Rejected: they tie a checkpoint to the code that wrote it.
- **A server database (Postgres) or a server-side site.** Not needed. One file per run, and a static site reading Parquet, as
  today.
- **Byte-identical replay across code versions.** Rejected (38.07 §3, cybertron 1's experience).

## Open questions

- Checkpoint at every step, or every day plus the step's changes? Every step is simplest. At 5-8 steps a day the size is still
  small; to measure on the region world.
- Conversations on resume: restore each agent's running conversation exactly (needs raw replies, which the journal keeps), or
  restart conversations at the resume day? Exact is the default, since it is what the record makes possible.
- The human interface's first form: the terminal, or a page served locally from the journal?
- Do the remaining writes outside `apply` (hunger, missed meals, offers closing) become primitives now (37.4's code)?

## Affects

- `spec/measurement/measures.md` (what runs record: 37.4, to compile);
- `spec/core/architecture.md` (the chokepoint records its calls; steps commit);
- `spec/core/round.md` (named steps as commit points);
- `cybertron2/engine/run.py`, `world.py`, `publish_hf.py` (37.4's code).

## Order of work

| Step | What | Size |
|---|---|---|
| R1 | The journal: requests and responses by key, blobs, events, changes, step commits with checkpoints, provenance and frozen data. Runs write it alongside today's files; no behaviour change | M |
| R2 | The runner as a state machine: resume, cancel, pause (`--until`), replay with the byte-compare test; a run killed mid-step resumes to the same end | M |
| R3 | `context` and `play --as` (terminal): a human answers one agent's requests in a bot world | S-M |
| R4 | fork, replicates, interventions as ops on primitives | M |
| R5 | Views: `history`, `frames` with the layout and a local map viewer; `export` (journal and view tables) and its inverse `import` / `fetch`, with the round-trip test; `publish` rewritten | M-L |
| R6 | The site's cybertron2 run page: map, context viewer, chronicle | M |

## History

- 23 Oct 2026: proposed by 37.1 at Zach's request, from review 39.01 (checkpoints, keyed calls, logs, fork).
- 23 Oct 2026: revised after Zach's requirements (the website, the map through the history, exact agent context, human play,
  idempotent, resumable, cancellable): the runner as a state machine over keyed requests; the journal in SQLite with JSON values
  and Parquet export; views; the map layout; the human responder.
- 23 Oct 2026: revised again (Zach):
  - everything is written as it happens and the commit only makes a step official, so a run is visible layer by layer through the
    day and up to a crash (aborted attempts are kept);
  - publish exports lossless journal tables beside the view tables, with the inverse (`import`, `fetch`) to rebuild a runnable,
    forkable local run from the published Parquet.

## Sources

- Review 39.01.
- cybertron 1: `cybertron/provenance.py`, `replay.py`, `interventions.py`, `history.py`, `export.py`, `publish.py`, `settings.py`,
  `llm.py` (sessions, `--system-prompt`, `--json-schema`); docs/ARCHITECTURE.md §8; docs/data_format.md;
  docs/engine_versions.md; `site/lib/cybertron-data.js`.
- world/parcel_graph.md.
- Reviews 38.07 §3 and 38.14 §1.
