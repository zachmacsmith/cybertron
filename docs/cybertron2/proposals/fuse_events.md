# Proposal: fuse events (time to respond)

**Status:** accepted in principle: D2-5 (the mechanism); its details are discussion. **Owner:** 37.2 (author); the mechanism is
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

## Open questions

1. The cap on urgent calls per agent per night.
2. Which events have a fuse in the first worlds (proposed: raids on stone buildings, fire, arrivals at a shut gate).
3. The order of overlapping events beyond the rule above, and its tie-breaks.
4. OPEN C-5: riders who travel and strike in one round. Proposed: no exception to D4-8; riders simply leave almost no fuse.
5. The urgent call's prompt: what it shows, within the budget.

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

## Sources

[02k §1](../../review/37_growth/02k_fuses_and_gates.md); [38.05 §1](../../review/38_space_engine/05_round_design.md);
[38.06 §4](../../review/38_space_engine/06_actions_design.md); [02g §5b](../../review/37_growth/02g_resources_and_transport.md);
D2-5, D4-8, D4-16; OPEN C-5.
