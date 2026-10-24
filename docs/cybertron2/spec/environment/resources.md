# Resources and how they come back

## Summary

Each resource on the land comes back in one of five ways. Depletion, exhaustion and collapse are the resources' own physics, not
scheduled events.

## Decided

- D2-156: a forest as three stocks (trees, young growth, dead wood), at roughly real magnitudes by kind.
- D2-158: default rights in woods.

- D4-7: resources by how they come back: finite, fast renewable, renewable with a threshold, slow, periodic.
- D4-4: internal consequences (depletion, exhaustion, collapse) are the resources' own physics.

## Mechanics

| Regime | Example | Rule |
|---|---|---|
| finite | a copper seam | what is taken is gone |
| fast renewable | plants for foraging | grows back toward its capacity each night |
| renewable with a threshold | game | grows back, but below a threshold it collapses |
| slow | standing timber | grows back slowly |
| periodic | a crop, a fish run | comes at its time and must be taken in its window |

### Forests (D2-156, D2-158)

A forest parcel holds three stocks, each with its own regime:

| Stock | Regime | Grows | Taken by | Gives |
|---|---|---|---|---|
| trees | slow | about 0.5% a year (old forest), 1% (managed wood, copse), toward the parcel's capacity | felling (a tool) | timber; brash (1 firewood a timber) left as dead wood |
| young growth | fast renewable | 50% to 100% a year; **not while beasts graze the parcel** | cutting (a tool) | firewood (or poles, open) |
| dead wood | fast renewable, fed by the trees | the trees shed about 1% of their timber a year as dead wood (4 firewood a timber), plus brash and windfall; rots about 30% a year | gathering (by hand) | firewood |

| Kind, a unit of size | Trees (timber) | Young growth | Dead wood | Firewood a year it gives back | Hearths kept warm on that |
|---|---|---|---|---|---|
| old forest | 2,500 | 50 | 300 | about 106 | 1.3 |
| managed wood | 600 | 400 | 100 | about 124 | 1.5 |
| copse | 300 | 40 | 50 | about 18 | 0.2 |
| scrub | | 60 | 10 | about 9 | 0.1 |

- **Health** is the trees and young growth against capacity; under about 40% of its trees the parcel's cover turns to scrub (and
  its sight to 0.5: visibility.md). A wood with fewer trees sheds less dead wood, so felling a near wood lowers its firewood for good
  until it regrows: a commons that can collapse.
- **Gathering** gets less as the dead wood thins (3 a unit at a full pool, less below).
- **Rights** (D2-158): dead wood, and young growth on common land, are anyone's to gather; trees are their holder's.
- **Game and forage** read the forest: game's capacity rises with trees and young growth (cover and browse); forage in the
  understorey rises where trees are thinned (light).
- **Gales** throw trees (trees down, dead wood up: a windfall, D2-79); drought dries dead wood (fire later, OPEN L-21).

Growth slows in winter. A tool never adds to a resource; it only takes it faster (recipes.md §8, a proposal).

## Data

Per parcel resource: its regime, its stock and capacity, its rate.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| rates, capacities, thresholds | per world | calibrate |

## What agents see

Resources in words ("picked over", "thick with berries", "the game is thin"), never as numbers.

## Sources

devlog 37.4 #7; 38.04 §5.

*Current as of 24 Oct 2026: D4-4, D4-7, D2-156, D2-158.*
