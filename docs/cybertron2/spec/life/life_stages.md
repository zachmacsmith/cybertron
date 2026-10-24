# Life stages

## Summary

Childhoods are short, counted in days: a few days cared for, a few of menial work without a model call, then a youth as an agent.
Every stage is a share of the world's lifespan. Prompts name life stages, never ages in years. Runs start with people of every age;
there are no time skips. Youth learn faster and keep it longer.

## Decided

- D4-19: short childhoods; prompts name life stages, never ages in years; no time skips; youth learn faster and keep it longer.
- D4-20: one agent, one model, for life; a child's model is chosen when it comes of age.
- D2-139: all time is counted in days: ages, stages, lifespans, the seeded tree.
- D2-153: the lifespan is a world setting that scales every part of a life (amends D4-19's spans to its default).

## Mechanics

`lifespan` (a world setting, default 32) is the days from birth to the start of old age. Each stage is a share of it, in whole days,
at least 1 (the adult span takes up the rounding). A person's stage follows its days since birth (`born`, a day; negative for those
born before the run); a world whose people have no `born` keeps the stages it was given.

| Stage | Share of the lifespan | Days at the default (32) | At 16 | At 64 | Agent |
|---|---|---|---|---|---|
| infant | 1/16 | 2 | 1 | 4 | no; cared for |
| child | 1/8 | 4 | 2 | 8 | no (no model call); menial work by the head's order |
| youth | 3/16 | 6 | 3 | 12 | yes; learns faster, and what it learns decays more slowly |
| adult | 5/8 | 20 | 10 | 40 | yes |
| elder | until death | | | | yes; fewer units (agents/work.md) |

- Prompts say the stage ("a youth", "an elder"), never an age in years (D4-19).
- A run starts with people of every age and family; there are no time skips (D4-19).
- Coming of age, old age and the rest of a life: life/birth_and_death.md.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| lifespan | 32 days, a world setting | decided (D2-153); calibrate |
| stage shares | 1/16, 1/8, 3/16, 5/8 | decided (D2-153) |
| youth's learning multiplier | higher than an adult's | calibrate |

## Sources

38.09 §3b; spec/life/birth_and_death.md.

*Current as of 24 Oct 2026: D4-19, D4-20, D2-139, D2-153.*
