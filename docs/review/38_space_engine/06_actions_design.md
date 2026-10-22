# Review 38.06: what agents can do (actions, the day's budget, standing orders)

*22 Oct 2026, 37.4 session, with Zach. Design only. cybertron 1 has 145 actions (`cybertron/action_registry.py`, as of
`bench/first-batch`); cybertron2 has 15 (`cybertron2/act.py`). This lists them all, says what each becomes on a graph of places,
adds what space needs, and proposes how many an agent gets a day and what runs without a decision.*

## 1. Every action so far, and what it becomes on nodes

Treatments: **here** (needs the agent at the right node, and often at a site: witnessed by those present); **seat** (done at an
institution's seat, or remotely through a proxy or a letter); **letter** (crosses distance only as a carried item); **free** (no
action used: reading, notes, look-ups); **role** (only for a role that may not exist in cybertron2); **drop** (a mechanic left
behind: 00_plan §3).

| Group | cybertron 1 actions | cybertron2 now | On nodes |
|---|---|---|---|
| **Talk** | dm, reply, send, post, anon_post, create_channel, channel_post, add_member, remove_member, close_channel, open_channel, set_channel, join_channel, leave_channel | say, tell (free, heard at round end) | **free, here**: talk in the talk step to people at the node; **post** becomes a notice at the node (a board, a proclamation); groups are people who meet; channels across nodes only as **letters** or carried papers |
| **Give and trade** | transfer, reply-with-payment, standing_order | give, store, take | **here**: give, offer/accept (05 §4), store and take at one's house; standing payments as standing orders (§3) |
| **Produce** | harvest (dial camps), hunt, farm, tend, improve, practice, clear, build (store), withdraw, survey, invest | forage, hunt, fell, mine | **here, at a site**: forage, hunt, fish, fell, clear, drain, quarry, mine, herd, sow, tend, reap, improve; survey and invest kept for sites; the dial camps **drop** |
| **Make** | forge, craft, fortify, write_edition | forge, craft | **here, at a workshop**: forge, craft, and 37.2's recipes (cook, preserve with salt, tan, weave, build gear); fortify becomes building a wall |
| **Build and keep** | build (store) | repair | **here**: build any building on a free slot (house, store, workshop, inn, mill, hall), work on it over days, repair it |
| **Force** | attack, join_attack, watch, guard, contract (assassin), buy_initiative, forge_dm | attack, raid, guard | **here**: attack, raid, guard, join an attack; the assassin and buy_initiative **drop** (role mechanics); forging someone's message becomes forging a letter (**letter**) |
| **Lineage** | conceive, commission, create_agent, copy_agent, bequest, name_successor | none | **here** for conceive (both present); bequest anywhere (a will, kept at the seat); Makers **drop** |
| **Politics** | propose, amend, vote, veto, patch, rule, request_fix | none | **seat**: proposing, voting and judging happen where the institution sits (its hall), on its days (assemblies, 05 §7), or by proxy or sealed letter; the Board and Fixer **drop** with their roles |
| **Courts** | accuse, respond, appeal, represent, withdraw_case | none | **seat**: at the court's node; a summons is carried |
| **Contracts** | create_contract, join_contract, leave_contract, deposit_escrow, set_allowance, fulfil, propose_contract_change, authorize, revoke_authorization, act_for | none | **here** to sign (the parties present, or a sealed letter as consent); escrow held at a store; authorize and act_for become **proxies** (an absent member acts through one present) |
| **Finance** | lend, accept_loan, repay_loan, extend_loan, deposit, redeem | none | money and credit can be written **anywhere by letter** (a bill), goods only **here**; deposit and redeem at the reserve's node |
| **Jurisdictions** | found, fund, invite, join, leave, declare, set_charter | none | **here** to found and join (people meet); a polity then claims nodes (territorial law, later) |
| **Commons** | contribute, pay_tribute | none | **here**: work on a project at its site, pay tribute where the collector stands |
| **Press** | subscribe, unsubscribe, buy_placement, leak, answer_poll, buy_licence, publish, write_digest, report, annotate, run_placement, poll, set_subscription_fee, send_subscriber_list, revoke_licence, grant_licence | none | papers become **printed items carried** between nodes (later); a notice board at a node now |
| **Information** (free reads) | manual, manual_search, recent, search_board, search_dms, read_law, preview_law, legal_position, recall, read_file, read_archive, search_archive, run_python, read, read_library, read_register, wiretap, dir_* (5) | none | **free**: manual, recall, read_law, legal_position, preview_law; records and registers are **here** (read at the seat, or a copy carried); wiretap becomes reading letters you carry |
| **Memory and files** | write_scratchpad, write_archive, write_file, pin, unpin, rename_file, share_file, delete_file, buy_memory, dir_write, dir_edit, dir_move, dir_delete, dir_grant, doc_send, dir_history | note (free) | **free**: the note; documents as **items** (a deed, a ledger, a letter, a charter) that are held, copied, carried and lost |
| **Camps (dial)** | lease, accept_lease | none | **drop**; leasing a plot or a site stays, as a contract |
| **Powers** | invoke | none | kept: an action a law defined, done where the law says |
| **Rest** | (none) | rest | free |

## 2. What space adds

