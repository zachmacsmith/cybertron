# 37.2j From roots to end uses: every path costed in actions

> **Status (23 Oct):** the current state of these ideas is in `docs/cybertron2/proposals/` (resources_and_goods.md, tools.md); decided rules are in `docs/cybertron2/spec/economy/`. This note keeps the analysis.

*22 Oct 2026. Zach: start from the end uses, the possible roots and the ways things could be processed, and bridge them, with an
economic analysis of the actions going into each; ladders where the much better rungs need qualitative jumps in resources or long
supply chains. Numbers from [02j_end_uses_model.py](02j_end_uses_model.py): proposals (historically plausible orders of magnitude),
not engine values, except where marked. It is the tool for choosing the set of goods (02g §1f), not a build list.*

## 1. Method

1. **End uses** are the services people and societies need: food, warmth and shelter, storage, tools (yield), transport, information,
   meeting space, force.
2. **Roots** are what is taken from the land, each with its cost in actions (a journeyman with basic tools), where it is found, and
   how it comes back.
3. **Recipes** are processing steps: inputs, actions, and the building or skill each needs. A good's **full cost** is its inputs'
   full costs plus the step's actions, computed down to the roots.
4. **Ladders:** for each end use, the rungs (alternative paths), each costed **per unit of the service**: per tool-use, per
   person-night, per food kept, per page, per unit carried per edge. For each rung, what it gains over the rung below, and whether
   it needs **a root the rung below did not** (a qualitative jump).

The value of a service is priced at what it saves: an extra grain is worth the 0.77 actions it would otherwise take; a ration is worth
0.5 actions (02b). Capital is written off over 40 rounds.

## 2. Roots (proposals)

| Root | Actions a unit | Found | Comes back |
|---|---|---|---|
| wild food | 1.00 | forest, scrub | fast; game has a threshold |
| grain | 0.77 | fields | yearly |
| timber | 0.33 (ENGINE: 3 a fell) | woods | slowly |
| stone | 0.50 | a quarry | endless, heavy |
| clay | 0.25 | a riverbank | endless, heavy |
| copper ore | 0.33 | a seam in the hills | finite |
| tin ore | 1.00 | one far place | finite, rare |
| iron ore | 0.50 | bogs and hills | finite, common |
| salt | 0.33 | a spring | endless, one place |
| fibre | 0.50 | flax fields | yearly |
| hide | 1.00 | slaughter or the hunt | a by-product |

## 3. The ladders

### Tools: one use of a tool on a field

| Rung | Actions to make | Chain depth | Uses | Yield x | Cost a use | Gain a use | Return | New roots needed |
|---|---|---|---|---|---|---|---|---|
| bare hands | - | - | - | 0.5 | - | - | - | - |
| crude (wood, stone) | 1.7 | 1 | 10 | 0.8 | 0.17 | 0.30 | 1.8x | timber |
| copper | 5.0 | 3 | 20 | 1.0 | 0.25 | 0.50 | **2.0x** | copper ore |
| **bronze** | 6.9 | 4 | 40 | 1.25 | 0.17 | 0.75 | **4.3x** | **tin ore** (from far away) |
| **iron** | 22.1 | 3 | 100 | 1.5 | 0.22 | 1.00 | **4.5x** | **iron ore**, and a bloomery's charcoal and skill |

- **Copper tools are a weak rung:** barely better than crude ones per action spent. The real jumps are bronze and iron, and both
  are qualitative.
  - Bronze needs tin, found in one far place, so it needs long-distance trade.
  - Iron needs no rare ore, but about 78% of its cost is charcoal (6 charcoal a bloom, each 5 timber), plus a bloomery and a high
    skill. So it needs woods and a smith.
- **Two routes to the same rung.** A region on a trade route goes to bronze; a region with woods and a skilled smith goes to iron.
- **Copper's case rests on blades, fittings and coin,** not tools.

### Shelter: a person-night under a roof, against sleeping out

