# Proposal: the layout of a road (stretches and landmarks)

**Status:** partly accepted: D2-104, D2-105 (23 Oct); landmarks first, building on them, waiting and the escalation rule open. Design only. **Owner:** 37.2 (author); edges, places and travel
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

### 3. Crossing challenges decided by what is there (D2-105)

Travel decides itself most of the time; decisions are needed only where something complex emerges. Three tiers:

| Tier | When | How it is decided | What the traveller learns |
|---|---|---|---|
| **nothing** | most days on most roads | | journeys.md's notices |
| **minor trouble** | a high ford, mud, a lame ox, a cold night at the pass | by the traveller's choice at departure, or the default | on arrival, with what it cost ("the ford was high: you waited a day; 2 grain got wet") |
| **serious or complex** | proposed: a risk of death above about 5%, a loss of more than half the load or herd, other people involved (a meeting, a party camped at the block), or two challenges at once (the bridge down and the ford in flood) | a **fuse call** (D2-81), with the choices the situation offers; still rare, at most one a day (D2-80) | in the call itself |

Even minor trouble keeps a small chance (proposed 0.1) of a call, so travel is not wholly mechanical.

**Where the line falls between automatic and a call is open (Zach, 23 Oct: not yet sure).** Candidate factors, to explore:

| Side | Factor | Pushes toward a call when |
|---|---|---|
| the event | stakes | a life, most of the load or herd, a large debt at risk |
| | whether the departure choice covers it | the situation is not one the choice names (two challenges at once) |
| | other people | someone else is deciding too (a meeting, a party at the block): their choice cannot be decided in advance |
| the agent | noticing in time | it saw the trouble coming (sight, the eye for the land); unnoticed trouble just happens |
| | experience of that road or landmark | it is new to the agent; a carrier who has forded it ten times handles it as routine |
| | what it carries and who is with it | children, a herd, goods held for others |
| the run | the cap | at most one call a day (D2-80) |

One shape: a call happens when the stakes are high, the departure choice does not cover it, and the agent noticed in time;
experience raises the bar, and other people always lower it.

**Choices at departure:** a short, fixed set given with `travel` (a modifier, D2-93): `on trouble: push on | wait up to N days |
turn back | go round`. The departure prompt shows the landmarks the traveller knows on that road (known by having travelled it or
been told); on an unknown road they meet them as they come.

**Waiting it out (37.2 proposes yes):** a traveller can wait at a block (a flooded ford, a snowed pass) for up to N days, sleeping
out (D4-12: 1.5 food a night, the cold), better with a bedroll, tent or camp (D2-68). It is the same act as road_encounters.md
§4's `wait` on a road, brought forward for this one use. The risk is real: in the region run (38.23) people starved on the road,
so waiting with little food should show in the departure prompt as a cost.

Defaults when no choice is given:

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

1. ~~Stretches and landmarks~~ decided: D2-104 (very simple; no landmarks behaves as now).
2. Which landmarks in the first worlds (proposed: ford, bridge, pass, narrows, spring)?
3. ~~How challenges are decided~~ decided: D2-105. Open: where the line falls between automatic and a call (§3: the event,
   the agent, or both), and the 0.1 chance.
4. Building on landmarks (a bridge, a hut, a toll) in the first worlds, or later?
5. ~~OPEN Q-17~~ the edge's terrain is its stretches' default (D2-104).
6. Waiting it out at a block, as a departure choice and in a fuse call (§3)?

## History

- 23 Oct: Zach (on whether roads should be in one stretch per day): perhaps landmarks along a road used for events, like a node
  being one thing in the game with parcels; most edges hold little, but a mountain pass, a bridge section and so on, with events
  varying by where on the journey they happen, and the challenges of crossing decided by what is present, as at a node. Written.

- 23 Oct: Zach decided D2-104 (stretches and landmarks, very simple: most of the time a single-terrain edge, but complex events can
  emerge and connect) and D2-105 (minor trouble resolved automatically and reported with what went wrong; choices at departure such
  as "if trouble, turn back" or "keep pushing"; still some chance of a fuse call, and more extreme or complex, interacting situations
  give one with more choices). Asked whether travellers can wait out a block: §3, 37.2 proposes yes.

## Sources

[things_in_places.md](things_in_places.md), [road_encounters.md](road_encounters.md), [journeys.md](journeys.md),
[hidden_ways.md](hidden_ways.md), [layout.md](layout.md), [gates.md](gates.md), [environment.md](environment.md) §11-12,
[environment_state.md](environment_state.md); D2-9, D2-51, D2-69, D2-71, D2-72, D4-10, D4-12; OPEN Q-17.
