# Proposal: the layout inside a node (parcels, features, and things on them)

**Status:** discussion (23 Oct). **Owner:** 37.4. **Affects:** spec/world/places.md, land.md, holding.md;
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
| **Feature** | something running across or set in parcels | the brook, the north road, the well, the copper seam, the ford | its course (which parcels), its state (the brook's level) |
| **Structure** | something built on built ground or on a feature | houses, a smithy, a store, a mill on the brook, a fence, a wall | parts (02i), condition, rooms, claims |
| **Movable** | something that is somewhere and moves | a herd, a cart, a pack of goods, a body (people are not placed: see below) | where it is (a parcel or a room), its state |

- **Plots** are the divisions of a field parcel (world/holding.md: land counted in plots); **lots** are the divisions of built
  ground.
- **Land changes are parcels changing cover:** felling and clearing turn forest into field; draining turns marsh into field;
  abandonment turns field back to scrub and forest (38.04 §5).
- **The node's edges leave from a side:** the north road from the north side, so a watch on the north side sees what comes that way.

## Why it is worth having, even though moving within a node is free

| Use | Example |
|---|---|
| **Descriptions agree with each other** | "smoke over the trees to the north" means something; the village lies between the fields and the wood, the same for everyone |
| **Neighbouring parcels affect each other** | deer from the wood graze the field next to it; the brook floods the meadow and the houses on its bank; fire spreads to the next roof or into the wood; a herd strays from the pasture into the barley next door (a feud) |
| **What carries how far** | the forge's hammering is heard by the houses next to it, its smoke smelt across the green; a scream in the wood is heard only near the wood |
| **Defence** | a wall encloses built ground; a watch stands on the side the road comes in; a raid reaches the outlying houses first |
| **Attention** | every target is a thing in a state at a place: attend to a parcel (and whatever is on it), a feature, a structure or room, or a movable (a person, a herd, a cart), or the sky |
| **Claims** | a claim is on a parcel, a plot, a lot or a structure (world/holding.md) |

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
the fact rules are written per kind (cover, feature, fitting, animal), not per named place.

## Size and cost

A node holds a handful of parcels (a hamlet: green and houses, two or three fields, a pasture, a wood, the brook), each with a few
numbers; adjacency is a short list. The generator (38.04 §6) draws them from the node's land kind; a hand-made world names them.
None of it costs a model call.

## Open questions

1. How many parcels a node has (5-15?), and whether a parcel's size matters beyond plots and capacity.
2. ~~Whether presence is tracked per parcel~~: no (Zach): agents are at the node; their actions say where they worked.
3. Whether features like the brook and the road continue from node to node (the brook leaves by the south side and is the same
   brook downstream: 38.04 §6's rivers).

## History

- 23 Oct: proposed (37.4, with Zach), after Zach noted that fields, herds and the rest are things in different states and asked for
  a general per-node abstraction of space, with a layout (the town next to the fields next to the forest) even if moving within a
  node is free.

- 23 Oct: Zach: agents should be able to attend to everything in general (less subtle things spread around, ambience); senses not
  restricted much (sounds across most of the node); no tracking of agents' parcels, since actions say where they happen. Added:
  people are not placed; senses broad, adjacency only for quiet sounds; "the place in general" as an attention target.

## Sources

38.04 (places, land cover, generation), world/holding.md (claims, plots), seeing.md §3b (attention), 02i (buildings from parts),
02e §3.9 (lots).
