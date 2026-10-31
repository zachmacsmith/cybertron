# 38.37: Everything an agent is shown: inventory, origins, what it does to them, and a redesign

Session 37.4, 31 Oct 2026. Asked by Zach: "Dig into every single thing currently in the system prompt or daily notes, why it is
structured like this, where it traces back to, and if we could be better serving these purposes with a different design that
scales better with the complexity of the world" ... "showing them enough information to understand the world, but not to bias them
too much and hand hold them into acting in a certain way". Proposal from it: docs/cybertron2/proposals/agent_view.md.

Evidence: runs/d1_duo (D4-61 run, 10 days, 14 people; 324 replies with the journal on). Code: cybertron2/engine/prompt.py
(`system_prompt`, `turn_prompt`, `talk_prompt`, `memory_prompt`, `fuse_prompt`, `lighten_prompt`), knowledge.py (`crafts_lines`,
`options`), perceive.py (what was seen). A full example: Lucy's first decision, system text and message, is reproduced by
`python -m cybertron2.engine context runs/d1_duo d0.decide.Lucy.1`.

## 1. How a call is put together

- **System text**: built at the start of each agent's stretch of days (3 days, staggered), then frozen for the stretch (D4-27,
  converse.py). Sent with every call of the stretch; cached, so its repeats are cheap in money but not in the model's attention.
  Lucy's: 14,837 characters (about 3,700 tokens).
- **Messages**: one per call: the morning's decision (opening or not), talk replies, a lighten call when overloaded, night and road
  calls, the end-of-stretch memory. Each call also carries the whole conversation so far (earlier messages and the agent's own
  replies, D4-26, D4-27).
- **Not seen by Zach until now** because `turns.jsonl` keeps only the message (its `prompt` field) and the chronicle reads that;
  the system text was kept only inside the model call until the journal (R1, 24 Oct) stored it. Runs before 24 Oct have no copy.

Sizes (characters):

| Part | Lucy d0 (opening) | Lucy d1 | Odo d4 (Haiku, append) |
|---|---|---|---|
| System text | 14,837 | (same) | 14,891 |
| of which: the verb list | 7,024 | | |
| of which: How life works | 2,703 | | |
| of which: reply format | 1,979 | | |
| of which: What you know how to do | 1,448 | | |
| Message | 3,981 | 5,564 | 7,443 |
| of which: Your crafts today | 840 | 2,247 | 767 |

## 2. Inventory: every part, why it is there, where it traces back to

Legend for the last column: **W** world (what is there, as perceived), **R** rules (how the world works), **K** know-how, **C**
computed for the agent (the engine works something out on its behalf), **F** form (how to reply).

### 2a. The system text

| # | Part (as built) | Why it is there | Traces back to | Kind |
|---|---|---|---|---|
| S1 | "You are Lucy, a grown adult, of the Fenwicks in Stannick. Its head is Jory. By trade: ..." | who one is; stage words, not ages | D4-19 (stages), D4-21 (seeded society) | W |
| S2 | The home village in a line (houses, land, beasts, the crafts its people know) | repute: what the village is known for | D4-33 | W |
| S3 | "Your people": every person one knows, the relation, where they live, dead ones marked | kin and acquaintance from the family tree | D4-21; seeing.md §5 "relationships" | W |
| S4a | A day: plan, talk, work; units by season, youth/elder caps; "Any units you do not use are wasted" | the day's shape and the budget | cybertron 1 (scenario_design §3 keeps "wasted": Haiku acted half as much without it); D4-17 | R |
| S4b | Eating: the ration, the order one eats from, the cold, hunger stages | survival rules | cybertron 1's rules text; knowledge.md §5 "the manual: only common knowledge" | R |
| S4c | Food in meals a unit, for every food, raw and cooked; what spoils fastest; a store keeps food N times better | exact food values | D4-24's "every rule's number comes from the physics" (prompt.py docstring) | R (numbers) |
| S4d | Fuel as heat a unit; what a hearth needs; spaces warmed; camp and open fires | the heat system (Package F) | D2-156 to D2-161 | R (numbers) |
| S4e | Buildings are what is in them; who can build what; disrepair | buildings from fittings | D4-34 | R |
| S4f | What is whose: claims, use is seen, theft, households, hosting, joining, founding, claiming | holding and membership | D4-36, holding.md | R |
| S4g | Knowing how: levels, watching, explaining, trying, being taught | how people learn | knowledge.md §5 | R |
| S4h | What you notice: the morning's notice, one thing attended | the two channels | seeing.md §3c | R |
| S5 | Other places as known, roads, a night out, carry limits, every good's weight | travel and weight | D4-35, D4-47, D4-32 | W, R |
| S6 | "What you know how to do": 40 crafts "everyone knows" by their long names; known crafts with a skill word; capable, rough, aware with their source | one's know-how | knowledge.md §4d (names only, grouped, with a skill word) | K |
| S7 | "What you can do": every verb with its argument syntax and a line on it; under gather, work, make and build **every craft the agent knows anything of, aware ones included**, with tool multipliers (bare hands x0.25, a copper tool x2), the fitting, materials and work for buildings; "ways" (modifiers) | the verbs and their exact syntax; the craft words to use | D4-24 (verb registry, cybertron 1's action_registry); 37 growth rules "concrete options with exact syntax" (from cybertron 1's institution role cards) | F, K (and a manual) |
| S8 | Reply format: why, actions, tell, say, explain, offers, attend, note, pin, forget, open, look_up, memory | how to answer | cybertron 1's reply schema; notes.md; seeing.md | F |

