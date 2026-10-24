# Export, publish, import

## Summary

A run exports to Parquet as two kinds of table:
- journal tables, which lose nothing;
- view tables, for analysis and the site.

Publishing uploads both. Importing turns published journal tables back into a local run that can be replayed, viewed, forked and
continued from any committed step.

## Decided

- D1-1: the website is generated from published data, as cybertron 1's.
- D1-3: the inverse of publishing: a published run converts back to something that runs locally and can be forked and continued
  from any point.
- D1-4: as below.
- D1-5: Parquet for export, publishing and the site.

## Mechanics

- **Journal tables** mirror `run.db` one to one (journal.md: meta, data, segments, steps, requests, responses, blobs,
  checkpoints, events, changes, interventions), with a manifest carrying each table's row count and checksum.
- **View tables** are derived from the journal tables and can be regenerated:
  - `people_days`, `holdings` (container, item, qty, day), `claims`, `buildings`, `parcels`;
  - `acts`, `beliefs` (agent, day, about, what, as of), `messages` (said, told, heard by whom, where), `calls`;
  - `frames` and `layout` (views.md).
- **Publish:**
  - both kinds of table, a catalog row and the dataset card;
  - through the privacy gate (this machine's session, container, account and organisation ids and the account email replaced and
    then scanned for, as `cybertron2/publish_hf.py` and cybertron 1's publisher do);
  - only with `--push`;
  - runs stay under `experimental/cybertron2/` until Zach decides otherwise.
- **Import** rebuilds `run.db` exactly from the journal tables. **Fetch** downloads a published run (pinned to a dataset commit)
  and imports it. Checkpoints are JSON, so publishing and loading them is safe; cybertron 1 never published its pickled
  checkpoints and rebuilt them by replay.
- **Round trip.** Export, import and replay must reproduce the run byte for byte (a test).
- **The website** reads the published Parquet in the browser, as `site/lib/cybertron-data.js` does today. A cybertron2 run page
  shows the map, each agent's context by day, and the chronicle.

## Commands

```
python -m cybertron2.engine export RUN... --out DIR
python -m cybertron2.engine publish RUN... [--push]
python -m cybertron2.engine import DIR --out RUN
python -m cybertron2.engine fetch RUN_ID [--revision vX.Y] --out RUN
```

## Parameters

| Parameter | Value | Status |
|---|---|---|
| dataset folder | `experimental/cybertron2/` | decided (board Post 3) |

## What agents see

Nothing.

## Open

None beyond journal.md.

## Sources

proposals/run_record.md §6; cybertron 1: `cybertron/export.py`, `publish.py`, `fetch.py`, docs/data_format.md,
`site/lib/cybertron-data.js`.

*Current as of 24 Oct 2026: D1-1, D1-3, D1-4, D1-5.*
