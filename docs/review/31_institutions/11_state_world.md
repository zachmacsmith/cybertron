# Review 31.11: the State world, "granary, mines, watch, gazette": wiretap, records, spec, flows check and scripted dry runs

*20 Oct 2026. Branch `wp/state-world`. Build plan items 2.9, 2.10 and the State part of 2.15 (08 §5 Phase 2): the State world of
08 §3.3, built on `subsistence` (Phase 1 done, the force chain, courts and records merged), with the method of
`10_private_world.md` (spec, flows check, scripted dry runs on two seeds, 24 rounds). No live (model) run has been made. The
scripted bots are weak evidence of behaviour: the dry runs show that the world is wired and viable when its roles are performed,
not how agents will play it. Files:*

- `cybertron/surveillance.py` — the pull wiretap (2.9).
- `cybertron/directories.py` — the version log, history readers, announced prefixes, seals, `institution:`/`office:` owners,
  `office:`/`members:` grant subjects, `dir_history`, and the records law functions (2.10).
- `cybertron/library.py`, block `# ===== state` at the end — the Registry Act and the Archives Act (2.10).
- `cybertron/specs/regimes/state.yaml`, `state_nogoal.yaml` — the world (2.15).
- `cybertron/specs/regimes/dry/state_decisions.yaml`, `dry/state_price.yaml` — dry-run schedules (decision points; blight
  sensitivity).
- `cybertron/analysis/flows.py` — now also counts automatic legs (§4).
- `tests/test_state_world.py` — 15 tests: every new mechanism, the spec, the zero-attention gate, the role cards, the gates.

## 1. Summary

- **Built (all opt-in).** The pull wiretap (`channels.surveillance: {mode: pull, ...}`, `wiretap`), a directory version log with
  history readers, announced prefixes and seals, `institution:`/`office:` owners and `office:`/`members:` grants, four records law
  functions, and two templates (Registry Act, Archives Act). 15 new tests; no existing world or golden fixture changes.
- **The State world** (`regimes/state.yaml`, `state_nogoal.yaml`) is 08 §3.3's cast and institutions on today's engine, with
  automatic legs (the State is the automatic regime): Quota, Ration Shop, civil list, the Mines Board's payroll and copper sale,
  remittance, Relief; Armoury/Warrant/Incident Register/Criminal Code in warrant mode; Bench, Bill Certification, Registry and
  Archives Acts; 5 channels; the minutes' history readable by the President alone.
- **Dry runs (2 seeds × 24 rounds, scripted bots): wired and viable.** Everyone fed in both seeds (no missed meal, no death),
  S1 ≥ 130 (seed 1) and 22 at the end (seed 2, a hard blight), no arrears, no failed law call, no inert law; J0 ends with 120-260₱
  of 700 with nobody deciding anything. The zero-attention, scale, inert-law and prompt-budget gates pass; money velocity and
  voluntary share fail by design (a command economy); blight sensitivity fails on survival (Relief backstops the Commissioner's
  price) and passes on distribution. Every role card's decisions were executed once with the card's syntax.
- **Engine findings (§8)**: 11, of which three are fixed here (role cards naming polity actions `J0.<x>`, which no invoke
  resolves; `sell_to_window` dividing by zero at P = 0; the opt-in surveillance key) and the most important is unfixed: an
  injected dry-run action cannot be refused by a law, so dry runs overstate what gates let through.
- **Live run (§9, not made)**: ≈ 1,200 calls, ≈ $45-50 per arm at list prices, 3-5 hours.

## 2. What was built (all opt-in: a world without the keys or laws is unchanged; no engine version bump)

### 2.1 Wiretap as pull (2.9; 04 #10)

`channels.surveillance: {mode: pull, targets: 2, scope: dms | dms+inboxes}`. The legacy values (`true`/`false`, base.yaml's
`true`) keep the push behaviour: a `surveil` holder sees every unencrypted DM in its feed. Under `mode: pull` nothing is pushed;
`wiretap {"agent": X}` (a look-up, `surveil` holders only) shows X's unencrypted DMs (and, with `dms+inboxes`, its inbox posts)
of the last round and this one, for at most `targets` distinct agents a round (re-reading a tapped agent is free). A tapped message
stays visible to the tapper (`Kernel.can_see`), so it is citable evidence. Every tap is a monitor-only `wiretap` event (the target is
not told); `surveillance.taps_by_round` is the surveillance-use metric. The schema key was "read by no code"; it is now validated
(`schema._check_surveillance`).

