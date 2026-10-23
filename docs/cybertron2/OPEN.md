# cybertron2: open questions and conflicts

Each item has an owner (README "Who owns what") who resolves it, with Zach where it needs a decision. Resolved items move to
[DECISIONS.md](DECISIONS.md) or into the spec, and are struck through here. Compiled 22 Oct 2026.

## Conflicts between documents

| # | Conflict | Where | Proposed resolution | Owner |
|---|---|---|---|---|
| C-1 | Carrying capacity: on foot 20, pack 35, animal +60, cart +150 | 38.06 §3 vs 02g §3 (on foot 10, pack 20, pack ox 60, handcart 40, ox cart 200, wagon 500, boat 1,500) | take 02g's numbers (calibrated against grain's cost); 06's table superseded | 37.2 (numbers) |
| C-2 | Building limits: slots by land kind | 38.04 §1 vs 02e §3.9 lots, 02i parts | lots and slots are the same thing (land per node, by kind); parts decide what a building does | 37.4 with 37.2 |
| C-3 | Speech at a node: one talk step | 38.05 §1 vs 02h §4a (the square, rooms by access, private messages) | the talk step delivers in 02h's three scopes | 37.4 |
| C-4 | Letters and channels | 38.05 §5 (letters, errands) vs 02h §4 (channels with a medium and a location; boards, carried editions, boxes) | letters and boards first, on 02h's channel record; editions later | 37.4 with 37.2 |
| C-5 | Riders who travel and strike in one round | 02g §5b vs D4-8 (arrive, then decide) | a fuse event (02k): riders shorten detection to almost nothing, so no exception to D4-8 is needed | 37.4 (Zach to confirm) |
| C-6 | Danger on the road | 38.05 §2 (a risk draw per night) vs 02g §3b-3c (danger per edge by terrain and season, per rung) | 02g's table as the draws of the 37.4 scheduler | 37.4 |
| C-7 | The handoff README's next steps and document list | 38 README §2, §7 | superseded by this folder; README gets a pointer | 37.4 |
| C-8 | Environment design for the old engine (calendar, micro-events, foresight) | `wp/environment`: 04_environment_design.md, cybertron/environment.py | redesigned for cybertron2 in spec/environment.md; the old branch marked superseded | 37.4 |
| C-9 | Ages: calendar years | 38.09 §2a-2b vs D4-19 | D4-19 wins | 37.4 |

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
| Q-20 | Built for Package A and B (24 Oct), choices the spec left open, for Zach to confirm or change: (1) the fuse's length by structure: wattle counted as a hut (no call), timber 1 act, stone 3; (2) `method: dibble` is now learned and untaught `no` (agents/modifiers.md), so nobody in the existing worlds can dibble until taught; (3) one who dies at home (no work yet that day) lies in the house, found at once by its household; (4) the decay table's warm and frozen multipliers apply in houses as well as outside; (5) on the road, offers in a meeting are goods for goods from what each carries (no promises); (6) two parties crossing between stretches meet on the stretch where the party from the road's first node is that night; (7) a road with no terrain and no landmarks holds nothing at all (no meetings, notices or traces): the comparison arm. Not built: hidden ways (parcels have no sides yet), fire as a fuse event (no house fire in the scheduler yet), wet timber unusable as fuel, scavengers | review 38.24 | 37.4, Zach to confirm |

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

