# Proposal: buildings people make their own (descriptions and lines written on them)

**Status:** decided in part (3 Nov): every building carries a description and lines its people write, anyone can read them, and
others can change or deface them (D2-169); each line costs its own engraving (D2-170); extravagance comes in tiers (D2-171).
Built with the building package (3 Nov; review 02zh §10, 38.45): the verbs, lengths and places, the costs, fading on wattle, the
monument and the tiers, all at the numbers below (data.py LINES, MONUMENTS, TIERS; calibrate). Not yet seen in a run (38.49: no
lines written). Still open: 1 question (4, whether a tier gives more than notice), listed in Open questions. **Owner:** 37.2. **Affects:** spec/economy/buildings.md; information/noticing.md and memory.md
(37.4's: reading and keeping); letters_and_documents.md (writing as a later skill); proposals/law.md (a rule written at a seat);
beliefs_and_values.md (OPEN L-25: passing on by exposure).

## Summary

**Instead of designing a church,** every building carries what its people write on it:
- a **description**: what it is or looks like, in their words;
- **lines**: a dedication, a rule, the names of the dead, a story.

**Who reads and who writes:**
- Anyone who enters a building or attends to it reads them.
- Anyone present can change or deface them, at a cost in work, and may be seen doing it.
- Building finely costs more and makes a building more noticeable. That is its only payback.

**Why:**
- A building's purpose then comes from its fittings, who may enter, and what is written there. A hall is a court because a rule is
  written there and people gather to hear it.
- It measures what agents value when nothing pays: what they build, what they write, whether it spreads, and whether they fight over
  it.

## 1. What a building carries

| | Who writes it | When | Length | Shown to |
|---|---|---|---|---|
| **name** | its builder; later its holder | at `build` (as now), or `name` | a few words | everyone who knows of it (as now) |
| **description** | its builder or holder; anyone, as a change (§3) | at `build` (`describe`), or `write` | one sentence (about 25 words) | everyone who sees the building, after the engine's own facts (structure, fittings, held by) and set apart as their words |
| **lines** | anyone at the building (§3) | `write` | a sentence each (about 30 words); places by size: small room 2, medium 4, hall 8, a monument 3 (proposed) | whoever enters it (sleeps, works or speaks inside) or attends to it that day |

**How they're shown.** Lines are shown as writing in the world, with where they are and how they look:
- 'Carved over the door: "..."';
- 'Painted on the east wall: "..."'.

Each is quoted and capped in length. They're never shown as part of the agent's instructions. Text that one agent writes and others
read can carry instructions as well as content, so the frame and the cap are the guard.

**How long they last:**
- They last with the building.
- A ruined building (condition 0) can't be read until repaired.
- Painted lines on wattle wear: one fades with each break of the building (proposed). Carved lines on timber or stone last.

**What a reader keeps.** It may take a line it read as one of its own lines kept for good (D4-64), by its own choice like any kept
line. That is how a written line passes into people. Reading is free and automatic; keeping is chosen.

## 2. A monument: a building with no room

A **monument** has no floor and no fittings: a carved post, a standing stone, a cairn.
- **Cost (proposed):** a post 2 timber and 2 units; a stone 4 stone and 4 units, a mason's work; a cairn 6 stone and 3 units, anyone.
- **Where:** it stands on any parcel but water, takes 1 space of ground (built ground or scrub; elsewhere it takes none), and has a
  description and 3 lines.
- **Uses:** marking a grave, a boundary, a claim, a meeting place or an event.
- **What exists now:** burial (D2-96) already makes a grave; a monument is what people put there if they choose to.

## 3. Writing, changing and defacing

**Verbs** (D4-24: a small set):
- `write {at: a building or monument here, line?: which, text}` writes a new line in a free place, or replaces one;
- `write {at, description: text}` replaces the description;
- `erase {at, line}` scratches one out.

No line comes with a building: each costs its own engraving (D2-170). The description is written with the build.

| Act | Work (D2-170; calibrate) | Seen |
|---|---|---|
| paint a line (wattle, timber) | 2 units | by the noticing rule, as work at the building |
| carve one (timber) | 4 units, with a tool (wears it) | the same |
| carve one in stone | 6 units, a mason's, with a tool | the same |
| change or erase another's, or the description | the same as writing it, plus 1 | the same; the building's people notice next time they see it ("the dedication over the door has been scratched out") |

- **Who may write:** anyone who can reach the building. Writing on another's building isn't refused, because the engine enforces
  only possession (D4-23). It is seen and remembered, and may be disputed by custom or law, like any use of what others hold.
- **The record:** the journal keeps every text with who wrote it and when, so ground truth and each person's reading can be
  compared.

## 4. Extravagance in tiers (D2-171)

`build {..., "how": "fine" | "rich" | "grand"}` (a modifier, D2-93), for a building or a monument:

| Tier | Materials | Work | Noticed | Described |
|---|---|---|---|---|
| plain | x1 | x1 | as any building | (as now) |
| fine | x1.5 | x2 | also from neighbouring parcels | "finely built" |
| rich | x2.5 | x4 | also named in the village overview and on arrival | "richly built" |
| grand | x4 | x8 | also seen from the road's last stretch coming in | "a grand ..." |

A tier can be raised later by paying the difference (materials and work). Nothing else pays it back (Q4).

## 5. What it lets us measure

- **What agents build when nothing pays:** monuments, unfitted rooms, fine work.
- **What they write:** dedications, rules, names of the dead, claims, insults.
- **Spread:** whether written lines are kept by those who read them, and how far a line travels in people from where it is written.
  This is the first case of passing on by exposure (L-25).
- **Fights over meaning:** defacing, and rewriting a rival's lines.
- **Law from below:** a rule written at a gathering place, before law exists (law.md).

**The control:** a world where the monument and lines are unknown. Without it, a shrine built may be the models' picture of a
medieval village rather than a choice.

## Open questions (for Zach)

1. Lengths and places (§1): about 25 words for a description, 30 for a line, and places by size (2, 4, 8; a monument 3)? — Built
   as proposed (02zh §10, which Zach asked to be built; data.py LINES); no decision row of its own; calibrate.
3. Should painted lines wear with the building's breaks? — Built as proposed (02zh §10; night.py: one painted line on wattle fades
   at each break).
