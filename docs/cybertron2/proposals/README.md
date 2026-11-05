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

**Status** (discussion | ready for a decision | accepted: D-n | rejected | superseded by ... | retrospective, accepted: D-n);
**Owner**; **Summary**; **The
proposal**; **Why**; **Alternatives considered**; **Open questions**; **Affects** (the spec files it would change); **History**
(dated entries: proposed, revised and why, decided or rejected and why); **Sources**.

**Retrospective proposals.** When Zach asks for something to be built straight away, in conversation, it is built first and written
down afterwards: a proposal with the status `retrospective, accepted: D-n`, saying what was built, why (his words and the problem it
answered), what else was considered, and what is still open, with a History entry dated the day it was built. Nothing built is left
without a proposal.

## Proposals

Rebuilt from the files on 5 Nov (status and owner as each file states them; 37.2's sweep).

| File | Summary | Owner | Status |
|---|---|---|---|
| [household_customs.md](household_customs.md) | a custom held by named households, not only by places | 37.4 | retrospective, accepted: D4-57; replaced by D4-64 |
| [led_beasts.md](led_beasts.md) | a beast one leads stays with one until let go | 37.4 | retrospective, accepted: D4-58 |
| [more_signs.md](more_signs.md) | signs for the newer systems (people, houses, woods, herds, travellers) | 37.4 | retrospective, accepted: D4-59 |
| [clearing.md](clearing.md) | clearing meadow, pasture or scrub into a field | 37.4 | retrospective, accepted: D4-60 |
| [memory_rewrite.md](memory_rewrite.md) | one memory rewritten each stretch, its length growing with age; weak models keep the queue | 37.4 | accepted: D4-61 |
| [day_route.md](day_route.md) | a day as one chain of parcels in act order, kept in the day's record | 37.4 | retrospective, accepted: D4-62 |
| [play_page.md](play_page.md) | a page for playing an agent: its exact context, and a form from the reply schema | 37.4 | retrospective, accepted: D4-63 |
| [agent_view.md](agent_view.md) | what an agent is shown: the world and its rules, not choices made for it; crafts by depth of knowledge; a constant schema | 37.4 | partly accepted: D4-78 (points 1 and 9, as a world setting); the rest in discussion |
| [lasting_memory.md](lasting_memory.md) | lines kept for good beside the rewritten memory; passed on with care; customs as seeded kept lines | 37.4 | accepted: D4-64 |
| [run_record.md](run_record.md) | the run as a journal (SQLite; JSON values; content-addressed prompts) of keyed requests and answers, with step commits and checkpoints; the runner as a resumable, idempotent, cancellable state machine; views: state at any step, exact agent context, map frames, history, Parquet export, the site; a human responder plays an agent with the same context (review 39.01) | 37.1 (37.4: engine code) | accepted: D1-1 to D1-5 (24 Oct; spec/record/). |
| [households.md](households.md) | membership, use and home as data agents change: admit and leave, grant use of a house, home derived, occupy an empty house (possession and a claim), build one from parts; the night follows use | 37.4 (37.2: building costs) | partly accepted: D4-36 (the principle); the open questions remain. |
| [place.md](place.md) | place as the foundation: every entity and event has a place; state partitioned by node; agent-facing code gets only a view of where the agent is (`Here`) and its own mind (`Mind`), never the world; only travel moves anything between nodes; static and canary tests | 37.4 | accepted in principle: D4-35 (the mechanism is part of the D4-34 rebuild). |
| [layout.md](layout.md) | the layout inside a node: parcels of one cover (forest, field, pasture, water, built ground...) with neighbours and a side; features (brook, road, well, seam); structures on built ground; movables on a parcel or in a room; attention, claims and land change on one model | 37.4 | discussion (23 Oct). |
| [parcel_graph.md](parcel_graph.md) | parcels as a graph of neighbours shaped by the land, each with a side and a height; no coordinates or walking; sensing along the way; attending to the village; an overview on arrival | 37.2 (37.4 owns places and perception) | accepted: D2-114 to D2-116 (24 Oct), amended by D4-62 (the day's route) and D4-98 (next door 0.3). ... |
| [seeing.md](seeing.md) | everything an agent is shown each round and how it changes; attention (concerns you, salient, a glimpse, one thing attended to in detail), feeling watched, observations from the state; templates first, an optional narrator per node and day; what is missing and what should go | 37.4 | discussion (23 Oct). |
| [verbs.md](verbs.md) | the closed list of about 25 verbs always in the system prompt (force always shown), objects shown by knowledge and place, office verbs to holders; the possible space against the shown space; gaps (steal, damage, flee, yield, tend, bury, scout) | 37.4 | ready for a decision (23 Oct; Zach likes the verb system; its principle is D4-24). |
| [notes.md](notes.md) | private notes: up to 8, one pinned and shown, titles of the rest, opened in the talk step and shown at once; memory, not objects: never passed on except by telling, lost at death | 37.4 | discussion (23 Oct). |
| [knowledge.md](knowledge.md) | what agents know they can do: few verbs on many objects, options computed from place and knowledge, know-how spread by teaching, apprenticeship and documents, a manual of common knowledge only, no blind crafting | 37.4 (37.2: content) | discussion (23 Oct). |
| [law.md](law.md) | law as text taking effect through mechanical clauses on records, duties of office, and judgment only on disputes; Python as the clause implementation and a world setting; how law can still be captured | 37.4 (37.3 to review) | discussion (23 Oct). |
| [farming.md](farming.md) | optional stages, crops from the sowing day, rotations, cattle, the harvest window, sowing work per seed | 37.2 | largely accepted and built (swept 5 Nov): D2-11 to D2-18, D2-53, D2-54, D2-59, D2-64 to D2-67, D2-119, D2-129, D2-163, D2-172, D4-38 to ... |
| [tools.md](tools.md) | the tool set by dependence: hand tools with grades, plough, harness, saddle, carts, weapons, traps | 37.2 | accepted: D2-23 (open points remain). |
| [livestock.md](livestock.md) | one livestock system; herds, pasture, fodder, herding scale, the common herd | 37.2 | partly accepted: D2-6, D2-18, D2-23, D2-42, D2-63, D2-117, D2-123 to D2-125, D2-127, D2-128, D2-130 to D2-132, D2-136, D2-189, D4-41, ... |
| [shelter.md](shelter.md) | houses, upkeep, breaks, the cold, the shelter ladder | 37.2 | partly accepted: H-5, D2-10; later decisions settle most of the rest: D2-9 and D2-154 (a house is rooms, beds and a hearth), D2-157 and ... |
| [buildings.md](buildings.md) | buildings from parts: structures, rooms, fittings, scaling, storeys, limits | 37.2 | partly accepted: D2-3, D2-9 (23 Oct), then D2-45, D2-49, D2-154, D2-155, D2-166, D2-168 (numbers, fittings, storage, wear; to 3 Nov). ... |
| [buildings_integration.md](buildings_integration.md) | how buildings meet every other system; eight decisions before Package E: fuel and timber (woods too small; firewood apart from timber), beds for members, heating by floor, building ground as a claim, children, room access, fire and floods, materials over roads | 37.2 | mostly settled. Package E (02y) was deferred until this was worked out (Zach, 24 Oct), then replaced by the building package (02zh), built ... |
| [forests.md](forests.md) | a forest as trees, young growth and dead wood; timber (builds, 2 heat), firewood (burns, 0.5 heat, by hand), charcoal (6 heat, light); near woods degrade, far forests endure; links to perception, labour, building, food, trade, claims, environment | 37.2 (37.4 owns land and perception) | accepted: D2-156 to D2-159 (24 Oct); poles from young growth (Q4) open. Design only. |
| [resources_and_goods.md](resources_and_goods.md) | the base resources, the lean first-world set and the pruning rule, unlocks, end uses | 37.2 | largely accepted (swept 5 Nov): the lean set (D2-24), with charcoal a good again (D2-56) and the food goods added since (D2-41, D2-42, ... |
| [economy_later.md](economy_later.md) | options kept out of the first worlds (armour, nets, boats, seed drill, irrigation, clay, iron, the press, ...) | 37.2 | deferred (23 Oct): kept out of the first worlds by D2-10, D2-14, D2-19 and D2-23. |
| [transport_and_lodging.md](transport_and_lodging.md) | the transport ladder, capacities, danger by edge and season, inns and hosts | 37.2 (37.4 the mechanism) | partly accepted: D4-9 (goods, letters and people cross only when carried), D4-12 (a night out costs 1.5 food ... |
| [environment_state.md](environment_state.md) | the hidden state of places and things: a few variables per parcel, water, building, herd, person and node, damped, one step a day; hazards read them, incidents and people's acts write them; cascades; low-salience signs | 37.2 | discussion (23 Oct); flagged for later as a whole (OPEN L-23, 24 Oct: water as a need and the land's hidden state, all six questions) ... |
| [environment_catalogue.md](environment_catalogue.md) | what can happen: eras (climate, disease, ecology, outside pressure), weather by land kind, hazards that spread (fire, crop, livestock and human disease) in six patterns; how people prepare, respond and recover | 37.2 | partly accepted: D2-76 to D2-79 (23 Oct), compiled into spec/environment/scheduler.md; disease deferred (OPEN Q-16, L-9) ... |
| [environment.md](environment.md) | one scheduler for eras, years, spells, incidents and spreads; each layer sets the odds of the next; paired draws; consequences and signs read by presence, salience, skill and concern | 37.2 (owns spec/environment: D2-75) | partly accepted: D2-69 to D2-75 (23 Oct, §13), with the catalogue accepted in environment_catalogue.md (D2-76 to D2-79) ... |
| [road_encounters.md](road_encounters.md) | meetings on the road as fuse events: travellers going opposite ways, lost herds, searches; later waiting on a road for camps, tolls and ambushes | 37.2 (37.4 owns travel and combat) | accepted: D2-81, D2-110 (23 Oct); odds by stretch and landmark (D2-104); waiting on a road later (OPEN L-7) ... |
| [journeys.md](journeys.md) | what travellers see on the way: daily notices on the road (others, herds, a body, traces left by passers), remembered on arrival; rare signs of slow change on long journeys | 37.2 (37.4 owns perception and roads) | accepted: D2-88, D2-89, D2-97 (23 Oct). Design only. |
| [hidden_ways.md](hidden_ways.md) | edges tied to a side and parcels, some hidden; found by work in the parcel, attention, knack and traces; the finder chooses whom to tell | 37.2 (37.4 owns edges and knowledge) | accepted: D2-90 to D2-92, D2-98 (23 Oct); numbers to calibrate. Design only. |
| [things_in_places.md](things_in_places.md) | one kind of thing at a spot (a parcel, or a stretch of road: one per day of its length): goods left or hidden, remains, herds, camps, traces, hidden ways' ends; one noticing rule (conspicuousness x presence x attention x knack x traces); a find on the road worth taking gives a short call; left things held by nobody | 37.2 (37.4 owns places and perception; extends objects_in_world.md) | accepted: D2-85 to D2-88, D2-93, D2-95, D2-96, D2-102, D2-104, D2-111, with D4-52, D4-70, D4-75, D4-89, D4-90 and D4-99 since. ... |
| [road_layout.md](road_layout.md) | a road as one place with stretches and a few landmarks (ford, bridge, pass, narrows, spring...): events happen where on the road; landmarks decide crossing challenges and risks; bridges, huts and tolls built on them | 37.2 (37.4 owns edges and travel) | partly accepted: D2-104 to D2-110, D2-113, D2-121, D2-122. Built: stretches, landmarks, good places, the three tiers with choices at ... |
| [verb_modifiers.md](verb_modifiers.md) | modifiers on verbs as data (`for`, `hidden`, `searching`, `method`, `aim`): the same act done another way, nothing by default, some common and some learned | 37.2 (37.4 owns verbs and knowledge) | accepted: D2-93, D2-94, D2-111, D2-112 (23 Oct); `searching` and `aim: burn` as modifiers still open. ... |
| [visibility.md](visibility.md) | how much a place and the day let each sense through: sight and sound by cover, changed by the land's state (felling, crops, snow, building) and by light and weather; multiplies every sign | 37.2 (37.4 owns perception) | accepted: D2-99 to D2-103 (23 Oct); numbers to calibrate; smell later. Design only. |
| [recipes.md](recipes.md) | the first worlds' recipes as technique cards: gathering, making, building, working; basics and ten trades; tool wear; what travels; price anchors | 37.2 (37.4: verbs, knowledge) | largely accepted (swept 5 Nov): D2-41 to D2-48, D2-56, D2-60 to D2-62, D2-160, D2-166, D2-167, D4-97 ... |
| [hiring.md](hiring.md) | work for someone: `for` on work actions puts output into the employer's container; day labour, piece rate, wages, sharecropping, tenancy, apprenticeship, shopkeepers, guards, carriers | 37.2 (37.4, 37.3) | accepted: D2-36 to D2-40 (23 Oct); in spec/economy/agreements.md. |
| [agreements.md](agreements.md) | one system of agreements made of legs (cybertron 1's Standing Contract): trade, credit, subscriptions, wages, rent, dues; paid where there is a path, else arrears; ledgers; currency wanted, not required | 37.2 (37.4, 37.3) | accepted: D2-31 to D2-36 (23 Oct); in spec/economy/agreements.md. |
| [exchange_and_money.md](exchange_and_money.md) | exchange at a node, coin, debts, credit, tolls | 37.2 | accepted: D2-1, D2-2, D2-25 to D2-30, D4-17 (23 Oct); hiring moves to hiring.md. |
| [information_economics.md](information_economics.md) | writing materials, documents, the information ladder, libraries, archives, maps | 37.2 (37.4 owns information/) | partly accepted (swept 5 Nov): D2-7, D2-8; documents as goods on parchment (D2-24), each somewhere (D4-35). ... |
| [economy_plan.md](economy_plan.md) | the economy plan for cybertron2 (E1-E6, the first region) and society-scale layers | 37.2 | partly accepted and built (swept 5 Nov). The first region was adopted as the target world (38.08 §1), then replaced by 02t's four villages ... |
| [beasts_known.md](beasts_known.md) | one knows one's beasts by memory and noticing; a household's living seeded as experience | 37.4 (37.2: livestock) | retrospective, accepted: D4-56 (built 24 Oct at Zach's request; written down afterwards) |
| [offers_to_children.md](offers_to_children.md) | an offer to a child goes to its parent here | 37.4 (37.2: agreements) | retrospective, accepted: D4-55 (built 24 Oct at Zach's request; written down afterwards) |
| [one_noticing_rule.md](one_noticing_rule.md) | every sign and event by the one noticing rule, each reaching as far as what it is: the node, a parcel, a building, a stretch or the road | 37.4 | retrospective, accepted: D4-53 (built 24 Oct at Zach's request; written down afterwards) |
| [herds_at_dusk.md](herds_at_dusk.md) | a herd that wandered goes home at dusk by chance, less when well fed where it is | 37.2 (37.4 built it) | retrospective, accepted: D4-54 (built 24 Oct at Zach's request; written down afterwards) |
| [carcasses.md](carcasses.md) | a beast that dies leaves a carcass: fit to eat about a day, then gone off, then bones; on a road maybe none or hidden; meat limited by how it died | 37.4 (37.2: livestock numbers) | retrospective, accepted: D4-52 (built 24 Oct at Zach's request; written down afterwards) |
| [open_fire_and_camp.md](open_fire_and_camp.md) | a fire in the open 2 timber a night; a camp 3 timber to build, 1 a night to keep lit | 37.4 (37.2: shelter) | retrospective, accepted: D4-49 (built 23 Oct at Zach's request; written down afterwards, 24 Oct) |
| [passing_by.md](passing_by.md) | `travel {meeting: pass by}`: a meeting passes on its own, no call, described to both | 37.4 | retrospective, accepted: D4-51 (built 24 Oct at Zach's request; written down afterwards) |
| [fuse_events.md](fuse_events.md) | events with a detection time and a completion time; urgent calls for those who notice in time | 37.2 (37.4 owns conflict/, core/) | accepted: D2-5 (the mechanism), D2-80 to D2-84 (the details, 23 Oct) ... |
| [gates.md](gates.md) | boundaries with entry rules: names, passes, tolls, a keeper; admission in the talk step | 37.2 (37.4 owns conflict/) | accepted: D2-5 (an automatic check first, otherwise the keeper and the arrivals talk on the day they arrive); the rest discussion. |
| [attacks_and_walls.md](attacks_and_walls.md) | attacks on people, buildings and nodes; walls multiplying defenders; the watch | 37.2 (37.4 owns conflict/) | partly accepted: D2-20 (three kinds of attack; walls multiply defenders), D2-21 (the watch), D2-22 (any party may raid a node), D2-49 to ... |
| [act_fixes.md](act_fixes.md) | Acts made to work as they read | 37.4 | retrospective, accepted: D4-94 (2 Nov) |
| [ages_shown.md](ages_shown.md) | Each person told their age and what lies ahead | 37.4 | retrospective, accepted: D4-69 (2 Nov) |
| [baby_and_partner_lines.md](baby_and_partner_lines.md) | A baby sleeps with its mother; a partner's death shown only once known | 37.4 | retrospective, accepted: D4-87, D4-88 (2 Nov) |
| [beliefs_and_values.md](beliefs_and_values.md) | beliefs, values and customs (flagged for later: OPEN L-25) | 37.2 | flagged for later (24 Oct): a large future integration that needs more thought and design (Zach). |
| [building_lines.md](building_lines.md) | buildings people make their own (descriptions and lines written on them) | 37.2 | decided in part (3 Nov): every building carries a description and lines its people write, anyone can read them, and others can change or ... |
| [building_risks.md](building_risks.md) | What can happen to buildings and fittings, by weather and use (flagged for later) | 37.4 | deferred (OPEN L-48), with the harsher weather (L-47) and the levels of fire (L-46) |
| [children.md](children.md) | children as a choice, counted in days (costs, care, growing up, old age, succession) | 37.2 | accepted: D2-138 to D2-152 (24 Oct; pregnancy, gap and cap replaced by D2-162, see fertility.md); care beyond survival later (OPEN L-26) ... |
| [departure_times.md](departure_times.md) | Setting off in the morning or at nightfall | 37.4 | accepted: D4-67 (2 Nov) |
| [dependence_ladder.md](dependence_ladder.md) | The dependence ladder (OPEN L-50) | 37.2 | designed and generated, not run (the cheap ladder: 3 worlds, regenerated 3 Nov). Zach, 2 Nov: "design but don't build yet. ... |
| [ecosystems.md](ecosystems.md) | environments, ecosystems and how they cluster | 37.2 | discussion; the wide design, kept for later. Its narrowed part is decided and built as [temperate_landscapes.md](temperate_landscapes.md) ... |
| [every_line_by_the_rule.md](every_line_by_the_rule.md) | Every perceived line by the one noticing rule | 37.4 | retrospective, accepted: D4-75 (2 Nov) |
| [fallback.md](fallback.md) | A fallback each person sets | 37.4 | retrospective, accepted: D4-76 (2 Nov) |
| [fences.md](fences.md) | fences, hedges and walls | 37.4 | discussion (23 Oct). |
| [fertility.md](fertility.md) | fertility and replacement | 37.2 | decided in part (29 Oct): pregnancy 2 days, the gap after a birth 1 day, and the conception chance's cap 0.8 (D2-162) ... |
| [fire_levels_and_camps.md](fire_levels_and_camps.md) | Levels of fire, and camps built out (flagged for later) | 37.4 | deferred (flagged for later: OPEN L-46, L-47) |
| [fire_lines.md](fire_lines.md) | One room, one fire; the night says what fuel was missing; a theft at a door told as one | 37.4 | retrospective, accepted: D4-93 (2 Nov) |
| [fire_weather.md](fire_weather.md) | A fire under no roof in the night's weather | 37.4 | retrospective, accepted: D4-83 (2 Nov) |
| [generator.md](generator.md) | the landscape generator (a world under the graph) | 37.2 | partly accepted: D2-173 to D2-175 here, D2-177 to D2-188 through stage 1, D2-189 to D2-191 since. ... |
| [generator_stage1.md](generator_stage1.md) | the generator, stage 1 (a spec for review before it is built) | 37.2 | built (3 Nov) by 37.2 at Zach's request, with what differs listed in [02zj](../../review/37_growth/02zj_generator_build.md). ... |
| [graves.md](graves.md) | Graves dug by many, over days; a cairn after burial; an unfinished grave's signs | 37.4 | retrospective, accepted: D4-99 (4 Nov) |
| [heap_sizes.md](heap_sizes.md) | How much lies there: heaps seen by their bulk, counted when attended, and kept by their house | 37.4 | retrospective, accepted: D4-89, D4-90, D4-91, D4-92 (2 Nov) |
| [herd_seen_next_door.md](herd_seen_next_door.md) | A herd seen: its sighting at the spec's own, and presence next door raised | 37.4 | retrospective, accepted: D4-98 (3 Nov) |
| [life.md](life.md) | life (partners, children, growing up, death, inheritance) | 37.4 | discussion (23 Oct). |
| [mill_and_oven_scale.md](mill_and_oven_scale.md) | Mills and ovens at scale: a few units that do a great deal | 37.4 | accepted: D4-97 (2 Nov); the upkeep moved to building_risks.md (L-48) |
| [objects_in_world.md](objects_in_world.md) | objects placed in the world | 37.4 | discussion (23 Oct; flagged to explore). |
| [referent_tags.md](referent_tags.md) | Short tags for things one can act on that have no unique name | 37.4 | accepted: D4-68 (2 Nov) |
| [refusal_messages.md](refusal_messages.md) | What a refusal says | 37.4 | retrospective, accepted: D4-95, D4-96 (2 Nov) |
| [run_data_interface.md](run_data_interface.md) | A fixed data interface for runs: versioned shapes, one read layer, one published layout | 37.4 | partly accepted: D4-100 (part 1, built at Zach's request; retrospective). Part 2: discussion. |
| [run_tools.md](run_tools.md) | Runs that stop before the weekly limit, and play on | 37.4 | retrospective, accepted: D4-79 (1 Nov) |
| [search_on_take.md](search_on_take.md) | Taking from a place is a search | 37.4 | retrospective, accepted: D4-70 (2 Nov) |
| [senses.md](senses.md) | the senses across every system | 37.4 | discussion (23 Oct). |
| [sign_bundles.md](sign_bundles.md) | Events and their aftermath show themselves | 37.4 | retrospective, accepted: D4-74 (2 Nov) |
| [sign_rules.md](sign_rules.md) | No invented acts in signs; one's beasts kept short | 37.4 | retrospective, accepted: D4-72, D4-73 (2 Nov) |
| [slaughter_signs.md](slaughter_signs.md) | A slaughter shows itself | 37.4 | retrospective, accepted: D4-71 (2 Nov) |
| [speech_order.md](speech_order.md) | When people talk, and what it costs: by reach, with an evening at the hearth | 37.4 | accepted: D4-65, D4-66, D4-77 (2 Nov) |
| [temperate_landscapes.md](temperate_landscapes.md) | landscapes that make sense, within one environmental envelope | 37.2 | built (D2-191; Zach, 2 Nov: "build this out"); as built in §5, with what differs from the design. |
| [thefts_known.md](thefts_known.md) | Who knows of a theft | 37.4 | retrospective, accepted: D4-81 (2 Nov) |

## Log of ideas and their outcomes

Newest first. Ideas decided or rejected in conversation before 23 Oct are backfilled from the 37.4 work log and DECISIONS.md.

| Date | Idea | Outcome | Where |
|---|---|---|---|
| 24 Oct | The forest's three stocks; fuel in heat with firewood; rights in woods; shelter and fire separate, fires shared; raw food values; seeding below capacity | accepted: D2-156 to D2-161 | forests.md, recipes.md §17, 02za |
| 24 Oct | Every staple worthless without a fire; one fire per person in the open | rejected: D2-160, D2-159 | recipes.md, forests.md |
| 24 Oct | The forest as a system; firewood apart from timber, by the forest's health; fuel in heat | discussion | forests.md |
| 24 Oct | Package E deferred; buildings' integration with the other systems, and woods too small for fuel | discussion | buildings_integration.md |
| 24 Oct | One unit of space from parcel to fitting; storage takes space; a cheaper cellar | accepted: D2-154, D2-155 | buildings.md; spec/economy/buildings.md |
| 24 Oct | Fittings free of space; unlimited stores | rejected: D2-154, D2-155 | buildings.md |
| 24 Oct | Care for survival only now; the cost dial built low and high; any two of opposite sex who both choose | accepted: D2-150 to D2-152 | children.md; spec/life/birth_and_death.md |
| 24 Oct | Beliefs, values and customs held by people and passed on | flagged for later: OPEN L-25 | beliefs_and_values.md |
| 24 Oct | One's beasts known by memory and noticing, not listed; the merchants' ox as seeded experience (built, then written down) | retrospective, accepted: D4-56 | [beasts_known.md](beasts_known.md) |
| 24 Oct | An offer to a child goes to its parent (built, then written down) | retrospective, accepted: D4-55 | [offers_to_children.md](offers_to_children.md) |
| 24 Oct | Every sign and event by the one noticing rule, with an extent by kind (built, then written down) | retrospective, accepted: D4-53 | [one_noticing_rule.md](one_noticing_rule.md) |
| 24 Oct | Going home at dusk a chance, not a rule (built, then written down) | retrospective, accepted: D4-54 | [herds_at_dusk.md](herds_at_dusk.md) |
| 24 Oct | A child's total cost as a world setting (the cost dial), to test low and high | accepted to explore: D2-145 | children.md |
| 24 Oct | Children by choice with work spent trying; time in days only; partnering by both even when arranged; pregnancy food and a gap; care optional; succession by the household's rules; no loyalty mechanic, memories | accepted: D2-138 to D2-144 | children.md |
| 24 Oct | Ages in calendar years in the generator; loyalty set by feeding | rejected: D2-139, D2-144 | children.md |
| 24 Oct | Dead beasts leave carcasses, edible about a day; on roads maybe none or hidden (built, then written down) | retrospective, accepted: D4-52 | [carcasses.md](carcasses.md) |
| 24 Oct | Passing by on the road, chosen at departure (built, then written down) | retrospective, accepted: D4-51 | [passing_by.md](passing_by.md) |
| 23 Oct | An open fire 2 timber; a camp 3 to build and 1 a night (built, then written down) | retrospective, accepted: D4-49 | [open_fire_and_camp.md](open_fire_and_camp.md) |
| 24 Oct | Dibbling known to at least one person in the world; fences round a parcel; the split share peaked at a quarter; gates automatic, opening one an act | accepted: D2-129 to D2-132 | livestock.md |
| 24 Oct | Fences on borders between parcels (for now); one farmer per village knowing dibbling | replaced: D2-130, D2-129; borders later (L-24) | livestock.md |
| 24 Oct | Build choices confirmed or changed (Q-20); herds wandering, lost on roads, driven, split by size; fences wood then stone on borders; searching as a modifier | accepted: D2-118 to D2-128 | livestock.md, fences.md, OPEN Q-20 |
| 24 Oct | Road-meeting offers as their own goods-for-goods system | rejected: the same agreement system as at a node (D2-120) | road_encounters.md |
| 24 Oct | The parcel graph from the land, with sides and heights; sensing along the way; the village as a whole; herds wandering far; fire, raiders as outside agents, and water and the land's hidden state flagged for later | accepted: D2-114 to D2-117; OPEN L-21 to L-23 | parcel_graph.md, livestock.md, OPEN.md |
| 24 Oct | Parcels as a plain list, or with coordinates | rejected: D2-114 | parcel_graph.md |
| 23 Oct | Meetings on the road with a short conversation and a choice of direction; `leave` folded into `give`; modifiers as techniques; waiting out a block; good places on the way change one's state, stopping only if known and chosen in advance | accepted: D2-109 to D2-113 | road_layout.md, road_encounters.md, verb_modifiers.md |
| 23 Oct | Stopping points on the way | replaced: D2-109 | road_layout.md |
| 23 Oct | A meeting as one wave of decisions | replaced: a short conversation (D2-110) | road_encounters.md |
| 23 Oct | Experience works through the risk; five landmarks and stopping points; building on landmarks later | accepted: D2-106 to D2-108 | road_layout.md |
| 23 Oct | One list of everything flagged for later | added: OPEN.md "Flagged for later" | OPEN.md |
| 23 Oct | Roads as stretches with optional landmarks; travel decides itself, minor trouble reported on arrival, choices at departure, a fuse call for extreme or complex situations | accepted: D2-104, D2-105 | road_layout.md |
| 23 Oct | Visibility for sight and sound by land, state and weather (light only at night); loud things mask; smell later and simple; conspicuousness split | accepted: D2-99 to D2-102 | visibility.md |
| 23 Oct | Light (dusk, night) in the day's notices; wind direction now | rejected: agents notice by day; no wind direction for now | visibility.md |
| 23 Oct | Modifiers on verbs (trying an unknown one does it worse and makes one aware); `for` and sowing method as modifiers; scavengers later with wild animals; rot near water, food and people, burial as work on a body; daily notices on the road; hidden ways found by the noticing rule | accepted: D2-93 to D2-98 | verb_modifiers.md, things_in_places.md, journeys.md, hidden_ways.md |
| 23 Oct | An unknown modifier refused outright | rejected: D2-93 | verb_modifiers.md |
| 23 Oct | `leave` folded into `give` (to a place), hide as its variant; visibility per place and sense | discussion | verb_modifiers.md §5, visibility.md |
| 23 Oct | One noticing rule; a find on the road gives a call only if noticed; left things anyone's, faster spoiling and rot with a disease risk; traces fade; slow-change signs later as data; edge ends by side and parcels, road or hidden; one knack, the eye for the land; hiding follows the land | accepted: D2-85 to D2-92 | things_in_places.md, journeys.md, hidden_ways.md |
| 23 Oct | Woodcraft as a separate skill; a third visibility "path"; ways growing back after a fixed time | rejected: D2-91, D2-90, D2-92 | hidden_ways.md |
| 23 Oct | Roads with stretches and landmarks like a node's parcels; modifiers on verbs; decay defined per item by condition | discussion (to explore) | road_layout.md, verb_modifiers.md, things_in_places.md §6 |
| 23 Oct | Fuse events' details: rare (one call a night); raids only sometimes; fire, meetings and finds on the road; acts by fuse length; a simple overlap rule to revisit; riders a small fuse; the call continues the agent's conversation | accepted: D2-80 to D2-84 | [fuse_events.md](fuse_events.md) |
| 23 Oct | Arrivals at a shut gate at night as a fuse event (37.2's list) | rejected: the gate's rule at dawn, then the talk step (D2-5) | [gates.md](gates.md) |
| 23 Oct | Things left in places (goods, caches, bodies, herds, ways) noticed by one rule; roads in stretches; the dead on the road leave remains | discussion | [things_in_places.md](things_in_places.md) |
| 23 Oct | Everything happens in a place; nothing seen across nodes by accident | accepted: D4-35 | spec/core/architecture.md |
| 23 Oct | Moving is general: join a household, take up an empty house, build one | accepted: D4-36 | spec/institutions/membership.md |
| 23 Oct | Rebuild the M1 engine on the designed general core | accepted: D4-34 | spec/core/architecture.md |
| 23 Oct | Moving: joining a household, occupying an empty house, building one, as general rules, not a migration feature | discussion | proposals/households.md |
| 23 Oct | Place as the engine's foundation (Here and Mind views, state by node, every event placed) | discussion | proposals/place.md |
| 23 Oct | A traveller too heavy to set off chooses what to leave, with a person or at a house | accepted: D4-32 | spec/economy/transport.md |
| 23 Oct | Seeded knowledge of other lines' crafts as awareness; repute from the lines born there | accepted: D4-33 | spec/seeding/README.md |
| 23 Oct | Port cybertron 1's private-message ration; make speaking aloud cost a unit of work | accepted: D4-31 | spec/information/speech.md |
| 23 Oct | Speech in one's own house only (M1) | replaced: any building one has access to, access as data | D4-30 |
| 23 Oct | Re-ask everyone who heard anything in the talk step (M1) | rejected (Zach): only direct speech wakes | D4-25 |
| 23 Oct | Speech in a building reaches those with access on the node that day, not those inside at talk time | accepted: D4-25 | spec/information/speech.md |
| 23 Oct | Thinking, past reasoning and conversation memory back from cybertron 1; agent-written memory at the end of each stretch | accepted: D4-26 to D4-28 | spec/information/memory.md |
| 23 Oct | Engine-written memory bands (two full days, one-line days); a ledger of transfers | replaced by D4-27, D4-28; ledger not adopted (Zach: forgetting is the agent's, unless shown badly) | [seeing.md](seeing.md), 38.13 |
| 23 Oct | In-world aims in every prompt | turned off: D4-29 | spec/agents/aims.md |
| 23 Oct | A per-node layout: parcels, features, structures, movables | discussion | [layout.md](layout.md) |
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
| 23 Oct | What travellers see on the way; hidden ways found by work, attention and woodcraft | discussion | [journeys.md](journeys.md), [hidden_ways.md](hidden_ways.md) |
| 23 Oct | Meetings on the road (opposite-way travellers, lost herds, searches, later ambushes) | discussion | [road_encounters.md](road_encounters.md) |
| 23 Oct | Fences, hedges, walls and folds for herds (for later) | discussion | [livestock.md](livestock.md) |
| 23 Oct | Eras in four families; outside raiders as new agents with goals; the first-world set as data; six spreading patterns; windfalls follow possession and claims | accepted: D2-76 to D2-79 | spec/environment/scheduler.md |
| 23 Oct | Outside raiders as scripted incidents | rejected: they arrive as agents with goals | D2-76 |
| 23 Oct | Shared hidden state of places and things, with cascades | discussion | [environment_state.md](environment_state.md) |
| 23 Oct | The scheduler's layers and hazard; paired draws; risks attached to things; fires and signs across edges; eras as starting conditions; the environment area to 37.2 | accepted: D2-69 to D2-75 | spec/environment/scheduler.md |
| 23 Oct | Nothing seen at another node (D4-35, strict) | amended: signs a kind declares as carrying cross edges as the terrain allows | D2-74 |
| 23 Oct | The catalogue of eras, weather and spreading hazards, with responses | discussion | [environment_catalogue.md](environment_catalogue.md) |
| 23 Oct | The environment over time: eras, years, spells, incidents, spreads; one scheduler; signs and experience | discussion | [environment.md](environment.md) |
| 23 Oct | Field works now with fixed wet and hill penalties; irrigation later; bedroll, tent and camp | accepted: D2-66 to D2-68 | spec/economy/production.md, lodging.md |
| 23 Oct | Irrigation's effects through a plot's water each day; floods, droughts and blight noted as missing (need 37.4's incidents) | discussion | [farming.md](farming.md) |
| 23 Oct | Camps and portable shelter: bedroll, tent, a camp built at a site | discussion | [transport_and_lodging.md](transport_and_lodging.md) |
| 23 Oct | Master farmer's skill raises yield x1.2; seed selection | accepted: D2-64, D2-65 | spec/economy/production.md |
| 23 Oct | Field works (ditches on wet land, terraces on hills) as projects on a plot; irrigation's parts | discussion | [farming.md](farming.md) |
| 23 Oct | The food ladder; the mill ladder (water mill a new build at a river); dried meat; cattle as three roles of one kind | accepted: D2-60 to D2-63 | spec/economy |
| 23 Oct | One expensive mill; every mill upgrade a full rebuild | rejected: a ladder by parts, geography deciding the water mill | D2-61 |
| 23 Oct | Grain spoils a little; the plot's seed | accepted: D2-58, D2-59 | spec/economy/production.md |
| 23 Oct | The food ladder: whole grain 0.7, ground 1.0, bread 1.3 that keeps; an oven | accepted: D2-60 | [recipes.md](recipes.md) §16 |
| 23 Oct | Labour need not be scarce; land binds; farms should feed towns | accepted: D2-55 | conversation |
| 23 Oct | Forcing soil-breaking to make grain dearer | rejected: farming is not to be made harder | D2-55 |
| 23 Oct | Charcoal back, cheese 2.5, beds of timber and straw, fieldstone, sun-dried shore salt, coin stamp later; two smiths seeded | accepted: D2-56, D2-57 | spec/economy |
| 23 Oct | Skill by practice on all work; crops from the sowing day with the cold as the limit; sowing work per seed (broadcast or dibble) | accepted: D2-52 to D2-54 | spec/economy/production.md |
| 23 Oct | Burn orders in a node raid, given in advance | accepted: D2-51 | [attacks_and_walls.md](attacks_and_walls.md) |
| 23 Oct | Fire kills those still inside when a building burns down | accepted: D2-50 | [attacks_and_walls.md](attacks_and_walls.md) |
| 23 Oct | Sleepers in a burning house only wounded | rejected: they should be very likely to die | D2-50 |
| 23 Oct | Stone resists fire, walls stand; a vault does not burn | accepted: D2-49 | spec/economy/buildings.md |
| 23 Oct | All stone fireproof | rejected: it would remove fire as the counter to stone houses | [buildings.md](buildings.md) |
| 23 Oct | Setting fire in a raid: a torch, access, catch chances by material, fire as a fuse event | discussion | [attacks_and_walls.md](attacks_and_walls.md) |
| 23 Oct | Bread (flour by quern or mill; eaten without a hearth; keeps), cellar and stalls, weapon wear with a small chance of breaking | accepted: D2-44 to D2-46 | [recipes.md](recipes.md) |
| 23 Oct | Specialised tools (felling axe, miner's pick, scythe, mason's chisels, reaping hook) from master smiths' recipes; cheese | accepted: D2-47, D2-48 | [recipes.md](recipes.md) §14-15 |
| 23 Oct | Meat (dense, spoils fast), milk as a learned technique, the basic set and ten trades | accepted: D2-41 to D2-43 | [recipes.md](recipes.md) |
| 23 Oct | Separate tools per method (axe, pick, sickle) | rejected in the proposal: wear is per use, so they add only up-front cost; effects differ by method as data | [recipes.md](recipes.md) §8 |
| 23 Oct | Recipes for the first worlds in work units (about 40 techniques, ten trades; a coin about a food; smelting at the seam; copper tools as the step up) | discussion | [recipes.md](recipes.md) |
| 23 Oct | Agreements of legs, the settlement rule, ledgers, legs in any good, porting standing.py and credit.py, work as a leg, acting for others, engine-checked duties, the presets | accepted: D2-31 to D2-40 | spec/economy/agreements.md |
| 23 Oct | Hiring as agreements with a work leg; `for` on work actions sends output to the employer's container | accepted: D2-36 to D2-40 | [hiring.md](hiring.md) |
| 23 Oct | Offers free of work units; stalls as offers to anyone; promise legs; copper coin struck by smiths; prices only as witnessed; markets as custom | accepted: D2-25 to D2-30 | spec/economy/money_and_markets.md |
| 23 Oct | Agreements made of legs, with one settlement rule (pay where there is a path: same node, same ledger, a carrier; else arrears); ledgers for distance; currency wanted, not required | accepted: D2-31 to D2-34 | [agreements.md](agreements.md) |
| 23 Oct | Exchange for cybertron2: offers to a person or to anyone, settling at once, free of work units; promises as a leg; prices only as witnessed; copper coin struck by smiths; markets as custom | accepted: D2-25 to D2-30 | [exchange_and_money.md](exchange_and_money.md) |
| 23 Oct | Trades that cost actions (cybertron 1's escrowed Exchange, 2-3 actions and a round) | rejected in the proposal: specialisation lost to self-supply | [exchange_and_money.md](exchange_and_money.md) |
| 23 Oct | The lean first-world set: copper, salt, documents, hides and timber with the goods already decided | accepted: D2-24 | spec/economy/goods.md |
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
| 23 Oct | Farming stages' work and returns (02l §2); soil fertility worn and restored; the plot unit; oxen as a role within cattle; winter fodder of hay and straw; recipes.md as the calibrate base | accepted: D4-38 to D4-43 (38.20 A1, A2, A5, B3, B4, E1) | farming.md, livestock.md, recipes.md (spec: 37.2's production.md, livestock.md) |
| 23 Oct | Breeding on its own with a bull present and the herd fed, managed by where the bull is kept; cattle graze and eat fodder, overgrazing wears pasture | accepted: D4-44, D4-45 | livestock.md (spec: 37.2's livestock.md) |
| 23 Oct | Smelting by charcoal or timber; unexplored places reached by following an unexplored way | accepted: D4-46, D4-47 | conversation (spec: world/places.md, edges.md; recipes: 37.2) |
| 23 Oct | Each state shows a bundle of signs, each with a sense, a chance, conditions and a knack; observers roll on their own | accepted: D4-48 | spec/information/perception.md |
| 23 Oct | The senses across every system: what the observer brings, and coverage by system (Zach's worklist) | discussion | [senses.md](senses.md) |
| 23 Oct | Life: partners, children by choice, growing up in rounds, death of old age, inheritance | discussion | [life.md](life.md) |
| [children.md](children.md) | children only by choice, trying costs work; everything in days; pregnancy's food and the nursing gap; care optional; what a child costs and gives (nearly free when compressed: a cost dial); old age; succession by the household's rules | 37.2 (37.4 owns life) | accepted: D2-138 to D2-152 |
| [beliefs_and_values.md](beliefs_and_values.md) | customs and values held by people and passed on (to children, by exposure), distinct from know-how; cultural evolution | 37.2 (with 37.3, 37.4) | flagged for later (OPEN L-25) |
| 23 Oct | Objects placed in the world: leave on a parcel, noticed by anyone, whose they are | discussion (to explore) | [objects_in_world.md](objects_in_world.md) |
| 23 Oct | Fences, hedges and stone walls as field works that keep beasts in or out | discussion | [fences.md](fences.md) |
| 23 Oct | The senses: an eye for the land (some have none) and signs of bareness scaled by how bare | partly accepted: D4-50 | [senses.md](senses.md) |
| 24 Oct | Customs held by named households (for Hollins 2) | retrospective, accepted: D4-57 | [household_customs.md](household_customs.md) |
| 24 Oct | A led beast stays with its leader until let go | retrospective, accepted: D4-58 | [led_beasts.md](led_beasts.md) |
| 24 Oct | Signs for the newer systems | retrospective, accepted: D4-59 | [more_signs.md](more_signs.md) |
| 24 Oct | Clearing new ground for fields | retrospective, accepted: D4-60 | [clearing.md](clearing.md) |
| 24 Oct | Memory rewritten each stretch, its length set by age (after live tests) | accepted: D4-61 | [memory_rewrite.md](memory_rewrite.md) |
| 24 Oct | A day as a chain of parcels in act order (built, then written down) | retrospective, accepted: D4-62 | [day_route.md](day_route.md) |
| 29 Oct | Fertility and replacement: shorter waits, a higher chance; soft limits to discuss | accepted in part: D2-162 | [fertility.md](fertility.md) |
| 31 Oct | A page for playing an agent (built, then written down) | retrospective, accepted: D4-63 | [play_page.md](play_page.md) |
| 1 Nov | Lines kept for good, passed on with care, replacing customs | accepted: D4-64 | [lasting_memory.md](lasting_memory.md) |
| 2 Nov | An evening at the hearth, one wave of answers; the evening settles the night | partly accepted: D4-65, D4-66 | [speech_order.md](speech_order.md) |
| 2 Nov | Setting off in the morning or at nightfall | accepted: D4-67 | [departure_times.md](departure_times.md) |
| 2 Nov | Short tags and names for herds and things | accepted: D4-68 | [referent_tags.md](referent_tags.md) |
| 2 Nov | Each person told their age (built, then written down) | retrospective, accepted: D4-69 | [ages_shown.md](ages_shown.md) |
| 2 Nov | Taking from a place is a search (built, then written down) | retrospective, accepted: D4-70 | [search_on_take.md](search_on_take.md) |
| 2 Nov | A slaughter shows itself (built, then written down) | retrospective, accepted: D4-71 | [slaughter_signs.md](slaughter_signs.md) |
| 2 Nov | No invented acts in signs; one's beasts kept short (built, then written down) | retrospective, accepted: D4-72, D4-73 | [sign_rules.md](sign_rules.md) |
| 2 Nov | A fallback each person sets (built, then written down) | retrospective, accepted: D4-76 | [fallback.md](fallback.md) |
| 2 Nov | The evening's add-ons: meetings, memory at the evening, plan at the hearth | accepted: D4-77 | [speech_order.md](speech_order.md) |
| 2 Nov | The morning message from beliefs (built 1 Nov, recorded in review) | partly accepted: D4-78 | [agent_view.md](agent_view.md) |
| 2 Nov | Runs stop before the weekly limit; continue --days (built, then written down) | retrospective, accepted: D4-79 | [run_tools.md](run_tools.md) |
| 2 Nov | The memory at the evening withdrawn after a test (38.44) | accepted: D4-80 (replaces D4-77 (2)) | [speech_order.md](speech_order.md) |
| 2 Nov | Events and their aftermath as bundles of signs, four kinds (built, then written down) | retrospective, accepted: D4-74 | [sign_bundles.md](sign_bundles.md) |
| 2 Nov | Every perceived line by the one noticing rule; sound and smell carry (built, then written down) | retrospective, accepted: D4-75 | [every_line_by_the_rule.md](every_line_by_the_rule.md) |
| 2 Nov | Who knows of a theft (built, then written down) | retrospective, accepted: D4-81 | [thefts_known.md](thefts_known.md) |
| 2 Nov | The day's sightings at the hearth | accepted: D4-82 | [speech_order.md](speech_order.md) |
| 3 Nov | Buildings people make their own: descriptions and lines written on them, a monument, fine work | accepted in part: D2-169 | [building_lines.md](building_lines.md) |
| 3 Nov | The landscape generator: a world under the graph, filled in around what a world file gives | accepted in part: D2-173 | [generator.md](generator.md) |
| 2 Nov | A fire under no roof in the night's weather (built, then written down) | retrospective, accepted: D4-83 | [fire_weather.md](fire_weather.md) |
| 3 Nov | The generator, stage 1: a spec for review (today's world format plus the mesh, no engine change) | for review | [generator_stage1.md](generator_stage1.md) |
| 2 Nov | A baby sleeps with its mother; a partner's death shown only once known (built, then written down) | retrospective, accepted: D4-87, D4-88 | [baby_and_partner_lines.md](baby_and_partner_lines.md) |
| 2 Nov | How much lies there: heaps by bulk, counted when attended, kept by their house; a begun fitting shown (built, then written down) | retrospective, accepted: D4-89, D4-90, D4-91 | [heap_sizes.md](heap_sizes.md) |
| 2 Nov | One room, one fire; the night line names the fuel it lacked; a theft at a door told as one (built, then written down) | retrospective, accepted: D4-93 | [fire_lines.md](fire_lines.md) |
| 2 Nov | Acts made to work as they read: open fire by heat, take by tag in a phrase, move overflows, work-leg notes, camp fittings (built, then written down) | retrospective, accepted: D4-94 | [act_fixes.md](act_fixes.md) |
| 2 Nov | What a refusal says: where a good is, who took it, how it is made, who did it, where here, who sets a door; pin by text; no known-dead head (built, then written down) | retrospective, accepted: D4-95 | [refusal_messages.md](refusal_messages.md) |
| 2 Nov | Using the store at home: give draws on it too; every act says what it took from which store (built, then written down) | retrospective, accepted: D4-96 | [refusal_messages.md](refusal_messages.md) |
| 2 Nov | Levels of fire; camps built out with harder weather | deferred (L-46, L-47) | [fire_levels_and_camps.md](fire_levels_and_camps.md) |
| 2 Nov | Mills and ovens at scale (numbers for Zach) | discussion | [mill_and_oven_scale.md](mill_and_oven_scale.md) |
| 3 Nov | A herd seen at the spec's own; presence next door 0.3 | retrospective, accepted: D4-98 | [herd_seen_next_door.md](herd_seen_next_door.md) |
| 4 Nov | Graves dug by many over days; a cairn after burial; an unfinished grave's signs | retrospective, accepted: D4-99 | [graves.md](graves.md) |
| 4 Nov | A fixed data interface for runs: the world record's shape versioned (built); upgrade chain, view tables as the read interface, derived logs, one published layout, converting pre-journal runs (discussion) | partly accepted: D4-100 | [run_data_interface.md](run_data_interface.md) |
| 2 Nov | What can happen to buildings and fittings, by weather and use | deferred (L-48) | [building_risks.md](building_risks.md) |
| 2 Nov | Mills and ovens at scale; oven in stone; coppice held; fuel line; babies by shelter; refused acts not retried; stone walling | accepted: D4-97 | [mill_and_oven_scale.md](mill_and_oven_scale.md) |
| 24 Oct | how buildings fit the other systems (before Package E is built) | mostly settled. Package E (02y) was deferred until this was worked out (Zach, 24 Oct), then replaced by the building package (02zh), built ... | [buildings_integration.md](buildings_integration.md) |
| 2 Nov | The dependence ladder (OPEN L-50) | designed and generated, not run (the cheap ladder: 3 worlds, regenerated 3 Nov). Zach, 2 Nov: "design but don't build yet. ... | [dependence_ladder.md](dependence_ladder.md) |
| 2 Nov | environments, ecosystems and how they cluster | discussion; the wide design, kept for later. Its narrowed part is decided and built as [temperate_landscapes.md](temperate_landscapes.md) ... | [ecosystems.md](ecosystems.md) |
| 24 Oct | the forest as a system (trees, young growth, dead wood; timber, firewood, charcoal) | accepted: D2-156 to D2-159 (24 Oct); poles from young growth (Q4) open. Design only. | [forests.md](forests.md) |
| 23 Oct | Households and dwellings: membership, use and home are data that agents change | partly accepted: D4-36 (the principle); the open questions remain. | [households.md](households.md) |
| 23 Oct | the parcel graph (where things are inside a node) | accepted: D2-114 to D2-116 (24 Oct), amended by D4-62 (the day's route) and D4-98 (next door 0.3). ... | [parcel_graph.md](parcel_graph.md) |
| 23 Oct | Place as the engine's foundation: everything is somewhere, and an agent can reach only where it is | accepted in principle: D4-35 (the mechanism is part of the D4-34 rebuild). | [place.md](place.md) |
| 23 Oct | the layout of a road (stretches and landmarks) | partly accepted: D2-104 to D2-110, D2-113, D2-121, D2-122. Built: stretches, landmarks, good places, the three tiers with choices at ... | [road_layout.md](road_layout.md) |
| 23 Oct | the run record and the run backend | accepted: D1-1 to D1-5 (24 Oct; spec/record/). | [run_record.md](run_record.md) |
| 2 Nov | landscapes that make sense, within one environmental envelope | built (D2-191; Zach, 2 Nov: "build this out"); as built in §5, with what differs from the design. | [temperate_landscapes.md](temperate_landscapes.md) |
| 23 Oct | modifiers on verbs (ways of doing an act that people know or learn) | accepted: D2-93, D2-94, D2-111, D2-112 (23 Oct); `searching` and `aim: burn` as modifiers still open. ... | [verb_modifiers.md](verb_modifiers.md) |
| 23 Oct | visibility (what a place and the day let the senses reach) | accepted: D2-99 to D2-103 (23 Oct); numbers to calibrate; smell later. Design only. | [visibility.md](visibility.md) |
