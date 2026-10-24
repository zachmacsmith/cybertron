# 38.29: R1 of the run record built (the journal, and every physical write through `apply`)

Session 37.4, 24 Oct 2026. Built from 37.1's spec/record/ (D1-1 to D1-5) and proposals/run_record.md "Order of work" R1, which was
queued for 37.4 on the board (OPEN Q-RR6). Code on `wp/cybertron2`: cybertron2/engine/journal.py (new); world.py, run.py, night.py,
forests.py, farm.py, life.py, roads.py. Tests: tests/test_cybertron2_journal.py (4); 156 cybertron2 tests pass.

## 1. What was built

| Spec (journal.md, execution.md) | Built |
|---|---|
| one SQLite file per run, WAL, JSON values (D1-5) | `run.db` in the run directory, beside run.json and the jsonl files; WAL, `synchronous=NORMAL`; readable while the run writes |
| inputs: code, frozen data, resolved spec, seed | `meta`: provenance (git sha, dirty flag, diff sha, a sha per `cybertron2` module, a code sha over them, python), the resolved spec, the seed; `data`: every upper-case table in data.py and signs.py, as they stood at the start |
| segments | one `start` segment: first step `d0.dawn`, code sha, the responder of each person (`model:<id>` or `bot`) |
| steps, attempts, commits | the day's steps `dawn`, `decide`, `talk.0`, `talk.1`, `work`, `settle`, `night`, `memory`, keyed `d<day>.<step>`; each opened as attempt 1 and committed in one transaction with its checkpoint |
| checkpoints | the whole `World.s` and the runner's state (each agent's running conversation, the cost, what the day's steps carry between them), as compressed JSON; in the runner's part, texts over 200 characters are blobs referred to by sha, so prompts repeated across steps are stored once |
| requests and responses by key | `d<day>.<step>.<agent>.<n>` for every call: decision, talk, lighten, fuse, memory; the request holds the conversation id (`<agent>@<first day>`), its index in it, and the system, schema and new message as blobs; the response holds every attempt (raw text, error, latency), the parsed reply, the thinking, the usage and how it was sent. A bot's failure is recorded as its answer |
| events and changes with their cause | every `World.event` and every `World.apply` call, as they happen, tagged with step and attempt; a change made inside another primitive carries `"within": true` in its cause, so a replay applies only the outer one |
| no behaviour change | 20-day bot runs of wide_s7, hollins2_s8 and region_c_s27 give byte-identical turns, days, perception, memory and state.json with and without the journal |

## 2. Every physical write through `apply` (OPEN Q-RR4)

Review 39.01 §5 found three writes outside `apply` (hunger, missed meals, offers closing). The engine has grown since; the same
coverage method (wrap `apply`, compare the state between calls, nested calls excluded) over 16-day bot runs of six worlds, and a
search of the code, found these, now all primitives:

| Write | Now |
|---|---|
| hunger, missed meals, eating raw, the cold's fall | `harm` (hunger), `set` (missed, ate_raw) |
| offers lapsing at night | `close_offer` (a lapsed offer now has `closed: "lapsed"`, the only difference in the outputs) |
| nature's night: plants, grass and game regrowing; trees growing, shedding, rotting, thrown by gales; a wood turning to scrub; dung | `set_res` (new), `set` (cover), `add_res` (brash) |
| a hearth's warmth | `set` |
| journeys: the choices at departure, an infant carried, where one was last, what one noticed, a day lost to trouble | `transit` (new) |
| traces left on a road, and their fading | `traces` (new) |
| the house as last seen, an arrival's day | `set` |
| growing up, the model at coming of age, care of a child, conception, a pregnancy lost, the gap after a birth | `set` |
| the members' naming of a head ending | `office` (fields `head` and `succession`) |

The same bot runs are byte-identical before and after (apart from `closed: "lapsed"`). The knowledge stores (`mind`, `know`), the
logs and the action record are still written by perception, as journal.md says.

## 3. Measurements

| World (bots, 20 days) | People | run.db | Checkpoints | Blobs | Changes | Events |
|---|---|---|---|---|---|---|
| wide_s7 | 23 | 17.8 MB | 140, 11.1 MB | 2.5 MB | 7,356 | 1,919 |
| hollins2_s8 | 20 | 14.5 MB | | | | |
| region_c_s27 | 51 | 39.0 MB | 140, 26.0 MB | 5.0 MB | 9,446 | 2,003 |

A checkpoint at every step costs about 80 KB a step for 23 people and 185 KB for 51, so a 120-day run of the Wide Country would
keep about 100 MB, most of it checkpoints (for OPEN Q-RR1: a checkpoint each day plus the day's changes would be about a seventh).
A model run's checkpoints are larger by its conversations' messages, which are blobs and stored once.

## 4. Left for R2, and points for 37.1

- Reads during the run do not yet go through the frozen copy of the data tables; the copy is stored, and R2's replay will read from it.
- The `within` mark is kept inside the change's cause (journal.md's columns unchanged); a `depth` column would be cleaner if 37.1
  prefers it.
- Resume, cancel, pause, replay and the `--as` responders are R2 and R3; nothing reads the journal yet but the tests.
- The run that was going when this was built (runs/w1_wide) started on the earlier code and has no journal.

*Current as of 24 Oct 2026.*
