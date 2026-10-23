# Review 38.16: where M1 was built too narrowly, system by system, against what was designed

*23 Oct 2026, 37.4 session, at Zach's request ("Everything should be starting as a broad system. That is the point of M1: testing a
general system in a very simple narrow scenario, not building it to fit tiny sentence descriptions"). Read for this:
- every spec file;
- 37.4's own design notes: 04 places, 05 the round, 06 actions, 07 cybertron 1's engine, 08 the build plan, 09 life;
- the proposals on buildings, hiring and agreements;
- all of `cybertron2/m1/`.*

## 1. How it happened

38.08 planned M1 as the general core:
- the chokepoint, where every change is a primitive applied with hooks and causes;
- containers with a place;
- nodes, sites and lots;
- the day;
- actions as work units;
- then forage, hunt and the rest ported onto that core.

What I built, under the name M1, was a different thing. I started from a one-village scenario and wrote each feature as the
narrowest code that made the scenario run, from one-line descriptions. I did not read the decided spec files first: buildings,
holding, agreements, goods, money and markets, livestock, lodging. When several villages came, I added "same node" filters feature
by feature.

The result works for the scenario. But almost every system is a special case of a general one the designs had already described.
The faults in the valley run (38.15) all came from this. This note lists every case and the general form.

## 2. The missing core

These are the pieces everything else should stand on. M1 has none of them.

| Core piece | Designed in | M1 | Consequence |
|---|---|---|---|
| **The chokepoint**: every change is a primitive applied with checks, before/after hooks and a cause | 07 §2.1, §4; 08 M1.1; core/architecture.md (to compile) | Every verb changes `w.s` directly, about 40 hand-written mutations | No law, agreement, duty (D2-39), standing order (07 §5) or reflex can attach to anything. Each new rule means editing each verb |
| **Containers with a place**: hands, a house's stock, a store, escrow, a treasury, each a record with a node and a holder | 07 §3; 08 M1.2; goods.md ("stored in a container at a place") | Two hard-coded kinds: `agent.holdings` and `house.stock`. Escrow is a flag on offers (`held`). `leave` writes into a house's stock | No stores, granaries, treasuries or ledgers (D2-33). `for: party` (D2-37) has nothing to point at. Dying moves goods to the home house even from the road |
| **Place on everything** (place.md) | D4-2, D4-9; 07 §2.2 (audiences from presence) | Agents and parcels have a node; everything else derives one; offers have none; events infer one | The leaks in 38.15 §4 |
| **Records as data**: claims, memberships, agreements, access, bookings | holding.md (D4-23), agreements.md (D2-31 to D2-40), 09 §2e, buildings.md | None. A feud over Long Field is a sentence in a memory; household and house are fixed fields | No holding, renting, hiring, joining, hosting by rule or debt; nothing for agents to dispute except in words |
| **Agents see only `Here` and `Mind`** (place.md) | 07 §2.2; seeing.md | Agent-facing code reads all of `w.s` | Leaks by omission |

## 3. System by system

