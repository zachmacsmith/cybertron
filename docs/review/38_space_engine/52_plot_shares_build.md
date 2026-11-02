# 38.52: Plot shares and a crop for each holding, as built

Session 37.4, 3 Nov 2026. Built from 37.2's brief, review/37_growth/02zi_build_brief_plot_shares.md (Zach, 3 Nov: "option C for
crops, go ahead with plot shares"), for D2-163 (land is held in plot shares within a parcel) and D2-172 (a field carries one crop
for each holding on it). The rules are in spec/world/holding.md §Plots and §A crop for each holding. Nothing beyond the brief was
built; the choices it left open are listed at the end, each marked as mine.

## The model

A field held whole keeps its state exactly where it always was. The parcel's own crop and soil fields (`crop`, `fertility`,
`broken`, `last_crop`, `last_kind`, `fallow_since`) are the record of the ground held whole (by the claims that name no plots:
`held_whole`), or, where nobody holds it whole, of its unclaimed plots. Each holding of part of a field has its own record in the
parcel's `shares` list (`holder`, `plots`, and the same six fields). Every reader of a field goes through `farm.records(par)`, which
gives the parcel's own record first (holder None) and then each part holding.

This is why every existing world runs unchanged: none of them has a claim with `plots`, so none has a share record, and their crops,
soil and draws are where they were. The first version I wrote moved a whole holder's crop into a share record; it was the same
physics but broke every reader of `par["crop"]` (tests, c2viz, the overview), so I replaced it before committing.

The records follow the claims through one engine-side function, `farm.sync(w, pid, carry)`, called inside the claim primitives
(`claim`, `end_claim`, the new `plots`), inside `die` (inheritance), at seeding, and each night if a claim has run out. Plots given
up go into a pool with their soil and broken ground; plots gained are drawn from that pool first, then from the unclaimed plots,
then (a dispute: plots someone else already holds) at the unclaimed level. With `carry` (seeding, inheritance) a holding that gave
up all its plots hands its standing crop on, split by plots; otherwise the crop stays with the holding that sowed it.

## File by file

| File | What changed |
|---|---|
| `engine/farm.py` | The plot-share layer: `layout`, `holdings`, `records`, `record`, `unclaimed`, `plots_of`, `standing`, `main_rec`/`main_crop` (the holding that stands for the field in a summary), `view` (the field as one holding shows it), `named` (whether a field's holdings are told apart in words), the words (`the_crop`, `the_part`, `crop_words`, `held_words`), `sync`, `seed_crops`, and the targeting (`target`, `sow_targets`, `on_holder`, `against`). Sow, break, weed, manure, choose seed and reap act on one record; sowing can run across one's own record and then the unclaimed one in a single act. The night grows, blights, kills, rots and ends each record's crop, and rests and grazes each record's soil. |
| `engine/world.py` | Claims take `plots`, `of`, `over`, `joint`; seeded claims pass them. New primitives: `set_share` (a field of one record), `shares` (sync), `plots` (n plots move between parties). `draw` takes `holder` for a holding's crop. `claim` and `end_claim` sync a field. A co-heir named in `joint` has the claim's rights. Seeding: syncs each field and reads `state: {crops: [{holder, kind, left, ripe_day, plots?}]}`. |
| `engine/verbs.py` | `claim {thing, plots?, for?}` (`_claim_plots`: of the unclaimed first, any more overlaps the holder with the most plots there, recorded as `of`/`over`, seen as a dispute). `work` takes `on` and `plots`. The work event names whose plots ("on the Webbs' plots"), concerns that holding's people, and carries `holding`. The act reaches `ready` (through `_site` and `shortfall`), so `on` and `for` count when deciding whether a work can be done. Clearing a held parcel syncs its holdings; clearing a field for building drops them. |
| `engine/agreements.py` | A land leg, "2 plots of Long Field": parsed, tied to a parcel here when offered, checked against the giver's holding and right to sell (`alienation`) when offered and when taken, and paid at once with the `plots` primitive. |
| `engine/life.py` | `on_death`: land (field, pasture, meadow) passes in whole plots (`plot_heirs`): eldest, all to one; partible, eldest first; more heirs than plots, the last plot held jointly. Then the fields sync with `carry`. Buildings and herds pass as before. |
| `engine/herds.py` | `trample`: every standing crop loses the day's trampling share of what stands, each recorded on its record. `value` and `drawn` see every holding's crop. |
| `engine/signs.py` | `context(here, pid, h, holder)` builds one holding's view (`x.p` is the field with that holding's crop and soil; `x.the`, `x.part` name it). CROP rows are emitted per crop record, with "the {kind}" written as `x.the`. On a field held in shares the FIELD rows about a holding's ground and soil (rows 3 to 9) are emitted per holding, named by its part; the rest once. Reaping signs fire only for the holding reaped. No row's chance changed; no new rows. |
| `engine/prompt.py` | The field line adds what stands and, where claims name plots, who holds how many; the schema takes `on` and `plots`. |
| `engine/run.py` | The dawn stray incident eats from every standing crop, by what stands. |
| `engine/knowledge.py`, `environment.py`, `layout.py`, `exchange.py`, `perceive.py`, `landgen/economy.py` | Read a field's crops through `farm.standing`/`main_crop` instead of `par["crop"]`. |
| `c2viz/extract.py` | One line: a parcel's record is read from `signs.context`'s view (`x.p`), so a field held in shares draws its main holding. A field held whole is unchanged. c2viz's tests pass. |
| `tests/test_cybertron2_farm.py` | Two calls changed (assertions kept): Edric sowing the Hales' Brook Field and Simkin sowing it for the Reeds now name it (`on: "the Hales"`), as the brief requires for sowing plots another holds. |

