# Birth and death: partners, children, growing up, old age, succession

## Summary

Children come only when two people choose it and spend work trying. A pregnancy costs the mother food and, late on, work; a birth
carries risk; an infant and a child cost their household food and a carer's time, and do small work by the head's standing order.
At the end of childhood a child becomes an agent (a youth) with memories of what it lived through. Every span of life is counted
in days. The old die with a risk that rises with age; on a death, the household's own rules say who inherits and who heads it.

Written by 37.2 at Zach's request (24 Oct), from proposals/children.md, life.md and 38.09; the area is 37.4's. It extends
life/life_stages.md (D4-19).

## Decided

- D2-138: a child only by choice: both people, at the same node on the same day, each spend work trying; never automatic.
- D2-139: all time is counted in days: ages, stages, lifespans, the seeded tree.
- D2-140: partnering is both people's choice, even when their households arranged it.
- D2-141, D2-147: pregnancy adds about 0.3 food a day; a gap of about 4 days after a birth before the mother can conceive again.
- D2-142, D2-150: care is a choice; for now it bears on survival only; its effects on health and learning come later (OPEN L-26).
- D2-143: inheritance and the head's succession are the household's own rules.
- D2-144: no loyalty mechanic; a child carries memories of its childhood.
- D2-145, D2-151: a child's total cost is a world setting (the cost dial), built with a low and a high setting, to be tested in a
  world designed for it once this is built.
- D2-146: more units spent trying raise the chance, with diminishing returns.
- D2-148: a child's menial work is set by the household head's standing order.
- D2-149: old age is tuned to a life expectancy under each health regime; disease adds later (OPEN L-9).
- D2-152: any two people of opposite sex at the same node can try for a child if both choose; a partnership is not required.
- D4-19, D4-20: short childhoods in days; one agent, one model, for life.

## Mechanics

### Partners (D2-140)

- `partner {with}`: when both choose it on the same day at the same node, a partnership is recorded (in the family tree). `part`
  ends it; so does death. Partners may live in one household (`join`, `admit`: D4-36) or apart.
- A marriage arranged between households is an agreement between their heads (economy/agreements.md); it binds nobody to partner:
  the two still choose.

### Trying for a child (D2-138, D2-146, D2-152)

- `try for a child {with, units}`: both, at the same node on the same day, each spending the units (1 or more). Opposite sex
  (the engine records sex); both adults; the woman not pregnant and not in a gap.
- That night, if both sleep in the same building, camp or place out and neither went hungry, the woman conceives with chance
  **0.5 x (1 - e^(-0.5 x units))**, the units being what each spent (about 0.20 for 1, 0.32 for 2, 0.39 for 3, 0.48 for 6).
  Keyed draw (D2-70).
- Nobody is told of a conception; it shows later as signs.

### Pregnancy and birth (D2-141, D2-147)

- **5 days.** The mother needs about 0.3 food a day more. In the last 2 days she has 1 unit a day fewer, and each day on the road
  then carries 0.05 of losing the child.
- **Signs** from the third day ("Maud moves slowly now, near her time"), noticed by the usual rule (information/noticing.md).
- **Birth** on the night ending the fifth day, wherever the mother is. Risks that night:

  | | Housed and fed | Out, cold or hungry |
  |---|---|---|
  | the mother dies | 0.02 | 0.06 |
  | the infant dies | 0.03 | 0.10 |

  An adult other than the mother present that night halves both. A birth is a sign seen by those present; the household knows at once.
- The child belongs to **the mother's household**; both parents are in the family tree; it is named from its line's names.
- **The gap:** 4 days from the birth before she can conceive again.

### Infancy and childhood (D4-19, D2-142, D2-145, D2-148, D2-150)

| Stage | Days | Eats a day (from its household's store or its carer's hands) | Care | Does | Dies a day |
|---|---|---|---|---|---|
| infant | 2 | 0.5 | `work {what: care, at: <child>}` by anyone at its place, the units a day the dial sets | is carried with its carer if she travels (weight 2) | 0.02 cared for; 0.08 not; x2 hungry; x2 on a cold night without a fire |
| child | 4 | as the dial sets | at the high setting, minding as the dial sets | menial work by the head's standing order, up to the units the dial sets: minding a herd, keeping the watch (D2-21), foraging or fetching at a low skill | 0.005; x4 at the high setting if not minded |

