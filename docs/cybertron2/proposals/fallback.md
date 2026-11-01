# A fallback each person sets

**Status:** retrospective, accepted: D4-76 (2 Nov)
**Owner:** 37.4

## Summary

Besides the day's plan, a reply may give `fallback` acts. Units left over when the plan is done go to them, in order and again, until
the units are used or none can be done.

## The proposal

As summarised; rule in spec agents/actions.md.

## Why

In c3 the largest single cause of refusals was the harvest overshoot: several people each planned four reaps of a field that ran
out by midday, and the units were lost. The agents wrote their fallback into their reasons ("firewood is my fallback"), but the engine
had no way to act on it. Zach (2 Nov): "the fallback option (they should be able to set it themselves)".

## Alternatives considered

- **An engine default** (gather firewood, rest): the engine would be choosing for the agent.
- **Per-act alternatives** ("reap, or else hay"): more precise, more to write; a plan-level list covers the cases seen.

## Open questions

1. Whether per-act alternatives are wanted later.

## Affects

run.py (the work step), prompt.py (schema, reply lines); spec agents/actions.md.

## History

- 2 Nov 2026: built at Zach's request; written down after (retrospective).

## Sources

runs/c3_combe_rich; review 38.41; review 38.42.
