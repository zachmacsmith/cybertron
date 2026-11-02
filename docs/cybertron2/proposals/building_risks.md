# What can happen to buildings and fittings, by weather and use (flagged for later)

**Status:** deferred (OPEN L-48), with the harsher weather (L-47) and the levels of fire (L-46)
**Owner:** 37.4 (the night, buildings in the engine, signs); 37.2 owns buildings.md and lodging.md, where the rules would go

## Summary

Each building and fitting gets the risks it really had. Each risk is triggered by the world's own state: weather, lying snow,
season, cold, a parcel's height, structure, condition, use. Each can be guarded against at a price, and each is sensed as a change
(guides/senses.md), never announced.

## The proposal

### Buildings

| Building | Risk | Trigger | Guard | Sensed as |
|---|---|---|---|---|
| Wattle house | thatch torn; walls slump | gales; heavy rain (beyond today's nightly breaks, D2-168) | mending with straw and timber; stone footings | "the thatch on the Hearne hut is lifting at the eaves"; drips |
| Wattle house | collapse under snow | lying snow for several nights | clearing the roof (a unit) | a sagging ridge; creaking at night |
| Any house with a fire | house fire, spreading to neighbours | a hearth or oven inside; dry and windy weather; wattle and timber | a stone hearth and chimney; space between houses; water to hand; someone awake | smoke, then flames, by the whole village |
| Timber house | rot at the sills | damp ground; wet seasons over time | stone footings; repair | soft wood; a smell of rot |
| Stone house | damp and cold without a fire | cold nights | fuel | damp walls |
| Storeys | load on a weak ground floor; snow load | snow; gales | timber or stone | |
| Camp | blown down; fire out | gales and heavy rain (D4-83); harder with L-47 | windbreak, extensions (L-47) | |

### Fittings

| Fitting | Risk | Trigger | Guard | Sensed as |
|---|---|---|---|---|
| Hearth | chimney fire; smoke; cracks | a big fire (L-46); dry wind | repair; not overloading | sparks on the roof |
| Fire ring | sparks to thatch | wind | stone room, or outside | |
| Oven | house fire (the largest real risk); the crown cracks with firings | each firing; dry wind | a stone room or bakehouse; relining (a mason's technique) | smoke and heat; "the oven's crown is cracked" |
| Beds | damp straw, lice, illness (with disease) | wet seasons; crowding | fresh straw | "the bedding is damp and stinks" |
| Bins | rats and mice; damp | warm, wet weather; a full store; rotting heaps nearby | a granary floor; clearing spilt grain | droppings; gnawed grain; rats at night |
| Granary | as bins, rarer; damp if the roof leaks | heavy rain on a broken roof | roof upkeep | |
| Cellar | flooding on low, wet ground | heavy rain on a parcel of height 0 by water | building high; drainage work | water in the cellar |
| Woodshed | keeps fuel dry; fire if beside a hearth | rain soaks fuel left out (wet fuel needs more heat) | the woodshed | "the wood at the door is sodden" |
| Millstones | wear by grinding: dressing | use (about 300 grain); the ox's feed | dressing (a mason's technique); fodder | gritty, coarse flour; a thin ox |
| Water wheel | the leat silts; paddles break; floods; ice; low water | season and use; heavy rain at height 0; frost and lying snow; a dry late summer | seasonal crew upkeep of the leat; repair after floods | the river high and brown; the wheel stopped and iced; the leat choked |
| Anvil | fire; noise (already loud) | | a stone room | |
| Stalls | beasts sicken in muck; fodder runs out | long, wet winters | mucking out (gives dung); a hay store | stink; thin beasts |
| Monuments, lines | weathered, defaced | frost and gales slowly; people | repair; guarding | "the letters over the hall door are worn" |

### First, if taken up

1. House fire, from hearths and ovens, by structure and weather. It needs the scheduler's house-fire event (fuse.py notes it).
2. Floods on low ground: mills, cellars, the riverside (parcel height exists).
3. Mill upkeep: millstone dressing and the leat (see mill_and_oven_scale.md).
4. Snow load and torn thatch on wattle.
5. Rats in stores, linked to the heap signs (D4-90).
6. Damp fuel and the woodshed.

### Upkeep, as risks (moved here from mill_and_oven_scale.md by D4-97)

Upkeep and risk are one thing: each clearing or dressing is a small risk that comes due. Millstones are dressed after about 300 grain
ground, or their flour goes coarse and their output falls. The leat is cleared each season, or the wheel stops. An oven is relined
after about 10 firings, or it cracks. Each is a technique anyone may learn (dressing and relining are a mason's; clearing is crew
work).

## Why

Zach (2 Nov): "For each of the buildings / fittings, can you think about additional risks or occurrences etc. that we could add,
how these might relate to weather, environment conditions etc." Then: "save this as a deferred proposal". Today buildings only
break at random by structure and cold (D2-168), and fittings never wear.

## Open questions

1. The masonry gate: building in stone checks any mason's technique at one's best level (verbs._mason). Whether stone walling should
   be its own technique, so that knowing only quarrying does not let one build in stone.
2. Which of these are new techniques (dressing millstones, relining an oven, clearing a leat) that anyone may learn, as every craft is.

## History

- 2 Nov 2026: written at Zach's request after the mills-and-ovens discussion; deferred with the weather work.

## Sources

D2-154 to D2-168, D2-157, D2-159, D4-83, D4-89 to D4-93; fuse.py (the house fire waiting for the scheduler); review 38.49.