### 2b. The morning message

| # | Part | Why | Traces back to | Kind |
|---|---|---|---|---|
| M1 | "What you remember": seeded history and customs (opening only) | the past one was born into | D4-21 | W |
| M2 | "Your memory" (rewrite) or the last six stretch memories and the engine's marked events (append) | continuity across stretches | D4-28, D4-61 | own words |
| M3 | "Now": season, day, days left, weather, units today, private messages | the day | D2-99; D4-17 | W, R |
| M4 | "What happened yesterday": what one did (results), said, heard | outcomes of one's acts | cybertron 1's last rounds; seeing.md | W |
| M5 | "What you saw yesterday": felt, learned, concerned, stood out, attended (in detail), in passing | perception in tiers | seeing.md §2, §3c; noticing.md (D2-85, D2-102, D2-115) | W |
| M6 | "This morning": dawn lines (arrivals, births told) | the night's news | D2-4, D2-97 | W |
| M7 | "Here": who is here (pregnancy, children shown); arrival lines; each parcel with its cover, holder, fence, **"here one can ..." (the crafts this kind of ground allows, that one knows)**, how bare as one has seen; buildings with fittings and holders; roads; things lying about | the place | D4-35, D2-97, D2-99, D2-116, D4-47, D4-50 | W (the "here one can" list is K by place) |
| M8 | "You": hunger, what one carries and its weight; partner, pregnancy, the household's children with **how to care for them (syntax)**; beasts as last known; one's house: condition, door, fire, sleepers, store, **"food worth N meals; those who eat from it eat about K a night; the fire takes X heat"** | oneself and one's household | D4-32; birth_and_death "What agents see"; beasts_known | W, C (the meals and nights) |
| M9a | **"Today you could"**: verb, craft, places, units; **cut at 10 entries in the order of the crafts table**; buildings never | what is possible here and now | knowledge.md §2 and §4d ("budgeted, most useful first": built without the ordering) | **C** |
| M9b | **"Not yet"**: up to 4 near misses, in table order, with what is short | near misses | knowledge.md §4d | **C** |
| M9c | "What you know how to do" again, **every day after the first of a stretch** (because the system text is frozen) | knowledge that changed mid-stretch | prompt.py (`if not opening`) | K (repeat) |
| M10 | Offers open here | trade | agreements.md | W |
| M11 | Agreements, what is owed as one knows it | debts | D4-37 | W |
| M12 | "As you last saw them": beliefs about elsewhere, dated | elsewhere | D4-35, D2-4 | W |
| M13 | Notes: the pinned one in full, titles of the rest | the agent's own | notes.md | own words |

Other calls: the talk message (what was said, offers, opened notes, looked-up cards; "give your whole plan again"); lighten (too
heavy to set off, D4-32); the night and road calls (D2-84: senses, holdings, choices with their meanings); the meeting on the road;
the memory request (D4-61).

## 3. What it does to the agents (d1_duo)

