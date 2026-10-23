# Money and markets

## Summary

Goods change hands at a node through offers that settle both sides at once when accepted, at no cost in work units. An offer goes
to one person, or to anyone at the node while the offerer stays. One leg can be a promise, which makes a debt that exists only as
information. Prices are what agents saw or were told. Coin is copper, carried, seeded and struck by smiths. Markets are custom: a
known place and day. One merchant household with a cart is seeded in the first region.

## Decided

- D2-1: coin is carried; debts move only as information.
- D2-2: one merchant household with a cart is seeded in the first region.
- D4-17: a shop needs a shopkeeper.
- D4-9: goods cross between nodes only with someone carrying them.
- D2-25: offers settle both sides at once when accepted; offering and accepting cost no work units.
- D2-26: offers to anyone at the node, open while the offerer stays, in lots.
- D2-27: a promise can be one leg; accepting it creates a debt that is only information.
- D2-28: copper coin, seeded; any smith can strike it.
- D2-29: prices only as witnessed or told.
- D2-30: markets are seeded custom.

## Mechanics

- **Offers** (D2-25, D2-26): `offer {to: a person here | anyone, give, get, lots, until}`; `accept {offer, lots}` moves both legs
  at once if both parties are here and hold the goods (carried, or in a container at the node they may take from), else nothing
  moves; `withdraw`. An offer to a person lapses at the day's end, an offer to anyone when the offerer leaves. Offers made or
  accepted in the talk step settle there; an `accept` can also be a planned action in the work step. No work units.
- **A promise leg** (D2-27): `get` may be a promise (item, qty, by a day). Accepting moves the goods leg and records a debt known to
  the parties and to whoever saw it. Paying it is a `give`.
- **Prices** (D2-29): every settlement is seen by those present (in a room, by those with access) and becomes a dated belief;
  open offers to anyone show their terms to all at the node; the engine never states a price.
- **Coin** (D2-1, D2-28) is copper, an item in holdings with weight (transport.md), carried, stored, stolen and lost like any
  good. Some households and the merchant hold it at day 0; a smith with a hearth can strike coin from copper.
- **Markets** (D2-30): a node's market place and day are seeded knowledge; the engine adds nothing; the site's holder may charge
  for a stall (a payment rule, as a gate's toll).
- **A debt** is a record known to the parties (and to anyone told, or holding a written copy). Paying it is a physical transfer of
  goods or coin where both are present, or by a carrier.
- **Selling** at a node: goods change hands only from someone present (D4-17). An unattended stall sells nothing.

## Data

Coin in holdings. Debts as knowledge and documents (information/).

## Parameters

| Parameter | Value | Status |
|---|---|---|
| coin's weight; copper per coin; the cost of striking | 02f | calibrate |
| work units for offer and accept | 0 | decided (D2-25); calibrate if trade proves too cheap |
| coin seeded per household | seeding | calibrate |

## What agents see

Their coin; the debts they know of (owed to them and by them) in words; prices as they last heard them at each place, with how old
the knowledge is (information/).

## Open

- Agreements made of legs (recurring payments, wages, rent, supply, loans), the settlement rule, ledgers: proposals/agreements.md.
- Hiring: proposals/hiring.md.

## Sources

[02f_economy_plan.md](../../../review/37_growth/02f_economy_plan.md) §6; proposals/exchange_and_money.md.

*Current as of 23 Oct 2026: D2-1, D2-2, D2-25 to D2-30, D4-9, D4-17.*
