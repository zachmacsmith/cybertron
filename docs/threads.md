# Open threads

A running list of what is in flight, kept up to date as work lands. Newest changes at the top of each section.

## In progress

- **Hugging Face dataset (zachmacsmith/charter-runs), clean and republish**
  - Done:
    - Full history backed up to the private dataset `zachmacsmith/charter-run-backup` and verified by a fresh download: all refs, 16 commits, 539 LFS objects with SHA-256 checks.
    - 16 archives repacked without `claude_sessions/`, history squashed, tags v0.9-v0.14 deleted, the 58 unreferenced LFS files permanently deleted.
    - Card and changelog renamed to Cybertron, the cleaned state tagged v0.15.
    - `publish --audit` on a fresh snapshot: clean.
  - Next: the full suite on the merged privacy gate. Then publish the no-goal Millbrook runs (below), switch the dataset back to public (confirm with Zach first), and fast-forward `main`.
  - Later: rename the dataset to `cybertron-runs`. It is one constant in `cybertron/publish.py`, one in `site/lib/cybertron-data.js`, and a sed over README.md, docs/data_format.md and docs/publishing.md (docs/publishing.md has the recipe).
- **Publish the no-goal runs** once the dataset is ready:
  - Millbrook, no goals (temperaments kept): `cybertron/out/millbrook_nogoal/2026-10-16T15-51-40_seed1`.
  - Millbrook, no goals and no temperaments: `cybertron/out/millbrook_nogoal_notemp/2026-10-16T17-23-29_seed1`.
  - Their cards should say that the first run's temperaments still held goal and payoff wording, since fixed; that both use engine 17 while the goal run used engine 12; and that the CLI names each agent's model.
- **Obligations system + usability round 2** (agent; branch `wp/obligations2`).
  - Finish the interrupted `wp/obligations` build: manual legs, `fulfil`, due lines, reminders, notices, escalation, role cards, petitions, forgiving args. Engine 19 if a default flips.
  - Then rerun the five usability worlds with manual obligations, role cards, Opus decision seats, goals tied to roles and only the camps each test needs.
  - Write-up: docs/review/31_institutions/09_usability_round2.md.
- **`wp/publish-complete` merge check** (agent; trial branch `trial/publish-complete`). Oct 15 branch: continue published runs, `calls_seen` instead of viewer.json, releases name their code. Is it still wanted, and does it merge onto the renamed code with the privacy gate?

## Offered, not started

- Clean A/B: rerun Millbrook with goals on the current engine (about 25 min), so the no-goal comparison is not confounded by engine 12 vs 17.
- Qualitative read of the no-goal, no-temperament run: posts and self-set aims, as done for the first no-goal run.
- Model-identity leak check: rerun the model-identification interviews on `LLM_BACKEND=api` (no CLI text). About $1, and it needs an API key.
- Publish the model-identification interviews (E_models, F_creator) next to the situational-awareness ones.

## Bugs

- `agents/<Name>/working/notes.md` is empty ("(none)" every round) in recent runs, although agents write their scratchpads.

## Later

- Fragment composer, a pairwise interlock matrix of institutions, and the slim Private-regime world (docs/review/31_institutions/08_integration.md).

## Recently done

- 2026-10-20:
  - Publish privacy gate (`cybertron/privacy.py`, `publish --audit`, wider NEVER list).
  - Dataset id single-sourced, `publish --repack-raw`, docs/publishing.md.
  - Dataset cleaned, see above.
- 2026-10-19: project renamed charter -> cybertron; GitHub repo renamed; engine 18 (prompts no longer name the world).
- 2026-10-16:
  - Per-agent `goals.explicit.<id>: none` and `personality.explicit.<id>: none`.
  - Goalless temperaments and manuals carry no goal wording.
  - No-goal and no-goal/no-temperament Millbrook runs.
