# Lodging: hosts and inns

## Summary

A night away from home costs more food than a night at home. A traveller can sleep out, be hosted by someone at the node, or lodge
at an inn. Shared file: 37.4 owns the mechanism (where people sleep, nights out), 37.2 the economics (what hosting and inns cost and
charge).

## Decided

- D4-12: a night out costs 1.5 food (2 in winter, and the cold); hosts and inns are part of the design.
- D2-68: camps and portable shelter (bedroll, tent, a camp built at a site).
- H-5: a lack of shelter raises the food needed, and in the cold carries a 0.3 chance of waking starving.

## Mechanics

- **Sleeping out:** the night-out food rate and the cold (H-5, D4-12).
- **Hosted:** a guest sleeps in a house whose holder (or a member of the household) welcomes it; it is sheltered as the household is.
- **With gear or a camp** (D2-68):

  | Shelter | Made from (technique) | Weight | Lasts | Sleeps | A night out (winter) | The cold's fall |
  |---|---|---|---|---|---|---|
  | none | | | | | 1.5 (2.0) | yes |
  | bedroll | 1 hide, 1 unit (basic) | 1 | about 40 nights | 1 | about 1.35 (1.75) | halved |
  | tent | 3 hides, 2 timber poles, 2 units (leatherworker) | 6 | about 30 nights | 2 | about 1.2 (1.4) | none |
  | camp at a site (a lean-to and a fire ring) | 3 timber, 1 unit (basic); a fire burns 1 timber a night | none: it stays where built | about 10 nights, then decays | 4 | about 1.2 (1.5 with the fire lit) | none |

  Gear wears a night of its life each night used. A camp stays at its site after its builder leaves; anyone there may use or mend
  it (its holder, if any, may set who: world/holding.md).
- **At an inn:** a building with beds that lets them to travellers on terms its holder sets (buildings.md: rooms can be booked).

## Data

Per night: where each agent sleeps (home, a host's house, an inn, out).

## Parameters

| Parameter | Value | Status |
|---|---|---|
| a night out | 1.5 food; 2 in winter | decided (D4-12) |
| an inn's beds, prices, food | 02g §4 | calibrate |
| gear and camps: lives, food a night, weights | above | decided (D2-68); calibrate |

## What agents see

Where they can sleep tonight and on what terms ("the inn has beds at 1 food a night; Mara has offered you a place by her fire").

## Open

- Inns as information hubs and letter drops; hosting customs: proposals/transport_and_lodging.md.

## Sources

[02g §4](../../../review/37_growth/02g_resources_and_transport.md), 38.05 §3; proposals/transport_and_lodging.md.

*Current as of 23 Oct 2026: H-5, D2-68, D4-12.*
