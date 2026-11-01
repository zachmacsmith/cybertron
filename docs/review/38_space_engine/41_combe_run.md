# 38.41: Combe, the first run of the belief-built message (c1_combe, days 0 to 39; c2_combe, days 40 to 79; c3_combe_rich, 80 days)

Session 37.4, 1 to 2 Nov 2026. Zach: "build out this new belief prompt building system, and then we can do a very small (have
multiple nodes but only one originally populated, with a family that wants to grow their numbers) but pretty long run, to see if it
works"; "rather than cutting, could you design the new world from the ground up"; "Make sure the test doesn't start out with way
too many models! I want it to be cheap. But it should allow for them to expand to more numbers if they have children". Kept under
40% of the weekly usage (the run's own stop, `llm.week_stop`; the week stood at 23% after it).

## The world (cybertron2/specs/combe_base.yaml, designed from the ground up)

- **Combe** (home): Hobb House (6 beds, hearth, bins), the Byre (plough and harness), a 2-plot Infield of barley, the Common and
  the Hobb cattle (2 cows, 2 oxen, a bull, a calf), Combe Copse (a managed wood), Combe Moor (scrub), a brook. Feeds 4.9 people a
  year (1.6x its three); fuel for 11.
- **Wenmoor** (1 day): a village the fever emptied: 6 plots of rich fallow bottoms, a meadow, the river, an empty damaged house and
  an idle water mill (the only mill: grinding's chokepoint).
- **Holtwood** (1 day): old forest: timber, game, forage.
- **Redscar** (unexplored, 1 day past Holtwood by a faint path): stone and a copper seam.
- **The family:** Ivo (head, Opus 5.5), Margery (Sonnet 5.5) and their son Everard (a child, coming of age as Haiku 5.5). The
  generator's families were too big or too old for a cheap start, so seed 54's was cut by hand to the young couple and their son.
  Customs (kept lines, D4-64): the Hobbs mean to be a great house with ground for every grown child; clearing holds land; Wenmoor
  lies empty with its mill; twelve timber a winter. Lifespan 96 (at 48 every adult turned elder inside the run).
- **Checks before running:** capacity by node (capacity.py); every access gate tried by hand (claiming and repairing the house and
  the mill, the water mill's 40-grain batch, hoeing and claiming the Bottoms, felling and hunting in the Holt, the unexplored way to
  Redscar seen from Holtwood); a 40-day bot run without errors.
- **Fixes found on the way:** the reply schema closed `at` to places while the prompt says `work care at <the child>` (strict
  checks refused care; now free text); a child alive at the start was seeded the customs, which filled the childhood limit so
  nothing could be passed on (the limit now counts lines passed on); the acting channel reported birdsong as a change (ambient
  lines left out).

## How the belief-built message did (against d1_duo, the old message)

| | d1_duo (old) | c1_combe (beliefs) |
|---|---|---|
| decisions | 127 | 110 |
| opening message, median characters | 8,977 | 8,631 |
| **daily message, median characters** | 6,604 | **2,002** (-70%) |
| system text, median | 15,097 | 14,148 (unchanged: still the verb manual) |
| refused or not done, share of results | 6.5% | 7.4% |
| units used | 73.9% | 70.6% |

- **Shorter without loss of footing.** The daily message is a third of the old one; the agents kept their bearings (no one lost
  track of the house or the fields), and without the "Today you could" menu refusals rose by less than one point. The refusals are
  the world's state (the copse picked bare, the cow already milked, a failed crop, a field not yet cleared), not vocabulary.
- **The deltas are used.** Margery's memory reckons the store from the "since you last looked" lines ("firewood -2 (now 58),
  grain -2.6 (now 57.4)"); "the Byre: now damaged" brought repairs the next day, twice.
- **Reading the field from the senses works.** The crop's state reached them as signs ("you judge the barley in the Infield will
  be fit to reap in about 5 days"; "thistle and dock are coming up"), not as a menu line; they weeded and reaped on it. One crop
  failed ("the barley in the Infield has failed") after the reap was put off.

## What the family did

- **Waited to have children until the food was safe.** No one tried for a child until day 18, when the harvest was in and the
  store held about 100 grain; then Ivo and Margery tried most nights ("I'll also give one unit to trying for a child with Margery,
  since the Hobbs mean to be a great house"). Hawise was born on day 26. Not a fault of the prompt: Margery's memory on day 5 reads
  "Grain is short for the year, so save it for winter and seed".
- **Gave the grown son ground of his own, as the custom says.** From Everard's coming of age (day 10) the three cleared new ground
  for him, first on the Common, then Combe Moor (86 clearing acts in all); Ivo claimed it and named Everard his heir; Everard sowed
  "his" field in spring and keeps as a line "Combe Moor, cleared by Ivo and me, is my ground once sown".
- **Did not go to Wenmoor.** It comes up in 28 replies, as a place to go, but nobody went: Combe's fields, cleared ground and cattle
  kept them busy, and home still fed them. Ivo went once to Holtwood to hunt when the store ran down (day 28) and planned a second
  trip at the end. Redscar was never found. Meanwhile the empty house and the mill at Wenmoor decayed to ruins (condition 0 by day
  40): unheld buildings fall down, so the expansion target is on a clock nobody in the world can see.
- **Kept lines (D4-64), in a live run for the first time:**
  - Ivo (Opus 5.5) filled 16 own lines beside the 4 customs: lessons of the farm ("Reap the moment the barley is ripe; rain and
    birds ruin it within days"; "A newly cleared field must be ploughed with the oxen before sowing") and one judgment of a person
    ("Tell Everard his work plainly each morning and repeat it").
  - Margery (Sonnet 5.5) kept 3 own lines; Everard (Haiku 5.5) kept 7 ("Combe Moor ... is my ground once sown"; "Hawise needs one
    unit of care each day"): Haiku does use kept lines (bears on OPEN L-28).
  - **Passing on:** Ivo passed one line to Everard while caring for him as a child ("Keep the best of the harvest for seed, and
    never eat the seed corn"), twice; Everard holds it "from Ivo"; Ivo and Margery each also kept it themselves. Nobody has yet
    passed anything to Hawise (14 days old at day 40).
- **Margery (Sonnet 5.5) left about half her units unused** for long stretches, though her own memory notes it.

## Days 40 to 79 (c2_combe, continued from the end of day 39 under the same code, `continue --days 80`)

**What happened:**

| Day | |
|---|---|
| 42, 48 | Margery conceives; Idonea is born (helped, housed) |
| 44 | Hawise comes of age (Haiku 5.5); Ivo turns elder (born 52 days before the start, lifespan 96) |
| 49 to 51 | Hawise, a youth, passes a line to her baby sister while caring for her: "Keep warm by the hearth, and grow strong with your brother and sister." |
| 53 | Idonea dies of a fever. Ivo leaves for Wenmoor "to claim its empty fields, house and mill for Everard and Hawise", with dried meat and a pack |
| 54 to 58 | At Wenmoor Ivo repairs the Old House (back to sound: it was a ruin by day 40) and claims the place, then goes home |
| 59 to 61 | On Ivo's orders Everard and Hawise take the herd and an ox to Wenmoor: repair, plough and sow the Bottoms |
| 58 to 67 | At Wenmoor they sow barley but carry little food; they forage Wen Meadow bare; Hawise misses meals from day 58 |
| 62 | Ivo dies of old age at Combe. Nobody at Wenmoor knows: news travels only with people (D4-35), and they go on with his orders |
| 67 | Hawise dies of hunger at the Old House |
| 68 | Everard walks home starving, hears of Ivo's death ("Mother, I am sorry about Ivo"), tries to bake bread from grain (refused: bread needs flour, and the only mill is ruined), takes one grain from a store of 64 and sets off back at nightfall with nothing for the night |
| 69 | Everard dies of hunger on the way |
| 80 | Margery, an elder, alone at Combe |

**Reading it:**

- **The family did what the world was built for, and it killed the young.** The custom ("every grown child given ground of their own
  to hold") and the empty valley drew them to Wenmoor; Ivo planned it as a gift to the children. What failed was logistics: nobody
  carried a harvest's worth of food to a place that would not yield for weeks, the meadow was soon bare, and the two Haiku youths
  starved within a day of a full store rather than walk home. The decision to stay was obedience to a head they did not know was
  dead.
- **Perception worked as designed, and it mattered.** The youths knew their own hunger exactly ("I am starving", self, shown
  directly); they did not know of Ivo's death until Everard came home; the Old House's empty store and the picked-bare meadow reached
  them by their own looking. That is the belief-built message doing what it should: a world one sees from where one stands, with
  real consequences of not knowing.
- **Weak spots that are the agents', not the engine's:** carrying food for a night on the road (Everard took one grain); bread
  needs flour, and flour needs a mill (none working); the Haiku youths stayed starving rather than walk a day home.
- **Possible engine and world questions (for Zach):** unheld buildings fall to ruin within 40 days (the Old House was a ruin by day
  40 and had to be rebuilt); a world with one mill, idle, means grain is only ever boiled (no bread) until someone repairs it.
- **Kept lines and passing on:** Hawise passed a line to her sister (the first pass by a sibling); her own lines include "Everard
  gave me his beans by hand when I was starving at Wenmoor" (a judgment of a person, kept). Ivo reached 24 lines; Everard 19.

**Numbers (days 40 to 79):** daily message median 1,923 characters (the old view 6,604); refused or not done 8.9% of results
(higher than c1's 7.4%: travel and a new place); units used 63%. Cost for the 40 days $5.34; both halves $11.78 for 80 days.
Weekly usage at the end: 24%.

## c3_combe_rich: more Opus, more food (80 days)

Zach: "Can you do another run that starts with more opus's and more food initially?" Spec cybertron2/specs/combe_rich.yaml: the
same world and family, but Margery and every child who comes of age on Opus 5.5 (so all four people in the run were Opus); the house
store four times fuller (grain 120, beans 30, dried meat 20, timber 12, firewood 40); 80 days in one go. Same code as c1 and c2.

| Day | |
|---|---|
| 0 to 4 | Margery passes three lines to Everard while caring for him (seed corn, farm lore) |
| 10 | Everard comes of age (Opus); Ivo names him heir |
| 13 to 20 | Ivo and Margery try for a child (seven tries; five days earlier than c1) |
| 17, 23 | Margery conceives; Matthew is born (helped, housed) |
| 24 to 34 | Margery passes four lines to Matthew, among them the house custom "The Hobbs mean to be a great house ..." |
| 30 | The Infield barley fails; Margery resows it to beans |
| 34, 35 | Ivo builds a granary floor into Hobb House (first refused four times: "say which building here to put it in") |
| 41 to 44 | Ivo and Everard go to Wenmoor with the cattle; Ivo claims the Old House and the mill (and sets out to claim the Bottoms and the meadow), finds hay cannot be cut in autumn, and goes home; Everard hoes, finds the meadow bare, and walks home |
| 44 | Ivo and Margery turn elder (both born 52 days before the start, lifespan 96); their next try is refused: no more children |
| 48 to 57 | Everard goes back twice, for an ox left at Wenmoor; hungry, but walks home each time |
| 62 | Ivo dies of old age; Everard and Margery name Everard head, Matthew his heir |
| 68 to 70 | Everard cuts about 44 hay into the Old House on the last summer days, leaves timber, harness and grain there, and walks home |
| 80 | Margery (elder), Everard and Matthew, all fed; the store holds grain 118, beans 207, timber 93, firewood 225 |

**Against c1 and c2:**

| | c1 + c2 (Opus head, Sonnet wife, Haiku young) | c3 (all Opus, rich store) |
|---|---|---|
| cost, 80 days | $11.78 | $28.95 |
| births | 2 (Hawise 26, Idonea 48) | 1 (Matthew 23) |
| deaths | Idonea (fever), Hawise and Everard (hunger at Wenmoor), Ivo (old age) | Ivo (old age) |
| alive at day 80 | 1 | 3 |
| units used | 71%, 63% | 80% (Margery 76%; Sonnet Margery had left about half unused) |
| refused or not done, share of results | 7.4%, 8.9% | 7.0% |
| daily message, median characters | 2,002, 1,923 | 2,892 (four people and a bigger store: more lines change) |
| lines passed on | 2 (Ivo 1, Hawise 1) | 7 (all Margery: 3 to Everard, 4 to Matthew) |
| kept lines at the end | Ivo 24, Everard 19 | Ivo 24, Margery 24, Everard 25, Matthew 13 |

**Reading it:**

- **Food plus Opus removed the deaths, not the ceiling.** No one went hungry at home and the store grew all run (beans 30 to 207,
  timber 12 to 93): the family over-provisioned rather than grew. The cap on growth is the world's, not the agents': one fertile
  couple, both turning elder on day 44 (lifespan 96, born day -52), and no partner for a grown son. c1/c2 had the same window.
  Between Matthew's birth (23) and day 44 Ivo did not try again; whether that is caution with an infant or the six-day care load
  I have not checked.
- **Wenmoor was tried the same way and failed more gently.** The Opus son still went with almost no food (hungry on day 49) and
  lost an ox there, but walked home each time instead of staying. Nobody farmed the Bottoms; the claims were made on day 42 and then
  held from a distance. The Old House and the mill stayed at condition 0; Everard used the ruined house as a hay store.
- **Passing on works when the carer is Opus.** Margery (Sonnet in c1) passed nothing; on Opus she passed seven lines, and Matthew's
  kept lines begin with hers. Matthew is the first person born in a run who holds the house custom, passed by his mother (D4-64:
  customs reach the born only by being passed on).
- **Small frictions found:** `build granary at the Green` is refused with "say which building here to put it in" (a granary is a
  fitting, but the refusal does not say so); `drive` refused "no herd here by that name" for the beasts one led; "You hoed 0 of a
  plot" at the Bottoms in the first day of winter (not checked whether that is the frozen ground or a fault).

**Weekly usage:** 24% before, 31% after (about 7 points for 80 days of four Opus agents).

## Cost

$6.44 for 40 days (about 2.7 agents a day on average): $0.16 a day.

## Open (for the continuation and after)

1. (Answered by c2_combe: they went, and the young starved there.) Whether a second try, with food carried, would hold Wenmoor.
2. Unheld buildings decaying to ruin within 40 days: a design question for the world (should an empty house last a generation?).
3. The system text is still the verb manual (14,000 characters): the next lever (agent_view.md, 38.37).

4. The fertile window: with lifespan 96 and a couple born day -52, children are possible only until day 44; growth past one or two
   births needs younger adults, a second couple, or partners from outside (for Zach).
5. The granary refusal wording and the zero hoe at Wenmoor (37.4, to check).
6. **Correction (2 Nov):** the refusal shares above count one per result line, so an act refused five times in a row (shown "(x5)")
   counts once. Counted per refused act, over results other than speech and notes: d1_duo 12.9%, h1_hollins 20.8%, h2_hollins
   15.3% (old view); c1_combe 21.1%, c2_combe 19.1%, c3_combe_rich 15.9% (beliefs). Different worlds, no paired run: no
   attribution to the view either way. What changed is the kind: under the belief view most refusals are the world's state met
   unseen (no crop left, grass too short, no cow in milk, herd not there), the largest single cause the harvest overshoot (several
   people each plan four reaps of a field that runs out at midday).

*Current as of 2 Nov 2026 (c1_combe, c2_combe and c3_combe_rich complete).*
