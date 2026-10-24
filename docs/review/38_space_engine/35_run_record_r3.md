# 38.35: R3 of the run record built (a person plays an agent, through a thin API)

Session 37.4, 24 Oct 2026. From spec/record/human_play.md and views.md (D1-1, D1-4). Code: cybertron2/engine/api.py (new);
run.py (the `human` responder, `--as`, `play`, `serve`). Tests: tests/test_cybertron2_play.py (2). Zach: "a relatively thin
layer on everything else that returns as an api / with clean interface so something else like a website can show the context and
collect the choices. Build a super basic version."

- **The `human` responder.** `run SPEC --as NAME=human` (or `fork ... --as NAME=human`): when NAME's request comes, it is
  written to the journal exactly as a model's would be (system text, schema, message, conversation), the other agents' answers in
  that step are kept, and the run stops. Answered, the run goes on (`resume`): every earlier answer is reused, so nothing is asked
  twice and the person's answers replay like any other.
- **The API** (api.py), on the journal only: `pending(run, agent)`, `context(run, key)` (views.context: what a model would be
  shown), `answer(run, key, reply)` (checked against the reply schema; refused with the problems, or stored), `advance(run)`
  (plays on to the next person's turn or the end), `status(run)`.
- **Front ends, basic:** `play RUN --as NAME` in the terminal; `serve RUN [--port]`: `GET /status`, `GET /context/<key>`,
  `POST /answer/<key>`, and a bare page at `/` that shows the context and takes a JSON reply (checked in a headless browser).

A person gets every request a model would: the day's decision, talk-step replies when woken, the memory at the end of a stretch
(in the conversation's own schema), and a new stretch begins from what they wrote.

Not built: a form that composes the JSON (the page takes JSON as typed); R6 (dropped).

*Current as of 24 Oct 2026.*