- No model call for an infant or a child. A child can't be spoken to (as built) but is present: what happens where it is goes into
  its memories.
- **Care counts** on a day if someone did the care work for that child at its place that day; for now it bears on survival only
  (D2-150). Health and learning from care come later (OPEN L-26).

**The cost dial** (D2-145, D2-151), a world setting:

| Setting | Infant care, units a day | Child: eats, works, minding a day | A child's cost in all before it is an agent |
|---|---|---|---|
| **low** | 1 | 0.7 food, 1 unit of work, no minding | about 3 to 7 food and units |
| **high** | 3 | 1.0 food, 0.5 unit of work, 1 unit of minding | about 15 to 20 |

### Coming of age

- After its 2 infant and 4 child days a child becomes **a youth: an agent**, with its model chosen then (D4-20: the heir to a pole
  seat takes that seat's model; the rest keep the cast balanced).
- It starts with **lasting memories** of what it was present for (information/memory.md): who cared for it and fed it, who was away,
  births and deaths, raids, cold nights; its household's crafts as awareness (D4-33); the places it has been.

### Life spans (D2-139, D2-149)

| Stage | Days | Units a day |
|---|---|---|
| infant | 2 | none |
| child | 4 | menial only |
| youth | 12 | 4; learns faster (D4-19: practice counts double) |
| adult | 50 | by season (agents/work.md) |
| elder | until death | 5 |

- **Death** each night, beyond hunger, cold and wounds (as built): an adult **0.001**; an elder **0.01, doubling every 20 days into
  old age** (about a third to a half of elders die in a 24-day run). These are tuned later to a chosen life expectancy under each
  health regime; disease adds to them when it exists (OPEN L-9).
- A death is seen by those present and never announced (D2-4); the dead leave everything where they die (D2-87).

### Inheritance and succession (D2-143)

- Each household has rules, seeded per line and changeable by the household: **inheritance** (`eldest`, `partible`, `household`)
  and **succession** of its head.
- The head may `name heir {person}` at any time (a member of the household). On the head's death: the named heir; else, within 2
  days, each adult member may `name head {person}` and the one named most becomes head; else the eldest adult (as built). This is the
  household-sized case of offices and succession (law.md); built general enough to serve them later.
- The dead's claims pass by the inheritance rule (world/holding.md); goods stay where they are, so an heir far away must come for
  them.

### Seeding in days (D2-139)

The generator dates the family tree in days, with these spans: stages follow days since birth; founders three or four generations
back (a few hundred days); no calendar years anywhere (replacing generate.py's ages in years: child under 12, youth under 18).

## Data

Per person: born (day), sex, parents, partner, stage, pregnant since, gap until, cared for today. Per household: inheritance rule,
succession rule, named heir. Per world: the cost dial's setting.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| conception chance | 0.5 x (1 - e^(-0.5 x units)) | decided (D2-146); calibrate |
| pregnancy, gap | 5 days; 4 days; +0.3 food a day | decided (D2-147); calibrate |
| birth risks | above | proposed; calibrate |
| infant and child costs and deaths | above, by the dial | proposed (D2-145); calibrate |
| youth, adult | 12 days, 50 days | proposed; calibrate |
| death | adult 0.001; elder 0.01 doubling every 20 days | proposed (D2-149); calibrate |

## What agents see

Partnerships; a pregnancy as signs; a birth; their infants and children in their household lines, with whether each was fed and
cared for; the care option where a child is; the children's work; a child coming of age; an elder failing; a death and who inherits,
as each saw or was told it.

## Open

- Care's effects on health and learning (OPEN L-26); beliefs and values passed to children (OPEN L-25).
- Disease (OPEN L-9).

## Sources

[proposals/children.md](../../proposals/children.md), [life.md](../../proposals/life.md),
[38.09](../../../review/38_space_engine/09_life_design.md); 02v_children_model.py.

*Current as of 24 Oct 2026: D2-138 to D2-152, D4-19, D4-20.*
