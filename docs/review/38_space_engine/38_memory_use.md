# 38.38: How agents have used their memory: notes, pins, opening, look-ups, stretch memories

Session 37.4, 1 Nov 2026. Zach: "before changing anything, do a deeper analysis comparing how the agents previously used the various
memory mechanisms? Did they use them frequently? In what situations? What for? When?" and "are they read back often? when? when
not?". Nothing changed in the engine. Scripts: the session's scratchpad (`mem/a1.py` to `a7.py`), over every cybertron2 run that
recorded replies, aborted and duplicate runs left out: 35 runs, about 7,500 agent-days, 1,941 note writes, 1,982 stretch
memories. Each run's `turns.jsonl` holds the decision and every talk reply; the memory requests are in `memory.jsonl`.

## The mechanisms, and how each comes back

| Mechanism | Written | Comes back |
|---|---|---|
| the conversation | everything of the current stretch (3 days) | in full on every call of the stretch; gone after |
| stretch memory (D4-28 queue; D4-61 rewrite in d1_duo) | at the end of each stretch, when asked | at every stretch's opening (the queue: the last six, so for 18 days; rewrite: the one memory, for life) |
| notes (up to 8, about 150 words) | any reply, free | **the pinned one in full every morning; the rest by title only**, in full only if opened (a reply asks; it is shown at the talk step, at most 2 a day) |
| look-up | any reply | a craft's full card at the talk step |
| always known | seeded | every opening, for life |

## 1. How often

| Model | Agent-days | Notes written /100 | Pins /100 | Openings /100 | Look-ups /100 |
|---|---|---|---|---|---|
| Haiku 5.5 | 4,011 | 7.6 | 17.6 | 1.1 | 4.0 |
| Opus 5.5 | 1,346 | 81.7 | 47.8 | 0.5 | 4.2 |
| **Sonnet 5.5** | 1,255 | **0** | **0** | **0** | **0** |
| Opus 4.5 | 221 | 17.6 | 0 | 1.4 | 0 |
| Opus 4.7 | 183 | 150.8 | 79.2 | 15.8 | 1.1 |
| Haiku 4.5 | 169 | 15.4 | 8.3 | 3.0 | 0 |
| Sonnet 4.6 | 106 | 178.3 | 158.5 | 3.8 | 7.5 |

- **It is a model trait more than a world one.** Sonnet 5.5 never wrote a note, pinned, opened or looked anything up in 1,255
  agent-days (it uses `attend`, `tell`, `say` and `offers`; its replies are short: median 335 output tokens against Opus 5.5's
  968). Opus 4.7 and Sonnet 4.6 write more than one note a day. Opus 5.5 writes most days; Haiku 5.5 rarely.
- **Concentrated:** of 238 agents who wrote any note, the top 20% wrote 64% of them.
- **The cap binds only for the heavy writers:** 31 refusals "you already keep 8 notes" in all runs, all in w1 and d1_duo (Opus 4.7
  21, Opus 4.5 4).
- **Look-ups are rare, not absent:** 225 in all (3 per 100 agent-days), mostly Haiku 5.5 (159), mostly early in a run: `fell`,
  `copper tool`, `ditch`, `hunt`, `reap`, `bury`. (d1_duo had none; 38.37's "0 of 324" is that run's.)

## 2. What for

One topic a note, by its title first (keyword rules; rough):

| Topic | Share |
|---|---|
| stores, food, fuel, winter | 42% |
| plan, status (general) | 30% |
| debts and deals | 11% |
| journeys and places | 5% |
| crafts, tools, building | 4% |
| fields and harvest | 3% |
| beasts | 2% |
| children, family, birth | 1% |
| threats and wrongs | 0.6% |
| people | 0.6% |

Most common titles: "Plan" (386 writes), "Food" (186), "Winter plan" (122), "Winter needs" (112), "Plans" (106), "Winter prep" (98),
"Owed" (49), "Ockley errands" (45), "Debts" (37).

**Notes are a working ledger, not a long-term memory.** 77% of writes replace an existing title (456 distinct notes, 1,485
rewrites); a title is kept up over a median of 4 days (up to 36). 85% of notes carry quantities of goods; 13% mention a happening
between people. Examples: "Winter day 1, cold: store has 2.5 timber; a cold night burns 2. Food is about 6 meals for Hob and me,
with 5 nights left. I need an axe badly" (Osric, m1_C); "Owe Everard (Merchant, Millford) 1 copper by day 20 (O1354; got 6 bread)"
(Henry, r1). The rare exceptions are lessons and people: "say vs tell: say into Moor House refused for lack of access ... Lesson:
for Moor ears, use 'tell'" (Jory, d1_duo); "neighbours: Moors here. Richard reap deal. Avice knows cheese/milking" (Jory, w1).

