# Review 31.13: the Merchant world, "individuals and a weak assembly", and the Phase 2 mechanisms it needs

*20 Oct 2026. Branch `wp/merchant-world` (from `subsistence`). Build plan items 2.1, 2.13, 2.14 and the Merchant part of 2.15
(08 §5): the Bank Charter and a role-restricted procedure, the Commission (guard-only), Arbitration through an Arbitrators' Hall,
Charge as subscription, the wound bounty, the Security Licence, and the Merchant world of 08 §3.2 with a flows check and scripted
dry runs (2 seeds, 24 rounds) against the 08 §6 gates. No live (model) run has been made. Scripted bots are weak evidence: the dry
runs below prove wiring and viability while roles are performed; they were not used to tune behaviour.*

Files:
- `cybertron/library.py`, block `# ===== merchant (review 31 Phase 2 ...)` at the end: Bank Charter, Role Procedure, Arbitrators'
  Hall, Wound Bounty, Security Licence.
- `cybertron/standing.py`: two small core additions (a `bond` leg; `FORUM: arbiter:<institution>`; terms that name an agent) and a
  `# ===== merchant` presets block: Commission, Paper Subscription.
- `cybertron/specs/regimes/merchant.yaml`, `merchant_nogoal.yaml`; dry schedules `dry/merchant_decisions.yaml`,
  `dry/merchant_release.yaml`.
