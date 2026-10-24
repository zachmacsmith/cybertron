# Carcasses: what a beast leaves when it dies

**Status:** retrospective, accepted: D4-52 (built 24 Oct at Zach's request; written down afterwards)
**Owner:** 37.4 (places, things, perception); 37.2 owns livestock and goods, so the numbers are theirs to tune

## Summary

A beast that dies leaves a carcass where it fell, as a person leaves a body: meat and its hide, fit to eat for about a day, then
gone off, then bones. On a road a dying beast may leave nothing (it wandered off to die) or lie hidden off the road.

## The proposal

- A beast that dies of hunger at a node, or on a road, leaves a thing at a spot of the kind `carcass` (world/things_in_places.md),
  held by the herd's holders, with meat and the hide.
- **Meat:** a share of what slaughtering it would give, by how it died: a quarter if it starved, half otherwise (calibrate). The hide
  whole.
- **Fit to eat about a day:** the meat is good the day after the death; that night it becomes rotting meat (no food). Bones after
  about six days.
- **On a road:** for each beast that dies, 0.3 it leaves nothing, 0.3 a carcass off the road out of sight (own conspicuousness x
  0.2), 0.4 one by the road (calibrate). A herd that is gone for good (wandered beyond finding) leaves nothing.
- **Noticed** by the noticing rule like a body (own conspicuousness 0.9; bones 0.3); its signs are a bundle (signs.py CARCASS): a
  dead beast, crows going down, the stink once it has gone off, a starved one all hide and bone, bones picked clean.
- **Taken** like anything lying at a spot (`take {item: meat, from: <place>}`), or in the find call on a road.

## Why

- Zach asked whether herds leave bodies as people do; they did not: a beast that died simply vanished, though the spec already
  imagined "a dead ox by the road" among the things a traveller notices (information/noticing.md).
- A dead beast is a real event in a farming world: a sign that something is wrong (hunger, a herd lost on the road), a windfall for
  whoever finds it in time, a stink and crows if not.
- The meat is limited, or letting cattle starve would cost almost nothing (slaughter gives 40 meat a cow): little meat on a starved
  beast, and it keeps only about a day (Zach: "realistic, no?" Yes in warm weather; in a frost it would keep longer: open below).
- On a road a beast that dies may have wandered off to die, or lie out of sight (Zach), so a herd lost on a road does not leave a
  trail of carcasses for every traveller.

## Alternatives considered

- No carcass (as before): loses the sign and the windfall.
- The full slaughter yield: makes starving cattle nearly free.
- Butchering as work (2 units, as slaughter) before the meat can be taken: more faithful, more machinery; not built.

## Open questions

- Does a carcass keep longer in a frost (as hung game does)? Built as one day in every season, as Zach said.
- The meat shares and the road chances are guesses (calibrate; 37.2).
- Scavengers (wolves, dogs, birds) eating carcasses: with wild animals (OPEN L-2).

## Affects

spec/world/things_in_places.md (written: D4-52); spec/economy/livestock.md (37.2: a pointer from dying); signs.py CARCASS.

## History

- 24 Oct: Zach asked whether herds leave bodies when they die; 37.4 answered no and proposed carcasses with limited meat. Zach: dead
  cattle edible about a day then gone off, and on roads a chance of no body or a hidden one. Built the same day (things.py
  `leave_carcass`, farm.py starvation, herds.py road deaths, night.py going off, signs.py CARCASS; tests in test_cybertron2_package_c.py)
  and written down here afterwards: retrospective, accepted D4-52.

## Sources

Conversation, 24 Oct; review 38.25.
