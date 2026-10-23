# 02u: do the carrying capacities make sense? (OPEN C-1)

Session 37.2, 24 Oct 2026. Zach: check the proposed capacities (on foot 10, pack 20, pack ox 60, handcart 40, ox cart 200) with
economic analysis. Model: [02u_transport_model.py](02u_transport_model.py), costed against the engine as built; it replaces 02g's
transport model, which assumed the old engine (4 actions a round, a whole round lost on the road).

**How carrying costs now:** travel costs no work units; a round trip over a 1-day road costs one day away from home (the day at the
far end, which can be used there) and two nights out (0.5 food each beyond a night at home). A unit of work is taken as worth 1
food (02p), with 0.5 and 2 as bounds.

## 1. Cost per unit of weight per edge (round trip, empty back)

| Rung | Capacity | Cost (a unit = 1 food) | If half the far day is used |
|---|---|---|---|
| on foot | 10 | 0.70 | 0.40 |
| pack | 20 | 0.35 | 0.20 |
| pack ox | 60 | 0.12 | 0.07 |
| handcart (track) | 40 | 0.18 | 0.10 |
| ox cart (track; not built) | 200 | 0.035 | 0.02 |

## 2. How far each good travels before carrying costs what it is worth (edges)

| Good | Worth a weight | Pack | Pack ox | Handcart | Ox cart |
|---|---|---|---|---|---|
| timber, stone | 0.33 | 1.0 | 2.9 | 1.9 | 9.5 |
| grain | 1.0 | 2.9 | 8.6 | 5.7 | 29 |
| bread | 1.3 | 3.7 | 11 | 7.4 | 37 |
| charcoal | 2.7 | 7.6 | 23 | 15 | 76 |
| dried meat | 3.0 | 8.6 | 26 | 17 | 86 |
| copper tool | 13.7 | 39 | 117 | 78 | 390 |

**This is the pattern the economy wants:** bulky goods (timber, stone) double in price within one edge by pack, so they stay near
their source unless they are needed badly (fuel for the winter is); grain travels two or three edges; dense goods (charcoal, dried
meat, bread, tools) travel anywhere. It is why charcoal matters to a forge two days from the wood (D2-56) and why travellers carry
dried meat and bread (D2-60, D2-62).

## 3. Does each rung pay for itself?

- **Handcart over a pack:** saves about 7 food a full trip; pays back its cost (6 timber, 3 units) in **one trip**. On a track it
  should spread fast; only a carpenter can make one, which is the leverage.
- **Pack ox over a pack:** saves about 14 food a full trip; as capital (an ox, about 75 food as meat) it pays back in about **5
  trips**. But an ox that carries is not ploughing, and an ox ploughing a 16-plot farm saves about 96 units a season; so a pack ox
  pays its way only on a route carrying **more than about 7 full loads a season**. A merchant with no fields has no such cost, and
  can hire its ox out for the spring ploughing.

## 4. Against history (rough ranges; I do not have precise figures)

| Rung | In the game, x a person with a pack | Historically, roughly |
|---|---|---|
| pack ox | 3 | 3 to 4 |
| handcart | 2 | 3 to 5 |
| ox cart | 10 | 17 to 33 |

People and pack animals are about right. **Carts are understated by about half**: a handcart historically carries 100 to 150 kg
against a porter's 25 to 35, an ox cart half a tonne or more.

## 5. Recommendation

- **Keep foot 10, pack 20, pack ox 60** (they fit history and give the economic radii above).
- **Handcart 40 for now**, though history says 60 to 80: at 60 it would equal the pack ox on a track while costing a seventh as
  much, leaving the ox a role only off the track. Revisit when the ox cart comes.
- **Ox cart, when built (later): 300 to 400**, not 200, to match history; at that size carrying on a track is almost free, which is
  right for a later rung.
- **The engine's cheap travel** (no units for the journey, the far day usable) makes all of these cheaper than history; the economic
  radii still come out in the right order, so I would not change it for this.

## 6. The pack ox for the next region run (D2-133)

Proposed mechanics, for 37.4 to build with Package C's accompanying herd: an ox with a harness (D2-23) carries 60, on any road (no
track needed), led by a person of its household; it travels with that person's party, grazes on stretches with grass (farmland,
plain, river valley, a meadow) and otherwise eats 1 hay a day from the load; it is part of its owner's herd, can stray if left
unwatched, and can be taken. The merchant starts with one ox and a harness, and keeps one handcart.
