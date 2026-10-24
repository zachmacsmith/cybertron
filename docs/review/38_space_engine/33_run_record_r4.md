# 38.33: R4 of the run record built (rewind, fork, replicates, interventions, continue, branches)

Session 37.4, 24 Oct 2026. From spec/record/branching.md (D1-1, D1-4). Code: cybertron2/engine/branch.py (new); journal.py,
run.py, world.py (`rng` salt). Tests: tests/test_cybertron2_branch.py (4).

| Command | What it does |
|---|---|
| `rewind RUN --to STEP --out NEW` | copies the run's journal and cuts everything after STEP (steps, checkpoints, requests and answers, events, changes); `resume NEW` plays on live from there. The parent is untouched |
| `fork RUN --at STEP --out DIR [--apply iv.yaml] [--as NAME=model:<id>\|bot] [--replicates K] [--no-play]` | a rewind that also stores interventions, other responders and a seed salt, then plays on (earlier requests answered from the parent's record) |
| `continue RUN --at dN.memory --out DIR` | restores the world and the runner (conversations, cost, systems) from the checkpoint at the end of a day and plays on under the current code; a `continue` segment records both code shas |
| `branches RUN` | the run's segments and the runs branched from it (forks, rewinds, continues found beside it) |

- **Interventions** are `{after: STEP, op: <primitive>|event, place, args, note}`, applied through `World.apply` inside a cause
  `intervention` after their step's commit, on every play of the run (so resume and replay reproduce them), and recorded as applied
  once with a digest of the state.
- **Replicates** salt every draw after the fork point (`World.rng` adds `rep<k>` from the world state, so a checkpoint keeps it):
  the past is shared, the world's chances after it differ.
- **Responders** at the fork: an agent's model is changed through `set` at the fork point. `human` comes with R3.

Tests: a rewind resumed ends as its parent did, and the parent is unchanged; a fork that burns a store at d1.memory diverges, logs
one intervention change, and replays clean; two replicates share the checkpoint at the fork point and end differently; `continue`
from d2.memory under the same code ends exactly as the parent.

*Current as of 24 Oct 2026.*
