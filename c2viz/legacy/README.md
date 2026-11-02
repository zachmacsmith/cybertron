# Runs from before the journal

Runs made before R1 (0408831, 24 Oct 2026) have no `run.db`, only their logs (run.json, turns.jsonl, days.jsonl, memory.jsonl).
c2viz reads only journals, so such a run is replayed: the engine runs its spec again and each call to an agent is answered with
the reply the run recorded (decision, each talk wave, lighten, fuse, memory), so the run gets a journal. Nothing else is fed in:
the world, its draws and the order of acts are the engine's.

```
git worktree add ../eng 0408831                     # an engine at or just after the run's own code, with the journal
PYTHONPATH=../eng python c2viz/legacy/replay.py HF_RUN_DIR OUT --days N
python c2viz/legacy/compare.py HF_RUN_DIR OUT       # the replayed night records and results against the published ones
PYTHONPATH=../eng:. python -m c2viz.model OUT --days N
PYTHONPATH=. python c2viz/legacy/routes.py OUT OUT/viz.json   # routes by today's engine's rule (D4-62), marked routes_derived
```

Build the viz with the engine the run ran on (today's may refuse some of its changes); `routes.py` then asks today's engine for
the route rule, which older engines lack.

**w1_wide** (review 38.31): replayed on 0408831 for days 0 to 24, every call answered, no reply left over; every agent's results,
plans and night lines identical to the published ones on all 25 days, and the night records identical but for one label (a lapsed
offer says `closed: "lapsed"`, which c1b9878 added: w1 ran on the code just before it). All 24 good days' changes replay.
