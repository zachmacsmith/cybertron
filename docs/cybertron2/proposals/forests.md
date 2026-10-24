# Proposal: the forest as a system (trees, young growth, dead wood; timber, firewood, charcoal)

**Status:** accepted: D2-156 to D2-159 (24 Oct); poles from young growth (Q4) open. Design only. **Owner:** 37.2 (author; resources and the economy); land and perception are 37.4's.
**Model:** [02z_forest_model.py](../../review/37_growth/02z_forest_model.py). **Affects:** spec/environment/resources.md,
environment_state.md, spec/economy/goods.md, production.md, buildings.md, lodging.md (fuel); spec/information/ (signs, noticing);
world/ (cover, claims); life/ (children's work).

## Summary

Zach (24 Oct): separate firewood from timber; both should depend on the health of a forest (how many trees there are); timber should
build and also burn far better (one lights a hearth where several firewood are needed for a night, so firewood costs more labour).
Proposed: a forest parcel carries **three stocks**: standing trees, young growth and dead wood. Trees shed dead wood in proportion to
how many there are; felling takes trees and leaves brash; young growth regrows fast where it is not grazed. **Timber** is felled from
the trees, with a tool, and builds or burns (2 heat). **Firewood** is gathered from dead wood by hand, or cut from young growth with a
tool, and only burns (0.5 heat, bulkier). **Charcoal** is burned from timber, light for its heat, and carries fuel far. At real
magnitudes, a small wood by a village keeps few hearths warm on what it sheds, felling it strips it to scrub and ends its dead wood,
and old forest a day or two out is effectively inexhaustible within a run: so getting fuel pushes people toward the forests, and a
near wood is a commons that can collapse.

## 1. The forest's state (per forest parcel; hidden, read through signs: environment_state.md)

| Stock | What it is | Grows | Taken by |
|---|---|---|---|
| **trees** (T, in timber) | the standing stand: its density and age | slowly (old forest about 0.5% a year, a managed wood 1%) | felling |
| **young growth** (Y, in firewood) | saplings, coppice shoots, poles | fast (50% to 100% a year), **not where beasts graze** | cutting (coppicing) |
| **dead wood** (W, in firewood) | fallen branches and dead trees | **shed by the trees: about 1% of T a year as firewood**, plus brash from felling and windfall from gales; rots about 30% a year | gathering |

**Health** is how full T and Y are against what the parcel can hold. Below about 40% trees, the cover turns from forest to scrub.

**By kind, a unit of size (about 2 ha), at roughly real magnitudes (02z):**

| Kind | Trees (timber) | Firewood a year it gives without running down | Hearths it keeps warm on that |
|---|---|---|---|
| old forest | 2,500 | about 106 | 1.3 |
| managed wood (coppice) | 600 | about 124 | 1.5 |
| copse | 300 | about 18 | 0.2 |
| scrub | none | about 9 | 0.1 |

A timber here is about 240 kg (a hearth burns 21 a year, a household's few tonnes); a firewood is a bundle of a quarter of that heat.

## 2. Fuel by heat (proposed)

A hearth needs **1 heat a normal night and 4 a cold one** (today's 0.5 and 2 timber).

| Fuel | Heat | Weight | Heat a weight | Got by | Heat a unit of work |
|---|---|---|---|---|---|
| timber | 2 | 2 | 1 | felling standing trees, with a tool (1.5 a unit, crude) | 3 |
| firewood (dead wood) | 0.5 | 1 | 0.5 | gathering by hand, no tool (3 a unit while the pool lasts, less as it thins) | 1.5 |
| firewood (young growth) | 0.5 | 1 | 0.5 | cutting with a tool (5 a unit) | 2.5 |
| charcoal | 6 | 2 | 3 | burning 5 timber, 2 units, at a wood (woodsman) | 1.1 |

So a hearth's year is **21 timber (14 units of felling) or 84 firewood (28 units of gathering)**: firewood doubles the labour of
fuel but needs no tool, no standing trees taken, and can be gathered by children. Timber is the efficient fuel and the building
material, but it is the stand itself. A hearth burns what its household chooses (a standing order: firewood first by default).

## 2a. Warmth: levels, and how many a fire warms (Zach, 24 Oct)

**Today in the engine:** a building's fire (hearth or fire ring) burns 0.5 timber a night (2 cold) and warms **everyone sleeping
in that building, however many**; a camp's fire burns 1 a night and warms the camp's 4; a fire in the open burns 2 from **each
sleeper's own hands** (two travellers at one spot each burn their own: no sharing). A house with no fire on a cold night is 1.3 food.

**Proposed: one ladder, by shelter and fire, in heat:**

| Sleeping | Fire | Heat a night (normal / cold) | Warms | Food a night (normal / cold) |
|---|---|---|---|---|
| out | none | | | 1.5 / 2.0, and 0.3 of waking starving |
| out | a fire in the open | 2 / 4 | **up to 4 sleeping at that spot** (shared) | 1.4 / 1.6 |
| a tent | none | | 2 | 1.2 / 1.4 |
| a camp (lean-to) | its fire ring | 2 / 2 | 4 | 1.2 / 1.5 |
| a house | none | | | 1.0 / 1.3 |
| a house | a fire ring | 1 / 4 | 6 spaces of floor, half-warm in the cold | 1.0 / 1.15 |
| a house | a hearth | 1 / 4 | **12 spaces of floor** (about 10 sleepers); more floor needs another hearth or more heat | 1.0 / 1.0 |

On normal nights a house's fire is for cooking (grain needs one, D2-60); in the cold it is for warmth.

**What this gives:** fuel per person falls as more share a fire. On a cold night a hearth's 4 heat warms a cottage's 4 (1 each) or a
full family house's 10 (0.4 each); a camp's fire 0.5 each; a fire in the open shared by 4, 1 each, alone, 4. So in winter it pays to
crowd in: families sleeping together, hosting a neighbour at a lit fire (which saved lives in 38.23 and costs the host no fuel), a
longhouse or a hall's hearth. Travellers do better camping together. This also fixes 2c of buildings_integration.md (a hall burning
what a cottage does) by tying a hearth's reach to floor.

## 3. What it does over a run (02z)

**A village of 3 hearths, 48 days (two winters), on a copse of size 1 (300 trees):**

| Plan | Heat got of 252 needed | Days short | The copse after |
|---|---|---|---|
| gather dead wood only (5 a day) | 34 | 39 | whole, its dead wood gone |
| gather and cut young growth (5 a day) | 55 | 33 | trees whole, young growth gone |
| fell its trees for all the fuel (2.6 a day) | 250 | 0 | 59% of its trees left |
| fell hard and sell the rest (8 a day) | 602 | 0 | **scrub: its trees gone, and the dead wood it shed with them** |

**An old forest node of size 6 (15,000 trees):** felling 4 a day for 48 days takes 1% of it; 40 a day, 13%. Its dead wood alone
keeps about 7 hearths warm.

**So:**
- **A near wood can't keep a village on firewood** unless it is large; the village fells it, which works for a while and then turns it
  to scrub, and a wood with fewer trees sheds less dead wood: **a degradation spiral**. A near wood is a commons that can collapse,
  unless people make rules (who may fell, a coppice rotation, a warden): leverage for institutions.
- **Forests further out are effectively inexhaustible within runs**, so the push is distance and carrying, not exhaustion: fell
  timber there and carry it (dense), burn charcoal there and carry that (denser), or go and live there (firewood is bulky and local).
- **Worlds choose the push** by the size and state of the near woods (region_c's copses of 10 to 20 timber are, at these magnitudes, a
  hedgerow; Hollins's 70 is a thin holt).

## 4. How it meets the other systems

**Perception** (seeing, noticing, visibility):
- Visibility is computed from the forest's state (D2-103): dense trees sight 0.2 to 0.35; thinned toward scrub 0.5; cleared, open.
  So felling opens sight lines, exposes hidden ways (D2-92) and hidden caches, and spoils an ambush's narrows.
- Signs of the forest's state, read by the eye for the land (D4-50, D2-91): "stumps everywhere in the copse now"; "no dead wood left
  within reach"; "fallen branches thick after the gale"; "young shoots eaten off where the cattle get in". Bareness (D4-50) extends to
  dead wood.
- Sounds: axes in the wood (felling is heard: a theft of another's trees can be noticed); smoke from charcoal burning (a short-lived
  state, D2-103).

**Labour:**
- Gathering firewood is basic, needs no tool and can be **children's menial work** (Package D: forage, herd, hay, and firewood), so
  children's labour is worth more where firewood is the fuel.
- Felling needs a tool (wear: about 6 crude tools for 186 timber, 02t), skill by practice, and carrying; charcoal needs a woodsman.
- Fuel's share of labour becomes visible: 14 to 28 units a hearth a year, before carrying.

**Supply chains:**
- **Building** (buildings.md, deferred E): rooms, beds, bins, granary floors, carts, ploughs and handles take timber; **wattle walls,
  hurdles and fences are poles from young growth** in history (proposed: a wattle room and a wood fence take poles, cut from young
  growth, not timber), so a managed wood houses people cheaply.
- **Smelting and smithing** take charcoal (D4-46); proposed, charcoal also burns in hearths.
- **Food:** game depends on the forest's health (its capacity rises with trees and young growth: cover and browse); forage in the
  understorey rises where the canopy is thinned (light); **herds grazing in a wood eat its young growth**, so a wood-pasture slowly
  stops renewing.
- **Trade:** by weight, firewood travels about half an edge before its carrying costs its worth, timber about one, charcoal about
  three (02u's radii): firewood is local, timber regional, charcoal far.

**Claims and institutions** (D4-23, holding.md):
- Proposed default rights: **firewood (dead wood, and young growth on common land) may be gathered by anyone; trees are their
  holder's.** The engine enforces only possession, so felling another's trees is possible, heard, and a matter for custom or law.
- The collapse of an unmanaged near wood is an institutional problem, and the coppice rotation an institutional answer.

**The environment** (scheduler.md, environment_state.md):
- Gales throw trees (T down, W up: a windfall, D2-79); drought dries dead wood (wildfire later, L-21: more dead wood, more fuel for
  fire); winter slows growth (as built, x0.25).

**Demography** (Package D): each new household with a hearth adds 21 timber or 84 firewood a year of fuel; a growing village runs its
near wood down faster.

## 5. What the engine would change

- A forest parcel's `wood` stock becomes `trees`, `young growth` and `dead wood`, with the flows above.
- New good **firewood** (weight 1, heat 0.5, burns only); fuel in **heat**: a hearth draws its night's heat from firewood, timber or
  charcoal by its household's order (default firewood, then timber).
- Techniques: `gather firewood` (basic, no tool, from dead wood, children may), `cut` young growth (a tool, gives firewood or poles),
  `fell` (from trees, leaves brash as dead wood), charcoal from timber as now.
- Signs for the three stocks; visibility from tree density; the cover's change to scrub.
- World files: woods by kind and size; the capacity check (38.21) counting what woods give back a year, and what can be carried.

## Open questions (for Zach)

1. Three stocks per forest (trees, young growth, dead wood), dead wood shed in proportion to the trees?
2. Fuel in heat: timber 2, firewood 0.5, charcoal 6 (charcoal burning in hearths); a hearth 1 a normal night, 4 a cold one?
3. Firewood basic and gatherable by children; felling needs a tool?
4. Poles from young growth for wattle rooms and wood fences, or keep those in timber for now?
5. Real magnitudes (old forest 2,500 a unit of size), with the push set by how small and worn the near woods are in each world?
6. Default rights: firewood anyone's, trees their holder's?
7. The warmth ladder (2a): a fire in the open shared by up to 4; a fire ring half-warming 6 spaces; a hearth fully warming 12?

## History

- 24 Oct: Zach: separate firewood and timber, both depending on the forest's health; timber for building and far better as fuel; how
  a forest should work as a system; and how it meets perception, other supply chains and labour. Written, with 02z (first pass at too
  small magnitudes, recalibrated to real ones).

- 24 Oct: Zach: different levels of warming (hearths, campfires); does a hearth or campfire warm many people? Added 2a.

- 24 Oct: Zach: an open fire and a camp are the same fire, different shelter (D2-159); the forest and food changes accepted (D2-156 to
  D2-160); seeding below capacity (D2-161). Spec written.

## Sources

[buildings_integration.md](buildings_integration.md) §2a, [environment_state.md](environment_state.md),
[visibility.md](visibility.md), [hidden_ways.md](hidden_ways.md), [children.md](children.md); 02t, 02u, 02x, 02z; D2-56, D2-79,
D2-92, D2-99, D2-103, D4-23, D4-46, D4-50.
