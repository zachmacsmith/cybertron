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
| 4 | the pixel renderer (`pixel.js`): the region and a place, in the site-v2 look; a bare preview page | first version |
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
