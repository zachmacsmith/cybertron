# Buildings

## Summary

Households start in houses that need upkeep. Buildings are made from parts (a structure, rooms and fittings, each with resource
costs), not from templates. Rooms can be booked. Capacity can be extended, and larger or adjoining rooms cost less per person. Large
buildings and buildings of two or three storeys need stone. Walls multiply the defence of those inside.

## Decided

- H-5: houses with upkeep and rare breaks; a lack of shelter raises the food needed; in the cold an unsheltered agent falls straight
  to starving with chance 0.3.
- D2-3: large buildings and buildings of 2-3 storeys must have stone; building up costs more.
- D2-9: buildings from parts; rooms can be booked (a room is a channel, information/); capacity can be extended, with larger and
  adjoining rooms cheaper per person.
- D2-20: walls multiply the defence of those inside, and a stone building is less likely to be picked in a node raid (conflict/).

## Mechanics

- **A building** stands on a lot (spec/world) and has a structure (its material), one or more rooms, and fittings in its rooms.
  What a building does is what its fittings do.
- **Building** costs materials and work, over several days; the parts' costs are what it costs.
- **Shelter:** sleeping in a house you may use, with the hearth lit in the cold, gives the full ration rule; sleeping without
  shelter raises the food needed, and in the cold carries the 0.3 chance of waking starving (H-5).
- **Upkeep:** a building needs materials every so often or it decays; a decayed one can break.
- **Stone:** a large building, or any second or third storey, needs stone (D2-3), and each storey up costs more.
- **Rooms** can be booked by others on terms the holder sets; who may use a room is its access (information/: speech in rooms).
- **Defence:** the structure sets how much it multiplies the defence of those inside and how hard it is to break into (conflict/).

## Data

Per building: lot, structure, rooms (size), fittings, condition, holder (claims: spec/world/holding.md), access, bookings.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| the shelter ration multipliers | 02e §3 | calibrate |
| the cold's chance of waking starving | 0.3 | decided (H-5) |
| part costs, scaling with capacity, storey costs, upkeep, break chances | 02i, 02e | calibrate |
| defence multipliers by structure | 02k §3 | calibrate |

## What agents see

Their house and its state ("the roof needs mending"); the buildings at their node by what they look like and do ("a stone hall
with a hearth"), who holds them as they know it, and the rooms they may enter.

## Open

- Structures, room sizes, the fittings list, scaling, storeys in detail, limits: proposals/buildings.md.
- Lots against slots (OPEN C-2).

## Sources

[02e_shelter.md](../../../review/37_growth/02e_shelter.md), [02i_buildings.md](../../../review/37_growth/02i_buildings.md),
[02k §3](../../../review/37_growth/02k_fuses_and_gates.md); proposals/buildings.md, proposals/shelter.md.

*Current as of 23 Oct 2026: H-5, D2-3, D2-9, D2-20.*
