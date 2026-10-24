# Buildings

## Summary

Households start in houses that need upkeep. Buildings are made from parts: a structure, rooms and fittings, each with its costs.
One unit of space runs from the land to the fitting: a parcel has ground for buildings, a building's ground-floor rooms take that
ground, a room has floor, and every fitting and every store takes floor. People housed are the beds. Larger and adjoining rooms cost
less per space; upper storeys and large buildings need stone. A village that runs out of ground builds up in stone, builds on scrub,
or clears land. Walls multiply the defence of those inside.

## Decided

- H-5: houses with upkeep and rare breaks; a lack of shelter raises the food needed; in the cold an unsheltered agent falls straight
  to starving with chance 0.3.
- D2-3: large buildings and buildings of 2-3 storeys must have stone; building up costs more.
- D2-9: buildings from parts; rooms can be booked (a room is a channel, information/); capacity can be extended, with larger and
  adjoining rooms cheaper per person.
- D2-45: a cellar (stone; food keeps at a quarter of the house rate) and stalls (animals housed in winter: less fodder, dung
  kept, safe from rustling) are fittings.
- D2-49: stone resists fire (walls stand; roof and contents can burn); a vault (stone-arched, ground floor, dear) does not burn.
- D2-56: beds are made of timber and straw.
- D2-60: an oven (stone) is a fitting: bread in batches. D2-61: millstones (hand, dressed), the ox gear and a water wheel are
  fittings; a water wheel only at a river site.
- D2-20: walls multiply the defence of those inside, and a stone building is less likely to be picked in a node raid (conflict/).
- D2-154: one unit of space at every level (parcel ground, room floor, fitting); people housed are the beds; rooms of 6, 12 and 30
  spaces; adjoining rooms a quarter cheaper; upper storeys at 1.5 times the cost, with stone.
- D2-155: storage takes space; a cellar is cheaper (4 stone, 6 units) and holds by the building's footprint.

## Mechanics

### Space (D2-154)

A **space** is about the floor a bed takes (about 5 m²). Everything is counted in spaces:

| Level | Has | Takes |
|---|---|---|
| a parcel | ground for buildings: **built ground 24 spaces a unit of size, scrub 16**; fields, pasture, meadow, woods, rock and water none unless cleared (below) | |
| a building | a structure, rooms, and its footprint (its ground-floor rooms) | its footprint from its parcel's ground |
| a room | its floor | |
| a fitting, a store | | its spaces of floor |

People housed are **the beds** in the building (one a bed), not a property of the room.

### Rooms and structures

| Room | Floor | Wattle | Timber (on a stone footing) | Stone | Work |
|---|---|---|---|---|---|
| small room | 6 | 8 timber | 8 timber, 2 stone | 12 stone, 3 timber | 6 units (stone: 10, a mason) |
| medium room | 12 | (too large for wattle) | 15 timber, 4 stone | 24 stone, 5 timber | 15 units (stone: 22, a mason) |
| hall | 30 | (too large for wattle) | 30 timber, 10 stone (its stone footing meets D2-3) | 50 stone, 10 timber | 30 units, a carpenter (stone: 40, a mason) |
| camp | 4, lasts 10 nights | 3 timber | | | 1 unit (D2-68) |

- **A building's structure** is one material for all its rooms. Wattle: anyone; timber: a carpenter for a medium room; stone: a
  mason.
- **Adjoining rooms:** a room added to an existing building costs **a quarter less** in materials and work (it shares a wall).
- **Storeys** (D2-3): a second storey adds floor up to the ground floor's, at **1.5 times** the cost a space; a third at 2 times;
  only in a stone building. Upper floors take no ground.
- **Upgrading** a building's structure (wattle to timber, timber to stone): the new structure's materials for its rooms, less a
  quarter, and the work; the building keeps its rooms, fittings and stores; it counts as damaged while the work is under way.
- **Defence and fire** by structure: conflict/defence.md (wattle x0.5, timber x1, stone x2, proposed) and D2-49.

### Fittings (D2-154), their space and cost

Each fitting takes floor in a room of the building, and its work is charged over days like a building's (each `build` action
does 2 units, more with skill, until its work is done).

| Fitting | Spaces | Materials | Work | Who | Does |
|---|---|---|---|---|---|
| bed | 1 each | 1 timber, 2 straw (proposed; was 2 and 2) | 1 | anyone | sleeps one, housed |
| bins | 1 | 3 timber | 1 | anyone | 60 food stored, spoiling at half the house rate |
| hand mill | 1 | 2 stone | 2 | anyone | grinds 8 grain a unit |
| fire ring | 1 | 1 stone | 1 | anyone | a fire for cooking; indoors it half-warms a house on a cold night (proposed) |
| hearth | 1 | 4 stone | 3 | mason | a fire that warms the house, cooks, bakes |
| oven | 2 | 6 stone | 4 | mason | bread in batches of 40 |
| anvil and bellows | 2 | 6 stone, 2 hides, 1 timber | 4 | smith; needs a hearth | a smithy |
| granary floor | 3 | 6 timber | 4 | anyone | 300 grain stored at a fifth of the house rate |
| dressed millstones | 3 | 10 stone | 10 | mason | an ox mill, 16 grain a unit with an ox |
| water wheel | 0 inside (on the water) | 15 timber, 1 copper | 12 | carpenter; needs millstones, a river site | a water mill, 40 grain a unit |
| cellar | 0 (underground; one a building) | 4 stone, 6 units (D2-155) | 6 | mason | 40 food for each space of footprint, at a quarter of the house rate |
| stalls | 2 a beast | 1 timber a stall | 1 a stall | anyone | beasts housed: winter fodder x0.8, dung kept x1.5, cannot be driven off without entering (proposed) |
| woodshed (a lean-to against the building) | 0 inside; 2 spaces of ground | 2 timber | 1 | anyone | 40 timber kept dry |
| vault (a stone room, ground floor) | 4 of floor, its own room | 16 stone | 12 | mason | 30 weight a space stored; does not burn (D2-49) |

