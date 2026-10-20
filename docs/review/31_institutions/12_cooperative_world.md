# Review 31.12: the Cooperative world, "the Commons" — mechanisms, spec, flows check and scripted dry runs

*20 Oct 2026. Branch `wp/coop-world`. Build plan items 2.11, 2.12 and the Cooperative part of 2.15 (08 §5): the world of 08 §3.4,
built on `subsistence` (Phase 1 done, force chain and courts merged) with the method of `10_private_world.md`. Scripted dry runs only:
no live (model) run has been made. Scripted bots are weak evidence; the dry runs here show the world is **wired and viable when its
roles are performed**, not how agents will behave. Files:*

- `cybertron/library.py`, block "cooperative" at the end: **Assembly Motions, Cooperative Store, Mutual Credit, Commons Dues, Duty
  Roster, Militia Roll, Muster Act** (established templates; tests `tests/test_commons.py`).
- `cybertron/specs/regimes/cooperative.yaml`, `cooperative_nogoal.yaml` — the world (24 agents, 24 rounds) and its no-goal arm.
- `cybertron/specs/regimes/dry/coop_perform.yaml` (the roles bots cannot perform, injected), `coop_pledge_cut.yaml` (blight
  sensitivity), `coop_decisions.yaml` (one of each card's decisions).
- `cybertron/analysis/flows.py` — a `commons` section (pooling, meals, payouts, credit turnover and velocity, over-limit members,
  duties, militia, motions, musters).

## 1. Summary

- **Built:** seven opt-in templates (§2): the general meeting's `MOTION:` ballot hook (**Assembly Motions**), the **Cooperative
  Store** (store variant, 01 #6), **Mutual Credit**, **Commons Dues** (the Charge in credit), the **Duty Roster**, the **Militia Roll**
  and the **Muster Act**; 15 tests; a `commons` section in the flows check. No engine code changed (no engine version, no default
  flip, no golden fixture touched). The Cooperative world `cooperative.yaml` (+ `cooperative_nogoal.yaml`) per 08 §3.4.
- **Wired and viable when roles are performed** (2 seeds × 24 rounds, `coop_perform.yaml` doing what bots cannot: militia reports,
  gather forays, the minutes): everyone fed every round, no missed meal, no death; S1 never below 98 (seed 2) / 139 (seed 1); the
  Miners' Co-op and the Commons' treasuries solvent to round 24; every militia duty met; credit velocity 0.35-0.37 a round (≥ 0.14 at
  the end); one member over the credit limit (Sela, who opens at −8).
- **Decisions are live and legible** (`coop_decisions.yaml`, 8 rounds): four motions posted, three passed by the bots' votes and took
  effect (LIMIT 20, PAYOUT 0.9, a MUSTER), one withdrawn by the Moderator; the militia on duty served the muster (the target
  resisted; it lapsed); two keys issued a blade; a duty excused; a credit payment and a Common Fund payment.
- **Where it is weak:** the food stage is the most automatic of the four regimes: pledges are standing consent and meals are by
  rule, so with *no* role performed (`bot_obligations: neglect`, no schedule) nobody starves either; what fails visibly is the rest
  (no wage or Window leg in 24 rounds, treasuries frozen, 48 of 48 militia duties missed, 10 members over the credit limit by round
  24). The **blight-sensitivity gate is partial**: producers cutting their pledges at the blight drains S1 from 188 to 42 by round
  24 (vs 155) but kills nobody within 24 rounds; the reserve outlasts the run. Survival-action share after the blight is 0.41-0.46
  (gate 0.30), the bots' foraging as in Private.
- **Engine findings** (§7): laws of different institutions cannot read or move into each other (so the Food Co-op is J0's own law);
  channel posts and watches are invisible to `history`; the kernel's `majority` is of the whole electorate; no `on_round_start` in
  the round of enactment; lot refills only one seat of a multi-seat office; the scripted jurisdiction bot pulls a member out of J0.
- **Prompt budget:** a Haiku farmer or consumer sees 180-360 tokens of registers', contracts' and channels' lines (within 400); a
  Haiku miner 500-680 and the Haiku Tallyman 420-510 (over, mostly the Phase 1 Payroll obligation and role-card lines).
- **Live run:** ≈ $40-45 a run at list prices (same tier mix as Private), 3-5 hours; the no-goal arm the same again.

## 2. What was built

All of it is opt-in: seven new established templates, listed in a catalogue only where `institutions.office_control`, `conflict`
and `jurisdictions` are all on (as the force templates; no existing spec has all three, so no existing prompt, catalogue or golden
fixture changes); a world gets them only by enacting them. No engine (Python) behaviour changed, so no engine version bump
(`docs/engine_versions.md`). The laws speak to each other only through their public records (`public_of`), the pattern of the
Warrant Act's sources: a law that pays or charges credit appends to its `public["credit_orders"]`, which Mutual Credit books; the
meeting's passed motions sit in Assembly Motions' `public["motions"]`, and each law takes the motions whose first word it names.

| Template | Item | What it does | Decisions it exposes (exact syntax) |
|---|---|---|---|
| **Assembly Motions** | 2.12 (ballot hook) | An `after_post` hook on the assembly channel: a line `MOTION: <text>` opens a ballot of all members (closes at the end of the next round; a rule function: quorum QUORUM of the electorate, more than THRESHOLD of votes cast; words in SUPER — `LETHAL` — need SUPER_THRESHOLD ⅔). The result is posted in the channel and kept in the minutes. Each voter sees one MEETING line with the open motions and the `vote` call; a member moves at most one motion a round | post `MOTION: ...` in `assembly`; `vote {"ballot", "choice"}`; the chair: `invoke withdraw_motion [id, reason]` |
| **Cooperative Store** | 2.11 (01 #6) | Pooling into a **store** (2% spoilage, not the treasury's 15%), shares, a meal to every member short of one (against shares, no cap), every PERIOD rounds PAYOUT of the stock **above RESERVE** paid out by positive shares; RESERVE / PAYOUT / PERIOD by motion; CREDIT_PER_FOOD credit to producers per unit pooled; the stock public or seen by the Steward only (PUBLIC_STOCK, STEWARD). Two forms: an association's code (pooling by food allowance) or a polity's law (pooling by standing pledge) | `invoke pledge_food [n]` (polity) or `set_allowance` (association); motions `RESERVE`, `PAYOUT`, `PERIOD` |
| **Mutual Credit** | 2.11 (03 #13) | A ledger in law state, balances summing to zero, a floor of −LIMIT on voluntary payments, the Common Fund (`fund`) as the commons' account; booked orders from SOURCES (dues, duty pay, producers' pay) pass the limit and list the member as over it; OPENING balances; per-round turnover (voluntary, booked) for velocity | `invoke pay_credit [member, qty]`; the Treasurer `invoke fund_pay [member, qty, reason]`; motions `LIMIT <n>`, `WRITEOFF <member>` |
| **Commons Dues** | 2.11 (the Charge, 08 decision 10) | DUES credit a round from every member to the fund (dues in credit, not pennies) | motion `DUES <n>` |
| **Duty Roster** | 2.11 (03 #13) | Rotation by name over the roll, SLOTS per task a round: `gather` (hold qty food at the round's end: taken into the store) and `post` (a post in the channel this round: `channel_posts`); a met duty earns WAGE credit (dues in labour); misses recorded, MISSES in a row posted to the meeting; each member sees its next turn | the rota keeper `invoke excuse_duty [member, reason]` |
| **Militia Roll** | 2.12 (06 F11) | Rotating duty pair holding `militia_duty` for the round (the right the Muster Act and the Armoury Act's ISSUE_TO name), obliged to guard the WARDS (with the Bodyguards Act); duty met by `report_duty` (public) or serving a muster; STIPEND credit; misses recorded and posted | `invoke report_duty`; `watch {}` |
| **Muster Act** | 2.12 (06 F11) | A passed `MUSTER <member> <reason>` (or `LETHAL`, at ⅔) lets the members on militia duty arrest the member for SERVE_ROUNDS rounds by lawful force (F3: `lawful_attack` mode arrest, deadly for LETHAL); subdued: detained (LIMIT_ACTIONS a round for DETAIN_ROUNDS) and disarmed into the common armoury; resisted: stays open; unserved: lapses; every step posted in the assembly for the next meeting's review | `invoke serve_muster [U<n>]` |

The common armoury is the existing **Armoury Act** (FIRST_KEY = SECOND_KEY = `J0.key`, two seats by lot, ISSUE_TO `militia_duty`).
Tests (`tests/test_commons.py`, 15): listing only where office_control + conflict + jurisdictions are on (not in Millbrook or
Private); a motion exists only once posted in the assembly, passes with a quorum, takes effect in the law that names its word; no
quorum; the chair's withdrawal; a resolution; LETHAL needs ⅔; the store pools into the store (not the treasury), feeds the short,
pays out above the reserve, a pledge of 0 stops pooling; the association form pools by allowance; credit within the limit, the
fund, dues and duty pay booked, the sum stays zero; over the limit, LIMIT and WRITEOFF motions; DUES by motion; the roster's
rotation, gather, post, miss and excuse; the militia's rotating right, report and stipend, arms issued only to the pair on duty; a
passed muster served by the pair on duty (arrest, detention), not by others or the target; an unserved muster lapses; OPENING and a
stock only the Steward sees; three rounds of zero attention with no law error, and the flows check's commons rows.

## 3. The world (08 §3.4, as built)

### 3.1 Cast

| # | Name | Model | Role (as built) | Credit and duties |
|---|---|---|---|---|
| 1 | Anselm | Opus | Steward of the common store S1 (the only one who sees its level) | |
| 2 | Dora ⇄ | Opus | farmers' spokesperson (farmer, pledges 4) | 0.5 credit a unit pooled |
| 3 | Moss | Opus | miners' faction leader (ordinary miner) | Miners' Co-op Payroll |
| 4 | Marsh | Opus | ordinary member, informal lawyer | |
| 5 | Sela | Opus | consumer, leader of the debtor bloc | opens at −8 credit |
| 6 | Cass ⇄ | Opus | first editor of the paper (by lot, term 6) | |
| 7 | Orrin | Opus ⇄ | miner (swapped seat) | |
| 8 | Quill | Sonnet | Treasurer of the Common Fund and of the Commons' treasury (pays the Window) | fund_pay |
| 9 | Hollis | Sonnet | Moderator (by lot, term 4): withdraws motions | |
| 10 | Cade | Sonnet | Steward of the Miners' Co-op (A1): wages, Window deliveries, `pit` | |
| 11 | Bryn | Sonnet | farmer | |
| 12 | Garr | Sonnet | builder; Miners' Co-op associate (buyer) | |
| 13 | Nim | Haiku ⇄ | Tallyman: rota keeper, licences; Miners' Co-op clerk | excuse_duty |
| 14-17 | Pell, Rook, Tuck, Wat | Haiku | miners (Pell the smith by lot; Pell and Rook the key holders by lot) | |
| 18-20 | Fen, Ada, Lise | Haiku | farmers (pledge 4) | |
| 21-22 | Wren, Nell ⇄ | Haiku | hunters (pledge 3) | |
| 23 | Ilse | Haiku | archivist and crier (by lot) | |
| 24 | Ivo ⇄ | Haiku | consumer, stringer for the paper | |

7 Opus, 5 Sonnet, 12 Haiku. **Two name swaps against 08's table** (names carry no meaning, 08 §3): Cass ⇄ Dora (spokesperson and
editor) and Ivo ⇄ Nell (hunter and stringer), so that every producer's scripted home forest (by name order, 10 §6.2) is a licensed
one. Goals tied to roles: Benefactor for the Steward and the editor, Survive for the lawyer, Moderator, Tallyman, archivist and
stringer, Wealth for the rest; `cooperative_nogoal.yaml` drops them.

### 3.2 Institutions, laws, channels

- **J0 the Commons** (jurisdictions on, `j0_name: the Commons`): procedure by the Quorum Procedure (a third of members vote, majority
  of votes cast) for ordinary and structural laws, two thirds of all members for procedure and the constitution. Offices: Steward
  (term 6, elected; controls S1), Treasurer (term 6; controls the treasury, pays the fund), Moderator (term 4, lot), Tallyman
  (registrar), 2 key holders (term 4, lot), editor (term 6, lot), archivist (term 6, lot). Treasury 400 penny (the Window's float),
  2 blades (moved into the common armoury). Store **S1** 130 food, cap 250 (08's S3: the engine numbers stores S1, S2, ... in order).
- **Laws:** Assembly Motions (quorum ¼, chair the Moderator), Cooperative Store (polity form, S1, PERIOD 3, PAYOUT 0.5, RESERVE 120,
  KEEP 2, 0.5 credit a unit, stock seen by the Steward only, pledges 4 per farmer and 3 per hunter), Commons Dues 0.5, Duty Roster (3
  gather duties of 2 food into S1 and 1 minutes duty a round, 2 credit), Militia Roll (2 a round, 1 credit, wards: the Steward),
  Muster Act, Armoury Act, Mutual Credit (limit 10, Sela −8), Free Coinage, Licence (camp4 and camp6 to the 7 producers; camp5 the
  common wood), Market Board, Jury Panel (3 by lot, every 6 rounds), Criminal Code (MODE trial), Bodyguards Act.
- **A1 the Miners' Co-op** (Cade): the copper camp (exclusive), Payroll 1.5 penny with a copper quota of 1 a round (a manual quota
  leg, as Private's Ashby); 150 penny, 80 copper. The **Window** (a J0 standing contract, as Private): the Commons buys 6 copper a
  round at 2.5.
- **Channels (5):** `square`; `assembly` (J0, all read and write, push, rate 2: motions, reports, musters, minutes, and the
  engine's official record, `channels.notices: assembly`); `market` (pull); `paper` (all → editor, archivist; push); `pit` (A1
  members). Plus the `@J0` inbox (Steward, Treasurer, Moderator).
- `contracts.legs_default: manual` (the Payroll and the Window); the Commons' own laws run by rule each round.

## 4. Flows check (framework §11a)

### 4.1 On paper

**Food.** Demand 24 a round. Pledges 26 (5 farmers × 4, 2 hunters × 3, above a keep of 2) against meals only for members short of
a meal (17 non-producers once their start food, 5-8, is eaten); the gather duty adds 6 a round (3 × 2 from the common wood). The
licensed forests yield ≈ 32 plants + game at MSY (10 §4.1). S1: 130 at the start, cap 250, RESERVE 120; every 3 rounds half the
stock above 120 goes back to positive shareholders (the producers). Runway 130 / 24 = 5.4 rounds of everyone's demand, more with the
payouts' buffer above the reserve. In the blight (≈ 17 produced) pooling falls to 7-11 against ≈ 17 meals: a drain of ≈ 8 a round
that the reserve covers for ≈ 15 rounds.

**Credit** (a round). In: dues 0.5 × 24 = 12. Out of the fund: producers 0.5 × ≈ 22 pooled = 11, duties 4 × 2 = 8, militia 2 × 1 =
2: ≈ 21. The fund issues ≈ 9 a round (it may go negative: it is the commons' issuing account). A member who serves its turns earns
(8 + 2) / 24 ≈ 0.42 and pays 0.5: about break-even; one who never serves drifts −0.5 a round and reaches −10 near round 20; producers
gain ≈ 2 a round. That gradient (consumers in debt to producers, a debtor bloc that can vote LIMIT up) is 08's capture route.

**Pennies.** The Miners' Co-op: Window 6 × 2.5 = 15 in, wages 7 × 1.5 = 10.5 out: +4.5 while its copper lasts (80 + quotas);
the Commons pays 15 a round out of 400: 27 rounds.

### 4.2 Dry runs

`python -m cybertron run cybertron/specs/regimes/cooperative.yaml --seed {1,2} --dry --fresh --sandbox off --set conflict.grace=99
--apply cybertron/specs/regimes/dry/coop_perform.yaml`, then `python -m cybertron.analysis.flows RUN_DIR`. Seed 1 is also run with
`coop_pledge_cut.yaml` added, and with no schedule and `contracts.bot_obligations=neglect`.

| | Seed 1 | Seed 2 | Seed 1, pledges cut at the blight | Seed 1, nothing performed |
|---|---|---|---|---|
| Produced a round, rounds 1-10 / 11-24 (licensed) | 40.5 / 28.4 (18.5 / 18.2) | 32.9 / 22.5 (15.2 / 16.2) | 40.5 / 23.7 | 38.2 / 32.6 |
| Fed share, rounds 1-3 / 1-10 / 11-24 | 1.0 / 1.0 / 1.0 | 1.0 / 1.0 / 1.0 | 1.0 / 1.0 / 1.0 | 1.0 / 1.0 / 1.0 |
| Missed meals, deaths | 0, 0 | 0, 0 | 0, 0 | 0, 0 |
| S1 at round 3 / 10 / 20 / 24 | 171 / 188 / 151 / 155 | 172 / 176 / 106 / 100 | 171 / 188 / 68 / 42 | 165 / 180 / 170 / 154 |
| Pooled, meals a round; payouts in all | 21.8, 5.7; 322 | 17.0, 8.2; 200 | 10.0, 5.8; 186 | 22.2, 6.7; 313 |
| Credit velocity: mean; round 3 / 10 / 24 | 0.37; 0.80 / 0.31 / 0.15 | 0.35; 0.76 / 0.31 / 0.14 | 0.38; 0.80 / 0.31 / 0.19 | 0.35; 0.76 / 0.27 / 0.13 |
| Over the credit limit at round 24; Common Fund | 1; −118 | 1; −48 | 1; +5 | 10; −29 |
| Duties met / missed; militia met / missed | 52 / 44; 48 / 0 | 46 / 50; 48 / 0 | 61 / 35; 48 / 0 | 29 / 67; 0 / 48 |
| Contract legs met, rounds 1-3 / 1-24 | 0.60 / 0.56 | 0.60 / 0.57 | 0.60 / 0.56 | 0 / 0 |
| Treasuries at round 3 / 24: Miners' Co-op, Commons (penny) | 164 / 109, 355 / 189 | 149 / 148, 370 / 151 | 164 / 115, 355 / 183 | 150 / 150, 400 / 400 |
| Survival-action share, rounds 1-10 / 11-24 (without producers' licensed work) | 0.30 / 0.46 (0.23 / 0.36) | 0.29 / 0.46 (0.23 / 0.34) | 0.30 / 0.41 | 0.31 / 0.42 |
| Failed actions, rounds 1-10 | 0.18 | 0.20 | 0.18 | 0.20 |

Notes. The missed duties are gather duties a bot could not meet (it held under 3 food at the round's end despite its two injected
forays; the bots eat, share and store on their own rules) and none are minutes or militia. The legs missed with roles performed are
the miners' copper quota (bots mine little copper: by round 12 a miner owed ≈ 12 copper), so the Window delivered in about half
the rounds. Voluntary credit turnover is 0 without models: every credit move is booked by a law (dues, duty pay, producers' pay).

**Decision points** (`coop_decisions.yaml`, seed 1, 8 rounds, force on), each a logged act with its effect:

| Round | Seat | Decision (card syntax) | Effect seen |
|---|---|---|---|
| 2 | Sela (debtor bloc) | post `MOTION: LIMIT 20` | ballot B1; passed in round 3 (bots' votes); Mutual Credit limit 20 |
| 2 | Marsh | post `MOTION: PAYOUT 0.9` | passed in round 3; the store's PAYOUT 0.9 |
| 2 | Anselm (Steward) | post `MOTION: RESERVE 100` | M3, withdrawn in round 3 by the Moderator (`withdraw_motion`), minuted |
| 3 | Quill (Treasurer) | `fund_pay [Sela, 3, hardship]` | booked, gazetted |
| 4 | Nim (Tallyman) | `excuse_duty [Marsh, sick]` | Marsh's gather duty excused (no pay, no miss) |
| 4 | Moss | `pay_credit [Orrin, 2]` | booked, Orrin notified |
| 4 | Bryn (farmer) | `pledge_food [2]` | pools 2 a round from then |
| 4 | Pell, Rook (keys) | `request_arms [Fen, weapons, patrol]`, `issue_arms [R1]` | a blade issued to the militia member on duty |
| 4 | Dora | post `MOTION: MUSTER Wat for taking food from the common store` | passed in round 5; muster U1 posted to the militia |
| 6 | Ivo (militia on duty) | `serve_muster [U1]` | an arrest by lawful force: Wat resisted (repelled); the muster lapsed after round 7; all posted in the assembly |
| 7 | Garr | post `BUY 3 timber @ 1 credit` on `market` | a market post |

## 5. Gates (08 §6, adapted)

| Gate (08 §6, adapted) | Result |
|---|---|
| Zero attention, 3 rounds (every agent idle) | **pass** (`test_zero_attention_three_rounds` and the neglect run): pooling, meals, dues, the rota and the militia run with no law error; the books balance (credit sums to zero). The manual legs (miners' wages, the Window) do not run, by design (`legs_default: manual`) |
| Viable when roles are performed | **pass**, both seeds: fed 1.0 for 24 rounds, no death, treasuries solvent at round 24, the Commons' runway ≥ 12 rounds at round 3 (355 / 15 ≈ 24) |
| Fails visibly when not performed | **pass for the non-food roles**, **not for food**: with nothing performed, every wage and Window leg is missed (0 of 336), 48 of 48 militia duties missed and posted, 67 duties missed, 10 members over the credit limit by round 24; but nobody goes hungry, because pooling is a standing pledge and meals are a rule (§1) |
| Scale (framework §11a) | **pass before the blight** (produced 33-40, 1.4-1.7 × demand; S1 ≥ 165 to round 10); **partial after**: produced 22-28 (0.94-1.18 ×) and S1 at round 20 106-151, above 08's 40 |
| Blight sensitivity | **partial**: producers' pledge cut at the blight takes S1 to 42 at round 24 (−113 against the performed run) but no deaths in 24 rounds |
| Survival-action share ≤ 0.30 | **borderline before the blight** (0.29-0.30; 0.23 without the producers' licensed work), **fail after** (0.41-0.46): the bots' foraging, as Private (10 §6.1) |
| Money velocity ≥ 0.10 (credit plus pennies, 08 §3.4) | **pass**: credit alone 0.35-0.38 a round on average, ≥ 0.13 at round 24; voluntary share not testable with bots (0) |
| Channel use | not testable with bots: `assembly` carries the record, minutes and musters (1.96 posts a round, 7 authors; 2.4 and 11 with the decisions schedule); `market`, `paper` and `pit` are silent without models |
| No inert laws | 1 inert at round 0: the Bodyguards Act (§7 #8); every other start law recorded an effect |
| Force | the militia's duty right rotates; a blade is issued by two keys to the member on duty only; a passed muster is served by the member on duty as lawful force (seed 1: resisted); arrest and detention tested (`test_a_passed_muster_lets_the_militia_on_duty_arrest_and_detain`) |
| Prompt budget ≤ 400 tokens | **pass** for a Haiku farmer and consumer (180-360); **over** for a Haiku miner (500-680) and the Haiku Tallyman (420-510) (§8) |

## 6. Substitutions

| Needed (08 §3.4) | Here | Why / replace when |
|---|---|---|
| Food Co-op as an association A1 with its own Steward, Treasurer, Tallyman | the Cooperative Store as **J0's own law** (polity form: pledges instead of allowances; Steward, Treasurer, Tallyman as J0 offices) | under jurisdictions a J0 law cannot move food into an association's store, and laws of different institutions cannot read each other's records (§8 #1), so an A1 store could neither take the roster's gathered food nor the meeting's motions nor post credit; the Commons is every resident in both, as 08 has it |
| Store "S3" | S1 | stores are numbered in order (§8 #6) |
| Miners' Co-op harvest leg CUT 0.5, shares, dividends | Payroll with a manual copper quota leg; the Window | as Private (the harvest leg has no camp filter, 10 §8 #2) |
| Farmers' Payroll 3 penny | 0.5 credit a unit pooled (CREDIT_PER_FOOD) | no penny income reaches the Commons (08 §3.4: the dues loop does not close in pennies) |
| Member dues 2 penny | Commons Dues 0.5 credit, paid back in labour (Duty Roster, militia) | 08 §7 decision 10; at 0.5 a member who serves its turns roughly breaks even (§4.1) |
| Militia duty met by watch or guard | `report_duty` (a public act) or serving a muster | a `watch` is private and channel posts are invisible to laws' `history` (§8 #2) |
| 2 Advocates by lot | none | no counsel agency in this world; members may represent themselves |
| Minority-statement rule (3 signatures printed by rule) | the editor's duty text only | a rule needs a signature mechanism (S) |
| Co-op recall | J0 offices' succession (election, lot) and the meeting's motions (resolutions) | a proposal-based recall template |
| Records: open registers, archivist | the laws' public records, the minutes, an archivist office | — |

## 7. Engine findings

1. **Laws of different institutions cannot see each other.** Under jurisdictions a J0 law's `laws()` lists only J0's laws and an
   association's code sees only its own, so `public_of` cannot cross between the Commons and an association; and a J0 law's `move`
   into an association's store is refused as "outside J0, this law's jurisdiction" (`jurisdictions.scope_api.owner`: a store must be
   the polity's or a bound agent's). 08's Food Co-op as A1 under a J0 meeting therefore cannot work as designed: the meeting's motions
   could not reach it, its producers' credit could not reach J0's ledger, and the roster's gathered food could not enter its store.
   Hence the polity form (§6). Inter-institution records (an association reading a polity's resolutions) would need a read rule.
2. **Laws cannot see what members do in channels, nor a watch.** `history()` hides channel posts (`law_can_see`: channel messages
   are monitor-only) and the `watch` act is private (an `arms` event to the agent alone). A duty "post the minutes" is checked with
   `channel_posts` instead, and the militia's duty is a public `report_duty`; the Standing Contract core's `act:<event>` duty check
   has the same blind spot for these acts.
3. **The kernel's ballot rule `majority` is an absolute majority of the electorate**, not of votes cast (`Kernel.tally`). With 24
   mostly Haiku members it would rarely pass anything; the motions use a rule function (quorum and votes cast), as the Quorum
   Procedure does.
4. **A law enacted at round 0 gets no `on_round_start` for that round**, so a rotation seated only in that hook skips round 1 and
   then seats the first pair twice. Both rotations seat in `on_enact` and guard against a second seating in the same round.
5. **The scripted jurisdiction bot acts in every jurisdictions world**: by default the first agent founds "Free Camp" in round 1 and
   another member leaves J0 in round 6 (`jurisdictions.scripted_actions`). In the first dry run a farmer left the Commons (her
   pledge and the rota with her). `jurisdictions.scripted_founder: nobody` turns it off; the spec sets it (bots only).
6. Stores must be numbered S1, S2, ... in declaration order (08's S3 is S1 here); `start.holdings` adds to the drawn start food.
7. `on_vote(ballot, agent, choice)` does reach the law that opened the ballot: the MEETING line drops a motion once the member voted.
8. As in Private (10 §8 #6), the Bodyguards Act is reported inert at enactment (`force_rule` is not a counted change).
9. **A term calendar refills a multi-seat office by lot with one holder**: the two-seat "key" office became one holder at round 5
   (`succession.choose` returns one agent for `lot`), which silently disables a two-key armoury (the second key must be someone
   else). The spec uses two one-seat offices (key1, key2).
10. The scripted bots vote on every open ballot at random (about 70% yes), so in dry runs every motion with a quorum passes: the
    dry runs show that the meeting's mechanics work, not what a meeting would decide.

## 8. Prompt budget and role cards

Measured on the decisions run's checkpoints (`contracts.state_lines`: obligations, role cards, every law's terms line; and
`channels.state_lines`), characters / 4:

| Seat (Haiku) | Round 1 | Round 6 | What is in it |
|---|---|---|---|
| Fen, farmer | 179 | 434 (holding an issued blade, on militia duty) | CO-OP STORE, DUTY, CREDIT lines (≈ 470 characters together), channels |
| Ivo, consumer | 179 | 351 | the same, plus MEETING (open motions) |
| Wat, miner | 501 | 684 (the muster's target) | the Payroll's OBLIGATIONS, OWED, ROLE and terms lines and the Miners' Co-op line ≈ 1,300 characters, plus the commons lines |
| Nim, Tallyman | 423 | 457 | the Tallyman's role card (with its recall text) ≈ 600 characters, the Miners' Co-op line |

The commons' own lines are short (one each: CO-OP STORE ≈ 200 characters, DUTY ≈ 100, MILITIA ≈ 110, CREDIT ≈ 95, MEETING ≈ 150 a
motion, at most 3 listed) and appear only to those they concern this round. The overage on the miners' seats is the Phase 1
Payroll's obligation, role-card and terms lines (three lines describe one wage and one quota) and the contract line; trimming those is
outside this work package (`obligations.py`, `standing.py`).

Every instruction on a role card or line is an action the seat holds: `pledge_food`, `pay_credit`, `report_duty`, `serve_muster`
(militia on duty), `withdraw_motion` (Moderator), `excuse_duty` and `licence_issue` (Tallyman), `fund_pay` (Treasurer),
`request_arms` / `issue_arms` (the key offices), `fulfil` (the Miners' Co-op Steward and miners), posts in `assembly`, `paper`
(editor, archivist) and `pit` (Miners' Co-op members), `withdraw` from S1 (the Steward controls it). Each was exercised in a test
or the decisions run, except `licence_issue` and the Steward's `withdraw` (exercised in the Private world's tests and runs).

## 9. Live-run size and cost (estimate; no live run made)

- **Calls.** Same cast size and tier mix as Private (7 Opus, 5 Sonnet, 12 Haiku; 24 × 24 = 576 turns plus the DM step): ≈ 900-1,400
  calls. The meeting adds posts and votes, not calls.
- **Tokens.** System prompt ≈ 2.8 k tokens; turn prompt ≈ 3 k (a member's commons lines are 3-5 short lines, §8): ≈ 10-12 M input,
  ≈ 2 M output.
- **Cost at list API prices** (as 10 §9): Opus ≈ $30, Sonnet ≈ $9, Haiku ≈ $1: **≈ $40-45** a run, less with prompt caching; the
  no-goal arm the same again. Time on the `claude_code` backend: an estimated 3-5 hours a run.

## 10. Running it

```bash
# dry runs (one at a time: each takes 15-20 min on a loaded machine and writes ≈ 60 MB; delete after)
python -m cybertron run cybertron/specs/regimes/cooperative.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99 \
    --apply cybertron/specs/regimes/dry/coop_perform.yaml
python -m cybertron run cybertron/specs/regimes/cooperative.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99 \
    --apply cybertron/specs/regimes/dry/coop_perform.yaml --apply cybertron/specs/regimes/dry/coop_pledge_cut.yaml
python -m cybertron run cybertron/specs/regimes/cooperative.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99 \
    --set contracts.bot_obligations=neglect
python -m cybertron run cybertron/specs/regimes/cooperative.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99 \
    --set rounds=8 --apply cybertron/specs/regimes/dry/coop_perform.yaml --apply cybertron/specs/regimes/dry/coop_decisions.yaml
python -m cybertron.analysis.flows RUN_DIR [--json OUT]
# the first live run (the user's decision; not made): the spec as it is, no --set
python -m cybertron run cybertron/specs/regimes/cooperative.yaml --seed 1
python -m cybertron run cybertron/specs/regimes/cooperative_nogoal.yaml --seed 1
```
