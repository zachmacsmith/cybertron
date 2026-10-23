# Things in places: putting down, hiding, the dead, burial

## Summary

Anything not in someone's hands or a building's store lies at a spot: a parcel at a node, or a stretch of road. Goods put down,
goods hidden, a dropped load, remains of the dead, a camp, traces. Whoever finds a thing can take it. Things in the open spoil much
faster, and bodies and rotting food rot where they lie. Burying is work on a body.

Written by 37.2 at Zach's request (23 Oct), from proposals/things_in_places.md and verb_modifiers.md; the area is 37.4's. It
extends world/places.md, world/holding.md (D4-23) and core/architecture.md (containers, D4-34).

## Decided

- D2-85: things at a spot are noticed by one rule (information/noticing.md).
- D2-87: left things are held by nobody: anyone can pick them up; the dead leave everything where they die; in the open food and
  bodies spoil much faster and rot, with a disease risk.
- D2-93: hiding is the `hidden` modifier, tryable untaught (agents/modifiers.md).
- D2-96: rot near water, food and people; a death in a settlement is highly salient; burying is work on the body, shown only where
  one lies, its labour by the ground and the cold.
- D2-111: `leave` folds into `give`; a give that cannot reach its recipient is left at its door.

## Mechanics

### Spots

A spot is a parcel at a node (world/places.md) or a stretch of road (world/roads.md). A thing at a spot is a container with that
place (D4-34): a pile of goods, remains (a body and what it carried), a camp, a trace.

### Putting down: `give` (D2-111)

`give {item, qty, to}`, where `to` is a person, a household, a building, or a place here (a parcel, or the stretch one is on);
`leave`, `put`, `drop` and `hide` are read as `give` to a place.

| Giving to | What happens |
|---|---|
| a person here | into their hands |
| a household, or a building one may use | into its store |
| a building one may not use, or someone not here | left at its door, in the open |
| a place | left there, in the open |
| a place, `hidden: under brush` or `hidden: buried` | hidden there (information/noticing.md: x0.2 or x0.03 conspicuousness) |

- Giving costs nothing; hiding costs work: about 1 unit under brush, 2 to bury (more for more than a pack).
- Putting down and hiding are acts seen by whoever is present, by attention (perception.md): a cache is secret only if nobody
  watched. The hider remembers where it is; telling is its choice.
- In the departure prompt (the "too heavy to set off" call, D4-32), a give to someone not at home or to a house one has no access to
  leaves the goods at that house's door.

### Whose (D2-87, D4-23)

A thing at a spot is held by nobody: whoever takes it holds it (`take` from a place, or from someone's remains, as now). The
leaver's claim is social only. Taking is an act seen by whoever is present.

### The dead (D2-87, D2-96)

- The dead leave everything they carried where they die, at a node or on the road (world.p_die; remains on the road since 06c7148).
- A body's signs change: "dead some days" for about 10 days, then "bones" until the season's end, then nothing. In a settlement a
  body is highly salient (own conspicuousness 1.0 on built ground; its signs grow with the days).
- **Rot:** a rotting body or rotting food at a spot is a thing with a disease risk (environment/scheduler.md, D2-71), reaching what is
  near it: water (a well or stream downhill), food stored nearby, people working or living close. Disease itself waits (OPEN Q-16,
  L-9); until then rot has signs but no effect on health.
- **Burying** (D2-96): `work {what: bury, at: <remains>}`, an option shown only where a body lies. About 2 units in soft ground, 4 in
  stony ground, 6 or more in frozen ground; or a cairn (3 stone, 2 units). A burial ends the body's rot and signs; what it carried
  stays with whoever took it, or is buried with it.

### Decay in the open (D2-87)

Things in the open spoil much faster than in a house, by the item's own decay table (economy/goods.md, "Decay").

## Data

Per thing at a spot: its place (parcel or stretch), contents, own conspicuousness, hidden (how, by whom), the day it was put there,
for remains whose they were and the day of death.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| hiding work | under brush 1 unit, buried 2 | proposed; calibrate |
| a body's signs | "dead some days" about 10 days, then bones to the season's end | proposed; calibrate |
| burying | 2 units soft, 4 stony, 6 or more frozen; a cairn 3 stone and 2 units | proposed; calibrate |

## What agents see

Things they notice where they are (information/noticing.md); the bury option where a body lies; what they put down and where.

## Open

- Scavengers, with wild animals (OPEN L-2).
- Markers and offerings, objects whose meaning is what they say (proposals/objects_in_world.md Q4).

## Sources

[proposals/things_in_places.md](../../proposals/things_in_places.md), [verb_modifiers.md](../../proposals/verb_modifiers.md),
[objects_in_world.md](../../proposals/objects_in_world.md).

*Current as of 23 Oct 2026: D2-85, D2-87, D2-93, D2-96, D2-111.*
