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

**How much there is to see.** A thing at a moment carries more facts than its state fields: its own state (a building's storeys,
material, condition, fittings: about 5-15), what its **processes and occupants give off** (cattle lowing in a byre, a hammer at a
working forge, bread smelling from an oven, smoke from a lit hearth, a dog barking at a stranger), what **the weather and light do to
it** (mud after rain, frost on the thatch, low evening sun), **traces of recent use** (fresh chips at the chopping block, a new cart
rut, a door left open), and **who and what is about it**. All of these can be derived from the state by simple rules (a table of what
each fitting, animal, process and weather gives off to each sense), so they are facts, not invention: a place may hold 20-60 at a
time, of which attention and salience pick 5-12 for one observation. Rendering, by template or model, may only state or directly
imply given facts.

Observations are how information that is otherwise not obvious enters the world: a store that looks too full after a lean
season, a neighbour's ox that is not theirs, tracks where nobody should have walked, a house that has been empty three nights.

## 3b. How facts are produced, chosen and tracked

**Produced on demand, not stored.** The engine never keeps a list of every possible fact. Each round it computes, for each node,
the facts its current state gives off, from two sources:

1. **Things, by rule.** Each kind of thing (the node, a site or plot, a building and its rooms, a fitting, a person, a herd, an
   edge, the weather) has a small set of fact rules: `(state) -> facts`. A **sense table** (data) says what each fitting, animal,
   process and weather gives off to each sense: a byre with cattle gives lowing and dung; a forge in use, hammering and smoke; an
   oven, the smell of bread; rain, mud and dripping eaves.
2. **Happenings, from the event log.** Every change on the chokepoint (a fight, a cart arriving, a door forced, a fall) and every
   incident or fuse event (02k) gives off **momentary facts**: shouting, hooves on the road, a crash, smoke rising.

Each fact carries: its subject, the sense, its **salience** (how much it stands out), its **range** (a room, a site, the whole node,
or carried along an edge toward neighbouring nodes), the **skill** needed to notice or read it (a builder reads rot, a hunter reads
tracks), whether it lasts or is momentary, and, hidden, whether it is true (signs can mislead).

**Chosen per agent, by how it spends the day:**

| How the agent relates to the thing | What it gets |
|---|---|
| **Just being present** at the node | every high-salience fact in range (the weather, loud sounds, smoke, bells, a fight), plus a few lower-salience ones drawn at random, weighted by salience (the seed decides; the same in every arm) |
| **Working at it** (it spent units at that site, building or animal) | the facts about that thing that bear on the work (the field's state when sowing it, the forge's fire when using it) |
| **Attending to it** (one target a day) | all its facts above a low salience threshold, plus the facts its skill lets it read |
| **Standing watch** (`guard`, or a watch office) | a better chance of catching momentary facts at the node's edges: **hooves on the road at dusk** is how a raid is heard coming (the detection of a fuse event, 02k) |
| **Being watched** | a chance of the fact "someone was watching you" |

**Everything an agent can attend to** (one a day; only what is at its node, or visible from it):

| Target | What attending gives |
|---|---|
| **a person** here | condition (fed, hungry, wounded, ill, tired), what they carry and wear, what they did today, with whom, where they went when they left |
| **a gathering** (a market, a meeting in a hall, a crowd, a quarrel) | who is there, who stands with whom, who speaks and who is listened to, the mood |
| **a building** (from outside) | structure, material, condition, what can be seen of its fittings, smoke, sounds and smells from inside, who went in and out today, how full its store looks |
| **a room** it may enter | who is in it, what is on show (goods, a notice, a document left out), its fittings in use |
| **a field or plot** | crop and its ripeness, soil, weeds, water, animals on it, signs of work or trespass |
| **a wood, pasture or other site** (the stream, the well, a quarry, a seam) | the state of what it gives (plants, game, timber, stone), signs of use, tracks |
| **a herd or animals** | about how many, their condition, whose marks they carry, how they behave (unrest before weather) |
| **goods in view** (a cart, a stall, a pack being unloaded) | what and roughly how much, their quality to a skilled eye |
| **a notice or document posted** | its text, if it can read |
| **a road out** (each edge) | who came along it today, tracks, its condition, and at dusk anything approaching |
| **the land and sky** | weather, the season's signs, the horizon: smoke, a glow at night, birds |
| **the place in general** (eyes open all day) | the less subtle facts spread around the node (a few, here and there), its ambience (sounds, smells, the mood), and a better chance at anything salient; no detail about any one thing |
| **a body, or a scene** (where a fight was, a burnt house) | what can be seen of what happened |

