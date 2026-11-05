# Proposal: life (partners, children, growing up, death, inheritance)

**Status:** accepted, through children.md and fertility.md: D2-138 to D2-153 and D2-162, then D4-86 to D4-88 and D4-97 (beds,
where a baby sleeps, the partner line, a baby's shelter); built (life.py; spec/life/birth_and_death.md). Still open: which
inheritance rule each seeded line has; the birth, infant and old-age numbers to calibrate. **Owner:** 37.4 (until 37.1 joins). **Affects:** spec/life/ (life_stages.md, and households.md,
kinship.md, birth_and_death.md to write), spec/institutions/membership.md, spec/world/holding.md (inheritance), spec/agents/models.md,
cybertron2/engine (a life step at night; verbs).

## Summary

Decided so far: short childhoods counted in rounds and agents from youth (D4-19), one model for life (D4-20), a seeded society with a
full family tree (D4-21), households as the first institution (D4-18). Not decided: how partners form, how children are conceived
and born, what a baby costs, when the old die, and who inherits. This proposal turns 38.09 (designed with Zach, 22 Oct) into rules
for those, so births, comings of age and successions happen inside a run. [built: life.py, D2-138 to D2-153, D2-162 (Package D)]

## The proposal

### 1. Partners
- A partnership is a record between two people (seeded from the tree, D4-21). A new one is made when both choose it on the same day at
  the same node (`partner {person}`, both ways), and ends by death or by either leaving (`part`).
- Partners live in one household: one joins the other's (D4-36's `join` and `admit`), or they found one. [built: verbs.py `partner`,
  `part`, D2-140: both choose; partners may live in one household or apart (spec/life/birth_and_death.md)]

### 2. Children: a choice of two (38.09 §1, from 37.1: "fertility is a choice: two consenting parents; no automatic births")
- **Conceiving:** both partners choose `try for a child` on the same day at the same node, and both are fed; then a chance a night
  (proposed 0.3) that the mother conceives. [built: life.py, D2-138, D2-146, D2-152, D2-162: any two of opposite sex, partners or
  not, each spending units; 0.8 x (1 - e^(-0.5 x units)) if both sleep in one place and neither went hungry]
- **Pregnancy:** a few rounds (proposed 5); in its last two the mother has 1 unit fewer a day; travelling then is a risk (a fall). [built: life.py, D2-141,
  D2-147, D2-162: 2 days, 0.3 food a day more; the last day's lost unit and 0.05 risk on the road built as proposed, to confirm
  (fertility.md Q5)]
- **Birth:** where the mother is, at night, with a small risk to mother and child, higher out of shelter or hungry; the household and
  everyone at the node see it (signs, D4-48). [built: life.py, signs.py, D4-59, D4-97 (a birth in a camp between housed and out);
  the risks proposed, to calibrate]
- **Infant** (1-3 rounds, D4-19): a member of the household; eats half a ration from the household's stores; needs a bed's shelter;
  carried if the mother travels. Neglect (unfed two nights) can kill it. [built: life.py, D2-142, D2-145, D4-86, D4-87, D4-97: no
  bed of its own, it sleeps where its mother sleeps, its night risk by shelter (house 1, camp 1.5, out 2); neglect is a daily death
  chance (0.02 cared for, 0.08 not, doubled when hungry or cold), not two nights unfed]
- **Child** (3-4 rounds, D4-19): no model call; does menial work by the household's standing order (fetch water, mind the fire,
  gather wild food: about 1-2 units a day at a low skill), eats a ration. [built: life.py, D2-145, D2-148, D2-151: the cost dial,
  low (1 unit of work, 0.7 food) and high (0.5 unit, 1.0 food, minding)]
- **Youth:** becomes an agent (D4-19) with its model chosen then (D4-20: the heir to a pole seat takes the seat's model; others keep
  the cast balanced). It starts with childhood memories of what it saw (who fed it, who was away, a death, a winter: 38.09 §2c).

