# Proposal: hiring (work for someone else)

**Status:** accepted: D2-36 to D2-40 (23 Oct); in spec/economy/agreements.md. **Owner:** 37.2, with 37.4 (the verbs, possession under D4-23) and 37.3 (employers as
institutions). **Affects:** spec/economy/money_and_markets.md, production.md; agents/actions.md (the `for` argument); world/holding.md
(possession and output); institutions/ (payroll, offices).

## Summary

Hiring is an agreement whose legs are **work one way and pay the other** (agreements.md). The one new thing is **working for
someone**: an action done `for` an employer puts its output straight into the employer's container at that node, and is witnessed
as work for them. Pay is a leg like any other: by the day, by the piece, a share of the crop, or teaching. Place does the rest: the
worker must be where the work is, the employer's store must be there, and what was done is seen by whoever is present.

## The problem it solves

Under D4-23 the engine enforces only possession: whoever reaps carries the harvest. Without more, a hired reaper holds the crop and
must choose to hand it over, the same trust problem run 2 showed with blades. And the farm model (02l §7) says the harvest peak
needs hired hands: a household can bring in about 16 plots in the window, 48 with staggered sowing, and beyond that it needs help.

## The proposal

### 1. Working for someone

- **`for: <party>`** on a work action (reap, sow, weed, fell, quarry, mine, forge, carry, build, guard): the worker spends its own
  units; the output goes into **the employer's container at this node** (its barn, house stock, store) instead of the worker's
  hands. Refused if the employer has no container here, or the worker may not use the site (the employer's claim gives it access).
- **The employer's tools:** a worker working `for` an employer uses the tools in the employer's container at the site for that work.
- **Possession still holds:** a worker can always work for itself instead, or take from the store if it has access. Working `for`
  is a choice; what it guarantees is that output done for you lands with you, and that everyone present saw it.
- **Witnessed:** "Eoin reaped the Long Field for the Alders: 9 grain into Alder barn." The employer learns it when it is there or
  when told.

### 2. Kinds of hiring (presets of agreements.md)

| Kind | The work leg | The pay leg |
|---|---|---|
| **day labour** | work `for` the employer today (a duty: some work done for it) | food or coin at the day's end |
| **piece rate** | each plot reaped, each load carried `for` the employer | per unit of the work leg (`per`) |
| **wages** | a duty every day (or on n days of each week) | every n days, until notice |
| **sharecropping** | the tenant farms the holder's plot for itself | a share of each harvest to the holder (cybertron 1's `harvest` leg) |
| **tenancy** | the tenant farms for itself | rent every n days, for the claim's access (D4-23) |
| **apprenticeship** | work `for` the master | teaching (37.4's `teach`; knowledge.md) and keep |
| **a shopkeeper** | offers made `for` the shop, from the shop's container (D4-17: the keeper is the one present) | wages |
| **a guard, a watch** | the guard duty at a place (cybertron 1's duty leg; 02k's watch) | wages, or a retainer from many (a subscription) |
| **a carrier** | carry these goods to that node and give them to X | per load, on delivery |

### 3. Checking that the work was done

The engine knows what each action did and for whom, so a duty leg can be checked as cybertron 1's were (`act:<event>` this day).
A day-labour leg is met when the worker did some work `for` the employer that day; a piece-rate leg counts units done. A missed
duty is a miss or a breach (agreements.md §2) and the pay leg it conditions does not fall due.

### 4. What it changes

- **The harvest peak becomes a labour market** at the right moment, at the right place: day labour at harvest, with a price set by
  how many hands are idle at the node that day.
- **Shops, workshops and institutions get staff** without new mechanics: the shopkeeper sells `for` the shop; the smith's
  journeyman forges `for` the master.
- **Landless people have a living** (D4-23's younger heirs): work for others, sharecrop or rent.
- **Children's work** (D4-19's menial tasks) is work `for` the household.

## Why

- One argument (`for`) and the agreements system give every form of hiring.
- It keeps possession as the engine's only enforcement (D4-23): nothing stops a worker cheating except that it is seen.
- It uses place where cybertron 1 could not: the worker has to be at the work, the store has to be there, and the witnesses are
  whoever is present.

## Alternatives considered

- **The worker carries the output and hands it over:** run 2's trust problem again; kept as the default when `for` is not used.
- **The engine assigns output to the plot's holder automatically:** rejected: it would enforce claims, which D4-23 leaves to people.
- **Wages paid automatically wherever the parties are:** rejected (D2-1, D4-9); paid where there is a path (agreements.md §2).

## Open questions (for Zach)

1. `for` on work actions, putting output into the employer's container at the node?
2. A hired worker may use the employer's tools there?
3. Duty legs checked by the engine from what the worker did for the employer that day?
4. The presets above as the first set (day labour, piece rate, wages, sharecropping, tenancy, apprenticeship, shopkeeper, guard,
   carrier)?

## History

- 22 Oct: 02l: the harvest peak needs hired hands; 37.4's verbs.md: hiring as an offer whose terms are work.
- 23 Oct: Zach: hiring, contracts and subscriptions next. Proposed: work `for` an employer, with pay legs from agreements.md.

- 23 Oct: Zach accepted all of it (D2-31 to D2-40), widening `for`: people can act and pay on behalf of others (households,
  companies, institutions), D2-37. Written into spec/economy/agreements.md.

## Sources

[agreements.md](agreements.md), [exchange_and_money.md](exchange_and_money.md), [verbs.md](verbs.md), [knowledge.md](knowledge.md),
spec/world/holding.md (D4-23), [02l §7](../../review/37_growth/02l_farming.md), 31.03 §4 (cybertron 1's Payroll); D2-25 to
D2-27, D4-17, D4-19.
