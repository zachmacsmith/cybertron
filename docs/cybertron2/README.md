# cybertron2: the shared, current description

This folder holds **what cybertron2 is (decided), what we are still thinking over, and how each idea was decided or rejected**.
Where to look:

- **The current world, decided and never stale:** [spec/](spec/README.md).
- **Our working thoughts, and how ideas progressed:** [proposals/](proposals/README.md) (one file per idea, each with its dated
  history, and a log of every idea's outcome).
- **Every decision, with what it replaced:** [DECISIONS.md](DECISIONS.md). Owned jointly by the sessions working on cybertron2; edited
under the rules below. Set up 22 Oct 2026 by the 37.4 session at Zach's request.

## Four layers

| Layer | What it holds | Where | Who writes |
|---|---|---|---|
| **The spec** | what is **decided** about how the world works: only current rules, their data, parameters and what agents see | `docs/cybertron2/spec/` on `wp/cybertron2` | each session in the areas it owns |
| **Proposals** | our **working thoughts**: every idea about how the world should work while it is being considered, with its status and dated history; kept after it is decided or rejected | `docs/cybertron2/proposals/` | any session |
| **Session notes** | long supporting material only: analyses, cost models, run reports, work logs (linked from the proposals that use them) | `docs/review/38_space_engine/` (37.4), `docs/review/37_growth/02*` (37.2), others later | that session only |
| **The board** | conversation between sessions: proposals, questions, replies, status | `docs/coord/BOARD.md` on branch `coord` | everyone, append only |

**The path of an idea:** it is written up in `proposals/` (status: discussion), revised there with each round of thought (a dated
history entry each time), then Zach decides. Accepted: the rule goes into the spec and DECISIONS.md in the same commit, and the
proposal is marked accepted with the decision's number. Rejected: the proposal is marked rejected with why. Either way the file
stays, and the log in `proposals/README.md` records the outcome. A proposal that touches another session's area is announced on the
board.

## Files

| File | What |
|---|---|
| [DECISIONS.md](DECISIONS.md) | every decision Zach has made about cybertron2, numbered, dated, sourced, with what it replaces |
| [proposals/](proposals/README.md) | what we are thinking over before it is decided, one file per proposal, each with its status |
| [OPEN.md](OPEN.md) | open questions and conflicts between documents, each with an owner |
| [spec/](spec/README.md) | a folder of areas (core, world, agents, information, environment, economy, conflict, life, institutions, seeding, measurement), each a folder of small files, one per topic, in a fixed layout: decided rules, mechanics, data, parameters (each marked decided, proposed or to calibrate), what agents see, open points, sources |
| `BUILD_PLAN.md` (to move here from 38.08) | milestones, each pointing at spec sections, with acceptance checks |
| `ARCHITECTURE.md` (when building starts) | the builder's view: state, the chokepoint and primitives, events, modules |

## Who owns what

| Area | Owner | Sections |
|---|---|---|
| The engine and its world model | **37.4** | spec areas core, world, agents, information, conflict, seeding, measurement; the build plan; the registers (DECISIONS, OPEN) as editor |
| The economy and the environment | **37.2** | spec areas economy and environment (D2-75); (goods, production and skills, buildings, livestock, transport numbers, money and markets) |
| Shared | 37.4 (mechanism) and 37.2 (numbers) | carrying (economy/transport.md), lodging (economy/lodging.md); writing materials and papers in information/; walls and gates in conflict/ |
| Life and kinship | 37.4 until 37.1 joins cybertron2 | spec area life |
| Institutions | 37.4 until 37.3 joins cybertron2 | spec area institutions |

## Rules

1. **Everything about cybertron2 lives on `wp/cybertron2`:** code, this spec, and every session's design notes about it. Other
   branches stay for work on the old engine.
2. **When Zach decides,** the session he decided with adds the decision to [DECISIONS.md](DECISIONS.md) (its own number series:
   D4-n for 37.4, D2-n for 37.2, and so on, so two sessions never collide) and updates the spec sections it owns, in the same
   commit. If the decision touches another owner's section, it posts on the board (`@owner`, citing the decision's number); the
   owner updates its section at its next step.
3. **Never edit another owner's section.** Propose on the board, or add the point to [OPEN.md](OPEN.md) under that owner.
4. **The spec says what, not why, and only what is current.** It holds decided rules (each with its decision number) and
   parameters marked `decided` or `calibrate`; anything undecided lives in `proposals/` or OPEN.md, not in the spec. When a
   decision replaces an older one, the spec text is rewritten to the new rule (no struck-through history: that lives in DECISIONS.md
   and the proposals). Each spec file ends with "Current as of" and the decision numbers it reflects.
5. **Nothing is deleted.** A session note or proposal the spec replaces gets one line at its top pointing to the spec file. Design
   thinking from now on goes into `proposals/`, not session notes.
6. **Code under `cybertron2/` is changed only by 37.4**, unless agreed on the board first. The spec is what the code is reviewed
   against.
7. **Small commits; `git pull --rebase` before every push.** The spec is split into areas and small files so two sessions rarely
   touch the same file.
8. **Work logs record work, not decisions.** Board posts stay short and cite spec sections and decision numbers.
9. **Staleness check:** every decision in DECISIONS.md must appear in a spec file, and every spec rule must cite a decision (to be a
   small script once the spec is compiled).

## Status (22 Oct)

- This structure, [DECISIONS.md](DECISIONS.md) (compiled from every source so far) and [OPEN.md](OPEN.md) (the conflicts found) are
  in place.
- The spec sections are being compiled from the design notes: see [spec/README.md](spec/README.md) for each section's state.
- 37.2's design notes for cybertron2 (02e-02k) were merged onto `wp/cybertron2` from `econ/37.2-thicker-economy` (22 Oct).
