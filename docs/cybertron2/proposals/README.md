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
| [households.md](households.md) | membership, use and home as data agents change: admit and leave, grant use of a house, home derived, occupy an empty house (possession and a claim), build one from parts; the night follows use | 37.4 (37.2: building costs) | partly accepted: D4-36 |
| [place.md](place.md) | place as the foundation: every entity and event has a place; state partitioned by node; agent-facing code gets only a view of where the agent is (`Here`) and its own mind (`Mind`), never the world; only travel moves anything between nodes; static and canary tests | 37.4 | accepted in principle: D4-35 |
| [layout.md](layout.md) | the layout inside a node: parcels of one cover (forest, field, pasture, water, built ground...) with neighbours and a side; features (brook, road, well, seam); structures on built ground; movables on a parcel or in a room; attention, claims and land change on one model | 37.4 | discussion |
| [parcel_graph.md](parcel_graph.md) | parcels as a graph of neighbours shaped by the land, each with a side and a height; no coordinates or walking; sensing along the way; attending to the village; an overview on arrival | 37.2 (37.4 owns places and perception) | partly accepted: D2-114 to D2-116 |
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
| [environment_state.md](environment_state.md) | the hidden state of places and things: a few variables per parcel, water, building, herd, person and node, damped, one step a day; hazards read them, incidents and people's acts write them; cascades; low-salience signs | 37.2 | discussion |
| [environment_catalogue.md](environment_catalogue.md) | what can happen: eras (climate, disease, ecology, outside pressure), weather by land kind, hazards that spread (fire, crop, livestock and human disease) in six patterns; how people prepare, respond and recover | 37.2 | partly accepted: D2-76 to D2-79 |
| [environment.md](environment.md) | one scheduler for eras, years, spells, incidents and spreads; each layer sets the odds of the next; paired draws; consequences and signs read by presence, salience, skill and concern | 37.2 (owns spec/environment: D2-75) | partly accepted: D2-69 to D2-75 |
| [road_encounters.md](road_encounters.md) | meetings on the road as fuse events: travellers going opposite ways, lost herds, searches; later waiting on a road for camps, tolls and ambushes | 37.2 (37.4 owns travel and combat) | accepted: D2-81, D2-110; waiting later |
| [journeys.md](journeys.md) | what travellers see on the way: daily notices on the road (others, herds, a body, traces left by passers), remembered on arrival; rare signs of slow change on long journeys | 37.2 (37.4 owns perception and roads) | accepted: D2-88, D2-89, D2-97 |
| [hidden_ways.md](hidden_ways.md) | edges tied to a side and parcels, some hidden; found by work in the parcel, attention, knack and traces; the finder chooses whom to tell | 37.2 (37.4 owns edges and knowledge) | accepted: D2-90 to D2-92, D2-98 |
| [things_in_places.md](things_in_places.md) | one kind of thing at a spot (a parcel, or a stretch of road: one per day of its length): goods left or hidden, remains, herds, camps, traces, hidden ways' ends; one noticing rule (conspicuousness x presence x attention x knack x traces); a find on the road worth taking gives a short call; left things held by nobody | 37.2 (37.4 owns places and perception; extends objects_in_world.md) | partly accepted: D2-85 to D2-87, D2-95, D2-96 |
| [road_layout.md](road_layout.md) | a road as one place with stretches and a few landmarks (ford, bridge, pass, narrows, spring...): events happen where on the road; landmarks decide crossing challenges and risks; bridges, huts and tolls built on them | 37.2 (37.4 owns edges and travel) | accepted: D2-104 to D2-109, D2-113 |
| [verb_modifiers.md](verb_modifiers.md) | modifiers on verbs as data (`for`, `hidden`, `searching`, `method`, `aim`): the same act done another way, nothing by default, some common and some learned | 37.2 (37.4 owns verbs and knowledge) | accepted: D2-93, D2-94, D2-111, D2-112 |
| [visibility.md](visibility.md) | how much a place and the day let each sense through: sight and sound by cover, changed by the land's state (felling, crops, snow, building) and by light and weather; multiplies every sign | 37.2 (37.4 owns perception) | accepted: D2-99 to D2-103 |
| [recipes.md](recipes.md) | the first worlds' recipes as technique cards: gathering, making, building, working; basics and ten trades; tool wear; what travels; price anchors | 37.2 (37.4: verbs, knowledge) | discussion |
| [hiring.md](hiring.md) | work for someone: `for` on work actions puts output into the employer's container; day labour, piece rate, wages, sharecropping, tenancy, apprenticeship, shopkeepers, guards, carriers | 37.2 (37.4, 37.3) | accepted: D2-36 to D2-40 |
| [agreements.md](agreements.md) | one system of agreements made of legs (cybertron 1's Standing Contract): trade, credit, subscriptions, wages, rent, dues; paid where there is a path, else arrears; ledgers; currency wanted, not required | 37.2 (37.4, 37.3) | accepted: D2-31 to D2-36 |
| [exchange_and_money.md](exchange_and_money.md) | exchange at a node, coin, debts, credit, tolls | 37.2 | accepted: D2-1, D2-2, D2-25 to D2-30, D4-17 |
| [information_economics.md](information_economics.md) | writing materials, documents, the information ladder, libraries, archives, maps | 37.2 (37.4 owns information/) | partly accepted: D2-7, D2-8 |
| [economy_plan.md](economy_plan.md) | the economy plan for cybertron2 (E1-E6, the first region) and society-scale layers | 37.2 | discussion |
| [fuse_events.md](fuse_events.md) | events with a detection time and a completion time; urgent calls for those who notice in time | 37.2 (37.4 owns conflict/, core/) | accepted: D2-5, D2-80 to D2-84 |
| [gates.md](gates.md) | boundaries with entry rules: names, passes, tolls, a keeper; admission in the talk step | 37.2 (37.4 owns conflict/) | accepted: D2-5 (details open) |
| [attacks_and_walls.md](attacks_and_walls.md) | attacks on people, buildings and nodes; walls multiplying defenders; the watch | 37.2 (37.4 owns conflict/) | partly accepted: D2-20 to D2-22 |

## Log of ideas and their outcomes

Newest first. Ideas decided or rejected in conversation before 23 Oct are backfilled from the 37.4 work log and DECISIONS.md.

| Date | Idea | Outcome | Where |
|---|---|---|---|
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
| 23 Oct | Objects placed in the world: leave on a parcel, noticed by anyone, whose they are | discussion (to explore) | [objects_in_world.md](objects_in_world.md) |
| 23 Oct | Fences, hedges and stone walls as field works that keep beasts in or out | discussion | [fences.md](fences.md) |
| 23 Oct | The senses: an eye for the land (some have none) and signs of bareness scaled by how bare | partly accepted: D4-50 | [senses.md](senses.md) |
