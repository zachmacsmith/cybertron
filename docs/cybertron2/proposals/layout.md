# Proposal: the layout inside a node (parcels, features, and things on them)

**Status:** partly accepted: D2-114 to D2-116 and D4-62 (the parcel graph and the day's route, through parcel_graph.md), D2-154 and
D2-164 (space a count, not positions), D2-181 (parcels a node), D2-185 (covers as data); people not placed (Zach, 23 Oct). Features,
structures off built ground and scrub, and one place record for movables not built; under revision to one model (Zach, 4 Nov: see
History). **Owner:** 37.4. **Affects:** spec/world/places.md, land.md, holding.md;
information/perception.md; conflict/defence.md; seeding and generation. Generalises 38.04's sites, lots and land cover.

## Summary

A node's land is divided into a small graph of **parcels** (about 5-15): each a patch of one **cover** (forest, field, pasture,
meadow, water, marsh, built ground, yard or road, waste) with a size, its neighbouring parcels, and the side of the node it lies
on. **Features** run across or sit in parcels (a stream, a road, a well, a seam, a ford). **Structures** stand on built ground
(houses, workshops, a mill on the stream). **Movable things** (people, herds, carts, goods) are somewhere on a parcel or in a room.
Everything in a node is one of these four, so attention, holding, description and the land's changes all work on one model.
Moving within a node stays free; the layout is for **where things are relative to each other**, not for travel.

## The proposal