- `cybertron/analysis/flows.py`: `--all-stores` (the Merchant world's stores belong to agents).
- `tests/test_merchant.py` (15 tests).

## 1. Summary

- **Every mechanism is built, opt-in and tested.** Nothing changes for a world that does not name them; the existing standing
  contract, force, courts and regime suites pass unchanged (277 tests) with the core additions in place.
- **The Merchant world is built and runs** (24 agents, 7 Opus / 5 Sonnet / 12 Haiku, 5 counted channels, 17 seeded standing
  orders in one Order Book, an Arbitrators' Hall, two subscription papers, a Commission, a Retainer, Velma's four seeded loans).
- **Viable while roles are performed:** both seeds feed everyone for rounds 1-3 (contract legs met 0.87-0.88) and keep the fed
  share ≥ 0.96 until round 7-11. **It then degrades by design, not by physics:** output stays above demand throughout (1.1-1.4×),
  but customers run out of pennies around round 9-11 (the 25-penny purse 08 §3.2 flagged: the bots never sell labour or goods),
  producers' orders miss when the bots under-forage, and the dealer's store sits shut. 4-6 deaths by round 24.
- **Money gate fails, as 08 said it would:** velocity 0.05 (both seeds), voluntary share 0.83-0.84, hoard ratio 0.30-0.38
  (0.54-0.74 at the end). Reported, not forced.
- **Prompt budget fails for most Haiku seats:** registers + contracts + channels lines are ≈ 400 tokens for a hunter with one
  order, ≈ 550-700 for a farmer or customer, ≈ 1,000 for the Registrar (§5.7). Every action the cards name was executed on a copy of
  the kernel: all literal calls work; the only failures are placeholders (`<id>`) and the DM limit already used that round.

## 2. Mechanisms

| Item | What it is | Where | Tests |
|---|---|---|---|
| 2.1 **Bank Charter** | An association's code. Every member is a customer. A deposit is `deposit_escrow` of the coin with the bank: swept into the bank's cash and credited to the customer's account (`after_deposit_escrow`, and a sweep each round). `withdraw [qty]` pays cash at once, or queues the claim first-come-first-served (gazetted "the bank cannot pay") when cash is short or withdrawals are suspended; the queue is paid as cash comes in. `pay [to, qty]` moves deposit money between accounts. The banker's `lend [borrower, qty, rounds, rate, collateral item, qty]` is an offer; the borrower's `take_loan [offer]` **credits its account** (deposit money: the bank lends more than its cash) only while cash ≥ MIN_RESERVE × deposits, and pledges collateral kept in escrow (any goods but the coin). Instalments come from the account, else the allowance; more than GRACE misses → default: collateral forfeited to the bank and a public breach. `set_rate` (deposit interest credited to accounts), `suspend [true|false]`, the teller's `pay_queue`. Public: cash, deposits, loans out, reserve ratio, queue, suspension, the loan book. One terms line per customer. | library.py | deposits/withdrawals/payments; lending beyond cash within the reserve, refusal below it, a run queued and paid, suspension; instalments, default and forfeit; repayment releases collateral |
| 2.1 **Role Procedure** | `set_procedure` for an association: only holders of the VOTERS offices vote on its code (depositors, customers, subscribers do not); one voter proposing alone adopts; no voter in office → the founder. | library.py | a depositor's proposal goes to a ballot of the banker and teller only; the sole banker adopts; a non-voter's proposal fails |
| 2.13 **Arbitration** | `FORUM: "arbiter:<institution>"` on any standing contract: a breach's claim (with its cap: the contract's PENALTY) is published in the contract's public record; the **Arbitrators' Hall** (an association template) builds its docket from every contract naming it, and its arbiters `award [claim, qty, reason]` or `dismiss`; an arbiter who is a party cannot rule. The contract carries out the ruling at the end of the round from the losing party's bond, with the hall's FEE moved to the hall's treasury. The award register is public. `arbiter:<agent>` (the old form) is unchanged. | standing.py core (`hall`, `settle_rulings`, `show_claims`); library.py | a would-not breach reaches the hall's docket and the arbiter's state line; parties can no longer self-award; the award and the fee are paid; recusal |
| 2.13 **Commission** (guard-only) | A bilateral preset: the hirer's fee sits in its escrow (BOND); leg G is a `guard` duty (sword → client), leg P releases `fee` per guarded round out of the hirer's escrow (the new **`bond` leg**: never manual, it is the record of a performed duty, not labour). Unguarded rounds are not paid; at TERM what is left goes back; exit without notice costs EXIT_FEE. No strike leg exists (08 §7 decision 9). | standing.py presets block | nothing released while unguarded; 2 per guarded round; refund and the sword's bond at term |
| 2.13 **Charge as subscription** | The **Paper Subscription** preset: a roster in the paper's code; each subscriber pays `fee` a round into its treasury; a subscriber who would not pay past GRACE is expelled, so it stops reading (channel readers `{members: <paper>}`); the editor enrols an applicant (`sub_enrol`) and sets the fee (`sub_fee`). A subscriber who *could* not pay is told, not expelled (core rule: could-not is never a breach). | standing.py presets block | auto: the editor is not charged, a would-not subscriber is expelled, a new reader is enrolled; manual legs: fulfil pays, a holder who does not pay is expelled |
| 2.13 **Wound Bounty** | Bounty on Aggressors that also pays for a wound (most harm outcomes): BOUNTY_WOUND / BOUNTY_KILL from the treasury, CAP a round, covert attacks earn nothing; public list. | library.py | a wound on an earlier aggressor is paid |
| 2.14 **Security Licence** | J0 law: the REGISTRAR licenses or revokes a firm; holders of the firm's GUARD_OFFICES (or all members) hold `licensed_guard` and may `detain [target, reason]`: an F3 arrest (`lawful_attack` mode arrest) of an agent who attacked unlawfully within LOOKBACK rounds (TARGETS aggressors), the target then limited for LIMIT_ROUNDS; public register and detention log. Needs conflict + jurisdictions (listed only there, like the force templates). | library.py | guards get the right on licensing, lose it on revocation; a non-aggressor is refused; an aggressor is subdued |
| core: **terms naming an agent** | `enrol` and `set_term` accept an agent's name for a term whose default is text (the Order Book's `seller`; it also lets a Service guard be reassigned, the limit 31.08 noted for 1.3). Numeric terms behave as before. | standing.py | enrol with a producer; a number is refused for a name term |

