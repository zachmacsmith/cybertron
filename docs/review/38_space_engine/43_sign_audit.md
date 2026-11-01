# 38.43: what shows itself, and what does not (a sign audit)

Session 37.4, 2 Nov 2026. After the paired Combe run (38.42), where the family slaughtered a calf, two cows and an ox and nobody saw
or heard a thing of it, Zach: "slaughter and related should have some pretty visceral senses for the person and others nearby ... I
imagine it would be hard to miss". This note records what a slaughter showed before, what was added (D4-71), and an audit of the other
events and states that show themselves thinly or not at all, ranked.

## What was checked

- Every event the engine emits (`here.event` / `w.event` across verbs.py, farm.py, herds.py, life.py, night.py, run.py, settle.py,
  fuse.py), its kind, and whether perception lets anyone but the doer read it: perceive.evening skips events of the ROUTINE kinds
  (work, make, store, take, give, trade, teach, build) for everyone but those they concern, so a work act shows only through the
  state it leaves, read by the sign tables.
- Every sign table in signs.py (CROP, FIELD, PASTURE, HERD, TRAMPLED, ASTRAY, EMPTY, FENCE, WAY, CARCASS, SKY, WILD, BUILDING, PERSON,
  THING, ROAD, TRACE, TRAVELLER, NIGHT, PASSING) against the states and acts it would show: how many rows, which senses.
- The techniques (data.TECHNIQUES) by verb: make (19), work (20), gather (9).

## Slaughter, before

A slaughter emitted one event, "Ivo was slaughtering a beast at the Common" (kind `work`, salience 0.15, about the herd). Work is
routine, so no one else read it; the doer had only the result line ("You slaughtered a cow of the Hobb cattle: 40 meat, 2 hide (now in
your hands)."). The only trace for anyone else was PERSON's load row (0.12: "Ivo has a load: a great deal meat ..."). Checked on
combe.yaml: after Ivo slaughtered a cow, Margery's facts held the work event and nothing else about it.

## What was added (D4-71)

- **State:** farm._slaughter records the day's kills on the parcel, `parcel.slaughter = {day, kills: [{beast, herd, by}]}` (through
  the `set` primitive, so journalled and replayed).
- **SLAUGHTER** (signs.py), read for the day and the next by spot_rows, each row by its reach:

  | Row | Sense | Chance | Who |
  |---|---|---|---|
  | "Ivo killed a cow of the Hobb cattle on the Common today: the cow went down kicking, and the blood ran out on the ground" | sight | 1.0 | at the parcel today, not the doer |
  | "the cow was butchered where it fell ...: the hide stripped off, the guts heaped steaming on the grass, the meat cut from the bone" | sight | 0.8 | at the parcel, not the doer |
  | "the hot, iron smell of blood and opened guts on the Common" | smell | 0.9 | at the parcel |
  | "a cow bellowing on the Common, a heavy fall, then quiet: a beast killed there" | sound | 0.95 x the sound visibility | at, crossing or next to the parcel, not the doer |
  | "a beast's bellow from toward the Common, cut off short" | sound | 0.4 x the sound visibility | anyone at the place, not the doer |
  | "the cow kicked as it went down, and its blood ran hot over your hands: you are red to the elbows and stink of it" | touch | 1.0 | the doer only |
  | "the Hobb cattle are uneasy on the Common, bunched and snorting at the smell of blood" (a herd still there) | sight | 0.4, the rule (own 0.95), herder's knack | |
  | "the dogs are wild at the smell of blood from the Common ..." (a dog at the place) | sound | 0.5 | anyone at the place |
  | "crows and kites dropping onto the Common, after the leavings of a slaughter" (not in fog; today and tomorrow) | sight | 0.6, the rule (own 0.9) | |
  | "blood in the snow on the Common, trodden pink ..." (snow lying; today and tomorrow) | sight | 0.9 | at the parcel |
  | "a dark patch soaked into the ground on the Common, flies on it: the blood of the beast killed there yesterday" | sight | 0.8 | at the parcel, the next day |
  | "a smell of old blood and offal hangs over the Common" (not frost) | smell | 0.6 | at the parcel, the next day |

- **PERSON:** one who slaughtered today is seen "with blood to the elbows and down their front, from butchering a beast" (sight 0.6)
  and smelt (0.3); their household reads it as if inside; they do not read it of themselves.
- **Reach at a spot:** rows read by spot_rows take the reach thing rows already had: "near" (one who was at the parcel today: worked
  there, was about it, attended to it), "around" (also one who crossed it or worked next to it), "node" (anyone at the place); "rule"
  stays the default (things.near_spot). A row's `who` ("others", "doer") limits who reads it. A fact limited to some people (`only`)
  no longer reaches others through "what one worked on, one sees".
