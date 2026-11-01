# Taking from a place is a search

**Status:** retrospective, accepted: D4-70 (2 Nov)
**Owner:** 37.4

## Summary

Taking something from a parcel one does not know holds it is a search: each unknown thing there holding the good is found with a
chance from how plain it lies and how well it is hidden (the noticing rule's own conspicuousness and hiding, the parcel's visibility,
a search's attention, one's eye). A slaughter's result says where its meat and hide went.

## The proposal

As summarised; the rule and numbers in spec information/noticing.md.

## Why

The paired Combe run (p1_combe_evening, review 38.42): Margery slaughtered a calf and then a cow, and everyone believed the meat lay on
the Common ("40 meat and 2 hide lie at the Common"); eleven takes were refused, "you know of no meat lying at the Common". **Root
cause:** the meat had gone into her hands (a slaughter's output goes to the doer's hands), the result line did not say so ("You
slaughtered a cow of the Hobb cattle (H1): 40 meat, 2 hide."), and the refusal read as if the meat were there but unknown. Zach (2 Nov):
"If they try to pick something up in a place, they must know that it is there, so if they don't then there should at least be a check
for how hidden / visible it is ... if it is just slaughtered meat they will almost certainly find it, and if it is hidden there is still
a chance they find it but they might also not if it is very well hidden."

## Alternatives considered

- **Only fix the slaughter message:** fixes this case; a thing really lying unnoticed would still be untakeable until noticed.
- **Take anything at the place, known or not:** makes hiding useless.

## Open questions

1. Whether searching a parcel should cost more than a take's unit when the thing is well hidden.

## Affects

things.py (search, search_chance), here.py, verbs.py (`_take`, slaughter's result); spec information/noticing.md.

## History

- 2 Nov 2026: built at Zach's request after the paired run's meat refusals; written down after (retrospective).

## Sources

runs/p1_combe_evening (days 30 to 35); review 38.42.
