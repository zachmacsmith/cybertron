# Review 38.17: the rebuilt engine (`cybertron2/engine/`), its model and its primitives

*23 Oct 2026, 37.4 session. D4-34: rebuild M1 on the designed general core (38.08 M1, 38.16 §5). This note is the reference for the
code; it says what each part is and which decision or design it follows. Interpretations not yet decided are marked **(to confirm)**
and listed in §9.*

## 1. Three rules the code keeps

1. **Everything has a place.**
   - Every node entity carries its node: parcels, buildings, herds, offers, remains, events.
   - A person is at a node or on a road; hands are where their person is.
   - Events are recorded at a place; no event lacks one.
2. **Every change goes through the chokepoint.** `World.apply(primitive, place, **payload)` does four things in order:
   - checks that every entity the primitive touches is at `place`;
   - runs before-hooks, which may refuse;
   - makes the change;
   - runs after-hooks.

   Each call is recorded with its cause (the verb, the actor, and `for` whom).
3. **Agents' code sees only `Here` and `Mind`.**
   - `Here(w, name)` is a view of the node the agent stands in, plus its own body and hands.
   - `Mind(w, name)` is what it knows.
   - The verbs, knowledge, perception and prompt modules never read world state directly (a test checks the source).

## 2. State

| Table | Record | From |
|---|---|---|
| `nodes`, `roads` | name, text; road: a, b, days | D4-2, D4-10 |
| `parcels` | node, name, cover, size, adjacency, resources (plants, game, wood, seam, quarry, crop), fertility | 04, holding.md (plots), D4-7 |
| `buildings` | node, parcel (its lot), name, structure, size, fittings {hearth, beds: n, bins, quern, anvil, cellar, ...}, condition, door, fire, stock (a container), unfinished {blueprint, units, materials} | D2-9, buildings.md, recipes.md §3 |
| `herds` | node, parcel, kind, count, in milk | D2-6, livestock.md |
| `containers` | kind (hands, stock, remains), of whom or what, goods, wear | 07 §3, goods.md |
| `people` | body (stage, hunger, health, strength), hands (a container), at (node) or transit (road) | 09, D4-8 |
| `institutions` | kind (household), name, members, offices {head}, rules {admit, grant} | D4-18, 09 §2e |
| `claims` | thing (building, parcel, herd), claimant (a person or an institution), rights, grounds, since, until | D4-23 |
| `offers` | node, by, to, give, get (legs), lots, until | D2-25 to D2-27 |
| `agreements` | parties, legs (goods now, by a day, every n days; work days), made where and when, witnesses, status | D2-31 to D2-40 |
| `know`, `mind` | each person's knowledge and memory | knowledge.md, memory.md |
| `events` | today's events, each at a node or a road | place.md |
| `acts` | the action record (who did what, for whom, where), which duties are checked against | D2-39 |

## 3. Rights and physics (D4-23)

**Physics, enforced by the engine:**
- presence: one acts only at the node one is at;
- a barred door: only those with access can enter;
- what one holds, and what is in a container one can reach.

**Rights are claims:**
- `access`: enter, sleep, and speak in a building;
- `withdrawal`: take from its stock and its produce;
- `management`: the door, repairs;
- `exclusion`: grant access to others;
- `alienation`: transfer the claim.

A household's claim is exercised by its members according to its rules. Members have access and withdrawal; the head has the rest
(holding.md: "the head manages it"). Granting is by whoever the household's `grant` rule names: members, by default, per 05 §3:
"anyone its household allows" **(to confirm)**.

**Using without a right is allowed and witnessed:** taking from an open store, sleeping in a house, milking a herd. Taking from a
store one has no withdrawal right to is theft (05, holding.md "carried goods").

**What the engine does on the agent's behalf follows rights, never physics alone:**
- eating at night draws on stores where one has withdrawal;
- the default sleeping place is a building where one has access **(to confirm)**.

## 4. Primitives

| Primitive | Change | Place check |
|---|---|---|
| `transfer` | goods between two containers | both at the place |
| `create`, `destroy` | goods come into being (gathered, made) or go (eaten, used, spoilt, burnt) | the container at the place |
| `draw` | a parcel's resource is taken | the parcel |
| `wear` | wear on a tool or weapon; a worn-out one breaks | the container |
| `set` | a field of a building, parcel, herd or person (door, fire, condition, crop, hunger) | the entity |
| `admit`, `leave`, `found` | membership of an institution | the person (and the admitter) |
| `claim`, `end_claim` | claims made, granted, ended, transferred (`transfer_claim`) | the thing |
| `agree`, `settle` | an agreement made; a leg paid (by `transfer`) or put in arrears | the parties |
| `depart`, `arrive` | a person onto a road, and off it | the node left, the node reached |
| `harm`, `die` | wounds; death (what the dead carried lies where they died: 09 §2d) | the person |
| `learn` | a level of knowledge | the person |

