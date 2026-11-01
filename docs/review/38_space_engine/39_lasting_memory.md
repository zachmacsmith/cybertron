# 38.39: Lines kept for good: a small replay test

Session 37.4, 1 Nov 2026. Proposal: docs/cybertron2/proposals/lasting_memory.md. Harness: 39_lasting_memory.py; results in
39_lasting_memory/ (four JSON files). Stopped at Zach's word ("stop doing more tests"), with Opus 5.5's last test half done.

## What was tested

A **replay**, not a live world: w1's real stretches (days 0 to 23; about 8 stretches each) for Lucy and Jory (Fenwicks; Opus 4.7 in
w1), Gunnild (Reeds; Haiku 5.5) and Gilbert (Ashes; Sonnet 4.5), as in 38.36's harness. Each stretch's conversation is the agent's
own, as recorded; only the end-of-stretch memory request is new and live, and what it writes (the memory, the kept lines) goes into
the next stretch's opening. The days do not change: this shows **what agents choose to keep and how they curate it**, not whether
keeping changes what they do.

Arms, four places each: **none** (the rewritten memory alone, keep_change, D4-61); **replace** (an emptied place can be refilled at
once, or a line replaced); **later** (an emptied place is free only from the next stretch: Zach's hypothesis "so they don't always
overwrite"). Then, after Zach ("they should start with just one"), **places opening over time**: one at first, one more every two
stretches (6 days, close to the proposal's linear schedule of one every 5 to 6 days at lifespan 64). One agent per cell: signals,
not measurements. Models: Sonnet 5.5 (all four agents, both tests), Opus 5.5 (all four with places open at once; Lucy and Jory only
with places opening over time).

## Results

**All four places open at once:**

| | Sonnet 5.5 replace | Sonnet 5.5 later | Opus 5.5 replace | Opus 5.5 later |
|---|---|---|---|---|
| lines added | 6 | 19 | 16 | 17 |
| replaced | 2 | (not allowed) | **17** | (not allowed) |
| forgotten | 0 | 3 | 0 | 1 |
| refused (no place) | 1 | **16** | 0 | 0 |
| agents who kept nothing | 2 of 4 | 0 | 0 | 0 |

- **Places fill in the first one or two stretches and then freeze; the first lines win.** Sonnet under `later` kept trying to add
  without forgetting, after being told lines had found no place (Gilbert re-submitted his four existing lines). Lines turned away
  included "Rose died spring day 1", "Roger is named my heir", "Check a field still has a crop before going to reap it".
- **Opus curates by replacing, and its replacements are corrections, not impulses.** Lucy's line went from "a baby needs one unit
  of care" to "Helewise was born winter day 2; I am not with child" to "I am NOT with child; Helewise was born winter day 2. Any
  'Birth plan' note is false: delete it, work, try": the false belief w1's Lucy actually held (she rested for a birth already past).
  Jory's family line gained "daughter Helewise born winter day 2". Gunnild's lessons sharpened stretch by stretch.
- **`later` stops correction.** Under it Opus changed one line in 32 stretches: to fix a line it would have to give it up for a
  stretch first, and it does not.
- **What is kept:** household aims copied from customs (already shown every stretch), current deals (stale soon), routes and market
  day, and many lessons about the game's controls ("the 'units' field does nothing; repeat the action", "pin only an existing note":
  real learning, and a sign of friction in the interface). Almost no judgments of people.
- **Over 23 days the rewrite alone lost nothing probed** (Sonnet: Rose's death, the heir, the debts, the baby were all in the control
  memory at day 23); everything kept was also in the memory. The horizon is too short to show what kept lines rescue.
- **With places shown, Sonnet's memory got shorter** (median 265 to 308 words against 456 without; Opus 600 against 672): more than
  four lines' worth.

**Places opening over time:**

| | Sonnet 5.5 replace | Sonnet 5.5 later | Opus 5.5 replace (Lucy, Jory) | Opus 5.5 later (Lucy, Jory) |
|---|---|---|---|---|
| lines added | 2 | 9 | 8 | 8 |
| replaced | 0 | | 4 | |
| places filled at the end (of 4 open; Lucy, Jory, Gunnild, Gilbert) | 1, 1, 0, 0 | 1, 3, 4, 1 | 4, 4 | 4, 4 |

- **Opus: the lock-in is gone.** Each new place takes something from the latest stretch: the family's aim, then cheese for winter,
  then tools, then the baby's care. "Hoeing an already-sown field gives nothing"; "A baby needs one care unit daily ... check it
  took". Replacing is again used to correct: Lucy's "Try with Roger every day" became "... unless I am with child", then "I am NOT
  pregnant; Helewise was born winter day 2. Never rest for a birth". Under `later` Lucy reached the same correction by a new line:
  "Read 'You' each morning; if it does not say I am with child, I am not."
- **Sonnet 5.5 leaves the opened places empty**: the line "More places open as you grow older" does not prompt it; four of eight
  runs kept one line all along, two kept none, only Gunnild (later) filled all four. Consistent with 38.38: Sonnet 5.5 does not use optional memory.

## Where kept lines came from, and what was not kept (no new calls; Zach: "if things ended up there, did they originate in days
between remembering, were they in short term memory until being saved, and were there things in short term memory that would have
been better saved?")

- **Tracing by words fails for most lines:** 57% of the 100 lines kept across the four tests are in the agent's own words, distilled
  rather than quoted ("a crude tool quadruples felling"), so their distinctive words never appear in the days; 20% are general
  lessons; 14% copy what they always know (the household's aim from its custom, shown every stretch anyway); 7% match the stretch
  just ended. So the subject of each line was followed by hand (Opus 5.5, places opening over time, Lucy and Jory).
- **Two kinds of line, two routes:**
  - **Lessons distilled from something that recurred for many stretches**, carried in the rewritten memory all along, and saved
    when a place opened: wild food picked bare (in the days of every stretch, in the memory after 7 of 8), the crude tool and
    cheese (every stretch, every memory), hoeing a sown field (days of stretches 1, 2, 4, 7; memory 1 to 6; kept at stretch 5).
  - **Corrections and events, saved at once:** the birth and Lucy's false belief that she was still with child (in the days from
    stretch 5, in the memory from 7, kept at 7 and 8).
- **What the rewritten memory carried for 3 or more rewrites, about people, promises or events, and was never kept** (5 to 11 such
  sentences per run): "Roger is my named heir" (all 8 rewrites, never kept in either growth run); "the Moors are fair and very
  generous" (7); "I owe Denise Rook 1 meat (A21)" (8; kept only with all places open); "I promised to teach Ellen quarrying" (4 to
  6); kin and holdings (8).
- **So the split agents made:** the memory holds facts about their world (kin, holdings, debts, the heir, judgments of people,
  promises), and over these 23 days held them through every rewrite; kept lines hold rules to live by, corrections and lessons,
  many about the game's controls ("write work offers exactly as 'work 2 days'"). By the proposal's stated purpose ("people,
  lessons, promises, what one holds true") the heir, the debt, the promise and the judgment of the Moors belong in kept lines
  as much as the lessons do; the agents left them where they already were. Whether that costs anything shows only over a horizon
  long enough for the rewrite to drop them, which 23 days is not.

## Reading

1. Places opening over time (Zach's direction) fix the first-lines-win problem, for a model that uses them.
2. **Replace at once beats forget-now-add-later:** the replacements are corrections, and the cooldown blocks them; impulsive
   overwriting was not seen.
3. Sonnet 5.5's uptake is the open problem: it would need the request to ask outright when a place opens (not tested, at Zach's
   word).
4. Whether kept lines change behaviour, and what they rescue over long lives, needs a live run, not a replay.

*Current as of 1 Nov 2026.*