4. The tiers: noticeability only, or also something more (visitors, standing)? — Still open: D2-171 decided the cost and how far
   each tier is noticed (built: signs.py, layout.py, roads.py); nothing decides whether a tier should give more, and no run has yet
   shown anyone building finely.
5. The monument (§2): a post, a stone and a cairn at those costs? — Built as proposed (02zh §10; data.py MONUMENTS). The cairn
   raised over a grave (D4-99: 3 stone, 2 units) is a separate thing: a mark on the grave, with no lines.

## History

- 3 Nov: Zach, on village capital: rather than a church, "different buildings they can customize themselves and somehow put
  themselves into"; then: every building, anyone can read, others can deface; write it up. D2-169. Written.
- 3 Nov: Zach: a line costs extra to engrave (D2-170); extravagance in several tiers, each dearer (D2-171); build it with the
  building package (02zh).
- 5 Nov: Swept against DECISIONS, the spec and what is built (37.2): everything here is built at the proposed numbers (02zh §10,
  38.45); question 4 stays open; D4-99's grave cairn is not this file's monument cairn.

## Sources

[spec/economy/buildings.md](../spec/economy/buildings.md); [lasting_memory.md](lasting_memory.md) (D4-64);
[beliefs_and_values.md](beliefs_and_values.md) (L-25); [law.md](law.md); [verb_modifiers.md](verb_modifiers.md) (D2-93);
spec/information/letters_and_documents.md; D2-96, D4-23, D4-24.
