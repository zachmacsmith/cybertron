# Goods

## Summary

The goods decided so far, what each is for, and where it comes from. The full first-world set (about ten goods, chosen by a pruning
rule) is still a proposal; this file lists only what decisions have fixed.

## Decided

- H-6: wild food from foraging and hunting.
- D2-11, D2-13, D2-17: grain from fields, with seed kept back; worlds start with grain in store.
- D2-6, D2-18: livestock (cattle and horses), bred not made.
- D2-3: stone, needed for large and tall buildings.
- D2-1: coin, carried.
- D2-10: no clothing (parked).
- D2-19: a short metal ladder in first worlds.
- D2-23: the tool set (production.md).
- D2-24: copper, salt, documents, hides and timber are in the first worlds.
- D2-157: fuel in heat; firewood a good (weight 1, 0.5 heat, burns only); timber 2 heat; charcoal 6 heat and burns in a hearth.
- D2-160: each food's value raw (below).
- D2-87: goods left in the open are held by nobody; food in the open spoils much faster than in a house (rates: calibrate).
- D2-41: meat, dense but quick to spoil fresh. D2-42: milk, by a learned technique, from a cow in milk. D2-47: cheese.
- D2-56: charcoal is a good; shore salt sun-dried, inland salt boiled; fields yield some fieldstone.
- D2-60, D2-62: flour, bread and dried meat.
- D4-9: every good crosses between nodes only by being carried.

## Mechanics

| Good | Comes from | Used for | Decided by |
|---|---|---|---|
| wild food | foraging, hunting, traps | eating | H-6, D2-23 |
| grain | reaping a field | eating; seed; fodder | D2-11, D2-17 |
| livestock | breeding | draught, dung, riding (livestock.md) | D2-6, D2-18 |
| stone | a quarry; a little fieldstone from fields | hearths, large and tall buildings, walls | D2-3, D2-20, D2-56 |
| coin | (to decide: its metal) | payment | D2-1 |
| tools, plough, harness, saddle, cart, weapons, traps | made (production.md) | production, transport, fighting | D2-23 |
| timber | felling at a forest | fuel, building, carts, tools, fittings | D2-24 |
| copper | mining a seam, then smelting | tools, blades, fittings, coin | D2-24 |
| charcoal | timber burned in a clamp at the wood | fuel for smelting and smithing; much lighter to carry than timber | D2-56 |
| salt | sun-dried on the shore, or boiled at an inland spring | keeping meat and fish; cheese; cattle | D2-24, D2-56 |
| hides | slaughter and the hunt | harness, saddles, packs, parchment | D2-24 |
| documents | written on parchment (from hides) | letters, records, deeds, ledgers (information/) | D2-24 |
| meat | the hunt, slaughter | eating: more food per unit than other food; spoils fast unless salted | D2-41 |
| milk | milking a cow in milk (a learned technique) | eating, fresh the same day | D2-42 |
| cheese | milk, a little salt, work, aged in a cool room or cellar | eating; keeps and travels | D2-47 |
| flour | grain ground at a mill | porridge (1.0 food a grain against 0.7 whole); bread | D2-60, D2-61 |
| bread | flour baked at a hearth or an oven | eating (1.3 food a grain); keeps; eaten without a hearth | D2-60 |
| dried meat | meat dried to about half its weight | eating; keeps and travels | D2-62 |

Every good is an item with a quantity, held by someone or stored in a container at a place, with a weight for carrying
(transport.md) and, where it decays, a spoilage rate.

## Fuel, in heat (D2-157)

| Fuel | Heat | Weight | Got by |
|---|---|---|---|
| timber | 2 | 2 | felling standing trees, with a tool; also builds |
| firewood | 0.5 | 1 | gathering dead wood by hand (children may), or cutting young growth with a tool; burns only |
| charcoal | 6 | 2 | burning 5 timber at a wood (2 units, a woodsman); burns in a hearth or a forge |

A hearth needs 1 heat a normal night (cooking) and 4 a cold one; a year is about 21 timber or 84 firewood. A fire draws from the
household's fuel by its order (default: firewood, then timber, then charcoal). Fires in the open and in camps: lodging.md (D2-159).

## Eating raw (D2-160)

| Food | At a fire | Raw |
|---|---|---|
| bread, cheese, dried meat, milk, wild food | as listed | the same |
| flour | 1.0 (porridge) | 0.5 |
| grain, rye | 0.7 (boiled) | 0.2 |
| fresh meat | 1.5 | 0.8 (a chance of sickness once disease exists, OPEN L-9) |
| beans | 0.6 | 0 |

## Decay (D2-87)

Every item says how it decays under each condition, as data. The rate in a house is multiplied by every condition that applies.

| Item | In a house a day | Open, dry | Open, wet | Buried | Warm season | Frozen | Becomes |
|---|---|---|---|---|---|---|---|
| grain | 0.5% (D2-58; bins, cellar, granary lower) | x4 | x10 | x2 | x1.2 | x0.5 | nothing |
| bread | about 2% | x3 | x8 | x3 | x1.5 | x0.2 | nothing |
| fresh meat | about 15% | x2 | x2.5 | x1 | x1.5 | x0.1 | rotting meat |
| dried or salted meat | about 1% | x2 | x6 | x2 | x1.2 | x0.5 | nothing |
| cheese | about 1% | x3 | x5 | x1 | x1.5 | x0.3 | nothing |
| hides | none | 1% a day | 3% a day | 2% a day | | | nothing |
| timber, charcoal | none | none | wet: no use as fuel until dried (a dry day under a roof) | | | | |
| tools, coin, ore, stone | none | none | | | | | |

Rotting meat and rotting food are things with a disease risk where they lie (world/things_in_places.md, D2-96). "Open, wet" is a
day of rain, heavy rain or snow (environment/scheduler.md), or a flooded parcel.

## Data

Items in holdings and containers: kind, quantity, wear (for tools), and the container's place.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| weights, spoilage rates, costs to make | 02g §1, 02j model | calibrate |
| decay by condition | the Decay table | proposed (D2-87); calibrate |

## What agents see

What they carry and what is in the stores they may use, by name and rough quantity; spoilage in words ("the meat will not keep
past tomorrow").

## Open

- Recipes and numbers for each good; the pruning rule; unlocks: proposals/resources_and_goods.md.
- Goods kept for later: proposals/economy_later.md.

## Sources

[02g §1-§1f](../../../review/37_growth/02g_resources_and_transport.md), [02j](../../../review/37_growth/02j_end_uses.md);
proposals/resources_and_goods.md.

*Current as of 24 Oct 2026: H-6, D2-1, D2-3, D2-6, D2-10, D2-11, D2-13, D2-17, D2-18, D2-19, D2-23, D2-24, D2-41, D2-42, D2-47, D2-56, D2-60, D2-62, D2-87, D2-157, D2-160, D4-9.*
