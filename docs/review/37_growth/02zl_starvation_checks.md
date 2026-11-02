# 02zl · Can a world feed its people? Past runs and the pre-run checks

Current as of 2 Nov (37.2), with D2-190: the carrying burden is a warning, never a refusal. Zach asked (2 Nov) for economic analyses of past runs, to find when the economics worked and when they
failed, and for automatic checks a world must pass before a run so nobody starts bound to starve. This note covers what the runs
show, the checks built from them (`cybertron2/landgen/economy.py`), how the checks score against the runs, and what the evidence
cannot yet say. Nothing here is decided. The thresholds are first values for Zach to accept or change.

- Data: the 48 runs in the Hugging Face dataset `zachmacsmith/charter-runs`, `experimental/cybertron2/`, read by
  `02zk_run_economics.py`. 37.4 reports staging 48 runs to Zach as a tarball and believes nothing is on the Hub yet. The Hub copy
  exists but lacks wb2 and the later Wenbridge runs, so it is probably an earlier upload.
- Ten runs (m1_*) are from the first engine's world format, which no longer loads; they are left out.

## 1. What the runs show

A run is scored on what happened, not on what was planned. Old-age and infant deaths are left out, because they are not the
economy's doing.

| Verdict | Rule |
| --- | --- |
| failed | hunger or cold deaths reach 10% of the people, or 10% of person-days are missed meals |
| strained | 3% or more of person-days are missed meals, or anyone starved |
| held | anything better |

w1_wide is read only to day 24: its later days are empty replies after the usage limit (38.31).

| | Runs |
| --- | --- |
| Failed | b1_wild, c2_combe, f1_frontier, h1_hollins, h2_hollins, m2_V, r1_region_dependent, v3, w3_region, wb1_wenbridge_hungry |
| Strained | the barleyfield and two-valleys families, w1_hamlet, w2_two_valleys, p1_combe_evening |
| Held | a1, a2, c1_combe, c3_combe_rich, d1_duo, p1_combe_now |
| Cut short | r1's four restarts, r0, h1_noway, v2_bugged, w1_wide. These stopped before half their days and did not fail, so they say nothing either way. |

What separates the failures:

1. **Every failed world but one had a village whose own land could not feed it.** That village had to bring in food (or fuel) from
   a day away, and the share of its people needed on the road each day was 0.13 to 0.34:
   - Coppergate: 0.26 in r1 and w3.
   - Hollins: 0.24.
   - Elkmere: 0.24.
   - Gormhold: 0.22.
   - Millbrook: 0.27.
   - Wenbridge: 0.13.

   No world that held or was strained had such a village. The carrying was physically possible: a quarter of the people on the
   road is a lot, but not impossible. The agents did not sustain it. Trade moves food, but these agents did not move enough of it,
   day after day.
2. **Totals mislead.** Counted generously (store, crops ripening, milk, the wild's standing food), the whole world's food for the
   run came to 0.9 to 1.03 of need in r1, w3 and wb1. In other words, there was nearly enough food in the world, but in the wrong
   places and the wrong hands. The yearly flow per village predicts failure better than the stock per region.
3. **Stocks are not eaten as arithmetic says.** Counting a village's store and its woods' standing plants and game as food for the
   run missed five of the ten failures (b1_wild, f1, h2, wb1, c2). People did not live off a stock they had to gather and share.
4. **Households' runway predicts strain, not death.** Households starting with under 3 days' food a member, with no harvest of their
   own sooner, are where the early missed meals fall:
   - the Lowes and Hales;
   - the Smiths;
   - the Newcomes.

   Such households appear in strained and held runs alike. wb1 is the extreme case: the Arderns held 34 days a member while the
   Newcomes held 1.2, and two people starved the day before the harvest.
5. **Fuel.** The old worlds' woods are small. Their flow falls short of their hearths ("region heat" warns on nearly every pre-2 Nov
   world), yet their hearths stayed lit: people burned into the standing wood (a2, c1, w1). A fuel shortfall is fatal only where the
   village itself has no woods. That is wb2 (37.4, 38.49): the region's woods were a day off, food was eaten raw, and 11 of 14 died.
   Raw grain gives 0.2 against 0.7 cooked, so a cold hearth costs a village most of its grain.
6. **c2_combe** is the one failure the land does not explain. The land fed 16 and 4 lived there. The head (Ivo, born day −52, lifespan
   96) died of age on day 62, and the two he had fed (a Haiku youth and an unmodelled child) starved within a week. It is a
   succession failure: labour and care, not land.

## 2. The checks

`python -m cybertron2.landgen.economy <world.yaml>` runs the checks on any world with people, hand-made or generated. The generator
runs them after it makes people. Only a run whose food or heat cannot be covered even counting everything the world holds is refused;
a file may still allow that as a designed hardship:

```yaml
generate:
  allow: [food over the run]
```

