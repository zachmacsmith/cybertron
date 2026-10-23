# Proposal: the layout of a road (stretches and landmarks)

**Status:** discussion (23 Oct; Zach: "let's explore this next"). Design only. **Owner:** 37.2 (author); edges, places and travel
are 37.4's (world/edges.md, layout.md, place.md), so this goes to them. **Affects:** spec/world/edges.md, generation.md;
spec/environment/ (risks of things on roads); road_encounters.md, journeys.md, things_in_places.md, hidden_ways.md; OPEN Q-17
(edge terrain), which this would replace.

## Summary

A node is one place in the game with parcels inside it. A road could be the same: **one edge, made of stretches, with a few
landmarks** where things happen: a pass, a bridge, a ford, a narrows in the wood, a spring, a ruin. Most stretches hold nothing
and cost nothing. The landmarks decide what can happen on the way, as a node's contents decide what can happen there: a ford can
rise, a bridge wash out, a pass snow shut, a narrows hide an ambush. Meetings, finds, bodies, camps and ambushes happen **at a
place on the road**, not just "on the edge". People can build on roads (a bridge over the ford, a hut at the pass, a toll at the
bridge), which makes roads places to invest in and to hold.

## The proposal

### 1. Stretches and landmarks

- An edge of n days has **n stretches**, one for each day (a traveller sleeps on one stretch each night). Each stretch has a
  **terrain** (plain, farmland, woodland, marsh, hills, mountain, river valley) and **0 to 2 landmarks**.
- A **landmark** is a kind, as data, like a parcel's cover or a building: its signs (D4-48), what crossing it asks, its risks of
  things (D2-71), its sight and cover, and what can be built on it.

| Landmark | Crossing | Risks, by layer (D2-69) | Sight and cover | Meetings | Can be built |
|---|---|---|---|---|---|
| **a ford** | a delay or a risk when high: wait a day, or cross and risk goods, beasts, a cart | rises with rain and floods; a herd can be swept | open | likely: everyone crosses at the one place | a bridge (stone or timber), a ferry |
| **a bridge** | none, unless broken | timber rots, floods wash it out, it can be burned | open | near certain | a toll (a gate on the road: gates.md), repairs |
| **a pass** | a cold night (the cold's fall, D4-12); shut by snow in deep winter | snow, rockfall, the cold | long sight up to it, short in it | near certain | a hut or shelter, a cairn, a beacon |
| **a narrows** (a gorge, the deep wood) | none | a place to lie in wait | short sight, deep cover | near certain, and the waiter sees first | a watch post |
| **a causeway** (over marsh) | slow with a cart; lost in a flood | flood, sinking | open | likely | repairs |
| **a spring or well** | water and a place to stop | fouled by a body or a midden (environment_state.md) | | likely: travellers stop there | a camp (D2-68), a waystation or inn |
| **a ruin, an old camp** | shelter for a night | | cover | possible | |
| **an overlook** | none | | sees far along the road: parties ahead and behind | | a beacon |

- A stretch with no landmark is plain road: travellers pass, meet by the terrain's odds, and nothing else happens.

### 2. What happens where

- **Meetings** (road_encounters.md): parties going opposite ways meet on the stretch where they cross; odds from that stretch's
  terrain and landmark (a bridge or narrows near certain; open plain lower, but seen from afar), instead of one number per edge.
- **Things at a spot** (things_in_places.md): a body, a dropped load, a camp, a cache lie on a stretch, at a landmark or not; a
  spring or a ford is where travellers stop and look, so things there are noticed more.
- **Ambushes** (later): a party waiting picks a landmark; a narrows lets it see first, an overlook lets travellers see it.
- **The environment** (scheduler.md): incidents attach to landmarks as to things at a node: rain raises the ford, a flood takes
  the bridge, snow shuts the pass. A fire runs along a wooded stretch (D2-72).
- **Journeys** (journeys.md): a traveller's notices come from what the stretches hold ("the river is high at the ford"; "the
  bridge at Alder Beck is down").

### 3. Crossing challenges decided by what is there

How a traveller in transit (who makes no call, D4-10) meets a challenge: proposed, a **standing choice given when setting out**
(as burn orders are given before a raid, D2-51), with a sensible default:

| Challenge | Default | Other choices at departure |
|---|---|---|
| the ford is high | wait a day (and eat, sleep out) | cross anyway; turn back |
| the bridge is down | go round by the ford, if there is one (a day more) | turn back |
| the pass is snowed | turn back | wait for it to clear; try it (the cold, a chance of death) |

The risk of crossing anyway falls on what is carried: a cart or a laden ox at a high ford risks losing part of the load (proposed
0.2 of the load), a herd risks beasts (0.05 a head), a person on foot risks a soaking (the cold that night).

### 4. Making and holding roads

Bridges, ferries, huts at a pass, wells, waystations and tolls are buildings on a landmark (D2-9), built with the same parts and
work, and upkept. A bridge turns a ford's risk and delay into none, so it is worth building on a busy road; a toll at a bridge
makes it a chokepoint (scenario_design.md: leverage from chokepoints). Whoever holds the bridge, or burns it, controls the road.

### 5. Seeding

Generation (generation.md) gives each edge its stretches from the land it crosses: a mountain edge has a pass; an edge along or
across a river a ford or a bridge; a forest edge a narrows; a long plain edge a spring. Most edges in the first worlds have 0 to 2
landmarks in all.

## Why

- It mirrors the node: one place in the game, with parts inside it where things happen, and contents that decide what can happen.
- It gives events on the road a place, so meetings, finds and ambushes depend on where, and the environment has something to act on.
- It turns roads into things worth building and holding (bridges, tolls, huts), which the economy otherwise lacks.

## Alternatives considered

- **One number per edge** (road_encounters.md's terrain table, OPEN Q-17): simple, but nothing on the road has a place, and no
  challenge depends on what is there.
- **Waypoint nodes for every landmark** (D4-10 allows real waypoints): a pass as a node gives full turns there, at the cost of a
  call each day; kept for places that deserve it (a town at a bridge), not every ford.

## Open questions (for Zach, and 37.4)

1. Stretches with a terrain and a few landmarks, as data kinds like parcels?
2. Which landmarks in the first worlds (proposed: ford, bridge, pass, narrows, spring)?
3. Crossing challenges met by a standing choice given at departure, with defaults, rather than a call?
4. Building on landmarks (a bridge, a hut, a toll) in the first worlds, or later?
5. Does this replace OPEN Q-17 (edge terrain) as the data 37.4 adds to edges?

## History

- 23 Oct: Zach (on whether roads should be in one stretch per day): perhaps landmarks along a road used for events, like a node
  being one thing in the game with parcels; most edges hold little, but a mountain pass, a bridge section and so on, with events
  varying by where on the journey they happen, and the challenges of crossing decided by what is present, as at a node. Written.

## Sources

[things_in_places.md](things_in_places.md), [road_encounters.md](road_encounters.md), [journeys.md](journeys.md),
[hidden_ways.md](hidden_ways.md), [layout.md](layout.md), [gates.md](gates.md), [environment.md](environment.md) §11-12,
[environment_state.md](environment_state.md); D2-9, D2-51, D2-69, D2-71, D2-72, D4-10, D4-12; OPEN Q-17.
