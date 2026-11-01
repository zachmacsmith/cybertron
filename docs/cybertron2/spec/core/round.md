# The round

## Summary

A round is a day. Everyone at a node decides at once; only the talk step asks anyone again. Travel ends a day, and the traveller
decides at the place it arrives.

## Decided

- D4-13: a round is a day; the calendar is compressed (environment/calendar.md).
- D4-14: everyone plans at once (cybertron 1's simultaneous mode); only the talk step asks anyone again.
- D4-15, D4-25: speech is not a round late; the talk step comes before work, among the people at the node (information/speech.md).
- D4-8: travel is the last act of a day; the traveller arrives at the start of a later round, sees the place and decides there.
- D4-28: at the end of each stretch of days an agent writes its own memory (information/memory.md).
- D2-80 to D2-84: the night begins with the fuse sub-step: events with a fuse, detected or not, and one urgent call for the woken
  (conflict/fuse_events.md).

## Mechanics

| Step | What happens |
|---|---|
| dawn | travellers whose journey ends today arrive (D4-8); the scheduler's incidents and signs for the day (environment/scheduler.md) |
| decide | every agent at a node is asked once, all at the same time (D4-14) |
| talk | the talk step (information/speech.md): messages to one person wake them; up to the waves set there |
| work | the day's acts are carried out; travel is the last act of the day (D4-8) |
| night | first the fuse sub-step (conflict/fuse_events.md: the woken answer in their own conversation, D2-84); then fights, where each sleeps, eating, the cold, deaths, spoilage by condition (economy/goods.md "Decay"), departures onto the roads |
| memory | at the end of a stretch, each agent writes what it wants to remember (D4-28) |

Travellers on a road make no daily decision until they arrive (D4-10); on a road with a terrain they may get one urgent call a day,
for trouble, a meeting or a find (D2-81, world/roads.md). Departures happen at nightfall before the roads' night and the fuse
sub-step, so those leaving are on their first stretch.

### With an evening (`evening: true`)

| Step | What happens |
|---|---|
| dawn | as above; a traveller who set off at nightfall comes in with half the day's units (D4-67) |
| decide, talk | as above, with one wave of answers (D4-65) |
| work | as above; one who sets off in the morning does so as the day's first act and walks the day (D4-67); those whose road ends today come in by nightfall |
| evening | the evening at the hearth (information/speech.md, D4-65): one call each, then one wave for those asked something. Its acts (D4-66): sleep, host (the guest sleeps there), grant, revoke, admit, join, leave, found, partner, part, try (with units kept back), fire, set the door, accept, withdraw, release, give, move, name, claim, order, rest, travel at nightfall; anything else is refused ("the day's work is done") |
| settle, night, memory | as above; what was shown at the evening is not repeated in the next morning's record of the day |


## Parameters

| Parameter | Value | Status |
|---|---|---|
| days a run | a world setting | decided (world file) |

## Open

- The order within work (interleaved or in turn) and the settlement of agreements at its end: 38.17 §6 (engine reference).

## Sources

38.05 §1; 38.17 §6.

*Current as of 2 Nov 2026: D4-8, D4-13, D4-14, D4-15, D4-25, D4-28, D2-80 to D2-84, D4-65 to D4-67.*
