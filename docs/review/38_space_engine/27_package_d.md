# 38.27: Package D (children and reproduction) built; the Hollins world

Session 37.4, 24 Oct 2026. Built from 37.2's brief 02w (D2-138 to D2-153; spec/life/birth_and_death.md). Code on `wp/cybertron2`:
cybertron2/engine/life.py (new), world.py, night.py, run.py, verbs.py, here.py, prompt.py, generate.py, data.py (LIFE); tests
tests/test_cybertron2_package_d.py (14) and test_cybertron2_hollins.py (3). All 131 cybertron2 tests pass.

## 1. What was built (02w §1)

| Item | Built |
|---|---|
| 1. Days everywhere; lifespan a world setting (D2-139, D2-153) | `lifespan` (default 32); stages are its shares (2, 4, 6, 20 at 32); pregnancy, gap and old age's doubling scale with it; a person's stage follows `born`; the generator dates its tree in days (§2) |
| 2. Partners (D2-140) | `partner {with}` (both, same day, same place); `part`; death ends it |
| 3. Trying, conception (D2-138, D2-146, D2-152) | `try {with, units}` (opposite sex, both adults); that night 0.5 x (1 - e^(-0.5 x units)), the lesser of the two's units, if they slept in one place and neither missed a meal; keyed |
| 4. Pregnancy (D2-141) | 5 days; +0.3 food a night; a unit fewer in its last 2 days; 0.05 a day of loss on the road then; it shows from day 3 |
| 5. Birth (D2-141, D2-147) | on the night ending the fifth day; risks by shelter, fire and food, halved with another adult in the same building (or out at the same place); the child is a new person in the mother's household, named from its line, with kin both ways; the 4-day gap |
| 6. Infants and children (D2-142, D2-145, D2-148, D2-150) | they eat (0.5; a child by the dial) from the stores here, then their family's hands; `work {what: care, at: <child>}`; deaths by care, hunger and a cold night without a fire; an infant goes with its mother when she travels (weight 2 in her load); `order {what}` by the head: children forage, herd or cut hay each day; the dial, low or high, a world setting (`children: {on, dial}`) |
| 7. Coming of age (D4-20) | at the end of childhood a youth agent: the heir to a seat with a model takes it, the rest the cast's youth model (bots in a bot run); what it was present for (carers, births, deaths, raids, fires, going hungry) as lasting memories; its household's crafts as awareness |
| 8. Old age (D2-149) | adult 0.001 a night; elder 0.01, doubling every 20 days into old age |
| 9. Succession, inheritance (D2-143) | `name {heir}` by the head; on the head's death the heir, else the eldest stands in while the grown members `name {head}` for 2 days, the most named heading it; the dead's claims pass by the household's rule (eldest, partible, household) |

What agents see: a partner; their own pregnancy once it shows, and others' ("near her time") in who is here; babies and children
of their household, whether each was fed and who looked after it yesterday, days until grown; the care work; the children's order;
an heir or a succession under way; births and comings of age as events at their place (birth: the building; grown: the node).

## 2. Choices the spec left open (OPEN Q-22, for Zach to confirm or change)

1. `part` is one-sided: either partner can end it.
2. A pregnancy refuses `try` only once it shows (day 3): before that nobody knows, so trying is accepted and does nothing.
3. "Both adults": the adult stage only (not youths, not elders).
4. The helper at a birth: any adult or elder other than the mother sleeping in the same building, or out at the same place.
5. An infant travels only with its mother (not another carer) and weighs 2 in her load; on arrival it has no arrival event of its own.
6. A child eats from the stores at its place first, then its parents' and household's hands where it is.
7. Children's work: forage, herd, cut hay (the watch, D2-21, is not built); at the high dial half a unit is a half chance each day;
   a newborn knows that work at skill 0.5.
