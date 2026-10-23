# Proposal: the senses across every system

**Status:** discussion (23 Oct). **Owner:** 37.4 (information). **Affects:** spec/information/perception.md, cybertron2/engine/signs.py,
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
2. Expert and lay readings: one row with two texts, or two rows gated by knowledge?
3. A cap on signs per day per person, or let the chances do the work?

## Affects

spec/information/perception.md; cybertron2/engine/signs.py, perceive.py; proposals/seeing.md (attention, glimpses).

## History

- 23 Oct: written for Zach after D4-48 ("note down somewhere for me to build out and extend the sensory system"), with his remark
  that what one notices should depend on the person.

## Sources

D4-48; H-7; proposals/seeing.md; cybertron2/engine/signs.py.
