# Prompts

## Summary

An agent's prompt says what it can see and do in world terms: life stages, never ages; the techniques it knows of, never a full
manual; what it carries against what it can carry. It carries no aims for now. The agent thinks before answering, and its calls over
a stretch of days are one conversation (memory.md).

## Decided

- D4-19: prompts name life stages, never ages in years.
- D4-24: agents are shown the actions they know of; the rest they come to know in the world.
- D4-29: no aims in any prompt (agents/aims.md).
- D4-32: the prompt states each good's weight and what the agent carries against what it can carry.
- D4-26, D4-27: native thinking on every call; one conversation per stretch of days (memory.md).
- D2-4, D2-29: no computed absence, no computed price (perception.md).

## Mechanics

- **System prompt:** the world's rules in words, the verbs and how to reply.
- **Turn prompt:** what the agent remembers, the day, where it is and who is there, itself (fed, carrying, its house), what it can
  do today (by the techniques it knows of and the sites and tools at hand), its agreements, and what it was told.
- Everything is in world terms; engine numbers appear only where a person would count (goods, days, units of work).

## Parameters

| Parameter | Value | Status |
|---|---|---|
| prompt budgets by section | the engine's (38.17) | calibrate |

## Open

- Section budgets and order: 38.02, 38.17.

## Sources

38.02; cybertron2/engine/prompt.py; 38.17.

*Current as of 23 Oct 2026: D2-4, D2-29, D4-19, D4-24, D4-26, D4-27, D4-29, D4-32.*
