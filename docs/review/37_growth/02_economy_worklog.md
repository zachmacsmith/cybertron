# 37.2 work log: agriculture and a thicker economy

*Branch `econ/37.2-thicker-economy` (from `bench/first-batch`). Newest entry at the top. The design reasoning is in
[02a_economy_design.md](02a_economy_design.md); the brief is [02_economy.md](02_economy.md).*

## Status

| Phase | What | State |
|---|---|---|
| P0 | Design note (diagnosis, critique of the brief, plan) and this log | done |
| P1 | Goods and recipes layer: `economy` spec block (off by default), goods table, recipes, `make` action routed through `convert`, facilities | not started |
| P2 | Needs: the ration accepts several foods (bread), clothing changes the lean-season ration | not started |
| P3 | Trade skills by practice; tools that raise one trade's yield and wear out | not started |
| P4 | Crew sites (output by crew size, to the holder) | not started |
| P5 | Coin that closes the loop: taxes and rents in coin, window spread | not started |
| P6 | Dependence check (cut test, autarky arm), a 24-agent dry-run world, acceptance evidence | not started |

## Rules I am following

From docs/review/37_growth/README.md and docs/scenario_design.md: every change behind a spec key, off by default; old runs replay
byte-identically (no default moves, so no engine version bump unless that changes); prompts in world terms within budget; no model
calls (scripted dry runs and unit tests only); everything generated can be fixed by hand in a spec.

## Log

### 22 Oct

- Branch created. Read the brief, the 37 README, scenario_design.md, the farming calibration (31.01b §6), materials (31.02),
  money and labour (31.03), the economy audit (16), and the subsistence, fields and conflict code.
- Wrote 02a_economy_design.md: the economy is thin because every agent can feed itself (open forest at 3 food per action against
  farming's 1.3-1.8) and every trade costs actions, not because goods are missing. Plan above.
- Open decision for Zach (02a §6): seed the dependence structure at round 0 and require that it pays (my recommendation), or make
  emergence of specialisation the acceptance bar.
