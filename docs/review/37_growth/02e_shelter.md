# 37.2e Shelter: houses, upkeep, the cold

> **Status (23 Oct):** the current state of these ideas is in `docs/cybertron2/proposals/` (shelter.md); decided rules are in `docs/cybertron2/spec/economy/`. This note keeps the analysis.

*22 Oct 2026. Specification for discussion; nothing built. Shelter is the first use of the generic building model (02a §3.1, guide
§6). Clothing is parked (02_economy_worklog.md). Numbers not marked ENGINE are proposals.*

## 1. Why

Shelter turns buildings into a need, and does four things nothing else in the package does:

1. **A recurring demand for timber, stone and builders** that does not end once a town is built: steady upkeep plus rare,
   lumpy repairs after breaks, most of them in the cold.
2. **Scale inside the household:** one house and one hearth serve its occupants, so a household of five spends less per head on
   shelter and fuel than five people alone.
3. **Land use on a node:** houses, workshops and fields compete for the same land, and the timber comes from forests whose felling
   lowers their food yield.
4. **Exit becomes costly, and landlords exist.** Leaving means leaving your house; living in someone else's means rent and the
   threat of eviction. This is among the oldest forms of leverage (tenancy, the tied cottage).

## 2. What exists (ENGINE)

- The ration: every eater eats `ration` (1) food at the end of each round from its holdings, topped up from its own stores. With less
  than a full ration it eats nothing (subsistence.py `_eat`), its hunger stage falls (fed 0, hungry -1, starving -2) and `missed`
  rises. From 3 missed meals the starvation hazard applies: death with chance frailty + 0.15 per further miss, certain at 4.
- Seasons: lean, normal and plentiful, which set regrowth. There is no winter yet. 37.4 brings a calendar with a winter phase (board
  Post 1, loop 3).
- Felling: 3 timber a fell; each fell shrinks the forest's plant capacity by 1% of its initial size, down to 50%.
- Buildings: food stores (10 timber + 6 stone, built in one action, no work, no upkeep), forts, farm works with upkeep every 5 rounds
  (unpaid: they lose a level). There is no generic building and no shelter.
- 37.1: households as minimal institutions with a pooled food pot (`households.py` on `wp/demography`).

## 3. Design

### 3.1 The house

A house is a building:

