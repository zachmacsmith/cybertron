# 37.1 Demography and growth: development log

Branch `wp/demography` (from `bench/first-batch`). Brief: [01_demography.md](01_demography.md). Cross-package contract: post 1 on
the `coord` branch (`docs/coord/BOARD.md`). Entries newest last, headed with the UTC time. Questions for Zach are marked `Q:`.

## Plan (agreed with Zach, 22 Oct)

Zach's decisions take precedence over the brief and the board where they contradict; otherwise the board's contract holds.

| Step | What | State |
|---|---|---|
| 0 | Log, design review against the shared rules | done |
| 1 | Baseline: tests, dry-run growth probe of today's pairs mode | done |
| 2 | Ages and labour: `age(agent)`, `labour(agent)` (0 below a set age, a fraction as a minor, 1 as an adult), law reads | next |
| 3 | Raising a child: cheap, quick conception; the first rounds' food decides survival (underfed minors are frailer) and loyalty at coming of age (well raised: takes up the family's cause; neglected: rarely turns against it) | |
| 4 | Children's work: minors forage or farm at their labour factor; what they gather beyond their keep goes to the household; minors play every k rounds | |
| 5 | Households as minimal institutions: an association running the Household template (pooled food pot), founded automatically at a couple's first birth, a `head` office, roster read (board contract A) | |
| 6 | Inheritance of plots and stores: `partible`, `eldest`, `household` (board loop 2) | |
| 7 | Scripted bots: conceive by household food and land per head, feed and keep children; dry runs for loops 1 and 2 | |
| 8 | Seats carry the model (heirs to pole seats get the seat's model) | |
| 9 | Docs: engine_gaps (G-6, G-7), scenario_design §5, the brief's "as built" | |
| 10 | A small live test, when Zach says go | |

Dropped (Zach, 22 Oct): automatic or hazard births (fertility stays a choice), dependents held as counts, marriage in the engine
(a world can add it as law through `before_conceive`).

## Entries

### 2026-10-22 16:45 UTC: review and baseline

- **Doing:** reading the brief against the shared rules (37 README, scenario_design.md) and the code.
- **Found:**
  - Food capacity is fixed at the starting population: `subsistence.compose_camps` (cybertron/subsistence.py:889) sets
    K = capacity_per_agent x N0. Default forests carry about 1.5 N0 at perfect management, the Hearth's about 2.5 N0. Growth to a
    doubling needs land that grows (37.2 fields, 37.5) or capacity set high by hand.
  - Today a child is a pure cost: parents pay 5 + 1 food each (`life.reproduction`, cybertron/life.py:101), and everything the child
    gathers is its own.
  - Children default to the weak model (`reproduction.model: "weak"`), so a long run drifts to all-Haiku as founders die
    (scenario_design §2).
  - The lineage line ("goals about your own holdings or offices count only through living descendants", cybertron/life.py:1367)
    is a scoring proxy shown to agents (scenario_design §3).
  - Tests: life, pairs, succession, demography: 139 passed, 1 skipped.
  - Dry run, `nature_pairs`, 16 workers, 100 rounds, lifespans U[60, 120] stationary, default heirs children, seed 1: population
    16 -> 11 (round 10) -> 9 (30) -> 6-7 (50-60); deaths 11 old age, 6 attacks. With default lifespans, 11 births in 100 rounds.
    The bots offer to conceive whenever they hold 14+ food, and rarely do: at today's price even eager bots cannot replace the dead.
- **Decided:** see the plan. Fertility stays a choice: what makes children worth having is that they work for the household and,
  well raised, take up the family's cause; what makes it a real decision is that a neglected child may die or turn against them.
- **Q:** in growth worlds, drop the lineage-scoring line from the prompt? (It is a scoring proxy; the in-world fact "what you hold
  passes to your children, or to the polity if you have none" can replace it.)

### 2026-10-22 17:20 UTC: coordination board

- **Doing:** replied to post 1 on `coord` (the couplings contract): agreed, with Zach's changes (choice fertility; households as
  minimal institutions; `labour(agent)`; inheritance `partible | eldest | household`; minors' work through 37.2's standing orders).
  Asked 37.2 for a plot-split primitive and the minimum viable plot size.
- **Found:** existing pieces to reuse:
  - The Household contract template (cybertron/library.py:4049): pooled food pot, feeds members and their minor children.
  - The investment ledger and coming-of-age draw (cybertron/pairs.py:675, 711).
  - Ally and Foil goals (cybertron/goal_registry.py:500): an agent scores exactly what, or 1 minus what, its target scores. These
    are the family's cause and its opposite.
  - `start.kin` for founding families (cybertron/start.py:960).
  - `subsistence.minor_yield` (0.5): a minor's foraging fraction, which becomes the labour factor.
- **Next:** step 2.
