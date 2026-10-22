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

### 2026-10-22 18:20 UTC: steps 2-3, ages, labour, raising a child

- **Doing:** ages, the labour factor, and family raising.
- **Built:**
  - `life.age(k, aid)`: elapsed at entry plus rounds since (born agents from their birth, arrivals from arrival).
  - `life.labour(k, aid)`: 1 for adults; for a minor `life.labour.minor` (default `subsistence.minor_yield`, 0.5), 0 below
    `life.labour.from_age` (default 0, so unchanged). It now scales a minor's yields (`subsistence.yield_mult`).
  - Law reads `age(agent)` and `labour(agent)`, documented only in family worlds.
  - `life.reproduction.raising` (mode `inherit` = today, `family` = new):
    - the ledger records each parent's food (`minors[c]["by"]`);
    - at coming of age one draw (the existing stream) gives loyal with p = lo + (hi - lo) x, estranged with p = e (1 - x)^2,
      else own way, where x is the investment share (the existing formula);
    - loyal sets primary Ally {target: the parent who gave more, family: true}; estranged sets Foil; the old primary becomes
      secondary, and a goal boundary means the child is scored as two segments;
    - Ally and Foil get family wording (`goal_registry.FAMILY_TEXTS`) instead of "secretly ...", and no score wording;
    - `minor_frailty` raises an underfed minor's starvation hazard base;
    - parents learn only "comes of age" unless `tell_parents`;
    - prompt lines in world terms: parents see "a child well fed while it grows up is likely to stand by you ...; a neglected
      one may die young, and now and then turns against the parent who failed it"; minors see that how they are raised weighs on
      it.
  - Tests: `tests/test_family.py` (14).
- **Found:**
  - Adding default keys changes `instance.json` in all 11 golden cases. Events, snapshots, scores and prompts are unchanged, so
    the fingerprints were refreshed (the test's own instructions for a deliberate change).
  - On a clean `bench/first-batch`, 14 tests fail and 7 error already (consistency, contract, eventtypes, rights_writes, tiers,
    dataset_naming, farming replay, history, continue). These are not ours. Only `test_cybertron_lawapi` needed updating for the
    two new law functions.
- **Decided:**
  - Loyalty uses the existing Ally and Foil goals rather than a new goal: their scorers already follow a target's score, so a loyal
    child succeeds exactly when its parent does, which is "another agent working for your goals".
  - The target is the parent who gave more food: the investment decides whose cause it is.
- **Next:** step 4, children's work (a minor's surplus to the household; minors play every k rounds).

### 2026-10-22 19:05 UTC: steps 4-5, children's work and households

- **Built:**
  - Children's work:
    - `life.labour.surplus: household` (default `none`): after eating, a minor's food beyond `life.labour.keep` (2) goes to its
      household's pot, else to its living parents in equal shares (a move, why `household`).
    - `life.reproduction.raising.turn_every k`: a minor takes a turn only in rounds born + j*k (runner filters the order after
      the shuffle, so the order stream is unchanged). The minor's state line says so.
  - Households (`cybertron/households.py`, `life.households.enabled`, needs pairs and contracts):
    - a household is an association running the library's Household template (pooled pot, feeds members and their minor
      children);
    - it is founded automatically at a birth: the child joins its parents' shared household, else the one a parent heads (the
      initiator's first), else a new "<initiator>'s household" with both parents and the child;
    - a parent who moves leaves its old household (a leave request, made good at round end through the template's after_leave);
    - the head passes at death to a co-parent member, else the eldest adult member;
    - roster read `households()` [{id, name, head, members [{agent, age}], pot, plots}] and `household_of(agent)`, documented in
      household worlds;
    - a state line for members; a `household` monitor event; truth under `life.households`.
  - Tests: `tests/test_family.py` (22 in all).
- **Found:** contracts install after life (features.PHASES init order), so the households install checks the spec
  (`FT.on("contracts", k.spec)`), not `k.w`.
- **Decided:**
  - The head is recorded by households.py rather than as an Offices Act office. An office needs institutions.grants and law
    code per household. Kept minimal, as Zach asked; 37.3 gets "someone who acts for it" from `head`.
  - Q: should a household head be an office (so 37.3's appoint/remove powers apply to it)? It is cheap to add later.
- **Next:** step 6, inheritance (`partible | eldest | household`) in `subsistence.on_death`, where stores and plots already pass
  to `_store_heir`.

### 2026-10-22 19:30 UTC: step 6, inheritance (board loop 2)

- **Built:** `life.households.inheritance: none | partible | eldest | household` (read whenever pairs is on, with or without
  households), applied in `subsistence.on_death`:
  - stores go to the first heir (a store is not divided);
  - plots under `partible` go round the living children, eldest first, as whole plots; under `eldest` all go to the oldest living
    child; under `household` all go to the household's id (else as `eldest`); `none` is unchanged;
  - a household's head may withdraw from a store the household owns (`subsistence.can_withdraw`).
  - Tests: 4 more in `tests/test_family.py` (26).
- **Found:** today's heir is the first living child by id, not by age (`subsistence._store_heir`); `none` keeps that.
- **Open (37.2):** partible hands out whole plots; splitting a plot below a minimum viable size waits for 37.2's plot-split
  primitive (asked on the board).
- **Next:** step 7, family-aware scripted bots and a growth preset; dry runs for loops 1 and 2.

### 2026-10-22 20:00 UTC: step 7 (bots, preset, analysis) and step 8 (the seat carries the model)

- **Built:**
  - Family bot (`pairs._family_bot`, family worlds only, so other bots and goldens are unchanged). It conceives with a chance
    rising with household food per head (0 at 2 rations, up to 0.5 at 8), halved below one plot a head where fields exist, with a
    partner from its household when it has one.
  - `cybertron/specs/fragments/growth.yaml`, the 37.1 settings in one place:
    - conception 1 + 0.5 food, born next round;
    - maturity 12, minors work from age 3 at half yield and pass surplus above 2 to the household;
    - family raising, minor frailty 0.6, minors act every 3 rounds;
    - households, eldest inheritance.
  - `cybertron/specs/growth_probe.yaml`: 16 founders, fields, conflict off, forest capacity raised by hand to 14 per agent,
    150 rounds.
  - `python -m cybertron analyze demography RUN..`: population, births, deaths by cause, coming-of-age outcomes, households,
    turns per agent-round by age group, per window.
  - `life.households.head_model: keep | inherit`: a new household head takes the dead head's model when stronger (opus > sonnet >
    haiku), so heirs to a pole seat keep the seat's model.
- **Board:**
  - corrected my reply: the head is recorded by households.py, not an office, and households need contracts but not unified;
  - confirmed `life.labour(k, aid)` to 37.3;
  - agreed to post 2 (graph of places): households will get a home node, and feeding, surplus and inheritance become "at its
    node".
- **Doing:** three 150-round dry runs (growth eldest, growth partible, baseline without the fragment).
