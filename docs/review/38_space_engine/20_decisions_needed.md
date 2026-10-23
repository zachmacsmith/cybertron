# Review 38.20: the decisions still open, by what they block

Session 37.4, 23 Oct 2026. Every open question in `docs/cybertron2/proposals/` and `OPEN.md`, as of commit b325c5f, when every
decision in `DECISIONS.md` is written into a spec file. Grouped by what each blocks in the engine, in the order the build needs them
(38.08's milestones, 37.2's phases E2-E6). Each has the proposal's own answer where it has one. Answer by number ("A1 yes", "B3: a
role"); answers become decisions in `DECISIONS.md` and the spec, by the owner of the file.

Owners: **37.2** economy content and numbers; **37.4** mechanisms, places, agents, information, conflict; **37.1/37.3** life and
institutions when they join.

## A. Farming (blocks E3: the farming stages; owner 37.2)

| # | Question | Proposed answer | Note |
|---|---|---|---|
| A1 | The stages' work and returns | 02l §2: sow 0.5 a plot; break the soil with a hoe 3 or an ox plough 0.75, for a harvest +1.5x the seed; weeding +24% / +37% / +43% for 1 / 2 / 3 units; manure 1 (needs dung); reap 1.5 with a sickle, 2.5 bare-handed; threshing folded in | the engine has sow, weed, reap only; tools speed reaping but add nothing per plot |
| A2 | Soil | fertility multiplies the harvest; each grain crop takes 15% of it; legumes, fallow, grazing and dung restore it toward a level (grain every time settles about 0.43, three-field about 1.04) | the engine's fertility is fixed |
| A3 | Crops and the cold | growth counted from the day sown; winter kills what is growing unless hardy; crops: grain, winter grain, legumes (60% of grain's food, restore soil), hay; the same crop twice raises failure from 5% to 15% | crops currently grow through winter |
| A4 | Crop cycles in days or as shares of the year | shares of the year (so they follow the world's year length) | |
| A5 | The plot unit | about what one adult works in a season by hoe and weeding; the ox plough lets one adult work 1.5-2 plots | the engine's fields are sizes with a seed cap |
| A6 | How plots, lots and pasture share a node's land | (asked of 37.4) parcels by cover, as built: fields counted in plots, pasture parcels with a grazing stock, built ground in lots | 37.4's answer, needs your yes |
| A7 | Sowing | work per unit of seed, not per plot; broadcasting (fast, wastes seed) or dibbling (about 3x the work, about 40% less seed) | your remark of 23 Oct; still a proposal |
| A8 | A garden on the house lot | worked with spare units; fast, small, spoils | |
| A9 | Weeding: one stage on a curve, or several tends | one stage on a curve (as built) | |
| A10 | **Food's share of work** | target 25-30% of a day; at 02l's numbers it is about 10% (the engine measures about 8%, 38.19) | the largest open lever: what absorbs the rest (seed, milling, storage, winter, fodder, upkeep, fewer units) |

## B. Livestock (blocks oxen, the plough, harness, ox carts, dung; owners 37.2 numbers, 37.4 mechanism)

| # | Question | Proposed answer | Note |
|---|---|---|---|
| B1 | Pasture | parcels of pasture cover with a grazing stock (as built) | |
| B2 | Breeding, milk, herding numbers | "cattle about 0.10 of the herd a round, horses 0.05" (livestock.md) | written per round; with a round a day (D4-13) that is 10% a day, far too fast: needs rescaling to the year |
| B3 | Oxen | a kind of animal, or a role within cattle (some cows in milk, some oxen) | not in any proposal |
| B4 | Winter fodder | hay cut from pasture in summer, straw from the grain harvest; numbers by dry run | |
| B5 | Harness | made by the leatherworker (D2-43) from hides; costs in tools.md | |
| B6 | Dogs | a third kind in the same system, or not | |
| B7 | A common herd's rules | a law's clauses (law.md) or custom | |

## C. Skill and the day's work (blocks E2; owners 37.2 and 37.4)

| # | Question | Proposed answer | Note |
|---|---|---|---|
| C1 | **Skill by practice** | a continuous curve, 0.5 novice to 2.0 master, rising with practice and decaying unused (02c §5; knowledge.md, economy_plan E2) | the engine raises skill only on non-basic crafts; nobody gets better at farming or felling |
| C2 | Does it apply to basic work (farming, felling, foraging)? | yes in 02d's model, where it carries most of the village's gain | |
| C3 | The automation rule | transfers and standing offers free; routine work spends units; decisions never automated | standing orders (D4-16) are decided, not built |
| C4 | Units a day and the cost table (OPEN Q-1) | summer 7, autumn 6, winter 5, spring 6 (calibrate) | settled by experiment (D4-17) |
| C5 | Overexertion and working late (Q-2) | x1.5 food, x2, then exhaustion | |
| C6 | The levers for a 2-2.5x organised advantage (02d §5b) | master skill 3, metal x1.5, crude x0.7, porridge 0.8, mill 1.6, forest halved | written for one node; with the mill serving several nodes (your answer, 23 Oct) the mill levers may not be needed |

## D. Tools and metal (owner 37.2)

| # | Question | Proposed answer | Note |
|---|---|---|---|
| D1 | Tool effects by method | felling x2; quarrying, mining, reaping, hay x1.5; foraging none (recipes.md §8) | as built |
| D2 | Do copper tools exist at all? | a calibration choice: in 02j copper returns 2.0x against crude 1.8x; bronze 4.3x and iron 4.5x are the real jumps | |
| D3 | Which metal rung first worlds have | bronze (needs tin, by trade) or iron (charcoal, skill); D2-19 says one | |
| D4 | Great trees and great beams | a small stock in woodland, felled only with a felling axe and a crew | |
| D5 | Trap numbers | by dry run | |
| D6 | The iron-axe and charcoal loop | later | |

## E. Goods, transport and the first region (owners 37.2, 37.4 for edges)

| # | Question | Proposed answer | Note |
|---|---|---|---|
| E1 | recipes.md as a whole | the engine runs on its numbers now, marked calibrate; accept it as the calibrate base? | |
| E2 | Carrying capacities (OPEN C-1) | 02g: on foot 10, pack 20, pack ox 60, handcart 40, ox cart 200 | as built, except the ox |
| E3 | Danger on edges (C-6), and the chance a body is found | 02g's table as the scheduler's draws; about 50% on a short edge | |
| E4 | Tracks and roads as works | cost, upkeep, who builds them | the engine has tracks as data only |
| E5 | The first region's inn and host | an inn at Millford, a host at the pass | |
| E6 | Salt's place | at the pass's waypoint or in the hills | |
| E7 | The hard tier (iron, tin, silver, old oak, wild horses, goods from beyond) | when each enters | |

## F. Buildings and shelter (owner 37.2)

| # | Question | Proposed answer |
|---|---|---|
| F1 | Rescale 02e's per-round shelter numbers to day rounds | needed |
| F2 | Beds as a soft limit | yes: over them is "poorly housed" |
| F3 | Lodging for single agents | a spare bed for rent, or a lodging house |
| F4 | Deforestation | a managed woodlot (coppice) under rules on felling, with the forest's regrowth |
| F5 | Parts | the cost curve's exponent; x0.8 for adjoining rooms; upkeep per fitting and room; fire spreading from forges and kilns; lots = slots (OPEN C-2: proposed yes) |

## G. Households (owner 37.4; proposals/households.md)

| # | Question | Proposed answer | As built |
|---|---|---|---|
| G1 | Does a night's welcome include a meal? | optional: the host says | `host {feed}` |
| G2 | Who may admit someone or grant use of the house? | the household's own rule, seeded default | head only by default |
| G3 | An emptied house | stays held by the old claim until abandoned (how long?) | stays held |
| G4 | May two households merge? | | no |

## H. Agents, knowledge, seeing (owner 37.4)

| # | Question | Proposed answer |
|---|---|---|
| H1 | **The verb set** (verbs.md, ready for a decision) | the lean set of 24; `steal` kept separate from `move` |
| H2 | Stealing | allowed when unseen; noticed later by the owner as missing |
| H3 | Fleeing and yielding | chosen actions now, reflexes later |
| H4 | A coverage test: every mechanic reachable by a verb | yes |
| H5 | Teaching: how long; can watching alone teach, after how many times | one session to capable; watching teaches slowly (counts in knowledge.md §4c) |
| H6 | Do written recipes need literacy? | yes (02h) |
| H7 | Invention | later, or never |
| H8 | Prerequisites and tiers within a trade | |
| H9 | Seeing: how many a glimpse covers; one attention target or more; noticing being watched; which observations first; templates or a narrator | templates first, the narrator as an experiment |
| H10 | Notes: how many, how long, how many opened a step, whether they fade | 8 notes, 150 words, 2 opened |
| H11 | Seeing within a node by site (parcel, building) | later; the node boundary is fixed by D4-35 |
| H12 | Can travellers meet on a road (see, trade, fight)? | possible in the engine; a separate decision |
| H13 | Seeded knowledge of elsewhere | kin, roads and a repute line at seeding, then visits and being told (as built) |
| H14 | Parcels a node; rivers and roads continuing between nodes | 5-15 parcels |

## I. Conflict (owners 37.4 mechanism, 37.2 numbers)

| # | Question | Proposed answer |
|---|---|---|
| I1 | Break-in work by structure; do tools shorten it? | proposals/attacks_and_walls.md |
| I2 | Wall multipliers; does a village wall multiply guards on it? | timber x1, stone x2 |
| I3 | The watcher's food | x1.5 |
| I4 | Exposure weights in a node raid | herds, crops, open stores, people outside first |
| I5 | Fire: catch chances, the bucket line, waking, death inside | 0.8 wattle to 0 vault; about 0.9 death inside |
| I6 | Fuse events: which first; the cap on urgent calls; order of overlaps; the urgent call's prompt | raids on stone buildings, fire, arrivals at a shut gate |
| I7 | Riders who travel and strike in one day (OPEN C-5) | no exception to D4-8: riders leave almost no fuse |
| I8 | Gates: does the re-ask count as a talk wave; tolls in goods before coin; the rule as a holder's setting or a law; what arrivals see | |

## J. Life (owner 37.4 until 37.1 joins; no proposal file yet)

38.09 has the design; none of it is decided beyond D4-19 and D4-21. Blocks children, ageing, death and heirs.

| # | Question |
|---|---|
| J1 | Conception and birth: who, how often, what it costs a household (food, the mother's work) |
| J2 | How long a youth lasts and lifespans in rounds (OPEN Q-5) |
| J3 | Death by age and illness in a run |
| J4 | Inheritance: of claims (whole plots, eldest first: holding.md), of goods, of the head's office |
| J5 | Children's menial tasks (D4-19): which, and what they yield |

## K. Institutions and law (owner 37.4, reviewed by 37.3)

| # | Question |
|---|---|
| K1 | The first clause menu (about ten clauses) |
| K2 | Who may change a register, and with what witness |
| K3 | How a clause's application is shown to those it binds |
| K4 | Courts: judge, elders or assembly; what a ruling can do |
| K5 | cybertron 1's full law language, or a smaller one |

## L. Environment and land (owner 37.4)

| # | Question | Proposed answer |
|---|---|---|
| L1 | Year length and season lengths (OPEN Q-4) | a world setting, 16-60 days; seasons equal |
| L2 | Which signs, incidents and eras first (Q-8) | |
| L3 | The climate axes and eras by land kind (38.04 §3) | |
| L4 | First land kinds (Q-7) | river valley, woodland, hills, crossroads |
| L5 | A node's population limit: a hard cap or a crowding cost (Q-6) | |
| L6 | Clearing and draining to make new fields (holding.md: "clearing and draining add plots") | the mechanism, its work and what it costs the forest |

## M. Information economics (owner 37.2, mechanism 37.4)

| # | Question |
|---|---|
| M1 | Documents as objects (text, author, seal, copies) and their acts |
| M2 | Channels as media in places: boards, boxes, editions (OPEN C-4) |
| M3 | Archives and institutions as buildings |
| M4 | Wax tablets: worth a good? |

## What blocks the next build

The economy's next phases (E2 skill and work, E3 farming and livestock) need **A1-A3, A5, A10, B2-B4, C1-C2 and E1**. With those,
the engine can build the farming stages, the soil, oxen and the plough, skill by practice, and the ox cart, and the first region
can be run at the scale economy_plan.md sets. Everything else can follow in the order above.

*Supporting material for OPEN.md; nothing here is decided.*
