# Proposal: visibility (what a place and the day let the senses reach)

**Status:** accepted: D2-99 to D2-102 (23 Oct); numbers to calibrate; smell later. Design only. **Owner:** 37.2 (author; the environment, D2-75, sets the land and the weather);
perception and the senses are 37.4's (perception.md, senses.md, seeing.md, D4-48, D4-50), which apply it. **Affects:**
spec/information/perception.md, signs.md; spec/environment/scheduler.md (weather, light); spec/world/places.md, edges.md;
things_in_places.md, hidden_ways.md, road_layout.md, road_encounters.md, fuse_events.md (detection).

## Summary

Zach (23 Oct): felling the woods to expose a hidden way should be one case of something broader: **visibility**, a property of a
place that bears on the senses, set by the kind of land, changed by its state (trees felled, crops grown, snow) and by the day
(light, weather), and changing how things are seen. Today it appears piecemeal: cover in things_in_places.md's table, terrain
setting range in journeys.md, fog halving meetings in road_encounters.md, the edge's terrain carrying signs in D2-74. Proposed:
one value per place and sense, used by every sign.

## The proposal

### 1. What the observer brings and what the place lets through

A sign's chance of being noticed (D4-48) is already the observer's side (presence, attention, the eye for the land: D2-85,
D2-91). Visibility is the other side: **how much the place and the day let through**, for each sense.

**chance a sign is noticed = the sign's own chance x the observer's factors (D2-85) x the place's visibility for that sense**

### 2. Sight by the land (base, as data on each cover kind)

| Cover | Sight | Notes |
|---|---|---|
| open field, pasture, open plain | 1.0 | |
| built ground | 0.7 | walls and corners |
| marsh | 0.6 | reeds |
| scrub, hill country | 0.5 | |
| woodland | 0.35 | |
| dense forest, a gorge | 0.2 | |
| inside a building | its room only | |

### 3. Changed by the state of the land (the environment's slow state)

| Change | Effect on sight |
|---|---|
| a wood felled or burned | rises to scrub (0.5), then open (1.0) when cleared |
| land left to regrow | falls back over seasons (field to scrub to wood) |
| a grain crop standing high (late summer) | a field falls to about 0.5 until reaped |
| snow lying | things on the ground hidden (x0.5), tracks in it very plain (x3) |
| a building raised, a wall built | built ground; behind a wall nothing is seen |

### 4. Changed by the weather, and by night (D2-99, D2-100)

Agents act once a day, and the day's notices are taken **by day**, so light does not enter them. It matters only for what happens
at night: fuse events (a raid, a fire), the watch, and working late.

