# Roads: stretches, landmarks, crossing and meetings

## Summary

A road (an edge) is one place in the game with parts inside it, as a node has parcels. It has one stretch for each day of its
length and, on some stretches, a landmark: a ford, a bridge, a pass, a narrows, a spring. A road with no landmarks behaves as one
terrain throughout, as before. Travel decides itself most of the time: minor trouble is settled by the traveller's choices at
departure or a default and reported on arrival; serious or complex trouble, and meetings with other people, give a fuse call.
Each end of a road leaves its node from a side and one or more parcels, and some ends are hidden.

Written by 37.2 at Zach's request (23 Oct), from proposals/road_layout.md, road_encounters.md and hidden_ways.md; the area is
37.4's. It extends world/edges.md (D4-8, D4-10, D4-12, D4-47).

## Decided

- D2-104: stretches and landmarks, very simple; no landmarks behaves as one terrain throughout; the edge's terrain is its stretches'
  default.
- D2-105: travel decides itself; choices at departure; a fuse call for serious or complex trouble.
- D2-106: experience lowers the chance of trouble; the call follows the risk as it stands for that traveller.
- D2-107: the first landmarks: ford, bridge, pass, narrows, spring. D2-109: good places on the way change the traveller's state;
  stopping only by choice at departure and only at a known place.
- D2-108: building on landmarks later (OPEN L-5).
- D2-110: meetings on the road: a short conversation, then each party's choice.
- D2-113: travellers can wait out a block.
- D2-90: each road end is tied to a side and parcels, a road or hidden. D2-92: how hidden follows the land. D2-98: hidden ways are
  found by the noticing rule.
- D2-81: travellers get fuse calls (an exception to D4-10).
- D2-120: offers in a meeting go through the same agreement system as at a node. D2-121: where crossing parties meet varies.
- D2-122: every road has a terrain by default; a bare road is only a comparison switch.
- D2-125: `searching` on travel.

## Mechanics

### Stretches (D2-104)

- An edge of n days has **n stretches**, numbered from each end. A traveller leaving at nightfall spends its first night on
  stretch 1 from its end, its second on stretch 2, and arrives at dawn after the last (D4-8).
- Each stretch has a **terrain** (plain, farmland, woodland, marsh, hills, mountain, river valley): the edge's terrain unless the
  world gives that stretch its own. **Every road has a terrain** (D2-122): from the land it crosses, else a farm track; a world can
  make a road bare (no meetings, notices or traces) only as a switch for a comparison arm.
- Things on a road lie on a stretch (world/things_in_places.md): remains, dropped goods, a camp, traces.

### Landmarks (D2-107, D2-109)

A landmark is a data kind, like a parcel's cover: its signs, what crossing it asks, its risks of things (environment/scheduler.md,
D2-71), and its sight and cover (environment/visibility.md). A stretch has 0 to 2; most have none.

| Landmark | Crossing | Risks | Meetings |
|---|---|---|---|
| **ford** | when high: wait, or cross and risk the load | rises with rain and floods; a herd can be swept | near certain (one crossing place) |
| **bridge** | none, unless down | rots, washed out by a flood, can be burned | near certain |
| **pass** | a cold night; shut by snow in deep winter | snow, the cold | near certain |
| **narrows** (a gorge, the deep wood) | none | short sight, deep cover | near certain |
| **spring** | water | (fouled: later) | likely |
| **good places**: a meadow, wild fruit trees, a sheltered hollow | none: they change the traveller's state on arrival (below) | | |

- **Known landmarks:** a traveller who passes a landmark knows it (as a place found, D4-47); it can tell others. The departure
  prompt shows the landmarks the traveller knows on that road.
- **Good places on the way (D2-109):** passing one is a trip with nothing to decide, but the traveller arrives changed: in season,
  fed on the way (that night out costs 1.0 food instead of 1.5) or with 1 to 2 food gathered; twice as likely if it knows the
  place. It may **stop** at one only by choosing so at departure, and only if it knows it: it stays there up to the days it chose,
  gathering as at a wild site and sleeping as in a camp (1.2 food a night, lodging.md).

