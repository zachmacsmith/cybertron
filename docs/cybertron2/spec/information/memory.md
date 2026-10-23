# Memory and reasoning

## Summary

An agent thinks before it answers and sees its own earlier reasoning. Its calls over a stretch of days form one conversation; at
the end of each stretch it writes, in its own words, what it wants to remember, and that is what it carries into the next.

## Decided

- D4-26: native thinking on every call; the agent's earlier replies (plans and stated reasons) stay in its context.
- D4-27: conversation memory, as cybertron 1's history mode: one conversation per stretch of days, restarting at staggered days,
  served by one cached CLI session per stretch.
- D4-28: at the end of each stretch the agent writes its own memory, shown at the start of the next.

## Mechanics

- **Stretch:** an agent's calls (its morning decision, any talk-step answers, its memory) from the first day of a stretch to the
  last are one conversation. Each agent's stretches start on its own offset of days, so not every agent restarts on one day.
- **Opening** (the first message of a stretch): what it has always remembered (its seeded history), the memories it wrote, what
  it did and heard the day before, then the day.
- **Continuing** (every later day): the day only; its earlier days are in the conversation.
- **Its own memory:** at the end of the stretch's last day it is told the day's results and asked to write what it wants to
  remember; the most recent are kept.
- What it did each day is the engine's record of its acts, kept apart from what it said.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| days in a stretch | 3 (cybertron 1's chunk) | calibrate |
| thinking budget a call | 2000 tokens (cybertron 1) | calibrate |
| words in a written memory | 150 | calibrate |
| written memories kept | 6 | calibrate |

*Current as of 23 Oct 2026: D4-26, D4-27, D4-28.*
