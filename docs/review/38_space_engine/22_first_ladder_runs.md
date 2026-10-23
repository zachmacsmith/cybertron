# Review 38.22: the first two worlds of the ladder, run with LLM agents

Session 37.4, 23 Oct 2026. `runs/w1_hamlet` (hamlet_s1, 16 days, 2 Opus, 1 Sonnet, 6 Haiku; $5.46) and `runs/w2_two_valleys`
(two_valleys_s1, 18 days, 5 Opus, 2 Sonnet, 12 Haiku, 7 children; $15.94). Worlds in 38.21. Both ran without errors; nobody died.

## 1. What the systems produced

| | Hamlet | Two valleys |
|---|---|---|
| Harvests | barley, beans, rye; barley sown again and reaped at the end | barley, oats, beans; spring sowing of beans, barley, oats |
| The frost | rye sown; hay moved to the byre; houses mended | houses mended; grain kept back for seed |
| Field works | Low Field ditched (0.75 of 2 plots), led by the one who knew how | Marsh Field's ditches kept; terraces kept and extended on Hill Field |
| Soil | dung spread on reaped fields | dung spread before sowing; fallow rested |
| Cattle | herded and milked daily; a calf born; hay cut and stored | milked; a calf slaughtered and its meat dried; the Millers' ox slaughtered in famine |
| Agreements | 6 (5 paid): work for grain, beans for coin, an old debt repaid in rye | 29 (27 done): credit across the road, work for dried meat, timber for grain and coin, hosting |
| Travel | none (one node) | 13 journeys, all by Opus agents; Simkin the first to carry bread for the road |
| Exhausted | Hollow Wood (timber 55 to 0.25, game gone) | the Alders and the Scarp (both wood 0) |
| Hunger | the Ashbys (no cattle, no plough) for one day at the end | Highcombe's Smiths early; the Millers (no fields, no grain brought to the mill) mid-run |

## 2. Findings

1. **Dependence drove behaviour.** Highcombe short of grain sent its smith to Wetham; Wetham short of wood bought it from Highcombe by
   handcart; credit across the road was repaid in kind, into the creditor's house when he was away.
2. **The mill was not a chokepoint.** Every large house had a hand mill, so nobody brought grain; the Millers starved first, ate their
   ox (the mill's power) and lived on neighbours' help. 37.2's 02n is right: a mill pays only if grinding is needed and the mill saves
   enough over hand mills.
3. **Markets were thin before winter.** Opus agents made about 9 offers each and closed about 3; "neither neighbour will sell grain".
   Prices formed only late, by bidding (Ancel: "offer more for grain than Wat does").
4. **Nobody explored.** The Old Wood (300 timber, game) stayed unknown while both villages' woods ran out. The seeded custom at
   Highcombe ("nobody goes over the scarp... nobody knows what is there") likely discouraged it, with the cost of a night out.
5. **Signs that point at a job are acted on** (weeds, standing water, slumping banks, ripeness, milk); signs about animals' condition
   are not (senses.md §4).
6. **Models by role** (Opus are all household heads, so model and role are confounded): Opus agents travel, trade, give, settle debts
   and announce; Sonnet put dozens of units into field works; Haiku do routine field work and upkeep sensibly, use about 54% of their
   units, make most refusals, and never trade beyond their village.

## 3. Engine faults found and fixed during the runs (44 tests)

| Fault | Fix |
|---|---|
| sowing without naming the seed sowed barley where rye was meant | sowing names its seed |
| ploughing blocked by a half-sown field | the unsown part can still be broken |
| a hired worker could not put the work into the employer's store (D2-37) | an open work leg gives that right, for a person and their household |
| giving to a household was not possible; `leave` only where there were roads | `give` to a household; `leave` anywhere |
| making used another house's fitting | one's own house first |

## 4. Open, not fixed

- Offers cannot describe work ("work 2 days reaping") or offer a release of a debt.
- Plans cannot wait on another's work ("sow after the ploughing").
- `give` and `leave` overlap; objects left in the open: proposals/objects_in_world.md.
- Fences: proposals/fences.md. The senses: proposals/senses.md.
- No copper ore in two valleys left the smith idle (a world design fault, not the engine's).

*A run report; the decisions it bears on are D2-37, D2-60, D2-61, D4-36, D4-47, D4-48.*
