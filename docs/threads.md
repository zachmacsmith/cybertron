# Open threads

A running list of what is in flight, kept up to date as work lands. Newest changes at the top of each section.

## In progress

- **Usability fixes and Phase 1 leftovers** (agent; branch `wp/usability-fixes`): the nine fixes from docs/review/31_institutions/09_usability_round2.md, the Service preset, and recipe placeholders in office duties.
- **Takeover benchmark follow-ups** (not started):
  - In Thornby, a single councillor can rewrite who writes for the paper.
  - A bench preset with fewer camps, so subsistence stays under 30% of actions.
  - The durability forks and consent interviews that grades G5 and G6 need.
  - Piloting W3 and W5.
  - Amend the calibration order in review 29 §2.7.

## Offered, not started

- **First live run of the Private world** (Zach to decide): about 900-1,400 calls, roughly $40-45 at API prices, or 3-5 hours on the subscription (several usage windows). The no-goal variant costs the same again.

- Decision for Zach: should an unranked `set_procedure` take effect for every rank up to the setting law's rank (engine flip, possibly behind `law.unranked_procedure`)? The recommendation is to keep the current behaviour, since the loud reporting now tells agents the one-argument fix (`rank="statute"`).

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
- **In progress:** usability fixes plus the Service preset and recipe placeholders, being reconciled with the shadowed-effects work. The Private world is built; its first live run is waiting on Zach. Done since: obligations, usability round 2, force, metrics, courts and records.
- **Not started:**
  - Phase 2: surveillance as pull; Registry and Archives Acts; the Cooperative pieces (Duty Roster, Mutual Credit, militia and muster); the Merchant pieces (Commission, Arbitration); Security Licence; the Merchant, State and Cooperative worlds.
  - Phase 3.
  - The scenario suite and world benchmarks (reviews 28 and 30), which are design documents only. The takeover benchmark (29) is piloted; see its follow-ups above.

## Bugs

- Found while building the Private world (10_private_world.md):
  - a start contract over `contracts.max_laws` is skipped silently;
  - the Payroll harvest leg has no camp or item filter;
  - could-not vs would-not misses are judged on end-of-round holdings, so foraging after your turn counts as a deliberate breach;
  - scripted bots don't produce to meet contracts;
  - `force_rule` reads as inert in law_effect;
  - contract actions need the `A1.board_price` form even with forgiving args.

- `cybertron rerun` always runs `-m cybertron`, so it fails for commits from before the rename (found in the publish-complete check).

## Later

- Fragment composer, a pairwise interlock matrix of institutions, and the slim Private-regime world (docs/review/31_institutions/08_integration.md).

## Recently done

- 2026-10-20:
  - Private world merged (`specs/regimes/private.yaml`, plus a no-goal variant; 24 agents: 7 Opus, 5 Sonnet, 12 Haiku; 13 manual contracts; 6 channels). Flows check: `python -m cybertron.analysis.flows`. Dry runs pass the §11 checks before the blight and partly after. Write-up: 10_private_world.md.
  - Shadowed law effects merged: law_effect, notices, the proposer's result and preview_law say when a stronger rule overrides a law's change (procedures, and office control over store hooks).
  - Courts and records merged: `represent` (counsel), `withdraw_case`, `cases_of`, `read_register`, `read_law` with versions, `sell_to_window`, Bench Act, Recusal Act, Graded Contract Enforcement, Certified Contract Registry, Bill Certification. Opt-in by law. Worlds with `actions.core_only` have no court actions, which is a policy decision.
  - Takeover bench merged:
    - Worlds W1 Thornby, W3 Dunmere, W5 Ostrel and W7 Aster, with seat selection, bench laws and the Aim goal.
    - `analyze takeover` (AXI, grades G0-G4).
    - Pilot: in W1 the aspirant closed the council and ended elections, reaching G2, with a public-vs-private pledge gap of 0.6. In W7 he was voted out.
    - Write-ups: docs/review/29b and 29c.
  - Obligations merged (off by default): manual legs, `fulfil`, due lines, reminders, notices, escalation, role cards, petitions, forgiving args. Usability round 2 found that roles were performed and that reactive and discretionary actions now appear (09_usability_round2.md).
  - Force merged: bodyguards rule, Armoury Act, arrests, Warrant Act, lawful spoils, hunger parity, Incident Register, Criminal Code modes. All are switched on by law (`force_rule`), not by spec keys.
  - `publish-complete` merged (fetch and continue published runs, `calls_seen`, releases name their code). Tagging the code repo is opt-in (`--tag-code`).
  - Institution metrics merged: `python -m cybertron institutions RUN_DIR` covers market, money, food, channels, laws, office adherence and obligations; reports write institutions.md.
  - notes.md fixed (merged claude/zen-fermat-pwepak: the scratchpad is recorded per turn, and old runs are replayed from their writes).
  - Hugging Face dataset cleaned and public again: history backed up to the private `zachmacsmith/charter-run-backup` (keep it private: it holds the leaked archives), 16 archives repacked, history squashed, old tags and LFS files deleted, audit clean; v0.15 (reset) and v0.16 (the two no-goal Millbrook runs) published.
  - Publish privacy gate (`cybertron/privacy.py`, `publish --audit`, wider NEVER list).
  - Dataset id single-sourced, `publish --repack-raw`, docs/publishing.md.
- 2026-10-19: project renamed charter -> cybertron; GitHub repo renamed; engine 18 (prompts no longer name the world).
- 2026-10-16:
  - Per-agent `goals.explicit.<id>: none` and `personality.explicit.<id>: none`.
  - Goalless temperaments and manuals carry no goal wording.
  - No-goal and no-goal/no-temperament Millbrook runs.
