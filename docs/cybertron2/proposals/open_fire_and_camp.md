# An open fire and a camp: what fire away from a house costs

**Status:** retrospective, accepted: D4-49 (built 23 Oct at Zach's request; written down afterwards, 24 Oct)
**Owner:** 37.4 (the night, shelter in the engine); 37.2 owns shelter and fuel numbers

## Summary

A fire in the open for one night takes about 2 timber; a camp takes 3 timber to build and 1 timber a night to keep lit.

## The proposal

- `fire` (a verb): an open fire for the night where one is, 2 timber; it cooks grain and warms as a hearth does for that night.
- A camp (D2-68's portable shelter): 3 timber to build; its fire burns 1 timber a night (PHYSICS fuel: open 2.0, camp 1.0, a house's
  hearth 0.5, 2.0 on a cold night).

## Why

- In the region run, people starved with grain in hand and no lit hearth; Zach asked whether there was no portable fire if one carries
  or finds timber. There was none, and a camp's fire burned at a house's rate (0.5 timber), cheaper than a house, which Zach called
  weird: "Surely it should need at least like 2 timber as a temporary? Then they can build a camp with 3, and keep it lit with 1
  timber each round."
- An open fire makes carried grain and found timber useful away from home, at a cost that keeps a house worth having.

## Alternatives considered

- No fire away from a house (as built before): travellers with grain starve.
- A camp fire at a house's rate: cheaper than a house.

## Open questions

- Wet timber as fuel (OPEN L-21 and Package B's list): not built.

## Affects

core/round.md, agents/actions.md (the `fire` verb), economy shelter (37.2).

## History

- 23 Oct: asked by Zach after the region run ("is there not a way portable fire if they bring or find timber?"), with the numbers; built
  that day (verbs.py `fire`, night.py fuel and camps); D4-49.
- 24 Oct: written down here afterwards as a retrospective proposal.

## Sources

Conversation, 23 Oct; review 38.23.
