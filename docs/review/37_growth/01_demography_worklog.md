# 37.1 Demography and growth: worklog

Branch `wp/demography` (from `bench/first-batch`). The brief is [01_demography.md](01_demography.md); this file says what is being
built, what was decided and why, and what is done. Newest log entries at the top of the log. Pushed after every step.

## Status

| Step | What | State |
|---|---|---|
| 0 | Worklog, design decisions against the shared rules (README, scenario_design.md) | done |
| 1 | Baseline: the existing tests, and a dry-run growth probe of today's pairs mode | next |
| 2 | Cost and push: provisions per parent, per-round upkeep of a minor from the household | |
| 3 | Fertility: `life.fertility: chosen \| hazard` (births as a per-round chance by household food per head), `born_at` schedule | |
| 4 | Households (members, head, shared store, land, head succession) | |
| 5 | Marriage (consent, law hook, only married couples conceive by default) | |
| 6 | Childhood: minors play every k rounds; maturity as a setting worth using | |
| 7 | Seats carry the model (a child gets its model when it inherits a pole seat) | |
| 8 | Seniority by age; inheritance of land (partible, impartible) | |
| 9 | Kin as a relation laws can read | |
| 10 | Demography metrics and the acceptance dry runs | |
| 11 | Docs: engine_gaps (G-6, G-7), scenario_design §5, engine_versions | |

Order may change once the code is read; the log says when it does.

## Decisions (from the review before building)

Read against docs/scenario_design.md and the 37 README rules (opt-in, byte-identical replay, world-term prompts within budget, no
model usage, hand-crafting possible, measure what the mechanic is for).

1. **Food capacity is fixed at the starting population** (`subsistence.compose_camps`: K = capacity_per_agent x N0). Default forests
   carry about 1.5 N0 at perfect management, the Hearth's about 2.5 N0. "Doubles within the food bound" therefore needs land that
   grows (37.2 fields, 37.5 frontier) or a capacity set high by hand. The acceptance runs set it by hand and say so.
2. **Growth to the ceiling breaks scenario_design §4** (capacity ≥ 1.25x demand in normal times). Fertility must fall as food per
   head falls, so the population settles near that margin rather than at the famine line.
3. **Hazard fertility** (`life.fertility: hazard`): married couples have a per-round birth chance set by household food per head,
   with an opt-out action. Reasons: (a) the package may not use models, so under chosen fertility its goal cannot be verified (dry
   runs only show what follows if agents choose children); (b) arms must stay comparable (Control Share is read against the null
   arm, and population that differs by agent whim confounds it); (c) it gives decision 2's settling point. `chosen` stays (today's
   conceive) for worlds that study dynastic strategy. A dry-run sweep over the bots' propensity to conceive reports how growth
   depends on it under `chosen`.
4. **The seat carries the model** (scenario_design §2: never all-Haiku). Children default to the weak model, so a long run drifts to
   an all-Haiku society as Opus founders die. A child's model is set when it takes a pole seat it inherits (a landed household's
   head, an office marked as a pole), not only at birth.
5. **Households must not all be self-sufficient** (§1: a node that needs nothing is passive). Impartible inheritance (landless
   younger children) is the main route by which demography makes dependence, so it is part of the package, not an option.
6. **Lineage scoring line** ("goals about your own holdings or offices count through your living descendants") is a scoring proxy
   shown to agents (§3). Growth worlds should be able to drop it; flagged, decision for Zach.
7. **Open questions to settle while reading the code:** households as a third institution kind (reuses treasuries, offices,
   succession, dissolution; needs `institutions.unified`) or a light object of their own; marriage as a contract template or a
   primitive; dependents held as counts (no model calls) or only as agents.

## Log

- **Step 0.** Branch and this worklog. Read the brief, the 37 README, scenario_design.md, pairs.py, life.py (config, cap,
  install), succession.py (rules), subsistence.py (capacity, ration, seasons), the Hearth spec and the demography fragment.
