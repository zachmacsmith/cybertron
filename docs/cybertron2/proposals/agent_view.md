# What an agent is shown: the world and its rules, not choices made for it

**Status:** discussion
**Owner:** 37.4

## Summary

Rebuild the system text and the daily message on these principles: the engine shows the world and the rules a person living there
would know, and never works out the agent's choices for it; each thing is shown once; detail about a craft follows how well one
knows it and stops at know-how (skill and its effects are never told, only met in outcomes); a fixed grammar of action kinds
replaces the verb manual; common knowledge only, in words; stable things in the system text and today's world in the message;
lists that grow with the world are budgeted by closeness; the verbs back to the closed grammar first designed; one belief store
per person, fed by the senses and every other channel, from which the message is rendered. Also: a constant reply schema, so
conversations restart only at the end of a stretch. The inventory and evidence are in review 38.37.

## The proposal

1. **No computed choices.** Drop "Today you could" and "Not yet". A refused act already says why. The place lines' "here one can
   ..." (what this kind of ground allows, of the crafts one knows) stay as the answer to "what can I do here".
2. **Each thing once.** One entry a craft, putting the reply word beside the long name; one line a rule.
3. **Craft entries by depth:**

   | One's relation | Shown |
   |---|---|
   | never heard of it | nothing |
   | knows of it | the reply word, the long name, how one knows of it |
   | a rough idea | plus where it is done and what goes in, without amounts |
   | capable or knows it (basic crafts too) | plus amounts, what comes out, the work, whether it needs a tool or beasts; a skill word |
   | long practice | the skill word risen |

   No multipliers or yields by tool at any level. Practice changes outcomes; agents meet them in their results, in what they see
   others get and in what they are told, and keep what they learn in their notes and memory.
4. **The verb grammar as first designed** (verbs.md): about 22 verbs, each a kind of change on a kind of referent, shown once
   with their slots (about 300 tokens); settings on things one controls through `set`, powers of offices and creditors through
   `invoke`, membership of any institution through `join`, `leave`, `found`; the night's and the road's choices as existing verbs
   with options. Today's 34 verbs and 18 event words (52 values of `do`) fold back into it. (Replaces "action kinds", which only
   grouped the same verbs.)
5. **Common knowledge only** in "How life works": the day and units, eating and the cold, fire, what is whose, how people learn,
   what one notices; numbers only where people count (meals, units, days, weights).
6. **Stable in the system text, today in the message;** a change in what one knows mid-stretch is one line in the message ("You
   have learned of ..."), not the whole list again each day.
7. **Budgets by closeness** for kin, places, crafts known of and beliefs, once they grow long.
8. **A constant reply schema** for the run: the lists of known names out of it (free strings; the verbs refuse unknown words).
   Conversations then restart only at the end of a stretch, where the memory is written.
9. **One belief store per person, and the message rendered from it.** Entries of (thing, aspect, value, day, how known); every
   channel writes to it: the senses (signs, the noticing rule), speech (mentions), one's own acts and their results (which sense
   what was worked), seeding. Structure anyone present sees at once (parcels, buildings, people) goes in by a sure sight; states
   (crops, stores, condition, beasts) by signs. The engine reads the true state only for one's own body and the day; nothing is
   computed for the agent from the true state. The five partial stores today (land, beasts, things, home, elsewhere) become
   aspects of the one store. The senses become the channel for nearly everything in the world (today 3.8% of what an agent reads).

Open to test: whether the store's "food worth N meals; about K a night" stays (arithmetic on what one sees).

## Why

Zach (31 Oct): "showing them enough information to understand the world, but not to bias them too much and hand hold them into
acting in a certain way"; "there are a bunch of different actions, but the individual agent only knows some ... knowledge and
learning should be able to cap how much they see about all possible actions naturally"; "we shouldn't arbitrarily insert too much
info, because some of this they should learn themselves ... it shouldn't just be like 'reap 5 times then you suddenly are told
that you need to reap on Wednesdays'".

Evidence (38.37, d1_duo): 87% of craft actions were on the day's menu, which is cut at 10 entries in the crafts table's order;
nobody built anything in 10 days; 18 of 324 replies plan with the manual's multipliers ("felling runs at x1 now, not x0.25"); the
look-up was used in 0 of 324; each craft is shown up to five times; the system text is 14,800 characters and grows with every craft
in the data; 22 conversation restarts off schedule lost detail with no memory written. Against D4-24 ("not from a complete
manual") and knowledge.md §4d (names in the system text, cards by look-up).

## Alternatives considered

- **Keep the menu, make it fair** (uncapped, buildings in, no table order): keeps uptake, keeps the engine choosing what is shown
  as possible. Tested as arm B; a candidate for Haiku only, as Haiku keeps the memory queue (D4-61).
- **Cards by look-up** (knowledge.md §4d): unused (0 of 324); detail one must ask for is not seen.
- **Detail rising with skill** (tool effects, better ways shown to the skilled): rejected by Zach (31 Oct): that is told learning,
  not learning.
- **Fewer basic crafts** (today 47 of 63): not part of this proposal; a world-design choice that would shrink every agent's list
  and make people need each other (scenario_design §1). For Zach.

## Open questions

1. The test (38.37 §7): arms A (as now), B (a fair menu), C (this), in the duo world; waste on refusals, the range of crafts used,
   make and build, chains completed, Haiku's acts, the end state.
2. Whether Haiku keeps a fair menu, whatever C shows for the others.
3. The store's meals and nights line.
4. Which crafts are basic.

## Affects

spec/information/prompts.md, perception.md, spec/agents/actions.md (D4-24's wording), proposals/verbs.md, knowledge.md §4d,
seeing.md §1, senses.md; cybertron2/engine/prompt.py, perceive.py, knowledge.py, verbs.py, converse.py.

## History

- 31 Oct 2026: proposed (37.4) after Zach asked for a review of everything in the system text and the daily message (review
  38.37), with his point that skill should not unlock told detail; the schema restarts found while answering his question on
  what carries from day to day.

- 31 Oct 2026: revised after Zach ("didn't we originally design the verbs to be the primitives? ... It feels like a rename";
  "are senses not coming much into this at all?"): "action kinds" withdrawn as a rename; point 4 now restores verbs.md's grammar
  (38.37 §7c: 24 designed, 34 verbs and 18 event words built, none decided); point 9 added, one belief store rendered into the
  message, from 38.37 §7d (3.8% of what an agent reads comes through the senses; the menu tells crop states the senses would gate)
  and §7e (what an agent has to know, from first principles).

## Sources

Review 38.37; runs/d1_duo; proposals/knowledge.md, seeing.md; D4-24, D4-27, D4-61; Zach's messages of 31 Oct.
