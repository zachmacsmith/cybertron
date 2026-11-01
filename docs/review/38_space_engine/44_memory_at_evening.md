# 38.44: the memory asked at the evening against the memory asked on its own (a targeted test)

Session 37.4, 2 Nov 2026. Zach: "Do a few very small targeted tests (not runs) of memory at evening to make sure there isn't a large
degradation from the previous memory only ask. Especially for haiku (but all models)."

## The test

Seven memory requests recorded in runs/p1_combe_evening (Ivo, Opus 5.5: days 11, 29; Margery, Sonnet 5.5: days 12, 30; Everard,
Haiku 5.5: days 13, 28; Idonea, Haiku 5.5: day 32), each asked again two ways from its recorded conversation (views.context), sent
self-contained (llm.flatten), same system, schema and thinking budget:

- **A, on its own (as before D4-77):** the conversation up to the memory request, which holds that day's evening exchange, then the
  memory request.
- **B, at the evening (D4-77 as built):** the conversation up to that day's evening, then the evening message with the memory request
  after it, in one call.

Haiku cases twice each, the others once: 20 calls. Script and replies: scratchpad memfold.py, memfold_out.jsonl (not kept).

## Results

| Case | A~B | A~A (two A replies) | A~recorded | B~recorded | Evening acts / speech in B |
|---|---|---|---|---|---|
| Ivo d11 (Opus) | 0.63 | | 0.60 | 0.60 | 0 / 0 (recorded: 2 / 1) |
| Ivo d29 (Opus) | 0.61 | | 0.66 | 0.57 | 0 / 0 (2 / 1) |
| Margery d12 (Sonnet) | 0.73 | | 0.69 | 0.72 | 0 / 0 (2 / 1) |
| Margery d30 (Sonnet) | 0.60 | | 0.62 | 0.58 | 0 / 0 (1 / 1) |
| Everard d13 (Haiku) | 0.43 | 0.51 | 0.47 | 0.41 | 0 / 0 (1 / 1) |
| Everard d28 (Haiku) | 0.28 | 0.46 | 0.49 | 0.25 | 0 / 0 (1 / 1, a tell) |
| Idonea d32 (Haiku) | 0.35 | 0.56 | 0.62 | 0.37 | 0 / 0 (1 / 1) |

(Overlap: Jaccard of content words. Lengths were alike: Opus 476-557 words, Sonnet 285-321, Haiku 131-174, in both arms.)

## Reading it

1. **The evening's own business was dropped in every folded call.** All 20 B replies held a memory and nothing else: no night's acts
   (sleep, trying for a child) and no speech, where the recorded evenings of those days all had both. On memory days (every third
   day) the evening would be lost.
2. **The folded memory misses that evening.** It is written before the hearth's talk, so what was agreed there is not in it: Everard's
   lacks "Ivo asked me to clear there tomorrow", Idonea's her next day's task. This shows most in Haiku (overlap with the recorded
   memory 0.25 to 0.41, against 0.47 to 0.62 asked on its own, and below two A replies' overlap with each other); Opus and Sonnet barely
   moved (their memory is a long rewrite in which one evening is a small part).
3. **The saving is small:** one call a person every three days, continuing a cached conversation.

**Decision (D4-80):** the memory is asked in its own call after the night, as before; the fold is kept as a world setting
(`memory_at_evening: true`) for later tests, off by default.

*Current as of 2 Nov 2026.*
