# 02w: build brief for 37.4: children and reproduction (Package D)

Session 37.2, 24 Oct 2026. Zach wants children and reproduction specified and building as soon as possible: after Package C, ahead
of the region world (02t). 37.2 does not build. Decisions D2-138 to D2-152; spec **spec/life/birth_and_death.md** (new, in your
life area, written at Zach's request); background proposals/children.md and your life.md; model 02v_children_model.py.

## 1. Order

1. **Days everywhere (D2-139):** the generator's tree dated in days, stages by days since birth (infant 2, child 4, youth 12, adult
   50, then elder), replacing ages in years in generate.py; life_stages.md's spans in days (yours to edit).
2. **Partners:** `partner {with}` and `part` (both choose the same day at the same node).
3. **Trying and conception:** `try for a child {with, units}`, opposite sex, both adults, both choosing; the night's chance
   0.5 x (1 - e^(-0.5 x units)) if they sleep in one place and neither went hungry; keyed.
4. **Pregnancy:** 5 days, +0.3 food a day, 1 unit fewer in the last 2, 0.05 a day of losing the child on the road then; signs from
   day 3.
5. **Birth:** risks by shelter and food, halved with another adult present; into the mother's household; named from its line; the
   4-day gap.
6. **Infants and children:** eating from the household's store or the carer's hands; `work {what: care, at: <child>}`; deaths by
   care, hunger and cold; carried with the carer; children's menial work by the head's standing order; the cost dial (a world
   setting: low, high).
7. **Coming of age:** an agent at the end of childhood, its model by D4-20, its memories from what it was present for, its
   household's crafts as awareness.
8. **Old age and death:** adult 0.001 a night; elder 0.01 doubling every 20 days.
9. **Inheritance and succession:** the household's rules; `name heir`; on the head's death the heir, else the members' `name head`
   within 2 days, else the eldest adult; claims by the inheritance rule.

## 2. Tests

| Test |
|---|
| no conception unless both chose to try; same-sex pairs and a pregnant or gapped woman refused |
| the chance a night with 1, 2, 3 units each matches the formula; hungry or apart: none |
| pregnancy adds 0.3 food a day; the mother has 1 unit fewer in its last 2 days; a birth on the fifth night; the gap blocks for 4 days |
| birth risks halve with another adult present; worse out in the cold |
| an uncared-for infant dies at about four times the cared-for rate; hunger and a cold night without a fire double it |
| at the low dial a child eats 0.7 and works up to 1 unit; at the high, an infant needs 3 units a day of care |
| a child becomes a youth agent after 6 days of life, with memories of its carers and of deaths it was present for |
| a seeded world has no ages in years; everyone's stage follows their days since birth |
| the named heir becomes head on the head's death; without one, the most-named by the adult members; else the eldest |
| over a 24-day world of couples who try every day, births and new agents fall near 02v's (about 1.6 births a couple at the low dial) |

## 3. Running it

A world to test the dial (low against high) is to be designed once this is built (D2-151). Until then, worlds can run with
children on or off (a world setting), so the region world (02t) can run without births and stay a clean test of dependence.

## 4. Later, not in this package

Care's effects on health and learning (OPEN L-26); beliefs and values passed to children (L-25); disease (L-9).
