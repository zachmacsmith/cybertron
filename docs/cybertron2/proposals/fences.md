# Proposal: fences, hedges and walls

**Status:** discussion (23 Oct). **Owner:** 37.4 (author; the mechanism: herds, parcels, incidents); 37.2 for the numbers (field works,
livestock). **Affects:** spec/economy/livestock.md, production.md (field works, D2-66), spec/world/places.md, conflict/ (predators,
rustling), cybertron2/engine (farm.py, signs.py).

## Summary

Today beasts are kept only by watching: a herd someone herds that day stays put; an unwatched one has a chance each night of getting
into a neighbouring field with a crop standing and eating and trampling it (the Thornes lost their rye this way in the hamlet run).
Fences would turn that daily labour into capital: a field work on a parcel (like ditches and terraces, D2-66) that keeps beasts in or
out, wears, needs mending, and can be upgraded from a hedge or wattle fence to a stone wall.

## The proposal

| Work | Materials and labour (a plot's edge; calibrate) | What it does | Upkeep |
|---|---|---|---|
| **hedge or wattle fence** | timber (about 4 a plot) and about 10 units | beasts on a fenced pasture stray about a quarter as often; a fenced field keeps strays out at the same rate | some mending each season, or it decays a level (D2-66's rule) |
| **stone wall** (an upgrade of a fence, or new) | stone (about 8 a plot, fieldstone or quarried) and about 20 units; a mason knows it best | strays almost never; when predators exist, far fewer beasts lost | little upkeep |
| **gate** | part of either | a gate left open after work is the weak point: a sign others can notice ("the gate of the Common is standing open") | |

- **Whose:** a fence belongs to the plot (it passes with the land, D4-23), like D2-66's works; a fence on a boundary between two holders
  is a joint work, and who mends it is a question for custom or an agreement.
- **Built as a project:** work by anyone on the plot's edge, led by someone who knows it for a stone wall (mason), anyone for a hedge.
- **Signs** (D4-48): a fence whole, gapped, broken by beasts; a gate open; a wall going up.

## Why

- It makes keeping beasts a choice between labour (herding every day) and capital (a fence and its upkeep), as historically.
- It gives fieldstone (D2-56) and the quarry another use, and a mason a trade at the farm.
- Common pastures fenced and stinted raise the questions institutions answer: who builds, who mends, how many beasts each may put
  in (livestock.md's commons problem).
- When predators (wolves) come with the scheduler's incidents, walls and folds are the defence; until then fences stop only straying.

## Alternatives considered

1. Herding only (as built): labour every day, no capital; kept for unfenced land.
2. A fence as a building: rejected; it belongs to a parcel's edge, not a lot, and works like D2-66's field works.

## Open questions

1. The numbers (timber, stone, units, stray chances, upkeep): 37.2.
2. Edges: is a fence per parcel (all round it) or per boundary between two parcels (shared)?
3. Predators: wolves as incidents drawn by the scheduler, taking unfenced and unwatched beasts; when?
4. Folds and stalls (D2-45): penning beasts at night near the house, against both straying and predators.

## History

- 23 Oct: Zach asked whether herds need fences or only herding, and suggested timber fences around plots, upgraded to stone, for lower
  chances of escaping cattle or wolves attacking. Written up at his request.

## Sources

D2-45, D2-56, D2-66, D4-23, D4-44, D4-45, D4-48; the hamlet run (runs/w1_hamlet, day 7: cattle in the rye).
