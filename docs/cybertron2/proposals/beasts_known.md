# Knowing one's beasts: memory and noticing, not a list

**Status:** retrospective, accepted: D4-56 (built 24 Oct at Zach's request; written down afterwards)
**Owner:** 37.4 (perception, prompts); 37.2 owns livestock

## Summary

One knows one's household's beasts as one knows anything (D4-35): from what one last saw of them (how many, where, when), kept in
one's memory and shown as such; it is updated when one notices them (by the noticing rule) or works with them, and their home
pasture seen empty marks them missing. What a household's living depends on is seeded as its experience: the merchants know what
their ox is for.

## Why

- The region run's merchant never used his pack ox: the prompt never mentioned it (livestock.md's "What agents see: their animals"
  was never built). 37.4 first added a live list of one's beasts with a hint to lead the ox. Zach: "This seems like a thing he should
  naturally have rather than a quick fix. Everyone shouldn't have their animals listed all the time, but they should almost always see
  things about them, and the merchants should start maybe with some knowledge of them ... this way feels potentially like a quick fix
  forcing it?"

## The proposal (as built)

- Mind store `beasts`: seeded at the start for each household's herds ("as you have long known"); updated on noticing a sign about
  the herd, on working its parcel (herding, milking, driving), and to "not on <home>; where they are you do not know" when the home
  pasture is seen empty (signs.py EMPTY).
- The prompt shows "Your household's beasts, as you last knew of them: ..." from that memory, which can be stale.
- The region world seeds the Merchant household's memory of what the ox does (60 on any road, led, grazing or eating hay); no hint in
  the prompt tells anyone what to do.

## Alternatives considered

- A live list of one's beasts and what they could do (built and withdrawn: omniscient and leading).
- Nothing (as before): the merchant cannot know he has an ox.

## Open questions

- Beasts of others one knows (a neighbour's bull): only by noticing, as now.

## Affects

perceive.remember_beasts, prompt._beast_lines, signs EMPTY; region_c1.yaml; livestock.md "What agents see" (37.2's).

## History

- 24 Oct: the merchant's unused ox found; a list added; Zach's objection; replaced the same day by memory and seeded experience:
  retrospective, accepted D4-56.

## Sources

Conversation, 24 Oct; runs/r1_region_dependent_noox.
