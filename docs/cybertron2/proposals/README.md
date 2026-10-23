# cybertron2 proposals: our working thoughts

Every idea about how the world should work, while we think it over, separate from the spec (which holds only what is decided).
One file per idea; any session may write one; talk about it on the board. Each file keeps a **dated history** of how the idea
changed, so the progression stays readable. When Zach decides, the decided parts go into the spec and DECISIONS.md, the file is
marked accepted or rejected with the reason, and it stays here. The **log** below records every idea's outcome, including those
decided or rejected in conversation before this folder existed.

| Layer | Holds |
|---|---|
| `spec/` | what is decided |
| `proposals/` (here) | what is being considered: one file per proposal, with its status |
| session notes (`docs/review/...`) | long analyses, models, run reports, work logs |
| the board | talk between sessions |

## Layout of a proposal

**Status** (discussion | ready for a decision | accepted: D-n | rejected | superseded by ...); **Owner**; **Summary**; **The
proposal**; **Why**; **Alternatives considered**; **Open questions**; **Affects** (the spec files it would change); **History**
(dated entries: proposed, revised and why, decided or rejected and why); **Sources**.

## Proposals

| File | Summary | Owner | Status |
|---|---|---|---|
| [seeing.md](seeing.md) | everything an agent is shown each round and how it changes; attention (concerns you, salient, a glimpse, one thing attended to in detail), feeling watched, observations from the state; templates first, an optional narrator per node and day; what is missing and what should go | 37.4 | discussion |
| [verbs.md](verbs.md) | the closed list of about 25 verbs always in the system prompt (force always shown), objects shown by knowledge and place, office verbs to holders; the possible space against the shown space; gaps (steal, damage, flee, yield, tend, bury, scout) | 37.4 | ready for a decision |
| [notes.md](notes.md) | private notes: up to 8, one pinned and shown, titles of the rest, opened in the talk step and shown at once; memory, not objects: never passed on except by telling, lost at death | 37.4 | discussion |
| [knowledge.md](knowledge.md) | what agents know they can do: few verbs on many objects, options computed from place and knowledge, know-how spread by teaching, apprenticeship and documents, a manual of common knowledge only, no blind crafting | 37.4 (37.2: content) | discussion |
| [law.md](law.md) | law as text taking effect through mechanical clauses on records, duties of office, and judgment only on disputes; Python as the clause implementation and a world setting; how law can still be captured | 37.4 (37.3 to review) | discussion |
| [farming.md](farming.md) | optional stages, crops from the sowing day, rotations, cattle, the harvest window, sowing work per seed | 37.2 | partly accepted: D2-11 to D2-18 |
| [tools.md](tools.md) | the tool set by dependence: hand tools with grades, plough, harness, saddle, carts, weapons, traps | 37.2 | accepted: D2-23 (details open) |
| [livestock.md](livestock.md) | one livestock system; herds, pasture, fodder, herding scale, the common herd | 37.2 | partly accepted: D2-6, D2-18 |
| [shelter.md](shelter.md) | houses, upkeep, breaks, the cold, the shelter ladder | 37.2 | partly accepted: H-5, D2-10 |
| [buildings.md](buildings.md) | buildings from parts: structures, rooms, fittings, scaling, storeys, limits | 37.2 | partly accepted: D2-3, D2-9 |
| [resources_and_goods.md](resources_and_goods.md) | the base resources, the lean first-world set and the pruning rule, unlocks, end uses | 37.2 | discussion (D2-10, D2-19, D2-23 accepted) |
| [economy_later.md](economy_later.md) | options kept out of the first worlds (armour, nets, boats, seed drill, irrigation, clay, iron, the press, ...) | 37.2 | deferred |
| [transport_and_lodging.md](transport_and_lodging.md) | the transport ladder, capacities, danger by edge and season, inns and hosts | 37.2 (37.4 the mechanism) | partly accepted: D4-9, D4-12, D2-4 |
| [exchange_and_money.md](exchange_and_money.md) | exchange at a node, coin, debts, credit, tolls | 37.2 | partly accepted: D2-1, D2-2, D4-17 |
| [information_economics.md](information_economics.md) | writing materials, documents, the information ladder, libraries, archives, maps | 37.2 (37.4 owns information/) | partly accepted: D2-7, D2-8 |
| [economy_plan.md](economy_plan.md) | the economy plan for cybertron2 (E1-E6, the first region) and society-scale layers | 37.2 | discussion |
| [fuse_events.md](fuse_events.md) | events with a detection time and a completion time; urgent calls for those who notice in time | 37.2 (37.4 owns conflict/, core/) | accepted in principle: D2-5 |
| [gates.md](gates.md) | boundaries with entry rules: names, passes, tolls, a keeper; admission in the talk step | 37.2 (37.4 owns conflict/) | accepted: D2-5 (details open) |
| [attacks_and_walls.md](attacks_and_walls.md) | attacks on people, buildings and nodes; walls multiplying defenders; the watch | 37.2 (37.4 owns conflict/) | partly accepted: D2-20 to D2-22 |

