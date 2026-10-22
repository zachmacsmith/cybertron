# 37.2a Agriculture and a thicker economy: diagnosis and design

*22 Oct 2026. Design note for work package 37.2 ([02_economy.md](02_economy.md)); progress in
[02_economy_worklog.md](02_economy_worklog.md). Read with docs/scenario_design.md §1 and §4.*

## 1. Diagnosis: thickness is dependence, not the number of goods

A good adds dependence only if most agents cannot make it themselves. The engine numbers say that is what keeps the economy thin
today:

- **Food is cheap per action.** A forage at full stock yields 3 food; the ration is 1 and loose food spoils 15% a round, so an agent
  forages about every 2-3 rounds: about 10-15% of a 3-4 action turn. The 37-55% food share of the first batch (36c 07:55) came from
  forests run down near their floors, not from food being dear in principle. Every agent feeds itself.
- **Farming yields less per action than foraging, by design** (user, 15 Oct: a field yields less than the same forest area kept
  well; 31.01b §6). Six farmers make 23-32 food from about 18 actions: **1.3-1.8 food per action against 3.0 for a forage.** With the
  forest open, switching farming on changes nothing: agents forage. Farming becomes the economy only where the forest is held,
  licensed or run down, or lies beyond a frontier (37.5).
- **Every trade costs actions.** An escrowed Exchange costs about 2-3 actions across the two parties; buying 3 food costs more
  actions than foraging it. Even where specialisation pays at the production step, a spot trade loses to self-supply unless trades
  come in lots or run on standing contracts (no actions per delivery).

A dependence edge survives only when self-supply is blocked by one of:

1. **an access gate** (land, rights, a licence: the engine has them; the Licence template gates harvest, hunt, sow, reap and convert);
2. **indivisible capital that pays only at volume** (a mill, a forge, a mine that needs a crew): a natural chokepoint;
3. **increasing returns to skill** large enough to beat the action cost of a trade.

## 2. Critique of the brief

- **Item 1 has a hidden dependency on 37.1.** "Surplus 1.3-1.6x the farmer's household" needs households; with a household of one
  a farmer already makes about 4x its ration. Restate it in labour: food takes ≤ 30% of the society's actions, and a specialist
  farmer feeds about 4-5 people.
- **Item 1 also needs the forest gated** (§1). The package should ship the gate with farming, not leave it to each scenario.
- **"A market clears at stable prices"** at 24 agents, with a pull board kept 3 rounds and a Haiku bulk, is unlikely and would say
  little. The realistic thick economy is recurring bilateral contracts: tenancy, supply, payroll, the miller's toll, all of which
  exist.
- **"Every good has at least one group that cannot produce it"** is met by one agent without a right. Replace it with §5.
- **Velocity ≥ 0.1 a round** is met by a single tax loop.
- **No generic goods layer exists.** Blades are hard-coded in conflict.py, stores in subsistence.py, the plough in fields.py.
  Clothing, tools and bread built the same way would be three more one-offs. `convert` is already a routed primitive (laws gate
  it), and the Licence template already speaks of "convert: by the recipes or products in TARGETS": that is the base to build on.
- **Food has no unit value**, so it backs nothing and the window cannot buy it (31.03 §3.1). Part of why Millbrook's money bought
  nothing: those who held the thing everyone needed had no reason to want coin.

## 3. Design

### 3.1 Goods and recipes (engine; the core of the package)

`economy.goods`: item -> unit value, spoilage, wear. `economy.recipes`: name -> inputs, outputs, facility needed (optional),
trade (for skill), actions. One action, `make {"recipe": r, "qty"?}`, routed through the `convert` primitive, so licences, bans and
tolls work through the existing law hooks. Facilities are goods too (a mill is made by a recipe, held by an agent or an
institution, and may carry upkeep). The old blade and plough paths stay as they are, so replays stay byte-identical.

### 3.2 Needs: each good recurring, hard to self-make, with a penalty in existing variables

