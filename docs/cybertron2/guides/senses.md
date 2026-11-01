# Writing senses: a guide for adding signs to cybertron2

For any session or agent asked to add or change what people in a world can sense. Read it before touching
`cybertron2/engine/signs.py`. Decided rules are in the spec (information/signs.md, noticing.md, perception.md) and DECISIONS.md
(D4-6, D4-48, D4-53, D4-59, D4-70, D4-71, D4-72, D4-74, D4-75); this guide is how to apply them well, with the evidence behind it.

## What senses are for

An agent learns about the world outside itself through three routes (review 38.40): what it knows of itself is shown directly (its
body, what it carries, its units); what was said and done between people lives in its own conversation and memory; **everything else
about the world reaches it through the senses**, as beliefs with a date. Senses are therefore the channel for:

1. **Hidden change made visible.** A crop ripening, a store running down, a fence failing, a death in the night: the state changes
   whether or not anyone looks; a sign is how a person finds out, and only if they could have.
2. **Consequences felt.** A slaughter, a fight, a birth, hunger in a house: these should land on the people near them.
3. **News by presence.** Signs are local (D4-35). They travel further only as people carry them, which is what makes being there,
   watching and asking matter.
4. **Uncertainty.** A sign can be missed, glimpsed or misread. That ignorance is the point: in c2, two youths kept to a dead head's
   orders because news of his death had not reached them.

## What makes a good sign

1. **It reads only what the state holds.** A sign is a sentence about the engine's state, at the state's resolution (CLAUDE.md:
   "a picture may only show what the state holds"). If the engine does not decide it, the sign may not assert it.
   - **Never invent an act or a feeling a person did not choose.** "X was heard weeping" and "X is short with everyone today" put
     acts in an agent's mouth that its own model never chose (Margery, told by Everard that she was heard weeping, had to accept a
     grief the engine wrote for her). Signs of a person's body are fine: hunger, injury, age, pregnancy, a baby carried. Their
     behaviour comes from their own replies and acts.
   - **Point at the right thing.** "The bins in the Byre look near empty" fired 172 times in five runs and was never acted on: the
     Byre holds hay and dung, the sign reads food. "A baby crying in the Byre" fired 62 times: the sign counted everyone of the
     household as living in every household building. Check which buildings, people and goods a condition really covers.
2. **It is worth acting on.** Measured over seven runs (14,387 sign lines shown; "acted on" means two of the line's content words
   reappear in that day's reasoning, plan or speech; crude, but the contrast is large):

   | Acted on most (share) | Acted on least |
   |---|---|
   | a body found (1.00), mould on stored grain (0.97), "the ears rub out hard in the hand: the barley is ready" (0.96), rain on ripe barley (0.94), sheaves stooked with the rest still standing (0.93), barley beaten flat (0.90), beasts trampling a crop (0.77-0.86), "fit to reap in about 5 days" (0.79), thistle and dock coming up (0.77) | static facts ("the Byre has bins", "the Byre is sound"), weather moods and forecasts, "it stayed bitterly cold", "voices and work about the houses", "nothing out of the ordinary", someone set off on the road, a baby carried (all 0.00) |

   The pattern: signs that change what one should do today are used almost every time; standing facts and ambience are never used.
   Forecasts were ignored here too: a fact the agents had no way to act on in these worlds.
3. **It tells a change, not a standing fact.** What a building has, where a field lies, how big it is: that belongs in the place's
   layout ("Here, as you see it"), shown once. A sign is for what is different now.
4. **It comes as a bundle** (D4-48). One state, several signs across senses, each with how plain it is, its conditions and scope: the
   obvious one near (the sight of it), fainter ones further off (the sound, the smell, the crows over it), and signs of its
   aftermath on later days. Different people then notice different things, which is what gives them something to tell each other.
   The slaughter bundle (D4-71, below) is the worked example; "The four kinds of sense" says which signs a bundle needs.
5. **Its chance comes from the one rule, never from the row** (D4-53, D4-75). Every perceived line about the world takes its
   chance from the noticing rule: the row's base chance (1 unless set) x own x the visibility for its sense (cover, weather, the
   dark, masking) x presence (where one was that day, or slept; for sound and smell, steps in the parcel graph) x attention x the eye
   (sight only). **Always build bundles this way:** a row gives how plain the thing is (`own`; above 1 for what is plain from far off,
   like a glow or a bellow), its sense, its conditions (`when`) and its scope (`who`: the doer, the others, those inside); the rule
   gives the chance. `reach` is only shorthand for the rule's inputs (near: a close look at the spot; around: the spot and next
   door); `night=True` marks a sign sensed in the dark. Then **check the outcome** against the chances you intend for typical cases
   (on the parcel, next door, across the place; clear, fog, night) and adjust the inputs (`own`, and if it is general, the factors in
   `data.NOTICING`), never the result. Hard to miss should come out near certain for those there in clear daylight; easy to miss
   rare. Hidden things go through `hidden` (taught or untaught), not lower prose.
