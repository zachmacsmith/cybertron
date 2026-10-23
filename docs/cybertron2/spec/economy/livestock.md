# Livestock

## Summary

Cattle and horses are kinds of one livestock system: animals in herds that breed, are never made, graze, and need fodder. Wild herds
live on grassland. On the farm, oxen pull the plough and their dung keeps the soil. A herd stays put if it is herded or fenced in;
otherwise it wanders across the village's parcels toward what draws it, into crops, and rarely onto a road, where it is soon lost
unless someone finds it. One person can hold only so many head; beyond that a herd splits.

## Decided

- D2-6: one livestock system; animals are bred, not made; wild herds live on grassland.
- D2-18: the plough needs an ox; fodder takes land; dung keeps the soil.
- D2-63: cattle are one kind with three roles: cows (milk, calves), oxen (trained steers that pull), bulls (breeding). D4-41: the
  role changes by training or growing up, the kind never.
- D2-23: an ox works with a harness, a horse carries a rider with a saddle.
- D4-42: winter fodder is hay cut from pasture in summer and straw from the grain harvest.
- D4-44: breeding happens on its own wherever a bull is with the cows and the herd is fed; keeping the bull apart stops it.
- D4-45: cattle graze the pasture they are on and eat stored fodder where there is no grazing; too many wear a pasture down.
- D2-117, D2-123: herds wander on the node, far if drawn.
- D2-124: a herd lost on a road drifts, dies or is gone, comes home or strays to the far node, and is found by noticing.
- D2-125: searching is a travel modifier (agents/modifiers.md).
- D2-127: driving a found herd, or accompanying it.
- D2-128, D2-131: herd size and splitting; the share that breaks off.
- D2-130: fences round a parcel, wood or stone. D2-132: gates open by themselves; opening one and leaving it is an act.

## Mechanics

### Cattle

- **Roles** (D2-63, D4-41): a cow gives milk after calving and bears calves; an ox, a steer trained to the yoke, pulls a plough or
  cart; a bull is needed for a herd to breed, so whoever holds the bull controls breeding (D4-44). Young animals are counted with
  the herd.
- A herd is a count of animals of one kind held by an owner, on a parcel (holding: spec/world/holding.md). It grows only by breeding.
- **Eating** (D4-45, D4-42): a herd grazes the parcel it is on; where there is no grazing (winter) it eats stored hay and straw;
  overgrazing wears the pasture, which recovers slowly.
- An ox with a harness pulls a plough (production.md) or a cart (transport.md); a horse with a saddle carries a rider.
- Dung restores a field's fertility, by manuring or by grazing a fallow plot. Wild herds on grassland can be caught and tamed.

### Staying put

A herd stays where it is if, that day, it is **herded** (someone does herding work with it: about 1 unit, one herder holding about
30 head) or its parcel is **fenced** and the gate shut. Otherwise it wanders.

### Wandering on the node (D2-117, D2-123)

- Each day an unherded herd outside a fence takes steps across the parcel graph (world/parcel_graph.md): a fed herd on good pasture
  0 to 1; a hungry one, or one drawn by a ripe crop or water, up to about 8 (enough to cross a village). Cows in milk drift home at
  dusk.
- Each step goes to the most attractive neighbour (a ripe crop, water when thirsty, better grazing), keyed draws (D2-70). A fenced
  parcel is entered only at the fence's odds (below).
- **In a field** each head eats and tramples about 1% of the standing crop a day, recorded with the herd as the cause and its holder
  known.
- People who work or pass through a parcel the herd is on notice it by the noticing rule (information/noticing.md: a herd's own
  conspicuousness 0.95, also heard); anyone there can `drive` it back or tell its owners. The owners notice their pasture empty
  themselves; nobody is told.
- **Onto a road:** at each step from a parcel where a road leaves (world/roads.md), about 0.1 of taking the road.

### Lost on a road (D2-124)

- The herd is on a stretch (world/roads.md) and drifts one stretch a day in a keyed random direction. Drifting off the end it came
  from brings it home; off the far end, it is a stray at the far node.
- **Losses each day:** each head dies with 0.15 (0.3 in winter); the group as a whole is gone for good (wandered beyond finding)
  with 0.15.
- **Found** by anyone on its stretch, by the noticing rule; a searcher (`travel {to, searching: <herd>}`, D2-125) notices it x5. A
  find is a fuse call (conflict/fuse_events.md): drive it, accompany it, or leave it. Whoever takes it holds it (D4-23); the owner's
  claim is for custom and law.