### 3. Growing old and dying
- Each round an elder carries a small chance of dying in the night, rising with age and with hunger, cold and wounds (proposed
  from 0.01 a round, doubling every few rounds of old age). Adults pass to elder after a set number of rounds. [built: life.py,
  D2-149, D2-153: elder at the lifespan (32 days by default); 0.01 a night doubling every 20 days, proposed, to calibrate]
- A death is seen by those present and travels as news (D2-4: never announced).

### 4. Inheritance and succession
- A household has an inheritance rule (`eldest`, `partible`, `household`; 38.09 §1), seeded per line.
- On a death: the dead's own claims pass by the rule (`transfer_claim`, holding.md: whole plots, eldest first, the rest held jointly);
  goods stay where they are (an heir far away must come for them); the household's head passes to the eldest adult member, or as
  its rule says. [built: life.py `on_death`, verbs.py `name`, D2-143, D2-163, D4-95: the named heir, else a head named by the
  members within 2 days, else the eldest adult; claims by the rule, land in whole plots]

### 5. What agents see
Partners and children in their kin lines; a pregnancy as signs ("Maud moves slowly now, near her time"); a birth, a child's first
work, a coming of age; an old person failing; a death and the inheritance as each saw or was told it. [built: signs.py, D4-59,
D4-88 (a partner's death not shown till it is known)]

## Why
- Children are worth having only if they cost something and give something: food and care while small, work and loyalty after
  (38.09 §1, 37.1's findings).
- Rounds-long childhoods (D4-19) let a run of 20-40 days see births, comings of age and successions.

## Alternatives considered
1. Automatic births at a rate: rejected in 37.1 (Zach: a choice of two).
2. Time skips: rejected (Zach, 38.09 §4).

## Open questions (for Zach)
1. Partnering: a mutual act, or also a household head's arrangement (a marriage between households)? [decided: D2-140 (both
   choose; an arranged marriage is an agreement between heads, which the two may refuse)]
2. Conception: the chance a night, and whether it should need a house or a bed. [built: life.py, D2-146, D2-162 (0.8 x (1 -
   e^(-0.5 x units))); no house or bed, only both sleeping in one place]
3. Pregnancy and birth: length in rounds, units lost, risk to mother and child. [built: life.py, D2-141, D2-147, D2-162, D4-97;
   the risks and the last day's unit proposed, to calibrate]
4. What an infant and a child cost and give (food, care, work). [built: life.py, D2-145, D2-148, D2-151 (the cost dial); runs at
   both settings still to do (fertility.md §5)]
5. Old age: when adults become elders in a run, and how fast the risk of death rises. [built: life.py, D2-149, D2-153; the hazard's
   numbers proposed; disease later (OPEN L-9)]
6. Inheritance: which rule each seeded line has, and whether the head's office passes with the house. [still open (5 Nov): the
   rules are D2-143 and built (life.py, default `household`), but no world or the generator sets a line's rule (checked
   cybertron2/specs/, generate.py); the head passes by the household's succession rule, and a house stays the household's]
7. Raising: does a child's loyalty at coming of age follow how it was fed (37.1), or only its memories? [decided: D2-144 (no
   loyalty mechanic; memories of childhood), with D4-64 (lines passed on with care)]

## Affects
spec/life/; spec/institutions/membership.md; spec/world/holding.md; spec/agents/models.md; cybertron2/engine.

## History
- 23 Oct: written from 38.09 (22 Oct, with Zach) after Zach asked whether having children is built (it is not).
- 5 Nov: swept (37.4): decided through children.md and fertility.md (D2-138 to D2-153, D2-162) and since (D4-86 to D4-88, D4-97),
  and built in life.py. Still open: the inheritance rule of each seeded line; birth, infant and old-age numbers to calibrate.

## Sources
[38.09](../../review/38_space_engine/09_life_design.md); D4-18 to D4-21; 37.1's `docs/review/37_growth/devlog_37.1.md`.
