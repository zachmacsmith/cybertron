# Review 37: worlds that grow: work packages

*23 Oct 2026. Seven independent briefs, each to be handed to one agent, for the engine and generator work that makes societies deep
enough to be worth taking over. They come out of the first bench-36 batch (docs/review/36c_first_batch_log.md): every society there
was too small, hand-placed, food-only and static, and nothing in it grew. Read `docs/scenario_design.md` first; it holds the design
rules these packages serve.*

## Why

A society grows and builds institutions when it has surplus, people, room to expand and problems no individual can solve. The
engine is broad (a large law library, contracts, courts, force, channels, records, offices, positions, money, life) but offers few of
those things:

- **Few coordination problems.** Food is gathered alone, the hunting party is the only team production, a garrison cannot fight
  raiders, and public goods are marginal.
- **A thin economy.** Food is the only thing consumed; copper only makes blades; money buys little.
- **No growth.** Children cost 12 food when residents hold 1-3, caps are low, there is no frontier, and worlds are seeded with a
  handful of founders and no history.
- **Institutions cannot act on each other** (gap G-3), so a society of institutions is a set of islands.

## The packages

| # | Package | What it adds | Depends on |
|---|---|---|---|
| 37.1 | [Demography and growth](01_demography.md) | cheap children, surplus-driven population growth, households and marriage, a real childhood, inheritance of place | — |
| 37.2 | [Agriculture and a thicker economy](02_economy.md) | farming switched on and calibrated, several consumed goods, tools that raise yields, team production, specialisation that pays | — |
| 37.3 | [Institutions acting on each other](03_institutions.md) | a permissioned API for laws of one institution to read and act on another's (G-3), charters, hierarchy | — |
| 37.4 | [Environment over time](04_environment.md) | seasons with consequences, micro-events, long-term trends, all seeded and paired across arms | — |
| 37.5 | [Frontier and exploration](05_frontier.md) | unexplored land, expeditions that cost food and risk death, discoveries that unlock fields, forests and camps | 37.4 (events), 37.2 (what the land is for) |
| 37.6 | [Generated populations](06_population.md) | worlds seeded from distributions: family trees, households, occupations, holdings, debts, relationships and a short history; every field overridable by hand | 37.1 (households) |
| 37.7 | [Coordination problems](07_coordination.md) | problems only collective action solves: defence against raids that works, granaries against lean seasons, irrigation and walls as projects | 37.2, 37.4 |

37.1-37.4 can start at once in parallel; 37.5-37.7 after the first versions of their dependencies.

## Rules for every package

- **Opt-in and versioned.** Every change sits behind a spec key, off by default. Old runs replay byte-identically under their
  frozen settings; when a default must move, it is an engine version bump with an `ENGINE_FLIPS` entry (docs/engine_versions.md).
- **Prompts stay in world terms**, inside the prompt budget (a Haiku seat's institutional state ≤ about 400 tokens); new mechanics
  appear as concrete options with exact syntax, never as rules of a game.
- **No model usage to build or test.** Dry runs with scripted bots, unit tests, flows checks. Report the dry-run evidence.
- **Hand-crafting must stay possible**: anything generated or emergent can be fixed explicitly in a spec.
- **Measure what the mechanic is for** (each brief lists its acceptance checks), and add any new engine gap to docs/engine_gaps.md.
