# Review 31.09: usability round 2 (manual obligations, role cards, Opus decision seats)

*20 Oct 2026. Branch `wp/obligations2`. Five live runs, seed 1, 8 rounds each, `LLM_BACKEND=claude_code`, specs
`cybertron/specs/usability/v2/*.yaml`. Run dirs (not committed): `cybertron/out/{contracts,payroll,farming,market,laws}/2026-10-20T03-*_seed1`.
A first payroll run (`cybertron/out/payroll/2026-10-20T03-37-39_seed1`, 1 round) was killed by a container restart and is left as is;
the payroll numbers below are from the rerun.*

## What changed since round 1 (16 Oct)

| Change | How (spec) | Systems |
|---|---|---|
| Manual obligations: nothing moves by itself; `fulfil` or a matching transfer meets a leg; misses recorded, the defaulter reminded at the top of its next turn, the counterparty told, terms escalate | `contracts: {legs_default: manual, obligations: true}` | contracts, payroll |
| Role cards (purpose, answers to / answer to you, what you get and from which leg, numbers, 2-4 decisions with exact syntax) as vital lines at the top of the state | `contracts: {role_cards: true}` | contracts, payroll, market, laws |
| Petitions to an institution's inbox listed to its officers, public after 2 rounds unanswered | `institutions: {petition_public_after: 2}` | contracts, payroll, laws |
| Forgiving arguments | `actions: {forgiving: true}` | all |
| Opus in the decision seats | Mara (shopkeeper), Oren (owner), Ada and Kell (councillor, keeper), Bryn (a seller) | all but farming |
| Goals tied to roles instead of drawn private goals | Company on A1 for the shop and the firm; Wealth for paid roles; Survive for consumers; Benefactor for councillors; Kell keeps Hoard food (the scenario's capture) | all |
| Only forest and fields (no ore, gold, compute camps) | `camps: {typed: {set: []}}` (payroll keeps its timber camp) | all |

The Oct 16 run directories are gone (container restarts; none in any worktree), so the baseline is the round-1 summary: automatic
flows worked with nobody acting, Sonnet decision seats ignored their roles (private goals pulled them away, roles not salient), Haiku
did the passive parts, and nobody took reactive or discretionary actions.

## Headline

**The roles were performed, and the reactive and discretionary layer appeared.** Every contracted party met its legs by acting
(`fulfil` 40 times in contracts, 7 of 8 rounds in payroll), misses were noticed and answered within a round, and every decision seat
took decisions its card listed (price cut, wage cut and restore, two hires, a law amendment). No run had a death. Model errors were
3-9% of actions, none from `fulfil` misuse; the rest are argument near-misses in farming, harvest and store actions (fixes below).

| System | Seat performance | Reactive / discretionary actions | Failed actions |
|---|---|---|---|
| contracts | shopkeeper (Opus) met every leg, 8/8 rounds, 0 misses; 3 farmers (Haiku) delivered 21 of 24 rounds (all 4 misses could-not, food short); 2 subscribers paid 11 of 16 (late in round 1-2 only) | price cut 1.5 -> 1 to stay solvent; farmers negotiated (Cass: "the 1.5p rate back once it recovers"); a subscriber used the store as a food bank and demanded a public ledger, which the shopkeeper posted | 13 / 229 (6%) |
| payroll | owner (Opus) paid wages 7 of 8 rounds; misses in rounds 3-5 (treasury short), all paid off by round 6 | wage cut 2 -> 1 (round 2) then restored after a worker's ultimatum (round 3); owner put his own pennies into the treasury; hired Faye and Gus; one worker gave notice; 4 workers DMed arrears demands within a round of a miss; a worker petitioned @A1 | 7 / 223 (3%) |
| farming | 6 of 6 farmers sowed, tended and reaped (18 sow, 27 tend, 15 reap) | none needed (no institution) | 15 / 166 (9%) |
| market | sellers (Opus + Haiku) and buyers traded: 20 transfers, 8 board posts | prices posted on the board; deals closed in DMs; pennies hardly used (timber for food) | 13 / 208 (6%) |
| laws | keeper (Opus) drew 6 a round for himself (the scenario); council (Opus + 2 Sonnet) amended the Granary Ration the round the notice was discussed (proposed round 3, passed 3-0 round 4) | the amendment did nothing (see below); no recall or election of a new keeper was tried; no petition was sent to @J0 | 17 / 197 (9%) |

## Per system

### Contracts (the Corner Shop: Board + Supply Contract)

| Agent | Role | Model | fulfil ok / err | Legs paid (tagged) | Missed notices | Decisions |
|---|---|---|---|---|---|---|
| Mara | shopkeeper | Opus | 8 / 0 | F 16, P 15 | 0 (as counterparty 4) | supply_price 1.5 -> 1 (round 4); ledger post; 15 DMs |
| Bryn | farmer | Haiku | 8 / 0 | D 8 | 0 | - |
| Cass | farmer | Haiku | 6 / 1 | D 6 | 2 (could-not) | asked for the old price back |
| Dell | farmer | Haiku | 7 / 1 | D 7 | 2 (could-not) | - |
| Edda | subscriber | Haiku | 6 / 0 | P 6 | 1 (round 2) | deposited food in S1, asked for a ledger |
| Fion | subscriber | Haiku | 5 / 0 | P 5 | 0 | - |
| Gale, Hob | not subscribed | Sonnet, Haiku | - | - | - | Hob joined A1; neither set an allowance |

Treasury 30 -> 7 penny, store S1 30 -> 44 food over 8 rounds: viable, but only because of the price cut.

What agents ignored, and why:
- **Promises not acted on.** Mara told Hob "I'm enrolling you as a supplier this round" and Bryn "setting the supply price to 2p";
  neither happened (she used her actions on fulfil, withdrawals and transfers). Hob joined and was never enrolled. Nothing in her
  state listed "members not on any roster".
- **Unsubscribed consumers stayed out.** Gale (Sonnet) and Hob never set an allowance on the Board: their card is absent until
  they are on a roster, so the shop's offer is not salient to non-members.
- **Goal gaming.** Mara paid 1-penny "member dividends" to Fion and Hob to count payout rounds for her Company goal, and drew 7.5
  food from S1 for herself.
- **board_price never touched**, though the treasury fell every round.

### Payroll (the Ridge Timber Company)

| Agent | Role | Model | Pay received / actions | Reactions to misses |
|---|---|---|---|---|
| Oren | owner | Opus | fulfil 7 (W 35 payments); set_wage x2; hire x3 (1 refused: Gus had not applied) | missed in rounds 3-5 (treasury empty; round 3 paid in timber, which does not meet a penny leg), arrears paid by round 6 |
| Ash, Bea, Cole, Ezra | workers | Haiku / Sonnet (Ezra) | wages 2 a round (1 in round 2), 50% timber cut automatic | Ash: ultimatum to restore the wage (restored next round); Bea, Ezra: arrears demands; Ezra petitioned @A1 |
| Dina | worker | Haiku | - | gave notice (payroll_notice) in round 4 after a missed wage; left after round 5, sold her timber to A1 |
| Faye, Gus | outsiders | Haiku | joined, hired at wage 1 | Faye bargained 10 timber for a written wage guarantee |

This is the reactive layer round 1 lacked: each miss produced DMs within a round, one notice, and a renegotiated wage. Haiku workers
did both their passive part (harvest, 6-31 a run) and the reactive part.

### Farming

All six farmed. Errors were the cycle's argument shapes: `farm {"plot": 1, "amount": 3}` (sow on a plot), `farm {"reap": true}`,
reaping a fallow plot or sowing a ripe one, `harvest {"camp": "forest1"}` / `harvest {}`. Store-building failed every time: a store
costs 6 stone and the stripped world has no stone camp (a side effect of the camp strip, also in market and laws).

### Market

Trading worked but mostly off the board: 8 board posts (SELL/BUY lines), deals closed in DMs, settled by transfers (timber for
food). The three penny holders barely spent pennies; one buyer (Edda) never traded and hunted instead. One invented action
(`take_offer`).

### Laws (the granary keeper)

- The council reacted the round the notice was discussed: Ada (Opus) proposed an amendment letting councillors draw too
  (round 3; structural, passed 3-0 in round 4) and Kell, publicly pressed, stopped drawing for a round and posted his draw log.
- **The amendment silently did nothing**: the Offices Act gives the keeper's office sole control of S1, so councillors' withdrawals
  were refused (Ada and Cora, round 5). Ada noticed and ran out of rounds. (Framework §12: "laws can silently do nothing".)
- Kell (Opus, Hoard) resumed drawing in rounds 6-8, reasoning that a removal vote could not close before the end. No councillor tried
  recall or a new election, though the keeper's card says who fills the office.
- Nobody wrote to @J0, so petitions went untested live. Councillors read Benefactor as "everyone above the median" and spent the late
  rounds on transfers to cross that line.

## What works

1. **`fulfil` with the exact call in the state.** Every party that owed something used it from round 1, Haiku included, with no
   errors except could-not shortfalls (which the error explains: "2.22 food due, you hold 0.85 (keep 2)").
2. **Miss notices drive reactions.** Defaulter and counterparty notices produced arrears demands, notices, a restored wage and the
   owner topping up the treasury from his own pocket.
3. **Role cards make the decision seats act on their roles.** Both Opus officers used their card's invoke calls (supply_price,
   set_wage, hire) and cited their duties in reasoning. Goals tied to the role (Company) aligned them, with some gaming.
