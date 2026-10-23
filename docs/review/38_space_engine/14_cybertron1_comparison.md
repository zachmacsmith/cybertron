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
| **The model thinking** | `llm.thinking_budget: 2000` by default ("every reply also carries a stated reasoning field") | no budget was passed, but **the models thought anyway**: the CLI's adaptive thinking ran on nearly every call (withheld thinking blocks in runs A to D); its text is withheld by the CLI for these models either way | **not lost** (corrected 23 Oct after the check run: an earlier version of this row said it was); the budget is now set as cybertron 1; reading the thinking needs the API backend |
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

## 4. Content added to M1 without a decision (Zach: "when did you add fishing? ... pots?")

| What | When and where | Source | Against the decided economy |
|---|---|---|---|
| fishing (a line, the brook's fish), line-making from withies | 23 Oct 02:02, `cybertron2/m1/data.py` in the M1 build (adc2f84) | my plan for the slice: "fish" is listed as a method of water in layout.md and verbs.md (method names only) | not in the goods or trades; nets and boats deferred (economy_later.md) |
| pots, a firing pit, clay, pottage | the same commit | my own example in knowledge.md (4fcec07, 23 Oct: "pots: clay and fuel, fired in a pit or a kiln") turned into world content | pottery deferred: "pottery jars never win" (economy_later.md, resources_and_goods.md) |
| baskets, withies | the same commit | invented for the slice | none; baskets did nothing in any run |
| hunting, felling, reaping as restricted crafts (only some households) | the same commit | to make leverage between two households (scenario_design: restricted access) | D2-43 (decided 23 Oct 02:59, an hour later): **basic, everyone knows them** |
| bread from 2 grain doubling the food (grain half a meal) | the same commit | invented | D2-44: porridge needs only a hearth; 10 flour make 11 bread |
| an axe, a sickle, a fishing line as separate tools | the same commit | invented | D2-23: one hand-tool good with grades (single-use tools rejected) |
| gleaning | the same commit | invented | not in D2-43 |

None of it was written in a proposal or the spec, and it was not reconciled when D2-23, D2-43 and D2-44 were decided, so runs B, C2,
C0 and D ran on it. **Removed on 23 Oct** (this commit): M1 now uses the decided set (forage, hunt, fell, reap for everyone; one
hand-tool good, crude or copper, with recipes.md §9's multipliers; porridge, grinding at a quern and bread per D2-44; milking as a
learned technique per D2-42; a crude weapon). Speech had the same fault: D2-7 (22 Oct) already decided the building scope.

**Verbs.** verbs.md (23 Oct) proposed a lean set; M1 built 15 of them plus one it did not have (`learn`, kept so teaching needs both
sides the same day), and has now dropped `build` (its only use was the firing pit): 14. Proposed since but not built: `lend` and
`return` (§3.3). The swelling was in content (13 techniques and 10 goods not in any decision), not in verbs.

## 5. Is one node carrying too much? (Zach)

Millbrook has five kinds of land (field, pasture, forest, brook, meadow) and the green. A lowland village with its fields, common,
wood and water within a day's walk is realistic, and D4-11's node scale allows it. What was too much was the trades: every craft
the world had sat in one hamlet, so nothing would ever need another node. In the decided design trades sit at different places
(recipes.md §5 names them: a trapper at Ashwood, smiths at Coppergate and Millford), which is what makes nodes trade (04 §: node kinds
as comparative advantage). After the removal, Millbrook has only the basic set and milking: little leverage at one node, which is
the honest state of a single village under the decided economy. Leverage for single-node tests should come from holdings (the one
copper tool, the cows in milk, fields held by a household under D4-23), not from inventing trades.

## 6. Check run after the changes (23 Oct)

`runs/m1_E_check`: the founders village, 4 days, after D4-25 to D4-29 and the re-based economy. $0.76 (the same village cost about
$1.30 for 4 days before). Sessions: 12 started, 27 continued, no fallbacks; 75% of input tokens read from the cache (runs A-D:
about half, the rest written and never reused). Woken: only agents told or offered something directly (2-4 a day, not all six).
Speech: 21 of 23 `say`s were in a house. Morning messages about 2.6k characters (run D: 7-16k). Written memories are specific and
useful (Agnes: "when I went to store the grain, none was in my hands... if it isn't there, the debt may still stand and I should ask
her gently"). Thinking: on every call except one Sonnet call; text withheld by the CLI.

## 7. Run F: the village on the new systems (23 Oct)

`runs/m1_F`: the generated village (m1_village_s8: 12 people in three houses, 4 Opus, 7 Haiku, a child), 10 days, after D4-25 to
D4-30 and the decided economy. **$3.83** (run D, the same village before: $7.13). Everyone lived; no missed meal.

| System | Result |
|---|---|
| Sessions and cache | 44 conversations started, 245 calls continued, no fallbacks; 83% of input read from the cache for both models; Opus $3.57, Haiku $0.26 |
| Thinking | withheld thinking blocks on 233 of 256 calls (the CLI does not return the text) |
| Waking | 8 to 11 of 11 woken every day; half needed a second wave. 290 tells, **180 of them within the speaker's own house** (often repeating what was just said in the house) |
| Speech scopes | 117 to everyone, 74 in a house |
| Morning messages | grow from 1.1k to about 9k characters by day 9; most of it is "What happened yesterday", i.e. the town's 117 broadcasts heard the next morning |
| Written memories | 33 of 33 asked for were written; specific (store counts, trades, who owes what) |
| Said and did | the debt was right this time: Piers gave 3 grain on day 3, Hamo confirmed it paid, both records agree |
| Notes | Haiku 19 written, 47 pins; Opus 20 written, no pins |
| Rejections | 80 of 1,178 results (7%) |

Faults found and fixed after the run: **milking could never happen** (the world dropped the herd's cows in milk; one attempt, refused;
a test now covers it); `pin` given a note's text instead of its title was refused six times (it now pins the note written in the same
reply). Behaviour: foraging 227 of 600 planned acts, hunting 71, reaping 34, felling 32; 5 trades and 6 gifts across houses; Hamo
ended with 28 timber and 10 grain. Open for Zach: whether a tell to one's own household should wake (house speech already reaches
them), and whether the town's broadcasts should be capped or summarised in the next morning's message.

