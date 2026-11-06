# Branches

On 6 Nov 2026 the repository went from 57 branches to two: **`main`** and **`archive`**. Nothing was lost: every deleted branch's
last commit is in one of them, and any branch can be restored with `git branch <name> <tip>` from the tables below.

- **`main`** holds all finished Cybertron 1 work.
- **`archive`** holds branches that were closed unfinished or moved to Cybertron 2. It has main's files; each closed branch is
  merged into it with `-s ours` (its commits are kept, its changes are not), and the merge message says what the branch was and
  why it was closed: `git log --first-parent archive`.
- Cybertron 2 moved to https://github.com/zachmacsmith/Cybertron2 with its full history and the same commit ids.

## Folded into main on 6 Nov (the Cybertron 1 work since 22 Oct)

| Branch | Tip | Last commit |
|---|---|---|
| `bench/first-batch` | `3f20912fad` | 2026-11-01 bench36 publish.sh: always write the run-page viewer files (the site needs them until it reads the  |
| `design/benchmark-scenarios` | `133a0673a3` | 2026-10-22 Review 36b: three tiers (L18 on cheap short runs with all factors and all three aspirant models; mo |
| `wp/ic-horizon` | `86712e38cd` | 2026-11-04 Aim-change wave 2: a scripted Assessor (no model calls in any phase) and the 15-food fee capped at  |
| `wp/lead` | `164b27cec8` | 2026-11-05 writeup: anecdotes by pattern, with full quotes |

## Archived (see `git log --first-parent archive` for each reason)

| Branch | Tip | Last commit |
|---|---|---|
| `build/buildings-02zh` | `23ce8c54ba` | 2026-11-01 Building package (02zh) 3: the build verb's arguments; build note 38.45; OPEN Q-24 for 37.2 (readin |
| `build/generator-37.2` | `25728e420a` | 2026-11-01 Landscape generator, stage 1 (cybertron2/landgen, built by 37.2 at Zach's request): macro primitive |
| `coord` | `8aaede867b` | 2026-11-04 board: 37.4 to c2viz on run-written visual records |
| `econ/37.2-thicker-economy` | `12da73e073` | 2026-10-22 37.2k: fuse events (time to respond) and gates (entry rules); open proposals on attacks and stone |
| `wp/cybertron2` | `ddd84a42a9` | 2026-11-05 lodging.md: the host's feed option as built; livestock.md: fences decided (D2-130), numbers to cali |
| `wp/demography` | `8185fe74f8` | 2026-10-23 37.1 devlog: paused; moved to the cybertron2 run record |
| `wp/environment` | `0d52782b75` | 2026-10-22 37.4 log: design decisions (scales, signs, external vs internal, space approved) |
| `wp/inst-cross` | `779ab564f0` | 2026-10-22 37.3: reads as monitor-only cross_read records; devlog |
| `wp/obligations` | `05aed0a73c` | 2026-10-19 WIP: obligations (uncommitted edits left when the build agent stopped; unreviewed) |

## Already merged into main before the tidy-up, deleted

| Branch | Tip | Last commit |
|---|---|---|
| `claude/charming-wozniak-4iqwdk` | `7cf91231b6` | 2026-10-22 Review 34: temperament and values (personality.model hexaco, opt-in) |
| `claude/zen-fermat-pwepak` | `3570b95737` | 2026-10-20 Report: working/notes.md shows each round's scratchpad again |
| `doc/26-run-comparison` | `0dd786b7e6` | 2026-10-15 review 26: name which runs the per-agent-round law ratio covers |
| `doc/27-systems-inventory` | `4ac7220a2f` | 2026-10-15 docs(review): 27 systems inventory and established starting worlds |
| `doc/28-scenario-suite` | `68f4303ce8` | 2026-10-15 Review 28: scenario suite of established societies, testbeds, convergence metric |
| `doc/29-takeover-bench` | `51e5949cfa` | 2026-10-15 Review 29: takeover benchmark design (worlds, seat designs, autocracy index, private interviews) |
| `doc/30-world-benchmarks` | `c7cd4523aa` | 2026-10-15 docs: review 30, world benchmarks beyond the 1984 bench |
| `integrate/batch2` | `09ba13a791` | 2026-10-22 Tests: the three slowest setup files each on one xdist worker (their world is built once, not once  |
| `subsistence` | `09ba13a791` | 2026-10-22 Tests: the three slowest setup files each on one xdist worker (their world is built once, not once  |
| `trial/publish-complete` | `a9d5191c5a` | 2026-10-20 Merge wp/publish-complete (trial): fetch/continue published runs, calls_seen (export 2.7), releases |
| `wp/channel-purposes` | `7a53ccc3b3` | 2026-10-15 prompts: starvation reads as starvation (never "killed by an unknown hand"); food and hunger head t |
| `wp/channels-delivery` | `e0829f207a` | 2026-10-16 Channels: declare channel_resealed and channel_read on set_channel and read (action registry emits) |
| `wp/coop-world` | `f3f04123b3` | 2026-10-22 Merge remote-tracking branch 'origin/subsistence' into wp/coop-world |
| `wp/courts-records` | `2d480fc3e6` | 2026-10-20 Courts and records (review 31 build plan 0.11, 1.7, 1.8, 2.2, 2.8), all opt-in |
| `wp/dataset-naming` | `49a788edfd` | 2026-10-20 Dataset id in one place; repack a published raw archive |
| `wp/documents` | `44115206d1` | 2026-10-22 Documents: merge subsistence; keep golden fixtures unchanged (documents.DEFAULTS not yet frozen, ex |
| `wp/econ-plumbing` | `0310200c30` | 2026-10-16 tests: re-record golden instance hashes (contracts.DEFAULTS gains pay_institutions and applicant_li |
| `wp/engine-bugs` | `3b2ba4f7da` | 2026-10-20 Engine 20: resource_of is documented only where contracts and subsistence are both on (lawdocs.REQU |
| `wp/established-worlds` | `68ff97eb71` | 2026-10-15 Merge origin/subsistence (reviews 29, 30) into wp/established-worlds |
| `wp/farming` | `31d1ac0c61` | 2026-10-16 Engine 14: keep earlier prompts under the shared hunt; register the farm bot's stream |
| `wp/force` | `03d59a9559` | 2026-10-20 Force chain (review 31.06; 08 §5 items 1.9, 2.5-2.7): bodyguards, arrest, lawful spoils, hunger par |
| `wp/inst-metrics` | `41da74df57` | 2026-10-20 Institution metrics (review 31 item 1.11): market, money, food, channels, inert laws, role adherenc |
| `wp/interview` | `355cd7114b` | 2026-10-15 Interview module: ask agents in character at a round with their exact context |
| `wp/law-imports` | `0bb9d3ed38` | 2026-10-22 law imports: merge engine 21 (no duplicate-law check); draft previews presets again; archive docume |
| `wp/laws-loud` | `7a4d5dcaf9` | 2026-10-16 tests: re-record the golden fingerprints for laws that work or fail loudly (new EXTRA keys in insta |
| `wp/lawyer-expert` | `497d610c8a` | 2026-10-22 lawyer: merge subsistence; consistency test hides draft; positions note |
| `wp/merchant-world` | `82d5c9fd0a` | 2026-10-22 Merge subsistence (engines 19-20): agent terms on one mechanism (AGENT_TERMS: assign sets, enrol ac |
| `wp/obligations2` | `ef48ff92fa` | 2026-10-20 Review 31.09: usability round 2 (manual obligations, role cards, decision seats in Opus): findings  |
| `wp/old-code-cleanup` | `c2869e8ee1` | 2026-10-22 Merge remote-tracking branch 'origin/subsistence' into wp/old-code-cleanup |
| `wp/positions` | `634db57637` | 2026-10-22 Positions: As built (review 33 §5) and the threads status |
| `wp/private-final` | `dfa3d58072` | 2026-10-20 golden: instance.json hashes only (two new default settings, contracts.brief_lines and context.setu |
| `wp/private-world` | `08725d4311` | 2026-10-20 Private world (review 31.10; 08 §5 item 1.12): spec, flows check, scripted dry-run tuning |
| `wp/publish-complete` | `3f2495aaf3` | 2026-10-15 Continue published runs; calls_seen replaces viewer.json; releases name their code |
| `wp/publish-privacy` | `c522565254` | 2026-10-20 publish: privacy gate that refuses to push private strings, secrets or local paths |
| `wp/shadowed-effects` | `cb24d6583f` | 2026-10-20 law_effect reports shadowed changes (Thornby L11: unranked set_procedure under rank-specific proced |
| `wp/similar-flag` | `608081943c` | 2026-10-22 Engine 21 as a default flip: law.similar_check (true -> false), so runs of engines 13-20 replay aga |
| `wp/site-archive` | `dece01d21f` | 2026-11-01 Archive the old broadsheet site; site/ is the pixel-art site |
| `wp/site-cybertron1` | `687ae3cb57` | 2026-11-01 Site: pin to dataset release v0.17.2 (every run has its run-page files) |
| `wp/site-v2` | `8e1b37de72` | 2026-10-24 Site v2: the night-village redesign |
| `wp/state-world` | `844540e87d` | 2026-10-22 After the merge: courts-records test expects wiretap and dir_history hidden in existing worlds; wri |
| `wp/takeover-index` | `07363f3395` | 2026-10-20 takeover index: build the autocracy_full calibration regime without a rights subscript write (right |
| `wp/takeover-worlds` | `7cbf4a6ec1` | 2026-10-20 Review 29b: the W7 Aster pilot, interviews in both worlds, P1 gates, test summary |
| `wp/usability-fixes` | `a2796cdc5c` | 2026-10-20 Merge origin/subsistence (shadowed effects): one mechanism for the office-control case; agents admi |
