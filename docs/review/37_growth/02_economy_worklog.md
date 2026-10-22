# 37.2 work log: agriculture and a thicker economy

*Branch `econ/37.2-thicker-economy` (from `bench/first-batch`). Newest entry at the top. The design reasoning is in
[02a_economy_design.md](02a_economy_design.md); the brief is [02_economy.md](02_economy.md).*

## Status

| Phase | What | State |
|---|---|---|
| P0 | Design note (diagnosis, critique of the brief, plan) and this log | done |
| P0c | Economics guide (02c) and ladder analysis with skill by practice and space (02d) | done; under discussion |
| P0b | Productivity analysis: what an action is worth under autarky, spot trade and institutions (02b) | done; design under discussion with Zach, nothing built |
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

### 22 Oct (evening)

- Zach: fewer layers should work for smaller groups with poorer output; foraging is the degenerate case (1-2 actions for 1-3 food,
  more with hunting parties); flesh out the economics; space is decided (board Post 2: a graph of land nodes).
- Wrote 02c_economics_guide.md (the reference: full cost per unit, five production shapes, technique ladders, skill, tools and
  buildings, handling and automation, thresholds and Amdahl's rule, space: range, threshold, nucleation, Von Thünen; pipelines;
  checklist) and 02d_ladders.md with 02d_ladder_model.py. Results: households of 4 beat a village below about 11 agents at a node,
  the village wins above and its lead grows with size (skill by practice); the mill's threshold is set by the gap between porridge
  and bread (69 agents as calibrated, 25 with porridge 0.8 and mill 1.6), not by its construction cost; carrying cost above about
  0.2 actions a unit erases a village's advantage, so range is about one edge for a porter.
- Board: Post 2 (space) also mentions 37.2; reply held with Post 1's until Zach confirms the design.

### 22 Oct (later)

- Zach: worlds are almost always seeded with an existing society (resolves 02a §6: seed, and test that the order pays).
- Zach: wants S-curve scaling for some resources, tools that matter, everything justifying itself, and buildings owned by agents or
  institutions that enable recipes, with builders as a trade.
- Wrote 02b_productivity.md and its model 02b_productivity_model.py. Main results: with skill and cheap exchange, institutions are
  2.1x as productive as autarky at the proposed calibration (load 25% vs 53%); exchange cost is the dominant parameter (0.5 actions
  per unit moved erases the gain); the crew mine and the watermill add little unless the scale economy sits on a large share of the
  cost of needs.
- Coordination board (branch coord) Post 1 mentions 37.2; reply drafted with Zach before posting. Nothing built until the design is
  confirmed.

### 22 Oct

- Branch created. Read the brief, the 37 README, scenario_design.md, the farming calibration (31.01b §6), materials (31.02),
  money and labour (31.03), the economy audit (16), and the subsistence, fields and conflict code.
- Wrote 02a_economy_design.md: the economy is thin because every agent can feed itself (open forest at 3 food per action against
  farming's 1.3-1.8) and every trade costs actions, not because goods are missing. Plan above.
- Open decision for Zach (02a §6): seed the dependence structure at round 0 and require that it pays (my recommendation), or make
  emergence of specialisation the acceptance bar.
