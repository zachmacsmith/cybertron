# site

The Cybertron website: static HTML, CSS and ES modules (no node, no bundler), reading runs straight from the Hugging Face dataset.

| Page | What |
|---|---|
| `index.html` | the experiment, a carousel of stories from the runs (`stories.json` on the Hub), featured runs, notes, open data |
| `runs.html` | the registry: every run in `catalog.json`, with search and filters |
| `run.html?id=RUN_ID` | one run, on a shared clock (`#section/target@round`): Front page, Chronicle (one edition per round), People, Correspondence, Laws, The square, Data |
| `notes.html`, `note.html?slug=` | analysis posts: markdown files in `notes/` with front matter (title, date, summary, draft) |

The design is Broadsheet. Swiss and Night remain as CSS variables in `assets/site.css` (`?theme=swiss|night`, `?themes` shows the switcher).

## Run it locally
```bash
python site/build.py                                   # notes/index.json, assets/mascots.svg
python -m cybertron publish RUN... --card site/cards.yaml --stories site/stories.yaml --with-viewer-json --staging cybertron/out/site-data
ln -sfn ../cybertron/out/site-data site/_data            # the site reads _data on localhost, the Hub elsewhere
python site/serve.py                                   # http://localhost:8790, caching off
```
`?data=hf` reads the published dataset instead of `_data`; `?data=URL` reads any copy.

## Pieces
- `lib/cybertron-data.js`: the data layer (catalog, run tables, channels, threads, inboxes, turns); commit-pinned, cached, lazy.
  Follows export schema 2 (docs/data_format.md) and derives messages/channels from `events` for older exports.
- `assets/run/`: the run page. `model.js` turns a run's data into rounds, ballots, threads and law histories (the event semantics of
  cybertron/viewer/template.html); `views.js` renders each section as of the shared round; `square.js` is the animated society map;
  `mascots.js` draws each agent.
- `cards.yaml`: curated titles, descriptions, tags and featured flags for `cybertron publish --card`.
- `stories.yaml`: the stories registry (title, subtitle, verbatim quote, agent, run). `python -m cybertron publish --stories site/stories.yaml --push`
  uploads it as `stories.json` on its own; the home page shows them in a new random order on every visit (`assets/stories.js`).

## Temporary (until export schema 2 lands)
- The run page loads `viewer.json` (written by `publish --with-viewer-json`) into `assets/run/model.js`. Once the export tables carry
  everything, build the same input from them through `lib/cybertron-data.js` (one adapter) and drop the flag and the file.
- Conversations use the schema-1 fallback (messages derived from `events`) until the exporter writes `messages`/`channels`.
