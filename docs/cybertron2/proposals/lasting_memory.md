# Kept for good: a few lines an agent keeps word for word

**Status:** discussion
**Owner:** 37.4

## Summary

Beside the memory it rewrites each stretch (D4-61), an agent has a small number of places for lines it means to keep for good: a
sentence each, kept word for word, shown at every opening, never reworded by the engine or by the rewrite. At the end of each
stretch, with the memory request, it is shown its kept lines and how many places it has, and may put a new line into an empty
place or empty a place. Places open over time, starting with one. Whether an emptied place can be refilled at once, or only from the
next stretch, is tested (review 38.39).

## The proposal

- **Places:** **one at first, and more opening over time, scaled by the lifespan** (Zach, 1 Nov). With all places open at once,
  agents fill them in the first one or two stretches and then hardly change them (38.39), so the first lines win.
  - The schedule runs on the share of adult life lived, as the memory's length does (D4-61), so a 32-day and a 96-day life open
    places at the same stages: `places = 1 + round((most - 1) * (1 - e^(-k * x)) / (1 - e^(-k)))`, with `x` = (days since coming of
    age) / (days from coming of age to the end of the lifespan), `k` 3 (the memory's): one place as a youth, the largest rises
    early, levelling off.
  - The most a life reaches also scales with the lifespan, since a longer life has more stretches to remember: about one place a
    stretch's worth of six days, e.g. `most = round(lifespan / 6)`: 5 at lifespan 32, 11 at 64, 16 at 96 (calibrate).
  - **People who start a world already grown** would have several empty places at once (the freeze above). Their places open as
    if from the start of the run: one at first, then one more each stretch until they reach the number for their age. (Or the
    generator fills some from their seeded past; for Zach.)
- **A line:** one sentence, at most about 25 words (cut beyond), in the agent's words.
- **Shown:** under its own heading at every opening, before the memory; and at the end of each stretch, in the memory request,
  numbered, with the empty places shown as empty: "Kept for good (3 of 5 places): 1. ... 2. ... 3. ... 4. (empty) 5. (empty)".
- **Changed only at the memory request**, only by the agent: `keep: [lines]` fills empty places; `forget: [numbers]` empties
  places. Two variants, to be chosen from the test:
  - **replace at once:** an emptied place can be filled in the same reply (or `replace {slot, text}`);
  - **forget now, add later:** an emptied place is free only from the next stretch ("emptied; free from the next stretch"), so a
    line is not swapped out on impulse (Zach's hypothesis, 1 Nov: "so they don't always overwrite").
- **Asked, not optional:** the memory request asks about them every time (optional fields reach few models: 38.38).
- **What it is for**, said once in the request: what one means to know for years: people, lessons, promises, what one holds
  true. Nothing is put there by the engine.

## Why

Zach (1 Nov): "this churns all the time? Would we not want any way for them to write short excerpts that they can see all the time
for longer periods that don't get rewritten?"; then: "when doing the memory they should be shown their current keep for good
memories, how many long term memory slots they have, and the option to write into a new empty slot, or forget an old slot. Maybe
they cannot overwrite a slot, but instead have to forget and then add a new one next time so they don't always overwrite? But idk
that mechanism being useful is a hypothesis." Earlier (31 Oct): long-term memory unlocked over time, with a limit.

Evidence: in d1_duo, 44% of the sentences in rewritten memories are gone from every later rewrite. Most are settled state (a debt
paid, an old store count), rightly dropped; but judgments of people ("Jory took the one tool for himself ... mark his style"),
lessons ("I weeded it unasked, lesson taken") and stances ("keep goodwill" with the Moors) go too. Notes do not serve: they are a
working ledger (77% rewrites; 58% never read back: 38.38).

## Alternatives considered

- **A section of the rewrite kept word for word:** models paraphrase what they rewrite; the churn is the evidence.
- **Notes with a "lasting" flag:** notes are used as ledgers; the flag would fill with stores and plans.
- **The engine's list of marked events** (`lasting`, before D4-61): the engine choosing what one remembers; removed by D4-61.
- **No limit:** the lines would become a second memory, and the prompt would grow without end.

## Open questions

1. Replace at once, or forget now and add later (38.39).
2. How many places, on what curve.
3. Shown at every opening only, or every morning.
4. Whether a line can be told to someone, or passed to a child at coming of age (the upbringing channel of a beliefs and values
   design: Zach's redesign of proposals/beliefs_and_values.md, OPEN L-25).
5. Haiku agents, on the memory queue (D4-61): the same places, or none.

## Affects

spec/information/memory.md (D4-61's rule); cybertron2/engine/memory.py, prompt.py (`_memory_sections`), run.py (the memory step).

## History

- 1 Nov 2026: proposed (37.4) at Zach's request, after 38.38 (how agents used their memory) and the churn count in d1_duo; a small
  live test of the two variants against the rewrite alone is review 38.39.

- 1 Nov 2026: first test (38.39; Sonnet 5.5 and Opus 5.5, four places open from the start): places filled in the first one or two
  stretches and then hardly moved (forgetting and replacing rare); under forget-now-add-later many new lines found no place
  because agents added without forgetting. Zach: "they should definitely open up over time. they should start with just one, and
  then get some more over time". Places now start at one; retested with places opening over time (38.39).
- 1 Nov 2026: Zach: "the number of memories should scale based on lifespan". The schedule now runs on the share of adult life
  lived (as D4-61's memory length), and the most a life reaches scales with the lifespan; people grown at a world's start get their
  places opened one a stretch.

## Sources

Review 38.36, 38.38, 38.39; runs/d1_duo; Zach's messages of 31 Oct and 1 Nov.
