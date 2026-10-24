# cybertron2: open questions and conflicts

Each item has an owner (README "Who owns what") who resolves it, with Zach where it needs a decision. Resolved items move to
[DECISIONS.md](DECISIONS.md) or into the spec, and are struck through here. Compiled 22 Oct 2026.

## Conflicts between documents

| # | Conflict | Where | Proposed resolution | Owner |
|---|---|---|---|---|
| ~~C-1~~ | Carrying capacity: on foot 20, pack 35, animal +60, cart +150 | 38.06 §3 vs 02g §3 (on foot 10, pack 20, pack ox 60, handcart 40, ox cart 200, wagon 500, boat 1,500) | take 02g's numbers (calibrated against grain's cost); 06's table superseded | 37.2 (numbers) | resolved 24 Oct: D2-135 (02u) |
| C-2 | Building limits: slots by land kind | 38.04 §1 vs 02e §3.9 lots, 02i parts | lots and slots are the same thing (land per node, by kind); parts decide what a building does | 37.4 with 37.2 |
| C-3 | Speech at a node: one talk step | 38.05 §1 vs 02h §4a (the square, rooms by access, private messages) | the talk step delivers in 02h's three scopes | 37.4 |
| C-4 | Letters and channels | 38.05 §5 (letters, errands) vs 02h §4 (channels with a medium and a location; boards, carried editions, boxes) | letters and boards first, on 02h's channel record; editions later | 37.4 with 37.2 |
| C-5 | Riders who travel and strike in one round | 02g §5b vs D4-8 (arrive, then decide) | a fuse event (02k): riders shorten detection to almost nothing, so no exception to D4-8 is needed | 37.4 (Zach to confirm) |
| C-6 | Danger on the road | 38.05 §2 (a risk draw per night) vs 02g §3b-3c (danger per edge by terrain and season, per rung) | 02g's table as the draws of the 37.4 scheduler | 37.4 |
| C-7 | The handoff README's next steps and document list | 38 README §2, §7 | superseded by this folder; README gets a pointer | 37.4 |
| C-8 | Environment design for the old engine (calendar, micro-events, foresight) | `wp/environment`: 04_environment_design.md, cybertron/environment.py | redesigned for cybertron2 in spec/environment.md; the old branch marked superseded | 37.4 |
| C-9 | Ages: calendar years | 38.09 §2a-2b vs D4-19 | D4-19 wins | 37.4 |
| C-10 | Run files, checkpoints, replay, versioning | spec/core/README `records.md` (37.4, to compile) vs spec/record/ (37.1, D1-4) | `core/records.md` becomes a pointer to spec/record/; `core/events.md` keeps what an event is, record/journal.md how events are stored | 37.4 to confirm |

## Open questions

