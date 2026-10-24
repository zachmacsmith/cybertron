# c2viz: the cybertron2 world as a pixel map across time

The core visuals for a central map of a cybertron2 world: no site, only the drawing, in the look of the site's night-village
design (`wp/site-v2`, `site/assets/scene.js`). Two scales, both drawn from the run's data for one day:

Both are drawn from one **ground plan** per place (`C2Pixel.geom`), read from what the world has and nothing else. Parcels have no
coordinates, so the plan is built from what they do have:
- **size**: every unit of size is the same ground (2,600 close-up pixels), so a field of 5 is five times a copse of 1;
- **neighbours** (`adj`): neighbours are pulled together until they share a border; parcels that are not neighbours are pushed
  apart, and where they would still touch, a strip of wild ground is left between them, so the graph can be read off the map;
- **side** pulls a parcel that way; a chain of river parcels is one long band with one river through it, running on to the
  map's edges and stopped by built ground, fields and rock;
- **lots**: a parcel holds buildings in lots (data.py `COVERS`: built ground 6 a unit of size), spread through it from the
  middle; each building keeps its lot from the day it first stands. A building does not take a parcel: a village's houses
  share its built ground.

- **A place, close up** (`C2Pixel.node`): a canvas sized to the place, shown large and panned. Fields are squared off along
  their strips; meadow, pasture, scrub and woods have a bank against the wild, which is rougher and darker. On top:
  - crops by growth (bare soil, sprouting, green, ripe gold, stubble where reaped, grey if failed), hedges, fences and walls (gappy
    or down by their level);
  - woods thinning to stumps where they were felled, pasture grazed bare, boulders, copper-stained seams, scrub in clumps;
  - buildings by structure (timber, stone, wattle, a camp), condition (damaged, ruined), smoke when the fire is lit, fittings (a
    water wheel, a smithy's chimney, an oven, a granary), the frame of one being built; a yard, a kitchen garden by each house,
    lanes to the roads;
  - herds head by head, by kind (cattle, sheep, goats, pigs); bodies lying, graves, carcasses, goods left lying;
  - people (5 x 9) where they worked that day, holding what they worked with (an axe, a sickle, a basket, a pick, a pail, a spade,
    a hammer, a crook), with a speech bubble, hunger over the head (amber one meal missed, red two or more), a wound, lying dead;
    those who did not go out stand at their door;
  - roads leaving the edge towards the next place.
- **The region** (`C2Pixel.world`): every place's plan at one scale for all places, in its own territory of wild country by its
  character; its buildings as small houses, its people as small figures (3 x 6), its herds; roads winding between places (a track
  narrower than a road); stone markers for landmarks; travellers on the roads at how far they have come. Unexplored places are
  drawn as they are: the world exists before anyone has found it.

Each returns hotspots (kind, id, box, label) so a page can label, hover and click.

```
python -m c2viz.capture cybertron2/specs/region_s1.yaml --out RUN --days 12    # a scripted run, the state saved each day
python -m c2viz.build RUN                                                      # RUN/viz.json and RUN/map.html (open it)
```

`map.html` is a bare preview: the map, place and exit labels, hover, day controls; click a place to go in, an exit to follow the
road; in a place, drag to pan and +/- to zoom. Query: `?day=N&node=<id>&z=<zoom>` (`&full` fits a place to the page).

| File | What |
|---|---|
| `capture.py` | runs a world (scripted bots by default) and saves the whole state at each day's end; a stand-in for the run journal (spec/record/) |
| `layout.py` | positions: places by travel days on the road graph; parcels by side, height, neighbours and size |
| `frames.py` | `viz.json`: the static world, the layout and one compact record a day |
| `pixel.js` | the renderer (`C2Pixel.geom`, `C2Pixel.plan`, `C2Pixel.world`, `C2Pixel.node`) |
| `preview.html`, `build.py` | the preview page with the renderer and the data inlined |