| Condition | Sight | Sound |
|---|---|---|
| clear | x1 | x1 |
| fog | x0.3 | x1 |
| heavy rain | x0.6 | x0.5 |
| falling snow | x0.5 | x0.7 |
| strong wind (the region's wind, environment_state.md §10) | x1 | x0.5 |
| **at night only** | x0.1 (x0.25 under a full moon; near a fire, its light) | x1.2 (night is quiet) |

**Sound** has its own base by land (forest dampens, x0.7; open land carries, x1). **Loud things mask quieter ones (D2-100):** each
place has an ambient loudness from what is there (a waterfall or a weir, a mill or a smithy at work, a crowd at market, a fight, a
horn, wind and rain), and a quieter sound there is heard less (proposed: x0.3 near something very loud, x0.6 near something loud).
A very loud sound also carries further: a horn or a fight is heard across the node, a horn at the far end of an edge if the edge
carries sound (D2-74).

### 4a. How the three senses differ

| | Sight | Sound | Smell (later, D2-101) |
|---|---|---|---|
| blocked by | cover, walls, dark, fog, rain, snow | little: dampened by forest and walls | nothing much |
| masked by | | louder sounds, wind, rain | (stronger smells, later) |
| at night | almost nothing | better | the same |
| how fast | at once | at once | builds up over days (a body from the second or third day) and lingers after the source is gone |
| tells | detail: who, how many, what they carry | that something is happening and roughly where; little detail | that a kind of thing is there (rot, smoke, beasts, bread), no detail |
| reach | the parcel and open neighbours | by loudness: the parcel to the whole node | the spot and the parcel; very strong ones the next parcel |

### 5. Smell, later and simple (D2-101)

Smell signs carry only their own salience and reach, with no visibility multipliers and no wind direction for now: the stench of a
corpse (very salient after a few days, within the parcel and the next), a midden or latrine, a tannery, livestock in a byre, smoke,
bread baking, grain rotting in a store (a warning before the loss shows). Wind direction would come with fire spreading by the wind
(D2-72), if that is ever wanted; then smell could follow it too.

### 5. What it changes

- **Things at a spot** (things_in_places.md): conspicuousness splits into the thing's own (its size, kind, and how hidden) x the
  spot's sight; the table there becomes the product.
- **Hidden ways** (hidden_ways.md, D2-92): a way is hidden by its parcel's sight; felling exposes it because felling raises sight.
- **Roads** (road_layout.md, road_encounters.md): meeting odds and who sees first follow each stretch's sight and the weather; an
  overlook is a stretch of long sight, a narrows one of short.
- **Fuse events** (D2-81): a raid by night is detected by sound more than sight; rain covers the noise; a watcher's fire lights its
  surroundings.
- **Across edges** (D2-74): smoke and beacons carry by the edge's sight and the weather.
- **Defence as a choice:** clearing the woods along a road or round a village exposes approaches and hidden ways (England's
  Statute of Winchester, 1285, ordered brush cleared 200 feet each side of highways against robbers); keeping them grown hides one's
  own caches and escape.

### 6. Data

Per cover kind: sight and sound bases. Per place: its cover and state (from layout.md and the environment's slow state). Per day:
light and weather (scheduler.md). Per sign: its sense (D4-48). Nothing per thing beyond what it already has.

## Why

- One factor instead of several local rules; every system that shows something gets the land and the weather for free.
- It makes the land's state matter to what people see, so changing the land (felling, building, clearing) changes information,
  surprise and safety.

## Alternatives considered

- **Cover baked into each table** (as things_in_places.md §1 now): works, but each system tunes it separately, and weather and light
  would have to be added to each.
- **Range in distance** (metres or parcels): more precise, but the world has no coordinates inside a parcel; a multiplier per place
  is enough.

### 7. Visibility is read from the land's hidden state, not stored

Visibility fits the hidden parameters of the land (environment_state.md), but as a **reading of them, computed each day**, not a
variable of its own: sight from the parcel's cover and vegetation (felling and regrowth move it), a standing crop, snow lying, and
**smoke** (a fire, a burning, charcoal burners, a smithy: a short-lived state that lowers sight nearby and gives a smell); sound from
the ambient loudness of what is there and the weather. Computing it rather than storing it means it can never drift from the land
it describes.

## Open questions (for Zach, and 37.4)

1. ~~Visibility per place and sense~~ decided: D2-99. 2. ~~Sight and sound now, smell later~~ decided: D2-99 to D2-101.
3. ~~The numbers~~ starting values (D2-99; calibrate). 4. ~~Split conspicuousness~~ decided: D2-102.
5. Visibility computed each day from the land's state (smoke included) rather than stored (§7)?
6. The masking factors (x0.3, x0.6) and what counts as very loud.

## History

- 23 Oct: Zach: felling the woods should be one case of something broader; should visibility be a thing that affects the senses,
  depends on the kind of land, can be changed by conditions (trees felled) and weather, and changes how things are seen? Written.

- 23 Oct: Zach decided D2-99 (visibility for sight and sound; rain and snow; and asked how anything is noticed at dusk or night when
  agents act once a day: it is not, so light only matters for night events, the watch and working late), D2-100 (very loud things
  mask others), D2-101 (smell later, simple: own salience, no wind for now; corpses, animals), D2-102 (split conspicuousness).
  Asked whether visibility fits the land's hidden parameters, with smoke from fires: §7.

## Sources

[things_in_places.md](things_in_places.md), [hidden_ways.md](hidden_ways.md), [road_layout.md](road_layout.md),
[road_encounters.md](road_encounters.md), [journeys.md](journeys.md), [senses.md](senses.md), [seeing.md](seeing.md),
[layout.md](layout.md), [environment_state.md](environment_state.md); D2-74, D2-81, D2-85, D2-91, D2-92, D4-48, D4-50.
