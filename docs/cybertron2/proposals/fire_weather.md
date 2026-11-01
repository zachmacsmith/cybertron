# A fire under no roof in the night's weather

**Status:** retrospective, accepted: D4-83 (2 Nov)
**Owner:** 37.4 (the heat rules are 37.2's: OPEN, under 37.2)

## Summary

A camp's fire and a fire in the open take more fuel in rain, wind and snow, and in a downpour or a gale may go out in the night,
taking its warmth; a sound house's hearth is untouched. Data: `heat.weather`, `snow_lying_fuel`, `ring_keeps` (data.py; calibrate).

## The proposal

| Night's weather | Camp or open | Sound house |
|---|---|---|
| clear, fog | as before | as before |
| rain | fuel x1.5 | as before |
| heavy rain, gale | fuel x1.5; goes out with chance 0.5 (x0.8 with a fire ring) | as before |
| snow | fuel x1.25 (x1.15 more with snow lying) | as before |

A fire that goes out has cooked the evening's food but gives no warmth through the night: the cold night's toll and an infant's cold
risk apply. Night line: "The night's weather put the fire out: you lay cold till morning."

## Why

Zach (2 Nov), asking why anyone would build a house rather than live in camps, and how a house could favour children: "what if we
have it that a fire can't be lit in a camp when it rains during the night or snows?" 37.4 answered that people kept fires through
rain and snow and an absolute rule would kill every winter camp; Zach: "yes implement the graded version".

## Alternatives considered

- **No fire in a camp in rain or snow** (Zach's first form): too strong; bands kept winter fires.
- **As before:** a camp's fire as safe as a hearth, so a house gave a family little.

## Open questions

1. Whether a damaged or ruined house's hearth should also feel the weather.
2. The infant risk by shelter (camp against house) and births housed only in a house: proposed to Zach, not yet decided.

## Affects

night.py (fires, `weather_fuel`, `fire_goes_out`), life.py (an infant's cold risk), run.py (the night line), data.py; spec
economy/lodging.md and goods.md (37.2).

## History

- 2 Nov 2026: built at Zach's request; written down after (retrospective).

## Sources

D2-68, D2-157, D2-159 (37.2); runs/b1_wild.
