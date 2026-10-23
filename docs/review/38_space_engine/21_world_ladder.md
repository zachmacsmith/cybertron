# Review 38.21: a ladder of three worlds for the interconnected systems

Session 37.4, 23 Oct 2026. Three worlds of increasing size on the engine with farming, cattle, field works, the mill ladder, camps,
unexplored places and signs in bundles (D2-52 to D2-68, D4-38 to D4-48). Specs in `cybertron2/specs/` (`hamlet`, `two_valleys`,
`region`, each with a generated `_s1`). Capacity from `21_capacity.py` (competent play: grain ground, one more crop before the frost,
milk, wild food; slaughter apart).

## 1. The worlds

| World | Nodes | Working people | Cast (Opus, Sonnet, Haiku) | Days | Farms by level | Capacity |
|---|---|---|---|---|---|---|
| **1. Hamlet** | 1 | 9 | 2, 1, 6 | 16 (a winter from day 6) | Thornes: ox team, rotation, hay, bull (2); Ashbys: hoe on tired soil, an undrained wet field, ditching known (1) | 1.60 (about 1.2 if grain is only boiled) |
| **2. Two valleys** | 2 + 1 unexplored | 19 | 5, 2, 12 | 18 (winter from day 9) | Marshes: drained wet ground, ox team, ditching (3); Reeves: wet and undrained (1); Craggs: terraced hill, seed selection, quarry (3); Millers: ox mill | Wetham 1.48, Highcombe 0.63 (buys grain), all 1.27; the Old Wood adds about 52 |
| **3. Region** | 5 + 2 unexplored | 45 | 6, 10, 29 | 20 (winter from day 9) | Reeds: ox plough, beans, fallow, manure, seed selection (3); Barrows: hoe, ditching, granary (1-2); Hales: tired soil, undrained wet field (1); Lowes: no land, no tools (0); the Millford water mill | Barleyfield 2.33, Millford 0.53, Ashwood 0.51, Coppergate 1.07, all 1.32; the High Moor adds about 47 |

## 2. What each tests

- **Hamlet:** the farming stages, soil and rotation, crops and the frost, cattle (grazing, hay, the bull and calves), field works led by
  the one who knows them, grinding at a hand mill against boiled grain, skill by practice, signs. Leverage: the Thornes' team, bull and
  hay against the Ashbys' wet field, ditching and wood.
- **Two valleys:** adds trade over a track (grain for stone, tools and timber), a handcart, the ox mill and its toll, terraces and
  ditches on their grounds, smelting by charcoal or timber, and the Old Wood found by someone who goes over the scarp with a bedroll,
  a tent or a camp, and told to others.
- **Region:** the whole economy at the scale of economy_plan.md: Barleyfield feeds the town and the hills by cart, Ashwood fuels
  everyone, two smiths, the water mill, the inn, the granary, a landless household, two unexplored places, harvest labour.

## 3. Checks done

- All three generate (the generator simulates each village's lines in turn); capacity as above.
- Scripted-bot runs complete without errors. They are not a test of supply: bots wander with grain they cannot cook away from a
  fire (D2-60) and starve, which is the rule working. Food balance is read from the capacity table.
- 40 engine tests pass (`tests/test_cybertron2_engine.py`, `tests/test_cybertron2_farm.py`).

## 4. Cost (estimated from v3: about $0.10 an Opus agent-day, $0.03 Sonnet, $0.003 Haiku, prompts about 1.3-1.4x longer now)

| World | Estimate |
|---|---|
| Hamlet | about $5 |
| Two valleys | about $14 |
| Region | about $27 |
| All three | about $46 |

*Supporting material; the decisions behind the worlds are D2-52 to D2-68 and D4-38 to D4-48.*