| # | Question | Where | Owner |
|---|---|---|---|
| Q-1 | Work units a day and the cost table (by experiment) | 38.06 §3, D4-17 | 37.4 |
| Q-2 | Overexertion costs (x1.5, x2, exhaustion) | 38.06 §3 | 37.4 |
| Q-3 | Talk-step waves (one or two) | 38.05 §8 | 37.4 |
| Q-4 | Year length in days; season lengths | 38.05, D4-13 | 37.4 |
| Q-5 | Rounds a youth lasts; lifespans in rounds | 38.09 §4 | 37.4 (37.1) |
| Q-6 | Settlement limit: a hard cap or a crowding cost | 38.04 §7 | 37.4 |
| Q-7 | First land kinds (proposed: river valley, woodland, hills, crossroads) | 38.04 §7 | 37.4 |
| Q-8 | Which signs, incidents and eras first | 37.4 environment | 37.4 |
| Q-9 | 37.2's open decisions in 02f §6, 02g §7, 02h §9, 02i §8, 02j, 02k | those notes | 37.2 |
| ~~Q-11~~ | ~~Who holds a plot; can plots be split; the minimum plot size (37.1's question)~~ resolved by D4-23 (spec/world/holding.md) | board | 37.4 |
| Q-10 | The first LLM world for M1 (a small version of 02f §4's region) | 38.08 §2 | 37.4 with 37.2 |
| ~~Q-12~~ | ~~Decisions made with 37.2 that belong in 37.4's spec areas and are not yet written there (staleness check, 23 Oct): D2-5 (fuse events, gates), D2-21 (the watch), D2-22 (any party may raid a node), D2-50 (fire kills), D2-51 (burn orders in a raid) for `spec/conflict/`; D2-8 (wide reach costs more) for `spec/information/`. Drafts: proposals/fuse_events.md, gates.md, attacks_and_walls.md, information_economics.md~~ written 23 Oct: spec/conflict/combat.md, raids.md, defence.md; spec/information/letters_and_documents.md (with perception.md, prompts.md; H-1 to H-4, H-7 also placed) | DECISIONS.md | 37.4 |
| ~~Q-13~~ | ~~D4-37 (whoever is owed may release a debt; gives and leaves to the creditor are credited) belongs in `spec/economy/agreements.md` (37.2's file): Settlement and What agents see. Built in cybertron2/engine (`release`, the credit hook)~~ written 23 Oct in spec/economy/agreements.md | DECISIONS.md D4-37 | 37.2 |
| Q-14 | The whole agenda of open decisions in the proposals, by what each blocks (A farming to M information), with each proposal's own answer: review 38.20 | docs/review/38_space_engine/20_decisions_needed.md | Zach, with each file's owner |
| Q-16 | Disease: mortality, the units of the sick, immunity, nursing, a healer (Zach: needs more thought) | proposals/environment_catalogue.md §3 | 37.2 with 37.1 |
| Q-17 | Edge terrain data (what an edge's land is: plain, woodland, ridge, river, marsh) for fires and signs across edges (D2-72, D2-74) and danger (C-6) | world/edges.md | 37.4 |
| Q-18 | D2-74 amends D4-35: information/signs.md and perception need the cross-edge rule | spec/information | 37.4 |
| Q-19 | Overlapping fuse events in more depth (D2-82's simple rule for now): a fire set during a raid, two raids on one night, a raid while a fire spreads, a meeting on the road and a find on the same stretch; whether one event can cut another's fuse, and who is woken by which | proposals/fuse_events.md | 37.2 with 37.4 |
| ~~Q-20~~ | Built for Package A and B (24 Oct), choices the spec left open, for Zach to confirm or change: (1) the fuse's length by structure: wattle counted as a hut (no call), timber 1 act, stone 3; (2) `method: dibble` is now learned and untaught `no` (agents/modifiers.md), so nobody in the existing worlds can dibble until taught; (3) one who dies at home (no work yet that day) lies in the house, found at once by its household; (4) the decay table's warm and frozen multipliers apply in houses as well as outside; (5) on the road, offers in a meeting are goods for goods from what each carries (no promises); (6) two parties crossing between stretches meet on the stretch where the party from the road's first node is that night; (7) a road with no terrain and no landmarks holds nothing at all (no meetings, notices or traces): the comparison arm. Not built: hidden ways (parcels have no sides yet), fire as a fuse event (no house fire in the scheduler yet), wet timber unusable as fuel, scavengers | review 38.24 | 37.4, Zach to confirm | answered 24 Oct: D2-118 to D2-122 |
| Q-21 | Built for Package C (24 Oct), choices the spec left open, for Zach to confirm or change: (1) what draws a herd's step: the share of its need it would eat on a parcel (grazing, or a crop at the 1% trampling rate), plus a ripe crop's pull while much of it is left, and water when hungry; cows in milk that wandered walk home at dusk (a shut fence round home lets them in at its odds); the pull falls off 0.8 a step, and a fenced parcel counts at its odds; (2) "good pasture" is grazing at 0.3 of its best or more; a fed herd on poorer grazing also roams up to 8 steps; (3) a herd in a crop is fed only by what it tramples (1% a head), so a hungry herd leaves a trampled field; (4) a fence has levels whole, gappy and down: a herd gets through a gappy wood fence at 0.6 and a gappy wall at 0.2; a quarter of the build in mending brings a gappy fence back a level; materials go in with the work in proportion; a fence in a world file counts as mended this season; (5) walling is a mason's craft (a crew led by one who knows it); `work {what: shut the gate}` is also an act (0 units); (6) a herd drifting off the road's end it came from goes to its home parcel; off the far end, onto the road's end parcel there, with an event at that node (salience 0.6); (7) in the find call, driving a herd a stretch back costs the party two days, going after a group that broke away one; `accompany {to: back}` turns the party back with the herd; the taker's claim is access and withdrawal, grounds "found"; (8) a group that split off rejoins its herd when they are on one parcel the next day; (9) `searching` matches a herd's name, its holders' name, or "cattle", "herd", "beasts"; (10) offers in a meeting close when the meeting ends; an agreement made there has the road as its place; (11) a hidden end worn to 0.8 is a path everyone at the node knows; a wood felled below 0.3 of its timber is open ground to the eye (sight 0.8) for all noticing; unused, wear falls to about a twentieth over a season; (12) dibbling goes to an adult whose trade names farm work (sow, seed, reap, plough, hoe, field), drawn by a keyed draw; (13) the way from where one slept starts at one's house at the node, else the built ground; the arrival overview is drawn from the built ground and its houses, the striking fittings (a mill, a smithy, a bake oven, a granary), crops, herds, woods and water, and how many people are about; (14) the default road terrain is farmland; (15) generation does not make parcels yet, so sides and heights come only from world files (default centre and 1, not spoken); (16) the old rule that a stray herd walks home after a day is removed. | review 38.25 | 37.4, Zach to confirm (livestock items: 37.2) |
| Q-22 | Built for Package D (24 Oct), choices the spec left open, for Zach to confirm or change: (1) `part` is one-sided; (2) a pregnancy refuses `try` only once it shows (day 3); (3) "both adults" is the adult stage only; (4) the helper at a birth is any adult or elder in the same building, or out at the same place; (5) an infant travels only with its mother, weight 2; (6) a child eats from the stores at its place, then its family's hands; (7) children's work is forage, herd or hay (the watch not built); at the high dial half a unit is a half chance a day; a newborn knows that work at 0.5; (8) a child is named from its line's forebears, else a name nobody living has; (9) succession ties go to the earlier born, youths do not name, the eldest adult stands in; (10) the generator maps its years to days by the stages' starts (winters counted at 24 days a year, so most remembered winters are recent); (11) a world without `born` keeps its stages, its elders die at 0.01 a night; (12) a newborn knows the places its mother knows. | review 38.27 | 37.4, Zach to confirm |
| Q-23 | Built for Package F (24 Oct), choices the spec left open, for Zach to confirm or change: (1) an older world's `wood` is read as its trees, with young growth and dead wood in a copse's proportions; scrub with no wood state gets scrub's (so old worlds' scrub now gives firewood); (2) a forest turns to scrub under 40% of its trees and back above 45%; felling is done only on forest, so a wood's last 40% cannot be felled; (3) gathering gives 3 x the square root of how full the dead wood is; the pool's capacity rises with brash; (4) a gale throws 0.2% of the trees as windfall; (5) a house's floor is its size; each hearth or ring burns its heat; a house too big for its hearths is warmed in proportion (between housed and unwarmed); a fire ring alone 1.15 in the cold; (6) a fire in the open is shared by those sleeping out at one node, or one party on the road, those who chose a fire first; (7) food that wants a fire is eaten raw after all that needs none; fresh meat now counts as better cooked (1.5, raw 0.8); (8) axes are heard from any felling on a parcel; (9) children may be set to gathering firewood; (10) not built: game and forage reading the forest (cover, browse, light), drought and forest fire, wet timber. | review 38.28 | 37.4, Zach to confirm (resources, fuel: 37.2) |
| Q-RR1 | Checkpoint at every step, or every day plus the step's changes (measure on the region world) | spec/record/journal.md | 37.1 |
| Q-RR2 | On resume, restore each agent's running conversation exactly (default) or restart conversations at the resume day | spec/record/execution.md | 37.1 |
| Q-RR3 | The human player's first interface: the terminal or a local web page | spec/record/human_play.md | 37.1 |
| Q-RR4 | The physical writes outside `World.apply` (hunger, missed meals, offers closing; review 39.01 §5) become primitives | spec/record/journal.md | 37.4 |
| Q-RR5 | A replay test with shuffled completion order of model calls (nothing may depend on arrival order) | spec/record/execution.md | 37.1 |
| Q-RR6 | Who builds R1 (the journal written alongside today's files) in `cybertron2/engine/` (README rule 6) | board Post 7 | 37.4 with 37.1 |

## Flagged for later

Things Zach decided to add later, or parked, with where each is designed and what it waits on. Add a row whenever something is
flagged; strike it through when it is built or decided.

| # | Later | Decision | Designed in | Waits on | Owner |
|---|---|---|---|---|---|
| L-1 | Signs of slow change on long journeys | D2-89 | proposals/journeys.md §3 | slow states (eras, environment_state.md) | 37.2 |
| L-2 | Scavengers, with wild animals that attack herds and hunters and are drawn to food | D2-95 | things_in_places.md §6 | wild animals as a system | 37.2 |
| L-3 | Smell, simple: own salience and short reach | D2-101 | visibility.md §5 | nothing (any time) | 37.4 |
| L-4 | Wind direction (fire spreading by the wind; smell following it) | D2-101 | visibility.md §5 | fire spreading | 37.2 |
| L-5 | Building on landmarks: bridges, ferries, huts at a pass, wells, waystations, tolls | D2-108 | road_layout.md §4 | roads working in runs | 37.2 with 37.4 |
| L-6 | Overlapping fuse events in depth | D2-82 | fuse_events.md; Q-19 | fuse events built | 37.2 with 37.4 |
| L-7 | Waiting on a road for camps, tolls, patrols and ambushes (bandits) | proposed | road_encounters.md §4 | road meetings built | 37.4 |
| L-8 | Herds wandering onto edges: lost, found, searched for | proposed | livestock.md; road_encounters.md §3 | roads with stretches | 37.2 with 37.4 |
| L-9 | Disease (mortality, the sick, immunity, nursing, a healer); rot's risk feeds it (D2-96) | Q-16 | environment_catalogue.md §3 | | 37.2 with 37.1 |
| L-10 | Irrigation | D2-67 | farming.md | the weather | 37.2 |
| L-11 | Fences, hedges and walls for herds | proposed | fences.md; livestock.md | | 37.4 |
| L-12 | Children and life ("we'll come back to this") | | life.md | | 37.4 with 37.1 |
| L-13 | Economy options kept out of the first worlds: slash and burn, armour, nets, boats, the seed drill, clay, iron, the press | D2-14, D2-19 | economy_later.md | | 37.2 |
| L-14 | Clothing | D2-10 (parked) | resources_and_goods.md | | 37.2 |
| L-15 | Hiding in a building | 22 Oct (deferred) | information_economics.md | | 37.4 |
| L-16 | Reflexes, fallbacks and policies as standing orders | D4-16 | 38.06 §4 | | 37.4 |
| L-17 | Aims (cybertron 1's goals, edited) | D4-29 | spec/agents/aims.md | | 37.4 |
| L-18 | An institution's stamp on coin | D2-28 | exchange_and_money.md | institutions | 37.2 with 37.3 |
| L-19 | Further verb modifiers (going quietly, working carefully) | D2-93 | verb_modifiers.md §1 | modifiers built | 37.4 |
| L-20 | The catalogue's later kinds (storm surge, locusts, anthrax, peat fires, the dark year, migration and trade eras, landslides) | D2-77 | environment_catalogue.md §6 | | 37.2 |
| L-21 | Fire: house fire and wildfire in the scheduler, spreading along the parcel graph and edges; setting fire in a raid; fire as a fuse event (D2-49 to D2-51, D2-72 decided) | 24 Oct | attacks_and_walls.md; environment.md | | 37.2 with 37.4 |
| L-22 | Raiders and other outside agents arriving with goals (D2-76): seeding transient populations; needed to test raids live | 24 Oct | environment_catalogue.md §1 | | 37.4 |
| L-23 | Water as a need, and the land's hidden state (water table, wells, latrines, middens, cleanness: environment_state.md, all six of its questions) | 24 Oct | environment_state.md | | 37.2 |
| L-24 | Fences on the borders between parcels (rather than round a parcel); hedges; night folds; wolves | D2-130 | fences.md; livestock.md | the parcel graph and fences round parcels built | 37.2 with 37.4 |
| L-25 | **Beliefs, values and customs** (a large future integration): customs and values held by people, not villages; seeded per village and household; passed on in childhood and by exposure (hearths, campfires, travellers); distinct from know-how (explain is about ability, this about belief); children's values permeable, adults' firmer but open by choice or repeated exposure; family values passing down, cultural evolution, a state raising children to believe something | 24 Oct (Zach: needs more thought and design) | proposals/beliefs_and_values.md | children built; knowledge.md; law.md | 37.2 with 37.3, 37.4 |
| L-26 | Care's effects beyond survival: a cared-for child growing into a healthier (less frail) youth, and one taken along to work starting with some practice in it | D2-150 | proposals/children.md §3 | children built; with L-25 | 37.2 with 37.4 |
