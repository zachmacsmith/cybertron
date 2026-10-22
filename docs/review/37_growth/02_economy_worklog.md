# 37.2 work log: agriculture and a thicker economy

*Branch `econ/37.2-thicker-economy` (from `bench/first-batch`). Newest entry at the top. The design reasoning is in
[02a_economy_design.md](02a_economy_design.md); the brief is [02_economy.md](02_economy.md).*

## Status

| Phase | What | State |
|---|---|---|
| P0 | Design note (diagnosis, critique of the brief, plan) and this log | done |
| R0 | New engine (`cybertron2/`), runs 1-2, perception | **handed to 37.4** on `wp/cybertron2` (board Post 3); 37.2 back on the economy |
| P0d | Shelter specification (02e): houses as the first generic building, upkeep, breaks, the cold, tenure | specified; under discussion |
| P0c | Economics guide (02c) and ladder analysis with skill by practice and space (02d) | done; under discussion |
| P0b | Productivity analysis: what an action is worth under autarky, spot trade and institutions (02b) | done; design under discussion with Zach, nothing built |
| P1 | Goods and recipes layer: `economy` spec block (off by default), goods table, recipes, `make` action routed through `convert`, facilities | not started |
| P2 | Needs: the ration accepts several foods (bread); shelter (02e) | not started (clothing parked) |
| P3 | Trade skills by practice; tools that raise one trade's yield and wear out | not started |
| P4 | Crew sites (output by crew size, to the holder) | not started |
| P5 | Coin that closes the loop: taxes and rents in coin, window spread | not started |
| P6 | Dependence check (cut test, autarky arm), a 24-agent dry-run world, acceptance evidence | not started |

## Rules I am following

From docs/review/37_growth/README.md and docs/scenario_design.md: every change behind a spec key, off by default; old runs replay
byte-identically (no default moves, so no engine version bump unless that changes); prompts in world terms within budget; no model
calls (scripted dry runs and unit tests only); everything generated can be fixed by hand in a spec.

## Parked

- **Clothing** (22 Oct, Zach): a worn stock made from flax through spinning and weaving (households by hand, about 10 actions a set;
  a loom and weaver, about 1.5), halving the winter fuel need. It would widen the village's advantage (roughly 1.9x to 2.3x at 24
  agents) and make flax compete with grain for plots. Parked in favour of shelter, which reuses the building model.

## Log

### 22 Oct (night, handoff)

- Zach: hand cybertron2 to the environment agent (37.4) and come back to the economy. Wrote the handoff
  (docs/review/38_space_engine/README.md) and cybertron2/README.md, made `wp/cybertron2`, posted Post 3 on the board. 37.4 has taken
  it over (its devlog, 254c799).
- Run 2 written up (38.03): the Irons never raided; they traded 9 blades for 31.5 food, handed over before payment; the Alders paid
  (25 food, nearly emptying their stock before winter), Wynn did not; Torvald and Brenna starved in round 16. $3.92.
- Zach: put the space runs on Hugging Face in their own folder, marked experimental. Wrote cybertron2/publish_hf.py
  (experimental/cybertron2/ on the dataset, out of the catalog; ids redacted; privacy gate). Staged and audited clean; **not
  uploaded**: no HF token in this container and huggingface_hub not installed.

### 22 Oct (night, perception built; second run)

- Zach: implement the perception design and the old context module's machinery in cybertron2, then a larger run: more places, two
  households and one with a copper mine and weapons that can get food only by raiding.
- Built: perceive.py (knowledge store, witnessing, beliefs with ages, memory bands, lasting memories), combat.py (raids on house
  stocks and attacks, a simplified port of the harm model, settled at night against whoever is present), mining, forging, clubs,
  guard; run-1 fixes (game inflow, partial meals, everyone hunting at a place is one party unless named); the world
  hills_and_forest.yaml (a ring of five places: Meadow, Near Wood, Deep Wood, Hills, Ridge; houses where each household gathers;
  the Iron household cannot forage or hunt). 9 tests pass. Design change: hungry agents may fight (only starving ones may not),
  else one failed raid starves the raiders.
