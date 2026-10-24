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
| 4 | the viewer: one self-contained HTML; world map, node view, road view, detail panel, timeline; Broadsheet and Night themes | next |
| 5 | acts and events drawn (verbs as marks, travel along roads, night events), changes highlighted, history sparklines | |
| 6 | screenshots with Playwright on a bot run; README; a board post | |

## Log

- 17:13 UTC: steps 1-3. region_s1 with bots, 12 days: the capture is 1.3 MB gzipped; viz.json is 695 KB. Roads of one
  day come out about 200 px apart in the world layout.
