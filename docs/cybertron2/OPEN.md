# cybertron2: open questions and conflicts

Each item has an owner (README "Who owns what") who resolves it, with Zach where it needs a decision. Resolved items move to
[DECISIONS.md](DECISIONS.md) or into the spec, and are struck through here. Compiled 22 Oct 2026.

## Conflicts between documents

| # | Conflict | Where | Proposed resolution | Owner |
|---|---|---|---|---|
| C-1 | Carrying capacity: on foot 20, pack 35, animal +60, cart +150 | 38.06 §3 vs 02g §3 (on foot 10, pack 20, pack ox 60, handcart 40, ox cart 200, wagon 500, boat 1,500) | take 02g's numbers (calibrated against grain's cost); 06's table superseded | 37.2 (numbers) |
| C-2 | Building limits: slots by land kind | 38.04 §1 vs 02e §3.9 lots, 02i parts | lots and slots are the same thing (land per node, by kind); parts decide what a building does | 37.4 with 37.2 |
| C-3 | Speech at a node: one talk step | 38.05 §1 vs 02h §4a (the square, rooms by access, private messages) | the talk step delivers in 02h's three scopes | 37.4 |
| C-4 | Letters and channels | 38.05 §5 (letters, errands) vs 02h §4 (channels with a medium and a location; boards, carried editions, boxes) | letters and boards first, on 02h's channel record; editions later | 37.4 with 37.2 |
| C-5 | Riders who travel and strike in one round | 02g §5b vs D4-8 (arrive, then decide) | a fuse event (02k): riders shorten detection to almost nothing, so no exception to D4-8 is needed | 37.4 (Zach to confirm) |
| C-6 | Danger on the road | 38.05 §2 (a risk draw per night) vs 02g §3b-3c (danger per edge by terrain and season, per rung) | 02g's table as the draws of the 37.4 scheduler | 37.4 |
| C-7 | The handoff README's next steps and document list | 38 README §2, §7 | superseded by this folder; README gets a pointer | 37.4 |
| C-8 | Environment design for the old engine (calendar, micro-events, foresight) | `wp/environment`: 04_environment_design.md, cybertron/environment.py | redesigned for cybertron2 in spec/environment.md; the old branch marked superseded | 37.4 |
| C-9 | Ages: calendar years | 38.09 §2a-2b vs D4-19 | D4-19 wins | 37.4 |

## Open questions

| # | Question | Where | Owner |
|---|---|---|---|
| Q-1 | Work units a day and the cost table (by experiment) | 38.06 §3, D4-17 | 37.4 |
| Q-2 | Overexertion costs (x1.5, x2, exhaustion) | 38.06 §3 | 37.4 |
| Q-3 | Talk-step waves (one or two) | 38.05 §8 | 37.4 |
| Q-4 | Year length in days; season lengths | 38.05, D4-13 | 37.4 |
| Q-5 | Rounds a youth lasts; lifespans in rounds | 38.09 §4 | 37.4 (37.1) |
| Q-6 | Settlement limit: a hard cap or a crowding cost | 38.04 §7 | 37.4 |
| Q-7 | First land kinds (proposed: river valley, woodland, hills, crossroads) | 38.04 §7 | 37.4 |
| Q-8 | Which signs, incidents and eras first | 37.4 environment | 37.4 |
| Q-9 | 37.2's open decisions in 02f §6, 02g §7, 02h §9, 02i §8, 02j, 02k | those notes | 37.2 |
| ~~Q-11~~ | ~~Who holds a plot; can plots be split; the minimum plot size (37.1's question)~~ resolved by D4-23 (spec/world/holding.md) | board | 37.4 |
| Q-10 | The first LLM world for M1 (a small version of 02f §4's region) | 38.08 §2 | 37.4 with 37.2 |
| ~~Q-12~~ | ~~Decisions made with 37.2 that belong in 37.4's spec areas and are not yet written there (staleness check, 23 Oct): D2-5 (fuse events, gates), D2-21 (the watch), D2-22 (any party may raid a node), D2-50 (fire kills), D2-51 (burn orders in a raid) for `spec/conflict/`; D2-8 (wide reach costs more) for `spec/information/`. Drafts: proposals/fuse_events.md, gates.md, attacks_and_walls.md, information_economics.md~~ written 23 Oct: spec/conflict/combat.md, raids.md, defence.md; spec/information/letters_and_documents.md (with perception.md, prompts.md; H-1 to H-4, H-7 also placed) | DECISIONS.md | 37.4 |
| Q-13 | D4-37 (whoever is owed may release a debt; gives and leaves to the creditor are credited) belongs in `spec/economy/agreements.md` (37.2's file): Settlement and What agents see. Built in cybertron2/engine (`release`, the credit hook) | DECISIONS.md D4-37 | 37.2 |
