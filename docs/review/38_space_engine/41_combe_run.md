# 38.41: Combe, the first run of the belief-built message (c1_combe, 40 days; c2_combe continuing to 80)

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

## Cost

$6.44 for 40 days (about 2.7 agents a day on average): $0.16 a day.

## Open (for the continuation and after)

1. Whether food pressure, a second child and Hawise's coming of age push anyone to Wenmoor (c2_combe, days 40 to 79).
2. Unheld buildings decaying to ruin within 40 days: a design question for the world (should an empty house last a generation?).
3. The system text is still the verb manual (14,000 characters): the next lever (agent_view.md, 38.37).

*Current as of 2 Nov 2026 (c1_combe complete; c2_combe running).*