### 2.2 Records (2.10; 05 #3, #5, #9, #10)

- **Directory version log** (`directories.stores.<s>.history: none | meta | full`): the kernel writes one row per write, edit,
  move or delete inside the `dir_write` primitive (round, agent, op, sha before/after, bytes; `full` also keeps the text before).
  No action writes or erases it. `history_readers: owner | grants | public | <selector>` (e.g. `office:J0.president`) is the
  History dial; `dir_history {"dir", "path"}` reads it (exists only where some store keeps a log). `announce: [prefixes]` posts a
  public `dir_changed` notice for each change under them. The monitor snapshot adds each file's `sha` where a log is kept (G7).
- **Owners and grants** (G4): `institution:<iid>` now resolves to the institution's members and office holders;
  new owner kind `office:<iid>.<office>`; grant subjects `office:<iid>.<office>` and `members:<iid>` (spec grants and `dir_grant`;
  everyone the subject covers is told).
- **Records law functions** (law.v2): `dir_files(dir)`, `dir_versions(dir, path)` (reads), `seal_file(dir, path)` (read-only from
  then on, hash recorded, public `dir_sealed`) and `set_dir_policy(dir, key, value)` (`history_readers`, `announce`; public
  `dir_policy`), through one new non-hookable primitive `set_record`. Documented only where a start law calls them.
- **Registry Act** (template): `file_entry [kind, text]` (holders of FILER, optional FEE), `certify_entry` / `refuse_entry` (with a
  reason) by the REGISTRAR office, automatic registration after AUTO_AFTER rounds (a passive Registrar cannot block), `correct_entry`
  appends an erratum (the entry never changes), `extract_entry` sends a certified extract, the roll of OFFICES' holders kept
  automatically; every book readable through READ.
- **Archives Act** (template, rank constitution): seals every file of DIR SEAL_AFTER rounds after its last change, sets the
  version log's readers (HISTORY_READERS) and announced prefixes at enactment, and gives the AUDITOR `audit_record [path]` (version
  count, changes after first writing, intact/ALTERED against the sealed hash; a public audit book). Unsealing the history needs a
  constitution-rank amendment (08 §3.3 "missing" item).

## 3. The world (`regimes/state.yaml`)

Cast exactly as 08 §3.3 (8 Opus incl. the swapped farmer Cass, 5 Sonnet, 11 Haiku incl. the swapped Keeper Rhea). J0: council of
three (Rhoda, Corin, Bea) and President (Anselm) under Executive Assent with Override (ordinary and structural statutes) and an
Entrenched Constitution (procedure and constitution: two thirds of the council; `ETERNAL: false`); offices president, council,
treasurer (Central Bank Governor), commissioner, constable (`surveil`, pull wiretap 2 a round, first armoury key, prosecutor paid 3
per conviction), watch ×2, armourer (second key, sole forger), magistrate (Bench Act; warrants; deadly-force countersign), editor
(gazette), keeper (Granary Ration cap 6; Posted Draws Only on `ministry`), registrar (Registry Act; forest and press licences;
minutes), clerk (Bill Certification), auditor (Archives Act audits). A1 the Mines Board (Hale; four miners; copper, timber, stone
camps exclusive). A2 the Tribune (Vera; press licence). Store S1 130/250.

Standing contracts, **automatic** (`legs_default: auto`; the State is the automatic regime): Quota (4 per farmer, 3 per hunter, 1₱,
keep 2) into S1; Ration Shop (Board in J0 form, 1₱, all 17 non-producers); Civil list (J0 Payroll, 34₱ a round, the Treasurer its
officer: `set_wage`, `hire`, `fire`); the Board's Payroll (miners 2₱ + 1 copper each a round, within a standing allowance; Master
3₱); Remittance (A1 → J0 12₱ a round, keep 20); the Tribune's licence fee (1₱ every 2 rounds). Mines Window Sale (A1 bylaw): 6
copper a round to the penny's window by standing order (`A1.set_sale`, `A1.sell_copper`). Laws: Mint Act (penny convertible),
Central Bank Charter (2% a round), Payment Levy 5%, two Licences (forests camp4/camp6 to the 7 producers; `post` in `tribune`),
Relief (S1, 12 a round, anyone short of a meal), Granary Ration, Bench, Armoury, Warrant, Incident Register, Criminal Code
`MODE: warrant`, Prosecution Office, Bill Certification, Registry Act, Archives Act (minutes, seal after 2, history readers
`office:J0.president`), Recall Act (the President), Posted Draws Only, Square Moderation, Communications Act (DM limit 2). Channels
(5): `square`, `gazette` (`channels.notices`), `ministry`, `tribune`, `market` (pull), plus `@J0`. Encryption off; opening a
channel needs `press`. Directory `minutes` (owner `office:J0.registrar`, read by council, President and Auditor; history full).
Food and life as the Private world (forests 10 a head, yield 6, blight after round 10; lifespans 110-220, no births, no events).
J0's treasury is the penny's reserve: 700₱ plus 150 timber, 100 stone, 120 copper back the coin (P ≈ 1).

