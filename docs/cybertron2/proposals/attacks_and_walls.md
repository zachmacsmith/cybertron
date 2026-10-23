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

### Setting fire (23 Oct; with D2-49: stone resists fire, the vault does not burn)

**What a raider needs:**

| Need | How |
|---|---|
| to be there | at the building, at night or unseen by day (it is witnessed by anyone present) |
| fire | a **torch** (basic: half a timber and half a unit) or embers taken from any lit hearth; everyone knows how to make fire |
| access to something that burns | a thatched or timber roof can be lit **from outside**; a stone building's roof needs a ladder or a way in (a break-in first, or someone inside); **a vault cannot be lit** |
| work | `attack {target, aim: burn}`: about 1 unit for the attempt |

**Will it catch?** Proposed chances per attempt: wattle and thatch 0.8, timber frame 0.6, stone with a timber roof 0.2 (once the
roof is reached), a vault 0; higher in a dry season, about half in rain (the season and weather are 37.4's).

**A fire is a fuse event** (fuse_events.md): it starts, then takes the night to run its course, so people can respond in time.

- **Who notices:** sleepers inside (smoke) most of the time; a watcher at once; neighbours often; the whole node sees the flames.
- **What they can do** (the urgent call's menu): fight it (a bucket line: each pair of hands with water cuts the damage, more if
  the fire is caught early; a well or river at the site makes it possible), save what they can carry, flee, or fight the raiders.
- **Unfought,** the building burns: timber and wattle are lost with what is in them; stone keeps its walls (repair about a third of
  the cost) but loses roof and contents; a cellar's contents mostly survive; a vault's entirely. Documents on shelves burn (an
  archive can be lost in a night). Fire spreads to adjoining rooms and to wattle neighbours, hardly from stone.
- **People asleep inside who do not wake** are wounded (the harm model's wound) rather than killed outright; to make death possible
  is a choice (Open).

**What it is for, in a raid:**
- **Smoking defenders out:** a stone house with a burning roof cannot be held. Defenders who leave lose the walls' multiplier
  (x2 for stone) and fight in the open, or yield. This is the counter to the stone house (02k §3) without making stone weak.
- **Destruction and terror:** burning destroys rather than takes. It serves revenge, a feud, pressure on a rival, or denying a
  granary or a mill to an enemy (a burned mill is a chokepoint lost for many days, 02g §5b).
- **The counters:** a watch, dogs, stone, a vault for what must not burn, space between buildings, water near at hand, and a fire
  crew (neighbours, or an office).

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
5. Setting fire (above): the catch chances, the bucket line's effect, wounds or deaths for sleepers who do not wake.

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

- 23 Oct: Zach: stone resists fire (walls stand) and a vault does not burn (D2-49); raiders can set fire when they attack: what
  would they need? Added "Setting fire": a torch or embers, access to something that burns, catch chances by material, fire as a
  fuse event with a bucket line, smoking defenders out of stone houses.

## Sources

[02k §3](../../review/37_growth/02k_fuses_and_gates.md); [02g §5b](../../review/37_growth/02g_resources_and_transport.md);
[02j](../../review/37_growth/02j_end_uses.md) (shelter, stone, saddle and horse costs); `cybertron2/combat.py`;
[38.06 §3](../../review/38_space_engine/06_actions_design.md) (working late); D2-20, D2-21, D2-22, D4-19; OPEN C-5.
