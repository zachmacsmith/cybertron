# Signs for the newer systems

**Status:** retrospective, accepted: D4-59
**Owner:** 37.4

## Summary

Every system added since the noticing rule (D4-53) now shows itself through signs, read by the same rule: what a person, a house, a
wood, a herd and a party on the road look, sound and smell like when it is pregnant, growing, building, burning, leading, arriving,
failing or thinning.

## The proposal (as built, cybertron2/engine/signs.py)

| Bundle | New signs |
|---|---|
| a person | heavy with child, her time near; a baby on her hip; leading a beast on a halter; just come in from the road (soaked, in rain or snow); an elder failing (a quarter of a lifespan into old age); chewing raw grain after a night without a fire; partners keeping close |
| a building | a frame going up (and the sound of the work); new, the daub not dry (3 days); crowded (more living there than beds); the far end cold (a hearth too small for the floor, D2-159); smoke hanging from a fire ring; a baby crying; children's voices; firewood stacked; the woodpile nearly gone, in heat (less than a cold night's) |
| a wood | fresh chips and stumps where felling was done today; a wood turned to scrub; charcoal smoke and a smoking mound where charcoal is burned (D2-156, D2-157; with the dead wood, young growth and axes signs of Package F) |
| a herd | a beast on a halter, kept close by its leader (D4-58) |
| a party on the road | an ox among them loaded with packs; one carrying a baby |

Arrivals of people and of led beasts are also events at the node (D4-53's extent: the node).

## Why

Zach (24 Oct): "Can you also do another dive into the various systems we have added, and add various appropriate potential bundles
of senses that could come up? Eg arrivals of people or herds, forest states, what else? Building? Etc?"

## Alternatives considered

Telling agents the state directly (a line in the prompt): against D4-35 (what is seen, not the state) and D4-53 (one rule).

## Open questions

- Signs for the household's inner life (quarrels, courting) wait on L-25 (beliefs and values).
- The probabilities are first guesses (calibrate).

## Affects

information/noticing.md (the extents table is unchanged; these are new rows in its bundles).

## History

- 24 Oct 2026: built at Zach's request (37.4), with D4-59.
