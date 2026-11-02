# 02zj: the landscape generator, stage 1, as built

Session 37.2, 3 Nov 2026. **Built at Zach's request:** "Could you build this yourself and then merge into its work?", then "Yes. Just
let the other agent know". This waives README rule 6 for this package only, and 37.4 was told.

- **Spec:** docs/cybertron2/proposals/generator_stage1.md (D2-173 to D2-188).
- **Code:** cybertron2/landgen/.
- **Tests:** tests/test_cybertron2_landgen.py (11).
- **Example:** cybertron2/specs/twin_bays_gen.yaml, pictured in 02zj_twin_bays.png.

```
python -m cybertron2.landgen cybertron2/specs/twin_bays_gen.yaml --out <world.yaml> --people --picture <png>
```

## What it does

1. **Input:** a world file with a `generate:` block (seed, size, settlements, configuration, features, places with pins, require,
   and any default). Everything else in the file is kept as the settings the world sits in.
2. **Large shapes** (macro.py): primitives composed in order, bent by noise, with anchors for pins. All of D2-188's fifteen named
   configurations are data; the five that wait on later systems are refused with the reason.
3. **Physical layers** (physical.py):
   - **elevation:** noise plus the shapes, and a gentle tilt so rivers run somewhere;
   - **temperature and moisture:** one wind sweep, giving rain on windward slopes and a shadow beyond;
   - **water:**
     - Priority-Flood filling, then flow and accumulation;
     - one pass of valley cutting, then flow again;
     - lakes in hollows deeper than 4 m, rivers in three classes, springs at stream heads, wetness;
     - height above the river, and distance to the sea;
   - **soil:** texture by belt or by rule, depth, and fertility (silt on floodplains);
   - **terrain:** the catalogue's scores, with natural cover from terrain.
4. **Settlement** (settle.py):
   - **sites:** scored on water, flatness, fertile land, crossings, fuel, flood safety and lying between terrains. Pinned places go
     first, placed where their pins allow or refused with the reason; the rest at least 17 km apart.
   - **land:** grown outward as contiguous pieces and sized to each village's capacity target, against the world's year length and
     the woods' yearly flows (capacity.py, forests.py).
   - **parcels:** connected pieces of one use; large arable split into great fields; 6 to 15 per node; a connected parcel graph with
     sides, heights, terrain and soil.
5. **Roads** (roads.py):
   - least-cost routes on the cells, by pace by cover and slope, with fords on large rivers;
   - a tree of the shortest roads, plus direct roads where much shorter;
   - a stopping place on any road over a day and a half;
   - a wild node for each large wild area half a day out (deep forest; hills, with a copper seam), unexplored;
   - stretches with landmarks (ford, pass, narrows, spring, meadow), and hidden ways through cover.
6. **Writing** (write.py, names.py):
   - names from parts by the land, with plain parcel names;
   - resources per unit of size from the hand-made worlds;
   - houses, a byre, and the first household's oxen;
   - fields and meadows held by households in turn, the first field in crop;
   - trades by resources (smith by a seam, mason by stone, carpenter by managed wood, miller at a mill site);
   - people from generate.py, unchanged, with each house then given a bed for each member plus one and stores for about a week;
   - the checks;
   - the world file, the cells (.npz) and the report (.json).

## The example (twin bays, seed 7)

| Check | Kind | Passed | Detail |
|---|---|---|---|
| rivers run downhill | physics | yes | 0 river cells drain uphill |
| every pin met | physics | yes | Northby and Southby at the heads of the bays |
| capacity | design | yes | 0.60 to 0.64 of the scarcest flow, for all four villages |
| dependence | design | yes | every village lacks stone and metal; the hill node has a seam |
| reachable by land | design | yes | |
| chokepoint | design | yes | the pass over the spur between the two bays |
| roads about a day | design | yes | 5 roads, all of one day |
| parcels per node | design | yes | 9 each |

**Generation time:** about 7 seconds with people.

**A bot run** of 6 days on it ran without errors. Bots wander to other villages and starve away from home, as in 38.27's dry run;
that is the bots, not the world.

