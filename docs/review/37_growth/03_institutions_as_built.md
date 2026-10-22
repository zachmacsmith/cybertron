# 37.3 as built: institutions acting on each other

*22 Oct 2026, branch `wp/inst-cross`. Brief: [03_institutions.md](03_institutions.md). Decision record:
[devlog_37.3.md](devlog_37.3.md). Closes gap G-3 (docs/engine_gaps.md).*

## What was built

One module, `cybertron/cross.py`, behind the opt-in key `institutions.cross` (off by default; listed in `cybertron/schema.py`
OPT_IN, so no instance's frozen settings change). It needs law.v2.

1. **A permission model.** An institution holds a power over another only by a grant inside an *instrument*, and every
   cross-institution call names the power it uses. There are three kinds of instrument, stored as one record kind:
   - **charter**: a parent charters a child. `powers` are what the parent holds over the child; `child_powers` what the child holds
     over the parent. One parent at a time.
   - **treaty**: two institutions grant each other named powers.
   - **membership**: a member grants a league powers over itself.

   An instrument comes into force once both parties consent. The offering law consents for its own institution, and the other
   party's law calls `accept_instrument(id)`. Instruments declared in the spec are initial conditions and are in force at round 0.
   Any party may end an instrument (`end_instrument`), so exit stays free. An instrument with a dissolved party grants nothing.

   The powers are **read**, **levy**, **pay**, **appoint**, **remove**, **enact**, **veto** and **seize** (land, for the
   coordination board's loop 2). Levy and pay can be limited to an item and a quantity per period.
2. **A gated law API** (the module "cross" rows of `cybertron/lawapi.py`, documented in `cybertron/lawdocs.py`). A call made
   without the matching grant returns False (`state_of` returns None). The reason is reported in world terms ("J0 (the Council)
   holds no power to levy on the treasury and stores of A1 (the Weavers) (the charter C1 ended in round 2)"); it goes to the
   law's author and officers as a `cross_refused` event and as a `law_call_failed` record where `law.call_failures` is on.
   Every use of a power is a public `cross_act` event naming the instrument and the power, so capture of one institution by
   another can be measured from events.jsonl.
3. **Hierarchy.** A charter from a polity to an association incorporates the child while it is in force: the record's `parent`
   is set, and the W8e machinery (cybertron/incorporation.py) makes the parent's laws see the child's acts, outrank its
   bylaw-rank code and decide conflicts by the parent's rule. Ending the charter clears `parent`. `enact_in` puts a law straight
   into a child's code, past the child's own procedure.
4. **Templates** (library family `cross`, listed by read_library and the catalogue only where `institutions.cross` is on):
   - **Charter**: the parent's copy offers it, the child's copy accepts it, and repealing either copy ends it.
   - **Treaty**: the first party's copy offers it, the other party's copy accepts it, and repealing a copy withdraws from it.
   - **Guild Levy**: a parent's statute that each period levies a share of a guild's treasury or store within the charter's
     limit, keeping a public register. It takes nothing once the charter ends.
5. **The raid is closed under the flag.** With the flag off, and as before, a J0 law in a world without jurisdictions can
   `move("assoc:A1", "reserve", ...)` out of an association's treasury with no check. With it on, a law's move out of another
   institution's treasury, store or escrow fails ("assoc:A1 belongs to A1 (the Weavers), not to J0 (the Council): a law takes from
   another institution only with a power it holds") unless `levy_on` or `pay_out_of` is making the move under a held grant.
6. **Land and labour** (review 37 coordination board, loops 2 and 4):
   - `grant_plot` hands a fields plot the institution holds to an agent or an institution as a tenure, through the routed
     `set_farm` give, with optional service terms.
   - `seize_plot` takes back a plot the institution granted, or one held by an institution it holds `seize` over.
   - `demand_service` demands harvest, sow, tend or reap work of a member (when the institution holds `compel_members`) or of a
     holder of its land. The work is counted from the routed changes the agent then makes. Each action counts 1, or 37.1's
     `labour(agent)` once that exists on the engine side.
   - A demand that is short at its deadline is recorded as missed, and `service_owed` lets a law enforce it.

## Spec syntax

```yaml
law: {v2: true}
institutions:
  unified: true          # recommended (offices: grants; appoint/remove need offices)
  grants: true
  cross: true            # the API only; or, with instruments in force at round 0:
  cross:
    instruments:
      - kind: charter
        id: C1                                   # optional (default C1, C2, ...; T<n> treaties, M<n> memberships)
        name: Charter of the Weavers             # optional
        parent: J0
        child: A1
        powers: [read, {power: levy, item: penny, qty: 4, every: 1}, appoint, remove, enact, veto]
        child_powers: [read]                     # optional
        incorporate: true                        # default: a polity's charter of an association incorporates it
      - kind: treaty
        parties: [A1, A2]
        grants: {A1: [read], A2: [veto]}         # holder -> powers over the other party
      - kind: membership
        league: A3
        member: A2
        powers: [remove]                         # what the league holds over the member
```

`python -m cybertron spec check` reports a bad shape (an unknown power, limits on a power that takes none, a treaty without two
parties, cross without law.v2). A name that does not resolve fails the run before round 1.

The law calls, as a law of the acting institution writes them:

| Call | Power | Effect |
|---|---|---|
| `powers_over(iid)`, `instruments()` | none | what this institution holds; its instruments with their status and grants |
| `state_of(iid)` | read | members, treasury, stores, offices and laws of the other (None without the power) |
| `levy_on(iid, item, qty, store=None, into=None)` | levy | up to qty from its treasury or one of its stores, into ours or one of our stores, within the limit; returns what was taken |
| `pay_out_of(iid, to, item, qty)` | pay | from its treasury to an agent, an institution or a store |
| `pay_into(iid, item, qty)` | none | from our treasury into its treasury (polities cannot otherwise name another treasury) |
| `appoint_to(iid, office, agent)`, `remove_from(iid, office, agent)` | appoint, remove | through `institutions.reseat` (an association's officers must be its members) |
| `enact_in(iid, code)` | enact | a law in force in its code at once (an association: rank bylaw, within its law limit) |
| a `before_<change>(p, chain)` hook | veto | the holder's laws see the other's own changes (a payload naming it, its treasury, stores or office rights) and block them like anything else |
| `offer_charter(child, powers, name, child_powers)`, `offer_treaty(other, give, take, name)`, `offer_membership(league, powers, name)` | none | an offer; in force once the other party accepts |
| `accept_instrument(id)`, `end_instrument(id, reason)` | none | consent; revoke, withdraw, leave or decline |
| `grant_plot(camp, plot, to, service)`, `seize_plot(camp, plot)`, `tenures()` | seize (for another institution's plot) | tenures |
| `demand_service(agent, work, qty, camp, rounds)`, `service_owed(agent)` | members (compel_members) or tenants | labour service |

The structural calls have distinctive names on purpose. lawlang classifies a law by the names it calls, so short names like
`levy` or `appoint` would have made existing laws that define helpers of those names structural (the library's Guardianship
defines `appoint`) and changed old worlds.

## How it appears in agent prompts

Off: nothing, byte for byte. On, each agent gets one state line per instrument that concerns it: it is an officer of either
party, or a member of a party other than J0 (J0's members are everyone when jurisdictions are off). It also gets a line per
tenure it holds and a DUE line per open service demand. From the dry run, Bo's turn in round 3 (about 120 tokens for the four
lines):

```
Charter C1 'Charter of the Weavers' between J0 (the Council of Ashby) and A1 (the Weavers' Guild). J0 over A1: read records, levy up to 4 penny a round, appoint officers, remove officers, enact laws (laws use these powers: read_law for the calls).
Treaty T1 'Treaty of the Vats' between A1 (the Weavers' Guild) and A2 (the Dyers). A1 over A2: read records; A2 over A1: veto acts (laws use these powers: read_law for the calls).
You hold camp8 plot 1 of J0 (the Council of Ashby), owing service when it demands: harvest 2 time(s) a round; it may take the plot back.
DUE: service to J0 (the Council of Ashby): harvest 2 more time(s) by the end of round 3.
```

An instrument on offer reads `..., offered by J0. A2 over J0: read records. In force once A2 accepts by a law calling
accept_instrument("T1").`

The law calls are listed in the system prompt's law section under "Institutions:" (law_docs preset core). The land and labour
calls go into the codex article `codex/law/cross`. The events read in world terms in the feed, for example:
- `J0 levied 4 penny from A1 under C1 (law L10)`
- `A2 vetoed A1's move (the Dyers forbid the Weavers' great payments) under T1`
- `Charter C1 between J0 and A1 ended (J0 ended it: the guild defied the council)`

## Dry-run evidence

No model calls were made. Two kinds of check were run with scripted bots.

**Guild Town** (`cybertron/specs/cross/guild_town.yaml`, schedule `cybertron/specs/cross/guild_town_dryrun.yaml`; 8 residents,
8 rounds):
- The cast: J0 the Council of Ashby (granary, two plots); A1 the Weavers' Guild, chartered by the council (C1: read, levy up to
  4 penny a round, appoint, remove, enact); A2 the Dyers, who hold a veto over the Weavers by treaty (T1); A3 the Wool League,
  of which the Dyers are a member (M1: remove).
- The schedule stands in for the laws the institutions' members would pass, round by round.
- Command: `python -m cybertron run cybertron/specs/cross/guild_town.yaml --dry --apply cybertron/specs/cross/guild_town_dryrun.yaml`

| Round | Act | Result |
|---|---|---|
| 1-4 | the Guild Levy (10% of the guild's purse, cap 4) | 4 penny each round, logged `cross_act levy` under C1; the register reads 4, 4, 4, 4 |
| 2 | the guild's law takes grain from the council's granary, coin from its treasury, and grain by a raw move | `levy_on` False, `pay_out_of` False (no charter, treaty or membership grants it), the move refused; granary untouched |
| 2 | the guild pays its head 15 penny | blocked by the Dyers' Embargo under T1 (`cross_act veto`); Ada holds 0 |
| 3 | the council reads the guild's books and grants Bo a plot for harvest service | `state_of("A1")` returned the treasury; `state_of("A2")` None (no read power); plot camp8/1 held by Bo; service W1 demanded |
| 3 | Bo, a scripted bot, harvests once | W1 missed at round end (1 of 2), `service_missed` to Bo and the council's officers |
| 4 | the council deposes the guild's head | Ada removed and Di seated (`cross_act remove`, `appoint` under C1) |
| 4 | the League removes the Dyers' master and tries to seat Fay | removal done under M1; seating refused (no appoint power); the office's own succession then seated Fay |
| 5 | the council revokes the charter | C1 ended; the guild is no longer incorporated; the levy register reads "no levy power over A1" from round 5 to 8 |
| 6 | the council tries to restore Ada, raid the purse and levy again | all three refused, each with its reason ("the charter C1 ended in round 5"; "assoc:A1 belongs to A1 ...") |

Totals from events.jsonl: 13 `cross_act` (5 read, logged for the monitor only after this run; 4 levy, 2 remove, 1 appoint, 1 veto) and 6 `cross_refused` (2 levy, 1 pay,
1 read, 2 appoint). End state: the guild's purse went from 60 to 44 (4 x 4 levied, nothing after the revocation); C1 ended, T1
and M1 in force.

**Off is byte-identical.** The March (`cybertron/specs/bench36/march.yaml`, 3 rounds, dry, seed 0) was run on `bench/first-batch`
(d9acf18) and on this branch. events.jsonl (999 lines), turns.jsonl, interventions.jsonl, snapshots.json, ground_truth.json,
every prompt file and every agent transcript are identical. calls.jsonl differs only in the recorded latency. The golden and
history-replay tests pass as before.

**Tests:** `tests/test_institutions_cross.py` (13 tests) covers:
- the brief's acceptance checks: the council levies the guild only while the charter grants it, and revoking it stops the levy
  (directly, and through the Guild Levy template over four rounds with a revocation in round 3); the guild cannot touch the
  council's store without a power, and can once a treaty grants it; a league court's ruling binds a member's office (and binds
  nothing without the membership);
- incorporation, `enact_in` and `state_of`; veto by another association's hook; the templates; tenures and service;
- the prompt lines and who sees them; the spec check; the flag off.

## Limits and open points

- **A league court must be a polity's.** Associations cannot declare court clauses: `clause` is in the contract column's deny
  list. So the acceptance test's league court is J0's court ruling on a member association's office. A league of polities needs
  jurisdictions on and sibling polities (G-2).
- **A child's own laws can block a levy** its charter allows: the levy is a move out of its treasury, and its laws see that.
  Defiance is then visible (`cross_refused`, "the levy was blocked"). I kept this as physics rather than exempting levies from
  hooks; see Q1 in the devlog.
- **`burn` from another institution's treasury** is not closed by the flag (only moves are); no library law does it.
- **Reads are logged for the monitor only** (the Guild Levy reads the guild's books each round; a read changes nothing).
- **Instruments and service demands are module records, not routed primitives**: nothing can hook an offer or an acceptance yet
  (a constitution cannot forbid its guilds' treaties). They are listed in `primitives.LAW_OUTPUTS` / `OUTPUT_EVENTS` with that
  reason; see Q5 in the devlog. What they lead to (moves, office rights, enactments, plots) goes through those changes'
  primitives and their hooks.
- With jurisdictions off, J0's laws already see every change, so a veto matters most for associations' laws and for polities
  with jurisdictions on.
