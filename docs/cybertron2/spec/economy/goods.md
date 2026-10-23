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
- D2-41: meat, dense but quick to spoil fresh. D2-42: milk, by a learned technique, from a cow in milk. D2-47: cheese.
- D4-9: every good crosses between nodes only by being carried.

## Mechanics

| Good | Comes from | Used for | Decided by |
|---|---|---|---|
| wild food | foraging, hunting, traps | eating | H-6, D2-23 |
| grain | reaping a field | eating; seed; fodder | D2-11, D2-17 |
| livestock | breeding | draught, dung, riding (livestock.md) | D2-6, D2-18 |
| stone | a quarry | large and tall buildings, walls | D2-3, D2-20 |
| coin | (to decide: its metal) | payment | D2-1 |
| tools, plough, harness, saddle, cart, weapons, traps | made (production.md) | production, transport, fighting | D2-23 |
| timber | felling at a forest | fuel, building, carts, tools, fittings | D2-24 |
| copper | mining a seam, then smelting | tools, blades, fittings, coin | D2-24 |
| salt | a spring or the coast | keeping meat and fish; cattle | D2-24 |
| hides | slaughter and the hunt | harness, saddles, packs, parchment | D2-24 |
| documents | written on parchment (from hides) | letters, records, deeds, ledgers (information/) | D2-24 |
| meat | the hunt, slaughter | eating: more food per unit than other food; spoils fast unless salted | D2-41 |
| milk | milking a cow in milk (a learned technique) | eating, fresh the same day | D2-42 |
| cheese | milk, a little salt, work, aged in a cool room or cellar | eating; keeps and travels | D2-47 |

Every good is an item with a quantity, held by someone or stored in a container at a place, with a weight for carrying
(transport.md) and, where it decays, a spoilage rate.

## Data

Items in holdings and containers: kind, quantity, wear (for tools), and the container's place.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| weights, spoilage rates, costs to make | 02g §1, 02j model | calibrate |

## What agents see

What they carry and what is in the stores they may use, by name and rough quantity; spoilage in words ("the meat will not keep
past tomorrow").

## Open

- Recipes and numbers for each good; the pruning rule; unlocks: proposals/resources_and_goods.md.
- Goods kept for later: proposals/economy_later.md.

## Sources

[02g §1-§1f](../../../review/37_growth/02g_resources_and_transport.md), [02j](../../../review/37_growth/02j_end_uses.md);
proposals/resources_and_goods.md.

*Current as of 23 Oct 2026: H-6, D2-1, D2-3, D2-6, D2-10, D2-11, D2-13, D2-17, D2-18, D2-19, D2-23, D2-24, D2-41, D2-42, D2-47, D4-9.*
