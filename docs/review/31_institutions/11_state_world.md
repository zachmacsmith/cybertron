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
- `tests/test_state_world.py` — 14 tests: every new mechanism, the spec, the zero-attention gate, the role cards, the gates.

SUMMARY_PLACEHOLDER

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

RESULTS_PLACEHOLDER

