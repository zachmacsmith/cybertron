# 37.2o Livestock numbers: kinds, breeding, fodder, work, products, herding, prices

*23 Oct 2026. Analysis for Zach; nothing here is decided. Model: [02o_livestock_model.py](02o_livestock_model.py). Units are work
units (6 a day); 1 food is about 1 unit (02m). A 40-day year (D4-13 allows 16-60). Decided in principle: D2-6, D2-18, D2-23, D2-41,
D2-42, D2-45, D2-47. Numbers come from historical orders of magnitude (small medieval cattle and horses), scaled to the compressed
year; all to calibrate.*

## 1. Kinds and roles

| Kind | Animals | Roles |
|---|---|---|
| cattle | cows, bulls, steers, oxen, calves | cows calve and give milk; one bull serves about 20 cows; **an ox is a steer trained to the yoke** (about 6 units of a handler's work over several days, with the technique "yoke an ox": D2-43's farmer and herder); oxen work in **pairs** under a yoke, for the plough and the cart |
| horses | mares, stallions, geldings, foals | a horse must be **broken** before it is ridden or harnessed (about 12 units of a horse breaker's work over days); it eats grain on working days |

**A team is two oxen,** not one (a light plough or a cart is pulled by a yoked pair). 02l priced one.

## 2. Breeding

| | Cattle | Horses |
|---|---|---|
| births a female a year | 0.7 | 0.5 |
| young surviving | 0.85 | 0.85 |
| to work or first birth | 3 years (120 days) | 4 years (160 days) |
| working life; lifespan | 8; 12 years | 12; 18 years |
| herd growth a year, no slaughter | about 18% | about 14% |
| in a 25-day run | +12% (2-3 calves in a herd of 20) | +9% |

**No animal born in a run grows up in it.** Within a run of 20-30 days, herds and their ages are what seeding gives (D4-21); the
calves born are stock for later years. Breeding matters across years and generations, not inside a run: the sustainable offtake
(meat, sales, gifts) is about 15% of a herd a year.

## 3. Fodder and land

| A head a year | Outdoors | In stalls (D2-45) |
|---|---|---|
| summer grazing | 0.5 plot of pasture (2 head a plot) | the same |
| winter hay (1 hay = a head's winter day) | 10 hay: 3.3 units to cut; 0.83 plot of meadow | 8 hay: 2.7 units; 0.67 plot |
| land in all | 1.33 plots | 1.17 plots |
| grain given up where land is short | about 16 food | about 14 food |

- **Straw** from each grain plot winters part of a beast: about 1.7 plots' straw a stalled head. Mixed farms need less meadow.
- **Horses** eat about 1.2 hay a winter day, and **about a ration of grain on each working day** (and a fifth of one idle): cavalry
  competes with people for grain.

## 4. Work

| | Number | Basis |
|---|---|---|
| a team and one ploughman | 8 plots a day (0.75 units a plot) | 02l; a medieval team ploughed about an acre a day |
| an ox cart | 200 capacity, one edge a day, 2 oxen | 02g §3 |
| a pack ox | 60 | 02g §3 |
| a rider | about 2.5 edges a day on a track | 02g §2b |
| mounted fighting | +3 strength | 02g §2b |

## 5. Products

| Product | Number | Basis |
|---|---|---|
| milk | 0.8 food a day for a cow in milk; in milk 0.6 of the year after calving; about 19 food a cow a year; a unit milks 3 cows | 2-3 litres a day for a small medieval cow |
| cheese | 6 milk (2.4 food) with 0.2 salt and 1 unit make 1 cheese (2 food): 83% of the food kept, for weeks | 10 litres to a kilo of cheese, whey drunk |
| meat a slaughter | cow 40, ox 50, calf 10, horse 40 meat (meat feeds 1.5: D2-41) | about 100 kg of meat from a small medieval cow |
| hides | 2 a beast, 1 a calf | 02m |
| dung | manures 2 plots a head a year | 02l |

**Milk is interest; meat is principal.** A cow's milk over its working life is about 154 food against 60 for its meat now. Eating
the herd is a famine's choice, and costs the milk, the calves and the draught of the years after.

## 6. Herding

- Any herd needs watching: at least **1 unit a day** for a household's one or two beasts; **one herder watches about 30 head** (0.2
  a head). An unwatched herd strays and is easy to rustle.
- So a household keeping its own pair pays about 40 units a year to watch them; in a common herd it pays about 16. That is the
  common herd's scale economy (02l §5), and children's work (D4-19) lowers the household's cost.
- **The commons problem:** common pasture regrows like the forest's plants; more beasts than it carries run it down. Its answer is
  a rule: so many beasts a household (a stint), whose turn to herd, who pays for the bull. An institution's work (law.md).

## 7. Upkeep, raising and price

| Animal | Land | Upkeep a year (common herd) | Cost to raise to work | Proposed price |
|---|---|---|---|---|
| ox, trained | plentiful | 11 | 25 | 50-100 coin |
| ox, trained | short | 25 | 50 | |
| cow, first calf | plentiful | 11 | 19 | 40-60 coin |
| cow, first calf | short | 25 | 44 | |
| horse, broken | plentiful | 16 | 50 | 90-150 coin |
| horse, broken | short | 32 | 88 | |

Prices sit between the cost of raising and what the animal yields: a cow gives about 19 food of milk, 0.6 calves and dung for 2
plots a year (about 40 units of value) against 11-25 of upkeep; an ox in a village team saves about 90 units of hoeing a year.
Against 02m's anchors (a coin about a food; a day's work about 6 coin; a blade 22; a cart 23), **an ox is worth about 2-4 blades,
a horse about 4-7: two to four weeks of a person's work.**

