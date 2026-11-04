# c2viz: the cybertron2 world visualiser, work log (37.1)

Zach (24 Oct): build the core visuals for a central map of the whole cybertron2 world across time:
- space, environments, nodes and parcels, buildings, the entities on them (objects, herds, plots and their states), what actions
  look like;
- different scales: a world map, then click into a node for more detail, and edges too;
- the style of the old site's map;
- not editing the website: a standalone visualiser the site can use later.

Code: top-level `c2viz/` on `wp/cybertron2`. It is not under `cybertron2/`, which is 37.4's (README rule 6); it reads the
engine's state and imports nothing it changes.

## Plan

| Step | What | State |
|---|---|---|
| 1 | `c2viz.capture`: the state at each day's end (a stand-in for the journal, spec/record) | done |
| 2 | `c2viz.layout`: world positions from roads (days), parcel cells per node (side, height, adjacency, size) | done |
| 3 | `c2viz.frames`: viz.json (static world, layout, one record a day) | done |
| 4 | the pixel renderer (`pixel.js`): the region and a place, in the site-v2 look; a bare preview page | second version |
| 5 | acts and events drawn (tools in hand, travel along roads, night events), changes from day to day | partly |
| 6 | screenshots with Playwright on a bot run; README; a board post | |

## Log

- 17:13 UTC: steps 1-3. region_s1 with bots, 12 days: the capture is 1.3 MB gzipped; viz.json is 695 KB. Roads of one
  day come out about 200 px apart in the world layout.
- 17:36 UTC: Zach rejected the first viewer (a broadsheet diagram styled from the old site): the map must look like the new site's
  pixel art (`wp/site-v2`, pushed 24 Oct: the night-village design, `site/assets/scene.js`), a real map with environments, and
  only the visuals at the core, not a website. Replaced it with `pixel.js`:
  - the region: places in country made from their own parcels, roads, travellers, fog over unexplored places;
  - a place: parcels as land with terraces; crops, fences, woods thinning, buildings by structure, condition and fire; herds,
    things, people holding their tools;
  - a bare `preview.html` with labels, hover, day controls and click-through.

  Checked with screenshots of region_s1 (bots, 12 days); no console errors.
  - Known: water parcels draw as lakes even when they are brooks; the world's scrub and terrace detail is busy.
  - Not yet: animation within a day, a road view, night events beyond a marker, a run with model agents.
- 17:57 UTC: second version, after Zach's review: the close-up was far too far out to see what happens on a parcel; the land
  looked the same everywhere; houses did not follow how the world places them; fog hid unexplored places that exist.
  - One ground plan per place, read from the parcels' sizes, neighbours and sides (no coordinates in the world): area by size,
    neighbours share borders, non-neighbours get wild ground between them, a river chain is one band and one river.
  - Buildings in lots (built ground 6 a unit of size, data.py), spread through the parcel. Checked against the engine and the
    worlds: buildings share their village's built parcel (region_s1: 7 on the Square; wide_s7: 4 on wy_green); none takes a
    parcel of its own.
  - Close-up at a fixed scale with pan and zoom; people 5 x 9 with their state; herds head by head by kind; things lying about.
  - The region at one scale for every place; people as the small figures; places' character by biome; no fog.
  - Checked with screenshots of region_s1 (bots, 12 days); no console errors. The places are small in their territories on the
    region's map: at one scale, a day's travel is far wider than a village.
- 18:25 UTC: rebuilt on the engine, at Zach's instruction that visuals be grounded in how the engine works, from the general model
  up. Five read-throughs of the engine (land and environment, buildings and goods, people and herds, actions, senses) gave
  `c2viz/ENGINE.md`; CLAUDE.md now carries the rule. Buildings follow the spec's end state (rooms, spaces, ground), derived from
  today's state by the spec's seeding rule until the engine stores rooms.
  - `model.py` replaces `capture.py` and `frames.py`: it reads the run journal and asks the engine (signs.context and siblings,
    spot_of, weather, roads.position, claims) for everything computed.
  - `pixel.js` draws only that record. The audit of the first renderer (ENGINE.md §10) is fixed: reaped share from `area_left`,
    sown share, the engine's crop stages, woods by S/K, cattle by role, buildings from rooms, scrub lots, spot_of, weather and snow
    from the engine, roads from their ends.
  - `layout.py`: the world layout diverged for 14 places (wide_s7); now a stable stress majorisation.
  - Checked on two bot runs of the current engine (region_s1 and wide_s7, 14 days each, no model calls); no console errors.
    Found by the model, not visible before: region_s1's Willow Holt starts as scrub and is cleared to a field by day 6; Deep Wood
    is felled to scrub by day 12; Coppergate's yard is overfull under the spec's ground rule.
- 01 Nov 2026 19:20 UTC: made modular at Zach's instruction (the engine will keep changing). `touch.py` is the only file that imports the
  engine (`check()` lists what it no longer has); `source.py` the only reader of the journal; `extract.py`, `timeline.py`,
  `spec_rooms.py`, `schema.py` (SCHEMA.md: the contract), `model.py` (orchestration). The renderer split from one file into
  fourteen modules (`js/`, explicit imports and exports, bundled in MANIFEST order), the engine's words it knows in `js/vocab.js`.
  Checked: the same viz.json for both runs and the same pixels for 17 views (hashes before and after); `c2viz/tests` (touchpoints,
  a 2-day run to the contract with every change replayed, module order) pass.
