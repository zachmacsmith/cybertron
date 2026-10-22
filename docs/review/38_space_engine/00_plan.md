# Review 38: a new engine on a graph of places (plan)

*22 Oct 2026, from the 37.2 session. Plan for discussion: nothing built. Decided by Zach on 22 Oct: build space as a new engine in
its own package instead of retrofitting the old one, port the physical modules onto nodes, and test with LLM agents early rather
than relying on scripted bots. Background: review 17 (space), board Post 2 (the world becomes a graph of places), the 37.2 design
notes (docs/review/37_growth/02a-02e).*

## 1. Why a new engine

- **Space touches every physical act.** Review 17 counted about 60 code sites that name a harvest right, 42 that move goods and 98
  that read balances. Each would need a location check.
- **Retrofitting means two paths everywhere.** The old engine must keep a one-node world byte-identical (replay, goldens, frozen
  settings, ENGINE_FLIPS), so every ported module would carry an old path and a spatial one.
- **Review 17 already concluded** that space "is a different simulation family that shares the kernel".

So the old engine is **frozen** for the bench batches and for reproducing published runs. The new one starts without replay
obligations and moves fast. Replay versioning begins the day its first run matters.

## 2. The seam, and what that means for copying

The engine has a clean seam at the **kernel interface**, not at module boundaries:

- the routed primitives through `k.apply`;
- balances and accounts;
- the law hooks.

Laws, contracts and courts talk to the world almost entirely through that interface. But the modules themselves are wired
together: the law language imports the primitives table, and the kernel imports 37 modules. So only leaf modules can be imported
unchanged. The institutional layer is **copied**, keeping its interface and its fixes, and adapted where it reads the world.

## 3. Inventory (167 modules, 91k lines)

| Treatment | Modules | Lines | What |
|---|---|---|---|
| **import** unchanged | 9 | 2.5k | llm, gas, sandbox, privacy, temperament, personality, archetypes, probing, agent_rules: no engine dependencies |
| **port onto nodes** | 23 | 19.3k | kernel, accounts, primitives, the economy, world and force changes, subsistence, forest, fields, the camp framework, resources, conflict, mortality, life, pairs, start, generator, events, actions, action_registry, projects, flows analysis |
| **copy and adapt** | 71 | 45.9k | contracts, standing, obligations, institutions, positions, jurisdictions, library, the law language and its tools, credit, courts, succession, registers, grants, powers, rights, channels, context, agents, memory, history, runner, goals, scorer, spec, settings, provenance, features, eventtypes, schema, the dispatch core, the default code |
| **later** | 26 | 14.1k | export, publishing, replay, rerun, interview, interventions, reports and analyses, digest, preview, directories, documents |
| **leave behind** | 31 | 8.4k | the dial camps and their modifiers, leases, media2 and Scholars, hidden caps, roles (Board, Fixer), the observer, the old outside power, tiers, regimes, difftest and armdiff, the legacy dispatch |

The copy-and-adapt group carries most of the hard-won fixes. Engine versions 9, 11, 19 and 22 each fixed a real ballot or contract
bug. Copying keeps them; rewriting would lose them.

## 4. Porting the physical modules: what changes

| Module | On nodes |
|---|---|
| kernel, accounts | every holding is at a node: an agent's goods where it is; a store's, a building's and a treasury's at their seat (review 17, condition 3: no global ledger). Balance reads are local; a transfer needs both parties present, or a carrier |
| primitives, actions | presence gates on every physical act (harvest, sow, reap, build, transfer, attack); a `travel` action; edges cost actions (and food) |
| subsistence | the ration from what the agent holds at its node and its house's pot; seasons from 37.4's calendar; stores located |
| forest | one forest per forest node, its flow fixed per node (37.2d: about 1 food per forage action, capped by regrowth); felling shrinks it |
| fields | plots belong to an arable node; holder field kept (37.3's tenures, 37.1's inheritance) |
| camp framework | camps become sites on nodes |
| conflict | an attack needs the attacker and target at one node; defenders are those present |
| life, pairs, mortality | a household's home node; births there; estates at the node |
| start, generator | the seeded world placed on nodes: households in houses, plots, stores, workshops |
| projects | construction becomes the building model (37.2e §3.8): sites, work, upkeep |

New in the core (designed in 37.2): buildings (houses, stores, workshops), shelter and the cold, the ration multiplier, skills by
practice, recipes through `convert`, subscriptions, transport costs.

## 5. Phases

| Phase | Builds | Evidence |
|---|---|---|
| **0: the hamlet** | the node graph, presence and travel, located accounts, the ported kernel interface and dispatch; subsistence, forest, fields and stores on nodes; houses and the cold; the LLM turn loop and prompts with a node-local state view | smoke tests with scripted bots (determinism, no crash: fixtures, not evidence); then **one small LLM run** |
| 1: institutions | the law language, contracts, standing contracts and subscriptions, households (37.1), positions, channels per node | small LLM runs |
| 2: the economy | skills, workshops and recipes (37.2), conflict at nodes, life and children | LLM runs at 24 agents |
| 3: parity | export, analysis, replay versioning; the parity checklist met | the new engine replaces the old for new worlds |

**The first LLM world (phase 0):** 3 households of 4 (12 agents) on 4 nodes: the hamlet (houses, a store), fields, a forest, hills.
20-30 rounds, cold rounds scripted until 37.4 exists, in-world aims. The cast follows scenario_design §2 (no all-Haiku society),
for example 3 Opus household heads, 4 Sonnet, 5 Haiku.

What it answers:

- Can households feed and house themselves within the action budget, at or below 30% of actions?
- Do they trade or subscribe at all?
- Does the cold bite?
- Does travel cost shape who goes where?

## 6. Coordination

- **37.1** (households, ages, labour on `wp/demography`) and **37.3** (powers between institutions on `wp/inst-cross`) are mostly
  institutional: they carry over by the copy rule, but each must say what it reads of the physical world.
- **37.4** is designing the space interface: it becomes the new engine's node model.
- **37.2's designs** (02a-02e) become the new core's economy.

### Draft board post (for Zach's approval; not posted)

> **Post 3 (37.2 for Zach): space is a new engine, not a retrofit.** @37.1 @37.3 @37.4 @lead
>
> Zach has decided to build space as a new engine in its own package (plan: docs/review/38_space_engine/00_plan.md on
> `econ/37.2-thicker-economy`). The old engine is frozen for the bench batches and published runs.
>
> - The physical modules are ported onto nodes.
> - The institutional layer (law language, contracts, courts, positions, channels, the turn loop) is copied with its interface
>   and fixes.
> - The first test is a 12-agent hamlet run with LLM agents.
>
> What this means for you:
> - 37.1 and 37.3: your work carries over if it talks to the world through the kernel interface. Please reply with anything that
>   reads physical state directly.
> - 37.4: your node model becomes the engine's.
> - Nothing already built needs to stop. New physical work should target the new engine.

## 7. Open decisions

1. **Where it lives:** a new top-level package in this repo (proposed: `cybertron2/`, sharing specs and docs) or a separate repo.
2. **LLM budget for testing:** the 37 README says "no model usage to build or test". Zach's decision to test with LLM agents changes
   that; it needs a budget per phase.
3. **Who announces it:** Zach, the lead session, or the draft above.
4. **Who builds phase 0:** this session, 37.4 (which owns the node model), or a new one.
5. **The parity checklist** for when the new engine takes over new worlds.