| Check | Level | What it compares |
| --- | --- | --- |
| region food, region heat | warn > 0.85 | people against what the land keeps for good (capacity.py) |
| food over the run | refuse > 1.0, warn > 0.85 | the run's need (grown 1, young 0.6 a night) against store, crops ripening within the run, milk (1.6 a cow in milk a day), the wild's standing food, woods' forage, and fields past a year |
| heat over the run | refuse only if even the woods standing fall short; warn if store plus flow fall short | hearths × (normal nights + cold nights × 4) against store, the woods' flow and their standing wood |
| **carrying burden** | **warn > 0.04, marked `high` above 0.12 (D2-190: never a refusal)** | per village: (yearly food short, as grain) + (the run's fuel short, as timber), carried both ways over its shortest road, by foot (10), pack (20) or pack ox (60), as a share of its people |
| households' runway | warn if households holding over 20% of people have < 3 days' food a member and no harvest sooner | the households' stores |
| fuel | warn | hearths with under 3 nights' fuel and no woods in their village |
| room to grow | warn | (people + projected births) against the land, where children are on |
| succession | warn | someone grown in a household dies of age within the run, leaving others |

## 3. Against the runs

`python docs/review/37_growth/02zk_run_economics.py --check <runs>`

| | Refused | Ran |
| --- | --- | --- |
| Failed (10) | 9 | 1 (c2_combe: succession warns) |
| Held or strained (20 conclusive) | 0 | 20 |
| Cut short (8) | 6, all twins of failed worlds | 2 |

The weak points:

1. **One check does the work.** Every refusal includes the carrying burden. The other refuse-level checks add only m2_V and v3, and
   both were already caught by it.
2. **The threshold is a lower bound on failure, not a calibrated line.** No past world had a short village that held, so the data
   cannot say whether a village carrying 5% of its people's food survives. 0.12 sits just under the lowest failure (wb1, 0.13), and
   it was chosen knowing the answers. The 38 conclusive runs are about a dozen distinct worlds, and the failing ones are also the
   region and frontier worlds, the longest runs and the most agents. Carrying burden may partly stand in for "a regional world"
   rather than measure carrying itself.
3. **This sits in tension with scenario_design.md, which asks for dependence.** The evidence says food dependence, at the levels
   tried, kills, and that dependence in metal, stone and tools (what generated worlds have) is safe. The generator already seeds
   each village at 60 to 70% of its own land's capacity, so generated worlds pass with a burden of 0. Food dependence below 0.12 is
   allowed, untested.
4. **The checks are not causal.** They do not see ownership or care: the Masons starving beside a heap of surplus grain (D4-89), or
   the Arderns' hall. The households' runway is the nearest proxy.

## 4. What 37.4 and the other sessions used

37.4's reply (board, 2 Nov):
- **capacity.py** (38.21), not run on Wenbridge, though it would have flagged the near fuel.
- **Bot dry runs**, which catch crashes, not calibration.
- **Hand arithmetic for Wenbridge**, wrong three ways: it was not checked by household, it ignored fuel, and it ignored need above
  one meal a night.
- **The beds-and-store test**: `tests/test_cybertron2_buildings.py`.
- **After a run**: run.db's `changes` table summed by `why`, against days.jsonl's `ate` and `uncooked`, which exposes food eaten raw
  (wb2: 459 against 286). run.db's `checkpoints` give stores by day.

37.1 and 37.3 have not replied yet.

That post-run audit is the better way to read a run, and these checks do not replace it. The HF runs carry days.jsonl and run.json
but not run.db, so it could not be repeated here.

## 5. On today's world files

What the checker says about the world files in `cybertron2/specs/`:
- **Refused** (carrying burden): every region, Hollins, frontier and wild-bands file, valley_s5, and **wenbridge.yaml at 0.12**,
  right at the line, even with its new coppice.
  - Wenbridge's land keeps 8 for 12 people. Its 30 days are fed from store and harvest, but the village is short for good.
  - Either Wenbridge is a designed hardship (`allow`), or the next Wenbridge run tests the threshold. **That is a prediction:** if it
    holds, 0.12 is too strict.
- **Run with warnings**: the hamlets, barleyfields, two valleys, combes, duo and wide_s7.
- **Not checked**: worlds whose people come from a `cast` (hamlet, region, valley, wide, two_valleys, hollins, combe_base) need
  their people generated first.

## 6. Open

- **L-50:** calibrate the carrying burden with a ladder: one generated region at burdens 0, 0.04, 0.08 and 0.12, a fixed cast, and
  two replicates each. That is eight runs of about 20 days. The ladder would answer whether food dependence can work for these
  agents at all, and where it stops.
- **L-49** (37.2's, first L-42 then L-44; both clashed with 37.4's numbers): the automated supply-chain checks remain later. Until then, generated
  worlds are checked by hand.
- **Fuel to cook.** Food that needs a fire is counted at its cooked worth. A village with no fuel should count it raw (grain 0.2).
  The carrying burden counts the fuel short, but food over the run does not yet discount the food.
- **Labour.** Neither the capacity nor these checks ask whether there are hands enough to work the land and gather the wild. The
  c2_combe and b1_wild failures suggest that is the next gap.

## 7. After Zach's reading (2 Nov)

- **D2-190: dependence is warned of, never refused.** "This should be a warning not a blocker. Some food specialisation and
  dependence is probably important, especially as societies scale up."
- The table in §3 scored the carrying burden as a refusal. As a warning flagged `high` above 0.12, it now separates the same runs,
  but no world is refused for it.
  - Refusals now come only from food or heat over the run, which catch m2_V and v3.
  - wenbridge.yaml runs, with a high-burden warning.
- **The succession check is rewritten on the engine's own hazard** (life._old_age, D2-149). `lifespan` is the age a person becomes
  an elder, not the age of death; after it, death is a nightly chance doubling every 20 days. The check flags anyone grown with a
  25% or greater chance of dying in the run. c2_combe: Ivo and Margery, 39% each.
- **The ladder (L-50) is designed and generated, not run:** proposals/dependence_ladder.md.
