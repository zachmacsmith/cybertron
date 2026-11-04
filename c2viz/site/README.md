# The c2viz site: browse runs and explore them

```
python -m c2viz.site.server --runs DIR            # http://127.0.0.1:8791
```

A list of every run with a journal: the local ones (each folder under `--runs` with a `run.db`, two levels deep; default `./runs`
or `$C2VIZ_RUNS`) and the published ones (each `<folder>/<run>/` in the dataset with `journal/*.parquet` and `manifest.json`, as
`python -m cybertron2.engine exchange publish` writes them). Choose a run to explore it:

1. **A published run is fetched and imported.** It is fetched at the dataset revision the list was read at, so a run never changes
   under you. The engine's own importer (`exchange.import_`, through `c2viz.touch`) rebuilds its `run.db`, checked against the
   manifest.
2. **The model builds it in parts.** `c2viz.model.RunModel` builds the head first: the world, the tables, a generated world's
   ground truth, and every building the run ever had, so each place's plan is fixed whichever days are loaded. It then builds
   each day, in order, replaying every change through the engine.
3. **The page streams the days.** The first day shows as soon as it is built; the slider grows as the rest arrive.

Every part is cached on disk (`--cache`, default `~/.cache/c2viz-site`), keyed by the journal and by c2viz's own code, so a run
seen before opens at once and a changed model builds it again.

| Flag | |
|---|---|
| `--runs DIR` | a directory of local runs (repeatable) |
| `--repo OWNER/NAME` | the dataset of published runs (default: the project's; or `$C2VIZ_REPO`) |
| `--folder PATH` | the folder in it that holds runs (default `experimental/cybertron2`; or `$C2VIZ_FOLDER`) |
| `--revision REV` | the dataset revision to read (default `main`, pinned to the commit it resolves to) |
| `--no-hub` | local runs only |
| `--host`, `--port` | where it listens (default 127.0.0.1:8791) |

A run moved to its own dataset is `--repo` (and `--folder` if its layout changes); nothing else.

| File | |
|---|---|
| `server.py` | the catalog (local and published), fetching and importing, building parts in order, the cache, the JSON API |
| `index.html` | the list of runs: search, local or published, what each run is |
| `run.html` | one run, streamed: derived from `../preview.html` (the same controls, the same renderer) |

API: `GET /api/runs`; `GET /api/run/<id>/head`, `/api/run/<id>/day/<d>` (built when first asked, then cached);
`/api/run/<id>/status`. Run ids are `local:<name>` or `hub:<run>`.

A generated world's ground truth is drawn when its `.cells.npz` lies beside the run. Published runs do not carry their cells yet
(engine_gaps G-33), so they are drawn with the derived landscape.
