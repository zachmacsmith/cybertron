# 02r: build brief for 37.4: fuse events, noticing, things in places, visibility, roads

Session 37.2, 23 Oct 2026. Zach: write up everything needed, as spec, and pass it to 37.4 to build; 37.2 does not build. This
note is the hand-over: which spec files to build against, the order, the engine points I saw, the tests, the edits your existing
spec files need, and a run plan. Every rule cited is in DECISIONS.md (D2-80 to D2-113) and in the spec files below; numbers there
are marked proposed or calibrate.

## 1. Spec to build against

| Spec file | Holds | Decisions |
|---|---|---|
| spec/conflict/fuse_events.md (new) | events with a fuse, detection, acts by fuse length, rarity, overlaps, the call appended to the agent's conversation | D2-5, D2-80 to D2-84, D2-86, D2-110 |
| spec/information/noticing.md (new) | one noticing rule; own conspicuousness; traces; daily notices on the road; "On the way" on arrival | D2-85, D2-86, D2-88, D2-89, D2-91, D2-97, D2-98, D2-102 |
| spec/world/things_in_places.md (new) | spots; `give` to a place, hiding, at the door; whose; the dead, rot, burial | D2-85, D2-87, D2-93, D2-96, D2-111 |
| spec/agents/modifiers.md (new) | modifiers as techniques; first modifiers; showing; trying untaught | D2-93, D2-94, D2-111, D2-112 |
| spec/environment/visibility.md (new, 37.2's) | sight and sound computed per place and day; masking | D2-99 to D2-103 |
| spec/environment/scheduler.md (37.2's) | "The day's weather" within the spell; snow lying; a ford high | D2-99 |
| spec/economy/goods.md (37.2's) | "Decay": each item's decay by condition | D2-87 |
| spec/world/roads.md (new) | stretches, landmarks, three tiers of crossing, departure choices, waiting, good places, meetings, road ends and hidden ways | D2-81, D2-90, D2-92, D2-98, D2-104 to D2-110, D2-113 |

The four new files in your areas were written by 37.2 at Zach's request; they are yours from here (README rule 3 kept: none of
your existing text was edited). §4 lists the lines in your existing files that now need changing.

## 2. Order: two packages, each tested before the next

**Package A (one node):**

1. The day's weather in the scheduler (keyed draws), snow lying.
2. Visibility, computed (cover base x state x weather; night factors for night events; masking).
3. Things at a spot as containers at a parcel (remains already are: give them a parcel), with own conspicuousness.
4. The noticing rule, replacing "remains shown to all at the node at 0.7" (perceive.py) with the roll.
5. `give` to a place and at the door; `leave` read as `give`; the `hidden` modifier (tryable untaught); `bury` as work on remains.
6. Modifiers as techniques (`modifies`, `untaught`), with `for` and the sowing method moved onto it.
7. Decay by condition (the goods table), open and buried included; rot's signs (no health effect yet).
8. Fuse events: the night sub-step, detection of raids (settle.py's raid) by the chances given, acts by fuse length, one call a
   night, the call appended to the conversation (run.py's `decide` with `conv` already does this for the lighten prompt).

**Package B (roads):**

1. Stretches: the transit record gains its stretch (world.py's `transit`: road, from, to, left, arrive).
2. Edge data: terrain, per-stretch terrain and landmarks, landmark state (a ford's level from the day's weather).
3. Daily notices on the road and "On the way" on arrival; things on a stretch (remains on the road since 06c7148: give them a stretch).
4. Departure choices (`on trouble`, `stop at`, `gather`) as travel modifiers; the departure prompt shows known landmarks and the food
   cost of waiting.
5. Crossing in three tiers, experience per landmark, waiting out a block, good places on the way.
6. Meetings: who meets, the chance by stretch, the fuse call with up to 3 waves of talk (converse.py's talk step), free give and
   offers, then each party's choice; attacks through combat.py on the road.
7. Finds on the road worth taking: a fuse call if noticed.

**Later (not in A or B):** hidden ways need parcels to have sides (layout.md, not in the engine yet); fire as a fuse event needs the
scheduler's house fire or setting fire in a raid; everything in OPEN.md "Flagged for later".

## 3. Tests (each a unit test; draws keyed so they repeat)

| Package | Test |
|---|---|
| A | the day's weather repeats for the same seed and differs by day; snow lies until three days without frost |
| A | sight in fog in woodland = 0.35 x 0.3; at night only for night events |
| A | a body on open ground is noticed by a farmer working that parcel far more often than one in woodland; a buried pack almost never; untaught hiding x0.4 not x0.2 |
| A | `give` to someone not here leaves the goods at their door, in the open, takeable by a passer-by; `give` into one's own house still goes to the store |
| A | `bury` is offered only where remains lie; frozen ground costs 6 units |
| A | grain in the open on a wet day loses 5% (0.5% x10) |
| A | a raid on a hut gives no call; on a timber house at most 1 act; on stone up to 3; no agent gets two calls in a night |
| A | the urgent call is in the agent's conversation history after the day's turn |
| B | a 1-day edge: two parties leaving opposite ends the same evening meet on stretch 1 |
| B | a 3-day edge: parties leaving on days 1 and 2 from opposite ends cross on the right stretch |
| B | a high ford with no choice given: wait 1 day; with `push on` and a cart, 0.3 chance of losing 0.2 of the load; reported on arrival |
| B | an experienced traveller (5 crossings) gets half the trouble, and a call only above the death threshold |
| B | a meeting gives each party one call with up to 3 waves; an offer accepted on the road settles from what each carries; `turn back` reverses the stretches |
| B | an edge with no landmarks behaves exactly as before (the regression test for D2-104) |

## 4. Edits your existing spec files need (yours to make)

| File | Now says | Change |
|---|---|---|
| world/edges.md | "On the road a traveller is at no node: it makes no decision, sees no node" | point to world/roads.md: fuse calls in transit (D2-81, D2-110), daily notices (D2-97), stretches (D2-104) |
| world/edges.md | Data: "Per edge: the two nodes and the days" | add terrain, stretches, landmarks, ends (world/roads.md Data) |
| conflict/defence.md | the fuse-event paragraph | point to conflict/fuse_events.md |
| core/round.md | night: "where each sleeps, ..." | add the fuse sub-step (conflict/fuse_events.md "When") |
| agents/actions.md | `give` and `leave` as two verbs | `give` to a place absorbs `leave` (D2-111); `bury`; modifiers (agents/modifiers.md) |
| information/perception.md | remains seen at the node | the noticing rule (information/noticing.md); D2-91 extends D4-50 (the eye raised by practice) |
| information/prompts.md | the call prompts | the urgent call appended (D2-84); "On the way" lines on arrival (D2-97); the departure prompt's choices (world/roads.md) |
| world/places.md | containers at a node | things at a parcel or stretch (world/things_in_places.md) |

## 5. Run plan

Package A first in the hamlet (one node): a dry run that scripts a raid on a timber and a stone house, a death left unburied, a
cache hidden in the wood, and two wet days; then a live run to check nothing else moved. Package B in a variant of two valleys
with the Wetham-Highcombe road made **2 days with a ford on stretch 1**, a wet spell in the first week, and a reason to cross both
ways (each valley needs what the other has, so travellers meet: scenario_design.md §1). Before running, the check 38.23 lacked:
fuel and food that must be carried over that road in the days available, by the people free to carry them. Cast as
scenario_design.md §2 (Opus at each side of the dependence, Sonnet middle, Haiku bulk).

**The comparison arm:** the same world and seed with no landmarks (D2-104 says it then behaves as before), so meetings, trouble
and notices are read against roads that hold nothing. Read: meetings and what came of them (trades, joins, fights), calls per day
(cost), deaths on the road, things found and taken, whether "On the way" lines changed what agents did, with a qualitative
reading of the end state.

## 6. Open, not blocking

`searching` and `aim: burn` as modifiers; overlapping events in depth (Q-19); everything in OPEN.md "Flagged for later" (L-1 to
L-20).
