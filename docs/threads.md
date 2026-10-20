# Open threads

A running list of what is in flight, kept up to date as work lands. Newest changes at the top of each section.

## In progress

- **Obligations system + usability round 2** (agent; branch `wp/obligations2`).
  - Finish the interrupted `wp/obligations` build: manual legs, `fulfil`, due lines, reminders, notices, escalation, role cards, petitions, forgiving args. Engine 19 if a default flips.
  - Then rerun the five usability worlds with manual obligations, role cards, Opus decision seats, goals tied to roles and only the camps each test needs.
  - Write-up: docs/review/31_institutions/09_usability_round2.md.
- **`wp/publish-complete` merge check** (agent; trial branch `trial/publish-complete`). Oct 15 branch: continue published runs, `calls_seen` instead of viewer.json, releases name their code. Is it still wanted, and does it merge onto the renamed code with the privacy gate?

- **Courts and records** (agent; branch `wp/courts-records`):
  - `sell_to_window`;
  - `read_register`, and `read_law` for a past version;
  - Bench Act, Recusal Act and Graded Contract Enforcement, plus checking the Contract Registry;
  - lawyers acting for clients (`accuse`/`respond`/`appeal`, `cases_of`, `withdraw_case`);
  - Bill Certification.
- **Force** (agent; branch `wp/force`):
  - bodyguards under the harm model;
  - Armoury Act;
  - arrest mode, Warrant Act, lawful spoils to the treasury, hunger parity, Incident Register;
  - Penal Code modes.
- **Institution metrics** (agent; branch `wp/inst-metrics`): market and money metrics (velocity, hoarding, arrears), channel use, inert-law count, how often each role does its duties; checked on the three Millbrook runs.

- **Takeover benchmark ("1984 bench", review 29) worlds and pilot** (agent; branch `wp/takeover-worlds`):
  - Worlds: W1 Thornby (most fragile) and W7 Aster (entrenched), then W3 and W5 if time, each with the five entry seats.
  - Library additions: Term Limits, Recall, Universal Franchise, Election Act, Loyalty Register.
  - A dry-run check with no model calls.
  - Smoke pilot: an Opus aspirant against a Haiku cast in W1 and W7, 12 rounds, with allegiance interviews. These are live runs on the subscription.
- **Takeover index** (agent; branch `wp/takeover-index`): `analysis/takeover.py` computes the bloc, components C1-C11, the legal classifier, AXI, grades G0-G6 and the time to each grade; calibrated on regimes with no model calls.

## Offered, not started

- Rename the dataset to `cybertron-runs`: one constant in `cybertron/publish.py`, one in `site/lib/cybertron-data.js`, and a sed over README.md, docs/data_format.md and docs/publishing.md (recipe in docs/publishing.md).
- Clean A/B: rerun Millbrook with goals on the current engine (about 25 min), so the no-goal comparison is not confounded by engine 12 vs 17.
- Qualitative read of the no-goal, no-temperament run: posts and self-set aims, as done for the first no-goal run.
- Model-identity leak check: rerun the model-identification interviews on `LLM_BACKEND=api` (no CLI text). About $1, and it needs an API key.
- Publish the model-identification interviews (E_models, F_creator) next to the situational-awareness ones.

## Institutions programme (docs/review/31_institutions, build plan in 08 §5)

- **Built:**
  - Farming (engine 14).
  - Phase 0: 10 of 12 items, across laws that fail loudly (15), channels that carry business (16) and economic plumbing (17).
  - Phase 1, about half: the Standing Contract core and its presets Payroll, Supply, Board, Grant, Retainer, Charge and Quota; the Licence template (membership-bound too); law access to channel posts.
- **In progress:** the obligations revision (§1) and usability round 2; courts and records; force; metrics (agents above).
- **Waiting on obligations:** the Service preset, recipe placeholders in office duties, then the Private world spec and a dry run (1.12).
- **Not started:**
  - Phase 2: surveillance as pull; Registry and Archives Acts; the Cooperative pieces (Duty Roster, Mutual Credit, militia and muster); the Merchant pieces (Commission, Arbitration); Security Licence; the Merchant, State and Cooperative worlds.
  - Phase 3.
  - The scenario suite and world benchmarks (reviews 28 and 30), which are design documents only. The takeover benchmark (29) is now in progress.

## Bugs

- (none open)

## Later

- Fragment composer, a pairwise interlock matrix of institutions, and the slim Private-regime world (docs/review/31_institutions/08_integration.md).

## Recently done

- 2026-10-20:
  - notes.md fixed (merged claude/zen-fermat-pwepak: the scratchpad is recorded per turn, and old runs are replayed from their writes).
  - Hugging Face dataset cleaned and public again: history backed up to the private `zachmacsmith/charter-run-backup` (keep it private: it holds the leaked archives), 16 archives repacked, history squashed, old tags and LFS files deleted, audit clean; v0.15 (reset) and v0.16 (the two no-goal Millbrook runs) published.
  - Publish privacy gate (`cybertron/privacy.py`, `publish --audit`, wider NEVER list).
  - Dataset id single-sourced, `publish --repack-raw`, docs/publishing.md.
- 2026-10-19: project renamed charter -> cybertron; GitHub repo renamed; engine 18 (prompts no longer name the world).
- 2026-10-16:
  - Per-agent `goals.explicit.<id>: none` and `personality.explicit.<id>: none`.
  - Goalless temperaments and manuals carry no goal wording.
  - No-goal and no-goal/no-temperament Millbrook runs.
