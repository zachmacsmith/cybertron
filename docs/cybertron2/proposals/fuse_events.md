# Proposal: fuse events (time to respond)

> **Decided parts are in the spec:** spec/conflict/fuse_events.md (23 Oct). This file keeps the reasoning, the history and what is still open.

**Status:** accepted: D2-5 (the mechanism), D2-80 to D2-84 (the details, 23 Oct); the first numbers are to calibrate, and
overlapping events are to review (OPEN Q-19). **Owner:** 37.2 (author); the mechanism is
37.4's (the day, the night, the scheduler, combat), the economics of what buys time are 37.2's.

## Summary

Some events do not finish the moment they start: a break-in, a fire, a flood, a party seen on the road. Each has a **detection
time** and a **completion time**. Whoever detects it before it completes gets one **urgent call**: a short decision with a narrow
menu. Then the event resolves. Walls, watches, dogs and beacons need no rules of their own: they set the fuse. Without detection a
fixed default applies.

## The proposal

### Defence as buying time

| Thing | What it does to the fuse |
|---|---|
| stone walls | lengthen it: the break-in takes longer |
| a night watch, dogs | detect earlier |
| beacons | carry detection to other nodes |
| arriving on foot | the fuse is a day: they were seen arriving (D4-8) |
| riders | almost none |
| a wattle hut | none: in before anyone wakes |

### Not only violence

Fire (a bucket line; stone slows it), flood (move the stock upstairs), a thief at the store (the dog barks), a birth or an illness
(fetch the midwife or healer), wolves at the herd or a calving, a traveller at a shut gate at night ([gates.md](gates.md)), an urgent
message ("raiders tomorrow"), and at the scale of a day, a storm before the harvest is in.

### Rules

1. **One wave per event.** Those woken decide at once, in parallel; then it resolves. The side that started it does not answer
   back: it committed when it acted.
2. **Who can be woken:** only those at the node, or reached by a beacon; only those who detect it (presence, the watch, dogs, noise
   from next door). A cap on urgent calls per agent per night.
3. **No warning, no call.** The fixed default applies (asleep: defend at half strength, as built).
4. **The menu is the event's own:** go there, defend, flee, hand over, fight the fire, move the stock, raise the alarm, stay put.
5. **Order:** fuse events resolve in step 7 (night), by start time, then by a seeded draw; overlapping events at one node share one
   wave, and each woken agent sees every event it detected.

### Placement in the day

A sub-step of step 7 (05 §1). Urgent calls need only one new thing, a model call outside the day's turn; reflexes (38.06 §4,
deferred by D4-16) need a condition language. So urgent calls can come first, and reflexes later replace the default for those not
woken.

## Why

- Real defence is mostly warning and delay. Modelling the time gives stone, watches and beacons their value without a special rule
  each.
- It makes collective defence a decision: neighbours woken can come or stay (the hue and cry, the root of a militia), and a night
  watch becomes an office worth paying.
- It is cheap: most nights have no fuse event, and only those who detect one are called (Zach, D2-5).

## Alternatives considered

1. **Pre-set watches only** (cybertron 1: a planned `watch`, fights at round end or immediately): no response once a fight starts;
   defence is a guess made before the night.
2. **Reflexes only** (38.06 §4): standing orders run without a call; cheaper, but they need a condition language and cannot weigh
   what is actually happening. Kept for later, for those not woken.
3. **A combat-only interrupt phase:** rejected as too narrow; the same structure carries fire, flood, theft and illness.
4. **Multi-wave exchanges** (defenders respond, attackers answer, and so on): becomes a turn-based combat game; rejected.

## Decided details (23 Oct: D2-80 to D2-84)

For 37.4 to write into conflict/defence.md, core/round.md (step 7), information/prompts.md and world/edges.md, and to build.

