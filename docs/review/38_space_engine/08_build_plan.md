# Review 38.08: what to build next in cybertron2 (plan)

*22 Oct 2026, 37.4 session. A plan for Zach to approve: nothing is built until he says. It turns the designs of 04-07 (places, the
round, actions, cybertron 1's lessons) and 37.2's designs for cybertron2 (02f-02i on `econ/37.2-thicker-economy`) into milestones.*

## 1. Where 37.2's designs and 37.4's meet

37.2 has designed much of the economy for cybertron2 and several proposals for 37.4's parts. Read 22 Oct:

| Topic | 37.4 (04-07) | 37.2 (02f-02i) | Resolution proposed |
|---|---|---|---|
| Carrying | on foot 20, pack 35, animal +60, cart +150 | on foot 10, pack 20, pack ox 60, handcart 40, ox cart 200, wagon 500, boat 1,500, with a cost model (02g §3, `02g_transport_model.py`) | **take 37.2's numbers** (calibrated against grain's cost); 37.4 builds the mechanism (weight, capacity, rungs as items) |
| Inns and hosts | guest bed, inn, camping gear (05 §3) | the same, plus inns as information hubs and letter drops (02g §4) | agree; one design |
| Buildings | slots by land kind (04 §1) | buildings from parts: structures, rooms, fittings; lots per node (02i) | **lots = 37.4's slots**; 37.2's parts decide what a building does; templates (house, inn, hall) as blueprints |
| Speech at a node | the talk step (05 §1) | three scopes: the square, rooms (by access to the building), private messages (02h §4a) | **the talk step carries 37.2's scopes**: a message goes to the square, a room or a person; delivered in the talk step |
| Letters, boards, papers | letters as items, errands (05 §5) | channels re-imagined: boards at sites, carried editions, boxes, the channel record with a medium and a location (02h §4) | letters and boards first; carried editions later |
| Danger on edges | a risk draw per night in transit (05 §2) | danger per edge by terrain and season; travellers who die are never announced, found by chance (02g §3c) | agree; the draws are 37.4's scheduler (seeded, paired) |
| Computed absence | — | Zach: the prompt must not say "not seen for N rounds"; the household remembers the departure and the stated plan (02g §3c) | **fix in M0** |
| Riders | arrive, then decide (devlog decision 8) | mounted parties may ride and strike in one round (02g §5b): an exception | **Zach to decide**; not needed before horses exist |
| Raids | combat.py's raid on a house | attacks on any building (damage, burn), herds driven off, node-wide raids by exposure; outside raiders as incidents (02g §5b) | agree in principle; after M1 |
| Coin | "money and credit move anywhere" (proposed) | Zach decided: **coin is carried; debts move only as information** (02f §6) | **superseded: coin is carried** |
| Merchants | emergent from delay | one merchant household seeded in the first region (Zach, 02f §6) | agree |
| First world | a few hand-made nodes | the first region: Millford, Barleyfield, Ashwood, Coppergate, about 40 people, 4 nodes (02f §4) | **use 37.2's first region** as the target world, scaled down for the first runs |

## 2. Milestones

### M0. Small fixes (an hour)
- Remove the computed absence ("not seen for N rounds") from the prompt; keep a household member's witnessed departure and stated
  plan as lasting memories.
- Not possible from this session: publishing runs 1-2 to Hugging Face (no `HF_TOKEN`, and the run logs are not in the repository).

### M1. The core on the new design (the large one)
The engine everything else needs. Rewrites `cybertron2`'s world and actions on:
1. **The chokepoint** (07 §4.1): every change is a primitive applied through `apply` (checks, before-hooks, change, after-hooks)
   in a cause stack; an event log whose audience is presence (and room access). No laws yet, but the hooks exist.
2. **Containers with a place** (07 §3): packs, house stocks, stores, escrow; weight and carrying capacity (37.2's numbers).
3. **Nodes with sites and lots, edges with length** (04): land kinds as data (river valley, woodland, hills, crossroads first);
   land cover (forest, fields, pasture) with felling and clearing.
4. **The day** (05): dawn, look, decide (everyone at once), talk (square, rooms, private; one wave to start), work (travel last),
   departures, night, memory; transit with nights out, gear, hosts and inns.
5. **Actions as work units** (06): a budget by age, health and season; costs per action; working late; a routine that fills
   unused units; `offer`/`accept` (the swap); letters and errands.
6. **Ported onto it**: forage, hunt, fell, mine, forge, craft, houses and the cold, combat, perception.

Evidence: scripted smoke tests (determinism, conservation of goods, presence gates); then **one LLM run** on a small version of the
first region (3 nodes, about 12 agents, 20-30 days).

### M2. The environment
The calendar (compressed year, daylight units), the central scheduler (incidents and eras, seeded, the same in every arm), signs
through perception, the climate axes per land kind, danger per edge by season, internal consequences (soil, game threshold, woods).
Evidence: a scripted check that a suited strategy beats a myopic one (the 37.4 acceptance); an LLM run across a winter.

### M3. Institutions
The law language and dispatch (v2 only), households as institutions (37.1), contracts (escrow, standing, agency), offices.
Coordinated with 37.3 on the board. Evidence: the hills world again, with contracts available (did the Irons trade safely?).

### M4. The economy (37.2's E2-E6 on M1-M3)
Standing work, skills, production shapes, buildings from parts, recipes, the transport ladder, coin and debts. 37.2 designs and
may build against M1's interfaces after posting on the board.

### M5. The frontier and the generator
Unknown nodes, expeditions, claims; the landscape generator (04 §6) and checks.

## 3. Proposed next step

Write the **node interface** (M1's schemas: node, site, lot, edge, container, the primitive table, the round's phases) as one short
doc and post it on the board for 37.1, 37.2 and 37.3, then build M0 and M1 once Zach says go.
