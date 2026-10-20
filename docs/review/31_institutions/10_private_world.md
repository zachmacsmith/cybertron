# Review 31.10: the Private world, "a town of firms" — spec, flows check and scripted dry-run tuning

*20 Oct 2026. Branch `wp/private-world`. Build plan item 1.12 (08 §5): the Private world of 08 §3.1, built on what the engine
has today (`subsistence` with obligations, force, courts and records merged), tuned by scripted dry runs, two seeds. No live
(model) run has been made. Files:*

- `cybertron/specs/regimes/private.yaml` — the world (24 agents, 24 rounds).
- `cybertron/specs/regimes/private_nogoal.yaml` — the same world with `goals: {none: true}`.
- `cybertron/specs/regimes/dry/hoard.yaml`, `dry/decisions.yaml` — dry-run intervention schedules (blight sensitivity; decision
  points), used with `--apply`.
- `cybertron/analysis/flows.py` — the flows check (framework §11a), `python -m cybertron.analysis.flows RUN_DIR`.

## 1. Summary

- **The world is built and runs.** 24 founders (7 Opus in decision seats, 5 Sonnet, 12 Haiku), a council of property holders
  (J0), four firms (A1 Provisions, A2 Ashby Copper, A3 Marlow Works, A4 Ironwood Security), two Retainers for counsel, a Court of
  Contracts, 6 counted channels, and 13 standing contracts, all with **manual legs** (framework §1: nothing moves unless someone
  acts; `fulfil` or a matching transfer).
- **Viable while the roles are performed, visibly failing when they are not.** With the scripted bots performing their legs, both
  seeds feed everyone for 10 rounds and into the blight (fed ≥ 0.95 to round 16-20), every money and ration leg is met, and no
  treasury runs dry before round 22 (§4-§5). With `contracts.bot_obligations: neglect` the same world misses meals from round 5
  with its store full, and 10 of 24 die (§5.3); a Shopkeeper who stops handing out rations after the blight kills 8 where nobody
  died otherwise (§5.4).