These are instances of four general kinds (a parcel, a feature, a structure or room, a movable) plus gatherings and the sky:
see [layout.md](layout.md), which generalises them.

Not attendable: other nodes (only what can be seen from here, such as smoke on the horizon), anything inside a room it may not
enter, and its own house and body (already shown to it every round).

**Noticing: the engine offers, the describer picks, and reports what it picked.** An agent does not take in every fact in range.
The engine offers a set of candidate facts for an observation, each marked **salient** (it stands out: a fire, a fight, a scream, a
stranger, a cold hearth in the evening) or not, and each with an id. The describer (template or model) must:

1. include **every salient fact**;
2. add the facts **most relevant to this observer**: what bears on its state (a hungry man notices the woodpile and the bread
   smell), its trade and skill (a builder the rotten beam), its concerns, its beliefs and its experience (the almanac keeper the
   early geese; a man robbed last winter the broken lock), up to a few facts;
3. **return the ids of the facts it conveyed**, with the text.

Only the returned facts go into the agent's knowledge store, so the store and the text always agree, at no extra call. A template
renderer does the same with relevance computed by the engine (facts tagged by what they bear on: food, shelter, a trade, danger, a
named person, a claim, matched against the observer's state, skill and concerns); a model renderer judges relevance itself, which
is where it can do better than a template.

**Tracked: only what was perceived.** What an agent perceived goes into its knowledge store as dated beliefs (knowledge §7); what
it was not given is never stored. So the record shows exactly who noticed what, when, and why (present, working, attending,
watching), which is what information studies need.

**Is it easy?** The machinery is: a node holds tens to a couple of hundred candidate facts a round, computed from state, filtered
by range, salience, skill and the agent's day, with seeded draws; the event log already has places and causes. The work is in the
content: the fact rules per kind of thing, the sense table, salience and skill thresholds, and the phrasing pools (§4). That grows
with the world, as data (D4-24), and can start small: a dozen kinds of thing, a few facts each.

## 3c. Two channels: the daily notice and attending (Zach, 23 Oct)

| | **The daily notice** (every agent, every round) | **Attending** (one target a day, chosen) |
|---|---|---|
| What | only the **most salient** facts in range: a fire, a fight, a stranger, smoke on the horizon, the first frost, a sign of a coming change | every fact about the target above a low threshold, plus what the observer's skill reads |
| Who | each fact reaches an agent **with a chance**, weighted by how salient it is and **how relevant it is to that agent** | the attender |
| Rendering | **templates only**, a line or two | detail; a **model description** through the observer's eyes (Sonnet's level), or templates |
| On a quiet day | often nothing: quiet days are quiet, and the engine does not invent things to notice | whatever the target holds |

**Relevance to an agent** is a score the engine computes from tags on the fact against the agent's record:

| Source | Example |
|---|---|
| trade and skill | a fowler or hunter notices the geese; a farmer the frost on the stubble; a herder the cattle's thick coats; a builder a sagging roof |
| experience | it has seen this kind of sign before: the hard winter twenty years ago, a raid that began with smoke on the road; a man once robbed notices locks |
| state and concerns | the hungry notice food; whoever worries about the stores notices the season's signs; a guard notices movement on the road |
| where it spent the day | in the fields it sees the sky; on the road, travellers; on watch, the approaches |
| what it knows | it can only see "the fires of Millford" if it knows Millford and which way it lies; otherwise "a glow in the east at night" |
| ties | its kin, its land, its house |

The chance of noticing is roughly salience times relevance: the most salient facts reach nearly everyone in range; low-salience
ones reach only the agents they bear on.

**Signs for environmental shifts.** Every change from outside (an era, a season's severity, an incident, an event at a distant
place: D4-4, D4-5) is defined with two parts: **its effects on the mechanisms** (regrowth, the cold, danger, yields) and **its signs**,
each with a sense, a salience, a range, a lead or lag, a reliability and relevance tags. For a hard winter coming:

| Sign | Salience | Noticed by |
|---|---|---|
| geese leaving early | low | fowlers, hunters, the almanac keeper, the old who remember the last hard winter |
| first frost two weeks early | medium | farmers, anyone out at dawn |
| cattle growing thick coats | low | herders |
| a hard, cold wind from the north for days | high | everyone |

For a city burning two days away: a glow on the horizon at night and smoke by day (high salience, seen from nodes within sight of
it), named only by those who know the city; then travellers' news.

**Is there enough to notice?** For the daily notice, it depends on the world: quiet days give little and should; a world with
seasons, incidents, eras and neighbours gives a steady trickle, which is what the environment design (D4-4 to D4-7) supplies. For
attending, each kind of target holds 5-15 facts once the fact rules exist (§3b), which is plenty for a detailed look.

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

