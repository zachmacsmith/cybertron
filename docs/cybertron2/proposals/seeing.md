# Proposal: what an agent is shown each round, attention, and describing the world

**Status:** discussion (23 Oct). **Owner:** 37.4. **Affects:** spec/information/perception.md, prompts.md, signs.md;
core/round.md. Builds on 38.02 (perception as built), [knowledge.md](knowledge.md), [notes.md](notes.md), [verbs.md](verbs.md).

## Summary

An inventory of everything an agent sees, as built in phase 0 and as the designs so far would add, with how it changes over rounds;
then what is missing and what should go. The main change proposed: **an agent does not see everything everyone does at its node.**
It sees what concerns it, what is salient, a brief glimpse of the rest, and **in detail only what it pays attention to**. Attention
is a free daily choice (a person, a building, a site, the land), and being watched may be felt. What it sees is **observations**:
facts drawn from the world's state, with what a skilled or attentive observer notices, rendered in world terms. The facts come from
the engine (deterministic, the same in every arm); rendering them is templates first, with an optional narrator model per node and
day that may only rephrase given facts.

## 1. Everything an agent is shown, and how it changes

**System prompt** (rebuilt only when something in it changes):

| Section | Content | Phase 0 | Planned | Changes over a run |
|---|---|---|---|---|
| Who you are | name, role, age (stage), household and kin, others in the land | yes | stage words, not ages (D4-19) | at coming of age, a partnership, a death in the household |
| What you want | the aim in world terms | yes | | rarely (a goal change) |
| The land | **every place, its features and neighbours** | yes | **only the places the agent knows, as it last knew them** (a map is knowledge); **every edge from its current node is always visible**, named where it leads if the agent knows, otherwise described by what it looks like ("a cart track north-east, rising toward the hills, well used") | as it travels or is told |
| How life works | rules with their numbers | yes | the manual's common knowledge, short; detail by look-up | rarely |
| What you know how to do | | no | crafts, rough ideas, awareness with sources (knowledge §4d) | when it learns |
| Your institutions | | no | memberships, offices and their powers (`invoke`), laws it knows | when it joins, takes office, or learns a law |
| How to act | the reply format and action syntax | yes (15 actions) | the 24 verbs (verbs.md) | when an office adds powers |

**Turn prompt** (every round):

| Section | Content | Phase 0 | Planned | Changes over rounds |
|---|---|---|---|---|
| Now | the round, the season, your units | yes | day of the season, daylight units (D4-17), today's signs (D4-6) | daily |
| Here | the place and its signs (with change since last seen), houses, people present with how they look and what they carry | yes | sites, buildings and rooms, people, **observations** (§3) | daily |
| Seen last round | **every act at every place you were**, grouped | yes | **what concerned you, what was salient, a glimpse of the rest, and in detail what you attended to** (§2) | daily |
| You | hunger, carried goods, tonight's need | yes | plus wounds, illness, exhaustion (working late), life stage | daily |
| Your house | exact when there, else as last seen | yes | plus who slept there, the stock's changes | daily |
| Today you could | | no | options here and near misses (knowledge §4d) | daily |
| Owed and asked | | no | **due lines**: debts, duties of office, errands, offers and requests made to you, invitations | as they arise |
| Elsewhere | kin and people last seen, places last seen | yes (with a computed absence to remove: D2-4) | dated beliefs only | as beliefs age (dropped after 6 rounds) |
| Lasting memories | deaths, fights, gifts, the cold (14) | yes | plus childhood memories (09 §2c), arrivals and departures of kin with stated plans (D2-4) | slowly |
| Earlier rounds | one line a round (8) | yes | | rolls |
| Last rounds | the last 2 in full: did, heard, saw | yes | | rolls |
| Notes | one free note | yes | one pinned note in full, titles of the rest (notes.md) | when it writes |
| Talk step (if asked again) | messages to it, replies, opened notes, looked-up cards | no | yes (05 §1, notes.md) | when spoken to or when it opens something |

## 2. Attention: not everything everyone does