## Log of ideas and their outcomes

Newest first. Ideas decided or rejected in conversation before 23 Oct are backfilled from the 37.4 work log and DECISIONS.md.

| Date | Idea | Outcome | Where |
|---|---|---|---|
| 23 Oct | Deliberate misperception by the engine (a seeded wrong fact) | rejected (Zach) | [seeing.md](seeing.md) §4 |
| 23 Oct | Two channels: a daily notice of the most salient facts (templates, by chance and relevance) and attending (detail, model description); signs of shifts by salience and relevance | discussion (Zach's direction) | [seeing.md](seeing.md) §3c |
| 23 Oct | The engine keeps facts about the world as dated beliefs with a source; the agent keeps interpretations and plans | discussion | [knowledge.md](knowledge.md) §7 |
| 23 Oct | Opening a note shown only the next round | rejected (Zach): opening is a talk-step action, shown at once | [notes.md](notes.md) |
| 23 Oct | Every act at the node shown to everyone present (phase 0) | replaced in the proposal by attention tiers | [seeing.md](seeing.md) §2 |
| 23 Oct | What an agent sees; attention; observations; descriptions by templates or a model | discussion | [seeing.md](seeing.md) |
| 23 Oct | Teaching passes skill: a share of the gap between teacher and learner | in the proposal | [knowledge.md](knowledge.md) §4c |
| 23 Oct | The world grows by data on a few verbs; agents explore and learn it | accepted: D4-24 | [verbs.md](verbs.md), [knowledge.md](knowledge.md) |
| 23 Oct | The verbs (a lean set of 24) and what each agent is shown; force always shown | ready for a decision | [verbs.md](verbs.md) |
| 23 Oct | Detecting what was told by reading the meaning of free speech | rejected in the proposal: name mentions, an `about` field and explicit `explain`/`teach` instead | [knowledge.md](knowledge.md) §4e |
| 23 Oct | Know-how as a continuous score (0-1) | replaced in the proposal by four levels moved by counts (Zach) | [knowledge.md](knowledge.md) §4c |
| 23 Oct | Private notes with one pinned, the rest opened by choice; memory, not documents | discussion | [notes.md](notes.md) |
| 23 Oct | Knowing what you can do: few verbs, options computed from place and knowledge, know-how as personal knowledge | discussion | [knowledge.md](knowledge.md) |
| 23 Oct | Blind crafting (Minecraft's grid) for discovering recipes | rejected in the proposal, Zach to confirm | [knowledge.md](knowledge.md) §6 |
| 23 Oct | Sowing takes work per unit of seed; broadcasting or dibbling | discussion | [farming.md](farming.md) |
| 23 Oct | Crops counted from the day sown, the cold as the limit; five crops; rotations | discussion | [farming.md](farming.md) |
| 23 Oct | Options for later kept in the spec (spec/economy/later.md) | moved: the spec holds decided rules only | [economy_later.md](economy_later.md) |
| 23 Oct | Tool set by dependence, with traps, harness and saddle | accepted: D2-23 | [tools.md](tools.md) |
| 23 Oct | Two tool goods (tools, weapons) | superseded by the set by dependence | D2-23 |
| 23 Oct | One tool per activity (plough, axe, pick, sickle, spear) | rejected: single-use goods | D2-23 |
| 23 Oct | Hide armour, metal armour, nets, boats, the seed drill | deferred | [economy_later.md](economy_later.md) |
| 22 Oct | Optional farming stages, a harvest window, farming under way at day 0, hoe and ox plough only, labour on a curve, land pressure, seed kept, cattle on the farm | accepted: D2-11 to D2-18 | [farming.md](farming.md) |
| 22 Oct | The old engine's farming (yield follows the seed; two tends and nothing more) | replaced by optional stages and labour on a curve | D2-11, D2-15 |
| 22 Oct | Slash and burn and irrigation in the first worlds | deferred | D2-14, [economy_later.md](economy_later.md) |
| 22 Oct | Fuse events: whoever notices an event in time gets one urgent call | accepted in principle: D2-5 | [fuse_events.md](fuse_events.md) |
| 22 Oct | A combat-only interrupt phase, or several exchanges between the sides | rejected: one wave per event, for any event with a fuse | [fuse_events.md](fuse_events.md) |
| 22 Oct | Gates: an automatic entry rule at dawn, otherwise the keeper and the arrivals talk | accepted: D2-5 | [gates.md](gates.md) |
| 22 Oct | A separate pre-entry phase for walled nodes; admission as a work-step action | rejected: the dawn check and the talk step cover it, and the admitted arrival keeps its day | [gates.md](gates.md) |
| 22 Oct | Three kinds of attack; walls multiply the defence of those inside | accepted: D2-20 | [attacks_and_walls.md](attacks_and_walls.md) |
| 22 Oct | Walls as a fixed defence of their own | rejected: barely moves the odds against armed raiders, and makes a house a vault | [attacks_and_walls.md](attacks_and_walls.md) |
| 22 Oct | The watch: skips sleep, costs food, rotated; children may keep it | accepted: D2-21 | [attacks_and_walls.md](attacks_and_walls.md) |
| 22 Oct | Node raids only by riders or large parties (37.2) | rejected: any party may raid | D2-22 |
| 22 Oct | cybertron 1's personal fort (stone locked into a person's defence) | superseded: stone defends a building | D2-20 |
| 22 Oct | Both bronze and iron in the first worlds | rejected: a short metal ladder first | D2-19 |
| 22 Oct | Clothing as a worn stock from fibre | deferred: parked | D2-10 |
| 22 Oct | The inherited base resources, assumed rather than chosen | replaced by resources chosen by six tests and a bill of materials | [resources_and_goods.md](resources_and_goods.md) |
| 22 Oct | Stone as a later resource | rejected: stone restored for infrastructure | D2-3 |
| 22 Oct | The full production-chain catalogue as a build list | rejected for first worlds: the pruning rule and a lean set of about ten goods; the catalogue kept for later eras | [resources_and_goods.md](resources_and_goods.md) |
| 22 Oct | Template buildings with fixed functions | rejected: buildings from parts, rooms bookable, capacity that scales | D2-9 |
| 22 Oct | Large buildings and upper storeys without stone | rejected: they must have stone; building up costs more | D2-3 |
| 22 Oct | One livestock system, bred not made; wild herds | accepted: D2-6 | [livestock.md](livestock.md) |
| 22 Oct | Horses as a separate good from cattle | replaced: one livestock system, equipment gives the use | D2-6 |
| 22 Oct | Speech at a node: the square, rooms by access, private messages | accepted: D2-7 | [information_economics.md](information_economics.md) |
| 22 Oct | Wide reach costs more: rumour, then letters, then papers | accepted: D2-8 | [information_economics.md](information_economics.md) |
| 22 Oct | Hiding in a building | deferred | [information_economics.md](information_economics.md) |
| 22 Oct | Merchants left to emerge from delay alone | replaced: one merchant household with a cart is seeded | D2-2 |
| 22 Oct | The old-engine economy build plan (P1-P6) | superseded by the cybertron2 plan (E1-E6) | [economy_plan.md](economy_plan.md) |
| 22 Oct | Houses with upkeep and breaks; 30% straight to starving in the cold, no separate exposure | accepted: H-5 | [shelter.md](shelter.md) |
| 22 Oct | Agents told someone is missing ("not seen for N rounds") | rejected: the household saw the departure and remembers it | D2-4 |
| 23 Oct | Law as text with mechanical clauses on records, duties of office, judgment on disputes | discussion | [law.md](law.md) |
| 22 Oct | Holding as a recognised claim; the engine enforces possession only | accepted: D4-23 | spec/world/holding.md |
| 22 Oct | Plots split by a primitive, with a minimum plot size (37.1's question) | rejected: plots whole, holdings divided; viability is land per mouth | D4-23 |
| 22 Oct | The engine enforces a holder field (cybertron 1) | rejected: replaced by recognised claims | D4-23 |
| 22 Oct | A youth plays on a cheaper model for its first rounds | rejected: one agent, one model, for life | D4-20 |
| 22 Oct | Chapters with time skips for generations | rejected | D4-19 |
| 22 Oct | Ages in calendar years | rejected: life stages in rounds, named not numbered | D4-19 |
| 22 Oct | Agents not called on quiet days (event-driven calls) | deferred: everyone called every day in the first runs; the agent would decide its own quiet days later | 38.06 §5 |
| 22 Oct | Reflexes, fallbacks and policies as standing orders | deferred: routine first | D4-16 |
| 22 Oct | Money and credit move anywhere | rejected: coin is carried; debts move only as information | D2-1 |
| 22 Oct | A round as a work period, short hops acted on the same round | rejected: an agent would trade blind on arrival | D4-8 |
| 22 Oct | Half-day rounds, eating every two rounds | rejected: too slow and costly; a round is a day with a compressed calendar | D4-13 |
| 22 Oct | One night out cheaper than 1.5 food | rejected: 1.5 kept | D4-12 |
| 22 Oct | Riders ride and strike in one round (37.2, 02g §5b) | open: fuse events may make it unnecessary | OPEN C-5 |
| 22 Oct | Space retrofitted into cybertron 1 (board Post 2) | rejected: a new engine | H-1 |
| 22 Oct | A separate environment scheduler (37.4's draft `environment.py` on `wp/environment`) | rejected: one central scheduler on cybertron2 | D4-4 |
| 22 Oct | Speech heard a round late (phase-0 cybertron2) | rejected: a talk step at the node | D4-15 |
| 22 Oct | Places as single woods and meadows (phase-0 cybertron2) | rejected: a node is a village or valley with sites | D4-2, D4-11 |