The full cybertron2 suite passes: 262, 3 skipped.

## Not built yet, or built differently from the spec

| Spec | As built |
|---|---|
| Poisson-disc points with Delaunay neighbours; cells as parquet | a jittered square grid; .npz (scipy and pyarrow are not installed) |
| descriptions written by a model (D2-179) | the hook is built (`--describe`, cached by the facts' hash) but has never been run against a model; without it, templates |
| a window chosen by scanning the macro world (D2-178) | only configurations placed in the window |
| fine detail only where needed, for large worlds (D2-178) | the whole window at full detail (a 50 km window is about 110,000 cells, under 2 s) |
| the full vocabulary (stage 1 §11c) | `at`, `terrain`, `on` (river, sea, lake), `has` (ford, mill site), `short_of` and `plenty_of` (wood, food), `land` (pressed, rich), `households`. Not yet: `soil`, `wet` and `dry`, `sheltered` and `exposed`, `remote`, `at a crossroads`, `n days out`, and words that place a template |
| hidden ways known to the few who would use them (D2-187) | not seeded: hidden ways known to none at the start |
| ore belts in the hills by a geology mask | a seam only at the hill wild node |
| the supply-chain and junction checks (stage 1 §11i) | not built; dependence is only "lacks stone or metal" |
| capacity against the people as generated | against the planned people (households x 5) |
| kin between villages | none: generate.py's tree per village, unchanged (37.4's, later) |

**What also needs tuning:** the terrain scores' thresholds. A plain lowland world is mostly lowland loam with some heath; that is
plausible, but worth a look on more seeds and configurations.

## Second pass (2 Nov), at Zach's request ("Do 1, 4, 5, 6. Then 2 and 7")

1. **Descriptions written by a model** (D2-179). `--describe [MODEL]` takes the model on the command line, otherwise the world's
   `describe.model` or its cast's middle model.
   - **The model is given words, not numbers,** and is told never to mention what is absent.
   - **On the example:** 43 descriptions written, none failed, about 3.5 minutes; cached by the hash of the facts, and frozen.
2. **Ore belts.** Veins along ridged noise in hill country, and an `ore` primitive for a pinned belt.
   - The hill wild node is entered where its ore is, and has a seam only if there is ore.
   - A place may pin `resources: [copper]` or `[stone]`. It is then sited within 4 km of ore or stone, and gets a rock parcel
     (with a seam for copper) and a smith.
3. **Hidden ways known to a few** (D2-187). Each hidden way is known at the start to one or two grown people of the village at its
   end, hunters first.
   - This needed a small hook in the engine: perceive.seed_knowledge reads an agent's `ways: [{road, end}]`.
4. **Capacity for the people as generated** (D2-161). With `--people` the generator runs twice:
   - the land is sized first for households of the default size;
   - then again for the people generate.py actually made (its tree depends on the lines and the seed, not the land, so the people
     are the same).

   On the example the villages now sit at 0.58 to 0.62 of their scarcest flow (they were 0.37 to 0.48).
5. **The vocabulary**, adding:
   - `soil: rich | poor` (site and fields' fertility);
   - `wet` and `dry`;
   - `sheltered` and `exposed`;
   - `remote` (the others kept two days off);
   - `at a crossroads` (the most central site);
   - `days_out: {from, days}`;
   - words that place a shape: `on: sea` with no sea places a coast, `terrain: hills` with no relief places hills, `is: [on an
     island]` makes the land an island.
6. **Terrain tuning.**
   - **Soil:** regions from a broader geology mask (clay in low moist land, sand, natural chalk on higher ground), and more relief.
   - **A plain world over three seeds** is now about 61% lowland loam, 15% clay vale, 6% chalk down, 6% river terrace, 5% water,
     5% heath and 2% floodplain (it was 79% loam).
   - **Capacity** in a provisional first pass refuses only on physics; tiny villages (a household alone) may sit below the target,
     because their least land rounds up.

Tests: 13 in test_cybertron2_landgen.py. The whole cybertron2 suite passes: 279, 3 skipped.
