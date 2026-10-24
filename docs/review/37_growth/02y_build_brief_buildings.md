# 02y: build brief for 37.4: buildings with space (Package E)

**Deferred (24 Oct, Zach): not to be built until Zach says so; its integration with the other systems to be worked out first.**

Session 37.2, 24 Oct 2026. For after Package D (children), whose new households will need houses. 37.2 does not build. Spec:
**spec/economy/buildings.md** (37.2's, rewritten); decisions D2-154, D2-155; analysis 02x_housing_model.py. Numbers marked proposed
in the spec are for Zach to confirm; build them as data so they change in one place.

## Why

Nobody has built a building in any run. The engine supports small rooms, medium rooms, halls, camps and eleven fittings, but: no
building can be extended or upgraded, there is no stone blueprint (Coppergate's stone is seeded), fittings take no space, stores are
unlimited, land cannot be cleared, and the prompt shows a craft only when one holds its materials, so building never appears as an
option (nobody carries 8 timber). With births (Package D) households will grow and split, and need houses.

## 1. Order

1. **The fitting-work bug (fix first):** a fitting goes in with one 2-unit action whatever its listed work (`_build` in verbs.py
   never reads `FITTINGS[x]["units"]`), so a cellar (8), millstones (10) and a water wheel (12) cost the same labour as a bin. Charge
   it over days like a building's work.
2. **Space:** ground per parcel (built 24, scrub 16 a unit of size); floor per room (6, 12, 30); spaces per fitting (spec table);
   beds as the people housed; a building's footprint taken from its parcel's ground. Seeded buildings get floor enough for what the
   world file puts in them.
3. **Rooms and structures:** adding a room to a building (a quarter cheaper); storeys in stone (1.5x, then 2x); stone structures
   for each room; upgrading a structure, keeping the building.
4. **Storage:** capacity by kind (free floor 30 weight a space, bins 60 food a space, granary floor 300 grain, cellar 40 food a space
   of footprint, woodshed 40 timber, vault 30 weight a space); what does not fit refused or left outside.
5. **New fittings:** stalls, a woodshed, the vault (a stone room); the cellar at 4 stone and 6 units; beds at 1 timber and 2 straw;
   an indoor fire ring half-warming on a cold night (a hearth to warm a house fully).
6. **Clearing ground:** a field, pasture or meadow to built ground (4 units a unit of size); a wood to scrub by felling it out, then
   to built ground (10 units a unit of size); the claim and the parcel's new cover.
7. **The prompt:** every known blueprint and fitting with its full needs and what one has; each building's floor used and free; a
   line saying what makes a house.

## 2. Tests

| Test |
|---|
| a cellar takes 6 units of work over 3 actions, not one |
| a small room (6 spaces) takes 4 beds, a hearth and bins and refuses a hand mill until a bed goes or a room is added |
| an added room costs a quarter less than the same room alone; a second storey is refused unless the building is stone |
| a farm household's 200 grain does not fit a cottage's bins; it fits a family house with a granary floor |
| the Green (built ground, size 2) refuses a ninth cottage (48 spaces of ground) |
| clearing a pasture of size 1 (4 units) turns it into 24 spaces of built ground |
| upgrading a wattle house to timber keeps its beds, fittings and stores |
| an agent with no timber sees "a small room: 8 timber (you have 0), 6 units" among its crafts |
| a woodshed's timber stays dry through a wet day; timber left outside does not burn until dried |

## 3. Running it

With Package D on, in a seeded village with its ground nearly full and a few couples: read whether households build, extend, store,
or clear land as families grow; what a new household does for a house (occupy, join, build: D4-36).
