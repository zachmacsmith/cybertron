# Proposal: transport and lodging

**Status:** partly accepted: D4-9 (goods, letters and people cross only when carried), D4-12 (a night out costs 1.5 food; hosts and
inns are part of the design), D2-4 (a death on the road is never announced); the ladder, capacities and danger numbers are
discussion. **Owner:** 37.2 (author; the numbers); the mechanisms of carrying, travel and lodging are 37.4's.

## Summary

A transport ladder costed in work units per unit carried per edge, from walking to rail, with break-even volumes that say which
rung pays at what traffic; each rung also differs in people carried, rest on the road and danger. Danger belongs to the edge
(terrain and season). Travellers sleep out, at a host's or at an inn; an inn pays only on a route with traffic, and is an
information hub.

## The proposal

### The ladder (02g §3; first worlds up to the ox cart)

| Rung | Capacity | Edges a day | Needs | Units a unit an edge | Capital |
|---|---|---|---|---|---|
| on foot | 10 | 1 | nothing | 0.92 | 0 |
| pack | 20 | 1 | nothing | 0.47 | 3 |
| pack ox, led | 60 | 1 | pasture or fodder | 0.19 | 30 |
| handcart | 40 | 1 | a track | 0.25 | 12 |
| ox cart (2 oxen) | 200 | 1 | a track | 0.074 | 80 |
| wagon (later) | 500 | 2 | a road | 0.033 | 220 |
| river boat (later) | 1,500 | 3 down, 1 up | a river | 0.006 | 150 |
| rail (much later) | 20,000 | 8 | a railway | 0.002 | 6,000 |

**Break-even traffic:** pack ox beats pack from about 3 units a day; ox cart beats pack ox from about 16 (a few households' trade);
wagon beats ox cart from about 115 (a town's); boat beats ox cart from about 60. In a region of about 40 people, ox carts pay and
wagons do not. Bulky goods stay near their source; light, dear goods travel (grain walks one edge at twice its own cost).

### Carrying capacity (OPEN C-1)

02g's capacities above, proposed over 38.06 §3's (on foot 20, pack 35, animal +60, cart +150), because they are calibrated against
grain's cost. 37.4 builds the mechanism (weights, capacity, rungs as items).

### People, rest and danger per rung (02g §3b)

Carts carry 2-3 riders and shelter them as a damaged house (1.2 food, 1.5 in the cold); a covered wagon as a sound house without a
fire; carriages 4-6 passengers; riders are fast and robbed for the horse. Danger per edge-day falls up the ladder: foot about 2%,
ox cart about 1%, wagon about 0.5%. Travelling together, hiring an escort and sleeping at an inn lower it further.

### Danger per edge (02g §3c; OPEN C-6)

Track through farmland about 0.2% a day, forest about 1%, a ford about 2% (ice x2, spring flood x3 or closed), a pass about 3% (winter
x4 or closed). Accidents and weather are the central scheduler's draws (D4-4); robbery is agents present, never random. A traveller
who dies never arrives and nobody is told (D2-4); a later traveller on the edge may find the body and what was carried.

### Lodging (02g §4, 38.05 §3)

| Where | Food a night | Gives |
|---|---|---|
| out in the open | 1.5 (winter 2, and the cold) | nothing |
| camping gear (hides, timber) | about 1.2 (winter 1.5) | no cold fall |
| a host's house | as the host's house | needs a welcome and a free bed; payment or reciprocity |
| an inn | as housed | a fee; a bed, a meal, the fire, a stable |

An inn needs a flow of about 3-5 travellers a day; a hamlet off the road has hosts. Inns collect news and prices, hold letters for
collection (the first post office), change horses for coaches, and know who travels where with what.

## Why

- Costing every rung in the same units as production says which goods travel and which rung pays, by route traffic (Von Thünen,
  Weber), so trade patterns emerge from distance.
- Rest and danger make the ladder about people and risk, not only tonnage: carts and inns are worth having for safety too.
- Unannounced deaths keep perception honest (H-7, D2-4).

## Alternatives considered

1. **38.06's capacities** (20, 35, +60, +150): simpler, not tied to costs; superseded if C-1 is accepted.
2. **One risk draw per night for every edge** (38.05 §2): replaced by per-edge danger by terrain and season (C-6).
3. **Announced deaths, or a computed absence** ("not seen for N rounds"): rejected (D2-4).
4. **Wagons, boats and rail in the first worlds:** deferred by era ([economy_later.md](economy_later.md)).

## Open questions

1. C-1 (capacities) and C-6 (danger table as the scheduler's draws).
2. Whether the danger numbers are in the right order (02g §7.2c).
3. The first region's inn and host: an inn at Millford, a host at the pass (02f §4; 02g §7.4).
4. The chance a later traveller finds a body (about 50% on a short edge proposed).
5. Tracks and roads as edge works: cost, upkeep, who builds them.

## Affects

economy/transport.md, economy/lodging.md (shared: 37.4 mechanism, 37.2 numbers); world/edges.md (danger, tracks, roads);
agents/work.md (carrying); life/ (deaths on the road).

## History

- 22 Oct: 02g §3 costed the transport ladder (`02g_transport_model.py`) after Zach asked for graduations of carts, cattle,
  carriages and trains.
- 22 Oct: Zach: carts should carry low danger; rungs differ in people carried and rest; horses for speed. Added §3b.
- 22 Oct: Zach: some edges far more dangerous, risk changing in winter; a traveller who dies just never arrives and the society has
  to notice. Added §3c; the "not seen for N rounds" prompt line flagged (D2-4).
- 22 Oct: Zach suggested hosts and inns; added §4; 37.4 decided nights out at 1.5 and hosts and inns as part of the design (D4-12).
- 22 Oct: 37.4's 38.08 took 02g's carrying numbers and agreed edge danger and unannounced deaths; logged as OPEN C-1 and C-6.

## Sources

[02g §3-§4](../../review/37_growth/02g_resources_and_transport.md); [02g_transport_model.py](../../review/37_growth/02g_transport_model.py);
[38.05 §2-§3](../../review/38_space_engine/05_round_design.md); [38.06 §3](../../review/38_space_engine/06_actions_design.md);
[38.08 §1](../../review/38_space_engine/08_build_plan.md); D2-4, D4-4, D4-9, D4-12; OPEN C-1, C-6.
