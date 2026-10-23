# Proposal: things left in places, and who finds them

**Status:** discussion (23 Oct). Design only. **Owner:** 37.2 (author); places, perception and the engine are 37.4's, and this
extends their [objects_in_world.md](objects_in_world.md) and the movables of [layout.md](layout.md), so 37.4 may merge it there.
**Affects:** spec/world/places.md, edges.md, holding.md; spec/information/perception.md, signs.md; spec/conflict/defence.md (fuse
events on the road); cybertron2/engine (containers, `leave`, death, signs.py).

## Summary

One kind of thing covers goods put down, a cache hidden in the forest, a load dropped on the road, a body and what it carried, a
lost herd, a camp, traces, and the end of a hidden way: **something at a spot** (a parcel at a node, or a stretch of road), with
how conspicuous it is. **One rule decides who notices it**: being there, what one is doing there, attention, knack and traces,
the same rule hidden_ways.md proposed for ways. Roads, journeys.md's notices and hidden_ways.md become cases of it. Finding
something gives a choice (take it, leave it, bury, tell), and a left thing is whoever's holds it (D4-23).

## The proposal

### 1. A thing at a spot

- **Spots:** a parcel at a node (layout.md), a room, or a **stretch of road**: an edge is split into one stretch for each day of
  its length (`Road(edge, stretch)`), so a 3-day road has 3 stretches, and a traveller on its second day is on stretch 2 (or on
  the stretch from the other end in the opposite direction).
- **Things:** a pile of goods (a container with a place: D4-34), remains (a body and what it carried), a herd, a camp, a trace (ashes,
  ruts, tracks), a hidden way's end (hidden_ways.md). Each has a **conspicuousness** from its size and kind, the cover of the spot,
  and any work spent hiding it.

| Thing | On open ground or a road | In woodland or scrub | Hidden with work |
|---|---|---|---|
| a body | 0.9 | 0.5 | buried: 0.05 |
| a heap of goods (10 or more) | 0.9 | 0.4 | under brush 0.15; buried 0.02 |
| a small pack | 0.4 | 0.15 | 0.02 |
| a herd | 0.95 | 0.6 | |
| a camp, used lately | 0.7 | 0.4 | |
| traces (ashes, ruts, tracks) | 0.3, fading over days | 0.2 | |
| a hidden way's end | | 0.01 to 0.03 (hidden_ways.md) | |

### 2. Putting things down and hiding them

- **`leave {item, qty, at}`**: puts goods down at a spot here (a parcel, or the stretch of road one is on). It costs nothing more
  than any give.
- **`hide {item, qty, at}`**: work (about 1 unit for a pack under brush, 2 to bury it; more for more) lowers the conspicuousness as
  in the table. Woodland and rock hide better than a field.
- **Being seen putting it there:** leaving and hiding are acts like any other, seen by those present by attention (seeing.md). A
  cache is only secret if nobody watched. The hider remembers where it is; telling is a choice (as for ways).

### 3. Who notices: one rule

For each person and each thing at a spot, each day (keyed draws, D2-70):

**chance = conspicuousness x presence x attention x knack x traces**

| Factor | Values (proposed) |
|---|---|
| conspicuousness | the table in §1 |
| presence | working that parcel 1.0; crossing it 0.3; at the node, elsewhere 0.05 (only things above 0.8: a herd, smoke, a body on the green); on that stretch of road 1.0 |
| attention (seeing.md) | none 1; attending to the place x3; attending to it then working in it (a search) x5 |
| knack | an eye for the land (D4-50) or woodcraft (hidden_ways.md): novice x0.5 to master x3; a herder for herds, a hunter for tracks |
| traces | fresh tracks or disturbed ground lead to the thing: x2; a party passed lately x5 |

Capped at 1. What is noticed shows through its signs (D4-48), so a body seen far off reads differently from one found close.
Today remains are shown to everyone at the node at salience 0.7; under this rule a body on the green is still seen by nearly all,
one in the far wood by few.

### 4. On the road

