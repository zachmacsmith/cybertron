# Clearing new ground for fields

**Status:** retrospective, accepted: D4-60
**Owner:** 37.4 (world/holding.md "Plots" says clearing adds plots; farming numbers are 37.2's to tune)

## Summary

`work {what: clear, at: <a meadow, pasture or scrub>}` breaks up turf or grubs out scrub, a unit at a time; when the parcel's work
is done (6 units a unit of size for meadow or pasture, 10 for scrub; a tool helps, bare hands 0.4) the whole parcel is a field,
fallow, ready to be broken and sown. Nobody holding it, it is held by whoever cleared it (or their household), grounds "cleared".
A wood must first be felled to scrub (under 40% of its trees, D2-156), then cleared.

## Why

Zach (24 Oct): "Can they not clear land at all and make new plots? Why does it matter if there is rich land if not plots?" Before
this the only fields were those a world file gave; rich land elsewhere could only be grazed, foraged or felled, so expansion meant
camps and hunting, not farms.

## Alternatives considered

- Package E's clearing (02y item 6) makes built ground (for building), not fields; deferred with E.
- Clearing part of a parcel into a new parcel (a split): parcels are whole in the graph; left for when land is generated.

## Open questions

- The work per unit of size and the new field's fertility (meadow 1.1, pasture 1.0, scrub 0.85): first guesses (calibrate, 37.2).
- Draining wet ground into fields; clearing a wood directly (stumps), not by felling first.

## Affects

world/holding.md "Plots" (claims by clearing); economy/farming (37.2's).

## History

- 24 Oct 2026: built at Zach's request (37.4), with D4-60, before the Wide Country run.
