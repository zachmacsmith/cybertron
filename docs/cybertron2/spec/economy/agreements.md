# Agreements: legs, settlement, ledgers and presets

## Summary

Every trade, debt, subscription, wage, rent, supply deal, loan and due is an **agreement made of legs**, made by an offer and its
acceptance. An obligation exists wherever the parties are; it is **paid automatically only where there is a way to pay it** (both
at one node, both in one ledger, or by a carrier), and otherwise accrues as arrears. Anyone may act **for** a household, company or
institution whose container it may use. Work can be a leg, checked by the engine from what was done.

## Decided

- D2-31: one system of agreements made of legs, made by offers.
- D2-32: the settlement rule (a path, or arrears).
- D2-33: ledgers.
- D2-34: legs in any good; coin not forced.
- D2-35: built by porting `cybertron/standing.py` and `cybertron/credit.py` (37.4 changes the code).
- D2-36: work can be a leg.
- D2-37: acting for others.
- D2-38: a worker uses the employer's tools there.
- D2-39: duties checked by the engine.
- D2-40: the presets below.
- D4-37: whoever is owed may count a debt paid or forgive it; goods given or left by the debtor to the creditor are credited.
- D2-25, D2-27: offers cost no work units; a promise leg makes a debt that is only information.

## Mechanics

### Records

| Record | Fields |
|---|---|
| **leg** | id; from (party, and optionally a source container); to (party, and optionally a container); item and qty, or **work** (a duty: a kind of act done for the payee, at a place); when: `now`, `by` a day, or `every` n days from a day for a number of times or until notice; `per` (qty per unit of another leg); `bond` (paid from a deposit made up front); arrears |
| **agreement** | id; parties; legs; notice (days); remedy (none, the bond, an arbiter, a court); where and when it was made; who saw it; status (open, ended, broken) |
| **ledger** | an institution's container at its seat; for each holder, its share (a claim, world/holding.md) |

Records are information (D2-1): known to the parties and to witnesses; a written copy is a document (information/).

### Making and ending

- An agreement is made by `offer {to, legs, notice?, remedy?, lots?}` and `accept` (money_and_markets.md), at no work units. An
  offer to `anyone` with lots makes the same agreement with each acceptor (a roster: a paper's subscribers, a shop's customers).
- A party ends an agreement by **notice**, which takes effect `notice` days after the other party learns of it (told in person or
  by a letter that arrives). Leaving without notice is allowed and is recorded as a breach, with the remedy.

### Settlement (D2-32)

At the end of each day's work step, every leg that is due, or in arrears, is paid automatically if there is a path:

| Path | Condition |
|---|---|
| in person | the payer, or its named source container, and the payee, or its named container, are at the same node |
| in a ledger | both hold shares in the same ledger: the shares change; nobody needs to be there |
| by a carrier | a carrier named in the agreement holds the goods at the payee's node |

- **Spot trades** (two `now` legs) settle at acceptance, both or neither.
- **No path:** the leg accrues as arrears, shown to both; arrears are paid first when a path appears.
- **A miss:** the source does not hold enough. **A breach:** the payer held enough at the node but not in the named source, or
  moved it away, for more than the grace; the remedy applies (the bond pays; an arbiter or court rules).
- **Release** (D4-37): the person owed, or a member of the household owed, can release what is owing on an agreement when they
  judge it paid (to their household, in kind) or to forgive it. Goods the debtor gives or leaves to the creditor are credited to
  the debt automatically.
- Deposits into and withdrawals from a ledger are physical, at its seat; orders to pay from a share come in person or by sealed
  letter.

### Acting for others (D2-37, D2-38)

- `for: <party>` on work (sow, weed, reap, fell, quarry, mine, forge, build, carry, guard), on `give`, on `offer` and on `accept`:
  the act is done on that party's behalf. Output goes into the party's container at this node; payments and goods offered come from
  it. Allowed only if the actor may use that container (a household member its house stock; an officer the institution's store; an
  employee as its agreement says).
- A worker acting for an employer may use the tools in the employer's container at the site for that work.
- Acts done for another are witnessed as such ("Eoin reaped the Long Field for the Alders: 9 grain into Alder barn").

### Duties (D2-36, D2-39)

A work leg is met when the engine's record shows the worker did that kind of act for the payee on that day (at that place, if the
leg names one). A pay leg conditioned on a duty (`per` it, or due only when it is met) falls due only when the duty was done; an
unmet duty is a miss or, if the worker was free and present, a breach.

### Presets (D2-40)

| Preset | Legs | Notice, remedy (defaults) |
|---|---|---|
| spot trade | goods now <-> goods now | none |
| credit sale | goods now -> ; payment by a day <- | none; the debt |
| consignment | goods now -> carrier; proceeds or a share by its return <- | none; the debt |
| subscription | payment every n days, against a delivery or a duty every n days, until notice | notice 1 |
| supply | goods every n days -> ; payment per delivery <- | notice 2 |
| board (meals) | payment every day -> ; food every day <- | notice 0 |
| rent, lease | payment every n days, for a claim's access and withdrawal for the term (`transfer_claim`, world/holding.md) | notice set by the parties |
| loan | the sum now -> ; instalments every n days <- , growing by interest if agreed | the bond or collateral |
| dues, levies, fines, taxes | legs created by an institution's code or a law | the institution's rules |
| day labour | work for the employer today ; pay at the day's end | none |
| piece rate | each unit of work for the employer ; pay per unit | none |
| wages | work on the agreed days ; pay every n days | notice 1-2 |
| sharecropping | the tenant's access to a plot ; a share of each harvest from it to the holder | to the season's end |
| tenancy | the rent preset for land | to the season's end |
| apprenticeship | work for the master ; teaching (`teach`) by a day and food every day | the term |
| shopkeeper | offers and gives for the shop, from its container ; wages | notice 1 |
| guard, watch | a guard duty at a place each night ; wages, or subscriptions from many | notice 1 |
| carrier | carry goods to a node and give them to the named party ; pay on delivery | none; the goods are the bond |

## Data

Agreements, legs and arrears (above); ledger shares as claims; the action record (who did what for whom, where, when), which duties
are checked against.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| grace before a breach | 1-2 days | calibrate |
| default notice per preset | above | calibrate |
| interest, bonds | set by the parties | decided (agreement terms) |

## What agents see

Each open agreement as one line in words ("You rent the Long Field from the Alders: 2 grain every 6 days; next due in 3 days; you
owe 2 from before"); arrears owed to and by them; work done for them that they saw or were told of; their ledger shares as last
known.

## Open

- How porting `standing.py` and `credit.py` maps their accounts onto containers and legs onto the settlement rule (37.4, board).
- Letters of credit between ledgers; institution-issued notes: later.

## Sources

[proposals/agreements.md](../../proposals/agreements.md), [proposals/hiring.md](../../proposals/hiring.md),
[31.03 §2, §4, §5](../../../review/31_institutions/03_money_labour.md); `cybertron/standing.py`, `cybertron/credit.py`.

*Current as of 23 Oct 2026: D2-25, D2-27, D2-31 to D2-40, D4-37.*
