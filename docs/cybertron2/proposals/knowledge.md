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
6. Attempting the seen-but-untaught: how much worse (materials, failure chance), and how many successes to learn it.

## History

- 23 Oct: proposed (37.4, with Zach), after Zach asked how agents can know what they can do and build in a world with many
  possible tools and buildings, and whether to use manuals or Minecraft-style discovery.

- 23 Oct: Zach: remembering what you once built, and being told automatically what you can build, are good; how would a farmer
  ever know how to farm? Added §4b: farming is known from upbringing and said in the system prompt; for new things, doing,
  seeing, teaching, reading and attempting what you have seen at novice skill; near misses in the turn prompt.

## Sources

38.02 (perception), 38.06 (actions), 09 §2c (childhood memories), 02c §5 (skills, apprenticeship), 02h (knowledge as documents,
literacy, libraries), 02i (blueprints and parts), cybertron 1's context module (manual, look-ups, budgets).
