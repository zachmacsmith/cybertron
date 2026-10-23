# Review 39.01: how a run is recorded in cybertron 1 and cybertron2, what was lost, and what to bring back

*23 Oct 2026, the 37.1 session at Zach's request ("compare how information is written to and stored in state in cybertron 2 and
cybertron 1, exported, published; what has been lost; can we reintroduce forking, each point fully rebuildable, easy to
analyse"). Read against `wp/cybertron2` at 42b258e (the engine in `cybertron2/engine/`) and the old engine as frozen on
`bench/first-batch`. Measurements were made with scripted bots (no model calls); the scripts are described in §5. The proposal
that follows from this is [proposals/run_record.md](../../cybertron2/proposals/run_record.md).*

## 1. In one paragraph

cybertron 1 treats a run as **an instrument**. Every input is recorded: the spec, the frozen code defaults, the code version, and
every model reply keyed by round, phase, wave and agent. Every change is logged with its cause chain, and the state is
checkpointed every round with offsets into the append-only logs. Any round can therefore be replayed byte for byte, resumed,
rewound, or forked with interventions and replicates. Scoring is computed afterwards from a read-only History, and the run exports
as typed tables and publishes with a raw archive that is enough to continue it.

cybertron2 treats a run as **a set of readable logs plus a final state**. It has no checkpoints, no call log keyed for replay, no
record of the changes it makes, no event log that outlives the day, and minimal provenance. A crashed run is lost; no run can be
replayed, rewound or forked; and state at any point but the end must be reconstructed from text.

Two things make this cheap to fix:
- The state is now one plain-JSON dictionary, about 50 to 200 KB a day compressed.
- The engine is deterministic given its inputs (measured: two scripted runs are byte-identical in every file).

## 2. Side by side

