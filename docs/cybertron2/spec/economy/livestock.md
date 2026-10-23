# Livestock

## Summary

Cattle and horses are kinds of one livestock system: animals in herds that breed, are never made, graze, and need fodder. Wild herds
live on grassland. On the farm, oxen pull the plough and their dung keeps the soil.

## Decided

- D2-6: one livestock system; animals are bred, not made; wild herds live on grassland.
- D2-18: the plough needs an ox; fodder takes land; dung keeps the soil.
- D2-63: cattle are one kind with three roles: cows (milk, calves), oxen (trained steers that pull), bulls (breeding).
- D2-23: an ox works with a harness, a horse carries a rider with a saddle.

## Mechanics

- **Cattle roles** (D2-63): a cow gives milk after calving and bears calves; an ox, a steer trained to the yoke, pulls a plough
  or cart; a bull is needed for a herd to breed, so whoever holds the bull controls breeding. All three share the rules for
  feeding, herding and slaughter. Young animals are counted with the herd; none grows up within a run.
- A herd is a count of animals of one kind held by an owner at a node (holding: spec/world/holding.md). It grows only by breeding.
- Animals eat: they graze where there is grazing, and need stored fodder where there is none (winter).
- An ox with a harness can pull a plough (production.md) or a cart (transport.md). A horse with a saddle carries a rider.
- Dung from cattle restores a field's fertility, by manuring or by grazing a fallow plot.
- Wild herds on grassland can be caught and tamed, adding to a herd.

## Data

Per owner and node: animals by kind (and, for breeding, enough to say how many can breed). Per pasture: its grazing.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| breeding rate, fodder a head, grazing capacity, herding work | 02g §2, 02l §5 as the starting point | calibrate |

## What agents see

Their animals by kind and count, whether they are fed, the pasture in words, wild herds where they are seen.

## Open

- Mechanics beyond the above (milk, meat and hides, horses' grain, mounted strength, herding scale, the common herd):
  proposals/livestock.md.
- How pasture is represented (plots of another cover or a site with a capacity): board, 23 Oct (37.4).

## Sources

[02g §2-2c](../../../review/37_growth/02g_resources_and_transport.md), [02l §5](../../../review/37_growth/02l_farming.md);
proposals/livestock.md.

*Current as of 23 Oct 2026: D2-6, D2-18, D2-23, D2-63.*
