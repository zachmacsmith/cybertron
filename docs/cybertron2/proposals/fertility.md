# Proposal: fertility and replacement

**Status:** decided in part (29 Oct): pregnancy 2 days, the gap after a birth 1 day, and the conception chance's cap 0.8 (D2-162).
The rest (§3 to §5) is for discussion. **Owner:** 37.2. **Affects:** spec/life/birth_and_death.md, data.LIFE. Model:
[02ze_fertility_model.py](../../review/37_growth/02ze_fertility_model.py).

## Summary

As built (D2-146, D2-147), a population could not replace itself even if every couple tried every night. The cause was the hard
waits, not the odds: a woman is an adult for 20 days at the default lifespan, and each birth took at least 10 of them (5 of
pregnancy, 5 to the end of the gap), so two births at most fitted in her life.
- **Decided:** shorter waits and a higher cap (D2-162). A couple that tries every night now has about 3 children, and one that
  tries a little over half the nights replaces itself.
- **Zach's direction (29 Oct):** limits should be soft rather than hard waits: the child has to be fed, and the young are
  vulnerable.
- **Open:**
  - what lifespan should do to family size (§3);
  - how vulnerable the young should be (§4);
  - whether children should cost more (§5).
- Flagged for later: replacement rates against how often people try, across lifespans (OPEN L-27).

## 1. As built: below replacement at any effort

R0 is daughters reaching adulthood per woman; a population holds at R0 = 1, which needs about 2.2 births a woman, since 93% of
children well kept reach youth. The figures are for lifespan 32 and 1 unit each.

| How often a couple tries | Births a woman | R0 |
|---|---|---|
| every night | 1.28 | 0.59 |
| half the nights | 0.89 | 0.41 |
| a third | 0.68 | 0.32 |
| every night, conception certain | 1.97 | 0.91 |

**Why the waits were too long.** Pregnancy was 16% of a life to old age and the gap 12%. For people the figures are about 1% (nine
months in 60 years) and about 3%. Natural human fertility fits 8 to 10 birth cycles into a woman's fertile years; this fitted 2.

**Why nobody saw it.** The children model (02v) and 37.4's check (38.27: 1.3 to 1.9 births a couple) counted births within one
24-day run. Neither computed the lifetime rate.

## 2. Decided (D2-162): pregnancy 2 days, gap 1, cap 0.8

The conception chance becomes 0.8 × (1 − e^(−0.5 × units)): about 0.31 a night for 1 unit each, 0.51 for 2, 0.62 for 3. Pregnancy
and the gap stay scaled with lifespan (D2-153) unless §3 changes that.

| How often (1 unit each) | Births a woman | R0 |
|---|---|---|
| every night | 3.00 | 1.39 |
| 3 nights in 4 | 2.55 | 1.18 |
| half the nights | 1.96 | 0.91 |
| a third | 1.45 | 0.67 |
| 1 in 5 | 0.96 | 0.44 |

| Half the nights, by effort | Chance a night | Births | R0 |
|---|---|---|---|
| 1 unit each | 0.31 | 1.96 | 0.91 |
| 2 units | 0.51 | 2.66 | 1.23 |
| 3 units | 0.62 | 2.98 | 1.38 |

So children stay a choice that matters:
- a family that tries often grows, like the Fenwicks in w1, who tried every day;
- one that rarely tries shrinks, like the Cotters, who never did;
- replacement sits at about 55 to 60% of nights with 1 unit, or half the nights with 2.

**What follows from shorter pregnancies** (derived, to confirm):
- birth on the night ending the second day;
- the last day of pregnancy carries 1 unit fewer and the road risk (was the last 2 of 5);
- signs from the day after conception (were from the third day), scaled.

## 3. Lifespan and family size (open)

D2-153 scales pregnancy and the gap with lifespan. With them scaled, family size barely changes with lifespan: a long life is
the same life slowed down. With them fixed in days, longer lives allow larger families, as people's do.

| Lifespan | Adult days | Scaled: every night | Scaled: half | Fixed: every night | Fixed: half | Fixed: a third |
|---|---|---|---|---|---|---|
| 32 | 20 | 3.0 | 2.0 | 3.0 | 2.0 | 1.5 |
| 48 | 30 | 3.4 | 2.4 | 4.5 | 3.0 | 2.2 |
| 64 | 40 | 4.0 | 3.0 | 6.0 | 4.0 | 3.0 |
| 96 | 60 | 4.5 | 3.5 | 8.9 | 5.9 | 4.4 |

(Births a woman, decided values, 1 unit.)

**The trade-off:**
- **Fixed** pregnancy and gap let a long-lived world have large families, so soft limits (§4, §5) can be the main check rather
  than the waits. It breaks D2-153's rule that lifespan scales every part of a life.
- **Scaled** keeps that rule, but family size is then capped at 3 to 4.5 births a woman whatever the lifespan, well below what
  people manage when they try a lot.

## 4. Soft limits: the young are vulnerable (open)

**Today:**
- an infant's risk rises when it is uncared for (0.02 to 0.08 a night), hungry (×2) or cold without a fire (×2);
- a child's risk (0.005 a night) ignores hunger and cold altogether; only the high dial's minding raises it;
- children also die of starvation like anyone else.

**Proposed ("vulnerable young"):**