- **A death on the road leaves remains on that stretch.** Travellers who pass it roll to notice (§3), more on an open road, less in
  woodland. This closes D2-4: a household learns of a death on the road from someone who saw the body.
- **What a traveller can do on finding something:** it makes no call in transit (D4-10). Proposed: if what it finds is worth taking
  (goods, a herd, a person still alive), it gets one short call as a fuse event (D2-5), with the menu take what it can carry,
  drive the herd, bury the body, mark the spot, or go on; the same exception to D4-10 road_encounters.md asks for. Anything else is
  only remembered on arrival (journeys.md).
- Things left on the road (a load too heavy to carry on, D4-32; a broken cart) are the same.

### 5. Whose a left thing is

- The engine enforces possession only (D4-23): a left thing is held by nobody, so whoever takes it holds it. The leaver's claim is
  social: others may honour it or not; a taker seen taking can be named, owed, or punished by custom or law.
- Taking from remains is as today (`take` from someone's remains).

### 6. Change over time

- Food in the open spoils faster than in a house (proposed x2), and animals scavenge: meat and bodies first, grain in the open
  next, buried things rarely.
- A body's signs change ("dead some days", then "bones by the ford"), and are gone after about a season.
- Traces fade over days. A hidden way grows back (hidden_ways.md).

## What it gives a world

Caches against raids and lean winters (grain buried in the forest); smuggling and theft (goods hidden on the way); a dead
traveller found and their kin told; loot and lost loads found on the road; later, markers and offerings ([objects_in_world.md](objects_in_world.md)
Q4).

## Engine gap found while writing this (for 37.4)

`p_die` in cybertron2/engine/world.py makes remains only when the person dies at a node; a person who dies on the road loses what
they carried (it is set to zero and put nowhere). That breaks D4-34 (goods are always in a container with a place). In the region
run (38.23) people died on the road, some carrying grain. Until roads hold things, the smallest fix is remains on the road.

## Why

- One rule instead of four: placed goods, bodies, herds and hidden ways all use the same noticing, so a new kind of thing needs only
  its conspicuousness and signs.
- It makes the world physical in the way the runs lacked: what is dropped stays, what is hidden can be found, and the road holds what
  happened on it.

## Alternatives considered

- **Everything at a node seen by everyone** (as remains are now): simple, but nothing can be hidden, and position inside a node means
  nothing.
- **A separate mechanism per thing** (a body rule, a cache rule, a way rule): more rules, each tuned alone.
- **A road as one place without stretches**: cheaper, but then a body on a 4-day road is equally near every traveller on it, and an
  ambush has no position.

## Open questions (for Zach, and 37.4)

1. One noticing rule for every thing at a spot, hidden ways included, as in §3?
2. Roads split into one stretch per day of their length?
3. `leave` and `hide` at a spot, with hiding as work and concealment by cover and effort?
4. Finding something worth taking on the road gives a short call (a fuse event); anything else is remembered on arrival?
5. A left thing held by nobody, the leaver's claim only social?
6. Spoilage and scavenging in the open, and how long a body and traces last?

## History

- 23 Oct: Zach: is there a spec for fuse events, meetings on the road, someone who starves on the road being seen and their goods
  taken, and observations on the road? These should be a special case of leaving objects somewhere, within a parcel, so people can
  place or hide something in the forest with different saliences. Checked: only D2-5's mechanism is in spec (conflict/defence.md);
  meetings, journeys and objects in the world are proposals; the engine drops the goods of those who die on the road. Written.

## Sources

[objects_in_world.md](objects_in_world.md), [layout.md](layout.md), [place.md](place.md), [seeing.md](seeing.md),
[journeys.md](journeys.md), [hidden_ways.md](hidden_ways.md), [road_encounters.md](road_encounters.md),
[fuse_events.md](fuse_events.md); [38.23](../../review/38_space_engine/23_region_run.md); D2-4, D2-5, D2-70, D4-10, D4-23,
D4-32, D4-34, D4-35, D4-48, D4-50.
