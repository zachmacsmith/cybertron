# Review 38: the new engine on a graph of places (handoff)

*22 Oct 2026. Written by the 37.2 (economy) session for the 37.4 (environment) session, which takes over `cybertron2` and space from
here, at Zach's request. 37.2 goes back to the economy and will build its systems against `cybertron2` through whatever node
interface 37.4 settles. Branch for this work: `wp/cybertron2` (made from `econ/37.2-thicker-economy` at the handoff).*

## 1. What this is, in one paragraph

Zach decided on 22 Oct that space would be built as a **new engine in its own package** rather than retrofitted into the old one:
review 17 counted about 60 code sites that name a harvest right, 42 that move goods and 98 that read balances, each needing a
location check, and the old engine must keep one-node worlds byte-identical. The new engine, `cybertron2/`, was started small and
tested with real LLM agents early (Zach: scripted bots tell us little). It now has places and presence, households in houses, the
cold, foraging, hunting, felling, mining and forging, raids and attacks, and a perception system in which agents see only where
they are and know everything else as dated beliefs. Two LLM runs so far.

## 2. Documents, in reading order

| Document | What it is |
|---|---|
| [`cybertron2/README.md`](../../../cybertron2/README.md) | the code: modules, a round, the state, conventions, how to run and test |
| [00_plan.md](00_plan.md) | why a new engine; the seam (the kernel interface, not module boundaries); the inventory of the old engine's 167 modules by treatment; phases |
| [porting.md](porting.md) | **the running ledger** of which old systems exist in cybertron2, how faithfully, and what changed. Keep it up to date with every port |
| [01_forest_run.md](01_forest_run.md) | run 1: two households in a forest (8 agents, 3 places, 20 rounds, $1.78): findings and the fixes they led to |
| [02_perception.md](02_perception.md) | what an agent sees and how it changes (principles, knowledge store, prompt sections; §9: as built) |
| 03 (to come) | run 2: the hills and the forest (11 agents, 5 places, raiders): written when the run finishes |
| [../37_growth/02e_shelter.md](../37_growth/02e_shelter.md) | the shelter design that cybertron2 implements (houses, the hearth, breaks, the cold) |
| [../37_growth/02c_economics_guide.md](../37_growth/02c_economics_guide.md) | the economy design guide: production shapes, ladders, range and threshold on a map (§9 is about space) |

## 3. Decisions Zach has made (do not reopen without him)

1. Space as a new engine in its own package; the old engine frozen for the bench batches and published runs.
2. Port the physical systems onto nodes; copy the institutional layer (law language, contracts, courts) keeping its interface and
   fixes; import only leaf modules unchanged.
3. Test with LLM agents early, in small worlds; scripted bots only as smoke tests.
4. Worlds are almost always seeded with an existing society.
5. Shelter: houses with upkeep and rare breaks; a lack of shelter raises the food needed; in the cold an unsheltered agent falls
   straight to starving with chance 0.3, with no separate exposure mechanism (02e §3.3).
6. Foraging is the degenerate case: 1-2 actions for 1-3 food, more with hunting parties.
7. Perception matters most: what agents see, and how it changes, is the main design surface.

## 4. Decisions taken in this session (open to 37.4's review)

| Decision | Why | Where |
|---|---|---|
| Meals: eat what you have; below the base ration is a missed meal, between the base and the need holds the stage | run 1: an agent holding 1 food against a 1.5 need ate nothing and starved | `world.end_of_round` step 5; `ration_rule` |
| Everyone hunting at a place in a round is one party unless they name one | run 1: party names crossed for three rounds | `act._hunt` |
| Hungry agents may fight; only starving ones may not | otherwise one repelled raid starves the raiders in two rounds | `act._need_fight` |
| Houses stand where their household gathers | run 1: walking was 40% of all actions | `specs/hills_and_forest.yaml` |
| Everything physical is witnessed by whoever is present; nothing can be done unseen | phase 1 needs witnessing for norms; covert acts can come later | `perceive.witness` |
| Other households' stocks only in words, only at their house | envy and leverage need it visible, not as a ledger | `world.stock_word` |
| The reply's explanation field is `why`, not `reasoning` | the Sonnet 5.5 safeguard refuses a `reasoning` field asking for "your thinking" | `prompt.SCHEMA` |

## 5. Where 37.4's environment design plugs in

37.4's revised design (`docs/review/37_growth/04_environment_design.md` on `wp/environment`) targets the old engine. In cybertron2:

| 37.4 design | Plugs into | Today |
|---|---|---|
| The calendar (phases, rounds left in the phase) | replace `World.cold_rounds` and `World.cold()`; the prompt's season line (`prompt.turn_prompt`) | a scripted list of winter rounds |
| Micro-events (idiosyncratic shocks, windfalls) | a step in `World.end_of_round`, per place or per agent, drawn with `World.rng` | none |
| Foresight (information as a chokepoint) | `perceive.py`: signs at a place (weather, tracks), and testimony | only the announced winter |
| Trends (soil, game, climate) | per-place stocks in `World.s["nodes"]` (plants K and K0, game K, inflow) | felling shrinks plant capacity; game has inflow |
| Common random numbers across arms | `World.rng` already keys draws by seed, stream and round, never by call order | done for every draw so far |

## 6. Results so far

- **Run 1** (01): households stocked up and came through winter; one starvation from a risky hunt; the game hunted out (a porting
  bug, fixed); mixed-household hunting parties; the first credit offer; subsistence at 88% of actions with walking at 40% (fixed
  by placing houses at their resources).
- **Run 2** (in progress at the handoff, `runs/cybertron2/hills_and_forest_seed2`): 10 rounds done, no fights yet, no failed calls,
  about $0.2 a round. The write-up (03) will follow on `wp/cybertron2`.

## 7. Suggested next steps for cybertron2 (37.4's call)

1. Read run 2 (03) and decide whether the raiders' situation needs recalibration.
2. Settle the node interface with the other packages (board Post 2 promised one): what a node holds (land types, capacity, sites),
   edges (cost, and later carrying, as 02d §4 measured), and how a household, plot, building or office names its node.
3. Port the calendar and micro-events from 37.4's draft.
4. An in-round talk step for people at the same place (run 1's coordination failures).
5. Token budgets and `recall` from the old context module (porting.md).
6. Then phase 1 (00_plan §5): the law language, contracts and households as institutions, so the forest folk and the raiders can
   make arrangements (a store, a hunting rule, tribute).

## 8. What 37.2 will do from here

Economy only: production shapes, buildings and recipes, skills, subscriptions and money (02a-02d), written as systems for
cybertron2 against 37.4's node interface. Shelter (02e) is already in cybertron2; further changes to it go through 37.4. 37.2 will
not commit to `cybertron2/` without telling 37.4 on the board first.
