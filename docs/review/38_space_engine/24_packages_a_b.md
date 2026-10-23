# Review 38.24: Packages A and B built and run (37.2's brief 02r)

Session 37.4, 24 Oct 2026. Zach: build Package A, test it in a small and a larger single-node run, then Package B and a run; few,
reasonable live runs; build the new systems as general parts, not one-off cases. The brief is
`docs/review/37_growth/02r_build_brief_roads_and_fuses.md`; the spec files are the ones it lists. 79 cybertron2 tests pass
(tests/test_cybertron2_package_a.py and _package_b.py hold the brief's list).

## 1. What was built, and how it extends

| Part | Module | Extends by |
|---|---|---|
| The day's weather by spell (keyed), snow lying, visibility per place and sense, masking | `engine/environment.py` | WEATHER, SPELLS, ENV rows in data; any system reads `visibility()`, `wet()`, `snow_lying()` |
| Things at a spot (piles, remains; traces on roads) and one noticing rule; the eye for the land as levels raised by practice and finds | `engine/things.py` | a new kind of thing is a kind, a conspicuousness and its signs (THINGS, NOTICING) |
| Modifiers as techniques: `for`, `hidden`, `method: dibble`, `method: cairn`, travel's `on trouble`, `stop at`, `gather` | `engine/modifiers.py` | a modifier is a TECHNIQUES row with `modifies`, `key`, `value`, `untaught`, `changes`; a verb reads the changes it understands |
| `give` to a person, household, building or place; at the door when it cannot reach; `leave`, `put`, `drop`, `hide` read as `give`; `take` from what one knows lies about; `bury` as work on a body | `engine/verbs.py` | |
| Decay by condition (open dry or wet, buried, warm, frozen; what it becomes) | `night.decay_rate` | DECAY rows per item |
| Fuse events: a registry of kinds (source, detection, choices); the night sub-step; one call a night, a day on the road; the call appended to the agent's own conversation | `engine/fuse.py` | a new kind registers a source, a detector and its choices (raids in fuse.py; meeting, find, crossing in roads.py) |
| Roads: stretches, terrain, landmarks, trouble settled by choices at departure or a call, experience, good places, daily notices and "On the way", meetings with up to 3 waves of talk and trades, finds, traces | `engine/roads.py` | TERRAIN, LANDMARKS, ROADS rows; a new kind of trouble is one branch in `challenge()` |
| Spec variants (`base:`), things seeded at a spot or on a road, a death incident, scripted acts for dry runs; one village cut from a region; bare roads (the comparison arm) | `world.load_spec`, `engine/variants.py` | |

A road with no terrain and no landmarks holds nothing, so a world can switch roads off: the regression test runs a world with the
roads step and without it and finds the days identical (D2-104).

## 2. Runs

| Run | World | Agents, days | Cost | What it showed |
|---|---|---|---|---|
| dry (bots) | hamlet_a_dry: raids scripted on a timber and a stone house, a death, a buried cache, two wet days | 9, 6 | 0 | timber raid: one woken, 1 act (alarm); stone raid: four woken, 3 acts each (alarm, defend); the buried cache almost unseen (own 0.024); the body on the Green, then its smell from day 4 |
| a1 small | hamlet_a_live: a wet spell, an elder's death, two caches in the wood | 9, 6 | $2.39 | no errors; the household planned a cairn, refused for naming the house (fixed); the cache under brush noticed by two, left alone; the owner of the buried coin did not touch it; dried meat in the open 3 to 2.7 |
| a2 larger | barleyfield_a: Barleyfield alone with a wood, a wet spell, an elder's death, a dropped sack, two caches | 16, 10 | $4.59 | no errors; Bennet buried Daniel for the Hales the day he died; Avice found and took the sack on day 2; the cache under brush noticed on day 8 and left; 15 refusals on picked-bare land in 10 days (the region had 321 in 20); weather in every prompt, snow on the last day |
| b1 roads | two_valleys_b: the road 2 days with a ford and a meadow, heavy rain on day 3 | 19, 8 | $5.35 | Ancel (Opus) baked bread, made a pack and set off with `on trouble: push on`; fed at the meadow, crossed the high ford and was soaked; arrived with "On the way: ... the ford was high: you crossed anyway and were soaked to the skin" and reasoned from it ("I'm starving, soaked ... I need a warm bed at a lit hearth"); a round trip, 9 agreements |
| b0 bare | two_valleys_b0: the same, roads bare | 19, 8 | $5.53 | two late journeys, 2 agreements, more missed meals; one traveller in each arm: the differences are run variance, not the roads |
| b2 meeting | two_valleys_meet: the road 1 day with a ford; two agents set off from opposite ends on day 1; a pack on the road | 19, 3 | $2.38 | a meeting at the ford with a trade (§3); no find (neither noticed the pack) |

## 3. The meeting run

The 8-day arms had one traveller each, so no meeting and no find happened live. A 3-day run with two departures scripted from
opposite ends of a one-day road with a ford:

- Night 1, at the ford: one call each (3 acts). **Simkin** (Opus, Wetham) greeted Joyce, asked whether the way was clear and offered
  2 coin for 1 timber; **Joyce** (Sonnet, Highcombe) first meant only to go on; in the second wave she saw the offer and took it
  ("Trade one timber for coin at no real cost, tell him the way is clear, and carry on"). The trade settled from what each carried;
  both went on. No errors.
- Both arrived hungry (Simkin's rye needs a fire; neither had bread) and asked for a bed and food. Joyce reasoned she was "at Wetham
  by mistake": her departure was scripted, not chosen.
- Neither noticed the pack on the road (own 0.4 x the valley's sight x the eye, per person, per night).
- Found by the run and fixed: the arrival lines left out the meeting (now "you met Simkin at a ford; Simkin traded 2 coin for 1
  timber"); a wave showed each its own words back.

Total for the five live runs: $20.24 (hamlet $2.39, Barleyfield $4.59, roads $5.35, bare $5.53, meeting $2.38).

## 4. Faults found by the runs and fixed

| Fault | Fix |
|---|---|
| a death at home put the body on the Green, where its own household rarely noticed it | one who dies at home lies in the house, found at once by its household; one's own ground is crossed daily (0.3) |
| "bury her by Thorne House" refused | bury by a building's name, the ground it stands on, or the person |
| giving grain from one's household's store to another household refused ("you carry only 0") | `give` takes from the household's store with `for`, to anyone |
| a cairn counted twice (4 units) | its work once (2) |
| a traveller's urgent call could not build its reply schema (the view refused the road) | the view allows the road for urgent calls; a test with a live-model stand-in (the roads arm was restarted on the fix) |
| the arrival lines left out a meeting; a meeting wave echoed one's own words | the meeting and its trades in "On the way"; others' words only |

## 5. Choices the spec left open (OPEN Q-20), and what is not built

Wattle counted as a hut (no call); `method: dibble` learned and untaught `no`, so nobody in the existing worlds can dibble until
taught; the dead at home lie in the house; warm and frozen decay apply in houses too; road trades are goods for goods; parties
crossing between stretches meet on the first-node party's stretch. Not built: hidden ways (parcels have no sides), fire as a fuse
event (no house fire in the scheduler), wet timber, scavengers; raids were not exercised live (no agent chose to attack).

*A run report; the decisions it bears on are D2-80 to D2-113, D4-50.*