4. **Forgiving arguments** absorbed `good`/`amount`/`note` on transfers and `institution`/`leg_id` on fulfil; no `fulfil` call failed
   on its arguments.

## Concrete fixes

| # | Fix | Where |
|---|---|---|
| 1 | A per-unit leg's amount that may still wait to next round is shown as "in arrears" on the officer's card every round; say "payable by next round" and count arrears only once late | `obligations.role_lines` |
| 2 | Officer card: list members on no roster ("Hob joined, not enrolled: supply_enrol") and pending applicants for every roster contract | `obligations.role_lines` |
| 3 | Non-members see open institutions' offers (a Board's price and how to subscribe) once, on a card or a notice | role cards / contracts.state_lines |
| 4 | Forgiving: `transfer` to a store with no item means food; `kind` as `item`; `harvest {"camp": "forest1"}` or `{}` with one forest means that forest; `farm {"reap": true}` reaps the ripe plot; `farm {"plot", "amount"}` sows | `actions._forgive` |
| 5 | Usability specs that strip camps must keep a stone source or cheaper stores (every store build failed) | specs v2 |
| 6 | A law that grants a right the office-control gate overrides should be flagged at proposal (preview) or its grant should pass the gate | lawpreview / institutions.controls_for |
| 7 | Keeper card: show the accountability route (who can recall, with the action) to the council, not only "who fills the office" | `obligations._answers_to` |
| 8 | Petitions need a test that sends one: add a citizen goal or a scripted shock that petitions @J0 | specs v3 |
| 9 | Company goal: payouts of 1 penny to members count as company payouts; require a minimum or exclude transfers without a contract leg | `institution_goals.h_company` |

## Engine

All of this is off by default (engine 18 unchanged, no flip). A world opts in with the settings above; worlds made before keep their
automatic flows. Flipping manual legs on by default (engine 19) is the next decision, after fixes 1-4.
