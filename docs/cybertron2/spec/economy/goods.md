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

- The rest of the first-world set (timber, copper, salt, hides, documents), the pruning rule, unlocks: proposals/resources_and_goods.md.
- Goods kept for later: proposals/economy_later.md.

## Sources

[02g §1-§1f](../../../review/37_growth/02g_resources_and_transport.md), [02j](../../../review/37_growth/02j_end_uses.md);
proposals/resources_and_goods.md.

*Current as of 23 Oct 2026: H-6, D2-1, D2-3, D2-6, D2-10, D2-11, D2-13, D2-17, D2-18, D2-19, D2-23, D4-9.*
