> **Decided parts are in the spec:** spec/life/birth_and_death.md (24 Oct).

# Proposal: children as a choice, counted in days (costs, care, growing up, old age, succession)

**Status:** accepted: D2-138 to D2-152 (24 Oct); care beyond survival later (OPEN L-26); the rest to explore. Design only. **Owner:** 37.2 (author: the economics of
children); life, households and the engine's life step are 37.4's ([life.md](life.md), spec/life/), so this extends their proposal
and goes to them. **Model:** [02v_children_model.py](../../review/37_growth/02v_children_model.py). **Affects:** spec/life/,
spec/institutions/membership.md, spec/world/holding.md, spec/seeding/ (the tree in days), spec/agents/work.md.

## Summary

Children come only when both partners choose it and spend work trying (D2-138). Every span of life is counted in days (D2-139).
Partnering is the two people's own choice even when their households arranged it (D2-140). Pregnancy costs the mother food, and
she cannot conceive again for a while after a birth (D2-141). Care is a choice whose consequences are to explore (D2-142).
Inheritance and the head's succession are the household's own rules, the first case of offices in institutions (D2-143). There is
no loyalty mechanic while agents have no aims; a child carries memories of its childhood (D2-144).

The model's main finding: **with childhood compressed into days, a child is nearly free.** Even with the decided costs, a child
costs about 3 food and units to become an agent and pays that back in a day or two of youth work. What limits births is the days
(pregnancy and the gap), not the cost. A region of 15 couples who try every day adds about 14 agents in a 24-day run.

## Decided (24 Oct)

| # | Rule |
|---|---|
| D2-138 | a child only by choice: both partners, at the same node on the same day, each spend work trying; never automatic |
| D2-139 | all time is counted in days: ages, life stages, lifespans, the seeded family tree; no calendar years anywhere |
| D2-140 | partnering is both people's choice; a marriage arranged between households is an agreement between their heads, which the two may still refuse |
| D2-141 | pregnancy raises the mother's food need; after a birth there is a gap before she can conceive again |
| D2-142 | caring for an infant or child is a choice, not required; its consequences are to explore (§3) |
| D2-143 | inheritance and the head's succession are the household's own rules (seeded, changeable by the household): the head names a successor, or the household decides together; the first case of offices and succession in institutions (D4-18, law.md) |
| D2-144 | no loyalty mechanic for now (no aims, D4-29); a child carries lasting memories of its childhood (who fed it, who was away, a death, a winter) |

## 1. Calendar age: what it was, and the fix (D2-139)

The world generator (cybertron2/engine/generate.py) simulates the family tree forward in years of the compressed calendar and gives
seeded people a stage by age in years (child under 12, youth under 18, adult under 60). D4-19 already counts childhood in days.
Under D2-139 the tree is dated in days and stages follow D4-19's spans: infant 1-3 days, child 3-4, youth about 10-15, adult, elder.
A generation is then some tens of days, so a seeded past of three or four generations spans a few hundred days.

## 2. What a child costs and gives (02v)

| Scenario (15 couples, 24 days) | Chance a night when trying | Births a couple | New agents in the region by the end | Cost to an agent (food and units) | Survives infancy | Pays back (days of youth work) |
|---|---|---|---|---|---|---|
| as life.md proposed (no gap, no extra food) | 0.20 | 2.0 | 21 | 1.0 | 0.96 | 0.3 |
| with D2-141 (a 4-day gap, +0.3 food a day pregnant), a child eating 0.7 and working 1 unit | 0.20 | 1.6 | 14 | 3.3 | 0.85 | 1.3 |
| the same, with an infant cared for (2 units a day) | 0.20 | 1.6 | 16 | 7.3 | 0.96 | 2.5 |
| the same, trying a third of days | 0.07 | 0.9 | 8 | 3.3 | 0.85 | 1.3 |
| the same, trying hard (3 units each, every day) | 0.39 | 1.95 | 19 | 3.3 | 0.85 | 1.3 |

Conception to agent takes about 11 days (pregnancy 5, infant 2, child 4).

**Why a child is nearly free:** real childhoods cost a household years of food before a child gives much back. Compressing those
years into days shrinks the burden, while a youth's output a day stays near an adult's. So the real trade-off (feed now, gain
later) disappears unless the costs of a day of childhood are scaled up.