| Rung | Actions to build | People | Cost a person-night | Worth a person-night | Return | Needs |
|---|---|---|---|---|---|---|
| a lean-to | 2 | 2 | 0.05 | 0.28 (a roof, no warmth) | 6x | timber |
| wattle hut with a hearth | 11 | 4 | 0.16 | 0.46 | 3x | timber, stone, clay |
| **timber frame on stone, hearth** | 19 | 10 | **0.08** | 0.46 | **6x** | timber, stone, clay |
| stone house, hearth | 37 | 10 | 0.13 | 0.46 | 4x | stone, a mason |

- **Every rung pays,** so shelter is a sound need (02e). The timber frame for ten is the cheapest per person-night: the household
  scale economy of one hearth and one roof.
- **Stone does not pay per night.** It pays for what the model leaves out: size and storeys on scarce land (02i §2c), durability,
  and fire. Its case is density and permanence, so it is a town's material.

### Storage: keeping food through a 6-round winter (total cost: food lost plus the storage's share, in actions)

| Rung | Household (20 food) | Village store (120 food) | Needs |
|---|---|---|---|
| grain carried (15% a round) | 6.2 | 37.4 | nothing |
| grain in the house stock (5%) | 2.6 | 15.9 | a house |
| **grain in bins (2.5%)** | **1.7** | 10.4 | timber |
| grain in pottery jars (2%) | 2.0 | 12.2 | clay, a kiln |
| **grain in a cellar (1.25%)** | 2.4 | **9.4** | stone |
| fresh meat (25%) | 8.2 | 49.3 | nothing |
| **salted meat (2%)** | **4.5** | **26.8** | **salt** |

- **Bins win for a household; a stone cellar wins only at village scale.** So the granary is a village layer, with a threshold.
- **Pottery jars never win,** which confirms deferring clay (02g §1f).
- **Salt halves the cost of keeping meat at any scale.** That confirms salt's place: everyone with meat wants it, and one place has it.

### Writing: the cost of a page

| Rung | A sheet | A page written | A copy | Needs |
|---|---|---|---|---|
| parchment, by hand | 0.50 | 1.50 | 1.50 | hides |
| paper, by hand | 0.20 | 1.21 | 1.21 | fibre, a paper mill |
| **paper, printed** | 0.20 | 1.21 | **0.26** | fibre, a paper mill, **a press** (a later era) |

- **The scribe's time, not the material, is the cost of writing.** Paper saves only about a fifth on a page.
- **The press is the qualitative jump:** copies fall to about a sixth.
- So the first worlds can write on **parchment from hides, with no paper mill.** A record costs a scribe's time; a widely read text is
  dear until a press exists (02h §4b).

### Food and transport (computed earlier)

- **Food** (02d §3): the bottom rung is wild food at about 1 food an action; fields with skill and the plough give 3-5. Bread pays only
  above a threshold set by the gap between porridge and bread (25-70 people).
- **Transport** (02g §3): on foot 0.92 actions a unit an edge; pack ox 0.19; ox cart 0.074 (from about 16 units a round on a
  route); wagon 0.033 (about 115); river boat 0.006.

### Traps, harness and saddle (23 Oct; Zach: in the tool set, D2-23)

**Traps:** a trapline checked once a day (1 unit a visit plus 0.1 a trap); each trap catches about 1.5 food with chance 0.3 x the
game's share of its capacity, and lasts about 20 nights (1.6 units to make: timber and hide strips).

| Case | Work a day | Catch a day | Food a unit |
|---|---|---|---|
| one trap, full game | 1.18 | 0.45 | 0.38 |
| six traps, full game | 2.07 | 2.70 | **1.30** |
| six traps, game at half | 2.07 | 1.35 | 0.65 |
| six traps, game at a fifth | 2.07 | 0.54 | 0.26 |

- **A trap is only worth it as a line:** the visit is the cost, so six traps beat foraging (about 1 food a unit) and one does not.
- **Traps deplete game,** and their return falls with it; with game's threshold (37.4) a trapped-out forest can collapse. Trapping
  is a commons problem like the herd's.
