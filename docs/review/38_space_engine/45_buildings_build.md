# 38.45: the building package, as built (brief 02zh)

Session 37.4, 3 Nov 2026. Zach (through 37.2): "wrap together all the main building modules as a spec to build and get the other
agent to build this for real now"; to 37.4: "yes build it". Brief: [02zh](../37_growth/02zh_build_brief_buildings.md) (replaces
02y); spec economy/buildings.md (37.2's, current as of 3 Nov); proposals/building_lines.md; D2-154, D2-155, D2-165 to D2-171.
Branch `build/buildings-02zh`. Nothing under "Not in this package" was built (plot shares, D2-163, wait for Zach).

## What was built, by part

| Part | Built | Where |
|---|---|---|
| 1. Space | Ground in spaces (built 24, scrub 16 a unit of size) replaces lots; a building takes its footprint (ground-floor rooms, a room under way, a woodshed's 2, a vault's room) from its parcel; a monument 1 on built ground or scrub; a camp 4 there; D2-164's parcel line in spaces ("18 of 24 spaces used, room for 6 more spaces"); seeded buildings get the fewest rooms that hold their fittings and stores, plus `free` from the file | buildings.py: `ground_total`, `ground_of`, `ground_used`, `seed_rooms`, `best_rooms`; world.py `_new_building`; prompt.py `_ground_words` |
| 2. Rooms and structures | Rooms as records `{kind, floor, storey}`; a room added a quarter less; storeys 2 and 3 in stone only, at 1.5 and 2 times, up to the floor below, no ground; heavy fittings only within the ground floor; upgrade to timber or stone (new materials less a quarter, and the work; damaged at night while under way; keeps rooms, fittings, stores, lines); the room table's costs; one work at a time a building (`works`) | verbs.py `_new_building`, `_add_room`, `_upgrade`, `_works_progress`; buildings.py `room_cost`, `upgrade_cost`; night.py |
| 3. Storage | Stores by kind in order granary (grain, rye, beans), cellar (food, 40 a space of footprint), bins (food 60), woodshed (timber, firewood 40), vault (30 weight a space), then free floor 30 weight a space; `move` into a full store is refused with what is full; anything else that does not fit (a harvest, a make, a gift) lies outside the door, said in the result line | buildings.py `stores`, `alloc`, `fits`, `room_for`, `full_words`, `install`/`overflow` (a hook after create and transfer); verbs.py `_move`, `_into_store`, `_full_note` |
| 4. Fittings | Spaces for every fitting; cellar 4 stone 6 units; beds 1 timber 2 straw; stalls (2 spaces, 1 timber 1 unit a beast; in winter fodder x0.8, dung x1.5, not driven off by one who cannot get in); woodshed; vault (its own 4-space stone room, safe from fire); water wheel and leat 60 timber, 20 stone, 2 copper, 250 units | data.py FITTINGS; verbs.py `_fitting`, `_fitting_work`; farm.py `_herds`, `drive`; buildings.py `stall_share`, `vaulted`; run.py fire |
| 5. Beds | Members sleep housed only in a bed, eldest first; one with no bed at home looks for one where it may sleep, else lies on its home's floor as in a damaged house; the house lines say when beds are too few | night.py `sleeping_places`, `bed_share`, `night`; prompt.py `_house_lines` |
| 6. Mill ladder | Hand mill: 3 grain a unit into meal (food 1.0, raw 0.5, porridge); bread and oven bread from flour only; seeded flour stays flour | data.py ITEMS `meal`, TECHNIQUES `grind` |
| 7. Wear and repair | Breaks x1.5 wattle, x1 timber, x0.4 stone; repair takes 1 timber (stone for stone) and 1 unit for every 4 spaces of floor, at least 2 and 2, materials at the start and the work 2 units an action (`mending`); a painted line on wattle fades at each break | night.py; verbs.py `_repair`; buildings.py `repair_need` |
| 8. Clearing | `work clear for building`: a field, pasture or meadow 4 units a unit of size, scrub 10, to built ground; farmland ends (crop and grass gone); a claim with grounds `cleared` if nobody held it | verbs.py `_clear_built`; data.py TECHNIQUES `clear for building`, CLEARING `built`; knowledge.py `ready` |
| 9. What agents see | Each building: structure, tier, rooms and storeys, "12 spaces, 9 used: 6 beds, a hearth, bins; 3 free", work under way, holder, its description quoted as its builders' words; each parcel in spaces; the build verb lists each room by structure with its full cost, each fitting's spaces and store, the monuments, rooms added, storeys, upgrades, `describe`, and for one's own buildings here what each addition and the next upgrade would take; the tiers show as the build verb's ways; refusals name what is full | prompt.py `building_line`, `_craft_note`, `_build_more`, `verb_lines`; view.py through `_place_lines` |
| 10. Lines, monument, tiers | `build {..., describe}`; `write {at, text, line?, how?}`, `write {at, description}`, `erase {at, line}`; places small 2, medium 4, hall 8, monument 3; painting 2, carving 4 with a tool (worn), in stone 6 and a mason, another's +1; writing is an event (own 3) read by the noticing rule; its people read what changed the next time they see it; whoever sleeps, works, makes, builds, stores, speaks inside or attends reads the lines, shown next morning as 'Painted over the door of Hobb House: "..."', framed as others' words with the note that one may keep a line; a ruin cannot be read; the monument (carved post, standing stone, cairn); tiers fine, rich, grand by `how` (a modifier), raised later by the difference; each line keeps what it replaced (`was`, `was_by`) and every change is journaled | verbs.py `_write`, `_erase`, `write_units`, `_monument`, `_upgrade`; buildings.py `read`, `entered`, `line_words`, `cap_text`; perceive.py `evening`; night.py; prompt.py `written_lines`; signs.py BUILDING tier rows, `GRAND_AHEAD`; layout.py `tier_words`, `overview`, `layout_lines`; roads.py `_notices` |

## Data keys (data.py; all calibrate)

COVERS `ground`; FITTINGS `spaces`, `holds`, `by`, `heavy`, `ground`, `room`, `fodder`, `dung` (stalls); ROOMS (floor, places, cost by
structure); BLUEPRINTS (rooms and the camp); SPACE (`added` 0.75, `storeys` {2: 1.5, 3: 2}, `upgrade` 0.75, `order`, `camp_floor` 4,
`monument_ground` 1, `seed_free` 0); STORES (kinds, order, floor 30, words); MONUMENTS; TIERS and TIER_ORDER; LINES (places, words 25
and 30, chars 240, units 2/4/6, other 1, carve tools and wear, spots, how); CLEARING `built`; PHYSICS `breaks.structure`, `repair`
{per 4, min 2}, `beds`; TECHNIQUES `grind` (3 grain to 3 meal), `repair` (no fixed input), `clear for building`, `how: fine|rich|grand`;
ITEMS `meal`. Signs: signs.py TIER_LOOK (a presentation choice), the tier rows' `own` (fine 4 within next door, rich 6, grand 10) and
GRAND_AHEAD (own 3 on the road's last stretch).

## Part 5 defaults, for Zach to confirm (PHYSICS `beds`)

- An infant takes no bed (it shares its carer's): `infant: 0.0`.
- Two children share one bed: `child: 0.5`; youths, adults and elders one each.
- Without a bed one sleeps on the floor as in a damaged house (1.2 food, 1.5 in the cold): `floor: "damaged"`.
- Beds go eldest first (elders, adults, youths, children, infants; then by name).

## Deviations and readings (also OPEN.md Q-24)

- **Camps** keep no floor and no store limit (a lean-to: what lies in it is not counted); they take 4 spaces on built ground or scrub.
- **Upper storeys** cost the room alone times 1.5 or 2, without the added-room quarter off as well.
- **Repair** "for every 4 beds of the building's size" is read as every 4 spaces of floor (a hall's 30: 7 timber, 7 units).
- **A mason** is anyone who knows a mason's craft (hearth, oven, cellar, millstones, quarrying, walling): no new technique; building
  in stone, a standing stone, a vault and carving in stone need one. A mason's fitting may now be built by any mason.
- **Spoilage** in a store is still at its best keeping fitting for all of it (as before), not by where each good lies.
- **The woodshed** holds 40 timber or firewood; "kept dry" has no effect, because the engine has no wet timber in stores (Q-23 (10)).
- **Warmth**: a hearth's 12 spaces are now set against the building's floor in spaces (D2-159), not its old `size` in people.
- **Seeded houses are given no free floor** (the brief's rule; `seed_free` 0). Some are full on day 1 (combe's Hobb House: 12 spaces,
  12 used), so their household's first gathered goods are refused or left at the door. A world can give `free:` on a building.
- **A building's `size`** in a world file is no longer read; the record's `size` is now its floor.

## World files changed

Built-ground parcels too small for their seeded buildings in spaces, made a unit larger: `bf_green` 2 to 3 (barleyfield_s1, region,
region_c, region_c_s27, region_s1), `cg_yard` 1 to 2 (region, region_c, region_c_s27, region_s1), `h_green` 1 to 2 (hamlet,
hamlet_s1). Every seeded house already had beds for its household under the new rule; no beds were added. Two existing tests changed
with the rules they test: test_cybertron2_fittings_ground (a cellar is 6 units: three actions; ground in spaces; materials in hand,
as the house's floor is full) and test_cybertron2_package_f (warmth by rooms).

## Checks

- tests/test_cybertron2_buildings.py: the brief's 13 tests and 5 more (overflow at the door, stalls, the seed check of every world
  file, a capped line and the description shown, tiers costed and named on arrival): 18 pass.
- The whole cybertron2 suite: 248 pass.
- Bot runs, 20 days: combe_evening and frontier_camps finish with no errors; both replay with no mismatches.
