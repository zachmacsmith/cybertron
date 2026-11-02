# A walk-through video of a run

`w1_walkthrough.py` (made for w1_wide, review 38.31; its title and closing cards are that run's) renders a run's viz.json at 1920x1080,
12 frames a second, with a chapter a day: the region after each day's night (place names, the night record's travel, building,
births, deaths, agreements and missed meals), then the three busiest places close up through the day (`C2Pixel.nodeAt`: talk,
the acts in the journal's order, dusk, night), with who lives there and their household's model, and what one of them said there
that day (from turns.jsonl). Places at 3x, the region at 1x, both whole pixels.

```
python -m c2viz.build --js VIDEO_DIR/c2pixel.js
cp c2viz/video/page.html VIDEO_DIR/; (printf 'var V = '; cat RUN/viz.json; printf ';') > VIDEO_DIR/viz.js; cp RUN/viz.json VIDEO_DIR/
python c2viz/video/w1_walkthrough.py VIDEO_DIR HF_RUN_DIR OUT.mp4 [--days N] [--stills]
```
