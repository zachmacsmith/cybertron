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

RESULTS_SUMMARY

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

FLOWS_PAPER

### 4.2 Dry runs

DRY_RUNS

## 5. Gates (08 §6, adapted)

GATES

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

ENGINE_FINDINGS

## 8. Prompt budget and role cards

BUDGET

## 9. Live-run size and cost (estimate; no live run made)

COST

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
