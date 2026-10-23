# Proposal: the verbs, and what each agent is shown

**Status:** discussion (23 Oct). **Owner:** 37.4. **Affects:** spec/agents/actions.md, information/prompts.md, conflict/,
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

## The verbs

Each verb's meaning is crisp so that similar ones do not blur: **make** produces a carried item; **build** produces something fixed
at a lot or in a room; **work** is labour on something fixed (a plot, a project, a repair); **gather** takes from a site.

| Group | Verbs | Always shown? | Objects come from |
|---|---|---|---|
| Body and place | `travel`, `rest`, `watch` (a person, for the day) | yes | edges; people here |
| Getting | `gather {site, how?}` | yes (basic foraging needs no technique) | sites here; gathering methods known |
| Making and building | `make {what}`, `build {what, at}`, `work {what, at}` | yes | techniques known (or a rough idea, to try) |
| Goods | `give`, `offer`, `accept`, `store`, `take`, `pack` | yes | goods carried; people here; one's house |
| Talk and mind | `say`, `tell`, `explain`, `note`, `pin`, `open` (free, talk step) | yes | people here; techniques known; one's notes |
| Learning | `teach`, `learn` | yes | techniques; people here |
| Writing | `write`, `read` | if literate | documents carried or here |
| Hospitality | `host`, `welcome`, `lodge` | yes | people here; inns here |
| Land and claims | `claim`, `transfer_claim` (give, sell, let) | yes | sites and plots here; claims held |
| Force | `attack`, `raid`, `guard`, `steal`, `damage`, `flee`, `yield` | **yes, always** | people, houses, buildings, herds here |
| Life | `partner`, `conceive`, `join`, `leave`, `bequeath` | yes (adults) | people here; households |
| Institutions | `found`, `propose`, `vote`, `appoint`, `judge`, `proclaim`, `register`, `collect`, and powers a law defines | members and office holders only | institutions it belongs to; its offices |

**Force is always shown.** Run 2's raiders never raided, starving beside full stores; if attack and raid were hidden or buried, the
question "will they fight" could not even be asked. They stay in every system prompt, with their costs in world terms.

## Force and defence: what was missing

| Need | Verb or mechanism | Status |
|---|---|---|
| Fight a person | `attack` (as built) | exists |
| Take a house's food by force | `raid` (as built) | exists |
| Defend people and houses at night | `guard` (as built) | exists |
| Take without a fight | **`steal {item, from}`**: only when nobody else is present at the place (everything else is witnessed, handoff §4); taking from a house needs its door unlocked or the lock broken (02i fittings) | missing |
| Damage or burn a building, drive off a herd | **`damage {building}`**, `raid {herd}` (02g §5b) | proposed by 37.2 |
| Escape | **`flee`**: leave a fight before it is settled (travel as a reflex, at night, unsheltered) | missing |
| Give in | **`yield {goods}`**: hand over what is demanded to end a threat (a demand made in the talk step) | missing |
| Fortify | `build` walls, gates, towers, locks (blueprints and fittings, techniques) | via build |
| Arm | `make` weapons (recipes); carrying a weapon is holding it | via make |
| Keep watch and raise the alarm | a guard detects early; the hue and cry wakes neighbours (02k fuse events) | proposed (02k) |
| Hold someone | detention needs a locked room and a guard; ransom is an offer | later |
| Muster a militia | an office's power (`collect` people as a duty) | with institutions |

## Other gaps found in the same pass

| Area | Missing | Proposed |
|---|---|---|
| Health | wounds exist, care does not | `tend {person}` (a technique: healing; midwifery), shortening a wound |
| The dead | bodies lie where they fell | `bury {person}` (kin's duty; a lasting memory to those present) |
| Animals | herding, breeding, milking, yoking, riding, breaking | gathering and working methods on herds (37.2 livestock) |
| Hiring | wages for work | an `offer` whose terms are work (a contract once institutions exist) |
| Exploration | scouting an edge, mapping | `scout {edge}` (37.5); a map is a document (`write`) |
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

1. The final verb list (about 25) and which are free (no work units).
2. `steal`: allowed only unseen? Detected later (a missing item noticed by its owner)?
3. `flee` and `yield` as reflexes (standing orders, later) or only as chosen actions?
4. A coverage test: every mechanic in the spec reachable by some verb and object.

## History

- 23 Oct: proposed (37.4, with Zach), after Zach asked how the whole space of possible actions compares with what an agent is
  shown, whether it avoids confusion and bloat, and what is missing (attacking, raiding, guarding, fortifying).

## Sources

38.06 (all cybertron 1 actions), knowledge.md, 02g §5b (raids at scale), 02i (fittings, locks), 02k (fuse events, gates),
38.03 (run 2: no fights), cybertron2/act.py.