### Driving (D2-127)

- At a node, `drive` moves a herd to a parcel there (as built). On the road, in the find call: **drive it a stretch** (on, or back)
  and leave it there; or **accompany it** to either end: the drovers travel with it automatically, a stretch a day.
- While driving or accompanying, a further call comes only if a group splits off (below) that is a quarter of the herd or 3 head or
  more, and a drover notices it.

### Size and splitting (D2-128, D2-131)

- **Capacity:** about 10 head for each drover on a road, 30 for each herder on pasture; an unherded herd holds together loosely,
  about 6 head.
- **Each day,** a herd at or under capacity splits almost never (0.01). Over it, it splits with chance 0.1 x (head / capacity - 1),
  at most 0.6. Enough people keep a herd together.
- **The share that breaks off** (D2-131): most often about a quarter, falling off exponentially toward smaller groups and toward
  half. Drawn as share = 1/4 x 2^z, z from a Laplace distribution centred on 0 with a spread (standard deviation) of one doubling,
  redrawn if above half; at least one head. About 3 splits in 100 take a sixteenth or less, 11 a sixteenth to an eighth, 24 an
  eighth to a fifth, 45 a fifth to a third, 18 a third to nearly half.
- The group that breaks off is a herd of its own, the owner's still, wandering its own way.

### Fences and gates (D2-130, D2-132)

- A **fence goes round a parcel**: a parcel is fenced or not. It keeps the herd on it in and strays out, at the same odds. Fences on
  the borders between parcels come later (OPEN L-24).

  | Fence | Build (a parcel of size s) | A herd gets through, a day | Upkeep |
  |---|---|---|---|
  | wood (wattle or post and rail) | 4 timber and 10 units, x the square root of s | 0.3 | loses a level each season unmended; mending is a quarter of the build |
  | stone (a dry wall) | 8 stone and 20 units, x the square root of s, led by a mason | 0.05 | little |

  It is built as a field work on the parcel (production.md, D2-66), part of the parcel thereafter.
- **Gates** open and close by themselves when people or a driven herd pass; nobody acts on them to move.
- **Opening a gate and leaving it open** is an act: `work {what: open the gate, at: <parcel>}`, no units, by anyone; it is seen by
  whoever is present (perception.md), so it can be sabotage. While open, beasts pass as if unfenced, and "the gate of the Long Field
  is standing open" is a sign others can notice (own 0.6). Anyone of the parcel's household who works or passes there and notices it
  shuts it.

## Data

Per herd: owner, parcel (or stretch of road), animals by role, herded today, lost since. Per parcel: fenced (wood or stone), its
condition, gate open. Per pasture: its grazing.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| breeding rate, fodder a head, grazing capacity, herding work | 02g §2, 02l §5, 02o | calibrate |
| steps a day; trampling; onto a road | 0 to 1 fed, up to 8 drawn; 1% a head a day; 0.1 a step | decided (D2-123); calibrate |
| on the road | each head 0.15 a day (winter 0.3); the group gone 0.15 a day; a searcher x5 | proposed (D2-124); calibrate |
| capacity; splitting | 10 a drover, 30 a herder, 6 unherded; 0.01 under, 0.1 x (head / capacity - 1) over, at most 0.6 | proposed (D2-128); calibrate |
| share split off | a quarter x 2^z, z Laplace with a spread of one doubling, at most half | decided (D2-131) |
| fences | above | proposed (D2-130); calibrate |

## What agents see

Their animals by role and count, whether fed, where they are when seen; the pasture in words; a herd where they work or pass ("the
Fenn cows are in the Long Field, trampling the barley"); their fences and gates; wild herds where they are seen.

## Open

- Fences on borders, hedges, night folds, wolves (OPEN L-24, L-2).
- Milk, meat and hides, horses' grain, mounted strength, the common herd: proposals/livestock.md.

## Sources

[02g §2-2c](../../../review/37_growth/02g_resources_and_transport.md), [02l §5](../../../review/37_growth/02l_farming.md),
[02o](../../../review/37_growth/02o_livestock.md); proposals/livestock.md, fences.md.

*Current as of 24 Oct 2026: D2-6, D2-18, D2-23, D2-63, D2-117, D2-123 to D2-125, D2-127, D2-128, D2-130 to D2-132, D4-41, D4-42,
D4-44, D4-45.*
