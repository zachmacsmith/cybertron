# Proposal: how buildings fit the other systems (before Package E is built)

**Status:** discussion (24 Oct). Package E (02y) is deferred until this is worked out (Zach). **Owner:** 37.2. **Affects:**
spec/economy/buildings.md and every file named below.

## Summary

Buildings touch almost every system. Most connections are already consistent (rooms as speech channels, raids by structure, home
derived from use, spoilage by fitting). Eight need a decision before Package E is built, because building it without them would
either do nothing (nobody needs to build) or break something (fuel, beds, ground). The largest is fuel: timber is both what houses
are built of and what every hearth burns, and the worlds' woods are far too small for either, so they are stripped within days.

## 1. What already fits

| System | How buildings meet it | State |
|---|---|---|
| parcel graph (D2-114 to D2-116) | buildings stand on parcels; built ground's sight 0.7; the village overview names notable buildings | fits |
| noticing and visibility (D2-85, D2-99) | inside a building one sees its room only; goods inside are unseen from outside; a building's signs (smoke when the fire is lit, a light at night, the roof mending) | fits |
| speech (D2-7, D4-30) | speaking in a building reaches those with access to it | fits; per building, not per room |
| fuse events (D2-81, D2-118) | a raid's fuse by structure (wattle none, timber 1 act, stone 3) | fits; an upgrade changes it |
| raids and defence (D2-20, D2-51) | walls multiply defence; stone less likely to be picked; burn orders | fits |
| households (D4-36) | home derived from use; occupy an empty house; build one | fits |
| decay (D2-58, D2-87) | bins, granary floor and cellar slow spoilage | fits; storage capacity new in E |
| agreements and hiring (D2-31 to D2-40) | `for` on build; wages for builders; a house paid for in instalments | fits |

## 2. What needs a decision

### 2a. Fuel and timber (the largest)

- **Timber is both the building material and the only fuel.** A hearth burns 21 over a 24-day run; a cottage takes about 13 timber
  to build. Every house built is most of a winter's fire.
- **The worlds' woods are too small.** Standing wood near the villages is 7 to 75 timber a unit of forest size (hamlet's Hollow Wood
  55, region_c's copses 10 to 20 with no regrowth, Deep Wood 420 for size 6), and regrowth (r 0.03) gives a size-2 wood about 0.45
  timber a day at most, against 2 to 3.5 a day for a village's hearths. So every run mines its near woods bare within one or two
  weeks. A year of burning (24 days) should not strip a wood that took a century to grow.
- **Proposed:**
  1. **Size woods by kind and size:** standing timber per unit of size about 300 for old forest, 100 for a managed wood, 40 for a
     copse, none for scrub; regrowth slow for old forest, faster for coppice (cut in rotation). Felling a whole old wood should take
     years, so labour and carrying, not the stock, bind.
  2. **Firewood apart from timber:** dead wood, brush and coppice poles as **firewood**, gathered by anyone (3 a unit) from a fast
     regrowing pool in woods and scrub (about 5 a unit of size, regrowing in days), burnable but not buildable; timber (felled from
     standing trees, with a tool) builds and can also burn. This is the historical split (commoners' firewood rights against the
     lord's timber) and lets houses and fires stop competing for the same stock.
- Either needs the capacity check (38.21) to compare fuel and building needs against what woods give back, not what stands.

### 2b. Beds and who sleeps where

- The engine lets household members sleep at home whatever the beds (night.py: "members sleep at home always"); only guests need a
  free bed. E's rule "people housed are the beds" is then empty for families.
- **Proposed:** members need a bed too, or sleep as `damaged` shelter (1.2 food, 1.5 cold) on the floor; **an infant shares its
  carer's bed; two children share one.** Then a family growing (Package D) needs beds, so floor, so a room.

### 2c. Heating a larger building

- Fuel is per building with a fire (0.5 a night, 2 cold) whatever its size: a hall for 25 burns what a cottage does.
- **Proposed:** a hearth warms 12 spaces; fuel scales with floor heated (a hall needs about 3 hearths' fuel, or its far end is
  `no_fuel` in the cold).

### 2d. Who may build where

- Today anyone may build on any built ground or scrub. With ground limited, a household's yard, the common and another's garden
  differ.
- **Proposed:** building on a parcel is a claim like any other (D4-23): the engine enforces only possession, so anyone can build,
  but on ground another household claims it is seen and disputed by custom or law; a parcel's ground can be claimed in part (spaces
  of it). Clearing makes a claim with grounds `cleared`.

### 2e. Children (Package D)

- Infants and children sleep in their household's house (2b); a new partnership forming a household needs a house: occupy an empty
  one, join, or build (D4-36), so ground and timber become the limit on new households.

### 2f. Rooms and access

- Access is per building now (D4-30). With rooms, a hall's room may be booked while the house's rooms stay private.
- **Proposed:** keep access per building in E; booking a room as an agreement whose leg grants access for days (a leg type agreements
  do not yet have).

### 2g. Fire and floods (later: L-21, L-23)

- Density makes fire spread (D2-72, D2-78: neighbouring buildings); storeys make escape harder (D2-50); low parcels (height 0) flood
  and wet their stores. E should record each building's parcel, structure and storeys so these can read them later.

### 2h. Materials over roads

- Timber barely travels one road by pack and stone (weight 3) less (02u), so stone houses stand near quarries and fieldstone;
  Barleyfield builds dear. This is intended (a dependence), but it should be checked in the capacity check with E's costs.

## Open questions (for Zach)

1. Fuel: size woods by kind (2a.1), split firewood from timber (2a.2), or both?
2. Beds for members, with infants sharing and two children a bed (2b)?
3. A hearth warming 12 spaces, fuel scaling with floor (2c)?
4. Building ground as a claim, disputed by custom (2d)?
5. Room bookings as an access leg in agreements, later (2f)?

## History

- 24 Oct: Zach: defer Package E; first consider how buildings integrate with the other systems; and the little forests seem to be
  stripped bare quickly in every run. Written.

## Sources

[spec/economy/buildings.md](../spec/economy/buildings.md), [02x](../../review/37_growth/02x_housing_model.py),
[02u](../../review/37_growth/02u_transport_check.md), [38.23](../../review/38_space_engine/23_region_run.md);
cybertron2/engine/night.py (sleeping places, fuel), cybertron2/specs/*.yaml (wood stocks); D2-7, D2-20, D2-50, D2-51, D2-58, D2-72,
D2-78, D2-81, D2-85, D2-87, D2-99, D2-114 to D2-116, D2-118, D4-23, D4-30, D4-36.
