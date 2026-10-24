# 38.28: Package F (forests, fuel in heat, eating raw, seeding below capacity) built; Hollins 2

Session 37.4, 24 Oct 2026. Built from 37.2's brief 02zb (D2-156 to D2-161). Code on `wp/cybertron2`: cybertron2/engine/forests.py
and capacity.py (new); world.py, night.py, verbs.py, knowledge.py, signs.py, perceive.py, prompt.py, run.py, data.py (FORESTS,
heat, raw values, firewood, the gather and cut techniques). Tests: tests/test_cybertron2_package_f.py (the 9 of 02zb §2) and
test_cybertron2_hollins2.py (3); 145 cybertron2 tests pass.

## 1. What was built (02zb §1)

| Item | Built |
|---|---|
| 1. Forests | a forest or scrub parcel holds `wood` (its trees, timber), `young` and `dead` (firewood); world files give `wood: {kind}` (old forest, managed wood, copse, scrub) at 02z's magnitudes a unit of size; each night trees grow, young growth regrows unless a herd is on the parcel, trees shed 1% a year of their timber as dead wood (4 firewood a timber), dead wood rots 30% a year, a gale throws trees; under 40% of its trees a forest's cover is scrub |
| 2. Fuel in heat | timber 2, firewood 0.5 (new, weight 1), charcoal 6 (now in hearths); a hearth 1 heat, 4 in the cold; a fire draws firewood, then timber, then charcoal |
| 3. Techniques | gather firewood (no tool, basic, children may; 3 a unit at a full pool, less as it thins); cut young growth (a tool, 5); felling leaves brash; children's work gains firewood |
| 4. Shelter and fire | a fire in the open (4 heat) or a camp's (2) shared by up to 4 sleeping there; a hearth warms 12 spaces of floor, a ring 6 (half in the cold); a house too big for its hearths is partly warm |
| 5. Eating raw | grain and rye 0.2, flour 0.5, beans 0, fresh meat 0.8; the rest full |
| 6. Rights | world/holding.md "Wood" (D2-158): dead wood anyone's; young growth anyone's on common land; trees the holder's |
| 7. Signs | dead wood picked clean, scarce or lying thick; branches down after a gale; shoots browsed where beasts get in; shoots from the stumps; the ring of axes |
| 8. Seeding and checks | capacity.py: the people a node's land feeds and its woods keep warm a year (02za); 38.21 prints it; worlds seeded at about 60-70% |

Choices the spec left open: OPEN Q-23.

## 2. What the check says of the worlds we ran

| World | Node | People | Food keeps | Woods keep warm | |
|---|---|---|---|---|---|
| Hollins (h1) | Ockley | 11 | 26 | 0.0 | its copse (12 timber) kept nobody warm |
| Hollins (h1) | Hollins | 8 | 1.2 | 0.2 | 40 times over |
| Hollins 2 (h2) | Ockley | 12 | 26 | 21 | 57% |
| Hollins 2 (h2) | Hollins | 8 | 1.2 | 8.6 | food binds: grain from Ockley, game from the forests beyond |

Both earlier runs died of fuel because their woods were sized on standing stock (02zb "Why"); the check makes that visible before a
run.

## 3. Hollins 2 (Zach's request)

Zach: "design a similar run to this one to test how it goes, with a few households, and one having custom to explore and expand
out, and another to have all the children expansion etc., and one to just improve and build out the farms"; and "seed the village
with a custom for expanding their family and reach".

cybertron2/specs/hollins2.yaml (base) and hollins2_s8.yaml (seed 8): 20 people in three households, 48 days, lifespan 48, children
on (low dial), Package F woods.

- **The Thornes** (Ockley; head Payn, Opus): "land well kept is the only wealth that lasts: break the fallow, dung every field, pick
  the best seed, ditch the wet ground and keep the plough going". Long Field, Fallow Field, the Granary, cattle with two oxen, a plough.
- **The Webbs** (Ockley; head Thurstan, Opus; two couples): "a house is as strong as its children: take a partner young, have
  children and raise them well, and send your grown sons and daughters out to clear ground and build houses of their own". Middle
  Field; a house of 8 beds to grow into; can build rooms and beds.
- **The Hunts** (the hut at Hollins; head Osric, Opus): "the wood beyond the wood is where a family's future lies: go further than
  anyone has gone, learn the ways and the places, make camps and huts where the game and the timber are good, and bring others".
  Hunting, packs, camps, felling, charcoal; bedrolls.
- Customs held by households: D4-57 (proposals/household_customs.md, retrospective).
- Woods: Ockley a copse and a coppiced wood of size 3 (the Hanger); Hollins a copse of 2 and a hazel coppice; beyond Hollins the same
  three ways as Hollins 1, each two or three places deep, now as old forests, managed woods and copses.
- The generated tree gave adults mostly near old age (35 to 47 days at lifespan 48), so they would have turned elder within days;
  adults of 30 days or more were made younger by hand (18 + (age - 18) x 0.45), a README-allowed edit noted in the file. Four
  couples of age: two Webb, one Thorne, one Hunt.
- Gates: each household holds its own way (one married in keeps her birth house's too); firewood is had in Ockley and its woods keep
  it at about two-thirds; couples can try; four ways out of Hollins. A 48-day bot run kept every hearth lit (the bots die of food: they
  don't sow).
- Running as runs/h2_hollins.
