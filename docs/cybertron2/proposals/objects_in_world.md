# Proposal: objects placed in the world

**Status:** superseded by proposals/things_in_places.md (which extends it; accepted: D2-85 to D2-88, D2-93, D2-95, D2-96, D2-111,
with D4-68, D4-70, D4-89, D4-90 and D4-99 since) and built (things.py); still open here: markers (boundary stones, offerings) and
what weather does to things in the open. **Owner:** 37.4 (places, perception). **Affects:** spec/world/places.md,
spec/information/perception.md, spec/world/holding.md (carried goods), cybertron2/engine (containers, verbs, signs.py).

## Summary

Today goods are always in someone's hands or a building's store, or lie where someone died (remains, a container at a place). Zach
(23 Oct): `leave` could put an object down on a parcel, so it sits in the world, is noticed by anyone there, and stands out. This
file holds that idea and the questions it raises: how objects get placed in the world, who notices them, and whose they are.

## The proposal (to explore)

- **A pile on a parcel:** `leave {item, qty, at: a place here}` puts goods down in the open as a container at that parcel (the same
  record as remains). Anyone at the node can take from it (possession, D4-23); taking is seen as any act is. [built: things.py,
  verbs.py `give`, D2-111 (giving to a place), D2-164 (no position in the parcel, only how plain or hidden it lies), D4-68 (a tag,
  T1, T2, ...), D4-70 (taking what one did not know of is a search)]
- **Noticed:** a pile shows through signs (D4-48), with a high chance for something large or unexpected (a cart left on the road, a
  heap of grain in a field) and a low one for something small or hidden. [built: things.py, D2-85, D2-102, D4-75 (one noticing
  rule), D4-90 (by bulk: a heap of about X to Y)]
- **Giving into a store** stays `give` (to a person, a household or a building). If `leave` becomes the open-ground act, `leave`
  into a building is folded into `give`. [built: verbs.py, D2-111]

## Why

- Objects in the open make the world physical: a cache, a dropped load, a gift on a doorstep, a warning left at a boundary, goods
  abandoned by someone too heavy to go on (D4-32), loot left behind after a raid.
- They test the rules of possession and witness: whose is a thing nobody holds, and who saw it put there.

## Open questions

1. Whose is a left object: still the leaver's (a claim others may honour), or anyone's who takes it? [built: things.py, night.py,
   D2-87 (held by nobody; the dead leave everything where they die), D4-89 (goods left at a door stay the house's)]
2. Hiding: can something be left out of sight (buried, under a stone), noticed only by someone looking there? [built: things.py,
   data.py `hidden`, D2-93, D2-111 (giving to a place with the `hidden` modifier), D4-70 (found by a search)]
3. Decay and weather: what spoils or is carried off by animals in the open. [decided: D2-87 (food and bodies spoil faster and rot in
   the open; built: night.py), D2-96 (rot), D2-95 (scavengers later, with wild animals), D4-90 (signs of spoiling by bulk); what
   weather does to things in the open not decided]
4. Markers: boundary stones, signs, offerings: objects whose meaning is what they say, not what they are. [still open (5 Nov):
   built in part as monuments carrying lines (data.py MONUMENTS: a carved post, a standing stone, a cairn; D2-169, D2-170) and a
   grave's cairn (D4-99); boundary stones tied to a claim and offerings not decided; whether the two cairns are one is OPEN L-67]
5. Does `leave` into a building merge with `give` now, or wait for this? [built: verbs.py, D2-111 (`leave` folds into `give`)]

## History

- 23 Oct: flagged by Zach while discussing whether `leave` is the same as `give` ("we could have leave on a parcel, so an object could
  just sit in the world, and will be noticed by anyone and is very high salience").
- 5 Nov: swept (37.4): taken up by things_in_places.md and built: leaving and hiding are giving to a place (D2-111), held by nobody
  except at a door (D2-87, D4-89), noticed by the one rule and by bulk (D2-85, D4-90), tagged (D4-68), found by a search (D4-70),
  graves and cairns on the body (D4-99). Still open: boundary stones and offerings (OPEN L-67 on the cairns), weather in the open.

## Sources

D4-23, D4-32, D4-35, D4-48; cybertron2/engine (remains as a container at a place).
