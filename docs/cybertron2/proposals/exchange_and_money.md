# Proposal: exchange and money

**Status:** partly accepted: D2-1, D2-2, D4-17 (a shop needs a shopkeeper); the rest discussion (23 Oct). **Owner:** 37.2 (the
economics); the `offer` and `accept` verbs are shared with 37.4 (agents/actions, verbs.md). **Affects:**
spec/economy/money_and_markets.md; agents/actions.md (with 37.4); information/ (what agents see of prices, with 37.4);
institutions/ (tolls, market rights, courts for debts, with 37.3).

## Summary

Goods change hands between people at the same node through **offers that settle both sides at once when accepted**. An offer can
go to one person for the day, or to **anyone here** for as long as the offerer stays, in lots (a stall without a building). Making
and accepting offers takes **no work units**, like speech: what trade costs in cybertron2 is being in the same place at the same
time, carrying, and trusting a promise. One leg of an offer can be **a promise** ("5 food by the market day"), which creates a debt
that exists only as what people know and what is written (D2-1). **Prices are what agents saw or were told**, never computed for
them. **Coin is copper**, seeded with some households and the merchant; a smith can strike more, so its value follows copper's.

## How cybertron 1 did it

| Mechanism | How it worked | Cost |
|---|---|---|
| `transfer` | give anything to anyone, anywhere, at once | 1 action; no protection: one side goes first |
| `reply` with payment | pay inside a DM reply | 1 action; the same trust problem |
| `post` | offers as free text on the public board | no mechanism behind it |
| the **Exchange** contract template | found a contract, both deposit in escrow, the swap runs at round end (both or neither), refunded at a deadline | about 2-3 actions across the two parties, and a round's delay |
| the **standing order** template | a recurring payment from an allowance | founding a contract |
| the **Market Board** law template | lines like `SELL 3 food @ 2 coin` on a board become a public offers table (kept 3 rounds); a trader takes one at the posted price | a law someone had to pass first |
| `lend`, `accept_loan`, `repay_loan`; currencies; `sell_to_window` | credit and money | institutional setup |

## What went wrong

1. **Trading cost more than producing.** An escrowed exchange took 2-3 actions; buying 3 food cost more actions than foraging it
   (02a §1). Specialisation lost to self-supply even where it paid at the production step (02b: the cost of exchange is the largest
   term; at half a unit per unit traded the gain from institutions disappears).
2. **Safe trade was heavy and light trade was unsafe.** `transfer` meant one side went first on trust; the Exchange meant founding
   a contract and waiting a round. Agents mostly used neither: 17 contracts in 5 runs, mostly one-member tests, none carrying a
   strategy (26 §4.2); food changed hands 4-21 times a run in Ashwood (26 §4.3).
3. **No prices.** There was no food price, and the currency had no tie to food (27 §4). A market existed only if someone passed the
   Market Board law, and a market that clears at stable prices with a 3-round board and a Haiku bulk was never likely (02a §2).
4. **Everything at a distance.** A transfer reached anyone anywhere instantly, so distance, carrying and merchants never mattered.
5. **cybertron2 phase 0 repeated problem 2 in space.** With only `give`, run 2's Irons handed over 9 blades for promised food;
   payment came a day late or never while the sellers starved (38.03; the Alders paid late, one blade stayed unpaid).

## The proposal

### 1. Offers (extending 37.4's `offer` / `accept`, 38.05 §4)

| Verb | Arguments | What it does |
|---|---|---|
| `offer` | `to` (a person here, or `anyone`); `give` {item: qty}; `get` {item: qty} or a promise; `lots` (default 1); `until` (a day; default: the end of today for a person, while you stay for `anyone`) | proposes an exchange. Nothing moves yet |
| `accept` | `offer`; `lots` | carries out both legs at once if both parties are here and hold the goods; otherwise refused, and nothing moves |
| `withdraw` | `offer` | ends an open offer |

- **Where the goods come from:** what the party carries, or a container at the node it may take from (its house stock, a store it
  keeps). The offerer must be present (D4-17); an offer lapses when it leaves.
- **When it settles:** offers and acceptances made in the talk step settle there, and both parties are asked again (they received
  something) so they can plan with what they now hold. An `accept` can also be a planned action in the work step, for goods made
  that day; it is refused if the goods are not there at its turn.
- **Offers to anyone** are a stall without a building: "Brenna offers 1 blade for 5 food (3 left)" in the Here section of everyone
  present and of anyone who arrives. Busy places are trimmed by priority (verbs.md).
- **Cost: no work units** for offering, accepting or withdrawing (calibrate: if trade proves too cheap, a fraction of a unit per
  settlement).

### 2. What a trade costs, then

| Cost | Where it comes from |
|---|---|
| meeting | both at the same node on the same day: travel, waiting, market days |
| carrying | weight and capacity (transport.md), spoilage on the way |
| trust | only when one leg is a promise (§3) |
| the seller's presence | a stall needs its keeper there (D4-17), so selling competes with working elsewhere |
| tolls and fees | a market's or a gate's payment rule (02k §2), set by whoever holds them |

