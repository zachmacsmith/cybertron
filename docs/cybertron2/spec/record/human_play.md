# A human playing as an agent

## Summary

A person can play any agent in a run: they are shown exactly the context the model would be shown, and they answer with the
same reply schema and verbs.

## Decided

- D1-1: a human plays in-world as an agent, with the same context, writing decisions as the same verbs.
- D1-4: as a responder, below.

## Mechanics

- The `human` responder answers one agent's requests. When the runner reaches one, it writes the request, commits what is
  committed, and waits, or exits and is resumed later (execution.md: pause).
- The player is shown `context(agent, key)` (views.md): the same system text, the conversation so far and the new message, and
  nothing else (no map, no other agent's view, no state beyond what the world shows that agent).
- The player answers in the same JSON reply schema. A form may help compose it, but the stored response is that JSON, checked,
  applied and refused as a model's would be.
- A world can mix humans, models and bots per agent. The journal records which responder answered each request.

## Commands

```
python -m cybertron2.engine run SPEC --out RUN --as NAME=human
python -m cybertron2.engine play RUN --as NAME          # answer NAME's pending requests in the terminal
```

## Parameters

| Parameter | Value | Status |
|---|---|---|
| first interface | the terminal; a local web page later, on the same journal | proposed (OPEN Q-RR3) |

## What agents see

Other agents see a human-played agent only through the world, as any agent.

## Open

- OPEN Q-RR3: the first interface (terminal or local page).

## Sources

proposals/run_record.md §5.

*Current as of 24 Oct 2026: D1-1, D1-4.*
