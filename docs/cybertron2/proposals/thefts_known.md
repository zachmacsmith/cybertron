# Who knows of a theft

**Status:** retrospective, accepted: D4-81 (2 Nov)
**Owner:** 37.4

## Summary

A theft names the thief only to those who saw it. The house's people find a loss by the store's signs and its count, not by being
told; who did it travels by speech.

## The proposal

As summarised; the rule in spec information/perception.md.

## Why

Zach (2 Nov): "Are you told about thefts directly? How would they know?" They were: settle.py made the theft event concern the
witnesses and everyone of the house, and a line about one's own house is read in full, so the owners learned the thief's name while
away at work if anyone else had seen; with no witness, they got a certain "some grain is missing from the store". Neither is how one
would know. The store's own signs (D4-74) and its count when at home already carry the loss.

## Alternatives considered

- **Owners told of a loss, not the thief:** still a line nobody sensed.

## Open questions

1. Whether a household notices a small loss from a large store at all (the count shows it; a sign may not).

## Affects

settle.py (settle_thefts), perceive.py (concerned lines); spec information/perception.md.

## History

- 2 Nov 2026: built at Zach's question; written down after (retrospective).

## Sources

cybertron2/engine/settle.py; D4-74, D4-75.
