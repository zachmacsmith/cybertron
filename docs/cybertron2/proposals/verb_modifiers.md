# Proposal: modifiers on verbs (ways of doing an act that people know or learn)

**Status:** discussion (23 Oct). Design only. **Owner:** 37.2 (author); verbs and knowledge are 37.4's (verbs.md, knowledge.md,
D4-24), so this goes to them. **Affects:** spec/agents/actions.md; verbs.md; knowledge.md; information/prompts.md; things in
places (hiding), road_encounters.md (searching), attacks_and_walls.md (burning), farming (sowing methods).

## Summary

Zach (23 Oct): rather than a `hide` verb, hiding could be an optional extra input on `leave`, nothing by default, that people have
to know; verbs could carry **modifiers** that change how the act is done, learned like other know-how. The engine already has
several of these without calling them that: `for` on work (D2-37), `aim: burn` on an attack (D2-51), broadcast or dibble on sowing
(D2-54), travelling with the aim of searching (road_encounters.md). This proposal makes them one thing.

## The proposal

### 1. What a modifier is

A **modifier** is data: a name, the verbs it attaches to, what it changes, and who knows it.

| Modifier | On | Changes | Known by |
|---|---|---|---|
| `for: <party>` | work, give, offer, accept | where output goes, whose store pays (D2-37) | all |
| `hidden: under brush` | leave | conspicuousness lower; 1 unit of work | all |
| `hidden: buried` | leave | conspicuousness much lower; 2 units; slower to take back | all |
| `searching: <herd or person>` | travel | the odds of finding them (road_encounters.md) | all |
| `method: dibble` | sow | 3x the work, 0.6x the seed (D2-54) | taught |
| `aim: burn` | attack | sets fire (D2-51) | all who carry fire |
| `quietly` (later) | travel, take, leave | seen less by others; slower | learned |
| `carefully` (later) | gather, make | less wear, less waste, slower | learned |

### 2. The rule for a modifier against a new verb

- **A modifier is the same act done another way:** the same object and result, changed in cost, visibility, destination, yield
  or wear. Hiding is leaving, done so as not to be seen.
- **A new verb is a different act:** a different object or result (bury a body is `work` on remains, not `leave`).

### 3. Knowing and showing

- Default nothing: a verb without a modifier does what it does now.
- Each modifier is **common knowledge** (in every prompt's verb line, as now for `for`) or **know-how** (taught, apprenticed,
  read, practised: knowledge.md), shown only in the verb lines of those who know it, so the prompt grows only with what the
  agent knows.
- Using one you do not know is refused with a reason ("you do not know how to hide it well").
- How well a modifier works can rise with the eye for the land or skill by practice (D2-52, D2-91): a keen eye hides better.

## Why

- It keeps the verb list short (D4-24: the world grows by data on a few verbs) while letting skill and knowledge change what
  people can do.
- It turns several one-off arguments already in the engine into one data-driven mechanism, which 37.4 can test once.

## Risks

- **Unused options:** agents rarely use what they are not shown. Every known modifier must be in the verb's line, with a few words
  of what it does.
- **Growth:** modifiers must stay few per verb (proposed at most 4 shown at once), or the verb line becomes the verb list again.
- **Combinations:** two modifiers on one act (hidden and for) need a rule; proposed, each is independent, and data marks any pair
  that cannot combine.

## Alternatives considered

- **A verb per way** (`hide`, `bury`, `search`, `sow_dibble`): clear but the verb list grows with every skill.
- **Free text read by a model** ("I hide it under the roots"): flexible, but the engine cannot check it and agents would invent
  effects.

## Open questions (for Zach, and 37.4)

1. Modifiers as data on verbs, nothing by default, some common and some learned?
2. Hiding as `leave` with `hidden: under brush | buried`, known to all, better with the eye for the land?
3. Fold the existing ones (`for`, `aim: burn`, the sowing method, searching) into this?

## History

- 23 Oct: Zach: should hiding be an optional extra input on `leave` that people have to know, nothing by default, so they can
  learn things, with modifiers on verbs that change their behaviour rather than different verbs? Written, with 37.2's view (yes,
  with the rule in §2 and the risks).

## Sources

[verbs.md](verbs.md), [knowledge.md](knowledge.md), [things_in_places.md](things_in_places.md),
[road_encounters.md](road_encounters.md), [attacks_and_walls.md](attacks_and_walls.md), [farming.md](farming.md); D2-37,
D2-51, D2-52, D2-54, D2-91, D4-24.
