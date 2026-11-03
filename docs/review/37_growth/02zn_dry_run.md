# 02zn · The first dry run of a generated world

Current as of 3 Nov (37.2). Zach, 3 Nov: "do the bot dry run on a generated world". The world is twin bays
(`cybertron2/specs/twin_bays_gen.yaml`, seed 7, generated with people):
- four villages, two wild places (Hazelthorpe, a forest; Craghurst, hills with a copper seam) and 37 people;
- it passes every generator check, with one warning (succession).

## 1. The bot run

`python -m cybertron2.engine run <world> --bots --days 10`, then `replay`.

- **The engine ran clean:** no errors on any of the 10 days, and the replay checked 70 steps with no mismatches.
- **But 13 of the 37 people starved, between days 4 and 7.** They were adults and youths from all four villages and several
  households, none of them a household head.
- **The cause is the bots, not the world.** These bots walked to a neighbouring village on day 1 with empty hands, where they had no
  store of their own. There they spent their days felling timber and gathering firewood until they were too heavily loaded to walk
  home (carrying 17.4 against a limit of 10), and they missed every meal until they died. The houses at home held 30 grain and 6
  beans a household.
- **This matches 37.4's warning** (board, 2 Nov): bots wander and starve whatever the numbers. So a bot run checks that the engine
  runs and replays; it does not check a world's economy or its gates.

## 2. The gate probe

scenario_design §4 asks to "verify every access gate in a dry run, per action". That needs every action tried at every place, which
bots don't do, so the probe does it directly: `python -m cybertron2.landgen.gates <world.yaml> [out.json]` (new).

**What it tries:**
- At each place, every gather and work technique, by the person best suited there (one who knows the craft and holds a tool), on a
  fresh copy of the world.
- At a wild place, someone who knows it walks in.
- Every road from each end.
- Each wild place both by name (by someone who knows it) and by its unexplored way (by a stranger).
- Sowing with a seed named, and reaping on the day the first crop ripens.

**How it reports:**
- what works where;
- the techniques **shut everywhere**: wherever their ground exists, nobody can do them;
- those refused only for the moment or the inputs: a crop not ripe, no dung to hand, a tool still with the household head;
- crashes, and roads that refuse.

**On the world as first generated, it found four shut gates.** All four are generator faults, now fixed:

| Gate | Cause | Fix |
| --- | --- | --- |
| **No one could mine.** The copper seam at Craghurst could not be worked by anyone, and the cheap ladder's copper village could smelt but not dig its own ore. | The "smith" trade gave smelting, copper tools and coin, but not mining. | A smith near a seam mines it. |
| **No one could quarry.** | Trades were handed out one per household, so the third trade in a two-household village (mason, after smith and carpenter) was dropped; masons also came only where a village had rock of its own. The "trapper" trade was defined but never given. | Every trade a village earns goes to some household (two to one if need be). A village a road away from hill country gets a mason. A village next to a wild forest gets a trapper. |
| **No stone anywhere.** The hill place's rock had a copper seam but no stone to quarry. | Rock parcels got a seam only. | Every rock parcel holds stone (100 a unit of size, finite: wenbridge's quarry). |
| **No one knew the way to the wild places.** Strangers could still take "the open road" there (D4-47), but D2-187's rule (known from the start to the households whose trade uses them) was never built. | No seeding of known places; the engine skipped every unexplored place when seeding knowledge. | The generator lists, for each agent, the wild places its household's trade uses (`places:`): the miners and masons know the hill, the trappers the forest. A one-line hook in `engine/perceive.py` exempts those places from being hidden. |

**After the fixes**, on twin bays and on all three cheap-ladder worlds:
- no gate is shut, nothing crashes and every road opens;
- the copper chain runs end to end: ore mined at the Scar, smelted at the smith's forge, made into a copper tool;
- stone is quarried at the Scar;
- the bot run is again clean and replays exactly.

The bots still starve the same 13 people, for the same reason as before.

## 3. What the dry run does not cover

- **The economy under real play.** Neither bots nor the probe say whether agents will feed themselves. Only the economic checks
  (02zl) speak to that before a run, and only the first live days speak to it after one.
- **Learning crafts.** The probe tries each craft with one who knows it. That others can learn it ("watch someone, ask to be taught")
  shows in the refusals, but isn't exercised.
- **Building, making and trading** beyond the copper chain: the probe covers gather and work techniques, roads, and here smelting.

A better bot, one that eats from home, carries what it can and comes back, would make bot runs useful for the economy. That's
37.4's area; it is suggested to them, not built.

## Files

- `cybertron2/landgen/gates.py` (new): the probe.
- `cybertron2/landgen/write.py`: trades, the mason near hill country, the trapper, stone in rock, wild-place knowers.
- `cybertron2/engine/perceive.py`: the `places` hook.
- `tests/test_cybertron2_landgen.py`: a generated world has no gate shut for everyone.
- `cybertron2/specs/ladder/`: regenerated. The copper village's smiths can now mine; same cast, same burdens.