## Tests (`tests/test_cybertron2_plot_shares.py`)

The brief's eight, all passing; 332 cybertron2 tests pass in all (291 before, plus 41 here: test 8 runs over every world).

| # | Test | What it checks |
|---|---|---|
| 1 | two households holding 3 and 2 plots each sow their own | each record's crop and area; the unclaimed plot fallow; the line "field; 6 plots; barley on 3 (Reeds), beans on 2 (Webbs), 1 fallow; held: Reeds 3, Webbs 2; 1 unclaimed" |
| 2 | sowing past one's plots sows the unclaimed plot, then stops; another's needs `on` and is seen | 3 own + 1 unclaimed, then refused; with `on` it sows the Webbs' plots; the event names them and concerns Wat |
| 3 | reaping another's holding: the grain is the reaper's, noticed by those working the field | grain to Rafe, the Reeds' crop untouched; the event's chance by the rule is higher for Wat (working there) than for Col (elsewhere) and higher again for one minding the field; it reaches Wat in perception; signs name the holding, and only the holding reaped |
| 4 | beans after barley gain fertility; barley twice loses it | per record, from 0.8; the unclaimed level untouched |
| 5 | a herd tramples the standing crops in proportion to their plots | 3 plots to 1: losses 3 to 1; recorded on each crop and on the herd |
| 6 | partible: 5 plots by 2 heirs give 3 and 2; by 6 heirs, five single plots, one held jointly | also the standing crop split 60/40 with the plots, and the joint co-heir's rights |
| 7 | "2 plots of Long Field" accepted moves the claim; the line shows it | holdings Reeds 1, Webbs 4; the soil went with the plots (1.1); a member who may not sell is refused |
| 8 | every world held whole runs unchanged | every world file with fields and people (32, in `specs/*.yaml` and `specs/ladder/*.yaml`) loads with no share records, its whole holders as the field's own record, its seeded crop on the parcel; valley_s5 and hollins_s7 bot-run 4 days with no share records and replay with no mismatches |

**Against the old engine.** Before building, every runnable world with fields (32, including the ladder) was bot-run for 10 days on
the old engine and digested: every good's total, who lived, and each field's crop records, fertility and last crop. On the new
engine 11 of 32 came out identical; the rest differ only because bots no longer sow fields held whole by other households (the
brief's rule: sowing another's plots needs `on`). With that one rule relaxed for the experiment, all 32 came out identical, field by
field and good by good. The scripts are in the session scratchpad (`digest.py`).

## Runs

