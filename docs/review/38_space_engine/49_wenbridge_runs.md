# 38.49: The Wenbridge runs (wb1 paused at day 14, wb2 to day 30)

Session 37.4, 2 Nov 2026. This note reports the runs of the world designed in 38.46, which tests whether people build. Both runs
use seed 91, so births and weather match, and only the agents' choices and the calibration differ. Starts that failed within a day
are recorded in 38.46.

## The two runs

| | wb1 (paused at day 14) | wb2 (30 days) |
|---|---|---|
| Food, stores and harvest against demand | about 1.0 | about 1.1 planned; the harvest gave 314 |
| Engine changes since wb1 | none | D4-89 overflow at a door stays the house's; D4-90 heaps by bulk; D4-91 the begun wheel shown; D4-92 a fire burns its woodpile at the door |
| Cost | $11.74 | $17.29 |
| Deaths | Odo (day 8), Rob (day 14) | 11 of 14 (below) |
| Alive at the end | 12 (when paused) | 3: Tom, Ellen, Alys |
| Agreements, thefts | 9, 0 | 17, 7 |
| Missed meals | | 84 |

**Deaths in wb2:**
- of hunger: Margery (night 15), Joan (18), Wat (19), Mary (21), Piers, Rob and Will (22), Odo and Randal (26), Kit (28);
- of "a sudden illness" while starving in the cold: Hugh (22).

Winter came on day 18.

## What was built

| Read-out (38.46) | wb1 | wb2 |
|---|---|---|
| The mill | untouched in 14 days (the begun wheel could not be seen) | Piers worked on the wheel from day 2, paid in 3-day work agreements, from 150 units left down to 69.5; it stopped when he starved on day 22 |
| New buildings, rooms, storeys | none | none |
| Fittings | a hearth (Masons) | a hearth (Masons), a hand mill (Hall) |
| Storage | Ellen, Kit and Tom tried bins and a granary on open ground, refused; none built | Gorse Bank cleared to built ground for a granary; never built, for want of timber |
| Clearing | Mary began on Gorse Bank | Gorse Bank cleared (the Hearnes); Rob began Mill Mead, the lord's, without leave, and left it unfinished |
| Lines, tiers, monuments | none | none |
| Repairs | the Hall and Wright's House mended | some; Wright's House and the Masons' cottage ended in ruin |

**The answer to "do they build?":** they start, and they use the trades. The wheel was the one sustained project, and it was paid
for. But nothing new was finished. Food took over the second half of both runs.

## Why it went this way

### Food (the design's fault, twice)

- **I calibrated against 1 meal a person a night.** The village ate about 13 a night for 12 to 14 people: need rises in cold and
  poor shelter, there were two births, and the Hall's grain also went out as wages (41 of its 160 in ten days).
- **The commons were bare within days.** Without weapons, hunting gave little.
- **For later worlds:** calibrate to about 1.3 meals a person a night, net of wages.

### Distribution (the agents, and the aim I wrote)

- **The Hearnes never sold their surplus.** They are two Sonnets and two Haikus, and they reaped 314 grain, far more than the hut
  could hold. They treated it as storage and theft:
  - they covered it, carried it in their hands, barred the door, and cleared ground for a granary;
  - for ten days every one of their prompts carried the Masons' offers (work for 6 grain; 3 stone for 2 grain; 1 coin for 2 grain);
  - they took only one, to buy stone for a hand mill;
  - no Hearne ever offered grain for sale;
  - sharing began after Margery's death (day 15), as a little grain to Joan;
  - from day 18 Ellen sold to the rich at 3 to 4 coin a grain, six to eight times Wat's bid.
- **Wat stole instead.** Wat (Opus) posted his offers to everyone but never dealt with Tom face to face. Then he stole 19 grain
  from the heap at the Hearnes' door (day 12), and Mary took 20 (day 14). The Hearnes saw Wat and barred their door.
- **Correction (2 Nov):** aims are never shown to agents (D4-29: data only), so "kept" did not push them. An earlier draft of
  this note said it did.
- **Probe (Tom's own day-11 prompt, rebuilt from the d11.decide checkpoint, 4 replies per arm).** A reply counted if it took a
  Mason offer, offered grain, gave grain to the Masons, or spoke of feeding them:

  | Arm | Traded or shared with the Masons |
  |---|---|
  | Sonnet, as it was | 0 of 4 |
  | Opus, as it was | 1 of 4 (sold grain to Wat "for coin, which keeps") |
  | Sonnet + "stand back: who needs what you have, what do you need from them, what is about to go wrong?" | 0 of 4 |
  | Sonnet + the Masons' hunger shown as signs (Wat gaunt; Joan thin with a weak-crying newborn) | 0 of 4 |

  Fifteen of sixteen carried on the plan in Tom's own memory text (timber, the granary site, guarding the grain). It is not mainly
  the model tier, and neither a nudge nor seen hunger moved it. Scripts: the session scratchpad, probe/.
- **The grain was not a surplus in the end.** On day 11 the Hearnes held about 150 grain (about 105 meals), near their own need for
  20 days, 4 people and a winter; Will and Kit later starved. From day 10 the village held about half of what it needed, so
  someone was going to starve wherever the grain lay. Keeping it was defensible. The Hearnes' mistake was timing: trading a little
  early for the Masons' stone and labour would have got them their granary.
- **The next probe:** Tom's prompt without his written plan, in a world with a real surplus.

### Engine faults the run exposed (to fix)

1. **The night line said "fire went out: no timber in its store"** whatever fuel was short (run.py). Wat learned a false rule:
   "Put timber in the store each night: our fire went out twice with only firewood".
2. **The prompt gives a house's fire as 1 heat, but the night burns 1 for each hearth and fire ring.** Wat's new hearth beside the
   old ring doubled the Masons' fuel need, unseen (prompt.py and night.py). A hearth and a ring in one room should probably burn as
   one fire.
3. **A theft from the heap at a door reads "slipped into the Hearne hut and came out with 19.2 grain"**: the store's wording for a
   pile outside. That is why barring the door looked like the answer.
4. **An offer cannot name what the work is for or offer teaching** ("work 2 days on the water wheel" is refused). Plain days of
   work go through.
5. **The log's "talked" counts those woken for the answer wave, not who spoke.** A day with speech read "talked 0".
6. **Alys named Odo head of the Arderns the day after he died.** Either the act does not check the dead, or she did not yet know.

### What worked

- **The begun wheel, once shown (D4-91),** was worked on from day 2.
- **The overflow kept as the house's (D4-89):** taking it became a theft, seen by witnesses.
- **The heap's band:** "a heap of grain (perhaps 20 to 30)" read as designed.
- **The woodpile at the door (D4-92).**
- **A labour market:** day wages in coin, Rob hired by Hugh, Piers paid in agreements.
- **Burials and mourning were carried out:** Kit buried Margery at Holm Wood, and Tom and Ellen saw to Wat and Joan.

## Next

- Fix faults 1 to 6.
- Rerun with food at 1.3 a person a night net of wages, so the grain is a real surplus. Before that, run the plan-removal probe
  above (it is cheap).
- Both runs are in `runs/` (wb1_wenbridge_paused, wb2_wenbridge). They are not yet on the Hub (HF_TOKEN is not in this session).

*Current as of 2 Nov 2026.*
