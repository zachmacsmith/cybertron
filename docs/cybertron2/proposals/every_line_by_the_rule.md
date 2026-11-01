# Every perceived line by the one noticing rule

**Status:** retrospective, accepted: D4-75 (2 Nov)
**Owner:** 37.4

## Summary

Every line an agent perceives about the world outside itself takes its chance from the one noticing rule (D4-53): a sign's base
chance x its own conspicuousness x the visibility for its sense x presence x attention x the eye. A sign row sets how plain the sign
is, its sense, its conditions and its scope; never a final chance. Sound and smell carry by steps in the parcel graph; a sign in the
night is read from where one sleeps. What one knows of one's own body, carriage and units is shown directly, and what was said lives
in the conversation: neither is a sense.

## The proposal

The rule and its factors are in spec information/noticing.md ("Every perceived line by the one rule"). In short:

- **Sound and smell carry:** presence for them is at least the carry for the number of steps from where one was that day to the
  sign's parcel (sound 0.5, 0.45, 0.2, 0.1, 0.05; smell 0.5, 0.3, 0.12, 0.05, 0), times the sense's visibility (cover, weather, the
  night, masking). Touch reaches only where one is. The eye reads sight only. A sound of own 1 or more is not masked.
- **Reach** is shorthand for the rule's inputs: near (the spot, attention x2: a close look), around (the spot and next door).
- **Every path goes through it:** signs at a spot; things (their close looks and the signs that carry, each with its own); what
  concerns one (in full only when it happened to one or in one's house); dawn lines; the attended subject (sought out: presence at
  least 0.5, attention x5); the place's ambient lines; what one worked on (attention x3); glimpses of others (a person at work, own
  2); feeling watched; road notices (by the terrain's visibility for each sense); who sees a theft; who is woken by a break-in.
- **The cap** comes after the base chance, so attention can lift a weak sign.

Before and after on typical cases (clear day, ordinary eye):

| Path, sign | Typical case | Before | After | What now moves it |
|---|---|---|---|---|
| slaughter: the kill (sight) | worked on the parcel | 1.0 | 1.0 | fog 0.3, night 0.1, crossing 0.6 |
| slaughter: the bellow (sound) | next door; two steps; three | 0.95; 0.4; 0.4 | 0.9; 0.4; 0.2 | a gale 0.5; night x1.2 |
| slaughter: the smell of guts | on the parcel; next door | 0.9; 0 | 0.9; 0.54 | distance |
| slaughter: crows | worked there; elsewhere | 0.27; 0.03 | 0.45; 0.05 | fog, night, distance |
| a thing's close look (whose body it is) | worked on its parcel | 1.0 | 0.9 | fog, crossing, attention, hiding |
| crows over a body some days dead | elsewhere at the place; on its parcel | 0.25; 0.25 | 0.15; 1.0 | fog, distance |
| the smell of a body rotting, across the place | two steps; on its parcel | 0.3; 0.3 | 0.18; 0.75 | steps |
| a body in one's own house | one who lives there | 1.0 | 1.0 | |
| a frost (the sky) | anyone at the place | 0.85 | 0.85 | |
| concerned: a theft from one's house | one who lives there | 1.0 | 1.0 | |
| concerned: work done against one's claim | at home next door to it | 1.0 | 0.04 | where one was |
| dawn: a fire in the night (0.95) | anyone at the place | 1.0 | 0.95 | fog 0.29 |
| dawn: a sign from the spec (0.3, the sky) | anyone | 0.09 to 0.39 | 0.3 | |
| attending a person: "looks drawn and hungry" (0.35) | not of one's household; of it | listed, 1.0 | 0.61 (on built ground) to 0.88; 1.0 | where they are, weather |
| attending the place: "cattle lowing on the Common" (0.35) | anyone at the place | 4 of all at random | 0.88 | distance does not lower it (sought out); a gale does |
| what one worked on: "the barley stands ripe" (0.35) | its worker | in the top 4, 1.0 | 0.53 | fog, crop height |
| glimpse: where another spent the day | not of one's household, same parcel; next door; elsewhere | up to 3, 1.0 | 1.0; 0.2; 0.1 | where each was |
| glimpse: one's household | anyone | 1.0 | 1.0 | |
| road: a cart's creak far off (0.3) | on the stretch, in woodland | 0.3 | 0.21 | terrain, weather |
| a theft seen | one of the house at home; one attending it; another on the same ground | 0.45; 0.8; 0.05 | 0.4; 0.7; 0.14 | weather, where one was |
| woken by a break-in, a neighbour | asleep on the same ground; next door | 0.18 | 0.18; 0.16 | the night's sound, steps |

## Why

Zach (2 Nov), on D4-71's rows that set a chance by reach: "are these senses being given direct chances? Are they not using the
normal sense system, with scope, place etc.?"; then "Everything should be going through the core shared sense system"; and "they
should still end up with similar or comparable probabilities, but naturally not hand made. This should def be in the sense
instructions to always build bundles like this." D4-71's reach rows ignored fog, the dark, how far one was and attention; several
other paths (close looks, concerned and dawn lines, attention, ambient lines, what one worked on, glimpses, road rows, theft and
break-in detection) set or listed chances outside the rule.

## Alternatives considered

- **Keep reach as a fixed chance, scaled by hand for weather:** two systems where D4-53 says one; every new bundle re-implements
  visibility.
- **Make sound and smell node-wide with a fixed fall-off:** loses the place's shape; the parcel graph already says what is near.
- **Leave attention as a listing:** the attended subject would still bypass weather and distance.

## Open questions

1. The carry and attention values are calibrated against the old typical chances; the bot and live runs should be read for whether
   far-off sounds now crowd the notice.
2. Signs about the sky are not lowered by the weather itself; whether fog should hide other sky lines.
3. Smell has no visibility (D2-101); rain and wind on smell are not modelled.

## Affects

things.py (steps, night_spot, presence, spot_chance, chance), perceive.py (chance_of, happened_to; evening and dawn), signs.py (rows'
own and reach; roll's rule), roads.py (notices), settle.py (thefts seen), fuse.py (raid detection), environment.py (open_air),
data.NOTICING; spec information/noticing.md, perception.md, signs.md.

## History

- 2 Nov 2026: built at Zach's request while the 18 bundles of review 38.43 were being built (D4-74); written down after
  (retrospective). Replaces in part D4-71's fixed chances by reach.

## Sources

review 38.43; proposals/one_noticing_rule.md (D4-53), slaughter_signs.md, sign_bundles.md; tests/test_cybertron2_one_rule.py, test_cybertron2_slaughter_signs.py.
