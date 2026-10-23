# Place as the engine's foundation: everything is somewhere, and an agent can reach only where it is

**Status:** accepted in principle: D4-35 (the mechanism is part of the D4-34 rebuild). **Owner:** 37.4.

## Summary

Every entity and every event has a place, required by the engine and never inferred. The world's state is partitioned by node.
Code that serves an agent (its verbs, its prompt, its perception) is never handed the world. It is handed a view of the node the
agent stands in (`Here`) and the agent's own mind (`Mind`). It holds no reference to any other node, so it cannot read one even by
mistake. Anything known about elsewhere is in the mind, put there by having been there, by being told, or by seeding. Only travel
moves anything between nodes. Tests enforce both rules: a static check that agent-facing code never touches the world, and a canary
check that no agent sees anything from a node it has no way of knowing about.

## The proposal

### 1. Every entity has a place

A place is one of:
- `Site(node, parcel)`: on open ground;
- `Site(node, building, room?)`: indoors;
- `Road(edge, from, day)`: on a road.

The entities that carry a place:
- **People.** Each person is in exactly one place. A household is an identity and has no place; its members each have one.
- **Houses, other buildings, fittings and herds.** They carry their node explicitly. It is not derived from a parcel at read time.
- **Goods.** Goods are always in a container that has a place: a person's hands, a store, a parcel. Nothing is "in the world".
- **Offers.** An offer is made at a node and stays there. It closes when the offerer leaves (D2-26: "open while the offerer
  stays").
- **Agreements and debts.** These have no physical place; they exist as information (D2-1, D2-32). They live in minds and in
  documents, and a document has a place.

### 2. Every event has a place

- **`happen` needs a place.** It takes a place as a required argument and raises an error without one. Events are appended to that
  node's log; there is no world log.
- **Every source of change is placed:** dawn incidents, signs, fires, arrivals, departures, speech and fights.
  - The scheduler (D4-4) places each incident.
  - A valley-wide change, such as an early frost, is one event per node, each with its own lag and reliability (D4-6).
- **Speech has a place:**
  - to the town: the node;
  - in a building: the building;
  - to a person: both are at the node, which is checked once at the speech step.
- **A road is a place too.** Events on a road go into that road's log, so nothing that happens to a traveller is placeless. Meeting
  others on a road can be added later on the same footing.

### 3. The state is partitioned by node

`World` holds `nodes: {id: Node}` and `roads: {edge: Road}`.

A `Node` holds:
- its parcels, buildings, fittings and herds;
- the set of people present;
- its open offers;
- its event log.

People's own state (body, holdings, mind) is keyed by name. A person's presence is in exactly one node or road.

Engine steps that run over the whole world loop node by node, and each node's step sees only that node: night, spoilage, growth,
the fire, perception. One function moves anything between partitions: departure and arrival (D4-8, D4-10). It carries the person,
what the person holds, and the person's mind. Carried messages (D4-9) travel the same way.

### 4. Agents reach the world only through `Here` and `Mind`

**`Here(node, agent)`** is a read view of one node, plus the agent's own body and holdings. It gives:
- who is present;
- the houses, buildings, parcels, fittings and herds here;
- the offers open here;
- today's events here;
- name lookup here, so a name not here resolves to nothing ("not here").

**`Mind(agent)`** holds what the agent knows:
- seeded and lasting memories, and notes;
- beliefs and the house "as last seen";
- kin and where it believes they live;
- the map as known: roads, distances, and repute as last heard;
- prices witnessed (D2-29).

Each module reaches the world as follows:
- **Verbs:** `do(here, actor, action)`. A verb changes the world only through methods on `Here`, and those methods act on that node.
- **Prompts:** built from `Here` and `Mind` only.
- **Perception:** reads the node's event log and writes into `Mind`.
- **Knowledge checks** (what you can do here): read `Here` and `Mind`.

These modules (`act`, `prompt`, `perceive`, `knowledge`) do not import `World` and never see `w.s`.

What changes in what agents see:
- **The kin list** shows what the agent believes: the place it last heard, and "(dead)" only once it has learned of a death. That
  is D2-4, enforced by construction.
- **The map** shows repute as the agent knows it: what it has seen or been told, or what it was seeded with. It is not generated
  from the other node's current contents.
- **The home house when away** is the one remembered when leaving (already done this way in M1).

### 5. The reply schema names only what the agent knows

The enums for people, houses and places are the names in the agent's `Mind`, not world-wide lists. A verb still checks `Here`, so a
known name that is not here is refused.

### 6. Enforcement

- **Static check (a test):** an AST check that `act.py`, `prompt.py`, `perceive.py` and `knowledge.py` neither import `World` nor
  read world state. Only `world.py`, `run.py` and the scheduler may.
- **Canary check (a test):**
  - Seed each node with unique marker names: a parcel, an item note, a person, a spoken line, an offer.
  - Run bots for N days.
  - Check that the prompts of agents who have never been to node B, and have no seeded or told knowledge of it, never contain B's
    markers.
  - Run it again with travel and carried messages, and check that markers arrive only with a carrier.
- **Per-verb check (a test):** every verb, given a target at another node, is refused.

### 7. Migration of M1

The order of work:
1. Place becomes required. Give houses, fittings, herds and offers an explicit node; give `happen` a required place; close offers
   when the offerer leaves.
2. Introduce `Here` and port the verbs to it, one at a time, running the per-verb test as each lands.
3. Introduce `Mind`: kin, map and home-as-seen move into it. Port prompt and perception.
4. Partition the state, and make node-by-node steps of night, spoilage and perception.
5. Add the static and canary checks. Delete the world-wide helpers from the agent-facing modules.

This is about a day of work. It changes no rule, only where the rules can look.

## Why

M1 was built for one node. Multi-node scope was then added one filter at a time: each subsystem got its own "same node" check
wherever one was noticed. The valley run (38.15) showed the cost of that approach:
- offers seen and tried across villages;
- the live state of a house a day away shown in a prompt.

The audit then found more of the same:
- milking any herd in the world;
- barring one's door from elsewhere;
- absent household members and any guard counting as defenders;
- herd and fitting names resolved world-wide;
- kin deaths and other villages' repute taken from live state.

Every one is a leak by omission. While agent-facing code holds the whole world, a new feature leaks unless its author remembers to
filter. Place is the axis of the whole design (nodes, travel, carried information, D4-2 and D4-9), so it should hold by
construction, not by care.

## Alternatives considered

- **Keep filtering at each read (now).** Leaks by omission; rejected above.
- **One global state with a required node field and a `local(node)` helper.** Better: every read can be local. But it is opt-in: any
  code can still read the world. Useful as step 1 of the migration, not as the end state.
- **A separate world object per node,** with travel as message passing between them. The strongest isolation. But the scheduler, the
  calendar and people's identity are naturally global, and real separation would buy little over §3 and §4 at more cost. Kept in
  reserve if nodes are ever run in parallel.

## Open questions

- **Places inside a node.** Should seeing also be scoped to a site (a parcel, a building) inside a node? That belongs to seeing.md
  and layout.md. This proposal fixes the node boundary; the same `Here` can narrow to a site later.
- **Roads.** Can travellers on the same road meet, see each other, trade, or fight? The road as a place allows it; whether to use it
  is a separate decision.
- **Seeded knowledge of elsewhere.** How much does a person know at the start of a run of other villages and of kin living
  elsewhere? Proposed: kin, roads and a repute line written at seeding, then updated only by visits and by being told.
- **Valley-wide signs.** Is one event per node, each with its own lag, the right reading of D4-6?

## Affects

- `spec/core/` (the state and the day's steps);
- `spec/world/` (places and roads);
- `spec/information/` (Mind: memory, beliefs, the map as known);
- `spec/economy/transport.md` (only carrying crosses nodes; offers by place);
- `spec/economy/lodging.md` (none).

## History

- **23 Oct 2026.** Zach stated the principle (D4-35); the mechanism (Here, Mind, the chokepoint's place checks) is built under D4-34.

- **23 Oct 2026.** Proposed by 37.4 after the valley run (38.15) and Zach's "Things happening in other nodes shouldn't even be able
  to accidentally see them. Every single event should occur in a place."

## Sources

- [38.15](../../review/38_space_engine/15_m2_valley.md) §3-§4;
- D2-1, D2-4, D2-26, D2-29, D2-32, D4-2, D4-4, D4-6, D4-8, D4-9, D4-10;
- seeing.md, layout.md.
