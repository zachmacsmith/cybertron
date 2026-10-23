# Proposal: resources and goods

**Status:** discussion (23 Oct); parts accepted: D2-10 (clothing parked), D2-19 (a short metal ladder first), D2-23 (the tool set).
**Owner:** 37.2. **Affects:** spec/economy/goods.md, production.md; information/ (writing materials).

## Summary

The set of things taken from the land and made from them is **chosen by principle**, not inherited: a base resource stays only if it
passes six tests, a processed good only if several things use it, it makes a chokepoint or a trade, it changes weight or shelf life
enough to matter, or it unlocks something. That leaves a lean first-world set of about ten goods. Which rungs of each ladder are
worth having is decided by costing every path from the roots to the end uses in work units (02j).

## The proposal

### Six tests for a base resource (02g §1)

1. It traces to a need (food, warmth and shelter, tools and security, transport), directly or through a chain.
2. It is found in different places from the others, so node kinds differ and depend on each other.
3. It comes back in its own way (D4-7: finite, fast renewable, renewable with a threshold, slow, periodic).
4. It has its own weight for its value and its own perishability (how far it travels, how long it keeps).
5. It adds a dependence edge no other resource adds.
6. The set is the smallest that passes 1-5.

The tests are applied against **what buildings and infrastructure consume** as well as against people's needs (02g §1b, the bill
of materials): that is why stone is in.

### The lean first-world set (02g §1f)

| Good | Uses | Why it stays |
|---|---|---|
| grain | food, bread at a mill, fodder for horses | the staple, and the mill's chokepoint |
| wild food | food | the bottom rung (H-6) |
| livestock (cattle; horses later) | milk, meat, hides, draught, dung | one entity, five dependences (D2-6) |
| timber | fuel, building, carts, fittings | used by almost everything; fuel is the hidden spine of every metal |
| stone | walls, storeys, roads, hearths, millstones, cellars | every larger or lasting build (D2-3); defence (D2-20) |
| copper | tools, blades, fittings, coin | the metal; the hill camp's trade |
| salt | keeping meat; cattle | the long-distance good and the tax |
| hides | packs, harness, saddles, bellows, parchment, traps | the herds' second product, and writing |
| tools and blades | yield, fighting, hunting | made goods that wear out: the smith's trade (D2-23 splits them into hand tools, plough, carts, weapons, traps, harness, saddle) |
| documents | writing | the unlock Zach rates highest |

**Folded into recipes** (not goods of their own): charcoal, planks, lime, gravel, dressed stone, slate, leather. **Deferred:** pitch
and boats; clay, pottery and bricks; fibre, rope and cloth; iron and tin; tannin ([economy_later.md](economy_later.md)).

### Unlocks: capabilities, not multipliers (02g §1d)

First-world shortlist: **writing, seals, locks and keys, dogs, beacons.** Each fits a system that exists or is planned and makes a
chokepoint someone can hold (the scribe, the seal, the keyholder, the kennel, the watch). The rest (pigeons, lenses, medicine, maps as
goods, new crops, gunpowder) come by era or frontier.

### End uses decide the rungs (02j)

Each end use (food, shelter, storage, tools, transport, writing) is a ladder of rungs costed per unit of service, with the roots
each rung needs. A good is worth adding only if it is on some ladder's best rung at some scale. Findings:

| Ladder | Finding |
|---|---|
| tools | copper tools barely beat crude ones (return 2.0x against 1.8x); **bronze (tin, so trade) and iron (78% charcoal, a bloomery, skill) are the real jumps** (4.3-4.5x) |
| shelter | a timber frame for ten is cheapest per person-night; stone pays for density, permanence and defence, not warmth |
| storage | bins win for a household, a stone cellar only at village scale; **pottery jars never win**; **salt halves the cost of keeping meat** |
| writing | a page's cost is the scribe's time; parchment suffices; **the press is the jump** |

## Why

The old set (food, timber, stone, copper; silver, gold, quicksilver) was inherited; silver, gold and quicksilver had no need path and
were scoring artefacts. Many goods with one use each add prompt length and calibration work without adding dependence. Costing the
paths shows which jumps are large enough to shape a society and which are decoration.

## Alternatives considered

- **The old engine's set unchanged:** rejected, not chosen by any test.
- **A full chain catalogue as the build list** (02g §1e: timber to planks, pitch, tannin; stone to lime and slate; clay; fibre):
  rejected for the first worlds; kept as a catalogue for later eras.
- **Seven or nine core resources including clay and fibre** (02g §1, §1b): superseded by the pruning rule; clay and fibre deferred.

## Open questions

1. Whether copper tools exist at all, or copper serves only blades, fittings and coin (a calibration choice).
2. Which metal route first worlds use, iron or none (D2-19 says short; which rung is open).
3. Salt's place in the first region: at the pass's waypoint or in the hills (02g §7.5).
4. The hard tier (iron, tin, silver, old-growth oak, wild horses, goods from beyond) and when each enters.

## History

- 22 Oct: Zach: the base resources had been assumed, not chosen; asked for a principled set. 02g §1: six tests, an audit (food split
  three ways, silver, gold and quicksilver dropped, stone marked "later"), a core of seven.
- 22 Oct: Zach: resources must also be chosen for infrastructure. 02g §1b: the bill of materials; stone restored (the earlier
  "later" judged it against people's needs only); fibre and leather added; core of nine.
- 22 Oct: Zach asked for resources hard to get but valuable (§1c), then for resources that add something new (§1d): the unlocks.
- 22 Oct: Zach asked whether the chains were already in the engine: no, drawn from history this session. Then whether so many
  single-use variants are needed: no. 02g §1f: the pruning rule and the lean set of about ten; §1e marked a catalogue.
- 22 Oct: clothing parked (D2-10).
- 22-23 Oct: Zach: start from end uses, roots and processes (02j). Findings above. D2-19: a short metal ladder in first worlds.
- 23 Oct: tools by dependence (D2-23): hand tools with grades, plough, carts, weapons, traps, harness, saddle; armour, nets, boats
  and the seed drill to economy_later.md.

## Sources

[02g §1-§1f](../../review/37_growth/02g_resources_and_transport.md), [02j](../../review/37_growth/02j_end_uses.md) and
[its model](../../review/37_growth/02j_end_uses_model.py), [economy_later.md](economy_later.md); D2-6, D2-10, D2-19, D2-23.
