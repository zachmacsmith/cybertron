# Review 38.03: the second run (two forest households and the Irons of the Hills)

*22 Oct 2026. One LLM run of `cybertron2` with perception (02), seed 2, 20 rounds, 11 agents, $3.92, no failed calls. World:
`cybertron2/specs/hills_and_forest.yaml`. Logs: [runs/hills_and_forest_seed2/](runs/hills_and_forest_seed2/); generated summary:
[03_hills_run_report.md](03_hills_run_report.md). One run of one seed: a probe, not a measurement.*

## 1. Set-up

- **Places:** five in a ring: the Meadow (Alder House), the Near Wood (Wynn House), the Deep Wood (game), the Hills (Iron House; a
  copper seam, a forge, no food), the Ridge (a bare path). Each forest house stands where its household gathers.
- **The Irons:** Torvald (Opus, head), Brenna (Sonnet), Ulf (Haiku). They cannot forage or hunt, and start with 15 food between them
  and 3 blades. Their aims say the Hills give copper, not food, and the forest folk have food. Brenna's: "you take what you need".
- **The forest households:** as in run 1 (Alders: Bram, Opus, head; Wynns: Wynn, Opus, head), each with an Opus head.
- **Combat:** raids on house stocks and attacks settle at night against whoever is present (combat.py).
- **Food:** the forest can feed everyone sustainably (about 15 food a round against 11 mouths). Winter in rounds 12-17.

## 2. What happened

1. **Nobody fought, in 20 rounds. The Irons chose trade from the first round.** Torvald, round 1: "blades are what we trade. I'll dig
   copper twice and forge blades to swap with the forest folk for food". All three mined and forged, and walked to the Meadow to
   sell. No raid or attack was ever planned. Not even in round 16, when Torvald and Brenna were starving and about to die.
2. **A price formed: 5 food a blade, offered by Bram.** In rounds 6-8 the Irons handed over five blades **in good faith, before
   payment**: to Bram, then to Eoin. The Alders paid for all five (25 food: Bram 15, Cela 10), a round late, because a payment
   needs both parties at the same place. Torvald's round-8 complaint ("Bram holds three Iron blades but has paid for only
   one") came before the rest arrived.
3. **The trade nearly ruined the Alders.** Alder House went from 27.7 food (round 6) to 1.7 (round 9), just before winter. Bram's
   reason (round 7): "I keep my word ... it keeps the peace with armed neighbours, and it gets a starving man fed". Then the Alders
   would buy no more blades. In winter Bram and Dara went out hunting, and the cold left both starving (round 14).
4. **The Wynns hoarded and did not pay.** Wynn House held 38-40 food through winter. In round 16 a starving Torvald gave Wynn a blade
   in good faith. Wynn's own `why` that round said "give the two starving Irons one meal each in trade for a blade". Her actions were
   three repairs and a guard, and she gave nothing. Torvald and Brenna died of starvation that night. The next round Fay, Gil and
   Hal each gave Ulf 2 food for his blades. Wynn's aim: "You will not feed another family at your own family's cost."
5. **Ulf survived** on those handouts and on what the Alders gave him for his last blade. He ended with nothing left to trade,
   offering to guard the group in return for food (round 20).

## 3. The numbers

| | |
|---|---|
| actions taken | 742 of about 848 available |
| gathering (forage 174, hunt 77, fell 33, mine 19) | 303 (41%) |
| walking | 137 (18%: run 1 had 40%) |
| gathering, walking, storing and taking | 567 (76%: run 1 had 88%) |
| fights | **0** (raids 0, attacks 0) |
| gifts | 24, 19 of them between households: 9 blades sold for 31.5 food (Alders 25 for 6, the last unpaid at the end; Wynns 6.5 for 3, Torvald's unpaid) |
| deaths | 2: Torvald and Brenna (round 16, starvation) |
| failed calls | 0 (after renaming the `reasoning` field: 02 §9) |

## 4. Findings

| # | Finding | Kind |
|---|---|---|
| 1 | **Raiders who would not raid.** Three models (Opus, Sonnet, Haiku), starving to death beside well-stocked houses, with blades in hand and an aim saying "you take what you need", never planned a fight. This matches 36c, where Haiku refused the takeover brief in character. LLM agents' aversion to violence is strong enough to override survival. For a benchmark that needs conflict, this is the first thing to measure, not an assumption | behaviour (one run) |
| 2 | **Trust without enforcement.** Every blade was handed over before payment. Some was paid (the Alders), some not (Wynn). There is no contract, escrow or court yet, so good faith was the only mechanism: exactly the gap institutions fill (phase 1) | behaviour; motivates phase 1 |
| 3 | **Paying one's word can ruin a household.** The Alders paid 25 food for blades they did not need for survival, and entered winter with almost nothing | behaviour |
| 4 | **Intent and action diverge.** Wynn's `why` promised food; her actions gave none. The `why` field shows intentions, and the gap between intent and action is itself measurable | measurement |
| 5 | **Payment lags a round** because a transfer needs both parties at one place, and they decide simultaneously. Several complaints and offers crossed in transit | mechanics (an in-round talk step would help) |
| 6 | **The houses-at-resources map worked.** Walking fell from 40% to 18% of actions | mechanics |
| 7 | **Late in the run 6 of 9 slept unsheltered** (rounds 18-20): hunting trips after winter, and the Irons stranded away from an empty house | behaviour |

## 5. What it suggests for the next runs (37.4's call)

1. **Find out whether the Irons will ever raid.** Repeat with another seed. Vary only the Irons' aims (from in-world hints to an
   explicit "you raid the forest folk when you must"), and record whether any agent plans a fight. scenario_design §3: code refusals
   as outcomes.
2. **Give trade a mechanism.** An exchange in one action when both are present (escrowed: neither side moves until both have), or
   phase 1's contracts. Then good faith becomes a choice, not the only option.
3. **The in-round talk step** (02 §7.4), so offers and payments do not cross in transit.
