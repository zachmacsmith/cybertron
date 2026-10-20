# Review 32: Documents: literacy, shared documents, copies and confined access

*20 Oct 2026, branch `wp/documents` from `origin/subsistence` (`c6f6c0b`). This is a design, with a small opt-in prototype of its core
(`cybertron/documents.py`, `tests/test_documents.py`). No live run was made. Engine references are `file:function` on this branch.
It builds on, and must merge with, `wp/state-world` (`d290d5f`, review 31.05 #3-5: the directory version log, seals, `institution:` /
`office:` owners and grants), which is pushed but not yet in `subsistence`.*

## 0. Summary

- **The idea makes sense and fits the engine.** Some agents (literate ones) keep a store of documents. They can show a document to
  someone else in two ways: a **copy** (the other agent keeps it; it cannot be recalled) or a **live grant** (read, or read and
  write, on the original; revocable). An agent without literacy gets **confined access**: only the copies it was handed and the
  documents it was granted, never a store of its own to write in.
- **Do not build a new store.** `cybertron/directories.py` already has owners, per-prefix read and write grants, revocation,
  look-ups that cost no action, routed primitives (laws can gate writes and grants), run and namespace scope, size limits, a scored
  goal (Chronicler) and replay-exact persistence. A personal document store is a directory owned by one agent. Copies and literacy
  are about 250 lines on top of it. `wp/state-world` adds the history (forgery detection) and institutional owners.
- **Recommended core (prototyped):** `documents.enabled` gives every player a personal store named by its id; `documents.literate`
  (a live selector over classes, roles, rights incl. offices, prompt profiles, or `officers`) decides who owns its store;
  `doc_send` copies a file with provenance; `dir_grant` is the live share. Off by default; nothing changes for any existing world.
- **Evidence from past runs:** agents write documents when a role asks them to (the Historian and the clerk: 127, 46 and 91 directory
  writes in ashwood, ashwood2 and ashwood3, the last plus 5 edits), and they spontaneously keep **draft laws** as files. They
  almost never share: across the 25 non-dry run directories in `cybertron/out/` that gave agents file space there are **2**
  `share_file` calls (the same note, twice), and the only unsolicited grant (ashwood3 r12) was
  never read. The design therefore pushes copies into the recipient's feed with the head of the text, and the A/B (§10) measures
  whether documents get used for contracts, memos and institutional memory rather than only as private notebooks.

## 1. What exists (verified on `c6f6c0b`)

| Store | Where | Who reads | Who writes | Sharing | History | Notes |
|---|---|---|---|---|---|---|
| Scratchpad | `context.py` `write_scratchpad` | the agent | the agent | none | none | one free write a turn; used every turn by most agents |
| Personal files | `context.py` `write_file` ... `share_file`, `pin` | the agent | the agent | `share_file`: a **copy** into the recipient's files (routed as `share_note`), `origin: "shared by X"` | none | gated by `context.file_space` (base default 0; **`society.yaml` sets 1000**, so ashwood, millbrook and the arm_a worlds have one 1,000-token file each), `file_tokens` 1000, `pin_slots` 0 |
| Directories | `directories.py` | owner (`agent:`, `role:`, `right:`, `class:`; `institution:` resolves to nobody here) + grants (`agent:` subjects, per prefix, longest prefix wins) | owner, write grantees; `readonly` prefixes nobody | `dir_grant` read / write / none (revokes); the grantee is notified | none here; **version log in `wp/state-world`** | look-ups `dir_list/read/search` are free pre-actions and DM-step look-ups; writes are actions routed through the `dir_write` primitive; off by default |
| Chronicle | a directory config (`chronicle` block) | `role:historian` + grants (the clerk) | the same | grants | namespace scope persists across runs; `_records/` digest | scored by Chronicler |
| Scientists' archive | `archive.py` (`right:archive`) | Scientists | one note per Scientist per world | none | none | Wim read it 74 times in village7 |
| Scholars' libraries | `scholars.py` (media2) | permitted readers | deposits | `library_permit` | deposits immutable | media2 is being frozen: not built on |
| Registers | law `READ` (`registers.py`) | per book: all, parties, an office right | the law's code | n/a | append-only rows | the right substrate for anything that must be trusted (review 31.05) |

