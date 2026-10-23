# Proposal: what travellers see on the way

> **Decided parts are in the spec:** spec/information/noticing.md (23 Oct). This file keeps the reasoning, the history and what is still open.

**Status:** accepted: D2-88, D2-89, D2-97 (23 Oct). Design only. **Owner:** 37.2 (author); perception, roads and memory are 37.4's (place.md,
seeing.md, senses.md, D4-48), so this goes to them. **Affects:** spec/information/perception.md, memory.md, signs.md;
spec/world/edges.md; environment/ (signs of slow change).

## Summary

A traveller in transit makes no decisions (D4-10), but it is not blind. Each day on the road it **notices things on that road**,
drawn as at a node (D4-48: each sign rolled for each observer, with its sense, chance and conditions), and **remembers them on
arrival** ("On the way: ..."). What a road holds: other travellers seen at a distance, herds (lost or wild), a body, a camp, and
**traces left by earlier passers** (ashes, cart ruts, tracks, a dropped load), the land and weather along it, and, more rarely,
**signs of slow change** a long journey shows better than a day at home. Longer edges give more. It costs no call in transit; it
adds a few lines to the arrival prompt.

## The proposal

### 1. What a road holds

A road is a place with its own log (place.md: `Road(edge, from, day)`). Things on it, each with a bundle of signs (D4-48):

| On the road | Signs (examples) | Lasts as a trace |
|---|---|---|
| other travellers going the other way, not met (road_encounters.md) | "a party of three with a laden ox, far off on the plain" | footprints, a day or two |
| travellers ahead or behind | "smoke from a camp ahead"; "voices behind you at dusk" | a camp's ashes, several days |
| a lost or wild herd | "cattle bellowing in the wood"; dung on the path | tracks, a few days |
| a body (D2-4: a death on the road is never announced) | "a man lying by the ford, dead some days"; crows circling | until found or eaten |
| a camp (D2-68) | "a lean-to by the stream, recently used" | about ten days |
| goods dropped or left (objects_in_world.md) | "a broken cart wheel in the ditch" | until taken |
| the land and weather along it | "the river is high at the ford"; "the pass is snowing" | |
| slow change (§3) | "more of the wood is burnt than you remember" | |

### 2. How a traveller notices

- **Each day on the road, one observation** (as seeing.md's daily notice): every high-salience thing in range, plus a few lower
  ones drawn by salience and the traveller's knack (a hunter reads tracks, a herder dung, a soldier a camp's size).
- **An aim raises what it is looking for:** a searcher (road_encounters.md) or someone watching for raiders notices those signs
  more.
- **Terrain sets range:** far on open plains, short in woodland (environment.md §12).
- **On arrival** the day's notices become memories ("On the way: smoke from a camp at the forest's edge; fresh cart ruts going
  east; a dead ox by the ford"), in the arrival prompt's budget; a long journey's are summarised.
- **What it is for:** news travels with travellers, so what they saw on the road (a body, a raiders' camp, a lost herd, the state of
  the ford) is information they carry and can tell or sell (D4-9, D2-29), and a body on the road is how a household's missing
  member is eventually found (D2-4).

### 3. Slow change seen from the road

A day at home rarely shows an era (environment.md §7). A journey crosses more land, so it shows more: **a rarer class of signs
about the land's longer state**, drawn on the road with low chance and more on long edges ("the fen is lower than you have ever
seen it"; "farms along the valley stand empty"; "new ruts: more carts use this road than before"). The sign states what is there;
"than before" comes from the traveller's own memory of the road, never from the engine (D2-4).

## Why

- It makes travel informative without calls in transit, so merchants and travellers carry news as they did.
- It closes D2-4's loop: deaths on the road are found by those who pass.
- It uses the road as a place (place.md) and signs as bundles (D4-48) with no new mechanism.

## Open questions (for Zach, and 37.4)

1. ~~Daily notices~~ decided: D2-97.
2. ~~Traces~~ decided: persist and fade (D2-88).
3. ~~Slow change~~ decided: later, flagged; data in the shared sign registry (D2-89).

## History

- 23 Oct: Zach: even when nothing happens, travellers should arrive with what they saw on the trip, more on multi-day edges:
  herds, other people, a body, signs left by others; longer journeys could give rarer signs of structural shifts. Written.
- 23 Oct: Zach: what lies on the road should be a case of objects left somewhere. The road's contents and how they are noticed
  now follow [things_in_places.md](things_in_places.md) (roads in one stretch per day; one noticing rule).

- 23 Oct: Zach decided D2-88 (traces that fade) and D2-89 (slow change later, as data in the shared registry). Asked what Q1
  means; explained.

- 23 Oct: Zach decided D2-97 (daily notices on the road, remembered on arrival).

## Sources

[place.md](place.md), [seeing.md](seeing.md), [senses.md](senses.md), [road_encounters.md](road_encounters.md),
[objects_in_world.md](objects_in_world.md), [environment.md](environment.md) §7, §12; D2-4, D2-29, D2-68, D4-9, D4-10, D4-48.