- Checked: one working on the Common reads the kill with certainty; one gathering firewood in the Copse (not next to it) reads
  something of it with a chance of about 0.41 (mostly the bellow); one on the Infield next door hears it at 0.95.

Blood, guts, crows and the bellow are how a slaughter record shows: a presentation choice, deterministic, named here. The hide is not
said to be pegged out: the engine has no tanning and the hide lies in hands or a store.

## The audit, ranked

Ranked by how hard the thing would be to miss in life, how much it matters to others (danger, food, kin), and how thin it shows now.
"State" is what a bundle would read; "(new)" marks a small record the engine would need, as the slaughter record was.

1. **Night fights, beatings and killings** (settle.py:104, 114, 117; set up at verbs.py:943-955). One sight line each, node-wide, at
   night; no sound for neighbours (shouts, blows, a scream), nothing on the ground next day where it happened (a killing leaves a body
   with THING rows; a beating leaves nothing); the wounded show only through PERSON's two sight rows (signs.py:543-544). State: the
   night's fight records (by, target, outcome, took), `wounded`; (new) a parcel or building record of the fight for the aftermath.
2. **A hunting kill** (verbs.py:342-353). A `work` event, routine: no one else knows a deer was killed. No blood on the ride, no beast
   gralloched, no carcass carried in; only PERSON's load row. The same shape as slaughter. State: the catch (got, the hide by-product),
   the parcel, the hunter; (new) the same per-parcel record.
3. **A fire in a house** (run.py:379-387). One dawn line; no glow, crackle or shouting in the night for neighbours, no charred thatch or
   smell of burnt grain in the days after; BUILDING shows only the lower condition. State: the fire incident, the building, what burnt;
   (new) a building record of the fire's day.
4. **A birth** (life.py:412). One line; no labour heard from the house in the night, no one fetched; after, BUILDING's baby crying and
   PERSON's baby on the hip (signs.py:558-561) carry it. State: the birth (mother, child, house).
5. **Food rotting in a store** (night.py:141-157). Spoilage makes "rotting meat" in a house's stock, but BUILDING has no smell row for
   it (THING has, for piles in the open: signs.py "the stink of meat gone bad"). State: the stock's rotting goods.
6. **A guard posted** (verbs.py:960-963). No sign at all that someone sits up by a door with a club; it matters most to the one
   deciding whether to break in. State: today's guards, the guard's weapon.
7. **Beasts driven across the place** (farm.py:492-545; the event at 541 is kind `work`, routine). No one sees or hears cattle moved;
   HERD and ASTRAY show only where they end up. State: the drive (from, to, which beasts, by whom).
8. **A weapon being made** (verbs.py:448; BUILDING's made rows, signs.py:514-525). Made rows cover bread, grinding, smithing, cheese,
   dried meat and smelting; nothing for crude weapon, crude tool, wooden plough, handcart, harness, tent, bedroll or pack. A club or
   spear being shaped is the one others most need to know of. State: today's make events and their technique.
9. **Sleeping out on a cold night** (night.py:28, 80-99). Only the sleeper is told; no PERSON row for others (shivering, frost on the
   blanket, stiff in the morning). State: where each slept, the cold; (new) a person field for the night, like `ate_raw`.
10. **Ploughing and reaping** (farm.py:354, 378). One sight row each on the result (FIELD "dug over" 0.15; CROP "sheaves stooked"
    0.25); no sound of the ox team or sickles, no harvest bustle. State: today's work events by technique (as WILD reads felling).
11. **Quarrying and mining** (verbs.py:354-357). No sound of picks; WILD shows the seam only. State: today's work events.
12. **Theft from a store** (settle.py:194-199). Two single lines; nothing on the building (a gap in the wattle, bins disturbed).
    State: the night's thefts.
13. **Calving** (farm.py:704). The event and HERD's new-calf row (sight 0.45); no lowing for the calf, no afterbirth. State:
    `last_calf`.
14. **A house falling in, a house mended** (night.py:161; verbs.py:381; BUILDING's mended row, sight 0.3). No sound of the fall in the
    night; mending is silent. State: condition, today's repair events.
15. **A burial** (verbs.py:372-380). The act shows nothing (no digging, no one at the graveside); THING's grave rows after. State:
    `buried`, today's bury events.
16. **Old age, illness** (signs.py:568, one sight row; life.py:473). "A sudden illness" is only a cause of death: the engine holds no
    illness before it, so nothing can show (an engine gap, not a sign gap).
17. **A threat** (verbs.py:949). One sight line, node-wide; no raised voices. State: today's fights.
18. **Milking, herding, caring for a child.** No signs; routine, low.

## Sources

runs/p1_combe_evening (days 26 to 39); signs.py, perceive.py, things.py, farm.py; proposals/slaughter_signs.md; D4-71.