6. **It is concrete and in-world.** One sentence, in the words of someone who saw, heard, smelt or felt it ("the ears rub out hard in
   the hand"). Numbers only where people count (meals, days, head of cattle); judgements as judgements ("about 5 days"). Name things
   by their in-world names, and tagged things with their tag (D4-68).
7. **It does not repeat what the doer already knows.** The doer of an act reads its result line; a sign of the act is for others
   (and for the doer only as a felt or bodily line the result does not give, e.g. blood on one's hands).
8. **It stays quiet when nothing matters.** Ambient lines cost reading and are ignored. Keep their chance low, or let the "Now"
   section (the day and the weather, which anyone awake there senses) carry them.

## The four kinds of sense

A thing that happens can show itself four ways (Zach, 2 Nov). Not every event needs all four; use those that fit, and say in the
bundle's comment which it gives. Each maps onto the rule:

1. **To the doer, as they do it:** felt or bodily, and only what the result line does not already say; scope `who="doer"`, usually
   touch (which reaches only where one is). Example (SLAUGHTER): "the cow kicked as it went down, and its blood ran hot over your
   hands: you are red to the elbows and stink of it".
2. **To those nearby as it happens:** by presence and distance; sound and smell carry by steps, the far, faint ones (sound, smoke,
   a glow) reach the whole place. Example (FIRE): "a glow over Hale House in the night, flames through the thatch" (own 3, its own
   light) and "the roar and crack of fire from Hale House in the night" (`night=True`, carries).
3. **Lingering traces afterwards:** on later days, fading: the row's `when` reads the days since (`x.age`). Example (FIGHT): "the
   ground by the Green is scuffed and trampled, with dark spots of blood on it", that day and the next.
4. **Conditional:** a sign that exists only under certain circumstances, in its `when`: snow, rain, frost, the dark, dogs kept, a
   door, who is inside. Example (SLAUGHTER): "blood in the snow on the Common, trodden pink where a beast was killed" (only when snow
   lies).

### Worked example: the slaughter bundle (D4-71, D4-75)

Intended chances first, then `own` set until the rule gives them (ordinary eye; the valley: the Common Pasture, the Green next
door, Long Field two steps off, Alder Copse three):

| Sign | Sense | Own, reach, scope | Intended | Actual: on it / next door / two / three (clear) | Fog | Night |
|---|---|---|---|---|---|---|
| who killed which beast | sight | 1.0, near, others | certain on the parcel | 1.0 / 0 / 0 / 0 | 0.3 | 0.1 |
| the butchering | sight | 0.8, near, others | likely on it | 0.8 / 0 / 0 / 0 | 0.24 | 0.08 |
| the smell of guts | smell | 1.8, around | on it and beside it | 0.9 / 0.54 / 0 / 0 | same | same |
| the bellow | sound | 2.0, others | near certain beside it, about 0.4 across the place | 1.0 / 0.9 / 0.4 / 0.2 | same | x1.2 |
| the blood over one's hands | touch | 2.0, doer | certain for the doer | 1.0 (the doer) | same | same |
| the herd uneasy | sight | 0.38, herder's knack | now and then | 0.19 / 0 / 0 / 0 | 0.06 | 0.02 |
| crows over the leavings | sight | 0.9 | sometimes, from far rarely | 0.45 / 0.09 / 0.05 / 0.05 | 0.14 | 0.05 |

## Checklist for adding a bundle

1. Find the state: which fields change, when, and who could be near (`here.events()`, the containers, the herds, the parcels).
2. Read how a similar bundle is built in `signs.py` (the same dict shape: `when`, `who`, `own`, `sense`, `reach`, `night`, `tags`,
   `text`; no `p` on a new row) and its
   context builder (`thing_context`, `herd_context`, the building and person contexts). Add any state the conditions need the way
   similar systems do, deterministic and replay-safe.
3. Write 3 to 6 signs across senses, by the four kinds that fit (to the doer, nearby, lingering, conditional). Give each an `own`,
   never a chance. Check each against "What makes a good sign".
4. Calibrate: compute each row's chance through `perceive.chance_of` for typical cases (on the parcel, next door, across the place;
   clear, fog, night) and adjust `own` until they land where you intend; write the table into the bundle's proposal.
5. Test: a focused test that the bundle reaches those it should (near: near certain; far: rarer; fog or night lowering sight, not
   sound; lingering; conditional), then the whole cybertron2 suite
   (`python3 -m pytest -q tests/ -k cybertron2 -p no:cacheprovider`), then a short bot run and its replay with no mismatches.
6. Record: a proposal (or a retrospective one if built at Zach's request), a DECISIONS row, the spec line in
   information/signs.md, an outcome-log row (CLAUDE.md, "The path of an idea").

## Known gaps

The audit (review 38_space_engine/43_sign_audit.md) is built (D4-74): bundles for fights and raids in the night, a hunting kill, a
house fire, a birth, food rotting in a store, a guard posted, beasts driven, things made, sleeping out, ploughing and reaping,
quarrying, a theft, calving, a house breaking or mended, a burial, milking and minding. Still open:

- **Old age and illness:** the engine holds no illness before a death ("a sudden illness" is only a cause), so nothing can show it;
  old age shows only as "failing". An engine gap first.
- **A threat:** it leaves no trace; its event line is read by the rule. A sound of it would put cries in a mouth that did not choose
  them (D4-72).
- **A raid as it happens** reaches only those fuse wakes (by the rule since D4-75); neighbours who are not woken get nothing until
  the gouges at the door next morning.
- **Smell** has no visibility (D2-101): rain and wind do not touch it.
- **The sky** is not lowered by the weather it describes; whether fog should hide other sky lines is open.

Fixed while writing this guide (D4-72): the bereavement signs and "short with everyone" removed; signs about a building's dwellers
limited to buildings with beds. Every line by the one rule: D4-75 (proposals/every_line_by_the_rule.md).

## Sources

Runs c1_combe, c2_combe, c3_combe_rich, p1_combe_now, p1_combe_evening, d1_duo, h2_hollins (the measure above); reviews 38.37,
38.40, 38.41, 38.42; Zach (2 Nov): "slaughter and related should have some pretty visceral senses for the person and others nearby";
"a guidance writeup describing the purpose of senses and what makes a good sense ... for giving to future agents".

*Current as of 2 Nov 2026.*