| System | What is decided or designed (general) | What M1 does (specific) | General form |
|---|---|---|---|
| **Households** | 09 §2d-2e, D4-18: an institution with members, a house, a stock, a head (an office), land and an inheritance rule. Joining is the head's consent plus living there; membership changes by partnership, birth, adoption, leaving and death; a new household needs a new house | `agent.household` and `agent.house` are set at seeding and never change. No head as an office. No admission, leaving or founding | Membership records changed by primitives (`admit`, `leave`, `found`); the head as an office; home derived (proposals/households.md) |
| **Buildings** | D2-9, buildings.md: a structure, rooms and fittings on a lot; what a building does is what its fittings do; built from materials and work over days; access per room; bookings; upkeep | Two record kinds: `houses` (with beds, condition, stock, door, fire) and `buildings` (name, access); a smithy is a "fitting" record that stands for a whole building. No building or rooms; access is a string on the house. `_build` is dead code for a "firing pit" left from removed pottery | One building record: lot, structure, rooms, fittings, access, condition, holder by claim. A house is a building with a hearth, beds and bins; a smithy is one with an anvil-and-bellows. A building verb adds work and materials to a project |
| **Lodging** | 05 §3: `host {guest}` by the head or whoever the household allows; a standing `welcome {all, household, name}`; a guest sleeps there if welcomed and a bed is free; adds to the host's fuel; inns with `lodge`, paid. lodging.md: sheltered as the household is | `welcome` by anyone at their own house, one night only. No bed limit, no standing setting, no inn. A guest eats only what they carry | Hosting is access to a building for sleeping, granted by whoever may grant it, for a night or standing. Eating from a store follows the right to take from that container. Beds are a fitting with a count. An inn is a building whose access is sold (a board or rent preset) |
| **Goods and containers** | goods.md: every good is an item held by someone or in a container at a place, with weight and spoilage; tools with wear | `ITEMS` is fine. Containers are two hard-coded kinds. Tools have no wear (D2-46 decided). `TOOLS` and `WEAPONS` are separate tuples, not item properties | Containers as records. Item properties (tool grade, weapon strength, wear factor) on the item. Wear applied by the primitive that uses a tool |
| **Gathering** | 06 §1, production.md: forage, hunt, fell, mine, quarry, herd, sow and reap at a site, each drawing on a resource with a regime (D4-7) | `_gather` and `_work` have one hand-written branch per technique (forage, hunt, fell, mine; reap, milk, repair), each with its own formula and special refusals | One handler. The technique's data names the resource it draws on (plants, game, seam, crop, herd), the yield rule, the tool use and what it gives; regimes per resource (D4-7). Adding a technique is adding a row |
| **Farming** | D2-11 to D2-17: sow and reap minimum, optional stages, a harvest window, seed kept back, fertility, hands on a plot | A crop is `{left, ripe_day}` on a field; reap only. No sowing, window, seed or fertility | Plots with fertility and a crop record; sow and reap as techniques on the general gather and work handler; the window as a resource regime |
| **Livestock** | livestock.md, D2-6: a herd is animals of a kind held by an owner at a node, bred, grazing, fodder | One herd with no owner; `in_milk` is a count; milking takes the first herd in milk anywhere in the world | Herds as holdings with an owner (claim) and a node; milk drawn from a herd one may use |
| **Recipes (`make`)** | recipes.md (proposal), D2-44: inputs, fittings, work | Mostly general (data-driven). But `at: "house"` hard-codes one's own house as the place of the quern and hearth, and inputs come only from hands | Recipes need fittings (a quern, a hearth, an anvil) in a building one may use here. Inputs come from containers one may take from here |
| **Exchange** | money_and_markets.md, D2-25 to D2-27: `offer {to, give, get, lots, until}`, `accept {offer, lots}`, `withdraw`; a promise leg makes a debt; an offer to anyone open while the offerer stays; goods from hands or containers one may take from | No lots, no withdraw, no promise legs. Fixed lifetimes (to a person: today; to anyone: today and tomorrow). Pays from hands then one's own store at home. Duplicates were possible | The spec's offer, as a case of agreements (D2-31): legs (now, by a day), lots, withdraw; settlement by the path rule (D2-32) |
| **Agreements, hiring, acting for others** | agreements.md (D2-31 to D2-40, port of `standing.py` and `credit.py`), hiring.md | None. Credit in the run lived only in notes | Built on the chokepoint and containers: legs, settlement, arrears, duties checked from the action record, `for: party` |
| **Holding** | holding.md (D4-23): possession by the engine; claims as records with rights, grounds, since, recognition; disputes; plots; `transfer_claim` | None. Fields have no claims; the feud's subject has no record | Claim records and `transfer_claim`, shown to agents as they know them |
| **Speech** | speech.md (D2-7, D4-15, D4-25, D4-30, D4-31) | Close to the spec (built after you corrected it). Access is read from `has_access`, which special-cases a house's household | Keep. Access comes from the building's access records |
| **Memory and conversation** | memory.md (D4-26 to D4-28) | As specified | Keep. Belongs to `Mind` |
| **Perception** | seeing.md (proposal): observations from the state, templates first; audiences by presence and room access (07 §2.2) | One long function with a branch per entity type. Weather lines per season in code. A stale tool list ("axe, sickle, club, basket"), so nobody is ever seen carrying a tool or weapon. `TRADE_TAGS` still lists pottery. Not scoped by node at generation | Observation templates as data on each kind of thing (cover, item, fitting, building, herd, person), read through `Here`, so a new kind of thing comes with how it is seen |
| **Knowledge** | knowledge.md (proposal): levels, teaching, watching, documents | Fairly general (techniques as data, levels). Aliases are hard-coded for each technique | Aliases as technique data |
| **Combat** | conflict/ (to compile), D2-20 to D2-22, D2-46 | A simplified port. In raids, absent household members and guards anywhere count as defenders. No building defence. Weapons don't wear | On the chokepoint: attack and raid as primitives at a place; defenders = those present who may defend; wear on use |
| **Environment** | D4-4 to D4-7: one scheduler for incidents and eras, signs, resource regimes | Incidents are hand-written kinds in `run.dawn` (stray, fire); `cold_days` is a list; one regrowth rule | The scheduler with incident kinds as data, each with its effect as primitives |
| **Life** | 09, D4-19, D4-20: stages, birth, death, inheritance, households founded and joined | Stages as fields; death by starvation or attack; goods go to the home house wherever one dies | Death as a primitive at a place: what is carried lies where one died (09 §2d); inheritance by the household's rule |
| **Travel** | transport.md, D4-8 to D4-10, D4-32 | Fairly general: edges, transit, nights out, carrying, `leave` | Keep. Carriers and messages (D4-9) next |
| **Prompts** | information/prompts.md (to compile) | The verb list and schema are generated (good). `describe_node` hard-codes the list of covers and their words. The food line special-cases grain | Words for covers and goods as data |
| **World generation** | 04 §6, D4-21, D4-22 | People are generated generally (good). Land, houses and nodes are written by hand per spec | Fine for now (04 §6 says the first worlds are hand-made) |