## 8. Speech limits: cybertron 1 against M1 (run F)

| | cybertron 1 | M1 (run F) |
|---|---|---|
| Private | `dm`/`reply`, free in the DM step but rationed: 3 a round plus a personal jitter (mostly 3-6), hard cap 10 (`base.yaml:11-19`); replies count against it; 2 reply waves | `tell`, free, 3 a reply, no daily ration; 2 waves, so up to 9 a day; mean 2.6, most 8 |
| Public | `post` **costs one of the agent's 3-7 actions**, arrives next round, clipped to 100 tokens in others' feeds (DMs 400) (31_institutions/04_information.md:10-14) | `say` to everyone or in a building, free, 3 a reply, heard the next morning, up to 600 characters |
| DM share (DMs ÷ all messages) | Millbrook 0.84 (577 DMs, 106 posts); target ≤ 0.7 (04_information.md:450) | 0.60 (290 tells, 191 says) |
| Extra calls from talk | Ashwood: 595 DM-reply calls to 713 decisions, 0.83 a decision (20_memory_and_prompts.md:119, 357) | 146 talk calls to 110 decisions, 1.33 a decision (no ration) |

What cybertron 1 found: coordination ran through DMs and the square while most channels went unused; a council chamber stayed at
0 posts while its members exchanged 63-108 DMs; the one hall that worked carried one order a round to many (04_information.md:15-19);
long runs' public posts collapsed from 30-120 per 40 rounds to 0-6 (36c_first_batch_log.md:236); a ritual hashtag post by about
40 of 100 agents that never did anything (14_state_of_nature.md:35); broadcast by identical DMs; and DM-reply calls that shared no
cached prefix, 72% of a run's cost in cache writes never read (20_memory_and_prompts.md:32) — the fault M1's sessions now avoid.
No review reports agents hitting the DM limit; halving the reply waves (cutting about 30% of calls) was considered and not done
(36b_first_batch.md:292).

## 9. Run G: the ration and the cost of speaking (D4-31)

`runs/m1_G`, the same village and seed as run F. $3.54 (F $3.83).

| | F | G |
|---|---|---|
| says a person a day; public share of messages | 1.74; 0.40 | 0.08; **0.04** |
| says to everyone / in a building | 117 / 74 | 9 / 0 |
| tells a person a day; within own house | 2.64; 62% | 2.13; 71% |
| person-days that used their last private message | 0 | 17 (none refused) |
| woken a day; talk calls a decision | 9.8; 1.33 | 9.5; 1.31 |
| words spoken a person a day | 126 | 67 |
| morning message, days 2 / 5 / 9 | 2.9k / 5.6k / 9.0k | 2.3k / 4.2k / 4.4k |
| milkings (the fix after F) | 0 | 22 |

A unit of work for each say all but ended public speech (DM share 0.96 against cybertron 1's 0.84 and its own ≤ 0.7 target); the
ration bound on 17 person-days but refused nothing; waking did not fall, because 71% of tells go to one's own household.
