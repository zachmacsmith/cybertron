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
- D4-64: beside the memory, places for lines kept for good, word for word; kept or let go at the end of each stretch; passed on
  to children with care, each childhood line adding a place; at coming of age the childhood lines and one place more, then places
  open evenly over adult life; customs are such lines, seeded only to those alive when a world starts; a world may fix lines; the
  settings are per run.

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

### Kept for good (D4-64)

- **A line** is one sentence in the person's own words, at most `words` long (cut beyond), kept word for word: neither the engine
  nor the rewrite changes it. Each line has a source: seeded, passed on by a named carer in childhood, or one's own.
- **Shown** at every opening, under "Kept for good", before the memory; and in the memory request, numbered, with the places:
  "Kept for good (3 of 5 places): 1. ... 2. ... 3. ... 4. (empty) 5. (empty)".
- **Changed only at the memory request**, by the person, asked as its own question after the memory:

  > Kept for good: what you want to remember for good, a sentence each (at most 25 words), kept word for word whatever you rewrite.
  > When your places are full, you can forget one to keep something that matters more. ("keep": [new lines]; "drop": [the numbers
  > of lines to forget]; a place you empty can be filled at once.)

  `drop` empties places (fixed lines excepted; the reply's `forget` stays the notes'); `keep` fills empty places in order; a line
  with no empty place is not kept, and the next request says so. When a place has opened since the last request, the request says
  so ("A new place has opened since last time."); beyond that, what to keep is up to them: nothing says what, and the engine puts
  nothing there itself.
- **Places.** At coming of age: one place for each line passed on in childhood (life/birth_and_death.md: care), and one more.
  Then the scheduler opens the rest **evenly over adult life**, from coming of age to the end of the lifespan, up to `most`:
  places = start + floor((most - start) x x), x = (days since coming of age) / (days from coming of age to the end of the
  lifespan), start = childhood lines + 1.
- **People alive when a world starts** have the places for their age by the same rule (start = their seeded lines + 1), filled
  first with their seeded lines (seeding/populations.md); a world that seeds more lines than that gives as many places.
- **Fixed lines**: a seeded line a world marks fixed takes a place and cannot be forgotten.
- **Settings per run** (world file `memory.kept`): `words`, `childhood` (most places childhood lines may add), `most` (a number,
  or per lifespan), `schedule` (evenly, every N days, or none), `fixed`, and `refill` (at once, or only from the next stretch).
  Defaults in Parameters.

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
| kept for good: words a line | 25 | calibrate |
| kept for good: most places childhood can add | 4 | calibrate |
| kept for good: most places in a life | childhood lines + 1 + round(lifespan / 5) (14 at lifespan 64 with no childhood lines) | calibrate |
| kept for good: schedule | evenly over adult life | decided (D4-64) |
| kept for good: an emptied place refilled | at once (a per-run option: only from the next stretch) | decided (D4-64; 38.39) |

*Current as of 1 Nov 2026: D4-26, D4-27, D4-28, D4-61, D4-64.*
