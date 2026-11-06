# 37.1 Demography and growth

## Goal
Populations that grow when food is plentiful, so a society of 16 at round 0 can be 40 by round 100 and its institutions must scale
with it; families that are real (households, marriage, a childhood, inheritance of place), not prompt text.

## What exists
- `cybertron/pairs.py`: two consenting parents (conceive), each paying `life.reproduction.provisions` + `fee` (5 + 1 food in
  `nature_pairs`), gestation 2 rounds, a minor for `maturity` rounds (limited actions, no conceiving, attacking, founding, proposing
  or voting), household feeding of minors from parents' food, goals drawn or inherited at maturity.
- `cybertron/life.py`: lifespans, age structures, heirs and bequests, `max_population` / `cap_mult`.
- Office succession rules (`succession.py`): designation, hereditary, election, cooptation, seniority (join order), lot.
- Observed (36c): 1-5 births per run; children cost 12 food when residents held 1-3; any two agents can conceive (no sex, no
  marriage); kinship told in prompts did not constrain who paired; seniority went by join order, not age.

## Design
1. **Cost and push.** Make children cheap relative to surplus (provisions 1-2 food per parent, a per-round upkeep while a minor drawn
   from the household instead of a lump sum), and give a reason to have them that lives in the world: a household's labour and
   land claims grow with its members (37.2), and positions and offices can pass to children. No goal text saying "have children".
2. **Caps by carrying capacity, not a headcount:** the population is limited by food (and later land), with a high safety cap for
   cost (`life.max_population`) set per batch.
3. **Households** as an engine object: members, a head, a shared store, land held by the household, inheritance within it. Children
   belong to a household by a rule (mother's, father's, or chosen at marriage).
4. **Marriage** as an act: two agents marry (consent; a law may require a ceremony, a fee, or the heads' consent), and only married
   couples conceive by default (a world may relax it). Optional sexes, or none, as a world setting.
5. **Childhood that matters:** minors take a turn every k rounds or a one-action turn, are fed by the household, and learn (a skill
   or position from a parent) before maturity. Cheap in model calls.
6. **Seniority by age** as a succession option, alongside join order.
7. **Children's goals and positions** in world terms (a household aim, an apprenticeship), drawn from the parents' and the world's.

## Spec keys (sketch)
`life.reproduction.cost {provisions, upkeep}`, `life.households: true`, `life.marriage {required, consent, ceremony_law}`,
`life.childhood {turn_every, actions, learns}`, `succession.rule: seniority` with `by: age | join`.

## Acceptance (dry runs)
- With food at 1.5x demand, a 16-agent world doubles within about 60-80 rounds and stays within the food bound.
- No births outside marriage when marriage is required; children belong to one household; a household's head passes by its rule.
- Model calls per round grow with the population at a rate the batch can afford (report calls per agent-round for minors).

## Non-goals
Genetics, disease, aging effects beyond lifespan.
