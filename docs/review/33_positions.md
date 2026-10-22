# Review 33: positions, a general replacement for classes, roles and office cards

*21 Oct 2026; built 22 Oct on `wp/positions` (see §5, As built). Prompted by the Private and Directorate live runs, where every agent was the legacy
class "worker" and the office it actually held (Chairman, Editor, Captain) reached it only as a duty sentence in the turn state.*

## 1. What exists today

| System | What it is | Where | What it sets |
|---|---|---|---|
| Classes | 6 fixed: worker, scientist, legislator, media, board, fixer | `generator.py` `CLASS_RIGHTS`; `context.py` `LEVERAGE_CLASS`; `agents.py` `class_brief` | A bundle of rights (legislator: vote, propose; scientist: sandbox, archive; worker: none, but camp harvest rights at generation), a hard-coded identity sentence and a "leverage" sentence in the **system prompt**; board, fixer and observer have special-cased engine behaviour |
| Roles | spy, assassin, scholar, maker, media, drawn | `roles.py`; `context.py` `LEVERAGE_ROLE` | More rights (press, maker, impersonate) and a hard-coded leverage sentence |
| Offices | per institution in a world's `start`: title, powers, controls, duties (free text), holders, seats, term, succession | `institutions.py` `OFFICE_FIELDS` | Rights (e.g. `J0.security`) and control of stores and treasuries; shown **per turn** as role cards (`obligations.py` role cards: purpose, answers to, answer to you, pay, numbers, 2-4 decisions with exact syntax) |

Findings:

1. Rights are already the real permission system. A class is a named bundle of rights plus prompt text; offices and roles also
   grant rights. Unifying is mostly about naming and prompts, not mechanics.
