# Proposal: modifiers on verbs (ways of doing an act that people know or learn)

**Status:** accepted: D2-93, D2-94, D2-111, D2-112 (23 Oct); `searching` and `aim: burn` as modifiers still open. Spec written:
spec/agents/modifiers.md. Design only. **Owner:** 37.2 (author); verbs and knowledge are 37.4's (verbs.md, knowledge.md,
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

### 3. Knowing, showing and trying (D2-93)

- Default nothing: a verb without a modifier does what it does now.
- Those an agent knows are **shown in its verb lines**; they are learned, explained and taught like other know-how (knowledge.md),
  so the prompt grows only with what the agent knows.
- **Trying one you do not know** depends on the modifier, as data (`untaught`):
  - **tryable** (hiding, going quietly, searching): anyone could think of it, so it is done at the lowest level (a pack hidden
    untaught is half as well hidden as by someone who knows how) and the agent becomes **aware** of it, with rough knowledge; doing
    it again raises the level by practice (D2-52);
  - **not tryable** (dibbling, which takes being shown): refused with a reason, and the agent becomes aware it exists.
- How well a modifier works rises with skill by practice and, for hiding and spotting, the eye for the land (D2-91).

### 4. Are modifiers techniques? (37.2's view)

Yes: **a modifier is a technique that changes another act** rather than making something of its own. A technique (knowledge.md)
is know-how with levels, learned by teaching, watching, reading or practice; most are a recipe (make bread), a blueprint (build a
mill) or a site (work a seam). A modifier technique has the same record, the same levels and the same ways of being learned, plus
the verbs it attaches to and what it changes. So nothing new is needed in knowledge: one more field on a technique (`modifies:
leave`). The difference that matters is only in the prompt: a recipe shows as something one can make, a modifier as an option on
a verb one already has.

### 5. One verb for putting things somewhere: `give` (Zach's question)

Today the engine has `give` (to a person or a household's store) and `leave` (at a building, found by its household in the
morning). Proposed: one verb, **`give {item, qty, to}`**, where `to` is a person, a household, a building, or **a place** (a
parcel, a spot on the road); leaving is giving to a place, and hiding is giving to a place with `hidden` (aliases `leave`, `put`,
`drop`, `hide` read as `give`, so agents can write what comes naturally).

| Giving to | What happens |
|---|---|
| a person here | into their hands |
| a household, or a building one may use | into its store, as now |
| a building one may not use, or someone not here | **left at its door, in the open** (held by nobody, D2-87; noticed by D2-85; spoils as in the open) |
| a place | left there, in the open; with `hidden`, hidden |

This covers the departure prompt (the "too heavy to set off" call, D4-32, which is appended to the agent's cached conversation of
that day like every other call): a give there to someone not at home, or to a house one has no access to, leaves the goods outside
that house. One consequence to accept: a gift left at the door of someone else's house is no longer safe until morning; someone
passing can take it.

### 6. Searching

`travel {to, searching: <herd or person>}`: someone travels along an edge looking for a lost herd (livestock.md, once herds wander
onto edges) or a missing person, which raises the daily chance of finding them from about 0.15 to about 0.5 and lets them turn back
on the way (road_encounters.md §3). It is a modifier on `travel`, known to all.

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

1. ~~Modifiers as data~~ decided: D2-93.
2. ~~One verb `give`~~ decided: D2-111.
3. ~~`for`, the sowing method~~ decided: D2-94. `searching` on travel (§6) and `aim: burn` on attack: modifiers too?
4. ~~Modifiers as techniques~~ decided: D2-112.

## History

- 23 Oct: Zach: should hiding be an optional extra input on `leave` that people have to know, nothing by default, so they can
  learn things, with modifiers on verbs that change their behaviour rather than different verbs? Written, with 37.2's view (yes,
  with the rule in §2 and the risks).

- 23 Oct: Zach decided D2-93 (trying an unknown modifier does it worse and makes one aware, by modifier; known ones shown; learned
  and explained like techniques) and D2-94 (`for`, sowing method). Asked whether modifiers differ from techniques (§4: 37.2's view,
  no), whether `leave` can fold into `give` with leave and hide as variants and a give in the departure prompt left outside the
  house (§5), and what searching meant (§6).

- 23 Oct: Zach decided D2-111 (`leave` folds into `give`) and D2-112 (modifiers are techniques). Spec written.

## Sources

[verbs.md](verbs.md), [knowledge.md](knowledge.md), [things_in_places.md](things_in_places.md),
[road_encounters.md](road_encounters.md), [attacks_and_walls.md](attacks_and_walls.md), [farming.md](farming.md); D2-37,
D2-51, D2-52, D2-54, D2-91, D4-24.