Hooks register per primitive, before and after. The engine's own hooks are the action record for duties and the event log. Laws,
standing orders and reflexes attach here later (07 §5).

## 5. Verbs as compositions of primitives

| Verb | What it does |
|---|---|
| `gather`, `work` | Any technique, from its data: where (covers, fittings), what it draws on, how it yields (stock, chance, fixed, crop, herd), the tool table, the wear, what it gives (recipes.md §1, §4, §8). One handler |
| `make` | A recipe from inputs at a fitting. Inputs come from what one carries, then from containers one may take from here |
| `build` | Start or continue a building or a fitting from a blueprint: materials and work over days (recipes.md §3) |
| `sow`, `weed`, `reap` | Techniques on plots: crops count from the sowing day, ripen, and rot after the window (D2-11, D2-12, D2-17; 02l numbers, calibrate) |
| `move` | Goods between hands and a store one may use here |
| `take` | From any store here: theft without the right |
| `give`, `leave` | To a person or a house here |
| `offer`, `accept`, `withdraw` | Two-sided agreements: lots, legs now or by a day or every n days, work days (D2-25 to D2-27, D2-31) |
| `for` | On work, gather, make, give, offer and accept: the act is done on that party's behalf; output into its container here (D2-37) |
| `host`, `grant`, `withdraw_grant` | Access to a building, for a night or standing (05 §3) |
| `join`, `admit`, `leave_household`, `found` | Membership (09 §2d: the head's consent and living there) |
| `claim` | A bare claim on a thing here (holding.md) |
| `sleep` | Where one sleeps tonight, if not the default |
| `travel` | As before, with `leave` when too heavy (D4-32) |
| `attack`, `guard` | Fights, settled at night among those present |
| `watch`, `teach`, `learn`, `explain` | Knowledge (knowledge.md) |
| `set` | A door one manages |
| `rest` | Nothing |

## 6. The day

1. **Dawn:** arrivals, the scheduler's incidents and signs (data), goods left yesterday found.
2. **Morning:** perception, then everyone decides.
3. **Talk:** 2 waves (D2-7, D4-25, D4-31).
4. **Work:** interleaved.
5. **Settlement of agreements** (D2-32).
6. **Teaching and membership matched.**
7. **Night, node by node:**
   - fights;
   - departures;
   - where each sleeps;
   - fires;
   - eating;
   - shelter and the cold;
   - deaths;
   - spoilage;
   - breaks;
   - growth and crops;
   - offers lapse;
   - grants end.
8. **Evening:** perception, then memory at the end of a stretch.

## 7. Kept from M1 and moved across

- the talk step and speech;
- the message ration;
- conversations and thinking;
- agent-written memory;
- knowledge levels and teaching;
- the verb registry with the generated verb list and schema;
- recipes as data;
- travel, carrying and `leave`;
- the family-tree generator;
- the chronicle.

## 8. Tests

- one per primitive;
- conservation of goods (no goods appear or vanish except by `create` and `destroy`);
- the scope canary;
- the source check (no world state in the agent-facing modules);
- a test per verb;
- a deterministic bot run.

## 9. Interpretations to confirm with Zach

1. Who may grant access to a house: members by default (05 §3).
2. The default sleeping place follows access: own household, then a grant. A guest needs a free bed.
3. Night eating draws on stores where one has withdrawal. A host feeds a guest only by granting withdrawal or by giving.
4. Joining is matched like teaching: `join` by the person and `admit` by whoever the household's rule names, on the same day.
5. Agreements follow `standing.py`'s semantics (legs, arrears, misses, duties), written natively, since cybertron2 has no law
   language yet (D2-35 says port; the law language is M3).
6. Farming numbers from 02l (calibrate): crops ripen 6 days after sowing; return about 5 times the seed; a 2-day window, then a
   quarter lost a day.
7. Stone and a quarry where 04's catalogue puts them (hills), so hearths and anvils can be built.

*Engine reference. Rules decided elsewhere are cited; nothing here decides a rule.*
