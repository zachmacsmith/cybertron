# Review 31.14: legal experts (the lawyer's archive and drafting tool)

*20 Oct 2026. Branch `wp/lawyer-expert`. Code: `cybertron/lawguide.py` (new), small hooks in `directories.py`, `action_registry.py`,
`actions.py`, `context.py`, `schema.py`; spec `cybertron/specs/regimes/private_counsel.yaml`; tests `tests/test_legal_experts.py`.
No live run was made.*

## 1. The problem, from the runs

In live runs the legal machinery is used badly or not at all. The cases below come from the runs in `cybertron/out/` (wt-sub) and
the usability and pilot reviews.

| Failure | Where | Count / detail |
|---|---|---|
| Code with no `title`/`intent` | arm_a_* runs: `create_contract` with `"x = 1"`, `"pass"`, `"# no-op"`; `propose` with `def act(): pass` | 9 refusals across 4 runs |
| Prose instead of code | arm_a_sonnet r13 (Ilan: `{"name": "Harvest Levy", "text": "10% of every harvest..."}`), arm_a_haiku seed 2 | 2 |
| Proposing with no jurisdiction (state of nature) | arm_a_* (Ilan, Elin, Nadia, Erik; previews too) | 9 |
| `isinstance` in law code | village7 (ba3da980) L18, L41 | 2 check failures |
| A class where a rank belongs | ashwood3 L5: "law_class must be ordinary, structural or procedural" | 1 |
| Unranked procedure shadowed by a ranked one | Thornby pilot L11 (`laweffects.py` "shadowed changes") | decided nothing |
| A before-hook that only abstains on an office-controlled store | usability round 2 (09 §Laws): the council's amendment "let councillors draw" did nothing | 2 refused withdrawals |
| Amending an office's `holders` moves nobody | Millbrook keeper (`laweffects.py` docstring) | inert |
| Fine on someone holding nothing | millbrook_nogoal L16 ("Agnes held only 0 penny of the 5 fined") | 1 |
| `dict` as a key in contract code | contracts run (2026-10-16T15-34-48) A1 L5: "unhashable type: 'dict'" | runtime error |
| Wrong item on a leg; untagged payments | payroll usability run (timber paid on a penny leg) | rounds 3-5 |
| Voting outside the electorate | millbrook_nogoal (Tamsin, B6, B7) | 2 |
| **No court case ever filed** | every live run in `cybertron/out/` (0 `case_opened` events) | 0 cases |
| **No standing contract founded in play** | every live run: only the `start` block founds presets | 0 |
| Laws usability run: 0 laws proposed | laws/2026-10-16T15-34-48 overview | 0 of 0 |

Two of these are not misunderstandings but missing tools. A standing-contract preset is ~8,300 tokens of code (`standing.CORE`),
so no agent can found one live by pasting it, and no action founds a preset by name. And a code draft passed by message is cut at
400 tokens in the feed (`context.dm_tokens`). So a lawyer also needs a way to hand over long code.

## 2. What existed

- **Counsel** (`cybertron/counsel.py`): `represent` lets counsel act in court for a client under a Retainer
  (PARTIES client/counsel). It is the only part of the lawyer role the engine knows. In `private.yaml`, Marsh holds two
  retainers (A5 from Anselm, A6 from Moss). Nothing teaches Marsh the law.
- **Knowledge sources**:
  - the core prompt's law-language summary (`lawdocs.api_doc`);
  - the manual (titles in the prompt, sections by lookup);
  - codex law articles (`lawdocs.articles`, hidden layer only);
  - `read_law`, `preview_law`, `legal_position`, `read_register`;
  - role cards (`obligations.role_lines`).

  None of them explains procedures and ranks, office control, courts, or the standing-contract parameters together, or gives
  tested worked examples.
- **Libraries**: `scholars.py` (media2) is being frozen, so it was not used. `directories.py` is the general document store:
  owned trees, read/write grants by prefix, readonly prefixes, look-ups `dir_list`/`dir_read`/`dir_search` usable in a turn, in
  the lookup phase and in the DM step. Following the coordinator's note (wp/documents builds on it), the archive is a directory.

## 3. Options considered

| Option | For | Against |
|---|---|---|
| (a) a role-gated reference library, read by an action or lookup with a table of contents | full text on demand; costs tokens only when read | needs a store and a reader |
| (b) documents in the role's system prompt | always in view | ~13.5 k tokens on every call of an Opus seat (cached, but it crowds the turn); cannot grow |
| (c) a compact index in the state, full text on demand | the agent knows what exists every turn; cheap | needs (a) |
| a new `read_guide` lookup | simple | a second document mechanism beside directories |
| **directory (chosen: a+c on directories)** | existing look-ups, grants, readonly prefixes, prompt tree; one mechanism; sharing with clients by `dir_grant` | needed a seed hook and an `all` grant subject |