1. **The menu steers the day.** Of 1,244 gather, work, make and build actions, **1,079 (87%) were on that day's "Today you could"
   list**. Most of the 165 off it were crafts the cut at 10 left out (care 71, milk 25, grind 13, dung 12, reap 12, bread 11).
   Nobody built anything in 10 days; `make` was used 34 times. What sits early in the crafts table is what gets done.
2. **The system text is a manual, and agents optimise against it.** 18 of 324 replies plan with its multipliers: "The tool is in
   my hand at last: felling runs at x1 now, not x0.25, so two units at the Gill should bring in ~5.6 timber"; "With a tool x1 or
   more vs bare hands x0.4, 5 units today could knock off 5 to 7"; "Hay cut bare-handed is slow (x0.3 of a unit)". These are
   things a person would come to know by doing them; here they are handed out on day 0, to everyone.
3. **Pull does not happen.** `look_up` (full craft cards on request): **0 of 324 replies**. Whatever an agent needs must be in
   front of it.
4. **Vocabulary is not the problem.** One refusal of 80 was for a wrong word ("'fell' is not something you work"); the rest were
   the world's state (picked bare, no crop, out of notes, out of messages).
5. **Each craft is shown up to five times**: S6 (long name), S7 (reply word, with a card), M7 (by place), M9a or M9b (today), M9c
   (long name, again each day). The reply word and the long name are never put side by side.
6. **The system text grows with the data, not with the agent.** 47 of 63 crafts are basic (everyone knows them, D4-33's awareness
   only gates 16), so every agent carries every basic craft's card. S7 is 7,000 characters at 63 crafts and grows linearly with
   each craft, modifier and verb a package adds; S4 grows with each mechanic; S3 with the population.

## 4. Against the designs it came from

- **D4-24** (decided): "agents come to know them in the world ... not from a complete manual". S7 is very nearly the complete
  manual for every basic craft.
- **knowledge.md §4d** (discussion): the system text was to hold names only; full cards only by look-up; "Today you could" budgeted
  "most useful first". Built: cards in the system text, no ordering, look-up unused.
- **knowledge.md §3** (discussion): "the basics (walk, carry, give, talk, forage, cook a meal, mend, build a lean-to) need no
  technique". Built: 47 basic crafts, including baking in an oven, milling at a water mill, building a granary.
- **seeing.md §5** (discussion): "Long rule text in every prompt: keep the short common knowledge, move detail to look-ups". Built:
  2,700 characters of rules with the physics' numbers.
- **prompts.md** (spec): "engine numbers appear only where a person would count (goods, days, units of work)". Multipliers and
  heat values are not things a person counts.