| Field | Meaning |
|---|---|
| id, node | where it stands (one node in a one-node world) |
| owner | an agent, a household or an institution |
| beds | how many it shelters (default 5) |
| occupants | who lives there; set by the owner (like a farm's allow list), gated by law |
| condition | sound, damaged or ruined |
| hearth | the fuel burnt there this round (from its own stock) |
| stock | materials delivered for repair or construction |

### 3.2 Shelter states and their effect

Each round every agent has one shelter state:

| State | When | Ration multiplier, normal round | Cold round |
|---|---|---|---|
| **housed** | an occupant of a sound house within its beds, hearth lit in the cold | 1.0 | 1.0 |
| **cold house** | sound but no fuel in a cold round | 1.0 | 1.3 |
| **poorly housed** | the house is damaged, or the agent is over its beds | 1.2 | 1.5 |
| **unsheltered** | no house, or a ruined one | 1.5 | 2.0, and a 30% chance of falling to starving (§3.3) |

The ration multiplier changes how much an agent must eat to count as fed. It is one hook in `_eat`: ration x `shelter_mult(k, aid)`.
Everything after it (stages, missed meals, the hazard) stays as it is.

### 3.3 The cold: a chance of falling straight to starving (Zach, 22 Oct)

An unsheltered agent in a cold round falls straight to starving (hunger stage -2) with chance 0.3, seeded per agent and round. That
is the only extra effect of the cold beyond the higher ration. There is no separate exposure mechanism.

- **When it applies:** after the ration step, so it bites the next round. A starving agent has at most 2 actions, and only trade,
  talk, produce, vote and look-ups. Eating applies first and would otherwise lift it straight back to hungry.
- **It cripples; hunger kills.** The drop sets the stage but does not count a missed meal, so it does not start the starvation
  hazard. An unsheltered agent who keeps eating (2 rations in the cold) climbs back one stage per fed round, but each further cold
  round may knock it down again. Deaths still come only through missed meals and the existing hazard. A cold spell without
  shelter costs an agent its politics and most of its turn, not usually its life.
- **Harsher worlds:** `unsheltered_cold.missed: true` also counts a missed meal (so a long spell can kill), or
  `unsheltered_cold.death` adds a chance of immediate death.

### 3.4 Cold

A cold round comes from 37.4's calendar (winter phase) and its shock draws (cold snaps). In worlds without 37.4, a spec lists cold
rounds (`shelter.cold_rounds`) or there are none. Nothing infers cold from today's lean season.

### 3.5 Upkeep, breaks, repair

| | Default | Notes |
|---|---|---|
| upkeep | 1 timber + 1 stone every 10 rounds, from the owner | unpaid: the house loses a level (the farm-works rule) |
| breaks | chance 0.02 a round, 0.08 in a cold round | a break drops one level; a storm (37.4 shock) can break many houses in one round |
| repair | 4 timber + 2 stone in the house's stock, plus 3 work units | restores one level |
| construction | 20 timber + 10 stone + 12 work units | a new house starts as a site, sound when complete |

Work is the generic building work (§3.8): anyone may do it, and a builder's skill raises work per action.

### 3.6 Fuel and the hearth

- A house burns 0.5 timber a round for cooking and 2 in a cold round, from its stock (occupants deposit, or a subscription to a
  woodcutter fills it).
- **One hearth per house**, so fuel per head falls with the number of occupants: the household's scale economy.
- An unsheltered agent has no hearth.
- This replaces the per-agent fuel need assumed in 02b and 02d (1 timber a head a round) with a per-house one: about 0.06-0.07
  actions a head a round in a full house.

### 3.7 Ownership, tenure, rent, eviction

The house's `owner` and `occupants` fields work like a farm's holder and allow list. One routed primitive moves a house between
owners (37.3's grant and seize call it, as for plots). Another sets occupants; eviction is removing an occupant, gated by law
(`before_set_occupants`: a law can require notice, forbid winter evictions, or let a court decide).

- **Rent** is a standing contract between occupant and owner (a subscription, guide §7).
- **Inheritance** passes the house with the household's holdings (37.1 `life.households.inheritance`).
- **Houses are assets:** they can be pledged for loans, taxed by a hearth tax, and seized for debt.

### 3.8 Buildings in general (what shelter needs of the building model)

| Primitive | What it does | Law hook |
|---|---|---|
| `build` | starts a site of a type at a node, owner the builder or an institution it acts for | before_build (permits, land rules) |
| `work` | adds work units to a site or a damaged building (skill raises work per action) | before_work |
| `supply` | delivers materials into a building's stock (a transfer to `building:<id>`) | before_transfer, as today |
| `set_building` | owner sets occupants (houses), crew and access (workshops), or gives the building away | before_set_building |
| `demolish` | removes it and returns part of the materials | before_demolish |

Workshops (mill, smithy, loom) use the same record with `crew` and `recipes` instead of `beds`. Stores stay on their engine path in
old worlds and become a building type under `economy.buildings`.

### 3.9 Space and land

- Every building has a footprint in the node's land (houses 1 lot, a workshop 1-2), and a node's land is shared between forest,
  fields and building lots (the space interface, board Post 2, decides the unit).
- Clearing forest makes open land for either fields or lots. A growing household must choose: a new house takes land a plot could
  use, and the timber comes from a forest that then feeds fewer people.
- Houses face the same rules as goods once accounts are located: a house's stock is at its node.

### 3.10 Seeding

- In a seeded world every household starts in a sound house with a stocked hearth (37.6 generates houses with households; a spec's
  `start.houses` fixes them by hand).
- Single agents lodge in a household's house or a lodging house (an institution's).
- `start` can leave some unhoused (outcasts, newcomers) or set houses damaged (a world after a storm).

### 3.11 Prompts (one line each)

- Housed: `Home: Aldric's house (sound; 4 of 5 beds); hearth: 6 timber (2 a round in the cold); cold in 3 rounds.`
- Damaged: `Your house is damaged (a break, round 14): you eat 1.2 a round, 1.5 in the cold. Repair: 4 timber, 2 stone, 3 work.`
- Unsheltered: `You have no shelter: you eat 1.5 a round, 2 in the cold, and each cold round may leave you starving.`
- Owners see their houses summed: `Houses: 3 (2 sound, 1 damaged); 11 occupants; rent due 6 coin a round.`

## 4. Economics

Actions per unit as in 02b: a village with a master builder (timber 0.33, stone 0.40, work 0.5) against a household doing everything
itself (timber 0.42, stone 0.63, work 2.0 as a novice). One cold round in four, 5 occupants a house.

| | Village (builder hired) | Household (does it itself) |
|---|---|---|
| construction of a house | 16.6 actions | 38.7 actions |
| one repair | 3.6 actions | 8.9 actions |
| upkeep and expected repairs, per head a round | 0.04 | 0.08 |
| fuel, per head a round | 0.06 | 0.07 |
| **what shelter saves, per head a round** (the food a housed agent does not need) | **0.26** | **0.56** |

- **Shelter pays several times over:** it saves about 2.5-4x what it costs to keep, fuel included (6-7x without fuel). So agents keep houses, and a broken house is an
  emergency, not a shrug.
- **Repairs are the builder's trade.** A household repairing itself spends about 9 actions, two rounds of one member's turn. A
  builder spends about 3.6. Repairs are rare and lumpy and come mostly in the cold, so a builder sells urgency: after a winter storm
  breaks several houses at once there is a queue, and whoever orders the queue has leverage.
- **Losing shelter is costly but survivable:** unsheltered, an agent needs about 0.2 actions a round more food in a normal round and
  0.4 more in the cold, plus the risk of starting a round starving.

**The forest, a warning.** Five houses for 24 people burn and mend about 5.6 timber a round, about 1.9 fells. At today's felling cost
(each fell shrinks the forest by 1% of its initial capacity) the node's forest falls to its 50% floor in about 27 rounds. That
lowers its food yield. It is the deforestation trend Zach described and a good slow dynamic for 37.4. But it needs a renewable
technique so it is not inevitable: a **managed woodlot** (coppice) that yields timber without shrinking, kept by rules on felling (a
commons problem with an institution as the answer). That is the timber ladder: clear-felling is the degenerate rung, the woodlot
the organised one.

## 5. Spec keys (sketch)

```yaml
economy:
  shelter:
    enabled: false                       # off by default; one-node worlds without it replay unchanged
    house: {beds: 5, build: {timber: 20, stone: 10, work: 12}, repair: {timber: 4, stone: 2, work: 3},
            upkeep: {every: 10, cost: {timber: 1, stone: 1}}, breaks: {p: 0.02, cold: 0.08}}
    ration: {housed: 1.0, poor: 1.2, unsheltered: 1.5}
    cold: {housed_no_fuel: 1.3, poor: 1.5, unsheltered: 2.0}
    unsheltered_cold: {starving: 0.3, missed: false, death: 0.0}   # chance of falling to starving; harsher options
    fuel: {normal: 0.5, cold: 2.0}            # timber a house a round
    cold_rounds: []                            # without 37.4's calendar
start:
  houses: [{owner: H1, node: n0, occupants: [Aldric, Bram, Cela, Dara], condition: sound, stock: {timber: 6}}]
```

## 6. Dry-run checks

1. Housed vs unsheltered agents: food eaten and hunger stages differ as §3.2 says. About 30% of unsheltered agent-rounds in the cold
   begin the next round starving; no death comes from the cold itself under the defaults.
2. Upkeep and repairs make a steady timber and stone demand (per round, against §4) and a lumpy builder demand after cold rounds.
3. A storm in the cold breaks several houses: the builder's queue and the price of repair rise (subscription and spot prices, board
   Post 1).
