# Proposal: things left in places, and who finds them

> **Decided parts are in the spec:** spec/world/things_in_places.md, spec/information/noticing.md (23 Oct). This file keeps the reasoning, the history and what is still open.

**Status:** partly accepted: D2-85 to D2-87 (23 Oct); roads' layout, hiding and decay still to explore. Design only. **Owner:** 37.2 (author); places, perception and the engine are 37.4's, and this
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
- **Conspicuousness is the thing's own x the spot's sight (D2-102, visibility.md):** the cover columns below are that product
  for open ground and woodland, kept as a guide.
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

- **Putting down** is `give` to a place (verb_modifiers.md §5): goods left at a spot here (a parcel, or the stretch of road one is
  on). It costs nothing more than any give.
- **Hiding** is the `hidden` modifier on it (D2-93): work (about 1 unit for a pack under brush, 2 to bury it; more for more)
  lowers the conspicuousness as in the table; untaught it hides half as well. Woodland and rock hide better than a field, through
  the place's visibility (visibility.md).
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

### 6. Change over time: each item says how it decays (to explore with Zach)

Decided (D2-87): in the open, food and bodies spoil much faster and rot, and rotting things carry a disease risk. Proposed: every
item declares **how it decays under each condition**, as data, so the rule is one lookup and a new item is a new row.

**Conditions** (any that apply multiply): where it is (a house; bins, cellar or granary as now, D2-58; in the open; buried; in
water), the season (warm faster, frozen almost not at all), and wet (rain, a flood, a damp parcel).

| Item | In a house a day | Open, dry | Open, wet | Buried | Warm season | Frozen | Becomes |
|---|---|---|---|---|---|---|---|
| grain | 0.5% (D2-58) | x4 | x10 (sprouts, moulds) | x2 (damp) | x1.2 | x0.5 | nothing |
| bread | about 2% (keeps, D2-44) | x3 | x8 | x3 | x1.5 | x0.2 | nothing |
| fresh meat | about 15% | x2 | x2.5 | x1 | x1.5 | x0.1 | rotting meat |
| dried or salted meat | about 1% | x2 | x6 | x2 | x1.2 | x0.5 | nothing |
| cheese | about 1% | x3 | x5 | x1 | x1.5 | x0.3 | nothing |
| hides | none | 1% a day | 3% a day | 2% a day | | | nothing |
| timber, charcoal | none | none | charcoal and timber get wet: no use as fuel until dried | | | | |
| tools, coin, ore, stone | none | none (tools rust a little if wet) | | | | | |
| a body | | "dead some days" about 10 days, "bones" to the season's end | faster | kept | faster | kept | bones, then nothing |

**Scavengers: later (D2-95)**, with wild animals that attack herds and hunters and are drawn to food. What is meant: wild animals and pests that eat what is left exposed (crows and foxes anywhere, wolves and
boar in wild land, rats and dogs near houses). Separately from spoiling, an exposed item loses a share each day by how much it
draws them (meat and bodies most, grain and bread next, cheese, hides little, tools none), how many there are where it lies (the
parcel's wildlife; more in forest, rats at a settlement), and what protects it (buried, sealed, in a building: none). Scavengers
also make a thing **easier to notice** (crows circling a body, a fox at the grain), and may draw predators (wolves near a carcass,
a risk to herds and people).

**Rot and disease (D2-96):** a rotting body or rotting food lies at a spot, so once disease exists (OPEN Q-16) its risk reaches
what is near it: water (a well or stream downhill: environment_state.md's water cascade), food stored nearby, and people working
or living close. A death in a settlement is highly salient (the smell within days). **Burying** is work on the body, an option
shown only where a body lies: about 2 units in soft ground, 4 in stony ground, 6 or more in frozen ground (or wait for the thaw, a
cairn of stones instead); a burial ends the risk and the body's signs.

Traces fade over days (D2-88). How a hidden way hides again follows its land (D2-92).

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

1. ~~One noticing rule~~ decided: D2-85.
2. Roads: one stretch per day, or a layout with landmarks (a pass, a bridge, a ford) like a node's parcels? To explore:
   [road_layout.md](road_layout.md).
3. Hiding: a separate `hide`, or a modifier on `leave` that people know or learn? To explore:
   [verb_modifiers.md](verb_modifiers.md).
4. ~~A short call for a find on the road~~ decided: D2-86.
5. ~~Left things held by nobody~~ decided: D2-87.
6. Decay by item and condition, scavengers, rot and disease (§6): the table's numbers and conditions.

## History

- 23 Oct: Zach: is there a spec for fuse events, meetings on the road, someone who starves on the road being seen and their goods
  taken, and observations on the road? These should be a special case of leaving objects somewhere, within a parcel, so people can
  place or hide something in the forest with different saliences. Checked: only D2-5's mechanism is in spec (conflict/defence.md);
  meetings, journeys and objects in the world are proposals; the engine drops the goods of those who die on the road. Written.

- 23 Oct: Zach decided D2-85 (one noticing rule, through spontaneous observation, attending and salience), D2-86 (a short call
  only if the find is noticed at all), D2-87 (left things anyone's; the dead leave everything; open spoilage much faster, rot,
  disease risk). Asked to explore landmarks along roads (road_layout.md), hiding as an optional modifier on `leave` rather than a
  verb (verb_modifiers.md), and decay with each item defining how it decays by condition (§6 rewritten).

- 23 Oct: Zach decided D2-95 (scavengers later, with wild animals) and D2-96 (rot near water, food and people; a death in a
  settlement highly salient; burying as work on the body, shown only where one lies, by ground and cold). Putting down and hiding
  become `give` to a place with the `hidden` modifier (verb_modifiers.md §5); cover as the place's visibility (visibility.md).

- 23 Oct: D2-102: conspicuousness is the thing's own x the place's sight (visibility.md).

## Sources

[objects_in_world.md](objects_in_world.md), [layout.md](layout.md), [place.md](place.md), [seeing.md](seeing.md),
[journeys.md](journeys.md), [hidden_ways.md](hidden_ways.md), [road_encounters.md](road_encounters.md),
[fuse_events.md](fuse_events.md); [38.23](../../review/38_space_engine/23_region_run.md); D2-4, D2-5, D2-70, D4-10, D4-23,
D4-32, D4-34, D4-35, D4-48, D4-50.
