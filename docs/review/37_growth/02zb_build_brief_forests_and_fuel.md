# 02zb: build brief for 37.4: forests, fuel and warmth, eating raw, seeding below capacity (Package F)

Session 37.2, 24 Oct 2026. Decisions D2-156 to D2-161. Spec: spec/environment/resources.md "Forests", spec/economy/goods.md "Fuel,
in heat" and "Eating raw", spec/economy/production.md "Wood", spec/economy/lodging.md "Shelter and fire" (all 37.2's). Proposals
forests.md, recipes.md §17; models 02z (forests), 02za (what a node keeps). 37.2 does not build; Zach decides when this is built.

## Why

Nearly every run dies of fuel: worlds' woods are sized on standing stock (7 to 75 timber a unit of size near villages, some with no
regrowth), so they are stripped within one or two weeks; grain, flour and beans are worth nothing without a fire, so people die by
full stores. This package makes fuel a yearly flow from a wood's health, adds firewood, separates shelter from fire, lets some food
be eaten raw, and seeds worlds below what they sustain.

## 1. Order

1. **Forests** (resources.md): a forest parcel's `wood` becomes three stocks: trees, young growth, dead wood, with their flows (trees
   shed dead wood in proportion to their number; brash from felling; young growth not regrowing while beasts graze there; under 40%
   trees the cover turns to scrub, and visibility follows). Kinds and magnitudes as the table.
2. **Fuel in heat** (goods.md): a hearth needs 1 heat a normal night, 4 a cold one; timber 2, firewood 0.5 (a new good, weight 1,
   burns only), charcoal 6 (now also in hearths); a fire draws by the household's order (firewood, timber, charcoal).
3. **Techniques** (production.md): gather firewood (basic, no tool, children may, less as dead wood thins), cut young growth (a tool),
   fell (brash left), burn charcoal (as now). Children's menial work (D2-148) gains gathering firewood.
4. **Shelter and fire** (lodging.md, D2-159): the shelter table; a fire in the open (2 timber, D4-49) or a camp's (1) shared by up to
   4 sleeping there (today each sleeper in the open burns their own); a fire ring half-warms 6 spaces, a hearth 12.
5. **Eating raw** (goods.md, D2-160): each food's raw value as data (grain 0.2, flour 0.5, beans 0, fresh meat 0.8, the rest full).
6. **Rights** (D2-158): dead wood and young growth on common land anyone's; trees their holder's (felling another's is heard: the
   felling's sound sign). Yours to write into world/holding.md.
7. **Signs** of the three stocks (stumps, no dead wood within reach, branches after a gale, shoots eaten where cattle get in), read by
   the eye for the land; axes heard; charcoal smoke.
8. **Seeding and checks** (D2-161): world files give woods by kind and size; the capacity check (38.21) counts what land and woods
   give back a year (02za's method) and what must be carried; worlds seeded at about 60 to 70% of the yearly flow of their scarcest
   resource. Existing worlds (region_c, hollins) need their woods restated as kinds; whether to change worlds mid-series is Zach's.

## 2. Tests

| Test |
|---|
| a copse of size 1 left alone keeps its trees and sheds about 18 firewood a year; felled to 30% it turns to scrub and sheds far less |
| young growth regrows on an ungrazed parcel and not on one with a herd on it |
| a hearth burns 2 firewood or 0.5 timber on a normal night, 8 firewood or 2 timber on a cold one |
| charcoal in a hearth gives 6 heat; a cold night needs two-thirds of a charcoal |
| two travellers sleeping out at one spot share one fire of 2 timber; five need two fires |
| a house of 10 sleepers with one hearth on 12 spaces is fully warm; a hall of 30 spaces with one hearth is partly cold |
| 100 grain with no fire feeds 20; 100 flour 50; beans nothing; bread full |
| gathering firewood takes no tool and a child can do it; felling refuses bare hands at full yield |
| the capacity check for a small village (8 plots, 2 managed wood, a copse) gives about 17 for food and 14 for fuel |

## 3. Running it

A small village seeded at about two-thirds of what its node sustains, children on, near woods of a copse and a managed wood, an old
forest a day out: read fuel by source (firewood, felled, carried), the near wood's health over the run, whether households crowd in
for the winter, deaths by cause.
