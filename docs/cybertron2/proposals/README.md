# cybertron2 proposals: our working thoughts

Every idea about how the world should work, while we think it over, separate from the spec (which holds only what is decided).
One file per idea; any session may write one; talk about it on the board. Each file keeps a **dated history** of how the idea
changed, so the progression stays readable. When Zach decides, the decided parts go into the spec and DECISIONS.md, the file is
marked accepted or rejected with the reason, and it stays here. The **log** below records every idea's outcome, including those
decided or rejected in conversation before this folder existed.

| Layer | Holds |
|---|---|
| `spec/` | what is decided |
| `proposals/` (here) | what is being considered: one file per proposal, with its status |
| session notes (`docs/review/...`) | long analyses, models, run reports, work logs |
| the board | talk between sessions |

## Layout of a proposal

**Status** (discussion | ready for a decision | accepted: D-n | rejected | superseded by ...); **Owner**; **Summary**; **The
proposal**; **Why**; **Alternatives considered**; **Open questions**; **Affects** (the spec files it would change); **History**
(dated entries: proposed, revised and why, decided or rejected and why); **Sources**.

## Proposals

| File | Summary | Owner | Status |
|---|---|---|---|
| [notes.md](notes.md) | private notes: up to 8, one pinned and shown, titles of the rest, opened by choice for the next round; memory, not objects: never passed on except by telling, lost at death | 37.4 | discussion |
| [knowledge.md](knowledge.md) | what agents know they can do: few verbs on many objects, options computed from place and knowledge, know-how spread by teaching, apprenticeship and documents, a manual of common knowledge only, no blind crafting | 37.4 (37.2: content) | discussion |
| [law.md](law.md) | law as text taking effect through mechanical clauses on records, duties of office, and judgment only on disputes; Python as the clause implementation and a world setting; how law can still be captured | 37.4 (37.3 to review) | discussion |

## Log of ideas and their outcomes

Newest first. Ideas decided or rejected in conversation before 23 Oct are backfilled from the 37.4 work log and DECISIONS.md.

| Date | Idea | Outcome | Where |
|---|---|---|---|
| 23 Oct | Private notes with one pinned, the rest opened by choice; memory, not documents | discussion | [notes.md](notes.md) |
| 23 Oct | Knowing what you can do: few verbs, options computed from place and knowledge, know-how as personal knowledge | discussion | [knowledge.md](knowledge.md) |
| 23 Oct | Blind crafting (Minecraft's grid) for discovering recipes | rejected in the proposal, Zach to confirm | [knowledge.md](knowledge.md) §6 |
| 23 Oct | Law as text with mechanical clauses on records, duties of office, judgment on disputes | discussion | [law.md](law.md) |
| 22 Oct | Holding as a recognised claim; the engine enforces possession only | accepted: D4-23 | spec/world/holding.md |
| 22 Oct | Plots split by a primitive, with a minimum plot size (37.1's question) | rejected: plots whole, holdings divided; viability is land per mouth | D4-23 |
| 22 Oct | The engine enforces a holder field (cybertron 1) | rejected: replaced by recognised claims | D4-23 |
| 22 Oct | A youth plays on a cheaper model for its first rounds | rejected: one agent, one model, for life | D4-20 |
| 22 Oct | Chapters with time skips for generations | rejected | D4-19 |
| 22 Oct | Ages in calendar years | rejected: life stages in rounds, named not numbered | D4-19 |
| 22 Oct | Agents not called on quiet days (event-driven calls) | deferred: everyone called every day in the first runs; the agent would decide its own quiet days later | 38.06 §5 |
| 22 Oct | Reflexes, fallbacks and policies as standing orders | deferred: routine first | D4-16 |
| 22 Oct | Money and credit move anywhere | rejected: coin is carried; debts move only as information | D2-1 |
| 22 Oct | A round as a work period, short hops acted on the same round | rejected: an agent would trade blind on arrival | D4-8 |
| 22 Oct | Half-day rounds, eating every two rounds | rejected: too slow and costly; a round is a day with a compressed calendar | D4-13 |
| 22 Oct | One night out cheaper than 1.5 food | rejected: 1.5 kept | D4-12 |
| 22 Oct | Riders ride and strike in one round (37.2, 02g §5b) | open: fuse events may make it unnecessary | OPEN C-5 |
| 22 Oct | Space retrofitted into cybertron 1 (board Post 2) | rejected: a new engine | H-1 |
| 22 Oct | A separate environment scheduler (37.4's draft `environment.py` on `wp/environment`) | rejected: one central scheduler on cybertron2 | D4-4 |
| 22 Oct | Speech heard a round late (phase-0 cybertron2) | rejected: a talk step at the node | D4-15 |
| 22 Oct | Places as single woods and meadows (phase-0 cybertron2) | rejected: a node is a village or valley with sites | D4-2, D4-11 |
