# Proposal: meetings on the road (travellers, lost herds, ambushes)

**Status:** accepted: D2-81, D2-110 (23 Oct); odds by stretch and landmark (D2-104); waiting on a road later (OPEN L-7); searching
with wandering herds (OPEN L-8). Design only. **Owner:** 37.2 (author); travel, transit and combat are 37.4's (world/edges.md,
agents/, conflict/), so this goes to them on the board. **Affects:** world/edges.md, spec/core (the day), agents/actions.md
(`travel` with an aim; `wait` on a road), conflict/ (ambush), economy/money_and_markets.md (offers on the road), livestock.

## Summary

A road is a place (D4-35: everything is at a node or on a road), so **people and beasts on the same edge on the same day can meet**.
A meeting is a **fuse event** (D2-5): each party gets one urgent call, though travellers in transit otherwise make none (D4-10).
They can talk, trade, join up, turn back, attack, flee or pass by. The chance of meeting depends on the edge's terrain and the
weather. The same mechanism covers a traveller coming on a lost herd, a searcher looking for one, and, later, bandits who wait on
a road on purpose to ambush whoever comes.

## The problem it solves

In a test run, families kept passing each other: one left to trade at the other's node just as the other left for the first
(Zach). With no meeting on the road, two parties who both want the same trade can miss each other for days.

## The proposal

### 1. Who can meet

| Case | Meets when | Chance |
|---|---|---|
| **travellers going opposite ways** on one edge | they are on it the same day | by terrain (below) |
| travellers going the same way | they left the same day (they already travel as one party: 38.05 §2) | certain |
| **a traveller and a lost herd** | the herd is on the edge (livestock.md) | about 0.15 a day |
| **a searcher and a lost herd** | the searcher travels with the aim of searching | about 0.5 a day |
| **a traveller and someone waiting on the road** (a camp, a toll, an ambush) | the waiter is on the edge | by terrain and by who sees whom first (§4) |

**Meeting odds by the edge's terrain** (proposed; edges need terrain data: OPEN Q-17):

| Terrain | Chance two parties going opposite ways meet | Why |
|---|---|---|
| a ridge or pass | about 0.95 | one way through |
| a road through farmland | about 0.9 | |
| a river valley | about 0.8 | |
| woodland | about 0.7 | paths branch, sight is short |
| marsh | about 0.6 | ways shift |
| open plain | about 0.6 | many ways across; but seen from afar (they can choose to meet) |

Fog halves it; a party that wants to meet (it knows the other set out) raises it.

### 2. What a meeting is

- **A fuse event for each party:** one urgent call, with what it sees (who, how many, armed or not, what they visibly carry, their
  beasts), then one wave of decisions (fuse_events.md rule 1).
- **The menu:**
  - **talk** (both hear, as at a node);
  - **trade:** offers and acceptances settle on the road as at a node (D2-25), from what each carries;
  - **join:** travel on together, the same way, or one turns back with the other;
  - **give** (news, letters, a lost herd driven along);
  - **attack or flee** (conflict/: the road is the place);
  - **pass by.**
- After the wave, each party continues (or turns back), and the day's travel goes on.

### 3. Lost herds

As livestock.md: coming on a lost herd is a meeting; the finder can drive it along, drive it back or leave it. A **search** is
`travel` along an edge with the aim of finding a named herd (or person): the odds of the meeting rise from about 0.15 to about 0.5 a
day, and a searcher can turn back at any point.

### 4. Waiting on the road (later): camps, tolls and ambushes

- **`wait` on an edge** (a new act): a party stops on a road, at a spot, for days, sleeping out or in a camp (D2-68). It is then on
  the road for everyone passing.
- **Who sees whom first** decides the fuse: a waiting party that chose its spot well (woodland, a ridge's narrows) sees travellers
  first; travellers with a scout, a rider ahead or a watch, or in open country, may see the waiters first.
  - If the **waiters see first**, they can attack before the travellers can choose (an ambush: the travellers get no response
    wave), or hail them (a toll, a trade, a robbery by threat).
  - If the **travellers see first**, they can go round (lose a day), turn back, prepare to fight, or walk on.
- The same act serves a **toll post** (a gate's payment rule on a road, 02k), a **patrol**, a **hermit's hut**, and **bandits**.

## Why

- It fixes a real failure seen in runs (parties passing each other).
- One mechanism (a fuse event at a place on the road) covers trade on the road, lost herds, searches, tolls and ambushes.
- It keeps the cost low: calls only when a meeting happens.

## Alternatives considered

- **No meetings in transit** (D4-10 as it stands): simple, but parties pass each other and roads are empty of incident.
- **Every party on an edge sees every other:** too easy; terrain should matter.

## Open questions (for Zach, and 37.4)

1. Meetings on the road as fuse events, with the odds by terrain above?
2. Trade, talk and joining on the road as at a node?
3. Searching as an aim of `travel`?
4. `wait` on a road for camps, tolls and ambushes (later), with "who sees first" deciding the fuse?

## History

- 23 Oct: Zach: herds lost on the road; people travelling the same road in opposite directions should be able to meet as fuse
  events (in a test, families kept passing each other); later, bandits who hide in wait and attack travellers. Written.

- 23 Oct: Zach decided D2-110: a meeting is a fuse event with a few waves of talk, giving and offers, then each party chooses to
  go on, turn back, change where it is going, travel together, attack or flee. Spec written: spec/world/roads.md §Meetings.

## Sources

[livestock.md](livestock.md), [fuse_events.md](fuse_events.md), [attacks_and_walls.md](attacks_and_walls.md),
[gates.md](gates.md), [exchange_and_money.md](exchange_and_money.md), [environment.md](environment.md) §12 (edges' terrain);
D2-5, D2-25, D2-68, D2-74, D4-10, D4-35; 38.05 §2.
