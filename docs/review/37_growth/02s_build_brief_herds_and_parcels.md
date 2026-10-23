# 02s: build brief for 37.4: the parcel graph, herds, fences, hidden ways, and the Q-20 changes (Package C)

Session 37.2, 24 Oct 2026. Zach: pass the next spec to 37.4 to build; 37.2 does not build. Same shape as 02r. Decisions D2-114 to
D2-132 (DECISIONS.md); numbers in the spec are marked proposed or calibrate.

## 1. Spec to build against

| Spec file | Holds | Decisions |
|---|---|---|
| spec/world/parcel_graph.md (new; 37.4's area, written at Zach's request) | neighbours from the land, a side and a height per parcel; presence along the way; `attend {to: the village}`; the arrival overview | D2-114 to D2-116 |
| spec/economy/livestock.md (37.2's; rewritten) | staying put; wandering on the node; lost on a road; driving and accompanying; capacity and splitting; fences round a parcel and gates | D2-117, D2-123 to D2-125, D2-127, D2-128, D2-130 to D2-132 (also D4-41, D4-42, D4-44, D4-45, now written there) |
| spec/world/roads.md (edited) | default terrain on every road; where crossing parties meet varies; meeting offers through agreements; searching; road ends on a parcel's side | D2-120 to D2-122, D2-125 |
| spec/information/noticing.md (edited) | presence: passing through 0.3, next door 0.1 | D2-115 |
| spec/agents/modifiers.md (edited) | `searching`; dibbling known to at least one person in the world | D2-125, D2-129 |
| spec/economy/production.md | fences as field works (pointer) | D2-130 |

Hidden ways are already specified (world/roads.md "Where a road leaves a node", D2-90, D2-92, D2-98); they were waiting only for
parcels to have sides.

## 2. Order

1. **The Q-20 changes** (small, independent): every road gets a terrain by default (D2-122; the bare switch stays for comparison
   arms); the meeting stretch drawn between the two, x3 at a landmark (D2-121); **meeting offers through `agreements.py`** (D2-120:
   roads.py has its own goods-for-goods offer table; route `offer` and `accept` in a meeting through the same code as at a node,
   with the road as the place, so promises and payments over time follow with no special case); dibbling seeded in one person in
   the world (D2-129).
2. **The parcel graph:** side and height per parcel (defaults centre and 1 where a world sets none; generation sets them from the
   land); shortest paths from where each slept to what it works; presence along the way and next door in the noticing rule; `attend
   {to: the village}`; the arrival overview (3 to 5 lines).
3. **Fences and gates:** a parcel fenced (wood or stone) as a field work; the herd's daily crossing odds; decay unmended; gates
   automatic; `work {what: open the gate}` as an act with no units, seen by those present, the open gate a sign (own 0.6), shut by
   the holding household when noticed.
4. **Herds wandering on the node:** steps a day by hunger and draw, the most attractive neighbour, fence odds, trampling 1% a head a
   day, noticed by the rule, `drive` back; 0.1 a step onto a road from a road-end parcel.
5. **Herds on roads:** a herd on a stretch drifting a stretch a day; losses by head (0.15, winter 0.3) and the group gone (0.15);
   home or a stray at the far node by drifting off an end; finds by the rule (a fuse call: drive a stretch, accompany, leave);
   `travel {searching}` x5.
6. **Capacity and splitting** everywhere a herd is held (herded, driven, accompanied, unherded): the split chance and the share
   (a quarter x 2^z, z Laplace with a standard deviation of 1, redrawn above half, at least 1 head); a further call while driving
   only for a split of a quarter or 3 head or more that a drover notices.
7. **Hidden ways:** road ends on a side and parcels; hidden while the parcel's sight is 0.5 or less; own conspicuousness 0.03 plus
   0.05 a party passing; regrowth in about a season in forest or scrub; exposed (0.8) when the parcel is opened; the finder learns
   an unexplored way (D4-47).

## 3. Tests

| Test |
|---|
| a road with no terrain in its world file gets one, and two parties crossing on it can meet; a road made bare holds nothing (the comparison switch) |
| crossing parties meet on either stretch, three times as often on the one with the ford |
| a promise made in a meeting ("1 timber now for 2 coin by day 6") is an open agreement settled at a node later, or in arrears |
| exactly one person in a seeded world knows dibbling; teaching spreads it |
| a farmer working Long Acre from the Green passes through the parcels between and can notice a pack on one (0.3), and a herd next door (0.1) |
| `attend {to: the village}` lists neighbours, sides and road ends; an arriving traveller gets 3 to 5 overview lines |
| a fenced pasture holds its herd at 0.3 (wood) and 0.05 (stone) a day; an opened gate lets it out; opening it is seen by those present |
| a hungry unherded herd crosses several parcels in a day and tramples a field (1% a head); a fed one on good pasture mostly stays |
| a herd on a road drifts; 10 head lose about 1.5 a day; a searcher on its stretch finds it far more often than a passer-by |
| 20 head driven by one drover split about 0.1 a day; by two drovers almost never; shares drawn peak near a quarter |
| a hidden way in a wood is found by hunters over weeks, not days; felling the wood exposes it |

## 4. Run plan

Two runs, few and reasonable as before.

- **Herds and fences, one node:** the hamlet or Barleyfield with two herds, one fenced pasture (wood) and one open common, ripe crops
  next to the common, and a road leaving from the common's side. Read: strays into crops, who noticed, who drove them back, whether
  anyone fenced or opened a gate, any herd lost onto the road and found.
- **Roads and herds:** the two-valleys roads world with a default terrain everywhere, so meetings happen without scripting; a herd
  that can wander onto the road. Read: meetings and promises made in them, herds found on the road, searches.

## 5. Not in this package

Fire (OPEN L-21), raiders as outside agents (L-22), water and the land's hidden state (L-23), fences on borders, hedges, folds and
wolves (L-24, L-2); everything else in OPEN.md "Flagged for later".
