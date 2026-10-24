# c2viz: what the engine is, and what may be drawn of it

The visuals are drawn from the engine, never fitted by eye (Zach, 24 Oct; CLAUDE.md "Visuals are drawn from the engine"). This
file is the model the renderer is built on: for each part of the world, what the state holds (keys, ranges), what changes it and
when, what a picture should convey, and what is only in the spec. Read against `wp/cybertron2` at aa52b92 (code) and the spec of
24 Oct. Where code and spec differ, the code is what a run did; the spec is the end state the renderer must also support (Zach:
"buildings are going to change ... your engine should support that end state").

**Rule for every picture:** show only what the state holds, at the resolution it has. Anything the engine does not decide (a
position inside a parcel, a building's outline) is a *presentation choice*: it is named as one below, made deterministically
from the state, and never read back as fact.

## 0. The engine's ontology (review 38.17, core/architecture.md)

1. **Everything has a place** (D4-35). A parcel, building, herd, offer or container is at a node; a person is at a node or on a
   road; hands are where their person is; every event is at a node or a road.
2. **Every physical change is a primitive** through `World.apply(primitive, place, **payload)` with a cause `{actor, verb, for,
   node, within?}`: `transfer`, `create`, `destroy`, `draw`, `wear`, `set`, `admit/leave/found`, `claim/end_claim`,
   `agree/settle`, `depart/arrive`, `transit`, `traces`, `harm/die`, `learn`, `raise`, `office`, `close_offer`. The journal
   records each one (`changes`), so every visible change has a cause that can be drawn.
3. **Agents see only `Here` and `Mind`.** Knowledge (`mind`, `know`) is written by perception, outside `apply`, and is in the
   checkpoints only.
4. **Data is tables** (`data.py`): COVERS, ITEMS, DECAY, FITTINGS, BLUEPRINTS, TECHNIQUES, THINGS, PHYSICS, HERDS, LAYOUT,
   ENV, WEATHER, NOTICING, TERRAIN, FUSE, ROADS. The renderer imports them (frozen per run in the journal's `data` table); it
   never keeps its own copy of a rule.

**Resolution.** Nothing inside a node has a position (layout.py:1-9; world/parcel_graph.md). The finest places are: a parcel
(its `size`, `adj`, `side`, `height`), a building (on a parcel), a thing (on a parcel, `in` a building, or at a building's
`door`), a road stretch. Distance inside a node is steps on the parcel graph.

## 1. The source: the run journal (spec/record/; journal.py, views.py)

- `run.db` (SQLite) holds: meta and provenance; frozen `data` tables; `steps` and `segments`; every request and response; a
  **checkpoint of the whole `World.s` at every committed step** (`d{d}.dawn`, `.decide`, `.talk.N`, `.work`, `.settle`,
  `.night`, `.memory`); every event with its cause; every change (`apply`) with primitive, place, args, cause, result.
- `views.py`: `state(run, step)`, `beliefs(run, agent, step)`, `context(run, key)` (the exact prompt an agent saw),
  `events`, `changes`; `frames(run)` is minimal (people at node points, events) and the spec's richer frames (people at their
  parcel, acts in order with changes highlighted) are not built.
- **A day's picture** is the state after its night: the `d{d}.memory` checkpoint. `fire` and `warm` on buildings describe the
  night just passed. Within a day, the `work` step's changes, in their journal order, are the day's acts as they happened.
- **Not in the journal:** perception facts (only in `perception.jsonl`, overwritten on resume) and the noticing chances (never
  stored).
- c2viz's `capture.py` was a stand-in from before the journal; c2viz reads the journal.

## 2. Land, space and the environment (world.py, layout.py, farm.py, forests.py, environment.py, roads.py)

### Places and parcels
- `nodes[nid] = {name, text, unexplored}`: a village or valley small enough to go out and back in a day; moving inside it costs
  nothing. `unexplored` is about who knows it, not what exists: the place is drawn as it is.
- `parcels[pid]`: `node, name, text, cover` (forest, field, pasture, meadow, water, built, scrub, rock), `size` (int ≥ 1),
  `adj` (two-way), `side` (centre, north, east, south, west), `height` (0 by the water, 1 valley floor, 2 slope, 3 hilltop),
  `res {key: {S, K, r, kind?}}`, `crop`, `fertility` (≈ 0.4-1.2: worn out < 0.55 < tired < 0.8 < good < 1.05 < rich),
  `broken` (plots dug, 0..size), `last_crop`, `last_kind`, `fallow_since`, `ground` (None, wet, hill), `works`, `fence`,
  `clearing`, `was` (the cover before).
- **A unit of size is the same area on every cover**, and the code relies on it: a field's unit is a plot (about 16 seed, an
  adult's season of tillage); clearing turns `size` units of meadow into `size` plots; forest stocks, grass (25 a unit) and lots
  are per unit; fences cost × √size (a perimeter). So parcel area is drawn in proportion to size, one scale for all covers.
- **No geometry.** `adj` is the only spatial fact; `side` and `height` are words (side is read by road ends and words; height
  only by words: flow downhill is spec only, OPEN L-23). `adj` need not agree with side; a parcel may have no neighbours. Worlds
  differ: region_s1 sets no side or height (all centre, 1) and has sparse `adj`; wide_s7 sets both everywhere.
- **Holding** is a record (`claims`), never a structure: shown as an overlay (a household's colour), not on the land. The only
  physical bounds are fences and walls.

### Resources (draw S/K, never S: magnitudes differ between worlds)
| stock | where | taken by (day) | at night | picture |
|---|---|---|---|---|
| plants | forest, meadow, pasture, scrub | forage | logistic regrowth, ×0.25 in winter | picked over or thick |
| game | forest | hunt (chance 0.35 S/K) | logistic, none below 0.15 K | not a beast: signs only |
| wood (trees) | forest (FORESTS kinds: old forest, managed wood, copse) | fell (+ brash to dead) | slow growth; gale throws trees | standing trees in proportion; stumps; S/K < 0.3 **felled** (open to sight); < 0.4 the cover becomes **scrub** (`was: forest`), back at ≥ 0.45 |
| young | forest, scrub | cut | regrows, not where a herd stands | coppice shoots |
| dead | forest, scrub | firewood | shed, rot, gale | fallen wood |
| seam | rock | mine | none (finite) | a green-stained seam, worked out at 0 |
| quarry | rock | quarry (draws nothing) | none | a face of stone |
| grass | pasture, meadow (25 a unit) | hay (summer), herds eat 1 a head | logistic | green or grazed bare |
| dung | where herds stand | gather dung | + head × 20 / year | dung lying thick |

Water has no state (no flow, level, fish or flood): a cover, a pull for thirsty herds, a water wheel's site. A river's course
across a place is a presentation choice (a chain of water parcels through their neighbours).

### Fields and crops (farm.py)
- `crop {kind, crop (grain, winter grain, legumes), sown, ripe_day, window (2), seed, area (plots sown ≤ size), area_left,
  broken, weeded, base, rot, left (what reaping now gives), failed, hardy, sower, shown_failed?, killed?, rotting?, reaped?,
  trampled?}`; CROPS: grain a quarter of the year, winter grain a third, legumes a sixth.
- **Stages, by the engine's own rules:** dug (`broken/size`, no crop); new sown (progress < 0.25); green; high (≥ 0.6 of its
  growing time: also halves sight); ripe (`d ≥ ripe_day`); rotting (`d ≥ ripe_day + window`); blighted (`failed` and
  `shown_failed`); frost-killed (`killed`); partly reaped (**the reaped share is `1 - area_left/area`**; `left` is yield, not
  area); stubble or fallow when the slot ends (`crop None`, `last_crop`, `fallow_since`).
- **Sown share** is `area/size`: the rest of the field is unsown ground, not crop.
- **Works:** `{ground wet|hill, done (plots, 0..size), units, kept, pending}`: ditches and banks on wet ground, stone terraces
  on hill ground; `done/size` made; unkept works lose a quarter a season.
- **Fence:** `{kind wood|stone, level 2 whole|1 gappy|0 down, built, gate open|shut, mend, pending}` round the whole parcel.
- **Clearing:** `clearing` units toward `CLEARING[cover] × size`; then cover becomes field.

### Time, weather, light
- No time is stored but the day: `calendar(day)` (season, day of season, year day; four equal seasons), `cold(day)` (winter or a
  listed cold day). A day has work units (summer 7 ... winter 5), no hours. Night is one state, not a gradation.
- Weather is computed, one for the whole world: pinned in the spec, else drawn by spell (`environment.weather`); rain on a cold
  day is snow; `snow_lying` after snow until 3 days without frost. WEATHER: clear, rain, heavy rain, fog, snow, gale. A gale
  throws trees and is loud; it does not damage roofs (words only).
- **Visibility** (computed per parcel and sense): cover base × felled × high crop × smoke × weather × masking. Smoke on a parcel
  today: charcoal, smelt, dry meat, smithing, a fire.

### Roads
- `roads[rid] = {a, b, days, track, way, terrain, stretches: [{terrain, landmarks: [{kind, state?}]}], ends: {node: {side,
  parcels, hidden, worn, used}}}`. A road leaves a place **from its end parcels, on its end's side**; length is in days, one
  stretch a day, each with its terrain (TERRAIN) and 0-2 landmarks (ford, bridge, pass, narrows, spring, meadow, fruit trees,
  hollow); challenges computed (ford high after heavy rain, pass snowed in winter, bridge down if seeded).
- A **hidden end** is known by those who found it, came by it or were told, and to all once worn to 0.8 (about 16 passages);
  `worn` regrows in forest and scrub. Drawn faint, firmer as it wears.
- **Traces** `traces[] = {road, pos, day, kind tracks|ruts|ashes, n, toward}`: tracks 3 days, ashes 10, ruts 60.
- A traveller is drawn at the middle of their stretch: `(position - 0.5) / days` from `a`.
## 3. Buildings (spec: economy/buildings.md, the end state; code: world.py, verbs.py, night.py)

### The end state (spec, D2-154, D2-155; to be built in Package E)
- **The space** (about 5 m², the floor a bed takes) is the one unit from land to fitting.
- **Ground:** built ground has 24 spaces a unit of parcel size, scrub 16; other covers none unless cleared (a field, pasture or
  meadow becomes built ground with work; a wood becomes scrub when felled, then built ground).
- **A building:** one structure (wattle, timber, stone; a camp) for all its rooms; **rooms** of 6 (small), 12 (medium), 30 (hall)
  spaces, wattle only small; adjoining rooms a quarter cheaper; **storeys** 2 and 3 only in stone, taking no ground; the
  **footprint** is its ground-floor rooms (plus a woodshed's 2 spaces of ground).
- **Fittings take floor:** bed 1 each, bins 1, hand mill 1, fire ring 1, hearth 1, oven 2, anvil and bellows 2, granary floor 3,
  dressed millstones 3, stalls 2 a beast, vault 4 (its own stone room, ground floor); water wheel 0 inside (on the water, needs
  millstones and a river site), cellar 0 (underground, one a building), woodshed 0 inside (a lean-to, 2 spaces of ground).
- **Stores:** free floor 30 weight a space; bins 60 food; granary 300 grain; cellar 40 food a space of footprint; woodshed 40
  timber; vault 30 weight a space and does not burn. Stores cannot take more than they hold.
- **Condition and upkeep:** sound, damaged, ruined; breaks a night (more in the cold); mended with 2 timber and 2 units;
  upgrading a structure counts as damaged while under way; stone walls stand in a fire (roof and contents can burn).
- **Rooms can be booked**; who may use a room is its access. Seeded buildings get floor enough for what the world file puts in
  them.

### The code now
- `buildings[bid]`: `node, parcel, name, structure (wattle|timber|stone|camp), size` (people: caps beds, spreads a hearth's
  warmth; **not** footprint), `fittings {name: count}` (beds a count), `condition` (2 sound, 1 damaged, 0 ruined), `door`
  (open|barred), `fire` (lit last night), `warm` (0..1, last night), `stock` (`stock:{bid}`), `unfinished`
  (`{blueprint, units_left}`), `built_day`, `lasts_until` (camps).
- **Lots** are a count, not area: COVERS lots built 6, scrub 4 a unit of size; enforced only in `verbs._build`; a camp skips
  it (not on water). No rooms, storeys, footprint, floor or storage capacity exist in code; stores hold any amount.
- **Holders** come from claims (`w.claims_on(("building", bid))`), never stored on the building. **Sleepers** come from the
  night log (`log[-1].hearth[bid] = {sleepers, lit, warm}`, `slept {name: building | out}`).
- Breaks: 0.02 a night, 0.08 when cold. Repair: `work {what: repair}` 2 units, 2 timber, +1 condition. Camps fall in at
  `lasts_until`. A building fire is only a scripted incident (85% of food stock, 50% of the rest, condition −1).
- Heat: a building with sleepers and a hearth or fire ring burns fuel from its own stock (firewood, timber, charcoal); `warm =
  min(1, (12 × hearths + 6 × rings) / size)`.
- Production by fitting (TECHNIQUES `at.fittings`): hand mill grind; millstones mill (with an ox); water wheel water mill;
  hearth bread and dry meat; oven bread in batches; anvil smelt, copper tools, coin; cellar cheese. Smoke: charcoal, smelt, dry
  meat, smithing. Loud: mill, water mill, grind, smithing. LAYOUT.seen names what a building is seen as (a mill, a smithy).

### What the renderer does (and what is a presentation choice)
- **The building model is the spec's.** A building is drawn from rooms (each a rectangle of its floor in spaces, storeys,
  structure), fittings placed in rooms, stores, a footprint taken from its parcel's ground. When the state has rooms, they are
  read. **Until then they are derived** by the spec's seeding rule: the floor its beds, fittings and stores need, split into the
  fewest rooms of 6, 12 and 30 the structure allows. Derived rooms are marked so in the data.
- **A parcel's ground** is drawn as used and free (24 or 16 spaces a unit of size), so a full village is visibly full.
- **Presentation choices:** where in its parcel a building stands (lots spread through the parcel, kept from the day it first
  stands); the layout of its rooms (a row or an L, by count); the pixels a space takes (the same everywhere).
- **Shown from the state:** structure (material), condition (sound, damaged: slipped thatch and a cracked wall; ruined), the
  frame of an unfinished one and its work left, new (green wattle, 3 days), the door (barred), fire and smoke (last night),
  warmth, crowding (sleepers above beds), activity (the day's `make` events at it: grinding, hammering, baking, the wheel
  turning), the woodpile (stock timber and firewood), a camp's lean-to and its nights left.

## 4. People and the body (world.py, night.py, life.py, things.py)

- `people[name]`: `at` (node id, `None` on a road), `transit` (`{road, from, to, left, arrive, choices, notices, last_pos,
  turned?, with?, carried_by?}`), `stage` (infant, child, youth, adult, elder; from `born` and `LIFE.shares` of `lifespan`),
  `sex`, `born`, `alive`, `died`, `cause`, `hunger` (0 fed, -1 hungry, -2 starving), `missed` (nights without a ration),
  `wounded` (bool; **never heals** in code or spec), `frailty`, `attack`, `defence`, `hands` (`hands:{name}`: the carried
  container, with gear: weapon, tent, bedroll, pack, handcart), `pregnant`, `partner`, `parents`, `arrived`, `ate_raw`,
  `home_seen` (the house as last seen on leaving), `cared` (infants and children).
- **No position below the node.** Where someone is on a parcel is *derived*, as the engine derives it (`things.spot_of`): the
  last parcel or building worked today (`today.worked[name]`, in act order), else their home's parcel here, else the built
  ground, else the first parcel. The renderer uses this rule and nothing else. Acts that work nowhere (build, move, talk, trade,
  care) leave a person at their home.
- **Home** is derived: `w.homes(name)` (buildings their household or they claim with access, finished), `w.dwellings` (with
  beds). **Where one slept** is the night log: `log[-1].slept = {name: building name | "out"}`.
- **On a road:** stretch `clamp(days - (arrive - d) + 1, 1, days)` from the road's `a` end (`roads.position`); parties are
  travellers with the same `(road, from, to, left, arrive)`; they sleep out (gear, camp, open fire) and eat from their hands.
- **The body over a night** (night.py): sleeping place (dwelling, else a free bed one may enter, else out) → fires (`warm`) →
  food needed (housed 1.0; damaged 1.2, cold 1.5; out 1.5, cold 2.0; gear and open fires lower it) → eating (hands, then
  stores one may withdraw from, then carers' hands; without a lit fire cookable food counts raw) → hunger ±1, `missed` →
  the cold's fall (0.3 to starving when unsheltered in the cold) → starvation from 3 missed nights (certain at 6).
- **Work capacity** (`units_for`): summer 7, autumn 6, winter 5, spring 6; youth ≤ 4, elder ≤ 5; hungry −1, starving ≤ 2,
  wounded −2, late pregnancy −1. Yield ×1, 0.75, 0.5 by hunger.
- **Life:** conception at night (partners, same bed, fed), pregnancy 5 days (scaled), birth where the mother is, infant and
  child deaths by care and hunger and cold, old age. Stages at lifespan 32: infant 2, child 4, youth 6, adult 20 days.
  Infants and children are not agents (seen, never asked).
- **Death** (`p_die`): a `remains` container at the spot of death (or `in` the house, or on a road stretch) holding what they
  carried (or the killer takes it). Body: fresh, days (≤ 10), bones; rotting from 2 days unburied; burial sets `buried` (a
  grave; a sunk mound after 7 days) or a `cairn`. Bodies are never removed.
- **Signs of a person** (signs.PERSON): well fed / drawn and hungry / gaunt and unsteady; moves stiffly (wounded); bereaved;
  pregnant and showing; a baby on the hip; leading an ox; just arrived, soaked; failing (old); carrying a weapon, gear, a load.

**Drawn:** a person on their derived spot, by stage (infant carried, child small, elder stooped), with hunger, wound,
pregnancy, a baby, what they carry (weapon, load, gear) and the tool of the day's act; at their dwelling's door if they did not
work; sleepers in their house at night; travellers on their stretch. Every mark has a key in the state behind it.

## 5. Herds and game (farm.py, herds.py)

- `herds[hid]`: `node` (a node, or a road id), `parcel`, `home` (where it walks back at dusk), `pos` (stretch on a road),
  `kind` (only `cattle` in code), roles `cows`, `oxen`, `bulls`, `young` (calves never grow up), `count` (their sum; 0 = gone,
  skip), `in_milk`, `milked {day, n}`, `hungry` (nights unfed), `watched` (day herded), `herders`, `ate` (a crop trampled),
  `lost`, `strayed_in`, `with`, `pack`. **Holders** come from claims on `("herd", hid)`.
- **Movement at night** (`herds.night`): stays if herded today or a fence holds (wood 0.3/0.6, stone 0.05/0.2 by level);
  else 0-1 steps on good grass, 1-8 when hungry or drawn by a ripe crop, along `layout.path`; 0.1 a step onto a road from a
  parcel a road leaves from; tramples a crop 1% a head; home at dusk (0.8 for cows in milk). Splits over capacity (6 unherded,
  30 a herder), rejoins on the same parcel.
- **Eating:** trampled crop, then `res.grass`, then hay and straw from holders' stores; hungry from < 90% of a ration; ribs
  showing at 2 nights, a beast dies a night from 4 (a carcass). Calves with a bull when fed; milk fades; dung into `res.dung`.
- **Carcass:** `{kind: carcass, node, parcel or stretch, beast, of, holders, cause, died, hidden?, goods {meat, hide}}`; meat
  turns rotten after a day, bones after 6, gone from view at 18.
- **Game is not an entity:** `res.game = {S, K, r}` on forest parcels; hunting draws it; it regrows logistically.

**Drawn:** each head by role (cow, ox, bull, calf), on its parcel; with its herder when watched; ribs when hungry; a herd
astray off its home; on a road at its stretch. Wild animals are not drawn as beasts (they are a stock), only as signs.

## 6. Acts and their effects (verbs.py, world.py apply, farm.py, settle.py, agreements.py)

- **The day's acts** are the work step's changes, interleaved (round i runs each agent's i-th act in a keyed shuffle); the
  journal's `changes.seq` is the order. Up to 10 acts each within the units budget; travel ends one's acts.
- **Act record** `acts[]`: `{day, actor, verb, tech, for, node, site?, ...}` written by techniques (site = parcel, building or
  remains), make (no site; the event's `about` is the building), build (no site; the event's `about`), thefts, gives (`to`,
  `item`, `qty`), accept, drive (site). Many verbs write none (move, travel, attack, guard, watch, teach, sleep, host, grant,
  claim, join, set, fire, try, rest): their intents are in `today` and the night log.
- **Primitives** (`World.apply`, journaled with cause): `transfer`, `create`, `destroy`, `draw`, `add_res`, `set_res`, `wear`,
  `set`, `raise`, `claim`, `end_claim`, `new_thing`, `set_thing`, `depart`, `arrive`, `transit`, `harm`, `die`, `admit`,
  `leave`, `found`, `office`, `partner`, `born`, `learn`, `offer`, `close_offer`, `agree`, `leg`, `close_agreement`, `traces`.
- **Technique → place → state → trace** (data.py TECHNIQUES, one handler `_technique`; every use appends the site to
  `today.worked`, wears the tool, emits a `work` event about the site):

  | Technique | Where | Changes | What is left to see |
  |---|---|---|---|
  | forage | forest, meadow, pasture, scrub | `res.plants` | picked over |
  | hunt | forest | `res.game` (chance) | weapon wear; tracks thinning |
  | fell | forest | `res.wood` → timber, `res.dead` += brash | stumps, brash; a wood no longer |
  | firewood, cut | forest, scrub | `res.dead`, `res.young` | |
  | mine | rock | `res.seam` → ore | the seam worked out |
  | quarry | rock | stone (no draw) | only the event |
  | hay, dung | pasture, meadow (field for dung) | `res.grass`, `res.dung` | mown, grazed bare |
  | clear | meadow, pasture, scrub | `parcel.clearing` → cover becomes field | the cover changes |
  | hoe, plough | field | `parcel.broken` (+ stone) | dug over |
  | sow | field | `crop {kind, sown, ripe_day, window, area, area_left, left, ...}` | sown share `area/size` |
  | weed, manure | field | `crop.weeded`, `fertility` | |
  | reap | field (ripe) | `draw crop`: `area_left` falls | reaped share `1 - area_left/area`; stubble when the crop ends |
  | ditch, terrace | field | `parcel.works {done, ...}` | half made, made |
  | fence, wall, gate | pasture, meadow, field, scrub | `parcel.fence {kind, level, built, gate}` | fence, gaps, gate open |
  | herd, milk, slaughter, drive | where the herd is | herd `watched`, `milked`, roles, `parcel` | herder by the herd |
  | repair | a building | `condition` +1 | fresh timber |
  | bury | a body's spot | `buried`, `cairn` | grave, cairn |
  | make | a fitting's building (or a forest: charcoal) | goods created and destroyed | grinding, smoke, hammering |
  | build | built ground or scrub (a camp anywhere dry) | `raise`, `unfinished.units_left`, fittings | a frame, then a building |

- **Talk:** `say` (to everyone at the node or a building's users; event `speech` without the words), `tell` (private, no event),
  `explain`; offers (`offers[]`, no event), accept (`agreements[]`, event `trade`), settlement of legs (cause verb `settle`).
- **Conflict, all settled at night:** attacks on a person (kill only when the aim is hurt; wound takes the food carried;
  repelled), raids on a building (stone ×2, barred ×1.5; half the food store), fuse calls (defend, flee, alarm, hand over),
  thefts seen or found missing at settle; outcomes in `log[-1].fights` and events `death`, `fight`, `raid`, `alarm`, `theft`,
  `loss`, `threat` (when squaring up, by day).
- **Events** `{id, day, place, kind, actor, target, about, text, salience, tags, sense, concerns, tech?, dawn?}`; cleared at
  dawn in the state, kept in the journal.

**Drawn:** within a day, the acts in journal order, each at its site with its tool, and its change on the land as it happens
(the reaped share grows strip by strip, a tree falls, goods move from a field to hands to a store); for the day as a whole, the
end state and a mark for each event at its extent (a parcel, a building, the whole place). Speech as a bubble from the speaker
to its hearers, never with words the event does not carry (the words are in the hearers' minds and the journal's responses).
## 7. Senses and perception (perceive.py, things.py, signs.py, environment.py; information/*.md)

### The day
dawn (incidents, arrivals, dawn notices) → decide (prompts) → talk waves (speech into `mind.today.heard`) → work (acts; each
appends its parcel or building to `today.worked[name]`) → settle → night (departures, roads, raid detection, `N.night`, then
**the evening's noticing** `PC.evening`, then `close_day`) → memory (stretch memories; `perception.jsonl` written).

### Facts
Every candidate fact at a node, built once per evening: `{id, about: [person:|building:|parcel:|herd:|thing:|sky], sense,
text, salience, tags, concerns, spot|at: {node, parcel, own, inside, everyone}, ...}`. Sources:
- **ambient** lines of each cover (COVERS.ambient): never noticed, only when one attends to "the place";
- **signs** regenerated each evening from the state (signs.py tables CROP, FIELD, PASTURE, HERD, TRAMPLED, ASTRAY, EMPTY, FENCE,
  WAY, CARCASS, SKY, WILD, BUILDING, PERSON, THING): a sign lasts exactly as long as its condition holds. Only **traces** on
  roads are stored objects (`w.s["traces"]`: tracks 3 days, ashes 10, ruts 60);
- **things** at a spot (piles, remains, carcasses);
- **events** at the node, by extent (EVENT_EXTENT): node-wide (death, fire, alarm, fight, raid, arrive, depart, ...: everyone),
  building (store, put, left, make, host, build, birth: those inside), else the parcel. Routine events (work, make, store,
  take, give, trade, teach, build) are never *noticed*, though they set presence and teach by sight.

### The noticing rule (things.py:171-252)
`p = salience × knack × min(1, own × visibility(node, parcel, sense) × presence(name, parcel, own) × attention × eye)`.

- **Presence** of an observer on a parcel, first match: worked there (by what the technique draws: game 1.0, plants 0.7, herd
  0.5, work 0.5); its spot today 0.5; a home parcel 0.3; passed through on the shortest way from where it slept (0.3); next
  door to where it worked (0.1, things of own ≥ 0.5); elsewhere at the node 0.05 (own ≥ 0.8).
- **Visibility** = cover base (sight: forest 0.35, built 0.7, scrub and rock 0.5, open 1.0; sound: forest 0.7, scrub and rock
  0.9, else 1.0) × the land's state (felled wood opens to ≥ 0.8; a high grain crop ×0.5; smoke ×0.7) × weather (WEATHER: fog
  sight 0.3; gale sound 0.5; ...) × loudness masking.
- **Attention** ×3 on the parcel attended, ×5 if also worked there. **Eye**: none, ordinary, keen (×0.5, 1, 3 on things).
- Selection: things concerning one are always seen; the rest are drawn with `rng("notice", day, name)`, ranked, top 5 kept
  (+2 when attending the place); attending a subject shows up to 9 facts about it without a draw.
- Speech is not noticed: `say` reaches everyone acting at the node (or with access, in a building); `tell` the one told.
- Travellers: road notices each night (signs ROAD, THING, TRACE, TRAVELLER) into `transit.notices`, shown on arrival.

### What one knows
`mind[name]`: `days`, `beliefs{subject: {day, lines}}`, `places{node: ...}`, `ways`, `landmarks`, `things{cid: {text, close,
day, how, node, parcel}}`, `beasts`, `land{"pid|what": {day, state, how}}`, `kin`, `today{dawn, notice, attended, concerned,
glimpse, felt, learned, heard}`, `log`. `know[name][tech] = {level: aware|rough|capable|known, skill, ...}`. While at a node an
agent is shown every parcel and building in full (the static layout is always known there); only signs and events go through
noticing.

### For the picture of "what X saw on day d"
- From the journal: the `d{d}.memory` checkpoint (`mind`, `today.worked`, events), `perception.jsonl` (fact ids noticed,
  attended, concerned; the facts themselves), `context(run, "d{d}.decide.X.1")` (the prompt).
- **Computed by the engine's own Python, never re-implemented in JS:** presence per parcel and why, visibility per parcel and
  sense, eye, attention; each fact's chance against whether it was noticed. c2viz's `perceived.py` rebuilds the `World` from the
  checkpoint and calls `things.presence`, `environment.visibility`, `layout.passed`, `layout.next_door` (the shortest-way tie
  break uses the engine's keyed Python rng, so only Python reproduces it).
- Drawn as: a presence wash over the parcels (worked / passed / next door / elsewhere), the facts placed on their spot
  (noticed bright, missed dim), speech heard as lines from the speaker.

## 8. The framework, from the general model up

Two halves, so that every rule stays in the engine:

1. **The model (Python, `c2viz/model.py`)** reads a run's journal, rebuilds the `World` from each day's `d{d}.memory` checkpoint
   (`World(spec)`, then `w.s = checkpoint`), and calls the engine's own functions for everything computed: `calendar`, `cold`,
   `environment.weather / snow_lying / felled / smoky / crop_high / visibility`, `things.spot_of / body_state / rotting /
   carcass_fresh / at_node`, `roads.position / challenge`, `layout.passed / next_door`, `farm.soil_word`, `w.homes`,
   `w.claims_on`. It writes `viz.json`: the engine's tables (COVERS, CROPS, FITTINGS, BLUEPRINTS, FENCES, WEATHER, LAYOUT.seen,
   THINGS, TERRAIN, LANDMARKS, and the spec's space table until the engine has one) and one record a day in the engine's terms.
   Every value is one of: **state** (read), **engine** (an engine function's result) or **spec** (the spec's end-state model,
   derived until built: rooms, footprints, ground in spaces). None is a guess.
2. **The renderer (JS, `c2viz/pixel.js`)** only draws that record, in layers, each depending on the ones before:
   1. **places**: the node graph (roads, days) and each node's ground plan from its parcels' size and `adj` (presentation:
      the plan's geometry, named in §9);
   2. **land**: each parcel by cover and its stocks (S/K), crops by stage and share, works, fences, clearing; the weather and
      snow over all;
   3. **structures**: buildings from rooms and fittings at the space scale, on the parcel's ground (used and free); things
      lying; road ends from their parcels and sides;
   4. **beings**: people at their spot, herds by role on their parcel, travellers on their stretch;
   5. **the day's acts and events**: tools in hand at the site; marks by extent; later, the acts in journal order;
   6. **senses** (later): one agent's presence, visibility and what it noticed.
   Each layer reads only the day's record and the tables, never invents a rule.

## 9. Presentation choices (named, deterministic, never read back as fact)

- **The ground plan:** a parcel's area is its size × 2,600 close-up pixels (one scale for all covers, as the engine's units
  are); neighbours (`adj`) share a border, non-neighbours are kept apart with wild ground between; `side` pulls a parcel that
  way; fields are squared off along their strips. A chain of water parcels is drawn as one river through them to the map's
  edges. The wild country around a place is drawn by the place's character; it is not state.
- **The space** (spec: about 5 m²) is drawn as 54 px² close up: built ground at its 24 spaces a unit would then be half covered
  by building when full, leaving lanes and yards.
- **Where in a parcel** a building stands (its lot, spread through the parcel, kept from the day it first stands), a person
  stands (around the parcel the engine says they are on), a beast grazes.
- **Roads' ways:** a curve through a few waypoints set off to either side of the straight line (deterministic per road); on the
  region's map each day's stretch, its landmarks and any river at a ford or bridge sit on that way.
- **Height** (a word in the engine) as terraces and cliff faces: a parcel above its neighbours to the south shows a face.
- **The region's map is a schematic at a fixed scale, explored by panning:** each place's plan at half its close-up scale (its
  houses drawn half as large again so a village stands out), roads about 60 pixels a day of travel beyond the two places' land,
  places pulled together along their roads and pushed apart until their land clears. A larger world is a larger map, not a
  smaller drawing.
- **The landscape between places** is built from what the engine says, and only that: a place stands at its parcels' height
  (0 to 3, or 4) or, where a world sets no heights, at a height from its rock and scrub and its name (a crag, a tor, a pass, a
  fell: hills; a moor; a mere, a fen, a carr: wet); an upland place is ringed by peaks, clear of its roads; each day's stretch
  of road stands at its terrain's height and carries its terrain (TERRAIN: woodland grows forest, marsh is wet, a river valley
  is low, hills and mountain are high); a pass is a ridge of peaks with a saddle where the road goes over; narrows are rocks by
  the road; a hollow a dip; a ford or a bridge is a river crossing the road, running from a short way above it down towards the
  nearest water (a place's water, a marsh, the map's edge). Between these the land eases from one to the next with some noise;
  its kind follows from its height and wetness (low ground, slopes, hills, mountain with snow on the heights and in winter,
  marsh with pools and reeds), its colour is the places' characters blended by nearness, and it is shaded by its relief.
  Worlds that say little (region_s1: every road farmland, every height 1) get a landscape from little: mostly the names.

## 10. Audit of the first renderer (before this model), fixed in the rebuild

- Reaped share was read from `crop.left` (yield): it is `1 - area_left/area`. A field was drawn wholly sown: the sown share is
  `area/size`. Stages were invented: the engine's are dug, new sown, green, high, ripe, rotting, blighted, killed, reaped,
  stubble.
- Woods thinned against day 0: they are S/K of `res.wood`, felled below 0.3, scrub below 0.4.
- Sheep, goats and pigs were drawn: the engine has cattle only, as cows, oxen, bulls and calves.
- Buildings were sized from `size` (beds): they are drawn from rooms (spec), with today's buildings' rooms derived.
- Lots were for built ground only: scrub has 4 a unit.
- People were placed by the act's `site` or the house: the engine's rule is `spot_of`; sleeping from the night log.
- Weather was not drawn; snow only by season: it is `environment.weather` and `snow_lying`.
- Roads left from the first parcel and toward a direction from layout.py: they leave from their ends' parcels on their sides,
  and hidden ends are faint by `worn`.

## 11. Next: a person's way through the day

What the engine has: `today.worked[name]` (sites in act order) and `layout.passed` (the shortest way from where one slept to
each worked parcel, ties by a keyed draw: a star out and back, not a chain from act to act), which is what one senses in
passing (presence 0.3) along with what is next door (0.1). Not stored; recomputed by the evening. When the visuals draw a
person's way, they draw exactly that (from the engine, in Python), and if the engine moves to a chain of acts, the same.