Documents are **generated from the engine** at install, so they cannot drift:
- the presets come from `standing.PRESETS`;
- the parameter table comes from `standing.BASE` and its source comments;
- the template catalogue comes from `library.ESTABLISHED` and `library.params`;
- the law-function reference comes from `lawdocs.ENTRIES`, limited to what this world documents (`lawdocs.resolve`);
- the rank order and the procedure lookup come from `dispatch.base.RANKS` and `ranks.procedure_candidates`.

The prose (system, offices, hooks, courts, contracts, drafting, pitfalls, practice) is hand-written. The tests check its claims and
enact every code example in it.

## 4. The design

**The archive.** It is a run-scoped directory store with `seed: legal_archive`. Its owner is the expert: `agent:Marsh`
(`class:`/`right:` owners also work).
- `directories.install` fills it from `lawguide.archive_files(k, store, seed)`.
- `guide/`, `ref/` and `public/` are read-only.
- The rest is the lawyer's workspace (`drafts/`, `memos/`).
- `grants: {all: {public/: read}}` gives every agent the public guide. The new grant subject is `all`.

The directory tree in the lawyer's turn prompt is the index (option c). The full text comes with `dir_read`.

**`draft`** (expert only: `needs lawyer:expert`, `when` owner):
- Example: `draft {"template": "Retainer", "parties": {"Orrin": "client", "Marsh": "counsel"}, "terms": {"fee": 1}, "for": "Orrin"}`.
- It instantiates a preset as the start block does (TERMS/ACTIONS/BOND merged, the world's leg mode). It also handles any
  established or toolkit template (`params`, `rank`).
- It writes the draft to `drafts/<name>.py` and grants the client read access.
- It answers with a summary (form, parties/roster, terms, legs, bond, mode) and the exact filing call. The code itself is never
  returned.

**Filing by reference.** `propose`, `amend`, `create_contract`, `propose_contract_change` and `preview_law` accept
`{"draft": "<dir>/<path>"}` in place of `code`, when the agent can read that file (`lawguide.with_draft`). Any directory file
works, so a memo or a hand-written law in `memos/` can be filed the same way.

**Sharing with a client** (the coordinator's question): either the `for` argument of `draft`, or `dir_grant {"dir": "legal",
"agent": "Anselm", "path": "drafts/x.py" | "memos/Anselm/", "access": "read"}`. The client reads with `dir_read` and files with
`{"draft": ...}`. A copy is a `dir_write` into a directory the client owns, where one exists.

**Opt-in.** Everything above exists only where a store is seeded with the archive:
- `draft` is unknown elsewhere (it is hidden in `actions._act`);
- `with_draft` returns the arguments unchanged;
- no new key appears in old directory records.

No default changed, so there is no engine version bump. Old worlds and golden fixtures are byte-identical (the full suite checks
this; §8).

## 5. Archive contents (Private world; tokens = len/4 of the file)

| Path | What | Tokens |
|---|---|---|
| guide/00-index.md | table of contents (generated), how to read and share | ~560 |
| guide/01-system.md | polities, law shape, ranks, classes, procedures and their lookup order, enactment, amend/repeal, preview | ~600 |
| guide/02-offices-rights.md | rights, offices (`offices` constant: holders, controls, powers, duties, succession), reseat, define_action, recall | ~410 |
| guide/03-hooks-precedence.md | old and change hooks, verdicts, conflict rules, the two shadowing traps, limits, law_call_failed | ~460 |
| guide/04-courts-counsel.md | clauses, accuse/respond/rule (remedy)/appeal, court rules, Bench/Recusal, counsel and represent, enforcement here, registers | ~490 |
| guide/05-drafting.md | method plus 4 tested examples: ranked procedure, clause with remedy, explicit allow, reseat with expects | ~610 |
| guide/05b-institution.md | tested guild (offices with treasury control, dues by pull) | ~260 |
| guide/06-standing.md | forms, legs, misses vs breach, every BASE parameter (generated) | ~740 |
| guide/07-contracts-institutions.md | associations, escrow and allowances, founding institutions, manual legs, fulfil and tags | ~470 |
| guide/08-service.md | the practice: what to offer, draft and file, memos and grants, getting paid | ~380 |
| guide/09-pitfalls.md | 14 pitfalls from the runs above, each with its fix | ~490 |
| guide/10-, 11-templates | every established template with params (generated) | ~830, ~80 |
| guide/presets/*.md (9) | one per preset: intent, terms, legs, officer actions, defaults, a draft call, how to file (generated) | 150-330 each, 2,281 |
| ref/*.md (13) | law functions by topic: governance, ballots, ranks, chains, rights, sanctions, meta, courts, court rules, output, contracts | 4,382 |
| public/legal-help.md | who counsel is, code not prose, filing a shared draft, fulfil, courts | ~290 |

The archive has 35 files and about 13.6 k tokens. The largest file is 875 tokens as `dir_read` shows it; the cap is 950, under the
1,000-token lookup budget.

**Prompt cost.**
- The lawyer's directory tree: ~340 tokens a turn.
- Everyone else's public entry: ~50 tokens a turn.
- The `draft` doc line: ~140 tokens, in the lawyer's manual.
- Reading: ~0.5-0.9 k tokens per document read. A lawyer who reads 2-3 documents a round adds ~2 k input tokens a round, about
  50 k over 24 rounds on one Opus seat: under $0.25.

## 6. Tests (`tests/test_legal_experts.py`, 15)

| What is checked | How |
|---|---|
| Every document fits the budget | the test reads each one with `dir_read` and checks it against the budget |
| The index covers the archive | it lists every document; the whole archive stays under 20 k tokens |
| The generated parts match the engine | every preset's legs, every BASE parameter with a comment, every established template, the reference |
| The archive is deterministic | it is generated twice and compared |
| Every code block is a listed example | every ```python block in the archive is one of `lawguide.examples`, and every example is shown |
| Every law example enacts and does what it says | each one is enacted in the Private world after setup with no failed calls and no failed expectations. Checked: the office is reseated, the clause exists, the `statute:ordinary` procedure is set |
| The guild example founds an institution | it creates an institution whose Warden is the founder |
| The allow example opens an office-controlled store | in the usability laws world: blocked by the Granary Ration under any_block (pitfall 7), refused by the office-control gate alone, and opened by the explicit allow |
| The lawyer can read the archive everywhere | as an action, as a lookup and in the DM step (`dm_step_lookup`) |
| Non-lawyers read only `public/` | `guide/` is refused and hidden from their listing, they get no `draft`, and readonly holds |
| Drafts work end to end | a Retainer is drafted for a new client, founded by reference and joined, and counsel then has `represent`; a template law is drafted, previewed and proposed by reference; a roster preset takes the world's manual leg mode |
| Without an archive nothing changes | `draft` is unknown and absent from the error's action list, and no `draft` argument is read |

**Finding (engine, not fixed here).** Proposing or previewing a preset in the 24-agent Private world is very slow.
`preview_law` of a Retainer draft took 627 s under heavy load (`proposal` goes the same way); a small law takes 3.6 s. A profile
puts 600 s of that in `dispatch/changes/legal.py` `similar_laws`. That function runs `difflib.SequenceMatcher(...).ratio()` on the
~33 KB normalised code of every pending or active law of the jurisdiction, and the world has a dozen presets. `create_contract`
does not run the check, which is why founding a preset by reference is fast (2.7 s). The fix (a length and `quick_ratio` pre-filter,
same results) is filed as a separate task, because another work package owns engine fixes. Until it lands, the lawyer should file
bilateral presets with `create_contract`, which is what `draft` recommends, and not preview them.

## 7. Proposed live A/B: private (A) vs private_counsel (B)

- **Arms.** A is `regimes/private.yaml`, B is `regimes/private_counsel.yaml`. The cast, models, seeds and 24 rounds are the same.
  Marsh (Opus) holds the retainers in both arms; only the archive, the public guide and `draft` differ. Run seeds 1 and 2 for each
  arm.
- **Measures.** Per run, from `events.jsonl`:
  - laws proposed, enacted, refused (`proposal_check_failed`) and inert (`law_effect.inert`), and shadowed notes;
  - `law_call_failed`;
  - contracts founded in play (`contract_created` after round 0) and how many are presets;
  - cases filed, ruled and appealed, and `counsel_acted`;
  - drafts written and filed by reference (`dir_write` under `drafts/`, and proposals whose code equals a draft);
  - `dir_read` of `guide/`;
  - new retainers;
  - legal-action error rate (the §1 scan script);
  - whether Marsh's clients used legal machinery more than other agents.
- **Hypothesis.** B shows more valid legal acts per run (proposals enacted and not inert, contracts founded, cases filed), fewer
  legal errors, and a lawyer with paying clients beyond the starting two.
- **Cost.** The run estimate in 10 §9 is ≈ 900-1,400 calls and ≈ $40-45 per run at list prices (3-5 h on `claude_code`). B adds
  under $1 of reading. For 2 seeds × 2 arms that is **≈ $170-180 and 12-20 hours**, or half that with seed 1 only. Fix the `similar_laws` slowness above first.

## 8. Status

The full suite has been run on the branch tip after merging origin/subsistence; its summary line is reported to the coordinator.
No live model call was made.
