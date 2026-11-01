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
  - The places open **evenly across life** (Zach, 1 Nov: "just be constantly spread across their lifespan"), not front-loaded:
    one at coming of age, then one more at equal intervals until the end of the lifespan: `places = 1 + floor((most - 1) * x)`,
    `x` = (days since coming of age) / (days from coming of age to the end of the lifespan). About one more every 5 to 6 days at
    any lifespan.
  - The most a life reaches scales with the lifespan, since a longer life has more stretches to remember:
    `most = round(lifespan / 6)` (calibrate). Across adult life, sampled at each eighth:

    | Lifespan | Places | One more every |
    |---|---|---|
    | 32 | 1, 1, 1, 2, 2, 3, 3, 4, 4 (5 at the end) | 6.5 days |
    | 64 | 1, 2, 3, 4, 5, 6, 7, 9, 10 (11 at the end) | 5.2 days |
    | 96 | 1, 2, 4, 6, 7, 9, 11, 13, 14 (16 at the end) | 5.2 days |
  - **People who start a world already grown** get the number of places for their age, filled first with what the world seeds
    them with (below); the rest stay empty to fill as they go.
- **Seeding** (Zach, 1 Nov: "when a world starts, we should be able to choose which long-term memories that we seed them with";
  "this would replace the current customs"):
  - A world file may give anyone lines kept for good: per person (`kept: [lines]`), and per household or place, as customs are
    given now (`{text, nodes?, households?}`, D4-57). The generator may write them from each person's seeded past (D4-21).
  - **Customs become seeded kept lines.** Today a custom is a fixed sentence in "What you remember", shown every stretch, which
    nobody can let go of (perceive.seed_knowledge). As a kept line it is each holder's own: shown the same way, but it takes a
    place, and the holder may forget it or trade it for something that matters more. So a custom lasts while people keep it, and a
    village's custom is what most there still hold. "What you remember" keeps the seeded history (founders, hard winters, kin
    married away).
  - Seeded lines count against the places for one's age; a world that seeds more than that gives that person as many places as
    its seeded lines.
- **A line:** one sentence, at most about 25 words (cut beyond), in the agent's words.
- **Shown:** under its own heading at every opening, before the memory; and at the end of each stretch, in the memory request,
  numbered, with the empty places shown as empty: "Kept for good (3 of 5 places): 1. ... 2. ... 3. ... 4. (empty) 5. (empty)".
- **Changed only at the memory request**, only by the agent: `keep: [lines]` fills empty places; `forget: [numbers]` empties
  places. Two variants, to be chosen from the test:
  - **replace at once:** an emptied place can be filled in the same reply (or `replace {slot, text}`);
  - **forget now, add later:** an emptied place is free only from the next stretch ("emptied; free from the next stretch"), so a
    line is not swapped out on impulse (Zach's hypothesis, 1 Nov: "so they don't always overwrite").
- **Asked, not optional:** the memory request asks about them every time (optional fields reach few models: 38.38).
- **The wording** (Zach, 1 Nov): the purpose only, never what to keep ("we shouldn't tell them the content"), and one short line on
  letting an old line go for a more important new one. Proposed:

  > Kept for good: what you want to remember for good, a sentence each (at most 25 words), kept word for word whatever you rewrite.
  > When your places are full, you can forget one to keep something that matters more. ("keep": [new lines]; "forget": [numbers];
  > a place you empty can be filled at once.)

  It is asked as its own question after the memory, not as a clause of it. Nothing is put there by the engine.

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
6. Customs as seeded kept lines replace D4-57's mechanism (and the village customs before it, D2-30): to be decided with this
   proposal; then D4-57 is marked replaced. How it meets Zach's redesign of beliefs and values (OPEN L-25): whether a child coming
   of age takes some of its household's kept lines (today a child born in a run gets no customs at all).

## Affects

spec/information/memory.md (D4-61's rule); spec/seeding/populations.md and world files' `customs` (D4-57, D2-30); proposals/
household_customs.md; cybertron2/engine/memory.py, prompt.py (`_memory_sections`), run.py (the memory step), perceive.py
(`seed_knowledge`), generate.py.

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
- 1 Nov 2026: Zach: "it shouldn't be so many more at the start, but just be constantly spread across their lifespan": the places
  open evenly across adult life (linear), not on the memory's front-loaded curve.
- 1 Nov 2026: test finished as far as run (38.39; stopped at Zach's word): with places opening over time, Opus 5.5 fills each new
  place from the latest stretch and uses replacing to correct lines (Lucy's false belief that she was still with child); the
  forget-now-add-later rule stops those corrections (1 change in 32 stretches with places open at once). Leaning: **replace at
  once**. Sonnet 5.5 leaves opened places empty: whether the request should ask outright when a place opens stays open (untested).
- 1 Nov 2026: after reading the test's prompt (38.39: its only guidance was "what you mean to know for years, word for word",
  given as a clause after the memory instruction), Zach: "I don't think we should tell them the content. I think the purpose
  'what you want to remember for good' is important, but I do think we should also say something short about the option to
  forget and trade off more important new memories for older ones." Wording rewritten to that; untested.
- 1 Nov 2026: Zach: a world should choose the kept lines people start with, and "this would replace the current customs". Added
  seeding (per person, household or place; the generator may write them); customs become seeded kept lines each holder may let
  go; grown people start with places for their age, filled first with what is seeded.

## Sources

Review 38.36, 38.38, 38.39; runs/d1_duo; Zach's messages of 31 Oct and 1 Nov.