- `hollins_s7.yaml`, bots, 8 days (three deaths, so inheritance runs): no errors; replay checked 56 steps, `"mismatches": []`.
- A scratch world held in shares (the tests' hamlet: Reeds 3, Webbs 2, Wynns 2 overlapping, crops on two holdings, a herd), bots, 10
  days: no errors; replay checked 70 steps, `"mismatches": []`. Bots with no ripe crop of their own reaped the Reeds' barley "on the
  Reeds' plots".

## Choices the brief left open (mine)

1. **Where a field's state lives.** The parcel's own fields are the ground held whole, or the unclaimed plots; only part holdings
   get records (above). The brief describes one record for each holding; a whole holding's record is the parcel itself.
2. **Default target for one with no holding with that work to do.** The brief says breaking, weeding and manuring fall on one's own
   holding "by default", and reaping on one's own. For one who has no holding with that work to do in the field: the unclaimed
   plots, else the only holding that has it (seen, as using another's land always was), else one must say whose. This keeps a field
   held whole by others workable as before (a hired hand, a neighbour reaping). Sowing has no such fallback: the brief says
   another's plots must be named. One who does have a holding with that work (a crop of one's own not yet ripe, say) is refused
   with its reason, not sent to another's. Flagged for 37.2 (OPEN L-62).
3. **One crop per holding.** A holding's unsown plots take only the crop already on it; seed of another kind goes on to the
   unclaimed plots, or is refused.
4. **A crop standing on plots that change hands** by an agreement stays with the holding that sowed it until reaped (the
   away-going crop), so a holding's crop may stand on more ground than it now holds; a holder of the whole who comes to hold only
   part keeps the crop it had on the whole. On inheritance and at seeding the crop goes with the plots, split by plots (merged into
   an heir's crop of the same kind; one of another kind stays on the dead holder's record until reaped).
5. **Inheritance with more heirs than plots.** I read "5 plots by 6 heirs: 5 single plots and one share held jointly" as: the plots
   stay whole; heirs one to four take a plot each; the fifth plot is held jointly by heirs five and six. The joint share is claimed
   by the dead's household where there is one (the spec's "held jointly by the household or the co-heirs"), with the co-heirs named
   in `joint`; `joint` gives them its rights. Partible with one heir, eldest and household rules pass a whole claim as a whole claim.
6. **Overlap words.** A claim of more plots than are unclaimed records whose plots it overlaps: the holder with the most plots there
   (`of`, `over`), so the line can say "the Wynns claim 1 of the Reeds' plots". A world file's overlapping claim without `of` reads
   "(disputed: 7 claimed of 6)".
7. **Trampling "in proportion to plots".** Each standing crop loses the same share of what stands (today's rate times the head), so
   the loss falls by plots where the yield per plot is alike. The alternative (a total loss split by plots) would take a larger share
   from a poor holding than a rich one.
8. **Land legs are "now" only**, and multiplied by lots. A promise of land by a day is not built.
9. **The parcel line** keeps the line's existing shape: "- Long Field (field; 6 plots; barley on 4 (Reeds 3, Webbs 1), beans on 1
   (Coles), 1 fallow; held: Reeds 3, Webbs 2, Coles 1; here one can ...): its text." It is the place as one sees it there, like the
   rest of the line; areas are to a tenth of a plot. A field held whole keeps "held by the Reeds" and now also says what stands on it
   ("barley on 5"): the only change existing worlds see, and in the prompt only.
10. **Signs name the holding** only on a field held in shares (more than one crop on it, or a holding of part of it): "the Reeds'
    barley in Long Field", "stubble in the Wynns' part of Long Field". A field held whole reads word for word as before.
11. **Joint co-heirs and "own".** A co-heir named in `joint` counts the joint share as its own for the default target.
12. **Field works** (ditches, terraces) and fences stay parcel-level, as the brief says for fences.

## Open

- **How plain is working another's holding?** The work event keeps the engine's existing calibration for using land others hold
  (base 0.35 by the one rule): about 0.09 to one working the same field, about 0.44 to one minding it. The brief says reaping
  another's holding "is seen and remembered"; whether it should be plainer (an `own` on the event) is a calibration for the noticing
  rule, not decided here.
- production.md "Farming" does not yet say that sowing goes on to the unclaimed plots, or how reaping defaults: OPEN L-62 (37.2).
- Pasture and meadow claims hold plots and show in the line, but nothing uses the shares yet (grazing and hay stay whole-parcel, as
  the brief says).
- `wp/cybertron2` on origin has moved on by 9 commits since this branch was cut, some in files changed here (knowledge, life,
  prompt, run, verbs, OPEN.md): the merge needs care.
