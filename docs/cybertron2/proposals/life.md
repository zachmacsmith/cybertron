# Proposal: life (partners, children, growing up, death, inheritance)

**Status:** discussion (23 Oct). **Owner:** 37.4 (until 37.1 joins). **Affects:** spec/life/ (life_stages.md, and households.md,
kinship.md, birth_and_death.md to write), spec/institutions/membership.md, spec/world/holding.md (inheritance), spec/agents/models.md,
cybertron2/engine (a life step at night; verbs).

## Summary

Decided so far: short childhoods counted in rounds and agents from youth (D4-19), one model for life (D4-20), a seeded society with a
full family tree (D4-21), households as the first institution (D4-18). Not decided: how partners form, how children are conceived
and born, what a baby costs, when the old die, and who inherits. This proposal turns 38.09 (designed with Zach, 22 Oct) into rules
for those, so births, comings of age and successions happen inside a run.

## The proposal

### 1. Partners
- A partnership is a record between two people (seeded from the tree, D4-21). A new one is made when both choose it on the same day at
  the same node (`partner {person}`, both ways), and ends by death or by either leaving (`part`).
- Partners live in one household: one joins the other's (D4-36's `join` and `admit`), or they found one.

### 2. Children: a choice of two (38.09 §1, from 37.1: "fertility is a choice: two consenting parents; no automatic births")
- **Conceiving:** both partners choose `try for a child` on the same day at the same node, and both are fed; then a chance a night
  (proposed 0.3) that the mother conceives.
- **Pregnancy:** a few rounds (proposed 5); in its last two the mother has 1 unit fewer a day; travelling then is a risk (a fall).
- **Birth:** where the mother is, at night, with a small risk to mother and child, higher out of shelter or hungry; the household and
  everyone at the node see it (signs, D4-48).
- **Infant** (1-3 rounds, D4-19): a member of the household; eats half a ration from the household's stores; needs a bed's shelter;
  carried if the mother travels. Neglect (unfed two nights) can kill it.
- **Child** (3-4 rounds, D4-19): no model call; does menial work by the household's standing order (fetch water, mind the fire,
  gather wild food: about 1-2 units a day at a low skill), eats a ration.
- **Youth:** becomes an agent (D4-19) with its model chosen then (D4-20: the heir to a pole seat takes the seat's model; others keep
  the cast balanced). It starts with childhood memories of what it saw (who fed it, who was away, a death, a winter: 38.09 §2c).

### 3. Growing old and dying
- Each round an elder carries a small chance of dying in the night, rising with age and with hunger, cold and wounds (proposed
  from 0.01 a round, doubling every few rounds of old age). Adults pass to elder after a set number of rounds.
- A death is seen by those present and travels as news (D2-4: never announced).

### 4. Inheritance and succession
- A household has an inheritance rule (`eldest`, `partible`, `household`; 38.09 §1), seeded per line.
- On a death: the dead's own claims pass by the rule (`transfer_claim`, holding.md: whole plots, eldest first, the rest held jointly);
  goods stay where they are (an heir far away must come for them); the household's head passes to the eldest adult member, or as
  its rule says.

### 5. What agents see
Partners and children in their kin lines; a pregnancy as signs ("Maud moves slowly now, near her time"); a birth, a child's first
work, a coming of age; an old person failing; a death and the inheritance as each saw or was told it.

## Why
- Children are worth having only if they cost something and give something: food and care while small, work and loyalty after
  (38.09 §1, 37.1's findings).
- Rounds-long childhoods (D4-19) let a run of 20-40 days see births, comings of age and successions.

## Alternatives considered
1. Automatic births at a rate: rejected in 37.1 (Zach: a choice of two).
2. Time skips: rejected (Zach, 38.09 §4).

## Open questions (for Zach)
1. Partnering: a mutual act, or also a household head's arrangement (a marriage between households)?
2. Conception: the chance a night, and whether it should need a house or a bed.
3. Pregnancy and birth: length in rounds, units lost, risk to mother and child.
4. What an infant and a child cost and give (food, care, work).
5. Old age: when adults become elders in a run, and how fast the risk of death rises.
6. Inheritance: which rule each seeded line has, and whether the head's office passes with the house.
7. Raising: does a child's loyalty at coming of age follow how it was fed (37.1), or only its memories?

## Affects
spec/life/; spec/institutions/membership.md; spec/world/holding.md; spec/agents/models.md; cybertron2/engine.

## History
- 23 Oct: written from 38.09 (22 Oct, with Zach) after Zach asked whether having children is built (it is not).

## Sources
[38.09](../../review/38_space_engine/09_life_design.md); D4-18 to D4-21; 37.1's `docs/review/37_growth/devlog_37.1.md`.
