# Review 38.23: the region run (the third world of the ladder)

Session 37.4, 23 Oct 2026. `runs/w3_region` (region_s1, 20 days, 51 people: 6 Opus, 10 Sonnet, 29 Haiku, 6 children; $23.64).
World in 38.21 and region.yaml; the two smaller worlds in 38.22. No engine errors. **27 of 51 died; 24 lived.**

The run was on code from before two fixes made during it: a traveller's work and gathering for their own household away from home,
and gifts of work into another household's store (both refused in this run), and the missed-meal line naming food without a fire.

## 1. What happened

| Days | |
|---|---|
| 0-5 | Harvest at Barleyfield with hired reapers from Millford paid in grain and beds; gifts of grain to the poor Hales and Lowes; Ashwood burns charcoal; Nicol (Moor) buys a handcart and brings 11 timber and 4 charcoal to Coppergate; copper tools made and taught (7 teachings in the run). Near woods and wild food picked bare by day 5. |
| 4-9 | Fires go out in houses whose timber runs out (Lowe, Moor, Cole, Barrow). Grain is food only at a lit fire (D2-60): people die beside full stores and on the road carrying grain. First deaths day 7. |
| 10-12 | The first cold night (2 timber a hearth): every Barleyfield house and both Coppergate houses go dark; 27 miss a meal. 11 deaths in three days. |
| 13-18 | Timber trickles in and some fires relight; Ashwood (wood, little food) now starves too. The Hales, the Coles and the Bell die out. |
| 19 | No deaths on the last night (the hazard is not rolled then); 5 still hungry. |

**Deaths:** by home village Barleyfield 10 of 16 adults and youths, Millford 6 of 14, Coppergate 5 of 8, Ashwood 2 of 7, and 4 of 6
children. By model: Haiku 16 of 29, Sonnet 5 of 10, Opus 2 of 6. 12 died sleeping out (on the road or with no bed), 15 in a house,
almost all with its fire out. Households gone: Hale, Cole, Bell.

**Activity:** 106 journeys (Haiku 45, Opus 35, Sonnet 26; to Millford 39, Ashwood 31, Barleyfield 23, Coppergate 12, the Pass 1);
46 agreements; nobody went to Grey Crag or the High Moor.

## 2. Findings

1. **Fuel, not food, was the chokepoint, and it killed through D2-60.** Barleyfield held over 100 grain and could not cook it. Bennet
   (Opus, day 8): "our grain is useless without a fire". The rule was learnt in the run; several Haiku agents never connected "the
   fire went out" with "a missed meal" (Emma, day 7: "I carry 8 grain, enough to eat tonight").
2. **The world's fuel was enough in total and out of reach in practice (a design fault, mine).** The capacity check (21_capacity.py)
   compared timber needed per node (Barleyfield 76, Millford 76, Coppergate 38, Ashwood 38) with wood in the region (Ashwood 250, the
   High Moor 40, Millford 10). It did not check transport: Barleyfield is two roads from Ashwood (about four days there and back), a
   person carries 10, a cold night burns 2 a hearth. Barleyfield needed about 54 timber brought in during harvest.
3. **The intended trade did not form at scale.** Barleyfield (2.3x its food) and Ashwood (0.5x) should have traded grain for timber.
   Instead Barleyfield's people went to Millford, which had no wood, Ashwood kept its timber for its own winter, and ore was worth
   little to anyone. The only carrier with capacity was Nicol's handcart. Coppergate received about 13 timber and 4 charcoal in 20
   days.
4. **Hosting at a lit fire saved lives and was rarely given.** Bennet lived because the Reeds took him in (day 10); his father
   Thurstan died the night before when nobody let him in. Alard took in the Coles' orphan Sarra (she died anyway; Moor House went cold).
5. **Deaths changed behaviour.** After Annora and Emma died, Barleyfield's people cited them and shared grain (Beatrix, Thurstan,
   Elena); Ancel had earlier stopped the Reeds' gifts "the winter will be hard". The reapers were paid what was owed.
6. **Nobody explored**, though every near wood was bare by day 7 and the High Moor had 40 wood. The roads were shown ("Roads from
   here"); the cost of a night out while hungry and the pull of known trades won.
7. **Travel killed the weak.** Starving people set out without bread or dried meat, slept out, and died on the road (Drew, Florence,
   Reynold, Ancel, Adam). A load rounded down in the refusal ("you carry 10; you can carry 10") cost Drew a day (fixed, df9549b).
8. **Models:** Opus died least (2 of 6) and travelled most per head; Haiku travelled as much in total and died most. Model and
   role are still confounded (Opus are the household heads).

## 3. Engine changes during the run (47 tests)

| Change | Commit |
|---|---|
| a traveller's work and gathering for their own household away from home go to their hands; work given into another's store | 1931cc4 (made on day 4; not in this run) |
| a missed meal with food that needs a fire says so in the night lines (Zach: fine to tell them why after the miss) | df9549b, 97d7646 |
| the carry refusal shows the load rounded up and how much to set down | df9549b |

## 4. For the next world

- Size fuel with transport: timber per node against what can be carried in over the roads in the days available, by the people
  free to carry it.
- The same check for any good a node must import (grain into Ashwood and Millford).
- Not rebalanced here (Zach: they are allowed to die).

*A run report; the decisions it bears on are D2-37, D2-60, D2-68, D4-47, D4-48.*
