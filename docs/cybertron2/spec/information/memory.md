# Memory and reasoning

## Summary

An agent thinks before it answers and sees its own earlier reasoning. Its calls over a stretch of days form one conversation; at
the end of each stretch it writes, in its own words, what it wants to remember, and that is what it carries into the next.

## Decided

- D4-26: native thinking on every call; the agent's earlier replies (plans and stated reasons) stay in its context.
- D4-27: conversation memory, as cybertron 1's history mode: one conversation per stretch of days, restarting at staggered days,
  served by one cached CLI session per stretch.
- D4-28: at the end of each stretch the agent writes its own memory, shown at the start of the next.
- D4-61: the agent rewrites its one memory each stretch, within a length that grows with its age; the engine keeps no list of
  events for it; weak models keep D4-28's queue.

## Mechanics

- **Stretch:** an agent's calls (its morning decision, any talk-step answers, its memory) from the first day of a stretch to the
  last are one conversation. Each agent's stretches start on its own offset of days, so not every agent restarts on one day.
- **Opening** (the first message of a stretch): what it has always remembered (its seeded history), its memory, what it did and
  heard the day before, then the day.
- **Continuing** (every later day): the day only; its earlier days are in the conversation.
- **Its own memory (D4-61):** at the end of the stretch's last day it is told the day's results and the night, shown its memory as
  it stands, and asked: "Rewrite your memory in at most N words: keep what still matters, add from these days only what you will
  want later, and leave the rest." The reply replaces the memory (an empty reply keeps it). A reply more than 15% over N is cut
  back to N at a sentence end. The engine keeps no list of marked events alongside: what is remembered is the agent's choice.
- **Its length** grows with age, fastest when young: N = (lo + (hi - lo) x (1 - e^(-k x age / lifespan)) / (1 - e^(-k))) tokens,
  told in words (0.75 a token).
- **Weak models** (by model id) keep D4-28's rule instead: a new memory of at most 150 words each stretch, the most recent six
  shown, and the engine's list of marked events (deaths, thefts, missed meals, claims, what one was given or taught). A world may
  put every agent on this rule (`memory.mode: append`).
- What it did each day is the engine's record of its acts, kept apart from what it said.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| days in a stretch | 3 (cybertron 1's chunk) | calibrate |
| thinking budget a call | 2000 tokens (cybertron 1) | calibrate |
| memory length: lo, hi, k | 150 tokens, 800 tokens, 3 (about 110 words at birth, 470 grown at lifespan 64, 600 old) | calibrate |
| over the length before it is cut | 15% | calibrate |
| the instruction | as above (review 38.36: keep_change) | decided (D4-61) |
| weak models (the queue) | model ids starting `claude-haiku` | calibrate |
| words in a written memory (queue) | 150 | calibrate |
| written memories kept (queue) | 6 | calibrate |

*Current as of 24 Oct 2026: D4-26, D4-27, D4-28, D4-61.*