4. Births (37.1) fill houses past their beds: households build or crowd, and construction demand follows population.
5. On a small node, land runs out: new houses take plots or force clearing, and the forest's food yield falls.
6. Eviction is visible, gated by any law that governs it, and leaves the evicted unsheltered.

## 7. Interfaces with other packages

- **37.1:** households are the usual owners and occupants; a house passes by the household's inheritance rule; crowding follows
  births.
- **37.3:** grant and seize houses by the same moving primitive as plots; a hearth tax and labour service on building work are
  ordinary powers.
- **37.4:** the cold phase and its shocks (storms) drive breaks, fuel and the fall to starving; deforestation is a trend; the space interface
  places houses on nodes and gives the land unit.
- **37.6:** generates houses with households, their condition and stock.

## 8. Open questions (with recommendations)

1. ~~Exposure: missed meal, straight to starving, or death?~~ **Decided (Zach, 22 Oct):** a 30% chance of falling straight to
   starving, no separate exposure; the harsher options stay as spec keys.
2. **Can anyone build a house anywhere?** Recommend a building needs a free lot at the node and the owner's right to the land (a plot
   held, or open land); land rules are laws.
3. **Beds: hard or soft?** Recommend soft: over the beds is "poorly housed", not refused.
4. **Lodging for single agents:** a household's spare bed (rent) or a lodging house (an institution's), so outcasts and newcomers
   have a market to enter.
