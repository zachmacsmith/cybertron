# Proposal: what agents know they can do (actions, recipes, buildings)

**Status:** discussion (23 Oct). **Owner:** 37.4 (information, agents); 37.2 for the content (recipes, skills, blueprints).
**Affects:** spec/agents/actions.md, information/perception.md, information/prompts.md, information/letters_and_documents.md,
economy/production.md, economy/buildings.md, seeding/populations.md.

## Summary

The world can hold hundreds of things to make and build; no prompt can list them, and agents should not have to search blind.
Proposed: **a small set of verbs that everyone knows**, applied to objects (make *a recipe*, build *a blueprint*, work *a site*);
**what an agent can do here** computed and shown from where it is, what it carries and what it knows; and **know-how as personal
knowledge**, seeded with each person's upbringing and trade, spread by seeing, teaching, practice and documents. A short manual
covers only what everyone in the world knows (how food, the cold, travel and the day work). No blind crafting: agents cannot try
combinations to discover recipes.

## The proposal

### 1. Few verbs, many objects

cybertron 1 had 145 actions, one per mechanism. Here the verbs are few and general, and the variety is in their objects:

| Verb | Object | Examples |
|---|---|---|
| gather | a site here | forage, hunt, fell, quarry, mine, fish, draw water |
| make | a recipe | bread, a blade, a pack, rope, cloth, a letter |
| build | a blueprint or a part, at a lot here | a house, a store, a room, a hearth, a fence |
| work | a site, a plot, a project | sow, tend, reap, repair, a day on the mill's construction |
| give, offer, accept, store, take | goods | |
| travel, host, lodge | | |
| say, tell | (talk step) | |
| teach, learn | a skill or recipe, with someone present | |
| write, read | a document | |
| attack, raid, guard | | |

The verbs and their syntax are in every system prompt (concrete options with exact syntax, scenario_design §3). The objects come
from knowledge and from the place.

### 2. What you can do here (computed, not listed)

The turn prompt shows the options that are **real for this agent now**: the sites at its node and what it knows to do there, the
recipes it knows whose tools and workplace are here, with what it carries and what it lacks:

> At the Forge: you can make a blade (6 copper, 1 timber; you have 2 copper) or a knife (2 copper; you have enough).
> At the Long Field: sow (it is the sowing season), tend, or reap (nothing ripe yet).

Only what is relevant and known, within the budget (priority trimming, as cybertron 1's context module). A thing the agent does not
know how to make is not shown, even at a workshop that could make it.

### 3. Knowing that versus knowing how

| Kind | What it gives | How it spreads |
|---|---|---|
| **Awareness** (knowing that) | that a thing exists and roughly what it does: "the smith at Millford makes ploughs"; "a kiln fires pots" | seeing it, being told, hearing it at the inn, reading of it |
| **Know-how** (knowing how) | the recipe or blueprint: inputs, tools, workplace, work | **teaching** (both present, takes days), **apprenticeship** (youth learn fast and keep it: D4-19; 02c §5), **reading** a written recipe (with literacy: 02h), and **watching** a master at work many times |
| **Skill** (how well) | yield and cost per action, by practice | practice, decay (02c §5) |

Awareness without know-how is what makes specialists worth paying and secrets worth keeping: you know ploughs exist and that the
smith makes them; you must buy one, or learn from him, or find the book. Guilds, apprenticeships, recipe books and libraries become
valuable for the same reason (02h §6).

### 4. Seeded with each person's life

Seeded worlds (D4-21) give every person what their life would have taught them: the basics everyone in that world knows (gather,
cook, mend, build a hut), their household's trade (the smiths know smithing), a few things from elsewhere (an elder who once saw a
mill), and awareness of what their village has. A child learns from its household and from what it sees growing up (09 §2c).

### 4b. How a farmer knows how to farm

Nobody in a seeded world works out farming from nothing: they were raised in it. A farming household's members **know how** to sow,
tend, reap, thresh, keep and yoke oxen and plough, because that is their seeded upbringing (D4-21), and their **system prompt says
so in world terms**, from their knowledge record: "You know how to sow and tend barley and beans, reap and thresh, keep and yoke
oxen, and plough." The turn prompt then shows which of these can be done today (§2). The question "how would they ever figure it
out" arises only for what is **new to them**:

| Path | How it works |
|---|---|
| **Doing it** | making or building something once makes the agent remember how; practice raises the skill (02c §5) |
| **Seeing it** | watching a neighbour plough with oxen gives awareness; with enough watching, a rough know-how |
| **Being taught** | someone who knows teaches them, present, over days; youth learn fast and keep it (D4-19) |
| **Reading** | a written recipe or method, with literacy (02h) |
| **Trying what you have seen** | an agent may **attempt** something it is aware of but has not been taught, at novice skill: more materials, a chance of failure (the materials spoiled), and success teaches it. This is the bounded form of trial and error: you can only try what you know exists |

**Near misses** help planning: the turn prompt may add, within its budget, what an agent could make here if it had one more input
("you could make a blade with 4 more copper").

### 4c. The mechanics, concretely (counts proposed, to calibrate)

**A technique** is anything an agent might know how to do beyond the basics everyone knows: a recipe (make a blade, cure meat),
a blueprint (build a hearth, a kiln), a gathering method (fish with a net, quarry stone), a working method (plough with oxen, sow
barley, operate a mill), animal handling (yoke oxen, break a horse), and skills of the mind (reading and writing). Each technique
names its verb and object, what it needs (inputs, tools, a fitting or building, a site, a season), its work units and its result.
The basics (walk, carry, give, talk, forage, cook a meal, mend, build a lean-to) need no technique.

**Four levels, not a continuous score.** For each agent and technique, the engine keeps a level and a few counts:

| Level | Means | The agent is told |
|---|---|---|
| **aware** | knows it exists | the name, what it is for, and **how it heard of it**: "ploughs (you saw Torvald make them)", "kilns (Wynn told you of them)", "millstones (you read of them in the almanac)". Cannot attempt it |
| **rough idea** | knows what goes into it and where it is done | "pots: clay and fuel, fired in a pit or a kiln" (no amounts). May attempt it, at a cost and a risk |
| **capable** | knows the method, not yet sure of hand | the full card: "pots: 3 clay, 2 fuel, a firing pit, 2 units; at your level you use about 4 clay and it works about 3 times in 4" |
| **known** | knows it | the full card at its normal cost, under "Your crafts", with a skill word (novice, competent, skilled, master) |

Skill (how well and how cheaply) stays 37.2's continuous practice curve in the engine (02c §5), shown as a word.

**How an agent moves up** (counts, to calibrate):

| Path | What happens | Moves the agent |
|---|---|---|
| **Being told of it** | someone mentions it, or the agent reads of it | to **aware** |
| **Seeing it done** | present at the site or in the room when someone does it (perception records it) | to aware at once; to **rough idea** after 3 sightings; never beyond by watching in passing |
| **Watching on purpose** | `watch {person}` for the day, working beside them | each day counts as 2 sightings; to **capable** after 3 such days |
| **Being explained it** | `explain {to, technique}` in the talk step, by someone who knows it | to **rough idea** |
| **Being taught** | `teach {to, technique}`, accepted by the learner, both present, one day (teacher about 2 units, learner about 4) | **one session to capable** (a youth: to known); practice does the rest |
| **Reading a method** | `read {document}`, literate, a written method made by someone who knows it | to **capable** |
| **Trying** | `make` or `build` with a rough idea or capable | success: the result, and a step toward the next level (2 successes from rough idea to capable, 2 more to known); failure: the inputs are lost, and 2 failures count as one success |

Trying costs more at lower levels: with a rough idea, inputs x1.7 and success about 1 in 2; capable, inputs x1.3 and about 3 in 4;
known, normal inputs and no failure (skill then sets yield and time).

**What "trying" means.** Agents never compose recipes. The call only names the technique, from the lists in the agent's prompt:

`{"do": "make", "what": "pot", "qty": 2}` or `{"do": "build", "what": "hearth", "at": "<lot or room>"}` or
`{"do": "work", "what": "plough", "at": "<plot>"}`

