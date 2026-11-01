# When people talk, and what it costs: by reach, with an evening at the hearth

**Status:** accepted: D4-65, D4-66, D4-77 (2 Nov)
**Owner:** 37.4

## Summary

The day gets an evening. Everyone who sleeps in one building or camp meets at its hearth after the day's work. There they learn how
their day went (what they did and got, what they saw on the parcels they worked, whom they met) and talk freely with the house.
Anyone asked something directly is then woken once to answer. The morning keeps the plan and one wave of answers to private words.
The second wave goes, both morning and evening. Free speech in common happens only at a gathering: the hearth by default, later a
place one chooses to spend the evening, or a meeting someone calls. Speech beyond a gathering is a private word (free, capped) or
calling out to the whole place (a unit).

## The proposal

1. **Who hears is fixed by where one is when speaking**, never by where one will be. Speech comes before the day's work or after
   it, so "those on my parcel" is not known when one speaks; the parcel is not a reach.
2. **The evening at the hearth** (after work; before who sleeps where is settled, eating and the night's events):
   - each person at a hearth is asked once, together: the day's outcome is shown here (the results of their acts, what they saw,
     whom they met, the day's events), not the next morning;
   - each may speak to the house (free, everyone at that hearth hears), tell one person (a private word), write a note, and say
     what they mean to do tomorrow;
   - then **one wave**: only those asked something directly (a tell, or speech to the house naming them) are woken to answer.
     A asks, B answers; A reads the answer in the morning.
2a. **The evening decides the night** (Zach, 2 Nov: "if someone asks to be let in during the day, the owners of the house can
   decide whether to let them in in the evening talk"). The evening call comes before who sleeps where is settled, and it carries
   the free acts that answer the day's requests or take effect tonight:
   - answers to requests made during the day, listed in the evening message: let someone in for the night (host), take someone
     into the household (admit), accept or refuse an offer, become partners;
   - the night's own choices: where to sleep, the door barred or open, a fire if sleeping out, trying for a child, setting off on
     a journey at nightfall;
   - two-sided acts that today must be chosen by both in the same morning (partner, try, join and admit) are then answered where
     both are present; trying for a child is decided at the hearth, where it belongs;
   - whoever a decision concerns and who is not at that hearth (the stranger at the door) learns it in the answer wave, before
     the night.
   The morning plans the work; the evening settles the night.
3. **The morning:** the decision as now, with dawn's news and what was said last night; private words to people at the same place;
   **one wave**, in which those told something are woken once to answer and re-plan. No second wave.
4. **Speech by reach:**

   | Speech | Who hears | Cost |
   |---|---|---|
   | at a gathering (the hearth; later, a chosen evening place or a called meeting) | everyone at it | free |
   | a private word (tell) | one person at the same node | free, capped per day |
   | calling out to the whole place | everyone at the node | 1 unit |

5. **Gatherings, for larger places (later):**
   - the evening place is a choice, home by default: an alehouse, a hall or a neighbour's house instead, if one may go in. Each
     gathering has its own round, so a town's evening is many rooms at once;
   - **a gathering called for the day** (Zach, 2 Nov): anyone may call one at a parcel or a building, for tomorrow, at the hearth
     or by calling out. Everyone at that place finds it in their morning message ("Ivo has called the Hobbs and the Ashbys to the
     Green: a unit to come"). Those who come spend a unit and get a round of their own after the morning's answers and before the
     work, with up to three waves among those present, and may re-plan the rest of the day. What is agreed there is witnessed:
     everyone present knows it, so agreements made at a gathering are common knowledge (cybertron 1: halls lost to private
     messages because they had no power of their own; this gives them one);
   - writing a notice (a document at a place, D2-24) is the town-wide channel that lasts.
6. **The memory request** (every few days) is folded into that evening's hearth call, which saves a call.
7. **To test against it:** plan tomorrow at the hearth, and wake people at dawn only if something new reached them (a word, an
   arrival, the night's events). This is cheaper than now, but dawn's weather reaches the plan only when someone is woken.

## Why

Zach (2 Nov): "what are the orders of speech times ... Maybe speech to everyone in a building should be free, but talking to
everyone in the town costs an action?"

Evidence:
- c3_combe_rich: 602 messages in 80 days, 97% private tells, almost all planning; 20 things said aloud (each costs a unit). Talk
  calls outnumber decisions: 382 re-asks on 251 decisions (60% of calls), mostly confirmations. Nothing is said in the evening,
  at meals or at work. The only grief beyond the day of the death came when the engine's weeping sign prompted it.
- cybertron2 measured: a unit per say "all but ended public speech" (DM share 0.96; review 38_space_engine/14).
- cybertron 1: channels lost to DMs on cost, speed and binding force (review 31_institutions/04); talk took 35-70% of actions in
  institutional worlds (review 26); long runs fell silent (36c); 72% of one run's cost was cache writes of DM-reply calls never
  read (review 20).

## Alternatives considered

- **All speech free.** The cost moves to API calls. Cybertron 1's talk-heavy worlds spent most of their actions on talk.
- **As now.** Private planning only, nothing said in common, and the most calls spent on confirmations.
- **Building speech free, town speech a unit, morning only** (Zach's first form). Cheap; keeps talk a planning step.

## Open questions

1. Whether the evening is its own call (point 2) or also the plan for tomorrow (point 7).
2. (Answered by Zach, 2 Nov: not the parcel, since nobody knows who will be there until they act.)
3. Whether speech to the house in the morning is free as well (the house is the same gathering) or the morning is for private words
   only.
4. Whether gatherings are used at all: not in one family (the hearth covers it); the test is a world of several households with a
   common to share (the Common at Combe was grazed bare again and again).
5. What to measure: share of talk that is not work; calls per agent-day; DM share; coordination failures (the harvest
   overshoot); whether households talk about aims, kin and the dead.

## Affects

run.py (talk step, waves), prompt.py (talk prompts), data.py (say_units), converse.py (the cached conversation), spec
information/prompts.md.

## History

- 2 Nov 2026: proposed (37.4) after Zach asked about the order and cost of speech and how it compares with cybertron 1.
- 2 Nov 2026: revised after Zach: the parcel dropped as a reach ("you don't know who will be in your parcel until you have
  acted"); the evening at the building or camp, where they "chat and plan and talk about what they want" and see the day's
  outcomes; the second wave of replies removed ("A says to B and then B responds to A"); only those asked something directly are
  woken in the answer wave; gatherings generalise the hearth for towns (his question about meeting rooms).
- 2 Nov 2026: Zach suggested a gathering one declares at a parcel, which others may join for more back-and-forth; folded into point
  5, called for the next day so others know of it before they plan, a unit to come, up to three waves, witnessed agreements.
- 2 Nov 2026: Zach: requests made in the day (being let in) answered in the evening talk. Point 2a: the evening carries the night's
  free acts and the answers to the day's requests; two-sided acts decided where both are present; the evening call moved before
  the night's sleeping is settled.
- 2 Nov 2026: Zach: "build all five then do the paired combe run". Accepted and built as D4-65 (the evening, one wave of answers,
  reach by where one speaks) and D4-66 (the evening settles the night), as a world setting (`evening: true`). Not built: gatherings
  called for the day (point 5), the memory request folded into the evening (point 6), planning tomorrow at the hearth (point 7),
  and the day's sightings shown at the hearth (they still reach the next morning, since noticing runs after the night); open in
  OPEN.md.
- 2 Nov 2026: Zach: "Add the evening add ons". Built as D4-77: meetings called for the next morning (point 5, with `meet` and
  `come`), the memory request at the evening (point 6), the plan made at the hearth as a world setting (point 7, `evening: plan`).
  Still open: the day's sightings at the hearth (needs noticing to run before the evening; after the noticing rework, D4-74).

## Sources

runs/c3_combe_rich; reviews 38_space_engine/14, 31_institutions/04, 26, 20, 36c; cybertron/runner.py dm_exchange;
cybertron2/engine/run.py talk step.
