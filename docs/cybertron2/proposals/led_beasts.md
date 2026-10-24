# A beast one leads stays with one until let go

**Status:** retrospective, accepted: D4-58
**Owner:** 37.4 (the livestock spec, economy/livestock.md and transport, is 37.2's: posted on the board)

## Summary

A beast led on a road (a pack ox) stays led when its party arrives: with its leader, at the place they came in, carrying for
them, listed under what they have ("Leading: the Merchant's ox"). It does not wander while led. It is let go only when its leader
turns it out (`drive` it to a pasture here), sets off without leading it, or dies; then it is an ordinary herd, known by memory and
noticing (D4-56).

## Why

The region run r1 (38.26): Everard led the Merchants' ox to Ashwood; on arrival the engine turned it out onto a parcel by itself and
his carry fell back to 10; nothing told him, so he decided "the ox stayed behind" and went home without it, and his family searched
for it for ten days. A first fix (4ad63cc) told him by writing it into his memory, a special case. Zach: "Did you fix the ox story
with unnecessarily specific patches or broad, clean sensory additions ..."; and, on the cleaner rule, "If they travel with the ox tho
yeah it should be clear".

## The proposal (as built)

- Arrival (herds.arrive_with): a pack ox keeps `with` its leader at the node, on the end parcel it came in by; an event says it came
  in, led, noticed by the one rule (D4-53). The memory write of 4ad63cc is gone.
- At night a led beast whose leader is with it is held: no splitting, wandering or rejoining its herd. Its leader gone (set off
  without it, dead): let go where it stands.
- Turning out: `drive {thing, to}` of a led beast lets it go there.
- Leading on: `travel {lead}` takes the beast already led, without a new split.
- Capacity: a led ox counts at the node too (60).
- The prompt lists it under "You": what it carries, and how it is let go.

## Alternatives considered

- Keep turning it out on arrival and tell the leader (4ad63cc): a special memory write; the leader still lost the carry without
  choosing to.
- Tie it up as a thing at a spot: needs the things-in-places record for beasts; later, with theft of beasts.

## Open questions

- A driven herd (not a pack ox) still spreads onto the node on arrival; whether a drover keeps it led is the same question.
- Handing the lead to another person, and taking a beast left tied and unwatched (theft), are not built.

## Affects

economy/livestock.md "The pack ox" and transport (37.2's).

## History

- 24 Oct 2026: built at Zach's request (37.4), replacing 4ad63cc's memory write; D4-58.

## Sources

Review 38.26 §3-4; the conversation of 24 Oct.