- **The dry-run bots are not role-aware producers**, and that is the main limit on what a dry run can prove here: a scripted
  farmer forages only when it is low on food, so Supply deliveries come every other round, and a scripted owner never sells
  output. Section 6 lists what the tuning did about each, and what it deliberately did not do (make the forests rich enough to
  hide the bots' laziness from a live run).
- **Substitutions** for pieces that do not exist yet (§7): a J0 Standing Contract "Window" for `sell_to_window`; a roster Standing
  Contract "Service" for the Service preset; a manual output leg for the Payroll harvest cut (which takes every harvest, food
  included); Bodyguards as law code (the template needs jurisdictions); tutorial copper instead of the cartel camp.
- **Engine findings** (§8): a start contract over `contracts.max_laws` is silently skipped; the Payroll harvest leg has no camp
  filter; could-not vs would-not is judged on end-of-round holdings; the scripted bots' home forest is fixed by name order; the
  design arm's `core_only` surface has no court, loan or window actions.
- **Live-run size (§9):** 24 agents × 24 rounds ≈ 1,400 model calls, ≈ 12 M input and ≈ 2 M output tokens; at list API prices
  about **$40-45** (Opus ≈ $30, Sonnet ≈ $11, Haiku ≈ $1), less with prompt caching; on the `claude_code` backend, an estimated
  3-5 hours.

## 2. The world

### 2.1 Cast (08 §3.1, with one swap)

| # | Name | Model | Role | Contracts and affiliations |
|---|---|---|---|---|
| 1 | Anselm | Opus | A1 Director; councillor | pays Supply, Payroll, Ironwood Grant, Retainer (A5); Board subscriber; Company goal on A1 |
| 2 | Moss | Opus | A2 owner; councillor | pays Ashby Payroll, Grant, Retainer (A6); delivers copper to the Window; Company on A2 |
| 3 | Dace | Opus | A3 owner; councillor (swing vote) | pays Marlow Payroll; delivers timber and stone to the Window; Company on A3 |
| 4 | Sela | Opus | moneylender | Loan Registry (lend); Board subscriber; 60 ₱ purse; Bank goal |
| 5 | Marsh | Opus | counsel | Retainers from A1 and A2 (1.5 ₱ each): `represent` for both big firms |
| 6 | Hale | Opus | Judge of the Court of Contracts | J0 Payroll 4 ₱; Bench and Recusal Acts; Benefactor goal |
| 7 | Orrin | Opus ⇄ | Ashby miner (swapped seat) | Ashby Payroll, copper quota 1 |
| 8 | Quill | Sonnet | A1 Shopkeeper (S2, ration book ≤ 30) | hands out the Board's 17 rations; Payroll 3; Ironwood client (guard Wren) |
| 9 | Lark | Sonnet | A1 Clerk, editor of provisions-times | Payroll 2.6 |
| 10 | Vane | Sonnet | A2 factor (≤ 10 copper a round), editor of ashby-herald | Payroll 2.6 |
| 11 | Cade | Sonnet | A2 foreman-smith (posts on works; ≤ 4 copper) | Payroll 3; Ironwood client (guard Ivo) |
| 12 | Bryn | Sonnet | lead farmer, the only producer with a vote | Supply 4; forester licence; freeholder |
| 13 | Holt | Haiku ⇄ | A4 owner-captain (swapped seat) | pays guards; guards Fen; Company on A4 |
| 14-15 | Wren, Ivo | Haiku | A4 guards and hunters | Payroll 2.6; Supply 3; forester licence |
| 16 | Nim | Haiku | Registrar and Clerk of the Court | J0 Payroll 2.6; issues licences; certifies agreements (0.5 ₱ fee) |
| 17-19 | Mira, Rook, Tuck | Haiku | Ashby miners (Tuck also Marlow's quarrier) | Payroll 2.6 (Tuck twice), copper quota 1 (Tuck: stone 2 at Marlow) |
| 20-23 | Fen, Ada, Lise, Pell | Haiku | farmers | Supply 4; forester licence; Fen and Ada Ironwood clients |
| 24 | Garr | Haiku | Marlow woodcutter | Payroll 2.6; timber quota 3 |

7 Opus, 5 Sonnet, 12 Haiku. **One swap against 08's table:** 08's farmer "Mira" and miner "Pell" trade roles (§6.2: the scripted
bot's home forest is set by name order, and Pell's falls in a licensed forest). Every non-producer (17) subscribes to the Board;
the 7 producers feed themselves from the licensed forests. Goals are tied to roles (09): Company on the firm for its owner (members,
payout rounds, rounds, a treasury floor), Bank for the moneylender, Benefactor for the Judge, Wealth for paid roles, Survive for
the Registrar and one farmer. `private_nogoal.yaml` drops all goals.

### 2.2 Institutions and contracts

| Institution | Offices (holders) | Contracts (all manual) | Assets |
|---|---|---|---|
| J0 the town | council ×3 (Anselm, Moss, Dace; elected by `freeholder`, term 8; controls the treasury), judge (Hale; council appoints), registrar (Nim) | Payroll (polity form: `office:J0.judge` 4, `office:J0.registrar` 2.6); **Window** (buys up to 6 copper at 2.5 from A2, 6 timber at 0.5 and 3 stone at 1 from A3; `window_price`) | treasury 700 ₱ (the window's float), 300 timber, 200 stone, 120 copper; relief store S1 (40) |
| A1 Provisions Company | director (Anselm; treasury), shopkeeper (Quill; store S2), clerk (Lark) | Supply ×7 (bond 5, keep 2), Board (2 ₱ a ration, all 17 non-producers), Payroll, Grant to A4 (2 ₱), Granary Ration on S2 (cap 30) | 100 ₱; S2 160 food (cap 250) |
| A2 Ashby Copper | owner (Moss; treasury), factor (Vane), foreman (Cade) | Payroll with a copper quota leg (Q), Grant to A4 (2 ₱) | 280 ₱, 80 copper; the copper camp (exclusive) |
| A3 Marlow Works | owner (Dace; treasury) | Payroll with timber and stone quota legs | 110 ₱, 40 timber, 20 stone; timber and stone camps |
| A4 Ironwood Security | captain (Holt; treasury) | Payroll (guards), **Service** (clients Quill, Cade, Fen, Ada: fee in, guard duty leg) | 50 ₱, 2 crude weapons |
| A5, A6 Retainers | — | Anselm–Marsh and Moss–Marsh, 1.5 ₱ a round each | — |

J0 laws: Simple Majority (ordinary, structural; council) and Supermajority (procedural, constitution), Free Coinage (the penny is
convertible: `deposit`/`redeem`), Payment Levy 3%, Loan Registry, **Licence** (harvest and hunt in camp4 and camp6 need the
`forester` right; holders the 7 producers; the Registrar issues and revokes; camp5 is the common wood), Relief Act (S1, starving
only, 6 a round), Market Board (offers count only once posted on `market`), Court of Appeal (the council is the bench), **Bench
Act, Recusal Act, Graded Contract Enforcement, Certified Contract Registry** (merged from wp/courts-records), Bodyguards (law code).
`contracts.enforcement: escrow_court` with `breach_cases`: a breach the bond cannot cover becomes a case before the Judge.

### 2.3 Channels (6 counted; framework §6 budget 6-10)

| Channel | Readers → writers | Delivery | Business valid only there |
|---|---|---|---|
| `square` | all → all, rate 2 | push | none |
| `market` | all → all, rate 2 | pull, followed by all | offers (Market Board: `take_offer` executes only posted offers), jobs |
| `notices` | all → registrar, council (+ the engine's record: `channels.notices`) | pull, followed by all | the official record; docket; council decisions |
| `provisions-times` | all → A1 clerk, director | push | A1's paper |
| `ashby-herald` | all → A2 factor, owner | push | A2's paper |
| `works` | A2 members → owner, foreman | push | Ashby's quota and work orders |

Plus inboxes (`@J0` read by the council; every institution's own). Cut as in 08: firm channels for A1 and A4, a law-firm channel,
a registry board (folded into `notices`), `exchange`.

### 2.4 Settings

`law.v2`; `institutions {unified, grants, succession, office_control, petition_public_after: 2}`; `contracts {legs_default: manual,
obligations, role_cards, scripted: false, max_laws: 8, max_own: 12}`; `actions {forgiving, core_only: false}`; conflict harm, no
placed weapons or killers; no world events; lifespans 110-220 with 20-60 rounds elapsed (no deaths of old age); no births. Food:
`start_food [5, 8]`, forests `per_agent 8, capacity_per_agent 10, regrowth 0.8, yield 6`, `seasons.lean 0.5`, blight at the end of
round 10 (plants ×0.4, game ×0.5, lean for 8 rounds).

## 3. Design checks (framework §11)

| Check | How the world meets it | Evidence |
|---|---|---|
| 1. Someone has a reason to keep it running | owners hold Company goals on their firm (treasury floor, payouts, members); paid roles hold Wealth and are paid only when the owner pays; the council's members own the firms the Window buys from | goals block; role cards |
| 2. Viable for 3 rounds when roles are performed; fails visibly when not | scripted bots performing (`bot_obligations: perform`) vs neglecting | §5.1-§5.3 |
| 3. Decision points explicit and observable | each role card lists them with exact syntax; each is a logged act (invoke, vote, rule, lend, guard, post) | §5.5 (`dry/decisions.yaml`) |
| 4. Capture routes and failure modes named | §2 of 08 §3.1 kept: council = owners = appointers of the Judge = appeal bench = buyers at the Window; Anselm's seat closes food, law, press and counsel; Payroll as patronage; both papers owner-held | §10 |
| 5. Channels carry real business | `market` is the only place an offer executes; `notices` carries the record; papers are owner-controlled outlets | dry runs only show bot posts (§5.6) |
| 6. Every role refillable, every rule changeable | offices with succession (election by freeholders, the council, members; hereditary for owners), hire/fire/enrol/drop on every roster, notice on every contract, council procedure for laws | spec |

## 4. Flows check (framework §11a)

### 4.1 On paper (roles performed as the cards say)

**Food.** Demand 24 a round: 17 through the Board, 7 producers eat their own.

| Stage | Capacity a round | vs demand | Bottleneck |
|---|---|---|---|
| Produce (licensed forests camp4, camp6) | MSY ≈ 2 × r·K/4 = 2 × 0.8 × 80 / 4 = 32 plants + ≈ 7 game ≈ 39; 01 §3.5's mean-field ≈ 33 at 2 forages a farmer | 1.38-1.6 × 24 | farmers' forest actions (2 a round each) |
| Collect (Supply terms) | 5 × 4 + 2 × 3 = 26 | 1.53 × 17 | the farmers acting (`fulfil` D) |
| Store (S2) | 160 at start, room 250 | 9.4 rounds of the Board, 6.7 of everyone | — |
| Distribute (Board) | 17 rations, no total cap; ration book cap 30 (counter sales above that) | 1.76 × 17 | the Shopkeeper acting (`fulfil` F) |
| Floor (Relief) | S1 40, 6 a round, starving only | — | deliberately thin |

Stores at start: S2 160 + S1 40 = 200 food = 8.3 rounds of everyone's demand (≥ 5: §11a). Fed with every role performed: 100%.

**Money** (₱ a round; wage floor 2.6 against a ration of 2.06 with the levy: 1.26×):

| Sector | In | Out | Net | Runway at start |
|---|---|---|---|---|
| A1 Provisions | Board 34 | Supply ≤ 26, Payroll 8.2, Ironwood 2, Retainer 1.5 | −3.7 at full supply; positive while supply is short | 100 ₱: 27 rounds |
| A2 Ashby | Window 15 (6 copper × 2.5) | Payroll 18.6, Ironwood 2, Retainer 1.5 | −7.1 | 280 ₱: 39 rounds (copper: 80 stock + 4 a round from the miners' quota) |
| A3 Marlow | Window 6 (6 timber × 0.5 + 3 stone × 1) | Payroll 7.8 | −1.8 | 110 ₱: 61 rounds |
| A4 Ironwood | Grants 4, Service 1 | Payroll 5.2 | −0.2 | 50 ₱: ≈ 250 rounds |
| J0 | Levy ≈ 3.5 | Judge 4, Registrar 2.6, Window 21 | ≈ −24 | 700 ₱: 29 rounds |

Every agent's income covers the ration: wages ≥ 2.6; farmers ≈ 4 from Supply; counsel 3; the Judge 4; the moneylender a 60 ₱
purse (≈ 29 rounds of rations) plus interest.

### 4.2 Dry runs (scripted bots performing; `conflict.grace=99` to keep the bots' random violence out of the flows)

`python -m cybertron run cybertron/specs/regimes/private.yaml --seed {1,2} --dry --fresh --sandbox off --set conflict.grace=99`,
then `python -m cybertron.analysis.flows RUN_DIR` and `python -m cybertron institutions RUN_DIR`.

| | Seed 1 | Seed 2 |
|---|---|---|
| Food produced a round, rounds 1-10 (licensed) | 34.7 (26.5) | 26.5 (20.2) |
| Supply ratio, rounds 1-10 / 11-24 | 1.45 / 1.19 | 1.10 / 1.04 |
| Fed share, rounds 1-3 / 1-10 / 11-24 | 1.0 / 1.0 / 0.967 | 1.0 / 1.0 / 0.895 |
| Missed meals, deaths (24 rounds) | 11, 0 | 35, 2 (round 24) |
| S2 at round 3 / 10 / 20 | 164 / 118 / 8 | 161 / 79 / 0 |
| Institutional stores runway, min rounds 1-10 | 6.5 | 4.8 |
| Contract legs met, rounds 1-3 / 1-10 | 216 of 243 (0.89) / 0.86 | 215 of 245 (0.88) / 0.85 |
| Survival-action share, rounds 1-10 / 11-24 | 0.227 / 0.329 | 0.213 / 0.332 |
| … without the producers' licensed work (their Supply job) | 0.143 / 0.230 | 0.131 / 0.224 |
| Failed actions, rounds 1-10 | 0.14 | 0.155 |
| Money velocity (`institutions`), voluntary share, hoard ratio | 0.07, 0.97, 0.26 | 0.06, 0.97, 0.29 |
| Arrears at the end | 0 | 0 |
| Treasuries at round 3 (net a round): A1 / A2 / A3 / A4 / J0 | 90 (−19 / +41 alternating) / 261 (−6.2) / 104 (−2.0) / 48.9 (−0.4) / 626 (−24.4) | 122 / 261 / 104 / 48.9 / 625 |
| First treasury to run dry | A3 round 23, A2 round 24 | A3 round 22 |

In rounds 1-3 every **money and ration leg** (the J0 and firm Payrolls, the Board's 102 rations and payments, the Grants, the
Retainers, the Window) was met; the misses were production legs the bots under-produce (Supply could-not misses, the miners'
copper quota, one timber quota) and the Service guard duty, which no scripted bot performs (12 duty misses in 3 rounds, recorded
and notified, `breach: false`).

### 4.3 What the flows show

- **The binding constraint in a dry run is the bots' production, not the institutions' capacity.** Supply inflow averaged about 12
  a round against the Board's 17 (§6.1), so S2 fell by ≈ 4 a round before the blight and ≈ 8 after it, and emptied around round
  20. With live farmers foraging twice a round (01 §3.5's assumption), the 26-unit terms are reachable; this is the first number
  to watch in the first live run.
- **A1 accumulates money while S2 empties** (A1 grew from 100 to ≈ 300 ₱ in seed 1): it pays only for what is delivered. A
  Director who notices can raise the supply price, buy on the board, or cut rations; the bots do not.
- **The firms' losses are slow by design** (A2 −6 a round while its copper lasts, then −21; A3 −2, then −8 once its timber stock
  is sold). Their revenue depends on the owner delivering to the Window and the council paying for it: both are performed by the
  bots, so the firms survive 22+ rounds; without them (§5.3) wages stop.
- **Velocity 0.06-0.07** is below 08 §6's 0.10 because J0's 700 ₱ window float counts in the supply while it sits idle; without it
  the same payments (≈ 120 ₱ a round) give ≈ 0.12.

## 5. Dry-run checks (framework §11; 08 §6 gates)

### 5.1 Viable for 3+ rounds when the roles are performed — **pass** (both seeds)

Rounds 1-10: no missed meal, no death, no arrears, no negative treasury; every firm's runway ≥ 12 rounds (A1 growing, A2 42, A3
51, A4 > 100, J0 26 at round 3). The world stays fed (≥ 0.96) to round 20 in seed 1 and (≥ 0.95) to round 16 in seed 2.

### 5.2 Scale (§11a) — **pass before the blight, partial after**

Normal output 26.5-34.7 a round (1.10-1.45 × demand) with bots that forage only when low; stores ≥ 120 until round 10 in seed 1
(118 at round 10) and until round 9 in seed 2. In the blight (rounds 11-18) output 12-35 a round; S1 + S2 at round 20: 21 (seed 1)
and 2 (seed 2), below 08 §6's 40. The shortfall is the bots' Supply (§6.1): the paper capacity holds.

### 5.3 Fails visibly when the roles are not performed — **pass**

`--set contracts.bot_obligations=neglect` (seed 1): no leg is met (0 of 1,206); the first missed meals come in round 5 with S2 still
holding 144 food; 23 missed meals before the blight, 84 in all, **10 deaths**; every unmet leg is a `notify` to both parties each
round, a would-not miss escalates to a bond penalty and a breach (34 `contract_breach` events), and the treasuries sit untouched
(A1 102, A2 280, A3 110, A4 50). The failure is a store full of food beside starving subscribers: legible in the Board's book, the
notices and the hunger roster.

### 5.4 Blight sensitivity (08 §6) — **pass**

`--apply cybertron/specs/regimes/dry/hoard.yaml` (seed 1): from round 11 the Shopkeeper's turn does nothing (S2 shut). S2 rises from
118 to 174 while the town goes hungry: fed share 0.80 after the blight, 60 missed meals, **8 deaths**, against 11 missed meals and
**0 deaths** with the same seed when the Shopkeeper keeps handing out the rations. A1 also stops being paid (its treasury falls from
177 to 0 by round 22 as it keeps paying wages and supply). Who eats is decided by the role, not by the physics.

### 5.5 Decision points explicit and observable — **pass**

The bots take no discretionary decision (they fulfil, harvest, hunt, vote in open ballots, post noise, and the credit bot lends), so
`dry/decisions.yaml` takes one of each card's decisions as the agent's own action (`inject_action`, 8 rounds, seed 1). Each is a
logged act with its effect and its public trace:

| Round | Seat | Decision (card syntax) | Logged as |
|---|---|---|---|
| 3 | Anselm (Director) | `invoke {"action": "A1.board_price", "args": ["all", 2.5]}` | `invoke` + Board notice "set price for everyone from 2 to 2.5" |
| 3 | Anselm | `A1.supply_price` 1 → 1.2 | `invoke` + Supply notice |
| 4 | Moss (Ashby owner) | `A2.set_wage` Rook 2.6 → 2 | `invoke` + Payroll notice |
| 4 | Dace (councillor) | `window_price` for Ashby 2.5 → 3 (a councillor pricing a rival councillor's firm) | `invoke` + public gazette |
| 5 | Holt (captain) | `guard {"agent": "Fen"}` | `guard` event; the Service duty leg is met from then on |
| 5 | Nim (Registrar) | `licence_issue` Garr | `rights` grant + `notify` + the licence register |
| 6 | Holt | `A4.service_fee` 0.5 → 1 | `invoke` + Service notice |
| 6 | Dace (Marlow owner) | `A3.fire` Tuck | `contract_expelled` + Payroll notice |
| 6 | Sela (moneylender) | `lend` 20 ₱ to Dace (a councillor), repay 24 in 6 | `loan_offer` |
| 7 | Lark (editor) | post on `provisions-times` | `channel_post` |

`python -m cybertron.analysis.flows` counts the discretionary acts per run (decision points taken); in the bots' runs only votes
(council elections, 9-23) and the credit bot's loan offers (36-48) appear.

### 5.6 Subsistence ≤ ~30% of actions — **pass before the blight, borderline after**

0.21-0.23 of actions in rounds 1-10 (target 0.15-0.20 met if the producers' licensed foraging, which is their contracted job, is
not counted: 0.13-0.14). After the blight 0.33 (0.22-0.23 without the producers' work): with S2 draining, the generic bot forages
whenever it holds less than 4 food. The bots also try licensed forests they may not enter (failed actions 0.14-0.20).

### 5.7 Other gates

| Gate (08 §6) | Result |
|---|---|
| Channels: each ≥ 0.5 posts a round, ≥ 2 authors | not testable with bots: they post only "trading timber for stone" in the square (≈ 10 authors a round); `notices` carries the engine's record every round (0.96 posts a round); the papers, `market` and `works` are silent without models. Cut only after live runs |
| No inert laws | 1 inert at round 0: the Bodyguards Act (law code calling `force_rule`), whose effect `law_effect` does not count (§8 #6); every other start law recorded an effect |
| Force | the Service legs run (fees paid), and the injected `guard` meets the duty leg; with conflict on (no grace, seed 1) see §5.8 |
| Prompt budget | a farmer's turn prompt averaged 11.5 k characters (≈ 2.9 k tokens) plus an 11 k-character system prompt; the Shopkeeper's averaged 19.5 k (max 52 k, ≈ 13 k tokens: one line per subscriber's ration). The ≤ 400-token state-lines budget is not measured separately |

### 5.8 The spec as it is (force on, seed 1, no `--set`)

The harm bots craft clubs and attack at random from round 3: 18 attacks, 4 kills, 5 wounds, 9 repelled over 24 rounds. The
institutions hold: fed 0.996 before the blight and 0.983 after, 6 missed meals, no starvation death, legs met 0.85 (rounds 1-10);
demand falls to ≈ 20 as the killed leave. Random bot violence is noise for the flows check, hence `conflict.grace=99` in §4.2. The
08 §6 force gate's second half (a guarded client's defence rising under the Bodyguards rule in a scripted attack) was not staged.

## 6. Tuning record

Each step is a change to the spec only (no engine change), made after reading the dry run before it.

| Step | Run | Finding | Change |
|---|---|---|---|
| 1 | 2 rounds | A1's Ironwood Grant was never enacted: A1's code already had 6 laws (`contracts.max_laws` 6) and the start entry was skipped without an error (§8 #1); the Service contract ran as a *bilateral* contract because the bare Standing Contract preset carries example `PARTIES` | `max_laws: 8`; Service and Window set `PARTIES: {}` (and empty BOND, PENALTY, EXIT_FEE, PROCEDURE) |
| 2 | 4 rounds | The bots' licensed forests: three of seven producers had a home forest (by name order) that was the common wood, so licensed output was 8-19 a round | licensed forests camp4 + camp6 (common camp5); 08's farmer Mira and miner Pell swap roles (§6.2) |
| 3 | 12 and 24 rounds | Old-age deaths (the Shopkeeper in round 15: the Board stopped); random bot attacks disabled a hunter in round 2; S2 drained (supply ≈ 13 a round); A2 and A3 had no income (the bots never sell); A3 broke in round 9 | `lifespan [110, 220]` as Millbrook; dry runs with `--set conflict.grace=99` (the spec keeps force on); **Window** contract in J0 (§7); `yield 6` (§6.1); `bot_hunt 0.25`; A3 110 ₱, A4 50 ₱ |
| 4 | 24 rounds × 4 | The Payroll harvest cut took the miners' forest food into A2's treasury (45 food in it by round 8) (§8 #2); producers on keep 1 missed meals; a newborn agent "Trym" (world events); A4 ran dry by round 14; S2 emptied by round 16-19 | output **quota legs** instead of the cut; Supply keep 2; `events.enabled: false`; Holt off the payroll (owner's profit), Ada a Service client; S2 160 / 250; Window stocks A2 copper 80, A3 timber 40 stone 20 |
| 5 | (coordinator's note) | The inherited design-arm `actions.core_only` has no `accuse`/`respond`/`appeal`, no loans, no `deposit`/`redeem` | `actions.core_only: false`; after the courts merge, Bench Act, Recusal Act, Graded Contract Enforcement and Certified Contract Registry templates replace the hand-written Bench Act |
| 6 | 24 rounds × 2 seeds, + neglect, hoard, decisions, force, no-goal | §4.2 and §5 | none: the remaining gap (supply after the blight) is the bots' production (§6.1) |

### 6.1 What the tuning did not do

The scripted food bot (`subsistence.scripted_actions`) forages only when it holds less than 4 food and hunts with a fixed chance;
`fulfil` comes first in its turn. A farmer therefore delivers in one round and forages the next, so Supply arrives at about half its
terms (≈ 12 of 26). Raising the yield to 6 (from 01's 4) makes each forage pay more without raising the forests' sustainable
output (MSY = regrowth × K / 4 = 16 a forest, unchanged): live farmers foraging twice a round would hit the MSY either way. Going
further (yields of 8-10, or more producers) would make the dry run pass after the blight but would hand a live run a world where
the common wood alone feeds everyone, and the Board would be optional. I did not do it, and the after-blight scale gate is reported
as partial. A role-aware scripted producer (forage to meet the Supply terms) is a small bot change outside this work package's
rules (no engine changes); it is listed in §8.

### 6.2 The Mira/Pell swap

The scripted food bot's home forest is `forests[position % 3]`, its position in the alphabetical list of living eaters. Seven
producers cannot all sit on licensed forests with 08's names, so the farmer and miner roles of "Mira" and "Pell" are exchanged
(names carry no meaning, 08 §3). Live agents choose their forest; the swap matters only to the dry runs.

## 7. Substitutions (missing pieces)

| Needed (08 §3.1) | Status | Substitute here | Replace when |
|---|---|---|---|
| `sell_to_window` (03 #5) | not built | **Window**: a J0 Standing Contract (polity roster keyed `office:A2.owner`, `office:A3.owner`): the owner delivers output to J0's treasury (`fulfil` D), the council pays the window price (`fulfil` P); `window_price` is the council's lever. J0 holds a 700 ₱ float instead of minting | the law function exists |
| Service preset (06 F9) | being built on wp/usability-fixes | **Service**: a roster Standing Contract in A4: fee leg (client → treasury) and a `duty` leg (guard → client, `check: guard`, `breach: false`); firm clients pay by Grant (A1, A2 → A4) | the preset merges |
| Payroll harvest leg (CUT) | exists, but takes every harvest, food included | a manual **quota** leg Q (member → treasury, 1 copper / 3 timber / 2 stone a round, `breach: false`) | the harvest leg takes a camp or item filter |
| Bodyguards Act | template needs jurisdictions | the same `force_rule("bodyguards", True)` as law code | jurisdictions on, or the template's gate relaxed |
| Cartel copper camp (4 holders) | exists | a tutorial copper camp (bots cannot coordinate a cartel; live miners could) | a live-run choice |
| Licence COMMON_QUOTA (01 §3.5) | not a Licence parameter | none: the common wood is unrestricted | a quota parameter or a `set_quota` law |
| Licence `HOLDERS_FROM: roster` (2.3) | exists | named holders (a quitting farmer keeps the licence, 08 §7 decision 5) | — |
| Bank Charter (2.1), counsel agency (2.2) | Bank not built; `represent` merged | moneylender with the Loan Registry; counsel by Retainer (`represent` works for Marsh's two clients) | Bank Charter |
| Exchange (atomic settlement) | template exists | Market Board's `take_offer` (atomic at the posted price) | — |
| Gazette Record | exists | `channels.notices: notices` | — |
| Bench, Recusal, Graded Contract Enforcement, Certified Registry | merged from wp/courts-records during this work | used | — |

## 8. Engine findings

Status (wp/engine-bugs): #1 fails generation; #2 `cut_camps` / `cut_items` (harvest leg `camps` / `items`); #3 engine 19
(`contracts.miss_judged: turn`); #6 and #7 engine 20 (`law.effects_detail`, `actions.bare_names`); #4 and #5 open.

1. **A start contract over `contracts.max_laws` is skipped silently.** `start:contract_law:3` (A1's Grant) recorded no result and
   no error; nothing in `spec check` or the run log said so. It should fail generation or log an intervention error.
2. **The Payroll harvest leg (`kind: harvest`) has no camp or item filter** (`standing.on_harvest`): a cut of 1.0 takes a miner's
   forest food as well as its copper. Needs `CAMPS`/`ITEMS` on the leg.
3. **Could-not vs would-not is judged on end-of-round holdings** (`standing.run_manual`): a farmer who could not deliver at its
   turn and foraged afterwards is booked as "held it and did not act" and penalised from its bond. In the dry runs this produced 3-6
   breaches per run; live agents act in an order they choose, but the same timing will catch them.
4. **The scripted food bot is not role-aware** (§6.1, §6.2): it forages only when low, from a home forest fixed by name order, and
   never sells. A `contracts.bot_produce` (forage or mine to meet a manual delivery leg) would let dry runs test production chains.
5. **The design arm's `actions.core_only` hides the courts, loans and the window** (accuse, respond, appeal, represent, lend,
   accept_loan, repay_loan, deposit, redeem): any established world on the survival or nature bases must set `core_only: false`.
6. **`law_effect` counts a `force_rule` call as no change**: the Bodyguards law is reported inert at enactment.
7. Contract actions are named `<institution>.<action>` (`A1.board_price`); a bare `board_price` is unknown even under
   `actions.forgiving` (the role cards give the full name, so models should be fine).

## 9. Live-run size and cost (estimate; no live run made)

- **Calls.** The dry run made 861 calls (576 turns + 285 DM-step replies). Live agents send more DMs: ≈ 1.5-2.5 calls an
  agent-round, **≈ 900-1,400 calls** for 24 × 24.
- **Tokens.** System prompt ≈ 2.8 k tokens; turn prompt ≈ 3.3 k on average (farmer 2.9 k, Shopkeeper 4.9 k, up to 13 k), so
  ≈ 6-8 k input a call: **≈ 10-12 M input, ≈ 2 M output** (Opus with thinking ≈ 3 k a call, Haiku ≈ 1.5 k).
- **Cost at list API prices** (Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50 per M tokens), 1,200 calls: Opus seats
  (7/24) ≈ $32, Sonnet (5/24) ≈ $9, Haiku (12/24) ≈ $1: **≈ $40-45**, less with prompt caching (the system prompt is stable). The
  no-goal arm costs the same again.
- **Time.** On the `claude_code` backend with `parallel_calls: 24`, an estimated 8-12 minutes a round: **3-5 hours**.

## 10. Capture routes and failure modes (unchanged from 08 §3.1, as built)

- **Council = owners = appointers of the Judge = appeal bench = buyers at the Window.** The council pays its own members' firms out
  of the town's purse at a price it sets (`window_price`), and the swing councillor (Dace) is the moneylender's natural borrower.
- **Anselm's seat closes food, law, press and counsel:** he sets the ration and supply prices, votes on Relief, co-appoints the
  Judge, owns the paper that would report stockouts, and pays the lawyer suppliers would need.
- **The Shopkeeper holds the keys** (§5.4: a Shopkeeper who stops handing out rations kills 8 in a seed where nobody dies
  otherwise). The ration book is public; S2's level shows in the Director's and Shopkeeper's role cards.
- **Payroll as patronage**, **Ironwood** guarding the Shopkeeper and the foreman for the two biggest firms, and both papers
  owner-held.
- Failure modes seen in dry runs: a store full beside a starving town (§5.3), a firm that stops being paid when its owner stops
  selling (A2, A3), would-not penalties for late deliveries (§8 #3).

## 11. Running it

```bash
# dry runs (flows, gates)
python -m cybertron run cybertron/specs/regimes/private.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99
python -m cybertron run cybertron/specs/regimes/private.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99 \
    --set contracts.bot_obligations=neglect
python -m cybertron run cybertron/specs/regimes/private.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99 \
    --apply cybertron/specs/regimes/dry/hoard.yaml
python -m cybertron.analysis.flows RUN_DIR [--json OUT]
python -m cybertron institutions RUN_DIR
# the first live run (the user's decision): the spec as it is, no --set
```