| Rate | Engine | Proposed |
|---|---|---|
| infant cared for | 0.02 | 0.02 |
| infant not cared for | 0.08 | 0.15 |
| infant hungry | ×2 | ×3 |
| infant cold | ×2 | ×3 |
| child | 0.005 | 0.006 |
| child hungry | (none) | ×4 |
| child cold | (none) | ×3 |
| birth (infant) | 0.03 | 0.04 |

This is what reaches youth, and R0, by how the young are kept. The figures use the decided values, at lifespan 32.

| Keeping | Engine rates | Vulnerable young | R0 every night | R0 half | R0 a third |
|---|---|---|---|---|---|
| well kept | 0.93 | 0.92 | 1.38 | 0.90 | 0.67 |
| busy (infant cared half the nights) | 0.87 | 0.80 | 1.20 | 0.78 | 0.58 |
| poor (hungry 1 night in 4, cold 1 in 4) | 0.91 | 0.84 | 1.26 | 0.82 | 0.61 |
| neglected (uncared, hungry 1 in 3, cold 1 in 4) | 0.71 | 0.35 | 0.52 | 0.34 | 0.25 |

**What the model shows:**
- **At lifespan 32, hunger and cold barely bite:** infancy and childhood are only 6 nights, so they move survival by under 10
  points. Neglect cuts it to a third.
- **At lifespan 64 with fixed waits (§3), vulnerability matters much more**, because there are more nights to survive:
  - well kept 0.86 reaches youth, R0 1.71 at half the nights;
  - poor 0.72, R0 1.43;
  - neglected 0.13, R0 0.25.
- So vulnerability is a strong soft limit only in long-lived worlds.

**Your word was "youth".** In the engine a youth is the agent stage (it acts, works 4 units, eats a full ration), and it has no risk
of its own beyond hunger and cold, like an adult. The proposal reads you as meaning infancy and childhood (the stages with no
model call). Whether youths should also be more vulnerable (say, a higher risk when hungry or cold) is open (Q3).

## 5. What a child costs: feeding binds only when the land is full (open)

| Lifespan | Dial | Food | Units of care | Total | Adult days of work | Share of a woman's adult span |
|---|---|---|---|---|---|---|
| 32 | low | 4.4 | 2 | 6.4 | 1.1 | 5% |
| 32 | high | 5.6 | 10 | 15.6 | 2.6 | 13% |
| 64 | low | 8.8 | 4 | 12.8 | 2.1 | 5% |
| 64 | high | 11.2 | 20 | 31.2 | 5.2 | 13% |

(Low dial: infant care 1 unit a day, a child eats 0.7. High dial: infant care 3 units, a child eats 1.0 and needs 1 unit of minding
a day.)

**What it means:**
- **Children are cheap.** For people, a child to working age costs about 20 to 30% of a working life; here 5% (low dial) or 13%
  (high).
- **The cause:** an adult works about 6 units a day, worth about 6 food, against a ration of 1. So a household can feed many
  children from its own work, and having to feed the child is a weak limit at the household level.
- **Where it does bind is the land.** Worlds are seeded at 60 to 70% of what their land gives each year (D2-161), and holding is
  counted as land per mouth (D4-23). As a village grows, food per mouth falls, and the cost of a child shows as hunger, hence as the
  vulnerability of §4. That is the realistic soft limit, a Malthusian one, and it needs runs long enough to reach it.

**Options to make the household-level cost bite sooner:**
- a child eats a full ration on the low dial (1.0 instead of 0.7);
- an infant needs 2 units of care a day;
- or keep the costs and let the land do it.

## 6. For later (OPEN L-27)

Examine replacement and fertility rates over lifespans against how often people try. This is the model's §1 to §3 grid, then
checked in long runs:
- **the trying share:** what share of nights couples actually try, by model (Opus households tried every day in w1; Haiku never);
- **the result:** the R0 that share gives;
- **the trajectory:** whether populations grow, hold or die out over several generations;
- **the outcome:** whether any society ends near replacement by choice rather than by the dial.

## Open questions (for Zach)

1. Pregnancy and the gap: keep them scaled with lifespan (D2-153), or fix them in days so long-lived worlds can have large families
   (§3)?
2. The vulnerable young (§4): adopt the proposed rates, with hunger and cold now bearing on children as well as infants?
3. You wrote "youth": should youths (the agent stage) also be more vulnerable when hungry or cold, or only infants and children?
4. A child's cost (§5): raise it at the household (a full ration, 2 units of infant care), or leave the limit to the land (D2-161)?
5. Confirm what follows from a 2-day pregnancy (§2): the last day lighter, signs from the day after conception.

## History

- 29 Oct: Zach: "Are the chances of children too low? I feel like they won't keep a population up?" Modelled: below replacement at
  any effort as built. Zach: "your 2, 1, 0.8 makes sense. 5 days was way too long"; limits should be softer (feeding the child, the
  young vulnerable) rather than hard waits; note replacement over lifespans against how often people try for later. Written;
  D2-162; OPEN L-27.

## Sources

[spec/life/birth_and_death.md](../spec/life/birth_and_death.md); [children.md](children.md);
[02v](../../review/37_growth/02v_children_model.py); [02ze](../../review/37_growth/02ze_fertility_model.py);
[38.27](../../review/38_space_engine/27_package_d.md); [38.31](../../review/38_space_engine/31_wide_w1.md);
cybertron2/engine/life.py, data.py (LIFE); D2-138 to D2-153, D2-161, D4-23.
