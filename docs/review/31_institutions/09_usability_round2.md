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

## Fixes made (branch `wp/usability-fixes`)

All nine fixes are in, each behind the switch the round-2 specs already turn on, so worlds without those settings play as before. The
one exception is #6, which is a bug fix (see below). Tests: `tests/test_usability_round2.py`, plus the Service preset tests in
`tests/test_standing_contracts.py`.

| # | What changed | Where | Gate |
|---|---|---|---|
| 1 | The officer's card splits what its institution owes. **Owes X this round** is the amount due by the end of this round. **(Y in arrears)** counts only what was already late at the end of last round. **Z for this round's deliveries payable by the end of next round** is the amount a per-unit leg may still hold back. OBLIGATIONS "of which ... overdue" counts arrears the same way. A per-unit payment carried into its grace round is no longer called arrears. | `obligations._late`, `_split`, `role_lines`, `due_lines` | obligations / role cards |
| 2 | The officer's card lists **members on no roster**: members of the association who are on no standing contract's roster or terms and hold no office. It also lists applicants. Both come with the exact enrol action, e.g. `members on no roster: Hob (take on: A1.supply_enrol)`. These lines show only when the officer holds an office with an enrol action. | `obligations._unrostered`, `_enrol_calls` | role cards |
| 3 | An **OFFER:** card for an open standing contract (OPEN: a shop's Board). It goes to an agent who is not on the contract and who may join the institution (or is already a member), and is not one of its officers. It says what the agent gets and pays and gives the exact steps: `join_contract`, then `set_allowance` for the amount. At most two offers. The card shows every turn until the agent is on the contract. A state card was chosen over a one-time notice so that round 1 has it too. | `obligations.offer_lines` | role cards |
| 4 | Forgiving shapes. `harvest {"camp": "forest1"}`, `{"camp": "the forest"}` and `{}` now mean the one live forest; `{}` resolves only when the agent holds no other harvest right. `farm {"reap": true}` (or "yes"/"ripe"/"all") reaps the first ripe plot the agent may work; before, `true` meant plot 1. If no plot is ripe, the error lists the plots' statuses. `{"plot": n, "reap": true}` reaps plot n. `transfer` to a store with no item means food. `kind`/`type`/`what` name the item when no item is given. `farm {"plot", "amount"}` already sowed (the `amount -> sow` alias). | `actions._forgive`, `_forgive_harvest`, `_forgive_farm` | actions.forgiving |
| 5 | Every v2 spec now sets `subsistence.store.cost: {timber: 16}`. These worlds have no stone source: the camps are stripped, and payroll keeps only its timber camp. Timber is felled in the forest (`harvest {"fell": true}`). | `specs/usability/v2/*.yaml` | spec |
| 6 | A law of an institution whose stores an office controls (institutions.office_control) is now flagged when its `before_withdraw` can only block (None / False / a number / `{"block": True}`). Under office control only the controlling holders draw unless a law of the owner explicitly allows (`True` or `{"block": False}`), so such a law cannot widen draws. That is what happened to the council's Granary amendment. The note appears in the proposal event (`control_note`, shown under the proposal), in `preview_law` and on the `law_effect` event. Setup acts are not flagged. | `laweffects.control_note`; `dispatch/changes/legal.do_propose`; `lawpreview` | law.effects + office control (**bug fix**: informational, no world state changes) |
| 7 | **Recall** on the card of an office that others elect (or of a polity office that controls goods). It names the route and the exact law: `Recall: a law of J0 revoking J0.keeper removes you (passed by J0's procedure), e.g. propose {"code": "title = ...\ndef on_enact():\n    revoke(\"Kell\", \"J0.keeper\")"}`. The office that elects it (the council) gets an **Oversee:** line naming the holder, with the same recall call. A test enacts the call and the holder loses the office. | `obligations._recall_route`, `_oversees` | role cards |
| 8 | `specs/usability/v3/laws.yaml` (the v2 laws world) and the scripted shock `specs/usability/v3/schedules/laws_petition.yaml`, run with `--apply`. In it Gil petitions @J0 at the start of round 3 (inject_action send). The test runs the world with the shock: the petition is posted, it is listed to the councillors (PETITIONS line, card count), and it goes public after 2 rounds unanswered. | specs v3; test | spec / schedule |
| 9 | The Company goal gains two params: `payouts` (any or legs) and `payout_min`. **legs** counts only payments a law makes (`law:<id>`) or an officer's payment tagged with the contract leg it meets (fulfil). An untagged plain transfer that a manual leg credits does not count, so pay legs with fulfil. **payout_min** counts a round only if its payouts total at least that much. The defaults (any, 0) keep the old score and text. These params are kept in `institution_goals.OPTIONAL`, outside the DEFAULTS that every run's settings snapshot freezes, so no instance changes. The v2 contracts and payroll specs set `payouts: legs`. | `institution_goals._payout_rounds`; goal text | spec param |

Also on this branch (08 §5 Phase 1): **1.3** the Service preset in `standing.py`, and **1.10** the recipe placeholder `{best:camp1}` in
office duties (`start.recipe`). See 08 §5.

## Engine

All of this is off by default (engine 18 unchanged, no flip). A world opts in with the settings above; worlds made before keep their
automatic flows. Flipping manual legs on by default (engine 19) is the next decision, after fixes 1-4. Fixes 1-4 are now in; the flip
is not made on this branch.
