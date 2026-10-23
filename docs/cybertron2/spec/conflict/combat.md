# Combat: attacks on a person

## Summary

Force is an act like any other: one person attacks another at the same node, and the fight is settled at night. Weapons raise
strength and wear with use. Attacks on buildings and on whole nodes are in raids.md; what slows and detects them is in defence.md.

## Decided

- D2-20: three kinds of attack: on a person, on a building, on a whole node (raids.md for the last two).
- D2-46: weapons wear on the one wear scale for tools; a fight is heavy use (a blade lasts about 10 fights, a crude weapon about
  3); a small chance of breaking in a fight; a smith mends a worn blade.
- D2-23: weapons (crude, blade) serve in fighting and hunting.
- D4-35: an attack happens at a node, between people there, and is witnessed by those present.

## Mechanics

- **Attack a person:** `attack {target}` against someone at the attacker's node; the fight is settled at night (round.md) from
  each side's strength (weapon, wounds, hunger) and who stands with them (`guard`).
- **Weapons wear:** each fight uses a weapon by the fight factor on the wear scale (production.md, D2-46), and may break.
- **Witnesses:** everyone at the node sees the fight and who started it (information/perception.md).

## Data

Per person: weapon in hand, wounded or not. Per fight: who, where, the day, the outcome.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| a fight's wear factor | 4 standard uses (recipes.md §9) | calibrate |
| a blade's and a crude weapon's life in fights | about 10; about 3 | decided (D2-46) |
| the chance of breaking in a fight | small | calibrate |
| strength, guard and asleep multipliers | the engine's (38.17) | calibrate |

## What agents see

Fights at their node and who started them; their own wounds; their weapon's wear in words.

## Open

- An attacked person's response (reflexes, fuse events): defence.md, proposals/fuse_events.md.

## Sources

proposals/attacks_and_walls.md, proposals/recipes.md §9; 38.03; 38.17.

*Current as of 23 Oct 2026: D2-20, D2-23, D2-46, D4-35.*
