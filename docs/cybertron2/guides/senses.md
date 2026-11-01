# Writing senses: a guide for adding signs to cybertron2

For any session or agent asked to add or change what people in a world can sense. Read it before touching
`cybertron2/engine/signs.py`. Decided rules are in the spec (information/signs.md, noticing.md, perception.md) and DECISIONS.md
(D4-6, D4-48, D4-53, D4-59, D4-70, D4-71); this guide is how to apply them well, with the evidence behind it.

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
4. **It comes as a bundle** (D4-48). One state, several signs across senses, each with its own chance, reach and conditions: the
   obvious one near (the sight of it), fainter ones further off (the sound, the smell, the crows over it), and signs of its
   aftermath on later days. Different people then notice different things, which is what gives them something to tell each other.
   The slaughter bundle (D4-71) is the worked example.
5. **Its chance fits how plain it is.** The one noticing rule (D4-53): own conspicuousness x the parcel's visibility for the sense x
   presence (worked there, passed through, next door) x attention x the eye. Set `p` so that what would be hard to miss is near
   certain for those there (a slaughter, a body, a fire), and what is easy to miss stays rare (a trace, a thing under brush). Hidden
   things go through `hidden` (taught or untaught), not lower prose.
6. **It is concrete and in-world.** One sentence, in the words of someone who saw, heard, smelt or felt it ("the ears rub out hard in
   the hand"). Numbers only where people count (meals, days, head of cattle); judgements as judgements ("about 5 days"). Name things
   by their in-world names, and tagged things with their tag (D4-68).
7. **It does not repeat what the doer already knows.** The doer of an act reads its result line; a sign of the act is for others
   (and for the doer only as a felt or bodily line the result does not give, e.g. blood on one's hands).
8. **It stays quiet when nothing matters.** Ambient lines cost reading and are ignored. Keep their chance low, or let the "Now"
   section (the day and the weather, which anyone awake there senses) carry them.

## Checklist for adding a bundle

1. Find the state: which fields change, when, and who could be near (`here.events()`, the containers, the herds, the parcels).
2. Read how a similar bundle is built in `signs.py` (the same dict shape: `when`, `sense`, `p`, `reach`, `tags`, `text`) and its
   context builder (`thing_context`, `herd_context`, the building and person contexts). Add any state the conditions need the way
   similar systems do, deterministic and replay-safe.
3. Write 3 to 6 signs across senses: the plain one near, the far ones, the aftermath. Check each against "What makes a good sign".
4. Test: a focused test that the bundle reaches those it should (near: near certain; far: rarer), then the whole cybertron2 suite
   (`python3 -m pytest -q tests/ -k cybertron2 -p no:cacheprovider`), then a short bot run and its replay with no mismatches.
5. Record: a proposal (or a retrospective one if built at Zach's request), a DECISIONS row, the spec line in
   information/signs.md, an outcome-log row (CLAUDE.md, "The path of an idea").

## Known gaps

The ranked audit of events and states with thin or no signs is review 38_space_engine/43_sign_audit.md. Signs found wrong while
writing this guide (to be fixed by 37.4): the weeping and "grey-faced and silent" signs of bereavement and "short with everyone"
(invented behaviour); "the bins in X look near empty" and "a baby crying in X" applied to household buildings nobody lives in.

## Sources

Runs c1_combe, c2_combe, c3_combe_rich, p1_combe_now, p1_combe_evening, d1_duo, h2_hollins (the measure above); reviews 38.37,
38.40, 38.41, 38.42; Zach (2 Nov): "slaughter and related should have some pretty visceral senses for the person and others nearby";
"a guidance writeup describing the purpose of senses and what makes a good sense ... for giving to future agents".

*Current as of 2 Nov 2026.*