At village scale (up to about 15-20 people, D4-11), showing every act of everyone is both unrealistic and too long. Proposed tiers:

| Tier | What | Shown as |
|---|---|---|
| **Concerns you** | acts done to you or yours (a gift, an offer, a blow, your house raided, your field reaped), speech to you | always, in full |
| **Salient** | arrivals and departures, fights, deaths, a fire, a building raised, a proclamation, someone in distress | always, briefly |
| **Glimpse** | everyone else at the node | one short line about each of a few people (who is busy where: "Gil spent the day in the Deep Wood"), a sample drawn by the seed, most familiar people first |
| **Attended** | the one thing the agent chose to pay attention to today | in detail (§3) |

**Attention is a free choice in the reply** (`attend {person | building | site | the land}`), one a day. It costs no work units;
it is the agent deciding what to look at. Following someone all day (`watch`, a verb) costs units and teaches (knowledge §4c);
attending only observes.

**Being watched may be felt.** When someone attends to a person, that person has a chance of noticing ("you had the feeling Brenna
was watching you today"), higher if they are themselves attending to the watcher or to their own surroundings, lower in a crowd.
This gives surveillance a cost and counterplay without new rules.

## 3. Observations: what the world can tell an observant agent

An observation is **a fact the engine draws from the state**, at a fidelity set by attention and skill, rendered in world terms:

| Target | Facts available | Who sees more |
|---|---|---|
| A building | storeys, material, condition (sound, worn, damaged, ruined), fittings visible from outside (a chimney smoking, a lock), signs of use (smoke, traffic, tools left out), how full its store looks | a builder sees the rot in a beam; a thief sees the lock |
| A person | how they look (fed, hungry, starving, wounded, ill, exhausted), what they carry, what they did today, whom they spoke to (not what they said, unless near) | a healer sees illness early; anyone attending sees more of their day |
| A site or plot | the crop's state, the soil, signs of use or trespass, the stream's level | a farmer judges soil and crop; a hunter reads tracks |
| The land and sky | the weather, the season's signs, smoke from the next valley, birds leaving early (signs, D4-6) | the almanac keeper, the old |
| A gathering | who is there, who stands with whom, the mood | anyone attending |

Observations are how information that is otherwise not obvious enters the world: a store that looks too full after a lean
season, a neighbour's ox that is not theirs, tracks where nobody should have walked, a house that has been empty three nights.

## 4. Generating descriptions: templates or a model?

| | Templates from the engine's facts | A model drafting from the state |
|---|---|---|
| Cost | none | a call per description |
| Same in every arm, replayable | yes | only if recorded and replayed |
| Truthful | yes, by construction | can invent or leak what the agent should not know |
| Variety | repetitive | rich |

**Proposed: facts always come from the engine; wording is templates first.** If the wording proves too flat, an optional
**narrator per node per day** (one cheap-model call for the whole node, not one per agent) rewrites the day's facts for that node
in prose, given only the facts each agent may see, recorded with the run and replayed. A check compares each narrated sentence
against the facts it was given (no new names, numbers or events). The narrator never decides what an agent learns: the engine
does.

## 5. What is missing, and what should go

**Missing:**
- **Relationships**: who these people are to me (kin, friend, rival, creditor, patron) and how things stand: from the seeded past
  (D4-21) and what has happened since. A short "People you know" section, budgeted.
- **Owed and asked**: debts, duties, errands, offers and requests to me, in one place.
- **The body**: wounds, illness, exhaustion, stage of life.
- **What I meant to do**: plans carry over only through notes; a standing plan line (the pinned note may be enough).
- **Prices and terms known**, with their age.
- **Attention and observations** (§2-3).

**Should go or change:**
- **The whole map in the system prompt**: only places the agent knows, as it knew them.
- **Every act at the node**: replaced by the four tiers.
- **The computed absence** ("not seen for N rounds"): already decided (D2-4).
- **Long rule text in every prompt**: keep the short common knowledge, move detail to look-ups.
- **Ids where names will do.**

## 5b. A worked example (proposed; abridged)

**System prompt** (rebuilt on change):
> You are Cela, a woman of the Alder household (Bram, your husband; Dara and Eoin, your children), living at Alder House in
> Millbrook. Others you know: the Wynns (Near Wood), Torvald's people (the Hills, by repute).
> What you want: keep your children safe and fed; keep on good terms with the Wynns.
> The places you know: Millbrook (home: fields, meadow, the brook, three houses); the Near Wood (a day east; timber, game); the
> Hills (a day north-east, by repute: copper, Torvald's forge). From Millbrook: a track east into the woods (to the Near Wood); a
> cart track north-east, rising toward the hills (to the Hills); a footpath south along the brook (you have not been).
> How life works here: [a short paragraph of common knowledge; detail by look-up].
> What you know how to do: farming (competent): sow, tend and reap barley and beans; cooking, mending. A rough idea of: firing
> pots (you saw Mora fire them). You know of: ploughs (you saw Torvald's), kilns (Wynn told you of them).
> How to act: [the 24 verbs with syntax; the reply fields: say, tell, note, pin, open, attend, look up].

**Turn prompt** (each day):
> Day 9 of autumn; winter in 6 days. Cold and clear. You have 6 units.
> Here, Millbrook: the barley on the Long Field is ripe; the brook runs low. Bram and Eoin are here; Wynn arrived this morning from
> the Near Wood, carrying a full pack.
> Concerned you yesterday: Wynn offered 3 grain for a pot (open until tonight).
> Seen yesterday: Dara spent the day in the Near Wood; Torvald's son passed through toward the Hills with copper.
> You attended to: Wynn House: the door barred, smoke from the chimney though Wynn was away.
> You: fed; carrying 2 grain, a knife. Tonight at home you need 1 food.
> Your house: sound; 14 grain, 6 beans, 9 timber; four of you sleep here.
> Owed and asked: the village's harvest levy, 2 grain, due by winter.
> Today you could: reap the Long Field (ripe: about 2 days' work for one); make bread; try firing a pot (clay at the brook, you
> would need a firing pit).
> People you know: Wynn (neighbour, owes you a favour since the flood); Torvald (a stranger, armed).
> Lasting memories: the flood two summers ago took the low field; your mother died last winter.
> Earlier days: [one line each]. Yesterday in full: [what you did, heard, saw].
> Pinned note: "Ask Wynn about the kiln before winter." Other notes: Prices at the Hills; What the Wynns owe.

## 6. Open questions

1. How many people a glimpse covers, and how they are chosen (familiarity, salience, a seeded sample).
2. Whether attention is one target a day or a little more for some (an observant temperament, an office such as a watchman).
3. The chance of noticing being watched.
4. Which observation facts come first (buildings' condition, people's state, signs, crops, tracks).
5. Templates only for the first runs, the narrator as an experiment?

## History

- 23 Oct: proposed (37.4, with Zach), after Zach asked for a deep dive on everything an agent is shown, whether agents should see
  everything others do, attention to a person or a building, the feeling of being watched, and generating rich descriptions
  automatically or with a model.

- 23 Oct: Zach: every edge from the agent's node is visible, described by its look unless the agent knows where it leads; asked
  for a walk-through of a whole prompt (added §5b); a quick test of templates against a model writing descriptions is running
  (docs/review/38_space_engine/10_descriptions_test.md).

- 23 Oct: the quick test (docs/review/38_space_engine/10_descriptions_test.md; 5 states, 45 calls, $0.05): templates conveyed all
  32 visible facts with nothing invented; Haiku and Sonnet conveyed 29, each inventing 2 small details ("beyond the ridge" where
  there is none); no hidden fact leaked; an agent understood template text as well as model prose (the reader's instruction to
  draw conclusions mattered, the wording did not); templates read flatter. Its recommendation: templates in the engine, with
  phrasing pools written once by a model against set fact values and checked; a narrator per place only as a later experiment;
  prompts that invite agents to draw conclusions from what they see.

## Sources

cybertron2/prompt.py and perceive.py (as built), 38.02, knowledge.md, notes.md, verbs.md, D4-6, D4-11, D4-19, D4-21, D2-4.
