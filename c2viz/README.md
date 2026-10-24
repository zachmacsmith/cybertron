# c2viz: the cybertron2 world as a pixel map across time

The core visuals for a central map of a cybertron2 world: no site, only the drawing, in the look of the site's night-village
design (`wp/site-v2`, `site/assets/scene.js`). Two scales, both drawn from the run's data for one day:

- **The region** (`C2Pixel.world`): each place set in country made from its own parcels (woods, fields, water, rock, scrub,
  pasture), with a village of the buildings standing that day; roads winding between places (a track narrower than a road); stone
  markers for landmarks; travellers on the roads at how far they have come; fog over unexplored places.
- **A place** (`C2Pixel.node`): its parcels as land, with terraces and cliff faces by height and shores on water. On top:
  - crops by growth (bare soil, sprouting, green, ripe gold, stubble where reaped, grey if failed), hedges, fences and walls (gappy
    or down by their level);
  - woods thinning to stumps as they are felled, pasture grazed bare, boulders, copper-stained seams;
  - buildings by structure (timber, stone, wattle, a camp), condition (damaged, ruined), smoke when the fire is lit, fittings (a
    water wheel, a smithy's chimney, an oven, a granary), the frame of one being built, packed earth and lanes to the roads;
  - herds as cattle, bodies and graves, carcasses, goods left;
  - people where they worked that day, holding what they worked with (an axe, a sickle, a basket, a pick, a pail, a spade, a
    hammer, a crook) or speaking;
  - roads leaving the edge towards the next place.

Each returns hotspots (kind, id, box, label) so a page can label, hover and click.

```
python -m c2viz.capture cybertron2/specs/region_s1.yaml --out RUN --days 12    # a scripted run, the state saved each day
python -m c2viz.build RUN                                                      # RUN/viz.json and RUN/map.html (open it)
```

`map.html` is a bare preview: the map, place and exit labels, hover, day controls; click a place to go in, an exit to follow the
road. Query: `?day=N&node=<id>`.

| File | What |
|---|---|
| `capture.py` | runs a world (scripted bots by default) and saves the whole state at each day's end; a stand-in for the run journal (spec/record/) |
| `layout.py` | positions: places by travel days on the road graph; parcels by side, height, neighbours and size |
| `frames.py` | `viz.json`: the static world, the layout and one compact record a day |
| `pixel.js` | the renderer (`C2Pixel.world`, `C2Pixel.node`) |
| `preview.html`, `build.py` | the preview page with the renderer and the data inlined |