### Crossing: three tiers (D2-105, D2-106)

| Tier | When | How it is decided | What the traveller learns |
|---|---|---|---|
| nothing | most days on most roads | | its daily notices (information/noticing.md) |
| minor trouble | a high ford, mud, a lame ox, a cold night at the pass | its choice at departure, or the default | on arrival, with what it cost ("the ford was high: you waited a day; 2 grain got wet") |
| serious or complex | a risk of death for that traveller of 0.05 or more; a loss of half the load or herd or more; other people involved; or two challenges at once that its choice does not cover | a fuse call (conflict/fuse_events.md) with the choices the situation offers | in the call |

- Any minor trouble also has a small chance of a call (0.1), so travel is not wholly mechanical.
- **Noticing in time:** trouble gives a call only if the traveller notices it coming (information/noticing.md: sight, the eye for
  the land); unnoticed trouble just happens and is reported on arrival.
- **Experience (D2-106):** each crossing of a landmark lowers that traveller's chance of trouble there (to half after about five
  crossings). Whether a call comes follows the risk as it is for that traveller, so an experienced traveller is woken only when the
  risk stays high even for it (a flood, a blizzard on the pass), which is unusual for it.

**Challenges and their effects:**

| Challenge | When | Default | If crossed anyway |
|---|---|---|---|
| the ford is high | after heavy rain, a wet spell or a flood (environment/scheduler.md) | wait 1 day | a cart or a laden ox: 0.3 chance of losing 0.2 of the load; a herd: 0.05 of the head; on foot: soaked (the cold's fall that night) |
| the bridge is down | a flood took it, it rotted, it was burned | go round by a ford if there is one (+1 day), else turn back | |
| the pass is snowed | deep winter, a cold snap or a blizzard | turn back | each night on the pass in a blizzard: 0.1 chance of death, less with a tent or camp (lodging.md) |

### Choices at departure (D2-105, D2-113)

`travel {to, on trouble, stop at, gather}`, modifiers known to all (agents/modifiers.md):

| Choice | Values |
|---|---|
| `on trouble` | `push on` (cross anyway), `wait up to N days` (then the next choice, default turn back), `turn back`, `go round` |
| `stop at` | a good place it knows, for N days (D2-109) |
| `gather` | gather at good places passed (a little food, no day lost) |
| `meeting` | `stop` (the default: a meeting is a call, D2-110) or `pass by`: a meeting passes on its own, described to both sides (D4-51) |

**Waiting out a block (D2-113):** each day waited is a night out (lodging.md: 1.5 food, 2 in winter, and the cold; less with gear
or a camp); the departure prompt states what N days of waiting would cost in food.

### Meetings (D2-110)

- **Passing by (D4-51):** if either party chose `meeting: pass by` at departure, the meeting passes on its own: no call for anyone,
  no talk or trade; each side is told what it saw in its "On the way" lines (signs.py PASSING: who went by, armed or laden, in fog
  only shapes). Bandits and ambushes will act differently (later).

- **Who meets:** parties going opposite ways on one edge meet on the night they are on the same stretch, or cross between
  stretches; then where they meet is drawn between the two stretches (keyed), three times likelier on one with a landmark (D2-121). Parties going the same way that left the same day already travel together.
- **Chance:** by the stretch: 0.95 at a ford, bridge, pass or narrows; otherwise by terrain: farmland 0.9, river valley 0.8,
  woodland 0.7, marsh 0.6, open plain 0.6 (seen from afar: either can choose to meet or avoid); fog halves it
  (environment/visibility.md).
- **What happens:** a fuse event for both parties (one call each, D2-80). Each sees the other: how many, armed or not, beasts, what
  they visibly carry. Then:
  1. **A short conversation:** up to 3 waves of talk among everyone in both parties, as the talk step at a node
     (information/speech.md); speech costs nothing in transit.
  2. **Giving and offers** during the talk: `give`, `offer` and `accept`, free as at a node (D2-25), through **the same agreement
     system as at a node** (D2-120: spec/economy/agreements.md): legs due now settle from what each carries; promises and payments
     over time stay open and are paid where there is a path (D2-32).
  3. **Each party's choice**, made at once: go on; turn back; change course (travel with the other party, the same way, to its
     destination); attack; flee.