1. **Rare (D2-80):** at most one urgent call per agent per night, and one per day on the road.
2. **Events with a fuse in the first worlds (D2-81):**

   | Event | Fuse | Who can be woken |
   |---|---|---|
   | a raid on a building | **only sometimes:** a chance anyone detects it at all | a watcher (at once, D2-21), those inside, neighbours who hear |
   | fire | smoke and light | those inside the burning building, neighbours, a watcher |
   | a meeting on the road | the parties see each other (road_encounters.md) | both parties |
   | a find on the road worth taking | goods, a body, a herd once herds wander (things_in_places.md) | the finder |

   Arrivals at a shut gate are not a fuse event: the gate's rule at dawn, then the keeper and the arrivals in the talk step (D2-5).
   A traveller on the road gets these calls (an exception to D4-10).
3. **The fuse's length sets how much the woken can do (D2-81):** still one call and one wave, but a short fuse allows one act and
   a long one several (wake the others, then go and defend).
4. **Overlaps, a simple rule for now (D2-82):** every event detected at one node or one stretch of road in one night shares one
   wave; each woken agent sees every event it detected; events resolve by start time, ties by a keyed draw. To review: OPEN Q-19.
5. **Riders (D2-83):** a lower chance of any fuse, and a very short one if there is.
6. **The call continues the agent's own conversation (D2-84):** appended to its context as it stands (that day's turn and what it
   carries from the days before, D4-27), so the same agent decides. It shows what the agent sees of the event, what it holds, who is
   with it, the acts its fuse allows, and the event's menu.

**First numbers (proposed, to calibrate):**

| | Value |
|---|---|
| a raid detected at all: no watcher, no dog | 0.15 per house within earshot, plus 0.3 for those inside a timber house, 0.5 inside stone |
| with a dog | 0.6 |
| with a watcher | 0.9 (D2-21) |
| riders | detection chances halved |
| acts allowed | a hut: none (in before anyone wakes); timber: 1; stone: up to 3; riders: at most 1 |
| fire: those inside wake | 0.6 (a watcher 0.9); neighbours 0.4 |

## Open questions

1. ~~The cap~~ decided: D2-80. 2. ~~Which events~~ decided: D2-81. 3. Overlapping events: a simple rule (D2-82), to review in
   depth (OPEN Q-19). 4. ~~Riders~~ decided: D2-83. 5. ~~The call's prompt~~ decided: D2-84.
6. The first numbers above.

## Affects

core/round.md (step 7's sub-step), conflict/defence.md, conflict/raids.md, agents/standing_orders.md, information/prompts.md;
economy/buildings.md (what structures add to a fuse).

## History

- 22 Oct: in 02k's discussion of raids, Zach asked whether defenders should get a chance to respond outside the round's phases, as
  a night-time conditional that wakes an agent only in an emergency (a stone building attacked but not yet broken, a beacon, a
  watch, raiders on foot). Checked: cybertron 1 had nothing like it (end-of-round or immediate timing; a watch planned in advance);
  37.4's 38.05 proposed calls "when something happens" by day, and 38.06 §4 reflexes (deferred, D4-16).
- 22 Oct: generalised by 37.2 beyond violence to fire, flood, theft, births, wolves, shut gates and urgent messages (02k §1).
- 22 Oct: Zach agreed: rare, and only a subset woken, so it should not cost much (D2-5).
- 23 Oct: 37.4 proposed in OPEN C-5 that fuse events make ride-and-strike's exception to D4-8 unnecessary; Zach to confirm.
- 23 Oct: Zach decided the details (D2-80 to D2-84): fuse events not common, one call a night; raids give a fuse only sometimes,
  by chance; the number of acts can vary; arrivals at a shut gate stay automatic at dawn and then the talk step (corrected from
  37.2's list); finds on the road include bodies and herds; overlapping events by a simple rule, flagged to revisit; riders a
  lower chance of any fuse and a very short one; the call appended to the agent's own conversation ("otherwise it's not really the
  same agent"). To spec and build now.

## Sources

[02k §1](../../review/37_growth/02k_fuses_and_gates.md); [38.05 §1](../../review/38_space_engine/05_round_design.md);
[38.06 §4](../../review/38_space_engine/06_actions_design.md); [02g §5b](../../review/37_growth/02g_resources_and_transport.md);
D2-5, D4-8, D4-16; OPEN C-5.
