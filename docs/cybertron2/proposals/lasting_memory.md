# Kept for good: a few lines an agent keeps word for word

**Status:** ready for a decision (Zach's design of 1 Nov; parameters to calibrate)
**Owner:** 37.4

## Summary

Beside the memory it rewrites each stretch (D4-61), a person has places for lines it wants to remember for good: a sentence each,
kept word for word, shown at every opening, never reworded by the engine or by the rewrite. It starts adult life with a few places,
some already filled: by what the world seeds (this replaces customs) and by what was passed on to it as a child by whoever cared for
it. **Lines passed on in childhood add places** (up to a limit), so more care gives a larger long-term memory. More places open
evenly over adult life. At the end of each stretch it is shown its lines and places and may keep a new line or let one go for
something that matters more. A world may fix some lines so they cannot be let go (what a custom is today). The line length, the
number of places, the schedule and the fixed lines are set per run. Tests: review 38.39.

## The proposal

**Passing on in childhood** (Zach, 1 Nov: "a mother who has a current child to care for is told that when she does the caring
action she can pass on some customs that will become long term memories. The model can then later remove them, but they are their
starting ones. This is an interesting test to see if they pass on traditions, goals etc."):

- Whoever cares for a child (`work {what: care, at: <child>}`; Zach's words: the mother) is told, with the child's care line in
  her morning, that while caring she may pass something on, and what the child holds so far: `pass: [a sentence]` on the care
  action, one a care (calibrate). A line of her own kept lines, a custom, or new words: her choice.
- The child (no model) collects them; **each line passed on in childhood adds a place** (up to a limit, e.g. 4), so a child cared
  for and taught more starts adult life with a larger long-term memory. Past the limit, a new line is refused (the carer is told).
- At coming of age the lines become the youth's kept lines, each with its source ("from my mother"), its own to keep or let go.

**Places:**

- At coming of age: **a few places** (e.g. 3, calibrate), plus those added in childhood. Filled first with the world's seeded lines
  (customs, below) and what was passed on; the rest empty.
- Then **more open evenly across adult life** (Zach: "constantly spread across their lifespan"), up to a most that scales with the
  lifespan (Zach: "the number of memories should scale based on lifespan"); more than before (Zach: "we should increase the number
  people have"): e.g. `most = start + childhood + round(lifespan / 5)` (calibrate), one more every 4 to 5 days.
- **People grown at a world's start** get the places for their age, filled first with what the world seeds them with.

**Seeding and customs** (Zach: "when a world starts, we should be able to choose which long-term memories that we seed them with";
"this would replace the current customs"):

- A world file gives lines per person (`kept: [lines]`), per household or per place (as customs are given now: `{text, nodes?,
  households?}`, D4-57); the generator may write them from each person's seeded past (D4-21).
- **Customs become seeded kept lines**, each holder's own: shown the same way as now, but taking a place, and the holder may let
  one go. A custom lasts while people keep it and pass it on; a village's custom is what most there still hold. "What you
  remember" keeps the seeded history (founders, hard winters, kin married away).
- **Fixed lines** (Zach: "a world setting that fixes some of the memory slots (which is the same as having them as a custom)"): a
  world may mark seeded lines fixed; they take a place and cannot be forgotten. That is today's custom, kept for experiments that
  need it to hold.

**Set per run** (Zach: "the specific slot lengths, the number and discovery schedule should be configurable per run"), in the
world file's `memory.kept`:

| Setting | Meaning | Proposed default |
|---|---|---|
| `words` | the length of a line | 25 |
| `start` | places at coming of age, before childhood's | 3 |
| `childhood` | most places added by lines passed on in childhood | 4 |
| `pass_per_care` | lines that may be passed on with one care | 1 |
| `most` | most places in a life (a number, or per lifespan) | start + childhood + lifespan / 5 |
| `schedule` | how adult places open: evenly to `most`, every N days, or none | evenly |
| `fixed` | seeded lines that cannot be forgotten (per person, household or place) | none |

- **A line:** one sentence, at most about 25 words (cut beyond), in the agent's words.
- **Shown:** under its own heading at every opening, before the memory; and at the end of each stretch, in the memory request,
  numbered, with the empty places shown as empty: "Kept for good (3 of 5 places): 1. ... 2. ... 3. ... 4. (empty) 5. (empty)".
- **Changed at the memory request**, only by the person: `keep: [lines]` fills empty places; `forget: [numbers]` empties places
  (fixed lines excepted). An emptied place can be filled in the same reply (38.39: replacing was used to correct; making it wait
  a stretch stopped corrections). (Forget-now-add-later, Zach's hypothesis, kept as a per-run option if wanted.)
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

1. Who may pass on: the mother only (Zach's words), or whoever gives the care that day (a father, a grandmother, an older sibling).
2. What may be passed: only one's own kept lines (customs carried as they are) or any sentence (traditions reworded, new goals).
3. The defaults in the table (calibrate).
4. Shown at every opening only, or every morning.
5. Haiku agents, on the memory queue (D4-61): the same places, or none.
6. Sonnet 5.5 leaves opened places empty (38.39): whether the memory request should ask outright when a place opens.
7. On decision: D4-57 (household customs) and D2-30's village customs marked replaced by seeded kept lines; and how it meets
   Zach's redesign of beliefs and values (OPEN L-25), which this carries (passing on, holding, letting go).

## Affects

spec/information/memory.md (D4-61's rule); spec/seeding/populations.md and world files' `customs` (D4-57, D2-30); proposals/
household_customs.md; cybertron2/engine/memory.py, prompt.py (`_memory_sections`), run.py (the memory step), perceive.py
(`seed_knowledge`), generate.py, life.py (care), verbs.py (`pass` on care); spec/life/birth_and_death.md (care: 37.2's; to agree
on the board).

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
- 1 Nov 2026: Zach's design: passing on through care ("a mother ... when she does the caring action she can pass on some customs
  that will become long term memories. The model can then later remove them, but they are their starting ones. This is an
  interesting test to see if they pass on traditions, goals etc."); more places, a few filled at the start by customs or
  childhood; "those added during childhood actually increase the number of slots (up to a limit) rather than using up, so more
  caring can actually increase the long term memory"; "a world setting that fixes some of the memory slots (which is the same as
  having them as a custom)"; "the specific slot lengths, the number and discovery schedule should be configurable per run".
  Written in; status ready for a decision.

## Sources

Review 38.36, 38.38, 38.39; runs/d1_duo; Zach's messages of 31 Oct and 1 Nov.