| Kind | Is | Examples | Holds |
|---|---|---|---|
| **Parcel** | a patch of land of one cover | the Long Field, Alder Wood, the common pasture, the green, the brook meadow | cover, size (in plots), soil, what it gives (plants, game, timber), neighbours, side of the node, claims (world/holding.md) |
| **Feature** | something running across or set in parcels | the brook, the north road, the well, the copper seam, the ford | its course (which parcels), its state (the brook's level) [still open (5 Nov): never built as entities: a brook is water parcels (world/parcel_graph.md), a road an edge with stretches and landmarks (D2-104, D2-107), a seam a parcel's resource (data.py RESOURCES); part of the 4 Nov revision] |
| **Structure** | something built on built ground or on a feature | houses, a smithy, a store, a mill on the brook, a fence, a wall | parts (02i), condition, rooms, claims [built: buildings.py, D2-9, D2-154: buildings only, on built ground (24 spaces a unit of size) or scrub (16); a water mill needs a water parcel (D2-61, data.py); fences are a parcel's state (D2-130, herds.py), not structures; structures on any land: the 4 Nov revision] |
| **Movable** | something that is somewhere and moves | a herd, a cart, a pack of goods, a body (people are not placed: see below) | where it is (a parcel or a room), its state [built as separate systems: herds at a parcel (herds.py), goods, bodies and carcasses as things at a spot (things.py, D2-85, D2-87, D4-52), goods in a building's store (D4-35); no common place record: the 4 Nov revision] |

- **Plots** are the divisions of a field parcel (world/holding.md: land counted in plots); **lots** are the divisions of built
  ground. [superseded by D2-163 (plot shares within a parcel) and D2-164 (a parcel's ground for buildings is a count of spaces, not
  lots or positions)]
- **Land changes are parcels changing cover:** felling and clearing turn forest into field; draining turns marsh into field;
  abandonment turns field back to scrub and forest (38.04 §5). [built: forests.py (a forest under 40% of its trees turns to scrub,
  D2-156), verbs.py (meadow, pasture or scrub cleared to a field, D4-60; a field, pasture, meadow or scrub cleared to built ground, a
  whole parcel at once, 02zh §8, proposed, no D-n); draining marsh and abandonment to scrub not built (fen's own changes in stage 2,
  D2-185)]
- **The node's edges leave from a side:** the north road from the north side, so a watch on the north side sees what comes that way.
  [built: layout.py, roads.py, D2-90, D2-114]

## Why it is worth having, even though moving within a node is free

| Use | Example |
|---|---|
| **Descriptions agree with each other** | "smoke over the trees to the north" means something; the village lies between the fields and the wood, the same for everyone |
| **Neighbouring parcels affect each other** | deer from the wood graze the field next to it; the brook floods the meadow and the houses on its bank; fire spreads to the next roof or into the wood; a herd strays from the pasture into the barley next door (a feud) |
| **What carries how far** | the forge's hammering is heard by the houses next to it, its smoke smelt across the green; a scream in the wood is heard only near the wood |
| **Defence** | a wall encloses built ground; a watch stands on the side the road comes in; a raid reaches the outlying houses first |
| **Attention** | every target is a thing in a state at a place: attend to a parcel (and whatever is on it), a feature, a structure or room, or a movable (a person, a herd, a cart), or the sky |
| **Claims** | a claim is on a parcel, a plot, a lot or a structure (world/holding.md) |

## Cover types: what a parcel is, as data

Each parcel has a **cover type**, and a cover type is a data row (D4-24: the world grows by data) that says everything about that
kind of land:

| Attribute | Meaning |
|---|---|
| **what can be done there** | the gathering and working methods it allows (forage, hunt, fell, graze, sow and reap, quarry, mine, fish, draw water) and the techniques they need |
| **what it gives** | its resources and how they come back (D4-7): plants and game renewable, timber slow, stone and ore finite, fish periodic |
| **building** | whether it can be built on, how many lots per unit of size, and what it costs to build there (rock is a good footing; marsh needs piles; a slope needs terracing) |
| **risks** | the incidents it is prone to and their base rates: flood (water, meadow, marsh), fire (forest, built ground, dry pasture), rockfall (quarry, rock), wolves (forest edge), fever (marsh) |
| **how it changes** | what it can become and how (fell and clear forest to field; drain marsh to field; abandoned field to scrub, then forest; a worked-out quarry to waste) |
| **what it gives off** | its fact rules and sense entries (seeing.md §3b): the wood's birdsong and the smell of leaf mould, the meadow's insects, the quarry's dust |

**First rows** (to be filled with numbers): [built in part: data.py COVERS (ground for buildings D2-154, sight and sound D2-99, digging
D4-99, ambient lines), what can be done as each technique's covers (data.py TECHNIQUES), grazing on the waste covers (D2-189), and
heath, moor, fen and saltmarsh added (D2-185); risks by cover still open (hazards are the scheduler's kinds, D2-77)]

| Cover | Can be done | Builds on | Risks | Becomes |
|---|---|---|---|---|
| forest | forage, hunt, fell | no (clear first) | fire, wolves | field (felled and cleared), scrub |
| field | sow, tend, reap, glean | yes, at the cost of its plots | flood if low | scrub (abandoned), built ground |
| pasture | graze, gather | yes | drought, fire when dry | field (ploughed), scrub |
| meadow (by water) | mow hay, graze | poorly (floods) | flood | field |
| water (brook, river) | fish, draw water, power a mill | a mill on a feature, a bridge | flood, ice | |
| marsh | gather reeds, fowl, fish | piles only | fever, flood | field (drained) |
| rock and quarry | quarry stone; mine a seam | yes, good footing | rockfall | waste when worked out |
| built ground | live, work, store, meet | yes (its lots) | fire | |
| scrub and waste | forage a little | yes | fire | forest (left), field (cleared) |

**The node's land kind (38.04 §2) is a distribution over cover types and features.** A river valley draws mostly field, meadow and
water with a little forest; hills draw rock, pasture and scrub, and perhaps a seam; a woodland draws mostly forest. A hand-made
world sets its parcels directly. [built: cybertron2/landgen/ (D2-174 the mesh, D2-183 a terrain sets which covers its land takes,
D2-191 the landscape systems); a hand-made world pins what it gives (D2-173)]

**Land is fixed per node, so uses compete.** A quarry takes parcels that could be pasture; houses take field; clearing forest
gives fields and loses the game and timber; draining the marsh gives the best fields and loses the fowl and reeds. Who decides what a
parcel becomes is a question of claims and institutions (world/holding.md), which is where land disputes and commons rules come
from.

## People are not placed on parcels (Zach, 23 Oct)

An agent is at the node, not on a parcel. Its **actions** say where its day was spent (sowing the Long Field, felling in Alder
Wood, a day at the smithy), and that is all the engine needs: facts about the parcels an agent worked on today are a little more
likely to be noticed by it. Herds, carts and goods do have a parcel (a herd in the wrong field is a fact; a cart left in the yard is
a fact).

**Senses are broad.** Most sounds, smoke and smells carry across most of the node: everyone in a hamlet hears the forge, a scream,
the church bell, the cattle; everyone smells a fire. Adjacency matters only at the edges: a quiet sound (a door forced at night)
reaches the neighbouring parcels and whoever is awake or on watch; a sound in the deep wood reaches those working near it.

## Attending, generalised

With the four kinds, the attention targets of seeing.md §3b reduce to: **a parcel** (with what grows and stands on it), **a
feature**, **a structure or one of its rooms**, **a movable** (a herd, a cart, goods, a body), **a person**, **a gathering** (people
together in one place or room), **the land and sky**, and **the place in general**: keeping one's eyes open all day, which picks up
the less subtle facts spread around the node (a few, here and there), its ambience (sounds, smells, the mood of the place), and a
better chance at anything salient, but no detail about any one thing. What attending gives comes from the thing's kind and state, and
the fact rules are written per kind (cover, feature, fitting, animal), not per named place. [built: prompt.py, perceive.py: attend
to a person, a building, a parcel, a herd, a thing by its tag (D4-68), the sky, the village (D2-116) or the place in general
(noticing.md: attention x3, the ambient lines); no features to attend to]

## Size and cost

A node holds a handful of parcels (a hamlet: green and houses, two or three fields, a pasture, a wood, the brook), each with a few
numbers; adjacency is a short list. The generator (38.04 §6) draws them from the node's land kind; a hand-made world names them.
None of it costs a model call.

## Open questions

1. How many parcels a node has (5-15?), and whether a parcel's size matters beyond plots and capacity. [decided: D2-181 (6 to 15 a
   node, a generator default); size counts ground for buildings (D2-154), wood (D2-156) and the work of clearing (D4-60)]
2. ~~Whether presence is tracked per parcel~~: no (Zach): agents are at the node; their actions say where they worked. [built:
   layout.py, D2-114 (nobody moves inside a node), D4-62 (the day's route from one's acts)]
3. Whether features like the brook and the road continue from node to node (the brook leaves by the south side and is the same
   brook downstream: 38.04 §6's rivers). [still open (5 Nov): roads continue as edges (D4-2, D2-104); the landgen mesh runs one
   river through nodes (D4-22, D2-174), but the engine keeps only water parcels per node, with no record of the river (checked
   DECISIONS.md, data.py, layout.py, landgen/settle.py); part of the 4 Nov revision]

## History

- 23 Oct: proposed (37.4, with Zach), after Zach noted that fields, herds and the rest are things in different states and asked for
  a general per-node abstraction of space, with a layout (the town next to the fields next to the forest) even if moving within a
  node is free.

- 23 Oct: Zach: agents should be able to attend to everything in general (less subtle things spread around, ambience); senses not
  restricted much (sounds across most of the node); no tracking of agents' parcels, since actions say where they happen. Added:
  people are not placed; senses broad, adjacency only for quiet sounds; "the place in general" as an attention target.

- 23 Oct: Zach: parcels should say what can be done there, whether they can be built on, and their risks; a node's environmental
  type sets the chances of each kind of parcel; a quarry takes parcels that could hold buildings. Added cover types as data rows
  (methods, resources, building, risks, changes, what they give off), first rows, the node's land kind as a distribution over
  covers, and competing land uses.

- 4 Nov: Zach and 37.4 discussed the layout. Since 23 Oct: the parcel graph was built (D2-114 to D2-116, D4-62); people are not
  placed (Zach); space became a count, not positions (D2-154, D2-164); features (brook, well, seam as entities) were never built;
  structures are only buildings, on built ground or scrub; movables became separate systems (herds, things at a spot, stores).
  Revision direction (Zach): finish it as one model: structures on any land, taking ground, with clearing a plot at a time; graves,
  cairns, folds and camps as small structures; one record for work in progress and decay; a common place record for movables. The
  design is not yet written.

- 5 Nov: swept (37.4): decided and built: the graph, sides and heights, the day's route, space as a count, parcels a node (D2-181),
  covers as data rows (data.py COVERS), clearing to field and to built ground, attention targets. Still open: features (the brook
  across nodes), risks by cover, draining and abandonment, and the one model of the 4 Nov revision.

## Sources

38.04 (places, land cover, generation), world/holding.md (claims, plots), seeing.md §3b (attention), 02i (buildings from parts),
02e §3.9 (lots).
