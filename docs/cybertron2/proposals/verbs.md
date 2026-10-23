# Proposal: the verbs, and what each agent is shown

**Status:** ready for a decision (23 Oct; Zach likes the verb system; its principle is D4-24). **Owner:** 37.4. **Affects:** spec/agents/actions.md, information/prompts.md, conflict/,
institutions/, life/. Builds on [knowledge.md](knowledge.md) and 38.06 (every action of cybertron 1 and its fate).

## Summary

Everything an agent can ever do is **a short, closed list of verbs**, each with exact syntax, always in its system prompt; the
variety lives in their **objects** (a technique, a site, a person, a document, a claim), which are shown by what the agent knows,
where it is, and the offices it holds. Universal verbs, including force, are always shown, so no capability is hidden by omission;
technique objects are shown by knowledge; institutional verbs only to members and office holders. Every refusal says why. The
full possible space and what one agent sees meet in a predictable way: the grammar is fixed and small, the objects are local.

## The possible space and the shown space

| Layer | What it is | Size in the world | What one agent is shown | Where |
|---|---|---|---|---|
| **Verbs** | the closed grammar | about 25 | **all universal verbs** with syntax (about 300 tokens); office verbs only if it holds the office | system prompt |
| **Techniques** | recipes, blueprints, gathering and working methods, animal handling, literacy | hundreds | the names it knows, has a rough idea of, or knows of (with sources), within a budget | system prompt, rebuilt on change |
| **Objects here** | sites, lots, buildings, rooms, people, goods, documents at its node | tens per node | what is at its node and its rooms | turn prompt: Here |
| **Options now** | verb x object pairs it can do today | many | the useful ones and a few near misses, budgeted | turn prompt: Today you could |
| **Duties and requests** | what its offices, debts and others ask of it | few | all, one line each | turn prompt |
| **Full cards** | the detail of any technique, law or claim | | on request (look-up in the talk step) | talk step |

Rough budget per turn: system prompt about 1,500 tokens (world rules, verbs, crafts, identity and aims), cached and rebuilt rarely;
turn prompt about 1,500-2,500 (here, today's options, self and house, seen and heard, memory bands, pinned note and titles,
duties). Busy places (a market day, a crowded hall) are trimmed by priority, as cybertron 1's context module did.

## How actions are defined

- **A verb is a handler with typed referents**: who acts (always the agent), what it acts on (a person here, goods carried, a
  site here, a technique, a container, a claim, an institution, a power), its parameters, and the kind of change it makes on the
  chokepoint (one or a few primitives). Verbs are not interchangeable because their referents and changes differ.
- **An action is one use of a verb**: verb + object + parameters (`make {what: "pot", qty: 2}`).
- **Everything else is data, not verbs.** Techniques (recipes, blueprints, methods), fittings, claims, offices' powers and laws'
  clauses add objects for existing verbs. A new kind of pot, a mill, a guild's power to fine: none adds a verb.

So verbs partition actions by the kind of change and the kind of thing changed; the world grows by data.

## The verbs (a lean set: 24)

| Verb | Acts on | Kind of change | Folds in (from earlier lists) |
|---|---|---|---|
| `travel {to, with?}` | an edge | move self (and party) | flee (at night, as a response), scout later |
| `rest` | | none | |
| `gather {site, method?}` | a site here | take from the land | forage, hunt, fell, quarry, mine, fish, draw water |
| `make {what, qty?}` | a recipe | transform goods into a carried item | forge, craft, cook, cure, weave, write a copy |
| `build {what, at}` | a blueprint, a lot or room | make something fixed | fortify (walls, gates, locks) |
| `work {what, at}` | a method, on a plot, project, building, animal or person | labour on something fixed or living | sow, tend crops, reap, repair, operate a mill, herd, yoke, milk, tend the wounded, bury |
| `move {goods, from, to}` | goods, between containers the agent may use | move goods | store, take, pack |
| `give {to, goods}` | a person here | hand over | yield (to a demand), deliver an errand, give a claim |
| `offer {to?, give, get}` | a person here, or anyone here | propose an exchange | sell, hire, let land, lodge at an inn, ask to be taught |
| `accept {offer}` | an offer | carry out both sides at once | |
| `set {thing, setting}` | something the agent controls | change a setting | lock or open a door, welcome guests, who may use a farm or a stock, standing prices, an office's settings |
| `claim {thing}` | a plot or site | assert a claim | |
| `attack {target, aim}` | a person, house, building or herd here | force | raid (aim rob), damage, burn, drive off |
| `guard {where?}` | the place or a person | defend tonight | keep watch |
| `steal {goods, from}` | goods in an unwatched place | take unseen | |
| `watch {person}` | a person working here | learn by watching | |
| `teach {to, technique}` | a person here who accepts | pass know-how | learn (the learner accepts, or asks with `offer`) |
| `read {document}` / `write {what}` | a document | information to and from objects (literacy) | |
| `join {institution}` / `leave {institution}` / `found {institution}` | an institution (households included) | membership | partner (joining a household), adopt |
| `conceive {with}` | a partner here who also chooses it | a child | |
| `invoke {power, ...}` | a power the agent holds through an office or a law | whatever the power does | propose, vote, appoint, judge, register, proclaim, collect, muster: every institutional act |

**Free, in the reply rather than as verbs** (talk step, no work units): `say`, `tell` (with an optional `about`, and `explain` to
give a rough idea of a technique), `note`, `pin`, `open` (a note), `look up` (a card).

