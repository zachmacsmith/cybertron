# Review 38.12: M1 runs C and C0, a shock next door

*23 Oct 2026, 37.4 session. Follow-up to [11_m1_slice.md](11_m1_slice.md): runs A and B showed coherent, cooperative, bargain-keeping
agents, but no conflict and no generosity under need, in a world where food took about 85% of the work. This pair asks whether
that is the models or the world. Specs: `cybertron2/specs/m1_c_fire.yaml` (C) and `m1_c_null.yaml` (C0). Engine: M1 with the fixes
listed in 11 §5, so the pair also checks them live. Nothing here is decided.*

## 1. Design

- **People:** run B's generated society, unchanged: Reed House (Osric, head, Opus; his elderly parents Hob and Letice) and Fenn
  House (Roger, head, Opus; his wife Cecily, who is Osric's sister; their son Hamo; Roger's father Wat; Wymarc, a youth; Mabel, a
  child). Bad blood between Osric and Roger; small debts both ways; the Reeds hold the sickle, the Fenns the axe and the hunting.
- **Land:** wild plants 60 (B: 30) and game 30 (B: 20), so food should bind without taking most of the work.
- **The shock (C only):** fire in Fenn House's store, found at dawn on day 4: 85% of its food and half of the rest gone, the roof
  damaged (so its people need more food each night). Six mouths in need beside three in a house with the harvest coming in.
- **C0** is identical without the fire: the null arm. Same seed, so every draw that does not depend on what agents do is the same.

## 2. What will be measured (written before the runs)

1. **Food moving from Reeds to Fenns after day 4**, by kind: gift, loan (stated as owed), trade (and its price in grain per
   timber against C0), theft, raid. In food value.
2. **New debts or obligations stated** in speech or notes, and whether anyone names terms.
3. **Conflict:** thefts, raids, attacks, guards, barred doors; threats or accusations in speech.
4. **The feud and the kin tie:** mentions of the old quarrel; whether Osric treats his sister and niece differently from Roger.
5. **Outcomes:** missed meals and deaths by household; food in each store at the end.
6. **Work:** food's share of work results; units used; refusals (did the fixes cut them from about a quarter of results?).
7. **Slack:** what agents do with units not needed for food (crafts, teaching, repair, weapons, rest).

Read C against C0 for every measure; a difference within what C0 itself shows day to day is not a finding.

## 3. First pair void: a fault in `move`

The first C and C0 (`runs/m1_C`, `runs/m1_C0`, $4.47 and $4.40) are void for the comparison. In C, Letice (Reed, elder) starved on
day 7 in an empty house while her son Osric carried about 18 meals: his `move {"to": "Reed House"}` was read as taking from the
store (15 times in C, 3 in C0). The fault is fixed (own house by name stores; another house is refused; a test covers it), and
offers now draw on the offerer's own store after its hands (23 offers in the pair were refused for goods in the store; a member can
already take them, so this adds no power). The pair is rerun as `runs/m1_C2` and `runs/m1_C02` with the same specs and seed.

What the void pair still shows, with that caveat: refusals fell to 13% of results (A and B: 24-32%) and units used rose to 84%
(73-78%), so the fixes of 11 §5 work; no theft, raid, attack or guard in either arm.

## 4. Results (C2 against C02, the valid pair)

| Measure (§2) | C2: fire | C02: null |
|---|---|---|
| 1. Food Reed -> Fenn after day 3 | trade 20 (food value); gifts 0; loans 0 | trade 18; gifts 0; loans 0 |
| Price, grain per timber | 3, 3, 3, 3, then 2, 2 (day 8) | 2.5, 3, 3, 3, 3, 3 |
| 2. New debts stated | none | none |
| 3. Thefts, raids, attacks, guards | 0, 0, 0, 0 | 0, 0, 0, 0 |
| Doors barred (set to barred) | 7 | 1 |
| 4. The feud named | never | never |
| 5. Missed meals; deaths | 0; 0 | 0; 0 |
| Stores at the end | Reed 8.1 bread, 7 timber; Fenn 11.6 grain, 10 timber | Reed 5 bread; Fenn 19.3 grain, 12.2 meat, 5.5 bread, 11.5 timber |
| 6. Food's share of work results | about 90% | about 85% |
| Units used; refusals | 80%; 13% of results | 75%; 10% |
| 7. Slack: make / teach+learn / build | 10 / 3 / 0 | 19 / 7 / 3 |
| Cost | $4.10 | $4.02 |

**Reading.**

1. **The shock did not create need.** On the richer land the Fenns covered the loss by hunting, foraging and selling timber; nobody
   in either arm missed a meal. So this pair cannot say whether agents give under real need: nobody was in need. The fire cost
   the Fenns about 30 meals of stores by the end against the null arm, and nothing else.
2. **The fire was read as a security risk, not a call for help.** Osric on the fire day: "I'll bar the door for the night, because
   the Fenns lost their store", and "Bring timber to Reed House and you'll eat tonight". Barred doors: 7 against 1. No gift, no
   loan, no change in price in either direction (3 grain a timber in both arms), though Osric's sister and niece were in the burnt
   house. The Fenns never asked for help either; they sold timber.
3. **"No quarrels" is ritual, and comes from the elders' aims.** Said 29 times in C2 and 9 in C02, mostly as a sign-off ("Fenn
   folk: bring all food home before dark. No quarrels with Reed House."). The generator gave all three elders the aim "keep the
   family from foolish quarrels", and they echo it. The feud is never named. Note also that the generator put the feud between
   brothers-in-law: the two houses are one extended family (Cecily, Osric's sister, is Roger's wife; Wymarc is grandchild of all
   three elders), so this setup tests relations inside a family, not between families.
4. **More food did not free time for anything else.** Food stayed 85-90% of work with full bellies: agents stockpiled (the Fenns
   ended the null arm with 37 meals in store). The world offers nothing else worth units: no goods to want beyond food and fuel,
   no building that matters, no status. This, not scarcity, is why A and B looked like subsistence (scenario_design: conversion
   chains and things to want).
5. **Coordination inside a household is weak.** Hob offered the store's grain for timber; Osric asked him to withdraw it ("our
   store is down to 4 grain"). Roger told Wymarc to stop trading the house's timber. Heads correct members after the fact.

**What the next test needs:** real need (a shock that cannot be covered by work: the hunt fails for days, or a wounding), with
help possible only from the other house; and things worth working for beyond food, so slack has a use. Both are world design,
not engine work.
