# Proposal: attacks, buildings and walls

**Status:** partly accepted: D2-20 (three kinds of attack; walls multiply defenders), D2-21 (the watch), D2-22 (any party may raid
a node); the numbers are discussion. **Owner:** 37.2 (author); combat and raids are 37.4's (conflict/), the costs of walls and
structures are 37.2's.

## Summary

Three kinds of attack: on a person, on a building (a break-in, then a fight), and on a whole node (targets drawn by exposure).
Walls multiply the defence of those inside rather than defending on their own, so a wall needs people and numbers still beat walls.
A stone building is both less likely to be picked in a node raid and harder to take. A watcher stays awake, detects first and can
wake the others.

## The proposal

### Three kinds

| Kind | Target | How it resolves |
|---|---|---|
| attack a person | someone at your node | as built (`cybertron2/combat.py`); the target's response once reflexes or a fuse exist |
| raid a building | one building | (1) **break in**: work set by the structure (wattle quick, a barred timber door longer, stone much longer), noisy, so those inside may wake ([fuse events](fuse_events.md)); (2) **fight whoever defends**, who chose to defend, flee (lose the stock, keep their lives) or hand over. An empty building is the break-in only, against its lock and walls |
| raid a node | a sweep by any party | each raider's engagement draws a target weighted by exposure x value / hardness: herds, crops, open stores and people outside first; wattle and timber next; stone and guarded sites last |

### Walls multiply defenders (proposed numbers)

Defence of those inside: asleep with no house x0.5 (as built), behind a timber door x1, behind stone x2. Raid success with 37.4's
harm contest, a household of four:

| Household | Raiders | No house | Timber | Stone | Empty stone house |
|---|---|---|---|---|---|
| unarmed | 3 crude | 90% | 76% | 50% | 90% |
| crude weapons | 3 crude | 62% | 32% | 11% | 90% |
| crude weapons | 3 blades | 87% | 66% | 34% | 97% |
| crude weapons | 12 blades | 99% | 97% | 89% | 100% |

### The watch (D2-21)

A watcher skips the night's sleep and eats as if it worked late (38.06: x1.5); it detects a fuse event first and can wake the
others. Households rotate it; children can keep it (D4-19's menial tasks). A town's night watch is an office.

### What follows (consequences to check in runs)

- **Stone pays for whoever holds stock:** about 18 units more than a timber frame (02j); it repays after about nine raids on a
  20-food household, one or two on a 120-food store. The tower, the stone granary, the church as refuge.
- **Fortifying displaces raids:** in a sweep, a stone house sends raiders to the neighbours; a reason to pool into a village wall,
  whose cost per household falls with population (its perimeter grows with the square root of the area enclosed).
- **A refuge is leverage:** in a node raid people flee to the strongest building, and whoever controls its door can charge for it.
- **Raiders turn to what cannot be walled:** herds, crops, mills, people on the roads. Horses fit the node raid: strike on arrival,
  drive herds off, carry loot, leave before pursuit; a rider's real cost is the horse's grain (02j).

## Why

- Stone needed a value beyond density: per night of shelter it does not pay (02j), but as defence it does, for those with stock.
- A multiplier keeps "enforcement needs people" (scenario_design): an empty or unarmed house is not a vault.
- Drawing node-raid targets by exposure gives the historical pattern (raiders took cattle, not towers) without scripting it.

## Alternatives considered

1. **Option A: a flat defence per wall** (the house defends itself): rejected. It barely moves the odds against armed raiders
   (strength enters squared), and it makes a house a self-defending vault, removing force as a lever.
2. **cybertron 1's personal fort** (stone locked into a person's defence): replaced; once space exists, stone belongs to a building.
3. **Node raids only by riders or large parties** (37.2's proposal): rejected by Zach (D2-22). Any party may raid; a small one
   usually fails and a single rider may try at greater risk; the contest and the defences decide.
4. **Riders who ride and strike in one round** as an exception to D4-8 (02g §5b): open, OPEN C-5; fuse events may make it
   unnecessary.

## Open questions

1. Break-in work by structure (units), and whether tools (a ram, iron) shorten it.
2. The multipliers (x1 timber, x2 stone) and whether a village wall multiplies guards on it.
3. The watch's food cost (x1.5 proposed).
4. Exposure weights in a node raid.
5. Damage and burning of buildings (02g §5b): condition lost, contents lost, repair work.

## Affects

conflict/combat.md, conflict/raids.md, conflict/defence.md (37.4); economy/buildings.md (structure, break-in work, wall costs);
agents/actions.md (raid kinds, watch).

## History

- 22 Oct: 02g §5b proposed attacks that damage or burn buildings, herds driven off, node-wide raids by exposure, and riders who ride
  and strike in one round.
- 22 Oct: Zach: stone should mean a household is safer in its house during an attack (fortify the house, not oneself). 37.2 tested
  two forms against the harm contest: option A (flat) rejected, option B (multiplier) proposed.
- 22 Oct: Zach: a stone building should also be less likely to be attacked at all in a node raid; asked for three kinds of attack
  (a person, a building with a break-in and a separate fight, a whole node) and whether horses fit the node raid.
- 22 Oct: Zach decided the three kinds and the break-in (D2-20); the watch skipping sleep, rotated, kept by children (D2-21); any
  party may raid a node, rejecting 37.2's riders-or-large-parties proposal (D2-22).

## Sources

[02k §3](../../review/37_growth/02k_fuses_and_gates.md); [02g §5b](../../review/37_growth/02g_resources_and_transport.md);
[02j](../../review/37_growth/02j_end_uses.md) (shelter, stone, saddle and horse costs); `cybertron2/combat.py`;
[38.06 §3](../../review/38_space_engine/06_actions_design.md) (working late); D2-20, D2-21, D2-22, D4-19; OPEN C-5.