Everything is opt-in: the core additions act only on a leg with `bond`, a FORUM naming an institution, or a text-valued term; the
templates exist only where named. The templates are listed in `read_library` wherever `institutions.office_control` and
`contracts` are on (as the other established templates; Security Licence also needs conflict and jurisdictions). No default
flipped, so no engine version bump.

## 3. How the Bank Charter replaces the Private world's moneylender (not edited here)

In `private.yaml` Sela is a moneylender with a purse and kernel loans (Loan Registry). The swap:
1. Add an institution `A7 the Bank` (founder Sela; offices `banker` = Sela with `controls: [treasury]`, `teller` = a Haiku clerk;
   admission open; **no `procedure:` key**, because `start` sets the procedure after the laws are enacted and would overwrite the
   Role Procedure); `laws: [{template: Bank Charter, params: {MIN_RESERVE: 0.2, DEPOSIT_RATE: 0.01, GRACE: 1}}, {template: Role
   Procedure, params: {VOTERS: [banker]}}]`; `treasury: {penny: 60}` (Sela's purse becomes the bank's capital).
2. Depositors: the cast's "depositor of #4" seats (Hale, Bryn, Lise) join A7 and get a `start.escrow` of pennies (swept into
   their accounts at round 1); borrowers (Dace) get an offer at round 1 via the role card (`A7.lend`), or a seeded offer.
3. Firms that bank there pay wages from the treasury as now; a worker paid into an account is a later step (Payroll paying
   `assoc:A7` with a `pay` per worker is not built).
4. Keep the Loan Registry for agent-to-agent loans; the Bank's book is its own public record (an association cannot be a kernel
   lender), so the analysis reads `public.loans` and `public.figures` of the Bank Charter law next to `credit` records.
5. The Bank goal (`goals.explicit Sela: Bank`) scores kernel loans; it would need a variant reading the charter's book.

## 4. The world (08 §3.2 as built)

Cast as 08 §3.2, with one swap: 08's farmer **Edda** and miner **Bram** trade roles and tiers (the scripted bots' home forest is
`forests[position % 3]` in name order; with the swap all 7 producers sit on the two licensed forests camp5 and camp6, camp4 is the
common wood). Names carry no meaning across worlds (08 §3).

| Institution | Built as |
|---|---|
| J0 Assembly of Citizens | Quorum Procedure (all `vote` holders, quorum 0.5) for every class and rank; offices Magistrate (Hollis, `judge`; Graded Remedies on `tort`, Bench Act), Registrar-notary (Ivy: Licence register, Certified Contract Registry, notices), Speaker (Garron: the agenda on notices) |
| Money | Free Mint (penny convertible; J0 reserve 200 timber, 150 stone, 120 copper, 60 penny), Payment Levy 2%; Loan Registry (in J0's institution laws so `start.loans` can seed Velma's four loans to Ilse, Odo, Edda and Hollis) |
| Food | Licence on camp5, camp6 for the 7 producers; the dealer's store S1 (Dorin, 60/150); five farmer pantries S2-S6 (12/40); **A1 the Order Book**: one roster standing contract, 17 orders (customer-keyed; `seller` in each customer's terms), 1 food for 2 pennies, manual legs, bonds (3 a producer, 2 a customer), FORUM `arbiter:A2` |
| Law | **A2 the Arbitrators' Hall** (Marsh, fee 1); Criminal Code MODE auto (pennies 3/6/10); Wound Bounty (4/8, cap 12); Bodyguards Act; Market Board |
| Press | **A3 the Ledger-Sheet** (Ansel editor, Dorin partner, 7 subscribers) and **A4 the Courier** (Bea, 7 subscribers): Paper Subscription at 1 penny |
| Force | **A5 Commission** Dorin → Brand (2 a guarded round, 24 in escrow, term 12); Brand and Rafe armed; no public force but the bounty |
| Counsel | **A6 Retainer** Velma → Marsh (1.5): the creditor retains the arbiter |

