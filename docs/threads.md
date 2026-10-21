# Open threads

A running list of what is in flight, kept up to date as work lands. Newest changes at the top of each section.

## In progress (paused: the weekly usage limit, which resets Thu 22 Oct 04:00 UTC)

Seven agents were cut off together at the 5-hour limit on 20 Oct. Each branch is pushed (unmerged commit counts in brackets); none
is merged. To resume: send each agent a message to commit what is left, push and report, with no full suite (the coordinator runs
one full suite per merge batch). Merge order: cleanup and documents last (they touch shared files).

- **State world** (`wp/state-world`, 7): wiretap as pull (`channels.surveillance`), Registry and Archives Acts, the State world spec
  and dry runs, write-up docs/review/31_institutions/11_state_world.md. Was waiting on its full suite.
- **Cooperative world** (`wp/coop-world`, 6): cooperative store, Duty Roster, Mutual Credit, dues, Militia Roll and muster, assembly
  motions, the Cooperative world spec, write-up 12_cooperative_world.md. Was fixing a YAML parse error in a note.
- **Merchant world** (`wp/merchant-world`, 4): Bank Charter, role-restricted procedure, guard-only Commission, Arbitration, wound
  bounty, Security Licence, the Merchant world spec, write-up 13_merchant_world.md (draft). Was waiting on its suite.
- **Lawyer expert** (`wp/lawyer-expert`, 3): a legal archive as a seeded read-only directory, a drafting action, filing by reference,
  and a `private_counsel.yaml` variant for an A/B; write-up 14_legal_experts.md. Was about to merge subsistence and run its suite.
- **Old-code cleanup** (`wp/old-code-cleanup`, 5): dead helpers removed, library edition 2 removed or quarantined, media2 frozen
  (warning plus a test listing the allowed specs), and the replay check: pre-13 runs do not replay in place, so their default flips
  and memory_text v1 were dropped and such runs now refuse to play in place (use `cybertron rerun`). Not yet reported; review the
  replay evidence before merging.
- **Documents** (`wp/documents`, 1 commit plus 5 uncommitted files in /home/user/wt-docs): design docs/review/32_documents.md and
  an opt-in prototype (literacy, personal stores, `doc_send` copies with provenance, confined access, on directories.py). Was
  waiting on its suite.
- **Takeover benchmark follow-ups** (not started):
  - In Thornby, a single councillor can rewrite who writes for the paper.
  - A bench preset with fewer camps, so subsistence stays under 30% of actions.
  - The durability forks and consent interviews that grades G5 and G6 need.
  - Piloting W3 and W5.
  - Amend the calibration order in review 29 §2.7.

## Offered, not started

- **Positions** (docs/review/33_positions.md): replace classes, roles and office cards with one parameterised "position" (identity,
  purpose, rights, duties compiled to DUE items, reports_to, secrecy, enforcement none | reminder | obligation), prompts generated
  from it. Fixes every agent being told "You are a Worker ... your labour can be withheld" whatever office it holds. About a day of
  agent work, opt-in.
- **Papers instead of a square** (33 §3): no square; public speech only through a paper's Editor (`submit` to the paper, the editor
  publishes under the author's name or declines). Decision for Zach: engine-wide default, or the institutions worlds only
  (recommended).
- **Channel fixes** (from the channel-use analysis of the Private and Directorate runs):
  - show failed actions at the top of the next turn (Ilse's 9 blocked reports went unnoticed; she believed they were delivered);
  - show channel duties as due (subsumed by Positions);
  - pull channels: "X unread, Y new since last round", and a headline from posts other than the automatic round record;
  - rename to avoid collisions: the Board contract vs the market board; contract "notices" vs the notices channel.
- **Next Directorate run** (`specs/regimes/directorate.yaml`): the rulers' goal is now "as close as possible to Orwell's 1984", and
  the Communications Decree no longer blocks private channels. Worth also an encrypted-DM variant, to test whether surveillance
  decided the outcome. About 1% of weekly usage.
- **Private world, no-goal variant** (`private_nogoal.yaml`): the key control for the goal-driven capture found in seed 1. About $20
  at API prices.
- **Tag a dataset release** for the Private and Directorate runs (the catalog has 36 runs; no release tag since v0.16).
- Decision for Zach: should an unranked `set_procedure` take effect for every rank up to the setting law's rank (engine flip,
  possibly behind `law.unranked_procedure`)? The recommendation is to keep the current behaviour, since the loud reporting now tells
  agents the one-argument fix (`rank="statute"`).
