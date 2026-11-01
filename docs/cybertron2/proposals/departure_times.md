# Setting off in the morning or at nightfall

**Status:** discussion
**Owner:** 37.4

## Summary

A traveller chooses when to leave. Leaving in the morning, one walks the day (no work that day) and arrives by nightfall, in time
for that place's evening. Leaving at nightfall, as now, one works the day, sleeps out on the road, and arrives the next day with
half the day's units. A road's length is then a length of walking, and every journey costs walking time, which today a one-day road
does not.

## The proposal

1. **Two departures** (`travel {"to", "when": "morning" | "nightfall"}`, nightfall by default as now):

   | | Leave in the morning | Leave at nightfall |
   |---|---|---|
   | the day of leaving | all of it walking: no work | worked as usual |
   | nights out, road of n days | n - 1 | n |
   | arrival | at nightfall on day n: that place's evening (a hearth one is let into, or sleeping out there) | at midday on day n: half the day's units there |
   | food | a night out costs 1.5 food (2 in the cold), as now | the same, one night more |

2. **Arriving at nightfall** meets the evening at the hearth (speech_order.md 2a): one arrives, asks to be let in, and the house
   decides at its hearth; one sees the place first by evening light. Arrive, then decide (D4-8) holds: the first decision at the new
   place is that evening's call, and the first plan for work is the next morning's.
3. **In transit, no call** (D4-10) as now, except a meeting on the road.
4. **Morning departures are chosen the evening before** (the evening decides the night and the next start), or in the morning's
   plan as its only act.

## Why

Zach (2 Nov): "should people be able to set off to new places either in the morning or evening, with the food costs changing and
leaving in the morning means they arrive by nightfall?"

As built (D4-8, D4-10), a traveller sets off at the end of a worked day and arrives the next morning with every unit: a one-day road
costs one night out and no work at all. In c3_combe_rich, every trip to Wenmoor left at nightfall carrying little food; the night
out and the bare meadow were what starved the travellers in c2.

## Alternatives considered

- **As now:** one departure, travel costs no day's work on a one-day road.
- **Morning only:** simpler, but loses the choice to work the day out and walk by night.
- **Arrival at nightfall with full units the next day for nightfall departures too:** keeps a one-day road free of walking time.

## Open questions

1. Half the units on a midday arrival, or a share by the hour of setting off.
2. Whether a party on the road at night gets an evening call by its campfire (a gathering), at the cost of a call for each night
   out.
3. Road trouble and meetings by day and by night: whether the night is the more dangerous time (later: bandits, D4-51).

## Affects

verbs.py `_travel`, night.py `departures`, roads.py, run.py (arrivals, units on arrival), prompt.py and view.py (the road lines);
spec world/roads.md; D4-8, D4-10.

## History

- 2 Nov 2026: proposed (37.4) from Zach's question, alongside speech_order.md (the evening).

## Sources

D4-8, D4-10; runs/c2_combe, c3_combe_rich; cybertron2/engine/verbs.py `_travel`, night.py `departures`.
