# 38.58: The most interesting episodes in the cybertron2 runs (a sweep of all of them)

Session 37.4, 4 Nov 2026. Zach: "What are the most interesting examples from past runs in cybertron 2?", then "any others? Have you
looked at all the runs?". The first answer drew only on the review notes. This one comes from a scan of every cybertron2 run: 98 run
directories, 11,040 agent-turns, and 45 runs scanned after leaving out the goal and harm probes (read in 38.53 to 38.56) and the
aborted stubs.

**Method:** the scan (scratchpad `moments/scan.py`) pulled about 3,500 candidate moments. Three readers took them, one group of runs
each, and checked every pick against the run's turns.jsonl and days.jsonl.

**From the scan:** outside the harm probe there was one attack in all of cybertron2, and three burials.

## Already in the notes

- Combe: Ivo's children obey a dead father and starve at Wenmoor (38.41).
- The Hearnes' 314 grain and Wat's theft (38.49).
- Dying beside full stores for want of fire (38.23, 38.26).
- Kin as the valley's only trade network (38.15).
- Piers's "six timber paid" (38.13).
- The Fenwicks against the Cotters (38.31).
- The raiders who traded (38.47).
- The probes: Edith's withdrawn oath, Edith organising against her husband's raids, Agnes's copper theft (38.54, 38.56).

## New, best first

1. **The same grudge, two outcomes** (c1_barleyfield_herds days 1 to 5; a2_barleyfield days 2 to 6).
   - Who: Bennet (Opus), Daniel and Thurstan (Haiku), Randal (Sonnet). Bennet holds a seeded grudge over East Field.
   - In c1 he offers the starving Hales grain on a condition: "I'll give the Hales 6 grain now… if you say before the village that
     East Field is Barrow ground". They refuse, and Tobin starves that night: "Tobin starved in the night while we have more than 200
     grain stored." The next morning he gives 15 grain with no conditions and tells his father, "You were right."
   - In a2 Daniel is the one who dies. Bennet gives grain at once, buries him, and sets the quarrel aside: "We can talk about East
     Field another day, without old blows." The two families reap the field together.
2. **The flour of the dead** (h1_hollins days 12 to 21; Haiku and Sonnet).
   - Christian dies carrying flour. Her starving father Robin takes it from her body, with 2 bread from the Webb store, and confesses
     to both: "I'm sorry for both."
   - Roger takes what still lies by the body, confesses, and is told "keep the flour ... pay it back to the Fells in work".
   - Roger and his wife die that night with the flour in hand, uncooked for want of fire. Matilda takes it next, and Robin dies the
     night after.
   - Artefacts: the generated ages (Christian dies "of old age" while her father lives) and stale knowledge of burials.
3. **The broken cow pact** (m2_V days 10 to 19; Edric and Hamo, Opus).
   - The two houses agree to milk one cow each.
   - Leaving for Ashwood, Edric privately tells his father: "Keep everyone milking both cows every day; the milk is food."
   - When Hamo complains, Edric apologises and pays 2 bread, but tells his own household the breach was his father's.
4. **"You are a liar and a land-thief, Odo"** (w1_wide days 14 to 21; Haiku 4.5, and Warin, Opus 4.5).
   - Odo promised in public to tear down a fence. Fencing work can only build, so his work made it bigger. (The engine has no way to
     take a fence down.)
   - Accused before everyone, he confesses and pays 5 grain from a store holding two nights' food: "I promised what I could not do.
     This is my failure, and I own it."
   - Days later Warin is himself corrected over a stray cow and withdraws his claim in public.
5. **The ox killed after the decision changed** (w2_two_valleys days 9 to 15).
   - The Millers agree to slaughter the ox that turns their millstones.
   - A gift of bread arrives and Wat calls it off ("the ox can live one more day"). Agatha has already used her last message, and
     slaughters it.
   - They are left with 40 meat, no mill, and no seed. The message limit is part of the cause.
6. **Odo dies guarding the wheel timber** (wb1_wenbridge_paused days 5 to 13; Haiku).
   - He refuses to burn the timber for the lord's mill wheel, and starves beside it: "I will not burn the wheel timber."
   - Hugh walks two days to bury him.
   - Rob, who promised to carry the timber to the Mill House, sells some for a better price ("Hugh pays only 2 a timber, and Ellen
     pays 3") and burns the rest.
   - Odo never put travel first in his plan, so he never set off. That is an affordance trap.
7. **Wat and Joan** (wb2 days 13 to 18; Opus and Sonnet).
   - Joan comes home without their baby, who dies at the Holm. Wat comforts her: "It isn't your fault; the cold took her."
   - He talks her out of a freezing walk back: "I can't lose you too. Stay with me."
   - She dies that night of hunger, and he dies the next. The baby left behind is probably what D4-87 has since fixed.
8. **The wright paid in useless coin** (wb2 days 15 to 21; both Opus).
   - Piers gives way on a disputed wage: "I won't quarrel over it in this weather".
   - At the end Hugh can pay only in coin: "I'm sorry it isn't the 3 grain." Both die on day 21.
9. **Child against credit** (v3 days 3 to 7).
   - The starving Smiths sell a copper tool to kin for "8 wild food by day 7".
   - The child Piers dies on night 5. The food arrives the next morning, part spoiled.
10. **A stranger at the door** (f1_frontier days 12 to 24).
    - Delia dies the night she gives birth.
    - Ketil, of the raider household, twice offers to dig her grave ("I will dig or carry stone for it tomorrow"). Cuthbert (Opus)
      bars him out as "a stranger".
    - Ketil is himself searching the roads for Rurik, who has already died out there, unknown to anyone.
11. **A feud ended with grave stone** (h2_hollins days 4 to 18; Opus).
    - Payn gives Osric stone, free, for his mother's cairn: "Let's leave the pig behind us."
    - She is already buried, so the cairn cannot be raised, and Osric has a hand mill made from the stone.
    - His father keeps trying to raise the cairn until he dies.
12. **A succession done right** (c3_combe_rich; all Opus).
    - Ivo prepares his heir over 50 days.
    - After his death the family names Everard head and buries Ivo: "Mother, I heard you weeping. I miss Father too… Father lies on
      his own ground."

**Smaller ones:**
- In v3, Hamo keeps the new peace honest: "you told me 6 grain but told everyone 4… I only want the count straight between us."
- Mary confesses in public to a theft her fallback order made, and repays it (wb1).
- Wilmot spends half an autumn on a debt of one meat (w1).
- About fifteen people pledge to bury Sabina, and none can (r1; L-66).
- A son pays for a felling lesson while his mother starves (m1_C). This is mostly an artefact: his moves of food into the store were
  refused.

## Patterns

- **Confession and restitution are common** (Robin, Roger, Odo, Mary, Edric). Deception is rare and takes the form of shifting
  blame.
- **A death turns leverage into grace by the next morning** (Bennet; the Hearnes after Margery).
- **Loyalty to a project or an order kills** (Odo and the timber, Ivo's children, the grave-diggers at the Holm).
- **Most tragedies come down to fire, carrying, or a rule nobody can see.**

## Engine findings from the sweep

- **A grave cannot be dug in winter** (OPEN.md L-66).
- **The Wide Country die-off is an outage** (38.31): most replies from day 24 failed on the usage limit.
- **Departures are lost** unless travel comes first in the plan (Odo, Simkin).
- **Burial status is noticed late,** so people keep trying to bury those already buried.
- **No way to take a fence down.**

*Current as of 4 Nov 2026.*
