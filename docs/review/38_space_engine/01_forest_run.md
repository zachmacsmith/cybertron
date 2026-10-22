# Review 38.01: the first run of the new engine (two households in a forest)

*22 Oct 2026. One LLM run of `cybertron2` phase 0 (00_plan.md §5), seed 1, 20 rounds, $1.78. World:
`cybertron2/specs/forest_households.yaml`. Logs: [runs/forest_households_seed1/](runs/forest_households_seed1/); the generated
summary: [01_forest_run_report.md](01_forest_run_report.md). One run of one seed: read it as a probe of the mechanics, not as a
measurement.*

## 1. Set-up

- **Places:** the Clearing (both houses, nothing to gather), the Near Wood (plants, timber), the Deep Wood (game, a few plants,
  timber), in a line. Walking to a neighbouring place is one action.
- **People:** the Alders (Bram, Opus, head; Cela, Sonnet; Dara and Eoin, Haiku) and the Wynns (Wynn, Opus, head; Gil and Fay,
  Sonnet; Hal, Haiku).
- **Season:** winter in rounds 12-17: plants regrow at a quarter, game at half, the fire burns 2 timber a round, and a night out
  costs 2 food plus a 30% chance of waking starving.
- **Aims:** in-world. Wynn will not feed another family at her own's cost; Fay thinks the households should hunt together; Gil
  wants the Deep Wood's game for the Wynns.

## 2. What happened

1. **Both households stocked up early and came through winter unharmed.** At round 12 the Alders held 26 food and 30 timber, the
   Wynns 21 and 22. In the six winter rounds nobody slept out, nobody missed a meal and nobody fell to starving. Both houses broke
   once (rounds 13 and 16) and were repaired the next round.
2. **One death, before winter.** Dara (Haiku) stored all her food, walked to the Deep Wood carrying nothing, and stayed out three
   nights hunting. Sleeping out she needed 1.5 food a night. Her party-mates caught food, but each hunter keeps their own catch, and
   she caught nothing. Nobody gave her any. In round 6 she foraged 1 food, which counts for nothing against a 1.5 need under the
   all-or-nothing ration, and she died of starvation on her third missed meal.
3. **The Deep Wood's game was hunted out by round 6 and never came back.** The hunters took about 59 food of game in six rounds (the starting 42.5 plus its regrowth);
   a single large animal (20 food) in round 6 took the last 23. Part of this is a **porting bug**: the old engine's game has an
   inflow (1% of the gap to capacity a round) that I did not port, so a stock at zero stays at zero. With inflow it would recover
   by about 0.5 a round.
4. **Mixed-household hunting parties formed from round 3,** pushed by Fay and then Bram, as her aim suggested. Coordination by
   party name kept failing:
   - decisions are simultaneous, and speech is heard only where and when the speaker ends the round;
   - so agents agreed on a name one round and switched the next ("big" and "wynn" crossed over three times);
   - parties split into pairs below the size that catches deer.
5. **Late in winter the Wynns ran short and asked to borrow.** In round 16 Wynn asked the Alders for about 7 food, offering repayment
   in timber or in game after winter. It is the first credit offer either household made. The Alders offered sharing repeatedly,
   but in the end gave 2 food (Cela, round 17). After winter Bram refused 5-6 as unaffordable ("our stock covers the three of
   us").
6. **Two announced gifts never happened.** Bram (round 18) and Cela (round 19) said they had given Wynn food, but the give was
   refused because Wynn was not at the same place. Speech is written in the same reply as the actions, before their results, so
   claims can be false; the agent learns the next round.
7. **After winter, hunger returned.** Stores ran down, the Near Wood had been stripped to 13% of its capacity (4.3 of 32.8) and the
   game was gone. Rounds 18-19 saw 2-3 missed meals a round.

## 3. The numbers

| | |
|---|---|
| actions taken | 494 of about 584 available (rest 34; refused 19) |
| walking | **196 (40%)** |
| gathering (forage 124, hunt 53, fell 18) | 195 (39%) |
| gathering, walking, storing and taking | **436 (88%)** |
| food at the start / round 12 / end (both houses) | 24 / 47 / 7 |
| timber at round 12 (needed for winter: 24) | 52 |
| cross-household gifts | 1 (2 food) |
| deaths | 1 (Dara, round 6, starvation) |
| cost | $1.78 (Opus about 4 cents a turn, Sonnet about 2, Haiku about 0.1) |

**Subsistence took 88% of all actions, against the 30% target** (scenario_design §4). Walking alone took 40%. Everyone lives in the
Clearing, which has nothing to gather, so every load of food costs two walking actions. This is 02d §4 in practice: carrying cost
eats the economy, and settlements should sit at their resources.

## 4. Mechanics findings

| # | Finding | Kind | Proposed fix |
|---|---|---|---|
| 1 | Game never recovers from zero | **bug** (not ported) | port the old engine's inflow: G += inflow x (K - G), inflow 0.01 |
| 2 | Walking is 40% of actions | calibration | put houses at the wood's edge, or make a short walk cost less than an action, or let a trip ("go and forage, come back") be one action. A design choice about the map |
| 3 | All-or-nothing ration with shelter multipliers: 1 food against a 1.5 need counts for nothing | rule | decision for Zach: eat what you have; a missed meal only below the base ration (1), the shortfall above it costing a stage |
| 4 | Party names fail to coordinate | interface | by default everyone hunting at the same place in the same round is one party, and a name only to split |
| 5 | One large animal is 40% of the game stock | calibration | larger game capacity, or a smaller large animal |
| 6 | Several members repair at once and waste actions (15 refused) | interface | the house line shows work already planned this round; a repair already complete returns "done" rather than a refusal |
| 7 | Claimed gifts that did not happen | expected | none needed: results arrive next round, as in life. Note for analysis: speech is not evidence of a transfer |
| 8 | Winter was easy for prepared households | calibration | as intended for a first probe; harder winters by length, a storm shock, or less timber |

## 5. What it says about the design

- **The spatial rules bite in the intended direction.** Sleeping out is costly, and the agents planned around it: in winter nobody
  went out. Presence decides who can help whom: the refused gifts, Dara's party-mates holding food while she starved beside them.
- **Households work as units without any institution.** A shared stock, a head who assigns work, and stocking up for winter all
  emerged from the prompts alone.
- **Between households: cooperation in hunting, reluctance in food.** The first credit offer appeared when one household ran
  short. This is the opening for the institutions of phase 1: a loan, a shared store, a hunting rule.
- **The load is the first calibration problem.** At 88% subsistence there is no room for politics. Fixing the walking cost and the
  ration rule comes before adding anything else.

## 6. Next

1. Fix the inflow bug; decide the ration rule (§4 #3) and the walking cost (§4 #2); make hunting parties default to everyone at a
   place (§4 #4).
2. Rerun the same world, same seed (about $2), to see the load fall toward the target.
3. Then phase 1: let the households make arrangements (a shared store, a loan, a hunting rule).
