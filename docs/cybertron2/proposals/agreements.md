# Proposal: agreements and obligations (one system for trade, credit, subscriptions, wages, rent and dues)

**Status:** discussion (23 Oct). **Owner:** 37.2, with 37.4 (law.md's mechanical clauses create the same records; the verbs) and
37.3 (institutions, courts). **Affects:** spec/economy/money_and_markets.md; agents/actions.md (offer, accept, notice);
institutions/ (contracts, ledgers, courts); information/ (debts and ledgers as knowledge and documents).

## Summary

Every exchange, debt, subscription, wage, rent, supply deal, retainer and loan is **an agreement made of legs**: cybertron 1's
Standing Contract, kept. A leg is "this item, this much, from this party to that one, now, by a day, or every n days until notice".
One rule adapts it to space: **an obligation exists anywhere, but it is paid only where there is a way to pay it**: both parties'
goods at the same node, both accounts in the same ledger, or a carrier. When there is no way, it accrues as arrears, paid first
later. An offer is how an agreement is made; a spot trade is the smallest agreement (two legs, now, both or neither).

## What cybertron 1 already had (31.03 §2; `cybertron/standing.py`, `cybertron/credit.py`)

- **The Standing Contract:** legs (`move`, `harvest` share, `duty`), each per round, run at the round's end with no action from
  anyone; `owe` (arrears recorded, paid first later); a **miss** (could not pay) against a **breach** (could pay, would not, after
  a grace); a **bond** in escrow; **notice** and an exit fee (leaving is a right, but priced); an **arbiter** or a court.
- **Presets** over the same code: Supply Contract, Board (meal plans), Payroll, Quota, Grant, Charge, Retainer, Service, and
  subscriptions on a roster (31.03 §2.7).
- **Forms:** bilateral (two named parties) and roster (one principal, many enrolled: a shop's customers, a paper's subscribers, a
  firm's workers).
- **Loans** with interest, default, rollover and refinancing, and public credit records (`credit.py`).

Its weakness was not the design but its setting: legs moved goods between accounts anywhere, instantly, and founding a contract
cost actions. Both go away in cybertron2.

## The proposal

### 1. One record: the leg

| Field | What |
|---|---|
| from, to | a party (agent, household, institution) and, optionally, a container (a house stock, a store, a ledger account) |
| item, qty | any good (food, grain, coin, timber, a document) or **work** (a duty: guard, reap a plot, carry a load) |
| when | `now`; `by` a day (a promise); `every` n days from a day, until notice or a number of times |
| per | optional: qty per unit of another leg (pay per delivery) |
| bond | optional: paid from what the party deposited up front |

An **agreement** is a set of legs, its parties, its notice period and its remedy (none, a bond, an arbiter, a court). A **debt** is
an unpaid leg. Records are information (D2-1): the parties and witnesses know them; written, they are documents.

### 2. The settlement rule

A leg falls due on its day. It is **paid automatically** (no call, no work unit) if there is a path:

| Path | When it exists |
|---|---|
| **in person** | payer (or its container) and payee (or its container) are at the same node |
| **in a ledger** | both hold accounts in the same ledger: the payment is a change in the ledger's records at its seat, wherever the two people are |
| **by a carrier** | the payer named a carrier who holds the goods and reaches the payee |

Otherwise it **accrues as arrears**, shown to both parties, and is paid first when a path appears. A payer who could not pay (does
not hold it) has a **miss**; a payer who held it and did not let it go (its allowance, or it moved it away) has a **breach** after a
grace, as in cybertron 1.

**Spot trade** is the special case: two `now` legs, settled both or neither (the swap). **Notice** reaches the other party only as
information (in person or by letter), so a subscription cancelled by a letter runs until the letter arrives.

### 3. Everything else is a preset

| Arrangement | Legs |
|---|---|
| spot trade | goods now <-> goods now (the swap) |
| a sale on credit | goods now -> ; payment by a day <- |
| consignment | goods now -> merchant; proceeds or a share by its return <- |
| **subscription** | payment every n days, until notice (a paper delivered, a pew rented, a guard retained) |
| wages | payment every n days <- ; a duty every day -> (work) |
| supply | goods every n days -> ; payment per delivery <- |
| rent, a lease | payment every n days, for a claim's access (spec/world/holding.md: `transfer_claim` with access and withdrawal) |
| board (meals) | payment every day -> ; food every day <- |
| a loan | principal now -> ; instalments every n days <- (interest as a growing leg) |
| dues, levies, fines, taxes | legs created by an institution's code or a law (law.md: mechanical clauses change records only) |

### 4. Making agreements: offers

`offer {to, legs, notice?, remedy?}` and `accept` (exchange_and_money.md §1): one verb for all of the above. Free of work units.
Offers to `anyone` in lots are stalls and rosters (a paper offering subscriptions to all comers). Institutions make standing ones
(a shop's Board, a firm's Payroll).

### 5. Ledgers: how money moves at a distance

A **ledger** is a container at an institution's seat (a merchant house, a temple, a lord's hall) holding goods or coin for many
holders, with each holder's share as a record (a claim, D4-23). Deposits and withdrawals are physical, at the seat. **Payments
between accounts in the same ledger are record changes**, so subscriptions, wages and rents between depositors run automatically
even when the parties are nodes apart. Orders to the ledger come in person or by sealed letter (forgery is possible: seals, 02g §1d).
A ledger is the first bank; letters of credit between two ledgers are its later form.

This is where the system stays consistent with D2-1 and D4-9: **goods move only when carried; records change where they are
kept.**

### 6. Currency: wanted, not required

| Function | Without coin | With coin |
|---|---|---|
| unit of account | prices and debts in grain or food (common in history) | one measure for everything |
| medium of exchange | barter needs both sides to want what the other has | anyone takes it |
| store of value | food spoils (15% a day loose); grain in a store keeps; a debt keeps | copper does not spoil |

**Proposal:** legs may be in any good; **copper coin exists** (seeded; a smith can strike it: exchange_and_money.md §5); nothing
forces its use. Spoilage gives a principled reason for people to want a store of value that keeps, so coin, stored grain or a
ledger balance should emerge as money. Whether agents adopt coin is a finding, not an assumption. Institution-issued money
(ledger notes, stamped coin, par and reserves from `credit.py`) is a later layer on the same records.

## Why

- **Elegance:** one record (the leg), one rule (pay where there is a path, else arrears), one verb (offer and accept) cover trade,
  credit, subscriptions, wages, rent, supply, loans and taxes.
- **It reuses cybertron 1's institutional layer** (H-2: copy it with its fixes): the Standing Contract core, its presets, misses
  and breaches, bonds, notice, arbiters, loans and credit records.
- **Space shows up in exactly one place:** settlement. That is where it matters in life: a debt is easy to make and hard to collect.
- **It gives institutions their economic jobs:** keeping ledgers (banking), holding bonds (notaries), judging breaches (courts),
  creating legs (taxes, fines), running rosters (shops, papers, employers).

## Alternatives considered

- **Separate systems** for trade, loans, contracts and subscriptions (cybertron 1's modules): replaced by one record.
- **Recurring payments that move goods anywhere** (cybertron 1): rejected by D4-9 and D2-1; replaced by the settlement rule.
- **Recurring payments only between people at the same node:** too restrictive; ledgers give distance without teleporting goods.
- **No currency, barter only:** possible, and agents may choose it; but light, durable money is what merchants need between nodes.

## Open questions (for Zach)

1. One system of agreements made of legs (cybertron 1's Standing Contract), made by offers?
2. The settlement rule: an obligation exists anywhere; it is paid automatically only where there is a path (same node, same ledger,
   a carrier); otherwise arrears.
3. Ledgers as the way recurring payments work at a distance, and the first form of banking?
4. Coin as a seeded good that nobody is forced to use, with legs in any good?
5. Port `cybertron/standing.py` and `cybertron/credit.py` onto this (with 37.4, who owns the code), rather than design anew?
6. Work as a leg (a duty): the base for hiring (whose output is it: delivered into the employer's container at the site, or carried
   by the worker and handed over?).

## History

- 22 Oct (old engine, carried over): Zach: purchases and payments are fair; markets can sell subscriptions, not just one-offs.
- 23 Oct: Zach: much of the economics and contracts was designed for cybertron 1; do we want a currency; an elegant method that
  brings things together; subscriptions (automatic transfers that recur until cancelled). Proposed: cybertron 1's Standing
  Contract as the one record, with the settlement rule, ledgers for distance, and currency as wanted, not required.

## Sources

[31.03 §2-5](../../review/31_institutions/03_money_labour.md); `cybertron/standing.py`, `cybertron/credit.py`,
`cybertron/contracts.py`; [exchange_and_money.md](exchange_and_money.md); [law.md](law.md); spec/world/holding.md (D4-23);
D2-1, D4-9, D4-16, H-2.
