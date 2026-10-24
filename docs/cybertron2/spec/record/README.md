# Spec: record

How a run is recorded, run, branched, viewed, exported, published and brought back: the journal, the runner's steps and
commits, the views built from the journal, fork and interventions, human play, export and import. Owner: **37.1**. The engine
code that writes the record (`cybertron2/engine/run.py`, `world.py`) is 37.4's (README rule 6): building waits on the board.

The run record must support (D1-1):
- everything cybertron 1's instrument did: the website from published data, analysis, fork, pause, resume, rerun;
- a map that plays through the world's history;
- exactly what an agent saw at any point;
- a human playing as an agent with the same context and verbs;
- running that is idempotent, resumable and cancellable.

| File | Covers | Compiled from | State |
|---|---|---|---|
| [journal.md](journal.md) | what a run stores, where and in what format; provenance and frozen data | proposals/run_record.md §2, §8 | **written** (D1-1, D1-4, D1-5) |
| [execution.md](execution.md) | steps, attempts, keyed requests and responders, writing as it happens, commits, resume, cancel, pause, determinism, replay | run_record.md §1, §7 | **written** (D1-1, D1-2, D1-4) |
| [views.md](views.md) | the state at any point, beliefs, an agent's exact context, the map, history, live views | run_record.md §3, §4 | **written** (D1-1, D1-2, D1-4) |
| [branching.md](branching.md) | rewind, fork, replicates, interventions, continuing under other code | run_record.md §7 | **written** (D1-1, D1-4) |
| [human_play.md](human_play.md) | a human answering an agent's requests | run_record.md §5 | **written** (D1-1, D1-4) |
| [exchange.md](exchange.md) | export (journal and view tables), publish, import and fetch, the website | run_record.md §6 | **written** (D1-1, D1-3, D1-4, D1-5) |

Background: review 39.01 (cybertron 1 and cybertron2 compared, with measurements). Overlap with `core/records.md` (37.4, to
compile): OPEN C-10.

*Current as of 24 Oct 2026: D1-1 to D1-5.*
