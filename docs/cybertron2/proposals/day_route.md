# A day as a chain of parcels

**Status:** retrospective, accepted: D4-62
**Owner:** 37.4

## Summary

What a person passes through in a day is one chain, in the order of its acts: from where it slept, to each parcel it worked in
turn, to where it ends the day (its bed tonight, or the road's end if it sets off). The chain is kept in the day's record, so the
evening's noticing and the map read the same route.

## The proposal (as built)

- `layout.route(w, name)`: stops are where one slept (one's house's parcel at this node, else the built ground), each worked parcel
  in act order (a building counts as its parcel; a parcel again if one goes back to it), and where one ends the day: the road end's
  parcel if one travels tonight, else the bed one chose (`sleep`), else where one slept. Each leg is a shortest way on the parcel
  graph, ties broken by a keyed draw (D2-70, keyed by the person and the leg).
- `layout.routes` runs at the end of the work step and keeps every acting person's route in `today["route"]` (parcel ids in order).
  It is in each step's checkpoint from then until the next dawn, so the journal holds every day's routes.
- The noticing rule's "passed through" (presence 0.3, D2-115) is the parcels on the route other than those worked; next door
  (0.1) is unchanged.
- `views.frames` gives each person's route with its frame, for the map.

## Why

Zach (24 Oct), on the way it was: "a star from the sleeping place out to each worked parcel ('and back'), not a chain from act to
act in order. It also isn't stored anywhere; it's recomputed when the evening's noticing runs." He asked to "build a path chain the
actions in order, and save this".

## Alternatives considered

- **Keep the star:** simpler, but a day of copse, meadow, copse crosses ground the star never counts, and the map could not draw it.
- **Not storing it** (recompute when needed): replay recomputes it anyway; but the map and analysis would need the layout code of
  the run's own version, and noticing and the map could disagree. One list of parcel ids a person a day is small.
- **A history per person in the world state:** not needed; each day's route is in that day's checkpoints in the journal.

## Open questions

- Whether the time of day matters (acts are in order but untimed; a route has no hours).
- Whether a traveller's last day at a node should end at the road's end only when it sets off at nightfall (as now).

## Affects

spec/world/parcel_graph.md "Sensing along the way" (D2-115's path rule).

## History

- 24 Oct 2026: built at Zach's request (37.4), with D4-62.

## Sources

Zach's message of 24 Oct; cybertron2/engine/layout.py; tests/test_cybertron2_package_c.py.
