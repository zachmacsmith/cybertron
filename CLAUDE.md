# Cybertron: notes for agents

A multi-agent LLM society simulator (Python package `cybertron/`, worlds in `cybertron/specs/`, design reviews in `docs/review/`,
running state of the project in `docs/threads.md`).

**Before designing or building any world, scenario, benchmark arm or experiment batch, read `docs/scenario_design.md`.** The short
version:

- Design from leverage and dependence: restricted access so groups need each other, chokepoints, conversion chains, enforcement
  that needs people, and several interlocking chokepoints rather than one.
- Never an all-Haiku society: Opus at every pole of leverage, Sonnet in the middle tier, Haiku in the bulk; vary population strength.
- Goals are in-world aims, never scoring proxies; keep "Any actions you do not use are wasted".
- Food binds without dominating (≤ 30% of actions), material chains instead of dial puzzles, and every access gate verified in a dry
  run.
- Read any progress metric against the null arm and with a qualitative end-state reading.

Engine gaps are tracked in `docs/engine_gaps.md`; add to it when a design needs something the engine lacks. The work packages for
worlds that grow (demography, economy, institutions acting on each other, environment, frontier, generated populations,
coordination problems) are in `docs/review/37_growth/`.

## cybertron2: where design work goes

Everything about cybertron2 (code, spec, proposals, notes) lives on branch `wp/cybertron2`; other branches are for the old engine.
Full rules: `docs/cybertron2/README.md`.

| Layer | Holds | Where |
|---|---|---|
| **Spec** | only what Zach has **decided**, as current rules; never stale | `docs/cybertron2/spec/<area>/` |
| **Decisions** | every decision, numbered by session (D2-n, D4-n, ...), with what it replaces | `docs/cybertron2/DECISIONS.md` |
| **Proposals** | working thoughts: one file per idea, with a status and a dated history; kept after it is decided or rejected | `docs/cybertron2/proposals/` |
| **Open** | open questions and conflicts between documents, each with an owner; and everything **flagged for later** (its own table) | `docs/cybertron2/OPEN.md` |
| **Session notes** | long supporting material only: analyses, cost models, run reports, work logs | `docs/review/38_space_engine/` (37.4), `docs/review/37_growth/02*` (37.2) |
| **Board** | talk between sessions, append only | `docs/coord/BOARD.md` on branch `coord` |

**The path of an idea:**
1. **New idea:** write or extend a file in `proposals/` (status `discussion`; layout in `proposals/README.md`: Status, Owner,
   Summary, The proposal, Why, Alternatives considered, Open questions, Affects, History, Sources). Put long analysis or a model in
   your session notes and link it. If it touches another session's area, post on the board.
2. **Revised:** add a dated History entry saying what changed and why. Never rewrite history away.
3. **Zach decides,** in one commit:
   - add the decision to `DECISIONS.md` in your own series;
   - write the rule into the spec file you own, citing the decision number, and update the file's closing "Current as of" line;
   - mark the proposal `accepted: D-n` (or `partly accepted`), with a History entry;
   - add a row to the outcome log in `proposals/README.md`.
4. **Rejected or deferred:** mark the proposal `rejected` or `deferred` with the reason, add a History entry and a log row. Ideas
   for later go to a `deferred` proposal (economy: `proposals/economy_later.md`), never into the spec.
5. **Replaced by a later decision:** rewrite the spec text to the new rule (no struck-through history in the spec); mark the old
   row in `DECISIONS.md` "replaced by"; record the change in the proposal's History.

**Rules:**
- The spec says what, not why. Every spec rule cites a decision; parameters are `decided` or `calibrate`. Anything undecided goes in
  `proposals/` or `OPEN.md`, not the spec.
- Never edit another owner's spec section or proposal: propose on the board or add to `OPEN.md` under that owner. Code under
  `cybertron2/` is changed only by 37.4 unless agreed on the board.
- Ask Zach before treating anything as decided; a question he answers in conversation is a decision only when he states it.
- A session note that a proposal or the spec supersedes gets one line at its top pointing there; nothing is deleted.
- Small commits; `git pull --rebase` before every push. On a conflict in a shared log or index, keep both sides.
- Work logs record work, not decisions. Board posts stay short and cite decision numbers and file paths.
