# Porting ledger: cybertron 1 -> cybertron2

*A running record of which systems of the old engine (`cybertron/`) exist in the new one (`cybertron2/`), how faithfully, and what
changed. Update it in the same commit as any port. Plan and inventory: [00_plan.md](00_plan.md). Last updated 22 Oct 2026 (commit
after 946c0c7).*

Fidelity: **unchanged** (imported or copied as is), **ported** (same mechanism and formulas, adapted to places), **simplified**
(the core kept, parts dropped: listed), **replaced** (a different mechanism doing the same job), **new** (no cybertron 1
counterpart), **not yet**, **left behind** (not planned).

## Ported or replaced

| System (cybertron 1) | Fidelity | cybertron2 | What changed |
|---|---|---|---|
| LLM backend (`llm.py`: `claude -p` and API calls, JSON parsing, retries, usage) | unchanged (imported) | `run.decide` calls `cybertron.llm.call` | nothing; cybertron2 reads its failed-call placeholder (`_error`) |
| Seeded random streams (`random.Random(f"{seed}|stream|...")`) | ported | `world.World.rng` | same convention |
| Forest plants: logistic regrowth, forage yield = yield x S/K, refuge (`camptypes/forest.py`) | ported | `world.end_of_round` step 3, `act._forage` | one stock per place, not per forest camp; capacity set per place in the spec |
| Game: logistic regrowth plus inflow (`subsistence._ecology`) | simplified | `world.end_of_round` step 3 | no Allee threshold, theta fixed at 1, inflow per place (added in run 2) |
| The individual hunt (`camptypes/forest.py`, engine 14: draws per effort unit, large/medium/small odds, crowding, hunger) | ported | `world._hunts` | everyone hunting at a place is one party unless they name one (run 1 showed names failing to coordinate) |
| Felling (fell_timber, plant capacity lost per fell, floor) | ported | `act._fell` | none |
| Hunger stages, missed meals, frailty, starvation hazard (`subsistence.py`) | ported | `world.end_of_round` steps 5-6 | ration rule `partial` by default (eat what you have; at least the base ration holds the stage); the old all-or-nothing rule is `ration_rule: all_or_nothing` |
| Action limits by hunger (hungry one fewer, starving at most 2) | ported | `world.actions_for` | none |
| Yield by hunger (x0.75 hungry, x0.5 starving) | ported | `physics.hunger_yield` | none |
| Spoilage of carried and stored food | ported | `world.end_of_round` step 8 | the store's 2% becomes the house stock's 5% |
| Food stores (S3: build, deposit, withdraw) | replaced | house stock (`store`, `take`) | every house has a stock; no separate store buildings yet |
| Seasons (lean, normal, plentiful) | replaced | `cold_rounds` (winter) | scripted winter until 37.4's calendar; no lean or plentiful draws |
| Harm combat model (`conflict.py`, docs/review/21_combat.md) | simplified | `combat.py`, `act._attack`, `act._raid`, `act._guard` | kept: per-agent bases x hunger, weapon quality, p_kill = P^2/(P^2+X^2) and p_wound with X = 2(D+1), weapons used up, food cost, settled at night. Dropped: forts, watch and first strike (guard stands in for watch and bodyguards), dying blow, initiative, assassin, accidents, lawful force and arrest, spoils rules (attackers take what the victim carried). New: raids on house stocks. Changed: hungry agents may fight (only starving ones may not) |
| Forge (copper + timber -> blade) | ported | `act._forge` | a blade costs 6 copper and 1 timber (was 25 and 1), and needs a forge at the place |
| Craft (crude weapon) | simplified | `act._craft` | from timber only (was timber or stone) |
| Mining (copper camps) | replaced | `act._mine` at a place with a copper seam | a fixed yield per dig instead of the cartel camp's game |
| Death and estates (`mortality.py`) | simplified | `world.die` | what the dead carried goes to their house stock, or to their killers; no bequests, probate or offices |
| Context: history mode's memory gradient (`memory.py`, review 20 §4) | simplified | `perceive.close_round`, `prompt.turn_prompt` | full band of 2 rounds, summary band of 8, lasting memories of salient events (at most 14); no conversations or chunks, a fresh call each round |
| Context: the reply's reasoning field | replaced | `why` in the reply schema | renamed: a `reasoning` field asking for "your thinking" is refused by the Sonnet 5.5 safeguard |
| Context: scratchpad | replaced | `note` in the reply, shown every round | one free note, no files or pins |
| Visibility (`Kernel.can_see`: audiences per event type) | replaced | `perceive.py`: presence decides | an act is seen by whoever is at the place at that step; see 02_perception.md |
| DMs, posts, channels | replaced | `say` (heard at your place) and `tell` (one person at your place), free, 3 a round | no global messages, no in-round talk step, no channels or papers |

## New in cybertron2

| System | Where | Design |
|---|---|---|
| Places, edges, presence, travel | `world.py`, `act._travel` | 00_plan.md, review 17 |
| Houses, shelter multipliers, the hearth, breaks and repair | `world.py`, `act._repair` | 37_growth/02e_shelter.md |
| The cold: a night out may leave you starving (30%) | `world.end_of_round` step 7 | 02e §3.3 |
| Knowledge store, witnessing, beliefs with ages, visible condition and load | `perceive.py`, `prompt.py` | 02_perception.md |
| Households that cannot gather (`cannot`) | `world.py`, `act._gather` | 03 (the hills world) |

## Not yet ported (in the order they are likely to be needed)

| System | Why it is needed next |
|---|---|
| Law language, laws and the library (`lawlang`, `library`, `dispatch`) | institutions in phase 1: a shared store, a hunting rule, a tribute |
| Contracts and standing contracts (`contracts`, `standing`) | subscriptions and recurring deliveries (02c §7), tribute as a contract |
| Institutions, offices, positions (`institutions`, `positions`) | a head who assigns work; a keeper of a store |
| Context budgets with deterministic trimming, look-ups, `recall` (`context.py`) | larger worlds; today sections are capped by line counts |
| Life: births, children, lineages (`life`, `pairs`; 37.1's households) | growth (37.1) |
| Fields and farming (`camptypes/fields.py`) | the agrarian economy (37.2) |
| Goals and scoring (`goals`, `goal_registry`, `scorer`) | benchmark arms |
| Export, analysis, replay versioning | phase 3 |

## Left behind

The dial camps and their modifiers, leases, media2 and Scholars, hidden caps, roles (Board, Fixer), the observer, the old outside
power, tiers, regimes, difftest and armdiff (00_plan.md §3).