**Slight misreadings are acceptable** (Zach, 23 Oct): people mis-see things a little all the time, so a narrator's small
stretches ("the north wind has frost in it") need not be caught. The check catches only what would mislead an agent into a wrong
act or a wrong belief about something that matters: a new object, place or person; a new cause or order it would act on ("the deer
prints are fresher still"); a hidden fact.There is **no deliberate misperception** (Zach): the engine never gives an agent a
wrong fact on purpose; false beliefs come only from what people say, rumour and old sightings (knowledge §7).

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

- 23 Oct: Zach: the facts may be too thin; add what things give off (sounds, smells), and a model description should only imply real
  given facts, seen through the observer's eyes (who they are, their skill, their state, what they care about). Added the paragraph
  on how much there is to see (derived sensory and ambient facts); a second test round is running with richer facts and an
  observer's-eye prompt.

- 23 Oct: Zach: how attending varies by target; just being present should give clear things about the place (sounds) and chance
  noticing; environmental events such as an approaching raid heard; how facts are tracked and whether it is easy. Added §3b: facts
  produced on demand by rules and a sense table, and from happenings; each with sense, salience, range, skill; chosen by presence,
  work, attention, watch; only what was perceived is stored.

- 23 Oct: test run 2 (10_descriptions_test.md "Run 2"; 64 richer facts incl. sounds and smells; observer profiles; every clause
  must rest on a given fact; 30 calls, $0.18): no clause without a supporting fact in either model (the rule worked); Haiku and
  Sonnet conveyed 83-84% of facts (dropping season, time, light), with a few small stretches; one borderline hint at a hidden fact
  (Sonnet's almanac keeper "knows what the early geese mean", a belief she might fairly form); comprehension unchanged (10/10).
  Only Sonnet writes through the observer's eyes (about 15 times Haiku's cost). Recommendation unchanged: templates for facts in
  the engine; an observer's-eye Sonnet narrator only as a later experiment, with a checker that knows which beliefs an observer
  may form.

- 23 Oct: Zach: descriptions need not convey every fact; people notice some. Added: noticing is the engine's draw, so the engine
  picks fewer facts and the renderer conveys all it is given (else the store and the text disagree).

- 23 Oct: Zach: the describer should notice at least the most salient facts and those most relevant to the observer (its state,
  beliefs, experience). Replaced "the engine picks fewer facts" with: the engine offers candidates marked salient; the describer
  includes all salient facts plus the most relevant to the observer, and returns the ids it conveyed, which alone go into the
  knowledge store.

- 23 Oct: test run 2b (Opus, same prompt, 5 calls, $0.11): reads best and takes the observer's view most clearly (58/64 facts, no
  clause without a fact) but takes more small liberties than Sonnet (6 stretches, e.g. ordering the deer prints and the boots in a
  way the facts do not give, which a hunter would act on) and costs twice as much. For the observer's eye Sonnet is enough; any
  narrator needs a check that catches facts joined into new causes or orders, not only new facts.

- 23 Oct: Zach: every agent sees a few templated, most salient facts each round, with a chance and only where relevant; attending
  gives detail and the model description; environmental shifts each have mechanical effects and signs of different salience,
  low ones noticed only by the relevant (a fowler sees the geese); distant events seen as signs (a city's fires) by those who know
  of the place. Added §3c: two channels, relevance from trade, experience, state, the day's place, knowledge and ties; signs for
  shifts with salience and relevance tags.

- 23 Oct: Zach: a very slight misinterpretation is fine; people mis-see things subtly all the time. Added to §4: the check catches
  only misleading inventions (new objects, causes or orders an agent would act on, hidden facts); misperception as a mechanic lives
  in the engine (seeded, recorded as false beliefs).

- 23 Oct: Zach: no deliberate misperception. Removed the engine misperception mechanic. Zach asked for everything an agent can
  attend to: replaced the short table in §3b with the full list (a person, a gathering, a building, a room, a plot, a site, a
  herd, goods in view, a posted notice, a road out, the land and sky, a body or a scene) and what is not attendable.

- 23 Oct: tested in M1 runs A and B ([11_m1_slice.md](../../review/38_space_engine/11_m1_slice.md)): agents attend to their own house
  more than anything (Q4 there); low-salience signs reach few, as designed; felt-watched and sightings read naturally. Not
  revised yet.

## Sources

cybertron2/prompt.py and perceive.py (as built), 38.02, knowledge.md, notes.md, verbs.md, D4-6, D4-11, D4-19, D4-21, D2-4.