Channels: `square`, `market` (pull, followed by all), `notices` (pull; Registrar and Speaker write; the engine's record),
`ledger-sheet` and `courier` (readers: the paper's members), plus inboxes. Settings as Private (law.v2, institutions on,
`contracts.legs_default: manual`, obligations and role cards, `enforcement: escrow`, conflict harm, the same forests and blight).

## 5. Flows check and dry runs

`python -m cybertron run cybertron/specs/regimes/merchant.yaml --seed {1,2} --dry --fresh --sandbox off --set conflict.grace=99`,
then `python -m cybertron.analysis.flows RUN --all-stores` and `python -m cybertron institutions RUN`.

### 5.1 On paper (08 §3.2)

Demand 24: 17 through standing orders, 7 producers eat their own. Output ≈ 33 at two forages a producer; orders take 17; stores
120 at start (S1 60 + 5 × 12). Money: the 17 orders move ≈ 34 pennies a round against a supply of ≈ 640 (≈ 0.05 automatic
velocity); a customer's order plus its paper costs ≈ 3 a round against a 25-penny purse: about 8-10 rounds unless it sells labour
or goods (a worker-round at the Mint earns ≈ 5).

### 5.2 Dry runs (bots performing their legs)

| | Seed 1 | Seed 2 |
|---|---|---|
| Food produced a round, rounds 1-10 / 11-24 (× demand) | 26.8 (1.12×) / 29.2 (1.34×) | 32.7 (1.36×) / 21.5 (1.04×) |
| Fed share rounds 1-3 / 1-10 / 11-24 | 1.0 / 0.979 / 0.908 | 1.0 / 0.975 / 0.907 |
| Missed meals, deaths (24 rounds) | 33, 4 | 33, 6 |
| Stores (all) at round 1 / 10 / 24 | 118 / 68 / 49 | 123 / 88 / 44 |
| Legs met rounds 1-3 / 1-10 / 11-24 | 0.87 / 0.73 / 0.21 | 0.88 / 0.76 / 0.18 |
| Claims to the Hall by round 13 (seed 1) | 18 | — |
| Survival-action share 1-10 / 11-24 | 0.22 / 0.36 | 0.21 / 0.35 |
| Velocity, voluntary share, hoard ratio (end) | 0.05, 0.83, 0.38 (0.74) | 0.05, 0.84, 0.30 (0.54) |
| Arrears, breaches | 0, 34 | 0, 40 |

**What the flows show.** Output never falls below demand, yet people starve: the failure is distribution, as 08 predicted
("the food exists, at the dealer's price"). Three causes, read from the Order Book's per-round record:
1. *Customers run out of money.* From round 9-11 most payment legs are could-not misses (purses spent at ≈ 3 a round); the bots
   never sell labour or goods at the Mint, which live customers can.
2. *Producers under-deliver.* The bots forage when low and fulfil once per contract, so producers often hold too little at their
   turn (could-not) or hold it and do not act (would-not → claims to the Hall: 18 by round 13 in seed 1). The pantries are eaten by
   their owners by round 6.
3. *The dealer's store stays shut.* S1 holds 45-55 food throughout; the bot dealer neither sells nor gives.
The deaths are customers whose producer failed (seed 1: Velma, Odo, Hollis, Ivy).

### 5.3 Gates (08 §6)

| Gate | Result |
|---|---|
| Viable 3 rounds with roles performed | **pass** (both seeds): fed 1.0, no missed meal, legs met 0.87-0.88; no arrears |
| Fails visibly when not performed | **pass** (§5.4): 13 deaths, first missed meals in round 5 beside full stores |
| Scale (§11a) | **partial**: output ≥ 30 a round only in seed 2's first 10 rounds (bots); stores ≥ 120 only at the start (120 by design; 08 put it at 5 rounds of demand); the 17 orders are not all served every round (bot production) |
| Survival-action share ≤ 30% | **pass before the blight** (0.21-0.22), **fail after** (0.35-0.36) as bots forage when hungry |
| Money velocity ≥ 0.10 | **fail by design** (0.05): reported, not forced (08 §3.2) |
| Channel use | not testable with bots (only the square and the engine's notices carry posts) |
| No inert laws | 1 inert at round 0: the Bodyguards Act as law code (`force_rule`, as in Private: 31.10 §8 #6) |
| Blight sensitivity | **weak pass** (§5.5): 2 deaths with the dealer releasing S1, 4 with it shut |
| Force | the Commission's G/P legs run (fee released only on guarded rounds); not staged under attack |
| Prompt budget ≤ 400 tokens | **fail** for most Haiku seats (§5.7) |

### 5.4 Neglect (`contracts.bot_obligations=neglect`, seed 1)

**Pass: fails visibly.** No standing-order leg is met (1 of 306); the first missed meals come in round 5 (6 customers) with the
dealer's store and the pantries still holding ≈ 110 food; 65 missed meals and **13 deaths** by round 24 (6 before the blight),
against 33 and 4 when the bots perform. 59 breaches are recorded and every would-not miss raises a claim on the Hall's docket;
velocity falls to 0.03. The failure is legible where the framework wants it: each party's OBLIGATIONS line, the counterparty's
notice, the Book's public record and the Hall's docket.

### 5.5 Blight sensitivity (`--apply dry/merchant_release.yaml`, seed 1)

**Weak pass.** With the dealer releasing S1 from round 11 (6 food a round to six customers), seed 1 ends with **2 deaths**
against 4 when the bot dealer keeps S1 shut; missed meals are the same (33), and S1 is empty by round 17 (the schedule overdraws
it from round 18 and those transfers fail). The dealer's choice moves deaths, but S1 (60) is small against a blight that leaves
≈ 8 orders a round unmet: in this world the larger lever is customers' money and producers' delivery, not one store. A live dealer
selling at a price is the case the dry run cannot stage.

### 5.6 Decision points (`--apply dry/merchant_decisions.yaml`, 8 rounds, seed 1)

The bots take no discretionary decision, so one decision of each card is injected as the agent's own action; each is a logged
act with its effect and public trace:

| Round | Seat | Decision | Logged as / effect |
|---|---|---|---|
| 1 | Brand (sell-sword) | `guard {"agent": "Dorin"}` | `guard`; the Commission then releases 2 pennies from Dorin's escrow every guarded round (rounds 1-7) |
| 2-3 | Kip (hunter) | holds food, does not deliver | would-not misses → claim L13#1 (and the bots' own misses: claims 2-7 by round 5) |
| 2 | Velma (broker) | `deposit` 5 copper at the Mint | 14.48 pennies at P = 1.727 |
| 2 | Velma (lender) | `lend` 10 to Ketty, 12 back in 5 | `loan_offer` N12 |
| 2 | Garron (Speaker) | `post` the agenda on notices | `channel_post` |
| 3 | Ivy (Registrar) | `invoke licence_issue [Wat]` | a forester licence, the register |
| 3 | Dorin (dealer) | `post` "SELL 5 food @ 3 penny" on market | a Market Board offer |
| 3 | Ansel (editor) | `post` on ledger-sheet | read by the paper's members only |
| 4 | Ansel | `invoke A3.sub_fee [all, 1.5]` | the subscription notice |
| 4 | Wat, Bea | `join_contract A4`; `invoke A4.sub_enrol [Wat]` | Wat a member and subscriber (reads the Courier) |
| 5 | Marsh (arbiter) | `invoke A2.award ["L13#1", ...]` | **refused: Marsh is the claimant** (Kip is his supplier): recusal works |
| 5 | Marsh | `invoke A2.award ["L13#2", 2, ...]` | ruled; at the round's end the Book paid Wat 2 pennies and the Hall its fee (0.96) out of Fion's bond, gazetted |
| 6 | Hobb (customer) | `invoke A1.orders_notice` | notice: the order ends after round 8 |

### 5.7 Prompt budget and executability (seed 1, round 2 state)

Registers (loans, credit records, stores), contracts (obligations, owed, role card, contract lines, terms lines, "could join") and
channels lines, measured on `agents.state_view`; tokens ≈ chars / 4.

| Seat | Registers | Contracts | Channels | Total ≈ tokens |
|---|---|---|---|---|
| Kip (hunter, 1 order) | 419 | 811 | 359 | ≈ 400 |
| Wat (customer) | 418 | 1,410 | 359 | ≈ 550 |
| Fion (farmer, 3 orders + a paper) | 478 | 1,682 | 360 | ≈ 630 |
| Nell (customer, a paper) | 419 | 2,038 | 360 | ≈ 700 |
| Brand (customer, paper, Commission) | 399 | 2,876 | 366 | ≈ 910 |
| Ivy (Registrar-notary, customer, paper) | 418 | 3,241 | 369 | ≈ 1,000 |

The biggest items: the public credit records line (≈ 300 chars: every loan in town), "Contracts you could join" (≈ 300: the hall
and the papers), one "Your contract …" line per membership (≈ 250 each) on top of each role card. Cuts that would bring a farmer
under 400 without losing anything actionable: show credit records only to parties and lenders; drop "could join" for closed
associations; fold "Your contract" into the role card. These are engine changes outside this item.

Executability: every action the state names was tried on a fresh copy of the kernel for ten seats (`fulfil` per contract and leg,
`invoke A1.orders_notice`, `A5.commission_notice`, `leave_contract`, `send` to an institution's inbox, `read`, the recall
`propose`). All literal calls ran. Failures were only placeholders (`read_law {"law": "<id>"}`, `propose {"code": "<law
source>"}`) and `send` when the bot had used its 3 messages that round. Office duties name the exact actions (`A1.orders_enrol
[customer, producer]`, `A3.sub_enrol [name]`, `A2.award [claim, qty, reason]`, `licence_issue`, `certify_agreement`).

## 6. Findings and limits

1. **`start` overwrites a law-set procedure**: `h_institution` enacts the laws and then applies `procedure:`; an institution using
   the Role Procedure must omit `procedure:` (merchant.yaml's A1 does; noted for the Private bank in §3).
2. **The seller side of a customer-keyed roster has no terms line or role card**: producers see their dues in OBLIGATIONS but no
   "Standing order" line; acceptable (it costs no tokens) but a seller's card would help.
3. **The Commission's guard counts only with the Bodyguards rule** (F1), so merchant.yaml enacts it; without it a sword is worth its
   fort.
4. **Could-not subscribers are never expelled** (core rule); a paper whose readers cannot pay keeps them reading until they leave.
5. **The bot dealer and the bot customers do not trade**: the dry runs cannot show the Merchant squeeze's market side (dealer prices,
   labour sold at the Mint). That is the live run's question.
6. **Bounty and Criminal Code**: a bounty hunter's own strike is an unlawful attack, fined under the auto Criminal Code (3 pennies
   on a first offence against a 4-penny wound bounty). Left as is: it is the Merchant regime's question whether private justice pays.

## 7. Running it

```bash
python -m cybertron run cybertron/specs/regimes/merchant.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99
python -m cybertron run cybertron/specs/regimes/merchant.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99 \
    --set contracts.bot_obligations=neglect
python -m cybertron run cybertron/specs/regimes/merchant.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99 \
    --apply cybertron/specs/regimes/dry/merchant_release.yaml
python -m cybertron run cybertron/specs/regimes/merchant.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99 \
    --set rounds=8 --apply cybertron/specs/regimes/dry/merchant_decisions.yaml
python -m cybertron.analysis.flows RUN_DIR --all-stores
python -m cybertron institutions RUN_DIR
```
