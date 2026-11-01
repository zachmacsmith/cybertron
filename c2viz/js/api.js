// c2viz/js/api.js: what a page may call (c2viz/README.md). Everything else is the renderer's own.
//   C2Pixel.world(canvas, viz, day)            the region's map for a day; returns { width, height, hotspots, focus }
//   C2Pixel.node(canvas, viz, place, day)      one place close up at the end of a day
//   C2Pixel.nodeAt(canvas, viz, place, day, t) one place close up at time t of its day (-0.1 talk, 0 to 1 the work, past 1 night)
// The canvas is drawn at low resolution: show it scaled up with `image-rendering: pixelated`. The same data gives the same picture.
(function (X, G) {
  "use strict";
  G.C2Pixel = { world: X.world, node: X.node, nodeAt: X.nodeAt, plan: X.plan, geom: X.geom, biomeOf: X.biomeOf, looks: X.looks, hstr: X.hstr,
    rng: X.rng, noise: X.noise, PAL: X.PAL, BIOMES: X.BIOMES };
})(C2X, typeof window !== "undefined" ? window : globalThis);