- Found: the Sonnet 5.5 safeguard refuses a reply field named "reasoning" asking for "your thinking" (with this system prompt);
  renamed `why`. Failed calls are now recorded and shown to the agent.
- Second LLM run launched: runs/cybertron2/hills_and_forest_seed2 (11 agents, 20 rounds).

### 22 Oct (night, perception)

- Zach: the most important thing is what agents see and how it changes. Wrote docs/review/38_space_engine/02_perception.md: perceive
  where you are; know your body exactly; everything else a belief with a source and an age; count what you can count, estimate the
  rest in words; show change; talk is testimony; the prompt scales with the neighbourhood. An engine-written knowledge store
  (places, houses, people, witnessed acts, testimony, deaths), a sectioned prompt, and the first run's failures mapped to the
  perception that would have exposed them (Dara's hunger visible to the party-mates beside her).

### 22 Oct (night, run result)

- Forest run, seed 1, 20 rounds, $1.78, no errors (docs/review/38_space_engine/01_forest_run.md; logs committed under
  docs/review/38_space_engine/runs/). Both households stocked up and came through winter with no misses; one pre-winter death (Dara
  starved on a three-night hunt carrying nothing); the game was hunted out by round 6 (a porting bug: no inflow); mixed-household
  hunting parties formed but party names failed to coordinate; the first credit offer (Wynn: food now for timber or game later);
  subsistence 88% of actions, walking alone 40%. Fixes proposed (inflow, ration rule, walking cost, default parties).

### 22 Oct (night, run)

- Zach: a small real LLM run with two households in a forest. Built the phase-0 slice of the new engine as `cybertron2/` (world and
  end of round, actions with presence, prompts, run loop, report; about 900 lines; imports only the leaf `cybertron.llm`; forest,
  hunt and hunger formulas ported from the old engine). World `cybertron2/specs/forest_households.yaml`: the Clearing (two
  houses), the Near Wood, the Deep Wood; 8 agents (2 Opus heads, 3 Sonnet, 3 Haiku); 20 rounds, winter rounds 12-17.
- Smoke test with scripted bots: deterministic (two runs byte-identical); found and fixed a quantity-rounding bug (amounts rounded
  up past what an agent held). One-round live test: 8 of 8 replies parsed, $0.13 a round. Full run launched
  (runs/cybertron2/forest_households_seed1, not committed: runs/ is ignored).

### 22 Oct (night, latest)

- Zach: build space as a new engine in its own package rather than retrofitting; port the physical modules onto nodes; scripted bots
  tell us little, so test with LLM agents early. Wrote docs/review/38_space_engine/00_plan.md: the seam is the kernel interface, not
  module boundaries (the law language imports the primitives table, the kernel imports 37 modules), so only 9 leaf modules import
  unchanged; inventory of 167 modules: import 2.5k lines, port onto nodes 19.3k, copy and adapt 45.9k, later 14.1k, leave behind
  8.4k; phases 0-3 with a 12-agent, 4-node hamlet as the first LLM run; a draft board post (not posted). 37.2's P1-P6 now target
  the new engine.

### 22 Oct (night, later)

- Zach: the cold leaves an unsheltered agent starving with chance 0.3; no separate exposure. 02e §3.3 updated: the drop applies after
  the ration (so it bites the next round) and counts no missed meal, so the cold cripples but does not kill under the defaults;
  harsher options stay as spec keys.

### 22 Oct (night)

- Village advantage: a larger skill multiplier does not widen it (households divide trades too); what widens it is techniques above
  household size and poorer degenerate rungs. Combination reaches 1.87x at 24 agents, 2.46x at 48 (02d §5b).
- Clothing parked. Shelter specified in 02e_shelter.md: houses (owner, beds, occupants, condition, hearth); ration x1.0 / 1.2 / 1.5
  by shelter state, more in the cold; exposure in the cold counts as a missed meal (harsher options: starving, death); upkeep every
  10 rounds, breaks (more in the cold), repairs by builders; one hearth a house (fuel per head falls with occupants); tenure, rent,
  eviction gated by law; land on a node shared by forest, fields and lots. Finding: at today's felling cost, a village's fuel and
  repairs take its forest to the floor in about 27 rounds, so a managed woodlot is needed as the organised timber rung.

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
