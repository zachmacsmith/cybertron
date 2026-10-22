# cybertron2: the shared, current description

This folder is **the one place that says what cybertron2 is and will be**. Everything else (design notes, run reports, work logs,
the coordination board) is how we got here; this is where we are. Owned jointly by the sessions working on cybertron2; edited
under the rules below. Set up 22 Oct 2026 by the 37.4 session at Zach's request.

## Three layers

| Layer | What it holds | Where | Who writes |
|---|---|---|---|
| **The spec** (here) | what cybertron2 is: every decided rule, its data, its parameters, what agents see, and what is still open | `docs/cybertron2/` on `wp/cybertron2` | each session in the sections it owns |
| **Design notes** | the reasoning: analyses, options weighed, models, run reports, work logs | each session's own folder: `docs/review/38_space_engine/` (37.4), `docs/review/37_growth/02*` (37.2), and later any other session's | that session only |
| **The board** | conversation between sessions: proposals, questions, replies, status | `docs/coord/BOARD.md` on branch `coord` | everyone, append only |

A design note is where an idea is worked out with Zach; when Zach decides, the decision is recorded here and the spec section
changes in the same commit. A proposal that changes another session's section goes to the board first.

## Files

| File | What |
|---|---|
| [DECISIONS.md](DECISIONS.md) | every decision Zach has made about cybertron2, numbered, dated, sourced, with what it replaces |
| [OPEN.md](OPEN.md) | open questions and conflicts between documents, each with an owner |
| [spec/](spec/README.md) | one file per system, in a fixed layout: decided rules, mechanics, data, parameters (each marked decided, proposed or to calibrate), what agents see, open points, sources |
| `BUILD_PLAN.md` (to move here from 38.08) | milestones, each pointing at spec sections, with acceptance checks |
| `ARCHITECTURE.md` (when building starts) | the builder's view: state, the chokepoint and primitives, events, modules |

## Who owns what

| Area | Owner | Sections |
|---|---|---|
| The engine and its world model | **37.4** | places and land, time and the round, actions and work, perception and prompts, travel and lodging, communication, environment, conflict, seeding and generation, architecture, build plan; the registers (DECISIONS, OPEN) as editor |
| The economy | **37.2** | goods and resources, production and skills, buildings, transport (the ladder's numbers), money, credit and markets |
| Shared | 37.4 (mechanism) and 37.2 (numbers) | carrying and weights, inns and hosts, livestock |
| Life and kinship | 37.4 until 37.1 joins cybertron2 | ages, households, the family tree, births, death, inheritance |
| Institutions | 37.4 until 37.3 joins cybertron2 | the port plan; membership, offices, contracts in space |

## Rules

1. **Everything about cybertron2 lives on `wp/cybertron2`:** code, this spec, and every session's design notes about it. Other
   branches stay for work on the old engine.
2. **When Zach decides,** the session he decided with adds the decision to [DECISIONS.md](DECISIONS.md) (its own number series:
   D4-n for 37.4, D2-n for 37.2, and so on, so two sessions never collide) and updates the spec sections it owns, in the same
   commit. If the decision touches another owner's section, it posts on the board (`@owner`, citing the decision's number); the
   owner updates its section at its next step.
3. **Never edit another owner's section.** Propose on the board, or add the point to [OPEN.md](OPEN.md) under that owner.
4. **The spec says what, not why.** Each rule carries its status (`decided D4-12`, `proposed`, `calibrate`, `open`) and links to
   the note that explains it. Reasoning stays in the notes.
5. **A note the spec replaces** gets one line at its top: "Superseded by docs/cybertron2/spec/<file>.md §x (date)". Notes are
   never deleted.
6. **Code under `cybertron2/` is changed only by 37.4**, unless agreed on the board first. The spec is what the code is reviewed
   against.
7. **Small commits; `git pull --rebase` before every push.** The spec is split into one file per system so two sessions rarely
   touch the same file.
8. **Work logs record work, not decisions.** Board posts stay short and cite spec sections and decision numbers.

## Status (22 Oct)

- This structure, [DECISIONS.md](DECISIONS.md) (compiled from every source so far) and [OPEN.md](OPEN.md) (the conflicts found) are
  in place.
- The spec sections are being compiled from the design notes: see [spec/README.md](spec/README.md) for each section's state.
- 37.2's design notes for cybertron2 (02e-02k) were merged onto `wp/cybertron2` from `econ/37.2-thicker-economy` (22 Oct).
