# Passing by on the road: choosing at departure not to stop for others

**Status:** retrospective, accepted: D4-51 (built 24 Oct at Zach's request; written down afterwards)
**Owner:** 37.4 (roads, fuse calls)

## Summary

A traveller can choose at departure not to stop for others (`travel {meeting: pass by}`). A meeting on the road then passes on its
own: no urgent call for anyone, no talk or trade; each side is told what it saw. Bandits and ambushes will act differently, later.

## The proposal

- `meeting` is a travel modifier with values `stop` (the default: a meeting is a call, D2-110) and `pass by`.
- If either party chose `pass by`, the meeting is not a call; each side gets one or two lines in "On the way" from signs.py PASSING
  (who went by, armed or laden, a cart; in fog only shapes; whether the other called a greeting).

## Why

- Zach: "when deciding ahead of time when they set off they can also decide if they do not want to stop and talk to others ... which
  means any interactions will pass on automatically with appropriate descriptions." A traveller in a hurry, or wary, should not be
  forced into a conversation, and every meeting being a call made travel costly in calls.

## Alternatives considered

- Every meeting a call for both (D2-110 as first built).
- Deciding in the call (costs a call anyway).

## Open questions

- Bandits and ambushes: a party set on meeting others will not let them pass (later; OPEN L-22).

## Affects

spec/world/roads.md (written: D4-51), agents/modifiers.md.

## History

- 24 Oct: asked by Zach; built that day (roads.py `passes`, `pass_by`; signs.py PASSING; data.py the `meeting` modifier); D4-51;
  written down here afterwards as a retrospective proposal.

## Sources

Conversation, 24 Oct; review 38.24 §5.
