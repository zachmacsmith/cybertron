# Proposal: exchange and money

**Status:** partly accepted: D2-1, D2-2, D4-17 (a shop needs a shopkeeper); the rest discussion (23 Oct). **Owner:** 37.2.
**Affects:** spec/economy/money_and_markets.md; agents/actions.md (offer and accept, with 37.4); institutions/ (tolls, levies, with
37.3).

## Summary

Goods change hands only between people at the same node, through **escrowed swaps** that settle at once, and **standing offers** at
the node's market. Prices are per node and known elsewhere only as dated beliefs. **Coin is carried like any good; debts are records
that move only as information** (D2-1). Routine deliveries run on standing arrangements, not on one-off trades, because the cost of
exchange decides whether specialising pays at all (02b).

## The proposal

### E1. Exchange at a node (02f §3)

- **The swap:** one side offers (give X, want Y, to a named person or to anyone here); the other accepts; nothing moves until both
  hold what they promised. 37.4's `offer` / `accept` (38.05 §4) is the mechanism.
- **Standing offers** at a node's market ("3 bread a round for 1 blade-share", until cancelled or unpaid): one action to post or take.
  **A shop needs a shopkeeper** (D4-17): goods are sold only by someone present to hand them over.
- **Prices per node:** each node records its trades; agents there see the last few rounds; elsewhere only what they saw or were told,
  with its age (02f §6.4).

### Standing arrangements

Supply, payroll, consignment (carry my goods, sell them there, bring back the price) and subscriptions as **standing orders and
contracts** (38.06 §4 policies; 37.3's instruments). The market board sets terms; deliveries run without a model call.

### E5. Money and credit (02f §3; D2-1)

- **Coin:** light, durable, carried. Settling a debt needs coin or goods to be carried.
- **Debts:** records both parties hold (a tally, a note, an entry in a ledger at a node: a merchant house, a temple). They move only
  in person or by letter.
- **Tolls, taxes and levies:** at passes, bridges and gates (02k §2: a toll as a gate's payment rule, the town's revenue for its
  wall and keeper); levies and fines are debts paid by carrying ([law.md](law.md)).

### The merchant (D2-2)

One merchant household with a cart is seeded in the first region; anyone else may trade. Merchants profit from price gaps and from
knowing them first; they also carry letters and news (information_economics.md).

## Why

- **Run 2:** trade on good faith failed both ways (the Irons handed over 9 blades before payment; Wynn did not pay). The swap is the
  cheapest, most general fix, and it makes prices exist.
- **02b:** institutions give about 2.1x autarky's productivity at the calibration target (load 25% against 53%), and the cost of
  exchange is the largest term. At half a unit per unit traded the gain disappears. Standing arrangements, pooled household stores
  and institutional stores move goods at almost no work per unit.
- **Carried coin** keeps the transport problem real: if coin teleported, merchants would never carry value home and only bulky
  goods would face distance.

## Alternatives considered

- **Money and credit move anywhere** (37.4's early proposal): rejected, D2-1.
- **Merchants emerge from delay alone:** rejected for first worlds, D2-2.
- **A global market:** rejected; markets are per node.
- **Trust only (no escrow):** run 2 showed it fails.

## Open questions

1. Prices: how many rounds of a node's trades agents see (02f §6.4).
2. Coin's metal (copper first; silver as the hard tier, 02g §1c) and who mints.
3. Ledgers: which institutions keep them, and whether a ledger at one node can settle a debt recorded at another (letters of credit,
   later).
4. Default: what a broken consignment or credit costs, and what remedy exists (37.3's courts).
5. Subscriptions and standing payments: as standing orders (38.06 §4, deferred by D4-16) or as contracts.

## History

- 22 Oct: 02b: exchange cost is the first design problem; standing contracts and routine orders come before markets.
- 22 Oct: Zach: purchases and payments are fair; markets can sell subscriptions, not just one-offs (old-engine discussion, carried
  over).
- 22 Oct: 02f E1 and E5 written for cybertron2 after run 2's failed trades.
- 22 Oct: Zach agreed coin is carried and debts move only as information (D2-1), and one merchant household seeded (D2-2).
- 22 Oct: 37.4: a shop needs a shopkeeper (D4-17); offer and accept in the day's order (38.05 §4).
- 23 Oct: tolls as a gate's payment rule (02k §2).

## Sources

[02f §3, §6](../../review/37_growth/02f_economy_plan.md), [02b](../../review/37_growth/02b_productivity.md),
[02k §2](../../review/37_growth/02k_fuses_and_gates.md), 38.05 §4, 38.06 §4; D2-1, D2-2, D4-16, D4-17.
