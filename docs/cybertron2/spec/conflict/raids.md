# Raids: on a building and on a whole node

## Summary

A building can be raided (a break-in, then a fight with whoever defends it) and a whole node can be raided by any party, however
small. In a node raid each raider's target is drawn by exposure, value and hardness, so stone is picked less often and is stronger
when it is. A raiding party states in advance what it will take and what it will burn; fire kills those who do not get out.

## Decided

- D2-20: an attack on a building is a break-in whose work depends on the structure, then a fight with whoever defends; an attack on
  a whole node draws targets by exposure, value and hardness, so a stone building is less likely to be picked and stronger when it
  is; walls multiply the defence of those inside (defence.md).
- D2-22: any party may raid a node: no minimum size; a small party usually fails and the outcome depends on the defences; a single
  rider may attack, at greater risk.
- D2-51: a node raid can include orders to burn, stated in advance when the raid is planned (what to take, what to burn, and when,
  such as on leaving); raiders cannot change them mid-raid.
- D2-49: stone resists fire but is not fireproof (rarely catches, hardly spreads; when it burns the walls stand and the roof and
  contents are lost); a vault does not burn at all.
- D2-50: anyone still inside when a building burns down is very likely to die; waking in time and getting out is how people survive.

## Mechanics

| Kind | Target | How it resolves |
|---|---|---|
| raid a building | one building at the node | a break-in (work set by its structure), then a fight with whoever inside chose to defend; an empty building is the break-in only (D2-20) |
| raid a node | the whole node, by a party of any size | each raider's engagement draws a target weighted by exposure, value and hardness (D2-20, D2-22) |

- **Orders:** a node raid is planned with its orders (take, burn, when); they hold for the whole raid (D2-51). Only the defenders
  respond during it (defence.md, fuse events).
- **Fire:** a building set alight burns unless fought; stone keeps its walls and loses roof and contents, a vault loses nothing
  (D2-49). Those still inside when it burns down very likely die (D2-50).
- Raids are settled at night (round.md), at the node, and seen by those present (D4-35).

## Data

Per raid: the party, the node, the orders, the targets drawn, the outcome. Per building: structure (its hardness and how it burns).

## Parameters

| Parameter | Value | Status |
|---|---|---|
| break-in work by structure | proposals/attacks_and_walls.md | calibrate |
| exposure weights in a node raid | proposals/attacks_and_walls.md | calibrate |
| catch chances by structure; death for those still inside | 0.8 wattle to 0 vault; about 0.9 | calibrate |

## What agents see

A raid on their node as it happens to them (woken, attacked, a fire), and afterwards what they saw: who came, what was taken or
burned, who died.

## Open

- The numbers above, tools that shorten a break-in, the bucket line: proposals/attacks_and_walls.md.
- Riders who travel and strike in one day (OPEN C-5).

## Sources

proposals/attacks_and_walls.md; 02k §3; 02g §5b.

*Current as of 23 Oct 2026: D2-20, D2-22, D2-49, D2-50, D2-51.*
