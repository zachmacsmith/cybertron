# Proposal: tools

**Status:** accepted: D2-23 (open points remain). **Owner:** 37.2. **Affects:** spec/economy/goods.md (the tool goods),
spec/economy/production.md (what each tool multiplies or enables), spec/economy/livestock.md (harness, saddle),
spec/conflict/combat.md (weapons; 37.4).

## Summary

Tools are chosen by the dependence they create, not one per activity. Hand tools are one good with grades (crude, then metal) and
multiply hand work: felling, hoeing, reaping, quarrying, mining. The plough needs an ox. Carts need an animal and a road. Weapons
serve fighting and hunting. Traps catch game while the trapper is elsewhere. A harness lets an ox pull; a saddle lets a horse carry
a rider. Armour, nets, boats and the seed drill wait.

## The proposal

| Good | Used for | Made from (02j costs, units) | Dependence it creates |
|---|---|---|---|
| hand tools (crude, then metal) | felling, hoeing, reaping, quarrying, mining | crude 1.7 (timber); metal tiers by the metal ladder | quarrying needs metal tools, so stone depends on the smith |
| plough | breaking the soil (0.75 a plot against the hoe's 3) | timber and a metal share | needs an ox: cattle, fodder, herding |
| cart | transport (02g §3) | timber and fittings | needs an ox or a horse, and a road for the larger rungs |
| weapons | fighting; the hunting bonus | crude 2 (timber or stone); a blade (copper, timber) | the power to take; a hunting people is an armed people |
| trap | catching game overnight while elsewhere | 1.6 (timber, hide strips); lasts about 20 nights | pays only as a line (six traps about 1.3 food a unit at full game, one 0.38); depletes game; can be robbed |
| harness (yoke and straps) | an ox pulls a plough or a cart | 3.7 (timber, hide); about 2 years | cheap; the ox is the burden (about 48 units a year kept alone) |
| saddle | a horse carries a rider | 5.3 (timber, hides; a leatherworker); about 4 years | cheap; the horse is the burden (about 65 a year, mostly grain) |

Deferred: hide armour, metal armour, nets, boats, metal-jawed traps, the seed drill ([economy_later.md](economy_later.md)).

## Why

- A separate good earns its place only if it creates a different dependence (02g §1f's pruning rule). An axe, a hoe and a pick
  differ only in what they multiply, so they are one good; the plough, the cart, weapons, traps and riding gear each tie a
  different part of the world together (cattle, roads, force, game, horses).
- Crafts can still differ through skill per activity rather than through more goods.

## Alternatives considered

1. **Tools as farm tools only** (02j's first tools ladder, implicitly a yield multiplier on a field): too narrow; superseded.
2. **Two goods, tools and weapons:** too coarse; it left cattle out (no plough) and merged everything else. Superseded by the set
   above.
3. **One tool per activity** (sickle, scythe, axe, pick, spear, sword): many single-use goods; rejected by the pruning rule.

## Open questions

1. Whether copper tools exist at all: in 02j they return 2.0x against crude tools' 1.8x; bronze (4.3x) and iron (4.5x) are the real
   jumps. A calibration choice.
2. Which metal rung the first worlds have (D2-19: a short ladder, not both bronze and iron).
3. The iron-axe and charcoal loop: an iron axe makes timber cheaper, and about 78% of iron's cost is charcoal, so iron axes make
   iron cheaper. 02j leaves this feedback out.
4. Trap numbers (catch chance, the cost of a visit) by dry run.

## History

- 22 Oct: 02j costed a tools ladder (crude, copper, bronze, iron) as a yield multiplier on a field, without saying so.
- 23 Oct: Zach asked "tools for what? hunting? foraging? mining? fighting?". 37.2 found the old engine has no general tool (a plough
  for farming, blades for fighting) and proposed two goods, tools and weapons.
- 23 Oct: Zach: "surely there are different types of tools? None would use cattle?". 37.2 revised to the set by dependence (hand
  tools with grades, plough, cart, weapons), with one tool per activity rejected.
- 23 Oct: Zach asked "nothing else?". 37.2 listed traps, harness and saddle, armour, nets and boats. Zach: traps, harness and saddle
  in; the rest as future options. Decided D2-23; the deferred ones recorded in economy_later.md, with their costs in 02j.

## Sources

[02j_end_uses.md](../../review/37_growth/02j_end_uses.md) §3 (tools ladder; traps, harness and saddle),
[02j_end_uses_model.py](../../review/37_growth/02j_end_uses_model.py),
[02g_resources_and_transport.md](../../review/37_growth/02g_resources_and_transport.md) §1f, §2b, §3; cybertron 1's
`cybertron/conflict.py` (weapons) and `cybertron/camptypes/fields.py` (the plough); D2-19, D2-23.
