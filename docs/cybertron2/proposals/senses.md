# Proposal: the senses across every system

**Status:** partly accepted, largely built (swept 5 Nov). Decided: one observer term, the eye for the land (D4-50, D2-91);
the one noticing rule (D4-53, D4-75), which replaces relevance as a factor in the chance; much of §2's coverage through D4-59,
D4-71, D4-74, D4-90, D4-91 and D4-99 (signs.py), written up for later work in guides/senses.md. Built: expert and lay readings,
caps on lines a day. Still open: the observer terms beyond the eye and the knack (§1), and the rest of §2. **Owner:** 37.4
(information). **Affects:** spec/information/perception.md, cybertron2/engine/signs.py,
perceive.py; every system that has states (economy, conflict, life, environment, institutions).

## Summary

D4-48 makes every state show itself as a bundle of possible signs, each with a sense, a chance, conditions and a knack, rolled by
each observer on its own. The first pass covers fields, crops, pastures, herds, buildings, people, the sky and what grows wild
(signs.py). This file is Zach's worklist for extending it (23 Oct: "note down somewhere for me to build out and extend the sensory
system more for all the systems we have so far and build in the future"): what each observer brings to noticing, and which
systems still speak in one line or not at all.

## The proposal

### 1. What the observer brings (Zach, 23 Oct: "the ones they notice might depend on them")

Today a sign's chance depends on the sign, attention to its subject, relevance (one's own household, concerns, hunger) and a knack
(practice at the matching work). Proposed further terms, each a multiplier on a sign's chance:

| Term | What it is | Example |
|---|---|---|
| where one spent the day | signs of the parcel or building one worked at are read more; far corners of the node less | a reaper notices the rooks at the next field, a smith in the forge does not |
| the sense itself | each person has a sharpness per sense, drawn once (an old man hears less; a child sees more) | a smell sign missed by someone with a cold |
| age and stage | youths notice people and novelty; elders notice weather and the land's long changes | an elder reads "frost not far off" twice as often |
| temperament | an observant or a dreamy person, drawn once (seeing.md's open question 2) | |
| mood and body | hunger narrows notice to food; a wound or exhaustion lowers everything | |
| what one cares about | concerns and interests, already in relevance; extended to people one loves or fears | a mother notices her son's hunger first |
| what one knows | a sign may need knowledge to be read at all, not just a knack (a blight only a farmer names) | others see "the barley looks poorly" |
| company | a sign pointed out by someone who noticed it (a `say` naming it) is noticed by those who hear | |

The same sign can come in **two readings**: the expert's ("the ears rub out hard: ready tomorrow") and the lay one ("the barley has
turned gold"); who gets which follows knowledge.

[5 Nov: of these terms, built: the eye (D4-50, D2-91; sight only, D4-75), the knack (perceive.py `knack`), where one spent the day
as presence along the day's route (D4-62, D4-75) and attention x3 for what one worked on, one's household and house always read
(D4-75); hunger, ties and concerns only order what is noticed (perceive.py `relevance`), not its chance. Still open (5 Nov): a
sharpness per sense, age and stage, temperament, mood and body, knowledge needed to read a sign, company (none in things.py or
perceive.py). D4-72 rules out signs of feelings the person did not choose]

### 2. Coverage by system

| System | States with signs now | Missing, to build |
|---|---|---|
| crops and fields | growing, weeds, ripe, birds, ripe-to-rot, rot, blight, frost risk; soil; wet and hill ground; works | crop by crop (beans, rye look different); dibbled rows; seed selection's even stand; a plot's history ("cropped three years running") |
| pastures and herds | grass, hay-ready, dung; the herd by role, calves, hunger, the bull, milk, unwatched by a crop | heat and calving to come; lameness; a strange beast in the herd; tracks where a herd strayed; a herd driven off (rustling) |
| buildings | condition, draught, camp sagging, smoke, cold hearth, woodpile, baking, grinding, hammering, smelting fumes, fittings, door, bins near empty | locks; a light at night; someone inside; repairs under way; a building's stock seen through a window; noise of a crowd in a hall |
| people | hunger, wounds, carried gear and loads, travel gear | tiredness from working late; illness; pregnancy; grief (a death in the household); drink; new clothes or tools (wealth); who is with whom; someone avoiding someone |
| the sky and seasons | frost, cold, season's turn, frost coming, spring coming | weather when built (rain, wind, storms, wet and dry spells: 37.2's incident post); omens; the moon for night travel |
| wild resources | forage, game, wood, the seam, the quarry | animal signs by kind (wolves, boar); a spring's flow; fish |
| trade and agreements | offers open (as lines in the prompt) | a stall's display; a merchant's cart arriving heavy or light; prices overheard; someone counting coin; a debtor avoiding a creditor |
| claims and disputes | a use against a claim is a witnessed event | boundary stones moved; a fence put up; a field sown by the wrong people seen from afar |
| travel and roads | departures and arrivals as events | on a road: tracks, a camp's ashes, a body, other travellers (place.md's open question); at an unexplored way: a path worn or overgrown |
| conflict | fights and raids as events | the watch's fire at night; armed men gathering; a barred door that was open; smoke of a burning |
| knowledge | seeing a technique done (watching) | a new tool in someone's hands; a building of a kind never seen; a recipe's smell (cheese, charcoal) |
| institutions and law | none | a notice posted; a register kept; an officer's badge; a court gathering |
| life | deaths as events | a birth; a sickbed; an old person failing; a child growing |

