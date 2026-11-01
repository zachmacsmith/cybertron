# 38.40: The agent's interface: a taxonomy of what it knows, how each kind reaches it, and how it scales

Session 37.4, 1 Nov 2026. Zach asked how the sensing work fits now, for a taxonomy of the kinds of knowledge and experience an
agent needs, how it lines up with the least-bias-most-expressive intersection (38.37), where the cached and the updating parts
split, how actions are chosen, and how to design it so it scales as the world grows, learning from cybertron 1's and cybertron 2's
failures. Builds on 38.02 (perception principles), 38.37 (inventory of the prompt), 38.38 and 38.39 (memory), proposals/seeing.md,
senses.md, knowledge.md, verbs.md, agent_view.md, lasting_memory.md (D4-64). A framework for discussion; nothing built.

## 1. The sensing work so far, and where it stands

| Piece | What it is | Status |
|---|---|---|
| Signs (D4-6, D4-48, D4-59) | every state of a thing shows itself as a bundle of possible signs: a sense, a chance, conditions, a knack | built for fields, crops, pastures, herds, buildings, people, sky, wild resources, roads (signs.py, 1,350 lines) |
| One noticing rule (D4-53) | own conspicuousness x visibility x presence x attention x the eye | built |
| Two channels (seeing.md §3c) | the daily notice (salient and relevant facts, by chance) and attending (one thing in detail) | built |
| Tiers of what others do (seeing.md §2) | concerns you, salient, a glimpse, attended | built |
| Acting senses (D2-115, D4-62) | whoever works a parcel senses it, its neighbours and the parcels passed on the way | built |
| What the observer brings (senses.md §1) | where one worked, sharpness, age, temperament, mood, knowledge (expert and lay readings), company | proposed, not built |
| Beliefs with an age (38.02 principle 3) | elsewhere, one's home while away, beasts, things lying, land | built as five separate stores |

**How it fits now:** the machinery is good and almost unused. Per decision in d1_duo, 856 of about 22,800 characters (3.8%) came
through the senses (38.37 §7d), because three things bypass them: presence shows the node's structure and one's stores whole and
exactly; the computed menu tells crop and field states with certainty; and the system text hands out the physics as a manual. The
taxonomy below is the frame that would put the senses where they were meant to be: the channel for nearly everything outside
one's own body.

## 2. The taxonomy

Seven kinds. For each: what it holds, how a person comes to know it, how sure it is, and what drives its size.

| Kind | Holds | Comes by | Certainty | Size driven by |
|---|---|---|---|---|
| **1. Self** | body (fed, hurt, tired, with child, stage); what one carries; one's time today (units) and voice (messages); one's standing (household, office, heir); one's own deals and offers | feeling and knowing oneself | exact or near (one knows one's hunger better than anyone looking) | constant |
| **2. Here and now** (perception) | (a) ambient: weather, light, season, the place's sounds and smells; (b) the place's layout and the ways out; (c) who is here; (d) the states of things here (crops, stores, buildings, herds, land, goods lying); (e) what others do; (f) what is said | the senses, by the noticing rule: ambient and conspicuous structure surely, states by signs, others' acts by tiers, one thing in detail by attention, what one works on by acting | by sense and sign; exact only for what one counts in hand or in a store one looks into | the neighbourhood, by salience x relevance, within a budget |
| **3. Remembered world** (beliefs) | everything in 2 once out of sight: places, one's home while away, beasts, people last seen, prices witnessed, things lying | 2, plus testimony (said by someone) | dated and sourced; may be stale or wrong | recency x relevance, within a budget; older only if kept in one's memory |
| **4. People and ties** | kin, household, neighbours known, what one thinks of them (reputation from what one saw and was told) | the seeded past (D4-21); meeting; witnessing; hearing | acquaintance is known; character is belief | closeness: household and kin always; others by how well known |
| **5. How the world works** | (a) common knowledge every adult has from growing up; (b) know-how: crafts by depth (aware, rough, capable, known) and a skill word; (c) lore and customs: kept lines (D4-64) and the seeded history | upbringing; watching, being taught, trying; being told | as held: lore can be wrong | (a) constant; (b) what one has learned; (c) one's places |
| **6. One's own mind** | the rewritten memory, kept lines, notes, the conversation of the stretch | one's own writing | one's own | age (memory length, places) |
| **7. Means of acting** | the verbs and their slots; the reply form; the results and refusals of one's acts | given once; feedback from the world | exact | constant (the grammar); feedback by day |

Two distinctions inside this answer Zach's questions:

- **Self against seen-by-others** (Zach: "they should have more info about themselves than others do from looking"). Kind 1 is felt
  and near exact; the same facts reach others only as signs in kind 2 ("Lucy looks pale and slow"). Today others see a person's
  hunger as a word for everyone present; with signs, some notice and some do not, and the person itself always knows.