**Stretch memories hold more of what happened between people** (37% mention one, against 13% of notes), and nearly all (94%)
also carry quantities: they are where events go, beside the state.

## 3. When written

Share of agent-days with a note written, the note-writing models (6,036 agent-days, base 20%):

| On a day ... | With | Without | |
|---|---|---|---|
| they arrived somewhere new | 35.5% | 19.3% | x1.84 |
| someone spoke to them | 23.2% | 13.2% | x1.76 |
| an agreement or offer was accepted | 26.4% | 18.9% | x1.39 |
| a refusal in their results | 22.6% | 18.0% | x1.25 |
| a cold day | 23.9% | 19.2% | x1.25 |
| the first day of a stretch | 21.4% | 19.4% | x1.11 |
| a death or birth in the run | 12.3% | 22.0% | x0.56 |

By day of run: steady at 19% to 23% through day 19, 14% on days 20 to 39, 1% after day 40 (those late days are mostly h2's
Haiku-heavy households; confounded by model). The pattern: notes are written when something changes the ledger (an arrival, a
deal, talk, the cold), not when something happens to people (births and deaths go with fewer notes).

## 4. Are they read back?

- **The pinned note: yes, every morning, and it shapes the plan.** 1,676 pins by 221 agents; mostly re-pinning the same title
  (1,271), 184 changes of pinned note. On 1,297 decisions with a pinned note, the day's "why" shares 3 or more content words with
  one's own pinned note 94% of the time, against 68% for another agent's pinned note (the shared vocabulary of stores and
  winter): a real but modest lift, since most notes and plans are about the same things.
- **Unpinned notes: almost never.** 456 distinct notes: 155 (34%) were pinned at some time; 38 never pinned were opened at least
  once; **263 (58%) were never read back in full**, only their titles. Of those, 152 were written once and left; 111 were rewritten
  without being read ("Food plan" x7 by Ivo; "Debts" x4 by Simkin), from what was in the conversation.
- **Openings:** 91 in 1,615 agent-days on which someone held unpinned notes (5.6 per 100); two-thirds in the decision (which then
  shows them at the talk step), a third in talk. By whom: Haiku 5.5 43, Opus 4.7 29; four agents account for 37 (Roger and Jory in
  d1_duo, Lucy and Randal in r1). When: 38 of 91 on a day of offers or agreements, 9 on arrivals; the opened note was most often
  written the day before (27) or long before (25 at 5+ days). What: "Timber for winter" (14), "Winter plan" (10), "Fenwick Rise"
  (6), "Stores watch", "Who is where", "Winter stores" (5 each); debts and terms a few times.
- **Stretch memories:** read back by construction at every opening; not chosen. In the queue (D4-28) each is shown for six
  stretches, then dropped; in rewrite (D4-61) the one memory for life.
- **Look-ups:** read at once, by definition; rare (§1).

**When not:** a note that is not pinned is, in practice, write-only. Agents open notes when a deal or a ledger needs checking, and
the habit lives in a few agents; nobody browses their notes, and the title list does not prompt it.

## 5. What this means for the questions asked (31 Oct and 1 Nov)

- **More blocks would change little.** The cap binds for a handful of heavy writers; for everyone else unpinned notes are not
  read. What gets used is what is shown without asking: the pinned note, the stretch memory, the conversation.
- **Notes do the work of the engine's missing ledger.** 42% stores and winter, 11% debts: agents keep by hand what a store and an
  agreement list already show them each morning, mostly to reckon (meals against nights, timber against cold nights). A belief
  store that shows their own stores and debts plainly (38.37 §7e) would free notes for what the engine cannot keep: lessons,
  intentions, judgments of people.
- **Long-term memory of people and events lives in the stretch memories, not the notes**; with D4-61 it is one rewritten text.
- **Cued recall** (a note shown when today names what it is about) fits the evidence: notes are opened on deal days, about the
  thing being dealt in; the engine could do what the agent rarely does.
- **Sonnet 5.5's silence** means any design that relies on agents choosing to write will not reach a third of a typical cast.
- **Data faults found:** w1's Opus 4.5 memories after day 24 are empty (the usage limit before the fail-stop existed); excluded.

*Current as of 1 Nov 2026.*
