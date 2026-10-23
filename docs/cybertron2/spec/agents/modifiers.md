# Modifiers: ways of doing an act

## Summary

A modifier changes how an act is done (where its output goes, how well something is hidden, how seed is sown) without being a new
verb. Modifiers are techniques: known, learned, taught and improved by practice like other know-how. A verb with no modifier does
what it does now. Those an agent knows are shown in its verb lines; some can be tried untaught, done worse, and trying one makes the
agent aware of it.

Written by 37.2 at Zach's request (23 Oct), from proposals/verb_modifiers.md; the area is 37.4's. It extends agents/actions.md
and the know-how of proposals/knowledge.md (D4-24).

## Decided

- D2-93: modifiers on verbs as data; nothing by default; known ones shown; learned like know-how; trying an unknown one, where the
  modifier allows it, does it worse and makes the agent aware of it.
- D2-94: `for` and the sowing method are modifiers.
- D2-112: modifiers are techniques with one more field naming the verbs they change.
- D2-125: `searching` on travel, known to all.
- D2-129: at least one person in the world knows dibbling by default; it spreads by teaching.
- D2-111: `give` takes `to: <place>`; leaving and hiding are giving to a place (world/things_in_places.md).

## Mechanics

### The record

A modifier is a technique (the same record, levels and ways of being learned as other know-how) with:

| Field | Meaning |
|---|---|
| `modifies` | the verbs it attaches to |
| `changes` | what it does: cost, conspicuousness, destination, yield, wear |
| `known by` | `all` (common knowledge) or learned (taught, apprenticed, read, watched, practised) |
| `untaught` | `tryable` (anyone could think of it: done at the lowest level, and the agent becomes aware of it) or `no` (refused with a reason; the agent becomes aware it exists) |

### The first modifiers

| Modifier | On | Changes | Known by | Untaught |
|---|---|---|---|---|
| `for: <party>` | work, gather, make, build, give, offer, accept | output into, and payment from, that party's container (D2-37) | all | |
| `hidden: under brush` / `hidden: buried` | give to a place | conspicuousness x0.2 / x0.03; 1 / 2 units of work | all | tryable (half as well hidden) |
| `method: dibble` | sow | 3x the work, 0.6x the seed (D2-54) | learned (at least one person in the world knows it, D2-129) | no |
| `on trouble`, `stop at`, `gather` | travel | the choices at departure (world/roads.md) | all | |
| `searching: <herd or person>` | travel | attention x5 for it on each stretch (D2-125) | all | |

### Showing and using

- An agent's verb lines show the modifiers it knows, with a few words each; at most 4 shown on one verb.
- Using one it does not know: if tryable, done at the lowest level and it becomes aware of it (rough knowledge); doing it again
  raises its level by practice (D2-52); if not tryable, refused ("you do not know how to dibble seed; someone could show you") and it
  becomes aware it exists.
- Two modifiers on one act are independent unless the data marks a pair that cannot combine.
- How well a modifier works rises with its level and, for hiding and spotting, the eye for the land (D2-91).

## Data

Per modifier: the fields above. Per agent: the modifiers it knows and at what level, as for other know-how.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| shown per verb | at most 4 | proposed |
| an untaught try | half as effective | proposed; calibrate |

## What agents see

In each verb line, the modifiers it knows ("give ... `hidden: under brush` to hide it"); a refusal with a reason; after a first
untaught try, the modifier in its verb line.

## Open

- `aim: burn` on attack as a modifier (with fire: OPEN L-21).
- Later modifiers: going quietly, working carefully (OPEN L-19).

## Sources

[proposals/verb_modifiers.md](../../proposals/verb_modifiers.md), [knowledge.md](../../proposals/knowledge.md).

*Current as of 24 Oct 2026: D2-93, D2-94, D2-111, D2-112, D2-125, D2-129.*
