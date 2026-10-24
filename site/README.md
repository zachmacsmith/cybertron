# site

The Cybertron website: static HTML, CSS and ES modules (no node, no bundler), reading runs straight from the Hugging Face dataset.
The look is a pixel-art village at night: every run is drawn as its own generated village, every agent as a villager.

| Page | What |
|---|---|
| `index.html` | the night hero with the cast, stories from the runs (`stories.json` on the Hub), featured runs, open data |
| `runs.html` | every run in `catalog.json` as its own village, with search and filters |
| `run.html?id=RUN_ID` | one run on a shared day clock (`#section[/target]@day`): Front page, Chronicle, People (a villager's dossier and diary at `#people/Name`), Letters, Laws, The square, Data |
| `experiment.html`, `notes.html` | write-ups (coming soon); `note.html?slug=` redirects to `notes.html#slug` |

## Run it locally
```bash
python site/build.py                                   # notes/index.json
python -m cybertron publish RUN... --card site/cards.yaml --stories site/stories.yaml --with-viewer-json --staging cybertron/out/site-data
ln -sfn ../cybertron/out/site-data site/_data            # a local copy; the site reads it with ?data=local
python site/serve.py                                   # http://localhost:8790, caching off
```
The site reads the published dataset on the Hub; `?data=local` reads `_data` instead.

## Pieces
- `assets/base.css`, `assets/chrome.js`: tokens, type, the header and footer every page shares. Pixel headings use "Cyber Digits"
  (Nunito's digits) before Pixelify Sans, so numbers stay readable.
- `assets/scene.js`: the generated pixel scenery. `backdrop()` draws the night landscape; `village()` draws a run's village from its
  cast (homes for its agents, buildings for its roles, laid out once for the largest population so it grows day by day).
- `assets/core/`: `model.js` turns a run's data into days, ballots, threads and law histories; `villagers.js` draws each agent
  (class hat and prop, colours from its name); `square.js` is the animated society map; `text.js` the shared text helpers.
- `assets/run/`: the run page. `app.js` is the shell (masthead, section bar, day clock, routing); one module per section:
  `front.js`, `chronicle.js` (chronicle, laws, letters), `people.js` + `diary.js`, `square.js`, `dataview.js`. Each section's CSS
  is scoped to its view (`.v-front`, `.v-chronicle`, `.v-people`, `.v-square`).
- `assets/data.js`: where the data comes from. A run page loads `viewer-core.json.gz` (the run without the agents' private reasoning)
  and fetches `reasoning/<agent>.json.gz` when that agent's diary opens; runs uploaded before the split fall back to `viewer.json`.
- `cards.yaml`: curated titles, descriptions, tags and featured flags for `charter publish --card`.
- `stories.yaml`: the stories registry (title, subtitle, verbatim quote, agent, run). `python -m cybertron publish --stories site/stories.yaml --push`
  uploads it as `stories.json` on its own.
- `lib/cybertron-data.js`: a reader for the published tables (catalog, run tables, threads, inboxes), used by `demo/`.

## Temporary (until export schema 2 lands)
- The run page reads `viewer.json` (written by `publish --with-viewer-json`, split into `viewer-core.json.gz` and `reasoning/`;
  `publish --resplit DIR` writes the split files for an existing staging directory). Once the export tables carry everything, build
  the same input from them (one adapter) and drop the flag and the files.
