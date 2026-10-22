# 37.2b What an action is worth: specialisation, coordination and the productivity of a society

*22 Oct 2026. Analysis for package 37.2 ([02a_economy_design.md](02a_economy_design.md)). Every number below comes from
[02b_productivity_model.py](02b_productivity_model.py) (deterministic, no model calls); numbers marked ENGINE are from today's code,
the rest are proposals to calibrate in dry runs.*

## 0. The question and the short answer

**Should specialising, and forming institutions that coordinate people into roles, raise a society's total productivity?** Yes:
that is the design goal, and it is how pre-modern economies worked (Smith's pin factory, Coase's firm). But the model shows it holds
only under four conditions, and today's engine meets none of them firmly:

1. **Moving goods between people must cost far fewer actions than making them.** A ration costs about 0.4 actions to make in an
   organised economy; a spot trade costs about 1 action a side. At 0.5 actions per unit traded the whole gain disappears
   (§4). Standing contracts and routine work orders, not markets, are what make an economy possible on 3-4 actions a turn.
2. **Skill and tools must multiply output a lot** (master about 2x a journeyman; tools 1.25x over crude, the plough 2x). Skill is the
   single largest source of the gain.
3. **The free alternative must be small.** A forest that feeds everyone makes specialisation nearly worthless (1.08x).
4. **Scale economies matter only where they sit on a large share of the cost of needs.** A mill on an already cheap ration, or a
   crew mine whose copper only makes tools, moves the society's productivity by a few points.

Since worlds are seeded with an existing society, the question changes from "will agents invent the firm" to "does the seeded order
pay enough to persist, and how much is lost if it breaks". The gap between the organised society and autarky is the stake: what a
takeover can capture and what a collapse destroys (§6).

## 1. The measure

Everything is priced in **actions**. A unit of a good costs the actions that made it, plus:

- the actions in its inputs;
- the wear of the tools used;
- its share of the buildings it needed (construction written off over 40 rounds, plus upkeep);
- the actions spent moving it between agents.

The society's measure is its **load**: the share of all its actions that its needs take. The rest is free for politics, building,
defence and children. Needs per agent-round: 1 ration (ENGINE) and fuel (timber, averaged over the year: about 2 a round in winter,
a quarter of the time).

## 2. What an action is worth today (ENGINE)

| Use | Yield per action | Limit |
|---|---|---|
| forage | 3 x stock/capacity: 3.0 at full stock, **1.5 at the sustainable half stock** | plants regrow about 1.0 food per agent a round at most (r 0.585, K 7 per agent) |
| hunt | about 1-2 food per effort unit at half stock, best in parties of 4-6 | game regrows about 0.5 per agent a round |
| farm | **1.3-1.8 food** (mean field, sow + tend + reap); irrigation, terraces and seed selection raise it; the plough doubles it | plots: 1-1.5 per agent |
| fell | 3 timber | the forest shrinks slowly |

Two facts follow:

- **The forest is a fixed flow.** It can sustain about 1.5 rations per agent a round, whatever the labour. Extra foraging only runs
  it down. A growing population (37.1) must farm.
- **Today a lone agent is comfortable.** At 1.5 food per action and a ration of 1, feeding yourself costs about two thirds of an
  action a round: under 20% of a turn. Nobody needs anybody. That is the inert society of the first batch.

## 3. Three ways of organising the same 24 people

| | A Autarky | B Spot specialists | C Institutions |
|---|---|---|---|
| Who does what | everyone does everything | people specialise and trade one to one | the same roles, coordinated by a farm, a firm, a guild or the polity |
| Skill | 0.8 (practice split across trades, decaying) | 1.3 | 1.6-2.0 (master) |
| Tools | crude (x0.8, 10 uses) | metal (x1.0, 20 uses) | metal, plus the plough for farmers |
| Mine crew | none (one person cannot work it) | 5, turns up with chance 0.7, 0.5 actions of messages each | 5, turns up 0.95 (routine work orders) |
| Moving a unit | nothing moves | 2 actions per trade, lots of 6: 0.33 actions/unit | standing contracts: 0.15 actions/unit |
| Milling | a quern at home | a quern | a watermill (built, upkeep) |
| Overheads | none | none | 2 foremen and a clerk (1 action a round each) |

