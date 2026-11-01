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

## With an evening (`evening: true`)

- D4-65: the day has an evening at the hearth, after work and before the day's settling and the night. Everyone at a place who is
  not setting off tonight is asked once, together, where they will sleep: the building they mean to sleep in, else their house
  here with beds, else the open. Shown: where they are and who is with them, how their day went (its acts and results), and what
  waits on their answer.
- What is said there (`say`) is heard by everyone at that hearth and costs nothing; a private word (`tell`) goes to anyone at the
  place, from the day's ration.
- Then one wave: only those asked something directly are asked again (told something; named in what was said at their hearth;
  someone trying for a child with them, asking to be partners, asking to join their household, or making them an offer). What
  they say is heard, and answered the next day.
- The morning keeps one wave of answers to private words (two without an evening). Speech to everyone at the place, or in a
  building, in the morning costs a unit as before (D4-31).
- Who hears is fixed by where one is when speaking, never where one will be.
- D4-66: the evening's acts are those that take no work and answer the day's requests or take effect tonight (core/round.md).


### Meetings, and the memory at the evening (D4-77)

- `meet {"at": a building or a place here, "about"?}` (free; in the evening or the day's plan) calls a meeting for the next
  morning. Everyone at the place is shown it in their morning message. Those whose plan holds `come` (a unit) meet after the talk
  step and before work: up to three rounds, each asking all present at once with what was said before; it ends early when a round
  says and offers nothing. Speech there is heard by all present and costs nothing; an offer made there is written into each one's
  lasting memories as witnessed; each may give their whole plan again.
- The memory request (information/memory.md) is asked in its own call after the night (D4-80); a world may ask it at the evening call
  instead (`memory_at_evening: true`).
- `evening: plan`: the evening reply's acts beyond the night's are tomorrow's plan (with its fallback); at dawn one is asked again
  only if a sign at dawn or something concerning one came, one's household had a birth, a death or a missed meal in the night, or a
  meeting is called; otherwise the plan is done as made, and what the morning would have shown is put at the head of that evening's
  message.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| waves of answers in one talk step | 2 | calibrate |
| messages an agent may send in one step | 3 of each kind | calibrate |
| private messages a day | 3 plus a jitter drawn once per person (weights 37, 37, 18, 8 for +0 to +3), at most 10 | decided (D4-31: cybertron 1's) |
| work for speaking aloud | 1 unit a say | decided (D4-31) |

*Current as of 2 Nov 2026: D2-7, D4-15, D4-25, D4-30, D4-31, D4-65, D4-66, D4-77, D4-80.*
