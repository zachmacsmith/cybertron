# 02zh: build brief for 37.4: the building package

Session 37.2, 3 Nov 2026. **Zach asked for this to be built** (3 Nov: "wrap together all the main building modules as a spec to
build and get the other agent to build this for real now"). It replaces 02y (Package E). The spec is
**spec/economy/buildings.md** (37.2's; current as of 3 Nov), with proposals/building_lines.md for §10.

Every number here is data, marked calibrate in the spec, so it changes in one place. Build nothing beyond this brief (README
rule 10); "Not in this package" lists what waits.

## Why

- **Nobody builds.** Building has been rare in every run.
- **Discoverability:** building options showed only when an agent held the materials (since fixed in the belief view).
- **No limits:** ground and storage were unlimited.
- **Big capital is too cheap:** one household could put up a hall or a water mill from under half a year's surplus (02zf).
- **The hand mill:** it made the mill pointless.
- **No meaning:** buildings carried nothing of the people who built them.

## 1. Space (D2-154)

**Ground:**
- Each parcel's ground for buildings is counted in spaces: built ground 24 a unit of size, scrub 16. This replaces today's lots (6
  and 4).
- A building's footprint is its ground-floor rooms' floor, taken from its parcel's ground.
- D2-164's parcel lines switch from lots to spaces ("room for 18 more spaces").

**Rooms and fittings:**
- Each room has floor: small 6, medium 12, hall 30.
- Every fitting and store takes floor (the spec's fitting table).
- People housed are the beds.

**Seeded buildings** get floor enough for what their world file puts in them, plus any free space the file gives.

## 2. Rooms and structures

- **Rooms as records:** a building holds rooms, each with its floor and storey. Access stays per building (D4-30). Rooms as places
  of their own are later (OPEN L-33).
- **Adding a room** to a building costs a quarter less in materials and work.
- **Storeys:** in stone only (D2-3). The second storey costs 1.5 times the cost a space and the third 2 times. Upper floors take no
  ground. Heavy fittings (stalls, cellar, millstones, water wheel, anvil, vault) go on the ground floor only.
- **Upgrading a structure** (wattle to timber, timber to stone) costs the new structure's materials for its rooms less a quarter,
  plus the work. The building keeps its rooms, fittings, stores and lines, and counts as damaged while the work is under way.
- **Costs** (the spec's room table; D2-166):

| Room | Timber (on a stone footing) | Stone |
|---|---|---|
| small room | 8 timber, 2 stone; 6 units | 30 stone, 4 timber; 40 units, a mason |
| medium room | 15 timber, 4 stone; 15 units | 60 stone, 8 timber; 90 units, a mason |
| hall | 80 timber, 20 stone; 200 units, a carpenter | 150 stone, 20 timber; 250 units, a mason |

  Wattle: a small room only, 8 timber and 6 units, as now.

## 3. Storage (D2-155)

Capacity by kind:
- free floor: 30 weight a space;
- bins: 60 food a space;
- granary floor: 300 grain;
- cellar: 40 food a space of the building's footprint;
- woodshed: 40 timber, kept dry;
- vault: 30 weight a space.

A store can't take more than it holds. What doesn't fit is refused, or left outside if put there.

## 4. Fittings, new and changed

| Fitting | Change |
|---|---|
| cellar | 4 stone, 6 units (D2-155) |
| beds | 1 timber and 2 straw a bed (proposed) |
| stalls | 1 timber and 1 unit a beast, 2 spaces a beast; beasts housed in winter: fodder x0.8, dung kept x1.5, not driven off without entering |
| woodshed | a lean-to: 2 timber, 1 unit, 2 spaces of ground; 40 timber kept dry |
| vault | a stone room of its own, ground floor: 4 spaces, 40 stone, 30 units, a mason; does not burn (D2-49) |
| water wheel and leat | 60 timber, 20 stone, 2 copper, 250 units, a carpenter; on millstones; a river site (D2-166) |

Fitting work already runs over days (02zg, ab971ff).

## 5. Beds for everyone (D2-165)

- **Members need beds:** household members sleep housed only in a bed, as guests do. This replaces night.py's rule that members
  sleep at home whatever the beds.
- **Defaults, which Zach is to confirm:**
  - an infant shares its carer's bed;
  - two children share one bed;
  - without a bed, one sleeps on the floor as in a damaged house (1.2 food, 1.5 in the cold).
- **Seeded houses** start with beds for their household. Check every world file and add beds where a house has fewer than its
  people.

## 6. The mill ladder (D2-167)

- **Hand mill:** grinds about 3 grain a unit and gives **meal**: porridge-grade, food 1.0, raw 0.5.
- **Ox mill and water mill:** give **flour**, as now.
- **Bread** is baked from flour only.
- **Existing worlds:** seeded flour stays flour.

## 7. Wear by structure, repair by size (D2-168)

**Breaks.** The chance of a break each night (now 0.02, and 0.08 in the cold) is multiplied by structure:
- wattle x1.5;
- timber x1;
- stone x0.4 (proposed).

**Repair.** A break is mended with 1 timber and 1 unit for every 4 beds of the building's size, at least 2 and 2. A stone building
uses stone in place of timber.

## 8. Clearing for building

- **Farmland:** a field, pasture or meadow becomes built ground with 4 units of work a unit of size, and stops being farmland.
- **Woods:** a wood felled to scrub becomes built ground with 10 units a unit of size (grubbing out the roots).
- **The claim:** clearing is a claim with grounds `cleared` (D4-60's rule for fields, extended).

## 9. What agents see

**Each building:**
- its floor, used and free: "Reed House: 12 spaces, 9 used: 6 beds, a hearth, bins, a hand mill; 3 free";
- its rooms and storeys;
- its tier (§10);
- its description, in quotes as its builders' words.

**Each parcel:** its ground in spaces, used and free.

**Blueprints:** the build verb lists every blueprint, room addition, upgrade, storey and fitting the agent knows, with its full
needs. It already shows needs whether or not they're held.

**Storage refusals** say what is full: "the bins hold 60 food; 58 are in them".

## 10. Lines, the monument and tiers (D2-169 to D2-171; proposals/building_lines.md)

- **Description:**
  - `build {..., "describe": text}` writes one sentence (about 25 words) with the build;
  - `write {at, description: text}` replaces it.
- **Lines:**
  - `write {at: a building or monument here, line?: which, text}` writes a line (about 30 words), or replaces one;
  - `erase {at, line}` scratches one out.
  - Places by size: small room 2, medium 4, hall 8, monument 3.
  - Costs (D2-170): painting 2 units; carving 4 units with a tool, which wears it; carving in stone 6 units, a mason's; changing or
    erasing another's line, or the description, the same plus 1.
  - Writing is seen by the noticing rule, as work at the building. Its people notice a change the next time they see it ("the
    dedication over the door has been scratched out").
- **Reading:**
  - whoever enters a building (sleeps, works or speaks inside) or attends to it reads its lines that day;
  - lines are shown as writing in the world: 'Carved over the door: "..."', quoted and capped in length, never as part of the
    agent's instructions;
  - a reader may keep a line as one of its own lines kept for good (D4-64), by its own choice;
  - a ruined building can't be read;
  - painted lines on wattle fade, one for each break of the building.
- **The monument:** a building with no room.
  - Kinds: a carved post (2 timber, 2 units), a standing stone (4 stone, 4 units, a mason's) or a cairn (6 stone, 3 units).
  - It stands on any parcel but water, takes 1 space of ground on built ground or scrub (none elsewhere), and has a description and
    3 lines.
- **Tiers** (D2-171): `build {..., "how": "fine" | "rich" | "grand"}`, a modifier, for a building or a monument.

| Tier | Materials | Work | Noticed |
|---|---|---|---|
| plain | x1 | x1 | as any building |
| fine | x1.5 | x2 | also from neighbouring parcels |
| rich | x2.5 | x4 | also named in the village overview and on arrival |
| grand | x4 | x8 | also seen from the road's last stretch coming in |

  The tiers are described "finely built", "richly built" and "a grand ...". A tier is raised later by paying the difference.
- **The journal** keeps every text with who wrote it, when, and what it replaced.

## Order

1. Space and storage (§1, §3).
2. Rooms, structures and costs (§2, §4, §6).
3. Beds (§5).
4. Wear (§7).
5. Clearing (§8).
6. Lines, the monument and tiers (§10).
7. The view (§9).
8. The seed check of every world file (beds, floor for what is in each building).

## Tests

| Test |
|---|
| a small room (6 spaces) takes 4 beds, a hearth and bins, and refuses a hand mill until a bed goes or a room is added |
| an added room costs a quarter less than the same room alone; a second storey is refused unless the building is stone |
| a farm household's 200 grain does not fit a cottage's bins; it fits a family house with a granary floor |
| the Green (built ground, size 2: 48 spaces) refuses a ninth cottage |
| clearing a pasture of size 1 (4 units) turns it into 24 spaces of built ground |
| upgrading a wattle house to timber keeps its beds, fittings, stores and lines |
| a household of 5 with 4 beds: one sleeps as in a damaged house; with an infant, all 5 are housed |
| a hand mill gives meal at 3 grain a unit; bread from meal is refused; bread from mill flour is made |
| over 100 nights a stone building breaks less than half as often as a wattle one; repairing a hall takes 7 timber and 7 units |
| carving a line in stone takes 6 units and a mason; erasing another's line costs 1 more and is seen by someone working there |
| an agent sleeping in a building with a line reads it in the next morning's message, quoted, as writing on the wall |
| a grand monument is seen from the road's last stretch coming in; a plain one is not |
| a hall costs about 270 units in all and a water mill about 350 (02zf's pricing) |

## Running it

**Prerequisite:** a dry run with bots for the access gates (scenario_design).

**The live run:** one generated village with children on, its ground nearly full, a river site, and a few couples coming of age.
Read:
- whether households build, extend, store or clear as families grow;
- whether a mill is built and who holds it;
- what gets written on buildings, and whether any line spreads;
- whether anything is built finely, or defaced.

**The control:** the same world with the monument and lines unknown.

## Not in this package

- plot shares (D2-163): waiting on Zach's choice of crop records (option C);
- room bookings;
- rooms as places;
- fire spreading between buildings;
- floods;
- bridges and works on the land (OPEN L-34);
- walls and towers;
- the pound and the common granary as their own kinds.
