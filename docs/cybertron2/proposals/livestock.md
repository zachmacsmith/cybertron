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

## Fences, hedges and walls (23 Oct, discussion; for later)

Zach: are herds kept in by fences or by herding? Both, proposed: **a herd stays put if it is herded or enclosed**. Unherded and
unenclosed, it wanders: strays into crops (the M1 stray incident), gets lost, and is easy prey and easy to steal.

| Enclosure | Made from | Cost for a 10-plot pasture (about 20 head) | Upkeep a year | Strays and escapes | Wolves at night | Pays back (herding saved) |
|---|---|---|---|---|---|---|
| none, herded | a herder's day (1 unit; less for a common herd, 02l §5) | | | low while herded | as the herder's watch | |
| **hurdles** (wattle) | timber | about 42 units | about 17 (they rot) | x0.3 | x0.7 | about 2.8 years |
| **post and rail** | timber | about 63 | about 13 | x0.2 | x0.7 | about 3.3 years |
| **hedge** | planting (a year to grow before it holds) | about 38 | about 4 (laying) | x0.15 once grown | x0.6 | about 1.3 years, after it grows |
| **dry-stone wall** | fieldstone (D2-56), a waller | about 150 | about 5 | x0.05 | x0.5 | about 5.5 years, but it lasts generations |
| **a fold** (a small stone pen by the houses, for nights) | stone | small | small | | **x0.2** | with a watch (D2-21) and dogs (later) |

- **A fence is a structure on a parcel's boundary** (layout.md lists fences and walls as structures), with a **condition** that
  decays without upkeep and drops in a gale (D2-71's risks of things): gaps let beasts out ("the fence by the Long Field is down in
  two places", salience 0.4).
- **What it saves is herding work:** a fenced pasture needs a check and a move (about 0.2 units a day) instead of a herder (1). So
  fences pay where labour is dear or herds are large, and hardly where a child can mind the herd (D4-19); that is the historical
  pattern too.
- **Fence the beasts in, or the crops off:** a hedge round a field keeps the herd and the deer out of the crop instead.
- **Enclosure is politics:** fencing part of a common pasture takes it from everyone else's use. That is a claim (D4-23), and a
  village's quarrel, which the engine leaves to people.
- Seeded worlds start with old hedges and walls where the land has long been farmed.

**Tracking where a herd wanders (Zach: would we track its path, so it hits other people's crops or goes into the woods?).** Yes,
at the level of parcels, which the engine already has (a herd is on a parcel in M1; parcels know their neighbours: layout.md):

- **Fences sit on borders between parcels**, not around a parcel, so one fence keeps a herd in and other herds out, and a border
  with nothing on it is open.
- **An unherded herd moves** up to about two steps a day across the parcel graph. Each step picks a neighbour by what draws it (a
  ripe crop, water when it is thirsty, good grazing, the way home at dusk for cows in milk) and crosses the border only with the
  border's odds (open 1; hurdles 0.3; a hedge 0.15; a wall 0.05; scaled by the fence's condition). Draws are keyed (D2-70).
- **Where it goes, things happen:** in a field it eats and tramples the crop (a `draw` on the crop, recorded with the herd as the
  cause and its holder known); in the woods it can be lost or meet wolves (higher hazard); at the edge of the node it can, rarely,
  wander along an edge into the next node.
- **People see it** where they are: "the Fenn cattle are in the Long Field, trampling the barley" (high salience to the field's
  holder), tracks and dung on a path after (low), a herd seen heading for the wood. Whose crop and whose herd are known, so
  damages are a claim people can press (custom, an arbiter, a court).
- **The same walk serves wild animals:** deer coming out of the wood into the next field, a wolf pack's track (D2-78).
- Cost: small: a handful of herds a node, a few steps each a day, at parcel resolution (no paths within a parcel).

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

- 23 Oct (analysis): [02o_livestock.md](../../review/37_growth/02o_livestock.md) proposes the numbers: cattle as one kind with
  roles (cows, bulls, oxen as trained steers, calves), teams of two for plough and cart, breeding (cattle 0.7 young a year, work at
  3 years), herds not growing up within a run (seeding sets them), about 1.2-1.3 plots of land a head, horses eating a ration of
  grain each working day, milk 0.8 food a day for 0.6 of the year, slaughter 40-50 meat and 2 hides, herding at least 1 unit a
  day, prices (cow 40-60 coin, ox 50-100, horse 90-150). 02l's and 02m's ox costs need a team of two.

- 23 Oct: Zach: would we track the parcels a herd wanders through? Yes: fences on parcel borders, a walk of about two steps a day
  drawn by crops, water, grazing and home, crossing borders by the fence's odds; crops eaten, losses in the woods, damages known.
- 23 Oct: Zach: are herds kept by fences or herding; timber fences round plots, upgraded to stone for fewer escapes and wolves.
  Added: herded or enclosed; hurdles, post and rail, hedge, dry-stone wall, a fold; costs, upkeep, effects, paybacks; enclosure as a
  claim. For later.

## Sources

[02g_resources_and_transport.md](../../review/37_growth/02g_resources_and_transport.md) §2, §2b, §2c,
[02l_farming.md](../../review/37_growth/02l_farming.md) §5, [02j_end_uses.md](../../review/37_growth/02j_end_uses.md) (harness and
saddle), [02k_fuses_and_gates.md](../../review/37_growth/02k_fuses_and_gates.md) §3; D2-6, D2-18, D2-23.
