# Review 38.07: cybertron 1 as an engine, and what cybertron2 should take from it

*22 Oct 2026, 37.4 session, at Zach's request. Read: `docs/ARCHITECTURE.md` (the target architecture of 7 Oct and its as-built
notes), `docs/engine_versions.md`, the registries in code, and the modules cybertron2 touches. Complements 00_plan.md §3 (the
inventory by treatment) and porting.md (the ledger). Design only.*

## 1. What cybertron 1 is, in one picture

| Layer | What it is | Size today |
|---|---|---|
| **State** | one plain JSON dict `k.w`; accounts are owner keys (`agent`, `reserve`, `reserve:<jid>`, `store:<sid>`, `escrow:<cid>:<aid>`, `fund:<lid>:<name>`, `estate:<aid>`) | |
| **The chokepoint** | every state change is a **primitive** applied through `k.apply(name, **payload)`: physics checks, before-hooks (laws may block or charge), the change, after-hooks, all inside a **cause stack** so every event knows what caused it | 132 primitives |
| **Events** | `k.log(type, agent, data, vis=)` with explicit visibility on every call; a registry of event types with their audiences and renderers | 318 event types |
| **Law** | sandboxed Python with a static whitelist, gas metering, classes and ranks; hooks `before_<p>` / `after_<p>` on primitives; procedures, ballots, vetoes; imports between laws; previews and dry runs | 180 law functions; `dispatch/` package |
| **Institutions** | polities (jurisdictions) and associations (contracts): members, treasuries, escrow, allowances, atomic `swap`, standing contracts, agency (`authorize`, `act_for`), offices, succession, incorporation, grants of power | contracts 2.5k, standing, obligations, institutions, positions, succession, grants |
| **Actions** | a registry of what agents may do, each with its handler, gates (rights, modules, hunger) and docs | 145 actions, 21 kernel rights |
| **Features** | one row per optional module: its spec flag, state keys, RNG streams, phase functions in a fixed order | 18 features |
| **Agents' view** | sections (core prompt, manual, state lines), budgets, look-ups, memory modes, the DM step | context, memory, sections, agents |
| **The instrument** | events.jsonl, snapshots, checkpoints each round, frozen settings, replay, fork, interventions, History and post-hoc scoring | 22 engine versions |

Totals: about 90k lines in 150 modules; the kernel imports 43 of them; `base.yaml` has about 300 keys and `schema.EXTRA` 98 more.

## 2. The ideas worth keeping (port the idea; copy code where it is clean)

1. **One chokepoint for every change, with hooks and causes.** This is what makes laws and contracts general: a rule can attach to
   any change, whoever caused it. cybertron2 today changes state directly in `act.py` and `world.py`. **It needs this before any
   law or contract can be ported.** It is also what standing orders should be built on (§5).
2. **Every event has a cause and an audience.** In cybertron2 the audience should mostly derive from **presence** (who is at the
   node), which replaces most of the 318 types' hand-set visibility.
3. **Registries that fail on unknown names**, and one completeness test across them.
4. **String-seeded RNG streams**, keyed by seed, stream and round (already in cybertron2).
5. **The law language** (whitelist, gas, static classification, hooks on primitives, procedures, ranks, imports, previews).
6. **The institution layer:** membership, treasuries, escrow, atomic swap, standing contracts, agency, offices, succession,
   incorporation. These carry real bug fixes (engine versions 9, 11, 19, 22).
7. **The instrument:** frozen settings, checkpoints, replay and fork, interventions, post-hoc scoring from History.

## 3. What drifted or bloated, and the cleaner form for cybertron2

| In cybertron 1 | Why it grew | In cybertron2 |
|---|---|---|
| **Two or three paths for everything**: law v1 and v2 (`law.v2` is named in 357 places), legacy hook aliases, jurisdictions vs `institutions.unified` vs `grants` vs `succession` flags with `legacy_view` projections back to old shapes, media2 frozen beside channels v2, the context-off prompts beside sections, `rng_version` 1 and 2 | the rule that every old run replays byte-identically, so each change shipped behind a flag with the old path kept | **one path**: copy only the v2 / unified forms; no flags for old behaviour; replay obligations start at cybertron2's first run that matters |
| **Seven ways to speak**: dm, reply, send, post, anon_post, channel_post, papers (plus the DM step) | each review added a channel | **talk at the node** (the talk step), **letters** (carried items), **notices** at a node; groups are people who meet; papers later as carried items |
| **Accounts as parsed strings** (`store:`, `reserve:<jid>`, `escrow:<cid>:<aid>`, `fund:<lid>:<name>`, `estate:<aid>`) | each feature added an owner kind | **containers with a place**: an agent's pack, a house's stock, a store, an escrow, a treasury, each a record with a node and an owner; goods move between containers at the same node, or by carrying |
| **Rights as strings**, including one `harvest:<camp>` per camp | access was granted per camp | **access to land is tenure**: a site or a plot has a holder (agent, household, institution), and law decides who may use it; rights stay for powers and offices |
| **Kernel roles as exceptions**: the Board, the Fixer, the observer, Makers, Scholars, the assassin, each with its own branches | each experiment needed a role | **drop**; anything institutional is an institution's office |
| **"Today's order" constraints**: feature tables kept in a hand order because snapshot and prompt bytes depended on it | byte identity | order chosen once, by design |
| **The spec surface**: about 400 keys and flags, many of them tuned dials | every package added defaults | a short world spec (places, people, institutions) plus one `physics` block; anything tunable is data |
| **Turn modes**: sequential, simultaneous, fast mode, buy_initiative | experiments | **simultaneous only**, with the talk step |
| **Dial camps** (search puzzles) | the early economy | drop (00_plan) |
| **Goals with scoring rules shown to agents** | the benchmark | in-world aims in prompts (scenario_design §3); scoring stays post-hoc, never shown |

## 4. Port plan for the institution layer

Order (each step needs the one before):

1. **The chokepoint in cybertron2**: primitives for every physical act it already has (travel, forage, hunt, fell, mine, give,
   store, take, attack, raid, eat, die), `apply` with before/after hooks, the cause stack, an event log with presence-derived
   audiences. Rewritten small, following cybertron 1's design (§3.3 of ARCHITECTURE), not copied.
2. **Containers** (agent packs, house stocks, stores, treasuries, escrow) with a node each.
3. **The law language and dispatch, v2 only**: copied, with the v1 path, the legacy aliases and the flags removed at copy time;
   cybertron 1's tests for them ported as fixtures, so the fixes stay fixed.
4. **Households as the first institution** (37.1): members, a treasury (the house stock), a head as an office.
5. **Contracts**: escrow, swap (the face-to-face `offer`/`accept` of 05 §4 is a swap), allowances, standing contracts, agency
   (proxies for absent members), with signing at a node or by sealed letter.
6. **Offices and succession**, then **courts** (at a seat), then polities with territory (later).

Risk: copying 46k lines of the institutional layer brings its bloat with it. The rule for each copied module: v2 path only, no
compatibility flags, its tests come with it, and anything that reads physical state goes through the new chokepoint.

## 5. Standing orders are hooks

cybertron 1's ARCHITECTURE already says standing orders are contract templates, not kernel features (§7.2). On the chokepoint, a
**reflex** ("if attacked, fight back") is a hook an agent owns on a primitive that names it (`before_attack` with the agent as
target), and a **fallback** is a hook on its own refused action. So standing orders need no separate condition list: they are
small hooks from a fixed menu of templates, owned by one agent, binding only itself. That is why the chokepoint comes first.
