# Lodging: hosts and inns

## Summary

A night away from home costs more food than a night at home. A traveller can sleep out, be hosted by someone at the node, or lodge
at an inn. Shared file: 37.4 owns the mechanism (where people sleep, nights out), 37.2 the economics (what hosting and inns cost and
charge).

## Decided

- D4-12: a night out costs 1.5 food (2 in winter, and the cold); hosts and inns are part of the design.
- D2-68: camps and portable shelter (bedroll, tent, a camp built at a site).
- D4-49: a fire in the open takes about 2 timber a night; a camp takes 3 timber to build and 1 a night to keep lit.
- D2-159: shelter and fire separate; fires shared; a hearth's reach.
- D2-134: riders in a cart sleep as in a damaged house: 1.2 food a night on the road, 1.5 in the cold.
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
- **Shelter and fire** (D2-159): where one sleeps sets the night's food; a fire there cooks, and in the cold warms.

  | Shelter | Food a night | In the cold, no fire | In the cold, with a fire | A fire there burns | It warms |
  |---|---|---|---|---|---|
  | out | 1.5 | 2.0, and 0.3 of waking starving | 1.6 | 2 timber (D4-49) | up to 4 sleeping at that spot |
  | bedroll | 1.35 | 1.75 | 1.5 | 2 timber (in the open) | up to 4 |
  | tent | 1.2 | 1.4 | 1.25 | 2 timber (in the open) | up to 4 |
  | a camp (lean-to) | 1.2 | 1.8 | 1.5 | 1 timber (D4-49) | its 4 |
  | a house | 1.0 | 1.3 | a hearth 1.0; a fire ring 1.15 | 0.5 timber, 2 in the cold, a hearth (D2-157: 1 and 4 heat) | a hearth 12 spaces of floor; a fire ring 6, half-warm in the cold; more floor needs another hearth |

  A fire is shared by everyone it warms; fuel per person falls as more share it (a cottage's 4 at a hearth, 1 heat each on a cold
  night; a family house's 10, 0.4).
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

*Current as of 24 Oct 2026: H-5, D2-68, D2-134, D2-159, D4-12, D4-49.*