### Storage (D2-155)

| Where | Holds | Spoils |
|---|---|---|
| free floor in a room | 30 weight a space, any goods | the house rate |
| bins | 60 food a space | x0.5 |
| a granary floor | 300 grain in 3 spaces | x0.2 |
| a cellar | 40 food a space of footprint | x0.25 |
| a woodshed | 40 timber | kept dry |
| a vault | 30 weight a space | the house rate; does not burn |
| outside | anything | the open (economy/goods.md: food much faster; timber wet in rain, no use as fuel until dried) |

A building's stores cannot take more than its storage holds; what does not fit is refused, or left outside if put there.
**Check (02x):** a farm household of 4 at the harvest holds about 200 grain, beans, 16 timber and some tools; a cottage (6 spaces:
4 beds, a hearth, bins) holds only 60 food, so a farm family needs a family house (12 spaces) or a cottage and a store room or a
share of a granary. A cellar pays back in about 3 days on fresh meat and 9 on milk, but 27 on grain: grain keeps well when dry.

### Ground for building: clearing (proposed)

- **Scrub** takes buildings as it is (16 a unit of size).
- **A field, pasture or meadow** becomes built ground (24) with 4 units of work a unit of size; it stops being farmland.
- **A wood** becomes scrub once its standing wood is felled (the timber is the felling's), then built ground as above: grubbing out
  roots is 10 units a unit of size.
- Clearing is a claim of its own (grounds `cleared`: world/holding.md) and changes the parcel's cover (world/parcel_graph.md).

### What agents see when building

The build verb lists every blueprint and fitting the agent knows, with its full needs whether or not it has them now ("a small
room: 8 timber (you have 2), 6 units of work; a house needs a room, beds and a hearth or fire ring"), and each building's floor:
used and free ("Reed House: 12 spaces, 9 used: 6 beds, a hearth, bins, a hand mill; 3 free").

### Shelter and upkeep

- **Shelter:** sleeping in a house you may use, with its fire lit in the cold, gives the full ration rule; sleeping without shelter
  raises the food needed, and in the cold carries the 0.3 chance of waking starving (H-5).
- **Upkeep:** a building breaks with a small chance a night (more in the cold) and is mended with 2 timber and 2 units; neglected,
  it falls in.
- **Rooms** can be booked by others on terms the holder sets; who may use a room is its access (information/: speech in rooms).

### Seeded worlds

Seeded buildings are given floor enough for what the world file puts in them (beds, fittings, stores), with free space as the file
says; a seeded village's ground may be full, so growth means building up, on scrub, or clearing.

## Data

Per parcel: its ground (by cover and size) and what of it is used. Per building: parcel, structure, rooms (each with floor, storey),
footprint, fittings (each with its room and spaces), stores by kind, condition, holder, access, bookings; work left on anything
unfinished.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| ground a unit of size | built 24, scrub 16 | decided (D2-154); calibrate |
| room floors; adjoining discount; storeys | 6, 12, 30; a quarter; 1.5x and 2x | decided (D2-154); calibrate |
| fitting spaces | above | decided (D2-154); calibrate |
| storage | above | decided (D2-155); calibrate |
| stone structures' costs; bed's cost; an indoor fire ring half-warming; stalls; woodshed; vault; clearing; upgrading | above | proposed |
| the shelter ration multipliers | 1.0, 1.2, 1.5; cold 1.0, 1.3, 1.5, 2.0 | calibrate |
| defence multipliers by structure | wattle x0.5, timber x1, stone x2 | proposed; calibrate |

## What agents see

Their house and its state ("the roof needs mending"); its floor, used and free; the buildings at their node by what they look like
and do ("a stone hall with a hearth"), who holds them as they know it, and the rooms they may enter.

## Open

- Room bookings in detail; lots against slots (OPEN C-2, now ground in spaces).

## Sources

[02x_housing_model.py](../../../review/37_growth/02x_housing_model.py), [02e_shelter.md](../../../review/37_growth/02e_shelter.md),
[02i_buildings.md](../../../review/37_growth/02i_buildings.md), [02k §3](../../../review/37_growth/02k_fuses_and_gates.md);
proposals/buildings.md, proposals/shelter.md.

*Current as of 24 Oct 2026: H-5, D2-3, D2-9, D2-20, D2-45, D2-49, D2-56, D2-60, D2-61, D2-154, D2-155.*
