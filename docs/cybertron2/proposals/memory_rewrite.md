# Memory rewritten, its length set by age

**Status:** accepted: D4-61
**Owner:** 37.4

## Summary

Instead of writing a new memory every stretch of days (the last six kept), an agent rewrites its one memory at the end of each
stretch: it keeps what it still wants from before and adds what it wants from the new days. How long the memory may be is set by
a schedule over its life: it grows with age, fastest when young, levelling off later. The engine keeps nothing on the agent's
behalf; what is remembered, including major events, is the agent's choice.

## The proposal (as built, cybertron2/engine/memory.py)

- `memory.mode: rewrite` in a world file (default `append`, today's rule, D4-28).
- At the end of a stretch the agent is told what it did that day, shown its memory as it stands, and asked, in one short
  instruction, to rewrite it within its budget. The reply replaces the memory; an empty reply keeps the old one.
- The opening of each stretch shows what it has always known (its seeded history and customs, unchanged) and its memory. The
  engine's own list of marked events (`lasting`: deaths, thefts, missed meals, claims...) is not shown in this mode.
- The budget, in tokens: `lo + (hi - lo) * (1 - e^(-k * age / L)) / (1 - e^(-k))`, age in days, L the lifespan. Defaults
  lo 150, hi 1,200, k 3 (calibrate): at lifespan 64, about 110 words at birth, 470 at 12 days (a youth), 670 at 24 (grown), 810
  at 40, 900 at 64. Told to the agent in words (0.75 a token). A memory more than 15% over is cut back at a sentence end.
- Instruction variants compared live (review 38.36): `plain`, `keep_change`, `most_days`, `future_self`.

## Why

Zach (24 Oct): "rather than forming a new memory every 3 days, they rewrite their memory section to include both what was there
previously and if there is anything relevant from the new days ... a scheduler that decides how the token length ... changes over
time. It should increase over their lifespan but with a decreasing [rate] so that it levels off later in their lifespan and the
largest increases are earlier ... what best strikes the balance of remembering new things and not just [keeping] absolutely
everything from the recent days ... always updating if there are major events but this being up to them rather than forced by
the engine".

Today an agent's memory is a queue: after six stretches (18 days) its oldest memory is gone, whatever it was (a birth, a feud), and
the engine adds its own list of marked events beside it.

## Alternatives considered

- Keep the queue and add a summary of the dropped memories (two layers): more text, two places to look.
- Fold the seeded history into the rewritten memory, so an agent may also let go of what it was born knowing: possible later;
  for now customs and kin stay as known facts.
- A token budget fixed for all ages: simpler, but a youth would carry as much as an elder.

## Open questions

- The defaults lo, hi, k and the cut's slack (calibrate from the live tests).
- Whether children (who take no turns) start their memory at coming of age from their childhood lines (now: the childhood lines
  are among what they always remember).

## Affects

spec/information/memory.md (D4-28's rule, if adopted).

## History

- 24 Oct 2026: built as an option at Zach's request, with live tests of four instructions (review 38.36), before integrating.
- 24 Oct 2026: four rounds of live tests (seven instructions, Sonnet 5.5 and Haiku 4.5, 384 calls; review 38.36). Zach proposed
  "what might you still want to know in the days to come" (future_days) and a length note ("n more than last time; last time you
  wrote x of y"); both tested: the forward wording made more rewriting and invention, the note made agents fill the space.
- 24 Oct 2026: accepted (Zach: "you can implement your recommended memory changes"): D4-61. keep_change; the plain length; ceiling
  800 tokens; rewrite the default; Haiku models keep the queue (they rewrite from scratch and drop what matters).

## Sources

Zach's message of 24 Oct; cybertron2/engine/memory.py; docs/review/38_space_engine/36_memory_rewrite.py.
