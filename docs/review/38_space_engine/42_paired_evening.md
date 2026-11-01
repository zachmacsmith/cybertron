# 38.42: the paired Combe run, as now against the evening (p1_combe_now, p1_combe_evening)

Session 37.4, 2 Nov 2026. Zach: "build all five then do the paired combe run". The five, built behind world settings and recorded as
D4-65 to D4-69: the evening at the hearth with one wave of answers (D4-65), the evening settles the night (D4-66), setting off in the
morning or at nightfall (D4-67), tags and names for herds and things (D4-68), ages shown (D4-69).

## The pair

Same world (cybertron2/specs/combe.yaml: Ivo, head, Opus 5.5; Margery, Sonnet 5.5; both 52 days old, lifespan 96; their son Everard,
coming of age on day 10 as Haiku 5.5), same seed (61), 40 days, the belief-built message in both. The evening arm is
cybertron2/specs/combe_evening.yaml (the same, with `evening`, `tags`, `ages`). c1_combe (38.41) is a second run of the "as now" arm
for these 40 days, on the same code but for the new settings.

| | c1 (as now) | p1 as now | p1 evening |
|---|---|---|---|
| first try for a child | day 18 | day 4 | day 0 |
| tries (units spent) | 9 | 8 | 31 |
| conceived | day 20 | days 4, 20 | days 0, 12, 23, 36 |
| born | Hawise (26) | Geoffrey (10), Hawise (26) | Idonea (6), Avice (18), Ursula (29); a fourth due |
| alive at day 40 | 4 | 5 | 6 |
| store at the end | ample | grain 59, beans 11 | grain 0, beans 3, meat 75; Ivo starving |
| speech per agent-day | 2.0 | 2.0 | 3.9 |
| private share of speech | 0.99 | 0.97 | 0.56 |
| speech not about work (keyword count, crude) | 0.01 | 0.05 | 0.11 |
| calls per agent-day | 2.5 | 2.4 | 3.7 |
| refused or not done (per refused act) | 21% | 16% | 13% |
| units used | 71% | 71% | 66% |
| departures | 2 at nightfall | 9 at nightfall | 5 in the morning, 4 at nightfall |
| cost | $6.44 | $10.45 | $7.91 |

## Reading it

- **More children, and the cost of them.** The couple tried on the first night of the evening arm ("Margery, did you try with me
  today?") and at the hearth most nights after; three born, a fourth conceived. Which of the evening and the age line did it cannot be
  separated with one run each; the "as now" arm also tried early (day 4) and had two, against c1's one, so the spread between runs of
  one arm is large. Growth then met food: blight took the barley on day 26 ("Food is now everything"); they slaughtered a calf, two
  cows and an ox, hunted the Holt for nothing, tried to bake bread with no flour, and ended with six people, no grain and Ivo starving.
  The "as now" arm, five people, ended with stores.
- **The evening became the household's meeting.** Nightly plans ("Ivo minds Idonea each morning, Everard keeps felling"), care around
  the births ("Stay near; the child may come soon" / "I'll be right here, Margery. Sleep well"), the young sharing the minding ("I will
  stay and mind Ursula while you are away. Safe hunting"), and the food crisis argued out (which beast to kill, what was found). Still
  mostly practical; talk about aims, kin or the dead did not appear in 40 days.
- **Answers.** 112 answer calls on 128 evenings: most evenings someone was named and answered. Morning re-asks fell from 1.3 to 0.8
  per agent-day (one wave instead of two).
- **Departures.** Everard and Idonea set off for the Holt in the morning to hunt and came back the same way; nightfall departures came
  in at midday with half their units, as built.
- **Tags.** 12 actions used tags; nobody named anything.

## Cost

The "as now" arm cost more because of its cast, not the evening: Ivo named Everard heir before he came of age, so Everard took Ivo's
model (D4-20) and ran on Opus ($3.44 against $0.13 on Haiku in the evening arm). For the two who were the same in both arms, Ivo and
Margery: $5.78 as now, $6.89 with the evening (+19%). The evening's calls cost $1.91 (evening $1.16, answers $0.75); the morning
wave and the memory calls cost less with it. Weekly usage: 34% before, 36% after.

## Faults found, and fixed

1. **Slaughter ignored which beast was asked for** (the tag setting makes `thing` free text; the models wrote `"thing": "bull"`, which
   slaughter did not read): a calf, two cows and an ox died for "the bull". Fixed: slaughter reads a beast's role from `thing` too, and
   a herd's tag picks the herd (farm.py; test).
2. **The meat that "lay on the Common".** Eleven takes refused, "you know of no meat lying at the Common". Root cause: a slaughter's
   meat goes into the doer's hands, the result line did not say so, and the refusal read as if the meat were there unknown. Fixed as
   D4-70 (proposals/search_on_take.md): the slaughter line says where the goods went, and taking from a place one does not know holds
   the thing is a search by how plain or hidden it lies.
3. **Slaughter had no signs for anyone near** (Zach: "pretty visceral senses for the person and others nearby"): an audit and a sign
   bundle are in hand (38.43).

## Open

1. A second pair (another seed) before reading the births as the evening's doing.
2. Whether the age line alone (no evening) brings the early trying.
3. The evening arm's growth outran its food: whether that is the world (one small infield, one blighted crop) or the household's
   planning; a world with more ground is the test.

*Current as of 2 Nov 2026.*