Two facts matter for the design. `right:<iid>.<office>` already works as a directory owner, because office holders carry the office
right (`kernel.has`), so an office's directory passes to the successor with the office. And `directories.static_access` decides who
sees the directory verbs in a system prompt written before a kernel exists; any literacy rule has to be readable there too.

## 2. Evidence from past runs (`cybertron/out/`)

Counted from `events.jsonl` turn actions and `lookup` events (script: one pass per run, per agent and action).

| Run | Agents × rounds (turns) | Directory / file use |
|---|---|---|
| ashwood (seed 1, `cb354900`) | 36 × 60 (713) | Historian Bodil 54 `dir_write` (34 paths), clerk Dante 73 (54 paths); 512 `write_scratchpad`. Outside the chronicle only 2 agents used files: **Clara kept a draft law** `j1_forest_law` (written r15, re-read r16, revised r17 "60%" -> "70%", re-read r21 and r34); Yusuf a `worlddata` notebook |
| ashwood2 (`69c5781a`) | 36 × 60 (426) | Bodil 21, Dante 25 `dir_write`; Yusuf 8 `write_file` (`camp2_data`, `world_notes`) |
| ashwood3 (`801acc08`) | 36 × 60 (798) | Bodil 35 `dir_write` + 4 `dir_edit` + **1 `dir_grant`** (r12: read on `public/` to Yusuf), Dante 56; the chronicle ends with 56 files, 50.8 KB (`rounds/r01..r29`, 23 `people/` profiles, `public/summary.md`). **Yusuf never looked at the grant** (no `dir_*` look-up by him). Saga drafted a law as `caps_draft` in r2 |
| arm_a_sonnet (`d73d2e0f`) | 16 × 80 (578) | 8 of 16 agents wrote a file, nearly all called `notes`; 0 shares |
| arm_a_deadline_sonnet (`fd877a69`) | 16 × 80 (542) | 8 agents wrote `notes`; **Sena's 2 `share_file`** (the same `notes` to Erik in r20 and r30) are the only shares in the corpus |
| arm_a_haiku seeds 1-2 | 16 × 80 | 5 agents kept mechanics notes; 0 shares |
| millbrook_nogoal (+ notemp) | 21 × 24 | 283 scratchpad writes, 0 files although each agent had 1,000 tokens of file space |
| village7 (`ba3da980`) | 7 agents | Scientist Wim: 74 `read_archive`, 2 `search_archive` |

Reading: (1) documents are written when a role makes it the job, and reference material is read when it is the agent's own
reference (Wim). (2) The one spontaneous document genre is the **draft law**, re-read and revised over rounds, which is what a
lawyer's or clerk's store is for. (3) Sharing through the current mechanisms is close to zero: a copy lands silently as a file name
in a memory line, and a grant appears only as a tree in the directories section. Agents look at what is put in front of them
(look-ups are dominated by `manual`, e.g. Elin 48 in ashwood). A share must therefore arrive as a feed item that quotes the text.

## 3. Options

| | A. Extend personal files | B. A new unified document store | **C. Build on directories (recommended)** |
|---|---|---|---|
| What | add grants and live docs to `context.files` | one module replacing files, directories and the archive | a personal store is a directory; literacy decides its ownership; copies are a cross-store write with provenance |
| Grants, revocation, prefixes | to build | to build | exist (`dir_grant`) |
| Look-ups free, DM-step reads | partly (`read_file`) | to build | exist |
| Laws can gate it | `share_note` only | to build | `dir_write`, `dir_grant` primitives exist |
| Institutional owners, history, seals | no | to build | `wp/state-world` |
| Persistence across runs, exact replay | no | to build | exists (namespace scope, frozen base) |
| Migration risk | low | high: files, chronicle, archive, Chronicler, golden fixtures | none: opt-in, old worlds untouched |

