# cybertron2: decisions

Every decision Zach has made about cybertron2. Append only; a later decision that replaces an earlier one says so in its
`Replaces` column, and the earlier row is marked `replaced by`. Number series by session (README rule 2): **H** the handoff
(decisions Zach made in the 37.2 session before 37.4 took cybertron2 over), **D2** the 37.2 session, **D4** the 37.4 session.
Compiled 22 Oct 2026 from: `docs/review/38_space_engine/README.md` §3 (H), `devlog_37.4.md` and the 37.4 conversation (D4),
`docs/review/37_growth/02*` and `02_economy_worklog.md` (D2). **37.2: please check the D2 rows and the "directions" list below,
and correct them in place.**

## Decisions

| Id | Date | Decision | Source | Replaces |
|---|---|---|---|---|
| H-1 | 22 Oct | Space is a **new engine in its own package**, `cybertron2/`; the old engine is frozen for the bench batches and published runs | 38 README §3.1, 00_plan | board Post 2's retrofit |
| H-2 | 22 Oct | Port the physical systems onto nodes; copy the institutional layer keeping its interface and fixes; import only leaf modules unchanged | 38 README §3.2 | |
| H-3 | 22 Oct | Test with LLM agents early, in small worlds; scripted bots only as smoke tests | 38 README §3.3 | 37 README's "no model usage" (for cybertron2) |
| H-4 | 22 Oct | Worlds are almost always **seeded with an existing society** | 38 README §3.4 | |
| H-5 | 22 Oct | Shelter: houses with upkeep and rare breaks; a lack of shelter raises the food needed; in the cold an unsheltered agent falls straight to starving with chance 0.3, no separate exposure | 38 README §3.5, 02e §3.3 | |
| H-6 | 22 Oct | Foraging is the degenerate case: 1-2 actions for 1-3 food, more with hunting parties | 38 README §3.6 | |
| H-7 | 22 Oct | **Perception matters most**: what agents see, and how it changes, is the main design surface | 38 README §3.7, 02_perception | |
| D4-1 | 22 Oct | Start from what 37.2 built and extend it; what does not match the plans is redesigned, not patched | devlog 37.4 #1 | |
| D4-2 | 22 Oct | **A node is a village, a valley or a camp**; places used routinely are sites inside one node; an edge is a real trip | devlog #2, 04 §1 | the phase-0 places (one place per wood or meadow) |
| D4-3 | 22 Oct | Travel takes time; no moving as a pre-action | devlog #3 | replaced in part by D4-8 |
| D4-4 | 22 Oct | **External change is separate from internal consequences**: eras, cycles and incidents drawn from the seed, the same in every arm, one central scheduler; depletion, exhaustion and collapse are the resources' own physics | devlog #4 | |
| D4-5 | 22 Oct | **Three time scales**, each modulating the one below: eras and trends, cycles, incidents | devlog #5 | |
| D4-6 | 22 Oct | **Signs**: at most one in-world sentence, with an audience, a lag and a reliability, kept separate from the effects | devlog #6 | |
| D4-7 | 22 Oct | Resources by how they come back: finite, fast renewable, renewable with a threshold, slow, periodic | devlog #7 | |
| D4-8 | 22 Oct | **Arrive, then decide**: travel is the last act of a day; the traveller arrives at the start of the next round, sees the place and decides there | devlog #8, 05 §2 | D4-3 (same-round hops rejected) |
| D4-9 | 22 Oct | **Transport and communication between nodes are delayed and carried**: goods, letters and people cross only with someone; merchants carry trade, messages and passengers | devlog #9 | |
| D4-10 | 22 Oct | Both kinds of distance: edges with a length (travellers in transit make no call) and real waypoint nodes | devlog #10, 05 §2 | |
| D4-11 | 22 Oct | **Node scale: if you could go there and be back before nightfall, it is the same node**; a larger settlement is a cluster of nodes | devlog #11, 04 §1 | |
| D4-12 | 22 Oct | A night out costs 1.5 food (2 in winter, and the cold); **hosts and inns** are part of the design | devlog #12, 04 §1, 05 §3 | |
| D4-13 | 22 Oct | **A round is a day**; the calendar is compressed (year length a world setting, about 16-60 days) | conversation; 05 §1 | |
| D4-14 | 22 Oct | **Everyone plans at once** (cybertron 1's simultaneous mode); only the talk step asks anyone again | conversation; 05 §1 | |
| D4-15 | 22 Oct | **Speech is not a round late**: a message step among the people at the node before work (cybertron 1's DM step, limited to the node) | conversation; 05 §1 | the phase-0 rule (speech heard at round end) |
| D4-16 | 22 Oct | Routine work runs on standing orders the agent sets; reflexes, fallbacks and policies come later | conversation; 06 §4, §6 | |
| D4-17 | 22 Oct | Units a day and the action cost table are **settled by experiment**; **daylight varies by season**; a shop needs a shopkeeper | devlog #13, 06 §6 | |
| D4-18 | 22 Oct | **Institutions grow from households**: villages, then specialised institutions within them, then companies and a state; an institution can be a member of another from the start | devlog #14, 09 §3b | |
| D4-19 | 22 Oct | **Short childhoods counted in rounds**: 1-3 rounds cared for, 3-4 rounds of menial tasks (no model call), then a youth as an agent; prompts name life stages, never ages in years; no time skips; youth learn faster and keep it longer | devlog #15, 09 §3b | 09 §2a's calendar ages |
| D4-20 | 22 Oct | **One agent, one model, for life**: chosen when it becomes an agent; heirs to pole seats take the seat's model; the rest keep the cast balanced | devlog #16, 09 §3b.5 | |
| D4-21 | 22 Oct | **Worlds are seeded as a society with a past**, with a full family tree of the whole population (living and dead, back to the founders; every kin tie derived from it), relationships, debts, holdings, standing, institutions and a short history, written into each agent's knowledge from its own position | devlog #17, 09 §3c | |
| D4-22 | 22 Oct | The landscape is generated physical-first (elevation, moisture, rivers by drainage, kinds from terrain), every layer overridable by hand | conversation ("I like this"); 04 §5-6 | |
| D4-23 | 22 Oct | **Holding is a recognised claim.** The engine enforces only possession; claims (rights, grounds, since) are records and memories; recognition by custom or an institution's register makes a holding, and an institution's code may bind its own members; individuals, households, institutions and joint holders can hold; two claims make a dispute (feud, border); land is counted in whole plots, holdings divided, plots never split; viability is land per mouth; one routed primitive moves a claim | spec/world/holding.md | the old engine's holder field enforced by the engine |
| D4-24 | 23 Oct | **The world grows by data, and agents explore and learn it**: new and richer actions are added as data (techniques, fittings, settings, powers, clauses) on a small set of verbs, and agents come to know them in the world (seeing, being told, taught, reading, trying), not from a complete manual | proposals/verbs.md, knowledge.md | |
| D2-1 | 22 Oct | **Coin is carried; debts move only as information** | 02f §6.1 | 37.4's proposal "money and credit move anywhere" |
| D2-2 | 22 Oct | One merchant household with a cart is seeded in the first region | 02f §6.2 | |
| D2-3 | 22 Oct | Large buildings and buildings of 2-3 storeys must have stone; building up costs more | 02i §2b-2c | |
| D2-4 | 22 Oct | **Agents are never told someone is missing**: the household saw the departure and remembers the stated plan; a death on the road is never announced | 02g §3c, board | the phase-0 "not seen for N rounds" line |
| D2-5 | 22 Oct | **Fuse events** are worth adding (rare; only a subset of people woken); **gates** check arrivals automatically first, otherwise the keeper and the arrivals talk on the day they arrive | 02k | |
| D2-6 | 22 Oct | **One livestock system, bred not made**: cattle and horses are kinds of livestock that breed from a herd; wild herds live on grassland ("fields where horses just naturally are") | 02g §2b-2c | 02g §2's separate horse good |
| D2-7 | 22 Oct | **Speech at a node:** the square is everyone there; private messages to anyone at the node; everyone sees what is said in the buildings they have access to at their node, and can speak in several in one day | 02h §4a | |
| D2-8 | 22 Oct | **Wide reach costs more:** rumour travels with merchants for free; letters, and later papers that are centralised and delivered, have costs and charges | 02h §4b | |
| D2-9 | 22 Oct | **Buildings are made from parts** (structures, rooms and fittings, each with resource costs), not from template buildings; rooms can be booked (a room is a channel); capacity can be extended, larger and adjoining rooms costing less per person | 02i §1-§2b, §4 | template buildings |
| D2-10 | 22 Oct | **Clothing is parked**; shelter (houses) carries the cold instead | 02 worklog (parked) | the direction "clothing as a worn stock" |
| D2-11 | 22 Oct | **Farming's minimum is short, the other stages optional:** sow and reap give a crop; breaking the soil, weeding, manure, rotation and grazing the fallow each cost work and give a better return (more food per plot, or soil that does not wear out), worth most to those who can do them and at scale | 02l §1-§2 | the old engine's fixed sow, tend, reap |
| D2-12 | 22 Oct | **A harvest window:** a ripe crop not reaped in time rots | 02l §2 | |
| D2-13 | 22 Oct | **Worlds start with farming under way:** crops in the ground, last year's grain (and seed) in store | 02l §8 | |
| D2-14 | 22 Oct | First worlds farm with **the hoe and the ox plough** only (slash and burn, irrigation and the rest later) | 02l §1 | |
| D2-15 | 22 Oct | **More hands on a plot raise its yield** on a saturating curve; cattle add to it; part of the return to labour comes from doing the further stages | 02l §2 | the old engine's two tends |
| D2-16 | 22 Oct | **Nodes differ in land pressure:** some short of land, some of people | 02l §5 | |
| D2-17 | 22 Oct | **Seed is kept back** from each harvest | 02l §2 | |
| D2-18 | 22 Oct | **Cattle on the farm:** the plough needs an ox, fodder takes land, dung keeps the soil. Households need **land to live on**, with a capacity | 02l §5-§6 | |
| D2-19 | 22 Oct | **First worlds start with a short metal ladder** (not both bronze and iron) | 02j §3 | |
| D2-20 | 22 Oct | **Three kinds of attack:** on a person; on a building (a break-in whose work depends on the structure, then a fight with whoever defends); on a whole node (targets drawn by exposure, value and hardness, so a stone building is less likely to be picked and stronger when it is). **Walls multiply the defence of those inside** | 02k §3 | combat.py's raid on a house only |
| D2-21 | 22 Oct | **The watch:** a watcher skips the night's sleep and eats more for it, detects first and can wake the others; households rotate it; children can keep it | 02k §3 | |
| D2-22 | 22 Oct | **Any party may raid a node:** no minimum size; a small party usually fails and the outcome depends on the defences; a single rider may attack, at greater risk | 02k §3 | 02k's proposal (riders and large parties only) |
| D2-23 | 23 Oct | **The tool set:** hand tools as one good with grades (crude, then metal); the plough (needs an ox); carts; weapons (fighting, and hunting); **traps** (catch game overnight while the trapper is elsewhere); **harness** (an ox pulls) and **saddle** (a horse carries a rider). Armour, nets, boats and the seed drill wait (proposals/economy_later.md) | 02j §3; conversation | 02g's single "tools and blades" good |
| D2-24 | 23 Oct | **The first-world goods include copper, salt, documents, hides and timber** (with grain, wild food, livestock, stone, coin and the tool set already decided) | proposals/resources_and_goods.md; conversation | |

## Directions (Zach's stated aims recorded in the notes; designs follow them; checked by 37.2, 22 Oct)

Promoted to decisions by 37.2's check: buildings from parts (D2-9), speech at a node (D2-7), wide reach costs more (D2-8), one
livestock system (D2-6); clothing was parked, not adopted (D2-10).

- Resources that unlock new capabilities, not only more output (02g §1d); some resources hard to get but valuable (02g §1c).
- **Information comes first** among the new capabilities: maps, parchment, writing (02h).
- Fewer goods: a good or step stays only if several things use it, it makes a chokepoint or a trade, it changes weight or shelf
  life enough to matter, or it unlocks something (02g §1f).
- Edges differ in danger by terrain and season (02g §3c); carts lower danger; the transport ladder also carries people and rest
  (02g §3b).
- Horses for speed and fighting (02g §2b); whether riders may arrive and strike in one day is open (OPEN C-5).
- Start the economy from end uses, roots and processes; ladders whose better rungs need a new resource, a long chain or scale (02j).
