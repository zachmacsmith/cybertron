# Engine gaps: things the benchmark societies need that the engine may not have

A tracker, not a plan: nothing here is being built yet. Started 22 Oct 2026 while designing review 36's societies. Each row says
which society or measure needs it, what exists today, and a rough size (S ≤ 1 day, M 2-4 days, L more). "Verify" means the claim
comes from the design docs and has not yet been checked in the code. Add rows as they come up; mark rows done with the commit.

| # | Gap | Needed by | What exists | Size | Status |
|---|---|---|---|---|---|
| G-1 | **Acquaintance / locality**: who can DM whom (household, unit, ward, guild, a few outsiders), new ties formed by meeting, introductions | every society above ~40 agents; S7-S10 | anyone may DM anyone; DM limits by law (`set_dm_limit`) cap volume, not reach | M | open |
| G-2 | **Sibling polities at round 0** (several jurisdictions with their own institutions, a league above them, movement between them) | S10, W6, W8 | jurisdictions exist (found, join, leave, `on_exit`); seeding several at start: verify (29b says W6/W8 need it, "WP-I") | M | verify |
| G-3 | **Laws of one institution that read or move another's** (guild courts, league over polities, a council taxing a guild) | S8, S10, S5 | laws read each other's public records (`public_of`) only within limits; Cooperative finding: one institution's laws cannot read or move another's | M | open |
| G-4 | **Orders as first-class objects**: an order from an office to a person, accepted or refused, logged, with a deadline | directive probes, compliance metric, S3, S7 | an order is a DM; adherence is guessed from duty text (positions will compile duties to DUE items) | M | open |
| G-5 | **Restricted reading of law and archive** (only interpreters or scribes may read the canon or the tally) | S6, S7 | `read_law` is open to all; documents and literacy prototype on `wp/documents` (review 32) | S-M | verify |
| G-6 | **Inheritance of offices and positions to heirs; children's positions and goals** | S1, S7, S9, long runs | Life: lifespans, pairs reproduction, heirs inherit holdings; Board succession; office succession by rule (election, appointment); hereditary succession: verify | M | verify |
| G-7 | **Marriage / alliance rules** (who may pair, which clan the child joins) | S1, S9 | pairs reproduction (cap 3N) | S-M | open |
| G-8 | **Scripted outside actors**: raids every N rounds, a distant crown or board that writes and acts, an outside market with prices | S3, S4, S5 | legacy tribute-demanding outside power (grand35); scheduled interventions can inject events | S-M | verify |
| G-9 | **Reactive residents**: rule-based agents (work, eat, pay, comply or refuse by what they see: food, fear, pay, their leader) as a mass for 500-agent worlds | S10 at 500 | dry-run scripted bots exist but are not role-aware producers (31.10 §1) | M-L | open |
| G-10 | **Seasons**: harvest cycles so food binds in some rounds only | long runs | blights and scheduled shocks; constant yields otherwise | S | open |
| G-11 | **Memory over 100+ rounds**: plan persistence, summaries that keep long-term aims | long runs | notes, memory_text v2, conversation restarts every chunk | ? | measure first (36 §2.6) |
| G-12 | **Arrivals and departures on a schedule** (traders who come and go) | S4 | `add_agent` / `remove_agent` intervention ops | S | exists as ops; needs a schedule template |
| G-13 | **Two-key armoury** | S2, S8, robust variants | not built (29b S4); Armoury Act with keys on the force branch: verify | S | verify |
| G-14 | **Associations with their own lands, stores and courts** (clans, guilds) | S8, S9 | associations own treasuries and channels; camp rights are personal, not institutional (31.02) | M | open |
| G-15 | **Indenture / status classes that change over time** | S5 | rights by class and office; time-limited contracts | S | open |
| G-16 | **Bench runner**: shared prefix, set-up manifest, conditional end-state forks, global concurrency cap across runs | the batch | `cybertron fork --at --apply --replicates`; no runner (29b §6) | M | open |
| G-17 | **Control Share and milestones** in the index (arenas, de jure / de facto readings) | 36 §2 | `analysis/takeover.py`: bloc, C1-C11, AXI, G0-G4, procedure probe | M | open |
| G-18 | **Interview safeguard misses** (Haiku 5.5 blocked interviews of an agent with an uprising goal) | loyalty metric | interview tool; failures not always loud | S | open: report missing interviews with the agent's goal |
| G-19 | **Bare-class `set_procedure` shadowed by `statute:` keys** (29c): a capture law can be silently inert | every takeover world | loud reporting added; behaviour unchanged pending Zach's decision (threads) | S | decision pending |
| G-20 | **Engine performance at 150-500 agents** (DM step, feeds, checkpoint size) | S9, S10 | haiku100 pilot (100 agents, 30 rounds) exists | ? | measure |
| G-21 | **Positions** (identity, duties as DUE, secrecy) | every society; removes the "Worker" confound | being built on `wp/positions` | — | in progress elsewhere |
| G-22 | **Temperament and values (HEXACO, Schwartz)** with population-level distributions | temperament factor | legacy traits, `personality.explicit` per agent; brief in review 34 | — | in progress elsewhere |
| G-23 | **Spatial layout** (wards, distance, movement cost) | S8-S10 | review 17 design; verify what is built | ? | verify |
| G-24 | **Ideology / doctrine as an object** (a canon text whose interpretation is ruled on and binds) | S6 | laws and the archive; nothing that binds interpretation | M | open |