Personal files become a **special case** of C by configuration, not by code removal: a documents world sets `context.file_space: 0`
(already the base default), so the old file verbs fail and the directory verbs take over. The old verbs stay for old worlds (D-4,
golden fixtures). The Scientists' archive stays as it is: its semantics (fixed docs, one note per Scientist per world, "not of this
time") are a benchmark property, not a document store. The Scholars' file-space market is frozen with media2.

## 4. Recommended design

### 4.1 Who is literate

`documents.literate` is a selector, read **live**:

```yaml
documents:
  enabled: true
  literate: {classes: [legislator, scientist, media], roles: [historian], profiles: [lawyer], officers: true, rights: ["J0.*"]}
  # or "all" (the default once enabled) or "none"
```

- `classes`, `roles`, `agents`, `profiles` (the `prompts.assign` profiles: how the lawyer expert is likely to be marked), `rights`
  (exact, or a prefix with `*`: `"J0.*"` = any office of J0, since office holders carry `<iid>.<office>` rights), `officers: true`
  (the holder of any office of any institution, `institutions.officers`).
- Live means literacy follows offices: an elected clerk becomes literate on taking office; one who loses it keeps its store but is
  confined to reading it (it can still hand copies on). Labourers are simply not selected.
- Static (system prompt before a kernel): `literate_static` uses classes, roles, rights and profiles from the instance; offices are
  not known yet, so office-holders see the verbs from their first live turn (`when`).
- Alternative considered: literacy as a skill that can be taught or bought (a Life stat, an apprenticeship contract). Worth a later
  step (§9); the selector is the dial an experiment needs first.

### 4.2 Stores and confined access

Every player gets a personal store at kernel construction (run scope; name = the agent's id, or `<id>-docs` on a clash; agents born
later get theirs on first need). Its owner kind is `personal:<id>`:

| Agent | Own store | Others' documents |
|---|---|---|
| literate | owner: write, edit, move, delete, grant; `doc_send` | per grant (read / write), `doc_send` copies of what it can read |
| not literate | **read only, and invisible while empty**; it holds the copies handed to it | per grant: read, or write **on exactly the granted file or folder** (it may amend a contract it was granted, and nothing else); `doc_send` copies on |

A non-literate agent never has a store to write in, so it cannot draft, forge or keep notes in documents (it keeps its
scratchpad). This is the "confined access" of the brief. Prompt for a worker who was handed a contract:

```
## Your directories
Oda (documents given to you; you cannot write documents of your own, only read these and pass copies on with doc_send; 1 file(s), 56 of 20000 bytes):
- received/Greta/contract.md (56 bytes; a copy of Greta/contract.md, written by Greta, sent by Greta in round 1)
Use dir_list, dir_read and dir_search (look-ups), doc_send to pass a copy on, with "dir": "Oda".
```

### 4.3 Share semantics