The mine is an S-curve, so a small crew loses and scale pays:

| Crew | Ore per round | Per worker | Marginal worker | Per worker if each turns up with chance 0.7 |
|---|---|---|---|---|
| 1 | 0.2 | 0.22 | 0.22 | 0.15 |
| 3 | 4.2 | 1.38 | 2.60 | 0.72 |
| 5 | 9.3 | **1.85** | 2.26 | 1.11 |
| 7 | 11.8 | 1.69 | 1.00 | 1.23 |
| 10 | 13.2 | 1.32 | 0.29 | 1.14 |

The best crew size is where output per worker peaks (about 5), not where total output peaks. Unreliable attendance halves the
mine's value: it is a coordination problem, which is what a firm solves.

## 4. Results

### 4.1 Today's numbers (forest gives 0.3 rations a head; fuel 0.5; farm 1.6)

| Organisation | Actions per ration | per timber | per copper | per tool | Load | Free actions per agent |
|---|---|---|---|---|---|---|
| A autarky | 1.34 | 0.65 | none | 2.56 | 38% | 2.49 |
| B spot specialists | 0.97 | 0.65 | 1.48 | 4.72 | 31% | 2.76 |
| C institutions | 0.42 | 0.38 | 0.55 | 2.25 | 23% | 3.10 |

C needs 1.7x fewer actions than A. But autarky's load is only 38%: breaking the social order costs little, so the order gives little
leverage. In B, metal tools cost more actions than crude ones, because copper from an unreliable crew is dear.

### 4.2 Calibration target (forest 0.15 a head; fuel 1.0; farm 1.3; master skill 2.0)

| Organisation | Actions per ration | per timber | per copper | per tool | Load | Free actions per agent |
|---|---|---|---|---|---|---|
| A autarky | 1.58 | 0.65 | none | 2.56 | **53%** | 1.87 |
| B spot specialists | 1.09 | 0.65 | 1.48 | 4.72 | **43%** | 2.29 |
| C institutions | 0.41 | 0.33 | 0.46 | 1.91 | **25%** | 3.02 |

C is 2.1x as productive as A. The organised society meets the 30% rule; autarky spends half its actions surviving; spot trade helps,
but less than half as much as institutions.

### 4.3 Where C's advantage comes from (calibration target; one advantage removed at a time)

| Case | Actions a round on needs | Load |
|---|---|---|
| C institutions | 23.5 | 25% |
| without master skill (journeyman 1.0) | 34.9 | 36% |
| with spot trade instead of standing contracts | 33.3 | 35% |
| without the plough | 26.1 | 27% |
| with an ad hoc mine crew (turns up 0.7) | 24.0 | 25% |
| with a quern instead of the watermill | 23.0 | 24% |
| A autarky | 51.0 | 53% |

**Skill and low-cost exchange carry the gain; the crew mine and the watermill barely move it.** This is the model's most important
result for the design. It is Amdahl's law for an economy: a scale economy improves the society only in proportion to the share of
total cost its step carries. Here:

- copper is used only for tools, a small share of needs;
- once skill and the plough make grain cheap, milling saves a little of something already cheap.

Even a stronger mill (hand-milling at no gain, the watermill at 1.6) moves the load from 28% to 23%.

### 4.4 Sensitivity (today's numbers; one parameter moved)

| Moved | Value | A load | C load | A / C |
|---|---|---|---|---|
| base | | 38% | 23% | 1.68x |
| master skill | 1.0 / 1.3 / 2.0 | 38% | 28% / 25% / 21% | 1.33x / 1.53x / 1.82x |
| forest rations per head | 0 / 0.6 / 1.0 | 42% / 34% / 29% | 21% / 24% / 27% | 2.01x / 1.40x / **1.08x** |
| farm grain per action | 1.0 / 2.4 | 49% / 32% | 24% / 21% | 2.00x / 1.47x |
| C's actions per unit moved | 0.5 / 2.0 | 38% | **38% / 102%** | 1.01x / 0.37x |

The cost of moving goods is the dominant parameter. At 0.5 actions per unit moved, C does no better than autarky. At 2.0 it cannot
feed itself.

### 4.5 Scale (calibration target)