8. A child's name: an unused name of its line's forebears (the generated tree), else one nobody living has.
9. Succession: a tie goes to the earlier born; youths do not name; the stand-in is the eldest adult.
10. The generator keeps its tree in years (its demography) and maps every date to days by the stages' starts (4, 12, 18, 60 years
    to the infant, child, youth and adult spans; L/40 days a year beyond); winters ago are counted from days at 24 a year, so most of
    an elder's remembered hard winters fall on "last winter" or "2 winters ago" (a 32-day life is a year and a third).
11. A world whose people have no `born` keeps its stages; its elders die at 0.01 a night (no doubling), its adults not of age.
12. A newborn knows the places its mother knows.

## 3. Dry runs

- The valley world (valley_s5) with children on and three couples scripted to try every day, bots otherwise, 20 days: 3 conceptions
  by day 2, births on day 5 (out, unhelped: the mother died the next night, the child on day 10), day 7 (housed, helped; the infant
  died the next night, uncared for: the bots never care) and day 12; old age took two elders. The starvation deaths there are the
  bots' (they also die on the old code, same seed).
- 02v check (test): couples trying with 1 unit every day for 24 days have 1.3 to 1.9 births each (02v: 1.6).
- Prompts checked on a real day-0 prompt (Hollins, the Hunt head): the verbs listed, partner shown, the unexplored ways with the
  exact travel line (below).

## 4. Fixes made alongside

- `travel`: a way named in "stop at" with no "to" is taken as the destination (Wilmot in r1's first attempt wrote the deer path as
  the stop and was refused); the unexplored way's line now says `travel {"to": "<its name>"}`.
- A led ox keeps its herd's name ("the Merchant's ox"), not "the pack ox of Merchant's ox".

## 5. The Hollins world (Zach's request, 24 Oct)

Zach: "a single village in one node, and then a few huts out in one forest but they have a bunch of edges going out into other
forests and the forests on their node will run out fast"; "some should be at least multiple nodes deep to see if they explore and
then explore again"; "a smaller village that has relatively good resources for a long time to see if they grow and expand".

cybertron2/specs/hollins.yaml (base) and hollins_s7.yaml (generated, seed 7): 19 people (13 adults, 2 youths, 2 elders, 2
children; 6 couples of age), 48 days, children on at the low dial, lifespan 32. Opus: the Thorne head (the Granary), the Hunt
head (the huts), and one more adult; Sonnet the other heads and two more; Haiku the rest.

- Ockley: two households and a cottage; 450 grain standing, 256 in store, a fallow field to sow, cattle: 1.78 times what it eats
  over 48 days (21_capacity.py). Wood: a copse of 10 against about 126 its hearths burn.
- Hollins: two huts, a day away; Hollin Wood 70 timber that does not grow back, a little game; no field: 0.34 times what it eats.
- Beyond, nobody there, each place showing its next way only once reached: east Blackthorn (1) -> Thornend (1) -> Greyhanger (1);
  north Fern Hollow (1) -> Oakhanger (1) -> the Beckside (1, the best ground); west Birchmoss (1) -> the Fen Edge (2); and a long
  way round Blackthorn-Birchmoss (2).
- Gate tests: Hollin Wood gives 50 to 72 timber and then refuses; Ockley's only road is to Hollins; from Hollins four ways, and
  arriving in Fern Hollow shows the way on to Oakhanger; a couple can try; a child takes no turn.
- Running as runs/h1_hollins (report to follow).

## 6. Region run r1 so far (day 11)

Five of the Cole household in Coppergate died of hunger on days 5 to 11 with grain in their store: no timber, so their hearth was
out and grain cannot be eaten unboiled (D2-60). Two of them went to Ashwood for timber; one died on the way; the Moors next door
(Opus head, 160 grain and a fire) were asked for help only on day 7. A gap in the world, not the engine: Coppergate's Hillside
holds 20 timber, but felling is done only in forest, so the scrub's wood cannot be cut. Noted for the r1 report.
