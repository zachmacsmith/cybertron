# Signs

## Summary

Hidden change shows itself, if at all, as one in-world sentence: a sign. A sign has an audience, a lag and a reliability, and is
kept apart from the change it signals.

## Decided

- D4-6: signs: at most one in-world sentence, with an audience, a lag and a reliability, kept separate from the effects.
- D4-71: a slaughter shows itself as a bundle of signs on its parcel, that day and the next; signs read at a spot may carry a reach.

## Mechanics

- **A sign** is a sentence about the world ("a white frost on the grass at dawn, weeks before its time") shown to those who could
  notice it: its audience (who is at the place, by sense and attention), after its lag, and true only with its reliability (D4-6).
- **Signs are local**: a sign happens at a place (D4-35) and travels further only as people carry it.
- The scheduler draws signs alongside the changes they signal (environment/scheduler.md).
- **Reach at a spot** (D4-71): a sign read at a spot is noticed by the noticing rule (noticing.md) unless it says otherwise: **near**,
  its chance for one who was at the parcel that day (worked there, was about it, attended to it); **around**, the same also for one who
  crossed it or worked next to it; **node**, its chance for anyone at the place. A sign may be kept from those who did the act it shows,
  or shown only to them.
- **A slaughter** (D4-71) records on its parcel the day's kills (the beast, its herd, who killed it) and shows for that day and the
  next (chances `calibrate`):

  | When | Sign | Sense | Chance | Reach |
  |---|---|---|---|---|
  | the day | who killed which beast there; it went down kicking and bled out | sight | 1.0 | near, not the doer |
  | the day | the beast butchered where it fell: the hide off, the guts heaped, the meat cut | sight | 0.8 | near, not the doer |
  | the day | the smell of blood and opened guts | smell | 0.9 | near |
  | the day | the bellow, the fall, then quiet | sound | 0.95 x the parcel's sound | around, not the doer |
  | the day | a bellow cut short | sound | 0.4 x the parcel's sound | node, not the doer |
  | the day | the beast going down, its blood over one's hands | touch | 1.0 | near, the doer only |
  | the day, a herd still there | the herd uneasy at the smell of blood | sight | 0.4 (own 0.95; a herder's knack) | the rule |
  | the day, a dog kept at the place | the dogs wild at the smell of blood | sound | 0.5 | node |
  | the day and the next, not in fog | crows and kites over the leavings | sight | 0.6 (own 0.9) | the rule |
  | the day and the next, snow lying | blood in the snow | sight | 0.9 | near |
  | the next day, no snow | blood soaked into the ground (flies, if not frost) | sight | 0.8 | near |
  | the next day, not frost | the smell of old blood and offal | smell | 0.6 | near |

  One who slaughtered that day is seen with blood to the elbows (sight 0.6) and smelt (0.3), as a sign of the person.

## Signs of people (D4-72)

A sign of a person shows their body (hunger, injury, age, pregnancy, what they carry or lead) and what they did; never an act or a
feeling they did not choose. Signs about those who live in a building apply only to buildings with beds. How to write signs:
docs/cybertron2/guides/senses.md.

## Data

Per sign: day, place, sense, text, salience, what it bears on.

## Sources

devlog 37.4 #6; 38.04 §3.

*Current as of 2 Nov 2026: D4-6, D4-35, D4-71, D4-72.*
