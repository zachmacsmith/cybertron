# Mills and ovens at scale: a few units that do a great deal

**Status:** discussion (the direction is Zach's, 2 Nov; the numbers wait for him)
**Owner:** 37.4 (the recipes as built); 37.2 owns production.md and goods.md, where the rule goes once decided

## Summary

The food bonus stays: grain 0.7, meal and flour 1.0, bread 1.3 (Zach: "keep the food bonus"). A big mill or an oven does far more
for each unit of work than a hand or a hearth. The oven costs more to build, as the water wheel already does (D2-166).

## The proposal (numbers to calibrate)

| Recipe | Now | Proposed |
|---|---|---|
| Hand mill: grain to meal | 3 a unit | 3 a unit (labour-bound, as a quern is) |
| Ox mill: grain to flour at millstones | 16 in 1 unit | 64 in 2 units (32 a unit) |
| Water mill: grain to flour | 40 in 1 unit | 200 in 2 units (100 a unit): a harvest ground in a few units |
| Hearth bread: flour to bread | 10 in 1 unit, 1 timber | 10 in 1 unit, 1 timber (0.1 timber a loaf) |
| Oven bread: flour to bread | 40 in 2 units, 2 timber | 100 in 3 units, 4 timber (one firing; 0.04 timber a loaf) |
| Building an oven (mason) | 6 stone, 4 units | 20 stone, 2 timber, 12 units |

**Payback,** materials counted as the work to get them (about 1.5 timber or 1 stone a unit):

| Fitting | Cost | Saving | Pays back after |
|---|---|---|---|
| Oven | about 34 units | against the hearth: about 7 units and 6 timber per 100 loaves | about 300 loaves (three firings) |
| Water wheel | about 310 units (unchanged) | against the ox mill: 68 more flour a unit of work, with no ox | a village's harvest or two |

## Why

Zach (2 Nov): "it would make more sense where there are a few units that do a much larger amount for both mill and oven. I imagine
ovens should probably cost quite a bit more though? Because I increased the cost of mill but not oven".

The engine's ladder had the right order and too short a top. A real watermill ground for a village, a hand quern for a household;
a communal oven baked dozens of loaves a firing, on far less fuel a loaf than hearth baking.

## Alternatives considered

- **Same food value for grain, meal and flour, with fuel and time as the gain** (more historical): declined. The food bonus stays.
- **More fittings, more output** (two ovens bake twice a firing): left for towns.

## Open questions

1. Whether the oven needs a building of its own (a bakehouse), or stands in any house with the floor.
2. Whether the mill should take a toll for its holder (multure), or leave that to agreements.

## History

- 2 Nov 2026: written after Zach's answer on the economics of milling and baking (38.49 era).

## Sources

data.py TECHNIQUES (grind, mill, water mill, bread, oven bread), FITTINGS (oven, water wheel); D2-60, D2-61, D2-160, D2-166, D2-167.
