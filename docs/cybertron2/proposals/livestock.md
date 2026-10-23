# Proposal: livestock

**Status:** partly accepted: D2-6, D2-18 (rest discussion). **Owner:** 37.2 (numbers), with 37.4 (the mechanism is shared:
README "Who owns what"). **Affects:** spec/economy/livestock.md, spec/economy/production.md (draught, dung, fodder),
spec/economy/transport.md (pack animals, carts, riders), spec/world (pasture; 37.4), spec/conflict/raids.md (herds driven off).

## Summary

Cattle and horses are kinds in one livestock system: herds that breed, graze pasture, need winter fodder and herding, and are
never made from other goods. Equipment gives an animal its function (a harness makes an ox pull, a saddle makes a horse a mount).
Cattle give milk, meat, hides, draught, dung and a store of wealth; horses give speed and mounted fighting and eat grain. Herding
has a strong scale economy (one herder watches about 30 head), which makes the common herd, and its commons problem, the village's
answer.

## The proposal

### Accepted

- **D2-6:** one livestock system, bred not made; wild herds live on grassland.
- **D2-18:** on the farm, the plough needs an ox, fodder takes land, dung keeps the soil.

### In discussion (02g §2-2c, 02l §5)

| Mechanic | Proposal |
|---|---|
| a herd | a count per owner (or held in common) at a node, grazing a pasture whose grass is stock-limited |
| breeding | grows while the pasture holds out: cattle about 0.10 of the herd a round, horses about 0.05; foals usable after several rounds |
| winter | needs fodder: hay cut from pasture in summer, and straw from the grain harvest (a by-product, 02l §3) |
| herding | any herd needs watching (at least about 1 unit a day); one herder watches about 30 head (about 0.2 a head); an unherded herd strays; children can herd |
| cattle give | milk about 0.6-0.8 food a round a cow; slaughter about 12 food and a hide (meat spoils 25% a round, salted 2%); draught; dung; wealth that walks (lent, given as bride price, paid as a fine) |
| horses give | speed (2-3 edges a round on a track); about +3 mounted strength; light draught; they eat grain, so cavalry competes with people for food |
| equipment | harness (ox: plough, cart; horse: wagon), saddle (a mount); costs in tools.md |
| wild herds | on grassland, a herd with a threshold; catching is crew work; a caught horse must be broken (riding skill) |
| raids | herds can be driven off; riders make it easy (02k §3) |

## Why

- One entity creates many dependence edges at once (food, transport, farming, fighting, credit), which is what the scenario design
  asks for.
- Bred, not made: if a horse were cattle plus a resource, anyone could raise a cavalry in a round; breeding makes a fleet an
  investment and a stud a chokepoint.
- The herding scale economy is the clearest case of a village beating households (02l §5: about 30% less work per person where land
  is short), and the common herd brings rules on who grazes how many and who herds.

## Alternatives considered

1. **Horses as cattle plus another resource:** rejected (Zach agreed, D2-6): a horse would be made, not bred.
2. **No cattle; the plough as a hand good** (cybertron 1's plough covers 2 plots): loses draught, dung, milk and the farm-to-transport
   link. Replaced by D2-18.
3. **Separate horse and cattle systems:** duplicate mechanics for the same herd, pasture and breeding.

## Open questions

1. How pasture is represented: plots of a different cover, or a site with a grazing capacity (asked of 37.4 on the board, 23 Oct).
2. Breeding, milk and herding numbers (dry runs).
3. Whether dogs (02g §1d shortlist) are a third kind in the same system.
4. Rules for a common herd: a law's clauses (proposals/law.md) or custom.

## History

- 22 Oct: 02g §2 proposed cattle (milk, meat and hides, draught, manure, wealth).
- 22 Oct: Zach asked whether horses should be cattle with another resource; 37.2 proposed one livestock system with kinds, equipment
  giving the function; Zach liked shared livestock that is bred, and fields where horses naturally are (02g §2b-2c). Decided D2-6.
- 23 Oct: farming tied in: the plough needs an ox, fodder and dung (D2-18). 02l found the herding scale economy; straw added as
  winter fodder.
- 23 Oct: harness and saddle accepted as tools (D2-23); 02j found the animal, not its gear, is the burden (about 48 units a year for
  an ox kept alone, 65 for a horse).

## Sources

[02g_resources_and_transport.md](../../review/37_growth/02g_resources_and_transport.md) §2, §2b, §2c,
[02l_farming.md](../../review/37_growth/02l_farming.md) §5, [02j_end_uses.md](../../review/37_growth/02j_end_uses.md) (harness and
saddle), [02k_fuses_and_gates.md](../../review/37_growth/02k_fuses_and_gates.md) §3; D2-6, D2-18, D2-23.
