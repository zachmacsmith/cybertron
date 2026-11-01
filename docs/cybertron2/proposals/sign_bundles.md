# Events and their aftermath show themselves

**Status:** retrospective, accepted: D4-74 (2 Nov)
**Owner:** 37.4

## Summary

The 18 events and states that review 38.43 found showing thinly or not at all each get a bundle of signs in the slaughter pattern
(D4-71), every row read by the one noticing rule (D4-75). Each bundle gives, where they fit, four kinds of sense: to the doer as they
do it; to those nearby as it happens; lingering traces on later days; and signs that exist only under conditions. Old age and
illness are left out (the engine holds no state to show) and a threat keeps its event line.

## The proposal

The table of bundles is in spec information/signs.md ("Events and their aftermath"); the rows are in signs.py (FIGHT, RAID, HUNTED,
FIRE, BIRTH, GUARD, DRIVEN, THEFT, BROKE, BURIAL, DOGS, and new rows in PERSON, BUILDING, HERD, FIELD, CROP and WILD). Kinds given:

| Item (38.43) | Doer | Nearby | Lingering | Conditional |
|---|---|---|---|---|
| 1 fights at night; raids | the striker's knuckles | blows heard (night); shapes struggling (near, night) | the ground scuffed, blood; gouges at a door; the store gone through | snow, blood, dogs |
| 2 a hunting kill | the kill's weight and blood | the gutting (near) | crows; the smell next day; the hunter bloodied | snow, warmth |
| 3 a house fire | | glow, roar (night), smoke inside | burnt thatch (3 days), ash smell (2) | rain or snow through the roof |
| 4 a birth | | a newborn's cry (night) | the mother just risen from childbed | |
| 5 food rotting in a store | | the stink | flies at it | not in frost |
| 6 a guard posted | the long night | the watcher at the door (night) | heavy-eyed | a weapon; frost |
| 7 beasts driven | | hooves and lowing; the drover | hoof-marks (2 days) | wet: mud |
| 8 things made | | woodwork; a club or spear; hides stitched | | |
| 9 sleeping out | (the night lines) | | stiff with cold, soaked, roofless | frost, rain |
| 10 ploughing, reaping | | plough and team, hoes, sickles; birds; swathes | (field and crop signs) | frozen clods; rain on sheaves |
| 11 quarrying, mining | | picks; spoil | | |
| 12 a theft | | | the store lower (inside) | snow footprints; mud |
| 13 calving | | lowing to the calf | the afterbirth (a day) | cold: the calf steaming |
| 14 a house breaking, mended | | a crack in the night; mallets | the roof in, a crack (2 days) | how far it went |
| 15 a burial | frozen ground, or the weight | a grave dug; a spade heard | (the grave) | frost |
| 16 old age, illness | left out: the engine holds no illness before a death, and old age already shows as "failing" | | | |
| 17 a threat | left out: it leaves no trace, and a sound of it would put words or cries in a mouth that did not choose them (D4-72); its event line is read by the rule | | | |
| 18 milking, minding | | milk into a pail; someone out with the herd; a child kept close | | |

**State added** (all through `set`, so journalled and replayed): parcel `fight` (the night's fights: by, target, outcome) and
`hunted` (the day's kills); building `fire_hit`, `raided` (outcome), `theft` (item) and `broke` (to which condition); person `guarded`
(the night's watch) and `slept_out` (with the cold); herd `driven` (from, to, by). The rest reads what the engine already held (the
day's events, a herd's `last_calf`, `milked`, `watched`, a store's goods, a child's `born`, the day's care).

## Why

Zach (2 Nov): "Get the agent to add bundles for the 18 it ranked", with the four kinds: to the doer, to those nearby as it happens,
lingering traces, and conditional signs ("obviously the blood on the snow is only if there is snow").

## Alternatives considered

- **One line per event, shown to all at the place:** against D4-48 and D4-53; no reason to be there, to ask, or to tell.
- **New goods for traces (offal, ash, blood):** would invent items the economy does not have; a record of the event carries them.
- **Signs of illness before a death:** the engine decides "a sudden illness" only as a cause of death; showing illness first would
  assert a state the engine does not hold (engine gap, review 38.43).

## Open questions

1. A raid as it happens is still told through fuse's NIGHT bundle to those woken (now by the rule); whether neighbours not woken
   should get a sound line too.
2. A threat: whether a squared-up pair should leave anything for those near.
3. Old age: whether the engine should hold frailty before death, which would give it signs.

## Affects

signs.py, verbs.py (hunt, guard), farm.py (drive), settle.py (fights, raids, thefts), night.py (sleeping out, breaks), run.py (the
fire incident); spec information/signs.md.

## History

- 2 Nov 2026: built at Zach's request after the audit (review 38.43); the rule change (D4-75) came in the same session, so every
  row is an own read by the rule; written down after (retrospective).

## Sources

review 38.43; tests/test_cybertron2_sign_bundles.py; the scripted bot runs (combe_evening 30 days, valley_s5 20 days) with their
replays.
