# 02zo · What is open in 37.2's area, after sweeping every proposal (5 Nov)

Zach, 5 Nov: "aren't there a bunch of other open and incomplete things ... Is the proposals still being kept up?", then "do this".
37.2's 21 open proposals were read against DECISIONS.md, the spec, OPEN.md, the review notes and the engine, and each open question
marked decided, built, superseded, dropped or still open (each file has a 5 Nov History entry). This is the result in one list, the
counterpart of 37.4's 38.51 for their area.

**The answer to "is it kept up":** not well. Before the sweep:
- 34 of 92 proposals were open, most untouched since 23-24 Oct;
- the index table lacked 37 proposals and the log lacked 12.

**Now:**
- every one of 37.2's open proposals has an accurate status;
- the index is rebuilt from the files: `python3 docs/cybertron2/proposals/rebuild_index.py docs/cybertron2/proposals`;
- 37.4 is asked to sweep their 13.

## A. Decide now: each is small and unblocks something

| # | Decision | Recommendation | Where |
|---|---|---|---|
| A1 | **Salt has no source.** Cheese needs 0.2 salt, and no world makes or seeds it, so cheese cannot be made anywhere. D2-56 decided salt from saltmarsh pans or a salt spring; it was never built. | Build salt-making at saltmarsh now (a gather technique, data only), and salted meat with the preservation proposal | resources_and_goods.md; economy_plan.md; goods.md |
| A2 | **The night watch costs nothing.** D2-21 decided a watch that gives up sleep and eats more (x1.5). As built, `guard` costs one unit and keeps both. | Make `guard` at night the watch, with no sleep and x1.5 food (small, engine) | attacks_and_walls.md Q3; conflict/defence.md |
| A3 | **The garden and hay as crops** (D2-53). Neither is built; hay is cut from pasture instead (D4-42). | Drop hay as a crop (D4-42 covers it). Keep the garden for the preservation and food-variety work, on built ground by the house | farming.md |
| A4 | **The vulnerable young** (fertility.md Q2 to Q4). Only infants' shelter is built (D4-97). | Adopt Q2: hunger and cold raise a child's risk too (cheap; makes food and houses matter). Q3: no extra youth risk. Q4: leave a child's cost to the land. | fertility.md |
| A5 | **Pregnancy and gap: scaled with lifespan or fixed in days** (fertility Q1; L-27) | Scaled, as now, and read replacement from long runs (L-27) | fertility.md |
| A6 | **Part of a building parcel held** (plot shares cover fields only) | Not yet: whole-parcel claims until a crowded village shows the need | buildings_integration.md Q4 |
| A7 | **The organised advantage of 2 to 2.5 times** (38.20 C6, never answered) | Drop the fixed target and measure against the dependence null (D2-137) | economy_plan.md |

## B. Confirm as built (built since 24 Oct, never confirmed)

- **Q-21:** herds, fences and roads, 15 choices. Q-21 item 15 is stale: the generator now sets parcels' sides and heights.
- **Q-22:** children, 12 choices. Q-22 (2) is stale: since D2-162 a pregnancy refuses `try` from the first day.
- **Q-23:** forests and fuel, 10 choices.
- **C-5:** riders as a fuse event, with no exception to D4-8.
- **Road trouble:** the line between settling it automatically and an urgent call (death risk 0.05, half the load, chance 0.1).
- **D2-124:** losses on the road by head.
- **Fertility Q5:** the last day lighter, and signs from the day after conception.
- **D2-167:** bread only from mill flour. It is marked "to confirm" but built.

Recommendation: confirm all as built (37.4's 38.51 §B recommends the same for Q-21 to Q-23 and C-5).

## C. Decided but not built: keep waiting, or drop?

None is blocking. Each waits for its system:
- blades (D2-46);
- traps, locks, the saddle, carts, parchment and documents (D2-23, D2-24);
- the specialised tools (D2-48);
- great trees and great beams (the felling axe has nothing to fell);
- horses (D2-6);
- skill fading (production.md; not in knowledge.py);
- standing work orders for adults (D4-16; built for children only).

Recommendation: keep them all as decided-and-waiting. The spec now says which are not built.

## D. Open, deferred with a system: no decision until that system is taken up

| Item | Waits for |
|---|---|
| Disease: deaths, the sick's work, a healer, immunity, nursing (Q-16) | a disease proposal |
| Water as a need, wells and latrines, groundwater and the river's hidden state, the first variables, damping, nutrition by variety (environment_state Q1 to Q6; L-23) | L-23; it pairs with the water proposal |
| The scheduler's details (hidden daily conditions, data and interfaces, 02q's numbers) | the stage 2 scheduler |
| Which climate zone after temperate; a world as a zone plus dials (ecosystems Q1, Q3, Q4) | each zone's engine system (D2-191) |
| Wild land as large parcels, places and reach, roads or across country, places finer with use (generator Q2, Q3, Q6, Q7; L-33, L-35) | towns and the frontier |
| Danger per edge and its order (C-6) | roads used heavily in runs |
| Room bookings and lodging terms | an inn or hall that needs them |
| Break-in work, the raid multipliers' numbers, the village wall, node raids, fire numbers | raids in runs; L-21, L-22, L-48 |
| Documents as objects, channels as media, institutions with archives, shelves (C-4) | letters and boards (37.4) |
| Dogs as a beast; rules for a common herd | wildlife (L-37); leave to people |
| The hard tier (iron, tin, silver, old oak, wild horses, goods from beyond); the unlocks shortlist | by era (L-13) |
| Fine building giving more than notice | a run where someone builds finely |

## E. Drop

Wax tablets: nothing needs them.

## F. Open from the recent conversation (also Zach's)

- Run the cheap ladder (L-50; 3 runs, about $75 to $90).
- The varied landscapes plan (per-world wood, wetlands and meres, floodplains, ponds as parcel features, ranges and variety checks).
- The water, preservation and boats proposal (fishing gear, weirs, salt, reeds, peat, the smokehouse, the coast, then boats).
- Transport after the ladder (L-53).
- The carrying burden as a measure (L-52).

## Contradictions the sweep found

**Fixed by 37.2:**
- **goods.md:**
  - coin's metal is copper (D2-28);
  - the first-world set is decided, not "still a proposal";
  - the goods decided but not built are named, and salt has no source.
- **production.md:**
  - the plot unit is settled (D4-40, D2-59);
  - the felling axe's great trees do not exist yet;
  - skill does not fade as built.
- **buildings.md and lodging.md:**
  - the camp store is about 10 weight under cover (D4-84), not 15 in the open;
  - the defence multipliers as built: wattle x1, a barred door x1.5, asleep inside x0.5.
- **scheduler.md** now says what is built: only the day's weather within hand-written spells. 02zc says the same.
- **D2-124** is marked "built by head; Zach to confirm".
- **OPEN.md:**
  - L-8 is done;
  - L-11 is narrowed to borders, hedges and folds;
  - L-34 no longer waits on the land;
  - L-101 is new: compile the generator into spec/world/generation.md, which is still as of 23 Oct.

**For 37.4 (their files):**
- OPEN Q-21 item 15 and Q-22 (2) are stale.
- conflict/defence.md: its `watch` for the night is not the engine's `watch` (learning by watching); the night watch is not built.
- A raid on a house only takes food (L-64).
- Two cairns: the monument's (6 stone, 3 units, carries lines) and the grave's (D4-99: 3 stone, 2 units, none).
- D2-74's signs across nodes are decided but not built (Q-18).
- The life spec's Open list lacks fertility.md §3 to §5.