- **Traps work while the trapper is away and can be robbed** by whoever checks them first, seen only if someone is there.

**Harness and saddle are cheap; the animal is the burden.**

| Good | Units to make | Life | A year | Upkeep of what it serves, a year (40 days, one animal kept alone) |
|---|---|---|---|---|
| harness (yoke and straps) | 3.7 | 2 years | 1.8 | an ox: about 48 (hay, its own raising, 1 unit a day of herding) |
| saddle | 5.3 | 4 years | 1.3 | a horse: about 65 (grain on working days, herding) |

The herding share falls to about 0.2 units a head a day in a common herd (02l §5). A rider's real cost is the horse's grain, so a
raiding people needs a farming base or steady loot (02k §3).

## 4. Every processed good: full cost, chain depth, roots

| Good | Actions | Depth | Roots | Needs |
|---|---|---|---|---|
| charcoal | 2.65 | 1 | timber | a charcoal clamp |
| copper | 3.81 | 2 | copper ore, timber | hearth and bellows |
| tin | 5.15 | 2 | tin ore, timber | hearth and bellows |
| bronze | 5.77 | 3 | copper ore, tin ore, timber | hearth and bellows |
| iron | 20.40 | 2 | iron ore, timber | a bloomery; a high skill |
| crude tool | 1.66 | 1 | timber | nothing |
| copper tool | 4.98 | 3 | copper ore, timber | a smithy |
| bronze tool | 6.93 | 4 | copper ore, tin ore, timber | a smithy |
| iron tool | 22.07 | 3 | iron ore, timber | a smithy; skill |
| parchment page | 0.50 | 1 | hide | nothing |
| paper page | 0.17 | 1 | fibre | a paper mill |
| pottery jar | 2.66 | 1 | clay, timber | a kiln |
| salted meat | 0.17 a unit | 1 | salt | nothing |
| trap | 1.58 | 1 | hide, timber | nothing |
| harness | 3.66 | 1 | hide, timber | nothing |
| saddle | 5.33 | 1 | hide, timber | a leatherworker's skill |
| hide armour (later) | 7.00 | 1 | hide | a leatherworker's skill |
| net (later) | 5.00 | 1 | fibre | fibre |
| boat (later) | 15.95 | 1 | hide, timber | a boatwright; water |

**Timber is in every metal.** Fuel is the hidden spine (02g §1e): an iron tool is mostly burnt wood.

## 5. What it says about the set of goods

| Finding | Consequence |
|---|---|
| the tool ladder's real jumps are bronze (tin, trade) and iron (charcoal, skill) | **tools are the strongest case for a hard tier**: bronze or iron as the rung a society reaches for, by trade or by woods and skill |
| copper tools barely beat crude ones | copper stays for blades, fittings and coin; whether copper tools exist at all is a calibration choice |
| stone does not pay per night of shelter | stone's place is density and permanence (towns, storeys, cellars at village scale), not every house |
| bins beat jars; the cellar wins only at village scale | clay waits; the granary is a village layer |
| salt halves the cost of keeping meat | salt stays in the core |
| a page's cost is the scribe's time | parchment from hides suffices at first; the press is the jump that matters for information |

**The pattern Zach asked for is there:** each end use has cheap rungs a household can reach and better rungs that need a new
root, a long chain or a society's scale. The model shows which jumps are large (bronze and iron tools; the press; the ox cart;
the village cellar) and which are not worth a good of their own (copper tools, pottery jars, paper without a press).

## 6. Using the model

- **To add an end use:** write its rungs as a function costed per unit of the service.
- **To add a good:** add its recipe; its full cost, depth and roots follow.
- **Before adding a good to the world,** check that it is on some ladder's best rung for some scale (a household, a village, a
  town). If it is never best, it is not worth a good (02g §1f).
- **What it leaves out:** time (chains take rounds), risk, distance between the roots (02g's transport model covers that), skill
  gained by practice (02d), and agents' behaviour. Dry runs and LLM runs calibrate it.
