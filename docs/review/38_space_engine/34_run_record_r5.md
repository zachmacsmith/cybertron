# 38.34: R5 of the run record built (views, export, import, publish, fetch)

Session 37.4, 24 Oct 2026. From spec/record/views.md and exchange.md (D1-1, D1-3, D1-4, D1-5). Code: cybertron2/engine/views.py,
exchange.py (new); commands in run.py. Tests: tests/test_cybertron2_exchange.py (4). pyarrow and huggingface_hub are the
`publish` extra in pyproject.toml.

## Views (views.py): the read-only API on a journal

`state(run, step)`, `beliefs(run, agent, step)`, `context(run, key)` (the exact input to a request: system text, schema, the
conversation's earlier messages and raw replies, the new message, and the answer), `requests(run, agent, pending)`, `steps`,
`events(kind, place, actor, days)`, `changes(primitive, actor, days)`, `calls(agent)`, `layout(run)` (a seeded spring layout of
the road graph, parcels by side, buildings on their parcels), `frames(run)` (one a day: each person at a node or along a road by
days travelled; the day's events at their places). Commands: `context RUN [KEY] [--agent NAME]`, `frames RUN --out DIR`,
`dump RUN --table events|changes|calls|steps`.

## Export, import, publish, fetch (exchange.py)

- `export RUN... --out DIR`: `journal/<table>.parquet` one to one with run.db (types kept, blobs and checkpoints as compressed
  bytes), `views/<table>.parquet` (people_days, holdings, buildings, parcels, claims, messages, calls, layout, frames), a
  manifest with row counts and sha256 of every file, and run.json.
- `import DIR --out RUN`: checks every journal file against the manifest, then rebuilds run.db row for row.
- `publish RUN... [--push]`: stages exports under `experimental/cybertron2/` with the dataset card; this machine's session,
  container, account and organisation ids and the account email are replaced in every text and inside every compressed blob, then
  the gate reads every Parquet value and decompressed blob back and refuses on any hit; uploads only with `--push` and HF_TOKEN.
  Runs from before the journal are staged as their files, as before.
- `fetch RUN_ID [--revision R] --out RUN`: downloads a published run's journal at a pinned revision and imports it.

Tests: export, import and replay reproduce the run (every table identical, every checkpoint replayed byte for byte); a tampered
file is refused; a model run's context at d1 holds day 0's exchange and exactly the message the model was sent; the view tables;
publishing redacts a private id that the unredacted export would have leaked, and the gate finds none.

Not built: the `beliefs` view table (beliefs are read through `beliefs()`), and R6 (the site's run page; dropped by Zach).

*Current as of 24 Oct 2026.*