| Action | Where | What it does |
|---|---|---|
| `travel {to}` | last act of the day | leave for a neighbouring node (05 §2) |
| `offer` / `accept` | here | a two-sided exchange, all or nothing (05 §4) |
| `write {to, text, sealed?}` | anywhere | make a letter (an item) |
| `give ... deliver_to, at` | here | hand goods or a letter to a carrier as an errand (05 §5) |
| `host {guest}`, `welcome {who}`, `lodge {inn}` | here | a night's shelter for a guest (05 §3) |
| `build {kind, site?}` / `work {project}` | here | start a building on a free slot; add a day's work to it |
| `clear`, `drain` | here, at a site | change the land's cover (04 §5) |
| `fish`, `quarry`, `herd` | here, at a site | the kinds' other resources (04 §2) |
| `proclaim {text}` | here | a notice everyone at the node sees, and anyone who arrives while it stands |
| `pack {item, qty}` | here | load goods to carry (carrying capacity, 05 §2; packs and pack animals raise it) |
| `scout` | here | look at what lies along an edge, or for an unknown one (the frontier) |
| `claim {site}` | here | mark land as yours (whether it holds is law) |
| `set {standing order}` | free | §3 |

## 3. The day's budget

**Work units, not a count of actions.** A day has a budget of units; each action costs units by how long it takes; talking,
reading, notes and setting standing orders cost nothing.

| | Proposed |
|---|---|
| Units a day | 6 for an adult |
| Costs | forage, fish, give, store, take, offer, accept: 1; hunt, fell, quarry, mine, craft: 2; forge, a day's building work, clear, drain: 3; travel: whatever is left (it ends the day) |
| Less | hungry -1, starving at most 2 (as built); ill (37.4 micro-events); a minor 3-4 (37.1); an elder 4 |
| More or less by season | daylight: 7 in summer, 5 in winter (so labour is short exactly when the cold needs fuel and stores) |
| Tools | a tool makes its action cheaper or yield more (37.2) |

This replaces the flat 4 actions and the cap of 2 gathering actions a day (both arbitrary). What limits work is then time, place
and stock: you can only forage where you are, as much as the plants give, in the hours you have.

**How limited should agents be?** The constraint should come from the world (time, place, stock, hunger, tools), not from a cap
on the number of moves. Too few units and routine eats the day (run 1: 88% of actions on gathering, walking and storing); too
many and plans grow long, each choice matters less, and output per agent rises faster than the land can bear. Six units with
standing orders for routine (§4) is a starting point to calibrate in the first runs.

### Working late (overexertion)

An agent may work **1 or 2 units beyond its day's budget**, at a cost in food that night: +1 unit eats x1.5, +2 units eats x2 (on
top of the shelter multiplier). Two overworked days in a row leave it **exhausted**: 2 units fewer the next day. It is the tool for
a crunch (the harvest window, winter preparation, a raid) and not a way of life, and it sets an exchange rate between food and
labour that a household or an employer can bargain over.

### Carrying

Only what is carried crosses an edge, so **load** matters (within a node, moving goods between sites is free). Each item has a
weight; an agent on foot carries up to a capacity; a pack, a pack animal or a cart (on a road) raises it. An agent over capacity
cannot travel.

| Item | Weight per unit | | Carrier | Capacity |
|---|---|---|---|---|
| food | 1 | | on foot | 20 |
| timber | 2 | | with a pack (a good: hides and timber) | 35 |
| stone | 3 | | a pack animal | +60 |
| copper | 1 | | a cart (needs a road) | +150 |
| blade, club, tool | 1 | | | |
| letter, document | 0 (no limit) | | | |

Rough guide: a day's food is 1, so on foot a traveller can carry about two weeks' food or about 10 timber. Documents are weightless:
the limit on letters is who will carry them, not their bulk.

### Who gets more

The baseline is the same for every adult; differences come from the person and their tools, not from a class: age (minors and
elders fewer), health (ill, hungry, starving), skills (a practised smith forges for fewer units), tools (cheaper or better yield),
daylight (the season). An institution can still give an office extra standing (an office's powers), but not extra hours.

## 4. Standing orders

What an agent sets once and the engine carries out until the agent changes it. **The agent decides them** (setting or changing one
is free, and they are shown in its prompt every day); the engine only runs them. Three kinds:

| Kind | Example | When it runs |
|---|---|---|
| **Routine** | "each day: forage 2, store what I carry above 2 food, keep the fire" | fills the units the day's plan leaves unused, in order |
| **Reflex** (if this, then that) | "if attacked: fight back" (or flee home, or hand over food); "if my house is raided while I am there: defend it" | at the moment the event happens, during the work step or at night |
| **Fallback** | "if foraging is refused: hunt instead"; "if the buyer is gone: store the goods" | when an action in the plan or the routine is refused |
| **Policy** | "my door is open to the Wynns"; "anyone here may buy blades at 5 food each" (a standing offer); "my household may take from the house stock" | whenever the matching act comes up |

Conditions come from a fixed list the engine can check (attacked, raided, refused, a guest asks, an offer matching these terms,
food below n, a stranger arrives, winter starts), so a standing order never needs a model call to run.

## 5. Being called every day

Proposed for the first runs: **every agent at a node is called every day**, as now. The rest (an agent choosing to let its routine
run for some days unless something happens) is later, and if it comes, **the agent decides it**: "keep to my routine for 3 days
unless someone speaks to me, I am attacked, or a stranger comes". The engine wakes it early only on what it asked for, plus a few
things that always wake anyone (being spoken to, attacked or robbed; a letter arriving; its routine failing). First measure how
often a day's plan differs from the routine; if it rarely does, the saving is large and safe.

## 6. Decisions and open questions

Zach, 22 Oct:
1. **Units a day and the cost table: settle by experiment** (small LLM runs comparing budgets).
2. **Daylight by season: yes.**
3. **Reflexes, fallbacks and policies: later.** Choosing the day's actions is not hard for the agents; routine first. When they
   come, they are agent-owned hooks on the chokepoint (07 §5).
4. **A shop needs a shopkeeper:** goods are sold only by someone present to hand them over.

Open: the carrying weights and capacities above; the overexertion costs (x1.5, x2, exhaustion) to calibrate with the units.