This puts the cost of exchange where it is in life, so the prediction is testable: **thick trade inside a node, thin trade between
nodes, carried by merchants** (02g's transport ladder sets how thin).

### 3. Promises and debts (D2-1)

- **A promise as one leg:** `get: {promise: {item: food, qty: 5, by: day 12}}`. On acceptance the goods leg moves and a **debt**
  is recorded: who owes whom, what, by when, and who saw it.
- **A debt is information.** The parties and the witnesses remember it; that is all the engine guarantees. Paying is a `give`.
- **Written, it is a document** (an IOU, a tally, a ledger line): a good that can be carried and handed on, so a debt can be sold or
  used to pay (bills of exchange later).
- **Default** costs standing with those who know (memories, relationships); remedies come from institutions (37.3's courts;
  law.md: levies and fines are debts too).
- **Consignment** is a promise leg: a merchant takes 20 hides now and promises the proceeds, or a share, on its return.

### 4. Prices: only what agents saw or were told

- **Every settlement is witnessed** by those present (in a room: those with access): "Bram bought a blade from Torvald for 5 food."
  The price becomes a dated belief in each witness's knowledge store.
- **Standing offers show asking prices** to everyone at the node.
- **Elsewhere,** a price is what you remember or were told, with its age. Merchants carry prices; telling them spreads them.
- **No computed market price is shown.** The engine never tells an agent "the price of blades is 5" (the rule against computed
  knowledge, as D2-4 for absence).

### 5. Coin

- **Copper coin** (copper is in, D2-24): a light, standard good. Seeded with some households and the merchant household (D2-2).
- **Striking coin:** a smith with a hearth can strike coin from copper at a small cost, so coin is commodity money and its value
  follows copper's. A stamp that only an institution may use (a seal, 02g §1d) comes later, with debasement and forgery.
- Coin's use is that it is accepted: nothing forces it. If a world's agents prefer food or blades as money, that is a finding.

### 6. Market places and days

- A **market** is a custom, not a mechanism: a known place at a node (a square, a crossroads) and a known day ("Millford holds
  market every sixth day"), seeded as knowledge. Its effect is that sellers and buyers are there at once.
- Whoever holds the market site can charge for a stall (a payment rule, as a gate's toll) or grant market rights (37.3).

### 7. Standing arrangements

Routine payments and deliveries run on the routine standing orders already decided (D4-16): "each day: give 2 food to Mara".
Recurring trade is an offer to anyone with lots, renewed while the seller stays. Contracts that bind both sides (supply, payroll,
tenancy) wait for institutions (37.4's M3).

## Why

- It removes cybertron 1's two failures at once: an exchange is safe (both or neither) and costs no actions.
- It needs no institution to exist before anyone can trade, but leaves institutions everything to do: markets, tolls, courts for
  debts, ledgers, stamped coin.
- Credit grows out of exchange (a promise leg) instead of being a separate system, and stays information (D2-1).
- Prices exist from the first trade, and spread only as fast as people do, which gives merchants their edge.

## Alternatives considered

- **Keep trades costing actions** (cybertron 1): rejected in this proposal: it made specialisation lose to self-supply (02a, 02b).
- **A posted-price market board as the only market** (cybertron 1's Market Board): kept as an institution a node can create, not
  the default.
- **A computed node price shown to everyone:** rejected: agents would know what they never saw.
- **Trust only (`give`):** run 2 showed it fails.
- **Money and credit move anywhere:** rejected, D2-1.
- **Merchants emerge from delay alone:** replaced by D2-2.

## Open questions (for Zach)

1. Offers and acceptances cost no work units (calibrate later)?
2. Offers to anyone, open while the offerer stays, in lots, as the default stall?
3. A promise as one leg of an offer, creating a debt that is only information?
4. Copper coin seeded, and struck by any smith (commodity money), with an institution's stamp later?
5. Prices only from what agents witness or are told; no computed price?
6. Markets as seeded custom (a place and a day), with no engine mechanic of their own?
7. Next: hiring (an offer whose terms are work: whose is the output, D4-23), a separate proposal.

## Measures (with spec/measurement)

Settlements per agent-day; the share of food and of tools obtained by trade; price dispersion within a node over time and between
nodes; merchants' margins; promises kept and broken; all against a null arm with offers disabled.

## History

- 22 Oct: 02b: the cost of exchange is the first design problem; standing contracts and routine orders before markets.
- 22 Oct: Zach: purchases and payments are fair; markets can sell subscriptions, not just one-offs (old-engine discussion).
- 22 Oct: 02f E1 and E5 written for cybertron2 after run 2's failed trades.
- 22 Oct: Zach agreed coin is carried and debts move only as information (D2-1), and one merchant household seeded (D2-2).
- 22 Oct: 37.4: a shop needs a shopkeeper (D4-17); offer and accept in the day's order (38.05 §4).
- 23 Oct: tolls as a gate's payment rule (02k §2).
- 23 Oct: Zach: work through exchange: how cybertron 1 did it, its problems, a new system for cybertron2. Rewritten: the cybertron 1
  review and its failures; offers to a person or to anyone, in lots, settling at once, free of work units; promises as a leg
  (credit from exchange); prices only as witnessed or told; copper coin seeded and struck by smiths; markets as custom; trade's
  cost moved to meeting, carrying and trust.

## Sources

[02a §1-2](../../review/37_growth/02a_economy_design.md), [02b](../../review/37_growth/02b_productivity.md),
[02f §3, §6](../../review/37_growth/02f_economy_plan.md), [02k §2](../../review/37_growth/02k_fuses_and_gates.md),
[26 §4](../../review/26_run_comparison.md), [27 §4](../../review/27_systems_inventory.md), 38.03 (run 2), 38.05 §4, 38.06 §4,
verbs.md; cybertron 1: `cybertron/action_registry.py` (transfer, reply), `cybertron/contracts.py` (Exchange, standing order, swap),
`cybertron/library.py` (Market Board); D2-1, D2-2, D2-24, D4-16, D4-17.
