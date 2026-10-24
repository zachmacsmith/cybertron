# One noticing rule for every sign and event, each reaching as far as what it is

**Status:** retrospective, accepted: D4-53 (built 24 Oct at Zach's request; written down afterwards)
**Owner:** 37.4 (perception, signs)

## Summary

Every sign and every event is noticed by the one rule (own conspicuousness x visibility x presence x attention x the eye). How far each
reaches depends on what it is: the whole node, a parcel, a building, a stretch of road or the whole road.

## The proposal

- The older sign bundles (crops, fields, pastures, wild land, herds, buildings, people, the sky) and events, which were read by
  salience x relevance wherever one was, go through the rule like things, strays, gates and carcasses.
- Each sign carries its spot: a parcel; a building's parcel with its residents always present; a person's parcel (where it worked)
  with its household present; the sky open to everyone at the node.
- Each event kind has an extent (data.EVENT_EXTENT): the node (a death, a fire, an alarm, a fight, a threat, a raid, arrivals,
  departures, a household joined, a claim or grant), a building (stored, left, made, hosted, built), else the parcel it names or where
  its actor was.
- Relevance (one's concerns, interests, hunger) orders what one has noticed; it no longer decides whether one notices. What concerns
  one still comes as "what concerned you".

## Why

- c6 showed a trampled field to 15 of 18 villagers wherever they were: the rows had been put in the crop bundle, read by the old
  salience formula. Zach: "every sign should follow the same rules. Why would you ever build one that doesn't?" Only the rows written
  for Packages A to C used the rule; the older bundles predated it.
- Zach: "do events not have locations as well?" They had a node or road (D4-35) and usually a parcel or building in their subjects, but
  perception ignored it. "A location could span maybe a whole node, or just a single parcel, or an edge, or just a portion of an edge,
  it depends on what it is."

## Alternatives considered

- Leave the older bundles on salience x relevance: what one notices then does not depend on where one was.
- An extent per row rather than per bundle and event kind: finer, more data; later if a row needs it.

## Open questions

- Sound carries further than sight: a fight heard from the next parcel. The extent table puts loud events on the node; a sound reach
  by parcel distance would be finer.
- Speech stays with the talk step (information/speech.md).

## Affects

spec/information/noticing.md (written: D4-53); perception.py, signs.py, data.EVENT_EXTENT.

## History

- 24 Oct: after c6, Zach asked why any sign does not follow the rule, and whether events have locations, with their extents; built
  that day (signs.facts gives every bundle a spot; perceive reads events by the rule with an extent; things.spot_chance takes those
  inside and the whole node), written down here afterwards: retrospective, accepted D4-53.

## Sources

Conversation, 24 Oct; review 38.25.
