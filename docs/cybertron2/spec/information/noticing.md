# Noticing things at a place, and on the road

## Summary

One rule decides who notices a thing at a spot: goods left or hidden, remains, a herd, a camp, traces, a hidden way's end. It works
through ordinary perception (the daily spontaneous notice, attending, salience: D4-48), from the thing's own conspicuousness, the
place's visibility, where the observer is and what it is doing, its attention, its eye for the land, and fresh traces. Travellers
notice things on the road each day the same way, and remember them on arrival.

Written by 37.2 at Zach's request (23 Oct), from proposals/things_in_places.md, journeys.md and hidden_ways.md; the area is
37.4's. It extends information/perception.md and signs.md.

## Decided

- D2-85: one noticing rule for every thing at a spot, through the daily notice, attending and salience.
- D2-86: a find on the road worth taking gives a fuse call only if noticed at all.
- D2-88: traces left by passers persist, fade, and can be read by later travellers.
- D2-89: signs of slow change on long journeys later (OPEN L-1), as data in the sign registry.
- D2-91: one knack for spotting things, the eye for the land (D4-50), raised by practice.
- D2-97: daily notices on the road, remembered on arrival.
- D2-98: hidden ways are found by this rule (world/roads.md).
- D2-102: a thing's conspicuousness is its own x the place's sight.
- D4-53: every sign and event by this one rule, each reaching as far as what it is.
- D2-115: presence along the way and next door (world/parcel_graph.md).

## Mechanics

### The rule (D2-85, D2-102)

For each person and each thing at a spot where the person is, each day (keyed draw, D2-70):

**chance = the thing's own conspicuousness x the place's visibility for its sense x presence x attention x the eye x traces**,
capped at 1. What is noticed shows through its signs (D4-48).

### Every sign and event, and how far it reaches (D4-53)

- **One rule for all:** every sign (crops, fields, pastures, wild land, herds, buildings, people, the sky, things at a spot) and every
  event is noticed by the rule above; a sign's base chance multiplies it. Nothing is noticed for being merely salient or relevant;
  relevance only orders what one has noticed.
- **Extent:** each kind of sign or event reaches as far as what it is:

  | Extent | Who can notice it | Kinds |
  |---|---|---|
  | the node | everyone at the node (presence 1) | the sky and the weather; a death, a fire, an alarm, a fight, a threat, a raid; arrivals and departures; a household joined, a claim or grant made |
  | a parcel | by presence there (worked, passed, next door, elsewhere) | crops, fields, pastures, wild land, herds; work, a trade, a gift, a theft, a gate opened; a person (where it worked) |
  | a building | those inside (who live there: presence 1), and by presence on its parcel | its signs; goods stored or left there, making, hosting, building |
  | a stretch of road, or the whole road | those on it (world/roads.md) | daily notices, meetings, finds, traces |

- A person's signs reach those of its household at the node as if inside.

| Factor | Values |
|---|---|
| own conspicuousness | the table below |
| visibility | the place's sight (or sound) that day (environment/visibility.md) |
| presence | hunting there 1.0; foraging 0.7; herding 0.5; fixed work in the parcel (felling, farming, building) 0.5; passing through it on the way 0.3; next to where one works 0.1 (things of 0.5 or more); at the node elsewhere 0.05 (things of 0.8 or more); on that stretch of road 1.0 (world/parcel_graph.md, D2-115) |
| attention (perception.md) | none x1; attending to the place x3; attending to it, then working in it (a search) x5 |
| the eye for the land (D4-50, D2-91) | none x0.5; ordinary x1; keen x3; raised by practice at roaming work (hunting, foraging, trapping, scouting) and by finding things |
| traces | fresh tracks or disturbed ground leading to it x2; a party passed lately x5 |

**Own conspicuousness:**

| Thing | Own |
|---|---|
| a body | 0.9 (on built ground in a settlement 1.0) |
| a heap of goods (10 or more) | 0.9 |
| a small pack | 0.4 |
| a herd (also heard) | 0.95 |
| a camp, used lately | 0.7 |
| traces: tracks, ashes, ruts | 0.3, fading (below) |
| a hidden way's end | 0.03, rising with use (world/roads.md) |
| hidden under brush | x0.2 (untaught x0.4) |
| buried | x0.03 (untaught x0.06) |

### Traces (D2-88)

Passers leave traces on the stretch or parcel they pass: tracks (fade in about 3 days; snow lying makes them plain), a camp's
ashes (about 10 days), cart ruts (about a season). A trace's conspicuousness falls as it fades; what it says ("fresh cart ruts going
east"; "tracks of a herd, two days old") is read by the eye for the land.

### On the road (D2-97)

- Each day in transit, the traveller gets a **daily notice** as at home: what on its stretch it notices by the rule above (other
  travellers seen far off, herds, a body, a camp, traces, the land and the weather, landmarks and their state).
- It cannot act on them in transit, except through a fuse call (a meeting, a find worth taking, serious trouble:
  conflict/fuse_events.md).
- **On arrival** its notices open the turn prompt as memories: "On the way: smoke from a camp at the forest's edge; the ford was
  high; a dead ox by the road." Up to 5 lines; a long journey's are summarised.
- A **find worth taking** (goods, a body and what it carried, a herd once herds wander) noticed on the road gives the finder a
  fuse call (D2-86); unnoticed, it stays where it is.

## Data

Per thing at a spot: its own conspicuousness and signs. Per person: its eye for the land and its practice. Per traveller: the day's
notices on the road, held until arrival.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| own conspicuousness, presence, attention, eye, traces | above | proposed; calibrate |
| trace lives | tracks 3 days, ashes 10, ruts a season | proposed; calibrate |
| arrival lines | up to 5 | proposed; calibrate |

## What agents see

Things they notice, as signs in their daily notice ("a pack lies under the hazel at the wood's edge"); on arrival, "On the way:
...". What they found and who saw them take it.

## Open

- Signs of slow change on long journeys (OPEN L-1).
- Smell (OPEN L-3).

## Sources

[proposals/things_in_places.md](../../proposals/things_in_places.md), [journeys.md](../../proposals/journeys.md),
[hidden_ways.md](../../proposals/hidden_ways.md), [visibility.md](../../proposals/visibility.md).

*Current as of 24 Oct 2026: D2-85, D2-86, D2-88, D2-89, D2-91, D2-97, D2-98, D2-102, D2-115, D4-53.*
