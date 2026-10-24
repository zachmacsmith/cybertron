# Review 38.25: Package C built and run (37.2's brief 02s): the parcel graph, herds, fences, hidden ways

Session 37.4, 24 Oct 2026. Zach: "Then go and build the new package"; later "After building do a run to test it". The brief is
`docs/review/37_growth/02s_build_brief_herds_and_parcels.md`, decisions D2-114 to D2-132; D4-52 (carcasses) was decided during the
work. 106 cybertron2 tests pass (`tests/test_cybertron2_package_c.py` holds the brief's §3 list and more).

## 1. What was built, and how it extends

| Part | Module | Extends by |
|---|---|---|
| **Q-20 changes:** every road a farm track unless its world says (D2-122), `bare: true` the comparison switch; crossing parties meet on a stretch drawn between them, x3 at a landmark (D2-121); offers and accepts in a meeting through agreements.py with the road as the place, so promises stay open and settle at a node later (D2-120); dibbling seeded in one farmer per world (D2-129) | `roads.py`, `here.py` (a place and a company on the road), `agreements.py`, `knowledge.seed_world` | `KNOWN_SOMEWHERE` lists techniques someone must know |
| **The parcel graph:** side and height per parcel; shortest ways with keyed ties; presence 0.3 on the way from where one slept to each parcel worked, 0.1 next door (D2-115); `attend {to: the village}` gives the layout; 3 to 5 lines on arriving (D2-116); road ends on a side and parcels | `engine/layout.py` | `LAYOUT` (height words, striking fittings, overview length) |
| **Fences and gates:** `fence` (wattle, anyone) and `wall` (a mason's crew) as field works on a parcel, materials with the work; levels whole, gappy, down; a wood fence loses a level a season unmended, a quarter of the build mends it; `work {what: open the gate}` (0 units, seen) and `shut the gate`; an open gate is no fence; its holders shut it when they notice it (D2-130, D2-132) | `farm.py` (acts), `herds.py` (upkeep), `perceive.py` (shutting) | `FENCES` per kind |
| **Herds wandering:** an unherded herd outside a shut fence steps toward what feeds it (grazing, a crop at the trampling rate, a ripe crop's pull, water), 0 to 1 steps fed on good grass, up to 8 hungry or drawn; fences crossed at their odds; tramples 1% of a crop a head; cows in milk home at dusk; a step from a road-end parcel takes the road at 0.1 (D2-117, D2-123) | `engine/herds.py` | `HERDS` |
| **Herds on roads:** drift a stretch a day, each head dies 0.15 (winter 0.3), the group gone 0.15; off the end it came from home, off the far end a stray there; found by the noticing rule (x5 for `travel {searching: ...}`); the find call: drive on, drive back, accompany (to the destination or back), leave; the taker holds them; a finder knows its own beasts and its neighbours' (D2-124, D2-125, D2-127) | `herds.py`, `roads.py` (fuse kinds `herd`, `split`) | a fuse kind registers source, detector and choices |
| **Capacity and splitting:** 10 a drover, 30 a herder, 6 unherded; split 0.01 under, 0.1 x (head/cap - 1) over, at most 0.6; the share a quarter x 2^z, z Laplace; a call while driving for a big split a drover sees; a split group rejoins when on one parcel next day (D2-128, D2-131) | `herds.py`, primitive `split_herd` | |
| **Hidden ways:** road ends hidden where the parcel's sight is 0.5 or less; out of "Roads from here" until found by the rule (0.03, +0.05 a party passing, regrowing in about a season); felling a wood opens the land (sight 0.8) and shows it (0.8); learned by coming in by it or being told (D2-90, D2-92, D2-98) | `layout.py`, `perceive.py`, `run._mentions` | signs.py `WAY` |
| **Signs:** herds out, a trampled field, an empty home pasture (holders only), fences and gates, a dead beast; all but the field's by the noticing rule | `signs.py` ASTRAY, EMPTY, FENCE, CARCASS, CROP rows | rows, not code (D4-24, D4-48) |
| **Carcasses (D4-52):** a beast that dies leaves one where it fell, fit to eat about a day; on a road none, hidden or by the road | `things.leave_carcass`, `night.py` | `THINGS` carcass rows |
| World files: `holder:` on a parcel or herd, `fence:` on a parcel, herds lost on a road (`road`, `stretch`) | `world.py` | |

## 2. Runs

| Run | World | Agents, days | Cost | What it showed |
|---|---|---|---|---|
| c1 | barleyfield_c: two herds (one behind wattle), ripe crops, a road off the Common, a hidden trail in the wood | 18, 10 | $5.21 | no errors; the Reeds herded their cattle some days, the Barrows began fencing East Field "until it is reaped"; **no herd strayed**: found the cause (below) |
| c2 | two_valleys_c: a farm-track road, Wetham's road end at its cattle's meadow, the Cragg cattle loose on the road | 26, 8 | $7.02 | no errors; three journeys, none at once, so no meeting; Ancel passed the Cragg cattle between nights (finds need one stretch); the strays died on the road by day 5; arrival overview worked |
| c3 | barleyfield_gate: Randal (a Hale, an old quarrel with Bennet) opens the Barrows' gate on day 2, scripted | 18, 5 | $1.98 | Bennet saw it, shut it next morning and told Randal "Leave our gates alone" ("I'll leave your gates alone"); the cattle, fed on good grass with the barley next door unripe, stayed in |
| c4 | barleyfield_c again (the dusk fix), 6 days | 18, 6 | $1.96 | both herds walked into the Reeds' ripe barley at night and home at dusk (about 20 of 210 trampled), the Barrows' through their fence; **nobody noticed**: found the cause (below) |
| c5 | two_valleys_search: Osric sets off searching for the Cragg cattle, Simkin the other way, scripted | 26, 4 | $3.09 | Osric found the herd the first night, took it along "to give them back to their owners" (his own family's: below); a three-party meeting (Ancel, Osric, Simkin): three offers through agreements on the road, one with a promise ("5 rye now, 1 rye by day 6"), none taken; Simkin turned back to look for "the Wetham cattle" on Osric's word; at Wetham Simkin bought Ancel's copper tool for 8 grain |
| c6 | barleyfield_c, 5 days (trampled-field signs) | 18, 5 | see §5 | see §5 |

## 3. Faults found by the runs and fixed

| Fault | Fix |
|---|---|
| "a stray herd walks home after a day" (an old dawn rule) undid the wandering | removed: D2-117 replaces it |
| cows in milk were held at home all day (a standing pull toward home), so c1's Reed cattle never left the Common | they roam by day and walk home at dusk (a shut fence round home at its odds) |
| a ripe crop drew a starving herd to stay in a trampled field | its pull scales with what is left |
| every parcel listed "open the gate", "fence", "wall"; fences unseen in a parcel's line | gate acts only where there is a gate; the fence and its state in the line; no fencing on built ground |
| the old "only a broken hedge stands between them" line fired for a herd behind a sound fence (c1's Barrows fenced East Field because of it) | it follows the fence: open ground, gaps, or nothing |
| a herd on the road did not say whose it was (c5: Osric took his own family's cattle to Wetham to return them) | its own household's, a neighbour's from its own village, or strangers' |
| herds trample at night and are home by dusk, so a trampled field showed nothing (c4) | the field shows hoof-marks and flattened crop for days |
| a counter-offer in a meeting's last exchange could never be taken (c5, Ancel) | the last exchange says so |
| a fence seeded in a world file decayed on the first night (the season turned) | it counts as mended this season |

## 4. What the runs could not show, and why

- **The open gate letting the herd out** (c3): the cattle were fed and had nothing to go to; the mechanism is the test's (escapes 0.3 a
  day through wattle, over 0.95 with the gate open). The social side worked.
- **Meetings without scripting** (c2): three journeys in eight days, none overlapping. Meetings need traffic; the next region (D2-137)
  has more.
- **A find by a passer-by** (c2): the herd and the traveller crossed between nights. c5's searcher found it on the first night.
- **Hidden ways** live: nobody hunted in Barley Wood long enough; the test covers it (found by hunters after weeks, at once once felled).
- **Splitting with a call while driving**: not live; dry runs and tests only.
- c5's searcher did not know he was searching: the departure was scripted and nothing told the Craggs their cattle were lost. The
  world file should tell the holders (`known_by` for a lost herd), next time.

## 5. c6

(Filled in when the run ends.)

## 6. Choices the spec left open

OPEN Q-21 lists them (16 items, for Zach and, for livestock, 37.2), with D4-52's numbers in world/things_in_places.md as calibrate.

*A run report; the decisions it bears on are D2-114 to D2-132, D4-52.*
