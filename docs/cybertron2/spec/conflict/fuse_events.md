# Fuse events: time to respond

## Summary

Some events take time to finish: a raid on a building, a fire, a meeting on the road, a find on the road worth taking. Whoever
detects one before it finishes gets an urgent call: a short decision, added to its own conversation, with the event's own
choices. Fuse events are rare, and most people are never woken. Without detection the default applies.

Written by 37.2 at Zach's request (23 Oct), from proposals/fuse_events.md; the area is 37.4's.

## Decided

- D2-5: fuse events (rare; only a subset of people woken).
- D2-80: at most one urgent call per agent a night, and one a day on the road.
- D2-81: the events with a fuse in the first worlds, and the fuse's length setting how much the woken can do; travellers get
  these calls (an exception to D4-10); arrivals at a shut gate are not a fuse event (the dawn rule, then the talk step).
- D2-82: overlapping events share one wave, by a simple rule, to review (OPEN Q-19).
- D2-83: riders give a lower chance of any fuse, and a very short one.
- D2-84: the urgent call continues the agent's own conversation.
- D2-86: a find on the road worth taking gives a call only if it is noticed at all.
- D2-110: a meeting on the road is a fuse event with a short conversation (world/roads.md).

## Mechanics

### When

A sub-step of the night (core/round.md): after the day's work and before sleep's effects, events with a fuse are drawn and
resolved in order of their start time, ties by a keyed draw (D2-70).

### Which events (D2-81)

| Event | Detected by | Who can be woken | The event's choices |
|---|---|---|---|
| a raid on a building | **a chance only**: a watcher, a dog, neighbours hearing it, those inside | the watcher, those inside, neighbours who hear | defend, flee, hand over, raise the alarm (wake others), stay put |
| a fire | smoke and light | those inside the burning building, neighbours, a watcher | get out, fight the fire (with water), save goods, wake others |
| a meeting on the road | the parties see each other (world/roads.md) | both parties | a short conversation, then go on, turn back, change course, travel together, attack, flee (world/roads.md) |
| a find on the road worth taking (goods, a body, a herd once herds wander) | noticing (information/noticing.md) | the finder | take what it can carry, drive the herd, bury, mark the spot, go on |
| serious or complex trouble crossing a landmark | noticing in time | the traveller | as world/roads.md §Crossing |

Not a fuse event: arrivals at a shut gate (conflict/defence.md: the gate's rule at dawn, then the keeper and the arrivals talk).

### Detection

Detection is a roll for each person who could detect it, as a sign (D4-48) of the event's sense, through the place's visibility
for that sense (environment/visibility.md): raids are mostly heard; at night sight is almost nothing and sound carries; rain and
wind cover noise.

### The fuse's length: how much the woken can do (D2-81)

Still one call and one wave of decisions; the fuse sets how many acts the call allows.

| Fuse | Acts in the call |
|---|---|
| none (a hut: in before anyone wakes) | no call: the default applies |
| short (a timber house; riders, D2-83) | 1 |
| long (a stone building) | up to 3 (for example: wake the others, take a weapon, go to the door) |

### Rarity and overlaps

- At most one call per agent a night, and one a day on the road (D2-80).
- **Overlaps (D2-82, to review: OPEN Q-19):** every event detected at one node, or one stretch of road, in one night shares one
  wave; each woken agent sees every event it detected and answers once; events resolve by start time, ties by a keyed draw.

### The call (D2-84)

The urgent call is **appended to the agent's own conversation** as it stands (that day's turn and what it carries from the days
before: information/memory.md, D4-27), so the same agent decides. It shows: what the agent sees or hears of the event (its signs),
what it holds, who is with it, how many acts it has, and the event's choices. Its reply is actions only.

### No warning, no call

Undetected events resolve with the default: asleep, those inside defend at half strength (conflict/combat.md); a fire burns until
someone wakes or it is out; an unnoticed find stays where it is.

## Data

Per event kind: its sense, its detection chances, who can be woken, its fuse by structure, its choices and its default. Per call:
the event, the agent, the acts allowed, the reply.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| a raid detected, no watcher or dog | each house within earshot 0.15; those inside a timber house 0.3, a stone one 0.5 | proposed; calibrate |
| with a dog | 0.6 | proposed; calibrate |
| with a watcher (D2-21) | 0.9 | proposed; calibrate |
| riders | detection chances halved; at most 1 act | proposed (D2-83); calibrate |
| a fire: those inside wake | 0.6 (a watcher 0.9); neighbours 0.4 | proposed; calibrate |
| acts by fuse | none 0; short 1; long up to 3 | proposed (D2-81); calibrate |
| calls per agent | 1 a night; 1 a day on the road | decided (D2-80) |

## What agents see

In the call: the event as signs ("a crash at the door below; voices; the dog is barking"), their hands, who is near, "you have
time for 2 things", and the choices. In the next day's turn: what happened, as anyone present saw it.

## Open

- Overlapping events in depth (OPEN Q-19, L-6).
- Fire as an incident needs the scheduler's house fire and wildfire (environment/scheduler.md) or setting fire in a raid
  (proposals/attacks_and_walls.md).

## Sources

[proposals/fuse_events.md](../../proposals/fuse_events.md), [02k §1](../../../review/37_growth/02k_fuses_and_gates.md),
[proposals/road_encounters.md](../../proposals/road_encounters.md).

*Current as of 23 Oct 2026: D2-5, D2-80 to D2-84, D2-86, D2-110.*
