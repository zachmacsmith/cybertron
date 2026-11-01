# A slaughter shows itself

**Status:** retrospective, accepted: D4-71 (2 Nov)
**Owner:** 37.4

## Summary

A beast slaughtered on a parcel shows itself as a bundle of signs (D4-48), the day of the kill and the day after: the kill seen and
smelt by those on the parcel, the bellow heard by those beside it and, less often, across the place, the doer's own felt line, the herd
uneasy, the dogs wild at the blood, crows over the leavings, blood on the ground or in the snow the next day; and the one who did it is
seen bloodied. Signs read at a spot may now carry a reach, as thing signs do.

## The proposal

- **The record:** a slaughter records the day's kills on its parcel: for each, the beast (cow, ox, bull, calf), its herd and who
  killed it. A new day's slaughter starts a new record.
- **The bundle** (signs.py SLAUGHTER), read by the noticing rule for the day of the kill and the next:
  - today, for those at the parcel (not the doer): who killed which beast, and that it went down kicking and bled out (sight, 1.0);
    the butchering where it fell (sight, 0.8);
  - today, for those at the parcel, the doer too: the smell of blood and opened guts (smell, 0.9);
  - today, for those at, crossing or next to the parcel (not the doer): the bellow, the fall, the quiet (sound, 0.95 x the parcel's
    sound that day); for anyone at the place: a bellow cut short (sound, 0.4 x the same);
  - today, for the doer only: the beast's weight going down and its blood over one's hands (touch, 1.0);
  - today, by the rule: a herd still on the parcel uneasy at the smell of blood (sight 0.4, a herder's knack); for anyone at the
    place where a dog is kept: the dogs wild at the smell (sound 0.5);
  - today and tomorrow: crows and kites over the leavings, by the rule (sight 0.6, own 0.9, not in fog); blood in the snow if snow
    lies (sight 0.9, at the parcel);
  - tomorrow, at the parcel: a dark patch of blood soaked into the ground, with flies if not frost (sight 0.8); the smell of old blood
    and offal if not frost (smell 0.6).
- **On the person:** one who slaughtered today is seen with blood to the elbows (sight 0.6) and smells of it (0.3); the household
  reads it as if inside; nobody reads it of themselves.
- **Reach at a spot:** a sign read at a spot may say how it reaches, as thing signs do (information/noticing.md): by the rule (the
  default); "near", for one who was at the parcel today (worked there, was about it, attended to it); "around", also for one who
  crossed it or worked next to it; "node", for anyone at the place. A sign may be kept from those who did the act, or given only to
  them.

Blood, guts, crows and the bellow are presentation of the record (which beast, where, by whom, which day), deterministic. Numbers are
`calibrate`.

## Why

The paired Combe run (p1_combe_evening, days 26 to 39): the family slaughtered a calf, two cows and an ox, and the only trace was the
doer's ledger line ("You slaughtered a cow of the Hobb cattle (H1): 40 meat, 2 hide. (now in your hands)"). The work event was routine,
so nobody else read it; the rest of the household learned of it only by being told. Zach (2 Nov): "slaughter and related should have
some pretty visceral senses for the person and others nearby ... I imagine it would be hard to miss".

## Alternatives considered

- **Show the work event to others:** one plain line ("Ivo was slaughtering a beast at the Common"), sight only, the same for everyone
  wherever they were; against D4-48 (a bundle, each sign met on its own) and D4-53 (reach by what it is).
- **Leave a carcass-like thing on the parcel (offal, blood) as goods:** would invent items the economy does not have; the record on the
  parcel carries the same signs without them.
- **Make the rows "rule"-reached with a high own conspicuousness:** the rule gives one working there at most 0.5 and one next door 0.1,
  so the kill would often be missed by the person beside it; a reach says plainly who is close enough.

## Open questions

1. Whether a carcass on the parcel (THING/CARCASS) should take over when a beast is slaughtered and left unbutchered (the engine always
   butchers in the act now).
2. The same treatment for the other acts the audit ranks first (review 38.43): night fights, a hunting kill, a house fire.

## Affects

farm.py (`_slaughter`: the parcel record), signs.py (SLAUGHTER, slaughter_context, PERSON rows, spot_rows' reach and `who`),
things.py (`near_spot`), perceive.py (reach for spot signs; `only` respected in what one worked on); spec information/signs.md.

## History

- 2 Nov 2026: built at Zach's request after the paired run's slaughters showed nothing to anyone; written down after (retrospective).
  The audit of other thin signs is review 38.43.
- 2 Nov 2026: the mechanism changed by D4-75 (proposals/every_line_by_the_rule.md): the reach rows with fixed chances became own
  values read by the one noticing rule, calibrated to the same typical chances (the kill certain on the parcel in clear daylight,
  the bellow about 0.9 next door and 0.4 two steps off); fog and the dark now lower the sight of it. The rows are in spec
  information/signs.md.

## Sources

runs/p1_combe_evening (days 26 to 39); review 38.42, 38.43; tests/test_cybertron2_slaughter_signs.py.