- **Resolution:** an attack is fought on the road as at a node (conflict/combat.md), the other party's choice counting as its
  response (flee: a chance to get away, 0.5, 0.9 mounted; anything else: it defends). Then each party goes on as it chose; a party
  that turned back travels back over the stretches it has covered.

### Where a road leaves a node; hidden ways (D2-90, D2-92, D2-98)

- Each end of an edge is tied to **a side of the node and one or more parcels** (world/parcel_graph.md); those working there are
  near it.
- Each end is a **road** (known to everyone at the node) or **hidden** (known to none, or to those who found it or were told). The
  two ends can differ.
- **How hidden follows the land (D2-92):** a hidden end exists only while its parcel's cover hides it (sight 0.5 or less:
  environment/visibility.md). Use wears it into a path (its own conspicuousness rises by about 0.05 for each party that passes, up to
  a road); unused, it grows back toward hidden where the land regrows (about a season in forest or scrub). If the parcel is opened
  (felled, burned, cleared), the end shows: anyone working or crossing the parcel finds it (conspicuousness 0.8).
- **Finding one (D2-98):** by the noticing rule (information/noticing.md), its own conspicuousness about 0.03 (a game trail) times
  the parcel's sight. The finder learns only that a way leaves there, as an unexplored way (D4-47), and chooses whom to tell.

## Data

Per edge: the two nodes and the days (as before); its terrain; per stretch, a terrain if different and its landmarks with their
state (a ford's level, a bridge up or down, the pass open or shut); per end, its side, parcels and whether hidden, and a hidden end's
use. Per traveller: from, to, the day it left and the day it arrives (as before), its stretch, its departure choices. Per person: the
landmarks it knows and how many times it has crossed each.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| landmarks an edge has | 0 to 2 in all in the first worlds | proposed |
| meeting chance by stretch | above | proposed; calibrate |
| conversation waves in a meeting | up to 3 | proposed; calibrate |
| flight | 0.5; mounted 0.9 | proposed; calibrate |
| the call's thresholds | death risk 0.05; half the load or herd; 0.1 for any minor trouble | proposed; calibrate |
| experience | trouble halved after about 5 crossings | proposed; calibrate |
| a high ford crossed | 0.3 chance of losing 0.2 of a cart's or ox's load; 0.05 of a herd | proposed; calibrate |
| a blizzard on the pass | 0.1 chance of death a night out | proposed; calibrate |
| good places | night out 1.0 food in season, or 1 to 2 food gathered; x2 if known | proposed; calibrate |
| a hidden way | own conspicuousness 0.03; +0.05 a party passing; regrows in about a season | proposed; calibrate |

## What agents see

At departure: the road's days and the landmarks it knows on it, the choices, and what waiting would cost. In transit: nothing,
unless a fuse call. On arrival: "On the way: ..." (information/noticing.md) and what trouble cost. In a meeting call: the other
party and the conversation.

## Open

- Waiting on a road for camps, tolls, patrols and ambushes: later (OPEN L-7).
- Herds wandering onto roads, and searching for them: later (OPEN L-8).
- Building on landmarks: later (OPEN L-5).
- Searching: `travel {to, searching: <herd or person>}` (D2-125): attention x5 for that herd or person on each stretch passed
  (information/noticing.md); the searcher may turn back at any point by its departure choice.

## Sources

[proposals/road_layout.md](../../proposals/road_layout.md), [road_encounters.md](../../proposals/road_encounters.md),
[hidden_ways.md](../../proposals/hidden_ways.md), [journeys.md](../../proposals/journeys.md); world/edges.md.

*Current as of 24 Oct 2026: D2-81, D2-90, D2-92, D2-98, D2-104 to D2-110, D2-113, D2-120 to D2-122, D2-125, D4-51.*
