# Proposal: objects placed in the world

**Status:** discussion (23 Oct; flagged to explore). **Owner:** 37.4 (places, perception). **Affects:** spec/world/places.md,
spec/information/perception.md, spec/world/holding.md (carried goods), cybertron2/engine (containers, verbs, signs.py).

## Summary

Today goods are always in someone's hands or a building's store, or lie where someone died (remains, a container at a place). Zach
(23 Oct): `leave` could put an object down on a parcel, so it sits in the world, is noticed by anyone there, and stands out. This
file holds that idea and the questions it raises: how objects get placed in the world, who notices them, and whose they are.

## The proposal (to explore)

- **A pile on a parcel:** `leave {item, qty, at: a place here}` puts goods down in the open as a container at that parcel (the same
  record as remains). Anyone at the node can take from it (possession, D4-23); taking is seen as any act is.
- **Noticed:** a pile shows through signs (D4-48), with a high chance for something large or unexpected (a cart left on the road, a
  heap of grain in a field) and a low one for something small or hidden.
- **Giving into a store** stays `give` (to a person, a household or a building). If `leave` becomes the open-ground act, `leave`
  into a building is folded into `give`.

## Why

- Objects in the open make the world physical: a cache, a dropped load, a gift on a doorstep, a warning left at a boundary, goods
  abandoned by someone too heavy to go on (D4-32), loot left behind after a raid.
- They test the rules of possession and witness: whose is a thing nobody holds, and who saw it put there.

## Open questions

1. Whose is a left object: still the leaver's (a claim others may honour), or anyone's who takes it?
2. Hiding: can something be left out of sight (buried, under a stone), noticed only by someone looking there?
3. Decay and weather: what spoils or is carried off by animals in the open.
4. Markers: boundary stones, signs, offerings: objects whose meaning is what they say, not what they are.
5. Does `leave` into a building merge with `give` now, or wait for this?

## History

- 23 Oct: flagged by Zach while discussing whether `leave` is the same as `give` ("we could have leave on a parcel, so an object could
  just sit in the world, and will be noticed by anyone and is very high salience").

## Sources

D4-23, D4-32, D4-35, D4-48; cybertron2/engine (remains as a container at a place).