| | cybertron 1 (`cybertron/`) | cybertron2 (`cybertron2/engine/`) |
|---|---|---|
| **State** | `Kernel.w` plus the instance and per-module state; Python objects; checkpointed by pickle every round (`checkpoints/rNNNN.pkl`; the 37.1 growth probe: 28 KB at the start, 48 MB over 150 rounds, about 320 KB a round) | `World.s`, one plain-JSON dict (state by place: nodes, roads, parcels, buildings, herds, containers, people, institutions, claims, offers, agreements, `know`, `mind`, `events`, `acts`, `log`); written once, at the end (`state.json`) |
| **What an agent knows** | derived: events carry `vis` (who may see them); prompts filter the global log; "what X saw" is rebuilt by filtering | **state**: perception writes each agent's knowledge store (`mind`, `know`) as things are seen; beliefs, places known and memories are records. They are 75-80% of the state's bytes (§5) |
| **Events** | `events.jsonl`, append-only, every event with id, round, type, agent, data, `vis` and its **cause chain** (phase, turn, action, law, primitive, world, intervention frames) | `World.s["events"]`, **reset at every dawn** (`run.py`: `w.s["events"] = []`); never written to a log. What survives: per-node "facts" and per-agent perception in `perception.jsonl`, result lines (text) in `turns.jsonl` |
| **Changes of state** | through `k.apply` (routed primitives with law hooks), each logged as the events it emits, inside cause frames | through `World.apply` (one chokepoint, place-checked, before/after hooks, a cause context `{actor, verb, for, node}`), but the call record is **built and dropped**: no log. Some changes bypass `apply` (§5: hunger, missed meals, offers closing, besides memory and knowledge by design) |
| **The action record** | events plus `turns.jsonl` and `reasoning.jsonl` | `World.s["acts"]` (day, actor, verb, technique, for whom, node): in state, so only in the final `state.json` |
| **Model calls** | `calls.jsonl`: one row per call with its replay key `r<round>:<phase>:<wave>:<agent>:<n>`, system and user prompt sha (texts content-addressed under `prompts/`), every attempt's raw text (retries and errors), the parsed reply, reasoning, usage | `turns.jsonl`: one row per agent and day with the turn prompt (the new message only), the **parsed** first reply, talk-step and lighten exchanges, results, usage; memory calls in `memory.jsonl`. No call key, no raw text, no failed attempts; the system prompt only as at day 0 (`run.json` `systems`), though it is recomputed every day |
| **Per-round state** | `snapshots.json` (per-round derived state: holdings, rights, prices, ...), `ground_truth.json` | `days.jsonl`: one night record a day (meals, deaths, cold, stocks, cost, offers, agreements); otherwise only the final state |
| **Provenance** | `run.json`: git sha, dirty flag and diff sha, a sha per module, python, backend, models, spec and instance sha, seed, `log_format`, `engine_version`, **segments** (start, resume, rewind, fork, each with its code); `instance.json` with **frozen settings** (every code default the run read, D-43) | `run.json`: the spec, backend, day-0 system prompts and models. No code version. Engine data tables (`data.py`: PHYSICS, ITEMS, TECHNIQUES, ...) are read from the code at run time: "no defaults are frozen yet" (cybertron2/README) |
| **Resume after a crash** | `python -m cybertron resume` from the latest checkpoint | none: the run is lost (noted in 38.14 §1) |
| **Replay** | `replay RUN [--to N]`: replays every recorded reply and checks events and snapshots are byte-identical | none (the engine is deterministic given its replies, but they are not recorded in replayable form) |
| **Rewind, fork, replicates** | `rewind --to N`; `fork --at N --apply iv.yaml --replicates K` (parent's replies before N, live policy after; post-fork sampling differs per replicate) | none. A world can script acts and incidents by day from the start (`script:`, `incidents:` in the spec), but nothing can branch a run that exists |
| **Interventions** | typed ops scheduled by round and phase, applied through primitives inside an intervention cause frame, recorded with a state diff, never applied twice | `script:` and `incidents:` from day 0 only |
| **Analysis** | `History`: state(r), series, events by type/agent/round, life spans, lineage, goal spans, windows; post-hoc scoring; `analyze` (takeover, control, demography) | `report.py` (for the phase-0 runner) and `chronicle.py` (a readable HTML page of a run); analysis is ad hoc over the jsonl files |
| **Export** | `export`: long, typed tables (schema 2) with a manifest; `load()` reads them back | none |
| **Publish** | `publish`: tables, a raw archive enough to replay and continue a run (`fetch`, `continue`), a catalog, the dataset card, the site; privacy gate; releases | `publish_hf.py`: an experimental folder, privacy gate, but written for the phase-0 runner (`FILES` names `rounds.jsonl`; the engine writes `days.jsonl`), so it does not cover engine runs as they stand |
| **Code checks** | `difftest` (two revisions, same worlds, first divergence), `armdiff` (arms differ only in goals), golden fingerprints | determinism tests in `tests/test_cybertron2*.py` |

## 3. What is fundamentally different

1. **Information is placed, and knowledge is state.** In cybertron 1 one global log is filtered per viewer. In cybertron2 an event
   happens at a place, only those present perceive it, and what they perceive is written into their own store. So "what did X
   believe on day d" is a record in cybertron2, where cybertron 1 had to rebuild it, but only if the state of day d is kept. The
   loss of per-day state therefore costs cybertron2 more than it would have cost cybertron 1: the most interesting thing it models
   (who knew what, when) is exactly what is overwritten every day.
2. **State is plain JSON with a single shape.** cybertron 1 pickled kernel objects, which couples checkpoints to the code that
   wrote them. cybertron2's state can be checkpointed as JSON, diffed, queried and published without the engine.
3. **One chokepoint with a cause context already exists.** Logging what passes through it is a few lines; cybertron 1 needed a
   phase-long refactor (review 09, the primitive layer) to get there.
4. **More calls per day, in more kinds.** A day can ask an agent several times (decide, up to two talk waves, lighten, a fuse call
   at night, a memory call at the end of a stretch), inside a conversation that spans days. A replay key must name the step and
   wave, as cybertron 1's did.
5. **No replay obligations yet.** 38.07 §3 recommended that obligations start at cybertron2's first run that matters. cybertron 1's
   experience says why: byte identity across code versions grew two or three paths for everything and still failed (the engine-12
   run diverged at its first call under engine 18, docs/engine_versions.md). The lesson is to replay within a code version only,
   and to freeze data, not to promise identity across versions.

## 4. What has been lost, ranked by what it costs us

1. **Recovery.** A crash, a usage limit or a reclaimed container loses the run and its cost. Cloud sessions are reclaimed when
   idle, and background runs only progress while a session is active (scenario_design §7).
2. **Counterfactuals.** No fork means no "same world, same history, one thing changed": the takeover benchmark's end-state shock
   forks (36 §2.5), interventions, and replicates that separate model noise from effect all depend on it.
3. **State at any point.** Only the final state survives. Holdings, claims, who was where, and above all each agent's beliefs on
   day d can only be guessed from result text.
4. **Verifiability.** Without a replay we cannot show that a run's logs are complete, or that two code revisions behave the same
   (difftest).
5. **Causes.** The chokepoint knows who did what for whom; none of it is written. Consequences ("this theft led to that feud")
   cannot be traced.
6. **Provenance.** Without a code sha, frozen data tables or segments, a result cannot be tied to the code and parameters that
   made it. The world now grows by editing data tables, so the tables a run used change under it.
7. **The dataset path.** No export tables, and the publisher does not match the engine's files, so runs cannot reach the site or
   be continued by others.

## 5. Measurements (scripted bots)

Run with `python -m cybertron2.engine run SPEC --out DIR --bots --days N` on 42b258e.

| World | People | Days | Final state | State gzipped | Largest parts |
|---|---|---|---|---|---|
| `hamlet_s1` | 10 | 20 | 489 KB | 47 KB | mind 366 KB, log 49, acts 37, know 11 |
| `region_s1` | 51 | 20 | 2,097 KB | 184 KB | mind 1,570 KB, know 129, people 116, log 116, acts 104 |

- **Checkpoint cost.** A gzipped state at every day's end costs about 1 MB per 20 days for the hamlet and 4 MB for the region.
  The c1 growth probe's checkpoints took 48 MB over 150 rounds.
- **Determinism.** Two runs of `region_s1` for 8 days give byte-identical `state.json`, `days.jsonl`, `turns.jsonl`,
  `perception.jsonl`, `memory.jsonl` and `run.json`. With models, replies arrive in completion order (`_parallel` uses
  `as_completed`); the engine indexes them by name, but only a replay test with recorded replies can show that nothing depends on
  that order.
- **Changes outside `apply`.** A coverage script wrapped `World.apply`, recorded the state paths each call changed, and compared
  them with everything that changed between dawns (`hamlet_s1`, 20 days).
  - Inside `apply`: containers' goods and wear, parcels' resources, crops, works and fertility, herds, buildings' fire and
    condition, people's death, offers created, agreements, institutions' offices.
  - Outside `apply`: `people/*/hunger` (21 days), `people/*/missed` (35), `offers/*/open` (5), `fuse_calls`, and by design
    `mind`, `know`, `acts`, `log`, `day`, `seq`.
  - So a log of `apply` calls alone cannot rebuild the state today. The eating and hunger code and the offer closing write
    directly.

## 6. Can we bring it back? Yes, and more cheaply than in cybertron 1

The design is in [proposals/run_record.md](../../cybertron2/proposals/run_record.md). In short: a run is its inputs (code sha,
frozen data tables, the resolved spec, the seed, every model reply keyed by day, step, wave and agent, every intervention) plus a
JSON checkpoint every day and append-only logs of events and changes. From that:
- every day's state is a file;
- every point within a day is the dawn checkpoint plus the changes up to it;
- every prompt is rebuildable from the state at that point and checked against its recorded sha;
- resume, replay, rewind, fork with interventions and replicates, History, export and publish follow, ported from cybertron 1 with
  fewer moving parts.
