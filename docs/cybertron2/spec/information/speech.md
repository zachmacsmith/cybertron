# Speech at a node

## Summary

People speak to one person, in a building, or to the whole town. Only speech to one person calls them away from their day: they
hear it before work and may answer or change their plans. Speech in a building or to the town is heard by everyone it reaches,
without interrupting them.

## Decided

- D2-7: the square is everyone at the node; private messages to anyone at the node; everyone hears what is said in the buildings
  they have access to at their node, and may speak in several in one day.
- D4-15: speech is not a round late: a talk step among the people at the node, before work.
- D4-25: who hears and who is woken (below).
- D4-30: speaking in a building is one action for any building one has access to; access is data on each building.
- D4-31: private messages rationed a day (cybertron 1's limit); speaking aloud takes one unit of work.

## Mechanics

| Speech | Reaches | Wakes |
|---|---|---|
| to one person | that person, at the node | yes: asked again before work; may answer or change plans |
| in a building (any one the speaker has access to) | everyone with access to it who is at the node that day, wherever they are | no |
| to the town | everyone at the node | no |

| Speech | Costs |
|---|---|
| to one person | one of the day's private messages (answers count too); none left: refused |
| in a building, or to the town | one unit of the day's work |

- Answers to a message go back the same way and wake their recipient, for a few waves (cybertron 1's DM step).
- An offer made to one person wakes them, as a message does.
- Speech that does not wake is taken in at the hearer's next decision.
- **Access** is recorded on each building: a house gives it to its household and to anyone listed as let in; a public building
  (a hall) to everyone at the node.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| waves of answers in one talk step | 2 | calibrate |
| messages an agent may send in one step | 3 of each kind | calibrate |
| private messages a day | 3 plus a jitter drawn once per person (weights 37, 37, 18, 8 for +0 to +3), at most 10 | decided (D4-31: cybertron 1's) |
| work for speaking aloud | 1 unit a say | decided (D4-31) |

*Current as of 23 Oct 2026: D2-7, D4-15, D4-25, D4-30, D4-31.*
