# Review 33: positions, a general replacement for classes, roles and office cards

*21 Oct 2026. Design only, nothing built. Prompted by the Private and Directorate live runs, where every agent was the legacy
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