The engine takes the inputs from what the agent carries (or its house's stock, at its house), checks tools, workplace, site and
season, and either does it or **refuses, saying exactly what is short**, at no cost:

> Refused: pots need 2 fuel; you have 1. / Refused: you have no kiln here (you know of Mora's, at the Hollow). / Refused:
> ploughing needs a yoked ox; you have none. / Refused: milling needs a mill; there is none at Barleyfield.

So a rough idea tells the agent what to gather and where to go, and a refusal teaches the amounts. Choices a technique really has
(which plot, which room, which grain) are named parameters in its option line.

**What the agent sees** (within the budget):

> Your crafts: smithing (skilled): blades, knives, hoes, ploughshares; carpentry (novice): stools, handles.
> You have a rough idea of: firing pots (you saw Mora fire them three times).
> You know of: ploughs (you saw Torvald make them); kilns (Wynn told you of them).
> Today you could make: a knife; a blade, with 4 more copper.

**Is teaching worth it, and will agents do it?** One session costs the teacher about a third of a day and saves the learner
several days of watching and the materials wasted in trying. So teaching pays where the teacher gains from the learner's skill: **a
household teaching its own** (its labour becomes more productive: this will be most teaching, as it was historically), **an
apprentice** (labour at the master's forge), **payment** (a price below what the learner saves), or **duty** (a guild's or a
village's rule). It does not pay where the learner becomes a competitor, which is why masters keep secrets and guilds form.
Whether LLM agents teach readily, refuse or charge is behaviour to measure: run 2 suggests they give too readily rather than too
little.

**Two worked examples.**

- *Watching.* Cela lives next to the potter. She sees Mora fire pots three times: a rough idea. She tries: it takes 1.7 times the
  clay, and it cracks. She tries again and it holds (two failures and a success: one step short of capable). One more success and
  she is capable, two more and she knows it. She paid no one; it cost her clay, fuel and days.
- *Teaching.* Eoin (a youth) is taught smithing by Torvald, who wants a forge-hand: one session, and Eoin knows it. Torvald spent
  2 units and gained an apprentice whose skill grows twice as fast while he works at Torvald's forge. Torvald
  could have refused, or charged Eoin's household.

### 4d. Where an agent's knowledge shows

Knowledge is written by the engine (not the agent's notes, which are its own words). Three places, by how often it changes and how
much it matters today:

| Where | What | Size |
|---|---|---|
| **System prompt** ("What you know how to do") | every technique the agent **knows**, as names grouped by trade with a skill word; then its **rough ideas** and what it **knows of**, as names with their source in brackets. Rebuilt when its knowledge changes (rare: a few times a run), as cybertron 1 rebuilt system prompts on a change | names only; past a budget, the least used and oldest awareness drop out of the prompt (they stay in the store) |
| **Turn prompt** ("Today you could") | what it can do **here and now**, with the choices it has, plus a few **near misses** ("a blade, with 4 more copper"; "pots, at Mora's kiln at the Hollow") | budgeted, most useful first |
| **Look-up** (in the talk step, like opening a note) | the full card of any technique it knows anything of: inputs and amounts, tools, workplace, season, work, its level, how it learned it | on request, shown at once |

So a smith away from the forge still sees "smithing (skilled): blades, knives, hoes, ploughshares" in its system prompt, and today's
options show where it can use it ("at your forge, at the Hills"). Nothing is listed in full unless asked for.

### 4e. How telling is detected

Free speech cannot be parsed for meaning reliably, so the engine uses two cheap, deterministic rules and two explicit actions:

1. **Mentions make awareness.** Every technique, place, person, building and law has a canonical name and a few aliases. When an
   agent's message (said or told, in the talk step) **mentions a name the speaker knows of**, every hearer who did not know of it
   becomes **aware** of it, with the source "told by <speaker>". String matching, no model call. A passing mention ("we could use a
   mill") is enough, as in life; a speaker cannot spread what it does not know of itself.
2. **Messages can carry what they are about.** The message schema has an optional `about` field listing names (the speaker's
   prompt shows the names it may use), for agents that want to be sure; it gives the same awareness.
3. **A rough idea needs `explain`.** Knowing what goes into a thing and where it is done is passed only by `explain {to, technique}`
   (talk step, free, the speaker must know it). The explanation's words are the speaker's own; the engine records the level.
4. **Capability needs teaching, reading or practice** (§4c), all explicit actions.

**If agents do not bother:** a technique mentioned only loosely in words is still in the hearer's memory of what it heard (the
recent rounds), so the model knows of it for a while even if the engine did not record it; rule 1 catches most mentions anyway,
because names are what people use. **Asking:** a hearer can ask in words ("will you teach me to fire pots?"), or make it a visible request with `offer {to,
give: <a payment or nothing>, get: teaching of <technique>}`; the other's prompt shows "Eoin asks you to teach him smithing".
Teaching happens only if the teacher chooses `teach` and the learner accepts that day: the teacher's choice, and its leverage.

The same two rules (mentions and `about`) carry testimony about places, people, claims and laws (02_perception's testimony), so
one mechanism spreads every kind of awareness.

### 5. The manual: only common knowledge

A short, free look-up of what everyone in the world knows: how meals, hunger, the cold, travel, the day and the seasons work, how
to talk and trade. Not recipes or blueprints the agent has not learned. (cybertron 1's manual and look-ups, ported with their
budget and trimming.)

### 6. No blind crafting

Minecraft's original crafting grid let players try combinations, and most players learned recipes from a wiki outside the game.
Agents would learn little from blind trials and would waste actions on them; their own real-world knowledge would mislead them
where our recipes differ. So: an agent can only make what it knows how to make. **Invention** (a skilled practitioner, given time
and materials, works out a new recipe within their trade) is a later option, tied to the frontier and eras (37.5).

## Why

- Prompts stay small however large the recipe list grows.
- Knowledge becomes a resource with a place, holders and a cost to move, like everything else in the world: a source of
  specialisation, dependence and leverage (scenario_design §1).
- Agents are never asked to guess.

## Alternatives considered

1. **A manual of every recipe and blueprint** (cybertron 1's manual): too long for the prompt, and makes knowledge free and
   universal, removing the specialist's leverage.
2. **Blind discovery** (try combinations): costly and uninformative for agents (§6).
3. **Everything shown at the workshop to anyone present**: simpler, but anyone becomes a smith by standing at the forge.

## Open questions

1. The basic set everyone knows (37.2: which recipes are basic).
2. How long teaching takes, and whether watching alone can teach (and after how many times).
3. Whether written recipes need literacy (02h says yes) and how a recipe document looks.
4. How awareness shows in the prompt (a line "you know of: ploughs (the smith at Millford)").
5. Invention: later, or never?
6. The counts in §4c (sightings, days, successes per level; the cost and chance of trying), to calibrate in the first runs.
7. Whether a technique has prerequisites (pottery before a kiln) or tiers within a trade.

## History

- 23 Oct: proposed (37.4, with Zach), after Zach asked how agents can know what they can do and build in a world with many
  possible tools and buildings, and whether to use manuals or Minecraft-style discovery.

- 23 Oct: Zach: remembering what you once built, and being told automatically what you can build, are good; how would a farmer
  ever know how to farm? Added §4b: farming is known from upbringing and said in the system prompt; for new things, doing,
  seeing, teaching, reading and attempting what you have seen at novice skill; near misses in the turn prompt.

- 23 Oct: Zach asked how each path works materially. Added §4c: the per-agent technique record (aware, know-how `k`, skill),
  each path as an action or event with its gain and cost, what the agent sees, and two worked examples.

- 23 Oct: Zach asked what trying means if the agent does not know how: what call, which resources, what it selects. Added to §4c:
  the call only names the technique; the recipe is the world's; the agent's recipe card grows with know-how (aware, rough, good,
  known); the gamble is waste and failure, not composition.

- 23 Oct: Zach: a few discrete levels rather than a continuous score; awareness says how the agent heard of it; refusals say
  exactly what is short; does it cover enough kinds of action? §4c rewritten: techniques cover recipes, blueprints, gathering and
  working methods, animal handling and literacy; four levels (aware, rough idea, capable, known) moved by counts; the source of
  awareness in brackets; refusals name the shortfall ("you have no mill here").

- 23 Oct: Zach: where should what an agent knows but cannot do here show (system prompt, a note, a list)? how would the engine
  detect that telling happened? Added §4d (system prompt lists known crafts and awareness by name, rebuilt on change; the turn prompt
  shows today's options and near misses; full cards by look-up in the talk step) and §4e (mentions of known names make hearers aware,
  an optional `about` field, `explain` for a rough idea, `learn` as a visible request; the same rule carries all testimony).

- 23 Oct: Zach: is teaching economically viable, would agents do it, should it take fewer rounds? Teaching became one session (to
  capable; a youth to known), the learner accepting; added when teaching pays (household, apprentice, payment, duty) and when it
  does not (a competitor), as behaviour to measure.

## Sources

38.02 (perception), 38.06 (actions), 09 §2c (childhood memories), 02c §5 (skills, apprenticeship), 02h (knowledge as documents,
literacy, libraries), 02i (blueprints and parts), cybertron 1's context module (manual, look-ups, budgets).
