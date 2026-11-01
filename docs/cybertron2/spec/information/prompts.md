# Prompts

## Summary

An agent's prompt says what it can see and do in world terms: life stages, never ages; the techniques it knows of, never a full
manual; what it carries against what it can carry. It carries no aims for now. The agent thinks before answering, and its calls over
a stretch of days are one conversation (memory.md).

## Decided

- D4-19: prompts name life stages, never ages in years.
- D4-24: agents are shown the actions they know of; the rest they come to know in the world.
- D4-29: no aims in any prompt (agents/aims.md).
- D4-32: the prompt states each good's weight and what the agent carries against what it can carry.
- D4-26, D4-27: native thinking on every call; one conversation per stretch of days (memory.md).
- D2-4, D2-29: no computed absence, no computed price (perception.md).
- D2-84: an urgent call in the night is appended to the agent's own conversation: what it senses, what it carries, who is in the
  house with it, how many things there is time for, and the choices (conflict/fuse_events.md).
- D2-97: on arrival, "On the way: ..." (what the traveller noticed and what trouble cost) opens its turn. World/roads.md: the
  roads line names the landmarks one knows on each road and what a night or a day of waiting on it costs; `travel` takes its
  choices for trouble (`on trouble`, `days`, `stop at`, `gather`).
- D2-99: the day's weather is part of "Now"; what one knows lies about a place (world/things_in_places.md) is part of "Here".

## Mechanics

- **System prompt:** the world's rules in words, the verbs and how to reply.
- **Turn prompt:** what the agent remembers, the day, where it is and who is there, itself (fed, carrying, its house), what it can
  do today (by the techniques it knows of and the sites and tools at hand), its agreements, and what it was told.
- Everything is in world terms; engine numbers appear only where a person would count (goods, days, units of work).

### Tags, names and ages

- D4-68 (`tags: true`): groups of beasts carry a tag H1, H2, ... and things lying at a spot T1, T2, ..., given when they come to
  be and shown in brackets after their name or description, the same for everyone. The verbs take a tag wherever they take a name;
  a herd's name picks the group of that name that has beasts in it. `name {"thing": tag, "as": name}` gives a tagged thing a name,
  known to the namer, everyone at the place and the namer's household; for them every "(H4)" in what they are shown reads
  "(H4: name)", and the verbs take the name. With tags on, the reply schema leaves `thing`, `from` and `attend` free text.
- D4-69 (`ages: true`): under "You", one's age in days and what lies ahead: when a youth comes of age; when an adult turns elder
  and can have no more children; one's partner's age and when they turn elder.
- With an evening (D4-65 to D4-67), the system text says how the day goes, and `travel` shows `"when": morning | nightfall`.


## Parameters

| Parameter | Value | Status |
|---|---|---|
| prompt budgets by section | the engine's (38.17) | calibrate |

## Open

- Section budgets and order: 38.02, 38.17.

## Sources

38.02; cybertron2/engine/prompt.py; 38.17.

*Current as of 2 Nov 2026: D2-4, D2-29, D2-84, D2-97, D2-99, D4-19, D4-24, D4-26, D4-27, D4-29, D4-32, D4-68, D4-69.*