**A cost dial (proposed):** set what a child costs in all, before it becomes an agent, as a world setting in days of an adult's
surplus, and derive the daily costs from it: for example, a child costing about 20 food and units in all (an infant eating a full
ration and needing a carer to thrive; a child eating a full ration and doing little). Then a child pays back over about a week of
youth work, a couple chooses whether it can afford one, and a lean winter makes the choice hard.

**Trying, with diminishing returns:** if partners may spend more than one unit each (Zach's question), the chance a night rises
0.20 (1 unit), 0.32 (2), 0.39 (3), 0.43 (4), 0.48 (6). Because pregnancy and the gap bound births, trying hard adds little over a
run (1.95 births against 1.6).

## 3. Care (D2-142: optional; consequences to explore)

What could follow from care or neglect, judged by whether it is mechanical and visible rather than a hidden trait:

| Consequence | For | Against |
|---|---|---|
| **survival** (an uncared-for infant is likelier to die, more so hungry or cold) | real, visible, already in life.md | |
| **health** (frailty, the engine's per-person hazard, set lower for a well-cared child) | real; frailty exists | slow to show |
| **what the child learns** (a child who goes with a parent to work, or is taught, starts as a youth knowing some of that work: knowledge.md's watching) | uses existing know-how; makes care an investment in skill | |
| more work units as a youth | | arbitrary; units are a body's, not an upbringing's |
| temperament | | scenario_design §3: temperament text does little; it would be a hidden trait |

**Recommendation:** survival, health and learning; not units or temperament. Its memories carry the rest (D2-144).

## 4. Old age (to explore)

The chance an elder dies within a 24-day run, by the daily risk when old age starts and how fast it rises:

| Daily risk at the start of old age | Doubling every | Newly old | 10 days into old age | 20 days in |
|---|---|---|---|---|
| 0.005 | 20 days | 17% | 23% | 31% |
| **0.01** | **20 days** | **31%** | **41%** | **53%** |
| 0.01 | 10 days | 45% | 71% | 92% |
| 0.02 | 20 days | 53% | 66% | 78% |

**Recommendation:** 0.01 a day rising to double every 20 days: about a third to a half of elders die in a run, so succession and
inheritance happen in most runs without emptying the village.

## 5. Succession (D2-143)

A household is the first institution (D4-18), and its head the first office. Its rules (inheritance: eldest, partible, household;
succession: the head names an heir, or the members decide together, or the eldest adult by default) are seeded per household and
changeable by the household by its own procedure. This is the household-sized case of the general offices and procedures in
law.md (37.3), so it should be built on them rather than as its own rule.

## Open questions

1. ~~Trying with more units~~ decided: D2-146.
2. ~~The cost dial~~ decided as a world setting to explore (D2-145): a test with the dial low (about 3) and high (about 20) in the
   same world, reading whether and when couples choose to try, how many children are born and survive, and what it does to food.
3. Care's consequences: survival, health and learning (§3)? Zach to come back to it, with passing on customs to children.
4. Old age: tuned to a chosen life expectancy under each health regime (D2-149); the numbers wait on choosing those expectancies.
5. ~~The gap and pregnancy's food~~ decided: D2-147.
6. ~~A child's menial work~~ decided: D2-148.

## History

- 24 Oct: Zach: children are a choice, not automatic; trying should take an action from each parent, perhaps more for better odds
  with diminishing returns; everything counted in days, no calendar ages; arranged marriages still need both to choose; pregnancy
  costs more food and a mother needs a gap between children; care to explore (what does neglect do?); the household decides
  inheritance and the head's successor, a basic case of institutions and offices; no goals now, so no loyalty, but memories. Decided
  D2-138 to D2-144; model 02v; this proposal.

- 24 Oct: Zach: the cost dial as something to explore, to see whether it works and how agents respond, and whether they decide to
  have children (D2-145).

- 24 Oct: Zach decided D2-146 to D2-149; old age to be tuned by life expectancy under health regimes, extendable when disease comes;
  care to come back to, possibly with passing on customs to children.

- 24 Oct: Zach decided D2-150 to D2-152 (care for survival now, health and learning later; the dial built low and high, tested in
  a world designed after; any two of opposite sex who both choose). Spec written: spec/life/birth_and_death.md.

## Sources

[life.md](life.md), [38.09](../../review/38_space_engine/09_life_design.md), [knowledge.md](knowledge.md), [law.md](law.md);
cybertron2/engine/generate.py; D4-16, D4-18 to D4-21, D4-29, D4-36.