## 8. A team of two: when it pays

Plots a team must break a year to beat the hoe:

| Kept | Land | 1 crop a plot a year | 2 crops |
|---|---|---|---|
| a household's own team | plentiful | 24 | 11 |
| a household's own team | short | 40 | 19 |
| in a common herd | plentiful | 14 | 6 |
| in a common herd | short | 29 | 13 |

A team breaks 8 plots a day, so one team serves a whole village. **Where land is short, a team pays only for a village's
ploughing**, never for one household's few plots.

## 9. What this changes in 02l and 02m

- **02l** priced one ox and a plough at about 19 units a year (one ox, a 20-unit ox, no land). A team of two costs about 37 a year
  in a common herd with land plentiful, and 71 with land short. 02l's thresholds rise; its result (the common herd and the shared
  team beat the household where land is short) gets stronger, not weaker.
- **02m's worth table:** "plough and ox" should be a team at these costs; "cart" should carry its team (about the same again).
- **02g's ox cart** (capital 80, fodder only) understates the team by about 2-3 times; its break-even traffic rises.

## 10. Recommended decisions (for Zach)

1. Cattle in one kind with roles (cows, bulls, oxen, calves); an ox is a steer trained to the yoke by a learned technique.
2. The plough and the ox cart need a team of two oxen.
3. Herds do not grow up within a run; seeding sets their size and ages, and breeding matters across years.
4. A head needs about 1.2-1.3 plots of land a year (grazing and hay), less in stalls and with straw.
5. Horses eat about a ration of grain on each working day; a horse must be broken before use.
6. A cow in milk gives about 0.8 food a day for about 0.6 of the year; cheese keeps about 83% of it.
7. A slaughter gives 40-50 meat and 2 hides for cattle (10 and 1 for a calf).
8. Herding costs at least 1 unit a day for any herd, 0.2 a head in a herd of 30; common pasture runs down if overstocked.
9. Seed prices at about 40-60 coin for a cow, 50-100 for an ox, 90-150 for a horse.
10. Update 02l's ox costs, 02m's worth table and 02g's ox cart to carry a team of two.
