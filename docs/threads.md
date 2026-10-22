# Open threads

A running list of what is in flight, kept up to date as work lands. Newest changes at the top of each section.

## In progress (22 Oct)

- **Suite speed** (full suite 16 min at -n 3 on 22 Oct, 3330 tests; the README's 4-5 min is out of date): the biggest costs were
  module-level world builds repeated on every xdist worker. Done 22 Oct: test_legal_experts, test_state_world and
  test_takeover_index each on one worker (`xdist_group`): 7.5 -> 4.8 CPU-min, 3.5 -> 2.7 min wall for the three. Next: the same
  for any other file whose module fixture costs over ~10 s, then `slow` on the 30-60 s calls (history scorer windows, state
  zero-attention, twenty-laws render, private_positions world).
- **Testing tiers** (Zach, 22 Oct: full suites for every merge are too slow): a merge gate `scripts/test_fast.sh BASE` (goldens,
  prompts, schema, settings, every spec loads, plus the tests importing any module changed since BASE: 3-5 min) gates
  `subsistence`; the full suite (~25 min at -n 3) runs in the background daily or before `main` moves and never blocks; mark the
  slowest tests `slow`. Not built yet. Agents: targeted tests only, unique `--basetemp`.
- **Benchmark scenario design**: Zach's agent elsewhere, from docs/review/35_benchmark_scenarios_brief.md.
- **Decisions waiting for Zach** (from positions): 36 older channels-v2 worlds (ashwood*, millbrook*, survival/*, takeover/*,
  usability/*) warn at load until each declares `channels.square`; the Directorate positions variant runs its middle managers
  under `enforcement: obligation` (or `reminder`), renames J0 "the State" and uses the short duty texts; still outside positions:
  roles (spy, scholar...), Board and Fixer, camp rules naming the class ("open to Workers only").
- **Temperament norms**: `personality.model: hexaco` is built but `norms: published` refuses to draw until the HEXACO-PI-R tables are
  filled in `cybertron/temperament.py` (hexaco.org, PMC, OSF are blocked by both environments' network policy: allow them or paste
  the tables); `norms: uncorrelated` works for the one-dimension pilot.
- **Takeover benchmark follow-ups** (not started):
  - In Thornby, a single councillor can rewrite who writes for the paper.
  - A bench preset with fewer camps, so subsistence stays under 30% of actions.
  - The durability forks and consent interviews that grades G5 and G6 need.
  - Piloting W3 and W5.
  - Amend the calibration order in review 29 §2.7.

## Offered, not started

- **Positions** (docs/review/33_positions.md §5, "As built"): **built on `wp/positions`, not merged** (22 Oct). Opt-in, no engine
  version: positions library and offices that name one, identity and derived leverage in the system prompt, duties as DUE items
  with `duty` records (measured adherence in `cybertron institutions`), enforcement none | reminder | obligation; papers; failed
  banner; unread/new counts; the channel-setup check at spec load; `regimes/directorate_positions.yaml` and
  `regimes/private_positions.yaml` (dry runs only). Goldens and legacy prompts unchanged. Not done: replacing the roles system and
  the Board and Fixer special cases; live runs of the two variants.
- **Generalise the hard-coded institution logic** (audit 21 Oct; searches only). The kernel is fairly clean; the drift is a layer up:
  about 11.4k lines of institution modules and about 25 of the 721 spec keys are institutional policy rather than physics. Fixes, in
  order (each opt-in, old runs unchanged):
  1. A permission query ("what can X do after this law?": run the real checks with a test action before and after) to replace
     `laweffects.control_shadows`, which pattern-matches law code for one trap (before_withdraw that only blocks on an
     office-controlled store).
  2. Office control (`institutions.office_control`) and petitions (`institutions.petition_public_after`, obligations.py) as library
     laws, so later laws override them by precedence.
  3. A holdings-history query laws can call (`held_at(agent, item, "turn")`), so the contract law judges could-not vs would-not
     itself; today Python writes `turn_held` into the law's state (obligations.py ~398, engine 19).
  4. Combat hooks for laws (before an attack, on resolution, who defends whom), so bodyguards, lawful spoils and fed-only
     (`conflict.FORCE_RULES`, also duplicated by `conflict.spoils.*`) become library laws.
  5. Positions (above), absorbing the role-card one-off lines (recall route, oversight, enrol, roster, offers, petitions); then one
     budgeted prompt renderer replacing the per-fix switches (`contracts.brief_lines`, `compact_lines`, `applicant_lines`,
     `context.setup_feed`, ...).
  Also: DM capacity as physics capped by any law, instead of the kernel reading the Communications Act by name (kernel.py ~240,
  ~268) and two `dm_step.capacity` modes (this capped every Directorate DM limit at 1 until switched); the Board and Fixer
  special cases go with Positions.
- **Papers instead of a square** (33 §3): built on `wp/positions` as the regime worlds' preset (`fragments/papers.yaml`), not an
  engine default; every channels-v2 world must now declare its channel setup (a warning; an error under `specs/regimes/`). 36
  existing worlds warn until each declares `channels.square` (a per-scenario decision).
- **Channel fixes** (from the channel-use analysis of the Private and Directorate runs):
  - built on `wp/positions` (opt-in, `fragments/positions.yaml`): failed actions at the top of the next turn
    (`context.failed_banner`); channel duties as DUE (Positions); "X unread, Y new since last round" and record-free headlines
    for pull channels, "N new since last round" for pushed ones (`channels.unread_new`);
  - rename to avoid collisions: the Board contract vs the market board; contract "notices" vs the notices channel.
- **Reproduction back on for future runs** (Zach, 21 Oct): future runs will be longer and larger, with Life and reproduction on.
  Today it is off by design: the Private world has Life on but no births (`ensure_maker: false`, no Makers, no pairs mode; its flows
  are sized for 24), and the Directorate and the takeover bench inherit `life.enabled: false` (a fixed cast). Pairs reproduction
  (cap 3N) is on only in the survival worlds and Ashwood. To do: 40+ round runs; resize the Private world's flows (and the flows
  check) for a growing population; decide what children get (positions, goals, temperaments) and how offices, firms and holdings
  pass to heirs; keep subsistence and lineage from crowding out politics (review 26 finding 4).
  Sequence: first smaller pilot runs within a world to choose which parameters to sweep and their ranges, then the long, large
  runs as sweeps over those parameters.
- **Temperament and values redesign** (discussion 21 Oct; brief for an agent: docs/review/34_temperament.md, with the analysis scripts in docs/review/34_temperament_scripts/; to be built by a local agent on Zach's laptop). Today: 7 independent Beta(2,2) traits (risk, trust, honesty,
  assertiveness, patience, reciprocity, talkativeness), bucketed low/mid/high, the 4 most extreme rendered as fixed sentences
  (personality.py); plus an independent 50% archetype draw (archetypes.py) that can contradict the traits (a "contrarian" who
  "follows others' proposals"). Proposed: three layers sampled jointly. (1) Temperament: HEXACO at facet level (6 factors drawn
  correlated; each facet = loading x factor + unique noise; loadings and intercorrelations from the HEXACO-PI-R norms, Lee and Ashton),
  keeping about 15 game-relevant facets of the 25 (Sincerity, Fairness, Greed Avoidance, Modesty; Fearfulness, Anxiety; Social
  Boldness, Sociability; Forgiveness, Flexibility; Diligence, Prudence; Inquisitiveness, Unconventionality; Altruism) and showing the
  4-5 most extreme as behavioural sentences on a 5-level scale. (2) Strategic preferences (risk, time, trust, reciprocity), partly
  derived from temperament. (3) Values (Schwartz circumplex or Moral Foundations: neighbours correlate, opposites anti-correlate);
  the lever for loyalty and dissent in the regime worlds. Archetypes become named regions of this space, not an overlay.
  Effect-size check on the 36 published runs (790 agents; behaviour z-scored within run x model; Spearman r; a trait not among the 4
  shown is a natural control):
  - talkativeness -> DM length r = +0.69 when shown vs +0.03 when not; DMs per turn +0.22 vs +0.01; reasoning length +0.28 vs +0.01.
    By shown level, DM length roughly doubles low -> high for every model (Haiku 134 -> 272 chars, Sonnet 79 -> 217, Opus 147 -> 347).
  - assertiveness -> proposals +0.24 shown vs -0.10 not; posts and DMs about 0.
  - risk -> attacks +0.28 shown vs -0.10 not (n = 58, weak).
  - trust -> gifts and transfers +0.02 (no effect). Honesty, reciprocity, patience: no behaviour in the logs to test (deception and
    promise-breaking need a text judge, which costs model usage).
  - Archetypes (mean z vs agents with none; n 25-90, so about +-0.2 is noise): secretive posts less (-0.55) and messages less;
    chaotic messages, posts and varies actions more; zealot and loyalist narrow their actions (entropy -0.41); opportunist proposes
    more (+0.46) and gives less; paranoid withdraws; loyalist writes more and longer DMs (+0.41, +0.59). Gossip goes the wrong way
    (-0.22 DMs, -0.43 length): "pass on everything you hear" does not mean talking more.
  Second pass, conditioned behaviour and promises (same 36 runs, data only):
  - Vote promises naming a ballot ("I'll vote yes on B4"), checked against the vote cast: kept 88% (258 promises); no honesty
    effect (shown high 84%, shown low 95%, not shown 88%).
  - Payment promises: a loose pattern finds 1,597 but most are trade terms, offers of information or standing policies, so the
    26% "kept" is meaningless; explicit ones ("I'll send you 5 food", no condition) number only 50, kept 40%, too few to test.
    Honesty needs a text judge (model usage).
  - Gift returned within 3 rounds, by the recipient's shown reciprocity or trust: 23-34% at every level, no effect.
  - Retaliation within 3 rounds after being attacked: 2 of 112 targets, at every reciprocity and risk level (review 26 found no
    retaliation at all): the model's own disposition overrides the "you punish every defection" sentence.
  - Giving first (to someone who had not given to you): 74-78% at every trust level, no effect.
  So communication-style traits move behaviour; strategic and social dispositions (trust, reciprocity, honesty) do not, even
  measured where they should matter. For the redesign this argues for carrying those through values, positions and goals (or
  stronger, concrete framing with examples) rather than one trait sentence each.
  Conclusion: rendered temperament text works when it names a concrete, frequent behaviour (how much and how long you talk, whether
  you propose), and does little when it names a disposition with no obvious action (trust). Write facets as concrete behaviours, and
  test the new model with a small controlled pilot (one seat, varied profiles) before adopting it.
  Built (22 Oct, opt-in `personality.model: hexaco`; review 34 §8): cybertron/temperament.py, the hooks, the export column, the
  `set_temperament` intervention and the pilot (temperament_pilot.yaml, 34_temperament_scripts/pilot.py). Blocked: the published
  norms tables (the build environment could not reach the sources); until they are filled only `norms: uncorrelated` draws.
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

- 2026-10-22:
  - **Batch 2 integrated, engine 22, on `main` and `subsistence` (351b00a; full suite clean)**: State, Cooperative and Merchant worlds; documents; lawyer expert and
    law imports (`use("L12")`, pinned versions, library blocks); old-code cleanup (MIN_ENGINE 13, library edition 2 removed);
    temperament redesign (review 34, opt-in); positions and papers (review 33 §5 "As built": identity and derived leverage in the
    system prompt, duties as DUE with none/reminder/obligation, failed-action banner, unread/new counts, submit/publish/decline,
    a spec-load check that every channels-v2 world declares its channel setup: an error under specs/regimes/ and for positions
    worlds; `directorate_positions.yaml`, `private_positions.yaml`).
  - **Engine 21 made a frozen flip** (`law.similar_check` true -> false): runs of engines 13-20 replay again.
  - **Engine 22** (`contracts.change_rounds` 0 -> 1): a members' ballot on a contract change closed in the round it opened, so under
    simultaneous turns every change to a contract of two or more members failed with no votes (Lawtown; also earlier runs).
  - **Lawtown live run** (`specs/regimes/lawtown.yaml`, 10 agents, 10 rounds; two Opus lawyers with archives and `draft`, Haiku
    clients with legal goals): clients did their own legal work (a company, a supply contract, the Road Fund Act) and declined
    counsel; lawyers mostly harvested, never drafted or read their archives; Marsh found and fixed a 100% transfer-tax bug in the
    Road Fund Act (its on_transfer returned qty). Lesson: legal expertise only pays where the legal surface is complex (an existing
    body of law, disputes in court, amending a complex institution, deals between institutions). Not published.
  - **Engine limits for lawyers** (open): institutions are islands (one institution's laws cannot read or move another's; a contract
    cannot read its members' J0 cases, 07 #6); `draft` fills templates and presets only; office duties were free text (positions
    fixes).
  - **Registry tables**: dir_changed, dir_sealed and dir_policy were never shown to agents (declared rendered in agents.py, no branch);
    fixed with the other bookkeeping gaps of the merged branches.

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