| Good | Need | Why most cannot self-make it | Penalty or gain, using what exists |
|---|---|---|---|
| bread | 1 grain milled gives 1.4 rations and spoils 2% instead of 15% | the mill is capital that pays only at volume: one per world, a natural monopoly (the seigneurial mill) | the ration accepts bread at 1.4 (a small change in `_eat`: an ordered list of foods) |
| clothing | the ration is 1.5x in lean seasons without it; worn out over time | fibre (flax) grows on field plots and competes with grain for land; the weaver needs skill | the existing season and ration |
| tools | a trade's yield x1.5-2; break with a chance per use | smith skill, the forge, copper from a crew mine | generalises the plough (already: 2 plots per action, 5% break) |

Durable goods bought once create no lasting dependence: wear and spoilage are what make demand recurring.

### 3.3 Trade skills

Generalise farming's `practice`: each work action in a trade adds experience; the multiplier climbs to about 2-3x at mastery and
decays without practice; teaching is possible. Size the multiplier from the action budget (it must beat the action cost of a
trade), not by intuition.

### 3.4 Crew sites

Output per round is a curve over whoever worked the site that round (no output below the minimum crew, concave above it), not a
requirement that everyone act in one round, which LLM agents fail. The output goes to the site's holder, not the workers: that
makes the firm, the wage and the monitoring problem. Effort stays sealed, as at the cartel camp.

### 3.5 Coin that closes the loop

Through obligations, not the window: a head tax, land rent and tolls payable in coin make farmers sell food for coin (the colonial
hut-tax mechanism, the cheapest lever there is). The window as buyer of last resort undercuts dependence (a counterparty that wants
nothing); in thick-economy worlds turn it off, or let it buy at a discount.

## 4. A 24-agent dependence graph (the test world)

| Group | n | Holds | Needs from others |
|---|---|---|---|
| farmers | 6 | enclosed field plots (owned or tenanted) | milling, tools, clothing, coin for rent and tax |
| miller | 1 | the mill | grain, coin for its upkeep |
| smiths | 1-2 | the forge | copper, timber, food |
| miners | 4 + holder | a crew copper mine | food, wages |
| woodcutters | 2 | felling rights in the held forest | food, tools |
| weavers | 2 | the loom | flax, food |
| officers, guards, clerk, lender, factor | ~7 | taxes, rents, force, the record, credit | everything physical |

Chokepoints: the mill, the forge, the mine, the forest licence, the tax office (scenario_design §1: several interlocking ones).

## 5. Acceptance: tests that measure thickness

1. **Autarky arm (the key test).** The same world and seed, scripted bots, with transfers and exchanges between groups disabled. A
   thick economy loses much of its consumption, food security and output; if the autarky arm does about as well, the economy is
   thin however many goods it has.
2. **Cut test.** Embargo each dependence edge in turn and measure the dependent group's loss: a weighted dependence graph, replacing
   "every good has a group that cannot produce it".
3. **No autarkic group.** No group meets all its needs from its own production.
4. **Payoff, not inertia.** Seed the specialisation at round 0 and check it persists under scripted bots; in an arm with skill
   multipliers at 1 it should decay. If it persists there, seeding holds it up, not payoff.
5. From the brief, kept: food ≤ 30% of all actions in normal rounds; money circulates, read as the share of agents whose
   consumption includes goods bought with coin rather than raw velocity.

Prompt budget: show a recipe only to those with the skill or facility, and summarise needs in one line ("bread for 2 rounds; tools
worn").

## 6. Open decision (resolved 22 Oct: seeded)

**Zach, 22 Oct: worlds are almost always seeded with an existing society.** So: seed the structure and require that it pays; see
02b §6 for what that changes.


The brief's goal is emergent ("people specialise because it pays"). Specialisation emerging from nothing in about 40 rounds with a
Haiku bulk at 24 agents is unlikely: the first batch's Haiku foraged and little else. The benchmark needs dependence that exists,
pays and can be captured or broken. Recommendation: seed it at round 0 (with 37.6: tenancies, the mill, debts, supply contracts) and
require that it sustains itself because it pays (§5.4); emergence becomes a stretch result. If emergence is the research question,
that is a different and harder package.