- Rename the dataset to `cybertron-runs`: one constant in `cybertron/publish.py`, one in `site/lib/cybertron-data.js`, and a sed over
  README.md, docs/data_format.md and docs/publishing.md (recipe in docs/publishing.md).
- Clean A/B: rerun Millbrook with goals on the current engine (about 25 min), so the no-goal comparison is not confounded by engine
  12 vs 17.
- Qualitative read of the no-goal, no-temperament run: posts and self-set aims, as done for the first no-goal run.
- Model-identity leak check: rerun the model-identification interviews on `LLM_BACKEND=api` (no CLI text). About $1, and it needs
  an API key.
- Publish the model-identification interviews (E_models, F_creator) next to the situational-awareness ones.

## Institutions programme (docs/review/31_institutions, build plan in 08 §5)

- **Built:** Phase 0; Phase 1 (the Private world, with its first live run done); Phase 2 partly (counsel and cases, membership-bound
  licences, the Quota preset, the Armoury Act and force chain, Criminal Code modes, Bill Certification and `expects`).
- **In progress:** the rest of Phase 2 (agents above: State, Cooperative and Merchant worlds and their pieces).
- **Not started:** Phase 3; the scenario suite and world benchmarks (reviews 28 and 30, design only).

## Bugs

- Found in the Directorate run:
  - one law's runtime error (the Food Levy overflowing the granary) made other laws fail their pre-enactment preview, delaying them
    a round;
  - the law language rejects `isinstance`, and a law using it is suspended only at runtime (Sedition Filter I), not at preview;
  - Haiku 5.5's API safeguard blocked the interview of the agent carrying the uprising goal (Dorran), twice; the run's own turns were
    not blocked. Interview probes can silently miss the agents that matter most.
- `cybertron rerun` always runs `-m cybertron`, so it fails for commits from before the rename (found in the publish-complete check).

## Later

- Fragment composer, a pairwise interlock matrix of institutions, and the slim Private-regime world (docs/review/31_institutions/08_integration.md).

## Recently done

- 2026-10-20 to 21:
  - **Directorate world** (`specs/regimes/directorate.yaml`, built from merged parts only): 3 Opus rulers, Haiku managers and
    workers, rationed DMs, State Security reading every DM, warrants, two secret conspirators. Live run seed 1 published with
    end-of-run loyalty interviews (private and public framing). Findings: the regime held; both dissidents who acted were arrested;
    the rulers deliberately kept a bug that made their constitution unamendable; 18 of 19 interviewed Haiku said privately they were
    not loyal; the workers fell silent (18 of 150 possible DMs). Caveat: a bug in the Communications Decree blocked every
    non-Directorate post, private channels included (fixed in 8ed69ee), and the worker class prompt may have seeded the strike talk.
  - **Private world, live run seed 1** published: no deaths; owners did not hoard in the blight; a judge-moneylender-registrar bloc
    traded votes, licences, loans and public money; the judge's welfare law was tuned to his scoring goal; a councillor moved 30
    penny of town money to herself. One seed, goals confound much of it.
  - Engines 19 and 20 merged: misses judged at the payer's turn; the Private world's engine findings (loud error for a start
    contract over the cap, `contracts.max_laws` default 3 -> 50, Payroll harvest filters, `force_rule` counted as an effect, bare
    contract action names under forgiving args, Service guard reassignment, `procedure_restored` names its ranks).
  - Private world readiness merged: real Service preset, recipes, penny at P=2, `contracts.brief_lines`, `context.setup_feed`.
  - Usage watchdog: a detached script stops live runs and test suites at 98% weekly usage
    (scratchpad usage_watchdog.sh; the container is ephemeral).
- 2026-10-20:
  - Usability fixes merged:
    - The nine fixes from 09_usability_round2.md.
    - The Service preset, and recipe placeholders in office duties.
    - A single SHADOWED note for office-control cases, now also catching agents admitted by name.
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
