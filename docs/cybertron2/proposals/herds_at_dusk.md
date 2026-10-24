# Herds at dusk: going home is a chance

**Status:** retrospective, accepted: D4-54 (built 24 Oct at Zach's request; written down afterwards)
**Owner:** 37.2 (livestock); 37.4 built it (herds.py)

## Summary

A herd that wandered walks home at dusk only by chance: likelier if its cows are in milk, less likely the better it is feeding where it
stands, so it often stays the night where the food is. A hungry herd stays out.

## The proposal

- Chance home at dusk = 0.8 (cows in milk) or 0.3 (others) x (1 - 0.7 x how well it feeds where it is, 0 to 1) (calibrate).
- A shut fence round home lets it back in only at its odds; a hungry herd does not go home.

## Why

- Package C first held cows in milk at home all day (c1: the Reed cattle never left the Common); fixed to "roam by day, home at dusk",
  every time. Zach: "do herds always return at dusk? I feel like they should have a chance, or be more likely to just end up in a parcel
  with food and stay there?"

## Alternatives considered

- Always home at dusk for cows in milk (as first fixed); never for others (as built).

## Open questions

- The numbers (37.2).

## Affects

spec/economy/livestock.md "Wandering on the node" (37.2's: "Cows in milk drift home at dusk" to read as a chance); herds.py `home_at_dusk`.

## History

- 24 Oct: asked by Zach after Package C's runs; built that day; written down here afterwards: retrospective, accepted D4-54.

## Sources

Conversation, 24 Oct; review 38.25.