- 02 Nov 2026 16:48 UTC: the real Wide Country run (w1_wide, Hub `zachmacsmith/charter-runs`, review 38.31) as a video. No
  published run has a journal; w1 is the only Wide run, and only its days 1 to 24 are agents acting. `c2viz/legacy/`: the run's
  spec replayed on 0408831 with every agent call answered by the reply the run recorded. Every result, plan and night line is
  identical to the published ones on all 25 days, and so are the night records, except a lapsed offer's `closed` label (c1b9878).
  So w1 ran on 13ccb2e, and the journal is a faithful reconstruction.
  - `timeline.py`: a thing made again on replay keeps the id the run gave it. Events advance the id counter without being
    changes, so a replayed `raise` took another id and later changes to it failed.
  - `timeline.py`: routes for runs from before D4-62 by the engine's rule, marked `routes_derived`.
  - Built with the run's own engine, all 24 days' changes replay; today's engine refuses 29 transfers of that run (a stock rule
    changed since), which is why a legacy run is built on its own engine.
- 02 Nov 2026 17:54 UTC: a generated world is drawn from its ground truth, at Zach's request. The landscape generator
  (cybertron2/landgen, 37.2) keeps the cells a world was drawn from beside it.
  - `ground.py` reads the cells (height, water, rivers, wetness, terrain, cover, parcel of each cell) and each site.
  - Roads are recovered with the generator's own road rule; on twin bays all 6 leave by the world file's parcels.
  - `js/ground.js` fills the region plan from these, so the painter, terraces, woods, peaks and villages are unchanged.
    Places stand at their real sites, larger than life, moved off open water only as far as their drawing needs. Close-ups
    take the same ground.
  - Schema 2 (`land`, optional).
  - Hand-made worlds render pixel-identical to before (5 views of w1).
  - Engine gaps G-32 (road cells not saved) and G-33 (a run does not carry its cells).
  - Test: twin bays generated, packed, every road matched.
- 02 Nov 2026 18:07 UTC: roads laid in steps so the two scales agree (ENGINE.md §13), at Zach's report that close-up roads
  tangled, crossed water, ended in elbows and left from a different side than on the region's map. The cause was two
  independent drawings: the close-up headed for its end parcel's side, the region for the other place.
  - One heading and exit point per road and place, from the region (`roadOut`).
  - Inside a place, the cheapest way from the green through the parcel it leaves by to that exit: cheap along hedges and field
    edges, dear through crops and woods, rivers crossed once, water gone round. Roads laid earlier are cheap, so later ones
    join them.
  - Smoothed, each road drawn only where it is its own; the region draws the same lines.
  - `geom.js` is now the parcel plan alone; `village.js` lays roads, green and buildings on it.
  - Close-ups of generated worlds take the region's woods.
  - Audit over every place of twin bays and w1: exits identical at both scales; open water only where Wealdmere's roads skirt
    the mere they leave by.
- 02 Nov 2026 18:45 UTC: waterways, lakes and woods, at Zach's questions. Waterways did not match:
  - a generated world's river parcel ran in a direction guessed from its graph while the generator's river passed elsewhere
    (Northby: 18 and 111 px apart);
  - a hand-made world's village river stopped at the edge of its drawing on the region map (Wynford: 72 and 101 px short).

  Now a river parcel lies on the generator's own river (its course is that river, in the plan's pixels), and a hand-made
  world's village river goes on beyond its drawing; every one meets the region's river at 0 px.
  - Round lakes and woods in hand-made worlds were c2viz's: parcels drawn as circles and rounded boxes; now lobed outlines.
  - Found on the way: the area fitting oscillated, so a generated world's built parcel could end with none (Northby 0 px,
    Welmere 19 against 2,600). It existed before today. Now damped, and every parcel of both worlds is within 7% of its size.
  - The round shapes in generated land are the generator's (deep forest beyond a fixed 12 km of every settlement; radial
    bumps for hills and lakes); measured, drawn as they are, and recorded as engine gap G-34.
- 02 Nov 2026 19:20 UTC: worlds that have not been run can be drawn (`model.build_world`, `--world`): as the world file makes
  them, at dawn of day 0, with a generated world's ground truth.
  - 17 worlds generated, one per configuration the generator builds (gated valley refused at seed 3 by its own physics check;
    seed 4 passes), varied in seed, size (45 to 60 km), villages (3 to 5) and season; none run.
  - Every road of all 17 (119) recovered by the generator's rule leaves by the world file's parcels.
  - Gallery in the scratchpad (index, a page per world, contact sheet). Ring basin's lake and the isthmus's two landmasses
    show G-34's circles.
- 03 Nov 2026: the regenerated worlds (37.2's temperate landscapes, D2-191) drawn from their new layers.
  - Each cell's ecosystem sets its colour, look and trees; a wood's depth thins its edge and darkens its core.
  - Fixed my three faults: snow by the generator's temperature and the season (no summer snow); heather purple only in
    flower; a place levelled and cleared under its drawing, not in a disc.
  - 18 worlds (rift and delta now wait; estuary and fens, sand country, upland and moor added), all 113 roads matched.
  - Measured against the first batch: wood 30% in 17 of 18 worlds (frontier 60%), was 36 to 86%; lowland lakes 0, were 27 to
    153; fen with islands 16% fen, was 0.
- 04 Nov 2026: the c2viz site (`c2viz/site/`), at Zach's request: browse runs and explore any of them as its days are built.
  - Lists local journals and runs published with journals (the dataset and folder are flags). 55 are on the Hub now, at
    3e449ed.
  - A published run is fetched at a pinned revision and imported by the engine's importer. `model.RunModel` builds its head
    (with every building the run ever had, so plans do not shift as days arrive), then each day, cached by journal and code.
  - The page streams the days in. Checked: published c1_combe fetched, imported and its world shown in 6.5 s, all 40 days
    built; local runs open; no page errors. The test says a run built in parts equals the whole.
  - Fixed on the way: a village river continued on the region map could circle (combe).
