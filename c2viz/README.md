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
2. **The renderer** (`pixel.js`) draws only that record, in layers:
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

Each scale returns hotspots (kind, id, box, label, info) so a page can label, hover and click.

```
python -m cybertron2.engine run cybertron2/specs/region_s1.yaml --out RUN --bots --days 14    # any run: it keeps its journal
python -m c2viz.build RUN                                                                    # RUN/viz.json and RUN/map.html
```

`map.html` is a bare preview: the map, labels, hover, day controls; click a place to go in, an exit to follow the road; in a
place, drag to pan and +/- to zoom. Query: `?day=N&node=<id>&z=<zoom>` (`&full` fits a place to the page).

| File | What |
|---|---|
| `ENGINE.md` | the engine model the visuals are built on; presentation choices; the audit of the first renderer |
| `model.py` | the journal to `viz.json`, through the engine's own functions |
| `layout.py` | presentation positions: places by travel days on the road graph; parcel sites by side and neighbours |
| `pixel.js` | the renderer (`C2Pixel.geom`, `C2Pixel.plan`, `C2Pixel.world`, `C2Pixel.node`) |
| `preview.html`, `build.py` | the preview page with the renderer and the data inlined |

Next (ENGINE.md §11): a person's way through the day (the parcels they pass, which is what they sense in passing), the acts in
the order the journal has them, and what one agent perceived.