[5 Nov: much of the "missing" column is built (signs.py): newer systems (D4-59: pregnancy, babies, led beasts, arrivals, failing
elders, building work, firewood, felling, charcoal, scrub); events and their aftermath (D4-74: fights and raids in the night, a
theft, a birth, calving, a burial, beasts driven, a house breaking or mended, food rotting, things made, sleeping out); slaughter
(D4-71); weather on fires (D4-83); heaps by bulk (D4-90); a fitting begun (D4-91); graves (D4-99); tracks, ashes, bodies and
travellers on the road. Dropped by D4-72: grief and someone avoiding someone (acts and feelings not chosen). Still open (5 Nov):
locks, illness and tiredness (no such states), wild animals by kind (D2-95, later), trade's displays and prices overheard,
boundary stones, institutions and law (none built), omens and the moon]

### 3. How to extend

Each row is data in signs.py (a condition, a sense, a chance, tags, a knack, and later an expert/lay pair). A new system adds its
table and a context; the observer terms in §1 go into perceive.evening's chance, one function per term, each with its own
parameter, so a run can turn them on one at a time and measure what they change.

## Why

- H-7: perception is the main design surface. Bundles make knowledge partial and personal, which is what makes telling, trusting
  and checking worth doing.
- Observer terms make the same village look different to different people, so information has value and travels.

## Alternatives considered

1. **One line per state** (perceive.py before D4-48): replaced.
2. **A narrator model describing each scene** (seeing.md §4): richer words, but not reproducible across arms and not a record of
   what was there to see; kept as an experiment.

## Open questions

1. Which observer terms first (§1), and their sizes.
   [still open (5 Nov): the eye was first (D4-50; none x0.5, ordinary x1, keen x3, noticing.md); no other term of §1 is decided
   or built beyond the knack and presence]
2. Expert and lay readings: one row with two texts, or two rows gated by knowledge?
   [built: signs.py, two rows gated by knowledge (`knows: tech` for the expert, `lay: tech` for one who does not), on things at a
   spot and the road; crop and herd rows use a knack instead; no decision names the form]
3. A cap on signs per day per person, or let the chances do the work?
   [built: perceive.py, both: the rule's chances, then caps (the day's notice up to 5, 7 when attending the place; the attended
   subject up to 9; ambient and worked lines up to 4, noticing.md); the notice and attention caps are not in the spec]

## Affects

spec/information/perception.md; cybertron2/engine/signs.py, perceive.py; proposals/seeing.md (attention, glimpses).

### 4. From the first runs (hamlet, two valleys; 23 Oct)

Signs that point at a job are used: weeds led to weeding, standing water to ditching, slumping banks to mending, ripeness to reaping,
cows heavy with milk to milking (17 of 19). Signs about animals' condition are mostly ignored: "lowing and restless" 0 of 8, a new
calf 1 of 15, a pasture grazed bare 1 of 9 (Water Meadow grazed to the earth and the herd left on it). To try: clearer words that say
what the sign means ("the cows are lowing: they are hungry"), and making such signs a concern of the herd's holders. Nobody attends
to the sky or the place in general; season and weather signs reach them only in passing.
[built in part: herd rows now say what they mean ("lowing and restless: they want feeding", signs.py), and the measured evidence on
what is acted on is in guides/senses.md; still open (5 Nov): herd signs as a concern of the herd's holders (signs.py emits herd
rows with no concerns)]

## History

- 5 Nov: swept (37.4) against DECISIONS, the spec (information/noticing.md, signs.md, perception.md), guides/senses.md, OPEN.md
  and the engine (perceive.py, signs.py, things.py). The worklist's coverage (§2) was largely carried out through other proposals
  (more_signs.md, sign_bundles.md, slaughter_signs.md, heap_sizes.md: D4-59, D4-71, D4-74, D4-90) under the one noticing rule
  (D4-53, D4-75); the observer terms beyond the eye stay open. Open questions: 2 built, 1 still open.
- 23 Oct: one observer term decided for one system (D4-50): an eye for the land, drawn once per person, some with none, applied to
  how bare a place is; the signs' chances grow with bareness. The rest of §1 stays open.
- 23 Oct: §4 added from the first runs (which signs are acted on, which ignored).
- 23 Oct: written for Zach after D4-48 ("note down somewhere for me to build out and extend the sensory system"), with his remark
  that what one notices should depend on the person.

## Sources

D4-48; H-7; proposals/seeing.md; cybertron2/engine/signs.py.
