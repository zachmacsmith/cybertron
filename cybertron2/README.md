# cybertron2: the engine on a graph of places

A new engine, in its own package, built because space touches every physical act of the old one (docs/review/38_space_engine/
00_plan.md). It is small (about 1,600 lines), has no replay obligations yet, and imports only one module of the old engine (the
LLM backend `cybertron.llm`). Status, decisions and next steps: [docs/review/38_space_engine/README.md](../docs/review/38_space_engine/README.md).
What has been ported from cybertron 1: [docs/review/38_space_engine/porting.md](../docs/review/38_space_engine/porting.md).

## Run it

```
python -m cybertron2 run cybertron2/specs/hills_and_forest.yaml --out runs/cybertron2/<name> [--rounds N] [--bots]
python -m cybertron2 report runs/cybertron2/<name>
python -m pytest tests/test_cybertron2.py
```

- Models are called through `claude -p` on the subscription (`LLM_BACKEND=claude_code`, the default here) or the API
  (`LLM_BACKEND=api`). One call per living agent per round, in parallel.
- `--bots` replaces every model with a scripted bot: a smoke test (determinism, no crash), not evidence about behaviour.
- `runs/` is git-ignored; copy a run you want to keep under `docs/review/38_space_engine/runs/` (check it for session ids first).
- Publish runs to the Hugging Face dataset, in their own folder marked experimental (`experimental/cybertron2/`, out of the
  catalog): `python -m cybertron2.publish_hf RUN_DIR... [--push]`. It redacts this machine's ids, runs the privacy gate, and
  uploads only with `--push` and a write token in `HF_TOKEN`.
- Cost seen: about $0.09 a round for 8 agents (2 Opus, 3 Sonnet, 3 Haiku), about $0.19-0.22 for 11 (3 Opus, 4 Sonnet, 4 Haiku).

## Modules

| Module | What it holds |
|---|---|
| `world.py` | the state (`World.s`, plain JSON), the spec loader, physics defaults (`PHYSICS`), reads (who is where, shelter, words for what people see), and the end of the round: hunts, fights, regrowth, hearth, ration, hazard, the cold, spoilage, breaks |
| `act.py` | every action, each checked against where the agent is; each returns the agent's result line and what others present see |
| `combat.py` | raids on house stocks and attacks on people, settled at night against whoever is at the place (a simplified port of the old harm model) |
| `perceive.py` | each agent's knowledge store: what it saw where, who it saw how, its house as last seen, witnessed acts, testimony, the memory bands and lasting memories |
| `prompt.py` | the system prompt (fixed per run) and the turn prompt in sections (Here, Seen last round, You, Your house, Elsewhere, Lasting memories, Earlier rounds, Last rounds, Notes); the reply schema |
| `run.py` | the round loop, model calls, the scripted bot, logs, the CLI |
| `report.py` | a run's summary from its logs |
| `specs/` | `forest_households.yaml` (run 1: two households, three places), `hills_and_forest.yaml` (run 2: three households, five places, raiders) |

## A round

1. Every living agent observes where it is (`perceive.observe_all`) and decides from the same state: one model call each, in
   parallel. The reply: `why` (a few sentences), `actions`, `say`, `tell`, `note`.
2. The plans run interleaved: one action from each agent in turn, in an order shuffled per round from the seed. An attack or a raid
   takes two of an agent's actions. After every step everyone observes again and witnesses what was done where they stand.
3. Speech is delivered to whoever is at the speaker's place when the round ends (`say` to all there, `tell` to one).
4. The night (`World.end_of_round`): hunts, fights, regrowth, the hearth, the ration, the starvation hazard, the cold, spoilage,
   house breaks. Those present witness the night's fights, deaths and breaks (`perceive.night`).
5. Each agent's round moves into its memory (`perceive.close_round`): the full band (last 2 rounds) and a one-line summary.

## State (`World.s`)

`round`; `nodes` (name, text, plants {S, K, K0, r, yield, refuge}, game {G, K, r, inflow}, timber, copper, forge); `edges`;
`agents` (household, house, model, role, aim, at, holdings {food, timber, copper, blade, crude}, stage, missed, frailty, attack,
defence, cannot, alive, notes); `houses` (node, household, beds, condition 2/1/0, stock, work); per-round `hunts`, `fights`,
`guards`, `gathered`; `know` (the knowledge stores); `gifts`; `log` (the end-of-round records).

## Conventions

- **Randomness:** `World.rng(*parts)` seeds `random.Random("seed|stream|round|who")`, so a draw depends on the seed and the round,
  never on call order (the old engine's rule). Scripted runs are byte-identical across repeats (tested).
- **Presence:** every physical act checks the agent's place. Nothing is global except the calendar and the rules.
- **Knowledge is written by the engine,** at the moment of observation; the model's own notes are separate.
- **Quantities shown to agents are rounded down** (`world.show`), so any amount an agent reads is there to use.
- **No defaults are frozen yet.** When a cybertron2 run first matters for a result, start versioning (as `cybertron/provenance.py`).

## Known gaps

- No institutions, laws, contracts, births, farming or money yet (porting.md, "Not yet ported").
- Context budgets are line caps, not token budgets; no look-ups or `recall`.
- Winter is a scripted list of cold rounds (`cold_rounds`), waiting for a calendar.
- Speech is face to face and arrives a round late; there is no in-round talk step (run 1's hunting parties failed on this).
- The reply field must not be called `reasoning`: with these prompts the Sonnet 5.5 safeguard refuses it (review 38.02 §9).
