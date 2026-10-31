# A page for playing an agent

**Status:** retrospective, accepted: D4-63
**Owner:** 37.4

## Summary

A local web page on the run's journal where a person plays one agent: on the left exactly what the model would be shown, on the
right a form built from that request's reply schema. A verb is chosen from a list and shows only its own arguments; arguments the
schema closes are lists; free text is typed. The reply sent is the same JSON a model would send, checked against the schema.

## The proposal (as built)

- `python -m cybertron2.engine serve RUN --new WORLD --as NAME [--days N] [--bots] [--port 8765]` starts a run with NAME played by
  a person and serves the page at `http://127.0.0.1:8765/?as=NAME`; `serve RUN` serves an existing run. `--bots` makes everyone
  else scripted (no model calls), to try it out.
- The left: the system text, each earlier turn of the conversation (its message and the reply given), and the new message, as
  `views.context` returns them; nothing else.
- The right, built from the request's own schema (`cybertron2/engine/play.html`):
  - **Why**, a text box.
  - **Actions, in order**: a verb from the schema's list; under it the verb's line from the registry (`api.verbs()`: arguments
    and what it does) and one field per argument it takes (optional ones marked); a list where the schema closes the argument
    (crafts, places, items, people), a number, a tick, or free text; free-text fields that name someone or somewhere (`with`, `to`,
    `lead`, `stop at`, `head`, `heir`) offer the schema's own names but take anything. "+ other field" adds any other argument.
    Rows can be moved and removed.
  - The message's "Today you could: ..." line as one-click actions (verb, craft and place filled in).
  - Tell, say and offers as rows of their own fields; explain, notes, attend, look up, pin, forget and open folded under "More".
  - A memory turn shows the memory box first, a word count against the limit the message states, and (when there is one) a
    button to start from the memory as it stands.
  - A talk turn ("give your whole plan for the day again") starts from the plan given before.
  - The reply as JSON, shown as it is built; "Edit as JSON" to write it by hand.
- On "Answer" the server checks the reply against the schema (refusals shown, nothing stored); once no person is waiting, the run
  goes on, and the page waits for the person's next turn.

## Why

Zach (31 Oct): "a very basic system where I can see exactly what an agent would, and give my input to play in the simulation like
I am one of them ... rather than having to type literally everything it could like show me the verbs I can choose and then I just
type the things that are fully freeform". R3 (review 38.35) had the terminal and a bare page where the whole reply was typed as
JSON.

## Alternatives considered

- **The terminal only** (R3's `play`): exact, but the whole reply is typed as JSON.
- **A form per verb written by hand:** drifts from the engine; the form is generated from the schema and the registry instead,
  so a new verb or argument appears without touching the page.
- **Showing the verbs' costs and the units left as you plan:** needs the world's state in the page (a cost depends on tools,
  skill and place); left out so the page shows only what the model is shown.

## Open questions

- Whether the page should say how many units the plan spends (the model is not told; the engine refuses what is beyond).
- Several people playing at once (each with `?as=`) works on one server; untested beyond two.
- The interface named in spec/record/human_play.md is 37.1's (OPEN Q-RR3); board post asks them to record both.

## Affects

spec/record/human_play.md (37.1: the interface and commands); cybertron2/engine/api.py, play.html, run.py (`serve` options).

## History

- 31 Oct 2026: built at Zach's request (37.4), with D4-63; tried with Lucy in the duo world (scripted others): decisions, a talk
  turn after Roger spoke to her, and an end-of-stretch memory, to the end of the run; tests in tests/test_cybertron2_play.py.

## Sources

Zach's message of 31 Oct; cybertron2/engine/api.py; cybertron2/engine/play.html; review 38.35 (R3).