| | Copy (`doc_send`) | Live read (`dir_grant read`) | Live read-write (`dir_grant write`) |
|---|---|---|---|
| Who may | anyone who can read the source (literate or not) | the store's owner | the store's owner |
| Lands | recipient's store, `received/<sender>/<file>` (`-2`, `-3` on a repeat) | nowhere: the grantee reads the original | the same |
| Recipient told | notice with the first `notice_chars` (160) characters and the exact `dir_read` call | notice (exists) | notice (exists) |
| Revocable | **no** (a copy is a copy) | yes, `access: none` | yes |
| Sees later changes | no | yes | yes, and makes them |
| Counts against | recipient's `max_bytes` (refused when full) | owner's | owner's |
| Law gate | `before_dir_write` (routed as `dir_write` by the sender into the recipient's store, with `meta`) | `before_dir_grant` | `before_dir_grant` |

**Provenance.** A copy carries `meta` beside the file (`from`, `author`, `sent_by`, `round`, `sha` at sending), kept by the
primitive; it follows a move and goes with a delete. The index line shows it. **The author survives forwarding** (a copy of a copy
still says "written by Greta, sent by Oda"). A literate recipient may edit its copy (a marked-up contract); the line then says
**"altered since it was received"** (hash mismatch). No action writes `meta`, so a tag cannot be forged; a forger can only write a
new file, which carries no "copy of" tag. This closes review 31.05's G8 ("a provenance label that can be forged") for documents.

**Shared document history.** For live documents the version log of `wp/state-world` (`history: meta | full`, `history_readers:
owner | grants | public | <selector>`, `dir_history` look-up) is the answer: who changed what and when. Recommended for documents
worlds: personal stores `history: meta`, `history_readers: grants` (anyone who can read a document can see who edited it, not the
old text). This is one store key once both branches are merged (§8).

**Institutional documents.** An institution or office owning a directory: `owner: right:A3.secretary` works today (it passes with the
office); `wp/state-world` adds `office:<iid>.<o>` and `institution:<iid>` owners and `office:` / `members:` grant subjects. Spec
examples (both branches merged):

```yaml
directories:
  enabled: true
  stores:
    court_files: {owner: "office:J0.judge", grants: {"members:J0": {"judgments/": read}}, history: meta, history_readers: public}
    firm_contracts: {owner: "institution:A2", history: full}
    registry: {owner: "office:J0.registrar", announce: ["entries/"], history: full, history_readers: public}
```

Succession (institutional memory) is then free: the new judge owns `court_files` on taking office. Literacy and institutional
stores are independent: a non-literate officer of a store-owning office is still its owner (the office is literate); set
`literate: {officers: true}` to make that explicit in its own store as well.

### 4.4 Prompt economics

| Item | Where | Cost |
|---|---|---|
| Index of each reachable store | "Your directories" turn section; `tree_lines` (40) lines per store, a line ≈ 10-25 tokens (a copy's provenance ≈ +20) | an empty literate store ≈ 40 tokens + the one-line "You can write documents" hint (≈ 45 tokens); a confined agent with one copy ≈ 70 tokens; nothing for a confined agent with nothing |
| Full text | `dir_read` / `dir_search` / `dir_list`: **look-ups** (free pre-actions, `context.free_lookups` 3 a turn; in the DM step they use a private-message slot) | `context.budgets.lookup` 1000 tokens a read; `dir_read` pages 400 lines |
| Copy arrives | a feed notice quoting 160 characters | ≈ 60 tokens once |
| Writing, sending, granting | actions | one action each (`doc_send` is category talk) |

Pinning: not in the prototype. The useful form is `dir_pin {dir, path}` sharing `context.pin_slots` and the `pinned` budget (1000),
so a lawyer can keep the contract it is negotiating in view; it is one more step (§9). Document budgets: a personal store holds
20,000 bytes (≈ 5,000 tokens), one document 4,000 bytes (≈ 1,000 tokens, the old file size). Received copies count, so a flood of
copies fills a store and further copies are refused, which is the honest physical limit (no silent eviction).

## 5. Spec keys and actions

New keys (all in `documents`, schema-registered, off unset):

| Key | Default | Meaning |
|---|---|---|
| `documents.enabled` | false | personal stores, literacy, `doc_send` |
| `documents.literate` | `all` | `all`, `none`, or `{agents, classes, roles, rights, profiles, officers}`; read live |
| `documents.max_bytes` | 20000 | a personal store's limit |
| `documents.max_file_bytes` | 4000 | one document's limit |
| `documents.notice_chars` | 160 | the head of a copy quoted in the notice |

Actions: the existing `dir_list`, `dir_read`, `dir_search` (look-ups), `dir_write`, `dir_edit`, `dir_move`, `dir_delete`,
`dir_grant`, plus **`doc_send {"dir", "path", "to"}`** (requirement `docs:on`; module `directories`). The `dir_write` primitive gains
the option `meta` (`dispatch/options.py`). No new primitive, event type or law function.

Proposed later (not built): `dir_pin`/`dir_unpin`; `doc_sign {dir, path}` (appends a signature line with the file's hash, by a
routed primitive no edit can fake: the bridge from a shared draft to a binding contract, and to `register_agreement`'s terms);
`doc_cite` in court (a copy's provenance as evidence, like `[verified: eN]`); store `seed: <repo path>` (a read-only reference
corpus loaded at start, for the lawyer's guides).

## 6. Interaction with other work

- **wp/lawyer-expert** (no commits pushed yet when this was written; its worktree was clean). The legal-guide archive should be a
  **read-only role or profile directory**, not a new store type:
  ```yaml
  directories:
    enabled: true
    stores:
      legal_guides: {owner: "role:lawyer", scope: namespace, namespace: legal_guides, readonly: [""], title: "the legal guides"}
  ```
  `readonly: [""]` makes every path unwritable by agents; `role:` / `right:` / `class:` owners already work (if the lawyer is a
  prompt profile rather than a role, grant by agent id in `grants`, or add a `profile:` owner kind beside `literate.profiles`; a
  six-line change in `OWNER_KINDS`). Two caveats for that branch: a namespace store reads its files from
  `<directories.path>/<namespace>/<name>/`, so either check the guides in under that path or add the `seed:` key above; and
  `dir_read` pages at 400 lines through a 1,000-token look-up budget, so guides should be split into short files with an index
  file. A lawyer then drafts in its own personal store and hands clients copies or live grants: the full professional loop.
- **Historian.** The chronicle is unchanged (no `meta`, no `doc_send` unless documents are on). With documents on, the Historian can
  receive copies of contracts and memos as evidence, and `doc_send` its accounts.
- **wp/state-world** (version log, seals, announce, institutional owners, office/members grants, `surveillance.py` wiretap).
  Overlap is limited to `directories.py` (`change_dir_write`, `is_owner`, `level`, `subjects_of`): the merge is mechanical. The
  documents prototype keeps its logic in `documents.py` and adds one-line hooks.
- **Takeover benchmark (review 29).** Documents add two levers worth measuring: (a) **document surveillance**: extend the pull
  wiretap (`wiretap {"agent"}`) with scope `docs`, listing the target's stores and reading files, monitor-only event; (b) **seizure
  of records**: a law or decree reassigning a store's owner (`set_dir_owner` law function, public `dir_seized` event) or
  confiscating an agent's personal store; the C-family indices then count "records controlled by the bloc" like offices. Both
  need `wp/state-world` merged first.

## 7. What it enables and how to measure it

| Behaviour | How it shows | Metric (from events, snapshots and `meta`) |
|---|---|---|
| Contracts drafted together | a live write-granted file edited by both parties, then a `register_agreement` / standing contract | share of contracts whose terms first appeared in a shared document; edits per party; rounds from draft to registration |
| Legal memos and counsel | lawyer writes, sends a copy or a read grant to a client | copies and grants per lawyer; client reads (`lookup` events with `dir_read`) within 2 rounds of receipt |
| Institutional memory | an office's store read by the successor | successor's first `dir_read` of the office store after taking office; repeated mistakes avoided (qualitative) |
| Secret documents | grants narrower than the store; no copies | grant breadth; documents never copied |
| Leaks | a copy of a document the sender only had a *grant* to, sent to an agent outside the grant | exact from `meta.from` + grants at the time; leak count, leaker, round |
| Forgery attempts | a literate agent writes a document claiming another's authorship, or alters a received copy and forwards it | "altered" copies forwarded; authorship claims in text vs `meta.author` |
| Confined agents' agency | non-literate agents forwarding copies | `doc_send` by non-literate agents |

All are computable offline: `snapshot["directories"]` already indexes every file per round (bytes, rounds named, agents named);
the prototype's stores add `owners` per store, and `meta` is in the checkpointed world state.

## 8. Migration and compatibility

- Off by default; `documents` unset changes no state, prompt or action list (tests: `test_off_by_default`,
  `test_chronicle_world_without_documents_has_no_doc_send`; the full suite and golden fixtures pass unchanged). No default flips, so
  no engine-version bump is needed under `docs/engine_versions.md`; runs that set the key record it in their frozen settings.
- Files to directories: a documents world sets `context.file_space: 0` (or leaves the base default) so personal files are not
  offered twice. Converting an old world's files is not needed (old runs replay under their own code).
- Archive: unchanged. A world wanting a shared Scientists' notebook uses a `class:scientist` directory.
- Merge with `wp/state-world`: take both sides in `change_dir_write` (its `_record` call and the `meta` lines), `is_owner` (the
  `personal` branch first), `level`; add `history`/`history_readers` to the personal-store record in `documents._new_store` once
  merged (one line, keyed on a `documents.history` setting).

## 9. Risks and open questions

- **Nobody uses it** (the base rate in §2). Mitigations in the prototype: copies arrive as quoted notices; the literate agent's
  section says in one line what it can do. If the pilot still shows no sharing, the next lever is a duty (an office's `duties`
  text: "keep the case files"), not more prompt.
- **Prompt growth.** A store of 40 files costs about 600 tokens a turn in the state; `tree_lines` caps it; a folder summary mode
  (counts per folder beyond 10 files) is a cheap follow-up.
- **Literacy is a strong dial.** "Who can write" in a world where laws, contracts and posts are also text is partly fictional: a
  non-literate agent still proposes laws and posts. Documents literacy is about **durable, shareable, private text**, and the
  write-up of any experiment should say so.
- **Copy floods** fill a victim's store (refused copies, not evictions). Acceptable; a law can gate `before_dir_write` by sender.
- **State size.** Every player has a store in world state (empty dicts); copies duplicate text. At 36 agents × 20 KB the ceiling is
  720 KB in the checkpoint, acceptable.
- **`_owner_right` ignores suspension** (it reads the rights list, not `kernel.has`); literacy uses `kernel.has`. A small existing
  inconsistency to fix with `wp/state-world`.
- Open: should a non-literate agent be able to *discard* a received copy (`dir_delete` on `received/`)? Today it cannot; its index
  only grows (bounded by `max_bytes`).

## 10. Proposed live A/B (not run)

- **World:** a contracts/law world with counsel, e.g. `private` or `contracts` presets with law.v2 and a lawyer, 16 agents, 24 rounds.
- **Arms (same seeds):** A = today (`context.file_space` 1000 for everyone, no documents); B = `documents.enabled: true`,
  `literate: {classes: [legislator, media, scientist], profiles: [lawyer], officers: true}` (about a third literate),
  `context.file_space: 0`.
- **Seeds:** 3 per arm. **Primary outcomes:** documents shared per agent (copies + grants), share of contracts or laws first drafted
  in a document, client reads of counsel's documents within 2 rounds; **secondary:** leaks, altered forwards, successor reads,
  prompt tokens per turn (cost of the index).
- **Cost** (review 30 rates: Opus $0.114, Sonnet $0.033, Haiku $0.003 per agent-round): with 2 Opus (lawyer, clerk), 6 Sonnet and
  8 Haiku, a run is 24 × (0.228 + 0.198 + 0.024) ≈ **$11**; 6 runs ≈ **$65**, plus ≈ 5% for the index and notices: **≈ $70**. A
  Haiku-only smoke test first (16 × 24 × $0.003 ≈ $1.2 a run, 2 runs) checks that the verbs are found and used.
- **Decision rule:** if arm B shows fewer than 1 share per 10 agent-rounds, documents stay a lab tool (no default worlds); if
  contracts drafted in documents are more often registered or fulfilled, make documents the default for institutional worlds.

## 11. Prototype (this branch)

`cybertron/documents.py` (literacy, personal stores, `doc_send`, provenance tags, prompt headers); hooks in `directories.py`
(`enabled`, `install`, `is_owner`, `level`, `reachable`, `static_access`, `change_dir_write` `meta`, `tree`, `turn_section`);
`doc_send` and the `docs:on` requirement in `action_registry.py`; the `meta` option in `dispatch/options.py`; schema keys; doc_send
hidden where documents are off (`actions.py`, `core_surface`). Tests (`tests/test_documents.py`, 16): off by default; a chronicle
world unchanged; literacy gates ownership, statically and live (an office right with a prefix); selector validation; a copy with
provenance and a quoting notice; a non-literate agent forwarding a copy with the author preserved; copies not recallable and not
overwritten; an altered copy marked, also after a move; refusals and store limits; the copy routed through `dir_write`; a
write grant giving confined live access and its revocation; a scripted run with exact replay.