- **Knowing someone against seeing them now** (Zach: "knowledge of the core entities around them ... but they shouldn't always see
  this"). Who lives in one's village is kind 4, acquaintance: stable, remembered, like knowing one's neighbours. Who is in front of
  one today is kind 2(c), perception. Where the Moor cattle are now is kind 3, a belief from when one last saw them. Today the three
  are one list read from the true state. In a hamlet the difference is small (everyone is seen daily); in a town it is everything.

## 3. Against the least-bias, most-expressive intersection

**Expressive** means an agent can say anything the world allows: it knows the grammar (7), the names of what it can act on (2, 3,
4 and 5b), and its own means (1). **Biased** means the engine has done the agent's thinking: chosen, ordered, or optimised for it.

| Kind | Needed to be expressive | Where bias creeps in | Rule |
|---|---|---|---|
| 1 Self | its means today, what it holds | arithmetic done for it ("food worth 15.5 meals, about 4 a night") | show what one feels and counts; leave the sums |
| 2 Here and now | the names of what is here, and the states it noticed | computed affordances ("Today you could ..."); certainty about states nobody noticed; lists ordered by the engine | the senses decide what is known; the ground's general affordance ("here one can clear, forage, ...") may stay, because it describes the kind of ground, not today's best move |
| 3 Remembered | names and last-known states, with age | silent refreshing; dropping or keeping for the agent | dated beliefs; the agent's memory decides what lasts beyond the budget |
| 4 People | who they are to one | engine-written judgments ("Wynn is friendly") | relations from the tree; character only from what one saw or heard |
| 5 How it works | (a) what any adult there would know; (b) the reply word and what a craft needs, for crafts one can do | numbers to optimise with (tool multipliers, yields), told skill, rules for systems one has not met | (a) the upbringing test (below); (b) names by depth, no multipliers |
| 6 Own mind | its own words | engine prompts that say what to keep | ask at fixed moments, say what for, never what |
| 7 Acting | the grammar and the slots; why an act failed | a menu of verb x object pairs; examples in the prompt that show a "good" plan | a closed grammar; refusals that say what is short |

**The upbringing test** for common knowledge (5a): a rule is in the system text only if any adult raised in that world would know it
without having met it this run, and getting it wrong is costly before it can be learned (eating, the cold, fire, what is whose, how
people learn, that work comes in units). Everything else is learned by doing, by watching, by being told, or is carried as
experience: seeded memories and kept lines ("Hard winters you remember, when the stores ran out" teaches more than "a hearth needs
4 heat a cold night", and it is memory, not manual). This is Zach's "less explanation and more just as memory and discovery": the
rules move into what seeded people remember and into customs, and the newborn generation gets them only if someone passes them on.

**How small can the system text be?** With the upbringing test, the verb grammar as designed (verbs.md: about 300 tokens), crafts by
depth (aware: a name; capable: a line), identity, and kin by closeness: about 1,500 tokens for a grown agent, against 3,700 now.
The risk is an agent that never learns a lethal rule in time; the test for it is the same three-arm comparison as 38.37 §7.

## 4. Cached against updating

The conversation of a stretch accumulates (D4-27): whatever is in the system text or the opening is in front of the agent all
stretch, and each day's message is appended. So:

| Layer | Holds (kinds) | When it changes |
|---|---|---|
| **System text** (frozen a stretch, cached) | 7 the grammar and reply form; 5a common knowledge; 5b know-how by depth; 4 kin and household; 1 standing | rebuilt each stretch |
| **Opening** (the stretch's first message, cached after) | 6 memory and kept lines; 5c the seeded history; 3 beliefs, as of now, by the budget; 2 the full picture of here | once a stretch |
| **Each day** (appended) | 1 body, means and deals as they are; 2 what is noticed today, **as changes** since the last message; 7 yesterday's results; 3 beliefs that changed; 5b and 4 changes ("You have learned of milling", "Avice has partnered with Gil") | daily |
| **When asked** | 6 the memory and kept lines (end of stretch); the talk step | at fixed moments |

Two consequences. **Deltas, not re-renders:** today every day's message re-renders the whole picture (7,759 characters a day in
d1_duo), three times in one conversation; within a stretch a day should carry what changed and what was noticed, and the opening
carries the whole (38.02 principle 5, "change is shown"). **Learning between caches:** what one learns mid-stretch goes in that
day's message as a change, and into the system text at the next stretch; nothing is reprinted daily.

## 5. How actions get chosen

The agent composes acts from: the grammar (7: verb and slots), the names it has (2, 3, 4: what is here, what it remembers, who it
knows), what it knows how to do (5b: the craft words, at its depth), and what it has (1: units, goods, voice). The engine supplies
none of the composition. It answers each act: done (with what came of it) or refused (with what was short: "you need a tool in your
hands"; "the Infield has a crop in it"). The results are the learning signal, and the agent's memory, notes and kept lines are where
the learning lives. The place lines' general affordance ("here one can clear, forage, hay ...") is the only standing hint, and it is
general: it says what this kind of ground allows of the crafts one knows, not what is ready or best.

## 6. Scaling: a bounded slice

The prompt must grow with the agent's neighbourhood and its knowledge, never with the world. Each kind needs a driver and a budget
from the day it is built:

| Kind | Grows with | Bound |
|---|---|---|
| 7 grammar | nothing (data on verbs, never new verbs: verbs.md rules) | about 22 verbs |
| 5a common knowledge | nothing (new systems add signs and lore, not rules) | the upbringing test |
| 5b know-how | what one has learned (time spent) | one line a craft one can do; a name a craft one knows of; the oldest awareness drops past a budget |
| 5c, 6 lore, memory, kept lines | age | the memory curve; places (D4-64) |
| 4 people | closeness | household and kin in full; others by how well known; the rest as "and N others of the village" |
| 2 here and now | the place's busyness | salience x relevance: concerns always, then the top of the rest within a budget; one thing attended; presence by proximity (same parcel or building, household, those one dealt with) and a count for the rest |
| 3 beliefs | how far one has been and how long | recency x relevance within a budget; beyond it, only what one's own memory kept |
| 1 self | nothing | constant |

So a new system adds entity types, aspects and signs (2), crafts as data (5b), lore (5c), and a verb's object or setting (7): none of
them adds a prompt section or a rule every agent must read.

## 7. What failed before, and the lesson each gives

| Failure | Where | Lesson |
|---|---|---|
| a dashboard of the state: one's house from the forest, everyone's whereabouts, every death | cybertron 1; 38.02 §1 | **one pipeline**: state reaches the agent only through a channel into beliefs; render beliefs, never state (body and day excepted) |
| memory one round deep, and agents told otherwise | cybertron 1 (review 20 §1) | say plainly what will be remembered, and make memory a fixed moment, not an option |
| scratchpads and notes used as status lines (87% of turns; 77% rewrites; 58% never read back) | cybertron 1; 38.38 | agents keep ledgers when the engine does not show their own state plainly; show self and deals plainly (kind 1) and notes free up for what the engine cannot keep |
| 145 actions; and in cybertron 2, 24 verbs designed and 52 values of `do` built, none decided | cybertron 1; 38.37 §7c | a closed grammar with rules against swelling, enforced: a new verb is a decision |
| a manual and menus: role cards made offices used; the menu decided 87% of the work; agents planned with the manual's multipliers | cybertron 1 (31_institutions); 38.37 §3 | exact syntax raises uptake, a computed menu takes the decision; give syntax and names, never choices or numbers to optimise |
| presence gives the node whole; the menu tells states with certainty; senses carry 3.8% | cybertron 2; 38.37 §7d | presence gives only what is conspicuous; states go through signs |
| five belief stores, each rendered its own way | cybertron 2 | one belief store (agent_view.md point 9) |
| the schema's lists change, restarting conversations 22 times and silently menu-ing the reply | cybertron 2; 38.37 §7b | a constant schema; names in the prompt, free strings in the reply |
| the whole picture re-rendered every day inside one conversation | cybertron 2 (7.7k a day) | deltas within a stretch, the whole at the opening |
| look-ups and opening notes almost never used (0 to 3 per 100 agent-days) | cybertron 2; 38.38 | push, not pull: what is not shown is not used, so the selection (salience, relevance, budget) is the design |
| Sonnet 5.5 never used an optional field in 1,255 agent-days | cybertron 2; 38.38 | anything that depends on an agent choosing to write reaches only some models: ask at fixed moments |
| dynamic content first broke the cache (72% of cost written, never read) | cybertron 1 (review 20 §2.2) | stable first, changing last; within a stretch only append |
| goals with scoring shown to agents | cybertron 1 | in-world aims only (scenario_design §3) |

And one check to build with it: **a leak audit**. For each act that succeeds, ask whether the agent could have known what it used:
a store it never saw, a crop state nobody noticed, a person it never met. Today the menu and presence would fail it everywhere; a
belief-rendered prompt should pass it by construction.

## 8. What this asks of Zach

1. The seven kinds as the frame for agent_view.md (the redesign), with one pipeline (state to channels to beliefs to render).
2. The upbringing test for common knowledge, and moving rules into seeded memory and customs.
3. Deltas within a stretch.
4. Presence by proximity and a count, for large places.
5. Order of work, if agreed: the constant schema (a fault); the verb grammar; the belief store with presence and signs; deltas;
   the small system text; then the three-arm test of 38.37 §7.

*Current as of 1 Nov 2026.*