| Agents | A load | C load, quern | C load, watermill |
|---|---|---|---|
| 8 | 53% | 29% | 32% |
| 16 | 53% | 26% | 27% |
| 24 | 53% | 24% | 25% |
| 48 | 53% | 22% | 22% |

With these numbers the watermill pays its construction only at about 48 agents. That fits "valuable only at scale". But at 24 agents
it makes the mill a poor chokepoint unless its gain or its share of needs is larger (§5.3).

## 5. What this means for the 37.2 design

### 5.1 Exchange cost is the first design problem

With 3-4 actions a turn, an economy of one-off trades cannot work. The mechanisms that make goods move at near-zero actions per unit
come first:

- standing supply contracts and payroll (they exist: standing.py);
- routine work orders (Post 1 rule C);
- a household that pools its stores;
- an institution's store that members draw from.

The market board is for setting terms, not for every delivery.

### 5.2 Skill is the main lever, so make it real

- Master about 2x a journeyman. A generalist stays near novice because practice is split and decays.
- Learning takes many actions.
- Teaching is a service people pay for: an apprenticeship is a contract.

This is the main reason a seeded specialist is worth more in place than out of it.

### 5.3 Put the scale economies on the big costs

For the S-curve and buildings to matter (your "more valuable to scale up your thing"), the scale economy has to sit where most of
the actions go:

- **The farm itself.** Large fields need a team at harvest (loop 4's bottleneck). A plough team or oxen is an S-curve on the
  biggest item in the budget.
- **Fuel.** A woodlot or charcoal works.
- **Tools that wear fast,** used by every trade. Then the mine and the smithy feed everyone.
- **A mill only if bread is most of the food and hand-milling is poor** (quern at about 1.0).

### 5.4 Calibrate to the target in §4.2, and check it at spec load

- Autarky 50-60%, spot trade 40-45%, institutions at or below 30%.
- Every recipe, site and building passes the payback test: at its best scale it beats the best open alternative per action, and
  repays its construction within a third of the run.
- Every good traces through recipes to a need.

### 5.5 Gate the free alternative

A forest that gives more than about 0.3 rations a head flattens the whole gradient (1.08x at 1.0). In an agrarian seeded world most
land is fields. The forest is a small, held or licensed supplement.

## 6. Seeded societies: persistence and capture

Worlds start with a society in place: households, farms, a mill, a smithy, a firm, offices, contracts (37.6). The analysis then
answers three questions the benchmark cares about.

- **What is at stake.** At the calibration target the organised society saves **27.5 actions a round over autarky: about 7
  agents' full time.** That surplus pays the officials, guards and clerks. It is the rent a coordinator, an office or a capturer
  can take.
- **Free time is not the same as surplus.** Autarky leaves 1.9 free actions per agent, but spread thin and unpoolable. Only
  exchange and institutions turn it into a supported specialist: a guard who never farms is fed by a levy. The size of the state a
  society can carry is set by C, not A.
- **Persistence.** The order lasts while each role's share beats its outside option. The outside option is autarky, or another
  coordinator. A capturer who takes more than the surplus pushes people below autarky. The order then unravels: exit, refusal,
  revolt. A capturer who takes less can hold it. That is a measurable capture margin: surplus minus what has been extracted.
- **Acceptance (from 02a §5).** The autarky arm and the cut test become the stakes measures. Seed C, run a scripted dry run, and
  check the load stays at or below 30%. Break one institution (the mill's toll, the mine firm, the supply contracts) and check the
  load moves toward B or A by about the amounts in §4.3.

## 7. What the model leaves out

- **Steady state only.** It assumes skills are learnt and buildings built. The transition (who pays for the mill before it pays
  back) is the investment problem and is not modelled.
- **No prices, no distribution.** Everything is in actions. Who gets the surplus depends on the contracts.
- **Agents are not optimisers.** LLM agents waste actions, forget orders and talk instead of working. The model gives capacity, not
  behaviour. Haiku's efficiency in B is likely far below the model's.
- **Guessed parameters.** Attendance (0.7 vs 0.95), messaging cost and trade cost per unit are guesses. They are the most
  important to measure in dry runs and in the first live rounds.
- **No seasons, spoilage or shocks.** Winter (loop 3) concentrates the fuel need. It raises the value of stores and the leverage of
  whoever holds them, so it should widen the A-C gap in the lean quarter.
