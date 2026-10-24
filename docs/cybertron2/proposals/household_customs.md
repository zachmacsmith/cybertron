# Customs held by households

**Status:** retrospective, accepted: D4-57
**Owner:** 37.4

## Summary

A world file may give a custom to named households: their members, and those born into them, hold it as part of what they
remember; others at the same place do not. So one house can live by exploring, another by growing its family, another by improving
its land.

## The proposal (as built)

- A custom in a world file is `{text, nodes?, households?}`. With `households`, only those whose household or birth household is
  named hold it (perceive.seed_knowledge); without, everyone at the named nodes, as before.
- Someone who married in keeps the way of the house they were born in as well as the one they live in.
- First used in cybertron2/specs/hollins2.yaml: the Thornes ("land well kept is the only wealth that lasts"), the Webbs ("a house is
  as strong as its children"), the Hunts ("the wood beyond the wood is where a family's future lies").

## Why

Zach (24 Oct): "design a similar run to this one to test how it goes, with a few households, and one having custom to explroe and
expand out, and another to have all the children expansion etc. like you showed before, and one to just improve and build out the
farms"; and before it, "seed the village with a custom for expanding their family and reach". In Hollins 1 nobody tried for a child
in 22 days and the aims gave no reason to; customs held by a whole village could not give different houses different ways.

## Alternatives considered

- Each person's aim (the `aim` field): per person, so a household's way would have to be written into every member's aim, and
  aims are generated for roles (head, youth, elder).
- Seeded memories per person (as Wilmot's): works, but is written by hand for each person and is not the household's.
- The full design, customs and values held by people and passed on (OPEN L-25): later; this is its smallest case.

## Open questions

- Whether a household's custom passes to children born in the run (now: a newborn knows no customs; at coming of age it gets
  its household's crafts as awareness, not its customs). Belongs with L-25.
- Whether a household can change or drop its custom.

## Affects

information/memory.md (what is seeded); world files.

## History

- 24 Oct 2026: built at Zach's request for Hollins 2 (37.4), with D4-57.
- 24 Oct 2026: written into spec/seeding/populations.md (it had been left out). For the Wide Country, Zach: "Some of the new goals
  should be more explicit about having many children as a goal". The Cotter and Fenwick customs now say it plainly ("the Cotter way
  is to have as many as you can: take partners young, try for a child every day you can"). The generator also takes a line's own
  `aim` for its adults and youths, but under D4-29 no aim reaches a prompt, so that is data only; the customs are what the agents
  read.

## Sources

The conversation of 24 Oct; proposals/beliefs_and_values.md (L-25).
