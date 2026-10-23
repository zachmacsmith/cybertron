# Review 38.18: the valley on the rebuilt engine (run v3)

Session 37.4, 23 Oct 2026. Same world and seed as 38.15 (`cybertron2/specs/valley_s5.yaml`, 20 days, 4 Opus, 2 Sonnet, 9 Haiku),
now on `cybertron2/engine/` (D4-34). Data: `runs/v3/` (local); chronicle `runs/v3_chronicle.html`. A first attempt (v2, `runs/v2_bugged`)
was stopped on day 5: accepting an offer read the acceptor's hands instead of the offerer's, so every carried-goods trade failed, and
agents came to distrust an honest trader. Fixed and tested before v3.

## 1. Results against the old engine (38.15)

| | M1 engine (38.15) | Rebuilt engine (v3) |
|---|---|---|
| Deaths | 4 (Piers, Rohese, Elena, Warin) | 1 (Piers, day 6) |
| Journeys between villages | 15 | 38 |
| Agreements made | 0 recorded (one informal credit) | 15, all completed: spot trades, two credit sales across villages, coin for timber, grain and bread |
| Hosting | 14 nights, at one house, guests unfed | 56 hosting and grant acts, in all three villages, with and without food; across unrelated households |
| Cost | $8.85 | $10.27 (Opus $8.11, Sonnet $1.13, Haiku $0.45) |

## 2. What the general systems produced

- **A dispute settled by custom (D4-23).** The Reeds and the Hales both claim Long Field. Both reaped it the first day it was ripe,
  each seen as using a field the other claims. They then agreed a half-and-half split, kept a count, set a boundary stone before two
  witnesses, and sowed and reaped the second crop together. The engine still holds two claims. The settlement lives in their
  memories and their witnesses.
- **Credit across the road.** Warin took 6 timber now for a copper tool by day 12, and delivered on day 11. Simkin took a copper
  tool now for 8 wild food by day 7, and carried the food a day's walk to pay it. Both were settled.
- **A valley economy.** Millbrook has grain, bread and milk but no timber once Alder Copse was felled bare. Ashwood has timber but
  no food. Coppergate has coin and copper. Coin became the go-between: timber for coin, coin for grain, bread for lodging.
- **Coppergate emptied into Ashwood.** The Smiths wintered at Fenn House as guests. Six beds for nine meant some slept out in the
  cold. In spring they went home.

## 3. What nobody did

No one built, founded or joined a household, or made a claim (0 of each), though all are available. The bed shortage at Fenn House
was answered by negotiating beds, never by adding them. Likely causes, in order:
1. The morning prompt's "today you could" list leaves out building and joining (shown badly).
2. Hides, which beds need, are scarce.
3. The 20-day horizon.

Children cannot be born: the life module is designed (38.09) but not built, and its rules are not decided.

## 4. Engine faults found during the run, all fixed and tested (23 tests)

| Fault | Fix |
|---|---|
| Accepting read the acceptor's hands for the offerer's goods (v2) | `available` reads whose container it is |
| A tool in the household's store was not named when refused | the refusal names the store |
| Paying a debt by give or leave was not counted | a chokepoint hook credits gives and leaves to the creditor |
| "by autumn day 8" not understood in promises | season dates read |
| Telling a child; acting for a household one is not of | refusals say why and what to do instead |
| (Zach) the one owed should be able to count a debt paid | `release` (D4-37) |

*A run report; the decisions it led to are D4-37 and the fixes above.*