## Rules against swelling

cybertron 1 reached 145 actions because each mechanism got its own action. To keep the list near 24:

1. **New things are data.** A new mechanic first tries to be a technique, a fitting, a setting, a claim, an institution's power or
   a law's clause on an existing verb.
2. **A new verb needs a new kind of change** on the chokepoint or a new kind of referent that no verb takes, shown in a short note,
   and Zach's yes.
3. **Institutional acts are powers**, all through `invoke`, shown only to holders.
4. **Every verb is in the coverage test**: each spec mechanic names the verb that reaches it, and each verb names its primitives.
5. **The count is reported** in the spec; growing it is a decision (DECISIONS.md), like any other.

## What may not fit the verbs

Checked against the designs so far: ceremonies and oaths (an institution's power through `invoke`, or a promise in words);
threats and negotiation (talk); prayer and ritual (later, as a work method at a site); hiding (a later `set` on oneself, 02h §4a);
searching a place for hidden things or a lost traveller (a later `gather` method, or `scout`); signals and beacons (`work` at a
beacon). Nothing found so far needs a new verb.

## Force and defence: what was missing

| Need | Verb or mechanism | Status |
|---|---|---|
| Fight a person | `attack` (as built) | exists |
| Take a house's food by force | `raid` (as built) | exists |
| Defend people and houses at night | `guard` (as built) | exists |
| Take without a fight | **`steal {goods, from}`**: only when nobody else is present at the place (everything else is witnessed, handoff §4); taking from a house needs its door unlocked or the lock broken (02i fittings) | missing |
| Damage or burn a building, drive off a herd | `attack {target, aim: damage, burn or drive off}` (02g §5b) | proposed by 37.2 |
| Escape | `travel` as a response before a fight is settled (at night, unsheltered) | via travel |
| Give in | `give` what is demanded (a demand made in the talk step) | via give |
| Fortify | `build` walls, gates, towers, locks (blueprints and fittings, techniques) | via build |
| Arm | `make` weapons (recipes); carrying a weapon is holding it | via make |
| Keep watch and raise the alarm | a guard detects early; the hue and cry wakes neighbours (02k fuse events) | proposed (02k) |
| Hold someone | detention needs a locked room and a guard; ransom is an offer | later |
| Muster a militia | an office's power (`collect` people as a duty) | with institutions |

## Other gaps found in the same pass

| Area | Missing | Proposed |
|---|---|---|
| Health | wounds exist, care does not | `work {what: tend wounds, at: person}` (healing and midwifery as methods) |
| The dead | bodies lie where they fell | `work {what: bury, at: the body}` (a lasting memory to those present) |
| Animals | herding, breeding, milking, yoking, riding, breaking | gathering and working methods on herds (37.2 livestock) |
| Hiring | wages for work | an `offer` whose terms are work (a contract once institutions exist) |
| Exploration | scouting an edge, mapping | `travel` and return, later a scouting method (37.5); a map is a document (`write`) |
| Travel together | leaving as a party, escorting | `travel {to, with}` |

## How it avoids confusion and bloat

- **One grammar, always the same.** Agents learn about 25 verbs once; nothing appears or disappears from the grammar except office
  verbs when an office is taken.
- **Objects are local and known.** The agent sees only what is at its node, what it carries, what it knows, whom it can see.
- **Refusals teach.** Every refusal names what is short or wrong ("pots need 2 fuel; you have 1"; "Torvald is not here"; "you have
  no kiln here"), at no cost.
- **Names, not ids.** Objects are named as the agent sees them, with aliases and closest-match suggestions on a miss.
- **Budgets and look-ups.** Lists are trimmed by priority; detail is a look-up away.

## Open questions

1. The lean set of 24: anything to merge or split (for example `steal` into `move`, which would hide the act).
2. `steal`: allowed only unseen? Detected later (a missing item noticed by its owner)?
3. Fleeing and yielding as reflexes (standing orders, later) or only as chosen actions?
4. A coverage test: every mechanic in the spec reachable by some verb and object.

## History

- 23 Oct: proposed (37.4, with Zach), after Zach asked how the whole space of possible actions compares with what an agent is
  shown, whether it avoids confusion and bloat, and what is missing (attacking, raiding, guarding, fortifying).

- 23 Oct: Zach: how are actions defined (verbs as handlers, or a partition)? which verbs? closed lists tend to swell. Added how
  actions are defined (verbs are typed handlers; actions are uses; everything else is data), a lean set of 24 verbs with what each
  folds in, rules against swelling (data first, a new verb only for a new kind of change, institutional acts through `invoke`, a
  coverage test, the count as a decision), and a check of what may not fit.

- 23 Oct: built as a subset in M1 with `learn` kept as a verb; the same-day teach and learn match failed often in run B (Q5 in
  [11_m1_slice.md](../../review/38_space_engine/11_m1_slice.md)), which supports the offer-and-accept form proposed here.

- 23 Oct: in M1, `say` now has a scope (a building one has access to, or the town) and only `tell` and direct offers wake
  (D4-25); `build` dropped from M1 with the firing pit; no lend or return yet (38.14 §3.3: an omission of this proposal).

## Sources

38.06 (all cybertron 1 actions), knowledge.md, 02g §5b (raids at scale), 02i (fittings, locks), 02k (fuse events, gates),
38.03 (run 2: no fights), cybertron2/act.py.