- **The 37 growth rule** "concrete options with exact syntax, never as rules of a game" came from cybertron 1's institution role
  cards (31_institutions: a role's 2 to 4 decisions with exact syntax made offices usable). It argues for exact syntax; it does
  not argue for the engine choosing the options.

## 5. The tension

Usability against bias. cybertron 1 showed concrete syntax raises uptake (Haiku did half as much without the "wasted" line; role
cards made offices used). d1_duo shows the same force cutting the other way: a computed, capped, ordered menu decides 87% of the
work. A menu is harmless only if it is complete and neutral; this one is neither, and no menu is neutral about what it leaves out.
**What would show the redesign is wrong:** with the menu gone, agents waste many more units on refusals (above about 15% of units,
say), or fall back to a narrower set of crafts than now, or Haiku stops acting. The test in §7 measures exactly these.

## 6. A redesign (proposal: proposals/agent_view.md)

Principles:

1. **The engine shows the world and the rules a person living there would know; it never works out choices for the agent.** No
   "Today you could", no "Not yet"; a refused act says why (already so). Perceived state carries what matters: each field's stage,
   what lies where, what one carries, the store.
2. **Each thing once.** A craft has one entry; a rule one line; the place shows what its ground allows.
3. **Detail follows how well one knows a craft, and stops at know-how.** Skill and its effects are never told; they show in
   outcomes ("You felled 0.7 timber with your bare hands"), in what one sees others get, and in what people say.
4. **A fixed grammar of action kinds** instead of a verb manual: about eight kinds, each with its reply form, the same size in any
   world.
5. **Common knowledge only**, short, in words; numbers only where people count (meals, units, days, weights).
6. **Stable things in the system text, today's world in the message**; a change in what one knows is said once, in the message.
7. **Lists that grow with the world are budgeted by closeness**: kin, places, crafts known of, beliefs.

The craft entries by depth (principle 3):

| One's relation to the craft | Shown | Example |
|---|---|---|
| never heard of it | nothing | |
| knows of it | the reply word and the long name, and how one knows of it | `plough`: ploughing with a yoked pair of oxen (you have seen the Wynns at it) |
| a rough idea | plus where it is done and what goes in, without amounts | `charcoal`: burning charcoal; timber, in a stack in the open |
| capable or knows it (basic crafts included) | plus amounts, what comes out, and that it needs a tool or beasts, and a skill word | `bread`: baking bread at a hearth; 10 flour and 1 timber make 10 bread, 1 unit; you: competent |
| long practice | the same, with the skill word risen | `reap`: ...; you: better than most |

No multipliers at any level. "Needs a tool" or "slow by hand" is know-how and stays; "bare hands x0.25, a copper tool x2" goes.

The action kinds (principle 4; each a sentence and its form; the craft words above plug into "what"):

| Kind | Form |
|---|---|
| Take from the land | `gather {what, at}` |
| Work land, crops, beasts, people in your care | `work {what, at, item?}` |
| Make from what you have | `make {what, qty?}`, at the fitting it needs |
| Build or fit out | `build {what, at}` |
| Goods: move, give, take, leave, hide | `move`, `give`, `take` |
| Dealing: offers, accepting, releasing, hosting | `offers`, `accept`, `release`, `host`, `grant` |
| Household and family | `join`, `admit`, `found`, `name`, `order`, `partner`, `try` |
| Going elsewhere | `travel {to, on trouble?, ...}` |
| Learning | `watch`, `teach`, `learn`, `explain` |
| Force | `attack`, `guard`, `fire` |

Each verb's full argument list stays in the reply schema the model is given, so exact syntax is not lost; the prompt gives one
line a kind and the verbs in it.

Size: about 1,000 characters for the kinds; about 70 characters a craft one can do (47 basic crafts: about 3,300; fewer if Zach
makes fewer crafts basic, a world-design choice scenario_design §1 favours: "restricted access so groups need each other"); 40 to
60 characters a craft known of. Against today's 7,024 + 1,448, and the 2,247 repeated in each later message.

What else would change:

| Part | Change |
|---|---|
| S4 How life works | cut to common knowledge in words: the day and units, eating and the cold, fire, what is whose, how people learn, what one notices. Food and fuel values only as meals and nights where a person counts; the rest learned |
| S6 + S7 | replaced by the craft entries by depth and the action kinds |
| M7 "here one can ..." | kept: it is the ground's affordance, general, filtered by what one knows; the main place where "what can I do here" is answered |
| M8 "food worth N meals; eat about K a night" | an open question: it is arithmetic on what one sees (C, mild). Keep or drop by test |
| M9a, M9b | dropped |
| M9c | replaced by one line when knowledge changes: "Since the stretch began you learned: ..." |
| S3 kin, M12 beliefs, S5 places | budgeted by closeness when long (household, close kin, those met lately; then by household) |

## 7. Test before deciding

The duo world, 10 days, about $34 an arm (or a cheaper cut of 6 days):

| Arm | System text | Message |
|---|---|---|
| A (as now) | as built | as built |
| B (fair menu) | as built | "Today you could" uncapped, buildings included, no table order |
| C (the redesign) | kinds + crafts by depth, short common knowledge | no menu; a knowledge-change line |

Read across arms, and against each other's seeds: units wasted on refusals (and lost to nothing); distinct crafts used; make and
build counts; whether chains complete (grain to flour to bread; felling to building; tool making then tool use); food and fuel at
the end; Haiku's share of acts; and a qualitative end-state reading (CLAUDE.md). If C's waste stays within a few points of A's and
its range widens, the menu and the manual were crutches; if waste jumps for Haiku only, Haiku may keep a fair menu (B) as it keeps
the memory queue (D4-61).

## 7b. What carries from day to day (Zach: "is everything cached until the next reset, or reconstructed each day?")

**As designed** (D4-27, converse.py): within a stretch nothing is rebuilt. The conversation grows: day 1's message and the agent's
reply, then day 2's message appended, its reply, and so on, with talk, lighten and night calls appended the same way. Every call
sends the whole conversation (the CLI session caches it). The system text and the schema are frozen for the stretch. At the
stretch's end the agent writes its memory (D4-61); the next day a new conversation opens with a rebuilt system text and an opening
message (what it has always known, its memory, yesterday's record, then the day). The detail of the old stretch is gone except
what the memory, the notes and yesterday's record keep.

**As it runs:** a conversation also restarts **whenever the reply schema changes**, because the schema leads the cached prefix
(converse.py: "a changed schema ... restarts it"), and **no memory is written at such a restart**. The schema carries lists of
what the agent knows (crafts known of, herds, the verbs available where it stands), so it changes often. In d1_duo, **22
restarts off schedule** among 13 agents in 10 days (Mabel 3, Warin 3, Roger 3), for example:

| Agent | Restart | What changed in the schema |
|---|---|---|
| Avice | day 4 | she heard of coin, copper tools, mining, smelting (four new crafts known of) |
| Mabel | day 4 | the Wynn oxen left with her: `drive` and the herd's name dropped out |
| Warin | day 7 | he heard of harness |
| Jory | day 9 | "the Moor cattle: 2 strays" appeared as a herd |

The opening message keeps yesterday's record, so a restart one day in loses little; one two days in loses a day's detail
(conversations, plans, reasons), with no memory written for it. The schema is also a second, unseen menu: its lists of craft
words and targets are what the model's reply is fitted to.

**Fix (in the proposal):** keep the schema constant for a run: the knowledge lists out of it (free strings; the verbs already
refuse unknown words, and the prompt carries the words). Restarts then happen only on schedule, and the schema shrinks.

## 7c. The verbs: the original design, and how far it drifted (Zach: "didn't we design the verbs to be the primitives?")

**The design** (proposals/verbs.md, 23 Oct, "ready for a decision", never decided as a list; its principle is D4-24): a short
closed grammar of about 24 verbs, each a kind of change on a kind of referent; all variety in their objects and parameters
(techniques, sites, people, settings, powers), which are data. Its rules against swelling: a new verb needs a new kind of change
and Zach's yes; settings on things one controls go through `set {thing, setting}`; every institutional act is a power through
`invoke`; households are institutions (`join`, `leave`, `found`). It budgeted the verbs at about 300 tokens in the system text and
techniques as names only.

**As built:** 34 verbs, plus 18 words that only night and road events accept (`defend`, `flee`, `hand over`, `alarm`, `push on`,
`go round`, `accompany` ...): 52 values of `do`. None of the additions went through a decision. What should have been data on a
verb became verbs:

| Built as its own verb | In the design |
|---|---|
| `host`, `grant`, `revoke`, `sleep`, `fire`, `order`, `withdraw` | settings: `set {thing, setting}` (a house's guests, where one sleeps tonight, a fire tonight, the children's work, an offer) |
| `admit`, `name` (heir, head), `release` | powers of an office or a creditor: `invoke` |
| `partner`, `part`, `leave_household`, `join` (households only), `found` (households only) | membership of any institution: `join`, `leave`, `found` |
| `learn` | the learner's side of `teach` (accept) |
| `drive` | `move` of a herd, or a `work` method on a herd |
| the 18 event words | existing verbs with the event's options (`flee` is `travel` or `leave`; `defend` is `guard` or `attack`; `hand over` is `give`; `alarm` is `say`; `push on`, `wait`, `turn back`, `go round` are `travel`'s `on trouble`) |

And the verb list in the system text carries every craft's card (tools, multipliers, materials) under its verb: 7,024 characters
against the design's ~1,200. The "action kinds" in §6 were only a grouping of the same verbs, not a fix; withdrawn. The fix is the
original grammar: about 22 verbs, objects and settings as data, the verbs' lines short, the crafts elsewhere by depth.

## 7d. The senses (Zach: "are senses not coming much into this at all?")

They are not, and the structure explains why. Per decision in d1_duo an agent reads about 22,800 characters (15,074 system,
7,759 message); **856 (3.8%) come through the senses** (what was seen and attended yesterday, what was seen elsewhere, the night's
news). "Your crafts today" alone is 1,488. Three reasons:

1. **Presence gives the node whole.** D4-35's rule shows everything structural at one's node exactly: every parcel, building,
   fitting, holder, fence, a home store to 0.1 of a unit. Senses (D4-48 signs, D4-53's noticing rule) only gate changes of state
   and things at a spot.
2. **Computed sections read the true state, bypassing the senses.** The menu says "work reap at the Infield" or "Not yet: work sow,
   but the Infield is sown as thick as it will take": crop and field states told with certainty, whether or not anyone noticed a
   sign. The "Here" line for a field does not show its crop at all; the menu is the channel. Lucy's d1 message never mentions the
   barley except through it.
3. **The knowledge stores are separate and partial.** What one has seen of bare land, of one's beasts, of things lying about, of
   one's home while away, of elsewhere: five stores, each with its own rendering, beside the direct reads.

## 7e. From the other end: what an agent has to know, and one general system for it

The information a person needs to act, whatever the world:

| # | What | How a person comes to know it | Changes |
|---|---|---|---|
| 1 | **Oneself**: body (fed, hurt, stage, with child), time to spend today, what one holds and can carry | feels it; certain | daily |
| 2 | **When**: season, day, weather | sees it; certain | daily |
| 3 | **Where**: the place, its parts and how they join, the ways out | sees it on arrival, learns it by going | rarely |
| 4 | **What is there and its state**: land and what grows, crops, buildings and what is in them, stores, beasts, goods lying | **senses**: sight, sound, smell, touch, by attention and work | constantly |
| 5 | **Who**: people present, how they look, what they are to one | sees them; knows kin | daily |
| 6 | **Whose**: claims and rights | seen, told, remembered | sometimes |
| 7 | **What happened**: one's acts and their outcomes; what others did; what was said | own results; senses; hearing | daily |
| 8 | **What is owed and planned**: agreements, offers, one's intentions | records, memory | sometimes |
| 9 | **How the world works**: common knowledge (eating, cold, a day's work) and know-how (crafts, by depth) | upbringing, watching, teaching, trying | slowly |
| 10 | **How to act**: the verbs and their slots | given once | never |
| 11 | **One's own mind**: memory, notes | written by oneself | by oneself |

Items 4 to 8 are **beliefs about the world**, each held with when and how it was learned. Today the engine has them as five
partial stores plus direct reads of the true state. **A general system:** one belief store per person, entries of (thing, aspect,
value, day, how known: saw, heard, did, worked it, always known); every channel writes to it (the senses through the noticing
rule; speech through mentions; one's own acts through their results, which also sense what was worked, D2-115; seeding); the
message is a rendering of it, by thing: what is here (fresh), one's own (house, beasts, fields), elsewhere (aged); the engine
reads the true state only for one's own body (1) and the day (2). Structure that anyone present sees at once (parcels, buildings,
people) goes in by a sure sight; states go in by signs. **Nothing is computed for the agent from the true state.**

What it gives: senses become the channel for nearly everything in the world, as D4-48 meant; asymmetries of information become
real (a farmer who works her field knows its crop; a neighbour may not); a new system adds things, aspects and signs, never a new
prompt section; the prompt grows with what one knows and where one is, not with the data. What it costs: a rebuild of perceive.py
and prompt.py's rendering around one store; a calibration of signs so that ordinary states (one's own field, one's own store) are
reliably known to those who work them; some agents will act on stale or missing beliefs (as people do).

## 8. For Zach

1. The principles in §6 (especially 1 and 3: no computed choices; no skill told).
2. Which crafts are basic (today 47 of 63): a world-design lever for how much each agent sees and how much people need each other.
3. Whether the store's "food worth N meals" stays.
4. Whether to run the three arms.
5. The schema fix (§7b): a constant schema, so conversations restart only at the end of a stretch. This one is a fault more than a
   design choice; it can go in before the arms, in all three.
6. Restoring the verb grammar (§7c): about 22 verbs, settings through `set`, powers through `invoke`, membership general, event
   choices as existing verbs.
7. The belief store (§7e): one store, every channel writing to it, the message rendered from it, nothing computed from the true
   state; the senses as the main channel.

*Current as of 31 Oct 2026.*
