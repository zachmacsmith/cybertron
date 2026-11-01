# Runs that stop before the weekly limit, and play on

**Status:** retrospective, accepted: D4-79 (1 Nov)
**Owner:** 37.4 (the record and execution spec is 37.1's: see OPEN)

## Summary

Before each live day a run checks the subscription's weekly usage window and stops cleanly at a set level (`llm.week_stop` in the
world file, or env CYBERTRON2_WEEK_STOP; default 0.9), writing STOPPED.md; `resume` goes on later. `continue --days N` plays a
finished run on past its world's length, with the journal's spec updated so a later resume plays to the new length.

## The proposal

As summarised. Built in run.py (`_week_stop`, `UsageStop`; `continue`'s `--days`).

## Why

Zach (1 Nov), leaving runs going unattended: "don't go past 40% weekly usage". c1_combe was played on for 40 more days as c2_combe
with `continue --days 80`.

## Alternatives considered

- **A cost cap in dollars:** the binding limit is the subscription's weekly window, which the CLI reports with every call.
- **A new run instead of continuing:** loses the world's state and the agents' conversations.

## Open questions

1. The rule's text belongs in spec record/execution.md (37.1's): OPEN, under 37.1.

## Affects

run.py; tests/test_cybertron2_view.py (the stop); spec record/execution.md (37.1).

## History

- 1 Nov 2026: built at Zach's request; written down after (retrospective), 2 Nov.

## Sources

runs/c1_combe, c2_combe, c3_combe_rich.