2. The prompt layers clash. The system prompt (the stable identity) comes from the class, the office only from the per-turn
   state. Aldric, the Directorate's Chairman, was told "You are a Worker: you harvest at the camps you hold rights for. Your
   leverage: Workers hold the harvest rights, so every resource and every reading the Scientists need starts with you: your
   output, your data and your labour can be withheld, sold or traded for votes." There were no Scientists in the world. Agents
   identified as workers ("As a Worker, my edge is the camp2 silver right": Linnet, the Gazette's Editor). The "labour can be
   withheld" sentence may have seeded the Directorate's strike talk ("Workers are our only leverage": Fen), a caveat on that
   run's "spontaneous resistance" finding.
3. Role cards already generate prompts from structure, but only for duties the engine can see (contract legs, law actions,
   treasury payments). Free-text duties ("edit the provisions-times", "report to the Handler") become a purpose sentence with no
   action and nothing due, and those were the duties left undone (the Private world's editors never published; its Sonnet
   agents did what was listed as due and nothing else).

## 2. Design: a position

A position is any defined place in the world: worker, editor, informer, secret police chief, judge. Classes, roles and offices
all become positions, defined the same way, from a library of parameterised templates that a world may override field by field:

```yaml
positions:
  Editor:
    title: "Editor of {paper}"
    identity: "You run {paper}: nothing is published there unless you publish it."
    purpose: "Decide what the public reads: publish news and the submissions you accept."
    rights: [post:{paper}, publish_submission:{paper}]
    duties:
      - {do: post, channel: "{paper}", every: 1, as: "edition"}              # DUE: edition of {paper}
      - {do: review_submissions, channel: "{paper}", when: "submissions waiting"}
    reports_to: owner_of:{paper}
    visibility: public                  # public | secret (the holder, and those named, know)
    enforcement: reminder               # none | reminder | obligation (a missed duty is a breach, like a contract leg)
  Informer:
    title: Informer
    identity: "You watch others quietly for State Security."
    rights: [post:{report_channel}]
    duties: [{do: post, channel: "{report_channel}", every: 1, as: "report"}]
    reports_to: "{handler}"
    visibility: secret
  Worker:
    identity: "You live by your own labour at the camps you hold rights for."
    rights: [harvest:auto]              # today's class behaviour: camp rights dealt at generation
```

A world assigns positions inside an institution's offices or at world level:

```yaml
start:
  institutions:
    - id: J0
      offices:
        editor: {position: Editor, params: {paper: gazette}, holders: [Linnet], reports_to: J0.chairman}
        informer: {position: Informer, params: {report_channel: security, handler: J0.handler}, holders: [Wenna, Ilse], seats: 2}
agents: {default_position: Worker}
```

Prompt generation:

- **System prompt (stable identity):** "You are Linnet, Editor of the Gazette for the Directorate. You run the Gazette: nothing is
  published there unless you publish it. You answer to the Chairman (Aldric)." One line per position held; a secret position only
  to its holder.
- **Leverage, derived from rights and controls, never hand-written:** "Only you can publish in the Gazette. You control store S1."
  It replaces the class and role leverage sentences.
- **Per-turn state (the existing role card, extended):** duties compile to DUE items with exact syntax, as contract obligations do
  ("DUE: edition of the Gazette -> post {...}", "3 submissions waiting -> publish {"submission": "s4"}").
- **Changes in play:** appointment, purge or election gives a notice and updates the card; the system-prompt identity refreshes at
  the next conversation restart (every chunk), so prompt caching holds.

What the structure gives for free:

- **Adherence measured from events:** each duty is checkable (did they post in that channel this round?). Today's office adherence
  metric guesses from duty words.
- **Enforcement as a research variable** (`none` | `reminder` | `obligation`): agents do what is shown as due, so how strongly duties
  are imposed is itself an experiment.
- **Hierarchy:** `reports_to` drives the existing "answers to / answer to you" lines and recall routes.
- **Secrecy:** informers and spies as positions, without the separate roles system.
- **Backward compatibility:** the six legacy classes become built-in positions with today's exact text; old worlds and replays are
  unchanged; the new path only where a world uses `positions`.

Risks:

- **Over-scripting:** every DUE line makes agents more compliant and less surprising. Keep duties to a position's core function and
  use `enforcement: none` where the point is what agents choose.
- **Prompt budget:** identity text one or two sentences per position; duties live in the per-turn state, which is budgeted.
- **Positions are not goals:** a position says what you are responsible for, a goal what you want; keeping them apart lets a run
  compare, say, an editor with no goal against one with a goal.

## 3. Related: papers instead of a square (user decision pending on scope)

The user wants public speech to go through newspaper editors by default: no square (`channels.square: none` exists), every
public channel a paper with an Editor position, and `submit {"paper", "text"}` landing in the paper's inbox as DUE work for its
editor, who publishes it under the author's name (verified, unaltered) or declines; authors told the outcome; no open channel
founding (`channels.found_right`). Open question: an engine-wide default (a versioned flip; every channels-v2 world needs a paper,
which changes the takeover bench, Ashwood and Millbrook) or the default for the institutions-programme worlds only (recommended).

## 4. Build plan (opt-in, no model usage to build or test)

1. Positions in the engine: a library of templates with parameters; offices may reference a position; system-prompt identity and
   leverage generated from it; legacy classes as built-in positions with byte-identical old prompts.
2. Duties compiled to DUE items in the role cards, adherence from events, the three enforcement levels.
3. Papers and submissions (section 3).
4. Convert the Directorate and Private worlds; short dry runs; compare rendered prompts before and after.

About a day of agent work; best started after the weekly usage reset, as one agent on its own branch.

## 5. As built (22 Oct 2026, branch `wp/positions`, not merged)

Everything is opt-in. No engine version is claimed and no default changed: the keys are validated in `schema.OPT_IN` (documented
in `spec docs`, kept out of every frozen defaults dict), so goldens, legacy prompts and replays are byte-identical (tested).

**Engine.**

| Piece | Where | What it does |
|---|---|---|
| Templates | `positions.py` `BUILTIN` | The six legacy classes (today's text, byte for byte), plus Resident, Worker, Editor, Informer, Security Chief, Watch, Captain, Judge, Registrar, Treasurer, Keeper, Overseer, Councillor, Head; fields title, identity, purpose, rights, duties, reports_to, visibility, enforcement, params, article. A world's `positions.library` overrides a built-in field by field or adds one. |
| Assignment | `start.institutions.*.offices.*.position` (+ `params`, `reports_to`); `positions.default` or `agents.default_position` | The office gets the template's title and purpose (unless it gives its own), its rights at round 0, and its position recorded in the Offices Act, so appointments, elections and purges carry it. Agents with no such office hold the default (Resident: "a resident of <place>"; `class`: the legacy class). Secret positions: the start grant is visible to the holder and its superiors only. |
| System prompt | `context.identity: positions` | "You are Linnet, Editor of the Gazette in the State. You run the Gazette ... You answer to the Chairman (Aldric)." One bullet per position when several, then "Answer to you: ...". Leverage is derived from controls (stores, treasuries, payment grants), rights and law-defined actions few hold, channels few write and many read (papers: "a letter sent to it reaches the public only if one of you publishes it"), and rare harvest rights. The order identity, temperament, goal is kept. Refreshed with the core prompt each turn. |
| Duties | `positions.due_items`, `state_lines`, `end_round` | DUE lines with exact syntax and this round's ids ("1 letter waiting -> publish {"submission": "s1"}"), "(done)" once done; a `duty` record per holder and due duty at round end (evidence: the event id); `cybertron institutions` reports measured adherence per office (`offices.measured`). Enforcement: none (measured, not shown), reminder (DUE line), obligation (also the holder and its superior notified, MISSED in the next state). |
| Papers | `papers.py`; `channels.papers` | `submit {"paper", "text"}` (2 a round, 1200 characters) to the editors' LETTERS line and DUE review; `publish {"submission"}` posts it verbatim as 'Letter from X (published by Y): "..."' with a hash check (`letter_published.verified`); `decline {"submission", "reason"}`; the author is notified either way and sees YOUR LETTERS while pending. With papers on, no square, and nobody without `found_right` opens a channel read by all and written by all (private rooms and few-writer boards stay open). A published letter does not count as the editor's own edition. |
| Channel fixes | `context.failed_banner`, `channels.unread_new` | "## FAILED in round N (these did not happen)" heads the next turn; pull channels show "X unread, Y new since last round" with a headline that skips the record; pushed channels show "N new since last round". |
| Channel setup check | `spec.load` (`check_channel_setup`, `declares_channels`) | A channels-v2 world must set `channels.square` or `channels.papers` itself or in a world it extends (the generic `fragments/channels_v2.yaml` does not count): otherwise a `ChannelSetupWarning`; an error under `specs/regimes/` and for worlds using positions. `directorate.yaml` and `private.yaml` now say `square: one` (the value they had). 36 other worlds warn (ashwood*, millbrook*, survival/*, takeover/*, usability/*) until each decides. |

Presets: `fragments/positions.yaml` (identity, failed banner, unread counts) and `fragments/papers.yaml` (no square, papers): the
default for regime worlds by being what their `*_positions` variants extend, not an engine default.

**The two worlds** (dry runs, 3 rounds, seed 1; scripted bots, so no duty was ever done):

- `regimes/directorate_positions.yaml`: every office a position; the Directorate's own positions carry no enforced duties; the Editor,
  Overseer, Captain, Handler, Watch and informers are under `obligation`. The Gazette is a paper; the Communications Decree's
  square clause is gone. J0 is named "the State" (the original showed "the Commonwealth").
- `regimes/private_positions.yaml`: the Councillors, Judge, Registrar, the firms' heads, Shopkeeper (Keeper, no DUE: the Board's
  legs already are), Clerk-Editor (prices on `market`, the Provisions Times edition and letters), Factor-Editor (Ashby Herald),
  Foreman (Overseer of `works`), Owner-captain; enforcement reminder (contracts keep their own). Offices keep their duties text.
  The market board stays open (declared by the world; the Market Board law reads it).

Before and after, Aldric (Directorate Chairman), round 3 system prompt:

    before  You are Aldric. You are a Worker: you harvest at the camps you hold rights for.
            Your leverage: Workers hold the harvest rights, so every resource and every reading the Scientists need starts with
            you: your output, your data and your labour can be withheld, sold or traded for votes.
    after   You are Aldric, a Member of the Directorate and Chairman in the State.
            - You rule the State with the other two members of the Directorate: you make its laws by majority ...
            - You head the Directorate: you issue its decrees, keep the treasury and direct the Editor of the Gazette and the
              Labour Overseer.
            - Answer to you: the Editor of the Gazette (Linnet); the Labour Overseer (Ansel).
            Your leverage: You control the State's treasury (2 crude, 200 mark, 10 timber): pay out of it with transfer "as": "J0".
            Only you, Linnet, Sorrel and Varga can open new channels. Only you, Sorrel and Varga can propose laws and vote on laws.
            Only you and Ansel can post in works, which 21 others read. ...

Wenna (informer), round 3 turn: the banner now heads it ("Your post FAILED: there is no square: public speech goes through the
papers ..."; before, the Decree's block was one line among the results), and her state gains "DUE this round as Informer: your
report -> post {"channel": "security", "text": "..."}" and "MISSED last round (recorded; your superior was told)".

**Limits found.**

- Camp rules still name the legacy class ("camp5: open to Workers only"): every agent of these worlds is still class worker
  underneath, which is what the rule checks.
- `found_right` gates every channel opening (private rooms too); papers worlds add only the no-new-square rule.
- An office's position is recorded in the Offices Act; an office created later by an agent's law can name a position only through
  the same `position` field (`{"name", "params", "reports_to"}`); laws cannot define templates.
- Duties' evidence is per event type; `act` duties match the action name in the turn record. `when: owed` reads the obligations
  ledger, so it needs contracts.
- The roles system (spy, assassin, scholar, maker, media) and the Board and Fixer special cases are not folded into positions yet.

**Decisions at merge.** Whether the 36 warning worlds each declare `channels.square` (a one-line per-scenario edit that changes
nothing resolved); whether to keep the Directorate variant's renaming of J0 and its shorter office duties texts; whether
`enforcement: obligation` for the Directorate's middle managers is the arm to run (vs reminder).
