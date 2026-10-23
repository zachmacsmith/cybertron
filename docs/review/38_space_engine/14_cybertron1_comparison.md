# Review 38.14: cybertron2 M1 against cybertron 1: what was lost, and what to do about it

*23 Oct 2026, 37.4 session, at Zach's request ("talking should work kinda like DMs... Why is the talk step re-asking? Compare to
cybertron 1... see if there has been any good functionalities lost"). Read: `cybertron/runner.py` (the DM step), `memory.py`
(history mode), `agents.py` (the reply), `credit.py` and `action_registry.py` (loans, channels), `specs/base.yaml`; this
session's `cybertron2/m1/`. Complements [07_cybertron1_review.md](07_cybertron1_review.md) and [porting.md](porting.md). Nothing
here is decided.*

## 1. Lost or worse in M1

| Function | cybertron 1 | M1 | Verdict |
|---|---|---|---|
| **Who is asked again after talk** | the DM step: only an agent who **received a DM** is asked again; replies are delivered and their recipients asked again, up to `exchanges` waves. Public posts wake nobody | anyone who **heard anything**, including every `say`, is asked again: 110 of 110 agent-days in run D, doubling the calls | **worse**: a regression in cost and in design. Zach: only direct speech should wake |
| **Scopes of speech** | `dm` (one person), `reply` (to a message, optionally with payment), `post` (public), channels (private groups), `send` (an agent, an institution's inbox or a channel) | `say` (everyone at the node), `tell` (one person, or one household since run C) | **narrower**: no room or building scope, no groups, no reply-to-a-message |
| **The model thinking** | `llm.thinking_budget: 2000` by default ("every reply also carries a stated reasoning field") | **no thinking budget is passed**: the models answer without native thinking; only the stated `why` ("a sentence or two") | **lost**: a one-line fix; it costs output tokens |
| **Continuity of the agent's own reasoning** | history mode: each agent's prompt is a **conversation** that runs for `chunk` rounds (3), so its own earlier replies and reasoning stay in context (cached by a CLI session); then restarts with a gradient | a fresh call each day; the agent never sees what it reasoned yesterday (only, in the talk step, its own first plan of the same day) | **lost** |
| **Memory of exchanges** | the full band holds "every private message of the round in order per counterpart"; the summary band "who it exchanged messages with and about what" | heard lines in arrival order, everyone's speech mixed; the summary band does not mention exchanges | **worse** |
| **Recall** | `recall {"round": N}` returns a past round in full | none | **lost** |
| **Long memories** | by salience **category**: deaths of close contacts, attacks, kin, open deals, laws | a keyword filter on a few result lines | **worse** |
| **Per-agent memory length** | each agent draws its own `memory_turns` (2-5) | 2 for everyone | lost (a design choice that varied agents) |
| **Lookups** | the manual's sections, facts, in the DM step | crafts and one's own notes only | narrower |
| **Loans** | `lend`, `accept_loan`, `repay_loan`, `extend_loan` (an item, an amount to repay, a due round, a rate; defaults recorded), when a law enables them | none: offers are same-day exchanges of goods only; no lending a tool, no loans, no services | **lost**, and not in proposals/verbs.md either: an omission of this session |
| **Contracts, escrow, standing contracts, agency** | yes | none | not yet (known, porting.md) |
| **Prompt budgets and trimming** | context budgets with deterministic trimming | none: run D's prompts reached 16k characters | lost |
| **One registry for actions** | each action's handler, gates, docs and prompt line from one place | handlers, options and prompt text in three places | lost; the source of several M1 faults (13 §5) |
| **The instrument** | checkpoints each round, resume, replay, fork, interventions | none: a crashed run is lost | not yet |
| **The chokepoint** | every change through `k.apply` with hooks and causes | direct changes in `act.py` | not yet (07 §4 step 1) |

## 2. Kept or better in M1

Places and parcels with cover types as data; presence-based audiences; the knowledge levels with sources and near misses;
attention and the daily notice; notes with a pinned one (cybertron 1 had one scratchpad); same-day talk before work; households
with stores and hearths; a generated society with a family tree; offers with goods set aside; schema-enforced arguments.

## 3. Proposals

### 3.1 Speech (Zach's model)

| Verb | Heard by | Wakes the hearer? |
|---|---|---|
| `tell {to: person}` | that person | **yes**: asked again before work; may reply (which wakes the first speaker in the next wave) or change plans; waves capped as in cybertron 1 |
| `say {in: building}` | everyone in that building | no |
| `announce` (to the town) | everyone at the node | no |

Open points: (a) where people are at talk time: if everyone is at home in the morning, a building means one's household and any
guest; a hall or the green would need presence by building; (b) speech that does not wake arrives in the hearer's next morning
prompt, a day late for anyone not woken, which conflicts with "speech must not lag" (devlog decision; 05 §1); cybertron 1 accepted the same
lag for posts. (c) `reply` to a message as in cybertron 1, or a `tell` back.

### 3.2 Memory (Zach: "leave it off, or have an agent summarise their history")

| Option | What the agent sees | Cost | Risk |
|---|---|---|---|
| A. Off | yesterday's results and what concerned it (engine facts), notes, seeded memories | lowest | loses anything not written in a note |
| B. Agent-written | A, plus a line the agent writes each morning about yesterday ("in your own words"), kept as its summary band; every few days it rewrites a short "story so far" that replaces the oldest lines | one more field a day; a longer reply every few days | the Piers error: an agent's account of itself drifts from the facts; yesterday's engine facts stay as a check |
| C. cybertron 1's conversation | the agent's own past replies in context for a few days, cached; a gradient at each restart | cheaper per call through caching; longer prompts | needs session handling (already in `cybertron.llm`) |

Recommendation: B with yesterday's engine facts kept, or C if continuity of reasoning matters more than prompt size.

### 3.3 Lending

A loan is a promise with a return: `lend {to, item, qty, back_by}` (goods leave now; the borrower sees a due line until it is
returned or the day passes; the lender sees it too), `return {to, item, qty}`. Whether a missed return is only remembered or also
enforced is a law question (later). A tool lent can be used by the borrower that day.

### 3.4 Aims

Aims are written once (by hand or by the generator) and never change. Maud's generated aim was "Prove yourself to your family, and
learn reaping grain as the Reeds do it"; she was taught on day 1 and went on trying to learn. Either aims are allowed to be met and
replaced (by the agent, in a note), or the prompt says when one has been met.

### 3.5 Thinking

Pass `thinking_budget: 2000` as cybertron 1 did. The CLI returns the thinking text for Haiku and withholds it for Sonnet and Opus
(counted as withheld); the API returns summaries for all.
