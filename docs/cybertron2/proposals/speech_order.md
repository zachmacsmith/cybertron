# When people talk, and what it costs: by reach, with an evening at the hearth

**Status:** discussion
**Owner:** 37.4

## Summary

Price speech by how far it carries rather than by kind. Words to those beside you, in the same building or on the same parcel, are
free. Words to everyone at the place cost a unit. A private word needs the other person to be at the same place. Move the main
talk from the morning re-plan to an evening round at the hearth, where housemates hear each other once. The morning keeps one
short wave for answers.

## The proposal

1. **Reach sets the price:**

   | Speech | Who hears | Cost |
   |---|---|---|
   | to those beside you (one building, or the parcel where you work that day) | everyone there | free |
   | to everyone at the place (the node) | everyone at the node | 1 unit (calling round, gathering them) |
   | a private word (tell) | one person at the same node | free, capped per day as now |

2. **An evening round at the hearth:** after the day's work, everyone sleeping in one building is asked once, together, with what
   each said that day and what happened. Each may speak to the house, tell one person, and set an intention for tomorrow. The
   framing is not "plan your day". What is said reaches the next morning's message.
3. **The morning keeps one wave** (today two): enough to answer a tell; most of today's second waves are confirmations ("Yes,
   Father").
4. **Option, to test:** merge the evening into the decision, so the household plans tomorrow at the hearth tonight (one call a
   person a day, as now). Dawn's news (weather, what happened in the night) then reaches the plan a day late.

## Why

Zach (2 Nov): "what are the orders of speech times ... Maybe speech to everyone in a building should be free, but talking to
everyone in the town costs an action?"

Evidence:
- c3_combe_rich: 602 messages in 80 days, 97% private tells, almost all planning; 20 things said aloud (each costs a unit). Talk
  calls outnumber decisions: 382 re-asks on 251 decisions (60% of calls), mostly confirmations. Nothing is said in the evening,
  at meals or at work. The only grief beyond the day of the death came when the engine's weeping sign prompted it.
- cybertron2 measured: a unit per say "all but ended public speech" (DM share 0.96; review 38_space_engine/14).
- cybertron 1: channels lost to DMs on cost, speed and binding force (review 31_institutions/04); talk took 35-70% of actions in
  institutional worlds (review 26); long runs fell silent (36c); 72% of one run's cost was cache writes of DM-reply calls never
  read (review 20).

## Alternatives considered

- **All speech free.** The cost moves to API calls. Cybertron 1's talk-heavy worlds spent most of their actions on talk.
- **As now.** Private planning only, nothing said in common, and the most calls spent on confirmations.
- **Building speech free, town speech a unit, morning only** (Zach's first form). Cheap; keeps talk a planning step.

## Open questions

1. Whether the evening is a separate call or the decision itself (point 4).
2. Whether talk while working beside someone counts as "beside you" (same parcel, same day).
3. What to measure: share of talk that is not work; calls per agent-day; DM share; coordination failures (the harvest
   overshoot); whether households talk about aims, kin and the dead.

## Affects

run.py (talk step, waves), prompt.py (talk prompts), data.py (say_units), converse.py (the cached conversation), spec
information/prompts.md.

## History

- 2 Nov 2026: proposed (37.4) after Zach asked about the order and cost of speech and how it compares with cybertron 1.

## Sources

runs/c3_combe_rich; reviews 38_space_engine/14, 31_institutions/04, 26, 20, 36c; cybertron/runner.py dm_exchange;
cybertron2/engine/run.py talk step.
