# c2viz: the cybertron2 world as a pixel map across time

The core visuals for a central map of a cybertron2 world: no site, only the drawing, in the look of the site's night-village
design (`wp/site-v2`, `site/assets/scene.js`). **Drawn from the engine, never fitted by eye:** what the engine is and what may be
drawn of it is in [ENGINE.md](ENGINE.md) (state, mechanics, the spec's end state for buildings, presentation choices named as such).

Two halves, so every rule stays in the engine:

1. **The model** (`model.py`, Python) reads a run's journal (`run.db`), rebuilds the world at each day's end and asks the engine
   for everything it computes: calendar and weather, snow lying, what each parcel, building, person, herd and thing is like
   (`signs.context` and its siblings, the derivations the agents' signs are made from), where a person is (`things.spot_of`),
   where a traveller is (`roads.position`), landmark challenges, holders from claims. Buildings follow the spec's end state
   (rooms, footprints, ground in spaces: economy/buildings.md), read from the state when the engine has rooms and derived by the
   spec's seeding rule until then (marked `derived`). It writes `viz.json`: the engine's tables, the static world, one record a day.
2. **The renderer** (`js/`, bundled by `build.py`) draws only that record, in layers:
   - **places**: each place's ground plan from its parcels' sizes (one scale for all covers), neighbours (`adj`: neighbours share a
     border, others have wild ground between) and sides; a chain of water parcels as one river; the region by travel days;
   - **land**: each parcel by its cover that day and its stocks (S/K): trees in proportion to standing wood and stumps where it was
     felled, grass grazed down, fallen wood, scrub, seams; fields in strips with the engine's crop stage (new, green, high, ripe,
     rotting, blighted, killed), the sown share, the reaped share as stubble with stooks, dug ground, fallow; ditches and terraces
     for works done; fences and walls by level and gate; clearing; the day's weather (rain, heavy rain, fog, snow, gale) and snow
     lying;
   - **structures**: buildings from their rooms at a fixed size a space (structure, condition, the frame of one being built,
     new, the door, chimneys and smoke, a water wheel at the water, millstones, an anvil, a woodpile from its store, the day's
     work at it), placed on their parcel's ground (one that does not fit is shown spilling over, and says so); things lying
     (bodies, graves, sunk graves, cairns, carcasses, bones, heaps, goods under brush or buried); roads leaving from their ends'
     parcels, hidden ways faint until worn;
   - **beings**: people (5 x 9 close up, 3 x 6 on the region's map) on the parcel the engine says they are on, or at their door,
     with the tool of their act, speech, hunger, a wound, pregnancy, a load; cattle head by head as cows, oxen, bulls and calves,
     ribs when hungry; travellers at the middle of their stretch;
   - **marks**: the day's events by how far they reach (a person, a building, a parcel, the place).

**A day as it happened** (close up, `C2Pixel.nodeAt`; ENGINE.md §11): talk first, then each act in the journal's order, its change
landing on the land as it ends, each person walking the engine's route (D4-62) between the parcels of their acts with the tool of
the act in hand; dusk; night with the night log's beds lit. In the preview, "☀ the day" plays it; the clock slider scrubs it.

Each scale returns hotspots (kind, id, box, label, info) so a page can label, hover and click.

```
python -m cybertron2.engine run cybertron2/specs/region_s1.yaml --out RUN --bots --days 14    # any run: it keeps its journal
python -m c2viz.build RUN                                                                    # RUN/viz.json and RUN/map.html
python -m c2viz.build RUN --land WORLD.cells.npz                                             # a generated world: drawn from its cells
```

`map.html` is a bare preview: the map, labels, hover, day controls; click a place to go in, an exit to follow the road; in a
place, drag to pan and +/- to zoom. Query: `?day=N&node=<id>&z=<zoom>` (`&full` fits a place to the page).

## How it is built: modular, because the engine will keep changing

```
cybertron2 engine ── touch.py ──► source.py ─► extract.py ─► model.py ──► viz.json ──► js/ (the renderer) ──► a canvas
   (only here)        (journal)   timeline.py  spec_rooms.py   (schema.py, SCHEMA.md)     (vocab.js: the engine's words)
```

- **Where the engine is touched:** `touch.py` is the only file that imports `cybertron2`: every engine function, table and class
  c2viz uses is named there, and `touch.check()` lists any the engine no longer has. `source.py` is the only reader of the
  journal's tables. `extract.py` and `timeline.py` read `World.s` (its shape is documented in ENGINE.md).
- **The contract:** the renderer reads only `viz.json` (SCHEMA.md, `schema.py`); it never sees engine state.
- **The engine's words** the renderer draws differently (techniques' tools, fittings that show a fire, river names, crop stages,
  road terrains, quiet events) are all in `js/vocab.js`; an unknown word is drawn plainly.
- **A generated world's land** is read from the generator's cells by `ground.py` alone (`viz.json` `land`), and drawn by
  `js/ground.js` into the same plan the derived landscape gives, so the rest of the renderer does not know which it has.
- **The spec's end state** for buildings (rooms, spaces, ground) is in `spec_rooms.py` alone, until the engine stores rooms.
- **When the engine changes:** run `python -m pytest c2viz/tests -q`. It checks the touchpoints, builds a short real run to the
  contract (every change must replay), and checks the renderer's modules load in order. Then fix, in this order: `touch.py`
  (a renamed or moved function), `extract.py` / `timeline.py` (a changed state shape), `js/vocab.js` (a new or renamed word).
  The renderer's other modules should not need to change.

| File | What |
|---|---|
| `ENGINE.md` | the engine model the visuals are built on; presentation choices; the audit of the first renderer |
| `SCHEMA.md` | viz.json, the contract between the model and the renderer |
| `touch.py` | every engine function, table and class c2viz uses; `check()` |
| `source.py` | the run journal: meta, steps, the world at a step, changes, speech |
| `extract.py` | a day's records (parcels, buildings, herds, things, people, roads, events) |
| `timeline.py` | a day as it happened: the work step's changes replayed through the engine, act by act |
| `ground.py` | a generated world's ground truth (the generator's cells beside its world file): layers, sites, rivers, roads by the generator's rule (ENGINE.md §12) |
| `legacy/` | runs from before the journal, replayed to one from their recorded replies |
| `video/` | a walk-through video of a run |
| `spec_rooms.py` | the spec's building model (rooms, spaces, ground), derived until the engine has it |
| `schema.py` | the contract's version and `validate` |
| `model.py` | the run to `viz.json` (orchestration and the CLI) |
| `layout.py` | presentation positions: places by travel days; parcel sites by side and neighbours |
| `js/` | the renderer, one module a concern, loaded in `js/MANIFEST` order: core, vocab, palette, sprites, buildings, model, roads, geom, land, plan, region, ground, node, day, world, api |
| `preview.html`, `build.py` | the preview page with the bundled renderer and the data inlined (`--js` writes the bundle alone) |
| `tests/` | the checks above |

Next (ENGINE.md §11): a person's way through the day (the parcels they pass, which is what they sense in passing), the acts in
the order the journal has them, and what one agent perceived.