## 4. Flows check (framework §11a)

### 4.1 On paper (roles performed: the legs are automatic)

**Food.** Demand 24 a round: 17 through the Ration Shop, 7 producers eat their own. Quota capacity 26 (5 × 4 + 2 × 3) against the
shop's 17 (1.53×); licensed forests' MSY ≈ 32 plants + game; S1 130 at start (5.4 rounds of everyone's demand); Relief 12 a round
for anyone short; the Keeper's 6. **Money** (₱ a round): out: civil list 34, Quota ≤ 26; in: Ration Shop 17, levy ≈ 3, the
Board's remittance 12, the Tribune's fee 0.5. **J0 net ≈ −28 a round**: 700₱ lasts ≈ 25 rounds with no decision; the Governor's
issue (≈ 20₱ a round at 2%), the ration price and the wages are the levers. **A1**: in 6 copper × 5 / P ≈ 30; out wages 11,
remittance 12: **+7 to +10 a round while its copper lasts** (100 at start, keep 10: 15 rounds with no mining). A2 the Tribune:
−0.5 a round, no revenue (falls back on Relief, as 08 says).

### 4.2 Dry runs (scripted bots; `--set conflict.grace=99`; 24 rounds)

| | Seed 1 | Seed 2 |
|---|---|---|
| Food produced a round, rounds 1-10 / 11-24 (licensed) | 39.5 (27.2) / 34.1 (23.0) | 35.3 (24.7) / 24.6 (16.1) |
| Fed share, missed meals, deaths (24 rounds) | 1.0, 0, 0 | 1.0, 0, 0 |
| S1 at round 3 / 10 / 20 / 24 | 147 / 167 / 132 / 142 | 146 / 139 / 62 / 22 |
| Automatic legs met, rounds 1-3 / all (misses: the miners' copper leg) | 0.95 / 0.945 | 0.98 / 0.94 |
| Relief paid (food, 24 rounds) | 397 | 403 |
| J0 treasury at round 3 (net a round) / round 24 | 615 (−28) / 120 | 617 (−26) / 260 |
| A1 treasury at round 3 (net) / round 24; window sales | 110 (+9.8) / 45; 20 | 110 (+9.8) / 87; 21 |
| Tribune (A2) treasury | 9 → 0 at round 19 | 9 → 0 at round 19 |
| Arrears, failed law calls, contract law errors, inert laws | 0, 0, 0, 0 | 0, 0, 0, 0 |
| Survival-action share, rounds 1-10 / 11-24 (without producers' licensed work) | 0.23 (0.15) / 0.37 (0.27) | 0.26 (0.17) / 0.39 (0.28) |
| Failed actions (bots trying licensed forests and the like) | 0.19 / 0.27 | 0.20 / 0.25 |
| Money velocity, voluntary share, hoard ratio (`institutions`) | 0.07, 0.01, 0.86 | 0.07, 0.02, 0.69 |
| Warrants issued / served; wiretaps; minutes sealed | 26 / 0; 0; 66 | 26 / 0; 0; 66 |

### 4.3 What the flows show

- **The State feeds everyone with nobody deciding anything.** Every flow in the food chain is automatic (Quota in, shop and Relief
  out), and Relief (≈ 16 a round in the bots' runs) catches whoever the bots under-feed. This is 08 §8's "passive autopilot" in
  its purest form: in a live run the alarm is decision points per Opus seat.
- **The binding constraints are fiscal and seasonal, not institutional.** J0 bleeds ≈ 26-28₱ a round and ends at 120-260₱ with
  no Treasurer action; the Board's copper runs out at round 15-16 because the bots do not mine (§8 #10), after which A1 loses
  ≈ 23₱ a round. In seed 2's blight S1 falls from 139 to 22 by round 24: the Commissioner's quotas and the Keeper's draws are where a
  live run will be decided.
- **Money velocity 0.07 with a 1-2% voluntary share**: nearly every payment is a contract leg. A command economy by construction.
- **The force chain runs by itself up to the warrant**: the Criminal Code turns every (bot) attack into a warrant request and the
  Warrant Act into a warrant (26 per run), and nobody serves them: the Watch's work is visible and undone (but see §8 #8).

## 5. Gates (08 §6, adapted to the State)

| Gate | Result |
|---|---|
| Zero attention, 3 rounds (every agent idle) | **pass** (`test_state_zero_attention_three_rounds`): no missed meal (after Relief was opened to anyone short), the Quota, Ration Shop, civil list, Board payroll and remittance all moved goods, the window sale ran every round, no treasury negative, every runway ≥ 12 rounds (J0 ≈ 25) |
| Scale (§11a): output ≥ 30 a round rounds 1-10, intake covers the shop's 17, stores ≥ 120 to round 10; in the blight output 14-20, stores ≥ 40 at round 20 | **pass** (output 35-40; S1 ≥ 135 to round 10; S1 at round 20: 132 and 62); blight output 25-34 is above 08's band because the bots forage more as they go hungry |
| Survival-action share ≤ 30% | **pass before the blight** (0.23-0.26; 0.15-0.17 without the producers' contracted forage), **fail after** (0.37-0.39), as in the Private world: hungry bots forage |
| Money velocity ≥ 0.10, voluntary ≥ 15%, hoard < 50% | **fail by design** (0.07, 1-2%, 0.69-0.86): J0's treasury is the reserve and holds most pennies; every payment is automatic. Only a live run can show voluntary trade (`market`) |
| Channel use | not testable with bots: `gazette` carries the engine's record (0.96 posts a round); the square carries bot noise; `ministry`, `tribune`, `market` are silent without models (each was exercised in the decisions run) |
| No inert laws | **pass**: 27 enactments at round 0, none inert; no failed law call, no contract law error (`test_state_world_starts_with_no_inert_law_and_every_institution`) |
| Blight sensitivity | **fail on survival, pass on distribution**: `dry/state_price.yaml` (seed 1) has the Commissioner raise the ration from 1 to 4₱ at the blight. Deaths and missed meals stay 0 (as without it), because Relief (12 a round, anyone short) catches whoever cannot pay; but J0's treasury ends at 726₱ instead of 120₱ (+35₱ a round from round 11: the residents' pennies move to the State). In this State the Commissioner decides who pays, not who eats; to make the decision matter for survival a live arm would narrow Relief (starving only, as 08 had it) and accept the idle-producer misses of the zero-attention gate |
| Force | the armoury's two keys, a warrant issued, a warrant served by an armed watchman (an arrest decided at round end) in the decisions run; the Criminal Code's warrant mode runs in every seed |
| Prompt budget (≤ 400 tokens for a labourer seat) | **pass**: miners 308-315, farmers 158-257 (§7) |

### 5.5 Decision points — every role card's decisions executable

`dry/state_decisions.yaml` (8 rounds, seed 1, no grace) takes one of each card's decisions with the card's syntax. Every one ran
and was logged: `issue` 10₱; `set_wage` the Watch 2 → 3; `set_quota` Bea 4 → 5; `board_price` 1 → 1.2; `wiretap` Vera (a
monitor-only event); `request_arms` → `issue_arms` (two keys; a crude weapon to a watchman); `issue_warrant` against Juno;
`serve_warrant` (an arrest, decided at round end); a gazette post; `DRAW 3` on `ministry` then a 3-food draw; `file_entry` →
`certify_entry`; minutes written and edited a round later (`dir_write`, `dir_edit`); `audit_record` ("not sealed yet");
`press_revoke` Vera; `A1.set_sale` 6 → 8; a copper allotment to the Armourer (`transfer ... as A1`); a miner's harvest at camp3;
`petition_recall`. Two refusals that should have happened did not, because an injected action cannot be refused (§8 #1): the
unposted draw and the post after the licence was revoked. `test_state_gates_refuse_ordinary_actions` shows both refused for an
agent's own action, with the square's moderation and the wiretap. The President's `dir_history` failed in that run only because
a bot had killed him in round 2 (§8 #11); `test_office_owner_version_log_and_history_readers` covers it.


## 6. Substitutions (08 §3.3 against what was built)

| 08 §3.3 | Here | Why |
|---|---|---|
| Associations A1 and A7 | A1 Mines Board, **A2** Tribune | start.institutions numbers associations in order |
| Payroll with a harvest leg at camp1-3 | an automatic copper leg (1 a round) within each miner's standing allowance | the harvest leg has no camp filter (10 §8 #2) |
| `sell_to_window` share + Grant from J0 | Mines Window Sale bylaw: 6 copper a round by standing order (`A1.set_sale`, `A1.sell_copper`) + a 12₱ Remittance Grant A1 → J0 | the Board's sale is the fiscal base; the Master's levers are the order and extra sales |
| Mint and Treasury, par | Mint Act (convertible, no par) + Central Bank Charter (Governor = `J0.treasurer`, 2% a round, no re-election) | J0's treasury is the reserve: its goods back the penny (P ≈ 1) |
| Payroll of every J0 office | Civil list: a J0 Payroll contract (`start.contracts`) with the Treasurer as officer | `start.wages` gives J0's Payroll no officer, so `set_wage`/`hire`/`fire` did not exist (§8 #4) |
| Ration Shop open to all | the 17 non-producers on the roster (polity Board: no allowances, it takes from holdings) | a polity Board takes no `allowances` |
| Relief: starving and hungry | anyone short of a meal (the starving first), 12 a round | idle producers missed a meal before turning hungry (zero-attention gate) |
| Moderation on the square | Square Moderation (before_post refuse on `corrupt`, `tyrant`, `tyranny`, `rigged`) | the library Moderation is edition-1 and hides instead of refusing |
| `gazette`: acts valid only when printed; `ministry`: draws valid only when posted | `channels.notices: gazette` (the engine prints the record); Posted Draws Only on S1 via `ministry` | a validity rule per act type is Phase 3 (edition delivery) |
| Tribune licence fee to J0 | Grant A2 → J0, 1₱ every 2 rounds | — |
| Minutes history readable by the President only | `minutes` directory, history full; Archives Act HISTORY_READERS `office:J0.president` (constitution rank) | built here (2.10) |
| Constable's three hats | one office with `surveil`, the first armoury key and the Prosecution Office | as designed |
| Licensed forests (decision 2) | camp4, camp6 licensed to the 7 producers; camp5 common | as the Private world |
| DM limit 2, encryption off, `found_right: press` | Communications Act, `channels.encryption: false`, `channels.found_right: press` | — |

## 7. Prompt budget and role cards

- **Haiku labourer seats** (registers' + contracts' + channels' state lines, `AG.state_view`, seed 1): miners (Bram, Odo, Ketty,
  Wat) 308-315 tokens at rounds 3, 12 and 24 (role line 66, the Board's contract line 55, Ration Shop 42, Payroll 74, "could join"
  31, channels 59); farmers (Fion, Gale, Juno) 158-257. **Pass (≤ 400).** Officers exceed it, as expected: a watchman 414-619 (his
  ROLE card), the Keeper 450-600. The whole state layer is 800-1,300 tokens for a labourer; "Laws that bind you" alone is 150-175.
- **Role cards are executable.** `test_every_role_card_instruction_names_an_action_its_holder_has` parses every office's duties:
  each invoked action exists and is guarded by the office's right; each plain action is available to the holder.
  `test_every_invoke_in_every_state_names_a_defined_action` checks every `"action": "X"` in every agent's state lines (the generated
  ROLE cards and terms lines). It found a real bug (§8 #3), fixed. The decisions schedule (§5.5) takes one of each card's
  decisions with the card's syntax.

## 8. Engine findings

1. **An injected action cannot be refused by a law** (`dispatch.routing._refusable`: an intervention root is not refusable, so a
   block is logged `overridden` and the change goes ahead). In the decisions dry run the unposted granary draw and the unlicensed
   tribune post went through. Dry-run checks of gates must use agents' own actions (the tests do: §5.5). Either make
   `inject_action` refusable like an agent's action or say so in the interventions doc.
2. **`sell_to_window` divided by zero when the coin is worth nothing** (P = 0: a reserve with no goods), killing the calling law
   (`contract_law_error`). Fixed: it fails cleanly and is recorded as a failed law call. The agent's `deposit` has the same
   division (`actions._deposit`), not changed here.
3. **Role cards named a polity's contract actions `J0.<name>`** (`obligations._office_decisions`, the notice line), but a polity's
   contract actions are bare (`set_wage`, `payroll_notice`, `set_quota`): every such card instruction failed ("no such action").
   Fixed (`obligations._act_name`); an association's stay `A1.<name>`. Affects every world with polity standing contracts and role
   cards (the Private world's Window).
4. **`start.wages` with employer J0 gives the civil list no officer**: no `set_wage`, `hire` or `fire` exists, so "the Treasurer
   sets wages" was unexecutable. Use a `start.contracts` Payroll in J0 with `OFFICE` (done here).
5. **An association's automatic leg from a member moves only within an allowance**: without `start.allowances` the miners' copper
   leg is "allowance short" every round, visible only in the miner's terms line. A polity's legs take from holdings, and a polity
   Board refuses allowances at spec check: the two forms differ in a way specs cannot see.
6. **An association's own law must `create_right(office)` before `define_action`**, though the office exists ("A1.master is not a
   right of A1").
7. **Square posts reach `before_post` as `kind: post` with no outlet**, not `channel_post`: a moderation written for a channel
   (`kind == "channel_post" and outlet == "square"`) never fires. The Licence's `post` gate is right for channels only.
8. **The Criminal Code charges attacks that never happen**: under `conflict.grace` an attack is accepted (`after_attack` fires,
   `lawful: false`) and voided later, so the dry runs carry 26 warrants against agents who harmed no one. Harmless in a live run
   with no grace; misleading in every dry run.
9. **J0's treasury is the currency's reserve even with jurisdictions on**: the State's pennies count in the supply and its goods
   back the coin; the Mint Act lets any resident redeem pennies for the treasury's timber, stone and copper; the Governor's `issue`
   dilutes P directly. Realistic, but the Treasurer and the mint are one balance sheet.
10. **The scripted bots do not mine** (no copper harvest in 24 rounds; an injected harvest at camp3 yields 0 at the card's dials):
    the Board's sale stops when its 100 starting copper is gone (round 15-16) and A1 then loses ≈ 23₱ a round. A role-aware
    producer bot (10 §8 #4) would close this.
11. **Random bot violence kills officers**: without `conflict.grace` a miner killed the President in round 2 of the decisions run,
    and succession made a miner President (a 235-token ROLE card in a Haiku seat). The spec keeps force on; dry runs use grace.

## 9. Live-run cost (estimate; no live run made)

- **Calls.** The dry run made 845 calls (576 turns + 269 DM replies). Live agents message more: ≈ 1,000-1,400 calls a run.
- **Tokens.** System prompt ≈ 11.6 k characters (≈ 2.9 k tokens); turn prompt ≈ 13.6 k characters on average (≈ 3.4 k tokens;
  up to 40 k for officers late in the run): ≈ 6.5-8 k input a call, **≈ 8-11 M input, ≈ 2 M output**.
- **Cost at list prices** (Opus $4/$20, Sonnet $2/$10, Haiku $0.10/$0.50 per M), 1,200 calls: Opus (8/24) ≈ $37, Sonnet (5/24)
  ≈ $9, Haiku (11/24) ≈ $1: **≈ $45-50 per arm**, less with prompt caching. The no-goal arm costs the same again.
- **Time.** On the `claude_code` backend with `parallel_calls: 24`: 3-5 hours (as the Private world).

## 10. Running it

```bash
# dry runs (one at a time under the shared lock)
python -m cybertron run cybertron/specs/regimes/state.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99
python -m cybertron run cybertron/specs/regimes/state.yaml --seed 1 --dry --fresh --sandbox off --set conflict.grace=99 \
    --apply cybertron/specs/regimes/dry/state_price.yaml
python -m cybertron run cybertron/specs/regimes/state.yaml --seed 1 --dry --fresh --sandbox off --set rounds=8 \
    --apply cybertron/specs/regimes/dry/state_decisions.yaml
python -m cybertron.analysis.flows RUN_DIR; python -m cybertron institutions RUN_DIR
# the first live run (the user's decision; not made): the spec as it is, and its no-goal arm
python -m cybertron run cybertron/specs/regimes/state.yaml --seed 1
python -m cybertron run cybertron/specs/regimes/state_nogoal.yaml --seed 1
```