## 4. What is general already and stays

- the talk step and speech scopes;
- the message ration;
- conversations, thinking and agent-written memory;
- knowledge levels and teaching;
- the verb registry with the generated verb list and schema;
- recipes as data;
- travel, carrying and `leave`;
- the family-tree generator;
- the chronicle.

These move onto the new core largely unchanged.

## 5. The rebuild proposed

This is 38.08's M1, which I skipped. It replaces the narrow parts of the slice and keeps §4. The order:

1. **State and place.**
   - Partitioned by node; every entity and event placed (place.md).
   - Containers as records: hands, a building's stock, a store, escrow.
   - Buildings as one record kind with fittings and access (houses included).
   - Herds with an owner.
2. **The chokepoint.**
   - Primitives with checks, before- and after-hooks and a cause stack: move goods between containers, gather from a resource,
     consume inputs, give, settle a swap, enter or leave a building's access, admit or leave a household, transfer a claim, travel,
     attack, die.
   - An event log per place with presence-derived audiences.
3. **Verbs as compositions of primitives**, reading `Here` and `Mind` only:
   - gather and work from technique data (one handler);
   - make from recipe data with fittings;
   - the spec's offer and accept (lots, withdraw, promise legs).
4. **Records:**
   - claims (holding.md);
   - household membership and the head as an office;
   - access and hosting (05 §3);
   - agreements and the settlement rule (agreements.md; port `standing.py` and `credit.py` as D2-35 says).
5. **Observation templates as data,** so perception follows from the kinds of things.
6. **Tests:**
   - a scope canary (place.md);
   - conservation of goods across primitives;
   - one test per primitive;
   - the earlier M1 tests rewritten on the new core.

Then rerun the valley on the same seed to see what the general rules change.

**Estimate:** steps 1 to 3 are the bulk, about two to three days of work. Steps 4 and 5 are one to two more.

## 6. Questions for Zach

1. **The order of work.** Is the order above right: the core first (place, containers, chokepoint), then the records (households,
   claims, agreements)? Or should the records come in the same pass?
2. **Hosting.** Should the round design's hosting (05 §3: `host` by the head or whoever the household allows, a standing `welcome`,
   beds) be built as written?
3. **Cutting M1.** May the narrow parts of M1 be deleted rather than kept beside the new core? (07 §3: one path, no compatibility
   flags.)

*Session note. The proposals it leads to are place.md and households.md; nothing here is decided.*
