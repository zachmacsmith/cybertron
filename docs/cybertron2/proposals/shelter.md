# Proposal: shelter

**Status:** partly accepted: H-5, D2-10 (rest discussion). **Owner:** 37.2. **Affects:** spec/economy/buildings.md (houses,
upkeep, breaks, hearths), spec/agents (the ration multiplier; 37.4), spec/environment (cold rounds, storms; 37.4),
spec/conflict/defence.md (stone and defence; 37.4).

## Summary

Every household starts in a house. A house needs upkeep and sometimes breaks, most often in the cold. Without proper shelter an
agent needs more food, and in the cold an unsheltered agent has a 30% chance of falling straight to starving. One house and one
hearth serve all their occupants, so shelter is a scale economy inside the household. Upkeep and fuel make a steady demand for
timber and stone, and deforestation a slow trend.

## The proposal

### Accepted

- **H-5:** houses with upkeep and rare breaks; a lack of shelter raises the food needed; in the cold an unsheltered agent falls
  straight to starving with chance 0.3; no separate exposure.
- **D2-10:** clothing is parked; shelter carries the cold.

### In discussion (02e)

| Shelter state | When | Ration, normal round | Ration, cold round |
|---|---|---|---|
| housed | in a sound house within its beds, hearth lit in the cold | x1.0 | x1.0 |
| cold house | sound, no fuel | x1.0 | x1.3 |
| poorly housed | damaged, or over the beds | x1.2 | x1.5 |
| unsheltered | no house, or a ruined one | x1.5 | x2.0, and the 30% fall to starving |

- **The fall to starving** comes after eating, sets the stage without counting a missed meal, so it cripples rather than kills;
  harsher worlds can count a missed meal or add a death chance.
- **Upkeep and breaks:** upkeep 1 timber and 1 stone every 10 rounds; breaks 2% a round, 8% in the cold; repair 4 timber, 2
  stone, 3 work; a new house 20 timber, 10 stone, 12 work (numbers in old-engine rounds, to rescale to days).
- **Hearth and fuel:** 0.5 timber a round, 2 in the cold, per house, not per person.
- **Tenure:** owner and occupants; rent as a standing contract; eviction a routed act a law can gate; houses as assets (pledged,
  taxed, seized). With D4-23, the owner is read from claims.
- **The shelter ladder** (02j): a lean-to, a wattle hut with a hearth, a timber frame on stone for ten (the cheapest per
  person-night, about 0.08 units), a stone house. Stone does not pay per night; it pays for density and storeys (D2-3), permanence,
  and defence (D2-20: walls multiply the defence of those inside, and a stone building is less likely to be picked in a raid).

## Why

- Shelter pays about 2.5-4 times its cost of keeping (02e §4), so houses are kept and a break is an emergency: lumpy repair demand
  after storms gives the builder a queue to order.
- Leaving a house is costly, and living in someone else's means rent and the threat of eviction: one of the oldest forms of leverage.
- One hearth per house rewards living together.

## Alternatives considered

1. **Clothing as the cold's good** (flax, spinning, weaving; halves winter fuel): parked (D2-10) in favour of shelter, which reuses
   the building model.
2. **Exposure as a separate mechanism, or death from the cold:** rejected (H-5); kept only as harsher world settings.
3. **Template houses:** superseded by buildings from parts (D2-9): a house is rooms, beds and a hearth.

## Open questions

1. Rescaling 02e's per-round numbers to day rounds (D4-13).
2. Whether beds are a soft limit (over them is "poorly housed"; recommended).
3. Lodging for single agents (a spare bed for rent, or a lodging house).
4. **Deforestation:** five houses for 24 people would bring a node's forest to its floor in about 27 rounds at the old felling
   rule; a managed woodlot (coppice) under rules on felling is the organised rung. To settle with 37.4's forest regrowth.

## History

- 22 Oct: Zach proposed shelter: agents start in a house that needs upkeep; a lack of a proper household raises food consumed;
  winter, and a chance of going straight to starving; timber felled from forests that then yield less. 02e written.
- 22 Oct: Zach decided the 30% chance of falling straight to starving, with no separate exposure (H-5). Clothing parked (D2-10).
- 22 Oct: buildings from parts (D2-9) and storeys needing stone (D2-3) made the house a building of rooms and fittings.
- 23 Oct: 02j costed the shelter ladder: the timber frame for ten is cheapest per person-night; stone's case is density,
  permanence and, after Zach's point on raids, defence (D2-20).

## Sources

[02e_shelter.md](../../review/37_growth/02e_shelter.md), [02j_end_uses.md](../../review/37_growth/02j_end_uses.md) §3 (shelter),
[02i_buildings.md](../../review/37_growth/02i_buildings.md) §2c, [02k_fuses_and_gates.md](../../review/37_growth/02k_fuses_and_gates.md)
§3; H-5, D2-3, D2-9, D2-10, D2-20.
