# 38.36: Memory rewritten each stretch: live tests of the instruction, the budget, and the old way

Session 37.4, 24 Oct 2026. Proposal: docs/cybertron2/proposals/memory_rewrite.md (discussion; built as an option, not the default).
Code: cybertron2/engine/memory.py. Harness: 36_memory_rewrite.py (live model calls on w1's real stretches), scorer:
36_memory_score.py.

## 1. What was tested

Three agents from the Wide Country run w1, days 0 to 23 (8 stretches each), chosen for what happened to them:
- **Lucy** (Fenwick): conceived on day 5, gave birth to Helewise on day 15;
- **Gunnild** (Reed): cleared Fen Meadow into a field over the whole period; her husband Payn went west by an unknown way on day 21;
- **Gilbert** (Ashe, trader): went to the Weald and Wynford, made agreements.

Each stretch is the agent's own conversation as it really was (its day prompts, talk prompts and replies), with the opening's memory
replaced by the memory it has rewritten so far, then the end-of-stretch request. Only the memory calls are new. Rounds:

| Round | Model | Budget (tokens, ceiling) | Instructions |
|---|---|---|---|
| 1 | Sonnet 5.5 | 1,200 (about 900 words when old) | plain, keep_change, most_days, future_self |
| 2 | Sonnet 5.5 | 600 (half) | keep_change, revise, most_days |
| 2 | Haiku 4.5 | 1,200 | keep_change, revise |
| 3 | Sonnet 5.5 (600), Haiku 4.5 (1,200) | | future_days (Zach's: "what might you still want to know") |
| 4 | Haiku 4.5, Sonnet 5.5 (600) | | keep_change, future_days, keep_future, each with "(n more than last time; last time you wrote x of y)" (running) |

The instructions (each followed by `Write it in "memory". Reply with JSON only.`):

| Name | Text |
|---|---|
| plain | Rewrite your memory to carry forward, in at most N words. |
| keep_change | Rewrite your memory in at most N words: keep what still matters, add from these days only what you will want later, and leave the rest. |
| most_days | Rewrite your memory in at most N words. Most days are not worth keeping; some things are. Keep what still matters from before. |
| revise | Rewrite your memory in at most N words: keep what still matters, correct what has changed, and add from these days only what you will want later. |
| future_self | Rewrite your memory in at most N words, for yourself in a season's time: what will you need to know? |
| future_days | What might you still want to know in the days to come? Rewrite your memory with that, in at most N words. |
| keep_future | Rewrite your memory in at most N words: keep what still matters, and add what you might still want to know in the days to come. |

**A caveat that runs through every example:** w1 had an engine bug (now fixed, 17a8cda): a mother was never told she had given
birth. Lucy was only shown "a baby crying in Fenwick House", so in the record she goes on believing she is with child after
Helewise is born. Every memory below inherits that confusion; how each instruction copes with it turned out to be telling.

## 2. The numbers

| Model, budget | Instruction | Words / budget | Churn (how much each rewrite changes) | Names kept from one rewrite to the next | Key events never written / dropped later |
|---|---|---|---|---|---|
| Sonnet, full | plain | 75% | 63% | 83% | 0 / 0 |
| Sonnet, full | keep_change | **62%** | **48%** | 87% | 0 / 0 |
| Sonnet, full | most_days | 64% | 54% | 89% | 0 / 0 |
| Sonnet, full | future_self | 81% | 59% | 85% | 0 / 0 |
| Sonnet, half | keep_change | 93% | 59% | 89% | 0 / 0 |
| Sonnet, half | most_days | 93% | 54% | 89% | 0 / 0 |
| Sonnet, half | revise | 101% | 54% | 88% | 0 / 0 |
| Sonnet, half | future_days | 95% | 66% | 84% | 0 / 0 |
| Haiku, full | keep_change | 67% | 79% | 72% | 0 / pregnancy dropped in 2 of 5 later memories |
| Haiku, full | revise | 67% | 81% | 78% | 0 / pregnancy dropped in 4 of 5 |
| Haiku, full | future_days | 90% | **92%** | **56%** | Payn's trip never written / pregnancy dropped in 1 of 5 |

(Key events: Lucy's pregnancy and the birth, Gunnild's clearing and Payn's trip, Gilbert's travels and agreements. "Names kept":
of the people and places named in one memory, the share still named in the next.)

## 3. The old way (w1, `append` mode, Lucy on Opus 4.7)

Every three days a new memory of at most 150 words; the last six are shown in each opening, beside the engine's own list of marked
events. What Lucy's opening held on day 21 (abridged):

> ## What you remember
> - (her seeded history and customs: 14 lines) ...
> - summer day 6: Jory gave 1 crude tool to Lucy
> - autumn day 1: Richard gave 5 rye to Lucy
>
> ## Your own memory of recent days (written by you)
> - summer day 8 to summer day 8: Summer day 8: harvest started at the Infield, all five of us reaping bare-handed (learned: a
>   crude tool does not help reaping). I brought in 16.4 rye for the Moors — quarter-share deal means ~4.1 rye to the Fenwicks ...
> - autumn day 5 to autumn day 6: Autumn days 5–6: I am with child, my time is near. Avice, Ellen, Roger all told me to rest at
>   the house ... Jory's O1062 open to anyone: 2 timber for 2 rye ... Ellen's O752: 2 timber for 1 bread ...
> - winter day 3 to winter day 4: Winter days 3–4: rested both days by Moor House fire. My time near, no sign yet ... Helewise
>   cared for by Avice/Jory daily; 10 days to grown ...
> - winter day 5 to winter day 7: ... My time near, no sign yet. Helewise now a child, ~7 days to grown ...

What it shows:
- each memory is a dense ledger of that stretch only (offer numbers, store counts), and "my time near, no sign yet" is written
  afresh in four of them: nothing is consolidated;
- the queue drops the oldest whatever it held (her first stretch, the harvest deal's terms, is gone by day 21);
- the engine's own picks are trivia ("Jory gave 1 crude tool to Lucy"), and the birth is not among them.

## 4. Lucy's memory at the end (days 21-23) under each instruction

**Sonnet, keep_change, full budget (811 of 870 words).** The one that worked out what had happened:

> I live in Fenwick House with Roger, Ellen (mother-in-law), Jory (father-in-law) and Helewise, our child (born around winter day
> 2-3, grown by about winter day 14) ...
>
> STATE (spring day 2, fog, snow on ground): I have been resting for many days on the belief that my time was near, with NO sign of
> anything: no twinge, no waters. That belief is probably wrong or stale. Each morning check whether I am fit; if I am fed and fine,
> STOP resting and resume normal work (6 units in spring). Pinned note "Birth plan" is out of date in tone; rewrite or drop it.
> Everyone (Roger, Jory, Ellen, Avice) is waiting on my word ...
>
> Lessons: messages cross, so settle plans early ... Offer syntax: work must be written 'work 2 days' ... Do not waste units
> resting when fit: I left many units unused over several days.

**Sonnet, plain, full budget (978 of 870, cut back).** The same facts, the stale belief kept and contradicted:

> STATUS at spring day 2 (day 24 of these days): fog, snow on the ground. I am WITH CHILD and my time is near, but there is no sign
> yet ... HOUSEHOLD: Helewise, a child of my household, is grown in about 4 days ...

**Sonnet, most_days, half budget (422 of 440).** Tighter and denser, still with child:

> I am Lucy, Fenwick of Stannick, wife of Roger ... Helewise is a child of our household (grown in ~4 days as of spring day 2) ...
> I AM WITH CHILD and my time is near (no sign yet as of spring day 2, day 24 overall). Rest, no travel, no strain ...

**Sonnet, future_days, half budget (474 of 440).** Looks forward, and invents to make the story fit:

> Helewise (my sister's child) is in the Fenwick household ... I am WITH CHILD and my time is near ...
> To learn next: whether the birth goes well, whether Avice renews the grant, whether Richard returns with salt and the copper tool,
> whether the firewood holds, the next sowing, and any chance to learn walling or copper.

(Her sister Helewise married into Ashby; "my sister's child" is a confabulation.)

**Haiku, keep_change (572 of 870).** Headings and narrative; gets the birth, keeps the contradiction:

> **Helewise: Born Winter Day 4, Growing Fast** I conceived trying with Roger on autumn days 1–3. On winter day 4, Helewise came—our
> first child ...
> **Birth and Resting: Spring Day 2, No Sign Yet** Rules: no road, no Gill, no Quarry, no strain, no trying ... No sign of labour yet.

**Haiku, revise (941 of 870, cut back).** Long, and starts to invent the family:

> **Ellen**: Avice's daughter (Fenwick now by marriage to Jory). Capable at quarrying, building, caring for children ...
> **Jory**: Roger's father, Ellen's husband. Seasoned farmer and builder ...

(Ellen is Jory's wife; she is not Avice's daughter. Lucy is.)

**Haiku, future_days (847 of 870).** A planning document in capitals, with worries it made up:

> HELEWISE: 4 DAYS OLD, 6 DAYS TO GROWN — NO SIGN OF BIRTH YET ...
> THE CALF: UNKNOWN STATUS, CRITICAL FOR SURVIVAL
> Moor cow due ~autumn d6-7; calf status unknown. If live calf: milk flows ... If dead or cow died: milk stops, Fenwick starves in
> 4-5 days unless Moor subsidy massive. ASK AVICE ...
> AFTER BIRTH (SPRING D5+, WHEN STRONG): 1. Confirm calf with Avice ... 2. Make/get crude tool ... (10 items)

## 5. Gunnild: an ordinary life, with no single big event

**Sonnet, keep_change.** A standing description updated in place. After days 3-5:

> ## Who/where I am
> Gunnild Reed, at Westmere (the Holm): Reed House (5 beds, hearth, bins), Holm Field (barley, now reaped), the Carr ... Household
> Reeds: Payn (husband/partner, head), daughters Philippa and Tiffany ...
> ## Work in progress
> Clearing Fen Meadow into a new Reed field: about 10 units of work left (my bare-hand clearing is slow, x0.4; a copper tool would
> be x1.5) ...
> ## Lessons
> - Costs: hunt 2 units, fell 2, forage 1, firewood 1, clear 1, reap 1, weed 1 ...

and after days 21-23, the same sections, brought up to date:

> Fen Meadow (grazing, hay; wild food picked bare; clearing now DONE: 0 units left, it is a Reed field ready to sow), the Mere
> (wildfowl, but "hunt" is refused there - don't try again) ... Payn went west on winter day 8 / spring day 1 to look for game
> (camping a night, expected back in ~2 days); result unknown.

**Haiku, future_days.** A diary of the last few days; what was there before is gone. After days 21-23:

> **Winter Days 5–7: The Carr Hunted Out; Fen Meadow Nearly Ready**
> Winter ended as it began: brutal and meat-starved. Over three days I made multiple hunts at the Carr—Payn, Philippa, and Tiffany
> all tried—and caught nothing ...
> **Winter Day 8 and Spring Days 1–2: Fen Meadow Complete; Payn Goes West** ...

**Haiku, keep_change.** In between: it opens with who the Reeds are ("The Reeds have always gone further"), then turns to a
narrative of winter.

## 6. What I take from it

1. **Rewriting works better than the queue for continuity**, on the stronger model: one standing account of who I am, my
   household, my place, what I am working on, deals and lessons, updated in place. Nothing important falls off the end, and the
   engine's trivia list is not needed. The queue's strength (short, dated, hard to corrupt) is also its weakness (nothing is ever
   consolidated, and the oldest goes whatever it was).
2. **The risk of rewriting is that a mistake is copied forward.** Once "I am with child" was in the memory it survived the birth in
   most variants. Only keep_change on Sonnet stepped back and wrote "that belief is probably wrong or stale". The mother is now told
   of the birth, which removes this case; others will arise.
3. **keep_change is the best instruction on Sonnet**: least churn, least padding (it uses about 60% of a generous budget), and the
   one that corrected itself. most_days is close. plain and future_self fill the budget and churn more.
4. **Forward-looking wording (future_days, future_self) makes plans and lists**, "to learn next" and numbered after-birth plans.
   That is useful, but on both models it also brought more rewriting from scratch and more invention (Lucy's "sister's child",
   Haiku's calf crisis). It is good at deciding what matters going forward and poor at keeping what was there.
5. **Haiku rewrites from scratch.** About 80-90% of each memory changes every time. It drifts into a diary of the last few days
   (exactly the "keeping everything from the recent days" to avoid) and loses older things: it dropped Lucy's pregnancy while she
   was still pregnant and never wrote down Payn's journey. Under revise it invented family relations. A weak model may need the old
   queue, a smaller budget, or an instruction that tells it to edit rather than write.
6. **The budget is used up to the limit when tight, about 60-80% when generous.** On Sonnet, halving it did not lose events; it
   squeezed out padding (ledger numbers, long place descriptions). The schedule's shape is right; the ceiling may be lower than 1,200
   tokens.
7. **All instructions hoard mechanics**: store counts, offer IDs, unit costs, "offer syntax". Some of that is genuinely useful to
   an agent; much goes stale within a day.

**Recommendation so far** (before round 4): keep_change; ceiling about 800 tokens; leave it to the agent (no forced events).
Round 4 tests whether stating the growth and the last length ("n more than last time; last time you wrote x of y") makes Haiku edit
rather than rewrite, and whether keep_future (keep_change's keeping with Zach's forward question) gets the planning without the
churn.

*In progress, 24 Oct 2026.*
