# Proposal: buildings from parts

**Status:** partly accepted: D2-3, D2-9 (the numbers, the fitting list and the limits still discussion; 23 Oct). **Owner:** 37.2.
**Affects:** spec/economy/buildings.md; world/ (lots, with 37.4: OPEN C-2); information/ (rooms as speech scopes); conflict/defence.md
(walls).

## Summary

A building is a structure (a material and a footprint on a lot) with rooms, and fittings in the rooms. **Functions attach to
fittings, not to building types:** the engine never asks "is this a mill?", it asks whether there are millstones and a water wheel in
a room at a river site. Templates survive as blueprints for seeding and one-action building. Rooms are also speech scopes, so a
building is access to information. Capacity scales: bigger rooms and adjoining rooms cost less per person, and stone is what lets a
building grow large or tall.

## The proposal

### Structure (02i §2)

| Material | Room size | Storeys | Rooms in a building | Breaks (02e) | Fire |
|---|---|---|---|---|---|
| wattle and timber | up to about 10 people | 1 | 2 | 2% a round, 8% in the cold | burns easily |
| timber frame on stone | up to about 25 | 2 | 6 | half | burns |
| stone or brick | larger, with great beams, columns or arches | 3 | limited by labour | a quarter | the roof burns, the walls stand |

### Capacity that scales (02i §2b-2c; D2-9, D2-3)

- **A room's cost** = 8 timber-equivalent x (capacity / 4)^0.7; fitting slots = 2 x (capacity / 4)^0.6. A 4-person room costs 2 a
  person, a 100-person hall 0.76.
- **Adjoining rooms** share a wall and the roof: x0.8 each after the first.
- **Storeys:** a room on the second storey costs x1.3 and needs stone below (or a timber frame on a stone footing); on the third
  x1.6, stone throughout. **Heavy fittings only on the ground floor** (stalls, cellar, kiln, millstones, water wheel, anvil, press).
- **Limits** that stop one giant hall winning: span by material, rooms by material, heat (a hearth warms about 10), upkeep growing
  with cost, land (lots per node), fire.

### Fire and the vault (D2-49)

Stone resists fire: it rarely catches, hardly spreads, and when it burns the walls stand and only the roof and contents are lost.
A **vault** (a room roofed with a stone arch: ground floor, small, much dearer, a mason with chisels and dressed stone) does not
burn at all: the place for a treasury, an archive of deeds, a granary or a strongroom. Proposed cost: about twice a stone room of
the same size.

### Fittings: a closed vocabulary (02i §3, cut by the pruning rule, 02g §1f)

First worlds: **beds, hearth, bins, benches, shelves, lock, anvil-and-bellows, millstones** (with a water wheel by a river), and **cellar and stalls** (D2-45). Each
has a cost, a capacity, upkeep, prerequisites and one hook in the rules. Oven, copy desks, loom, kiln and press come
with the goods that need them. Beds are one fitting for any number of beds up to the room's size (2 timber and a hide each), so a hall for 25 sleeps 25 and keeps its other slots (recipes.md §3, 23 Oct).

### Rooms as channels (02i §4; D2-9)

A room's speech scope is a channel. Its owner sets access: the household, members or a list, anyone at the node, or **whoever has
booked it for N rounds**. Booking is renting access; a locked booked room is a secret meeting, and who booked it is itself
information.

### Houses (02e)

The house is the first generic building: upkeep, rare breaks, the cold (H-5), tenure and rent. Its rooms and fittings follow this
file; 02e §3 holds the shelter rules.

### Stone and defence (D2-20)

Walls multiply the defence of those inside (proposed x1 timber, x2 stone) and a stone building is less likely to be picked in a
node raid. Its economics are 37.2's; the mechanism is 37.4's (conflict/defence.md, 02k).

## Why

Template buildings (house, mill, inn) fix what each building can do and multiply special cases. Parts let functions combine (a forge
with a meeting room, an inn with an archive of letters) and let specialisation branch by itself (02i §5's tree). Scaling and storeys
give towns and villages different shapes for a reason: land is short in towns, stone is what lets them build up.

## Alternatives considered

- **Template buildings with fixed functions** (02e §3.8's first form): replaced by D2-9.
- **The full 17-fitting list** (02i §3): cut to eight for first worlds by the pruning rule.
- **No storeys** (only building out): rejected by D2-3.
- **Hiding in a building** (unreachable for the round): later, once there is pressure to escape (02h §4a).

## Open questions

From 02i §8: the cost curve's exponent and the x0.8 for adjoining rooms; document capacity of shelves in documents or pages; fire
spreading from forges and kilns to neighbouring rooms; whether lots are 37.4's slots by land kind (OPEN C-2: proposed yes); upkeep
per fitting and per room.

## History

- 22 Oct: 02e: houses as the first generic building (upkeep, breaks, the cold, tenure).
- 22 Oct: Zach: rather than template buildings, rooms and capacities with resource costs; a hearth's difference from a room;
  archives that store documents. 02i: structures, rooms, a closed vocabulary of fittings; rooms bookable as channels (Zach).
- 22 Oct: Zach: capacity should extend, scaling efficiently. 02i §2b: the cost curve, adjoining rooms, limits.
- 22 Oct: Zach: building up costs more and needs stone; larger buildings must have stone. 02i §2c; D2-3.
- 22 Oct: the pruning rule cut the fittings to eight (02g §1f). D2-9 recorded buildings from parts as decided (23 Oct check).
- 23 Oct: stone's defence role (D2-20, 02k §3).

- 23 Oct: Zach asked whether a room for 25 has 25 beds. It did not: each bed counted as a fitting, so a hall slept 6. Fixed: beds
  are one fitting for any number up to the room's size; a room seats its size by day and sleeps it by night.

- 23 Oct: Zach: stone resists fire but is not fireproof; add a vault that does not burn (D2-49).

## Sources

[02i](../../review/37_growth/02i_buildings.md), [02e](../../review/37_growth/02e_shelter.md), [02g §1f](../../review/37_growth/02g_resources_and_transport.md),
[02k §3](../../review/37_growth/02k_fuses_and_gates.md), [02j](../../review/37_growth/02j_end_uses.md) (shelter and storage ladders);
D2-3, D2-9, D2-20, H-5.
